#!/bin/bash
git diff master
python setup.py build
python setup.py install
galaxy-cachefile-validator urls.tsv
