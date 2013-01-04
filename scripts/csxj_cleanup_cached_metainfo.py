import argparse
import csxj.db as csxjdb

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deletes the cached metainfo (article and error counts)')
    parser.add_argument('--jsondb', type=str, dest='jsondb', required=True, help='json db root directory')
    args = parser.parse_args()

    for source_name in csxjdb.get_all_provider_names(args.jsondb):
        p = csxjdb.Provider(args.jsondb, source_name)
        p.remove_all_cached_metainfo()
