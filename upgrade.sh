# Cleanup old hashes
rm -f *.sha256sum

# Renaming files into folders.
#echo 'set -x' > mkdir.txt
#cat urls.tsv | awk -F'\t' '(NR>1){a=$1"_"$2"_"$3"_"$4".tar.gz"; print "mkdir -p "$1"; mv "$7" "$1"/"a}' >> mkdir.txt
#cat mkdir.txt | bash

# Remove existing SHA256SUMs files.
find . -name 'SHA256SUMS' -exec rm '{}' \;

# Remove empty files
find . -type f -empty -exec rm '{}' \;

# Update the individual files.
cat urls.tsv | awk -F'\t' '(NR>1){a=$1"_"$2"_"$3"_"$4".tar.gz"; print "echo \""$7"  \""a" >> "$1"/SHA256SUMS"}' | bash
