#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import codecs
from datetime import datetime, time
import urlparse
import bs4
import itertools
from scrapy.selector import HtmlXPathSelector
from parser_tools import utils
from parser_tools import twitter_utils
from parser_tools.utils import remove_text_formatting_markup_from_fragments, extract_plaintext_urls_from_text, remove_text_formatting_and_links_from_fragments
from csxj.common import tagging
from csxj.db.article import ArticleData
from parser_tools.utils import fetch_html_content
from parser_tools.utils import setup_locales
from parser_tools import rossel_utils

from helpers.unittest_generator import generate_test_func, save_sample_data_file


setup_locales()

SOURCE_TITLE = u"Le Soir"
SOURCE_NAME = u"lesoir_new"

LESOIR_NETLOC = "www.lesoir.be"
LESOIR_INTERNAL_SITES = {

    'archives.lesoir.be': ['archives', 'internal'],
   
    'belandroid.lesoir.be':['internal', 'jblog'],
    'geeko.lesoir.be':['internal', 'jblog'],
    'blog.lesoir.be':['internal', 'jblog'],

    'belandroid.lesoir.be': ['internal', 'jblog'],
    'geeko.lesoir.be': ['internal', 'jblog'],
    'blog.lesoir.be': ['internal', 'jblog'],

    'pdf.lesoir.be': ['internal', 'pdf newspaper']
}


def extract_title_and_url(link_hxs):
    title = u"".join(link_hxs.select("text()").extract())
    url = link_hxs.select('@href').extract()[0]
    if not title:
        title = u"__NO_TITLE__"
    return title, url


def separate_news_and_blogposts(titles_and_urls):
    def is_external_blog(url):
        return not url.startswith('/')

    toc, blogposts = list(), list()
    for t, u in titles_and_urls:
        if is_external_blog(u):
            blogposts.append((t, u))
        else:
            toc.append((t, u))
    return toc, blogposts


def reconstruct_full_url(url):
    return urlparse.urljoin("http://{0}".format(LESOIR_NETLOC), url)



def separate_paywalled_articles(all_link_hxs):
    regular, paywalled = list(), list()
    for link_hxs in all_link_hxs:
        if link_hxs.select("../span [@class='ir locked']"):
            paywalled.append(link_hxs)
        else:
            regular.append(link_hxs)
    return regular, paywalled



def get_frontpage_toc():
    html_data = fetch_html_content('http://www.lesoir.be')
    hxs = HtmlXPathSelector(text=html_data)

    # main stories
    list_items = hxs.select("//div [@id='main-content']//ul/li")
    headlines_links = list_items.select("./h2/a | ./h3/a")

    # just for the blog count statistics
    blog_block = hxs.select("//div [@class='bottom-content']//div [@class='block-blog box']//h5/a")

    # mainly soccer
    sport_block = hxs.select("//div [@class='bottom-content']//div [@class='block-sport']")
    sports_links = sport_block.select(".//h2/a | .//aside//li/a")

    # bottom sections
    bottom_news_links = hxs.select("//div [@class='bottom-content']//div [@class='block-articles']//a")


    all_links_hxs = itertools.chain(headlines_links, blog_block, sports_links, bottom_news_links)
    regular_articles_hxs, all_paywalled_hxs = separate_paywalled_articles(all_links_hxs)

    titles_and_urls = [extract_title_and_url(link) for link in regular_articles_hxs]
    paywalled_titles_and_urls = [extract_title_and_url(link) for link in all_paywalled_hxs]

    articles_toc, blogpost_toc = separate_news_and_blogposts(titles_and_urls)
    return [(title, reconstruct_full_url(url)) for (title, url) in articles_toc], blogpost_toc, [(title, reconstruct_full_url(url)) for (title, url) in paywalled_titles_and_urls]


def extract_title(soup):
    # trouver le titre
    main_content = soup.find(attrs={"id": "main-content"})
    title = main_content.find("h1").contents[0]
    return title


def extract_author_name(soup):
    authors = []
    meta_box = soup.find(attrs={"class": "meta"})
    #sometimes there's an author mentioned in bold at the end of the article
    author_name = meta_box.find("strong").contents[0]
    authors.append(author_name)

    #sometimes there's an author mentioned in bold at the end of the article

    return authors


def extract_date_and_time(soup):
    meta_box = soup.find(attrs={"class": "meta"})
    date = meta_box.find(attrs={"class": "prettydate"})
    date_part1 = date.contents[0]
    date_part2 = date.contents[-1]
    full_date_and_time_string = "%sh%s" % (date_part1, date_part2)
    date_bytestring = codecs.encode(full_date_and_time_string, 'utf-8')
    datetime_published = datetime.strptime(date_bytestring, u'%A %d %B %Y, %Hh%M')
    return datetime_published.date(), datetime_published.time()


