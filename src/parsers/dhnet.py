#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
from datetime import datetime, time
from itertools import chain
import re
from BeautifulSoup import Tag
from utils import fetch_html_content, make_soup_from_html_content, remove_text_formatting_markup, extract_plaintext_urls_from_text
from article import ArticleData, tag_URL, make_tagged_url, classify_and_tag

# for datetime conversions
if sys.platform in ['linux2', 'cygwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF8')
elif sys.platform in [ 'darwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR')


DHNET_INTERNAL_SITES = {
    'tackleonweb.blogs.dhnet.be':['internal blog', 'internal', 'sports'],
    'galeries.dhnet.be':['internal site', 'image gallery'],
}

DHNET_NETLOC = 'www.dhnet.be'


def classify_and_make_tagged_url(urls_and_titles, additional_tags=[]):
    """
    Classify (with tags) every element in a list of (url, title) tuples
    Returns a list of TaggedURLs
    """
    tagged_urls = []
    for url, title in urls_and_titles:
        tags = classify_and_tag(url, DHNET_NETLOC, DHNET_INTERNAL_SITES)
        tagged_urls.append(make_tagged_url(url, title, tags+additional_tags))
    return tagged_urls



def cleanup_text_fragment(text_fragment):
    """
    Recursively cleans up a text fragment (e.g. nested tags).
    Returns a plain text string with no formatting info whatsoever.
    """
    if isinstance(text_fragment, Tag):
        return ''.join([cleanup_text_fragment(f) for f in text_fragment.contents])
    else:
        return text_fragment




def filter_out_useless_fragments(text_fragments):
    """
    Removes all <br /> tags and '\n' string from a list of text fragments
    extracted from an article.
    """
    def is_linebreak(text_fragment):
        if isinstance(text_fragment, Tag):
            return text_fragment.name == 'br'
        else:
            return len(text_fragment.strip()) == 0
    
    return [fragment for fragment in text_fragments if not is_linebreak(fragment)]



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
            return link.get('href'),  link.contents[0]
    links = [extract_link_and_title(link)
             for link in article_text.findAll('a', recursive=True)]

    keyword_links, other_links = separate_keyword_links(links)

    tagged_urls = (classify_and_make_tagged_url(keyword_links, additional_tags=['keyword', 'in text']) +
                   classify_and_make_tagged_url(other_links, additional_tags=['in text']))

    return tagged_urls



def extract_text_content_and_links_from_articletext(article_text):
    """
    Cleans up the text from html tags, extracts and tags all
    links (clickable _and_ plaintext).

    Returns a list of string (one item per paragraph) and a
    list of TaggedURL objects.

    Note: sometimes paragraphs are clearly marked with nice <p> tags. When it's not
    the case, we consider linebreaks to be paragraph separators. 
    """

    in_text_tagged_urls = extract_and_tag_in_text_links(article_text)


    children = filter_out_useless_fragments(article_text.contents)
    # first child is the intro paragraph, discard it
    children = children[1:]

    # the rest might be a list of paragraphs, but might also just be the text, sometimes with
    # formatting.
    TEXT_MARKUP_TAGS = ['b', 'i', 'u', 'em', 'strong', 'tt', 'h1',  'h2',  'h3',  'h4',  'h5',  ]
    cleaned_up_text_fragments = []
    
    for child in children:
        if isinstance(child, Tag):
            if child.name in TEXT_MARKUP_TAGS:
                cleaned_up_text_fragments.append(''.join([cleanup_text_fragment(f)
                                                          for f in child.contents]))
            elif child.name == 'p':
                cleaned_up_text_fragments.append(''.join([cleanup_text_fragment(f)
                                                          for f in child.contents]))
        else:
            cleaned_up_text_fragments.append(child)


    all_plaintext_urls = []
    for text in cleaned_up_text_fragments:
        all_plaintext_urls.extend(extract_plaintext_urls_from_text(text))
    # plaintext urls are their own title
    urls_and_titles = zip(all_plaintext_urls, all_plaintext_urls)
    plaintext_tagged_urls = classify_and_make_tagged_url(urls_and_titles, additional_tags=['plaintext url', 'in text'])

    return cleaned_up_text_fragments, in_text_tagged_urls + plaintext_tagged_urls




def extract_intro_from_articletext(article_text):
    """
    Finds the introduction paragraph, returns a string with the text
    """
    # intro text seems to always be in the first paragraph.
    intro_paragraph = article_text.p
    def extract_title_and_link(link):
        return link.contents[0], link.get('href')

    intro_text = ''.join([cleanup_text_fragment(f) for f in intro_paragraph.contents])

    return intro_text




def extract_author_name_from_maincontent(main_content):
    """
    Finds the <p> element with author info, if available.
    Returns a string if found, 'None' if not.
    """
    signature = main_content.find('p', {'id':'articleSign'})
    if signature:
        # the actual author name is often lost in a puddle of \n and \t
        # cleaning it up.
        return signature.contents[0].lstrip().rstrip()
    else:
        return None
    



def extract_category_from_maincontent(main_content):
    """
    Finds the breadcrumbs list. Returns a list of strings,
    one per item in the trail. The '\t\n' soup around each entry is cleaned up.
    """
    breadcrumbs = main_content.find('p', {'id':'breadcrumbs'})
    links = breadcrumbs.findAll('a', recursive=False)

    return [link.contents[0].rstrip().lstrip() for link in links]
    



def extract_associated_links_from_maincontent(main_content):
    """
    Finds the list of associated links. Returns a list of (title, url) tuples.
    """
    container = main_content.find('ul', {'class':'articleLinks'}, recursive=False)

    # sometimes there are no links
    if container:
        def extract_link_and_title(list_item):
            return  list_item.a.get('href'), list_item.a.contents[0]
        list_items = container.findAll('li', recursive=False)
        urls_and_titles = [extract_link_and_title(list_item) for list_item in list_items]
        print urls_and_titles
        return classify_and_make_tagged_url(urls_and_titles)
    else:
        return []

    

    
