#!/usr/bin/env python
import sys
import yaml

DEFAULT_HASH_TYPE = 'sha256'
HASH_TYPE_ORDER = ('sha256', 'md5')


def pickOne(url):
    # Pick one
    if isinstance(url, list):
        return url[0]
    return url

def extDetect(url):
    url = pickOne(url)

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


for element in sorted(yaml.load(sys.stdin), key=lambda el: el['name']):
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

    hash_value = ''
    for hash_type in HASH_TYPE_ORDER:
        if element.get(hash_type):
            if hash_type == DEFAULT_HASH_TYPE:
                hash_value = element[hash_type]
            else:
                hash_value = '%ssum:%s' % (hash_type, element[hash_type])

    print '\t'.join([
        element['name'],
        element['version'],
        platform,
        arch,
        pickOne(element['url']),
        extDetect(element['url']),
        hash_value,
        "True"
    ])
