"""Lifecycle for the two digest-pinned, owned DGN-004 SQL Server containers."""
from __future__ import annotations

from dataclasses import dataclass
from contextlib import contextmanager
import os
import re
import secrets
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "Tests" / "Runtime"
if str(RUNTIME) not in sys.path:
    sys.path.insert(0, str(RUNTIME))

from dgn004_capture_runner import CaptureTimeoutError, collect_bounded_process  # noqa: E402
from execution_target import ExecutionTarget, docker_target  # noqa: E402


PROJECT_LABEL = "com.sqlperf.project"
DEMO_LABEL = "com.sqlperf.demo"
RUN_LABEL = "com.sqlperf.run-token"
OWNER_LABEL = "com.sqlperf.owner"
OWNER_VALUE = "dgn004-runtime-v1"
SQL_READY_MARKER = "SQL Server is now ready for client connections."
CPU_NANOCORES = 2_000_000_000
CPU_SET = "0-1"
MEMORY_BYTES = 3 * 1024 * 1024 * 1024
SA_PASSWORD_ENV = "MSSQL_SA_PASSWORD"
START_RECOVERY_SETTLE_SECONDS = 20.0
START_RESPONSE_SETTLE_SECONDS = 1.0


@dataclass(frozen=True)
class BuildProfile:
    name: str
    image: str
    digest: str
    product_version: str
    edition: str
    compatibility_level: int
    mssql_pid: str = "Developer"


BUILD_PROFILES = (
    BuildProfile(
        name="2022",
        image="mcr.microsoft.com/mssql/server",
        digest="sha256:ba4c8329f48fb8f02e1416be6a930ebfd71268caee78aa985f3af4315e457c89",
        product_version="16.0.4265.3",
        edition="Developer Edition (64-bit)",
        compatibility_level=160,
    ),
    BuildProfile(
        name="2025",
        image="mcr.microsoft.com/mssql/server",
        digest="sha256:4bab24f36c1ecd48e85f7d37df26e6bf301641d84c3fe652f9a0dcc947d512e1",
        product_version="17.0.4075.5",
        edition="Enterprise Developer Edition (64-bit)",
        compatibility_level=170,
    ),
)


class ContainerError(RuntimeError):
    """A container boundary could not be established or preserved."""


class UncertainContainerStartError(ContainerError):
    """A start response was lost and cleanup could not be proven complete."""

    def __init__(self, message: str, *, cleanup_ok: bool):
        super().__init__(message)
        self.cleanup_ok = cleanup_ok


@dataclass(frozen=True)
class OwnedContainer:
    profile: BuildProfile
    name: str
    run_token: str
    container_id: str
    sa_password: str
    target: ExecutionTarget


def _docker_executable() -> str:
    return shutil.which("docker") or "docker"


def _password() -> str:
    upper = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    lower = "abcdefghijkmnopqrstuvwxyz"
    digits = "23456789"
    # Use a shell-, connection-string- and sqlcmd-safe symbol. The credential
    # is passed through environment variables, but minimizing punctuation also
    # avoids parser-specific ambiguity in native client libraries.
    special = "!"
    alphabet = upper + lower + digits
    chars = [secrets.choice(upper), secrets.choice(lower), secrets.choice(digits), secrets.choice(special)]
    chars.extend(secrets.choice(alphabet) for _ in range(28))
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


@contextmanager
def sqlcmd_password(password: str):
    """Expose the ephemeral credential to existing direct sqlcmd runners only."""
    if type(password) is not str or not re.fullmatch(r"[A-Za-z0-9!]{32}", password):
        raise ContainerError("invalid ephemeral SQL credential")
    previous = os.environ.get("SQLCMDPASSWORD")
    os.environ["SQLCMDPASSWORD"] = password
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("SQLCMDPASSWORD", None)
        else:
            os.environ["SQLCMDPASSWORD"] = previous


