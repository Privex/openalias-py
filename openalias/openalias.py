import textwrap
from typing import List, Optional, Union
import dns.message
import dns.query
import dns.rdatatype
import dns.resolver
from dns.rrset import RRset
from openalias.version import LICENSE, REPO, VERSION
from privex.helpers import empty, empty_if, DictDataClass, DictObject, ErrHelpParser, retry_on_err
from privex.helpers.exceptions import NotFound
from .helpers import pick_server, get_resolver_list, print_err
from openalias import settings
from dataclasses import dataclass, field
from rich import print as rprint
from rich.table import Table, Column
from rich.console import Console
from privex.loghelper import LogHelper
import requests
import logging
import re
import sys

log = logging.getLogger(__name__)
RE_COIN = re.compile(r'oa1:([a-zA-Z0-9_-]+)')
# RE_ADDRESS = re.compile(r'recipient_address=([a-zA-Z0-9_+@:$£€%.,#! -]+);')
RE_ADDRESS = re.compile(r'recipient_address=([^\;]+);')
RE_NAME = re.compile(r'recipient_name=([^\;]+);')
# RE_OTHER = re.compile(r'(.*)=(.*);')
# RE_OTHER = re.compile(r'([^=]+)=([^\;]+); ?')
RE_OTHER_COIN = re.compile(r'(oa1:([^\ ]+))? ?([^=]+)=([^\;]+); ?')
RE_OTHER = re.compile(r'([^=]+)=([^\;]+); ?')

console = Console()

@retry_on_err(delay=1)
def doh_lookup(domain: str, resolver: str = None, rtype=dns.rdatatype.TXT):
    # If no resolver is passed, automatically select one from the settings resolver list
    if empty(resolver):
        log.debug("Selecting DNS-over-HTTPS Server...")
        resolver = pick_server(*settings.DOH_RESOLVERS)
    
    log.info(f"Looking up {rtype!r} records for domain '{domain}' using DoH resolver '{resolver}'")

    results = []
    with requests.sessions.Session() as session:
        q = dns.message.make_query(domain, rtype)
        r = dns.query.https(q, resolver, session=session)
        for answer in r.answer:
            answer: RRset
            itms = list(answer.items)
            for i in itms:
                results.append(i.to_text().strip('"'))
            # print(repr(answer))
    log.debug(f"Obtained {len(results)} records for domain '{domain}': {results!s}")
    return results

@retry_on_err(delay=1)
def dns_lookup(domain: str, resolver: Union[str, list] = None, proto: str = None, rtype='TXT'):

    if empty(proto):
        if settings.DNS_PROTOCOL == 'dnstcp':
            proto = 'tcp'
        proto = 'udp'

    if empty(resolver):
        resolver = get_resolver_list(kind='dnscombo')
    
    rsv = dns.resolver.Resolver(configure=False)
    rsv.nameservers = resolver if isinstance(resolver, list) else [resolver]
    log.info(f"Getting {rtype} records from domain {domain} using resolver(s) {resolver} with standard DNS (proto: {proto})")
    answer = rsv.resolve(domain, rtype, tcp=proto == 'tcp')

    results = []
    # for rr in rrset:
    itms = list(answer.rrset.items)
    for i in itms:
        results.append(i.to_text().strip('"') if rtype in [dns.rdatatype.TXT, 'TXT', 'txt'] else i.to_text())

    # qname = dns.name.from_text(domain)
    # q = dns.message.make_query(qname, rtype)

    # if proto == 'udp':
    #     r = dns.query.udp(q, resolver)
    # else:
    #     r = dns.query.tcp(q, resolver)
    
    # ns_rrset = r.find_rrset(r.answer, qname, dns.rdataclass.IN, rtype)
    # results = []
    # for answer in ns_rrset:
    #     answer: RRset
    #     itms = list(answer.items)
    #     for i in itms:
    #         results.append(i.to_text().strip('"') if rtype == dns.rdatatype.TXT else i.to_text())
    return results

