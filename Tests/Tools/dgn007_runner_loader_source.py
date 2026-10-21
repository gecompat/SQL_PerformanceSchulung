"""Additive vollständige Runnerroute; Generierung startet keine Kandidaten."""
import ast
import hashlib
from pathlib import Path
import symtable

import dgn007_harness_loader_source as base


_INLINE_RUNNER = r'''_RL_ORDER = (0, 1, 5, 3, 4, 6, 7, 8)
_RL_SEQUENCES = (1, 2, None, 4, 5, 3, 8, 9, 10)
_RL_NAMES = ('run_dgn007_automated_setup', 'execution_target', 'docker_sqlcmd_proxy', 'run_demo', 'orchestrate_sessions', 'sqlcmd_process', 'Tests.Contracts.dgn007_capture_projection', 'Tests.Contracts.dgn007_collector_transport', 'Tests.Contracts.dgn007_prospective_acceptance')
_RL_MEMBERS = ('Tests/Runtime/run_dgn007_automated_setup.py', 'Tests/Runtime/execution_target.py', 'Tests/Runtime/docker_sqlcmd_proxy.py', 'Demos/00_Framework/Tools/run_demo.py', 'Demos/00_Framework/Tools/orchestrate_sessions.py', 'Demos/00_Framework/Tools/sqlcmd_process.py', 'Tests/Contracts/dgn007_capture_projection.py', 'Tests/Contracts/dgn007_collector_transport.py', 'Tests/Contracts/dgn007_prospective_acceptance.py')
_RL_OWN = _RL_NAMES + ('Tests', 'Tests.Contracts')
_RL_ORIGINS = tuple(('/dgn007/source/' + str(n) + '.py' for n in range(9)))
_RL_EDGES = ((0, 'execution_target', None, 1), (0, 'execution_target', ('ExecutionTarget', 'ExecutionTargetError'), 1), (1, 'sqlcmd_process', ('resolve_sqlcmd',), 5), (0, 'run_demo', ('load_manifest',), 3), (3, 'orchestrate_sessions', ('run_manifest',), 4), (4, 'sqlcmd_process', ('build_sqlcmd_command', 'collect_process', 'resolve_sqlcmd', 'start_sqlcmd'), 5), (3, 'sqlcmd_process', ('build_sqlcmd_command', 'extract_summary', 'resolve_sqlcmd', 'run_sqlcmd'), 5), (0, 'sqlcmd_process', ('SqlcmdResult', 'build_sqlcmd_command', 'run_sqlcmd'), 5), (0, 'sqlcmd_process', ('start_sqlcmd', '_terminate_process_tree'), 5), (0, 'sqlcmd_process', ('_linux_descendants', '_linux_process_identity'), 5), (0, 'Tests.Contracts.dgn007_capture_projection', ('decode_projection', 'ProjectionError'), 6), (6, 'Tests.Contracts.dgn007_collector_transport', ('CaptureBody', 'SCHEMA', 'TransportError', 'decode_capture'), 7), (7, 'Tests.Contracts.dgn007_prospective_acceptance', ('AcceptanceContract', 'ActivePlanRecord', 'MAX_SQL_TICKS', 'PlanUnionRecord', 'QueryFamilyRecord', 'REQUEST_MAPPING', 'WindowRecord', '_contract_valid'), 8), (6, 'Tests.Contracts.dgn007_prospective_acceptance', ('AcceptanceContract', '_contract_valid'), 8), (0, 'Tests.Contracts.dgn007_collector_transport', ('CaptureBody',), 7), (0, 'Tests.Contracts.dgn007_prospective_acceptance', ('contract_from_mapping',), 8))
_RL_STD = ((('__future__', ('annotations',)), ('argparse', None), ('dataclasses', ('dataclass', 'field')), ('json', None), ('os', None), ('pathlib', ('Path',)), ('re', None), ('signal', None), ('subprocess', None), ('sys', None), ('threading', None), ('time', None), ('typing', ('Sequence',))), (('__future__', ('annotations',)), ('dataclasses', ('dataclass',)), ('os', None), ('pathlib', ('Path',)), ('re', None), ('subprocess', None), ('sys', None)), (), (('__future__', ('annotations',)), ('argparse', None), ('dataclasses', ('dataclass',)), ('json', None), ('os', None), ('pathlib', ('Path',)), ('re', None), ('sys', None), ('time', None), ('typing', ('Any',))), (('__future__', ('annotations',)), ('argparse', None), ('dataclasses', ('dataclass',)), ('json', None), ('os', None), ('pathlib', ('Path',)), ('re', None), ('sys', None), ('time', None), ('typing', ('Any',))), (('__future__', ('annotations',)), ('dataclasses', ('dataclass',)), ('os', None), ('pathlib', ('Path',)), ('re', None), ('shutil', None), ('signal', None), ('subprocess', None), ('sys', None), ('time', None), ('typing', ('Mapping', 'Sequence'))), (('__future__', ('annotations',)), ('re', None)), (('__future__', ('annotations',)), ('dataclasses', ('dataclass', 'fields')), ('decimal', ('Decimal',)), ('fractions', ('Fraction',)), ('json', None), ('re', None)), (('__future__', ('annotations',)), ('dataclasses', ('dataclass',)), ('decimal', ('Decimal',)), ('fractions', ('Fraction',)), ('hashlib', None), ('json', None)))

def _rl_kernel_check(context):
    T, L, FT, DT, TT, ST, GA, DG, DI, E, LS, Z, BT = context[0]
    namespace, bi, items = context[2:5]
    if T(namespace) is not DT or T(bi) is not DT or L(namespace) > 256 or L(bi) != L(items):
        raise E()
    for mapping in (namespace, bi):
        for key in mapping:
            if T(key) is not ST or L(key) > 4096 or '\x00' in key:
                raise E()
    for key, value in items:
        if DG(bi, key) is not value:
            raise E()
    state, holder, received, input_state = context[8], context[13], context[5], context[14]
    if T(state) is not LS or L(state) != 15 or state[3] is not holder or T(holder) is not LS or L(holder) != 1 or holder[0] is not received:
        raise E()
    if T(input_state) is not LS or L(input_state) != context[15] or T(input_state[6]) is not BT:
        raise E()
    for saved in (context[1], context[6]):
        fn = saved[0]
        if T(fn) is not FT or fn.__code__ is not saved[1] or fn.__globals__ is not saved[2] or fn.__defaults__ is not saved[3] or fn.__kwdefaults__ is not saved[4] or fn.__closure__ is not saved[6] or GA(fn, '__annotate__', None) is not saved[8]:
            raise E()
        kw = fn.__kwdefaults__
        if kw is not None:
            if T(kw) is not DT or L(kw) != L(saved[5]):
                raise E()
            for key in kw:
                if T(key) is not ST or L(key) > 4096 or '\x00' in key:
                    raise E()
            for key, value in saved[5]:
                if DG(kw, key) is not value:
                    raise E()
        cells = fn.__closure__
        if cells is not None:
            if T(cells) is not TT or L(cells) != L(saved[7]):
                raise E()
            for cell, value in Z(cells, saved[7]):
                if cell.cell_contents is not value:
                    raise E()
    frame = context[7]
    context[1][0](frame[0], frame[1], input_state[6])

def _rl_gate_impl(actual, packet, expected=None, pins=(), primitives=()):
    T, L, FT, DT, TT, ST, GA, DG, DI, E, LS, Z, BT = primitives
    if actual is not expected:
        raise E()
    ns, marker, st, bi, items = expected[:5]
    if T(ns) is not DT or T(bi) is not DT or L(ns) > 256 or (L(bi) > 256):
        raise E()
    for mapping in (ns, bi):
        for key in mapping:
            if T(key) is not ST or L(key) > 4096 or '\x00' in key:
                raise E()
    if DG(ns, '_RL_OWNER') is not expected or L(bi) != L(items):
        raise E()
    for key, value in items:
        if DG(bi, key) is not value:
            raise E()
    if T(pins) is not TT or L(pins) > 256:
        raise E()
    pending = LS(pins)
    if L(pending) > 256:
        raise E()
    while pending:
        saved = pending.pop()
        if T(saved) is not TT or L(saved) not in (9, 10):
            raise E()
        fn = saved[0]
        if T(fn) is not FT or fn.__code__ is not saved[1] or fn.__globals__ is not saved[2] or (fn.__defaults__ is not saved[3]) or (fn.__kwdefaults__ is not saved[4]) or (fn.__closure__ is not saved[6]) or (GA(fn, '__annotate__', None) is not saved[8]):
            raise E()
        kw = fn.__kwdefaults__
        if kw is None:
            if saved[5] != ():
                raise E()
        else:
            if T(kw) is not DT or L(kw) != L(saved[5]) or L(kw) > 256:
                raise E()
            for key in kw:
                if T(key) is not ST or L(key) > 4096 or '\x00' in key:
                    raise E()
            for key, value in saved[5]:
                if DG(kw, key) is not value:
                    raise E()
        cells = fn.__closure__
        if cells is None:
            if saved[7] != ():
                raise E()
        else:
            if T(cells) is not TT or L(cells) != L(saved[7]) or L(cells) > 256:
                raise E()
            for cell, value in Z(cells, saved[7]):
                if cell.cell_contents is not value:
                    raise E()
        if L(saved) == 10 and saved[9] is not None:
            if L(pending) >= 256:
                raise E()
            pending.append(saved[9])
    if T(st) is not LS or L(st) != 15:
        raise E()
    for index, held in Z((3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14), expected[23]):
        if st[index] is not held or T(held) is not LS or L(held) > 32:
            raise E()
    for index in (0, 1, 2):
        if T(st[index]) is not BT:
            raise E()
    if L(st[3]) != 1 or T(st[3][0]) is not TT or L(st[3][0]) != 3:
        raise E()
    io = st[3][0][0]
    fn = st[3][0][1]
    frame = None
    if T(fn) is not FT or fn.__globals__ is not ns or fn.__code__ is not st[3][0][2]:
        raise E()
    for name, cell in Z(fn.__code__.co_freevars, fn.__closure__):
        if name == 'frame':
            frame = cell.cell_contents
    if T(frame) is not TT or L(frame) != 4 or T(io[2][6]) is not BT:
        raise E()
    check, code = io[12:]
    if T(check) is not FT or check.__code__ is not code or check.__globals__ is not ns:
        raise E()
    check(frame[0], frame[1], io[2][6])
    if packet is not None:
        check = expected[13][0]
        check(expected, packet)

def _rl_binding(o, v):
    _inline_need(type(v) is list and len(v) == 21, 'RUNNER_SOURCE_BINDING')
    _inline_need(type(v[19]) is list and len(v[19]) == 2 and (type(v[20]) is list) and (len(v[20]) == 2), 'RUNNER_SOURCE_BINDING')
    for slot in (0, 1):
        phase, offset, row = (v[19][slot], v[16 + slot], v[20][slot])
        _inline_need(type(phase) is int and 0 <= phase <= 4 and (type(offset) is int) and (offset >= 0), 'RUNNER_SOURCE_BINDING')
        _inline_need(row is None and phase == 0 and (offset == 0) or (type(row) is bytes and 0 < len(row) <= 256 and (offset <= len(row))), 'RUNNER_SOURCE_BINDING')
        if phase == 1:
            _inline_need(offset == 0, 'RUNNER_SOURCE_BINDING')
        if phase == 3:
            _inline_need(0 < offset < len(row), 'RUNNER_SOURCE_BINDING')
        if phase == 4:
            _inline_need(offset == len(row), 'RUNNER_SOURCE_BINDING')
    _inline_need(v[19][1] == 0 or v[19][0] == 4, 'RUNNER_SOURCE_BINDING')
    _inline_need(v[9] is False or (v[9] is True and v[19][1] == 4), 'RUNNER_SOURCE_BINDING')
    raw, d, context, m, spec, origin = v[:6]
    _inline_need(type(d) is tuple and len(d) in (1, 5) and (type(d[0]) is int) and (d[0] in (0, 1, 5, 3, 4, 6, 7, 8, 9, 10)), 'RUNNER_SOURCE_BINDING')
    index = d[0]
    parent = index >= 9
    _inline_need(len(d) == (1 if parent else 5), 'RUNNER_SOURCE_BINDING')
    if not parent:
        _inline_need(v[6] is None or (type(v[6]) is type(_rl_binding.__code__) and type(v[6].co_filename) is str and (v[6].co_filename == origin)), 'RUNNER_SOURCE_BINDING')
        _inline_need(v[7] is None or v[7] is v[6], 'RUNNER_SOURCE_BINDING')
    stage, locations = v[14:16]
    actual, bodies = o[2][4][0][0][0][2:]
    _inline_need(context is actual[2], 'RUNNER_SOURCE_BINDING')
    if parent:
        _inline_need(len(d) == 1 and raw is None and (origin is None), 'RUNNER_SOURCE_BINDING')
    else:
        _inline_need(d is actual[0][5][index] and raw is bodies[index] and (origin is _RL_ORIGINS[index]), 'RUNNER_SOURCE_BINDING')
    _inline_need(all((type(v[i]) is bool for i in (8, 9, 11, 12, 13, 18))), 'RUNNER_SOURCE_BINDING')
    _inline_need(type(stage) is int and 0 <= stage <= 6, 'RUNNER_SOURCE_BINDING')
    if stage < 2:
        _inline_need(m is None and spec is None, 'RUNNER_SOURCE_BINDING')
        return
    _inline_need(type(m) is o[9], 'RUNNER_SOURCE_BINDING')
    md = _rl_namespace(m.__dict__)
    name = _RL_OWN[index]
    _inline_need(type(md.get('__name__')) is str and md['__name__'] == name, 'RUNNER_SOURCE_BINDING')
    if stage < 4:
        _inline_need(spec is None and md.get('__spec__') is None and (md.get('__loader__') is None) and (md.get('__package__') is None) and ('__path__' not in md) and ('__file__' not in md) and ('__cached__' not in md), 'RUNNER_SOURCE_BINDING')
        return
    _inline_need(type(spec) is o[10][0], 'RUNNER_SOURCE_BINDING')
    sd = _rl_namespace(spec.__dict__)
    loader = None if parent else o[2][6][0][1][index]
    _inline_need(type(sd.get('name')) is str and sd['name'] == name and (sd.get('loader') is loader) and (sd.get('origin') is origin) and (sd.get('loader_state') is None), 'RUNNER_SOURCE_BINDING')
    if stage == 4:
        _inline_need('__path__' not in md and '__file__' not in md and ('__cached__' not in md) and (sd.get('_cached') is None), 'RUNNER_SOURCE_BINDING')
        _inline_need(sd.get('_set_fileattr') is False and md.get('__spec__') is None and (md.get('__package__') is None) and (md.get('__loader__') is None), 'RUNNER_SOURCE_BINDING')
        if parent:
            _inline_need(type(sd.get('submodule_search_locations')) is list and len(sd['submodule_search_locations']) == 0, 'RUNNER_SOURCE_BINDING')
        else:
            _inline_need(sd.get('submodule_search_locations') is None, 'RUNNER_SOURCE_BINDING')
        return
    _inline_need(md.get('__spec__') is spec and md.get('__loader__') is loader and (type(md.get('__package__')) is str) and (md['__package__'] == (name if parent else 'Tests.Contracts' if index >= 6 else '')), 'RUNNER_SOURCE_BINDING')
    if parent:
        _inline_need(type(locations) is list and len(locations) == 0 and (md.get('__path__') is locations) and (sd.get('submodule_search_locations') is locations) and (sd.get('_set_fileattr') is False) and ('__file__' not in md) and ('__cached__' not in md) and (sd.get('_cached') is None), 'RUNNER_SOURCE_BINDING')
    else:
        _inline_need(sd.get('submodule_search_locations') is None and sd.get('_set_fileattr') is True and ('__path__' not in md) and (type(md.get('__file__')) is str) and (md['__file__'] == origin) and (md.get('__builtins__') is v[10]), 'RUNNER_SOURCE_BINDING')
        items = _worker_profile_items(_rl_namespace(v[10]), [0])
        _inline_need(len(items) == len(o[4]) and all((a[0] == b[0] and a[1] is (o[2][7][0][0] if b[0] == '__import__' else b[1]) for a, b in zip(items, o[4]))), 'RUNNER_SOURCE_BINDING')
    _inline_need(o[11].get(name) is m if v[8] is True else name not in o[11], 'RUNNER_SOURCE_BINDING')

def _rl_parent_binding(o, p):
    values = o[2][14]
    _inline_need(type(values) is list and len(values) <= 2, 'RUNNER_SOURCE_BINDING')
    for v in values:
        _rl_binding(o, v)
    published = {v[1][0]: v for v in values if v[8] is True}
    for index in (9, 10):
        _inline_need(o[11].get(_RL_OWN[index]) is published[index][3] if index in published else _RL_OWN[index] not in o[11], 'RUNNER_SOURCE_BINDING')
    if 9 in published:
        md = _rl_namespace(published[9][3].__dict__)
        linked = next((v for v in values if v[1][0] == 10 and v[18] is True), None)
        _inline_need(md.get('Contracts') is linked[3] if linked is not None else 'Contracts' not in md, 'RUNNER_SOURCE_BINDING')
    if 10 in published:
        md = _rl_namespace(published[10][3].__dict__)
        for index in (6, 7, 8):
            found = [v for v in o[2][5] if v[1][0] == index and v[8] is True]
            key = _RL_NAMES[index].rsplit('.', 1)[1]
            _inline_need(md.get(key) is found[0][3] if len(found) == 1 else key not in md, 'RUNNER_SOURCE_BINDING')

def _rl_make_pair(o, p, v, *, _guard=None, _kernel=None, _primitives=()):
    _rl_checkpoint(o, p)
    _inline_need(o[2][2] is False and (v[14] == 0 and v[3] is None and (v[4] is None)), 'RUNNER_SOURCE_ORDER')
    v[14] = 1
    _rl_checkpoint(o, p)
    try:
        v[3] = o[9](_RL_OWN[v[1][0]])
    finally:
        if v[3] is not None:
            v[14] = 2
        _rl_checkpoint(o, p)
    _inline_need(type(v[3]) is o[9], 'RUNNER_SOURCE_BINDING')
    md = _rl_namespace(v[3].__dict__)
    _kernel[11].append((v[1][0], v[3], md))
    v[14] = 3
    _rl_checkpoint(o, p)
    index = v[1][0]
    try:
        v[4] = o[10][0](_RL_OWN[index], None if index >= 9 else o[2][6][0][1][index], origin=v[5], is_package=index >= 9)
    finally:
        if v[4] is not None:
            v[14] = 4
        _rl_checkpoint(o, p)
    _inline_need(type(v[4]) is o[10][0], 'RUNNER_SOURCE_BINDING')
    md, sd = (_rl_namespace(v[3].__dict__), _rl_namespace(v[4].__dict__))
    if index >= 9:
        v[15] = sd['submodule_search_locations']
        md.update(__package__=_RL_OWN[index], __spec__=v[4], __loader__=None, __path__=v[15])
    else:
        sd['_set_fileattr'] = True
        v[10] = dict(o[4])
        v[10]['__import__'] = o[2][7][0][0]
        md.update(__package__='Tests.Contracts' if index >= 6 else '', __spec__=v[4], __loader__=o[2][6][0][1][index], __file__=v[5], __builtins__=v[10])
    v[14] = 5
    _rl_checkpoint(o, p)

def _rl_parents(o, p, *, _guard=None, _kernel=None, _primitives=()):
    st = o[2]
    _rl_checkpoint(o, p)
    _inline_need(st[2] is False and (not st[14] and len(st[5]) == 5 and (tuple((v[1][0] for v in st[5])) == (0, 1, 5, 3, 4)) and (len(st[8]) == 1) and (st[8][0] is st[5][0]) and (st[8][0][13] is True) and (st[8][0][7] is None) and all((v[9] is True for v in st[5][1:]))), 'RUNNER_SOURCE_ORDER')
    for index in (9, 10):
        v = [None, (index,), p[0][0][2][2], None, None, None, None, None, False, False, None, False, False, False, 0, None, 0, 0, False, [0, 0], [None, None]]
        st[14].append(v)
        _rl_make_pair(o, p, v)
        o[11][_RL_OWN[index]] = v[3]
        v[8], v[14] = (True, 6)
        _rl_checkpoint(o, p)
        if index == 10:
            st[14][0][3].__dict__['Contracts'] = v[3]
            v[18] = True
            _rl_checkpoint(o, p)
        for tag in ('BEGIN', 'COMPLETE'):
            sequence = index - 3
            row = _report_json((tag, 1, sequence, 'PARENT', index - 9, st[12][0], None, index, sequence), p[1][0][3]) + b'\n'
            _rl_checkpoint(o, p)
            _rl_write(o, p, row, record=v, complete=tag == 'COMPLETE')
            _rl_checkpoint(o, p)
        v[9] = True
    _rl_checkpoint(o, p)

def _rl_run(o, p, index, *, _guard=None, _kernel=None, _primitives=()):
    ns, marker, st = o[:3]
    guard = o[13]
    _rl_checkpoint(o, p)
    _inline_need(st[2] is False and (type(index) is int and len(st[5]) < 8 and (index == _RL_ORDER[len(st[5])])), 'RUNNER_SOURCE_ORDER')
    received, first, second = p[0]
    actual, bodies = received[2:]
    context, d, raw = (actual[2], actual[0][5][index], bodies[index])
    _inline_need(actual[1][:3] == (1, 'run_dgn007_automated_setup', 'PRE_IMPORT') and d[:3] == (index, _RL_NAMES[index], _RL_MEMBERS[index]), 'RUNNER_SOURCE_SELECTION')
    if index == 0:
        _inline_need(not st[8] and all((n not in o[11] for n in _RL_OWN)), 'RUNNER_SOURCE_BINDING')
        digest = _inline_context_digest(context, expected_format=_COMMAND_FORMAT)
        _rl_checkpoint(o, p)
        _inline_need(type(digest) is tuple and digest[:2] == ('FORMATTED_CONTEXT_DIGEST', 'NONE'), 'RUNNER_SOURCE_BINDING')
        st[12].append(digest[2])
    else:
        _inline_need(st[8] and st[8][-1][13] is True and (st[8][-1][7] is None), 'RUNNER_SOURCE_ORDER')
    if index >= 6:
        _inline_need(len(st[14]) == 2 and all((v[9] is True for v in st[14])), 'RUNNER_SOURCE_BINDING')
    cls, loaders, method, code = st[6][0]
    v = [raw, d, context, None, None, _RL_ORIGINS[index], None, None, False, False, None, False, False, False, 0, None, 0, 0, False, [0, 0], [None, None]]
    st[5].append(v)
    st[8].append(v)
    stack = st[8]
    try:
        _rl_make_pair(o, p, v)
        m, spec = v[3:5]
        _rl_checkpoint(o, p)
        o[11][_RL_NAMES[index]] = m
        if index >= 6:
            st[14][1][3].__dict__[_RL_NAMES[index].rsplit('.', 1)[1]] = m
        v[8], v[14] = (True, 6)
        _rl_checkpoint(o, p)
        sequence = _RL_SEQUENCES[index]
        fields = (1, sequence, 'SOURCE', index, st[12][0], d[4], index, sequence)
        begin = _report_json(('BEGIN',) + fields, p[1][0][3]) + b'\n'
        _rl_checkpoint(o, p)
        _rl_write(o, p, begin, record=v, complete=False)
        _rl_checkpoint(o, p)
        v[11] = True
        _inline_need(method.__code__ is code and method.__globals__ is ns, 'RUNNER_SOURCE_BINDING')
        method(loaders[index], m)
        _rl_checkpoint(o, p)
        _inline_need(v[6] is not None and v[7] is v[6], 'RUNNER_SOURCE_BINDING')
        complete = _report_json(('COMPLETE',) + fields, p[1][0][3]) + b'\n'
        _rl_checkpoint(o, p)
        _rl_write(o, p, complete, record=v, complete=True)
        _rl_checkpoint(o, p)
        v[9] = True
        return m
    finally:
        if stack and stack[-1] is v:
            stack.pop()
        else:
            st[2] = True

def _rl_factory(o, *, _guard=None, _kernel=None, _primitives=()):
    B = BaseException
    T0, L0, LS0, TT0 = type, len, list, tuple
    ns, marker, st = o[:3]
    run, rc = (_rl_run, _rl_run.__code__)
    action, ac = o[20]
    guard, gc = o[13]
    io_record = None

    def bind_kernel(context):
        nonlocal _kernel
        if _kernel is not None:
            raise RuntimeError()
        _kernel = context

    def input_capture():
        return io_record

    def invoke(index):
        original_owner, original_state = o, st
        if run.__code__ is not rc or run.__globals__ is not ns:
            raise
        return run(original_owner, original_state[4][0], index)

    class Loader:
        __slots__ = ()

        def exec_module(self, m):
            original_owner, original_state = o, st
            if not (original_state[0] is True and original_state[1] is False and (original_state[2] is False) and original_state[8]):
                original_state[2] = True
                raise
            _rl_checkpoint(original_owner, original_state[4][0] if original_state[4] else None)
            v = original_state[8][-1]
            if not (m is v[3] and self is original_state[6][0][1][v[1][0]] and (v[11] is True) and (v[12] is False)):
                original_state[2] = True
                raise
            v[11], v[12] = (False, True)
            _rl_original(original_owner[15], ns)(original_owner, original_state[4][0], m)

    def gateway(name, globals=None, locals=None, fromlist=(), level=0):
        original_owner, original_state = o, st
        reserved = False
        try:
            _rl_checkpoint(original_owner, original_state[4][0] if original_state[4] else None)
            _inline_need(original_state[8], 'RUNNER_SOURCE_IMPORT')
            v = original_state[8][-1]
            index = v[1][0]
            _inline_need(v[13] is True and v[6] is not None and (v[7] is None) and (globals is v[3].__dict__) and (locals is None or locals is globals) and (index not in original_state[11]), 'RUNNER_SOURCE_IMPORT')
            _rl_namespace(globals)
            _inline_need(type(name) is str and 0 < len(name) <= 256 and ('\x00' not in name) and (type(level) is int) and (level == 0), 'RUNNER_SOURCE_IMPORT')
            _inline_need(fromlist is None or (type(fromlist) is tuple and len(fromlist) <= 16 and all((type(n) is str and 0 < len(n) <= 256 and ('\x00' not in n) and (n != '*') for n in fromlist))), 'RUNNER_SOURCE_IMPORT')
            original_state[11].append(index)
            reserved = True
            matches = [n for n, edge in enumerate(_RL_EDGES) if edge[:3] == (index, name, fromlist)]
            if matches:
                _inline_need(len(matches) == 1, 'RUNNER_SOURCE_ORDER')
                edge = matches[0]
                _inline_need(original_state[9][edge] is False, 'RUNNER_SOURCE_ORDER')
                original_state[9][edge] = True
                target = _RL_EDGES[edge][3]
                existing = [w for w in original_state[5] if w[1][0] == target]
                if existing:
                    _inline_need(len(existing) == 1 and existing[0][9] is True, 'RUNNER_SOURCE_ORDER')
                    _rl_checkpoint(original_owner, original_state[4][0] if original_state[4] else None)
                    m = existing[0][3]
                else:
                    if target == 6:
                        _inline_need(action.__code__ is ac and action.__globals__ is ns, 'RUNNER_SOURCE_BINDING')
                        action(original_owner, original_state[4][0])
                        _rl_checkpoint(original_owner, original_state[4][0] if original_state[4] else None)
                    m = invoke(target)
            else:
                key = (index, name, fromlist)
                _inline_need((name, fromlist) in _RL_STD[index] and key not in original_state[10], 'RUNNER_SOURCE_IMPORT')
                original_state[10].append(key)
                try:
                    m = original_owner[17](name, globals, locals, fromlist, level)
                finally:
                    _rl_checkpoint(original_owner, original_state[4][0] if original_state[4] else None)
            _rl_checkpoint(original_owner, original_state[4][0] if original_state[4] else None)
            _inline_need(type(m) is original_owner[9], 'RUNNER_SOURCE_IMPORT')
            md = _rl_namespace(m.__dict__)
            _inline_need(type(md.get('__name__')) is str and md['__name__'] == name and (fromlist is None or all((n in md for n in fromlist))), 'RUNNER_SOURCE_IMPORT')
            return m
        except B:
            original_state[2] = True
            raise
        finally:
            if reserved:
                if original_state[11] and original_state[11][-1] == index:
                    original_state[11].pop()
                else:
                    original_state[2] = True

    def input_handoff(io, entry):
        nonlocal io_record
        _inline_need(not st[3] and st[0] is False and (st[2] is False) and (type(io) is tuple) and (len(io) == 14) and (io[0] is ns) and (type(entry) is type(_rl_factory)) and (entry.__globals__ is ns), 'RUNNER_SOURCE_BINDING')
        _inline_need(io_record is None, 'RUNNER_SOURCE_BINDING')
        io_record = (io, entry, entry.__code__)
        st[3].append(io_record)

    def eof_handoff(io, frame, value):
        _inline_need(st[0] is True and st[1] is True and (st[2] is False) and (len(st[3]) == 1) and (io is st[3][0][0]) and (not st[4]) and (type(frame) is tuple) and (len(frame) == 4) and (type(value) is tuple) and (len(value) == 3), 'RUNNER_SOURCE_BINDING')
        st[4].append((value, frame))

    def entry():
        original_owner, original_state = o, st
        cache, namespaces = original_owner[11], _kernel[11]
        B, T, L, G, D, S, A, R, LI, TU, NAMES, I, M = (BaseException, type, len, dict.get, dict, str, all, reversed, list, tuple, _RL_OWN, int, original_owner[9])
        sources, parents = (original_state[5], original_state[14])
        if original_state[0] is not False or original_state[2] is not False or L(original_state[3]) != 1:
            original_state[2] = True
            return ('REJECTED_RUNNER_SOURCES', 'RUNNER_SOURCE_BINDING', None)
        original_state[0], original_state[1] = (True, True)
        result, issue = (None, 'RUNNER_SOURCE_REJECTED')
        try:
            io, f, c = original_state[3][0]
            if f.__code__ is not c or f.__globals__ is not ns:
                raise
            received = f()
            original_state[1] = False
            _inline_need(T(received) is tuple and L(received) == 3 and (received[:2] == ('RECEIVED_WORKER_INPUTS', 'NONE')) and (L(original_state[4]) == 1) and (received[2] is original_state[4][0][0]) and (original_state[2] is False), 'RUNNER_SOURCE_BINDING')
            invoke(0)
            _rl_checkpoint(original_owner, original_state[4][0] if original_state[4] else None)
            _inline_need(L(original_state[5]) == 8 and L(original_state[14]) == 2 and (not original_state[8]) and (not original_state[11]) and all((v[9] is True for v in original_state[5])) and all((v is True for v in original_state[9])), 'RUNNER_SOURCE_ORDER')
            result = (tuple(((v[3], v[4], original_state[6][0][1][v[1][0]], v[6], v[0]) for v in original_state[5])), tuple(((v[3], v[4], v[15]) for v in original_state[14])))
        except B:
            pass
        try:
            _rl_checkpoint(original_owner, original_state[4][0] if original_state[4] else None, diagnostic=True)
        except B:
            result, issue = (None, 'RUNNER_SOURCE_BINDING')
        if result is None:
            valid_cache = T(cache) is D and L(cache) <= 256 and A(T(k) is S and L(k) <= 4096 and '\x00' not in k for k in cache)
            valid_namespaces = T(namespaces) is LI and L(namespaces) <= 10
            if valid_namespaces:
                for captured in namespaces:
                    if T(captured) is not TU or L(captured) != 3 or T(captured[0]) is not I or captured[0] not in (0, 1, 5, 3, 4, 6, 7, 8, 9, 10) or T(captured[1]) is not M or T(captured[2]) is not D or L(captured[2]) > 256 or not A(T(k) is S and L(k) <= 4096 and '\x00' not in k for k in captured[2]):
                        valid_namespaces = False
                        break
            if valid_cache and valid_namespaces:
                for index, module, md in R(namespaces):
                    parent_index = 9 if index == 10 else 10 if 6 <= index <= 8 else None
                    key = NAMES[index].rsplit('.', 1)[1]
                    for parent_index_actual, parent_module, parent_namespace in namespaces:
                        if parent_index_actual == parent_index and G(parent_namespace, key) is module:
                            del parent_namespace[key]
                    name = NAMES[index]
                    if G(cache, name) is module:
                        del cache[name]
            if T(original_state) is LI and L(original_state) == 15:
                original_state[2] = True
            return ('REJECTED_RUNNER_SOURCES', issue, None)
        return ('EXECUTED_RUNNER_SOURCES', 'NONE', result)

    def call():
        original_state = st
        T, L, LS = T0, L0, LS0
        if T(_kernel) is not TT0 or L(_kernel) != 17:
            if T(original_state) is LS and L(original_state) == 15:
                original_state[2] = True
            return ('REJECTED_RUNNER_SOURCES', 'RUNNER_SOURCE_BINDING', None)
        try:
            _rl_checkpoint(o, None)
        except B:
            if T(original_state) is LS and L(original_state) == 15:
                original_state[2] = True
            return ('REJECTED_RUNNER_SOURCES', 'RUNNER_SOURCE_BINDING', None)
        return entry()
    return (entry, input_handoff, eof_handoff, Loader, gateway, invoke, call, bind_kernel, input_capture)

def _initialize_rl_control():
    global _RL_INITIALIZED, _RL_MARKER, _RL_CLASS, _RL_OWNER, _RL_GATE_FN
    global _rl_entry, _rl_input_handoff, _rl_eof_handoff, _rl_call, _rl_pre_snapshot
    global _RL_SEALER, _RL_D1_CARRIER, _RL_INPUT_CARRIER
    if _RL_INITIALIZED is not False:
        _RL_MARKER = None
        return ('REJECTED_RUNNER_CONTROL', 'RUNNER_SOURCE_BINDING')
    _RL_INITIALIZED = True
    try:
        _worker_profile_check(_WORKER_PROFILE_BINDING)
        ns, bi = (globals(), globals().get('__builtins__'))
        items = _worker_profile_items(_rl_namespace(bi), [0])
        compile_fn, exec_fn, import_fn = (bi.get('compile'), bi.get('exec'), bi.get('__import__'))
        fs = tuple((_worker_input_function(f, bi) for f in (compile_fn, exec_fn, import_fn)))
        _inline_need(all((type(f.__name__) is str and f.__name__ == n for f, n in zip((compile_fn, exec_fn, import_fn), ('compile', 'exec', '__import__')))), 'RUNNER_SOURCE_BINDING')
        cache = _rl_namespace(sys.__dict__.get('modules'))
        _RL_MARKER = object()
        st = [False, False, False, [], [], [], [], [], [], [False] * len(_RL_EDGES), [], [], [], [], []]
        slot, namespaces = [], []
        o = (ns, _RL_MARKER, st, bi, items, compile_fn, exec_fn, fs[0], fs[1], _SEMANTIC_CONTROL_ANCHOR[9], _rl_spec_state(_SEMANTIC_CONTROL_ANCHOR[4]), cache, _worker_input_run.__code__, (_rl_guard, _rl_guard.__code__), [], [], (_rl_binding, _rl_binding.__code__), import_fn, fs[2], (_rl_parent_binding, _rl_parent_binding.__code__), [], [], slot, tuple((st[i] for i in (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))))
        _RL_OWNER = o
        primitive = (type, len, type(_rl_gate_impl), dict, tuple, str, getattr, dict.get, dict.items, RuntimeError, list, zip, bool)
        T, L, FT, DT, TT, ST, GA, DG, DI, E, LS, Z, BT = primitive
        gate = FT(_rl_gate_impl.__code__, ns, '_rl_gate_impl', (o, (), primitive))
        early = (gate, gate.__code__, ns, gate.__defaults__, primitive)
        slot.append(early)
        _RL_GATE_FN = gate
        originals, ready = [], [False]
        kernel_context, record = None, None

        def carrier():
            return record

        def wrap(fn):
            originals.append(fn)
            def wrapped(*args, **kw):
                if '_guard' in kw or '_kernel' in kw or '_primitives' in kw:
                    raise E()
                return fn(*args, _guard=slot, _kernel=kernel_context, _primitives=primitive, **kw)
            return wrapped
        for name in ('_rl_make_pair', '_rl_parents', '_rl_run', '_rl_write', '_rl_execute', '_rl_factory'):
            ns[name] = wrap(ns[name])
        o[14].extend((_rl_write, _rl_write.__code__))
        o[15].extend((_rl_execute, _rl_execute.__code__))
        o[20].extend((_rl_parents, _rl_parents.__code__))
        o[21].extend((_rl_make_pair, _rl_make_pair.__code__))
        _rl_entry, _rl_input_handoff, _rl_eof_handoff, _RL_CLASS, gateway, invoke, _rl_call, binder, input_capture = _rl_factory(o)
        _RL_D1_CARRIER, _RL_INPUT_CARRIER = carrier, input_capture
        input_capture_code, input_capture_cells = input_capture.__code__, input_capture.__closure__
        method = _RL_CLASS.__dict__['exec_module']
        st[6].append((_RL_CLASS, tuple((_RL_CLASS() for _ in range(9))), method, method.__code__))
        st[7].append((gateway, gateway.__code__, _worker_profile_function(gateway, [0])))
        outer_fn, kernel_fn = _worker_report_check, _rl_kernel_check
        outer_saved = _worker_profile_function(outer_fn, [0])
        kernel_saved = _worker_profile_function(kernel_fn, [0])
        selected = tuple(v for k, v in _worker_profile_items(ns, [0]) if T(v) is FT and v is not gate and v is not carrier and v is not input_capture and v is not _rl_input_handoff)
        selected += tuple(originals) + (gateway, invoke, method, wrap, binder)
        before = tuple(_worker_profile_function(f, [0]) for f in selected)
        holder = st[3]

        def seal():
            nonlocal kernel_context, record
            if ready[0] is not False or record is not None or kernel_context is not None:
                raise E()
            ready[0] = True
            if T(slot) is not LS or L(slot) != 1 or slot[0] is not early:
                raise E()
            if gate.__code__ is not early[1] or gate.__globals__ is not early[2] or gate.__defaults__ is not early[3] or gate.__kwdefaults__ is not None or gate.__closure__ is not None:
                raise E()
            for saved in before:
                fn = saved[0]
                if T(fn) is not FT or fn.__code__ is not saved[1] or fn.__globals__ is not saved[2] or fn.__defaults__ is not saved[3] or fn.__kwdefaults__ is not saved[4] or fn.__closure__ is not saved[6] or GA(fn, '__annotate__', None) is not saved[8]:
                    raise E()
                kw = fn.__kwdefaults__
                if kw is not None:
                    if T(kw) is not DT or L(kw) != L(saved[5]):
                        raise E()
                    for key in kw:
                        if T(key) is not ST:
                            raise E()
                    for key, value in saved[5]:
                        if DG(kw, key) is not value:
                            raise E()
                if fn.__closure__ is not None:
                    for cell, value in Z(fn.__closure__, saved[7]):
                        if cell.cell_contents is not value:
                            raise E()
            if input_capture.__code__ is not input_capture_code or input_capture.__globals__ is not ns or input_capture.__defaults__ is not None or input_capture.__kwdefaults__ is not None or input_capture.__closure__ is not input_capture_cells:
                raise E()
            received = input_capture()
            if T(received) is not TT or L(received) != 3 or T(received[0]) is not TT or L(received[0]) != 14 or T(received[1]) is not FT or received[1].__code__ is not received[2] or received[1].__globals__ is not ns:
                raise E()
            if T(holder) is not LS or L(holder) != 1 or holder[0] is not received or st[3] is not holder:
                raise E()
            io, entry, code = received
            if io[0] is not ns or io[12] is not outer_fn or io[13] is not outer_saved[1] or T(io[2]) is not LS or L(io[2]) != 7:
                raise E()
            frame = None
            for name, cell in Z(entry.__code__.co_freevars, entry.__closure__):
                if name == 'frame':
                    frame = cell.cell_contents
            if T(frame) is not TT or L(frame) != 4:
                raise E()
            input_saved = _worker_profile_function(entry, [0])
            kernel_context = (primitive, outer_saved, ns, bi, items, received, input_saved, frame, st, slot, carrier, namespaces, kernel_saved, holder, io[2], 7, early)
            binder(kernel_context)
            pins = tuple(_worker_profile_function(saved[0], [0]) for saved in before) + (input_saved,)
            for saved, final in Z(before, pins):
                if not all(saved[i] is final[i] for i in (0, 1, 2, 3, 4, 6, 8)) or L(saved[5]) != L(final[5]) or L(saved[7]) != L(final[7]):
                    raise E()
                for name, old, new in Z(saved[1].co_freevars, saved[7], final[7]):
                    if old is not new and not (name in ('_kernel', 'kernel_context') and old is None and new is kernel_context):
                        raise E()
            gateway_final = next(final for saved, final in Z(before, pins) if saved[0] is gateway)
            st[7][0] = (gateway, gateway_final[1], gateway_final)
            defaults = (o, pins, primitive)
            gate.__defaults__ = defaults
            record = (early[0], early[1], early[2], defaults, early[4])
            slot[0] = record
            st[13].append(pins)
            if gate.__code__ is not early[1] or gate.__globals__ is not ns or gate.__defaults__ is not defaults or slot[0] is not record:
                raise E()
        _RL_SEALER = seal
        seal_saved = _worker_profile_function(seal, [0])

        def dispatch_seal():
            if ready[0] is not False:
                if T(st) is LS and L(st) == 15:
                    st[2] = True
                raise E()
            for mapping in (ns, bi):
                if T(mapping) is not DT or L(mapping) > 256:
                    raise E()
                for key in mapping:
                    if T(key) is not ST or L(key) > 4096 or '\x00' in key:
                        raise E()
            if L(bi) != L(items):
                raise E()
            for key, value in items:
                if DG(bi, key) is not value:
                    raise E()
            fn = seal_saved[0]
            if T(fn) is not FT or fn.__code__ is not seal_saved[1] or fn.__globals__ is not seal_saved[2] or fn.__defaults__ is not seal_saved[3] or fn.__kwdefaults__ is not seal_saved[4] or fn.__closure__ is not seal_saved[6] or GA(fn, '__annotate__', None) is not seal_saved[8]:
                raise E()
            for cell, value in Z(fn.__closure__, seal_saved[7]):
                if cell.cell_contents is not value:
                    raise E()
            try:
                fn()
            except BaseException:
                if T(st) is LS and L(st) == 15:
                    st[2] = True
                raise
        _rl_pre_snapshot = dispatch_seal
        return ('BOUND_RUNNER_CONTROL', 'NONE')
    except BaseException:
        _RL_MARKER = None
        return ('REJECTED_RUNNER_CONTROL', 'RUNNER_SOURCE_BINDING')

'''


