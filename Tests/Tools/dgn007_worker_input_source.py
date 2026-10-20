"""Reine Workerquellenfolge; keine OS-I/O oder Workerausführung beim Erzeugen."""
import ast
import hashlib
import tokenize

import dgn007_control_bootstrap_source as base


_INLINE_WORKER_INPUT = r'''
_WORKER_INPUT_INITIALIZED = False
_WORKER_INPUT_MARKER = None
_WORKER_INPUT_IO_CAP = 1088
_WORKER_INPUT_BYTE_CAP = 1064960


def _worker_input_namespace(module):
    _inline_need(type(module) is _MODULE_CLASS, "WORKER_INPUT_BINDING")
    namespace = module.__dict__
    _inline_need(type(namespace) is dict and len(namespace) <= 16368, "WORKER_INPUT_BINDING")
    for key in namespace:
        _inline_need(type(key) is str and len(key) <= 4096 and "\0" not in key,
                     "WORKER_INPUT_BINDING")
        _inline_need(len(key.encode("utf-8", "strict")) <= 4096, "WORKER_INPUT_BINDING")
    return namespace


def _worker_input_function(function, namespace):
    if type(function) is type(_worker_input_function):
        _inline_need(function.__globals__ is namespace, "WORKER_INPUT_BINDING")
        return ("FUNCTION", _worker_profile_function(function, [0]))
    _inline_need(type(function) is type(struct.pack), "WORKER_INPUT_BINDING")
    return ("BUILTIN", function, function.__self__)


def _worker_input_function_check(before, function, namespace):
    _inline_need(function is (before[1][0] if before[0] == "FUNCTION" else before[1]),
                 "WORKER_INPUT_BINDING")
    after = _worker_input_function(function, namespace)
    _inline_need(after[0] == before[0], "WORKER_INPUT_BINDING")
    if before[0] == "FUNCTION":
        _inline_need(_worker_profile_function_equal(before[1], after[1]), "WORKER_INPUT_BINDING")
    else:
        _inline_need(after[1] is before[1] and after[2] is before[2], "WORKER_INPUT_BINDING")


def _worker_input_entry():
    return ("REJECTED_WORKER_INPUT", "WORKER_INPUT_BINDING", None)


def _worker_input_seal():
    return ("REJECTED_WORKER_INPUT", "WORKER_INPUT_BINDING", None)


def _worker_input_report_handoff(held, marker, report):
    raise RuntimeError()


def _initialize_worker_input_control():
    global _WORKER_INPUT_INITIALIZED, _WORKER_INPUT_MARKER
    global _worker_input_entry, _worker_input_seal, _worker_input_report_handoff
    if _WORKER_INPUT_INITIALIZED is not False:
        _WORKER_INPUT_MARKER = None
        return ("REJECTED_WORKER_INPUT", "WORKER_INPUT_ALREADY_INITIALIZED", None)
    _WORKER_INPUT_INITIALIZED = True
    try:
        profile = _WORKER_PROFILE_BINDING
        _worker_profile_check(profile)
        namespace = globals()
        filesystem = profile[1].get("os")
        filesystem_namespace = _worker_input_namespace(filesystem)
        reads, writes = filesystem_namespace.get("read"), filesystem_namespace.get("write")
        read_state = _worker_input_function(reads, filesystem_namespace)
        write_state = _worker_input_function(writes, filesystem_namespace)
        _inline_need(type(reads.__name__) is str and reads.__name__ == "read"
                     and type(writes.__name__) is str and writes.__name__ == "write", "WORKER_INPUT_BINDING")
        hooks = sys.__dict__.get("path_hooks")
        _inline_need(type(hooks) is list and len(hooks) == 2
                     and hooks[0] is profile[1].get("zipimporter")
                     and type(hooks[1]) is type(_worker_input_function), "WORKER_INPUT_BINDING")
        marker = object()
        _WORKER_INPUT_MARKER = marker
        # Nur dieser private Halter schreitet fort. Seine Identität und alle
        # Closurezell-Inhalte bleiben nach dem Report-Scriptsnapshot stabil.
        state = [False, False, False, 0, 0, 0, False]
        owner = (namespace, marker, state, profile, filesystem, reads, writes,
                 read_state, write_state, hooks, hooks[0], hooks[1],
                 _worker_report_check, _worker_report_check.__code__)
        _worker_input_entry, _worker_input_seal, _worker_input_report_handoff = _worker_input_factory(owner)
        return ("BOUND_WORKER_INPUT_CONTROL", "NONE", None)
    except BaseException:
        _WORKER_INPUT_MARKER = None
        return ("REJECTED_WORKER_INPUT", "WORKER_INPUT_BINDING", None)


def _worker_input_factory(owner):
    run, run_code = _worker_input_run, _worker_input_run.__code__
    frame = None
    def entry():
        if run.__code__ is not run_code or run.__globals__ is not owner[0]:
            owner[2][2] = True
            return ("REJECTED_WORKER_INPUT", "WORKER_INPUT_BINDING", None)
        return run(owner, frame)
    def handoff(held, marker, report):
        nonlocal frame
        if frame is not None or owner[2][0] is not False or owner[2][1] is not False:
            owner[2][2] = True
            raise RuntimeError()
        _inline_need(type(held) is tuple and len(held) == 6
                     and type(marker) is tuple and len(marker) == 6
                     and type(report) is type(_worker_input_factory)
                     and report.__globals__ is owner[0], "WORKER_INPUT_BINDING")
        # Direkte Übergabe aus der tatsächlichen Kernelinitialisierung, bevor
        # deren Scriptsnapshot diese endgültigen Closurezell-Inhalte hält.
        frame = (held, marker, report, _worker_profile_function(report, [0]))
    def seal():
        state, namespace = owner[2], owner[0]
        if state[0] is not False or state[1] is not False or state[2] is not False:
            state[2] = True
            return ("REJECTED_WORKER_INPUT", "WORKER_INPUT_BINDING", None)
        state[1] = True
        try:
            _inline_need(namespace.get("_WORKER_INPUT_MARKER") is owner[1], "WORKER_INPUT_BINDING")
            check, code = owner[12:]
            if frame is None or check.__code__ is not code or check.__globals__ is not namespace:
                raise RuntimeError()
            check(frame[0], frame[1], False)
            _inline_need(namespace.get("_inline_observed_worker_report") is frame[2], "WORKER_INPUT_BINDING")
            return ("SEALED_WORKER_INPUT_CONTROL", "NONE", None)
        except BaseException:
            state[2] = True
            return ("REJECTED_WORKER_INPUT", "WORKER_INPUT_BINDING", None)
    return entry, seal, handoff


def _worker_input_run(owner, frame):
    namespace, marker, state, profile, filesystem, reads, writes = owner[:7]
    if (namespace.get("_WORKER_INPUT_MARKER") is not marker or state[0] is not False
            or state[1] is not True or state[2] is not False or frame is None):
        state[2] = True
        return ("REJECTED_WORKER_INPUT", "WORKER_INPUT_BINDING", None)
    state[0] = True
    result, issue = None, "WORKER_INPUT_REJECTED"
    def guard():
        check, code = owner[12:]
        if check.__code__ is not code or check.__globals__ is not namespace:
            raise RuntimeError()
        if type(state[6]) is not bool:
            raise RuntimeError()
        check(frame[0], frame[1], state[6])
        _inline_need(namespace.get("_WORKER_INPUT_MARKER") is marker
                     and state[0] is True and state[1] is True and state[2] is False,
                     "WORKER_INPUT_BINDING")
        _inline_need(sys.__dict__.get("path_hooks") is owner[9]
                     and len(owner[9]) == 2 and owner[9][0] is owner[10]
                     and owner[9][1] is owner[11], "WORKER_INPUT_BINDING")
        filesystem_namespace = _worker_input_namespace(filesystem)
        _worker_input_function_check(owner[7], filesystem_namespace.get("read"), filesystem_namespace)
        _worker_input_function_check(owner[8], filesystem_namespace.get("write"), filesystem_namespace)
        _inline_need(type(state[3]) is int and 0 <= state[3] <= _WORKER_INPUT_IO_CAP
                     and type(state[4]) is int and 0 <= state[4] <= _WORKER_INPUT_BYTE_CAP
                     and type(state[5]) is int and 0 <= state[5] <= 65536, "WORKER_INPUT_BINDING")
    def book():
        guard()
        _inline_need(state[3] < _WORKER_INPUT_IO_CAP, "WORKER_INPUT_LIMIT")
        state[3] += 1
    def read(size, *, eof=False):
        _inline_need(type(size) is int and 1 <= size <= 4096, "WORKER_INPUT_LIMIT")
        _inline_need((eof and size == 1) or state[4] + size <= _WORKER_INPUT_BYTE_CAP,
                     "WORKER_INPUT_LIMIT")
        book()
        try:
            value = reads(0, size)
        finally:
            guard()
        _inline_need(type(value) is bytes, "WORKER_INPUT_READ")
        _inline_need(len(value) <= size, "WORKER_INPUT_READ")
        state[4] += len(value)
        _inline_need(state[4] <= _WORKER_INPUT_BYTE_CAP, "WORKER_INPUT_LIMIT")
        return value
    def exact(size):
        _inline_need(type(size) is int and 0 <= size <= 131072, "WORKER_INPUT_LIMIT")
        pieces, missing = [], size
        while missing:
            piece = read(min(missing, 4096))
            _inline_need(len(piece) > 0, "WORKER_INPUT_EOF")
            pieces.append(piece)
            missing -= len(piece)
        return b"".join(pieces)
    def write(value):
        _inline_need(type(value) is bytes and 0 < len(value) <= 1024, "WORKER_INPUT_WRITE")
        offset = 0
        while offset < len(value):
            _inline_need(state[5] + len(value) - offset <= 65536, "WORKER_INPUT_LIMIT")
            book()
            try:
                count = writes(1, value[offset:])
            finally:
                guard()
            _inline_need(type(count) is int and 0 < count <= len(value) - offset, "WORKER_INPUT_WRITE")
            state[5] += count
            _inline_need(state[5] <= 65536, "WORKER_INPUT_LIMIT")
            offset += count
    def call(name, status, *args, **kwargs):
        guard()
        value = namespace[name](*args, **kwargs)
        guard()
        _inline_need(type(value) is tuple and len(value) == 3
                     and value[:2] == (status, "NONE"), "WORKER_INPUT_REJECTED")
        return value[2]
    def command(kind, context):
        pieces = []
        for _ in range(256):
            piece = read(1)
            _inline_need(len(piece) == 1, "WORKER_INPUT_EOF")
            pieces.append(piece)
            if piece == b"\n":
                return call("_inline_command_match", "MATCHED_DECLARED_COMMAND", b"".join(pieces),
                    expected_kind=kind, expected_context=context, expected_format=_COMMAND_FORMAT)
        raise RuntimeError()
    try:
        guard()
        header = exact(16)
        magic, metadata_size, body_size = _INLINE_HEADER.unpack(header)
        _inline_need(magic == _INLINE_MAGIC and 0 < metadata_size <= 16368
                     and body_size <= _INLINE_BODY_CAP and 16 + metadata_size + body_size <= _INLINE_FRAME_CAP,
                     "WORKER_INPUT_HEADER")
        metadata = exact(metadata_size)
        guard()
        syntax = call("_inline_metadata_syntax", "VALID_METADATA_SYNTAX", header, metadata)
        _semantic_hex(syntax[2][3], 64)
        token = bytes.fromhex(syntax[2][3])
        joined = header + metadata
        chunks = tuple(joined[n:n + 1024] for n in range(0, len(joined), 1024))
        _inline_need(_worker_profile_function_equal(frame[3], _worker_profile_function(frame[2], [0])),
                     "WORKER_INPUT_BINDING")
        state[6] = True
        report = frame[2](chunks, token=token, separately_known_filefinder_hook=owner[11])
        guard()
        _inline_need(type(report) is tuple and len(report) == 3
                     and report[:2] == ("OBSERVED_WORKER_REPORT", "NONE"), "WORKER_INPUT_REJECTED")
        actual, first, records = report[2][2:]
        context = actual[2]
        digest = call("_inline_context_digest", "FORMATTED_CONTEXT_DIGEST", context,
                      expected_format=_COMMAND_FORMAT)
        commands = tuple(_report_json((kind, context[5], context[3], digest), frame[0][3]) + b"\n"
                         for kind in _COMMAND_KINDS)
        guard()
        _inline_need(all(len(row) <= 256 for row in commands)
                     and len(joined) + body_size + sum(len(row) for row in commands) <= _WORKER_INPUT_BYTE_CAP,
                     "WORKER_INPUT_LIMIT")
        for row in records:
            write(row)
        command("BODY_RELEASE", context)
        bodies = tuple(exact(row[3]) for row in actual[0][5])
        command("BODY_END", context)
        held = call("_inline_receive_declared_bodies", "RECEIVED_DECLARED_BODIES", chunks, bodies,
                    expected_format=_RECEIVE_FORMAT, expected_input=actual[0],
                    expected_worker=actual[1], expected_context=context)
        second = call("_inline_observe_selected_worker_profile", "OBSERVED_SELECTED_WORKER_PROFILE",
                      actual[1], token=token, separately_known_filefinder_hook=owner[11])
        _inline_need(second.scalars == first.scalars, "WORKER_INPUT_PROFILE")
        complete = _report_json(("INPUT_COMPLETE", context[5], context[3], digest), frame[0][3]) + b"\n"
        guard()
        _inline_need(len(complete) <= 256, "WORKER_INPUT_LIMIT")
        write(complete)
        command("IMPORT_RELEASE", context)
        _inline_need(read(1, eof=True) == b"", "WORKER_INPUT_EOF")
        guard()
        result = (held, first, second)
    except BaseException:
        pass
    try:
        guard()
    except BaseException:
        issue, result = "WORKER_INPUT_BINDING", None
    if result is None:
        state[2] = True
        return ("REJECTED_WORKER_INPUT", issue, None)
    return ("RECEIVED_WORKER_INPUTS", "NONE", result)


def _worker_input_main():
    result = _worker_input_entry()
    if result[:2] != ("RECEIVED_WORKER_INPUTS", "NONE"):
        raise SystemExit(1)
'''


