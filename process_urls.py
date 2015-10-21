#!/usr/bin/env python
import os
import sys
import subprocess
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

with open(sys.argv[1], 'r') as handle:
    for line in handle:
        if line.startswith('#'):
            continue

        data = line.strip().split('\t')
        sha = data[0]
        url = data[1]
        if os.path.exists(sha):
            log.info("URL exists %s", url)
        else:
            log.info("URL missing, downloading %s to %s", url, sha)
            subprocess.check_call(['wget', url, '-O', sha])

            with open(os.path.join('%s.sha256sum' % sha), 'w') as handle:
                handle.write("%s  %s" % (sha, sha))

            # Check sha256sum of download
            try:
                subprocess.check_call(['sha256sum', '-c', '%s.sha256sum' % sha])
            except subprocess.CalledProcessError:
                log.error("File has bad hash! Refusing to serve this to end users.")
                os.unlink(sha)
