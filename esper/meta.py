# -*- coding:utf-8 -*-
#
# meta.py - release information for the esper distribution
#
"""Esper is a lightweight Entity System for Python, with a focus on performance.
"""

name = 'esper'
version = '0.9.9'
description = __doc__.splitlines()[0]
keywords = 'ecs,entity component system'
author = 'Benjamin Moran'
license = 'MIT'
author_email = 'benmoran56@gmail.com'
url = 'https://github.com/benmoran56/esper'
download_url = url + '/releases'
platforms = 'POSIX, Windows, MacOS X'
classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Topic :: Games/Entertainment
Topic :: Software Development :: Libraries :: Python Modules
"""
classifiers = [c.strip() for c in classifiers.splitlines()
               if c.strip() and not c.startswith('#')]
