import urllib
from BeautifulSoup import BeautifulSoup

def fetch_content_from_url(url):
    response = urllib.urlopen(url)
    return response.read()


def fetch_html_content(url):
    return fetch_content_from_url(url)


def fetch_html_content_with_redirection(url):
    pass


def fetch_rss_content(url):
    return fetch_content_from_url(url)



def make_soup_from_html_content(html_content, convert_entities=True):
    if convert_entities:
        return BeautifulSoup(html_content, convertEntities=BeautifulSoup.HTML_ENTITIES)
    else:
        return BeautifulSoup(html_content)
