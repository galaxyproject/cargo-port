#!/usr/bin/env python

from distutils.core import setup

setup(name='galaxy-package-cache',
      version='1.0',
      description='Python Distribution Utilities',
      author='Intergalactic Utilities Commission',
      maintainer='Eric Rasche',
      url='https://github.com/erasche/community-package-cache',
      packages=['gsl'],
      scripts=["bin/galaxy-package-locator","bin/galaxy-cachefile-dedup","bin/galaxy-cachefile-validator","bin/galaxy-package-updater"],
      classifiers=[
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
        ],
    )
