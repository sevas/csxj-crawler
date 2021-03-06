import urlparse
import urllib
from csxj.common import tagging

TWITTER_WIDGET_NETLOC="widgets.twimg.com"
TWITTER_WIDGET_SCRIPT_URL="http://widgets.twimg.com/j/2/widget.js"

def is_twitter_widget_url(url):
    _, netloc, _, _, _, _ = urlparse.urlparse(url)
    return netloc == TWITTER_WIDGET_NETLOC


def grep_line(text, word):
    lines = text.split(",")
    grepped = [l for l in lines if word in l]
    if grepped:
        return grepped[0]
    else:
        return None


def extract_parameter(script_content):
    grepped = grep_line(script_content, "type")
    if grepped:
        return grepped.split(':')[1].rstrip(",'\"").lstrip(" '\"")
    else:
        return None


def extract_user_name(script_content):
    return script_content.split(".setUser")[1].split(".")[0].strip("()'")


def extract_query(script_content):
    grepped = grep_line(script_content, "search:")
    if grepped:
        return grepped.split(':')[1].rstrip(",'\"").lstrip(" '\"")
    else:
        return None


def build_tagged_url(widget_type, param):
    if widget_type == 'search':
        title = u"Twitter widget: search for {0}".format(param)
        url = "https://twitter.com/search?{0}".format(urllib.urlencode(dict(q=param)))
        tags = set(["twitter widget", "twitter search"])
        return title, url, tags
    elif widget_type == 'profile':
        title = u"Twitter widget: {0}'s twitter profile".format(param)
        if param.startswith("@"):
            param = param[1:]
        url = "https://twitter.com/{0}".format(param)
        tags = set(["twitter widget", "twitter profile"])
        return title, url, tags


def get_widget_type(script_content):
    script_content = script_content.replace("\n", "").strip()
    if script_content.startswith("new TWTR.Widget"):
        type_value = extract_parameter(script_content)
        if type_value:
            if type_value == 'profile':
                return build_tagged_url(type_value, extract_user_name(script_content))
            elif type_value == 'search':
                return build_tagged_url(type_value, extract_query(script_content))
            else:
                raise ValueError("Unknown TWTR.Widget type: {0}".format(type_value))
        else:
            raise ValueError("No type line was found in the TWTR.Widget script")
    else:
        raise ValueError("Detected script is not TWTR.Widget")



def extract_rendered_tweet(paragraph, netloc, internal_site):
    tagged_urls = []
    tweets = paragraph.findAll(attrs = {"class" : "twitter-tweet"})
    if tweets:
        for tweet in tweets:
            links = tweet.findAll("a")
            for link in links :
                if link.get("data-datetime"):
                    url = link.get("href")
                    tags = tagging.classify_and_tag(url, netloc, internal_site)
                    tags.add('embedded media')
                    tags.add('tweet')
                    tagged_urls.append(tagging.make_tagged_url(url, url, tags))

    return tagged_urls




