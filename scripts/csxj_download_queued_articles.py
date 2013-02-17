"""

"""
import os
import argparse
import csxj.crawler
from csxj.datasources import lalibre, dhnet, sudinfo, rtlinfo, lavenir
from csxj.articlequeue import ArticleQueueDownloader
import traceback


ALL_PARSERS = dhnet, lalibre, rtlinfo, sudinfo


def make_parser_list():
    return ','.join([p.SOURCE_NAME for p in ALL_PARSERS])


def download_all_queued_articles(db_root, sources):
    if not os.path.exists(db_root):
        print("no such database directory: {0}".format(db_root))
    else:
        ArticleQueueDownloader.setup_logging()
        for parser in ALL_PARSERS:
            if parser.SOURCE_NAME in sources:
                try:
                    csxj.crawler.download_queued_articles(parser, db_root)
                except Exception:
                    stacktrace = traceback.format_exc()
                    print stacktrace


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Download, analyze and store all the queued articles in the csxj json database')
    arg_parser.add_argument('--jsondb', type=str, dest='jsondb', required=True, help='directory to dump the json db in')
    arg_parser.add_argument('--sources', type=str, dest='sources', default=make_parser_list(), help='sources to consider (one of %s)' % make_parser_list())
    args = arg_parser.parse_args()

    sources = [s for s in args.sources.split(',') if s]

    download_all_queued_articles(args.jsondb, sources)
