import itertools as it
import json
from pprint import pprint

from csxj.db import Provider, get_all_provider_names
from csxj.db import ErrorLogEntry, ErrorLogEntry2
from csxj.datasources import lesoir, lalibre, dhnet, sudinfo, rtlinfo, lavenir, rtbfinfo, levif, septsursept, sudpresse



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
    'sudpresse': sudpresse
}


def main(infile):
    with open(infile, 'r') as f:
        errors_by_source = json.load(f)
        for source_name, errors in errors_by_source.iteritems():
            print "--- {0}: {1} errors".format(source_name, len(errors))
            datasource = NAME_TO_SOURCE_MODULE_MAPPING[source_name]
            if source_name == "sudinfo":
                print "PASS"
                continue
            for timestamp, error in errors:
                if error[0].startswith('http://'):
                    url, title, stacktrace = error
                else:
                    title, url, stacktrace = error

                title=title.strip()

                print u"*** Reprocessing: {0} {1})".format(url, title)
                try:
                    article_data, html = datasource.extract_article_data(url)
                    article_data.print_summary()
                except:
                    print "fail"




if __name__=="__main__":
    main("json_db_0_5_errors.json")