# -*- coding: utf-8 -*-
"""
Link extraction test suite for DHNet
"""

import os
from nose.tools import nottest, eq_

from csxj.common.tagging import make_tagged_url, print_taggedURLs
from csxj.datasources import dhnet

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', 'dhnet')


class TestDHNetLinkExtraction(object):
    @nottest
    def assert_taggedURLs_equals(self, expected_links, extracted_links):
        eq_(len(expected_links), len(extracted_links))
        for expected, extracted in zip(sorted(expected_links), sorted(extracted_links)):
            eq_(expected, extracted)

    def test_simple_link_extraction(self):
        """ DHNet parser can extract bottom links from an article. """
        with open(os.path.join(DATA_ROOT, "single_bottom_link.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)

            extracted_links = article.links
            expected_links = [make_tagged_url("/infos/faits-divers/article/381491/protheses-pip-plus-de-330-belges-concernees.html",
                                              u"Prothèses PIP:  plus de 330 belges concernées",
                                              set(["internal"]))]
            self.assert_taggedURLs_equals(expected_links, extracted_links)

    def test_removed_article(self):
        """ DHNet parser should return a None value when processing a URL to a removed article. """
        with open(os.path.join(DATA_ROOT, "removed_article.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)

            eq_(article, None)

    def test_same_sidebox_and_bottom_links(self):
        """ DHNet parser can extract all the links in the sidebox and the bottom box, with adequate tags. """
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

    def test_no_links(self):
        """ DHNet parser returns an empty link list if the article has no link. """
        with open(os.path.join(DATA_ROOT, "no_links.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            eq_(len(extracted_links), 0)

    def test_embedded_video_and_in_text_link(self):
        """ DHNet parser can extract embedded videos and in text links. """
        with open(os.path.join(DATA_ROOT, "embedded_video_and_in_text_link.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links

            expected_sidebox_links = [
                make_tagged_url("#embed_pos1", u"Maingain : 'Charles Michel est tel quel !'", set(["sidebar box", "anchor"])),
                make_tagged_url("#embed_pos2", u"'Elio Di Rupo spreekt Vlaams', il y a de l'espoir", set(["sidebar box", "anchor"]))
            ]

            expected_intext_links = [
                make_tagged_url("", u"www.soisbelge.be ou www.compagnievictor.be. ", set(["no target", "in text"]))
            ]

            expected_embedded_videos = [
                make_tagged_url("http://sll.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&vformat=&sig=iLyROoafrZiF&autostart=false)",
                                u"Maingain : 'Charles Michel est tel quel !'",
                                set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sll.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&vformat=&sig=iLyROoafrZRe&autostart=false)",
                                u"'Elio Di Rupo spreekt Vlaams', il y a de l'espoir",
                                set(['kplayer', 'video', 'external', 'embedded']))
            ]

            expected_links = expected_intext_links + expected_sidebox_links + expected_embedded_videos
            self.assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_poll_script(self):
        """ DHNet can extract the link to an embedded js widget (e.g. from a polling service). """
        with open(os.path.join(DATA_ROOT, "embedded_poll_script.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links

            expected_sidebox_links = [
                make_tagged_url("#embed_pos1", u"SONDAGE: Quel est l'événement qui constitue, pour vous, la meilleure nouvelle de 2011?", set(["sidebar box", "anchor"]))
            ]

            expected_in_text_links = [
                make_tagged_url("", u"Quel est l'événement qui constitue, pour vous, la meilleure nouvelle de 2011?", set(["in text", "no target"]))
            ]

            expected_widget_links = [
                make_tagged_url("http://www.123votez.com/sondages/sondage-quel-evenement-constitue-pour-vous-meilleure-51734_10322823.php",
                                u"Quel est l'événement qui constitue, pour vous, la meilleure nouvelle de 2011?",
                                set(["external", "embedded", "script"]))
            ]

            expected_links = expected_sidebox_links + expected_in_text_links + expected_widget_links
            self.assert_taggedURLs_equals(expected_links, extracted_links)

    def test_storify_gallery_videos(self):
        """ DHNet parser can extract a storify link, tag DHNet galleries, detect embedded videos. """
        with open(os.path.join(DATA_ROOT, "storify_gallery_videos.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links

            expected_sidebox_links = [
                make_tagged_url("http://www.dhnet.be/infos/monde/article/413062/la-cote-est-des-etats-unis-se-barricade-pour-affronter-l-ouragan-sandy.html#encart", u"Sandy : 6 ou 7 Français disparus entre Martinique et Dominique", set([])),
                make_tagged_url("#embed_pos1", u"Retrouvez les photos et les vidéos de l'ouragan", set([])),
                make_tagged_url("/infos/monde/article/412959/sandy-presque-tous-les-vols-depuis-brussels-airport-vers-les-usa-annules.html", u"Sandy:  presque tous les vols depuis Brussels Airport vers les USA annulés", set([])),
                make_tagged_url("#embed_pos3", u"VIDEO: Sandy menace 50 millions d'Américains", set([])),
                make_tagged_url("http://galeries.dhnet.be/album/actumonde/ouragansandy/", u"La galerie photos de l'ouragan Sandy", set([])),
                make_tagged_url("#embed_pos2", u"VIDEO: Sandy a déjà fait 21 morts", set([])),

            ]

            expected_bottom_links = [
                make_tagged_url("/infos/monde/article/412959/sandy-presque-tous-les-vols-depuis-brussels-airport-vers-les-usa-annules.html", u"Sandy:  presque tous les vols depuis Brussels Airport vers les USA annulés", set(["internal"])),
                make_tagged_url("/infos/monde/article/412961/pour-eviter-l-ouragan-sandy-un-paquebot-se-refugie-dans-un-fjord-du-quebec.html", u"Pour éviter l'ouragan Sandy, un paquebot se réfugie dans un fjord du Québec", set(["internal"])),
                make_tagged_url("/infos/monde/article/412976/sandy-s-invite-dans-la-campagne-presidentielle-americaine.html", u"Sandy s'invite dans la campagne présidentielle américaine", set(["internal"])),
                make_tagged_url("/infos/monde/article/413089/sandy-11600-belges-concernes-par-l-ouragan.html", u"Sandy: 11.600 Belges concernés par l'ouragan", set(["internal"])),
                make_tagged_url("/infos/monde/article/413108/sandy-au-moins-16-morts-aux-usa-deux-reacteurs-nucleaires-fermes.html", u"Sandy: au moins 16 morts aux USA, deux réacteurs nucléaires fermés", set(["internal"])),
                make_tagged_url("http://www.dhnet.be/infos/monde/article/413062/la-cote-est-des-etats-unis-se-barricade-pour-affronter-l-ouragan-sandy.html#encart", u"Sandy : 6 ou 7 Français disparus entre Martinique et Dominique", set(["internal"])),
                make_tagged_url("http://galeries.dhnet.be/album/actumonde/ouragansandy/", u"La galerie photos de l'ouragan Sandy", set(["internal", 'image gallery', 'internal site'])),
            ]

            expected_embedded_media_links = [
                make_tagged_url("http://storify.com/pocket_pau/l-ouragan-sandy-menace-les-etats-unis",
                                u"""View the story "L'ouragan Sandy menace les Etats-Unis" on Storify""",
                                set(["embedded", "script", "external"])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=d0f8730a863s&autostart=false",
                                u"VIDEO: Sandy a déjà fait 21 morts",
                                set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=b5224f57c4cs&autostart=false",
                                u"VIDEO: Sandy menace 50 millions d'Américains",
                                set(['kplayer', 'video', 'external', 'embedded']))
            ]

            expected_links = expected_sidebox_links + expected_bottom_links + expected_embedded_media_links
            self.assert_taggedURLs_equals(expected_links, extracted_links)

    def test_media_overload(self):
        """ DHNet can extract links from a page with a rich collection of embedded media (twitter widget, embedded videos, regular links, poll script). """
        with open(os.path.join(DATA_ROOT, "media_overload.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links

            expected_sidebox_links = [
                make_tagged_url("#embed_pos1", u"""Vidéo : Dexia devient Belfius""", set(["internal", "anchor"])),
                make_tagged_url("#embed_pos2", u"""Jos Clijsters (CEO) présente Belfius""", set(["internal", "anchor"])),
                make_tagged_url("#embed_pos6", u"""Twitter s'emballe avec #RemplaceLeTitreDunFilmParBelfius""", set(["internal", "anchor"])),
                make_tagged_url("#embed_pos3", u"""Quel nom aurait-il fallu donner à la nouvelle Dexia ?""", set(["internal", "anchor"])),
                make_tagged_url("#embed_pos4", u"""Sondage : le logo Belfius est...""", set(["internal", "anchor"])),
                make_tagged_url("#embed_pos5", u"""Sondage: Le nom "Belfius", une bonne ou mauvaise idée ?""", set(["internal", "anchor"])),
            ]

            expected_in_text_links = [
                make_tagged_url("http://storify.com/pocket_pau/belfius-aide-le-transit-intestinal", u"""View the story ""Belfius aide le transit intestinal" " on Storify""", set(['in text', 'external']))

            ]

            expected_bottom_links = [
                make_tagged_url("/infos/economie/article/387096/dexia-s-appellera-belfius-et-voici-le-logo.html", u"""Dexia s'appellera Belfius... et voici le logo !""", set(['internal']))
            ]

            expected_embedded_media_links = [
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=a2edd636accs&autostart=false",
                                u"""__NO_TITLE__""",
                                set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=b8f94722bcas&autostart=false",
                                u"""Jos Clijsters (CEO) présente Belfius""",
                                set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://www.123votez.com/sondages/sondage-quel-aurait-fallu-donner-nouvelle-dexia-51734_10326940.php",
                                u"""Quel nom aurait-il fallu donner à la nouvelle Dexia ?""",
                                set(['external', 'embedded', 'script'])),
                make_tagged_url("http://www.123votez.com/sondages/sondage-sondage-logo-belfius-51734_10326938.php",
                                u"""SONDAGE: Le logo de Belfius est...""",
                                set(['external', 'embedded', 'script'])),
                make_tagged_url("http://www.123votez.com/sondages/sondage-belfius-bonne-mauvaise-idee-51734_10326936.php",
                                u"""Le nom "Belfius", une bonne ou mauvaise idée ?""",
                                set(['external', 'embedded', 'script'])),
                make_tagged_url(u"https://twitter.com/search?q=%23RemplaceLetitreDunFilmParBelfius",
                                u"""Twitter widget: search for #RemplaceLetitreDunFilmParBelfius""",
                                set(['twitter widget', 'script', 'twitter search', 'embedded', 'external'])),
            ]

            expected_links = expected_sidebox_links + expected_in_text_links + expected_bottom_links + expected_embedded_media_links
            self.assert_taggedURLs_equals(expected_links, extracted_links)
