import unittest
from csxj.articlequeue import ArticleQueueFiller



OLD_TOC = [
    (u"foo", "http://foo"),
    (u"bar", "http://bar"),
    (u"zorg", "http://zorg")
]


CURRENT_TOC = [
    (u"bar", "http://bar"),
    (u"zorg", "http://zorg"),
    (u"quux", "http://quux")
]


NEW_STORIES = [
    (u"zorg", "http://zorg"),
    (u"quux", "http://quux")
]



def save_toc_to_file(toc, filename):
    pass


def load_last_toc_from_file(filename):
    return OLD_TOC



class QueueFillerTestCases(unittest.TestCase):
    def setUp(self):
        pass


    def tearDown(self):
        pass



