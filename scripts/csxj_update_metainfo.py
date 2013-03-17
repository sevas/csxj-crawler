# coding=utf-8
import argparse
import csxj.db as csxjdb
from csxj.datasources import lesoir, lalibre, dhnet, sudinfo, rtlinfo, lavenir, rtbfinfo, levif, septsursept, sudpresse, lesoir_new

NAME_TO_SOURCE_MODULE_MAPPING = {
    'lesoir': lesoir,
    'lalibre': lalibre,
    'dhnet': dhnet,
    'sudinfo': sudinfo,
    'rtlinfo': rtlinfo,
    'lavenir': lavenir,
    'rtbfinfo': rtbfinfo,
    'levif': levif,
    'septsursept': septsursept,
    'sudpresse': sudpresse,
    'lesoir_new': lesoir_new
}


def make_parser_list():
    return ','.join([p.SOURCE_NAME for p in NAME_TO_SOURCE_MODULE_MAPPING.values()])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show the cached metainfo. Generates it if missing')
    parser.add_argument('--jsondb', type=str, dest='jsondb', required=True, help='json db root directory')
    parser.add_argument('--sources', type=str, dest='source_names', default=make_parser_list(), help='comma-separated list of the sources to consider (default={0})'.format(make_parser_list()))
    args = parser.parse_args()

    for source_name in csxjdb.get_all_provider_names(args.jsondb):
        p = csxjdb.Provider(args.jsondb, source_name)
        if source_name in args.source_names:
            print(source_name)
            for day_string in p.get_all_days():
                print('\t{0}'.format(day_string))
                metainfo = p.get_cached_metainfos_for_day(day_string)
                for k, v in metainfo.items():
                    print('\t\t{0}:\t{1}'.format(k, v))

    print "\n\n\n"
    print "°"*80
    print "Summary:"
    for source_name in csxjdb.get_all_provider_names(args.jsondb):
        p = csxjdb.Provider(args.jsondb, source_name)
        if source_name in args.source_names:
            print(source_name)
            source_metainfo = p.get_cached_metainfos()

            for k, v in source_metainfo.items():
                print('\t\t{0}:\t{1}'.format(k, v))

    print "°"*80
    summed_stats = csxjdb.get_summed_statistics_for_all_sources(args.jsondb)
    for k, v in summed_stats.items():
        print('\t\t{0}:\t{1}'.format(k, v))
