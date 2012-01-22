import sys
import os, os.path
from datetime import datetime
import json
import utils
import logging
import traceback

from db import Provider, ProviderStats, make_error_log_entry
from db.constants import *


def write_dict_to_file(d, outdir, outfile):
    """
    """
    publication_outdir = outdir
    if not os.path.exists(publication_outdir):
        os.makedirs(publication_outdir)

    filename = os.path.join(publication_outdir, outfile)
    with open(filename, 'w') as outfile:
        json.dump(d, outfile)





class ArticleQueueFiller(object):
    log_name = "csxj_QueueFiller.log"
    def __init__(self, source, source_name, db_root):
        self.source = source
        self.source_name = source_name
        self.db_root = db_root
        self.new_stories = list()
        self.root = os.path.join(db_root, source_name)



    def make_log_message(self, message):
        return u"[{0}] {1}".format(self.source_name, message)



    def log_info(self, message):
        self.log.info(self.make_log_message(message))



    def log_error(self, message):
        self.log.error(self.make_log_message(message))


    @classmethod
    def setup_logging(cls):
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)

        file_formatter = logging.Formatter('%(asctime)s [%(levelname)s:] %(message)s')
        file_handler = logging.FileHandler(os.path.join(LOG_PATH, cls.log_name))
        file_handler.setFormatter(file_formatter)

        stream_formatter = logging.Formatter("[%(levelname)s]  %(message)s")
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(stream_formatter)
        
        cls.log = logging.getLogger("csxj_QueueFiller")
        cls.log.setLevel(logging.INFO)
        cls.log.addHandler(file_handler)
        cls.log.addHandler(stream_handler)
        



    def fetch_newest_article_links(self):
        outdir = os.path.join(self.db_root, self.source_name)
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        frontpage_toc, blogposts_toc = self.source.get_frontpage_toc()
        self.log_info("Found {0} stories and {1} blogposts on frontpage".format(len(frontpage_toc),
                                                                                 len(blogposts_toc)))

        last_stories_filename = os.path.join(self.db_root,
                                             self.source_name,
                                             LAST_STORIES_FILENAME)
        last_blogposts_filename = os.path.join(self.db_root,
                                               self.source_name,
                                               LAST_BLOGPOSTS_FILENAME)

        self.new_stories = utils.filter_only_new_stories(frontpage_toc, last_stories_filename)
        self.new_blogposts = utils.filter_only_new_stories(blogposts_toc, last_blogposts_filename)

        self.log_info("Found {0} new stories and {1} new blogposts since last time".format(len(self.new_stories),
                                                                                           len(self.new_blogposts)))



    def update_global_queue(self):
        today = datetime.today()

        day_str = today.strftime("%Y-%m-%d")
        day_directory = os.path.join(self.root, "queue", day_str)
        
        if not os.path.exists(day_directory):
            os.makedirs(day_directory)

        batch_hour_str = today.strftime("%H.%M.%S")
        batch_filename = "{0}.json".format(os.path.join(day_directory, batch_hour_str))

        self.log.info(self.make_log_message("Saving toc to {0}".format(batch_filename)))
        with open(batch_filename, "w") as f:
            self.log.info(self.make_log_message("Enqueuing {0} new stories and {1} blogposts".format(len(self.new_stories),
                                                                                                     len(self.new_blogposts))))
            json.dump({"articles":self.new_stories, "blogposts":self.new_blogposts}, f)

            


