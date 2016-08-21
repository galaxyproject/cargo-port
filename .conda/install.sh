#!/bin/bash
set -e

CONDA_INSTALLATION_PATH=$HOME/anaconda

if hash conda 2>/dev/null; then
    echo "Conda already installed"
else
    date "Installing Conda"
    curl -O https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
    bash Miniconda2-latest-Linux-x86_64.sh -b -p CONDA_INSTALLATION_PATH/anaconda
    export PATH=CONDA_INSTALLATION_PATH/anaconda/bin:$PATH
fi

if hash conda 2>/dev/null; then
    echo "Conda build already installed"
else
    date "Installing conda-build"
    conda install -y conda-build
fi


