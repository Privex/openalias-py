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
import unittest
from os.path import abspath, dirname, join
from openalias import CoinResult, doh_lookup, dns_lookup
from openalias import openalias

BASE_DIR = dirname(abspath(__file__))


RECORD_1 = 'oa1:ltc recipient_address=MDRRb9pdLs6nXQ91VNfJEN68ohHSwWvscv; recipient_name=Privex Donations;'
RECORD_2 = 'oa1:bch recipient_address=bitcoincash:qr6ss5pnnx9wad32j7lhulwp6k6we60gyuzsqc6pyj; recipient_name=Privex Donations;'

class TestConvertRecord(unittest.TestCase):

    def test_record_1(self):
        """Test converting a simple OA record into a :class:`.CoinResult`"""
        c = CoinResult.read_record(RECORD_1)
        self.assertEqual(c.coin, 'ltc')
        self.assertEqual(c.recipient_address, 'MDRRb9pdLs6nXQ91VNfJEN68ohHSwWvscv')
        self.assertEqual(c.recipient_name, 'Privex Donations')

    def test_record_2(self):
        """Test converting an OA record with a BCH formatted address"""
        c = CoinResult.read_record(RECORD_2)
        self.assertEqual(c.coin, 'bch')
        self.assertEqual(c.recipient_address, 'bitcoincash:qr6ss5pnnx9wad32j7lhulwp6k6we60gyuzsqc6pyj')
        self.assertEqual(c.recipient_name, 'Privex Donations')

    def test_multi_record(self):
        """Test converting multiple OA records at once using read_records"""
        cs = CoinResult.read_records(RECORD_1, RECORD_2)

        self.assertEqual(len(cs), 2)
        self.assertIsInstance(cs, list)
        self.assertEqual(cs[0].coin, 'ltc')
        self.assertEqual(cs[0].recipient_address, 'MDRRb9pdLs6nXQ91VNfJEN68ohHSwWvscv')
        self.assertEqual(cs[0].recipient_name, 'Privex Donations')
        self.assertEqual(cs[1].coin, 'bch')
        self.assertEqual(cs[1].recipient_address, 'bitcoincash:qr6ss5pnnx9wad32j7lhulwp6k6we60gyuzsqc6pyj')
        self.assertEqual(cs[1].recipient_name, 'Privex Donations')


class TestDNSLookup(unittest.TestCase):
    def test_doh_lookup(self):
        """Test a simple DoH lookup"""
        l = doh_lookup('privex.io')
        self.assertGreater(len(l), 0)
        self.assertIsInstance(l, list)
        self.assertIsInstance(l[0], str)
        
    def test_dns_lookup_udp(self):
        """Test a simple UDP DNS lookup"""
        l = dns_lookup('privex.io', proto='udp')
        self.assertGreater(len(l), 0)
        self.assertIsInstance(l, list)
        self.assertIsInstance(l[0], str)
    
    def test_dns_lookup_tcp(self):
        """Test a simple TCP DNS lookup"""
        l = dns_lookup('privex.io', proto='tcp')
        self.assertGreater(len(l), 0)
        self.assertIsInstance(l, list)
        self.assertIsInstance(l[0], str)
    

class TestOACore(unittest.TestCase):
    def test_coin_lookup_dns(self):
        l = dns_lookup('privex.io')
        res = openalias.lookup_coin(l, 'xmr')
        self.assertIsInstance(res, CoinResult)
        self.assertEqual(res.coin, 'xmr')
    
    def test_coin_lookup_doh(self):
        l = doh_lookup('privex.io')
        res = openalias.lookup_coin(l, 'xmr')
        self.assertIsInstance(res, CoinResult)
        self.assertEqual(res.coin, 'xmr')
    

if __name__ == '__main__':
    unittest.main()
