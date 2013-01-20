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

        with open(full_path_name) as f:
            f.write(html_data)

        full_index_name =os.path.join(root_path, "index.json")
        index = dict(test_data=[])
        if os.path.exists(full_index_name):
            with open(full_index_name) as f:
                old_index = json.load(f)
                index.update(old_index)
            index['test_data'].append(('url', test_name+".html"))
            with open(full_index_name, 'w') as f:
                json.dump(f, index, indent=2)


