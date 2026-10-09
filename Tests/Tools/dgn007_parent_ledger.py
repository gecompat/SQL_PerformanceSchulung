"""Lokales synthetisches Parent-Ledger; keine Kanal- oder Ereignisherkunft.

Die bekannte Fakeadapterwahl und ein exklusiver Owner sind Kontrollannahmen.
Es gibt keine Worker, I/O, JSON/SHA, Aufnahme oder globale Replayabwehr.
"""
from dataclasses import dataclass
from types import CellType, FunctionType, MappingProxyType, ModuleType

import dgn007_import_profile_binding as binding

_STATES = ("RESERVED", "START_RESERVED", "AWAIT_PROFILE", "BODY_RELEASE_RESERVED",
           "BODY_TRANSFER", "BODY_END_RESERVED", "AWAIT_INPUT_COMPLETE",
           "IMPORT_RELEASE_RESERVED", "AWAIT_SESSION_END", "AWAIT_DRAIN_EXIT",
           "AWAIT_CLEANUP", "CLOSED")
_EVENTS = ("RESERVE_START", "START_AND_METADATA", "PROFILE_AND_PLAN",
           "WRITE_BODY_RELEASE", "BODIES_COMPLETE", "WRITE_BODY_END",
           "INPUT_COMPLETE", "WRITE_IMPORT_RELEASE", "SESSION_COMPLETE",
           "DRAIN_EXIT", "CLEANUP")
_K_FIELDS = ("commit", "raw27_binding", "source_profile", "nonce", "modules",
             "ordinal", "entry", "phase")
_D_FIELDS = ("ordinal", "module", "member", "size", "sha256")
_CLASS_DICT = type.__dict__["__dict__"]
_CLASS_MRO = type.__dict__["__mro__"]
_CLASS_BASES = type.__dict__["__bases__"]
_ISSUES = frozenset(("LEDGER_FORM", "LEDGER_LIMIT", "LEDGER_CONTEXT", "LEDGER_OWNER",
                     "LEDGER_ORDER", "LEDGER_CONSUMED", "LEDGER_REENTRANT",
                     "LEDGER_INTERNAL", "LEDGER_CLEANUP", "HASH_PROVIDER_BINDING",
                     "REPORT_ENCODER_BINDING"))
_CREATE_KEY = object()


class LedgerRejected(ValueError):
    """Nur feste Labels, keine fremden Fehlertexte oder Ketten."""


class _SyntheticPartial(Exception):
    pass


class _SyntheticUnknown(Exception):
    pass


class _SyntheticCleanupUnknown(Exception):
    pass


class _SyntheticProviderLoss(Exception):
    pass


class _SyntheticEncoderLoss(Exception):
    pass


class _SyntheticBothLoss(Exception):
    pass


def _need(ok, issue="LEDGER_FORM"):
    if not ok:
        raise LedgerRejected(issue) from None


def _issue(error, fallback="LEDGER_INTERNAL"):
    if type(error) is LedgerRejected:
        args = BaseException.__dict__["args"].__get__(error, BaseException)
        if type(args) is tuple and len(args) == 1 and type(args[0]) is str and len(args[0]) <= 32:
            if args[0] in _ISSUES:
                return args[0]
    return fallback


def _text(value):
    _need(type(value) is str)
    try:
        _need(len(value) <= 4096 and "\0" not in value
              and len(value.encode("utf-8")) <= 4096)
    except UnicodeError:
        raise LedgerRejected("LEDGER_FORM") from None


def _integer(value, maximum=99999999):
    _need(type(value) is int and 0 <= value <= maximum)


def _baseline_shape(row):
    _need(type(row) is tuple and len(row) == 8)
    for index in (0, 1, 2, 6, 7):
        _text(row[index])
    _need(type(row[3]) is bytes and len(row[3]) == 32)
    _integer(row[5])
    _need(type(row[4]) is tuple and len(row[4]) == 9)
    for descriptor in row[4]:
        _need(type(descriptor) is tuple and len(descriptor) == 5)
        _integer(descriptor[0])
        _text(descriptor[1])
        _text(descriptor[2])
        _integer(descriptor[3])
        _text(descriptor[4])


def _primitive(context):
    _need(type(context) is _CONTEXT_CLASS)
    row = tuple(object.__getattribute__(context, name) for name in _K_FIELDS)
    _need(type(row[4]) is tuple and len(row[4]) == 9)
    # Alle Descriptorobjekte vor dem ersten Feldlookup aufnehmen.
    for descriptor in row[4]:
        _need(type(descriptor) is _DESCRIPTOR_CLASS)
    descriptors = tuple(tuple(object.__getattribute__(d, name) for name in _D_FIELDS)
                        for d in row[4])
    result = row[:4] + (descriptors,) + row[5:]
    _baseline_shape(result)
    return result


def _namespace(mapping):
    _need(type(mapping) is dict and len(mapping) <= 256, "LEDGER_OWNER")
    keys = tuple(mapping)
    _need(all(type(key) is str for key in keys), "LEDGER_OWNER")
    return tuple((key, mapping[key]) for key in keys)


def _same_namespace(mapping, snapshot):
    actual = _namespace(mapping)
    _need(len(actual) == len(snapshot), "LEDGER_OWNER")
    for (key, value), (old_key, old_value) in zip(actual, snapshot):
        _need(key == old_key and value is old_value, "LEDGER_OWNER")