_INLINE_SHARED_IO = r"""
def _rl_write(o, p, value, *, record, complete=False, _guard=None, _kernel=None, _primitives=()):
    _rl_checkpoint(o, p)
    _inline_need(o[2][2] is False and type(value) is bytes and 0 < len(value) <= 256,
                 'RUNNER_SOURCE_WRITE')
    slot = 1 if complete else 0
    _inline_need(type(complete) is bool and record[19][slot] == 0
        and record[20][slot] is None and (not complete or record[19][0] == 4), 'RUNNER_SOURCE_ORDER')
    record[20][slot], record[19][slot] = value, 1
    io = o[2][3][0][0]
    budget, writes = io[2], io[6]
    while record[16 + slot] < len(value):
        _rl_checkpoint(o, p)
        _inline_need(budget[3] < _WORKER_INPUT_IO_CAP
            and budget[5] + len(value) - record[16 + slot] <= 65536, 'RUNNER_SOURCE_LIMIT')
        budget[3] += 1
        record[19][slot] = 2
        try: count = writes(1, value[record[16 + slot]:])
        finally: _rl_checkpoint(o, p)
        _inline_need(type(count) is int and 0 < count <= len(value) - record[16 + slot], 'RUNNER_SOURCE_WRITE')
        budget[5] += count
        record[16 + slot] += count
        record[19][slot] = 4 if record[16 + slot] == len(value) else 3
    _rl_checkpoint(o, p)


def _rl_execute(o, p, module, *, _guard=None, _kernel=None, _primitives=()):
    _rl_checkpoint(o, p)
    _inline_need(o[2][2] is False, 'RUNNER_SOURCE_ORDER')
    v = o[2][8][-1]
    _inline_need(module is v[3] and v[6] is None and v[7] is None
        and v[11] is False and v[12] is True and v[13] is False, 'RUNNER_SOURCE_BINDING')
    v[13] = True
    try: code = o[5](v[0], v[5], 'exec', dont_inherit=True, optimize=0)
    finally: _rl_checkpoint(o, p)
    _inline_need(type(code) is type(_rl_execute.__code__) and type(code.co_filename) is str
        and code.co_filename == v[5], 'RUNNER_SOURCE_BINDING')
    v[6] = code
    try: o[6](code, module.__dict__)
    finally: _rl_checkpoint(o, p)
    _inline_need(v[6] is code and v[7] is None, 'RUNNER_SOURCE_BINDING')
    v[7] = code
"""

