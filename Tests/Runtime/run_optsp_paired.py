"""Run the two-pair OPTIMIZED_SP_EXECUTESQL comparison on an owned container."""

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import secrets
from time import monotonic, sleep

from dgn004_capture_runner import CaptureRunnerError, collect_bounded_process
from optsp_paired_evidence import CONFIGURATIONS, EvidenceFailure, evaluate_series

IMAGE = "mcr.microsoft.com/mssql/server@sha256:05644dad1266ca3d445d1e8f6d2ebb9a6a03df9a39376e0f7b48917356dca9d9"
PROFILE = "17.0.5065.9|Enterprise Developer Edition (64-bit)|0"
CONTAINER_ID = re.compile(r"[0-9a-f]{64}")
OWNER_LABEL = "com.sqlperf.optsp.owner"
WORK_SECONDS = 240
CLEANUP_SECONDS = 60
ARM_WORKER = Path(__file__).with_name("Invoke-OptspPairedArm.ps1")
DATABASES_SQL = "SET NOCOUNT ON; SELECT name FROM sys.databases WHERE database_id > 4;"


@dataclass(frozen=True)
class Database:
    token: str

    @property
    def name(self) -> str:
        return f"OptspProbe_{self.token}"


class PilotError(RuntimeError):
    pass


class OwnedPilot:
    def __init__(self, owner_token: str | None = None) -> None:
        if owner_token is not None and re.fullmatch(r"[0-9a-f]{32}", owner_token) is None:
            raise ValueError("invalid OPTSP owner token")
        self.token = owner_token if owner_token is not None else secrets.token_hex(16)
        self.name = f"sqlperf-optsp-{self.token}"
        self.password = "Opt9!" + secrets.token_hex(16)
        self.deadline = monotonic() + WORK_SECONDS
        self.docker = ["docker"]
        self.create_attempted = False
        self.container = None
        self.databases: list[Database] = []
        self.stage = "preflight"

    def _run(self, command, *, cap=16, payload=b"", secret=None):
        remaining = self.deadline - monotonic()
        if remaining <= 0:
            raise PilotError("deadline exhausted")
        environment = os.environ.copy()
        if secret is not None:
            environment[secret] = self.password
        result = collect_bounded_process(
            command, input_bytes=payload, environment=environment, timeout_seconds=min(cap, remaining),
            stdout_limit_bytes=128 * 1024, stderr_limit_bytes=16 * 1024, timeout_ceiling_seconds=WORK_SECONDS,
        )
        if result.returncode or result.stderr or monotonic() >= self.deadline:
            raise PilotError("bounded process did not finish cleanly")
        return result.stdout.decode("utf-8", errors="strict").strip()

    def _docker(self, *args, secret=None):
        return self._run([*self.docker, *args], secret=secret)

    def _owned_container(self):
        command = ("container", "ls", "--all", "--quiet", "--no-trunc", "--filter")
        by_name = self._docker(*command, f"name=^/{self.name}$")
        by_label = self._docker(*command, f"label={OWNER_LABEL}={self.token}")
        if (
            by_label != by_name or (by_name and CONTAINER_ID.fullmatch(by_name) is None)
            or (by_name and self.container is not None and by_name != self.container)
        ):
            raise PilotError("container ownership unconfirmed")
        return by_name or None

    def _sql(self, database: str, statement: str) -> str:
        if self.container is None:
            raise PilotError("no verified container")
        return self._run([
            *self.docker, "exec", "-i", "-e", "SQLCMDPASSWORD", "-e", "SQLCMDINI=", self.container,
            "/opt/mssql-tools18/bin/sqlcmd", "-S", "127.0.0.1", "-d", database, "-C", "-U", "sa",
            "-b", "-x", "-r", "1", "-l", "3", "-t", "5", "-h", "-1", "-W",
        ], payload=(statement + "\nGO\n").encode("ascii"), secret="SQLCMDPASSWORD")

    def _bind_local_context(self) -> None:
        context = self._docker("context", "show")
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", context) is None:
            raise PilotError("invalid Docker context")
        endpoint = self._docker("context", "inspect", context, "--format", "{{.Endpoints.docker.Host}}")
        if not endpoint.startswith(("npipe:////./pipe/", "unix:///")):
            raise PilotError("Docker socket must be local")
        self.docker.extend(["--context", context])

    def _start(self) -> str:
        self._bind_local_context()
        image_id = self._docker("image", "inspect", "--format", "{{.Id}}", IMAGE)
        if re.fullmatch(r"sha256:[0-9a-f]{64}", image_id) is None:
            raise PilotError("pinned image is not locally verified")
        if self._owned_container() is not None:
            raise PilotError("chosen container identity already exists")

        self.create_attempted = True
        candidate = self._docker(
            "create", "--pull", "never", "--name", self.name, "--label", f"{OWNER_LABEL}={self.token}",
            "--cpus", "2", "--memory", "4g", "--memory-swap", "4g", "-e", "ACCEPT_EULA=Y",
            "-e", "MSSQL_PID=Developer", "-e", "MSSQL_SA_PASSWORD", "-p", "127.0.0.1::1433", IMAGE,
            secret="MSSQL_SA_PASSWORD",
        )
        if CONTAINER_ID.fullmatch(candidate) is None or self._owned_container() != candidate:
            raise PilotError("container ID does not match its markers")
        self.container = candidate
        fields = self._docker(
            "inspect", "--format",
            "{{.Image}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}|{{.HostConfig.MemorySwap}}|"
            "{{json .Mounts}}|{{.State.Status}}|{{json .HostConfig.PortBindings}}", candidate,
        ).split("|")
        bindings = json.loads(fields[6]) if len(fields) == 7 else {}
        if not isinstance(bindings, dict):
            raise PilotError("unexpected port binding format")
        ports = bindings.get("1433/tcp", [])
        if (
            set(bindings) != {"1433/tcp"} or len(ports) != 1
            or not isinstance(ports[0], dict) or ports[0].get("HostIp") != "127.0.0.1"
        ):
            raise PilotError("unexpected container port binding")
        reserved = ports[0].get("HostPort", "")
        if not isinstance(reserved, str) or (reserved not in {"", "0"} and (
            re.fullmatch(r"[1-9][0-9]{0,4}", reserved) is None or int(reserved) > 65535
        )):
            raise PilotError("invalid reserved loopback port")
        if (
            len(fields) != 7 or fields[:4] != [image_id, "2000000000", "4294967296", "4294967296"]
            or json.loads(fields[4]) not in ([], None) or fields[5] != "created"
        ):
            raise PilotError("container profile mismatch")
        self._docker("start", candidate)
        binding = self._docker("port", candidate, "1433/tcp")
        port = re.fullmatch(r"127\.0\.0\.1:([1-9][0-9]{0,4})", binding)
        if port is None or int(port[1]) > 65535 or reserved not in {"", "0", port[1]}:
            raise PilotError("no bound loopback endpoint")

        ready_deadline = min(self.deadline, monotonic() + 45)
        while monotonic() < ready_deadline:
            try:
                self._sql("master", "SET NOCOUNT ON; SELECT 1;")
            except (CaptureRunnerError, PilotError):
                sleep(1)
            else:
                break
        else:
            raise PilotError("owned SQL instance did not become ready")
        if self._sql(
            "master", "SET NOCOUNT ON; SELECT CONCAT(CONVERT(nvarchar(64),SERVERPROPERTY('ProductVersion')),"
            "'|',CONVERT(nvarchar(128),SERVERPROPERTY('Edition')),'|',"
            "(SELECT COUNT(*) FROM sys.databases WHERE database_id>4));",
        ) != PROFILE:
            raise PilotError("SQL profile mismatch")
        return f"127.0.0.1,{port[1]}"

    def _provision(self) -> None:
        for option, _ in CONFIGURATIONS:
            database = Database(secrets.token_hex(16))
            self.databases.append(database)
            name = database.name
            self._sql("master", f"CREATE DATABASE [{name}];")
            self._sql(
                name, f"EXEC sys.sp_addextendedproperty @name=N'OptspOwner', @value=N'{database.token}';"
            )
            self._sql(
                "master", f"ALTER DATABASE [{name}] SET COMPATIBILITY_LEVEL=170; "
                f"ALTER DATABASE [{name}] SET AUTO_UPDATE_STATISTICS OFF;",
            )
            mode = "ON" if option else "OFF"
            self._sql(name, f"ALTER DATABASE SCOPED CONFIGURATION SET OPTIMIZED_SP_EXECUTESQL = {mode};")
        found = self._sql("master", DATABASES_SQL).splitlines()
        if sorted(name.strip() for name in found) != sorted(database.name for database in self.databases):
            raise PilotError("test database inventory mismatch")

    def execute(self):
        server = self._start()
        self.stage = "provision"
        self._provision()
        records = []
        for position, (database, (option, variant)) in enumerate(zip(self.databases, CONFIGURATIONS, strict=True), 1):
            self.stage = f"arm_{position}"
            record = self._run([
                "pwsh", "-NoProfile", "-NonInteractive", "-File", str(ARM_WORKER),
                "-Server", server, "-Database", database.name, "-Owner", database.token,
                "-Option", str(option), "-Variant", variant,
            ], cap=32, secret="SQLCMDPASSWORD")
            records.append(json.loads(record))
        self.stage = "evaluation"
        return evaluate_series(records)

    def _drop_database(self, database: Database) -> None:
        name = database.name
        xe = f"optsp_on_{database.token}"
        self._sql("master", f"""SET NOCOUNT ON;
IF DB_ID(N'{name}') IS NOT NULL
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM [{name}].sys.extended_properties
        WHERE class=0 AND name COLLATE Latin1_General_100_BIN2=N'OptspOwner'
        AND DATALENGTH(CONVERT(nvarchar(4000),value))=64
        AND CONVERT(nvarchar(4000),value) COLLATE Latin1_General_100_BIN2=N'{database.token}'
    ) THROW 51000,'cleanup marker missing',1;
    IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name=N'{xe}')
        DROP EVENT SESSION [{xe}] ON SERVER;
    DROP DATABASE [{name}];
END
IF DB_ID(N'{name}') IS NOT NULL
    OR EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name=N'{xe}')
    OR EXISTS (SELECT 1 FROM sys.dm_xe_sessions WHERE name=N'{xe}')
    THROW 51000,'database or XE session still exists',1;""")

    def cleanup(self) -> bool:
        if not self.create_attempted:
            return True
        cleanup_deadline = monotonic() + CLEANUP_SECONDS
        self.deadline = cleanup_deadline
        owned = self._owned_container()
        if owned is None:
            # A failed or timed-out create does not establish daemon-side absence.
            return False

        sql_clean = True
        try:
            # Keep time for the independent container removal and absence check.
            self.deadline = cleanup_deadline - 12
            for database in reversed(self.databases):
                try:
                    self._drop_database(database)
                except (CaptureRunnerError, OSError, PilotError, ValueError):
                    sql_clean = False
            if self.databases:
                sql_clean = self._sql("master", DATABASES_SQL) == "" and sql_clean
        finally:
            self.deadline = cleanup_deadline
            if self._owned_container() != owned:
                raise PilotError("cleanup ownership changed")
            self._docker("rm", "--force", "--volumes", owned)
            container_absent = self._owned_container() is None
        return sql_clean and container_absent


