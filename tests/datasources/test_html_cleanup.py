import unittest
from BeautifulSoup import BeautifulSoup

from csxj.datasources.common.utils import remove_text_formatting_markup_from_fragments


def make_fragments(html_data):
    soup = BeautifulSoup(html_data)
    return soup.contents

class HTMLCleanupTestCases(unittest.TestCase):
    def test_one_tag(self):
        html_fragments = make_fragments(u"<strong>hello</strong>")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        self.assertEquals(clean_fragments, u"hello")


    def test_multiple_tags(self):
        html_fragments = make_fragments(u"<em><strong>hello</strong><em>")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        self.assertEquals(clean_fragments, u"hello")


    def test_unsupported_tag(self):
        html_fragments = make_fragments(u"<foo>hello</foo>")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        self.assertEquals(clean_fragments, u"")


    def test_link(self):
        html_fragments = make_fragments(u"""<a href="/foo">foo</a>""")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        self.assertEquals(clean_fragments, u"foo")


    def test_multiple_fragments(self):
        html_fragments = make_fragments(u"<strong>foo</strong><em>bar</em>")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        self.assertEquals(clean_fragments, u"foobar")


    def test_mixed_carriage_returns(self):
        html_fragments = make_fragments(u"<i>foo</i>\n<b>bar</b>")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        self.assertEquals(clean_fragments, u"foo\nbar")


    def test_cascading_formatting(self):
        html_fragments = make_fragments("""
        <p><strong>First</strong> paragraph.</p>
        <p><strong>Second</strong> paragraph.</p>
        """)
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        self.assertEquals(clean_fragments, u"\nFirst paragraph.\nSecond paragraph.\n")


    def test_string_stripping(self):
        html_fragments = make_fragments("\n  \tI'm formatting from word, bitch!\n\n\n")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments, "\n\t ")
        self.assertEquals(clean_fragments, "I'm formatting from word, bitch!")

if __name__ == '__main__':
    unittest.main()
