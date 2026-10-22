#!/usr/bin/env python3
"""Gegenproben für Setup-Batchgrenzen, vollständige Zustände und Fehlerklassifikation."""
from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Runtime'))
import setup_ownership as probe
from execution_target import ExecutionTargetError,docker_target

SOURCE="""/* synthetischer Einstieg */
USE [master];
GO
DECLARE @Value int=1;
GO
USE [$(TargetDatabase)];
GO
SELECT 'DATA_MODEL';
GO
"""


class SetupOwnershipTests(unittest.TestCase):
    def target(self):
        return docker_target(container='synthetic-only',sqlcmd_path='/synthetic/sqlcmd')

    def test_inventory_has_unique_actual_control_phases(self):
        self.assertEqual(10,len(set(probe.DEMO_IDS)))
        for demo in probe.DEMO_IDS:
            with self.subTest(demo=demo):
                source=probe.source_path(demo).read_text(encoding='utf-8-sig')
                phase=probe.control_phase(source)
                self.assertNotIn('$(',probe.ownership.render(phase,demo))

    def test_control_phase_preserves_guard_and_excludes_data_model(self):
        phase=probe.control_phase(SOURCE)
        self.assertIn('DECLARE @Value int=1;',phase)
        self.assertNotIn('DATA_MODEL',phase)
        self.assertNotIn('\nGO\n',phase)

    def test_unknown_go_or_entry_fails_before_sql(self):
        for source in (SOURCE.replace('GO\n','GO 2\n',1),SOURCE.replace('GO\n','GO -- Kommentar\n',1),SOURCE.replace('USE [master];','DROP DATABASE [synthetic]; USE [master];'),SOURCE.replace('USE [$(TargetDatabase)];','USE [synthetic];'),'USE [master];\nGO\nSELECT 1;'):
            with self.subTest(source=source),patch.object(probe,'run_sql') as run:
                with self.assertRaises(RuntimeError):probe.control_phase(source)
                run.assert_not_called()

    def test_snapshot_decoder_preserves_complete_binary_payload(self):
        value=bytes(range(100))+bytes(range(100))+b'\x00\xff'
        text='LENGTH|202\nBYTES|1|'+value[:100].hex().upper()+'\nBYTES|101|'+value[100:200].hex().upper()+'\nBYTES|201|00FF\n'
        self.assertEqual(value,probe.decode_snapshot(text))

    def test_snapshot_decoder_rejects_gaps_duplicates_truncation_and_extra(self):
        good='LENGTH|102\nBYTES|1|'+'41'*100+'\nBYTES|101|4243\n'
        cases=('', 'LENGTH|0\n','LENGTH|1048577\n',good.replace('101|','102|'),good.replace('4243','42'),good+'BYTES|103|44\n',good+'LENGTH|102\n',good.replace('BYTES|1|','BYTES|1|GG'),good.replace('41'*100,'41'*99),good.replace('BYTES|101|4243\n',''))
        for value in cases:
            with self.subTest(value=value):
                with self.assertRaises(RuntimeError):probe.decode_snapshot(value)

    def test_full_file_rejection_requires_specific_error_and_no_later_batch(self):
        cases=('Msg 51002 FAIL_STATE: Marker','Msg 51002 OTHER','Msg 51002 FAIL_STATE; Msg 51999 UNREACHED_BATCH','Msg 51000 FAIL_CONTRACT','')
        for value in cases:
            effect=ExecutionTargetError(value) if value else None
            with self.subTest(value=value),patch.object(probe,'run_sql',side_effect=effect):
                if value==cases[0]:probe.file_rejection(self.target(),'OPT-002',SOURCE)
                else:
                    with self.assertRaises(RuntimeError):probe.file_rejection(self.target(),'OPT-002',SOURCE)

    def test_batch_requires_exact_positive_preservation_record(self):
        for output in ('PRESERVED\n','','PRESERVED\nPRESERVED\n','OTHER\n'):
            with self.subTest(output=output),patch.object(probe,'run_sql',return_value=output):
                if output=='PRESERVED\n':probe.batch_rejection(self.target(),'OPT-002','SELECT 1;',{})
                else:
                    with self.assertRaises(RuntimeError):probe.batch_rejection(self.target(),'OPT-002','SELECT 1;',{})

    def test_batch_refuses_unparsed_separator_before_sql(self):
        with patch.object(probe,'run_sql') as run:
            with self.assertRaises(RuntimeError):probe.batch_rejection(self.target(),'OPT-002','SELECT 1;\nGO\nSELECT 2;',{})
            run.assert_not_called()

    def test_mutating_oracle_requires_both_specific_failures(self):
        for effect in (None,ExecutionTargetError('Msg 51994 SETUP_STATE_WAS_CHANGED'),ExecutionTargetError('Msg 51002 OTHER')):
            with self.subTest(effect=str(effect)),patch.object(probe,'run_sql',side_effect=['ORACLE_COMPLETE','','']),patch.object(probe,'batch_rejection',side_effect=effect) as batch:
                if effect and '51994' in str(effect):
                    probe.verify_oracles(self.target(),'OPT-002')
                    self.assertEqual(2,batch.call_count)
                else:
                    with self.assertRaises(RuntimeError):probe.verify_oracles(self.target(),'OPT-002')

    def test_invalid_selection_and_version_fail_before_fixture(self):
        for major,demos in ((14,('OPT-002',)),(17,()),(17,('UNKNOWN',)),(17,('OPT-002','OPT-002'))):
            with self.subTest(major=major,demos=demos),patch.object(probe,'fixture') as fixture:
                with self.assertRaises(ValueError):probe.run_probes(self.target(),major,demos=demos)
                fixture.assert_not_called()

    def test_unsupported_feature_skips_before_fixture(self):
        for major,demo in ((15,'OPT-009'),(15,'OPT-010'),(16,'OPT-010')):
            with self.subTest(major=major,demo=demo),patch.object(probe,'fixture') as fixture,patch.object(probe,'run_sql') as run,redirect_stdout(io.StringIO()) as output:
                self.assertEqual(0,probe.run_probes(self.target(),major,demos=(demo,)))
                self.assertIn('SKIP_VERSION',output.getvalue())
                fixture.assert_not_called();run.assert_not_called()

    def test_positive_setup_requires_unique_success_and_expected_config(self):
        for record in ('1|SETUP|SUMMARY|PASS|OK\n','','1|SETUP|SUMMARY|WARN|OK\n','1|SETUP|SUMMARY|PASS|OK\n1|SETUP|SUMMARY|PASS|OK\n'):
            with self.subTest(record=record),patch.object(probe,'run_sql',side_effect=[record,'MARKERS_VERIFIED']),patch.object(probe,'config_snapshot',return_value='7|SIMPLE|0|0|2|170'):
                if record=='1|SETUP|SUMMARY|PASS|OK\n':probe.positive(self.target(),'OPT-002',SOURCE,17)
                else:
                    with self.assertRaises(RuntimeError):probe.positive(self.target(),'OPT-002',SOURCE,17)
        with patch.object(probe,'run_sql',return_value='1|SETUP|SUMMARY|PASS|OK\n'),patch.object(probe,'config_snapshot',return_value='7|FULL|0|0|2|170'):
            with self.assertRaises(RuntimeError):probe.positive(self.target(),'OPT-002',SOURCE,17)
        for marker in ('','MARKERS_VERIFIED\nMARKERS_VERIFIED\n'):
            with self.subTest(marker=marker),patch.object(probe,'run_sql',side_effect=['1|SETUP|SUMMARY|PASS|OK\n',marker]),patch.object(probe,'config_snapshot',return_value='7|SIMPLE|0|0|2|170'):
                with self.assertRaises(RuntimeError):probe.positive(self.target(),'OPT-002',SOURCE,17)


if __name__=='__main__':unittest.main()
