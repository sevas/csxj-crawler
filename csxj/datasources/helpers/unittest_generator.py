# Coding: utf-8

import os
from web import template


def generate_test_func(fname, parser_name, urls_by_group):
    render = template.render(os.path.join(os.path.dirname(__file__), 'templates/'))

    print render.test_func(fname, parser_name, urls_by_group)


if __name__=="__main__":
    generate_test_func('bleh.html', 'sudinfo', dict(foo=['bar', 'baz']))