"""Konservative Quelltextkandidaten, keine CPython-P11-Importinventur."""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile


ARCHIVE_SHA256 = "b5796915dc45ff745cfb4e990a7e7c93d6f546328a102ce31448d69ebc37575c"
ARCHIVE_ROOT = "Python-3.12.16/Lib/"
STDLIB_MODULE_NAMES_MEMBER = "Python-3.12.16/Python/stdlib_module_names.h"
STDLIB_MODULE_NAMES_SHA256 = "450581463358b2ffaeca45b261c2e59a41cd6546b487445ed5ff9e0a2b4163a6"
FROZEN_SOURCE_MEMBER = "Python-3.12.16/Python/frozen.c"
FROZEN_SOURCE_SHA256 = "ff2d5e301f1725c013788f30882fd48127a9ecfe891bfaa592cc08c284d4f79f"
BOOTSTRAP_SETUP_MEMBER = "Python-3.12.16/Modules/Setup.bootstrap.in"
BOOTSTRAP_SETUP_SHA256 = "d7a4c34c97f414585c7e8480c106a0f85075fb166d4c82a91c5b0b00df455271"
STDLIB_SETUP_MEMBER = "Python-3.12.16/Modules/Setup.stdlib.in"
STDLIB_SETUP_SHA256 = "d78ae3af2718df36ac5a80531fe21831c0117a26534a977bbf4e7843c2ee6524"
CONFIG_C_TEMPLATE_MEMBER = "Python-3.12.16/Modules/config.c.in"
CONFIG_C_TEMPLATE_SHA256 = "5c76ef60a799f420b09b047dc1087728e5ed08ba82f6c7664c4d4f1d1d715b21"
CONFIGURE_SOURCE_MEMBER = "Python-3.12.16/configure.ac"
CONFIGURE_SOURCE_SHA256 = "4f5345c8d648693030493bdd4a499ae453d477c81a26f61af149d5c70e74d088"
GETPATH_SOURCE_MEMBER = "Python-3.12.16/Modules/getpath.py"
GETPATH_SOURCE_SHA256 = "46901bf54c780960d0ced5ac12a2f8e0db545518b54d6008a10fcefa903f7be2"
SYSCONFIG_SOURCE_SHA256 = "ce56212ba89be181fb90fe62496e6d2e436befaf2dffd10e87ce37d1685271a8"
IMPORTLIB_BOOTSTRAP_SOURCE_SHA256 = "d112d54b7831cf4a818d4841d5ff8003b54df220a6dabafa61f67d7c7a5603f7"
IMPORTLIB_EXTERNAL_SOURCE_SHA256 = "e6ad72f3f0f9b65c99ab52598cd02ab748511dcdce1dd51f18dace9be9a680c6"
IMPORTLIB_MACHINERY_SOURCE_SHA256 = "d045cd7ecf2a12b6ecbfbef79eb114e87ef2ebd756f5b705f73e6f3266e3dede"
IMPORTLIB_UTIL_SOURCE_SHA256 = "671f2995653f673f6d5056a1089debef473bc28ae7114f7a8db71475733d6876"
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_SOURCE_BYTES = 64 * 1024 * 1024
MAX_SOURCE_FILES = 2048
MAX_STDLIB_MODULE_NAMES_BYTES = 64 * 1024
MAX_FROZEN_SOURCE_BYTES = 64 * 1024
MAX_BOOTSTRAP_SETUP_BYTES = 64 * 1024
MAX_STDLIB_SETUP_BYTES = 64 * 1024
MAX_GETPATH_SOURCE_BYTES = 64 * 1024
MAX_CONFIG_C_TEMPLATE_BYTES = 64 * 1024
MAX_CONFIGURE_SOURCE_BYTES = 512 * 1024
ROOTS = (
    "dataclasses", "hashlib", "importlib.machinery", "importlib.util", "json",
    "os", "struct", "sys", "sysconfig", "types", "zipimport", "zlib",
)


def _archive_bytes(archive_path):
    path = Path(archive_path)
    with path.open("rb") as raw:
        archive_bytes = raw.read(MAX_ARCHIVE_BYTES + 1)
    if len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise ValueError("SOURCE_ARCHIVE_LIMIT")
    if hashlib.sha256(archive_bytes).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("SOURCE_ARCHIVE_MISMATCH")
    return archive_bytes


