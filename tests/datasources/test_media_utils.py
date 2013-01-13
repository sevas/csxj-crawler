"""
Test suite for the embedded <script> extraction
"""
from nose.tools import raises, eq_, ok_
from BeautifulSoup import BeautifulSoup

from csxj.datasources.common import media_utils
from csxj.datasources.common import twitter_utils

import test_twitter_utils



def make_soup(html_data):
    return BeautifulSoup(html_data)


class TestMediaUtils(object):
    def setUp(self):
        self.netloc = 'foo.com'
        self.internal_sites = {}

    def test_embedded_script(self):
        """ The embedded <script> extraction works on a simple embedded script with <noscript> fallback """
        html_data = """
        <div>
            <script src='http://bar.com/some_widget.js'>
            </script>
           * <noscript>
                <a href='http://bar.com/some_resource'>Disabled JS, go here</a>
            </noscript>
        </div>
        """
        soup = make_soup(html_data)
        tagged_URL = media_utils.extract_tagged_url_from_embedded_script(soup.script, self.netloc, self.internal_sites)
        eq_(tagged_URL.URL, "http://bar.com/some_resource")

    @raises(ValueError)
    def test_embedded_script_without_noscript_fallback(self):
        """ The embedded <script> extraction raises a ValueError exception when encountering a script without <noscript> fallback """
        html_data = """
        <div>
            <script src='http://bar.com/some_widget.js'>
            </script>
        </div>
        """
        soup = make_soup(html_data)
        media_utils.extract_tagged_url_from_embedded_script(soup.script, self.netloc, self.internal_sites)

    def test_embeded_tweet_widget(self):
        """ The embedded <script> extraction returns a link to a twitter resource when the script is a twitter widget """
        html_data = """
        <div>
            <script src={0}>
            {1}
            </script>
        </div>
        """.format(twitter_utils.TWITTER_WIDGET_SCRIPT_URL, test_twitter_utils.SAMPLE_TWIMG_PROFILE)

        soup = make_soup(html_data)
        tagged_URL = media_utils.extract_tagged_url_from_embedded_script(soup.script, self.netloc, self.internal_sites)
        expected_tags = set(['twitter widget', 'twitter profile', 'script', 'external', 'embedded'])

        eq_(tagged_URL.tags, expected_tags)

    @raises(ValueError)
    def test_embedded_javascript_code(self):
        """ The embedded <script> extraction raises a ValueError when processing a <script> tag with arbitrary Javascript code inside """
        js_content = """<script type='text/javascript'>var pokey='penguin'; </script>"""
        soup = make_soup(js_content)
        media_utils.extract_tagged_url_from_embedded_script(soup, self.netloc, self.internal_sites)



    def test_embedded_tweet_widget_splitted(self):
        """ The embedded <script> extraction should work when an embedded tweet is split between the widget.js inclusion and the actual javascript code to instantiate it."""
        html_data = """
        <div>
            <script src={0}></script>
            <script>
            {1}
            </script>
        </div>
        """.format(twitter_utils.TWITTER_WIDGET_SCRIPT_URL, test_twitter_utils.SAMPLE_TWIMG_PROFILE)

        soup = make_soup(html_data)
        tagged_URL = media_utils.extract_tagged_url_from_embedded_script(soup.script, self.netloc, self.internal_sites)
        expected_tags = set(['twitter widget', 'twitter profile', 'script', 'external', 'embedded'])

        eq_(tagged_URL.tags, expected_tags)