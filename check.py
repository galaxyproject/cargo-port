#!/usr/bin/env python
import sys
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def yield_packages(handle):
    """Copy this between python scripts"""
    for lineno, line in enumerate(handle):
        if line.startswith('#'):
            continue
        try:
            data = line.split('\t')
            keys = ['id', 'version', 'platform', 'arch', 'url', 'sha', 'size',
                    'alt_url', 'comment']
            ld = {k: v for (k, v) in zip(keys, data)}
            yield ld, lineno, line
        except Exception, e:
            log.error(str(e))


with open(sys.argv[1], 'r') as handle:
    retcode = 0
    identifiers = set()
    keys = ['id', 'version', 'platform', 'arch', 'url', 'sha', 'size',
            'alt_url', 'comment']

    for ld, lineno, line in yield_packages(handle):
        try:
            for x in keys[0:6]:
                if ld.get(x, '').strip() == '':
                    log.error("[%s] Empty %s", lineno, x)
                    retcode = 1

            if ld['platform'] not in ('linux', 'windows', 'darwin', 'src'):
                log.error("[%s] Unknown platform %s", lineno, ld['platform'])
                retcode = 1

            if ld['arch'] not in ('x32', 'x64', 'all'):
                log.error("[%s] Unknown architecture %s", lineno, ld['arch'])
                retcode = 1

            if len(ld['sha']) != 64:
                log.error("[%s] Bad checksum %s", lineno, ld['sha'])
                retcode = 1

            platform_id = (ld['id'], ld['version'], ld['platform'], ld['arch'])
            if platform_id in identifiers:
                log.error("[%s] identifier is not unique: '%s'", lineno, platform_id)
                retcode = 1
            else:
                identifiers.add(platform_id)

        except:
            log.error("[%s] Line not tabbed properly", lineno)
            retcode = 1
    sys.exit(retcode)
