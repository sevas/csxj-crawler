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
        if item_div.find('div', {'class': 'containerKplayer'}):
            if len(item_div.findAll('div', recursive=False)) == 2:
                title_div = item_div.findAll('div', recursive=False)[1]
                title = remove_text_formatting_markup_from_fragments(title_div.contents)
            else:
                title = u"__NO_TITLE__"

            kplayer = item_div.find('div', {'class': 'containerKplayer'})

            kplayer_flash = kplayer.find('div', {'class': 'flash_kplayer'})
            url_part1 = kplayer_flash.object['data']
            url_part2 = kplayer_flash.object.find('param', {'name': 'flashVars'})['value']
            if url_part1 is not None and url_part2 is not None:
                url = "%s?%s" % (url_part1, url_part2)
                all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
                return make_tagged_url(url, title, all_tags | set(['video', 'embedded', 'kplayer']))
            else:
                raise ValueError("We couldn't find an URL in the flash player. Update the parser.")

        elif item_div.find('script'):
            # try to detect a <script>
            return media_utils.extract_tagged_url_from_embedded_script(item_div.find('script'), site_netloc, site_internal_sites)
        else:
            raise ValueError("Unknown media type with class: {0}. Update the parser.".format(item_div.get('class')))


def extract_tagged_url_from_associated_link(link_list_item, netloc, associated_sites, additional_tags=[]):
    # sometimes list items are used to show things which aren't links
    # but more like unclickable ads
    url = link_list_item.a.get('href')
    title = remove_text_formatting_markup_from_fragments(link_list_item.a.contents).strip()
    tags = classify_and_tag(url, netloc, associated_sites)
    tags |= set(additional_tags)
    tagged_url = make_tagged_url(url, title, tags)
    return tagged_url


def extract_and_tag_associated_links(main_content, netloc, associated_sites):
    """
    Extract the associated links. .

    """
    strong_article_links = main_content.find('div', {'id': 'strongArticleLinks'})
    if not strong_article_links:
        return []

    link_list = strong_article_links.find('ul', {'class': 'articleLinks'})
    tagged_urls = []
    # sometimes there are no links, and thus no placeholder
    if link_list:
        for li in link_list.findAll('li', recursive=False):
            if li.a:
                new_url = extract_tagged_url_from_associated_link(li, netloc, associated_sites, additional_tags=['sidebar box'])
                tagged_urls.append(new_url)

    return tagged_urls


def extract_bottom_links(main_content, netloc, associated_sites):
    link_list = main_content.findAll('ul', {'class': 'articleLinks'}, recursive=False)

    tagged_urls = []
    if link_list:
        for li in link_list[0].findAll('li', recursive=False):
            if li.a:
                tagged_urls.append(extract_tagged_url_from_associated_link(li, netloc, associated_sites, additional_tags=['bottom box']))
            else:
                raise ValueError("Found list item without <a> tag")
    return tagged_urls


def extract_embedded_audio_links(main_content, netloc, associated_sites):
    strong_article_links = main_content.find('div', {'id': 'strongArticleLinks'})
    if not strong_article_links:
        return []

    embedded_audio_link_list = strong_article_links.find('ul', {'id': 'audioContents'})

    if not embedded_audio_link_list:
        return []

    tagged_urls = []
    for item in embedded_audio_link_list.findAll('li', recursive=False):
        if item.object:
            flash_obj = item.object
            data_url = flash_obj.get('data')
            if data_url:
                source_url = media_utils.extract_source_url_from_dewplayer(data_url)
                title = item.text
                tags = classify_and_tag(source_url, netloc, associated_sites)
                tags |= set(['sidebar box', 'audio', 'embedded',])
                tagged_url = make_tagged_url(source_url, title, tags)
                tagged_urls.append(tagged_url)
            else:
                raise ValueError("Could not find the source url for the flash object. Fix your parser.")
        else:
            raise ValueError("Could not find the flash object for embedded audio. Fix your parser.")

    return tagged_urls