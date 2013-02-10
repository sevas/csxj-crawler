# -*- coding: utf-8 -*-
"""
Link extraction test suite for dhnet.py
"""

import os
from nose.tools import eq_

from csxj.common.tagging import make_tagged_url
from csxj.datasources import dhnet

from csxj_test_tools import assert_taggedURLs_equals

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', 'dhnet')


class TestDHNetLinkExtraction(object):
    def test_simple_link_extraction(self):
        """ dhnet parser can extract bottom links from an article. """
        with open(os.path.join(DATA_ROOT, "single_bottom_link.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)

            extracted_links = article.links
            expected_links = [make_tagged_url("/infos/faits-divers/article/381491/protheses-pip-plus-de-330-belges-concernees.html",
                                              u"Prothèses PIP:  plus de 330 belges concernées",
                                              set(["internal", 'bottom box']))]
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_removed_article(self):
        """ dhnet parser returns 'None' when processing a URL to a removed article. """
        with open(os.path.join(DATA_ROOT, "removed_article.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)

            eq_(article, None)

    def test_same_sidebox_and_bottom_links(self):
        """ dhnet parser can extract all the links in the sidebox and the bottom box, with adequate tags. """
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
                                set(["internal", 'bottom box'])),
                make_tagged_url("/infos/belgique/article/378135/chastel-il-faudra-trouver-quelques-centaines-de-millions-au-printemps.html",
                                u"Chastel : \"il faudra trouver quelques centaines de millions au printemps\"",
                                set(["internal", 'bottom box'])),
            ]

            expected_links = expected_sidebar_links + expected_bottom_links
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_plaintext_links(self):
        """ dhnet parser can extract and tag plaintext links, as well as embedded iframe and a bunch of sidebar box and bottom box links. """
        with open(os.path.join(DATA_ROOT, "plaintext_links.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.infotec.be", u"""http://www.infotec.be""", set(['plaintext', 'external', 'in text'])),
                make_tagged_url("#embed_pos1", u"""Revivez la situation de cette matinée eneigée""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("/infos/societe/article/417423/au-volant-le-calme-est-le-plus-important.html", u"""Au volant, le calme est le plus important""", set(['internal', 'sidebar box'])),
                make_tagged_url("/infos/belgique/article/417349/plan-neige-active-pour-la-stib-et-le-tec-brabant-wallon.html", u"""Plan neige activé pour la STIB et le TEC Brabant wallon""", set(['internal', 'sidebar box'])),
                make_tagged_url("/infos/belgique/article/417311/sncb-et-infrabel-activent-leur-plan-hiver.html", u"""SNCB et Infrabel activent leur plan hiver""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://embed.scribblelive.com/Embed/v5.aspx?Id=73514&ThemeId=8499", u"""http://embed.scribblelive.com/Embed/v5.aspx?Id=73514&ThemeId=8499""", set(['embedded', 'external', 'iframe'])),
                make_tagged_url("/infos/belgique/article/417349/plan-neige-active-pour-la-stib-et-le-tec-brabant-wallon.html", u"""Plan neige activé pour la STIB et le TEC Brabant wallon""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/belgique/article/417311/sncb-et-infrabel-activent-leur-plan-hiver.html", u"""SNCB et Infrabel activent leur plan hiver""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/belgique/article/417423/au-volant-le-calme-est-le-plus-important.html", u"""Au volant, le calme est le plus important""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/belgique/article/417478/vingt-centres-de-ski-ouverts.html", u"""Vingt centres de ski ouverts""", set(['bottom box', 'internal'])),
                make_tagged_url("www.thalys.com", "www.thalys.com", set(["plaintext", "in text", "external"]))
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_no_links(self):
        """ dhnet parser returns an empty link list if the article has no link. """
        with open(os.path.join(DATA_ROOT, "no_links.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            eq_(len(extracted_links), 0)

    def test_embedded_video_and_in_text_link(self):
        """ dhnet parser can extract embedded videos and in text links. """
        with open(os.path.join(DATA_ROOT, "embedded_video_and_in_text_link.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links

            expected_sidebox_links = [
                make_tagged_url("#embed_pos1", u"Maingain : 'Charles Michel est tel quel !'", set(["internal", "sidebar box", "anchor"])),
                make_tagged_url("#embed_pos2", u"'Elio Di Rupo spreekt Vlaams', il y a de l'espoir", set(["internal", "sidebar box", "anchor"]))
            ]

            expected_intext_links = [
                make_tagged_url("", u"www.soisbelge.be ou www.compagnievictor.be. ", set(["no target", "in text"])),
                make_tagged_url("www.compagnievictor.be", "www.compagnievictor.be", set(["plaintext", "in text", "external"])),
                make_tagged_url("www.soisbelge.be", "www.soisbelge.be", set(["plaintext", "in text", "external"]))
            ]

            expected_embedded_videos = [
                make_tagged_url("http://sll.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&vformat=&sig=iLyROoafrZiF&autostart=false",
                                u"Maingain : 'Charles Michel est tel quel !'",
                                set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sll.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&vformat=&sig=iLyROoafrZRe&autostart=false",
                                u"'Elio Di Rupo spreekt Vlaams', il y a de l'espoir",
                                set(['kplayer', 'video', 'external', 'embedded']))
            ]

            expected_links = expected_intext_links + expected_sidebox_links + expected_embedded_videos
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_poll_script(self):
        """ dhnet can extract the link to an embedded js widget (e.g. from a polling service). """
        with open(os.path.join(DATA_ROOT, "embedded_poll_script.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links

            expected_sidebox_links = [
                make_tagged_url("#embed_pos1", u"SONDAGE: Quel est l'événement qui constitue, pour vous, la meilleure nouvelle de 2011?", set(["internal", "sidebar box", "anchor"]))
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
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_storify_gallery_videos(self):
        """ dhnet parser can extract a storify link, tag dhnet galleries, detect embedded videos. """
        with open(os.path.join(DATA_ROOT, "storify_gallery_videos.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links

            expected_sidebox_links = [
                make_tagged_url("http://www.dhnet.be/infos/monde/article/413062/la-cote-est-des-etats-unis-se-barricade-pour-affronter-l-ouragan-sandy.html#encart", u"Sandy : 6 ou 7 Français disparus entre Martinique et Dominique", set(["internal", "sidebar box"])),
                make_tagged_url("#embed_pos1", u"Retrouvez les photos et les vidéos de l'ouragan", set(["internal", "sidebar box", "anchor"])),
                make_tagged_url("/infos/monde/article/412959/sandy-presque-tous-les-vols-depuis-brussels-airport-vers-les-usa-annules.html", u"Sandy:  presque tous les vols depuis Brussels Airport vers les USA annulés", set(["internal", "sidebar box"])),
                make_tagged_url("#embed_pos3", u"VIDEO: Sandy menace 50 millions d'Américains", set(["internal", "sidebar box", "anchor"])),
                make_tagged_url("http://galeries.dhnet.be/album/actumonde/ouragansandy/", u"La galerie photos de l'ouragan Sandy", set(["internal", "sidebar box", "image gallery", "internal site"])),
                make_tagged_url("#embed_pos2", u"VIDEO: Sandy a déjà fait 21 morts", set(["internal", "sidebar box", "anchor"])),

            ]

            expected_bottom_links = [
                make_tagged_url("/infos/monde/article/412959/sandy-presque-tous-les-vols-depuis-brussels-airport-vers-les-usa-annules.html", u"Sandy:  presque tous les vols depuis Brussels Airport vers les USA annulés", set(["internal", 'bottom box'])),
                make_tagged_url("/infos/monde/article/412961/pour-eviter-l-ouragan-sandy-un-paquebot-se-refugie-dans-un-fjord-du-quebec.html", u"Pour éviter l'ouragan Sandy, un paquebot se réfugie dans un fjord du Québec", set(["internal", 'bottom box'])),
                make_tagged_url("/infos/monde/article/412976/sandy-s-invite-dans-la-campagne-presidentielle-americaine.html", u"Sandy s'invite dans la campagne présidentielle américaine", set(["internal", 'bottom box'])),
                make_tagged_url("/infos/monde/article/413089/sandy-11600-belges-concernes-par-l-ouragan.html", u"Sandy: 11.600 Belges concernés par l'ouragan", set(["internal", 'bottom box'])),
                make_tagged_url("/infos/monde/article/413108/sandy-au-moins-16-morts-aux-usa-deux-reacteurs-nucleaires-fermes.html", u"Sandy: au moins 16 morts aux USA, deux réacteurs nucléaires fermés", set(["internal", 'bottom box'])),
                make_tagged_url("http://www.dhnet.be/infos/monde/article/413062/la-cote-est-des-etats-unis-se-barricade-pour-affronter-l-ouragan-sandy.html#encart", u"Sandy : 6 ou 7 Français disparus entre Martinique et Dominique", set(["internal", 'bottom box'])),
                make_tagged_url("http://galeries.dhnet.be/album/actumonde/ouragansandy/", u"La galerie photos de l'ouragan Sandy", set(["internal", 'bottom box', 'image gallery', 'internal site'])),
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
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_media_overload(self):
        """ dhnet parser can extract links from a page with a rich collection of embedded media (twitter widget, embedded videos, regular links, poll script). """
        with open(os.path.join(DATA_ROOT, "media_overload.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links

            expected_sidebox_links = [
                make_tagged_url("#embed_pos1", u"""Vidéo : Dexia devient Belfius""", set(["sidebar box", "anchor", "internal"])),
                make_tagged_url("#embed_pos2", u"""Jos Clijsters (CEO) présente Belfius""", set(["sidebar box", "anchor", "internal"])),
                make_tagged_url("#embed_pos6", u"""Twitter s'emballe avec #RemplaceLeTitreDunFilmParBelfius""", set(["sidebar box", "anchor", "internal"])),
                make_tagged_url("#embed_pos3", u"""Quel nom aurait-il fallu donner à la nouvelle Dexia ?""", set(["sidebar box", "anchor", "internal"])),
                make_tagged_url("#embed_pos4", u"""Sondage : le logo Belfius est...""", set(["sidebar box", "anchor", "internal"])),
                make_tagged_url("#embed_pos5", u"""Sondage: Le nom "Belfius", une bonne ou mauvaise idée ?""", set(["sidebar box", "anchor", "internal"])),
            ]

            expected_in_text_links = [
                make_tagged_url("http://storify.com/pocket_pau/belfius-aide-le-transit-intestinal", u"""View the story ""Belfius aide le transit intestinal" " on Storify""", set(['in text', 'external']))

            ]

            expected_bottom_links = [
                make_tagged_url("/infos/economie/article/387096/dexia-s-appellera-belfius-et-voici-le-logo.html", u"""Dexia s'appellera Belfius... et voici le logo !""", set(['internal', 'bottom box']))
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
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_audio_video(self):
        """ dhnet can extract links to embedded audio and video content """

        with open(os.path.join(DATA_ROOT, "embedded_audio_video.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links

            expected_sidebox_links = [
                make_tagged_url("#embed_pos1", u"""Un jour de deuil national décrété après le drame de Sierre""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos2", u"""L'effroyable bilan de la tragédie en Suisse""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos3", u"""Vive émotion pour Elio Di Rupo après le drame de Sierre""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos6", u"""Les réactions de Vande Lanotte et Van Quickenborne""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos4", u"""Tragédie de Sierre : réaction de J. Milquet""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("http://podcast.dhnet.be/articles/audio_dh_388635_1331708882.mp3", u"""Accident de car en Suisse: écoutez Didier Reynders""", set(['sidebar box', 'audio', 'embedded', 'internal site'])),
                make_tagged_url("http://podcast.dhnet.be/articles/audio_dh_388635_1331708068.mp3", u"""Jan Luykx  revient sur l'accident de car de ce matin à Sierre""", set(['sidebar box', 'audio', 'embedded', 'internal site'])),
                make_tagged_url("http://podcast.dhnet.be/articles/audio_dh_388635_1331708936.mp3", u"""Le chef des informations de la police du canton de Valais""", set(['sidebar box', 'audio', 'embedded', 'internal site'])),
                make_tagged_url("http://podcast.dhnet.be/articles/audio_dh_388635_1331728657.mp3", u"""Le témoignage du chef de la police de Val d'anivier, reccueilli par Twizz Radio""", set(['sidebar box', 'audio', 'embedded', 'internal site'])),


            ]

            expected_bottom_links = [
                make_tagged_url("/infos/faits-divers/article/388683/tragedie-de-sierre-vous-avez-laisse-vos-condoleances.html", u"""Tragédie de Sierre: vous avez laissé vos condoléances""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/faits-divers/article/388635/tragedie-de-sierre-3-enfants-encore-dans-un-etat-serieux.html", u'''Tragédie de Sierre: 3 enfants encore dans un "état sérieux"''', set(['bottom box', 'internal'])),
                make_tagged_url("/infos/faits-divers/article/388704/tragedie-de-sierre-top-tours-possede-une-bonne-reputation.html", u"""Tragédie de Sierre: Top Tours possède une bonne réputation""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/faits-divers/article/388719/les-causes-de-l-accident-trois-pistes-possibles.html", u"""Les causes de l'accident ? Trois pistes possibles""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/faits-divers/article/388721/tragedie-de-sierre-vendredi-sera-une-journee-de-deuil-national.html", u"""Tragédie de Sierre: vendredi sera une journée de deuil national""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/faits-divers/article/388731/tragedie-de-sierre-les-enqueteurs-ne-confirment-pas-la-these-du-dvd.html", u"""Tragédie de Sierre: les enquêteurs ne confirment pas la thèse du DVD""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/faits-divers/article/388737/tragedie-de-sierre-qu-est-il-arrive-au-car-belge.html", u"""Tragédie de Sierre: qu'est-il arrivé au car belge?""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/faits-divers/article/388736/tragedie-de-sierre-un-gros-boum-puis-le-bus-eventre.html", u"""Tragédie de Sierre: un gros boum,  puis le bus éventré""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/faits-divers/article/388782/tragedie-de-sierre-le-match-alost-lommel-remis.html", u"""Tragédie de Sierre: Le match Alost-Lommel remis""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/faits-divers/article/388805/tragedie-de-sierre-toptours-etait-dans-le-rouge.html", u"""Tragédie de Sierre : Toptours était dans le rouge""", set(['bottom box', 'internal'])),
            ]

            expected_embedded_media_links = [
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=b68aaa9d47cs&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=8e6437d5479s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=42dcc8dbd55s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=c4a038b7874s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=2561f1bd073s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=b97ce2d0dc1s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=82c2aa5fc83s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=3869c7bf503s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=b2bca84c11fs&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=e2bbfd134fds&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=d68d030739fs&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=fa32644185bs&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://storify.com/pocket_pau/tragedie-a-sierre", u"""View the story "Tragédie à Sierre" on Storify""", set(['external', 'embedded', 'script'])),
            ]

            expected_links = expected_sidebox_links + expected_bottom_links + expected_embedded_media_links
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_same_owner_tagging(self):
        """ dhnet parser correctly tags 'same owner' links """
        with open(os.path.join(DATA_ROOT, "same_owner_tagging.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.essentielle.be/", u"""L'info au féminin sur Essentielle.be""", set(['sidebar box', 'external', 'same owner'])),
                make_tagged_url("http://babescm.blogs.dhnet.be/", u"""Retrouvez les plus belles sur notre blog Babes""", set(['sidebar box', 'internal site'])),
                make_tagged_url("/infos/societe/article/420071/un-nouveau-regime-miracle-75kg-en-six-semaines.html", u"""Un nouveau régime miracle : - 7,5 kg en six semaines""", set(['internal', 'sidebar box'])),
                make_tagged_url("/infos/societe/article/420071/un-nouveau-regime-miracle-75kg-en-six-semaines.html", u"""Un nouveau régime miracle : - 7,5 kg en six semaines""", set(['bottom box', 'internal'])),
                make_tagged_url("http://www.essentielle.be/", u"""L'info au féminin sur Essentielle.be""", set(['bottom box', 'external', 'same owner'])),
                make_tagged_url("http://babescm.blogs.dhnet.be/", u"""Retrouvez les plus belles sur notre blog Babes""", set(['bottom box', 'internal site'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_extract_embedded_tweets(self):
        """ dhnet parser can extract rendered embedded tweets"""
        with open(os.path.join(DATA_ROOT, "extract_embedded_tweets.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            bottom_links = [
            ]
            audio_content_links = [
            ]
            sidebox_links = [
            ]
            embedded_content_links = [
            ]
            in_text_links = [
                make_tagged_url("https://twitter.com/datirachida/status/204621853304700928", u"""https://twitter.com/datirachida/status/204621853304700928""", set(['tweet', 'embedded media', 'external'])),
                make_tagged_url("https://twitter.com/Bernard_Debre/status/204848053025390592", u"""https://twitter.com/Bernard_Debre/status/204848053025390592""", set(['tweet', 'embedded media', 'external'])),
                make_tagged_url("https://twitter.com/datirachida/status/204904963619561475", u"""https://twitter.com/datirachida/status/204904963619561475""", set(['tweet', 'embedded media', 'external'])),
            ]
            expected_links = bottom_links + audio_content_links + sidebox_links + embedded_content_links + in_text_links
            assert_taggedURLs_equals(expected_links, extracted_links)
