#!/usr/bin/env python

import sys
import locale
import os.path
from datetime import datetime, date, time
from collections import namedtuple
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, UnicodeDammit, Tag
from utils import fetch_html_content, fetch_rss_content, count_words, make_soup_from_html_content

try:
    import json
except ImportError:
    import simplejson as json


# for datetime conversions
if sys.platform in ['linux2', 'cygwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF8')
elif sys.platform in [ 'darwin']:
    locale.setlocale(locale.LC_TIME, 'fr_FR')


    
TaggedURL = namedtuple('TaggedURL', 'URL title tags')


def tag_URL((url, title), tags):
    return TaggedURL(URL=url, title=title, tags=tags)

    
class ArticleData(object):
    """
    A glorified dict to keep the extracted metadata and content of one article.
    Has utility methods for json (de)serialization.
    """
    
    def __init__(self, url, title,
                 pub_date, pub_time, fetched_datetime,
                 external_links, internal_links,
                 category, author,
                 intro, content):
        """
        Boring init func.
        """
        self.url = url
        self.title = title
        self.pub_date = pub_date
        self.pub_time = pub_time
        self.fetched_datetime = fetched_datetime

        self.external_links = external_links
        self.internal_links = internal_links
        
        self.category = category
        self.author = author
        
        self.intro = intro
        self.content = content


        
    def to_json(self):
        """
        Converts all attributes in self.__dict__ into a json string.
        Takes care of non natively serializable objects (such as datetime).
        """
        d = dict(self.__dict__)
        # datetime, date and time objects are not json-serializable

        date = d['fetched_datetime']
        d['fetched_datetime'] = date.strftime('%Y-%m-%dT%H:%M:%S')

        pub_date, pub_time = d['pub_date'], d['pub_time']

        d['pub_date'] = pub_date.strftime('%Y-%m-%d')
        d['pub_time'] = pub_time.strftime('%H:%S')
        
        return json.dumps(d)


    
    @classmethod
    def from_json(kls, json_string):
        """
        Class method to rebuild an ArticleData object from a json string.
        Takes care of non natively deserializable objects (such as datetime).        
        """
        d = json.loads(json_string)

        date_string = d['fetched_datetime']
        d['fetched_datetime'] = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')

        pub_date, pub_time = d['pub_date'],  d['pub_time']
        year, month, day = [int(i) for i in pub_date.split('-')]
        d['pub_date'] = date(year, month, day)

        h, m = [int(i) for i in pub_time.split(':')]
        d['pub_time'] = time(h, m)
        
        return kls(**d)




TEXT_MARKUP_TAGS = ['b', 'i', 'u', 'em', 'tt', 'h1',  'h2',  'h3',  'h4',  'h5', 'span' ]    


def sanitize_fragment(fragment):
    """
    Returns the plain text version of a chunk of text formatted with HTML tags.
    Unsupported tags are ignored.
    """
    
    # A text fragment is either an HTML tag (with its own child text fragments)
    # or just a plain string. 
    if isinstance(fragment, Tag):
        # If it's the former, we remove the tag and clean up all its children
        if fragment.name in TEXT_MARKUP_TAGS:
            return ''.join([sanitize_fragment(f) for f in fragment.contents])
        # sometimes we get embedded <objects>, just ignore it
        else:
            return ''
    # If it's a plain string, there is nothing else to do
    else:
        return fragment

    
    
def sanitize_paragraph(paragraph):
    """
    Removes image links, removes paragraphs, formatting
    """
    return ''.join([sanitize_fragment(fragment) for fragment in paragraph.contents])




def extract_content(story):
    """
    Finds the story's body, cleans up the text to remove all html formatting.
    Returns a list of strings, one per found paragraph.
    """
    story = story.find('div', {'id':'story_body'})

    paragraphs = story.findAll('p', recursive=False)

    clean_paragraphs = [sanitize_paragraph(p) for p in paragraphs]
    
    return clean_paragraphs
    



def extract_to_read_links_from_sidebar(sidebar):
    to_read_links_container = sidebar.find('div', {'id':'lire_aussi'})

    #sometimes, it does not exist at all
    if to_read_links_container:
        return [(link.get('href'), link.get('title'))
                for link in to_read_links_container.findAll('a', recursive=False)]
    else:
        return []

    

