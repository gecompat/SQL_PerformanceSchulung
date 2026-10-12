"""Begrenzte Aggregation vollständig gebundener RES-008-Records; kein SQL."""
from __future__ import annotations

import statistics
import importlib.util
import json
import sys
import res008_measurement as measurement
from res008_source import DIMS

METRICS = ('CpuMs', 'ElapsedUs', 'Reads', 'LogicalReads', 'Writes')
BOUND = 9223372036854775807
MEMORY_KEYS = ('SerialRequiredMemory', 'SerialDesiredMemory', 'RequiredMemory',
               'DesiredMemory', 'RequestedMemory', 'GrantWaitTime', 'MaxQueryMemory',
               'GrantedMemory', 'MaxUsedMemory', 'LastRequestedMemory')
spec = importlib.util.spec_from_file_location(
    'res008_summary_fwk011', measurement.HERE.parents[2] /
    'Demos/00_Framework/Tools/evaluate_result_contract.py')
fwk = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = fwk
spec.loader.exec_module(fwk)


def numeric(value, minimum=0):
    measurement.integer(value, minimum)
    if value > BOUND:
        raise ValueError('Begrenzter tatsächlicher numerischer Wert erforderlich')
    return value


def ratio(comparison, baseline):
    return None if baseline == 0 else comparison / baseline


def distribution(records):
    return {
        name: {'n': len(records),
               'median': statistics.median(r[name] for r in records),
               'min': min(r[name] for r in records),
               'max': max(r[name] for r in records),
               'zero_count': sum(r[name] == 0 for r in records)}
        for name in METRICS
    }


def evaluate_invariants(aggregate, contracts):
    """FWK-011 bewertet ausschließlich die festgelegten numerischen Invarianten."""
    if set(contracts) != set(DIMS[1:]):
        raise ValueError('Drei feste Dimensionsverträge erforderlich')
    reports = []
    for pair in aggregate['pairs']:
        d = pair['dimension']
        contract = contracts[d]
        evidence = {'contract_version': '1.0', 'demo_id': 'RES-008',
                    'profile': 'RES008_D'+str(d)}
        for phase, dimension in (('baseline', 32), ('comparison', d)):
            evidence[phase] = {
                'source_rows': aggregate['storage'][dimension]['rows'],
                'vector_bytes': aggregate['storage'][dimension]['vector_bytes'],
                'measured_windows': pair[phase]['CpuMs']['n'],
                'query_oracles': pair[phase]['CpuMs']['n']*100,
                'query_result_rows': 1,
            }
        demo_id, profile = fwk.validate_metadata(contract, evidence)
        assertions = contract.get('assertions')
        required = {phase+'_'+metric for phase in ('baseline', 'comparison')
                    for metric in ('source_rows', 'vector_bytes', 'measured_windows',
                                   'query_oracles', 'query_result_rows')}
        if (not isinstance(assertions, list) or len(assertions) != 10
                or any(not isinstance(a, dict) for a in assertions)
                or {a.get('id') for a in assertions} != required):
            raise ValueError('Fester vollständiger Invariantenvertrag fehlt')
        seen, results = set(), []
        canonical = {}
        for phase, dimension in (('baseline', 32), ('comparison', d)):
            for metric, expected_value in (('source_rows', 100), ('vector_bytes', 8+4*dimension),
                                           ('measured_windows', 6), ('query_oracles', 600),
                                           ('query_result_rows', 1)):
                canonical[phase+'_'+metric] = (phase, metric, expected_value)
        for assertion in assertions:
            identity = assertion.get('id')
            if identity in seen:
                raise ValueError('Doppelte Assertion')
            seen.add(identity)
            if assertion.get('kind') != 'EXACT' or assertion.get('severity') != 'FAIL' or assertion.get('on_missing') != 'FAIL':
                raise ValueError('Pflichtinvarianten dürfen nicht herabgestuft werden')
            if (set(assertion) != {'id', 'kind', 'phase', 'metric', 'expected', 'severity', 'on_missing'}
                    or type(assertion.get('expected')) is not int
                    or (assertion.get('phase'), assertion.get('metric'), assertion['expected']) != canonical[identity]):
                raise ValueError('Feste Phase-/Metric-/Expected-Bindung verletzt')
            results.append(fwk.evaluate_assertion(assertion, evidence))
        result = fwk.summarize(results, demo_id, profile)
        reports.append({'dimension': d, 'evidence': evidence, 'result': result,
                        'assertions': [r.as_dict(i) for i, r in enumerate(results, 1)]})
        if result['outcome'] != 'PASS':
            raise ValueError('Begrenzte numerische Invarianten nicht bestanden')
    return reports


def summarize_result(result):
    """Positiver Controllerabschluss im Speicher; ausschließlich eigene Verträge."""
    aggregate = summarize(result.evidence, outcome=result.outcome, code=result.code,
                          cleanup_ok=result.cleanup_ok, client_end_unknown=result.client_end_unknown)
    contracts = {}
    for d in DIMS[1:]:
        content = (measurement.HERE/'Expected'/('RES008_D'+str(d)+'.result-contract.json')).read_bytes()
        if len(content) > 10000:
            raise ValueError('Begrenzter eigener Vertrag erforderlich')
        contracts[d] = json.loads(content)
    aggregate['fwk011'] = evaluate_invariants(aggregate, contracts)
    return aggregate