def extract_intro(soup):
    intro_box = soup.find(attrs={"class": "article-content"})
    intro = intro_box.find("h3").contents[0]
    return intro


def extract_title_and_url_from_bslink(link):
    base_tags = []
    if link.get('href'):
        url = link.get('href')
    else:
        url = "__GHOST_LINK__"
        base_tags.append("ghost link")

    if link.find('h3'):
        title = link.find('h3').contents[0].strip()
    else:
        if link.contents:
            if len(link.contents[0]) > 1:
                if type(link.contents[0]) is bs4.element.NavigableString:
                    title = link.contents[0].strip()
                else:
                    title = "__GHOST_LINK__"
                    base_tags.append("ghost link")
            else:
                title = "__GHOST_LINK__"
                base_tags.append("ghost link")
        else:
            title = "__GHOST_LINK__"
            base_tags.append("ghost link")
    return title, url, base_tags


def extract_text_content_and_links(soup) :
    tagged_urls = list()
    inline_links = []
    text = list()

    article_body = soup.find(attrs = {"class" : "article-body"})
    text_fragments = article_body.find_all("p")

    if text_fragments:
        for paragraph in text_fragments:
            text.append(u"".join(remove_text_formatting_markup_from_fragments(paragraph)))

        plaintext_urls = extract_plaintext_urls_from_text(remove_text_formatting_and_links_from_fragments(text_fragments))
        for url in plaintext_urls:
            tags = classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            tags.update(['plaintext', 'in text'])

            tagged_urls.append(make_tagged_url(url, url, tags))
    else:
        text = u""

    for p in text_fragments :
        link = p.find_all("a")
        inline_links.extend(link)

    titles_and_urls = [extract_title_and_url_from_bslink(i) for i in inline_links]

    for title, url, base_tags in titles_and_urls:
        tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
        tags.update(base_tags)
        tags.add('in text')
        tagged_urls.append(tagging.make_tagged_url(url, title, tags))


    return text, tagged_urls

def extract_article_tags(soup):
    tagged_urls = list()
    meta_box = soup.find(attrs={"class": "meta"})
    if meta_box.find(attrs={'class': 'tags'}):
        tags = meta_box.find(attrs={'class': 'tags'})
        links = tags.find_all("a")
        titles_and_urls = [extract_title_and_url_from_bslink(link) for link in links]
        for title, url, base_tags in titles_and_urls:
            tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            tags.update(base_tags)
            tags.add('keyword')
            tagged_urls.append(tagging.make_tagged_url(url, title, tags))

    return tagged_urls


def extract_category(soup):
    breadcrumbs = soup.find('div', {'class': 'breadcrumbs'})
    category_stages = [a.contents[0] for a in breadcrumbs.findAll('a')]
    return category_stages


def extract_links_from_sidebar_box(soup):
    tagged_urls = list()
    sidebar_boxes = soup.find_all('div', {'class': 'box alt'})
    if sidebar_boxes:
        for sidebar_box in sidebar_boxes:
            links = sidebar_box.find_all('a')
            titles_and_urls = [extract_title_and_url_from_bslink(link) for link in links]
            for title, url, base_tags in titles_and_urls:
                tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
                tags.update(base_tags)
                tags.add('sidebar box')
                tagged_urls.append(tagging.make_tagged_url(url, title, tags))
    return tagged_urls


def extract_embedded_media_from_top_box(soup):
    tagged_urls = list()
    top_box = soup.find(attrs={'class': 'block-slidepic media'})
    if top_box.find("embed"):
        url = top_box.find("embed").get("src")
        if url:
            tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            tags.add('embedded')
            tags.add('top box')
            tagged_urls.append(tagging.make_tagged_url(url, url, tags))
        else:
            raise ValueError("There to be an embedded object but we could not find an link. Update the parser.")

    # sometimes it's a kewego player
    kplayer = top_box.find(attrs={'class': 'emvideo emvideo-video emvideo-kewego'})
    if kplayer:
        url_part1 = kplayer.object['data']
        url_part2 = kplayer.object.find('param', {'name': 'flashVars'})['value']
        if url_part1 is not None and url_part2 is not None:
            url = "%s?%s" % (url_part1, url_part2)
            tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            if kplayer.next_sibling.name == "figcaption":
                if len(kplayer.next_sibling) > 0:
                    title = kplayer.next_sibling.contents[0]
                    tagged_urls.append(tagging.make_tagged_url(url, title, tags | set(['embedded', 'top box', 'kplayer'])))
                else:
                    title = "__NO_TITLE__"
                    tagged_urls.append(tagging.make_tagged_url(url, title, tags | set(['embedded', 'top box', 'kplayer'])))
            else:
                title = "__NO_TITLE__"
                tagged_urls.append(tagging.make_tagged_url(url, title, tags | set(['embedded', 'top box', 'kplayer'])))
        else:
            raise ValueError("We couldn't find an URL in the flash player. Update the parser.")

    # sometimes it's a youtube player
    youtube_player = top_box.find(attrs={'class': 'emvideo emvideo-video emvideo-youtube'})
    if youtube_player:
        url = youtube_player.find("a").get("href")
        if url:
            tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            tags.add('embedded')
            tags.add('top box')
            tags.add('video')
            tagged_urls.append(tagging.make_tagged_url(url, url, tags))
        else:
            raise ValueError("There seems to be a Youtube player but we couldn't find an URL. Update the parser.")
    return tagged_urls


