#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup

root = os.path.abspath(os.path.dirname(__file__))

version = __import__('mangrove').__version__

setup(
    name='mangrove',
    version=version,
    license='MIT',
    description='a boto connexion pool',
    author='Oleiade',
    author_email='theo@botify.com',
    url='http://github.com/botify-labs/mangrove',
    keywords='amazon aws boto python connexion pool',
    zip_safe=True,
    install_requires=[
        'boto',
        'futures',
    ],

    package_dir={'': '.'},
    include_package_data=False,

    packages=[
        'mangrove',
    ],
)
