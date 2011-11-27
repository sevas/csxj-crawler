#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os, os.path
from datetime import datetime

from datasources import lesoir, dhnet, lalibre, sudpresse, rtlinfo
from datasources.common.utils import fetch_html_content
from providerstats import ProviderStats
from articlequeue import ArticleQueueFiller, ArticleQueueDownloader

DEBUG_MODE = True


def update_provider_stats(outdir, articles, errors):
    stats_filename = os.path.join(outdir, 'stats.json')
    if not os.path.exists(stats_filename):
        print 'creating stats file:', stats_filename
        init_stats = ProviderStats.make_init_instance()
        init_stats.save_to_file(stats_filename)

    current_stats = ProviderStats.load_from_file(stats_filename)
    current_stats.n_articles += len(articles)
    current_stats.n_errors += len(errors)
    current_stats.n_dumps += 1
    current_stats.end_date = datetime.today()
    current_stats.n_links += sum([(len(art.external_links) + len(art.internal_links)) for art in articles])

    current_stats.save_to_file(stats_filename)





def put_articles_in_queue(provider, db_root):
    name = provider.SOURCE_NAME
    print("Enqueuing stories for {0}".format(name))
    queue_filler = ArticleQueueFiller(provider, name, db_root)
    queue_filler.fetch_newest_article_links()
    queue_filler.update_global_queue()




def download_queued_articles(source, db_root):
    name = source.SOURCE_NAME
    print("Downloading enqueued stories for {0}".format(name))
    queue_downloader = ArticleQueueDownloader(source, name, db_root)
    queue_downloader.download_all_articles_in_queue()




def main(outdir):
    d = datetime.today()
    print d.strftime('New articles saved on %d/%m/%Y at %H:%M')
    update_all_queues(outdir)


if __name__=="__main__":
    main("testing")
