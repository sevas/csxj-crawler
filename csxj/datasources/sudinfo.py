# -*- coding: utf-8 -*-

import sys
from datetime import datetime
import locale
from itertools import chain
import urllib
import codecs

from BeautifulSoup import Tag
from scrapy.selector import HtmlXPathSelector

from common.utils import make_soup_from_html_content, fetch_content_from_url, fetch_html_content
from common.utils import extract_plaintext_urls_from_text
from common.utils import remove_text_formatting_markup_from_fragments
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
    'portfolio.sudpresse.be':['internal site', 'images', 'gallery']
}

SUDINFO_OWN_NETLOC = 'sudinfo.be'

SOURCE_TITLE = u"Sud Info"
SOURCE_NAME = u"sudinfo"


def extract_date(hxs):
    today = datetime.today()

    date_string = u"".join(hxs.select("//p[@class='publiele']//text()").extract())
    date_bytestring = codecs.encode(date_string, 'utf-8')
    date_fmt = codecs.encode(u"Publié le %A %d %B %Y à %Hh%M", 'utf-8')

    datetime_published = datetime.strptime(date_bytestring, date_fmt)

    return datetime_published.date(), datetime_published.time()


def extract_text_and_links_from_paragraph(paragraph):
    def extract_url_and_title(link):
        if isinstance(link.contents[0], Tag):
            if link.contents[0].name == 'img':
                img_target = link.contents[0].get('src')
                return link.get('href'), '(img){0}'.format(img_target)
            else:
                title = remove_text_formatting_markup_from_fragments(link.contents)
                return link.get('href'), title
        else:
            return link.get('href'), remove_text_formatting_markup_from_fragments(link.contents)

    # Why do we filter on link.contents? Because sometimes there
    # are <a id="more"></a> links which point to nothing.
    # Awesome.
    urls_and_titles = [extract_url_and_title(link) for link in paragraph.findAll('a', recursive=False) if link.contents]

    tagged_urls = list()
    for url, title in urls_and_titles:
        tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
        tags.update(['in text'])
        tagged_urls.append(make_tagged_url(url, title, tags))

    text  = remove_text_formatting_markup_from_fragments(paragraph.contents)


    plaintext_urls = extract_plaintext_urls_from_text(text)
    for url in plaintext_urls:
        tags = classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES)
        tags.update(['plaintext', 'in text'])
        tagged_urls.append(make_tagged_url(url, url, tags))

    return text, tagged_urls



def extract_intro_and_links(hxs):
    intro_container = hxs.select("//p[@class='chapeau']/text()")
    intro_text, tagged_urls = extract_text_and_links_from_paragraph(intro_container)
    return intro_text, tagged_urls



def extract_content_and_links(article):
    all_paragraphs = article.findAll('p', recursive=False)

    content_paragraphs = [p for p in all_paragraphs if p.get('class') not in ['ariane', 'chapeau', 'auteur', 'publiele']]

    all_content_paragraphs = list()
    all_tagged_urls = list()
    for p in content_paragraphs:
        cleaned_up_text, tagged_urls = extract_text_and_links_from_paragraph(p)
        all_content_paragraphs.append(cleaned_up_text)
        all_tagged_urls.extend(tagged_urls)

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
            url = "{0}{1}".format(source_url, item)
            title = "EMBEDDED MEDIA {0}".format(i)
            tags = set(['media', 'embedded'])


    print all_tagged_urls

    return all_tagged_urls


def is_page_error_404(hxs):
    return hxs.select("//head/title/text()").extract() == '404'



def extract_article_data(source_url):
    """
    """
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

#        intro, intro_links = extract_intro_and_links(hxs)
#        content, content_links = extract_content_and_links(article)

        associated_links = extract_associated_links(hxs, source_url)

        return ArticleData(source_url, title, pub_date, pub_time, fetched_datetime,
                           intro_links + content_links + associated_links,
                           category, author,
                           intro, content), html_content



def extract_title_and_url(container):
    if container.h1 and container.h1.a:
        link = container.h1.a
        return link.contents[0].strip(), link.get('href')





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
    BASE_URL = 'http://www.sudinfo.be/'
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
    for title, url in toc[:]:
        print
        print url
        article_data, html_content = extract_article_data(url)

        article_data.print_summary()
        print article_data.to_json()



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
    url = "http://www.sudinfo.be/336280/article/sports/foot-belge/anderlecht/2012-02-26/lierse-anderlecht-les-mauves-vont-ils-profiter-de-la-defaite-des-brugeois"
    url = "http://www.sudinfo.be/335985/article/sports/foot-belge/charleroi/2012-02-26/la-d2-en-direct-charleroi-gagne-en-l-absence-d-abbas-bayat-eupen-est-accro"
    article_data, raw_html = extract_article_data(url)

    if article_data:
        article_data.print_summary()
        print article_data.intro
        print article_data.content
    else:
        print 'no article found'





def show_frontpage_toc():
    headlines, blogposts = get_frontpage_toc()

    for title, url in headlines:
        print u"{0} \t\t\t\t\t [{1}]".format(title, url)



if __name__=='__main__':
    #download_one_article()
    #show_frontpage_articles()
    show_article()