#!/usr/bin/env python
# coding=utf-8

from datetime import datetime
import codecs
import itertools as it
from urlparse import urlparse
from scrapy.selector import HtmlXPathSelector

from urllib2 import HTTPError

from csxj.common.tagging import classify_and_tag, make_tagged_url, update_tagged_urls, print_taggedURLs
from csxj.db.article import ArticleData
from parser_tools.utils import fetch_html_content
from parser_tools.utils import extract_plaintext_urls_from_text, setup_locales
from parser_tools.utils import remove_text_formatting_markup_from_fragments, remove_text_formatting_and_links_from_fragments
from parser_tools import constants
from parser_tools import media_utils

setup_locales()

SOURCE_TITLE = u"L'Avenir"
SOURCE_NAME = u"lavenir"

LAVENIR_INTERNAL_BLOGS = {
    'lavenir.newspaperdirect.com': ['internal', 'pdf newspaper']
}

LAVENIR_NETLOC = 'www.lavenir.net'

BLACKLIST = ["http://citysecrets.lavenir.net"]

LAVENIR_SAME_OWNER = [
    'corelioconnect.be',
    'corelioclassifieds.be',
    'travelspotter.be',
    'wematch.be',
    'notarisblad.be',
    'inmemoriam.be',
    'necrologies.net',
    'jobat.be',
    'gezondheid.be',
    'passionsante.be',
    'zimmo.be',
    'immonot.be',
    'vroom.be',
    'siaffinites.be',
    'citysecrets.be',
    'coldsetprintingpartners.be',
    'corelioprinting.be',
    'arco.be',
    'mifratel.be',
    'queromedia.be',
    'xpertize.be',
    'larian.com',
    'wataro.com',
    'domaininvest.lu',
    'oxynade.com',
    'detondeldoos.be',
    'adam.be',
    'standaard.be',
    'nieuwsblad.be',
    'gentenaar.be',
    'sportwereld.be',
    'nostalgie.be',
    'robtv.be',
    'vier.be',
    'vijf.be',
    'humo.be',
    'woestijnvis.be',
    'thebulletin.be',
    'xpats.com',
    'passe-partout.be',
    'passionsante.be',
    'plusplus.be'
]


def is_internal_url(url):
    if url.startswith('/'):
        return True
    else:
        parsed_url = urlparse(url)
        scheme, netloc, path, params, query, fragments = parsed_url
        return LAVENIR_NETLOC.endswith(netloc)


def extract_publication_date(raw_date):
    date_string = raw_date.split(':')[1].strip().split("&")[0]
    date_bytestring = codecs.encode(date_string, 'utf-8')

    date_component_count = len(date_bytestring.split(" "))
    if date_component_count == 4:
        datetime_published = datetime.strptime(date_bytestring, u"%A %d %B %Y")
    elif date_component_count == 5:
        datetime_published = datetime.strptime(date_bytestring, u"%A %d %B %Y %Hh%M")
    else:
        raise ValueError("Date has an unknown format: {0}".format(date_bytestring))

    return datetime_published.date(), datetime_published.time()


def extract_links_from_text_hxs(hxs):
    tagged_urls = list()
    # intext urls: take all the <a>, except what might be inside a rendered tweet

    intext_link_hxs = hxs.select(".//a")
    for link_hxs in intext_link_hxs:
        title, url = extract_title_and_url(link_hxs)
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags.add('in text')
        tagged_urls.append(make_tagged_url(url, title, tags))

    #plaintext text urls
    raw_content = hxs.select(".//p/text()").extract()

    if raw_content:
        for paragraph in raw_content:
            plaintext_urls = extract_plaintext_urls_from_text(remove_text_formatting_and_links_from_fragments(paragraph))
            for url in plaintext_urls:
                tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
                tags.update(['plaintext', 'in text'])
                tagged_urls.append(make_tagged_url(url, url, tags))

    #embedded objects
    iframe_sources = hxs.select(".//iframe/@src").extract()
    for url in iframe_sources:
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags = tags.union(['in text', 'embedded', 'iframe'])
        tagged_urls.append(make_tagged_url(url, url, tags))

    return tagged_urls


def extract_links_from_article_body(article_body_hxs):
    return extract_links_from_text_hxs(article_body_hxs)