def _class_namespace(cls):
    _need(type(cls) is type, "LEDGER_OWNER")
    namespace = _CLASS_DICT.__get__(cls, type)
    _need(len(namespace) <= 256, "LEDGER_OWNER")
    keys = tuple(namespace)
    _need(all(type(key) is str for key in keys), "LEDGER_OWNER")
    return tuple((key, namespace[key]) for key in keys)


def _function_snapshot(function):
    _need(type(function) is FunctionType, "LEDGER_OWNER")
    defaults = function.__defaults__
    _need(defaults is None or (type(defaults) is tuple and len(defaults) <= 256),
          "LEDGER_OWNER")
    kw = function.__kwdefaults__
    kw_values = () if kw is None else _namespace(kw)
    closure = function.__closure__
    _need(closure is None or (type(closure) is tuple and len(closure) <= 256),
          "LEDGER_OWNER")
    cells = []
    for cell in closure or ():
        _need(type(cell) is CellType, "LEDGER_OWNER")
        try:
            cells.append((cell, cell.cell_contents))
        except ValueError:
            raise LedgerRejected("LEDGER_OWNER") from None
    return (function, function.__code__, function.__globals__, defaults,
            () if defaults is None else tuple(defaults), kw, kw_values, closure,
            tuple(cells))


def _function_check(anchor):
    fn, code, glob, defaults, values, kw, kw_values, closure, cells = anchor
    _need(type(fn) is FunctionType and fn.__code__ is code and fn.__globals__ is glob
          and fn.__defaults__ is defaults and fn.__kwdefaults__ is kw
          and fn.__closure__ is closure, "LEDGER_OWNER")
    if defaults is not None:
        _need(type(defaults) is tuple and len(defaults) == len(values), "LEDGER_OWNER")
        _need(all(a is b for a, b in zip(defaults, values)), "LEDGER_OWNER")
    if kw is not None:
        _same_namespace(kw, kw_values)
    for cell, value in cells:
        try:
            _need(type(cell) is CellType and cell.cell_contents is value, "LEDGER_OWNER")
        except ValueError:
            raise LedgerRejected("LEDGER_OWNER") from None


class _Anchors:
    __slots__ = ("namespaces", "functions", "classes")

    def __init__(self, hook):
        functions = list(_HELD_FUNCTIONS)
        if hook is not None:
            functions.append(hook)
        classes = []
        for cls in _HELD_CLASSES:
            snapshot = _class_namespace(cls)
            classes.append((cls, snapshot, _CLASS_MRO.__get__(cls, type),
                            _CLASS_BASES.__get__(cls, type)))
            for _, value in snapshot:
                if type(value) is FunctionType:
                    _need(len(functions) < 256, "LEDGER_LIMIT")
                    functions.append(value)
        self.functions = tuple(_function_snapshot(fn) for fn in functions)
        _need(len(self.functions) <= 256, "LEDGER_LIMIT")
        namespaces = []
        for anchor in self.functions:
            glob = anchor[2]
            if not any(glob is old[0] for old in namespaces):
                namespaces.append((glob, _namespace(glob)))
            # Bekannte Builtins-Tabelle ist eine direkt verwendete Globalsabhängigkeit.
            builtins = glob.get("__builtins__")
            if type(builtins) is ModuleType:
                builtins = object.__getattribute__(builtins, "__dict__")
            _need(type(builtins) is dict, "LEDGER_OWNER")
            if not any(builtins is old[0] for old in namespaces):
                namespaces.append((builtins, _namespace(builtins)))
        for module in (binding, binding.input82):
            _need(type(module) is ModuleType, "LEDGER_OWNER")
            md = object.__getattribute__(module, "__dict__")
            if not any(md is old[0] for old in namespaces):
                namespaces.append((md, _namespace(md)))
        _need(len(namespaces) <= 256, "LEDGER_LIMIT")
        self.namespaces = tuple(namespaces)
        self.classes = tuple(classes)

    def check(self):
        for namespace, snapshot in self.namespaces:
            _same_namespace(namespace, snapshot)
        for cls, snapshot, mro, bases in self.classes:
            actual = _class_namespace(cls)
            _need(_CLASS_MRO.__get__(cls, type) is mro
                  and _CLASS_BASES.__get__(cls, type) is bases
                  and len(actual) == len(snapshot), "LEDGER_OWNER")
            for (key, value), (old_key, old_value) in zip(actual, snapshot):
                _need(key == old_key and value is old_value, "LEDGER_OWNER")
        for anchor in self.functions:
            _function_check(anchor)


@dataclass(frozen=True, slots=True, repr=False, eq=False)
class _Receipt:
    owner: object
    ledger: object
    slot: object
    context: object
    baseline: tuple
    sequence: int
    before: int
    after: int
    invocation: object


class _Invocation:
    __slots__ = ("owner", "ledger", "slot", "context", "baseline", "sequence",
                 "before", "after", "receipt", "attempted", "completed", "consumed")

    def __init__(self, ledger, slot, before, after):
        self.owner, self.ledger, self.slot = ledger._owner, ledger, slot
        self.context, self.baseline = slot.context, slot.baseline
        self.sequence, self.before, self.after = slot.sequence, before, after
        self.attempted = self.completed = self.consumed = False
        self.receipt = _Receipt(self.owner, ledger, slot, slot.context, slot.baseline,
                                slot.sequence, before, after, self)


