# Cleanup old hashes
#rm -f *.sha256sum
# Generate new, single file.
#cat urls.tsv | awk -F'\t' '(NR>1){print $6"  "$1"-"$2"-"$3"-"$4}' > cpc.sha256sum

# Renaming files into folders.
echo 'set -x' > mkdir.txt
cat urls.tsv | awk -F'\t' '(NR>1){a=$1"_"$2"_"$3"_"$4".tar.gz"; print "mkdir -p "$1"; mv "$7" "$1"/"a}' >> mkdir.txt
cat mkdir.txt | bash

# Remove existing SHA256SUMs files.
find . -name 'SHA256SUMS' -exec rm '{}' \;

# Update the individual files.
echo 'set -x' > mv.txt
cat urls.tsv | awk -F'\t' '(NR>1){a=$1"_"$2"_"$3"_"$4".tar.gz"; print "echo "$7" >> "$1"/SHA256SUMS"}' >> mv.txt
cat mv.txt | bash
