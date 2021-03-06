"""
Note: functions listed here depends on BeautifulSoup3.x interfaces
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urlparse import urlparse

from csxj.common.tagging import classify_and_tag, make_tagged_url
from utils import remove_text_formatting_markup_from_fragments

import twitter_utils


def extract_url_from_iframe(iframe):
    url = iframe.get('src')
    title = url
    return url, title


def clean_snippet(snippet):
    return ''.join(c for c in snippet if c not in u' \n\t').lower()


IGNORED_JS_SNIPPETS = [
    clean_snippet(u"""
            // default textHighlight call
            textHighlight();
     """),
    clean_snippet(u"""
            setTimeout(' document.location=document.location' ,45000);
    """)
]


def ignore_snippet(snippet):
    #print type(snippet)
    for s in IGNORED_JS_SNIPPETS:
        if clean_snippet(snippet) == s:
            return True
    return False



def extract_tagged_url_from_embedded_script(script, site_netloc, site_internal_sites):
    if script.get('src'):
        script_url = script.get('src')
        if twitter_utils.is_twitter_widget_url(script_url):
            if script.contents:
                title, url, tags = twitter_utils.get_widget_type(script.contents[0])
            else:
                # sometimes the TWTR.Widget code is in the next <script> container. Whee.
                sibling_script = script.findNextSibling('script')
                title, url, tags = twitter_utils.get_widget_type(sibling_script.contents[0])
            tags |= classify_and_tag(url, site_netloc, site_internal_sites)
            tags |= set(['script', 'embedded'])
            return make_tagged_url(url, title, tags)
        else:
            if script.findNextSibling('noscript'):
                noscript = script.findNextSibling('noscript')
                link = noscript.find('a')
                if link:
                    url = link.get('href')
                    title = remove_text_formatting_markup_from_fragments(link.contents)
                    all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
                    all_tags |= set(['script', 'embedded'])
                    return make_tagged_url(url, title, all_tags)
                else:
                    raise ValueError("No link was found in the <noscript> section. Update the parser.")
            else:
                raise ValueError("Could not extract fallback noscript url for this embedded javascript object. Update the parser.")
    else:
        raise ValueError("Embedded script of unknown type was detected. Update the parser.")


def extract_source_url_from_dewplayer(dewplayer_link):
    """
        Extracts the source url from a DewPlayer query
        (e.g. "http://download.saipm.com/flash/dewplayer/dewplayer.swf?mp3=http://podcast.dhnet.be/articles/audio_dh_388635_1331708882.mp3")
    """
    _, _, _, _, query, _ = urlparse(dewplayer_link)
    k, v = query.split('=')
    if k == 'mp3':
        return v
    else:
        raise ValueError("A DewPlayer object was instantiated with an unhandled query. Fix your parser")


def extract_source_url_from_bs3_youtube_object(bs3_youtube_object):
    """ Extracts the source url from an embedded youtube object (parsed By BeautifulSoup3)"""
    if bs3_youtube_object.a:
        return bs3_youtube_object.a.get('href')
    elif bs3_youtube_object.get('data'):
        data = bs3_youtube_object.get('data')
        if data.startswith('http'):
            return data
        else:
            raise ValueError("The data attribute of that youtube object does not look like a url. Update the parser.")
    else:
        raise ValueError("Could not find a source url for this youtube object" )
