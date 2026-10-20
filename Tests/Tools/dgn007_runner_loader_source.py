"""Additive vollständige Runnerroute; Generierung startet keine Kandidaten."""
import ast
import hashlib
from pathlib import Path
import symtable

import dgn007_harness_loader_source as base
import dgn007_codefree_parents as parents


_INLINE_RUNNER = r'''
_RL_ORDER = (0, 1, 5, 3, 4, 6, 7, 8)
_RL_SEQUENCES = (1, 2, None, 4, 5, 3, 8, 9, 10)
_RL_NAMES = ("run_dgn007_automated_setup", "execution_target", "docker_sqlcmd_proxy",
    "run_demo", "orchestrate_sessions", "sqlcmd_process", "Tests.Contracts.dgn007_capture_projection",
    "Tests.Contracts.dgn007_collector_transport", "Tests.Contracts.dgn007_prospective_acceptance")
_RL_MEMBERS = ("Tests/Runtime/run_dgn007_automated_setup.py", "Tests/Runtime/execution_target.py",
    "Tests/Runtime/docker_sqlcmd_proxy.py", "Demos/00_Framework/Tools/run_demo.py",
    "Demos/00_Framework/Tools/orchestrate_sessions.py", "Demos/00_Framework/Tools/sqlcmd_process.py",
    "Tests/Contracts/dgn007_capture_projection.py", "Tests/Contracts/dgn007_collector_transport.py",
    "Tests/Contracts/dgn007_prospective_acceptance.py")
_RL_OWN = _RL_NAMES + ("Tests", "Tests.Contracts")
_RL_ORIGINS = tuple("/dgn007/source/" + str(n) + ".py" for n in range(9))
_RL_EDGES = ((0, "execution_target", None, 1),
    (0, "execution_target", ("ExecutionTarget", "ExecutionTargetError"), 1),
    (1, "sqlcmd_process", ("resolve_sqlcmd",), 5),
    (0, "run_demo", ("load_manifest",), 3),
    (3, "orchestrate_sessions", ("run_manifest",), 4),
    (4, "sqlcmd_process", ("build_sqlcmd_command", "collect_process", "resolve_sqlcmd", "start_sqlcmd"), 5),
    (3, "sqlcmd_process", ("build_sqlcmd_command", "extract_summary", "resolve_sqlcmd", "run_sqlcmd"), 5),
    (0, "sqlcmd_process", ("SqlcmdResult", "build_sqlcmd_command", "run_sqlcmd"), 5),
    (0, "sqlcmd_process", ("start_sqlcmd", "_terminate_process_tree"), 5),
    (0, "sqlcmd_process", ("_linux_descendants", "_linux_process_identity"), 5),
    (0, "Tests.Contracts.dgn007_capture_projection", ("decode_projection", "ProjectionError"), 6),
    (6, "Tests.Contracts.dgn007_collector_transport", ("CaptureBody", "SCHEMA", "TransportError", "decode_capture"), 7),
    (7, "Tests.Contracts.dgn007_prospective_acceptance", ("AcceptanceContract", "ActivePlanRecord", "MAX_SQL_TICKS",
        "PlanUnionRecord", "QueryFamilyRecord", "REQUEST_MAPPING", "WindowRecord", "_contract_valid"), 8),
    (6, "Tests.Contracts.dgn007_prospective_acceptance", ("AcceptanceContract", "_contract_valid"), 8),
    (0, "Tests.Contracts.dgn007_collector_transport", ("CaptureBody",), 7),
    (0, "Tests.Contracts.dgn007_prospective_acceptance", ("contract_from_mapping",), 8))
_RL_STD = (
    (("__future__", ("annotations",)), ("argparse", None), ("dataclasses", ("dataclass", "field")),
     ("json", None), ("os", None), ("pathlib", ("Path",)), ("re", None), ("signal", None),
     ("subprocess", None), ("sys", None), ("threading", None), ("time", None), ("typing", ("Sequence",))),
    (("__future__", ("annotations",)), ("dataclasses", ("dataclass",)), ("os", None),
     ("pathlib", ("Path",)), ("re", None), ("subprocess", None), ("sys", None)), (),
    (("__future__", ("annotations",)), ("argparse", None), ("dataclasses", ("dataclass",)),
     ("json", None), ("os", None), ("pathlib", ("Path",)), ("re", None), ("sys", None), ("time", None), ("typing", ("Any",))),
    (("__future__", ("annotations",)), ("argparse", None), ("dataclasses", ("dataclass",)),
     ("json", None), ("os", None), ("pathlib", ("Path",)), ("re", None), ("sys", None), ("time", None), ("typing", ("Any",))),
    (("__future__", ("annotations",)), ("dataclasses", ("dataclass",)), ("os", None),
     ("pathlib", ("Path",)), ("re", None), ("shutil", None), ("signal", None), ("subprocess", None),
     ("sys", None), ("time", None), ("typing", ("Mapping", "Sequence"))),
    (("__future__", ("annotations",)), ("re", None)),
    (("__future__", ("annotations",)), ("dataclasses", ("dataclass", "fields")), ("decimal", ("Decimal",)),
     ("fractions", ("Fraction",)), ("json", None), ("re", None)),
    (("__future__", ("annotations",)), ("dataclasses", ("dataclass",)), ("decimal", ("Decimal",)),
     ("fractions", ("Fraction",)), ("hashlib", None), ("json", None)))


def _rl_parent_graph(entry, factory, namespace, codes, callbacks):
    pending, saved = [entry], []
    budget = [0]
    while pending:
        _inline_need(len(pending) <= 64, "RUNNER_SOURCE_BINDING")
        fn = pending.pop()
        if any(fn is pair[0] for pair in saved): continue
        _inline_need(len(saved) < 16 and type(fn) is type(factory) and fn.__globals__ is namespace
            and any(fn.__code__ is code for code in codes), "RUNNER_SOURCE_BINDING")
        state = _worker_profile_function(fn, budget)
        _inline_need((state[3] is None or len(state[3]) <= 32)
            and len(state[5]) <= 32 and len(state[7]) <= 32, "RUNNER_SOURCE_BINDING")
        saved.append((fn, state))
        values = (() if state[3] is None else state[3]) + tuple(v for k, v in state[5]) + state[7]
        for value in values:
            if type(value) is not type(factory): continue
            if value is factory or any(value is pair[0] for pair in callbacks): continue
            _inline_need(value.__globals__ is namespace and any(value.__code__ is code for code in codes),
                         "RUNNER_SOURCE_BINDING")
            if any(value is pair[0] for pair in saved) or any(value is item for item in pending): continue
            _inline_need(len(saved) + len(pending) < 16, "RUNNER_SOURCE_BINDING")
            pending.append(value)
    return tuple(saved)


def _rl_parent_binding(o, p):
    st = o[2]
    factory, code, namespace, items, held, run_code, callbacks, codes = st[13][0]
    _inline_need(factory.__code__ is code and factory.__globals__ is namespace,
                 "RUNNER_SOURCE_BINDING")
    current = _worker_profile_items(_rl_namespace(namespace), [0])
    _inline_need(len(current) == len(items) and all(a[0] == b[0] and a[1] is b[1]
        for a, b in zip(current, items)), "RUNNER_SOURCE_BINDING")
    _inline_need(_worker_profile_function_equal(held, _worker_profile_function(factory, [0])), "RUNNER_SOURCE_BINDING")
    for fn, saved in callbacks:
        _inline_need(_worker_profile_function_equal(saved, _worker_profile_function(fn, [0])), "RUNNER_SOURCE_BINDING")
    if st[14][2]:
        entry = st[14][2][0]
        _inline_need(type(entry) is type(factory) and entry.__code__ is run_code
            and entry.__globals__ is namespace, "RUNNER_SOURCE_BINDING")
        _inline_need(len(st[14][4]) == 1 and type(st[14][4][0]) is tuple
            and 0 < len(st[14][4][0]) <= 16, "RUNNER_SOURCE_BINDING")
        budget = [0]
        for fn, saved in st[14][4][0]:
            _inline_need(_worker_profile_function_equal(saved, _worker_profile_function(fn, budget)),
                         "RUNNER_SOURCE_BINDING")
    values = st[14][3]
    _inline_need(type(values) is list and len(values) <= 2
        and all(type(v) is tuple and len(v) == 3 for v in values), "RUNNER_SOURCE_BINDING")
    if not values:
        if st[14][1] is False:
            _inline_need(all(n not in o[11] for n in ("Tests", "Tests.Contracts")), "RUNNER_SOURCE_BINDING")
        return
    _inline_need(st[14][1] is False and len(values) == 2, "RUNNER_SOURCE_BINDING")
    for index, (m, spec, locations) in enumerate(values):
        _inline_need(type(m) is o[9] and type(spec) is o[10][0], "RUNNER_SOURCE_BINDING")
        md, sd = _rl_namespace(m.__dict__), _rl_namespace(spec.__dict__)
        name = ("Tests", "Tests.Contracts")[index]
        _inline_need(type(locations) is list and len(locations) == 0
            and md.get("__path__") is locations and sd.get("submodule_search_locations") is locations
            and md.get("__spec__") is spec and md.get("__loader__") is None
            and sd.get("origin") is None and sd.get("loader") is None
            and sd.get("loader_state") is None and sd.get("_set_fileattr") is False
            and "__file__" not in md and "__cached__" not in md
            and o[11].get(name) is m, "RUNNER_SOURCE_BINDING")
        for actual in (md.get("__name__"), md.get("__package__"), sd.get("name")):
            _inline_need(type(actual) is str and actual == name, "RUNNER_SOURCE_BINDING")
    _inline_need(values[0][0].__dict__.get("Contracts") is values[1][0], "RUNNER_SOURCE_BINDING")
    namespace = _rl_namespace(values[1][0].__dict__)
    for index in (6, 7, 8):
        found = [v for v in st[5] if v[1][0] == index and v[8] is True]
        key = _RL_NAMES[index].rsplit(".", 1)[1]
        _inline_need((len(found) == 1 and namespace.get(key) is found[0][3])
            if found else key not in namespace, "RUNNER_SOURCE_BINDING")


def _rl_parents(o, p):
    st, ns = o[2], o[0]
    _inline_need(st[14][0] is False and not st[14][3], "RUNNER_SOURCE_ORDER")
    _inline_need(len(st[5]) == 5 and tuple(v[1][0] for v in st[5]) == (0, 1, 5, 3, 4)
        and len(st[8]) == 1 and st[8][0] is st[5][0] and st[8][0][13] is True
        and st[8][0][6] is not None and st[8][0][7] is None
        and all(v[9] is True for v in st[5][1:]), "RUNNER_SOURCE_ORDER")
    st[14][0], st[14][1] = True, True
    try:
        _rl_original(o[13], ns)(o, p)
        factory, code, namespace, items, held, run_code, callbacks, codes = st[13][0]
        value = factory(module_type=o[9], spec_type=o[10][0], cache=o[11],
            context_digest=st[12][0], guard=callbacks[0][0], write=callbacks[1][0])
        _rl_original(o[13], ns)(o, p)
        _inline_need(type(value) is type(factory) and value.__code__ is run_code
            and value.__globals__ is namespace and not st[14][2], "RUNNER_SOURCE_BINDING")
        graph = _rl_original(o[21], ns)(value, factory, namespace, codes, callbacks)
        st[14][4].append(graph)
        st[14][2].append(value)
        _rl_original(o[13], ns)(o, p)
        _inline_need(len(st[5]) == 5 and len(st[8]) == 1 and st[8][0] is st[5][0]
            and st[8][0][13] is True and st[8][0][7] is None
            and all(v[9] is True for v in st[5][1:]), "RUNNER_SOURCE_ORDER")
        result = value()
        _rl_original(o[13], ns)(o, p)
        _inline_need(type(result) is tuple and len(result) == 3
            and type(result[0]) is str and type(result[1]) is str
            and result[:2] == ("REGISTERED_CODEFREE_PARENTS", "NONE")
            and type(result[2]) is tuple and len(result[2]) == 2
            and all(type(v) is tuple and len(v) == 3 for v in result[2]), "RUNNER_SOURCE_BINDING")
        st[14][3].extend(result[2])
    finally:
        st[14][1] = False
    _rl_original(o[13], ns)(o, p)


def _rl_binding(o, v):
    raw, d, context, m, spec, origin = v[:6]
    index = d[0]
    cls, loaders, method, code = o[2][6][0]
    _inline_need(type(m) is o[9] and type(spec) is o[10][0]
        and type(loaders[index]) is cls and method.__code__ is code, "RUNNER_SOURCE_BINDING")
    md, sd = _rl_namespace(m.__dict__), _rl_namespace(spec.__dict__)
    _inline_need(md.get("__spec__") is spec and md.get("__loader__") is loaders[index]
        and sd.get("loader") is loaders[index] and sd.get("submodule_search_locations") is None
        and sd.get("loader_state") is None and sd.get("_set_fileattr") is True
        and "__path__" not in md, "RUNNER_SOURCE_BINDING")
    for actual, expected in ((md.get("__name__"), _RL_NAMES[index]),
        (md.get("__package__"), "Tests.Contracts" if index >= 6 else ""),
        (md.get("__file__"), origin), (sd.get("name"), _RL_NAMES[index]), (sd.get("origin"), origin)):
        _inline_need(type(actual) is str and actual == expected, "RUNNER_SOURCE_BINDING")
    _inline_need(type(raw) is bytes and type(origin) is str and origin == _RL_ORIGINS[index]
        and md.get("__builtins__") is v[10], "RUNNER_SOURCE_BINDING")
    items = _worker_profile_items(_rl_namespace(v[10]), [0])
    _inline_need(len(items) == len(o[4]) and all(a[0] == b[0]
        and a[1] is (o[2][7][0][0] if b[0] == "__import__" else b[1])
        for a, b in zip(items, o[4])), "RUNNER_SOURCE_BINDING")
    if v[8]:
        _inline_need(o[11].get(_RL_NAMES[index]) is m, "RUNNER_SOURCE_BINDING")


def _rl_run(o, p, index):
    ns, marker, st = o[:3]
    guard = o[13]
    def close():
        f, c = guard
        if f.__code__ is not c or f.__globals__ is not ns: raise RuntimeError()
        f(o, p)
    close()
    _inline_need(type(index) is int and len(st[5]) < 8
        and index == _RL_ORDER[len(st[5])], "RUNNER_SOURCE_ORDER")
    received, first, second = p[0]
    actual, bodies = received[2:]
    context, d, raw = actual[2], actual[0][5][index], bodies[index]
    _inline_need(actual[1][:3] == (1, "run_dgn007_automated_setup", "PRE_IMPORT")
        and d[:3] == (index, _RL_NAMES[index], _RL_MEMBERS[index]), "RUNNER_SOURCE_SELECTION")
    if index == 0:
        _inline_need(not st[8] and all(n not in o[11] for n in _RL_OWN), "RUNNER_SOURCE_BINDING")
        digest = _inline_context_digest(context, expected_format=_COMMAND_FORMAT)
        close()
        _inline_need(type(digest) is tuple and digest[:2] == ("FORMATTED_CONTEXT_DIGEST", "NONE"), "RUNNER_SOURCE_BINDING")
        st[12].append(digest[2])
    else:
        _inline_need(st[8] and st[8][-1][13] is True and st[8][-1][7] is None, "RUNNER_SOURCE_ORDER")
    if index >= 6:
        _inline_need(len(st[14][3]) == 2, "RUNNER_SOURCE_BINDING")
    cls, loaders, method, code = st[6][0]
    m = o[9](_RL_NAMES[index])
    close()
    spec = o[10][0](_RL_NAMES[index], loaders[index], origin=_RL_ORIGINS[index], is_package=False)
    close()
    _inline_need(type(m) is o[9] and type(spec) is o[10][0], "RUNNER_SOURCE_BINDING")
    _rl_namespace(m.__dict__)
    _rl_namespace(spec.__dict__)
    spec.__dict__["_set_fileattr"] = True
    bi = dict(o[4])
    bi["__import__"] = st[7][0][0]
    m.__dict__.update(__name__=_RL_NAMES[index], __package__="Tests.Contracts" if index >= 6 else "",
        __spec__=spec, __loader__=loaders[index], __file__=_RL_ORIGINS[index], __builtins__=bi)
    v = [raw, d, context, m, spec, _RL_ORIGINS[index], None, None, False, False, bi, False, False, False]
    st[5].append(v)
    st[8].append(v)
    try:
        close()
        o[11][_RL_NAMES[index]] = m
        if index >= 6:
            st[14][3][1][0].__dict__[_RL_NAMES[index].rsplit(".", 1)[1]] = m
        v[8] = True
        close()
        sequence = _RL_SEQUENCES[index]
        fields = (1, sequence, "SOURCE", index, st[12][0], d[4], index, sequence)
        begin = _report_json(("BEGIN",) + fields, p[1][0][3]) + b"\n"
        close()
        _rl_original(o[14], ns)(o, p, begin)
        close()
        v[11] = True
        _inline_need(method.__code__ is code and method.__globals__ is ns, "RUNNER_SOURCE_BINDING")
        method(loaders[index], m)
        close()
        _inline_need(v[6] is not None and v[7] is v[6], "RUNNER_SOURCE_BINDING")
        complete = _report_json(("COMPLETE",) + fields, p[1][0][3]) + b"\n"
        close()
        _rl_original(o[14], ns)(o, p, complete)
        close()
        v[9] = True
        return m
    finally:
        if st[8] and st[8][-1] is v: st[8].pop()
        else: st[2] = True


def _rl_factory(o):
    ns, marker, st = o[:3]
    run, rc = _rl_run, _rl_run.__code__
    action, ac = o[20]
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
            if not (m is v[3] and self is st[6][0][1][v[1][0]] and v[11] is True and v[12] is False):
                st[2] = True
                raise RuntimeError()
            v[11], v[12] = False, True
            _rl_original(o[15], ns)(o, st[4][0], m)
    def gateway(name, globals=None, locals=None, fromlist=(), level=0):
        reserved = False
        try:
            close()
            _inline_need(st[8], "RUNNER_SOURCE_IMPORT")
            v = st[8][-1]
            index = v[1][0]
            _inline_need(v[13] is True and v[6] is not None and v[7] is None
                and globals is v[3].__dict__ and (locals is None or locals is globals)
                and index not in st[11], "RUNNER_SOURCE_IMPORT")
            _rl_namespace(globals)
            _inline_need(type(name) is str and 0 < len(name) <= 256 and "\0" not in name
                and type(level) is int and level == 0, "RUNNER_SOURCE_IMPORT")
            _inline_need(fromlist is None or (type(fromlist) is tuple and len(fromlist) <= 16
                and all(type(n) is str and 0 < len(n) <= 256 and "\0" not in n and n != "*"
                    for n in fromlist)), "RUNNER_SOURCE_IMPORT")
            st[11].append(index)
            reserved = True
            matches = [n for n, edge in enumerate(_RL_EDGES) if edge[:3] == (index, name, fromlist)]
            if matches:
                _inline_need(len(matches) == 1, "RUNNER_SOURCE_ORDER")
                edge = matches[0]
                _inline_need(st[9][edge] is False, "RUNNER_SOURCE_ORDER")
                st[9][edge] = True
                target = _RL_EDGES[edge][3]
                existing = [w for w in st[5] if w[1][0] == target]
                if existing:
                    _inline_need(len(existing) == 1 and existing[0][9] is True, "RUNNER_SOURCE_ORDER")
                    close()
                    m = existing[0][3]
                else:
                    if target == 6:
                        _inline_need(action.__code__ is ac and action.__globals__ is ns, "RUNNER_SOURCE_BINDING")
                        action(o, st[4][0])
                        close()
                    m = invoke(target)
            else:
                key = (index, name, fromlist)
                _inline_need((name, fromlist) in _RL_STD[index] and key not in st[10], "RUNNER_SOURCE_IMPORT")
                st[10].append(key)
                try: m = o[17](name, globals, locals, fromlist, level)
                finally: close()
            close()
            _inline_need(type(m) is o[9], "RUNNER_SOURCE_IMPORT")
            md = _rl_namespace(m.__dict__)
            _inline_need(type(md.get("__name__")) is str and md["__name__"] == name
                and (fromlist is None or all(n in md for n in fromlist)), "RUNNER_SOURCE_IMPORT")
            return m
        except BaseException:
            st[2] = True
            raise RuntimeError() from None
        finally:
            if reserved:
                if st[11] and st[11][-1] == index: st[11].pop()
                else: st[2] = True
    def parent_guard():
        close()
        _inline_need(st[14][1] is True and len(st[5]) == 5 and len(st[8]) == 1
            and st[8][0][1][0] == 0 and st[8][0][13] is True and st[8][0][7] is None
            and all(v[9] is True for v in st[5][1:]), "RUNNER_SOURCE_BINDING")
    def parent_write(row):
        parent_guard()
        _rl_original(o[14], ns)(o, st[4][0], row)
        parent_guard()
    def input_handoff(io, entry):
        _inline_need(not st[3] and st[0] is False and st[2] is False and type(io) is tuple
            and len(io) == 14 and io[0] is ns and type(entry) is type(_rl_factory)
            and entry.__globals__ is ns, "RUNNER_SOURCE_BINDING")
        st[3].append((io, entry, entry.__code__))
    def eof_handoff(io, frame, value):
        _inline_need(st[0] is True and st[1] is True and st[2] is False and len(st[3]) == 1
            and io is st[3][0][0] and not st[4] and type(frame) is tuple and len(frame) == 4
            and type(value) is tuple and len(value) == 3, "RUNNER_SOURCE_BINDING")
        st[4].append((value, frame))
    def entry():
        if st[0] is not False or st[2] is not False or len(st[3]) != 1:
            st[2] = True
            return ("REJECTED_RUNNER_SOURCES", "RUNNER_SOURCE_BINDING", None)
        st[0], st[1] = True, True
        result, issue = None, "RUNNER_SOURCE_REJECTED"
        try:
            io, f, c = st[3][0]
            if f.__code__ is not c or f.__globals__ is not ns: raise RuntimeError()
            received = f()
            st[1] = False
            _inline_need(type(received) is tuple and len(received) == 3
                and received[:2] == ("RECEIVED_WORKER_INPUTS", "NONE") and len(st[4]) == 1
                and received[2] is st[4][0][0] and st[2] is False, "RUNNER_SOURCE_BINDING")
            invoke(0)
            close()
            _inline_need(len(st[5]) == 8 and len(st[14][3]) == 2 and not st[8] and not st[11]
                and all(v[9] is True for v in st[5]) and all(v is True for v in st[9]), "RUNNER_SOURCE_ORDER")
            result = (tuple((v[3], v[4], st[6][0][1][v[1][0]], v[6], v[0]) for v in st[5]), tuple(st[14][3]))
        except BaseException: pass
        try: close()
        except BaseException: result, issue = None, "RUNNER_SOURCE_BINDING"
        if result is None:
            cache = o[11]
            if type(cache) is dict and len(cache) <= 256 and all(type(k) is str for k in cache):
                for v in reversed(st[5]):
                    index = v[1][0]
                    if index >= 6 and len(st[14][3]) == 2:
                        parent = st[14][3][1][0]
                        if type(parent) is o[9]:
                            md = parent.__dict__
                            if type(md) is dict and len(md) <= 256 and all(type(k) is str for k in md):
                                key = _RL_NAMES[index].rsplit(".", 1)[1]
                                if md.get(key) is v[3]: del md[key]
                    if cache.get(v[1][1]) is v[3]: del cache[v[1][1]]
                if len(st[14][3]) == 2:
                    first, second = st[14][3]
                    if type(first[0]) is o[9]:
                        md = first[0].__dict__
                        if type(md) is dict and len(md) <= 256 and all(type(k) is str for k in md):
                            if md.get("Contracts") is second[0]: del md["Contracts"]
                    for name, v in zip(("Tests.Contracts", "Tests"), (second, first)):
                        if cache.get(name) is v[0]: del cache[name]
            st[2] = True
            return ("REJECTED_RUNNER_SOURCES", issue, None)
        return ("EXECUTED_RUNNER_SOURCES", "NONE", result)
    return entry, input_handoff, eof_handoff, Loader, gateway, parent_guard, parent_write


def _initialize_rl_control():
    global _RL_INITIALIZED, _RL_MARKER, _RL_CLASS, _rl_entry, _rl_input_handoff, _rl_eof_handoff
    if _RL_INITIALIZED is not False:
        _RL_MARKER = None
        return ("REJECTED_RUNNER_CONTROL", "RUNNER_SOURCE_BINDING")
    _RL_INITIALIZED = True
    try:
        _worker_profile_check(_WORKER_PROFILE_BINDING)
        ns, bi = globals(), globals().get("__builtins__")
        items = _worker_profile_items(_rl_namespace(bi), [0])
        compile_fn, exec_fn, import_fn = bi.get("compile"), bi.get("exec"), bi.get("__import__")
        fs = tuple(_worker_input_function(f, bi) for f in (compile_fn, exec_fn, import_fn))
        _inline_need(all(type(f.__name__) is str and f.__name__ == n for f, n in
            zip((compile_fn, exec_fn, import_fn), ("compile", "exec", "__import__"))), "RUNNER_SOURCE_BINDING")
        cache = _rl_namespace(sys.__dict__.get("modules"))
        _RL_MARKER = object()
        st = [False, False, False, [], [], [], [], [], [], [False] * len(_RL_EDGES), [], [], [], [], [False, False, [], [], []]]
        o = (ns, _RL_MARKER, st, bi, items, compile_fn, exec_fn, fs[0], fs[1],
            _SEMANTIC_CONTROL_ANCHOR[9], _rl_spec_state(_SEMANTIC_CONTROL_ANCHOR[4]), cache,
            _worker_input_run.__code__, (_rl_guard, _rl_guard.__code__), (_rl_write, _rl_write.__code__),
            (_rl_execute, _rl_execute.__code__), (_rl_binding, _rl_binding.__code__), import_fn, fs[2],
            (_rl_parent_binding, _rl_parent_binding.__code__), (_rl_parents, _rl_parents.__code__),
            (_rl_parent_graph, _rl_parent_graph.__code__))
        _rl_entry, _rl_input_handoff, _rl_eof_handoff, _RL_CLASS, gateway, pg, pw = _rl_factory(o)
        method = _RL_CLASS.__dict__["exec_module"]
        st[6].append((_RL_CLASS, tuple(_RL_CLASS() for _ in range(9)), method, method.__code__))
        st[7].append((gateway, gateway.__code__, _worker_profile_function(gateway, [0])))
        pn = {"__builtins__": bi, "__name__": "__main__", "ModuleType": o[9],
              "ModuleSpec": o[10][0], "MappingProxyType": type(type.__dict__)}
        pf = type(make_codefree_parent_registry)(make_codefree_parent_registry.__code__, pn)
        pn["make_codefree_parent_registry"] = pf
        run_codes = tuple(c for c in pf.__code__.co_consts if type(c) is type(pf.__code__) and c.co_name == "run")
        _inline_need(len(run_codes) == 1, "RUNNER_SOURCE_BINDING")
        codes, pending = [], [pf.__code__]
        while pending:
            c = pending.pop()
            if any(c is old for old in codes): continue
            _inline_need(len(codes) < 64 and len(c.co_consts) <= 256, "RUNNER_SOURCE_BINDING")
            codes.append(c)
            for v in c.co_consts:
                if type(v) is not type(c) or any(v is old for old in codes) or any(v is old for old in pending): continue
                _inline_need(len(codes) + len(pending) < 64, "RUNNER_SOURCE_BINDING")
                pending.append(v)
        st[13].append((pf, pf.__code__, pn, _worker_profile_items(pn, [0]),
            _worker_profile_function(pf, [0]), run_codes[0],
            ((pg, _worker_profile_function(pg, [0])), (pw, _worker_profile_function(pw, [0]))),
            tuple(c for c in codes if c is not pf.__code__)))
        return ("BOUND_RUNNER_CONTROL", "NONE")
    except BaseException:
        _RL_MARKER = None
        return ("REJECTED_RUNNER_CONTROL", "RUNNER_SOURCE_BINDING")
'''


