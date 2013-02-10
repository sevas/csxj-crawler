# -*- coding: utf-8 -*-

import codecs
from datetime import datetime
import locale
from itertools import chain
import urllib
import urllib2
import itertools as it
from urlparse import urlparse
from datetime import datetime

from scrapy.selector import HtmlXPathSelector

from parser_tools.utils import fetch_content_from_url, fetch_html_content
from parser_tools.utils import extract_plaintext_urls_from_text, remove_text_formatting_markup_from_fragments
from parser_tools.utils import remove_text_formatting_and_links_from_fragments
from parser_tools.utils import convert_utf8_url_to_ascii
from parser_tools.utils import setup_locales
from csxj.common.tagging import classify_and_tag, make_tagged_url, update_tagged_urls
from csxj.db.article import ArticleData

from parser_tools import rossel_utils
from helpers.unittest_generator import generate_test_func, save_sample_data_file

from csxj.common.tagging import print_taggedURLs

setup_locales()


SUDINFO_INTERNAL_SITES = {
    'portfolio.sudinfo.be': ['internal', 'gallery'],
    'portfolio.sudpresse.be': ['internal', 'gallery'],

    'comines-warneton.blogs.sudinfo.be':['internal', 'jblog'],
    'mouscron.blogs.sudinfo.be':['internal', 'jblog'],
    'dottignies.blogs.sudinfo.be':['internal', 'jblog'],
    'woluwesaintlambert.blogs.sudinfo.be':['internal', 'jblog'],
    'haren.blogs.sudinfo.be':['internal', 'jblog'],
    'tournai.blogs.sudinfo.be':['internal', 'jblog'],
    'pecq.blogs.sudinfo.be':['internal', 'jblog'],
    'beloeil.blogs.sudinfo.be':['internal', 'jblog'],
    'peruwelz.blogs.sudinfo.be':['internal', 'jblog'],
    'ath.blogs.sudinfo.be':['internal', 'jblog'],
    'leuze-en-hainaut.blogs.sudinfo.be':['internal', 'jblog'],
    'estinnes.blogs.sudinfo.be':['internal', 'jblog'],
    'binche.blogs.sudinfo.be':['internal', 'jblog'],
    'chapelle-lez-herlaimont.blogs.sudinfo.be':['internal', 'jblog'],
    'lalouviere.blogs.sudinfo.be':['internal', 'jblog'],
    'leroeulx.blogs.sudinfo.be':['internal', 'jblog'],
    'waterloo.blogs.sudinfo.be':['internal', 'jblog'],
    'tubize.blogs.sudinfo.be':['internal', 'jblog'],
    'havre-obourg-saint-denis.blogs.sudinfo.be':['internal', 'jblog'],
    'saint-symphorien.blogs.sudinfo.be':['internal', 'jblog'],
    'mesvin.blogs.sudinfo.be':['internal', 'jblog'],
    'frameries.blogs.sudinfo.be':['internal', 'jblog'],
    'haut-pays.blogs.sudinfo.be':['internal', 'jblog'],
    'dour.blogs.sudinfo.be':['internal', 'jblog'],
    'quievrain.blogs.sudinfo.be':['internal', 'jblog'],
    'colfontaine.blogs.sudinfo.be':['internal', 'jblog'],
    'boussu-hornu.blogs.sudinfo.be':['internal', 'jblog'],
    'saint-ghislain.blogs.sudinfo.be':['internal', 'jblog'],
    'aiseau-presles.blogs.sudinfo.be':['internal', 'jblog'],
    'charleroi.blogs.sudinfo.be':['internal', 'jblog'],
    'chatelet.blogs.sudinfo.be':['internal', 'jblog'],
    'erquelinnes.blogs.sudinfo.be':['internal', 'jblog'],
    'fleurus.blogs.sudinfo.be':['internal', 'jblog'],
    'fontaine-leveque.blogs.sudinfo.be':['internal', 'jblog'],
    'gerpinnes.blogs.sudinfo.be':['internal', 'jblog'],
    'hamsurheure-nalinnes.blogs.sudinfo.be':['internal', 'jblog'],
    'lobbes.blogs.sudinfo.be':['internal', 'jblog'],
    'thuin.blogs.sudinfo.be':['internal', 'jblog'],
    'hannut.blogs.sudinfo.be':['internal', 'jblog'],
    'heron.blogs.sudinfo.be':['internal', 'jblog'],
    'marchin.blogs.sudinfo.be':['internal', 'jblog'],
    'mohalongpre.blogs.sudinfo.be':['internal', 'jblog'],
    'nandrin.blogs.sudinfo.be':['internal', 'jblog'],
    'oreye.blogs.sudinfo.be':['internal', 'jblog'],
    'tinlot.blogs.sudinfo.be':['internal', 'jblog'],
    'vinalmont.blogs.sudinfo.be':['internal', 'jblog'],
    'waremme.blogs.sudinfo.be':['internal', 'jblog'],
    'bassenge.blogs.sudinfo.be':['internal', 'jblog'],
    'dalhem.blogs.sudinfo.be':['internal', 'jblog'],
    'fourons.blogs.sudinfo.be':['internal', 'jblog'],
    'herstal.blogs.sudinfo.be':['internal', 'jblog'],
    'oupeye.blogs.sudinfo.be':['internal', 'jblog'],
    'vise.blogs.sudinfo.be':['internal', 'jblog'],
    'ans.blogs.sudinfo.be':['internal', 'jblog'],
    'beyne-heusay.blogs.sudinfo.be':['internal', 'jblog'],
    'bressoux-droixhe.blogs.sudinfo.be':['internal', 'jblog'],
    'esneux.blogs.sudinfo.be':['internal', 'jblog'],
    'fleron.blogs.sudinfo.be':['internal', 'jblog'],
    'fragnee.blogs.sudinfo.be':['internal', 'jblog'],
    'juprelle.blogs.sudinfo.be':['internal', 'jblog'],
    'laveu.blogs.sudinfo.be':['internal', 'jblog'],
    'neupre.blogs.sudinfo.be':['internal', 'jblog'],
    'rocourt.blogs.sudinfo.be':['internal', 'jblog'],
    'seraing.blogs.sudinfo.be':['internal', 'jblog'],
    'trooz.blogs.sudinfo.be':['internal', 'jblog'],
    'aubel.blogs.sudinfo.be':['internal', 'jblog'],
    'malmedy.blogs.sudinfo.be':['internal', 'jblog'],
    'plombieres.blogs.sudinfo.be':['internal', 'jblog'],
    'trois-ponts.blogs.sudinfo.be':['internal', 'jblog'],
    'vervietois.blogs.sudinfo.be':['internal', 'jblog'],
    'daverdisse.blogs.sudinfo.be':['internal', 'jblog'],
    'nassogne.blogs.sudinfo.be':['internal', 'jblog'],
    'neufchateau.blogs.sudinfo.be':['internal', 'jblog'],
    'tellin.blogs.sudinfo.be':['internal', 'jblog'],
    'vielsalm.blogs.sudinfo.be':['internal', 'jblog'],
    'wellin.blogs.sudinfo.be':['internal', 'jblog'],
    'gaume.blogs.sudinfo.be':['internal', 'jblog'],
    'virton.blogs.sudinfo.be':['internal', 'jblog'],
    'andenne.blogs.sudinfo.be':['internal', 'jblog'],
    'ciney.blogs.sudinfo.be':['internal', 'jblog'],
    'gedinne.blogs.sudinfo.be':['internal', 'jblog'],
    'malonne.blogs.sudinfo.be':['internal', 'jblog'],
    'profondeville.blogs.sudinfo.be':['internal', 'jblog'],
    'rochefort.blogs.sudinfo.be':['internal', 'jblog'],
    'yvoir.blogs.sudinfo.be':['internal', 'jblog'],
    'couvin.blogs.sudinfo.be':['internal', 'jblog'],
    'florennes.blogs.sudinfo.be':['internal', 'jblog'],
    'fosses-la-ville.blogs.sudinfo.be':['internal', 'jblog'],
    'jemeppe-sur-sambre.blogs.sudinfo.be':['internal', 'jblog'],
    'sambreville.blogs.sudinfo.be':['internal', 'jblog'],
    'sivryrance.blogs.sudinfo.be':['internal', 'jblog'],
    'walcourt.blogs.sudinfo.be':['internal', 'jblog'],
    'ostendesurmer.blogs.sudinfo.be':['internal', 'jblog'],

    'secret-story.blogs.sudinfo.be' : ['internal', 'jblog'],
    'joggings.blogs.sudinfo.be' : ['internal', 'jblog'],
    'signebeaute.blogs.sudinfo.be' : ['internal', 'jblog'],
    'moteurs.blogs.sudinfo.be' : ['internal', 'jblog'],
    'secourslux.blogs.sudinfo.be' : ['internal', 'jblog'],
    'lameuse04.blogs.sudinfo.be' : ['internal', 'jblog'],
    'corpos.blogs.sudinfo.be' : ['internal', 'jblog'],
    'cyclismerevue.blogs.sudinfo.be' : ['internal', 'jblog'],
    'faitsdivers.blogs.sudinfo.be' : ['internal', 'jblog'],
    'rallye-passion.blogs.sudinfo.be' : ['internal', 'jblog'],
    'jeudeballe.blogs.sudinfo.be' : ['internal', 'jblog'],

    'pdf.lameuse.be': ['internal', 'pdf newspaper'],
    'pdf.lacapitale.be': ['internal', 'pdf newspaper'],
    'pdf.lanouvellegazette.be': ['internal', 'pdf newspaper'],
    'pdf.laprovince.be': ['internal', 'pdf newspaper'],
    'pdf.nordeclair.be': ['internal', 'pdf newspaper']
}