def _docker(
    args: list[str],
    *,
    environment: dict[str, str] | None = None,
    timeout: float = 20.0,
    output_limit: int = 64 * 1024,
    allow_stderr: bool = False,
) -> str:
    command = [_docker_executable(), *args]
    env = dict(os.environ if environment is None else environment)
    env["PYTHONIOENCODING"] = "utf-8"
    result = collect_bounded_process(
        command,
        input_bytes=b"",
        environment=env,
        timeout_seconds=timeout,
        stdout_limit_bytes=output_limit,
        stderr_limit_bytes=16 * 1024,
    )
    if result.returncode != 0 or (result.stderr and not allow_stderr):
        raise ContainerError("Docker command failed or wrote diagnostic output")
    try:
        output = result.stdout + (result.stderr if allow_stderr else b"")
        return output.decode("utf-8" if allow_stderr else "ascii",
                             errors="replace" if allow_stderr else "strict").strip()
    except UnicodeDecodeError as exc:
        raise ContainerError("Docker control output was not ASCII") from exc


def verify_pinned_image(profile: BuildProfile) -> None:
    if type(profile) is not BuildProfile or profile not in BUILD_PROFILES:
        raise ContainerError("unknown DGN-004 build profile")
    reference = f"{profile.image}@{profile.digest}"
    try:
        raw = _docker(["image", "inspect", "--format", "{{json .RepoDigests}}", reference])
    except ContainerError as exc:
        raise ContainerError("pinned DGN-004 image is not locally inspectable") from exc
    if reference not in raw and f"{profile.image}@{profile.digest}" not in raw:
        raise ContainerError("local image does not expose the exact registered digest")


def _resolve_sqlcmd(name: str, deadline: float) -> str:
    probe = (
        "if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then "
        "printf /opt/mssql-tools18/bin/sqlcmd; "
        "elif [ -x /opt/mssql-tools/bin/sqlcmd ]; then "
        "printf /opt/mssql-tools/bin/sqlcmd; else exit 127; fi"
    )
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise ContainerError("runtime deadline expired while resolving the owned sqlcmd")
    result = _docker(["exec", name, "sh", "-c", probe], timeout=min(10.0, remaining), output_limit=256)
    if result not in {"/opt/mssql-tools18/bin/sqlcmd", "/opt/mssql-tools/bin/sqlcmd"}:
        raise ContainerError("owned container sqlcmd path is not recognized")
    return result


def _inspect_identity(
    name: str,
    *,
    expected_profile: BuildProfile,
    expected_run_token: str,
) -> tuple[str, str]:
    template = (
        "{{.Id}}|{{.Config.Image}}|"
        f"{{{{index .Config.Labels \"{PROJECT_LABEL}\"}}}}|"
        f"{{{{index .Config.Labels \"{DEMO_LABEL}\"}}}}|"
        f"{{{{index .Config.Labels \"{RUN_LABEL}\"}}}}|"
        f"{{{{index .Config.Labels \"{OWNER_LABEL}\"}}}}|"
        "{{.HostConfig.NanoCpus}}|{{.HostConfig.CpusetCpus}}|{{.HostConfig.Memory}}|{{.HostConfig.MemorySwap}}|"
        "{{.HostConfig.NetworkMode}}|{{json .NetworkSettings.Ports}}|{{len .Mounts}}|{{.State.Status}}"
    )
    frame = _docker(["container", "inspect", "--format", template, name])
    fields = frame.split("|")
    if len(fields) != 14:
        raise ContainerError("container identity frame is incomplete")
    container_id, image, project, demo, run, owner, cpu, cpuset, memory, swap, network, ports, mounts, state = fields
    if (not re.fullmatch(r"[0-9a-f]{64}", container_id)
            or project != "SQL_PerformanceSchulung" or demo != "DGN-004"
            or run != expected_run_token or owner != OWNER_VALUE
            or int(cpu) != CPU_NANOCORES or cpuset != CPU_SET or int(memory) != MEMORY_BYTES
            or int(swap) != MEMORY_BYTES or network != "none"
            or ports not in {"{}", "null"} or int(mounts) != 0
            or expected_profile not in BUILD_PROFILES
            or image != f"{expected_profile.image}@{expected_profile.digest}"):
        raise ContainerError("container does not match the complete owned DGN-004 boundary")
    return container_id, state


