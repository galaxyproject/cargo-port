#!/usr/bin/python

from urlparse import urlparse
import urllib
import urllib2
import click
import os
import hashlib

@click.command()
@click.option('--package_id', help='Package ID', required=True)
@click.option('--download_location', default='./',
              help='Location for the downloaded file')
def get(package_id, download_location):
    package_found = False
    for line in urllib2.urlopen('https://github.com/bgruening/gsl/raw/master/packages.list'):
        if line.strip() and not line.startswith('#'):
            iid, url, checksum = line.split('\t')
            if iid.strip() == package_id.strip():
                package_found = True
                pkg_name = urlparse(url).path.split('/')[-1]
                storage_path = os.path.join(download_location, pkg_name)
                urllib.urlretrieve (url, storage_path)
                download_checksum = hashlib.sha256( open(storage_path, 'rb').read() ).hexdigest()
                if checksum.strip() != download_checksum:
                    print 'Checksum does not match, something seems to be wrong.\n'
                    print checksum, '\t(expected)'
                    print download_checksum, '\t(downloaded)'
                else:
                    print 'Download sucessfull for %s.' % (pkg_name)
    if not package_found:
        print 'Package (%s) could not be found in this servive.' % (package_id)

if __name__ == '__main__':
    get()