SUDINFO_OWN_NETLOC = 'www.sudinfo.be'
SUDINFO_OWN_DOMAIN = 'sudinfo.be'

SOURCE_TITLE = u"Sud Info"
SOURCE_NAME = u"sudinfo"


def extract_date(hxs):
    today = datetime.today()

    date_string = u"".join(hxs.select("//p[@class='publiele']//text()").extract())
    date_bytestring = codecs.encode(date_string, 'utf-8')

    if date_string.startswith(u"Publié le "):
        date_fmt = codecs.encode(u"Publié le %A %d %B %Y à %Hh%M", 'utf-8')
    elif date_string.startswith(u"Mis à jour le "):
        date_fmt = codecs.encode(u"Mis à jour le %A %d %B %Y à %Hh%M", 'utf-8')
    else:
        raise ValueError("Unsupported date format. Update your parser.")

    datetime_published = datetime.strptime(date_bytestring, date_fmt)

    return datetime_published.date(), datetime_published.time()


def extract_title_and_url(link_hxs):
    url = link_hxs.select("./@href").extract()[0]
    # sometimes, there are links only I can see.
    if link_hxs.select(".//text()").extract():
        title = link_hxs.select(".//text()").extract()[0].strip()
        # maybe it was a space only string, which is not really interesting either
        if not title:
            title = "__GHOST_LINK__"
    else:
        title = "__GHOST_LINK__"
    return title, url


