#import unittest
#import os.path
#import csxj.db as csxjdb
#from csxj.common.tagging import tag_URL
#
#DB_ROOT = os.path.join(os.path.dirname(__file__), "../mock_db")
#TEST_SOURCE_NAME="source1"
#
#MOCK_ARTICLE = csxjdb.ArticleData("http://localhost", "Title", today.day, today.time, today,
#                                    set([tag_URL(("http://media.foo.com/123", "Some Video"), 'external') ]),
#                                    ["Foo", "Bar", "Video"], "Anon", "lorem ipsum", "dolor")
#
#
#class CSxJDBProviderTestCases(unittest.TestCase):
#    def setUp(self):
#        p = csxjdb.Provider(DB_ROOT, TEST_SOURCE_NAME)
#
#
#    def test_articles_extraction(self):
#        pass
#
#
#    def test_articles_extraction_wrong_time(self):
#        pass
#
