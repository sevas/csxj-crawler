# coding=utf-8
"""
Link extraction test suite for lesoir.py
"""

import os
from nose.tools import eq_

from csxj.common.tagging import make_tagged_url
from csxj.datasources import lesoir

from csxj_test_tools import assert_taggedURLs_equals

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', 'lesoir')


class TestLesoirLinkExtraction(object):
    def test_same_owner_tagging(self):
        """ Lesoir parser correctly tags 'same owner' links """
        with open(os.path.join(DATA_ROOT, "same_owner_tagging.html")) as f:
            article, raw_html = lesoir.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.lafetefwb.be/", u"""Fête de la Fédération Wallonie-Bruxelles""", set(['web', 'sidebar box', 'external'])),
                make_tagged_url("http://www.netevents.be/fr/concert/232154/Rallye-Chantons-francais-/", u"""Rallye Chantons français""", set(['web', 'sidebar box', 'external', 'same owner'])),
                make_tagged_url("http://www.netevents.be/fr/soiree/232842/3-rd-Birthday-Weekend/", u"""Wood Audiorama""", set(['web', 'sidebar box', 'external', 'same owner'])),
                make_tagged_url("http://www.netevents.be/fr/loisirs/actualite/41766/Festival-de-la-Biere-Fantastique/", u"""Festival de la bière fantastique""", set(['web', 'sidebar box', 'external', 'same owner'])),
                make_tagged_url("http://www.citysonic.be/2012/speaker-lineup/sonic-kids-huy/", u"""Sonic Kids Huy""", set(['web', 'sidebar box', 'external'])),
                make_tagged_url("http://mad.lesoir.be/musiques/classique/concert/41853-coppola-quatuor-alfama/", u"""Coppola, Quatuor Alfama""", set(['to read', 'sidebar box', 'internal site'])),
                make_tagged_url("http://mad.lesoir.be/musiques/classique/concert/41852-oprl-arming/", u"""OPRL, Arming""", set(['to read', 'sidebar box', 'internal site'])),
                make_tagged_url("http://mad.lesoir.be/scenes/41717-multivers-agnes-limbos/", u"""Multivers : Agnès Limbos""", set(['to read', 'sidebar box', 'internal site'])),
                make_tagged_url("http://mad.lesoir.be/event/225465-ghost-road/", u"""Ghost Road""", set(['to read', 'sidebar box', 'internal site'])),
                make_tagged_url("http://mad.lesoir.be/scenes/41940-cirkopolis/", u"""Cirkopolis""", set(['to read', 'sidebar box', 'internal site'])),
                make_tagged_url("http://mad.lesoir.be/musiques/pop-rock/concert/41829-dead-can-dance/", u"""Dead Can Dance""", set(['to read', 'sidebar box', 'internal site'])),
                make_tagged_url("http://mad.lesoir.be/musiques/classique/concert/41858-sufi-night/", u"""Sufi Night""", set(['to read', 'sidebar box', 'internal site'])),
                make_tagged_url("http://mad.lesoir.be/musiques/pop-rock/concert/41828-fun-/", u"""Fun""", set(['to read', 'sidebar box', 'internal site'])),
                make_tagged_url("http://mad.lesoir.be/musiques/classique/concert/41856-festival-espana/", u"""Festival Espana""", set(['to read', 'sidebar box', 'internal site'])),
                make_tagged_url("http://www.lesoir.be/actualite/monde/2012-09-28/six-morts-dans-des-inondations-en-espagne-940394.php", u"""Six morts dans des inondations en Espagne""", set(['internal', 'sidebar box', 'internal site', 'recent'])),
                make_tagged_url("http://www.lesoir.be/actualite/sciences/2012-09-28/pesticides-une-evaluation-defaillante-940393.php", u"""Pesticides : une évaluation défaillante""", set(['internal', 'sidebar box', 'internal site', 'recent'])),
                make_tagged_url("http://portfolio.lesoir.be/main.php?g2_itemId=775179", u"""Les photos du concert pour la Fête de la Fédération Wallonie-Bruxelles""", set(['sidebar box', 'internal site', 'recent'])),
                make_tagged_url("http://www.lafetefwb.be/", u"""Fête de la Fédération Wallonie-Bruxelles""", set(['external', 'in text'])),
                make_tagged_url("http://www.netevents.be/fr/concert/232154/Rallye-Chantons-francais-/", u"""Rallye Chantons français""", set(['same owner', 'external', 'in text'])),
                make_tagged_url("http://www.netevents.be/fr/soiree/232842/3-rd-Birthday-Weekend/", u"""Wood Audiorama""", set(['same owner', 'external', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/musiques/classique/concert/41853-coppola-quatuor-alfama/", u"""Coppola, Quatuor Alfama""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/musiques/classique/concert/41852-oprl-arming/", u"""OPRL, Arming""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/scenes/41717-multivers-agnes-limbos/", u"""Multivers : Agnès Limbos""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/event/225465-ghost-road/", u"""Ghost Road""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/scenes/41940-cirkopolis/", u"""Cirkopolis""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/musiques/pop-rock/concert/41829-dead-can-dance/", u"""Dead Can Dance""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/musiques/classique/concert/41858-sufi-night/", u"""Sufi Night""", set(['internal site', 'in text'])),
                make_tagged_url("http://www.netevents.be/fr/loisirs/actualite/41766/Festival-de-la-Biere-Fantastique/", u"""Festival de la bière fantastique""", set(['same owner', 'external', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/musiques/pop-rock/concert/41828-fun-/", u"""Fun""", set(['internal site', 'in text'])),
                make_tagged_url("http://mad.lesoir.be/musiques/classique/concert/41856-festival-espana/", u"""Festival Espana""", set(['internal site', 'in text'])),
                make_tagged_url("http://www.citysonic.be/2012/speaker-lineup/sonic-kids-huy/", u"""Sonic Kids Huy""", set(['external', 'in text'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_ignore_embedded_images(self):
        """ lesoir parser ignores links that point to an embedded image."""
        with open(os.path.join(DATA_ROOT, "links_ignore_embedded_images.html")) as f:
            article, raw_html = lesoir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.lesoir.be/sports/basket/2012-05-11/championnat-ostende-rafle-la-pole-juste-avant-les-playoffs-915188.php", u"""Championnat : Ostende rafle la pole juste avant les playoffs""", set(['internal', 'sidebar box', 'internal site', 'recent'])),
                make_tagged_url("http://www.lesoir.be/sports/football/2012-05-11/kompany-elu-joueur-de-la-saison-en-angleterre-915181.php", u"""Kompany élu Joueur de la saison en Angleterre""", set(['internal', 'sidebar box', 'internal site', 'recent'])),
                make_tagged_url("http://www.lesoir.be/actualite/belgique/2012-05-11/collision-de-godinne-les-trains-n-etaient-pas-equipes-du-systeme-europeen-de-securite-915177.php", u"""Collision de Godinne : les trains nétaient pas équipés du système européen de sécurité""", set(['internal', 'sidebar box', 'internal site', 'recent'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_overload(self):
        """ lesoir parser can handle a page with a lot of various links
        """
        with open(os.path.join(DATA_ROOT, "links_overload.html")) as f:
            article, raw_html = lesoir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://bit.ly/PyDYLG", u"""Vers L'Avenir""", set(['web', 'sidebar box', 'external'])),
                make_tagged_url("http://www.lalibre.be/actu/belgique/article/753624/michel-daerden-est-decede.html", u"""La Libre""", set(['web', 'sidebar box', 'external'])),
                make_tagged_url("http://www.dhnet.be/infos/belgique/article/403840/michel-daerden-est-decede.html", u"""La Dernière Heure""", set(['web', 'sidebar box', 'external'])),
                make_tagged_url("http://bit.ly/PyEFVp", u"""Het Laatste Niews""", set(['web', 'sidebar box', 'external'])),
                make_tagged_url("http://bit.ly/PyEQ30", u"""De Morgen""", set(['web', 'sidebar box', 'external'])),
                make_tagged_url("http://www.gva.be/nieuws/binnenland/aid1218943/michel-daerden-overleden.aspx", u"""Gazet Van Antwerpen""", set(['web', 'sidebar box', 'external'])),
                make_tagged_url("/debats/editos/2012-08-06/victime-de-l-image-qu-il-a-lui-meme-creee-930676.php", u"""L'édito de Véronique Lamquin - Victime de limage quil a lui-même créée""", set(['to read', 'internal', 'sidebar box'])),
                make_tagged_url("/actualite/belgique/2012-08-05/kris-peeters-michel-daerden-a-determine-la-politique-belge-et-l-a-coloree-930653.php", u"""Kris Peeters : Michel Daerden a déterminé la politique belge et l'a « colorée »""", set(['to read', 'internal', 'sidebar box'])),
                make_tagged_url("/actualite/belgique/2012-08-05/une-grande-perte-pour-le-ps-930642.php", u"""« Une grande perte pour le PS » : les réactions au sein du parti de Michel Daerden""", set(['to read', 'internal', 'sidebar box'])),
                make_tagged_url("/actualite/belgique/2012-08-05/michel-daerden-est-decede-930641.php", u"""Michel Daerden est décédé""", set(['to read', 'internal', 'sidebar box'])),
                make_tagged_url("/actualite/belgique/2012-08-05/a-relire-l-interview-verite-avec-michel-daerden-930644.php", u"""A relire : linterview vérité avec Michel Daerden""", set(['to read', 'internal', 'sidebar box'])),
                make_tagged_url("/actualite/belgique/2012-08-05/michel-daerden-fils-de-cheminot-emigre-en-terre-liegeoise-930645.php", u"""Michel Daerden, fils de cheminot émigré en terre liégeoise""", set(['to read', 'internal', 'sidebar box'])),
                make_tagged_url("http://www.lesoir.be/debats/editos/2012-08-06/victime-de-l-image-qu-il-a-lui-meme-creee-930676.php", u"""Victmie de l'image qu'il a lui-même créée""", set(['to read', 'internal', 'sidebar box', 'internal site'])),
                make_tagged_url("http://pdf.lesoir.be/", u"""Dans Le Soir en PDF : Michel Daerden était hors normes""", set(['to read', 'internal', 'sidebar box', 'pdf newspaper'])),
                make_tagged_url("/debats/chats/2012-08-06/daerden-a-su-utiliser-sa-notoriete-pour-relancer-sa-carriere-politique-930690.php", u"""11h02 : que retenir de Michel Daerden ?""", set(['to read', 'internal', 'sidebar box'])),
                make_tagged_url("/actualite/belgique/2012-08-06/daerden-jose-happart-a-perdu-un-grand-ami-930708.php", u"""Daerden : José Happart a perdu « un grand ami »""", set(['to read', 'internal', 'sidebar box'])),
                make_tagged_url("/actualite/belgique/2012-08-06/le-corps-de-michel-daerden-sera-rapatrie-mardi-au-plus-tard-930805.php", u"""Le corps de Michel Daerden sera rapatrié mardi au plus tard""", set(['to read', 'internal', 'sidebar box'])),
                make_tagged_url("http://www.lesoir.be/sports/JO2012londres/2012-08-06/jo-superman-fond-en-larmes-930845.php", u"""JO : « Superman » fond en larmes""", set(['internal', 'sidebar box', 'internal site', 'recent'])),
                make_tagged_url("http://www.lesoir.be/sports/JO2012londres/2012-08-06/jo-pas-de-medaille-s-pour-les-borlee-930843.php", u"""JO : pas de médaille(s) pour les Borlée""", set(['internal', 'sidebar box', 'internal site', 'recent'])),
                make_tagged_url("http://www.lesoir.be/sports/JO2012londres/2012-08-06/ouedraogo-je-suis-tres-contente-de-ma-course-930841.php", u"""Ouedraogo : « Je suis très contente de ma course »""", set(['internal', 'sidebar box', 'internal site', 'recent'])),
                make_tagged_url("http://www.lesoir.be/debats/editos/2012-08-06/victime-de-l-image-qu-il-a-lui-meme-creee-930676.php", u"""Le Soir """, set(['internal', 'in text'])),
                make_tagged_url("http://pdf.lesoir.be/", u"""Le Soir""", set(['internal', 'pdf newspaper', 'in text'])),
                make_tagged_url("http://bit.ly/PyDYLG", u"""L'Avenir """, set(['external', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/belgique/article/753624/michel-daerden-est-decede.html", u"""La Libre """, set(['external', 'in text'])),
                make_tagged_url("http://www.dhnet.be/infos/belgique/article/403840/michel-daerden-est-decede.html", u"""La Dernière heure """, set(['external', 'in text'])),
                make_tagged_url("http://bit.ly/PyEFVp", u"""Het Laatste Nieuws """, set(['external', 'in text'])),
                make_tagged_url("http://bit.ly/PyEQ30", u"""De Morgen""", set(['external', 'in text'])),
                make_tagged_url("http://www.gva.be/nieuws/binnenland/aid1218943/michel-daerden-overleden.aspx", u"""Gazet van Antwerpen """, set(['external', 'in text'])),
                make_tagged_url("http://concours.lesoir.be/09/v1.cfm?id=B34DC6C5-5056-BE00-631A-8FB06877A308&style=1100&iframe=true", u"""http://concours.lesoir.be/09/v1.cfm?id=B34DC6C5-5056-BE00-631A-8FB06877A308&style=1100&iframe=true""", set(['internal', 'internal site', 'embedded'])),
                make_tagged_url("http://www.coveritlive.com/index2.php/option=com_altcaster/task=viewaltcast/altcast_code=137fb7d38c/height=1200/width=480", u"""http://www.coveritlive.com/index2.php/option=com_altcaster/task=viewaltcast/altcast_code=137fb7d38c/height=1200/width=480""", set(['external', 'embedded'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)