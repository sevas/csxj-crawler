
import os
import sys
from csxj.db import Provider, get_all_provider_names
from csxj.datasources import lesoir, rtlinfo, sudpresse, lalibre, dhnet


def main(db_root):
    for source in [lesoir, rtlinfo, sudpresse, lalibre, dhnet]:
        provider_db = Provider(db_root, source.SOURCE_NAME)
        for date_string in provider_db.get_all_days():
            errors = provider_db.get_errors_per_batch(date_string)
            for (time, errors) in errors:
                if errors:
                    print source.SOURCE_NAME, date_string, len(errors)
                    

if __name__=="__main__":
    main("./out")