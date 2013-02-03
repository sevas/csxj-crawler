# Coding: utf-8

import os
import json

from web import template


def generate_test_func(fname, parser_name, urls_by_group):
    render = template.render(os.path.join(os.path.dirname(__file__), 'templates/'))

    return render.test_func(fname, parser_name, urls_by_group)


def save_sample_data_file(html_data, source_url, test_name, root_path):
    if os.path.exists(root_path):

        full_path_name = os.path.join(root_path, test_name+".html")
        if os.path.exists(full_path_name):
            print "{0} already exists. Delete it if you want to overwrite it. Aborting.".format(full_path_name)
            return

        with open(full_path_name, 'w') as f:
            f.write(html_data)

        full_index_name =os.path.join(root_path, "index.json")
        index = dict(test_data=[])
        if os.path.exists(full_index_name):
            with open(full_index_name, 'r') as f:
                old_index = json.load(f)
                index.update(old_index)
            index['test_data'].append((source_url, test_name+".html"))
            with open(full_index_name, 'w') as f:
                json.dump(index, f, indent=2)


def generate_unittest(test_name, parser_name, urls_by_group, html_data, source_url, test_data_root_path):
    """
    example usage, from within an extract_article_data() function:
        import os
        generate_unittest('extract_embedded_tweets', SOURCE_NAME, dict(audio_content_links=audio_content_links,
                                                                    sidebox_links=sidebox_links,
                                                                    bottom_links=bottom_links,
                                                                    embedded_content_links=embedded_content_links,
                                                                    in_text_links=in_text_links),
                            html_content, source, os.path.join(os.path.dirname(__file__), "../../tests/datasources/test_data/", SOURCE_NAME))

    """
    print ("-"*80)
    print (generate_test_func(test_name, parser_name, urls_by_group))
    print ("-"*80)

    save_sample_data_file(html_data, source_url, test_name, test_data_root_path)