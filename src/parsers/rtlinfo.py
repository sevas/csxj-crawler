import sys
from datetime import datetime, time
import locale

from utils import fetch_content_from_url, make_soup_from_html_content, remove_text_formatting_markup
from article import ArticleData, make_tagged_url, classify_and_tag


# for datetime conversions
if sys.platform in ['linux2', 'cygwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF8')
elif sys.platform in [ 'darwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR')


def extract_title(main_article):
    left_column = main_article.find('div', {'id':'leftCol'})
    title = left_column.find('h1', {'class':'rtl_font_weight_normal'})

    return ''.join([remove_text_formatting_markup(fragment) for fragment in title.contents])



def extract_date_and_time(main_article):
    date_container = main_article.find('span', {'class':'date'})
    date_string = date_container.contents[0].strip()

    pub_date = datetime.strptime(date_string, '%d %B %Y')

    time_container = date_container.find('span', {'class':'time'})
    time_string=  time_container.contents[0]
    h, m = [int(i) for i in time_string.split('h')]
    pub_time = time(h, m)

    return pub_date, pub_time



def extract_category(main_article):
    breadcrumb_container = main_article.find('div', {'id':'breadcrumb'})
    breadcrumbs = [''.join(link.contents) for link in  breadcrumb_container.findAll('a')]

    return breadcrumbs



def extract_article_data(html_content):
    soup = make_soup_from_html_content(html_content)

    main_article= soup.find('div', {'id':'mainArticle'})

    title = extract_title(main_article)
    category = extract_category(main_article)
    pub_date, pub_time = extract_date_and_time(main_article)

    print category
    print pub_date, pub_time
    print title





def extract_frontpage_title_and_url(link):
    title = ''.join([remove_text_formatting_markup(c.strip()) for c in link.contents])
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
    blogposts = set([(title, url) for title, url in all_items if not url.startswith('/')])
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

    return [make_full_url(title_and_url) for title_and_url in news_items], blogposts



def test_sample_data():
    filename = '../../sample_data/rtlinfo_sample.html'
    with open(filename) as f:
        html_content = f.read()

        extract_article_data(html_content)
    




if __name__=='__main__':
    toc, blogs = get_frontpage_toc()

    for t, u in toc:
        print t

    #test_sample_data()


