"""CI-Abnahmegrenzen, synthetische Vertrags- und Steuerungsgegenproben."""
import copy
import importlib.util
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Tests/Runtime'))
import run_dgn010_cost_profile as consumer
from test_dgn010_cost_profile import p, fake_executor


def synthetic_result(*, skip=None, fault=None):
    with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, SQLCMDPASSWORD='synthetic-only'):
        return p.run_cost_profile(executable='synthetic-client', server='synthetic',
                                  confirmed=True, high_impact=True, input_folder=folder,
                                  executor=fake_executor(skip=skip), fault=fault)


class ConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.positive = synthetic_result()
        cls.version_skip = synthetic_result(skip='SKIP_VERSION')
        cls.fault = synthetic_result(fault='after_setup')

    def test_positive_warn_full_record(self):
        self.assertTrue(consumer.validate(self.positive, 17))

    def test_version_skip_and_2025_fail_closed(self):
        for major in (15, 16):
            self.assertFalse(consumer.validate(self.version_skip, major))
            with self.assertRaises(ValueError): consumer.validate(self.positive, major)
        for major in (17, 18):
            with self.assertRaises(ValueError): consumer.validate(self.version_skip, major)
        configuration = synthetic_result(skip='SKIP_CONFIGURATION')
        with self.assertRaises(ValueError): consumer.validate(configuration, 17)

    def test_cleanup_unknown_and_inputs_rejected(self):
        for bad in (replace(self.positive, cleanup_ok=False),
                    replace(self.positive, client_end_unknown=True),
                    replace(self.positive, evidence={**self.positive.evidence, 'own_input_files_preserved':1})):
            with self.assertRaises(ValueError): consumer.validate(bad, 17)

    def test_record_aggregate_and_actual_negative_binding(self):
        for target in ('record', 'aggregate', 'negative', 'absence'):
            evidence = copy.deepcopy(self.positive.evidence)
            phases = self.positive.phases
            if target == 'record': evidence['record']['records'][0]['DdlSha256'] = '0'*64
            if target == 'aggregate': evidence['aggregate']['ddl_windows'] = 3
            if target == 'negative': phases = tuple(p for p in phases if p[1] != 'EXPECTED_REJECTION')
            if target == 'absence': phases = phases[:-1]
            with self.subTest(target=target), self.assertRaises(ValueError):
                consumer.validate(replace(self.positive, evidence=evidence, phases=phases), 17)

    def test_review_p2_missing_renamed_duplicate_or_failed_native_phases(self):
        for phases in ((), self.version_skip.phases[:-1],
                       (self.version_skip.phases[0],('00_Preflight.sql','PASS','OK'),self.version_skip.phases[-1])):
            with self.assertRaises(ValueError): consumer.validate(replace(self.version_skip, phases=phases),16)
        for index in (1,2,7,12,16,32):
            for label,status,code in (('WRONG_LABEL','EXPECTED_REJECTION','51003'),
                                      ('20_Probe.sql','EXPECTED_REJECTION','51003'),
                                      (self.positive.phases[index][0],'FAIL','FAIL_EXECUTION')):
                phases=list(self.positive.phases);phases[index]=(label,status,code)
                if tuple(phases) == self.positive.phases: continue
                with self.subTest(index=index,label=label,status=status), self.assertRaises(ValueError):
                    consumer.validate(replace(self.positive,phases=tuple(phases)),17)

    def test_fault_requires_actual_setup_and_recovery(self):
        consumer.validate_fault(self.fault)
        for bad in (self.positive, replace(self.fault, cleanup_ok=False),
                    replace(self.fault, phases=self.fault.phases[:2]+self.fault.phases[3:])):
            with self.assertRaises(ValueError): consumer.validate_fault(bad)

    def test_two_positive_lifecycles_then_exactly_one_fault_without_raw_export(self):
        calls = []
        def runner(**kwargs):
            calls.append(kwargs.get('fault'))
            return self.fault if kwargs.get('fault') else self.positive
        target = SimpleNamespace(shim='synthetic', server='synthetic', auth='sql', username='sa')
        output = io.StringIO()
        with redirect_stdout(output): consumer.qualify(target, 17, runner)
        self.assertEqual(calls, [None, None, 'after_setup'])
        text = output.getvalue()
        self.assertIn('SQLPERF_SUMMARY|WARN|WARN_OPTIONAL_EVIDENCE_SKIPPED', text)
        self.assertNotIn('DdlSha256', text); self.assertNotIn('modify_date', text)
        calls.clear()
        with redirect_stdout(io.StringIO()):
            consumer.qualify(target, 16, lambda **k:(calls.append(k.get('fault')) or self.version_skip))
        self.assertEqual(calls, [None, None])

    def test_first_failure_admits_no_following_lifecycle(self):
        calls=[]; target=SimpleNamespace(shim='synthetic', server='synthetic', auth='sql', username='sa')
        def runner(**kwargs):
            calls.append(kwargs); return replace(self.positive, client_end_unknown=True)
        with redirect_stdout(io.StringIO()), self.assertRaises(ValueError): consumer.qualify(target,17,runner)
        self.assertEqual(len(calls),1)

    def test_cost_input_dependencies_admit_required_native_gates(self):
        import select_runtime_workflow as selector
        workflow=selector.WORKFLOWS['sql2025-ai-local']
        for path in ('Tests/Static/dgn010_cost_evidence.py','Tests/Static/dgn010_cost_inputs.py'):
            self.assertTrue(selector.select_runtime({path},(path,),workflow,runtime_job_changed=False))

    def test_proxy_preserves_complete_width_and_remote_end_without_password_argument(self):
        spec=importlib.util.spec_from_file_location('cost_ci_proxy',ROOT/'Tests/Runtime/dgn010_docker_sqlcmd_proxy.py')
        proxy=importlib.util.module_from_spec(spec);spec.loader.exec_module(proxy)
        with tempfile.TemporaryDirectory() as folder:
            script=Path(folder)/'synthetic.sql';script.write_text('SELECT 1;',encoding='utf-8')
            args=['proxy','-S','synthetic','-d','master','-U','sa','-i',str(script),'-y','0','-C','-l','2']
            with patch.object(sys,'argv',args),patch.dict(os.environ,SQLCMDPASSWORD='synthetic-only',SQLPERF_SQL_CONTAINER='synthetic-container'),patch.object(proxy.proxy,'_sqlcmd_path',return_value='/synthetic/sqlcmd'),patch.object(proxy.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='',stderr='DGN010_REMOTE_END|0')) as run,redirect_stdout(io.StringIO()),patch('sys.stderr',new=io.StringIO()):
                self.assertEqual(proxy.main(),0)
                command=run.call_args.args[0]
                self.assertIn('-y',command); self.assertEqual(command[command.index('-y')+1],'0')
                self.assertNotIn('-P',command);self.assertNotIn('synthetic-only',command)
                self.assertIn(proxy.REMOTE_WAIT,command)
                args[args.index('-y')+1]='1'
                self.assertEqual(proxy.main(),1);self.assertEqual(run.call_count,1)


if __name__ == '__main__': unittest.main()
