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


def _module_body_import_names(tree, module, path):
    """Include module/class execution bodies, but not uncalled function bodies."""
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


def analyze(archive_path):
    files = _source_files(archive_path)
    modules, edges, rows_sha256 = _candidate_closure(files)
    module_body, module_body_edges, module_body_sha256 = _module_body_candidate_closure(files)
    return {
        "archive_sha256": ARCHIVE_SHA256,
        "edge_count": edges,
        "module_count": len(modules),
        "module_rows_sha256": rows_sha256,
        "module_body_candidate_count": len(module_body),
        "module_body_edge_count": module_body_edges,
        "module_body_scope": "MODULE_AND_CLASS_BODIES_ONLY",
        "module_body_rows_sha256": module_body_sha256,
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
