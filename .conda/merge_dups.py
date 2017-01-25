#!/usr/bin/env python

import yaml

linux = yaml.load(open('data_linux-64.yml', 'r'))
res = yaml.load(open('data_osx-.yml', 'r'))
res.extend(linux)

# Remove duplicates
unique_packages = {}
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
    # We turn the architecture item into a list.
    if key in unique_packages:
        unique_packages[key]['arch'].append(package['arch'])
    else:
        unique_packages[key] = package
        unique_packages[key]['arch'] = [unique_packages[key]['arch']]

res = []
for item in unique_packages.values():
    if len(item['arch']) == 1:
        # If there is only one arch, then we have a platform specific URL,
        # since otherwise we would have generated an arch that contains both
        # linux + osx
        item['arch'] = item['arch'][0]
        res.append(item)
    else:
        # Here we have two or more archs (ideally. We don't check conditions
        # like 0 arches)
        item['arch'] = 'src'
        res.append(item)

with open('data.yml', 'w') as outfile:
    yaml.safe_dump(res, outfile, default_flow_style=False)
