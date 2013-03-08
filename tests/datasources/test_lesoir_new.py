# coding=utf-8
"""
Link extraction test suite for lesoir_new.py
"""

import os
from nose.tools import eq_

from csxj.common.tagging import make_tagged_url
from csxj.datasources import lesoir_new

from csxj_test_tools import assert_taggedURLs_equals

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', lesoir_new.SOURCE_NAME)

class TestLeSoirNewContentExtraction(object):
    def test_intro_type1(self):
        """ lesoir_new can extract intro"""
        with open(os.path.join(DATA_ROOT, "intro_type1.html")) as f:
            article, raw_html = lesoir_new.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.lacapitale.be/674531/article/actualite/politique/2013-03-01/didier-reynders-veut-mettre-nos-imams-sous-controle", u"""dans un entretien donné aux journaux SudPresse""", set(['same owner', 'external', 'in text'])),
                make_tagged_url("http://www.lacapitale.be/674531/article/actualite/politique/2013-03-01/didier-reynders-veut-mettre-nos-imams-sous-controle", u"""Didier Reynders veut mettre nos imams sous contrôle (SudPresse)""", set(['sidebar box', 'external', 'same owner'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_intro_type2(self):
        """ lesoir_new can extract other type of intro"""
        with open(os.path.join(DATA_ROOT, "intro_type2.html")) as f:
            article, raw_html = lesoir_new.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.lesoir.be/191377/article/culture/cinema/2013-02-16/berlinale-%C2%ABthe-broken-circle-breakdown%C2%BB-remporte-prix-du-public", u"""Berlinale: «The Broken Circle Breakdown» remporte le prix du Public""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.youtube.com/watch?v=ZtoCo9pJ2yU", u"""http://www.youtube.com/watch?v=ZtoCo9pJ2yU""", set(['video', 'external', 'embedded', 'top box'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)



