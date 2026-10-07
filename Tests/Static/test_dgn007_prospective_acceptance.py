#!/usr/bin/env python3
"""Reine synthetische Fixtures für den vorher festgelegten Akzeptanzvertrag.

Keine SQL-Ausführung oder Runtime-/Incidentabnahme. Die Charakterisierung der
2019-Überlappung ist absichtlich synthetisch und keine prospektive alte Evidenz.
Alle Entscheidungen kommen aus dem tatsächlichen JSON-gebundenen Evaluator.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext, ROUND_DOWN, ROUND_UP
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from validate_dgn007_prospective_acceptance import (
    MODULE, CONTRACT, AUTOMATED, WORKFLOW, SOURCE_FILES, pure_findings, source_findings, workflow_findings,
)

sys.path.insert(0, str(MODULE.parent))
import dgn007_prospective_acceptance as evaluator

D = Decimal
HASH_A = bytes.fromhex("0102030405060708")
HASH_B = bytes.fromhex("1112131415161718")
ORDERS = (("AB", "BA", "AA"), ("AA", "BA", "AB"))
PHASES = ("PREFLIGHT", "SETUP", "DATA_ASSERTION", "CONTROL_CONFIG", "CONTROL_WINDOWS",
          "PROFILE_COMPARISON", "CONTROL_EVIDENCE", "CLEANUP")


def fixture_runs(contract, major=15, *, plans_different=True, reads_separated=True):
    """Sechs frische deklarierte Lifecycles; ein tatsächlich ausgeführter Plan pro Fenster."""
    runs = []
    for block, orders in enumerate(ORDERS, 1):
        for slot, order in enumerate(orders, 1):
            lifecycle = (block-1)*3+slot
            parent = 100+lifecycle
            object_id = 900+major
            windows, plans, requests = [], [], []
            for window_id, condition in enumerate(order):
                start = 1000+window_id*1000
                interval = 10+window_id
                duration = D("200") if condition == "B" else D("100")
                reads = D("50") if condition == "B" and reads_separated else D("100")
                if order == "AA" and window_id == 1:
                    duration, reads = D("110"), D("103")
                windows.append(evaluator.WindowRecord(
                    window_id=window_id, condition=condition, interval_id=interval,
                    interval_start_ticks=start, interval_end_ticks=start+1000,
                    execution_started_ticks=start+100, execution_finished_ticks=start+200,
                    first_request_log_id=5+window_id*4, last_request_log_id=8+window_id*4,
                    request_count=4, captured_executions=4, execution_count=4,
                    observed_plan_count=1, executed_plan_count=1,
                    avg_duration_us=duration, avg_cpu_us=D("10") if condition == "B" else D("50"),
                    avg_logical_reads=reads, avg_row_count=D("1057.25"), total_rows=D("4229")))
                plans.append(evaluator.ActivePlanRecord(
                    window_id=window_id, parent_query_id=parent, query_id=parent,
                    plan_id=1 if order == "AA" else 1+window_id,
                    interval_id=interval, execution_type=0, execution_count=4,
                    first_execution_ticks=start+100, last_execution_ticks=start+200,
                    query_plan_hash=HASH_B if condition == "B" and plans_different else HASH_A,
                    plan_type=None if major==15 else 0))
                pairs = ((8,3,228),(1,3,2286),(5,3,1144),(1,1,571)) if condition=="A" else ((1,3,2286),(8,3,228),(5,3,1144),(1,1,571))
                requests.extend(evaluator.RequestRecord(window_id,ordinal,4+window_id*4+ordinal,*pair)
                                for ordinal,pair in enumerate(pairs,1))
            run = evaluator.RunRecord(
                major=major, compatibility=major*10, block=block, slot=slot, lifecycle_id=lifecycle,
                scope="DGN-007_CONTROL_"+order, contract_digest=contract.contract_digest,
                source_digest=contract.source_digest, parent_object_id=object_id,
                phases=tuple(evaluator.PhaseResult(phase,"PASS","OK") for phase in PHASES),
                absence_outcome="PASS", absence_code="OK",
                requests=tuple(requests),
                families=(evaluator.QueryFamilyRecord(parent,parent,object_id,"dbo.usp_CaseSearch","/* DGN007_CASE_SEARCH */"),),
                windows=tuple(windows), plans=tuple(plans), plan_union=())
            runs.append(rebuild_union(run))
    return tuple(runs)


def rebuild_union(run):
    keys = {(plan.parent_query_id,plan.query_id,plan.plan_id,plan.query_plan_hash) for plan in run.plans}
    union = tuple(evaluator.PlanUnionRecord(*key,
        int(any((p.parent_query_id,p.query_id,p.plan_id,p.query_plan_hash)==key and p.window_id==0 for p in run.plans)),
        int(any((p.parent_query_id,p.query_id,p.plan_id,p.query_plan_hash)==key and p.window_id==1 for p in run.plans)))
        for key in sorted(keys))
    return replace(run, plan_union=union)


def change_window(runs, run_index, window_index, **values):
    run = runs[run_index]
    windows = list(run.windows)
    windows[window_index] = replace(windows[window_index], **values)
    changed = list(runs)
    changed[run_index] = replace(run, windows=tuple(windows))
    return tuple(changed)


def change_run(runs, index=0, **values):
    return (*runs[:index], replace(runs[index], **values), *runs[index+1:])


class ProspectiveAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.mapping = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.contract = evaluator.contract_from_mapping(self.mapping)
        self.runs = fixture_runs(self.contract)

    def evaluate(self, runs=None, major=15, contract=None):
        return evaluator.evaluate_version(contract or self.contract, major, self.runs if runs is None else runs)

    def result(self, runs, outcome="FAIL", code="FAIL_RESULT_CONTRACT", *, major=15):
        decision = self.evaluate(runs, major)
        self.assertEqual((decision.outcome,decision.code), (outcome,code))
        self.assertFalse(decision.runtime_attested)
        self.assertEqual(decision.validation_scope,"PROJECT_SEMANTIC")
        return decision

    def test_positive_both_evidence_routes_and_all_supported_versions(self):
        for major in (15,16,17):
            with self.subTest(major=major):
                decision = self.result(fixture_runs(self.contract,major),"PASS","OK",major=major)
                self.assertTrue(decision.directed_symptom)
                self.assertTrue(decision.plan_evidence)
                self.assertTrue(decision.profile_evidence)
                self.assertEqual(decision.duration_contrasts,(Fraction(100),)*4)
                self.assertEqual(decision.duration_aa_drift,Fraction(10))
                self.assertEqual(decision.reads_contrasts,(Fraction(-50),)*4)
                self.assertEqual(decision.reads_aa_drift,Fraction(3))

    def test_or_routes_accept_plan_evidence_without_reads_and_reads_without_plan_changes(self):
        for plans, reads in ((True,False),(False,True)):
            with self.subTest(plans=plans,reads=reads):
                decision = self.result(fixture_runs(self.contract,plans_different=plans,reads_separated=reads),"PASS","OK")
                self.assertEqual((decision.plan_evidence,decision.profile_evidence),(plans,reads))

    def test_partial_per_lifecycle_or_routes_do_not_replace_global_evidence_rule(self):
        runs = fixture_runs(self.contract,reads_separated=False)
        # Drei Planbelege und ein Reads-Beleg erfüllen keine vollständige Route.
        run=runs[0]
        plans=tuple(replace(p,query_plan_hash=HASH_A) for p in run.plans)
        runs=change_run(runs,plans=plans,plan_union=rebuild_union(replace(run,plans=plans)).plan_union)
        runs=change_window(runs,0,1,avg_logical_reads=D("50"))
        decision=self.result(runs,"SKIP","SKIP_EVIDENCE_MISSING")
        self.assertFalse(decision.plan_evidence)
        self.assertFalse(decision.profile_evidence)

    def test_invalid_later_metric_dominates_earlier_valid_nonseparation(self):
        runs=fixture_runs(self.contract,plans_different=False,reads_separated=False)
        self.result(change_window(runs,5,1,avg_duration_us=None))

    def test_plan_changes_without_directed_duration_are_not_incident_evidence(self):
        runs = self.runs
        for index,run in enumerate(runs):
            if "B" in run.scope.rsplit("_",1)[1]:
                for window in run.windows:
                    runs = change_window(runs,index,window.window_id,avg_duration_us=D("100"))
        decision = self.result(runs,"SKIP","SKIP_EVIDENCE_MISSING")
        self.assertFalse(decision.directed_symptom)
        self.assertTrue(decision.plan_evidence)

    def test_duration_alone_and_same_hash_with_different_plan_ids_are_not_enough(self):
        runs = fixture_runs(self.contract,plans_different=False,reads_separated=False)
        self.assertNotEqual(runs[0].plans[0].plan_id,runs[0].plans[1].plan_id)
        decision = self.result(runs,"SKIP","SKIP_EVIDENCE_MISSING")
        self.assertTrue(decision.directed_symptom)
        self.assertFalse(decision.plan_evidence)
        self.assertFalse(decision.profile_evidence)

    def test_positive_cpu_contrasts_are_not_a_fallback_evidence_route(self):
        runs=fixture_runs(self.contract,plans_different=False,reads_separated=False)
        for index,run in enumerate(runs):
            for window in run.windows:
                runs=change_window(runs,index,window.window_id,
                                   avg_cpu_us=D("500") if window.condition=="B" else D("50"))
        self.result(runs,"SKIP","SKIP_EVIDENCE_MISSING")

    def test_all_four_lifecycle_hashsets_must_differ_for_plan_route(self):
        runs = fixture_runs(self.contract,reads_separated=False)
        for index in (0,1,4,5):
            run = runs[index]
            plans = tuple(replace(p,query_plan_hash=HASH_A) for p in run.plans)
            changed = change_run(runs,index,plans=plans)
            changed = change_run(changed,index,plan_union=rebuild_union(changed[index]).plan_union)
            with self.subTest(index=index):
                decision = self.result(changed,"SKIP","SKIP_EVIDENCE_MISSING")
                self.assertFalse(decision.plan_evidence)

    def test_hashset_comparison_ignores_query_and_plan_ids_across_lifecycles(self):
        runs = fixture_runs(self.contract,plans_different=False,reads_separated=False)
        # IDs und Hashes zwischen Datenbanken ändern sich; innerhalb jedes Runs bleiben Hashsets gleich.
        for index,run in enumerate(runs):
            plans = tuple(replace(p,query_plan_hash=bytes([index+1])*8) for p in run.plans)
            changed = replace(run,plans=plans)
            runs = change_run(runs,index,plans=plans,plan_union=rebuild_union(changed).plan_union)
        self.assertFalse(self.result(runs,"SKIP","SKIP_EVIDENCE_MISSING").plan_evidence)

    def test_ba_direction_is_b_minus_a_not_later_minus_earlier(self):
        self.assertEqual(self.runs[1].windows[0].condition,"B")
        self.assertGreater(self.runs[1].windows[0].avg_duration_us,self.runs[1].windows[1].avg_duration_us)
        self.result(self.runs,"PASS","OK")
        changed = change_window(self.runs,1,0,avg_duration_us=D("90"))
        decision = self.result(changed,"SKIP","SKIP_EVIDENCE_MISSING")
        self.assertLess(decision.duration_contrasts[1],0)

    def test_strict_duration_equality_zero_and_negative_contrasts_skip(self):
        for value in (D("110"),D("100"),D("99")):
            with self.subTest(value=value):
                self.result(change_window(self.runs,0,1,avg_duration_us=value),"SKIP","SKIP_EVIDENCE_MISSING")

    def test_reads_decrease_increase_mixed_sign_zero_and_noise_boundary(self):
        base = fixture_runs(self.contract,plans_different=False)
        self.result(base,"PASS","OK")
        increase = base
        for index,run in enumerate(base):
            for w in run.windows:
                if w.condition=="B": increase = change_window(increase,index,w.window_id,avg_logical_reads=D("150"))
        self.assertTrue(self.result(increase,"PASS","OK").profile_evidence)
        for value in (D("150"),D("100"),D("97"),D("99")):
            with self.subTest(value=value):
                decision = self.result(change_window(base,0,1,avg_logical_reads=value),"SKIP","SKIP_EVIDENCE_MISSING")
                self.assertFalse(decision.profile_evidence)

    def test_zero_duration_baseline_is_valid_under_absolute_rule(self):
        runs = self.runs
        for index,run in enumerate(runs):
            for window in run.windows:
                runs = change_window(runs,index,window.window_id,
                                     avg_duration_us=D("1") if window.condition=="B" else D("0"))
        self.assertEqual(self.result(runs,"PASS","OK").duration_aa_drift,Fraction(0))

    def test_2019_overlap_characterization_is_synthetic_nonproof_and_skips(self):
        runs = change_window(self.runs,1,0,avg_duration_us=D("1255.25"))
        runs = change_window(runs,2,1,avg_duration_us=D("1813.5"))
        decision = self.result(runs,"SKIP","SKIP_EVIDENCE_MISSING")
        self.assertEqual(decision.duration_contrasts[1],Fraction(D("1155.25")))
        self.assertEqual(decision.duration_aa_drift,Fraction(D("1713.5")))

    def test_tiny_decimal_difference_is_exact_independent_of_global_context(self):
        runs = self.runs
        tiny_b = D("1.000000000000000000000000000001")
        for index,run in enumerate(runs):
            for window in run.windows:
                runs = change_window(runs,index,window.window_id,
                                     avg_duration_us=tiny_b if window.condition=="B" else D("1"))
        for precision,rounding in ((2,ROUND_DOWN),(3,ROUND_UP),(50,ROUND_DOWN)):
            with self.subTest(precision=precision), localcontext() as context:
                context.prec=precision;context.rounding=rounding
                before=(context.prec,context.rounding,dict(context.flags))
                decision = self.result(runs,"PASS","OK")
                self.assertEqual(decision.duration_contrasts,(Fraction(1,10**30),)*4)
                self.assertEqual((context.prec,context.rounding,dict(context.flags)),before)

    def test_null_nan_infinity_negative_bool_float_and_decimal_limits_fail_closed(self):
        bad = (None,D("NaN"),D("sNaN"),D("Infinity"),D("-Infinity"),D("-1"),True,False,1.0,1,
               D("1e-31"),D("1e21"),D("12345678901234567890.123456789012345"))
        for field in ("avg_duration_us","avg_cpu_us","avg_logical_reads","avg_row_count","total_rows"):
            for value in bad:
                with self.subTest(field=field,value=repr(value)):
                    self.result(change_window(self.runs,0,0,**{field:value}))

    def test_exact_decimal_input_boundaries_and_row_rounding_tolerance(self):
        for value in (D("1e-30"),D("1e20"),D("1234.123456789012345678901234567890")):
            with self.subTest(value=value):
                self.result(change_window(self.runs,0,0,avg_cpu_us=value),"PASS","OK")
        for offset, valid in (("4229.000001",True),("4228.999999",True),("4229.0000011",False)):
            with self.subTest(offset=offset):
                self.result(change_window(self.runs,0,0,total_rows=D(offset)),"PASS" if valid else "FAIL","OK" if valid else "FAIL_RESULT_CONTRACT")

    def test_actual_run_order_missing_duplicate_and_mutable_containers_fail_contract(self):
        for runs in (self.runs[::-1],self.runs[1:],self.runs+(self.runs[-1],),
                     self.runs[:1]+self.runs[:1]+self.runs[2:],list(self.runs),None,(object(),)*6):
            with self.subTest(shape=type(runs).__name__):
                # None is tested directly because helper's None selects the valid default.
                decision = evaluator.evaluate_version(self.contract,15,runs)
                self.assertEqual((decision.outcome,decision.code),("FAIL","FAIL_CONTRACT"))
        for field in ("phases","requests","families","windows","plans","plan_union"):
            self.result(change_run(self.runs,**{field:list(getattr(self.runs[0],field))}),code="FAIL_CONTRACT")

    def test_run_version_block_slot_scope_and_lifecycle_digest_bindings(self):
        for field,value in (("major",16),("major",True),("compatibility",160),("block",2),("slot",3),
                            ("scope","DGN-007_CONTROL_BA"),("lifecycle_id",0),("lifecycle_id",True),
                            ("contract_digest","a"*64),("source_digest","b"*64)):
            with self.subTest(field=field):
                self.result(change_run(self.runs,**{field:value}),code="FAIL_CONTRACT")
        self.result(change_run(self.runs,1,lifecycle_id=self.runs[0].lifecycle_id),code="FAIL_CONTRACT")
        for expected in (14,18,True,None,"15"):
            decision = evaluator.evaluate_version(self.contract,expected,self.runs)
            self.assertEqual((decision.outcome,decision.code),("FAIL","FAIL_CONTRACT"))

    def test_window_conditions_missing_double_counts_ranges_and_intervals(self):
        run = self.runs[0]
        for windows in (run.windows[:1],run.windows+(run.windows[1],)):
            self.result(change_run(self.runs,windows=windows),code="FAIL_CONTRACT")
        self.result(change_run(self.runs,windows=run.windows[::-1]))
        bad = (("condition",None),("condition","C"),("condition","B"),("window_id",True),
               ("request_count",3),("captured_executions",5),("execution_count",None),
               ("observed_plan_count",2),("executed_plan_count",0),
               ("first_request_log_id",9),("last_request_log_id",12),
               ("interval_end_ticks",2100),("interval_start_ticks",None),
               ("execution_started_ticks",999),("execution_finished_ticks",2000))
        for field,value in bad:
            with self.subTest(field=field): self.result(change_window(self.runs,0,0,**{field:value}))
        self.result(change_window(self.runs,0,1,interval_id=run.windows[0].interval_id))

    def test_parent_family_scope_variant_and_plan_query_binding(self):
        run = self.runs[0];family = run.families[0]
        for values in ({"query_id":999},{"parent_query_id":999},{"parent_object_id":999},
                       {"parent_object_name":"dbo.OtherSearch"},{"statement_marker":"DGN007_OTHER"}):
            with self.subTest(values=values): self.result(change_run(self.runs,families=(replace(family,**values),)))
        self.result(change_run(self.runs,families=()),code="FAIL_CONTRACT")
        self.result(change_run(self.runs,families=run.families+run.families))
        for values in ({"parent_query_id":999},{"query_id":999},{"interval_id":999}):
            plan = replace(run.plans[0],**values)
            self.result(change_run(self.runs,plans=(plan,run.plans[1])))

    def test_valid_psp_variant_and_parent_self_anchor_are_required(self):
        for major in (16,17):
            runs=fixture_runs(self.contract,major)
            run=runs[0]; parent=run.families[0]
            variant=replace(parent,query_id=parent.query_id+1000)
            plans=tuple(replace(p,query_id=variant.query_id,plan_type=2) for p in run.plans)
            changed=replace(run,families=(parent,variant),plans=plans)
            valid=change_run(runs,families=changed.families,plans=plans,plan_union=rebuild_union(changed).plan_union)
            self.result(valid,"PASS","OK",major=major)
            self.result(change_run(valid,families=(variant,)),major=major)
        run=valid[0]
        invalid15=change_run(self.runs,families=run.families,plans=tuple(replace(p,plan_type=None) for p in run.plans),plan_union=run.plan_union)
        self.result(invalid15)

    def test_request_mix_order_binding_missing_duplicate_and_extra_are_rejected(self):
        run=self.runs[0]
        for requests in (run.requests[:7],run.requests+run.requests[:1]):
            self.result(change_run(self.runs,requests=requests),code="FAIL_CONTRACT")
        for requests in (run.requests[::-1],run.requests[:1]+run.requests[:1]+run.requests[2:]):
            self.result(change_run(self.runs,requests=requests))
        for values in ({"ordinal":2},{"window_id":1},{"request_log_id":6},{"group_key":1},
                       {"status_code":1},{"returned_rows":229},{"ordinal":True},{"returned_rows":None}):
            with self.subTest(values=values):
                self.result(change_run(self.runs,requests=(replace(run.requests[0],**values),*run.requests[1:])))

    def test_hash_sets_use_all_active_plans_without_plan_count_minimum(self):
        runs=fixture_runs(self.contract,plans_different=False,reads_separated=False)
        run=runs[0]
        plans=[]
        for p in run.plans:
            plans.extend((replace(p,plan_id=10+p.window_id*2,execution_count=2),
                          replace(p,plan_id=11+p.window_id*2,execution_count=2,query_plan_hash=HASH_B)))
        windows=tuple(replace(w,observed_plan_count=2,executed_plan_count=2) for w in run.windows)
        changed=replace(run,windows=windows,plans=(plans[0],plans[1],plans[3],plans[2]))
        runs=change_run(runs,windows=windows,plans=changed.plans,plan_union=rebuild_union(changed).plan_union)
        # Gleiche Hashmengen in anderer Reihenfolge bleiben kein Planbeleg.
        self.assertFalse(self.result(runs,"SKIP","SKIP_EVIDENCE_MISSING").plan_evidence)

    def test_hash_plan_type_execution_counts_and_profile_bounds(self):
        run = self.runs[0]
        for values in ({"query_plan_hash":None},{"query_plan_hash":b'1234567'},
                       {"query_plan_hash":'0102030405060708'},{"plan_type":1},
                       {"execution_type":3},{"execution_count":0},{"execution_count":True},
                       {"first_execution_ticks":999},{"last_execution_ticks":2000}):
            with self.subTest(values=values):
                self.result(change_run(self.runs,plans=(replace(run.plans[0],**values),run.plans[1])))
        for major in (16,17):
            runs=fixture_runs(self.contract,major)
            for value in (None,1,3,True):
                self.result(change_run(runs,plans=(replace(runs[0].plans[0],plan_type=value),runs[0].plans[1])),major=major)
            for value in (0,2):
                self.result(change_run(runs,plans=(replace(runs[0].plans[0],plan_type=value),runs[0].plans[1])),"PASS","OK",major=major)

    def test_sql_time_domain_maximum_and_execution_capture_boundaries(self):
        maximum=3155378975999999999
        for field in ("interval_start_ticks","interval_end_ticks","execution_started_ticks","execution_finished_ticks"):
            with self.subTest(field=field):
                self.result(change_window(self.runs,0,0,**{field:maximum+1}))
        run=self.runs[0]; plan=run.plans[0]; window=run.windows[0]
        for field,value in (("first_execution_ticks",maximum+1),("last_execution_ticks",maximum+1),
                            ("first_execution_ticks",window.execution_started_ticks-1),
                            ("last_execution_ticks",window.execution_finished_ticks+1)):
            with self.subTest(field=field,value=value):
                self.result(change_run(self.runs,plans=(replace(plan,**{field:value}),run.plans[1])))
        self.result(self.runs,"PASS","OK")  # first/last exakt an beiden Requestgrenzen.
        offset=maximum-3000
        windows=tuple(replace(w,interval_start_ticks=w.interval_start_ticks+offset,
                              interval_end_ticks=w.interval_end_ticks+offset,
                              execution_started_ticks=w.execution_started_ticks+offset,
                              execution_finished_ticks=w.execution_finished_ticks+offset) for w in run.windows)
        plans=tuple(replace(p,first_execution_ticks=p.first_execution_ticks+offset,
                            last_execution_ticks=p.last_execution_ticks+offset) for p in run.plans)
        self.result(change_run(self.runs,windows=windows,plans=plans),"PASS","OK")

    def test_active_plan_union_must_equal_exact_window_membership(self):
        run=self.runs[0]
        for union in (run.plan_union[:1],run.plan_union+run.plan_union[:1],
                      (replace(run.plan_union[0],executed_in_t1=1),run.plan_union[1]),
                      (replace(run.plan_union[0],query_plan_hash=HASH_B),run.plan_union[1]),
                      (replace(run.plan_union[0],executed_in_t0=True),run.plan_union[1])):
            with self.subTest(union=union): self.result(change_run(self.runs,plan_union=union))
        self.result(change_run(self.runs,plans=run.plans+run.plans[:1]))

    def test_missing_duplicate_reordered_skip_warn_and_unknown_phase_is_not_pass(self):
        run=self.runs[0]
        for phases in (run.phases[:-1],run.phases+run.phases[-1:],run.phases[::-1],
                       tuple(replace(p,phase_id="UNKNOWN") if p.phase_id=="CONTROL_EVIDENCE" else p for p in run.phases)):
            self.result(change_run(self.runs,phases=phases),code="FAIL_CONTRACT")
        for outcome,code in (("SKIP","SKIP_EVIDENCE_MISSING"),("WARN","WARN_EMPIRICAL_VARIANCE"),("PASS","UNKNOWN")):
            phases=tuple(replace(p,outcome=outcome,code=code) if p.phase_id=="CONTROL_WINDOWS" else p for p in run.phases)
            self.result(change_run(self.runs,phases=phases),code="FAIL_CONTRACT")

    def test_cleanup_dominates_timeout_and_malformed_records(self):
        run=self.runs[0]
        timed=tuple(replace(p,outcome="FAIL",code="FAIL_TIMEOUT") if p.phase_id=="CONTROL_WINDOWS" else p for p in run.phases)
        self.result(change_run(self.runs,phases=timed),code="FAIL_TIMEOUT")
        for values in ({"absence_outcome":"FAIL","absence_code":"FAIL_CLEANUP"},
                       {"phases":timed[:-1]+(replace(timed[-1],outcome="FAIL",code="FAIL_CLEANUP"),)},
                       {"absence_outcome":"SKIP","absence_code":"SKIP_EVIDENCE_MISSING"}):
            failed=change_run(self.runs,phases=timed,windows=None)
            failed=change_run(failed,**values)
            self.result(failed,code="FAIL_CLEANUP")
        failed=change_run(self.runs,absence_outcome="FAIL",absence_code="FAIL_CLEANUP")
        self.result((None,*failed[1:],failed[0]),code="FAIL_CLEANUP")
        for code in ("FAIL_CLEANUP","FAIL_TIMEOUT"):
            phases=tuple(replace(p,outcome="FAIL",code=code) if p.phase_id=="CONTROL_WINDOWS" else p for p in run.phases)
            malformed=list(change_run(self.runs,phases=phases,windows=None))
            decision=evaluator.evaluate_version(self.contract,15,malformed)
            self.assertEqual((decision.outcome,decision.code),("FAIL",code))

    def test_json_every_policy_leaf_is_enforced_and_unknown_rules_rejected(self):
        def leaves(value,path=()):
            if isinstance(value,dict):
                for key,item in value.items(): yield from leaves(item,path+(key,))
            elif isinstance(value,list):
                for index,item in enumerate(value): yield from leaves(item,path+(index,))
            else: yield path,value
        policy={key:value for key,value in self.mapping.items() if key!="source_sha256"}
        for path,value in leaves(policy):
            mutated=deepcopy(self.mapping);target=mutated
            for key in path[:-1]: target=target[key]
            target[path[-1]]=not value if type(value) is bool else value+1 if type(value) is int else "MUTATED" if value is None else str(value)+"_MUTATED"
            with self.subTest(path=path),self.assertRaisesRegex(evaluator.ContractError,"^FAIL_CONTRACT$"):
                evaluator.contract_from_mapping(mutated)
        for changed in ({**self.mapping,"unknown_rule":True}, {k:v for k,v in self.mapping.items() if k!="duration_rule"}):
            with self.assertRaisesRegex(evaluator.ContractError,"^FAIL_CONTRACT$"): evaluator.contract_from_mapping(changed)

    def test_canonical_contract_and_source_digests_bind_actual_evaluator_records(self):
        canonical=lambda mapping: hashlib.sha256(json.dumps(mapping,sort_keys=True,ensure_ascii=True,separators=(',',':'),allow_nan=False).encode('ascii')).hexdigest()
        self.assertEqual(self.contract.contract_digest,canonical(self.mapping))
        self.assertEqual(self.contract.source_digest,canonical(self.mapping['source_sha256']))
        shuffled=dict(reversed(list(self.mapping.items())))
        self.assertEqual(evaluator.contract_from_mapping(shuffled),self.contract)
        changed=deepcopy(self.mapping);changed['source_sha256'][SOURCE_FILES[0]]='a'*64
        rebound=evaluator.contract_from_mapping(changed)
        self.assertNotEqual(rebound.contract_digest,self.contract.contract_digest)
        self.assertNotEqual(rebound.source_digest,self.contract.source_digest)
        decision=self.evaluate(contract=rebound)
        self.assertEqual((decision.outcome,decision.code),("FAIL","FAIL_CONTRACT"))
        self.assertTrue(source_findings(changed))
        for values in ({"schema":"unknown"},{"contract_digest":"a"*64},{"source_digest":"b"*64},{"source_hashes":()}):
            decision=self.evaluate(contract=replace(self.contract,**values))
            self.assertEqual((decision.outcome,decision.code),("FAIL","FAIL_CONTRACT"))

    def test_source_normalization_and_one_byte_drift_without_file_mutations(self):
        self.assertEqual(source_findings(self.mapping),[])
        original=Path.read_bytes
        selected=AUTOMATED/SOURCE_FILES[0]
        def changed(path):
            data=original(path)
            return data+b' ' if path==selected else data
        with patch.object(Path,'read_bytes',changed): self.assertTrue(source_findings(self.mapping))
        def crlf(path): return original(path).replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
        with patch.object(Path,'read_bytes',crlf): self.assertEqual(source_findings(self.mapping),[])

    def test_records_contract_decision_are_immutable_and_do_not_attest_runtime(self):
        decision=self.result(self.runs,"PASS","OK")
        self.assertIn("keine Runtime-Abnahme",decision.claim_scope)
        for value,field,new in ((self.contract,"schema","unknown"),(self.runs[0],"slot",3),
                                (self.runs[0].windows[0],"condition","B"),(decision,"outcome","FAIL")):
            with self.assertRaises(FrozenInstanceError): setattr(value,field,new)

    def test_pure_module_and_separate_ci_do_not_start_sql_or_export_artifacts(self):
        self.assertEqual(pure_findings(MODULE.read_text(encoding='utf-8')),[])
        workflow=WORKFLOW.read_text(encoding='utf-8')
        self.assertEqual(workflow_findings(workflow),[])
        for addition in ('import subprocess','print("synthetic")','open("synthetic")'):
            self.assertTrue(pure_findings(addition))
        for addition in ('\n          docker run synthetic','\n          run_dgn007_automated_setup.py','\n          upload-artifact'):
            self.assertTrue(workflow_findings(workflow+addition))


if __name__ == "__main__":
    unittest.main()
