#!/usr/bin/env python3
"""Narrow framework entry point for the self-cleaning IDX-007 live demo."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Tests.Runtime.idx007_hot_leaf_pilot import run_bounded_trials


def main() -> int:
    parser = argparse.ArgumentParser(description="One bounded live IDX-007 demonstration run")
    parser.add_argument("--major", type=int, choices=(15, 16, 17), required=True)
    args = parser.parse_args()
    print("LESSON|Two controlled insert bursts; observe exclusive page-latch overlap and rightmost-leaf evidence.")
    try:
        result = run_bounded_trials(args.major, attempts=1)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"SQLPERF_SUMMARY|FAIL|FAIL_EXECUTION\n{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    if result == 0:
        print("SQLPERF_SUMMARY|PASS|OK")
        return 0
    if result == 2:
        print("SQLPERF_SUMMARY|WARN|WARN_NOT_PROVEN")
        return 0
    print(f"SQLPERF_SUMMARY|FAIL|FAIL_EXECUTION (pilot exit {result})", file=sys.stderr)
    return result if 1 <= result <= 125 else 1


if __name__ == "__main__":
    raise SystemExit(main())
