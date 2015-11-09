# Cleanup old hashes
rm -f *.sha256sum
# Generate new, single file.
cat urls.tsv | awk -F'\t' '(NR>1){print $6"  "$1"-"$2"-"$3"-"$4}' > cpc.sha256sum
