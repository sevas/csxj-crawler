__author__ = 'sevas'

from datetime import datetime
import json



def make_dict_keys_str(a_dict):
    items = [(str(k), v) for (k, v) in a_dict.items()]
    return dict(items)



class ProviderStats(object):

    def __init__(self, n_articles, n_errors, n_dumps, n_links, start_date, end_date):
        self.n_articles = n_articles
        self.n_errors = n_errors
        self.n_dumps =  n_dumps
        self.n_links = n_links
        self.start_date = start_date
        self.end_date = end_date


    def to_json(self):
        attributes = dict(self.__dict__)

        d1, d2 = attributes['start_date'], attributes['end_date']
        attributes['start_date'] = d1.strftime('%Y-%m-%dT%H:%M:%S')
        attributes['end_date'] = d2.strftime('%Y-%m-%dT%H:%M:%S')

        return json.dumps(attributes)


    @classmethod
    def load_from_file(cls, filename):
        """
        """
        with open(filename, 'r') as f:
            json_content = f.read()
            attrs = json.loads(json_content)

            # get the dates in string form
            d1_s, d2_s = attrs['start_date'], attrs['end_date']
            # make datetime objects from them
            attrs['start_date'] = datetime.strptime(d1_s, '%Y-%m-%dT%H:%M:%S')
            attrs['end_date'] = datetime.strptime(d2_s, '%Y-%m-%dT%H:%M:%S')

            attrs = make_dict_keys_str(attrs)
            return cls(**attrs)


    def save_to_file(self, stats_filename):
        with open(stats_filename, 'w') as f:
            f.write(self.to_json())


    @classmethod
    def make_init_instance(cls):
        return cls(0, 0, 0, 0, datetime.today(), datetime.today())