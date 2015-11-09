#!/usr/bin/env python
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

def yield_packages(handle, meta=False, retcode=None):
    for lineno, line in enumerate(handle):
        if line.startswith('#'):
            continue
        try:
            data = line.split('\t')
            keys = ['id', 'version', 'platform', 'arch', 'url', 'sha', 'size',
                    'alt_url', 'comment']
            if len(data) != len(keys):
                log.error('[%s] data has wrong number of columns. %s != %s', lineno + 1, len(data), len(keys))
                retcode = 1

            ld = {k: v for (k, v) in zip(keys, line.split('\t'))}

            if meta:
                yield ld, lineno, line, retcode
            else:
                yield ld
        except Exception, e:
            log.error(str(e))
