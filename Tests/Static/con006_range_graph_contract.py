"""Offline checker for a supplied CON-006 range deadlock graph.

This checks only caller-supplied XML and identity values. Lock modes are
reported by the engine graph and are required to be present, but this
prospective contract does not assume a particular RangeS/RangeI mode pair or
authenticate the source, run, actor outcomes, or SQL Server execution.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from Tests.Static.con006_conversion_graph_contract import (
    MAX_GRAPH_BYTES, CaptureEvidence, GraphIdentity, GraphResult, Verdict,
    _evaluate_capture,
    _nonempty_attr, _single, _unsigned_attr, _valid_identity,
)


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
                    or not (waiter.get("requestType") or "").strip()):
                failures.append("each KEY waiter must identify an actor, observed mode, and request type")
    if failures:
        return GraphResult(Verdict.FAIL, tuple(failures))
    return GraphResult(Verdict.PASS, (), process_by_id[victim_id])


def evaluate_range_capture(evidence: CaptureEvidence | None) -> GraphResult:
    """Check the range graph and supplied event/window/outcome bindings."""
    return _evaluate_capture(evidence, evaluate_range_graph, "range")
