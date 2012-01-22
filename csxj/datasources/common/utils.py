import urllib2
import re
import random
from BeautifulSoup import BeautifulSoup, Tag
from useragents import USER_AGENT_STRINGS


def pick_random_ua_string():
    index = random.randint(0, len(USER_AGENT_STRINGS))
    return USER_AGENT_STRINGS[index]


def fetch_content_from_url(url):
    request = urllib2.Request(url)
    request.add_header('User-agent', pick_random_ua_string())
    response = urllib2.urlopen(request)
    return response.read()


def fetch_html_content(url):
    return fetch_content_from_url(url)


def fetch_rss_content(url):
    return fetch_content_from_url(url)


def make_soup_from_html_content(html_content, convert_entities=True):
    if convert_entities:
        return BeautifulSoup(html_content, convertEntities=BeautifulSoup.HTML_ENTITIES)
    else:
        return BeautifulSoup(html_content)


URL_MATCHER = re.compile(r'\(?\bhttp://[-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|]') #comes from http://www.codinghorror.com/blog/2008/10/the-problem-with-urls.html

def strip_matching_parenthesis(text):
    if text.startswith('(') and text.endswith(')'):
        return text[1:-1]
    return text

def extract_plaintext_urls_from_text(some_text):
    """
    """
    urls = URL_MATCHER.findall(some_text)
    urls = [strip_matching_parenthesis(url) for url in urls]
    return urls


TEXT_MARKUP_TAGS = ['a', 'b', 'i', 'u', 'em', 'strong', 'tt', 'h1',  'h2',  'h3',  'h4',  'h5', 'span', 'sub', 'sup', 'p' ]

def remove_text_formatting_markup(formatted_text_fragment, strip_chars):
    """
    Returns the plain text version of a chunk of text formatted with HTML tags.
    Unsupported tags are ignored.
    """

    # A text fragment is either an HTML tag (with its own child text fragments)
    # or just a plain string.
    if isinstance(formatted_text_fragment, Tag):
        # If it's the former, we remove the tag and clean up all its children
        if formatted_text_fragment.name in TEXT_MARKUP_TAGS:
            return u''.join([remove_text_formatting_markup(f, strip_chars) for f in formatted_text_fragment.contents])
        # sometimes we get embedded <objects>, just ignore it
        else:
            return u''
    # If it's a plain string, we just strip
    else:
        return formatted_text_fragment.strip(strip_chars)



def remove_text_formatting_markup_from_fragments(fragments, strip_chars=''):
    """
    cleans up the html markup from a collection of fragments
    """
    return u''.join(remove_text_formatting_markup(f, strip_chars) for f in fragments)
