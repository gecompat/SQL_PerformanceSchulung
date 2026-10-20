"""Additive Harness-Quellenfolge; Generierung führt keine Kandidaten aus."""
import ast
import hashlib

import dgn007_proxy_loader_source as base


_INLINE_HARNESS = r'''
_HL_INITIALIZED = False
_HL_MARKER = None
_HL_CLASS = None
_HL_NAMES = ("run_demo", "orchestrate_sessions", "sqlcmd_process")
_HL_MEMBERS = tuple("Demos/00_Framework/Tools/" + n + ".py" for n in _HL_NAMES)
_HL_ORIGINS = tuple("/dgn007/source/" + str(n) + ".py" for n in (3, 4, 5))
_HL_OWN = ("run_dgn007_automated_setup", "execution_target", "docker_sqlcmd_proxy",
    "run_demo", "orchestrate_sessions", "sqlcmd_process", "Tests.Contracts.dgn007_capture_projection",
    "Tests.Contracts.dgn007_collector_transport", "Tests.Contracts.dgn007_prospective_acceptance", "Tests", "Tests.Contracts")
_HL_EDGES = ((3, "orchestrate_sessions", ("run_manifest",)),
    (4, "sqlcmd_process", ("build_sqlcmd_command", "collect_process", "resolve_sqlcmd", "start_sqlcmd")),
    (3, "sqlcmd_process", ("build_sqlcmd_command", "extract_summary", "resolve_sqlcmd", "run_sqlcmd")))
_HL_COMMON = (("__future__", ("annotations",)), ("dataclasses", ("dataclass",)),
    ("os", None), ("pathlib", ("Path",)), ("re", None), ("sys", None), ("time", None))
_HL_STD = (_HL_COMMON + (("argparse", None), ("json", None), ("typing", ("Any",))),
    _HL_COMMON + (("argparse", None), ("json", None), ("typing", ("Any",))),
    _HL_COMMON + (("shutil", None), ("signal", None), ("subprocess", None), ("typing", ("Mapping", "Sequence"))))


def _hl_entry():
    return ("REJECTED_HARNESS_SOURCES", "HARNESS_SOURCE_BINDING", None)


def _hl_input_handoff(o, entry):
    raise RuntimeError()


def _hl_eof_handoff(o, frame, value):
    raise RuntimeError()


def _hl_binding(o, v):
    raw, d, context, m, s, origin = v[:6]
    cls, loaders, method, code = o[2][6][0]
    index = d[0] - 3
    loader = loaders[index]
    _inline_need(type(m) is o[9] and type(s) is o[10][0] and type(loader) is cls
                 and method.__code__ is code, "HARNESS_SOURCE_BINDING")
    md, sd = m.__dict__, s.__dict__
    _hl_namespace(md)
    _hl_namespace(sd)
    _inline_need(md.get("__spec__") is s and md.get("__loader__") is loader
        and sd.get("loader") is loader and sd.get("submodule_search_locations") is None
        and sd.get("loader_state") is None and sd.get("_set_fileattr") is True
        and "__path__" not in md, "HARNESS_SOURCE_BINDING")
    for value, expected in ((md.get("__name__"), _HL_NAMES[index]), (md.get("__package__"), ""),
            (md.get("__file__"), origin), (sd.get("name"), _HL_NAMES[index]), (sd.get("origin"), origin)):
        _inline_need(type(value) is str and value == expected, "HARNESS_SOURCE_BINDING")
    _inline_need(type(raw) is bytes and type(origin) is str and origin == _HL_ORIGINS[index]
                 and md.get("__builtins__") is v[10], "HARNESS_SOURCE_BINDING")
    items = _worker_profile_items(_hl_namespace(v[10]), [0])
    _inline_need(len(items) == len(o[4]) and all(a[0] == b[0]
        and a[1] is (o[2][7][0][0] if b[0] == "__import__" else b[1])
        for a, b in zip(items, o[4])), "HARNESS_SOURCE_BINDING")
    if v[8]:
        _inline_need(o[11].get(_HL_NAMES[index]) is m, "HARNESS_SOURCE_BINDING")


def _hl_run(o, p, index):
    ns, marker, st = o[:3]
    guard = o[13]
    def close():
        f, c = guard
        if f.__code__ is not c or f.__globals__ is not ns: raise RuntimeError()
        f(o, p)
    close()
    _inline_need(type(index) is int and index == len(st[5]) + 3 and index <= 5,
                 "HARNESS_SOURCE_ORDER")
    received, first, second = p[0]
    actual, bodies = received[2:]
    context, d, raw = actual[2], actual[0][5][index], bodies[index]
    _inline_need(actual[1][:3] == (3, "run_demo", "PRE_IMPORT")
        and d[:3] == (index, _HL_NAMES[index - 3], _HL_MEMBERS[index - 3]), "HARNESS_SOURCE_SELECTION")
    if index == 3:
        _inline_need(not st[8] and all(n not in o[11] for n in _HL_OWN), "HARNESS_SOURCE_BINDING")
        digest = _inline_context_digest(context, expected_format=_COMMAND_FORMAT)
        close()
        _inline_need(type(digest) is tuple and digest[:2] == ("FORMATTED_CONTEXT_DIGEST", "NONE"), "HARNESS_SOURCE_BINDING")
        st[12].append(digest[2])
    else:
        _inline_need(st[8] and st[8][-1][1][0] == index - 1 and st[8][-1][13] is True
            and st[8][-1][7] is None, "HARNESS_SOURCE_ORDER")
    cls, loaders, method, code = st[6][0]
    loader = loaders[index - 3]
    m = o[9](_HL_NAMES[index - 3])
    close()
    s = o[10][0](_HL_NAMES[index - 3], loader, origin=_HL_ORIGINS[index - 3], is_package=False)
    close()
    _inline_need(type(m) is o[9] and type(s) is o[10][0], "HARNESS_SOURCE_BINDING")
    _hl_namespace(m.__dict__)
    _hl_namespace(s.__dict__)
    s.__dict__["_set_fileattr"] = True
    bi = dict(o[4])
    bi["__import__"] = st[7][0][0]
    m.__dict__.update(__name__=_HL_NAMES[index - 3], __package__="", __spec__=s,
        __loader__=loader, __file__=_HL_ORIGINS[index - 3], __builtins__=bi)
    v = [raw, d, context, m, s, _HL_ORIGINS[index - 3], None, None, False, False, bi, False, False, False]
    st[5].append(v)
    st[8].append(v)
    try:
        close()
        o[11][_HL_NAMES[index - 3]] = m
        v[8] = True
        close()
        fields = (3, index - 2, "SOURCE", index, st[12][0], d[4], index, index - 2)
        begin = _report_json(("BEGIN",) + fields, p[1][0][3]) + b"\n"
        close()
        _hl_original(o[14], ns)(o, p, begin)
        close()
        v[11] = True
        _inline_need(method.__code__ is code and method.__globals__ is ns, "HARNESS_SOURCE_BINDING")
        method(loader, m)
        close()
        _inline_need(v[6] is not None and v[7] is v[6], "HARNESS_SOURCE_BINDING")
        complete = _report_json(("COMPLETE",) + fields, p[1][0][3]) + b"\n"
        close()
        _hl_original(o[14], ns)(o, p, complete)
        close()
        v[9] = True
        return m
    finally:
        if st[8] and st[8][-1] is v: st[8].pop()
        else: st[2] = True


def _hl_factory(o):
    ns, marker, st = o[:3]
    run, rc = _hl_run, _hl_run.__code__
    guard, gc = o[13]
    def close():
        if guard.__code__ is not gc or guard.__globals__ is not ns: raise RuntimeError()
        guard(o, st[4][0])
    def invoke(index):
        if run.__code__ is not rc or run.__globals__ is not ns: raise RuntimeError()
        return run(o, st[4][0], index)
    class Loader:
        __slots__ = ()
        def exec_module(self, m):
            if not (st[0] is True and st[1] is False and st[2] is False and st[8]):
                st[2] = True
                raise RuntimeError()
            close()
            v = st[8][-1]
            if not (m is v[3] and self is st[6][0][1][v[1][0] - 3]
                    and v[11] is True and v[12] is False):
                st[2] = True
                raise RuntimeError()
            v[11], v[12] = False, True
            _hl_original(o[15], ns)(o, st[4][0], m)
    def gateway(name, globals=None, locals=None, fromlist=(), level=0):
        reserved = False
        try:
            close()
            _inline_need(st[8], "HARNESS_SOURCE_IMPORT")
            v = st[8][-1]
            index = v[1][0]
            _inline_need(v[13] is True and v[6] is not None and v[7] is None and globals is v[3].__dict__
                and (locals is None or locals is globals) and index not in st[11], "HARNESS_SOURCE_IMPORT")
            _hl_namespace(globals)
            _inline_need(type(name) is str and 0 < len(name) <= 256 and "\0" not in name
                and type(level) is int and level == 0, "HARNESS_SOURCE_IMPORT")
            _inline_need(fromlist is None or (type(fromlist) is tuple and len(fromlist) <= 16
                and all(type(n) is str and 0 < len(n) <= 256 and "\0" not in n and n != "*"
                    for n in fromlist)), "HARNESS_SOURCE_IMPORT")
            st[11].append(index)
            reserved = True
            key = (index, name, fromlist)
            if key in _HL_EDGES:
                edge = _HL_EDGES.index(key)
                _inline_need(st[9][edge] is False, "HARNESS_SOURCE_ORDER")
                st[9][edge] = True
                if edge == 2:
                    _inline_need(len(st[5]) == 3 and st[5][2][9] is True, "HARNESS_SOURCE_ORDER")
                    close()
                    m = st[5][2][3]
                else:
                    m = invoke(4 if edge == 0 else 5)
            else:
                _inline_need((name, fromlist) in _HL_STD[index - 3] and key not in st[10], "HARNESS_SOURCE_IMPORT")
                st[10].append(key)
                try: m = o[17](name, globals, locals, fromlist, level)
                finally: close()
            close()
            _inline_need(type(m) is o[9], "HARNESS_SOURCE_IMPORT")
            md = _hl_namespace(m.__dict__)
            _inline_need(type(md.get("__name__")) is str and md["__name__"] == name,
                         "HARNESS_SOURCE_IMPORT")
            _inline_need(fromlist is None or all(n in md for n in fromlist), "HARNESS_SOURCE_IMPORT")
            return m
        except BaseException:
            st[2] = True
            raise RuntimeError() from None
        finally:
            if reserved:
                if st[11] and st[11][-1] == index: st[11].pop()
                else: st[2] = True
    def input_handoff(io, entry):
        _inline_need(not st[3] and st[0] is False and st[2] is False and type(io) is tuple
            and len(io) == 14 and io[0] is ns and type(entry) is type(_hl_factory)
            and entry.__globals__ is ns, "HARNESS_SOURCE_BINDING")
        st[3].append((io, entry, entry.__code__))
    def eof_handoff(io, frame, value):
        _inline_need(st[0] is True and st[1] is True and st[2] is False and len(st[3]) == 1
            and io is st[3][0][0] and not st[4] and type(frame) is tuple and len(frame) == 4
            and type(value) is tuple and len(value) == 3, "HARNESS_SOURCE_BINDING")
        st[4].append((value, frame))
    def entry():
        if st[0] is not False or st[2] is not False or len(st[3]) != 1:
            st[2] = True
            return ("REJECTED_HARNESS_SOURCES", "HARNESS_SOURCE_BINDING", None)
        st[0], st[1] = True, True
        result, issue = None, "HARNESS_SOURCE_REJECTED"
        try:
            io, f, c = st[3][0]
            if f.__code__ is not c or f.__globals__ is not ns: raise RuntimeError()
            received = f()
            st[1] = False
            _inline_need(type(received) is tuple and len(received) == 3
                and received[:2] == ("RECEIVED_WORKER_INPUTS", "NONE") and len(st[4]) == 1
                and received[2] is st[4][0][0] and st[2] is False, "HARNESS_SOURCE_BINDING")
            invoke(3)
            close()
            _inline_need(len(st[5]) == 3 and not st[8] and not st[11]
                and all(v[9] is True for v in st[5]) and all(flag is True for flag in st[9]), "HARNESS_SOURCE_ORDER")
            result = tuple((v[3], v[4], st[6][0][1][n], v[6], v[0]) for n, v in enumerate(st[5]))
        except BaseException: pass
        try: close()
        except BaseException: result, issue = None, "HARNESS_SOURCE_BINDING"
        if result is None:
            cache = o[11]
            if type(cache) is dict and len(cache) <= 256 and all(type(k) is str for k in cache):
                for v in reversed(st[5]):
                    name = v[1][1]
                    if cache.get(name) is v[3]: del cache[name]
            st[2] = True
            return ("REJECTED_HARNESS_SOURCES", issue, None)
        return ("EXECUTED_HARNESS_SOURCES", "NONE", result)
    return entry, input_handoff, eof_handoff, Loader, gateway


def _initialize_hl_control():
    global _HL_INITIALIZED, _HL_MARKER, _HL_CLASS, _hl_entry, _hl_input_handoff, _hl_eof_handoff
    if _HL_INITIALIZED is not False:
        _HL_MARKER = None
        return ("REJECTED_HARNESS_CONTROL", "HARNESS_SOURCE_BINDING")
    _HL_INITIALIZED = True
    try:
        _worker_profile_check(_WORKER_PROFILE_BINDING)
        ns = globals()
        bi = ns.get("__builtins__")
        items = _worker_profile_items(_hl_namespace(bi), [0])
        compile_fn, exec_fn, import_fn = bi.get("compile"), bi.get("exec"), bi.get("__import__")
        fs = tuple(_worker_input_function(f, bi) for f in (compile_fn, exec_fn, import_fn))
        _inline_need(all(type(f.__name__) is str and f.__name__ == n for f, n in
            zip((compile_fn, exec_fn, import_fn), ("compile", "exec", "__import__"))), "HARNESS_SOURCE_BINDING")
        cache = _hl_namespace(sys.__dict__.get("modules"))
        _HL_MARKER = object()
        st = [False, False, False, [], [], [], [], [], [], [False, False, False], [], [], []]
        o = (ns, _HL_MARKER, st, bi, items, compile_fn, exec_fn, fs[0], fs[1],
            _SEMANTIC_CONTROL_ANCHOR[9], _hl_spec_state(_SEMANTIC_CONTROL_ANCHOR[4]), cache,
            _worker_input_run.__code__, (_hl_guard, _hl_guard.__code__), (_hl_write, _hl_write.__code__),
            (_hl_execute, _hl_execute.__code__), (_hl_binding, _hl_binding.__code__), import_fn, fs[2])
        _hl_entry, _hl_input_handoff, _hl_eof_handoff, _HL_CLASS, gateway = _hl_factory(o)
        method = _HL_CLASS.__dict__["exec_module"]
        st[6].append((_HL_CLASS, tuple(_HL_CLASS() for _ in range(3)), method, method.__code__))
        st[7].append((gateway, gateway.__code__, _worker_profile_function(gateway, [0])))
        return ("BOUND_HARNESS_CONTROL", "NONE")
    except BaseException:
        _HL_MARKER = None
        return ("REJECTED_HARNESS_CONTROL", "HARNESS_SOURCE_BINDING")


def _hl_main():
    if _hl_entry()[:2] != ("EXECUTED_HARNESS_SOURCES", "NONE"): raise SystemExit(1)
'''


