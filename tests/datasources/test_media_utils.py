from nose.tools import raises, eq_, ok_
from csxj.datasources.common import media_utils
from BeautifulSoup import BeautifulSoup


def make_soup(html_data):
    return BeautifulSoup(html_data)


class TestMediaUtils(object):
    def setUp(self):
        self.netloc = 'foo.com'
        self.internal_sites = {}

    def test_embedded_script(self):
        """
            Test that the embedded media extraction works on a simple embedded script with <noscript> fallback
        """
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
        """
            Test that the embedded media extraction on a simple embedded script without <noscript> fallback raises a ValueError exception
        """
        html_data = """
        <div>
            <script src='http://bar.com/some_widget.js'>
            </script>
        </div>
        """
        soup = make_soup(html_data)
        media_utils.extract_tagged_url_from_embedded_script(soup.script, self.netloc, self.internal_sites)

    def test_embeded_tweet_widget(self):
        """
            Test that the embedded media extraction returns a link to a twitter ressource when the script is a twitter widget
        """
        assert(False)

    @raises(ValueError)
    def test_embedded_javascript_code(self):
        """
            Test that the embedded script detector raises a ValueError when processing a <script> tag with arbitrary JS inside
        """
        js_content = """<script type='text/javascript'>var pokey='penguin'; </script>"""
        soup = make_soup(js_content)
        media_utils.extract_tagged_url_from_embedded_script(soup, self.netloc, self.internal_sites)