def extract_img_link_info(link_hxs):
    url = link_hxs.select("./@href").extract()[0]
    title = link_hxs.select("./img/@src").extract()[0].strip()
    return title, url


def extract_and_tag_iframe_source(embedded_frame):
    target_url = embedded_frame.select("./@src").extract()[0]
    tags = classify_and_tag(target_url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
    tags.update(['embedded', 'iframe'])
    return target_url, tags


def extract_text_and_links_from_paragraph(paragraph_hxs):
    def separate_img_and_text_links(links):
        img_links = [l for l in links if l.select("./img")]
        text_links = [l for l in links if l not in img_links]

        return [extract_title_and_url(link) for link in text_links], [extract_img_link_info(link) for link in img_links]

    links = paragraph_hxs.select(".//a")

    titles_and_urls, img_targets_and_urls = separate_img_and_text_links(links)

    tagged_urls = list()
    for title, url in titles_and_urls:
        tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
        tags.update(['in text'])
        if title == "__GHOST_LINK__":
            tags.update(['ghost link'])
        tagged_urls.append(make_tagged_url(url, title, tags))

    for img_target, url in img_targets_and_urls:
        tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
        tags.update(['in text', 'embedded image'])
        tagged_urls.append(make_tagged_url(url, img_target, tags))

    # plaintext urls
    text_fragments = paragraph_hxs.select("./text()").extract()
    if text_fragments:
        text = u"".join(remove_text_formatting_markup_from_fragments(text_fragments))

        #print remove_text_formatting_and_links_from_fragments(text_fragments)
        plaintext_urls = extract_plaintext_urls_from_text(remove_text_formatting_and_links_from_fragments(text_fragments))
        for url in plaintext_urls:
            tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
            tags.update(['plaintext', 'in text'])

            tagged_urls.append(make_tagged_url(url, url, tags))
    else:
        text = u""

    # iframes
    iframes = paragraph_hxs.select(".//iframe")
    for iframe in iframes:
        target_url, tags = extract_and_tag_iframe_source(iframe)
        tagged_urls.append(make_tagged_url(target_url, "__EMBEDDED_IFRAME__", tags))

    return text, tagged_urls


def extract_intro_and_links(hxs):
    intro_container = hxs.select("//div [@id='article']/p[starts-with(@class, 'chapeau')]/following-sibling::*[1]")
    intro_text, tagged_urls = extract_text_and_links_from_paragraph(intro_container)
    return intro_text, tagged_urls


def extract_links_from_media_items(media_items):
    """ Extract and tag links from the list of embedded items.
    Returns a list of TaggedURL

    Parameters:

        @media_items: list of html selectors pointing to every list item (<li>)
    """

    def extract_and_tag_url_from_iframe(item):
        embedded_frame = item.select(".//iframe")
        if embedded_frame:
            target_url, tags = extract_and_tag_iframe_source(embedded_frame)
            tags = classify_and_tag(target_url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)

            return make_tagged_url(target_url, title, tags)
        else:
            return None

    tagged_urls = list()
    for item in media_items:
        media_type = item.select("./@class").extract()[0]

        title = item.select('./h3/text()').extract()
        if title:
            title = title[0]
        else:
            title = "__NO_TITLE__"

        if  media_type == 'video':
            if item.select(".//div [contains(@class, 'emvideo-kewego')]"):
                url = item.select(".//div [contains(@class, 'emvideo-kewego')]//video/@poster").extract()
                if url:
                    url = url[0]
                    tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
                    tags.update(['bottom video', 'embedded video', 'embedded', 'kewego'])
                    tagged_urls.append(make_tagged_url(url, title, tags))
                else:
                    raise ValueError("There is a kewego video here somewhere, but we could not find the link.")
            elif item.select(".//div [contains(@class, 'emvideo-youtube')]"):
                url = item.select(".//div [contains(@class, 'emvideo-youtube')]//object/@data").extract()
                if url:
                    url = url[0]
                    tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
                    tags.update(['bottom video', 'embedded video', 'embedded', 'youtube'])
                    tagged_urls.append(make_tagged_url(url, title, tags))
                else:
                    raise ValueError("There is a youtube video here somewhere, but we could not find the link.")
            else:
                raise ValueError("A unknown type of embedded video has been detected. Please update this parser.")
        elif media_type == 'document':
            embedded_widget_url = extract_and_tag_url_from_iframe(item)
            if embedded_widget_url:
                tagged_urls.append(embedded_widget_url)
            else:
                raise ValueError("This document does not embed an iframe. Please update this parser.")
        elif media_type == "links":
            links = item.select("./span/a")
            for l in links:
                title, url = extract_title_and_url(l)
                tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
                tagged_urls.append(make_tagged_url(url, title, tags))
        elif media_type == "other":
            embedded_widget_url = extract_and_tag_url_from_iframe(item)
            if embedded_widget_url:
                tagged_urls.append(embedded_widget_url)
            else:
                raise ValueError("The expected iframe object was not found. Please update this parser.")
        else:
            raise ValueError("Unknown media type ('{0}') detected. Please update this parser.".format(media_type))

    return tagged_urls


def extract_content_and_links(hxs):
    content_paragraphs_hxs = hxs.select("//div [@id='article']/p[starts-with(@class, 'publiele')]/following-sibling::p")

    all_content_paragraphs, all_tagged_urls = list(), list()

    # process paragraphs
    for p in content_paragraphs_hxs:
        text, tagged_urls = extract_text_and_links_from_paragraph(p)
        all_content_paragraphs.append(text)
        all_tagged_urls.extend(tagged_urls)


    #extract embedded videos
    divs = hxs.select("//div [@id='article']/p[starts-with(@class, 'publiele')]/following-sibling::div/div [@class='bottomVideos']")

    for div in divs:
        urls = div.select("./div [contains(@class, 'emvideo-kewego')]//video/@poster").extract()
        for url in urls:
            tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
            tags.update(['bottom video', 'embedded video', 'embedded'])

            all_tagged_urls.append(make_tagged_url(url, url, tags))

    new_media_items = hxs.select("//div [@class='digital-wally_digitalobject']//li")

    all_tagged_urls.extend(extract_links_from_media_items(new_media_items))

    return all_content_paragraphs, all_tagged_urls


LINK_TYPE_TO_TAG = {
    'media-video': ['video'],
    'media-press': [],
}


def extract_associated_links(hxs):
    links = hxs.select("//div[@id='picture']/descendant::div[@class='bloc-01']//a")

    all_tagged_urls = []

    if links:
        def extract_url_and_title(link_hxs):
            url = link_hxs.select('@href').extract()[0]
            title = u"".join(link_hxs.select("text()").extract())

            tags = set()
            if not title:
                title = u'No Title'
                tags.add('ghost link')
            if not url:
                url = u''
                tags.add('no target')
            return url, title, tags

        all_tagged_urls = list()
        for item in links:
            url, title, tags = extract_url_and_title(item)
            tags.update(classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES))
            link_type = item.select('@class')
            if link_type and link_type[0] in LINK_TYPE_TO_TAG:
                tags.update(LINK_TYPE_TO_TAG[link_type])

            tags.add("sidebar box")

            all_tagged_urls.append(make_tagged_url(url, title, tags))

    media_links = hxs.select("//div[@id='picture']/descendant::div[@class='wrappAllMedia']/div")


    for i, item in enumerate(media_links):
        if item.select('./img'):
            pass
        else:
            raise ValueError("The media box contains something other than an image. Update your parser")
            # item_id = item.select("./@class").extract()
            # url = item_id[0]
            # title = u"EMBEDDED MEDIA {0}".format(i)
            # tags = set(['media', 'embedded'])
            # all_tagged_urls.append(make_tagged_url(url, title, tags))

    return all_tagged_urls


