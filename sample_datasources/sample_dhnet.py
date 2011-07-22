import sys
sys.path.append('../src')

from datasources import dhnet

def test_sample_data():
    filename = '../sample_data/dhnet_missing_links.html'
    with open(filename, 'r') as f:
        article_data, html_content = dhnet.extract_article_data(f)
        article_data.print_summary()

        for l in article_data.internal_links:
            if 'keyword' not in l.tags:
                print l.title, l.tags

        for l in article_data.external_links:
            print l

        print '-' * 20


def show_frontpage_articles():
    frontpage_items, blogposts = dhnet.get_frontpage_toc()

    print '%d items on frontpage' % len(frontpage_items)
    for title, url in frontpage_items:
        print 'Fetching data for : %s (%s)' % (title, url)

        article_data, html_content = dhnet.extract_article_data(url)
        if article_data:
            article_data.print_summary()

            for (title, url, tags) in article_data.external_links:
                print u'{0} -> {1} {2}'.format(title, url, tags)

            for (title, url, tags) in article_data.internal_links:
                print u'{0} -> {1} {2}'.format(title, url, tags)


            print article_data.to_json()
            print '-' * 20



if __name__ == '__main__':
    show_frontpage_articles()
    #test_sample_data()
