"""Begrenztes synthetisches Oraclemodell; ausschließlich PROJECT_SEMANTIC.

Tokens sind erfundene individuelle Ausführungsidentitäten, die reales Query
Store nicht liefert. Sättigung folgt aus injektiver Teilmenge und unabhängig
deklarierter Obergrenze, nicht aus vorausgesetzter vollständiger Tokenaufnahme.
Die exakte Viermetrik-/positive-Extrema-Signatur ist nur eine konservative
Modellregel: Fraction beseitigt keine vorherige Floatrundung. Zero-Extrema sind
keine positiven Ausführungszeiten. Ordinals sind eigene Modellereignisse;
Ticks sind getrennte deklarierte Zeitwerte, keine gemeinsame Clockgarantie.
Keine Produktionsrecords, Herkunftsattestation, SQL-Methode oder I/O.
"""

from dataclasses import dataclass, fields
from decimal import Decimal
from enum import Enum
from fractions import Fraction

MAX_ITEMS = 64
MAX_FAMILY = 16
MAX_TICKS = 3155378975999999999
MAX_ORDINAL = 10000


class Assumption(str, Enum):
    DECLARED_MODEL_ASSUMPTION = "DECLARED_MODEL_ASSUMPTION"
    UNKNOWN = "UNKNOWN"
    MISSING = "MISSING"


class Claim(str, Enum):
    CONDITIONALLY_SUPPORTED = "CONDITIONALLY_SUPPORTED"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    REFUTED = "REFUTED"


class Stage(str, Enum):
    PRIOR = "PRIOR"
    T0 = "T0"
    T1 = "T1"


class SnapshotKind(str, Enum):
    BASELINE = "BASELINE"
    T0_POST = "T0_POST"
    T1_POST = "T1_POST"
    FINAL = "FINAL"


class CoverageState(str, Enum):
    COMPLETE = "COMPLETE"
    DECLARED_ABSENT = "DECLARED_ABSENT"
    UNKNOWN = "UNKNOWN"
    MISSING = "MISSING"


class PriorMode(str, Enum):
    READ_WRITE = "READ_WRITE"
    HISTORICALLY_EXCLUDED = "HISTORICALLY_EXCLUDED"


class QsState(str, Enum):
    READ_WRITE_ALL = "READ_WRITE_ALL"
    READ_ONLY = "READ_ONLY"
    READ_WRITE_NONE = "READ_WRITE_NONE"
    OFF = "OFF"


class Issue(str, Enum):
    INVALID_RECORD = "INVALID_RECORD"
    BINDING_MISMATCH = "BINDING_MISMATCH"
    POPULATION_MISMATCH = "POPULATION_MISMATCH"
    ORDER_MISMATCH = "ORDER_MISMATCH"
    ACQUISITION_MISMATCH = "ACQUISITION_MISMATCH"
    INVALID_FRAGMENT = "INVALID_FRAGMENT"
    NON_INJECTIVE_COUNT = "NON_INJECTIVE_COUNT"
    FOREIGN_OR_FUTURE_TOKEN = "FOREIGN_OR_FUTURE_TOKEN"
    SATURATION_MISSING = "SATURATION_MISSING"
    UNKNOWN_PREMISE = "UNKNOWN_PREMISE"
    HISTORICAL_EXCLUSION_MISSING = "HISTORICAL_EXCLUSION_MISSING"
    UNKNOWN_COVERAGE = "UNKNOWN_COVERAGE"
    FAMILY_MISMATCH = "FAMILY_MISMATCH"
    DESTRUCTIVE_CHANGE = "DESTRUCTIVE_CHANGE"
    STABLE_SIGNATURE_CHANGED = "STABLE_SIGNATURE_CHANGED"
    BUCKET_MISMATCH = "BUCKET_MISMATCH"
    STATE_NOT_CONTINUOUS = "STATE_NOT_CONTINUOUS"
    STATE_HISTORY_MISSING = "STATE_HISTORY_MISSING"


@dataclass(frozen=True)
class Binding:
    lifecycle_id: int
    database_generation: int
    source_digest: str


@dataclass(frozen=True)
class Premises:
    actual_closed_universe: Assumption
    eligible_target_statement: Assumption
    truthful_successful_completion: Assumption
    coherent_visible_enumeration: Assumption
    historical_prior_exclusion: Assumption
    complete_state_history: Assumption


@dataclass(frozen=True)
class OracleCall:
    token: int
    stage: Stage
    ordinal: int
    started: int
    finished: int
    binding: Binding
    successful: Assumption
    target_statement_count: int


@dataclass(frozen=True)
class FamilyMember:
    query_id: int
    parent_query_id: int


