"""Offline contract for caller-supplied RES-003 memory signal snapshots.

This checks a declared baseline/pressure/recovery sequence only. Timestamp
ordering preserves datetime2(7)'s seventh fractional digit. It does not collect
or authenticate DMV data, establish causality, or qualify a pressure run.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
import re


_RFC3339 = re.compile(
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"
    r"(?:\.(\d{1,7}))?(Z|[+-]\d{2}:\d{2})\Z"
)


class Phase(str, Enum):
    BASELINE = "baseline"
    PRESSURE = "pressure"
    RECOVERY = "recovery"


class Verdict(str, Enum):
    PASS = "PASS"
    NOT_PROVEN = "NOT_PROVEN"
    FAIL = "FAIL"


@dataclass(frozen=True)
class MemorySignalSample:
    run_token: str
    phase: Phase
    captured_at: str
    process_physical_memory_low: bool
    system_low_memory_signal_state: bool


@dataclass(frozen=True)
class Result:
    verdict: Verdict
    reasons: tuple[str, ...]
    process_low_observed: bool
    system_low_observed: bool
    recovery_signals_clear: bool


def _timestamp(value: object) -> tuple[datetime, Decimal] | None:
    if type(value) is not str:
        return None
    match = _RFC3339.fullmatch(value)
    if match is None:
        return None
    base, fraction, offset = match.groups()
    try:
        parsed = datetime.fromisoformat(base + ("+00:00" if offset == "Z" else offset))
        fractional_second = Decimal("0." + fraction) if fraction is not None else Decimal(0)
        if parsed.utcoffset() is None:
            return None
        instant = parsed.astimezone(timezone.utc)
    except (ValueError, InvalidOperation, OverflowError):
        return None
    return instant, fractional_second


def evaluate_memory_signals(
    expected_run_token: str,
    samples: tuple[MemorySignalSample, ...] | None,
    run_started_at: str,
    run_finished_at: str,
) -> Result:
    """Check signal transitions without inventing thresholds or source trust."""
    empty = Result(Verdict.NOT_PROVEN, ("required samples or run window are missing",), False, False, False)
    if samples is None:
        return empty
    if type(samples) is not tuple or any(type(sample) is not MemorySignalSample for sample in samples):
        return Result(Verdict.FAIL, ("samples must be a tuple of exact MemorySignalSample records",), False, False, False)
    if type(expected_run_token) is not str or not expected_run_token.strip():
        return Result(Verdict.FAIL, ("expected run token is invalid",), False, False, False)
    if any(type(sample.phase) is not Phase for sample in samples):
        return Result(Verdict.FAIL, ("sample phase must be an exact Phase value",), False, False, False)
    started, finished = _timestamp(run_started_at), _timestamp(run_finished_at)
    if started is None or finished is None or started >= finished:
        return Result(Verdict.FAIL, ("run window is invalid or unordered",), False, False, False)
    if len(samples) != 3 or {sample.phase for sample in samples} != set(Phase):
        return Result(Verdict.NOT_PROVEN, ("exactly one baseline, pressure, and recovery sample is required",), False, False, False)

    by_phase: dict[Phase, MemorySignalSample] = {}
    for sample in samples:
        if (
            sample.phase in by_phase
            or type(sample.run_token) is not str
            or sample.run_token != expected_run_token
            or type(sample.process_physical_memory_low) is not bool
            or type(sample.system_low_memory_signal_state) is not bool
        ):
            return Result(Verdict.FAIL, ("sample identity, phase, or low-memory flags are invalid",), False, False, False)
        captured = _timestamp(sample.captured_at)
        if captured is None or not started <= captured <= finished:
            return Result(Verdict.FAIL, ("sample timestamp is invalid or outside the run window",), False, False, False)
        by_phase[sample.phase] = sample

    baseline, pressure, recovery = (by_phase[p] for p in (Phase.BASELINE, Phase.PRESSURE, Phase.RECOVERY))
    times = tuple(_timestamp(by_phase[p].captured_at) for p in (Phase.BASELINE, Phase.PRESSURE, Phase.RECOVERY))
    if not times[0] < times[1] < times[2]:
        return Result(Verdict.FAIL, ("baseline, pressure, and recovery captures must be strictly ordered",), False, False, False)

    process_observed = pressure.process_physical_memory_low
    system_observed = pressure.system_low_memory_signal_state
    baseline_clear = not baseline.process_physical_memory_low and not baseline.system_low_memory_signal_state
    recovery_clear = not recovery.process_physical_memory_low and not recovery.system_low_memory_signal_state
    if not baseline_clear:
        return Result(Verdict.NOT_PROVEN, ("low-memory signals were already present at baseline",), process_observed, system_observed, recovery_clear)
    if not (process_observed or system_observed):
        return Result(Verdict.NOT_PROVEN, ("neither documented low-memory signal was present in the pressure sample",), False, False, recovery_clear)
    if not recovery_clear:
        return Result(Verdict.NOT_PROVEN, ("one or more low-memory signals remain set in recovery",), process_observed, system_observed, False)
    return Result(Verdict.PASS, (), process_observed, system_observed, True)
