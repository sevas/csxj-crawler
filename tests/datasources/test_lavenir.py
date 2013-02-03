# -*- coding: utf-8 -*-
"""
Link extraction test suite for lavenir.py
"""

import os
from nose.tools import eq_

from csxj.common.tagging import make_tagged_url
from csxj.datasources import lavenir

from csxj_test_tools import assert_taggedURLs_equals

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', lavenir.SOURCE_NAME)

class TestLavenirLinkExtraction(object):
    def test_same_owner_tagging(self):
        """ lavenir parser correctly tags 'same owner' links """
        with open(os.path.join(DATA_ROOT, "same_owner_tagging.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.jobat.be/fr/articles/de-quel-bois-sont-faits-vos-cadets-au-boulot/?utm_source=lavenir&utm_medium=content&utm_campaign=artikel&utm_content=link", u"""Une volonté d’engagement et encore 2 autres caractéristiques de ces jeunes recrues""", set(['same owner', 'external', 'in text'])),
                make_tagged_url("http://www.jobat.be/fr/articles/cinq-types-de-collegues-insupportables-que-nous-connaissons-tous/?utm_source=lavenir&utm_medium=content&utm_campaign=artikel&utm_content=link", u"""Nico le petit comique et 4 autres collègues que nous connaissons tous""", set(['sidebar box', 'external', 'same owner'])),
                make_tagged_url("http://www.jobat.be/fr/articles/5-ruses-pour-obtenir-plus-de-ses-collegues/?utm_source=lavenir&utm_medium=content&utm_campaign=artikel&utm_content=link", u"""5 ruses pour en obtenir plus de ses collègues""", set(['sidebar box', 'external', 'same owner'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)
