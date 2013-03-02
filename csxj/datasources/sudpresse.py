# -*- coding: utf-8 -*-

from datetime import datetime, date, time
from itertools import chain
import urllib
from BeautifulSoup import Tag, NavigableString
from parser_tools.utils import make_soup_from_html_content, fetch_content_from_url, fetch_html_content
from parser_tools.utils import extract_plaintext_urls_from_text
from parser_tools.utils import remove_text_formatting_markup_from_fragments, remove_text_formatting_and_links_from_fragments
from parser_tools.utils import setup_locales
from csxj.common.tagging import classify_and_tag, make_tagged_url, update_tagged_urls
from csxj.db.article import ArticleData

from parser_tools import rossel_utils

from helpers.unittest_generator import generate_test_func, save_sample_data_file

setup_locales()


SUDPRESSE_INTERNAL_SITES = {
    'portfolio.sudpresse.be': ['internal', 'gallery'],

    'pdf.lameuse.be': ['internal', 'pdf newspaper'],
    'pdf.lacapitale.be': ['internal', 'pdf newspaper'],
    'pdf.lanouvellegazette.be': ['internal', 'pdf newspaper'],
    'pdf.laprovince.be': ['internal', 'pdf newspaper'],
    'pdf.nordeclair.be': ['internal', 'pdf newspaper']
}

SUDPRESSE_OWN_NETLOC = 'www.sudpresse.be'

SOURCE_TITLE = u"Sud Presse"
SOURCE_NAME = u"sudpresse"


def extract_category(content):
    breadcrumbs = content.find('p', {'class': 'ariane'})
    if breadcrumbs:
        return [link.contents[0].strip() for link in breadcrumbs.findAll('a')]
    else:
        alternate_breadcrumbs = content.find('p', {'class': 'fil_ariane left'})
        return [link.contents[0].strip() for link in alternate_breadcrumbs.findAll('a')]


def extract_title(article):
    return article.h1.contents[0].strip()


def extract_date(article):
    pub_date_container = article.find('p', {'class': 'publiele'})

    today = datetime.today()

    date_string = pub_date_container.span.contents[0]
    d, m = [int(i) for i in date_string.split('/')]
    pub_date = date(today.year, m, d)

    hour, minutes = pub_date_container.contents[2], pub_date_container.contents[4]
    h = int(hour.split(u'à')[1])
    m = int(minutes)
    pub_time = time(h, m)

    return pub_date, pub_time


def extract_author_name(article):
    return article.find('p', {'class': 'auteur'}).contents[0].strip()


def extract_text_and_links_from_paragraph(paragraph):
    def extract_url_and_title(link):
        if isinstance(link.contents[0], Tag):
            if link.contents[0].name == 'img':
                img_target = link.contents[0].get('src')
                return link.get('href'), '(img){0}'.format(img_target)
            else:
                title = remove_text_formatting_markup_from_fragments(link.contents)
                return link.get('href'), title
        else:
            return link.get('href'), remove_text_formatting_markup_from_fragments(link.contents)

    # Why do we filter on link.contents? Because sometimes there
    # are <a id="more"></a> links which point to nothing.
    # Awesome.
    urls_and_titles = [extract_url_and_title(link) for link in paragraph.findAll('a', recursive=False) if link.contents]

    tagged_urls = list()

    for url, title in urls_and_titles:
        tags = classify_and_tag(url, SUDPRESSE_OWN_NETLOC, SUDPRESSE_INTERNAL_SITES)
        tags.update(['in text'])
        tagged_urls.append(make_tagged_url(url, title, tags))


    text_fragments = paragraph.contents

    if text_fragments:
        text = u"".join(remove_text_formatting_markup_from_fragments(text_fragments))

        plaintext_urls = extract_plaintext_urls_from_text(remove_text_formatting_and_links_from_fragments(text_fragments))
        for url in plaintext_urls:
            tags = classify_and_tag(url, SUDPRESSE_OWN_NETLOC, SUDPRESSE_INTERNAL_SITES)
            tags.update(['plaintext', 'in text'])

            tagged_urls.append(make_tagged_url(url, url, tags))
    else:
        text = u""

    return text, tagged_urls


def extract_intro_and_links(article):
    intro_container = article.find('p', {'class': 'chapeau'})
    intro_text, tagged_urls = extract_text_and_links_from_paragraph(intro_container)
    return intro_text, tagged_urls


def extract_content_and_links(article):
    all_paragraphs = article.findAll('p', recursive=False)

    content_paragraphs = [p for p in all_paragraphs if p.get('class') not in ['ariane', 'chapeau', 'auteur', 'publiele']]

    all_content_paragraphs = list()
    all_tagged_urls = list()
    for p in content_paragraphs:
        cleaned_up_text, tagged_urls = extract_text_and_links_from_paragraph(p)
        all_content_paragraphs.append(cleaned_up_text)
        all_tagged_urls.extend(tagged_urls)

    return all_content_paragraphs, all_tagged_urls


