#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import datetime as dt
import time
from itertools import chain

from scrapy.selector import HtmlXPathSelector
import bs4

from parser_tools import utils
from parser_tools import twitter_utils
from csxj.common import tagging
from csxj.db.article import ArticleData


SOURCE_TITLE = u"7 sur 7"
SOURCE_NAME = u"septsursept"


SEPTSURSEPT_NETLOC = "www.7sur7.be"
SEPTSURSEPT_INTERNAL_SITES = {}

SEPTSURSEPT_SAME_OWNER = [
    'regiojobs.be',
    'vkbanen.nl',
    'vacature.com',
    'jobscareer.be',
    'werkendichtbij.nl',
    'autozone.be',
    'echo.be',
    'hln.be',
    'parool.nl',
    'ad.nl',
    'trouw.nl',
    'volkskrant.nl',
    'demorgen.be',
    'tijd.be',
    'nina.be',
    'goedgevoel.be'
]


def make_full_url(item):
    title, url = item
    if not url.startswith("http"):
        return title, "http://{0}{1}".format(SEPTSURSEPT_NETLOC, url)
    else:
        return title, url


def extract_title_and_url(link_selector):
    url = link_selector.select("./@href").extract()[0]
    title = link_selector.select("./text()").extract()[0].strip()
    return title, url


def separate_articles_and_photoalbums(frontpage_items):
    def is_junk(frontpage_item):
        title, url = frontpage_item
        return ("/photoalbum/" in url) or ('/video/' in url)

    photoalbum_items = [item for item in frontpage_items if is_junk(item)]
    article_items = [l for l in frontpage_items if l not in photoalbum_items]
    return article_items, photoalbum_items


def try_extract_frontpage_items(url):

    html_data = urllib.urlopen(url).read()
    hxs = HtmlXPathSelector(text=html_data)

    # get all the stories from the left column
    first_story = hxs.select("//section//article/h1/a")
    main_stories = hxs.select("//section//article/h3/a")

    #this news site is terrible. really.
    random_crap_stories = hxs.select("//section//section [starts-with(@class, 'tn_you')]//li/h3/a")
    more_crap_stories = hxs.select("//section//section [starts-with(@class, 'tn_hln')]//li/h3/a")

    all_left_stories = chain(first_story, main_stories, random_crap_stories, more_crap_stories)
    left_items = [extract_title_and_url(link_hxs) for link_hxs in all_left_stories]

    # get all the stories from the right column
    all_side_stories = hxs.select("//section [@class='str_aside_cntr']//h3/a")
    stories_to_remove = hxs.select("//section [@class='str_aside_cntr']//section [starts-with(@class, 'teas_article_306')]//li/h3/a")

    right_items = set([extract_title_and_url(link_hxs) for link_hxs in all_side_stories])
    to_remove = set([extract_title_and_url(link_hxs) for link_hxs in stories_to_remove])

    right_items = list(right_items - to_remove)

    frontpage_items = left_items + right_items
    article_links, photoalbum_links = separate_articles_and_photoalbums(frontpage_items)
    return [make_full_url(item) for item in article_links], [make_full_url(item) for item in photoalbum_links]


def get_frontpage_toc():
    return try_extract_frontpage_items("http://www.7sur7.be/")


def extract_title(soup):
    # trouver le titre
    # la méthode avec "articleDetailTitle" ne marche pas tout le temps
    #title_box = soup.find(attrs = {"id" : "articleDetailTitle"})
    title_box = soup.find(attrs={"class": "k1 mrg"})
    title = title_box.contents[0]

    return title


def extract_author_name(author_box):
    # parfois le nom de l'auteur est dans un lien
    author_link = author_box.find_all('a', recursive = False)
    if author_link :
        author_name = author_link[0].contents[0]

    else :
    # quand le nom n'est pas dans un lien, je prends le premier élément de la author_box
        author_name = author_box.contents[0]
        # nettoyer les retours à la ligne inutiles
        author_name = author_name.strip("\n")

    return author_name


