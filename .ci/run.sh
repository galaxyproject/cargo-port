#!/bin/bash
set -ex
CPC_HOST=depot@orval.galaxyproject.org
CPC_DIR=/srv/nginx/depot.galaxyproject.org/root/software
rm -f report*.xml

# Update the index.html from the template
cat index.html.tpl | sed "s|BUILD_TAG_GOES_HERE|Build <a href='${BUILD_URL}'>#${BUILD_NUMBER}</a>|" > index.html

# Copy over all changed files to the target
rsync -avr --exclude bioconda-recipes --exclude .git . $CPC_HOST:$CPC_DIR/

# Any one-time upgrades
ssh $CPC_HOST "cd $CPC_DIR && sh upgrade.sh"

# Process URLs and copy back report
ssh $CPC_HOST "cd $CPC_DIR && PYTHONPATH=. python bin/process_urls.py urls.tsv > api-tcp.json"
rsync $CPC_HOST:$CPC_DIR/report.xml report-tcp.xml

# Run conda
bash .conda/run.sh
# Update now that we have a urls-bioconda
rsync -avr urls-bioconda.tsv $CPC_HOST:$CPC_DIR/urls-bioconda.tsv

# Process URLs and copy back report
ssh $CPC_HOST "cd $CPC_DIR && python bin/process_urls.py urls-bioconda.tsv > api-bioconda.json"
rsync $CPC_HOST:$CPC_DIR/report.xml report-bioconda.xml

# Merge the APIs on the remote end. Allows us to see both TCP + bioconda packages together.
ssh $CPC_HOST "cd $CPC_DIR && python bin/merge_apis.py api-tcp.json tcp api-bioconda.json bioconda > api.json"

# Lastly, do a dry-run verification
ssh $CPC_HOST "cd $CPC_DIR && python bin/verify.py urls.tsv dryrun"
rsync $CPC_HOST:$CPC_DIR/report.xml report-tcp-verify.xml
#ssh $CPC_HOST "cd $CPC_DIR && python bin/verify.py urls-bioconda.tsv dryrun"
#rsync $CPC_HOST:$CPC_DIR/report.xml report-bio-verify.xml
