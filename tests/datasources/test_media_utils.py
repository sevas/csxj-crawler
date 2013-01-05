from nose.tools import *
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
            Test that the embedded media extraction works on a simple embedded script
        """
        html_data = """
        <script src='http://bar.com/some_widget.js'>
        </script>
        """
        assert(False)

    def test_embeded_stweet_widget(self):
        """
            Test that the embedded media extraction returns a link to a twitter ressource when the script is a twitter widget
        """
        assert(False)
