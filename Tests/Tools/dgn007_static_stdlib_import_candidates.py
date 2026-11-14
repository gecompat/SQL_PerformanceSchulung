"""Konservative Quelltextkandidaten, keine CPython-P11-Importinventur."""
import argparse
import ast
import gzip
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
AST_ASDL_MEMBER = "Python-3.12.16/Parser/Python.asdl"
AST_ASDL_SHA256 = "ecc26bc2818ebddec685f96663c811de8915beaa74a7cb1ace6eea3920679ac7"
AST_C_MEMBER = "Python-3.12.16/Python/Python-ast.c"
AST_C_SHA256 = "07983b321fa333242448efc0eb9990f64823532a4a95b01eccf672f69c8c3b4e"
SYS_MODULE_C_MEMBER = "Python-3.12.16/Python/sysmodule.c"
SYS_MODULE_C_SHA256 = "6ac1dffffac870e8a7fbe7578ad6a93ff5f6afb4f501ac3ffd1b5e00f17630ff"
SYS_MODULE_CLINIC_MEMBER = "Python-3.12.16/Python/clinic/sysmodule.c.h"
SYS_MODULE_CLINIC_SHA256 = "957a480449ebdd284eae78bf27ef663b0f964ef595eb49208a82f8cb17a93833"
LOGGING_SOURCE_SHA256 = "43f86bbc08fdd5c7b6e697abffe1381f534a92bb32e1f1aee8360d6a142592a1"
WARNINGS_SOURCE_SHA256 = "6405e281882932205eae641b2d31fba7776f94517a206d289465a1caffbf310e"
WARNINGS_C_MEMBER = "Python-3.12.16/Python/_warnings.c"
WARNINGS_C_SHA256 = "5567817b35e387b6cc5c37074fdcbf0a3978242564a95460ccdc3fe5d6f08019"
WARNINGS_CLINIC_MEMBER = "Python-3.12.16/Python/clinic/_warnings.c.h"
WARNINGS_CLINIC_SHA256 = "8ec95ee20132c6ccd71b56070cd5028e0db877a745b215cc5e3ddff8d675b5f0"
DIS_SOURCE_SHA256 = "44c0b389c96124d8fb5cb0bc41c7a2aa7a6848ef4001b4000dcbd858efa4a1a2"
TOKENIZE_SOURCE_SHA256 = "026f566ac63e60d69c8185a3880831b657accc5eac984fadf271fc99a5e5825d"
OPCODE_SOURCE_SHA256 = "192f6008508f28d3273bff42eaea9b01c8394dab1607cd36aea778bdd166c3a6"
TOKEN_SOURCE_SHA256 = "1a4d994ce9744f4bfe2d964fc24d112a1e76796a08c2e45a2d73c82a8587f922"
OS_SOURCE_SHA256 = "6f3888d1a5bd4f1333116dd75ca8f1d2d951e38c8c8426179417aea097a1eef0"
POSIX_MODULE_C_MEMBER = "Python-3.12.16/Modules/posixmodule.c"
POSIX_MODULE_C_SHA256 = "a8f1410ad95326648a473672ee3bf8158a5f744b7c032c0142327fb252688ab4"
POSIX_MODULE_CLINIC_MEMBER = "Python-3.12.16/Modules/clinic/posixmodule.c.h"
POSIX_MODULE_CLINIC_SHA256 = "dd89b7a30073abfad8f082966f135a343ca4e1b7b856e3ba696a6e9c27870747"
TARGET_PYCONFIG_SHA256 = "22a6bfe20214fb395e546edd499f826d9d4be7b7b1289b0d391255145a207ed5"
TARGET_IMAGE_MANIFEST_SHA256 = "3c3ba8ad4c85eb63b7568f806434f14e33370056985da7fdf2673621cb1d7e93"
TARGET_IMAGE_CONFIG_SHA256 = "28d30c15b9e9c3b1d557441aad9592226e852f7716451d6c8df5b4f0c3ce3d1b"
TARGET_IMAGE_CONFIG_LAYER_SHA256 = "7f0ea382d75a163999c21529b19913d158821816106eed6f02039f8fdf346779"
TARGET_IMAGE_LAYER_NAMES = (
    "69245854ad5855991d16224f6abf55855d2d73922785206adea9c5c5988434a0",
    "338554e9113fa6731ba588cb8f45e85b3e3fe7ada531ee7d7b0bc9291d616727",
    "d6c30932f8d3f5798b438cce12cdf6cebb1717b52f51e22ff010b4d86667031d",
    "9bab93d346cda15207e5a5000093cee7256ec1092fb689ec3d2997faf31b9a16",
    "c3bb8894691e757a336b94388048f0557392a3e6d6e0a515f0b690a9cbfba3a1",
    "7f0ea382d75a163999c21529b19913d158821816106eed6f02039f8fdf346779",
    "7d0909af463852965fc4e328a11b968cf56707fd15258498d0a43b4c6a1b0953",
)
TARGET_EXECUTABLE_PATH = "usr/local/bin/python3.12"
TARGET_EXECUTABLE_SHA256 = "837a48d7afd08447fb43e28b282026fadb59368620072e57e01f66d12977e5ce"
THREADING_SOURCE_SHA256 = "846f450ae794e4aab823a163f8c71d27751148af33e91dd3de886686a4e8ebfb"
THREAD_NATIVE_ID_HEADER_MEMBER = "Python-3.12.16/Include/pythread.h"
THREAD_NATIVE_ID_HEADER_SHA256 = "cd063073710988ea21b54588473542e5f3b2be06f637dc5a028aefd5a7949144"
THREAD_NATIVE_ID_MODULE_MEMBER = "Python-3.12.16/Modules/_threadmodule.c"
THREAD_NATIVE_ID_MODULE_SHA256 = "277217c4a704bc84f9b7caf79123eaed8a45288c3023747e457df5d817cc8bc1"
THREAD_NATIVE_ID_PTHREAD_MEMBER = "Python-3.12.16/Python/thread_pthread.h"
THREAD_NATIVE_ID_PTHREAD_SHA256 = "467f48143ba6bd2dc8f139934d46fdaefe48b11ddf19e476a71ad156996f9195"
GETPATH_SOURCE_MEMBER = "Python-3.12.16/Modules/getpath.py"
GETPATH_SOURCE_SHA256 = "46901bf54c780960d0ced5ac12a2f8e0db545518b54d6008a10fcefa903f7be2"
SYSCONFIG_SOURCE_SHA256 = "ce56212ba89be181fb90fe62496e6d2e436befaf2dffd10e87ce37d1685271a8"
SITE_SOURCE_SHA256 = "b39ab288cc7a6d0cb3bb2655179221411340b22418e4efdee4c20175537a5fa2"
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
MAX_AST_ASDL_BYTES = 64 * 1024
MAX_AST_C_BYTES = 512 * 1024
MAX_SYS_MODULE_C_BYTES = 256 * 1024
MAX_SYS_MODULE_CLINIC_BYTES = 64 * 1024
MAX_WARNINGS_C_BYTES = 64 * 1024
MAX_WARNINGS_CLINIC_BYTES = 16 * 1024
MAX_POSIX_MODULE_C_BYTES = 512 * 1024
MAX_POSIX_MODULE_CLINIC_BYTES = 384 * 1024
MAX_TARGET_PYCONFIG_BYTES = 64 * 1024
MAX_TARGET_IMAGE_CONFIG_BYTES = 16 * 1024
MAX_TARGET_IMAGE_SAVE_BYTES = 1024 * 1024 * 1024
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
    ast_asdl = None
    ast_c_source = None
    sys_module_c_source = None
    sys_module_clinic_source = None
    warnings_c_source = None
    warnings_clinic_source = None
    posix_module_c_source = None
    posix_module_clinic_source = None
    thread_native_id_header = None
    thread_native_id_module = None
    thread_native_id_pthread = None
    thread_source_members = {
        THREAD_NATIVE_ID_HEADER_MEMBER: "header",
        THREAD_NATIVE_ID_MODULE_MEMBER: "module",
        THREAD_NATIVE_ID_PTHREAD_MEMBER: "pthread",
    }
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
            if member.name in (AST_ASDL_MEMBER, AST_C_MEMBER):
                is_asdl = member.name == AST_ASDL_MEMBER
                current = ast_asdl if is_asdl else ast_c_source
                limit = MAX_AST_ASDL_BYTES if is_asdl else MAX_AST_C_BYTES
                expected = AST_ASDL_SHA256 if is_asdl else AST_C_SHA256
                if not member.isfile() or current is not None or member.size > limit:
                    raise ValueError("AST_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("AST_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("AST_SOURCE_DIGEST")
                if is_asdl:
                    ast_asdl = body
                else:
                    ast_c_source = body
                continue
            if member.name in (SYS_MODULE_C_MEMBER, SYS_MODULE_CLINIC_MEMBER):
                is_module = member.name == SYS_MODULE_C_MEMBER
                current = sys_module_c_source if is_module else sys_module_clinic_source
                limit = MAX_SYS_MODULE_C_BYTES if is_module else MAX_SYS_MODULE_CLINIC_BYTES
                expected = SYS_MODULE_C_SHA256 if is_module else SYS_MODULE_CLINIC_SHA256
                if not member.isfile() or current is not None or member.size > limit:
                    raise ValueError("SYS_MODULE_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("SYS_MODULE_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("SYS_MODULE_SOURCE_DIGEST")
                if is_module:
                    sys_module_c_source = body
                else:
                    sys_module_clinic_source = body
                continue
            if member.name in (WARNINGS_C_MEMBER, WARNINGS_CLINIC_MEMBER):
                is_module = member.name == WARNINGS_C_MEMBER
                current = warnings_c_source if is_module else warnings_clinic_source
                limit = MAX_WARNINGS_C_BYTES if is_module else MAX_WARNINGS_CLINIC_BYTES
                expected = WARNINGS_C_SHA256 if is_module else WARNINGS_CLINIC_SHA256
                if not member.isfile() or current is not None or member.size > limit:
                    raise ValueError("WARNINGS_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("WARNINGS_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("WARNINGS_SOURCE_DIGEST")
                if is_module:
                    warnings_c_source = body
                else:
                    warnings_clinic_source = body
                continue
            if member.name in (POSIX_MODULE_C_MEMBER, POSIX_MODULE_CLINIC_MEMBER):
                is_module = member.name == POSIX_MODULE_C_MEMBER
                current = posix_module_c_source if is_module else posix_module_clinic_source
                limit = MAX_POSIX_MODULE_C_BYTES if is_module else MAX_POSIX_MODULE_CLINIC_BYTES
                expected = POSIX_MODULE_C_SHA256 if is_module else POSIX_MODULE_CLINIC_SHA256
                if not member.isfile() or current is not None or member.size > limit:
                    raise ValueError("POSIX_MODULE_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("POSIX_MODULE_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("POSIX_MODULE_SOURCE_DIGEST")
                if is_module:
                    posix_module_c_source = body
                else:
                    posix_module_clinic_source = body
                continue
            if member.name in thread_source_members:
                source_key = thread_source_members[member.name]
                current = {
                    "header": thread_native_id_header,
                    "module": thread_native_id_module,
                    "pthread": thread_native_id_pthread,
                }[source_key]
                expected = {
                    "header": THREAD_NATIVE_ID_HEADER_SHA256,
                    "module": THREAD_NATIVE_ID_MODULE_SHA256,
                    "pthread": THREAD_NATIVE_ID_PTHREAD_SHA256,
                }[source_key]
                if not member.isfile() or current is not None or member.size > MAX_AST_C_BYTES:
                    raise ValueError("THREAD_NATIVE_ID_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("THREAD_NATIVE_ID_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("THREAD_NATIVE_ID_SOURCE_DIGEST")
                if source_key == "header":
                    thread_native_id_header = body
                elif source_key == "module":
                    thread_native_id_module = body
                else:
                    thread_native_id_pthread = body
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
            getpath_source, config_c_template, configure_source, ast_asdl, ast_c_source,
            sys_module_c_source, sys_module_clinic_source, warnings_c_source,
            warnings_clinic_source, posix_module_c_source, posix_module_clinic_source,
            thread_native_id_header, thread_native_id_module, thread_native_id_pthread)


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
_IMPORTED_MODULE_NAME = object()
_STATIC_FALSE_LITERAL = object()
# Bounded from the digest-pinned linux/amd64 CPython 3.12.16 config.c/Inittab.
_TARGET_BUILTIN_MODULE_NAMES = (
    "_abc", "_ast", "_codecs", "_collections", "_functools", "_imp",
    "_io", "_locale", "_operator", "_signal", "_sre", "_stat",
    "_string", "_symtable", "_thread", "_tokenize", "_tracemalloc",
    "_typing", "_warnings", "_weakref", "atexit", "builtins", "errno",
    "faulthandler", "gc", "itertools", "marshal", "posix", "pwd", "sys",
    "time",
)
_TARGET_BUILTIN_MEMBERSHIP = {
    **dict.fromkeys(_TARGET_BUILTIN_MODULE_NAMES, True),
    "nt": False,
}
_TARGET_BUILTIN_CONFIG_C_SHA256 = (
    "30d353782cbaf8de2fed2ba82b1040940386e316b7f41604c49f8f3d6f16bb31"
)
_TARGET_BUILTIN_LAYER_SHA256 = (
    "7f0ea382d75a163999c21529b19913d158821816106eed6f02039f8fdf346779"
)
_TYPES_SOURCE_SHA256 = (
    "345474ef027a1273f353da9bdc1f7c18f65335e72e681bcc0376774cc51f2405"
)
_INSPECT_SOURCE_SHA256 = (
    "5c54ebf0bfdc25397750e5d0f63800751650ee50e65325ff3ea4069c9bfa5f75"
)
_AST_SOURCE_SHA256 = "b515c23dbbc459329d3b802a3aac742cc456d7472e66f7ed6e9dc97e40596d7d"
_TARGET_TYPES_DESCRIPTOR_ATTRIBUTES = (
    "GetSetDescriptorType", "MemberDescriptorType",
)


def _target_types_descriptor_call_facts(files):
    """Bind two `types` names only to their digest-pinned direct source definitions."""
    types_source = files.get("types.py")
    inspect_source = files.get("inspect.py")
    if (type(types_source) is not bytes or type(inspect_source) is not bytes
            or hashlib.sha256(types_source).hexdigest() != _TYPES_SOURCE_SHA256
            or hashlib.sha256(inspect_source).hexdigest() != _INSPECT_SOURCE_SHA256):
        return ()

    types_tree = ast.parse(types_source, filename="types.py")
    inspect_tree = ast.parse(inspect_source, filename="inspect.py")
    for name in _TARGET_TYPES_DESCRIPTOR_ATTRIBUTES:
        assignments = [
            statement for statement in types_tree.body
            if isinstance(statement, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == name
                    for target in statement.targets)
        ]
        stores = [
            node for node in ast.walk(types_tree)
            if isinstance(node, ast.Name) and node.id == name
            and isinstance(node.ctx, (ast.Store, ast.Del))
        ]
        if (len(assignments) != 1 or len(stores) != 1
                or not isinstance(assignments[0].value, ast.Call)
                or not isinstance(assignments[0].value.func, ast.Name)
                or assignments[0].value.func.id != "type"):
            return ()

    imports_types = [
        alias for statement in inspect_tree.body if isinstance(statement, ast.Import)
        for alias in statement.names if alias.name == "types"
    ]
    if (len(imports_types) != 1 or imports_types[0].asname is not None
            or any(isinstance(node, ast.Name) and node.id in {"types", "hasattr"}
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(inspect_tree))):
        return ()

    facts = []
    for name in _TARGET_TYPES_DESCRIPTOR_ATTRIBUTES:
        expression = f"hasattr(types, {name!r})"
        if not any(isinstance(node, ast.If) and ast.unparse(node.test) == expression
                   for node in inspect_tree.body):
            return ()
        facts.append(expression)
    return tuple((expression, True) for expression in sorted(facts))


def _target_ast_compatibility_call_facts(files, asdl_source, c_source):
    """Bind two legacy AST attribute absences to the pinned generated types."""
    ast_source = files.get("ast.py")
    if (type(ast_source) is not bytes
            or hashlib.sha256(ast_source).hexdigest() != _AST_SOURCE_SHA256
            or type(asdl_source) is not bytes
            or hashlib.sha256(asdl_source).hexdigest() != AST_ASDL_SHA256
            or type(c_source) is not bytes
            or hashlib.sha256(c_source).hexdigest() != AST_C_SHA256):
        return ()

    asdl_text = asdl_source.decode("utf-8")
    c_text = c_source.decode("utf-8")
    ast_tree = ast.parse(ast_source, filename="ast.py")
    if not any(
            isinstance(statement, ast.ImportFrom)
            and statement.module == "_ast"
            and any(alias.name == "*" for alias in statement.names)
            for statement in ast_tree.body):
        return ()
    if any(isinstance(node, ast.Name) and node.id in {"Constant", "Tuple", "hasattr"}
           and isinstance(node.ctx, (ast.Store, ast.Del)) for node in ast.walk(ast_tree)):
        return ()
    if not re.search(
            r'PyObject_SetAttrString\(state->AST_type, "_fields", empty_tuple\) < 0'
            r'.*?PyObject_SetAttrString\(state->AST_type, "_attributes", empty_tuple\) < 0',
            c_text, re.DOTALL):
        return ()
    if not re.search(
            r'state->expr_type\s*=\s*make_type\(state, "expr", state->AST_type, NULL, 0,',
            c_text):
        return ()

    definitions = (
        ("Constant", "constant value, string? kind", ("value", "kind"), "n"),
        ("Tuple", "expr* elts, expr_context ctx", ("elts", "ctx"), "dims"),
    )
    facts = []
    for name, asdl_fields, c_fields, absent_attribute in definitions:
        if (asdl_fields not in asdl_text
                or not re.search(
                    rf"\b{re.escape(name)}_fields\s*\[\s*\]\s*=\s*\{{([^}}]*)\}}\s*;",
                    c_text,
                )):
            return ()
        field_match = re.search(
            rf"\b{re.escape(name)}_fields\s*\[\s*\]\s*=\s*\{{([^}}]*)\}}\s*;", c_text
        )
        field_names = tuple(re.findall(r'"([^"\\]+)"', field_match.group(1)))
        if field_names != c_fields or absent_attribute in field_names:
            return ()
        make_type_pattern = (
            rf'state->{name}_type\s*=\s*make_type\(state,\s*"{name}",\s*'
            rf'state->expr_type,\s*{name}_fields,\s*{len(c_fields)},'
        )
        if not re.search(make_type_pattern, c_text):
            return ()
        expression = f"hasattr({name}, {absent_attribute!r})"
        expected_if = f"not {expression}"
        if not any(isinstance(node, ast.If) and ast.unparse(node.test) == expected_if
                   for node in ast.walk(ast_tree)):
            return ()
        facts.append((expression, False))
    return tuple(sorted(facts))


def _target_importlib_windows_name_facts(files):
    """Resolve the pinned importlib Windows selector from its direct sys binding."""
    source = files.get("importlib/_bootstrap_external.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != IMPORTLIB_EXTERNAL_SOURCE_SHA256):
        return {}
    tree = ast.parse(source, filename="importlib/_bootstrap_external.py")
    sys_imports = [
        alias for statement in tree.body if isinstance(statement, ast.Import)
        for alias in statement.names if alias.name == "sys"
    ]
    sys_stores = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id == "sys"
        and isinstance(node.ctx, (ast.Store, ast.Del))
    ]
    assignments = [
        statement for statement in tree.body if isinstance(statement, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "_MS_WINDOWS"
                for target in statement.targets)
    ]
    windows_stores = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id == "_MS_WINDOWS"
        and isinstance(node.ctx, (ast.Store, ast.Del))
    ]
    windows_guards = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.If) and ast.unparse(node.test) == "_MS_WINDOWS"
    ]
    expected = "sys.platform == 'win32'"
    if (len(sys_imports) != 1 or sys_imports[0].asname is not None or sys_stores
            or len(assignments) != 1 or len(windows_stores) != 1
            or not windows_guards
            or ast.unparse(assignments[0].value) != expected
            or assignments[0].lineno >= min(
                node.lineno for node in windows_guards
            )):
        return {}
    return {"_MS_WINDOWS": False}


def _target_sys_getframe_call_facts(files, sys_module_source, clinic_source):
    """Bind logging's sys._getframe probe to the pinned builtin method table."""
    logging_source = files.get("logging/__init__.py")
    if (type(logging_source) is not bytes
            or hashlib.sha256(logging_source).hexdigest() != LOGGING_SOURCE_SHA256
            or type(sys_module_source) is not bytes
            or hashlib.sha256(sys_module_source).hexdigest() != SYS_MODULE_C_SHA256
            or type(clinic_source) is not bytes
            or hashlib.sha256(clinic_source).hexdigest() != SYS_MODULE_CLINIC_SHA256
            or _TARGET_BUILTIN_MEMBERSHIP.get("sys") is not True):
        return ()
    logging_tree = ast.parse(logging_source, filename="logging/__init__.py")
    c_text = sys_module_source.decode("utf-8")
    clinic_text = clinic_source.decode("utf-8")
    imports_sys = [
        alias for statement in logging_tree.body if isinstance(statement, ast.Import)
        for alias in statement.names if alias.name == "sys"
    ]
    if (len(imports_sys) != 1 or imports_sys[0].asname is not None
            or any(isinstance(node, ast.Name) and node.id in {"sys", "hasattr"}
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(logging_tree))
            or not any(isinstance(node, ast.If)
                       and ast.unparse(node.test) == "hasattr(sys, '_getframe')"
                       for node in logging_tree.body)):
        return ()
    clinic_lines = clinic_text.splitlines()
    methoddef_index = next((index for index, line in enumerate(clinic_lines)
                            if line.startswith("#define SYS__GETFRAME_METHODDEF")), None)
    if (methoddef_index is None or methoddef_index + 1 >= len(clinic_lines)
            or '"_getframe"' not in clinic_lines[methoddef_index + 1]
            or '#include "clinic/sysmodule.c.h"' not in c_text
            or not re.search(r"(?m)^static PyMethodDef sys_methods\[\] = \{", c_text)
            or not re.search(r"(?m)^\s*SYS__GETFRAME_METHODDEF$", c_text)
            or not re.search(r"(?m)^static struct PyModuleDef sysmodule = \{", c_text)
            or not re.search(r"(?s)static struct PyModuleDef sysmodule = \{.*?\n\s*sys_methods,", c_text)
            ):
        return ()
    return (("hasattr(sys, '_getframe')", True),)


def _target_warnings_default_call_facts(files, c_source, clinic_source):
    """Prove the C warnings backend is selected by the pinned builtin import."""
    source = files.get("warnings.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != WARNINGS_SOURCE_SHA256
            or type(c_source) is not bytes
            or hashlib.sha256(c_source).hexdigest() != WARNINGS_C_SHA256
            or type(clinic_source) is not bytes
            or hashlib.sha256(clinic_source).hexdigest() != WARNINGS_CLINIC_SHA256
            or _TARGET_BUILTIN_MEMBERSHIP.get("_warnings") is not True):
        return {}
    tree = ast.parse(source, filename="warnings.py")
    backend_imports = [
        statement for statement in ast.walk(tree)
        if isinstance(statement, ast.ImportFrom) and statement.module == "_warnings"
    ]
    expected_names = {
        "filters", "_defaultaction", "_onceregistry", "warn", "warn_explicit",
        "_filters_mutated",
    }
    if (len(backend_imports) != 1
            or {alias.name for alias in backend_imports[0].names} != expected_names
            or not any(
                isinstance(node, ast.If) and ast.unparse(node.test) == "not _warnings_defaults"
                for node in tree.body
            )):
        return {}
    c_text = c_source.decode("utf-8")
    clinic_text = clinic_source.decode("utf-8")
    required_methods = (
        ("WARNINGS_WARN_METHODDEF", '"warn"'),
        ("WARNINGS_WARN_EXPLICIT_METHODDEF", '"warn_explicit"'),
        ("WARNINGS_FILTERS_MUTATED_METHODDEF", '"_filters_mutated"'),
    )
    clinic_lines = clinic_text.splitlines()
    for macro, method_name in required_methods:
        index = next((i for i, line in enumerate(clinic_lines)
                      if line.startswith(f"#define {macro}")), None)
        if (index is None or index + 1 >= len(clinic_lines)
                or method_name not in clinic_lines[index + 1]):
            return {}
    required_source_patterns = (
        r'#include "clinic/_warnings\.c\.h"',
        r"static PyMethodDef warnings_functions\[\] = \{",
        r"WARNINGS_WARN_METHODDEF",
        r"WARNINGS_WARN_EXPLICIT_METHODDEF",
        r"WARNINGS_FILTERS_MUTATED_METHODDEF",
        r'PyModule_AddObjectRef\(module, "filters", st->filters\)',
        r'PyModule_AddObjectRef\(module, "_onceregistry", st->once_registry\)',
        r'PyModule_AddObjectRef\(module, "_defaultaction", st->default_action\)',
        r"\.m_methods = warnings_functions",
        r"\.m_slots = warnings_slots",
        r"\{Py_mod_exec, warnings_module_exec\}",
    )
    if any(not re.search(pattern, c_text) for pattern in required_source_patterns):
        return {}
    return {"_warnings_defaults": True}


def _target_imported_name_star_imports_safe(files, module):
    """Keep imported __name__ only across pinned star exports that exclude it."""
    bindings = {
        "dis": (DIS_SOURCE_SHA256, "opcode", OPCODE_SOURCE_SHA256),
        "tokenize": (TOKENIZE_SOURCE_SHA256, "token", TOKEN_SOURCE_SHA256),
    }
    binding = bindings.get(module)
    if binding is None:
        return False
    importer_digest, exporter_name, exporter_digest = binding
    importer_path = module + ".py"
    exporter_path = exporter_name + ".py"
    importer = files.get(importer_path)
    exporter = files.get(exporter_path)
    if (type(importer) is not bytes or hashlib.sha256(importer).hexdigest() != importer_digest
            or type(exporter) is not bytes
            or hashlib.sha256(exporter).hexdigest() != exporter_digest):
        return False
    importer_tree = ast.parse(importer, filename=importer_path)
    star_imports = [
        statement for statement in importer_tree.body
        if isinstance(statement, ast.ImportFrom)
        and any(alias.name == "*" for alias in statement.names)
    ]
    if (len(star_imports) != 1 or star_imports[0].module != exporter_name
            or star_imports[0].level != 0):
        return False
    exporter_tree = ast.parse(exporter, filename=exporter_path)
    exports = [
        statement for statement in exporter_tree.body if isinstance(statement, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__all__"
                for target in statement.targets)
    ]
    stores = [
        node for node in ast.walk(exporter_tree)
        if isinstance(node, ast.Name) and node.id == "__all__"
        and isinstance(node.ctx, (ast.Store, ast.Del))
    ]
    if len(exports) != 1 or len(stores) != 1:
        return False
    try:
        exported_names = ast.literal_eval(exports[0].value)
    except (ValueError, TypeError):
        return False
    return (type(exported_names) is list
            and all(type(name) is str for name in exported_names)
            and "__name__" not in exported_names)


def _target_ast_imported_name_star_import_safe(files, ast_c_source):
    """Prove `_ast`'s default star exports cannot replace ast.__name__."""
    importer = files.get("ast.py")
    if (type(importer) is not bytes
            or hashlib.sha256(importer).hexdigest() != _AST_SOURCE_SHA256
            or type(ast_c_source) is not bytes
            or hashlib.sha256(ast_c_source).hexdigest() != AST_C_SHA256
            or b"__all__" in ast_c_source):
        return False
    tree = ast.parse(importer, filename="ast.py")
    star_imports = [
        statement for statement in tree.body if isinstance(statement, ast.ImportFrom)
        and any(alias.name == "*" for alias in statement.names)
    ]
    if (len(star_imports) != 1 or star_imports[0].module != "_ast"
            or star_imports[0].level != 0
            or any(isinstance(node, ast.Name) and node.id == "__name__"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(tree))):
        return False
    parents = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in {"exec", "eval", "locals", "vars"}):
            return False
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "globals"):
            continue
        ancestor = node
        function_scope = False
        comprehension = None
        while ancestor in parents:
            ancestor = parents[ancestor]
            if isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_scope = True
                break
            if isinstance(ancestor, ast.DictComp):
                comprehension = ancestor
                break
        if function_scope:
            continue
        attr_call = parents.get(parents.get(node))
        if (comprehension is None or not isinstance(attr_call, ast.Call)
                or not isinstance(attr_call.func, ast.Attribute)
                or attr_call.func.attr != "pop" or attr_call.func.value is not node
                or len(attr_call.args) != 1
                or not isinstance(attr_call.args[0], ast.Name)
                or attr_call.args[0].id != "name"):
            return False
        if not isinstance(comprehension, ast.DictComp) or not isinstance(
                comprehension.generators[0].iter, (ast.Tuple, ast.List)):
            return False
        try:
            names = ast.literal_eval(comprehension.generators[0].iter)
        except (ValueError, TypeError):
            return False
        if (type(names) not in (tuple, list)
                or any(type(name) is not str for name in names)
                or "__name__" in names):
            return False
    return True


