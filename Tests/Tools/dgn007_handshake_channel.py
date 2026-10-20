"""Eigener bidirektionaler Phasenweg mit deklarierten Traces; kein Importbeleg."""
from dataclasses import dataclass, field
import os
from types import FunctionType

import dgn007_handshake_input_plan as inputs
import dgn007_session_channel as channel


@dataclass(frozen=True, slots=True, repr=False)
class HandshakeSelection:
    program: bytes
    input_selection: inputs.HandshakeInputSelection


@dataclass(frozen=True, slots=True, repr=False)
class HandshakeChannelReport:
    status: str
    issue: str
    first_issue: str
    channels: channel.ChannelReport = field(repr=False)
    written_bytes: int = 0
    body_release_reserved: int = 0
    body_release_sent: int = 0
    body_end_reserved: int = 0
    body_end_sent: int = 0
    import_release_reserved: int = 0
    import_release_sent: int = 0
    stdin_closed: int = 0
    validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)
    runtime_attested: bool = field(default=False, init=False)
    trust_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)

    def __repr__(self):
        return "HandshakeChannelReport(PROJECT_SEMANTIC)"


def _write(fd, data):
    return os.write(fd, data)


class _Driver:
    def __init__(self):
        self.plans = self.base = None
        self.bound = self.written_bytes = self.body_release_reserved = self.body_release_sent = 0
        self.body_end_reserved = self.body_end_sent = 0
        self.import_release_reserved = self.import_release_sent = self.stdin_closed = 0

    def prepare(self, control, selections, limits):
        channel._need(type(selections) is tuple and 1 <= len(selections) <= 3)
        channel._need(all(type(item) is HandshakeSelection for item in selections))
        channel._need(all(type(item.program) is bytes and type(item.input_selection) is inputs.HandshakeInputSelection
                          for item in selections))
        helpers = ("_inline_match_profile_records", "_inline_plan_profile_body_release", "_inline_match_input_complete")
        channel._need(all(type(control.namespace.get(name)) is FunctionType
            and control.namespace[name].__globals__ is control.namespace for name in helpers), "CHANNEL_OWNER")
        self.base = tuple(channel.ChannelSelection(item.program, item.input_selection.reported,
                                                   item.input_selection.context) for item in selections)
        channel._prepare(control, self.base, limits)
        control.check()
        report = inputs.plan_handshake_inputs(control.namespace, tuple(item.input_selection for item in selections),
                                              expected_format=inputs.FORMAT)
        control.check()
        channel._need(type(report) is inputs.HandshakePlanReport
            and report.status == "PLANNED_DECLARED_HANDSHAKE_INPUTS" and report.issue == "NONE", "CHANNEL_INPUT")
        channel._need(len(report.plans) == len(selections)
            and all(plan.selected is item.input_selection for plan, item in zip(report.plans, selections)), "CHANNEL_OWNER")
        self.plans, self.transfer_cap = report.plans, report.transfer_bytes
        return self.base

    @staticmethod
    def launch(program):
        return channel._launch(program, stdin=channel.subprocess.PIPE)

    def bind(self, selection, process, selector, budget, control):
        index = selection.context[5] - 1
        channel._need(index == self.bound and self.base[index] is selection, "CHANNEL_OWNER")
        self.bound += 1
        return _Phase(self, self.plans[index], process, selector, budget, control)


