"""
Frontpage and article scrapping module for the new version of www.lesoir.be (as of oct 2, 2012)
"""

import itertools
from urllib2 import urlparse

from scrapy.selector import HtmlXPathSelector
from csxj.common.tagging import tag_URL, classify_and_tag, make_tagged_url, TaggedURL
from csxj.db.article import ArticleData
from common.utils import fetch_html_content
from common.utils import setup_locales


setup_locales()

SOURCE_TITLE = u"Le Soir"
SOURCE_NAME = u"lesoir2"

LESOIR2_NETLOC = 'www.lesoir.be'


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
    return urlparse.urljoin("http://{0}".format(LESOIR2_NETLOC), url)


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
    titles_and_urls = [extract_title_and_url(link) for link in all_links_hxs]

    articles_toc, blogpost_toc = separate_news_and_blogposts(titles_and_urls)
    return [(title, reconstruct_full_url(url)) for (title, url) in articles_toc], blogpost_toc


if __name__ == "__main__":
    toc, blogposts = get_frontpage_toc()
    for t, u in toc:
        print u"{0} ({1})".format(t, u)

    print len(toc), len(blogposts)