_CHECKPOINT = r"""
def _rl_checkpoint(o, p, _frame_kernel, _frame_primitives, _frame_record, *, diagnostic=False):
    _T, _L, _FT, _DT, _TT, _ST, _GA, _DG, _DI, _E, _LS, _Z, _BT = _frame_primitives
    if _T(_frame_kernel) is not _TT or _L(_frame_kernel) != 17 or _frame_kernel[0] is not _frame_primitives:
        raise _E()
    _kh = _frame_kernel[12]
    _kf = _kh[0]
    if (_T(_kf) is not _FT or _kf.__code__ is not _kh[1] or _kf.__globals__ is not _kh[2]
        or _kf.__defaults__ is not _kh[3] or _kf.__kwdefaults__ is not _kh[4]
        or _kf.__closure__ is not _kh[6] or _GA(_kf, '__annotate__', None) is not _kh[8]):
        raise _E()
    _kf(_frame_kernel)
    _current = _frame_kernel[10]()
    if _frame_record is None:
        _frame_record = _current
    elif _frame_record is not _current:
        raise _E()
    _slot, _early = _frame_kernel[9], _frame_kernel[16]
    if _T(_slot) is not _LS or _L(_slot) != 1 or _slot[0] is not _current:
        raise _E()
    if _T(_current) is not _TT or _L(_current) != 5:
        raise _E()
    _gf, _gc, _gn, _gd, _gp = _current
    if (_gf is not _early[0] or _gc is not _early[1] or _gn is not _early[2]
        or _gp is not _early[4] or _T(_gf) is not _FT or _gf.__code__ is not _gc
        or _gf.__globals__ is not _gn or _gf.__defaults__ is not _gd
        or _gf.__kwdefaults__ is not None or _gf.__closure__ is not None):
        raise _E()
    _gf(o, p)
    if not diagnostic and _frame_kernel[8][2] is not False:
        raise _E()
    return _frame_record
"""


