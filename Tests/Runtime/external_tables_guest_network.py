"""Read-only validation of the post-attachment External Tables guest network."""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import IPv4Interface, IPv4Network, IPv6Address, IPv6Network, ip_network
import json
from math import isfinite
from time import monotonic

from dgn004_capture_runner import CaptureRunnerError, CaptureTimeoutError, collect_bounded_process
from external_tables_pilot_sql import Role


_PRIVATE = (IPv4Network((0x0A000000, 8)), IPv4Network((0xAC100000, 12)), IPv4Network((0xC0A80000, 16)))
_LOOPBACK_V4 = IPv4Network("127.0.0.0/8")
_LINK_LOCAL_V6 = ip_network("fe80::/10")
_LOOPBACK_V6 = ip_network("::1/128")
_MULTICAST_V6 = ip_network("ff00::/8")


@dataclass(frozen=True)
class GuestNetwork:
    source: IPv4Interface
    query: IPv4Interface

    def __post_init__(self) -> None:
        if not isinstance(self.source, IPv4Interface) or not isinstance(self.query, IPv4Interface):
            raise ValueError("expected two explicit IPv4 interface addresses")
        network = self.source.network
        if (
            self.query.network != network or self.source.ip == self.query.ip
            or not any(network.subnet_of(block) for block in _PRIVATE)
            or any(endpoint.ip in (network.network_address, network.broadcast_address)
                   for endpoint in (self.source, self.query))
        ):
            raise ValueError("expected distinct guest addresses in one RFC 1918 subnet")

    def address(self, role: Role) -> IPv4Interface:
        return {Role.SOURCE: self.source, Role.QUERY: self.query}[role]


def verify_guest_network(network: GuestNetwork, role: Role, deadline: float) -> str:
    """Check addresses and both IP routing tables in one of the prepared guests."""
    interfaces = _ip(["address", "show"], deadline)
    ipv4_routes = _ip(["-4", "route", "show", "table", "all"], deadline)
    ipv6_routes = _ip(["-6", "route", "show", "table", "all"], deadline)
    return verify_network_snapshot(network.address(role), interfaces, ipv4_routes, ipv6_routes)


def verify_network_snapshot(expected: IPv4Interface, interfaces: list[dict], ipv4: list[dict], ipv6: list[dict]) -> str:
    names = [record.get("ifname") for record in interfaces]
    if len(names) != 2 or "lo" not in names or names[0] == names[1]:
        raise ValueError("expected loopback and exactly one private guest interface")
    link = next(record for record in interfaces if record["ifname"] != "lo")
    device = link.get("ifname")
    if not isinstance(device, str) or not device or "UP" not in link.get("flags", []):
        raise ValueError("the private guest interface is not up")
    observed = []
    for address in link.get("addr_info", []):
        family, local, prefix = address.get("family"), address.get("local"), address.get("prefixlen")
        if family == "inet" and address.get("scope") == "global":
            observed.append(IPv4Interface(f"{local}/{prefix}"))
        elif family != "inet6" or address.get("scope") != "link" or IPv6Address(local) not in _LINK_LOCAL_V6:
            raise ValueError("guest interface has an unexpected address")
    if observed != [expected]:
        raise ValueError("guest interface does not have the exact configured address")

    connected = 0
    for record in ipv4:
        route = _route(record, 4, device)
        if record["dev"] == "lo" and route.subnet_of(_LOOPBACK_V4):
            continue
        if record["dev"] != device or not route.subnet_of(expected.network):
            raise ValueError("guest has a route outside the private IPv4 subnet")
        if (
            route == expected.network and record.get("type", "unicast") == "unicast"
            and record.get("scope") == "link" and record.get("prefsrc") == str(expected.ip)
            and record.get("table", "main") == "main"
        ):
            connected += 1
    if connected != 1:
        raise ValueError("guest has no unique connected private subnet route")

    for record in ipv6:
        route = _route(record, 6, device)
        if record["dev"] == "lo" and route.subnet_of(_LOOPBACK_V6):
            continue
        if record["dev"] == device and (route.subnet_of(_LINK_LOCAL_V6) or route.subnet_of(_MULTICAST_V6)):
            continue
        raise ValueError("guest has a route outside IPv6 link-local scope")

    return device


def _route(record: dict, family: int, device: str) -> IPv4Network | IPv6Network:
    if record.get("dev") not in ("lo", device) or any(key in record for key in ("gateway", "via", "nexthops")):
        raise ValueError("guest has an indirect or unknown route")
    destination = record.get("dst")
    if not isinstance(destination, str) or destination == "default":
        raise ValueError("guest has a default or unknown route")
    route = ip_network(destination, strict=True)
    if route.version != family:
        raise ValueError("guest route has an unexpected address family")
    return route


def _ip(options: list[str], deadline: float) -> list[dict]:
    remaining = deadline - monotonic()
    if not isfinite(remaining) or remaining <= 0:
        raise TimeoutError("guest network check deadline exceeded")
    try:
        result = collect_bounded_process(
            ["/usr/sbin/ip", "-json", *options], input_bytes=b"", environment={"LC_ALL": "C"},
            timeout_seconds=min(5, remaining), stdout_limit_bytes=65_536, stderr_limit_bytes=4096,
        )
    except CaptureTimeoutError:
        raise TimeoutError("guest network check deadline exceeded") from None
    except CaptureRunnerError:
        raise OSError("guest network capture did not complete") from None
    if result.returncode or result.stderr or monotonic() >= deadline:
        raise OSError("guest network capture did not complete")
    data = json.loads(result.stdout)
    if not isinstance(data, list) or any(not isinstance(record, dict) for record in data):
        raise ValueError("guest network capture did not return iproute2 JSON")
    return data