class _SyntheticAdapter:
    """Bekannter Fakepfad; Hookreturn ist keine Ereignisauthority."""
    __slots__ = ("hook", "_owner")

    def __init__(self, hook=None):
        _need(hook is None or type(hook) is FunctionType, "LEDGER_OWNER")
        self.hook = hook
        self._owner = None

    def _invoke(self, invocation):
        receipt = invocation.receipt
        hook = self.hook
        completed_slot = _INV_COMPLETED
        invocation.attempted = True
        if hook is not None:
            hook(invocation)
        # Gehaltener nativer Slotsetter; kein veränderter Pythoncheckerdispatch.
        completed_slot.__set__(invocation, True)
        return receipt


class _Slot:
    __slots__ = ("context", "baseline", "state", "sequence", "bits",
                 "start_attempted", "cleanup_attempted", "cleanup_complete")

    def __init__(self, context, baseline):
        self.context, self.baseline = context, baseline
        self.state = self.sequence = self.bits = 0
        self.start_attempted = self.cleanup_attempted = False
        self.cleanup_complete = False


@dataclass(frozen=True, slots=True, repr=False, eq=False)
class LedgerDiagnostic:
    status: str
    state: str
    first_issue: str
    final_issue: str
    slot_index: int
    sequence: int
    starts: int
    commands: int
    bookings: int
    cleanup: int
    slots: tuple
    cleanup_state: str
    trust_attested: bool = False
    runtime_attested: bool = False
    channel_attested: bool = False
    replay_attested: bool = False
    consumption_attested: bool = False
    cleanup_attested: bool = False
    import_used_bytes_attested: bool = False
    method_approved: bool = False

    def __repr__(self):
        return "<LedgerDiagnostic>"


def _diagnostic(ledger, cls, states, issues, ledger_fields, slot_fields, result_fields, slot_class):
    """Feste gehaltene Codekopie; ruft diagnose oder DTO-__init__ nicht auf."""
    def get(name):
        return ledger_fields[name].__get__(ledger, type(ledger))
    slots = get("_slots")
    if type(slots) is not tuple or not 1 <= len(slots) <= 3:
        slots = ()
    index = get("_index")
    if type(index) is not int or not 0 <= index < len(slots):
        index = 0
    rows = []
    sequence = 0
    state = "UNKNOWN"
    cleanup_state = "NOT_STARTED"
    for number, slot in enumerate(slots):
        if type(slot) is not slot_class:
            rows.append((number + 1, "UNKNOWN", 0))
            continue
        st = slot_fields["state"].__get__(slot, slot_class)
        bits = slot_fields["bits"].__get__(slot, slot_class)
        seq = slot_fields["sequence"].__get__(slot, slot_class)
        name = states[st] if type(st) is int and 0 <= st < 12 else "UNKNOWN"
        bit_value = bits if type(bits) is int and 0 <= bits <= 31 else 0
        rows.append((number + 1, name, bit_value))
        if number == index:
            state = name
            sequence = seq if type(seq) is int and 0 <= seq <= 11 else 0
            started = slot_fields["start_attempted"].__get__(slot, slot_class)
            complete = slot_fields["cleanup_complete"].__get__(slot, slot_class)
            attempted = slot_fields["cleanup_attempted"].__get__(slot, slot_class)
            if started is True:
                cleanup_state = "COMPLETE" if complete is True else ("UNKNOWN" if attempted is True else "PENDING")
    terminal = get("_terminal")
    status = terminal if type(terminal) is str and len(terminal) <= 32 and terminal in ("FAILED", "UNKNOWN") else (
        "LOCAL_CLOSED" if state == "CLOSED" and index + 1 == len(slots) else "LOCAL_PENDING")
    first, final = get("_first"), get("_final")
    first = first if type(first) is str and len(first) <= 32 and (first == "" or first in issues) else "LEDGER_OWNER"
    final = final if type(final) is str and len(final) <= 32 and (final == "" or final in issues) else "LEDGER_OWNER"
    if status in ("FAILED", "UNKNOWN") and cleanup_state in ("PENDING", "UNKNOWN"):
        status, final = "UNKNOWN", "LEDGER_CLEANUP"
    counts = []
    for key, limit in (("_starts", 3), ("_commands", 9), ("_bookings", 42), ("_cleanup", 3)):
        value = get(key)
        counts.append(value if type(value) is int and 0 <= value <= limit else 0)
    values = (status, state, first, final, index + 1, sequence, *counts, tuple(rows), cleanup_state,
              False, False, False, False, False, False, False, False)
    names = ("status", "state", "first_issue", "final_issue", "slot_index", "sequence",
             "starts", "commands", "bookings", "cleanup", "slots", "cleanup_state", "trust_attested",
             "runtime_attested", "channel_attested", "replay_attested", "consumption_attested",
             "cleanup_attested", "import_used_bytes_attested", "method_approved")
    # Native Slots, kein ausgetauschter generated Konstruktor.
    result = object.__new__(cls)
    for key, value in zip(names, values):
        result_fields[key].__set__(result, value)
    return result


