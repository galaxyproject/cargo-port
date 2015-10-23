#!/usr/bin/env python
import sys
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


with open(sys.argv[1], 'r') as handle:
    print '# ' + '\t'.join(['Id', 'Version', 'Platform', 'Architecture', 'Upstream url', 'sha256sum', 'Alternate Url']),
    retcode = 0
    res = {}
    warnings = []
    for line in handle:
        if line.startswith('#'):
            continue

        data = line.split('\t')
        id = data[0]

        if id not in res:
            res[id] = []

        res[id].append(data)

    for x in res:
        print '\t'.join(res[x][0]),

    sys.exit(retcode)
