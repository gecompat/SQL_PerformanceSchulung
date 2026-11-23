"""Fixed FWK-010 entrypoint for the owned OPTSP comparison."""

import os
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Tests" / "Runtime"))
from run_optsp_paired import main as run_paired, recover_framework_container


def main() -> int:
    token = os.environ.get("SQLPERF_OPT018_OWNER_TOKEN", "")
    if re.fullmatch(r"[0-9a-f]{32}", token) is None:
        return 2
    if sys.argv[1:] == ["--recover"]:
        return 0 if recover_framework_container(token) else 3
    if sys.argv[1:]:
        return 2
    code = run_paired(["--confirm-disposable-container"], owner_token=token)
    summaries = {0: "PASS|OK", 1: "FAIL|FAIL_NOT_PROVEN", 3: "FAIL|FAIL_CLEANUP"}
    print(f"SQLPERF_SUMMARY|{summaries[code]}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
