"""Regression für Tagesablauf, Praxiszuordnung und exportierte native Inhalte."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
from validate_sql2025_ai_standard import COURSE, ROOT, course_findings, presentation_findings


class StandardCourseTests(unittest.TestCase):
    def setUp(self):
        self.course = json.loads(COURSE.read_text(encoding='utf-8'))

    def test_current_course_is_coherent(self):
        self.assertEqual(course_findings(self.course), [])

    def test_time_gaps_and_teaching_during_break_are_rejected(self):
        for change in ('gap','negative','pause'):
            course = deepcopy(self.course)
            if change == 'gap': course['blocks'][1]['start_minute'] += 1
            elif change == 'negative': course['blocks'][1]['minutes'] = -1
            else: course['blocks'][7]['demos'] = ['QRY-014']
            with self.subTest(change=change): self.assertTrue(course_findings(course))

    def test_missing_task_reordered_slides_and_source_drift_are_rejected(self):
        for change in ('task','order','source'):
            course = deepcopy(self.course)
            if change == 'task': course['blocks'][8]['demos'] = ['QRY-014']
            elif change == 'order': course['blocks'][8]['source_slides'].reverse()
            else: course['source_sha256'][next(iter(course['source_sha256']))] = '0'*64
            with self.subTest(change=change): self.assertTrue(course_findings(course))

    def test_missing_footer_and_changed_native_content_are_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'Runtime/Temp') as folder:
            copy = Path(folder)/'changed.pptx'
            with ZipFile(ROOT/self.course['output']) as original, ZipFile(copy,'w') as changed:
                for member in original.infolist():
                    data = original.read(member.filename)
                    if member.filename == 'ppt/slides/slide2.xml':
                        data = data.replace(b'STANDARD 2',b'UNBOUND 2').replace(b'Einstieg mit bekannten',b'Veraenderte')
                    changed.writestr(member,data)
            self.course['output'] = str(copy)
            findings = presentation_findings(self.course,label='STANDARD')
            self.assertIn('Folienzuordnung fehlt: 2',findings)
            self.assertIn('Native Inhalte weichen von Quellfolie 2 ab',findings)


if __name__ == '__main__':
    unittest.main()
