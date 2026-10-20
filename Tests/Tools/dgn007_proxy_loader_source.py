"""Additive Proxy-Loaderquelle; beim Erzeugen keine Kandidatenausführung."""
import ast
import hashlib
import tokenize

import dgn007_worker_input_source as inputs


_INLINE_PROXY_SOURCE = r'''
_PROXY_SOURCE_INITIALIZED = False
_PROXY_SOURCE_MARKER = None
_PROXY_LOADER_CLASS = None
_PROXY_MODULE = "docker_sqlcmd_proxy"
_PROXY_ORIGIN = "/dgn007/source/2/docker_sqlcmd_proxy.py"
_PROXY_CANDIDATES = ("run_dgn007_automated_setup", "execution_target", "docker_sqlcmd_proxy",
    "run_demo", "orchestrate_sessions", "sqlcmd_process", "Tests.Contracts.dgn007_capture_projection",
    "Tests.Contracts.dgn007_collector_transport", "Tests.Contracts.dgn007_prospective_acceptance",
    "Tests", "Tests.Contracts")


def _proxy_source_entry():
    return ("REJECTED_PROXY_SOURCE", "PROXY_SOURCE_BINDING", None)


def _proxy_input_handoff(io_owner, entry):
    raise RuntimeError()


def _proxy_eof_handoff(io_owner, frame, result):
    raise RuntimeError()


def _proxy_namespace(namespace):
    _inline_need(_dictionary(namespace) and all("\0" not in key for key in namespace),
                 "PROXY_SOURCE_BINDING")
    return namespace


def _proxy_spec_state(cls):
    _inline_need(type(cls) is type, "PROXY_SOURCE_BINDING")
    budget = [0]
    items = _worker_profile_items(_proxy_namespace(dict(_semantic_class_namespace(cls))), budget)
    methods = tuple(_worker_profile_function(value, budget) for _, value in items
                    if type(value) is type(_proxy_spec_state))
    return (cls, cls.__bases__, cls.__mro__, items, methods)


def _proxy_original(pair, namespace):
    function, code = pair
    if function.__code__ is not code or function.__globals__ is not namespace:
        raise RuntimeError()
    return function


def _proxy_guard(owner, packet):
    namespace, marker, state = owner[:3]
    io_owner, entry, entry_code = state[3][0]
    check, code = io_owner[12:]
    if check.__code__ is not code or check.__globals__ is not namespace:
        raise RuntimeError()
    if io_owner[2][6] is not True:
        raise RuntimeError()
    check(packet[1][0], packet[1][1], True)
    _inline_need(namespace.get("_PROXY_SOURCE_MARKER") is marker and state[0] is True
                 and state[1] is False and state[2] is False, "PROXY_SOURCE_BINDING")
    _inline_need(entry.__code__ is entry_code and entry.__globals__ is namespace,
                 "PROXY_SOURCE_BINDING")
    _inline_need(namespace.get("_WORKER_INPUT_MARKER") is io_owner[1]
                 and io_owner[2][0] is True and io_owner[2][1] is True
                 and io_owner[2][2] is False, "PROXY_SOURCE_BINDING")
    _inline_need(sys.__dict__.get("modules") is owner[11],
                 "PROXY_SOURCE_BINDING")
    _proxy_namespace(owner[11])
    _inline_need(sys.__dict__.get("path_hooks") is io_owner[9] and len(io_owner[9]) == 2
                 and io_owner[9][0] is io_owner[10] and io_owner[9][1] is io_owner[11],
                 "PROXY_SOURCE_BINDING")
    filesystem = _worker_input_namespace(io_owner[4])
    _worker_input_function_check(io_owner[7], filesystem.get("read"), filesystem)
    _worker_input_function_check(io_owner[8], filesystem.get("write"), filesystem)
    current = _worker_profile_items(_proxy_namespace(owner[3]), [0])
    _inline_need(len(current) == len(owner[4])
                 and all(a[0] == b[0] and a[1] is b[1] for a, b in zip(current, owner[4])),
                 "PROXY_SOURCE_BINDING")
    _worker_input_function_check(owner[7], owner[3].get("compile"), owner[3])
    _worker_input_function_check(owner[8], owner[3].get("exec"), owner[3])
    before, after = owner[10], _proxy_spec_state(owner[10][0])
    _inline_need(all(a is b for a, b in zip(before[:3], after[:3]))
                 and len(before[3]) == len(after[3])
                 and all(a[0] == b[0] and a[1] is b[1] for a, b in zip(before[3], after[3]))
                 and len(before[4]) == len(after[4])
                 and all(_worker_profile_function_equal(a, b) for a, b in zip(before[4], after[4])),
                 "PROXY_SOURCE_BINDING")
    _inline_need(type(io_owner[2][3]) is int and 0 <= io_owner[2][3] <= _WORKER_INPUT_IO_CAP
                 and type(io_owner[2][4]) is int and 0 <= io_owner[2][4] <= _WORKER_INPUT_BYTE_CAP
                 and type(io_owner[2][5]) is int and 0 <= io_owner[2][5] <= 65536,
                 "PROXY_SOURCE_BINDING")
    if state[5]:
        _proxy_original(owner[16], namespace)(owner, state[5][0])


def _proxy_binding(owner, invocation):
    raw, descriptor, context, module, spec, origin = invocation[:6]
    loader_class, loader, method, method_code = owner[2][6][0]
    _inline_need(type(module) is owner[9] and type(spec) is owner[10][0]
                 and type(loader) is loader_class and method.__code__ is method_code,
                 "PROXY_SOURCE_BINDING")
    md, sd = module.__dict__, spec.__dict__
    _proxy_namespace(md)
    _proxy_namespace(sd)
    _inline_need(md.get("__spec__") is spec and md.get("__loader__") is loader
                 and sd.get("loader") is loader and sd.get("submodule_search_locations") is None
                 and sd.get("loader_state") is None and sd.get("_set_fileattr") is True
                 and "__path__" not in md, "PROXY_SOURCE_BINDING")
    for value, expected in ((md.get("__name__"), _PROXY_MODULE), (md.get("__package__"), ""),
                            (md.get("__file__"), origin), (sd.get("name"), _PROXY_MODULE),
                            (sd.get("origin"), origin)):
        _inline_need(type(value) is str and value == expected, "PROXY_SOURCE_BINDING")
    _inline_need(type(raw) is bytes and type(descriptor) is tuple and type(context) is tuple
                 and type(origin) is str and origin == _PROXY_ORIGIN,
                 "PROXY_SOURCE_BINDING")
    _inline_need(md.get("__builtins__") is invocation[10], "PROXY_SOURCE_BINDING")
    items = _worker_profile_items(_proxy_namespace(invocation[10]), [0])
    _inline_need(len(items) == len(owner[4])
                 and all(a[0] == b[0] and a[1] is b[1] for a, b in zip(items, owner[4])),
                 "PROXY_SOURCE_BINDING")
    if invocation[8]:
        _inline_need(owner[11].get(_PROXY_MODULE) is module, "PROXY_SOURCE_BINDING")


def _proxy_write(owner, packet, value):
    guard = owner[13]
    def close():
        function, code = guard
        if function.__code__ is not code or function.__globals__ is not owner[0]:
            raise RuntimeError()
        function(owner, packet)
    close()
    _inline_need(type(value) is bytes and 0 < len(value) <= 256, "PROXY_SOURCE_WRITE")
    io_owner = owner[2][3][0][0]
    budget, writes = io_owner[2], io_owner[6]
    offset = 0
    while offset < len(value):
        close()
        _inline_need(budget[3] < _WORKER_INPUT_IO_CAP
                     and budget[5] + len(value) - offset <= 65536, "PROXY_SOURCE_LIMIT")
        budget[3] += 1
        try:
            count = writes(1, value[offset:])
        finally:
            close()
        _inline_need(type(count) is int and 0 < count <= len(value) - offset, "PROXY_SOURCE_WRITE")
        budget[5] += count
        offset += count


def _proxy_execute(owner, packet, module):
    guard = owner[13]
    def close():
        function, code = guard
        if function.__code__ is not code or function.__globals__ is not owner[0]:
            raise RuntimeError()
        function(owner, packet)
    close()
    invocation = owner[2][5][0]
    _inline_need(module is invocation[3] and invocation[6] is None
                 and invocation[7] is None and invocation[11] is False
                 and invocation[12] is True and invocation[13] is False, "PROXY_SOURCE_BINDING")
    invocation[13] = True
    close()
    try:
        code = owner[5](invocation[0], invocation[5], "exec", dont_inherit=True, optimize=0)
    finally:
        close()
    _inline_need(type(code) is type(_proxy_execute.__code__)
                 and type(code.co_filename) is str and code.co_filename == invocation[5],
                 "PROXY_SOURCE_BINDING")
    invocation[6] = code
    try:
        owner[6](code, module.__dict__)
    finally:
        close()
    _inline_need(invocation[6] is code and invocation[7] is None, "PROXY_SOURCE_BINDING")
    invocation[7] = code


def _proxy_source_run(owner, packet):
    namespace, marker, state = owner[:3]
    guard, writer = owner[13], owner[14]
    def close():
        function, code = guard
        if function.__code__ is not code or function.__globals__ is not namespace:
            raise RuntimeError()
        function(owner, packet)
    issue, result = "PROXY_SOURCE_REJECTED", None
    try:
        close()
        received, first, second = packet[0]
        actual, bodies = received[2:]
        context, descriptor, raw = actual[2], actual[0][5][2], bodies[2]
        _inline_need(actual[1][:3] == (2, _PROXY_MODULE, "PRE_IMPORT")
                     and descriptor[:3] == (2, _PROXY_MODULE, "Tests/Runtime/docker_sqlcmd_proxy.py")
                     and not state[5], "PROXY_SOURCE_SELECTION")
        _inline_need(all(name not in owner[11] for name in _PROXY_CANDIDATES), "PROXY_SOURCE_BINDING")
        digest = _inline_context_digest(context, expected_format=_COMMAND_FORMAT)
        close()
        _inline_need(type(digest) is tuple and digest[:2] == ("FORMATTED_CONTEXT_DIGEST", "NONE"),
                     "PROXY_SOURCE_REJECTED")
        loader_class, loader, method, method_code = state[6][0]
        module = owner[9](_PROXY_MODULE)
        close()
        spec = owner[10][0](_PROXY_MODULE, loader, origin=_PROXY_ORIGIN, is_package=False)
        close()
        _inline_need(type(module) is owner[9] and type(spec) is owner[10][0], "PROXY_SOURCE_BINDING")
        _proxy_namespace(module.__dict__)
        _proxy_namespace(spec.__dict__)
        spec.__dict__["_set_fileattr"] = True
        builtin_copy = dict(owner[4])
        module.__dict__.update(__name__=_PROXY_MODULE, __package__="", __loader__=loader,
            __spec__=spec, __file__=_PROXY_ORIGIN, __builtins__=builtin_copy)
        invocation = [raw, descriptor, context, module, spec, _PROXY_ORIGIN,
                      None, None, False, False, builtin_copy, False, False, False]
        state[5].append(invocation)
        close()
        owner[11][_PROXY_MODULE] = module
        invocation[8] = True
        close()
        fields = (2, 1, "SOURCE", 2, digest[2], descriptor[4], 2, 1)
        begin = _report_json(("BEGIN",) + fields, packet[1][0][3]) + b"\n"
        close()
        _proxy_original(writer, namespace)(owner, packet, begin)
        close()
        invocation[11] = True
        _inline_need(method.__code__ is method_code and method.__globals__ is namespace,
                     "PROXY_SOURCE_BINDING")
        method(loader, module)
        close()
        _inline_need(invocation[6] is not None and invocation[7] is invocation[6], "PROXY_SOURCE_BINDING")
        complete = _report_json(("COMPLETE",) + fields, packet[1][0][3]) + b"\n"
        close()
        _proxy_original(writer, namespace)(owner, packet, complete)
        close()
        invocation[9] = True
        result = (module, spec, loader, invocation[6], raw, begin, complete)
    except BaseException:
        pass
    try:
        close()
    except BaseException:
        issue, result = "PROXY_SOURCE_BINDING", None
    if result is None:
        # Ausschließlich eigener identischer Slot; fremde Ersetzungen erhalten.
        cache = owner[11]
        if state[5] and type(cache) is dict and len(cache) <= 256 and all(type(key) is str for key in cache):
            invocation = state[5][0]
            if cache.get("docker_sqlcmd_proxy") is invocation[3]:
                del cache["docker_sqlcmd_proxy"]
        state[2] = True
        return ("REJECTED_PROXY_SOURCE", issue, None)
    return ("EXECUTED_PROXY_SOURCE", "NONE", result)


def _proxy_source_factory(owner):
    namespace, marker, state = owner[:3]
    run, code = _proxy_source_run, _proxy_source_run.__code__
    class ProxyLoader:
        __slots__ = ()
        def exec_module(self, module):
            if not (state[0] is True and state[1] is False and state[2] is False
                    and len(state[5]) == 1 and self is state[6][0][1]
                    and state[5][0][11] is True and state[5][0][12] is False):
                state[2] = True
                raise RuntimeError()
            guard, guard_code = owner[13]
            if guard.__code__ is not guard_code or guard.__globals__ is not namespace:
                state[2] = True
                raise RuntimeError()
            guard(owner, state[4][0])
            state[5][0][11], state[5][0][12] = False, True
            _proxy_original(owner[15], namespace)(owner, state[4][0], module)
    def input_handoff(io_owner, entry):
        _inline_need(not state[3] and state[0] is False and state[2] is False
                     and type(io_owner) is tuple and len(io_owner) == 14 and io_owner[0] is namespace
                     and type(entry) is type(_proxy_source_factory) and entry.__globals__ is namespace,
                     "PROXY_SOURCE_BINDING")
        state[3].append((io_owner, entry, entry.__code__))
    def eof_handoff(io_owner, frame, result):
        _inline_need(state[0] is True and state[1] is True and state[2] is False
                     and len(state[3]) == 1 and io_owner is state[3][0][0] and not state[4]
                     and type(frame) is tuple and len(frame) == 4 and type(result) is tuple and len(result) == 3,
                     "PROXY_SOURCE_BINDING")
        state[4].append((result, frame))
    def entry():
        if state[0] is not False or state[2] is not False or len(state[3]) != 1:
            state[2] = True
            return ("REJECTED_PROXY_SOURCE", "PROXY_SOURCE_BINDING", None)
        state[0], state[1] = True, True
        try:
            io_owner, input_entry, input_code = state[3][0]
            if input_entry.__code__ is not input_code or input_entry.__globals__ is not namespace:
                raise RuntimeError()
            received = input_entry()
            state[1] = False
            _inline_need(type(received) is tuple and len(received) == 3
                         and received[:2] == ("RECEIVED_WORKER_INPUTS", "NONE")
                         and len(state[4]) == 1 and received[2] is state[4][0][0]
                         and state[2] is False, "PROXY_SOURCE_BINDING")
            if run.__code__ is not code or run.__globals__ is not namespace:
                raise RuntimeError()
            return run(owner, state[4][0])
        except BaseException:
            state[1], state[2] = False, True
            return ("REJECTED_PROXY_SOURCE", "PROXY_SOURCE_BINDING", None)
    return entry, input_handoff, eof_handoff, ProxyLoader


def _initialize_proxy_source_control():
    global _PROXY_SOURCE_INITIALIZED, _PROXY_SOURCE_MARKER, _PROXY_LOADER_CLASS
    global _proxy_source_entry, _proxy_input_handoff, _proxy_eof_handoff
    if _PROXY_SOURCE_INITIALIZED is not False:
        _PROXY_SOURCE_MARKER = None
        return ("REJECTED_PROXY_SOURCE_CONTROL", "PROXY_SOURCE_BINDING")
    _PROXY_SOURCE_INITIALIZED = True
    try:
        _worker_profile_check(_WORKER_PROFILE_BINDING)
        namespace = globals()
        builtins_namespace = namespace.get("__builtins__")
        items = _worker_profile_items(_proxy_namespace(builtins_namespace), [0])
        compiler, executor = builtins_namespace.get("compile"), builtins_namespace.get("exec")
        compiler_state = _worker_input_function(compiler, builtins_namespace)
        executor_state = _worker_input_function(executor, builtins_namespace)
        _inline_need(type(compiler.__name__) is str and compiler.__name__ == "compile"
                     and type(executor.__name__) is str and executor.__name__ == "exec", "PROXY_SOURCE_BINDING")
        module_class, spec_class = _SEMANTIC_CONTROL_ANCHOR[9], _SEMANTIC_CONTROL_ANCHOR[4]
        _inline_need(module_class is _MODULE_CLASS, "PROXY_SOURCE_BINDING")
        cache = sys.__dict__.get("modules")
        _proxy_namespace(cache)
        marker = object()
        _PROXY_SOURCE_MARKER = marker
        state = [False, False, False, [], [], [], []]
        owner = (namespace, marker, state, builtins_namespace, items, compiler, executor,
                 compiler_state, executor_state, module_class, _proxy_spec_state(spec_class), cache,
                 _worker_input_run.__code__, (_proxy_guard, _proxy_guard.__code__),
                 (_proxy_write, _proxy_write.__code__), (_proxy_execute, _proxy_execute.__code__),
                 (_proxy_binding, _proxy_binding.__code__))
        _proxy_source_entry, _proxy_input_handoff, _proxy_eof_handoff, _PROXY_LOADER_CLASS = _proxy_source_factory(owner)
        method = _PROXY_LOADER_CLASS.__dict__["exec_module"]
        state[6].append((_PROXY_LOADER_CLASS, _PROXY_LOADER_CLASS(), method, method.__code__))
        return ("BOUND_PROXY_SOURCE_CONTROL", "NONE")
    except BaseException:
        _PROXY_SOURCE_MARKER = None
        return ("REJECTED_PROXY_SOURCE_CONTROL", "PROXY_SOURCE_BINDING")


def _proxy_source_main():
    result = _proxy_source_entry()
    if result[:2] != ("EXECUTED_PROXY_SOURCE", "NONE"):
        raise SystemExit(1)
'''