LINK_TYPE_TO_TAG = {
    'media-video': ['video'],
    'media-press': [],
}


def extract_associated_links(article):
    links_block = article.find('div', {'class': 'bloc-01'})

    if links_block:
        link_list = links_block.find('ul')

        def extract_url_and_title(item):
            url = item.a.get('href')
            title = remove_text_formatting_markup_from_fragments(item.a.contents)

            tags = set()
            if not title:
                title = u'No Title'
                tags.add('ghost link')
            return url, title, tags

        all_tagged_urls = list()
        for item in link_list.findAll('li'):
            url, title, tags = extract_url_and_title(item)
            tags.update(classify_and_tag(url, SUDPRESSE_OWN_NETLOC, SUDPRESSE_INTERNAL_SITES))

            link_type = item.get('class')
            if link_type in LINK_TYPE_TO_TAG:
                tags.update(LINK_TYPE_TO_TAG[link_type])

            tags.add("sidebar box")

            all_tagged_urls.append(make_tagged_url(url, title, tags))

        return all_tagged_urls
    else:
        return []


def extract_embedded_media(article):
    tagged_urls = list()
    # extract any iframe from maincontent
    iframes = article.findAll("iframe")
    for media in iframes:
        url = media.get('src')
        tags = classify_and_tag(url, SUDPRESSE_OWN_NETLOC, SUDPRESSE_INTERNAL_SITES)
        tags.add('embedded')
        tags.add('iframe')
        tagged_url = make_tagged_url(url, url, tags)
        tagged_urls.append(tagged_url)

    return tagged_urls


def is_page_error_404(soup):

    return soup.head.title.contents[0] == '404'


def extract_article_data(source):
    """
    """
    if hasattr(source, 'read'):
        html_content = source.read()
    else:
        html_content = fetch_html_content(source)

    soup = make_soup_from_html_content(html_content)

    if is_page_error_404(soup):
        return None, html_content
    else:
        content = soup.find('div', {'id': 'content'})
        category = extract_category(content)

        article = soup.find('div', {'id': 'article'})
        title = extract_title(article)
        pub_date, pub_time = extract_date(article)
        author = extract_author_name(article)

        fetched_datetime = datetime.today()

        intro, intro_links = extract_intro_and_links(article)
        content, content_links = extract_content_and_links(article)

        associated_links = extract_associated_links(article)
        embedded_media = extract_embedded_media(article)

        all_links = intro_links + content_links + associated_links + embedded_media

        updated_tagged_urls = update_tagged_urls(all_links, rossel_utils.SUDINFO_SAME_OWNER)

        #print generate_test_func('intext_links_tagging', 'sudpresse', dict(tagged_urls=updated_tagged_urls))
        #save_sample_data_file(html_content, source.name, 'intext_links_tagging', '/Users/judemaey/code/csxj-crawler/tests/datasources/test_data/sudpresse')

        return ArticleData(source, title, pub_date, pub_time, fetched_datetime,
                           updated_tagged_urls,
                           category, author,
                           intro, content), html_content


def extract_title_and_url(container):
    if container.h1 and container.h1.a:
        link = container.h1.a
        return link.contents[0].strip(), link.get('href')


def extract_title_and_url_in_buzz(container):
        if container.h2 and container.h2.a:
            link = container.h2.a
            return link.contents[0].strip(), link.get('href')


def extract_headlines_from_buzz(column):
    buzz_container = column.find('div', {'class': 'buzz exergue clearfix'})

    main_buzzes = buzz_container.findAll('div')
    buzz_stories = [extract_title_and_url_in_buzz(b) for b in main_buzzes]

    def extract_title_and_url_from_list_item(item):
        return item.a.contents[0].strip(), item.a.get('href')

    buzz_list = buzz_container.ul.findAll('li')
    buzz_stories.extend([extract_title_and_url_from_list_item(item) for item in buzz_list])

    return buzz_stories


def extract_headlines_from_wrap_columns(column):
    wrap_columns = column.findAll('div', {'class': 'wrap-columns clearfix'})
    stories_by_column = [col.findAll('div', {'class': 'article lt clearfix'}) for col in wrap_columns]
    stories_by_column.extend([col.findAll('div', {'class': 'article lt clearfix noborder'}) for col in wrap_columns])

    # flatten the result list
    all_stories = chain(*stories_by_column)

    return [extract_title_and_url(story) for story in all_stories]


def extract_main_headline(column):
    main_headline = column.find('div', {'class': 'article gd clearfix'})
    return extract_title_and_url(main_headline)


def extract_headlines_from_regular_stories(column):
    regular_stories = column.findAll('div', {'class': 'article md clearfix noborder'})
    return [extract_title_and_url(story) for story in regular_stories]


def extract_headlines_from_column_1(column):
    all_headlines = list()
    all_headlines.append(extract_main_headline(column))
    all_headlines.extend(extract_headlines_from_regular_stories(column))
    all_headlines.extend(extract_headlines_from_wrap_columns(column))
    all_headlines.extend(extract_headlines_from_buzz(column))

    return all_headlines


