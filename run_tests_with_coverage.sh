#!/bin/sh

rm -rf  coverage/
PYTHONPATH=.
nosetests $* --with-color -s --doctest-tests --with-doctest  --with-coverage --cover-html --cover-html-dir=./coverage --cover-package=csxj csxj tests