class ArticleQueueDownloader(object):
    log_name = "csxj_QueueDownloader.log"
    def __init__(self, source, source_name, db_root, debug_mode=True):
        self.db_root = db_root
        self.source = source
        self.source_name = source_name
        self.downloaded_articles = []
        self.debug_mode = debug_mode



    def make_log_message(self, message):
        return u"[{0}] {1}".format(self.source_name, message)



    def log_info(self, message):
        self.log.info(self.make_log_message(message))



    @classmethod
    def setup_logging(cls):
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)

        file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        file_handler = logging.FileHandler(os.path.join(LOG_PATH, cls.log_name))
        file_handler.setFormatter(file_formatter)

        stream_formatter = logging.Formatter("[%(levelname)s]  %(message)s")
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(stream_formatter)

        cls.log = logging.getLogger(cls.log_name)
        cls.log.setLevel(logging.INFO)
        cls.log.addHandler(file_handler)
        cls.log.addHandler(stream_handler)



    def download_all_articles_in_queue(self):
        provider_db = Provider(self.db_root, self.source_name)
        queued_items = provider_db.get_queued_batches_by_day()

        if queued_items:
            for (day_string, batches) in queued_items:
                self.log_info("Downloading {0} batches for {1}".format(len(batches), day_string))
                day_directory = os.path.join(self.db_root, self.source_name, day_string)
                for (i, batch) in enumerate(batches):
                    batch_hour_string, items = batch
                    self.log.info(self.make_log_message("Downloading {0} articles for batch#{1} ({2})".format(len(items['articles']), i, batch_hour_string)))

                    articles, deleted_articles, errors, raw_data = self.download_batch(items['articles'])

                    self.log_info("Found data for {0} articles ({1} errors)".format(len(articles),
                                                                                    len(errors)))
                    batch_output_directory = os.path.join(day_directory, batch_hour_string)
                    self.save_articles_to_db(articles, deleted_articles, errors, items['blogposts'], batch_output_directory)
                    self.save_raw_data_to_db(raw_data, batch_output_directory)
                    self.update_provider_stats(os.path.join(self.db_root, self.source_name), articles, errors)

                self.log_info("Removing queue directory")
                provider_db.cleanup_queue(day_string)
        else:
            self.log_info("Empty queue. Nothing to do.")



    def download_batch(self, items):
        articles, deleted_articles, errors, raw_data = list(), list(), list(), list()
        for title, url in items:
            try:
                article_data, html_content = self.source.extract_article_data(url)
                if article_data:
                    articles.append(article_data)
                    raw_data.append((url, html_content))
                else:
                    deleted_articles.append((title, url))
            except Exception as e:
                if e.__class__ in [AttributeError]:
                    # this is for logging errors while parsing the dom. If it fails,
                    # we should get an AttributeError at some point. We'll keep
                    # that in a log, and save the html for future processing.
                    stacktrace = traceback.format_exc()
                    new_error = make_error_log_entry2(url, title, stacktrace)
                    errors.append(new_error)
                else:
                    if self.debug_mode:
                        # when developing, it's useful to not hide the exception
                        raise e
                    else:
                        # but in production, log everything
                        stacktrace = traceback.format_exc()
                        new_error = make_error_log_entry(url, stacktrace, self.db_root)
                        errors.append(new_error)

        return articles, deleted_articles, errors, raw_data



    def save_articles_to_db(self, articles, deleted_articles, errors, blogposts, outdir):
        all_data = {'articles':[art.to_json() for art in  articles],
                    'errors':[]}

        self.log_info("Writing {0} articles to {1}".format(len(articles), os.path.join(outdir, ARTICLES_FILENAME)))
        write_dict_to_file(all_data, outdir, ARTICLES_FILENAME)

        blogposts_data = {'blogposts':blogposts}
        self.log_info("Writing {0} blogpost links to {1}".format(len(blogposts), os.path.join(outdir, BLOGPOSTS_FILENAME)))
        write_dict_to_file(blogposts_data, outdir, BLOGPOSTS_FILENAME)

        deleted_articles_data = {'deleted_articles':deleted_articles}
        self.log_info("Writing {0} links to deleted articles to {1}".format(len(deleted_articles), os.path.join(outdir, DELETED_ARTICLES_FILENAME)))
        write_dict_to_file(deleted_articles_data, outdir, DELETED_ARTICLES_FILENAME)

        self.log_info("Writing {0} errors to {1}".format(len(errors), os.path.join(outdir, ERRORS2_FILENAME)))
        write_dict_to_file({'errors':errors}, outdir, ERRORS2_FILENAME)



    def save_raw_data_to_db(self, raw_data, batch_outdir):
        """
        """
        self.log_info("Writing raw html data to {0}".format(os.path.join(batch_outdir, RAW_DATA_DIR)))
        
        raw_data_dir = os.path.join(batch_outdir, RAW_DATA_DIR)
        if not os.path.exists(raw_data_dir):
            os.mkdir(raw_data_dir)
        references = []
        for (i, (url, html_content)) in enumerate(raw_data):
            outfilename = "{0}.html".format(i)
            with open(os.path.join(raw_data_dir, outfilename), 'w') as f:
                f.write(html_content)
            references.append((url, outfilename))

        with open(os.path.join(raw_data_dir, RAW_DATA_INDEX_FILENAME), 'w') as f:
            json.dump(references, f)


    def update_provider_stats(self, outdir, articles, errors):
        stats_filename = os.path.join(outdir, 'stats.json')
        if not os.path.exists(stats_filename):
            self.log_info("Creating stats file: {0}".format(stats_filename))
            init_stats = ProviderStats.make_init_instance()
            init_stats.save_to_file(stats_filename)

        try:
            self.log_info("Restoring stats from file {0} ".format(stats_filename))
            current_stats = ProviderStats.load_from_file(stats_filename)
            current_stats.n_articles += len(articles)
            current_stats.n_errors += len(errors)
            current_stats.n_dumps += 1
            current_stats.end_date = datetime.today()
            current_stats.n_links += sum([(len(art.external_links) + len(art.internal_links)) for art in articles])
            current_stats.save_to_file(stats_filename)
        except Exception as e:
            self.log_info(str(e))



        

def test_filler(json_db):
    from datasources import lesoir, lalibre
    ArticleQueueFiller.setup_logging()
    for source in [lesoir, lalibre]:
        queue_filler = ArticleQueueFiller(source, source.SOURCE_NAME, json_db)
        queue_filler.fetch_newest_article_links()
        queue_filler.update_global_queue()
    


def test_downloader(json_db):
    ArticleQueueDownloader.setup_logging()
    from datasources import rtlinfo
    for source in [rtlinfo]:
        queue_downloader = ArticleQueueDownloader(source, source.SOURCE_NAME, json_db)
        queue_downloader.download_all_articles_in_queue()



def main(json_db):
    #test_filler(json_db)
    test_downloader(json_db)