class _Phase:
    def __init__(self, driver, plan, process, selector, budget, control):
        self.driver, self.plan, self.process, self.selector = driver, plan, process, selector
        self.budget, self.control = budget, control
        self.registered = False
        self.written = 0
        self.stage = "SEND_METADATA"
        channel._need(process.stdin is not None, "CHANNEL_INPUT")
        os.set_blocking(process.stdin.fileno(), False)
        self._queue("SEND_METADATA", (plan.header, plan.metadata))

    def _queue(self, stage, pieces):
        self.stage, self.pieces, self.index, self.offset = stage, pieces, 0, 0
        if not self.registered:
            self.selector.register(self.process.stdin, channel.selectors.EVENT_WRITE, "stdin")
            self.registered = True
        self._advance()

    def _stop_write(self):
        if self.registered:
            self.selector.unregister(self.process.stdin)
            self.registered = False

    def _advance(self):
        # Höchstens neun eigene Bodies, keine freie oder fremde Iteration.
        while self.index < len(self.pieces) and self.offset == len(self.pieces[self.index]):
            self.index += 1
            self.offset = 0
        if self.index < len(self.pieces):
            return
        if self.stage == "SEND_METADATA":
            self._stop_write(); self.stage = "AWAIT_PROFILE"
        elif self.stage == "SEND_BODY_RELEASE":
            self.driver.body_release_sent += 1
            self._queue("BODY_TRANSFER", self.plan.selected.bodies)
        elif self.stage == "BODY_TRANSFER":
            self.driver.body_end_reserved += 1
            self._queue("SEND_BODY_END", (self.plan.commands[1],))
        elif self.stage == "SEND_BODY_END":
            self.driver.body_end_sent += 1
            self._stop_write(); self.stage = "AWAIT_INPUT_COMPLETE"
        elif self.stage == "SEND_IMPORT_RELEASE":
            self.driver.import_release_sent += 1
            self._stop_write()
            self.process.stdin.close()
            channel._need(self.process.stdin.closed, "CHANNEL_INPUT")
            self.driver.stdin_closed += 1
            self.stage = "DRAIN"
        else:
            channel._need(False, "CHANNEL_PHASE")

    def write(self):
        channel._need(self.registered and self.index < len(self.pieces), "CHANNEL_PHASE")
        data = self.pieces[self.index][self.offset:self.offset + 4096]
        try:
            count = _write(self.process.stdin.fileno(), data)
        except BlockingIOError:
            return False
        except OSError:
            raise channel._Rejected("CHANNEL_INPUT") from None
        channel._need(type(count) is int and 0 <= count <= len(data), "CHANNEL_INPUT")
        if count == 0:
            return False
        self.written += count
        self.driver.written_bytes += count
        channel._need(self.written <= self.plan.transfer_bytes
            and self.driver.written_bytes <= self.driver.transfer_cap, "CHANNEL_INPUT")
        self.offset += count
        self._advance()
        return True

    def read_phase(self):
        channel._need(self.stage in ("AWAIT_PROFILE", "AWAIT_INPUT_COMPLETE", "DRAIN"), "CHANNEL_PHASE")
        return self.stage

    def _call(self, name, status, *args, **kwargs):
        self.budget.check(); self.control.check()
        result = self.control.namespace[name](*args, expected_format=inputs.FORMAT, **kwargs)
        self.control.check(); self.budget.check()
        channel._need(type(result) is tuple and len(result) == 3 and type(result[0]) is str
            and type(result[1]) is str and result[:2] == (status, "NONE"), "CHANNEL_PHASE")
        return result[2]

    def record(self, rows, line, observed_phase):
        channel._need(observed_phase == self.stage, "CHANNEL_PHASE")
        if self.stage == "AWAIT_PROFILE":
            channel._need(line.startswith((b'["PROFILE_BEGIN",', b"P|", b'["PROFILE_END",')), "CHANNEL_PHASE")
            if line.startswith(b'["PROFILE_END",'):
                records = tuple(rows)
                actual = self._call("_inline_match_profile_records", "MATCHED_DECLARED_PROFILE_RECORDS", records,
                                    expected_phase="AWAIT_PROFILE", expected_reported=self.plan.selected.reported)
                channel._need(type(actual) is tuple and len(actual) == 4 and actual[3] is records, "CHANNEL_PHASE")
                ready = self._call("_inline_plan_profile_body_release", "PLANNED_DECLARED_BODY_RELEASE",
                    actual[0], actual[1], expected_phase="AWAIT_PROFILE",
                    expected_reported=self.plan.selected.reported, expected_context=self.plan.selected.context)
                channel._need(type(ready) is tuple and len(ready) == 5 and type(ready[3]) is bytes
                    and ready[3] == self.plan.commands[0], "CHANNEL_PHASE")
                self.driver.body_release_reserved += 1
                self._queue("SEND_BODY_RELEASE", (self.plan.commands[0],))
        elif self.stage == "AWAIT_INPUT_COMPLETE":
            actual = self._call("_inline_match_input_complete", "MATCHED_DECLARED_INPUT_COMPLETE", line,
                expected_phase="AWAIT_INPUT_COMPLETE", expected_context=self.plan.selected.context)
            channel._need(type(actual) is tuple and len(actual) == 2 and actual[0] is line, "CHANNEL_PHASE")
            self.driver.import_release_reserved += 1
            self._queue("SEND_IMPORT_RELEASE", (self.plan.commands[2],))
        else:
            channel._need(self.stage == "DRAIN", "CHANNEL_PHASE")

    def finished(self):
        channel._need(self.stage == "DRAIN" and self.process.stdin.closed
            and self.written == self.plan.transfer_bytes, "CHANNEL_PHASE")


def run_handshake_channels(namespace, selections, *, limits=channel.ChannelLimits()):
    """Eigene einmalige Phasen; keine öffentliche Transition-/Receipt-Authority."""
    start = channel.time.monotonic_ns()
    driver = _Driver()
    result = channel._run_session_channels(namespace, selections, limits, driver=driver, start=start)
    return HandshakeChannelReport("CLOSED_HANDSHAKE_CHANNELS" if result.issue == "NONE" else "REJECTED_HANDSHAKE_CHANNELS",
        result.issue, result.first_issue, result, driver.written_bytes, driver.body_release_reserved,
        driver.body_release_sent, driver.body_end_reserved, driver.body_end_sent,
        driver.import_release_reserved, driver.import_release_sent, driver.stdin_closed)
