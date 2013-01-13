#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, time
from BeautifulSoup import Tag
import urlparse
from common.utils import fetch_html_content, make_soup_from_html_content, extract_plaintext_urls_from_text
from common import constants
from csxj.common.tagging import tag_URL, classify_and_tag, make_tagged_url, TaggedURL, print_taggedURLs
from csxj.db.article import ArticleData
from common import ipm_utils

LALIBRE_ASSOCIATED_SITES = {

}

LALIBRE_NETLOC = 'www.lalibre.be'

SOURCE_TITLE = u"La Libre"
SOURCE_NAME = u"lalibre"


def is_on_same_domain(url):
    """
    Until we get all the internal blogs/sites, we can still detect
    if a page is hosted on the same domain.
    """
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    if netloc not in LALIBRE_ASSOCIATED_SITES:
        return netloc.endswith('lalibre.be')
    return False


def classify_and_make_tagged_url(urls_and_titles, additional_tags=set()):
    """
    Classify (with tags) every element in a list of (url, title) tuples
    Returns a list of TaggedURLs
    """
    tagged_urls = []
    for url, title in urls_and_titles:
        tags = classify_and_tag(url, LALIBRE_NETLOC, LALIBRE_ASSOCIATED_SITES)
        if is_on_same_domain(url):
            tags.update(['internal site'])
        tagged_urls.append(make_tagged_url(url, title, tags | additional_tags))
    return tagged_urls


def was_story_updated(date_string):
    return not date_string.startswith('Mis en ligne le')


def extract_date(main_content):
    publication_date = main_content.find('p', {'id': 'publicationDate'}).contents[0]
    publication_date = publication_date.rstrip().lstrip()

    if was_story_updated(publication_date):
        fragments = publication_date.split(' ')
        date_string = fragments[4]
        h, m = [int(i) for i in fragments[-1].split(':')]
        pub_time = time(h, m)
    else:
        date_string = publication_date.replace('Mis en ligne le ', '')
        pub_time = None

    pub_date = datetime.strptime(date_string, '%d/%m/%Y')
    return pub_date.date(), pub_time


def sanitize_fragment(fragment):
    if isinstance(fragment, Tag):
        # sometimes, we just get <p></p>
        if fragment.contents:
            return ''.join(sanitize_fragment(f) for f in fragment.contents)
        else:
            return ''
    else:
        return fragment


def separate_no_target_links(links):
    no_target_links = [(target, title) for (target, title) in links if not target]
    other_links = list(set(links) - set(no_target_links))
    return [('', title) for (target, title) in no_target_links], other_links


def separate_keyword_links(all_links):
    keyword_links = [l for l in all_links if l[0].startswith('/sujet')]
    other_links = list(set(all_links) - set(keyword_links))
    return keyword_links, other_links


def extract_and_tag_in_text_links(article_text):
    """
    Finds the links tags in the html text content.
    Detects which links are keyword and which aren't, sets the adequate tags.
    Returns a list of TaggedURL objects.
    """
    def extract_link_and_title(link):
            return link.get('href'), sanitize_fragment(link.contents[0])
    links = [extract_link_and_title(link)
             for link in article_text.findAll('a', recursive=True)]

    no_target_links, target_links = separate_no_target_links(links)
    keyword_links, other_links = separate_keyword_links(target_links)

    tagged_urls = (
        classify_and_make_tagged_url(keyword_links, additional_tags=set(['keyword', 'in text'])) +
        classify_and_make_tagged_url(other_links, additional_tags=set(['in text'])) +
        classify_and_make_tagged_url(no_target_links, additional_tags=set(['in text', 'no target']))
    )

    return tagged_urls


def sanitize_paragraph(paragraph):
    """Returns plain text article"""
    sanitized_paragraph = [sanitize_fragment(fragment) for fragment in paragraph.contents]
    return ''.join(sanitized_paragraph)


def extract_text_content_and_links(main_content):
    article_text = main_content.find('div', {'id': 'articleText'})

    in_text_tagged_urls = extract_and_tag_in_text_links(article_text)

    all_fragments = []
    all_plaintext_urls = []
    paragraphs = article_text.findAll('p', recursive=False)

    for paragraph in paragraphs:
        fragments = sanitize_paragraph(paragraph)
        all_fragments.append(fragments)
        all_fragments.append('\n')
        plaintext_links = extract_plaintext_urls_from_text(fragments)
        urls_and_titles = zip(plaintext_links, plaintext_links)
        all_plaintext_urls.extend(classify_and_make_tagged_url(urls_and_titles, additional_tags=set(['plaintext'])))

    text_content = all_fragments
    return text_content, in_text_tagged_urls + all_plaintext_urls


def extract_category(main_content):
    breadcrumbs = main_content.find('p', {'id': 'breadCrumbs'})
    links = breadcrumbs.findAll('a', recursive=False)

    return [link.contents[0].rstrip().lstrip() for link in links]



def extract_tagged_url_from_associated_link(link_list_item, tags=[]):
    # sometimes list items are used to show things which aren't links
    # but more like unclickable ads
    url = link_list_item.a.get('href')
    title = sanitize_fragment(link_list_item.a.contents[0].rstrip().lstrip())
    tags = classify_and_tag(url, LALIBRE_NETLOC, LALIBRE_ASSOCIATED_SITES)
    tagged_url = make_tagged_url(url, title, tags)
    return tagged_url