IGNORED_EMBED_SOURCES = ['videa.hu', 'meltybuzz.fr', 'canalplus.fr',
                         'brightcove', 'liveleak.com', 'facebook.com/v/',
                         'bimvid.com', 'qik.com']


def should_skip_embed_element(url):
    for ignored_source in IGNORED_EMBED_SOURCES:
        if ignored_source in url:
            return True
    return False


def extract_links_from_video_div(video_div_hxs):
    tagged_urls = list()
    iframes = video_div_hxs.select('.//iframe')
    did_skip_items = False

    for iframe in iframes:

        url = iframe.select('./@src').extract()
        if not url:
            raise ValueError("This iframe has no 'src' attribute. What?")
        else:
            url = url[0]
            tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
            tags |= set(['embedded', 'video'])
            tagged_urls.append(make_tagged_url(url, url, tags))

    objects = video_div_hxs.select('.//object')
    for object_hxs in objects:
        associated_link = object_hxs.select("./following-sibling::a[1]")
        if associated_link:
            title, url = extract_title_and_url(associated_link[0])
        else:
            url = object_hxs.select("./param [@name='movie']/@value").extract()[0]
            if 'canalplus.fr' in url:
                flashvars_str = object_hxs.select("./param [@name='flashvars']/@value").extract()[0]
                url = "{0}?{1}".format(url, flashvars_str)
            title = url
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags |= set(['embedded', 'video'])
        tagged_urls.append(make_tagged_url(url, title, tags))

    embeds = video_div_hxs.select('.//embed')
    for embed_hxs in embeds:
        embed_src = embed_hxs.select('./@src').extract()
        # some were already processed in the <object> loop, we can ignore them.

        if should_skip_embed_element(embed_src[0]):
            continue

        flashvars_str = embed_hxs.select('./@flashvars').extract()
        if flashvars_str:
            flashvars = dict([kv.split('=') for kv in flashvars_str[0].split('&')])

            url = flashvars['playlistfile']
            title = constants.EMBEDDED_VIDEO_TITLE
            tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
            tags |= set(['embedded', 'video'])
            tagged_urls.append(make_tagged_url(url, title, tags))
        else:
            if 'turner.com' in embed_src[0]:
                url = embed_src[0]
                title = constants.EMBEDDED_VIDEO_TITLE
                tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
                tags |= set(['embedded', 'video', constants.UNFINISHED_TAG])
                tagged_urls.append(make_tagged_url(url, title, tags))
            else:
                raise ValueError("Found an <embed> element with no @flashvars")

    scripts = video_div_hxs.select('.//script')
    for script_hxs in scripts:
        script_src = script_hxs.select('./@src').extract()
        if script_src:
            script_src = script_src[0]
            if 'flowplayer' in script_src:
                title = constants.EMBEDDED_VIDEO_TITLE
                url = constants.EMBEDDED_VIDEO_URL
                tags = set(['external', 'embedded', 'video', 'flowplayer', constants.UNFINISHED_TAG])
                tagged_urls.append(make_tagged_url(url, title, tags))
            elif 'jwplay' in script_src:
                title = constants.EMBEDDED_VIDEO_TITLE
                url = constants.EMBEDDED_VIDEO_URL
                tags = set(['external', 'embedded', 'video', 'jwplayer', constants.UNFINISHED_TAG])
                tagged_urls.append(make_tagged_url(url, title, tags))
            elif 'ooyala' in script_src:
                title = constants.EMBEDDED_VIDEO_TITLE
                url = constants.EMBEDDED_VIDEO_URL
                tags = set(['external', 'embedded', 'video', 'ooyala', constants.UNFINISHED_TAG])
                tagged_urls.append(make_tagged_url(url, title, tags))
            elif 'thinglink.' in script_src:
                title = u"__THINGLINK_ANNOTATED_IMAGE__"
                url = script_src
                tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
                tags |= set(['embedded', 'annoted image'])
                tagged_urls.append(make_tagged_url(url, title, tags))
            elif 'storify.com' in script_src:
                url = script_src
                title = constants.RENDERED_STORIFY_TITLE
                tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
                tags |= set(['embedded', 'storify'])
                tagged_urls.append(make_tagged_url(url, title, tags))
            elif 'vtm.be' in script_src:
                url = script_src
                title = constants.EMBEDDED_VIDEO_TITLE
                tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
                tags |= set(['embedded', 'video', 'vtm', constants.UNFINISHED_TAG])
                tagged_urls.append(make_tagged_url(url, title, tags))
            elif 'kewego.com' in script_src:
                url = script_src
                title = constants.EMBEDDED_VIDEO_TITLE
                tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
                tags |= set(['embedded', 'video', 'kewego', constants.UNFINISHED_TAG])
                tagged_urls.append(make_tagged_url(url, title, tags))
            elif 'worldnow.com' in script_src:
                url = script_src
                title = constants.EMBEDDED_VIDEO_TITLE
                tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
                tags |= set(['embedded', 'video', 'worldnow.com', constants.UNFINISHED_TAG])
                tagged_urls.append(make_tagged_url(url, title, tags))
            else:
                raise ValueError("Found a <script> for an embedded video, for an unknown type")

    if tagged_urls or did_skip_items:
        return tagged_urls
    else:
        # Sometimes that video div was there as a placeholder for images.
        # We just ignore them.
        if video_div_hxs.select('.//p/img'):
            return list()
        if video_div_hxs.select('.//a/img'):
            return list()
        if video_div_hxs.select('.//div/img'):
            return list()
        # Could not extract any link? Break everything.
        raise ValueError("There is an embedded video in here somewhere, but it's not an iframe or an object")


