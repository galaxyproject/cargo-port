#!/usr/bin/python
from urlparse import urlparse
import urllib
import urllib2
import click
import os
import hashlib
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

PACKAGE_SERVER = 'https://depot.galaxyproject.org/software/'


def yield_packages(handle):
    """Copy this between python scripts"""
    for line in enumerate(handle):
        if line.startswith('#'):
            continue
        try:
            keys = ['id', 'version', 'platform', 'arch', 'url', 'sha', 'size',
                    'alt_url', 'comment']
            ld = {k: v for (k, v) in zip(keys, line.split('\t'))}
            yield ld
        except Exception, e:
            log.error(str(e))


@click.command()
@click.option('--package_id', help='Package ID', required=True)
@click.option('--download_location', default='./',
              help='Location for the downloaded file')
def get(package_id, download_location):
    package_found = False
    for ld in yield_packages(
        urllib2.urlopen(PACKAGE_SERVER + 'urls.tsv')):
        # TODO: check platform/architecture, failover to all if available?
        # iid, version, platform, architecture, upstream_url, checksum, alternate_url = line.split('\t')
        if ld['id'] == package_id.strip() and ld['platform']== 'src':
            package_found = True
            # I worry about this being unreliable. TODO: add target filename column?
            pkg_name = urlparse(ld['upstream_url']).path.split('/')[-1]
            storage_path = os.path.join(download_location, pkg_name)
            if len(ld['alternate_url'].strip()):
                url = ld['alternate_url']
            else:
                url = PACKAGE_SERVER + ld['checksum']
            urllib.urlretrieve(url, storage_path)
            download_checksum = hashlib.sha256(open(storage_path, 'rb').read()).hexdigest()
            if ld['checksum'] != download_checksum:
                print ('Checksum does not match, something seems to be wrong.\n'
                       '{expected}\t(expected)\n{actual}\t(downloaded)').format(
                           expected=ld['checksum'],
                           actual=download_checksum)
            else:
                print 'Download successful for %s.' % (pkg_name)
    if not package_found:
        print 'Package (%s) could not be found in this server.' % (package_id)

if __name__ == '__main__':
    get()