def recover_framework_container(owner_token: str) -> bool:
    """Recover only the coordinator-owned, digest-bound disposable container."""
    pilot = OwnedPilot(owner_token)
    pilot.deadline = monotonic() + CLEANUP_SECONDS
    try:
        pilot._bind_local_context()
        owned = pilot._owned_container()
        if owned is None:
            # The terminated create might still be pending in the daemon.
            return False
        image_id = pilot._docker("image", "inspect", "--format", "{{.Id}}", IMAGE)
        actual = pilot._docker("inspect", "--format", "{{.Image}}", owned)
        if re.fullmatch(r"sha256:[0-9a-f]{64}", image_id) is None or actual != image_id:
            return False
        if pilot._owned_container() != owned:
            return False
        pilot._docker("rm", "--force", "--volumes", owned)
        return pilot._owned_container() is None
    except (CaptureRunnerError, OSError, PilotError, ValueError):
        return False


def main(argv: list[str] | None = None, *, owner_token: str | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument(
        "--confirm-disposable-container", required=True, action="store_true",
        help="Accept the SQL Server Developer EULA and start one isolated container.",
    )
    parser.parse_args(argv)
    pilot = OwnedPilot() if owner_token is None else OwnedPilot(owner_token)
    findings = ()
    evidence_code = None
    expected_failures = (CaptureRunnerError, IndexError, KeyError, OSError, PilotError, TypeError, ValueError)
    try:
        findings = pilot.execute()
    except EvidenceFailure as error:
        evidence_code = str(error)
    except expected_failures:
        pass
    finally:
        try:
            cleaned = pilot.cleanup()
        except expected_failures:
            cleaned = False
    if not cleaned:
        print(f"OPTSP|FAIL_CLEANUP|stage={pilot.stage}|owner={pilot.token}")
        return 3
    if not findings:
        suffix = f"|code={evidence_code}" if evidence_code else ""
        print(f"OPTSP|NOT_PROVEN|stage={pilot.stage}{suffix}")
        return 1
    for case, status, reason in findings:
        print(f"OPTSP|{case}|{status}|{reason}")
    print("OPTSP|PASS|cleanup=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
