from copy import deepcopy
from ipaddress import IPv4Interface
import json
from pathlib import Path
import sys
from time import monotonic
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_guest_network import GuestNetwork
from external_tables_source_firewall import install_source_firewall, source_firewall_batch, verify_source_firewall_snapshot


BLOCK = 0xC0A86400
NETWORK = GuestNetwork(IPv4Interface((BLOCK + 2, 29)), IPv4Interface((BLOCK + 3, 29)))
NAME = "sqlperf_external_source"
TABLE = {"family": "inet", "table": NAME}
RULE = {**TABLE, "chain": "inbound"}


def match(expression, value):
    return {"match": {"op": "==", "left": expression, "right": value}}


SNAPSHOT = {"nftables": [
    {"metainfo": {"version": "1.0.9", "json_schema_version": 1}},
    {"table": {"family": "inet", "name": NAME, "handle": 1}},
    {"chain": {**TABLE, "name": "inbound", "hook": "input", "type": "filter", "prio": 0,
               "policy": "drop", "handle": 1}},
    {"rule": {**RULE, "handle": 2, "expr": [match({"meta": {"key": "iifname"}}, "lo"), {"accept": None}]}},
    {"rule": {**RULE, "handle": 3, "expr": [
        match({"meta": {"key": "iifname"}}, "eth0"),
        match({"payload": {"protocol": "ip", "field": "saddr"}}, str(NETWORK.query.ip)),
        match({"payload": {"protocol": "ip", "field": "daddr"}}, str(NETWORK.source.ip)),
        match({"payload": {"protocol": "tcp", "field": "dport"}}, 1433),
        {"accept": None},
    ]}},
]}


class SourceFirewallTests(TestCase):
    def test_transaction_creates_owned_table_and_limits_tcp_to_exact_endpoints(self):
        commands = source_firewall_batch(NETWORK, "eth0").decode("ascii").splitlines()
        self.assertEqual(commands[0], f"create table inet {NAME}")
        self.assertEqual(len(commands), 4)
        self.assertIn("policy drop", commands[1])
        self.assertTrue(commands[2].endswith('iifname "lo" accept'))
        self.assertTrue(commands[3].endswith(
            f'iifname "eth0" ip saddr {NETWORK.query.ip} ip daddr {NETWORK.source.ip} tcp dport 1433 accept'
        ))
        for invalid in ("lo", '"; accept', "", "../eth0"):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "interface name"):
                source_firewall_batch(NETWORK, invalid)

    def test_reads_exact_policy_and_rejects_weaker_match_or_extra_accept(self):
        verify_source_firewall_snapshot(NETWORK, "eth0", SNAPSHOT)
        for alter in ("policy", "extra", "address", "port", "interface"):
            with self.subTest(alter=alter), self.assertRaises(ValueError):
                candidate = deepcopy(SNAPSHOT)
                rules = candidate["nftables"]
                if alter == "policy":
                    rules[2]["chain"]["policy"] = "accept"
                elif alter == "extra":
                    rules.append({"rule": {**RULE, "expr": [{"accept": None}]}})
                else:
                    expression = rules[4]["rule"]["expr"]
                    index = {"address": 1, "port": 3, "interface": 0}[alter]
                    expression[index]["match"]["right"] = {"address": str(NETWORK.query.ip + 1),
                                                            "port": 1434, "interface": "eth1"}[alter]
                verify_source_firewall_snapshot(NETWORK, "eth0", candidate)

    def test_installation_does_not_apply_to_an_attached_guest(self):
        calls = Mock()
        calls.nft.side_effect = [b"", json.dumps(SNAPSHOT).encode("ascii")]
        with (
            patch("external_tables_source_firewall.sys", SimpleNamespace(platform="linux")),
            patch("external_tables_source_firewall.os", SimpleNamespace(geteuid=lambda: 0)),
            patch("external_tables_source_firewall.require_guest_detached", calls.detached),
            patch("external_tables_source_firewall._run_nft", calls.nft),
        ):
            install_source_firewall(NETWORK, "eth0", monotonic() + 3)
            self.assertEqual([call[0] for call in calls.mock_calls], ["detached", "nft", "nft", "detached"])
            calls.nft.reset_mock()
            calls.detached.side_effect = ValueError("unexpected attached interface")
            with self.assertRaisesRegex(ValueError, "unexpected attached"):
                install_source_firewall(NETWORK, "eth0", monotonic() + 3)
            calls.nft.assert_not_called()


if __name__ == "__main__":
    main()
