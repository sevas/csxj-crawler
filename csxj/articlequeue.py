# Coding=utf8
import sys
import os
from datetime import datetime
import json
import utils
import logging
import traceback

from csxj.common.decorators import deprecated
from csxj.datasources.parser_tools.utils import fetch_html_content
from csxj.datasources.parser_tools.utils import convert_utf8_url_to_ascii
from csxj.datasources.parser_tools import constants

from db import Provider, ProviderStats, make_error_log_entry2
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
        self.new_blogposts = list()
        self.new_paywalled_articles = list()
        self.root = os.path.join(db_root, source_name)

    def make_log_message(self, message):
        return u"[{0}] {1}".format(self.source_name, message)

    def log_info(self, message):
        self.log.info(self.make_log_message(message))

    def log_error(self, message):
        self.log.error(u"[{0}] !!! {1}".format(self.source_name, message))

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

        try:
            frontpage_toc, blogposts_toc, paywalled_articles = self.source.get_frontpage_toc()
            self.log_info(u"Found {0} stories, {1} blogposts and {2} paywalled articles on the frontpage".format(len(frontpage_toc),
                                                                                                                 len(blogposts_toc),
                                                                                                                 len(paywalled_articles)))
            if len(frontpage_toc):
                last_stories_filename = os.path.join(self.db_root,
                                                     self.source_name,
                                                     LAST_STORIES_FILENAME)
                last_blogposts_filename = os.path.join(self.db_root,
                                                       self.source_name,
                                                       LAST_BLOGPOSTS_FILENAME)
                last_paywalled_articles_filename = os.path.join(self.db_root,
                                                                self.source_name,
                                                                LAST_PAYWALLED_ARTICLES_FILENAME)

                self.new_stories = utils.filter_only_new_stories(frontpage_toc, last_stories_filename)
                self.new_blogposts = utils.filter_only_new_stories(blogposts_toc, last_blogposts_filename)
                self.new_paywalled_articles = utils.filter_only_new_stories(paywalled_articles, last_paywalled_articles_filename)

                self.log_info(u"Found {0} new stories, {1} new blogposts and {2} new paywalled articles since last time".format(len(self.new_stories),
                                                                                                                                len(self.new_blogposts),
                                                                                                                                len(self.new_paywalled_articles)))
                self.update_global_queue()
            else:
                self.log_error(u"Found no headlines on the frontpage. Updating error log")
                self.update_queue_error_log("*** No link were extracted from the frontpage")

        except Exception:
            self.log_error(u"Something went wrong while fetching new frontpage headlines. Updating error log")
            stacktrace = traceback.format_exc()
            self.update_queue_error_log(stacktrace)

    def update_queue_error_log(self, stacktrace):
        """
        """
        error_log_file = os.path.join(self.root, QUEUE_ERROR_LOG_FILENAME)

        if(os.path.exists(error_log_file)):
            f = open(error_log_file, 'r')
            queue_error_log = json.load(f)
            f.close()
        else:
            queue_error_log = dict()

        today = datetime.today()
        day_str = today.strftime("%Y-%m-%d")
        batch_hour_str = today.strftime("%H.%M.%S")

        if day_str in queue_error_log:
            queue_error_log[day_str][batch_hour_str] = stacktrace
        else:
            queue_error_log[day_str] = {batch_hour_str: stacktrace}

        with open(error_log_file, 'w') as f:
            json.dump(queue_error_log, f)

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
            self.log.info(self.make_log_message("Enqueuing {0} new stories, {1} blogposts and {2} paywalled articles".format(len(self.new_stories),
                                                                                                                             len(self.new_blogposts),
                                                                                                                             len(self.new_paywalled_articles))))
            json.dump({"articles": self.new_stories, "blogposts": self.new_blogposts, "paywalled_articles": self.new_paywalled_articles}, f)


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

    def log_error(self, message):
        self.log.error(u"[{0}] !!! {1}".format(self.source_name, message))

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
                self.log_info(u"Downloading {0} batches for {1}".format(len(batches), day_string))
                day_directory = os.path.join(self.db_root, self.source_name, day_string)
                for (i, batch) in enumerate(batches):
                    batch_hour_string, items = batch

                    news_items, junk = self.source.filter_news_items(items['articles'])
                    if junk:
                        self.log.info(self.make_log_message("Found {0} articles which are not actually news".format(len(junk))))

                    self.log.info(self.make_log_message("Downloading {0} articles for batch#{1} ({2})".format(len(news_items), i, batch_hour_string)))
                    articles, detected_paywalled_articles, deleted_articles, errors, raw_data = self.download_batch(news_items)

                    self.log_info(u"Found data for {0} articles ({1} errors)".format(len(articles),
                                                                                     len(errors)))
                    batch_output_directory = os.path.join(day_directory, batch_hour_string)
                    self.save_articles_to_db(articles, deleted_articles, errors, items['blogposts']+junk, batch_output_directory)

                    # paywalled stuff
                    if 'paywalled_articles' not in items:
                        items['paywalled_articles'] = []
                    all_paywalled_articles = items['paywalled_articles'] + detected_paywalled_articles
                    self.log_info(u"Writing {0} paywalled article links to {1}".format(len(all_paywalled_articles), os.path.join(batch_output_directory, PAYWALLED_ARTICLES_FILENAME)))
                    write_dict_to_file(dict(paywalled_articles=all_paywalled_articles), batch_output_directory, PAYWALLED_ARTICLES_FILENAME)

                    # raw data
                    self.save_raw_data_to_db(raw_data, batch_output_directory)
                    self.save_errors_raw_data_to_db(errors, batch_output_directory)

                self.log_info(u"Removing queue directory for day: {0}".format(day_string))
                provider_db.cleanup_queue(day_string)
        else:
            self.log_info(u"Empty queue. Nothing to do.")

    def download_batch(self, items):
        articles, detected_paywalled_articles, deleted_articles, errors, raw_data = list(), list(), list(), list(), list()
        for title, url in items:
            try:
                article_data, html_content = self.source.extract_article_data(url)
                if article_data:
                    if article_data.content == constants.PAYWALLED_CONTENT:
                        detected_paywalled_articles.append((article_data.title, article_data.url))
                    else:
                        articles.append(article_data)
                        raw_data.append((url, html_content))
                else:
                    deleted_articles.append((title, url))
            except Exception:
                # log all the things
                stacktrace = traceback.format_exc()
                new_error = make_error_log_entry2(url, title, stacktrace)
                errors.append(new_error)

        return articles, detected_paywalled_articles, deleted_articles, errors, raw_data

    def save_articles_to_db(self, articles, deleted_articles, errors, blogposts, outdir):
        all_data = {'articles': [art.to_json() for art in articles],
                    'errors': []}

        self.log_info(u"Writing {0} articles to {1}".format(len(articles), os.path.join(outdir, ARTICLES_FILENAME)))
        write_dict_to_file(all_data, outdir, ARTICLES_FILENAME)

        blogposts_data = {'blogposts': blogposts}
        self.log_info(u"Writing {0} blogpost links to {1}".format(len(blogposts), os.path.join(outdir, BLOGPOSTS_FILENAME)))
        write_dict_to_file(blogposts_data, outdir, BLOGPOSTS_FILENAME)

        deleted_articles_data = {'deleted_articles': deleted_articles}
        self.log_info(u"Writing {0} links to deleted articles to {1}".format(len(deleted_articles), os.path.join(outdir, DELETED_ARTICLES_FILENAME)))
        write_dict_to_file(deleted_articles_data, outdir, DELETED_ARTICLES_FILENAME)

        self.log_info(u"Writing {0} errors to {1}".format(len(errors), os.path.join(outdir, ERRORS2_FILENAME)))
        write_dict_to_file({'errors': errors}, outdir, ERRORS2_FILENAME)

    def save_raw_data_to_db(self, raw_data, batch_outdir):
        """
        """
        raw_data_dir = os.path.join(batch_outdir, RAW_DATA_DIR)
        self.log_info(u"Writing raw html data to {0}".format(raw_data_dir))
        self.save_raw_data_to_path(raw_data, raw_data_dir)

    def save_errors_raw_data_to_db(self, errors, batch_outdir):
        """
        """
        raw_data = list()
        for i, error in enumerate(errors):
            url, _, _ = error
            try:
                url = convert_utf8_url_to_ascii(url)
                html_content = fetch_html_content(url)
                raw_data.append((url, html_content))
            except:
                self.log_error(u"Could not fetch raw html data for error'd url: {0} (Reason: {1})".format([url], traceback.format_exc()))
                continue

        raw_data_dir = os.path.join(batch_outdir, ERRORS_RAW_DATA_DIR)
        self.log_info(u"Writing raw html data to {0}".format(raw_data_dir))
        self.save_raw_data_to_path(raw_data, raw_data_dir)

    def save_raw_data_to_path(self, raw_data, root_path):
        raw_data_dir = root_path
        if not os.path.exists(raw_data_dir):
            os.mkdir(raw_data_dir)
        references = []
        for (i, (url, html_content)) in enumerate(raw_data):
            outfilename = u"{0}.html".format(i)
            with open(os.path.join(raw_data_dir, outfilename), 'w') as f:
                f.write(html_content)
            references.append((url, outfilename))

        with open(os.path.join(raw_data_dir, RAW_DATA_INDEX_FILENAME), 'w') as f:
            json.dump(references, f)

    @deprecated
    def update_provider_stats(self, outdir, articles, errors):
        stats_filename = os.path.join(outdir, 'stats.json')
        if not os.path.exists(stats_filename):
            self.log_info(u"Creating stats file: {0}".format(stats_filename))
            init_stats = ProviderStats.make_init_instance()
            init_stats.save_to_file(stats_filename)

        try:
            self.log_info(u"Restoring stats from file {0} ".format(stats_filename))
            current_stats = ProviderStats.load_from_file(stats_filename)
            current_stats.n_articles += len(articles)
            current_stats.n_errors += len(errors)
            current_stats.n_dumps += 1
            current_stats.end_date = datetime.today()
            current_stats.n_links += sum([(len(art.other_links) + len(art.internal_links)) for art in articles])
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
    from datasources import septsursept
    for source in [septsursept]:
        queue_downloader = ArticleQueueDownloader(source, source.SOURCE_NAME, json_db)
        queue_downloader.download_all_articles_in_queue()
