
import os.path
from datetime import datetime
from itertools import chain
from collections import defaultdict
import json


from article import ArticleData
from providerstats import ProviderStats
from provider import Provider
import utils
from csxj.common.decorators import deprecated
from constants import *

def get_all_provider_names(db_root):
    """
    Get the list of providers for which we have data.

    Returns a list of string, one for each content provider.
    """
    subdirs = utils.get_subdirectories(db_root)
    subdirs.sort()
    return subdirs


def get_provider_dump(filename):
    with open(filename, 'r') as f:
        json_content = f.read()
        return json.loads(json_content)


def get_first_and_last_date(db_root):
    source_names = get_all_provider_names(db_root)

    p = Provider(db_root, source_names[0])
    all_days = p.get_all_days()

    return utils.make_date_from_string(all_days[0]), utils.make_date_from_string(all_days[-1])


def get_summed_statistics_for_all_sources(db_root):
    overall_metainfo = defaultdict(int)
    for source_name in get_all_provider_names(db_root):
        p = Provider(db_root, source_name)
        source_metainfo = p.get_cached_metainfos()

        for k, v in source_metainfo.items():
            overall_metainfo[k] += v

    return overall_metainfo


def get_statistics_from_last_update_for_all_sources(db_root):
    last_metainfo_by_day = dict()

    # fetch the summary of the last day for every source
    for source_name in get_all_provider_names(db_root):
        p = Provider(db_root, source_name)
        all_days = p.get_all_days()
        if all_days:
            last_day = utils.get_latest_day(all_days)
            last_metainfo_by_day[source_name] = (last_day, p.get_cached_metainfos_for_day(last_day))

    # not every source has data for the real last day, search for th
    last_days = set([v[0] for k, v in last_metainfo_by_day.items()])
    real_last_day = utils.get_latest_day(last_days)

    # build the overall metainfos using only the source which have data for the real last day
    overall_metainfo = defaultdict(int)
    provider_count = 0
    for name, data in last_metainfo_by_day.items():
        day, metainfos = data
        if day == real_last_day:
            provider_count += 1
            for k, v in metainfos.items():
                overall_metainfo[k] += v

    overall_metainfo.update(dict(provider_count=provider_count))
    return overall_metainfo


def get_summary_from_last_update_for_all_sources(db_root):
    source_names = get_all_provider_names(db_root)

    last_update = list()
    for name in source_names:
        p = Provider(db_root, name)
        all_days = p.get_all_days()
        if all_days:
            last_day = utils.get_latest_day(all_days)

            summary = p.get_cached_metainfos_for_day(last_day)
            last_update.append((name, utils.make_date_from_string(last_day), summary))

    return last_update


def get_queue_error_count_for_all_sources(db_root, day_count=300):
    source_names = get_all_provider_names(db_root)

    all_errors = list()
    for name in source_names:
        p = Provider(db_root, name)
        error_count = p.get_queue_error_count_for_last_days(day_count)
        if error_count:
            all_errors.append((name, error_count))

    return all_errors


def get_queue_errors_for_all_sources(db_root):
    source_names = get_all_provider_names(db_root)

    all_errors = list()
    for name in source_names:
        p = Provider(db_root, name)
        errors = p.get_queue_errors()
        if len(errors):
            all_errors.append((name, errors))

    return all_errors


if __name__ == "__main__":
    from pprint import pprint
    all_errors = get_queue_errors_for_all_sources("/Users/sevas/Documents/juliette/json_db_allfeeds/")
    for name, errors in all_errors:
        print name
        pprint(errors)
