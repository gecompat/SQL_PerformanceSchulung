#!/usr/bin/env python3
"""SQL-Server-independent self-tests for FWK-006 and FWK-010."""

from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "Demos" / "00_Framework" / "Tools"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(ROOT / "Tests" / "Runtime"))

from execution_target import DOCKER, ExecutionTarget  # noqa: E402
from orchestrate_sessions import run_manifest as run_session_manifest  # noqa: E402
from run_demo import run_demo  # noqa: E402
from sqlcmd_process import run_sqlcmd  # noqa: E402
import sqlcmd_process  # noqa: E402


FAKE_SQLCMD = r'''#!/usr/bin/env python3
import pathlib
import sys
import time

args = sys.argv[1:]
try:
    script = pathlib.Path(args[args.index("-i") + 1])
except (ValueError, IndexError):
    print("missing -i", file=sys.stderr)
    raise SystemExit(2)

name = script.stem.lower()
if "unicode" in name:
    print("Prüfung gültig: \ufffd")
    print("Größe geprüft: \ufffd", file=sys.stderr)
if "timeout" in name:
    time.sleep(5)
    print("SQLPERF_SUMMARY|PASS|OK")
    raise SystemExit(0)
if "cleanup_fail" in name or "session_fail" in name or "execution_fail" in name:
    print("synthetic execution failure", file=sys.stderr)
    raise SystemExit(1)
if "preflight_skip" in name or "optional_skip" in name:
    print("SQLPERF_SUMMARY|SKIP|SKIP_CONFIGURATION")
    raise SystemExit(0)
if "no_summary" in name:
    print("synthetic output without summary")
    raise SystemExit(0)
print("SQLPERF_SUMMARY|PASS|OK")
raise SystemExit(0)
'''