def extract_links_from_highlight_section(article_detail_hxs):
    video_div_hxs = article_detail_hxs.select(".//div [@id='video']")

    if not video_div_hxs:
        return list()

    return extract_links_from_video_div(video_div_hxs)


def select_title_and_url(selector, tag_name):
    url = selector.select("./@href").extract()[0]
    title = selector.select(".//text()").extract()
    if title:
        title = remove_text_formatting_markup_from_fragments(title[0])
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags = tags.union([tag_name])
    else:
        tags = set([tag_name, constants.GHOST_LINK_TAG])
        title = constants.GHOST_LINK_TITLE
    return make_tagged_url(url, title, tags)


def extract_sidebar_links(sidebar_links):
    tagged_urls = [select_title_and_url(sidebar_link, 'sidebar box') for sidebar_link in sidebar_links]
    return tagged_urls


def extract_bottom_links(bottom_links):
    tagged_urls = [select_title_and_url(bottom_link, 'bottom box') for bottom_link in bottom_links]
    return tagged_urls


def extract_article_data_old(source, hxs):
    """ process an old-style lavenir.net article page"""
    article_detail_hxs = hxs.select("//div[@id='content']/div[starts-with(@class,'span-3 article-detail')]")

    category = hxs.select("//div[@id='content']/*[1]/p/a/text()").extract()
    intro_h1s = article_detail_hxs.select(".//div[@id='intro']/h1/text()").extract()

    title = ''
    if len(intro_h1s) == 1:
        title = intro_h1s[0].strip()
    else:
        return None, None

    # all the date stuff
    #raw_date = article_detail_hxs.select(".//div[@id='intro']//li[@id='liDate']/*").extract()
    raw_date = ''.join([t.strip() for t in article_detail_hxs.select(".//div[@id='intro']//li[@id='liDate']//text()").extract()])
    pub_date, pub_time = extract_publication_date(raw_date)
    fetched_datetime = datetime.today()

    #author(s)
    raw_author = article_detail_hxs.select("./div/ul/li[@class='author']/text()").extract()
    author = None
    if raw_author:
        author = raw_author[0].strip()

    #intro
    intro = None
    raw_intro = article_detail_hxs.select("./div/div[@class='intro ']//text()").extract()
    if raw_intro:
        intro = ''.join([fragment.strip() for fragment in raw_intro])

    # in photosets pages, the structure is a bit different
    if not intro:
        raw_intro = article_detail_hxs.select("./div/div[@class='intro']//text()").extract()
    if raw_intro:
        intro = ''.join([fragment.strip() for fragment in raw_intro])

    #detect photoset
    full_class = article_detail_hxs.select("./@class").extract()[0]
    if 'article-with-photoset' in full_class.split(" "):
        title = u"{0}|{1}".format("PHOTOSET", title)

    all_links = list()

    #content
    article_body = article_detail_hxs.select("./div/div[@class='article-body ']")
    content = article_body.select(".//p//text()").extract()

    all_links.extend(extract_links_from_article_body(article_body))
    all_links.extend(extract_links_from_highlight_section(article_body.select('../..')))

    # associated sidebar links
    sidebar_links = article_detail_hxs.select("./div/div[@class='article-side']/div[@class='article-related']//li/a")
    all_links.extend(extract_sidebar_links(sidebar_links))

    # bottom links
    bottom_box = hxs.select('//div[@class="span-3 lire-aussi"]//a')
    all_links.extend(extract_bottom_links(bottom_box))

    updated_tagged_urls = update_tagged_urls(all_links, LAVENIR_SAME_OWNER)

    article_data = ArticleData(source, title, pub_date, pub_time, fetched_datetime,
                               updated_tagged_urls,
                               category, author,
                               intro, content)

    return article_data


