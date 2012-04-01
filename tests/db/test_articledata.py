import unittest
from datetime import datetime, date, time

from csxj.common.tagging import classify_and_tag, tag_URL, TaggedURL


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
        self.assertEqual(tags, set(['internal']))


    def test_internal_url_with_netloc(self):
        url = 'http://www.foo.com/this/is/just/a/path.php'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        self.assertEqual(tags, set(['internal']))
    

    def test_external_url(self):
        url = 'http://www.bar.org'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        self.assertEqual(tags, set(['external']))


    def test_internal_blog(self):
        url = 'http://awesomeblog.foo.com/bestest-article-of-the-day.aspx?hl=nl'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        self.assertEqual(tags, set(['internal site', 'internal blog']))


    def test_internal_biased_blog(self):
        url = 'http://elections.foo.com/bestest-article-of-the-day.aspx?hl=nl'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        self.assertEqual(tags, set(['internal site', 'internal blog', 'politics']))


    def test_other_internal_site(self):
        url = 'http://community.foo.com/index.php?section=humor&show_rows=30'
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        self.assertEqual(tags, set(['internal site', 'community forum']))



    def test_tag_URL(self):
        url, title = ('/news/category/2438985/', 'There is a hole in the world')
        tags = ['internal']
        taggedURL = TaggedURL(URL=url, title=title, tags=tags)
        self.assertEqual(tag_URL((url, title), tags), taggedURL)


    def test_no_URL(self):
        url = ''
        tags = classify_and_tag(url, self.own_netloc, self.associated_sites)
        self.assertEqual(tags, set())




        
class JSONSerializationTestCases(unittest.TestCase):
    def setUp(self):
        self.url = 'http://www.foo.com/news/category'
        self.title = 'Fuck yeah royal wedding god damnit'
        self.pub_date = date(2011, 04, 28)
        self.pub_time = time(12, 23)
        self.fetched_datetime = datetime(2011, 04, 28, 13, 01)

        self.links = [TaggedURL(URL='http://www.bar.org/story.php?id=876543', title='I, Anteater', tags=['external']),
                     TaggedURL(URL='/news/cat/754365', title='Platypus considered harmful', tags=['internal']),
                     TaggedURL(URL='/define/platypus', title='Definition: Platypus', tags=['internal', 'keyword'])]

        self.category = ['maincat', 'subcat']
        self.author = 'Some Person'

        self.intro = 'So, that thing happenned'
        self.content = ['Paragraphs', 'are', 'proof', 'of', 'your', 'literacy']

#    def test_serialization(self):
#        article = ArticleData(self.url, self.title,
#                              self.pub_date, self.pub_time, self.fetched_datetime,
#                              self.external_links, self.internal_links,
#                              self.author, self.category,
#                              self.intro, self.content)
#
#        json_string = article.to_json()
#        article2 = ArticleData.from_json(json_string)
#        self.assertEqual(article, article2)



if __name__ == '__main__':
    unittest.main()
