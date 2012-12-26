#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
from datetime import datetime, time
import sys
from itertools import chain
import urlparse
from scrapy.selector import HtmlXPathSelector
import bs4
from common import utils
from common import twitter_utils
from csxj.common import tagging
from csxj.db.article import ArticleData


SEPTSURSEPT_NETLOC = "www.7sur7.be"
SEPTSURSEPT_INTERNAL_SITES = {}


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
    return [make_full_url(item) for item in frontpage_items], []

def get_frontpage_toc():
    return try_extract_frontpage_items("http://www.7sur7.be/")


def extract_title(soup):
    # trouver le titre
    # la méthode avec "articleDetailTitle" ne marche pas tout le temps
    #title_box = soup.find(attrs = {"id" : "articleDetailTitle"})
    title_box = soup.find(attrs = {"class" : "k1 mrg"})
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
        return time(h, m)

    # la date et l'heure sont dans le dernier élément de la author_box
    date_string = author_box.contents[-1]

    # parfois, la source est mentionnée
    if "Source" in date_string :
        date_string = date_string.split("Source")[0]

    date_and_time = date_string.split("-")

    # nettoyer les espaces et les retours à la ligne autour de la date
    date_clean = date_and_time[0].strip("\n ")

    pub_date = datetime.strptime(date_clean, '%d/%m/%y').date()
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
    if intro_box:
        intro = intro_box.find_all('b')
        intro = intro[0].contents[0]
    else:
        intro = ""
    return intro


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

def extract_links_from_sidebar_box(soup):
    tagged_urls = list()
    sidebar_box = soup.find(attrs = {"class" : "teas_article_306 mar10 clear clearfix relatedcomponents"})
    # there are links to articles
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
            tags.add('article tag')
            tags.add('sidebar box')
            tagged_urls.append(tagging.make_tagged_url(url, title, tags))

    for x in tagged_urls:
        print x

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
    else:
        if link.contents:
            title = link.contents[0].strip()
        else:
            title = "__GHOST_LINK__"
            base_tags.append("ghost link")

    return title, url, base_tags

def extract_category(soup):
    category_box = soup.find(attrs = {"class" : "actua_nav"})
    links = category_box.findAll('a')
    return [utils.remove_text_formatting_markup_from_fragments(link.contents[0]) for link in links]

def find_embedded_media_in_multimedia_box(multimedia_box):
        tagged_urls = list()
        all_sections = multimedia_box.findAll("section")
        for section in all_sections:

            if 'photo' in section.attrs['class']:
                continue

            elif 'video' in section.attrs['class']:
                video = section.find("iframe")
                url = video.get("src")
                tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
                tags.add('embedded media')
                tagged_urls.append(tagging.make_tagged_url(url, url, tags))

            elif 'snippet' in section.attrs['class']:

                # it might be a tweet
                tweets = section.find_all(attrs = {"class" : "twitter-tweet"})
                if tweets:
                    if len(tweets) == 1:
                        links = tweets[0].find_all("a")
                        for link in links :
                            if link.get("data-datetime"):
                                url = link.get("href")
                                tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
                                tags.add('embedded media')
                                tags.add('tweet')
                                tagged_urls.append(tagging.make_tagged_url(url, url, tags))
                    else:
                        raise ValueError("There seems to be more than one embedded tweet in the SNIPPET, check this")  

                # it might be an embedded javascript object that shows a twitter account or query
                twitter_widget = section.find_all(attrs = {"class" : "tweet_widget"})
                if twitter_widget:
                    if len(twitter_widget) ==1:
                        if twitter_widget[0].find('script').get('src'):
                            script_url = twitter_widget[0].find('script').get('src')
                            if twitter_utils.is_twitter_widget_url(script_url):
                                title, url, tags = twitter_utils.get_widget_type(twitter_widget[0].findAll('script')[1].contents[0])
                                tags |= tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
                                tags |= set(['script', 'embedded'])
                                tagged_urls.append(tagging.make_tagged_url(url, title, tags))
                            else:
                                if twitter_widget[0].find('noscript'):
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
                                    raise ValueError("Embedded script of unknown type was detected ('{0}'). Update the parser.".format(script_url))
                        else:
                            raise ValueError("Could not extract fallback noscript url for this embedded javascript object. Update the parser.")

                    else :
                        raise ValueError("There seems to be more than one embedded twitter wdget in the SNIPPET, check this")  

            else:
                raise ValueError("There seems to be an undefined embedded media here, you should check")
      
        return tagged_urls

def extract_embedded_media(soup):
    tagged_urls = list()
    # extract embedded media from any iframe in the article container
    article_container = soup.find(attrs = {"id" : "detail_content"})
    embedded_container = article_container.findAll("iframe")
    for x in embedded_container:
        url = x.get("src")
        tags = tagging.classify_and_tag(url, SEPTSURSEPT_NETLOC, SEPTSURSEPT_INTERNAL_SITES)
        tags.add('embedded media')
        tagged_urls.append(tagging.make_tagged_url(url, url, tags))

    # some embedded media are not in iframe, but embedded in the art_aside container
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


