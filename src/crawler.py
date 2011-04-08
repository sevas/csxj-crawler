#!/usr/bin/env python

import os.path
from itertools import izip_longest
from parsers import lesoir



def filter_only_new_stories(frontpage_titles, outdir):
    if not os.path.exists("%s/last_frontpage_list.txt" % (outdir)):
        




def are_stories_missing_from_frontpage(frontpage_titles, rss_titles):
    """
    Compare the list of titles found in both the frontpage and the RSS feed.
    The RSS feed is considered complete. This function tests whether or not
    the frontpage parser got all the frontpage stories.

    Returns the list of items found only in the rss feed
    """

    only_in_rss = set(rss_titles) - set(frontpage_titles)

    return list(only_in_rss)


if __name__ == '__main__':
    titles_and_urls = lesoir.get_frontpage_articles()
    rss_titles = lesoir.get_rss_articles()

    frontpage_titles = [t for (t, u) in titles_and_urls]
    print are_stories_missing_from_frontpage(frontpage_titles, rss_titles)

    print len(frontpage_titles), len(rss_titles)
    
    for (front, rss) in izip_longest(frontpage_titles, rss_titles, fillvalue='***'):
        print "%s \t\t\t\t\t\t\t\t %s" % (front, rss)
