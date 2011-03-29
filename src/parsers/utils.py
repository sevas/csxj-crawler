import urllib


def fetch_content_from_url(url):
    response = urllib.urlopen(url)
    return response.read()


def fetch_html_content(url):
    return fetch_content_from_url(url)


def fetch_html_content_with_redirection(url):
    pass


def fetch_rss_content(url):
    return fetch_content_from_url(url)


