#!/bin/bash
CPC_HOST=depot@orval.galaxyproject.org
CPC_DIR=/srv/nginx/depot.galaxyproject.org/root/software

rsync -avr . $CPC_HOST:$CPC_DIR/

ssh $CPC_HOST "cd $CPC_DIR && sh upgrade.sh"
ssh $CPC_HOST "cd $CPC_DIR && python bin/process_urls.py urls.tsv > api-tcp.json"
rsync $CPC_HOST:$CPC_DIR/report.xml report-tcp.xml
ssh $CPC_HOST "cd $CPC_DIR && python bin/process_urls.py urls-bioconda.tsv > api-bioconda.json"
rsync $CPC_HOST:$CPC_DIR/report.xml report-bioconda.xml
ssh $CPC_HOST "cd $CPC_DIR && python bin/merge_apis.py api-tcp.json tcp api-bioconda.json bioconda > api-bioconda.json"