@dataclass(frozen=True)
class Coverage:
    query_id: int
    state: CoverageState


@dataclass(frozen=True)
class Metrics:
    duration: Decimal
    cpu: Decimal
    logical_reads: Decimal
    rows: Decimal


@dataclass(frozen=True)
class RawFragment:
    query_id: int
    plan_id: int
    interval_id: int
    execution_type: int
    count: int | None
    tokens: tuple[int, ...]
    averages: Metrics | None
    first_ticks: int | None
    last_ticks: int | None
    binding: Binding
    acquisition_id: int


@dataclass(frozen=True)
class Snapshot:
    kind: SnapshotKind
    acquisition_id: int
    started: int
    finished: int
    binding: Binding
    generation_before: int
    generation_after: int
    ledger_epoch: int
    family: tuple[FamilyMember, ...]
    coverage: tuple[Coverage, ...]
    fragments: tuple[RawFragment, ...]


@dataclass(frozen=True)
class Window:
    stage: Stage
    interval_id: int
    interval_start_ticks: int
    interval_end_ticks: int
    request_start_ticks: int
    request_finish_ticks: int
    pulse_interval_id: int


@dataclass(frozen=True)
class StatePoint:
    ordinal: int
    state: QsState


@dataclass(frozen=True)
class CounterCase:
    binding: Binding
    major: int
    compatibility_level: int
    parent_query_id: int
    prior_mode: PriorMode
    premises: Premises
    calls: tuple[OracleCall, ...]
    snapshots: tuple[Snapshot, ...]
    windows: tuple[Window, ...]
    state_history: tuple[StatePoint, ...]
    destructive_ordinals: tuple[int, ...]


@dataclass(frozen=True)
class TimeRelation:
    stage: Stage
    first_minus_start: int
    last_minus_finish: int
    within_request_bounds: bool
    within_catalog_half_open: bool
    pulse_matches_bucket: bool


@dataclass(frozen=True)
class CounterResult:
    call_coverage: Claim
    collective_bucket: Claim
    permanent_state: Claim
    issues: tuple[Issue, ...]
    time_relations: tuple[TimeRelation, ...] = ()
    validation_scope: str = "PROJECT_SEMANTIC"
    runtime_attested: bool = False
    method_approved: bool = False
    exact_time_inclusion_claimed: bool = False


def _int(value, low=1, high=MAX_ORDINAL):
    return type(value) is int and low <= value <= high


def _tuple(value, cls, limit=MAX_ITEMS):
    return type(value) is tuple and len(value) <= limit and all(type(x) is cls for x in value)


def _enum(value, cls):
    return type(value) is cls and any(value is member for member in cls)


def _record(value, cls):
    # Exakte Typen verhindern fremde Getter/Equality; __new__ bleibt ungültig.
    return type(value) is cls and all(hasattr(value, f.name) for f in fields(cls))


def _binding(value):
    return (_record(value, Binding) and _int(value.lifecycle_id) and _int(value.database_generation)
            and type(value.source_digest) is str and len(value.source_digest) == 64
            and all(c in "0123456789abcdef" for c in value.source_digest))


def _decimal(value):
    if type(value) is not Decimal or not value.is_finite() or value < 0:
        return False
    t = value.as_tuple()
    return len(t.digits) <= 34 and -30 <= t.exponent <= 20


def _metrics(value):
    return _record(value, Metrics) and all(_decimal(getattr(value, f.name)) for f in fields(Metrics))


