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

    def test_loads_of_embedded_stuff_and_pdf_newspaper(self):
        with open(os.path.join(DATA_ROOT, "loads_of_embedded_stuff_and_pdf_newspaper.html")) as f:
            article, raw_html = lesoir_new.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://pdf.lesoir.be", u"""Notre dossier complet pp. 2 et 3 dans Le Soir en PDF""", set(['internal', 'pdf newspaper', 'in text'])),
                make_tagged_url("http://www.lesoir.be/194330/article/actualite/belgique/2013-02-20/syndicats-ont-ils-raison-manifester", u"""Les syndicats ont-ils raison de manifester ? (sondage)""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.lesoir.be/193899/article/actualite/belgique/2013-02-20/manif-jeudi-gros-points-noirs-redout%C3%A9s-partout-en-belgique", u"""Manif de jeudi: de gros points noirs redoutés partout en Belgique""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.lesoir.be/194401/article/debats/editos/2013-02-21/crise-vaut-bien-une-manif-mais-pas-une-fuite", u"""L'édito - La crise vaut bien une manif, mais pas une fuite""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.lesoir.be/193262/article/debats/chats/2013-02-19/manif-ce-jeudi-%C2%ABun-rapport-forces%C2%BB", u"""Manif de ce jeudi: «Un rapport de forces»""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://videos.lesoir.be/video/076717938cas.html", u'''Le 11h02 : "Un rapport de force"''', set(['internal', 'sidebar box', 'internal site'])),
                make_tagged_url("http://sll.kewego.com/swf/p3/epix.swf?language_code=fr&playerKey=5ff3260def2a&skinKey=6624e00d250s&sig=076717938cas&autostart=false&advertise=true", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded', 'top box'])),
                make_tagged_url("http://maps.google.be/maps/ms?msid=209311417319162309079.0004d630121a53cbdf34c&msa=0&output=embed", u"""http://maps.google.be/maps/ms?msid=209311417319162309079.0004d630121a53cbdf34c&msa=0&output=embed""", set(['embedded', 'external', 'iframe', 'top box'])),
                make_tagged_url("http://player.qualifio.com/08/v1.cfm?id=D55B0593-5056-8040-9EBD-0632E0DED7C7&iframe=true", u"""http://player.qualifio.com/08/v1.cfm?id=D55B0593-5056-8040-9EBD-0632E0DED7C7&iframe=true""", set(['iframe', 'external', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)


    def test_link_in_intro(self):
        with open(os.path.join(DATA_ROOT, "link_in_intro.html")) as f:
            article, raw_html = lesoir_new.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.lesoir.be/95459/article/sports/football/2012-10-08/diables-lukaku-absent-contre-serbie-et-l%E2%80%99ecosse", u"""Diables : Lukaku absent contre la Serbie et l’Ecosse""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.lesoir.be/93314/article/sports/football/2012-10-04/serbie-belgique-pas-surprise-dans-s%C3%A9lection-des-diables", u"""Serbie-Belgique : pas de surprise dans la sélection des Diables""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.lesoir.be/95308/article/sports/football/2012-10-08/prestations-des-diables-%C3%A0-loupe", u"""Les prestations des Diables à la loupe""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.lesoir.be/archives?url=/sports/football/2012-10-03/les-diables-rouges-30e-au-classement-fifa-941023.php", u"""Les Diables Rouges 30e au classement FIFA""", set(['internal', 'sidebar box'])),
                make_tagged_url("/tag/diables-rouges", u"""diables rouges""", set(['internal', 'keyword'])),
                make_tagged_url("http://soundcloud.com/lesoir/sets/diables-rouges-mboyo-la-1", u"""L’analyse de Frédéric Larsimont""", set(['in intro', 'external'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_storify_top_box(self):
        with open(os.path.join(DATA_ROOT, "embedded_storify_top_box.html")) as f:
            article, raw_html = lesoir_new.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://storify.com/lesoir/conference-de-presse-de-l-eurogroupe-sur-le-me", u"""http://storify.com/lesoir/conference-de-presse-de-l-eurogroupe-sur-le-me""", set(['external', 'embedded', 'storify'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)




