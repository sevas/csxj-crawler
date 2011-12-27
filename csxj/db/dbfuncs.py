
import os.path
from datetime import datetime
from itertools import chain
import json

from article import ArticleData
from providerstats import ProviderStats
from provider import Provider
import utils



def get_all_provider_names(db_root):
    """
    Get the list of providers for which we have data.

    Returns a list of string, one for each content provider.
    """
    return utils.get_subdirectories(db_root)



def get_provider_dump(filename):
    with open(filename, 'r') as f:
        json_content = f.read()
        return json.loads(json_content)



def collect_stats(all_articles, all_errors):
    num_providers = len(all_articles.keys())
    num_articles =  sum(len(articles) for articles in chain(all_articles.values()))
    num_errors = sum(len(errors) for errors in chain(all_errors.values()))

    return {'num_providers':num_providers, 'num_articles':num_articles, 'num_errors':num_errors}



def get_latest_fetched_articles(db_root):
    providers = utils.get_subdirectories(db_root)

    last_articles = {}
    last_errors = {}

    # todo: fix that shit
    fetched_date = datetime.today().date()

    for provider_name in get_all_provider_names(db_root):
        p = Provider(db_root, provider_name)

        all_days = p.get_all_days()
        last_day = utils.get_latest_day(all_days)


        last_day_dir = os.path.join(p.directory, last_day)
        all_hours = utils.get_subdirectories(last_day_dir)
        last_hour = utils.get_latest_hour(all_hours)

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



def get_last_status_update(db_root):
    fetched_date, articles, errors = get_latest_fetched_articles(db_root)

    stats = collect_stats(articles, errors)
    stats.update({'update_date':fetched_date[0].strftime('%B %d, %Y'),
                 'update_time':fetched_date[1].strftime('%H:%M')})

    return stats



def get_overall_statistics(db_root):
    providers = utils.get_subdirectories(db_root)

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
    sources = utils.get_subdirectories(db_root)

    source_stats = {}
    for source_name in sources:
        stats_filename = os.path.join(db_root, source_name, 'stats.json')
        source_stats[source_name] = ProviderStats.load_from_file(stats_filename)

    return source_stats


