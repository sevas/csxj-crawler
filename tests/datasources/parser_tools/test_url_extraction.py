# coding=utf-8

from nose.tools import eq_
from csxj.datasources.parser_tools.utils import extract_plaintext_urls_from_text


class TestPlainTextURLExtractor(object):
    def setUp(self):
        self.simple_url = 'http://www.foo.com'
        # fuck yeah gehol
        self.complex_url = 'http://164.15.72.157:8080/Reporting/Individual;Student%20Set%20Groups;id;%23SPLUS35F0F1?&template=Ann%E9e%20d%27%E9tude&weeks=1-14&days=1-6&periods=5-33&width=0&height=0'
        self.text = 'This text was written in notepad, hence {0} , fuck you if you like clicking stuff'
        self.text_with_urls = """ Visit my website at http://www.example.com, it's awesome!
        This is shit: http://en.wikipedia.org/wiki/PC_Tools_(Central_Point_Software)
        And this is shit too: http://msdn.microsoft.com/en-us/library/aa752574(VS.85).aspx
        My website (http://www.awesomeexample.com) is awesome. How about lastexample.com?
        """

    def test_simple_url(self):
        """ extract_plaintext_urls_from_text() can extract a simple URL """
        text_with_url = self.text.format(self.simple_url)
        urls = extract_plaintext_urls_from_text(text_with_url)
        eq_(urls, [self.simple_url])

    def test_complex_url(self):
        """ extract_plaintext_urls_from_text() can extract a complex URL (parameters, port, spaces and semicolons) """
        text_with_url = self.text.format(self.complex_url)
        urls = extract_plaintext_urls_from_text(text_with_url)
        eq_(urls, [self.complex_url])

    def test_multiple_urls(self):
        """ extract_plaintext_urls_from_text() can extract several URLs from a piece of text"""
        text = 'this {0} has {1} many {2} links {3}'
        text_with_urls = text.format(self.simple_url, self.complex_url, self.complex_url, self.simple_url)
        urls = extract_plaintext_urls_from_text(text_with_urls)
        eq_(urls, [self.simple_url, self.complex_url, self.complex_url, self.simple_url])

    def test_text_with_urls(self):
        """ extract_plaintext_urls_from_text()"""
        urls = extract_plaintext_urls_from_text(self.text_with_urls)
        eq_(urls, ['http://www.example.com', 'http://en.wikipedia.org/wiki/PC_Tools_(Central_Point_Software)',
                   'http://msdn.microsoft.com/en-us/library/aa752574(VS.85).aspx', 'http://www.awesomeexample.com',
                   'lastexample.com'])

    def test_no_url(self):
        """ extract_plaintext_urls_from_text() returns an empty list if the text contains no URL"""
        text = self.text.format('not a url')
        urls = extract_plaintext_urls_from_text(text)
        eq_(urls, [])

    def test_schemeless_url(self):
        """ extract_plaintext_urls_from_text() can handle urls with no scheme (e.g. 'www.foo.com') """
        url = "www.foo.com"
        extracted_urls = extract_plaintext_urls_from_text(url)
        eq_([url], extracted_urls, msg=u"(Expected '{0}', got'{1}')".format([url], extracted_urls))

    def test_schemeless_no_www_url(self):
        """ extract_plaintext_urls_from_text() can handle urls with no scheme, no 'www' prefix (e.g. 'foo.com') """
        urls = ["foo.net", "Foo.net"]
        for url in urls:
            extracted_urls = extract_plaintext_urls_from_text(url)
            eq_([url.lower()], extracted_urls, msg=u"Could not extract schemeless url without 'www' prefix (Expected '{0}', got'{1}')".format([url], extracted_urls))

    def test_schemeless_subdomain_url(self):
        """ extract_plaintext_urls_from_text() can handle urls with no scheme and a subdomain (e.g. 'blog.foo.net') """
        url = "blog.foo.net"
        extracted_urls = extract_plaintext_urls_from_text(url)
        eq_([url], extracted_urls, msg=u"Could not extract schemeless url with subdomain (Expected '{0}', got'{1}')".format([url], extracted_urls))

    def test_tinylinks(self):
        """extract_plaintext_urls_from_text() correctly guesses that things like “bit.ly/foo” and “is.gd/foo/” """
        url = "bit.ly/foo"
        extracted_urls = extract_plaintext_urls_from_text(url)
        eq_([url], extracted_urls)


    def test_discard_enails(self):
        """extract_plaintext_urls_from_text() ignores email adresses"""
        urls = ["blah@foo.com", "@foo.com", "ladh.be@gmail.com"]
        for url in urls:
            extracted_urls = extract_plaintext_urls_from_text(url)
            eq_([], extracted_urls, msg=u"{0} was matched as a url: {1}".format(url, extracted_urls))
