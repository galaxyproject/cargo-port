#!/bin/bash
set -e

./.conda/install.sh
./.conda/get_meta.sh > meta_files.list
python ./.conda/get_urls.py meta_files.list

cat data.yml
