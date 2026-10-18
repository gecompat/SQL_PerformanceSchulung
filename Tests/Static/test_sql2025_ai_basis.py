"""Gegenfälle gegen falsche Kursauswahl und unbemerkte Zeitsprünge."""
from copy import deepcopy
import json
import unittest
from validate_sql2025_ai_basis import COURSE, course_findings


class BasisCourseTests(unittest.TestCase):
    def setUp(self):
        self.course = json.loads(COURSE.read_text(encoding='utf-8'))

    def test_current_course_is_coherent(self):
        self.assertEqual(course_findings(self.course), [])

    def test_gap_overlap_and_negative_time_are_rejected(self):
        for field,value in (('start_minute',11),('start_minute',9),('minutes',-1)):
            with self.subTest(field=field,value=value):
                course = deepcopy(self.course)
                course['blocks'][1][field] = value
                self.assertTrue(course_findings(course))

    def test_duplicate_wrong_order_and_changed_source_are_rejected(self):
        course = deepcopy(self.course)
        course['blocks'][8]['source_slides'] = [35,34]
        self.assertTrue(course_findings(course))
        course['blocks'][8]['source_slides'] = [34,34]
        self.assertTrue(course_findings(course))
        course = deepcopy(self.course)
        name = next(iter(course['source_sha256']))
        course['source_sha256'][name] = '0'*64
        self.assertTrue(course_findings(course))

    def test_practical_and_reading_tasks_cannot_be_silently_exchanged(self):
        course = deepcopy(self.course)
        course['practical_demos'] = ['QRY-014','QRY-018']
        self.assertTrue(course_findings(course))
        course = deepcopy(self.course)
        course['blocks'][7]['source_slides'] = [29]
        self.assertTrue(course_findings(course))


if __name__ == '__main__':
    unittest.main()
