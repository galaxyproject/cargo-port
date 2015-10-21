#!/usr/bin/env python
import os
import sys
import subprocess
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


with open(sys.argv[1], 'r') as handle:
    print """<!DOCTYPE html><html><head><title>Galaxy Package
    Cache</title></head><body><h1>About</h1><p>This package cache serves to
    preserve packages permanently. Please see our <a
    href="https://github/...">Github Repository</a> for more
    information.</p><h1>Cached
    URLs</h1><table><thead><tr><th>sha256sum</th><th>URL</th><th>Comment</th></tr></thead><tbody>"""
    retcode = 0
    for line in handle:
        if line.startswith('#'):
            continue

        data = line.strip().split('\t')
        (sha, url) = data[0:2]
        comment = data[2] if len(data) > 2 else ""
        print """<tr><td>{sha}</td><td><a href="{sha}">Link</a></td><td>{comment}</td></tr>""".format(sha=sha, url=url, comment=comment)
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
    print "</tbody></table></body></html>"
    sys.exit(retcode)
