#!/usr/bin/env python

import copy, re
import urllib
from BeautifulSoup import BeautifulSoup,  BeautifulStoneSoup 

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
    return [(link.get("href"), link.get("title")) for link in to_read_links_container.findAll("a")]



def extract_external_links_from_sidebar(sidebar):
    external_links_container = sidebar.find("div", {"id":"external"})

    #warning : weird javascript clickthru crap to process first
    return [(link.get("onclick"), link.get("title")) for link in external_links_container.findAll("a")]



def extract_recent_links_from_soup(soup):
    #todo : check if those links are actually associated to the article
    recent_links_container = soup.find("div", {"id":"les_plus_recents"})
    return [(link.get("href"), link.contents[0]) for link in recent_links_container.findAll("a") ]



def extract_links(soup):
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



def get_frontpage_articles():
    """
    This function is completly broken due to many edge cases in that stupid html.
    Use the rss version for now.
    """
    url = "http://www.lesoir.be"
    frontpage = urllib.urlopen(url)
    html_content = frontpage.read()

    soup = make_soup_from_html_content(html_content)

    # Here we have interlaced <ul>'s with a bunch of random other shit that
    # need some filtering
    stories_containers = soup.findAll("ul", {"class":"stories_list grid_6"})

    for container in stories_containers:
        main_stories = set(container.findAll("li", {"class":"stories_main clearfix"}, recursive=False))
        other_stories = set(container.findAll("li", recursive=False))

        other_stories = other_stories - main_stories
        
        # So, in _some_ lists of stories, the first one has its title in an <h1>
        # and the rest in an <h2>
        # Beautiful soup indeed.

        #TODO : see about the two columns thingy
        for item in main_stories:
            print item.h1.a.get("title")
        for item in other_stories:
            print item.h2.a.get("title")

            

def get_rss_articles():
    rss_url = "http://www.lesoir.be/la_une/rss.xml"

    rss_file = urllib.urlopen(rss_url)
    xml_content = rss_file.read()

    stonesoup = BeautifulStoneSoup(xml_content)

    
    


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
    


    
if __name__ == '__main__':
    #parse_sample_data()
    get_frontpage_articles()
