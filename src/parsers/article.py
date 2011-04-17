__author__ = 'sevas'

from collections import namedtuple

try:
    import json
except ImportError:
    import simplejson as json


TaggedURL = namedtuple('TaggedURL', 'URL title tags')


def tag_URL((url, title), tags):
    return TaggedURL(URL=url, title=title, tags=tags)


class ArticleData(object):
    """
    A glorified dict to keep the extracted metadata and content of one article.
    Has utility methods for json (de)serialization.
    """

    def __init__(self, url, title,
                 pub_date, pub_time, fetched_datetime,
                 external_links, internal_links,
                 category, author,
                 intro, content):
        """
        Boring init func.
        """
        self.url = url
        self.title = title
        self.pub_date = pub_date
        self.pub_time = pub_time
        self.fetched_datetime = fetched_datetime

        self.external_links = external_links
        self.internal_links = internal_links

        self.category = category
        self.author = author

        self.intro = intro
        self.content = content



    def to_json(self):
        """
        Converts all attributes in self.__dict__ into a json string.
        Takes care of non natively serializable objects (such as datetime).
        """
        d = dict(self.__dict__)
        # datetime, date and time objects are not json-serializable

        date = d['fetched_datetime']
        d['fetched_datetime'] = date.strftime('%Y-%m-%dT%H:%M:%S')

        pub_date, pub_time = d['pub_date'], d['pub_time']

        d['pub_date'] = pub_date.strftime('%Y-%m-%d')
        d['pub_time'] = pub_time.strftime('%H:%S')

        return json.dumps(d)



    @classmethod
    def from_json(kls, json_string):
        """
        Class method to rebuild an ArticleData object from a json string.
        Takes care of non natively deserializable objects (such as datetime).
        """
        d = json.loads(json_string)

        date_string = d['fetched_datetime']
        d['fetched_datetime'] = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')

        pub_date, pub_time = d['pub_date'],  d['pub_time']
        year, month, day = [int(i) for i in pub_date.split('-')]
        d['pub_date'] = date(year, month, day)

        h, m = [int(i) for i in pub_time.split(':')]
        d['pub_time'] = time(h, m)

        return kls(**d)