def _target_inspect_imported_name_safe(files):
    """Prove inspect's module-level globals access cannot replace __name__."""
    source = files.get("inspect.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != _INSPECT_SOURCE_SHA256):
        return False
    tree = ast.parse(source, filename="inspect.py")
    if any(isinstance(node, ast.Name) and node.id == "__name__"
           and isinstance(node.ctx, (ast.Store, ast.Del)) for node in ast.walk(tree)):
        return False
    parents = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
    module_globals_calls = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in {"exec", "eval", "globals", "locals", "vars"}):
            continue
        ancestor = node
        in_function = False
        while ancestor in parents:
            ancestor = parents[ancestor]
            if isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef)):
                in_function = True
                break
        if in_function:
            continue
        if node.func.id != "globals":
            return False
        module_globals_calls.append(node)
    if len(module_globals_calls) != 1:
        return False
    call = module_globals_calls[0]
    assignment = parents.get(call)
    if (not isinstance(assignment, ast.Assign) or len(assignment.targets) != 1
            or not isinstance(assignment.targets[0], ast.Name)
            or assignment.targets[0].id != "mod_dict"):
        return False
    module_name_writes = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Store)
        and isinstance(node.value, ast.Name) and node.value.id == "mod_dict"
        and isinstance(node.slice, ast.Constant) and node.slice.value == "__name__"
    ]
    if module_name_writes:
        return False
    compiler_flags_loop = [
        node for node in tree.body if isinstance(node, ast.For)
        and ast.unparse(node) == (
            "for k, v in dis.COMPILER_FLAG_NAMES.items():\n"
            "    mod_dict['CO_' + v] = k"
        )
    ]
    return len(compiler_flags_loop) == 1


