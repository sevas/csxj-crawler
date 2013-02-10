# -*- coding: utf-8 -*-
"""
Link extraction test suite for sudinfo.py
"""

import os
from nose.tools import eq_


from csxj.datasources.parser_tools.utils import convert_utf8_url_to_ascii
from csxj.common.tagging import make_tagged_url
from csxj.datasources import sudinfo

from csxj_test_tools import assert_taggedURLs_equals

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', 'sudinfo')


class TestSudinfoLinkExtraction(object):

    def test_no_links(self):
        """ Sudinfo parser returns an empty link list if the article has no link. """
        with open(os.path.join(DATA_ROOT, "no_links.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)



    def test_sidebar_box_tagging(self):
        """ Sudinfo parser can extract and tag sidebar links from an article. """
        with open(os.path.join(DATA_ROOT, "sidebar_box_tagging.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url(u"/338420/article/sports/foot-belge/2012-02-29/grece-belgique-1-1-les-diables-tiennent-le-nul-a-10-contre-11", u"""Grèce - Belgique (1-1): les Diables tiennent le nul à 10 contre 11""", set(['internal', 'sidebar box'])),
                make_tagged_url(u"/338862/article/sports/foot-etranger/2012-02-29/foot-amicaux-la-france-surprend-l’italie-decoit-l’argentine-dit-merci-a-messi", u"""Foot (amicaux): la France surprend, l’Italie déçoit, l’Argentine dit "merci" à Messi""", set(['internal', 'sidebar box'])),
                make_tagged_url(u"/338806/article/sports/foot-belge/2012-02-29/angleterre-belgique-4-0-les-diablotins-encaissent-un-but-d’anthologie-video", u"""Angleterre - Belgique (4-0): les Diablotins encaissent un but d’anthologie (vidéo)""", set(['internal', 'sidebar box'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_in_text_same_owner(self):
        """ Sudinfo parser can extract and tag in text and sidebar links to same owner sites."""
        with open(os.path.join(DATA_ROOT, "in_text_same_owner.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.lesoir.be/sports/football/2012-05-31/en-combien-de-temps-hazard-gagne-t-il-votre-salaire-918967.php", u"""Le Soir.be""", set(['same owner', 'external', 'in text'])),
                make_tagged_url("http://www.lesoir.be/sports/football/2012-05-31/en-combien-de-temps-hazard-gagne-t-il-votre-salaire-918967.php", u"""En combien de temps, Eden Hazard gagne votre salaire?""", set(['sidebar box', 'external', 'same owner'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)



    def test_embedded_video_extraction(self):
        """ Sudinfo parser can extract and tag embedded video from the bottom of an article. """
        with open(os.path.join(DATA_ROOT, "embedded_video_extraction.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url(u"http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&sig=5a5a3d9f57ds", u"""http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&sig=5a5a3d9f57ds""", set(['embedded video', 'bottom video', 'external', 'embedded'])),
                make_tagged_url(u"/338194/article/regions/tournai/2012-02-29/prostitution-“dodo-la-saumure”-va-demander-l’acquittement-sur-tout-jeudi-devant", u"""Prostitution: “Dodo la Saumure” va demander l’acquittement sur tout jeudi devant la justice""", set(['internal', 'sidebar box'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)


    def test_in_text_link_extraction(self):
        """ Sudinfo parser can extract and tag in-text links """
        with open(os.path.join(DATA_ROOT, "in_text_link_extraction.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.sporza.be/cm/sporza/videozone/MG_programmas/MG_Extra_Time_GNMA/1.1450385?utm_medium=twitter&utm_source=dlvr.it", u"""Cliquez ici pour consulter la vidéo capturée par nos confrères de Sporza.""", set(['external', 'in text'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)


    def test_links_iframe_in_text(self):
        """ Sudinfo parser can extract iframes within text block"""
        with open(os.path.join(DATA_ROOT, "links_iframe_in_text.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.coveritlive.com/index2.php/option=com_altcaster/task=viewaltcast/altcast_code=82d305926f/height=850/width=600", u"""__EMBEDDED_IFRAME__""", set(['iframe', 'external', 'embedded'])),
                make_tagged_url("http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&sig=9bb12b4294es", u"""http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&sig=9bb12b4294es""", set(['embedded video', 'bottom video', 'external', 'embedded'])),
                make_tagged_url("http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&sig=ab7055b944bs", u"""http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&sig=ab7055b944bs""", set(['embedded video', 'bottom video', 'external', 'embedded'])),
                make_tagged_url("http://portfolio.sudpresse.be/main.php?g2_itemId=1033320", u"""Nos photos de la conférence de presse""", set(['internal', 'sidebar box', 'gallery', 'external'])),
                make_tagged_url("/425052/article/sports/foot-belge/standard/2012-05-29/ron-jans-au-standard-les-supporters-partages-entre-c-est-n-importe-quoi-et-", u'''Ron Jans au Standard: les supporters partagés entre "C'est n'importe quoi" et "Laissons-lui sa chance"''', set(['internal', 'sidebar box'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)