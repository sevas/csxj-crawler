#!/usr/bin/env python
# -*- coding: utf-8 -*-

from csxj.common.tagging import classify_and_tag, make_tagged_url
from common.utils import remove_text_formatting_markup_from_fragments
import twitter_utils
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
            if item_div.find('script').get('src'):
                script_url = item_div.find('script').get('src')
                if twitter_utils.is_twitter_widget_url(script_url):
                    title, url, tags = twitter_utils.get_widget_type(item_div.findAll('script')[1].contents[0])
                    tags |= classify_and_tag(url, site_netloc, site_internal_sites)
                    tags |= set(['script', 'embedded'])
                    return make_tagged_url(url, title, tags)
                else:
                    if item_div.find('noscript'):
                        noscript = item_div.find('noscript')
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
        else:
            raise ValueError("Unknown media type with class: {0}. Update the parser.".format(div.get('class')))
