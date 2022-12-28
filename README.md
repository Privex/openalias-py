# Privex Pyrewall

[![Build Status](https://travis-ci.com/Privex/pyrewall.svg?branch=master)](https://travis-ci.com/Privex/openalias-py) 
[![Codecov](https://img.shields.io/codecov/c/github/Privex/pyrewall)](https://codecov.io/gh/Privex/openalias-py)  
[![PyPi Version](https://img.shields.io/pypi/v/pyrewall.svg)](https://pypi.org/project/openalias/)
![License Button](https://img.shields.io/pypi/l/openalias) 
![PyPI - Downloads](https://img.shields.io/pypi/dm/openalias)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/openalias) 
![GitHub last commit](https://img.shields.io/github/last-commit/Privex/openalias-py)

A Python tool to query [OpenAlias records](https://openalias.org) - for easily grabbing all cryptocurrency addresses associated with a domain. Uses DNS-over-HTTPs by default for security, but also supports plain DNS if needed.

![Screenshot of OpenAlias.py commands](https://i.imgur.com/lEbjNHe.png)

```text
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

```

## Quickstart Install

We recommend that you use Python 3.7 or newer, as the tool makes use of dataclasses.

It might be possible to run on 3.6 at the lowest, but you'll need to install the `dataclasses` backport package

### Install via PyPi with Pip

```sh
python3 -m pip install -U openalias
```

### Install from source

```sh
git clone https://github.com/Privex/openalias-py.git
cd openalias-py
# You can either use pip to install it, or setup.py
# Via pip
pip3 install .
# Via setup.py
python3 setup.py install
```

## Usage

```sh
# You can either use the command which is supposed to be auto-installed into /usr/local/bin
# or ~/.local/bin - or you can use python3 -m openalias

# View help (independent command script)
openaliaspy --help
# View help (using the command via python module call)
python3 -m openalias --help

# Get the XMR address associated with the domain privex.io
openaliaspy get privex.io xmr

# Get JUST the LTC address on it's own associated with the domain privex.io
# (useful for programmatic use)
openaliaspy get -p privex.io ltc

# List all addresses associated with privex.io in a colourful rich table
openaliaspy list privex.io

# List the addresses and other data in plain comma-separated text
openaliaspy list -p privex.io

# Use standard DNS instead of DNS-over-HTTPs to list/get privex.io's addresses
openaliaspy -P dns list privex.io
openaliaspy -P dns get privex.io xmr

# Use a custom resolver for DNS-over-HTTPs or standard DNS
openaliaspy -P dns -r 9.9.9.9 get privex.io btc
openaliaspy -r https://dns.privex.io list privex.io
```

## License

OpenAlias.py is released under the X11 / MIT License, see `LICENSE` for more info.

## Thanks for reading!

**If this project has helped you, consider [grabbing a VPS or Dedicated Server from Privex](https://www.privex.io) -**
**prices start at as little as US$0.99/mo (we take cryptocurrency!)**

You can also donate to us using our OpenAlias address `privex.io` :)
