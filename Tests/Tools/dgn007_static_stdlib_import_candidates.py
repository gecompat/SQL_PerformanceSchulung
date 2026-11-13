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


_KNOWN_BUILTIN_NAMES = object()
# Bounded from the digest-pinned linux/amd64 CPython 3.12.16 config.c/Inittab.
_TARGET_BUILTIN_MEMBERSHIP = {"posix": True, "nt": False}


def _target_condition(node, known_names=None):
    """Resolve only fixed, side-effect-free target platform predicates."""
    target = {
        "sys.platform": "linux",
        "os.name": "posix",
        "sys.version_info": (3, 12, 16, "final", 0),
        "sys.implementation.name": "cpython",
        "sys.builtin_module_names": _KNOWN_BUILTIN_NAMES,
    }
    known_names = known_names or {}

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
        if isinstance(expr, ast.Name):
            return known_names.get(expr.id, _UNKNOWN)
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
                        if current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        matched = current == right
                    elif isinstance(op, ast.Is):
                        if current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        if (current is not None and type(current) is not bool
                                or right is not None and type(right) is not bool):
                            return _UNKNOWN
                        matched = current is right
                    elif isinstance(op, ast.NotEq):
                        if current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        matched = current != right
                    elif isinstance(op, ast.IsNot):
                        if current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        if (current is not None and type(current) is not bool
                                or right is not None and type(right) is not bool):
                            return _UNKNOWN
                        matched = current is not right
                    elif isinstance(op, ast.In):
                        if right is _KNOWN_BUILTIN_NAMES:
                            if type(current) is not str or current not in _TARGET_BUILTIN_MEMBERSHIP:
                                return _UNKNOWN
                            matched = _TARGET_BUILTIN_MEMBERSHIP[current]
                        else:
                            matched = current in right
                    elif isinstance(op, ast.NotIn):
                        if right is _KNOWN_BUILTIN_NAMES:
                            if type(current) is not str or current not in _TARGET_BUILTIN_MEMBERSHIP:
                                return _UNKNOWN
                            matched = not _TARGET_BUILTIN_MEMBERSHIP[current]
                        else:
                            matched = current not in right
                    elif isinstance(op, ast.Lt):
                        if current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        matched = current < right
                    elif isinstance(op, ast.LtE):
                        if current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        matched = current <= right
                    elif isinstance(op, ast.Gt):
                        if current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        matched = current > right
                    elif isinstance(op, ast.GtE):
                        if current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
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


