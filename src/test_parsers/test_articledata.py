__author__ = 'sevas'

import sys
# excuse me, but a bunny just died
sys.path.append('../')

import unittest
import json
from parsers.article import classify_and_tag, tag_URL, ArticleData

class URLClassificationTestCases(unittest.TestCase):
    def setUp(self):
        self.own_netloc = 'www.foo.com'
        self.associated_sites = {
            'awesomeblog.foo.com':['internal blog'],
            'elections.foo.com':['internal blog', 'politics'],
            'community.foo.com':['community forum'],
        }


    def test_internal_url(self):
        url = '/this/is/just/a/path.php'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        self.assertEqual(tags, ['internal'])

    

    def test_external_url(self):
        url = 'http://www.bar.org'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        self.assertEqual(tags, ['external'])


    def test_internal_blog(self):
        url = 'http://awesomeblog.foo.com/bestest-article-of-the-day.aspx?hl=nl'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        self.assertEqual(tags, ['internal blog'])


    def test_internal_biased_blog(self):
        url = 'http://elections.foo.com/bestest-article-of-the-day.aspx?hl=nl'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        self.assertEqual(tags, ['internal blog', 'politics'])


    def test_other_internal_site(self):
        url = 'http://community.foo.com/index.php?section=humor&show_rows=30'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        self.assertEqual(tags, ['community forum'])

        
class JSONSerializationTestCases(unittest.TestCase):
    pass

        
if __name__ == '__main__':
    unittest.main()
