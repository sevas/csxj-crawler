#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
from datetime import datetime
from scrapy.selector import HtmlXPathSelector
import urlparse
import codecs
from itertools import izip
from csxj.common.tagging import tag_URL, classify_and_tag, make_tagged_url, TaggedURL
from csxj.db.article import ArticleData
from common.utils import fetch_html_content, fetch_rss_content, make_soup_from_html_content
from common.utils import remove_text_formatting_markup, extract_plaintext_urls_from_text
from common import constants
from itertools import izip


# for datetime conversions
if sys.platform in ['linux2', 'cygwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF8')
elif sys.platform in [ 'darwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR')
elif sys.platform in [ 'win32']:
    # locale string from: http://msdn.microsoft.com/en-us/library/cdax410z(v=VS.80).aspx
    locale.setlocale(locale.LC_ALL, 'fra')

SOURCE_TITLE = u"L'Avenir"
SOURCE_NAME = u"lavenir"

LAVENIR_INTERNAL_BLOGS = {}


LAVENIR_NETLOC = 'www.lavenir.net'

BLACKLIST = ["http://citysecrets.lavenir.net"]



def extract_publication_date(raw_date):
    date_string = raw_date[0].split(':')[1].strip().split("&")[0]
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
        tags.union(['in text', 'plaintext'])
        links.append(make_tagged_url(url, url, tags))


    #embedded objects
    iframe_sources = article_body_hxs.select(".//iframe/@src").extract()
    for url in iframe_sources:
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags.union(['in text', 'embedded', 'iframe'])
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
        tags.union(['sidebar'])
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
    raw_date = article_detail_hxs.select(".//div[@id='intro']//li[@id='liDate']/*").extract()
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


def expand_full_urls(local_urls):
    story_urls = list()
    for url in local_urls:
        if not url.startswith("http://"):
            story_urls.append("http://{0}{1}".format(LAVENIR_NETLOC, url))
        else:
            story_urls.append(url)
    return story_urls


def get_frontpage_toc():
    url = "http://{0}".format(LAVENIR_NETLOC)
    html_data = fetch_html_content(url)

    hxs = HtmlXPathSelector(text=html_data)

    local_story_urls = hxs.select("//div[@id='content']/div[2]/div/div[@class='span-3 border ' or @class='span-2 last ']//h2/a/@href").extract()
    story_urls = expand_full_urls(local_story_urls)
    story_titles = [t.strip() for t in hxs.select("//div[@id='content']/div[2]/div/div[@class='span-3 border ' or @class='span-2 last ']//h2/a/text()").extract()]


    quote_titles = [u"\"{0}\"".format(title) for title in hxs.select("//div[@id='content']/div[2]/div/div[@class='span-3 border ']//div[@class='pullquote-full']//q/text()").extract()]
    quote_urls= hxs.select("//div[@id='content']/div[2]/div/div[@class='span-3 border ']//div[@class='pullquote-full']/a/@href").extract()

    titles_and_urls = zip(story_titles, story_urls)



    return [(title, url) for (title, url) in titles_and_urls if url not in BLACKLIST] + zip(quote_titles, quote_urls)



def show_article():

    normal_url = "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120221_00121183"
    photoset_url = "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120224_00122366"
    intro_url = "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120226_002"
    photoset_with_links = "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120222_00121489"

    #for url in [normal_url, photoset_url, intro_url, photoset_with_links]:
    for url in [photoset_with_links]:
        article, raw_html = extract_article_data(url)
        article.print_summary()
        for tagged_link in article.links:
            print tagged_link.URL, tagged_link.title, tagged_link.tags


def show_frontpage():
    toc = get_frontpage_toc()
    for title, url in toc:
        print u"{0} [{1}]".format(title, url)

    print len(toc)


def show_frontpage_articles():
    toc = get_frontpage_toc()
    for title, url in toc:
        print u"{0} [{1}]".format(title, url)
        try:
            article_data, raw_html = extract_article_data(url)
            article_data.print_summary()
        except Exception as e:
            print e.message
            print "DELETED"
        print "********\n\n"



if __name__ == "__main__":
    #show_article()
    show_frontpage_articles()
    #show_frontpage()
