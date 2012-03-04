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


SOURCE_TITLE = u"Le Vif"
SOURCE_NAME = u"levif"

LEVIF_INTERNAL_BLOGS = {
    'trends.levif.be':['internal blog', 'internal', 'economy'],
    'sportmagazine.levif.be':['internal blog', 'internal', 'sports'],
    'focus.lesoir.be':['internal blog', 'internal', 'entertainment'],
    'weekend.lesoir.be':['internal blog', 'internal']
}

LEVIF_NETLOC = 'www.levif.be'




def split_news_and_blogposts(titles_and_urls):
    frontpage_items, blogposts = list(), list()
    for title, url in titles_and_urls:
        parsed = urlparse.urlparse(url)
        scheme, netloc, path, params, query, fragment = parsed

        if netloc == LEVIF_NETLOC:
            frontpage_items.append((title, url))
        else:
            blogposts.append((title, url))

    return frontpage_items, blogposts



def extract_title_and_url(link_selector):
    url = link_selector.select("./@href").extract()[0]
    title = link_selector.select("./text()").extract()[0]
    return title, url


def get_frontpage_toc():
    url = "http://{0}/info".format(LEVIF_NETLOC)
    html_data = fetch_html_content(url)

    hxs = HtmlXPathSelector(text=html_data)


    h1_breaking_news_links = hxs.select("//div [@id='body']/div/div[@class='frame col_650']/div [@class='frame breakingNews']//div[@class='teaserContent']//h1/a")
    h2_breaking_news_links = hxs.select("//div [@id='body']/div/div[@class='frame col_650']/div [@class='frame breakingNews']//div[@class='teaserContent']//h2/a")

    other_news = hxs.select("//div [@id='body']/div/div[@class='frame col_650']/div [@class='frame teaserRow2 clearfix']//div[@class='teaserContent']/../h1/a")

    titles_and_urls = [extract_title_and_url(link_hxs) for link_hxs in chain(h1_breaking_news_links, h2_breaking_news_links, other_news)]

    frontpage_items, blogposts = split_news_and_blogposts(titles_and_urls)

    return frontpage_items, blogposts



def show_frontpage():
    frontpage_items, blogposts = get_frontpage_toc()

    print "NEWS ({0}):".format(len(frontpage_items))
    for title, url in frontpage_items:
        print u"{0} \t\t [{1}]".format(title, url)

    print "\n\nBLOGPOSTS ({0}):".format(len(blogposts))
    for title, url in blogposts:
        print u"{0} \t\t [{1}]".format(title, url)


def main():
    show_frontpage()

if __name__ == "__main__":
    main()