def extract_date_and_time(author_box):
    # une fonction utile
    def make_time_from_string(time_string):
        """
        Takes a HH:MM string, returns a time object
        """
        h, m = [int(i) for i in time_string.split('h')]
        return dt.time(h, m)

    # la date et l'heure sont dans le dernier élément de la author_box
    date_string = author_box.contents[-1]

    # parfois, la source est mentionnée
    if "Source" in date_string :
        date_string = date_string.split("Source")[0]

    date_and_time = date_string.split("-")

    # nettoyer les espaces et les retours à la ligne autour de la date
    date_clean = date_and_time[0].strip("\n ")

    pub_date = dt.datetime.strptime(date_clean, '%d/%m/%y').date()
    pub_time = make_time_from_string(date_and_time[1])

    return pub_date, pub_time


def extract_source(author_box):
    if "Source" in author_box.contents[-1]:
        source = author_box.contents[-1].split("Source: ")[-1]
        source = source.strip("\n ")

    else:
        source = None
    return source

def extract_intro(soup):
    intro_box = soup.find(attrs = {"class" : "intro"})
    tagged_urls = []

    if intro_box:
        intro_fragments = intro_box.find_all('b')
        intro = utils.remove_text_formatting_markup_from_fragments(intro_fragments)
        inline_links = intro_box.find_all("a")
        titles_and_urls = [extract_title_and_url_from_bslink(i) for i in inline_links]
        plaintext_urls = utils.extract_plaintext_urls_from_text(intro)

        for title, url, base_tags in titles_and_urls:
            tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
            tags.update(base_tags)
            tags.add('in intro')
            tagged_urls.append(tagging.make_tagged_url(url, title, tags))

        for url in plaintext_urls:
            tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
            tags.add('in intro')
            tags.add('plaintext')
            tagged_urls.append(tagging.make_tagged_url(url, url, tags))
    else:
        intro = ""

    return intro, tagged_urls


def extract_text_content_and_links(soup) :
    article_text = []
    inline_links = []

    content_box = soup.find(attrs = {"id" : "detail_content"})
    text = content_box.find_all(attrs = {"class":"clear"})
    for fragment in text :
        paragraphs = fragment.find_all("p", recursive=False)
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
        tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
        tags.update(base_tags)
        tags.add('in text')
        tagged_urls.append(tagging.make_tagged_url(url, title, tags))

    for url in plaintext_urls:
        tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
        tags.add('in text')
        tags.add('plaintext')
        tagged_urls.append(tagging.make_tagged_url(url, url, tags))

    return article_text, tagged_urls


def extract_links_from_read_more_box(soup):
    if soup.find(attrs = {"class" : "read_more"}) :
        read_more_box = soup.find(attrs = {"class" : "read_more"})
        if read_more_box.find('h4'):
            links = read_more_box.find_all("a")
            titles_and_urls = [extract_title_and_url_from_bslink(link) for link in links if not link.find("img")]
            tagged_urls = list()
            for title, url, base_tags in titles_and_urls:
                tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
                tags.update(base_tags)
                tags.add('bottom box')
                tagged_urls.append(tagging.make_tagged_url(url, title, tags))
            return tagged_urls
        else:
            return []
    else:
        return []

def extract_links_from_sidebar_box(soup):
    tagged_urls = list()
    sidebar_box = soup.find(attrs = {"class" : "teas_article_306 mar10 clear clearfix relatedcomponents"})
    # there are links to articles
    if sidebar_box :
        sidebar_box.find_all(attrs = {"class" : "clearfix"})
        articles = sidebar_box.find_all(attrs = {"class" : "clearfix"})
        links = articles[0].find_all("a")
        titles_and_urls = [extract_title_and_url_from_bslink(link) for link in links]
        for title, url, base_tags in titles_and_urls:
            tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
            tags.update(base_tags)
            tags.add('sidebar box')
            tagged_urls.append(tagging.make_tagged_url(url, title, tags))

        # and also links to thematic tags
        tags = sidebar_box.find_all(attrs = {"class" : "bt_meer_over clearfix"})
        for tag in tags:
            links = tag.find_all("a")
            titles_and_urls = [extract_title_and_url_from_bslink(link) for link in links]
            for title, url, base_tags in titles_and_urls:
                tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
                tags.update(base_tags)
                tags.add('keyword')
                tags.add('sidebar box')
                tagged_urls.append(tagging.make_tagged_url(url, title, tags))

    return tagged_urls