DATE_MATCHER = re.compile('\(\d\d/\d\d/\d\d\d\d\)')
def was_publish_date_updated(date_string):
    """
    In case of live events (soccer, the article gets updated.
    Hour of last update is appended to the publish date.
    """
    # we try to match a non-updated date, and check that it failed.<
    match = DATE_MATCHER.match(date_string)
    return not match



def make_time_from_string(time_string):
    """
    Takes a HH:MM string, returns a time object
    """
    h, m = [int(i) for i in time_string.split(':')]
    return time(h, m)


    
def extract_date_from_maincontent(main_content):
    """
    Finds the publication date string, returns a datetime object
    """
    date_string = main_content.find('p', {'id':'articleDate'}).contents[0]

    if was_publish_date_updated(date_string):
        # extract the update time, make the date look like '(dd/mm/yyyy)'
        date_string, time_string = date_string.split(',')
        date_string = '{0})'.format(date_string)

        # the time string looks like : 'mis à jour le hh:mm)'
        time_string = time_string.split(' ')[-1]
        pub_time = make_time_from_string(time_string.rstrip(')'))
    else:
        pub_time = None


    pub_date = datetime.strptime(date_string, '(%d/%m/%Y)').date()

    return pub_date, pub_time



def extract_article_data(source):
    """
    """
    if hasattr(source, 'read'):
        html_content = source.read()
    else:
        html_content = fetch_html_content(source)

    soup = make_soup_from_html_content(html_content)

    main_content = soup.find('div', {'id':'maincontent'})

    title = main_content.h1.contents[0]
    pub_date, pub_time = extract_date_from_maincontent(main_content)
    category = extract_category_from_maincontent(main_content)
    author_name = extract_author_name_from_maincontent(main_content)


    article_text = main_content.find('div', {'id':'articleText'})
    intro = extract_intro_from_articletext(article_text)
    text, in_text_urls = extract_text_content_and_links_from_articletext(article_text)
    associated_urls = extract_associated_links_from_maincontent(main_content)

    fetched_datetime = datetime.today()


    new_article = ArticleData(source, title, pub_date, pub_time, fetched_datetime,
                              in_text_urls+associated_urls,
                              category, author_name, intro, text)
    return new_article



def extract_title_and_link_from_item_box(item_box):
    title = item_box.h2.a.contents[0].rstrip().lstrip()
    url = item_box.h2.a.get('href')
    return title, url



def is_item_box_an_ad_placeholder(item_box):
    # awesome heuristic : if children are iframes, then go to hell 
    return len(item_box.findAll('iframe')) != 0



def extract_title_and_link_from_anounce_group(announce_group):
    # sometimes they use item box to show ads or some crap like that.
    odd_boxes = announce_group.findAll('div', {'class':'box4 odd'})
    even_boxes = announce_group.findAll('div', {'class':'box4 even'})

    all_boxes = chain(odd_boxes, even_boxes)

    return [extract_title_and_link_from_item_box(box)
            for box in all_boxes
            if not is_item_box_an_ad_placeholder(box)]



def get_first_story_title_and_url(main_content):
    """
    Extract the title and url of the main frontpage story
    """
    first_announce = main_content.find('div', {'id':'firstAnnounce'})
    first_title = first_announce.h2.a.get('title')
    first_url = first_announce.h2.a.get('href')

    return first_title, first_url



def get_frontpage_toc():
    url = 'http://www.dhnet.be'
    html_content = fetch_html_content(url)
    soup = make_soup_from_html_content(html_content)

    main_content = soup.find('div', {'id':'maincontent'})

    all_titles_and_urls = []

    # so, the list here is a combination of several subcontainer types.
    # processing every type separately
    first_title, first_url = get_first_story_title_and_url(main_content)
    all_titles_and_urls.append((first_title, first_url))

    # this will pick up the 'annouceGroup' containers with same type in the 'regions' div
    first_announce_groups = main_content.findAll('div',
                                                 {'class':'announceGroupFirst announceGroup'},
                                                 recursive=True)
    announce_groups = main_content.findAll('div',
                                           {'class':'announceGroup'},
                                           recursive=True)

    # all those containers have two sub stories
    for announce_group in chain(first_announce_groups, announce_groups):
        titles_and_urls = extract_title_and_link_from_anounce_group(announce_group)
        all_titles_and_urls.extend(titles_and_urls)

    return [(title, 'http://www.dhnet.be%s' % url) for (title, url) in  all_titles_and_urls]



def test_sample_data():
    #filename = '../../sample_data/dhnet_no_paragraphs.html'
    filename = '../../sample_data/dhnet_updated_date.html'
    with open(filename, 'r') as f:
        article_data = extract_article_data(f)
        article_data.print_summary()

        for l in article_data.internal_links:
            print l

        print '-' * 20



def show_frontpage_articles():
    frontpage_items = get_frontpage_toc()

    print '%d items on frontpage' % len(frontpage_items)
    for title, url in frontpage_items:
        print 'Fetching data for : %s (%s)' % (title, url)

        article_data = extract_article_data(url)
        article_data.print_summary()

        for (title, url, tags) in article_data.external_links:
            print u'{0} -> {1} {2}'.format(title, url, tags)

        for (title, url, tags) in article_data.internal_links:
            print u'{0} -> {1} {2}'.format(title, url, tags)

        print '-' * 20

        
if __name__ == '__main__':
    show_frontpage_articles()
    #test_sample_data()
