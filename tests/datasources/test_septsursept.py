#!/usr/bin/env python
# -*- coding: utf-8 -*-


from nose.tools import eq_
from csxj.datasources.septsursept import separate_articles_and_photoalbums


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