#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
from datetime import datetime
from BeautifulSoup import  BeautifulStoneSoup,  Tag
import urlparse
import codecs
from csxj.common.tagging import tag_URL, classify_and_tag, make_tagged_url, TaggedURL
from csxj.db.article import ArticleData
from parser_tools.utils import fetch_html_content, fetch_rss_content, make_soup_from_html_content
from parser_tools.utils import remove_text_formatting_markup_from_fragments, extract_plaintext_urls_from_text
from parser_tools.utils import setup_locales
from parser_tools import constants
from csxj.common import tagging


setup_locales()

SOURCE_TITLE = u"Le Soir"
SOURCE_NAME = u"lesoir"

LESOIR_INTERNAL_BLOGS = {

    'archives.lesoir.be':['archives', 'internal'],
   
    'belandroid.lesoir.be':['internal', 'jblog'],
    'geeko.lesoir.be':['internal', 'jblog'],
    'blog.lesoir.be':['internal', 'jblog'],

    'pdf.lesoir.be' : ['internal', 'pdf newspaper']
}

LESOIR_NETLOC = 'www.lesoir.be'


def is_on_same_domain(url):
    """
    Until we get all the internal blogs/sites, we can still detect
    if a page is hosted on the same domain.
    """
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    if netloc not in LESOIR_INTERNAL_BLOGS:
        return netloc.endswith('lesoir.be')
    return False



def sanitize_paragraph(paragraph):
    """
    Removes image links, removes paragraphs, formatting
    """
    return  remove_text_formatting_markup_from_fragments(paragraph)
    #return ''.join([remove_text_formatting_markup(fragment) for fragment in paragraph.contents])



def classify_and_make_tagged_url(urls_and_titles, additional_tags=set()):
    """
    Classify (with tags) every element in a list of (url, title) tuples
    Returns a list of TaggedURLs
    """
    tagged_urls = []
    for url, title in urls_and_titles:
        tags = classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_BLOGS)
        if is_on_same_domain(url):
            tags.update(['internal site'])
        tagged_urls.append(make_tagged_url(url, title, tags|additional_tags))
    return tagged_urls

def extract_title_and_url_from_bslink(link):
    base_tags = []
    if link.get('href'):
        url = link.get('href')

    else :
        url = "__GHOST_LINK__"
        base_tags.append("ghost link")

    if link.contents:
        title = link.contents[0].strip()
    else:
        title = "__GHOST_LINK__"
        base_tags.append("ghost link")

    return title, url, base_tags

def extract_text_content(story):
    """
    Finds the story's body, cleans up the text to remove all html formatting.
    Returns a list of strings, one per found paragraph, and all the plaintext urls, as TaggedURLs
    """
    story = story.find('div', {'id':'story_body'})
    paragraphs = story.findAll('p', recursive=False)

    tagged_urls = list()

    # extract regular, in text links
    inline_links = list()
    plaintext_urls = list()

    for paragraph in paragraphs:
        links = paragraph.findAll('a', recursive=True)
        inline_links.extend(links)

    titles_and_urls = [extract_title_and_url_from_bslink(i) for i in inline_links]
    for title, url, base_tags in titles_and_urls:
        tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_BLOGS)
        tags.add('in text')
        tagged_urls.append(tagging.make_tagged_url(url, title, tags))


    # extract story text
    clean_paragraphs = [sanitize_paragraph(p) for p in paragraphs]

    # extract plaintext links
    plaintext_urls = []
    for text in clean_paragraphs:
        plaintext_urls.extend(extract_plaintext_urls_from_text(text))

    for url in plaintext_urls:
        tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_BLOGS)
        tags.add('in text')
        tags.add('plaintext')
        tagged_urls.append(tagging.make_tagged_url(url, url, tags))


    return clean_paragraphs, tagged_urls



def extract_to_read_links_from_sidebar(sidebar):
    to_read_links_container = sidebar.find('div', {'id':'lire_aussi'})
    #sometimes, it does not exist at all
    if to_read_links_container:
        urls_and_titles = [(link.get('href'), link.get('title'))
                            for link in to_read_links_container.findAll('a')]
        return classify_and_make_tagged_url(urls_and_titles, additional_tags=set(['sidebar box', 'to read']))
    else:
        return []



def extract_external_links_from_sidebar(sidebar):
    external_links_container = sidebar.find('div', {'id':'external'})

    if external_links_container:
        urls_and_titles = [(link.get('href'), link.get('title'))
                            for link in external_links_container.findAll('a')]
        return classify_and_make_tagged_url(urls_and_titles, additional_tags=set(['sidebar box', 'web']))
    else:
        return []




def extract_recent_links_from_soup(soup):
    def extract_url_and_title(item):
        url = item.get('href')
        if item.contents[0]:
            title = item.contents[0]
        else:
            # yes, this happens
            title = 'No Title found'
        return url, title

    #todo : check if those links are actually associated to the article
    recent_links_container = soup.find('div', {'id':'les_plus_recents'})
    if recent_links_container:
        urls_and_titles = [extract_url_and_title(item)
                           for item in recent_links_container.findAll('a')]
        return classify_and_make_tagged_url(urls_and_titles, additional_tags=set(['recent', 'sidebar box']))
    else:
        return []



