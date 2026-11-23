"""Evaluate normalized evidence for the isolated OPTIMIZED_SP_EXECUTESQL pilot.

The producer must qualify the shared time basis, compile boundaries,
canonical resource keys and their compile classification. This module
joins independent waits and ownership intervals without interpreting raw
XE fields or RPC duration.
"""

from dataclasses import dataclass, field
from itertools import combinations
import re
from typing import Literal


@dataclass(frozen=True)
class ActorRequest:
    database_id: int
    session_id: int
    request_id: int


@dataclass(frozen=True)
class TimeBounds:
    """Inclusive earliest and latest ticks on the producer's qualified clock."""

    earliest: int
    latest: int

    def __post_init__(self) -> None:
        if type(self.earliest) is not int or type(self.latest) is not int or self.earliest > self.latest:
            raise ValueError("invalid time bounds")


@dataclass(frozen=True)
class EventTime:
    """One event from a producer-qualified, loss-free XE recording.

    The sequence orders events within that recording. It cannot add duration
    to a pair of equal timestamp labels.
    """

    ticks: int
    sequence: int
    recording: str

    def __post_init__(self) -> None:
        if type(self.ticks) is not int or type(self.sequence) is not int or self.sequence <= 0:
            raise ValueError("invalid recorded event time")
        if type(self.recording) is not str or not self.recording:
            raise ValueError("missing event recording identity")


Time = int | TimeBounds | EventTime


def _earliest(value: Time) -> int:
    if isinstance(value, EventTime):
        return value.ticks
    return value.earliest if isinstance(value, TimeBounds) else value


def _latest(value: Time) -> int:
    return value.latest if isinstance(value, TimeBounds) else _earliest(value)


def _strictly_before(left: Time, right: Time) -> bool:
    if isinstance(left, EventTime) and isinstance(right, EventTime):
        return (
            left.recording == right.recording
            and left.ticks <= right.ticks
            and left.sequence < right.sequence
        )
    return _latest(left) < _earliest(right)


def _at_or_before(left: Time, right: Time) -> bool:
    if isinstance(left, EventTime) or isinstance(right, EventTime):
        return left == right or _strictly_before(left, right)
    return _latest(left) <= _earliest(right)


@dataclass(frozen=True)
class Interval:
    start: Time
    end: Time

    @classmethod
    def from_end_and_duration(cls, end: TimeBounds, duration: TimeBounds) -> "Interval":
        """Use only when the producer has qualified the duration and end-time relationship."""
        if duration.earliest < 0:
            raise ValueError("duration bounds cannot be negative")
        return cls(TimeBounds(end.earliest - duration.latest, end.latest - duration.earliest), end)

    def valid(self) -> bool:
        if isinstance(self.start, EventTime) or isinstance(self.end, EventTime):
            return _strictly_before(self.start, self.end)
        return _earliest(self.start) < _latest(self.end)

    def contains(self, other: "Interval") -> bool:
        return other.valid() and _at_or_before(self.start, other.start) and _at_or_before(other.end, self.end)

    def overlaps(self, other: "Interval") -> bool:
        """Strictly positive overlap that survives the admitted bounds."""
        return (
            max(_latest(self.start), _latest(other.start)) < min(_earliest(self.end), _earliest(other.end))
            and _strictly_before(self.start, other.end)
            and _strictly_before(other.start, self.end)
        )

    def possibly_overlaps(self, other: "Interval") -> bool:
        """Overlap that cannot be ruled out when excluding other lock holders."""
        return not (_at_or_before(self.end, other.start) or _at_or_before(other.end, self.start))


@dataclass(frozen=True)
class Request:
    actor: ActorRequest
    batch_digest: str
    rpc: Interval
    statement_completed_at: Time
    statement_plan_handle: str


@dataclass(frozen=True)
class FirstCompile:
    # Start may bound an observed portion; end is the verified compilation end.
    actor: ActorRequest
    interval: Interval
    plan_handle: str


