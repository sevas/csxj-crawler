import os
import sys
import traceback
from jinja2 import Template, Environment, FileSystemLoader
from csxj.db import Provider, get_all_provider_names
from csxj.datasources import lesoir, rtlinfo, sudpresse, lalibre, dhnet




class HTMLReport(object):
    def __init__(self):
        self.results = []


    def process_error(self, date, hour, source, url):
        try:
            article, html = source.extract_article_data(url)
            self.add_success(url, article)
        except Exception as e:
            self.add_failure(url, e)


    def add_success(self, url, article):
        new_result = {
            'success': True,
            'url': url,
            'date':  article.pub_date,
            'internal_link_count': len(article.internal_links),
            'external_link_count': len(article.external_links)
        }
        self.results.append(new_result)

        

    def add_failure(self, url, e):
        trace = traceback.format_exc()
        new_result = {
            'success': False,
            'url': url,
            'trace': trace,
            'message': e.message
        }
        self.results.append(new_result)



    def write_html_to_file(self, filename):
        ENV = Environment( loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')))

        with open(os.path.join(page_directory_out, filename), 'w') as f:
            template = ENV.get_template(os.path.join('error_report.html'))
            html_content = template.render(results=self.results)
            f.write(html_content)


def reprocess_errors(db_root, sources):
    report = HTMLReport()

    for source in sources:
        provider_db = Provider(db_root, source.SOURCE_NAME)
        for date_string in provider_db.get_all_days():
            errors = provider_db.get_errors_per_batch(date_string)
            for (time, errors) in errors:
                if errors:
                    for err in errors[:1]:
                        report.process_error(date_string, time, source, err.url)

    report.write_html_to_file("reprocessed_errors_report.html")


def try_reprocessing(source, url):
    try:
        article_data, html_content = source.extract_article_data(url)
        if article_data:
            print article_data.title, article_data.links
        else:
            print 'no article found for that url'
    except Exception as e:
        trace = traceback.format_exc()
        print trace



def list_errors(db_root, sources):
    res = dict()

    for source in sources:
        provider_db = Provider(db_root, source.SOURCE_NAME)
        count = 0
        for date_string in provider_db.get_all_days():
            errors_by_batch = provider_db.get_errors_per_batch(date_string)
            for (time, errors) in errors_by_batch:
                if errors:
                    count += len(errors)
                    print source.SOURCE_NAME, date_string, time
                    for err in errors:
                        print "\t", err.url
                        #for line in err.stacktrace:
                        #    print "\t", line
                        try_reprocessing(source, err.url)
                    print
        res[source.SOURCE_NAME] = count

    print "\n" * 4
    for (name, error_count) in res.items():
        print "{0}: {1} errors".format(name, error_count)

def main(db_root):
    #list_errors(db_root, [lesoir, rtlinfo, sudpresse, lalibre, dhnet])
    list_errors(db_root, [dhnet])

if __name__=="__main__":
    main("/Users/sevas/Documents/juliette/json_db_0_5")