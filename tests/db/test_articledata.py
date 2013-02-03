
from datetime import date, time, datetime
from csxj.common.tagging import TaggedURL
        
class TestJSONSerializationTestCases(object):
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


