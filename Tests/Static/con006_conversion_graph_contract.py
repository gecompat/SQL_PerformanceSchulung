"""Offline contract checker for one supplied CON-006 conversion deadlock graph.

It validates graph shape and caller-supplied identity bindings only. It does
not acquire, authenticate, time, or attest to SQL Server evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
import xml.etree.ElementTree as ET


MAX_GRAPH_BYTES = 128 * 1024
_UNSIGNED = re.compile(r"[1-9][0-9]*\Z")


class Verdict(str, Enum):
    PASS = "PASS"
    NOT_PROVEN = "NOT_PROVEN"
    FAIL = "FAIL"


@dataclass(frozen=True)
class GraphIdentity:
    database_id: int
    actor_spids: tuple[tuple[str, int], ...]
    object_name: str
    index_name: str
    hobt_id: str | None = None


@dataclass(frozen=True)
class GraphResult:
    verdict: Verdict
    reasons: tuple[str, ...]


def _valid_identity(identity: object) -> bool:
    if type(identity) is not GraphIdentity:
        return False
    if type(identity.database_id) is not int or identity.database_id <= 0:
        return False
    if type(identity.actor_spids) is not tuple or len(identity.actor_spids) != 2:
        return False
    if any(type(pair) is not tuple or len(pair) != 2 for pair in identity.actor_spids):
        return False
    roles = [pair[0] for pair in identity.actor_spids]
    if any(type(role) is not str for role in roles) or set(roles) != {"ACTOR_A", "ACTOR_B"}:
        return False
    spids = [pair[1] for pair in identity.actor_spids]
    if (any(type(spid) is not int or spid <= 0 for spid in spids)
            or spids[0] == spids[1]):
        return False
    if type(identity.object_name) is not str or not identity.object_name.strip():
        return False
    if type(identity.index_name) is not str or not identity.index_name.strip():
        return False
    if identity.hobt_id is not None and (
        type(identity.hobt_id) is not str or not _UNSIGNED.fullmatch(identity.hobt_id)
    ):
        return False
    return True


def _single(parent: ET.Element, path: str, label: str, failures: list[str]) -> ET.Element | None:
    matches = parent.findall(path)
    if len(matches) != 1:
        failures.append(f"{label} must contain exactly one {path.rsplit('/', 1)[-1]}")
        return None
    return matches[0]


def _nonempty_attr(node: ET.Element, name: str, label: str, failures: list[str]) -> str | None:
    value = node.get(name)
    if value is None or not value.strip():
        failures.append(f"{label} is missing {name}")
        return None
    return value


def _unsigned_attr(node: ET.Element, name: str, label: str, failures: list[str]) -> int | None:
    value = _nonempty_attr(node, name, label, failures)
    if value is None:
        return None
    if not _UNSIGNED.fullmatch(value):
        failures.append(f"{label} {name} must be a positive decimal integer")
        return None
    return int(value)


def evaluate_conversion_graph(graph_xml: str | bytes | None, identity: GraphIdentity | None) -> GraphResult:
    """Check the two-actor, same-key S-to-X conversion cycle in one deadlock XML."""
    if graph_xml is None:
        return GraphResult(Verdict.NOT_PROVEN, ("deadlock graph evidence is missing",))
    if identity is None:
        return GraphResult(Verdict.NOT_PROVEN, ("owned database/object/session identity is missing",))
    if not _valid_identity(identity):
        return GraphResult(Verdict.FAIL, ("expected graph identity is invalid",))
    if type(graph_xml) is bytes:
        if len(graph_xml) > MAX_GRAPH_BYTES:
            return GraphResult(Verdict.FAIL, ("graph XML exceeds the fixed limit",))
        try:
            text = graph_xml.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            return GraphResult(Verdict.FAIL, ("graph XML must be valid UTF-8",))
    elif type(graph_xml) is str:
        text = graph_xml
    else:
        return GraphResult(Verdict.FAIL, ("graph XML must be text or UTF-8 bytes",))

    if len(text) > MAX_GRAPH_BYTES:
        return GraphResult(Verdict.FAIL, ("graph XML exceeds the fixed limit",))
    try:
        raw = text.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        return GraphResult(Verdict.FAIL, ("graph XML contains invalid Unicode",))
    if not raw or len(raw) > MAX_GRAPH_BYTES:
        return GraphResult(Verdict.FAIL, ("graph XML size is empty or exceeds the fixed limit",))
    if "<!doctype" in text.lower() or "<!entity" in text.lower():
        return GraphResult(Verdict.FAIL, ("DTD and entity declarations are outside this XML profile",))
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return GraphResult(Verdict.FAIL, ("graph XML is malformed",))
    if root.tag != "deadlock":
        return GraphResult(Verdict.FAIL, ("root element must be deadlock",))

    failures: list[str] = []
    process_list = _single(root, "process-list", "deadlock", failures)
    resource_list = _single(root, "resource-list", "deadlock", failures)
    victim_list = _single(root, "victim-list", "deadlock", failures)
    if process_list is None or resource_list is None or victim_list is None:
        return GraphResult(Verdict.FAIL, tuple(failures))

    processes = process_list.findall("process")
    if len(processes) != 2:
        failures.append("conversion variant requires exactly two deadlock processes")
    process_by_id: dict[str, ET.Element] = {}
    for process in processes:
        process_id = _nonempty_attr(process, "id", "process", failures)
        if process_id is not None:
            if process_id in process_by_id:
                failures.append("process IDs must be unique")
            process_by_id[process_id] = process
        current_db = _unsigned_attr(process, "currentdb", "process", failures)
        spid = _unsigned_attr(process, "spid", "process", failures)
        if current_db is not None and current_db != identity.database_id:
            failures.append("process currentdb differs from the supplied owned database")
        if spid is not None and spid not in {value for _, value in identity.actor_spids}:
            failures.append("deadlock process SPID is outside the two supplied actors")
    observed_spids = [
        _unsigned_attr(process, "spid", "process", [])
        for process in processes
    ]
    expected_spids = {value for _, value in identity.actor_spids}
    if len(processes) == 2 and set(observed_spids) != expected_spids:
        failures.append("deadlock processes do not bind exactly to ACTOR_A and ACTOR_B SPIDs")

    victims = victim_list.findall("victimProcess")
    victim_id = _nonempty_attr(victims[0], "id", "victimProcess", failures) if len(victims) == 1 else None
    if len(victims) != 1:
        failures.append("conversion variant requires exactly one deadlock victim")
    if victim_id is not None and victim_id not in process_by_id:
        failures.append("victim process is not present in the deadlock process list")

    target_resources = [
        node for node in resource_list
        if node.tag == "keylock"
        and node.get("objectname") == identity.object_name
        and node.get("indexname") == identity.index_name
        and node.get("dbid") == str(identity.database_id)
        and (identity.hobt_id is None or node.get("hobtid") == identity.hobt_id)
    ]
    if len(target_resources) != 1:
        failures.append("graph must contain exactly one keylock for the supplied database, object, index, and HoBT")
    else:
        target = target_resources[0]
        owners = target.findall("owner-list/owner")
        waiters = target.findall("waiter-list/waiter")
        expected_ids = set(process_by_id)
        owner_ids = [node.get("id") for node in owners]
        waiter_ids = [node.get("id") for node in waiters]
        if len(owners) != 2 or set(owner_ids) != expected_ids or any(node.get("mode") != "S" for node in owners):
            failures.append("the same keylock must show both actor processes owning S locks")
        if (len(waiters) != 2 or set(waiter_ids) != expected_ids
                or any(node.get("mode") != "X" or node.get("requestType") != "convert" for node in waiters)):
            failures.append("the same keylock must show both actor processes requesting X conversion")
        if set(owner_ids) != set(waiter_ids) or len(owner_ids) != len(waiter_ids):
            failures.append("S owners and X conversion waiters must be the same two processes")

    if failures:
        return GraphResult(Verdict.FAIL, tuple(failures))
    return GraphResult(Verdict.PASS, ())
