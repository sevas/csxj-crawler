# -*- coding: utf-8 -*-
"""
Link extraction test suite for lalibre.py
"""

import os
from nose.tools import eq_

from csxj.common.tagging import make_tagged_url
from csxj.datasources import sudinfo

from csxj_test_tools import assert_taggedURLs_equals

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', sudinfo.SOURCE_NAME)


class TestSudinfoLinkExtraction(object):
    pass