def extract_title_and_url_from_bslink(link):
    base_tags = []
    if link.get('href'):
        url = link.get('href')
    else :
        url = "__GHOST_LINK__"
        base_tags.append("ghost link")

    if link.find('h3'):
        title = link.find('h3').contents[0].strip()

    elif link.find('strong'):
        title = link.find('strong').contents[0].strip()
    else:
        if link.contents:
            if type(link.contents[0]) is bs4.element.NavigableString:
                title = link.contents[0].strip()
            elif type(link.contents[-1]) is bs4.element.NavigableString :
                title = link.contents[-1].strip()
            else :
                title = "__GHOST_LINK__"
        else:
            title = "__GHOST_LINK__"
            base_tags.append("ghost link")

    return title, url, base_tags

def extract_category(soup):
    category_box = soup.find(attrs = {"class" : "actua_nav"})
    links = category_box.find_all('a')
    return [utils.remove_text_formatting_markup_from_fragments(link.contents[0]) for link in links]

def find_embedded_media_in_multimedia_box(multimedia_box):
    tagged_urls = list()
    all_sections = multimedia_box.findAll("section")
    for section in all_sections:

        if 'photo' in section.attrs['class']:
            continue

        elif 'poll' in section.attrs['class']:
            continue

        elif 'asset' in section.attrs['class']:
            url = section.find('a').get('href')
            title = section.find('a').contents
            tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
            tags.add('embedded')
            tagged_urls.append(tagging.make_tagged_url(url, title, tags))

        elif 'video' in section.attrs['class']:
            # it might be an iframe
            if section.find("iframe"):
                iframe = section.find("iframe")
                url = iframe.get("src")
                if url :
                    tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
                    tags.add('embedded')
                    tagged_urls.append(tagging.make_tagged_url(url, url, tags))
                else:
                    raise ValueError("There seems to be an iframe but we could not find a link. Please update parser.")

            elif section.find("embed"):
                embedded_stuff = section.find("embed")
                url = embedded_stuff.get("src")
                if url :
                    tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
                    tags.add('embedded')
                    tagged_urls.append(tagging.make_tagged_url(url, url, tags))
                else:
                    raise ValueError("There seems to be an embedded video but we could not find a link. Please update parser.")
            else :
                raise ValueError("There seems to be an embedded video but we could not identify it. Please update parser.")


        elif 'snippet' in section.attrs['class']:

            # it might be a tweet
            tweets = section.find_all(attrs = {"class" : "twitter-tweet"})
            if tweets:
                for tweet in tweets:
                    links = tweet.find_all("a")
                    for link in links :
                        if link.get("data-datetime"):
                            url = link.get("href")
                            tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
                            tags.add('embedded')
                            tags.add('tweet')
                            tagged_urls.append(tagging.make_tagged_url(url, url, tags))

            # it might be an embedded javascript object that shows a twitter account or query
            twitter_widget = section.find_all(attrs = {"class" : "tweet_widget"})
            if twitter_widget:
                if len(twitter_widget) ==1:
                    if twitter_widget[0].find('script'):
                        script_url = twitter_widget[0].find('script').get('src')
                        if twitter_utils.is_twitter_widget_url(script_url):
                            title, url, tags = twitter_utils.get_widget_type(twitter_widget[0].findAll('script')[1].contents[0])
                            tags |= tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
                            tags |= set(['script', 'embedded'])
                            tagged_urls.append(tagging.make_tagged_url(url, title, tags))

                    elif section.find("script"):
                        script_url = section.find('script').get('src')
                        if twitter_utils.is_twitter_widget_url(script_url):
                            title, url, tags = twitter_utils.get_widget_type(section.findAll('script')[1].contents[0])
                            tags |= tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
                            tags |= set(['script', 'embedded'])
                            tagged_urls.append(tagging.make_tagged_url(url, title, tags))
                        else:
                            raise ValueError("Embedded script of unknown type was detected ('{0}'). Update the parser.".format(script_url))

                    elif twitter_widget[0].find('noscript'):
                        noscript = twitter_widget[0].find('noscript')
                        link = noscript.find('a')
                        if link:
                            url = link.get('href')
                            title = remove_text_formatting_markup_from_fragments(link.contents)
                            all_tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
                            all_tags |= set(['script', 'embedded'])
                            tagged_urls.append(tagging.make_tagged_url(url, title, all_tags))
                        else:
                            raise ValueError("No link was found in the <noscript> section. Update the parser.")

                    else:
                        raise ValueError("Could not extract fallback noscript url for this embedded javascript object. Update the parser.")
                else :
                    raise ValueError("There seems to be more than one embedded twitter wdget in the SNIPPET, check this")

            # it might be a spotify container
            spotify_widget = section.find(attrs = {"class" : "spotify"})
            if spotify_widget:
                if spotify_widget.find("iframe").get("src"):
                    url = spotify_widget.find("iframe").get("src")
                    all_tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
                    all_tags |= set(['spotify', 'embedded'])
                    tagged_urls.append(tagging.make_tagged_url(url, url, all_tags))
                else :
                    raise ValueError("There seems to be a spotify widget but we could not find a link")

        else:
            raise ValueError("There seems to be an undefined embedded media here, you should check")

    return tagged_urls