def _parent_ast():
    tree = ast.parse(Path(parents.__file__).read_bytes())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef)
             and n.name == "make_codefree_parent_registry"]
    base.base.inputs.base._need(len(nodes) == 1, "TEMPLATE_FORM")
    return nodes[0]


def _runner_nodes():
    original = base._INLINE_HARNESS.replace("_hl_", "_rl_").replace("_HL_", "_RL_").replace("HARNESS", "RUNNER")
    tree = ast.parse(original)
    replacement = ast.parse(_INLINE_RUNNER).body
    replaced = {n.name for n in replacement if isinstance(n, ast.FunctionDef)}
    assigned = {t.id for n in replacement if isinstance(n, ast.Assign)
                for t in n.targets if isinstance(t, ast.Name)}
    kept = [n for n in tree.body if not (isinstance(n, ast.FunctionDef) and n.name in replaced)
            and not (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name)
                and (t.id in assigned or t.id == "_RL_COMMON") for t in n.targets))]
    return kept + replacement


def _helpers():
    text = ast.unparse(ast.Module(body=base._helpers(), type_ignores=[]))
    nodes = ast.parse(text.replace("_hl_", "_rl_").replace("_HL_", "_RL_").replace("HARNESS", "RUNNER")).body
    guard = next(n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == "_rl_guard")
    guard.body[-1:] = ast.parse('''
_inline_need(all(name not in owner[11] for name in _RL_NAMES if name not in published), "RUNNER_SOURCE_BINDING")
_rl_original(owner[19], namespace)(owner, packet)
''').body
    return nodes


