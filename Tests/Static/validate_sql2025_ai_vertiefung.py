#!/usr/bin/env python3
"""Prüft Zweitageskurs und reine Belegaufgaben; keine neue ANN-/Livequalifikation."""
from copy import deepcopy
import hashlib
import json
import re
from validate_sql2025_ai_basis import ROOT, SOURCES, presentation_findings
from validate_sql2025_ai_standard import COURSE as STANDARD, DEMOS, SELECTION as DAY1

COURSE = ROOT/'Presentations/AI_SQL_Server_2025/vertiefung.course.json'
FIXTURE = ROOT/'Tests/Static/Fixtures/ai-courses/vertiefung.json'
DAY2 = [51,52,53,54,55,40,41,42,57,58,59,50,56,49,60,61]
RECORDS = [
    'Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_V2_REQUALIFICATION_REVIEW.md',
    'Documentation/HowTo/SQL_SERVER_2025_AI_IDX012_DML_ROLE_RECORDS.md',
    'Documentation/Project_Planning/SQL_SERVER_2025_AI_RESOURCE_AGGREGATION_REVIEW.md',
    'Documentation/HowTo/SQL_SERVER_2025_AI_MODEL_PATHS.md',
    'Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_READER_CLOCK_REVIEW.md',
    'Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_BUILD_COST_REVIEW.md',
    'Documentation/Project_Planning/SQL_SERVER_2025_AI_TENANT_IMPLEMENTATION_REVIEW.md',
    'Documentation/Project_Planning/SQL_SERVER_2025_AI_POOL_REQUALIFICATION_REVIEW.md']


def sha(path):
    return hashlib.sha256(path.read_text(encoding='utf-8').encode()).hexdigest()


def course_findings(course):
    findings = []
    standard = json.loads(STANDARD.read_text(encoding='utf-8'))
    if (course.get('schema') != 'sql2025-ai-vertiefung/v1'
            or course.get('output') != 'Presentations/SQL_Server_2025_KI_VERTIEFUNG.pptx'
            or (course.get('duration_minutes'),course.get('teaching_minutes'),course.get('break_minutes')) != (960,840,120)
            or course.get('standard_course_sha256') != sha(STANDARD)
            or course.get('practical_demos') != DEMOS or course.get('scored_tasks') != DEMOS
            or course.get('source_slide_count') != 61):
        findings.append('Zweitagesumfang oder STANDARD-Bindung verändert')
    first = deepcopy([b for b in course.get('blocks',[]) if b.get('day') == 1])
    for block in first: block.pop('day',None)
    if first != standard['blocks']:
        findings.append('Tag 1 weicht vom vollständigen STANDARD-Ablauf ab')
    position = 0
    numbers = []
    breaks = {1:[],2:[]}
    totals = {1:0,2:0}
    for block in course.get('blocks',[]):
        day = block.get('day')
        minutes = block.get('minutes')
        if day not in totals or type(minutes) is not int or minutes <= 0 or block.get('start_minute') != position:
            findings.append('Tag, Dauer oder durchgehende Zeitfolge ungültig')
            continue
        if (day == 1 and position+minutes > 480) or (day == 2 and position < 480):
            findings.append('Tagesgrenze verschoben')
        position += minutes
        totals[day] += minutes
        numbers.extend(block.get('source_slides',[]))
        if block.get('activity') == 'Pause':
            breaks[day].append(minutes)
            if block.get('source_slides') or block.get('demos'):
                findings.append('Pause enthält Unterricht')
        if day == 2 and (block.get('demos') or block.get('mode') not in {'discussion','record','design','break'}):
            findings.append('Tag 2 enthält eine nicht freigegebene Ausführung')
    if position != 960 or totals != {1:480,2:480} or breaks != {1:[15,30,15],2:[15,30,15]}:
        findings.append('Tagesfenster oder Pausen stimmen nicht')
    if (numbers != DAY1+DAY2 or course.get('repeated_source_slides') != [40,41,42,49,61]
            or set(course.get('source_titles',{})) != {str(n) for n in numbers}):
        findings.append('61-Folien-Folge oder ausdrückliche Wiederholungen verändert')
    if (course.get('overrides') != standard['overrides']
            or set(course.get('slide_overrides',{})) != {'61'}):
        findings.append('Tag-1-Inhalte oder letzte Transferfolie verändert')
    if set(course.get('source_sha256',{})) != set(SOURCES):
        findings.append('Masterquellenbindung unvollständig')
    else:
        for name in SOURCES:
            if course['source_sha256'][name] != sha(ROOT/name): findings.append('Masterdrift: '+name)
    for name in ('guide','workbook'):
        if not (ROOT/course.get(name,'')).is_file(): findings.append('Kursmaterial fehlt: '+name)
    return findings