@dataclass
class CoinResult(DictDataClass):
    recipient_address: str = None
    recipient_name: str = None
    coin: str = None
    raw_data: Union[DictObject, dict] = field(default_factory=DictObject)
    _DEF_FIELDS =  ['recipient_address', 'recipient_name', 'coin', 'raw_data', '_DEF_FIELDS']

    @property
    def extra_data(self) -> dict:
        """
        Return a dict of only extra fields in raw_data, i.e. those that don't exist as a
        specified field on the dataclass, so no recipient_address, recipient_name, etc.
        """
        return {k: v for k, v in self.raw_data.items() if k not in self._DEF_FIELDS}

    @classmethod
    def read_record(cls, rec: str) -> "CoinResult":
        """
        
            >>> c = CoinResult.read_record('oa1:doge recipient_address=D9XEBJF55kN3XWEdDr5Z19GHMmgh7nrsEQ; recipient_name=Privex Donations;')
            >>> c.recipient_address
            'D9XEBJF55kN3XWEdDr5Z19GHMmgh7nrsEQ'
            >>> c.coin
            'doge'
        
        """
        srec = rec.split()
        coin = srec[0].split(':')[1]
        rest = ' '.join(srec[1:])
        allfields = RE_OTHER.findall(rest)
        field_dict = {}
        for k, v in allfields:
            field_dict[k] = v
        field_dict['coin'] = coin
        return cls.from_dict(field_dict)

    @classmethod
    def read_records(cls, *rec: str) -> List["CoinResult"]:
        return [cls.read_record(r) for r in rec]

def get_all_coins(domain: str, resolver: str = None, proto: str = None) -> List[CoinResult]:
    proto = empty_if(proto, settings.DNS_PROTOCOL)
    
    if proto in ['dns', 'dnsudp', 'dnstcp']:
        rawres = dns_lookup(domain, resolver=resolver, proto='udp' if proto in ['dns', 'dnsudp'] else 'tcp')
    else:
        rawres = doh_lookup(domain, resolver=resolver)
    
    oares = [r for r in rawres if r.startswith('oa1:')]
    return CoinResult.read_records(*oares)

def lookup_coin(results: List[Union[str, CoinResult]], coin: str, fail=False) -> Optional[CoinResult]:
    if empty(results, itr=True):
        if not fail: return None
        raise ValueError("openalias.lookup_coin received an empty list! Cannot lookup coin")
    if isinstance(results[0], str):
        cleanresults = [r for r in results if r.startswith('oa1:')]
        results = CoinResult.read_records(*cleanresults)
    
    for c in results:
        if c.coin.lower() == coin.lower():
            return c
    
    if fail: raise NotFound(f"Coin '{coin}' was not found in results")
    return None

def cmd_get(args):
    coin, domain, plain, resolver, proto = args.coin, args.domain, args.plain, args.resolver, args.protocol

    coins = get_all_coins(domain, resolver, proto)

    try:
        c = lookup_coin(coins, coin, fail=True)
    except (ValueError, NotFound) as e:
        print_err(f"[red]Coin '{coin}' not found in results for domain '{domain}'")
        return sys.exit(1)

    if plain:
        print(c.recipient_address)
        return
    
    rprint(f"[cyan][bold]Address:[/bold] {c.recipient_address}[/]")
    rprint(f"[cyan][bold]Coin:[/bold] {c.coin}[/]")
    rprint(f"[cyan][bold]Recipient Name:[/bold] {c.recipient_name}[/]")
    rprint(f"[cyan][bold]Raw Data:[/bold] {c.raw_data}[/]")


def cmd_list(args):
    domain, plain, resolver, proto = args.domain, args.plain, args.resolver, args.protocol

    coins = get_all_coins(domain, resolver, proto)

    tb = Table(title=f"OpenAlias records for '{domain}'")
    tb.add_column('Coin', style="cyan")
    tb.add_column('Address', style="green")
    tb.add_column('Name', style="yellow")
    if not args.no_extra_fields:
        tb.add_column('Extra Data', style="magenta")

    for c in coins:
        if plain:
            if args.no_extra_fields:
                print(c.coin, c.recipient_address, c.recipient_name, sep=', ')
            else:
                print(c.coin, c.recipient_address, c.recipient_name, str(c.extra_data), sep=', ')
            continue
        
        if args.no_extra_fields:
            tb.add_row(c.coin, c.recipient_address, c.recipient_name)
        else:
            tb.add_row(c.coin, c.recipient_address, c.recipient_name, str(c.extra_data))
    
    if not plain:
        console.print(tb)