def extract_and_tag_associated_links(main_content):
    """
    Extract the associated links. .

    """
    strong_article_links = main_content.find('div', {'id': 'strongArticleLinks'})
    if not strong_article_links:
        return []

    link_list = strong_article_links.find('ul', {'class': 'articleLinks'})
    tagged_urls = []
    # sometimes there are no links, and thus no placeholder
    if link_list:
        for li in link_list.findAll('li', recursive=False):
            if li.a:
                new_url = extract_tagged_url_from_associated_link(li)
                tagged_urls.append(new_url)

    return tagged_urls


def extract_bottom_links(main_content):
    link_list = main_content.findAll('ul', {'class': 'articleLinks'}, recursive=False)

    tagged_urls = []
    if link_list:
        for li in link_list[0].findAll('li', recursive=False):
            if li.a:
                tagged_urls.append(extract_tagged_url_from_associated_link(li, tags=['bottom']))
            else:
                raise ValueError()
    return tagged_urls


def extract_embedded_content_links(main_content):
    items = main_content.findAll('div', {'class': 'embedContents'})
    return [ipm_utils.extract_tagged_url_from_embedded_item(item, LALIBRE_NETLOC, LALIBRE_ASSOCIATED_SITES) for item in items]


def extract_author_name(main_content):
    writer = main_content.find('p', {'id': 'writer'})
    if writer:
        return writer.contents[0].rstrip().lstrip()
    else:
        return constants.NO_AUTHOR_NAME


def extract_intro(main_content):
    hat = main_content.find('div', {'id': 'articleHat'})

    if hat:
        return hat.contents[0].rstrip().lstrip()
    else:
        return ''


def extract_article_data_from_file(source_url, source_file):

    if not hasattr(source_file, 'read'):
        f = open(source_file)
    else:
        f = source_file

    html_content = f.read()
    return extract_article_data_from_html(html_content, source_url)


def extract_article_data_from_html(html_content, source_url):
    soup = make_soup_from_html_content(html_content)

    main_content = soup.find('div', {'id': 'mainContent'})

    if main_content.h1:
        title = main_content.h1.contents[0].rstrip().lstrip()
    else:
        return None, html_content

    category = extract_category(main_content)
    author = extract_author_name(main_content)
    pub_date, pub_time = extract_date(main_content)
    fetched_datetime = datetime.today()

    intro = extract_intro(main_content)
    text_content, in_text_urls = extract_text_content_and_links(main_content)

    associated_tagged_urls = extract_and_tag_associated_links(main_content)
    bottom_links = extract_bottom_links(main_content)
    embedded_content_links = extract_embedded_content_links(main_content)
    all_links = in_text_urls + associated_tagged_urls + bottom_links + embedded_content_links

    new_article = ArticleData(source_url, title,
                              pub_date, pub_time, fetched_datetime,
                              all_links,
                              category, author,
                              intro, text_content)

    return new_article, html_content


def extract_article_data(source):
    """
    """
    if hasattr(source, 'read'):
        html_content = source.read()
    else:
        html_content = fetch_html_content(source)

    return extract_article_data_from_html(html_content, source)


def get_frontpage_toc():
    hostname_url = 'http://www.lalibre.be'
    html_content = fetch_html_content(hostname_url)

    soup = make_soup_from_html_content(html_content)

    article_list_container = soup.find('div', {'id': 'mainContent'})
    announces = article_list_container.findAll('div', {'class': 'announce'}, recursive=False)

    def extract_title_and_link(announce):
        title, url = announce.h1.a.contents[0], announce.h1.a.get('href')
        return title, '{0}{1}'.format(hostname_url, url)

    return [extract_title_and_link(announce) for announce in announces], []


def test_sample_data():
    urls = ["http://www.lalibre.be/economie/actualite/article/704138/troisieme-belgian-day-a-wall-street.html",
            "http://www.lalibre.be/culture/selection-culturelle/article/707244/ou-sortir-ce-week-end.html",
            "http://www.lalibre.be/actu/usa-2012/article/773294/obama-raille-les-chevaux-et-baionnettes-de-romney.html",
            "http://www.lalibre.be/actu/international/article/774524/sandy-le-calme-avant-la-tempete.html",
            "http://www.lalibre.be/sports/football/article/778966/suivez-anderlecht-milan-ac-en-live-des-20h30.html",
            ]

    for url in urls[:]:
        article, html = extract_article_data(url)

        if article:
            print u"{0}".format(article.title)
            article.print_summary()
            print_taggedURLs(article.links)

        print("\n" * 4)


def list_frontpage_articles():
    frontpage_items = get_frontpage_toc()
    print len(frontpage_items)

    for (title, url) in frontpage_items:
        print 'fetching data for article :', title

        article, html_content = extract_article_data(url)
        article.print_summary()

        for (url, title, tags) in article.internal_links:
            print u'{0} -> {1} {2}'.format(url, title, tags)

        for (url, title, tags) in article.external_links:
            print u'{0} -> {1} {2}'.format(url, title, tags)

        print '-' * 80


if __name__ == '__main__':
    #list_frontpage_articles()
    test_sample_data()