@dataclass(frozen=True)
class ResourceKey:
    """Canonical database-scoped key from a qualified resource mapping."""

    database_id: int
    namespace: str
    identity: str = field(repr=False)

    def valid(self) -> bool:
        return self.database_id > 0 and bool(self.namespace) and bool(self.identity)


@dataclass(frozen=True)
class LockHold:
    """Granted ownership, from independently bound acquisition and release."""

    owner: ActorRequest
    resource: ResourceKey
    interval: Interval
    verified_compile: bool


@dataclass(frozen=True)
class Wait:
    actor: ActorRequest
    interval: Interval
    wait_type_key: int
    resource: ResourceKey | None


@dataclass(frozen=True)
class Arm:
    mode: Literal["OFF", "ON"]
    database_id: int
    batch_digest: str
    expected_actors: frozenset[ActorRequest]
    requests: tuple[Request, ...]
    first_compiles: tuple[FirstCompile, ...]
    waits: tuple[Wait, ...]
    lock_holds: tuple[LockHold, ...]
    complete: bool  # Producer attests loss-free capture, provenance, and verified teardown.


@dataclass(frozen=True)
class ArmState:
    """Independently sampled options and comparison inputs for one database."""

    instance_incarnation: str
    database_id: int
    option: Literal["OFF", "ON"]
    profile_digest: str


@dataclass(frozen=True)
class ArmRun:
    evidence: Arm
    before: ArmState
    after: ArmState
    initial_database_plans: int
    workload_digest: str
    barrier_actors: frozenset[ActorRequest]



@dataclass(frozen=True)
class Result:
    status: Literal["PROVEN", "NOT_PROVEN"]
    reason: str


# Numeric key bound by the read-only XE catalog probe on build 17.0.5065.9.
LCK_M_X = 5


def _owns_compile_during_wait(hold: LockHold, wait: Wait, compile_: FirstCompile) -> bool:
    acquired = hold.interval.start
    waiting = wait.interval.start
    if _at_or_before(acquired, waiting):
        return True

    # A wait and a granted lock may be recorded in reverse order at one clock
    # label. This case proves ownership during the measured compile, not at onset.
    return (
        isinstance(acquired, EventTime) and isinstance(waiting, EventTime)
        and acquired.ticks == waiting.ticks and _strictly_before(waiting, acquired)
        and hold.interval.contains(compile_.interval)
    )


