from csxj.db import Provider, get_all_provider_names
from csxj.db import ErrorLogEntry, ErrorLogEntry2
import itertools as it

def filter_identical_ErrorLogEntries(entries):
    if entries:
        def keyfunc(a):
            return a.__class__

        splitted = dict()
        for k, g in it.groupby(entries, key=keyfunc):
            splitted[k] = list(g)

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


def list_errors(db_root):
    res = dict()
    source_names = get_all_provider_names(db_root)
    for source_name in source_names:
        provider_db = Provider(db_root, source_name)
        error_count = 0

        for date_string in provider_db.get_all_days():
            errors_by_batch = provider_db.get_errors2_per_batch(date_string)

            for (batch_time, errors) in errors_by_batch:
                print source_name, date_string, batch_time

                errors = flatten_list(errors)
                errors = filter_identical_ErrorLogEntries(errors)
                error_count += len(errors)

                for e in errors:
                    print e.url

        res[source_name] = error_count

    print "\n" * 4
    for name, error_count in res.items():
        print "{0}: Had {1} errors".format(name, error_count)



def main(db_root):
    list_errors(db_root)

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Utility prgram to list errors')
    parser.add_argument('--jsondb', type=str, dest='jsondb', required=True, help='json db root directory')
    args = parser.parse_args()

    main(args.jsondb)