def _recover_uncertain_start(
    *, name: str, profile: BuildProfile, run_token: str, deadline: float,
    settle_seconds: float = START_RECOVERY_SETTLE_SECONDS,
    expected_id: str | None = None,
) -> None:
    """Reconcile a lost `docker run` response using its unique name and labels."""
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise ContainerError("no recovery time remains after uncertain container start")
    settle_deadline = min(deadline, time.monotonic() + settle_seconds)
    while True:
        remaining = settle_deadline - time.monotonic()
        found = _docker(
            ["container", "ls", "--all", "--filter", f"name=^{name}$", "--format", "{{.Names}}"],
            timeout=min(10.0, max(0.1, remaining if remaining > 0 else deadline-time.monotonic())),
            output_limit=4096,
        )
        names = [line for line in found.splitlines() if line]
        if names:
            if names != [name]:
                raise ContainerError("uncertain start returned an ambiguous container name")
            # Inspection validates every ownership marker and runtime limit before any removal.
            identity, _ = _inspect_identity(name, expected_profile=profile, expected_run_token=run_token)
            if expected_id is not None and identity != expected_id:
                raise ContainerError("container ID differs from the acknowledged start response")
            cleanup_owned_container(
                name=name, expected_id=identity, run_token=run_token, profile=profile,
                deadline=deadline,
            )
        if time.monotonic() >= settle_deadline:
            # One final lookup at the end of the settle interval proves absence.
            final = _docker(
                ["container", "ls", "--all", "--filter", f"name=^{name}$", "--format", "{{.Names}}"],
                timeout=min(10.0, max(0.1, deadline-time.monotonic())), output_limit=4096,
            )
            if not final:
                return
            if final.strip() != name:
                raise ContainerError("uncertain start returned an ambiguous container name")
            identity, _ = _inspect_identity(name, expected_profile=profile, expected_run_token=run_token)
            if expected_id is not None and identity != expected_id:
                raise ContainerError("container ID differs from the acknowledged start response")
            cleanup_owned_container(
                name=name, expected_id=identity, run_token=run_token, profile=profile,
                deadline=deadline,
            )
        time.sleep(min(0.5, max(0.0, settle_deadline-time.monotonic())))


def start_owned_container(
    profile: BuildProfile, *, deadline: float, run_token: str | None = None
) -> OwnedContainer:
    verify_pinned_image(profile)
    run_token = secrets.token_hex(6).upper() if run_token is None else run_token
    if not re.fullmatch(r"[A-Z0-9]{12}", run_token):
        raise ContainerError("invalid owned-container run token")
    name = f"sqlperf_dgn004_{profile.name}_{run_token.lower()}"
    password = _password()
    environment = os.environ.copy()
    environment[SA_PASSWORD_ENV] = password
    reference = f"{profile.image}@{profile.digest}"
    command = [
        "run", "--detach", "--name", name,
        "--label", f"{PROJECT_LABEL}=SQL_PerformanceSchulung",
        "--label", f"{DEMO_LABEL}=DGN-004",
        "--label", f"{RUN_LABEL}={run_token}",
        "--label", f"{OWNER_LABEL}={OWNER_VALUE}",
        "--cpus=2", "--cpuset-cpus=0-1", "--memory=3g", "--memory-swap=3g", "--network=none",
        "--pull=never", "--restart=no",
        "--env", "ACCEPT_EULA=Y",
        "--env", f"MSSQL_PID={profile.mssql_pid}",
        "--env", SA_PASSWORD_ENV,
        reference,
    ]
    if time.monotonic() >= deadline:
        raise ContainerError("runtime deadline expired before container start")
    try:
        container_id = _docker(command, environment=environment, timeout=min(20.0, deadline - time.monotonic()))
        if not re.fullmatch(r"[0-9a-f]{64}", container_id):
            raise ContainerError("Docker did not return a complete container identity")
    except BaseException as start_error:
        settle_seconds = (START_RESPONSE_SETTLE_SECONDS
                          if isinstance(start_error, ContainerError)
                          and str(start_error) == "Docker did not return a complete container identity"
                          else START_RECOVERY_SETTLE_SECONDS)
        try:
            _recover_uncertain_start(
                name=name, profile=profile, run_token=run_token,
                deadline=time.monotonic() + 60.0,
                settle_seconds=settle_seconds,
            )
        except BaseException as recovery_error:
            raise UncertainContainerStartError(
                "container start outcome and cleanup are unknown", cleanup_ok=False
            ) from recovery_error
        raise start_error
    try:
        inspected_id, state = _inspect_identity(
            name, expected_profile=profile, expected_run_token=run_token
        )
        if inspected_id != container_id or state not in {"created", "running"}:
            raise ContainerError("new container identity or lifecycle state differs")
        sqlcmd_path = _resolve_sqlcmd(name, deadline)
        target = docker_target(container=name, sqlcmd_path=sqlcmd_path)
    except BaseException as startup_error:
        try:
            _recover_uncertain_start(
                name=name, expected_id=container_id, profile=profile,
                run_token=run_token, deadline=time.monotonic() + 60.0,
                settle_seconds=START_RESPONSE_SETTLE_SECONDS,
            )
        except BaseException as recovery_error:
            raise UncertainContainerStartError(
                "container startup failed and owned-container cleanup is unknown",
                cleanup_ok=False,
            ) from recovery_error
        raise startup_error
    return OwnedContainer(profile, name, run_token, container_id, password, target)


