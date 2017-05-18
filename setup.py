#!/usr/bin/env python
import glob
from setuptools import setup


setup(
    name='cargo-port',
    version='1.0',
    description='Python Distribution Utilities',
    author='Intergalactic Utilities Commission',
    maintainer='Eric Rasche',
    url='https://github.com/erasche/community-package-cache',
    packages=['cargoport'],
    scripts=list(glob.glob("bin/galaxy*")),
    install_requires=['click', 'future'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ]
)
