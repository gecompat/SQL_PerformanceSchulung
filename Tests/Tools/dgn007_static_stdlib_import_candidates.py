"""Konservative Quelltextkandidaten, keine CPython-P11-Importinventur."""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import tarfile


ARCHIVE_SHA256 = "b5796915dc45ff745cfb4e990a7e7c93d6f546328a102ce31448d69ebc37575c"
ARCHIVE_ROOT = "Python-3.12.16/Lib/"
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_SOURCE_BYTES = 64 * 1024 * 1024
MAX_SOURCE_FILES = 2048
ROOTS = (
    "dataclasses", "hashlib", "importlib.machinery", "importlib.util", "json",
    "os", "struct", "sys", "sysconfig", "types", "zipimport", "zlib",
)


def _source_files(archive_path):
    path = Path(archive_path)
    with path.open("rb") as raw:
        archive_bytes = raw.read(MAX_ARCHIVE_BYTES + 1)
    if len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise ValueError("SOURCE_ARCHIVE_LIMIT")
    if hashlib.sha256(archive_bytes).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("SOURCE_ARCHIVE_MISMATCH")
    files = {}
    total = 0
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:xz") as source:
        for member in source:
            if not member.isfile() or not member.name.startswith(ARCHIVE_ROOT):
                continue
            relative = member.name[len(ARCHIVE_ROOT):]
            if not relative.endswith(".py"):
                continue
            if (not relative or "\\" in relative or relative.startswith("/")
                    or any(part in ("", ".", "..") for part in relative.split("/"))
                    or relative in files):
                raise ValueError("SOURCE_ARCHIVE_MEMBER")
            if len(files) >= MAX_SOURCE_FILES or member.size > MAX_SOURCE_BYTES - total:
                raise ValueError("SOURCE_ARCHIVE_LIMIT")
            stream = source.extractfile(member)
            if stream is None:
                raise ValueError("SOURCE_ARCHIVE_MEMBER")
            body = stream.read(member.size + 1)
            if len(body) != member.size:
                raise ValueError("SOURCE_ARCHIVE_MEMBER")
            total += len(body)
            files[relative] = body
    return files


def _module_path(module, files):
    relative = module.replace(".", "/")
    package = relative + "/__init__.py"
    return package if package in files else relative + ".py" if relative + ".py" in files else None


def _import_names(tree, module, path):
    package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                parts = package.split(".") if package else []
                keep = max(0, len(parts) - node.level + 1)
                base = ".".join(parts[:keep] + ([base] if base else []))
            if base:
                yield base
                for alias in node.names:
                    if alias.name != "*":
                        yield base + "." + alias.name


def _target_condition(node):
    """Resolve only fixed, side-effect-free target platform predicates."""
    target = {
        "sys.platform": "linux",
        "os.name": "posix",
        "sys.version_info": (3, 12, 16, "final", 0),
        "sys.implementation.name": "cpython",
    }

    def value(expr):
        if isinstance(expr, ast.Constant) and type(expr.value) in (str, int, bool, type(None)):
            return expr.value
        if isinstance(expr, ast.Tuple):
            items = [value(item) for item in expr.elts]
            return tuple(items) if all(item is not _UNKNOWN for item in items) else _UNKNOWN
        if isinstance(expr, ast.List):
            items = [value(item) for item in expr.elts]
            return list(items) if all(item is not _UNKNOWN for item in items) else _UNKNOWN
        if isinstance(expr, ast.Attribute):
            name = ast.unparse(expr)
            return target.get(name, _UNKNOWN)
        if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.Not):
            item = value(expr.operand)
            return not item if item is not _UNKNOWN else _UNKNOWN
        if isinstance(expr, ast.BoolOp):
            items = [value(item) for item in expr.values]
            if isinstance(expr.op, ast.And):
                return False if False in items else (all(items) if _UNKNOWN not in items else _UNKNOWN)
            if isinstance(expr.op, ast.Or):
                return True if True in items else (any(items) if _UNKNOWN not in items else _UNKNOWN)
        if isinstance(expr, ast.Compare):
            left = value(expr.left)
            rights = [value(item) for item in expr.comparators]
            if left is _UNKNOWN or any(item is _UNKNOWN for item in rights):
                return _UNKNOWN
            current = left
            try:
                for op, right in zip(expr.ops, rights):
                    if isinstance(op, ast.Eq):
                        matched = current == right
                    elif isinstance(op, ast.Is):
                        if (current is not None and type(current) is not bool
                                or right is not None and type(right) is not bool):
                            return _UNKNOWN
                        matched = current is right
                    elif isinstance(op, ast.NotEq):
                        matched = current != right
                    elif isinstance(op, ast.IsNot):
                        if (current is not None and type(current) is not bool
                                or right is not None and type(right) is not bool):
                            return _UNKNOWN
                        matched = current is not right
                    elif isinstance(op, ast.In):
                        matched = current in right
                    elif isinstance(op, ast.NotIn):
                        matched = current not in right
                    elif isinstance(op, ast.Lt):
                        matched = current < right
                    elif isinstance(op, ast.LtE):
                        matched = current <= right
                    elif isinstance(op, ast.Gt):
                        matched = current > right
                    elif isinstance(op, ast.GtE):
                        matched = current >= right
                    else:
                        return _UNKNOWN
                    if not matched:
                        return False
                    current = right
                return True
            except (TypeError, ValueError):
                return _UNKNOWN
        return _UNKNOWN

    result = value(node)
    return result if type(result) is bool else None


