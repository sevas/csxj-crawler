import os, os.path
from datetime import datetime, time


def get_subdirectories(parent_dir):
    """
    Yields a list of directory names. Filter out anything that is not a directory
    """
    return [d for d in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, d))]



def make_time_from_string(time_string):
    """
    Converts  a string-formatted time ('HH.MM.SS') into a datetime.time object

    For example:

    >>> make_time_from_string('22:06:10')
    datetime.time(22, 6, 10)
    """
    h, m, s = [int(i) for i in time_string.split('.')]
    return time(h, m ,s)



def make_date_from_string(date_string):
    """
    Converts a string-formatted date ('YYYY-MM-DD') into a datetime.datetime object

    For example:

    >>> make_date_from_string('2011-04-30')
    datetime.datetime(2011, 4, 30, 0, 0)
    """
    return datetime.strptime(date_string, '%Y-%m-%d')



def make_date_time_from_string(date_string, time_string):
    return make_date_from_string(date_string), make_time(time_string)



def get_latest_hour(hour_directory_names):
    """
    From a list of string-formatted hours ('HH.MM.SS'), returns the latest hour (also in string form).

    For example:
    
    >>> get_latest_hour(['12.00.10', '21.00.00', '01.00.30'])
    '21.00.00'

    """
    l = [(make_time_from_string(time_string), time_string) for time_string in hour_directory_names]
    return max(l, key=lambda x: x[0])[1]



def get_latest_day(day_directory_names):
    """
    From a list of string-formatted dates ('YYYY-MM-DD'), returns the latest dat (also in string form)

    For example:

    >>> get_latest_day(['2011-04-30', '2011-09-18', '2011-01-01'])
    '2011-09-18'
    """
    l = [(make_date_from_string(date_string), date_string) for date_string in day_directory_names]
    last_day = max(l, key=lambda x: x[0])[1]
    return last_day