def _compact_token_gaps(text):
    """Nur horizontale Tokenabstände; Lexeme und Einrückung bleiben erhalten."""
    lines = text.splitlines(keepends=True)
    tokens = tuple(tokenize.generate_tokens(iter(lines).__next__))
    ignored = (tokenize.INDENT, tokenize.DEDENT, tokenize.NEWLINE,
               tokenize.NL, tokenize.ENDMARKER, tokenize.ENCODING)
    words = (tokenize.NAME, tokenize.NUMBER, tokenize.STRING)
    edits, previous = {}, None
    for current in tokens:
        if current.type in ignored:
            continue
        if previous is not None and previous.end[0] == current.start[0]:
            row, start = current.start
            end = previous.end[1]
            gap = lines[row - 1][end:start]
            separated = ((previous.type in words and current.type in words)
                         or (previous.type == tokenize.OP and current.type == tokenize.OP)
                         or (previous.type == tokenize.NUMBER and current.string == ".")
                         or (previous.string == "." and current.type == tokenize.NUMBER))
            if gap and not gap.strip() and not separated:
                edits.setdefault(row - 1, []).append((end, start))
        previous = current
    for row, intervals in edits.items():
        for start, end in reversed(intervals):
            lines[row] = lines[row][:start] + lines[row][end:]
    result = "".join(lines)
    actual = tuple(tokenize.generate_tokens(iter(result.splitlines(keepends=True)).__next__))
    inputs.base._need(tuple((t.type, t.string) for t in actual)
                      == tuple((t.type, t.string) for t in tokens), "TEMPLATE_FORM")
    return result


