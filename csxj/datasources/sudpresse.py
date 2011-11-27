# -*- coding: utf-8 -*-

import sys
from datetime import datetime, date, time
import locale
from itertools import chain
import urllib
from BeautifulSoup import Tag
from common.utils import make_soup_from_html_content, fetch_content_from_url, fetch_html_content
from common.utils import extract_plaintext_urls_from_text, remove_text_formatting_markup
from common.utils import remove_text_formatting_markup_from_fragments
from csxj.common.tagging import tag_URL, classify_and_tag, make_tagged_url, TaggedURL
from csxj.db.article import ArticleData


# for datetime conversions
if sys.platform in ['linux2', 'cygwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF8')
elif sys.platform in [ 'darwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR')


SUDPRESSE_INTERNAL_SITES = {
    'portfolio.sudpresse.be':['internal site', 'images', 'gallery']
}

SUDPRESSE_OWN_NETLOC = 'sudpresse.be'

SOURCE_TITLE = "Sud Presse"
SOURCE_NAME = "sudpresse"

def extract_category(content):
    breadcrumbs = content.find('p', {'class':'ariane'})
    if breadcrumbs:
        return [link.contents[0].strip() for link in breadcrumbs.findAll('a')]
    else:
        alternate_breadcrumbs = content.find('p', {'class':'fil_ariane left'})
        return [link.contents[0].strip() for link in alternate_breadcrumbs.findAll('a')]


def extract_title(article):
    return article.h1.contents[0].strip()



def extract_date(article):
    pub_date_container = article.find('p', {'class':'publiele'})

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
    return article.find('p', {'class':'auteur'}).contents[0].strip()



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

    urls_and_titles = [extract_url_and_title(link) for link in paragraph.findAll('a', recursive=False)]

    tagged_urls = list()
    for url, title in urls_and_titles:
        tags = classify_and_tag(url, SUDPRESSE_OWN_NETLOC, SUDPRESSE_INTERNAL_SITES)
        tags.update(['in text'])
        tagged_urls.append(make_tagged_url(url, title, tags))

    text = ''.join(remove_text_formatting_markup(p) for p in paragraph.contents)

    plaintext_urls = extract_plaintext_urls_from_text(text)
    for url in plaintext_urls:
        tags = classify_and_tag(url, SUDPRESSE_OWN_NETLOC, SUDPRESSE_INTERNAL_SITES)
        tags.update(['plaintext', 'in text'])
        tagged_urls.append(make_tagged_url(url, url, tags))

    return text, tagged_urls



def extract_intro_and_links(article):
    intro_container = article.find('p', {'class':'chapeau'})
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
    'media-video':['video'],
    'media-press':[],
}


def extract_associated_links(article):
    links_block = article.find('div', {'class':'bloc-01'})

    if links_block:
        link_list = links_block.find('ul')


        def extract_url_and_title(item):
            url = item.a.get('href')
            title = ''.join(remove_text_formatting_markup(c) for c in  item.a.contents)

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
            if  link_type in LINK_TYPE_TO_TAG:
                tags.update(LINK_TYPE_TO_TAG[link_type])

            all_tagged_urls.append(make_tagged_url(url, title, tags))

        return all_tagged_urls
    else:
        return []


