#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from articlequeue import ArticleQueueFiller, ArticleQueueDownloader


def put_articles_in_queue(provider, db_root):
    name = provider.SOURCE_NAME
    print("Enqueuing stories for {0}".format(name))
    queue_filler = ArticleQueueFiller(provider, name, db_root)
    queue_filler.fetch_newest_article_links()




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
