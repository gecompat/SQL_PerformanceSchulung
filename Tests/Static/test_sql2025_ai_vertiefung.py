"""Gegenfälle gegen verkürzten Tag 1, neue Runtimeclaims und falsche Rechenbelege."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
from validate_sql2025_ai_vertiefung import COURSE, FIXTURE, ROOT, course_findings, exercise_findings, presentation_findings


class VertiefungCourseTests(unittest.TestCase):
    def setUp(self):
        self.course = json.loads(COURSE.read_text(encoding='utf-8'))
        self.fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))

    def test_current_definition_and_exercises_are_coherent(self):
        self.assertEqual(course_findings(self.course),[])
        self.assertEqual(exercise_findings(self.fixture),[])

    def test_shortened_first_day_and_extra_live_demo_are_rejected(self):
        for change in ('shorten','execution','day'):
            course = deepcopy(self.course)
            if change == 'shorten': course['blocks'][8]['minutes'] -= 5
            elif change == 'execution': course['blocks'][21]['demos'] = ['IDX-011']
            else: course['blocks'][20]['day'] = 1
            with self.subTest(change=change): self.assertTrue(course_findings(course))

    def test_order_repeats_and_standard_drift_are_rejected(self):
        for change in ('order','repeats','standard'):
            course = deepcopy(self.course)
            if change == 'order': course['blocks'][21]['source_slides'].reverse()
            elif change == 'repeats': course['repeated_source_slides'] = []
            else: course['standard_course_sha256'] = '0'*64
            with self.subTest(change=change): self.assertTrue(course_findings(course))

    def test_false_population_source_values_and_claim_upgrade_are_rejected(self):
        for change in ('duplicate','foreign','cost','source','claim'):
            fixture = deepcopy(self.fixture)
            if change == 'duplicate': fixture['ann']['ann_ids'][-1] = 1
            elif change == 'foreign': fixture['ann']['ann_ids'][-1] = 99
            elif change == 'cost': fixture['resources']['elapsed_us'] = [8169,9000]
            elif change == 'source': fixture['source_sha256'][next(iter(fixture['source_sha256']))] = '0'*64
            else: fixture['boundaries']['full_performance'] = 'PASS'
            with self.subTest(change=change): self.assertTrue(exercise_findings(fixture))

    def test_second_transfer_cannot_silently_use_first_day_content(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'Runtime/Temp') as folder:
            target = Path(folder)/'changed.pptx'
            with ZipFile(ROOT/self.course['output']) as source, ZipFile(target,'w') as changed:
                first_transfer = source.read('ppt/slides/slide45.xml')
                for member in source.infolist():
                    data = source.read(member.filename)
                    if member.filename == 'ppt/slides/slide61.xml':
                        data = first_transfer
                    changed.writestr(member,data)
            self.course['output'] = str(target)
            findings = presentation_findings(self.course,label='VERTIEFUNG')
            self.assertIn('Native Inhalte weichen von Quellfolie 61 ab',findings)
            self.assertIn('Folienzuordnung fehlt: 61',findings)

    def test_pinned_evidence_changes_trigger_both_ci_events(self):
        workflow = (ROOT/'.github/workflows/sql2025-ai-basis.yml').read_text(encoding='utf-8')
        for name in self.fixture['source_sha256']:
            with self.subTest(name=name): self.assertEqual(workflow.count("'"+name+"'"),2)


if __name__ == '__main__':
    unittest.main()