def extract_article_data(source):
    """
    """
    if hasattr(source, 'read'):
        html_content = source.read()
    else:
        html_content = fetch_html_content(source)

    soup = make_soup_from_html_content(html_content)


    content = soup.find('div', {'id':'content'})
    category = extract_category(content)

    article = soup.find('div', {'id':'article'})
    title = extract_title(article)
    pub_date, pub_time = extract_date(article)
    author = extract_author_name(article)

    fetched_datetime = datetime.today()
    
    intro, intro_links = extract_intro_and_links(article)
    content, content_links = extract_content_and_links(article)

    associated_links = extract_associated_links(article)

    return ArticleData(source, title, pub_date, pub_time, fetched_datetime,
                       intro_links + content_links + associated_links,
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
    buzz_container = column.find('div', {'class':'buzz exergue clearfix'})
    
    main_buzzes = buzz_container.findAll('div')
    buzz_stories = [extract_title_and_url_in_buzz(b) for b in main_buzzes]

    def extract_title_and_url_from_list_item(item):
        return item.a.contents[0].strip(), item.a.get('href')

    buzz_list = buzz_container.ul.findAll('li')
    buzz_stories.extend([extract_title_and_url_from_list_item(item) for item in buzz_list])

    return buzz_stories


def extract_headlines_from_wrap_columns(column):
    wrap_columns = column.findAll('div', {'class':'wrap-columns clearfix'})
    stories_by_column = [col.findAll('div', {'class':'article lt clearfix'}) for col in wrap_columns]
    stories_by_column.extend([col.findAll('div', {'class':'article lt clearfix noborder'}) for col in wrap_columns])

    # flatten the result list
    all_stories = chain(*stories_by_column)

    return [extract_title_and_url(story) for story in all_stories]



def extract_main_headline(column):
    main_headline = column.find('div', {'class':'article gd clearfix'})
    return extract_title_and_url(main_headline)



def extract_headlines_from_regular_stories(column):
    regular_stories = column.findAll('div', {'class':'article md clearfix noborder'})
    return [extract_title_and_url(story) for story in regular_stories]



def extract_headlines_from_column_1(column):
    all_headlines = list()
    all_headlines.append(extract_main_headline(column))
    all_headlines.extend(extract_headlines_from_regular_stories(column))
    all_headlines.extend(extract_headlines_from_wrap_columns(column))
    all_headlines.extend(extract_headlines_from_buzz(column))

    return all_headlines



def extract_headlines_from_column_3(column):

    stories = column.findAll('div', {'class':'octetFun'})

    headlines = list()
    for story in stories:
        if story.h3.a.contents:
            clean_title =   remove_text_formatting_markup_from_fragments(story.h3.a.contents)
            title_and_url = clean_title, story.h3.a.get('href')
            headlines.append(title_and_url)

    return headlines


def extract_headlines_for_one_region(region_container):
    main_story = region_container.h3.a.contents[0].strip(), region_container.h3.a.get('href')

    story_list = region_container.find('ul', {'class':'story_list'})
    def extract_title_and_link(item):
        return item.a.contents[0].strip(), item.a.get('href')

    headlines = [main_story]
    headlines.extend([extract_title_and_link(item) for item in story_list.findAll('li')])

    return headlines



def extract_regional_headlines(content):
    region_containers = content.findAll('div', {'class':'story secondaire couleur_03'})

    return list(chain(*[extract_headlines_for_one_region(c) for c in region_containers]))



def get_regional_toc():
    url = 'http://sudpresse.be/regions'
    html_content = fetch_content_from_url(url)
    soup = make_soup_from_html_content(html_content)

    return extract_regional_headlines(soup.find('div', {'id':'content_first'}))



def make_full_url(prefix, titles_and_urls):
    return [(title, urllib.basejoin(prefix, url)) for title, url in titles_and_urls]



def get_frontpage_toc():
    url = 'http://sudpresse.be/'
    html_content = fetch_content_from_url(url)
    soup = make_soup_from_html_content(html_content)

    column1 = soup.find('div', {'class':'column col-01'})
    headlines = extract_headlines_from_column_1(column1)
    column3  = soup.find('div', {'class':'column col-03'})
    headlines.extend(extract_headlines_from_column_3(column3))


    regional_headlines = make_full_url(url, get_regional_toc())
    headlines.extend(regional_headlines)

    return make_full_url(url, headlines), []



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
    with open(filepath) as f:
        article_data, raw = extract_article_data(f)
        article_data.print_summary()

        for link in article_data.links:
            print link.title
        



if __name__=='__main__':
    show_frontpage_articles()
    #test_sample_data()