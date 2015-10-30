#!/usr/bin/env python
import sys
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def yield_packages(handle):
    """Copy this between python scripts"""
    for line in handle:
        if line.startswith('#'):
            continue
        try:
            keys = ['id', 'version', 'platform', 'arch', 'url', 'sha', 'size',
                    'alt_url', 'comment']
            ld = {k: v for (k, v) in zip(keys, line.split('\t'))}
            yield ld
        except Exception, e:
            log.error(str(e))



with open(sys.argv[1], 'r') as handle:

    print '# ' + '\t'.join(['Id', 'Version', 'Platform', 'Architecture', 'Upstream url', 'sha256sum', 'Alternate Url']),
    retcode = 0
    res = {}
    warnings = []
    for ld in yield_packages(handle):

        if ld['id'] not in res:
            res[ld['id']] = []

        res[ld['id']].append(ld)

    for x in res:
        print '\t'.join(res[x][0]),

    sys.exit(retcode)
