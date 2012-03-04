#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from itertools import chain
from scrapy.selector import HtmlXPathSelector
from csxj.common.tagging import tag_URL, classify_and_tag, make_tagged_url, TaggedURL
from csxj.db.article import ArticleData
from common.utils import fetch_html_content
from common.utils import setup_locales


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

    featured_link = hxs.select("//div [@id='mainContent']//div [starts-with(@class, 'doubleContent sticky')]//div [@id='featured']/h2/a")
    sticky_right_links =  hxs.select("//div [@id='mainContent']//div [starts-with(@class, 'doubleContent sticky')]/div [@class='second']//h3//a")
    #itembox_links = hxs.select("//div [@id='mainContent']//div [starts-with(@class, 'doubleContent sticky')]//div[@class='viewer']//div [@class='illuBox']/h4/a")

    doublecontent_list_links = hxs.select("//div [@id='mainContent']//div [starts-with(@class, 'doubleContent')]//ul//a")

    titles_and_urls = [extract_title_and_url(link_hxs) for link_hxs in chain(   featured_link,
                                                                                sticky_right_links,
                                                                                #itembox_links,
                                                                                doublecontent_list_links)]
    # Obviously, you could not let me have it.
    doublecontent_main_links = hxs.select("//div [@id='mainContent']//div [starts-with(@class, 'doubleContent archiveContent')]/div/div[@class='illuBox']/a/span/..")

    titles_and_urls += [extract_title_and_url_from_span_thing(link_hxs) for link_hxs in doublecontent_main_links]

    return titles_and_urls, []



def show_frontpage():
    frontpage_items, blogposts = get_frontpage_toc()

    for title, url in frontpage_items:
        print u"{0} \t\t [{1}]".format(title, url)

    print len(frontpage_items)


def main():
    show_frontpage()



if __name__ == "__main__":
    main()








