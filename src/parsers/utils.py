import urllib
from BeautifulSoup import BeautifulSoup
import re


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


URL_MATCHER = re.compile('http://.*')

def strip_punctuation(text):
    punctuation_symbols = ';:,.(){}[]\'\"|\\/!?'
    return text.lstrip(punctuation_symbols).rstrip(punctuation_symbols)

def extract_plaintext_urls_from_text(some_text):
    """
    """
    text_fragments = some_text.split(' ')
    text_fragments = [strip_punctuation(f) for f in text_fragments]
    urls = [f for f in text_fragments if URL_MATCHER.match(f)]
    return urls
    
