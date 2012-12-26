#!/usr/bin/env python
# -*- coding: utf-8 -*-


def extract_url_from_iframe(iframe):
    url = iframe.get('src')
    title = url
    return url, title