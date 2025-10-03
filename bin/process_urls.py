#!/usr/bin/env python
from __future__ import print_function

import json
import logging
import os
import subprocess
import sys

from itertools import groupby

# Conditional import to ensure we can run without non-stdlib on py2k.
if sys.version_info.major > 2:
    from builtins import str
    from builtins import zip
    from builtins import object

from cargoport.utils import (download_url, 
    package_hash_type,
    package_to_path, 
    symlink_depot, 
    verify_file, 
    XUnitReportBuilder,
    yield_packages) 

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
ALLOWED_PROTOCOLS = ('http://', 'https://', 'ftp://')


def cleanup_file(sha):
    try:
        os.unlink(sha)
        if os.path.exists(sha + '.sha256sum'):
            os.unlink(sha + '.sha256sum')
    except Exception as e:
        log.error("Unable to remove files: %s", str(e))


def main(galaxy_package_file, ignore_file):
    visited_paths = []
    api_data = {'data': []}

    ignored_downloads = set()
    with open(ignore_file, 'r') as handle:
        for line in handle:
            ignored_downloads.add(line.split('\t')[0])

    with open(galaxy_package_file, 'r') as handle:
        retcode = 0
        xunit = XUnitReportBuilder()

        for package_id, package_data in groupby(yield_packages(handle), key=lambda x: x['id']):
            if not os.path.exists(package_id):
                os.makedirs(package_id)
            checksum_file = os.path.join(package_id, 'SHA256SUM.txt')
            checksums_data = []
            if os.path.isfile(checksum_file):
                with open(checksum_file) as checksums:
                    for line in checksums:
                        package_checksum_data = line.strip().split()
                        if package_checksum_data not in checksums_data:
                            checksums_data.append(package_checksum_data)

            for ld in package_data:
                nice_name = package_to_path(**ld)
                file_name = nice_name + ld['ext']

                if file_name in ignored_downloads:
                    continue

                output_package_path = os.path.join(ld['id'], file_name)
                visited_paths.append(os.path.abspath(output_package_path))

                tmpld = {}
                tmpld.update(ld)
                tmpld['_gen'] = output_package_path
                api_data['data'].append(tmpld)

                if os.path.exists(output_package_path) and os.path.getsize(output_package_path) == 0:
                    log.error("Empty download, removing %s %s", ld['url'], output_package_path)
                    cleanup_file(output_package_path)

                hash_type, hash_value = package_hash_type(ld)

                if os.path.exists(output_package_path):
                    log.debug("URL exists %s", ld['url'])
                    xunit.skip(nice_name)
                elif hash_type is None:
                    err = "No hash provided for '%s', package will not be downloaded" % nice_name
                    log.error(err)
                    xunit.error(nice_name, "Sha256sumError", err)
                else:
                    log.info("URL missing, downloading %s to %s", ld['url'], output_package_path)

                    if ld['url'].startswith('/'):
                        err = symlink_depot(ld['url'], output_package_path)
                    else:
                        err = download_url(ld['url'], output_package_path)

                    if err is not None:
                        xunit.failure(nice_name, "DownloadError", err)
                        cleanup_file(output_package_path)
                        continue

                    # Check sha256sum of download
                    err = verify_file(output_package_path, hash_value, hash_type=hash_type)

                    if err is not None:
                        xunit.error(nice_name, "Sha256sumError", err)
                        cleanup_file(output_package_path)
                        continue

                    package_checksum_data = [hash_value, file_name]
                    if package_checksum_data not in checksums_data:
                        checksums_data.append(package_checksum_data)

                    xunit.ok(nice_name)

            with open(checksum_file, 'w') as checksums:
                for package_checksum_data in sorted(checksums_data, key=lambda x: x[1]):
                    checksums.write('\t'.join(package_checksum_data) + '\n')

        with open('report.xml', 'w') as xunit_handle:
            xunit_handle.write(xunit.serialize())

        print(json.dumps(api_data, indent=2))
    sys.exit(retcode)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
