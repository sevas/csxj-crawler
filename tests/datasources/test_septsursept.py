# coding=utf-8

import os
from nose.tools import eq_

from csxj.common.tagging import make_tagged_url
from csxj.datasources import septsursept
from csxj.datasources.septsursept import separate_articles_and_photoalbums
from csxj_test_tools import assert_taggedURLs_equals

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', 'septsursept')

class TestFrontpageItemsFilter(object):
    def setUp(self):
        self.article_item = (u"Some Article", "http://www.7sur7.be/7s7/fr/1504/Insolite/article/detail/1494529/2012/09/02/Ils-passent-devant-une-vitrine-avant-de-disparaitre.dhtml")
        self.photoalbum_item = (u"Some photoalbum", "http://www.7sur7.be/7s7/fr/8024/Stars/photoalbum/detail/85121/1212631/0/Showbiz-en-images.dhtml")
        self.video_item = (u"Some video", "http://www.7sur7.be/7s7/fr/3846/Sports/video/detail/1436930/Lucescu-degoute-par-la-douche-du-titre.dhtml")

    def test_photoalbum_filter(self):
        """ The 7sur7.be frontpage items filter can separate photoalbum url from regular news items. """
        frontpage_items = [self.article_item, self.photoalbum_item]

        expected_news, expected_junk = [self.article_item], [self.photoalbum_item]
        observed_news, observed_junk = separate_articles_and_photoalbums(frontpage_items)

        eq_(expected_news, observed_news)
        eq_(expected_junk, observed_junk)

    def test_nothing_to_filter(self):
        """ The 7sur7.be frontpage items filter does nothing to a list of urls with no photoalbum or video. """
        frontpage_items = [self.article_item]

        expected_news, expected_junk = [self.article_item], []
        observed_news, observed_junk = separate_articles_and_photoalbums(frontpage_items)

        eq_(expected_news, observed_news)
        eq_(expected_junk, observed_junk)

    def test_video_filter(self):
        """ The 7sur7.be frontpage items filter can separate video urls from regular news items. """
        frontpage_items = [self.article_item, self.video_item]

        expected_news, expected_junk = [self.article_item], [self.video_item]
        observed_news, observed_junk = separate_articles_and_photoalbums(frontpage_items)

        eq_(expected_news, observed_news)
        eq_(expected_junk, observed_junk)

    def test_filter(self):
        """ The 7sur7.be frontpage items filter can separate photoalbum and video urls from regular news items from regular news items. """
        frontpage_items = [self.photoalbum_item, self.article_item, self.video_item]

        expected_news, expected_junk = [self.article_item], [self.photoalbum_item, self.video_item]
        observed_news, observed_junk = separate_articles_and_photoalbums(frontpage_items)

        eq_(expected_news, observed_news)
        eq_(expected_junk, observed_junk)



class Test7sur7Extraction(object):
    def test_embedded_tweets(self):
        """ The 7sur7.be parser can extract and tag embedded tweets (as well as sidebar box links, bottom box links). """
        with open(os.path.join(DATA_ROOT, "embedded_tweets.html")) as f:
            article, raw_html = septsursept.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("/7s7/fr/1505/Monde/article/detail/1451992/2012/06/11/Nadine-Morano-n-a-aucun-etat-d-ame-a-en-appeler-aux-electeurs-du-FN.dhtml", u"""Nadine Morano n'a "aucun état d'âme" à en appeler aux électeurs du FN""", set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1527/People/article/detail/1438967/2012/05/15/La-sortie-dramatique-ratee-de-Nicolas-Bedos-sur-Twitter.dhtml", u"""La sortie dramatique ratée de Nicolas Bedos sur Twitter""", set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1527/People/article/detail/1434935/2012/05/08/Gros-clash-entre-Nicolas-Bedos-et-Mathieu-Kassovitz.dhtml", u"""Gros clash entre Nicolas Bedos et Mathieu Kassovitz""", set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1528/Cinema/article/detail/1425335/2012/04/18/Mathieu-Kassovitz-attaque-Frederic-Beigbeder.dhtml", u"""Mathieu Kassovitz attaque Frédéric Beigbeder""", set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1505/Monde/article/detail/1451992/2012/06/11/Nadine-Morano-n-a-aucun-etat-d-ame-a-en-appeler-aux-electeurs-du-FN.dhtml", u"""Nadine Morano n'a "aucun état d'âme" à en appeler aux électeurs du FN""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1527/People/article/detail/1438967/2012/05/15/La-sortie-dramatique-ratee-de-Nicolas-Bedos-sur-Twitter.dhtml", u"""La sortie dramatique ratée de Nicolas Bedos sur Twitter""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1527/People/article/detail/1434935/2012/05/08/Gros-clash-entre-Nicolas-Bedos-et-Mathieu-Kassovitz.dhtml", u"""Gros clash entre Nicolas Bedos et Mathieu Kassovitz""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1481/Home/230/Stars-internationales/actualite/index.dhtml", u"""Stars internationales""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("/7s7/fr/1481/Home/707974156/Twitter/actualite/index.dhtml", u"""Twitter""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("https://twitter.com/nadine__morano/status/209732333727780865", u"""https://twitter.com/nadine__morano/status/209732333727780865""", set(['tweet', 'external', 'embedded'])),
                make_tagged_url("https://twitter.com/kassovitz/status/212186904848900097", u"""https://twitter.com/kassovitz/status/212186904848900097""", set(['tweet', 'external', 'embedded'])),
                make_tagged_url("https://twitter.com/kassovitz/status/212189899279970304", u"""https://twitter.com/kassovitz/status/212189899279970304""", set(['tweet', 'external', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)
