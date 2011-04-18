#!/usr/bin/env python

import sys
import os, os.path
from itertools import izip_longest
from collections import namedtuple
import traceback
from datetime import datetime

from parsers import lesoir, dhnet, lalibre
from parsers.utils import fetch_html_content

try:
    import json
except ImportError:
    import simplejson as json


def filter_only_new_stories(frontpage_stories, filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            last_stories_fetched = [tuple(i) for i in  json.load(f)]
            new_stories = set(frontpage_stories) - set(last_stories_fetched)
    else:
        new_stories = frontpage_stories

    # save the current current list
    with open(filename, 'w') as f:
        json.dump(frontpage_stories, f)

    return new_stories


def find_stories_missing_from_frontpage(frontpage_toc, rss_toc):
    """
    Compare the list of titles found in both the frontpage and the RSS feed.
    The RSS feed is considered complete. This function tests whether or not
    the frontpage parser got all the frontpage stories.

    Returns the list of items found only in the rss feed
    """
    frontpage_titles = [t for (t, u) in frontpage_toc]
    rss_titles = [t for (t, u) in rss_toc]

    only_in_rss = set(rss_titles) - set(frontpage_titles)
    return list(only_in_rss)


ErrorLogEntry = namedtuple('ErrorLogEntry', 'url filename stacktrace')


def make_outfile_prefix(source_name):
    """
    """
    now = datetime.today()
    date_string = now.strftime('%Y-%m-%d')
    hour_string = now.strftime('%H.%M.%S')
    return os.path.join(source_name, date_string, hour_string)



def make_error_log_entry(url, stacktrace, outdir):
    """
    """
    html_content = fetch_html_content(url)
    outfile = '%s/%s' % (outdir, url)
    #with open(outfile, 'w') as f:
    #    f.write(html_content)

    return ErrorLogEntry(url, outfile, stacktrace)



def write_dict_to_file(d, outdir, source_name, outfile):
    """
    """
    publication_outdir = os.path.join(outdir, make_outfile_prefix(source_name))
    if not os.path.exists(publication_outdir):
        os.makedirs(publication_outdir)

    filename = os.path.join(publication_outdir, outfile)
    with open(filename, 'w') as outfile:
        json.dump(d, outfile)



def fetch_articles_from_toc(toc,  provider):
    articles, errors = [], []

    for (title, url) in toc:
        try:
            article_data = provider.extract_article_data(url)
            articles.append(article_data.to_json())
        except AttributeError as e:
            # this is for logging errors while parsing the dom. If it fails,
            # we should get an AttributeError at some point. We'll keep
            # that in a log, and save the html for future processing.
            stacktrace = traceback.format_stack()
            new_error = make_error_log_entry(url, stacktrace, outdir)
            errors.append(new_error)

    return articles, errors



def fetch_lesoir_articles(outdir):
    """
    """
    os.makedirs(os.path.join(outdir, 'lesoir'))
    frontpage_toc = filter_only_new_stories(lesoir.get_frontpage_toc(),
                                              "{0}/lesoir/last_frontpage_list.json".format(outdir))
    rss_toc = filter_only_new_stories(lesoir.get_rss_toc(),
                                         "{0}/lesoir/last_rss_list.json".format(outdir))

    article_links, blogpost_links = lesoir.separate_articles_from_blogposts(frontpage_toc)

    articles, errors = fetch_articles_from_toc(article_links, lesoir)

    print 'Summary for Le Soir:'
    print """
    articles : {0}
    blogposts : {1}
    errors : {2}""".format(len(articles),
                           len(blogpost_links),
                           len(errors))
    
    all_data = {'articles':articles, 'blogposts':blogpost_links, 'errors':errors}

    write_dict_to_file(all_data, outdir, 'lesoir', 'articles.json') 


    missing = find_stories_missing_from_frontpage(frontpage_toc, rss_toc)
    if missing:
        missing_filename = os.path.join(outdir, make_outfile_prefix('lesoir'), 'missing.json')
        with open(missing_filename, 'w') as f:
            json.dump(missing, f)


def fetch_dhnet_articles(outdir):
    os.makedirs(os.path.join(outdir, 'dhnet'))
    frontpage_toc = filter_only_new_stories(dhnet.get_frontpage_toc(),
                                            "{0}/dhnet/last_frontpage_list.json".format(outdir))

    articles, errors = fetch_articles_from_toc(frontpage_toc, dhnet)
    
    print 'Summary for DHNet:'
    print """
    articles : {0}
    errors : {1}""".format(len(articles),
                           len(errors))
    all_data = {'articles':articles, 'errors':errors}
    write_dict_to_file(all_data, outdir, 'dhnet', 'articles.json')
    


def main(outdir):
    if not os.path.exists(outdir):
        print 'creating output directory:', outdir
        os.mkdir(outdir)
    print 'saving all data to:', outdir

    fetch_lesoir_articles(outdir)
    fetch_dhnet_articles(outdir)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print 'usage : ./crawler.py <outdir>'
