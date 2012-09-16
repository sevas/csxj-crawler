# -*- coding: utf-8 -*-

import sys
from datetime import datetime
import locale
from itertools import chain
import urllib
import codecs

from scrapy.selector import HtmlXPathSelector

from common.utils import fetch_content_from_url, fetch_html_content
from common.utils import extract_plaintext_urls_from_text
from csxj.common.tagging import  classify_and_tag, make_tagged_url
from csxj.db.article import ArticleData



# for datetime conversions
if sys.platform in ['linux2', 'cygwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF8')
elif sys.platform in [ 'darwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR')
elif sys.platform in [ 'win32']:
    # locale string from: http://msdn.microsoft.com/en-us/library/cdax410z(v=VS.80).aspx
    locale.setlocale(locale.LC_ALL, 'fra')


SUDINFO_INTERNAL_SITES = {
    'portfolio.sudinfo.be':['internal site', 'images', 'gallery'],
    'portfolio.sudpresse.be':['internal site', 'images', 'gallery'],
    'bassenge.blogs.sudinfo.be':['internal blog', 'blog'],
    'pdf.lameuse.be':['internal site', 'pdf newspaper'],

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
    title = link_hxs.select(".//text()").extract()[0].strip()
    return title, url


def extract_img_link_info(link_hxs):
    url = link_hxs.select("./@href").extract()[0]
    title = link_hxs.select("./img/@src").extract()[0].strip()
    return title, url



def extract_text_and_links_from_paragraph(paragraph_hxs):
    def separate_img_and_text_links(links):
        img_links = [l for l in links if l.select("./img")]
        text_links = [l for l in links if l not in img_links]

        return [extract_title_and_url(link) for link in text_links],  [extract_img_link_info(link) for link in img_links]


    links = paragraph_hxs.select("./a")
    titles_and_urls, img_targets_and_urls = separate_img_and_text_links(links)

    tagged_urls = list()
    for title, url in titles_and_urls:
        tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
        tags.update(['in text'])
        tagged_urls.append(make_tagged_url(url, title, tags))

    for img_target, url in img_targets_and_urls:
        tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
        tags.update(['in text', 'embedded image'])
        tagged_urls.append(make_tagged_url(url, img_target, tags))

    text_fragments  = paragraph_hxs.select(".//text()").extract()
    if text_fragments:
        text = ' '.join(text_fragments)
        plaintext_urls = extract_plaintext_urls_from_text(text)
        for url in plaintext_urls:
            tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
            tags.update(['plaintext', 'in text'])

            tagged_urls.append(make_tagged_url(url, url, tags))
    else:
        text = u""


    return text, tagged_urls



def extract_intro_and_links(hxs):
    intro_container = hxs.select("//div [@id='article']/p[starts-with(@class, 'chapeau')]/following-sibling::*[1]")
    intro_text, tagged_urls = extract_text_and_links_from_paragraph(intro_container)
    return intro_text, tagged_urls



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

    for item in new_media_items:
        media_type = item.select("./@class").extract()[0]
        title = item.select('./h3/text()').extract()[0]
        if  media_type == 'video':
            if item.select(".//div [contains(@class, 'emvideo-kewego')]"):
                url = item.select(".//div [contains(@class, 'emvideo-kewego')]//video/@poster").extract()
                if url:
                    url = url[0]
                    tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
                    tags.update(['bottom video', 'embedded video', 'embedded', 'kewego'])
                    all_tagged_urls.append(make_tagged_url(url, title, tags))
                else:
                    raise ValueError("There is a kewego video here somewhere, but we could not find the link.")
            elif item.select(".//div [contains(@class, 'emvideo-youtube')]"):
                url = item.select(".//div [contains(@class, 'emvideo-youtube')]//object/@data").extract()
                if url:
                    url = url[0]
                    tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
                    tags.update(['bottom video', 'embedded video', 'embedded', 'youtube'])
                    all_tagged_urls.append(make_tagged_url(url, title, tags))
                else:
                    raise ValueError("There is a youtube video here somewhere, but we could not find the link.")
            else:
                raise ValueError("A unknown type of embedded video has been detected. Please update this parser.")
        elif media_type == 'document':
            embedded_frame = item.select(".//iframe")
            if embedded_frame:
                target_url = embedded_frame.select("./@src").extract()[0]
                tags = classify_and_tag(target_url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
                tags.update(['embedded document', 'iframe'])
                all_tagged_urls.append(make_tagged_url(target_url, title, tags))
            else:
                raise ValueError("This document does not embed an iframe. Please update this parser.")
        elif media_type == 'links':
            links = item.select("./span/a")
            for l in links:
                title, url = extract_title_and_url(l)
                tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
                all_tagged_urls.append(make_tagged_url(url, title, tags))
        else:
            raise ValueError("Unknown media type ('{0}') detected. Please update this parser.".format(media_type))

    return all_content_paragraphs, all_tagged_urls



LINK_TYPE_TO_TAG = {
    'media-video':['video'],
    'media-press':[],
}


def extract_associated_links(hxs, source_url):
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

            all_tagged_urls.append(make_tagged_url(url, title, tags))

    media_links = hxs.select("//div[@id='picture']/descendant::div[@class='bloc-01 pf_article']//a")

    if media_links:
        for i, item in enumerate(media_links):
            item_id = item.select("./@href").extract()
            url = u"{0}{1}".format(source_url, item_id)
            title = u"EMBEDDED MEDIA {0}".format(i)
            tags = set(['media', 'embedded'])
            all_tagged_urls.append(make_tagged_url(url, title, tags))

    return all_tagged_urls



def is_page_error_404(hxs):
    return hxs.select("//head/title/text()").extract() == '404'



def extract_article_data(source_url):
    """
    """
    source_url = codecs.encode(source_url, 'utf-8')

    html_content = fetch_html_content(source_url)
    hxs = HtmlXPathSelector(text=html_content)

    if is_page_error_404(hxs):
        return None, html_content
    else:
        category = hxs.select("//p[starts-with(@class, 'fil_ariane')]/a//text()").extract()
        title = hxs.select("//div[@id='article']/h1/text()").extract()[0]
        pub_date, pub_time = extract_date(hxs)
        author = hxs.select("//p[@class='auteur']/text()").extract()[0]
        fetched_datetime = datetime.today()

        intro, intro_links = extract_intro_and_links(hxs)

        content, content_links = extract_content_and_links(hxs)

        associated_links = extract_associated_links(hxs, source_url)

        all_links = intro_links + content_links + associated_links


        return (ArticleData(source_url, title, pub_date, pub_time, fetched_datetime,
                            all_links,
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



def get_frontpage_toc():
    BASE_URL = u'http://www.sudinfo.be/'
    html_content = fetch_content_from_url(BASE_URL)
    hxs = HtmlXPathSelector(text=html_content)

    column1_headlines = hxs.select("//div[starts-with(@class, 'first-content')]//div[starts-with(@class, 'article')]//h2/a")
    column3_headlines =  hxs.select("//div[@class='octetFun']/a/child::h3/..")
    buzz_headlines = hxs.select("//div[@class='buzz exergue clearfix']//h2/a")
    buzz_headlines.extend(hxs.select("//div[@class='buzz exergue clearfix']//li/a"))

    all_link_selectors = chain(column1_headlines, column3_headlines, buzz_headlines)
    headlines = [extract_title_url_from_hxs_a(link_selector) for link_selector in all_link_selectors]

    regional_headlines = get_regional_toc()
    headlines.extend(regional_headlines)

    return make_full_url(BASE_URL, headlines), []



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
    filepath = '../../sample_data/sudpresse_some_error.html'
    filepath = '../../sample_data/sudpresse_associated_link_error.html'
    with open(filepath) as f:
        article_data, raw = extract_article_data(f)
        article_data.print_summary()

        for link in article_data.links:
            print link.title

        print article_data.intro
        print article_data.content


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
        u"http://www.sudinfo.be/522139/article/regions/bruxelles/2012-09-15/victor-3-ans-s’echappe-de-son-ecole-et-se-retrouve-au-milieu-d’un-carrefour"
        ]

    for url in urls[-1:]:
        article_data, raw_html = extract_article_data(url)

        if article_data:
            article_data.print_summary()
            print article_data.intro
            print article_data.content

            for tagged_url in article_data.links:
                print u"{0} [{1}] {2!r}".format(*tagged_url)
        else:
            print 'no article found'





def show_frontpage_toc():
    headlines, blogposts = get_frontpage_toc()

    for title, url in headlines:
        print u"{0} \t\t\t\t\t [{1}]".format(title, url)

    print len(headlines)


if __name__=='__main__':
    #show_frontpage_toc()
    #download_one_article()
    #show_frontpage_articles()
    show_article()