def extract_external_links_from_sidebar(sidebar):
    external_links_container = sidebar.find('div', {'id':'external'})

    if external_links_container:
        return [(link.get('href'), link.get('title'))
                for link in external_links_container.findAll('a', recursive=False)]
    else:
        return []




def extract_recent_links_from_soup(soup):
    #todo : check if those links are actually associated to the article
    recent_links_container = soup.find('div', {'id':'les_plus_recents'})
    if recent_links_container:
        return [(link.get('href'), link.contents[0])
                for link in recent_links_container.findAll('a', recursive=False) ]
    else:
        return []

    

def extract_links(soup):
    """
    Get the link lists for one news item, from the parsed html content.
    'Le Soir' has 3 kinds of links, but they're not all always there.
    """
    sidebar = soup.find('div', {'id':'st_top_center'})

    external_links = [tag_URL(i, []) for i in extract_external_links_from_sidebar(sidebar)]
    associated_links = [tag_URL(i, ['to read']) for i in extract_to_read_links_from_sidebar(sidebar)]
    associated_links.extend([tag_URL(i, ['recent']) for i in extract_recent_links_from_soup(soup)])
    
    return external_links, associated_links

    

def extract_title(story):
    header = story.find('div', {'id':'story_head'})
    title = header.h1.contents[0]

    #return title
    return unicode(title)
    

def extract_author_name(story):
    header = story.find('div', {'id':'story_head'})
    author_name = header.find('p', {'class':'info st_signature'})

    return author_name.contents[0]



def extract_date(story):
    header = story.find('div', {'id':'story_head'})
    date = header.find('p', {'class':'info st_date'})

    date_string = date.contents[0]
    datetime_published = datetime.strptime(date_string, '%A %d %B %Y, %H:%M')

    return datetime_published.date(), datetime_published.time()
    


def extract_intro(story):
    header = story.find('div', {'id':'story_head'})
    intro = header.find('h4', {'class':'chapeau'})
    # so yeah, sometimes the intro paragraph contains some <span> tags with things
    # we don't really care about. Filtering that out.
    text_fragments = [fragment for fragment in intro.contents if not isinstance(fragment, Tag)]

    return ''.join(text_fragments)


    
def extract_category(story):
    breadcrumbs = story.find('div', {'id':'fil_ariane'})
    category_stages = [a.contents[0] for a in breadcrumbs.findAll('a') ]
    return category_stages


def extract_article_data_from_url(url):
    html_content = fetch_html_content(url)
    soup = make_soup_from_html_content(html_content)
    
    story = soup.find('div', {'id':'story'})


    category = extract_category(story)
    title = extract_title(story)    
    pub_date, pub_time = extract_date(story)
    author = extract_author_name(story)
    external_links, internal_links = extract_links(soup)

    intro = extract_intro(story)
    content = extract_content(story)

    fetched_datetime = datetime.today()

    return ArticleData(url, title, pub_date, pub_time, fetched_datetime,
                              external_links, internal_links,
                              category, author,
                              intro, content)
    


def get_two_columns_stories(element):
    """
    Returns the two <li> with two 'two columns' stories.
    This function assumes we already checked that the element actually has
    two sub stories
    """
    two_columns_stories_list = element.findAll('ul', {'class':'two_cols'}, recursive=False)[0]
    return two_columns_stories_list.findAll('li', recursive=False)



def element_has_two_columns_stories(element):
    """
    Checks whether or not a frontpage entry is a stand alone news item, or a container
    for two 'two columns' items.
    """
    return len(element.findAll('ul', {'class':'two_cols'}, recursive=False)) == 1



