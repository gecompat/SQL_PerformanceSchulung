"""Evaluate normalized evidence for the isolated OPTIMIZED_SP_EXECUTESQL pilot.

The producer must qualify the shared time basis, compile boundaries and
resource attribution before submitting evidence. This module does not infer
those facts from raw XE fields or RPC duration.
"""

from dataclasses import dataclass
from itertools import combinations
from typing import Literal


@dataclass(frozen=True)
class ActorRequest:
    database_id: int
    session_id: int
    request_id: int


@dataclass(frozen=True)
class Interval:
    start: int
    end: int

    def valid(self) -> bool:
        return self.start < self.end

    def contains(self, other: "Interval") -> bool:
        return other.valid() and self.start <= other.start < other.end <= self.end

    def overlaps(self, other: "Interval") -> bool:
        return max(self.start, other.start) < min(self.end, other.end)


@dataclass(frozen=True)
class Request:
    actor: ActorRequest
    batch_digest: str
    rpc: Interval
    statement_completed_at: int
    statement_plan_handle: str


@dataclass(frozen=True)
class FirstCompile:
    actor: ActorRequest
    interval: Interval
    plan_handle: str


@dataclass(frozen=True)
class Wait:
    actor: ActorRequest
    blocker: ActorRequest
    interval: Interval
    wait_type_key: int
    verified_compile_resource: str | None


@dataclass(frozen=True)
class Arm:
    mode: Literal["OFF", "ON"]
    database_id: int
    batch_digest: str
    expected_actors: frozenset[ActorRequest]
    requests: tuple[Request, ...]
    first_compiles: tuple[FirstCompile, ...]
    waits: tuple[Wait, ...]
    complete: bool  # Producer attests loss-free capture, provenance, and verified teardown.


@dataclass(frozen=True)
class Result:
    status: Literal["PROVEN", "NOT_PROVEN"]
    reason: str


# Numeric key bound by the read-only XE catalog probe on build 17.0.5065.9.
LCK_M_X = 5


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
            or not request.rpc.start < request.statement_completed_at <= request.rpc.end
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
            or compile_.interval.end > request.statement_completed_at
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
        or request.statement_completed_at <= winner.interval.end
        for request in waiters.values()
    ):
        return Result("NOT_PROVEN", "statement_plan_reuse")

    for wait in arm.waits:
        request = waiters.get(wait.actor)
        if (
            request is not None
            and wait.blocker == winner.actor
            and wait.wait_type_key == LCK_M_X
            and wait.verified_compile_resource
            and request.rpc.contains(wait.interval)
            and winner.interval.start <= wait.interval.start < winner.interval.end
            and winner.interval.end <= wait.interval.end <= request.statement_completed_at
        ):
            return Result("PROVEN", "compile_wait_and_statement_plan_reuse")
    return Result("NOT_PROVEN", "no_bound_compile_wait")
