#!/usr/bin/env python3
"""Den tatsächlichen CON-005-Bash-Cleanup mit kontrollierten Dockerantworten prüfen."""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github/workflows/con005-schema-locks.yml'
CID = 'a' * 64
OTHER_CID = 'b' * 64
IMAGE = 'sha256:' + 'c' * 64
NAME = 'sqlperf-con005-synthetic'
OWNER = 'con005-synthetic'


def cleanup_script() -> str:
    text = WORKFLOW.read_text(encoding='utf-8-sig')
    marker = '      - name: Eigene Instanz entfernen und Abwesenheit prüfen\n'
    if text.count(marker) != 1:
        raise RuntimeError('Eindeutiger Cleanupschritt fehlt')
    body = text.split(marker)[1].split('        run: |\n', 1)[1]
    lines = []
    for line in body.splitlines():
        if line and not line.startswith('          '):
            raise RuntimeError('Unbekannte Cleanupblockgrenze')
        lines.append(line[10:])
    return '\n'.join(lines)


def bash_executable() -> str:
    if os.name == 'nt':
        git = shutil.which('git')
        if git:
            candidate = Path(git).resolve().parent.parent / 'bin/bash.exe'
            if candidate.is_file():
                return str(candidate)
    found = shutil.which('bash')
    if not found:
        raise RuntimeError('Bash für die unveränderte Workflowgegenprobe fehlt')
    return found


# Die Funktion ersetzt ausschließlich Docker. Der Workflowblock selbst bleibt
# unverändert, einschließlich set -e und der tatsächlichen Absenzprüfungen.
MOCK = r'''
mock_removed=0
docker() {
  case "$1 $2" in
    "container ls")
      if [ "$SCENARIO" = DAEMON_DOWN ]; then return 125; fi
      if [ "$mock_removed" = 1 ]; then
        if [ "$SCENARIO" = POST_REMOVE_ERROR ]; then return 125; fi
        if [ "$SCENARIO" = LEFTOVER ]; then printf '%s\n' "$TEST_CID"; fi
        return 0
      fi
      if [ "$SCENARIO" = ALREADY_ABSENT ] || [ "$SCENARIO" = MISSING_CID ]; then return 0; fi
      if [ "$SCENARIO" = NOT_CREATED ]; then return 0; fi
      if [[ "$*" = *'name='* ]] && [ "$SCENARIO" = FOREIGN_NAME ]; then printf '%s\n' "$TEST_OTHER"; return 0; fi
      if [[ "$*" = *'label='* ]] && [ "$SCENARIO" = EXTRA_OWNER ]; then printf '%s\n%s\n' "$TEST_CID" "$TEST_OTHER"; return 0; fi
      printf '%s\n' "$TEST_CID"
      ;;
    "inspect -f")
      if [ "$SCENARIO" = INSPECT_ERROR ]; then return 125; fi
      if [ "$SCENARIO" = WRONG_OWNER ]; then printf '/%s|foreign-owner|%s\n' "$SQLPERF_SQL_CONTAINER" "$SQLPERF_IMAGE_ID"; return 0; fi
      if [ "$SCENARIO" = WRONG_IMAGE ]; then printf '/%s|%s|sha256:foreign\n' "$SQLPERF_SQL_CONTAINER" "$SQLPERF_OWNER"; return 0; fi
      printf '/%s|%s|%s\n' "$SQLPERF_SQL_CONTAINER" "$SQLPERF_OWNER" "$SQLPERF_IMAGE_ID"
      ;;
    "rm --force")
      if [ "$SCENARIO" = REMOVE_ERROR ]; then return 125; fi
      printf 'REMOVE\n' >> "$TEST_TRACE"
      mock_removed=1
      ;;
    *) return 126 ;;
  esac
}
'''


class ContainerCleanupTests(unittest.TestCase):
    def run_case(self, scenario: str) -> tuple[subprocess.CompletedProcess[str], str]:
        temp_root = ROOT / 'Runtime/Temp'
        temp_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='con005-cleanup-', dir=temp_root) as temporary:
            path = Path(temporary).resolve()
            self.assertTrue(path.is_relative_to(temp_root.resolve()))
            cidfile, trace = path / 'own.cid', path / 'trace.txt'
            if scenario != 'MISSING_CID':
                cidfile.write_text(CID, encoding='ascii')
            environment = os.environ.copy()
            environment.update(SCENARIO=scenario, SQLPERF_SQL_CONTAINER=NAME, SQLPERF_OWNER=OWNER,
                               SQLPERF_SQL_CIDFILE=cidfile.as_posix(), SQLPERF_IMAGE_ID=IMAGE,
                               SQLPERF_CREATE_ATTEMPTED='0' if scenario == 'NOT_CREATED' else '1',
                               TEST_CID=CID, TEST_OTHER=OTHER_CID, TEST_TRACE=trace.as_posix())
            result = subprocess.run([bash_executable(), '--noprofile', '--norc', '-c', MOCK + cleanup_script()],
                                    capture_output=True, text=True, encoding='utf-8', errors='replace',
                                    env=environment, timeout=15)
            return result, trace.read_text(encoding='ascii') if trace.exists() else ''

    def test_own_resource_is_removed_and_absence_is_checked(self):
        result, trace = self.run_case('OWN')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('CON005_CONTAINER_CLEANUP|PASS|ABSENT', result.stdout)
        self.assertEqual('REMOVE\n', trace)

    def test_known_absence_does_not_delete_another_resource(self):
        result, trace = self.run_case('ALREADY_ABSENT')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('PASS|ABSENT', result.stdout)
        self.assertEqual('', trace)

    def test_pre_create_failure_is_not_reported_as_executed_cleanup(self):
        result, trace = self.run_case('NOT_CREATED')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('NOT_CREATED', result.stdout)
        self.assertNotIn('PASS|ABSENT', result.stdout)
        self.assertEqual('', trace)

    def test_unknown_identity_and_docker_errors_never_become_success(self):
        scenarios = ('DAEMON_DOWN', 'MISSING_CID', 'FOREIGN_NAME', 'EXTRA_OWNER',
                     'WRONG_OWNER', 'WRONG_IMAGE', 'INSPECT_ERROR', 'REMOVE_ERROR',
                     'POST_REMOVE_ERROR', 'LEFTOVER')
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                result, trace = self.run_case(scenario)
                self.assertNotEqual(0, result.returncode)
                self.assertNotIn('PASS|ABSENT', result.stdout)
                if scenario not in ('POST_REMOVE_ERROR', 'LEFTOVER'):
                    self.assertEqual('', trace)

    def test_startup_test_and_cleanup_keep_a_job_reserve(self):
        text = WORKFLOW.read_text(encoding='utf-8-sig')
        self.assertIn('timeout --signal=TERM --kill-after=30s 600s python Tests/Runtime/run_con005.py', text)
        self.assertIn('timeout-minutes: 30', text)
        self.assertIn('timeout-minutes: 10', text)
        self.assertIn('timeout-minutes: 12', text)
        self.assertIn('timeout-minutes: 3', text)
        self.assertIn('-b -l 5 -t 5 -Q', text)
        self.assertIn('--cidfile "${cidfile}"', text)
        self.assertRegex(text, re.escape('-e MSSQL_SA_PASSWORD -d "${image_id}"'))


if __name__ == '__main__':
    unittest.main()
