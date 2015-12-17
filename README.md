# The Cargo Port

[Galactic Distribution Center](https://depot.galaxyproject.org/software/)

<img src="media/cpc-plain-small.png" style="max-height: 10em" alt="Cargo Port Logo"/>

[![Build Status](https://travis-ci.org/galaxyproject/cargo-port.svg)](https://travis-ci.org/galaxyproject/cargo-port)
[![Build Status](https://jenkins.galaxyproject.org/buildStatus/icon?job=cargo-port)](https://jenkins.galaxyproject.org/view/Meta/job/cargo-port/)

This project addresses the problem of unreliable URLs by providing stable, long term storage for downloads.
Instead of hoping that the upstream author (e.g. sourceforge or CPAN) will not remove or modify a downloadable
.tar.gz file over time, you can rely on the Galaxy Cargo Port to maintain a copy of that
file long term.

This helps package authors and tool developers work more efficiently, by
allowing them to rely on URLs being permanently available.

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
8      | Use upstream  | A boolean True or False on whether we should request upstream first, or use depot's download. Useful is upstream has requested that we stop making so many downloads to their old releases.

## Using TCP

You can use cargo-port with a small script called `galaxy-package-locator`.
Argument `--package_id` specifies the package name, `--package_version` the package version and with `--download_location` you can provide a path where the tarball should be stored.

Cargo port can be installed as follows:

```console
$ git clone https://github.com/galaxyproject/cargo-port.git
$ cd cargo-port
$ python setup.py build
$ sudo python setup.py install
```

Downloading a package with galaxy-package-locator can be done as follows:

```
galaxy-package-locator --package_id samtools --package_version "1.2"
```

## LICENSE

MIT licensed. See LICENSE file.
