#!/usr/bin/env python

import copy, re
import urllib
from pprint import pprint
from BeautifulSoup import BeautifulSoup,  BeautifulStoneSoup 
from utils import fetch_html_content, fetch_rss_content


class ArticleData(object):
    def __init__(self, url, title, date, content, links, category):
        self.url = url
        self.title = title
        self.date = date
        self.content = content
        self.links = links
        self.category = category


    def __repr__(self):
        #fixme
        return """ArticleData(%s, date=%s, n_links=%d, wordcount=%d, category=%s """ % (self.title,
                                                                                        self.date,
                                                                                        sum(len(links) for links in self.links.values()),
                                                                                        len(self.content),
                                                                                        self.category)
    def to_json(self):
        pass



def sanitize_content():
    "removes image links, removes paragraphs, formatting"
    pass
    


def extract_content(story):
    header = story.find("div", {"id":"story_head"})
    body = story.find("div", {"id":"story_body"})
    

def extract_to_read_links_from_sidebar(sidebar):
    to_read_links_container = sidebar.find("div", {"id":"lire_aussi"})

    #sometimes, it does not exist at all
    if to_read_links_container:
        return [(link.get("href"), link.get("title"))
                for link in to_read_links_container.findAll("a")]
    else:
        return []


def extract_external_links_from_sidebar(sidebar):
    external_links_container = sidebar.find("div", {"id":"external"})

    #warning : weird javascript clickthru crap to process first
    if external_links_container:
        return [(link.get("onclick"), link.get("title"))
                for link in external_links_container.findAll("a")]
    else:
        return []



def extract_recent_links_from_soup(soup):
    #todo : check if those links are actually associated to the article
    recent_links_container = soup.find("div", {"id":"les_plus_recents"})

    if recent_links_container:
        return [(link.get("href"), link.contents[0])
                for link in recent_links_container.findAll("a") ]
    else:
        return []


def extract_links(soup):
    """
    Get the link lists for one news item, from the parsed html content.
    'Le Soir' has 3 kinds of links, but they're not all always there.
    """
    sidebar = soup.find("div", {'id':"st_top_center"})
    
    all_links = {"to_read":extract_to_read_links_from_sidebar(sidebar),
                 "external":extract_external_links_from_sidebar(sidebar),
                 "recent":extract_recent_links_from_soup(soup)}
    
    return all_links

    

def extract_title(story):
    header = story.find("div", {'id':"story_head"})
    title = header.h1.contents[0]
    return title

    

def extract_date(story):
    header = story.find("div", {'id':"story_head"})
    date = header.find("p", {'class':"info st_date"})
    # todo : this should probably be a real datetime object
    return date.contents[0]
    


def extract_category(story):
    breadcrumbs = story.find("div", {'id':'fil_ariane'})
    category_stages = [a.contents[0] for a in breadcrumbs.findAll("a") ]
    return category_stages






def make_soup_from_html_content(html_content):
    hexentityMassage = copy.copy(BeautifulSoup.MARKUP_MASSAGE)
    hexentityMassage = [(re.compile('&#x([^;]+);'), 
                         lambda m: '&#%d' % int(m.group(1), 16))]
    
    soup = BeautifulSoup(html_content,
                         convertEntities=BeautifulSoup.HTML_ENTITIES,
                         markupMassage=hexentityMassage)

    return soup



def extract_article_data_from_html_content(html_content):
    soup = make_soup_from_html_content(html_content)
    
    story = soup.find("div", {'id':'story'})
    content = extract_content(story)
    category = extract_category(story)
    date = extract_date(story)
    title = extract_title(story)
    
    links = extract_links(soup)

    return title, content, category, date, title, links



def get_two_columns_stories(element):
    """
    Returns the two <li> with two 'two columns' stories.
    This function assumes we already checked that the element actually has
    two sub stories
    """
    two_columns_stories_list = element.findAll("ul", {'class':"two_cols"}, recursive=False)[0]
    return two_columns_stories_list.findAll("li", recursive=False)


def element_has_two_columns_stories(element):
    """
    Checks whether or not a frontpage entry is a stand alone news item, or a container
    for two 'two columns' items.
    """
    return len(element.findAll("ul", {'class':"two_cols"}, recursive=False)) == 1


def get_frontpage_articles():
    """
    Fetch links to articles listed on the 'Le Soir' front page.
    For each of them, extract the relevant data.
    """
    url = "http://www.lesoir.be"
    html_content = fetch_html_content(url)

    soup = make_soup_from_html_content(html_content)

    # Here we have interlaced <ul>'s with a bunch of random other shit that
    # need some filtering
    stories_containers = soup.findAll("ul", {"class":"stories_list grid_6"})


    frontpage_links = []

    for container in stories_containers:
        all_stories = set(container.findAll("li", recursive=False))
        main_stories = set(container.findAll("li", {"class":"stories_main clearfix"}, recursive=False))

        other_stories = all_stories - main_stories

        
        # So, in _some_ lists of stories, the first one ('main story') has its title in an <h1>
        # and the rest in an <h2>
        # Also, some have two columns stories.
        # Beautiful soup indeed.
        for item in main_stories:
            frontpage_links.append((item.h1.a.get("title"), item.h1.a.get("href")))

        for item in other_stories:
            if element_has_two_columns_stories(item):
                first, second = get_two_columns_stories(item)
                # For some reason, those links don't have a 'title' attribute.
                # Love this.
                def extract_title_and_link(item):
                    return (item.h2.a.contents[0], item.h2.a.get("href"))
                frontpage_links.append(extract_title_and_link(first))
                frontpage_links.append(extract_title_and_link(second))

            else:
                frontpage_links.append((item.h2.a.get("title"), item.h2.a.get("href")))


    return frontpage_links

            

def get_rss_articles():
    rss_url = "http://www.lesoir.be/la_une/rss.xml"

    xml_content = fetch_rss_content(rss_url)
    stonesoup = BeautifulStoneSoup(xml_content)

    articles = []
    
    for item in stonesoup.findAll("item"):
        url = item.link.contents[0]
        html_content = fetch_html_content(url)
        # fixme : urls sometimes point to an external blog article, with a different DOM
        # todo : catch the redirect and look at the url, or something
        print url
        title, content, category, date, title, links = extract_article_data_from_html_content(html_content)

        new_article_data = ArticleData(url, title, date, content, links, category)
        articles.append(new_article_data)

    print articles


    
def parse_sample_data():
    import sys
    data_directory = "../../sample_data" 
    sys.path.append(data_directory)
    from dataset import dataset

    url = dataset['le soir']['URL']
    filename = dataset['le soir']['file']
    filepath = "%s/%s" % (data_directory, filename)
    
    with open(filepath) as f:
        html_content = f.read()
        extract_article_data_from_html_content(html_content)
    


def is_external_blog(url):
    return not url.startswith("/")
        
    
if __name__ == '__main__':

    frontpage_links = [(title, url)
                       for (title, url) in  get_frontpage_articles()
                       if not is_external_blog(url)]

    for (title, url) in frontpage_links:
        full_url = "http://www.lesoir.be%s" % url
        print "fetching data for article : %s" % title

        html_content = fetch_html_content(full_url)
        article_data = extract_article_data_from_html_content(html_content)

        pprint(article_data)
        print "-" * 80


        
