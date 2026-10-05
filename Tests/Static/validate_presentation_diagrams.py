#!/usr/bin/env python3
"""Check diagram meaning, including intentionally reversed wait edges."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / 'Presentations/Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx'
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
COUNTS = {4:4, 14:2, 16:3, 20:3, 22:3, 27:3, 29:3, 31:8, 50:6, 51:2, 59:3, 66:3, 78:4}


def inspect(path):
    findings = []
    with ZipFile(path) as archive:
        for number, expected in COUNTS.items():
            root = ET.fromstring(archive.read(f'ppt/slides/slide{number}.xml'))
            arrows = []
            for edge in root.findall('.//p:cxnSp', NS):
                head = edge.find('.//a:headEnd', NS)
                tail = edge.find('.//a:tailEnd', NS)
                pointed = [e for e in (head, tail) if e is not None and e.get('type') != 'none']
                if not pointed:
                    continue
                arrows.append(edge)
                endpoint = head if number == 66 else tail
                if len(pointed) != 1 or endpoint is None or endpoint.get('type') != 'arrow':
                    findings.append(f'slide {number}: wrong arrow endpoint')
            if len(arrows) != expected:
                findings.append(f'slide {number}: {len(arrows)} arrows, expected {expected}')
            if number == 27:
                # Real topology: two independent inputs join at Nested Loops.
                pairs = {(e.find('.//a:stCxn', NS).get('id'),
                          e.find('.//a:endCxn', NS).get('id')) for e in arrows}
                if pairs != {('6','10'), ('8','10'), ('10','12')}:
                    findings.append('slide 27: Lookup plan lacks two inputs into Nested Loops')
            if number == 66:
                # Heads point to startCxn, so waiters are the endCxn objects.
                pairs = {(e.find('.//a:endCxn', NS).get('id'),
                          e.find('.//a:stCxn', NS).get('id')) for e in arrows}
                if pairs != {('8','6'), ('10','6'), ('12','8')}:
                    findings.append('slide 66: waiters do not point to blockers')
            if number == 16:
                pairs = {(e.find('.//a:stCxn', NS).get('id'),
                          e.find('.//a:endCxn', NS).get('id')) for e in arrows}
                if pairs != {('6','8'), ('8','10'), ('10','12')}:
                    findings.append('slide 16: checkpoint must be separate from commit chain')
                checkpoint = next(s for s in root.findall('.//p:sp', NS)
                                  if s.find('p:nvSpPr/p:cNvPr', NS).get('name') == 'flow-5')
                if int(checkpoint.find('.//a:off', NS).get('y')) <= 4038600:
                    findings.append('slide 16: checkpoint is still in the commit row')
            # Validate actual horizontal direction, accounting for flipH.
            for edge in arrows:
                transform = edge.find('.//a:xfrm', NS)
                extent = transform.find('a:ext', NS)
                if extent.get('cy') == '0':
                    points_left = transform.get('flipH') in ('1', 'true')
                    if number == 66:
                        points_left = not points_left
                    expected_left = number in (27, 66)
                    if points_left != expected_left:
                        findings.append(f'slide {number}: horizontal arrow points the wrong way')
        checks = {17:['Log-Autogrowth bis 64 MB ab SQL Server 2022'],
                  39:['WHERE EventTime >= @Date'],
                  54:['Relative Zugriffskosten (Schema)', 'Trefferzahl steigt'],
                  66:['Session wartet auf die Session an der Pfeilspitze']}
        for number, fragments in checks.items():
            root = ET.fromstring(archive.read(f'ppt/slides/slide{number}.xml'))
            text = ' '.join(n.text or '' for n in root.findall('.//a:t', NS))
            for fragment in fragments:
                if fragment not in text:
                    findings.append(f'slide {number}: missing clarification {fragment}')
    return findings


if __name__ == '__main__':
    results = inspect(Path(sys.argv[1]) if len(sys.argv) > 1 else DECK)
    print('presentation-diagrams: ' + ('FAIL' if results else 'PASS (13 arrow diagrams, topology and clarifications)'))
    for result in results:
        print('- ' + result)
    sys.exit(bool(results))
