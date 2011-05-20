#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os, os.path
from collections import namedtuple
import traceback
from datetime import datetime

from parsers import lesoir, dhnet, lalibre, sudpresse, rtlinfo
from parsers.utils import fetch_html_content
from providerstats import ProviderStats
import json

DEBUG_MODE = True


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


def make_outfile_prefix():
    """
    """
    now = datetime.today()
    date_string = now.strftime('%Y-%m-%d')
    hour_string = now.strftime('%H.%M.%S')
    return os.path.join(date_string, hour_string)



def make_error_log_entry(url, stacktrace, outdir):
    """
    """
    html_content = fetch_html_content(url)
    outfile = '%s/%s' % (outdir, url)
    #with open(outfile, 'w') as f:
    #    f.write(html_content)

    return ErrorLogEntry(url, outfile, stacktrace)



def write_dict_to_file(d, outdir, outfile):
    """
    """
    publication_outdir = outdir
    if not os.path.exists(publication_outdir):
        os.makedirs(publication_outdir)

    filename = os.path.join(publication_outdir, outfile)
    with open(filename, 'w') as outfile:
        json.dump(d, outfile)



def fetch_articles_from_toc(toc,  provider, outdir):
    articles, errors, raw_data = [], [], []

    for (title, url) in toc:
        try:
            article_data, raw_html_content = provider.extract_article_data(url)
            if article_data:
                articles.append(article_data)
                raw_data.append((url, raw_html_content))
        except Exception as e:
            if e.__class__ in [AttributeError]:
                # this is for logging errors while parsing the dom. If it fails,
                # we should get an AttributeError at some point. We'll keep
                # that in a log, and save the html for future processing.
                stacktrace = traceback.format_stack()
                new_error = make_error_log_entry(url, stacktrace, outdir)
                errors.append(new_error)
            else:
                if DEBUG_MODE:
                    # when developing, it's useful to not hide the exception
                    raise e
                else:
                    # but in production, log everything
                    stacktrace = traceback.format_stack()
                    new_error = make_error_log_entry(url, stacktrace, outdir)
                    errors.append(new_error)

    return articles, errors, raw_data



def update_provider_stats(outdir, articles, errors):
    stats_filename = os.path.join(outdir, 'stats.json')
    if not os.path.exists(stats_filename):
        print 'creating stats file:', stats_filename
        init_stats = ProviderStats.make_init_instance()
        init_stats.save_to_file(stats_filename)

    current_stats = ProviderStats.load_from_file(stats_filename)
    current_stats.n_articles += len(articles)
    current_stats.n_errors += len(errors)
    current_stats.n_dumps += 1
    current_stats.end_date = datetime.today()
    current_stats.n_links += sum([(len(art.external_links) + len(art.internal_links)) for art in articles])

    current_stats.save_to_file(stats_filename)



def save_raw_data(raw_data, batch_outdir):
    """
    """
    raw_data_dir = os.path.join(batch_outdir, 'raw_data')
    os.mkdir(raw_data_dir)
    references = []
    for (i, (url, html_content)) in enumerate(raw_data):
        outfilename = "{0}.html".format(i)
        with open(os.path.join(raw_data_dir, outfilename), 'w') as f:
            f.write(html_content)
        references.append((url, outfilename))

    with open(os.path.join(raw_data_dir, 'references.json'), 'w') as f:
        json.dump(references, f)

        

def fetch_lesoir_articles(prefix):
    """
    """
    outdir = os.path.join(prefix, 'lesoir')
    if not os.path.exists(outdir):
        os.makedirs(outdir)


    articles_toc, blogposts_toc = lesoir.get_frontpage_toc()
    blogposts_toc = list(filter_only_new_stories(blogposts_toc,
                                            os.path.join(outdir, 'last_blogposts_list.json')))
    

    new_articles_toc = filter_only_new_stories(articles_toc,
                                               os.path.join(outdir, 'last_frontpage_list.json'))

    rss_toc = filter_only_new_stories(lesoir.get_rss_toc(),
                                      os.path.join(outdir, 'last_rss_list.json'))


    articles, errors, raw_data = fetch_articles_from_toc(new_articles_toc, lesoir, outdir)

    print 'Summary for Le Soir:'
    print """
    articles : {0}
    blogposts : {1}
    errors : {2}""".format(len(articles),
                           len(blogposts_toc),
                           len(errors))
    
    all_data = {'articles':[art.to_json() for art in  articles],
                'blogposts':blogposts_toc,
                'errors':errors}



    batch_outdir = os.path.join(outdir, make_outfile_prefix())

    write_dict_to_file(all_data, batch_outdir, 'articles.json')
    update_provider_stats(outdir, articles, errors)

    missing = find_stories_missing_from_frontpage(articles_toc, rss_toc)
    if missing:
        missing_filename = os.path.join(batch_outdir, 'missing.json')
        with open(missing_filename, 'w') as f:
            json.dump(missing, f)


    save_raw_data(raw_data, batch_outdir)



def crawl_once(provider, provider_name, provider_title, prefix):
    outdir = os.path.join(prefix, provider_name)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    news_toc, blogposts_toc = provider.get_frontpage_toc()
    frontpage_toc = filter_only_new_stories(news_toc,
                                            os.path.join(outdir, 'last_frontpage_list.json'))

    articles, errors, raw_data = fetch_articles_from_toc(frontpage_toc, provider, outdir)

    print 'Summary for {0}:'.format(provider_title)
    print """
    articles : {0}
    errors : {1}""".format(len(articles),
                           len(errors))

    all_data = {'articles':[art.to_json() for art in  articles],
                'errors':errors}

    blogposts_data = {'blogposts':blogposts_toc}

    batch_outdir = os.path.join(outdir, make_outfile_prefix())
    write_dict_to_file(all_data, batch_outdir, 'articles.json')
    write_dict_to_file(blogposts_data, batch_outdir, 'blogposts.json')
    update_provider_stats(outdir, articles, errors)
    save_raw_data(raw_data, batch_outdir)



def fetch_dhnet_articles(prefix):
    crawl_once(dhnet, 'dhnet', 'DHNet', prefix)


def fetch_lalibre_articles(prefix):
    crawl_once(lalibre, 'lalibre', 'La Libre', prefix)


def fetch_sudpresse_articles(prefix):
    crawl_once(sudpresse, 'sudpresse', 'Sud Presse', prefix)


def fetch_rtlinfo_articles(prefix):
    crawl_once(rtlinfo, 'rtlinfo', 'RTLInfo', prefix)

def main(outdir):
    if not os.path.exists(outdir):
        print 'creating output directory:', outdir
        os.mkdir(outdir)

    print '-' * 30

    print datetime.today().strftime('New articles saved on %d/%m/%Y at %H:%S')

    fetch_lesoir_articles(outdir)
    fetch_dhnet_articles(outdir)
    fetch_lalibre_articles(outdir)
    fetch_sudpresse_articles(outdir)
    fetch_rtlinfo_articles(outdir)

    
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch pages from news sources, dumps interesting data')
    parser.add_argument('--debug', dest='debug', action='store_true', help="run crawler in debug mode")
    parser.add_argument('--outdir', type=str, dest='outdir', required=True, help='directory to dump the json db in')

    args = parser.parse_args()
    DEBUG_MODE = args.debug
    main(args.outdir)
    

