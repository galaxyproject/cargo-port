#!/usr/bin/env python
import os
import sys
import subprocess
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def yield_packages(handle, meta=False, retcode=None):
    for lineno, line in enumerate(handle):
        if line.startswith('#'):
            continue
        try:
            data = line.split('\t')
            keys = ['id', 'version', 'platform', 'arch', 'url', 'ext', 'sha', 'size',
                    'alt_url', 'comment']
            if len(data) != len(keys):
                log.error('[%s] data has wrong number of columns. %s != %s', lineno + 1, len(data), len(keys))

            ld = {k: v for (k, v) in zip(keys, line.split('\t'))}

            if meta:
                yield ld, lineno, line, retcode
            else:
                yield ld
        except Exception, e:
            log.error(str(e))

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
        <script>
          (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
          (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
          m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
          })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
          ga('create', 'UA-45719423-15', 'auto');
          ga('send', 'pageview');
        </script>
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
        <h3>Verifying URLs</h3>
        <p>
            The CPC ships an SHA256SUM file per package download.
            Downloaded files can be validated with the following command:

            <pre>
            LC_ALL=C sha256sum -c SHA256SUM 2>/dev/null | grep -v 'FAILED open or read'
            </pre>

            sha256sum has the <a href="https://bugzilla.redhat.com/show_bug.cgi?id=1276664">unfortunate
            behaviour</a> of printing a lot of noise when files aren't found.
        </p>
        <h1>Cached URLs</h1>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Package ID</th>
                    <th>Package Version</th>
                    <th>Platform</th>
                    <th>Upstream</th>
                </tr>
            </thead>
            <tbody>
"""

HTML_ROW_TPL ="""
<tr>
    <td><a href="{package_path}">{id}</a></td>
    <td>{version}</td>
    <td>{platform}-{arch}</td>
    <td><a href="{url}">Link</a></td>
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


def verify_file(path, sha):
    try:
        filehash = subprocess.check_output(['sha256sum', path])[0:64]
        if filehash != sha:
            raise Exception("Bad hash, %s != %s in %s", filehash, sha, path)
    except subprocess.CalledProcessError, cpe:
        log.error("File has bad hash! Refusing to serve this to end users.")
        os.unlink(path)
        return str(cpe)

def download_url(url, output, size=None):
    try:
        # (ulimit -f 34; curl --max-filesize 34714 $URL -L -o tmp)
        args = ['curl', '-L', '-k', '--max-time', '360']

        # if size is not None:
            # args += ['--max-filesize', size]

        args += [url, '-o', output]
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

def package_to_path(id="", version="", platform="", arch="", ext="", **kwargs):
    return '_'.join([id, version, platform, arch])

def main(galaxy_package_file):
    with open(galaxy_package_file, 'r') as handle:
        print HTML_TPL_HEAD
        retcode = 0
        xunit = XUnitReportBuilder()

        for ld in yield_packages(handle):
            nice_name = package_to_path(**ld)
            import pprint; pprint.pprint(nice_name)

            if not os.path.exists(ld['id']):
                os.makedirs(ld['id'])

            output_package_path = os.path.join(ld['id'], nice_name) + ld['ext']

            print HTML_ROW_TPL.format(
                package_path=output_package_path,
                id=ld['id'],
                version=ld['version'],
                platform=ld['platform'],
                arch=ld['arch'],
                url=ld['alt_url'] if len(ld['alt_url'].strip()) > 0 else ld['url'],
            )

            if os.path.exists(output_package_path) and os.path.getsize(output_package_path) == 0:
                log.error("Empty download, removing %s %s", ld['url'], output_package_path)
                cleanup_file(output_package_path)

            if os.path.exists(output_package_path):
                log.info("URL exists %s", ld['url'])
                xunit.skip(nice_name)
            else:
                log.info("URL missing, downloading %s to %s", ld['url'], output_package_path)

                err = download_url(ld['url'], output_package_path, size=ld['size'])
                if err is not None:
                    xunit.failure(nice_name, "DownloadError", err)
                    cleanup_file(output_package_path)
                    continue

                # Check sha256sum of download
                err = verify_file(output_package_path, ld['sha'])
                if err is not None:
                    xunit.error(nice_name, "Sha256sumError", err)
                    cleanup_file(output_package_path)
                    continue

                xunit.ok(nice_name)

        with open('report.xml', 'w') as xunit_handle:
            xunit_handle.write(xunit.serialize())

        print """
                </tbody>
            </table>
        </div>
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-45719423-15', 'auto');
  ga('send', 'pageview');

</script>
    </body>
</html>"""
        sys.exit(retcode)

if __name__ == '__main__':
    main(sys.argv[1])
