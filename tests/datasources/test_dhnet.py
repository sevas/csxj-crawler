# -*- coding: utf-8 -*-
"""
High level test
"""

import os
from nose.tools import nottest, raises, eq_

from csxj.common.tagging import make_tagged_url
from csxj.datasources import dhnet

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', 'dhnet')


class TestDHNetLinkExtraction(object):
    @nottest
    def assert_taggedURLs_equals(self, expected_links, extracted_links):
        eq_(len(expected_links), len(extracted_links))
        eq_(sorted(extracted_links), sorted(expected_links))

    def test_simple_link_extraction(self):
        """
            DHNet parser can extract bottom links from an article.
        """
        with open(os.path.join(DATA_ROOT, "single_bottom_link.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)

            extracted_links = article.links
            expected_links = [make_tagged_url("/infos/faits-divers/article/381491/protheses-pip-plus-de-330-belges-concernees.html",
                                              u"Prothèses PIP:  plus de 330 belges concernées",
                                              set(["internal"]))]
            self.assert_taggedURLs_equals(expected_links, extracted_links)

    def test_removed_article(self):
        """
            DHNet parser should return a None value when processing
            a URL to a removed article
        """
        with open(os.path.join(DATA_ROOT, "removed_article.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)

            eq_(article, None)

    def test_same_sidebox_and_bottom_links(self):
        """
            DHNet parser should returns all the links in the sidebox and the bottom box, with adequate tags.
        """
        with open(os.path.join(DATA_ROOT, "same_sidebox_and_bottom_links.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links

            expected_sidebar_links = [
                make_tagged_url("/infos/belgique/article/378094/400000-belges-toucheront-700-en-plus-par-an.html",
                                u"400.000 Belges toucheront 700 € en plus par an",
                                set(["internal", "sidebar box"])),
                make_tagged_url("/infos/belgique/article/378135/chastel-il-faudra-trouver-quelques-centaines-de-millions-au-printemps.html",
                                u"Chastel : \"il faudra trouver quelques centaines de millions au printemps\"",
                                set(["internal", "sidebar box"]))
            ]
            expected_bottom_links = [
                make_tagged_url("/infos/belgique/article/378094/400000-belges-toucheront-700-en-plus-par-an.html",
                                u"400.000 Belges toucheront 700 € en plus par an",
                                set(["internal"])),
                make_tagged_url("/infos/belgique/article/378135/chastel-il-faudra-trouver-quelques-centaines-de-millions-au-printemps.html",
                                u"Chastel : \"il faudra trouver quelques centaines de millions au printemps\"",
                                set(["internal"])),
            ]

            expected_links = expected_sidebar_links + expected_bottom_links
            self.assert_taggedURLs_equals(expected_links, extracted_links)
