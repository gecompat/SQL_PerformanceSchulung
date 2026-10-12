"""Öffentlicher CLI-Consumer: aggregierter Export erst nach bekanntem Abschluss."""
import contextlib,importlib.util,io,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
PUBLIC=ROOT/'Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions'
spec=importlib.util.spec_from_file_location('res008_summary_cli_profile',PUBLIC/'run_profile.py')
profile=importlib.util.module_from_spec(spec);sys.modules[spec.name]=profile;spec.loader.exec_module(profile)
spec=importlib.util.spec_from_file_location('res008_summary_cli_fixture',ROOT/'Tests/Static/test_res008_summary.py')
cases=importlib.util.module_from_spec(spec);spec.loader.exec_module(cases)

class CliCases(unittest.TestCase):
    def run_cli(self,result):
        output=io.StringIO()
        args=['profile','--server','synthetic-server','--summary','--confirm-isolated-lab','--high-impact-confirmed']
        with patch.object(sys,'argv',args),patch.object(profile,'resolve_sqlcmd',return_value='unused'),patch.object(profile,'run_profile',return_value=result),contextlib.redirect_stdout(output):
            status=profile.main()
        return status,output.getvalue()
    def test_positive_export_preserves_overall_warn_and_privacy(self):
        result=profile.Result('WARN','WARN_OPTIONAL_EVIDENCE_SKIPPED',True,False,(),cases.fixture())
        status,output=self.run_cli(result)
        self.assertEqual(status,0)
        aggregate=json.loads(next(line.split('|',1)[1] for line in output.splitlines() if line.startswith('RES008_AGGREGATE|')))
        self.assertEqual(aggregate['outcome'],'WARN');self.assertEqual(len(aggregate['fwk011']),3)
        self.assertIn('SQLPERF_SUMMARY|WARN|WARN_OPTIONAL_EVIDENCE_SKIPPED',output)
        for forbidden in ('ConnectionId','RequestStartTime','DatabaseId','SQLPERF_LAB_RES008','Queries'):
            self.assertNotIn(forbidden,output)
    def test_failed_or_skipped_profile_cannot_export(self):
        for outcome,code in (('FAIL','FAIL_CLEANUP'),('SKIP','SKIP_VERSION')):
            with self.subTest(outcome=outcome),patch.object(profile.summary,'summarize_result',side_effect=AssertionError('unexpected aggregate')):
                status,output=self.run_cli(profile.Result(outcome,code,outcome=='SKIP',outcome=='FAIL',(),{}))
                self.assertEqual(status,1 if outcome=='FAIL' else 0);self.assertNotIn('RES008_AGGREGATE|',output)
    def test_aggregation_error_is_fail_after_native_cleanup(self):
        result=profile.Result('WARN','WARN_OPTIONAL_EVIDENCE_SKIPPED',True,False,(),cases.fixture())
        with patch.object(profile.summary,'summarize_result',side_effect=ValueError('synthetic invalid contract')):
            status,output=self.run_cli(result)
        self.assertEqual(status,1);self.assertEqual(output.strip(),'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT')

if __name__=='__main__':unittest.main()
