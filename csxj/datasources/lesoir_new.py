#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
from datetime import datetime, time
import urlparse
import bs4
from common import utils
from common import twitter_utils
from csxj.common import tagging
from csxj.db.article import ArticleData


LESOIR_NETLOC = "www.lesoir.be"
LESOIR_INTERNAL_SITES = {}


def extract_title(soup):
    # trouver le titre
    main_content = soup.find(attrs = {"id" : "main-content"})
    title = main_content.find("h1").contents[0]
    return title

def extract_author_name(soup):
    authors = []
    meta_box = soup.find(attrs = {"class" : "meta"})
    author_name = meta_box.find("strong").contents[0]
    authors.append(author_name)

    #sometimes there's an author mentioned in bold at the end of the article

    return authors

def extract_date_and_time(author_box):
    pass

def extract_intro(soup):
    intro_box = soup.find(attrs = {"class" : "article-content"})
    intro = intro_box.find("h3").contents[0]
    return intro

def extract_title_and_url_from_bslink(link):
    base_tags = []
    if link.get('href'):
        url = link.get('href')
    else :
        url = "__GHOST_LINK__"
        base_tags.append("ghost link")
        
    if link.find('h3'):
        title = link.find('h3').contents[0].strip()
    else:
        if link.contents:
            title = link.contents[0].strip()
        else:
            title = "__GHOST_LINK__"
            base_tags.append("ghost link")

    return title, url, base_tags


def extract_text_content_and_links(soup) :
    article_text = []
    inline_links = []

    text = soup.find(attrs = {"class" : "article-body"})
    paragraphs = text.find_all("p")
    clean_text = utils.remove_text_formatting_markup_from_fragments(paragraphs, strip_chars = "\n")
    article_text.append(clean_text)
    for p in paragraphs:
        link = p.find_all("a")
        inline_links.extend(link)

    
    plaintext_urls = []

    for x in article_text:
        plaintext_links = utils.extract_plaintext_urls_from_text(x)
        plaintext_urls.extend(plaintext_links)


    titles_and_urls = [extract_title_and_url_from_bslink(i) for i in inline_links]

    tagged_urls = list()
    for title, url, base_tags in titles_and_urls:
        tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
        tags.add('in text')
        tagged_urls.append(tagging.make_tagged_url(url, title, tags))

    for url in plaintext_urls:
        tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
        tags.add('in text')
        tags.add('plaintext')
        tagged_urls.append(tagging.make_tagged_url(url, url, tags))

    return article_text, tagged_urls

def extract_article_tags(soup):
    tagged_urls = list()
    meta_box = soup.find(attrs = {"class" : "meta"})
    if meta_box.find(attrs = {'class': 'tags'}):
        tags = meta_box.find(attrs = {'class': 'tags'})
        links = tags.find_all("a")
        titles_and_urls = [extract_title_and_url_from_bslink(link) for link in links]
        for title, url, base_tags in titles_and_urls:
            tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            tags.add('article tag')
            tagged_urls.append(tagging.make_tagged_url(url, title, tags))

    for x in tagged_urls:
        print x
    return tagged_urls


def extract_category(soup):
    breadcrumbs = soup.find('div', {'class':'breadcrumbs'})
    category_stages = [a.contents[0] for a in breadcrumbs.findAll('a') ]
    return category_stages

def extract_links_from_sidebar_box(soup):
    tagged_urls = list()
    sidebar_box = soup.find('div', {'class': 'box alt'})
    if sidebar_box:
        links = sidebar_box.find_all('a')
        titles_and_urls = [extract_title_and_url_from_bslink(link) for link in links]
        for title, url, base_tags in titles_and_urls:
            tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            tags.add('sidebar box')
            tagged_urls.append(tagging.make_tagged_url(url, title, tags))
    for x in tagged_urls:
        print x
    return tagged_urls


def extract_article_data(url):

    request  = urllib.urlopen(url)
    html_data = request.read()

    soup  = bs4.BeautifulSoup(html_data)
    title = extract_title(soup)
    author_name = extract_author_name(soup)
    intro = extract_intro(soup)
    text, tagged_urls_intext = extract_text_content_and_links(soup)
    category = extract_category(soup)
    sidebar_links = extract_links_from_sidebar_box(soup)
    article_tags = extract_article_tags(soup)


if __name__ == '__main__':

    url = "http://www.lesoir.be/142224/article/culture/medias-tele/2012-12-21/audrey-pulvar-quitte-inrocks"
    url = "http://www.lesoir.be/142193/article/debats/cartes-blanches/2012-12-21/g%C3%A9rard-depardieu-l%E2%80%99arbre-qui-cache-for%C3%AAt"
 #   url = "http://www.lesoir.be/142176/article/actualite/belgique/2012-12-21/van-rompuy-%C2%AB-etre-premier-en-belgique-c%E2%80%99est-frustrant-%C2%BB"
    extract_article_data(url)





