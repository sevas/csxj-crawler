#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
from datetime import datetime, time
from itertools import chain
import re
import urlparse
from BeautifulSoup import Tag
from common.utils import fetch_html_content, make_soup_from_html_content, remove_text_formatting_markup_from_fragments, extract_plaintext_urls_from_text
from csxj.common.tagging import classify_and_tag, make_tagged_url
from csxj.db.article import ArticleData
from common import constants
from common import twitter_utils

# for datetime conversions
if sys.platform in ['linux2', 'cygwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF8')
elif sys.platform in [ 'darwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR')


DHNET_INTERNAL_SITES = {
    'tackleonweb.blogs.dhnet.be':['internal blog', 'internal', 'sports'],
    'galeries.dhnet.be':['internal site', 'internal', 'image gallery'],
}

DHNET_NETLOC = 'www.dhnet.be'

SOURCE_TITLE = u"DHNet"
SOURCE_NAME = u"dhnet"

def is_on_same_domain(url):
    """
    Until we get all the internal blogs/sites, we can still detect
    if a page is hosted on the same domain.
    """
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    if netloc not in DHNET_INTERNAL_SITES:
        return netloc.endswith('dhnet.be')
    return False



def classify_and_make_tagged_url(urls_and_titles, additional_tags=set()):
    """
    Classify (with tags) every element in a list of (url, title) tuples
    Returns a list of TaggedURLs
    """
    tagged_urls = []
    for url, title in urls_and_titles:
        tags = classify_and_tag(url, DHNET_NETLOC, DHNET_INTERNAL_SITES)
        if is_on_same_domain(url):
            tags = tags.union(['internal site', 'internal'])
        all_tags = tags.union(additional_tags)
        tagged_urls.append(make_tagged_url(url, title, all_tags))
    return tagged_urls



def cleanup_text_fragment(text_fragment):
    """
    Recursively cleans up a text fragment (e.g. nested tags).
    Returns a plain text string with no formatting info whatsoever.
    """
    if isinstance(text_fragment, Tag):
        return remove_text_formatting_markup_from_fragments(text_fragment.contents)
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
        return link.get('href'),  remove_text_formatting_markup_from_fragments(link.contents)

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



def extract_text_content_and_links_from_articletext(article_text, has_intro=True):
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
    if has_intro:
        children = children[1:]

    # the rest might be a list of paragraphs, but might also just be the text, sometimes with
    # formatting.

    cleaned_up_text_fragments = list()
    for text_block in children:
        cleaned_up_text_fragments.append(remove_text_formatting_markup_from_fragments(text_block, '\n\t '))

    all_plaintext_urls = []
    for text in cleaned_up_text_fragments:
        all_plaintext_urls.extend(extract_plaintext_urls_from_text(text))
    # plaintext urls are their own title
    urls_and_titles = zip(all_plaintext_urls, all_plaintext_urls)
    plaintext_tagged_urls = classify_and_make_tagged_url(urls_and_titles, additional_tags=set(['plaintext url', 'in text']))

    return cleaned_up_text_fragments, in_text_tagged_urls + plaintext_tagged_urls



def article_has_intro(article_text):
    return article_text.p


def extract_intro_from_articletext(article_text):
    """
    Finds the introduction paragraph, returns a string with the text
    """
    # intro text seems to always be in the first paragraph.
    if article_has_intro(article_text):
        intro_paragraph = article_text.p
        return remove_text_formatting_markup_from_fragments(intro_paragraph.contents)
    # but sometimes there is no intro. What the hell.
    else:
        return u''





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
        return constants.NO_AUTHOR_NAME




def extract_category_from_maincontent(main_content):
    """
    Finds the breadcrumbs list. Returns a list of strings,
    one per item in the trail. The '\t\n' soup around each entry is cleaned up.
    """
    breadcrumbs = main_content.find('p', {'id':'breadcrumbs'})
    links = breadcrumbs.findAll('a', recursive=False)

    return [link.contents[0].rstrip().lstrip() for link in links]



icon_type_to_tags = {
    'pictoType0':['internal', 'full url'],
    'pictoType1':['internal', 'local url'],
    'pictoType2':['images', 'gallery'],
    'pictoType3':['video'],
    'pictoType4':['animation'],
    'pictoType5':['audio'],
    'pictoType6':['images', 'gallery'],
    'pictoType9':['internal blog'],
    'pictoType12':['external']
}


