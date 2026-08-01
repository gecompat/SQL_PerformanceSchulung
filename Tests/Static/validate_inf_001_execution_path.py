#!/usr/bin/env python3
"""Static validation of the INF-001 execution path.

The validator confirms that the runtime runners expose a selectable execution
target, that the how-to covers the mandatory content from section 13.4 of the
master plan and that the runner topology stays consistent with the workflows.

Standard library only, so the check runs without a SQL Server runtime.
"""

from __future__ import annotations

import ast
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "Tests" / "Runtime"
WORKFLOWS = ROOT / ".github" / "workflows"

EXECUTION_TARGET = RUNTIME / "execution_target.py"
HOST_SHIM = RUNTIME / "host_sqlcmd_target.py"
DOCKER_SHIM = RUNTIME / "docker_sqlcmd_proxy.py"

HOWTO = ROOT / "Documentation" / "HowTo" / "LOCAL_TEST_ENVIRONMENT.md"
TOPOLOGY = ROOT / "Documentation" / "Architecture" / "RUNNER_TOPOLOGY.md"
DESIGN = (
    ROOT
    / "Documentation"
    / "Project_Planning"
    / "INF_001_EXECUTION_TARGET_DESIGN.md"
)

# Demo runners that must support both execution targets.
DEMO_RUNNERS = {
    "run_gate_b_pilots.py": "GATE_B_SUMMARY",
    "run_adv008_opt015_opt016.py": "ADV008_SUMMARY",
    "run_adv008_qry013.py": "QRY013_SUMMARY",
}

REQUIRED_RUNNER_OPTIONS = (
    "--target",
    "--container",
    "--server",
    "--username",
    "--confirm-disposable-instance",
)

# Public API that the runners rely on.
REQUIRED_TARGET_FUNCTIONS = (
    "container_sqlcmd",
    "docker_target",
    "host_target",
    "require_disposable_instance",
    "run_sql",
    "verify_engine",
    "redact",
)

# Mandatory how-to content, master plan section 13.4.
HOWTO_TOPICS = {
    "Auswahl des Ausführungspfads": ("## 1. Auswahl des Ausführungspfads",),
    "Mindestvoraussetzungen": ("## 2. Mindestvoraussetzungen",),
    "Anmeldedaten ohne Repository-Secrets": (
        "SQLCMDPASSWORD",
        "Repository-Secrets",
    ),
    "Healthcheck und Versionserkennung": (
        "Healthcheck",
        "ProductMajorVersion",
    ),
    "Lebenszyklus der Testdatenbank": ("SQLPERF_LAB_",),
    "Demo-Preflights": ("00_Preflight.sql",),
    "Cleanup und Recovery": ("Recovery",),
    "Versionsunterschiede": ("2019", "2022", "2025"),
    "Demos mit Zusatzinfrastruktur": ("Zusatzbedarf",),
}

TARGET_NAMES = ("local-host", "github-hosted", "key18-perf")

RUNNER_VARIABLE = "SQLPERF_RUNTIME_RUNNER"
RUNTIME_WORKFLOWS = (
    "framework-sql-matrix.yml",
    "gate-b-pilots.yml",
    "adv008-opt015-opt016.yml",
    "adv008-qry013.yml",
)

PASSWORD_ARGUMENT = re.compile(r"[\"']-P[\"']|--password")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check_files_exist(findings: list[str]) -> None:
    for path in (
        EXECUTION_TARGET,
        HOST_SHIM,
        DOCKER_SHIM,
        HOWTO,
        TOPOLOGY,
        DESIGN,
    ):
        if not path.is_file():
            findings.append(f"{rel(path)}: required file missing")


def _check_execution_target(findings: list[str]) -> None:
    if not EXECUTION_TARGET.is_file():
        return
    text = read(EXECUTION_TARGET)
    try:
        tree = ast.parse(text, filename=rel(EXECUTION_TARGET))
    except SyntaxError as exc:
        findings.append(f"{rel(EXECUTION_TARGET)}:{exc.lineno}: {exc.msg}")
        return

    defined = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    for name in REQUIRED_TARGET_FUNCTIONS:
        if name not in defined:
            findings.append(
                f"{rel(EXECUTION_TARGET)}: missing public function {name}()"
            )

    for constant in ('DOCKER = "docker"', 'HOST = "host"'):
        if constant not in text:
            findings.append(
                f"{rel(EXECUTION_TARGET)}: missing target constant {constant}"
            )

    if PASSWORD_ARGUMENT.search(text):
        findings.append(
            f"{rel(EXECUTION_TARGET)}: password must not be placed on the "
            "command line"
        )
    if "SQLCMDPASSWORD" not in text:
        findings.append(
            f"{rel(EXECUTION_TARGET)}: password handover via SQLCMDPASSWORD "
            "is not documented in code"
        )


