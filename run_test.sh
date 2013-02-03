#!/bin/sh

PYTHONPATH=.
nosetests $* --with-color -s --doctest-tests --with-doctest  csxj tests
