#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from itertools import chain
import urlparse

from scrapy.selector import HtmlXPathSelector
from csxj.common.tagging import tag_URL, classify_and_tag, make_tagged_url, TaggedURL
from csxj.db.article import ArticleData
from common.utils import fetch_html_content
from common.utils import setup_locales


setup_locales()


SOURCE_TITLE = u"7 sur 7"
SOURCE_NAME = u"septsursept"

SEPTSURSEPT_INTERNAL_BLOGS = {}

SEPTSURSEPT_NETLOC = "www.7sur7.be"





def make_full_url(item):
    title, url = item
    if not url.startswith("http"):
        return title, "http://{0}{1}".format(SEPTSURSEPT_NETLOC, url)
    else:
        return title, url



def extract_title_and_url(link_selector):
    url = link_selector.select("./@href").extract()[0]
    title = link_selector.select("./text()").extract()[0].strip()
    return title, url


def get_frontpage_toc():
    html_data = fetch_html_content('http://7sur7.be')
    hxs = HtmlXPathSelector(text=html_data)

    # get all the stories from the left column
    first_story = hxs.select("//section//article/h1/a")
    main_stories = hxs.select("//section//article/h3/a")

    #this news site is terrible. really.
    random_crap_stories = hxs.select("//section//section [starts-with(@class, 'tn_you')]//li/h3/a")
    more_crap_stories = hxs.select("//section//section [starts-with(@class, 'tn_hln')]//li/h3/a")

    all_left_stories = chain(first_story, main_stories, random_crap_stories, more_crap_stories)
    left_items = [extract_title_and_url(link_hxs) for link_hxs in all_left_stories]

    # get all the stories from the right column
    all_side_stories = hxs.select("//section [@class='str_aside_cntr']//h3/a")
    stories_to_remove = hxs.select("//section [@class='str_aside_cntr']//section [starts-with(@class, 'teas_article_306')]//li/h3/a")

    right_items = set([extract_title_and_url(link_hxs) for link_hxs in all_side_stories])
    to_remove = set([extract_title_and_url(link_hxs) for link_hxs in stories_to_remove])

    right_items = list(right_items - to_remove)



    frontpage_items = left_items + right_items
    return [make_full_url(item) for item in frontpage_items], []




def show_frontpage():
    frontpage_items, blogposts = get_frontpage_toc()

    print "NEWS ({0}):".format(len(frontpage_items))
    for title, url in frontpage_items:
        print u"{0} \t\t [{1}]".format(title, url)

    print "\n\nBLOGPOSTS ({0}):".format(len(blogposts))
    for title, url in blogposts:
        print u"{0} \t\t [{1}]".format(title, url)




if __name__ == '__main__':
    show_frontpage()
