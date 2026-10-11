"""Fester Filtervertrag; keine adaptive Qualitaetsschwelle oder Indexnutzungsableitung."""
import math

CASES = {1: (1, 1000), 2: (1, 100), 3: (501, 510)}


def valid_integer(value):
    return type(value) is int


def validate_filters(rows):
    data = [row for row in rows if row.get('kind', '').startswith('FILTER_')]
    if any(row.get('kind') not in ('FILTER_EXACT', 'FILTER_APPROX', 'FILTER_MEASURED') for row in data):
        raise RuntimeError('Unknown filter record')
    if any(not valid_integer(row.get('CaseId')) or row['CaseId'] not in CASES for row in data):
        raise RuntimeError('Unknown filter case')
    result = []
    for case, (lo, hi) in CASES.items():
        selected = [row for row in data if row['CaseId'] == case]
        summaries = [row for row in selected if row['kind'] == 'FILTER_MEASURED']
        exact = [row for row in selected if row['kind'] == 'FILTER_EXACT']
        approx = [row for row in selected if row['kind'] == 'FILTER_APPROX']
        if len(summaries) != 1 or len(exact) != 5 or not 0 <= len(approx) <= 5:
            raise RuntimeError('Actual filter row coverage missing or excessive')
        for group in (exact, approx):
            ids = []
            for row in group:
                distance = row.get('DistanceValue')
                if (not valid_integer(row.get('Id')) or not lo <= row['Id'] <= hi
                        or type(distance) not in (int, float) or not math.isfinite(distance)
                        or not 0 <= distance <= 2):
                    raise RuntimeError('Filter source ID or distance invalid')
                ids.append(row['Id'])
            if len(set(ids)) != len(ids):
                raise RuntimeError('Duplicate filter source ID')
        exact_ids = {row['Id'] for row in exact}
        hits = len(exact_ids.intersection(row['Id'] for row in approx))
        summary = summaries[0]
        expected = {'Lo': lo, 'Hi': hi, 'ExactRows': 5, 'ApproxRows': len(approx), 'RecallHits': hits}
        if any(not valid_integer(summary.get(key)) or summary[key] != value for key, value in expected.items()):
            raise RuntimeError('Measured filter summary not bound to actual rows')
        if case < 3 and (len(approx) < 4 or hits < 4):
            raise RuntimeError('Fixed broad filter quality floor failed')
        if case == 3 and approx:
            raise RuntimeError('Fixed narrow postfilter profile changed')
        result.append({'case': case, 'lo': lo, 'hi': hi, 'exact_rows': 5,
                       'approx_rows': len(approx), 'recall_at_5': hits / 5,
                       'quality': 'ROWS_BELOW_K' if len(approx) < 5 else 'K_ROWS',
                       'filtered_index_usage': 'UNPROVEN'})
    return {'kind': 'FILTER_QUALITY', 'generation': 'UNKNOWN', 'cases': result}
