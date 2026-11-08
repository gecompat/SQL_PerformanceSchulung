#!/usr/bin/env python3
"""SQL-Server-independent self-tests for FWK-006 and FWK-010."""

from __future__ import annotations

import ast
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
import run_demo as run_demo_module  # noqa: E402
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
    demo_id: str = "QRY-001",
    run_token: str = "TEST",
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
            "demo_id": demo_id,
            "run_token": run_token,
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


def test_qry023_contract_loads_in_existing_caller() -> None:
    manifest_path = ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/manifest.proposed.json"
    manifest = run_demo_module.load_manifest(manifest_path)
    assert_equal(manifest.demo_id, "QRY-023", "QRY-023 caller manifest ID")
    assert_equal(manifest.run_token, "LOCAL", "QRY-023 caller RunToken")


def test_invalid_qry023_contract_fails_before_sqlcmd_resolution(base: Path) -> None:
    for name, mutation in (
        ("non_object_root", lambda payload: payload.__setitem__("sqlcmd_input_validation", [])),
        ("validation_timing", lambda payload: payload["sqlcmd_input_validation"].update(
            must_validate_before="TSQL_GUARD"
        )),
        ("unknown_field", lambda payload: payload["sqlcmd_input_validation"].update(unrecognized=True)),
        ("boolean_byte_limit", lambda payload: payload["sqlcmd_input_validation"]["run_token"].update(
            max_bytes=True
        )),
        ("wrong_demo_id", lambda payload: payload["sqlcmd_input_validation"]["demo_id"].update(
            value="QRY-024"
        )),
        ("wrong_target_template", lambda payload: payload["sqlcmd_input_validation"]["target_database"].update(
            template="SQLPERF_LAB_UNBOUND"
        )),
    ):
        path = demo_manifest(base / f"invalid_qry023_contract_{name}", demo_id="QRY-023")
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["sqlcmd_input_validation"] = json.loads(
            json.dumps(run_demo_module.QRY023_SQLCMD_INPUT_VALIDATION)
        )
        mutation(payload)
        write_json(path, payload)
        with patch.object(run_demo_module, "resolve_sqlcmd") as resolve, \
             patch.object(run_demo_module, "run_sqlcmd") as execute:
            try:
                run_demo(
                    manifest_path=path,
                    server="synthetic",
                    auth="integrated",
                    username=None,
                    sqlcmd_path="synthetic-sqlcmd",
                    confirm_isolated_lab=True,
                    allow_red=False,
                    show_output=False,
                )
            except ValueError as exc:
                assert_equal(str(exc), "invalid sqlcmd_input_validation contract",
                             f"invalid QRY-023 {name} contract rejection")
            else:
                raise AssertionError(f"invalid QRY-023 SQLCMD contract variant {name} was accepted")
            resolve.assert_not_called()
            execute.assert_not_called()


def test_qry023_input_contract_rejects_other_demo_id_before_sqlcmd_resolution(base: Path) -> None:
    path = demo_manifest(base / "qry023_contract_on_opt_demo", demo_id="OPT-001")
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["sqlcmd_input_validation"] = json.loads(
        json.dumps(run_demo_module.QRY023_SQLCMD_INPUT_VALIDATION)
    )
    write_json(path, payload)
    with patch.object(run_demo_module, "resolve_sqlcmd") as resolve, \
         patch.object(run_demo_module, "run_sqlcmd") as execute:
        try:
            run_demo(
                manifest_path=path,
                server="synthetic",
                auth="integrated",
                username=None,
                sqlcmd_path="synthetic-sqlcmd",
                confirm_isolated_lab=True,
                allow_red=False,
                show_output=False,
            )
        except ValueError as exc:
            assert_equal(str(exc), "sqlcmd_input_validation requires demo_id QRY-023",
                         "QRY-023 contract scope rejection")
        else:
            raise AssertionError("QRY-023 SQLCMD contract was accepted for OPT-001")
        resolve.assert_not_called()
        execute.assert_not_called()


def test_qry023_contract_rejects_target_name_derivation_drift(base: Path) -> None:
    path = demo_manifest(base / "qry023_target_name_derivation_drift", demo_id="QRY-023")
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["sqlcmd_input_validation"] = json.loads(
        json.dumps(run_demo_module.QRY023_SQLCMD_INPUT_VALIDATION)
    )
    write_json(path, payload)
    with patch.object(run_demo_module, "target_database_name", return_value="SQLPERF_LAB_DRIFTED"), \
         patch.object(run_demo_module, "resolve_sqlcmd") as resolve, \
         patch.object(run_demo_module, "run_sqlcmd") as execute:
        try:
            run_demo(
                manifest_path=path,
                server="synthetic",
                auth="integrated",
                username=None,
                sqlcmd_path="synthetic-sqlcmd",
                confirm_isolated_lab=True,
                allow_red=False,
                show_output=False,
            )
        except ValueError as exc:
            assert_equal(str(exc), "target database does not satisfy sqlcmd_input_validation",
                         "QRY-023 target-name derivation binding")
        else:
            raise AssertionError("QRY-023 target-name derivation drift was accepted")
        resolve.assert_not_called()
        execute.assert_not_called()


