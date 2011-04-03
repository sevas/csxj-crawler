#!/usr/bin/env python

import urllib
from datetime import datetime
from itertools import chain
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, UnicodeDammit, Tag
from utils import fetch_html_content, count_words, make_soup_from_html_content


class ArticleData(object):
    def __init__(self, url, title, date, content, links, category, author, intro):
        self.url = url
        self.title = title
        self.date = date
        self.content = content
        self.links = links
        self.category = category
        self.author = author
        self.intro = intro

    def to_json(self):
        pass




def sanitize_fragment(fragment):
    """
    An html framgent is whether a tag (<i>, <a>, <b>, <span>, etc) or a string.
    If it's a tag, recursively convert it to the plaintext version.
    """
    if isinstance(fragment, Tag):
        # sometimes, we just get <p></p>
        if fragment.contents:
            return "".join(sanitize_fragment(f) for f in fragment.contents)
        else:
            return ""
    else:
        return fragment


    
def sanitize_paragraph(paragraph):
    """Extracts embedded links. Returns plain text article and the extracted links"""

    def extract_keyword_and_link(keyword_link):
        return keyword_link.contents[0], keyword_link.get('href')
        
    keyword_links = [extract_keyword_and_link(link) for link in paragraph.findAll("a", recursive=True)]
    sanitized_paragraph = [sanitize_fragment(fragment) for fragment in paragraph.contents]            

    return "".join(sanitized_paragraph), [(keyword, "http://www.dhnet.be%s" % url)
                                          for (keyword, url) in keyword_links]

    


def extract_sanitized_paragraph_and_links(paragraph):
    """
    Takes an html paragraph (soup of plain text, <i>, <b>, <em>, and <a> elements)
    Extracts the text content and a list of (keyword, link) tuples 
    """
    fragments, links = sanitize_paragraph(paragraph)

    intro_text = ''.join(fragments)
    return intro_text, links
    


def cleanup_text_fragment(text_fragment):    
    if isinstance(text_fragment, Tag):
        return ''.join([cleanup_text_fragment(f) for f in text_fragment.contents])
    else:
        return text_fragment


    
def extract_text_content_and_links_from_articletext(article_text):
    def extract_title_and_link(link):
        return link.contents[0], link.get('href')
    keyword_links = [extract_title_and_link(link) for link in article_text.findAll("a", recursive=True)]

    
    # first child is the intro paragraph
    children = article_text.contents[1:]


    TEXT_MARKUP_TAGS = ['b', 'i', 'u', 'em', 'tt', 'h1',  'h2',  'h3',  'h4',  'h5',  ]    
    # the rest might be a list of paragraphs, but might also just be the text, sometimes with
    # formatting.

    cleaned_up_text_fragments = []
    
    for child in children:
        if isinstance(child, Tag):
            if child.name in TEXT_MARKUP_TAGS:
                cleaned_up_text_fragments.append([cleanup_text_fragment(f) for f in child.contents])
            elif child.name == 'p':
                cleaned_up_text_fragments.append([cleanup_text_fragment(f) for f in child.contents])
            else:
                print "discarded tag : %s" % child.name
        else:
            cleaned_up_text_fragments.append(child)

    return cleaned_up_text_fragments, keyword_links



def extract_intro_and_links_from_articletext(article_text):
    intro_paragraph = article_text.p
    return extract_sanitized_paragraph_and_links(intro_paragraph)


def extract_category_from_maincontent(main_content):
    breadcrumbs = main_content.find("p", {'id':"breadcrumbs"})

    links = breadcrumbs.findAll("a", recursive=False)

    return [link.contents[0].rstrip().lstrip() for link in links]
    



def extract_associated_links_from_maincontent(main_content):
    container = main_content.find("ul", {'class':"articleLinks"}, recursive=False)

    # sometimes there are no links
    if container:
        def extract_title_and_link(list_item):
            return list_item.a.contents[0], list_item.a.get('href')
        list_items = container.findAll("li", recursive=False)
        return [extract_title_and_link(list_item) for list_item in list_items]
    else:
        return []



