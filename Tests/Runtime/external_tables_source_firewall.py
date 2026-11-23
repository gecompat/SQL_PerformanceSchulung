"""Install and verify the External Tables SQL source ingress policy."""

from __future__ import annotations

import json
from math import isfinite
import os
import re
import sys
from time import monotonic

from dgn004_capture_runner import CaptureRunnerError, CaptureTimeoutError, collect_bounded_process
from external_tables_guest_apt import require_guest_detached
from external_tables_guest_network import GuestNetwork
from external_tables_pilot_sql import SOURCE_PORT


_TABLE = "sqlperf_external_source"
_CHAIN = "inbound"
_FAMILY = "inet"
_NFT = "/usr/sbin/nft"
_LIST = ["--json", "list", "table", _FAMILY, _TABLE]


def source_firewall_batch(network: GuestNetwork, interface: str) -> bytes:
    """Produce a single atomic transaction without changing unrelated policies."""
    _require_interface(interface)
    return (
        f"create table {_FAMILY} {_TABLE}\n"
        f"add chain {_FAMILY} {_TABLE} {_CHAIN} {{ type filter hook input priority 0; policy drop; }}\n"
        f'add rule {_FAMILY} {_TABLE} {_CHAIN} iifname "lo" accept\n'
        f'add rule {_FAMILY} {_TABLE} {_CHAIN} iifname "{interface}" '
        f"ip saddr {network.query.ip} ip daddr {network.source.ip} tcp dport {SOURCE_PORT} accept\n"
    ).encode("ascii")


def install_source_firewall(network: GuestNetwork, interface: str, deadline: float) -> None:
    """Install once in the verified, still detached source guest."""
    if sys.platform != "linux" or os.geteuid() != 0:
        raise ValueError("source firewall installation requires the prepared Linux guest")
    require_guest_detached()
    _run_nft(["--file", "-"], source_firewall_batch(network, interface), deadline)
    verify_source_firewall(network, interface, deadline)
    require_guest_detached()


def verify_source_firewall(network: GuestNetwork, interface: str, deadline: float) -> None:
    """Read the actual configured ingress policy before the pilot opens SQL."""
    document = json.loads(_run_nft(_LIST, b"", deadline))
    verify_source_firewall_snapshot(network, interface, document)


def verify_source_firewall_snapshot(network: GuestNetwork, interface: str, document: object) -> None:
    _require_interface(interface)
    if not isinstance(document, dict) or set(document) != {"nftables"}:
        raise ValueError("expected the source nftables JSON snapshot")
    entries = document["nftables"]
    if not isinstance(entries, list) or len(entries) != 5 or any(
        not isinstance(entry, dict) or len(entry) != 1 for entry in entries
    ) or not isinstance(entries[0].get("metainfo"), dict):
        raise ValueError("source nftables snapshot has unexpected entries")

    table_fields = {"family": _FAMILY, "table": _TABLE}
    rule_fields = {**table_fields, "chain": _CHAIN}
    metadata = {"meta": {"key": "iifname"}}
    expected = [
        {"table": {"family": _FAMILY, "name": _TABLE}},
        {"chain": {**table_fields, "name": _CHAIN, "type": "filter", "hook": "input", "prio": 0, "policy": "drop"}},
        {"rule": {**rule_fields, "expr": [_match(metadata, "lo"), {"accept": None}]}},
        {"rule": {**rule_fields, "expr": [
            _match(metadata, interface),
            _match({"payload": {"protocol": "ip", "field": "saddr"}}, str(network.query.ip)),
            _match({"payload": {"protocol": "ip", "field": "daddr"}}, str(network.source.ip)),
            _match({"payload": {"protocol": "tcp", "field": "dport"}}, SOURCE_PORT),
            {"accept": None},
        ]}},
    ]
    actual = []
    for entry in entries[1:]:
        kind, fields = next(iter(entry.items()))
        if not isinstance(fields, dict):
            raise ValueError("source nftables snapshot has invalid rule data")
        actual.append({kind: {key: value for key, value in fields.items() if key != "handle"}})
    if actual != expected:
        raise ValueError("source nftables policy differs from the fixed ingress rules")


def _require_interface(interface: str) -> None:
    if not isinstance(interface, str) or interface == "lo" or re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,14}", interface) is None:
        raise ValueError("expected one configured private source interface name")


def _match(left: dict, right: str | int) -> dict:
    return {"match": {"op": "==", "left": left, "right": right}}


def _run_nft(options: list[str], payload: bytes, deadline: float) -> bytes:
    remaining = deadline - monotonic()
    if not isfinite(remaining) or remaining <= 0:
        raise TimeoutError("source firewall check deadline exceeded")
    try:
        result = collect_bounded_process(
            [_NFT, *options], input_bytes=payload, environment={"LC_ALL": "C"},
            timeout_seconds=min(5, remaining), stdout_limit_bytes=65_536, stderr_limit_bytes=4096,
        )
    except CaptureTimeoutError:
        raise TimeoutError("source firewall check deadline exceeded") from None
    except CaptureRunnerError:
        raise OSError("source firewall operation could not be confirmed") from None
    if result.returncode or result.stderr or monotonic() >= deadline:
        raise OSError("source firewall operation could not be confirmed")
    return result.stdout
