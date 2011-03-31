#!/usr/bin/env python

import urllib
from datetime import datetime
from itertools import chain
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, UnicodeDammit, Tag
from utils import fetch_html_content, count_words, make_soup_from_html_content


class ArticleData(object):
    def __init__(self, url, title, date, content, links, category, author, intro):
        self.url = url
        self.title = title
        self.date = date
        self.content = content
        self.links = links
        self.category = category
        self.author = author
        self.intro = intro



    def to_json(self):
        pass






    
def extract_title_and_link_from_item_box(item_box):
    title = item_box.h2.a.contents[0].rstrip().lstrip()
    url = item_box.h2.a.get("href")
    return title, url



def is_item_box_an_ad_placeholder(item_box):
    # awesome heuristic : if children are iframes, then go to hell 
    return len(item_box.findAll("iframe")) != 0



def extract_title_and_link_from_anounce_group(announce_group):
    # sometimes they use item box to show ads or some crap like that.
    odd_boxes = announce_group.findAll("div", {"class":"box4 odd"})
    even_boxes = announce_group.findAll("div", {"class":"box4 even"})

    all_boxes = chain(odd_boxes, even_boxes)

    return [extract_title_and_link_from_item_box(box)
            for box in all_boxes
            if not is_item_box_an_ad_placeholder(box)]



def get_frontpage_articles():
    url = "http://www.dhnet.be"
    html_content = fetch_html_content(url)
    soup = make_soup_from_html_content(html_content)

    main_content = soup.find("div", {'id':"maincontent"})

    # so, the list here is a combination of several subcontainer types.
    # processing every type separetely
    first_announce = main_content.find("div", {'id':"firstAnnounce"})

    # this will pick up the containers with same type in the 'regions' div
    first_announce_groups = main_content.findAll("div",
                                                 {'class':"announceGroupFirst announceGroup"},
                                                 recursive=True)
    
    announce_groups = main_content.findAll("div",
                                           {'class':"announceGroup"},
                                           recursive=True)

    first_title = first_announce.h2.a.get("title")
    first_url = first_announce.h2.a.get("href")

    
    all_titles_and_urls = [(first_title, first_url)]

    for announce_group in chain(first_announce_groups, announce_groups):
        titles_and_urls = extract_title_and_link_from_anounce_group(announce_group)
        all_titles_and_urls.extend(titles_and_urls)

    return [(title, "http://www.dhnet.be%s" % url) for (title, url) in  all_titles_and_urls]


        
if __name__ == '__main__':
    frontpage_links = get_frontpage_articles()

    for title, url in frontpage_links:
        print "%s (%s)" % (title, url)