def is_page_error_404(hxs):
    return hxs.select("//head/title/text()").extract() == '404'


def extract_article_data(source):
    """
    """

    if hasattr(source, 'read'):
        html_content = source.read()
    else:
        source = convert_utf8_url_to_ascii(source)
        try:
            html_content = fetch_html_content(source)
        except urllib2.HTTPError as err:
            if err.code == 404:
                return None, "<html><head><title>404</title></head><body></body></html>"
            else:
                raise err

    hxs = HtmlXPathSelector(text=html_content)

    if is_page_error_404(hxs):
        return None, html_content
    else:
        category = hxs.select("//p[starts-with(@class, 'fil_ariane')]/a//text()").extract()
        title = hxs.select("//div[@id='article']/h1/text()").extract()[0]
        # new version :
        # #title = hxs.select("//div[@id='article']/article//h1/text()").extract()[0]

        pub_date, pub_time = extract_date(hxs)
        author = hxs.select("//p[@class='auteur']/text()").extract()[0]
        fetched_datetime = datetime.today()

        intro, intro_links = extract_intro_and_links(hxs)

        content, content_links = extract_content_and_links(hxs)
        associated_links = extract_associated_links(hxs)
        all_links = intro_links + content_links + associated_links
        updated_tagged_urls = update_tagged_urls(all_links, rossel_utils.SUDINFO_SAME_OWNER)

        #print generate_test_func('links_intext_not_plaintext', 'sudinfo', dict(tagged_urls=updated_tagged_urls))
        #save_sample_data_file(html_content, source.name, 'in_text_same_owner', '/Users/judemaey/code/csxj-crawler/tests/datasources/test_data/sudinfo')

        return (ArticleData(source, title, pub_date, pub_time, fetched_datetime,
                            updated_tagged_urls,
                            category, author,
                            intro, content),
                html_content)


