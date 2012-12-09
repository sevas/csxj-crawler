import urlparse
import urllib
TWITTER_WIDGET_URL = "widgets.twimg.com"


def is_twitter_widget_url(url):
    _, netloc, _, _, _, _  = urlparse.urlparse(url)
    return netloc == TWITTER_WIDGET_URL


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


def build_tagged_url(widget_type, param ):
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



if __name__=="__main__":
    script_content = """
new TWTR.Widget({
  version: 2,
  type: 'search',
  search: '#RemplaceLetitreDunFilmParBelfius',
  interval: 30000,
  title: '#RemplaceLetitreDunFilmParBelfius',
  subject: 'Belfius',
  width: 400,
  height: 250,
  theme: {
    shell: {
      background: '#8f158f',
      color: '#ffffff'
    },
    tweets: {
      background: '#ffffff',
      color: '#444444',
      links: '#8f158f'
    }
  },
  features: {
    scrollbar: true,
    loop: false,
    live: true,
    behavior: 'default'
  }
}).render().start();
        """

    script_content_user = """
    new TWTR.Widget({  version: 2,  type: "profile",rpp: 15,  interval: 30000,  title: "",  subject: "",  width: "auto",  height: 350,  theme: {      shell: {          background: "#559abc",          color: "#ffffff"      },      tweets: {         background: "#ffffff",          color: "#444444",       links: "#1985b5"      }  },  features: {      scrollbar: false,       loop: true,     live: true,     behavior: "all"  }}).render().setUser('@oscarmayer').start();
    """


    print get_widget_type(script_content_user)
    print get_widget_type(script_content)