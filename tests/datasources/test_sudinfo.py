# coding=utf-8
"""
Test suites for sudinfo.py
"""

import os

from csxj.common.tagging import make_tagged_url
from csxj.datasources import sudinfo

from csxj_test_tools import assert_taggedURLs_equals, assert_content_equals

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', 'sudinfo')


class TestSudinfoLinkExtraction(object):
    def test_no_links(self):
        """ sudinfo parser returns an empty link list if the article has no link. """
        with open(os.path.join(DATA_ROOT, "no_links.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_sidebar_box_tagging(self):
        """ sudinfo parser can extract and tag sidebar links from an article. """
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
        """ sudinfo parser can extract and tag in text and sidebar links to same owner sites."""
        with open(os.path.join(DATA_ROOT, "in_text_same_owner.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.lesoir.be/sports/football/2012-05-31/en-combien-de-temps-hazard-gagne-t-il-votre-salaire-918967.php", u"""Le Soir.be""", set(['same owner', 'external', 'in text'])),
                make_tagged_url("http://www.lesoir.be/sports/football/2012-05-31/en-combien-de-temps-hazard-gagne-t-il-votre-salaire-918967.php", u"""En combien de temps, Eden Hazard gagne votre salaire?""", set(['sidebar box', 'external', 'same owner'])),
                make_tagged_url("slate.fr", u"""slate.fr""", set(['in text', 'plaintext', 'external']))
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_video_extraction(self):
        """ sudinfo parser can extract and tag embedded video from the bottom of an article. """
        with open(os.path.join(DATA_ROOT, "embedded_video_extraction.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url(u"http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&sig=5a5a3d9f57ds", u"""http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&sig=5a5a3d9f57ds""", set(['video', 'external', 'embedded', 'bottom'])),
                make_tagged_url(u"/338194/article/regions/tournai/2012-02-29/prostitution-“dodo-la-saumure”-va-demander-l’acquittement-sur-tout-jeudi-devant", u"""Prostitution: “Dodo la Saumure” va demander l’acquittement sur tout jeudi devant la justice""", set(['internal', 'sidebar box'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_in_text_link_extraction(self):
        """ sudinfo parser can extract and tag in-text links """
        with open(os.path.join(DATA_ROOT, "in_text_link_extraction.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.sporza.be/cm/sporza/videozone/MG_programmas/MG_Extra_Time_GNMA/1.1450385?utm_medium=twitter&utm_source=dlvr.it", u"""Cliquez ici pour consulter la vidéo capturée par nos confrères de Sporza.""", set(['external', 'in text'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_iframe_in_text(self):
        """ sudinfo parser extracts iframes within text block, does not consider iframes as text content"""
        with open(os.path.join(DATA_ROOT, "links_iframe_in_text.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.coveritlive.com/index2.php/option=com_altcaster/task=viewaltcast/altcast_code=82d305926f/height=850/width=600", u"""__EMBEDDED_IFRAME__""", set(['iframe', 'external', 'embedded'])),
                make_tagged_url("http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&sig=9bb12b4294es", u"""http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&sig=9bb12b4294es""", set(['video', 'external', 'embedded', 'bottom'])),
                make_tagged_url("http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&sig=ab7055b944bs", u"""http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&sig=ab7055b944bs""", set(['video', 'external', 'embedded', 'bottom'])),
                make_tagged_url("http://portfolio.sudpresse.be/main.php?g2_itemId=1033320", u"""Nos photos de la conférence de presse""", set(['internal', 'sidebar box', 'gallery'])),
                make_tagged_url("/425052/article/sports/foot-belge/standard/2012-05-29/ron-jans-au-standard-les-supporters-partages-entre-c-est-n-importe-quoi-et-", u'''Ron Jans au Standard: les supporters partagés entre "C'est n'importe quoi" et "Laissons-lui sa chance"''', set(['internal', 'sidebar box'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_intext_not_plaintext(self):
        """ sudinfo parser extracts in-text urls only once (and not as plaintext URLs)"""
        with open(os.path.join(DATA_ROOT, "links_intext_not_plaintext.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://secourslux.blogs.sudinfo.be", u"""http://secourslux.blogs.sudinfo.be""", set(['in text', 'internal', 'jblog'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_embedded_thumbnails(self):
        """ sudinfo parser ignores the images from the embedded gallery in the 'medias' box"""
        with open(os.path.join(DATA_ROOT, "links_embedded_thumbnails.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)


    def test_links_embedded_youtube(self):
        """ sudinfo parser extract links to youtube video presented inside the article media gallery"""
        with open(os.path.join(DATA_ROOT, "links_embedded_youtube.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.youtube.com/watch?v=4tkHmGycfz4", u"""__NO_TITLE__""", set(['youtube', 'video', 'external', 'embedded'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_empty_gallery_div(self):
        """ sudinfo parser ignores empty divs in the article media gallery"""
        with open(os.path.join(DATA_ROOT, "links_empty_gallery_div.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url(u"http://www.coveritlive.com/index2.php/option=com_altcaster/task=viewaltcast/altcast_code=3efed3214b/height=650/width=450", u"""__EMBEDDED_IFRAME__""", set(['iframe', 'external', 'embedded'])),
                make_tagged_url(u"/443260/article/sports/tennis/2012-06-26/wimbledon-olivier-rochus-elimine-des-le-1er-tour", u"""Wimbledon: Olivier Rochus éliminé dès le 1er tour""", set(['internal', 'sidebar box'])),
                make_tagged_url(u"/440873/article/regions/liege/sports/2012-06-22/le-perron-d’or-est-pour-david-goffin", u"""Le Perron d’Or est pour David Goffin""", set(['internal', 'sidebar box'])),
                make_tagged_url(u"/438432/article/actualite/l-info-en-continu/2012-06-19/15 nouveaux-athletes-pour-les-jo-de-londres-avec-david-goffin", u"""15 nouveaux athlètes pour les JO de Londres avec David Goffin""", set(['internal', 'sidebar box'])),
                make_tagged_url(u"http://portfolio.sudpresse.be/main.php?g2_itemId=1063685", u"""Les photos de David et Stéphanie à Wimbledon""", set(['internal', 'sidebar box', 'gallery'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_embedded_kewego_gallery(self):
        """ sudinfo parser can extract kewego videos from the article media gallery"""
        with open(os.path.join(DATA_ROOT, "links_embedded_kewego_gallery.html")) as f:
            article, raw_html = sudinfo.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://portfolio.sudpresse.be/main.php?g2_itemId=992521", u"""Une belle après-midi à Bleid""", set(['internal', 'sidebar box', 'gallery'])),
                make_tagged_url("http://sll.kewego.com/swf/p3/epix.swf?language_code=fr&playerKey=7b7e2d7a9682&skinKey=a07930e183e6&sig=054c411daa8s&autostart=0&advertise=true", u"""__NO_TITLE__""", set(['kewego', 'video', 'external', 'embedded'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)


class TestSudinfoContentExtracttion(object):
    def test_intext_link(self):
        """ sudinfo parser correctly extract text content, even when there is a link inside"""
        with open(os.path.join(DATA_ROOT, "content_intext_link.html")) as f:
            article, _ = sudinfo.extract_article_data(f)

            #expected_intro = u"""Le flash mob proposé par Stéphane Thiry, officier pompier au SRI de Saint-Hubert a obtenu un succès tel qu'ils étaient plus de 300 à danser et se regarder lors de la journée portes-ouvertes des pompiers de ce dimanche 7 octobre."""
            expected_content = [u"""Grosse foule et succès mérité pour les pompiers borquins qui ont réalisé multiples exrecices face au public.Une jounée sous un ciel clément et ensoleillé. Et pour cause, Mr Météo avait rangé ses grenouilles et les pompiers ont imploré Sainte-Claire en lui portant des oeufs.""",
                                u"""Plus de détails et un album photo sur  http://secourslux.blogs.sudinfo.be"""]
            assert_content_equals(expected_content, article.content)