class LocalLedger:
    __slots__ = ("_owner", "_slots", "_adapter", "_hook", "_anchors", "_index",
                 "_busy", "_active", "_terminal", "_first", "_final", "_rank",
                 "_starts", "_commands", "_bookings", "_cleanup", "_report")

    def __init__(self, contexts, baselines, adapter, anchors, key):
        _need(key is _CREATE_KEY, "LEDGER_OWNER")
        self._owner = object()
        self._slots = tuple(_Slot(c, p) for c, p in zip(contexts, baselines))
        self._adapter, self._hook, self._anchors = adapter, adapter.hook, anchors
        self._index = 0
        self._busy = False
        self._active = None
        self._terminal = self._first = self._final = ""
        self._rank = self._starts = self._commands = self._bookings = self._cleanup = 0
        adapter._owner = self._owner
        self._report = (LedgerDiagnostic, _STATES, _ISSUES,
                        MappingProxyType(dict(_LD_DESCRIPTORS)),
                        MappingProxyType(dict(_SLOT_DESCRIPTORS)),
                        MappingProxyType(dict(_DIAG_DESCRIPTORS)), _Slot,
                        (FunctionType, _DIAGNOSTIC_CODE, object, type, tuple,
                         int, str, len, enumerate, zip, bool, dict, all, max,
                         CellType, BaseException, ValueError,
                         _CLASS_DICT, _CLASS_MRO, _CLASS_BASES),
                        (_SyntheticProviderLoss, _SyntheticBothLoss,
                         _SyntheticEncoderLoss, _SyntheticCleanupUnknown),
                        (anchors, anchors.functions, anchors.classes, anchors.namespaces),
                        (_LEDGER_RUN.__code__, _LEDGER_RUN.__globals__, _LEDGER_RUN.__defaults__),
                        LocalLedger._stop.__code__,
                        (_LEDGER_POST, _RECEIPT_CHECK, _INV_CONSUMED), LocalLedger,
                        (_Anchors, MappingProxyType({name: _Anchors.__dict__[name]
                                                   for name in _Anchors.__slots__})))

    def __repr__(self):
        return "<LocalLedger>"

    def __copy__(self):
        raise LedgerRejected("LEDGER_CONSUMED") from None

    def __deepcopy__(self, memo):
        raise LedgerRejected("LEDGER_CONSUMED") from None

    def __reduce_ex__(self, protocol):
        raise LedgerRejected("LEDGER_CONSUMED") from None

    def _stop(self, issue, rank=0, unknown=False, hold=None):
        fields = (object.__getattribute__(self, "_report") if hold is None else hold)[3]
        def get(name):
            return fields[name].__get__(self)
        def put(name, value):
            fields[name].__set__(self, value)
        saved_rank, bookings, terminal = get("_rank"), get("_bookings"), get("_terminal")
        first, final = get("_first"), get("_final")
        if type(saved_rank) is not int or not 0 <= saved_rank <= 3:
            saved_rank = 0
        if type(bookings) is not int or not 0 <= bookings <= 42:
            bookings = 0
        if type(terminal) is not str or len(terminal) > 32:
            terminal = "UNKNOWN"
        first_valid = (type(first) is str and len(first) <= 32
                       and (first == "" or first in _ISSUES))
        final_valid = (type(final) is str and len(final) <= 32
                       and (final == "" or final in _ISSUES))
        if not first_valid:
            first = "LEDGER_OWNER"
        if not final_valid:
            final, saved_rank = "LEDGER_OWNER", 0
        if first == "":
            first = issue
            bookings += 1
        if final == "" or rank > saved_rank:
            final, saved_rank = issue, rank
        if terminal != "UNKNOWN":
            terminal = "UNKNOWN" if unknown else "FAILED"
        for name, value in (("_first", first), ("_final", final), ("_rank", saved_rank),
                            ("_bookings", bookings), ("_terminal", terminal)):
            put(name, value)

    def _contexts_check(self):
        _need(type(self._slots) is tuple and 1 <= len(self._slots) <= 3, "LEDGER_OWNER")
        _need(all(type(slot) is _Slot for slot in self._slots), "LEDGER_OWNER")
        _integer(self._index, len(self._slots) - 1)
        _need(type(self._owner) is object and type(self._busy) is bool, "LEDGER_OWNER")
        for value in (self._first, self._final):
            _need(type(value) is str and len(value) <= 32
                  and (value == "" or value in _ISSUES), "LEDGER_OWNER")
        _need(type(self._terminal) is str and len(self._terminal) <= 32
              and self._terminal in ("", "FAILED", "UNKNOWN"), "LEDGER_OWNER")
        for value, limit in ((self._starts, 3), (self._commands, 9),
                             (self._bookings, 42), (self._cleanup, 3), (self._rank, 3)):
            _integer(value, limit)
        # Beide ganzen Vorläufe vor dem ersten Baselinevergleich.
        actual = tuple(_primitive(slot.context) for slot in self._slots)
        for slot in self._slots:
            _baseline_shape(slot.baseline)
            _integer(slot.state, 11)
            _integer(slot.sequence, 11)
            _integer(slot.bits, 31)
            _need(type(slot.start_attempted) is bool and type(slot.cleanup_attempted) is bool
                  and type(slot.cleanup_complete) is bool)
        for slot in self._slots:
            _CONTEXT_CHECK(slot.context)
        for slot, row in zip(self._slots, actual):
            _need(row == slot.baseline, "LEDGER_CONTEXT")

    def _post(self):
        try:
            chosen, functions, classes, namespaces = self._report[9]
            _need(type(self._anchors) is _Anchors and self._anchors is chosen, "LEDGER_OWNER")
            _need(type(chosen.functions) is tuple and chosen.functions is functions
                  and type(chosen.classes) is tuple and chosen.classes is classes
                  and type(chosen.namespaces) is tuple and chosen.namespaces is namespaces,
                  "LEDGER_OWNER")
            _ANCHOR_CHECK(self._anchors)
            _need(type(self._adapter) is _SyntheticAdapter and self._adapter.hook is self._hook,
                  "LEDGER_OWNER")
            _need(self._adapter._owner is self._owner, "LEDGER_OWNER")
            _CONTEXTS_CHECK(self)
            return True
        except BaseException as error:
            self._stop(_issue(error, "LEDGER_OWNER"))
            return False

    def _receipt_check(self, invocation, receipt, returned, slot, before, after):
        _need(type(invocation) is _Invocation and type(receipt) is _Receipt, "LEDGER_OWNER")
        # Alle eigenen Primitive vor Equality/Identitätsabgleich.
        for value in (invocation, receipt):
            _need(type(value.owner) is object and type(value.ledger) is LocalLedger
                  and type(value.slot) is _Slot and type(value.context) is _CONTEXT_CLASS,
                  "LEDGER_OWNER")
            _baseline_shape(value.baseline)
            _integer(value.sequence, 11)
            _integer(value.before, 11)
            _integer(value.after, 11)
        for flag in (invocation.attempted, invocation.completed, invocation.consumed):
            _need(type(flag) is bool, "LEDGER_OWNER")
        _need(returned is receipt and invocation.receipt is receipt
              and receipt.invocation is invocation and self._active is invocation
              and invocation.owner is receipt.owner is self._owner
              and invocation.ledger is receipt.ledger is self
              and invocation.slot is receipt.slot is slot
              and invocation.context is receipt.context is slot.context
              and invocation.baseline is receipt.baseline is slot.baseline
              and invocation.sequence == receipt.sequence == slot.sequence
              and invocation.before == receipt.before == before
              and invocation.after == receipt.after == after
              and slot.state == before and self._busy
              and invocation.attempted and invocation.completed and not invocation.consumed,
              "LEDGER_OWNER")

    def _run(self, slot, before, after, failure_cleanup=False):
        invocation = None
        hold = self._report
        post, receipt_check, consumed_slot = hold[12]
        # Unabhängige aktive Codefolge: nach Callback keine zu prüfende
        # Pythoncheckerfunktion vor diesem lexikalischen Ankercheck aufrufen.
        chosen_anchor, core_functions, core_classes, core_namespaces = hold[9]
        natives = hold[7]
        native_type, native_len, native_tuple = natives[3], natives[7], natives[4]
        native_all, native_zip, native_max = natives[12], natives[9], natives[13]
        dict_type, str_type, tuple_type, int_type = natives[11], natives[6], natives[4], natives[5]
        function_type, cell_type, error_type = natives[0], natives[14], natives[15]
        value_error_type = natives[16]
        class_dict, class_mro, class_bases = natives[17:20]
        ledger_class, ledger_fields = hold[13], hold[3]
        if native_type(self) is not ledger_class:
            raise value_error_type("LEDGER_OWNER") from None
        missing = natives[2]()
        def get_field(instance, name):
            try:
                return ledger_fields[name].__get__(instance)
            except error_type:
                return missing
        def set_field(instance, name, value):
            ledger_fields[name].__set__(instance, value)
        def get_slot_field(instance, name):
            try:
                return hold[4][name].__get__(instance)
            except error_type:
                return missing
        allowed_issues = self._report[2]
        signal_provider, signal_both, signal_encoder, signal_cleanup = self._report[8]
        first_before, final_before, rank_before = get_field(self, "_first"), get_field(self, "_final"), get_field(self, "_rank")
        bookings_before = get_field(self, "_bookings")
        def check_core():
            core_ok = True
            candidate = get_field(self, "_anchors")
            anchor_class, anchor_fields = hold[14]
            if native_type(candidate) is not anchor_class or candidate is not chosen_anchor:
                core_ok = False
            for name, snapshot in (("functions", core_functions), ("classes", core_classes),
                                    ("namespaces", core_namespaces)):
                try:
                    current_snapshot = anchor_fields[name].__get__(chosen_anchor)
                except error_type:
                    current_snapshot = missing
                if current_snapshot is not snapshot:
                    core_ok = False
            # Keine Equality fremder Keys/Werte und keine fremden Checkerdispatches.
            for namespace, snapshot in core_namespaces:
                if native_type(namespace) is not dict_type or native_len(namespace) != native_len(snapshot) or native_len(namespace) > 256:
                    core_ok = False
                    break
                keys = native_tuple(namespace)
                if not native_all(native_type(key) is str_type for key in keys):
                    core_ok = False
                    break
                for key, (old_key, old_value) in native_zip(keys, snapshot):
                    if key != old_key or namespace[key] is not old_value:
                        core_ok = False
            for cls, snapshot, mro, bases in core_classes:
                if native_type(cls) is not native_type:
                    core_ok = False
                    continue
                namespace = class_dict.__get__(cls, native_type)
                keys = native_tuple(namespace) if native_len(namespace) <= 256 else ()
                if (native_len(keys) != native_len(snapshot) or not native_all(native_type(key) is str_type for key in keys)
                        or class_mro.__get__(cls, native_type) is not mro
                        or class_bases.__get__(cls, native_type) is not bases):
                    core_ok = False
                    continue
                for key, (old_key, old_value) in native_zip(keys, snapshot):
                    if key != old_key or namespace[key] is not old_value:
                        core_ok = False
            for fn, code, glob, defaults, values, kw, kw_values, closure, cells in core_functions:
                if (native_type(fn) is not function_type or fn.__code__ is not code
                        or fn.__globals__ is not glob or fn.__defaults__ is not defaults
                        or fn.__kwdefaults__ is not kw or fn.__closure__ is not closure):
                    core_ok = False
                    continue
                if defaults is not None and (native_type(defaults) is not tuple_type
                        or native_len(defaults) != native_len(values)
                        or not native_all(a is b for a, b in native_zip(defaults, values))):
                    core_ok = False
                if kw is not None:
                    if native_type(kw) is not dict_type or native_len(kw) != native_len(kw_values) or native_len(kw) > 256:
                        core_ok = False
                    else:
                        keys = native_tuple(kw)
                        if not native_all(native_type(key) is str_type for key in keys):
                            core_ok = False
                        else:
                            for key, (old_key, old_value) in native_zip(keys, kw_values):
                                if key != old_key or kw[key] is not old_value:
                                    core_ok = False
                for cell, value in cells:
                    try:
                        if native_type(cell) is not cell_type or cell.cell_contents is not value:
                            core_ok = False
                    except value_error_type:
                        core_ok = False
            return core_ok
        core_ok = True
        set_field(self, "_busy", True)
        if failure_cleanup or before == 10:
            hold[4]["cleanup_attempted"].__set__(slot, True)
            set_field(self, "_cleanup", get_field(self, "_cleanup") + 1)
        try:
            callback_error = None
            controls_changed = False
            controls_malformed = False
            core_ok = check_core()
            if core_ok:
                _ANCHOR_CHECK(self._anchors)
                _CONTEXTS_CHECK(self)
                _need(type(self._adapter) is _SyntheticAdapter and self._adapter.hook is self._hook,
                      "LEDGER_OWNER")
                _need(self._adapter._owner is self._owner, "LEDGER_OWNER")
                invocation = _Invocation(self, slot, before, after)
                receipt = invocation.receipt
                self._active = invocation
                if before == 1 and not failure_cleanup:
                    slot.start_attempted = True
                # Unveränderliche lokale Authority aller eigenen Slotwerte;
                # keine Caller-K-Werte oder Ressourcen werden repariert.
                own_slots = get_field(self, "_slots")
                slot_fields = hold[4]
                control_names = ("state", "sequence", "bits", "start_attempted",
                                 "cleanup_attempted", "cleanup_complete")
                slot_before = native_tuple((item, item.context, item.baseline,
                    native_tuple(slot_fields[name].__get__(item) for name in control_names))
                    for item in own_slots)
                counter_names = ("_index", "_starts", "_commands", "_bookings", "_cleanup")
                counters_before = native_tuple(get_field(self, name) for name in counter_names)
                cause_names = ("_first", "_final", "_rank", "_terminal")
                cause_before = native_tuple(get_field(self, name) for name in cause_names)
                returned = None
                callback_error = None
                try:
                    returned = _ADAPTER_INVOKE(self._adapter, invocation)
                except error_type as error:
                    callback_error = error
                # Alle eigenen Primitiven vor ihren Gleichheitsvergleichen.
                current_counters = native_tuple(get_field(self, name) for name in counter_names)
                current_cause = native_tuple(get_field(self, name) for name in cause_names)
                counter_forms = native_all(native_type(value) is int_type and 0 <= value <= limit
                    for value, limit in native_zip(current_counters, (2, 3, 9, 42, 3)))
                cause_forms = (native_type(current_cause[2]) is int_type and 0 <= current_cause[2] <= 3
                    and native_all(native_type(current_cause[i]) is str_type
                                   and native_len(current_cause[i]) <= 32 for i in (0, 1, 3)))
                slot_current = native_tuple(native_tuple(get_slot_field(item, name)
                    for name in control_names) for item, _, _, _ in slot_before)
                slot_forms = native_all(
                    native_all(native_type(v) is int_type and 0 <= v <= maximum
                               for v, maximum in native_zip(values[:3], (11, 11, 31)))
                    and native_all(native_type(v) is natives[10] for v in values[3:])
                    for values in slot_current)
                controls_malformed = not counter_forms or not cause_forms or not slot_forms
                reentered = (cause_forms and cause_before[0] == ""
                    and current_cause == ("LEDGER_REENTRANT", "LEDGER_REENTRANT", 0, "FAILED"))
                expected_counters = counters_before[:3] + (counters_before[3] + (1 if reentered else 0),
                                                          counters_before[4])
                controls_changed = (get_field(self, "_slots") is not own_slots
                    or not counter_forms or current_counters != expected_counters
                    or not cause_forms or (not reentered and current_cause != cause_before))
                for (item, context_before, baseline_before, values_before), values in native_zip(slot_before, slot_current):
                    if (not slot_forms or values != values_before
                            or get_slot_field(item, "context") is not context_before
                            or get_slot_field(item, "baseline") is not baseline_before):
                        controls_changed = True
                    # Nur unerlaubte eigene Callbackänderungen verwerfen; bereits
                    # gebuchte Reservierungen/Versuche bleiben unverändert erhalten.
                    for name, value in native_zip(control_names, values_before):
                        slot_fields[name].__set__(item, value)
                    slot_fields["context"].__set__(item, context_before)
                    slot_fields["baseline"].__set__(item, baseline_before)
                set_field(self, "_slots", own_slots)
                for name, value in native_zip(counter_names, expected_counters):
                    set_field(self, name, value)
                for name, value in native_zip(cause_names, current_cause if reentered else cause_before):
                    set_field(self, name, value)
            core_ok = core_ok and check_core()
            if not core_ok:
                # Gehaltenes natives setattr statt eines veränderten _stop/_post.
                typ = native_type(callback_error)
                label, rank = "LEDGER_OWNER", 0
                if typ is signal_provider or typ is signal_both:
                    label, rank = "HASH_PROVIDER_BINDING", 2
                elif typ is signal_encoder:
                    label, rank = "REPORT_ENCODER_BINDING", 1
                cleanup_unknown = failure_cleanup or before == 10 or typ is signal_cleanup
                if cleanup_unknown:
                    label, rank = "LEDGER_CLEANUP", 3
                current_first = get_field(self, "_first")
                current_bookings = get_field(self, "_bookings")
                valid_first = (native_type(current_first) is str_type and native_len(current_first) <= 32
                               and current_first in allowed_issues)
                set_field(self, "_first", current_first if valid_first else (first_before or label))
                set_field(self, "_final", label if rank >= rank_before else final_before)
                set_field(self, "_rank", native_max(rank, rank_before))
                set_field(self, "_terminal", "UNKNOWN" if cleanup_unknown else "FAILED")
                if not first_before and not valid_first:
                    set_field(self, "_bookings", bookings_before + 1)
                elif native_type(current_bookings) is int_type and 0 <= current_bookings <= 42:
                    set_field(self, "_bookings", current_bookings)
                return
            if callback_error is not None:
                raise callback_error
            post_ok = post(self)
            if not post_ok:
                return
            if controls_changed:
                raise LedgerRejected("LEDGER_FORM" if controls_malformed else "LEDGER_OWNER") from None
            receipt_check(self, invocation, receipt, returned, slot, before, after)
            if not self._terminal:
                # Reservierungsbit wird nach Prüferabschluss, vor späterem Write gebucht.
                if after in (3, 5, 7):
                    bit = {3: 2, 5: 4, 7: 8}[after]
                    _need(not slot.bits & bit, "LEDGER_CONSUMED")
                    slot.bits |= bit
                    self._commands += 1
                if after == 10:
                    _need(not slot.bits & 16, "LEDGER_CONSUMED")
                    slot.bits |= 16
                slot.state, slot.sequence = after, slot.sequence + 1
                self._bookings += 1
            elif failure_cleanup:
                self._bookings += 1
            if (failure_cleanup or before == 10) and post_ok:
                slot.cleanup_complete = True
            invocation.consumed = True
        except BaseException as error:
            typ = type(error)
            if typ is _SyntheticCleanupUnknown:
                self._stop("LEDGER_CLEANUP", 3, True)
            elif typ in (_SyntheticPartial, _SyntheticUnknown):
                self._stop("LEDGER_INTERNAL", unknown=True)
            elif typ in (_SyntheticProviderLoss, _SyntheticBothLoss):
                self._stop("HASH_PROVIDER_BINDING", 2)
            elif typ is _SyntheticEncoderLoss:
                self._stop("REPORT_ENCODER_BINDING", 1)
            elif typ is LedgerRejected:
                self._stop(_issue(error))
            else:
                self._stop("LEDGER_INTERNAL")
            if failure_cleanup or before == 10:
                self._stop("LEDGER_CLEANUP", 3, True)
            if invocation is not None:
                object.__setattr__(invocation, "consumed", True)
        finally:
            if core_ok:
                final_post_ok = post(self)
                if (failure_cleanup or before == 10) and not final_post_ok:
                    slot.cleanup_complete = False
                    self._stop("LEDGER_CLEANUP", 3, True)
            set_field(self, "_active", None)
            set_field(self, "_busy", False)
            if invocation is not None:
                consumed_slot.__set__(invocation, True)

    def advance(self):
        constructor, code, obj, type, tuple, int, str, len, enum, zip, bool = self._report[7][:11]
        held = self._report[:7]
        report = constructor(code, {"__builtins__": {
            "object": obj, "type": type, "tuple": tuple, "int": int,
            "str": str, "len": len, "enumerate": enum, "zip": zip}})
        stop = constructor(self._report[11], {"_ISSUES": held[2], "__builtins__": {
            "object": obj, "type": type, "int": int, "str": str, "len": len}},
            argdefs=(0, False, None))
        hold = self._report
        if (type(self._busy) is not bool or type(self._terminal) is not str
                or len(self._terminal) > 32 or self._terminal not in ("", "FAILED", "UNKNOWN")):
            stop(self, "LEDGER_OWNER", 0, True, hold)
            return report(self, *held)
        if self._busy:
            stop(self, "LEDGER_REENTRANT", 0, False, hold)
            return report(self, *held)
        if self._terminal:
            return report(self, *held)
        try:
            _ANCHOR_CHECK(self._anchors)
            _CONTEXTS_CHECK(self)
            slot = self._slots[self._index]
            if slot.state == 11:
                if self._index + 1 == len(self._slots):
                    return report(self, *held)
                self._index += 1
                slot = self._slots[self._index]
            if slot.state == 0:
                _need(not slot.bits & 1, "LEDGER_CONSUMED")
                slot.bits |= 1
                self._starts += 1
                slot.state = slot.sequence = 1
                self._bookings += 1
            else:
                _LEDGER_RUN(self, slot, slot.state, slot.state + 1)
        except BaseException as error:
            stop(self, _issue(error), 0, False, hold)
            _LEDGER_POST(self)
        return report(self, *held)

    def failure_cleanup(self):
        constructor, code, obj, type, tuple, int, str, len, enum, zip, bool = self._report[7][:11]
        held = self._report[:7]
        report = constructor(code, {"__builtins__": {
            "object": obj, "type": type, "tuple": tuple, "int": int,
            "str": str, "len": len, "enumerate": enum, "zip": zip}})
        stop = constructor(self._report[11], {"_ISSUES": held[2], "__builtins__": {
            "object": obj, "type": type, "int": int, "str": str, "len": len}},
            argdefs=(0, False, None))
        hold = self._report
        if (type(self._busy) is not bool or type(self._terminal) is not str
                or len(self._terminal) > 32 or self._terminal not in ("", "FAILED", "UNKNOWN")
                or type(self._slots) is not tuple or not 1 <= len(self._slots) <= 3
                or type(self._index) is not int or not 0 <= self._index < len(self._slots)
                or type(self._slots[self._index]) is not held[6]):
            stop(self, "LEDGER_OWNER", 0, True, hold)
            return report(self, *held)
        if self._busy:
            stop(self, "LEDGER_REENTRANT", 0, False, hold)
            return report(self, *held)
        slot = self._slots[self._index]
        if (type(slot.start_attempted) is not bool or type(slot.cleanup_attempted) is not bool
                or type(slot.bits) is not int or not 0 <= slot.bits <= 31
                or type(slot.state) is not int or not 0 <= slot.state <= 11
                or type(slot.sequence) is not int or not 0 <= slot.sequence <= 11
                or type(self._bookings) is not int or not 0 <= self._bookings <= 42
                or type(self._cleanup) is not int or not 0 <= self._cleanup <= 3
                or type(self._starts) is not int or not 0 <= self._starts <= 3
                or type(self._commands) is not int or not 0 <= self._commands <= 9
                or type(self._rank) is not int or not 0 <= self._rank <= 3):
            stop(self, "LEDGER_OWNER", 0, True, hold)
            return report(self, *held)
        if not self._terminal or not slot.start_attempted or slot.cleanup_attempted:
            return report(self, *held)
        if not slot.bits & 16:
            slot.bits |= 16
            self._bookings += 1
        code, glob, defaults = hold[10]
        run = constructor(code, glob, argdefs=defaults)
        run(self, slot, slot.state, slot.state, True)
        return report(self, *held)

    def diagnose(self):
        constructor, code, obj, type, tuple, int, str, len, enum, zip, bool = self._report[7][:11]
        held = self._report[:7]
        report = constructor(code, {"__builtins__": {
            "object": obj, "type": type, "tuple": tuple, "int": int,
            "str": str, "len": len, "enumerate": enum, "zip": zip}})
        return report(self, *held)


