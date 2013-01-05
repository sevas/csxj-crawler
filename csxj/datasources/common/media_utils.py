"""
Note: functions listed here depends on BeautifulSoup3.x interfaces
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from csxj.common.tagging import classify_and_tag, make_tagged_url
from utils import remove_text_formatting_markup_from_fragments

import twitter_utils


def extract_url_from_iframe(iframe):
    url = iframe.get('src')
    title = url
    return url, title


def extract_tagged_url_from_embedded_script(script_parent, site_netloc, site_internal_sites):
    if script_parent.find('script').get('src'):
        script_url = script_parent.find('script').get('src')
        if twitter_utils.is_twitter_widget_url(script_url):
            title, url, tags = twitter_utils.get_widget_type(script_parent.findAll('script')[1].contents[0])
            tags |= classify_and_tag(url, site_netloc, site_internal_sites)
            tags |= set(['script', 'embedded'])
            return make_tagged_url(url, title, tags)
        else:
            if script_parent.find('noscript'):
                noscript = script_parent.find('noscript')
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
                raise ValueError("Embedded script of unknown type was detected ('{0}'). Update the parser.".format(script_url))
    else:
        raise ValueError("Could not extract fallback noscript url for this embedded javascript object. Update the parser.")
