"""Fixed identity exchange for the External Tables guest control channel."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from math import isfinite
from pathlib import Path
from secrets import token_bytes
import socket
from struct import Struct
from time import monotonic, sleep
from uuid import UUID

from external_tables_package_state import expected_package_digest, installed_package_digest, read_dpkg_status
from external_tables_pilot_sql import Role, database_name


_REQUEST = Struct("!4s8sB16s")
_RESPONSE = Struct("!4s8sB16s32s")
_QUERY = b"SEI2"
_REPLY = b"SER2"
_DETACHED_QUERY = b"SED1"
_DETACHED_REPLY = b"SEP1"
_GUEST_STATUS_PATH = Path("/var/lib/dpkg/status")
_ROLE_ID = {Role.SOURCE: 1, Role.QUERY: 2}


def linux_service_id(port: int) -> UUID:
    """Map a Linux VSOCK port to the Hyper-V service GUID."""
    if type(port) is not int or not 1024 <= port <= 65535:
        raise ValueError("expected a nonprivileged VSOCK port")
    return UUID(f"{port:08x}-facb-11e6-bd58-64006a7986d3")


def verify_guest(
    vm_id: UUID, port: int, token: str, role: Role, deadline: float, *,
    base_status: bytes, package_lock: dict, detached: bool = False, wait: bool = False,
) -> None:
    """Verify the exact VM and role inventory in the requested phase."""
    with connect_verified_guest(
        vm_id, port, token, role, deadline,
        base_status=base_status, package_lock=package_lock, detached=detached, wait=wait,
    ):
        pass


@contextmanager
def connect_verified_guest(
    vm_id: UUID, port: int, token: str, role: Role, deadline: float, *,
    base_status: bytes, package_lock: dict, detached: bool = False, wait: bool = False,
) -> Iterator[socket.socket]:
    """Yield only the channel that returned the current identity proof."""
    _remaining(deadline)
    service_id = linux_service_id(port)
    run_marker, role_id = _identity(token, role)
    wildcards = {
        getattr(socket, field, "").lower()
        for field in ("HV_GUID_ZERO", "HV_GUID_BROADCAST", "HV_GUID_WILDCARD",
                      "HV_GUID_CHILDREN", "HV_GUID_LOOPBACK", "HV_GUID_PARENT")
    }
    if not isinstance(vm_id, UUID) or not vm_id.int or str(vm_id) in wildcards:
        raise ValueError("expected one exact Hyper-V guest ID")
    try:
        family, protocol = socket.AF_HYPERV, socket.HV_PROTOCOL_RAW
    except AttributeError:
        raise OSError("Hyper-V sockets are unavailable on the host") from None
    expected_digest = expected_package_digest(base_status, package_lock, role.value.lower())
    nonce = token_bytes(16)
    request_kind, reply_kind = (_DETACHED_QUERY, _DETACHED_REPLY) if detached else (_QUERY, _REPLY)
    with _connect_hyperv(family, protocol, (str(vm_id), str(service_id)), deadline, wait) as channel:
        _send(channel, _REQUEST.pack(request_kind, run_marker, role_id, nonce), deadline)
        reply, reply_token, reply_role, reply_nonce, digest = _RESPONSE.unpack(
            _receive(channel, _RESPONSE.size, deadline)
        )
        if (reply, reply_token, reply_role, reply_nonce) != (reply_kind, run_marker, role_id, nonce):
            raise ValueError("guest identity response does not match the current probe")
        if digest != expected_digest:
            raise ValueError("guest package inventory does not match the locked role")
        yield channel


@contextmanager
def _connect_hyperv(
    family: int, protocol: int, endpoint: tuple[str, str], deadline: float, wait: bool,
) -> Iterator[socket.socket]:
    while True:
        with socket.socket(family, socket.SOCK_STREAM, protocol) as channel:
            remaining = _remaining(deadline)
            channel.settimeout(min(2, remaining) if wait else remaining)
            try:
                channel.connect(endpoint)
            except (ConnectionRefusedError, TimeoutError):
                if not wait:
                    raise
            else:
                yield channel
                return
        sleep(min(0.25, _remaining(deadline)))


def serve_guest_identity(port: int, token: str, role: Role, deadline: float) -> None:
    """Respond to one parent connection on the prepared Linux guest."""
    _identity(token, role)
    with accept_parent_connection(port, deadline) as channel:
        _reply_to_probe(channel, token, role, deadline)


def serve_detached_guest_ready(
    port: int, token: str, role: Role, deadline: float, *, verify_ready: Callable[[], None],
) -> None:
    """Report detached preparation once, after a fresh guest-side check."""
    _identity(token, role)
    with accept_parent_connection(port, deadline) as channel:
        _reply_to_probe(channel, token, role, deadline, verify_ready=verify_ready)


@contextmanager
def accept_parent_connection(port: int, deadline: float) -> Iterator[socket.socket]:
    """Accept one connection from the Linux guest's host partition."""
    with open_parent_listener(port) as (listener, host_cid):
        listener.settimeout(_remaining(deadline))
        channel, (peer_cid, _) = listener.accept()
        with channel:
            if peer_cid != host_cid:
                raise ValueError("guest identity probe did not come from the parent")
            yield channel


@contextmanager
def open_parent_listener(port: int) -> Iterator[tuple[socket.socket, int]]:
    """Bind the configured guest VSOCK port once."""
    linux_service_id(port)
    try:
        family, any_cid, host_cid = socket.AF_VSOCK, socket.VMADDR_CID_ANY, socket.VMADDR_CID_HOST
    except AttributeError:
        raise OSError("virtual sockets are unavailable on the guest") from None
    with socket.socket(family, socket.SOCK_STREAM) as listener:
        listener.bind((any_cid, port))
        listener.listen(1)
        yield listener, host_cid


def _reply_to_probe(
    channel: socket.socket, token: str, role: Role, deadline: float, *, verify_ready: Callable[[], None] | None = None,
) -> None:
    expected_token, expected_role = _identity(token, role)
    request_kind, reply_kind = (_QUERY, _REPLY) if verify_ready is None else (_DETACHED_QUERY, _DETACHED_REPLY)
    kind, request_token, role_id, nonce = _REQUEST.unpack(_receive(channel, _REQUEST.size, deadline))
    if (kind, request_token, role_id) != (request_kind, expected_token, expected_role):
        raise ValueError("guest identity probe does not match the configured run")
    _remaining(deadline)
    digest = installed_package_digest(read_dpkg_status(_GUEST_STATUS_PATH))
    if verify_ready is not None:
        verify_ready()
    _send(channel, _RESPONSE.pack(reply_kind, expected_token, expected_role, nonce, digest), deadline)


def _identity(token: str, role: Role) -> tuple[bytes, int]:
    database_name(token, role)
    return token.encode("ascii"), _ROLE_ID[role]


def _send(channel: socket.socket, payload: bytes, deadline: float) -> None:
    channel.settimeout(_remaining(deadline))
    channel.sendall(payload)


def _receive(channel: socket.socket, size: int, deadline: float) -> bytes:
    payload = bytearray()
    while len(payload) < size:
        channel.settimeout(_remaining(deadline))
        chunk = channel.recv(size - len(payload))
        if not chunk:
            raise OSError("identity channel closed before the fixed packet arrived")
        payload.extend(chunk)
    return bytes(payload)


def _remaining(deadline: float) -> float:
    remaining = deadline - monotonic()
    if not isfinite(remaining) or remaining <= 0:
        raise TimeoutError("guest identity deadline exceeded")
    return remaining
