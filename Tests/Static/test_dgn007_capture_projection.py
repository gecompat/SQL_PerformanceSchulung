#!/usr/bin/env python3
"""Tatsächliche Packager-/Decoder- und extrahierte SQL-Producerfixtures.

SQLite prüft portable SQL-Ausdrücke mit synthetischen Tabellen. T-SQL-JSON,
Style3 und UTC-Konvertierung benötigen zusätzlich echte SQL-Server-Runtime.
Prozessfixtures starten ausschließlich Python, keine SQL-/Docker-Ressourcen.
Es entstehen keine RunRecord-, Freeze- oder Incidentattestationen.
"""
from __future__ import annotations
from contextlib import closing,redirect_stdout,redirect_stderr
from copy import deepcopy
from dataclasses import replace
from datetime import date
from decimal import Decimal,localcontext
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import threading
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
for directory in (ROOT,ROOT/'Tests/Static',ROOT/'Tests/Runtime'):
    sys.path.insert(0,str(directory))
from Tests.Contracts import dgn007_capture_projection as projection
from Tests.Contracts import dgn007_collector_transport as transport
from Tests.Contracts import dgn007_prospective_acceptance as acceptance
from test_dgn007_collector_transport import payload,encode,MAX_TICKS
from validate_dgn007_prospective_acceptance import CONTRACT
import validate_dgn007_capture_projection as validator
import run_dgn007_automated_setup as runner


def project(value): return {k:v for k,v in value.items() if k not in ('schema','contract_digest','source_digest')}


def frames_from_text(text):
    total=(len(text)+ 511)//512
    return tuple(f'DGN007_CAPTURE_FRAME|1|{i+1}|{total}|{len(text)}|'+text[i*512:(i+1)*512] for i in range(total))


def frames(value): return frames_from_text(encode(project(value)))