def _target_name_aliases(tree):
    known = {}
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            value = statement.value
            mapped = (_KNOWN_BUILTIN_NAMES
                      if isinstance(value, ast.Attribute)
                      and ast.unparse(value) == "sys.builtin_module_names"
                      else known.get(value.id, _UNKNOWN) if isinstance(value, ast.Name) else _UNKNOWN)
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    if mapped is _UNKNOWN:
                        known.pop(target.id, None)
                    else:
                        known[target.id] = mapped
        elif isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            value = statement.value
            mapped = (_KNOWN_BUILTIN_NAMES
                      if isinstance(value, ast.Attribute)
                      and ast.unparse(value) == "sys.builtin_module_names"
                      else known.get(value.id, _UNKNOWN) if isinstance(value, ast.Name) else _UNKNOWN)
            if mapped is _UNKNOWN:
                known.pop(statement.target.id, None)
            else:
                known[statement.target.id] = mapped
    if not known:
        return known
    bindings = {}

    def bind(name):
        if type(name) is str:
            bindings[name] = bindings.get(name, 0) + 1

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            bind(node.id)
        elif isinstance(node, ast.arg):
            bind(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bind(node.name)
        elif isinstance(node, ast.alias):
            bind(node.asname or node.name.split(".")[0])
        elif isinstance(node, ast.ExceptHandler):
            bind(node.name)
        elif isinstance(node, ast.Global):
            for name in node.names:
                bind(name)
        elif isinstance(node, ast.Nonlocal):
            for name in node.names:
                bind(name)
        elif isinstance(node, ast.MatchAs):
            bind(node.name)
        elif isinstance(node, ast.MatchStar):
            bind(node.name)
        elif isinstance(node, ast.MatchMapping):
            bind(node.rest)
    return {name: value for name, value in known.items() if bindings.get(name) == 1}


def _module_body_import_names(
        tree, module, path, target_platform=False, condition_stats=None, known_names=None):
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
            if target_platform and known_names is not None and any(
                    alias.name == "*" for alias in node.names):
                known_names.clear()
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
            decision = _target_condition(node.test, known_names)
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
        aliases = _target_name_aliases(tree)
        for name in _module_body_import_names(
                tree, module, path, target_platform=True, condition_stats=condition_stats,
                known_names=aliases):
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


def _top_level_function_index(tree):
    result = {}

    def collect(node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result.setdefault(node.name, []).append(node)
            return
        if isinstance(node, ast.ClassDef):
            return
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                collect(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    collect(statement)

    for statement in tree.body:
        collect(statement)
    return result


def _top_level_class_method_index(tree):
    result = {}

    def collect_class(node):
        methods = {}

        def collect_member(member):
            if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.setdefault(member.name, []).append(member)
                return
            if isinstance(member, ast.ClassDef):
                return
            for child in ast.iter_child_nodes(member):
                if isinstance(child, ast.stmt):
                    collect_member(child)
                elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                    for statement in child.body:
                        collect_member(statement)

        for statement in node.body:
            collect_member(statement)
        known = result.setdefault(node.name, {})
        for method_name, functions in methods.items():
            existing = known.setdefault(method_name, [])
            existing_ids = {id(function) for function in existing}
            for function in functions:
                if id(function) not in existing_ids:
                    existing.append(function)
                    existing_ids.add(id(function))

    def collect(node):
        if isinstance(node, ast.ClassDef):
            collect_class(node)
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                collect(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    collect(statement)

    for statement in tree.body:
        collect(statement)
    return result


def _top_level_class_base_index(tree):
    """Keep direct local base names for bounded zero-argument super() calls."""
    result = {}

    def collect(node):
        if isinstance(node, ast.ClassDef):
            bases = result.setdefault(node.name, [])
            for base in node.bases:
                if isinstance(base, (ast.Name, ast.Attribute)):
                    base_name = ast.unparse(base)
                    if base_name not in bases:
                        bases.append(base_name)
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            return
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                collect(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    collect(statement)

    for statement in tree.body:
        collect(statement)
    return {name: tuple(bases) for name, bases in result.items()}


def _has_possible_staticmethod_rebinding(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "staticmethod" \
                and not isinstance(node.ctx, ast.Load):
            return True
        if isinstance(node, ast.arg) and node.arg == "staticmethod":
            return True
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                and node.name == "staticmethod":
            return True
        if isinstance(node, ast.ExceptHandler) and node.name == "staticmethod":
            return True
        if isinstance(node, (ast.Global, ast.Nonlocal)) and "staticmethod" in node.names:
            return True
        if isinstance(node, ast.Import) and any(
                (alias.asname or alias.name.partition(".")[0]) == "staticmethod"
                for alias in node.names):
            return True
        if isinstance(node, ast.ImportFrom):
            if any(alias.name == "*" or (alias.asname or alias.name) == "staticmethod"
                   for alias in node.names):
                return True
        if isinstance(node, ast.MatchAs) and node.name == "staticmethod":
            return True
        if isinstance(node, ast.MatchStar) and node.name == "staticmethod":
            return True
        if isinstance(node, ast.MatchMapping) and node.rest == "staticmethod":
            return True
    return False


def _imported_function_aliases(tree, module, path, function_index):
    package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]
    result = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.module == "__future__":
            continue
        base = node.module or ""
        if node.level:
            parts = package.split(".") if package else []
            keep = max(0, len(parts) - node.level + 1)
            base = ".".join(parts[:keep] + ([base] if base else []))
        if not base:
            continue
        for imported in node.names:
            if imported.name == "*" or imported.name not in function_index.get(base, {}):
                continue
            alias = imported.asname or imported.name
            targets = result.setdefault(alias, [])
            target = (base, imported.name)
            if target not in targets:
                targets.append(target)
    return {name: tuple(dict.fromkeys(targets)) for name, targets in result.items()}


def _imported_class_aliases(tree, module, path, class_index):
    package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]
    result = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.module == "__future__":
            continue
        base = node.module or ""
        if node.level:
            parts = package.split(".") if package else []
            keep = max(0, len(parts) - node.level + 1)
            base = ".".join(parts[:keep] + ([base] if base else []))
        for imported in node.names:
            if imported.name not in class_index.get(base, {}):
                continue
            alias = imported.asname or imported.name
            target = (base, imported.name)
            targets = result.setdefault(alias, [])
            if target not in targets:
                targets.append(target)
    return {name: tuple(targets) for name, targets in result.items()}


def _imported_module_aliases(tree, module, path, module_index):
    result = {}

    def add(expression, target_module):
        if not expression or target_module not in module_index:
            return
        targets = result.setdefault(expression, [])
        if target_module not in targets:
            targets.append(target_module)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for imported in node.names:
                if imported.asname:
                    add(imported.asname, imported.name)
                else:
                    add(imported.name, imported.name)
                    root = imported.name.partition(".")[0]
                    if root != imported.name:
                        add(root, root)
        elif isinstance(node, ast.ImportFrom) and node.module != "__future__":
            package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]
            base = node.module or ""
            if node.level:
                parts = package.split(".") if package else []
                keep = max(0, len(parts) - node.level + 1)
                base = ".".join(parts[:keep] + ([base] if base else []))
            for imported in node.names:
                if imported.name == "*":
                    continue
                target_module = base + ("." if base else "") + imported.name
                add(imported.asname or imported.name, target_module)
    return {expression: tuple(targets) for expression, targets in result.items()}


def _imported_module_function_aliases(module_aliases, function_index, class_index):
    result = {}
    for expression, imported_modules in module_aliases.items():
        aliases = result.setdefault(expression, {})
        for module in imported_modules:
            for function_name in function_index.get(module, {}):
                target = (module, function_name)
                targets = aliases.setdefault(function_name, [])
                if target not in targets:
                    targets.append(target)
            for class_name, methods in class_index.get(module, {}).items():
                if "__init__" not in methods:
                    continue
                target = (module, class_name + ".__init__")
                targets = aliases.setdefault(class_name, [])
                if target not in targets:
                    targets.append(target)
    return {expression: {name: tuple(targets) for name, targets in functions.items()}
            for expression, functions in result.items()}


def _imported_module_class_method_aliases(module_aliases, class_index):
    result = {}

    for expression, imported_modules in module_aliases.items():
        for module in imported_modules:
            for class_name, methods in class_index.get(module, {}).items():
                receiver = expression + "." + class_name
                aliases = result.setdefault(receiver, {})
                for method_name in methods:
                    target = (module, class_name + "." + method_name)
                    targets = aliases.setdefault(method_name, [])
                    if target not in targets:
                        targets.append(target)
    return {expression: {name: tuple(targets) for name, targets in methods.items()}
            for expression, methods in result.items()}


def _module_init_call_import_names(tree, module, path, condition_stats=None,
                                   imported_functions=None, imported_modules=None,
                                   imported_class_methods=None,
                                   imported_module_class_methods=None,
                                   entry_functions=(),
                                   run_module=True, visited_global=None):
    """Follow direct and simply aliased local calls from initialization."""
    package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]
    postponed_annotations = any(
        isinstance(statement, ast.ImportFrom) and statement.module == "__future__"
        and any(alias.name == "annotations" for alias in statement.names)
        for statement in tree.body
    )
    known_names = _target_name_aliases(tree)
    def scope_functions(statements):
        result = {}
        conditions = dict(known_names)

        def collect(node):
            if isinstance(node, ast.FunctionDef):
                result.setdefault(node.name, []).append(node)
                return
            if isinstance(node, (ast.AsyncFunctionDef, ast.ClassDef)):
                return
            if isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names):
                conditions.clear()
                return
            if isinstance(node, ast.If):
                decision = _target_condition(node.test, conditions)
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

    def scope_function_aliases(statements, functions):
        """Conservatively add simple same-scope ``alias = function`` names."""
        result = {name: list(nodes) for name, nodes in functions.items()}
        conditions = dict(known_names)

        def add_alias(node):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                return
            if isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names):
                conditions.clear()
                return
            if isinstance(node, ast.If):
                decision = _target_condition(node.test, conditions)
                selected = node.body if decision is True else node.orelse if decision is False else None
                for statement in selected if selected is not None else (*node.body, *node.orelse):
                    add_alias(statement)
                return
            value = node.value if isinstance(node, (ast.Assign, ast.AnnAssign)) else None
            targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
            if isinstance(value, ast.Name) and value.id in result:
                for target in targets:
                    if isinstance(target, ast.Name):
                        known = result.setdefault(target.id, [])
                        known_ids = {id(function) for function in known}
                        known.extend(function for function in result[value.id]
                                     if id(function) not in known_ids)
                        known_ids.update(id(function) for function in known)
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.stmt):
                    add_alias(child)
                elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                    for statement in child.body:
                        add_alias(statement)

        for statement in statements:
            add_alias(statement)
        return result

    def class_scope_functions(statements, outer_functions):
        """Resolve class-body function aliases against ordered class bindings."""
        result = {name: list(nodes) for name, nodes in outer_functions.items()}
        conditions = dict(known_names)

        def copy_scope(scope):
            return {name: list(nodes) for name, nodes in scope.items()}

        def merge_scopes(left, right):
            merged = {}
            for name in left.keys() | right.keys():
                nodes = []
                seen = set()
                for node in (*left.get(name, []), *right.get(name, [])):
                    if id(node) not in seen:
                        seen.add(id(node))
                        nodes.append(node)
                merged[name] = nodes
            return merged

        def bind(node, scope, facts):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                scope[node.name] = [node]
                return
            if isinstance(node, ast.ClassDef):
                return
            if isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names):
                facts.clear()
                return
            if isinstance(node, ast.If):
                decision = _target_condition(node.test, facts)
                selected = node.body if decision is True else node.orelse if decision is False else None
                if selected is not None:
                    for statement in selected:
                        bind(statement, scope, facts)
                else:
                    left, right = copy_scope(scope), copy_scope(scope)
                    left_facts, right_facts = dict(facts), dict(facts)
                    for statement in node.body:
                        bind(statement, left, left_facts)
                    for statement in node.orelse:
                        bind(statement, right, right_facts)
                    scope.clear()
                    scope.update(merge_scopes(left, right))
                    facts.clear()
                    facts.update({name: value for name, value in left_facts.items()
                                  if right_facts.get(name, _UNKNOWN) == value})
                return
            value = node.value if isinstance(node, (ast.Assign, ast.AnnAssign)) else None
            targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
            if isinstance(value, ast.Name) and value.id in scope:
                for target in targets:
                    if isinstance(target, ast.Name):
                        scope[target.id] = list(scope[value.id])
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.stmt):
                    bind(child, scope, facts)
                elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                    for statement in child.body:
                        bind(statement, scope, facts)

        for statement in statements:
            bind(statement, result, conditions)
        return result

    def scope_class_methods(statements):
        """Index methods declared by local classes, preserving alternatives."""
        result = {}
        conditions = dict(known_names)

        def collect_class(node):
            methods = {}

            def collect_member(member):
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.setdefault(member.name, []).append(member)
                    return
                if isinstance(member, ast.ClassDef):
                    return
                if isinstance(member, ast.ImportFrom) and any(alias.name == "*" for alias in member.names):
                    conditions.clear()
                    return
                if isinstance(member, ast.If):
                    decision = _target_condition(member.test, conditions)
                    selected = member.body if decision is True else member.orelse if decision is False else None
                    for statement in selected if selected is not None else (*member.body, *member.orelse):
                        collect_member(statement)
                    return
                for child in ast.iter_child_nodes(member):
                    if isinstance(child, ast.stmt):
                        collect_member(child)
                    elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                        for statement in child.body:
                            collect_member(statement)

            for statement in node.body:
                collect_member(statement)
            known = result.setdefault(node.name, {})
            for method_name, functions in methods.items():
                existing = known.setdefault(method_name, [])
                existing_ids = {id(function) for function in existing}
                for function in functions:
                    if id(function) not in existing_ids:
                        existing.append(function)
                        existing_ids.add(id(function))

        def collect(node):
            if isinstance(node, ast.ClassDef):
                collect_class(node)
                return
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return
            if isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names):
                conditions.clear()
                return
            if isinstance(node, ast.If):
                decision = _target_condition(node.test, conditions)
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

    module_functions = scope_function_aliases(tree.body, scope_functions(tree.body))
    module_class_methods = scope_class_methods(tree.body)
    module_class_bases = _top_level_class_base_index(tree)

    def local_base_classes(class_name):
        """Return known local ancestors without imposing a linear MRO order."""
        pending_bases = list(module_class_bases.get(class_name, ()))
        seen = set()
        ancestors = []
        while pending_bases:
            base_name = pending_bases.pop()
            if base_name in seen:
                continue
            seen.add(base_name)
            ancestors.append(base_name)
            pending_bases.extend(module_class_bases.get(base_name, ()))
        return tuple(ancestors)

    def add_base_method_calls(class_name, method_name, function_scope):
        for base_name in local_base_classes(class_name):
            for function in module_class_methods.get(base_name, {}).get(method_name, ()):
                pending.append((function, function_closures.get(id(function), function_scope)))
            imported_targets = (imported_class_methods or {}).get(base_name, {}).get(
                method_name, ()
            )
            imported_module_targets = (imported_module_class_methods or {}).get(
                base_name, {}
            ).get(method_name, ())
            imported_calls.update(imported_targets)
            imported_calls.update(imported_module_targets)

    staticmethod_rebinding_possible = _has_possible_staticmethod_rebinding(tree)
    method_receiver_context = {}
    for class_name, methods in module_class_methods.items():
        for functions in methods.values():
            for function in functions:
                decorators = {decorator.id for decorator in function.decorator_list
                              if isinstance(decorator, ast.Name)}
                if "staticmethod" in decorators and not staticmethod_rebinding_possible:
                    continue
                positional = (*function.args.posonlyargs, *function.args.args)
                if positional:
                    method_receiver_context[id(function)] = (class_name, positional[0].arg)

    def constructed_instance_methods(statements):
        """Resolve only same-scope names assigned a direct known class call."""
        result = {}

        def bind_constructor(target_name, constructor):
            if isinstance(constructor, ast.Name):
                local_methods = module_class_methods.get(constructor.id, {})
                imported_methods = (imported_class_methods or {}).get(constructor.id, {})
            elif isinstance(constructor, ast.Attribute):
                receiver = ast.unparse(constructor.value) + "." + constructor.attr
                local_methods = {}
                imported_methods = (imported_module_class_methods or {}).get(receiver, {})
            else:
                return
            bound = result.setdefault(target_name, {})
            for method_name, functions in local_methods.items():
                local = bound.setdefault(method_name, {"local": [], "imported": []})["local"]
                for function in functions:
                    if function not in local:
                        local.append(function)
            for method_name, targets in imported_methods.items():
                external = bound.setdefault(method_name, {"local": [], "imported": []})["imported"]
                for target in targets:
                    if target not in external:
                        external.append(target)

        def bind_alias(target_name, source_name):
            source = result.get(source_name)
            if source is None:
                return
            target = result.setdefault(target_name, {})
            for method_name, entries in source.items():
                bound = target.setdefault(method_name, {"local": [], "imported": []})
                for kind in ("local", "imported"):
                    for entry in entries[kind]:
                        if entry not in bound[kind]:
                            bound[kind].append(entry)

        def collect(node):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                return
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if not isinstance(target, ast.Name):
                        continue
                    if isinstance(value, ast.Call):
                        bind_constructor(target.id, value.func)
                    elif isinstance(value, ast.Name):
                        bind_alias(target.id, value.id)
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.stmt):
                    collect(child)
                elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                    for statement in child.body:
                        collect(statement)

        for statement in statements:
            collect(statement)
        return result

    active_instance_methods = constructed_instance_methods(tree.body)
    active_method_context = None
    pending = []
    imported_calls = set()
    function_closures = {}

    def captures_method_receiver(function, receiver):
        args = (*function.args.posonlyargs, *function.args.args, *function.args.kwonlyargs)
        if (any(arg.arg == receiver for arg in args)
                or (function.args.vararg is not None and function.args.vararg.arg == receiver)
                or (function.args.kwarg is not None and function.args.kwarg.arg == receiver)):
            return False
        has_load = False
        has_local_binding = False

        def scan(node, root=False):
            nonlocal has_load, has_local_binding
            if not root and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                              ast.ClassDef, ast.Lambda)):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                        and node.name == receiver:
                    has_local_binding = True
                return
            if isinstance(node, ast.Name) and node.id == receiver:
                if isinstance(node.ctx, ast.Load):
                    has_load = True
                else:
                    has_local_binding = True
            elif isinstance(node, ast.Import):
                if any((alias.asname or alias.name.partition(".")[0]) == receiver
                       for alias in node.names):
                    has_local_binding = True
            elif isinstance(node, ast.ImportFrom):
                if any((alias.asname or alias.name) == receiver for alias in node.names):
                    has_local_binding = True
            elif isinstance(node, ast.ExceptHandler) and node.name == receiver:
                has_local_binding = True
            elif isinstance(node, (ast.Global, ast.Nonlocal)) and receiver in node.names:
                has_local_binding = True
            for child in ast.iter_child_nodes(node):
                scan(child)

        scan(function, root=True)
        return has_load and not has_local_binding

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
            if (active_method_context is not None
                    and captures_method_receiver(node, active_method_context[1])):
                method_receiver_context.setdefault(id(node), active_method_context)
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
            class_scope = class_scope_functions(node.body, active_functions)
            for expression in (*node.decorator_list, *node.bases, *(kw.value for kw in node.keywords)):
                yield from visit(expression, active_functions, in_function, function_scope)
            for statement in node.body:
                yield from visit(statement, class_scope, False, function_scope)
            return
        if isinstance(node, ast.GeneratorExp):
            # A generator may be consumed during initialization (for example
            # by tuple(), any(), or a constructor). Keep every local call in
            # its lazy body as a candidate; proving consumption is outside
            # this bounded source analysis.
            for generator in node.generators:
                yield from visit(generator.iter, active_functions, in_function, function_scope)
                yield from visit(generator.target, active_functions, in_function, function_scope)
                for condition in generator.ifs:
                    yield from visit(condition, active_functions, in_function, function_scope)
            yield from visit(node.elt, active_functions, in_function, function_scope)
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
            if any(alias.name == "*" for alias in node.names):
                known_names.clear()
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
            for function in module_class_methods.get(node.func.id, {}).get("__init__", ()):
                pending.append((function, function_closures.get(id(function), function_scope)))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if (isinstance(node.func.value, ast.Call)
                    and isinstance(node.func.value.func, ast.Name)
                    and node.func.value.func.id == "super"
                    and not node.func.value.keywords
                    and active_method_context is not None):
                class_name = active_method_context[0]
                receiver_name = active_method_context[1]
                super_args = node.func.value.args
                valid_super = not super_args or (
                    len(super_args) == 2
                    and isinstance(super_args[0], ast.Name)
                    and super_args[0].id == class_name
                    and isinstance(super_args[1], ast.Name)
                    and super_args[1].id == receiver_name
                )
                if valid_super:
                    add_base_method_calls(class_name, node.func.attr, function_scope)
            if isinstance(node.func.value, ast.Call):
                constructor = node.func.value.func
                if isinstance(constructor, ast.Name):
                    for function in module_class_methods.get(constructor.id, {}).get(node.func.attr, ()):
                        pending.append((function, function_closures.get(id(function), function_scope)))
                    imported_targets = (imported_class_methods or {}).get(
                        constructor.id, {}
                    ).get(node.func.attr, ())
                    imported_calls.update(imported_targets)
                elif isinstance(constructor, ast.Attribute):
                    receiver = ast.unparse(constructor.value) + "." + constructor.attr
                    imported_targets = (imported_module_class_methods or {}).get(
                        receiver, {}
                    ).get(node.func.attr, ())
                    imported_calls.update(imported_targets)
            if isinstance(node.func.value, ast.Name):
                if (active_method_context is not None
                        and node.func.value.id == active_method_context[1]):
                    class_name = active_method_context[0]
                    for function in module_class_methods.get(class_name, {}).get(node.func.attr, ()):
                        pending.append((function, function_closures.get(id(function), function_scope)))
                    add_base_method_calls(class_name, node.func.attr, function_scope)
                instance_targets = active_instance_methods.get(node.func.value.id, {}).get(
                    node.func.attr, {"local": (), "imported": ()}
                )
                for function in instance_targets["local"]:
                    pending.append((function, function_closures.get(id(function), function_scope)))
                imported_calls.update(instance_targets["imported"])
                methods = module_class_methods.get(node.func.value.id, {})
                for function in methods.get(node.func.attr, ()):
                    pending.append((function, function_closures.get(id(function), function_scope)))
            receiver = ast.unparse(node.func.value)
            imported_targets = (imported_modules or {}).get(receiver, {}).get(node.func.attr, ())
            imported_calls.update(imported_targets)
            class_targets = (imported_class_methods or {}).get(receiver, {}).get(node.func.attr, ())
            imported_calls.update(class_targets)
            module_class_targets = (imported_module_class_methods or {}).get(receiver, {}).get(node.func.attr, ())
            imported_calls.update(module_class_targets)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            imported_calls.update((target_module, target_function)
                                  for target_module, target_function
                                  in (imported_functions or {}).get(node.func.id, ()))
        if isinstance(node, ast.If):
            decision = _target_condition(node.test, known_names)
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
    if run_module:
        for statement in tree.body:
            imports.extend(visit(statement, module_functions))
    else:
        for name in entry_functions:
            if "." in name:
                class_name, method_name = name.split(".", 1)
                candidates = module_class_methods.get(class_name, {}).get(method_name, ())
            else:
                candidates = module_functions.get(name, ())
            for function in candidates:
                function_closures.setdefault(id(function), module_functions)
                pending.append((function, module_functions))
    visited = visited_global if visited_global is not None else set()
    visited_before = len(visited)
    while pending:
        function, closure_scope = pending.pop()
        if id(function) in visited:
            continue
        visited.add(id(function))
        active_instance_methods = constructed_instance_methods(function.body)
        active_method_context = method_receiver_context.get(id(function))
        visible_functions = dict(closure_scope)
        visible_functions.update(scope_functions(function.body))
        visible_functions = scope_function_aliases(function.body, visible_functions)
        for statement in function.body:
            imports.extend(visit(statement, visible_functions, True, visible_functions))
    return tuple(imports), len(visited) - visited_before, tuple(sorted(imported_calls))


