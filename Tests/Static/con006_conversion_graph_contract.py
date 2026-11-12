"""Offline contract checker for one supplied CON-006 conversion deadlock graph.

It validates graph shape and caller-supplied identity bindings only. It does
not acquire, authenticate, time, or attest to SQL Server evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
import re
import xml.etree.ElementTree as ET


MAX_GRAPH_BYTES = 128 * 1024
_UNSIGNED = re.compile(r"[1-9][0-9]*\Z")
# SQL capture timestamps use RFC-3339 offsets/fractions but not leap seconds.
# Fractions remain unbounded except for a small whole-input length guard.
_RFC3339 = re.compile(
    r"([0-9]{4}-[0-9]{2}-[0-9]{2})[Tt]"
    r"([0-9]{2}):([0-9]{2}):([0-9]{2})"
    r"(?:\.([0-9]+))?([Zz]|[+-][0-9]{2}:[0-9]{2})\Z"
)


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
    victim_spid: int | None = None


@dataclass(frozen=True)
class ActorOutcome:
    role: str
    spid: int
    outcome: str
    error_number: int | None


@dataclass(frozen=True)
class CaptureEvidence:
    """Caller-supplied correlation envelope; fields are not authenticated here."""

    expected_run_token: str | None
    observed_run_token: str | None
    event_name: str | None
    source_session: str | None
    database_id: int | None
    actor_spids: tuple[tuple[str, int], ...] | None
    event_timestamp_utc: str | None
    run_started_utc: str | None
    run_finished_utc: str | None
    matching_event_count: int | None
    actor_outcomes: tuple[ActorOutcome, ...] | None
    graph_identity: GraphIdentity | None
    graph_xml: str | bytes | None


def _valid_actor_spids(actor_spids: object) -> bool:
    if type(actor_spids) is not tuple or len(actor_spids) != 2:
        return False
    if any(type(pair) is not tuple or len(pair) != 2 for pair in actor_spids):
        return False
    roles = [pair[0] for pair in actor_spids]
    if any(type(role) is not str for role in roles) or set(roles) != {"ACTOR_A", "ACTOR_B"}:
        return False
    spids = [pair[1] for pair in actor_spids]
    if (any(type(spid) is not int or spid <= 0 for spid in spids)
            or spids[0] == spids[1]):
        return False
    return True


def _valid_identity(identity: object) -> bool:
    if type(identity) is not GraphIdentity:
        return False
    if type(identity.database_id) is not int or identity.database_id <= 0:
        return False
    if not _valid_actor_spids(identity.actor_spids):
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


def _timestamp(
    value: str | None,
    label: str,
    *,
    missing: list[str],
    failures: list[str],
) -> tuple[int, Decimal] | None:
    if value is None:
        missing.append(label)
        return None
    if type(value) is not str or len(value) > 128:
        failures.append(f"{label} must match the bounded SQL capture timestamp profile")
        return None
    match = _RFC3339.fullmatch(value)
    if match is None:
        failures.append(f"{label} must match the bounded SQL capture timestamp profile")
        return None
    date_text, hour_text, minute_text, second_text, fraction_text, offset_text = match.groups()
    try:
        parsed_date = datetime.fromisoformat(date_text)
        fraction = Decimal("0." + fraction_text) if fraction_text is not None else Decimal(0)
    except (ValueError, InvalidOperation):
        failures.append(f"{label} is not a valid timestamp")
        return None

    hour, minute, second = int(hour_text), int(minute_text), int(second_text)
    if hour > 23 or minute > 59 or second > 59:
        failures.append(f"{label} is outside the supported SQL capture timestamp profile")
        return None

    offset_seconds = 0
    if offset_text not in {"Z", "z"}:
        sign = 1 if offset_text[0] == "+" else -1
        offset_hour, offset_minute = int(offset_text[1:3]), int(offset_text[4:6])
        if offset_hour > 23 or offset_minute > 59:
            failures.append(f"{label} has an invalid UTC offset")
            return None
        offset_seconds = sign * (offset_hour * 3600 + offset_minute * 60)

    local_seconds = (
        parsed_date.date().toordinal() * 86400
        + hour * 3600
        + minute * 60
        + second
    )
    # Integer arithmetic avoids datetime.astimezone overflow at year 1/9999
    # boundaries and Decimal preserves arbitrary RFC-3339 fractional precision.
    return local_seconds - offset_seconds, fraction


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
    victim_spid = int(process_by_id[victim_id].get("spid", "0")) if victim_id is not None else None
    return GraphResult(Verdict.PASS, (), victim_spid)


def evaluate_conversion_capture(evidence: CaptureEvidence | None) -> GraphResult:
    """Check graph plus caller-supplied event, run-window, and actor outcome bindings."""
    if evidence is None:
        return GraphResult(Verdict.NOT_PROVEN, ("conversion capture evidence is missing",))
    if type(evidence) is not CaptureEvidence:
        return GraphResult(Verdict.FAIL, ("capture evidence must use the exact contract record",))

    missing: list[str] = []
    failures: list[str] = []

    def require_text(value: str | None, label: str, expected: str | None = None) -> None:
        if value is None:
            missing.append(label)
        elif type(value) is not str or not value.strip():
            failures.append(f"{label} is invalid")
        elif expected is not None and value != expected:
            failures.append(f"{label} differs from the required value")

    require_text(evidence.expected_run_token, "expected run token")
    require_text(evidence.observed_run_token, "observed run token", evidence.expected_run_token)
    require_text(evidence.event_name, "event name", "xml_deadlock_report")
    require_text(evidence.source_session, "source session", "system_health")

    if evidence.graph_identity is not None and type(evidence.graph_identity) is not GraphIdentity:
        failures.append("graph identity record is invalid")
    if evidence.database_id is None:
        missing.append("event database identity")
    elif type(evidence.database_id) is not int or evidence.database_id <= 0:
        failures.append("event database identity is invalid")
    elif (type(evidence.graph_identity) is GraphIdentity
          and evidence.database_id != evidence.graph_identity.database_id):
        failures.append("event database identity differs from the graph identity")

    if evidence.actor_spids is None:
        missing.append("event actor-to-SPID bindings")
    elif not _valid_actor_spids(evidence.actor_spids):
        failures.append("event actor-to-SPID bindings are invalid")
    elif (type(evidence.graph_identity) is GraphIdentity
          and evidence.actor_spids != evidence.graph_identity.actor_spids):
        failures.append("event actor-to-SPID bindings differ from the graph identity")

    event_time = _timestamp(evidence.event_timestamp_utc, "event timestamp", missing=missing, failures=failures)
    started = _timestamp(evidence.run_started_utc, "run start", missing=missing, failures=failures)
    finished = _timestamp(evidence.run_finished_utc, "run finish", missing=missing, failures=failures)
    if started is not None and finished is not None and started > finished:
        failures.append("run window ends before it starts")
    if event_time is not None and started is not None and finished is not None:
        if not started <= event_time <= finished:
            failures.append("deadlock event timestamp falls outside the supplied run window")

    if evidence.matching_event_count is None:
        missing.append("matching event count")
    elif type(evidence.matching_event_count) is not int or evidence.matching_event_count < 0:
        failures.append("matching event count is invalid")
    elif evidence.matching_event_count == 0:
        missing.append("matching deadlock event")
    elif evidence.matching_event_count != 1:
        failures.append("exactly one matching deadlock event is required")

    graph_result = evaluate_conversion_graph(evidence.graph_xml, evidence.graph_identity)
    if graph_result.verdict is Verdict.NOT_PROVEN:
        missing.extend(graph_result.reasons)
    elif graph_result.verdict is Verdict.FAIL:
        failures.extend(graph_result.reasons)

    if evidence.actor_outcomes is None:
        missing.append("actor outcome evidence")
    elif (type(evidence.actor_outcomes) is not tuple or len(evidence.actor_outcomes) != 2
          or any(type(item) is not ActorOutcome for item in evidence.actor_outcomes)):
        failures.append("exactly two actor outcome records are required")
    elif any(type(item.role) is not str or item.role not in {"ACTOR_A", "ACTOR_B"}
             for item in evidence.actor_outcomes):
        failures.append("actor outcome roles must be ACTOR_A and ACTOR_B")
    else:
        by_role = {item.role: item for item in evidence.actor_outcomes}
        expected_spids = dict(evidence.actor_spids) if _valid_actor_spids(evidence.actor_spids) else {}
        if set(by_role) != {"ACTOR_A", "ACTOR_B"} or len(by_role) != 2:
            failures.append("actor outcome roles must be ACTOR_A and ACTOR_B exactly once")
        elif not expected_spids:
            pass  # the missing or invalid actor binding already determines the result
        elif any(
            type(item.spid) is not int or item.spid != expected_spids.get(role)
            for role, item in by_role.items()
        ):
            failures.append("actor outcome SPIDs differ from the supplied actor bindings")
        else:
            victims = [
                item for item in evidence.actor_outcomes
                if item.spid == graph_result.victim_spid
                and item.outcome == "VICTIM"
                and type(item.error_number) is int
                and item.error_number == 1205
            ]
            survivors = [
                item for item in evidence.actor_outcomes
                if item.spid != graph_result.victim_spid
                and item.outcome == "SURVIVOR"
                and item.error_number is None
            ]
            if graph_result.verdict is Verdict.PASS and (len(victims) != 1 or len(survivors) != 1):
                failures.append("graph victim must match one error 1205 outcome and the other actor must be the survivor")
            elif graph_result.verdict is not Verdict.PASS:
                observed_victims = [item for item in evidence.actor_outcomes if item.outcome == "VICTIM"]
                observed_survivors = [item for item in evidence.actor_outcomes if item.outcome == "SURVIVOR"]
                if len(observed_victims) != 1 or len(observed_survivors) != 1:
                    failures.append("actor outcomes must contain one victim and one survivor")
                elif observed_victims[0].error_number not in (None, 1205):
                    failures.append("victim outcome error number must be 1205")
                elif observed_victims[0].error_number is None:
                    missing.append("victim error number 1205")
                elif observed_survivors[0].error_number is not None:
                    failures.append("survivor outcome must not report an error")

    if failures:
        return GraphResult(Verdict.FAIL, tuple(failures + missing))
    if missing:
        return GraphResult(Verdict.NOT_PROVEN, tuple(missing))
    return GraphResult(Verdict.PASS, (), graph_result.victim_spid)
