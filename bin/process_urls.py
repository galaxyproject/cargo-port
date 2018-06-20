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
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
ALLOWED_PROTOCOLS = ('http://', 'https://', 'ftp://')


def yield_packages(handle, meta=False, retcode=None):
    keys = ['id', 'version', 'platform', 'arch', 'url', 'ext', 'sha', 'use_upstream']
    for lineno, line in enumerate(handle):
        if line.startswith('#'):
            continue
        try:
            data = line.strip().split('\t')
            if len(data) != len(keys):
                log.error('[%s] data has wrong number of columns. %s != %s', lineno + 1, len(data), len(keys))

            ld = {k: v for (k, v) in zip(keys, line.split('\t'))}

            if meta:
                yield ld, lineno, line, retcode
            else:
                yield ld
        except Exception as e:
            log.error(str(e))


class XUnitReportBuilder(object):
    XUNIT_TPL = """<?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="cpc" tests="{total}" errors="{errors}" failures="{failures}" skip="{skips}">
        {test_cases}
    </testsuite>
    """

    TESTCASE_TPL = """
        <testcase classname="downloader" name="{name}">
            {error}
        </testcase>
    """

    ERROR_TPL = """
                <error type="cpc.{errorName}" message="{errorMessage}">
                </error>
    """

    def __init__(self):
        self.xunit_data = {
            'total': 0, 'errors': 0, 'failures': 0, 'skips': 0
        }
        self.test_cases = []

    def ok(self, test_name):
        self.xunit_data['total'] += 1
        self.__add_test(test_name, errors="")

    def error(self, test_name, errorName, errorMessage):
        self.xunit_data['total'] += 1
        self.__add_test(test_name, errors=self.ERROR_TPL.format(
            errorName=errorName, errorMessage=errorMessage))

    def failure(self, test_name, errorName, errorMessage):
        self.xunit_data['total'] += 1
        self.__add_test(test_name, errors=self.ERROR_TPL.format(
            errorName=errorName, errorMessage=errorMessage))

    def skip(self, test_name):
        self.xunit_data['skips'] += 1
        self.xunit_data['total'] += 1
        self.__add_test(test_name, errors="")

    def __add_test(self, name, errors):
        self.test_cases.append(
            self.TESTCASE_TPL.format(name=name, error=errors))

    def serialize(self):
        self.xunit_data['test_cases'] = '\n'.join(self.test_cases)
        return self.XUNIT_TPL.format(**self.xunit_data)


def verify_file(path, sha):
    # If no hash provided then this is a bioconda package.
    if 0 == len(sha.strip()):
        log.warning("Unvalidated file download (bioconda) %s", path)
        return
    try:
        filehash = subprocess.check_output(['sha256sum', path])[0:64].strip()
        if filehash.lower() != sha.lower():
            excstr = "Bad hash, %s != %s in %s" % (filehash.lower(), sha.lower(), path)
            raise Exception(excstr)
    except Exception as cpe:
        log.error("File has bad hash! Refusing to serve this to end users.")
        os.unlink(path)
        return str(cpe)


def download_url(url, output):
    if not any([url.startswith(proto) for proto in ALLOWED_PROTOCOLS]):
        log.error("Unsupported protocol: %s" % url[0:10])
        return "Unsupported protocol"

    try:
        args = ['curl', '-L', '-k', '--max-time', '720']

        args += [url, '-o', output]
        subprocess.check_call(args)
    except subprocess.CalledProcessError as cpe:
        log.error("File not found")
        return str(cpe)


def symlink_depot(url, output):
    try:
        args = ['ln', '-s', url, output]
        log.info(' '.join(args))
        log.info(subprocess.check_call(args))
    except subprocess.CalledProcessError as cpe:
        log.error("Unable to symlink")
        return str(cpe)


def cleanup_file(sha):
    try:
        os.unlink(sha)
        if os.path.exists(sha + '.sha256sum'):
            os.unlink(sha + '.sha256sum')
    except Exception as e:
        log.error("Unable to remove files: %s", str(e))


def package_to_path(id="", version="", platform="", arch="", ext="", **kwargs):
    return '_'.join([id, version, platform, arch])


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
                err = verify_file(output_package_path, ld['sha'].strip())
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
