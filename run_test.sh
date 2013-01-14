#!/bin/sh

PYTHONPATH=.
nosetests $* -s --doctest-tests --with-doctest --with-color csxj tests
