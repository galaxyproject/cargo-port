#!/usr/bin/env python
import os
import sys
import json
import subprocess
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


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
        except Exception, e:
            log.error(str(e))

class XUnitReportBuilder(object):
    XUNIT_TPL = """<?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="cpc-fulltest" tests="{total}" errors="{errors}" failures="{failures}" skip="{skips}">
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


def verify_file(path, sha, dryrun=False):
    try:
        filehash = subprocess.check_output(['sha256sum', path])[0:64].strip()
        if filehash.lower() != sha.lower():
            excstr = "Bad hash, %s != %s in %s" % (filehash.lower(), sha.lower(), path)
            raise Exception(excstr)
    except Exception, cpe:
        log.error("File has bad hash! Refusing to serve this to end users.")
        if not dryrun:
            os.unlink(path)
        return str(cpe)

def symlink_depot(url, output):
    try:
        args = ['ln', '-s', url, output]
        log.info(' '.join(args))
        log.info(subprocess.check_call(args))
    except subprocess.CalledProcessError, cpe:
        log.error("Unable to symlink")
        return str(cpe)


def package_to_path(id="", version="", platform="", arch="", ext="", **kwargs):
    return '_'.join([id, version, platform, arch])


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

            err = verify_file(output_package_path, ld['sha'].strip(), dryrun=dryrun)
            if err is not None:
                xunit.failure(nice_name, "ValidationError", err)

        with open('report.xml', 'w') as xunit_handle:
            xunit_handle.write(xunit.serialize())

    # Now that we've processed (hopefully) every file in urls.tsv
    # we need to check for files which shouldn't be there (aka things NOT
    # mentioned in urls.tsv) and remove those.
    whitelist = [
        'SHA256SUM.txt', 'index.html', 'report.xml',
        'cpc-plain-small.png', 'cpc-base.png', 'cpc-base.svg',
        'urls.tsv', 'urls-bioconda.tsv',
        'api-tcp.json', 'api-bioconda.json', 'api.json',
    ]
    for root, dirnames, filenames in os.walk('.'):
        if '.git' in root:
            continue

        if 'static' in root:
            continue

        for filename in filenames:
            if filename in whitelist:
                continue

            fullpath = os.path.abspath(os.path.join(root, filename))
            # Ensure we ahven't seen it and it's under our directory
            if fullpath not in visited_paths and fullpath.startswith('/srv/nginx/depot.galaxyproject.org/root/software/'):
                log.info("Found a file that we don't own: %s", fullpath)
                os.unlink(fullpath)
    sys.exit(retcode)

if __name__ == '__main__':
    main(sys.argv[1], dryrun=(False if len(sys.argv) <= 2 else True))
