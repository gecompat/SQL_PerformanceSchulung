"""Reines DGN-007-Voraussetzungenmodell, ausschließlich PROJECT_SEMANTIC.

Keine Runtime, Herkunftsattestation, Methodenfreigabe oder zeitliche Einschluss-
behauptung. CONDITIONAL_CONSISTENCY gilt nur unter sämtlichen ausdrücklich
deklarierten Modellannahmen. UNKNOWN/MISSING können keine Herkunft ersetzen.
Die Größen-/Zahlgrenzen sind ausschließlich synthetische Modellgrenzen;
sie genehmigen keine SQL-Capturekosten, Records oder Produktionsmethode.

Sechs Snapshots und zwölf Requests beschreiben eine deklarierte Ordinalfolge.
Vier PRIOR-Requests erhalten keine QS-Zuordnung. T0/T1 werden als Deltas auf
einer expliziten Basis geprüft. Jeder Snapshot muss die finale Querymenge
vollständig rückbinden: PRESENT_COMPLETE oder DECLARED_ABSENT. Keine implizite
Null aus einer selektierten/fehlenden Familie. UTC-Ticks sind Integer ab
0001-01-01 UTC; drei Zeitrelationen werden getrennt und ungerundet berichtet.
Das Modell ist kein v1-Adapter, Collector, Evaluator oder neuer SQL-Vertrag.
avg_rows ist die einzige exemplarische gewichtete Modellmetrik; Duration,
CPU, Reads und Planhashes werden nicht modelliert. Positive Modellzeitrelationen
verwenden inklusiven Request-Einschluss und halboffene Kataloggrenzen nur zur
arithmetischen Charakterisierung, ohne Methoden- oder SQL-Garantie.
"""

from dataclasses import dataclass, fields
from decimal import Decimal
from enum import Enum
from fractions import Fraction


# Ausschließlich Modell-/Fixturegrenzen, keine freigegebenen SQL-Bounds.
MAX_FAMILIES = 16
MAX_FRAGMENTS = 64
MAX_MODEL_COUNT = 1000
MAX_SQL_TICKS = 3155378975999999999
MARKER = "/* DGN007_CASE_SEARCH */"
PAIRS = ((8, 3, 228), (1, 3, 2286), (5, 3, 1144), (1, 1, 571))


class Assumption(Enum):
    DECLARED_MODEL_ASSUMPTION = "DECLARED_MODEL_ASSUMPTION"
    UNKNOWN = "UNKNOWN"
    MISSING = "MISSING"


class CoverageState(Enum):
    PRESENT_COMPLETE = "PRESENT_COMPLETE"
    DECLARED_ABSENT = "DECLARED_ABSENT"
    UNKNOWN = "UNKNOWN"
    MISSING = "MISSING"


class Stage(Enum):
    PRIOR = "PRIOR"
    T0 = "T0"
    T1 = "T1"


class SnapshotKind(Enum):
    BASELINE = "BASELINE"
    T0_PRE = "T0_PRE"
    T0_POST = "T0_POST"
    T1_PRE = "T1_PRE"
    T1_POST = "T1_POST"
    FINAL = "FINAL"


