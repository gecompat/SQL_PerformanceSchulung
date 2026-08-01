#!/usr/bin/env python3
"""Run QRY-013 twice against one SQL Server execution target."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "Tests" / "Runtime"
FRAMEWORK_TOOLS = ROOT / "Demos" / "00_Framework" / "Tools"

sys.path.insert(0, str(RUNTIME))
import execution_target  # noqa: E402
from execution_target import ExecutionTarget, ExecutionTargetError  # noqa: E402

DEMO_ID = "QRY-013"
MANIFEST = ROOT / "Demos" / "05_Query_Patterns" / "QRY-013_Client_Session_Context" / "manifest.json"
SUMMARY = re.compile(r"^SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)$", re.MULTILINE)


class Qry013Failure(RuntimeError):
    pass


def target_database() -> str:
    return f"SQLPERF_LAB_{DEMO_ID.replace('-', '')}_LOCAL"


def assert_database_absent(target: ExecutionTarget) -> None:
    database = target_database()
    output = execution_target.run_sql(
        target,
        database="master",
        sql_text=(
            f"IF DB_ID(N'{database}') IS NOT NULL "
            "THROW 51004, 'FAIL_CLEANUP: QRY-013-Testdatenbank ist nach dem Harness-Lauf noch vorhanden.', 1; "
            "SELECT N'ABSENT';"
        ),
        timeout_seconds=30,
    )
    if "ABSENT" not in output:
        raise Qry013Failure(f"{DEMO_ID}: cleanup verification did not return ABSENT")


def run_demo(*, target: ExecutionTarget, repetition: int) -> None:
    if not MANIFEST.is_file():
        raise Qry013Failure(f"{DEMO_ID}: manifest missing")

    command = [
        sys.executable,
        str(FRAMEWORK_TOOLS / "run_demo.py"),
        str(MANIFEST),
        *target.connection_arguments(),
        "--show-output",
    ]
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=target.child_environment(),
        timeout=900,
    )
    combined = "\n".join(part for part in (result.stdout, result.stderr) if part)
    summaries = SUMMARY.findall(combined)
    final_summary = summaries[-1] if summaries else None

    if result.returncode != 0 or final_summary != ("PASS", "OK"):
        diagnostic = execution_target.redact(combined[-12000:])
        raise Qry013Failure(
            f"{DEMO_ID} repetition {repetition}: harness failed; "
            f"returncode={result.returncode}; summary={final_summary}; diagnostic={diagnostic}"
        )

    variance = sum(1 for outcome, code in summaries if outcome == "WARN")
    assert_database_absent(target)
    print(f"QRY013_STAGE|{DEMO_ID}|RUN_{repetition}|PASS|OK|warnings={variance}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run QRY-013 twice.")
    parser.add_argument(
        "--target",
        choices=execution_target.TARGET_KINDS,
        default=execution_target.DOCKER,
        help="docker: wegwerfbare Container-Instanz; host: vorhandene Instanz",
    )
    parser.add_argument("--container", help="nur fuer --target docker")
    parser.add_argument("--server", default="localhost", help="nur fuer --target host")
    parser.add_argument(
        "--username",
        default="sa",
        help="SQL-Anmeldename; leer bedeutet Windows-Authentifizierung",
    )
    parser.add_argument(
        "--confirm-disposable-instance",
        action="store_true",
        help="bestaetigt, dass die Zielinstanz eine Wegwerfinstanz ist",
    )
    parser.add_argument(
        "--expected-major",
        type=int,
        help="erwartete Hauptversion; ohne Angabe wird die Instanz ausgelesen",
    )
    args = parser.parse_args()

    major = args.expected_major
    try:
        if args.target == execution_target.DOCKER:
            target = execution_target.docker_target(container=args.container or "")
        else:
            target = execution_target.host_target(
                server=args.server,
                username=args.username or None,
            )
        execution_target.require_disposable_instance(
            target, args.confirm_disposable_instance
        )
        major = execution_target.verify_engine(
            target, expected_major=args.expected_major
        )
        print(f"QRY013_STAGE|ENGINE_{major}|IDENTITY|PASS|OK")
        for repetition in (1, 2):
            run_demo(target=target, repetition=repetition)
        print(
            f"QRY013_SUMMARY|PASS|OK|major={major}; demos=1; repetitions=2; "
            f"target={target.kind}"
        )
        return 0
    except (
        ExecutionTargetError,
        Qry013Failure,
        OSError,
        subprocess.TimeoutExpired,
        ValueError,
    ) as exc:
        message = execution_target.redact(str(exc))
        print(
            f"QRY013_SUMMARY|FAIL|FAIL_EXECUTION|major={major}; "
            f"target={args.target}; {message}"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
