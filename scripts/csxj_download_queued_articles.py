"""

"""
import os
import argparse
import csxj.crawler
from csxj.datasources import lesoir, lalibre, dhnet, sudpresse, rtlinfo
from csxj.articlequeue import ArticleQueueDownloader




def download_all_queued_articles(db_root):
    if not os.path.exists(db_root):
        print("no such database directory: {0}".format(db_root))
    else:
        ArticleQueueDownloader.setup_logging()
        all_sources = lesoir, dhnet, lalibre, sudpresse, rtlinfo
        for source in all_sources:
            csxj.crawler.download_queued_articles(source, db_root)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download, analyze and store all the queued articles in the csxj json database')
    parser.add_argument('--debug', dest='debug', action='store_true', help="run crawler in debug mode")
    parser.add_argument('--outdir', type=str, dest='outdir', required=True, help='directory to dump the json db in')
    args = parser.parse_args()

    download_all_queued_articles(args.outdir)
