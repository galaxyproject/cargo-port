#!/usr/bin/env python

import yaml

unique_packages = {}

for meta_file in [
    'data_linux-64.yml',
    'data_linux-aarch64.yml',
    'data_osx-64.yml',
    'data_osx-arm64.yml'
]:
    res = yaml.safe_load(open(meta_file, 'r'))

    # Remove duplicates
    for package in res:
        # This information is the unique portion, so we key on that
        key_data = [
            package['version'],
            package['name']
        ]

        if isinstance(package['url'], list):
            key_data += package['url']
        else:
            key_data.append(package['url'])

        key = '|'.join(key_data)
        # maintain set of architectures seen for this particular key
        if key in unique_packages:
            unique_packages[key]['arch'].add(package['arch'])
        else:
            unique_packages[key] = package
            unique_packages[key]['arch'] = {unique_packages[key]['arch']}

res = []
for item in unique_packages.values():
    if len(item['arch']) == 1:
        # If there is only one arch, then we already have a platform specific URL.
        # We just extract the single identifier from the set.
        item['arch'] = item['arch'].pop()
    elif item['arch'] == {'linux-64', 'linux-aarch64'}:
        item['arch'] = 'linux-x64'
    elif item['arch'] == {'osx-64', 'osx-arm64'}:
        item['arch'] = 'osx-x64'
    elif item['arch'] == {'linux-64', 'linux-aarch64'}:
        item['arch'] = 'linux-x64'
    elif item['arch'] == {'linux-64', 'linux-aarch64'}:
        item['arch'] = 'linux-x64'
    else:
        # likely source code
        #(could  there be combinations beyond the above ones that mean something else?)
        item['arch'] = 'src-all'
    res.append(item)

with open('data.yml', 'w') as outfile:
    yaml.safe_dump(res, outfile, default_flow_style=False)
