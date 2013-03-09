"""
nose tests for the test_link_extraction_test_generator() function.
This is so meta.
"""

from nose.tools import ok_

from csxj.datasources.helpers import unittest_generator
from csxj.common.tagging import make_tagged_url


def test_link_extraction_test_generator():
    """
        csxj.datasources.helpers.unittest_generator.generate_test_func() generates a unit test function from lists of tagged urls (and other parameters)
    """
    expected_generated_code = u"""\
    def test_link_extraction_test(self):
        with open(os.path.join(DATA_ROOT, "link_extraction_test.html")) as f:
            article, raw_html = some_parser.extract_article_data(f)
            extracted_links = article.links
            group1 = [
                make_tagged_url("http://nice.com", u\"\"\"very nice website\"\"\", set(['very nice'])),
            ]
            group2 = [
            ]
            expected_links = group1 + group2
            assert_taggedURLs_equals(expected_links, extracted_links)
"""

    group1 = [
        make_tagged_url("http://nice.com", u"very nice website", set(['very nice']))
    ]

    group2 = []

    generated_code = unittest_generator.generate_test_func("link_extraction_test",
                                                           "some_parser",
                                                           dict(group1=group1, group2=group2))
    generated_code = generated_code.__body__

    if expected_generated_code != generated_code:
        import difflib
        d = difflib.Differ()
        diff = d.compare(generated_code.split('\n'), expected_generated_code.split('\n'))
        ok_(False, msg="Generated file is not what was expected. See diff:\n\n"+"\n".join(diff))
    else:
        ok_(True)