def extract_embedded_media(soup):
    tagged_urls = list()

    # extract embedded media from any iframe in the article body
    content_box = soup.find(attrs = {"id" : "detail_content"})
    text = content_box.find_all(attrs = {"class":"clear"})
    for fragment in text :
        for p in fragment.find_all("p", recursive=False):
            embedded_container = p.findAll("iframe")
            for x in embedded_container:
                url = x.get("src")
                tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
                tags.add('embedded')
                tags.add ('in text')
                tagged_urls.append(tagging.make_tagged_url(url, url, tags))

    # some embedded media are not in the artucle body, but embedded in the art_aside container
    art_aside = soup.find(attrs = {"class" : "art_aside"})
    if art_aside:
        tagged_urls.extend(find_embedded_media_in_multimedia_box(art_aside))

    # same, but in the art_bottom container
    art_bottom = soup.find(attrs = {"class" : "art_bottom"})
    if art_bottom:
        tagged_urls.extend(find_embedded_media_in_multimedia_box(art_bottom))

    return tagged_urls


# une fonction qui vérifie si l'url renvoie en fait vers la frontpage
IS_FRONTPAGE = 1
IS_ARTICLE = 2
MAYBE_ARTICLE = 3

def detect_page_type(url):
    current_item_count = len(try_extract_frontpage_items(url)[0])
    frontpage_item_count  = len(get_frontpage_toc()[0])
    if current_item_count == 0 :
        return IS_ARTICLE
    elif float(current_item_count) / frontpage_item_count < 0.8:
        return MAYBE_ARTICLE
    else :
        return IS_FRONTPAGE


SEPTSURSEPT_404_PAGE_CONTENT = """
<html>
 <head>
  <script language="JavaScript">
   function goToURL()
{
 parent.location = "http://www.7sur7.be/404";
}
  </script>
 </head>
 <body onload="goToURL()">
  <!-- MEDUSA -->
 </body>"""

