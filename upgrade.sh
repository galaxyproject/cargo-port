#!/bin/bash
set -x
# Cleanup old hashes
find . -name 'SHA256SUM.txt' -exec rm '{}' \;
# Create appropriate folders
cat urls.tsv | awk -F'\t' '(NR>1){print "mkdir -p "$1";"}' | bash
# Update the individual files.
cat urls.tsv | awk -F'\t' '(NR>1){a=$1"_"$2"_"$3"_"$4$6; print "echo \""$7"  \""a" >> "$1"/SHA256SUM.txt"}' | bash