def _target_sysconfig_imported_name_safe(files):
    """Resolve sysconfig's imported module name when dynamic access is deferred."""
    source = files.get("sysconfig.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256):
        return False
    tree = ast.parse(source, filename="sysconfig.py")
    if any(isinstance(node, ast.Name) and node.id == "__name__"
           and isinstance(node.ctx, (ast.Store, ast.Del)) for node in ast.walk(tree)):
        return False
    guards = [node for node in tree.body if isinstance(node, ast.If)
              and ast.unparse(node.test) == "__name__ == '__main__'"]
    if len(guards) != 1:
        return False
    parents = {child: parent for parent in ast.walk(tree)
               for child in ast.iter_child_nodes(parent)}
    dynamic_functions = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in {"exec", "eval", "globals", "locals", "vars"}):
            continue
        ancestor = node
        while ancestor in parents and not isinstance(
                parents[ancestor], (ast.FunctionDef, ast.AsyncFunctionDef)):
            ancestor = parents[ancestor]
        if (ancestor not in parents or not isinstance(
                parents[ancestor], (ast.FunctionDef, ast.AsyncFunctionDef))):
            return False
        dynamic_functions.add(parents[ancestor].name)
    guard_line = guards[0].lineno
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in dynamic_functions and node.lineno < guard_line):
            ancestor = node
            while ancestor in parents and not isinstance(
                    parents[ancestor], (ast.FunctionDef, ast.AsyncFunctionDef)):
                ancestor = parents[ancestor]
            if (ancestor not in parents or not isinstance(
                    parents[ancestor], (ast.FunctionDef, ast.AsyncFunctionDef))):
                return False
    return True


