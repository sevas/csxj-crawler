__author__ = 'sevas'

import sys
import unittest
from BeautifulSoup import BeautifulSoup

from csxj.datasources.common.utils import extract_plaintext_urls_from_text
from csxj.datasources.common.utils import remove_text_formatting_markup_from_fragments

class PlainTextURLExtractorTestCases(unittest.TestCase):
    def setUp(self):
        self.simple_url = 'http://www.foo.com'
        # fuck yeah gehol
        self.complex_url = 'http://164.15.72.157:8080/Reporting/Individual;Student%20Set%20Groups;id;%23SPLUS35F0F1?&template=Ann%E9e%20d%27%E9tude&weeks=1-14&days=1-6&periods=5-33&width=0&height=0'
        self.text = 'This text was written in notepad, hence {0} , fuck you if you like clicking stuff'
        self.text_with_urls =""" Visit my website at http://www.example.com, it's awesome!
        This is shit: http://en.wikipedia.org/wiki/PC_Tools_(Central_Point_Software)
        And this is shit too: http://msdn.microsoft.com/en-us/library/aa752574(VS.85).aspx
        My website (http://www.awesomeexample.com) is awesome. How about lastexample.com?
        """

    def test_simple_url(self):
        text_with_url = self.text.format(self.simple_url)
        urls = extract_plaintext_urls_from_text(text_with_url)
        self.assertEqual(urls, [self.simple_url])


    def test_complex_url(self):
        text_with_url = self.text.format(self.complex_url)
        urls = extract_plaintext_urls_from_text(text_with_url)
        self.assertEqual(urls, [self.complex_url])


    def test_multiple_urls(self):
        text = 'this {0} has {1} many {2} links {3}'
        text_with_urls = text.format(self.simple_url, self.complex_url, self.complex_url, self.simple_url)
        urls = extract_plaintext_urls_from_text(text_with_urls)
        self.assertEqual(urls, [self.simple_url, self.complex_url, self.complex_url, self.simple_url])


    def test_text_with_urls(self):
        urls = extract_plaintext_urls_from_text(self.text_with_urls)
        self.assertEqual(urls, ['http://www.example.com', 'http://en.wikipedia.org/wiki/PC_Tools_(Central_Point_Software)', 'http://msdn.microsoft.com/en-us/library/aa752574(VS.85).aspx', 'http://www.awesomeexample.com'])


    def test_no_url(self):
        text = self.text.format('not a url')
        urls = extract_plaintext_urls_from_text(text)
        self.assertEqual(urls, [])
        


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



if __name__ == '__main__':
    unittest.main()
