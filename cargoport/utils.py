#!/usr/bin/env python
import sys
# Conditional import to ensure we can run without non-stdlib on py2k.
if sys.version_info.major > 2:
    from builtins import str
    from builtins import zip
import subprocess
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

HEADER_KEYS = ['id', 'version', 'platform', 'arch', 'url', 'ext', 'sha256sum', 'upstream_first']
PACKAGE_SERVER = 'https://depot.galaxyproject.org/software/'


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


def yield_packages(handle, meta=False, retcode=None):
    for lineno, line in enumerate(handle):
        if line.startswith('#'):
            continue
        try:
            data = line.strip().split('\t')
            if len(data) != len(HEADER_KEYS):
                log.error('[%s] data has wrong number of columns. %s != %s', lineno + 1, len(data), len(HEADER_KEYS))
                retcode = 1

            ld = {k: v for (k, v) in zip(HEADER_KEYS, data)}

            if meta:
                yield ld, lineno, line, retcode
            else:
                yield ld
        except Exception as e:
            log.error(str(e))


def package_name(ld):
    return '_'.join(ld[key] for key in HEADER_KEYS[0:4]) + ld['ext']


def depot_url(ld):
    return PACKAGE_SERVER + '{id}/{id}_{version}_{platform}_{arch}{ext}'.format(**ld)


def get_url(ld):
    if ld['upstream_first'] == 'True':
        return ld['url']
    else:
        return depot_url(ld)


def download_url(url, output):
    try:
        args = ['curl', '-L', '-k', '--max-time', '720']

        args += [url, '-o', output]
        subprocess.check_call(args)
        return None
    except subprocess.CalledProcessError as cpe:
        log.error("File not found")
        return str(cpe)


def package_to_path(id="", version="", platform="", arch="", ext="", **kwargs):
    return '_'.join([id, version, platform, arch])


def symlink_depot(url, output):
    try:
        args = ['ln', '-s', url, output]
        log.info(' '.join(args))
        log.info(subprocess.check_call(args))
    except subprocess.CalledProcessError as cpe:
        log.error("Unable to symlink")


def verify_file(path, sha):
    try:
        filehash = subprocess.check_output(['sha256sum', path])[0:64].strip()
        log.info("File hash %s", filehash.lower())
        if filehash.lower() != sha.lower():
            excstr = "%s != %s in %s" % (filehash.lower(), sha.lower(), path)
            raise Exception(excstr)
        log.info("Verified, %s == %s", filehash.lower(), sha.lower())
        return None
    except Exception as cpe:
        log.error("File has bad hash! %s", cpe)
        return str(cpe)


def verify_filetype(path, ext, dryrun=False):
    mimetype = subprocess.check_output(['file', path]).strip()
    log.info("Mimetype of %s is %s", path, mimetype)
    # Currently just passing on without error.
    return
