#!/usr/bin/python
from urlparse import urlparse
import urllib
import urllib2
import click
import os
import hashlib
PACKAGE_SERVER = 'https://server-to-be-determined/'


@click.command()
@click.option('--package_id', help='Package ID', required=True)
@click.option('--download_location', default='./',
              help='Location for the downloaded file')
def get(package_id, download_location):
    package_found = False
    for line in urllib2.urlopen(PACKAGE_SERVER + 'urls.tsv'):
        if not line.strip() or line.startswith('#'):
            continue

        iid, platform, architecture, upstream_url, checksum, alternate_url = line.split('\t')
        # TODO: check platform/architecture, failover to all if available?
        if iid == package_id.strip() and platform == 'src':
            package_found = True
            # I worry about this being unreliable. TODO: add target filename column?
            pkg_name = urlparse(upstream_url).path.split('/')[-1]
            storage_path = os.path.join(download_location, pkg_name)
            if alternate_url.strip():
                url = alternate_url
            else:
                url = PACKAGE_SERVER + checksum
            urllib.urlretrieve(url, storage_path)
            download_checksum = hashlib.sha256(open(storage_path, 'rb').read()).hexdigest()
            if checksum != download_checksum:
                print ('Checksum does not match, something seems to be wrong.\n'
                       '{expected}\t(expected)\n{actual}\t(downloaded)').format(
                           expected=checksum,
                           actual=download_checksum)
            else:
                print 'Download successful for %s.' % (pkg_name)
    if not package_found:
        print 'Package (%s) could not be found in this server.' % (package_id)

if __name__ == '__main__':
    get()