def _target_os_posix_name_facts(files, posix_source, clinic_source):
    """Bind os.name only when the pinned posix star export cannot replace it."""
    source = files.get("os.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != OS_SOURCE_SHA256
            or type(posix_source) is not bytes
            or hashlib.sha256(posix_source).hexdigest() != POSIX_MODULE_C_SHA256
            or type(clinic_source) is not bytes
            or hashlib.sha256(clinic_source).hexdigest() != POSIX_MODULE_CLINIC_SHA256
            or _TARGET_BUILTIN_MEMBERSHIP.get("posix") is not True
            or _TARGET_BUILTIN_MEMBERSHIP.get("nt") is not False):
        return {}
    tree = ast.parse(source, filename="os.py")
    sys_imports = [
        alias for statement in tree.body if isinstance(statement, ast.Import)
        for alias in statement.names if alias.name == "sys"
    ]
    if (len(sys_imports) != 1 or sys_imports[0].asname is not None
            or any(isinstance(node, ast.Name) and node.id == "sys"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(tree))):
        return {}
    names_assignments = [
        statement for statement in tree.body if isinstance(statement, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "_names"
                for target in statement.targets)
    ]
    selector = next((statement for statement in tree.body if isinstance(statement, ast.If)
                     and ast.unparse(statement.test) == "'posix' in _names"), None)
    alternate = selector.orelse[0] if selector and selector.orelse else None
    if (len(names_assignments) != 1
            or ast.unparse(names_assignments[0].value) != "sys.builtin_module_names"
            or not isinstance(alternate, ast.If)
            or ast.unparse(alternate.test) != "'nt' in _names"):
        return {}
    name_assignments = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id == "name"
        and isinstance(node.ctx, ast.Store)
    ]
    parents = {child: parent for parent in ast.walk(tree)
               for child in ast.iter_child_nodes(parent)}
    module_name_assignments = []
    for node in name_assignments:
        ancestor = node
        while ancestor in parents and not isinstance(
                parents[ancestor], (ast.FunctionDef, ast.AsyncFunctionDef)):
            ancestor = parents[ancestor]
        if not (ancestor in parents and isinstance(
                parents[ancestor], (ast.FunctionDef, ast.AsyncFunctionDef))):
            module_name_assignments.append(node)
    if len(module_name_assignments) != 2:
        return {}

    def assignment_value(block, expected):
        return any(isinstance(statement, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "name"
                           for target in statement.targets)
                   and isinstance(statement.value, ast.Constant)
                   and statement.value.value == expected
                   for statement in block)

    star_imports = [
        statement for statement in selector.body if isinstance(statement, ast.ImportFrom)
        and any(alias.name == "*" for alias in statement.names)
    ]
    if (not assignment_value(selector.body, "posix")
            or not assignment_value(alternate.body, "nt")
            or len(star_imports) != 1 or star_imports[0].module != "posix"
            or star_imports[0].level != 0):
        return {}
    posix_text = posix_source.decode("utf-8")
    clinic_text = clinic_source.decode("utf-8")
    if ("__all__" in posix_text or "__all__" in clinic_text
            or posix_text.count('"name"') != 1
            or not re.search(
                r'static PyMemberDef DirEntry_members\[\] = \{\s*\{"name",',
                posix_text,
            )
            or clinic_text.count('"name"') != 2
            or not re.search(
                r'static const char \* const _keywords\[\] = \{"name", "flags", NULL\};'
                r'\s*static _PyArg_Parser _parser = \{\s*\.keywords = _keywords,\s*'
                r'\.fname = "memfd_create"',
                clinic_text,
            )
            or not re.search(
                r'static const char \* const _keywords\[\] = \{"path", "name", NULL\};'
                r'\s*static _PyArg_Parser _parser = \{\s*\.keywords = _keywords,\s*'
                r'\.fname = "pathconf"',
                clinic_text,
            )
            or not re.search(r"static PyMethodDef posix_methods\[\] = \{", posix_text)
            or not re.search(r"\.m_methods = posix_methods", posix_text)):
        return {}
    return {"name": "posix"}


def _target_os_fspath_call_facts(files, posix_source, clinic_source):
    """Prove the Linux posix star export leaves os.fspath for the Python fallback."""
    source = files.get("os.py")
    if (not _target_os_posix_name_facts(files, posix_source, clinic_source)
            or type(source) is not bytes):
        return ()
    tree = ast.parse(source, filename="os.py")
    guard = [node for node in tree.body if isinstance(node, ast.If)
             and ast.unparse(node.test) == "not _exists('fspath')"]
    exists_functions = [node for node in tree.body
                        if isinstance(node, ast.FunctionDef) and node.name == "_exists"]
    if (len(guard) != 1 or len(exists_functions) != 1
            or ast.unparse(exists_functions[0].body[0]) != "return name in globals()"
            or any(isinstance(node, ast.Name) and node.id == "_exists"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(tree))):
        return ()
    if any(isinstance(node, ast.Name) and node.id == "fspath"
           and isinstance(node.ctx, ast.Store) and node.lineno < guard[0].lineno
           for node in ast.walk(tree)):
        return ()
    posix_text = posix_source.decode("utf-8")
    clinic_text = clinic_source.decode("utf-8")
    method_macro = "OS_FSPATH_METHODDEF"
    clinic_lines = clinic_text.splitlines()
    method_index = next((i for i, line in enumerate(clinic_lines)
                         if line.startswith(f"#define {method_macro}")), None)
    if (method_index is None or method_index + 1 >= len(clinic_lines)
            or '"fspath"' not in clinic_lines[method_index + 1]
            or not re.search(r"(?m)^\s*OS_FSPATH_METHODDEF$", posix_text)
            or not re.search(r"(?m)^static PyMethodDef posix_methods\[\] = \{", posix_text)
            or not re.search(r"\.m_methods = posix_methods", posix_text)):
        return ()
    return (("_exists('fspath')", True),)


def _target_os_posix_boolean_assignment_facts(files, posix_source, clinic_source):
    """Propagate a digest-bound os.name expression into its next guard."""
    source = files.get("os.py")
    if (not _target_os_posix_name_facts(files, posix_source, clinic_source)
            or type(source) is not bytes):
        return {}
    tree = ast.parse(source, filename="os.py")
    assignments = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name)
                and target.id == "supports_bytes_environ"
                for target in node.targets)
    ]
    if (len(assignments) != 1
            or ast.unparse(assignments[0].value) != "name != 'nt'"
            or not any(isinstance(node, ast.If)
                       and ast.unparse(node.test) == "supports_bytes_environ"
                       and node.lineno > assignments[0].lineno
                       for node in tree.body)
            or any(isinstance(node, ast.Name)
                   and node.id == "supports_bytes_environ"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   and node.lineno > assignments[0].lineno
                   for node in ast.walk(tree))):
        return {}
    return {"supports_bytes_environ": True}


def _target_os_have_functions_call_facts(files, posix_source, clinic_source):
    """Prove posixmodule_exec always publishes os.py's feature inventory."""
    source = files.get("os.py")
    if (not _target_os_posix_name_facts(files, posix_source, clinic_source)
            or type(source) is not bytes):
        return ()
    tree = ast.parse(source, filename="os.py")
    imports = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "posix"
        and any(alias.name == "_have_functions" and alias.asname is None
                for alias in node.names)
    ]
    if (len(imports) != 1
            or not any(isinstance(node, ast.If)
                       and ast.unparse(node.test) == "_exists('_have_functions')"
                       for node in tree.body)
            or not any(isinstance(node, ast.FunctionDef) and node.name == "_exists"
                       and ast.unparse(node.body[0]) == "return name in globals()"
                       for node in tree.body)):
        return ()
    posix_text = posix_source.decode("utf-8")
    if (not re.search(
            r"(?s)static int\s+posixmodule_exec\(PyObject \*m\)\s*\{.*?"
            r'return _PyModule_Add\(m, "_have_functions", list\);\s*\}',
            posix_text,
        )
            or not re.search(r"\{Py_mod_exec, posixmodule_exec\}", posix_text)
            or not re.search(r"\.m_slots = posixmodile_slots", posix_text)):
        return ()
    return (("_exists('_have_functions')", True),)


def _target_posix_build_call_facts(files, posix_source, clinic_source,
                                  pyconfig_source):
    """Bind compile-time posix methods to the selected image's pyconfig.h."""
    if (type(pyconfig_source) is not bytes
            or len(pyconfig_source) > MAX_TARGET_PYCONFIG_BYTES
            or hashlib.sha256(pyconfig_source).hexdigest() != TARGET_PYCONFIG_SHA256
            or type(posix_source) is not bytes
            or hashlib.sha256(posix_source).hexdigest() != POSIX_MODULE_C_SHA256
            or type(clinic_source) is not bytes
            or hashlib.sha256(clinic_source).hexdigest() != POSIX_MODULE_CLINIC_SHA256
            or _target_os_have_functions_call_facts(
                files, posix_source, clinic_source
            ) != (("_exists('_have_functions')", True),)):
        return ()
    config_text = pyconfig_source.decode("ascii")
    config = set(re.findall(r"(?m)^#define (HAVE_[A-Z0-9_]+) 1$", config_text))
    c_text = posix_source.decode("utf-8")
    clinic_text = clinic_source.decode("utf-8")
    method_table = re.search(
        r"(?s)static PyMethodDef posix_methods\[\] = \{(.*?)\n\};",
        c_text,
    )
    if (method_table is None
            or not re.search(r"\.m_methods = posix_methods", c_text)):
        return ()
    table = method_table.group(1)

    def guarded_method(feature_condition, macro, exported_name):
        return bool(
            re.search(
                r"(?s)#if " + feature_condition + r".*?#define " + macro
                + r"\s+\\\s*\{\s*\"" + re.escape(exported_name) + r"\"",
                clinic_text,
            )
            and re.search(r"(?m)^\s*" + macro + r"\s*$", table)
        )

    facts = []
    have_statvfs = (
        "HAVE_STATVFS" in config and "HAVE_SYS_STATVFS_H" in config
        and guarded_method(
            r"\(defined\(HAVE_STATVFS\) && defined\(HAVE_SYS_STATVFS_H\)\)",
            "OS_STATVFS_METHODDEF", "statvfs",
        )
    )
    have_fstatvfs = (
        "HAVE_FSTATVFS" in config and "HAVE_SYS_STATVFS_H" in config
        and guarded_method(
            r"\(defined\(HAVE_FSTATVFS\) && defined\(HAVE_SYS_STATVFS_H\)\)",
            "OS_FSTATVFS_METHODDEF", "fstatvfs",
        )
    )
    have_lchown = (
        "HAVE_LCHOWN" in config
        and guarded_method(r"defined\(HAVE_LCHOWN\)",
                           "OS_LCHOWN_METHODDEF", "lchown")
    )
    have_fork = (
        "HAVE_FORK" in config
        and guarded_method(r"defined\(HAVE_FORK\)",
                           "OS_REGISTER_AT_FORK_METHODDEF", "register_at_fork")
        and guarded_method(r"defined\(HAVE_FORK\)",
                           "OS_FORK_METHODDEF", "fork")
    )
    have_execv = (
        "HAVE_EXECV" in config
        and guarded_method(r"defined\(HAVE_EXECV\)",
                           "OS_EXECV_METHODDEF", "execv")
    )
    spawnv_features = {"HAVE_SPAWNV", "HAVE_WSPAWNV", "HAVE_RTPSPAWN"}
    spawnv_enabled = bool(config & spawnv_features)
    spawnv_method_guarded = guarded_method(
        r"\(defined\(HAVE_SPAWNV\) \|\| defined\(HAVE_WSPAWNV\) \|\| "
        r"defined\(HAVE_RTPSPAWN\)\)", "OS_SPAWNV_METHODDEF", "spawnv"
    )
    have_spawnv = spawnv_enabled and spawnv_method_guarded
    if have_statvfs and have_fstatvfs:
        facts.append(("_exists('statvfs') and _exists('fstatvfs')", True))
    if have_lchown:
        facts.append(("_exists('lchown')", True))
    if have_fork:
        facts.extend((
            ("hasattr(os, 'register_at_fork')", True),
            ("_exists('fork')", True),
        ))
    if have_execv:
        facts.append(("_exists('execv')", True))
    if not spawnv_enabled and spawnv_method_guarded:
        facts.append(("_exists('spawnv')", False))
    if (b"spawnvp" not in posix_source
            and b"spawnvp" not in clinic_source):
        facts.append(("_exists('spawnvp')", False))
    if have_fork and not have_spawnv and have_execv:
        facts.append((
            "_exists('fork') and (not _exists('spawnv')) and _exists('execv')",
            True,
        ))
    return tuple(sorted(facts))


