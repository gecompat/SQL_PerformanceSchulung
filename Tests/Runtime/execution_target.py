#!/usr/bin/env python3
"""Ausfuehrungsziele der Runtime-Runner (INF-001).

Das Modul kapselt die Unterschiede zwischen einer wegwerfbaren
Container-Instanz (Ziel ``docker``) und einer bereits vorhandenen
SQL-Server-Instanz (Ziel ``host``). Die Runner formulieren ihre Pruefungen
gegen dieses Modul und bleiben dadurch frei von Containerannahmen.

Kennwoerter werden ausschliesslich ueber die Umgebungsvariable
SQLCMDPASSWORD uebergeben und nie als Argument gesetzt.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "Tests" / "Runtime"
FRAMEWORK_TOOLS = ROOT / "Demos" / "00_Framework" / "Tools"

if str(FRAMEWORK_TOOLS) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_TOOLS))

from sqlcmd_process import resolve_sqlcmd  # noqa: E402

DOCKER = "docker"
HOST = "host"
TARGET_KINDS = (DOCKER, HOST)

CONTAINER_VARIABLE = "SQLPERF_SQL_CONTAINER"
HOST_SQLCMD_VARIABLE = "SQLPERF_HOST_SQLCMD"
TRUST_CERTIFICATE_VARIABLE = "SQLPERF_HOST_TRUST_SERVER_CERTIFICATE"
CONFIRMATION_VARIABLE = "SQLPERF_HOST_DISPOSABLE_INSTANCE"

ENGINE_QUERY = (
    "SET NOCOUNT ON; "
    "SELECT CONVERT(int, SERVERPROPERTY('ProductMajorVersion')), "
    "CONVERT(int, SERVERPROPERTY('EngineEdition'));"
)
ENGINE_PATTERN = re.compile(r"(?m)^\s*(\d+)\|([234])\s*$")

_SQLCMD_OUTPUT_ARGUMENTS = (
    "-b",
    "-r",
    "1",
    "-W",
    "-s",
    "|",
    "-h",
    "-1",
    "-w",
    "65535",
)


class ExecutionTargetError(RuntimeError):
    """Fehler beim Aufloesen oder Ansprechen eines Ausfuehrungsziels."""


def redact(text: str) -> str:
    """Entfernt das Kennwort aus Diagnosetext.

    Ohne gesetztes Kennwort bleibt der Text unveraendert; ein Ersetzen des
    Leerstrings wuerde jedes Zeichen mit der Maske umgeben.
    """

    password = os.environ.get("SQLCMDPASSWORD")
    if not password:
        return text
    return text.replace(password, "***")


@dataclass(frozen=True)
class ExecutionTarget:
    """Beschreibt, wohin ein Runner seine T-SQL-Aufrufe richtet."""

    kind: str
    server: str
    auth: str
    username: str | None
    shim: Path
    sqlcmd_path: str
    container: str | None = None

    def child_environment(self) -> dict[str, str]:
        """Umgebung fuer Kindprozesse, die ueber den Shim verbinden."""

        environment = os.environ.copy()
        if self.kind == DOCKER:
            environment[CONTAINER_VARIABLE] = self.container or ""
        else:
            environment[HOST_SQLCMD_VARIABLE] = self.sqlcmd_path
        return environment

    def connection_arguments(self) -> list[str]:
        """Verbindungsargumente fuer run_demo.py und orchestrate_sessions.py."""

        arguments = ["--server", self.server, "--auth", self.auth]
        if self.auth == "sql" and self.username:
            arguments.extend(["--username", self.username])
        arguments.extend(["--sqlcmd", str(self.shim)])
        return arguments


def container_sqlcmd(container: str) -> str:
    """Ermittelt den sqlcmd-Pfad innerhalb des Containers."""

    result = subprocess.run(
        [
            "docker",
            "exec",
            container,
            "sh",
            "-lc",
            (
                "if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then "
                "printf /opt/mssql-tools18/bin/sqlcmd; "
                "elif [ -x /opt/mssql-tools/bin/sqlcmd ]; then "
                "printf /opt/mssql-tools/bin/sqlcmd; "
                "else exit 127; fi"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise ExecutionTargetError("sqlcmd not found inside container")
    return result.stdout.strip()


def docker_target(
    *,
    container: str,
    sqlcmd_path: str | None = None,
    server: str = "localhost",
) -> ExecutionTarget:
    """Erzeugt das Ziel fuer eine wegwerfbare Container-Instanz."""

    if not container:
        raise ExecutionTargetError("target docker requires --container")
    shim = (RUNTIME / "docker_sqlcmd_proxy.py").resolve()
    if not shim.is_file():
        raise ExecutionTargetError("docker sqlcmd proxy missing")
    return ExecutionTarget(
        kind=DOCKER,
        server=server,
        auth="sql",
        username="sa",
        shim=shim,
        sqlcmd_path=sqlcmd_path or container_sqlcmd(container),
        container=container,
    )


def host_target(
    *,
    server: str,
    username: str | None = None,
    sqlcmd_path: str | None = None,
) -> ExecutionTarget:
    """Erzeugt das Ziel fuer eine vorhandene SQL-Server-Instanz."""

    if not server:
        raise ExecutionTargetError("target host requires --server")
    shim = (RUNTIME / "host_sqlcmd_target.py").resolve()
    if not shim.is_file():
        raise ExecutionTargetError("host sqlcmd target missing")
    auth = "sql" if username else "integrated"
    if auth == "sql" and not os.environ.get("SQLCMDPASSWORD"):
        raise ExecutionTargetError(
            "target host with SQL authentication requires SQLCMDPASSWORD"
        )
    try:
        resolved = resolve_sqlcmd(
            sqlcmd_path or os.environ.get(HOST_SQLCMD_VARIABLE) or None
        )
    except (FileNotFoundError, ValueError) as exc:
        raise ExecutionTargetError(str(exc)) from exc
    return ExecutionTarget(
        kind=HOST,
        server=server,
        auth=auth,
        username=username,
        shim=shim,
        sqlcmd_path=resolved,
    )


def require_disposable_instance(target: ExecutionTarget, confirmed: bool) -> None:
    """Erzwingt die ausdrueckliche Bestaetigung einer Wegwerf-Instanz.

    Die Runner legen Datenbanken an und loeschen sie wieder. Gegen eine
    vorhandene Instanz darf das nur nach bewusster Freigabe geschehen.
    """

    if target.kind != HOST:
        return
    if confirmed or os.environ.get(CONFIRMATION_VARIABLE) == "1":
        return
    raise ExecutionTargetError(
        "target host requires --confirm-disposable-instance; the runner "
        "creates and drops SQLPERF_ databases on the selected instance"
    )


def _host_command(target: ExecutionTarget, database: str) -> list[str]:
    command = [target.sqlcmd_path, "-S", target.server, "-d", database]
    if target.auth == "sql":
        command.extend(["-U", target.username or ""])
    else:
        command.append("-E")
    if os.environ.get(TRUST_CERTIFICATE_VARIABLE) == "1":
        command.append("-C")
    command.extend(_SQLCMD_OUTPUT_ARGUMENTS)
    return command


def _docker_command(target: ExecutionTarget, database: str) -> list[str]:
    return [
        "docker",
        "exec",
        "-i",
        "-e",
        "SQLCMDPASSWORD",
        target.container or "",
        target.sqlcmd_path,
        "-S",
        "localhost",
        "-d",
        database,
        "-U",
        "sa",
        "-C",
        *_SQLCMD_OUTPUT_ARGUMENTS,
    ]


def run_sql(
    target: ExecutionTarget,
    *,
    database: str,
    sql_text: str,
    timeout_seconds: int = 120,
) -> str:
    """Fuehrt ein T-SQL-Skript gegen das Ziel aus und liefert stdout."""

    if target.kind == DOCKER:
        command = _docker_command(target, database)
    else:
        command = _host_command(target, database)
    result = subprocess.run(
        command,
        input=sql_text,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_seconds,
        env=os.environ.copy(),
    )
    if result.returncode != 0:
        diagnostic = (result.stderr or result.stdout).strip()
        raise ExecutionTargetError(
            f"sqlcmd failed in database {database}: {diagnostic[-2000:]}"
        )
    return result.stdout


def verify_engine(
    target: ExecutionTarget,
    *,
    expected_major: int | None = None,
) -> int:
    """Prueft die Engine-Identitaet und liefert die Hauptversion zurueck."""

    output = run_sql(
        target,
        database="master",
        sql_text=ENGINE_QUERY,
        timeout_seconds=60,
    )
    match = ENGINE_PATTERN.search(output)
    if match is None:
        raise ExecutionTargetError(
            "engine identity could not be determined; expected a supported "
            "engine edition (2, 3 or 4)"
        )
    major = int(match.group(1))
    if expected_major is not None and major != expected_major:
        raise ExecutionTargetError(
            f"engine identity mismatch; expected major {expected_major}, "
            f"detected {major}"
        )
    return major
