#!/usr/bin/env python

import urllib
import locale
from datetime import datetime
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, UnicodeDammit, Tag
from utils import fetch_html_content, fetch_rss_content

# for datetime conversions
locale.setlocale(locale.LC_TIME, "fr_be")






def make_soup_from_html_content(html_content):    
    soup = BeautifulSoup(html_content, convertEntities=BeautifulSoup.HTML_ENTITIES)
    return soup



def get_frontpage_articles():
    url = "http://www.lalibre.be"
    html_content = fetch_html_content(url)

    soup = make_soup_from_html_content(html_content)

    article_list_container = soup.find("div", {'id':"mainContent"})

    announces = article_list_container.findAll("div", {'class':"announce"}, recursive=False)


    def extract_title_and_link(announce):
        return  announce.h1.a.contents[0], announce.h1.a.get("href")
    
    return [extract_title_and_link(announce) for announce in announces]



if __name__ == '__main__':
    frontpage_items = get_frontpage_articles()
    print len(frontpage_items)
    print "\n".join([title for (title, link) in frontpage_items])
