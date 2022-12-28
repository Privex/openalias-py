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
from typing import List, Union
from openalias import settings
from privex.helpers import empty, empty_if
import socket
import random
import sys
from rich import print as rprint

sysrandom = random.SystemRandom()

def print_err(*args, file=sys.stderr, **kwargs):
    return rprint(*args, file=file, **kwargs)


def test_network(
        ip_version: int = 6, test_ip=None, test_port: int = None, 
        socket_type=socket.SOCK_STREAM, timeout: Union[Decimal, float, int]=None
    ) -> bool:

    test_ip = empty_if(test_ip, settings.TEST_IP_V6 if ip_version == 6 else settings.TEST_IP_V4)
    test_port = empty_if(test_port, settings.TEST_PORT, zero=True)
    timeout = empty_if(timeout, settings.TEST_TIMEOUT)
    success = False
    s = socket.socket(socket.AF_INET6 if ip_version == 6 else socket.AF_INET, socket_type)
    s.settimeout(float(timeout))
    try:
        s.connect((test_ip, 443))
        success = True
    except (socket.timeout, TimeoutError):
        success = False
    except (ConnectionRefusedError, ConnectionResetError):
        success = True
    finally:
        s.close()
    return success

def get_resolver_list(ip_version=0, kind='auto') -> List[str]:
    if kind == 'doh' or (kind == 'auto' and settings.DNS_PROTOCOL == 'doh'): return settings.DOH_RESOLVERS
    
    if kind == 'dnscombo':
        combo_res = []
        if settings.HAS_V6 is None: settings.HAS_V6 = test_network(6)
        if settings.HAS_V6: combo_res += settings.DNS_RESOLVERS_V6
        if settings.HAS_V4 is None: settings.HAS_V4 = test_network(4)
        if settings.HAS_V4: combo_res += settings.DNS_RESOLVERS_V4
        random.shuffle(combo_res)
        return combo_res
    
    if kind == 'dns' or (kind == 'auto' and settings.DNS_PROTOCOL in ['dns', 'dnsudp', 'dnstcp']):
        if ip_version == 4: return settings.DNS_RESOLVERS_V4
        if ip_version == 6: return settings.DNS_RESOLVERS_V6
        
        if settings.USE_IPV6:
            if settings.HAS_V6 is None: settings.HAS_V6 = test_network(6)
            if settings.HAS_V6: return settings.DNS_RESOLVERS_V6
        
        if settings.USE_IPV4:
            if settings.HAS_V4 is None: settings.HAS_V4 = test_network(4)
            if settings.HAS_V4: return settings.DNS_RESOLVERS_V4
        raise ValueError("Neither IPv4 nor IPv6 appear to be working/enabled, can't auto-populate server list via helpers.get_resolver_list")
    raise AttributeError("Invalid kind specified to get_resolver_list, must be either: doh, dns, auto")

def pick_server(*servers: Union[str, List[str]], kind='auto', ip_version=0):
    servers = list(servers)
    if len(servers) == 0:
        servers = get_resolver_list(ip_version, kind)
    if len(servers) == 1 and isinstance(servers[0], (list, set)):
        servers = list(servers[0])
    return sysrandom.choice(servers)