# Externe Fixture-/Entrys bleiben unter ihren tatsächlichen Schnittstellennamen.
_PRESERVED = {"_worker_input_seal", "_worker_input_entry", "_worker_profile_state",
              "_inline_observe_selected_worker_profile", "_inline_kernel_check"}


def _runner_worker_tree(tree, protected):
    """Nur den elfknotigen Parentabgleich aus dieser Workerkomposition auslassen."""
    control = base.base.inputs.base
    names = ("_SESSION_SHAPES", "_SESSION_TRACES", "_SESSION_COUNTS", "_SESSION_ISSUES",
             "_session_parse", "_session_report", "_session_semantics", "_session_order",
             "_session_channel_sha", "_session_issue", "_inline_match_session_end")
    def binding(node):
        if isinstance(node, ast.FunctionDef): return node.name
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            return node.targets[0].id
        return None
    canonical = ast.parse(control._INLINE_SESSION_END_MATCH).body
    control._need(len(canonical) == 11 and tuple(binding(n) for n in canonical) == names, "TEMPLATE_FORM")
    selected = []
    for name, original in zip(names, canonical):
        matches = [n for n in tree.body if binding(n) == name]
        control._need(len(matches) == 1 and ast.dump(matches[0]) == ast.dump(original), "TEMPLATE_FORM")
        selected.append(matches[0])
    remaining = [n for n in tree.body if not any(n is old for old in selected)]
    for root in remaining + [protected]:
        for node in ast.walk(root):
            values = [getattr(node, field, None) for field in ("id", "arg", "name", "asname", "rest", "attr", "module")]
            if isinstance(node, (ast.Global, ast.Nonlocal)): values += node.names
            if isinstance(node, ast.keyword): values.append(node.arg)
            if isinstance(node, ast.MatchClass): values += node.kwd_attrs
            if isinstance(node, ast.Constant) and type(node.value) is str:
                control._need(all(name not in node.value for name in names), "TEMPLATE_FORM")
            control._need(not any(value in names for value in values), "TEMPLATE_FORM")
    tree.body = remaining
    return tree