def _helpers():
    chosen = {"_proxy_namespace", "_proxy_spec_state", "_proxy_original",
              "_proxy_guard", "_proxy_write", "_proxy_execute"}
    nodes = [node for node in ast.parse(base._INLINE_PROXY_SOURCE).body
             if isinstance(node, ast.FunctionDef) and node.name in chosen]
    base.inputs.base._need(len(nodes) == len(chosen), "TEMPLATE_FORM")
    class Names(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            node.name = node.name.replace("_proxy_", "_hl_")
            return self.generic_visit(node)
        def visit_Name(self, node):
            if node.id == "_PROXY_SOURCE_MARKER": node.id = "_HL_MARKER"
            else: node.id = node.id.replace("_proxy_", "_hl_")
            return node
        def visit_Constant(self, node):
            if node.value == "_PROXY_SOURCE_MARKER":
                node.value = "_HL_MARKER"
            elif isinstance(node.value, str) and node.value.startswith("PROXY_SOURCE_"):
                node.value = node.value.replace("PROXY_SOURCE_", "HARNESS_SOURCE_", 1)
            return node
    nodes = [Names().visit(node) for node in nodes]
    guard = next(node for node in nodes if node.name == "_hl_guard")
    guard.body[-1:] = ast.parse('''
_worker_input_function_check(owner[18], owner[3].get("__import__"), owner[3])
f, c, held = state[7][0]
_inline_need(f.__code__ is c and f.__globals__ is namespace
    and _worker_profile_function_equal(held, _worker_profile_function(f, [0])), "HARNESS_SOURCE_BINDING")
for invocation in state[5]:
    _hl_original(owner[16], namespace)(owner, invocation)
published = tuple(v[1][1] for v in state[5] if v[8] is True)
_inline_need(all(name not in owner[11] for name in _HL_OWN if name not in published), "HARNESS_SOURCE_BINDING")
''').body
    execute = next(node for node in nodes if node.name == "_hl_execute")
    bindings = [node for node in execute.body if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "invocation" for t in node.targets)]
    base.inputs.base._need(len(bindings) == 1, "TEMPLATE_FORM")
    bindings[0].value = ast.parse("owner[2][8][-1]", mode="eval").body
    return nodes