def make_tagged_url_from_pictotype(url, title, icon_type):
    """
    Attempts to tag a url using the icon used. Mapping is incomplete at the moment.
    Still keeps the icon type as part of the tags for future uses.
    """
    tags = set([icon_type])
    if icon_type in icon_type_to_tags:
        tags = tags.union(set(icon_type_to_tags[icon_type]))

    return make_tagged_url(url, title, tags)



def extract_associated_links_from_maincontent(main_content):
    """
    Finds the list of associated links. Returns a list of (title, url) tuples.
    """
    container = main_content.find('ul', {'class':'articleLinks'}, recursive=False)

    # sometimes there are no links
    if container:
        def extract_link_and_title(list_item):
            return  list_item.a.get('href'), remove_text_formatting_markup_from_fragments(list_item.a.contents)
        tagged_urls = list()
        for list_item in container.findAll('li', recursive=False):
            url, title = extract_link_and_title(list_item)
            pictotype = list_item.get('class')
            tagged_url = make_tagged_url_from_pictotype(url, title, pictotype)
            tags = classify_and_tag(url, DHNET_NETLOC, DHNET_INTERNAL_SITES)

            tagged_url.tags.update(set(tags))
            tagged_urls.append(tagged_url)
        return tagged_urls
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



def extract_links_from_embedded_content(embedded_content):
    if embedded_content.iframe:
        url = embedded_content.iframe.get('src')
        title = u"Embedded content"
        all_tags = classify_and_tag(url, DHNET_NETLOC, DHNET_INTERNAL_SITES)
        return [make_tagged_url(url, title, all_tags | set(['embedded']))]
    else:
        divs = embedded_content.findAll('div', recursive=False)
        kplayer = embedded_content.find('div', {'class':'containerKplayer'})
        if kplayer:
            kplayer_infos = kplayer.find('video')
            url = kplayer_infos.get('data-src')
            title = remove_text_formatting_markup_from_fragments(divs[1].contents)
            all_tags = classify_and_tag(url, DHNET_NETLOC, DHNET_INTERNAL_SITES)
            return [make_tagged_url(url, title, all_tags | set(['video', 'embedded', 'kplayer']))]
        else:
            return []



def extract_links_to_embedded_content(main_content):
    """

    Args:
        main_content

    Returns:

    """
    embedded_content_divs = main_content.findAll('div', {'class':'embedContents'})
    tagged_urls = []
    for div in embedded_content_divs:
        if div.iframe:
            url = div.iframe.get('src')
            title = u"__EMBEDDED_CONTENT__"
            all_tags = classify_and_tag(url, DHNET_NETLOC, DHNET_INTERNAL_SITES)
            tagged_urls.append(make_tagged_url(url, title, all_tags | set(['embedded'])))
        else:
            if div.find('div', {'class':'containerKplayer'}):
                if len(div.findAll('div', recursive=False)) == 2:
                    title_div = div.findAll('div', recursive=False)[1]
                    title = remove_text_formatting_markup_from_fragments(title_div.contents)
                else:
                    title = u"__NO_TITLE__"

                kplayer = div.find('div', {'class':'containerKplayer'})

                #methode 1
                kplayer_flash = kplayer.find('div', {'class': 'flash_kplayer'})
                url_part1 = kplayer_flash.object['data']
                url_part2 = kplayer_flash.object.find('param', {'name' : 'flashVars'})['value']
                if url_part1 is not None and url_part2 is not None:
                    url = "%s?%s" % (url_part1, url_part2)
                    all_tags = classify_and_tag(url, DHNET_NETLOC, DHNET_INTERNAL_SITES)
                    tagged_urls.append(make_tagged_url(url, title, all_tags | set(['video', 'embedded', 'kplayer'])))
                else:
                    raise ValueError("We couldn't find an URL in the flahs player, please check")

            elif div.find('script'):
                # try to detect a twitter widget
                if div.find('script').get('src'):
                    script_url = div.find('script').get('src')
                    if twitter_utils.is_twitter_widget_url(script_url):
                        title, url, tags = twitter_utils.get_widget_type(div.findAll('script')[1].contents[0])
                        tags |= classify_and_tag(url, DHNET_NETLOC, DHNET_INTERNAL_SITES)
                        tags |= set(['script', 'embedded'])
                        tagged_urls.append(make_tagged_url(url, title, tags))
                    else:
                        pass
                elif div.find('noscript'):
                    noscript = div.find('noscript')
                    link = noscript.find('a')
                    if link:
                        url = link.get('href')
                        title = remove_text_formatting_markup_from_fragments(link.contents)
                        all_tags = classify_and_tag(url, DHNET_NETLOC, DHNET_INTERNAL_SITES)
                        all_tags |= set(['script', 'embedded'])
                        tagged_urls.append(make_tagged_url(url, title, all_tags))
                    else:
                        print ValueError("No link was found in the <noscript> section")
                else:
                    print ValueError("Could not extract fallback noscript url for this embedded javascript object")
            else:
                print ValueError("Unknown media type with class: {0}".format(div.get('class')))


    print tagged_urls
    return tagged_urls


