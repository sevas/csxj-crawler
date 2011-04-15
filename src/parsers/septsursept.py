#!/usr/bin/env python

import sys
import locale
import urllib
from datetime import datetime
from itertools import chain
import re
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, UnicodeDammit, Tag
from utils import fetch_html_content, count_words, make_soup_from_html_content






def extract_titles_and_links_from_third_column(third_column):
    '''
    '''
    items = third_column.findAll('div', {'class':'gen_imgbox'}, recursive=False)
   
    def extract_title_and_link(imgbox):
        return imgbox.h3.a.contents, imgbox.h3.a.get('href')

    return [extract_title_and_link(imgbox) for imgbox in items]



def extract_titles_and_links_from_second_column(second_column):
    return []



def extract_frontpage_titles_and_links():
    
    html_content = fetch_html_content('http://7sur7.be')

    soup = make_soup_from_html_content(html_content, True)

    second_column = soup.find('div', {'id':'str_col2'})
    titles_and_links = extract_titles_and_links_from_second_column(second_column)
    
    third_column = soup.find('div', {'id':'str_col3'})
    titles_and_links = extract_titles_and_links_from_third_column(third_column)

    
    
    
    


def show_frontpage_articles():
    titles_and_links = extract_frontpage_titles_and_links()

    for (title, link) in titles_and_links:
        print '%s (%s)' % (title, link)






if __name__ == '__main__':
    show_frontpage_articles()