def get_frontpage_articles():
    """
    Fetch links to articles listed on the 'Le Soir' front page.
    For each of them, extract the relevant data.
    """
    url = 'http://www.lesoir.be'
    html_content = fetch_html_content(url)

    soup = make_soup_from_html_content(html_content)

    # Here we have interlaced <ul>'s with a bunch of random other shit that
    # need some filtering
    stories_containers = soup.findAll('ul', {'class':'stories_list grid_6'})


    frontpage_links = []

    for container in stories_containers:
        all_stories = set(container.findAll('li', recursive=False))
        main_stories = set(container.findAll('li', {'class':'stories_main clearfix'}, recursive=False))

        other_stories = all_stories - main_stories

        
        # So, in _some_ lists of stories, the first one ('main story') has its title in an <h1>
        # and the rest in an <h2>
        # Also, some have two columns stories.
        # Beautiful soup indeed.
        for item in main_stories:
            frontpage_links.append((item.h1.a.get('title'), item.h1.a.get('href')))

        for item in other_stories:
            if element_has_two_columns_stories(item):
                first, second = get_two_columns_stories(item)
                # For some reason, those links don't have a 'title' attribute.
                # Love this.
                def extract_title_and_link(item):
                    return item.h2.a.contents[0], item.h2.a.get('href')
                frontpage_links.append(extract_title_and_link(first))
                frontpage_links.append(extract_title_and_link(second))

            else:
                frontpage_links.append((item.h2.a.get('title'), item.h2.a.get('href')))

    return frontpage_links


            

def get_rss_articles():
    rss_url = 'http://www.lesoir.be/la_une/rss.xml'

    xml_content = fetch_rss_content(rss_url)
    stonesoup = BeautifulStoneSoup(xml_content)

    titles_in_rss = [item.title.contents[0] for item in stonesoup.findAll('item')]
        
    return titles_in_rss

    

    
#def parse_sample_data():
#    import sys
#    data_directory = '../../sample_data'
#    sys.path.append(data_directory)
#    from dataset import dataset
# 
# 
#    for entry in dataset['le soir']:
#        url = entry['URL']
#        filename = entry['file']
#        filepath = '%s/%s' % (data_directory, filename)
#    
#        with open(filepath) as f:
#            html_content = f.read()
#            extract_article_data_from_html_content(html_content)
    


def is_external_blog(url):
    return not url.startswith('/')


def separate_articles_from_blogposts(frontpage_links):
    articles = []
    blogposts = []
    for (title, url) in frontpage_links:
        if is_external_blog(url):
            blogposts.append((title, url))
        else:
            articles.append((title, url))

    return articles, blogposts




ErrorLogEntry = namedtuple('ErrorLogEntry', 'url filename stacktrace')


def get_frontpage_articles_data():
    import traceback
    frontpage_links = get_frontpage_articles()
    article_links, blogpost_links = separate_articles_from_blogposts(frontpage_links)

    articles = []
    errors = []

    for (title, url) in article_links:
        try:
            full_url = 'http://www.lesoir.be%s' % url
            
            article_data = extract_article_data_from_url(full_url)
            articles.append(article_data)
        except AttributeError:
            
            stacktrace = traceback.format_stack()
            new_error = ErrorLogEntry(full_url, None, stacktrace)
            errors.append(new_error)
     
    return articles, blogpost_links, errors


    


def make_json_filename(prefix):
    date = datetime.now().strftime('%Y%m%d-%H%M')
    return '{0}-{1}.json'.format(prefix, date)


def save_to_json_file(json_entries, outfilename, outdir):

    outpath = os.path.join(outdir, outfilename)
    with open(outpath, 'w') as f:
        json.dump(json_entries, f)



if __name__ == '__main__':
    articles, blogpost_links, errors = get_frontpage_articles_data()

    json_entries = []
    
    for article_data in articles:
        print 'title = ', article_data.title
        print 'url = ',  article_data.url
        print 'date = ', article_data.pub_date
        print 'n external links = ', len(article_data.external_links)
        print 'n internal links = ', len(article_data.internal_links)
        print 'category = ', '/'.join(article_data.category)
        print 'author = ', article_data.author
        print 'n words = ', count_words(''.join(article_data.content))
        print article_data.intro
        print
        print article_data.content

        json_entries.append(article_data.to_json())
        
        print '-' * 80
        
    print 'blogposts : '


    result = {'articles':json_entries, 'blogposts':blogpost_links, 'errors':errors}


    print 'articles : {0} \t blogposts : {1} \t errors : {2}'.format(len(json_entries), len(blogpost_links), len(errors))
    filename = make_json_filename('lesoir')
    #save_to_json_file(result, filename, '../../out')
