#!/bin/bash
set -ex

if hash conda 2>/dev/null; then
    echo "Conda already installed"
else
    rm -rf $CONDA_INSTALLATION_PATH
    wget --no-clobber --continue https://repo.anaconda.com/miniconda/${CONDA_VERSION_TO_INSTALL}-Linux-x86_64.sh
    bash ${CONDA_VERSION_TO_INSTALL}-Linux-x86_64.sh -b -p $CONDA_INSTALLATION_PATH || echo "Conda already installed"
    echo $PATH $CONDA_INSTALLATION_PATH
    conda install -y conda-build
fi
