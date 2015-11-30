# The Cargo Port

![Cargo-Port-Logo](media/cpc-plain-small.png)

[![Build Status](https://travis-ci.org/erasche/community-package-cache.svg)](https://travis-ci.org/erasche/community-package-cache)

This project should address the problem of unreliable URLs by proxying an ID to
a URL. The ID is your stable token you can rely on and the corresponded URL is
maintained by a community.
The pilot runs at https://depot.galaxyproject.org/software/

## Contributing

Please make PRs adding new lines to the `urls.tsv` file with your package, the
expected sha256sum, and optionally a comment. If you don't need to make
sweeping changes to `urls.tsv` honestly your best choice for editing it is
probably going to be a spreadsheet tool like libreoffice. If you do need to
edit it in vim, I've found `:set ts=120` to be helpful in aligning columns.

## URL file

The file consists of four tab separated columns:

Column | Name          | Meaning
------ | ------------- | --------
1      | Id            | A package ID, some short, unique (in the file) identifier for the package.
2      | Version       | A version number for the package. Should represent upstream's version accurately.
3      | Platform      | One of (linux, windows, darwin, src)
4      | Architecture  | One of (x32, x64, all)
5      | Upstream URL  | Upstream's URL for the download. This only necessarily exist before the Community Package Cacher downloads is the first time. After that the URL may disappear and we will retain our copy
6      | Extension     | File extension, used in downloads/nicer access for end-users
7      | sha256sum     | sha256sum of the correct file.

## Using the CPC

You can use the community package cache with a small script called `gsl` (get stable link).
`--package_id` specifies the unique package name and with `--download_location` you can provide a path where the tarball should be stored.

The simplest way to download your archive is using this magic curl command.

```console
$ curl https://raw.githubusercontent.com/erasche/package-cache/master/gsl.py | python - --package_id augustus_3_1
```

## LICENSE

MIT licensed. See LICENSE file.
