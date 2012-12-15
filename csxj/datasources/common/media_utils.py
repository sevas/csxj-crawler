


def extract_url_from_iframe(iframe):
    url = iframe.get('src')
    title = u"__EMBEDDED_CONTENT_IFRAME__"
    return url, title