def _check_host_shim(findings: list[str]) -> None:
    if not HOST_SHIM.is_file():
        return
    text = read(HOST_SHIM)
    try:
        ast.parse(text, filename=rel(HOST_SHIM))
    except SyntaxError as exc:
        findings.append(f"{rel(HOST_SHIM)}:{exc.lineno}: {exc.msg}")
        return

    if "SQLPERF_HOST_TRUST_SERVER_CERTIFICATE" not in text:
        findings.append(
            f"{rel(HOST_SHIM)}: certificate trust must stay an explicit opt-in"
        )
    if 'command.append("-C")' not in text:
        findings.append(
            f"{rel(HOST_SHIM)}: certificate trust argument is not applied"
        )
    if PASSWORD_ARGUMENT.search(text):
        findings.append(
            f"{rel(HOST_SHIM)}: password must not be placed on the command line"
        )


def _check_demo_runners(findings: list[str]) -> None:
    for filename, summary_prefix in DEMO_RUNNERS.items():
        path = RUNTIME / filename
        if not path.is_file():
            findings.append(f"{rel(path)}: required runner missing")
            continue
        text = read(path)
        try:
            ast.parse(text, filename=rel(path))
        except SyntaxError as exc:
            findings.append(f"{rel(path)}:{exc.lineno}: {exc.msg}")
            continue

        for option in REQUIRED_RUNNER_OPTIONS:
            if f'"{option}"' not in text:
                findings.append(f"{rel(path)}: missing option {option}")
        if "import execution_target" not in text:
            findings.append(f"{rel(path)}: does not use the execution target module")
        if "docker exec" in text:
            findings.append(
                f"{rel(path)}: container binding must stay in the execution "
                "target module"
            )
        if f"{summary_prefix}|PASS" not in text:
            findings.append(f"{rel(path)}: summary prefix {summary_prefix} changed")
        if "target={target.kind}" not in text:
            findings.append(
                f"{rel(path)}: summary line does not carry the execution target"
            )


def _check_howto(findings: list[str]) -> None:
    if not HOWTO.is_file():
        return
    text = read(HOWTO)
    for topic, markers in HOWTO_TOPICS.items():
        missing = [marker for marker in markers if marker not in text]
        if missing:
            findings.append(
                f"{rel(HOWTO)}: mandatory topic not covered: {topic} "
                f"(missing: {', '.join(missing)})"
            )


def _check_topology(findings: list[str]) -> None:
    if not TOPOLOGY.is_file():
        return
    text = read(TOPOLOGY)
    for marker in ("Key18_Perf", RUNNER_VARIABLE, *TARGET_NAMES):
        if marker not in text:
            findings.append(f"{rel(TOPOLOGY)}: missing statement about {marker}")


def _check_design(findings: list[str]) -> None:
    if not DESIGN.is_file():
        return
    text = read(DESIGN)
    for name in TARGET_NAMES:
        if name not in text:
            findings.append(f"{rel(DESIGN)}: execution target {name} not described")


def _check_workflows(findings: list[str]) -> None:
    expected = f"${{{{ vars.{RUNNER_VARIABLE} || 'ubuntu-latest' }}}}"
    for filename in RUNTIME_WORKFLOWS:
        path = WORKFLOWS / filename
        if not path.is_file():
            findings.append(f"{rel(path)}: required workflow missing")
            continue
        text = read(path)
        if expected not in text:
            findings.append(
                f"{rel(path)}: runtime job does not select the runner through "
                f"{RUNNER_VARIABLE}"
            )

    for filename, _ in DEMO_RUNNERS.items():
        stem = filename.removesuffix(".py")
        matches = [
            path
            for path in WORKFLOWS.glob("*.yml")
            if f"Tests/Runtime/{filename}" in read(path)
        ]
        if not matches:
            findings.append(f"{stem}: no workflow invokes the runner")
            continue
        for path in matches:
            text = read(path)
            if f"Tests/Runtime/{filename} \\" in text and "--target docker" not in text:
                findings.append(
                    f"{rel(path)}: runner invocation does not name the execution target"
                )
            for dependency in ("execution_target.py", "host_sqlcmd_target.py"):
                if f"'Tests/Runtime/{dependency}'" not in text:
                    findings.append(
                        f"{rel(path)}: path filter misses Tests/Runtime/{dependency}"
                    )


def main() -> int:
    findings: list[str] = []
    _check_files_exist(findings)
    _check_execution_target(findings)
    _check_host_shim(findings)
    _check_demo_runners(findings)
    _check_howto(findings)
    _check_topology(findings)
    _check_design(findings)
    _check_workflows(findings)

    if findings:
        print(f"inf-001-execution-path: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(
        "inf-001-execution-path: PASS "
        f"({len(DEMO_RUNNERS)} demo runners, {len(HOWTO_TOPICS)} how-to topics, "
        f"{len(RUNTIME_WORKFLOWS)} runtime workflows)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
