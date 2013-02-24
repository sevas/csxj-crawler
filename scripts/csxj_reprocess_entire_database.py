"""

"""
import os
import os.path
import json
import traceback
import multiprocessing as mp
from datetime import datetime

import csxj.db as csxjdb
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


def write_dict_to_file(d, outdir, outfile):
    """
    """
    publication_outdir = outdir
    if not os.path.exists(publication_outdir):
        os.makedirs(publication_outdir)

    filename = os.path.join(publication_outdir, outfile)
    with open(filename, 'w') as outfile:
        json.dump(d, outfile)


def reprocess_single_batch(datasource_parser, raw_data_dir):
    raw_data_index_file = os.path.join(raw_data_dir, csxjdb.constants.RAW_DATA_INDEX_FILENAME)

    reprocessed_articles = list()
    errors_encountered = list()

    with open(raw_data_index_file, 'r') as f:
        index = json.load(f)
        for url, raw_file in index:
            raw_filepath = os.path.join(raw_data_dir, raw_file)
            try:
                print u"    Reprocessing: {1} ({0})".format(url, raw_filepath)
                #reprocessed_articles.append(raw_filepath)
                with open(raw_filepath, 'r') as raw_html:
                    article_data, html = datasource_parser.extract_article_data(raw_html)
                    article_data.url = url
                    reprocessed_articles.append((article_data, html))
            except Exception as e:
                stacktrace = traceback.format_exc()
                print u"!!! FAIL", e.message
                errors_encountered.append((url, raw_filepath, stacktrace))

    return reprocessed_articles, errors_encountered


def save_reprocessed_batch(dest_root_dir, source_name, day_string, batch_hour_string, articles):
    batch_root_dir = os.path.join(dest_root_dir, source_name, day_string, batch_hour_string)
    if not os.path.exists(batch_root_dir):
        os.makedirs(batch_root_dir)

    print u"+++ Saving {0} articles to {1}".format(len(articles), batch_root_dir)
    articles_json_data = {"articles": [article.to_json() for article, raw_html in articles],
                          "errors": []}
    articles_filepath = os.path.join(batch_root_dir, csxjdb.constants.ARTICLES_FILENAME)
    write_dict_to_file(articles_json_data, batch_root_dir, articles_filepath)

    raw_data_dir = os.path.join(batch_root_dir, csxjdb.constants.RAW_DATA_DIR)
    if not os.path.exists(raw_data_dir):
        os.makedirs(raw_data_dir)

    print u"^^^ Saving raw html to {0}".format(raw_data_dir)
    raw_data = [(a[0].url, a[1], "{0}.html".format(i)) for (i, a) in enumerate(articles)]
    for url, raw_html, raw_html_filename in raw_data:
        raw_filepath = os.path.join(raw_data_dir, raw_html_filename)
        with open(raw_filepath, 'w') as f:
            f.write(raw_html)

    index = [(url, raw_filepath) for (url, raw_html, raw_filepath) in raw_data]
    index_filepath = os.path.join(raw_data_dir, csxjdb.constants.RAW_DATA_INDEX_FILENAME)
    with open(index_filepath, 'w') as f:
        json.dump(index, f)


def reprocess_raw_html(args):
    provider_name, dest_root_dir = args
    p = csxjdb.Provider(source_root, provider_name)
    datasource = NAME_TO_SOURCE_MODULE_MAPPING[provider_name]
    article_count = 0

    errors_by_day = dict()
    all_days = p.get_all_days()
    for day in all_days[:]:
        errors_by_batch = dict()
        for batch_hour in p.get_all_batch_hours(day):
            batch_root_dir = os.path.join(p.directory, day, batch_hour)
            raw_data_dir = os.path.join(batch_root_dir, csxjdb.constants.RAW_DATA_DIR)
            batch_reprocessed_articles, batch_reprocessing_errors = reprocess_single_batch(datasource, raw_data_dir)

            if p.has_reprocessed_content(day, batch_hour):
                reprocessed_dates = p.get_reprocessed_dates(day, batch_hour)
                for day_string, batch_time_string in reprocessed_dates:
                    old_reprocessed_raw_data_dir = os.path.join(batch_root_dir, "{0}_{1}_{2}".format(csxjdb.constants.REPROCESSED_DIR_PREFIX, day_string, batch_time_string), csxjdb.constants.RAW_DATA_DIR)
                    reprocessed_articles, errors = reprocess_single_batch(datasource, old_reprocessed_raw_data_dir)
                    batch_reprocessed_articles.extend(reprocessed_articles)
                    batch_reprocessing_errors.extend(errors)

            if batch_reprocessing_errors:
                errors_by_batch[batch_hour] = batch_reprocessing_errors
            article_count += len(batch_reprocessed_articles)

            save_reprocessed_batch(dest_root_dir, p.name, day, batch_hour, batch_reprocessed_articles)

        if errors_by_batch:
            errors_by_day[day] = errors_by_batch


    err_dict = dict()
    err_dict[provider_name] = errors_by_day
    return article_count, err_dict


def main(source_path, dest_path, processes):
    provider_names = csxjdb.get_all_provider_names(source_root)
    provider_names = NAME_TO_SOURCE_MODULE_MAPPING.keys()

    before = datetime.now()
    n_samples = 0
    errors_by_source = dict()


    p = mp.Pool(processes)
    results = p.map(reprocess_raw_html, [(name, dest) for name in provider_names])

    n_samples = sum([x[0] for x in results])
    errors_by_source = [x[1] for x in results]

    after = datetime.now()
    dt = after - before

    print u"Total time for {0} articles: {1} seconds".format(n_samples, dt.seconds)
    avg_time = float(dt.seconds) / n_samples
    print u"Avg time per articles: {0} seconds".format(avg_time)

    write_dict_to_file(errors_by_source, os.path.join(dest, os.path.pardir), os.path.basename(dest) + "_errors.json")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Utility functions to troubleshoot queue management')
    parser.add_argument('--source_jsondb', type=str, dest='source_jsondb', required=True, help='source json db root directory')
    parser.add_argument('--dest_jsondb', type=str, dest='dest_jsondb', required=True, help='dest json db root directory')
    parser.add_argument('--processes', type=int, dest='processes', required=False, default=1, help='Number of parallel processes to use (default=1)')

    args = parser.parse_args()

    source_root = args.source_jsondb
    dest = args.dest_jsondb

    print "Using {0} processes".format(args.processes)
    main(source_root, dest, args.processes)

