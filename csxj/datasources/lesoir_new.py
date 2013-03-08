#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
from datetime import datetime
import urlparse
import bs4
import itertools
from scrapy.selector import HtmlXPathSelector
from parser_tools.utils import remove_text_formatting_markup_from_fragments, extract_plaintext_urls_from_text, remove_text_formatting_and_links_from_fragments
from csxj.common import tagging
from csxj.db.article import ArticleData
from parser_tools.utils import fetch_html_content
from parser_tools.utils import setup_locales
from parser_tools import rossel_utils, constants

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
    # print soup.find(attrs={"id": "main-content"}).find("h2")
    # print soup.find("div", {"class": "article-content"}).find("h2")
    # print soup.find(attrs={"class": "meta"}).previous_sibling.previous_sibling
    if main_content.find("h1"):
        title = main_content.find("h1").contents[0]
    else :
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
        if len(intro_box.find("h3").contents) > 0:
            fragment = intro_box.find("h3").contents[0]
            intro = remove_text_formatting_markup_from_fragments(fragment, strip_chars='\t\r\n').rstrip()
            return intro

        if intro_box.find("h3").find_next_sibling("p"):
            fragment = intro_box.find("h3").find_next_sibling("p")
            intro = remove_text_formatting_markup_from_fragments(fragment, strip_chars='\t\r\n')
            return intro
        else:
            return []
    else:
        return []


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
            tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            tags.update(['plaintext', 'in text'])

            tagged_urls.append(tagging.make_tagged_url(url, url, tags))
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


def extract_embedded_media_from_top_box(container, site_netloc, site_internal_sites):
    # It might be a Kewego video
    if container.find(attrs={'class': 'emvideo emvideo-video emvideo-kewego'}):
        kplayer = container.find(attrs={'class': 'emvideo emvideo-video emvideo-kewego'})
        url_part1 = kplayer.object['data']
        url_part2 = kplayer.object.find('param', {'name': 'flashVars'})['value']
        if url_part1 is not None and url_part2 is not None:
            url = "%s?%s" % (url_part1, url_part2)
            all_tags = tagging.classify_and_tag(url, LESOIR_NETLOC, LESOIR_INTERNAL_SITES)
            if kplayer.next_sibling :
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

    # it might be a dailymotion or ustream video
    elif container.find(attrs={'class': 'emvideo emvideo-video emvideo-embedly'}):
        if container.find("param", {'name': 'movie'}):
            if container.find("param").get("value"):
                if container.find("param", {"name": "movie"}).get("value").startswith("http://www.ustream.tv"):
                    tagged_url = tagging.make_tagged_url(constants.NO_URL, constants.NO_TITLE, set(['embedded', 'video', constants.UNFINISHED_TAG]))
                    return tagged_url
            else:
                print "no value or what?"

        elif container.find("iframe"):
            url = container.find("iframe").get("src")
            if url:
                all_tags = tagging.classify_and_tag(url, site_netloc, site_internal_sites)
                tagged_url = tagging.make_tagged_url(url, url, all_tags | set(['embedded', 'top box', 'video']))
                return tagged_url
            else:
                raise ValueError("There seems to be a Dailymotion player but we couldn't find an URL. Update the parser.")
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
    elif container.find("img"):
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
    story = soup.find(attrs = {'class': 'article-body'})
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


