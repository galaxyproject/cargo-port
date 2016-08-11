#!/bin/bash
GIT_REMOTE=$(git remote -v | grep origin | grep fetch | sed 's/^origin\s*//g;s/ .*//g')
# Add a second remote since we can't seem to fetch master normally
git remote add origin2 $GIT_REMOTE
# Fetch from it
git fetch --quiet origin2
# And diff against that
git diff origin2/master urls.tsv | grep -v '^+++' | grep '^+' | galaxy-cachefile-external-validator
