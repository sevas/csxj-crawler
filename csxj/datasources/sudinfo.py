# -*- coding: utf-8 -*-

import sys
from datetime import datetime, date, time
import locale
from itertools import chain
import urllib
from BeautifulSoup import Tag
from scrapy.selector import HtmlXPathSelector
from common.utils import make_soup_from_html_content, fetch_content_from_url, fetch_html_content
from common.utils import extract_plaintext_urls_from_text
from common.utils import remove_text_formatting_markup_from_fragments
from csxj.common.tagging import tag_URL, classify_and_tag, make_tagged_url, TaggedURL
from csxj.db.article import ArticleData


# for datetime conversions
if sys.platform in ['linux2', 'cygwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF8')
elif sys.platform in [ 'darwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR')


SUDINFO_INTERNAL_SITES = {
    'portfolio.sudinfo.be':['internal site', 'images', 'gallery']
}

SUDINFO_OWN_NETLOC = 'sudinfo.be'

SOURCE_TITLE = u"Sud Info"
SOURCE_NAME = u"sudinfo"

def extract_category(content):
    breadcrumbs = content.find('p', {'class':'ariane'})
    if breadcrumbs:
        return [link.contents[0].strip() for link in breadcrumbs.findAll('a')]
    else:
        alternate_breadcrumbs = content.find('p', {'class':'fil_ariane left'})
        return [link.contents[0].strip() for link in alternate_breadcrumbs.findAll('a')]


def extract_title(article):
    return article.h1.contents[0].strip()



def extract_date(article):
    pub_date_container = article.find('p', {'class':'publiele'})

    today = datetime.today()

    date_string = pub_date_container.span.contents[0]
    d, m = [int(i) for i in date_string.split('/')]
    pub_date = date(today.year, m, d)

    hour, minutes = pub_date_container.contents[2], pub_date_container.contents[4]
    h = int(hour.split(u'à')[1])
    m = int(minutes)
    pub_time = time(h, m)

    return pub_date, pub_time



def extract_author_name(article):
    return article.find('p', {'class':'auteur'}).contents[0].strip()



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



def extract_intro_and_links(article):
    intro_container = article.find('p', {'class':'chapeau'})
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


def extract_associated_links(article):
    links_block = article.find('div', {'class':'bloc-01'})

    if links_block:
        link_list = links_block.find('ul')


        def extract_url_and_title(item):
            url = item.a.get('href')
            title = remove_text_formatting_markup_from_fragments(item.a.contents)

            tags = set()
            if not title:
                title = u'No Title'
                tags.add('ghost link')
            return url, title, tags

        all_tagged_urls = list()
        for item in link_list.findAll('li'):
            url, title, tags = extract_url_and_title(item)
            tags.update(classify_and_tag(url, SUDINFO_OWN_NETLOC, SUDINFO_INTERNAL_SITES))

            link_type = item.get('class')
            if  link_type in LINK_TYPE_TO_TAG:
                tags.update(LINK_TYPE_TO_TAG[link_type])

            all_tagged_urls.append(make_tagged_url(url, title, tags))

        return all_tagged_urls
    else:
        return []


def is_page_error_404(soup):

    return soup.head.title.contents[0] == '404'



def extract_article_data(source):
    """
    """
    if hasattr(source, 'read'):
        html_content = source.read()
    else:
        html_content = fetch_html_content(source)

    soup = make_soup_from_html_content(html_content)


    if is_page_error_404(soup):
        return None, html_content
    else:
        content = soup.find('div', {'id':'content'})
        category = extract_category(content)

        article = soup.find('div', {'id':'article'})
        title = extract_title(article)
        pub_date, pub_time = extract_date(article)
        author = extract_author_name(article)

        fetched_datetime = datetime.today()

        intro, intro_links = extract_intro_and_links(article)
        content, content_links = extract_content_and_links(article)

        associated_links = extract_associated_links(article)

        return ArticleData(source, title, pub_date, pub_time, fetched_datetime,
                           intro_links + content_links + associated_links,
                           category, author,
                           intro, content), html_content



def extract_title_and_url(container):
    if container.h1 and container.h1.a:
        link = container.h1.a
        return link.contents[0].strip(), link.get('href')


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


def download_one_article():
    url = 'http://www.sudpresse.be/regions/liege/2012-01-09/liege-un-mineur-d-age-et-un-majeur-apprehendes-pour-un-viol-collectif-930314.shtml'
    url = 'http://sudpresse.be/actualite/dossiers/2012-01-02/le-stage-du-standard-a-la-manga-infos-photos-tweets-928836.shtml'
    #url = 'http://sudpresse.be/%3C!--%20error:%20linked%20page%20doesn\'t%20exist:...%20--%3E'
    url = "http://sudpresse.be/actualite/faits_divers/2012-01-10/un-enfant-de-4-ans-orphelin-sa-mere-a-saute-sur-les-voies-pour-recuperer-son-gsm-930520.shtml"
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
    show_frontpage_toc()
    #download_one_article()