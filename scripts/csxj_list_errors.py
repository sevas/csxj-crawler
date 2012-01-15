import os
import sys
import traceback
import shutil
from jinja2 import Template, Environment, FileSystemLoader
from csxj.db import Provider, get_all_provider_names
from csxj.datasources import lesoir, rtlinfo, sudpresse, lalibre, dhnet


class HTMLReport(object):
    def __init__(self):
        self.results = list()


    def process_error(self, date, hour, source, url):
        try:
            article, html = source.extract_article_data(url)
            self.add_success(url, article, source)
        except Exception as e:
            self.add_failure(url, e, source)


    def add_success(self, url, article, source):
        new_result = {
            'success': True,
            'url': url,
            'title': article.title,
            'date':  article.pub_date,
            'internal_link_count': len(article.internal_links),
            'external_link_count': len(article.external_links)
        }
        #self.results[source.SOURCE_NAME].append(new_result)
        self.results.append(new_result)

        

    def add_failure(self, url, e, source):
        trace = traceback.format_exc()
        new_result = {
            'success': False,
            'url': url,
            'trace': trace.split('\n'),
            'message': e.message
        }
        #self.results[source.SOURCE_NAME].append(new_result)
        self.results.append(new_result)


    def write_html_to_file(self, outdir):
        ENV = Environment( loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),'../templates')))

        if not os.path.exists(outdir):
            os.makedirs(outdir)
            shutil.copytree(os.path.join(os.path.dirname(__file__),"../templates/blueprint"), outdir)

        filename = "reprocessed_errors_report.html"
        with open(os.path.join(outdir, filename), 'w') as f:
            template = ENV.get_template('error_report.html')
            html_content = template.render(results=self.results)
            pos = 3625
            print html_content[pos-10:pos+10]
            f.write(html_content)


def reprocess_errors(db_root, sources):
    report = HTMLReport()

    for source in sources:
        provider_db = Provider(db_root, source.SOURCE_NAME)
        for date_string in provider_db.get_all_days():
            errors = provider_db.get_errors_per_batch(date_string)
            for (time, errors) in errors:
                if errors:
                    for err in errors:
                        report.process_error(date_string, time, source, err.url)

    report.write_html_to_file("../error_report")


def try_reprocessing(source, url):
    try:
        article_data, html_content = source.extract_article_data(url)
        if article_data:
            print article_data.title, article_data.links
        else:
            print 'no article found for that url'
        return True
    except Exception as e:
        trace = traceback.format_exc()
        print trace
        return False



def list_and_reprocess_errors(db_root, sources):
    res = dict()

    for source in sources:
        provider_db = Provider(db_root, source.SOURCE_NAME)
        error_count_before = 0
        error_count_after = 0
        succesfully_reprocessd_articles = 0

        for date_string in provider_db.get_all_days():
            errors_by_batch = provider_db.get_errors_per_batch(date_string)
            for (time, errors) in errors_by_batch:
                if errors:
                    error_count_before += len(errors)
                    print source.SOURCE_NAME, date_string, time
                    for err in errors:
                        print "\t", err.url

                        success = try_reprocessing(source, err.url)
                        if success:
                            succesfully_reprocessd_articles += 1
                        else:
                            error_count_after += 1

        res[source.SOURCE_NAME] = (error_count_before, error_count_after, succesfully_reprocessd_articles)

    print "\n" * 4
    for (name, (error_count_before, error_count_after, succesfully_reprocessd_articles)) in res.items():
        print "{0}: Had {1} errors, Reprocessed {2}, still {3}".format(name,
            error_count_before,
            succesfully_reprocessd_articles,
            error_count_after)


def list_errors(db_root, sources):
    res = dict()

    for source in sources:
        provider_db = Provider(db_root, source.SOURCE_NAME)
        error_count = 0

        for date_string in provider_db.get_all_days():
            errors_by_batch = provider_db.get_errors_per_batch(date_string)
            for (time, errors) in errors_by_batch:
                if errors:
                    error_count += len(errors)
                    print source.SOURCE_NAME, date_string, time
                    for err in errors:
                        print "\t", err.url
        res[source.SOURCE_NAME] = error_count

    print "\n" * 4
    for name, error_count in res.items():
        print "{0}: Had {1} errors".format(name, error_count)



def main(db_root):
    list_errors(db_root, [lesoir, rtlinfo, sudpresse, lalibre, dhnet])
    #list_errors(db_root, [lalibre])
    #reprocess_errors(db_root, [lalibre])

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Utility functions to list and reprocess errors')
    parser.add_argument('--jsondb', type=str, dest='jsondb', required=True, help='json db root directory')
    args = parser.parse_args()
    
    main(args.jsondb)