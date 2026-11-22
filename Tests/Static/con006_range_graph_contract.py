"""Offline checker for a supplied CON-006 range deadlock graph.

This checks only caller-supplied XML and identity values. Lock modes are
reported by the engine graph and are required to be present, but this
prospective contract does not assume a particular RangeS/RangeI mode pair or
authenticate the source, run, actor outcomes, or SQL Server execution.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

from Tests.Static.con006_conversion_graph_contract import (
    MAX_GRAPH_BYTES, ActorOutcome, CaptureEvidence, GraphIdentity, GraphResult, Verdict,
    _evaluate_capture, _valid_actor_spids,
    _nonempty_attr, _single, _unsigned_attr, _valid_identity,
)


# SQL Server's documented compatibility matrix for common and key-range modes.
# Unknown modes fail closed: their presence in XML does not prove a wait edge.
_COMPATIBLE: dict[str, frozenset[str]] = {
    "S": frozenset({"S", "U", "RangeS-S", "RangeS-U", "RangeI-N"}),
    "U": frozenset({"S", "RangeS-S", "RangeI-N"}),
    "X": frozenset({"RangeI-N"}),
    "RangeS-S": frozenset({"S", "U", "RangeS-S", "RangeS-U"}),
    "RangeS-U": frozenset({"S", "RangeS-S"}),
    "RangeI-N": frozenset({"S", "U", "X", "RangeI-N"}),
    "RangeX-X": frozenset(),
}


@dataclass(frozen=True)
class RangeControlEvidence:
    """Caller-supplied serial-control observations; not source-authenticated."""

    expected_run_token: str | None
    observed_run_token: str | None
    actor_spids: tuple[tuple[str, int], ...] | None
    actor_outcomes: tuple[ActorOutcome, ...] | None
    expected_initial_keys: tuple[int, ...] | None
    expected_insertions: tuple[tuple[str, int], ...] | None
    observed_final_keys: tuple[int, ...] | None
    matching_deadlock_event_count: int | None
    observed_insertions: tuple[tuple[str, int], ...] | None = None


@dataclass(frozen=True)
class RangeInsertOutcome:
    role: str
    spid: int
    key: int
    outcome: str
    error_number: int | None


@dataclass(frozen=True)
class RangeCaptureEvidence:
    """Caller-supplied deadlock-arm insert outcomes and exact final keys."""

    capture: CaptureEvidence | None
    expected_initial_keys: tuple[int, ...] | None
    expected_insertions: tuple[tuple[str, int], ...] | None
    insert_outcomes: tuple[RangeInsertOutcome, ...] | None
    observed_final_keys: tuple[int, ...] | None


def evaluate_range_control(evidence: RangeControlEvidence | None) -> GraphResult:
    """Check both serial inserts, exact final keys, and no supplied deadlock event.

    A PASS means only that the caller-supplied values are internally consistent.
    It is not an authenticated capture or an SQL Server execution attestation.
    """
    if evidence is None:
        return GraphResult(Verdict.NOT_PROVEN, ("serial control evidence is missing",))
    if type(evidence) is not RangeControlEvidence:
        return GraphResult(Verdict.FAIL, ("serial control evidence must use the exact contract record",))

    missing: list[str] = []
    failures: list[str] = []
    for value, label in ((evidence.expected_run_token, "expected run token"),
                         (evidence.observed_run_token, "observed run token")):
        if value is None:
            missing.append(label)
        elif type(value) is not str or not value.strip():
            failures.append(f"{label} is invalid")
    if (type(evidence.expected_run_token) is str
            and type(evidence.observed_run_token) is str
            and evidence.expected_run_token != evidence.observed_run_token):
        failures.append("observed run token differs from the expected token")

    if evidence.actor_spids is None:
        missing.append("actor-to-SPID bindings")
    elif not _valid_actor_spids(evidence.actor_spids):
        failures.append("actor-to-SPID bindings are invalid")

    if evidence.actor_outcomes is None:
        missing.append("actor outcomes")
    elif (type(evidence.actor_outcomes) is not tuple or len(evidence.actor_outcomes) != 2
          or any(type(item) is not ActorOutcome for item in evidence.actor_outcomes)):
        failures.append("exactly two actor outcome records are required")
    elif any(type(item.role) is not str for item in evidence.actor_outcomes):
        failures.append("actor outcome roles must be text")
    else:
        by_role = {item.role: item for item in evidence.actor_outcomes}
        if len(by_role) != 2 or set(by_role) != {"ACTOR_A", "ACTOR_B"}:
            failures.append("actor outcome roles must be ACTOR_A and ACTOR_B exactly once")
        elif _valid_actor_spids(evidence.actor_spids):
            expected_spids = dict(evidence.actor_spids)
            for role, outcome in by_role.items():
                if type(outcome.spid) is not int or outcome.spid != expected_spids[role]:
                    failures.append("actor outcome SPIDs differ from supplied actor bindings")
                if outcome.outcome != "SUCCESS" or outcome.error_number is not None:
                    failures.append("both serial insert actors must succeed without an error")

    initial = _valid_key_tuple(evidence.expected_initial_keys, "expected initial keys", missing, failures)
    final = _valid_key_tuple(evidence.observed_final_keys, "observed final keys", missing, failures)
    expected_insertions = _valid_actor_insertions(
        evidence.expected_insertions, "expected actor insertions", missing, failures)
    observed_insertions = _valid_actor_insertions(
        evidence.observed_insertions, "observed actor insertions", missing, failures)
    if (expected_insertions is not None and observed_insertions is not None
            and expected_insertions != observed_insertions):
        failures.append("observed actor insertions differ from the expected actor/key bindings")
    if initial is not None and expected_insertions is not None:
        if any(key in initial for key in expected_insertions.values()):
            failures.append("inserted keys overlap the expected initial state")

    if initial is not None and final is not None and expected_insertions is not None:
        expected_final = set(initial) | set(expected_insertions.values())
        if set(final) != expected_final or len(final) != len(expected_final):
            failures.append("observed final keys do not equal the complete expected post-insert state")

    count = evidence.matching_deadlock_event_count
    if count is None:
        missing.append("matching deadlock event count")
    elif type(count) is not int or count < 0:
        failures.append("matching deadlock event count is invalid")
    elif count != 0:
        failures.append("serial control arm must contain no matching deadlock event")

    if failures:
        return GraphResult(Verdict.FAIL, tuple(failures))
    if missing:
        return GraphResult(Verdict.NOT_PROVEN, tuple(missing))
    return GraphResult(Verdict.PASS, ())


def _valid_actor_insertions(value: object, label: str, missing: list[str],
                            failures: list[str]) -> dict[str, int] | None:
    if value is None:
        missing.append(label)
        return None
    if (type(value) is not tuple or len(value) != 2
            or any(type(item) is not tuple or len(item) != 2 for item in value)):
        failures.append(f"{label} must contain exactly two actor/key pairs")
        return None
    roles = [item[0] for item in value]
    keys = [item[1] for item in value]
    if (any(type(role) is not str for role in roles)
            or set(roles) != {"ACTOR_A", "ACTOR_B"}
            or len(set(roles)) != 2):
        failures.append(f"{label} must bind ACTOR_A and ACTOR_B exactly once")
        return None
    if any(type(key) is not int for key in keys) or len(set(keys)) != 2:
        failures.append(f"{label} must bind two distinct integer keys")
        return None
    return dict(value)


def _valid_key_tuple(value: object, label: str, missing: list[str],
                     failures: list[str]) -> tuple[int, ...] | None:
    if value is None:
        missing.append(label)
        return None
    if type(value) is not tuple or any(type(key) is not int for key in value):
        failures.append(f"{label} must be a tuple of integers")
        return None
    if len(set(value)) != len(value):
        failures.append(f"{label} must not contain duplicates")
        return None
    return value


def evaluate_range_graph(graph_xml: str | bytes | None,
                         identity: GraphIdentity | None) -> GraphResult:
    """Require one mutual two-actor wait cycle on the supplied same KEY."""
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
        failures.append("range variant requires exactly two deadlock processes")
    process_by_id: dict[str, int] = {}
    expected_spids = {value for _, value in identity.actor_spids}
    for process in processes:
        process_id = _nonempty_attr(process, "id", "process", failures)
        current_db = _unsigned_attr(process, "currentdb", "process", failures)
        spid = _unsigned_attr(process, "spid", "process", failures)
        if process_id is not None:
            if process_id in process_by_id:
                failures.append("process IDs must be unique")
            if spid is not None:
                process_by_id[process_id] = spid
        if current_db is not None and current_db != identity.database_id:
            failures.append("process currentdb differs from the supplied owned database")
        if spid is not None and spid not in expected_spids:
            failures.append("deadlock process SPID is outside the two supplied actors")
    if len(processes) == 2 and set(process_by_id.values()) != expected_spids:
        failures.append("deadlock processes do not bind exactly to ACTOR_A and ACTOR_B SPIDs")

    victims = victim_list.findall("victimProcess")
    victim_id = (_nonempty_attr(victims[0], "id", "victimProcess", failures)
                 if len(victims) == 1 else None)
    if len(victims) != 1:
        failures.append("range variant requires exactly one deadlock victim")
    if victim_id is not None and victim_id not in process_by_id:
        failures.append("victim process is not present in the deadlock process list")

    matches = [node for node in resource_list.findall("keylock")
               if node.get("objectname") == identity.object_name
               and node.get("indexname") == identity.index_name
               and node.get("dbid") == str(identity.database_id)
               and node.get("hobtid") == identity.hobt_id]
    if len(matches) != 1:
        failures.append("graph must contain exactly one KEY for the supplied database, object, index, and HoBT")
    elif len(process_by_id) == 2:
        resource = matches[0]
        owners = resource.findall("owner-list/owner")
        waiters = resource.findall("waiter-list/waiter")
        if len(owners) != 2 or len(waiters) != 2:
            failures.append("the same KEY must contain exactly two owners and two waiters")
        owner_ids = [node.get("id") for node in owners]
        waiter_ids = [node.get("id") for node in waiters]
        if set(owner_ids) != set(process_by_id) or len(set(owner_ids)) != 2:
            failures.append("both actors must hold a lock on the same KEY")
        if set(waiter_ids) != set(process_by_id) or len(set(waiter_ids)) != 2:
            failures.append("both actors must wait on the same KEY")
        for owner in owners:
            if owner.get("id") not in process_by_id or not (owner.get("mode") or "").strip():
                failures.append("each KEY owner must identify an actor and its observed lock mode")
        for waiter in waiters:
            if (waiter.get("id") not in process_by_id
                    or not (waiter.get("mode") or "").strip()
                    or waiter.get("requestType") != "wait"):
                failures.append("each range KEY waiter must identify an actor, observed mode, and requestType=wait")
        if (len(owners) == 2 and len(waiters) == 2
                and set(node.get("id") for node in owners) == set(process_by_id)
                and set(node.get("id") for node in waiters) == set(process_by_id)):
            owner_modes = {node.get("id"): node.get("mode") for node in owners}
            waiter_modes = {node.get("id"): node.get("mode") for node in waiters}
            modes = (*owner_modes.values(), *waiter_modes.values())
            if any(mode not in _COMPATIBLE for mode in modes):
                failures.append("graph contains a lock mode outside the documented compatibility profile")
            else:
                # Each actor must request a mode incompatible with a mode held
                # by the other actor; arbitrary nonempty labels cannot imply a cycle.
                for actor_id, other_id in ((actor_id, other_id)
                                           for actor_id in process_by_id
                                           for other_id in process_by_id
                                           if actor_id != other_id):
                    if waiter_modes[actor_id] in _COMPATIBLE[owner_modes[other_id]]:
                        failures.append("observed lock modes do not prove reciprocal blocking")
    if failures:
        return GraphResult(Verdict.FAIL, tuple(failures))
    return GraphResult(Verdict.PASS, (), process_by_id[victim_id])


def evaluate_range_capture(evidence: RangeCaptureEvidence | None) -> GraphResult:
    """Check graph capture plus victim rollback, survivor insert, and exact final keys."""
    if evidence is None:
        return GraphResult(Verdict.NOT_PROVEN, ("range deadlock capture evidence is missing",))
    if type(evidence) is not RangeCaptureEvidence:
        return GraphResult(Verdict.FAIL, ("range deadlock capture must use the exact contract record",))
    graph = _evaluate_capture(evidence.capture, evaluate_range_graph, "range")
    if graph.verdict is not Verdict.PASS:
        return graph

    missing: list[str] = []
    failures: list[str] = []
    initial = _valid_key_tuple(evidence.expected_initial_keys, "expected initial keys", missing, failures)
    final = _valid_key_tuple(evidence.observed_final_keys, "observed final keys", missing, failures)
    insertions = _valid_actor_insertions(
        evidence.expected_insertions, "expected actor insertions", missing, failures)
    if initial is not None and insertions is not None:
        if any(key in initial for key in insertions.values()):
            failures.append("inserted keys overlap the expected initial state")

    capture = evidence.capture
    if (evidence.insert_outcomes is None):
        missing.append("deadlock-arm actor insert outcomes")
        actual: dict[str, RangeInsertOutcome] | None = None
    elif (type(evidence.insert_outcomes) is not tuple or len(evidence.insert_outcomes) != 2
          or any(type(item) is not RangeInsertOutcome for item in evidence.insert_outcomes)):
        failures.append("exactly two deadlock-arm actor insert outcomes are required")
        actual = None
    else:
        roles = [item.role for item in evidence.insert_outcomes]
        if (any(type(role) is not str for role in roles)
                or set(roles) != {"ACTOR_A", "ACTOR_B"} or len(set(roles)) != 2):
            failures.append("insert outcomes must bind ACTOR_A and ACTOR_B exactly once")
            actual = None
        else:
            actual = {item.role: item for item in evidence.insert_outcomes}

    if actual is not None and insertions is not None and type(capture) is CaptureEvidence:
        expected_spids = dict(capture.actor_spids or ())
        role_by_spid = {spid: role for role, spid in expected_spids.items()}
        victim_role = role_by_spid.get(graph.victim_spid)
        if victim_role not in {"ACTOR_A", "ACTOR_B"}:
            failures.append("graph victim does not bind to a supplied actor role")
        else:
            survivor_role = "ACTOR_B" if victim_role == "ACTOR_A" else "ACTOR_A"
            victim = actual[victim_role]
            survivor = actual[survivor_role]
            for role, outcome in actual.items():
                if (type(outcome.spid) is not int or outcome.spid != expected_spids.get(role)
                        or type(outcome.key) is not int or outcome.key != insertions[role]):
                    failures.append("insert outcome differs from its expected actor/SPID/key binding")
            if victim.outcome != "ROLLED_BACK" or victim.error_number != 1205:
                failures.append("deadlock victim insert must roll back with error 1205")
            if survivor.outcome != "INSERTED" or survivor.error_number is not None:
                failures.append("deadlock survivor insert must be confirmed without an error")
            if initial is not None and final is not None:
                expected_final = set(initial) | {insertions[survivor_role]}
                if set(final) != expected_final or len(final) != len(expected_final):
                    failures.append("deadlock-arm final keys must contain only the initial rows and survivor insert")

    if failures:
        return GraphResult(Verdict.FAIL, tuple(failures), graph.victim_spid)
    if missing:
        return GraphResult(Verdict.NOT_PROVEN, tuple(missing), graph.victim_spid)
    return GraphResult(Verdict.PASS, (), graph.victim_spid)