def test_hostile_qry023_token_fails_before_sqlcmd_resolution(base: Path) -> None:
    path = demo_manifest(
        base / "hostile_qry023_token",
        demo_id="QRY-023",
        run_token="X'; DROP DATABASE master;--",
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["sqlcmd_input_validation"] = run_demo_module.QRY023_SQLCMD_INPUT_VALIDATION
    write_json(path, payload)
    with patch.object(run_demo_module, "resolve_sqlcmd") as resolve, \
         patch.object(run_demo_module, "run_sqlcmd") as execute:
        try:
            run_demo(
                manifest_path=path,
                server="synthetic",
                auth="integrated",
                username=None,
                sqlcmd_path="synthetic-sqlcmd",
                confirm_isolated_lab=True,
                allow_red=False,
                show_output=False,
            )
        except ValueError as exc:
            assert_equal(str(exc), "invalid run_token", "hostile QRY-023 token rejection")
        else:
            raise AssertionError("hostile QRY-023 RunToken was accepted")
        resolve.assert_not_called()
        execute.assert_not_called()


def test_qry023_contract_rejects_leading_underscore_before_sqlcmd_resolution(base: Path) -> None:
    path = demo_manifest(
        base / "leading_underscore_qry023_token",
        demo_id="QRY-023",
        run_token="_LOCAL",
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["sqlcmd_input_validation"] = run_demo_module.QRY023_SQLCMD_INPUT_VALIDATION
    write_json(path, payload)
    with patch.object(run_demo_module, "resolve_sqlcmd") as resolve, \
         patch.object(run_demo_module, "run_sqlcmd") as execute:
        try:
            run_demo(
                manifest_path=path,
                server="synthetic",
                auth="integrated",
                username=None,
                sqlcmd_path="synthetic-sqlcmd",
                confirm_isolated_lab=True,
                allow_red=False,
                show_output=False,
            )
        except ValueError as exc:
            assert_equal(str(exc), "invalid run_token", "leading underscore QRY-023 token rejection")
        else:
            raise AssertionError("QRY-023 RunToken with leading underscore was accepted")
        resolve.assert_not_called()
        execute.assert_not_called()


def test_qry023_run_token_length_and_ascii_boundaries(base: Path) -> None:
    for name, token in (("minimum", "A"), ("maximum", "A" + "Z" * 19)):
        path = demo_manifest(base / f"valid_{name}_qry023_token", demo_id="QRY-023", run_token=token)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["sqlcmd_input_validation"] = run_demo_module.QRY023_SQLCMD_INPUT_VALIDATION
        write_json(path, payload)
        assert_equal(run_demo_module.load_manifest(path).run_token, token, f"valid {name} QRY-023 token")

    for name, token in (
        ("empty", ""),
        ("too_long", "A" * 21),
        ("non_ascii", "Ä"),
        ("lowercase", "local"),
        ("trailing_space", "A "),
    ):
        path = demo_manifest(base / f"invalid_{name}_qry023_token", demo_id="QRY-023", run_token=token)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["sqlcmd_input_validation"] = run_demo_module.QRY023_SQLCMD_INPUT_VALIDATION
        write_json(path, payload)
        with patch.object(run_demo_module, "resolve_sqlcmd") as resolve, \
             patch.object(run_demo_module, "run_sqlcmd") as execute:
            try:
                run_demo(
                    manifest_path=path,
                    server="synthetic",
                    auth="integrated",
                    username=None,
                    sqlcmd_path="synthetic-sqlcmd",
                    confirm_isolated_lab=True,
                    allow_red=False,
                    show_output=False,
                )
            except ValueError as exc:
                assert_equal(str(exc), "invalid run_token", f"invalid {name} QRY-023 token rejection")
            else:
                raise AssertionError(f"QRY-023 RunToken boundary {name} was accepted")
            resolve.assert_not_called()
            execute.assert_not_called()


def assert_equal(actual: object, expected: object, message: str) -> None:
    if actual != expected:
        raise AssertionError(f"{message}: expected={expected!r}, actual={actual!r}")


def runtime_test_registration_issues(source: str) -> tuple[str, ...]:
    tree = ast.parse(source)
    definitions = [
        node.name for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]
    main_functions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    if len(main_functions) != 1:
        return ("runtime test module must define exactly one main function",)
    main_function = main_functions[0]
    registrations: list[str] = []
    non_direct_call = False

    def test_calls(node: ast.AST) -> list[str]:
        return [
            call.func.id for call in ast.walk(node)
            if isinstance(call, ast.Call)
            and isinstance(call.func, ast.Name)
            and call.func.id.startswith("test_")
        ]

    def collect_direct_calls(statements: list[ast.stmt]) -> None:
        nonlocal non_direct_call
        for statement in statements:
            if isinstance(statement, ast.Expr):
                value = statement.value
                if (
                    isinstance(value, ast.Call)
                    and isinstance(value.func, ast.Name)
                    and value.func.id.startswith("test_")
                ):
                    registrations.append(value.func.id)
                elif test_calls(statement):
                    non_direct_call = True
            elif isinstance(statement, (ast.With, ast.AsyncWith)):
                if any(test_calls(item.context_expr) for item in statement.items):
                    non_direct_call = True
                collect_direct_calls(statement.body)
            elif test_calls(statement):
                non_direct_call = True

    collect_direct_calls(main_function.body)
    issues: list[str] = []
    if non_direct_call:
        issues.append("runtime tests must be direct unconditional main statements")
    if len(definitions) != len(set(definitions)):
        issues.append("runtime test functions must be uniquely defined")
    if len(registrations) != len(set(registrations)):
        issues.append("runtime tests must be registered only once")
    if set(registrations) != set(definitions):
        issues.append("runtime test definitions and registrations must match")
    return tuple(issues)


def test_runtime_test_functions_are_registered_once() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    assert_equal(runtime_test_registration_issues(source), (), "current runtime test registration")

    base = "def test_one(): pass\ndef main():\n    test_one()\n"
    assert_equal(runtime_test_registration_issues(base), (), "complete synthetic test registration")
    assert_equal(
        runtime_test_registration_issues("def test_one(): pass\ndef main(): pass\n"),
        ("runtime test definitions and registrations must match",),
        "missing synthetic test registration",
    )
    assert_equal(
        runtime_test_registration_issues(base.replace("    test_one()", "    test_one()\n    test_one()")),
        ("runtime tests must be registered only once",),
        "duplicate synthetic test registration",
    )
    duplicate_definition = "def test_one(): pass\ndef test_one(): pass\ndef main():\n    test_one()\n"
    assert_equal(
        runtime_test_registration_issues(duplicate_definition),
        ("runtime test functions must be uniquely defined",),
        "duplicate synthetic test definition",
    )
    assert_equal(
        runtime_test_registration_issues("def test_one(): pass\n"),
        ("runtime test module must define exactly one main function",),
        "missing synthetic test entry point",
    )
    duplicate_main = "def test_one(): pass\ndef main(): test_one()\ndef main(): test_one()\n"
    assert_equal(
        runtime_test_registration_issues(duplicate_main),
        ("runtime test module must define exactly one main function",),
        "duplicate synthetic test entry point",
    )
    undefined_registration = "def test_one(): pass\ndef main():\n    test_missing()\n"
    assert_equal(
        runtime_test_registration_issues(undefined_registration),
        ("runtime test definitions and registrations must match",),
        "undefined synthetic test registration",
    )
    nested_unexecuted_call = (
        "def test_one(): pass\ndef main():\n"
        "    def helper():\n        test_one()\n"
    )
    assert_equal(
        runtime_test_registration_issues(nested_unexecuted_call),
        (
            "runtime tests must be direct unconditional main statements",
            "runtime test definitions and registrations must match",
        ),
        "nested helper call is not a main registration",
    )
    conditional_call = (
        "def test_one(): pass\ndef main():\n"
        "    if False:\n        test_one()\n"
    )
    assert_equal(
        runtime_test_registration_issues(conditional_call),
        (
            "runtime tests must be direct unconditional main statements",
            "runtime test definitions and registrations must match",
        ),
        "conditional test call is not an unconditional registration",
    )
    async_test = "async def test_one(): pass\ndef main():\n    test_one()\n"
    assert_equal(
        runtime_test_registration_issues(async_test),
        ("runtime test definitions and registrations must match",),
        "unawaited asynchronous test is not an executed registration",
    )


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
    test_runtime_test_functions_are_registered_once()
    test_collect_process_interrupt()
    test_windows_process_tree_termination()
    test_completed_root_is_never_terminated_by_old_pid()
    test_linux_nested_session_interrupt()
    test_qry023_contract_loads_in_existing_caller()
    with tempfile.TemporaryDirectory(prefix="sqlperf-orchestration-") as temporary:
        base = Path(temporary)
        executable = fake_sqlcmd(base)
        test_invalid_qry023_contract_fails_before_sqlcmd_resolution(base)
        test_hostile_qry023_token_fails_before_sqlcmd_resolution(base)
        test_qry023_input_contract_rejects_other_demo_id_before_sqlcmd_resolution(base)
        test_qry023_contract_rejects_target_name_derivation_drift(base)
        test_qry023_contract_rejects_leading_underscore_before_sqlcmd_resolution(base)
        test_qry023_run_token_length_and_ascii_boundaries(base)
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
