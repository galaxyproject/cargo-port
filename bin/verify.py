#!/usr/bin/env python
import os
import sys
# Conditional import to ensure we can run without non-stdlib on py2k.
if sys.version_info.major > 2:
    from builtins import str
    from builtins import zip
    from builtins import object
import json
import subprocess
import logging

from cargoport.utils import (package_to_path,
    symlink_depot, 
    verify_file, 
    verify_filetype, 
    XUnitReportBuilder,
    yield_packages)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


def main(galaxy_package_file, dryrun=False):
    visited_paths = []
    api_data = {'data': []}

    with open(galaxy_package_file, 'r') as handle:
        retcode = 0
        xunit = XUnitReportBuilder()
        xunit.ok("I.Am.Alive")

        for ld in yield_packages(handle):
            nice_name = package_to_path(**ld)

            if not os.path.exists(ld['id']):
                continue

            output_package_path = os.path.join(ld['id'], nice_name) + ld['ext']

            if not os.path.exists(output_package_path):
                continue

            visited_paths.append(os.path.abspath(output_package_path))

            if os.path.exists(output_package_path) and os.path.getsize(output_package_path) == 0:
                log.error("Empty download, removing %s %s", ld['url'], output_package_path)
                cleanup_file(output_package_path)
                xunit.failure(nice_name, "EmptyFile", "%s was found to be empty" % output_package_path)

            err = verify_file(output_package_path, ld['sha256sum'].strip())
            if err is not None:
                xunit.failure(nice_name, "ValidationError", err)

            err = verify_filetype(output_package_path, ld['ext'].strip(), dryrun=dryrun)
            if err is not None:
                xunit.failure(nice_name, "ValidationError", err)

        with open('report.xml', 'w') as xunit_handle:
            xunit_handle.write(xunit.serialize())
    sys.exit(retcode)

if __name__ == '__main__':
    main(sys.argv[1], dryrun=(False if len(sys.argv) <= 2 else True))