def extract_article_data(url):

    request  = urllib.urlopen(url)
    html_data = request.read()

    # detecter si l'article est un photoalbum
    if "/photoalbum/" in url:
        title = "__photoalbum__"
        author_name = ""
        pub_date = None
        pub_time = None
        source = ""
        intro = ""
        text = ""
        return (ArticleData(url, title, pub_date, pub_time, datetime.now(),
                            [],
                            title, author_name,
                            intro, text),
                html_data)
    
    else:
        page_type = detect_page_type(url)
        if page_type == IS_FRONTPAGE:
            return None, None
        elif page_type == MAYBE_ARTICLE:
            raise Exception("We couldn't define if this was an article or the frontpage, please check")


    # pour tous les autres vrais articles
        elif page_type == IS_ARTICLE:

            # if hasattr(source, 'read'):
            #   html_data = source.read(source)
            # else:
            #   request  = urllib.urlopen(url)
            #   html_data = request.read()

            soup  = bs4.BeautifulSoup(html_data)
            title = extract_title(soup)
            
            author_box = soup.find(attrs = {"class" : "author"})
            author_name = extract_author_name(author_box)
            pub_date, pub_time = extract_date_and_time(author_box)

            source = extract_source(author_box)

            intro = extract_intro(soup)

            category = extract_category(soup)

            text, tagged_urls_intext = extract_text_content_and_links(soup)

            tagged_urls_read_more_box = extract_links_from_read_more_box(soup)

            tagged_urls_sidebar_box = extract_links_from_sidebar_box(soup)

            tagged_urls_embedded_media = extract_embedded_media(soup)

            tagged_urls = tagged_urls_intext + tagged_urls_read_more_box + tagged_urls_sidebar_box + tagged_urls_embedded_media

            return (ArticleData(url, title, pub_date, pub_time, datetime.now(),
                            tagged_urls,
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
    url4 = "http://www.7sur7.be/7s7/fr/8024/Stars/photoalbum/detail/1492820/1170797/0/La-Mostra-de-Venise-au-jour-le-jour.dhtml"
    url6 = "http://www.7sur7.be/7s7/fr/1757/Dopage-dans-le-cyclisme/article/detail/1514991/2012/10/11/Armstrong-est-un-grand-champion-point-final.dhtml"
    url7 = "http://www.7sur7.be/7s7/fr/1505/Monde/article/detail/1520913/2012/10/21/Une-premiere-Amerindienne-canonisee.dhtml"
    url8 = "http://www.7sur7.be/7s7/fr/8012/photo/photoalbum/detail/1520894/1188429/0/Nuit-blanche-a-Luxembourg.dhtml"
    url9 = "http://www.7sur7.be/7s7/fr/1502/Belgique/article/detail/1520790/2012/10/20/Le-pacte-de-solidarite-signe-par-Onkelinx-tres-critique.dhtml"
    url10 = "http://www.7sur7.be/7s7/fr/1509/Football-Belge/article/detail/1520820/2012/10/20/Une-raclee-pour-Bruges-un-exploit-pour-Charleroi.dhtml"
    url11 = "http://www.7sur7.be/7s7/fr/1505/Monde/article/detail/1528304/2012/11/04/La-Marche-russe-des-ultra-nationalistes-reclame-le-depart-de-Poutine.dhtml"
    url12 = "http://www.7sur7.be/7s7/fr/1505/Monde/article/detail/1528304/2012/11/04/La-Marche-russe-des-ultra-nationalistes-reclame-le-depart-de-Poutine.dhtml"
    url13 = "http://www.7sur7.be/7s7/fr/8024/Stars/photoalbum/detail/85121/1193441/0/Showbiz-en-images.dhtml"
    url14 = "http://www.7sur7.be/7s7/fr/1527/People/article/detail/1527428/2012/11/02/La-robe-interactive-de-Nicole-Scherzinger.dhtml"
    url15 = "http://www.7sur7.be/7s7/fr/1504/Insolite/article/detail/1501041/2012/09/14/Une-traversee-des-Etats-Unis-avec-du-bacon-comme-seule-monnaie.dhtml"
    urls = [url1, url2, url3, url4, url6, url7, url8, url9, url10, url11, url12, url13]
    
    from pprint import pprint
    import json
    f = open("/Users/judemaey/code/2012-09-02/7sur7.json")
    urls = json.load(f)

    for x in urls:
        for y in x[1]:
            url = y[1]
            article_data, html = extract_article_data(url)
            print article_data.title
            print article_data.url
            pprint(article_data.links)
            print len(article_data.links)
            print "\n"
            print "******************************"
            print "\n"

    # for url in urls:
    #     article_data, html = extract_article_data(url)
    #     print article_data.title
    #     print article_data.url
    #     pprint(article_data.links)
    #     print len(article_data.links)



    # frontpage = get_frontpage_toc()
    # for item in frontpage:
    #     for title, url in item:
    #         print url
    #         article_data, html = extract_article_data(url)
    #         if article_data:
    #             print article_data.title
    #             print len(article_data.links)

    # article_data, html = extract_article_data(url15)
    # if article_data:
    #     print article_data.title
    #     pprint(article_data.links)
    #     print len(article_data.links)

    


