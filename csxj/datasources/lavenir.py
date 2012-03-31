#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
from datetime import datetime
import codecs
from itertools import izip

from scrapy.selector import HtmlXPathSelector

from csxj.common.tagging import classify_and_tag, make_tagged_url
from csxj.db.article import ArticleData
from common.utils import fetch_html_content, fetch_rss_content
from common.utils import extract_plaintext_urls_from_text, setup_locales


setup_locales()

SOURCE_TITLE = u"L'Avenir"
SOURCE_NAME = u"lavenir"

LAVENIR_INTERNAL_BLOGS = {}


LAVENIR_NETLOC = 'www.lavenir.net'

BLACKLIST = ["http://citysecrets.lavenir.net"]



def extract_publication_date(raw_date):
    date_string = raw_date.split(':')[1].strip().split("&")[0]
    date_bytestring = codecs.encode(date_string, 'utf-8')

    datetime_published = datetime.strptime(date_bytestring, u"%A %d %B %Y %Hh%M")

    return datetime_published.date(), datetime_published.time()



def extract_links_from_article_body(article_body_hxs):
    links = list()
    # intext urls
    urls = article_body_hxs.select(".//p/a/@href").extract()
    titles = [t.strip() for t in article_body_hxs.select(".//p/a//text()").extract()]

    for title, url in izip(titles, urls):
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags.add('in text')
        links.append(make_tagged_url(url, title, tags))

    #plaintext text urls
    raw_content = article_body_hxs.select(".//p/text()").extract()
    content_as_text = ''.join(raw_content)
    plaintext_urls = extract_plaintext_urls_from_text(content_as_text)

    for url in plaintext_urls:
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags = tags.union(['in text', 'plaintext'])
        links.append(make_tagged_url(url, url, tags))


    #embedded objects
    iframe_sources = article_body_hxs.select(".//iframe/@src").extract()
    for url in iframe_sources:
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags = tags.union(['in text', 'embedded', 'iframe'])
        links.append(make_tagged_url(url, url, tags))



    return links


def extract_sidebar_links(sidebar_links):
    links = list()
    def select_title_and_url(selector):
        url = selector.select("./@href").extract()[0]
        title = selector.select(".//text()").extract()[0]
        return title, url

    titles_and_urls = [select_title_and_url(sidebar_link) for sidebar_link in sidebar_links]
    for (title, url) in titles_and_urls:
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags = tags.union(['sidebar'])
        links.append(make_tagged_url(url, title, tags))

    return links


def extract_article_data(source):
    html_content = fetch_html_content(source)

    hxs = HtmlXPathSelector(text=html_content)

    # extract breadcrumbs for category info
    category = hxs.select("//div[@id='content']/*[1]/p/a/text()").extract()

    #extractc title
    article_detail_hxs = hxs.select("//div[@id='content']/div[starts-with(@class,'span-3 article-detail')]")
    #intro_h1s = hxs.select("//div[@id='content']/div[@class='span-3 article-detail ']//div[@id='intro']/h1/text()").extract()
    intro_h1s = article_detail_hxs.select(".//div[@id='intro']/h1/text()").extract()
    title = ''
    if len(intro_h1s) == 1:
        title = intro_h1s[0].strip()
    else:
        return None

    # all the date stuff
    #raw_date = article_detail_hxs.select(".//div[@id='intro']//li[@id='liDate']/*").extract()
    raw_date = ''.join([t.strip() for t in article_detail_hxs.select(".//div[@id='intro']//li[@id='liDate']//text()").extract()])
    pub_date, pub_time = extract_publication_date(raw_date)
    fetched_datetime = datetime.today()


    #author(s)
    raw_author = article_detail_hxs.select("./div/ul/li[@class='author']/text()").extract()
    author = None
    if raw_author:
        author = raw_author[0].strip()

    #intro
    intro = None
    raw_intro = article_detail_hxs.select("./div/div[@class='intro ']//text()").extract()
    if raw_intro:
        intro = ''.join([fragment.strip() for fragment in raw_intro])

    # in photosets pages, the structure is a bit different
    if not intro:
        raw_intro = article_detail_hxs.select("./div/div[@class='intro']//text()").extract()
    if raw_intro:
        intro = ''.join([fragment.strip() for fragment in raw_intro])


    #detect photoset
    full_class = article_detail_hxs.select("./@class").extract()[0]
    if 'article-with-photoset' in full_class.split(" "):
        title = u"{0}|{1}".format("PHOTOSET", title)




    all_links = list()

    #content
    article_body = article_detail_hxs.select("./div/div[@class='article-body ']")
    content = article_body.select(".//p//text()").extract()


    all_links.extend(extract_links_from_article_body(article_body))


    # associated sidebar links
    sidebar_links = article_detail_hxs.select("./div/div[@class='article-side']/div[@class='article-related']//li/a")
    all_links.extend(extract_sidebar_links(sidebar_links))


    # wrapping up
    article_data = ArticleData(source, title, pub_date, pub_time, fetched_datetime,
                               all_links,
                               category, author,
                               intro, content)

    return article_data, html_content


def expand_full_url(local_url):

    if not local_url.startswith("http://"):
        return "http://{0}{1}".format(LAVENIR_NETLOC, local_url)
    else:
        return local_url



def extract_title_and_url(link_hxs):
    url = expand_full_url(link_hxs.select("./@href").extract()[0])
    title = link_hxs.select("./text()").extract()[0].strip()
    return url, title


def get_frontpage_toc():
    url = "http://{0}".format(LAVENIR_NETLOC)
    html_data = fetch_html_content(url)

    hxs = HtmlXPathSelector(text=html_data)

    story_links = hxs.select("//div[@id='content']//div/div[@class='span-3 border ' or @class='span-2 last ']//h2/a")
    story_items = [extract_title_and_url(link_hxs) for link_hxs in story_links]

    today_image_link = hxs.select("//p[text()=\"\r\n    L'image du jour\r\n\"]/../div[@class='content']//div[@class='item-title']/a")

    story_items.append(extract_title_and_url(today_image_link))

    return  [(url, title) for (url, title) in story_items if url not in BLACKLIST], []



def show_sample_articles():

    normal_url = "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120221_00121183"
    photoset_url = "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120224_00122366"
    intro_url = "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120226_002"
    photoset_with_links = "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120222_00121489"


    norma_url = "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120330_00139582"
    for url in [normal_url, photoset_url, intro_url, photoset_with_links]:
    #for url in [normal_url]:
        article, raw_html = extract_article_data(url)
        article.print_summary()
        for tagged_link in article.links:
            print tagged_link.URL, tagged_link.title, tagged_link.tags


def show_article():
    url = "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120326_023"
    url = "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120330_00139582"
    url = "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120331_00140331"
    article, raw_html = extract_article_data(url)
    article.print_summary()
    for tagged_link in article.links:
        print tagged_link.URL, tagged_link.title, tagged_link.tags



def show_frontpage():
    toc, blogposts = get_frontpage_toc()
    for title, url in toc:
        print u"{0} [{1}]".format(title, url)

    print len(toc)


def show_frontpage_articles():
    toc, posts = get_frontpage_toc()
    for url, title in toc:
        print u"{0} [{1}]".format(title, url)

        article_data, raw_html = extract_article_data(url)
        article_data.print_summary()

        print "********\n\n"



if __name__ == "__main__":
    #show_article()
    show_frontpage_articles()
    #show_frontpage()
