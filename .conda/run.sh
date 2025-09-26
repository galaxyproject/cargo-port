#!/bin/bash
set -ex

export CONDA_INSTALLATION_PATH=/tmp/anaconda
export PATH=$CONDA_INSTALLATION_PATH/bin:$PATH
export CONDA_VERSION_TO_INSTALL=25.3.1-0

./.conda/install.sh
./.conda/get_meta.sh | sort -u > meta_files.list
CONDA_SUBDIR=linux-64 python ./.conda/get_urls.py meta_files.list linux-64
CONDA_SUBDIR=osx- python ./.conda/get_urls.py meta_files.list osx-
python ./.conda/merge_dups.py

python ./.conda/to_cargoport.py < data.yml > urls-bioconda.tsv
