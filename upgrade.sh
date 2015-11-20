#!/bin/bash
set -ex
# Cleanup old hashes
rm -f *.sha256sum

# Renaming files into folders.
#echo 'set -x' > mkdir.txt
cat urls.tsv | awk -F'\t' '(NR>1){print "mkdir -p "$1";"}' | bash
#cat mkdir.txt | bash

# Remove existing SHA256SUMs files.
find . -name 'SHA256SUMS' -exec rm '{}' \;

# Update the individual files.
cat urls.tsv | awk -F'\t' '(NR>1){a=$1"_"$2"_"$3"_"$4".tar.gz"; print "echo \""$7"  \""a" >> "$1"/SHA256SUMS"}' | bash

ln -s /srv/nginx/depot.galaxyproject.org/root/package/darwin/x86_64/meme/meme-4.10.0_4-Darwin-x86_64.tar.gz /srv/nginx/depot.galaxyproject.org/root/software/meme/meme_4.10.0.4_darwin_x64.tar.gz
