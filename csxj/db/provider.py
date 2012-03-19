"""
Interface over the json database.

This is how a typical database looks like:

- provider1
  - stats.json
  - last_frontpage_list.json
  - YYYY-MM-DD/
    - cached_metainfo.json
    - HH.MM.SS/
        - articles.json
        - raw_data/
            - references.json
            - 0.html
            - 1.html
            - ...
        - reprocessed_YYYY-MM-DD_HH.MM.SS/
            - articles.json
            - raw_data/
                - references.json
                - 0.html
                - 1.html
                - ...
    - HH.MM.SS
    - HH.MM.SS
    - ...
  - YYYY-MM-DD
  - YYYY-MM-DD
  - ...
  - queue
    -

This helper module enables programmatic access to this hierarchy. 
"""

import os, os.path
from collections import namedtuple, defaultdict
import json
import shutil

import utils
from article import ArticleData
from csxj.common.decorators import deprecated
from constants import *




ErrorLogEntry = namedtuple('ErrorLogEntry', 'url filename stacktrace')
ErrorLogEntry2 = namedtuple('ErrorLogEntry2', 'url title stacktrace')

def make_error_log_entry(url, stacktrace, outdir):
    """
    """
    return ErrorLogEntry(url, outdir, stacktrace)


def make_error_log_entry2(url, title, stacktrace):
    """
    """
    return ErrorLogEntry2(url, title, stacktrace)


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
        filename = os.path.join(provider_dir, LAST_STORIES_FILENAME)
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                last_stories_fetched = [tuple(i) for i in  json.load(f)]
                return last_stories_fetched
        else:
            return list()


    def get_source_summary_for_all_days(self):
        """
        Returns a list of (date, article_count, error_count). The date is a string (formatted as: YYYY-MM-DD),
        and counters are integers.

        The list is sorted on the date (earlier date at the front)
        """

        all_days = [d for d in utils.get_subdirectories(self.directory) if d != QUEUE_DIR]
        all_days.sort()
        result = list()
        for date_string in all_days:
            metainfos = self.get_cached_metainfos_for_day(date_string)
            result.append((date_string, metainfos))
        return result


    def get_all_days(self):
        """
        Returns a sorted list of all the dates (formatted as: YYYY-MM-DD) for which there is data available
        """
        all_days = [d for d in utils.get_subdirectories(self.directory) if d != QUEUE_DIR]
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



    def get_batch_articles(self, date_string, batch_time_string):
        """
        Returns the articles saved for a specific first batch.
        This function does not return the articles which might have been reprocessed
        after a (manual) error handling session. You should use the
        get_reprocessed_articles() function for that.

        The function return a sorted list of ArticleData instances.
        The list is sorted using the the article url as key.
        """
        batch_dir = os.path.join(self.directory, date_string, batch_time_string)
        if os.path.exists(batch_dir):
            json_filepath = os.path.join(batch_dir, ARTICLES_FILENAME)
            with open(json_filepath, 'r') as f:
                json_content = json.load(f)
                articles = [ArticleData.from_json(json_string) for json_string in json_content['articles']]
                articles.sort(key=lambda art: art.url)
                return articles
        else:
            raise NonExistentBatchError(self.name, date_string, batch_time_string)


    def get_pending_batch_errors(self, date_string, batch_time_string):
        """
        Returns the pending errors for a specific batch.

        Returns a list of ErrorLogEntry2 instances.
        This list is not sorted.
        """
        batch_dir = os.path.join(self.directory, date_string, batch_time_string)
        if os.path.exists(batch_dir):
            all_errors = list()

            def extract_errors_from_file(ErrorKls, filename):
                with open(filename, 'r') as f:
                    json_content = json.load(f)
                    return [ErrorKls(*error_data) for error_data in json_content['errors']]

            json_filepath = os.path.join(batch_dir, ERRORS_FILENAME)
            if os.path.exists(json_filepath):
                all_errors.append(extract_errors_from_file(ErrorLogEntry, json_filepath))
            else:
                all_errors.append(list())


            json_filepath = os.path.join(batch_dir, ERRORS2_FILENAME)
            if os.path.exists(json_filepath):
                all_errors.append(extract_errors_from_file(ErrorLogEntry2, json_filepath))
            else:
                all_errors.append(list())

            return all_errors
        else:
            raise NonExistentBatchError(self.name, date_string, batch_time_string)



    def has_reprocessed_content(self, date_string, batch_time_string):
        batch_dir = os.path.join(self.directory, date_string, batch_time_string)
        if os.path.exists(batch_dir):
            return len([i for i in utils.get_subdirectories(batch_dir) if i.startswith(REPROCESSED_DIR_PREFIX)]) > 0
        else:
            raise NonExistentBatchError(self.name, date_string, batch_time_string)


    def get_reprocessed_batch_articles(self, date_string, batch_time_string):
        """
        Returns articles fetched during an error handling session.

        ((date_string, hour_string), articles)
        """
        batch_dir = os.path.join(self.directory, date_string, batch_time_string)
        if os.path.exists(batch_dir):
            reprocessed_articles = list()
            for reprocessed_data_dir in [i for i in utils.get_subdirectories(batch_dir) if i.startswith(REPROCESSED_DIR_PREFIX)]:
                reprocessed_date, reprocessed_time = reprocessed_data_dir.split("_")[1:]

                json_filepath = os.path.join(batch_dir, reprocessed_data_dir, ARTICLES_FILENAME)
                with open(json_filepath, 'r') as f:
                    json_content = json.load(f)
                    articles = [ArticleData.from_json(json_string) for json_string in json_content['articles']]
                    articles.sort(key=lambda art: art.url)
                    reprocessed_articles.append(((reprocessed_date, reprocessed_time), articles))
            return reprocessed_articles
        else:
            raise NonExistentBatchError(self.name, date_string, batch_time_string)


    def get_batch_metainfos(self, date_string, batch_time_string):
        """
        Returns a dictionnary with the metainfos associated to the
        given batch.

        Current metainfos are:
            - article_count
            - link_count
            - error_count (not reprocessed yet)
            - total_error_count (after reprocessing)
            - reprocessed_article_count
            _ reprocessed_link_count

        These infos are calculated on the fly after loading the database json files
        """

        def compute_article_and_link_count(articles):
            return len(articles), sum(len(art.links) for art in articles)

        articles = self.get_batch_articles(date_string, batch_time_string)
        article_count, link_count = compute_article_and_link_count(articles)
        errors = self.get_pending_batch_errors(date_string, batch_time_string)
        pending_error_count = len(errors[0]) + len(errors[1])

        reprocessed_articles = self.get_reprocessed_batch_articles(date_string, batch_time_string)
        reprocessed_article_count, reprocessed_link_count = 0, 0
        for (batch_time, reprocessed_articles) in reprocessed_articles:
            article_count, link_count = compute_article_and_link_count(reprocessed_articles)
            reprocessed_article_count += article_count
            reprocessed_link_count += link_count

        total_error_count = pending_error_count + reprocessed_article_count

        metainfos = {
            'article_count':article_count,
            'link_count':link_count,
            'pending_error_count':pending_error_count,
            'total_error_count':total_error_count,
            'reprocessed_article_count':reprocessed_article_count,
            'reprocessed_link_count':reprocessed_link_count
        }

        return metainfos



    def get_cached_metainfos_for_day(self, date_string):
        """
        Returns a dictionary with some cached statistics
        about the content for a particular day.
        """
        day_directory = os.path.join(self.directory, date_string)
        if os.path.exists(day_directory):
            cached_metainfo_file = os.path.join(day_directory, METAINFO_FILENAME)
            if os.path.exists(cached_metainfo_file):
                with open(cached_metainfo_file) as f:
                    cached_metainfo = json.load(f)
                    return cached_metainfo
            else:
                metainfos = defaultdict(int)
                for batch_time_string in self.get_all_batch_hours(date_string):
                    batch_metainfos = self.get_batch_metainfos(date_string, batch_time_string)
                    for k, v in batch_metainfos.items():
                        metainfos[k] += v

                cached_metainfo_file = os.path.join(day_directory, METAINFO_FILENAME)
                with open(cached_metainfo_file, 'w') as f:
                    json.dump(metainfos, f)
                return metainfos
        else:
            raise NonExistentDayError(self.name, date_string)



    def get_cached_metainfos(self):
        """
        Summizes the overall values of the cached metainfo files.

        Returns a dictionnary with metainfo names and their value.
        """
        source_metainfos = defaultdict(int)

        for day in self.get_all_days():
            day_metainfos = self.get_cached_metainfos_for_day(day)
            for k, v in day_metainfos.items():
                source_metainfos[k] += v

        return source_metainfos






    def remove_all_cached_metainfo(self):
        for date_string in self.get_all_days():
            day_directory = os.path.join(self.directory, date_string)
            cached_metainfo_file = os.path.join(day_directory, METAINFO_FILENAME)
            if os.path.exists(cached_metainfo_file):
                os.remove(cached_metainfo_file)





    ### convenience functions: group things per batch
    def get_articles_per_batch(self, date_string):
        """
        Returns a list of (time, [Articles]).
        """
        day_directory = os.path.join(self.directory, date_string)
        if os.path.exists(day_directory):
            all_batch_times = utils.get_subdirectories(day_directory)
            all_batches = []
            for batch_time in all_batch_times:
                articles = self.get_batch_articles(date_string, batch_time)
                all_batches.append((batch_time, articles))
                
            all_batches.sort(key=lambda x: x[0])
            return all_batches
        else:
            raise NonExistentDayError(self.name, date_string)


    def get_errors2_per_batch(self, date_string):
        """
        Returns a list of (time, [errors]).
        """
        day_directory = os.path.join(self.directory, date_string)
        if os.path.exists(day_directory):
            all_batch_times = utils.get_subdirectories(day_directory)
            all_errors = []
            for batch_time in all_batch_times:
                errors = self.get_pending_batch_errors(date_string, batch_time)
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




    def get_deleted_articles_from_batch_directory(self, batch_directory):
        deleted_articles_filename = os.path.join(batch_directory, DELETED_ARTICLES_FILENAME)
        if os.path.exists(deleted_articles_filename):
            with open(deleted_articles_filename, 'r') as f:
                return json.load(f)
        else:
            return {"deleted_articles":[]}


    def get_blogpost_titles_from_batch(self,  day_string, hour_string):
        blogpost_filename = os.path.join(self.directory, day_string, hour_string)
        if os.path.exists(blogpost_filename):
            with open(blogpost_filename) as f:
                return json.load(f)
        else:
            return {"blogposts":[]}


    ### Queue management
    def cleanup_queue(self, day_string):
        """
        Removes the queued items for a certain date. Should be called only after
        a successfull crawling session.
        """
        day_queue_directory = os.path.join(self.directory, QUEUE_DIR, day_string)
        if os.path.exists(day_queue_directory):
            shutil.rmtree(day_queue_directory)

            

    def get_queued_batches_by_day(self):
        """
        Each datasource directory contains a 'queue' directory in which items' urls
        are stored for delayed download.

        Under the 'queue' directory,
        """
        queue_directory = os.path.join(self.directory, QUEUE_DIR)
        batched_days = utils.get_subdirectories(queue_directory)
        batches_by_day = list()
        for day_string in batched_days:
            day_directory = os.path.join(queue_directory, day_string)
            batches_by_day.append((day_string, self.get_queued_items_by_batch(day_directory)))

        batches_by_day.sort(key=lambda day_batches: day_batches[0])
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
        items_by_batch.sort(key=lambda batch: batch[0])
        return items_by_batch



    def get_queued_items_count(self):
        queue_directory = os.path.join(self.directory, QUEUE_DIR)
        batched_days = utils.get_subdirectories(queue_directory)
        item_count = 0

        for day_string in batched_days:
            day_directory = os.path.join(queue_directory, day_string)
            item_count += self.get_item_count_for_day(day_directory)

        return item_count



    #OLD STUFF TO BE REMOVED SOME DAY:
    @deprecated
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


    @deprecated
    def get_item_count_for_day(self, day_directory):
        item_count = 0
        for batch_file in utils.get_json_files(day_directory):
            batch_hour = batch_file[:-5]
            with open(os.path.join(day_directory, batch_file)) as f:
                items = json.load(f)
                item_count += len(items['articles'])
        return item_count


    @deprecated
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


    @deprecated
    def get_articles_and_errorcounts_per_batch(self, date_string):
        """
        Returns a list of (hour_string, [Articles], error_count) for a certain date
        """
        day_directory = os.path.join(self.directory, date_string)
        if os.path.exists(day_directory):
            all_batch_times = utils.get_subdirectories(day_directory)
            all_batches = []
            for batch_time in all_batch_times:
                batch_content = self.get_batch_content(date_string, batch_time)
                articles, batch_error_count = batch_content
                all_batches.append((batch_time, articles, batch_error_count))

            all_batches.sort(key=lambda x: x[0])
            return all_batches
        else:
            raise NonExistentDayError(self.name, date_string)



    @deprecated
    def get_batch_content(self, date_string, batch_time_string):
        """
        Returns the data saved for a specific batch
        """
        batch_dir = os.path.join(self.directory, date_string, batch_time_string)
        if os.path.exists(batch_dir):
            json_filepath = os.path.join(batch_dir, ARTICLES_FILENAME)
            with open(json_filepath, 'r') as f:
                json_content = json.load(f)
                articles = [ArticleData.from_json(json_string) for json_string in json_content['articles']]
                articles.sort(key=lambda art: art.url)
                n_errors = len(json_content['errors'])
                return articles, n_errors
        else:
            raise NonExistentBatchError(self.name, date_string, batch_time_string)


    @deprecated
    def get_errors_from_batch(self, date_string, batch_time_string):
        batch_dir = os.path.join(self.directory, date_string, batch_time_string)
        if os.path.exists(batch_dir):
            json_filepath = os.path.join(batch_dir, ERRORS_FILENAME)
            if os.path.exists(json_filepath):
                with open(json_filepath, 'r') as f:
                    json_content = json.load(f)
                    return [ErrorLogEntry(*error_data) for error_data in json_content['errors']]
            else:
                return None
        else:
            raise NonExistentBatchError(self.name, date_string, batch_time_string)



if __name__=="__main__":
    db_root = "/Users/sevas/Documents/juliette/json_db_allfeeds"
    p = Provider(db_root, "sudpresse")
    from pprint import pprint

    day_string = "2012-02-22"
    hour_string = "14.05.09"


    errors = p.get_pending_batch_errors(day_string, hour_string)

    metainfos = p.get_batch_metainfos(day_string, hour_string)

    print metainfos
