import os, os.path
import utils
import json


class ArticleQueueFiller(object):
    def __init__(self, provider, provider_name, prefix):
        self.provider = provider
        self.provider_name = provider_name
        self.prefix = prefix


    def fetch_newest_article_links(self):
        outdir = os.path.join(self.prefix, self.provider_name)
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        queue_root_directory = os.path.join(self.prefix, self.provider_name, 'queue')

        news_toc, blogposts_toc = self.provider.get_frontpage_toc()

        
        if os.path.exists(last_stories_filename):
            with open(last_stories_filename, 'r') as f:
                last_stories_fetched = [tuple(i) for i in  json.load(f)]

        frontpage_toc = utils.filter_only_new_stories(news_toc, last_stories_filename)


    def update_global_queue(self):
        pass



class ArticleQueueDownloader(object):
    def __init__(self, provider, provider_name, provider_title):
        pass

    def download_all_articles_in_queue(self):
        pass