def _target_os_descriptor_support_facts(files, posix_source, clinic_source,
                                        pyconfig_source):
    """Resolve os.fwalk's descriptor guard from the pinned Linux build inputs."""
    source = files.get("os.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != OS_SOURCE_SHA256
            or type(pyconfig_source) is not bytes
            or len(pyconfig_source) > MAX_TARGET_PYCONFIG_BYTES
            or hashlib.sha256(pyconfig_source).hexdigest() != TARGET_PYCONFIG_SHA256
            or type(posix_source) is not bytes
            or hashlib.sha256(posix_source).hexdigest() != POSIX_MODULE_C_SHA256
            or type(clinic_source) is not bytes
            or hashlib.sha256(clinic_source).hexdigest() != POSIX_MODULE_CLINIC_SHA256
            or _target_os_have_functions_call_facts(
                files, posix_source, clinic_source
            ) != (("_exists('_have_functions')", True),)):
        return ()

    tree = ast.parse(source, filename="os.py")
    guard = [node for node in tree.body if isinstance(node, ast.If)
             and ast.unparse(node.test)
             == "{open, stat} <= supports_dir_fd and {scandir, stat} <= supports_fd"]
    if len(guard) != 1:
        return ()

    required_os_facts = {
        "_add('HAVE_OPENAT', 'open')",
        "_add('HAVE_FSTATAT', 'stat')",
        "_add('HAVE_FDOPENDIR', 'scandir')",
        "_set.add(stat)",
        "supports_dir_fd = _set",
        "supports_fd = _set",
    }
    observed_os_facts = {
        ast.unparse(node) for node in ast.walk(tree)
        if isinstance(node, (ast.Expr, ast.Assign))
    }
    if not required_os_facts <= observed_os_facts:
        return ()

    config_text = pyconfig_source.decode("ascii")
    config = set(re.findall(r"(?m)^#define (HAVE_[A-Z0-9_]+) 1$", config_text))
    required_config = {"HAVE_OPENAT", "HAVE_FSTATAT", "HAVE_FDOPENDIR"}
    if not required_config <= config:
        return ()

    c_text = posix_source.decode("utf-8")
    clinic_text = clinic_source.decode("utf-8")
    method_table = re.search(
        r"(?s)static PyMethodDef posix_methods\[\] = \{(.*?)\n\};", c_text
    )
    if method_table is None or not re.search(r"\.m_methods = posix_methods", c_text):
        return ()
    table = method_table.group(1)
    if any(not re.search(r"(?m)^\s*" + macro + r"\s*$", table)
           for macro in ("OS_OPEN_METHODDEF", "OS_STAT_METHODDEF", "OS_SCANDIR_METHODDEF")):
        return ()
    if any(macro not in clinic_text or '{"' + name + '"' not in clinic_text
           for macro, name in (("OS_OPEN_METHODDEF", "open"),
                               ("OS_STAT_METHODDEF", "stat"),
                               ("OS_SCANDIR_METHODDEF", "scandir"))):
        return ()

    if not re.search(
            r"(?s)#else\s+#  define HAVE_FSTATAT_RUNTIME 1.*?"
            r"#  define HAVE_FDOPENDIR_RUNTIME 1.*?"
            r"#  define HAVE_OPENAT_RUNTIME 1.*?#endif",
            c_text):
        return ()
    probes = (
        ('"HAVE_OPENAT", probe_openat', "HAVE_OPENAT_RUNTIME"),
        ('"HAVE_FSTATAT", probe_fstatat', "HAVE_FSTATAT_RUNTIME"),
        ('"HAVE_FDOPENDIR", probe_fdopendir', "HAVE_FDOPENDIR_RUNTIME"),
    )
    for row, probe in probes:
        if row not in c_text or probe not in c_text:
            return ()
    return (("{open, stat} <= supports_dir_fd and {scandir, stat} <= supports_fd", True),)


def _target_threading_os_alias_facts(files):
    """Carry the proven os.register_at_fork method through threading's alias."""
    source = files.get("threading.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != THREADING_SOURCE_SHA256):
        return ()
    tree = ast.parse(source, filename="threading.py")
    aliases = [alias for node in tree.body if isinstance(node, ast.Import)
               for alias in node.names if alias.name == "os" and alias.asname == "_os"]
    if (len(aliases) != 1
            or any(isinstance(node, ast.Name) and node.id == "_os"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(tree))):
        return ()
    return (("hasattr(_os, 'register_at_fork')", True),)


def _target_threading_native_id_name_facts(
        files, header_source, module_source, pthread_source, pyconfig_source):
    """Bind threading's native-id flag to the pinned Linux CPython build path."""
    if (_TARGET_BUILTIN_MEMBERSHIP.get("_thread") is not True
            or type(pyconfig_source) is not bytes
            or hashlib.sha256(pyconfig_source).hexdigest() != TARGET_PYCONFIG_SHA256):
        return {}
    sources = (
        (header_source, THREAD_NATIVE_ID_HEADER_SHA256),
        (module_source, THREAD_NATIVE_ID_MODULE_SHA256),
        (pthread_source, THREAD_NATIVE_ID_PTHREAD_SHA256),
    )
    if any(type(source) is not bytes or hashlib.sha256(source).hexdigest() != expected
           for source, expected in sources):
        return {}
    header = header_source.decode("utf-8")
    module = module_source.decode("utf-8")
    pthread = pthread_source.decode("utf-8")
    threading_source = files.get("threading.py")
    if (type(threading_source) is not bytes
            or hashlib.sha256(threading_source).hexdigest() != THREADING_SOURCE_SHA256
            or not re.search(
                r"(?s)#if \(defined\(__APPLE__\) \|\| defined\(__linux__\).*?"
                r"#define PY_HAVE_THREAD_NATIVE_ID",
                header,
            )
            or not re.search(
                r"(?s)#ifdef PY_HAVE_THREAD_NATIVE_ID.*?thread_get_native_id.*?"
                r"#endif",
                module,
            )
            or not re.search(
                r"(?s)#ifdef PY_HAVE_THREAD_NATIVE_ID\s*\{\"get_native_id\",\s*"
                r"thread_get_native_id,.*?#endif",
                module,
            )
            or "PyThread_get_thread_native_id" not in pthread):
        return {}
    tree = ast.parse(threading_source, filename="threading.py")
    native_id_tries = [node for node in tree.body if isinstance(node, ast.Try)
                       and any(isinstance(statement, ast.Assign)
                               and any(isinstance(target, ast.Name)
                                       and target.id == "get_native_id"
                                       for target in statement.targets)
                               for statement in node.body)]
    if (len(native_id_tries) != 1
            or not any(isinstance(statement, ast.Assign)
                       and any(isinstance(target, ast.Name)
                               and target.id == "_HAVE_THREAD_NATIVE_ID"
                               for target in statement.targets)
                       and isinstance(statement.value, ast.Constant)
                       and statement.value.value is True
                       for statement in native_id_tries[0].body)
            or not any(isinstance(handler.type, ast.Name)
                       and handler.type.id == "AttributeError"
                       and any(isinstance(statement, ast.Assign)
                               and any(isinstance(target, ast.Name)
                                       and target.id == "_HAVE_THREAD_NATIVE_ID"
                                       for target in statement.targets)
                               and isinstance(statement.value, ast.Constant)
                               and statement.value.value is False
                               for statement in handler.body)
                       for handler in native_id_tries[0].handlers)):
        return {}
    return {"_HAVE_THREAD_NATIVE_ID": True}


def _target_sysconfig_user_base_name_facts(files):
    """Prove `_HAS_USER_BASE` for the pinned Linux source branch."""
    source = files.get("sysconfig.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256):
        return {}
    tree = ast.parse(source, filename="sysconfig.py")
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "_getuserbase"]
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name)
                           and target.id == "_HAS_USER_BASE"
                           for target in node.targets)]
    if len(functions) != 1 or len(assignments) != 1:
        return {}
    function = functions[0]
    platform_exclusions = [node for node in ast.walk(function)
                           if isinstance(node, ast.If)
                           and ast.unparse(node.test)
                           == "sys.platform in {'emscripten', 'vxworks', 'wasi'}"]
    nested_joiners = [node for node in function.body
                      if isinstance(node, ast.FunctionDef) and node.name == "joinuser"]
    final_userbase_returns = [node for node in function.body
                              if isinstance(node, ast.Return)
                              and isinstance(node.value, ast.Call)
                              and isinstance(node.value.func, ast.Name)
                              and node.value.func.id == "joinuser"
                              and [ast.literal_eval(arg) for arg in node.value.args
                                   if isinstance(arg, ast.Constant)] == ["~", ".local"]]
    if (len(platform_exclusions) != 1 or len(nested_joiners) != 1
            or len(final_userbase_returns) != 1
            or ast.unparse(nested_joiners[0].body[0].value)
            != "os.path.expanduser(os.path.join(*args))"
            or ast.unparse(assignments[0].value)
            != "_getuserbase() is not None"
            or not any(isinstance(node, ast.Return)
                       and isinstance(node.value, ast.Constant)
                       and node.value.value is None
                       for node in platform_exclusions[0].body)):
        return {}
    return {"_HAS_USER_BASE": True}


def _target_sysconfig_no_site_facts(files, sys_module_c_source, no_site):
    """Resolve the venv-only sys._home branch under the explicit -S assumption."""
    source = files.get("sysconfig.py")
    site_source = files.get("site.py")
    if (no_site is not True
            or type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256
            or type(site_source) is not bytes
            or hashlib.sha256(site_source).hexdigest() != SITE_SOURCE_SHA256
            or type(sys_module_c_source) is not bytes
            or hashlib.sha256(sys_module_c_source).hexdigest() != SYS_MODULE_C_SHA256):
        return {}

    sysconfig_tree = ast.parse(source, filename="sysconfig.py")
    home_reads = [node for node in sysconfig_tree.body if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == "_sys_home"
                          for target in node.targets)]
    home_guards = [node for node in sysconfig_tree.body if isinstance(node, ast.If)
                   and ast.unparse(node.test) == "_sys_home"]
    if (len(home_reads) != 1 or len(home_guards) != 1
            or ast.unparse(home_reads[0].value) != "getattr(sys, '_home', None)"
            or not any(isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name)
                               and target.id == "_PROJECT_BASE"
                               for target in node.targets)
                       for node in home_guards[0].body)):
        return {}

    # Under -S, site.py is not imported. Fail closed if another library source
    # mentions the private field or the sys C module exposes the name.
    sys_home_forms = (b"sys._home", b"setattr(sys, '_home'",
                      b'setattr(sys, "_home"')
    for name, data in files.items():
        if (name not in ("site.py", "sysconfig.py")
                and any(form in data for form in sys_home_forms)):
            return {}
    if b"_home" in sys_module_c_source:
        return {}
    site_tree = ast.parse(site_source, filename="site.py")
    home_writes = [node for node in ast.walk(site_tree)
                   if isinstance(node, ast.Attribute) and node.attr == "_home"
                   and isinstance(node.ctx, ast.Store)]
    if (len(home_writes) != 2
            or any(not isinstance(node.value, ast.Name) or node.value.id != "sys"
                   for node in home_writes)):
        return {}
    return {"_sys_home": False}


