#!/bin/bash
set -ex
# Cleanup old hashes
find . -name 'SHA256SUM.txt' -exec rm '{}' \;

# Renaming files into folders.
#echo 'set -x' > mkdir.txt
cat urls.tsv | awk -F'\t' '(NR>1){print "mkdir -p "$1";"}' | bash
#cat mkdir.txt | bash

# Remove existing SHA256SUMs files.
find . -name 'SHA256SUMS' -exec rm '{}' \;

# Update the individual files.
cat urls.tsv | awk -F'\t' '(NR>1){a=$1"_"$2"_"$3"_"$4$6; print "echo \""$7"  \""a" >> "$1"/SHA256SUM.txt"}' | bash

# Remove empty directories
#find . -type d -empty -not -wholename '*/.git/*' -exec rmdir '{}' \;
