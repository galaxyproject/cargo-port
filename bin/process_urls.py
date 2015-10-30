#!/usr/bin/env python
import os
import sys
import subprocess
import logging
import gsl.utils
from gsl.utils import yield_packages
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

HTML_TPL_HEAD = """
<!DOCTYPE html>
<html>
    <head>
        <title>Galaxy Package Cache</title>
        <!-- Latest compiled and minified CSS -->
        <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css" integrity="sha512-dTfge/zgoMYpP7QbHy4gWMEGsbsdZeCXz7irItjcC3sPUFtf0kuFbDz/ixG7ArTxmDjLXDmezHubeNikyKGVyQ==" crossorigin="anonymous">

        <!-- Optional theme -->
        <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap-theme.min.css" integrity="sha384-aUGj/X2zp5rLCbBxumKTCw2Z50WgIr1vs/PFN4praOTvYXWlVyh2UtNUU0KAUhAX" crossorigin="anonymous">
    </head>
    <body>
        <div class="container">
        <h1>Galaxy Package Cache</h1>
        <p>
            This package cache serves to preserve packages permanently. Please
            see our <a href="https://github.com/erasche/community-package-cache">Github Repository</a>
            for more information.
        </p>
        <h3>How to Use This</h3>
        <p>
            You can use the following command to download
            packages from this repository:

            <pre>curl --silent https://raw.githubusercontent.com/erasche/community-package-cache/master/gsl.py | python - --package_id augustus_3_1</pre>
        </p>
        <p>
        </p>
        <h1>Cached URLs</h1>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Package ID</th>
                    <th>Package Version</th>
                    <th>Platform</th>
                    <th>Upstream</th>
                    <th>sha256sum</th>
                </tr>
            </thead>
            <tbody>
"""

HTML_ROW_TPL ="""
<tr>
    <td><a href="{sha}">{id}</a></td>
    <td>{version}</td>
    <td>{platform}-{arch}</td>
    <td><a href="{url}">Link</a></td>
    <td><a href="{sha}.sha256sum">{sha}</a></td>
</tr>
"""

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


def verify_file(sha):
    try:
        subprocess.check_output(['sha256sum', '-c', '%s.sha256sum' % sha])
    except subprocess.CalledProcessError, cpe:
        log.error("File has bad hash! Refusing to serve this to end users.")
        os.unlink(sha)
        return str(cpe)

def download_url(url, sha, size=None):
    try:
        # (ulimit -f 34; curl --max-filesize 34714 $URL -L -o tmp)
        args = ['curl', '-L', '-k', '--max-time', '360']

        if size is not None:
            args += ['--max-filesize', size]

        args += [url, '-o', sha]
        subprocess.check_call(args)
    except subprocess.CalledProcessError, cpe:
        log.error("File not found")
        return str(cpe)

def cleanup_file(sha):
    try:
        os.unlink(sha)
        if os.path.exists(sha + '.sha256sum'):
            os.unlink(sha + '.sha256sum')
    except Exception, e:
        log.error("Unable to remove files: %s", str(e))

@click.command()
@click.argument('galaxy_package_file')
def main(galaxy_package_file):
    with open(galaxy_package_file, 'r') as handle:
        print HTML_TPL_HEAD
        retcode = 0
        test_cases = []
        xunit = XUnitReportBuilder()

        for ld in yield_packages(handle):
            # (id, version, platform, arch, url, sha, alt_url) = data[0:7]
            nice_name = '{id}@{version}_{platform}-{arch}'.format(**ld)

            kwd = dict(**ld)
            kwd['url'] = ld['alt_url'] if len(ld['alt_url'].strip()) > 0 else ld['url']
            print HTML_ROW_TPL.format(
                **kwd
            )
            if os.path.exists(ld['sha']) and os.path.getsize(ld['sha']) == 0:
                log.error("Empty download, removing %s %s", ld['url'], ld['sha'])
                cleanup_file(ld['sha'])

            if os.path.exists(ld['sha']):
                log.info("URL exists %s", ld['url'])
                xunit.skip(nice_name)
            else:
                log.info("URL missing, downloading %s to %s", ld['url'], ld['sha'])

                err = download_url(ld['url'], ld['sha'], size=ld['size'])
                if err is not None:
                    xunit.failure(nice_name, "DownloadError", err)
                    cleanup_file(ld['sha'])
                    continue

                with open(os.path.join('%s.sha256sum' % ld['sha']), 'w') as handle:
                    handle.write("%s  %s" % (ld['sha'], ld['sha']))

                # Check sha256sum of download
                err = verify_file(ld['sha'])
                if err is not None:
                    xunit.error(nice_name, "Sha256sumError", err)
                    cleanup_file(ld['sha'])
                    continue

                xunit.ok(nice_name)

        with open('report.xml', 'w') as xunit_handle:
            xunit_handle.write(xunit.serialize())

        print "</tbody></table></div></body></html>"
        sys.exit(retcode)
