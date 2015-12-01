#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup  # , find_packages
import glob

setup(name='galaxy-package-cache',
      version='1.0',
      description='Python Distribution Utilities',
      author='Intergalactic Utilities Commission',
      maintainer='Eric Rasche',
      url='https://github.com/erasche/community-package-cache',
      packages=['gsl'],
      scripts=list(glob.glob("bin/galaxy*")),
      install_requires=['click'],
      classifiers=[
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
        ],
    )
