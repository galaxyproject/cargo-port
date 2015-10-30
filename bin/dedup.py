#!/usr/bin/env python
import sys
import logging
import click
import gsl.utils
from gsl.utils import yield_packages
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


keys = ['id', 'version', 'platform', 'arch', 'url', 'sha', 'size','alt_url', 'comment']

@click.command()
@click.argument('galaxy_package_file')
def main(galaxy_package_file):
    with open(galaxy_package_file, 'r') as handle:

        print '# ' + '\t'.join(['Id', 'Version', 'Platform', 'Architecture', 'Upstream url', 'sha256sum', 'Alternate Url']),
        retcode = 0
        res = {}
        warnings = []
        for ld in yield_packages(handle):

            if ld['id'] not in res:
                res[ld['id']] = []

            res[ld['id']].append(ld)

        for x in res:
            out = []
            for key in keys:
                out.append(res[x][0][key])
            print '\t'.join(out).rstrip("\n")

        sys.exit(retcode)


if __name__ == '__main__':
    main()
