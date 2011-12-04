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
        trace = traceback.format_stack()
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


def list_errors(db_root, sources):
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


def main(db_root):
    list_errors(db_root, [lesoir])
                    

if __name__=="__main__":
    main("./out")