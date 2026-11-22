"""Keep the isolated CON-006 SQLCMD connection on IPv4 loopback."""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests/Runtime"))
import con006_range_pilot


class Con006RunnerLoopbackTests(unittest.TestCase):
    def test_probe_uses_ipv4_loopback_inside_the_owned_container(self):
        target = SimpleNamespace(
            container="sqlperf-con006-range-123",
            sqlcmd_path="/opt/mssql-tools18/bin/sqlcmd",
            child_environment=lambda: {"SQLCMDPASSWORD": "masked"},
        )
        completed = SimpleNamespace(returncode=0, stdout="OK\n", stderr="")
        with patch.object(con006_range_pilot.subprocess, "run", return_value=completed) as run:
            result = con006_range_pilot._sql(target, "master", "SELECT 1")
        command = run.call_args.args[0]
        self.assertEqual(result, "OK\n")
        self.assertEqual(command[command.index("-S") + 1], "127.0.0.1")
        self.assertIn("-e", command)
        self.assertIn("SQLCMDPASSWORD", command)
        self.assertEqual(run.call_args.kwargs["timeout"], 20)


if __name__ == "__main__":
    unittest.main()
