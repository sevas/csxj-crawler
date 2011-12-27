"""
Bunch of utility functions to access the data in the json database.
Not meant to be an API just yet.

Directory structure is the following:

- A content provider has a list of subdirectories, one per day (format: YYYY-DD-MM)
- Each day has a list of timed batched (usually, one batch per hour)
- Each batch contains an 'articles.json' file (processed data), as well as a raw_data directory.
- A 'raw_data' directory contains a list of html files. 'The references.json' file is the mapping between
  original URLs and the files on disk
- At the top level, the content provider directory also has a 'stats.json' file. This file gets updated
  everytime the db gets updated. It contains inforamation about the number of articles, links and errors
  for this provider

Things should look like this:

- provider1
  - stats.json
  - YYYY-MM-DD
    - HH.MM.SS
        - articles.json
        - raw_data
            - references.json
            - 0.html
            - 1.html
            - ...

"""

import os, os.path
from datetime import time, datetime
from itertools import chain
import json

from csxj.datasources.common.article import ArticleData
from csxj.providerstats import ProviderStats

import utils






