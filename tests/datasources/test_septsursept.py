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



class Test7sur7LinkExtraction(object):
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

    def test_embedded_document(self):
        """ The 7sur7.be parser can extract and tag link to embedded document """
        with open(os.path.join(DATA_ROOT, "embedded_document.html")) as f:
            article, raw_html = septsursept.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("/7s7/fr/1502/Belgique/article/detail/1529567/2012/11/06/Forte-augmentation-du-nombre-de-demandeurs-d-asile-venant-de-Syrie.dhtml", u"""Forte augmentation du nombre de demandeurs d'asile venant de Syrie""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1502/Belgique/article/detail/1522934/2012/10/24/Le-code-de-la-nationalite-durci.dhtml", u"""Le code de la nationalité durci""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1502/Belgique/article/detail/1522338/2012/10/23/Regroupement-familial-refus-de-visas-a-foison.dhtml", u"""Regroupement familial: refus de visas à foison""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1481/Home/1445/immigration/actualite/index.dhtml", u"""immigration""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("/7s7/fr/1481/Home/152/Politique/actualite/index.dhtml", u"""Politique""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("/7s7/fr/1481/Home/972/Geert-Bourgeois/actualite/index.dhtml", u"""Geert Bourgeois""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("/7s7/fr/1481/Home/1135/N-VA/actualite/index.dhtml", u"""N-VA""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("http://static1.7sur7.be/static/asset/2012/BOEKJE_FR_181.pdf", u"""Téléchargez pdf""", set(['internal', 'internal site', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_video_and_in_text_links(self):
        """ The 7sur7.be parser can extract and tag embedded video, in-text links, link to document"""
        with open(os.path.join(DATA_ROOT, "embedded_video_and_in_text_links.html")) as f:
            article, raw_html = septsursept.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.facebook.com/pages/Carine-Gilson-Lingerie-Couture/161436673890010", u"""page Facebook""", set(['external', 'in text'])),
                make_tagged_url("http://www.carinegilson.com/", u"""http://www.carinegilson.com/""", set(['external', 'in text'])),
                make_tagged_url("/7s7/fr/1525/Tendances/article/detail/1517986/2012/10/16/Un-nouveau-fiasco-Photoshop.dhtml", u"""Un nouveau fiasco Photoshop""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1525/Tendances/article/detail/1515857/2012/10/12/Les-talons-de-la-mort.dhtml", u"""Les talons de la mort""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1525/Tendances/article/detail/1515660/2012/10/12/Des-bijoux-tres-intimes.dhtml", u"""Des bijoux très intimes""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1481/Home/400619/Tendances/actualite/index.dhtml", u"""Tendances""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("/7s7/fr/1481/Home/558/Entreprises/actualite/index.dhtml", u"""Entreprises""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("http://static1.7sur7.be/static/asset/2012/Look_book_CG_Couture_SS_012_dff_low_41.pdf", u"""Téléchargez pdf""", set(['internal', 'internal site', 'embedded'])),
                make_tagged_url("http://www.youtube.com/embed/mDzPISNuHCs/?wmode=opaque", u"""http://www.youtube.com/embed/mDzPISNuHCs/?wmode=opaque""", set(['external', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)