def is_404_page(html_data):
    stripped_html_data = html_data.translate(None, ' \n\t')
    stripped_404 = SEPTSURSEPT_404_PAGE_CONTENT.translate(None, ' \n\t')
    return stripped_404.lower() == stripped_html_data.lower()


def extract_article_data(source):
    # url is either a file-like object, or a url.
    # if it's a file we just open it, assume it's an article and extract article data

    if hasattr(source, 'read'):
        html_data = source.read()
    # if it's an url we need to check if it's a photo album, a link to the frontpage or a true article
    else:
        html_data = utils.fetch_html_content(source)

        page_type = detect_page_type(source)
        if page_type == IS_FRONTPAGE:
            return None, None
        elif page_type == MAYBE_ARTICLE:
            raise ValueError("We couldn't define if this was an article or the frontpage, please check")

    if is_404_page(html_data):
        return (None, html_data)

    # pour tous les autres vrais articles
    soup  = bs4.BeautifulSoup(html_data)


    if soup.find("head").find("title").contents[0] == "301 Moved Permanently":
          return (None, html_data)

    else :

        title = extract_title(soup)

        author_box = soup.find(attrs = {"class" : "author"})
        author_name = extract_author_name(author_box)
        pub_date, pub_time = extract_date_and_time(author_box)

        # original_source = extract_source(author_box)

        intro, tagged_urls_from_intro = extract_intro(soup)

        category = extract_category(soup)

        text, tagged_urls_intext = extract_text_content_and_links(soup)

        tagged_urls_read_more_box = extract_links_from_read_more_box(soup)

        tagged_urls_sidebar_box = extract_links_from_sidebar_box(soup)

        tagged_urls_embedded_media = extract_embedded_media(soup)

        tagged_urls = tagged_urls_intext + tagged_urls_read_more_box + tagged_urls_sidebar_box + tagged_urls_embedded_media + tagged_urls_from_intro

        updated_tagged_urls = tagging.update_tagged_urls(tagged_urls, SEPTSURSEPT_SAME_OWNER)

        return (ArticleData(source, title, pub_date, pub_time, dt.datetime.now(),
                        updated_tagged_urls,
                        category, author_name,
                        intro, text),
            html_data)

# on vérifie que les urls de la frontpage ne renvoient pas vers la frontpage (en y appliquant la fonction qui extrait les urls des la frontpage!!)
def show_frontpage():
    frontpage_items, blogposts = get_frontpage_toc()

    print "NEWS ({0}):".format(len(frontpage_items))
    for title, url in frontpage_items:
        x, y = try_extract_frontpage_items(url)
        if len(x) > 0:
            print u"{0} \t\t [{1}]".format(title, url)
            print len(x)



