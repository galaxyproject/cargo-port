#!/usr/bin/env python

from future import standard_library
standard_library.install_aliases()
from builtins import str
import click
import hashlib
from io import StringIO
import logging
import os
import urllib.request, urllib.parse, urllib.error

from cargoport.utils import yield_packages, package_name, PACKAGE_SERVER, get_url
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


@click.command()
@click.option('--package_id', help='Package ID', required=True)
@click.option('--package_version', help="Package version, downloads all versions if not specified", default=None, required=False)
@click.option('--urls', help="Override default urls.tsv location", default=PACKAGE_SERVER + "urls.tsv")
@click.option('--download_location', default='./',
              help='Location for the downloaded file')
def get(package_id, package_version, urls, download_location):
    package_found = False
    log.info("Searching for package: "+str(package_id)+" in "+str(urls))
    if not os.path.exists(download_location):
        os.makedirs(download_location)

    handle = None
    if '://' in urls:
        with urllib.request.urlopen(urls) as uf:
            handle = StringIO(uf.read())
    elif os.path.exists(urls):
        handle = open(urls, 'r')
    else:
        raise Exception("--urls option does not look like a url or a file path")

    for ld in yield_packages(handle):
        # TODO: check platform/architecture, failover to all if available?
        # iid, version, platform, architecture, upstream_url, checksum, alternate_url = line.split('\t')
        if ld['id'] == package_id.strip() and (package_version is None or ld['version'] == package_version):
            package_found = True
            # I worry about this being unreliable. TODO: add target filename column?
            pkg_name = package_name(ld)
            storage_path = os.path.join(download_location, pkg_name)
            url = get_url(ld)
            urllib.request.urlretrieve(url, storage_path)
            download_checksum = hashlib.sha256(open(storage_path, 'rb').read()).hexdigest()
            if ld['sha256sum'] != download_checksum:
                log.error(
                    'Checksum does not match, something seems to be wrong.\n'
                    '{expected}\t(expected)\n{actual}\t(downloaded)'
                ).format(expected=ld['sha256sum'], actual=download_checksum)
            else:
                log.info('Download successful for %s.' % (pkg_name))
    if not package_found:
        log.warning('Package (%s) could not be found in this server.' % (package_id))


if __name__ == '__main__':
    get()
