#!/usr/bin/env python3
"""OPT-007: FWK-011-Normalisierung und tatsächlichen Containercleanup prüfen."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Tests/Runtime'))
import run_opt007 as demo
import test_con005_container_cleanup as cleanup


class Opt007ContainerCleanupTests(cleanup.ContainerCleanupTests):
    def setUp(self):
        self.binding=patch.object(cleanup,'WORKFLOW',ROOT/'.github/workflows/opt007-adhoc-cache.yml')
        self.binding.start()
        self.addCleanup(self.binding.stop)

    def test_own_resource_is_removed_and_absence_is_checked(self):
        result,trace=self.run_case('OWN')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('OPT007_CONTAINER_CLEANUP|PASS|ABSENT',result.stdout)
        self.assertEqual(trace,'REMOVE\n')

    def test_startup_test_and_cleanup_keep_a_job_reserve(self):
        text=cleanup.WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('timeout --signal=TERM --kill-after=30s 600s python Tests/Runtime/run_opt007.py',text)
        for token in ('timeout-minutes: 30','timeout-minutes: 10','timeout-minutes: 12','timeout-minutes: 3',
                      '-b -l 5 -t 5 -Q','--cidfile "${cidfile}"','-e MSSQL_SA_PASSWORD -d "${image_id}"'):
            self.assertIn(token,text)


class ResultTests(unittest.TestCase):
    def output(self):
        return ('OPT007_METRIC|L|20|20|1000\nOPT007_METRIC|L|40|40|2000\n'
                'OPT007_METRIC|P|20|1|900\nOPT007_METRIC|P|40|1|900\n'
                'OPT007_RESULT|L|40|40|820\nOPT007_RESULT|P|40|40|820\n')

    def evaluate(self,text):
        temp=ROOT/'Runtime/Temp';temp.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='opt007-unit-',dir=temp) as directory:
            path=Path(directory)/'evidence.json'
            path.write_text(json.dumps(demo.numeric_evidence(text)),encoding='utf-8')
            return demo.evaluator.run(demo.DIRECTORY/'Expected/result-contract.json',path)

    def test_numeric_contract_positive_and_missing_or_wrong(self):
        self.assertEqual(self.evaluate(self.output())[0][-1]['outcome'],'PASS')
        for text in (self.output().replace('OPT007_METRIC|P|20|1|900\n',''),
                     self.output().replace('P|40|40|820','P|39|40|820'),
                     self.output().replace('L|20|20|1000','L|20|19|1000')):
            self.assertEqual(self.evaluate(text)[0][-1]['outcome'],'FAIL')

    def test_duplicate_and_invalid_bytes(self):
        for text in (self.output()+'OPT007_METRIC|L|20|20|1000\n',
                     self.output()+'OPT007_RESULT|P|40|40|820\n',
                     self.output().replace('L|20|20|1000','L|20|20|0')):
            with self.assertRaises(RuntimeError):demo.numeric_evidence(text)


if __name__=='__main__':unittest.main()
