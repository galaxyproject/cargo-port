#!/bin/sh


DIRECTORY=./bioconda-recipes

if [ -d "$DIRECTORY" ]; then
    cd "$DIRECTORY"
    git pull origin master > /dev/null
else
    git clone --quiet https://github.com/bioconda/bioconda-recipes.git
    cd bioconda-recipes
fi
git log --name-only --pretty="" --since="2 days ago" | grep -E '^recipes/.*/meta.yaml'
