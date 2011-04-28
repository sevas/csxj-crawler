__author__ = 'sevas'

import sys
sys.path.append('../')
import unittest

from parsers.utils import extract_plaintext_urls_from_text

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

if __name__ == '__main__':
    unittest.main()