def _shorten_globals(tree, protected):
    protected_nodes = tuple(ast.walk(protected))
    nodes = tuple(ast.walk(tree)) + protected_nodes
    occupied = {getattr(n, field, None) for n in nodes for field in ("id", "arg", "name", "asname", "rest", "attr")
                if isinstance(getattr(n, field, None), str)}
    occupied.update(name for n in nodes if isinstance(n, (ast.Global, ast.Nonlocal)) for name in n.names)
    texts = [n.value for n in nodes if isinstance(n, ast.Constant) and type(n.value) is str]
    mapping = {}
    for definition in tree.body:
        if not isinstance(definition, ast.FunctionDef): continue
        name = definition.name
        if not (name.startswith(("_inline_", "_semantic_", "_worker_profile_", "_worker_input_", "_report_", "_rl_", "_worker_report_"))
                or name in ("_require", "_dictionary")) or name in _PRESERVED: continue
        references = [n for n in nodes if isinstance(n, ast.Name) and n.id == name]
        if any(isinstance(n, ast.Name) and n.id == name for n in protected_nodes): continue
        if not references or any(not isinstance(n.ctx, ast.Load) for n in references): continue
        if sum(isinstance(n, ast.FunctionDef) and n.name == name for n in nodes) != 1: continue
        if any(name in text for text in texts): continue
        if any(isinstance(n, (ast.Global, ast.Nonlocal)) and name in n.names for n in nodes): continue
        if any(isinstance(n, ast.Attribute) and n.attr == name for n in nodes): continue
        if any(n is not definition and any(getattr(n, f, None) == name for f in ("arg", "name", "asname", "rest")) for n in nodes): continue
        number = len(mapping)
        target = "_g" + str(number)
        while target in occupied or any(target in text for text in texts):
            number += 1
            target = "_g" + str(number)
        occupied.add(target)
        mapping[name] = target
        definition.name = target
        for reference in references: reference.id = target
    return tree


