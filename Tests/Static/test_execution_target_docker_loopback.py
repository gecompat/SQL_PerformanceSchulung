"""Container SQL connections use an explicit IPv4 loopback endpoint."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests/Runtime"))
from execution_target import _docker_command, docker_target  # noqa: E402


class DockerTargetLoopbackTests(unittest.TestCase):
    def test_docker_sqlcmd_uses_ipv4_loopback(self):
        target = docker_target(
            container="sqlperf-owned-test",
            sqlcmd_path="/opt/mssql-tools18/bin/sqlcmd",
        )

        command = _docker_command(target, "master")
        server_index = command.index("-S") + 1
        self.assertEqual(command[server_index], "127.0.0.1")


if __name__ == "__main__":
    unittest.main()