def _compact_indentation(text):
    original = tuple(text.splitlines(keepends=True))
    lines, seen = list(original), set()
    ignored = (tokenize.INDENT, tokenize.DEDENT, tokenize.NEWLINE,
               tokenize.NL, tokenize.ENDMARKER, tokenize.ENCODING)
    for token in tokenize.generate_tokens(iter(original).__next__):
        if token.type in ignored or token.start[0] in seen:
            continue
        row, column = token.start
        seen.add(row)
        prefix = original[row - 1][:column]
        if prefix and not prefix.strip():
            base._need(set(prefix) == {" "} and column % 4 == 0, "TEMPLATE_FORM")
            lines[row - 1] = " " * (column // 4) + original[row - 1][column:]
    return "".join(lines)


def build_worker_input_control_bootstrap(profile_raw, *, logical_profile,
                                         expected_soabi, expected_destshared):
    """Neue Quellenroute ohne zusätzliche Scriptimporte oder Lauf-/Trustattestation."""
    selected = base.build_inline_worker_report_control_bootstrap(
        profile_raw, logical_profile=logical_profile, expected_soabi=expected_soabi,
        expected_destshared=expected_destshared)
    text = selected.source.decode("utf-8", "strict")
    old = ('\nif __name__ == "__main__":\n    _CONTROL_RESULT = _load_bound_control()\n'
           '    _WORKER_PROFILE_INIT_RESULT = _initialize_worker_profile_control()\n'
           '    _initialize_worker_report_control()\n')
    base._need(text.count(old) == 1, "TEMPLATE_FORM")
    handoff = '        _WORKER_REPORT_BINDING = marker\n        script.append(_worker_report_script())\n'
    base._need(text.count(handoff) == 1, "TEMPLATE_FORM")
    text = text.replace(handoff, '        _WORKER_REPORT_BINDING = marker\n'
                        '        _worker_input_report_handoff(held, marker, entry)\n'
                        '        script.append(_worker_report_script())\n', 1)
    main = old.replace('    _initialize_worker_report_control()\n',
        '    _initialize_worker_input_control()\n    _initialize_worker_report_control()\n'
        '    _worker_input_seal()\n    _worker_input_main()\n')
    text = text.replace(old, '\n' + _INLINE_WORKER_INPUT + main, 1)
    # Ausschließlich die neue Ausgabe; keine Änderung vorhandener Quellenrouten.
    formatted = ast.unparse(ast.parse(text)) + '\n'
    source = _compact_indentation(formatted).encode("utf-8", "strict")
    base._need(len(source) <= base.MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return base.BootstrapSource(source, profile_raw, logical_profile,
                                hashlib.sha256(source).hexdigest(),
                                hashlib.sha256(profile_raw).hexdigest(), len(source))
