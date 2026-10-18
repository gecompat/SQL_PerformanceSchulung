#!/usr/bin/env python3
"""Prüft BASIS-Ablauf, Masterbindung und native Folien; keine Teilnehmerabnahme."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
COURSE = ROOT / 'Presentations/AI_SQL_Server_2025/basis.course.json'
MASTER = ROOT / 'Presentations/SQL_Server_2025_KI.pptx'
SOURCES = ('Presentations/AI_SQL_Server_2025/content.mjs',
           'Presentations/AI_SQL_Server_2025/introduction.mjs')
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}


def course_findings(course: dict) -> list[str]:
    findings = []
    if (course.get('schema') != 'sql2025-ai-basis/v1'
            or (course.get('duration_minutes'), course.get('teaching_minutes'), course.get('break_minutes')) != (240,210,30)
            or course.get('practical_demos') != ['QRY-014','QRY-019']
            or course.get('scored_tasks') != ['QRY-014','QRY-019'] or course.get('reading_demo') != 'QRY-018'
            or course.get('source_slide_count') != 61):
        findings.append('BASIS-Umfang, Zeitfenster oder Aufgaben geändert')
    position = 0
    pauses = 0
    numbers = []
    for block in course.get('blocks', []):
        minutes = block.get('minutes')
        if type(minutes) is not int or minutes <= 0 or block.get('start_minute') != position:
            findings.append('Ablauf enthält Lücke, Überlappung oder ungültige Dauer')
            continue
        position += minutes
        if block.get('activity') == 'Pause':
            pauses += minutes
            if block.get('source_slides'):
                findings.append('Pause enthält Unterrichtsfolien')
        numbers.extend(block.get('source_slides', []))
    if position != 240 or pauses != 30:
        findings.append('Ablauf erreicht nicht 210 Lehr- und 30 Pausenminuten')
    if (len(numbers) != 39 or len(set(numbers)) != 39 or numbers[:28] != list(range(1,29))
            or numbers[28:] != [34,35,47,48,45,46,40,51,54,57,61]
            or set(course.get('source_titles', {})) != {str(n) for n in numbers}):
        findings.append('Auswahl oder Reihenfolge der 39 Quellfolien geändert')
    if set(course.get('source_sha256', {})) != set(SOURCES):
        findings.append('Masterquellenbindung unvollständig')
    else:
        for name in SOURCES:
            actual = hashlib.sha256((ROOT/name).read_text(encoding='utf-8').encode()).hexdigest()
            if actual != course['source_sha256'][name]:
                findings.append('Masterquelle seit der Kursauswahl geändert: '+name)
    for name in ('guide','workbook'):
        if not (ROOT/course.get(name, '')).is_file():
            findings.append('Kursmaterial fehlt: '+name)
    return findings


def shape_texts(xml: bytes) -> list[str]:
    tree = ET.fromstring(xml)
    shapes = tree.find('p:cSld/p:spTree', NS)
    return [
        ' '.join(' '.join(t.text or '' for t in child.findall('.//a:t', NS)).split())
        for child in shapes if child.findall('.//a:t', NS)]


def body_texts(xml: bytes) -> list[str]:
    return [t for t in shape_texts(xml)
            if not re.fullmatch(r'\d{2}\s+CUR-\d{3}(?: / CUR-\d{3})*',t)
            and not re.fullmatch(r'(?:BASIS|STANDARD|VERTIEFUNG) \d+ · Quellfolie \d+ · CUR-\d{3}(?: / CUR-\d{3})*',t)]


def presentation_findings(course: dict, label: str = 'BASIS') -> list[str]:
    findings = []
    target = ROOT/course['output']
    if not target.is_file():
        return [label+'-Präsentation fehlt']
    numbers = [n for block in course['blocks'] for n in block['source_slides']]
    with ZipFile(MASTER) as master, ZipFile(target) as basis:
        slides = [n for n in basis.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
        if len(slides) != len(numbers):
            findings.append(label+'-Datei enthält nicht die ausgewählte Folienzahl')
        a = ET.fromstring(master.read('ppt/presentation.xml')).find('p:sldSz',NS)
        b = ET.fromstring(basis.read('ppt/presentation.xml')).find('p:sldSz',NS)
        if (a.get('cx'),a.get('cy')) != (b.get('cx'),b.get('cy')):
            findings.append('Folienformat weicht vom Master ab')
        for index, source in enumerate(numbers,1):
            xml = basis.read(f'ppt/slides/slide{index}.xml')
            if index == 1:
                if label not in ' '.join(shape_texts(xml)):
                    findings.append(label+'-Titelfolie nicht gekennzeichnet')
            else:
                original = master.read(f'ppt/slides/slide{source}.xml')
                expected = body_texts(original)
                override = course.get('slide_overrides', {}).get(str(index), course.get('overrides', {}).get(str(source)))
                if override is not None:
                    expected = [course['source_titles'][str(source)]] + [t for pair in override['blocks'] for t in pair] + [override['bottom']]
                if body_texts(xml) != expected:
                    findings.append(f'Native Inhalte weichen von Quellfolie {source} ab')
                if not body_texts(xml) or body_texts(xml)[0] != ' '.join(course['source_titles'][str(source)].split()):
                    findings.append(f'Quellfolgentitel fehlt: {source}')
                if not any(t.startswith(f'{label} {index} · Quellfolie {source} · ') for t in shape_texts(xml)):
                    findings.append(f'Folienzuordnung fehlt: {index}')
            notes = basis.read(f'ppt/notesSlides/notesSlide{index}.xml')
            text = ' '.join(ET.fromstring(notes).itertext())
            original_notes = ' '.join(ET.fromstring(master.read(f'ppt/notesSlides/notesSlide{source}.xml')).itertext())
            if label+'-Folie' not in text or ('SRC-' in original_notes and 'SRC-' not in text):
                findings.append(f'Moderation oder Quellen fehlen: {index}')
        for name in ('docProps/core.xml','docProps/app.xml'):
            for node in ET.fromstring(basis.read(name)).iter():
                if node.tag.rsplit('}',1)[-1].lower() in {'creator','lastmodifiedby','company','manager'} and node.text:
                    findings.append('Identitätsmetadaten nicht neutralisiert')
    return findings


def main() -> int:
    course = json.loads(COURSE.read_text(encoding='utf-8'))
    findings = course_findings(course)
    if not findings:
        findings += presentation_findings(course)
    if findings:
        print('ai-basis: FAIL\n'+'\n'.join(findings))
        return 1
    print('ai-basis: PASS (39 native Folien; 210+30 Minuten; zwei bewertete Aufgaben; keine Teilnehmerabnahme)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