class DeclaredState(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNKNOWN = "UNKNOWN"
    NOT_ATTEMPTED = "NOT_ATTEMPTED"


class Outcome(Enum):
    CONDITIONAL_CONSISTENCY = "CONDITIONAL_CONSISTENCY"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    INCONSISTENT = "INCONSISTENT"


class Issue(Enum):
    CLEANUP_FAILURE = "CLEANUP_FAILURE"
    TIMEOUT = "TIMEOUT"
    INVALID_RECORD = "INVALID_RECORD"
    BINDING_MISMATCH = "BINDING_MISMATCH"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"
    MODEL_OVERFLOW = "MODEL_OVERFLOW"
    ORDER_MISMATCH = "ORDER_MISMATCH"
    REQUEST_MISMATCH = "REQUEST_MISMATCH"
    INVALID_FRAGMENT = "INVALID_FRAGMENT"
    FAMILY_MISMATCH = "FAMILY_MISMATCH"
    INTERVAL_MISMATCH = "INTERVAL_MISMATCH"
    BASELINE_MUTATION = "BASELINE_MUTATION"
    STAGE_DELTA_MISMATCH = "STAGE_DELTA_MISMATCH"
    FINAL_CAPTURE_CHANGED = "FINAL_CAPTURE_CHANGED"
    UNKNOWN_COVERAGE = "UNKNOWN_COVERAGE"
    MISSING_COVERAGE = "MISSING_COVERAGE"
    UNKNOWN_PREMISE = "UNKNOWN_PREMISE"
    MISSING_PREMISE = "MISSING_PREMISE"
    UNKNOWN_COMPLETION = "UNKNOWN_COMPLETION"


@dataclass(frozen=True)
class Binding:
    lifecycle_id: int
    database_generation: int
    source_digest: str


@dataclass(frozen=True)
class Premises:
    execution_discipline: Assumption
    source_and_scope_eligibility: Assumption
    qs_activation: Assumption
    complete_visibility: Assumption
    baseline_completion: Assumption
    truthful_request_completion: Assumption


@dataclass(frozen=True)
class Completion:
    lifecycle: DeclaredState
    cleanup: DeclaredState
    first_absence: DeclaredState
    recovery: DeclaredState
    timed_out: bool


@dataclass(frozen=True)
class Family:
    query_id: int
    parent_query_id: int
    parent_object_id: int
    statement_marker: str


@dataclass(frozen=True)
class Coverage:
    query_id: int
    state: CoverageState
    capture_generation: int


@dataclass(frozen=True)
class Fragment:
    query_id: int
    plan_id: int
    interval_id: int
    execution_type: int
    executions: int | None
    avg_rows: Decimal | None
    first_ticks: int | None
    last_ticks: int | None
    capture_generation: int


@dataclass(frozen=True)
class Snapshot:
    kind: SnapshotKind
    ordinal: int
    binding: Binding
    capture_generation: int
    coverage: tuple[Coverage, ...]
    fragments: tuple[Fragment, ...]


@dataclass(frozen=True)
class Request:
    stage: Stage
    ordinal: int
    sequence: int
    binding: Binding
    request_log_id: int
    group_key: int
    status_code: int
    returned_rows: int | None


@dataclass(frozen=True)
class Window:
    stage: Stage
    condition: str
    interval_id: int
    interval_start_ticks: int
    interval_end_ticks: int
    request_start_ticks: int
    request_finish_ticks: int


@dataclass(frozen=True)
class ModelCase:
    binding: Binding
    major: int
    compatibility_level: int
    parent_object_id: int
    control_sequence: str
    premises: Premises
    completion: Completion
    final_family: tuple[Family, ...]
    snapshots: tuple[Snapshot, ...]
    requests: tuple[Request, ...]
    windows: tuple[Window, ...]


@dataclass(frozen=True)
class TimeRelations:
    stage: Stage
    first_minus_request_start: int
    last_minus_request_finish: int
    qs_inside_request: bool
    qs_inside_catalog: bool
    request_inside_catalog: bool


@dataclass(frozen=True)
class ModelResult:
    outcome: Outcome
    issues: tuple[Issue, ...]
    time_relations: tuple[TimeRelations, ...] = ()

    @property
    def runtime_attested(self) -> bool:
        return False

    @property
    def exact_time_inclusion_claimed(self) -> bool:
        return False

    @property
    def method_approved(self) -> bool:
        return False


class _Invalid(Exception):
    def __init__(self, issue: Issue):
        self.issue = issue


def _need(test: bool, issue: Issue = Issue.INVALID_RECORD) -> None:
    if not test:
        raise _Invalid(issue)


def _int(value: object, low: int = 1, high: int = 2**63 - 1) -> bool:
    return type(value) is int and low <= value <= high


def _binding(value: Binding) -> None:
    _need(type(value) is Binding and _int(value.lifecycle_id)
          and _int(value.database_generation) and type(value.source_digest) is str
          and len(value.source_digest) == 64
          and all(c in "0123456789abcdef" for c in value.source_digest))


def _bound(value: Binding, expected: Binding) -> None:
    _binding(value)
    _binding(expected)
    _need(value == expected, Issue.BINDING_MISMATCH)


def _tuple(value: object, cls: type, maximum: int) -> None:
    _need(type(value) is tuple)
    _need(len(value) <= maximum, Issue.MODEL_OVERFLOW)
    _need(all(type(item) is cls for item in value))


def _fragment(row: Fragment) -> None:
    _need(type(row) is Fragment)
    _need(all(_int(v) for v in (row.query_id, row.plan_id, row.interval_id, row.capture_generation)))
    _need(_int(row.execution_type, 0, 255))
    _need(_int(row.executions, 0, MAX_MODEL_COUNT), Issue.INVALID_FRAGMENT)
    for value in (row.first_ticks, row.last_ticks):
        _need(value is None or _int(value, 0, MAX_SQL_TICKS), Issue.INVALID_FRAGMENT)
    if row.avg_rows is not None:
        _need(type(row.avg_rows) is Decimal and row.avg_rows.is_finite()
              and row.avg_rows >= 0, Issue.INVALID_FRAGMENT)
        parts = row.avg_rows.as_tuple()
        _need(len(parts.digits) <= 18 and -6 <= parts.exponent <= 6,
              Issue.MODEL_OVERFLOW)
    if row.executions > 0:
        _need(row.avg_rows is not None and row.first_ticks is not None
              and row.last_ticks is not None and row.first_ticks <= row.last_ticks,
              Issue.INVALID_FRAGMENT)
    # Zero-Fragmente sind keine Ausführungen; ihre Zeitsemantik wird nicht erfunden.


def _inspect(case: ModelCase, expected: Binding, issues: set[Issue]) -> bool:
    """Alle unabhängigen Records prüfen, auch bei UNKNOWN/MISSING-Premises."""
    def inspect(action):
        try:
            action()
        except _Invalid as error:
            issues.add(error.issue)
        except (AttributeError, TypeError, ValueError):
            issues.add(Issue.INVALID_RECORD)

    inspect(lambda: _binding(expected))
    inspect(lambda: _binding(case.binding))
    inspect(lambda: _bound(case.binding, expected))
    inspect(lambda: _need(_int(case.major, 15, 17)
                         and type(case.compatibility_level) is int
                         and case.compatibility_level == {15: 150, 16: 160, 17: 170}.get(case.major)
                         and _int(case.parent_object_id), Issue.SCOPE_MISMATCH))
    inspect(lambda: _need(type(case.control_sequence) is str
                         and case.control_sequence in ("AB", "BA", "AA"), Issue.SCOPE_MISMATCH))
    inspect(lambda: _need(type(case.premises) is Premises
                         and all(type(getattr(case.premises, f.name)) is Assumption
                                 for f in fields(Premises))))
    inspect(lambda: _need(type(case.completion) is Completion
                         and all(type(getattr(case.completion, f)) is DeclaredState
                                 for f in ("lifecycle", "cleanup", "first_absence", "recovery"))
                         and type(case.completion.timed_out) is bool))
    for name, cls, maximum in (("final_family", Family, MAX_FAMILIES),
                               ("snapshots", Snapshot, 6), ("requests", Request, 12),
                               ("windows", Window, 2)):
        inspect(lambda n=name, c=cls, m=maximum: _tuple(getattr(case, n), c, m))
    # Bounded malformed containers are never traversed as arbitrary iterables.
    for family in case.final_family if type(case.final_family) is tuple and len(case.final_family) <= MAX_FAMILIES else ():
        inspect(lambda f=family: _need(type(f) is Family
                                      and all(_int(v) for v in (f.query_id, f.parent_query_id, f.parent_object_id))
                                      and type(f.statement_marker) is str
                                      and f.statement_marker == MARKER))
    for snap in case.snapshots if type(case.snapshots) is tuple and len(case.snapshots) <= 6 else ():
        def snapshot(s=snap):
            _need(type(s) is Snapshot and type(s.kind) is SnapshotKind
                  and _int(s.ordinal) and _int(s.capture_generation))
            _bound(s.binding, expected)
            _tuple(s.coverage, Coverage, MAX_FAMILIES)
            _tuple(s.fragments, Fragment, MAX_FRAGMENTS)
            for coverage in s.coverage:
                _need(_int(coverage.query_id) and type(coverage.state) is CoverageState
                      and _int(coverage.capture_generation))
                _need(coverage.capture_generation == s.capture_generation, Issue.BINDING_MISMATCH)
        inspect(snapshot)
        if type(snap) is Snapshot and type(getattr(snap, "fragments", None)) is tuple and len(snap.fragments) <= MAX_FRAGMENTS:
            for row in snap.fragments:
                inspect(lambda r=row: _fragment(r))
                inspect(lambda r=row, s=snap: _need(type(r) is Fragment
                                                  and _int(r.capture_generation) and _int(s.capture_generation)
                                                  and r.capture_generation == s.capture_generation,
                                                  Issue.BINDING_MISMATCH))
    for request in case.requests if type(case.requests) is tuple and len(case.requests) <= 12 else ():
        def request_shape(r=request):
            _need(type(r) is Request and type(r.stage) is Stage
                  and _int(r.ordinal, 1, 4) and _int(r.sequence)
                  and _int(r.request_log_id) and _int(r.group_key)
                  and _int(r.status_code, 0, 255)
                  and (r.returned_rows is None or _int(r.returned_rows, 0, 100000)))
            _bound(r.binding, expected)
        inspect(request_shape)
    for window in case.windows if type(case.windows) is tuple and len(case.windows) <= 2 else ():
        inspect(lambda w=window: _need(type(w) is Window and type(w.stage) is Stage
                                      and w.stage in (Stage.T0, Stage.T1)
                                      and type(w.condition) is str and w.condition in ("A", "B")
                                      and _int(w.interval_id)
                                      and all(_int(v, 0, MAX_SQL_TICKS) for v in
                                              (w.interval_start_ticks, w.interval_end_ticks,
                                               w.request_start_ticks, w.request_finish_ticks))
                                      and w.interval_start_ticks < w.interval_end_ticks
                                      and w.request_start_ticks <= w.request_finish_ticks,
                                      Issue.INTERVAL_MISMATCH))
    return not issues.difference({Issue.CLEANUP_FAILURE, Issue.TIMEOUT})


def _ledger(case: ModelCase, issues: set[Issue]) -> tuple[TimeRelations, ...]:
    family = {f.query_id: f for f in case.final_family}
    _need(len(family) == len(case.final_family) and bool(family), Issue.FAMILY_MISMATCH)
    for f in family.values():
        _need(f.parent_object_id == case.parent_object_id
              and f.parent_query_id in family
              and family[f.parent_query_id].parent_query_id == f.parent_query_id
              and (case.major >= 16 or f.query_id == f.parent_query_id), Issue.FAMILY_MISMATCH)
    _need(tuple(s.kind for s in case.snapshots) == tuple(SnapshotKind), Issue.ORDER_MISMATCH)
    _need(len(set(s.capture_generation for s in case.snapshots)) == 6, Issue.BINDING_MISMATCH)
    _need(tuple(w.stage for w in case.windows) == (Stage.T0, Stage.T1), Issue.INTERVAL_MISMATCH)
    w0, w1 = case.windows
    _need(w0.condition + w1.condition == case.control_sequence, Issue.SCOPE_MISMATCH)
    _need(w0.interval_id != w1.interval_id and w0.interval_end_ticks <= w1.interval_start_ticks,
          Issue.INTERVAL_MISMATCH)
    _need(len(case.requests) == 12, Issue.REQUEST_MISMATCH)
    _need(len(set(r.request_log_id for r in case.requests)) == 12
          and all(a.request_log_id < b.request_log_id for a, b in zip(case.requests, case.requests[1:])),
          Issue.REQUEST_MISMATCH)
    for index, stage in enumerate(Stage):
        requests = case.requests[index * 4:index * 4 + 4]
        _need(tuple(r.stage for r in requests) == (stage,) * 4
              and tuple(r.ordinal for r in requests) == (1, 2, 3, 4), Issue.REQUEST_MISMATCH)
        pairs = PAIRS if stage is Stage.PRIOR or case.windows[index - 1].condition == "A" else (PAIRS[1], PAIRS[0], PAIRS[2], PAIRS[3])
        if stage is Stage.PRIOR:
            # Der bestehende Vorab-Cursor garantiert keine feste VALUES-Reihenfolge.
            _need(sorted((r.group_key, r.status_code) for r in requests)
                  == sorted((g, s) for g, s, _ in PAIRS)
                  and all(r.returned_rows is None for r in requests), Issue.REQUEST_MISMATCH)
        else:
            _need(tuple((r.group_key, r.status_code, r.returned_rows) for r in requests) == pairs,
                  Issue.REQUEST_MISMATCH)
    b, pre0, post0, pre1, post1, final = case.snapshots
    chronology = (tuple(r.sequence for r in case.requests[:4]) + (b.ordinal, pre0.ordinal)
                  + tuple(r.sequence for r in case.requests[4:8]) + (post0.ordinal, pre1.ordinal)
                  + tuple(r.sequence for r in case.requests[8:]) + (post1.ordinal, final.ordinal))
    _need(all(a < b for a, b in zip(chronology, chronology[1:])), Issue.ORDER_MISMATCH)
    counts = []
    coverages = []
    plan_queries = {}
    for snap in case.snapshots:
        coverage = {c.query_id: c.state for c in snap.coverage}
        _need(len(coverage) == len(snap.coverage) and not set(coverage).difference(family), Issue.FAMILY_MISMATCH)
        if set(coverage) != set(family):
            issues.add(Issue.MISSING_COVERAGE)
        if CoverageState.MISSING in coverage.values():
            issues.add(Issue.MISSING_COVERAGE)
        if CoverageState.UNKNOWN in coverage.values():
            issues.add(Issue.UNKNOWN_COVERAGE)
        coverages.append(coverage)
        grouped = {}
        for row in snap.fragments:
            _need(row.query_id in family, Issue.FAMILY_MISMATCH)
            _need(coverage.get(row.query_id) is not CoverageState.DECLARED_ABSENT, Issue.FAMILY_MISMATCH)
            _need(row.plan_id not in plan_queries or plan_queries[row.plan_id] == row.query_id,
                  Issue.BINDING_MISMATCH)
            plan_queries[row.plan_id] = row.query_id
            key = (row.query_id, row.plan_id, row.interval_id, row.execution_type)
            grouped[key] = grouped.get(key, 0) + row.executions
        _need(all(c <= MAX_MODEL_COUNT for c in grouped.values()), Issue.MODEL_OVERFLOW)
        counts.append(grouped)
    def signature(snap):
        result = {}
        for row in snap.fragments:
            if row.executions == 0:
                continue
            key = (row.query_id, row.plan_id, row.interval_id, row.execution_type)
            old = result.get(key)
            weighted = Fraction(row.avg_rows) * row.executions
            result[key] = ((old[0] if old else 0) + row.executions,
                           (old[1] if old else 0) + weighted,
                           min(old[2], row.first_ticks) if old else row.first_ticks,
                           max(old[3], row.last_ticks) if old else row.last_ticks)
        return result
    signatures = tuple(signature(s) for s in case.snapshots)
    _need(not any(k[2] in (w0.interval_id, w1.interval_id) for k in signatures[0]),
          Issue.INTERVAL_MISMATCH)
    def complete(index, query):
        return coverages[index].get(query) in (CoverageState.PRESENT_COMPLETE, CoverageState.DECLARED_ABSENT)
    def partial_stable(old, observed, issue):
        # Nichtnegative Counts/Rows und MIN/MAX: fehlende Reste können diese
        # sichtbaren Überschreitungen einer vollständigen früheren Gruppe nicht heilen.
        _need(observed[0] <= old[0] and observed[1] <= old[1]
              and observed[2] >= old[2] and observed[3] <= old[3], issue)
    # Bekannte Teilwidersprüche bleiben prüfbar, auch wenn andere Coverage fehlt.
    # Fehlende Querystatistik wird dabei niemals zu einer Nullbaseline ergänzt.
    for left, right, issue in ((0, 1, Issue.BASELINE_MUTATION),
                                (2, 3, Issue.FINAL_CAPTURE_CHANGED),
                                (4, 5, Issue.FINAL_CAPTURE_CHANGED)):
        for query in family:
            if complete(left, query):
                previous = {k: v for k, v in signatures[left].items() if k[0] == query}
                current = {k: v for k, v in signatures[right].items() if k[0] == query}
                if complete(right, query):
                    _need(previous == current, issue)
                else:
                    for key, value in current.items():
                        _need(key in previous, issue)
                        partial_stable(previous[key], value, issue)
    for window, left, right in ((w0, 1, 2), (w1, 3, 4)):
        observed_additions = 0
        for query in family:
            if not complete(left, query):
                continue
            previous = {k: v for k, v in signatures[left].items() if k[0] == query}
            current = {k: v for k, v in signatures[right].items() if k[0] == query}
            for key, value in previous.items():
                if complete(right, query):
                    _need(current.get(key) == value, Issue.BASELINE_MUTATION)
                elif key in current:
                    partial_stable(value, current[key], Issue.BASELINE_MUTATION)
            for key, value in current.items():
                if key not in previous:
                    _need(key[2] == window.interval_id and key[3] == 0, Issue.STAGE_DELTA_MISMATCH)
                    observed_additions += value[0]
        _need(observed_additions <= 4, Issue.STAGE_DELTA_MISMATCH)
    # Empty group entries imply zero ONLY under explicit complete query coverage.
    if issues.intersection({Issue.MISSING_COVERAGE, Issue.UNKNOWN_COVERAGE}):
        return ()
    # Zero fragments are preserved in snapshots but cannot invent executions.
    def positive(mapping):
        return {key: count for key, count in mapping.items() if count > 0}
    base, before0, after0, before1, after1, final_counts = map(positive, counts)
    _need(base == before0, Issue.BASELINE_MUTATION)
    _need(after0 == before1, Issue.FINAL_CAPTURE_CHANGED)
    _need(after1 == final_counts, Issue.FINAL_CAPTURE_CHANGED)
    _need(signature(b) == signature(pre0), Issue.BASELINE_MUTATION)
    _need(signature(post0) == signature(pre1)
          and signature(post1) == signature(final), Issue.FINAL_CAPTURE_CHANGED)
    _need(not any(k[2] in (w0.interval_id, w1.interval_id) for k in base), Issue.INTERVAL_MISMATCH)
    relations = []
    for window, previous, current, snap in ((w0, before0, after0, post0), (w1, before1, after1, post1)):
        for key, value in previous.items():
            _need(current.get(key) == value, Issue.BASELINE_MUTATION)
        prior_signature = signature(pre0 if window.stage is Stage.T0 else pre1)
        current_signature = signature(snap)
        _need(all(current_signature.get(key) == value for key, value in prior_signature.items()),
              Issue.BASELINE_MUTATION)
        added = {key: value for key, value in current.items() if key not in previous}
        _need(all(key[2] == window.interval_id and key[3] == 0 for key in added)
              and sum(added.values()) == 4
              and sum(current.values()) - sum(previous.values()) == 4,
              Issue.STAGE_DELTA_MISMATCH)
        selected = tuple(r for r in snap.fragments if (r.query_id, r.plan_id, r.interval_id, r.execution_type) in added)
        _need(sum(Fraction(r.avg_rows) * r.executions for r in selected if r.executions > 0) == 4229,
              Issue.STAGE_DELTA_MISMATCH)
        # Positive Modellfragmente liefern die Zeitrelation. Zero-Extrema sind
        # keine Ausführungen; dies ändert ausdrücklich keine SQL-/v1-Semantik.
        first = min(r.first_ticks for r in selected if r.executions > 0)
        last = max(r.last_ticks for r in selected if r.executions > 0)
        relations.append(TimeRelations(window.stage, first - window.request_start_ticks,
                                       last - window.request_finish_ticks,
                                       window.request_start_ticks <= first <= last <= window.request_finish_ticks,
                                       window.interval_start_ticks <= first <= last < window.interval_end_ticks,
                                       window.interval_start_ticks <= window.request_start_ticks
                                       <= window.request_finish_ticks < window.interval_end_ticks))
    return tuple(relations)


def evaluate_model(case: ModelCase, expected_binding: Binding) -> ModelResult:
    """Konditionale Modellkonsistenz; keine tatsächliche Zuordnung festgestellt.

    Feste Issuewerte ohne Eingabedaten. Cleanupfehler und Timeout bleiben auch
    bei ungültigen weiteren Records sichtbar. Recovery heilt first_absence
    nicht. UNKNOWN-Premises verstecken keine prüfbaren Recordwidersprüche.
    """
    issues: set[Issue] = set()
    completion = getattr(case, "completion", None) if type(case) is ModelCase else None
    if type(completion) is Completion:
        if any(getattr(completion, name, None) is DeclaredState.FAILURE
               for name in ("cleanup", "first_absence", "recovery")):
            issues.add(Issue.CLEANUP_FAILURE)
        if getattr(completion, "timed_out", None) is True:
            issues.add(Issue.TIMEOUT)
    relations = ()
    if type(case) is not ModelCase:
        issues.add(Issue.INVALID_RECORD)
    elif not all(hasattr(case, f.name) for f in fields(ModelCase)):
        issues.add(Issue.INVALID_RECORD)
    elif _inspect(case, expected_binding, issues):
        try:
            relations = _ledger(case, issues)
        except _Invalid as error:
            issues.add(error.issue)
        for field in fields(Premises):
            premise = getattr(case.premises, field.name)
            if premise is Assumption.UNKNOWN:
                issues.add(Issue.UNKNOWN_PREMISE)
            if premise is Assumption.MISSING:
                issues.add(Issue.MISSING_PREMISE)
        c = case.completion
        if c.lifecycle is DeclaredState.FAILURE:
            issues.add(Issue.REQUEST_MISMATCH)
        if any(getattr(c, name) is not DeclaredState.SUCCESS for name in ("lifecycle", "cleanup", "first_absence")):
            issues.add(Issue.UNKNOWN_COMPLETION)
    unknown = {Issue.UNKNOWN_COVERAGE, Issue.MISSING_COVERAGE, Issue.UNKNOWN_PREMISE,
               Issue.MISSING_PREMISE, Issue.UNKNOWN_COMPLETION}
    outcome = (Outcome.INCONSISTENT if issues.difference(unknown) else
               Outcome.NOT_ESTABLISHED if issues else Outcome.CONDITIONAL_CONSISTENCY)
    return ModelResult(outcome, tuple(i for i in Issue if i in issues), relations)