if __name__ == '__main__':
    url1 = "http://www.7sur7.be/7s7/fr/1504/Insolite/article/detail/1494529/2012/09/02/Ils-passent-devant-une-vitrine-avant-de-disparaitre.dhtml"
    url2 = "http://www.7sur7.be/7s7/fr/1504/Insolite/article/detail/1491869/2012/08/27/Fin-des-recherches-apres-une-alerte-au-lion-pres-de-Londres.dhtml"
    url3 = "http://www.7sur7.be/7s7/fr/1505/Monde/article/detail/1494515/2012/09/02/Obama-et-Romney-a-egalite-dans-les-sondages.dhtml"
    url6 = "http://www.7sur7.be/7s7/fr/1757/Dopage-dans-le-cyclisme/article/detail/1514991/2012/10/11/Armstrong-est-un-grand-champion-point-final.dhtml"
    url7 = "http://www.7sur7.be/7s7/fr/1505/Monde/article/detail/1520913/2012/10/21/Une-premiere-Amerindienne-canonisee.dhtml"
    url9 = "http://www.7sur7.be/7s7/fr/1502/Belgique/article/detail/1520790/2012/10/20/Le-pacte-de-solidarite-signe-par-Onkelinx-tres-critique.dhtml"
    url10 = "http://www.7sur7.be/7s7/fr/1509/Football-Belge/article/detail/1520820/2012/10/20/Une-raclee-pour-Bruges-un-exploit-pour-Charleroi.dhtml"
    url11 = "http://www.7sur7.be/7s7/fr/1505/Monde/article/detail/1528304/2012/11/04/La-Marche-russe-des-ultra-nationalistes-reclame-le-depart-de-Poutine.dhtml"
    url12 = "http://www.7sur7.be/7s7/fr/1505/Monde/article/detail/1528304/2012/11/04/La-Marche-russe-des-ultra-nationalistes-reclame-le-depart-de-Poutine.dhtml"
    url14 = "http://www.7sur7.be/7s7/fr/1527/People/article/detail/1527428/2012/11/02/La-robe-interactive-de-Nicole-Scherzinger.dhtml"
    url15 = "http://www.7sur7.be/7s7/fr/1504/Insolite/article/detail/1501041/2012/09/14/Une-traversee-des-Etats-Unis-avec-du-bacon-comme-seule-monnaie.dhtml"
    urls = [url1, url2, url3, url6, url7, url9, url10, url11, url12, url14, url15]

    # for url in urls:
    #     print url
    #     article_data, html = extract_article_data(url)
    #     for link in article_data.links:
    #         print link
    #     print article_data.title
    #     print article_data.intro
    #     print len(article_data.links)


    # from pprint import pprint
    # import json
    # f = open("/Users/judemaey/code/csxj-crawler/sample_data/septsursept/it_breaks.json")
    # urls = json.load(f)
    # for x in urls[u'articles']:
    #     url = x[1]
    #     article_data, html = extract_article_data(url)
    #     print url
    #     print article_data.to_json()

