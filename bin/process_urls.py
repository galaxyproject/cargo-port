#!/usr/bin/env python
from __future__ import print_function

import json
import logging
import os
import subprocess
import sys
# Conditional import to ensure we can run without non-stdlib on py2k.
if sys.version_info.major > 2:
    from builtins import str
    from builtins import zip
    from builtins import object

from cargoport.utils import (download_url, 
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


def main(galaxy_package_file):
    visited_paths = []
    api_data = {'data': []}

    with open(galaxy_package_file, 'r') as handle:
        retcode = 0
        xunit = XUnitReportBuilder()

        for ld in yield_packages(handle):
            nice_name = package_to_path(**ld)

            if not os.path.exists(ld['id']):
                os.makedirs(ld['id'])

            output_package_path = os.path.join(ld['id'], nice_name) + ld['ext']
            visited_paths.append(os.path.abspath(output_package_path))

            tmpld = {}
            tmpld.update(ld)
            tmpld['_gen'] = output_package_path
            api_data['data'].append(tmpld)

            if os.path.exists(output_package_path) and os.path.getsize(output_package_path) == 0:
                log.error("Empty download, removing %s %s", ld['url'], output_package_path)
                cleanup_file(output_package_path)

            if os.path.exists(output_package_path):
                log.debug("URL exists %s", ld['url'])
                xunit.skip(nice_name)
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
                err = verify_file(output_package_path, ld['sha256sum'].strip())
                if err is not None:
                    xunit.error(nice_name, "Sha256sumError", err)
                    cleanup_file(output_package_path)
                    continue

                xunit.ok(nice_name)

        with open('report.xml', 'w') as xunit_handle:
            xunit_handle.write(xunit.serialize())

        print(json.dumps(api_data, indent=2))
    sys.exit(retcode)


if __name__ == '__main__':
    main(sys.argv[1])
