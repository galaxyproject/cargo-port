#!/usr/bin/env python
import sys
import logging
import click
from gsl.utils import yield_packages, HEADER_KEYS
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


@click.command()
@click.argument('galaxy_package_file')
def main(galaxy_package_file):
    with open(galaxy_package_file, 'r') as handle:

        print '# ' + '\t'.join(['Id', 'Version', 'Platform', 'Architecture', 'Upstream Url', 'Extension', 'sha256sum', 'Alternate Url']),
        res = {}
        for ld in yield_packages(handle):
            # id, version, platform,a rch, sha
            key = '_'.join([ld[x] for x in HEADER_KEYS[0:4] + HEADER_KEYS[6:7]])

            if key not in res:
                res[key] = []

            res[key].append(ld)

        for x in sorted(res):
            out = []
            for key in HEADER_KEYS:
                out.append(res[x][0][key])
            print '\t'.join(out).rstrip("\n")


if __name__ == '__main__':
    main()