def extract_date_from_maincontent(main_content):
    date_string = main_content.find("p", {'id':"articleDate"}).contents[0]
    date = datetime.strptime(date_string, "(%d/%m/%Y)")
    return date



def extract_article_data_from_html_content(html_content):
    soup = make_soup_from_html_content(html_content)

    main_content = soup.find("div", {'id':"maincontent"})

    title = main_content.h1.contents[0]
    date = extract_date_from_maincontent(main_content)
    associated_links = extract_associated_links_from_maincontent(main_content)
    category = extract_category_from_maincontent(main_content)

    article_text = main_content.find("div", {'id':"articleText"})
    intro, kw_links = extract_intro_and_links_from_articletext(article_text)
    text, kw_links2 = extract_text_content_and_links_from_articletext(article_text)

    return title, date, category, associated_links, intro, kw_links, kw_links2, text




def extract_title_and_link_from_item_box(item_box):
    title = item_box.h2.a.contents[0].rstrip().lstrip()
    url = item_box.h2.a.get("href")
    return title, url



def is_item_box_an_ad_placeholder(item_box):
    # awesome heuristic : if children are iframes, then go to hell 
    return len(item_box.findAll("iframe")) != 0



def extract_title_and_link_from_anounce_group(announce_group):
    # sometimes they use item box to show ads or some crap like that.
    odd_boxes = announce_group.findAll("div", {"class":"box4 odd"})
    even_boxes = announce_group.findAll("div", {"class":"box4 even"})

    all_boxes = chain(odd_boxes, even_boxes)

    return [extract_title_and_link_from_item_box(box)
            for box in all_boxes
            if not is_item_box_an_ad_placeholder(box)]



def get_first_story_title_and_url(main_content):
    """
    Extract the title and url of the main frontpage story
    """
    first_announce = main_content.find("div", {'id':"firstAnnounce"})
    first_title = first_announce.h2.a.get("title")
    first_url = first_announce.h2.a.get("href")

    return first_title, first_url



def get_frontpage_articles():
    url = "http://www.dhnet.be"
    html_content = fetch_html_content(url)
    soup = make_soup_from_html_content(html_content)

    main_content = soup.find("div", {'id':"maincontent"})

    all_titles_and_urls = []

    # so, the list here is a combination of several subcontainer types.
    # processing every type separetely
    first_title, first_url = get_first_story_title_and_url(main_content)
    all_titles_and_urls.append((first_title, first_url))
    
    # this will pick up the 'annouceGroup' containers with same type in the 'regions' div
    first_announce_groups = main_content.findAll("div",
                                                 {'class':"announceGroupFirst announceGroup"},
                                                 recursive=True)    
    announce_groups = main_content.findAll("div",
                                           {'class':"announceGroup"},
                                           recursive=True)

    # all those containers have two sub stories
    for announce_group in chain(first_announce_groups, announce_groups):
        titles_and_urls = extract_title_and_link_from_anounce_group(announce_group)
        all_titles_and_urls.extend(titles_and_urls)

    return [(title, "http://www.dhnet.be%s" % url) for (title, url) in  all_titles_and_urls]



def print_report(extracted_data):
    title, date, category, associated_links, intro, kw_links, kw_links2, text = extracted_data

    print text
    
    print """
    title: %s
    date: %s
    category: %s
    n links: %d
    n keyword links: %s
    intro: %s
    n words: %d
    """ % (title, date, category,
           len(associated_links), len(kw_links)+len(kw_links2),
           intro, sum(count_words(p) for p in text))



def test_sample_data():
    filename = "../../sample_data/dhnet_no_paragraphs.html"
    with open(filename, "r") as f:
        html_content = f.read()
        extracted_data = extract_article_data_from_html_content(html_content)
        print_report(extracted_data)



def show_frontpage_articles():
    frontpage_items = get_frontpage_articles()

    print "%s items on frontpage" % len(frontpage_items)
    for title, url in frontpage_items:
        print "Fetching data for : %s (%s)" % (title, url)

        html_content = fetch_html_content(url)
        extracted_data = extract_article_data_from_html_content(html_content)

        print_report(extracted_data)
        print "-" * 20
    
        
if __name__ == '__main__':
    #show_frontpage_articles()
    test_sample_data()
