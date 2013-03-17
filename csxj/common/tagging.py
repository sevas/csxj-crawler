from collections import namedtuple
import urlparse

from urlutils import is_on_same_domain, get_netloc_domain
TaggedURL = namedtuple('TaggedURL', 'URL title tags')


def make_tagged_url(url, title, tags):
    return TaggedURL(URL=url, title=title, tags=tags)


def tag_URL((url, title), tags):
    return TaggedURL(URL=url, title=title, tags=tags)


def classify_and_tag(url, own_netloc, associated_sites):
    """

    >>> classify_and_tag("http://www.foo.org", "foo.org", {})
    set(['internal', 'internal site'])

    >>> classify_and_tag("http://www.foo.org/bar", "foo.org", {})
    set(['internal', 'internal site'])

    >>> classify_and_tag("http://www.baz.org/bar", "foo.org", {})
    set(['external'])

    >>> classify_and_tag("/bar/baz", "foo.org", {})
    set(['internal'])

    >>> classify_and_tag("#anchor", "foo.org", {})
    set(['internal', 'anchor'])

    >>> classify_and_tag("//pokey.com", "foo.org", {})
    set(['external'])
    """
    tags = []
    parsed = urlparse.urlparse(url)
    scheme, netloc, path, params, query, fragment = parsed
    if netloc:
        if netloc == own_netloc:
            tags.append('internal')
        else:
            if netloc in associated_sites:
                tags.extend(associated_sites[netloc])
            elif is_on_same_domain(url, get_netloc_domain(own_netloc)):
                tags.append('internal site')
                tags.append('internal')
            else:
                tags.append('external')
    elif not (scheme or netloc or path or params or query) and fragment:
        if url.startswith('#'):
            tags = ['internal', 'anchor']
    elif url:
        if url.startswith('/'):
            tags = ['internal']
        else:
            tags = ['external']
    return set(tags)


def tag_same_owner(url, same_owner_sites):
    tags = []
    parsed = urlparse.urlparse(url)
    _, netloc, _, _, _, _ = parsed
    if netloc:
        for site in same_owner_sites:
            if netloc.lower().endswith(site):
                tags.append('same owner')

    return set(tags)


def update_tagged_urls(all_links, same_owner_sites):

    updated_tagged_urls = []

    for url, title, tags in all_links:
        additional_tags = tag_same_owner(url, same_owner_sites)
        tags.update(additional_tags)
        updated_tagged_urls.append(make_tagged_url(url, title, tags))
    return updated_tagged_urls


def print_taggedURLs(tagged_urls, size=100):
    print "Count: ", len(tagged_urls)
    for tagged_url in tagged_urls:
        fmt = u"{{0:{0}}} ({{1:{0}}}) \t {{2}}".format(size)
        print(fmt.format(tagged_url.title[:size], tagged_url.URL[:size], tagged_url.tags))
