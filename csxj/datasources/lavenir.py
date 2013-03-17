#!/usr/bin/env python
# coding=utf-8

from datetime import datetime
import codecs
import itertools as it
from urlparse import urlparse
from scrapy.selector import HtmlXPathSelector

from csxj.common.tagging import classify_and_tag, make_tagged_url, update_tagged_urls, print_taggedURLs
from csxj.db.article import ArticleData
from parser_tools.utils import fetch_html_content
from parser_tools.utils import extract_plaintext_urls_from_text, setup_locales
from parser_tools.utils import remove_text_formatting_markup_from_fragments, remove_text_formatting_and_links_from_fragments
from parser_tools import constants

from helpers.unittest_generator import generate_unittest

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


def extract_links_from_video_div(video_div_hxs):
    tagged_urls = list()
    iframes = video_div_hxs.select('.//iframe')

    if iframes:
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
    if objects:
        for object_hxs in objects:
            associated_link = object_hxs.select("./following-sibling::a[1]")
            if associated_link:
                title, url = extract_title_and_url(associated_link[0])
            else:
                url = object_hxs.select("./param [@name='movie']/@value")
                title = url
            tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
            tags |= set(['embedded', 'video'])
            tagged_urls.append(make_tagged_url(url, title, tags))

    scripts = video_div_hxs.select('.//script')
    if scripts:
        for script_hxs in scripts:
            script_src = script_hxs.select('./@src').extract()
            if script_src:
                if 'flowplayer' in script_src[0]:
                    title = constants.EMBEDDED_VIDEO_TITLE
                    url = constants.EMBEDDED_VIDEO_URL
                    tags = set(['external', 'embedded', 'video', 'flowplayer', constants.UNFINISHED_TAG])
                    tagged_urls.append(make_tagged_url(url, title, tags))
                elif 'jwplay' in script_src[0]:
                    title = constants.EMBEDDED_VIDEO_TITLE
                    url = constants.EMBEDDED_VIDEO_URL
                    tags = set(['external', 'embedded', 'video', 'jwplayer', constants.UNFINISHED_TAG])
                    tagged_urls.append(make_tagged_url(url, title, tags))
                else:
                    raise ValueError("Found a <script> for an embedded video, for an unknown type")
    if tagged_urls:
        return tagged_urls
    else:
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
                    title = constants.RENDERED_TWEET_TITLE
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
            tags |= set(['embedded', 'tweet'])
            tagged_urls.append(make_tagged_url(url, title, tags))
        else:
            noscript_hxs = script_hxs.select('./following-sibling::noscript[1]')
            if noscript_hxs:
                link_hxs = noscript_hxs.select('a')
                title, url = extract_title_and_url(link_hxs)
                tags = classify_and_tag(url, LAVENIR_NETLOC, LAVENIR_INTERNAL_BLOGS)
                tags |= set(['embedded'])
                tagged_urls.append(make_tagged_url(url, title, tags))
            else:
                raise ValueError("Found a <script> without a <noscript> counterpart")

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
        html_content = fetch_html_content(source)

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

    title = link_hxs.select("./text()").extract()
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
        "http://www.lavenir.net/sports/cnt/DMF20121007_007",
    ]

    urls_before_june = [
        "/Volumes/Curst/csxj/tasks/lavenir_backwards_compat/jsondb/lavenir/2012-02-27/01.13.09/raw_data/39.html",
        "/Volumes/Curst/csxj/tasks/lavenir_backwards_compat/jsondb/lavenir/2012-02-27/13.05.12/raw_data/7.html",
    ]



    for url in urls_new_style[-1:]:
        article, html_content = extract_article_data(url)
        if article:
            print(article.title)
            print(article.url)
            print_taggedURLs(article.links, 70)
            print("°" * 80)

            import os
            #generate_unittest("links_new_jwplayer", "lavenir", dict(urls=article.links), html_content, url, os.path.join(os.path.dirname(__file__), "../../tests/datasources/test_data/lavenir"), True)

        else:
            print('page was not recognized as an article')



if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        import doctest
        doctest.testmod(verbose=True)
    else:
        test_sample_data()