def harness(frames,contract=runner.CONTROL_AB_CONTRACT,**changes):
    stdout='SQLPERF_SUMMARY|PASS|OK\n'+'\n'.join(f'{p}: PASS/OK (0.001s)' for p in contract.expected_phases)
    lines=[]
    for phase in contract.expected_phases:
        if phase=='CONTROL_EVIDENCE': lines.extend('[CONTROL_EVIDENCE:stderr] '+frame for frame in frames)
        lines.append(f'[{phase}:stderr] SQLPERF_SUMMARY|PASS|OK')
    return replace(runner.SqlcmdResult((),0,stdout,'\n'.join(lines),False,.001),**changes)


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.contract=acceptance.contract_from_mapping(json.loads(CONTRACT.read_text(encoding='utf-8')))
        self.value=payload(self.contract)

    def reject(self,stream,code='FAIL_CONTRACT'):
        with self.assertRaises(projection.ProjectionError) as caught:
            projection.decode_projection(stream,self.contract)
        self.assertEqual((str(caught.exception),caught.exception.code),(code,code))
        self.assertIsNone(caught.exception.__cause__);self.assertIsNone(caught.exception.__context__)

    def test_all_nine_major_scope_combinations_use_actual_decoder(self):
        for major in (15,16,17):
            for sequence in ('AB','BA','AA'):
                value=payload(self.contract,major,sequence)
                body=projection.decode_projection(frames(value),self.contract)
                direct=transport.decode_capture(encode(value),self.contract)
                self.assertEqual(body,direct)
                self.assertEqual(body.scope,'DGN-007_CONTROL_'+sequence)
                self.assertTrue(body.row_evidence_complete);self.assertFalse(body.runtime_attested)
                self.assertFalse(hasattr(body,'phases'));self.assertFalse(hasattr(body,'absence_code'))

    def test_nonfinal_full_chunks_and_exact_sixty_three_frame_payload_bound(self):
        text=encode(project(self.value))
        self.assertEqual((projection.MAX_CHUNK_CHARS,projection.MAX_PROJECTION_CHARS,
                          projection.MAX_FRAMES,projection.MAX_FRAME_CHARS),(512,32000,64,576))
        for length in (4096,4097,8192,8193,32000):
            padded=text[:-1]+' '*(length-len(text))+'}'
            if len(padded)!=length: continue
            stream=frames_from_text(padded)
            body=projection.decode_projection(stream,self.contract)
            self.assertEqual(len(stream),(length+ 511)//512)
            self.assertEqual(body.windows[0].avg_duration_us,Decimal('123.45678901234567'))
        self.assertEqual(len(stream),63)
        self.assertEqual([len(line.split('|',5)[5]) for line in stream],[512]*62+[256])
        self.reject(frames_from_text(text[:-1]+' '*(32001-len(text))+'}'))
        # 64 is only a defensive frame-count ceiling: no valid <=32000-byte
        # body can require 64 frames. Both inconsistent 64 and excess 65 fail.
        for count in (64,65):
            self.reject(tuple(f'DGN007_CAPTURE_FRAME|1|{i+1}|{count}|32000|'+
                              (stream[i].split('|',5)[5] if i<63 else '{}')
                              for i in range(count)))
        good=frames(self.value);first=good[0].split('|',5)
        for size in (511,513):
            changed=first.copy();changed[5]=first[5][:size] if size<512 else first[5]+' '
            self.reject(('|'.join(changed),*good[1:]))
        # Synthetic characterization of the observed 970-character received
        # line. Its declared full payload must never make truncation pass.
        header=f'DGN007_CAPTURE_FRAME|1|1|1|{len(text)}|'
        truncated=header+text[:970-len(header)]
        self.assertEqual(len(truncated),970);self.reject((truncated,))
        # Put a required space in the statement marker at a chunk boundary.
        # Preserved spaces decode; trimming that boundary fails before JSON.
        index=text.index('/* DGN007_CASE_SEARCH */')+2
        padded=text[:1]+' '*((511-index)%512)+text[1:]
        good=frames_from_text(padded)
        boundary=(index+(511-index)%512)//512
        self.assertTrue(good[boundary].endswith(' '))
        self.assertEqual(projection.decode_projection(good,self.contract),
                         transport.decode_capture(encode(self.value),self.contract))
        changed=list(good);changed[boundary]=changed[boundary][:-1]
        self.reject(tuple(changed))

    def test_truncated_duplicate_extra_reordered_unknown_frames_fail(self):
        text=encode(project(self.value));text=text[:-1]+' '*4500+'}'
        good=frames_from_text(text)
        bad=((),good[:-1],good+(good[-1],),good[::-1],(good[0],good[0]),
             (good[0][:-1],*good[1:]),('unknown'+good[0],*good[1:]),list(good))
        for stream in bad:
            with self.subTest(kind=type(stream).__name__): self.reject(stream)

    def test_frame_metadata_and_ascii_are_exact(self):
        good=frames(self.value)
        first=good[0];parts=first.split('|',5)
        for index,values in ((0,('UNKNOWN',)),(1,('0','2')),(2,('0','01','2')),(3,('0','9','01')),(4,('0','32001','01'))):
            for value in values:
                changed=parts.copy();changed[index]=value
                self.reject(('|'.join(changed),*good[1:]))
        for suffix in ('\n','\r','\x00','é','\ud800'):
            self.reject((first+suffix,*good[1:]))
        self.reject((first+'x'*9000,))

    def test_duplicate_json_unknown_fields_additional_document_and_missing_records(self):
        text=encode(project(self.value))
        for changed in ('{"major":15,'+text[1:],text+'{}',text.replace('"major":15','"major":15,"unknown":"synthetic-private"'),
                        text.replace('"window_id":0','"window_id":0,"window_id":0',1)):
            self.reject(frames_from_text(changed))
        for field in project(self.value):
            value=project(self.value);del value[field]
            self.reject(frames_from_text(encode(value)))
        for field in ('schema','contract_digest','source_digest','phases','absence_outcome','block'):
            value=project(self.value);value[field]='synthetic-private'
            self.reject(frames_from_text(encode(value)))

    def test_no_expected_rows_can_replace_measurement(self):
        for measured in (False,True):
            value=payload(self.contract,measured=measured)
            if measured:
                value['requests'][0]['returned_rows']=229
            else:
                self.assertFalse(transport.decode_capture(encode(value),self.contract).row_evidence_complete)
                self.assertIsNone(value['requests'][0]['returned_rows'])
            self.reject(frames(value),'FAIL_RESULT_CONTRACT')
        value=deepcopy(self.value);value['requests'][0]['returned_rows']=None
        self.reject(frames(value),'FAIL_CONTRACT')

    def test_precision_context_and_one_tick_exact(self):
        for metric in ('1.2345678901234567E+2','1.234567890123456789012345678901234E+3','1E-30','0E-30'):
            value=deepcopy(self.value);value['windows'][0]['avg_duration_us']=metric
            for precision in (2,50):
                with localcontext() as context:
                    context.prec=precision;before=(context.prec,dict(context.flags))
                    body=projection.decode_projection(frames(value),self.contract)
                    self.assertEqual(body.windows[0].avg_duration_us.as_tuple(),Decimal(metric).as_tuple())
                    self.assertEqual((context.prec,dict(context.flags)),before)
        value=deepcopy(self.value)
        value['windows'][0]['execution_started_ticks']+=1;value['plans'][0]['first_execution_ticks']+=1
        body=projection.decode_projection(frames(value),self.contract)
        self.assertEqual(body.plans[0].first_execution_ticks,1101)
        offset=MAX_TICKS-3000
        for w in value['windows']:
            for key in ('interval_start_ticks','interval_end_ticks','execution_started_ticks','execution_finished_ticks'):w[key]+=offset
        for p in value['plans']:
            for key in ('first_execution_ticks','last_execution_ticks'):p[key]+=offset
        self.assertEqual(projection.decode_projection(frames(value),self.contract).windows[1].interval_end_ticks,MAX_TICKS)
        value['windows'][1]['interval_end_ticks']+=1
        self.reject(frames(value),'FAIL_RESULT_CONTRACT')

    def test_decoder_rejects_metrics_hash_family_request_union_bindings(self):
        mutations=(('windows',0,'avg_duration_us','NaN'),('windows',0,'avg_cpu_us','-1'),
                   ('plans',0,'query_plan_hash','0x0102030405060708'),('plans',0,'query_id',999),
                   ('families',0,'parent_object_id',999),('requests',0,'ordinal',2),
                   ('plan_union',0,'executed_in_t1',1),('windows',0,'execution_count',3))
        for collection,index,key,value in mutations:
            changed=deepcopy(self.value);changed[collection][index][key]=value
            self.reject(frames(changed),'FAIL_RESULT_CONTRACT')

    def test_packager_is_pure_and_errors_have_no_raw_values(self):
        with patch('builtins.open',side_effect=AssertionError('I/O')),redirect_stdout(io.StringIO()) as out,redirect_stderr(io.StringIO()) as err:
            projection.decode_projection(frames(self.value),self.contract)
            self.reject(frames_from_text('{"private":"synthetic-private"}'))
        self.assertEqual(out.getvalue()+err.getvalue(),'')
        self.assertEqual(validator.pure_findings(validator.MODULE.read_text(encoding='utf-8')),[])
        source=validator.MODULE.read_text(encoding='utf-8')
        self.assertEqual(validator.frame_contract_findings(source),[])
        for before,after in (('MAX_CHUNK_CHARS = 512','MAX_CHUNK_CHARS = 513'),
                             ('MAX_PROJECTION_CHARS = 32000','MAX_PROJECTION_CHARS = 32001'),
                             ('MAX_FRAMES = 64','MAX_FRAMES = 65'),
                             ('MAX_CHUNK_CHARS + 64','MAX_CHUNK_CHARS + 65')):
            self.assertTrue(validator.frame_contract_findings(source.replace(before,after)),before)

    def test_harness_binds_all_summaries_and_exact_evidence_stderr(self):
        result=harness(frames(self.value))
        self.assertEqual(runner.check_capture(result,contract=runner.CONTROL_AB_CONTRACT,expected_major=15,expected_contract=self.contract),(2,8,1,2,2))
        for changed in (result.stderr.replace('CONTROL_EVIDENCE:stderr','CONTROL_EVIDENCE:stdout'),
                        result.stderr.replace('CONTROL_EVIDENCE:stderr] DGN007_CAPTURE','PROFILE_COMPARISON:stderr] DGN007_CAPTURE'),
                        result.stderr+'\n[UNKNOWN:stderr] SQLPERF_SUMMARY|PASS|OK',
                        result.stderr.replace('[CONTROL_EVIDENCE:stderr] SQLPERF_SUMMARY|PASS|OK',''),
                        result.stderr+'\n[CONTROL_EVIDENCE:stderr] '+frames(self.value)[0]):
            with self.assertRaisesRegex(runner.RunnerFailure,'FAIL_CONTRACT'):
                runner.check_capture(replace(result,stderr=changed),contract=runner.CONTROL_AB_CONTRACT,expected_major=15,expected_contract=self.contract)
        for major,contract in ((17,runner.CONTROL_AB_CONTRACT),(15,runner.CONTROL_BA_CONTRACT)):
            result=harness(frames(self.value),contract)
            with self.assertRaisesRegex(runner.RunnerFailure,'FAIL_RESULT_CONTRACT'):
                runner.check_capture(result,contract=contract,expected_major=major,expected_contract=self.contract)

    def test_foreign_line_partial_frame_and_skip_warn_fail(self):
        good=harness(frames(self.value))
        prefix='[CONTROL_EVIDENCE:stderr] '
        for changed in (good.stderr.replace(prefix+'SQLPERF_SUMMARY',prefix+'foreign\n'+prefix+'SQLPERF_SUMMARY'),
                        good.stderr.replace(frames(self.value)[0],frames(self.value)[0][:-1]),
                        good.stderr.replace('SQLPERF_SUMMARY|PASS|OK','SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING',1),
                        good.stderr.replace('SQLPERF_SUMMARY|PASS|OK','SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE',1)):
            with self.assertRaisesRegex(runner.RunnerFailure,'FAIL_CONTRACT'):
                runner.check_capture(replace(good,stderr=changed),contract=runner.CONTROL_AB_CONTRACT,expected_major=15,expected_contract=self.contract)
        # Ein Label allein darf den tatsächlichen Harness-Pipekanal nicht fälschen.
        spoof=replace(good,stdout=good.stdout+'\n'+good.stderr,stderr='')
        with self.assertRaisesRegex(runner.RunnerFailure,'FAIL_CONTRACT'):
            runner.check_capture(spoof,contract=runner.CONTROL_AB_CONTRACT,expected_major=15,expected_contract=self.contract)

    def test_cleanup_timeout_and_limit_priority_are_structured(self):
        good=harness(frames(self.value))
        for marker,code in (('[CLEANUP:stderr] SQLPERF_SUMMARY|FAIL|FAIL_CLEANUP','FAIL_CLEANUP'),
                            ('[CONTROL_WINDOWS:stderr] SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT','FAIL_TIMEOUT'),
                            ('not_a_status FAIL_TIMEOUT','FAIL_CONTRACT'),('[UNKNOWN:stderr] SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT','FAIL_CONTRACT')):
            result=replace(good,stderr=marker+'\n'+'x'*300000)
            with self.assertRaisesRegex(runner.RunnerFailure,code):
                runner.check_capture(result,contract=runner.CONTROL_AB_CONTRACT,expected_major=15,expected_contract=self.contract)
        result=replace(good,stdout=good.stdout.replace('CLEANUP: PASS/OK','CLEANUP: FAIL/FAIL_CLEANUP'),stderr=good.stderr.replace('[CONTROL_WINDOWS:stderr] SQLPERF_SUMMARY|PASS|OK','[CONTROL_WINDOWS:stderr] SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'))
        with self.assertRaisesRegex(runner.RunnerFailure,'FAIL_CLEANUP'):
            runner.check_capture(result,contract=runner.CONTROL_AB_CONTRACT,expected_major=15,expected_contract=self.contract)

    def test_failure_diagnostics_bind_known_outer_and_sql_status_without_raw_text(self):
        stdout='SQLPERF_SUMMARY|FAIL|FAIL_EXECUTION\nCONTROL_WINDOWS: FAIL/FAIL_EXECUTION (1.000s) - synthetic-private'
        stderr='\n'.join((
            '[CONTROL_WINDOWS:stderr] Msg 51002, Level 16, State 1, Server synthetic-private, Line 391',
            '[CONTROL_WINDOWS:stderr] SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT',
            '[CONTROL_WINDOWS:stderr] synthetic-private SELECT secret FROM synthetic_connection',
            '[UNKNOWN:stderr] Msg 51001, Level 16, State 1, Line 999',
            '[CONTROL_WINDOWS:stdout] Msg 51002, Level 16, State 1, Line 999',
            '[SETUP:stderr] Msg 51002, Level 16, State 1, Line 999'))
        result=replace(harness(()),returncode=1,stdout=stdout,stderr=stderr)
        self.assertEqual(runner.capture_failure_diagnostics(result,contract=runner.CONTROL_AB_CONTRACT),(
            'DGN007_FAILURE|OUTER_SUMMARY|FAIL|FAIL_EXECUTION',
            'DGN007_FAILURE|OUTER_PHASE|CONTROL_WINDOWS|FAIL|FAIL_EXECUTION',
            'DGN007_FAILURE|SQL_MESSAGE|CONTROL_WINDOWS|msg=51002; line=391',
            'DGN007_FAILURE|SQL_STATUS|CONTROL_WINDOWS|FAIL|FAIL_RESULT_CONTRACT'))
        self.assertEqual(runner.capture_failure_diagnostics(result,contract=runner.DATA_MODEL_CONTRACT),(
            'DGN007_FAILURE|OUTER_SUMMARY|FAIL|FAIL_EXECUTION',))
        good=harness(frames(self.value))
        self.assertEqual(runner.capture_failure_diagnostics(replace(good,stderr=stderr),contract=runner.CONTROL_AB_CONTRACT),())

    def test_failure_diagnostics_reject_unknown_malformed_numbers_and_bound_output(self):
        stdout='CONTROL_WINDOWS: FAIL/FAIL_EXECUTION (1.000s) - synthetic-private'
        ignored=('Msg 0, Level 16, State 1, Line 1','Msg 2147483648, Level 16, State 1, Line 1',
                 'Msg 51002, Level 26, State 1, Line 1','Msg 51002, Level 16, State 256, Line 1',
                 'Msg 51002, Level 16, State 1, Line 0','Msg 51002, Level 16, State 1, Line 1000001',
                 'Msg 51002, Level 16, State 1, Line 1 synthetic-private',
                 'prefix Msg 51002, Level 16, State 1, Line 1','SQLPERF_SUMMARY|FAIL|FAIL_SYNTHETIC_PRIVATE')
        stderr='\n'.join('[CONTROL_WINDOWS:stderr] '+line for line in ignored)
        result=replace(harness(()),returncode=1,stdout=stdout,stderr=stderr)
        expected=('DGN007_FAILURE|OUTER_PHASE|CONTROL_WINDOWS|FAIL|FAIL_EXECUTION',)
        self.assertEqual(runner.capture_failure_diagnostics(result,contract=runner.CONTROL_AB_CONTRACT),expected)
        for line in ('UNKNOWN: FAIL/FAIL_EXECUTION (1.000s) - synthetic-private',
                     'CONTROL_WINDOWS: FAIL/FAIL_SYNTHETIC_PRIVATE (1.000s) - synthetic-private',
                     'prefix '+stdout,stdout+'\nSQLPERF_SUMMARY|FAIL|FAIL_SYNTHETIC_PRIVATE'):
            diagnostics=runner.capture_failure_diagnostics(replace(result,stdout=line),contract=runner.CONTROL_AB_CONTRACT)
            self.assertNotIn('synthetic-private',' '.join(diagnostics))
            self.assertNotIn('FAIL_SYNTHETIC_PRIVATE',' '.join(diagnostics))
        stderr='\n'.join(f'[CONTROL_WINDOWS:stderr] Msg 51002, Level 16, State 1, Line {i}' for i in range(1,100))
        diagnostics=runner.capture_failure_diagnostics(replace(result,stderr=stderr),contract=runner.CONTROL_AB_CONTRACT)
        self.assertEqual(len(diagnostics),24)
        self.assertEqual(len(set(diagnostics)),24)
        self.assertEqual(runner.capture_failure_diagnostics(replace(result,stderr='x'*300000),contract=runner.CONTROL_AB_CONTRACT),())

    def test_failure_diagnostics_do_not_change_cleanup_timeout_or_decode_outcomes(self):
        target=runner.execution_target.docker_target(container='synthetic-test',sqlcmd_path='/opt/mssql-tools18/bin/sqlcmd')
        for source_code,absent_failure,expected in (
                ('FAIL_EXECUTION',None,'FAIL_EXECUTION'),
                ('FAIL_TIMEOUT',None,'FAIL_TIMEOUT'),
                ('FAIL_TIMEOUT',runner.RunnerFailure('FAIL_CLEANUP'),'FAIL_CLEANUP')):
            result=replace(harness(()),returncode=1,
                stdout=f'SQLPERF_SUMMARY|FAIL|{source_code}\nCONTROL_WINDOWS: FAIL/{source_code} (1.000s) - synthetic-private\nCLEANUP: PASS/OK (0.001s) - done',
                stderr='[CONTROL_WINDOWS:stderr] Msg 51002, Level 16, State 1, Line 391')
            with patch.object(runner,'run_harness',return_value=result),patch.object(runner,'assert_absent',side_effect=absent_failure) as absent,patch.object(runner,'recover'),redirect_stdout(io.StringIO()) as out:
                with self.assertRaisesRegex(runner.RunnerFailure,expected):
                    runner.run_one(target,1,contract=runner.CONTROL_AB_CONTRACT,check_capture_projection=True,expected_major=15,expected_contract=self.contract)
                self.assertGreaterEqual(absent.call_count,1)
                self.assertIn('DGN007_FAILURE|OUTER_PHASE|CONTROL_WINDOWS|FAIL|'+source_code,out.getvalue())
                self.assertIn('DGN007_STAGE|DGN-007_CONTROL_AB|RUN_1|FAIL|'+expected,out.getvalue())
                self.assertNotIn('synthetic-private',out.getvalue())
        # A passing harness with a malformed body has no failed-harness log.
        with patch.object(runner,'run_harness',return_value=harness(())),patch.object(runner,'assert_absent'),redirect_stdout(io.StringIO()) as out:
            with self.assertRaisesRegex(runner.RunnerFailure,'FAIL_CONTRACT'):
                runner.run_one(target,1,contract=runner.CONTROL_AB_CONTRACT,check_capture_projection=True,expected_major=15,expected_contract=self.contract)
            self.assertNotIn('DGN007_FAILURE',out.getvalue())

    def test_guard_diagnostics_all_seventeen_ids_and_failure_priorities(self):
        stdout='SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT\nCONTROL_EVIDENCE: FAIL/FAIL_RESULT_CONTRACT (1.000s) - synthetic-private'
        for number in range(1,18):
            guard=f'G{number:02}'
            stderr=f'[CONTROL_EVIDENCE:stderr] DGN007_CONTROL_GUARD|{guard}\n[CONTROL_EVIDENCE:stderr] \n[CONTROL_EVIDENCE:stderr] SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'
            result=replace(harness(()),returncode=1,stdout=stdout,stderr=stderr)
            diagnostics=runner.capture_failure_diagnostics(result,contract=runner.CONTROL_AB_CONTRACT)
            self.assertIn('DGN007_FAILURE|SQL_GUARD|CONTROL_EVIDENCE|'+guard,diagnostics)
            self.assertNotIn('synthetic-private',' '.join(diagnostics))
        target=runner.execution_target.docker_target(container='synthetic-test',sqlcmd_path='/opt/mssql-tools18/bin/sqlcmd')
        for suffix,expected in (('', 'FAIL_EXECUTION'),('\nCLEANUP: FAIL/FAIL_CLEANUP (1.000s) - ignored','FAIL_CLEANUP'),
                                ('\nSQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT','FAIL_TIMEOUT')):
            with patch.object(runner,'run_harness',return_value=replace(result,stdout=stdout+suffix)),patch.object(runner,'assert_absent') as absent,redirect_stdout(io.StringIO()) as out:
                with self.assertRaisesRegex(runner.RunnerFailure,expected):
                    runner.run_one(target,1,contract=runner.CONTROL_AB_CONTRACT,check_capture_projection=True,expected_major=15,expected_contract=self.contract)
                absent.assert_called_once()
                self.assertIn('DGN007_FAILURE|SQL_GUARD|CONTROL_EVIDENCE|G17',out.getvalue())
                self.assertIn('DGN007_STAGE|DGN-007_CONTROL_AB|RUN_1|FAIL|'+expected,out.getvalue())

    def test_guard_diagnostics_reject_unknown_duplicate_malformed_and_unbound_ids(self):
        stdout='CONTROL_EVIDENCE: FAIL/FAIL_RESULT_CONTRACT (1.000s) - synthetic-private'
        guard='[CONTROL_EVIDENCE:stderr] DGN007_CONTROL_GUARD|G01'
        summary='[CONTROL_EVIDENCE:stderr] SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'
        good=guard+'\n'+summary
        bad=(good.replace('|G01','|G00'),good.replace('|G01','|G18'),good.replace('|G01','|G1'),
             good.replace('|G01','|G01|synthetic-private'),good.replace('DGN007_CONTROL_GUARD','prefix DGN007_CONTROL_GUARD'),
             good.replace('CONTROL_EVIDENCE:stderr','SETUP:stderr'),good.replace('CONTROL_EVIDENCE:stderr','CONTROL_EVIDENCE:stdout'),
             guard,summary+'\n'+guard,guard+'\n[CONTROL_EVIDENCE:stderr] foreign\n'+summary,
             good.replace('|FAIL|FAIL_RESULT_CONTRACT','|PASS|OK'),good.replace('|FAIL|FAIL_RESULT_CONTRACT','|FAIL|FAIL_TIMEOUT'),
             guard+'\n'+good,guard.replace('|G01','|G18')+'\n'+good,
             '[UNKNOWN:stderr] DGN007_CONTROL_GUARD|G01\n'+good,
             'DGN007_CONTROL_GUARD|G01\n'+good,
             '[CONTROL_EVIDENCE:stderr] prefix DGN007_CONTROL_GUARD|G01\n'+good,
             '[CONTROL_EVIDENCE:stderr] '+'x'*9000+'\n'+good)
        for stderr in bad:
            result=replace(harness(()),returncode=1,stdout=stdout,stderr=stderr)
            self.assertFalse(any('|SQL_GUARD|' in line for line in runner.capture_failure_diagnostics(result,contract=runner.CONTROL_AB_CONTRACT)))
        for changed in ('CONTROL_WINDOWS: FAIL/FAIL_RESULT_CONTRACT (1.000s) - ignored',
                        'CONTROL_EVIDENCE: WARN/WARN_EMPIRICAL_VARIANCE (1.000s) - ignored',
                        'CONTROL_EVIDENCE: SKIP/SKIP_EVIDENCE_MISSING (1.000s) - ignored',
                        harness(()).stdout):
            result=replace(harness(()),returncode=1,stdout=changed,stderr=good)
            self.assertFalse(any('|SQL_GUARD|' in line for line in runner.capture_failure_diagnostics(result,contract=runner.CONTROL_AB_CONTRACT)))
        spoof=replace(harness(()),returncode=1,stdout=stdout+'\n'+good,stderr='')
        self.assertFalse(any('|SQL_GUARD|' in line for line in runner.capture_failure_diagnostics(spoof,contract=runner.CONTROL_AB_CONTRACT)))
        duplicate=replace(spoof,stderr=good)
        self.assertFalse(any('|SQL_GUARD|' in line for line in runner.capture_failure_diagnostics(duplicate,contract=runner.CONTROL_AB_CONTRACT)))

    def test_option_only_controls_before_connection_and_private_child_command(self):
        base=['--container','synthetic-test','--expected-major','15','--confirm-disposable-instance','--check-capture-projection']
        with patch.dict(os.environ,{'SQLCMDPASSWORD':'synthetic-test-value'}),patch.object(runner,'resolve_target') as connect,redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(base),1);connect.assert_not_called()
        target=runner.execution_target.docker_target(container='synthetic-test',sqlcmd_path='/opt/mssql-tools18/bin/sqlcmd')
        for contract in (runner.CONTROL_AB_CONTRACT,runner.CONTROL_BA_CONTRACT,runner.CONTROL_AA_CONTRACT):
            with patch.object(runner,'start_sqlcmd') as start,patch.object(runner,'collect_capture_process',return_value=harness(frames(self.value),contract)):
                runner.run_harness(target,contract=contract,check_capture_projection=True)
                command=start.call_args.args[0]
                self.assertEqual(command[:2],[sys.executable,'-u']);self.assertEqual(command.count('--show-output'),1)
                self.assertNotIn('-P',command);self.assertNotIn('synthetic-test-value',command)

    def test_capture_failure_still_checks_absence_and_cleanup_dominates(self):
        target=runner.execution_target.docker_target(container='synthetic-test',sqlcmd_path='/opt/mssql-tools18/bin/sqlcmd')
        for absent_failure,code in ((None,'FAIL_CONTRACT'),(runner.RunnerFailure('FAIL_CLEANUP'),'FAIL_CLEANUP')):
            with patch.object(runner,'run_harness',return_value=harness(())),patch.object(runner,'assert_absent',side_effect=absent_failure) as absent,patch.object(runner,'recover'),redirect_stdout(io.StringIO()) as output:
                with self.assertRaisesRegex(runner.RunnerFailure,code):
                    runner.run_one(target,1,contract=runner.CONTROL_AB_CONTRACT,check_capture_projection=True,expected_major=15,expected_contract=self.contract)
                self.assertGreaterEqual(absent.call_count,1)
                self.assertNotIn('DGN007_CAPTURE_FRAME',output.getvalue())

    def test_cli_controls_two_real_dispatches_each_with_expected_body_binding(self):
        target=runner.execution_target.docker_target(container='synthetic-test',sqlcmd_path='/opt/mssql-tools18/bin/sqlcmd')
        for sequence in ('AB','BA','AA'):
            contract=runner.scope_contract('control-'+sequence.lower())
            result=harness(frames(payload(self.contract,15,sequence)),contract)
            args=['--container','synthetic-test','--expected-major','15','--scope','control-'+sequence.lower(),
                  '--confirm-disposable-instance','--check-capture-projection']
            with patch.dict(os.environ,{'SQLCMDPASSWORD':'synthetic-test-value'}),patch.object(runner,'resolve_target',return_value=target),patch.object(runner.execution_target,'verify_engine'),patch.object(runner,'assert_empty_instance'),patch.object(runner,'run_harness',return_value=result) as process,patch.object(runner,'assert_absent') as absent,redirect_stdout(io.StringIO()) as output:
                self.assertEqual(runner.main(args),0)
                self.assertEqual(process.call_count,2);self.assertEqual(absent.call_count,2)
                self.assertTrue(all(call.kwargs==dict(contract=contract,check_capture_projection=True) for call in process.call_args_list))
                self.assertEqual(output.getvalue().count('DGN007_CAPTURE|'),2)
                for forbidden in ('DGN007_CAPTURE_FRAME','DGN007_FAILURE','synthetic-test-value','query_plan_hash','FAIL','RunRecord'):
                    self.assertNotIn(forbidden,output.getvalue())

    def test_malformed_expected_contract_is_rejected_before_connection(self):
        args=['--container','synthetic-test','--expected-major','15','--scope','control-ab',
              '--confirm-disposable-instance','--check-capture-projection']
        with patch.dict(os.environ,{'SQLCMDPASSWORD':'synthetic-test-value'}),patch.object(runner,'contract_from_mapping',side_effect=ValueError('synthetic-private')),patch.object(runner,'resolve_target') as connect,redirect_stdout(io.StringIO()) as output:
            self.assertEqual(runner.main(args),1);connect.assert_not_called()
            self.assertIn('FAIL|FAIL_CONTRACT',output.getvalue());self.assertNotIn('synthetic-private',output.getvalue())

    def test_private_python_process_capture_and_byte_limits(self):
        command=[sys.executable,'-u','-c',"import sys;print('synthetic');print('stderr',file=sys.stderr)"]
        result=runner.collect_capture_process(runner.start_sqlcmd(command),command)
        self.assertEqual((result.returncode,result.stdout,result.stderr),(0,'synthetic\n','stderr\n'))
        for status,code in (('not_a_status FAIL_TIMEOUT','FAIL_CONTRACT'),('[CLEANUP:stderr] SQLPERF_SUMMARY|FAIL|FAIL_CLEANUP','FAIL_CLEANUP'),('[CONTROL_WINDOWS:stderr] SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT','FAIL_TIMEOUT')):
            command=[sys.executable,'-u','-c',f"import sys,time;print({status!r},file=sys.stderr,flush=True);time.sleep(.1);print('é'*300,flush=True);time.sleep(1)"]
            with patch.object(runner,'MAX_CAPTURE_OUTPUT_BYTES',400),self.assertRaisesRegex(runner.RunnerFailure,code):
                runner.collect_capture_process(runner.start_sqlcmd(command),command)

    @unittest.skipUnless(sys.platform.startswith('linux'),'Linux-spezifische eigene Kindsession')
    def test_exit_before_eof_ends_own_readers_without_reused_pid_target(self):
        before={t.ident for t in threading.enumerate()}
        command=[sys.executable,'-u','-c',"import subprocess,sys,time; subprocess.Popen([sys.executable,'-c','import os,time;os.setsid();time.sleep(30)']);time.sleep(.3)"]
        with self.assertRaisesRegex(runner.RunnerFailure,'FAIL_CONTRACT'):
            runner.collect_capture_process(runner.start_sqlcmd(command),command)
        self.assertEqual({t.ident for t in threading.enumerate()},before)


