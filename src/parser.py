#!/usr/bin/env python

import copy, re
from BeautifulSoup import BeautifulSoup 

class ArticleData(object):
    def __init__(self, url, title, date, content, links, category):
        self.url = url
        self.title = title
        self.date = date
        self.content = content
        self.links = links
        self.category = category


    def to_json(self):
        pass




def extract_category(story):
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





def extract_article_data_from_html_content(html_content):
    soup = BeautifulSoup(html_content,
                         convertEntities=BeautifulSoup.HTML_ENTITIES,
                         markupMassage=hexentityMassage)
    
    story = soup.find("div", {'id':'story'})
    print extract_content(story)
    print extract_category(story)
    print extract_date(story)
    print extract_title(story)
    
    print extract_links(soup)




if __name__ == '__main__':
    import sys
    data_directory = "../sample_data" 
    sys.path.append(data_directory)
    from dataset import dataset

    url = dataset['le soir']['URL']
    filename = dataset['le soir']['file']
    filepath = "%s/%s" % (data_directory, filename)


    hexentityMassage = copy.copy(BeautifulSoup.MARKUP_MASSAGE)
    hexentityMassage = [(re.compile('&#x([^;]+);'), 
                         lambda m: '&#%d' % int(m.group(1), 16))]
    
    with open(filepath) as f:
        html_content = f.read()
        extract_article_data_from_html_content(html_content)
