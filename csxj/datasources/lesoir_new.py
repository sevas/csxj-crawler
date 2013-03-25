#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import urlparse
import itertools
from datetime import datetime

import bs4
from scrapy.selector import HtmlXPathSelector

from csxj.common import tagging
from csxj.db.article import ArticleData
from parser_tools.utils import remove_text_formatting_markup_from_fragments, extract_plaintext_urls_from_text, remove_text_formatting_and_links_from_fragments
from parser_tools.utils import fetch_html_content
from parser_tools.utils import setup_locales
from parser_tools import rossel_utils
from parser_tools.utils import convert_utf8_url_to_ascii
from parser_tools import constants
from urllib2 import HTTPError

from helpers.unittest_generator import generate_test_func, save_sample_data_file


setup_locales()

SOURCE_TITLE = u"Le Soir"
SOURCE_NAME = u"lesoir_new"

LESOIR_NETLOC = "www.lesoir.be"
LESOIR_INTERNAL_SITES = {

    'archives.lesoir.be': ['archives', 'internal'],
    'belandroid.lesoir.be': ['internal', 'jblog'],
    'geeko.lesoir.be': ['internal', 'jblog'],
    'blog.lesoir.be': ['internal', 'jblog'],

    'belandroid.lesoir.be': ['internal', 'jblog'],
    'geeko.lesoir.be': ['internal', 'jblog'],
    'blog.lesoir.be': ['internal', 'jblog'],

    'pdf.lesoir.be': ['internal', 'pdf newspaper']
}


def extract_title_and_url(link_hxs):
    title = u"".join(link_hxs.select("text()").extract())
    url = link_hxs.select('@href').extract()[0]
    if not title:
        title = constants.NO_TITLE
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
    # print soup.find(attrs={"id": "main-content"}).find("h2")
    # print soup.find("div", {"class": "article-content"}).find("h2")
    # print soup.find(attrs={"class": "meta"}).previous_sibling.previous_sibling
    if main_content.find("h1"):
        title = main_content.find("h1").contents[0]
    else:
        title = main_content.find("h2").contents[0]
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
    if soup.find(attrs={"class": "article-content"}).h3:
        intro_box = soup.find(attrs={"class": "article-content"})

        def extract_links_from_intro(fragment):
            tagged_urls = list()
            inline_links = fragment.find_all('a')
            titles_and_urls = [extract_title_and_url_from_bslink(i) for i in inline_links]
            plaintext_urls = extract_plaintext_urls_from_text(remove_text_formatting_and_links_from_fragments(fragment))

            for title, url, base_tags in titles_and_urls:
                tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
                tags.update(base_tags)
                tags.add('in intro')
                tagged_urls.append(tagging.make_tagged_url(url, title, tags))

            for url in plaintext_urls:
                tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
                tags.add('in intro')
                tags.add('plaintext')
                tagged_urls.append(tagging.make_tagged_url(url, url, tags))
            return tagged_urls

        if len(intro_box.find("h3").contents) > 0:
            fragment = intro_box.find("h3").contents[0]
            tagged_urls = extract_links_from_intro(intro_box.find("h3"))
            intro = remove_text_formatting_markup_from_fragments(fragment, strip_chars='\t\r\n').rstrip()
            return intro, tagged_urls

        if intro_box.find("h3").find_next_sibling("p"):
            fragment = intro_box.find("h3").find_next_sibling("p")
            tagged_urls = extract_links_from_intro(fragment)
            intro = remove_text_formatting_markup_from_fragments(fragment, strip_chars='\t\r\n')
            return intro, tagged_urls

        else:
            return [], []
    else:
        return [], []