def _shorten_uniform_locals(tree, protected):
    """Uniforme Bijection; compilerbestimmte globale Ursprünge bleiben gesperrt."""
    nodes = tuple(ast.walk(tree)) + tuple(ast.walk(protected))
    occupied = {getattr(n, f, None) for n in nodes
                for f in ("id", "arg", "name", "asname", "rest", "attr")
                if isinstance(getattr(n, f, None), str)}
    occupied.update(name for n in nodes if isinstance(n, (ast.Global, ast.Nonlocal)) for name in n.names)
    texts = tuple(n.value for n in nodes if isinstance(n, ast.Constant) and type(n.value) is str)
    forbidden = {n.attr for n in nodes if isinstance(n, ast.Attribute)}
    forbidden.update(n.arg for n in nodes if isinstance(n, ast.keyword) and n.arg)
    forbidden.update(n.name for n in nodes if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)))
    forbidden.update(n.name for n in nodes if isinstance(n, ast.alias))
    forbidden.update(n.asname for n in nodes if isinstance(n, ast.alias) and n.asname)
    # Symboltabellen erfassen auch Defaults und das äußere erste Comp-Iterable.
    table = symtable.symtable(ast.unparse(tree) + "\n" + ast.unparse(protected), "<runner-alpha>", "exec")
    pending = [table]
    while pending:
        scope = pending.pop()
        for symbol in scope.get_symbols():
            occupied.add(symbol.get_name())
            if symbol.is_global() or scope.get_type() == "class": forbidden.add(symbol.get_name())
        pending.extend(scope.get_children())
    scopes = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)
    public = _PRESERVED | {"entry", "seal", "handoff", "gateway", "input_handoff", "eof_handoff",
                           "parent_guard", "parent_write", "create_module", "exec_module"}
    def inspect(node, ancestors=()):
        chain = ancestors + ((node,) if isinstance(node, scopes) else ())
        if isinstance(node, ast.ClassDef):
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    forbidden.update(n.arg for n in ast.walk(member.args) if isinstance(n, ast.arg))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in public:
            forbidden.update(n.arg for n in ast.walk(node.args) if isinstance(n, ast.arg))
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in ("locals", "vars", "eval", "exec")):
            # Reflexion kann auch äußere Closure-/Defaultnamen beobachten.
            selected = chain[0] if chain else tree
            forbidden.update(getattr(n, f, None) for n in ast.walk(selected)
                             for f in ("id", "arg", "name", "asname", "rest"))
        if isinstance(node, (ast.Match, ast.TypeAlias)):
            forbidden.update(getattr(n, f, None) for n in ast.walk(node)
                             for f in ("id", "arg", "name", "asname", "rest"))
        for child in ast.iter_child_nodes(node): inspect(child, chain)
    inspect(tree)
    chosen, ordinal = {}, 0
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    names.update(n.arg for n in ast.walk(tree) if isinstance(n, ast.arg))
    for name in sorted(names):
        if len(name) < 4 or name.startswith("__") or name in forbidden or any(name in s for s in texts): continue
        while True:
            short = "z" + str(ordinal)
            ordinal += 1
            if short not in occupied and not any(short in s for s in texts): break
        chosen[name] = short
        occupied.add(short)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name): node.id = chosen.get(node.id, node.id)
        elif isinstance(node, ast.arg): node.arg = chosen.get(node.arg, node.arg)
        elif isinstance(node, ast.ExceptHandler): node.name = chosen.get(node.name, node.name)
        elif isinstance(node, ast.Nonlocal): node.names = [chosen.get(n, n) for n in node.names]
    return tree


