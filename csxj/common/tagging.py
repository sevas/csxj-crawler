from collections import namedtuple
import urlparse

TaggedURL = namedtuple('TaggedURL', 'URL title tags')




def make_tagged_url(url, title, tags):
    return TaggedURL(URL=url, title=title, tags=tags)


def tag_URL((url, title), tags):
    return TaggedURL(URL=url, title=title, tags=tags)


def classify_and_tag(url, own_netlog, associated_sites):
    """
    """
    tags = []
    parsed = urlparse.urlparse(url)
    scheme, netloc, path, params, query, fragment = parsed
    if netloc:
        if netloc == own_netlog:
            tags = ['internal']
        else:
            if netloc in associated_sites:
                tags = associated_sites[netloc]
            else:
                tags = ['external']
    elif url:
        tags = ['internal']

    return set(tags)

