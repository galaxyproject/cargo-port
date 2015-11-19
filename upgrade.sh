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


rm 05bc9fc1bbb32cfc885f558f027e3e8a3311118318b46590d9135affbe6320a8 210656d7e5f98a73b5c3e83444b3a2344bf1868ce06dc977aef030c0deeef083 6707b149d485b849d3c313dc5a73d3441fb0d18b4111f2289b488d0b0667269c 69b00985c84e6633cc2e518914436ce55666cc10d1edf15ee442758d9f8d5219 bcc95d95efdce39afea0a3d83d00b83006457977888d1eaee76b4659d2f258dd c7648f76d49ae378ef4c0758950441be010e51064c877ff0ec18d475b3965814
