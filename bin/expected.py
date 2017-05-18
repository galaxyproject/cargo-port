#!/usr/bin/env python
from __future__ import print_function
import logging
import click
from cargoport.utils import yield_packages, get_url
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


@click.command()
@click.argument('galaxy_package_file')
@click.argument('id')
@click.option('--version')
def main(galaxy_package_file, id, version=None):
    with open(galaxy_package_file, 'r') as handle:
        for ld in yield_packages(handle):
            if ld['id'].lower() != id.lower():
                continue

            if version is not None and ld['version'].lower() != version.lower():
                continue

            print("""<action type="download_by_url" sha256sum="{0[sha]}">
    {1}
</action>""".format(ld, get_url(ld)))


if __name__ == '__main__':
    main()
