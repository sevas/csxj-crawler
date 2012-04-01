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
            if is_on_same_domain(url, get_netloc_domain(own_netloc)):
                tags.append('internal site')
            else:
                tags.append('external')
    elif url:
        # url starting with '/'
        tags = ['internal']

    return set(tags)

