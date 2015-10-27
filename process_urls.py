#!/usr/bin/env python
import os
import sys
import subprocess
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

XUNIT_TPL = """
<?xml version="1.0" encoding="UTF-8"?>
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

HTML_TPL_HEAD = """
<!DOCTYPE html>
<html>
    <head>
        <title>Galaxy Package Cache</title>
    </head>
    <body>
        <h1>Galaxy Package Cache</h1>
        <p>
            This package cache serves to preserve packages permanently. Please
            see our <a href="https://github/erasche/community-package-cache">Github Repository</a>
            for more information. You can use the following command to download
            packages from this repository:

            <pre>curl --silent https://raw.githubusercontent.com/bgruening/gsl/master/gsl.py | python - --package_id augustus_3_1</pre>
        </p>
        <h1>Cached URLs</h1>
        <table>
            <thead>
                <tr>
                    <th>Package ID</th>
                    <th>Package Version</th>
                    <th>Platform</th>
                    <th>URL</th>
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
    <td>{url}</td>
    <td><a href="{sha}.sha256sum">{sha}</a></td>
</tr>
"""


with open(sys.argv[1], 'r') as handle, open('report.xml', 'w') as xunit:
    print HTML_TPL_HEAD
    retcode = 0
    xunit_data = {
        'total': 0, 'errors': 0, 'failures': 0, 'skips': 0
    }
    test_cases = []

    for line in handle:
        if line.startswith('#'):
            continue

        data = line.split('\t')
        (id, version, platform, arch, url, sha, alt_url) = data[0:7]
        nice_name = '-'.join([id, version, platform, arch])

        print HTML_TPL_HEAD.format(
            id=id,
            version=version,
            platform=platform,
            arch=arch,
            url=alt_url if alt_url is not None else url,
            sha=sha
        )
        xunit_data['total'] += 1

        if os.path.exists(sha) or alt_url.strip():
            log.info("URL exists %s", url)
            xunit_data['skips'] += 1
            test_cases.append(TESTCASE_TPL.format(name=nice_name, error=""))
        else:
            log.info("URL missing, downloading %s to %s", url, sha)
            try:
                subprocess.check_call(['wget', '--no-check-certificate', '--quiet', url, '-O', sha])
            except subprocess.CalledProcessError, cpe:
                log.error("File not found")
                xunit_data['failures'] += 1
                test_cases.append(TESTCASE_TPL.format(
                    name=nice_name,
                    error=ERROR_TPL.format(
                        errorName="DownloadError",
                        errorMessage=str(cpe),
                    )))
                continue

            with open(os.path.join('%s.sha256sum' % sha), 'w') as handle:
                handle.write("%s  %s" % (sha, sha))

            # Check sha256sum of download
            try:
                subprocess.check_call(['sha256sum', '-c', '%s.sha256sum' % sha])
            except subprocess.CalledProcessError, cpe:
                log.error("File has bad hash! Refusing to serve this to end users.")
                xunit_data['errors'] += 1
                os.unlink(sha)
                test_cases.append(TESTCASE_TPL.format(
                    name=nice_name,
                    error=ERROR_TPL.format(
                        errorName="Sha256sumError",
                        errorMessage=str(cpe),
                    )))
                continue

            test_cases.append(TESTCASE_TPL.format(name=nice_name, error=""))


    xunit_data['test_cases'] = '\n'.join(test_cases)
    xunit.write(XUNIT_TPL.format(**xunit_data))

    print "</tbody></table></body></html>"
    sys.exit(retcode)
