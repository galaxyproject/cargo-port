#!/usr/bin/python
import sys
import logging
import click
from cargoport.utils import yield_packages, HEADER_KEYS
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


@click.command()
@click.argument('galaxy_package_file')
def main(galaxy_package_file):
    with open(galaxy_package_file, 'r') as handle:
        retcode = 0
        identifiers = set()

        for ld, lineno, line, extraret in yield_packages(handle, retcode=retcode, meta=True):
            if extraret > 0:
                retcode = extraret
            try:
                for x in HEADER_KEYS[0:5] + HEADER_KEYS[6:6]:
                    # Skip extension, as it is OK to be empty
                    if ld.get(x, '').strip() == '':
                        log.error("[%s] Empty %s", lineno, x)
                        retcode = 1

                if ld['platform'] not in ('linux', 'windows', 'darwin', 'src'):
                    log.error("[%s] Unknown platform %s", lineno, ld['platform'])
                    retcode = 1

                if ld['arch'] not in ('x32', 'x64', 'all'):
                    log.error("[%s] Unknown architecture %s", lineno, ld['arch'])
                    retcode = 1

                if len(ld['sha256sum']) != 64:
                    log.error("[%s] Bad checksum %s", lineno, ld['sha256sum'])
                    retcode = 1

                if ld['sha256sum'] != ld['sha256sum'].lower():
                    log.error("[%s] Uppercase checksum needs to be lower case %s", lineno, ld['sha256sum'])
                    retcode = 1

                if len(ld['sha256sum']) != 64:
                    log.error("[%s] sha256sum is not 64 characters long. Typo?  %s", lineno, ld['sha256sum'])
                    retcode = 1

                if any([x not in list('1234567890abcdef') for x in list(ld['sha256sum'])]):
                    log.error("[%s] sha256sum contains non-hexidecimal characters. Typo?  %s", lineno, ld['sha256sum'])
                    retcode = 1

                if ld['upstream_first'] not in ('True', 'False'):
                    log.error("[%s] Upstream first must be 'True' or 'False', was '%s'", lineno, ld['upstream_first'])
                    retcode = 1

                platform_id = (ld['id'], ld['version'], ld['platform'], ld['arch'])
                if platform_id in identifiers:
                    log.error("[%s] identifier is not unique: '%s'", lineno, platform_id)
                    retcode = 1
                else:
                    identifiers.add(platform_id)
            except Exception, e:
                log.error("[%s] Line (probably) not tabbed properly: %s", lineno, e)
                retcode = 1
        sys.exit(retcode)


if __name__ == '__main__':
    main()
