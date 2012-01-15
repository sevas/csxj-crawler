
from csxj.db import Provider
from csxj.datasources import rtlinfo, sudpresse, lesoir, lalibre, dhnet


def show_queue_info(json_db):
    sources = [rtlinfo, sudpresse, lesoir, lalibre, dhnet]
    res = dict()
    for source in sources:
        p = Provider(json_db, source.SOURCE_NAME)
        print source.SOURCE_NAME
        batches_by_day = p.get_queued_batches_by_day()
        total_item_count = 0

        for day, batches in batches_by_day:
            print "\tDay:", day
            queued_item_count = 0
            for batch, items in batches:
                queued_item_count += len(items['articles'])

            print day, queued_item_count
            total_item_count += queued_item_count
        res[source.SOURCE_NAME] = (total_item_count, len(batches_by_day))


    for name, (item_count, day_count) in res.items():
        print "{0}: {1} items for {2} days".format(name, item_count, day_count)

def try_download_queue(json_db):
    sources = [rtlinfo, sudpresse, lesoir, lalibre, dhnet]
    for source in sources:
        p = Provider(json_db, source.SOURCE_NAME)
        batches_by_day = p.get_queued_batches_by_day()
        print source.SOURCE_NAME
        for day, batches in batches_by_day:
            print "\tDay:", day
            for batch, items in batches:
                print "\t\tBatch:", batch
                articles = items['articles']
                for title, url in articles:
                    print "\t\t\tDownloading {0}".format(url)
                    art, html = source.extract_article_data(url)
                    print "\t\t\t\t got {0} links".format(len(art.links))



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Utility functions to troubleshoot queue management')
    parser.add_argument('--jsondb', type=str, dest='jsondb', required=True, help='json db root directory')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--download-queue',  action='store_true')
    group.add_argument('--show-queue', action='store_true')

    args = parser.parse_args()

    if args.download_queue:
        try_download_queue(args.jsondb)
    elif args.show_queue:
        show_queue_info(args.jsondb)