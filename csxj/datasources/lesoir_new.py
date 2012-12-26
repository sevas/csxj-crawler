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
    return tagged_urls

def extract_embedded_media_from_top_box(soup):
    tagged_urls = list()
    top_box = soup.find(attrs = {'class': 'block-slidepic media'})
    if top_box.find("embed"):
        url = top_box.find("embed").get("src")
        if url :
            tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            tags.add('embedded')
            tagged_urls.append(tagging.make_tagged_url(url, url, tags))
        else :
            raise ValueError("There to be an embedded object but we could not find an link. Update the parser.")
    kplayer = top_box.find(attrs = {'class': 'emvideo emvideo-video emvideo-kewego'})
    if kplayer:
        url_part1 = kplayer.object['data']
        url_part2 = kplayer.object.find('param', {'name' : 'flashVars'})['value']
        if url_part1 is not None and url_part2 is not None:
            url = "%s?%s" % (url_part1, url_part2)
            tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            if kplayer.next_sibling.name == "figcaption":
                if len(kplayer.next_sibling) > 0 :
                    title = kplayer.next_sibling.contents[0]
                    tagged_urls.append(tagging.make_tagged_url(url, title, tags | set(['embedded'])))
                else :
                    title = "__NO_TITLE__"
                    tagged_urls.append(tagging.make_tagged_url(url, title, tags | set(['embedded'])))
            else:
                title = "__NO_TITLE__"
                tagged_urls.append(tagging.make_tagged_url(url, title, tags | set(['embedded'])))
        else:
            raise ValueError("We couldn't find an URL in the flash player. Update the parser.")
    return tagged_urls

def extract_embedded_media_from_bottom(soup):
    tagged_urls = list()
    article_body = soup.find(attrs = {'class': 'article-body'})
    bottom_box = article_body.find(attrs = {'class' : 'related-media'})
    if bottom_box :
        embedded_media = bottom_box.find("iframe")
        if embedded_media:
            url = embedded_media.get("src")
            tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            tags.add('embedded')
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
                tagged_urls.append(tagging.make_tagged_url(url, url, all_tags | set(['embedded'])))
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
    embedded_media_from_top_box = extract_embedded_media_from_top_box(soup)
    embedded_media_from_bottom = extract_embedded_media_from_bottom(soup)
    embedded_media_in_article = extract_embedded_media_in_article(soup)
    print embedded_media_in_article

if __name__ == '__main__':

    url = "http://www.lesoir.be/142224/article/culture/medias-tele/2012-12-21/audrey-pulvar-quitte-inrocks"
    url = "http://www.lesoir.be/142193/article/debats/cartes-blanches/2012-12-21/g%C3%A9rard-depardieu-l%E2%80%99arbre-qui-cache-for%C3%AAt"
    url = "http://www.lesoir.be/142176/article/actualite/belgique/2012-12-21/van-rompuy-%C2%AB-etre-premier-en-belgique-c%E2%80%99est-frustrant-%C2%BB"
    url = "http://www.lesoir.be/142265/article/actualite/belgique/2012-12-21/quatre-militantes-anti-poutine-interpell%C3%A9es-%C3%A0-bruxelles"
    url = "http://www.lesoir.be/140983/article/actualite/regions/bruxelles/2012-12-19/sacs-bleus-et-jaunes-sort-en-est-jet%C3%A9"
    url = "http://www.lesoir.be/141646/article/actualite/regions/bruxelles/2012-12-20/stib-l-abonnement-scolaire-co%C3%BBtera-120-euros"
    url = "http://www.lesoir.be/141861/article/debats/chats/2012-12-20/11h02-relations-du-parti-islam-avec-l-iran-posent-question"
    url = "http://www.lesoir.be/141613/article/actualite/regions/bruxelles/2012-12-20/catteau-danse-contre-harc%C3%A8lement"
    url = "http://www.lesoir.be/141854/article/debats/chats/2012-12-20/pol%C3%A9mique-sur-michelle-martin-%C2%ABne-confondons-pas-justice-et-vengeance%C2%BB"
    url = "http://www.lesoir.be/142297/article/sports/football/2012-12-21/genk-anderlecht-en-direct-comment%C3%A9"
    url = "http://www.lesoir.be/91779/article/actualite/belgique/2012-10-02/coupure-d%E2%80%99%C3%A9lectricit%C3%A9-%C3%A0-bruxelles-est-due-%C3%A0-un-incident-chez-elia"
    extract_article_data(url)





