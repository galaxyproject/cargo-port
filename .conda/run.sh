#!/bin/bash
set -ex
CONDA_INSTALLATION_PATH=/tmp/anaconda
export CONDA_INSTALLATION_PATH
export PATH=$CONDA_INSTALLATION_PATH/bin:$PATH

./.conda/install.sh
./.conda/get_meta.sh | sort -u > meta_files.list
python ./.conda/get_urls.py meta_files.list linux-64
python ./.conda/get_urls.py meta_files.list osx-
python ./.conda/merge_dups.py

cat data.yml
python ./.conda/to_cargoport.py < data.yml >> urls-bioconda.tsv