def extract_links(soup):
    """
    Get the link lists for one news item, from the parsed html content.
    'Le Soir' has 3 kinds of links, but they're not all always there.
    """
    sidebar = soup.find('div', {'id':'st_top_center'})

    all_tagged_urls = extract_external_links_from_sidebar(sidebar)
    all_tagged_urls.extend(extract_to_read_links_from_sidebar(sidebar))
    all_tagged_urls.extend(extract_recent_links_from_soup(soup))

    return all_tagged_urls



def extract_title(story):
    header = story.find('div', {'id':'story_head'})
    title = header.h1.contents[0]
    if title:
        return unicode(title)
    else:
        return 'No title found'


def extract_author_name(story):
    header = story.find('div', {'id':'story_head'})
    author_name = header.find('p', {'class':'info st_signature'})

    if author_name and author_name.contents:
        return author_name.contents[0]
    else:
        return constants.NO_AUTHOR_NAME



def extract_date(story):
    header = story.find('div', {'id':'story_head'})
    publication_date = header.find('p', {'class':'info st_date'})

    if publication_date:
        date_string = publication_date.contents[0]

        date_bytestring = codecs.encode(date_string, 'utf-8')
        datetime_published = datetime.strptime(date_bytestring, u'%A %d %B %Y, %H:%M')

        return datetime_published.date(), datetime_published.time()
    else:
        return None, None



def extract_intro(story):
    header = story.find('div', {'id':'story_head'})
    intro = header.find('h4', {'class':'chapeau'})
    # so yeah, sometimes the intro paragraph contains some <span> tags with things
    # we don't really care about. Filtering that out.
    text_fragments = [fragment for fragment in intro.contents if not isinstance(fragment, Tag)]

    return ''.join(text_fragments)

def extract_category(story):
    breadcrumbs = story.find('div', {'id':'fil_ariane'})
    category_stages = [a.contents[0] for a in breadcrumbs.findAll('a') ]
    return category_stages

def extract_links_from_embedded_content(story):
    tagged_urls = []

    # generic iframes
    iframe_items = story.findAll("iframe", recursive=True)
    for iframe in iframe_items:
        url = iframe.get('src')
        all_tags = classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_BLOGS)
        tagged_urls.append(make_tagged_url(url, url, all_tags | set(['embedded'])))

    # extract embedded storify
    scripts = story.findAll('script', recursive=True)
    for script in scripts :
        url = script.get('src')
        if url :
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
            if netloc == "storify.com":
                url = url.rstrip(".js")
                all_tags = classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_BLOGS)
                tagged_urls.append(make_tagged_url(url, url, all_tags | set(['embedded'])))

    # TO DO NEXT : reconstruc kplayer URL
    kplayer = story.find('div', {'class':'containerKplayer'})
    if kplayer:
        kplayer_flash = kplayer.find('div', {'class': 'flash_kplayer'})
        url_part1 = kplayer_flash.object['data']
        url_part2 = kplayer_flash.object.find('param', {'name' : 'flashVars'})['value']
        if url_part1 is not None and url_part2 is not None:
            url = "%s?%s" % (url_part1, url_part2)
            all_tags = classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_BLOGS)
            tagged_urls.append(make_tagged_url(url, url, all_tags | set(['embedded'])))
        else:
            raise ValueError("We couldn't find an URL in the flash player. Update the parser.")

    for x in tagged_urls:
        print x
    return tagged_urls




def extract_article_data(source):
    """
    source is either a file-like object, or a url.
    """
    if hasattr(source, 'read'):
        html_content = source.read()
    else:
        html_content = fetch_html_content(source)

    soup = make_soup_from_html_content(html_content)
    story = soup.find('div', {'id':'story'})

    category = extract_category(story)
    title = extract_title(story)
    pub_date, pub_time = extract_date(story)
    author = extract_author_name(story)

    sidebar_links = extract_links(soup)

    intro = extract_intro(story)
    content, intext_links = extract_text_content(story)

    fetched_datetime = datetime.today()

    embedded_content_links = extract_links_from_embedded_content(story)

    all_links = sidebar_links + intext_links + embedded_content_links


    return ArticleData(source, title, pub_date, pub_time, fetched_datetime,
                              all_links,
                              category, author,
                              intro, content), html_content



def extract_main_content_links(source):
    if hasattr(source, 'read'):
        html_content = source.read()
    else:
        html_content = fetch_html_content(source)

    soup = make_soup_from_html_content(html_content)

    # get maincontent div
    story = soup.find('div', {'id':'story'})

    all_links = soup.findAll('a', recursive=True)

    def extract_url_and_title(item):
        url = item.get('href')
        if item.contents[0]:
            title = item.contents[0]
        else:
            # yes, this happens
            title = 'No Title found'
        return url, title

    return [extract_url_and_title(l) for l in all_links]



