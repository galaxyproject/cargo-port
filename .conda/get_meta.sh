#!/bin/sh
set -ex

DIRECTORY=./bioconda-recipes

if [ -d "$DIRECTORY" ]; then
    cd "$DIRECTORY"
    git pull origin master
else
    git clone https://github.com/bioconda/bioconda-recipes.git
    cd bioconda-recipes
fi
git log --name-only --pretty="" --since="2 months ago" | grep -E '^recipes/.*/meta.yaml'