def handle_command():
    parser = ErrHelpParser(
        description=textwrap.dedent(f"""
        OpenAlias.py Version v{VERSION}
        (C) 2023 Privex Inc. https://www.privex.io
        License: {LICENSE}
        Repo: {REPO}
        """),
        usage=textwrap.dedent(f"""
        Usage:

            # Get the XMR address for privex.io via DNS-over-HTTPS default resolver list
            {sys.argv[0]} get privex.io xmr

            # Get JUST the address for XMR on privex.io (useful for programmatic use)
            # and use the DoH resolver https://dns.privex.io
            {sys.argv[0]} -r https://dns.privex.io get -p privex.io xmr
            
            # Get JUST the address for XMR on privex.io (useful for programmatic use)
            {sys.argv[0]} get -p privex.io xmr

            # Get JUST the address for XMR on privex.io and be verbose (print debug logging)
            {sys.argv[0]} -v get -p privex.io xmr

            # Get the LTC record from example.com using plain DNS instead of DNS-over-HTTPS
            {sys.argv[0]} --protocol dns get example.com xmr

            # Get the EOS record using plain DNS with resolver 9.9.9.9 instead of DNS-over-HTTPS
            {sys.argv[0]} -P dns -r 9.9.9.9 get privex.io xmr

            # List all OpenAlias records on privex.io as a table
            {sys.argv[0]} list privex.io

            # List all OpenAlias records on privex.io as plain text (coin, address, name, extra data - comma separated),
            # query using plain DNS instead of DoH, and use the custom resolver 185.130.44.20
            {sys.argv[0]} -P dns -r 185.130.44.20 list -p privex.io

            # Don't show the Extra Fields column when listing privex.io
            {sys.argv[0]} list -x privex.io


        """)
    )

    parser.add_argument('-r', '--resolver', default=None, help="Use a specific resolver")
    parser.add_argument('-P', '--protocol', default=None, help="Use a given DNS protocol (dns, dnstcp, dnsudp, doh)")
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help="Verbose mode (enables DEBUG + logging)")
    parser.set_defaults(verbose=False)
    sp = parser.add_subparsers()

    get_sp = sp.add_parser('get', description="Get a specific cryptocurrency coin address for a given domain")
    get_sp.add_argument('domain', type=str)
    get_sp.add_argument('coin', type=str)
    get_sp.add_argument('-p', '--plain', action='store_true', default=False, help="Return just the address on it's own (for programmatic use)")
    get_sp.set_defaults(func=cmd_get, plain=False)

    list_sp = sp.add_parser('list', description="Get all cryptocurrency coins and their associated data for a given domain")
    list_sp.add_argument('domain', type=str)
    list_sp.add_argument('-p', '--plain', action='store_true', default=False, help="Return just the coin names + addresses on their own (for programmatic use)")
    list_sp.add_argument('-x', '--no-extra-fields', action='store_true', default=False, help="Don't show non-standard fields in the results")

    list_sp.set_defaults(func=cmd_list, plain=False, no_extra_fields=False)

    args = parser.parse_args()

    if args.verbose:
        settings.DEBUG = True
        settings.LOG_LEVEL = logging.DEBUG
        settings.setup_logger(level=logging.DEBUG)
        # _log = logging.getLogger('openalias')
        # _log.setLevel(settings.LOG_LEVEL)
    # Resolves the error "'Namespace' object has no attribute 'func'
    # Taken from https://stackoverflow.com/a/54161510/2648583
    try:
        func = args.func
        func(args)
    except AttributeError as e:
        # if not sys.stdin.isatty():
        #     parse_stdin()
        #     sys.exit(0)
        parser.error(f'Too few arguments {str(e)}')
        sys.exit(1)

    