def evaluate_arm(arm: Arm) -> Result:
    if not arm.complete:
        return Result("NOT_PROVEN", "incomplete_capture")

    requests = {request.actor: request for request in arm.requests}
    if (
        requests.keys() != arm.expected_actors
        or len(requests) != len(arm.requests)
        or len({actor.session_id for actor in requests}) != len(requests)
        or len(requests) < 2
    ):
        return Result("NOT_PROVEN", "request_set")

    for request in requests.values():
        if (
            request.actor.database_id != arm.database_id
            or not arm.batch_digest
            or request.batch_digest != arm.batch_digest
            or not request.rpc.valid()
            or not _strictly_before(request.rpc.start, request.statement_completed_at)
            or not _at_or_before(request.statement_completed_at, request.rpc.end)
            or not request.statement_plan_handle
        ):
            return Result("NOT_PROVEN", "request_binding")

    compiles = {compile_.actor: compile_ for compile_ in arm.first_compiles}
    if len(compiles) != len(arm.first_compiles):
        return Result("NOT_PROVEN", "duplicate_first_compile")

    for compile_ in compiles.values():
        request = requests.get(compile_.actor)
        if (
            request is None
            or not request.rpc.contains(compile_.interval)
            or not _at_or_before(compile_.interval.end, request.statement_completed_at)
            or compile_.plan_handle != request.statement_plan_handle
        ):
            return Result("NOT_PROVEN", "compile_binding")

    if arm.mode == "OFF":
        if any(
            left.interval.overlaps(right.interval)
            for left, right in combinations(compiles.values(), 2)
        ):
            return Result("PROVEN", "overlapping_first_compiles")
        return Result("NOT_PROVEN", "no_compile_overlap")

    if arm.mode != "ON" or len(compiles) != 1:
        return Result("NOT_PROVEN", "expected_single_first_compile")

    winner, = compiles.values()
    waiters = {actor: request for actor, request in requests.items() if actor != winner.actor}
    if any(
        request.statement_plan_handle != winner.plan_handle
        or not _strictly_before(winner.interval.end, request.statement_completed_at)
        for request in waiters.values()
    ):
        return Result("NOT_PROVEN", "statement_plan_reuse")

    if any(
        not hold.interval.valid() or not hold.resource.valid()
        or hold.owner.database_id != hold.resource.database_id
        for hold in arm.lock_holds
    ):
        return Result("NOT_PROVEN", "invalid_lock_ownership")

    for wait in arm.waits:
        request = waiters.get(wait.actor)
        if (
            request is None
            or wait.wait_type_key != LCK_M_X
            or wait.resource is None
            or wait.resource.database_id != arm.database_id
            or not request.rpc.contains(wait.interval)
            or not wait.interval.overlaps(winner.interval)
            or not _at_or_before(winner.interval.end, wait.interval.end)
            or not _at_or_before(wait.interval.end, request.statement_completed_at)
        ):
            continue
        owners = tuple(
            hold for hold in arm.lock_holds
            if hold.resource == wait.resource and hold.interval.possibly_overlaps(wait.interval)
        )
        if len(owners) != 1:
            continue
        hold, = owners
        if (
            hold.owner == winner.actor
            and hold.verified_compile is True
            and requests[winner.actor].rpc.contains(hold.interval)
            and _owns_compile_during_wait(hold, wait, winner)
            and _at_or_before(winner.interval.end, hold.interval.end)
        ):
            return Result("PROVEN", "compile_wait_and_statement_plan_reuse")
    return Result("NOT_PROVEN", "no_bound_compile_wait")


_SHA256 = re.compile(r"[0-9a-f]{64}", re.ASCII)


def _valid_digest(value: str) -> bool:
    return type(value) is str and _SHA256.fullmatch(value) is not None


def evaluate_pair(off: ArmRun, on: ArmRun) -> Result:
    """Compare one matched pair of normalized arms before any series-level claim."""
    if off.evidence.mode != "OFF" or on.evidence.mode != "ON":
        return Result("NOT_PROVEN", "pair_modes")

    for run in (off, on):
        arm = run.evidence
        if (
            run.before != run.after
            or type(run.before.instance_incarnation) is not str
            or not run.before.instance_incarnation
            or type(arm.database_id) is not int
            or arm.database_id <= 0
            or run.before.database_id != arm.database_id
            or run.before.option != arm.mode
            or not _valid_digest(run.before.profile_digest)
        ):
            return Result("NOT_PROVEN", "arm_state")
        if type(run.initial_database_plans) is not int or run.initial_database_plans != 0:
            return Result("NOT_PROVEN", "initial_cache_state")
        if run.barrier_actors != arm.expected_actors:
            return Result("NOT_PROVEN", "barrier_actor_set")

    if (
        off.before.instance_incarnation != on.before.instance_incarnation
        or off.before.database_id == on.before.database_id
        or off.before.profile_digest != on.before.profile_digest
    ):
        return Result("NOT_PROVEN", "pair_profile")

    if (
        not _valid_digest(off.workload_digest)
        or off.workload_digest != on.workload_digest
        or not _valid_digest(off.evidence.batch_digest)
        or off.evidence.batch_digest != on.evidence.batch_digest
        or len(off.evidence.expected_actors) != len(on.evidence.expected_actors)
    ):
        return Result("NOT_PROVEN", "pair_workload")

    for run in (off, on):
        arm_result = evaluate_arm(run.evidence)
        if arm_result.status != "PROVEN":
            return Result("NOT_PROVEN", f"{run.evidence.mode.lower()}_{arm_result.reason}")
    return Result("PROVEN", "matched_off_on_pair")
