#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, time
import urlparse

import BeautifulSoup

from csxj.common.tagging import classify_and_tag, make_tagged_url, update_tagged_urls
from csxj.db.article import ArticleData
from parser_tools.utils import fetch_html_content, make_soup_from_html_content, extract_plaintext_urls_from_text
from parser_tools.utils import remove_text_formatting_markup_from_fragments, TEXT_MARKUP_TAGS
from parser_tools import constants
from parser_tools import ipm_utils
from parser_tools import twitter_utils

from helpers.unittest_generator import generate_test_func, save_sample_data_file

LALIBRE_ASSOCIATED_SITES = {
    'ask.blogs.lalibre.be': ['internal', 'jblog'],
    'irevolution.blogs.lalibre.be': ['internal', 'jblog'],
    'laloidesseries.blogs.lalibre.be': ['internal', 'jblog'],
    'letitsound.blogs.lalibre.be': ['internal', 'jblog'],
    'parislibre.blogs.lalibre.be': ['internal', 'jblog'],
    'momento.blogs.lalibre.be': ['internal', 'jblog'],
    'lameteo.blogs.lalibre.be': ['internal', 'jblog'],

    'pdf-online.lalibre.be' : ['internal', 'pdf newspaper']

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
        return link.get('href'), remove_text_formatting_markup_from_fragments(link.contents)

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

    sanitized_paragraph = [remove_text_formatting_markup_from_fragments(fragment, strip_chars='\t\r\n') for fragment in paragraph.contents if
                           not isinstance(fragment, BeautifulSoup.Comment)]

    return ''.join(sanitized_paragraph)


def extract_text_content_and_links(main_content):
    article_text = main_content.find('div', {'id': 'articleText'})

    in_text_tagged_urls = []
    all_fragments = []
    all_plaintext_urls = []
    embedded_tweets = []

    def is_text_content(blob):
        if isinstance(blob, BeautifulSoup.Tag) and blob.name in TEXT_MARKUP_TAGS:
            return True
        if isinstance(blob, BeautifulSoup.NavigableString):
            return True
        return False

    paragraphs = [c for c in article_text.contents if is_text_content(c)]

    for paragraph in paragraphs:
        if isinstance(paragraph, BeautifulSoup.NavigableString):
            cleaned_up_text = remove_text_formatting_markup_from_fragments([paragraph], strip_chars='\r\n\t ')
            if cleaned_up_text:
                all_fragments.append(cleaned_up_text)
                plaintext_links = extract_plaintext_urls_from_text(paragraph)
                urls_and_titles = zip(plaintext_links, plaintext_links)
                all_plaintext_urls.extend(classify_and_make_tagged_url(urls_and_titles, additional_tags=set(['plaintext'])))
        else:
            if not paragraph.find('blockquote', {'class': 'twitter-tweet'}):
                in_text_links = extract_and_tag_in_text_links(paragraph)
                in_text_tagged_urls.extend(in_text_links)

                fragments = sanitize_paragraph(paragraph)
                all_fragments.append(fragments)
                plaintext_links = extract_plaintext_urls_from_text(fragments)
                urls_and_titles = zip(plaintext_links, plaintext_links)
                all_plaintext_urls.extend(classify_and_make_tagged_url(urls_and_titles, additional_tags=set(['plaintext'])))
            else:
                embedded_tweets.extend(
                    twitter_utils.extract_rendered_tweet(paragraph, LALIBRE_NETLOC, LALIBRE_ASSOCIATED_SITES))

    text_content = all_fragments

    return text_content, in_text_tagged_urls + all_plaintext_urls + embedded_tweets


def extract_category(main_content):
    breadcrumbs = main_content.find('p', {'id': 'breadCrumbs'})
    links = breadcrumbs.findAll('a', recursive=False)

    return [link.contents[0].rstrip().lstrip() for link in links]


def extract_embedded_content_links(main_content):
    items = main_content.findAll('div', {'class': 'embedContents'})
    return [ipm_utils.extract_tagged_url_from_embedded_item(item, LALIBRE_NETLOC, LALIBRE_ASSOCIATED_SITES) for item in
            items]


def extract_author_name(main_content):
    writer = main_content.find('p', {'id': 'writer'})
    if writer:
        return writer.contents[0].rstrip().lstrip()
    else:
        return constants.NO_AUTHOR_NAME


def extract_intro(main_content):
    hat = main_content.find('div', {'id': 'articleHat'})

    if hat:
        return  remove_text_formatting_markup_from_fragments(hat.contents, strip_chars='\t\r\n ')
    else:
        return u''


def extract_article_data_from_file(source_url, source_file):
    if not hasattr(source_file, 'read'):
        f = open(source_file)
    else:
        f = source_file

    html_content = f.read()
    return extract_article_data_from_html(html_content, source_url)

def print_for_test(taggedURLs):
    print "---"
    for taggedURL in taggedURLs:
        print u"""make_tagged_url("{0}", u\"\"\"{1}\"\"\", {2}),""".format(taggedURL.URL, taggedURL.title,
                                                                           taggedURL.tags)

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

    embedded_audio_links = ipm_utils.extract_embedded_audio_links(main_content, LALIBRE_NETLOC,
                                                                  LALIBRE_ASSOCIATED_SITES)
    associated_tagged_urls = ipm_utils.extract_and_tag_associated_links(main_content, LALIBRE_NETLOC,
                                                                        LALIBRE_ASSOCIATED_SITES)
    bottom_links = ipm_utils.extract_bottom_links(main_content, LALIBRE_NETLOC, LALIBRE_ASSOCIATED_SITES)
    embedded_content_links = extract_embedded_content_links(main_content)

    all_links = in_text_urls + associated_tagged_urls + bottom_links + embedded_content_links + embedded_audio_links

    updated_tagged_urls = update_tagged_urls(all_links, ipm_utils.LALIBRE_SAME_OWNER)

    new_article = ArticleData(source_url, title,
                              pub_date, pub_time, fetched_datetime,
                              updated_tagged_urls,
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
            "http://www.lalibre.be/societe/insolite/article/786611/le-tweet-sarcastique-de-johnny-a-gege.html",
            "http://www.lalibre.be/actu/belgique/article/782423/intemperies-un-chaos-moins-important-que-prevu.html",
            "http://www.lalibre.be/culture/mediastele/article/748553/veronique-genest-mon-coeur-est-en-berne.html",
            "http://www.lalibre.be/culture/musique-festivals/article/792049/the-weeknd-de-retour-en-belgique.html",
            "http://www.lalibre.be/actu/international/article/791997/israel-une-campagne-qui-n-a-pas-vole-haut.html",
            "http://www.lalibre.be/economie/actualite/article/789261/le-fmi-s-est-trompe-et-fait-son-mea-culpa.html",
            "http://www.lalibre.be/societe/general/article/779522/la-pornographie-une-affaire-d-hommes-pas-seulement.html"]

    article, html = extract_article_data(urls[-1])


if __name__ == '__main__':
    test_sample_data()
