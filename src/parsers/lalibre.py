#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib
from datetime import datetime
from BeautifulSoup import Tag
from utils import fetch_html_content, count_words, make_soup_from_html_content
from article import ArticleData, tag_URL

try:
    import json
except ImportError:
    import simplejson as json

    
def extract_date(main_content):
    publication_date = main_content.find('p', {'id':'publicationDate'}).contents[0]
    date_string = publication_date.replace('Mis en ligne le ', '').rstrip().lstrip()
    
    date = datetime.strptime(date_string, '%d/%m/%Y')
    return date



def sanitize_fragment(fragment):
    if isinstance(fragment, Tag):
        # sometimes, we just get <p></p>
        if fragment.contents:
            return ''.join(sanitize_fragment(f) for f in fragment.contents)
        else:
            return ''
    else:
        return fragment


    
def sanitize_paragraph(paragraph):
    """Extracts embedded links. Returns plain text article and the extracted links"""

    def extract_keyword_and_link(keyword_link):
        return keyword_link.contents[0], keyword_link.get('href')
        
    keyword_links = [extract_keyword_and_link(link) for link in paragraph.findAll('a', recursive=True)]
    sanitized_paragraph = [sanitize_fragment(fragment) for fragment in paragraph.contents]            


    return ''.join(sanitized_paragraph), [(keyword, 'http://www.lalibre.be%s' % url) for (keyword, url) in keyword_links]



def extract_text_content_and_links(main_content):
    article_text = main_content.find('div', {'id':'articleText'})

    all_links = []
    all_fragments = [] 
    paragraphs = article_text.findAll('p', recursive=False)

    for paragraph in paragraphs:
        fragments, links = sanitize_paragraph(paragraph)
        all_links.extend(links)
        all_fragments.append(fragments)
        all_fragments.append('\n')

    text_content = ''.join(all_fragments)
    return text_content, all_links



def extract_category(main_content):
    breadcrumbs = main_content.find('p', {'id':'breadCrumbs'})
    links = breadcrumbs.findAll('a', recursive=False)

    return [link.contents[0].rstrip().lstrip() for link in links]


def extract_links(main_content):
    link_list = main_content.find('ul', {'class':'articleLinks'})

    # sometimes there are no links, and thus no placeholder
    if link_list:
        links = []
        for entry in link_list.findAll('li', {'class':'picoType1'}, recursive=False):
            title = entry.a.get('href')
            url = entry.a.contents[0]
            links.append((title, url))

        return ['http://www.lalibre.be%s' % link for link in links]
    else:
        return []
        


def extract_author_name(main_content):
    writer = main_content.find('p', {'id':'writer'})
    if writer:
        return writer.contents[0].rstrip().lstrip()
    else:
        return 'None'

    

def extract_article_data(source):
    """
    """
    if hasattr(source, 'read'):
        html_content = source.read()
    else:
        html_content = fetch_html_content(source)

    soup = make_soup_from_html_content(html_content)

    main_content = soup.find('div', {'id':'mainContent'})

    category = extract_category(main_content)
    author = extract_author_name(main_content)
    title = main_content.h1.contents[0].rstrip().lstrip()
    pub_date = extract_date(main_content)
    
    intro = main_content.find('div', {'id':'articleHat'}).contents[0].rstrip().lstrip()

    content, keyword_links = extract_text_content_and_links(main_content)

    article_links = extract_links(main_content)

    external_links = [tag_URL(i, ['to read']) for i in article_links]
    internal_links = [tag_URL(i, ['keyword']) for i in keyword_links]

    fetched_datetime = datetime.today()

    new_article = ArticleData(source, title, pub_date, None, fetched_datetime,
                              external_links, internal_links, category, author,
                              intro, content)
    return new_article



def get_frontpage_toc():
    hostname_url = 'http://www.lalibre.be'
    html_content = fetch_html_content(hostname_url)

    soup = make_soup_from_html_content(html_content)

    article_list_container = soup.find('div', {'id':'mainContent'})
    announces = article_list_container.findAll('div', {'class':'announce'}, recursive=False)

    def extract_title_and_link(announce):
        title, url = announce.h1.a.contents[0], announce.h1.a.get('href')
        return title, '{0}{1}'.format(hostname_url, url)
    
    return [extract_title_and_link(announce) for announce in announces]




#def test_sample_data():
#    with open('../../sample_data/la_libre_recursive_cleanup.html', 'r') as f:
#        html_content = f.read()
#
#        extracted_data = extract_article_data_from_html_content(html_content)
#        category, author, title, date, intro, content, links = extracted_data
#        url = 'foo'
#        article_data = ArticleData(url, title, date, content, links, category, author, intro)
#
#        print 'title = ', article_data.title
#        print 'url = http://www.lalibre.be%s' % article_data.url
#        print 'date = ', article_data.date
#        print 'n links = ', len(article_data.links)
#        print 'category = ', '/'.join(article_data.category)
#        print 'author = ', article_data.author
#        print 'n words = ', count_words(article_data.content)
#        print article_data.intro
#        print
#        print article_data.content
#        print article_data.links
                



def list_frontpage_articles():
    frontpage_items = get_frontpage_toc()
    print len(frontpage_items)

    for (title, url) in frontpage_items:
        print 'fetching data for article :',  title

        article = extract_article_data(url)
        article.print_summary()




if __name__ == '__main__':
    list_frontpage_articles()
    #test_sample_data()
