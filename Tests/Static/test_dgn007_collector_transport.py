#!/usr/bin/env python3
"""Synthetische Tests des tatsächlichen JSON-Decoders, ohne SQL-Produzent.

MEASURED ist hier eine deklarierte Fixtureangabe, keine Herkunftsattestation.
Keine Phasen-, Cleanup-, Budget- oder tatsächlichen Laufnachweise werden erzeugt.
"""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, replace
from decimal import Decimal, localcontext, ROUND_DOWN, ROUND_UP
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from validate_dgn007_collector_transport import MODULE, WORKFLOW, pure_findings, workflow_findings
from validate_dgn007_prospective_acceptance import CONTRACT

sys.path.insert(0,str(MODULE.parents[2]))
from Tests.Contracts import dgn007_collector_transport as transport
from Tests.Contracts import dgn007_prospective_acceptance as acceptance

MAX_TICKS=3155378975999999999
HASH_A="0102030405060708"
HASH_B="1112131415161718"


def payload(contract,major=15,sequence="AB",measured=True):
    """Direktes JSON-Dokument mit festen synthetischen Messangaben und IDs."""
    windows=[];requests=[];plans=[];union=[]
    for window_id,condition in enumerate(sequence):
        start=1000+window_id*1000
        windows.append(dict(window_id=window_id,condition=condition,interval_id=10+window_id,
            interval_start_ticks=start,interval_end_ticks=start+1000,
            execution_started_ticks=start+100,execution_finished_ticks=start+200,
            first_request_log_id=5+window_id*4,last_request_log_id=8+window_id*4,
            request_count=4,captured_executions=4,execution_count=4,
            observed_plan_count=1,executed_plan_count=1,
            avg_duration_us="1.2345678901234567E+2",avg_cpu_us="10",
            avg_logical_reads="50",avg_row_count="1057.25",total_rows="4229"))
        pairs=((8,3,228),(1,3,2286),(5,3,1144),(1,1,571)) if condition=="A" else ((1,3,2286),(8,3,228),(5,3,1144),(1,1,571))
        for ordinal,(group,status,rows) in enumerate(pairs,1):
            requests.append(dict(window_id=window_id,ordinal=ordinal,request_log_id=4+window_id*4+ordinal,
                group_key=group,status_code=status,returned_rows=rows if measured else None,
                row_evidence="MEASURED" if measured else "NOT_CAPTURED"))
        hash_value=HASH_A if condition=="A" else HASH_B
        plans.append(dict(window_id=window_id,parent_query_id=101,query_id=101,plan_id=1+window_id,
            interval_id=10+window_id,execution_type=0,execution_count=4,
            first_execution_ticks=start+100,last_execution_ticks=start+200,
            query_plan_hash=hash_value,plan_type=None if major==15 else 0))
        union.append(dict(parent_query_id=101,query_id=101,plan_id=1+window_id,query_plan_hash=hash_value,
            executed_in_t0=int(window_id==0),executed_in_t1=int(window_id==1)))
    return dict(schema=transport.SCHEMA,major=major,compatibility=major*10,
        scope="DGN-007_CONTROL_"+sequence,contract_digest=contract.contract_digest,
        source_digest=contract.source_digest,parent_object_id=915,
        windows=windows,requests=requests,
        families=[dict(query_id=101,parent_query_id=101,parent_object_id=915,
            parent_object_name="dbo.usp_CaseSearch",statement_marker="/* DGN007_CASE_SEARCH */")],
        plans=plans,plan_union=union)


def encode(value):
    return json.dumps(value,ensure_ascii=True,separators=(',',':'),allow_nan=False)