#    for x in urls:
#        for y in x[1]:
#            url = y[1]
#            article_data, html = extract_article_data(url)
#            print article_data.title
#            print article_data.url
#            pprint(article_data.links)
#            print len(article_data.links)
#            print "\n"
#            print "******************************"
#            print "\n"

    # total_time = 0.0
    # for url in urls[:]:
    #     before = dt.datetime.now()
    #     article_data, html = extract_article_data(url)
    #     elapsed = dt.datetime.now() - before
    #     total_time += elapsed.seconds
    #     print article_data.title
    #     print article_data.url
    #     pprint(article_data.links)
    #     print len(article_data.links)
    #     print article_data.pub_date
    #     print article_data.to_json()

    # avg = total_time / len(urls)
    # print "total time for {0} articles: {1}".format(len(urls), total_time)
    # print "avg time per article: {0}".format(avg)
    # projected_article_count = 50000
    # projected_time = avg * projected_article_count
    # print "Projection for {0} articles:".format(projected_article_count), time.strftime("%H:%M:%S", time.gmtime(projected_time))


    # articles, photos = get_frontpage_toc()
    # for item in articles:
    #     title, url = item
    #     print url
    #     article_data, html = extract_article_data(url)
    #     if article_data:
    #         print article_data.title
    #         print len(article_data.links)

    url = "http://www.7sur7.be/7s7/fr/1502/Belgique/article/detail/1500307/2012/09/13/Si-tu-me-mets-une-contravention-je-tire.dhtml"
    # url = "http://www.7sur7.be/7s7/fr/1510/Football-Etranger/article/detail/1554304/2012/12/27/Vincent-Kompany-dans-le-onze-ideal-du-journal-l-Equipe.dhtml"
    # url = "http://www.7sur7.be/7s7/fr/1528/Cinema/article/detail/1403291/2012/03/03/Julie-Arnold-Gerard-Rinaldi-etait-un-etre-exceptionnel.dhtml"
    # url = "http://7sur7.be/7s7/fr/1536/Economie/article/detail/1403430/2012/03/03/Manifestations-contre-les-abus-bancaires-en-Espagne.dhtml"
    # url = "http://7sur7.be/7s7/fr/1510/Football-Etranger/article/detail/1403137/2012/03/02/Blatter-appelle-a-adopter-la-technologie-sur-la-ligne-de-but.dhtml"
    # url = "http://7sur7.be/7s7/fr/1504/Insolite/article/detail/1403964/2012/03/05/Le-pire-cauchemar-d-une-mariee-devenu-realite.dhtml"
    # url = "http://7sur7.be/7s7/fr/1540/TV/article/detail/1408003/2012/03/13/Demande-en-mariage-sur-le-plateau-d-Une-Famille-en-or.dhtml"
    # url = "http://7sur7.be/7s7/fr/1759/Bundesliga/article/detail/1410425/2012/03/18/Le-sang-froid-d-Igor-De-Camargo-devant-le-but.dhtml"
    # url = "http://7sur7.be/7s7/fr/1762/Premier-League/article/detail/1410549/2012/03/18/Torres-retrouve-le-chemin-du-but.dhtml"
    # url = "http://7sur7.be/7s7/fr/1759/Bundesliga/article/detail/1410425/2012/03/18/Le-sang-froid-d-Igor-De-Camargo-devant-le-but.dhtml"
    # url = "http://7sur7.be/7s7/fr/1745/Standard/article/detail/1403891/2012/03/05/Le-Standard-n-est-toujours-pas-assure-de-jouer-les-Playoffs.dhtml"
    # url = "http://7sur7.be/7s7/fr/1525/Tendances/article/detail/1403993/2012/03/05/Le-harnais-etrange-accessoire-en-vogue.dhtml"
    # url = "http://7sur7.be/7s7/fr/1536/Economie/article/detail/1404580/2012/03/06/Le-Comite-restreint-se-penche-sur-les-recettes.dhtml"
    # url = "http://7sur7.be/7s7/fr/1525/Tendances/article/detail/1405399/2012/03/07/Le-mannequin-aux-grosses-fesses-a-gagne-son-proces.dhtml"
    url = "http://7sur7.be/7s7/fr/1767/Ligue-des-Champions/article/detail/1405471/2012/03/07/Messi-l-extraterrestre.dhtml"
    url = "http://7sur7.be/7s7/fr/1512/Cyclisme/article/detail/1405628/2012/03/08/Mais-que-se-passe-t-il-avec-Philippe-Gilbert.dhtml"
    url = "http://7sur7.be/7s7/fr/1527/People/article/detail/1411055/2012/03/19/M-Pokora-dement-etre-en-couple-avec-Alizee.dhtml"
    url = "http://7sur7.be/7s7/fr/1529/Musique/article/detail/1406607/2012/03/09/Deces-du-chanteur-du-group-disco-des-Trammps.dhtml"
    url = "http://www.7sur7.be/7s7/fr/1504/Insolite/article/detail/1407359/2012/03/12/Les-malheurs-d-un-journaliste-amusent-le-web.dhtml"
    url = "http://7sur7.be/7s7/fr/1527/People/article/detail/1408039/2012/03/13/Premier-apercu-de-la-frimousse-de-Giulia-Sarkozy.dhtml"
    url = "http://www.7sur7.be/7s7/fr/1505/Monde/article/detail/1487322/2012/08/17/La-tumeur-cancereuse-d-Israel-va-bientot-disparaitre.dhtml"
    url_test = "http://www.7sur7.be/7s7/fr/1527/People/article/detail/1452608/2012/06/12/Mathieu-Kassovitz-traite-Nadine-Morano-de-conne.dhtml"
    url = "http://www.7sur7.be/7s7/fr/1527/People/article/detail/1455287/2012/06/17/Lindsay-Lohan-plaisante-sur-son-malaise.dhtml"
    url = "http://www.7sur7.be/7s7/fr/1773/Festivals/article/detail/1486845/2012/08/16/Le-Pukkelpop-revit.dhtml"
    url = "http://www.7sur7.be/7s7/fr/9100/Infos/article/detail/1489178/2012/08/21/Myriam-Leroy-et-Pure-Fm-c-est-fini.dhtml"
    url = "http://www.7sur7.be/7s7/fr/2864/Dossier-Obama/article/detail/1492705/2012/08/29/Michelle-Obama-en-esclave-denudee.dhtml"
    url = "http://7sur7.be/7s7/fr/1536/Economie/article/detail/1404580/2012/03/06/Le-Comite-restreint-se-penche-sur-les-recettes.dhtml"
    url = "http://www.7sur7.be/7s7/fr/2625/Planete/article/detail/1407279/2012/03/12/Un-lundi-au-soleil-pour-l-ouest-et-le-centre.dhtml"
    url = "http://7sur7.be/7s7/fr/1510/Football-Etranger/article/detail/1413456/2012/03/24/Un-jeune-supporter-de-Port-Said-tue-dans-des-heurts-avec-la-police.dhtml"
    url = "http://7sur7.be/7s7/fr/1502/Belgique/article/detail/1411405/2012/03/20/Peine-de-travail-pour-un-double-accident-mortel.dhtml"
    url = open("/Users/judemaey/code/csxj-crawler/sample_data/septsursept/moved_permanently.html")
    url = "http://www.7sur7.be/7s7/fr/1513/tennis/article/detail/1455721/2012/06/18/Les-10-plus-gros-petages-de-plomb-de-l-histoire-du-tennis.dhtml"
    url = "http://www.7sur7.be/7s7/fr/1502/Belgique/article/detail/1426303/2012/04/20/Wesphael-annonce-la-creation-de-son-parti.dhtml"
    url = "http://7sur7.be/7s7/fr/1525/Tendances/article/detail/1415778/2012/03/29/La-lingerie-belge-de-Carine-Gilson-primee.dhtml"
    url = "http://www.7sur7.be/7s7/fr/1502/Belgique/article/detail/1436819/2012/05/11/Comment-etre-un-bon-Flamand-la-brochure-qui-fait-jaser.dhtml"
    url = "http://www.7sur7.be/7s7/fr/1536/Economie/article/detail/1446084/2012/05/30/Ces-grandes-entreprises-belges-qui-ne-paient-pas-d-impots.dhtml"
    url = "http://www.7sur7.be/7s7/fr/1527/People/article/detail/1495469/2012/09/04/Gad-Elmaleh-et-Charlotte-de-Monaco-officialisent-leur-relation.dhtml"
    url = "http://www.7sur7.be/7s7/fr/1509/Football-Belge/article/detail/1504847/2012/09/21/Le-Standard-voit-rouge-Trond-Sollied-sauve-sa-tete.dhtml"
    url = "http://www.7sur7.be/7s7/fr/1509/Football-Belge/article/detail/1507177/2012/09/26/Van-Damme-Pour-moi-ca-reste-une-question-ridicule.dhtml"
    url = "http://www.7sur7.be/7s7/fr/1767/Ligue-des-Champions/article/detail/1510948/2012/10/03/Anderlecht-mange-a-la-sauce-andalouse.dhtml"
    url = "http://www.7sur7.be/7s7/fr/9099/Hors-jeu/article/detail/1536875/2012/11/20/Varane-considere-Bilbao-pour-une-equipe-catalane.dhtml"
    url = "http://www.7sur7.be/7s7/fr/1502/Belgique/article/detail/1513518/2012/10/09/Arret-de-travail-aux-depots-TEC-de-Jemeppe-et-Robermont.dhtml"
    article_data, html = extract_article_data(url_test)
    if article_data:
        for link in article_data.links:
            print link
        print article_data.title
        print article_data.category
        print article_data.intro
        print len(article_data.links)

    # f = open("/Users/judemaey/code/csxj-crawler/sample_data/septsursept/sample_with_plaintext_in_intro.html")
    # article_data, html = extract_article_data(f)
    # for link in article_data.links:
    #     print link









