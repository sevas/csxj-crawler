#!/usr/bin/env python
# -*- coding: utf-8 -*-

from csxj.common.tagging import classify_and_tag, make_tagged_url
from utils import remove_text_formatting_markup_from_fragments, remove_text_formatting_and_links_from_fragments, extract_plaintext_urls_from_text
import media_utils
import constants

IPM_SAME_OWNER = [
    'essentielle.be',
    'tribunedebruxelles.be',
    'twizzradio.be',
    'cielradio.be',
    'cinebel.be',
    'tremplinpourlemploi.be',
    'betfirst.dhnet.be',
    'goodeal.lalibre.be'
]
DHNET_SAME_OWNER = []
DHNET_SAME_OWNER.extend(IPM_SAME_OWNER)
DHNET_SAME_OWNER.append("lalibre.be")
LALIBRE_SAME_OWNER = []
LALIBRE_SAME_OWNER.extend(IPM_SAME_OWNER)
LALIBRE_SAME_OWNER.append("dhnet.be")


def extract_kplayer_infos(kplayer_flash, title, site_netloc, site_internal_sites):
    url_part1 = kplayer_flash.object['data']
    url_part2 = kplayer_flash.object.find('param', {'name': 'flashVars'})['value']
    if url_part1 is not None and url_part2 is not None:
        url = "%s?%s" % (url_part1, url_part2)
        all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
        return make_tagged_url(url, title, all_tags | set(['video', 'embedded', 'kplayer']))
    else:
        raise ValueError("We couldn't find an URL in the flash player. Update the parser.")


