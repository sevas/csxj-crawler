import itertools as it
import json
from pprint import pprint

from csxj.db import Provider, get_all_provider_names
from csxj.db import ErrorLogEntry, ErrorLogEntry2
from csxj.datasources import lesoir, lalibre, dhnet, sudinfo, rtlinfo, lavenir, rtbfinfo, levif, septsursept, sudpresse


def filter_identical_ErrorLogEntries(entries):
    if entries:
        def keyfunc(a):
            return a.__class__

        splitted = dict()
        for k, g in it.groupby(entries, key=keyfunc):
            splitted[k] = list(g)

        out = list()

        if ErrorLogEntry2 in splitted:
            out = splitted[ErrorLogEntry2]
        out_urls = [e.url for e in out]
        if ErrorLogEntry in splitted:
            non_duplicates = [ErrorLogEntry2(url=e.url, title=e.filename, stacktrace=e.stacktrace) for e in splitted[ErrorLogEntry] if e.url not in out_urls]
            out.extend(non_duplicates)
        return out
    else:
        return list()


def flatten_list(entries):
    return [e[0] for e in entries if e]


def list_errors(db_root, outfile):
    res = dict()
    all_errors = dict()
    source_names = get_all_provider_names(db_root)
    for source_name in source_names:
        provider_db = Provider(db_root, source_name)
#        datasource = NAME_TO_SOURCE_MODULE_MAPPING[source_name]
        error_count = 0
        all_errors[source_name] = dict()

        for date_string in provider_db.get_all_days():
            errors_by_batch = provider_db.get_errors2_per_batch(date_string)
            all_errors[source_name] = list()
            for (batch_time, errors) in errors_by_batch:
                errors = flatten_list(errors)
                errors = filter_identical_ErrorLogEntries(errors)
                error_count += len(errors)

                if errors:
                    print source_name, date_string, batch_time

                    for e in errors:
                        print e.url
                        new_item = (("{0}/{1}".format(date_string, batch_time)), (e.url, e.title, e.stacktrace))
                        print "ADDING: {0}".format(new_item)
                        all_errors[source_name].append(new_item)

#                       print "*** Reprocessing: {0})".format(e.url)
#                       article_data, html = datasource.extract_article_data(e.url)
#                       article_data.print_summary()

        res[source_name] = error_count

    print "\n" * 4
    for name, error_count in res.items():
        print "{0}: Had {1} errors".format(name, error_count)

    pprint(all_errors)
    with open(outfile, 'w') as f:
            json.dump(all_errors, f, indent=4)



def main(db_root, outfile):
    list_errors(db_root, outfile)

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Utility prgram to list errors')
    parser.add_argument('--jsondb', type=str, dest='jsondb', required=True, help='json db root directory')
    parser.add_argument('--outfile', type=str, dest='outfile', required=True, help='file to output json file')
    args = parser.parse_args()

    main(args.jsondb, args.outfile)