class TestLaSoirNewLinkExtraction(object):
    def test_same_owner_tagging(self):
        """ lesoir_new parser correctly tags 'same owner' links """
        with open(os.path.join(DATA_ROOT, "same_owner_tagging.html")) as f:
            article, raw_html = lesoir_new.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://mad.lesoir.be/musiques/pop-rock/concert/61705-pias-nites/", u"""http://mad.lesoir.be/musiques/pop-rock/concert/61705-pias-nites/""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/event/235717-moi-je-crois-pas/", u"""http://mad.lesoir.be/event/235717-moi-je-crois-pas/""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/event/221582-un-coup-de-don/", u"""http://mad.lesoir.be/event/221582-un-coup-de-don/""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/musiques/pop-rock/concert/61620-concours-circuit/", u"""http://mad.lesoir.be/musiques/pop-rock/concert/61620-concours-circuit/""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/musiques/classique/concert/61765-ictus/", u"""http://mad.lesoir.be/musiques/classique/concert/61765-ictus/""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/scenes/24179-purgatoire/", u"""http://mad.lesoir.be/scenes/24179-purgatoire/""", set(['internal site', 'in text'])),
                make_tagged_url("http://www.facebook.com/events/133992883421165/", u"""http://www.facebook.com/events/133992883421165/""", set(['external', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/musiques/pop-rock/concert/61710-john-mayall/", u"""http://mad.lesoir.be/musiques/pop-rock/concert/61710-john-mayall/""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/musiques/jazz/concert/61720-toots-thielemans/", u"""http://mad.lesoir.be/musiques/jazz/concert/61720-toots-thielemans/""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/event/230133-/", u"""http://mad.lesoir.be/event/230133-/""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/musiques/classique/concert/61764-onb-boreyko-kremer/", u"""http://mad.lesoir.be/musiques/classique/concert/61764-onb-boreyko-kremer/""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/musiques/classique/concert/61763-samouil-mengova/", u"""http://mad.lesoir.be/musiques/classique/concert/61763-samouil-mengova/""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/event/236542-ensemblematic/", u"""http://mad.lesoir.be/event/236542-ensemblematic/""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/arts/61587-la-mediatine/", u"""http://mad.lesoir.be/arts/61587-la-mediatine/""", set(['internal site', 'in text'])),
                make_tagged_url("http://www.netevents.be/fr/bourse-brocante/239087/The-Micro-Marche-Christmas-Special-III/", u"""http://www.netevents.be/fr/bourse-brocante/239087/The-Micro-Marche-Chris...""", set(['same owner', 'external', 'in text'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)



    def test_in_text_and_sidebar(self):
        """ lesoir_new parser correctly tags in-text and sidebar """
        with open(os.path.join(DATA_ROOT, "in_text_and_sidebar.html")) as f:
            article, raw_html = lesoir_new.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url(u"http://www.lesoir.be/159908/article/actualite/regions/bruxelles/2013-01-12/didier-reynders-est-nouveau-patron-du-mr-bruxellois", u"""élu président de la Régionale bruxelloise du MR""", set(['internal', 'in text'])),
                make_tagged_url(u"http://www.lesoir.be/156156/article/actualite/belgique/crise-politique/2013-01-11/belgique-%C3%A0-trois-r%C3%A9gions-kris-peeters-s%E2%80%99y-r%C3%A9sout", u"""dans l’entretien qu’il nous a accordé""", set(['internal', 'in text'])),
                make_tagged_url(u"/159908/article/actualite/regions/bruxelles/2013-01-12/didier-reynders-est-nouveau-patron-du-mr-bruxellois", u"""Didier Reynders est le nouveau patron du MR bruxellois""", set(['internal', 'sidebar box'])),
                make_tagged_url(u"/156156/article/actualite/belgique/crise-politique/2013-01-11/belgique-à-trois-régions-kris-peeters-s’y-résout", u"""La Belgique à trois Régions ? Kris Peeters s’y résout""", set(['internal', 'sidebar box'])),
                make_tagged_url(u"http://https://twitter.com/dreynders", u"""Le compte Twitter de Didier Reynders""", set(['sidebar box', 'external'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_scribble_live(self):
        """ lesoir_new parser correctly extracts and tags an embedded scribble live """
        with open(os.path.join(DATA_ROOT, "embedded_scribble_live.html")) as f:
            article, raw_html = lesoir_new.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://football.lesoir.be/jupiler-pro-league/resultats", u"""Tous les résultats et classements""", set(['internal', 'sidebar box', 'internal site'])),
                make_tagged_url("http://embed.scribblelive.com/Embed/v5.aspx?Id=86477&ThemeId=7346", u"""http://embed.scribblelive.com/Embed/v5.aspx?Id=86477&ThemeId=7346""", set(['iframe', 'external', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_kplayer_without_title(self):
        with open(os.path.join(DATA_ROOT, "kplayer_without_title.html")) as f:
            article, raw_html = lesoir_new.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://soirmag.lesoir.be/search/node/gandolfi", u"""Dans toutes ses interviews""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://soirmag.lesoir.be/search/node/gandolfi", u"""Les articles sur Barbara Gandolfi sur SoirMag""", set(['internal', 'sidebar box', 'internal site'])),
                make_tagged_url("http://sll.kewego.com/swf/p3/epix.swf?language_code=fr&playerKey=5ff3260def2a&skinKey=6624e00d250s&sig=d09800d9f8as&autostart=false&advertise=true", u"""__NO_TITLE__""", set(['kplayer', 'external', 'embedded', 'top box'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_ustream(self):
        with open(os.path.join(DATA_ROOT, "embedded_ustream.html")) as f:
            article, raw_html = lesoir_new.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.lesoir.be/187345/article/economie/2013-02-11/gaz-schiste-menace-pour-belgique", u"""notre dossier sur le gaz de schiste""", set(['internal', 'in text'])),
                make_tagged_url("http://sll.kewego.com/swf/p3/epix.swf?language_code=fr&playerKey=5ff3260def2a&skinKey=6624e00d250s&sig=ed3b67b4053s&autostart=false&advertise=true", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded', 'top box'])),
                make_tagged_url("__NO_URL__", u"""__NO_TITLE__""", set(['video', u'unfinished', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_dailymotion_video(self):
        with open(os.path.join(DATA_ROOT, "embedded_dailymotion_video.html")) as f:
            article, raw_html = lesoir_new.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url(u"/156026/article/actualite/monde/2013-01-11/l-etat-d-urgence-été-décrété-au-mali", u"""L'Etat d'urgence a été décrété au Mali""", set(['internal', 'sidebar box'])),
                make_tagged_url(u"/159828/article/actualite/monde/2013-01-12/raid-raté-en-somalie-confusion-autour-l-otage-français", u"""Raid raté en Somalie : confusion autour de l'otage français""", set(['internal', 'sidebar box'])),
                make_tagged_url(u"/159960/article/actualite/france/2013-01-12/mali-l’intégralité-du-discours-françois-hollande", u"""Mali : l’intégralité du discours de François Hollande""", set(['internal', 'sidebar box'])),
                make_tagged_url(u"/tag/mali", u"""Mali""", set(['internal', 'keyword'])),
                make_tagged_url(u"http://www.dailymotion.com/embed/video/xwpmlt", u"""http://www.dailymotion.com/embed/video/xwpmlt""", set(['video', 'external', 'embedded', 'top box'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_rtl(self):
        with open(os.path.join(DATA_ROOT, "embedded_rtl.html")) as f:
            article, raw_html = lesoir_new.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.lesoir.be/191955/article/actualite/monde/2013-02-18/belgique-maintient-son-engagement-au-mali", u"""La Belgique maintient son engagement au Mali""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.lesoir.be/191635/article/actualite/monde/2013-02-17/arm%C3%A9e-malienne-quelle-contribution-belge", u"""Armée malienne: quelle contribution belge?""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.lesoir.be/191734/article/actualite/belgique/crise-politique/2013-02-17/r%C3%A9forme-l%E2%80%99etat-vers-un-accord-francophone", u"""Réforme de l’Etat : vers un accord francophone""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.lesoir.be/191090/article/actualite/belgique/2013-02-16/s%C3%BBret%C3%A9-l%E2%80%99%C3%A9tat-bart-debie-menti-sur-sa-fonction-%C2%ABtaupe%C2%BB", u"""Sûreté de l’État: Bart Debie a menti sur sa fonction de «taupe»""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.lesoir.be/188948/article/actualite/belgique/2013-02-13/s%C3%BBret%C3%A9-l%E2%80%99etat-victime-man%C5%93uvres-d%C3%A9stabilisation", u"""La Sûreté de l’Etat victime de manœuvres de déstabilisation?""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.rtl.be/videobelrtl/page/syndication/913.aspx?videoid=433472&key=bcef71c1-0360-4bc5-b78e-4d75d397ecfa", u"""La vidéo""", set(['sidebar box', 'external', 'same owner'])),
                make_tagged_url("http://videos.lesoir.be/video/236054e7441s.html", u"""Le 11h02 : l'Etat a plus que jamais besoin de sa Sûreté""", set(['internal', 'sidebar box', 'internal site'])),
                make_tagged_url("http://www.rtl.be/videos/page/rtl-video-en-embed/640.aspx?VideoID=433472&key=bcef71c1-0360-4bc5-b78e-4d75d397ecfa", u"""http://www.rtl.be/videos/page/rtl-video-en-embed/640.aspx?VideoID=433472&key=bcef71c1-0360-4bc5-b78e-4d75d397ecfa""", set(['same owner', 'video', 'external', 'embedded', 'top box'])),
                make_tagged_url("http://sll.kewego.com/swf/p3/epix.swf?language_code=fr&playerKey=5ff3260def2a&skinKey=6624e00d250s&sig=236054e7441s&autostart=false&advertise=true", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded', 'top box'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)