def wait_until_sql_server_ready(*, name: str, deadline: float, startup_limit: float = 60.0) -> None:
    """Wait on the owned container's startup log before the single SQL preflight."""
    if (type(name) is not str or not re.fullmatch(r"sqlperf_dgn004_(2022|2025)_[a-f0-9]{12}", name)
            or type(startup_limit) not in (int, float) or not 1 <= startup_limit <= 60):
        raise ContainerError("invalid SQL Server startup wait boundary")
    ready_deadline = min(deadline, time.monotonic() + startup_limit)
    while time.monotonic() < ready_deadline:
        remaining = ready_deadline - time.monotonic()
        logs = _docker(["container", "logs", "--tail", "100", name],
                       timeout=min(5.0, max(0.1, remaining)), output_limit=128 * 1024,
                       allow_stderr=True)
        if SQL_READY_MARKER in logs:
            # The log marker is emitted during engine startup. Give listener
            # and login initialization a brief bounded settle interval before
            # the single authenticated preflight connection.
            settle = min(1.5, max(0.0, deadline - time.monotonic()))
            if settle:
                time.sleep(settle)
            return
        time.sleep(min(1.0, max(0.0, ready_deadline-time.monotonic())))
    raise ContainerError("owned SQL Server did not report its ready state before the startup deadline")


def cleanup_owned_container(
    *,
    name: str,
    expected_id: str,
    run_token: str,
    profile: BuildProfile,
    deadline: float | None = None,
) -> None:
    if (type(name) is not str or not re.fullmatch(r"sqlperf_dgn004_(2022|2025)_[a-f0-9]{12}", name)
            or type(expected_id) is not str or not re.fullmatch(r"[0-9a-f]{64}", expected_id)
            or type(run_token) is not str or not re.fullmatch(r"[A-Z0-9]{12}", run_token)
            or type(profile) is not BuildProfile or profile not in BUILD_PROFILES):
        raise ContainerError("invalid owned-container cleanup identity")
    identity, state = _inspect_identity(
        name, expected_profile=profile, expected_run_token=run_token
    )
    if identity != expected_id:
        raise ContainerError("container ID changed; refusing cleanup")
    # Re-read labels/limits through _inspect_identity before every destructive action.
    if state == "running":
        timeout = 20.0 if deadline is None else min(20.0, max(0.1, deadline - time.monotonic()))
        _docker(["container", "stop", "--time", "10", name], timeout=timeout)
        identity, state = _inspect_identity(
            name, expected_profile=profile, expected_run_token=run_token
        )
        if identity != expected_id or state != "exited":
            raise ContainerError("owned container did not reach the stopped state")
    identity, state = _inspect_identity(
        name, expected_profile=profile, expected_run_token=run_token
    )
    if identity != expected_id or state not in {"exited", "created"}:
        raise ContainerError("container identity changed before removal")
    timeout = 20.0 if deadline is None else min(20.0, max(0.1, deadline - time.monotonic()))
    _docker(["container", "rm", name], timeout=timeout)
    try:
        _docker(["container", "inspect", name], timeout=min(5.0, timeout))
    except ContainerError:
        return
    raise ContainerError("removed container remains visible")
