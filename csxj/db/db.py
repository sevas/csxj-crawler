"""
Bunch of utility functions to access the data in the json database.
Not meant to be an API just yet.

Directory structure is the following:

- A content provider has a list of subdirectories, one per day (format: YYYY-DD-MM)
- Each day has a list of timed batched (usually, one batch per hour)
- Each batch contains an 'articles.json' file (processed data), as well as a raw_data directory.
- A 'raw_data' directory contains a list of html files. 'The references.json' file is the mapping between
  original URLs and the files on disk
- At the top level, the content provider directory also has a 'stats.json' file. This file gets updated
  everytime the db gets updated. It contains inforamation about the number of articles, links and errors
  for this provider

Things should look like this:

- provider1
  - stats.json
  - YYYY-MM-DD
    - HH.MM.SS
        - articles.json
        - raw_data
            - references.json
            - 0.html
            - 1.html
            - ...

"""


import os, os.path
from datetime import time, datetime
from itertools import chain
import json
from article import ArticleData

import utils

from providerstats import ProviderStats


def get_source_list(db_root):
    return utils.get_subdirectories(db_root)

def get_provider_dump(filename):
    with open(filename, 'r') as f:
        json_content = f.read()
        return json.loads(json_content)



def get_latest_fetched_articles(db_root):
    providers = get_subdirectories(db_root)

    last_articles = {}
    last_errors = {}

    # todo: fix that shit
    fetched_date = datetime.today().date()

    for p in providers:
        provider_dir = os.path.join(db_root, p)
        all_days = utils.get_subdirectories(provider_dir)
        last_day = get_latest_day(all_days)

        last_day_dir = os.path.join(provider_dir, last_day)
        all_hours = get_subdirectories(last_day_dir)
        last_hour = get_latest_hour(all_hours)

        fetched_date = utils.make_date_time_from_string(last_day, last_hour)

        filename = os.path.join(last_day_dir, last_hour, 'articles.json')

        dump = get_provider_dump(filename)

        articles, errors = [], []
        for article in dump['articles']:
            articles.append(ArticleData.from_json(article))

        for error in dump['errors']:
            errors.append(error)

        last_articles[p] = articles
        last_errors[p] = errors

    return fetched_date, last_articles, last_errors



def collect_stats(all_articles, all_errors):
    num_providers = len(all_articles.keys())
    num_articles =  sum(len(articles) for articles in chain(all_articles.values()))
    num_errors = sum(len(errors) for errors in chain(all_errors.values()))

    return {'num_providers':num_providers, 'num_articles':num_articles, 'num_errors':num_errors}


def get_last_status_update(db_root):
    fetched_date, articles, errors = get_latest_fetched_articles(db_root)

    stats = collect_stats(articles, errors)
    stats.update({'update_date':fetched_date[0].strftime('%B %d, %Y'),
                 'update_time':fetched_date[1].strftime('%H:%M')})

    return stats



def get_overall_statistics(db_root):
    providers = get_subdirectories(db_root)

    overall_stats = {'total_articles':0, 'total_errors':0, 'total_links':0, 'start_date':None, 'end_date':None}
    for p in providers:
        stats_filename = os.path.join(db_root, p, 'stats.json')
        provider_stats = ProviderStats.load_from_file(stats_filename)

        overall_stats['total_articles'] += provider_stats.n_articles
        overall_stats['total_errors'] += provider_stats.n_errors
        overall_stats['total_links'] += provider_stats.n_links
        overall_stats['start_date'] = provider_stats.start_date
        overall_stats['end_date'] = provider_stats.end_date

    return overall_stats


def make_overall_statistics(source_statistics):
    overall_stats = {'total_articles':0, 'total_errors':0, 'total_links':0, 'start_date':None, 'end_date':None}
    for (name, provider_stats) in source_statistics.items():
        overall_stats['total_articles'] += provider_stats.n_articles
        overall_stats['total_errors'] += provider_stats.n_errors
        overall_stats['total_links'] += provider_stats.n_links
        overall_stats['start_date'] = provider_stats.start_date
        overall_stats['end_date'] = provider_stats.end_date

    return overall_stats


def get_per_source_statistics(db_root):
    sources = get_subdirectories(db_root)

    source_stats = {}
    for source_name in sources:
        stats_filename = os.path.join(db_root, source_name, 'stats.json')
        source_stats[source_name] = ProviderStats.load_from_file(stats_filename)

    return source_stats


def get_all_days(db_root, source_name):
    all_days = get_subdirectories(os.path.join(db_root, source_name))
    all_days.sort()
    return all_days


def get_articles_per_batch(db_root, source_name, date_string):
    path = os.path.join(db_root, source_name, date_string)

    all_batch_times = get_subdirectories(path)
    all_batches = []
    for batch_time in all_batch_times:
        json_file = os.path.join(path, batch_time, 'articles.json')
        with open(json_file, 'r') as f:
            json_content = json.load(f)
            articles = [ArticleData.from_json(json_string) for json_string in json_content['articles']]
            n_errors = len(json_content['errors'])
            all_batches.append((batch_time, articles, n_errors))

    all_batches.sort(key=lambda x: x[0])
    return all_batches



def get_all_batches(db_root, source_name, date_string):
    path = os.path.join(db_root, source_name, date_string)
    all_batches = get_subdirectories(path)
    all_batches.sort()
    return all_batches


def get_articles_and_errors_from_batch(db_root, source_name, date_string, batch_time):
     json_file = os.path.join(db_root, source_name, date_string, batch_time, 'articles.json')
     with open(json_file, 'r') as f:
        json_content = json.load(f)
        articles = [ArticleData.from_json(json_string) for json_string in json_content['articles']]
        errors = json_content['errors']
        return articles, errors