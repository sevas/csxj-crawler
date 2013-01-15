import sys
from datetime import datetime, time
import locale
from itertools import chain
import codecs
from parser_tools.utils import fetch_content_from_url, make_soup_from_html_content, remove_text_formatting_markup_from_fragments
from parser_tools.utils import extract_plaintext_urls_from_text, setup_locales
from csxj.common.tagging import tag_URL, classify_and_tag, make_tagged_url, TaggedURL
from csxj.db.article import ArticleData


setup_locales()


RTLINFO_OWN_NETLOC = 'www.rtl.be'

RTLINFO_INTERNAL_SITES = {
    'blogs.rtlinfo.be':['internal', 'blog'],
}

SOURCE_TITLE = u"RTL Info"
SOURCE_NAME = u"rtlinfo"

def extract_title(main_article):
    left_column = main_article.find('div', {'id':'leftCol'})
    title = left_column.find('h1', {'class':'rtl_font_weight_normal'})

    return remove_text_formatting_markup_from_fragments(title.contents)



def extract_date_and_time(main_article):
    date_container = main_article.find('span', {'class':'date'})
    date_string = date_container.contents[0].strip()

    date_bytestring = codecs.encode(date_string, 'utf-8')
    pub_date = datetime.strptime(date_bytestring, '%d %B %Y')

    time_container = date_container.find('span', {'class':'time'})
    time_string=  time_container.contents[0]
    h, m = [int(i) for i in time_string.split('h')]
    pub_time = time(h, m)

    return pub_date, pub_time



def extract_category(main_article):
    breadcrumb_container = main_article.find('div', {'id':'breadcrumb'})
    breadcrumbs = [''.join(link.contents) for link in  breadcrumb_container.findAll('a')]

    return breadcrumbs



def extract_external_links(main_article):
    container = main_article.find('div', {'class':'art_ext_links'})

    if container:
        link_list = container.ul
        items = link_list.findAll('li')
        urls_and_titles = [(i.a.get('href'), remove_text_formatting_markup_from_fragments(i.a.contents))  for i in items]

        tagged_urls = list()
        for url, title in urls_and_titles:
            tags = classify_and_tag(url, RTLINFO_OWN_NETLOC, RTLINFO_INTERNAL_SITES)
            tagged_urls.append(make_tagged_url(url, title, tags))

        return tagged_urls

    else:
        return []



def extract_related_links(main_article):
    container = main_article.find('div', {'class':'relatedArticles'})

    if container:
        left_list, right_list = container.findAll('ul')
        all_list_items = [link_list.findAll('li', recursive=False) for link_list in (left_list, right_list)]

        tagged_urls = list()
        for item in chain(*all_list_items):
            url, title = item.a.get('href'), remove_text_formatting_markup_from_fragments(item.a.contents)
            tags = classify_and_tag(url, RTLINFO_OWN_NETLOC, RTLINFO_INTERNAL_SITES)
            tags.add('associated')

            tagged_urls.append(make_tagged_url(url, title, tags))

        return tagged_urls
    else:
        return []


def extract_links(main_article):
    external_links = extract_external_links(main_article)
    related_links = extract_related_links(main_article)

    return external_links + related_links



def extract_usable_links(container):
    """
    Extracts all <a> elements, then filters out anything with no title and target.

    Why, will you ask me? I'm going to tell you why. Because *sometimes* that
    stupid cms allows for broken empty links to appear in the source.
    It's not even clickable. It's just there, doing nothing.

    With no target.
    With no title.
    With no purpose.
    With no soul.

    This is the saddest thing ever.
    """
    def is_usable(link):
        return link.get('href') and link.contents

    all_links = container.findAll('a')
    return [l for l in  all_links if is_usable(l)]



def extract_embedded_links_from_articlebody(article_body):
    embedded_links = list()

    for link in extract_usable_links(article_body):
        url = link.get('href')
        title = remove_text_formatting_markup_from_fragments(link.contents)
        tags = classify_and_tag(url, RTLINFO_OWN_NETLOC, RTLINFO_INTERNAL_SITES)
        tags.add('in text')
        embedded_links.append(make_tagged_url(url, title, tags))

    for embedded_video_frame in article_body.findAll('iframe'):
        url = embedded_video_frame.get('src')
        title = '[Video] {0}'.format(url)
        tags = classify_and_tag(url, RTLINFO_OWN_NETLOC, RTLINFO_INTERNAL_SITES)
        tags = tags.union(['in text', 'embedded'])
        embedded_links.append(make_tagged_url(url, title, tags))

    return embedded_links



def extract_links_and_text_content(main_article):
    article_body = main_article.find('div', {'class':'articleBody rtl_margin_top_25'})

    embedded_links = extract_embedded_links_from_articlebody(article_body)

    all_paragraphs = article_body.findAll('p', recursive=False)
    cleaned_up_paragraphs = list()
    all_plaintext_urls = list()

    for p in all_paragraphs:
        paragraph = remove_text_formatting_markup_from_fragments(p.contents)
        plaintext_urls = extract_plaintext_urls_from_text(paragraph)
        for url in plaintext_urls:
            tags = classify_and_tag(url, RTLINFO_OWN_NETLOC, RTLINFO_INTERNAL_SITES)
            tags = tags.union(['in text', 'plaintext'])
            all_plaintext_urls.append(make_tagged_url(url, url, tags))

        cleaned_up_paragraphs.append(paragraph)

    all_links = embedded_links+all_plaintext_urls
    return all_links, cleaned_up_paragraphs