def extract_url_and_title(bslink):
    url = bslink.get('href')
    if bslink.contents:
        title = remove_text_formatting_markup_from_fragments(bslink.contents)
    else:
        title = constants.NO_TITLE
    return url, title


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
            return extract_kplayer_infos(kplayer_flash, title, site_netloc, site_internal_sites)

        elif item_div.find('embed') and item_div.find('embed').get('src').startswith("http://www.divertissonsnous.com"):
            url = item_div.div.find('a').get('href')
            title = item_div.div.find('a').contents[0]
            all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
            tagged_url = make_tagged_url(url, title, all_tags | set(['embedded', 'video']))
            return tagged_url

        elif item_div.find('div', {'class': 'flash_kplayer'}):
            kplayer_flash = item_div.find('div', {'class': 'flash_kplayer'})
            return extract_kplayer_infos(kplayer_flash, "__NO_TITLE__", site_netloc, site_internal_sites)

        #it's a tweet
        elif item_div.find('a', {'class': 'twitter-timeline'}):
            url = item_div.find('a', {'class': 'twitter-timeline'}).get('href')
            title = item_div.find('a', {'class': 'twitter-timeline'}).contents[0]
            all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
            tagged_url = make_tagged_url(url, title, all_tags | set(['embedded', 'tweet']))
            return tagged_url

        elif item_div.find('div', {'class': 'visually_embed'}):
            if item_div.find("a", {'id': 'visually_embed_view_more'}).get('href'):
                url = item_div.find("a", {'id': 'visually_embed_view_more'}).get('href')
                all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
                tagged_url = make_tagged_url(url, url, all_tags | set(['embedded']))
                return tagged_url
            else:
                raise ValueError("Looks like a visual.ly splendid dataviz, but it does not match known patterns")

        # it might be a hungarian video, or any other type of player
        elif item_div.object:
            container = item_div.object
            value = container.find("param", {"name": "movie"}).get('value')

            if value.startswith("http://www.youtube.com"):
                url = value
                all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
                tagged_url = make_tagged_url(url, url, all_tags | set(['embedded', 'video']))
                return tagged_url

            elif value.startswith("http://videa.hu/"):
                if container.findNextSibling('a'):
                    url = container.findNextSibling('a').get('href')
                    indigenous_title = container.findNextSibling('div').contents[0]
                    original_title = container.findNextSibling('a').get('title')
                    alternative_title = container.findNextSibling('a').contents[0]
                    all_tags = classify_and_tag(url, site_netloc, site_internal_sites)

                    if container.findNextSibling('div').contents[0]:
                        tagged_url = make_tagged_url(url, indigenous_title, all_tags | set(['embedded', 'video']))
                        return tagged_url

                    elif container.findNextSibling('a').get('title'):
                        tagged_url = make_tagged_url(url, original_title, all_tags | set(['embedded', 'video']))
                        return tagged_url

                    elif container.findNextSibling('a').contents[0]:
                        tagged_url = make_tagged_url(url, alternative_title, all_tags | set(['embedded', 'video']))
                        return tagged_url

                    else:
                        tagged_url = make_tagged_url(url, "__NO_TITLE__", all_tags | set(['embedded', 'video']))
                        return tagged_url
                else:
                    raise ValueError("It looks like a Hungarian video but it did not match known patterns")

            elif value.startswith("http://www.pixule.com"):
                if container.find("embed"):
                    url = container.find("embed").get("src")
                    all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
                    tagged_url = make_tagged_url(url, url, all_tags | set(['embedded', 'poll']))
                    return tagged_url
                else:
                    raise ValueError("It looks like a Pixule poll  but it did not match known patterns")

            elif value.startswith("http://vocaroo.com"):
                if container.find("embed"):
                    url = container.find("embed").get("src")
                    all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
                    tagged_url = make_tagged_url(url, url, all_tags | set(['embedded', 'audio']))
                    return tagged_url
                else:
                    raise ValueError("It looks like a Voocaroo audio clip but it did not match known patterns")

            elif value.startswith("http://www.wat.tv"):
                if item_div.find("div", {'class': 'watlinks'}):
                    watlinks = item_div.find("div", {'class': "watlinks"})
                    url = watlinks.find('a').get('href')
                    title = watlinks.find('a').get('title')
                    all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
                    tagged_url = make_tagged_url(url, title, all_tags | set(['embedded', 'video']))
                    return tagged_url

                else:
                    raise ValueError("It looks like a wat.tv video but it did not match known patterns")


            elif value.startswith("http://c.brightcove.com"):
                if item_div.find("param", {"name": "flashVars"}):
                    flashvars = item_div.find("param", {"name": "flashVars"})
                    all_parts = flashvars.get("value")
                    parsed_flashvars = all_parts.split('&')
                    
                    d = dict()
                    for var in parsed_flashvars:
                        splitted = var.split('=')
                        if len(splitted) == 2:
                            name, value = splitted
                        elif len(splitted) > 2:
                            name, value = splitted[0], '='.join(splitted[1:])
                        else:
                            raise ValueError()
                        d[name] = value

                    if 'playerID' in d and 'videoId' in d:
                        url = "http://link.brightcove.com/services/player/bcpid{0}?bctid={1}" .format(d['playerID'],d['videoId'])
                        all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
                        tagged_url = make_tagged_url(url, url, all_tags | set(['embedded', 'video']))
                        return tagged_url
                    else:
                        raise ValueError()
                else:
                    raise ValueError("It looks like a Brightcove video but it did not match known patterns")

            elif value.startswith("http://www.meltybuzz.fr/"):
                url = item_div.span.a.get("href")
                title = item_div.span.a.get("title")
                all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
                tagged_url = make_tagged_url(url, title, all_tags | set(['embedded', 'video']))
                return tagged_url

            elif value.startswith("http://player.canalplus.fr"):
                param = container.find('param', {'name': 'flashvars'})
                if param:
                    itele_div = container.parent.findNextSibling('div')
                    if itele_div:
                        url, title = extract_url_and_title(itele_div.a)
                        tags = classify_and_tag(url, site_netloc, site_internal_sites)
                        tags |= set(['embedded', 'video'])
                        return make_tagged_url(url, title, tags)
                    else:
                        raise ValueError('Could not find the itele.fr video link from that canaplus.fr embedded video')
                else:
                    raise ValueError("It looks like a canalplus.fr video but it did not match known patterns")

            else:
                raise ValueError("There seems to be a hungarian video or something but it didn't match known patterns")

        elif item_div.find('script'):
            if len(item_div.find('script').contents) > 0 :
                if "vmmaplayer" in item_div.find('script').contents[0]:
                    url = item_div.find('script').contents[0].split("videoUrl:'")[1].split("',width")[0]
                    all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
                    tagged_url = make_tagged_url(url, url, all_tags | set(['embedded', 'video']))
                    return tagged_url
            elif item_div.find('script').get('src').startswith("http://player.ooyala.com"):
                if item_div.find('script').get('src').startswith("http://player.ooyala.com"):
                    url_js = item_div.find('script').get('src')
                    url = url_js.replace("iframe.js", "iframe.html")
                    all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
                    tagged_url = make_tagged_url(url, url, all_tags | set(['embedded', 'video']))
                    return tagged_url
            else:
                return media_utils.extract_tagged_url_from_embedded_script(item_div.find('script'), site_netloc, site_internal_sites)      
        else:
            def test_for_plaintext_url(embed_contents):
                fragment = remove_text_formatting_and_links_from_fragments(embed_contents)
                url = extract_plaintext_urls_from_text(fragment)
                return url
            if test_for_plaintext_url(item_div):
                url = test_for_plaintext_url(item_div)[0]
                all_tags = classify_and_tag(url, site_netloc, site_internal_sites)
                tagged_url = make_tagged_url(url, url, all_tags | set(['embedded', 'plaintext']))
                return tagged_url

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
                tags |= set(['sidebar box', 'audio', 'embedded'])
                tagged_url = make_tagged_url(source_url, title, tags)
                tagged_urls.append(tagged_url)
            else:
                raise ValueError("Could not find the source url for the flash object. Fix your parser.")
        else:
            raise ValueError("Could not find the flash object for embedded audio. Fix your parser.")

    return tagged_urls
