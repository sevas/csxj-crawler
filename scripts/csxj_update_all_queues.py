"""

"""
import os
import argparse
import csxj.crawler
from csxj.datasources import lesoir, lalibre, dhnet, sudpresse, rtlinfo
from csxj.articlequeue import ArticleQueueFiller



def update_all_queues(db_root):
    if not os.path.exists(db_root):
        print 'creating output directory:', db_root
        os.mkdir(db_root)

    ArticleQueueFiller.setup_logging()
    all_providers = lesoir, dhnet, lalibre, sudpresse, rtlinfo
    for provider in all_providers:
        csxj.crawler.put_articles_in_queue(provider, db_root)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch pages from news sources, dumps interesting data')
    parser.add_argument('--debug', dest='debug', action='store_true', help="run crawler in debug mode")
    parser.add_argument('--jsondb', type=str, dest='jsondb', required=True, help='directory to dump the json db in')
    args = parser.parse_args()
    
    update_all_queues(args.jsondb)