def _source_archive_data(archive_bytes):
    files = {}
    stdlib_header = None
    frozen_source = None
    bootstrap_setup = None
    stdlib_setup = None
    getpath_source = None
    config_c_template = None
    configure_source = None
    total = 0
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:xz") as source:
        for member in source:
            if member.name == FROZEN_SOURCE_MEMBER:
                if not member.isfile() or frozen_source is not None \
                        or member.size > MAX_FROZEN_SOURCE_BYTES:
                    raise ValueError("FROZEN_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("FROZEN_SOURCE_MEMBER")
                frozen_source = stream.read(member.size + 1)
                if (len(frozen_source) != member.size
                        or hashlib.sha256(frozen_source).hexdigest()
                        != FROZEN_SOURCE_SHA256):
                    raise ValueError("FROZEN_SOURCE_DIGEST")
                continue
            if member.name == BOOTSTRAP_SETUP_MEMBER:
                if not member.isfile() or bootstrap_setup is not None \
                        or member.size > MAX_BOOTSTRAP_SETUP_BYTES:
                    raise ValueError("BOOTSTRAP_SETUP_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("BOOTSTRAP_SETUP_MEMBER")
                bootstrap_setup = stream.read(member.size + 1)
                if (len(bootstrap_setup) != member.size
                        or hashlib.sha256(bootstrap_setup).hexdigest()
                        != BOOTSTRAP_SETUP_SHA256):
                    raise ValueError("BOOTSTRAP_SETUP_DIGEST")
                continue
            if member.name == STDLIB_SETUP_MEMBER:
                if not member.isfile() or stdlib_setup is not None \
                        or member.size > MAX_STDLIB_SETUP_BYTES:
                    raise ValueError("STDLIB_SETUP_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("STDLIB_SETUP_MEMBER")
                stdlib_setup = stream.read(member.size + 1)
                if (len(stdlib_setup) != member.size
                        or hashlib.sha256(stdlib_setup).hexdigest()
                        != STDLIB_SETUP_SHA256):
                    raise ValueError("STDLIB_SETUP_DIGEST")
                continue
            if member.name == GETPATH_SOURCE_MEMBER:
                if not member.isfile() or getpath_source is not None \
                        or member.size > MAX_GETPATH_SOURCE_BYTES:
                    raise ValueError("GETPATH_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("GETPATH_SOURCE_MEMBER")
                getpath_source = stream.read(member.size + 1)
                if (len(getpath_source) != member.size
                        or hashlib.sha256(getpath_source).hexdigest()
                        != GETPATH_SOURCE_SHA256):
                    raise ValueError("GETPATH_SOURCE_DIGEST")
                continue
            if member.name in (CONFIG_C_TEMPLATE_MEMBER, CONFIGURE_SOURCE_MEMBER):
                is_template = member.name == CONFIG_C_TEMPLATE_MEMBER
                current = config_c_template if is_template else configure_source
                limit = MAX_CONFIG_C_TEMPLATE_BYTES if is_template else MAX_CONFIGURE_SOURCE_BYTES
                if not member.isfile() or current is not None or member.size > limit:
                    raise ValueError("CONFIGURE_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("CONFIGURE_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                expected = CONFIG_C_TEMPLATE_SHA256 if is_template else CONFIGURE_SOURCE_SHA256
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("CONFIGURE_SOURCE_DIGEST")
                if is_template:
                    config_c_template = body
                else:
                    configure_source = body
                continue
            if member.name == STDLIB_MODULE_NAMES_MEMBER:
                if not member.isfile() or stdlib_header is not None \
                        or member.size > MAX_STDLIB_MODULE_NAMES_BYTES:
                    raise ValueError("STDLIB_MODULE_NAMES_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("STDLIB_MODULE_NAMES_MEMBER")
                stdlib_header = stream.read(member.size + 1)
                if (len(stdlib_header) != member.size
                        or hashlib.sha256(stdlib_header).hexdigest()
                        != STDLIB_MODULE_NAMES_SHA256):
                    raise ValueError("STDLIB_MODULE_NAMES_DIGEST")
                continue
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
    return (files, stdlib_header, frozen_source, bootstrap_setup, stdlib_setup,
            getpath_source, config_c_template, configure_source)


def _source_files(archive_path):
    return _source_archive_data(_archive_bytes(archive_path))[0]


def _stdlib_module_names(header):
    if (type(header) is not bytes or not header
            or len(header) > MAX_STDLIB_MODULE_NAMES_BYTES
            or hashlib.sha256(header).hexdigest() != STDLIB_MODULE_NAMES_SHA256):
        raise ValueError("STDLIB_MODULE_NAMES_DIGEST")
    text = header.decode("ascii")
    blocks = re.findall(
        r"(?m)^static const char\* _Py_stdlib_module_names\[\] = \{\n"
        r"((?:\"[A-Za-z_][A-Za-z0-9_]*\",\n)+)\};$",
        text,
    )
    if len(blocks) != 1:
        raise ValueError("STDLIB_MODULE_NAMES_FORMAT")
    names = tuple(re.findall(r'^"([A-Za-z_][A-Za-z0-9_]*)",$', blocks[0], re.M))
    if not names or names != tuple(sorted(set(names))):
        raise ValueError("STDLIB_MODULE_NAMES_ORDER")
    canonical = "".join(name + "\n" for name in names).encode("ascii")
    return names, hashlib.sha256(canonical).hexdigest()


def _frozen_module_inventory(source_bytes):
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_FROZEN_SOURCE_BYTES
            or hashlib.sha256(source_bytes).hexdigest() != FROZEN_SOURCE_SHA256):
        raise ValueError("FROZEN_SOURCE_DIGEST")
    text = source_bytes.decode("utf-8")
    tables = {}
    for table in ("bootstrap_modules", "stdlib_modules", "test_modules"):
        blocks = re.findall(
            rf"(?ms)^static const struct _frozen {table}\[\] = \{{\n(.*?)^\}};?$",
            text,
        )
        if len(blocks) != 1:
            raise ValueError("FROZEN_TABLE_FORMAT")
        names = []
        rows = [
            line for line in blocks[0].splitlines()
            if line.strip() and not re.fullmatch(r"\s*/\*.*\*/\s*", line)
        ]
        sentinel = f"{table.removesuffix('_modules')} sentinel"
        if not rows or not re.fullmatch(
                rf"\s*\{{0,\s*0,\s*0\}}\s*/\* {sentinel} \*/\s*", rows[-1]):
            raise ValueError("FROZEN_TABLE_SENTINEL")
        for row in rows[:-1]:
            match = re.fullmatch(r'\s*\{"([^"\\]+)",.*\},?\s*', row)
            if match is None:
                raise ValueError("FROZEN_TABLE_ROW")
            names.append(match.group(1))
        names = tuple(names)
        if not names or len(names) != len(set(names)):
            raise ValueError("FROZEN_TABLE_NAMES")
        tables[table] = tuple(sorted(names))
    alias_blocks = re.findall(
        r"(?ms)^static const struct _module_alias aliases\[\] = \{\n(.*?)^\};$",
        text,
    )
    if len(alias_blocks) != 1:
        raise ValueError("FROZEN_ALIAS_FORMAT")
    alias_rows = [line for line in alias_blocks[0].splitlines() if line.strip()]
    if not alias_rows or not re.fullmatch(
            r"\s*\{0,\s*0\}\s*/\* aliases sentinel \*/\s*", alias_rows[-1]):
        raise ValueError("FROZEN_ALIAS_SENTINEL")
    aliases = []
    for row in alias_rows[:-1]:
        match = re.fullmatch(
            r'\s*\{"([^"\\]+)",\s*(?:"([^"\\]+)"|NULL)\},\s*', row
        )
        if match is None:
            raise ValueError("FROZEN_ALIAS_ROW")
        aliases.append((match.group(1), match.group(2) or ""))
    aliases = tuple(aliases)
    if not aliases or len(aliases) != len({alias for alias, _ in aliases}):
        raise ValueError("FROZEN_ALIAS_NAMES")

    def digest_rows(rows):
        return hashlib.sha256(
            "".join("\t".join(row) + "\n" for row in rows).encode("utf-8")
        ).hexdigest()

    return {
        "bootstrap_names": tables["bootstrap_modules"],
        "stdlib_names": tables["stdlib_modules"],
        "test_names": tables["test_modules"],
        "aliases": tuple(sorted(aliases)),
        "bootstrap_sha256": digest_rows(tuple((name,) for name in tables["bootstrap_modules"])),
        "stdlib_sha256": digest_rows(tuple((name,) for name in tables["stdlib_modules"])),
        "test_sha256": digest_rows(tuple((name,) for name in tables["test_modules"])),
        "aliases_sha256": digest_rows(tuple(sorted(aliases))),
    }


def _bootstrap_setup_inventory(source_bytes):
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_BOOTSTRAP_SETUP_BYTES
            or hashlib.sha256(source_bytes).hexdigest() != BOOTSTRAP_SETUP_SHA256):
        raise ValueError("BOOTSTRAP_SETUP_DIGEST")
    text = source_bytes.decode("utf-8")
    names = []
    rows = []
    static_count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "*static*":
            static_count += 1
            continue
        match = re.fullmatch(
            r"(?:@MODULE_([A-Z0-9_]+)_TRUE@\s*)?"
            r"([A-Za-z_][A-Za-z0-9_]*)\s+(.+)", stripped
        )
        if match is None:
            raise ValueError("BOOTSTRAP_SETUP_ROW")
        condition, name, sources = match.groups()
        source_paths = sources.split()
        if not source_paths or any(not path.endswith(".c") for path in source_paths):
            raise ValueError("BOOTSTRAP_SETUP_SOURCES")
        names.append(name)
        rows.append((name, condition or ""))
    if static_count != 1:
        raise ValueError("BOOTSTRAP_SETUP_STATIC")
    if len(names) != len(set(names)):
        raise ValueError("BOOTSTRAP_SETUP_NAMES")
    canonical = "".join("\t".join(row) + "\n" for row in sorted(rows)).encode("ascii")
    return {
        "name_count": len(names),
        "conditional_name_count": sum(bool(condition) for _, condition in rows),
        "source_sha256": BOOTSTRAP_SETUP_SHA256,
        "rows_sha256": hashlib.sha256(canonical).hexdigest(),
        "conditional_names": tuple(sorted(
            (name, condition) for name, condition in rows if condition
        )),
    }


def _stdlib_setup_inventory(source_bytes):
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_STDLIB_SETUP_BYTES
            or hashlib.sha256(source_bytes).hexdigest() != STDLIB_SETUP_SHA256):
        raise ValueError("STDLIB_SETUP_DIGEST")
    text = source_bytes.decode("utf-8")
    entries = []
    test_section = False
    directives = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            if stripped == "# Test modules":
                test_section = True
            continue
        if stripped in ("*shared*", "*static*", "*@MODULE_BUILDTYPE@*"):
            directives.append(stripped)
            continue
        match = re.fullmatch(
            r"@MODULE_([A-Z0-9_]+)_TRUE@([A-Za-z_][A-Za-z0-9_]*)\s+(.+)",
            stripped,
        )
        if match is None:
            raise ValueError("STDLIB_SETUP_ROW")
        condition, name, source_list = match.groups()
        source_paths = source_list.split()
        if not source_paths or any(
                not (path.endswith((".c", ".a")) or path.startswith("-")
                     or path.startswith("@") or path.startswith("$("))
                for path in source_paths):
            raise ValueError("STDLIB_SETUP_SOURCES")
        entries.append((name, condition, "test" if test_section else "stdlib"))

    names = tuple(entry[0] for entry in entries)
    if not entries or len(names) != len(set(names)):
        raise ValueError("STDLIB_SETUP_NAMES")
    if directives != ["*@MODULE_BUILDTYPE@*", "*shared*"]:
        raise ValueError("STDLIB_SETUP_DIRECTIVES")
    runtime_rows = tuple(sorted(entry for entry in entries if entry[2] == "stdlib"))
    test_rows = tuple(sorted(entry for entry in entries if entry[2] == "test"))
    canonical = "".join("\t".join(entry) + "\n" for entry in sorted(entries))
    return {
        "stdlib_entry_count": len(runtime_rows),
        "test_entry_count": len(test_rows),
        "condition_count": len({entry[1] for entry in entries}),
        "source_sha256": STDLIB_SETUP_SHA256,
        "rows_sha256": hashlib.sha256(canonical.encode("ascii")).hexdigest(),
        "stdlib_names_sha256": hashlib.sha256(
            "".join(entry[0] + "\n" for entry in runtime_rows).encode("ascii")
        ).hexdigest(),
        "test_names_sha256": hashlib.sha256(
            "".join(entry[0] + "\n" for entry in test_rows).encode("ascii")
        ).hexdigest(),
    }


def _top_level_names(tree):
    assignments = set()
    functions = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            functions.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assignments.add(node.target.id)
    return assignments, functions


def _getpath_source_inventory(source_bytes):
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_GETPATH_SOURCE_BYTES
            or hashlib.sha256(source_bytes).hexdigest() != GETPATH_SOURCE_SHA256):
        raise ValueError("GETPATH_SOURCE_DIGEST")
    tree = ast.parse(source_bytes.decode("utf-8"))
    assignments, functions = _top_level_names(tree)
    path_variables = (
        "base_exec_prefix", "base_executable", "base_prefix", "exec_prefix",
        "executable", "home", "platlibdir", "platstdlib_dir", "prefix",
        "program_name", "pythonpath", "real_executable_dir", "stdlib_dir",
        "venv_prefix",
    )
    if not set(path_variables).issubset(assignments) or "search_up" not in functions:
        raise ValueError("GETPATH_SOURCE_SYMBOLS")
    config_keys = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)
                and node.value.id == "config" and isinstance(node.slice, ast.Constant)
                and type(node.slice.value) is str):
            config_keys.add(node.slice.value)
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
              and node.func.attr == "get" and isinstance(node.func.value, ast.Name)
              and node.func.value.id == "config" and node.args
              and isinstance(node.args[0], ast.Constant)
              and type(node.args[0].value) is str):
            config_keys.add(node.args[0].value)
    if "pythonpath_env" not in config_keys:
        raise ValueError("GETPATH_SOURCE_CONFIG_KEYS")
    canonical = "".join(name + "\n" for name in path_variables).encode("ascii")
    config_canonical = "".join(name + "\n" for name in sorted(config_keys)).encode("ascii")
    return {
        "source_sha256": GETPATH_SOURCE_SHA256,
        "source_bytes": len(source_bytes),
        "path_variable_count": len(path_variables),
        "path_variables": path_variables,
        "path_variables_sha256": hashlib.sha256(canonical).hexdigest(),
        "config_key_count": len(config_keys),
        "config_keys": tuple(sorted(config_keys)),
        "config_keys_sha256": hashlib.sha256(config_canonical).hexdigest(),
    }


