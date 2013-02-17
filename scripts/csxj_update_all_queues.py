"""

"""
import os
import argparse
import csxj.crawler
from csxj.datasources import lalibre, dhnet, sudinfo, rtlinfo, lavenir, rtbfinfo, levif, septsursept, lesoir_new
from csxj.articlequeue import ArticleQueueFiller

ALL_PARSERS = dhnet, lalibre, sudinfo, rtlinfo, lavenir, rtbfinfo, levif, septsursept, lesoir_new


def make_parser_list():
    return ','.join([p.SOURCE_NAME for p in ALL_PARSERS])


def update_all_queues(db_root, sources):
    if not os.path.exists(db_root):
        print 'creating output directory:', db_root
        os.mkdir(db_root)

    ArticleQueueFiller.setup_logging()
    for parser in ALL_PARSERS:
        if parser.SOURCE_NAME in sources:
            csxj.crawler.put_articles_in_queue(parser, db_root)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Fetch frontpages from news sources, extract and stores headlines urls for future processing')
    arg_parser.add_argument('--debug', dest='debug', action='store_true', help="run crawler in debug mode")
    arg_parser.add_argument('--jsondb', type=str, dest='jsondb', required=True, help='directory to dump the json db in')
    arg_parser.add_argument('--sources', type=str, dest='sources', default=make_parser_list(), help='sources to consider (one of %s' % make_parser_list())
    args = arg_parser.parse_args()

    sources = [s for s in args.sources.split(',') if s]
    update_all_queues(args.jsondb, sources)
