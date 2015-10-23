# Community Package Cache

[![Build Status](https://travis-ci.org/erasche/community-package-cache.svg)](https://travis-ci.org/erasche/community-package-cache)

This project should adress the problem of unreliable URLs by proxying an ID to a URL.
The ID is your stable token you can rely on and the corresponded URL is maintained by a community.

## Contributing

Please make PRs adding new lines to the `urls.tsv` file with your package, the expected sha256sum, and optionally a comment.

## URL file

The file consists of four tab separated columns:

Column | Name | Meaning
------ | ---- | ---
1      | Id   | A package ID, some short, unique (in the file) identifier for the package.
2      | Platform | One of (linux, windows, darwin, src)
3      | Architecture | One of (x32, x64, all)
4      | Upstream URL | Upstream's URL for the download. This only necessarily exist before the Community Package Cacher downloads is the first time. After that the URL may disappear and we will retain our copy
5      | sha256sum | sha256sum of the correct file.
6      | Alternate URL | If the package is NOT to be hosted by the Community Package Cache, then an alternate url may be specified in column 4 which the downloader will use when downloading, and the updater will use to ignore that package.
7      | Comment | Feel free to add a comment to your package

## Using the CPC

You can use the community package cache with a small script called `gsl` (get stable link).
`--package_id` specifies the unique package name and with `--download_location` you can provide a path where the tarball should be stored.

The simplest way to download your archive is using this magic curl command.

```console
$ curl https://raw.githubusercontent.com/erasche/package-cache/master/gsl.py | python - --package_id augustus_3_1
```

## LICENSE

MIT licensed. See LICENSE file.
