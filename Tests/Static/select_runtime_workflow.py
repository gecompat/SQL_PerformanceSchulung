#!/usr/bin/env python3
"""Select an affected SQL runtime job from the exact Git revision pair.

An unavailable revision or an unparseable workflow conservatively selects runtime.
The selection never changes the qualification procedure when runtime is selected.
"""

from __future__ import annotations

import argparse
from fnmatch import fnmatchcase
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = {
    "adv008-opt009": ".github/workflows/adv008-opt009.yml",
    "adv008-opt010": ".github/workflows/adv008-opt010.yml",
    "adv008-opt015-opt016": ".github/workflows/adv008-opt015-opt016.yml",
    "adv008-qry004": ".github/workflows/adv008-qry004.yml",
    "adv008-qry013": ".github/workflows/adv008-qry013.yml",
    "adv017-opt017": ".github/workflows/adv017-opt017.yml",
    "dgn003-dgn005-pilots": ".github/workflows/dgn003-dgn005-pilots.yml",
    "dgn007": ".github/workflows/dgn007-automated-setup.yml",
    "framework": ".github/workflows/framework-sql-matrix.yml",
    "qry006-null-semantics": ".github/workflows/qry006-null-semantics.yml",
    "w-cov-001": ".github/workflows/w-cov-001.yml",
}


def parse_trigger_paths(text: str) -> tuple[str, ...]:
    event_block = re.search(r"(?ms)^on:\n(?P<events>.*?)(?=^permissions:|^concurrency:|^jobs:|\Z)", text)
    if not event_block:
        raise ValueError("workflow has no readable event block")
    paths = tuple(re.findall(r"(?m)^      - '([^']+)'$", event_block["events"]))
    if not paths:
        raise ValueError("workflow has no readable path selector")
    return paths


def trigger_paths(workflow: str) -> tuple[str, ...]:
    return parse_trigger_paths((ROOT / workflow).read_text(encoding="utf-8"))


def runtime_block(text: str) -> str:
    marker = "  runtime:\n"
    if text.count(marker) != 1:
        raise ValueError("workflow runtime job is unavailable or ambiguous")
    job = text.split(marker, 1)[1]
    execution_marker = "    runs-on:"
    if job.count(execution_marker) != 1:
        raise ValueError("workflow runtime execution body is unavailable or ambiguous")
    # Name, dependencies and the selector guard are scheduling metadata. The
    # runner, matrix and actual validation steps begin at runs-on.
    return job.split(execution_marker, 1)[1]


def select_runtime(
    changed_paths: set[str],
    patterns: tuple[str, ...],
    workflow: str,
    *,
    runtime_job_changed: bool,
) -> bool:
    """Fail closed for affected runtime inputs; static changes get static gates."""
    affected = {path for path in changed_paths if any(fnmatchcase(path, pattern) for pattern in patterns)}
    if any(path != workflow and not path.startswith("Tests/Static/") for path in affected):
        return True
    return workflow in affected and runtime_job_changed


def git_bytes(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.DEVNULL)


def decide(workflow: str, event: str, base: str, head: str) -> tuple[bool, str]:
    if event == "workflow_dispatch":
        return True, "manual qualification requested"
    if event not in {"pull_request", "push"} or not re.fullmatch(r"[0-9a-f]{40}", base) or not re.fullmatch(r"[0-9a-f]{40}", head):
        return True, "unknown event or revision binding"
    try:
        changed = {
            path.decode("utf-8")
            for path in git_bytes("diff", "--name-only", "-z", base, head, "--").split(b"\0")
            if path
        }
        old = git_bytes("show", f"{base}:{workflow}").decode("utf-8")
        new = git_bytes("show", f"{head}:{workflow}").decode("utf-8")
        patterns = tuple(set(parse_trigger_paths(old)) | set(parse_trigger_paths(new)))
        job_changed = runtime_block(old) != runtime_block(new)
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError, ValueError):
        return True, "revision or dependency comparison unavailable"
    selected = select_runtime(changed, patterns, workflow, runtime_job_changed=job_changed)
    return selected, "affected runtime input" if selected else "only unrelated or static inputs changed"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", choices=WORKFLOWS, required=True)
    parser.add_argument("--event", required=True)
    parser.add_argument("--base", default="")
    parser.add_argument("--head", default="")
    parser.add_argument("--output", type=Path, default=Path(os.devnull))
    args = parser.parse_args()
    selected, reason = decide(WORKFLOWS[args.workflow], args.event, args.base, args.head)
    with args.output.open("a", encoding="utf-8") as output:
        output.write(f"run_runtime={'true' if selected else 'false'}\n")
    print(f"runtime-selection: {'EXECUTE' if selected else 'NOT_APPLICABLE'} ({reason})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