def _target_sysconfig_project_base_env_facts(files, image_config_source,
                                             no_project_base_override):
    """Bind the direct os.environ guard to the pinned image ENV and call assumption."""
    source = files.get("sysconfig.py")
    if (no_project_base_override is not True
            or type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256
            or type(image_config_source) is not bytes
            or len(image_config_source) > MAX_TARGET_IMAGE_CONFIG_BYTES
            or hashlib.sha256(image_config_source).hexdigest()
            != TARGET_IMAGE_CONFIG_SHA256):
        return ()
    tree = ast.parse(source, filename="sysconfig.py")
    guards = [node for node in tree.body if isinstance(node, ast.If)
              and ast.unparse(node.test)
              == "'_PYTHON_PROJECT_BASE' in os.environ"]
    if len(guards) != 1:
        return ()
    config = json.loads(image_config_source)
    if (type(config) is not dict or config.get("os") != "linux"
            or config.get("architecture") != "amd64"):
        return ()
    runtime_config = config.get("config")
    env = runtime_config.get("Env") if type(runtime_config) is dict else None
    if (type(env) is not list or any(type(item) is not str for item in env)
            or any(item.partition("=")[0] == "_PYTHON_PROJECT_BASE" for item in env)):
        return ()
    return (("'_PYTHON_PROJECT_BASE' in os.environ", False),)


class _DigestReader:
    """Hash a sequential tar stream without buffering the image layer."""

    def __init__(self, source):
        self.source = source
        self.digest = hashlib.sha256()

    def read(self, size=-1):
        data = self.source.read(size)
        self.digest.update(data)
        return data