def get_two_columns_stories(element):
    """
    Returns the two <li> with two 'two columns' stories.
    This function assumes we already checked that the element actually has
    two sub stories
    """
    two_columns_stories_list = element.findAll('ul', {'class':'two_cols'}, recursive=False)[0]
    return two_columns_stories_list.findAll('li', recursive=False)



def element_has_two_columns_stories(element):
    """
    Checks whether or not a frontpage entry is a stand alone news item, or a container
    for two 'two columns' items.
    """
    return len(element.findAll('ul', {'class':'two_cols'}, recursive=False)) == 1



def get_frontpage_toc():
    """
    Fetch links to articles listed on the 'Le Soir' front page.
    For each of them, extract the relevant data.
    """
    url = 'http://www.lesoir.be'
    html_content = fetch_html_content(url)

    soup = make_soup_from_html_content(html_content)

    # Here we have interlaced <ul>'s with a bunch of random other shit that
    # need some filtering
    stories_containers = soup.findAll('ul', {'class':'stories_list grid_6'})


    articles_toc, blogpost_toc = [], []

    for container in stories_containers:
        all_stories = set(container.findAll('li', recursive=False))
        main_stories = set(container.findAll('li', {'class':'stories_main clearfix'}, recursive=False))

        other_stories = all_stories - main_stories

        # So, in _some_ lists of stories, the first one ('main story') has its title in an <h1>
        # and the rest in an <h2>
        # Also, some have two columns stories.
        # Beautiful soup indeed.
        for item in main_stories:
            title, url = (item.h1.a.get('title'), item.h1.a.get('href'))
            if is_external_blog(url):
                blogpost_toc.append((title, url))
            else:
                articles_toc.append((title, url))

        for item in other_stories:
            if element_has_two_columns_stories(item):
                # For some reason, those links don't have a 'title' attribute.
                # Love this.
                def extract_title_and_link(item):
                    return item.h2.a.contents[0], item.h2.a.get('href')

                for story in get_two_columns_stories(item):
                    title, url = extract_title_and_link(story)
                    if is_external_blog(url):
                        blogpost_toc.append((title, url))
                    else:
                        articles_toc.append((title, url))
            else:
                title, url = (item.h2.a.get('title'), item.h2.a.get('href'))
                if is_external_blog(url):
                    blogpost_toc.append((title, url))
                else:
                    articles_toc.append((title, url))

    return [(title, 'http://www.lesoir.be{0}'.format(url)) for (title, url) in articles_toc], blogpost_toc




def get_rss_toc():
    rss_url = 'http://www.lesoir.be/la_une/rss.xml'
    xml_content = fetch_rss_content(rss_url)
    stonesoup = BeautifulStoneSoup(xml_content)

    titles_in_rss = [(item.title.contents[0], item.link.contents[0]) for item in stonesoup.findAll('item')]

    return titles_in_rss



def parse_sample_data():
    import sys
    data_directory = '../../sample_data'
    sys.path.append(data_directory)
    from dataset import dataset

    for entry in dataset['le soir']:
        url = entry['URL']
        filename = entry['file']
        filepath = '%s/%s' % (data_directory, filename)

        with open(filepath) as f:
            extract_article_data(f)



def is_external_blog(url):
    return not url.startswith('/')



def get_frontpage_articles_data():
    import traceback

    articles_toc, blogposts_toc = get_frontpage_toc()

    articles = []
    errors = []

    for (title, url) in articles_toc:
        article_data, html_content = extract_article_data(url)
        articles.append(article_data)

    return articles, blogposts_toc, errors



def dowload_one_article():
    url = "http://www.lesoir.be/sports/sports_mecaniques/2012-01-07/pas-de-grand-prix-de-spa-francorchamps-en-2013-888811.php"
    url = "http://www.lesoir.be/actualite/belgique/elections_2010/2012-01-10/budget-2012-chastel-appele-a-s-expliquer-cet-apres-midi-889234.php"
    url = "http://www.lesoir.be/actualite/france/2012-01-10/free-defie-les-telecoms-francais-avec-un-forfait-illimite-a-19-99-euros-889276.php"
    url = "http://www.lesoir.be/actualite/belgique/2012-08-21/guy-spitaels-est-decede-933203.php"
    url = "../../sample_data/lesoir/lesoir_storify2.html"
    art, raw_html = extract_article_data(url)

    maincontent_links = set(extract_main_content_links(url))
    processed_links = set([(l.URL, l.title) for l in art.links])


    missing_links = maincontent_links - processed_links

    print "total links: ", len(maincontent_links)
    print "processed links: ", len(processed_links)
    print "missing: ", len(missing_links)

def test_sample_data():
    filepath = '../../sample_data/lesoir/lesoir_storify2.html'

    with open(filepath) as f:
        article_data, raw = extract_article_data(f)
        # article_data.print_summary()

        # for link in article_data.links:
        #     print link.title
        #     print link.URL
        #     print link.tags

        # print article_data.intro
        # print article_data.content

if __name__ == '__main__':
    test_sample_data()