def extract_title_and_url_from_bslink(link):
    base_tags = []
    if link.get('href'):
        url = link.get('href')
    else:
        url = constants.GHOST_LINK_URL
        base_tags.append(constants.GHOST_LINK_TAG)

    if link.find('h3'):
        title = link.find('h3').contents[0].strip()
    else:
        if link.contents:
            if len(link.contents) == 1:
                if len(link.contents[0]) > 1:
                    if type(link.contents[0]) is bs4.element.NavigableString:
                        title = link.contents[0].strip()
                    else:
                        title = "__GHOST_LINK__"
                        base_tags.append(constants.GHOST_LINK_TAG)
                else:
                    if link.find("strong") and type(link.find("strong").contents[0]) is bs4.element.NavigableString:
                        title = link.find("strong").contents[0]
                    elif link.find("span") and type(link.find("span").contents[0]) is bs4.element.NavigableString:
                        title = link.find("span").contents[0]
                    else:
                        title = "__GHOST_LINK__"
                        base_tags.append(constants.GHOST_LINK_TAG)
            else:
                for x in link.contents:
                    if len(x) > 1:
                        if type(x) is bs4.element.NavigableString:
                            title = x
                        else:
                            title = "__GHOST_LINK__"
                            base_tags.append(constants.GHOST_LINK_TAG)

                    else:
                        if type(x) is bs4.element.Tag:
                            if x.name == "strong" or x.name == "em" or x.name == "b":
                                title = x.contents[0]

        else:
            title = "__GHOST_LINK__"
            base_tags.append(constants.GHOST_LINK_TAG)

    return title, url, base_tags


def extract_text_content_and_links(soup) :
    tagged_urls = list()
    inline_links = []
    text = list()

    article_body = soup.find(attrs = {"class" : "article-body"})
    text_fragments = article_body.find_all("p")
    other_fragments = article_body.find_all("h2", {"style": "display: inline; font-size: 1em; padding: 0px; margin: 0px;"})
    all_fragments = text_fragments + other_fragments

    if all_fragments:
        for paragraph in text_fragments:
            text.append(u"".join(remove_text_formatting_markup_from_fragments(paragraph)))
            plaintext_urls = extract_plaintext_urls_from_text(remove_text_formatting_and_links_from_fragments(paragraph))
            for url in plaintext_urls:
                tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
                tags.update(['plaintext', 'in text'])
                tagged_urls.append(tagging.make_tagged_url(url, url, tags))

    else:
        text = u""

    for p in all_fragments:
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


