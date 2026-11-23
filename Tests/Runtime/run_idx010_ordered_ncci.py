"""Run the ordered NCCI comparison on its pinned disposable SQL Server build."""
from __future__ import annotations

import argparse
import secrets

from idx010_docker_transport import DockerPilotTransport
from idx010_pilot_sequence import run_pilot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument(
        "--confirm-disposable-container", action="store_true", required=True,
        help="Accept the SQL Server Developer EULA and create one isolated test container.",
    )
    parser.parse_args(argv)

    result = run_pilot(DockerPilotTransport(), secrets.token_hex(10).upper())
    for arm in result.arms:
        print(
            f"IDX010_NCCI|ARM|{arm.arm.value}|overlapping_pairs={arm.overlapping_pairs}"
            f"|segments_read={arm.segments.reads}|segments_skipped={arm.segments.skipped}"
        )
    print(f"IDX010_NCCI|{result.status}|stage={result.stage}")
    return {"PASS": 0, "NOT_PROVEN": 1, "FAIL_CLEANUP": 3}[result.status]


if __name__ == "__main__":
    raise SystemExit(main())
