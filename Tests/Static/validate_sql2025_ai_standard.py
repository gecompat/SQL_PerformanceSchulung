#!/usr/bin/env python3
"""Prüft den STANDARD-Tageskurs; Lehrzeiten bleiben Planwerte."""
import hashlib
import json
from validate_sql2025_ai_basis import ROOT, SOURCES, presentation_findings

COURSE = ROOT / 'Presentations/AI_SQL_Server_2025/standard.course.json'
DEMOS = ['QRY-014','QRY-015','QRY-016','QRY-017','QRY-018','QRY-019','DGN-008','DGN-009']
SELECTION = list(range(1,29)) + list(range(34,40)) + list(range(43,49)) + [40,41,42,49,61]
PRACTICE = [([34,35,36,37],['QRY-014','QRY-015']),([38,39],['QRY-016']),
            ([43,44],['QRY-017']),([45,46],['QRY-018']),([47,48],['QRY-019']),
            ([40,41,42],['DGN-008']),([49],['DGN-009'])]


def course_findings(course: dict) -> list[str]:
    findings = []
    if (course.get('schema') != 'sql2025-ai-standard/v1'
            or course.get('output') != 'Presentations/SQL_Server_2025_KI_STANDARD.pptx'
            or course.get('source_slide_count') != 61
            or (course.get('duration_minutes'),course.get('teaching_minutes'),course.get('break_minutes')) != (480,420,60)
            or course.get('practical_demos') != DEMOS or course.get('scored_tasks') != DEMOS):
        findings.append('STANDARD-Umfang, Zeitfenster oder Aufgaben geändert')
    position = 0
    pauses = []
    numbers = []
    practice = []
    for block in course.get('blocks', []):
        minutes = block.get('minutes')
        if type(minutes) is not int or minutes <= 0 or block.get('start_minute') != position:
            findings.append('Lücke, Überlappung oder ungültige Dauer')
            continue
        position += minutes
        slides = block.get('source_slides', [])
        demos = block.get('demos', [])
        if block.get('activity') == 'Pause':
            pauses.append(minutes)
            if slides or demos:
                findings.append('Pause enthält Unterricht')
        if demos:
            practice.append((slides,demos))
        numbers.extend(slides)
    if position != 480 or pauses != [15,30,15]:
        findings.append('Tagesablauf erreicht nicht 420+60 Minuten')
    if numbers != SELECTION or set(course.get('source_titles', {})) != {str(n) for n in SELECTION}:
        findings.append('Auswahl oder Reihenfolge der 45 Quellfolien geändert')
    if practice != PRACTICE:
        findings.append('Praxiszuordnung zu den Fachfolien verändert')
    if set(course.get('source_sha256', {})) != set(SOURCES):
        findings.append('Masterquellenbindung unvollständig')
    else:
        for name in SOURCES:
            actual = hashlib.sha256((ROOT/name).read_text(encoding='utf-8').encode()).hexdigest()
            if actual != course['source_sha256'][name]:
                findings.append('Masterquelle geändert: '+name)
    for name in ('guide','workbook'):
        if not (ROOT/course.get(name, '')).is_file():
            findings.append('Kursmaterial fehlt: '+name)
    return findings


def main() -> int:
    course = json.loads(COURSE.read_text(encoding='utf-8'))
    findings = course_findings(course)
    if not findings:
        findings += presentation_findings(course, label='STANDARD')
    if findings:
        print('ai-standard: FAIL\n'+'\n'.join(findings))
        return 1
    print('ai-standard: PASS (45 native Folien; 420+60 Minuten; acht Aufgaben; keine Teilnehmerabnahme)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