def extract_article_data(source):

    if hasattr(source, 'read'):
        html_data = source.read()
    else:
        try:
            html_data = fetch_html_content(source)
        except HTTPError as e:
            if e.code == 404 or e.code == 403:
                return None, None
            else:
                raise
        except Exception:
            raise


    soup = bs4.BeautifulSoup(html_data)

    if soup.find(attrs={"id": "main-content"}).h2 and soup.find(attrs={"id": "main-content"}).h2.find(attrs={'class': 'ir locked'}):
        print "PAID ARTICLE"
        return None, None

    else:
        title = extract_title(soup)
        author_name = extract_author_name(soup)
        intro = extract_intro(soup)
        text, tagged_urls_intext = extract_text_content_and_links(soup)
        category = extract_category(soup)
        sidebar_links = extract_links_from_sidebar_box(soup)
        article_tags = extract_article_tags(soup)
        embedded_media_from_top_box = extract_links_to_embedded_content(soup)
        embedded_media_from_bottom = extract_embedded_media_from_bottom(soup)
        embedded_media_in_article = extract_embedded_media_in_article(soup)
        embedded_media = embedded_media_from_top_box + embedded_media_from_bottom + embedded_media_in_article
        all_links = tagged_urls_intext + sidebar_links + article_tags + embedded_media
        pub_date, pub_time = extract_date_and_time(soup)
        fetched_datetime = datetime.today()

        updated_tagged_urls = tagging.update_tagged_urls(all_links, rossel_utils.LESOIR_SAME_OWNER)

        # print generate_test_func('loads_of_embedded_stuff_and_pdf_newspaper', 'lesoir_new', dict(tagged_urls=updated_tagged_urls))
        # save_sample_data_file(html_data, source, 'loads_of_embedded_stuff_and_pdf_newspaper', '/Users/judemaey/code/csxj-crawler/tests/datasources/test_data/lesoir_new')

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
    # _, _, paywalled = get_frontpage_toc()
    # for p in paywalled:
    #     print p

    urls = ["file://localhost/Users/judemaey/code/csxj-crawler/tests/datasources/test_data/lesoir_new/embedded_dailymotion_video.html",
            "http://www.lesoir.be/187412/article/debats/chats/2013-02-11/11h02-%C2%ABil-est-temps-d%C3%A9finir-notre-politique-%C3%A9nerg%C3%A9tique%C2%BB"
            "http://www.lesoir.be/191397/article/culture/cinema/2013-02-16/l%E2%80%99ours-d%E2%80%99or-d%C3%A9cern%C3%A9-au-drame-roumain-%C2%ABchild%E2%80%99s-pose%C2%BB",
            "http://www.lesoir.be/200886/article/actualite/belgique/2013-03-02/didier-reynders-veut-mettre-imams-sous-contr%C3%B4le",
            "http://www.lesoir.be/200800/article/sports/football/2013-03-02/coupe-genk-anderlecht-1-0-apr%C3%A8s-prolongations-direct",
            "http://www.lesoir.be/200395/article/actualite/quiz/2013-03-01/quiz-actu-chiffr%C3%A9-semaine",
            "http://www.lesoir.be/200851/article/actualite/belgique/2013-03-02/budget-pour-andr%C3%A9-antoine-%C2%AB-bons-comptes-font-bons-amis-%C2%BB",
            "http://www.lesoir.be/200881/article/actualite/regions/bruxelles/2013-03-02/philippe-moureaux-%C2%ABa-pourtant-temps-pour-une-s%C3%A9rieuse-psychanalyse%C2%BB"
            ]

    urls_from_errors = [
        # return "None" does not work
        #"http://www.lesoir.be/187412/article/debats/chats/2013-02-11/11h02-gaz-schiste-menace-pour-belgique", 
        "http://www.lesoir.be/194330/article/actualite/belgique/2013-02-20/syndicats-ont-ils-raison-manifester", 
        "http://www.lesoir.be/194302/article/economie/2013-02-20/energie-facture-des-wallons-va-grimper-380-euros", 
        "http://www.lesoir.be/194252/article/actualite/belgique/2013-02-20/freinet-f\u00e2ch\u00e9-avec-maths", 
        "http://www.lesoir.be/194330/article/actualite/belgique/2013-02-20/syndicats-ont-ils-raison-manifester-sondage", 
        "http://www.lesoir.be/194127/article/debats/chats/2013-02-20/11h02-palais-doit-il-moderniser-sa-communication", 
        "http://www.lesoir.be/194127/article/debats/chats/2013-02-20/11h02-palais-doit-il-moderniser-sa-communication", 
        "http://www.lesoir.be/194127/article/debats/chats/2013-02-20/11h02-\u00abil-est-temps-pour-palais-moderniser-sa-communication\u00bb", 
        "http://www.lesoir.be/194756/article/economie/2013-02-21/des-t\u00e9l\u00e9coms-encore-trop-co\u00fbteuses", 
        "http://www.lesoir.be/194795/gallerie/2013-02-21/un-jour-sans-pour-messi-son-match-en-images", 
        "http://www.lesoir.be/194839/article/actualite/belgique/2013-02-21/elio-di-rupo-appelle-\u00e0-reprise-du-dialogue-social", 
        "http://www.lesoir.be/194711/article/debats/cartes-blanches/2013-02-21/l-in\u00e9vitable-intervention-au-mali-et-apr\u00e8s", 
        "http://www.lesoir.be/195093/article/actualite/belgique/2013-02-21/echanges-fiscaux-154-demandes-fran\u00e7aises-renseignements-\u00e0-belgique-en-2012", 
        "http://www.lesoir.be/195220/article/actualite/belgique/2013-02-21/un-camion-charg\u00e9-voitures-se-renverse-sur-l\u2019e40-une-heure-files", 
        "http://www.lesoir.be/194839/article/actualite/belgique/2013-02-21/kern-se-termine-sans-relance-du-dialogue-social", 
        "http://www.lesoir.be/195313/article/actualite/belgique/2013-02-21/olivier-maingain-veut-un-etat-wallonie-bruxelles", 
        "http://www.lesoir.be/195374/article/actualite/vie-du-net/2013-02-22/google-veut-soigner-son-image", 
        "http://www.lesoir.be/195417/article/sports/2013-02-22/oscar-pistorius-arrive-au-tribunal-o\u00f9-il-compara\u00eet-pour-meurtre", 
        "http://www.lesoir.be/195372/article/sports/2013-02-22/van-petegem-l\u2019homme-qui-aimait-pav\u00e9s", 
        "http://www.lesoir.be/195417/article/sports/2013-02-22/pistorius-une-longue-peine-prison-est-\u00abpresque-garantie\u00bb-estime-procureur", 
        "http://www.lesoir.be/195395/article/debats/chats/2013-02-22/11h02-oscar-pistorius-peut-il-\u00e9chapper-\u00e0-condamnation", 
        "http://www.lesoir.be/195614/article/economie/2013-02-22/des-d\u00e9tectives-priv\u00e9s-envoy\u00e9s-\u00e0-batibouw-vid\u00e9o", 
        "http://www.lesoir.be/195417/article/sports/2013-02-22/pistorius-d\u00e9fense-admet-un-possible-homicide-volontaire", 
        "http://www.lesoir.be/195380/article/actualite/monde/2013-02-22/pas-piti\u00e9-pour-cardinaux-entach\u00e9s", 
        "http://www.lesoir.be/195736/article/sports/football/2013-02-22/charleroi-zulte-waregem-en-direct-comment\u00e9", 
        "http://www.lesoir.be/195903/article/culture/cinema/2013-02-22/soir\u00e9e-des-c\u00e9sar-en-direct-21-heures", 
        "http://www.lesoir.be/195903/article/culture/cinema/2013-02-22/soir\u00e9e-des-c\u00e9sar-en-direct", 
        "http://www.lesoir.be/195903/article/culture/cinema/2013-02-22/belge-matthias-schoenaerts-remporte-c\u00e9sar-du-meilleur-acteur-live", 
        "http://www.lesoir.be/195903/article/culture/cinema/2013-02-22/belge-matthias-schoenaerts-remporte-c\u00e9sar-du-meilleur-espoir-masculin-live", 
        "http://www.lesoir.be/196132/article/actualite/belgique/2013-02-22/certificats-verts-\u00ab-nous-avons-tir\u00e9-sonnette-d\u2019alarme-en-2011-\u00bb", 
        "http://www.lesoir.be/196234/article/actualite/belgique/2013-02-23/mort-en-prison-\u00e0-mortsel-slfp-contre-suspension-du-policier", 
        "http://www.lesoir.be/196234/article/actualite/belgique/2013-02-23/battu-\u00e0-mort-en-prison-slfp-oppos\u00e9-\u00e0-suspension-du-policier", 
        "http://www.lesoir.be/196236/article/actualite/belgique/2013-02-23/doel-tihange-doutes-fran\u00e7ais", 
        "http://www.lesoir.be/196247/article/economie/2013-02-23/duel-milliardaires-autour-herbalife", 
        "http://www.lesoir.be/196301/article/sports/tennis/2013-02-23/malisse-et-darcis-\u00e9vitent-t\u00eates-s\u00e9rie-au-1er-tour-\u00e0-delray-beach", 
        "http://www.lesoir.be/196254/article/sports/cyclisme/2013-02-23/voici-venu-temps-des-\u00ab-vrais-\u00bb-flandriens", 
        "http://www.lesoir.be/196352/article/actualite/belgique/2013-02-23/nollet-consommateur-ne-payera-pas-facture-du-photovolta\u00efque-\u00abje-m-y-engage\u00bb", 
        "http://www.lesoir.be/196345/article/sports/cyclisme/2013-02-23/d\u00e9part-du-circuit-het-nieuwsblad-\u00e9t\u00e9-donn\u00e9", 
        "http://www.lesoir.be/196351/article/actualite/belgique/2013-02-23/nollet-consommateur-ne-payera-pas-facture-du-photovolta\u00efque-\u00abje-m-y-engage\u00bb", 
        "http://www.lesoir.be/196351/article/actualite/belgique/2013-02-23/nollet-consommateur-ne-payera-pas-facture-\u00abje-m\u2019y-engage\u00bb", 
        "http://www.lesoir.be/196351/article/actualite/belgique/2013-02-23/nollet-consommateur-ne-payera-pas-facture-\u00abje-m\u2019y-engage\u00bb", 
        "http://www.lesoir.be/196351/article/actualite/belgique/2013-02-23/nollet-\u00able-consommateur-ne-sera-pas-pigeon-du-photovolta\u00efque-je-m\u2019y-engage\u00bb", 
        "http://www.lesoir.be/196404/article/sports/cyclisme/2013-02-23/l\u2019italien-paolini-remporte-het-nieuwsblad", 
        "http://www.lesoir.be/195736/article/sports/football/2013-02-22/charleroi-zulte-waregem-0-0-direct", 
        "http://www.lesoir.be/196514/article/sports/football/2013-02-23/mons-s\u2019impose-0-1-\u00e0-courtrai", 
        "http://www.lesoir.be/196345/article/sports/cyclisme/2013-02-23/d\u00e9part-du-circuit-het-nieuwsblad-\u00e9t\u00e9-donn\u00e9", 
        "http://www.lesoir.be/196760/article/debats/chats/2013-02-24/11h02-est-on-d\u00e9j\u00e0-en-campagne-\u00e9lectorale", 
        "http://www.lesoir.be/196760/article/debats/chats/2013-02-24/11h02-est-on-d\u00e9j\u00e0-en-campagne-\u00e9lectorale", 
        "http://www.lesoir.be/196962/article/culture/2013-02-25/lumi\u00e8re-et-l\u2019\u00e9l\u00e9gance", 
        "http://www.lesoir.be/197036/article/sports/football/2013-02-25/un-super-sunday\u2026-pour-rien", 
        "http://www.lesoir.be/196760/article/debats/chats/2013-02-24/11h02-\u00ab-entre-ps-et-mr-\u00e7a-va-\u00eatre-difficile-pour-cdh-et-ecolo-d-exister-\u00bb", 
        "http://www.lesoir.be/197288/article/actualite/monde/2013-02-25/italie-gauche-bersani-largement-en-t\u00eate-des-l\u00e9gislatives", 
        "http://www.lesoir.be/197317/article/economie/2013-02-25/bnp-paribas-fortis-annonce-une-s\u00e9rie-nouveaut\u00e9s-en-mati\u00e8re-paiements-\u00e9lectroniqu", 
        "http://www.lesoir.be/196760/article/debats/chats/2013-02-24/11h02-\u00ab-entre-ps-et-mr-\u00e7a-va-\u00eatre-difficile-pour-cdh-et-ecolo-d-exister-\u00bb", 
        "http://www.lesoir.be/197288/article/actualite/monde/2013-02-25/italie-gauche-en-t\u00eate-\u00e0-chambre-coude-\u00e0-coude-au-s\u00e9nat", 
        "http://www.lesoir.be/197288/article/actualite/monde/2013-02-25/grillo-vrai-vainqueur-des-\u00e9lections-l\u2019italie-est-bloqu\u00e9e", 
        "http://www.lesoir.be/197461/article/economie/2013-02-25/gr\u00e8ce-est-elle-presque-sauv\u00e9e", 
        "http://www.lesoir.be/197288/article/actualite/monde/2013-02-25/grillo-v\u00e9ritable-vainqueur-des-\u00e9lections-l\u2019italie-est-bloqu\u00e9e", 
        "http://www.lesoir.be/197549/article/culture/medias-tele/2013-02-25/eddy-wilde-failli-ravir-poste-\u00e0-corinne-boulangier", 
        "http://www.lesoir.be/197664/article/economie/2013-02-26/nollet-assure-t-il-rentabilit\u00e9-minguet", 
        "http://www.lesoir.be/197744/article/debats/chats/2013-02-26/11h02-le\u00e7ons-du-scrutin-italien", 
        "http://www.lesoir.be/197744/article/debats/chats/2013-02-26/11h02-\u00ab-gauche-italienne-aujourd\u2019hui-choix-entre-peste-et-chol\u00e9ra-\u00bb", 
        "http://www.lesoir.be/197631/article/actualite/sciences-et-sante/2013-02-26/circoncision-affaiblirait-plaisir", 
        "http://www.lesoir.be/197856/article/actualite/belgique/2013-02-26/kim-gelder-rit-des-photos-ses-victimes", 
        "http://www.lesoir.be/197635/article/debats/chroniques/2013-02-26/comment-jusqu\u2019ici-france-parvenait-\u00e0-s\u2019en-sortir", 
        "http://www.lesoir.be/198178/article/economie/2013-02-26/scrutin-italien-affole-march\u00e9s", 
        "http://www.lesoir.be/198364/article/actualite/belgique/2013-02-26/wallonie-va-mieux-c\u2019est-un-flamand-qui-dit", 
        "http://www.lesoir.be/198432/article/actualite/belgique/2013-02-27/acw-lib\u00e9raux-r\u00e9clament-une-enqu\u00eate-parlementaire", 
        "http://www.lesoir.be/198431/article/actualite/belgique/2013-02-27/acw-lib\u00e9raux-r\u00e9clament-une-enqu\u00eate-parlementaire", 
        "http://www.lesoir.be/198470/article/debats/chats/2013-02-27/11h02-proc\u00e8s-gelder-devait-il-avoir-lieu", 
        "http://www.lesoir.be/198513/article/economie/2013-02-27/marianne-dans-starting-blocks", 
        "http://www.lesoir.be/198462/article/sports/2013-02-27/thorgan-hazard-\u00ab-on-voit-qui-je-suis-et-ce-que-je-vaux-\u00bb", 
        "http://www.lesoir.be/198455/article/actualite/monde/2013-02-27/beppe-grillo-comique-devenu-homme-politique", 
        "http://www.lesoir.be/198453/article/debats/chroniques/2013-02-27/n-va-objet-politique-non-identifi\u00e9", 
        "http://www.lesoir.be/198955/article/actualite/belgique/2013-02-27/l\u2019accord-social-qui-ne-dit-pas-son-nom", 
        "http://www.lesoir.be/198364/article/actualite/belgique/2013-02-26/wallonie-va-mieux-c\u2019est-un-flamand-qui-dit", 
        "http://www.lesoir.be/199095/article/economie/2013-02-27/electricit\u00e9-risque-black-out-en-2014", 
        "http://www.lesoir.be/199241/article/economie/2013-02-28/carterpillar-\u00abune-perte-850-emplois-c\u2019est-extr\u00eamement-pr\u00e9occupant\u00bb", 
        "http://www.lesoir.be/199241/article/economie/2013-02-28/carterpillar-\u00abune-perte-850-emplois-c\u2019est-extr\u00eamement-pr\u00e9occupant\u00bb", 
        "http://www.lesoir.be/199074/article/debats/2013-02-27/11h02-\u00ab-beno\u00eet-xvi-restera-une-pr\u00e9sence-spirituelle-pour-l\u2019eglise-\u00bb", 
        "http://www.lesoir.be/199245/article/debats/chroniques/2013-02-28/calvaire-deux-\u00ab-bekende-\u00bb", 
        "http://www.lesoir.be/199392/article/actualite/monde/2013-02-28/berlusconi-fait-\u00e0-nouveau-l\u2019objet-d\u2019une-enqu\u00eate-pour-corruption", 
        "http://www.lesoir.be/199249/article/actualite/monde/2013-02-28/beno\u00eet-xvi-retourne-\u00ab-\u00e0-une-vie-pri\u00e8re-\u00bb", 
        "http://www.lesoir.be/199243/article/debats/cartes-blanches/2013-02-28/parfois-mieux-vaut-se-taire-que-grincer-des-dents", 
        "http://www.lesoir.be/199247/article/actualite/monde/2013-02-28/budget-am\u00e9ricain-prix-du-sacrifice", 
        "http://www.lesoir.be/199877/article/economie/2013-02-28/aust\u00e9rit\u00e9-usa-obama-accuse-r\u00e9publicains-menacer-croissance", 
        "http://www.lesoir.be/199816/article/une/2013-02-28/missions-princi\u00e8res-il-faudra-payer-pour-\u00eatre-\u00e0-table-royale", 
        "http://www.lesoir.be/199917/article/culture/livres/2013-03-01/foire-aux-\u00e9crits-meurtriers", 
        "http://www.lesoir.be/199892/article/sports/2013-03-01/lierse-y-\u00e9tait-parvenu-en-1997-zulte-waregem-peut-il-r\u00e9p\u00e9ter-l\u2019exploit", 
        "http://www.lesoir.be/199816/article/actualite/belgique/2013-02-28/missions-princi\u00e8res-il-faudra-payer-pour-\u00eatre-\u00e0-table-royale", 
        "http://www.lesoir.be/199794/article/debats/chats/2013-02-28/11h02-caterpillar-o\u00f9-s-arr\u00eatera-jeu-domino", 
        "http://www.lesoir.be/199962/article/economie/2013-03-01/belgacom-banquier-du-gouvernement", 
        "http://www.lesoir.be/199895/article/actualite/belgique/2013-03-01/l\u2019amiante-tu\u00e9-160-fois-\u00e0-kapelle", 
        "http://www.lesoir.be/199794/article/debats/chats/2013-02-28/11h02-caterpillar-o\u00f9-s-arr\u00eatera-jeu-dominos", 
        "http://www.lesoir.be/199816/article/actualite/belgique/2013-02-28/missions-princi\u00e8res-il-faudra-payer-pour-assister-au-d\u00eener-gala", 
        "http://www.lesoir.be/199794/article/debats/chats/2013-02-28/11h02-caterpillar-o\u00f9-s-arr\u00eatera-jeu-dominos", 
        "http://www.lesoir.be/199794/article/debats/chats/2013-02-28/11h02-\u00ab-caterpillar-au-del\u00e0-l\u2019indignation-retrouver-un-\u00e9lan-collectif-\u00bb", 
        "http://www.lesoir.be/200115/article/actualite/fil-info/fil-info-economie/2013-03-01/nouveau-record-du-nombre-faillites-en-f\u00e9vrier", 
        "http://www.lesoir.be/199890/article/actualite/monde/2013-03-01/john-kerry-d\u00e9\u00e7oit-l\u2019opposition", 
        "http://www.lesoir.be/200427/article/economie/2013-03-01/belgacom-sanctionn\u00e9-en-bourse-pour-ses-r\u00e9sultats", 
        "http://www.lesoir.be/200467/article/actualite/fil-info/fil-info-belgique/2013-03-01/un-bonus-pension-pour-inciter-travailleurs-\u00e0-rester-plus-longtemp", 
        "http://www.lesoir.be/200601/article/economie/2013-03-01/caterpillar-\u00able-gouvernement-est-trop-mou\u00bb", 
        "http://www.lesoir.be/200627/article/sports/autres-sports/2013-03-01/euro-en-salle-r\u00e9sultats-1re-journ\u00e9e", 
        "http://www.lesoir.be/200557/article/actualite/belgique/2013-03-01/un-barom\u00e8tre-du-m\u00e9tissage-en-belgique", 
        "http://www.lesoir.be/200596/article/actualite/belgique/2013-03-01/budget-un-effort-25-milliards", 
        "http://www.lesoir.be/200573/article/actualite/belgique/2013-03-01/\u00ab-avant-notre-pays-avait-l\u2019image-l\u2019eldorado-pour-migrants-c\u2019est-fini-\u00bb", 
        "http://www.lesoir.be/200765/article/economie/2013-03-02/sncb-bye-bye-papier-bonjour-puce", 
        "http://www.lesoir.be/200788/article/sports/football/2013-03-02/vercauteren-\u00abj\u2019ai-poliment-refus\u00e9-un-contrat-pour-9-matchs\u00bb", 
        "http://www.lesoir.be/200815/article/economie/2013-03-02/\u00ab-caterpillar-faute-aux-salaires-trop-\u00e9lev\u00e9s-\u00bb", 
        "http://www.lesoir.be/200842/article/actualite/belgique/2013-03-02/fun\u00e9railles-du-cardinal-julien-ries-ont-eu-lieu-\u00e0-tournai", 
        "http://www.lesoir.be/201002/article/actualite/belgique/2013-03-03/une-voiture-tombe-dans-canal-bruxelles-charleroi-\u00e0-hauteur-hal" 
    ]

    article, html = extract_article_data(urls_from_errors[0])
    # article, html = extract_article_data(urls[0])

    # print article.title
    # print article.intro
    # print article.content

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




    # for url in urls_from_errors:
    #     print url
    #     if "sondage" not in url and "gallerie" not in url :
    #         article, html = extract_article_data(url)
    #         if article:
    #             print "this one works just fine"
    #         else:
    #             print "404/403"



