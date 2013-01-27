# -*- coding: utf-8 -*-
from nose.tools import eq_, ok_, nottest
import itertools as it

from csxj.common.tagging import TaggedURL

@nottest
def to_frozensets(taggedURLs):
    return set([(url, title, frozenset(tags)) for url, title, tags in taggedURLs])


@nottest
def format_as_two_columns(expected, extracted):
    expected, extracted = sorted(expected), sorted(extracted)

    def make_pairs():
        for left, right in it.izip_longest(expected, extracted, fillvalue=TaggedURL("NONE", "NONE", set())):
            yield "{0:100}    {1:100}".format(left.URL[:100], right.URL[:100])
    return "\n".join(make_pairs())

@nottest
def assert_taggedURLs_equals(expected_links, extracted_links):
    """ Helper function to assess the equality of two lists of TaggedURL

        Provides somewhat helpful feedback to know what is actually different
        It does not compare the 'title' fields because character encoding
        issues make me cry. A lot.
    """
    expected_count, extracted_count = len(expected_links), len(extracted_links)
    eq_(expected_count, extracted_count, msg="Expected {0} links. Extracted {1}\n{2}".format(expected_count, extracted_count, format_as_two_columns(expected_links, extracted_links)))

    if to_frozensets(expected_links) != to_frozensets(extracted_links):
        for expected, extracted in zip(sorted(expected_links), sorted(extracted_links)):
            eq_(expected[0], extracted[0], msg=u'URLs are not the same: \n\t{0} \n\t{1}'.format(expected[0], extracted[0]))
            #eq_(expected[1], extracted[1], msg='titles are not the same')
            ok_(expected[2].issubset(extracted[2]), msg=u'[{0}]({1}): tags are not the same: \n\tExpected: {2} \n\tGot:      {3}'.format(expected[1], expected[0], expected[2], extracted[2]))

    else:
        ok_(True)