def _compact_raw_literal(text, raw):
    """Ein einziges wertgleiches Bytesliteral; keinerlei Runtime-Dekodierung."""
    before = ast.parse(text)
    values = [n.value for n in before.body if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == "_EXPECTED_PROFILE_RAW" for t in n.targets)]
    base.base.inputs.base._need(len(values) == 1 and isinstance(values[0], ast.Constant)
        and values[0].value == raw and type(raw) is bytes, "TEMPLATE_FORM")
    alternatives = [repr(raw).encode("ascii")]
    for quote in (34, 39):
        chunks = [b"b" + bytes([quote]) * 3]
        for value in raw:
            if value == 10: chunks.append(b"\n")
            elif value == 13: chunks.append(b"\\r")
            elif value in (92, quote): chunks.append(b"\\" + bytes([value]))
            elif 32 <= value < 127: chunks.append(bytes([value]))
            else: chunks.append(("\\x%02x" % value).encode("ascii"))
        chunks.append(bytes([quote]) * 3)
        alternatives.append(b"".join(chunks))
    literal = min(alternatives, key=len)
    base.base.inputs.base._need(ast.literal_eval(literal.decode("ascii")) == raw, "TEMPLATE_FORM")
    value = values[0]
    lines = text.encode("utf-8").splitlines(keepends=True)
    start = sum(map(len, lines[:value.lineno - 1])) + value.col_offset
    end = sum(map(len, lines[:value.end_lineno - 1])) + value.end_col_offset
    data = text.encode("utf-8")
    result = (data[:start] + literal + data[end:]).decode("utf-8")
    base.base.inputs.base._need(ast.dump(ast.parse(result)) == ast.dump(before), "TEMPLATE_FORM")
    return result


