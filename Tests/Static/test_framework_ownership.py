#!/usr/bin/env python3
"""Gegenproben für vollständige Frameworkmarker und spezifische Ablehnungsrecords."""
from pathlib import Path
from contextlib import redirect_stdout
import io
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Runtime'))
import framework_ownership as probe
from execution_target import ExecutionTargetError,docker_target


def record(check,outcome='FAIL',code='FAIL_STATE'):
    return f'1|LIFECYCLE|{check}|{outcome}|{code}|synthetisch|synthetisch|Erwartung\n'


class FrameworkOwnershipTests(unittest.TestCase):
    def target(self):return docker_target(container='synthetic-only',sqlcmd_path='/synthetic/sqlcmd')

    def test_real_source_has_one_control_batch_and_all_actions_render(self):
        source=probe.SOURCE.read_text(encoding='utf-8-sig')
        phase=probe.control_batch(source)
        self.assertNotIn('\nGO\n',phase)
        for action in probe.ACTIONS:
            text=probe.render(phase,action,17)
            self.assertIn("DECLARE @Action nvarchar(max) = N'"+action+"';",text)
            self.assertIn('DECLARE @RequestedCompatibilityLevel int = 170;',text)

    def test_unknown_preamble_and_go_forms_fail_before_sql(self):
        source=probe.SOURCE.read_text(encoding='utf-8-sig')
        for value in (source.replace('GO\n','GO 2\n',1),source+'\nGO\n',source.replace('USE [master];','DROP DATABASE [synthetic]; USE [master];',1)):
            with self.subTest(value=value[:50]),patch.object(probe,'run_sql') as run:
                with self.assertRaises(RuntimeError):probe.control_batch(value)
                run.assert_not_called()

    def test_invalid_action_and_version_are_rejected(self):
        for action,major in (('OTHER',17),('DROP',14)):
            with self.assertRaises(ValueError):probe.render('',action,major)

    def test_preservation_needs_exact_marker_failure_and_summary(self):
        good=record('OWNERSHIP_MARKERS')+record('SUMMARY')+'PRESERVED\n'
        cases=(good,good.replace('OWNERSHIP_MARKERS','DATABASE_CONFIGURATION'),good.replace('FAIL_STATE','FAIL_EXECUTION'),good+'PRESERVED\n',good.replace('PRESERVED',''),good+'UNEXPECTED\n',good.replace('1|LIFECYCLE|SUMMARY','x|LIFECYCLE|SUMMARY'),good.replace('OWNERSHIP_MARKERS|FAIL','OWNERSHIP_MARKERS|PASS'))
        for text in cases:
            with self.subTest(text=text):
                if text==good:probe.require_preserved(text)
                else:
                    with self.assertRaises(RuntimeError):probe.require_preserved(text)

    def test_invalid_demo_requires_specific_contract_record(self):
        text=record('DEMO_ID',code='FAIL_CONTRACT')+record('SUMMARY',code='FAIL_CONTRACT')+'PRESERVED\n'
        probe.require_preserved(text,invalid_demo=True)
        with self.assertRaises(RuntimeError):probe.require_preserved(text)

    def test_canonical_demo_diagnostic_keeps_embedded_pipes_and_rejects_other_shapes(self):
        native='1|LIFECYCLE|DEMO_ID|FAIL|FAIL_CONTRACT|XXX-000|STL|OPT|QRY|IDX|CON|RES|DGN-nnn|Die Demo-ID ist nicht kanonisch.\n'
        self.assertEqual(probe.rows(native)[0][6],'STL|OPT|QRY|IDX|CON|RES|DGN-nnn')
        probe.require_preserved(native+record('SUMMARY',code='FAIL_CONTRACT')+'PRESERVED\n',invalid_demo=True)
        for bad in (native.replace('STL|OPT','STL|OTHER'),native.replace('DEMO_ID','OWNERSHIP_MARKERS'),native.replace('XXX-000','XXX-001'),native.replace('kanonisch.','anderes.'),native+'EXTRA\n',native.replace('|STL|','|STL|EXTRA|')):
            with self.subTest(bad=bad),self.assertRaises(RuntimeError):probe.rows(bad)

    def test_batch_rejects_unparsed_go_before_sql(self):
        with patch.object(probe,'run_sql') as run:
            with self.assertRaises(RuntimeError):probe.reject_batch(self.target(),'SELECT 1;\nGO\n',{})
            run.assert_not_called()

    def test_full_file_rejection_requires_native_error_and_batch_stop(self):
        source=probe.SOURCE.read_text(encoding='utf-8-sig')
        for text in ('Msg 51002','Msg 51003','Msg 51002 UNREACHED_BATCH',''):
            with self.subTest(text=text),patch.object(probe,'run_sql',side_effect=ExecutionTargetError(text) if text else None):
                if text=='Msg 51002':probe.reject_file(self.target(),source,'DROP',17)
                else:
                    with self.assertRaises(RuntimeError):probe.reject_file(self.target(),source,'DROP',17)

    def test_first_marker_fault_probe_runs_real_source_and_checks_retained_error(self):
        source=probe.SOURCE.read_text(encoding='utf-8-sig')
        output=('1|CLEANUP|PRESERVE_DATABASE_AFTER_CREATE_ERROR|FAIL|FAIL_CLEANUP|Name unterdrückt|Datenbank erhalten|Bleibt erhalten\n'+
                '2|LIFECYCLE|EXECUTION_ERROR|FAIL|FAIL_CLEANUP|51998|erfolgreiche Lifecycle-Aktion|SYNTHETIC_FIRST_MARKER_FAULT\n'+
                '3|LIFECYCLE|SUMMARY|FAIL|FAIL_CLEANUP|||Fehlgeschlagen\n')
        fault_sql=[]
        def run(target,*,database,sql_text,timeout_seconds=120):
            if "SYNTHETIC_FIRST_MARKER_FAULT" in sql_text:
                fault_sql.append(sql_text)
                self.assertIn("DECLARE @Action nvarchar(max) = N'CREATE';",sql_text)
                self.assertIn("SYNTHETIC_FIRST_MARKER_FAULT",sql_text)
                self.assertNotIn('ROLLBACK_NEW_DATABASE',sql_text)
                return output
            return '0\n'
        with patch.object(probe,'run_sql',side_effect=run),patch.object(probe.ownership,'reset_markers') as mark,patch.object(probe,'finish') as cleanup:
            probe.verify_first_marker_failure_is_preserved(self.target(),source,17)
        self.assertEqual(2,len(fault_sql))
        self.assertTrue(any('FirstMarkerProbe' in text and "SQLPERF.Project" in text and f'SELECT COUNT(*) FROM [{probe.ownership.database(probe.DEMO)}].dbo.FirstMarkerProbe)' in text for text in fault_sql))
        self.assertTrue(any('FIRST_MARKER_SET_CHANGED' in text and 'FirstMarkerProbe' not in text for text in fault_sql))
        partial=next(text for text in fault_sql if 'FirstMarkerProbe' in text)
        self.assertIn("THROW 51998, ''SYNTHETIC_FIRST_MARKER_FAULT'', 1;",partial)
        self.assertIn("USE ' + QUOTENAME(@DatabaseName) + N';",partial)
        self.assertEqual(2,mark.call_count)
        self.assertEqual(2,cleanup.call_count)

    def test_first_marker_probe_rejects_missing_original_error_record(self):
        source=probe.SOURCE.read_text(encoding='utf-8-sig')
        output='1|CLEANUP|PRESERVE_DATABASE_AFTER_CREATE_ERROR|FAIL|FAIL_CLEANUP|Name unterdrückt|Datenbank erhalten|Bleibt erhalten\n2|LIFECYCLE|SUMMARY|FAIL|FAIL_CLEANUP|||Fehlgeschlagen\n'
        with patch.object(probe,'run_sql',return_value=output),patch.object(probe.ownership,'reset_markers') as mark:
            with self.assertRaisesRegex(RuntimeError,'Ursprünglicher Fehler'):
                probe.verify_first_marker_failure_is_preserved(self.target(),source,17)
        mark.assert_not_called()

    def test_snapshot_keeps_all_bytes_and_rejects_incomplete_records(self):
        raw=bytes(range(100))+b'\x00\xff'
        good='LENGTH|102\nBYTES|1|'+raw[:100].hex().upper()+'\nBYTES|101|00FF\n'
        for text in (good,good.replace('101|','102|'),good.replace('00FF','00'),good+'BYTES|103|11\n',good.replace('LENGTH|102','LENGTH|1048577'),good.replace('BYTES|1|','BYTES|1|GG')):
            with self.subTest(text=text),patch.object(probe,'run_sql',return_value=text):
                if text==good:self.assertEqual(raw.hex(),probe.snapshot(self.target()))
                else:
                    with self.assertRaises(RuntimeError):probe.snapshot(self.target())

    def test_missing_markers_need_specific_records_after_generic_file_error(self):
        source=probe.SOURCE.read_text(encoding='utf-8-sig');phase=probe.control_batch(source)
        good=record('OWNERSHIP_MARKERS')+record('SUMMARY')+'PRESERVED\n'
        for batch_output in ('PRESERVED\n',good):
            with self.subTest(batch_output=batch_output),patch.object(probe.ownership,'reset_markers'),patch.object(probe,'snapshot',return_value='same'),patch.object(probe,'run_sql',side_effect=[ExecutionTargetError('Msg 51002'),batch_output]) as run:
                if batch_output==good:probe.reject_missing(self.target(),source,phase,'VALIDATE',17)
                else:
                    with self.assertRaises(RuntimeError):probe.reject_missing(self.target(),source,phase,'VALIDATE',17)
                self.assertEqual(2,run.call_count)

    def test_harmful_oracles_require_both_exact_state_failures(self):
        for error in (None,ExecutionTargetError('51994 FRAMEWORK_STATE_WAS_CHANGED'),ExecutionTargetError('51002 OTHER')):
            with self.subTest(error=str(error)),patch.object(probe,'run_sql',side_effect=['ORACLE_COMPLETE','','']),patch.object(probe,'reject_batch',side_effect=error) as batch:
                if error and '51994' in str(error):
                    probe.verify_oracles(self.target());self.assertEqual(2,batch.call_count)
                else:
                    with self.assertRaises(RuntimeError):probe.verify_oracles(self.target())

    def test_positive_needs_unique_success_and_ownership_record(self):
        good=record('OWNERSHIP_MARKERS','PASS','OK')+record('SUMMARY','PASS','OK')
        source=probe.SOURCE.read_text(encoding='utf-8-sig')
        for text in (good,good+record('SUMMARY','PASS','OK'),record('SUMMARY','PASS','OK'),good.replace('OWNERSHIP_MARKERS|PASS','OWNERSHIP_MARKERS|FAIL'),good.replace('SUMMARY|PASS','SUMMARY|WARN'),record('UNEXPECTED')+good):
            with self.subTest(text=text),patch.object(probe,'run_sql',return_value=text):
                if text==good:probe.positive(self.target(),source,'VALIDATE',17)
                else:
                    with self.assertRaises(RuntimeError):probe.positive(self.target(),source,'VALIDATE',17)

    def test_invalid_runtime_shape_fails_before_fixture(self):
        for major,repetitions in ((14,2),(17,1),(17,0)):
            with patch.object(probe,'fixture') as fixture:
                with self.assertRaises(ValueError):probe.run_probes(self.target(),major,repetitions=repetitions)
                fixture.assert_not_called()

    def test_matrix_requires_complete_counter_and_wraps_native_failure(self):
        import run_framework_sql_matrix as matrix
        for result in (180,179):
            with patch.object(probe,'run_probes',return_value=result),redirect_stdout(io.StringIO()):
                if result==180:matrix._test_lifecycle_ownership(container='synthetic-only',sqlcmd_path='/synthetic/sqlcmd',expected_major=17)
                else:
                    with self.assertRaises(matrix.MatrixFailure):matrix._test_lifecycle_ownership(container='synthetic-only',sqlcmd_path='/synthetic/sqlcmd',expected_major=17)
        with patch.object(probe,'run_probes',side_effect=RuntimeError('synthetisch')):
            with self.assertRaises(matrix.MatrixFailure):matrix._test_lifecycle_ownership(container='synthetic-only',sqlcmd_path='/synthetic/sqlcmd',expected_major=17)


if __name__=='__main__':unittest.main()
