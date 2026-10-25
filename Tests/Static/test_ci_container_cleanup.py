"""Echten Bash-Cleanup mit synthetischen Dockerantworten ausführen."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from test_con005_container_cleanup import bash_executable

ROOT=Path(__file__).resolve().parents[2]
HELPER=ROOT/'Tests/Runtime/cleanup_ci_container.sh'
MOCK=r'''
docker() {
  case "$1 $2" in
    'container ls')
      if [ "$SCENARIO" = DAEMON_DOWN ]; then return 125; fi
      if [ -f "$TRACE" ]; then
        if [ "$SCENARIO" = POST_ERROR ]; then return 125; fi
        if [ "$SCENARIO" = RESIDUE ]; then echo "$CID"; fi
        return 0
      fi
      if [ "$SCENARIO" = ABSENT ]; then return 0; fi
      if [ "$SCENARIO" = EXTRA_OWNER ] && [[ "$*" = *label=* ]]; then printf '%s\n%s\n' "$CID" "$CID"; return 0; fi
      echo "$CID";;
    'inspect --format')
      if [ "$SCENARIO" = INSPECT_ERROR ]; then return 125; fi
      if [ "$SCENARIO" = FOREIGN ]; then echo "$CID|/$SQLPERF_SQL_CONTAINER|foreign"; return 0; fi
      echo "$CID|/$SQLPERF_SQL_CONTAINER|$SQLPERF_CI_OWNER";;
    'rm --force')
      [ "$3" = --volumes ] && [ "$4" = "$CID" ] || return 126
      if [ "$SCENARIO" = REMOVE_ERROR ]; then return 125; fi
      echo removed > "$TRACE";;
    *) return 126;;
  esac
}
'''

class CleanupTests(unittest.TestCase):
    def test_actual_cleanup_and_failure_boundaries(self):
        parent=ROOT/'Runtime/Temp';parent.mkdir(parents=True,exist_ok=True)
        for scenario in ('OWN','ABSENT','DAEMON_DOWN','FOREIGN','EXTRA_OWNER','INSPECT_ERROR','REMOVE_ERROR','POST_ERROR','RESIDUE','NOT_STARTED','INVALID_OWNER'):
            with self.subTest(scenario=scenario),tempfile.TemporaryDirectory(prefix='ci-cleanup-',dir=parent) as temporary:
                trace=Path(temporary)/'trace'
                env=dict(os.environ,SCENARIO=scenario,CID='a'*64,TRACE=trace.as_posix(),SQLPERF_SQL_CONTAINER='sqlperf-synthetic',SQLPERF_CI_OWNER='b'*32)
                if scenario=='NOT_STARTED':env.update(SQLPERF_SQL_CONTAINER='',SQLPERF_CI_OWNER='')
                if scenario=='INVALID_OWNER':env['SQLPERF_CI_OWNER']='foreign'
                result=subprocess.run([bash_executable(),'--noprofile','--norc','-c',MOCK+HELPER.read_text(encoding='utf-8')],env=env,capture_output=True,text=True,timeout=10)
                self.assertEqual(scenario in ('OWN','ABSENT','NOT_STARTED'),result.returncode==0,result.stderr)
                self.assertEqual(scenario in ('OWN','POST_ERROR','RESIDUE'),trace.exists())

    def test_all_legacy_producers_bind_the_new_cleanup(self):
        count=0
        for path in (ROOT/'.github/workflows').glob('*.yml'):
            text=path.read_text(encoding='utf-8-sig')
            if 'run: bash Tests/Runtime/cleanup_ci_container.sh' not in text:continue
            count+=1
            self.assertIn('--label "sqlperf.ci.owner=${owner}"',text)
            self.assertIn('echo "SQLPERF_CI_OWNER=${owner}" >> "${GITHUB_ENV}"',text)
            self.assertIn('if: always()\n        shell: bash\n        timeout-minutes: 3\n        run: bash Tests/Runtime/cleanup_ci_container.sh',text)
        self.assertEqual(11,count)

if __name__=='__main__':unittest.main()