def write(path: Path, content: str = "-- synthetic\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def fake_sqlcmd(root: Path) -> Path:
    path = root / "fake_sqlcmd.py"
    path.write_text(FAKE_SQLCMD, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def session_manifest(root: Path, names: list[str], timeout: int = 3) -> Path:
    sessions = []
    for index, name in enumerate(names, start=1):
        filename = f"{index:02d}_{name}.sql"
        write(root / filename)
        sessions.append(
            {
                "id": f"S{index}",
                "script": filename,
                "launch_delay_ms": 0,
            }
        )
    return write_json(
        root / "sessions.json",
        {
            "contract_version": "1.0",
            "demo_id": "CON-004",
            "run_token": "TEST",
            "timeout_seconds": timeout,
            "abort_on_first_failure": True,
            "sessions": sessions,
        },
    )


def demo_manifest(
    root: Path,
    *,
    preflight: str = "preflight_pass",
    demo: str = "demo_pass",
    cleanup: str = "cleanup_pass",
    safety: str = "GREEN",
    optional: str | None = None,
) -> Path:
    for name in (preflight, "setup_pass", demo, cleanup):
        write(root / f"{name}.sql")

    phases = [
        {
            "id": "PREFLIGHT",
            "kind": "sql",
            "script": f"{preflight}.sql",
            "database": "master",
            "required": True,
            "require_summary": True,
        },
        {
            "id": "SETUP",
            "kind": "sql",
            "script": "setup_pass.sql",
            "database": "target",
            "required": True,
            "require_summary": True,
        },
    ]
    if optional is not None:
        write(root / f"{optional}.sql")
        phases.append(
            {
                "id": "OPTIONAL_EVIDENCE",
                "kind": "sql",
                "script": f"{optional}.sql",
                "database": "target",
                "required": False,
                "require_summary": True,
            }
        )
    phases.append(
        {
            "id": "DEMONSTRATION",
            "kind": "sql",
            "script": f"{demo}.sql",
            "database": "target",
            "required": True,
            "require_summary": True,
        }
    )

    return write_json(
        root / "demo.json",
        {
            "contract_version": "1.0",
            "demo_id": "QRY-001",
            "run_token": "TEST",
            "safety_level": safety,
            "timeout_seconds": 4,
            "cleanup_timeout_seconds": 2,
            "phases": phases,
            "cleanup": {
                "id": "CLEANUP",
                "kind": "sql",
                "script": f"{cleanup}.sql",
                "database": "target",
                "required": True,
                "require_summary": True,
            },
        },
    )


def assert_equal(actual: object, expected: object, message: str) -> None:
    if actual != expected:
        raise AssertionError(f"{message}: expected={expected!r}, actual={actual!r}")


def test_sessions_pass(base: Path, executable: Path) -> None:
    result = run_session_manifest(
        manifest_path=session_manifest(base / "sessions_pass", ["session_pass", "session_pass"]),
        server="synthetic",
        database="SQLPERF_LAB_CON004_TEST",
        auth="integrated",
        username=None,
        sqlcmd_path=str(executable),
        show_output=False,
    )
    assert_equal((result.outcome, result.code), ("PASS", "OK"), "multi-session pass")


def test_sessions_fail(base: Path, executable: Path) -> None:
    result = run_session_manifest(
        manifest_path=session_manifest(base / "sessions_fail", ["session_fail", "timeout"]),
        server="synthetic",
        database="SQLPERF_LAB_CON004_TEST",
        auth="integrated",
        username=None,
        sqlcmd_path=str(executable),
        show_output=False,
    )
    assert_equal((result.outcome, result.code), ("FAIL", "FAIL_EXECUTION"), "multi-session fail-fast")


def test_sessions_timeout(base: Path, executable: Path) -> None:
    result = run_session_manifest(
        manifest_path=session_manifest(base / "sessions_timeout", ["timeout"], timeout=1),
        server="synthetic",
        database="SQLPERF_LAB_CON004_TEST",
        auth="integrated",
        username=None,
        sqlcmd_path=str(executable),
        show_output=False,
    )
    assert_equal((result.outcome, result.code), ("FAIL", "FAIL_TIMEOUT"), "multi-session timeout")


def run_harness(manifest: Path, executable: Path, *, confirm: bool = False):
    return run_demo(
        manifest_path=manifest,
        server="synthetic",
        auth="integrated",
        username=None,
        sqlcmd_path=str(executable),
        confirm_isolated_lab=confirm,
        allow_red=False,
        show_output=False,
    )


def test_harness_pass(base: Path, executable: Path) -> None:
    result = run_harness(demo_manifest(base / "harness_pass"), executable)
    assert_equal((result.outcome, result.code), ("PASS", "OK"), "harness pass")
    assert_equal(result.phases[-1].phase_id, "CLEANUP", "cleanup executed")


def test_harness_cleanup_failure(base: Path, executable: Path) -> None:
    result = run_harness(demo_manifest(base / "cleanup_failure", cleanup="cleanup_fail"), executable)
    assert_equal((result.outcome, result.code), ("FAIL", "FAIL_CLEANUP"), "cleanup priority")
    result = run_harness(demo_manifest(base / "double_failure", demo="execution_fail", cleanup="cleanup_fail"), executable)
    assert_equal((result.outcome, result.code), ("FAIL", "FAIL_CLEANUP"), "cleanup priority after execution failure")
    assert_equal((result.phases[-2].outcome, result.phases[-2].code), ("FAIL", "FAIL_EXECUTION"), "original execution error preserved")


def test_harness_preflight_skip(base: Path, executable: Path) -> None:
    result = run_harness(demo_manifest(base / "preflight_skip", preflight="preflight_skip"), executable)
    assert_equal((result.outcome, result.code), ("SKIP", "SKIP_CONFIGURATION"), "preflight skip")
    assert_equal(len(result.phases), 1, "no state-changing phase after required skip")


def test_harness_optional_skip(base: Path, executable: Path) -> None:
    result = run_harness(demo_manifest(base / "optional_skip", optional="optional_skip"), executable)
    assert_equal((result.outcome, result.code), ("WARN", "WARN_OPTIONAL_EVIDENCE_SKIPPED"), "optional evidence skip")
    assert_equal(result.phases[-1].phase_id, "CLEANUP", "cleanup after optional skip")


def test_harness_yellow_confirmation(base: Path, executable: Path) -> None:
    manifest = demo_manifest(base / "yellow", safety="YELLOW")
    denied = run_harness(manifest, executable, confirm=False)
    assert_equal((denied.outcome, denied.code), ("FAIL", "FAIL_SAFETY"), "yellow without confirmation")
    allowed = run_harness(manifest, executable, confirm=True)
    assert_equal((allowed.outcome, allowed.code), ("PASS", "OK"), "yellow with confirmation")


def test_utf8_transport_from_cp1252(base: Path, executable: Path) -> None:
    """UTF-8-Pipes behalten SQL-Ausgabe und Status trotz cp1252-Ausgangsumgebung."""

    script = write(base / "unicode_pass.sql")
    environment = {**os.environ, "PYTHONIOENCODING": "cp1252"}
    result = run_sqlcmd(
        [sys.executable, str(executable), "-i", str(script)],
        timeout_seconds=5,
        environment=environment,
    )
    assert_equal(result.returncode, 0, "Python-Shim unter cp1252")
    assert_equal(result.stdout, "Prüfung gültig: \ufffd\nSQLPERF_SUMMARY|PASS|OK\n", "UTF-8 stdout")
    assert_equal(result.stderr, "Größe geprüft: \ufffd\n", "UTF-8 stderr")
    assert_equal(environment["PYTHONIOENCODING"], "cp1252", "Aufruferumgebung bleibt unverändert")

    target = ExecutionTarget(
        kind=DOCKER,
        server="synthetic",
        auth="integrated",
        username=None,
        shim=executable,
        sqlcmd_path=str(executable),
        container="synthetic",
    )
    for demo, expected_exit, summary in (
        ("unicode_pass", 0, "PASS|OK"),
        ("unicode_execution_fail", 2, "FAIL|FAIL_EXECUTION"),
        ("unicode_no_summary", 2, "FAIL|FAIL_CONTRACT"),
    ):
        manifest = demo_manifest(base / demo, demo=demo)
        with patch.dict(os.environ, {"PYTHONIOENCODING": "cp1252"}):
            child_environment = target.child_environment()
        result = subprocess.run(
            [sys.executable, str(TOOLS / "run_demo.py"), str(manifest),
             *target.connection_arguments(), "--show-output"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            env=child_environment,
            timeout=10,
            check=False,
        )
        assert_equal(result.returncode, expected_exit, f"Harness-Exit: {demo}")
        assert_equal(f"SQLPERF_SUMMARY|{summary}" in result.stdout.splitlines(), True, f"Harness-Summary: {demo}")
        assert_equal("[DEMONSTRATION:stdout] Prüfung gültig: \ufffd" in result.stdout, True, "--show-output stdout")
        assert_equal("[DEMONSTRATION:stderr] Größe geprüft: \ufffd" in result.stderr, True, "--show-output stderr")
        assert_equal("CLEANUP: PASS/OK" in result.stdout, True, "Cleanup nach Unicode-Ausgabe")


def test_collect_process_interrupt() -> None:
    """Interrupt erst nach Terminierung und bounded Reap erneut auslösen."""
    for interruption in (KeyboardInterrupt(), SystemExit(7), RuntimeError("synthetic interruption")):
        events = []
        process = Mock()
        def communicate(*, timeout):
            events.append(("communicate", timeout))
            if len(events) == 1:
                raise interruption
            return "", ""
        process.communicate.side_effect = communicate
        with patch.object(sqlcmd_process, "_terminate_process_tree", side_effect=lambda value: events.append(("terminate", value))):
            try:
                sqlcmd_process.collect_process(process, ["synthetic"], timeout_seconds=10)
            except BaseException as exc:
                assert_equal(exc is interruption, True, "ursprünglicher Interrupt bleibt erhalten")
            else:
                raise AssertionError("Interrupt wurde verschluckt")
        assert_equal(events, [("communicate", 10), ("terminate", process), ("communicate", 5)], "Terminierung vor Reap und Wiederwurf")


def test_windows_process_tree_termination() -> None:
    """Taskkill beendet unter Windows den Baum und bleibt zeitlich begrenzt."""
    process = Mock(pid=12345)
    process.poll.side_effect = [None, 0]
    with patch.object(sqlcmd_process.os, "name", "nt"), \
         patch.object(sqlcmd_process.subprocess, "CREATE_NO_WINDOW", 0x08000000, create=True), \
         patch.object(sqlcmd_process.subprocess, "run") as run:
        sqlcmd_process._terminate_process_tree(process)
        assert_equal(run.call_args.args[0], ["taskkill", "/PID", "12345", "/T", "/F"], "Windows-Baumabbruch")
        assert_equal(run.call_args.kwargs["timeout"], 5, "Taskkill-Budget")
        process.wait.assert_called_once_with(timeout=2)
    process.poll.side_effect = None
    process.poll.return_value = None
    with patch.object(sqlcmd_process.os, "name", "nt"), \
         patch.object(sqlcmd_process.subprocess, "CREATE_NO_WINDOW", 0x08000000, create=True), \
         patch.object(sqlcmd_process.subprocess, "run", side_effect=subprocess.TimeoutExpired("taskkill", 5)):
        sqlcmd_process._terminate_process_tree(process)
        process.kill.assert_called_once()


def test_completed_root_is_never_terminated_by_old_pid() -> None:
    """Nach Reap darf eine wiederverwendete PID kein Terminierungsziel sein."""
    for platform_name in ("nt", "posix"):
        process = Mock(pid=12345)
        process.poll.return_value = 0
        with patch.object(sqlcmd_process.os, "name", platform_name), \
             patch.object(sqlcmd_process.subprocess, "run") as run, \
             patch.object(sqlcmd_process.os, "killpg", create=True) as killpg, \
             patch.object(sqlcmd_process.os, "kill") as kill:
            sqlcmd_process._terminate_process_tree(process)
            run.assert_not_called()
            killpg.assert_not_called()
            kill.assert_not_called()
            process.kill.assert_not_called()


def test_linux_nested_session_interrupt() -> None:
    """Ein reales Kind mit eigener Session darf nach Interrupt nicht weiterlaufen."""
    if not sys.platform.startswith("linux"):
        return
    child_code = "import time; time.sleep(30)"
    parent_code = (
        "import subprocess,sys,time; "
        f"child=subprocess.Popen([sys.executable,'-c',{child_code!r}],start_new_session=True); "
        "print(child.pid,flush=True); time.sleep(30)"
    )
    process = sqlcmd_process.start_sqlcmd([sys.executable, "-c", parent_code])
    child_pid = None
    child_identity = None
    try:
        import select
        if not select.select([process.stdout], [], [], 5)[0]:
            raise AssertionError("Kind meldet seine PID nicht innerhalb des Startbudgets")
        child_pid = int(process.stdout.readline().strip())
        child_identity = sqlcmd_process._linux_process_identity(child_pid)
        original_communicate = process.communicate
        calls = 0
        def interrupted_communicate(*, timeout):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise KeyboardInterrupt()
            return original_communicate(timeout=timeout)
        with patch.object(process, "communicate", side_effect=interrupted_communicate):
            try:
                sqlcmd_process.collect_process(process, [sys.executable, "-c", parent_code], timeout_seconds=5)
            except KeyboardInterrupt:
                pass
            else:
                raise AssertionError("Interrupt fehlt")
        assert_equal(process.poll() is not None, True, "Parent vor Rückgabe beendet und reap")
        # Ein bereits beendetes, noch nicht durch PID 1 reaptes Kind kann Zombie sein.
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            try:
                state = Path(f"/proc/{child_pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
            except OSError:
                break
            if state == "Z":
                break
            time.sleep(0.01)
        else:
            raise AssertionError("Kind mit eigener Session läuft nach Interrupt weiter")
    finally:
        sqlcmd_process._terminate_process_tree(process)
        if child_pid is not None and child_identity is not None and sqlcmd_process._linux_process_identity(child_pid) == child_identity:
            try:
                os.kill(child_pid, 9)
            except ProcessLookupError:
                pass
        process.communicate(timeout=5)


def main() -> int:
    test_collect_process_interrupt()
    test_windows_process_tree_termination()
    test_completed_root_is_never_terminated_by_old_pid()
    test_linux_nested_session_interrupt()
    with tempfile.TemporaryDirectory(prefix="sqlperf-orchestration-") as temporary:
        base = Path(temporary)
        executable = fake_sqlcmd(base)
        test_sessions_pass(base, executable)
        test_sessions_fail(base, executable)
        test_sessions_timeout(base, executable)
        test_harness_pass(base, executable)
        test_harness_cleanup_failure(base, executable)
        test_harness_preflight_skip(base, executable)
        test_harness_optional_skip(base, executable)
        test_harness_yellow_confirmation(base, executable)
        test_utf8_transport_from_cp1252(base, executable)

    print("orchestration-runtime: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