def datetime_from_iso8601(datetime_string):
    """
    >>> datetime_from_iso8601("2013-03-09T10h24")
    datetime.datetime(2013, 3, 9, 10, 24)
    """
    return datetime.strptime(datetime_string, "%Y-%m-%dT%Hh%M")


def extract_intro_and_links_new(content_hxs):
    intro_hxs = content_hxs.select(".//div [@class='entry-lead']")
    tagged_urls = list()
    intro = u''
    for p_hxs in intro_hxs.select('.//p'):
        text = p_hxs.select('./text()').extract()
        if text:
            intro += text[0]

        tagged_urls.extend(extract_links_from_text_hxs(p_hxs))

    return intro, tagged_urls


def extract_content_and_links_new(content_hxs):
    content = list()
    body_hxs = content_hxs.select(".//div [@class='entry-body']")
    tagged_urls = list()
    for p_hxs in body_hxs.select('./p'):
        text = p_hxs.select('./text()').extract()
        if text:
            content.append(text[0])

        tagged_urls.extend(extract_links_from_text_hxs(p_hxs))

    return content, tagged_urls


def extract_links_from_embbeded_media(content_hxs):
    body_hxs = content_hxs.select(".//div [@class='entry-body']")
    tagged_urls = []
    for script_hxs in body_hxs.select('./script'):
        snippet = script_hxs.select('./text()').extract()

        if len(snippet) > 0 and media_utils.ignore_snippet(snippet[0]):
            continue

        script_src = script_hxs.select("./@src").extract()
        if not script_src:
            raise ValueError("Found a <script> with no src attr.")

        if script_src[0].startswith("//platform.twitter.com/widgets.js"):
            # tagged_urls.append(make_tagged_url(constants.NO_URL, constants.NO_TITLE, set(['embedded', 'tweet', constants.UNFINISHED_TAG])))
            previous_blockquote = script_hxs.select("./preceding-sibling::blockquote[1]")
            if previous_blockquote:
                if 'twitter-tweet' in previous_blockquote[0].select("./@class").extract():
                    url = previous_blockquote.select('./a[last()]/@href').extract()[0]
                    tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
                    title = u"[RENDERED TWEET]"
                    tags |= set(['embedded', 'tweet'])
                    tagged_urls.append(make_tagged_url(url, title, tags))
                else:
                    raise ValueError("This blockquote does not appear to be a tweet.")
            else:
                raise ValueError("Found a twitter widget <script> without its companion blockquote.")
        elif script_src[0].startswith("http://storify.com"):
            url = script_src[0]
            title = constants.RENDERED_STORIFY_TITLE
            tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
            tags |= set(['embedded', 'storify'])
            tagged_urls.append(make_tagged_url(url, title, tags))
        else:
            noscript_hxs = script_hxs.select('./following-sibling::noscript[1]')
            if noscript_hxs:
                link_hxs = noscript_hxs.select('a')
                title, url = extract_title_and_url(link_hxs)
                tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
                title = constants.RENDERED_TWEET_TITLE
                tags |= set(['embedded'])
                tagged_urls.append(make_tagged_url(url, title, tags))
            else:
                raise ValueError("This blockquote does not appear to be a tweet.")

    return tagged_urls


def extract_links_from_other_divs(other_div_hxs):
    tagged_urls = list()

    for div_hxs in other_div_hxs:
        div_id = div_hxs.select("./@id").extract()
        if not div_id:
            continue
        div_id = div_id[0]
        if div_id in ['articlead', 'photoset']:
            continue
        else:
            if div_id == 'video':
                tagged_urls.extend(extract_links_from_video_div(div_hxs))
            else:
                raise ValueError("unknow <div id='{0}'>".format(div_id))

    return tagged_urls


