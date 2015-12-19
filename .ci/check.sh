#!/bin/bash
set -x

GIT_REMOTE=$(git remote -v | grep origin | grep fetch | sed 's/^origin\s*//g;s/ .*//g')
# Add a second remote since we can't seem to fetch master normally
git remote add origin2 $GIT_REMOTE
# Fetch from it
git fetch origin2
# And diff against that
git diff origin2/master urls.tsv | grep -v '^+++' | grep '^+' | awk -F'\t' '{print "queryHash=$(curl -L --silent "$5" | sha256sum - | sed \"s/  .*//g\" ); userHash="$7"; if [ \"$queryHash\" == \"$userHash\" ]; then echo \"Valid hash\"; else echo \"Invalid hash for \""$5"; exit 1; fi;"}' | bash
