"""Showplan-Gegenproben mit synthetischer Quelle; keine SQL-Ausführung."""
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / 'Demos/09_AI_SQL_Server_2025/IDX-011_Exact_Approximate_Search'
spec = importlib.util.spec_from_file_location('idx011_plan_metrics', FOLDER / 'plan_evidence.py')
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)
TOKEN = 'ABCDEF0123456789'
URI = parser.NS['p']
ET.register_namespace('', URI)


def tag(name):
    return '{' + URI + '}' + name


def fixture():
    root = ET.Element(tag('ShowPlanXML'), Build='17.0.5005.3')
    stmt = ET.SubElement(root, tag('StmtSimple'), StatementText=parser.STATEMENT)
    plan = ET.SubElement(stmt, tag('QueryPlan'), DegreeOfParallelism='0', NonParallelPlanReason='MaxDOPSetToOne')
    ET.SubElement(plan, tag('MemoryGrantInfo'), RequestedMemory='1024', GrantedMemory='1024', MaxUsedMemory='32', GrantWaitTime='0')
    op = ET.SubElement(plan, tag('RelOp'), NodeId='0', PhysicalOp='Index Seek', LogicalOp='Index Seek')
    runtime = ET.SubElement(op, tag('RunTimeInformation'))
    ET.SubElement(runtime, tag('RunTimeCountersPerThread'), Thread='0', ActualRows='5')
    seek = ET.SubElement(op, tag('IndexScan'))
    ET.SubElement(seek, tag('Object'), Database='[SQLPERF_LAB_IDX011_' + TOKEN + ']', Schema='[lab]', Table='[VectorFixture]', Index='[IDX011_OwnVector]')
    return root, stmt, plan, op


def capture(root, token=TOKEN):
    return parser.capture_plan(ET.tostring(root, encoding='unicode'), token)


class PlanMeasurements(unittest.TestCase):
    def test_actual_zero_and_missing_values_are_distinct(self):
        root, _, plan, _ = fixture()
        values = capture(root)['statement_metrics']
        self.assertEqual(values['degree_of_parallelism'], 0)
        self.assertEqual(values['memory_grant']['attributes']['GrantWaitTime'], 0)
        self.assertIsNone(values['memory_grant']['attributes']['LastRequestedMemory'])
        self.assertEqual(values['coverage'], 'REPRESENTATIVE_STATEMENT_ONLY')
        self.assertEqual(values['numeric_units'], 'RAW_SHOWPLAN_ATTRIBUTES')
        del plan.attrib['DegreeOfParallelism']
        self.assertIsNone(capture(root)['statement_metrics']['degree_of_parallelism'])

    def test_memory_grant_missing_is_not_zero(self):
        root, _, plan, _ = fixture()
        plan.remove(plan.find(tag('MemoryGrantInfo')))
        self.assertEqual(capture(root)['statement_metrics']['memory_grant'], {'state': 'NOT_CAPTURED', 'attributes': None})

    def test_nested_memory_grant_is_not_statement_memory(self):
        root, _, plan, op = fixture()
        node = plan.find(tag('MemoryGrantInfo'))
        plan.remove(node)
        op.append(node)
        self.assertEqual(capture(root)['statement_metrics']['memory_grant']['state'], 'NOT_CAPTURED')

    def test_duplicate_statement_memory_is_rejected(self):
        root, _, plan, _ = fixture()
        ET.SubElement(plan, tag('MemoryGrantInfo'), RequestedMemory='1024')
        with self.assertRaises(RuntimeError):
            capture(root)

    def test_invalid_or_excessive_numeric_values_are_rejected(self):
        for invalid in ('-1', '1.5', 'NaN', 'True', '9223372036854775808', '0' * 20):
            with self.subTest(invalid=invalid):
                root, _, plan, _ = fixture()
                plan.find(tag('MemoryGrantInfo')).set('MaxUsedMemory', invalid)
                with self.assertRaises(RuntimeError):
                    capture(root)

    def test_absent_warnings_and_waits_are_not_zero_cost(self):
        values = capture(fixture()[0])['statement_metrics']
        self.assertEqual(values['warnings'], {'state': 'NOT_CAPTURED', 'element_count': None, 'child_tags': None})
        self.assertEqual(values['wait_stats'], {'state': 'NOT_CAPTURED', 'entry_count': None})

    def test_present_empty_nodes_preserve_observed_empty_structure(self):
        root, _, plan, _ = fixture()
        ET.SubElement(plan, tag('Warnings'))
        ET.SubElement(plan, tag('WaitStats'))
        values = capture(root)['statement_metrics']
        self.assertEqual(values['warnings']['child_tags'], [])
        self.assertEqual(values['warnings']['element_count'], 1)
        self.assertEqual(values['wait_stats'], {'state': 'CAPTURED', 'entry_count': 0})

    def test_warning_presence_is_not_a_spill_counter(self):
        root, _, plan, op = fixture()
        warnings = ET.SubElement(op, tag('Warnings'))
        ET.SubElement(warnings, tag('SpillToTempDb'), SpillLevel='1')
        ET.SubElement(plan, tag('WaitStats'))
        values = capture(root)['statement_metrics']
        self.assertEqual(values['warnings']['child_tags'], ['SpillToTempDb'])
        self.assertNotIn('spill_count', values)

    def test_duplicate_wait_stats_and_query_plan_are_rejected(self):
        for name in ('WaitStats', 'QueryPlan'):
            root, stmt, plan, _ = fixture()
            if name == 'WaitStats':
                ET.SubElement(plan, tag(name))
                ET.SubElement(plan, tag(name))
            else:
                ET.SubElement(stmt, tag(name))
            with self.subTest(name=name), self.assertRaises(RuntimeError):
                capture(root)

    def test_other_statements_do_not_supply_memory_evidence(self):
        root, _, plan, _ = fixture()
        plan.remove(plan.find(tag('MemoryGrantInfo')))
        other = ET.SubElement(root, tag('StmtSimple'), StatementText='SELECT 1;')
        other_plan = ET.SubElement(other, tag('QueryPlan'), DegreeOfParallelism='8')
        ET.SubElement(other_plan, tag('MemoryGrantInfo'), RequestedMemory='9999')
        values = capture(root)['statement_metrics']
        self.assertEqual(values['degree_of_parallelism'], 0)
        self.assertEqual(values['memory_grant']['state'], 'NOT_CAPTURED')

    def test_statement_and_build_binding_remain_required(self):
        for field in ('statement', 'build', 'duplicate', 'token'):
            root, stmt, _, _ = fixture()
            if field == 'statement':
                stmt.set('StatementText', 'SELECT 1;')
            elif field == 'build':
                root.set('Build', '17.0.4075.5')
            elif field == 'duplicate':
                root.append(ET.fromstring(ET.tostring(stmt)))
            with self.subTest(field=field), self.assertRaises((RuntimeError, ValueError)):
                capture(root, TOKEN + 'X' if field == 'token' else TOKEN)

    def test_foreign_object_cannot_establish_owned_index_usage(self):
        root, _, _, op = fixture()
        op.find('.//' + tag('Object')).set('Database', '[SQLPERF_LAB_IDX011_FOREIGN]')
        self.assertEqual(capture(root)['index_usage'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