def _shape(case, expected):
    if not _binding(expected) or not _record(case, CounterCase) or not _binding(case.binding):
        return False
    if not (type(case.major) is int and case.major in (15, 16, 17)
            and type(case.compatibility_level) is int and case.compatibility_level == case.major * 10
            and _int(case.parent_query_id) and _enum(case.prior_mode, PriorMode)
            and _record(case.premises, Premises)
            and all(_enum(getattr(case.premises, f.name), Assumption) for f in fields(Premises))):
        return False
    if not (_tuple(case.calls, OracleCall) and _tuple(case.snapshots, Snapshot, 4)
            and _tuple(case.windows, Window, 2) and _tuple(case.state_history, StatePoint)
            and type(case.destructive_ordinals) is tuple and len(case.destructive_ordinals) <= MAX_ITEMS
            and all(_int(x) for x in case.destructive_ordinals)):
        return False
    for c in case.calls:
        if not (_record(c, OracleCall) and _int(c.token) and _enum(c.stage, Stage)
                and _int(c.ordinal, 1, 4) and _int(c.started) and _int(c.finished)
                and c.started <= c.finished and _binding(c.binding)
                and _enum(c.successful, Assumption) and _int(c.target_statement_count, 0, MAX_ITEMS)):
            return False
    for s in case.snapshots:
        if not (_record(s, Snapshot) and _enum(s.kind, SnapshotKind) and _int(s.acquisition_id)
                and _int(s.started) and _int(s.finished) and s.started <= s.finished
                and _binding(s.binding) and _int(s.generation_before) and _int(s.generation_after)
                and _int(s.ledger_epoch) and _tuple(s.family, FamilyMember, MAX_FAMILY)
                and _tuple(s.coverage, Coverage, MAX_FAMILY) and _tuple(s.fragments, RawFragment)):
            return False
        for f in s.family:
            if not (_record(f, FamilyMember) and _int(f.query_id) and _int(f.parent_query_id)):
                return False
        for c in s.coverage:
            if not (_record(c, Coverage) and _int(c.query_id) and _enum(c.state, CoverageState)):
                return False
        for r in s.fragments:
            if not (_record(r, RawFragment) and _int(r.query_id) and _int(r.plan_id)
                    and _int(r.interval_id) and type(r.execution_type) is int and r.execution_type in (0, 3, 4)
                    and (r.count is None or _int(r.count, -MAX_ITEMS, MAX_ITEMS))
                    and type(r.tokens) is tuple and len(r.tokens) <= MAX_ITEMS and all(_int(t) for t in r.tokens)
                    and (r.averages is None or _metrics(r.averages)) and _binding(r.binding)
                    and _int(r.acquisition_id)
                    and (r.first_ticks is None or _int(r.first_ticks, 0, MAX_TICKS))
                    and (r.last_ticks is None or _int(r.last_ticks, 0, MAX_TICKS))):
                return False
    for w in case.windows:
        if not (_record(w, Window) and _enum(w.stage, Stage) and w.stage in (Stage.T0, Stage.T1)
                and _int(w.interval_id) and _int(w.pulse_interval_id)
                and all(_int(v, 0, MAX_TICKS) for v in (w.interval_start_ticks, w.interval_end_ticks,
                                                       w.request_start_ticks, w.request_finish_ticks))
                and w.interval_start_ticks < w.interval_end_ticks
                and w.request_start_ticks <= w.request_finish_ticks):
            return False
    return all(_record(p, StatePoint) and _int(p.ordinal) and _enum(p.state, QsState) for p in case.state_history)


def _ledger(snapshot):
    ledger = {}
    for r in snapshot.fragments:
        if r.count is None or r.count <= 0:
            continue
        key = (r.query_id, r.plan_id, r.interval_id, r.execution_type)
        previous = ledger.get(key, (frozenset(), (Fraction(0),) * 4, r.first_ticks, r.last_ticks))
        sums = tuple(Fraction(getattr(r.averages, f.name)) * r.count for f in fields(Metrics))
        ledger[key] = (previous[0] | frozenset(r.tokens), tuple(a + b for a, b in zip(previous[1], sums)),
                       min(previous[2], r.first_ticks), max(previous[3], r.last_ticks))
    return ledger