def extract_embedded_media_from_bottom(soup):
    tagged_urls = list()
    article_body = soup.find(attrs={'class': 'article-body'})
    bottom_box = article_body.find(attrs={'class': 'related-media'})
    if bottom_box:
        embedded_media = bottom_box.find("iframe")
        if embedded_media:
            url = embedded_media.get("src")
            tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            tags.add('embedded')
            tags.add('iframe')
            tagged_urls.append(tagging.make_tagged_url(url, url, tags))
        else:
            raise ValueError("There seems to be an embedded media at the bottom of the article but we could not identify it. Update the parser")

    return tagged_urls


def extract_embedded_media_in_article(soup):
    tagged_urls = list()
    story = soup.find(attrs = {'class': 'article-body'})
    scripts = story.findAll('script', recursive=True)
    for script in scripts :
        url = script.get('src')
        if url :
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
            if netloc == "storify.com":
                url = url.rstrip(".js")
                all_tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
                tagged_urls.append(tagging.make_tagged_url(url, url, all_tags | set(['embedded', 'storify'])))
    return tagged_urls

def extract_article_data(source):

    if hasattr(source, 'read'):
        html_data = source.read()
    else:
        html_data = fetch_html_content(source)


    soup  = bs4.BeautifulSoup(html_data)
    title = extract_title(soup)
    author_name = extract_author_name(soup)
    intro = extract_intro(soup)
    text, tagged_urls_intext = extract_text_content_and_links(soup)
    category = extract_category(soup)
    sidebar_links = extract_links_from_sidebar_box(soup)
    article_tags = extract_article_tags(soup)
    embedded_media_from_top_box = extract_embedded_media_from_top_box(soup)
    embedded_media_from_bottom = extract_embedded_media_from_bottom(soup)
    embedded_media_in_article = extract_embedded_media_in_article(soup)
    embedded_media = embedded_media_from_top_box + embedded_media_from_bottom + embedded_media_in_article
    all_links = tagged_urls_intext + sidebar_links + article_tags + embedded_media
    pub_date, pub_time = extract_date_and_time(soup)
    fetched_datetime = datetime.today()

    updated_tagged_urls = tagging.update_tagged_urls(all_links, rossel_utils.LESOIR_SAME_OWNER)

    #print generate_test_func('in_text_and_sidebar', 'lesoir_new', dict(tagged_urls=updated_tagged_urls))
    #save_sample_data_file(html_data, source, 'in_text_and_sidebar', '/Users/judemaey/code/csxj-crawler/tests/datasources/test_data/lesoir_new')

    return (ArticleData(source, title, pub_date, pub_time, fetched_datetime,
                updated_tagged_urls,
                category, author_name,
                intro, text),
    html_data)


def test_sample_data():
    filepath = '../../sample_data/lesoir2/lesoir2.html'
    with open(filepath) as f:
        article, raw = extract_article_data(f)
        # from csxj.common.tagging import print_taggedURLs
        # print_taggedURLs(article.links)


if __name__ == '__main__':
    _, _, paywalled = get_frontpage_toc()
    for p in paywalled:
        print p
    
    article, html = extract_article_data(urls[-1])

    print article.title
    print article.content

    # for link in article.links:
    #     print link.title
    #     print link.URL
    #     print link.tags
    #     print "__________"


    # from csxj.common.tagging import print_taggedURLs
    # print_taggedURLs(article.links)


    # toc, blogposts = get_frontpage_toc()
    # for t, u in toc:
    #     url = codecs.encode(u, 'utf-8')
    #     print url
    #     try:
    #         extract_article_data(url)
    #     except Exception as e:
    #         print "Something went wrong with: ", url
    #         import traceback
    #         print traceback.format_exc()

    #     print "************************"