### frontpage stuff
def extract_title_url_from_hxs_a(link):
    title = ''.join(link.select(".//text()").extract())
    return title.strip(), link.select("@href").extract()[0]


def get_regional_toc():
    url = 'http://www.sudinfo.be/8/regions'
    html_content = fetch_content_from_url(url)

    hxs = HtmlXPathSelector(text=html_content)
    links = hxs.select("//div[@class='first-content w630-300']//div[@class='bloc_section']//li/a")
    return [extract_title_url_from_hxs_a(link) for link in links]


def make_full_url(prefix, titles_and_urls):
    return [(title, urllib.basejoin(prefix, url)) for title, url in titles_and_urls]


def separate_blogposts_and_news(titles_and_urls):
    def is_internal_url(url):
        scehem, netloc, path, params, query, fragments = urlparse(url)
        return not netloc
    news_items = [(t, u) for t, u in titles_and_urls if is_internal_url(u)]
    blogpost_items = [(t, u) for t, u in titles_and_urls if (t, u) not in news_items]
    return news_items, blogpost_items


def get_frontpage_toc():
    BASE_URL = u'http://www.sudinfo.be/'
    html_content = fetch_content_from_url(BASE_URL)
    hxs = HtmlXPathSelector(text=html_content)

    column1_headlines = hxs.select("//div[starts-with(@class, 'first-content')]//div[starts-with(@class, 'article')]//h2/a")
    column3_headlines = hxs.select("//div[@class='octetFun']/a/child::h3/..")
    buzz_headlines = hxs.select("//div[@class='buzz exergue clearfix']//h2/a")
    buzz_headlines.extend(hxs.select("//div[@class='buzz exergue clearfix']//li/a"))

    all_link_selectors = it.chain(column1_headlines, column3_headlines, buzz_headlines)
    headlines = [extract_title_url_from_hxs_a(link_selector) for link_selector in all_link_selectors]

    regional_headlines = get_regional_toc()
    headlines.extend(regional_headlines)

    news, blogposts = separate_blogposts_and_news(headlines)
    return make_full_url(BASE_URL, news), blogposts