def _expand_checkpoints(tree):
    # DEC-076: gemeinsamer vertrauenswürdiger Kontrollcode, kein Sandboxanker.
    class Bind(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            class Find(ast.NodeVisitor):
                found = False
                def visit_FunctionDef(self, inner):
                    pass
                def visit_Expr(self, inner):
                    if isinstance(inner.value, ast.Call) and isinstance(inner.value.func, ast.Name) and inner.value.func.id == '_rl_checkpoint':
                        self.found = True
                    self.generic_visit(inner)
            scan = Find()
            for statement in node.body:
                scan.visit(statement)
            node = self.generic_visit(node)
            if scan.found:
                node.body[:0] = ast.parse('_frame_kernel = _kernel\n_frame_primitives = _primitives\n_frame_record = None').body
            return node
        def visit_Expr(self, node):
            if (isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == '_rl_checkpoint'):
                keys = node.value.keywords
                base.base.inputs.base._need(len(node.value.args) == 2 and (not keys or
                    len(keys) == 1 and keys[0].arg == 'diagnostic' and
                    isinstance(keys[0].value, ast.Constant) and keys[0].value.value is True), 'TEMPLATE_FORM')
                call = ast.Call(func=ast.Name(id='_rl_checkpoint', ctx=ast.Load()),
                    args=node.value.args + [ast.Name(id=name, ctx=ast.Load()) for name in
                        ('_frame_kernel', '_frame_primitives', '_frame_record')], keywords=keys)
                return ast.Assign(targets=[ast.Name(id='_frame_record', ctx=ast.Store())], value=call)
            return self.generic_visit(node)
    result = Bind().visit(tree)
    result.body[-1:-1] = ast.parse(_CHECKPOINT).body
    return result


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
    for n in kept:
        if isinstance(n, ast.FunctionDef) and n.name == '_rl_main':
            n.body = ast.parse("result = _rl_call()\nif result[:2] != ('EXECUTED_RUNNER_SOURCES', 'NONE'): raise SystemExit(1)").body
    return kept + replacement


def _helpers():
    text = ast.unparse(ast.Module(body=base._helpers(), type_ignores=[]))
    nodes = ast.parse(text.replace("_hl_", "_rl_").replace("_HL_", "_RL_").replace("HARNESS", "RUNNER")).body
    guard = next(n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == "_rl_guard")
    class Sticky(ast.NodeTransformer):
        def visit_Compare(self, node):
            if ast.unparse(node) == 'state[2] is False':
                return ast.parse('type(state[2]) is bool', mode='eval').body
            return self.generic_visit(node)
    Sticky().visit(guard)
    guard.body[-1:] = ast.parse('''
_inline_need(all(name not in owner[11] for name in _RL_NAMES if name not in published), "RUNNER_SOURCE_BINDING")
_rl_original(owner[19], namespace)(owner, packet)
''').body
    own = {n.name: n for n in ast.parse(_INLINE_SHARED_IO).body if isinstance(n, ast.FunctionDef)}
    nodes = [own.get(n.name, n) if isinstance(n, ast.FunctionDef) else n for n in nodes]
    return nodes


# Externe Fixture-/Entrys bleiben unter ihren tatsächlichen Schnittstellennamen.
_PRESERVED = {"_worker_input_seal", "_worker_input_entry", "_worker_profile_state",
              "_inline_observe_selected_worker_profile", "_inline_kernel_check", "_worker_input_factory"}


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
    forbidden.add("owner")
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
    report_init = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_initialize_worker_report_control')
    hits = []
    class Seal(ast.NodeTransformer):
        def visit_Expr(self, node):
            if ast.unparse(node) == 'script.append(_worker_report_script())':
                hits.append(node)
                return [ast.parse('_rl_pre_snapshot()').body[0], node]
            return self.generic_visit(node)
    Seal().visit(report_init)
    inputs.base._need(len(hits) == 1, "TEMPLATE_FORM")
    parent = ast.Module(body=[], type_ignores=[])
    tree.body = [n for n in tree.body if n is not main] + _helpers() + _runner_nodes() + [main]
    tree = _expand_checkpoints(tree)
    tree = _shorten_globals(tree, parent)
    tree = base.base._compact_locals(_shorten_uniform_locals(tree, parent))
    text = inputs._compact_indentation(ast.unparse(ast.fix_missing_locations(tree)) + "\n")
    source = base.base._compact_token_gaps(_compact_raw_literal(text, profile_raw)).encode("utf-8", "strict")
    inputs.base._need(len(source) <= inputs.base.MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return inputs.base.BootstrapSource(source, profile_raw, logical_profile,
        hashlib.sha256(source).hexdigest(), hashlib.sha256(profile_raw).hexdigest(), len(source))