def build_harness_loader_control_bootstrap(profile_raw, *, logical_profile,
                                           expected_soabi, expected_destshared):
    options = dict(logical_profile=logical_profile, expected_soabi=expected_soabi,
                   expected_destshared=expected_destshared)
    selected = base.inputs.build_worker_input_control_bootstrap(profile_raw, **options)
    tree = ast.parse(selected.source)
    init = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_initialize_worker_input_control")
    block = next(n for n in init.body if isinstance(n, ast.Try)).body
    assignments = [i for i, n in enumerate(block) if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Tuple) and any(isinstance(v, ast.Name) and v.id == "_worker_input_entry" for v in t.elts) for t in n.targets)]
    base.inputs.base._need(len(assignments) == 1, "TEMPLATE_FORM")
    block.insert(assignments[0] + 1, ast.parse("_hl_input_handoff(owner, _worker_input_entry)").body[0])
    receiver = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_worker_input_run")
    base.inputs.base._need(isinstance(receiver.body[-1], ast.Return)
        and ast.dump(receiver.body[-1].value) == ast.dump(ast.parse(
            '("RECEIVED_WORKER_INPUTS", "NONE", result)', mode="eval").body), "TEMPLATE_FORM")
    receiver.body.insert(len(receiver.body) - 1, ast.parse("_hl_eof_handoff(owner, frame, result)").body[0])
    main = next(n for n in tree.body if isinstance(n, ast.If))
    base.inputs.base._need(ast.dump(main.body[-1]) == ast.dump(ast.parse("_worker_input_main()").body[0]), "TEMPLATE_FORM")
    main.body.insert(2, ast.parse("_initialize_hl_control()").body[0])
    main.body[-1] = ast.parse("_hl_main()").body[0]
    tree.body = [n for n in tree.body if n is not main] + _helpers() + ast.parse(_INLINE_HARNESS).body + [main]
    tree = base._compact_locals(tree)
    text = base.inputs._compact_indentation(ast.unparse(ast.fix_missing_locations(tree)) + "\n")
    source = base._compact_token_gaps(text).encode("utf-8", "strict")
    base.inputs.base._need(len(source) <= base.inputs.base.MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return base.inputs.base.BootstrapSource(source, profile_raw, logical_profile,
        hashlib.sha256(source).hexdigest(), hashlib.sha256(profile_raw).hexdigest(), len(source))
