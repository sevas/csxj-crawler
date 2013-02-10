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


class TestLalibreLinkExtraction(object):
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
