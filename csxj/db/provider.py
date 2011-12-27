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
from collections import namedtuple
import json
import shutil

import utils
from article import ArticleData
from providerstats import ProviderStats



ErrorLogEntry = namedtuple('ErrorLogEntry', 'url filename stacktrace')


def make_error_log_entry(url, stacktrace, outdir):
    """
    """
    outfile = '%s/%s' % (outdir, url)
    return ErrorLogEntry(url, outfile, stacktrace)


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
        all_days = [d for d in utils.get_subdirectories(self.directory) if d != "queue"]
        all_days.sort()
        return all_days


    def get_source_summary_for_all_days(self):
        """
        Returns a list of (date, article_count, error_count). The date is a string (formatted as: YYYY-MM-DD),
        and counters are integers.

        The list is sorted on the date (earlier date at the front)
        """

        all_days = [d for d in utils.get_subdirectories(self.directory) if d != "queue"]
        all_days.sort()
        result = list()
        for date_string in all_days:
            article_count, error_count = self.get_article_and_error_count(date_string)
            result.append((date_string, article_count, error_count))
        return result



    def get_article_and_error_count(self, date_string):
        """
        Returns the number of articles fetched and errors encountered for all the batches in a day.
        """
        article_count, error_count = 0, 0
        for hour_string in self.get_all_batch_hours(date_string):
            articles, batch_error_count = self.get_batch_content(date_string, hour_string)
            article_count += len(articles)
            error_count += batch_error_count
        return article_count, error_count


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



    def get_errors_from_batch(self, date_string, batch_time_string):
        batch_dir = os.path.join(self.directory, date_string, batch_time_string)
        if os.path.exists(batch_dir):
            json_filepath = os.path.join(batch_dir, 'articles.json')
            with open(json_filepath, 'r') as f:
                json_content = json.load(f)

                return [ErrorLogEntry(*error_data) for error_data in json_content['errors']]
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
                articles, error_count = batch_content
                all_batches.append((batch_time, articles))
                
            all_batches.sort(key=lambda x: x[0])
            return all_batches
        else:
            raise NonExistentDayError(self.name, date_string)



    def get_errors_per_batch(self, date_string):
        """
        Returns a list of (time, [errors]).
        """
        day_directory = os.path.join(self.directory, date_string)
        if os.path.exists(day_directory):
            all_batch_times = utils.get_subdirectories(day_directory)
            all_errors = []
            for batch_time in all_batch_times:
                errors = self.get_errors_from_batch(date_string, batch_time)
                all_errors.append((batch_time, errors))
            all_errors.sort(key=lambda x: x[0])
            return all_errors
        
        else:
            raise NonExistentDayError(self.name, date_string)




    def get_data_per_batch(self, date_string, data_extractor_func):
        day_directory = os.path.join(self.directory, date_string)
        if os.path.exists(day_directory):
            all_batch_times = utils.get_subdirectories(day_directory)
            all_data = []
            for batch_time in all_batch_times:
                extracted_data = data_extractor_func(self, date_string, batch_time)
                all_data.append(extracted_data)
            all_data.sort(key=lambda x: x[0])
            return all_data

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

