# coding=utf-8


import unittest

from csxj.datasources.common.utils import convert_utf8_url_to_ascii


class TestUTF8toASCIIConverter(unittest.TestCase):
    def test_regular_url(self):
        url = u'http://www.google.com'
        ascii_url = 'http://www.google.com'
        self.assertEqual(convert_utf8_url_to_ascii(url), ascii_url)


    def test_quoted_url(self):
        url = 'http://\xe2\x9e\xa1.ws/\xe2\x99\xa5'
        ascii_url = 'http://xn--hgi.ws/%E2%99%A5'
        self.assertEqual(convert_utf8_url_to_ascii(url), ascii_url)


    def test_quoted_with_params_url(self):
        url = 'http://\xe2\x9e\xa1.ws/\xe2\x99\xa5/%2F'
        ascii_url = 'http://xn--hgi.ws/%E2%99%A5/%2F'
        self.assertEqual(convert_utf8_url_to_ascii(url), ascii_url)


    def test_unicode_url(self):
        url = u'http://➡.ws/admin'
        ascii_url = 'http://xn--hgi.ws/admin'
        self.assertEqual(convert_utf8_url_to_ascii(url), ascii_url)


    def test_unicode_with_params_url(self):
        url = u'http://Åsa:abc123@➡.ws:81/admin'
        ascii_url = 'http://%C3%85sa:abc123@xn--hgi.ws:81/admin'
        self.assertEqual(convert_utf8_url_to_ascii(url), ascii_url)

