
from csxj.db import Provider
from csxj.datasources import rtlinfo, sudpresse, lesoir, lalibre, dhnet


def show_queue_info(json_db):
    for source in [sudpresse]:
        p = Provider(json_db, source.SOURCE_NAME)

        batches_by_day = p.get_queued_batches_by_day()

        for day, batches in batches_by_day:
            queued_item_count = 0
            for batch, items in batches:

                queued_item_count += len(items['articles'])
            print day, queued_item_count


def try_download_queue(json_db):

    for source in [lalibre]:
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


def main(json_db):
    #show_queue_info(json_db)
    try_download_queue(json_db)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Utility functions to troubleshoot queue management')
    parser.add_argument('--jsondb', type=str, dest='jsondb', required=True, help='json db root directory')
    args = parser.parse_args()

    main(args.jsondb)