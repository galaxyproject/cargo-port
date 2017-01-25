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

# We are not running regularly enough to do this.
# Were we running this more regularly it (will?) make sense.
#git log --name-only --pretty="" --since="2 months ago" | grep -E '^recipes/.*/meta.yaml'
# Thus we fall back to worst case, whole of bioconda.
find -mindepth 3 -maxdepth 3 -name 'meta.yaml'
