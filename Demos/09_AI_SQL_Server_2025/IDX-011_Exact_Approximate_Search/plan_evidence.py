"""Begrenzte Actual-Planaufnahme; keine numerische Generationsableitung."""
import re
import xml.etree.ElementTree as ET

NS = {'p': 'http://schemas.microsoft.com/sqlserver/2004/07/showplan'}
STATEMENT = "INSERT #Approx SELECT c.Id,r.distance FROM VECTOR_SEARCH( TABLE=lab.VectorFixture AS c,COLUMN=V,SIMILAR_TO=@q,METRIC='cosine',TOP_N=5) AS r;"


def normalized_statement(value):
    return ' '.join(value.split()).rstrip(';')


def identifier(value, expected):
    return value in (expected, '[' + expected + ']')


def capture_plan(output, token):
    if not re.fullmatch('[A-F0-9]{16}', token):
        raise ValueError('Invalid own token')
    if len(output.encode('utf-8')) > 1000000 or '<!DOCTYPE' in output or '<!ENTITY' in output:
        raise RuntimeError('Plan output outside bounded XML profile')
    blocks = re.findall(r'<ShowPlanXML\b.*?</ShowPlanXML>', output, re.S)
    if not 1 <= len(blocks) <= 4 or output.count('<ShowPlanXML') != len(blocks):
        raise RuntimeError('Missing, incomplete or excessive plan XML')
    statements = []
    for block in blocks:
        if len(block.encode('utf-8')) > 120000:
            raise RuntimeError('Plan XML size exceeded')
        # sqlcmd kann die einzelne XML-Spalte umbrechen; keine inhaltlichen Zeichen trimmen.
        root = ET.fromstring(block.replace('\r', '').replace('\n', ''))
        if root.tag != '{' + NS['p'] + '}ShowPlanXML' or root.get('Build') != '17.0.5005.3':
            raise RuntimeError('Current plan build/namespace not bound')
        for stmt in root.findall('.//p:StmtSimple', NS):
            if normalized_statement(stmt.get('StatementText', '')) == normalized_statement(STATEMENT):
                statements.append(stmt)
    if len(statements) != 1:
        raise RuntimeError('Actual fixed search statement missing or ambiguous')
    stmt = statements[0]
    plan = stmt.find('p:QueryPlan', NS)
    if plan is None:
        raise RuntimeError('Search QueryPlan missing')
    relops = plan.findall('.//p:RelOp', NS)
    if not 1 <= len(relops) <= 100:
        raise RuntimeError('Operator count outside bounded profile')
    parents = {child: parent for parent in plan.iter() for child in parent}
    operators = []
    runtime_rows = []
    own_index_observed = False
    for op in relops:
        counters = op.findall('p:RunTimeInformation/p:RunTimeCountersPerThread', NS)
        actual = []
        for counter in counters:
            raw = counter.get('ActualRows')
            if raw is None or not re.fullmatch('[0-9]+', raw):
                raise RuntimeError('Actual operator rows missing or invalid')
            actual.append(int(raw))
        runtime_rows.extend(actual)
        objects = []
        for obj in op.findall('.//p:Object', NS):
            closest = parents.get(obj)
            while closest is not None and closest.tag != '{' + NS['p'] + '}RelOp':
                closest = parents.get(closest)
            if closest is not op:
                continue
            item = {k: obj.get(k) for k in ('Database', 'Schema', 'Table', 'Index', 'IndexKind')}
            if any(value is not None and len(value) > 1024 for value in item.values()):
                raise RuntimeError('Object attribute size exceeded')
            objects.append(item)
            bound = (identifier(item['Database'], 'SQLPERF_LAB_IDX011_' + token)
                     and identifier(item['Schema'], 'lab')
                     and identifier(item['Table'], 'VectorFixture')
                     and identifier(item['Index'], 'IDX011_OwnVector'))
            if bound and actual and sum(actual) > 0:
                own_index_observed = True
        if len(objects) > 100:
            raise RuntimeError('Object count outside bounded profile')
        operators.append({'node': op.get('NodeId'), 'physical': op.get('PhysicalOp'),
                          'logical': op.get('LogicalOp'), 'actual_rows': actual, 'objects': objects})
    if not runtime_rows or 5 not in runtime_rows:
        raise RuntimeError('Actual search runtime rows not established')
    return {'kind': 'ACTUAL_PLAN', 'build': '17.0.5005.3',
            'generation': 'UNKNOWN',
            'index_usage': 'OWN_INDEX_RUNTIME_OBSERVED' if own_index_observed else 'UNKNOWN',
            'operators': operators}