def evaluate_countermodel(case: CounterCase, expected_binding: Binding) -> CounterResult:
    """Drei konditionale Schlüsse; niemals tatsächliche QS-/Methodenattestation."""
    if not _shape(case, expected_binding):
        return CounterResult(Claim.REFUTED, Claim.REFUTED, Claim.REFUTED, (Issue.INVALID_RECORD,))
    issues = set()
    call_bad = bucket_bad = False
    call_unknown = bucket_unknown = False
    declared = Assumption.DECLARED_MODEL_ASSUMPTION
    binding_bad = case.binding != expected_binding or any(c.binding != case.binding for c in case.calls)
    state_domain_bad = binding_bad
    if binding_bad:
        issues.add(Issue.BINDING_MISMATCH); call_bad = True
    required = (case.premises.actual_closed_universe, case.premises.eligible_target_statement,
                case.premises.truthful_successful_completion, case.premises.coherent_visible_enumeration)
    if any(p is not declared for p in required) or any(c.successful is not declared for c in case.calls):
        issues.add(Issue.UNKNOWN_PREMISE); call_unknown = True
    if case.prior_mode is PriorMode.HISTORICALLY_EXCLUDED and case.premises.historical_prior_exclusion is not declared:
        issues.add(Issue.HISTORICAL_EXCLUSION_MISSING); call_unknown = True
    expected_calls = tuple((stage, n) for stage in Stage for n in range(1, 5))
    if (tuple((c.stage, c.ordinal) for c in case.calls) != expected_calls
            or len({c.token for c in case.calls}) != 12 or any(c.target_statement_count != 1 for c in case.calls)):
        issues.add(Issue.POPULATION_MISMATCH); call_bad = state_domain_bad = True
    if any(a.finished >= b.started for a, b in zip(case.calls, case.calls[1:])):
        issues.add(Issue.ORDER_MISMATCH); call_bad = state_domain_bad = True
    if tuple(s.kind for s in case.snapshots) != tuple(SnapshotKind) or len(case.windows) != 2:
        issues.add(Issue.ORDER_MISMATCH)
        return CounterResult(Claim.REFUTED, Claim.REFUTED, Claim.REFUTED, tuple(sorted(issues, key=lambda i: i.value)))
    if tuple(w.stage for w in case.windows) != (Stage.T0, Stage.T1):
        issues.add(Issue.ORDER_MISMATCH); bucket_bad = True
    if case.windows[0].interval_id == case.windows[1].interval_id:
        issues.add(Issue.BUCKET_MISMATCH); bucket_bad = True
    snapshots = case.snapshots
    if (len({s.acquisition_id for s in snapshots}) != 4
            or any(a.finished >= b.started for a, b in zip(snapshots, snapshots[1:]))):
        issues.add(Issue.ACQUISITION_MISMATCH); call_bad = state_domain_bad = True
    if len(case.calls) == 12 and snapshots[-1].finished < case.calls[-1].finished:
        issues.add(Issue.ORDER_MISMATCH); state_domain_bad = True
    if len(case.calls) == 12 and (snapshots[0].finished >= case.calls[4].started
                                 or snapshots[1].finished >= case.calls[8].started):
        issues.add(Issue.ORDER_MISMATCH); bucket_bad = True
    if case.destructive_ordinals or len({s.ledger_epoch for s in snapshots}) != 1:
        issues.add(Issue.DESTRUCTIVE_CHANGE); call_bad = True
    family = {f.query_id: f.parent_query_id for f in snapshots[-1].family}
    if (len(family) != len(snapshots[-1].family) or family.get(case.parent_query_id) != case.parent_query_id
            or any(parent != case.parent_query_id for parent in family.values())
            or (case.major == 15 and len(family) != 1)):
        issues.add(Issue.FAMILY_MISMATCH); call_bad = True
    plan_binding = {}
    ledgers = []
    stage_limits = (Stage.PRIOR, Stage.T0, Stage.T1, Stage.T1)
    expected_sizes = (4, 8, 12, 12) if case.prior_mode is PriorMode.READ_WRITE else (0, 4, 8, 8)
    for s, limit, expected_size in zip(snapshots, stage_limits, expected_sizes):
        if (s.binding != case.binding or s.generation_before != case.binding.database_generation
                or s.generation_after != case.binding.database_generation):
            issues.add(Issue.ACQUISITION_MISMATCH); call_bad = state_domain_bad = True
        members = {f.query_id: f.parent_query_id for f in s.family}
        coverage = {c.query_id: c.state for c in s.coverage}
        if (len(members) != len(s.family) or len(coverage) != len(s.coverage)
                or not set(members) <= set(family) or any(family.get(q) != p for q, p in members.items())
                or not set(coverage) <= set(family)):
            issues.add(Issue.FAMILY_MISMATCH); call_bad = True
        for q in family:
            state = coverage.get(q)
            if state in (None, CoverageState.UNKNOWN, CoverageState.MISSING):
                issues.add(Issue.UNKNOWN_COVERAGE); bucket_unknown = True
            elif ((state is CoverageState.COMPLETE and q not in members)
                  or (state is CoverageState.DECLARED_ABSENT and q in members)):
                issues.add(Issue.FAMILY_MISMATCH); call_bad = True
        # E wird aus unabhängig deklarierten, bereits abgeschlossenen Calls gebildet.
        eligible = {c.token for c in case.calls if c.finished < s.started and list(Stage).index(c.stage) <= list(Stage).index(limit)
                    and (case.prior_mode is PriorMode.READ_WRITE or c.stage is not Stage.PRIOR)}
        ended = {c.token for c in case.calls if c.finished < s.started
                 and (case.prior_mode is PriorMode.READ_WRITE or c.stage is not Stage.PRIOR)}
        if len(ended) > expected_size or len(eligible) != expected_size:
            issues.add(Issue.ORDER_MISMATCH); call_unknown = True; bucket_bad = True
        seen = set(); total = 0; valid_rows = True
        for r in s.fragments:  # Kein vorheriges Scopefiltern fremder Rohzeilen.
            if (r.binding != s.binding or r.acquisition_id != s.acquisition_id):
                issues.add(Issue.ACQUISITION_MISMATCH); call_bad = True
            if r.query_id not in members or coverage.get(r.query_id) is CoverageState.DECLARED_ABSENT:
                issues.add(Issue.FAMILY_MISMATCH); call_bad = True
            if r.plan_id in plan_binding and plan_binding[r.plan_id] != r.query_id:
                issues.add(Issue.FAMILY_MISMATCH); call_bad = True
            plan_binding[r.plan_id] = r.query_id
            if (r.count is None or r.count < 0 or r.count != len(r.tokens)
                    or (r.count > 0 and r.execution_type != 0)
                    or (r.count > 0 and (r.averages is None or r.first_ticks is None or r.last_ticks is None
                                        or r.first_ticks > r.last_ticks))):
                issues.add(Issue.INVALID_FRAGMENT); call_bad = True; valid_rows = False
                continue
            if len(set(r.tokens)) != len(r.tokens) or seen.intersection(r.tokens):
                issues.add(Issue.NON_INJECTIVE_COUNT); call_bad = True
            if not set(r.tokens) <= eligible:
                issues.add(Issue.FOREIGN_OR_FUTURE_TOKEN); call_bad = True
            seen.update(r.tokens); total += r.count
        if total != expected_size:
            issues.add(Issue.SATURATION_MISSING); call_unknown = True
        ledgers.append(_ledger(s) if valid_rows else {})
    for old, new in zip(ledgers, ledgers[1:]):
        for key, signature in old.items():
            if new.get(key) != signature:
                issues.add(Issue.STABLE_SIGNATURE_CHANGED); bucket_bad = True
    # Nur bestehende Gruppen stabilisieren; neue Gruppen dürfen die vier neuen Calls tragen.
    if ledgers[-1] != ledgers[-2]:
        issues.add(Issue.STABLE_SIGNATURE_CHANGED); bucket_bad = True
    relations = []
    for index, (w, previous, current) in enumerate(zip(case.windows, ledgers, ledgers[1:])):
        stage_tokens = {c.token for c in case.calls if c.stage is w.stage}
        additions = {key: value for key, value in current.items() if key not in previous}
        tokens = set().union(*(v[0] for v in additions.values())) if additions else set()
        if (tokens != stage_tokens or any(k[2] != w.interval_id or k[3] != 0 for k in additions)
                or any(k[2] == w.interval_id for k in previous)):
            issues.add(Issue.BUCKET_MISMATCH); bucket_bad = True
        if additions:
            first = min(v[2] for v in additions.values()); last = max(v[3] for v in additions.values())
            relations.append(TimeRelation(w.stage, first - w.request_start_ticks, last - w.request_finish_ticks,
                                         w.request_start_ticks <= first <= last <= w.request_finish_ticks,
                                         w.interval_start_ticks <= first <= last < w.interval_end_ticks,
                                         w.pulse_interval_id == w.interval_id))
    state_claim = Claim.NOT_ESTABLISHED
    if case.premises.complete_state_history is not declared or not case.state_history:
        issues.add(Issue.STATE_HISTORY_MISSING)
    if len(case.calls) != 12 or any(a.ordinal >= b.ordinal for a, b in zip(case.state_history, case.state_history[1:])):
        issues.add(Issue.ORDER_MISMATCH); state_claim = Claim.REFUTED
    elif case.state_history:
        required_start = case.calls[0].started if case.prior_mode is PriorMode.READ_WRITE else case.calls[4].started
        history = case.state_history
        # Eigene Ereignisdomain bis zum Finalcapture; keine UTC-/QS-Clockableitung.
        active = [p.state for p in history if required_start <= p.ordinal <= snapshots[-1].finished]
        preceding = [p.state for p in history if p.ordinal <= required_start]
        prior_states = preceding[-1:] if case.premises.complete_state_history is declared else []
        if any(state is not QsState.READ_WRITE_ALL for state in active + prior_states):
            issues.add(Issue.STATE_NOT_CONTINUOUS); state_claim = Claim.REFUTED
        elif not preceding:
            issues.add(Issue.STATE_HISTORY_MISSING)
        elif case.premises.complete_state_history is declared:
            state_claim = Claim.CONDITIONALLY_SUPPORTED
    def claim(bad, unknown):
        return Claim.REFUTED if bad else Claim.NOT_ESTABLISHED if unknown else Claim.CONDITIONALLY_SUPPORTED
    if state_domain_bad:
        state_claim = Claim.REFUTED
    return CounterResult(claim(call_bad, call_unknown), claim(call_bad or bucket_bad, call_unknown or bucket_unknown),
                         state_claim, tuple(sorted(issues, key=lambda i: i.value)), tuple(relations))