def extract_intro(main_article):
    left_column = main_article.find('div', {'id':'leftCol'})
    intro_container = left_column.find('h2', recursive=False)

    if intro_container:
        intro = remove_text_formatting_markup_from_fragments(intro_container.contents)
    else:
        intro = None

    return intro



def extract_article_data(source):
    if hasattr(source, 'read'):
        html_content = source.read()
    else:
        html_content = fetch_content_from_url(source)

    soup = make_soup_from_html_content(html_content)

    main_article= soup.find('div', {'id':'mainArticle'})

    if main_article:
        title = extract_title(main_article)
        category = extract_category(main_article)
        pub_date, pub_time = extract_date_and_time(main_article)
        fetched_datetime = datetime.now()

        links = extract_links(main_article)

        author = None
        embedded_links, content = extract_links_and_text_content(main_article)
        intro = extract_intro(main_article)

        all_links = links+embedded_links

        article_data = ArticleData(source, title, pub_date, pub_time, fetched_datetime, all_links, category, author, intro, content)
        return article_data, html_content

    else:
        return None, html_content



def extract_frontpage_title_and_url(link):
    title = remove_text_formatting_markup_from_fragments(link, ' ')
    return title, link.get('href')



def extract_headlines_from_module(module_container):
    """

    """
    body = module_container.find('div', {'class':'ModuleElementBody'})

    if body:
        headline_lists = body.findAll('div', {'class':'tot_widget-ul'})

        titles_and_urls = list()
        for l in headline_lists:
            for tag_name in ('h3', 'h5', 'li'):
                titles_and_urls.extend([extract_frontpage_title_and_url(h.a) for h in l.findAll(tag_name) if h.a])

        return titles_and_urls
    else:
        return []



def extract_headlines_from_modules(maincontent):
    module_zone = maincontent.find('div', {'id':'hp-zone-list'})

    all_modules = module_zone.findAll('div', {'class':'ModuleElement'})

    headlines = list()
    for module in all_modules:
        module_headlines = extract_headlines_from_module(module)
        headlines.extend(module_headlines)

    return headlines



def extract_small_articles(maincontent):
    small_articles_container = maincontent.find('div', {'id':'SmallArticles'})

    small_articles = small_articles_container.findAll('div', {'class':'SmallArticles-Items'})
    small_articles.extend(small_articles_container.findAll('div', {'class':'SmallArticles-Items SmallArticles-Lasts'}))

    return [extract_frontpage_title_and_url(item.h5.a) for item in small_articles ]



def extract_first_articles(maincontent):
    first_article = maincontent.find('div', {'id':'FirstArticlesLeft'})
    titles_and_urls = list()

    if first_article:
        if first_article.h1:
            titles_and_urls.append(extract_frontpage_title_and_url(first_article.h1.a))
        else:
            video_headline = first_article.find('div', {'class':'img_with_text_on_top_holder'})
            if video_headline:
                url = video_headline.a.get('href')
                title = video_headline.a.img.get('alt')
                titles_and_urls.append((title, url))

    articles_right = maincontent.findAll('div', {'class':'ArticlesRight '})
    articles_right.extend(maincontent.findAll('div', {'class':'ArticlesRight ArticlesRight-First'}))
    articles_right.extend(maincontent.findAll('div', {'class':'ArticlesRight ArticlesRight-Last'}))

    titles_and_urls.extend(extract_frontpage_title_and_url(article.h5.a) for article in articles_right)

    return titles_and_urls



def make_full_url((title, url)):
    if url.startswith('http://'):
        return title, url
    else:
        return title, 'http://www.rtl.be{0}'.format(url)



def separate_news_and_blogposts(titles_and_urls):
    all_items = set(titles_and_urls)
    blogposts = set([(title, url) for title, url in all_items if not url.startswith('/info')])
    news_items = all_items - blogposts

    return news_items, blogposts



def get_frontpage_toc():
    url = 'http://www.rtl.be/info/'
    html_content = fetch_content_from_url(url)
    soup = make_soup_from_html_content(html_content)

    maincontent = soup.find('div', {'class':'mainContent'})

    first_articles = extract_first_articles(maincontent)
    small_articles = extract_small_articles(maincontent)
    modules_articles = extract_headlines_from_modules(maincontent)

    all_articles = first_articles + small_articles + modules_articles

    news_items, blogposts = separate_news_and_blogposts(all_articles)

    return [make_full_url(title_and_url) for title_and_url in news_items], list(blogposts)



def test_sample_data():
    filename = '../../sample_data/rtlinfo_unicode_date.html'
    with open(filename) as f:
        article, raw = extract_article_data(f)
        article.print_summary()


def show_frontpage_news():
    toc, blogs = get_frontpage_toc()
    for t, u in toc:
        print u'fetching: {0}[{1}]'.format(t, u)
        article_data, raw_html = extract_article_data(u)
        if article_data:
            article_data.print_summary()
        else:
            print 'Was redirected to a blogpost'

if __name__=='__main__':
    #show_frontpage_news()
    test_sample_data()



