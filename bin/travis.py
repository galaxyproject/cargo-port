#!/usr/bin/env python
import sys
import logging
from cargoport.utils import yield_packages, download_url, package_to_path, verify_file
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def main():
    for package in yield_packages(sys.stdin):
        print package
        # Remove the '+' at the beginning
        package['id'] = package['id'][1:]

        output_package_path = package_to_path(**package) + package['ext']
        err = download_url(package['url'], output_package_path)

        if err is not None:
            log.error("Could not download file", err)
        else:
            log.info("%s downloaded successfully", output_package_path)

        err = verify_file(output_package_path, package['sha256sum'])

        if err is not None:
            log.error("Could not verify file", err)
        else:
            log.info("%s verified successfully with hash %s", output_package_path, package['sha256sum'])


if __name__ == '__main__':
    main()
