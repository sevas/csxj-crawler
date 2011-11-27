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