def extract_related_links(hxs):
    aside_hxs = hxs.select("//div//aside [@class='entry-related']")
    tagged_urls = list()
    related_link_hxs = aside_hxs.select(".//ul/li//a")
    for link_hxs in related_link_hxs:
        title, url = extract_title_and_url(link_hxs)
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags |= set(['bottom box', 'related'])
        tagged_urls.append(make_tagged_url(url, title, tags))
    return tagged_urls


def extract_links_from_tags(hxs):
    tag_navbar_hxs = hxs.select("//nav [@class='entry-tags']")
    tagged_urls = list()
    for link_hxs in tag_navbar_hxs.select("./ul/li/a"):
        title, url = extract_title_and_url(link_hxs)
        tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
        tags |= set(['keyword'])
        tagged_urls.append(make_tagged_url(url, title, tags))

    return tagged_urls


def extract_article_data_new_style(source, hxs):
    """ """
    category = hxs.select("//nav [contains(@id,'breadcrumb')]//li").extract()

    datetime_string = hxs.select("//div [@class='row content']//time/@datetime").extract()
    if not datetime_string:
        raise ValueError("Could not find the date, update the parser")

    parsed_datetime = datetime_from_iso8601(datetime_string[0])
    pub_date, pub_time = parsed_datetime.date(), parsed_datetime.time()
    fetched_datetime = datetime.now()

    title = hxs.select("//header//h1/text()").extract()
    if not title:
        raise ValueError()
    title = title[0]

    content_hxs = hxs.select("//div [@class='entry-content']")

    author_fragments = content_hxs.select(".//p [@class='copyright']/text()").extract()
    author = ''.join([remove_text_formatting_markup_from_fragments(author_fragments, strip_chars='\r\n\t ')])

    intro, intro_links = extract_intro_and_links_new(content_hxs)
    content, content_links = extract_content_and_links_new(content_hxs)

    other_div_hxs = content_hxs.select("//div [@class='entry-content']/div [not(contains(@class, 'entry-'))]")
    content_media_links = extract_links_from_other_divs(other_div_hxs)
    related_links = extract_related_links(hxs)
    media_links = extract_links_from_embbeded_media(content_hxs)
    tag_links = extract_links_from_tags(hxs)

    all_links = it.chain(intro_links, content_links, media_links, content_media_links, related_links, tag_links)
    updated_tagged_urls = update_tagged_urls(all_links, LAVENIR_SAME_OWNER)

    article_data = ArticleData(source, title, pub_date, pub_time, fetched_datetime,
                               updated_tagged_urls,
                               category, author,
                               intro, content)
    return article_data


def extract_article_data(source):
    if hasattr(source, 'read'):
        html_content = source.read()
    else:
        try:
            html_content = fetch_html_content(source)
        except HTTPError as e:
            if e.code == 404 or e.code == 403:
                return None, None
            else:
                raise
        except Exception:
            raise

    hxs = HtmlXPathSelector(text=html_content)

    old_style_content_hxs = hxs.select("//div[@id='content']")

    if old_style_content_hxs:
        return extract_article_data_old(source, hxs), html_content
    else:
        return extract_article_data_new_style(source, hxs), html_content


def expand_full_url(local_url):
    if not local_url.startswith("http://"):
        return "http://{0}{1}".format(LAVENIR_NETLOC, local_url)
    else:
        return local_url


def extract_title_and_url(link_hxs):
    href = link_hxs.select("./@href").extract()
    if href:
        url = href[0]
    else:
        url = constants.NO_URL

    title = link_hxs.select(".//text()").extract()
    if title:
        title = title[0].strip()
    else:
        title = constants.NO_TITLE

    return title, url


def separate_blogposts(all_items):
    blogpost_items = set([(title, url)for title, url in all_items if not is_internal_url(url)])
    news_items = set(all_items) - blogpost_items

    return news_items, blogpost_items


def filter_news_items(frontpage_items):
    return frontpage_items, list()


