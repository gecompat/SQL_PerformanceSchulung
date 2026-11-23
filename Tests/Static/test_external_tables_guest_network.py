from copy import deepcopy
from ipaddress import IPv4Interface
from pathlib import Path
import sys
from unittest import TestCase, main

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_guest_network import GuestNetwork, verify_network_snapshot
from external_tables_pilot_sql import Role


LAB_BLOCK = 0xC0A86300
NETWORK = GuestNetwork(IPv4Interface((LAB_BLOCK + 2, 29)), IPv4Interface((LAB_BLOCK + 3, 29)))
SOURCE_IP = str(NETWORK.source.ip)
INTERFACES = [
    {"ifname": "lo", "flags": ["LOOPBACK", "UP"]},
    {"ifname": "eth0", "flags": ["BROADCAST", "UP"], "addr_info": [
        {"family": "inet", "local": SOURCE_IP, "prefixlen": 29, "scope": "global"},
        {"family": "inet6", "local": "fe80::a", "prefixlen": 64, "scope": "link"},
    ]},
]
IPV4 = [
    {"dst": str(NETWORK.source.network), "dev": "eth0", "scope": "link", "prefsrc": SOURCE_IP},
    {"type": "local", "dst": "127.0.0.0/8", "dev": "lo", "table": "local"},
    {"type": "local", "dst": SOURCE_IP, "dev": "eth0", "table": "local"},
    {"type": "broadcast", "dst": str(NETWORK.source.network.broadcast_address), "dev": "eth0", "table": "local"},
]
IPV6 = [
    {"dst": "::1", "dev": "lo", "table": "local"},
    {"dst": "fe80::/64", "dev": "eth0"},
    {"type": "local", "dst": "fe80::a", "dev": "eth0", "table": "local"},
    {"type": "multicast", "dst": "ff00::/8", "dev": "eth0", "table": "local"},
]


class GuestNetworkTests(TestCase):
    def test_exact_network_and_usable_distinct_endpoints(self):
        verify_network_snapshot(NETWORK.source, INTERFACES, IPV4, IPV6)
        self.assertEqual(NETWORK.address(Role.QUERY).ip, NETWORK.query.ip)
        for source, query in (
            (0x7F000002, 0x7F000003), (0xA9FE0102, 0xA9FE0103),
            (LAB_BLOCK + 2, LAB_BLOCK + 2), (LAB_BLOCK + 2, LAB_BLOCK + 7),
            (LAB_BLOCK + 2, LAB_BLOCK + 11),
        ):
            with self.subTest(source=source, query=query), self.assertRaises(ValueError):
                GuestNetwork(IPv4Interface((source, 29)), IPv4Interface((query, 29)))

    def test_wrong_address_and_extra_interface_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "exact configured address"):
            verify_network_snapshot(NETWORK.query, INTERFACES, IPV4, IPV6)
        with self.assertRaisesRegex(ValueError, "exactly one private"):
            verify_network_snapshot(NETWORK.source, INTERFACES + [{"ifname": "eth1"}], IPV4, IPV6)
        altered = deepcopy(INTERFACES)
        altered[1]["addr_info"].append({"family": "inet6", "local": "2001:db8::1", "scope": "global"})
        with self.assertRaisesRegex(ValueError, "unexpected address"):
            verify_network_snapshot(NETWORK.source, altered, IPV4, IPV6)

    def test_default_routes_other_tables_and_external_next_hops_are_rejected(self):
        for extra, family in (
            ({"dst": "default", "dev": "eth0", "table": 23}, 4),
            ({"dst": str(IPv4Interface((0xC6336400, 24)).network), "dev": "eth0", "table": 23}, 4),
            ({"dst": str(NETWORK.query.ip + 1), "dev": "eth0", "gateway": str(NETWORK.query.ip)}, 4),
            ({"dst": "default", "dev": "eth0", "table": 23}, 6),
            ({"dst": "2001:db8::/32", "dev": "eth0", "table": 23}, 6),
        ):
            with self.subTest(extra=extra, family=family), self.assertRaises(ValueError):
                verify_network_snapshot(
                    NETWORK.source, INTERFACES,
                    IPV4 + [extra] if family == 4 else IPV4,
                    IPV6 + [extra] if family == 6 else IPV6,
                )


if __name__ == "__main__":
    main()
