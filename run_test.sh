#!/bin/sh

PYTHONPATH=.
nosetests -v  -s --doctest-tests --with-doctest --with-color csxj csxj/db csxj/datasources csxj/common tests scripts