def extract_headlines_from_column_3(column):
    stories = column.findAll('div', {'class': 'octetFun'})

    last_story = column.findAll('div', {'class': 'octetFun noborder'})
    if last_story:
        stories.append(last_story[0])

    headlines = list()
    for story in stories:
        if story.h3.a.contents:
            clean_title = remove_text_formatting_markup_from_fragments(story.h3.a.contents)
            if story.h3.a.get('href'):
                title_and_url = clean_title, story.h3.a.get('href')
                headlines.append(title_and_url)

    return headlines


def extract_headlines_for_one_region(region_container):
    main_story = region_container.h3.a.contents[0].strip(), region_container.h3.a.get('href')

    story_list = region_container.find('ul', {'class': 'story_list'})

    def extract_title_and_link(item):
        return item.a.contents[0].strip(), item.a.get('href')

    headlines = [main_story]
    headlines.extend([extract_title_and_link(item) for item in story_list.findAll('li')])

    return headlines


def extract_regional_headlines(content):
    region_containers = content.findAll('div', {'class': 'story secondaire couleur_03'})

    return list(chain(*[extract_headlines_for_one_region(c) for c in region_containers]))


def get_regional_toc():
    url = 'http://sudpresse.be/regions'
    html_content = fetch_content_from_url(url)
    soup = make_soup_from_html_content(html_content)

    return extract_regional_headlines(soup.find('div', {'id': 'content_first'}))


def make_full_url(prefix, titles_and_urls):
    return [(title, urllib.basejoin(prefix, url)) for title, url in titles_and_urls]


def get_frontpage_toc():
    url = 'http://sudpresse.be/'
    html_content = fetch_content_from_url(url)
    soup = make_soup_from_html_content(html_content)

    column1 = soup.find('div', {'class': 'column col-01'})
    headlines = extract_headlines_from_column_1(column1)
    column3 = soup.find('div', {'class': 'column col-03'})
    headlines.extend(extract_headlines_from_column_3(column3))

    regional_headlines = make_full_url(url, get_regional_toc())
    headlines.extend(regional_headlines)

    return make_full_url(url, headlines), [], []


def show_frontpage_articles():
    toc, blogs = get_frontpage_toc()

    print len(toc)
    for title, url in toc[:]:
        print
        print url
        article_data, html_content = extract_article_data(url)

        article_data.print_summary()
        print article_data.to_json()


def test_sample_data():
    filepath = '../../sample_data/sudpresse_some_error.html'
    filepath = '../../sample_data/sudpresse_associated_link_error.html'
    filepath = "/Volumes/Curst/json_db_0_5/sudpresse/2012-01-09/11.05.13/raw_data/0.html"
    filepath = "../../sample_data/sudpresse/sudpresse_noTitle.html"
    filepath = "../../sample_data/sudpresse/sudpresse_noTitle2.html"
    filepath = "../../sample_data/sudpresse/sudpresse_erreur1.html"
    filepath = "../../sample_data/sudpresse/sudpresse_same_owner.html"
    filepath = "../../sample_data/sudpresse/sudpresse_associated_link_error.html"
    filepath = "../../sample_data/sudpresse/sudpresse_live_article.html"
    filepath = "../../sample_data/sudpresse/sudpresse_erreur1.html"
    filepath = "../../sample_data/sudpresse/sudpresse_true_plaintext.html"
    filepath = "../../sample_data/sudpresse/sudpresse_fake_plaintext.html"
    filepath = "../../tests/datasources/test_data/sudpresse/intext_links_tagging.html"
    with open(filepath) as f:
        article_data, raw = extract_article_data(f)
        print article_data.content

        for link in article_data.links:
            print link.URL
            print link.title
            print link.tags
            print "**********************"


def download_one_article():
    url = 'http://www.sudpresse.be/regions/liege/2012-01-09/liege-un-mineur-d-age-et-un-majeur-apprehendes-pour-un-viol-collectif-930314.shtml'
    url = 'http://sudpresse.be/actualite/dossiers/2012-01-02/le-stage-du-standard-a-la-manga-infos-photos-tweets-928836.shtml'
    #url = 'http://sudpresse.be/%3C!--%20error:%20linked%20page%20doesn\'t%20exist:...%20--%3E'
    url = "http://sudpresse.be/actualite/faits_divers/2012-01-10/un-enfant-de-4-ans-orphelin-sa-mere-a-saute-sur-les-voies-pour-recuperer-son-gsm-930520.shtml"
    url = "http://sudpresse.be/regions/tournai/2012-02-13/jean-dujardin-sera-ce-soir-a-lille-938309.shtml"
    article_data, raw_html = extract_article_data(url)

    for link in article_data.links:
        print link

if __name__ == '__main__':
    #get_frontpage_toc()
    #download_one_article()
    test_sample_data()
