#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from itertools import chain
from scrapy.selector import HtmlXPathSelector
from csxj.common.tagging import tag_URL, classify_and_tag, make_tagged_url, TaggedURL
from csxj.db.article import ArticleData
from parser_tools.utils import fetch_html_content
from parser_tools.utils import setup_locales


setup_locales()

SOURCE_TITLE = u"RTBF Info"
SOURCE_NAME = u"rtbfinfo"

RTBFINFO_INTERNAL_BLOGS = {}
RTBFINFO_NETLOC = 'www.rtbf.be'

BLACKLIST = ["http://citysecrets.lavenir.net"]



def extract_title_and_url(link_selector):
    url = link_selector.select("./@href").extract()[0]
    title = link_selector.select("./text()").extract()[0]
    return title, url


# sigh
def extract_title_and_url_from_span_thing(link_selector):
    url = link_selector.select("./@href").extract()[0]
    title = link_selector.select("./span/text()").extract()[0]
    return title, url



def get_frontpage_toc():
    url = "http://{0}/info".format(RTBFINFO_NETLOC)
    html_data = fetch_html_content(url)

    hxs = HtmlXPathSelector(text=html_data)

    main_story = hxs.select("//div [@id='mainContent']//article//h2//a")
    featured_stories = hxs.select("//div [@id='mainContent']//section/article//h3//a")
    anchored_stories = hxs.select("//div [@id='mainContent']//div [starts-with(@class, 'anchor')]//ul//a")

    chronic_title_hxs = hxs.select("//div [@id='mainContent']//div [@class='second chronic']/div [@class='illuBox']//p")
    chronic_links = [chronic_hxs for chronic_hxs in chronic_title_hxs.select("../@href").extract()]
    chronic_titles = [c.strip() for c in chronic_title_hxs.select(".//text()").extract()]

    chronic_stories = zip(chronic_titles, chronic_links)


    titles_and_urls = [extract_title_and_url(link_hxs) for link_hxs in chain(main_story, featured_stories, anchored_stories)] + chronic_stories

    return titles_and_urls, [], []




def show_frontpage():
    frontpage_items, blogposts = get_frontpage_toc()

    print "NEWS ({0}):".format(len(frontpage_items))
    for title, url in frontpage_items:
        print u"{0} \t\t ({1})".format(title, url)

    print "\n\nBLOGPOSTS ({0}):".format(len(blogposts))
    for title, url in blogposts:
        print u"{0} \t\t ({1})".format(title, url)






def main():
    show_frontpage()



if __name__ == "__main__":
    main()








