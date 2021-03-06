# -*- coding: utf-8 -*-
__author__ = 'sevas'

from datetime import datetime, date, time
from csxj.common.tagging import TaggedURL, make_tagged_url
import json


def count_words(some_text):
    words = some_text.split(' ')
    return len(words)


def make_dict_keys_str(a_dict):
    items = [(str(k), v) for (k, v) in a_dict.items()]
    return dict(items)


def datetime_to_string(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S')


def datetime_from_string(s):
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


def date_to_string(d):
    return d.strftime('%Y-%m-%d')


def date_from_string(s):
    year, month, day = [int(i) for i in s.split('-')]
    return date(year, month, day)


def time_to_string(t):
    if t:
        return t.strftime('%H:%S')
    else:
        return None

def time_from_string(s):
    if s:
        h, m = [int(i) for i in s.split(':')]
        return time(h, m)
    else:
        return None


def make_serializable(tagged_url):
    url, title, tags = tagged_url
    return TaggedURL(url, title, list(tags))




class ArticleData(object):
    """
    A glorified dict to keep the extracted metadata and content of one article.
    Has utility methods for json (de)serialization.
    """

    def __init__(self, url, title,
                 pub_date, pub_time, fetched_datetime,
                 links,
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

        self.links = links

        self.category = category
        self.author = author

        self.intro = intro
        self.content = content


    @property
    def other_links(self):
        return [l for l in self.links if 'internal' not in l.tags]


    @property
    def internal_links(self):
        return [l for l in self.links if 'internal' in l.tags]


    def print_summary(self):
        print 'title:', self.title
        print 'url:', self.url
        print 'publication date:', self.pub_date
        print 'publication time:', self.pub_time
        print 'fetched on:', self.fetched_datetime
        print '# other links:', len(self.other_links)
        print '# internal links:', len(self.internal_links)
        print 'category:', '/'.join(self.category)
        print 'author:', self.author
        print '# words:', count_words(''.join(self.content))
        print 'intro:', self.intro


    def to_json(self):
        """
        Converts all attributes in self.__dict__ into a json string.
        Takes care of non natively serializable objects (such as datetime).
        """
        d = dict(self.__dict__)

        # datetime, date and time objects are not json-serializable
        fetched_datetime = d['fetched_datetime']
        d['fetched_datetime'] = datetime_to_string(fetched_datetime)

        pub_date, pub_time = d['pub_date'], d['pub_time']
        d['pub_date'] = date_to_string(pub_date)
        d['pub_time'] = time_to_string(pub_time)

        links = d['links']
        d['links'] = [make_serializable(tagged_url) for tagged_url in links]

        return json.dumps(d)



    @classmethod
    def from_json(cls, json_string):
        """
        Class method to rebuild an ArticleData object from a json string.
        Takes care of non natively deserializable objects (such as datetime).
        """
        d = json.loads(json_string)

        date_string = d['fetched_datetime']
        d['fetched_datetime'] = datetime_from_string(date_string)

        pub_date, pub_time = d['pub_date'],  d['pub_time']
        d['pub_date'] = date_from_string(pub_date)
        d['pub_time'] = time_from_string(pub_time)

        links = d['links']
        tagged_urls = [make_tagged_url(url, title, set(tags)) for (url, title, tags) in links]
        d['links'] = tagged_urls

        d = make_dict_keys_str(d)
        return cls(**d)
