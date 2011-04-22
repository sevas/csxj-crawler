#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, time
from BeautifulSoup import Tag
from utils import fetch_html_content, make_soup_from_html_content
from article import ArticleData, tag_URL


def was_story_updated(date_string):
    return not date_string.startswith('Mis en ligne le')



def extract_date(main_content):
    publication_date = main_content.find('p', {'id':'publicationDate'}).contents[0]
    publication_date = publication_date.rstrip().lstrip()

    if was_story_updated(publication_date):
        fragments = publication_date.split(' ')
        date_string = fragments[4]
        h, m = [int(i) for i in fragments[-1].split(':')]
        pub_time = time(h, m)
    else:
        date_string = publication_date.replace('Mis en ligne le ', '')
        pub_time = None

    pub_date = datetime.strptime(date_string, '%d/%m/%Y')
    return pub_date.date(), pub_time



def sanitize_fragment(fragment):
    if isinstance(fragment, Tag):
        # sometimes, we just get <p></p>
        if fragment.contents:
            return ''.join(sanitize_fragment(f) for f in fragment.contents)
        else:
            return ''
    else:
        return fragment


def extract_tagged_links_from_paragraph(paragraph):
    """Extract and tag all the links found in a paragraph """
    def extract_keyword_and_link(keyword_link):
         return  sanitize_fragment(keyword_link.contents[0]), keyword_link.get('href')

    keyword_links = [extract_keyword_and_link(link) for link in paragraph.findAll('a', recursive=True)]
    all_links = set(keyword_links)

    internal_links = set([(t, url) for (t, url) in all_links if url.startswith('/')])
    external_links = all_links - internal_links

    tagged_keyword_links = [tag_URL((t, u), ['keyword']) for (t, u) in internal_links]
    tagged_external_links  = [tag_URL((t, u), ['external']) for (t, u) in external_links]

    return tagged_keyword_links, tagged_external_links



def sanitize_paragraph(paragraph):
    """Returns plain text article"""
    sanitized_paragraph = [sanitize_fragment(fragment) for fragment in paragraph.contents]
    return ''.join(sanitized_paragraph)



def extract_text_content_and_links(main_content):
    article_text = main_content.find('div', {'id':'articleText'})

    all_internal_links, all_external_links = [], []
    all_fragments = [] 
    paragraphs = article_text.findAll('p', recursive=False)

    for paragraph in paragraphs:
        fragments = sanitize_paragraph(paragraph)
        internal_links, external_links = extract_tagged_links_from_paragraph(paragraph)
        all_internal_links.extend(internal_links)
        all_external_links.extend(external_links)

        all_fragments.append(fragments)
        all_fragments.append('\n')

    text_content = ''.join(all_fragments)
    return text_content, all_internal_links, all_external_links



def extract_category(main_content):
    breadcrumbs = main_content.find('p', {'id':'breadCrumbs'})
    links = breadcrumbs.findAll('a', recursive=False)

    return [link.contents[0].rstrip().lstrip() for link in links]


icon_type_to_tags = {
    'pictoType0':['internal', 'full url'],
    'pictoType1':['internal', 'local url'],
    'pictoType2':['images'],
    'pictoType3':['video'],
    'pictoType4':['animation'],
    'pictoType5':['audio'],
    'pictoType9':['internal blog'],
    'pictoType12':['external']
}



def make_tagged_url(title, url, icon_type):
    """
    Attempts to tag a url using the icon used. Mapping is incomplete at the moment.
    Still keeps the icon type as part of the tags for future uses.
    """
    tags = [icon_type]
    if icon_type in icon_type_to_tags:
        tags.extend(icon_type_to_tags[icon_type])

    return tag_URL((url, title), tags)



def extract_and_tag_links(main_content):
    """
    Extract the associated links. Uses the icon type to tag it.
    
    """
    link_list = main_content.find('ul', {'class':'articleLinks'})

    # sometimes there are no links, and thus no placeholder
    if link_list:
        links = []
        for item in link_list.findAll('li', recursive=False):
            # sometimes list items are used to show things which aren't links
            # but more like unclickable ads
            if item.a:
                url = item.a.get('href')
                title = sanitize_fragment(item.a.contents[0])
                icon_type = item.get('class')
            
                links.append(make_tagged_url(title, url, icon_type))

        return links
    else:
        return []
        


def extract_author_name(main_content):
    writer = main_content.find('p', {'id':'writer'})
    if writer:
        return writer.contents[0].rstrip().lstrip()
    else:
        return 'None'


def extract_intro(main_content):
    hat = main_content.find('div', {'id':'articleHat'})

    if hat:
        return hat.contents[0].rstrip().lstrip()
    else:
        return ''

    
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
    pub_date, pub_time = extract_date(main_content)
    
    intro = extract_intro(main_content)

    content, keyword_links, external_links_in_text = extract_text_content_and_links(main_content)

    tagged_associated_links = extract_and_tag_links(main_content)

    external_links = tagged_associated_links + external_links_in_text
    internal_links = keyword_links

    fetched_datetime = datetime.today()

    new_article = ArticleData(source, title, pub_date, pub_time, fetched_datetime,
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




def test_sample_data():
    filename = '../../sample_data/lalibre_external_links_in_text.html'
    with open(filename, 'r') as f:
        article_data = extract_article_data(f)
        article_data.print_summary()

        article_data.url =  filename

        print article_data.to_json()
        for url in article_data.external_links:
            print url


        
def list_frontpage_articles():
    frontpage_items = get_frontpage_toc()
    print len(frontpage_items)

    for (title, url) in frontpage_items:
        print 'fetching data for article :',  title

        article = extract_article_data(url)
        article.print_summary()

        print article.internal_links
        print
        print article.external_links

        print article.to_json()


if __name__ == '__main__':
    #list_frontpage_articles()
    test_sample_data()
