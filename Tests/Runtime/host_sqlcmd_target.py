#!/usr/bin/env python3
"""sqlcmd-Shim fuer eine vorhandene SQL-Server-Instanz (INF-001).

Das Shim ist das Gegenstueck zu docker_sqlcmd_proxy.py fuer das
Ausfuehrungsziel ``host``. Es reicht saemtliche Argumente unveraendert an das
echte sqlcmd weiter, insbesondere den mit -S uebergebenen Servernamen.

Ergaenzt wird lediglich -C, und zwar nur wenn
SQLPERF_HOST_TRUST_SERVER_CERTIFICATE=1 gesetzt ist. Das Vertrauen in ein
selbstsigniertes Serverzertifikat bleibt damit eine bewusste Entscheidung und
ist nicht die Voreinstellung.

Kennwoerter werden ausschliesslich ueber SQLCMDPASSWORD gereicht.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

FRAMEWORK_TOOLS = (
    Path(__file__).resolve().parents[2] / "Demos" / "00_Framework" / "Tools"
)
if str(FRAMEWORK_TOOLS) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_TOOLS))

from sqlcmd_process import resolve_sqlcmd  # noqa: E402

SQLCMD_VARIABLE = "SQLPERF_HOST_SQLCMD"
TRUST_CERTIFICATE_VARIABLE = "SQLPERF_HOST_TRUST_SERVER_CERTIFICATE"


def main() -> int:
    try:
        executable = resolve_sqlcmd(os.environ.get(SQLCMD_VARIABLE) or None)
    except (FileNotFoundError, ValueError) as exc:
        print(f"host-sqlcmd-target: {exc}", file=sys.stderr)
        return 2

    if Path(executable).resolve() == Path(__file__).resolve():
        print(
            f"host-sqlcmd-target: {SQLCMD_VARIABLE} must point to the real "
            "sqlcmd executable, not to this shim",
            file=sys.stderr,
        )
        return 2

    command = [executable]
    if os.environ.get(TRUST_CERTIFICATE_VARIABLE) == "1":
        command.append("-C")
    command.extend(sys.argv[1:])

    completed = subprocess.run(
        command,
        check=False,
        shell=False,
        env=os.environ.copy(),
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
