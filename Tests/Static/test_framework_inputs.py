#!/usr/bin/env python3
"""Unabhängige Gegenfälle für den Framework-Eingabenachweis ohne SQL-Effekt."""
from contextlib import redirect_stdout
import io
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Runtime'))
import framework_inputs as probe
from execution_target import ExecutionTargetError,docker_target


def record(check: str,*,code: str='FAIL_CONTRACT',outcome: str='FAIL',tail: str='synthetisch|synthetisch|Erwartung') -> str:
    return f'1|LIFECYCLE|{check}|{outcome}|{code}|{tail}\n'


class FrameworkInputTests(unittest.TestCase):
    def target(self):return docker_target(container='synthetic-only',sqlcmd_path='/synthetic/sqlcmd')

    def test_inventory_covers_all_raw_families_null_unicode_and_long_suffixes(self):
        for action in probe.fwk.ACTIONS:
            cases=probe.cases(action)
            self.assertEqual(18,len(cases));self.assertEqual(18,len({c[0] for c in cases}))
            self.assertEqual({'Action','DemoId','RunToken'},{c[1] for c in cases})
            for field in ('Action','DemoId','RunToken'):
                self.assertTrue(any(f==field and value is None for _,f,value in cases))
                self.assertTrue(any(f==field and value is not None and len(value)>4000 and value.endswith('X') for _,f,value in cases))

    def test_raw_render_keeps_full_literals_and_null_without_unknown_fields(self):
        source=probe.fwk.SOURCE.read_text(encoding='utf-8-sig');raw='LOCAL'+' '*5000+'X'
        result=probe.render(source,'DROP',17,{'RunToken':raw,'DemoId':None})
        self.assertIn(probe.ownership.literal(raw),result)
        self.assertIn('DECLARE @DemoId nvarchar(max) = NULL;',result)
        with self.assertRaises(ValueError):probe.render(source,'DROP',17,{'Other':'synthetisch'})

    def test_exact_failure_prefixes_keep_free_diagnostic_pipes(self):
        text=record('DEMO_ID',tail='QRY-001X|STL|OPT|QRY|IDX|CON|RES|DGN-nnn|Diagnose')+record('DATABASE_NAME')+record('SUMMARY')+'PRESERVED\n'
        probe.require_preserved(text,'DEMO_ID')
        for bad in (text.replace('DEMO_ID','ACTION'),text.replace('FAIL_CONTRACT','FAIL_STATE'),text+record('OTHER'),text+'PRESERVED\n',text.replace('PRESERVED',''),text.replace('1|LIFECYCLE','x|LIFECYCLE'),text.replace('SUMMARY','DEMO_ID'),text+ 'EXTRA\n'):
            with self.subTest(bad=bad),self.assertRaises(RuntimeError):probe.require_preserved(bad,'DEMO_ID')

    def test_unexpected_execution_skip_and_warning_are_not_contract_success(self):
        base=record('ACTION')+record('DATABASE_NAME')+record('SUMMARY')
        for extra in (record('OTHER',code='FAIL_EXECUTION'),record('OTHER',code='FAIL_CLEANUP'),record('OTHER',code='SKIP_VERSION',outcome='SKIP'),record('OTHER',code='OTHER',outcome='FAIL'),record('OTHER',outcome='WARN')):
            with self.subTest(extra=extra),self.assertRaises(RuntimeError):probe.require_preserved(base+extra+'PRESERVED\n','ACTION')

    def test_known_safety_passes_and_strict_lifecycle_failure_binding(self):
        base=record('ACTION')+record('DATABASE_NAME')+record('SUMMARY')
        safety=record('LAB_CONFIRMATION',code='OK',outcome='PASS').replace('|LIFECYCLE|','|SAFETY|')
        safety+=record('DROP_CONFIRMATION',code='OK',outcome='PASS').replace('|LIFECYCLE|','|SAFETY|')
        probe.require_preserved(base+safety+'PRESERVED\n','ACTION')
        for bad in (base+safety.replace('|SAFETY|','|UNKNOWN|'),base+safety.replace('PASS|OK','FAIL|FAIL_CONTRACT'),base+safety.replace('LAB_CONFIRMATION','OTHER'),base.replace('|LIFECYCLE|ACTION','|SAFETY|ACTION')+safety,base.replace('|LIFECYCLE|SUMMARY','|SAFETY|SUMMARY')+safety,base+record('UNEXPECTED_CONTRACT'),base.replace(record('DATABASE_NAME'),'')):
            with self.subTest(bad=bad),self.assertRaises(RuntimeError):probe.require_preserved(bad+'PRESERVED\n','ACTION')

    def test_full_file_needs_contract_error_batch_stop_and_unchanged_state(self):
        for error in (ExecutionTargetError('Msg 51000'),ExecutionTargetError('Msg 51002'),ExecutionTargetError('Msg 51000 UNREACHED_BATCH'),None):
            with self.subTest(error=str(error)),patch.object(probe,'snapshot',return_value='same'),patch.object(probe,'run_sql',side_effect=error):
                if error and str(error)=='Msg 51000':probe.reject_file(self.target(),'synthetisch')
                else:
                    with self.assertRaises(RuntimeError):probe.reject_file(self.target(),'synthetisch')
        with patch.object(probe,'snapshot',side_effect=['before','after']),patch.object(probe,'run_sql',side_effect=ExecutionTargetError('Msg 51000')):
            with self.assertRaises(RuntimeError):probe.reject_file(self.target(),'synthetisch')

    def test_batch_requires_specific_record_and_rejects_go_before_sql(self):
        good=record('RUN_TOKEN')+record('DATABASE_NAME')+record('SUMMARY')+'PRESERVED\n'
        for output in (good,'PRESERVED\n'):
            with patch.object(probe,'run_sql',return_value=output):
                if output==good:probe.reject_batch(self.target(),'SELECT 1;','RUN_TOKEN')
                else:
                    with self.assertRaises(RuntimeError):probe.reject_batch(self.target(),'SELECT 1;','RUN_TOKEN')
        with patch.object(probe,'run_sql') as run:
            with self.assertRaises(RuntimeError):probe.reject_batch(self.target(),'SELECT 1;\nGO\n','ACTION')
            run.assert_not_called()

    def test_positive_executes_raw_values_without_rendering_them_again(self):
        text="DECLARE @Action nvarchar(max)=N' drop ';"
        good=record('OWNERSHIP_MARKERS',code='OK',outcome='PASS')+record('SUMMARY',code='OK',outcome='PASS')
        with patch.object(probe.fwk,'render',side_effect=AssertionError('Rohwerte erneut normalisiert')),patch.object(probe,'run_sql',return_value=good) as run:
            probe.positive(self.target(),text)
            self.assertEqual(text,run.call_args.kwargs['sql_text'])
        for bad in (good+record('SUMMARY',code='OK',outcome='PASS'),record('SUMMARY',code='OK',outcome='PASS'),good.replace('PASS','FAIL')):
            with patch.object(probe,'run_sql',return_value=bad),self.assertRaises(RuntimeError):probe.positive(self.target(),text)

    def test_both_harmful_counterprobes_require_exact_state_error_and_restoration(self):
        for error in (ExecutionTargetError('51994 INPUT_STATE_WAS_CHANGED'),ExecutionTargetError('51992 OTHER'),None):
            with patch.object(probe,'run_sql'),patch.object(probe,'snapshot',return_value='same'),patch.object(probe,'reject_batch',side_effect=error) as reject:
                if error and '51994' in str(error):probe.verify_oracles(self.target());self.assertEqual(2,reject.call_count)
                else:
                    with self.assertRaises(RuntimeError):probe.verify_oracles(self.target())
        with patch.object(probe,'run_sql'),patch.object(probe,'snapshot',side_effect=['before','after']),patch.object(probe,'reject_batch',side_effect=ExecutionTargetError('51994 INPUT_STATE_WAS_CHANGED')):
            with self.assertRaises(RuntimeError):probe.verify_oracles(self.target())

    def test_runtime_boundary_rejects_host_unknown_version_and_missing_repetition(self):
        for target,major,reps in ((SimpleNamespace(kind='host',container=None),17,2),(self.target(),14,2),(self.target(),17,1)):
            with patch.object(probe.fwk,'fixture') as fixture:
                with self.assertRaises(ValueError):probe.run_probes(target,major,repetitions=reps)
                fixture.assert_not_called()

    def test_public_matrix_requires_complete_count_and_propagates_failure(self):
        import run_framework_sql_matrix as matrix
        for result in (108,107,RuntimeError('synthetischer Fehler')):
            with patch.object(probe,'run_probes',side_effect=result if isinstance(result,Exception) else None,return_value=result),redirect_stdout(io.StringIO()) as output:
                if result==108:
                    matrix._test_lifecycle_inputs(container='synthetic-only',sqlcmd_path='/synthetic/sqlcmd',expected_major=17)
                    self.assertIn('negative=108',output.getvalue())
                else:
                    with self.assertRaises(matrix.MatrixFailure):matrix._test_lifecycle_inputs(container='synthetic-only',sqlcmd_path='/synthetic/sqlcmd',expected_major=17)


if __name__=='__main__':unittest.main()
