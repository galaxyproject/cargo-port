#!/usr/bin/env python
import os
import sys
import subprocess
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


with open(sys.argv[1], 'r') as handle:
    print """<!DOCTYPE html><html><head><title>Galaxy Package
    Cache</title></head><body><h1>Galaxy Package Cache</h1><p>This package cache serves to
    preserve packages permanently. Please see our <a
    href="https://github/...">Github Repository</a> for more
    information. You can use the following command to download packages from this repository:
    <pre>curl --silent https://raw.githubusercontent.com/bgruening/gsl/master/gsl.py | python - --package_id augustus_3_1</pre></p><h1>Cached
    URLs</h1><table><thead><tr><th>sha256sum</th><th>URL</th><th>Comment</th></tr></thead><tbody>"""
    retcode = 0
    for line in handle:
        if line.startswith('#'):
            continue

        data = line.split('\t')
        (id, url, sha, alt_url) = data[0:4]
        print """<tr><td>{sha}</td><td><a href="{sha}">Link</a></td><td>{id}</td></tr>""".format(sha=sha, url=url, id=id)
        if os.path.exists(sha) or alt_url.strip():
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