class CollectorTransportTests(unittest.TestCase):
    def setUp(self):
        self.contract=acceptance.contract_from_mapping(json.loads(CONTRACT.read_text(encoding='utf-8')))
        self.payload=payload(self.contract)

    def decode(self,value=None):
        return transport.decode_capture(encode(self.payload if value is None else value),self.contract)

    def rejected(self,value,code="FAIL_RESULT_CONTRACT",raw=False):
        with self.assertRaises(transport.TransportError) as raised:
            transport.decode_capture(value if raw else encode(value),self.contract)
        self.assertEqual(str(raised.exception),code)
        self.assertEqual(raised.exception.code,code)
        self.assertIsNone(raised.exception.__cause__)
        self.assertIsNone(raised.exception.__context__)

    def test_all_versions_and_ab_ba_aa_decode_to_immutable_records(self):
        for major in (15,16,17):
            for sequence in ("AB","BA","AA"):
                with self.subTest(major=major,sequence=sequence):
                    body=self.decode(payload(self.contract,major,sequence))
                    self.assertEqual((body.major,body.compatibility,body.scope),(major,major*10,"DGN-007_CONTROL_"+sequence))
                    self.assertEqual(tuple(w.condition for w in body.windows),tuple(sequence))
                    self.assertTrue(body.row_evidence_complete)
                    self.assertEqual(body.validation_scope,"PROJECT_SEMANTIC")
                    self.assertFalse(body.runtime_attested)
                    self.assertIsInstance(body,transport.CaptureBody)
                    for name in ('windows','requests','families','plans','plan_union'):
                        self.assertIs(type(getattr(body,name)),tuple)
                    self.assertIs(type(body.windows[0].avg_duration_us),Decimal)
                    self.assertEqual(body.plans[0].query_plan_hash,bytes.fromhex(HASH_A if sequence[0]=='A' else HASH_B))
        body=self.decode()
        for record,field,value in ((body,'major',17),(body.windows[0],'condition','B'),(body.requests[0],'returned_rows',999)):
            with self.assertRaises(FrozenInstanceError): setattr(record,field,value)

    def test_scientific_17_digits_and_34_digits_are_lossless_across_contexts(self):
        values=('1.2345678901234567E+2','1.234567890123456789012345678901234E+3','1E-30','1E+20','0E-30')
        for text in values:
            document=deepcopy(self.payload);document['windows'][0]['avg_duration_us']=text
            for precision,rounding in ((2,ROUND_DOWN),(3,ROUND_UP),(50,ROUND_DOWN)):
                with self.subTest(text=text,precision=precision),localcontext() as context:
                    context.prec=precision;context.rounding=rounding
                    before=(context.prec,context.rounding,dict(context.flags))
                    metric=self.decode(document).windows[0].avg_duration_us
                    self.assertEqual(metric.as_tuple(),Decimal(text).as_tuple())
                    self.assertEqual((context.prec,context.rounding,dict(context.flags)),before)

    def test_one_tick_precision_and_exact_sql_time_maximum(self):
        body=self.decode()
        document=deepcopy(self.payload)
        document['windows'][0]['execution_started_ticks']+=1
        document['plans'][0]['first_execution_ticks']+=1
        changed=self.decode(document)
        self.assertEqual(changed.windows[0].execution_started_ticks-body.windows[0].execution_started_ticks,1)
        self.assertEqual(changed.plans[0].first_execution_ticks-body.plans[0].first_execution_ticks,1)
        offset=MAX_TICKS-3000
        for window in document['windows']:
            for key in ('interval_start_ticks','interval_end_ticks','execution_started_ticks','execution_finished_ticks'): window[key]+=offset
        for plan in document['plans']:
            for key in ('first_execution_ticks','last_execution_ticks'): plan[key]+=offset
        self.assertEqual(self.decode(document).windows[1].interval_end_ticks,MAX_TICKS)
        for collection,key in (('windows','interval_end_ticks'),('plans','last_execution_ticks')):
            invalid=deepcopy(document);invalid[collection][1][key]=MAX_TICKS+1
            self.rejected(invalid)

    def test_missing_row_measurement_stays_unknown_and_never_uses_expected_counts(self):
        document=payload(self.contract,measured=False)
        body=self.decode(document)
        self.assertFalse(body.row_evidence_complete)
        self.assertTrue(all(r.returned_rows is None and r.row_evidence=='NOT_CAPTURED' for r in body.requests))
        mixed=deepcopy(self.payload);mixed['requests'][0].update(row_evidence='NOT_CAPTURED',returned_rows=None)
        body=self.decode(mixed)
        self.assertFalse(body.row_evidence_complete)
        self.assertIsNone(body.requests[0].returned_rows)
        for evidence,rows in (('NOT_CAPTURED',228),('MEASURED',None),('EXPECTED',228),('MEASURED',229)):
            invalid=deepcopy(self.payload);invalid['requests'][0].update(row_evidence=evidence,returned_rows=rows)
            self.rejected(invalid,'FAIL_CONTRACT' if evidence=='EXPECTED' or (evidence=='MEASURED' and rows is None) else 'FAIL_RESULT_CONTRACT')

    def test_capture_body_has_no_fabricated_lifecycle_status_or_attestation(self):
        body=self.decode()
        self.assertNotIsInstance(body,acceptance.RunRecord)
        names={field.name for field in fields(body)}
        self.assertFalse(names & {'phases','absence_outcome','absence_code','block','slot','lifecycle_id','resource_attestation'})
        for key in ('phases','absence_code','block','slot','runtime_attested','raw_output','query_text','plan_xml'):
            document=deepcopy(self.payload);document[key]='synthetic_untrusted_payload'
            self.rejected(document,'FAIL_CONTRACT')

    def test_duplicate_keys_top_level_and_nested_are_rejected(self):
        text=encode(self.payload)
        self.rejected(text.replace('"major":15','"major":15,"major":15'),'FAIL_CONTRACT',True)
        self.rejected(text.replace('"condition":"A"','"condition":"A","condition":"A"',1),'FAIL_CONTRACT',True)
        self.rejected(text.replace('"query_plan_hash":"'+HASH_A+'"','"query_plan_hash":"'+HASH_A+'","query_plan_hash":"'+HASH_A+'"',1),'FAIL_CONTRACT',True)

    def test_missing_additional_unknown_and_null_fields_at_every_record_level(self):
        for collection in (None,'windows','requests','families','plans','plan_union'):
            source=self.payload if collection is None else self.payload[collection][0]
            for key in source:
                document=deepcopy(self.payload);target=document if collection is None else document[collection][0]
                del target[key]
                with self.subTest(collection=collection,key=key): self.rejected(document,'FAIL_CONTRACT')
            document=deepcopy(self.payload);target=document if collection is None else document[collection][0]
            target['unknown']='synthetic_untrusted_payload'
            self.rejected(document,'FAIL_CONTRACT')

    def test_truncated_additional_malformed_and_nontext_documents(self):
        text=encode(self.payload)
        for invalid in ('',text[:-1],text+' {}',text+' trailing',text+',',text.replace('"major":15','"major":015'),'\ud800',None,True,{},text.encode()):
            with self.subTest(kind=type(invalid).__name__): self.rejected(invalid,'FAIL_CONTRACT',True)
        for token in ('NaN','Infinity','-Infinity'):
            self.rejected(text.replace('"major":15','"major":'+token),'FAIL_CONTRACT',True)

    def test_payload_size_and_depth_are_bounded_before_json_parsing(self):
        text=encode(self.payload)
        self.assertEqual(self.decode().major,15)
        maximum=32768
        padded=text+' '*(maximum-len(text.encode('utf-8')))
        self.assertEqual(transport.decode_capture(padded,self.contract).major,15)
        for invalid in (padded+' ',text+'ü'*maximum,'['*9+'0'+']'*9):
            with self.subTest(size=len(invalid)),patch.object(transport.json,'loads',side_effect=AssertionError('must not parse')):
                self.rejected(invalid,'FAIL_CONTRACT',True)

    def test_integer_fields_reject_bool_float_decimal_strings_and_large_tokens(self):
        for collection,key in ((None,'major'),('windows','interval_start_ticks'),('requests','request_log_id'),('plans','execution_count'),('plan_union','executed_in_t0')):
            for value in (True,False,1.0,'1',None,10**19):
                document=deepcopy(self.payload);target=document if collection is None else document[collection][0]
                target[key]=value
                with self.subTest(collection=collection,key=key,value=value): self.rejected(document,'FAIL_CONTRACT')
        text=encode(self.payload)
        for token in ('15.0','15e0','1e1'):
            self.rejected(text.replace('"major":15','"major":'+token),'FAIL_CONTRACT',True)

    def test_metric_strings_reject_null_nonfinite_negative_and_representation_limits(self):
        for key in ('avg_duration_us','avg_cpu_us','avg_logical_reads','avg_row_count','total_rows'):
            for value in (None,True,1,1.0):
                document=deepcopy(self.payload);document['windows'][0][key]=value
                with self.subTest(key=key,value=value): self.rejected(document,'FAIL_CONTRACT')
            for value in ('NaN','sNaN','Infinity','-Infinity','-1','1E-31','1E21','1234.1234567890123456789012345678901','1'*65,'synthetic_untrusted_payload'):
                document=deepcopy(self.payload);document['windows'][0][key]=value
                with self.subTest(key=key,value=value): self.rejected(document)

    def test_hash_format_length_and_union_binding(self):
        for value in (None,True,1,'0x'+HASH_A,HASH_A[:-1],HASH_A+'0','zz'*8):
            document=deepcopy(self.payload);document['plans'][0]['query_plan_hash']=value
            self.rejected(document,'FAIL_CONTRACT' if type(value) is not str else 'FAIL_RESULT_CONTRACT')
        document=deepcopy(self.payload);document['plan_union'][0]['query_plan_hash']=HASH_B
        self.rejected(document)
        document=deepcopy(self.payload)
        letter_hash='aabbccddeeff0011'
        document['plans'][0]['query_plan_hash']=letter_hash.upper();document['plan_union'][0]['query_plan_hash']=letter_hash
        self.assertEqual(self.decode(document).plans[0].query_plan_hash,bytes.fromhex(letter_hash))

    def test_version_scope_contract_and_source_bindings(self):
        for key,value in (('schema','unknown'),('major',14),('compatibility',160),('scope','DGN-007_PROFILE_COMPARISON'),
                          ('contract_digest','a'*64),('source_digest','b'*64),('parent_object_id',0)):
            document=deepcopy(self.payload);document[key]=value
            self.rejected(document,'FAIL_CONTRACT' if key!='parent_object_id' else 'FAIL_RESULT_CONTRACT')
        for contract in (None,{},replace(self.contract,contract_digest='a'*64),replace(self.contract,source_hashes=())):
            with self.assertRaisesRegex(transport.TransportError,'^FAIL_CONTRACT$'):
                transport.decode_capture(encode(self.payload),contract)

    def test_missing_duplicate_extra_records_and_array_types(self):
        for key in ('windows','requests','families','plans','plan_union'):
            for value in (None,{},self.payload[key]+[self.payload[key][0]]):
                document=deepcopy(self.payload);document[key]=value
                self.rejected(document,'FAIL_CONTRACT' if value is None or type(value) is dict or key in ('windows','requests') else 'FAIL_RESULT_CONTRACT')
        for key in ('windows','requests'):
            document=deepcopy(self.payload);document[key]=document[key][:-1]
            self.rejected(document,'FAIL_CONTRACT')

    def test_request_order_pairs_counts_and_ranges_remain_bound(self):
        for key,value in (('ordinal',2),('window_id',1),('request_log_id',6),('group_key',1),('status_code',1),('returned_rows',229)):
            document=deepcopy(self.payload);document['requests'][0][key]=value
            self.rejected(document)
        document=deepcopy(self.payload);document['requests'].reverse();self.rejected(document)
        for key,value in (('condition','B'),('request_count',3),('captured_executions',5),('execution_count',3),('observed_plan_count',2),('first_request_log_id',4),('total_rows','4229.000002')):
            document=deepcopy(self.payload);document['windows'][0][key]=value;self.rejected(document)

    def test_disjoint_intervals_and_execution_bounds(self):
        for collection,key,value in (('windows','interval_id',11),('windows','interval_end_ticks',2100),
                ('windows','execution_started_ticks',999),('windows','execution_finished_ticks',2000),
                ('plans','first_execution_ticks',999),('plans','last_execution_ticks',2000),('plans','interval_id',11)):
            document=deepcopy(self.payload);document[collection][0][key]=value;self.rejected(document)

    def test_v2_preserves_clock_mismatch_and_rejects_legacy_body(self):
        document=deepcopy(self.payload)
        document['plans'][0]['first_execution_ticks']=1099
        document['plans'][0]['last_execution_ticks']=1201
        result=self.decode(document)
        self.assertEqual(result.plans[0].first_execution_ticks,1099)
        self.assertEqual(result.plans[0].last_execution_ticks,1201)
        document['schema']='dgn007-capture-body/v1'
        self.rejected(document,'FAIL_CONTRACT')

    def test_parent_families_active_plans_and_plan_types(self):
        for collection,key,value in (('families','parent_query_id',999),('families','parent_object_id',999),
                ('families','statement_marker','/* OTHER */'),('families','parent_object_name','dbo.OtherSearch'),
                ('plans','parent_query_id',999),('plans','query_id',999),('plans','execution_count',0),('plans','execution_type',3)):
            document=deepcopy(self.payload);document[collection][0][key]=value;self.rejected(document)
        for major in (16,17):
            for value in (None,1,3):
                document=payload(self.contract,major);document['plans'][0]['plan_type']=value;self.rejected(document,'FAIL_CONTRACT' if value is None else 'FAIL_RESULT_CONTRACT')
            document=payload(self.contract,major)
            variant=deepcopy(document['families'][0]);variant['query_id']=201;document['families'].append(variant)
            for plan in document['plans']: plan.update(query_id=201,plan_type=2)
            for row in document['plan_union']: row['query_id']=201
            self.assertEqual(self.decode(document).plans[0].query_id,201)
            document['families']=document['families'][1:];self.rejected(document)

    def test_decoder_has_no_console_or_file_io_and_errors_never_leak_raw_values(self):
        output=io.StringIO();errors=io.StringIO()
        with redirect_stdout(output),redirect_stderr(errors),patch('builtins.open',side_effect=AssertionError('no file I/O')):
            self.decode()
            document=deepcopy(self.payload);document['windows'][0]['avg_duration_us']='synthetic_untrusted_payload'
            self.rejected(document)
        self.assertEqual((output.getvalue(),errors.getvalue()),('',''))

    def test_static_scope_and_own_ci_preserve_pure_dependency_checks(self):
        self.assertEqual(pure_findings(MODULE.read_text(encoding='utf-8')),[])
        source=WORKFLOW.read_text(encoding='utf-8');self.assertEqual(workflow_findings(source),[])
        for mutation in ('import subprocess','open("synthetic")','print("synthetic")','RunRecord()','PhaseResult()','evaluate_version()'):
            self.assertTrue(pure_findings(mutation))
        for addition in ('\n          docker run synthetic','\n          Tests/Runtime/runner.py','\n          upload-artifact'):
            self.assertTrue(workflow_findings(source+addition))


if __name__=='__main__':
    unittest.main()