def show_frontpage_articles():
    toc, blogs = get_frontpage_toc()

    print len(toc)
    for i, (title, url) in enumerate(toc[:]):
        print ""
        print u"----- [{0:02d}] -- {1}".format(i, url)
        article_data, html_content = extract_article_data(url)
        article_data.print_summary()
        #print article_data.to_json()


def test_sample_data():
    import os
    root = os.path.join(os.path.dirname(__file__), '../../sample_data')
    filepath = os.path.join(root, 'sudinfo/fake_plaintext.html')


    with open(filepath) as f:
        article_data, raw = extract_article_data(f)
        # article_data.print_summary()

        print_taggedURLs(article_data.links, 100)

def show_article():
    urls = [
        u"http://www.sudinfo.be/336280/article/sports/foot-belge/anderlecht/2012-02-26/lierse-anderlecht-les-mauves-vont-ils-profiter-de-la-defaite-des-brugeois",
        u"http://www.sudinfo.be/335985/article/sports/foot-belge/charleroi/2012-02-26/la-d2-en-direct-charleroi-gagne-en-l-absence-d-abbas-bayat-eupen-est-accro",
        u"http://www.sudinfo.be/361378/article/sports/foot-belge/standard/2012-03-31/jose-riga-apres-la-defaite-du-standard-a-gand-3-0-nous-n%E2%80%99avons-pas-a-rougir",
        u"http://www.sudinfo.be/361028/article/fun/people/2012-03-31/jade-foret-et-arnaud-lagardere-bientot-parents",
        u"http://www.sudinfo.be/361506/article/fun/insolite/2012-04-01/suppression-du-jour-ferie-le-1er-mai-sarkozy-qui-s’installe-en-belgique-attentio",
        u"http://www.sudinfo.be/359805/article/culture/medias/2012-03-29/gopress-le-premier-kiosque-digital-belge-de-la-presse-ecrite-avec-sudpresse",
        u"http://www.sudinfo.be/346549/article/regions/liege/actualite/2012-03-12/debordements-au-carnaval-de-glons-un-bus-tec-arrete-et-40-arrestationss",
        u"http://www.sudinfo.be/522122/article/actualite/faits-divers/2012-09-15/victor-dutroux-michelle-martin-est-aussi-une-victime-de-marc-dont-je-ne-sais-pa",
        u"http://www.sudinfo.be/518865/article/actualite/belgique/2012-09-11/le-prince-laurent-n%E2%80%99est-pas-sur-qu%E2%80%99albert-est-reellement-son-pere-%E2%80%9D",
        u"http://www.sudinfo.be/522313/article/regions/mons/2012-09-15/mons-accuse-de-viols-en-serie-le-malgache-n’a-avoue-qu’un-seul-fait",
        u"http://www.sudinfo.be/522322/article/regions/mouscron/2012-09-15/comines-john-verfaillie-champion-de-belgique-de-rummikub",
        u"http://www.sudinfo.be/522139/article/regions/bruxelles/2012-09-15/victor-3-ans-s’echappe-de-son-ecole-et-se-retrouve-au-milieu-d’un-carrefour",
        u"http://www.sudinfo.be/335985/article/sports/foot-belge/charleroi/2012-02-26/la-d2-en-direct-charleroi-gagne-en-l-absence-d-abbas-bayat-eupen-est-accro",
        u"http://www.sudinfo.be/529977/article/sports/foot-belge/anderlecht/2012-09-18/ligue-des-champions-anderlecht-va-t-il-pouvoir-realiser-un-«truc»-dans-l’",
        u"http://www.sudinfo.be/534336/article/culture/medias/2012-09-25/eva-longoria-nue-tiffany-de-virgin-radio-va-le-faire-ainsi-que-toute-l’equipe-de",
        u"http://www.sudinfo.be/534573/article/sports/foot-belge/standard/2012-09-25/jelle-van-damme-standard-menace-benjamin-deceuninck-en-direct-fais-gaffe-av",
        u"http://www.sudinfo.be/534931/article/actualite/sante/2012-09-26/la-prescription-des-medicaments-bon-marche-continue-de-progresser",
        u"http://www.sudinfo.be/551998/article/fun/buzz/2012-10-04/des-nus-partout-dans-bruxelles-qui-miment-l-acte-sexuel-l’incroyable-performance",

        # liens 'same owner'
        u"http://www.sudinfo.be/551998/article/fun/buzz/2012-10-04/schocking-in-brussles-des-hommes-nus-miment-l-acte-sexuel-au-palais-de-justice-a",
        u"http://www.sudinfo.be/535396/article/culture/musique/2012-09-27/mylene-farmer-donnera-deux-concerts-en-belgique-l’an-prochain",

        # embedded coveritlive + standard widget
        u"http://www.sudinfo.be/306989/article/sports/foot-belge/standard/2012-01-08/standard-chattez-en-exclusivite-avec-sebastien-pocognoli-ce-lundi-des-13h30",

        # embeddes scribble
        u"http://www.sudinfo.be/655859/article/sports/foot-belge/anderlecht/2013-02-03/suivez-le-super-sunday-en-live-genk-ecrase-bruges-4-1-le-standard-en-visi"
    ]

    article, html = extract_article_data(urls[-1])
    for link in article.links:
        print titles
        print url
        print content
        print link


def show_frontpage_toc():
    headlines, blogposts = get_frontpage_toc()

    for title, url in headlines:
        print u"{0} \t\t\t\t\t [{1}]".format(title, url)

    for title, url in blogposts:
        print u"{0} \t\t\t\t\t [{1}]".format(title, url)

    print len(headlines), len(blogposts)

if __name__ == '__main__':
    #show_frontpage_toc()
    #download_one_article()
    #show_frontpage_articles()
    # show_article()

    # url = "/Volumes/Curst/json_db_0_5/sudinfo/2012-06-05/14.05.07/raw_data/18.html"
    # f = open(url, "r")

    # article_data, content_html = extract_article_data(f)
    # article_data.print_summary()
    test_sample_data()
