# coding=utf-8

import urllib2
import urlparse
import re
import random
from datetime import datetime

from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import bs4

from useragents import USER_AGENT_STRINGS
from icann_tlds import TLD_LIST


def pick_random_ua_string():
    index = random.randint(0, len(USER_AGENT_STRINGS) - 1)
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


# regexp from:  http://daringfireball.net/2010/07/improved_regex_for_matching_urls
url_regexp = r'''(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))'''
URL_MATCHER = re.compile(url_regexp)

NETLOC_REGEXP = r'[a-z0-9.\-]+[.][a-z]{2,4}'
NETLOC_MATCHER = re.compile(NETLOC_REGEXP)


def strip_matching_parenthesis(text):
    """
    >>> strip_matching_parenthesis("(foo)")
    'foo'

    >>> strip_matching_parenthesis("foo")
    'foo'

    >>> strip_matching_parenthesis("foo)")
    'foo)'

    >>> strip_matching_parenthesis("(foo")
    '(foo'
    """
    if text.startswith('(') and text.endswith(')'):
        return text[1:-1]
    return text


def is_netloc_part_of_mail_address(text, netloc):
    """
    >>> is_netloc_part_of_mail_address("blah@foo.com", "foo.com")
    True

    >>> is_netloc_part_of_mail_address("foo.com", "foo.com")
    False

    >>> is_netloc_part_of_mail_address("foo.be@foo.com", "foo.be")
    True

    >>> is_netloc_part_of_mail_address("hello foo.be@foo.com world", "foo.be")
    True
    """

    if netloc in text and len(text) >= len(netloc):
        idx = text.find(netloc)
        before = idx - 1
        after = idx + len(netloc)

        if 0 < idx and text[before] == '@':
            return True
        elif after < len(text) and text[after] == '@':
            return True

        return False
    else:
        raise ValueError(u"Netloc {0} not present in text".format(netloc))


def extract_plaintext_urls_from_text(some_text):
    """
    """
    urls = [c[0] for c in URL_MATCHER.findall(some_text)]
    urls = [strip_matching_parenthesis(url) for url in urls]

    for url in urls:
        some_text = some_text.replace(url, '')

    some_text = some_text.lower()
    matched = NETLOC_MATCHER.findall(some_text)
    netloc_urls = [c for c in matched if c and not is_netloc_part_of_mail_address(some_text, c) and c.split('.')[-1] in TLD_LIST]

    return urls + netloc_urls


TEXT_MARKUP_TAGS = ['a', 'b', 'i', 'u', 'em', 'strong', 'tt', 'h1', 'h2', 'h3', 'h4', 'h5', 'span', 'sub', 'sup', 'p', 'img']


def remove_text_formatting_markup(formatted_text_fragment, strip_chars, remove_links):
    """
    Returns the plain text version of a chunk of text formatted with HTML tags.
    Unsupported tags are ignored.
    """

    # A text fragment is either an HTML tag (with its own child text fragments)
    # or just a plain string.
    if isinstance(formatted_text_fragment, Tag) or isinstance(formatted_text_fragment, bs4.Tag):
        # If it's the former, we remove the tag and clean up all its children
        if formatted_text_fragment.name in TEXT_MARKUP_TAGS:
            if formatted_text_fragment.name == 'a' and remove_links:
                return u""
            else:
                return u''.join([remove_text_formatting_markup(f, strip_chars, remove_links) for f in formatted_text_fragment.contents])
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
    return u''.join(remove_text_formatting_markup(f, strip_chars, remove_links=False) for f in fragments)


def remove_text_formatting_and_links_from_fragments(fragments, strip_chars=''):
    """
    cleans up the html markup and links from a collection of fragments
    """
    return u''.join(remove_text_formatting_markup(f, strip_chars, remove_links=True) for f in fragments)


def setup_locales():
    import locale
    import sys
    # for datetime conversions
    if sys.platform in ['linux2', 'cygwin']:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF8')
    elif sys.platform in ['darwin']:
        locale.setlocale(locale.LC_TIME, 'fr_FR')
    elif sys.platform in ['win32']:
        # locale string from: http://msdn.microsoft.com/en-us/library/cdax410z(v=VS.80).aspx
        locale.setlocale(locale.LC_ALL, 'fra')


def is_date_in_range(date_string, date_range):
    start_date_string, end_date_string = date_range

    start_date = datetime.strptime(start_date_string, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_string, "%Y-%m-%d")
    date_to_test = datetime.strptime(date_string, "%Y-%m-%d")

    return date_to_test >= start_date and date_to_test <= end_date


def convert_utf8_url_to_ascii(url):
    """
    taken from http://stackoverflow.com/questions/804336/best-way-to-convert-a-unicode-url-to-ascii-utf-8-percent-escaped-in-python
    """
       # turn string into unicode
    if not isinstance(url, unicode):
        url = url.decode('utf8')

    # parse it
    parsed = urlparse.urlsplit(url)

    # divide the netloc further
    userpass, at, hostport = parsed.netloc.rpartition('@')
    user, colon1, pass_ = userpass.partition(':')
    host, colon2, port = hostport.partition(':')

    # encode each component
    scheme = parsed.scheme.encode('utf8')
    user = urllib2.quote(user.encode('utf8'))
    colon1 = colon1.encode('utf8')
    pass_ = urllib2.quote(pass_.encode('utf8'))
    at = at.encode('utf8')
    host = host.encode('idna')
    colon2 = colon2.encode('utf8')
    port = port.encode('utf8')
    # could be encoded slashes!
    path = '/'.join(urllib2.quote(urllib2.unquote(pce).encode('utf8'), '')
                    for pce in parsed.path.split('/'))
    query = urllib2.quote(urllib2.unquote(parsed.query).encode('utf8'), '=&?/')
    fragment = urllib2.quote(urllib2.unquote(parsed.fragment).encode('utf8'))

    # put it back together
    netloc = ''.join((user, colon1, pass_, at, host, colon2, port))
    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))


if __name__ == '__main__':
    print URL_MATCHER.findall("http://fff.com")
