#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from setuptools import setup, find_packages


# read meta-data from esper/meta.py
setup_opts = {}
meta_info = os.path.join('esper', 'meta.py')
exec(compile(open(meta_info).read(), meta_info, 'exec'), {}, setup_opts)

readme = open('README.rst').read()

setup(
    long_description=readme,
    packages=find_packages(exclude=['docs']),
    **setup_opts
)