_UNKNOWN = object()


def _module_body_import_names(tree, module, path, target_platform=False, condition_stats=None):
    """Include module/class bodies, optionally pruning known target if-branches."""
    package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]

    def visit(node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return
        if isinstance(node, ast.ClassDef):
            for statement in node.body:
                yield from visit(statement)
            return
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
            return
        if isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                parts = package.split(".") if package else []
                keep = max(0, len(parts) - node.level + 1)
                base = ".".join(parts[:keep] + ([base] if base else []))
            if base:
                yield base
                for alias in node.names:
                    if alias.name != "*":
                        yield base + "." + alias.name
            return
        if target_platform and isinstance(node, ast.If):
            decision = _target_condition(node.test)
            if condition_stats is not None:
                key = "resolved" if decision is not None else "unknown"
                condition_stats[key] += 1
            selected = node.body if decision is True else node.orelse if decision is False else None
            if selected is not None:
                for statement in selected:
                    yield from visit(statement)
                return
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                yield from visit(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    yield from visit(statement)

    for statement in tree.body:
        yield from visit(statement)


def _candidate_closure(files, roots=ROOTS):
    if type(files) is not dict or type(roots) is not tuple:
        raise ValueError("SOURCE_INPUT_TYPE")
    if any(type(name) is not str for name in roots) or len(set(roots)) != len(roots):
        raise ValueError("SOURCE_ROOTS")
    reached = set()
    pending = list(roots)
    edges = 0
    while pending:
        module = pending.pop()
        if module in reached:
            continue
        path = _module_path(module, files)
        if path is None:
            continue
        reached.add(module)
        tree = ast.parse(files[path], filename=path)
        for name in _import_names(tree, module, path):
            parts = name.split(".")
            candidate = next(
                (".".join(parts[:index]) for index in range(len(parts), 0, -1)
                 if _module_path(".".join(parts[:index]), files) is not None),
                None,
            )
            if candidate is not None:
                edges += 1
                if candidate not in reached:
                    pending.append(candidate)
    rows = []
    for module in sorted(reached):
        path = _module_path(module, files)
        rows.append((module + "\t" + hashlib.sha256(files[path]).hexdigest() + "\n").encode("ascii"))
    return tuple(sorted(reached)), edges, hashlib.sha256(b"".join(rows)).hexdigest()


def _module_body_candidate_closure(files, roots=ROOTS):
    if type(files) is not dict or type(roots) is not tuple:
        raise ValueError("SOURCE_INPUT_TYPE")
    if any(type(name) is not str for name in roots) or len(set(roots)) != len(roots):
        raise ValueError("SOURCE_ROOTS")
    reached = set()
    pending = list(roots)
    edges = 0
    while pending:
        module = pending.pop()
        if module in reached:
            continue
        path = _module_path(module, files)
        if path is None:
            continue
        reached.add(module)
        tree = ast.parse(files[path], filename=path)
        for name in _module_body_import_names(tree, module, path):
            parts = name.split(".")
            candidate = next(
                (".".join(parts[:index]) for index in range(len(parts), 0, -1)
                 if _module_path(".".join(parts[:index]), files) is not None),
                None,
            )
            if candidate is not None:
                edges += 1
                if candidate not in reached:
                    pending.append(candidate)
    rows = []
    for module in sorted(reached):
        path = _module_path(module, files)
        rows.append((module + "\t" + hashlib.sha256(files[path]).hexdigest() + "\n").encode("ascii"))
    return tuple(sorted(reached)), edges, hashlib.sha256(b"".join(rows)).hexdigest()


def _target_platform_candidate_closure(files, roots=ROOTS):
    if type(files) is not dict or type(roots) is not tuple:
        raise ValueError("SOURCE_INPUT_TYPE")
    reached = set()
    pending = list(roots)
    edges = 0
    condition_stats = {"resolved": 0, "unknown": 0}
    while pending:
        module = pending.pop()
        if module in reached:
            continue
        path = _module_path(module, files)
        if path is None:
            continue
        reached.add(module)
        tree = ast.parse(files[path], filename=path)
        for name in _module_body_import_names(
                tree, module, path, target_platform=True, condition_stats=condition_stats):
            parts = name.split(".")
            candidate = next(
                (".".join(parts[:index]) for index in range(len(parts), 0, -1)
                 if _module_path(".".join(parts[:index]), files) is not None),
                None,
            )
            if candidate is not None:
                edges += 1
                if candidate not in reached:
                    pending.append(candidate)
    rows = []
    for module in sorted(reached):
        path = _module_path(module, files)
        rows.append((module + "\t" + hashlib.sha256(files[path]).hexdigest() + "\n").encode("ascii"))
    return tuple(sorted(reached)), edges, hashlib.sha256(b"".join(rows)).hexdigest(), condition_stats


def _module_init_call_import_names(tree, module, path, condition_stats=None):
    """Follow direct local function calls made by module/class initialization."""
    package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]
    postponed_annotations = any(
        isinstance(statement, ast.ImportFrom) and statement.module == "__future__"
        and any(alias.name == "annotations" for alias in statement.names)
        for statement in tree.body
    )
    def scope_functions(statements):
        result = {}

        def collect(node):
            if isinstance(node, ast.FunctionDef):
                result.setdefault(node.name, []).append(node)
                return
            if isinstance(node, (ast.AsyncFunctionDef, ast.ClassDef)):
                return
            if isinstance(node, ast.If):
                decision = _target_condition(node.test)
                selected = node.body if decision is True else node.orelse if decision is False else None
                for statement in selected if selected is not None else (*node.body, *node.orelse):
                    collect(statement)
                return
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.stmt):
                    collect(child)
                elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                    for statement in child.body:
                        collect(statement)

        for statement in statements:
            collect(statement)
        return result

    module_functions = scope_functions(tree.body)
    pending = []
    function_closures = {}

    def visit(node, active_functions, in_function=False, function_scope=None):
        if function_scope is None:
            function_scope = module_functions
        if isinstance(node, ast.Lambda):
            for expression in (*node.args.defaults, *node.args.kw_defaults):
                if expression is not None:
                    yield from visit(expression, active_functions, in_function, function_scope)
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_closures.setdefault(id(node), function_scope)
            expressions = [*node.decorator_list, *node.args.defaults, *node.args.kw_defaults]
            if not postponed_annotations:
                args = (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
                if node.args.vararg is not None:
                    args += (node.args.vararg,)
                if node.args.kwarg is not None:
                    args += (node.args.kwarg,)
                expressions.extend(arg.annotation for arg in args)
                expressions.append(node.returns)
            for expression in expressions:
                if expression is not None:
                    yield from visit(expression, active_functions, in_function, function_scope)
            return
        if isinstance(node, ast.ClassDef):
            class_functions = scope_functions(node.body)
            class_scope = dict(active_functions)
            class_scope.update(class_functions)
            for expression in (*node.decorator_list, *node.bases, *(kw.value for kw in node.keywords)):
                yield from visit(expression, active_functions, in_function, function_scope)
            for statement in node.body:
                yield from visit(statement, class_scope, False, function_scope)
            return
        if isinstance(node, ast.GeneratorExp):
            return
        if isinstance(node, ast.AnnAssign):
            yield from visit(node.target, active_functions, in_function, function_scope)
            if not postponed_annotations and not in_function:
                yield from visit(node.annotation, active_functions, in_function, function_scope)
            if node.value is not None:
                yield from visit(node.value, active_functions, in_function, function_scope)
            return
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
            return
        if isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                return
            base = node.module or ""
            if node.level:
                parts = package.split(".") if package else []
                keep = max(0, len(parts) - node.level + 1)
                base = ".".join(parts[:keep] + ([base] if base else []))
            if base:
                yield base
                for alias in node.names:
                    if alias.name != "*":
                        yield base + "." + alias.name
            return
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            for function in active_functions.get(node.func.id, ()):
                pending.append((function, function_closures.get(id(function), function_scope)))
        if isinstance(node, ast.If):
            decision = _target_condition(node.test)
            if condition_stats is not None:
                key = "resolved" if decision is not None else "unknown"
                condition_stats[key] += 1
            selected = node.body if decision is True else node.orelse if decision is False else None
            if selected is not None:
                for statement in selected:
                    yield from visit(statement, active_functions, in_function, function_scope)
                return
        for child in ast.iter_child_nodes(node):
            yield from visit(child, active_functions, in_function, function_scope)

    imports = []
    for statement in tree.body:
        imports.extend(visit(statement, module_functions))
    visited = set()
    while pending:
        function, closure_scope = pending.pop()
        if id(function) in visited:
            continue
        visited.add(id(function))
        visible_functions = dict(closure_scope)
        visible_functions.update(scope_functions(function.body))
        for statement in function.body:
            imports.extend(visit(statement, visible_functions, True, visible_functions))
    return tuple(imports), len(visited)


def _module_init_call_candidate_closure(files, roots=ROOTS):
    if type(files) is not dict or type(roots) is not tuple:
        raise ValueError("SOURCE_INPUT_TYPE")
    if any(type(name) is not str for name in roots) or len(set(roots)) != len(roots):
        raise ValueError("SOURCE_ROOTS")
    reached = set()
    pending = list(roots)
    edges = 0
    functions = 0
    conditions = {"resolved": 0, "unknown": 0}
    while pending:
        module = pending.pop()
        if module in reached:
            continue
        path = _module_path(module, files)
        if path is None:
            continue
        reached.add(module)
        tree = ast.parse(files[path], filename=path)
        names, visited_functions = _module_init_call_import_names(tree, module, path, conditions)
        functions += visited_functions
        for name in names:
            parts = name.split(".")
            candidate = next(
                (".".join(parts[:index]) for index in range(len(parts), 0, -1)
                 if _module_path(".".join(parts[:index]), files) is not None),
                None,
            )
            if candidate is not None:
                edges += 1
                if candidate not in reached:
                    pending.append(candidate)
    rows = []
    for module in sorted(reached):
        path = _module_path(module, files)
        rows.append((module + "\t" + hashlib.sha256(files[path]).hexdigest() + "\n").encode("ascii"))
    return tuple(sorted(reached)), edges, functions, hashlib.sha256(b"".join(rows)).hexdigest(), conditions


def analyze(archive_path):
    files = _source_files(archive_path)
    modules, edges, rows_sha256 = _candidate_closure(files)
    module_body, module_body_edges, module_body_sha256 = _module_body_candidate_closure(files)
    target_platform, target_edges, target_sha256, target_conditions = _target_platform_candidate_closure(files)
    call_modules, call_edges, call_functions, call_sha256, call_conditions = (
        _module_init_call_candidate_closure(files)
    )
    return {
        "archive_sha256": ARCHIVE_SHA256,
        "edge_count": edges,
        "module_count": len(modules),
        "module_rows_sha256": rows_sha256,
        "module_body_candidate_count": len(module_body),
        "module_body_edge_count": module_body_edges,
        "module_body_scope": "MODULE_AND_CLASS_BODIES_ONLY",
        "module_body_rows_sha256": module_body_sha256,
        "target_platform_candidate_count": len(target_platform),
        "target_platform_edge_count": target_edges,
        "target_platform_scope": "MODULE_CLASS_AND_KNOWN_LINUX_CPYTHON312_IF_BRANCHES",
        "target_platform_rows_sha256": target_sha256,
        "target_platform_resolved_if_count": target_conditions["resolved"],
        "target_platform_unknown_if_count": target_conditions["unknown"],
        "module_init_call_candidate_count": len(call_modules),
        "module_init_call_edge_count": call_edges,
        "module_init_call_function_count": call_functions,
        "module_init_call_scope": "MODULE_CLASS_AND_DIRECT_LOCAL_CALLS",
        "module_init_call_rows_sha256": call_sha256,
        "module_init_call_resolved_if_count": call_conditions["resolved"],
        "module_init_call_unknown_if_count": call_conditions["unknown"],
        "roots": list(ROOTS),
        "scope": "LEXICAL_SOURCE_CANDIDATES_ONLY",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="signaturgeprüftes CPython-3.12.16-Quellarchiv")
    args = parser.parse_args()
    try:
        result = analyze(args.archive)
    except (OSError, tarfile.TarError, UnicodeError, SyntaxError, ValueError):
        print(json.dumps({"status": "NOT_PROVEN", "issue": "SOURCE_INPUT_REJECTED"},
                         separators=(",", ":")))
        return 1
    print(json.dumps({"status": "CANDIDATES_ONLY", **result}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
