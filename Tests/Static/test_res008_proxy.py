"""Tatsächliche Controllerargumente und ENV-/stdin-Vertrag ohne SQL-Instanz."""
import importlib.util,os,sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Tests/Runtime'))
spec=importlib.util.spec_from_file_location('res008_proxy_test',ROOT/'Tests/Runtime/res008_docker_sqlcmd_proxy.py')
adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
spec=importlib.util.spec_from_file_location('res008_proxy_profile_test',ROOT/'Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions/run_profile.py')
profile=importlib.util.module_from_spec(spec);sys.modules[spec.name]=profile;spec.loader.exec_module(profile)

class ProxyCases(unittest.TestCase):
    def command(self,script,**kwargs):
        with patch.dict(os.environ,SQLCMDPASSWORD='synthetic-test-only'):
            command=profile.command_for('synthetic-sqlcmd','synthetic-server','sql','sa',script,**kwargs)
        return command[1:]
    def test_all_actual_controller_commands_parse(self):
        for script in profile.SCRIPTS:
            kwargs={'variables':{'Dimension':'32'},'full_scalar':True} if script=='40_Plan.sql' else {}
            with self.subTest(script=script):
                _,path,username,variables,flags=adapter.proxy._parse_args(self.command(script,**kwargs))
                self.assertEqual(path.name,script);self.assertEqual(username,'sa')
                self.assertIn('RunToken=LOCAL',variables);self.assertIn('-C',flags)
                self.assertEqual(flags[flags.index('-l')+1],'2');self.assertNotIn('-P',flags)
                if script=='40_Plan.sql':
                    self.assertEqual(flags[flags.index('-y')+1],'0');self.assertNotIn('-W',flags)
    def test_unknown_and_password_options_are_rejected(self):
        for extra in (['-P','synthetic-secret'],['-Q','SELECT 1'],['-l'],['-y']):
            with self.subTest(extra=extra),self.assertRaises(ValueError):
                adapter.proxy._parse_args(self.command('91_Absence.sql')+extra)
    def test_native_stdin_env_and_returncode_are_preserved(self):
        command=self.command('91_Absence.sql');calls=[]
        def run(actual,**kwargs):
            calls.append((actual,kwargs));return SimpleNamespace(returncode=17,stdout='',stderr='')
        with patch.dict(os.environ,SQLCMDPASSWORD='synthetic-test-only',SQLPERF_SQL_CONTAINER='synthetic-own-container'),patch.object(sys,'argv',['proxy',*command]),patch.object(adapter.proxy,'_sqlcmd_path',return_value='/synthetic/sqlcmd'),patch.object(adapter.proxy.subprocess,'run',side_effect=run):
            self.assertEqual(adapter.proxy.main(),17)
        actual,kwargs=calls[0]
        self.assertEqual(actual[:6],['docker','exec','-i','-e','SQLCMDPASSWORD','synthetic-own-container'])
        self.assertNotIn('synthetic-test-only',actual);self.assertNotIn('-P',actual)
        self.assertEqual(kwargs['env']['SQLCMDPASSWORD'],'synthetic-test-only')
        self.assertEqual(kwargs['input'],(profile.FOLDER/'91_Absence.sql').read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()
