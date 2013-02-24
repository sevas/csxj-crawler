#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
from datetime import datetime
import codecs
from itertools import izip, chain
from urlparse import urlparse
from scrapy.selector import HtmlXPathSelector

from csxj.common.tagging import classify_and_tag, make_tagged_url, update_tagged_urls, update_tagged_urls
from csxj.db.article import ArticleData
from parser_tools.utils import fetch_html_content
from parser_tools.utils import extract_plaintext_urls_from_text, setup_locales
from parser_tools.utils import remove_text_formatting_markup_from_fragments, remove_text_formatting_and_links_from_fragments
from helpers.unittest_generator import generate_test_func, save_sample_data_file

setup_locales()

SOURCE_TITLE = u"L'Avenir"
SOURCE_NAME = u"lavenir"

LAVENIR_INTERNAL_BLOGS = {
    'lavenir.newspaperdirect.com': ['internal', 'pdf newspaper']
}

LAVENIR_NETLOC = 'www.lavenir.net'

BLACKLIST = ["http://citysecrets.lavenir.net"]

LAVENIR_SAME_OWNER = [
    'corelioconnect.be',
    'corelioclassifieds.be',
    'travelspotter.be',
    'wematch.be',
    'notarisblad.be',
    'inmemoriam.be',
    'necrologies.net',
    'jobat.be',
    'gezondheid.be',
    'passionsante.be',
    'zimmo.be',
    'immonot.be',
    'vroom.be',
    'siaffinites.be',
    'citysecrets.be',
    'coldsetprintingpartners.be',
    'corelioprinting.be',
    'arco.be',
    'mifratel.be',
    'queromedia.be',
    'xpertize.be',
    'larian.com',
    'wataro.com',
    'domaininvest.lu',
    'oxynade.com',
    'detondeldoos.be',
    'adam.be',
    'standaard.be',
    'nieuwsblad.be',
    'gentenaar.be',
    'sportwereld.be',
    'nostalgie.be',
    'robtv.be',
    'vier.be',
    'vijf.be',
    'humo.be',
    'woestijnvis.be',
    'thebulletin.be',
    'xpats.com',
    'passe-partout.be',
    'passionsante.be',
    'plusplus.be'
]


def is_internal_url(url):
    if url.startswith('/'):
        return True
    else:
        parsed_url = urlparse(url)
        scheme, netloc, path, params, query, fragments = parsed_url
        return LAVENIR_NETLOC.endswith(netloc)


def extract_publication_date(raw_date):
    date_string = raw_date.split(':')[1].strip().split("&")[0]
    date_bytestring = codecs.encode(date_string, 'utf-8')

    date_component_count = len(date_bytestring.split(" "))
    if date_component_count == 4:
        datetime_published = datetime.strptime(date_bytestring, u"%A %d %B %Y")
    elif date_component_count == 5:
        datetime_published = datetime.strptime(date_bytestring, u"%A %d %B %Y %Hh%M")
    else:
        raise ValueError("Date has an unknown format: {0}".format(date_bytestring))

    return datetime_published.date(), datetime_published.time()


def extract_links_from_article_body(article_body_hxs):
    links = list()
    # intext urls
    urls = article_body_hxs.select(".//p//a/@href").extract()
    titles = [t.strip() for t in article_body_hxs.select(".//p//a//text()").extract()]

    for title, url in izip(titles, urls):
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags.add('in text')
        links.append(make_tagged_url(url, title, tags))

    #plaintext text urls
    raw_content = article_body_hxs.select(".//p/text()").extract()

    if raw_content:
        for paragraph in raw_content:
            plaintext_urls = extract_plaintext_urls_from_text(remove_text_formatting_and_links_from_fragments(paragraph))
            for url in plaintext_urls:
                tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
                tags.update(['plaintext', 'in text'])
                links.append(make_tagged_url(url, url, tags))

    #embedded objects
    iframe_sources = article_body_hxs.select(".//iframe/@src").extract()
    for url in iframe_sources:
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags = tags.union(['in text', 'embedded', 'iframe'])
        links.append(make_tagged_url(url, url, tags))

    return links


def select_title_and_url(selector, tag_name):
    url = selector.select("./@href").extract()[0]
    title = selector.select(".//text()").extract()
    if title:
        title = remove_text_formatting_markup_from_fragments(title[0])
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags = tags.union([tag_name])
    else:
        tags = set([tag_name, 'ghost link'])
        title = '__GHOST_LINK__'
    return make_tagged_url(url, title, tags)