def build_proxy_loader_control_bootstrap(profile_raw, *, logical_profile,
                                          expected_soabi, expected_destshared):
    selected = inputs.build_worker_input_control_bootstrap(profile_raw,
        logical_profile=logical_profile, expected_soabi=expected_soabi,
        expected_destshared=expected_destshared)
    tree = ast.parse(selected.source)
    initializer = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                       and node.name == "_initialize_worker_input_control")
    block = next(node for node in initializer.body if isinstance(node, ast.Try)).body
    bindings = [n for n, node in enumerate(block) if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Tuple) and any(isinstance(item, ast.Name)
                    and item.id == "_worker_input_entry" for item in target.elts) for target in node.targets)]
    inputs.base._need(len(bindings) == 1, "TEMPLATE_FORM")
    block.insert(bindings[0] + 1, ast.parse("_proxy_input_handoff(owner, _worker_input_entry)").body[0])
    receiver = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_worker_input_run")
    inputs.base._need(isinstance(receiver.body[-1], ast.Return)
        and ast.dump(receiver.body[-1].value) == ast.dump(ast.parse(
            '("RECEIVED_WORKER_INPUTS", "NONE", result)', mode="eval").body), "TEMPLATE_FORM")
    receiver.body.insert(len(receiver.body) - 1, ast.parse("_proxy_eof_handoff(owner, frame, result)").body[0])
    main = next(node for node in tree.body if isinstance(node, ast.If))
    inputs.base._need(ast.dump(main.body[-1]) == ast.dump(ast.parse("_worker_input_main()").body[0]), "TEMPLATE_FORM")
    main.body.insert(2, ast.parse("_initialize_proxy_source_control()").body[0])
    main.body[-1] = ast.parse("_proxy_source_main()").body[0]
    tree.body = [node for node in tree.body if node is not main] + ast.parse(_INLINE_PROXY_SOURCE).body + [main]
    formatted = inputs._compact_indentation(ast.unparse(ast.fix_missing_locations(tree)) + "\n")
    source = _compact_token_gaps(formatted).encode("utf-8", "strict")
    inputs.base._need(len(source) <= inputs.base.MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return inputs.base.BootstrapSource(source, profile_raw, logical_profile,
        hashlib.sha256(source).hexdigest(), hashlib.sha256(profile_raw).hexdigest(), len(source))
