import argparse
import csxj.db as csxjdb



if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Show the cached metainfo. Generates it if missing')
    parser.add_argument('--jsondb', type=str, dest='jsondb', required=True, help='json db root directory')
    args = parser.parse_args()

    for source_name in csxjdb.get_all_provider_names(args.jsondb):
        p = csxjdb.Provider(args.jsondb, source_name)
        print(source_name)
        for day_string in p.get_all_days():
            print('\t{0}'.format(day_string))
            metainfo = p.get_metainfo_for_day(day_string)
            for k,v in metainfo.items():
                print('\t\t{0}:\t{1}'.format(k, v))