def extract_article_data(source):
    """
    """
    if hasattr(source, 'read'):
        html_content = source.read()
    else:
        html_content = fetch_html_content(source)

    soup = make_soup_from_html_content(html_content)

    main_content = soup.find('div', {'id':'maincontent'})

    if main_content and main_content.h1:
        title = remove_text_formatting_markup_from_fragments(main_content.h1.contents)
        pub_date, pub_time = extract_date_from_maincontent(main_content)
        category = extract_category_from_maincontent(main_content)
        author_name = extract_author_name_from_maincontent(main_content)


        article_text = main_content.find('div', {'id':'articleText'})
        if article_has_intro(article_text):
            intro = extract_intro_from_articletext(article_text)
            text, in_text_urls = extract_text_content_and_links_from_articletext(article_text)
        else:
            intro = u""
            text, in_text_urls = extract_text_content_and_links_from_articletext(article_text, False)
        associated_urls = extract_associated_links_from_maincontent(main_content)

        embedded_content_urls = extract_links_to_embedded_content(main_content)


        fetched_datetime = datetime.today()


        new_article = ArticleData(source, title, pub_date, pub_time, fetched_datetime,
                                  in_text_urls+associated_urls+embedded_content_urls,
                                  category, author_name, intro, text)
        return new_article, html_content
    else:
        return None, html_content



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
    if main_content:
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

        return [(title, 'http://www.dhnet.be%s' % url) for (title, url) in  all_titles_and_urls], []
    else:
        return [], []


if __name__ == "__main__":
    # import json

    # urls = [
    #     "http://www.dhnet.be/infos/faits-divers/article/381082/le-fondateur-des-protheses-pip-admet-la-tromperie-devant-la-police.html",
    #     "http://www.dhnet.be/sports/formule-1/article/377150/ecclestone-bientot-l-europe-n-aura-plus-que-cinq-grands-prix.html",
    #     "http://www.dhnet.be/infos/belgique/article/378150/la-n-va-menera-l-opposition-a-un-gouvernement-francophone-et-taxateur.html",
    #     "http://www.dhnet.be/cine-tele/divers/article/378363/sois-belge-et-poile-toi.html",
    #     "http://www.dhnet.be/infos/societe/article/379508/contribuez-au-journal-des-bonnes-nouvelles.html",
    #     "http://www.dhnet.be/infos/belgique/article/386721/budget-l-effort-de-2-milliards-confirme.html",
    #     "http://www.dhnet.be/infos/monde/article/413062/sandy-paralyse-le-nord-est-des-etats-unis.html",
    #     "http://www.dhnet.be/infos/economie/article/387149/belfius-fait-deja-le-buzz.html",
    #     "http://www.dhnet.be/infos/faits-divers/article/388710/tragedie-de-sierre-toutes-nos-videos-reactions-temoignages-condoleances.html"

    # ]

    # for url in urls[-2:-1]:
    #     article, html = extract_article_data(url)

    #     if article:
    #         article.print_summary()
    #         print article.title
    #         for tagged_url in article.links:
    #             print(u"{0:100} ({1:100}) \t {2}".format(tagged_url.title, tagged_url.URL, tagged_url.tags))

    #     print("\n"*4)
    url = "/Volumes/Curst/json_db_0_5/dhnet/2011-12-19/15.05.05/raw_data/1.html"
    f = open(url,"r")

    extract_article_data(f)


