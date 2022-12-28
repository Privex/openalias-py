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
from decimal import Decimal
from privex.helpers import env_csv, env_bool, env_int, env_decimal
from os import getenv as env
from privex.loghelper import LogHelper
import logging
import sys
from rich import print as rprint
import random

sysrand = random.SystemRandom()

DEBUG = env_bool('DEBUG', False)

LOG_LEVEL = env('LOG_LEVEL', 'DEBUG' if DEBUG else 'WARNING')
LOG_LEVEL = logging.getLevelName(LOG_LEVEL)

def setup_logger(name='openalias', level=LOG_LEVEL, handler_level=logging.DEBUG):
    _lh = LogHelper('openalias', level=level, handler_level=handler_level)
    _ch = _lh.add_console_handler()
    _ch.setStream(sys.stderr)
    return _lh

setup_logger(level=LOG_LEVEL)

DOH_RESOLVERS = env_csv(
    'DOH_RESOLVERS', 
    [
        'https://dns.google/dns-query',
        'https://cloudflare-dns.com/dns-query',
        'https://dns.privex.io'
    ]
)

DNS_RESOLVERS_V4 = env_csv('DNS_RESOLVERS_V4', env_csv('RESOLVERS_V4', 
    [
        '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1', '4.2.2.3', '4.2.2.4',
        '185.130.44.20', '185.130.47.20'
    ]
))

DNS_RESOLVERS_V6 = env_csv('DNS_RESOLVERS_V6', env_csv('RESOLVERS_V6', 
    [
        '2001:4860:4860::8888', '2001:4860:4860::8844', '2606:4700:4700::1111', 
        '2606:4700:4700::1001', '2a07:e00::333', '2a07:e03::333',
    ]
))

sysrand.shuffle(DNS_RESOLVERS_V4)
sysrand.shuffle(DNS_RESOLVERS_V6)
sysrand.shuffle(DOH_RESOLVERS)

DNS_PROTOCOL = env('DNS_PROTOCOL', 'doh')

DNS_PROTOCOL_MAP = dict(
    doh="doh", dnsoverhttps="doh", https="doh", tls="doh", secure="doh",
    dns_over_https="doh",
    tcp="dnstcp", udp="dnsudp", normal="dnsudp", dns="dnsudp",
    dnstcp="dnstcp", dnsudp="dnsudp", standard="dnsudp", insecure="dnsudp",
    plain="dnsudp"
)

TEST_IP_V6 = env('TEST_IP_V6', '2001:4860:4860::8888')
"""IPv6 address to use when testing v6 connectivity"""
TEST_IP_V4 = env('TEST_IP_V4', '8.8.8.8')
"""IPv4 address to use when testing v4 connectivity"""
TEST_PORT = env_int('TEST_PORT', 443)
"""Port to connect to when testing v4/v6 connectivity"""
TEST_TIMEOUT = env_decimal('TEST_TIMEOUT', Decimal('3.0'))
"""Max time to wait before determining v4/v6 is broken"""
HAS_V6 = None
"""Will be ``True`` if system has working IPv6, otherwise ``False`` if broken IPv6. If not tested yet, will be ``None``"""
HAS_V4 = None
"""Will be ``True`` if system has working IPv4, otherwise ``False`` if broken IPv4. If not tested yet, will be ``None``"""

USE_IPV4 = env_bool('USE_IPV4', True)
USE_IPV6 = env_bool('USE_IPV6', True)

def print_err(*msg, file=sys.stderr, **kwargs):
    return rprint(*msg, file=file, **kwargs)

if DNS_PROTOCOL.lower() not in DNS_PROTOCOL_MAP:
    print_err(
        f"[red][bold]ERROR:[/bold] Invalid protocol '{DNS_PROTOCOL}'. DNS_PROTOCOL must be either: [/]\n\n"
        f"\t Standard unencrypted DNS (UDP): dns, plain, dnsudp, udp, normal\n"
        f"\t Standard unencrypted DNS (TCP): dnstcp, tcp\n"
        f"\t DNS-over-HTTPS (default): doh, https, tls, secure, dns_over_https\n"
    )
    sys.exit(3)