def build_runner_loader_control_bootstrap(profile_raw, *, logical_profile,
                                          expected_soabi, expected_destshared):
    inputs = base.base.inputs
    selected = inputs.build_worker_input_control_bootstrap(profile_raw,
        logical_profile=logical_profile, expected_soabi=expected_soabi, expected_destshared=expected_destshared)
    tree = ast.parse(selected.source)
    init = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_initialize_worker_input_control")
    block = next(n for n in init.body if isinstance(n, ast.Try)).body
    positions = [i for i, n in enumerate(block) if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Tuple) and any(isinstance(v, ast.Name) and v.id == "_worker_input_entry" for v in t.elts) for t in n.targets)]
    inputs.base._need(len(positions) == 1, "TEMPLATE_FORM")
    block.insert(positions[0] + 1, ast.parse("_rl_input_handoff(owner, _worker_input_entry)").body[0])
    receiver = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_worker_input_run")
    inputs.base._need(isinstance(receiver.body[-1], ast.Return) and ast.dump(receiver.body[-1].value)
        == ast.dump(ast.parse('("RECEIVED_WORKER_INPUTS", "NONE", result)', mode="eval").body), "TEMPLATE_FORM")
    receiver.body.insert(len(receiver.body) - 1, ast.parse("_rl_eof_handoff(owner, frame, result)").body[0])
    main = next(n for n in tree.body if isinstance(n, ast.If))
    inputs.base._need(ast.dump(main.body[-1]) == ast.dump(ast.parse("_worker_input_main()").body[0]), "TEMPLATE_FORM")
    main.body.insert(2, ast.parse("_initialize_rl_control()").body[0])
    main.body[-1] = ast.parse("_rl_main()").body[0]
    parent = _parent_ast()
    tree.body = [n for n in tree.body if n is not main] + _helpers() + _runner_nodes() + [main]
    tree = _runner_worker_tree(tree, parent)
    tree = _shorten_globals(tree, parent)
    tree = base.base._compact_locals(_shorten_uniform_locals(tree, parent))
    tree.body.insert(len(tree.body) - 1, parent)
    text = inputs._compact_indentation(ast.unparse(ast.fix_missing_locations(tree)) + "\n")
    source = base.base._compact_token_gaps(_compact_raw_literal(text, profile_raw)).encode("utf-8", "strict")
    inputs.base._need(len(source) <= inputs.base.MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return inputs.base.BootstrapSource(source, profile_raw, logical_profile,
        hashlib.sha256(source).hexdigest(), hashlib.sha256(profile_raw).hexdigest(), len(source))