def get_frontpage_toc():
    frontpage_url = "http://{0}".format(LAVENIR_NETLOC)
    html_data = fetch_html_content(frontpage_url)

    hxs = HtmlXPathSelector(text=html_data)

    story_links = hxs.select("//div[@id='content']//div[starts-with(@class, 'fr-row')]//h3/a")
    more_story_links = hxs.select("//div[@id='content']//div[starts-with(@class, 'fr-section')]//h3/a")
    local_sport_links = hxs.select("//div[@id='content']//div[contains(@class, 'article-with-photo')]//h2/a")
    nopic_story_list = hxs.select("//div[@id='content']//ul[@class='nobullets']//li//div[contains(@class, 'item-title')]//a")

    all_links = it.chain(story_links, more_story_links, local_sport_links, nopic_story_list)

    all_items = [extract_title_and_url(link_hxs) for link_hxs in all_links]
    news_items, blogpost_items = separate_blogposts(all_items)

    return [(title, expand_full_url(url)) for (title, url) in news_items if url not in BLACKLIST], list(blogpost_items), []


def test_sample_data():
    urls = [
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120326_023",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120330_00139582",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120331_00140331",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120902_00199571",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120902_00199563",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120831_00199041",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120901_00199541",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120831_00198968",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120901_00199482",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120317_002",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120317_002",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130224_001",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130224_005",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130224_016",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130221_00271965",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130224_00273104",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130224_005",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120831_00198968",  # highlighted videos + ghost links
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120226_00122978"
        ]

    urls_new_style = [
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120609_00168756",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120609_005",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120609_008",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120609_00168714",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120609_00168727",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120609_00168746",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120608_036",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120609_00168739",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120609_00168747",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120609_00168712",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120609_00168710",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120608_00168309",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120609_00168735",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120609_00168743",
        "http://www.lavenir.net/sports/cnt/DMF20120608_036",  # storify
        "http://www.lavenir.net/sports/cnt/DMF20130309_001",  # scribblelive
        "http://www.lavenir.net/sports/cnt/DMF20130309_00279912",  # youtube
        "http://www.lavenir.net/sports/cnt/DMF20130308_00279411",  # photoset in header
        "http://www.lavenir.net/sports/cnt/DMF20130308_00279366",  # youtube in header
        "http://www.lavenir.net/sports/cnt/DMF20130308_00279386",   # in text links
        "http://www.lavenir.net/sports/cnt/DMF20130307_00278978",  # rtlinfo vids
        "http://www.lavenir.net/sports/cnt/DMF20130307_00278892",  # in text link
        "http://www.lavenir.net/sports/cnt/DMF20130306_00278406m",  # vimeo link
        "http://www.lavenir.net/sports/cnt/DMF20130306_00278376",  # bottom links
        "http://www.lavenir.net/sports/cnt/DMF20130305_00277489",  # pdf newspaper
        "http://www.lavenir.net/sports/cnt/DMF20130304_037",  # another storify
        "http://www.lavenir.net/sports/cnt/DMF20130304_010",   # poll
        "http://www.lavenir.net/sports/cnt/DMF20130303_00276383",  # hungary video
        "http://www.lavenir.net/sports/cnt/DMF20130303_00276372",
        "http://www.lavenir.net/sports/cnt/DMF20130303_00276357",  # something intereactive
        "http://www.lavenir.net/sports/cnt/DMF20130303_00276369",
        "http://www.lavenir.net/sports/cnt/DMF20130305_010",  # embedded tweets
        "http://www.lavenir.net/sports/cnt/DMF20120719_00183602",  # weird storify (no <noscript>)
        "http://www.lavenir.net/sports/cnt/DMF20121007_007",  # jwplayer
        "http://www.lavenir.net/sports/cnt/DMF20121213_026",  # <embed> with eitb.com video
        "http://www.lavenir.net/sports/cnt/DMF20130103_025",  # picture instead of video
        "http://www.lavenir.net/sports/cnt/DMF20130116_00256248",  # animated gif
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120813_026",

        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20121213_026",

        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130116_00256248",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130123_044",

        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120920_011",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20121007_007",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120706_027",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120813_026",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120917_011",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20121024_00222907",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120918_015",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120920_011",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20121213_026",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130103_025",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130116_00256248",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20130123_044",
        "http://www.lavenir.net/article/detail.aspx?articleid=DMF20120226_00122978"  # flowplayer
    ]

    fpaths = [
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-11-14/15.05.09/raw_data/8.html",  # canalplus video
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-09-30/19.05.13/raw_data/1.html",  # image link in video div
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-08-06/18.05.11/raw_data/1.html",  # thinglink annonated image
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-09-13/11.05.11/raw_data/6.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-09-05/19.05.09/raw_data/1.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-09-05/22.05.10/raw_data/5.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-09-05/14.05.11/raw_data/4.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-19/15.05.09/raw_data/0.html",  # brightcove
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-19/15.05.09/raw_data/1.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-03-29/19.05.10/raw_data/2.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-10/17.05.10/raw_data/6.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-15/09.05.10/raw_data/5.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-15/13.05.09/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-15/12.05.10/raw_data/5.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-03-23/19.05.10/raw_data/1.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-04-03/13.05.10/raw_data/2.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-12-31/13.05.09/raw_data/2.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-04-20/11.05.10/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-09-06/10.05.10/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-05-28/19.05.10/raw_data/1.html",  # vtm
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-07-11/23.05.10/raw_data/3.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-05-16/09.05.10/raw_data/7.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-05-06/21.05.13/raw_data/8.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-05-07/11.05.12/raw_data/7.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-05-07/09.05.09/raw_data/13.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-05-26/09.05.10/raw_data/2.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-05-02/14.05.12/raw_data/3.html",  # kewego
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-05-02/19.05.10/raw_data/2.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-08-13/11.05.09/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-11-05/16.05.09/raw_data/5.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-11-04/16.05.15/raw_data/4.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-11-04/10.05.09/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-11-04/12.05.10/raw_data/3.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-11-04/11.05.08/raw_data/2.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-01-18/12.05.10/raw_data/5.html",  # facebook video
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-02-19/16.05.10/raw_data/1.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-11-28/11.05.09/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-11-28/07.05.09/raw_data/0.html",  # bimvid.com
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-11-08/12.05.09/raw_data/8.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-03-19/19.05.09/raw_data/1.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-03-19/19.05.09/raw_data/3.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-03-19/20.05.09/raw_data/3.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-05-03/09.05.10/raw_data/4.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-05-03/13.05.16/raw_data/4.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-08/10.05.11/raw_data/6.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-08/14.05.09/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-03-30/14.05.12/raw_data/6.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-02/23.05.14/raw_data/1.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-02/08.05.12/raw_data/8.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-03/23.05.10/raw_data/1.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-03/07.05.11/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-01/10.05.30/raw_data/12.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-01/08.05.26/raw_data/8.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-01/23.05.10/raw_data/1.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-10-07/23.05.10/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-04-10/14.05.11/raw_data/6.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-08-08/19.05.11/raw_data/2.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-12-07/15.05.09/raw_data/1.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-01-23/18.05.06/raw_data/4.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-01-23/01.05.09/raw_data/0.html",  # worldnow.com
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-01-22/17.05.13/raw_data/1.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-01-22/21.05.09/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-01-22/22.05.08/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-12-24/14.05.09/raw_data/4.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-07-23/19.05.12/raw_data/1.html",  # cnn, loads of links
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-07-23/21.05.10/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-07-24/08.05.10/raw_data/6.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-09-11/15.05.09/raw_data/1.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-09-11/13.05.10/raw_data/7.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-09-11/14.05.10/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-01-24/12.05.14/raw_data/24.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-01-02/18.05.09/raw_data/7.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-07-03/15.05.16/raw_data/4.html",  # qik  video
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-01-06/11.05.10/raw_data/0.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-01-08/15.05.12/raw_data/3.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-01-08/18.05.09/raw_data/3.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-01-08/16.05.09/raw_data/2.html",
        #"/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2012-05-25/19.05.11/raw_data/0.html",
        "/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-02-27/11.05.16/raw_data/2.html",  # div/img
        "/Volumes/Curst/csxj/tasks/121_final_reprocess/jsondb/lavenir/2013-02-25/11.05.22/raw_data/5.html",
    ]

    def process_single(source):
        article, html_content = extract_article_data(source)
        if article:
            print(article.title)
            print(article.url)
            print_taggedURLs(article.links, 70)
            print("°" * 80)

            # from helpers.unittest_generator import generate_unittest
            # import os
            # generate_unittest("links_new_thinglink", "lavenir", dict(urls=article.links), html_content, source.name, os.path.join(os.path.dirname(__file__), "../../tests/datasources/test_data/lavenir"), True)
        else:
            print('page was not recognized as an article')

    # for url in urls_new_style[-1:]:
    #     process_single(url)

    for i, fpath in enumerate(fpaths[:]):
        print(i, fpath)
        with open(fpath) as f:
            process_single(f)

if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        import doctest
        doctest.testmod(verbose=True)
    else:
        test_sample_data()