def summarize(evidence, *, outcome, code, cleanup_ok, client_end_unknown):
    """Nur vollständiger positiver Controllerabschluss; keine Rawdaten im Ergebnis.

    Lifecycle-/Quellenattestationen stammen vom Controller. Die erneute reine
    Recordprüfung ersetzt weder native Aufnahme noch deren Provenienzbindung.
    """
    if (outcome, code) != ('WARN', 'WARN_OPTIONAL_EVIDENCE_SKIPPED'):
        raise ValueError('Vollständiges begrenztes Profil mit sichtbaren WARNs erforderlich')
    if cleanup_ok is not True or client_end_unknown is not False:
        raise ValueError('Bestätigter Cleanup und bekanntes Clientende erforderlich')
    if not isinstance(evidence, dict) or evidence.get('qualification') != 'BOUNDED_PROFILE_ONLY':
        raise ValueError('Begrenztes Profil fehlt')
    if any(evidence.get(k) is not True for k in
           ('source_config_equal', 'negative_source_actual', 'negative_query_actual')):
        raise ValueError('Vollständige native Source-/Ergebnisattestationen fehlen')
    database_id = numeric(evidence.get('database_id'), 5)
    expected = [({'kind': 'WARMUP', 'dimension': d, 'ordinal': i}, d, 1)
                for d in DIMS for i in range(1, 6)]
    expected += [({'kind': 'MEASURED', 'pair': pair, 'block': block,
                  'order': order, 'slot': slot}, d, 100)
                 for pair, block, order, slot, d in measurement.slots()]
    windows = evidence.get('windows')
    if not isinstance(windows, list) or len(windows) != len(expected):
        raise ValueError('20 Warmups und 54 vollständige Messfenster erforderlich')
    seen, previous = set(), None
    measured = []
    for item, (labels, dimension, statements) in zip(windows, expected):
        if not isinstance(item, dict) or set(item) != {'labels', 'actual'}:
            raise ValueError('Vollständiger fester Windowrecord erforderlich')
        actual_labels = item['labels']
        if (not isinstance(actual_labels, dict) or actual_labels != labels
                or any(type(actual_labels[k]) is not type(v) for k, v in labels.items())):
            raise ValueError('Exakte Warmup-/AB-/BA-/AA-Reihenfolge erforderlich')
        actual = item['actual']
        identity = measurement.validate(actual, dimension, statements, database_id)
        start = measurement.stamp(actual['StartedUtc'])
        if identity in seen or previous is not None and start < previous:
            raise ValueError('Eindeutige serielle native Requests erforderlich')
        seen.add(identity)
        previous = measurement.stamp(actual['EndedUtc'])
        for name in METRICS:
            numeric(actual[name])
        if labels['kind'] == 'MEASURED':
            measured.append(item)
    storage = evidence.get('storage')
    if not isinstance(storage, dict) or len(storage) != 4:
        raise ValueError('Vollständige vier Storageaufnahmen erforderlich')
    if set(storage) == set(DIMS) and all(type(k) is int for k in storage):
        storage = dict(storage)
    elif set(storage) == {str(d) for d in DIMS}:
        storage = {d: storage[str(d)] for d in DIMS}
    else:
        raise ValueError('Exakte synthetische Dimensionen erforderlich')
    sanitized_storage = {}
    for d, values in storage.items():
        if not isinstance(values, (list, tuple)) or len(values) != 6:
            raise ValueError('Vollständiger Storageframe erforderlich')
        rows, data, used, reserved, minimum, maximum = [numeric(v) for v in values]
        if rows != 100 or not 0 < data <= used <= reserved or minimum != maximum or minimum != 8 + 4*d:
            raise ValueError('Tatsächlicher gebundener Storage-/Vektortypvertrag verletzt')
        sanitized_storage[d] = {'rows': rows, 'data_pages': data, 'used_pages': used,
                                'reserved_pages': reserved, 'vector_bytes': minimum}
    native_plans = evidence.get('plans')
    if not isinstance(native_plans, list) or len(native_plans) != 4:
        raise ValueError('Vier repräsentative Planrecords erforderlich')
    safe_plans = []
    for plan, d in zip(native_plans, DIMS):
        if (not isinstance(plan, dict) or type(plan.get('dimension')) is not int
                or plan['dimension'] != d or plan.get('build') != '17.0.5005.3'
                or plan.get('coverage') != 'REPRESENTATIVE_STATEMENT_ONLY'):
            raise ValueError('Repräsentative native Planbindung fehlt')
        metrics = plan.get('statement_metrics')
        if (not isinstance(metrics, dict) or set(metrics) != {
                'coverage', 'numeric_units', 'degree_of_parallelism', 'non_parallel_reason',
                'memory_grant', 'warnings', 'wait_stats'}
                or metrics['coverage'] != 'REPRESENTATIVE_STATEMENT_ONLY'
                or metrics['numeric_units'] != 'RAW_SHOWPLAN_ATTRIBUTES'):
            raise ValueError('Gebundene repräsentative Statementmetriken fehlen')
        operators = plan.get('operators')
        if not isinstance(operators, list) or not 1 <= len(operators) <= 100:
            raise ValueError('Vollständige gebundene repräsentative Operatorrecords fehlen')
        own_scan = False
        for index, op in enumerate(operators):
            if not isinstance(op, dict):
                raise ValueError('Tatsächlicher Operatorrecord fehlt')
            rows, objects = op.get('actual_rows'), op.get('objects')
            if rows is not None:
                if not isinstance(rows, list) or not 1 <= len(rows) <= 1000:
                    raise ValueError('Begrenzte tatsächliche Operatorrows fehlen')
                for count in rows:
                    numeric(count)
            if index == 0 and (rows is None or sum(rows) != 1):
                raise ValueError('Gebundener tatsächlicher Ergebnisroot fehlt')
            if not isinstance(objects, list) or len(objects) > 100:
                raise ValueError('Begrenzte tatsächliche Quellenobjekte fehlen')
            for obj in objects:
                if not isinstance(obj, dict) or any(obj.get(k) not in (v, '['+v+']')
                        for k, v in (('Database', 'SQLPERF_LAB_RES008_LOCAL'),
                                     ('Schema', 'lab'), ('Table', 'V'+str(d)))):
                    raise ValueError('Fremde repräsentative Planquelle')
                if rows is not None and sum(rows) == 100:
                    own_scan = True
        if not own_scan:
            raise ValueError('Gebundener eigener 100-Row-Scan fehlt')
        memory = metrics.get('memory_grant')
        if not isinstance(memory, dict) or memory.get('state') not in ('CAPTURED', 'NOT_CAPTURED'):
            raise ValueError('Tatsächlicher Memoryzustand fehlt')
        attributes = memory.get('attributes')
        if memory['state'] == 'NOT_CAPTURED':
            if attributes is not None:
                raise ValueError('Fehlende Memoryaufnahme darf keine Attribute erfinden')
        elif not isinstance(attributes, dict) or set(attributes) != set(MEMORY_KEYS):
            raise ValueError('Tatsächliche Memoryattribute fehlen')
        sanitized = {name: None if attributes is None or attributes[name] is None
                     else numeric(attributes[name]) for name in MEMORY_KEYS}
        dop = metrics.get('degree_of_parallelism')
        safe_plans.append({'dimension': d, 'coverage': 'REPRESENTATIVE_STATEMENT_ONLY',
                           'raw_dop': None if dop is None else numeric(dop),
                           'memory_state': memory['state'], 'raw_memory_attributes': sanitized,
                           'waits': 'NOT_EVALUATED', 'spills': 'NOT_EVALUATED'})
    pairs = []
    for d in DIMS[1:]:
        selected = [item for item in measured if item['labels']['pair'] == d]
        a = [item['actual'] for item in selected
             if item['labels']['order'] != 'AA' and item['actual']['Dimension'] == 32]
        b = [item['actual'] for item in selected
             if item['labels']['order'] != 'AA' and item['actual']['Dimension'] == d]
        if not any(r['LogicalReads'] > 0 for r in a) or not any(r['LogicalReads'] > 0 for r in b):
            raise ValueError('Inaktive Messpopulation nach Warmupausschluss')
        controls = []
        for block in range(1, 4):
            aa = [item['actual'] for item in selected
                  if item['labels']['order'] == 'AA' and item['labels']['block'] == block]
            controls.append({'block': block, 'first': {m: aa[0][m] for m in METRICS},
                             'second': {m: aa[1][m] for m in METRICS},
                             'second_over_first': {m: ratio(aa[1][m], aa[0][m]) for m in METRICS}})
        baseline, comparison = distribution(a), distribution(b)
        pairs.append({'dimension': d, 'baseline_dimension': 32, 'windows_per_path': 6,
                      'statements_per_window': 100, 'baseline': baseline, 'comparison': comparison,
                      'median_comparison_over_baseline': {
                          m: ratio(comparison[m]['median'], baseline[m]['median']) for m in METRICS},
                      'aa_controls': controls, 'tail_percentiles': 'N/A_SMALL_BATCH_SAMPLE'})
    return {'kind': 'RES008_BOUNDED_AGGREGATE', 'outcome': outcome, 'code': code,
            'warmup_requests_excluded': 20, 'measured_windows': 54, 'query_oracles': 5420,
            'scope': 'LIVE_REQUEST_BATCH_WITH_COUNTER_AND_TEMP_RESULT_OVERHEAD',
            'zero_baseline_ratio': 'N/A', 'pairs': pairs, 'storage': sanitized_storage,
            'plans': safe_plans, 'runtime_qualification': 'BOUNDED_ONLY',
            'complete_worker_io': 'NOT_ESTABLISHED', 'tp_perf': 'NOT_ESTABLISHED',
            'no_speedup_guarantee': True, 'statistical_significance': 'NOT_ESTABLISHED'}