def extract_embedded_media_from_top_box(container, site_netloc, site_internal_sites):
    # It might be a Kewego video
    if container.find(attrs={'class': 'emvideo emvideo-video emvideo-kewego'}):
        kplayer = container.find(attrs={'class': 'emvideo emvideo-video emvideo-kewego'})
        url_part1 = kplayer.object['data']
        url_part2 = kplayer.object.find('param', {'name': 'flashVars'})['value']
        if url_part1 is not None and url_part2 is not None:
            url = "%s?%s" % (url_part1, url_part2)
            all_tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            if kplayer.next_sibling:
                if len(kplayer.next_sibling) > 0 and kplayer.next_sibling.name == 'figcaption':
                    title = kplayer.next_sibling.contents[0]
                    all_tags = tagging.classify_and_tag(url, site_netloc, site_internal_sites)
                    tagged_url = tagging.make_tagged_url(url, title, all_tags | set(['embedded', 'top box', 'kplayer', 'video']))
                    return tagged_url

                else:
                    title = "__NO_TITLE__"
                    all_tags = tagging.classify_and_tag(url, site_netloc, site_internal_sites)
                    tagged_url = tagging.make_tagged_url(url, title, all_tags | set(['embedded', 'top box', 'kplayer', 'video']))
                    return tagged_url
            else:
                title = "__NO_TITLE__"
                all_tags = tagging.classify_and_tag(url, site_netloc, site_internal_sites)
                tagged_url = tagging.make_tagged_url(url, title, all_tags | set(['embedded', 'top box', 'kplayer', 'video']))
                return tagged_url
        else:
            raise ValueError("We couldn't find an URL in the flash player. Update the parser.")

    # it might be a dailymotion or ustream video or an embedded storify
    elif container.find(attrs={'class': 'emvideo emvideo-video emvideo-embedly'}):
        if container.find("param", {'name': 'movie'}):
            if container.find("param").get("value"):
                if container.find("param", {"name": "movie"}).get("value").startswith("http://www.ustream.tv"):
                    tagged_url = tagging.make_tagged_url(constants.NO_URL, constants.NO_TITLE, set(['embedded', 'video', constants.UNFINISHED_TAG]))
                    return tagged_url

        elif container.find("iframe"):
            url = container.find("iframe").get("src")
            if url:
                all_tags = tagging.classify_and_tag(url, site_netloc, site_internal_sites)
                tagged_url = tagging.make_tagged_url(url, url, all_tags | set(['embedded', 'top box', 'video']))
                return tagged_url
            else:
                raise ValueError("There seems to be a Dailymotion player but we couldn't find an URL. Update the parser.")

        elif len(container.find(attrs={'class': 'emvideo emvideo-video emvideo-embedly'}).contents) == 0:
            # this is to check if the div is not just empty...
            return None

        elif container.find("script"):
            if container.find("script").get("src").startswith("http://storify.com"):
                url = container.find("script").get("src").rstrip(".sjs")
                all_tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
                tagged_url = tagging.make_tagged_url(url, url, all_tags | set(['embedded', 'storify']))
                return tagged_url
            else:
                "Looks like a script but not something we know"


        else:
            raise ValueError("There's an embedded video that does not match known patterns")

    elif container.find(attrs={'class': 'emvideo emvideo-video emvideo-youtube'}):
        youtube_player = container.find(attrs={'class': 'emvideo emvideo-video emvideo-youtube'})
        url = youtube_player.find("a").get("href")
        if url:
            all_tags = tagging.classify_and_tag(url, site_netloc, site_internal_sites)
            tagged_url = tagging.make_tagged_url(url, url, all_tags | set(['embedded', 'top box', 'video']))
            return tagged_url

        else:
            raise ValueError("There seems to be a Youtube player but we couldn't find an URL. Update the parser.")

    # RTL videos
    elif container.find(attrs={'class': "emvideo emvideo-video emvideo-videortl"}):
        url = container.find("iframe").get("src")
        if url:
            all_tags = tagging.classify_and_tag(url, site_netloc, site_internal_sites)
            tagged_url = tagging.make_tagged_url(url, url, all_tags | set(['embedded', 'top box', 'video']))
            return tagged_url
        else:
            raise ValueError("There seems to be a RTL video but it doesn't match known patterns")

    elif container.find("iframe"):
        url = container.find("iframe").get("src")
        if url:
            all_tags = tagging.classify_and_tag(url, site_netloc, site_internal_sites)
            tagged_url = tagging.make_tagged_url(url, url, all_tags | set(['embedded', 'top box', 'iframe']))
            return tagged_url
        else:
            raise ValueError("There seems to be an iframe but it doesn't match known patterns")

    # we want to avoid images
    elif container.find("img") or container.find("figcaption", {"class": "photo"}):
        return None


    # if it's not a known case maybe we can still detect something:
    elif container.find("embed"):
        url = container.find("embed").get("src")
        if url:
            all_tags = tagging.classify_and_tag(url, site_netloc, site_internal_sites)
            tagged_url = tagging.make_tagged_url(url, title, all_tags | set(['embedded', 'top box']))
            return tagged_url

        else:
            raise ValueError("There to be an embedded object but we could not find an link. Update the parser.")

    elif len(container.find("a")) == 0:
        #to detect empty containers
        return None
    else:
        raise ValueError("Unknown type of embedded media")


