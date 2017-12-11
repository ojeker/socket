#!/bin/sh

CURDIR=$PWD

cd /Users/jeklin/Documents/python/venv/lint
pwd
source bin/activate lint

cd $CURDIR
pwd

pylint ccc_server output-format=parseable