"""
Interface over the json database.

This is how a typical database looks like:

- provider1
  - stats.json
  - last_frontpage_list.json
  - YYYY-MM-DD
    - HH.MM.SS
        - articles.json
        - raw_data
            - references.json
            - 0.html
            - 1.html
            - ...
  - queue
    -

This helper module enables programmatic access to this hierarchy. No data is
parsed or loaded here. We only allow to iterate over the directories.


"""

import os, os.path
from datetime import time, datetime
from itertools import chain
import utils


def get_all_provider_names(db_root):
    """
    Get the list of providers for which we have data.

    Returns a list of string, one for each content provider.
    """
    return utils.get_subdirectories(db_root)


def get_latest_fetched_articles(db_root):
    providers = utils.get_subdirectories(db_root)

    last_articles = {}
    last_errors = {}

    # todo: fix that shit
    fetched_date = datetime.today().date()

    for p in providers:
        provider_dir = os.path.join(db_root, p)
        all_days = utils.get_subdirectories(provider_dir)
        last_day = utils.get_latest_day(all_days)

        last_day_dir = os.path.join(provider_dir, last_day)
        all_hours = utils.get_subdirectories(last_day_dir)
        last_hour = utils.get_latest_hour(all_hours)

        fetched_date = utils.make_date_time_from_string(last_day, last_hour)

        filename = os.path.join(last_day_dir, last_hour, 'articles.json')
        return filename



class Provider(object):
    def __init__(self, db_root, provider_name):
        self.root = db_root
        self.name = provider_name

    