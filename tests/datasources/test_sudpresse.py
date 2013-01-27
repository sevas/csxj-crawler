# -*- coding: utf-8 -*-
"""
Link extraction test suite for sudpresse.py
"""

import os
from nose.tools import eq_
from csxj.datasources import sudpresse
from csxj.common.tagging import make_tagged_url

from csxj_test_tools import assert_taggedURLs_equals

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', 'sudpresse')

class TestSudpresseLinkExtraction(object):
    def test_same_owner_tagging(self):
        with open(os.path.join(DATA_ROOT, "same_owner_tagging.html")) as f:
            article, raw_html = sudpresse.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.nordeclair.fr/Actualite/Depeches/2012/02/13/dujardin-a-lille.shtml", u"""Nos confrères de Nord Eclair France """, set(['same owner', 'external', 'in text'])),
                make_tagged_url("http://www.nordeclair.fr/Actualite/Depeches/2012/02/13/dujardin-a-lille.shtml", u"""Voir sur le site nordeclair.fr""", set(['external', 'same owner'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)