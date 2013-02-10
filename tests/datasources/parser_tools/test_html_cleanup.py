from nose.tools import eq_
from BeautifulSoup import BeautifulSoup

from csxj.datasources.parser_tools.utils import remove_text_formatting_markup_from_fragments
from csxj.datasources.parser_tools.utils import remove_text_formatting_and_links_from_fragments


def make_fragments(html_data):
    soup = BeautifulSoup(html_data)
    return soup.contents


class TestHTMLCleanup():
    def test_one_tag(self):
        html_fragments = make_fragments(u"<strong>hello</strong>")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        eq_(clean_fragments, u"hello")

    def test_multiple_tags(self):
        html_fragments = make_fragments(u"<em><strong>hello</strong><em>")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        eq_(clean_fragments, u"hello")

    def test_unsupported_tag(self):
        html_fragments = make_fragments(u"<foo>hello</foo>")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        eq_(clean_fragments, u"")

    def test_link(self):
        html_fragments = make_fragments(u"""<a href="/foo">foo</a>""")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        eq_(clean_fragments, u"foo")

    def test_multiple_fragments(self):
        html_fragments = make_fragments(u"<strong>foo</strong><em>bar</em>")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        eq_(clean_fragments, u"foobar")

    def test_mixed_carriage_returns(self):
        html_fragments = make_fragments(u"<i>foo</i>\n<b>bar</b>")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        eq_(clean_fragments, u"foo\nbar")

    def test_cascading_formatting(self):
        html_fragments = make_fragments("""
        <p><strong>First</strong> paragraph.</p>
        <p><strong>Second</strong> paragraph.</p>
        """)
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        eq_(clean_fragments, u"\nFirst paragraph.\nSecond paragraph.\n")

    def test_string_stripping(self):
        html_fragments = make_fragments("\n  \tI'm formatting from word, bitch!\n\n\n")
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments, "\n\t ")
        eq_(clean_fragments, "I'm formatting from word, bitch!")

    def test_discard_iframes(self):
        """ <iframe> tags within a text block are discarded"""
        html_fragments = make_fragments("""
        <p>Hello there, <iframe src="lolz">random noise</iframe>friend</p>
        """)
        clean_fragments = remove_text_formatting_markup_from_fragments(html_fragments)
        expected_fragments = u"\nHello there, friend\n"
        eq_(clean_fragments, expected_fragments)

    def test_remove_markup_and_links(self):
        html_fragments = make_fragments(u"""there is no link here: <a href="/foo">foo</a>""")
        clean_fragments = remove_text_formatting_and_links_from_fragments(html_fragments)
        eq_(clean_fragments, u"there is no link here: ")
