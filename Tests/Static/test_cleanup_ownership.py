#!/usr/bin/env python3
"""Gegenproben für Fehlerklassifikation und vollständige Eigentumsfixtures."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Runtime'))
import cleanup_ownership as probe
from execution_target import ExecutionTargetError, docker_target


class CleanupOwnershipTests(unittest.TestCase):
    def test_every_inventory_source_is_unique_and_readable(self):
        self.assertEqual(22, len(set(probe.DEMO_IDS)))
        for demo in probe.DEMO_IDS:
            with self.subTest(demo=demo):
                source = probe.source_path(demo).read_text(encoding='utf-8-sig')
                self.assertNotIn('$(', probe.render(source, demo))
                cases = probe.negative_cases(demo)
                self.assertEqual(len(cases), len({row[0] for row in cases}))
                for name in probe.PROPERTIES:
                    self.assertIn('MISSING_' + name, {row[0] for row in cases})
                    self.assertIn('NULL_' + name, {row[0] for row in cases})
                    self.assertIn('LONG_' + name, {row[0] for row in cases})

    def test_rejection_requires_specific_error_and_stops_next_batch(self):
        target = docker_target(container='synthetic-only', sqlcmd_path='/synthetic/sqlcmd')
        for diagnostic in ('Msg 51004 FAIL_CLEANUP', 'Msg 51004 FAIL_CLEANUP; Msg 51999 UNREACHED_BATCH', 'Msg 51999 OTHER_ERROR', ''):
            with self.subTest(diagnostic=diagnostic):
                effect = ExecutionTargetError(diagnostic) if diagnostic else None
                with patch.object(probe, 'run_sql', side_effect=effect) as run:
                    if diagnostic == 'Msg 51004 FAIL_CLEANUP':
                        probe.rejection(target, 'OPT-002', 'SELECT 1;')
                    else:
                        with self.assertRaises(RuntimeError):
                            probe.rejection(target, 'OPT-002', 'SELECT 1;')
                    self.assertIn('GO\nTHROW 51999', run.call_args.kwargs['sql_text'])

    def test_missing_snapshot_records_are_not_a_pass(self):
        target = docker_target(container='synthetic-only', sqlcmd_path='/synthetic/sqlcmd')
        for output in ('', 'DATABASE|9\n', 'SENTINEL|73\n', 'DATABASE|9\nSENTINEL|73\nSENTINEL|73\n'):
            with self.subTest(output=output), patch.object(probe, 'run_sql', return_value=output):
                with self.assertRaises(RuntimeError):
                    probe.snapshot(target, 'OPT-002')

    def test_snapshot_keeps_complete_suffix_and_nulls(self):
        target = docker_target(container='synthetic-only', sqlcmd_path='/synthetic/sqlcmd')
        outputs = ['DATABASE|9\nSENTINEL|73\nMARKER|' + '41' * 128 + suffix + '|NULL\n' for suffix in ('42', '43')]
        with patch.object(probe, 'run_sql', side_effect=outputs):
            self.assertNotEqual(probe.snapshot(target, 'OPT-002'), probe.snapshot(target, 'OPT-002'))

    def test_restore_oracle_requires_complete_explicit_positive_record(self):
        target = docker_target(container='synthetic-only', sqlcmd_path='/synthetic/sqlcmd')
        for output in ('RESTORE_COMPLETE\n', '', 'RESTORE_COMPLETE\nRESTORE_COMPLETE\n'):
            with self.subTest(output=output), patch.object(probe, 'run_sql', return_value=output) as run:
                if output=='RESTORE_COMPLETE\n':
                    probe.assert_restored(target,'DGN-007')
                else:
                    with self.assertRaises(RuntimeError):
                        probe.assert_restored(target,'DGN-007')
                query=run.call_args.kwargs['sql_text']
                self.assertIn('OBJECT_DEFINITION(OBJECT_ID',query)
                self.assertIn('IS NULL',query)
                self.assertIn('COUNT(*) FROM lab.Dgn007ReferenceState)<>1',query)
                self.assertIn('CONVERT(varbinary(max)',query)

    def test_batch_oracle_never_accepts_missing_or_duplicate_record(self):
        target = docker_target(container='synthetic-only', sqlcmd_path='/synthetic/sqlcmd')
        for output in ('PRESERVED\n','','PRESERVED\nPRESERVED\n'):
            with self.subTest(output=output),patch.object(probe,'run_sql',return_value=output) as run:
                args=(target,'OPT-002','SELECT 1;','SYNTHETIC',{},False,False)
                if output=='PRESERVED\n':
                    probe.batch_rejection(*args)
                else:
                    with self.assertRaises(RuntimeError): probe.batch_rejection(*args)
                query=run.call_args.kwargs['sql_text']
                self.assertIn('@ActualError IS NULL',query)
                self.assertIn('DATALENGTH(@Before)<>DATALENGTH(@After)',query)

    def test_unknown_batch_structure_fails_before_sql(self):
        target = docker_target(container='synthetic-only', sqlcmd_path='/synthetic/sqlcmd')
        for source in ('SELECT 1;\nGO\nSELECT 2;','USE [master];\nGO 2\nSELECT 1;','USE [master];\nGO -- Kommentar\nSELECT 1;'):
            with self.subTest(source=source),patch.object(probe,'run_sql') as run:
                with self.assertRaises(RuntimeError):
                    probe.batch_rejection(target,'OPT-002',source,'SYNTHETIC',{},False,False)
                run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