def _sysconfig_source_inventory(source_bytes):
    if (type(source_bytes) is not bytes or not source_bytes
            or hashlib.sha256(source_bytes).hexdigest() != SYSCONFIG_SOURCE_SHA256):
        raise ValueError("SYSCONFIG_SOURCE_DIGEST")
    tree = ast.parse(source_bytes.decode("utf-8"))
    assignments, functions = _top_level_names(tree)
    required_functions = (
        "_get_sysconfigdata_name", "get_config_var", "get_config_vars",
        "get_path", "get_path_names", "get_paths",
    )
    if "_INSTALL_SCHEMES" not in assignments \
            or not set(required_functions).issubset(functions):
        raise ValueError("SYSCONFIG_SOURCE_SYMBOLS")
    function_nodes = {
        node.name: node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    def function_without_docstring(function):
        body = list(function.body)
        if (body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and type(body[0].value.value) is str):
            body.pop(0)
        fields = {name: getattr(function, name) for name in function._fields}
        fields["body"] = body
        normalized = type(function)(**fields)
        return ast.dump(normalized, include_attributes=False)

    expected_name_builder = ast.parse(
        "def _get_sysconfigdata_name():\n"
        "    multiarch = getattr(sys.implementation, '_multiarch', '')\n"
        "    return os.environ.get('_PYTHON_SYSCONFIGDATA_NAME', "
        "f'_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}')\n"
    ).body[0]
    expected_posix_init = ast.parse(
        "def _init_posix(vars):\n"
        "    name = _get_sysconfigdata_name()\n"
        "    _temp = __import__(name, globals(), locals(), ['build_time_vars'], 0)\n"
        "    build_time_vars = _temp.build_time_vars\n"
        "    vars.update(build_time_vars)\n"
    ).body[0]
    name_builder = function_nodes.get("_get_sysconfigdata_name")
    posix_init = function_nodes.get("_init_posix")
    if (name_builder is None or posix_init is None
            or function_without_docstring(name_builder)
            != function_without_docstring(expected_name_builder)):
        raise ValueError("SYSCONFIGDATA_NAME_SOURCE")
    if function_without_docstring(posix_init) != function_without_docstring(expected_posix_init):
        raise ValueError("SYSCONFIGDATA_IMPORT_SOURCE")
    scheme_assignment = next((node for node in tree.body
                              if isinstance(node, ast.Assign)
                              and any(isinstance(target, ast.Name)
                                      and target.id == "_INSTALL_SCHEMES"
                                      for target in node.targets)), None)
    if scheme_assignment is None:
        raise ValueError("SYSCONFIG_SCHEME_SOURCE")
    try:
        schemes = ast.literal_eval(scheme_assignment.value)
    except (ValueError, TypeError, SyntaxError) as error:
        raise ValueError("SYSCONFIG_SCHEME_LITERAL") from error
    if (type(schemes) is not dict or not schemes
            or any(type(name) is not str for name in schemes)
            or any(type(value) is not dict for value in schemes.values())):
        raise ValueError("SYSCONFIG_SCHEME_SHAPE")
    if any(type(key) is not str or type(value) is not str
           for scheme in schemes.values() for key, value in scheme.items()):
        raise ValueError("SYSCONFIG_SCHEME_PATHS")
    scheme_names = tuple(sorted(schemes))
    path_keys = tuple(sorted({key for value in schemes.values() for key in value}))
    template_rows = tuple(sorted(
        (scheme_name, key, template)
        for scheme_name, scheme in schemes.items()
        for key, template in scheme.items()
    ))
    scheme_digest = hashlib.sha256(
        "".join(name + "\n" for name in scheme_names).encode("ascii")
    ).hexdigest()
    path_digest = hashlib.sha256(
        "".join(name + "\n" for name in path_keys).encode("ascii")
    ).hexdigest()
    return {
        "source_sha256": SYSCONFIG_SOURCE_SHA256,
        "source_bytes": len(source_bytes),
        "scheme_count": len(scheme_names),
        "scheme_names": scheme_names,
        "scheme_names_sha256": scheme_digest,
        "path_key_count": len(path_keys),
        "path_keys": path_keys,
        "path_keys_sha256": path_digest,
        "path_template_row_count": len(template_rows),
        "path_templates_sha256": hashlib.sha256(
            "".join("\t".join(row) + "\n" for row in template_rows).encode("ascii")
        ).hexdigest(),
        "required_function_count": len(required_functions),
        "required_functions_sha256": hashlib.sha256(
            "".join(name + "\n" for name in required_functions).encode("ascii")
        ).hexdigest(),
        "sysconfigdata_override_key": "_PYTHON_SYSCONFIGDATA_NAME",
        "sysconfigdata_name_template": "_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}",
        "sysconfigdata_importer": "__import__",
        "sysconfigdata_imported_attribute": "build_time_vars",
    }


def _class_method_names(tree):
    classes = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes[node.name] = tuple(
                child.name for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
    return classes


def _importlib_source_inventory(bootstrap_bytes, external_bytes):
    sources = (
        (bootstrap_bytes, IMPORTLIB_BOOTSTRAP_SOURCE_SHA256),
        (external_bytes, IMPORTLIB_EXTERNAL_SOURCE_SHA256),
    )
    trees = []
    for body, expected in sources:
        if (type(body) is not bytes or not body
                or len(body) > MAX_SOURCE_BYTES
                or hashlib.sha256(body).hexdigest() != expected):
            raise ValueError("IMPORTLIB_SOURCE_DIGEST")
        trees.append(ast.parse(body.decode("utf-8")))
    bootstrap_tree, external_tree = trees
    bootstrap_classes = _class_method_names(bootstrap_tree)
    external_classes = _class_method_names(external_tree)
    spec = next((node for node in bootstrap_tree.body
                 if isinstance(node, ast.ClassDef) and node.name == "ModuleSpec"), None)
    init = next((node for node in spec.body
                 if isinstance(node, ast.FunctionDef) and node.name == "__init__"), None) if spec else None
    if init is None:
        raise ValueError("IMPORTLIB_MODULE_SPEC_INIT")
    spec_fields = set()
    for node in ast.walk(init):
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = (node.target,)
        else:
            continue
        for target in targets:
            if (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                    and target.value.id == "self"):
                spec_fields.add(target.attr)
    required_spec_fields = {
        "name", "loader", "origin", "loader_state", "submodule_search_locations",
        "_uninitialized_submodules", "_set_fileattr", "_cached",
    }


    if spec_fields != required_spec_fields:
        raise ValueError("IMPORTLIB_MODULE_SPEC_FIELDS")
    required_bootstrap = {
        "BuiltinImporter", "FrozenImporter", "ModuleSpec",
    }
    required_external = {
        "SourceFileLoader", "SourcelessFileLoader", "ExtensionFileLoader",
        "NamespaceLoader", "PathFinder", "FileFinder",
    }
    if not required_bootstrap.issubset(bootstrap_classes) or not required_external.issubset(external_classes):
        raise ValueError("IMPORTLIB_FINDER_LOADER_CLASSES")
    required_methods = {
        "_find_spec", "_find_and_load", "_load_unlocked", "_init_module_attrs",
    }
    bootstrap_functions = {
        node.name for node in bootstrap_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    if not required_methods.issubset(bootstrap_functions):
        raise ValueError("IMPORTLIB_BOOTSTRAP_METHODS")
    bootstrap_rows = tuple(sorted(
        (name, method) for name, methods in bootstrap_classes.items()
        for method in methods if name in required_bootstrap
    ))
    external_rows = tuple(sorted(
        (name, method) for name, methods in external_classes.items()
        for method in methods if name in required_external
    ))
    field_rows = tuple(sorted(spec_fields))
    canonical = lambda rows: "".join("\t".join(row) + "\n" if isinstance(row, tuple) else row + "\n" for row in rows).encode("ascii")
    return {
        "source_sha256": tuple(expected for _, expected in sources),
        "module_spec_field_count": len(field_rows),
        "module_spec_fields": field_rows,
        "module_spec_fields_sha256": hashlib.sha256(canonical(field_rows)).hexdigest(),
        "builtin_frozen_importer_count": len(required_bootstrap - {"ModuleSpec"}),
        "loader_finder_class_count": len(required_external),
        "bootstrap_method_count": len(required_methods),
        "bootstrap_methods_sha256": hashlib.sha256(canonical(tuple(sorted(required_methods)))).hexdigest(),
        "builtin_frozen_methods_sha256": hashlib.sha256(canonical(bootstrap_rows)).hexdigest(),
        "loader_finder_methods_sha256": hashlib.sha256(canonical(external_rows)).hexdigest(),
    }


def _importlib_public_api_inventory(machinery_bytes, util_bytes):
    sources = (
        ("machinery.py", machinery_bytes, IMPORTLIB_MACHINERY_SOURCE_SHA256),
        ("util.py", util_bytes, IMPORTLIB_UTIL_SOURCE_SHA256),
    )
    rows = []
    for filename, body, expected in sources:
        if (type(body) is not bytes or not body
                or hashlib.sha256(body).hexdigest() != expected):
            raise ValueError("IMPORTLIB_PUBLIC_API_DIGEST")
        tree = ast.parse(body.decode("utf-8"))
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module:
                for item in node.names:
                    exported = item.asname or item.name
                    if not exported.startswith("_"):
                        rows.append((filename, exported, node.module, item.name))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not node.name.startswith("_"):
                    rows.append((filename, node.name, "<local>", node.name))
    canonical_rows = tuple(sorted(rows))
    machinery_names = {row[1] for row in canonical_rows if row[0] == "machinery.py"}
    util_names = {row[1] for row in canonical_rows if row[0] == "util.py"}
    required_machinery = {
        "ModuleSpec", "BuiltinImporter", "FrozenImporter", "PathFinder",
        "FileFinder", "SourceFileLoader", "SourcelessFileLoader",
        "ExtensionFileLoader", "NamespaceLoader",
    }

    required_util = {
        "module_from_spec", "spec_from_loader", "find_spec",
        "spec_from_file_location", "LazyLoader",
    }
    if not required_machinery.issubset(machinery_names) or not required_util.issubset(util_names):
        raise ValueError("IMPORTLIB_PUBLIC_API_SYMBOLS")
    encoded = "".join("\t".join(row) + "\n" for row in canonical_rows).encode("ascii")
    return {
        "source_sha256": tuple(expected for _, _, expected in sources),
        "row_count": len(canonical_rows),
        "rows_sha256": hashlib.sha256(encoded).hexdigest(),
        "machinery_export_count": len(machinery_names),
        "util_export_count": len(util_names),
    }


def _configure_template_inventory(config_template, configure_source):
    if (type(config_template) is not bytes or not config_template
            or len(config_template) > MAX_CONFIG_C_TEMPLATE_BYTES
            or hashlib.sha256(config_template).hexdigest() != CONFIG_C_TEMPLATE_SHA256):
        raise ValueError("CONFIG_C_TEMPLATE_DIGEST")
    if (type(configure_source) is not bytes or not configure_source
            or len(configure_source) > MAX_CONFIGURE_SOURCE_BYTES
            or hashlib.sha256(configure_source).hexdigest() != CONFIGURE_SOURCE_SHA256):
        raise ValueError("CONFIGURE_SOURCE_DIGEST")
    c_text = config_template.decode("utf-8")
    if (c_text.count("/* -- ADDMODULE MARKER 1 -- */") != 1
            or c_text.count("/* -- ADDMODULE MARKER 2 -- */") != 1
            or c_text.count("struct _inittab _PyImport_Inittab[] = {") != 1):
        raise ValueError("CONFIG_C_TEMPLATE_MARKERS")
    rows = tuple(re.findall(
        r'^\s*\{"([A-Za-z_][A-Za-z0-9_]*)",\s*([A-Za-z_][A-Za-z0-9_]*|NULL)\},?\s*$',
        c_text, re.M,
    ))
    if len(rows) != 9 or len({name for name, _ in rows}) != len(rows):
        raise ValueError("CONFIG_C_TEMPLATE_ROWS")
    if not {"builtins", "sys", "marshal", "_imp"}.issubset({name for name, _ in rows}):
        raise ValueError("CONFIG_C_TEMPLATE_REQUIRED_ROWS")
    config_c_rows_sha256 = hashlib.sha256(
        "".join("\t".join(row) + "\n" for row in rows).encode("ascii")
    ).hexdigest()
    configure_text = configure_source.decode("utf-8")
    configure_lines = tuple(
        line.strip() for line in configure_text.splitlines()
        if "MODULE_BLOCK" in line or "MODULE_BUILDTYPE" in line
    )
    required_anchors = (
        "AC_DEFUN([_MODULE_BLOCK_ADD]",
        "AC_SUBST([MODULE_BLOCK])",
        "AC_SUBST([MODULE_BUILDTYPE])",
        "MODULE_BLOCK=",
    )
    if any(anchor not in configure_text for anchor in required_anchors):
        raise ValueError("CONFIGURE_MODULE_BLOCK_ANCHORS")
    configure_rows_sha256 = hashlib.sha256(
        "".join(line + "\n" for line in configure_lines).encode("utf-8")
    ).hexdigest()
    return {
        "config_c_source_sha256": CONFIG_C_TEMPLATE_SHA256,
        "config_c_source_bytes": len(config_template),
        "config_c_row_count": len(rows),
        "config_c_rows_sha256": config_c_rows_sha256,
        "configure_source_sha256": CONFIGURE_SOURCE_SHA256,
        "configure_source_bytes": len(configure_source),
        "configure_module_anchor_count": len(configure_lines),
        "configure_module_anchors_sha256": configure_rows_sha256,
    }


def _module_path(module, files):
    relative = module.replace(".", "/")
    package = relative + "/__init__.py"
    return package if package in files else relative + ".py" if relative + ".py" in files else None


def _module_source_rows(files, modules):
    """Return the ordered name/path/hash evidence for source candidates only."""
    if (type(modules) is not tuple or len(modules) > MAX_SOURCE_FILES
            or any(type(name) is not str or not name
                   or any(not part.isidentifier() for part in name.split("."))
                   for name in modules)):
        raise ValueError("CANDIDATE_MODULES")
    if modules != tuple(sorted(set(modules))):
        raise ValueError("CANDIDATE_MODULES")
    rows = []
    for module in modules:
        path = _module_path(module, files)
        if path is None or path not in files:
            raise ValueError("CANDIDATE_SOURCE_MISSING")
        rows.append({
            "module": module,
            "source_path": path,
            "source_sha256": hashlib.sha256(files[path]).hexdigest(),
        })
    return rows


def _import_names(tree, module, path):
    package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]

    def literal_string(node):
        if isinstance(node, ast.Constant) and type(node.value) is str:
            return node.value
        if isinstance(node, ast.JoinedStr):
            parts = []
            for value in node.values:
                if isinstance(value, ast.Constant) and type(value.value) is str:
                    parts.append(value.value)
                elif (isinstance(value, ast.FormattedValue)
                      and value.conversion in (-1, ord("s"))
                      and isinstance(value.value, (ast.Constant, ast.JoinedStr))):
                    formatted_value = literal_string(value.value)
                    format_spec = (literal_string(value.format_spec)
                                   if value.format_spec is not None else None)
                    if (formatted_value is None
                            or (value.format_spec is not None and format_spec != "s")):
                        return None
                    parts.append(formatted_value)
                else:
                    return None
            return "".join(parts)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left, right = literal_string(node.left), literal_string(node.right)
            if left is not None and right is not None:
                return left + right

    literal_name_aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = (node.target,)
        else:
            continue
        literal_value = literal_string(node.value)
        if literal_value is None:
            continue
        if not literal_value or literal_value.startswith("."):
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                literal_name_aliases.setdefault(target.id, set()).add(literal_value)

    importlib_module_aliases = {"importlib"}
    import_module_aliases = set()
    builtins_module_aliases = {"builtins"}
    builtin_import_aliases = {"__import__"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                binding = alias.asname or alias.name.partition(".")[0]
                if alias.name == "importlib":
                    importlib_module_aliases.add(binding)
                elif alias.name == "builtins":
                    builtins_module_aliases.add(binding)
                elif alias.name == "importlib.import_module":
                    import_module_aliases.add(binding)
                elif alias.name == "builtins.__import__":
                    builtin_import_aliases.add(binding)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                binding = alias.asname or alias.name
                if node.module == "importlib" and alias.name == "import_module":
                    import_module_aliases.add(binding)
                elif node.module == "builtins" and alias.name == "__import__":
                    builtin_import_aliases.add(binding)

    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, ast.AnnAssign):
                targets = (node.target,)
            else:
                continue
            names = tuple(target.id for target in targets if isinstance(target, ast.Name))
            value = node.value
            if isinstance(value, ast.Name):
                if value.id in import_module_aliases:
                    aliases, source = import_module_aliases, value.id
                elif value.id in builtin_import_aliases:
                    aliases, source = builtin_import_aliases, value.id
                else:
                    continue
            elif (isinstance(value, ast.Attribute)
                  and isinstance(value.value, ast.Name)
                  and value.attr == "import_module"
                  and value.value.id in importlib_module_aliases):
                aliases, source = import_module_aliases, value.attr
            elif (isinstance(value, ast.Attribute)
                  and isinstance(value.value, ast.Name)
                  and value.attr == "__import__"
                  and value.value.id in builtins_module_aliases):
                aliases, source = builtin_import_aliases, value.attr
            else:
                continue
            for name in names:
                if name not in aliases:
                    aliases.add(name)
                    changed = True

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
        elif isinstance(node, ast.Call) and node.args:
            direct_literal = literal_string(node.args[0])
            if (direct_literal and not direct_literal.startswith(".")):
                import_names = (direct_literal,)
            elif isinstance(node.args[0], ast.Name):
                import_names = tuple(sorted(literal_name_aliases.get(node.args[0].id, ())))
            else:
                import_names = ()
            if not import_names:
                continue
            if isinstance(node.func, ast.Name) and node.func.id in builtin_import_aliases:
                yield from import_names
            elif (isinstance(node.func, ast.Attribute)
                  and node.func.attr == "import_module"
                  and isinstance(node.func.value, ast.Name)
                  and node.func.value.id in importlib_module_aliases):
                yield from import_names
            elif (isinstance(node.func, ast.Name)
                  and node.func.id in import_module_aliases):
                yield from import_names
            elif (isinstance(node.func, ast.Attribute)
                  and node.func.attr == "__import__"
                  and isinstance(node.func.value, ast.Name)
                  and node.func.value.id in builtins_module_aliases):
                yield from import_names


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
            candidates = []
            for index in range(1, len(parts) + 1):
                candidate = ".".join(parts[:index])
                if _module_path(candidate, files) is not None:
                    candidates.append(candidate)
            if candidates:
                edges += 1
                pending.extend(candidate for candidate in candidates if candidate not in reached)
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
            candidates = []
            for index in range(1, len(parts) + 1):
                candidate = ".".join(parts[:index])
                if _module_path(candidate, files) is not None:
                    candidates.append(candidate)
            if candidates:
                edges += 1
                pending.extend(candidate for candidate in candidates if candidate not in reached)
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
    aliases = {}

    def collect_aliases(node):
        if isinstance(node, ast.ClassDef):
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            return
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            if isinstance(value, (ast.Name, ast.Attribute)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name):
                        aliases.setdefault(target.id, []).append(value)
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                collect_aliases(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    collect_aliases(statement)

    def resolve_base(expression, active=()):
        if isinstance(expression, ast.Name):
            if expression.id in active:
                return (expression.id,)
            candidates = aliases.get(expression.id)
            if candidates:
                resolved = []
                for candidate in candidates:
                    for value in resolve_base(candidate, (*active, expression.id)):
                        if value not in resolved:
                            resolved.append(value)
                return tuple(resolved)
            return (expression.id,)
        if isinstance(expression, ast.Attribute):
            return tuple(
                value + "." + expression.attr
                for value in resolve_base(expression.value, active)
            )
        return ()

    def collect(node):
        if isinstance(node, ast.ClassDef):
            bases = result.setdefault(node.name, [])
            for base in node.bases:
                if isinstance(base, (ast.Name, ast.Attribute)):
                    for base_name in resolve_base(base):
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
        collect_aliases(statement)
    for statement in tree.body:
        collect(statement)
    return {name: tuple(bases) for name, bases in result.items()}


def _top_level_factory_constructor_index(tree):
    factories = {}

    def simple_return_call(statement):
        if not isinstance(statement, ast.Return):
            return None
        returned = statement.value
        if (not isinstance(returned, ast.Call) or returned.keywords
                or not isinstance(returned.func, (ast.Name, ast.Attribute))):
            return None
        return ast.unparse(returned.func)

    def inert_prefix(statement):
        return (isinstance(statement, (ast.Import, ast.ImportFrom))
                or (isinstance(statement, ast.Expr)
                    and isinstance(statement.value, ast.Constant)
                    and type(statement.value.value) is str))

    def imported_bindings(statement):
        if isinstance(statement, ast.Import):
            return tuple(alias.asname or alias.name.partition(".")[0]
                         for alias in statement.names)
        if isinstance(statement, ast.ImportFrom):
            return tuple(alias.asname or alias.name for alias in statement.names)
        return ()

    def constructor_bindings(statements):
        bindings = {}
        for statement in statements:
            if inert_prefix(statement):
                for name in imported_bindings(statement):
                    bindings.pop(name, None)
                continue
            if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
                return None
            targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
            value = statement.value
            if len(targets) != 1 or not isinstance(targets[0], ast.Name):
                return None
            target = targets[0].id
            if isinstance(value, ast.Call) and not value.keywords \
                    and isinstance(value.func, (ast.Name, ast.Attribute)):
                bindings[target] = ast.unparse(value.func)
            elif isinstance(value, ast.Name) and value.id in bindings:
                bindings[target] = bindings[value.id]
            else:
                bindings.pop(target, None)
        return bindings

    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.body:
            continue
        returns = []
        prefix = node.body[:-1]
        if isinstance(node.body[-1], ast.Return):
            terminal = simple_return_call(node.body[-1])
            if terminal is not None:
                returns.append(terminal)
                for statement in prefix:
                    if inert_prefix(statement):
                        continue
                    if (isinstance(statement, ast.If) and not statement.orelse
                            and len(statement.body) == 1):
                        branch = simple_return_call(statement.body[0])
                        if branch is None:
                            returns = []
                            break
                        returns.append(branch)
                        continue
                    returns = []
                    break
            elif isinstance(node.body[-1].value, ast.Name):
                bindings = constructor_bindings(prefix)
                target = node.body[-1].value.id
                if bindings is not None and target in bindings:
                    returns.append(bindings[target])
            else:
                continue
        elif isinstance(node.body[-1], ast.If) and node.body[-1].orelse:
            branch = node.body[-1]
            if any(not inert_prefix(statement) for statement in prefix):
                continue
            if len(branch.body) != 1 or len(branch.orelse) != 1:
                continue
            body_return = simple_return_call(branch.body[0])
            else_return = simple_return_call(branch.orelse[0])
            if body_return is None or else_return is None:
                continue
            returns.extend((body_return, else_return))
        else:
            continue
        if not returns:
            continue
        factories[node.name] = tuple(dict.fromkeys(returns))
    return factories


def _top_level_local_class_alias_index(tree, class_index):
    """Resolve simple module-scope aliases to locally declared classes."""
    aliases = {}

    def collect(node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            return
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(node.value, ast.Name):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    candidates = aliases.setdefault(target.id, [])
                    if node.value.id not in candidates:
                        candidates.append(node.value.id)
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                collect(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    collect(statement)

    def resolve(name, active=()):
        if name in active:
            return ()
        if name in class_index:
            return (name,)
        result = []
        for source in aliases.get(name, ()):
            for target in resolve(source, (*active, name)):
                if target not in result:
                    result.append(target)
        return tuple(result)

    for statement in tree.body:
        collect(statement)
    return {name: resolve(name) for name in aliases}


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
    local_aliases = {}
    module_aliases = _imported_module_aliases(tree, module, path, class_index)

    def add_class_target(alias, target):
        targets = result.setdefault(alias, [])
        if target not in targets:
            targets.append(target)

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
            add_class_target(alias, (base, imported.name))

    def collect_aliases(node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            return
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if isinstance(value, (ast.Name, ast.Attribute)):
                for target in targets:
                    if isinstance(target, ast.Name):
                        sources = local_aliases.setdefault(target.id, [])
                        if not any(ast.dump(value) == ast.dump(source) for source in sources):
                            sources.append(value)
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                collect_aliases(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    collect_aliases(statement)

    def resolve(alias, active=()):
        if alias in active:
            return ()
        targets = list(result.get(alias, ()))
        for expression in local_aliases.get(alias, ()):
            if isinstance(expression, ast.Name):
                source_targets = resolve(expression.id, (*active, alias))
            elif isinstance(expression, ast.Attribute):
                receiver = ast.unparse(expression.value)
                source_targets = tuple(
                    (target_module, expression.attr)
                    for target_module in module_aliases.get(receiver, ())
                    if expression.attr in class_index.get(target_module, {})
                )
            else:
                source_targets = ()
            for target in source_targets:
                if target not in targets:
                    targets.append(target)
        return tuple(targets)

    for statement in tree.body:
        collect_aliases(statement)
    for alias in local_aliases:
        for target in resolve(alias):
            add_class_target(alias, target)
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


def _imported_module_function_aliases(
        module_aliases, function_index, class_dispatch_index):
    result = {}
    for expression, imported_modules in module_aliases.items():
        aliases = result.setdefault(expression, {})
        for module in imported_modules:
            for function_name in function_index.get(module, {}):
                target = (module, function_name)
                targets = aliases.setdefault(function_name, [])
                if target not in targets:
                    targets.append(target)
            for class_name, methods in class_dispatch_index.get(module, {}).items():
                constructors = methods.get("__init__", ())
                if not constructors:
                    continue
                targets = aliases.setdefault(class_name, [])
                for constructor in constructors:
                    target = constructor
                    if target not in targets:
                        targets.append(target)
    return {expression: {name: tuple(targets) for name, targets in functions.items()}
            for expression, functions in result.items()}


def _imported_module_class_method_aliases(module_aliases, class_dispatch_index):
    result = {}

    for expression, imported_modules in module_aliases.items():
        for module in imported_modules:
            for class_name, methods in class_dispatch_index.get(module, {}).items():
                receiver = expression + "." + class_name
                aliases = result.setdefault(receiver, {})
                for method_name, owners in methods.items():
                    targets = aliases.setdefault(method_name, [])
                    for owner in owners:
                        target = owner
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
    factory_constructors = _top_level_factory_constructor_index(tree)
    module_class_methods = scope_class_methods(tree.body)
    module_class_bases = _top_level_class_base_index(tree)
    module_class_aliases = _top_level_local_class_alias_index(
        tree, module_class_methods
    )

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

    def known_class_method_targets(class_name, method_name):
        """Return methods on a known class and its known local ancestors."""
        local_targets = []
        imported_targets = set()
        class_candidates = tuple(dict.fromkeys((
            class_name, *module_class_aliases.get(class_name, ()),
            *factory_constructors.get(class_name, ()),
        )))
        for local_class in class_candidates:
            for candidate in (local_class, *local_base_classes(local_class)):
                for function in module_class_methods.get(candidate, {}).get(method_name, ()):
                    if function not in local_targets:
                        local_targets.append(function)
                imported_targets.update(
                    (imported_class_methods or {}).get(candidate, {}).get(method_name, ())
                )
                imported_targets.update(
                    (imported_module_class_methods or {}).get(candidate, {}).get(method_name, ())
                )
        return tuple(local_targets), tuple(sorted(imported_targets))

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
                method_names = set(local_methods) | set(imported_methods)
                for factory_class in factory_constructors.get(constructor.id, ()):
                    method_names.update(module_class_methods.get(factory_class, {}))
                    method_names.update((imported_class_methods or {}).get(factory_class, {}))
                    method_names.update((imported_module_class_methods or {}).get(factory_class, {}))
                method_names.update(
                    name
                    for base_name in local_base_classes(constructor.id)
                    for name in (
                        set(module_class_methods.get(base_name, {}))
                        | set((imported_class_methods or {}).get(base_name, {}))
                        | set((imported_module_class_methods or {}).get(base_name, {}))
                    )
                )
                resolved_methods = {
                    name: known_class_method_targets(constructor.id, name)
                    for name in method_names
                }
            elif isinstance(constructor, ast.Attribute):
                receiver = ast.unparse(constructor.value) + "." + constructor.attr
                local_methods = {}
                imported_methods = (imported_module_class_methods or {}).get(receiver, {})
                resolved_methods = {
                    name: ((), tuple(targets))
                    for name, targets in imported_methods.items()
                }
            else:
                return
            bound = result.setdefault(target_name, {})
            for method_name, (functions, targets) in resolved_methods.items():
                local = bound.setdefault(method_name, {"local": [], "imported": []})["local"]
                for function in functions:
                    if function not in local:
                        local.append(function)
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
    function_imported_class_closures = {}
    class_method_closure_bases = []

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
        nonlocal imported_class_methods
        if function_scope is None:
            function_scope = module_functions
        if isinstance(node, ast.Lambda):
            for expression in (*node.args.defaults, *node.args.kw_defaults):
                if expression is not None:
                    yield from visit(expression, active_functions, in_function, function_scope)
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_closures.setdefault(id(node), function_scope)
            function_imported_class_closures.setdefault(
                id(node), dict(
                    class_method_closure_bases[-1]
                    if class_method_closure_bases else imported_class_methods or {}
                )
            )
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
            scoped_alias_tree = ast.Module(body=node.body, type_ignores=[])
            scoped_class_aliases = _top_level_local_class_alias_index(
                scoped_alias_tree, imported_class_methods or {}
            )
            scoped_method_aliases = {}
            for alias, sources in scoped_class_aliases.items():
                targets = {}
                for source_name in sources:
                    for method_name, entries in (imported_class_methods or {}).get(
                        source_name, {}
                    ).items():
                        bucket = targets.setdefault(method_name, [])
                        for entry in entries:
                            if entry not in bucket:
                                bucket.append(entry)
                if targets:
                    scoped_method_aliases[alias] = {
                        name: tuple(entries) for name, entries in targets.items()
                    }
            original_imported_class_methods = imported_class_methods
            class_method_closure_bases.append(original_imported_class_methods or {})
            if scoped_method_aliases:
                imported_class_methods = {
                    **(original_imported_class_methods or {}),
                    **scoped_method_aliases,
                }
            for statement in node.body:
                yield from visit(statement, class_scope, False, function_scope)
            class_method_closure_bases.pop()
            imported_class_methods = original_imported_class_methods
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
            constructor_targets, imported_constructor_targets = known_class_method_targets(
                node.func.id, "__init__"
            )
            for function in constructor_targets:
                pending.append((function, function_closures.get(id(function), function_scope)))
            imported_calls.update(imported_constructor_targets)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            constructor_targets = known_class_method_targets(
                ast.unparse(node.func), "__init__"
            )
            imported_calls.update(constructor_targets[1])
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
                    local_targets, imported_targets = known_class_method_targets(
                        constructor.id, node.func.attr
                    )
                    for function in local_targets:
                        pending.append((function, function_closures.get(id(function), function_scope)))
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
        enclosing_imported_class_methods = imported_class_methods
        closure_class_methods = function_imported_class_closures.get(id(function), {})
        if closure_class_methods:
            imported_class_methods = {
                **(imported_class_methods or {}),
                **closure_class_methods,
            }
        active_instance_methods = constructed_instance_methods(function.body)
        active_method_context = method_receiver_context.get(id(function))
        # Track direct same-function aliases of established class candidates.
        # Called nested functions inherit this snapshot as a lexical closure;
        # Conditional/compound factory results and dynamic rebinding remain unresolved.
        scoped_alias_tree = ast.Module(body=function.body, type_ignores=[])
        scoped_class_aliases = _top_level_local_class_alias_index(
            scoped_alias_tree, imported_class_methods or {}
        )
        scoped_method_aliases = {}
        for alias, sources in scoped_class_aliases.items():
            targets = {}
            for source_name in sources:
                for method_name, entries in (imported_class_methods or {}).get(
                    source_name, {}
                ).items():
                    bucket = targets.setdefault(method_name, [])
                    for entry in entries:
                        if entry not in bucket:
                            bucket.append(entry)
            if targets:
                scoped_method_aliases[alias] = {
                    name: tuple(entries) for name, entries in targets.items()
                }
        original_imported_class_methods = imported_class_methods
        if scoped_method_aliases:
            imported_class_methods = {
                **(original_imported_class_methods or {}),
                **scoped_method_aliases,
            }
        visible_functions = dict(closure_scope)
        visible_functions.update(scope_functions(function.body))
        visible_functions = scope_function_aliases(function.body, visible_functions)
        for statement in function.body:
            imports.extend(visit(statement, visible_functions, True, visible_functions))
        imported_class_methods = enclosing_imported_class_methods
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
    source_class_bases = {}
    class_dispatch_index = {}
    for source_module in lexical_modules:
        source_path = _module_path(source_module, files)
        if source_path is None:
            continue
        source_tree = ast.parse(files[source_path], filename=source_path)
        module_sources[source_module] = (source_path, source_tree)
        function_index[source_module] = _top_level_function_index(source_tree)
        class_index[source_module] = _top_level_class_method_index(source_tree)
    for source_module, (source_path, source_tree) in module_sources.items():
        class_bases = _top_level_class_base_index(source_tree)
        imported_classes = _imported_class_aliases(
            source_tree, source_module, source_path, class_index
        )
        imported_modules = _imported_module_aliases(
            source_tree, source_module, source_path, function_index
        )
        module_bases = {}
        for class_name, base_names in class_bases.items():
            resolved = []
            for base_name in base_names:
                candidates = []
                if base_name in class_index[source_module]:
                    candidates.append((source_module, base_name))
                candidates.extend(imported_classes.get(base_name, ()))
                if "." in base_name:
                    receiver, _, imported_name = base_name.rpartition(".")
                    candidates.extend(
                        (target_module, imported_name)
                        for target_module in imported_modules.get(receiver, ())
                        if imported_name in class_index.get(target_module, {})
                    )
                for candidate in candidates:
                    if candidate not in resolved:
                        resolved.append(candidate)
            module_bases[class_name] = tuple(resolved)
        source_class_bases[source_module] = module_bases

    for source_module, classes in class_index.items():
        module_dispatch = {}
        for class_name in classes:
            pending_classes = [(source_module, class_name)]
            seen_classes = set()
            methods = {}
            while pending_classes:
                candidate_module, candidate_class = pending_classes.pop()
                candidate = (candidate_module, candidate_class)
                if candidate in seen_classes:
                    continue
                seen_classes.add(candidate)
                for method_name in class_index.get(candidate_module, {}).get(
                    candidate_class, {}
                ):
                    owners = methods.setdefault(method_name, [])
                    owner = (candidate_module, candidate_class + "." + method_name)
                    if owner not in owners:
                        owners.append(owner)
                pending_classes.extend(
                    source_class_bases.get(candidate_module, {}).get(candidate_class, ())
                )
            module_dispatch[class_name] = {
                name: tuple(sorted(owners)) for name, owners in methods.items()
            }
        class_dispatch_index[source_module] = module_dispatch

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
                constructors = class_dispatch_index.get(target_module, {}).get(
                    class_name, {}
                ).get("__init__", ())
                if constructors:
                    existing = list(imported_functions.get(alias, ()))
                    for constructor in constructors:
                        target = constructor
                        if target not in existing:
                            existing.append(target)
                    imported_functions[alias] = tuple(existing)
        imported_class_methods = {}
        for alias, targets in imported_classes.items():
            methods = imported_class_methods.setdefault(alias, {})
            for target_module, class_name in targets:
                for method_name, owners in class_dispatch_index.get(
                    target_module, {}
                ).get(class_name, {}).items():
                    method_targets = methods.setdefault(method_name, [])
                    for owner in owners:
                        target = owner
                        if target not in method_targets:
                            method_targets.append(target)
        imported_class_methods = {
            alias: {name: tuple(targets) for name, targets in methods.items()}
            for alias, methods in imported_class_methods.items()
        }
        module_aliases = _imported_module_aliases(tree, module, path, function_index)
        imported_modules = _imported_module_function_aliases(
            module_aliases, function_index, class_dispatch_index
        )
        imported_module_class_methods = _imported_module_class_method_aliases(
            module_aliases, class_dispatch_index
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
    (files, stdlib_header, frozen_source, bootstrap_setup, stdlib_setup,
     getpath_source, config_c_template, configure_source) = _source_archive_data(
        _archive_bytes(archive_path)
    )
    if stdlib_header is None:
        raise ValueError("STDLIB_MODULE_NAMES_MISSING")
    if frozen_source is None:
        raise ValueError("FROZEN_SOURCE_MISSING")
    if bootstrap_setup is None:
        raise ValueError("BOOTSTRAP_SETUP_MISSING")
    if stdlib_setup is None:
        raise ValueError("STDLIB_SETUP_MISSING")
    if getpath_source is None:
        raise ValueError("GETPATH_SOURCE_MISSING")
    stdlib_names, stdlib_names_sha256 = _stdlib_module_names(stdlib_header)
    frozen = _frozen_module_inventory(frozen_source)
    bootstrap_setup_inventory = _bootstrap_setup_inventory(bootstrap_setup)
    stdlib_setup_inventory = _stdlib_setup_inventory(stdlib_setup)
    getpath_inventory = _getpath_source_inventory(getpath_source)
    sysconfig_source = files.get("sysconfig.py")
    if sysconfig_source is None:
        raise ValueError("SYSCONFIG_SOURCE_MISSING")
    sysconfig_inventory = _sysconfig_source_inventory(sysconfig_source)
    importlib_bootstrap = files.get("importlib/_bootstrap.py")
    importlib_external = files.get("importlib/_bootstrap_external.py")
    if importlib_bootstrap is None or importlib_external is None:
        raise ValueError("IMPORTLIB_SOURCE_MISSING")
    importlib_inventory = _importlib_source_inventory(
        importlib_bootstrap, importlib_external
    )
    machinery_source = files.get("importlib/machinery.py")
    util_source = files.get("importlib/util.py")
    if machinery_source is None or util_source is None:
        raise ValueError("IMPORTLIB_PUBLIC_API_SOURCE_MISSING")
    importlib_api_inventory = _importlib_public_api_inventory(
        machinery_source, util_source
    )
    configure_inventory = _configure_template_inventory(
        config_c_template, configure_source
    )
    modules, edges, rows_sha256 = _candidate_closure(files)
    module_body, module_body_edges, module_body_sha256 = _module_body_candidate_closure(files)
    target_platform, target_edges, target_sha256, target_conditions = _target_platform_candidate_closure(files)
    call_modules, call_edges, call_functions, call_sha256, call_conditions = (
        _module_init_call_candidate_closure(files)
    )
    call_roots = {name.partition(".")[0] for name in call_modules}
    call_roots_outside_stdlib = tuple(sorted(call_roots - set(stdlib_names)))
    frozen_roots = {
        name.partition(".")[0]
        for name in (*frozen["bootstrap_names"], *frozen["stdlib_names"])
    }
    frozen_roots_outside_stdlib = tuple(sorted(frozen_roots - set(stdlib_names)))
    return {
        "archive_sha256": ARCHIVE_SHA256,
        "source_stdlib_module_names_count": len(stdlib_names),
        "source_stdlib_module_names_sha256": stdlib_names_sha256,
        "frozen_source_sha256": FROZEN_SOURCE_SHA256,
        "frozen_bootstrap_name_count": len(frozen["bootstrap_names"]),
        "frozen_bootstrap_names_sha256": frozen["bootstrap_sha256"],
        "frozen_stdlib_name_count": len(frozen["stdlib_names"]),
        "frozen_stdlib_names_sha256": frozen["stdlib_sha256"],
        "frozen_test_name_count": len(frozen["test_names"]),
        "frozen_test_names_sha256": frozen["test_sha256"],
        "frozen_alias_count": len(frozen["aliases"]),
        "frozen_aliases_sha256": frozen["aliases_sha256"],
        "frozen_runtime_roots_outside_source_stdlib_names": list(
            frozen_roots_outside_stdlib
        ),
        "bootstrap_setup_name_count": bootstrap_setup_inventory["name_count"],
        "bootstrap_setup_conditional_name_count": bootstrap_setup_inventory[
            "conditional_name_count"
        ],
        "bootstrap_setup_source_sha256": bootstrap_setup_inventory["source_sha256"],
        "bootstrap_setup_rows_sha256": bootstrap_setup_inventory["rows_sha256"],
        "bootstrap_setup_conditional_names": [
            list(row) for row in bootstrap_setup_inventory["conditional_names"]
        ],
        "stdlib_setup_entry_count": stdlib_setup_inventory["stdlib_entry_count"],
        "stdlib_setup_test_entry_count": stdlib_setup_inventory["test_entry_count"],
        "stdlib_setup_condition_count": stdlib_setup_inventory["condition_count"],
        "stdlib_setup_source_sha256": stdlib_setup_inventory["source_sha256"],
        "stdlib_setup_rows_sha256": stdlib_setup_inventory["rows_sha256"],
        "stdlib_setup_names_sha256": stdlib_setup_inventory["stdlib_names_sha256"],
        "stdlib_setup_test_names_sha256": stdlib_setup_inventory[
            "test_names_sha256"
        ],
        "getpath_source_sha256": getpath_inventory["source_sha256"],
        "getpath_source_bytes": getpath_inventory["source_bytes"],
        "getpath_path_variable_count": getpath_inventory["path_variable_count"],
        "getpath_path_variables": list(getpath_inventory["path_variables"]),
        "getpath_path_variables_sha256": getpath_inventory[
            "path_variables_sha256"
        ],
        "getpath_config_key_count": getpath_inventory["config_key_count"],
        "getpath_config_keys": list(getpath_inventory["config_keys"]),
        "getpath_config_keys_sha256": getpath_inventory[
            "config_keys_sha256"
        ],
        "sysconfig_source_sha256": sysconfig_inventory["source_sha256"],
        "sysconfig_source_bytes": sysconfig_inventory["source_bytes"],
        "sysconfig_install_scheme_count": sysconfig_inventory["scheme_count"],
        "sysconfig_install_scheme_names": list(
            sysconfig_inventory["scheme_names"]
        ),
        "sysconfig_scheme_names_sha256": sysconfig_inventory[
            "scheme_names_sha256"
        ],
        "sysconfig_path_key_count": sysconfig_inventory["path_key_count"],
        "sysconfig_path_keys": list(sysconfig_inventory["path_keys"]),
        "sysconfig_path_keys_sha256": sysconfig_inventory["path_keys_sha256"],
        "sysconfig_path_template_row_count": sysconfig_inventory[
            "path_template_row_count"
        ],
        "sysconfig_path_templates_sha256": sysconfig_inventory[
            "path_templates_sha256"
        ],
        "sysconfig_required_function_count": sysconfig_inventory[
            "required_function_count"
        ],
        "sysconfig_required_functions_sha256": sysconfig_inventory[
            "required_functions_sha256"
        ],
        "sysconfigdata_override_key": sysconfig_inventory[
            "sysconfigdata_override_key"
        ],
        "sysconfigdata_name_template": sysconfig_inventory[
            "sysconfigdata_name_template"
        ],
        "sysconfigdata_importer": sysconfig_inventory["sysconfigdata_importer"],
        "sysconfigdata_imported_attribute": sysconfig_inventory[
            "sysconfigdata_imported_attribute"
        ],
        "importlib_module_spec_field_count": importlib_inventory[
            "module_spec_field_count"
        ],
        "importlib_module_spec_fields": list(importlib_inventory[
            "module_spec_fields"
        ]),
        "importlib_module_spec_fields_sha256": importlib_inventory[
            "module_spec_fields_sha256"
        ],
        "importlib_builtin_frozen_importer_count": importlib_inventory[
            "builtin_frozen_importer_count"
        ],
        "importlib_loader_finder_class_count": importlib_inventory[
            "loader_finder_class_count"
        ],
        "importlib_bootstrap_method_count": importlib_inventory[
            "bootstrap_method_count"
        ],
        "importlib_bootstrap_methods_sha256": importlib_inventory[
            "bootstrap_methods_sha256"
        ],
        "importlib_builtin_frozen_methods_sha256": importlib_inventory[
            "builtin_frozen_methods_sha256"
        ],
        "importlib_loader_finder_methods_sha256": importlib_inventory[
            "loader_finder_methods_sha256"
        ],
        "importlib_public_api_row_count": importlib_api_inventory["row_count"],
        "importlib_public_api_rows_sha256": importlib_api_inventory[
            "rows_sha256"
        ],
        "importlib_machinery_export_count": importlib_api_inventory[
            "machinery_export_count"
        ],
        "importlib_util_export_count": importlib_api_inventory[
            "util_export_count"
        ],
        **configure_inventory,
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
        "module_init_call_source_candidates": _module_source_rows(files, call_modules),
        "module_init_call_edge_count": call_edges,
        "module_init_call_function_count": call_functions,
        "module_init_call_roots_outside_source_stdlib_names": list(
            call_roots_outside_stdlib
        ),
        "module_init_call_scope": "MODULE_CLASS_CALLS_SIMPLE_ALIASES_GENERATORS_IMPORTED_FUNCTIONS_MODULE_ALIASES_FROM_IMPORT_IMPORTED_CLASS_METHODS_DIRECT_CONSTRUCTED_METHODS_SAME_SCOPE_INSTANCE_BINDINGS_INSTANCE_ALIASES_BOUND_RECEIVER_METHODS_NESTED_RECEIVER_CLOSURES_INHERITED_RECEIVER_METHODS_AND_TRANSITIVE_LOCAL_BASES_AND_IMPORTED_SOURCE_BASES_AND_BASE_ALIASES_AND_ZERO_ARG_AND_EXPLICIT_LOCAL_SUPER_METHODS_AND_INHERITED_CONSTRUCTORS_AND_CONSTRUCTED_INHERITED_METHODS_AND_IMPORTED_SOURCE_SUBCLASS_DISPATCH_SAME_MODULE_AND_IMPORTED_SOURCE_BASE_DISPATCH_AND_SIMPLE_IMPORTED_CLASS_ALIASES_AND_QUALIFIED_IMPORTED_CLASS_ALIASES_AND_LOCAL_CLASS_ALIASES_AND_DIRECT_FUNCTION_AND_CLASS_SCOPE_IMPORTED_CLASS_ALIASES_AND_CALLED_NESTED_FUNCTION_CLASS_ALIAS_CLOSURES_AND_DIRECT_TOP_LEVEL_FACTORY_RETURNS_AFTER_IMPORTS_AND_DOCSTRINGS_AND_SIMPLE_LOCAL_INSTANCE_ASSIGNMENTS",
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
