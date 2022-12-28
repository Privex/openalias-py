#!/usr/bin/env python3
"""
OpenAlias.py - A Python tool for easily querying OpenAlias records
Copyright (c) 2023    Privex Inc. ( https://www.privex.io )

Copyright::

    +===================================================+
    |                 © 2023 Privex Inc.                |
    |               https://www.privex.io               |
    +===================================================+
    |                                                   |
    |        OpenAlias.py - A python OpenAlias Client   |
    |        License: X11/MIT                           |
    |                                                   |
    |        https://github.com/Privex/openalias-py     |
    |                                                   |
    |        Core Developer(s):                         |
    |                                                   |
    |          (+)  Chris (@someguy123) [Privex]        |
    |                                                   |
    +===================================================+

"""

from setuptools import setup, find_packages
from openalias.version import VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='openalias',

    version=VERSION,

    description='A Python tool for easily querying OpenAlias records',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Privex/openalias-py",
    author='Chris (Someguy123) @ Privex',
    author_email='chris@privex.io',

    license='MIT',
    install_requires=[
        'privex-helpers>=3.0.0', 'dnspython>=2.0.0', 'rich>=12',
        'requests', 'httpx'
    ],
    packages=find_packages(),
    scripts=['bin/openaliaspy'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)