def _target_image_save_facts(image_save_path, image_config_source):
    """Verify the pinned Docker-save layers and inspect the final executable paths."""
    if image_config_source is None:
        raise ValueError("TARGET_IMAGE_CONFIG_REQUIRED")
    path = Path(image_save_path)
    if path.stat().st_size > MAX_TARGET_IMAGE_SAVE_BYTES:
        raise ValueError("TARGET_IMAGE_SAVE_LIMIT")
    try:
        with tarfile.open(path, "r:") as outer:
            manifest_info = outer.getmember("manifest.json")
            if manifest_info.size > MAX_TARGET_IMAGE_CONFIG_BYTES:
                raise ValueError("TARGET_IMAGE_SAVE_MANIFEST_LIMIT")
            manifest_member = outer.extractfile(manifest_info)
            manifest_bytes = manifest_member.read(MAX_TARGET_IMAGE_CONFIG_BYTES + 1)
            manifest = json.loads(manifest_bytes)
            if (type(manifest) is not list or len(manifest) != 1
                    or type(manifest[0]) is not dict):
                raise ValueError("TARGET_IMAGE_SAVE_MANIFEST")
            entry = manifest[0]
            config_name = entry.get("Config")
            layers = entry.get("Layers")
            if (config_name != "blobs/sha256/" + TARGET_IMAGE_CONFIG_SHA256
                    or type(layers) is not list or len(layers) != len(TARGET_IMAGE_LAYER_NAMES)
                    or any(layer != "blobs/sha256/" + digest
                           for layer, digest in zip(layers, TARGET_IMAGE_LAYER_NAMES))):
                raise ValueError("TARGET_IMAGE_SAVE_BINDING")
            index_info = outer.getmember("index.json")
            if index_info.size > MAX_TARGET_IMAGE_CONFIG_BYTES:
                raise ValueError("TARGET_IMAGE_SAVE_INDEX_LIMIT")
            index = json.loads(outer.extractfile(index_info).read(
                MAX_TARGET_IMAGE_CONFIG_BYTES + 1
            ))
            descriptors = index.get("manifests") if type(index) is dict else None
            expected_manifest_digest = "sha256:" + TARGET_IMAGE_MANIFEST_SHA256
            if (type(descriptors) is not list or len(descriptors) != 1
                    or type(descriptors[0]) is not dict
                    or descriptors[0].get("digest") != expected_manifest_digest):
                raise ValueError("TARGET_IMAGE_SAVE_INDEX_BINDING")
            image_manifest_name = "blobs/sha256/" + TARGET_IMAGE_MANIFEST_SHA256
            image_manifest_info = outer.getmember(image_manifest_name)
            if (image_manifest_info.size > MAX_TARGET_IMAGE_CONFIG_BYTES * 4
                    or image_manifest_info.size != descriptors[0].get("size")):
                raise ValueError("TARGET_IMAGE_SAVE_MANIFEST_LIMIT")
            image_manifest_bytes = outer.extractfile(image_manifest_info).read(
                MAX_TARGET_IMAGE_CONFIG_BYTES * 4 + 1
            )
            if hashlib.sha256(image_manifest_bytes).hexdigest() != TARGET_IMAGE_MANIFEST_SHA256:
                raise ValueError("TARGET_IMAGE_SAVE_MANIFEST_DIGEST")
            image_manifest = json.loads(image_manifest_bytes)
            config_descriptor = image_manifest.get("config")
            layer_descriptors = image_manifest.get("layers")
            if (type(config_descriptor) is not dict
                    or config_descriptor.get("digest")
                    != "sha256:" + TARGET_IMAGE_CONFIG_SHA256
                    or type(layer_descriptors) is not list
                    or len(layer_descriptors) != len(TARGET_IMAGE_LAYER_NAMES)
                    or any(type(descriptor) is not dict
                           or descriptor.get("digest") != "sha256:" + expected
                           or descriptor.get("mediaType")
                           != "application/vnd.oci.image.layer.v1.tar+gzip"
                           or descriptor.get("size") != outer.getmember(layer_name).size
                           for descriptor, expected, layer_name in zip(
                               layer_descriptors, TARGET_IMAGE_LAYER_NAMES, layers
                           ))):
                raise ValueError("TARGET_IMAGE_SAVE_OCI_MANIFEST_BINDING")
            config_info = outer.getmember(config_name)
            if config_info.size > MAX_TARGET_IMAGE_CONFIG_BYTES:
                raise ValueError("TARGET_IMAGE_SAVE_CONFIG_LIMIT")
            config_member = outer.extractfile(config_info)
            config_bytes = config_member.read(MAX_TARGET_IMAGE_CONFIG_BYTES + 1)
            if (len(config_bytes) > MAX_TARGET_IMAGE_CONFIG_BYTES
                    or hashlib.sha256(config_bytes).hexdigest() != TARGET_IMAGE_CONFIG_SHA256
                    or config_bytes != image_config_source):
                raise ValueError("TARGET_IMAGE_SAVE_CONFIG_MISMATCH")
            config = json.loads(config_bytes)
            rootfs = config.get("rootfs") if type(config) is dict else None
            diff_ids = rootfs.get("diff_ids") if type(rootfs) is dict else None
            if (type(diff_ids) is not list or len(diff_ids) != len(layers)
                    or any(type(item) is not str or not re.fullmatch(r"sha256:[0-9a-f]{64}", item)
                           for item in diff_ids)):
                raise ValueError("TARGET_IMAGE_SAVE_DIFF_IDS")

            tracked = {
                TARGET_EXECUTABLE_PATH: None,
                "usr/local/bin/python3": None,
                "usr/local/bin/Modules/Setup": None,
                "usr/local/bin/Modules/Setup.local": None,
            }
            for layer_name, expected_diff_id in zip(layers, diff_ids):
                compressed_reader = _DigestReader(outer.extractfile(layer_name))
                uncompressed_reader = _DigestReader(gzip.GzipFile(fileobj=compressed_reader))
                whiteouts = []
                additions = []
                with tarfile.open(fileobj=uncompressed_reader, mode="r|") as layer:
                    for member in layer:
                        name = member.name.lstrip("./").rstrip("/")
                        if not name:
                            continue
                        parent, _, basename = name.rpartition("/")
                        if basename == ".wh..wh..opq":
                            whiteouts.append((parent, True))
                        elif basename.startswith(".wh."):
                            whiteouts.append((parent + "/" + basename[4:], False))
                        elif name in tracked:
                            content_sha256 = None
                            if member.isfile() and name in (TARGET_EXECUTABLE_PATH,):
                                stream = layer.extractfile(member)
                                content_digest = hashlib.sha256()
                                while True:
                                    chunk = stream.read(1024 * 1024)
                                    if not chunk:
                                        break
                                    content_digest.update(chunk)
                                content_sha256 = content_digest.hexdigest()
                            additions.append((name, {
                                "file": member.isfile(), "symlink": member.issym(),
                                "linkname": member.linkname if member.issym() else None,
                                "mode": member.mode & 0o777,
                                "sha256": content_sha256,
                            }))
                if ("sha256:" + compressed_reader.digest.hexdigest()
                        != "sha256:" + layer_name.rsplit("/", 1)[-1]
                        or "sha256:" + uncompressed_reader.digest.hexdigest()
                        != expected_diff_id):
                    raise ValueError("TARGET_IMAGE_SAVE_LAYER_DIFF_ID")
                for target in tracked:
                    parts = target.split("/")
                    ancestors = ["/".join(parts[:index]) for index in range(1, len(parts))]
                    removed = False
                    for parent, opaque in whiteouts:
                        if (opaque and parent in ancestors
                                or not opaque and (parent == target
                                    or target.startswith(parent + "/"))):
                            removed = True
                            break
                    if removed:
                        tracked[target] = None
                for name, facts in additions:
                    tracked[name] = facts
            executable = tracked[TARGET_EXECUTABLE_PATH]
            if (executable != {"file": True, "symlink": False, "linkname": None,
                               "mode": 0o755, "sha256": TARGET_EXECUTABLE_SHA256}
                    or tracked["usr/local/bin/python3"] != {
                        "file": False, "symlink": True, "linkname": "python3.12",
                        "mode": 0o777, "sha256": None,
                    }
                    or tracked["usr/local/bin/Modules/Setup"] is not None
                    or tracked["usr/local/bin/Modules/Setup.local"] is not None):
                raise ValueError("TARGET_IMAGE_SAVE_PATH_FACTS")
    except (tarfile.TarError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("TARGET_IMAGE_SAVE_INVALID") from error
    return {
        "executable_path_candidate": "/usr/local/bin/python3.12",
        "_PYTHON_BUILD": False,
    }


def _target_condition(node, known_names=None, known_call_facts=None):
    """Resolve only fixed, side-effect-free target platform predicates."""
    target = {
        "sys.platform": "linux",
        "os.name": "posix",
        "sys.version_info": (3, 12, 16, "final", 0),
        "sys.implementation.name": "cpython",
        "sys.byteorder": "little",
        "sys.builtin_module_names": _KNOWN_BUILTIN_NAMES,
    }
    known_names = known_names or {}
    known_call_facts = known_call_facts or ()
    expression = ast.unparse(node)
    for fact_expression, fact_value in known_call_facts:
        if expression == fact_expression:
            return fact_value

    def value(expr):
        if isinstance(expr, ast.Call):
            expression = ast.unparse(expr)
            for fact_expression, fact_value in known_call_facts:
                if expression == fact_expression:
                    return fact_value
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
            known = known_names.get(expr.id, _UNKNOWN)
            if (type(known) is tuple and len(known) == 2
                    and known[0] is _STATIC_FALSE_LITERAL):
                return False
            return known
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
                        if (current is _IMPORTED_MODULE_NAME
                                or right is _IMPORTED_MODULE_NAME):
                            other = right if current is _IMPORTED_MODULE_NAME else current
                            if type(other) is not str or other != "__main__":
                                return _UNKNOWN
                            matched = False
                        elif current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        else:
                            matched = current == right
                    elif isinstance(op, ast.Is):
                        if (current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES
                                or current is _IMPORTED_MODULE_NAME
                                or right is _IMPORTED_MODULE_NAME):
                            return _UNKNOWN
                        if (current is not None and type(current) is not bool
                                or right is not None and type(right) is not bool):
                            return _UNKNOWN
                        matched = current is right
                    elif isinstance(op, ast.NotEq):
                        if (current is _IMPORTED_MODULE_NAME
                                or right is _IMPORTED_MODULE_NAME):
                            other = right if current is _IMPORTED_MODULE_NAME else current
                            if type(other) is not str or other != "__main__":
                                return _UNKNOWN
                            matched = True
                        elif current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        else:
                            matched = current != right
                    elif isinstance(op, ast.IsNot):
                        if (current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES
                                or current is _IMPORTED_MODULE_NAME
                                or right is _IMPORTED_MODULE_NAME):
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


def _target_name_aliases(tree, *, imported_module_name=False):
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
    known = {}
    module_name_aliases = {"__name__"} if imported_module_name else set()
    literal_false_aliases = set()
    first_load = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            position = (node.lineno, node.col_offset)
            first_load[node.id] = min(first_load.get(node.id, position), position)
    deletes_module_name = any(
        isinstance(node, ast.Name) and node.id == "__name__"
        and isinstance(node.ctx, ast.Del)
        for node in ast.walk(tree)
    )
    dynamic_namespace_access = any(
        (isinstance(node, ast.Name) and node.id in {
            "exec", "eval", "globals", "locals", "vars",
        })
        or (isinstance(node, ast.alias) and node.name in {
            "exec", "eval", "globals", "locals", "vars",
        })
        or (isinstance(node, ast.Attribute) and node.attr in {
            "exec", "eval", "globals", "locals", "vars",
        })
        for node in ast.walk(tree)
    )
    if (imported_module_name and bindings.get("__name__", 0) == 0
            and not deletes_module_name and not dynamic_namespace_access):
        known["__name__"] = _IMPORTED_MODULE_NAME
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            value = statement.value
            mapped = (_KNOWN_BUILTIN_NAMES
                      if isinstance(value, ast.Attribute)
                      and ast.unparse(value) == "sys.builtin_module_names"
                      else False if isinstance(value, ast.Constant)
                      and type(value.value) is int and value.value == 0
                      else known.get(value.id, _UNKNOWN) if isinstance(value, ast.Name) else _UNKNOWN)
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    if (target.id == "__name__"
                            or isinstance(value, ast.Name)
                            and value.id in module_name_aliases):
                        module_name_aliases.add(target.id)
                    else:
                        module_name_aliases.discard(target.id)
                    if mapped is _UNKNOWN:
                        known.pop(target.id, None)
                    else:
                        if (mapped is False and target.id != "_false"
                                or target.id == "_false"
                                and first_load.get(target.id, (float("inf"), 0))
                                < (statement.lineno, statement.col_offset)):
                            known.pop(target.id, None)
                        else:
                            known[target.id] = (
                                (_STATIC_FALSE_LITERAL, statement.lineno)
                                if target.id == "_false" and mapped is False
                                else mapped
                            )
                            if target.id == "_false" and mapped is False:
                                literal_false_aliases.add(target.id)
        elif isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            value = statement.value
            if (statement.target.id == "__name__"
                    or isinstance(value, ast.Name)
                    and value.id in module_name_aliases):
                module_name_aliases.add(statement.target.id)
            else:
                module_name_aliases.discard(statement.target.id)
            mapped = (_KNOWN_BUILTIN_NAMES
                      if isinstance(value, ast.Attribute)
                      and ast.unparse(value) == "sys.builtin_module_names"
                      else known.get(value.id, _UNKNOWN) if isinstance(value, ast.Name) else _UNKNOWN)
            if mapped is _UNKNOWN:
                known.pop(statement.target.id, None)
            else:
                known[statement.target.id] = mapped
    if dynamic_namespace_access:
        for name in module_name_aliases:
            known.pop(name, None)
        for name in literal_false_aliases:
            known.pop(name, None)
    return {
        name: value for name, value in known.items()
        if bindings.get(name) == 1
        or (name == "__name__" and value is _IMPORTED_MODULE_NAME
            and bindings.get(name, 0) == 0)
    }


def _module_body_import_names(
        tree, module, path, target_platform=False, condition_stats=None, known_names=None,
        unknown_conditions=None, known_call_facts=None, preserve_imported_name=False,
        preserve_name_facts=False):
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
                after_star_false = {
                    name: value for name, value in known_names.items()
                    if (type(value) is tuple and len(value) == 2
                        and value[0] is _STATIC_FALSE_LITERAL
                        and value[1] > node.lineno)
                }
                if (preserve_imported_name
                        and known_names.get("__name__") is _IMPORTED_MODULE_NAME):
                    after_star_false["__name__"] = _IMPORTED_MODULE_NAME
                if (preserve_name_facts
                        and known_names.get("name") == "posix"):
                    after_star_false["name"] = "posix"
                if (module == "os"
                        and known_names.get("supports_bytes_environ") is True):
                    after_star_false["supports_bytes_environ"] = True
                known_names.clear()
                known_names.update(after_star_false)
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
            decision = _target_condition(node.test, known_names, known_call_facts)
            if condition_stats is not None:
                key = "resolved" if decision is not None else "unknown"
                condition_stats[key] += 1
            if decision is None and unknown_conditions is not None:
                unknown_conditions.append({
                    "module": module,
                    "source_path": path,
                    "line": node.lineno,
                    "expression": ast.unparse(node.test),
                })
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


def _target_platform_candidate_closure(
        files, roots=ROOTS, unknown_conditions=None, known_call_facts=None,
        known_name_facts=None, preserve_imported_name_modules=()):
    if type(files) is not dict or type(roots) is not tuple:
        raise ValueError("SOURCE_INPUT_TYPE")
    if unknown_conditions is not None and type(unknown_conditions) is not list:
        raise ValueError("CONDITION_INVENTORY_TYPE")
    if (known_call_facts is not None and (
            type(known_call_facts) is not tuple
            or any(type(fact) is not tuple or len(fact) != 2
                   or type(fact[0]) is not str or type(fact[1]) is not bool
                   for fact in known_call_facts))):
        raise ValueError("CONDITION_FACTS_TYPE")
    if (known_name_facts is not None and (
            type(known_name_facts) is not dict
            or any(type(module) is not str or type(facts) is not dict
                   or any(type(name) is not str or type(value) not in (str, bool, int)
                          for name, value in facts.items())
                   for module, facts in known_name_facts.items()))):
        raise ValueError("CONDITION_NAME_FACTS_TYPE")
    if (type(preserve_imported_name_modules) is not tuple
            or any(type(module) is not str for module in preserve_imported_name_modules)):
        raise ValueError("CONDITION_MODULE_NAME_FACTS_TYPE")
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
        aliases = _target_name_aliases(tree, imported_module_name=True)
        if module == "importlib._bootstrap_external":
            aliases.update(_target_importlib_windows_name_facts(files))
        elif module == "warnings":
            aliases.update((known_name_facts or {}).get(module, {}))
        elif module == "os":
            aliases.update((known_name_facts or {}).get(module, {}))
        elif module == "threading":
            aliases.update((known_name_facts or {}).get(module, {}))
        elif module == "sysconfig":
            aliases.update((known_name_facts or {}).get(module, {}))
        preserve_imported_name = (
            module in preserve_imported_name_modules
            or _target_imported_name_star_imports_safe(files, module)
        )
        if (preserve_imported_name and module in {"ast", "inspect", "sysconfig"}
                and aliases.get("__name__") is not _IMPORTED_MODULE_NAME):
            aliases["__name__"] = _IMPORTED_MODULE_NAME
        for name in _module_body_import_names(
                tree, module, path, target_platform=True, condition_stats=condition_stats,
                known_names=aliases, unknown_conditions=unknown_conditions,
                known_call_facts=known_call_facts,
                preserve_imported_name=preserve_imported_name,
                preserve_name_facts=(module in preserve_imported_name_modules)):
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
    if unknown_conditions is not None:
        unknown_conditions.sort(
            key=lambda row: (
                row["module"], row["source_path"], row["line"], row["expression"]
            )
        )
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


def analyze(archive_path, target_pyconfig_path=None, target_no_site=False,
            target_image_config_path=None, target_no_project_base_override=False,
            target_image_save_path=None, target_direct_python312=False):
    (files, stdlib_header, frozen_source, bootstrap_setup, stdlib_setup,
     getpath_source, config_c_template, configure_source, ast_asdl, ast_c_source,
     sys_module_c_source, sys_module_clinic_source, warnings_c_source,
     warnings_clinic_source, posix_module_c_source,
     posix_module_clinic_source, thread_native_id_header,
     thread_native_id_module, thread_native_id_pthread) = _source_archive_data(
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
    sysconfig_name_facts = _target_sysconfig_user_base_name_facts(files)
    sysconfig_name_facts.update(_target_sysconfig_no_site_facts(
        files, sys_module_c_source, target_no_site,
    ))
    target_image_config_source = None
    if target_image_config_path is not None:
        with Path(target_image_config_path).open("rb") as stream:
            target_image_config_source = stream.read(MAX_TARGET_IMAGE_CONFIG_BYTES + 1)
        if (len(target_image_config_source) > MAX_TARGET_IMAGE_CONFIG_BYTES
                or hashlib.sha256(target_image_config_source).hexdigest()
                != TARGET_IMAGE_CONFIG_SHA256):
            raise ValueError("TARGET_IMAGE_CONFIG_MISMATCH")
    if target_no_project_base_override and target_image_config_source is None:
        raise ValueError("TARGET_IMAGE_CONFIG_REQUIRED")
    target_image_path_facts = {}
    if target_image_save_path is not None:
        if (not target_direct_python312 or not target_no_site
                or not target_no_project_base_override
                or target_image_config_source is None):
            raise ValueError("TARGET_IMAGE_PATH_ASSUMPTIONS_REQUIRED")
        target_image_path_facts = _target_image_save_facts(
            target_image_save_path, target_image_config_source,
        )
        sysconfig_name_facts.update({
            "_PYTHON_BUILD": target_image_path_facts["_PYTHON_BUILD"],
        })
    sysconfig_project_base_env_facts = _target_sysconfig_project_base_env_facts(
        files, target_image_config_source, target_no_project_base_override,
    ) if target_image_config_source is not None else ()
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
    types_descriptor_call_facts = _target_types_descriptor_call_facts(files)
    ast_compatibility_call_facts = _target_ast_compatibility_call_facts(
        files, ast_asdl, ast_c_source
    )
    sys_getframe_call_facts = _target_sys_getframe_call_facts(
        files, sys_module_c_source, sys_module_clinic_source
    )
    warnings_default_call_facts = _target_warnings_default_call_facts(
        files, warnings_c_source, warnings_clinic_source
    )
    os_name_facts = _target_os_posix_name_facts(
        files, posix_module_c_source, posix_module_clinic_source
    )
    os_name_facts.update(_target_os_posix_boolean_assignment_facts(
        files, posix_module_c_source, posix_module_clinic_source
    ))
    os_fspath_call_facts = _target_os_fspath_call_facts(
        files, posix_module_c_source, posix_module_clinic_source
    )
    os_have_functions_call_facts = _target_os_have_functions_call_facts(
        files, posix_module_c_source, posix_module_clinic_source
    )
    target_pyconfig_source = None
    if target_pyconfig_path is not None:
        with Path(target_pyconfig_path).open("rb") as stream:
            target_pyconfig_source = stream.read(MAX_TARGET_PYCONFIG_BYTES + 1)
        if (len(target_pyconfig_source) > MAX_TARGET_PYCONFIG_BYTES
                or hashlib.sha256(target_pyconfig_source).hexdigest()
                != TARGET_PYCONFIG_SHA256):
            raise ValueError("TARGET_PYCONFIG_MISMATCH")
    posix_build_call_facts = _target_posix_build_call_facts(
        files, posix_module_c_source, posix_module_clinic_source,
        target_pyconfig_source,
    ) if target_pyconfig_source is not None else ()
    os_descriptor_support_facts = _target_os_descriptor_support_facts(
        files, posix_module_c_source, posix_module_clinic_source,
        target_pyconfig_source,
    ) if target_pyconfig_source is not None else ()
    threading_os_alias_call_facts = _target_threading_os_alias_facts(files)
    if not any(fact[0] == "hasattr(os, 'register_at_fork')"
               for fact in posix_build_call_facts):
        threading_os_alias_call_facts = ()
    threading_native_id_facts = (
        _target_threading_native_id_name_facts(
            files, thread_native_id_header, thread_native_id_module,
            thread_native_id_pthread, target_pyconfig_source,
        ) if target_pyconfig_source is not None else {}
    )
    target_imported_name_safe_modules = tuple(sorted(
        module for module in ("ast", "dis", "inspect", "os", "sysconfig", "tokenize")
        if (_target_imported_name_star_imports_safe(files, module)
            or module == "ast" and _target_ast_imported_name_star_import_safe(
                files, ast_c_source
            )
            or module == "inspect" and _target_inspect_imported_name_safe(files)
            or module == "sysconfig" and _target_sysconfig_imported_name_safe(files)
            or module == "os" and bool(os_name_facts))
    ))
    target_call_facts = tuple(sorted(
        types_descriptor_call_facts + ast_compatibility_call_facts
        + sys_getframe_call_facts + tuple(warnings_default_call_facts.items())
        + os_fspath_call_facts + os_have_functions_call_facts
        + posix_build_call_facts + os_descriptor_support_facts
        + threading_os_alias_call_facts + sysconfig_project_base_env_facts
    ))
    if target_image_path_facts:
        target_call_facts += (("sys.executable", True),)
    modules, edges, rows_sha256 = _candidate_closure(files)
    module_body, module_body_edges, module_body_sha256 = _module_body_candidate_closure(files)
    target_unknown_conditions = []
    target_platform, target_edges, target_sha256, target_conditions = (
        _target_platform_candidate_closure(
            files, unknown_conditions=target_unknown_conditions,
            known_call_facts=target_call_facts,
            known_name_facts={"warnings": warnings_default_call_facts,
                              "os": os_name_facts,
                              "threading": threading_native_id_facts,
                              "sysconfig": sysconfig_name_facts},
            preserve_imported_name_modules=target_imported_name_safe_modules,
        )
    )
    target_unknown_conditions_sha256 = hashlib.sha256(
        json.dumps(
            target_unknown_conditions, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
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
        "frozen_bootstrap_names": list(frozen["bootstrap_names"]),
        "frozen_bootstrap_names_sha256": frozen["bootstrap_sha256"],
        "frozen_stdlib_name_count": len(frozen["stdlib_names"]),
        "frozen_stdlib_names": list(frozen["stdlib_names"]),
        "frozen_stdlib_names_sha256": frozen["stdlib_sha256"],
        "frozen_test_name_count": len(frozen["test_names"]),
        "frozen_test_names_sha256": frozen["test_sha256"],
        "frozen_alias_count": len(frozen["aliases"]),
        "frozen_alias_rows": [list(row) for row in frozen["aliases"]],
        "frozen_aliases_sha256": frozen["aliases_sha256"],
        "target_platform_frozen_name_candidates": sorted(
            set(target_platform) & set(frozen["bootstrap_names"] + frozen["stdlib_names"])
        ),
        "module_init_call_frozen_name_candidates": sorted(
            set(call_modules) & set(frozen["bootstrap_names"] + frozen["stdlib_names"])
        ),
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
        "target_platform_source_candidates": _module_source_rows(files, target_platform),
        "target_platform_edge_count": target_edges,
        "target_platform_scope": "MODULE_CLASS_AND_KNOWN_LINUX_CPYTHON312_IF_BUILTIN_AND_IMPORTED_MODULE_NAME_BRANCHES",
        "target_platform_rows_sha256": target_sha256,
        "target_platform_resolved_if_count": target_conditions["resolved"],
        "target_platform_unknown_if_count": target_conditions["unknown"],
        "target_platform_unknown_if_conditions": target_unknown_conditions,
        "target_platform_unknown_if_conditions_sha256": target_unknown_conditions_sha256,
        "target_platform_types_descriptor_call_facts": list(
            types_descriptor_call_facts
        ),
        "target_platform_ast_compatibility_call_facts": list(
            ast_compatibility_call_facts
        ),
        "target_platform_ast_source_sha256": _AST_SOURCE_SHA256,
        "target_platform_ast_asdl_sha256": AST_ASDL_SHA256,
        "target_platform_ast_c_sha256": AST_C_SHA256,
        "target_platform_sys_getframe_call_facts": list(sys_getframe_call_facts),
        "target_platform_sys_module_c_sha256": SYS_MODULE_C_SHA256,
        "target_platform_sys_module_clinic_sha256": SYS_MODULE_CLINIC_SHA256,
        "target_platform_warnings_default_call_facts": list(
            warnings_default_call_facts.items()
        ),
        "target_platform_source_name_fact_modules": list(
            target_imported_name_safe_modules
        ),
        "target_platform_os_name_fact": list(os_name_facts.items()),
        "target_platform_os_source_sha256": OS_SOURCE_SHA256,
        "target_platform_posix_module_c_sha256": POSIX_MODULE_C_SHA256,
        "target_platform_posix_module_clinic_sha256": POSIX_MODULE_CLINIC_SHA256,
        "target_platform_os_fspath_call_facts": list(os_fspath_call_facts),
        "target_platform_os_have_functions_call_facts": list(os_have_functions_call_facts),
        "target_platform_posix_build_call_facts": list(posix_build_call_facts),
        "target_platform_threading_os_alias_call_facts": list(
            threading_os_alias_call_facts
        ),
        "target_platform_threading_native_id_name_facts": list(
            threading_native_id_facts.items()
        ),
        "target_platform_sysconfig_name_facts": list(sysconfig_name_facts.items()),
        "target_profile_no_site_assumption": target_no_site,
        "target_platform_sysconfig_project_base_env_fact": list(
            sysconfig_project_base_env_facts
        ),
        "target_profile_no_project_base_override_assumption": (
            target_no_project_base_override
        ),
        "target_profile_direct_python312_executable_assumption": (
            target_direct_python312
        ),
        "target_platform_image_save_path_facts": target_image_path_facts,
        "target_platform_thread_native_id_source_sha256": {
            "header": THREAD_NATIVE_ID_HEADER_SHA256,
            "module": THREAD_NATIVE_ID_MODULE_SHA256,
            "pthread": THREAD_NATIVE_ID_PTHREAD_SHA256,
        },
        "target_platform_pyconfig_sha256": (
            hashlib.sha256(target_pyconfig_source).hexdigest()
            if target_pyconfig_source is not None else None
        ),
        "target_platform_image_config_sha256": (
            hashlib.sha256(target_image_config_source).hexdigest()
            if target_image_config_source is not None else None
        ),
        "target_platform_image_manifest_sha256": (
            TARGET_IMAGE_MANIFEST_SHA256
            if target_pyconfig_source is not None else None
        ),
        "target_platform_pyconfig_layer_sha256": (
            TARGET_IMAGE_CONFIG_LAYER_SHA256
            if target_pyconfig_source is not None else None
        ),
        "target_platform_types_source_sha256": _TYPES_SOURCE_SHA256,
        "target_platform_inspect_source_sha256": _INSPECT_SOURCE_SHA256,
        "target_platform_builtin_membership": _TARGET_BUILTIN_MEMBERSHIP,
        "target_platform_builtin_module_names": list(_TARGET_BUILTIN_MODULE_NAMES),
        "target_platform_builtin_config_c_sha256": _TARGET_BUILTIN_CONFIG_C_SHA256,
        "target_platform_builtin_layer_sha256": _TARGET_BUILTIN_LAYER_SHA256,
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
    parser.add_argument(
        "--target-pyconfig", type=Path,
        help="Digest-geprüfte pyconfig.h aus dem ausgewählten CPython-Zielimage",
    )
    parser.add_argument(
        "--target-no-site", action="store_true",
        help="Annahme für die feste Zielroute: CPython wird mit -S gestartet",
    )
    parser.add_argument(
        "--target-image-config", type=Path,
        help="Digest-geprüfte OCI-Config des ausgewählten CPython-Zielimages",
    )
    parser.add_argument(
        "--target-no-project-base-override", action="store_true",
        help="Annahme für die feste Zielroute: kein Override für _PYTHON_PROJECT_BASE",
    )
    parser.add_argument(
        "--target-image-save", type=Path,
        help="Digest- und DiffID-geprüfter Docker-save-Tarball des Zielimages",
    )
    parser.add_argument(
        "--target-direct-python312", action="store_true",
        help="Aufrufannahme: sys.executable verweist auf /usr/local/bin/python3.12",
    )
    args = parser.parse_args()
    if args.target_no_site and args.target_pyconfig is None:
        parser.error("--target-no-site requires --target-pyconfig")
    if args.target_no_project_base_override and args.target_image_config is None:
        parser.error("--target-no-project-base-override requires --target-image-config")
    if args.target_direct_python312 and args.target_image_save is None:
        parser.error("--target-direct-python312 requires --target-image-save")
    try:
        result = analyze(args.archive, args.target_pyconfig, args.target_no_site,
                         args.target_image_config,
                         args.target_no_project_base_override,
                         args.target_image_save,
                         args.target_direct_python312)
    except (OSError, tarfile.TarError, UnicodeError, SyntaxError, ValueError):
        print(json.dumps({"status": "NOT_PROVEN", "issue": "SOURCE_INPUT_REJECTED"},
                         separators=(",", ":")))
        return 1
    print(json.dumps({"status": "CANDIDATES_ONLY", **result}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
