#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
from datetime import datetime
from scrapy.item import Item, Field
import urlparse
import codecs
from csxj.common.tagging import tag_URL, classify_and_tag, make_tagged_url, TaggedURL
from csxj.db.article import ArticleData
from common.utils import fetch_html_content, fetch_rss_content, make_soup_from_html_content
from common.utils import remove_text_formatting_markup, extract_plaintext_urls_from_text
from common import constants