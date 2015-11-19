# Cleanup old hashes
#rm -f *.sha256sum
# Generate new, single file.
#cat urls.tsv | awk -F'\t' '(NR>1){print $6"  "$1"-"$2"-"$3"-"$4}' > cpc.sha256sum

# Renaming files into folders.
cat urls.tsv | head  | awk -F'\t' '(NR>1){a=$1"_"$2"_"$3"_"$4".tar.gz"; print "mkdir -p "$1"; mv "$6" "$1"/"a}' | bash

# Remove existing SHA256SUMs files.
find . -name 'SHA256SUMS' -exec rm '{}' \;

# Update the individual files.
cat urls.tsv | head  | awk -F'\t' '(NR>1){a=$1"_"$2"_"$3"_"$4".tar.gz"; print "echo "$6" >> "$1"/SHA256SUMS"}' | bash