def create_local_ledger(contexts, *, adapter) -> LocalLedger:
    """Vollständige Vorwahl vor jedem lokalen Ledger-/Startobjekt."""
    try:
        _need(type(contexts) is tuple and 1 <= len(contexts) <= 3, "LEDGER_LIMIT")
        _need(type(adapter) is _SyntheticAdapter, "LEDGER_OWNER")
        _need(adapter._owner is None, "LEDGER_CONSUMED")
        _need(adapter.hook is None or type(adapter.hook) is FunctionType, "LEDGER_OWNER")
        anchors = _Anchors(adapter.hook)
        anchors.check()
        baselines = tuple(_primitive(context) for context in contexts)
        # Sämtliche Primitive aller Slots sind jetzt geschlossen.
        for context in contexts:
            _CONTEXT_CHECK(context)
        for index, row in enumerate(baselines):
            _need(row[5:] == (index + 1, _ENTRIES[index], "PRE_IMPORT"), "LEDGER_CONTEXT")
            _need(row[:5] == baselines[0][:5], "LEDGER_CONTEXT")
        anchors.check()
        return LocalLedger(contexts, baselines, adapter, anchors, _CREATE_KEY)
    except BaseException as error:
        issue = _issue(error, "LEDGER_FORM")
        raise LedgerRejected(issue) from None