# Ausschließlich syntaktische Portierung von COUNT_BIG/SELECT INTO und Namen.
def portable(sql): return sql.replace('COUNT_BIG(','COUNT(').replace('lab.','lab_').replace('dbo.','dbo_').replace('#','tmp_')


def create_as(connection,statement):
    match=re.search(r'\bINTO (tmp_\w+)',statement)
    connection.execute('CREATE TEMP TABLE '+match[1]+' AS '+statement[:match.start()]+statement[match.end():])


def guard(sql): return portable(re.split(r'\bBEGIN\b',sql,maxsplit=1)[0].strip()[3:])


class ExtractedSqlTests(unittest.TestCase):
    def setUp(self):
        self.windows=validator.WINDOWS.read_text(encoding='utf-8')
        self.evidence=validator.EVIDENCE.read_text(encoding='utf-8')
        self.connection=sqlite3.connect(':memory:');self.addCleanup(self.connection.close)

    def test_guard_literal_canonicalization_is_exact_and_preserves_predicate_failures(self):
        canonical=validator.canonical_guard_diagnostics(self.evidence)
        self.assertNotIn('DGN007_CONTROL_GUARD',canonical)
        self.assertEqual(canonical.count("PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;"),17)
        first="PRINT 'DGN007_CONTROL_GUARD|G01';"
        second="PRINT 'DGN007_CONTROL_GUARD|G02';"
        for changed in (self.evidence.replace(first,''),self.evidence.replace(first,second),
                        self.evidence.replace(first,first+'\n'+first),self.evidence.replace(first,"PRINT @Guard;"),
                        self.evidence.replace(first,first.replace('G01','G18')),
                        self.evidence.replace(first,'')+'\n'+first,
                        self.evidence.replace("PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;",
                                              "PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT';",1)):
            with self.assertRaisesRegex(ValueError,'^FAIL_CONTRACT$'):
                validator.canonical_guard_diagnostics(changed)
        changed=self.evidence.replace('p.FirstExecutionTime<w.ExecutionStarted','1=0')
        with self.assertRaisesRegex(ValueError,'^FAIL_CONTRACT$'):
            validator.canonical_guard_diagnostics(changed)
        self.assertTrue(validator.projection_sql_findings(changed))

    def test_g13_raw_diagnostic_strip_is_exact(self):
        sql = self.evidence
        self.assertEqual(validator.strip_g13_raw_diagnostic(sql, check_baseline=True).count('DGN007_G13_RAW'), 0)
        for changed in (sql.replace('TOP(17)', 'TOP(18)', 1),
                        sql.replace('/* G13_RAW_DIAGNOSTIC_END */', ''),
                        sql.replace("PRINT 'DGN007_CONTROL_GUARD|G13';", "PRINT 'DGN007_CONTROL_GUARD|G12';")):
            self.assertTrue(validator.projection_sql_findings(changed))

    def test_actual_measurement_select_guard_and_insert_use_actual_rows(self):
        sql=validator.capture_section(self.windows,'REQUEST_MEASUREMENT')
        self.connection.executescript('CREATE TABLE tmp_Actual(ItemId int);CREATE TABLE lab_RequestResultCapture(WindowId int,Ordinal int,RequestLogId int,ReturnedRows int);')
        query=re.search(r'SELECT @MeasuredReturnedRows=(.*?);',sql,re.S)[1]
        predicate=re.search(r'IF (.*?)\bBEGIN',sql,re.S)[1]
        insertion=re.search(r'INSERT lab.RequestResultCapture.*?;',sql,re.S)[0]
        for actual,expected,fail in ((228,228,False),(0,228,True),(227,228,True),(229,228,True)):
            self.connection.execute('DELETE FROM tmp_Actual')
            self.connection.executemany('INSERT INTO tmp_Actual VALUES(?)',((n,) for n in range(actual)))
            measured=self.connection.execute('SELECT '+portable(query)).fetchone()[0]
            bindings=dict(MeasuredReturnedRows=measured,ExpectedCount=expected,WindowId=0,Sequence=1,LastRequestId=5)
            self.assertEqual(bool(self.connection.execute('SELECT '+predicate,bindings).fetchone()[0]),fail)
            if not fail:
                self.connection.execute(portable(insertion).replace('INSERT lab_','INSERT INTO lab_'),bindings)
        self.assertEqual(self.connection.execute('SELECT ReturnedRows FROM lab_RequestResultCapture').fetchall(),[(228,)])
        bindings['MeasuredReturnedRows']=None
        self.assertTrue(self.connection.execute('SELECT '+predicate,bindings).fetchone()[0])

    def request_fixture(self):
        self.connection.executescript('CREATE TABLE lab_IncidentState(WindowId int,FirstRequestLogId int,LastRequestLogId int);CREATE TABLE dbo_CaseRequestLog(RequestLogId int,GroupKey int,StatusCode int);CREATE TABLE lab_RequestResultCapture(WindowId int,Ordinal int,RequestLogId int,ReturnedRows int);CREATE TABLE tmp_Parameters(WindowId int,Sequence int,GroupKey int,StatusCode int,ExpectedCount int);')
        contract=acceptance.contract_from_mapping(json.loads(CONTRACT.read_text(encoding='utf-8')))
        data=payload(contract)
        for w in data['windows']:self.connection.execute('INSERT INTO lab_IncidentState VALUES(?,?,?)',(w['window_id'],w['first_request_log_id'],w['last_request_log_id']))
        for r in data['requests']:
            self.connection.execute('INSERT INTO dbo_CaseRequestLog VALUES(?,?,?)',(r['request_log_id'],r['group_key'],r['status_code']))
            self.connection.execute('INSERT INTO lab_RequestResultCapture VALUES(?,?,?,?)',(r['window_id'],r['ordinal'],r['request_log_id'],r['returned_rows']))
            self.connection.execute('INSERT INTO tmp_Parameters VALUES(?,?,?,?,?)',(r['window_id'],r['ordinal'],r['group_key'],r['status_code'],r['returned_rows']))

    def rebuild_requests(self):
        self.connection.execute('DROP TABLE IF EXISTS tmp_CaptureRequestSource');self.connection.execute('DROP TABLE IF EXISTS tmp_CaptureRequests')
        for statement in portable(validator.capture_section(self.evidence,'REQUEST_ROWS')).split(';'):
            if statement.strip():create_as(self.connection,statement.strip())

    def test_actual_request_join_rejects_missing_foreign_and_extra_measurements(self):
        self.request_fixture();self.rebuild_requests()
        predicate=guard(validator.capture_section(self.evidence,'REQUEST_GUARD'))
        self.assertFalse(self.connection.execute('SELECT '+predicate).fetchone()[0])
        rows=self.connection.execute('SELECT ReturnedRows FROM tmp_CaptureRequests ORDER BY WindowId,Ordinal').fetchall()
        self.assertEqual(rows,[(228,),(2286,),(1144,),(571,),(2286,),(228,),(1144,),(571,)])
        for mutation in ('DELETE FROM lab_RequestResultCapture WHERE RequestLogId=5','UPDATE lab_RequestResultCapture SET RequestLogId=999 WHERE RequestLogId=5','UPDATE lab_RequestResultCapture SET ReturnedRows=NULL WHERE RequestLogId=5','INSERT INTO lab_RequestResultCapture VALUES(0,1,5,228)','UPDATE lab_RequestResultCapture SET ReturnedRows=229 WHERE RequestLogId=5'):
            self.connection.execute('SAVEPOINT fixture');self.connection.execute(mutation);self.rebuild_requests()
            self.assertTrue(self.connection.execute('SELECT '+predicate).fetchone()[0],mutation)
            self.connection.execute('ROLLBACK TO fixture');self.connection.execute('RELEASE fixture')

    def test_actual_families_include_executed_variant_and_self_parent_only(self):
        self.connection.executescript('CREATE TABLE tmp_ScopedQueries(QueryId int,ParentQueryId int);CREATE TABLE lab_IncidentProfile(QueryId int,ParentQueryId int);INSERT INTO tmp_ScopedQueries VALUES(10,10),(11,10),(12,10),(99,99);INSERT INTO lab_IncidentProfile VALUES(11,10);')
        create_as(self.connection,portable(validator.capture_section(self.evidence,'FAMILY_ROWS')).rstrip(';'))
        self.assertEqual(self.connection.execute('SELECT * FROM tmp_CaptureFamilies ORDER BY QueryId').fetchall(),[(10,10),(11,10)])

    def test_actual_execution_boundary_predicate_is_inclusive(self):
        self.connection.executescript('CREATE TABLE lab_IncidentState(WindowId int,ExecutionStarted int,ExecutionFinished int);CREATE TABLE lab_IncidentProfile(WindowId int,FirstExecutionTime int,LastExecutionTime int);INSERT INTO lab_IncidentState VALUES(0,100,200);INSERT INTO lab_IncidentProfile VALUES(0,100,200);')
        predicate=guard(validator.capture_section(self.evidence,'EXECUTION_BOUNDS'))
        self.assertFalse(self.connection.execute('SELECT '+predicate).fetchone()[0])
        for column,value in (('FirstExecutionTime',99),('LastExecutionTime',201)):
            self.connection.execute('SAVEPOINT fixture');self.connection.execute(f'UPDATE lab_IncidentProfile SET {column}=?',(value,))
            self.assertTrue(self.connection.execute('SELECT '+predicate).fetchone()[0]);self.connection.execute('ROLLBACK TO fixture');self.connection.execute('RELEASE fixture')

    def test_actual_day_rest_tick_expression_preserves_offset_one_tick_and_sql_max(self):
        """Extrahierte Formel; SQLite-UDF modelliert DATEDIFF_BIG, keine T-SQL-Runtime."""
        def ticks(text):
            match=re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}):(\d{2})\.(\d{7})([+-]\d{2}:\d{2}))?',text)
            year,month,day=(int(value) for value in match.groups()[:3])
            value=(date(year,month,day).toordinal()-1)*864000000000
            if match[4] is not None:
                hour,minute,second=(int(value) for value in match.groups()[3:6])
                value+=(hour*3600+minute*60+second)*10000000+int(match[7])
                offset=match[8];sign=1 if offset[0]=='+' else -1
                value-=sign*(int(offset[1:3])*60+int(offset[4:6]))*600000000
            return value
        def datediff(unit,start,end):
            if unit=='day':return ticks(end)//864000000000-ticks(start)//864000000000
            if unit=='nanosecond':return (ticks(end)-ticks(start))*100
            raise AssertionError('Unbekannte Einheit')
        self.connection.create_function('DATEDIFF_BIG',3,datediff)
        section=validator.capture_section(self.evidence,'TIME_ROWS')
        expression=re.search(r'SELECT w.WindowId,t.TimeKind,\s*(.*?) AS Ticks',section,re.S)[1]
        expression=expression.replace("CONVERT(datetime2(7),'0001-01-01')","'0001-01-01'")
        expression=expression.replace('CONVERT(bigint,864000000000)','864000000000')
        expression=expression.replace('CONVERT(datetime2(7),CONVERT(date,u.UtcTime))','substr(@UtcTime,1,10)')
        expression=expression.replace('u.UtcTime','@UtcTime').replace('DATEDIFF_BIG(day,',"DATEDIFF_BIG('day',").replace('DATEDIFF_BIG(nanosecond,',"DATEDIFF_BIG('nanosecond',")
        def converted(utc):return self.connection.execute('SELECT '+expression,dict(UtcTime=utc)).fetchone()[0]
        first='2026-10-07T12:34:56.1234567+00:00'
        self.assertEqual(converted(first),ticks(first))
        self.assertEqual(converted('2026-10-07T12:34:56.1234568+00:00')-converted(first),1)
        self.assertEqual(converted('9999-12-31T23:59:59.9999999+00:00'),MAX_TICKS)
        self.assertEqual(converted('0001-01-01T00:00:00.0000000+00:00'),0)
        # Die UTC-Vorstufe ist im tatsächlichen SQL obligatorisch; die Formel
        # erhält deren normalisierten Wert, niemals lokale Offsetuhrzeit.
        self.assertEqual(section.count("SWITCHOFFSET(t.TimeValue,'+00:00')"),2)
        self.assertEqual(converted(first),ticks('2026-10-07T18:04:56.1234567+05:30'))

    def test_static_mutations_cannot_hide_measurement_precision_or_guards(self):
        self.assertEqual(validator.request_capture_findings(self.windows),[])
        self.assertEqual(validator.projection_sql_findings(self.evidence),[])
        for before,after in (('COUNT_BIG(*) FROM #Actual','@ExpectedCount'),('@LastRequestId,@MeasuredReturnedRows','@LastRequestId,@ExpectedCount'),('ReturnedRows bigint NOT NULL','ReturnedRows bigint NULL')):
            self.assertTrue(validator.request_capture_findings(self.windows.replace(before,after)),before)
        for before,after in (('t.AvgDurationUs,3','t.AvgDurationUs,2'),('c.RequestLogId=r.RequestLogId','1=1'),("SWITCHOFFSET(t.TimeValue,'+00:00')",'t.TimeValue'),('Ticks IS NULL OR ','Ticks<0 OR '),('PRINT @Frame;','PRINT LEFT(@Frame,2000);')):
            self.assertTrue(validator.projection_sql_findings(self.evidence.replace(before,after)),before)
        for mutation in ('DROP DATABASE master;','EXEC sys.sp_executesql N\'SELECT query_sql_text FROM sys.query_store_query_text;\';'):
            self.assertTrue(validator.projection_sql_findings(self.evidence.replace('/* CAPTURE_PROJECTION_BEGIN */','/* CAPTURE_PROJECTION_BEGIN */\n'+mutation)))
        workflow=validator.WORKFLOW.read_text(encoding='utf-8');self.assertEqual(validator.workflow_findings(workflow),[])
        for before,after in (('--check-capture-projection',''),('cancel-in-progress: false','cancel-in-progress: true'),('python Tests/Static/test_dgn007_capture_projection.py','true')):
            self.assertTrue(validator.workflow_findings(workflow.replace(before,after)),before)
        source=validator.RUNNER.read_text(encoding='utf-8');self.assertEqual(validator.runner_projection_findings(source),[])
        self.assertTrue(validator.runner_projection_findings(source+'\nprint("--show-output")'))
        self.assertTrue(validator.runner_projection_findings(source.replace(
            'if check_capture_projection or check_phase_diagnostics:', 'if True:')))
        self.assertTrue(validator.runner_projection_findings(source.replace(
            'or (check_capture_projection and contract.scope not in CONTROL_SCOPES)', 'or False')))
        for scope in ('data-model','query-store-windows','profile-comparison'):
            self.assertTrue(validator.workflow_findings(workflow.replace(
                '--scope '+scope+' --check-phase-diagnostics','--scope '+scope)))


if __name__=='__main__':unittest.main()
