#!/usr/bin/env python
# -*- coding: utf-8 -*-

from csxj.common.tagging import classify_and_tag, make_tagged_url
from utils import remove_text_formatting_markup_from_fragments
import media_utils

def extract_tagged_url_from_embedded_item(item_div, site_netloc, site_internal_sites):
    if item_div.iframe:
        url, title = media_utils.extract_url_from_iframe(item_div.iframe)
        all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
        return (make_tagged_url(url, title, all_tags | set(['embedded', 'iframe'])))
    else:
        if item_div.find('div', {'class':'containerKplayer'}):
            if len(item_div.findAll('div', recursive=False)) == 2:
                title_div = item_div.findAll('div', recursive=False)[1]
                title = remove_text_formatting_markup_from_fragments(title_div.contents)
            else:
                title = u"__NO_TITLE__"

            kplayer = item_div.find('div', {'class':'containerKplayer'})

            kplayer_flash = kplayer.find('div', {'class': 'flash_kplayer'})
            url_part1 = kplayer_flash.object['data']
            url_part2 = kplayer_flash.object.find('param', {'name' : 'flashVars'})['value']
            if url_part1 is not None and url_part2 is not None:
                url = "%s?%s" % (url_part1, url_part2)
                all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
                return make_tagged_url(url, title, all_tags | set(['video', 'embedded', 'kplayer']))
            else:
                raise ValueError("We couldn't find an URL in the flash player. Update the parser.")

        elif item_div.find('script'):
            # try to detect a twitter widget
            return media_utils.extract_tagged_url_from_embedded_script(item_div, site_netloc, site_internal_sites)
        else:
            raise ValueError("Unknown media type with class: {0}. Update the parser.".format(item_div.get('class')))
