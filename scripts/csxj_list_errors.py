from csxj.db import Provider, get_all_provider_names


def list_errors(db_root):
    res = dict()
    source_names = get_all_provider_names(db_root)
    for source_name in source_names:
        provider_db = Provider(db_root, source_name)
        error_count = 0

        for date_string in provider_db.get_all_days():
            errors_by_batch = provider_db.get_errors2_per_batch(date_string)

            for (time, errors) in errors_by_batch:
                if errors:
                    error_count += len(errors)
                    print source_name, date_string, time
                    for err in errors:
                        print "\t", err.url
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