_CONTEXT_CLASS = binding.BindingContext
_DESCRIPTOR_CLASS = binding.SourceDescriptor
_CONTEXT_CHECK = binding._context
_ENTRIES = binding.ENTRIES
_ADAPTER_INVOKE = _SyntheticAdapter._invoke
_ANCHOR_CHECK = _Anchors.check
_LEDGER_POST = LocalLedger._post
_LEDGER_RUN = LocalLedger._run
_CONTEXTS_CHECK = LocalLedger._contexts_check
_RECEIPT_CHECK = LocalLedger._receipt_check
_DIAGNOSTIC_CODE = _diagnostic.__code__
_LD_DESCRIPTORS = tuple((name, LocalLedger.__dict__[name]) for name in LocalLedger.__slots__)
_SLOT_DESCRIPTORS = tuple((name, _Slot.__dict__[name]) for name in _Slot.__slots__)
_DIAG_DESCRIPTORS = tuple((name, LedgerDiagnostic.__dict__[name]) for name in LedgerDiagnostic.__slots__)
_INV_COMPLETED = _Invocation.__dict__["completed"]
_INV_CONSUMED = _Invocation.__dict__["consumed"]
_HELD_CLASSES = (_CONTEXT_CLASS, _DESCRIPTOR_CLASS, LocalLedger, LedgerDiagnostic,
                 _Anchors, _Slot, _Invocation, _Receipt, _SyntheticAdapter,
                 LedgerRejected, _SyntheticPartial, _SyntheticUnknown,
                 _SyntheticCleanupUnknown, _SyntheticProviderLoss,
                 _SyntheticEncoderLoss, _SyntheticBothLoss)
_HELD_FUNCTIONS = (_need, _issue, _text, _integer, _baseline_shape, _primitive, _namespace,
                   _same_namespace, _class_namespace, _function_snapshot, _function_check,
                   _diagnostic, create_local_ledger, _CONTEXT_CHECK, binding._need, binding._hex,
                   binding._text, binding._integer, binding._selector, binding._tuple)
