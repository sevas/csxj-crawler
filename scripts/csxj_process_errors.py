import os
import traceback
import shutil
from datetime import datetime
import json
from jinja2 import Template, Environment, FileSystemLoader
from csxj.db import Provider, get_all_provider_names, make_error_log_entry2
from csxj.db.utils import convert_date_to_string, convert_hour_to_string
from csxj.db.constants import *
from csxj.datasources import lesoir, lalibre, dhnet, sudpresse, rtlinfo, lavenir

DEBUG_MODE = False

#class HTMLReport(object):
#    def __init__(self):
#        self.results = list()
#
#
#    def process_error(self, date, hour, source, url):
#        try:
#            article, html = source.extract_article_data(url)
#            self.add_success(url, article, source)
#        except Exception as e:
#            self.add_failure(url, e, source)
#
#
#    def add_success(self, url, article, source):
#        new_result = {
#            'success': True,
#            'url': url,
#            'title': article.title,
#            'date':  article.pub_date,
#            'internal_link_count': len(article.internal_links),
#            'external_link_count': len(article.external_links)
#        }
#        self.results.append(new_result)
#
#
#
#    def add_failure(self, url, e, source):
#        trace = traceback.format_exc()
#        new_result = {
#            'success': False,
#            'url': url,
#            'trace': trace.split('\n'),
#            'message': str(e)
#        }
#        self.results.append(new_result)
#
#
#
#    def write_html_to_file(self, outdir):
#        ENV = Environment( loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),'../templates')))
#
#        if not os.path.exists(outdir):
#            os.makedirs(outdir)
#            shutil.copytree(os.path.join(os.path.dirname(__file__),"../templates/blueprint"), outdir)
#
#        filename = "reprocessed_errors_report.html"
#        with open(os.path.join(outdir, filename), 'w') as f:
#            template = ENV.get_template('error_report.html')
#            html_content = template.render(results=self.results)
#            pos = 3625
#            print html_content[pos-10:pos+10]
#            f.write(html_content)
#
#
#
#def reprocess_errors(db_root, sources):
#    report = HTMLReport()
#
#    for source in sources:
#        provider_db = Provider(db_root, source.SOURCE_NAME)
#        for date_string in provider_db.get_all_days():
#            errors = provider_db.get_errors_per_batch(date_string)
#            for (time, errors) in errors:
#                if errors:
#                    for err in errors:
#                        report.process_error(date_string, time, source, err.url)
#
#    report.write_html_to_file("../error_report")





def reprocess_batch_errors(datasource, day_string, hour_string, errors):
    new_errors = list()
    new_articles = list()
    new_deleted_articles = list()
    new_raw_data = list()

    for err in errors:
        try:
            article_data, raw_html = datasource.extract_article_data(err.url)
            if article_data:
                new_articles.append(article_data)
                new_raw_data.append((err.url, raw_html))
            else:
                #todo: fix this after first fix iteration
                new_deleted_articles.append((err.url, err.url))
        except Exception as e:
            if e.__class__ in [AttributeError]:
                # this is for logging errors while parsing the dom. If it fails,
                # we should get an AttributeError at some point. We'll keep
                # that in a log, and save the html for future processing.
                stacktrace = traceback.format_exc()
                #todo: fix this after first fix iteration
                new_error = make_error_log_entry2(err.url, err.url, stacktrace)
                new_errors.append(new_error)
            else:
                if DEBUG_MODE:
                    # when developing, it's useful to not hide the exception
                    raise e
                else:
                    # but in production, log everything
                    stacktrace = traceback.format_exc()
                    new_error = make_error_log_entry2(err.url, err.url, stacktrace)
                    new_errors.append(new_error)

    return new_articles, new_deleted_articles, new_errors, new_raw_data



def reprocess_errors(db_root, sources):
    res = dict()

    for source in sources:
        provider_db = Provider(db_root, source.SOURCE_NAME)

        for date_string in provider_db.get_all_days():
            errors_by_batch = provider_db.get_errors2_per_batch(date_string)
            for (time, errors) in errors_by_batch:
                if errors:
                    print source.SOURCE_NAME, date_string, time, "found {0} errors".format(len(errors))
                    batch_directory = os.path.join(db_root, source.SOURCE_NAME, date_string, time)
                    articles, deleted_articles, errors, raw_data = reprocess_batch_errors(source, date_string, time, errors)
                    save_reprocessed_data(batch_directory, articles, deleted_articles, raw_data)
                    update_errors_file(batch_directory, errors)


def write_dict_to_file(d, outdir, outfile):
    """
    """
    publication_outdir = outdir
    if not os.path.exists(publication_outdir):
        os.makedirs(publication_outdir)

    filename = os.path.join(publication_outdir, outfile)
    with open(filename, 'w') as outfile:
        json.dump(d, outfile)



def save_reprocessed_data(batch_directory, articles, deleted_articles, raw_data):
    today = datetime.now()
    reprocessed_content_directory = "{0}_{1}_{2}".format(REPROCESSED_DIR_PREFIX,
                                                                convert_date_to_string(today),
                                                                today.strftime("%H.%M.%S"))
    outdir = os.path.join(batch_directory, reprocessed_content_directory)

    print "Writing {0} articles to {1}".format(len(articles), os.path.join(outdir, ARTICLES_FILENAME))
    write_dict_to_file({'articles':[art.to_json() for art in  articles]}, outdir, ARTICLES_FILENAME)


    print "Writing {0} links to deleted articles to {1}".format(len(deleted_articles), os.path.join(outdir, DELETED_ARTICLES_FILENAME))
    write_dict_to_file({'deleted_articles':deleted_articles}, outdir, DELETED_ARTICLES_FILENAME)

    print "Writing {0} raw html files to {1}".format(len(raw_data), os.path.join(outdir, RAW_DATA_DIR))
    save_raw_data(raw_data, outdir)


def update_errors_file(batch_directory, errors):
    #todo: change this after first reproces
    if errors:
        print "Writing {0} errors to {1}".format(len(errors), os.path.join(batch_directory, ERRORS2_FILENAME))
    else:
        print "Emptying all errors in {0}".format(os.path.join(batch_directory, ERRORS2_FILENAME))

    write_dict_to_file(dict(errors=errors), batch_directory, ERRORS2_FILENAME)



def save_raw_data(raw_data, batch_outdir):
     """
     """
     raw_data_dir = os.path.join(batch_outdir, RAW_DATA_DIR)

     if not os.path.exists(raw_data_dir):
         os.mkdir(raw_data_dir)
     references = []
     for (i, (url, html_content)) in enumerate(raw_data):
         outfilename = "{0}.html".format(i)
         with open(os.path.join(raw_data_dir, outfilename), 'w') as f:
             f.write(html_content)
         references.append((url, outfilename))

     with open(os.path.join(raw_data_dir, RAW_DATA_INDEX_FILENAME), 'w') as f:
         json.dump(references, f)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Try reprocessing previous errors')
    parser.add_argument('--jsondb', type=str, dest='jsondb', required=True, help='json db root directory')
    args = parser.parse_args()

    sources = [dhnet, lesoir, lalibre, sudpresse, rtlinfo, lavenir]
    reprocess_errors(args.jsondb, sources)