def extract_links_to_embedded_content(soup):
    if soup.find(attrs={'class': 'block-slidepic media'}):
        top_box = soup.find(attrs={'class': 'block-slidepic media'}).find_all("figure")
        embedded_links = list()
        for container in top_box:
            tagged_url = extract_embedded_media_from_top_box(container, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            if tagged_url is not None:
                embedded_links.append(tagged_url)
        return embedded_links
    else:
        return []


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
    story = soup.find(attrs={'class': 'article-body'})
    scripts = story.findAll('script', recursive=True)
    for script in scripts:
        url = script.get('src')
        if url:
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
            if netloc == "storify.com":
                url = url.rstrip(".js")
                all_tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
                tagged_urls.append(tagging.make_tagged_url(url, url, all_tags | set(['embedded', 'storify'])))
    return tagged_urls


IS_PHOTOALBUM = 1
IS_POLL = 2
IS_ARTICLE = 3


def filter_articles_from_photoalbums_and_polls(url):
    if "/sondage" in url:
        return IS_POLL
    elif "/gallerie" in url:
        return IS_PHOTOALBUM
    else:
        return IS_ARTICLE


def filter_news_items(frontpage_items):
    news_items = list()
    other_stuff = list()
    for title, url in frontpage_items:
        page_type = filter_articles_from_photoalbums_and_polls(url)
        if page_type == IS_ARTICLE:
            news_items.append((title, url))
        else:
            other_stuff.append((title, url))
    return news_items, other_stuff


def extract_article_data(source):

    if hasattr(source, 'read'):
        html_data = source.read()
    else:
        try:
            source = convert_utf8_url_to_ascii(source)
            html_data = fetch_html_content(source)
        except HTTPError as e:
            if e.code == 404 or e.code == 403:
                return None, None
            else:
                raise
        except Exception:
            raise

    soup = bs4.BeautifulSoup(html_data)

    # this is how we detect paywalled articles
    if soup.find(attrs={"id": "main-content"}).h2 and soup.find(attrs={"id": "main-content"}).h2.find(attrs={'class': 'ir locked'}):
        title = extract_title(soup)
        return (ArticleData(source, title, constants.NO_DATE, constants.NO_TIME, datetime.today(), [], [constants.NO_CATEGORY_NAME], None, None, constants.PAYWALLED_CONTENT), html_data)

    else:
        title = extract_title(soup)
        author_name = extract_author_name(soup)
        intro, links_from_intro = extract_intro(soup)
        text, tagged_urls_intext = extract_text_content_and_links(soup)
        category = extract_category(soup)
        sidebar_links = extract_links_from_sidebar_box(soup)
        article_tags = extract_article_tags(soup)
        embedded_media_from_top_box = extract_links_to_embedded_content(soup)
        embedded_media_from_bottom = extract_embedded_media_from_bottom(soup)
        embedded_media_in_article = extract_embedded_media_in_article(soup)
        embedded_media = embedded_media_from_top_box + embedded_media_from_bottom + embedded_media_in_article
        all_links = tagged_urls_intext + sidebar_links + article_tags + embedded_media + links_from_intro
        pub_date, pub_time = extract_date_and_time(soup)
        fetched_datetime = datetime.today()

        updated_tagged_urls = tagging.update_tagged_urls(all_links, rossel_utils.LESOIR_SAME_OWNER)

        # print generate_test_func('embedded_storify_top_box', 'lesoir_new', dict(tagged_urls=updated_tagged_urls))
        # save_sample_data_file(html_data, source, 'embedded_storify_top_box', '/Users/judemaey/code/csxj-crawler/tests/datasources/test_data/lesoir_new')

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
    urls = ["file://localhost/Users/judemaey/code/csxj-crawler/tests/datasources/test_data/lesoir_new/embedded_dailymotion_video.html",
            "http://www.lesoir.be/187412/article/debats/chats/2013-02-11/11h02-%C2%ABil-est-temps-d%C3%A9finir-notre-politique-%C3%A9nerg%C3%A9tique%C2%BB"
            "http://www.lesoir.be/191397/article/culture/cinema/2013-02-16/l%E2%80%99ours-d%E2%80%99or-d%C3%A9cern%C3%A9-au-drame-roumain-%C2%ABchild%E2%80%99s-pose%C2%BB",
            "http://www.lesoir.be/200886/article/actualite/belgique/2013-03-02/didier-reynders-veut-mettre-imams-sous-contr%C3%B4le",
            "http://www.lesoir.be/200800/article/sports/football/2013-03-02/coupe-genk-anderlecht-1-0-apr%C3%A8s-prolongations-direct",
            "http://www.lesoir.be/200395/article/actualite/quiz/2013-03-01/quiz-actu-chiffr%C3%A9-semaine",
            "http://www.lesoir.be/200851/article/actualite/belgique/2013-03-02/budget-pour-andr%C3%A9-antoine-%C2%AB-bons-comptes-font-bons-amis-%C2%BB",
            "http://www.lesoir.be/200881/article/actualite/regions/bruxelles/2013-03-02/philippe-moureaux-%C2%ABa-pourtant-temps-pour-une-s%C3%A9rieuse-psychanalyse%C2%BB",
            "http://www.lesoir.be/95589/article/sports/football/2012-10-08/diables-rouges-mboyo-surprise-wilmots",
            "http://www.lesoir.be/95700/article/actualite/monde/2012-10-08/gr%C3%A8ce-doit-%C3%AAtre-plus-convaincante",
            "http://www.lesoir.be/96047/article/sports/football/2012-10-09/diables-fellaini-touch\u00e9-au-genou",
            "http://www.lesoir.be/96047/article/sports/football/2012-10-09/diables-fellaini-ne-jouera-pas-contre-serbie",
            "http://www.lesoir.be/95589/article/sports/football/2012-10-08/diables-rouges-mboyo-surprise-wilmots",
            "http://www.lesoir.be/96818/article/sports/football/2012-10-10/diables-rouges-kompany-\u00ab-90-chances-jouer-\u00bb",
            "http://www.lesoir.be/97581/article/debats/chats/2012-10-11/communales-dernier-d%C3%A9bat-tillieux-pr%C3%A9vot",
            "http://www.lesoir.be/160924/article/actualite/belgique/2013-01-14/bon-plan-anti-crise-repas-gratuit-au-\u00ab-bar-\u00e0-soupe-\u00bb",
            "http://www.lesoir.be/121653/article/actualite/belgique/2012-11-16/jean-denis-lejeune-rencontr\u00e9-michelle-martin",
            "http://www.lesoir.be/101568/article/actualite/belgique/2012-10-18/michelle-martin-autoris\u00e9e-\u00e0-rencontrer-jean-denis-lejeune",
            "http://www.lesoir.be/134309/article/actualite/monde/2012-12-07/que-faire-jour-fin-du-monde",
            "http://www.lesoir.be/186293/article/styles/air-du-temps/2013-02-08/votre-week-end-en-15-clics",
            "http://www.lesoir.be/127339/article/styles/air-du-temps/2012-11-26/carla-bruni-\u00ab-ma-g\u00e9n\u00e9ration-n-pas-besoin-du-f\u00e9minisme-\u00bb",
            "http://www.lesoir.be/189598/article/economie/2013-02-14/karel-gucht-\u00ab-deux-ans-pour-r\u00e9ussir-\u00bb",
            ]

    urls_from_errors = ["http://www.lesoir.be/165044/article/geeko/2013-01-15/que-va-annoncer-facebook-suivre-en-direct",
                        "http://www.lesoir.be/165044/article/geeko/2013-01-15/facebook-lance-un-moteur-recherche-en-direct",
                        "http://www.lesoir.be/165044/article/geeko/2013-01-15/facebook-lance-un-moteur-recherche",
                        "http://www.lesoir.be/171006/article/sports/football/2013-01-24/erwin-leemens-nouvel-entra\u00eeneur-des-gardiens",
                        "http://www.lesoir.be/171006/article/sports/football/2013-01-24/erwin-lemmens-nouvel-entra\u00eeneur-des-gardiens-des-diables",
                        "http://www.lesoir.be/186293/article/styles/air-du-temps/2013-02-08/votre-week-end-en-15-clics",
                        "http://www.lesoir.be/134309/article/actualite/monde/2012-12-07/que-faire-jour-fin-du-monde"
                        ]

    for url in urls[-1:]:
        print url
        article, html = extract_article_data(url)
        print "this one was ok"
        article.print_summary()
        print article.to_json()

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
