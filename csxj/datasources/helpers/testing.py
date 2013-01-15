# Coding: utf-8

import os
from web import template


def indent_block(text, indent=0):
    lines = text.split('\n')
    spaces = u" " * indent
    indented_lines = [spaces + l for l in lines]
    return u"\n".join(indented_lines)


def make_test(fname, parser_name, urls_by_group):

    def make_tagged_url_call(taggedURL):
        return u"""    make_tagged_url("{0}", u\"\"\"{1}\"\"\", {2}),""".format(taggedURL.URL, taggedURL.title, taggedURL.tags)

    group_template = u"""{0} = [\n{1}\n]"""

    expected_links_groups = ""
    for group, taggedURLs in urls_by_group.iteritems():
        expected_links_groups += group_template.format(group, "\n".join([make_tagged_url_call(t) for t in taggedURLs]))
        expected_links_groups += "\n"

    expected_links = u"{0}\n    expected_links = {1}".format(expected_links_groups, "+".join(urls_by_group.keys()))

    test_func_template = u"""
def test_simple_link_extraction(self):
    \"\"\" \"\"\"
    with open(os.path.join(DATA_ROOT, "{0}")) as f:
        article, raw_html = {1}.extract_article_data(f)

        extracted_links = article.links

    {2}

        assert_taggedURLs_equals(expected_links, extracted_links)
    """

    print test_func_template.format(fname, parser_name, indent_block(expected_links, 4))


def generate_test_func(fname, parser_name, urls_by_group):
    render = template.render(os.path.join(os.path.dirname(__file__), 'templates/'))

    print render.test_func(fname, parser_name, urls_by_group)



if __name__=="__main__":
    generate_test_func('bleh.html', 'sudinfo', dict(foo=['bar', 'baz']))