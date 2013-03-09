# coding=utf-8
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
                make_tagged_url("http://galeries.dhnet.be/album/actumonde/ouragansandy/", u"La galerie photos de l'ouragan Sandy", set(["internal", "sidebar box", "image gallery"])),
                make_tagged_url("#embed_pos2", u"VIDEO: Sandy a déjà fait 21 morts", set(["internal", "sidebar box", "anchor"])),

            ]

            expected_bottom_links = [
                make_tagged_url("/infos/monde/article/412959/sandy-presque-tous-les-vols-depuis-brussels-airport-vers-les-usa-annules.html", u"Sandy:  presque tous les vols depuis Brussels Airport vers les USA annulés", set(["internal", 'bottom box'])),
                make_tagged_url("/infos/monde/article/412961/pour-eviter-l-ouragan-sandy-un-paquebot-se-refugie-dans-un-fjord-du-quebec.html", u"Pour éviter l'ouragan Sandy, un paquebot se réfugie dans un fjord du Québec", set(["internal", 'bottom box'])),
                make_tagged_url("/infos/monde/article/412976/sandy-s-invite-dans-la-campagne-presidentielle-americaine.html", u"Sandy s'invite dans la campagne présidentielle américaine", set(["internal", 'bottom box'])),
                make_tagged_url("/infos/monde/article/413089/sandy-11600-belges-concernes-par-l-ouragan.html", u"Sandy: 11.600 Belges concernés par l'ouragan", set(["internal", 'bottom box'])),
                make_tagged_url("/infos/monde/article/413108/sandy-au-moins-16-morts-aux-usa-deux-reacteurs-nucleaires-fermes.html", u"Sandy: au moins 16 morts aux USA, deux réacteurs nucléaires fermés", set(["internal", 'bottom box'])),
                make_tagged_url("http://www.dhnet.be/infos/monde/article/413062/la-cote-est-des-etats-unis-se-barricade-pour-affronter-l-ouragan-sandy.html#encart", u"Sandy : 6 ou 7 Français disparus entre Martinique et Dominique", set(["internal", 'bottom box'])),
                make_tagged_url("http://galeries.dhnet.be/album/actumonde/ouragansandy/", u"La galerie photos de l'ouragan Sandy", set(["internal", 'bottom box', 'image gallery'])),
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

            expected_intext_urls = [
                make_tagged_url("flightaware.com", u"flightaware.com", set(['in text', 'plaintext', 'external']))
            ]

            expected_links = expected_sidebox_links + expected_bottom_links + expected_embedded_media_links + expected_intext_urls
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
                make_tagged_url("http://podcast.dhnet.be/articles/audio_dh_388635_1331708882.mp3", u"""Accident de car en Suisse: écoutez Didier Reynders""", set(['sidebar box', 'audio', 'embedded', 'podcast'])),
                make_tagged_url("http://podcast.dhnet.be/articles/audio_dh_388635_1331708068.mp3", u"""Jan Luykx  revient sur l'accident de car de ce matin à Sierre""", set(['sidebar box', 'audio', 'embedded', 'podcast'])),
                make_tagged_url("http://podcast.dhnet.be/articles/audio_dh_388635_1331708936.mp3", u"""Le chef des informations de la police du canton de Valais""", set(['sidebar box', 'audio', 'embedded', 'podcast'])),
                make_tagged_url("http://podcast.dhnet.be/articles/audio_dh_388635_1331728657.mp3", u"""Le témoignage du chef de la police de Val d'anivier, reccueilli par Twizz Radio""", set(['sidebar box', 'audio', 'embedded', 'podcast'])),


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

    def test_kplayer(self):
        """ dhnet parser correctly extracts and tags embedded kplayer """
        with open(os.path.join(DATA_ROOT, "kplayer.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("#embed_pos1", u"""Regardez la bande-annonce d'Un Plan Parfait""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("http://www.cinebel.be/fr/film/1008711/Un%20Plan%20Parfait", u"""Tout savoir sur Un Plan Parfait sur Cinebel""", set(['sidebar box', 'external', 'same owner'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&playerKey=25e1a69bf7eb&configKey=3162af563b91&suffix=&sig=1034e8b6d47s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://www.cinebel.be/fr/film/1008711/Un%20Plan%20Parfait", u"""Tout savoir sur Un Plan Parfait sur Cinebel""", set(['bottom box', 'external', 'same owner'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_hungarian_video(self):
        """ dhnet parser correctly extracts embedded hungarian videos """
        with open(os.path.join(DATA_ROOT, "embedded_hungarian_video.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("#embed_pos1", u"""Deuxième but de Benteke à la 50e""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos2", u"""But de Benteke à la 29e""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("/sports/football/article/418325/le-coup-de-boule-de-fellaini.html", u"""Le "coup de boule" de Fellaini""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://videa.hu/videok/sport/liverpool-vs-aston-villa-03-benteke-SqNSxnB4M6HXc25h", u"""Deuxième but de Benteke à la 50e""", set(['external', 'embedded'])),
                make_tagged_url("http://videa.hu/videok/sport/liverpool-vs-aston-villa-01-benteke-W9oE53lSeQqS0Puk", u"""But de Benteke à la 29e""", set(['external', 'embedded'])),
                make_tagged_url("/sports/football/article/418325/le-coup-de-boule-de-fellaini.html", u"""Le "coup de boule" de Fellaini""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/football/article/418302/ronaldo-gagne-son-combat-contre-le-surpoids.html", u"""Ronaldo gagne son combat contre le surpoids""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/football/article/418317/des-red-devils-et-des-citizens-victorieux.html", u"""Des Red Devils et des Citizens victorieux""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/football/article/418339/hazard-et-chelsea-battus-en-finale-de-la-coupe-du-monde-des-clubs-1-0.html", u"""Hazard et Chelsea battus en finale de la Coupe du monde des clubs (1-0)""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/football/article/418482/les-medias-anglais-chantent-a-la-gloire-de-benteke.html", u"""Les médias anglais chantent à la gloire de Benteke""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/football/article/418959/lambert-on-n-a-pas-achete-benteke-pour-le-revendre.html", u'''Lambert : "On n'a pas acheté Benteke pour le revendre !"''', set(['bottom box', 'internal'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_audio(self):
        """ dhnet parser can extract embedded audio"""
        with open(os.path.join(DATA_ROOT, "embedded_audio.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://vocaroo.com/player.swf?playMediaID=s17mkpGCh0Qr&autoplay=0", u"""http://vocaroo.com/player.swf?playMediaID=s17mkpGCh0Qr&autoplay=0""", set(['audio', 'external', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_other_embedded_video_type(self):
        """ dhnet parser can extract embedded wat.tv video"""
        with open(os.path.join(DATA_ROOT, "other_embedded_video_type.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("#embed_pos1", u"""Voir l'intégralité de la vidéo""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("http://www.wat.tv/video/videosurveillance-dsk-sofitel-4lh5t_2exyv_.html", u"""Vidéo VIDEOSURVEILLANCE DSK SOFITEL sur wat.tv""", set(['video', 'external', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_brightcove_video(self):
        """ dhnet parser can extract embedded brightcove video"""
        with open(os.path.join(DATA_ROOT, "embedded_brightcove_video.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("#embed_pos1", u"""Regardez la boulette de  Xavier Bongibault.""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos2", u"""Xavier Bongibault présente ses excuses @bfmtv""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("/infos/monde/article/421044/des-centaines-de-milliers-de-manifestants-contre-le-mariage-gay.html", u"""Des centaines de milliers de manifestants contre le mariage gay""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://galeries.dhnet.be/album/actumonde/manifantimariagegay/01.jpg/", u"""Les manifs contre le mariage gay""", set(['sidebar box', 'internal', 'image gallery'])),
                make_tagged_url("http://link.brightcove.com/services/player/bcpid1027556707001?bctid=2090284983001", u"""http://link.brightcove.com/services/player/bcpid1027556707001?bctid=2090284983001""", set(['video', 'external', 'embedded'])),
                make_tagged_url("http://www.dailymotion.com/embed/video/xwq838", u"""http://www.dailymotion.com/embed/video/xwq838""", set(['embedded', 'external', 'iframe'])),
                make_tagged_url("/infos/monde/article/421044/des-centaines-de-milliers-de-manifestants-contre-le-mariage-gay.html", u"""Des centaines de milliers de manifestants contre le mariage gay""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/421154/mariage-gay-di-rupo-est-fier-de-la-modernite-de-la-belgique.html", u"""Mariage gay: Di Rupo est "fier de la modernité" de la Belgique""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/421973/francois-hollande-va-recevoir-les-opposants-au-mariage-homo.html", u"""François Hollande va recevoir les opposants au mariage homo""", set(['bottom box', 'internal'])),
                make_tagged_url("http://galeries.dhnet.be/album/actumonde/manifantimariagegay/01.jpg/", u"""Les manifs contre le mariage gay""", set(['bottom box', 'internal', 'image gallery'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_ooyala_embedded_video(self):
        """ dhnet parser can extract embedded ooyala video"""
        with open(os.path.join(DATA_ROOT, "ooyala_embedded_video.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("#embed_pos1", u"""Jennifer Lawrence perd sa robe !""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("http://player.ooyala.com/iframe.html#ec=t4YWF0ODq-F_xnDy9kb41w3bZnN8kN4Y&pbid=NDcyOWI0M2YyMDdkN2YwODU5Mzc5MDUz", u"""http://player.ooyala.com/iframe.html#ec=t4YWF0ODq-F_xnDy9kb41w3bZnN8kN4Y&pbid=NDcyOWI0M2YyMDdkN2YwODU5Mzc5MDUz""", set(['video', 'external', 'embedded'])),
                make_tagged_url("http://galeries.dhnet.be/album/people/jenniferlawrence/8.jpg/", u"""Les photos de l'incident !""", set(['bottom box', 'internal', 'image gallery'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_plaintext_links(self):
        """ dhnet parser can extract embedded plaintext links (yeah, wtf, exactly)"""
        with open(os.path.join(DATA_ROOT, "embedded_plaintext_links.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("#embed_pos1", u"""SONDAGES: votre avis sur les principales mesures prises par le gouvernement""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos2", u"""Dix centimes en plus par paquet de cigarettes !""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("http://www.dhnet.be/infos/belgique/article/388448/sondages-votre-avis-sur-les-principales-mesures-prises-par-le-gouvernement.html", u"""http://www.dhnet.be/infos/belgique/article/388448/sondages-votre-avis-sur-les-principales-mesures-prises-par-le-gouvernement.html""", set(['plaintext', 'internal', 'embedded'])),
                make_tagged_url("http://www.dhnet.be/infos/economie/article/388380/dix-centimes-en-plus-par-paquet-de-cigarettes.html", u"""http://www.dhnet.be/infos/economie/article/388380/dix-centimes-en-plus-par-paquet-de-cigarettes.html""", set(['plaintext', 'internal', 'embedded'])),
                make_tagged_url("/infos/belgique/article/388496/energie-60-euros-d-economie-sur-votre-facture.html", u"""Energie: 60 euros d'économie sur votre facture ?""", set(['bottom box', 'internal'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)



    def test_embedded_tweet_bottom(self):
        """ dhnet parser can extract rendered embedded tweets at the bottom of articles"""
        with open(os.path.join(DATA_ROOT, "embedded_tweet_bottom.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://galeries.dhnet.be/album/cinema/magritte_2013/", u"""Les Magritte en photos""", set(['sidebar box', 'internal', 'image gallery'])),
                make_tagged_url("http://www.cinebel.be/fr", u"""Toute l'actu cinéma sur Cinebel""", set(['sidebar box', 'external', 'same owner'])),
                make_tagged_url("#embed_pos1", u"""Revivez la cérémonie sur le Twitter d'Alain Lorfèvre""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("https://twitter.com/ALorfevre", u"""Tweets de @ALorfevre""", set(['tweet', 'external', 'embedded'])),
                make_tagged_url("/cine-tele/cinema/article/423464/lafosse-et-gourmet-se-mefier-du-piege-du-communautarisme-dans-le-cinema.html", u'''Lafosse et Gourmet: "Se méfier du piège du communautarisme dans le cinéma"''', set(['bottom box', 'internal'])),
                make_tagged_url("/people/cinema/article/423544/jamel-un-president-anormal.html", u"""Jamel, un président anormal""", set(['bottom box', 'internal'])),
                make_tagged_url("http://www.cinebel.be/fr", u"""Toute l'actu cinéma sur Cinebel""", set(['bottom box', 'external', 'same owner'])),
                make_tagged_url("http://galeries.dhnet.be/album/cinema/magritte_2013/", u"""Les Magritte en photos""", set(['bottom box', 'internal', 'image gallery'])),
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

    def test_youtube_video(self):
        """ dhnet parser can extract an embedded youtube video"""
        with open(os.path.join(DATA_ROOT, "youtube_video.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("www.police.be", u"""www.police.be""", set(['plaintext', 'external', 'in text'])),
                make_tagged_url("#embed_pos1", u"""La vidéo de l'agression à Anderlecht""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("http://www.youtube.com/v/ZI_dpfd6LMw?version=3&feature=player_detailpage", u"""http://www.youtube.com/v/ZI_dpfd6LMw?version=3&feature=player_detailpage""", set(['video', 'external', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_vtm_video(self):
        """ dhnet parser can extract an embedded VTM video"""
        with open(os.path.join(DATA_ROOT, "vtm_video.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("#embed_pos2", u"""Le lancer de chatons de Jan Fabre""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos1", u"""La réaction de Jan Fabre""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("http://flvpd.vtm.be/videocms/nieuws/2012/10/26/201210261923056010032016057005056B763420000007108B00000D0F002641.mp4", u"""http://flvpd.vtm.be/videocms/nieuws/2012/10/26/201210261923056010032016057005056B763420000007108B00000D0F002641.mp4""", set(['video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=b4968b239e7s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("/infos/belgique/article/413486/jan-fabre-le-lanceur-de-chats-n-a-pas-depose-plainte.html", u"""Jan Fabre, le lanceur de chats, n'a pas déposé plainte""", set(['bottom box', 'internal'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_video_melty(self):
        """ dhnet parser can extract an embedded Meltybuzz video"""
        with open(os.path.join(DATA_ROOT, "video_melty.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("#embed_pos1", u"""Voir Anakin, le félidé aux deux pattes avant""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("http://www.meltybuzz.fr/anakin-le-chat-a-deux-pattes-qui-se-porte-tres-bien-video-a115745.html", u"""Anakin, le chat à deux pattes qui se porte très bien (vidéo) sur meltybuzz.fr""", set(['video', 'external', 'embedded'])),
                make_tagged_url("/regions/societe/article/400152/sauvetage-de-chaton.html", u"""Sauvetage de chaton""", set(['bottom box', 'internal'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)
     
    def test_video_divertissante(self):
        """ dhnet parser can extract an embedded video from 'DIVERTISSONSNOUS.COM' (how entertaining)"""
        with open(os.path.join(DATA_ROOT, "video_divertissante.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("#embed_pos1", u"""Vidéo : Le brinicle ou doigt glacé de la mort, filmé pour la première fois""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("http://www.divertissonsnous.com/2011/11/26/le-brinicle-ou-doigt-glace-de-la-mort/", u"""Le brinicle ou doigt glacé de la mort""", set(['video', 'external', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)
    
    def test_embedded_stuff_frenzy(self):
        """ dhnet parser can extract many different embedded things"""
        with open(os.path.join(DATA_ROOT, "embedded_stuff_frenzy.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("/infos/monde/article/389533/toulouse-un-groupe-lie-a-al-qaida-revendique-la-tuerie.html", u"""Toulouse: un groupe lié à Al-Qaïda revendique la tuerie""", set(['internal', 'sidebar box'])),
                make_tagged_url("/infos/monde/article/389441/merah-avait-sejourne-dans-un-hopital-psychiatrique.html", u"""Merah avait séjourné dans un hôpital psychiatrique""", set(['internal', 'sidebar box'])),
                make_tagged_url("/infos/monde/article/389527/toulouse-une-fan-page-a-la-gloire-de-merah-sur-facebook.html", u"""Toulouse: une fan page à la gloire de Merah sur Facebook""", set(['internal', 'sidebar box'])),
                make_tagged_url("#embed_pos1", u"""Revivez l'assaut minute par minute""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos4", u"""Merah: le film de la nuit""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos2", u"""Vidéo: les images de Mohamed Merah, sur France 2""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("http://www.coveritlive.com/index2.php/option=com_altcaster/task=viewaltcast/altcast_code=7d2559d5e8/height=850/width=470", u"""http://www.coveritlive.com/index2.php/option=com_altcaster/task=viewaltcast/altcast_code=7d2559d5e8/height=850/width=470""", set(['embedded', 'external', 'iframe'])),
                make_tagged_url("http://www.twitvid.com/embed.php?guid=IWICN&autoplay=0", u"""http://www.twitvid.com/embed.php?guid=IWICN&autoplay=0""", set(['embedded', 'external', 'iframe'])),
                make_tagged_url("http://link.brightcove.com/services/player/bcpid1027556707001?bctid=1521783409001", u"""http://link.brightcove.com/services/player/bcpid1027556707001?bctid=1521783409001""", set(['video', 'external', 'embedded'])),
                make_tagged_url("http://api.dmcloud.net/player/embed/4e7343f894a6f677b10006b4/4f6acb3af325e148e900004a/c63cc0d05ba3464890178207f4f2d9a7?wmode=transparent", u"""http://api.dmcloud.net/player/embed/4e7343f894a6f677b10006b4/4f6acb3af325e148e900004a/c63cc0d05ba3464890178207f4f2d9a7?wmode=transparent""", set(['embedded', 'external', 'iframe'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=47584d06414s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("/infos/monde/article/389281/toulouse-l-enquete-avance-a-grands-pas.html", u'''Toulouse : "L'enquête avance à grands pas"''', set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389276/toulouse-la-piste-des-militaires-neo-nazis-n-est-plus-privilegiee.html", u'''Toulouse : la piste des militaires néo-nazis n'est "plus privilégiée"''', set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389272/tuerie-les-candidats-doivent-ils-suspendre-leur-campagne.html", u"""Tuerie, les candidats doivent-ils suspendre leur campagne ?""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389381/toulouse-tous-les-secrets-de-l-enquete.html", u"""Toulouse : tous les secrets de l'enquête""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389382/toulouse-le-suspect-avait-deja-ete-arrete-en-afghanistan.html", u"""Toulouse : le suspect avait déjà été arrêté, en Afghanistan""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389385/les-parents-d-eleves-de-l-ecole-d-ozar-hatorah-attendent-la-delivrance.html", u'''Les parents d'élèves de l'école d'Ozar Hatorah attendent "la délivrance"''', set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389393/israel-enterre-ses-victimes-de-toulouse.html", u"""Israël enterre ses victimes de Toulouse""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389408/qui-sont-les-jihadistes-francais.html", u"""Qui sont les jihadistes français?""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389441/merah-avait-sejourne-dans-un-hopital-psychiatrique.html", u"""Merah avait séjourné dans un hôpital psychiatrique""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389507/sarkozy-veut-des-mesures-penales-pour-lutter-contre-les-extremismes.html", u"""Sarkozy veut des mesures pénales pour lutter contre les extrémismes""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389527/toulouse-une-fan-page-a-la-gloire-de-merah-sur-facebook.html", u"""Toulouse: une fan page à la gloire de Merah sur Facebook""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389533/toulouse-un-groupe-lie-a-al-qaida-revendique-la-tuerie.html", u"""Toulouse: un groupe lié à Al-Qaïda revendique la tuerie""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389539/la-video-de-l-assaut-contre-mohammed-merah.html", u"""La vidéo de  l'assaut contre Mohammed Merah""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389554/al-qaida-l-appelait-youssef-le-francais.html", u"""Al-Qaida l'appelait Youssef le Français""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389603/qui-est-vraiment-mohamed-merah.html", u"""Qui est vraiment  Mohamed Merah ?""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/389629/toulouse-pouvoir-et-police-presentent-leur-defense-face-aux-critiques.html", u"""Toulouse : pouvoir et police présentent leur défense face aux critiques""", set(['bottom box', 'internal'])),
                make_tagged_url("/infos/monde/article/394230/affaire-merah-le-pere-d-un-soldat-tue-porte-plainte-contre-sarkozy.html", u"""Affaire Merah: le père d'un soldat tué porte plainte contre Sarkozy""", set(['bottom box', 'internal'])),
                make_tagged_url("http://galeries.dhnet.be/album/actumonde/raidtoulouse/", u"""L'opération en images""", set(['bottom box', 'internal', 'image gallery'])),
                make_tagged_url("http://podcast.dhnet.be/articles/audio_dh_389327_1332310479.mp3", u"""Ecoutez Claude Guéant, ministre français de l'Intérieur (Europe 1 et Twizz Radio)""", set(['internal', 'sidebar box', 'embedded', 'audio', 'podcast'])),
                make_tagged_url("http://podcast.dhnet.be/articles/audio_dh_389327_1332327971.mp3", u"""Ecoutez la journalsite (Ebba Kalondo) qui a reçu un appel du suspect (micro de Twizz et Europe 1)""", set(['internal', 'sidebar box', 'podcast', 'embedded', 'audio'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)
   
    def test_links_embedded_canalplus(self):
        """ dhnet parser can extract link to embedded canalplus.fr/itele.fr videos"""
        with open(os.path.join(DATA_ROOT, "links_embedded_canalplus.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("#embed_pos1", u"""Voir l'interview de Souad Merah""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("http://www.itele.fr/redirect?vid=767341&sc_cmpid=SharePlayerEmbed", u"""Témoignage exclusif de Souad Merah - 20/11/12 à 11:16""", set(['video', 'external', 'embedded'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_vuvox_collage(self):
        """ dhnet parser can extract weird multimedia thingy"""
        with open(os.path.join(DATA_ROOT, "vuvox_collage.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("#embed_pos1", u"""Vidéo : Comment prendre des photos au fond de la piscine ?""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("/sports/jo-2012/article/404241/le-relais-4x400-se-fait-peur-mais-va-en-finale.html", u"""Le relais 4X400 se fait peur mais va en finale""", set(['internal', 'sidebar box'])),
                make_tagged_url("/sports/jo-2012/article/404250/les-footballeuses-nippones-vont-elles-gagner-la-classe-affaires.html", u"""Les footballeuses nippones vont-elles gagner la classe affaires ?""", set(['internal', 'sidebar box'])),
                make_tagged_url("/sports/jo-2012/article/404247/usa-argentine-et-espagne-russie-en-demi-finales.html", u"""USA-Argentine et Espagne-Russie en demi-finales""", set(['internal', 'sidebar box'])),
                make_tagged_url("/sports/jo-2012/article/404242/notre-succes-est-du-a-nos-bikinis.html", u"""Notre succès est dû à nos bikinis""", set(['internal', 'sidebar box'])),
                make_tagged_url("/sports/jo-2012/article/404188/une-beaute-haut-perchee.html", u"""Une beauté haut perchée""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.vuvox.com/collage_express/collage.swf?collageID=05bf5f41ae", u"""Vidéo : Comment prendre des photos au fond de la piscine ?""", set(['external', 'embedded'])),
                make_tagged_url("/sports/jo-2012/article/404241/le-relais-4x400-se-fait-peur-mais-va-en-finale.html", u"""Le relais 4X400 se fait peur mais va en finale""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/jo-2012/article/404250/les-footballeuses-nippones-vont-elles-gagner-la-classe-affaires.html", u"""Les footballeuses nippones vont-elles gagner la classe affaires ?""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/jo-2012/article/404247/usa-argentine-et-espagne-russie-en-demi-finales.html", u"""USA-Argentine et Espagne-Russie en demi-finales""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/jo-2012/article/404242/notre-succes-est-du-a-nos-bikinis.html", u"""Notre succès est dû à nos bikinis""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/jo-2012/article/404188/une-beaute-haut-perchee.html", u"""Une beauté haut perchée""", set(['bottom box', 'internal'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_soundcloud(self):
        """ dhnet parser can extract embedded soundcloud"""
        with open(os.path.join(DATA_ROOT, "soundcloud.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("#embed_pos2", u"""Regardez la vidéo de Véronique De Keyser""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("/infos/monde/article/386553/les-usa-offrent-un-soutien-appuye-au-conseil-national-syrien.html", u"""Les USA offrent un soutien appuyé au Conseil national syrien""", set(['internal', 'sidebar box'])),
                make_tagged_url("https://player.soundcloud.com/player.swf?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F37663533&show_comments=true&auto_play=false&color=a900ff", u"""https://player.soundcloud.com/player.swf?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F37663533&show_comments=true&auto_play=false&color=a900ff""", set(['audio', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=7f379495096e&configKey=&suffix=&sig=08f4ba2000es&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("/infos/monde/article/386553/les-usa-offrent-un-soutien-appuye-au-conseil-national-syrien.html", u"""Les USA offrent un soutien appuyé au Conseil national syrien""", set(['bottom box', 'internal'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_dataviz(self):
        """ dhnet parser can extract link to embedded dataviz from visual.ly"""
        with open(os.path.join(DATA_ROOT, "embedded_dataviz.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("visual.ly", u"""visual.ly""", set(['plaintext', 'external', 'in text'])),
                make_tagged_url("#embed_pos1", u"""La... nymphographie de James Bond !""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("/cine-tele/cinema/article/414582/le-nouveau-james-bond-regne-sur-le-box-office-nord-americain.html", u"""Le nouveau James Bond règne sur le box-office nord-américain""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://babescm.blogs.dhnet.be/archive/2012/10/25/son-nom-est-marlohe-berenice-marlohe.html", u"""Son nom est Marlohe, Bérénice Marlohe""", set(['internal', 'sidebar box', 'internal site'])),
                make_tagged_url("http://www.cinebel.be/fr/", u"""Cinébel, notre site 100% cinéma !""", set(['sidebar box', 'external', 'same owner'])),
                make_tagged_url("http://visual.ly/james-bond-nymphographic", u"""http://visual.ly/james-bond-nymphographic""", set(['external', 'embedded'])),
                make_tagged_url("/cine-tele/cinema/article/414582/le-nouveau-james-bond-regne-sur-le-box-office-nord-americain.html", u"""Le nouveau James Bond règne sur le box-office nord-américain""", set(['bottom box', 'internal'])),
                make_tagged_url("http://www.cinebel.be/fr/", u"""Cinébel, notre site 100% cinéma !""", set(['bottom box', 'external', 'same owner'])),
                make_tagged_url("http://babescm.blogs.dhnet.be/archive/2012/10/25/son-nom-est-marlohe-berenice-marlohe.html", u"""Son nom est Marlohe, Bérénice Marlohe""", set(['bottom box', 'internal', 'internal site'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)


    def test_twizz_stream(self):
        """ dhnet parser can extract embedded twizz streaming and many other links"""
        with open(os.path.join(DATA_ROOT, "twizz_stream.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("#embed_pos1", u'''Chattez en direct avec les flingueurs de Twizz radio qui reviendront sur le sujet entre 17h et 18h''', set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("/sports/cyclisme/article/412016/gesink-rabobank-c-est-nous-qui-payons-la-note.html", u'''Gesink (Rabobank): "c'est nous qui payons la note"''', set(['internal', 'sidebar box'])),
                make_tagged_url("/sports/cyclisme/article/411925/rabobank-suspend-carlos-barredo.html", u'''Rabobank suspend Carlos Barredo''', set(['internal', 'sidebar box'])),
                make_tagged_url("/sports/cyclisme/article/411910/vantomme-quitte-katusha-pour-rejoindre-landbouwkrediet-euphony.html", u'''Vantomme quitte Katusha pour rejoindre Landbouwkrediet-Euphony''', set(['internal', 'sidebar box'])),
                make_tagged_url("/sports/cyclisme/article/411893/le-dr-ferrari-reseau-de-dopage-blanchiment-d-argent-et-evasion-fiscale.html", u'''Le Dr Ferrari: réseau de dopage, blanchiment d'argent et évasion fiscale''', set(['internal', 'sidebar box'])),
                make_tagged_url("http://embed.scribblelive.com/Embed/v5.aspx?Id=65567&ThemeId=7116", u'''http://embed.scribblelive.com/Embed/v5.aspx?Id=65567&ThemeId=7116''', set(['embedded', 'external', 'iframe'])),
                make_tagged_url("http://vipicecast.yacast.net/twizz", u"""http://vipicecast.yacast.net/twizz""", set(['audio', 'external', 'embedded'])),
                make_tagged_url("/sports/cyclisme/article/411963/cavendish-boonen-tandem-de-choc-au-tour.html", u"""Cavendish-Boonen,  tandem de choc au Tour""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/cyclisme/article/411809/apres-nike-et-anheuser-busch-trek-quitte-aussi-le-navire-armstrong.html", u"""Après Nike et Anheuser-Busch, Trek quitte aussi le navire Armstrong""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/cyclisme/article/411912/cavendish-rejoint-omega-pharma-quickstep.html", u"""Cavendish rejoint Omega Pharma-Quick.Step""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/cyclisme/article/411929/cavendish-je-suis-content-de-rouler-pour-omega-pharma-quickstep.html", u'''Cavendish: "Je suis content de rouler pour Omega Pharma-Quick.Step"''', set(['bottom box', 'internal'])),
                make_tagged_url("/sports/cyclisme/article/411928/guercilena-succede-a-bruyneel-chez-radioshack.html", u"""Guercilena succède à Bruyneel chez RadioShack""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/cyclisme/article/411865/hein-verbruggen-continue-a-soutenir-lance-armstrong.html", u"""Hein Verbruggen continue à soutenir Lance Armstrong""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/cyclisme/article/411893/le-dr-ferrari-reseau-de-dopage-blanchiment-d-argent-et-evasion-fiscale.html", u"""Le Dr Ferrari: réseau de dopage, blanchiment d'argent et évasion fiscale""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/cyclisme/article/411925/rabobank-suspend-carlos-barredo.html", u"""Rabobank suspend Carlos Barredo""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/cyclisme/article/411910/vantomme-quitte-katusha-pour-rejoindre-landbouwkrediet-euphony.html", u"""Vantomme quitte Katusha pour rejoindre Landbouwkrediet-Euphony""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/cyclisme/article/412016/gesink-rabobank-c-est-nous-qui-payons-la-note.html", u'''Gesink (Rabobank): "c'est nous qui payons la note"''', set(['bottom box', 'internal'])),
                make_tagged_url("/sports/cyclisme/article/412040/l-uci-se-prononcera-lundi-sur-le-dossier-armstrong.html", u"""L'UCI se prononcera lundi sur le dossier Armstrong""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/cyclisme/article/412044/la-loterie-nationale-poursuit-son-partenariat-dans-le-cyclisme.html", u"""La Loterie nationale poursuit son partenariat dans le cyclisme""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/cyclisme/article/412045/decouverte-de-preuves-reliant-ferrari-a-menchov-et-scarponi.html", u"""Découverte de preuves reliant Ferrari à Menchov et Scarponi""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/cyclisme/article/412132/jamais-le-test-d-armstrong-de-2001-ne-serait-positif.html", u""""Jamais" le test d'Armstrong de 2001 ne serait positif""", set(['bottom box', 'internal'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_tweet_with_emoji(self):
        """ dhnet parser does not choke when fallen popstars use emoji in their tweets, in a desperate attempt to reconnect with their long gone fanbase"""
        with open(os.path.join(DATA_ROOT, "links_tweet_with_emoji.html")) as f:
            article, raw_html = dhnet.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("https://twitter.com/mellealizee/status/275978005447315456", u"""https://twitter.com/mellealizee/status/275978005447315456""", set(['tweet', 'embedded media', 'external'])),
                make_tagged_url("http://babescm.blogs.dhnet.be/", u"""Les filles les plus sexy sur notre blog Babes""", set(['internal', 'sidebar box', 'internal site'])),
                make_tagged_url("http://babescm.blogs.dhnet.be/", u"""Les filles les plus sexy sur notre blog Babes""", set(['bottom box', 'internal', 'internal site'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)
