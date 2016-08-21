#!/usr/bin/env python

import yaml

linux = yaml.load(open('data_linux-64.yml'))
res = yaml.load(open('data_osx-.yml'))
res.extend(linux)

# Remove duplicates
unique_packages = {}
for package in res:
    # This information is the unique portion, so we key on that
    key = '|'.join([package[x] for x in ('url', 'version', 'name')])
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
