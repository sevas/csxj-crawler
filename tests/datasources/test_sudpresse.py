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
    def test_sidebar_box_tagging(self):
        """ Sudpresse parser correctly tags 'sidebar box' links """
        with open(os.path.join(DATA_ROOT, "sidebar_box_tagging.html")) as f:
            article, raw_html = sudpresse.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("/actualite/fil_info/2011-05-10/wouter-weylandt-un-registre-de-condoleances-ouvert-au-centre-du-tour-des-flandres-872031.shtml", u"""Wouter Weylandt : un registre de condoléances ouvert au centre du Tour des Flandres""", set(['internal', 'sidebar box'])),
                make_tagged_url("/sports/cyclisme/2011-05-10/deces-de-weylandt-la-4e-etape-du-giro-neutralisee-872000.shtml", u"""e étape du Giro neutralisée" >Décès de Weylandt: la 4e étape du Giro neutralisée""", set(['internal', 'sidebar box'])),
                make_tagged_url("/sports/cyclisme/2011-05-10/giro-neutralisee-la-4e-etape-prendra-la-forme-d-un-defile-871999.shtml", u"""Giro: neutralisée, la 4e étape prendra la forme dun défilé""", set(['internal', 'sidebar box'])),
                make_tagged_url("/sports/cyclisme/2011-05-10/andy-schleck-pour-wouter-weylandt-repose-en-paix-mon-ami-871991.shtml", u"""Andy Schleck pour Wouter Weylandt: Repose en paix, mon ami """, set(['internal', 'sidebar box'])),
                make_tagged_url("/sports/cyclisme/2011-05-10/deces-du-coureur-wouter-weylandt-leopard-trek-reste-sur-le-giro-871934.shtml", u"""Décès de Wouter Weylandt: Leopard-Trek reste sur le Giro""", set(['internal', 'sidebar box'])),
                make_tagged_url("/sports/cyclisme/2011-05-09/giro-terrible-chute-de-wouter-weylandt-dans-une-descente-son-etat-est-inquietant-871804.shtml", u"""Décès de Wouter Weylandt: "Un cas désespéré", explique le médecin de la course""", set(['internal', 'sidebar box'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_plaintext_links_tagging(self):
        """ Sudpresse parser correctly tags 'plaintext' links."""
        with open(os.path.join(DATA_ROOT, "plaintext_links_tagging.html")) as f:
            article, raw_html = sudpresse.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://expo-guide.com", u"""http://expo-guide.com""", set(['plaintext', 'external', 'in text'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)



    def test_same_owner_tagging(self):
        """ Sudpresse parser correctly tags 'same owner' links """
        with open(os.path.join(DATA_ROOT, "same_owner_tagging.html")) as f:
            article, raw_html = sudpresse.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.nordeclair.fr/Actualite/Depeches/2012/02/13/dujardin-a-lille.shtml", u"""Nos confrères de Nord Eclair France """, set(['same owner', 'external', 'in text'])),
                make_tagged_url("http://www.nordeclair.fr/Actualite/Depeches/2012/02/13/dujardin-a-lille.shtml", u"""Voir sur le site nordeclair.fr""", set(['external', 'same owner', 'sidebar box'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)