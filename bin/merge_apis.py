#!/usr/bin/env python
import sys
# Conditional import to ensure we can run without non-stdlib on py2k.
if sys.version_info.major > 2:
    from builtins import zip
import json
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

data = sys.argv[1:]
merged_data = {'data': []}

for path, tag in zip(data[0::2], data[1::2]):
    with open(path, 'r') as handle:
        ldata = json.load(handle)
        for element in ldata['data']:
            element['tag'] = tag
            merged_data['data'].append(element)

json.dump(merged_data, sys.stdout)
