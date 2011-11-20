import os, os.path
from datetime import datetime
import json
import utils


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


    def fetch_newest_article_links(self):
        outdir = os.path.join(self.prefix, self.provider_name)
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        queue_root_directory = os.path.join(self.prefix, self.provider_name, 'queue')

        news_toc, blogposts_toc = self.provider.get_frontpage_toc()

        last_stories_filename = os.path.join(self.prefix, self.provider_name, LAST_STORIES_FILENAME)
        last_blogposts_filename = os.path.join(self.prefix, self.provider_name, LAST_BLOGPOSTS_FILENAME)

        self.new_stories = utils.filter_only_new_stories(news_toc, last_stories_filename)
        self.new_blogposts = utils.filter_only_new_stories(blogposts_toc, last_blogposts_filename)


    def update_global_queue(self):
        today = datetime.today()
        day_str = today.strftime("%Y-%m-%d")

        day_directory = os.path.join(self.root, day_str)
        if not os.path.exists(day_directory):
            os.mkdir(day_directory)

        batch_hour_str = today.strftime("%H.%M.%S")
        batch_filename = "{0}.json".format(os.path.join(day_directory, batch_hour_str))

        with open(batch_filename, "w") as f:
            json.dump({"articles":self.new_stories, "blogposts":self.new_blogposts}, f)

            


class ArticleQueueDownloader(object):
    def __init__(self, provider, provider_name, provider_title):
        pass

    def download_all_articles_in_queue(self):
        pass



if __name__ == "__main__":
    from datasources import lesoir
    queue_filler = ArticleQueueFiller(lesoir, "lesoir", "out")
    queue_filler.fetch_newest_article_links()
    queue_filler.update_global_queue()