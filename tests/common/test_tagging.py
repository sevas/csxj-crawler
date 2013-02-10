
from nose.tools import eq_
from csxj.common.tagging import classify_and_tag, tag_URL, TaggedURL, make_tagged_url


class TestTaggedURL(object):
    def test_make_tagged_url(self):
        """ csxj.common.tagging.make_tagged_url() returns a TaggedURL """
        url, title, tags = "http://www.foo.com", u"a very nice website", set(['hello'])
        expected_url = TaggedURL(URL=url, title=title, tags=tags)
        tagged_url = make_tagged_url(url, title, tags)
        eq_(expected_url, tagged_url)

class TestURLClassificationTestCases(object):
    def setUp(self):
        self.own_netloc = 'www.foo.com'
        self.associated_sites = {
            'awesomeblog.foo.com':['internal blog'],
            'elections.foo.com':['internal blog', 'politics'],
            'community.foo.com':['community forum'],
        }

    def test_internal_url(self):
        """ csxj.common.tagging.classify_and_tag() classifies local path as 'internal' """
        url = '/this/is/just/a/path.php'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        eq_(tags, set(['internal']))

    def test_internal_url_with_netloc(self):
        """ csxj.common.tagging.classify_and_tag() classifies url from same netloc as 'internal' """
        url = 'http://www.foo.com/this/is/just/a/path.php'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        eq_(tags, set(['internal']))

    def test_external_url(self):
        """ csxj.common.tagging.classify_and_tag() classifies external url as 'external' """
        url = 'http://www.bar.org'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        eq_(tags, set(['external']))

    def test_internal_blog(self):
        """ csxj.common.tagging.classify_and_tag() classifies external url as 'external' """
        url = 'http://awesomeblog.foo.com/bestest-article-of-the-day.aspx?hl=nl'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        eq_(tags, set(['internal site', 'internal blog', 'internal']))

    def test_internal_biased_blog(self):
        """ csxj.common.tagging.classify_and_tag() returns adequate tags when a url matches a blog from 'associated_sites' """
        url = 'http://elections.foo.com/bestest-article-of-the-day.aspx?hl=nl'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        eq_(tags, set(['internal site', 'internal blog', 'politics', 'internal']))

    def test_other_internal_site(self):
        """ csxj.common.tagging.classify_and_tag() returns adequate tags when a url matches a site from 'associated_sites' """
        url = 'http://community.foo.com/index.php?section=humor&show_rows=30'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        eq_(tags, set(['internal site', 'community forum', 'internal']))

    def test_no_URL(self):
        """ csxj.common.tagging.classify_and_tag() returns an empty set whem the url is an empty string """
        url = ''
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        eq_(tags, set())

    def test_anchor(self):
        """ csxj.common.tagging.classify_and_tag() handles anchor links """
        url = '#anchor'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        eq_(tags, set(['internal', 'anchor']))

    def test_external_hashbang_url(self):
        """ csxj.common.tagging.classify_and_tag() handles external urls with hashbang """
        url = 'http://twitter.com/!#/foo'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        eq_(tags, set(['external']))

    def test_internal_hashbang_url(self):
        """ csxj.common.tagging.classify_and_tag() handles internal urls with a hashbang """
        url = 'http://twitter.com/!#/foo'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        eq_(tags, set(['external']))