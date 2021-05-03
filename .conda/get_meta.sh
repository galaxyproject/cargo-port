#!/bin/sh
set -ex

DIRECTORY=./bioconda-recipes

if [ -d "$DIRECTORY" ]; then
    cd "$DIRECTORY"
    git pull origin master > /dev/null
else
    git clone --quiet https://github.com/bioconda/bioconda-recipes.git
    cd bioconda-recipes
fi

# Set $RECIPE to only get meta for a specific recipe, useful for testing/development.
if [ -n "$RECIPE" ]; then
    meta="recipes/${RECIPE}/meta.yaml"
    if [ -f "$meta" ]; then
        echo "$meta"
        exit 0
    fi
    echo "ERROR: no meta.yaml for ${RECIPE}" >&2
    exit 1
fi

# We are not running regularly enough to do this.
# Were we running this more regularly it (will?) make sense.
#git log --name-only --pretty="" --since="2 months ago" | grep -E '^recipes/.*/meta.yaml'
# Thus we fall back to worst case, whole of bioconda.
find -mindepth 3 -maxdepth 3 -name 'meta.yaml'
