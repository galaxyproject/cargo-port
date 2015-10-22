# Community Package Cache

[![Build Status](https://travis-ci.org/erasche/community-package-cache.svg)](https://travis-ci.org/erasche/community-package-cache)

Because upstream is unreliable and URLs are mutable.

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

## Using the CPC

```console
$ curl https://raw.githubusercontent.com/erasche/package-cache/master/gsl.py | python - --package_id augustus_3_1
```

## LICENSE

MIT licensed. See LICENSE file.
