#!/bin/sh

PYTHONPATH=.
nosetests $* -s --doctest-tests --with-doctest  csxj tests
