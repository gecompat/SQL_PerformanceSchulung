"""Decode a bounded XE ring buffer snapshot before OPTSP event correlation."""

from dataclasses import dataclass, field
from datetime import date
import re
from xml.etree import ElementTree

_MAX_XML_BYTES = 4 * 1024 * 1024
_UTC_TIMESTAMP = re.compile(
    r"([0-9]{4}-[0-9]{2}-[0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]{1,7}))?Z"
)


@dataclass(frozen=True)
class SessionCounters:
    """Drop and pending-buffer counters sampled at the collection boundary."""

    dropped_event_count: int
    dropped_buffer_count: int
    pending_buffers: int
    largest_event_dropped_size: int


@dataclass(frozen=True)
class EventEnvelope:
    package: str
    name: str
    sequence: int
    timestamp_ticks: int
    payload: ElementTree.Element = field(repr=False, compare=False)


def _unsigned(value: str | None) -> int:
    if value is None or re.fullmatch(r"[0-9]{1,20}", value) is None:
        raise ValueError("invalid XE counter")
    return int(value)


def _timestamp_ticks(value: str) -> int:
    """Decode a UTC label as 100 ns ticks since 0001-01-01; this is not clock calibration."""
    match = _UTC_TIMESTAMP.fullmatch(value)
    if match is None:
        raise ValueError("invalid XE UTC timestamp")
    day, hour_text, minute_text, second_text, fraction = match.groups()
    hour, minute, second = int(hour_text), int(minute_text), int(second_text)
    if hour >= 24 or minute >= 60 or second >= 60:
        raise ValueError("invalid XE UTC timestamp")
    try:
        days = date.fromisoformat(day).toordinal() - 1
    except ValueError:
        raise ValueError("invalid XE UTC timestamp") from None
    seconds = ((days * 24 + hour) * 60 + minute) * 60 + second
    return seconds * 10_000_000 + int((fraction or "").ljust(7, "0"))


def read_ring_buffer(xml: bytes, counters: SessionCounters) -> tuple[EventEnvelope, ...]:
    """Reject incomplete snapshots. The caller must quiesce and bind the session first."""
    for count in (
        counters.dropped_event_count,
        counters.dropped_buffer_count,
        counters.pending_buffers,
        counters.largest_event_dropped_size,
    ):
        if type(count) is not int or count != 0:
            raise ValueError("XE session is lossy or has pending buffers")
    if not 0 < len(xml) <= _MAX_XML_BYTES:
        raise ValueError("XE snapshot size out of bounds")
    try:
        decoded = xml.decode("utf-8")
        if "<!" in decoded:
            raise ValueError("unexpected markup in XE snapshot")
        target = ElementTree.fromstring(decoded)
    except (UnicodeDecodeError, ElementTree.ParseError):
        raise ValueError("malformed XE snapshot") from None

    if target.tag != "RingBufferTarget" or target.get("truncated") != "0":
        raise ValueError("XE snapshot is missing or truncated")
    retained = _unsigned(target.get("eventCount"))
    processed = _unsigned(target.get("totalEventsProcessed"))
    if not retained or retained != len(target) or processed != retained or _unsigned(target.get("droppedCount")):
        raise ValueError("XE snapshot is empty or did not retain every event")

    events: dict[int, EventEnvelope] = {}
    for node in target:
        package, name = node.get("package"), node.get("name")
        if node.tag != "event" or not package or not name:
            raise ValueError("invalid XE event identity")
        sequences = node.findall("./action[@name='event_sequence']")
        if len(sequences) != 1 or sequences[0].get("package") != "package0":
            raise ValueError("missing or ambiguous XE event sequence")
        values = sequences[0].findall("value")
        if len(values) != 1 or len(values[0]):
            raise ValueError("invalid XE event sequence")
        sequence = _unsigned(values[0].text)
        if sequence in events:
            raise ValueError("duplicate XE event sequence")
        timestamp = _timestamp_ticks(node.get("timestamp", ""))
        events[sequence] = EventEnvelope(package, name, sequence, timestamp, node)

    return tuple(events[key] for key in sorted(events))
