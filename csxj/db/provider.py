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

This helper module enables programmatic access to this hierarchy. 
"""

import os, os.path
from datetime import time, datetime
import json
import shutil

import utils
from article import ArticleData
from providerstats import ProviderStats


class NonExistentDayError(Exception):
    def __init__(self, provider_name, date_string):
        super(NonExistentDayError, self).__init__()
        self.provider_name = provider_name
        self.date_string = date_string


class NonExistentBatchError(Exception):
    def __init__(self, provider_name, date_string, batch_time_string):
        super(NonExistentBatchError, self).__init__()
        self.provider_name = provider_name
        self.date_string = date_string
        self.batch_time_string = batch_time_string


def get_all_provider_names(db_root):
    """
    Get the list of providers for which we have data.

    Returns a list of string, the names of each content provider.
    """
    return utils.get_subdirectories(db_root)



def get_latest_fetched_articles(db_root):
    providers = utils.get_subdirectories(db_root)

    last_articles = dict()
    last_errors = dict()

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
    """
    Programmatic interface to access the data stored for one content provider.
    """
    def __init__(self, db_root, provider_name):
        self.db_root = db_root
        self.name = provider_name


    @property
    def directory(self):
        return os.path.join(self.db_root, self.name)


    def get_last_frontpage_items(self):
        """
        Returns a list of (title, url) for the items fetched on the last query.
        """
        provider_dir = self.directory
        filename = os.path.join(provider_dir, 'last_frontpage_list.json')
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                last_stories_fetched = [tuple(i) for i in  json.load(f)]
                return last_stories_fetched
        else:
            return list()


    def get_all_days(self):
        """
        Returns a sorted list of all the dates (formatted as: YYYY-MM-DD) for which there is data available
        """
        all_days = utils.get_subdirectories(self.directory)
        all_days.sort()
        return all_days



    def get_all_batch_hours(self, date_string):
        """
        For a certain date (YYYY-MM-DD string), returns a list of hours (as HH.MM.SS strings) for which we have data available.
        """
        path = os.path.join(self.directory, date_string)
        if os.path.exists(path):
            all_batches = utils.get_subdirectories(path)
            all_batches.sort()
            return all_batches
        else:
            raise NonExistentDayError(self.name, date_string)


    def get_batch_content(self, date_string, batch_time_string):
        """
        Returns the data saved for a specific batch
        """
        batch_dir = os.path.join(self.directory, date_string, batch_time_string)
        if os.path.exists(batch_dir):
            json_filepath = os.path.join(batch_dir, 'articles.json')
            with open(json_filepath, 'r') as f:
                json_content = json.load(f)
                articles = [ArticleData.from_json(json_string) for json_string in json_content['articles']]
                n_errors = len(json_content['errors'])
                return articles, n_errors
        else:
            raise NonExistentBatchError(self.name, date_string, batch_time_string)


    def get_articles_per_batch(self, date_string):
        """
        Returns a list of (time, [Articles]).
        """
        day_directory = os.path.join(self.directory, date_string)
        if os.path.exists(day_directory):
            all_batch_times = utils.get_subdirectories(day_directory)
            all_batches = []
            for batch_time in all_batch_times:
                batch_content = self.get_batch_content(date_string, batch_time)
                all_batches.append((batch_time, batch_content[0]))
                
            all_batches.sort(key=lambda x: x[0])
            return all_batches
        else:
            raise NonExistentDayError(self.name, date_string)



    def cleanup_queue(self, day_string):
        """

        """
        day_queue_directory = os.path.join(self.directory, "queue", day_string)
        if os.path.exists(day_queue_directory):
            shutil.rmtree(day_queue_directory)

            

    def get_queued_batches_by_day(self):
        """
        Each datasource directory contains a 'queue' directory in which items' urls
        are stored for delayed download.

        Under the 'queue' directory,
        """
        queue_directory = os.path.join(self.directory, "queue")
        batched_days = utils.get_subdirectories(queue_directory)
        batches_by_day = dict()
        for day_string in batched_days:
            day_directory = os.path.join(queue_directory, day_string)
            batches_by_day[day_string] = self.get_queued_items_by_batch(day_directory)

        return batches_by_day



    def get_queued_items_by_batch(self, day_directory):
        """
        Queued items for a day are stored in json files, one for every batch.
        The hierarchy looks like:

         - 2011-26-11/
            - ...
            - 21.00.00.json
            - 22.00.00.json
            - ...

        Every file contains two lists of (title, url) pairs: one for the actual
        news stories, and one for the occasionally promoted blogposts.
        """
        items_by_batch = list()
        for batch_file in utils.get_json_files(day_directory):
            batch_hour = batch_file[:-5]
            with open(os.path.join(day_directory, batch_file)) as f:
                items = json.load(f)
                items_by_batch.append((batch_hour, items))
        return items_by_batch