def extract_sidebar_links(sidebar_links):
    tagged_urls = [select_title_and_url(sidebar_link, 'sidebar box') for sidebar_link in sidebar_links]
    return tagged_urls


def extract_bottom_links(bottom_links):
    tagged_urls = [select_title_and_url(bottom_link, 'bottom box') for bottom_link in bottom_links]
    return tagged_urls


def extract_article_data(source):
    if hasattr(source, 'read'):
        html_content = source.read()
    else:
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

    # bottom links
    bottom_box = hxs.select('//div[@class="span-3 lire-aussi"]//a')
    all_links.extend(extract_bottom_links(bottom_box))

    updated_tagged_urls = update_tagged_urls(all_links, LAVENIR_SAME_OWNER)

    # print generate_test_func('external_links', 'lavenir', dict(tagged_urls=updated_tagged_urls))
    # save_sample_data_file(html_content, source, 'external_links', '/Users/judemaey/code/csxj-crawler/tests/datasources/test_data/lavenir')

    # wrapping up
    article_data = ArticleData(source, title, pub_date, pub_time, fetched_datetime,
                               updated_tagged_urls,
                               category, author,
                               intro, content)

    return article_data, html_content


def expand_full_url(local_url):

    if not local_url.startswith("http://"):
        return "http://{0}{1}".format(LAVENIR_NETLOC, local_url)
    else:
        return local_url


def extract_title_and_url(link_hxs):
    url = link_hxs.select("./@href").extract()[0]
    title = link_hxs.select("./text()").extract()[0].strip()
    return title, url


def separate_blogposts(all_items):
    blogpost_items = set([(title, url)for title, url in all_items if not is_internal_url(url)])
    news_items = set(all_items) - blogpost_items

    return news_items, blogpost_items


def get_frontpage_toc():
    url = "http://{0}".format(LAVENIR_NETLOC)
    html_data = fetch_html_content(url)

    hxs = HtmlXPathSelector(text=html_data)

    story_links = hxs.select("//div[@id='content']//div[starts-with(@class, 'fr-row')]//h3/a")
    more_story_links = hxs.select("//div[@id='content']//div[starts-with(@class, 'fr-section')]//h3/a")
    local_sport_links = hxs.select("//div[@id='content']//div[contains(@class, 'article-with-photo')]//h2/a")
    nopic_story_list = hxs.select("//div[@id='content']//ul[@class='nobullets']//li//div[contains(@class, 'item-title')]//a")

    all_links = chain(story_links, more_story_links, local_sport_links, nopic_story_list)

    all_items = [extract_title_and_url(link_hxs) for link_hxs in all_links]
    news_items, blogpost_items = separate_blogposts(all_items)

    return  [(title, expand_full_url(url)) for (title, url) in news_items if url not in BLACKLIST], list(blogpost_items), []


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


def show_sample_articles():
    urls = ["http://www.lavenir.net/article/detail.aspx?articleid=DMF20120326_023",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120330_00139582",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120331_00140331",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120902_00199571",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120902_00199563",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120831_00199041",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120901_00199541",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120831_00198968",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120901_00199482",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120317_002",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120317_002",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130224_001",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130224_005",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130224_016",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130221_00271965",
            "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130224_00273104"

            ]

    # for url in urls[:]:
    #     article, raw_html = extract_article_data(url)
    #     article.print_summary()
    #     for tagged_link in article.links:
    #         print tagged_link.URL, tagged_link.title, tagged_link.tags

    article, html = extract_article_data(urls[1])
    # print article.title
    # print article.intro
    # print article.url
    # print article.content
    # print "LINKS:"
    # for link in article.links:
    #     print link.title
    #     print link.URL
    #     print link.tags
    #     print "___________"


def show_frontpage():
    toc, blogposts = get_frontpage_toc()
    print "Articles:"
    for title, url in toc:
        print u"{0} [{1}]".format(title, url)

    print "BLogposts:"
    for title, url in blogposts:
        print u"{0} [{1}]".format(title, url)

    print len(toc), len(blogposts)


def show_frontpage_articles():
    toc, posts = get_frontpage_toc()
    print len(toc), len(posts)
    for title, url in toc:
        print u"{0} [{1}]".format(title, url)

        article_data, raw_html = extract_article_data(url)
        article_data.print_summary()

        print "********\n\n"


if __name__ == "__main__":
    show_sample_articles()
    #show_frontpage_articles()
    #show_frontpage()