def exercise_values(fixture):
    """Rechnung der synthetischen Recallaufgabe und der veröffentlichten Population."""
    ann = fixture['ann']
    if (ann['classification'] != 'DIDACTIC_SYNTHETIC' or ann['metric'] != 'cosine' or ann['k'] != 5
            or any(len(ids) != 5 or len(set(ids)) != 5 or not set(ids) <= set(ann['allowed_ids'])
                   for ids in (ann['exact_ids'],ann['ann_ids']))):
        raise ValueError('Ungültige Recallpopulation')
    resource = fixture['resources']
    if (resource['dimensions'] != [32,384,768,1536] or resource['warmups_per_dimension'] != 5
            or resource['pairs'] != 3 or resource['blocks_per_pair'] != 3
            or resource['orders'] != ['AB','BA','AA'] or resource['queries_per_window'] != 100):
        raise ValueError('RES-008-Population verändert')
    warmups = len(resource['dimensions'])*resource['warmups_per_dimension']
    windows = resource['pairs']*resource['blocks_per_pair']*len(resource['orders'])*2
    return {'recall_at_5':len(set(ann['exact_ids']) & set(ann['ann_ids']))/ann['k'],
            'warmups':warmups,'windows':windows,'requests':warmups+windows,
            'query_controls':warmups+windows*resource['queries_per_window'],
            'comparison_windows_per_path':resource['blocks_per_pair']*2}


def exercise_findings(fixture):
    findings = []
    if fixture.get('schema') != 'sql2025-ai-vertiefung-exercises/v1' or set(fixture.get('source_sha256',{})) != set(RECORDS):
        findings.append('Beleginventar unvollständig')
    else:
        for name in RECORDS:
            if fixture['source_sha256'][name] != sha(ROOT/name): findings.append('Belegdrift: '+name)
    if fixture.get('boundaries') != {'ann_generation':'UNKNOWN','ann_record':'COHERENT_PUBLIC_V2',
            'full_performance':'NOT_ESTABLISHED','full_pooling':'NOT_ESTABLISHED',
            'new_live_provider_calls':0,'day2_sql_calls':0}:
        findings.append('Begrenzte Belege werden zur Gesamtfreigabe hochgestuft')
    try:
        if exercise_values(fixture) != {'recall_at_5':0.4,'warmups':20,'windows':54,'requests':74,
                'query_controls':5420,'comparison_windows_per_path':6}:
            findings.append('Rechenaufgabe stimmt nicht')
        text = (ROOT/RECORDS[2]).read_text(encoding='utf-8')
        row = next(line for line in text.splitlines() if re.match(r'\|\s*1\s*\|\s*384\s*\|',line))
        cells = [c.strip() for c in row.split('|')[1:-1]]
        for key,index in (('cpu_ms',2),('elapsed_us',3),('logical_reads',5)):
            if fixture['resources'][key] != [float(x.strip()) for x in cells[index].split('/')]:
                findings.append('Zahlen stimmen nicht mit der veröffentlichten Beobachtung überein: '+key)
    except (KeyError,TypeError,ValueError,StopIteration):
        findings.append('Ungültige oder unvollständige Rechenfixture')
    return findings


def main():
    course = json.loads(COURSE.read_text(encoding='utf-8'))
    fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
    findings = course_findings(course)+exercise_findings(fixture)
    if not findings: findings += presentation_findings(course,label='VERTIEFUNG')
    if findings:
        print('ai-vertiefung: FAIL\n'+'\n'.join(findings))
        return 1
    print('ai-vertiefung: PASS (61 native Folien; 2 x 420+60 Planminuten; Tag 2 Beleglesen/Entwurf)')
    print('offline-exercises: PASS (Recall 0.4; 20/54/74/5420; n=6; acht gebundene Belegquellen; keine Runtimeattestation)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
