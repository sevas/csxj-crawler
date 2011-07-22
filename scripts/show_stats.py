__author__ = 'sevas'

import os, os.path
import argparse
from csxj.crawler.providerstats import ProviderStats


def print_report(stats):
    print 'Number of articles :', stats.n_articles
    print 'Number of links :   ', stats.n_links
    print 'Number of errors    ', stats.n_errors
    print 'Start date :        ', stats.start_date.strftime('%d/%m/%Y %H:%M')
    print 'End date :          ', stats.end_date.strftime('%d/%m/%Y %H:%M')



def main(json_db_dir):

    provider_dirs = [d for d in os.listdir(json_db_dir) if os.path.isdir(os.path.join(json_db_dir, d))]

    all_stats = ProviderStats.make_init_instance()
    for p in provider_dirs:
        stats_filename = os.path.join(json_db_dir, p, 'stats.json')
        stats = ProviderStats.load_from_file(stats_filename)
        all_stats.n_articles += stats.n_articles
        all_stats.n_errors += stats.n_errors
        all_stats.n_dumps += stats.n_dumps
        all_stats.n_links += stats.n_links

        all_stats.start_date = stats.start_date
        all_stats.end_date = stats.end_date

        print 'Summary for {0}'.format(p)
        print_report(stats)
        print

    print 'Overall stats'
    print_report(all_stats)



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Show a summary of the info from the stats.json files')
    parser.add_argument('--dir', type=str, dest='dir', required=True, help='directory of the json db')

    args = parser.parse_args()

    if os.path.exists(args.dir):
        main(args.dir)
    else:
        print 'directory {0} does not exist'
