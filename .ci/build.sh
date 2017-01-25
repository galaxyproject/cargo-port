#!/bin/bash
set -ex

## Cargo port
git fetch master
git diff master
python setup.py build
python setup.py install
galaxy-cachefile-validator urls.tsv
