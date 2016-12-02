#!/usr/bin/env python
import sys
import yaml


def extDetect(url):
    if url.endswith('.tar.gz'):
        return '.tar.gz'
    elif url.endswith('.tgz'):
        return '.tar.gz'
    elif url.endswith('.tar.bz2'):
        return '.tar.bz2'
    elif url.endswith('.tar.xz'):
        return '.tar.xz'
    else:
        guess = url[url.rindex('.'):]
        # If there's a slash, that's DEFINITELY not an extension. Return empty
        # and hope downstream handles that OK.
        if '/' in guess:
            return ''
        return guess


for element in yaml.load(sys.stdin):

    {'url': 'https://github.com/arq5x/lumpy-sv/66c83c8.tar.gz', 'version': '0.2.12', 'arch': 'linux-64', 'name': 'lumpy-sv'}
    # Id	Version	Platform	Architecture	Upstream Url	Extension	sha256sum	Use upstream
    platform = element['arch']
    arch = 'x64'
    if platform == 'src':
        arch = 'all'
    elif platform == 'osx-':
        platform = 'darwin'
    elif platform == 'linux-64':
        platform = 'linux'

    print '\t'.join([
        element['name'],
        element['version'],
        platform,
        arch,
        element['url'],
        extDetect(element['url']),
        "",
        "True"
    ])
