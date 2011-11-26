import sys
import os, os.path
from datetime import datetime
import json
import utils
import logging


from db import Provider

LAST_STORIES_FILENAME='last_frontpage_list.json'
LAST_BLOGPOSTS_FILENAME='last_blogposts_list.json'


def make_queued_batch_filename():
    pass



class ArticleQueueFiller(object):
    def __init__(self, provider, provider_name, prefix):
        self.provider = provider
        self.provider_name = provider_name
        self.prefix = prefix
        self.new_stories = list()
        self.root = os.path.join(prefix, provider_name)
        self.setup_logging()



    def setup_logging(self):
        if not os.path.exists("logs"):
            os.mkdir("logs")
            
        file_formatter = logging.Formatter('%(asctime)s [%(levelname)s:{0}] %(message)s'.format(self.provider_name))
        file_handler = logging.FileHandler("logs/csxj_QueueFiller.log")
        file_handler.setFormatter(file_formatter)

        stream_formatter = logging.Formatter("[%(levelname)s:{0}]  %(message)s".format(self.provider_name))
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(stream_formatter)
        
        self.log = logging.getLogger("csxj_QueueFiller")
        self.log.setLevel(logging.INFO)
        self.log.addHandler(file_handler)
        self.log.addHandler(stream_handler)



    def fetch_newest_article_links(self):
        outdir = os.path.join(self.prefix, self.provider_name)
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        frontpage_toc, blogposts_toc = self.provider.get_frontpage_toc()
        self.log.info("Found {0} stories and {1} blogposts on frontpage".format(len(frontpage_toc),
                                                                                 len(blogposts_toc)))

        last_stories_filename = os.path.join(self.prefix,
                                             self.provider_name,
                                             LAST_STORIES_FILENAME)
        last_blogposts_filename = os.path.join(self.prefix,
                                               self.provider_name,
                                               LAST_BLOGPOSTS_FILENAME)

        self.new_stories = utils.filter_only_new_stories(frontpage_toc, last_stories_filename)
        self.new_blogposts = utils.filter_only_new_stories(blogposts_toc, last_blogposts_filename)

        self.log.info("Found {0} new stories and {1} new blogposts since last time".format(len(self.new_stories),
                                                                                           len(self.new_blogposts)))



    def update_global_queue(self):
        today = datetime.today()

        day_str = today.strftime("%Y-%m-%d")
        day_directory = os.path.join(self.root, "queue", day_str)
        
        if not os.path.exists(day_directory):
            os.makedirs(day_directory)

        batch_hour_str = today.strftime("%H.%M.%S")
        batch_filename = "{0}.json".format(os.path.join(day_directory, batch_hour_str))

        self.log.info("Saving toc to {0}".format(batch_filename))
        with open(batch_filename, "w") as f:
            self.log.info("Enqueuing {0} new stories and {1} blogposts".format(len(self.new_stories), len(self.new_blogposts)))
            json.dump({"articles":self.new_stories, "blogposts":self.new_blogposts}, f)

            


class ArticleQueueDownloader(object):
    def __init__(self, db_root, provider_name, provider_title):
        self.db_root = db_root
        self.provider_name = provider_name
        self.provider_title = provider_title



    def download_all_articles_in_queue(self):
        provider_db = Provider(self.db_root, self.provider_name)



    def download_all_articles_for_day(self, day_string):
        pass



def test_filler():
    from datasources import lesoir
    queue_filler = ArticleQueueFiller(lesoir, "lesoir", "out")
    queue_filler.fetch_newest_article_links()
    queue_filler.update_global_queue()
    


def test_downloader():
    pass


if __name__ == "__main__":
    test_filler()