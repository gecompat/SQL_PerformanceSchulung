"""Reiner gebundener Handshakeeingang; kein Start, Send oder Phasenverbrauch."""
from dataclasses import dataclass, field
from types import FunctionType

import dgn007_session_channel as channel

FORMAT = "pooled-combined-input-design/v1"
_ISSUES = frozenset(("PLAN_FORM", "PLAN_BINDING", "PLAN_RECEIVE", "PLAN_FORMSET_LIMIT",
    "PLAN_TRANSFER_LIMIT", "PLAN_COMMAND", "PLAN_INTERNAL", "PLAN_OWNER",
    "HASH_PROVIDER_BINDING", "REPORT_ENCODER_BINDING"))
_ROLES = ("METADATA", "REPORTED", "pooled-installation-declaration/v1",
          "pooled-worker-declaration/v1", "pooled-profile-binding-context/v1")


@dataclass(frozen=True, slots=True, repr=False)
class HandshakeInputSelection:
    metadata_chunks: tuple
    bodies: tuple
    input_metadata: tuple
    worker: tuple
    context: tuple
    reported: tuple


@dataclass(frozen=True, slots=True, repr=False)
class PlannedWorkerInput:
    selected: HandshakeInputSelection
    header: bytes
    metadata: bytes
    commands: tuple
    form_sizes: tuple
    transfer_bytes: int


@dataclass(frozen=True, slots=True, repr=False)
class HandshakePlanReport:
    status: str
    issue: str
    plans: tuple = field(default=(), repr=False)
    transfer_bytes: int = 0
    validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)
    runtime_attested: bool = field(default=False, init=False)
    trust_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)

    def __repr__(self):
        return "HandshakePlanReport(PROJECT_SEMANTIC)"


class _Rejected(Exception):
    pass


def _need(condition, issue="PLAN_FORM"):
    if not condition:
        raise _Rejected(issue)


def _issue(error):
    args = BaseException.__dict__["args"].__get__(error, BaseException)
    if type(args) is tuple and len(args) == 1 and type(args[0]) is str and len(args[0]) <= 32:
        if args[0] in _ISSUES:
            return args[0]
        if args[0] == "CHANNEL_OWNER":
            return "PLAN_OWNER"
    return "PLAN_FORM"


def _preflight(control, selections):
    ns = control.namespace
    helpers = ("_inline_receive_declared_bodies", "_inline_command_encode", "_report_pack", "_report_json")
    _need(all(type(ns.get(name)) is FunctionType and ns[name].__globals__ is ns for name in helpers),
          "PLAN_OWNER")
    _need(type(selections) is tuple and 1 <= len(selections) <= 3)
    _need(all(type(item) is HandshakeInputSelection for item in selections))
    for item in selections:
        _need(type(item.metadata_chunks) is tuple and len(item.metadata_chunks) <= 256)
        _need(type(item.bodies) is tuple and len(item.bodies) == 9)
        _need(all(type(piece) is bytes for piece in item.metadata_chunks + item.bodies))
    for item in selections:
        ns["_report_shape"](ns["_INLINE_M"], (item.input_metadata, item.worker, item.context))
        ns["_report_shape"](ns["_REPORT_R"], item.reported)
        _need(all(len(piece) <= 1024 for piece in item.metadata_chunks))
        _need(16 <= sum(map(len, item.metadata_chunks)) <= 16384)
        _need(all(len(body) <= 131072 for body in item.bodies))
        _need(sum(map(len, item.bodies)) <= 1048576)
    for ordinal, item in enumerate(selections, 1):
        _need(item.context[5] == ordinal and item.worker[:3] == item.context[5:], "PLAN_BINDING")
        _need(item.reported == (item.context,) + item.worker[3:], "PLAN_BINDING")
        _need(item.context[:5] == selections[0].context[:5]
              and item.input_metadata == selections[0].input_metadata, "PLAN_BINDING")


def _accepted(result, status, issue):
    _need(type(result) is tuple and len(result) == 3 and type(result[0]) is str
          and type(result[1]) is str, issue)
    _need(result[:2] == (status, "NONE"), issue)
    return result[2]


def plan_handshake_inputs(namespace, selections, *, expected_format):
    """Atomar gegebene Eingangsbytes prüfen; keine operative Freigabe erzeugen."""
    control, plans, issue, total = None, [], "NONE", 0
    try:
        _need(type(expected_format) is str and expected_format == FORMAT)
        control = channel._Control(namespace)
        _preflight(control, selections)
        control.capture()
        for item in selections:
            control.check()
            received = _accepted(namespace["_inline_receive_declared_bodies"](
                item.metadata_chunks, item.bodies, expected_format=FORMAT,
                expected_input=item.input_metadata, expected_worker=item.worker,
                expected_context=item.context), "RECEIVED_DECLARED_BODIES", "PLAN_RECEIVE")
            control.check()
            _need(type(received) is tuple and len(received) == 4
                  and type(received[0]) is bytes and type(received[1]) is bytes
                  and type(received[2]) is tuple and received[3] is item.bodies, "PLAN_RECEIVE")
            header, metadata = received[:2]
            _need(received[2] == (item.input_metadata, item.worker, item.context), "PLAN_BINDING")
            payloads = (received[2], item.reported, (item.worker[3],), (item.worker,), (item.context,))
            sizes = []
            for index, (role, payload) in enumerate(zip(_ROLES, payloads)):
                control.check()
                packed = namespace["_report_pack"](payload)
                raw = namespace["_report_json"]((packed[0], role, packed[2], packed[3]), control.encoder)
                control.check()
                _need(type(raw) is bytes and 16 + len(raw) <= 16384, "PLAN_FORMSET_LIMIT")
                if index == 0:
                    _need(raw == metadata, "PLAN_BINDING")
                sizes.append(16 + len(raw))
            _need(sum(sizes) <= 65536, "PLAN_FORMSET_LIMIT")
            commands = []
            for kind in ("BODY_RELEASE", "BODY_END", "IMPORT_RELEASE"):
                control.check()
                command = _accepted(namespace["_inline_command_encode"](kind, item.context,
                    expected_format=FORMAT), "FORMATTED_BOUND_COMMAND", "PLAN_COMMAND")
                control.check()
                _need(type(command) is bytes and 0 < len(command) <= 256, "PLAN_COMMAND")
                commands.append(command)
            cost = len(header) + len(metadata) + sum(map(len, item.bodies)) + sum(map(len, commands))
            _need(cost <= 1064960, "PLAN_TRANSFER_LIMIT")
            total += cost
            _need(total <= 3194880, "PLAN_TRANSFER_LIMIT")
            plans.append(PlannedWorkerInput(item, header, metadata, tuple(commands), tuple(sizes), cost))
        control.check()
    except BaseException as error:
        issue = _issue(error)
    if control is not None:
        try:
            control.check()
        except BaseException as error:
            issue = channel._dominant(issue, _issue(error))
    if issue != "NONE":
        return HandshakePlanReport("REJECTED_HANDSHAKE_INPUTS", issue)
    return HandshakePlanReport("PLANNED_DECLARED_HANDSHAKE_INPUTS", "NONE", tuple(plans), total)
