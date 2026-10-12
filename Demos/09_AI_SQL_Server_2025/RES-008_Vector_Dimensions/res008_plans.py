"""Vier gebundene repräsentative Actual-Pläne; kein vollständiger Messplanclaim."""
import importlib.util,json,math,re,uuid,xml.etree.ElementTree as ET
from pathlib import Path
from res008_source import DIMS
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
METRICS_SOURCE=ROOT/'Demos/09_AI_SQL_Server_2025/IDX-011_Exact_Approximate_Search/plan_evidence.py'
spec=importlib.util.spec_from_file_location('res008_public_statement_metrics',METRICS_SOURCE)
metrics=importlib.util.module_from_spec(spec);spec.loader.exec_module(metrics)
NS=metrics.NS;LAST_EVIDENCE=None
DATABASE='SQLPERF_LAB_RES008_LOCAL'

def statement(d):
    return f"SELECT TOP(1) Id,VECTOR_DISTANCE('cosine',V,@Q{d}) AS DistanceValue FROM lab.V{d} ORDER BY VECTOR_DISTANCE('cosine',V,@Q{d}),Id OPTION(MAXDOP 1);"

def capture(output,d):
    if d not in DIMS or len(output.encode('utf-8'))>1000000 or re.search(r'<!\s*(DOCTYPE|ENTITY)',output,re.I):raise ValueError('Bounded own XML profile required')
    blocks=re.findall(r'<ShowPlanXML\b.*?</ShowPlanXML>',output,re.S)
    if len(blocks)!=1 or output.count('<ShowPlanXML')!=1 or len(blocks[0].encode('utf-8'))>120000:raise ValueError('One complete bounded actual plan required')
    results=[];header=False;separator=False
    for line in output.replace(blocks[0],'',1).splitlines():
        if '|' not in line:continue
        fields=tuple(part.strip() for part in line.split('|'))
        if fields==('SQLPERF_SUMMARY','PASS','OK'):continue
        if fields==('Id','DistanceValue') and not header and not results:
            header=True;continue
        if header and not separator and not results and len(fields)==2 and all(re.fullmatch(r'-+',part) for part in fields):
            separator=True;continue
        if len(fields)!=2 or fields[0]!='1' or not re.fullmatch(r'[+-]?[0-9]+(?:\.[0-9]*)?(?:[eE][+-]?[0-9]+)?',fields[1]):raise ValueError('Actual representative query row malformed or differs')
        if not math.isfinite(float(fields[1])) or abs(float(fields[1]))>1e-6:raise ValueError('Actual representative query oracle differs')
        results.append(fields)
    if len(results)!=1:raise ValueError('Actual single query result missing')
    root=ET.fromstring(blocks[0].replace('\r','').replace('\n',''))
    if root.tag!='{'+NS['p']+'}ShowPlanXML' or root.get('Build')!='17.0.5005.3':raise ValueError('Actual fixed build/namespace differs')
    matches=[s for s in root.findall('.//p:StmtSimple',NS) if metrics.normalized_statement(s.get('StatementText',''))==metrics.normalized_statement(statement(d))]
    if len(matches)!=1:raise ValueError('Exact representative statement missing or ambiguous')
    plans=matches[0].findall('p:QueryPlan',NS)
    if len(plans)!=1:raise ValueError('Single actual query plan required')
    plan=plans[0];ops=plan.findall('.//p:RelOp',NS)
    if not 1<=len(ops)<=100:raise ValueError('Bounded actual operators required')
    parents={child:parent for parent in plan.iter() for child in parent}
    roots=plan.findall('p:RelOp',NS)
    if len(roots)!=1:raise ValueError('Single actual result root required')
    captured=[];own_source=False;root_one=False
    for op in ops:
        counts=[];threads=set()
        for counter in op.findall('p:RunTimeInformation/p:RunTimeCountersPerThread',NS):
            thread=metrics.unsigned_attribute(counter,'Thread')
            if thread is None or thread in threads or len(threads)>=1000:raise ValueError('Unique actual numeric thread binding missing')
            threads.add(thread)
            actual=metrics.unsigned_attribute(counter,'ActualRows')
            if actual is None:raise ValueError('Actual operator rows missing')
            counts.append(actual)
        if op is roots[0] and counts and sum(counts)==1:root_one=True
        objects=[]
        for obj in op.findall('.//p:Object',NS):
            closest=parents.get(obj)
            while closest is not None and closest.tag!='{'+NS['p']+'}RelOp':closest=parents.get(closest)
            if closest is not op:continue
            item={k:obj.get(k) for k in ('Database','Schema','Table','Index','IndexKind')}
            if any(v is not None and len(v)>1024 for v in item.values()):raise ValueError('Bounded source object required')
            if not metrics.identifier(item['Database'],DATABASE) or not metrics.identifier(item['Schema'],'lab') or not metrics.identifier(item['Table'],'V'+str(d)):raise ValueError('Foreign actual source object')
            if counts and sum(counts)==100:own_source=True
            objects.append(item)
        if len(objects)>100:raise ValueError('Bounded source object count required')
        captured.append({'node':op.get('NodeId'),'physical':op.get('PhysicalOp'),'logical':op.get('LogicalOp'),'actual_rows':counts if counts else None,'objects':objects})
    if not own_source or not root_one:raise ValueError('Actual own hundred-row scan and one-row result root not established')
    return {'dimension':d,'coverage':'REPRESENTATIVE_STATEMENT_ONLY','build':'17.0.5005.3','operators':captured,'statement_metrics':metrics.statement_metrics(plan)}
