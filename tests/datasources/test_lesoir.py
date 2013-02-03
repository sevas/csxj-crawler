# -*- coding: utf-8 -*-
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