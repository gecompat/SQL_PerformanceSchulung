"""Bind a private OPTSP worker record to the existing compile evaluator."""

import re

from optsp_compile_evidence import (
    LCK_M_X, ActorRequest, Arm, ArmRun, ArmState, EventTime, FirstCompile,
    Interval, LockHold, Request, ResourceKey, Wait, evaluate_arm, evaluate_pair,
)

CONFIGURATIONS = ((0, "PAIR"), (1, "PAIR"), (1, "PAIR"), (0, "PAIR"), (0, "SEQUENTIAL"), (0, "DISTINCT"))
DIGEST = re.compile(r"[0-9a-f]{64}")
DECIMAL = re.compile(r"[0-9]{1,20}")


class EvidenceFailure(ValueError):
    """A bounded diagnosis for a failed paired-evidence gate."""


def _digest(value: str) -> str:
    if not isinstance(value, str) or DIGEST.fullmatch(value) is None:
        raise EvidenceFailure("worker_digest")
    return value


def _resource_numbers(values: list[str], width: int) -> tuple[int, ...]:
    if len(values) != width or any(DECIMAL.fullmatch(value) is None for value in values):
        raise EvidenceFailure("compile_coordinates")
    return tuple(map(int, values))


def _bind_compile_lock(record, actors, database, point):
    if record["prepared_entry_matches"] is not True:
        raise EvidenceFailure("prepared_plan_binding")
    matching = [
        row for row in record["wait_key_witness"]
        if row["label"] == "TAB: N:N:N [COMPILE]"
    ]
    if len(matching) != 2:
        raise EvidenceFailure("compile_wait_count")
    begin, end = matching
    waiter = begin["actor"]
    coordinates = _resource_numbers(begin["numeric"], 3)
    if (
        waiter != end["actor"] or (begin["opcode"], end["opcode"]) != ("Begin", "End")
        or coordinates != _resource_numbers(end["numeric"], 3)
        or coordinates[0] != database or coordinates[1] <= 0
    ):
        raise EvidenceFailure("compile_wait_binding")
    _, object_id, partition = coordinates
    key = ResourceKey(database, "build17_compile", f"{object_id}:{partition}")
    wait = Wait(
        actors[waiter],
        Interval(point(begin["ticks"], begin["ordinal"]), point(end["ticks"], end["ordinal"])),
        LCK_M_X, key,
    )
    acquired = {}
    holds = []
    for row in record["object_lock_witness"]:
        fields = _resource_numbers(row["rawfields"], 4)
        if fields != (object_id, object_id, 2, partition):
            continue
        if row["description"] != "[COMPILE]":
            raise EvidenceFailure("compile_lock_classification")
        owner = actors[row["actor"]]
        edge = point(row["ticks"], row["ordinal"])
        if row["name"] == "lock_acquired" and owner not in acquired:
            acquired[owner] = edge
        elif row["name"] == "lock_released" and owner in acquired:
            holds.append(LockHold(owner, key, Interval(acquired.pop(owner), edge), True))
        else:
            raise EvidenceFailure("compile_lock_edges")
    if acquired or len(holds) != 2 or {hold.owner for hold in holds} != set(actors.values()):
        raise EvidenceFailure("compile_lock_ownership")
    return (wait,), tuple(holds)


def bind_arm(record: dict, position: int) -> ArmRun:
    option, variant = CONFIGURATIONS[position]
    database = record["db_id"]
    if (
        record["status"] != "OBSERVED" or record["xe_cleanup"] != "PASS"
        or record["option"] != option or record["variant"] != variant
        or type(database) is not int or database <= 4
        or [actor["ordinal"] for actor in record["actors"]] != [0, 1]
        or record["barrier_actors"] != ([] if variant == "SEQUENTIAL" else [0, 1])
    ):
        raise EvidenceFailure("worker_record")
    mode = "ON" if option else "OFF"
    actors = {index: ActorRequest(database, index + 1, 0) for index in (0, 1)}

    def point(ticks, ordinal):
        return EventTime(ticks, ordinal, f"owned-arm-{position}")

    def edge(row, name):
        return point(row[name], row[name + "_ordinal"])

    requests = []
    compiles = []
    for row in record["actors"]:
        actor = actors[row["ordinal"]]
        # The private worker verified the unique actual cache entry for ON.
        # The evaluator needs identity equivalence, so real handles stay in the worker.
        handle = "verified-prepared" if option else str(row["ordinal"])
        requests.append(Request(
            actor, _digest(row["request_batch_digest"]),
            Interval(edge(row, "rpc_start"), edge(row, "rpc_end")),
            edge(row, "statement_end"), handle,
        ))
        if row["compile_end"] is not None:
            compiles.append(FirstCompile(
                actor, Interval(edge(row, "first_estimate"), edge(row, "compile_end")), handle,
            ))

    waits, holds = _bind_compile_lock(record, actors, database, point) if option else ((), ())
    arm = Arm(
        mode, database, _digest(record["batch_digest"]), frozenset(actors.values()),
        tuple(requests), tuple(compiles), waits, holds, True,
    )
    return ArmRun(
        arm,
        ArmState(_digest(record["instance_before"]), database, mode, _digest(record["profile_before"])),
        ArmState(_digest(record["instance_after"]), database, mode, _digest(record["profile_after"])),
        record["cache_before"], _digest(record["workload_digest"]),
        frozenset(actors[index] for index in record["barrier_actors"]),
    )


def evaluate_series(records: list[dict]) -> tuple[tuple[str, str, str], ...]:
    if len(records) != len(CONFIGURATIONS):
        raise EvidenceFailure("missing_arm")
    runs = [bind_arm(record, position) for position, record in enumerate(records)]
    if (
        len({run.before.database_id for run in runs}) != len(CONFIGURATIONS)
        or len({run.before.instance_incarnation for run in runs}) != 1
        or len({run.before.profile_digest for run in runs}) != 1
        or any(
            run.before != run.after or type(run.initial_database_plans) is not int
            or run.initial_database_plans != 0 for run in runs
        )
    ):
        raise EvidenceFailure("series_profile")

    off, on, on_second, off_second, sequential, distinct = runs
    forward = evaluate_pair(off, on)
    reverse = evaluate_pair(off_second, on_second)
    serial = evaluate_arm(sequential.evidence)
    unequal = evaluate_arm(distinct.evidence)
    unequal_pair = evaluate_pair(distinct, on)
    for direction, pair in (("off_on", forward), ("on_off", reverse)):
        if pair.status != "PROVEN":
            raise EvidenceFailure(f"{direction}_{pair.reason}")
    if (
        serial.reason != "no_compile_overlap" or serial.status != "NOT_PROVEN"
        or sequential.workload_digest != off.workload_digest
        or unequal.reason != "request_binding" or unequal.status != "NOT_PROVEN"
        or unequal_pair.reason != "pair_workload" or unequal_pair.status != "NOT_PROVEN"
        or len({request.batch_digest for request in distinct.evidence.requests}) != 2
    ):
        raise EvidenceFailure("negative_controls")
    return (
        ("OFF_ON", forward.status, forward.reason),
        ("ON_OFF", reverse.status, reverse.reason),
        ("SEQUENTIAL", serial.status, serial.reason),
        ("DISTINCT", unequal.status, unequal.reason),
        ("DISTINCT_PAIR", unequal_pair.status, unequal_pair.reason),
    )
