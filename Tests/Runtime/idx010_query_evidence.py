"""Offline acceptance checks for the IDX-010 ordered NCCI pilot candidate."""
from __future__ import annotations

from dataclasses import dataclass
import re
from xml.etree import ElementTree as ET


QUERY = (
    "SELECT COUNT_BIG(*) AS RowCount, SUM(EventDayKey) AS DaySum "
    "FROM dbo.Events WHERE EventDayKey >= 1048576 AND EventDayKey < 1052672 "
    "OPTION (MAXDOP 1)"
)
EXPECTED_RESULT = (4096, 4303353856)
SEGMENT_COUNT = 4
SHOWPLAN_NS = {"sp": "http://schemas.microsoft.com/sqlserver/2004/07/showplan"}
MAX_PLAN_CHARS = 1024 * 1024
SEGMENT_MESSAGE = re.compile(
    r"Table 'Events'\. (?:Scan count [0-9]{1,10}, [^\r\n]*? )?"
    r"Segment reads ([0-4]), segment skipped ([0-4])\.",
    re.ASCII,
)
SEGMENT_COUNTER = re.compile(r"\bsegment (?:reads|skipped)\b", re.IGNORECASE | re.ASCII)
OWNED_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,127}", re.ASCII)


class QueryEvidenceMissing(ValueError):
    """The captured inputs cannot prove a query-level segment observation."""


@dataclass(frozen=True)
class SegmentCounts:
    reads: int
    skipped: int


def verify_query_evidence(
    *,
    plan_xml: str,
    info_messages: tuple[str, ...],
    result_rows: tuple[tuple[int, int], ...],
    database_name: str,
    index_name: str,
) -> SegmentCounts:
    """Check one isolated query response against the fixed pilot profile.

    The caller must bind all three inputs to the same single SQL request and
    supply database/index names from the owned setup inventory. This function
    does not establish capture provenance, order quality, or overall pilot PASS.
    """
    if not all(OWNED_IDENTIFIER.fullmatch(name) for name in (database_name, index_name)):
        raise QueryEvidenceMissing("invalid identifier in the setup inventory")
    if result_rows != (EXPECTED_RESULT,) or any(type(value) is not int for value in result_rows[0]):
        raise QueryEvidenceMissing("result must be the single expected integer aggregate row")
    _verify_actual_scan(plan_xml, database_name, index_name)
    return _read_segment_counts(info_messages)


def _verify_actual_scan(plan_xml: str, database_name: str, index_name: str) -> None:
    if len(plan_xml) > MAX_PLAN_CHARS or "<!" in plan_xml:
        raise QueryEvidenceMissing("Showplan payload exceeds the accepted XML profile")
    try:
        plan = ET.fromstring(plan_xml)
    except ET.ParseError as exc:
        raise QueryEvidenceMissing("invalid Showplan XML") from exc
    if plan.tag != f"{{{SHOWPLAN_NS['sp']}}}ShowPlanXML":
        raise QueryEvidenceMissing("response is not a SQL Server Showplan")
    containers = plan.findall(".//sp:Statements", SHOWPLAN_NS)
    if len(containers) != 1 or len(containers[0]) != 1:
        raise QueryEvidenceMissing("expected exactly one statement in the Showplan")
    statement = containers[0][0]
    text = " ".join(statement.get("StatementText", "").split()).removesuffix(";")
    if text != QUERY:
        raise QueryEvidenceMissing("Showplan does not describe the fixed pilot query")

    accesses = [
        (operator, obj)
        for operator in statement.findall(".//sp:RelOp", SHOWPLAN_NS)
        for obj in operator.findall("*/sp:Object", SHOWPLAN_NS)
    ]
    if len(accesses) != 1:
        raise QueryEvidenceMissing("expected exactly one indexed data access")
    operator, obj = accesses[0]
    expected = {
        "Database": f"[{database_name}]",
        "Schema": "[dbo]",
        "Table": "[Events]",
        "Index": f"[{index_name}]",
        "IndexKind": "NonClustered",
    }
    scan = operator.find("sp:IndexScan", SHOWPLAN_NS)
    if scan is None:
        raise QueryEvidenceMissing("data access has no IndexScan evidence")
    storage = {element.get("Storage") for element in (scan, obj)} - {None}
    if (
        storage != {"ColumnStore"}
        or any(scan.get(flag) not in (None, "false", "0") for flag in ("ForcedIndex", "ForceScan", "ForceSeek", "Lookup"))
        or operator.get("PhysicalOp") != "Index Scan"
        or scan.find("sp:Object", SHOWPLAN_NS) is not obj
        or any(obj.get(key) != value for key, value in expected.items())
    ):
        raise QueryEvidenceMissing("data access is not the expected nonclustered columnstore scan")
    threads = operator.findall("sp:RunTimeInformation/sp:RunTimeCountersPerThread", SHOWPLAN_NS)
    if len(threads) != 1 or threads[0].get("ActualExecutions") != "1":
        raise QueryEvidenceMissing("the scan was not observed running once in the serial plan")


def _read_segment_counts(info_messages: tuple[str, ...]) -> SegmentCounts:
    if len(info_messages) > 32 or any(len(message) > 4096 for message in info_messages):
        raise QueryEvidenceMissing("STATISTICS IO capture exceeds the message limits")
    candidates = [
        message for message in info_messages
        if message.lstrip().startswith("Table 'Events'.") or SEGMENT_COUNTER.search(message)
    ]
    if len(candidates) != 1:
        raise QueryEvidenceMissing("expected one bounded STATISTICS IO segment message")
    message = candidates[0].strip()
    if len(SEGMENT_COUNTER.findall(message)) != 2:
        raise QueryEvidenceMissing("ambiguous segment counters")
    match = SEGMENT_MESSAGE.fullmatch(message)
    if not match:
        raise QueryEvidenceMissing("segment message does not match the Events scan")
    counts = SegmentCounts(*(int(value) for value in match.groups()))
    if counts.reads == 0 or counts.reads + counts.skipped != SEGMENT_COUNT:
        raise QueryEvidenceMissing("segment counters disagree with the four-rowgroup profile")
    return counts
