#!/usr/bin/env python

def yield_packages(handle):
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

def yield_packages2(handle,retcode):
    for lineno, line in enumerate(handle):
        if line.startswith('#'):
            continue
        try:
            data = line.split('\t')
            keys = ['id', 'version', 'platform', 'arch', 'url', 'sha', 'size',
                    'alt_url', 'comment']
            if len(data) != len(keys):
                log.error('[%s] data has wrong number of columns. %s != %s', lineno + 1, len(data), len(keys))
            ld = {k: v for (k, v) in zip(keys, data)}
            yield ld, lineno, line, retcode
        except Exception, e:
            log.error(str(e))