def _module_init_call_candidate_closure(files, roots=ROOTS):
    if type(files) is not dict or type(roots) is not tuple:
        raise ValueError("SOURCE_INPUT_TYPE")
    if any(type(name) is not str for name in roots) or len(set(roots)) != len(roots):
        raise ValueError("SOURCE_ROOTS")
    lexical_modules, _, _ = _candidate_closure(files, roots)
    module_sources = {}
    function_index = {}
    class_index = {}
    for source_module in lexical_modules:
        source_path = _module_path(source_module, files)
        if source_path is None:
            continue
        source_tree = ast.parse(files[source_path], filename=source_path)
        module_sources[source_module] = (source_path, source_tree)
        function_index[source_module] = _top_level_function_index(source_tree)
        class_index[source_module] = _top_level_class_method_index(source_tree)

    reached = set()
    initialized = set()
    processed_entries = set()
    pending = [(module, None) for module in roots]
    edges = 0
    functions = 0
    conditions = {"resolved": 0, "unknown": 0}
    visited_functions = set()
    while pending:
        module, entry_function = pending.pop()
        source = module_sources.get(module)
        if source is None:
            continue
        path, tree = source
        if entry_function is None:
            if module in initialized:
                continue
            initialized.add(module)
            reached.add(module)
            run_module = True
            entries = ()
        else:
            entry = (module, entry_function)
            if entry in processed_entries:
                continue
            if module not in initialized:
                pending.append((module, entry_function))
                pending.append((module, None))
                continue
            processed_entries.add(entry)
            run_module = False
            entries = (entry_function,)
        imported_functions = _imported_function_aliases(tree, module, path, function_index)
        imported_classes = _imported_class_aliases(tree, module, path, class_index)
        for alias, targets in imported_classes.items():
            for target_module, class_name in targets:
                if "__init__" in class_index.get(target_module, {}).get(class_name, {}):
                    existing = list(imported_functions.get(alias, ()))
                    target = (target_module, class_name + ".__init__")
                    if target not in existing:
                        existing.append(target)
                    imported_functions[alias] = tuple(existing)
        imported_class_methods = {}
        for alias, targets in imported_classes.items():
            methods = imported_class_methods.setdefault(alias, {})
            for target_module, class_name in targets:
                for method_name in class_index.get(target_module, {}).get(class_name, {}):
                    target = (target_module, class_name + "." + method_name)
                    entries = methods.setdefault(method_name, [])
                    if target not in entries:
                        entries.append(target)
        imported_class_methods = {
            alias: {name: tuple(targets) for name, targets in methods.items()}
            for alias, methods in imported_class_methods.items()
        }
        module_aliases = _imported_module_aliases(tree, module, path, function_index)
        imported_modules = _imported_module_function_aliases(
            module_aliases, function_index, class_index
        )
        imported_module_class_methods = _imported_module_class_method_aliases(
            module_aliases, class_index
        )
        names, visited_count, imported_calls = _module_init_call_import_names(
            tree, module, path, conditions,
            imported_functions=imported_functions,
            imported_modules=imported_modules,
            imported_class_methods=imported_class_methods,
            imported_module_class_methods=imported_module_class_methods,
            entry_functions=entries,
            run_module=run_module,
            visited_global=visited_functions,
        )
        functions += visited_count
        for name in names:
            parts = name.split(".")
            candidate = next(
                (".".join(parts[:index]) for index in range(len(parts), 0, -1)
                 if ".".join(parts[:index]) in module_sources),
                None,
            )
            if candidate is not None:
                edges += 1
                if candidate not in initialized:
                    pending.append((candidate, None))
        for target_module, target_function in imported_calls:
            is_function = target_function in function_index.get(target_module, {})
            class_name, separator, method_name = target_function.partition(".")
            is_method = bool(separator) and method_name in class_index.get(target_module, {}).get(class_name, {})
            if is_function or is_method:
                if target_module not in initialized:
                    pending.append((target_module, target_function))
                    pending.append((target_module, None))
                else:
                    pending.append((target_module, target_function))
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
        "target_platform_scope": "MODULE_CLASS_AND_KNOWN_LINUX_CPYTHON312_IF_AND_BUILTIN_BRANCHES",
        "target_platform_rows_sha256": target_sha256,
        "target_platform_resolved_if_count": target_conditions["resolved"],
        "target_platform_unknown_if_count": target_conditions["unknown"],
        "target_platform_builtin_membership": _TARGET_BUILTIN_MEMBERSHIP,
        "module_init_call_candidate_count": len(call_modules),
        "module_init_call_edge_count": call_edges,
        "module_init_call_function_count": call_functions,
        "module_init_call_scope": "MODULE_CLASS_CALLS_SIMPLE_ALIASES_GENERATORS_IMPORTED_FUNCTIONS_MODULE_ALIASES_FROM_IMPORT_IMPORTED_CLASS_METHODS_DIRECT_CONSTRUCTED_METHODS_SAME_SCOPE_INSTANCE_BINDINGS_INSTANCE_ALIASES_BOUND_RECEIVER_METHODS_NESTED_RECEIVER_CLOSURES_INHERITED_RECEIVER_METHODS_AND_TRANSITIVE_LOCAL_BASES_AND_IMPORTED_SOURCE_BASES_AND_ZERO_ARG_AND_EXPLICIT_LOCAL_SUPER_METHODS",
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
