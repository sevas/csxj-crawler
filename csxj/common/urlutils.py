import urlparse


def get_netloc_domain(netloc):
    """
    extracts the domain from a netloc

    Example:
    >>> get_netloc_domain("www.google.com")
    'google.com'

    >>> get_netloc_domain("blog.politics.cnn.com")
    'cnn.com'

    >>> get_netloc_domain("google.com")
    'google.com'

    """
    return '.'.join(netloc.split('.')[-2:])



def is_on_same_domain(url, domain):
    """
    Returns whether a url points to a page hosted on the given domain.

    The domain is the last two parts of a netloc.
    e.g.

    >>> is_on_same_domain('https://www.google.com/#hl=en&sclient=psy-ab&q=domain+name', 'google.com')
    True
    >>> is_on_same_domain('http://blog.politics.cnn.com', 'cnn.com')
    True
    >>> is_on_same_domain('http://www.google.com', 'google.be')
    False
    """


    parsed = urlparse.urlparse(url)
    scheme, netloc, path, params, query, fragment = parsed

    url_domain = get_netloc_domain(netloc)
    return url_domain == domain
