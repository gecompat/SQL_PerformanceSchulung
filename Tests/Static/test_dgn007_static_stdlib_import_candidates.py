"""Gegenproben für die deklarative CPython-Quellkandidatenanalyse."""
import ast
import hashlib
import gzip
import importlib.util
import inspect
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


TOOL = Path(__file__).resolve().parents[1] / "Tools/dgn007_static_stdlib_import_candidates.py"
SPEC = importlib.util.spec_from_file_location("dgn007_static_stdlib_import_candidates", TOOL)
SUBJECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUBJECT)


class StaticImportCandidateTests(unittest.TestCase):
    @staticmethod
    def _worker_sys_flag_fact_fixture():
        preconfig_header_source = (
            b"typedef struct {\nint isolated; int use_environment; "
            b"int dev_mode; int warn_default_encoding;\n} _PyPreCmdline;\n"
            b"#define _PyPreCmdline_INIT \\\n"
            b" (_PyPreCmdline){ .use_environment=-1, .isolated=-1, "
            b".dev_mode=-1}\n"
            b"/* Note: _PyPreCmdline_INIT sets other fields to 0/NULL */\n"
        )
        long_header_source = b"#define _PY_LONG_DEFAULT_MAX_STR_DIGITS 4300\n"
        preconfig_source = (
            b"case 'I': cmdline->isolated = 1;\n"
            b"PyStatus _PyPreCmdline_Read(_PyPreCmdline *cmdline, "
            b"const PyPreConfig *preconfig) {\n"
            b"if (cmdline->isolated > 0) { cmdline->use_environment = 0; }\n"
            b"if ((cmdline->dev_mode < 0) && "
            b"(_Py_get_xoption(&cmdline->xoptions, L\"dev\") || "
            b"_Py_GetEnv(cmdline->use_environment, \"PYTHONDEVMODE\"))) { "
            b"cmdline->dev_mode = 1; }\n"
            b"if (cmdline->dev_mode < 0) { cmdline->dev_mode = 0; }\n"
            b"if (_Py_get_xoption(&cmdline->xoptions, "
            b"L\"warn_default_encoding\") || "
            b"_Py_GetEnv(cmdline->use_environment, "
            b"\"PYTHONWARNDEFAULTENCODING\")) { "
            b"cmdline->warn_default_encoding = 1; }\n}\n"
            b"PyStatus _PyPreCmdline_SetConfig(const _PyPreCmdline *cmdline, "
            b"PyConfig *config) {\nCOPY_ATTR(dev_mode); "
            b"COPY_ATTR(warn_default_encoding);\n}\n"
        )
        initconfig_source = (
            b"if (config->isolated) { config->safe_path = 1; "
            b"config->use_environment = 0; "
            b"config->user_site_directory = 0; }\n"
            b"static void config_init_defaults(PyConfig *config) {\n"
            b"config->parser_debug = 0; config->inspect = 0; "
            b"config->interactive = 0; config->verbose = 0; "
            b"config->bytes_warning = 0; config->quiet = 0;\n"
            b"config->optimization_level = 0;\n}\n"
            b"static PyStatus config_init_int_max_str_digits(PyConfig *config) {\n"
            b"const char *env = config_get_env(config, \"PYTHONINTMAXSTRDIGITS\");\n"
            b"const wchar_t *xoption = config_get_xoption(config, "
            b"L\"int_max_str_digits\");\n"
            b"if (config->int_max_str_digits < 0) { "
            b"config->int_max_str_digits = _PY_LONG_DEFAULT_MAX_STR_DIGITS; }\n}\n"
            b"if (config->int_max_str_digits < 0) { "
            b"status = config_init_int_max_str_digits(config); }\n"
            b"case 'd': config->parser_debug++;\n"
            b"case 'i': config->inspect++; config->interactive++;\n"
            b"case 'b': config->bytes_warning++;\n"
            b"case 'v': config->verbose++;\n"
            b"case 'q': config->quiet++;\n"
            b"if (config->use_hash_seed < 0) { config->use_hash_seed = 0; "
            b"config->hash_seed = 0; }\n"
            b"static const char *config_get_env(const PyConfig *config, "
            b"const char *name) { return _Py_GetEnv(config->use_environment, name); }\n"
            b"static PyStatus config_init_hash_seed(PyConfig *config) { "
            b"const char *seed_text = config_get_env(config, \"PYTHONHASHSEED\"); "
            b"if (seed_text) { config->use_hash_seed = 1; } else { "
            b"/* Use a random hash */ config->use_hash_seed = 0; "
            b"config->hash_seed = 0; } }\n"
            b"case 'B': config->write_bytecode = 0;\n"
            b"case 'S': config->site_import = 0;\n"
            b"case 'O': config->optimization_level++;\n"
        )
        sys_module_source = (
            b"static PyStructSequence_Field flags_fields[] = {\n"
            b'{"debug", "-d"}, {"inspect", "-i"}, '
            b'{"interactive", "-i"}, {"optimize", "-O"}, '
            b'{"dont_write_bytecode", "-B"}, {"no_user_site", "-s"}, '
            b'{"no_site", "-S"}, {"ignore_environment", "-E"}, '
            b'{"verbose", "-v"}, {"bytes_warning", "-b"}, '
            b'{"quiet", "-q"}, {"hash_randomization", "-R"}, '
            b'{"isolated", "-I"}, {"dev_mode", "-X dev"}, '
            b'{"utf8_mode", "-X utf8"}, '
            b'{"warn_default_encoding", "-X warn_default_encoding"}, '
            b'{"safe_path", "-P"}, '
            b'{"int_max_str_digits", "-X int_max_str_digits"},\n};\n'
            b"static int set_flags_from_config(PyInterpreterState *interp, "
            b"PyObject *flags) {\n"
            b"SetFlag(config->optimization_level);\n"
            b"SetFlag(!config->write_bytecode);\n"
            b"SetFlag(!config->user_site_directory);\n"
            b"SetFlag(!config->site_import);\n"
            b"SetFlag(!config->use_environment);\n"
            b"SetFlag(config->isolated);\n"
            b"SetFlagObj(PyBool_FromLong(config->safe_path));\n"
            b"SetFlag(config->parser_debug);\n"
            b"SetFlag(config->inspect);\n"
            b"SetFlag(config->interactive);\n"
            b"SetFlag(config->verbose);\n"
            b"SetFlag(config->bytes_warning);\n"
            b"SetFlag(config->quiet);\n"
            b"SetFlag(config->use_hash_seed == 0 || config->hash_seed != 0);\n"
            b"SetFlagObj(PyBool_FromLong(config->dev_mode));\n"
            b"SetFlag(preconfig->utf8_mode);\n"
            b"SetFlag(config->warn_default_encoding);\n"
            b"SetFlag(config->int_max_str_digits);\n"
            b"return 0;\n}\n"
            b"int _PySys_UpdateConfig(PyThreadState *tstate) {\n"
            b"if (set_flags_from_config(interp, flags) < 0) { return -1; }\n"
            b'SET_SYS("dont_write_bytecode", '
            b"PyBool_FromLong(!config->write_bytecode));\n"
            b"return 0;\n}\n"
        )
        worker_source = (
            b"def run_import_only(ordinal, worker_nonce):\n"
            b"    command = [sys.executable, '-I', '-S', '-B', '-X', 'utf8=1', '-c', "
            b"_worker_source(ordinal, worker_nonce)]\n"
            b"def _collect_process(command):\n"
            b"    child_env = os.environ.copy()\n"
            b"    child_env.pop('_PYTHON_SYSCONFIGDATA_NAME', None)\n"
            b"    try:\n"
            b"        return subprocess.Popen(command, env=child_env)\n"
            b"    except OSError:\n"
            b"        return None\n"
        )
        return (preconfig_header_source, long_header_source, preconfig_source,
                initconfig_source, sys_module_source, worker_source)

    def test_archive_binding_and_limits_are_fixed(self):
        self.assertEqual(len(SUBJECT.ARCHIVE_SHA256), 64)
        self.assertEqual(SUBJECT.ARCHIVE_ROOT, "Python-3.12.16/Lib/")
        self.assertEqual(SUBJECT.MAX_ARCHIVE_BYTES, 64 * 1024 * 1024)
        self.assertEqual(SUBJECT.MAX_SOURCE_BYTES, 64 * 1024 * 1024)
        self.assertEqual(SUBJECT.MAX_SOURCE_FILES, 2048)

    def test_python_config_sources_are_digest_checked_during_archive_read(self):
        preconfig = b"preconfig source fixture"
        initconfig = b"initconfig source fixture"

        def make_archive(members):
            output = io.BytesIO()
            with SUBJECT.tarfile.open(fileobj=output, mode="w:xz") as archive:
                for name, content in members:
                    info = SUBJECT.tarfile.TarInfo(name)
                    info.size = len(content)
                    archive.addfile(info, io.BytesIO(content))
            return output.getvalue()

        members = [
            (SUBJECT.PRECONFIG_C_MEMBER, preconfig),
            (SUBJECT.INITCONFIG_C_MEMBER, initconfig),
        ]
        with patch.multiple(
            SUBJECT,
            PRECONFIG_C_SHA256=hashlib.sha256(preconfig).hexdigest(),
            INITCONFIG_C_SHA256=hashlib.sha256(initconfig).hexdigest(),
        ):
            result = SUBJECT._source_archive_data(make_archive(members))
            self.assertEqual(result[-2:], (preconfig, initconfig))
            with self.assertRaisesRegex(ValueError, "PYTHON_CONFIG_SOURCE_MEMBER"):
                SUBJECT._source_archive_data(make_archive(
                    members + [(SUBJECT.PRECONFIG_C_MEMBER, preconfig)]
                ))
            changed = b"changed initconfig fixture"
            with self.assertRaisesRegex(ValueError, "PYTHON_CONFIG_SOURCE_DIGEST"):
                SUBJECT._source_archive_data(make_archive([
                    (SUBJECT.PRECONFIG_C_MEMBER, preconfig),
                    (SUBJECT.INITCONFIG_C_MEMBER, changed),
                ]))

    def test_target_image_save_requires_verified_config_layers_and_path_facts(self):
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "image.tar"
            layers = []
            diff_ids = []
            for index in range(7):
                content = io.BytesIO()
                with SUBJECT.tarfile.open(fileobj=content, mode="w") as layer:
                    if index == 6:
                        for directory_name in ("usr", "usr/local", "usr/local/bin"):
                            directory = SUBJECT.tarfile.TarInfo(directory_name)
                            directory.type = SUBJECT.tarfile.DIRTYPE
                            directory.mode = 0o755
                            layer.addfile(directory)
                        for directory_name in (
                                "usr/local/lib", "usr/local/lib/python3.12",
                                "usr/local/lib/python3.12/lib-dynload"):
                            directory = SUBJECT.tarfile.TarInfo(directory_name)
                            directory.type = SUBJECT.tarfile.DIRTYPE
                            directory.mode = 0o755
                            layer.addfile(directory)
                        os_source = b"verified os source"
                        info = SUBJECT.tarfile.TarInfo(
                            SUBJECT.TARGET_PREFIX_STDLIB_LANDMARK
                        )
                        info.mode = 0o644
                        info.size = len(os_source)
                        layer.addfile(info, io.BytesIO(os_source))
                        executable = b"verified executable"
                        info = SUBJECT.tarfile.TarInfo("usr/local/bin/python3.12")
                        info.mode = 0o755
                        info.size = len(executable)
                        layer.addfile(info, io.BytesIO(executable))
                        link = SUBJECT.tarfile.TarInfo("usr/local/bin/python3")
                        link.type = SUBJECT.tarfile.SYMTYPE
                        link.mode = 0o777
                        link.linkname = "python3.12"
                        layer.addfile(link)
                        extension = b"verified pickle extension"
                        info = SUBJECT.tarfile.TarInfo(SUBJECT.PICKLE_EXTENSION_PATH)
                        info.mode = 0o755
                        info.size = len(extension)
                        layer.addfile(info, io.BytesIO(extension))
                        hashlib_extensions = {}
                        for extension_path in SUBJECT.HASHLIB_EXTENSION_FACTS:
                            filename = extension_path.rsplit("/", 1)[-1]
                            extension_content = ("verified " + filename).encode()
                            hashlib_extensions[extension_path] = extension_content
                            info = SUBJECT.tarfile.TarInfo(extension_path)
                            info.mode = 0o755
                            info.size = len(extension_content)
                            layer.addfile(info, io.BytesIO(extension_content))
                        sysconfigdata = (
                            b"build_time_vars = {"
                            b"'SOABI': 'cpython-312-x86_64-linux-gnu', "
                            b"'DESTSHARED': '/usr/local/lib/python3.12/lib-dynload', "
                            b"'EXT_SUFFIX': '.cpython-312-x86_64-linux-gnu.so', "
                            b"'MULTIARCH': 'x86_64-linux-gnu', "
                            b"'ABIFLAGS': '', "
                            b"'MACHDEP': 'linux', "
                            b"'prefix': '/usr/local', 'exec_prefix': '/usr/local', "
                            b"'PLATLIBDIR': 'lib', 'PYTHONPATH': '', "
                            b"'LIBDIR': '/usr/local/lib', "
                            b"'LDLIBRARY': 'libpython3.12.so', "
                            b"'INSTSONAME': 'libpython3.12.so.1.0', "
                            b"'Py_ENABLE_SHARED': 1}\n"
                        )
                        info = SUBJECT.tarfile.TarInfo(SUBJECT.TARGET_SYSCONFIGDATA_PATH)
                        info.mode = 0o644
                        info.size = len(sysconfigdata)
                        layer.addfile(info, io.BytesIO(sysconfigdata))
                        whiteout = SUBJECT.tarfile.TarInfo(
                            "usr/local/bin/Modules/.wh.Setup"
                        )
                        whiteout.size = 0
                        layer.addfile(whiteout, io.BytesIO())
                    if index == 5:
                        setup = b"removed in a later image layer"
                        info = SUBJECT.tarfile.TarInfo(
                            "usr/local/bin/Modules/Setup"
                        )
                        info.size = len(setup)
                        layer.addfile(info, io.BytesIO(setup))
                body = content.getvalue()
                compressed = gzip.compress(body, mtime=0)
                layers.append(compressed)
                diff_ids.append("sha256:" + hashlib.sha256(body).hexdigest())

            layer_names = tuple(hashlib.sha256(body).hexdigest() for body in layers)
            config = {
                "architecture": "amd64", "os": "linux",
                "config": {"Env": ["PATH=/usr/local/bin"]},
                "rootfs": {"type": "layers", "diff_ids": diff_ids},
            }
            config_bytes = json.dumps(config, separators=(",", ":")).encode()
            config_digest = hashlib.sha256(config_bytes).hexdigest()
            oci_manifest = {
                "config": {"digest": "sha256:" + config_digest},
                "layers": [{
                    "digest": "sha256:" + name,
                    "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
                    "size": len(body),
                } for name, body in zip(layer_names, layers)],
            }
            oci_manifest_bytes = json.dumps(oci_manifest, separators=(",", ":")).encode()
            oci_manifest_digest = hashlib.sha256(oci_manifest_bytes).hexdigest()
            image_index = {"manifests": [{
                "digest": "sha256:" + oci_manifest_digest,
                "size": len(oci_manifest_bytes),
            }]}
            image_manifest = [{
                "Config": "blobs/sha256/" + config_digest,
                "Layers": ["blobs/sha256/" + name for name in layer_names],
            }]
            with SUBJECT.tarfile.open(image_path, "w") as outer:
                def add(name, data):
                    info = SUBJECT.tarfile.TarInfo(name)
                    info.size = len(data)
                    outer.addfile(info, io.BytesIO(data))
                add("manifest.json", json.dumps(image_manifest).encode())
                add("index.json", json.dumps(image_index).encode())
                add("blobs/sha256/" + oci_manifest_digest, oci_manifest_bytes)
                add("blobs/sha256/" + config_digest, config_bytes)
                for name, body in zip(layer_names, layers):
                    add("blobs/sha256/" + name, body)

            with patch.multiple(
                SUBJECT,
                TARGET_IMAGE_CONFIG_SHA256=config_digest,
                TARGET_IMAGE_MANIFEST_SHA256=oci_manifest_digest,
                TARGET_IMAGE_LAYER_NAMES=layer_names,
                TARGET_EXECUTABLE_SHA256=hashlib.sha256(b"verified executable").hexdigest(),
                PICKLE_EXTENSION_SHA256=hashlib.sha256(
                    b"verified pickle extension"
                ).hexdigest(),
                HASHLIB_EXTENSION_FACTS={
                    path: hashlib.sha256(content).hexdigest()
                    for path, content in hashlib_extensions.items()
                },
                TARGET_SYSCONFIGDATA_SHA256=hashlib.sha256(
                    sysconfigdata
                ).hexdigest(),
                OS_SOURCE_SHA256=hashlib.sha256(os_source).hexdigest(),
            ):
                facts = SUBJECT._target_image_save_facts(image_path, config_bytes)
                altered_hashlib_facts = dict(SUBJECT.HASHLIB_EXTENSION_FACTS)
                first_extension = next(iter(altered_hashlib_facts))
                altered_hashlib_facts[first_extension] = "0" * 64
                with patch.object(SUBJECT, "HASHLIB_EXTENSION_FACTS",
                                  altered_hashlib_facts):
                    with self.assertRaisesRegex(
                            ValueError, "TARGET_IMAGE_HASHLIB_EXTENSION_FACT"):
                        SUBJECT._target_image_save_facts(image_path, config_bytes)
        self.assertEqual(facts, {
            "executable_path_candidate": "/usr/local/bin/python3.12",
            "executable_sha256": hashlib.sha256(b"verified executable").hexdigest(),
            "executable_size": len(b"verified executable"),
            "python3_symlink_target": "python3.12",
            "pickle_extension_sha256": hashlib.sha256(
                b"verified pickle extension"
            ).hexdigest(),
            "pickle_extension_size": len(b"verified pickle extension"),
            "hashlib_extension_facts": {
                path: {"sha256": hashlib.sha256(content).hexdigest(),
                       "size": len(content)}
                for path, content in hashlib_extensions.items()
            },
            "sysconfigdata_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
            "sysconfigdata_sha256": hashlib.sha256(sysconfigdata).hexdigest(),
            "build_time_vars_literal_dict": True,
            "build_time_vars_entry_count": 14,
            "soabi": "cpython-312-x86_64-linux-gnu",
            "destshared": "/usr/local/lib/python3.12/lib-dynload",
            "extension_suffix": ".cpython-312-x86_64-linux-gnu.so",
            "multiarch": "x86_64-linux-gnu",
            "abiflags": "",
            "machdep": "linux",
            "prefix": "/usr/local",
            "exec_prefix": "/usr/local",
            "platlibdir": "lib",
            "compiled_pythonpath": "",
            "library_dir": "/usr/local/lib",
            "library_name": "libpython3.12.so",
            "library_soname": "libpython3.12.so.1.0",
            "shared_library_enabled": 1,
            "inert_zip_candidate": "/usr/local/lib/python312.zip",
            "prefix_landmark_candidate": "/usr/local",
            "exec_prefix_landmark_candidate": "/usr/local",
            "prefix_venv_markers_absent": list(SUBJECT.TARGET_PREFIX_VENV_MARKERS),
            "build_marker_absent": SUBJECT.TARGET_BUILD_MARKER,
            "pth_override_files_absent": list(SUBJECT.TARGET_PTH_OVERRIDE_PATHS),
            "_PYTHON_BUILD": False,
            "setup_parent_paths_verified": True,
            "_pickle_extension": True,
        })
        md5_path = (
            "usr/local/lib/python3.12/lib-dynload/"
            "_md5.cpython-312-x86_64-linux-gnu.so"
        )
        self.assertEqual(
            SUBJECT.HASHLIB_EXTENSION_FACTS[md5_path],
            "de8d5205ffce91532652500af1142d00366924b3fb2512989099ecf363358035",
        )
        self.assertIn(md5_path, facts["hashlib_extension_facts"])
        with patch.multiple(
            SUBJECT,
            TARGET_EXECUTABLE_SHA256=hashlib.sha256(
                b"verified executable"
            ).hexdigest(),
            PICKLE_EXTENSION_SHA256=hashlib.sha256(
                b"verified pickle extension"
            ).hexdigest(),
            TARGET_SYSCONFIGDATA_SHA256=hashlib.sha256(
                sysconfigdata
            ).hexdigest(),
        ):
            path_candidate = SUBJECT._target_image_sys_path_candidate(
                facts,
                {"posix_default_path_append_order": (
                    "ZIP_LANDMARK", "stdlib_dir", "platstdlib_dir",
                ), "pth_override_guard": True},
                True, True, True,
            )
            self.assertEqual(SUBJECT._target_s15_files_field_candidate(path_candidate), {
                "value": (
                    (
                        "/usr/local/bin/python3.12",
                        len(b"verified executable"),
                        hashlib.sha256(b"verified executable").hexdigest(),
                    ),
                    (
                        "/" + SUBJECT.PICKLE_EXTENSION_PATH,
                        len(b"verified pickle extension"),
                        hashlib.sha256(b"verified pickle extension").hexdigest(),
                    ),
                ),
                "file_count": 2,
                "complete_file_list_claimed": False,
                "runtime_file_selection_claimed": False,
                "evidence_scope": "STATIC_S15_FILES_FIELD_CANDIDATE",
            })
            changed_files = dict(path_candidate)
            changed_files["files_field_candidate"] = [
                *path_candidate["files_field_candidate"][:1],
                dict(path_candidate["files_field_candidate"][1], sha256="0" * 64),
            ]
            self.assertIsNone(SUBJECT._target_s15_files_field_candidate(changed_files))
        self.assertEqual(path_candidate, {
            "sys_path_candidate": [
                "/usr/local/lib/python312.zip",
                "/usr/local/lib/python3.12",
                "/usr/local/lib/python3.12/lib-dynload",
            ],
            "executable_field_candidate": {
                "value": "/usr/local/bin/python3.12",
                "target": "/usr/local/bin/python3.12",
                "target_sha256": hashlib.sha256(
                    b"verified executable"
                ).hexdigest(),
                "direct_regular_file": True,
                "runtime_executable_claimed": False,
            },
            "executable_target_candidate": "/usr/local/bin/python3.12",
            "abi_field_candidate": {
                "value": "cpython-312-x86_64-linux-gnu",
                "source_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
                "source_sha256": hashlib.sha256(sysconfigdata).hexdigest(),
                "source_key": "SOABI",
                "runtime_abi_claimed": False,
            },
            "files_field_candidate": [
                {
                    "path": "/usr/local/bin/python3.12",
                    "size": len(b"verified executable"),
                    "sha256": hashlib.sha256(b"verified executable").hexdigest(),
                },
                {
                    "path": "/" + SUBJECT.PICKLE_EXTENSION_PATH,
                    "size": len(b"verified pickle extension"),
                    "sha256": hashlib.sha256(
                        b"verified pickle extension"
                    ).hexdigest(),
                },
            ],
            "roots_field_candidate": {
                "values": [
                    "/usr/local/lib/python3.12",
                    "/usr/local/lib/python3.12/lib-dynload",
                ],
                "stdlib_root": "/usr/local/lib/python3.12",
                "extension_root": "/usr/local/lib/python3.12/lib-dynload",
                "extension_file_verified": True,
                "runtime_roots_claimed": False,
            },
            "inert_zip_field_candidate": {
                "value": "/usr/local/lib/python312.zip",
                "path_role": "ZIP_LANDMARK",
                "sys_path_candidate_index": 0,
                "image_member_absent": True,
                "runtime_membership_claimed": False,
            },
        })
        self.assertEqual(SUBJECT._target_s15_paths_field_candidate(path_candidate), {
            "value": (
                "/usr/local/lib/python312.zip",
                "/usr/local/lib/python3.12",
                "/usr/local/lib/python3.12/lib-dynload",
            ),
            "inert_zip_candidate_bound": True,
            "roots_candidate_bound": True,
            "runtime_sys_path_claimed": False,
            "evidence_scope": "STATIC_S15_PATHS_FIELD_CANDIDATE",
        })
        changed_paths = dict(path_candidate)
        changed_paths["sys_path_candidate"] = ["/unexpected"]
        self.assertIsNone(SUBJECT._target_s15_paths_field_candidate(changed_paths))
        self.assertEqual(SUBJECT._target_s15_roots_field_candidate(path_candidate), {
            "value": (
                "/usr/local/lib/python3.12",
                "/usr/local/lib/python3.12/lib-dynload",
            ),
            "extension_file_verified": True,
            "runtime_roots_claimed": False,
            "evidence_scope": "STATIC_S15_ROOTS_FIELD_CANDIDATE",
        })
        changed_roots = dict(path_candidate)
        changed_roots["roots_field_candidate"] = dict(
            path_candidate["roots_field_candidate"],
            runtime_roots_claimed=True,
        )
        self.assertIsNone(SUBJECT._target_s15_roots_field_candidate(changed_roots))
        self.assertEqual(
            SUBJECT._target_s15_inert_zip_field_candidate(path_candidate),
            {
                "value": "/usr/local/lib/python312.zip",
                "image_member_absent": True,
                "runtime_membership_claimed": False,
                "evidence_scope": "STATIC_S15_INERT_ZIP_FIELD_CANDIDATE",
            },
        )
        changed_zip = dict(path_candidate)
        changed_zip["inert_zip_field_candidate"] = dict(
            path_candidate["inert_zip_field_candidate"], image_member_absent=False,
        )
        self.assertIsNone(SUBJECT._target_s15_inert_zip_field_candidate(changed_zip))
        changed_paths = dict(path_candidate)
        changed_paths["inert_zip_field_candidate"] = dict(
            path_candidate["inert_zip_field_candidate"],
            sys_path_candidate_index=False,
        )
        self.assertIsNone(SUBJECT._target_s15_paths_field_candidate(changed_paths))

    def test_target_sysconfigdata_rejects_unbound_source(self):
        with patch.object(SUBJECT, "TARGET_SYSCONFIGDATA_SHA256", "0" * 64):
            with self.assertRaisesRegex(ValueError, "TARGET_SYSCONFIGDATA_DIGEST"):
                SUBJECT._target_image_sysconfigdata_facts(
                    b"build_time_vars = {'SOABI': 'unbound'}"
                )

    def test_target_image_inert_zip_fact_rejects_present_path(self):
        with self.assertRaisesRegex(ValueError, "TARGET_IMAGE_INERT_ZIP_PRESENT"):
            SUBJECT._target_image_inert_zip_fact({
                SUBJECT.TARGET_INERT_ZIP_PATH: {"file": True},
            })

    def test_target_image_prefix_landmarks_reject_venv_marker(self):
        tracked = {
            SUBJECT.TARGET_PREFIX_STDLIB_LANDMARK: {
                "file": True, "directory": False, "symlink": False,
                "linkname": None, "mode": 0o644,
                "sha256": SUBJECT.OS_SOURCE_SHA256,
            },
            SUBJECT.TARGET_EXEC_PREFIX_LANDMARK: {
                "file": False, "directory": True, "symlink": False,
                "linkname": None, "mode": 0o755, "sha256": None,
            },
            SUBJECT.TARGET_PREFIX_VENV_MARKERS[0]: {"file": True},
            SUBJECT.TARGET_PREFIX_VENV_MARKERS[1]: None,
            SUBJECT.TARGET_BUILD_MARKER: None,
        }
        with self.assertRaisesRegex(ValueError, "TARGET_IMAGE_PREFIX_LANDMARKS"):
            SUBJECT._target_image_prefix_landmark_facts(tracked)

    def test_target_sys_path_candidate_rejects_compiled_extra_path(self):
        image_facts = {
            "prefix": "/usr/local", "exec_prefix": "/usr/local",
            "platlibdir": "lib", "compiled_pythonpath": "/unexpected",
            "prefix_landmark_candidate": "/usr/local",
            "exec_prefix_landmark_candidate": "/usr/local",
        }
        inventory = {"posix_default_path_append_order": (
            "ZIP_LANDMARK", "stdlib_dir", "platstdlib_dir",
        )}
        with self.assertRaisesRegex(ValueError, "TARGET_IMAGE_SYS_PATH_CANDIDATE"):
            SUBJECT._target_image_sys_path_candidate(
                image_facts, inventory, True, True, True,
            )

    def test_target_sys_path_candidate_rejects_unbound_inert_zip_path(self):
        image_facts = {
            "prefix": "/usr/local", "exec_prefix": "/usr/local",
            "platlibdir": "lib", "compiled_pythonpath": "",
            "prefix_landmark_candidate": "/usr/local",
            "exec_prefix_landmark_candidate": "/usr/local",
            "pth_override_files_absent": list(SUBJECT.TARGET_PTH_OVERRIDE_PATHS),
            "inert_zip_candidate": "/unexpected/python312.zip",
        }
        inventory = {
            "posix_default_path_append_order": (
                "ZIP_LANDMARK", "stdlib_dir", "platstdlib_dir",
            ),
            "pth_override_guard": True,
        }
        with self.assertRaisesRegex(ValueError, "TARGET_IMAGE_SYS_PATH_ZIP_BINDING"):
            SUBJECT._target_image_sys_path_candidate(
                image_facts, inventory, True, True, True,
            )

        image_facts.update({
            "inert_zip_candidate": "/usr/local/lib/python312.zip",
            "destshared": "/unexpected/lib-dynload",
            "_pickle_extension": True,
        })
        with self.assertRaisesRegex(ValueError, "TARGET_IMAGE_SYS_PATH_ROOT_BINDING"):
            SUBJECT._target_image_sys_path_candidate(
                image_facts, inventory, True, True, True,
            )

        image_facts.update({
            "destshared": "/usr/local/lib/python3.12/lib-dynload",
            "_pickle_extension": True,
            "executable_path_candidate": "/usr/local/bin/python3.12",
            "executable_sha256": SUBJECT.TARGET_EXECUTABLE_SHA256,
            "executable_size": SUBJECT.MAX_S15_FILE_BYTES + 1,
            "pickle_extension_size": 1,
            "pickle_extension_sha256": SUBJECT.PICKLE_EXTENSION_SHA256,
        })
        with self.assertRaisesRegex(ValueError, "TARGET_IMAGE_S15_FILE_CANDIDATES"):
            SUBJECT._target_image_sys_path_candidate(
                image_facts, inventory, True, True, True,
            )

        image_facts.update({
            "executable_size": 1,
            "soabi": "unbound-abi",
            "sysconfigdata_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
            "sysconfigdata_sha256": SUBJECT.TARGET_SYSCONFIGDATA_SHA256,
        })
        with self.assertRaisesRegex(ValueError, "TARGET_IMAGE_S15_ABI_CANDIDATE"):
            SUBJECT._target_image_sys_path_candidate(
                image_facts, inventory, True, True, True,
            )

    def test_s15_prefixes_candidate_requires_config_defaults_and_image_roots(self):
        image_facts = {
            "sysconfigdata_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
            "sysconfigdata_sha256": SUBJECT.TARGET_SYSCONFIGDATA_SHA256,
            "prefix": "/usr/local",
            "exec_prefix": "/usr/local",
            "prefix_landmark_candidate": "/usr/local",
            "exec_prefix_landmark_candidate": "/usr/local",
            "prefix_venv_markers_absent": list(SUBJECT.TARGET_PREFIX_VENV_MARKERS),
            "build_marker_absent": SUBJECT.TARGET_BUILD_MARKER,
            "_PYTHON_BUILD": False,
            "setup_parent_paths_verified": True,
            "pth_override_files_absent": list(SUBJECT.TARGET_PTH_OVERRIDE_PATHS),
        }
        getpath_inventory = {
            "source_sha256": SUBJECT.GETPATH_SOURCE_SHA256,
            "base_prefix_config_read": True,
            "base_prefix_fallback_bound": True,
        }
        path_candidate = {"sys_path_candidate": [
            "/usr/local/lib/python312.zip",
            "/usr/local/lib/python3.12",
            "/usr/local/lib/python3.12/lib-dynload",
        ]}
        initconfig = (
            b"void _PyConfig_InitCompatConfig(PyConfig *config) {\n"
            b"    memset(config, 0, sizeof(*config));\n}\n"
            b"static void config_init_defaults(PyConfig *config) {\n"
            b"    _PyConfig_InitCompatConfig(config);\n"
            b"    config->isolated = 0;\n}\n"
            b"void PyConfig_InitPythonConfig(PyConfig *config) {\n"
            b"    config_init_defaults(config);\n}\n"
        )
        with patch.object(
            SUBJECT, "INITCONFIG_C_SHA256", hashlib.sha256(initconfig).hexdigest(),
        ):
            candidate = SUBJECT._target_s15_prefixes_field_candidate(
                image_facts, getpath_inventory, path_candidate, initconfig,
                True, True, True,
            )
            self.assertEqual(candidate, {
                "values": ("/usr/local", "/usr/local", "/usr/local", "/usr/local"),
                "field_order": (
                    "prefix", "exec_prefix", "base_prefix", "base_exec_prefix",
                ),
                "prefix_source": "getpath POSIX landmarks and verified sysconfig defaults",
                "base_prefix_source": "empty PyConfig defaults and getpath fallback",
                "getpath_source_sha256": SUBJECT.GETPATH_SOURCE_SHA256,
                "initconfig_source_sha256": hashlib.sha256(initconfig).hexdigest(),
                "sysconfigdata_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
                "sysconfigdata_sha256": SUBJECT.TARGET_SYSCONFIGDATA_SHA256,
                "runtime_prefixes_claimed": False,
            })
            self.assertEqual(SUBJECT._target_s15_prefixes_field_candidate(
                image_facts, getpath_inventory, path_candidate,
                initconfig.replace(
                    b"config_init_defaults(config);", b"unknown_defaults(config);",
                ), True, True, True,
            ), {})
        self.assertEqual(SUBJECT._target_s15_prefixes_field_candidate(
            {**image_facts, "exec_prefix": "/unexpected"}, getpath_inventory,
            path_candidate, initconfig, True, True, True,
        ), {})

    def test_target_image_pth_override_fact_rejects_present_path(self):
        with self.assertRaisesRegex(ValueError, "TARGET_IMAGE_PTH_OVERRIDE_PRESENT"):
            SUBJECT._target_image_pth_override_facts({
                SUBJECT.TARGET_PTH_OVERRIDE_PATHS[0]: {"file": True},
            })

    def test_target_image_setup_paths_reject_symlinked_probe_parents(self):
        tracked = {
            "usr": {"directory": True, "symlink": False},
            "usr/local": {"directory": True, "symlink": False},
            "usr/local/bin": {"directory": True, "symlink": False},
            "usr/local/bin/Modules": None,
            "usr/local/bin/Modules/Setup": None,
            "usr/local/bin/Modules/Setup.local": None,
        }
        self.assertTrue(SUBJECT._target_image_setup_paths_safe(tracked))
        redirected = dict(tracked)
        redirected["usr/local/bin/Modules"] = {
            "directory": False, "symlink": True,
        }
        self.assertFalse(SUBJECT._target_image_setup_paths_safe(redirected))

    def test_sysconfig_build_guard_fact_requires_exact_image_and_route(self):
        source = (
            b"def _safe_realpath(path):\n    return path\n"
            b"if sys.executable:\n"
            b"    _PROJECT_BASE = os.path.dirname(_safe_realpath(sys.executable))\n"
            b"def is_python_build(check_home=None):\n"
            b"    if check_home is not None:\n        import warnings\n"
            b"    for fn in ('Setup', 'Setup.local'):\n"
            b"        if os.path.isfile(os.path.join(_PROJECT_BASE, 'Modules', fn)):\n"
            b"            return True\n"
            b"    return False\n"
        )
        files = {"sysconfig.py": source}
        image_facts = {
            "executable_path_candidate": "/usr/local/bin/python3.12",
            "_PYTHON_BUILD": False,
            "setup_parent_paths_verified": True,
            "_pickle_extension": True,
            "newly_verified_target_fact": {"sha256": "a" * 64},
        }
        sysconfig_name_facts = {"_sys_home": False}
        env_facts = (("'_PYTHON_PROJECT_BASE' in os.environ", False),)
        with patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(source).hexdigest(),
        ):
            facts = SUBJECT._target_sysconfig_build_setup_guard_line_facts(
                files, image_facts, sysconfig_name_facts, env_facts,
                True, True, True,
            )
            self.assertEqual(facts, {9: False})
            self.assertEqual(SUBJECT._target_sysconfig_build_setup_guard_line_facts(
                files, {**image_facts, "setup_parent_paths_verified": False},
                sysconfig_name_facts, env_facts, True, True, True,
            ), {})
            self.assertEqual(SUBJECT._target_sysconfig_build_setup_guard_line_facts(
                files, image_facts, sysconfig_name_facts, env_facts,
                False, True, True,
            ), {})
            self.assertEqual(SUBJECT._target_sysconfig_build_setup_guard_line_facts(
                files, image_facts, sysconfig_name_facts, (), True, True, True,
            ), {})

    def test_sysconfig_venv_guard_requires_equal_prefix_candidates(self):
        source = (
            b"def get_preferred_scheme(key):\n"
            b"    if key == 'prefix' and sys.prefix != sys.base_prefix:\n"
            b"        return 'venv'\n"
        )
        prefixes = {
            "values": ("/usr/local", "/usr/local", "/usr/local", "/usr/local"),
            "field_order": ("prefix", "exec_prefix", "base_prefix", "base_exec_prefix"),
            "runtime_prefixes_claimed": False,
        }
        with patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(source).hexdigest(),
        ):
            self.assertEqual(
                SUBJECT._target_sysconfig_venv_prefix_guard_line_facts(
                    {"sysconfig.py": source}, prefixes,
                ),
                {2: False},
            )
            different = dict(prefixes)
            different["values"] = (
                "/usr/local", "/usr/local", "/usr", "/usr/local",
            )
            self.assertEqual(
                SUBJECT._target_sysconfig_venv_prefix_guard_line_facts(
                    {"sysconfig.py": source}, different,
                ),
                {},
            )
            runtime_claim = {**prefixes, "runtime_prefixes_claimed": True}
            self.assertEqual(
                SUBJECT._target_sysconfig_venv_prefix_guard_line_facts(
                    {"sysconfig.py": source}, runtime_claim,
                ),
                {},
            )

    def test_sysconfig_preferred_scheme_guard_requires_literal_valid_schemes(self):
        source = (
            b"_INSTALL_SCHEMES = {'posix_prefix': {}, 'posix_home': {}}\n"
            b"if _HAS_USER_BASE:\n"
            b"    _INSTALL_SCHEMES |= {'posix_user': {}}\n"
            b"def _get_preferred_schemes():\n"
            b"    return {'prefix': 'posix_prefix', 'home': 'posix_home', "
            b"'user': 'posix_user'}\n"
            b"def get_preferred_scheme(key):\n"
            b"    scheme = _get_preferred_schemes()[key]\n"
            b"    if scheme not in _INSTALL_SCHEMES:\n"
            b"        raise ValueError()\n"
            b"    return scheme\n"
        )
        files = {"sysconfig.py": source}
        target_facts = {"_HAS_USER_BASE": True}
        with patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(source).hexdigest(),
        ):
            self.assertEqual(
                SUBJECT._target_sysconfig_preferred_scheme_membership_line_facts(
                    files, target_facts,
                ),
                {8: False},
            )
            self.assertEqual(
                SUBJECT._target_sysconfig_preferred_scheme_membership_line_facts(
                    files, {"_HAS_USER_BASE": False},
                ),
                {},
            )
            invalid = source.replace(b"'user': 'posix_user'",
                                     b"'user': 'missing_scheme'")
            with patch.object(
                SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(invalid).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_sysconfig_preferred_scheme_membership_line_facts(
                        {"sysconfig.py": invalid}, target_facts,
                    ),
                    {},
                )

    def test_pickle_buffer_line_fact_requires_exact_source_and_target_extension(self):
        source = (
            b"try:\n    from _pickle import PickleBuffer\n"
            b"    _HAVE_PICKLE_BUFFER = True\n"
            b"except ImportError:\n    _HAVE_PICKLE_BUFFER = False\n"
            b"class Pickler:\n    if _HAVE_PICKLE_BUFFER:\n        pass\n"
        )
        c_source = (
            b"/* Add types */\n    if (PyModule_AddType(m, "
            b"&PyPickleBuffer_Type) < 0) {"
        )
        with patch.multiple(
            SUBJECT,
            PICKLE_SOURCE_SHA256=hashlib.sha256(source).hexdigest(),
            PICKLE_MODULE_C_SHA256=hashlib.sha256(c_source).hexdigest(),
        ):
            self.assertEqual(SUBJECT._target_pickle_buffer_line_facts(
                {"pickle.py": source}, c_source, {"_pickle_extension": True}
            ), {7: True})
            self.assertEqual(SUBJECT._target_pickle_buffer_line_facts(
                {"pickle.py": source}, c_source, {}
            ), {})

    def test_target_image_save_rejects_invalid_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "not-an-image.tar"
            image_path.write_bytes(b"invalid")
            with patch.object(SUBJECT, "MAX_TARGET_IMAGE_SAVE_BYTES", 10):
                with self.assertRaisesRegex(ValueError, "TARGET_IMAGE_SAVE_INVALID"):
                    SUBJECT._target_image_save_facts(image_path, b"{}")

    def test_target_module_init_call_scan_uses_only_bound_guard_facts(self):
        files = {
            "entry.py": (
                b"def selected_branch():\n    return True\n"
                b"if selected_branch():\n    import windows_branch\n"
                b"else:\n    import linux_branch\n"
            ),
            "windows_branch.py": b"VALUE = 'windows'\n",
            "linux_branch.py": b"VALUE = 'linux'\n",
        }
        baseline = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",)
        )
        unknown = []
        target = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",),
            known_call_facts=(("selected_branch()", False),),
            unknown_conditions=unknown,
        )
        self.assertIn("windows_branch", baseline[0])
        self.assertIn("linux_branch", baseline[0])
        self.assertEqual(target[0], ("entry", "linux_branch"))
        self.assertEqual(target[4], {"resolved": 1, "unknown": 0})
        self.assertEqual(unknown, [])

    def test_unknown_call_guard_reports_lexical_imports_per_branch(self):
        files = {
            "entry.py": (
                b"if runtime_choice():\n"
                b"    import selected_branch as selected\n"
                b"    from package import helper as local_helper\n"
                b"    selected.run(2)\n"
                b"else:\n"
                b"    import fallback_branch\n"
                b"    fallback_branch.run()\n"
            ),
            "selected_branch.py": b"VALUE = 'selected'\n",
            "fallback_branch.py": b"VALUE = 'fallback'\n",
            "package.py": b"VALUE = 'package'\n",
        }
        unknown = []
        SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",), unknown_conditions=unknown
        )
        self.assertEqual(len(unknown), 1)
        self.assertEqual(unknown[0]["expression"], "runtime_choice()")
        self.assertEqual(unknown[0]["body_imports"], [
            {"kind": "import", "line": 2, "names": [
                {"name": "selected_branch", "asname": "selected"}
            ]},
            {"kind": "from", "line": 3, "level": 0, "module": "package",
             "names": [{"name": "helper", "asname": "local_helper"}]},
        ])
        self.assertEqual(unknown[0]["else_imports"], [
            {"kind": "import", "line": 6, "names": [
                {"name": "fallback_branch", "asname": None}
            ]}
        ])
        self.assertEqual(unknown[0]["body_calls"], [
            {"line": 4, "column": 4, "expression": "selected.run(2)"}
        ])
        self.assertEqual(unknown[0]["else_calls"], [
            {"line": 7, "column": 4, "expression": "fallback_branch.run()"}
        ])

    def test_lexical_call_inventory_is_deterministic_and_includes_nested_bodies(self):
        tree = ast.parse(
            "if check():\n"
            "    pkg.run(pkg.make())\n"
            "    pkg.run(pkg.make())\n"
            "    def deferred():\n"
            "        lazy_call()\n"
            "else:\n"
            "    fallback()\n"
        )
        self.assertEqual(SUBJECT._lexical_call_sites(tree.body[0].body), [
            {"line": 2, "column": 4, "expression": "pkg.run(pkg.make())"},
            {"line": 2, "column": 12, "expression": "pkg.make()"},
            {"line": 3, "column": 4, "expression": "pkg.run(pkg.make())"},
            {"line": 3, "column": 12, "expression": "pkg.make()"},
            {"line": 5, "column": 8, "expression": "lazy_call()"},
        ])
        self.assertEqual(SUBJECT._lexical_call_sites(tree.body[0].orelse), [
            {"line": 7, "column": 4, "expression": "fallback()"}
        ])

    def test_lexical_import_inventory_is_deterministic_and_preserves_locations(self):
        tree = ast.parse(
            "if check():\n    import zed, alpha as a\n    import zed, alpha as a\n"
            "else:\n    from .pkg import leaf as item\n"
        )
        result = SUBJECT._lexical_import_statements(tree.body[0].body)
        self.assertEqual(result, [
            {"kind": "import", "line": 2, "names": [
                {"name": "alpha", "asname": "a"},
                {"name": "zed", "asname": None},
            ]},
            {"kind": "import", "line": 3, "names": [
                {"name": "alpha", "asname": "a"},
                {"name": "zed", "asname": None},
            ]},
        ])
        fallback = SUBJECT._lexical_import_statements(tree.body[0].orelse)
        self.assertEqual(fallback, [
            {"kind": "from", "line": 5, "level": 1, "module": "pkg",
             "names": [{"name": "leaf", "asname": "item"}]}
        ])

    def test_target_module_init_call_scan_applies_source_name_facts(self):
        files = {
            "sysconfig.py": (
                b"_PYTHON_BUILD = True\n"
                b"if _PYTHON_BUILD:\n    import build_branch\n"
                b"else:\n    import installed_branch\n"
            ),
            "build_branch.py": b"VALUE = 'build'\n",
            "installed_branch.py": b"VALUE = 'installed'\n",
        }
        unknown = []
        target = SUBJECT._module_init_call_candidate_closure(
            files, roots=("sysconfig",),
            known_name_facts={"sysconfig": {"_PYTHON_BUILD": False}},
            unknown_conditions=unknown,
        )
        self.assertEqual(target[0], ("installed_branch", "sysconfig"))
        self.assertEqual(target[4], {"resolved": 1, "unknown": 0})
        self.assertEqual(unknown, [])

    def test_trusted_function_name_fact_requires_explicit_stable_source_scope(self):
        files = {
            "threading.py": (
                b"try:\n    get_native_id = _thread.get_native_id\n"
                b"    _HAVE_THREAD_NATIVE_ID = True\n"
                b"except AttributeError:\n    _HAVE_THREAD_NATIVE_ID = False\n"
                b"try:\n    _CRLock = _thread.RLock\n"
                b"except AttributeError:\n    _CRLock = None\n"
                b"def check():\n"
                b"    if not _HAVE_THREAD_NATIVE_ID:\n        import native_branch\n"
                b"    if _CRLock is None:\n        import crlock_branch\n"
                b"check()\n"
            ),
            "native_branch.py": b"VALUE = 1\n",
            "crlock_branch.py": b"VALUE = 2\n",
        }
        fact = {"_HAVE_THREAD_NATIVE_ID": True, "_CRLock": True}
        with patch.object(
            SUBJECT, "THREADING_SOURCE_SHA256",
            hashlib.sha256(files["threading.py"]).hexdigest(),
        ):
            self.assertTrue(SUBJECT._target_threading_native_id_function_fact_safe(
                files, fact
            ))
            for unsafe in (
                files["threading.py"] +
                b"def replace():\n    global _HAVE_THREAD_NATIVE_ID\n"
                b"    _HAVE_THREAD_NATIVE_ID = False\n",
                files["threading.py"] +
                b"def shadow(_CRLock):\n    return _CRLock is None\n",
            ):
                with patch.object(
                    SUBJECT, "THREADING_SOURCE_SHA256",
                    hashlib.sha256(unsafe).hexdigest(),
                ):
                    self.assertFalse(SUBJECT._target_threading_native_id_function_fact_safe(
                        {"threading.py": unsafe}, fact
                    ))
        baseline = SUBJECT._module_init_call_candidate_closure(
            files, roots=("threading",), known_name_facts={"threading": fact}
        )
        target = SUBJECT._module_init_call_candidate_closure(
            files, roots=("threading",), known_name_facts={"threading": fact},
            trusted_function_name_facts={"threading": fact},
        )
        self.assertIn("native_branch", baseline[0])
        self.assertIn("crlock_branch", baseline[0])
        self.assertEqual(target[0], ("threading",))
        self.assertEqual(target[4], {"resolved": 2, "unknown": 0})

    def test_threading_crlock_fact_requires_unconditional_pinned_c_registration(self):
        source = (
            b"import _thread\n"
            b"try:\n    _CRLock = _thread.RLock\n"
            b"except AttributeError:\n    _CRLock = None\n"
        )
        module = (
            b'static PyType_Spec rlock_type_spec = { .name = "_thread.RLock" };\n'
            b"thread_module_exec(PyObject *module) {\n// RLock\n"
            b"PyType_FromSpec(&rlock_type_spec);\n"
            b"PyModule_AddType(module, rlock_type);\n}\n"
            b"thread_module_traverse\n"
        )
        pyconfig = b"#define WITH_THREAD 1\n"
        with patch.object(
            SUBJECT, "THREADING_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ), patch.object(
            SUBJECT, "THREAD_NATIVE_ID_MODULE_SHA256", hashlib.sha256(module).hexdigest()
        ), patch.object(
            SUBJECT, "TARGET_PYCONFIG_SHA256", hashlib.sha256(pyconfig).hexdigest()
        ), patch.dict(SUBJECT._TARGET_BUILTIN_MEMBERSHIP, {"_thread": True}):
            self.assertEqual(SUBJECT._target_threading_crlock_name_fact(
                {"threading.py": source}, module, pyconfig
            ), {"_CRLock": True})
            conditional = module.replace(b"// RLock", b"#if WITH_THREAD\n// RLock")
            with patch.object(
                SUBJECT, "THREAD_NATIVE_ID_MODULE_SHA256",
                hashlib.sha256(conditional).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_threading_crlock_name_fact(
                    {"threading.py": source}, conditional, pyconfig
                ), {})

    def test_target_module_init_call_scan_applies_imported_module_name_fact(self):
        files = {
            "entry.py": (
                b"if __name__ == '__main__':\n    import script_only\n"
            ),
            "script_only.py": b"VALUE = 1\n",
        }
        baseline = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",)
        )
        target = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",),
            known_name_facts={
                "entry": {"__name__": SUBJECT._IMPORTED_MODULE_NAME},
            },
        )
        self.assertEqual(baseline[0], ("entry", "script_only"))
        self.assertEqual(target[0], ("entry",))
        self.assertEqual(target[4], {"resolved": 1, "unknown": 0})

    def test_verified_source_name_fact_can_survive_a_star_import(self):
        files = {
            "entry.py": (
                b"from posix import *\n"
                b"if platform_name == 'nt':\n    import nt_branch\n"
                b"else:\n    import posix_branch\n"
            ),
            "posix.py": b"VALUE = 1\n",
            "nt_branch.py": b"VALUE = 2\n",
            "posix_branch.py": b"VALUE = 3\n",
        }
        facts = {"entry": {"platform_name": "posix"}}
        unknown = []
        unpreserved = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",), known_name_facts=facts,
            unknown_conditions=unknown,
        )
        self.assertIn("nt_branch", unpreserved[0])
        self.assertIn("posix_branch", unpreserved[0])
        self.assertEqual(len(unknown), 1)
        preserved_unknown = []
        preserved = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",), known_name_facts=facts,
            preserve_name_facts_after_star={"entry": ("platform_name",)},
            unknown_conditions=preserved_unknown,
        )
        self.assertIn("posix_branch", preserved[0])
        self.assertNotIn("nt_branch", preserved[0])
        self.assertEqual(preserved[4], {"resolved": 1, "unknown": 0})
        self.assertEqual(preserved_unknown, [])
        with self.assertRaisesRegex(ValueError, "UNTRUSTED_STAR_IMPORT_NAME_FACT"):
            SUBJECT._module_init_call_candidate_closure(
                files, roots=("entry",),
                preserve_name_facts_after_star={"entry": ("platform_name",)},
            )

    def test_os_boolean_fact_requires_stable_function_scope(self):
        source = (
            b"def _exists(name):\n    return name in globals()\n"
            b"_globals = globals()\n"
            b"def _read(name):\n    return name in _globals\n"
            b"supports_bytes_environ = True\n"
            b"def check():\n    return supports_bytes_environ\n"
        )
        fact = {"supports_bytes_environ": True}
        with patch.object(
            SUBJECT, "OS_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ):
            self.assertTrue(SUBJECT._target_os_function_name_facts_safe(
                {"os.py": source}, fact
            ))
            for unsafe in (
                source + b"def shadow(supports_bytes_environ):\n    return supports_bytes_environ\n",
                source + b"def reset():\n    global supports_bytes_environ\n"
                b"    supports_bytes_environ = False\n",
            ):
                with patch.object(
                    SUBJECT, "OS_SOURCE_SHA256", hashlib.sha256(unsafe).hexdigest()
                ):
                    self.assertFalse(SUBJECT._target_os_function_name_facts_safe(
                        {"os.py": unsafe}, fact
                    ))

    def test_os_createenviron_fact_is_bound_to_one_unshadowed_guard(self):
        source = (
            b"def _createenviron():\n"
            b"    if name == 'nt':\n        import nt_branch\n"
            b"    else:\n        import posix_branch\n"
            b"_createenviron()\n"
        )
        with patch.object(
            SUBJECT, "OS_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ):
            facts = SUBJECT._target_os_createenviron_line_facts(
                {"os.py": source}, {"name": "posix"}
            )
            self.assertEqual(facts, {2: False})
            for unsafe in (
                source.replace(b"def _createenviron():", b"def _createenviron(name):"),
                source.replace(b"    if name == 'nt':", b"    name = 'nt'\n    if name == 'nt':"),
            ):
                with patch.object(
                    SUBJECT, "OS_SOURCE_SHA256", hashlib.sha256(unsafe).hexdigest()
                ):
                    self.assertEqual(SUBJECT._target_os_createenviron_line_facts(
                        {"os.py": unsafe}, {"name": "posix"}
                    ), {})
        files = {
            "os.py": source,
            "nt_branch.py": b"VALUE = 1\n",
            "posix_branch.py": b"VALUE = 2\n",
        }
        baseline = SUBJECT._module_init_call_candidate_closure(
            files, roots=("os",)
        )
        target = SUBJECT._module_init_call_candidate_closure(
            files, roots=("os",), trusted_line_facts={"os": {2: False}}
        )
        self.assertIn("nt_branch", baseline[0])
        self.assertIn("posix_branch", baseline[0])
        self.assertEqual(target[0], ("os", "posix_branch"))
        self.assertEqual(target[4], {"resolved": 1, "unknown": 0})

    def test_codecs_dead_import_fact_survives_prior_star_import(self):
        source = (
            b"try:\n    from _codecs import *\n"
            b"except ImportError:\n    pass\n"
            b"_false = 0\n"
            b"if _false:\n    import encodings\n"
        )
        with patch.object(
            SUBJECT, "_CODECS_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ):
            line_facts = SUBJECT._target_codecs_false_guard_line_facts(
                {"codecs.py": source}
            )
            self.assertEqual(line_facts, {6: False})
            for unsafe in (
                source.replace(b"_false = 0", b"_false = 1"),
                source + b"_false = 0\n",
                source.replace(b"import encodings", b"import os"),
            ):
                with patch.object(
                    SUBJECT, "_CODECS_SOURCE_SHA256", hashlib.sha256(unsafe).hexdigest()
                ):
                    self.assertEqual(SUBJECT._target_codecs_false_guard_line_facts(
                        {"codecs.py": unsafe}
                    ), {})
        files = {"codecs.py": source, "encodings.py": b"VALUE = 1\n"}
        baseline = SUBJECT._module_init_call_candidate_closure(
            files, roots=("codecs",)
        )
        target = SUBJECT._module_init_call_candidate_closure(
            files, roots=("codecs",), trusted_line_facts={"codecs": {6: False}}
        )
        self.assertIn("encodings", baseline[0])
        self.assertEqual(target[0], ("codecs",))
        self.assertEqual(target[4], {"resolved": 1, "unknown": 0})

    def test_trusted_empty_for_fact_prunes_body_but_keeps_else(self):
        files = {
            "entry.py": (
                b"for item in items:\n"
                b"    import loop_body\n"
                b"else:\n"
                b"    import loop_else\n"
            ),
            "loop_body.py": b"VALUE = 1\n",
            "loop_else.py": b"VALUE = 2\n",
        }
        loop_line = ast.parse(files["entry.py"]).body[0].lineno
        baseline = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",)
        )
        target = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",),
            trusted_empty_for_facts={"entry": {loop_line: "items"}},
        )
        self.assertIn("loop_body", baseline[0])
        self.assertEqual(target[0], ("entry", "loop_else"))
        self.assertEqual(target[4], {"resolved": 0, "unknown": 0})
        with self.assertRaisesRegex(ValueError, "UNTRUSTED_EMPTY_FOR_FACT"):
            SUBJECT._module_init_call_candidate_closure(
                files, roots=("entry",),
                trusted_empty_for_facts={"entry": {loop_line: "other"}},
            )
        with self.assertRaisesRegex(ValueError, "UNTRUSTED_EMPTY_FOR_FACT"):
            SUBJECT._module_init_call_candidate_closure(
                files, roots=("entry",), trusted_empty_for_facts=[],
            )

    def test_warning_options_empty_fact_requires_pinned_sources_and_route(self):
        warnings_source = (
            b"_processoptions(sys.warnoptions)\n"
            b"def _processoptions(args):\n"
            b"    for arg in args:\n"
            b"        __import__(arg)\n"
        )
        preconfig_source = b"case 'I': cmdline->isolated = 1;"
        initconfig_source = (
            b"if (config->isolated) { config->use_environment = 0; }\n"
            b"if (config->use_environment) { status = "
            b"config_init_env_warnoptions(config, &env_warnoptions); }\n"
            b"case 'W': status = PyWideStringList_Append(warnoptions, _PyOS_optarg);"
        )
        worker_source = (
            b"def run_import_only(ordinal, worker_nonce):\n"
            b"    command = [sys.executable, '-I', '-S', '-B', '-X', 'utf8=1', '-c', "
            b"_worker_source(ordinal, worker_nonce)]\n"
            b"def _collect_process(command):\n"
            b"    child_env = os.environ.copy()\n"
            b"    child_env.pop('_PYTHON_SYSCONFIGDATA_NAME', None)\n"
            b"    try:\n"
            b"        return subprocess.Popen(command, env=child_env)\n"
            b"    except OSError:\n"
            b"        return None\n"
        )
        with patch.multiple(
            SUBJECT,
            PRECONFIG_C_SHA256=hashlib.sha256(preconfig_source).hexdigest(),
            INITCONFIG_C_SHA256=hashlib.sha256(initconfig_source).hexdigest(),
            IMPORT_USED_BYTES_PROBE_SHA256=hashlib.sha256(worker_source).hexdigest(),
            WARNINGS_SOURCE_SHA256=hashlib.sha256(warnings_source).hexdigest(),
        ):
            fact = SUBJECT._target_warning_options_empty_for_facts(
                {"warnings.py": warnings_source}, preconfig_source,
                initconfig_source, worker_source,
            )
            self.assertEqual(fact, {"warnings": {3: "args"}})
            changed_worker = worker_source.replace(b"'-I'", b"'-W', 'ignore'")
            self.assertEqual(SUBJECT._target_warning_options_empty_for_facts(
                {"warnings.py": warnings_source}, preconfig_source,
                initconfig_source, changed_worker,
            ), {})
            env_worker = worker_source.replace(
                b"env=child_env", b"env={}"
            )
            self.assertEqual(SUBJECT._target_warning_options_empty_for_facts(
                {"warnings.py": warnings_source}, preconfig_source,
                initconfig_source, env_worker,
            ), {})

    def test_warning_options_empty_fact_is_applied_without_image_save_input(self):
        tree = ast.parse(inspect.getsource(SUBJECT.analyze))
        assignments = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "_target_warning_options_empty_for_facts"
            and any(
                isinstance(target, ast.Name)
                and target.id == "target_warning_options_empty_for_facts"
                for target in node.targets
            )
        ]
        image_save_guards = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "target_image_save_path"
            and len(node.test.ops) == 1
            and isinstance(node.test.ops[0], ast.IsNot)
            and len(node.test.comparators) == 1
            and isinstance(node.test.comparators[0], ast.Constant)
            and node.test.comparators[0].value is None
        ]
        self.assertEqual(len(assignments), 1)
        self.assertEqual(len(image_save_guards), 1)
        self.assertLess(assignments[0].lineno, image_save_guards[0].lineno)

    def test_worker_startup_facts_are_applied_without_image_save_input(self):
        tree = ast.parse(inspect.getsource(SUBJECT.analyze))
        calls = {
            node.func.id: node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {
                "_target_worker_sysconfigdata_environment_fact",
                "_target_worker_sys_flag_facts",
                "_target_importlib_optimize_line_facts",
            }
        }
        image_save_guards = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "target_image_save_path"
            and len(node.test.ops) == 1
            and isinstance(node.test.ops[0], ast.IsNot)
            and len(node.test.comparators) == 1
            and isinstance(node.test.comparators[0], ast.Constant)
            and node.test.comparators[0].value is None
        ]
        self.assertEqual(set(calls), {
            "_target_worker_sysconfigdata_environment_fact",
            "_target_worker_sys_flag_facts",
            "_target_importlib_optimize_line_facts",
        })
        self.assertEqual(len(image_save_guards), 1)
        for call in calls.values():
            self.assertLess(call.lineno, image_save_guards[0].lineno)

    def test_importlib_optimize_fact_requires_pinned_isolated_unoptimized_route(self):
        preconfig_source = b"case 'I': cmdline->isolated = 1;"
        initconfig_source = (
            b"if (config->isolated) { config->use_environment = 0; }\n"
            b"static void config_init_defaults(void) { "
            b"config->optimization_level = 0; }\n"
            b"case 'O': config->optimization_level++;\n"
            b"static PyStatus config_read_env_vars(PyConfig *config) { "
            b"int use_env = config->use_environment; "
            b"_Py_get_env_flag(use_env, &config->optimization_level, "
            b"\"PYTHONOPTIMIZE\"); }"
        )
        worker_source = (
            b"def run_import_only(ordinal, worker_nonce):\n"
            b"    command = [sys.executable, '-I', '-S', '-B', '-X', 'utf8=1', '-c', "
            b"_worker_source(ordinal, worker_nonce)]\n"
            b"def _collect_process(command):\n"
            b"    child_env = os.environ.copy()\n"
            b"    child_env.pop('_PYTHON_SYSCONFIGDATA_NAME', None)\n"
            b"    try:\n"
            b"        return subprocess.Popen(command, env=child_env)\n"
            b"    except OSError:\n"
            b"        return None\n"
        )
        external_source = (
            b"if sys.flags.optimize == 0:\n"
            b"    optimization = ''\n"
        )
        with patch.multiple(
            SUBJECT,
            PRECONFIG_C_SHA256=hashlib.sha256(preconfig_source).hexdigest(),
            INITCONFIG_C_SHA256=hashlib.sha256(initconfig_source).hexdigest(),
            IMPORT_USED_BYTES_PROBE_SHA256=hashlib.sha256(worker_source).hexdigest(),
            IMPORTLIB_EXTERNAL_SOURCE_SHA256=hashlib.sha256(external_source).hexdigest(),
        ):
            fact = SUBJECT._target_importlib_optimize_line_facts(
                {"importlib/_bootstrap_external.py": external_source},
                preconfig_source, initconfig_source, worker_source,
            )
            self.assertEqual(fact, {1: True})
            guard = ast.parse(external_source).body[0].test
            self.assertTrue(SUBJECT._target_condition(
                guard, known_call_facts=(("sys.flags.optimize == 0", True),)
            ))
            optimized_worker = worker_source.replace(
                b"'-B', '-X', 'utf8=1', '-c'", b"'-B', '-O', '-X', 'utf8=1', '-c'"
            )
            self.assertEqual(SUBJECT._target_importlib_optimize_line_facts(
                {"importlib/_bootstrap_external.py": external_source},
                preconfig_source, initconfig_source, optimized_worker,
            ), {})
            env_worker = worker_source.replace(
                b"env=child_env", b"env={}"
            )
            self.assertEqual(SUBJECT._target_importlib_optimize_line_facts(
                {"importlib/_bootstrap_external.py": external_source},
                preconfig_source, initconfig_source, env_worker,
            ), {})

    def test_worker_sys_flag_facts_bind_pinned_startup_values(self):
        header, long_header, preconfig, initconfig, sys_module, worker = (
            self._worker_sys_flag_fact_fixture()
        )
        expected = (
            ("sys.flags.isolated", 1),
            ("sys.flags.no_site", 1),
            ("sys.flags.dont_write_bytecode", 1),
            ("sys.flags.ignore_environment", 1),
            ("sys.flags.safe_path", True),
            ("sys.flags.optimize", 0),
            ("sys.dont_write_bytecode", True),
            ("sys.flags.no_user_site", 1),
            ("sys.flags.debug", 0),
            ("sys.flags.inspect", 0),
            ("sys.flags.interactive", 0),
            ("sys.flags.verbose", 0),
            ("sys.flags.bytes_warning", 0),
            ("sys.flags.quiet", 0),
            ("sys.flags.hash_randomization", 1),
            ("sys.flags.dev_mode", False),
            ("sys.flags.utf8_mode", 1),
            ("sys.flags.warn_default_encoding", False),
            ("sys.flags.int_max_str_digits", 4300),
        )
        with patch.multiple(
            SUBJECT,
            PRECONFIG_HEADER_SHA256=hashlib.sha256(header).hexdigest(),
            LONG_HEADER_SHA256=hashlib.sha256(long_header).hexdigest(),
            PRECONFIG_C_SHA256=hashlib.sha256(preconfig).hexdigest(),
            INITCONFIG_C_SHA256=hashlib.sha256(initconfig).hexdigest(),
            SYS_MODULE_C_SHA256=hashlib.sha256(sys_module).hexdigest(),
            IMPORT_USED_BYTES_PROBE_SHA256=hashlib.sha256(worker).hexdigest(),
        ):
            facts = SUBJECT._target_worker_sys_flag_facts(
                header, long_header, preconfig, initconfig, sys_module, worker,
            )
            self.assertEqual(facts, expected)
            changed_header = header.replace(
                b".dev_mode=-1}",
                b".dev_mode=-1, .warn_default_encoding=1}",
            )
            with patch.object(
                SUBJECT, "PRECONFIG_HEADER_SHA256",
                hashlib.sha256(changed_header).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                    changed_header, long_header, preconfig, initconfig, sys_module, worker,
                ), expected[:-2] + expected[-1:])
            missing_preconfig_transfer = preconfig.replace(
                b"COPY_ATTR(warn_default_encoding);", b"",
            )
            with patch.object(
                SUBJECT, "PRECONFIG_C_SHA256",
                hashlib.sha256(missing_preconfig_transfer).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                    header, long_header, missing_preconfig_transfer, initconfig,
                    sys_module, worker,
                ), expected[:-2] + expected[-1:])
            changed_long_header = long_header.replace(b"4300", b"0")
            with patch.object(
                SUBJECT, "LONG_HEADER_SHA256",
                hashlib.sha256(changed_long_header).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                    header, changed_long_header, preconfig, initconfig,
                    sys_module, worker,
                ), expected[:-1])
            changed_digit_default = initconfig.replace(
                b"config->int_max_str_digits = _PY_LONG_DEFAULT_MAX_STR_DIGITS;",
                b"config->int_max_str_digits = 0;",
            )
            with patch.object(
                SUBJECT, "INITCONFIG_C_SHA256",
                hashlib.sha256(changed_digit_default).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                    header, long_header, preconfig, changed_digit_default,
                    sys_module, worker,
                ), expected[:-1])
            missing_sys_attribute = sys_module.replace(
                b'SET_SYS("dont_write_bytecode", '
                b"PyBool_FromLong(!config->write_bytecode));\n",
                b"",
            )
            with patch.object(
                SUBJECT, "SYS_MODULE_C_SHA256",
                hashlib.sha256(missing_sys_attribute).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                    header, long_header, preconfig, initconfig, missing_sys_attribute, worker,
                ), ())
            duplicate_update = sys_module + (
                b"int _PySys_UpdateConfig(PyThreadState *tstate) {\n"
                b"return 0;\n}\n"
            )
            with patch.object(
                SUBJECT, "SYS_MODULE_C_SHA256",
                hashlib.sha256(duplicate_update).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                    header, long_header, preconfig, initconfig, duplicate_update, worker,
                ), ())
            self.assertEqual(SUBJECT._target_s15_flags_field_candidate(facts), {
                "value": (1, 1, 1, 1, 1, 0),
                "source_fact_names": tuple(name for name, _ in expected[:6]),
                "worker_route_fact_count": 19,
                "runtime_flags_claimed": False,
                "evidence_scope": "STATIC_S15_FLAGS_FIELD_CANDIDATE",
            })
            self.assertIsNone(SUBJECT._target_s15_flags_field_candidate(
                facts[:-1] + (("sys.dont_write_bytecode", 1),)
            ))
            condition = ast.parse(
                "sys.flags.isolated == 1 and sys.flags.no_site == 1 and "
                "sys.flags.dont_write_bytecode == 1 and "
                "sys.flags.no_user_site == 1 and "
                "sys.flags.ignore_environment == 1 and "
                "sys.flags.safe_path is True and sys.flags.optimize == 0 and "
                "sys.dont_write_bytecode is True and sys.flags.debug == 0 and "
                "sys.flags.inspect == 0 and sys.flags.interactive == 0 and "
                "sys.flags.verbose == 0 and sys.flags.bytes_warning == 0 and "
                "sys.flags.quiet == 0 and "
                "sys.flags.hash_randomization == 1 and "
                "sys.flags.dev_mode is False and "
                "sys.flags.utf8_mode == 1 and "
                "sys.flags.warn_default_encoding is False and "
                "sys.flags.int_max_str_digits == 4300",
                mode="eval",
            ).body
            self.assertIs(
                SUBJECT._target_condition(condition, known_call_facts=facts), True,
            )
            untyped_condition = ast.parse(
                "sys.flags.no_site", mode="eval",
            ).body
            self.assertIsNone(SUBJECT._target_condition(
                untyped_condition, known_call_facts=facts,
            ))
            files = {
                "pkg.py": (
                    b"if not sys.flags.no_site:\n    import other_route\n"
                    b"else:\n    import isolated_route\n"
                ),
                "isolated_route.py": b"VALUE = True\n",
                "other_route.py": b"VALUE = False\n",
            }
            modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
                files, ("pkg",), known_call_facts=facts,
            )
            self.assertEqual(modules, ("isolated_route", "pkg"))
            self.assertEqual(conditions, {"resolved": 1, "unknown": 0})

    def test_s15_installation_tuple_joins_all_fifteen_static_fields(self):
        exe = "/usr/local/bin/python3.12"
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        schema = SUBJECT._target_s15_installation_schema_candidate(profile_source)
        self.assertIsNotNone(schema)
        normalized_profile = profile_source.replace(b"\r\n", b"\n")
        crlf_profile = normalized_profile.replace(b"\n", b"\r\n")
        self.assertEqual(
            SUBJECT._normalized_profile_source_sha256(crlf_profile),
            SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        )
        self.assertEqual(
            SUBJECT._target_s15_installation_schema_candidate(crlf_profile),
            schema,
        )
        changed_profile = profile_source.replace(
            b"assumption, platform, implementation, version, exe, target,",
            b"platform, assumption, implementation, version, exe, target,",
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(changed_profile),
        ):
            self.assertIsNone(
                SUBJECT._target_s15_installation_schema_candidate(changed_profile)
            )
        roots = (
            "/usr/local/lib/python3.12",
            "/usr/local/lib/python3.12/lib-dynload",
        )
        candidates = {
            "assumption": {
                "value": "DECLARED_SETUP_PYTHON_CONTROL_RUNTIME",
                "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
                "runtime_assumption_attested": False,
            },
            "platform": {"value": "linux", "runtime_platform_claimed": False},
            "implementation": {
                "value": "cpython", "runtime_implementation_claimed": False,
            },
            "version": {
                "value": (3, 12, 16), "runtime_version_claimed": False,
            },
            "image_paths": {
                "executable_field_candidate": {
                    "value": exe, "target": exe, "direct_regular_file": True,
                    "runtime_executable_claimed": False,
                },
                "executable_target_candidate": exe,
                "abi_field_candidate": {
                    "value": SUBJECT.TARGET_SYSCONFIGDATA_EXPECTED_VALUES["SOABI"],
                    "runtime_abi_claimed": False,
                },
            },
            "prefixes": {
                "values": ("/usr/local",) * 4,
                "runtime_prefixes_claimed": False,
            },
            "paths": {
                "value": (
                    "/usr/local/lib/python312.zip", roots[0], roots[1],
                ),
                "runtime_sys_path_claimed": False,
            },
            "roots": {"value": roots, "runtime_roots_claimed": False},
            "inert_zip": {
                "value": "/usr/local/lib/python312.zip",
                "runtime_membership_claimed": False,
            },
            "flags": {
                "value": (1, 1, 1, 1, 1, 0), "runtime_flags_claimed": False,
            },
            "finders": {
                "values": ("BUILTIN", "FROZEN", "PATH"),
                "runtime_finder_instances_claimed": False,
            },
            "hooks": {
                "values": ("ZIPIMPORTER", "FILEFINDER"),
                "runtime_hook_objects_claimed": False,
            },
            "files": {
                "value": (
                    (exe, 10, SUBJECT.TARGET_EXECUTABLE_SHA256),
                    ("/" + SUBJECT.PICKLE_EXTENSION_PATH, 20,
                     SUBJECT.PICKLE_EXTENSION_SHA256),
                ),
                "file_count": 2,
                "complete_file_list_claimed": False,
                "runtime_file_selection_claimed": False,
            },
            "schema": schema,
        }
        candidate = SUBJECT._target_s15_installation_tuple_candidate(candidates)
        self.assertIsNotNone(candidate)
        self.assertEqual(len(candidate["value"]), 15)
        self.assertEqual(candidate["field_order"], (
            "assumption", "platform", "implementation", "version",
            "executable", "executable_target", "prefixes", "abi", "paths",
            "roots", "inert_zip", "flags", "finders", "hooks", "files",
        ))
        self.assertEqual(
            candidate["schema_source_sha256"],
            SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        )
        self.assertFalse(candidate["runtime_record_claimed"])
        altered = dict(candidates)
        altered["flags"] = dict(candidates["flags"], runtime_flags_claimed=True)
        self.assertIsNone(SUBJECT._target_s15_installation_tuple_candidate(altered))

    def test_profile_controls_selection_contract_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        candidate = SUBJECT._target_controls_selection_contract_candidate(
            profile_source
        )
        self.assertEqual(candidate, {
            "allowed_names": ("__main__", "dgn007_import_runtime_profile"),
            "maximum_count": 2,
            "unique_names_required": True,
            "must_equal_control_module_rows": True,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "selected_controls_claimed": False,
            "evidence_scope": "STATIC_PROFILE_CONTROLS_SELECTION_CONTRACT_CANDIDATE",
        })
        changed = profile_source.replace(
            b"len(controls) <= 2 and len(set(controls)) == len(controls)",
            b"len(controls) <= 3 and len(set(controls)) == len(controls)",
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(changed),
        ):
            self.assertIsNone(
                SUBJECT._target_controls_selection_contract_candidate(changed)
            )
        assumption = {
            "value": "DECLARED_SETUP_PYTHON_CONTROL_RUNTIME",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "runtime_assumption_attested": False,
        }
        roots = {
            "value": (
                "/usr/local/lib/python3.12",
                "/usr/local/lib/python3.12/lib-dynload",
            ),
            "runtime_roots_claimed": False,
        }
        inert_zip = {
            "value": "/usr/local/lib/python312.zip",
            "runtime_membership_claimed": False,
        }
        selection = SUBJECT._target_profile_selection_inputs_candidate(
            profile_source, assumption, roots, inert_zip, candidate,
        )
        self.assertEqual(selection, {
            "field_order": ("assumption", "roots", "inert_zip", "controls"),
            "fixed_values": (
                "DECLARED_SETUP_PYTHON_CONTROL_RUNTIME",
                roots["value"], inert_zip["value"],
            ),
            "controls_contract": ("__main__", "dgn007_import_runtime_profile"),
            "controls_maximum_count": 2,
            "controls_must_equal_control_module_rows": True,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "selection_tuple_claimed": False,
            "selected_controls_claimed": False,
            "evidence_scope": "STATIC_PROFILE_SELECTION_INPUT_CONTRACT_CANDIDATE",
        })
        changed_selection_source = profile_source.replace(
            b"selection = (expected.assumption, expected.roots, expected.inert_zip, expected.controls)",
            b"selection = (expected.roots, expected.assumption, expected.inert_zip, expected.controls)",
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(changed_selection_source),
        ):
            self.assertIsNone(SUBJECT._target_profile_selection_inputs_candidate(
                changed_selection_source, assumption, roots, inert_zip, candidate,
            ))

    def test_profile_scalar_projection_schema_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        selection_inputs = {
            "field_order": ("assumption", "roots", "inert_zip", "controls"),
            "selection_tuple_claimed": False,
        }
        installation = {
            "field_order": ("assumption", "platform", "implementation"),
            "runtime_record_claimed": False,
        }
        candidate = SUBJECT._target_profile_scalar_projection_schema_candidate(
            profile_source, selection_inputs, installation,
        )
        self.assertEqual(candidate, {
            "output_order": ("selection", "installation", "modules"),
            "selection_field_order": selection_inputs["field_order"],
            "declared_profile_installation_field_order": installation["field_order"],
            "installation_projection_field_order": (
                "platform", "implementation", "version", "executable",
                "executable_target", "prefixes", "abi", "flags", "paths",
                "finders", "hooks", "files",
            ),
            "module_row_field_order": (
                "name", "module_name", "spec_name", "origin", "file", "kind",
                "locations", "loader", "loader_name", "loader_path", "aliases",
            ),
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "projected_values_claimed": False,
            "runtime_projection_claimed": False,
            "evidence_scope": "STATIC_PROFILE_SCALAR_PROJECTION_SCHEMA_CANDIDATE",
        })
        changed = profile_source.replace(
            b"return selection, installation, tuple(modules)",
            b"return installation, selection, tuple(modules)",
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(changed),
        ):
            self.assertIsNone(
                SUBJECT._target_profile_scalar_projection_schema_candidate(
                    changed, selection_inputs, installation,
                )
            )
        changed_installation = profile_source.replace(
            b"installation = (observation.platform, observation.implementation, observation.version,",
            b"installation = (observation.implementation, observation.platform, observation.version,",
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(changed_installation),
        ):
            self.assertIsNone(
                SUBJECT._target_profile_scalar_projection_schema_candidate(
                    changed_installation, selection_inputs, installation,
                )
            )

    def test_selected_profile_shape_contract_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        installation_schema = {
            "tuple_length": 15, "runtime_schema_claimed": False,
        }
        controls_contract = {
            "maximum_count": 2, "selected_controls_claimed": False,
        }
        candidate = SUBJECT._target_selected_profile_shape_contract_candidate(
            profile_source, installation_schema, controls_contract,
        )
        self.assertEqual(candidate, {
            "installation_arity": 15,
            "module_row_arity": 11,
            "token_bytes": 32,
            "maximum_controls": 2,
            "control_names_unique": True,
            "module_names_sorted_unique": True,
            "controls_equal_control_rows": True,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "selected_values_claimed": False,
            "profile_bound_claimed": False,
            "evidence_scope": "STATIC_SELECTED_PROFILE_SHAPE_CONTRACT_CANDIDATE",
        })
        changed = profile_source.replace(
            b"names == tuple(sorted(set(names)))",
            b"names == tuple(sorted(names))",
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(changed),
        ):
            self.assertIsNone(
                SUBJECT._target_selected_profile_shape_contract_candidate(
                    changed, installation_schema, controls_contract,
                )
            )

    def test_selected_profile_binder_flow_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        shape_contract = {"profile_bound_claimed": False}
        candidate = SUBJECT._target_selected_profile_binder_flow_candidate(
            profile_source, shape_contract,
        )
        self.assertEqual(candidate, {
            "validation_order": ("selected_shapes", "bind_selected"),
            "failure_reports": ("REJECTED_SELECTED_PROFILE", "PROFILE_BINDING_FAILED"),
            "success_report": "BOUND_SELECTED_PROFILE",
            "success_requires_expected_profile": True,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "profile_binding_claimed": False,
            "runtime_observation_claimed": False,
            "evidence_scope": "STATIC_SELECTED_PROFILE_BINDER_FLOW_CANDIDATE",
        })
        changed = profile_source.replace(
            b"fingerprints = _selected_shapes(installation, controls, modules, token)",
            b"fingerprints = ()",
        )
        binder_start = profile_source.index(b"def bind_selected_profile(")
        binder_source = profile_source[binder_start:]
        early_return = (
            profile_source[:binder_start]
            + binder_source.replace(b"    try:", b"    try:\n        return None", 1)
        )
        self.assertNotEqual(early_return, profile_source)
        for mutation in (changed, early_return):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(mutation),
            ):
                self.assertIsNone(
                    SUBJECT._target_selected_profile_binder_flow_candidate(
                        mutation, shape_contract,
                    )
                )

    def test_selected_profile_anchor_binding_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        binder_flow = {"profile_binding_claimed": False}
        candidate = SUBJECT._target_selected_profile_anchor_binding_candidate(
            profile_source, binder_flow,
        )
        self.assertEqual(candidate, {
            "cache_copy_before_module_rows": True,
            "module_row_anchor_fields": (
                "name", "origin", "file", "kind", "locations", "module", "spec", "loader",
            ),
            "module_projection_equality_checks": 2,
            "profile_shape_checks": 2,
            "cache_anchor_identity_rechecked": True,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "anchor_binding_claimed": False,
            "runtime_observation_claimed": False,
            "evidence_scope": "STATIC_SELECTED_PROFILE_ANCHOR_BINDING_CANDIDATE",
        })
        changed = profile_source.replace(
            b'_need(_project_scalars(expected, observation)[2] == modules, "MODULE_MISMATCH")',
            b'_need(True, "MODULE_MISMATCH")', 1,
        )
        binder_start = profile_source.index(b"def _bind_selected(")
        binder_body = profile_source[binder_start:]
        early_return = (
            profile_source[:binder_start]
            + binder_body.replace(
                b"    # Nur nach ",
                b"    return None\n    # Nur nach ",
                1,
            )
        )
        self.assertNotEqual(early_return, profile_source)
        for mutation in (changed, early_return):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(mutation),
            ):
                self.assertIsNone(
                    SUBJECT._target_selected_profile_anchor_binding_candidate(
                        mutation, binder_flow,
                    )
                )

    def test_selected_profile_observation_flow_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        anchor_binding = {"anchor_binding_claimed": False}
        candidate = SUBJECT._target_selected_profile_observation_flow_candidate(
            profile_source, anchor_binding,
        )
        self.assertEqual(candidate, {
            "validation_order": (
                "selected_shapes", "bind_selected", "observe_current_scalars",
                "compare_selected_projection", "capture_and_compare_final",
                "recheck_hooks", "recheck_selected_postconditions",
            ),
            "matched_report": "MATCHED_SELECTED_PROFILE",
            "rejected_report": "REJECTED_SELECTED_OBSERVATION",
            "selected_profile_observation_claimed": False,
            "runtime_observation_claimed": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_SELECTED_PROFILE_OBSERVATION_FLOW_CANDIDATE",
        })
        changed = profile_source.replace(
            b"_need(actual.scalars == selected, \"PROFILE_MISMATCH\")",
            b"_need(True, \"PROFILE_MISMATCH\")",
        )
        post_check = b"_selected_post(expected, runtime, cache, finders, hooks, providers)"
        final_post_position = profile_source.rfind(post_check)
        self.assertGreaterEqual(final_post_position, 0)
        missing_final_post = (
            profile_source[:final_post_position]
            + b"pass"
            + profile_source[final_post_position + len(post_check):]
        )
        early_return_anchor = b"fingerprints = _selected_shapes(installation, controls, modules, token)"
        observation_start = profile_source.index(b"def observe_selected_profile_scalars")
        early_return_body = profile_source[observation_start:]
        early_return = (
            profile_source[:observation_start]
            + early_return_body.replace(
                early_return_anchor,
                early_return_anchor + b"\n        return None",
                1,
            )
        )
        for index, mutation in enumerate((changed, missing_final_post, early_return)):
            with self.subTest(mutation=index):
                with patch.object(
                    SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                    SUBJECT._normalized_profile_source_sha256(mutation),
                ):
                    self.assertIsNone(
                        SUBJECT._target_selected_profile_observation_flow_candidate(
                            mutation, anchor_binding,
                        )
                    )

    def test_current_scalar_observation_flow_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        projection_schema = {"runtime_projection_claimed": False}
        candidate = SUBJECT._target_current_scalar_observation_flow_candidate(
            profile_source, projection_schema,
        )
        self.assertEqual(candidate, {
            "fresh_records_required": True,
            "profile_comparisons": 2,
            "filefinder_hook_observations": 2,
            "scalar_projection_returned_only_after_checks": True,
            "rejected_status": "REJECTED_PROFILE",
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "runtime_observation_claimed": False,
            "evidence_scope": "STATIC_CURRENT_SCALAR_OBSERVATION_FLOW_CANDIDATE",
        })
        changed = profile_source.replace(
            b"_compare(expected, observation)",
            b"pass",
        )
        observer_start = profile_source.index(b"def observe_current_interpreter_scalars")
        observer_source = profile_source[observer_start:]
        early_return = (
            profile_source[:observer_start]
            + observer_source.replace(
                b"    try:",
                b"    try:\n        return ScalarObservationResult(records.report)",
                1,
            )
        )
        self.assertNotEqual(early_return, profile_source)
        for mutation in (changed, early_return):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(mutation),
            ):
                self.assertIsNone(
                    SUBJECT._target_current_scalar_observation_flow_candidate(
                        mutation, projection_schema,
                    )
                )

    def test_fresh_record_capture_flow_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        candidate = SUBJECT._target_fresh_record_capture_flow_candidate(profile_source)
        self.assertEqual(candidate, {
            "capture_order": ("before_files", "after_files"),
            "bounded_read_chunk_bytes": 65536,
            "file_and_total_caps_required": True,
            "failure_returns_observation": False,
            "success_report": "MATCHED_DECLARED_BASELINE",
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "runtime_capture_claimed": False,
            "trust_attested_claimed": False,
            "evidence_scope": "STATIC_FRESH_RECORD_CAPTURE_FLOW_CANDIDATE",
        })
        changed = profile_source.replace(
            b"_compare(expected, after)",
            b"pass",
        )
        capture_start = profile_source.index(b"def observe_current_interpreter_records")
        capture_source = profile_source[capture_start:]
        early_return = (
            profile_source[:capture_start]
            + capture_source.replace(
                b"    try:",
                b"    try:\n        return None",
                1,
            )
        )
        self.assertNotEqual(early_return, profile_source)
        for mutation in (changed, early_return):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(mutation),
            ):
                self.assertIsNone(
                    SUBJECT._target_fresh_record_capture_flow_candidate(mutation)
                )

    def test_profile_capture_schema_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        candidate = SUBJECT._target_profile_capture_schema_candidate(profile_source)
        self.assertEqual(candidate, {
            "observation_field_order": (
                "token", "platform", "implementation", "version", "executable",
                "executable_target", "prefixes", "abi", "flags", "paths",
                "finders", "hooks", "modules", "files",
            ),
            "module_snapshot_sorted": True,
            "module_and_path_counts_bounded": True,
            "module_rows_delegate_to_module_builder": True,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "runtime_observation_claimed": False,
            "evidence_scope": "STATIC_PROFILE_CAPTURE_SCHEMA_CANDIDATE",
        })
        changed = profile_source.replace(
            b"sorted(snapshot.items())",
            b"snapshot.items()",
        )
        capture_start = profile_source.index(b"def _capture(")
        capture_source = profile_source[capture_start:]
        early_return = (
            profile_source[:capture_start]
            + capture_source.replace(
                b"    _need(type(sys.modules)",
                b"    return None\n    _need(type(sys.modules)",
                1,
            )
        )
        self.assertNotEqual(early_return, profile_source)
        for mutation in (changed, early_return):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(mutation),
            ):
                self.assertIsNone(
                    SUBJECT._target_profile_capture_schema_candidate(mutation)
                )

    def test_profile_module_record_builder_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        capture_schema = {"module_rows_delegate_to_module_builder": True}
        candidate = SUBJECT._target_profile_module_record_builder_candidate(
            profile_source, capture_schema,
        )
        self.assertEqual(candidate, {
            "accepted_module_type": "ModuleType",
            "module_name_and_spec_identity_checked": True,
            "frozen_name_aliases_bound": True,
            "loader_kinds": ("CONTROL", "BUILTIN", "FROZEN", "SOURCE", "EXTENSION"),
            "unknown_loader_rejected": True,
            "record_field_order": (
                "name", "origin", "file", "kind", "locations", "module", "spec", "loader",
            ),
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "runtime_modules_claimed": False,
            "evidence_scope": "STATIC_PROFILE_MODULE_RECORD_BUILDER_CANDIDATE",
        })
        changed = profile_source.replace(
            b'raise _Failure("UNKNOWN_LOADER")',
            b'kind = "SOURCE"',
        )
        module_start = profile_source.index(b"def _module(")
        module_source = profile_source[module_start:]
        early_return = (
            profile_source[:module_start]
            + module_source.replace(
                b"    _need(type(name) is str and type(module) is ModuleType)",
                b"    return None\n    _need(type(name) is str and type(module) is ModuleType)",
                1,
            )
        )
        self.assertNotEqual(early_return, profile_source)
        for mutation in (changed, early_return):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(mutation),
            ):
                self.assertIsNone(
                    SUBJECT._target_profile_module_record_builder_candidate(
                        mutation, capture_schema,
                    )
                )

    def test_profile_compare_contract_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        module_builder = {"runtime_modules_claimed": False}
        candidate = SUBJECT._target_profile_compare_contract_candidate(
            profile_source, module_builder,
        )
        self.assertEqual(candidate, {
            "interpreter_platform_version_flags_checked": True,
            "expected_observation_fields_compared": (
                "token", "executable", "executable_target", "prefixes", "abi", "paths", "files",
            ),
            "finder_and_hook_identity_checked": True,
            "module_row_values_and_anchor_identity_checked": True,
            "owned_modules_rejected": True,
            "control_and_source_roots_checked": True,
            "observation_paths_restricted": True,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "trust_established": False,
            "evidence_scope": "STATIC_PROFILE_COMPARE_CONTRACT_CANDIDATE",
        })
        changed = profile_source.replace(
            b"p == expected.inert_zip",
            b"True",
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(changed),
        ):
            self.assertIsNone(
                SUBJECT._target_profile_compare_contract_candidate(
                    changed, module_builder,
                )
            )
        early_return = profile_source.replace(
            b"    _shape(expected, True)",
            b"    return None\n    _shape(expected, True)",
            1,
        )
        self.assertNotEqual(early_return, profile_source)
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(early_return),
        ):
            self.assertIsNone(
                SUBJECT._target_profile_compare_contract_candidate(
                    early_return, module_builder,
                )
            )

    def test_profile_validation_report_flow_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        compare_contract = {"trust_established": False}
        candidate = SUBJECT._target_profile_validation_report_flow_candidate(
            profile_source, compare_contract,
        )
        self.assertEqual(candidate, {
            "compare_attempts": 1,
            "comparison_failure_status": "REJECTED_PROFILE",
            "malformed_record_issue": "INVALID_RECORD",
            "matched_status": "MATCHED_DECLARED_BASELINE",
            "trust_assumed_only_on_match": True,
            "trust_attested": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_PROFILE_VALIDATION_REPORT_FLOW_CANDIDATE",
        })
        changed = profile_source.replace(
            b'ProfileReport("MATCHED_DECLARED_BASELINE", "NONE", True)',
            b'ProfileReport("MATCHED_DECLARED_BASELINE", "NONE", False)',
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(changed),
        ):
            self.assertIsNone(
                SUBJECT._target_profile_validation_report_flow_candidate(
                    changed, compare_contract,
                )
            )
        early_return = profile_source.replace(
            b"        _compare(expected, observation)",
            b"        return None\n        _compare(expected, observation)",
            1,
        )
        self.assertNotEqual(early_return, profile_source)
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(early_return),
        ):
            self.assertIsNone(
                SUBJECT._target_profile_validation_report_flow_candidate(
                    early_return, compare_contract,
                )
            )

    def test_profile_candidate_chain_and_result_wiring_are_source_bound(self):
        scanner_source = TOOL.read_bytes()

        def chain_is_bound(source):
            bodies = SUBJECT.re.findall(
                rb"(?ms)^def analyze\(.*?(?=^def main\()",
                source,
            )
            if len(bodies) != 1:
                return False
            body = SUBJECT.re.sub(rb"\s+", b" ", bodies[0])
            assignments = (
                b"target_profile_scalar_projection_schema_candidate = ( _target_profile_scalar_projection_schema_candidate( runtime_profile_source, target_profile_selection_inputs_candidate, target_s15_installation_tuple_candidate, ) )",
                b"target_current_scalar_observation_flow_candidate = ( _target_current_scalar_observation_flow_candidate( runtime_profile_source, target_profile_scalar_projection_schema_candidate, ) )",
                b"target_fresh_record_capture_flow_candidate = ( _target_fresh_record_capture_flow_candidate(runtime_profile_source) )",
                b"target_profile_capture_schema_candidate = ( _target_profile_capture_schema_candidate(runtime_profile_source) )",
                b"target_profile_module_record_builder_candidate = ( _target_profile_module_record_builder_candidate( runtime_profile_source, target_profile_capture_schema_candidate, ) )",
                b"target_profile_compare_contract_candidate = ( _target_profile_compare_contract_candidate( runtime_profile_source, target_profile_module_record_builder_candidate, ) )",
                b"target_profile_validation_report_flow_candidate = ( _target_profile_validation_report_flow_candidate( runtime_profile_source, target_profile_compare_contract_candidate, ) )",
                b"target_profile_shape_contract_candidate = ( _target_profile_shape_contract_candidate( runtime_profile_source, target_profile_compare_contract_candidate, target_profile_capture_schema_candidate, ) )",
                b"target_profile_record_validators_candidate = ( _target_profile_record_validators_candidate( runtime_profile_source, target_profile_shape_contract_candidate, ) )",
                b"target_profile_path_contract_candidate = ( _target_profile_path_contract_candidate( runtime_profile_source, target_profile_record_validators_candidate, ) )",
                b"target_profile_primitive_validators_candidate = ( _target_profile_primitive_validators_candidate( runtime_profile_source, target_profile_path_contract_candidate, ) )",
                b"target_profile_failure_primitive_candidate = ( _target_profile_failure_primitive_candidate( runtime_profile_source, target_profile_primitive_validators_candidate, ) )",
                b"target_profile_report_schema_candidate = ( _target_profile_report_schema_candidate( runtime_profile_source, target_profile_failure_primitive_candidate, ) )",
                b"target_profile_model_schemas_candidate = ( _target_profile_model_schemas_candidate( runtime_profile_source, target_profile_report_schema_candidate, ) )",
                b"target_profile_record_model_schemas_candidate = ( _target_profile_record_model_schemas_candidate( runtime_profile_source, target_profile_model_schemas_candidate, ) )",
                b"target_profile_result_model_schemas_candidate = ( _target_profile_result_model_schemas_candidate( runtime_profile_source, target_profile_record_model_schemas_candidate, ) )",
                b"target_selected_profile_result_schemas_candidate = ( _target_selected_profile_result_schemas_candidate( runtime_profile_source, target_profile_result_model_schemas_candidate, ) )",
                b"target_profile_record_observation_flow_candidate = ( _target_profile_record_observation_flow_candidate( runtime_profile_source, target_profile_result_model_schemas_candidate, ) )",
            )
            if any(body.count(item) != 1 for item in assignments):
                return False
            if not all(body.index(left) < body.index(right)
                       for left, right in zip(assignments, assignments[1:])):
                return False
            result_fields = (
                b'"target_profile_scalar_projection_schema_candidate": ( target_profile_scalar_projection_schema_candidate )',
                b'"target_current_scalar_observation_flow_candidate": ( target_current_scalar_observation_flow_candidate )',
                b'"target_fresh_record_capture_flow_candidate": ( target_fresh_record_capture_flow_candidate )',
                b'"target_profile_capture_schema_candidate": ( target_profile_capture_schema_candidate )',
                b'"target_profile_module_record_builder_candidate": ( target_profile_module_record_builder_candidate )',
                b'"target_profile_compare_contract_candidate": ( target_profile_compare_contract_candidate )',
                b'"target_profile_validation_report_flow_candidate": ( target_profile_validation_report_flow_candidate )',
                b'"target_profile_shape_contract_candidate": ( target_profile_shape_contract_candidate )',
                b'"target_profile_record_validators_candidate": ( target_profile_record_validators_candidate )',
                b'"target_profile_path_contract_candidate": ( target_profile_path_contract_candidate )',
                b'"target_profile_primitive_validators_candidate": ( target_profile_primitive_validators_candidate )',
                b'"target_profile_failure_primitive_candidate": ( target_profile_failure_primitive_candidate )',
                b'"target_profile_report_schema_candidate": ( target_profile_report_schema_candidate )',
                b'"target_profile_model_schemas_candidate": ( target_profile_model_schemas_candidate )',
                b'"target_profile_record_model_schemas_candidate": ( target_profile_record_model_schemas_candidate )',
                b'"target_profile_result_model_schemas_candidate": ( target_profile_result_model_schemas_candidate )',
                b'"target_selected_profile_result_schemas_candidate": ( target_selected_profile_result_schemas_candidate )',
                b'"target_profile_record_observation_flow_candidate": ( target_profile_record_observation_flow_candidate )',
            )
            return all(body.count(item) == 1 for item in result_fields)

        self.assertTrue(chain_is_bound(scanner_source))
        newline = b"\r\n" if b"\r\n" in scanner_source else b"\n"
        broken_edge = scanner_source.replace(
            b"            target_profile_module_record_builder_candidate,"
            + newline + b"        )",
            b"            target_profile_capture_schema_candidate,"
            + newline + b"        )",
            1,
        )
        self.assertNotEqual(broken_edge, scanner_source)
        self.assertFalse(chain_is_bound(broken_edge))
        broken_scalar_edge = scanner_source.replace(
            b"            target_profile_scalar_projection_schema_candidate,"
            + newline + b"        )",
            b"            target_profile_selection_inputs_candidate,"
            + newline + b"        )",
            1,
        )
        self.assertNotEqual(len(broken_scalar_edge), len(scanner_source))
        self.assertFalse(chain_is_bound(broken_scalar_edge))
        dropped_result = scanner_source.replace(
            b'"target_profile_compare_contract_candidate": (' + newline
            + b"            target_profile_compare_contract_candidate" + newline
            + b"        ),",
            b"",
            1,
        )
        self.assertNotEqual(len(dropped_result), len(scanner_source))
        self.assertFalse(chain_is_bound(dropped_result))
        dropped_parallel_result = scanner_source.replace(
            b'"target_current_scalar_observation_flow_candidate": (' + newline
            + b"            target_current_scalar_observation_flow_candidate" + newline
            + b"        ),",
            b"",
            1,
        )
        self.assertNotEqual(len(dropped_parallel_result), len(scanner_source))
        self.assertFalse(chain_is_bound(dropped_parallel_result))

        def report_is_candidate_only(source):
            bodies = SUBJECT.re.findall(
                rb"(?ms)^def main\(\):\r?\n(?P<body>.*?)(?=^if __name__|\Z)",
                source,
            )
            if len(bodies) != 1:
                return False
            body = SUBJECT.re.sub(rb"\s+", b" ", bodies[0])
            return (
                body.count(
                    b'print(json.dumps({"status": "CANDIDATES_ONLY", **result}, separators=(",", ":")))'
                ) == 1
                and body.count(
                    b'print(json.dumps({"status": "NOT_PROVEN", "issue": "SOURCE_INPUT_REJECTED"}, separators=(",", ":")))'
                ) == 1
                and body.count(b"return 0") == 1
            )

        self.assertTrue(report_is_candidate_only(scanner_source))
        promoted_report = scanner_source.replace(
            b'"status": "CANDIDATES_ONLY"',
            b'"status": "PROFILE_VALIDATED"',
            1,
        )
        self.assertNotEqual(len(promoted_report), len(scanner_source))
        self.assertFalse(report_is_candidate_only(promoted_report))

    def test_profile_shape_contract_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        candidate = SUBJECT._target_profile_shape_contract_candidate(
            profile_source,
            {"trust_established": False},
            {"runtime_observation_claimed": False},
        )
        self.assertEqual(candidate, {
            "accepted_value_types": ("DeclaredProfile", "Observation"),
            "shared_field_contracts": (
                "token_32_bytes", "text_fields", "version_3_ints_0_to_999",
                "prefixes_4_absolute_paths", "absolute_executable_targets",
                "three_known_finders", "two_known_hooks", "module_records", "file_records",
            ),
            "declared_only_contracts": (
                "fixed_assumption", "two_unique_roots", "bounded_control_names",
                "absolute_inert_zip", "file_paths_bound_to_target_or_roots",
            ),
            "observation_only_contracts": ("text_platform", "six_binary_flags"),
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "input_validation_claimed": False,
            "runtime_observation_claimed": False,
            "evidence_scope": "STATIC_PROFILE_SHAPE_CONTRACT_CANDIDATE",
        })
        changed = profile_source.replace(
            b"len(value.controls) <= 2",
            b"len(value.controls) <= 3",
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(changed),
        ):
            self.assertIsNone(SUBJECT._target_profile_shape_contract_candidate(
                changed,
                {"trust_established": False},
                {"runtime_observation_claimed": False},
            ))
        newline = b"\r\n" if b"\r\n" in profile_source else b"\n"
        early_return = profile_source.replace(
            b"def _shape(value, expected):" + newline + b"    _need(",
            b"def _shape(value, expected):" + newline
            + b"    return None" + newline + b"    _need(",
            1,
        )
        self.assertNotEqual(early_return, profile_source)
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(early_return),
        ):
            self.assertIsNone(SUBJECT._target_profile_shape_contract_candidate(
                early_return,
                {"trust_established": False},
                {"runtime_observation_claimed": False},
            ))

    def test_profile_record_validators_are_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        shape_contract = {"input_validation_claimed": False}
        candidate = SUBJECT._target_profile_record_validators_candidate(
            profile_source, shape_contract,
        )
        self.assertEqual(candidate, {
            "module_record_invariants": (
                "typed_module_and_spec", "loader_kind_and_coherence", "module_namespace_identity",
                "control_name_constraints", "sorted_unique_names", "frozen_companion_identity",
            ),
            "file_record_invariants": (
                "maximum_two_records", "absolute_unique_paths", "bounded_file_and_total_size",
                "lowercase_sha256_hex_64",
            ),
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "records_validated_claimed": False,
            "runtime_inventory_claimed": False,
            "evidence_scope": "STATIC_PROFILE_RECORD_VALIDATORS_CANDIDATE",
        })
        changed_names = profile_source.replace(
            b"names == sorted(set(names))",
            b"names == sorted(names)",
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(changed_names),
        ):
            self.assertIsNone(SUBJECT._target_profile_record_validators_candidate(
                changed_names, shape_contract,
            ))
        changed_digest = profile_source.replace(
            b'0123456789abcdef',
            b'0123456789ABCDEF',
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(changed_digest),
        ):
            self.assertIsNone(SUBJECT._target_profile_record_validators_candidate(
                changed_digest, shape_contract,
            ))
        newline = b"\r\n" if b"\r\n" in profile_source else b"\n"
        early_record_return = profile_source.replace(
            b"def _records(value):" + newline + b"    _need(",
            b"def _records(value):" + newline
            + b"    return None" + newline + b"    _need(",
            1,
        )
        self.assertNotEqual(early_record_return, profile_source)
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(early_record_return),
        ):
            self.assertIsNone(SUBJECT._target_profile_record_validators_candidate(
                early_record_return, shape_contract,
            ))
        early_file_return = profile_source.replace(
            b"def _files(value):" + newline + b"    _need(",
            b"def _files(value):" + newline
            + b"    return None" + newline + b"    _need(",
            1,
        )
        self.assertNotEqual(early_file_return, profile_source)
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(early_file_return),
        ):
            self.assertIsNone(SUBJECT._target_profile_record_validators_candidate(
                early_file_return, shape_contract,
            ))

    def test_profile_path_contracts_are_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        record_contract = {"records_validated_claimed": False}
        candidate = SUBJECT._target_profile_path_contract_candidate(
            profile_source, record_contract,
        )
        self.assertEqual(candidate, {
            "absolute_path_invariants": (
                "bounded_text", "leading_slash", "no_double_slash", "no_nul",
                "no_trailing_slash_except_root", "no_dot_segments", "path_mismatch",
            ),
            "root_containment_invariants": (
                "absolute_path", "no_dot_segments", "component_boundary_containment",
            ),
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "path_validation_claimed": False,
            "host_attestation_claimed": False,
            "evidence_scope": "STATIC_PROFILE_PATH_CONTRACT_CANDIDATE",
        })
        for changed in (
            profile_source.replace(b'"//" not in value', b"True"),
            profile_source.replace(
                b'path.startswith(root.rstrip("/") + "/")',
                b'path.startswith(root.rstrip("/"))',
            ),
        ):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_profile_path_contract_candidate(
                    changed, record_contract,
                ))
        newline = b"\r\n" if b"\r\n" in profile_source else b"\n"
        early_return = profile_source.replace(
            b"def _absolute(value):" + newline + b"    _text(value)",
            b"def _absolute(value):" + newline
            + b"    return None" + newline + b"    _text(value)",
            1,
        )
        self.assertNotEqual(early_return, profile_source)
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(early_return),
        ):
            self.assertIsNone(SUBJECT._target_profile_path_contract_candidate(
                early_return, record_contract,
            ))

    def test_profile_primitive_validators_are_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        path_contract = {"path_validation_claimed": False}
        candidate = SUBJECT._target_profile_primitive_validators_candidate(
            profile_source, path_contract,
        )
        self.assertEqual(candidate, {
            "text_invariants": (
                "exact_str_type", "character_length_cap", "utf8_byte_length_cap",
            ),
            "string_tuple_invariants": (
                "exact_tuple_type", "record_count_cap", "each_item_text_validated",
            ),
            "failure_helper_invariants": ("invalid_condition_raises_failure",),
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "primitive_validation_claimed": False,
            "profile_input_validation_claimed": False,
            "evidence_scope": "STATIC_PROFILE_PRIMITIVE_VALIDATORS_CANDIDATE",
        })
        newline = b"\r\n" if b"\r\n" in profile_source else b"\n"
        for name, expected_shape in (
            (b"_text", b"_need(type(value) is str"),
            (b"_strings", b"_need(type(value) is tuple"),
        ):
            early_return = profile_source.replace(
                b"def " + name + b"(value):" + newline + b"    " + expected_shape,
                b"def " + name + b"(value):" + newline
                + b"    return None" + newline + b"    " + expected_shape,
                1,
            )
            self.assertNotEqual(early_return, profile_source)
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(early_return),
            ):
                self.assertIsNone(SUBJECT._target_profile_primitive_validators_candidate(
                    early_return, path_contract,
                ))
        early_need_return = profile_source.replace(
            b"def _need(condition, issue=\"INVALID_RECORD\"):" + newline
            + b"    if not condition:",
            b"def _need(condition, issue=\"INVALID_RECORD\"):" + newline
            + b"    return None" + newline + b"    if not condition:",
            1,
        )
        self.assertNotEqual(early_need_return, profile_source)
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(early_need_return),
        ):
            self.assertIsNone(SUBJECT._target_profile_primitive_validators_candidate(
                early_need_return, path_contract,
            ))
        for changed in (
            profile_source.replace(
                b'_need(len(value.encode("utf-8")) <= MAX_FIELD)', b"pass",
            ),
            profile_source.replace(
                b"type(value) is tuple and len(value) <= MAX_RECORDS",
                b"isinstance(value, tuple) and len(value) <= MAX_RECORDS",
            ),
        ):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_profile_primitive_validators_candidate(
                    changed, path_contract,
                ))

    def test_profile_failure_primitive_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        primitive_contract = {"profile_input_validation_claimed": False}
        candidate = SUBJECT._target_profile_failure_primitive_candidate(
            profile_source, primitive_contract,
        )
        self.assertEqual(candidate, {
            "failure_class": "_Failure_subclass_of_ValueError",
            "default_issue": "INVALID_RECORD",
            "false_condition_behavior": "raise_failure_with_issue",
            "input_validation_claimed": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_PROFILE_FAILURE_PRIMITIVE_CANDIDATE",
        })
        for changed in (
            profile_source.replace(b'issue="INVALID_RECORD"', b'issue="UNKNOWN"'),
            profile_source.replace(
                b"raise _Failure(issue)", b"raise _Failure(\"INVALID_RECORD\")",
            ),
        ):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_profile_failure_primitive_candidate(
                    changed, primitive_contract,
                ))

    def test_profile_report_schema_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        failure_contract = {"input_validation_claimed": False}
        candidate = SUBJECT._target_profile_report_schema_candidate(
            profile_source, failure_contract,
        )
        self.assertEqual(candidate, {
            "report_fields": (
                "status", "issue", "trust_assumed", "trust_attested",
                "runtime_attested", "import_used_bytes_attested", "method_approved",
            ),
            "attestation_and_approval_defaults_false": True,
            "attestation_fields_not_init_parameters": True,
            "profile_validation_claimed": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_PROFILE_REPORT_SCHEMA_CANDIDATE",
        })
        changed = profile_source.replace(
            b"runtime_attested: bool = field(default=False, init=False)",
            b"runtime_attested: bool = field(default=True, init=False)",
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(changed),
        ):
            self.assertIsNone(SUBJECT._target_profile_report_schema_candidate(
                changed, failure_contract,
            ))

    def test_profile_model_schemas_are_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        report_schema = {"profile_validation_claimed": False}
        candidate = SUBJECT._target_profile_model_schemas_candidate(
            profile_source, report_schema,
        )
        declared_fields = (
            "assumption", "token", "implementation", "version", "executable",
            "executable_target", "prefixes", "abi", "paths", "roots",
            "inert_zip", "controls", "finders", "hooks", "modules", "files",
        )
        observation_fields = (
            "token", "platform", "implementation", "version", "executable",
            "executable_target", "prefixes", "abi", "flags", "paths",
            "finders", "hooks", "modules", "files",
        )
        self.assertEqual(candidate, {
            "declared_profile_fields": declared_fields,
            "observation_fields": observation_fields,
            "both_dataclasses_frozen": True,
            "profile_validation_claimed": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_PROFILE_MODEL_SCHEMAS_CANDIDATE",
        })
        changed_field = profile_source.replace(b"    platform: str", b"    unknown: str")
        changed_decorator = profile_source.replace(
            b"@dataclass(frozen=True)", b"@dataclass",
        )
        for changed in (changed_field, changed_decorator):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_profile_model_schemas_candidate(
                    changed, report_schema,
                ))

    def test_profile_record_model_schemas_are_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        model_schema = {"profile_validation_claimed": False}
        candidate = SUBJECT._target_profile_record_model_schemas_candidate(
            profile_source, model_schema,
        )
        self.assertEqual(candidate, {
            "module_record_fields": (
                "name", "origin", "file", "kind", "locations", "module", "spec", "loader",
            ),
            "file_digest_fields": ("path", "size", "sha256"),
            "both_dataclasses_frozen": True,
            "record_validation_claimed": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_PROFILE_RECORD_MODEL_SCHEMAS_CANDIDATE",
        })
        changed_field = profile_source.replace(b"    sha256: str", b"    digest: str")
        changed_decorator = profile_source.replace(
            b"@dataclass(frozen=True)", b"@dataclass",
        )
        for changed in (changed_field, changed_decorator):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_profile_record_model_schemas_candidate(
                    changed, model_schema,
                ))

    def test_profile_result_model_schemas_are_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        record_model_schema = {"record_validation_claimed": False}
        candidate = SUBJECT._target_profile_result_model_schemas_candidate(
            profile_source, record_model_schema,
        )
        self.assertEqual(candidate, {
            "observation_result_fields": ("report", "observation"),
            "scalar_observation_result_fields": ("report", "scalars"),
            "both_dataclasses_frozen": True,
            "observation_claimed": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_PROFILE_RESULT_MODEL_SCHEMAS_CANDIDATE",
        })
        changed_field = profile_source.replace(
            b"    scalars: tuple | None", b"    snapshot: tuple | None",
        )
        changed_decorator = profile_source.replace(
            b"@dataclass(frozen=True)", b"@dataclass",
        )
        for changed in (changed_field, changed_decorator):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_profile_result_model_schemas_candidate(
                    changed, record_model_schema,
                ))

    def test_selected_profile_result_schemas_are_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        result_model_schema = {"observation_claimed": False}
        candidate = SUBJECT._target_selected_profile_result_schemas_candidate(
            profile_source, result_model_schema,
        )
        self.assertEqual(candidate, {
            "bound_profile_result_fields": (
                "report", "profile", "validation_scope",
            ),
            "selected_scalar_observation_result_fields": (
                "report", "profile", "scalars", "validation_scope",
            ),
            "private_dataclasses_frozen_slotted_repr_hidden": True,
            "validation_scope": "PROJECT_SEMANTIC",
            "runtime_observation_claimed": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_SELECTED_PROFILE_RESULT_SCHEMAS_CANDIDATE",
        })
        changed_scope = profile_source.replace(
            b'validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)',
            b'validation_scope: str = field(default="TRUSTED", init=False)',
        )
        changed_decorator = profile_source.replace(
            b"@dataclass(frozen=True, slots=True, repr=False)",
            b"@dataclass(frozen=True, slots=True)",
        )
        for changed in (changed_scope, changed_decorator):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_selected_profile_result_schemas_candidate(
                    changed, result_model_schema,
                ))

    def test_profile_record_observation_flow_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        result_schema = {"observation_claimed": False}
        candidate = SUBJECT._target_profile_record_observation_flow_candidate(
            profile_source, result_schema,
        )
        self.assertEqual(candidate, {
            "capture_guards_and_order": (
                "linux_platform", "profile_shape", "root_and_executable_identity",
                "inert_zip_absence", "pre_capture_and_compare", "bounded_regular_file_hashes",
                "post_capture_and_compare", "fail_closed_reports",
            ),
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "runtime_observation_claimed": False,
            "trust_attested": False,
            "evidence_scope": "STATIC_PROFILE_RECORD_OBSERVATION_FLOW_CANDIDATE",
        })
        for changed in (
            profile_source.replace(
                b"not os.path.islink(item.path) and os.path.isfile(item.path)",
                b"os.path.isfile(item.path)",
            ),
            profile_source.replace(
                b"        _compare(expected, before)", b"        pass",
            ),
        ):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_profile_record_observation_flow_candidate(
                    changed, result_schema,
                ))

    def test_selected_profile_post_contract_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        observation_flow = {"runtime_observation_claimed": False}
        candidate = SUBJECT._target_selected_profile_post_contract_candidate(
            profile_source, observation_flow,
        )
        self.assertEqual(candidate, {
            "runtime_post_checks": (
                "implementation_namespace", "version_shape_and_range", "startup_flag_types_and_values",
                "bytecode_flag", "bounded_paths", "linux_profile_tuple_match",
            ),
            "selected_post_anchor_checks": (
                "provider_identity", "runtime_values", "container_identity", "finder_and_hook_identity",
                "module_cache_identity", "local_module_shape", "profile_shape",
            ),
            "post_observation_claimed": False,
            "runtime_attested": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_SELECTED_PROFILE_POST_CONTRACT_CANDIDATE",
        })
        newline = b"\r\n" if b"\r\n" in profile_source else b"\n"
        provider_check = (
            b'    _need(sys is runtime and os is providers[0] and sysconfig is providers[1], '
            b'"PROVIDER_MISMATCH")'
        )
        post_order = newline.join((
            provider_check,
            b"    keys = [0]",
            b"    current = _selected_containers(runtime, keys)",
        ))
        reordered_post = newline.join((
            b"    keys = [0]",
            b"    current = _selected_containers(runtime, keys)",
            provider_check,
        ))
        changed_order = profile_source.replace(post_order, reordered_post, 1)
        self.assertNotEqual(changed_order, profile_source)
        for changed in (
            profile_source.replace(
                b"(1, 1, 1, 1, 1, 0), expected.paths",
                b"(1, 1, 1, 1, 0, 0), expected.paths",
            ),
            profile_source.replace(
                b"_scalar_text(path)", b"str(path)",
            ),
            profile_source.replace(
                b"_scalar_text(value)", b"str(value)",
            ),
            profile_source.replace(
                b"version = tuple(version[:3])",
                b"version = tuple(version[:2])",
            ),
            profile_source.replace(
                b"all(0 <= number <= 1 for number in values)",
                b"all(number >= 0 for number in values)",
            ),
            profile_source.replace(
                b"paths = tuple(paths)", b"paths = tuple(sorted(paths))",
            ),
            profile_source.replace(
                b"_need(sys is runtime and os is providers[0] and sysconfig is providers[1], \"PROVIDER_MISMATCH\")",
                b"pass",
            ),
            changed_order,
        ):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_selected_profile_post_contract_candidate(
                    changed, observation_flow,
                ))

    def test_selected_hook_post_contract_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        observation_flow = {"runtime_observation_claimed": False}
        candidate = SUBJECT._target_selected_hook_post_contract_candidate(
            profile_source, observation_flow,
        )
        self.assertEqual(candidate, {
            "hook_identity_fields": ("finder", "loader", "path"),
            "hook_record_field_comparison": ("identity", "identity", "value"),
            "hook_mutation_rejected": True,
            "runtime_hook_observation_claimed": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_SELECTED_HOOK_POST_CONTRACT_CANDIDATE",
        })
        changed = profile_source.replace(
            b"a[0] is b[0] and a[1] is b[1] and a[2] == b[2]",
            b"a[0] is b[0] and a[1] is b[1]",
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            SUBJECT._normalized_profile_source_sha256(changed),
        ):
            self.assertIsNone(SUBJECT._target_selected_hook_post_contract_candidate(
                changed, observation_flow,
            ))

    def test_filefinder_hook_contract_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        observation_flow = {"runtime_observation_claimed": False}
        candidate = SUBJECT._target_filefinder_hook_contract_candidate(
            profile_source, observation_flow,
        )
        self.assertEqual(candidate, {
            "finder_hook_anchors": (
                "frozen_importlib_external_module", "FileFinder_class", "classmethod_path_hook",
                "factory_code_constant", "known_hook_globals_and_closure",
            ),
            "loader_detail_order": (
                "ExtensionFileLoader", "SourceFileLoader", "SourcelessFileLoader",
            ),
            "suffix_lists_bound": (
                "EXTENSION_SUFFIXES", "SOURCE_SUFFIXES", "BYTECODE_SUFFIXES",
            ),
            "runtime_hook_claimed": False,
            "trust_attested": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_FILEFINDER_HOOK_CONTRACT_CANDIDATE",
        })
        for changed in (
            profile_source.replace(
                b'known.__code__.co_freevars == ("cls", "loader_details")',
                b'known.__code__.co_freevars == ("cls",)',
            ),
            profile_source.replace(
                b'("ExtensionFileLoader", "SourceFileLoader", "SourcelessFileLoader")',
                b'("SourceFileLoader", "ExtensionFileLoader", "SourcelessFileLoader")',
            ),
        ):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_filefinder_hook_contract_candidate(
                    changed, observation_flow,
                ))

    def test_profile_scalar_projection_contract_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        filefinder_contract = {"runtime_hook_claimed": False}
        candidate = SUBJECT._target_profile_scalar_projection_contract_candidate(
            profile_source, filefinder_contract,
        )
        self.assertEqual(candidate, {
            "scalar_form": ("bounded_text", "no_nul"),
            "projection_sections": ("selection", "installation", "module_rows"),
            "control_and_root_checks": True,
            "loader_and_alias_identity_checks": True,
            "module_row_field_count": 11,
            "runtime_projection_claimed": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_PROFILE_SCALAR_PROJECTION_CONTRACT_CANDIDATE",
        })
        for changed in (
            profile_source.replace(b'"\\x00" not in value', b"True"),
            profile_source.replace(
                b"a.module is b.module and a.spec is b.spec",
                b"a.module is b.module",
            ),
        ):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_profile_scalar_projection_contract_candidate(
                    changed, filefinder_contract,
                ))

    def test_selected_shape_primitives_are_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        selected_shape_contract = {"selected_values_claimed": False}
        candidate = SUBJECT._target_selected_shape_primitives_candidate(
            profile_source, selected_shape_contract,
        )
        self.assertEqual(candidate, {
            "tree_limits": {"nodes": 16368, "depth": 8, "tuple_items": "MAX_RECORDS"},
            "accepted_leaf_types": ("str", "NoneType", "int_exact"),
            "tuple_type": "exact_tuple_with_optional_exact_size",
            "integer_type": "exact_int_inclusive_range",
            "selected_shape_validation_claimed": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_SELECTED_SHAPE_PRIMITIVES_CANDIDATE",
        })
        for changed in (
            profile_source.replace(
                b"count <= 16368 and depth <= 8", b"count <= 16368",
            ),
            profile_source.replace(
                b"type(value) is tuple and len(value) <= MAX_RECORDS",
                b"isinstance(value, tuple) and len(value) <= MAX_RECORDS",
            ),
        ):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_selected_shape_primitives_candidate(
                    changed, selected_shape_contract,
                ))

    def test_selected_namespace_contract_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        shape_primitives = {"selected_shape_validation_claimed": False}
        candidate = SUBJECT._target_selected_namespace_contract_candidate(
            profile_source, shape_primitives,
        )
        self.assertEqual(candidate, {
            "namespace_type": "exact_dict",
            "namespace_and_key_budget": 16368,
            "key_type": "exact_str",
            "shared_budget_increment_per_key": True,
            "scalar_key_validation": True,
            "selected_namespace_validation_claimed": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_SELECTED_NAMESPACE_CONTRACT_CANDIDATE",
        })
        for changed in (
            profile_source.replace(
                b"budget[0] + len(namespace) <= 16368",
                b"budget[0] + len(namespace) <= 16369",
            ),
            profile_source.replace(
                b"type(key) is str", b"isinstance(key, str)",
            ),
        ):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_selected_namespace_contract_candidate(
                    changed, shape_primitives,
                ))

    def test_selected_anchor_contract_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        namespace_contract = {"selected_namespace_validation_claimed": False}
        candidate = SUBJECT._target_selected_anchor_contract_candidate(
            profile_source, namespace_contract,
        )
        self.assertEqual(candidate, {
            "module_type": "exact_ModuleType",
            "spec_type": "exact_ModuleSpec_or_none",
            "loader_types": ("BuiltinImporter", "FrozenImporter", "SourceFileLoader", "ExtensionFileLoader", "none"),
            "module_cache": "exact_dict_with_sorted_exact_name_set",
            "namespace_budget_shared": True,
            "selected_anchor_validation_claimed": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_SELECTED_ANCHOR_CONTRACT_CANDIDATE",
        })
        for changed in (
            profile_source.replace(
                b"type(loader) in (SourceFileLoader, ExtensionFileLoader)",
                b"isinstance(loader, (SourceFileLoader, ExtensionFileLoader))",
            ),
            profile_source.replace(
                b"_scalar_text(path)", b"str(path)",
            ),
            profile_source.replace(
                b"len(cache) == len(names)", b"len(cache) <= len(names)",
            ),
        ):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_selected_anchor_contract_candidate(
                    changed, namespace_contract,
                ))

    def test_selected_container_contract_is_source_bound(self):
        profile_source = (
            Path(__file__).resolve().parents[2]
            / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
        ).read_bytes()
        anchor_contract = {"selected_anchor_validation_claimed": False}
        candidate = SUBJECT._target_selected_container_contract_candidate(
            profile_source, anchor_contract,
        )
        self.assertEqual(candidate, {
            "runtime_module_type": "exact_ModuleType",
            "module_cache_type": "exact_dict_bounded_by_MAX_RECORDS",
            "finder_container": "exact_tuple_or_list_length_3",
            "hook_container": "exact_tuple_or_list_length_2",
            "selected_container_validation_claimed": False,
            "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
            "source_sha256": SUBJECT.DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
            "evidence_scope": "STATIC_SELECTED_CONTAINER_CONTRACT_CANDIDATE",
        })
        for changed in (
            profile_source.replace(
                b"type(runtime) is ModuleType", b"isinstance(runtime, ModuleType)",
            ),
            profile_source.replace(
                b"len(hooks) == 2", b"len(hooks) <= 2",
            ),
        ):
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                SUBJECT._normalized_profile_source_sha256(changed),
            ):
                self.assertIsNone(SUBJECT._target_selected_container_contract_candidate(
                    changed, anchor_contract,
                ))

    def test_worker_route_binds_and_enforces_sysconfigdata_environment(self):
        header, long_header, preconfig, initconfig, _, worker = self._worker_sys_flag_fact_fixture()
        with patch.multiple(
            SUBJECT,
            PRECONFIG_C_SHA256=hashlib.sha256(preconfig).hexdigest(),
            INITCONFIG_C_SHA256=hashlib.sha256(initconfig).hexdigest(),
            IMPORT_USED_BYTES_PROBE_SHA256=hashlib.sha256(worker).hexdigest(),
        ):
            self.assertTrue(SUBJECT._target_isolated_worker_route_valid(
                preconfig, initconfig, worker,
            ))
            self.assertEqual(
                SUBJECT._target_worker_sysconfigdata_environment_fact(
                    preconfig, initconfig, worker,
                ),
                (("_PYTHON_SYSCONFIGDATA_NAME", "absent_from_child_environment"),),
            )
            inherited = worker.replace(
                b"child_env.pop('_PYTHON_SYSCONFIGDATA_NAME', None)\n", b"",
            )
            with patch.object(
                SUBJECT, "IMPORT_USED_BYTES_PROBE_SHA256",
                hashlib.sha256(inherited).hexdigest(),
            ):
                self.assertFalse(SUBJECT._target_isolated_worker_route_valid(
                    preconfig, initconfig, inherited,
                ))
                self.assertEqual(
                    SUBJECT._target_worker_sysconfigdata_environment_fact(
                        preconfig, initconfig, inherited,
                    ), (),
                )

    def test_worker_sys_flag_facts_fail_closed_on_route_or_source_changes(self):
        header, long_header, preconfig, initconfig, sys_module, worker = (
            self._worker_sys_flag_fact_fixture()
        )
        with patch.multiple(
            SUBJECT,
            PRECONFIG_C_SHA256=hashlib.sha256(preconfig).hexdigest(),
            INITCONFIG_C_SHA256=hashlib.sha256(initconfig).hexdigest(),
            SYS_MODULE_C_SHA256=hashlib.sha256(sys_module).hexdigest(),
            IMPORT_USED_BYTES_PROBE_SHA256=hashlib.sha256(worker).hexdigest(),
        ):
            changed_dev_mode = preconfig.replace(
                b"cmdline->dev_mode = 0;",
                b"cmdline->dev_mode = 1;",
            )
            with patch.object(
                SUBJECT, "PRECONFIG_C_SHA256",
                hashlib.sha256(changed_dev_mode).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                    header, long_header, changed_dev_mode, initconfig, sys_module, worker,
                ), ())
            self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                header, long_header, preconfig, initconfig, sys_module,
                worker.replace(b"'-I'", b"'-E'"),
            ), ())
            self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                header, long_header, preconfig, initconfig, sys_module,
                worker.replace(b"'-B', '-X', 'utf8=1', '-c'", b"'-B', '-X', 'utf8=0', '-c'"),
            ), ())
            self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                header, long_header, preconfig, initconfig,
                sys_module.replace(b"config->safe_path));", b"config->safe_path = 0));"),
                worker,
            ), ())
            changed_initconfig = initconfig.replace(
                b"case 'S': config->site_import = 0;",
                b"case 's': config->site_import = 0;",
            )
            with patch.object(
                SUBJECT, "INITCONFIG_C_SHA256",
                hashlib.sha256(changed_initconfig).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                    header, long_header, preconfig, changed_initconfig, sys_module, worker,
                ), ())
            changed_defaults = initconfig.replace(
                b"config->parser_debug = 0;",
                b"config->parser_debug = 1;",
            )
            with patch.object(
                SUBJECT, "INITCONFIG_C_SHA256",
                hashlib.sha256(changed_defaults).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                    header, long_header, preconfig, changed_defaults, sys_module, worker,
                ), ())
            changed_hash_default = initconfig.replace(
                b"config->hash_seed = 0;",
                b"config->hash_seed = 1;",
            )
            with patch.object(
                SUBJECT, "INITCONFIG_C_SHA256",
                hashlib.sha256(changed_hash_default).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                    header, long_header, preconfig, changed_hash_default, sys_module, worker,
                ), ())
            changed_hash_environment = initconfig.replace(
                b"_Py_GetEnv(config->use_environment, name)",
                b"_Py_GetEnv(1, name)",
            )
            with patch.object(
                SUBJECT, "INITCONFIG_C_SHA256",
                hashlib.sha256(changed_hash_environment).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_worker_sys_flag_facts(
                    header, long_header, preconfig, changed_hash_environment, sys_module, worker,
                ), ())

    def test_sys_implementation_version_binds_shared_version_info(self):
        sys_module = (
            b"static PyObject *\nmake_impl_info(PyObject *version_info)\n{\n"
            b"res = PyDict_SetItemString(impl_info, \"version\", version_info);\n"
            b"return ns;\n}\n"
            b"#ifdef __EMSCRIPTEN__\n"
            b"version_info = make_version_info(tstate);\n"
            b"SET_SYS(\"version_info\", version_info);\n"
            b"SET_SYS(\"implementation\", make_impl_info(version_info));\n"
        )
        expected = ((
            "sys.implementation.version", (3, 12, 16, "final", 0),
        ),)
        with patch.object(
            SUBJECT, "SYS_MODULE_C_SHA256", hashlib.sha256(sys_module).hexdigest(),
        ):
            facts = SUBJECT._target_sys_implementation_version_fact(sys_module)
            self.assertEqual(facts, expected)
            self.assertEqual(SUBJECT._target_s15_version_field_candidate(
                sys_module, facts,
            ), {
                "value": (3, 12, 16),
                "source_fact": "sys.implementation.version",
                "source_sha256": hashlib.sha256(sys_module).hexdigest(),
                "version_info_object_shared": True,
                "runtime_version_claimed": False,
            })
            condition = ast.parse(
                "sys.implementation.version == sys.version_info and "
                "sys.implementation.version[:2] == (3, 12)",
                mode="eval",
            ).body
            self.assertIs(SUBJECT._target_condition(
                condition, known_call_facts=facts,
            ), True)
            files = {
                "pkg.py": (
                    b"if sys.implementation.version[:2] == (3, 12):\n"
                    b"    import matching_version\n"
                    b"else:\n    import other_version\n"
                ),
                "matching_version.py": b"VALUE = True\n",
                "other_version.py": b"VALUE = False\n",
            }
            modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
                files, ("pkg",), known_call_facts=facts,
            )
            self.assertEqual(modules, ("matching_version", "pkg"))
            self.assertEqual(conditions, {"resolved": 1, "unknown": 0})

    def test_sys_implementation_version_rejects_a_separate_version_object(self):
        sys_module = (
            b"static PyObject *\nmake_impl_info(PyObject *version_info)\n{\n"
            b"res = PyDict_SetItemString(impl_info, \"version\", other_version);\n"
            b"return ns;\n}\n"
            b"#ifdef __EMSCRIPTEN__\n"
            b"version_info = make_version_info(tstate);\n"
            b"SET_SYS(\"version_info\", version_info);\n"
            b"SET_SYS(\"implementation\", make_impl_info(version_info));\n"
        )
        with patch.object(
            SUBJECT, "SYS_MODULE_C_SHA256", hashlib.sha256(sys_module).hexdigest(),
        ):
            facts = SUBJECT._target_sys_implementation_version_fact(sys_module)
            self.assertEqual(
                facts, (),
            )
            self.assertEqual(SUBJECT._target_s15_version_field_candidate(
                sys_module, facts,
            ), {})

    def test_sys_implementation_name_binds_pinned_constant(self):
        sys_module = (
            b'#define NAME "cpython"\n'
            b"const char *_PySys_ImplName = NAME;\n"
            b"static PyObject *\nmake_impl_info(PyObject *version_info)\n{\n"
            b"value = PyUnicode_FromString(_PySys_ImplName);\n"
            b'res = PyDict_SetItemString(impl_info, "name", value);\n'
            b"return ns;\n}\n"
            b"#ifdef __EMSCRIPTEN__\n"
        )
        with patch.object(
            SUBJECT, "SYS_MODULE_C_SHA256", hashlib.sha256(sys_module).hexdigest(),
        ):
            facts = SUBJECT._target_sys_implementation_name_fact(sys_module)
            self.assertEqual(facts, (("sys.implementation.name", "cpython"),))
            self.assertEqual(
                SUBJECT._target_s15_implementation_field_candidate(
                    sys_module, facts,
                ), {
                    "value": "cpython",
                    "source_fact": "sys.implementation.name",
                    "source_sha256": hashlib.sha256(sys_module).hexdigest(),
                    "runtime_implementation_claimed": False,
                },
            )
            condition = ast.parse(
                'sys.implementation.name == "cpython"', mode="eval",
            ).body
            self.assertIsNone(SUBJECT._target_condition(condition))
            self.assertIs(SUBJECT._target_condition(
                condition, known_call_facts=facts,
            ), True)
            files = {
                "pkg.py": (
                    b'if sys.implementation.name == "cpython":\n'
                    b"    import cpython_branch\n"
                    b"else:\n    import other_branch\n"
                ),
                "cpython_branch.py": b"VALUE = True\n",
                "other_branch.py": b"VALUE = False\n",
            }
            modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
                files, ("pkg",), known_call_facts=facts,
            )
            self.assertEqual(modules, ("cpython_branch", "pkg"))
            self.assertEqual(conditions, {"resolved": 1, "unknown": 0})

    def test_sys_implementation_name_rejects_unpinned_value(self):
        sys_module = (
            b'#define NAME "other"\n'
            b"const char *_PySys_ImplName = NAME;\n"
            b"static PyObject *\nmake_impl_info(PyObject *version_info)\n{\n"
            b"value = PyUnicode_FromString(_PySys_ImplName);\n"
            b'res = PyDict_SetItemString(impl_info, "name", value);\n'
            b"return ns;\n}\n"
            b"#ifdef __EMSCRIPTEN__\n"
        )
        with patch.object(
            SUBJECT, "SYS_MODULE_C_SHA256", hashlib.sha256(sys_module).hexdigest(),
        ):
            facts = SUBJECT._target_sys_implementation_name_fact(sys_module)
            self.assertEqual(facts, ())
            self.assertEqual(SUBJECT._target_s15_implementation_field_candidate(
                sys_module, facts,
            ), {})
            condition = ast.parse(
                'sys.implementation.name == "cpython"', mode="eval",
            ).body
            self.assertIsNone(SUBJECT._target_condition(
                condition, known_call_facts=facts,
            ))

    def test_sys_implementation_cache_tag_binds_pinned_version_macros(self):
        sys_module = (
            b'#define NAME "cpython"\n'
            b"const char *_PySys_ImplName = NAME;\n"
            b"#define MAJOR Py_STRINGIFY(PY_MAJOR_VERSION)\n"
            b"#define MINOR Py_STRINGIFY(PY_MINOR_VERSION)\n"
            b'#define TAG NAME "-" MAJOR MINOR\n'
            b"const char *_PySys_ImplCacheTag = TAG;\n"
            b"static PyObject *\nmake_impl_info(PyObject *version_info)\n{\n"
            b"value = PyUnicode_FromString(_PySys_ImplCacheTag);\n"
            b'res = PyDict_SetItemString(impl_info, "cache_tag", value);\n'
            b"return ns;\n}\n"
            b"#ifdef __EMSCRIPTEN__\n"
        )
        version_fact = (("sys.implementation.version", (3, 12, 16, "final", 0)),)
        with patch.object(
            SUBJECT, "SYS_MODULE_C_SHA256", hashlib.sha256(sys_module).hexdigest(),
        ):
            facts = SUBJECT._target_sys_implementation_cache_tag_fact(
                sys_module, version_fact,
            )
            self.assertEqual(
                facts, (("sys.implementation.cache_tag", "cpython-312"),),
            )
            condition = ast.parse(
                'sys.implementation.cache_tag == "cpython-312"', mode="eval",
            ).body
            self.assertIs(SUBJECT._target_condition(
                condition, known_call_facts=facts,
            ), True)

    def test_sys_implementation_cache_tag_rejects_unbound_version_or_macros(self):
        sys_module = (
            b'#define NAME "cpython"\n'
            b"const char *_PySys_ImplName = NAME;\n"
            b"#define MAJOR Py_STRINGIFY(PY_MAJOR_VERSION)\n"
            b"#define MINOR Py_STRINGIFY(PY_MINOR_VERSION)\n"
            b'#define TAG NAME "-" MINOR MAJOR\n'
            b"const char *_PySys_ImplCacheTag = TAG;\n"
            b"static PyObject *\nmake_impl_info(PyObject *version_info)\n{\n"
            b"value = PyUnicode_FromString(_PySys_ImplCacheTag);\n"
            b'res = PyDict_SetItemString(impl_info, "cache_tag", value);\n'
            b"return ns;\n}\n"
            b"#ifdef __EMSCRIPTEN__\n"
        )
        with patch.object(
            SUBJECT, "SYS_MODULE_C_SHA256", hashlib.sha256(sys_module).hexdigest(),
        ):
            self.assertEqual(SUBJECT._target_sys_implementation_cache_tag_fact(
                sys_module,
                (("sys.implementation.version", (3, 13, 0, "final", 0)),),
            ), ())
            self.assertEqual(SUBJECT._target_sys_implementation_cache_tag_fact(
                sys_module,
                (("sys.implementation.version", (3, 12, 16, "final", 0)),),
            ), ())

    def test_sys_implementation_multiarch_binds_source_and_target_image(self):
        source = (
            b"static PyObject *\nmake_impl_info(PyObject *version_info)\n{\n"
            b"#ifdef MULTIARCH\n"
            b"value = PyUnicode_FromString(MULTIARCH);\n"
            b"if (value == NULL)\n    goto error;\n"
            b"res = PyDict_SetItemString(impl_info, \"_multiarch\", value);\n"
            b"Py_DECREF(value);\n"
            b"if (res < 0)\n    goto error;\n"
            b"#endif\n"
            b"return ns;\n}\n#ifdef __EMSCRIPTEN__\n"
        )
        image_facts = {
            "sysconfigdata_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
            "sysconfigdata_sha256": SUBJECT.TARGET_SYSCONFIGDATA_SHA256,
            "multiarch": "x86_64-linux-gnu",
        }
        with patch.object(
            SUBJECT, "SYS_MODULE_C_SHA256", hashlib.sha256(source).hexdigest(),
        ):
            expected = (("sys.implementation._multiarch", "x86_64-linux-gnu"),)
            self.assertEqual(
                SUBJECT._target_sys_implementation_multiarch_fact(source, image_facts),
                expected,
            )
            condition = ast.parse(
                "sys.implementation._multiarch == 'x86_64-linux-gnu'", mode="eval",
            ).body
            self.assertIs(SUBJECT._target_condition(
                condition, known_call_facts=expected,
            ), True)
            self.assertEqual(SUBJECT._target_sys_implementation_multiarch_fact(
                source, {**image_facts, "multiarch": "aarch64-linux-gnu"},
            ), ())
            self.assertEqual(SUBJECT._target_sys_implementation_multiarch_fact(
                source.replace(b'"_multiarch"', b'"other"'), image_facts,
            ), ())

    def test_sys_abiflags_binds_source_and_target_image(self):
        source = (
            b"#ifdef ABIFLAGS\n"
            b'SET_SYS_FROM_STRING("abiflags", ABIFLAGS);\n'
            b"#endif\n"
        )
        image_facts = {
            "sysconfigdata_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
            "sysconfigdata_sha256": SUBJECT.TARGET_SYSCONFIGDATA_SHA256,
            "abiflags": "",
        }
        with patch.object(
            SUBJECT, "SYS_MODULE_C_SHA256", hashlib.sha256(source).hexdigest(),
        ):
            expected = (("sys.abiflags", ""),)
            self.assertEqual(SUBJECT._target_sys_abiflags_fact(source, image_facts), expected)
            condition = ast.parse('sys.abiflags == ""', mode="eval").body
            self.assertIs(SUBJECT._target_condition(
                condition, known_call_facts=expected,
            ), True)
            self.assertEqual(SUBJECT._target_sys_abiflags_fact(
                source, {**image_facts, "abiflags": "d"},
            ), ())
            self.assertEqual(SUBJECT._target_sys_abiflags_fact(
                source.replace(b'"abiflags"', b'"other"'), image_facts,
            ), ())

    def test_sys_platform_binds_pinned_sources_and_image_machdep(self):
        sys_module = b'SET_SYS_FROM_STRING("platform", Py_GetPlatform());\n'
        getplatform = (
            b'#ifndef PLATFORM\n#define PLATFORM "unknown"\n#endif\n'
            b"const char *\nPy_GetPlatform(void)\n{\n    return PLATFORM;\n}\n"
        )
        makefile = (
            b"$(CC) -c $(PY_CORE_CFLAGS) -DPLATFORM='\"$(MACHDEP)\"' "
            b"-o $@ $(srcdir)/Python/getplatform.c\n"
        )
        image_facts = {
            "sysconfigdata_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
            "sysconfigdata_sha256": SUBJECT.TARGET_SYSCONFIGDATA_SHA256,
            "machdep": "linux",
        }
        with patch.multiple(
            SUBJECT,
            SYS_MODULE_C_SHA256=hashlib.sha256(sys_module).hexdigest(),
            GETPLATFORM_SOURCE_SHA256=hashlib.sha256(getplatform).hexdigest(),
            MAKEFILE_PRE_SHA256=hashlib.sha256(makefile).hexdigest(),
        ):
            fact = SUBJECT._target_sys_platform_fact(
                sys_module, getplatform, makefile, image_facts,
            )
            self.assertEqual(fact, (("sys.platform", "linux"),))
            self.assertEqual(SUBJECT._target_s15_platform_field_candidate(
                fact, image_facts,
            ), {
                "value": "linux",
                "sys_platform_fact": "sys.platform",
                "build_value_key": "MACHDEP",
                "sysconfigdata_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
                "sysconfigdata_sha256": SUBJECT.TARGET_SYSCONFIGDATA_SHA256,
                "sys_module_c_sha256": hashlib.sha256(sys_module).hexdigest(),
                "getplatform_source_sha256": hashlib.sha256(
                    getplatform
                ).hexdigest(),
                "makefile_pre_sha256": hashlib.sha256(makefile).hexdigest(),
                "runtime_platform_claimed": False,
            })
            self.assertEqual(SUBJECT._target_s15_platform_field_candidate(
                (("sys.platform", "win32"),), image_facts,
            ), {})
            self.assertEqual(SUBJECT._target_s15_platform_field_candidate(
                fact, {**image_facts, "machdep": "win32"},
            ), {})
            condition = ast.parse("sys.platform == 'linux'", mode="eval").body
            self.assertIs(SUBJECT._target_condition(
                condition, known_call_facts=fact,
            ), True)
            self.assertIsNone(SUBJECT._target_condition(condition))
            self.assertEqual(SUBJECT._target_sys_platform_fact(
                sys_module, getplatform, makefile.replace(b"$(MACHDEP)", b"linux"),
                image_facts,
            ), ())
            self.assertEqual(SUBJECT._target_sys_platform_fact(
                sys_module, getplatform, makefile,
                {**image_facts, "machdep": "win32"},
            ), ())

    def test_sysconfigdata_module_name_requires_all_bound_components_and_route(self):
        inventory = {
            "source_sha256": SUBJECT.SYSCONFIG_SOURCE_SHA256,
            "sysconfigdata_name_template": (
                "_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}"
            ),
        }
        abiflags = (("sys.abiflags", ""),)
        platform = (("sys.platform", "linux"),)
        multiarch = (("sys.implementation._multiarch", "x86_64-linux-gnu"),)
        worker_environment = (
            ("_PYTHON_SYSCONFIGDATA_NAME", "absent_from_child_environment"),
        )
        expected = ((
            "sysconfigdata.module_name",
            "_sysconfigdata__linux_x86_64-linux-gnu",
        ),)
        fact = SUBJECT._target_sysconfigdata_module_name_fact(
            inventory, abiflags, platform, multiarch, worker_environment,
        )
        self.assertEqual(fact, expected)
        self.assertEqual(SUBJECT._target_sysconfigdata_module_name_fact(
            {**inventory, "sysconfigdata_name_template": "_other_{multiarch}"},
            abiflags, platform, multiarch, worker_environment,
        ), ())
        self.assertEqual(SUBJECT._target_sysconfigdata_module_name_fact(
            inventory, abiflags, platform, multiarch, (),
        ), ())
        self.assertEqual(SUBJECT._target_sysconfigdata_module_name_fact(
            inventory, abiflags, ("sys.platform", "linux"), multiarch,
            worker_environment,
        ), ())

    def test_sysconfigdata_module_name_matches_only_pinned_image_file(self):
        module_name = ((
            "sysconfigdata.module_name",
            "_sysconfigdata__linux_x86_64-linux-gnu",
        ),)
        image_facts = {
            "sysconfigdata_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
            "sysconfigdata_sha256": SUBJECT.TARGET_SYSCONFIGDATA_SHA256,
            "build_time_vars_literal_dict": True,
            "build_time_vars_entry_count": 14,
        }
        expected = ((
            "sysconfigdata.image_file_path", SUBJECT.TARGET_SYSCONFIGDATA_PATH,
        ),)
        self.assertEqual(SUBJECT._target_sysconfigdata_image_file_fact(
            module_name, image_facts,
        ), expected)
        self.assertEqual(SUBJECT._target_sysconfigdata_image_file_fact(
            (("sysconfigdata.module_name", "_sysconfigdata__linux_other"),),
            image_facts,
        ), ())
        self.assertEqual(SUBJECT._target_sysconfigdata_image_file_fact(
            module_name, {**image_facts, "sysconfigdata_sha256": "0" * 64},
        ), ())

    def test_sysconfigdata_import_target_joins_exact_route_and_image_candidate(self):
        inventory = {
            "source_sha256": SUBJECT.SYSCONFIG_SOURCE_SHA256,
            "sysconfigdata_name_template": (
                "_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}"
            ),
            "sysconfigdata_importer": "__import__",
            "sysconfigdata_imported_attribute": "build_time_vars",
        }
        module_name = ((
            "sysconfigdata.module_name",
            "_sysconfigdata__linux_x86_64-linux-gnu",
        ),)
        image_file = ((
            "sysconfigdata.image_file_path", SUBJECT.TARGET_SYSCONFIGDATA_PATH,
        ),)
        expected = {
            "module_name": "_sysconfigdata__linux_x86_64-linux-gnu",
            "image_file_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
            "importer": "__import__",
            "imported_attribute": "build_time_vars",
            "evidence_scope": "STATIC_IMPORT_TARGET_CANDIDATE",
        }
        self.assertEqual(SUBJECT._target_sysconfigdata_import_target_candidate(
            inventory, module_name, image_file,
        ), expected)
        self.assertIsNone(SUBJECT._target_sysconfigdata_import_target_candidate(
            {**inventory, "sysconfigdata_imported_attribute": "other"},
            module_name, image_file,
        ))
        self.assertIsNone(SUBJECT._target_sysconfigdata_import_target_candidate(
            inventory, module_name,
            (("sysconfigdata.image_file_path", "usr/local/other.py"),),
        ))

    def test_sysconfig_posix_initializer_call_uses_bound_os_name_fact(self):
        source = (
            b"def _init_config_vars():\n"
            b"    if os.name == 'nt':\n        _init_non_posix()\n"
            b"    if os.name == 'posix':\n        _init_posix(_CONFIG_VARS)\n"
            b"def _init_non_posix():\n    import rejected\n"
            b"def _init_posix(vars):\n    import selected\n"
            b"_init_config_vars()\n"
        )
        files = {
            "sysconfig.py": source,
            "selected.py": b"VALUE = 1\n",
            "rejected.py": b"VALUE = 2\n",
        }
        with patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(source).hexdigest(),
        ):
            line_facts = SUBJECT._target_sysconfig_posix_init_line_facts(
                files, (("os.name", "posix"),),
            )
            self.assertEqual(line_facts, {4: True})
            self.assertEqual(SUBJECT._target_sysconfig_posix_init_line_facts(
                files, (),
            ), {})
            modules, _, _, _, _ = SUBJECT._module_init_call_candidate_closure(
                files, ("sysconfig",),
                known_call_facts=(("os.name", "posix"),),
                trusted_line_facts={"sysconfig": line_facts},
            )
            self.assertEqual(modules, ("selected", "sysconfig"))
            changed = source.replace(
                b"_init_posix(_CONFIG_VARS)",
                b"_init_non_posix(_CONFIG_VARS)",
            )
            self.assertEqual(SUBJECT._target_sysconfig_posix_init_line_facts(
                {**files, "sysconfig.py": changed},
                (("os.name", "posix"),),
            ), {})

    def test_sysconfig_initialization_route_requires_selected_call_and_image_file(self):
        inventory = {
            "source_sha256": SUBJECT.SYSCONFIG_SOURCE_SHA256,
            "sysconfigdata_name_template": (
                "_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}"
            ),
            "sysconfigdata_importer": "__import__",
            "sysconfigdata_imported_attribute": "build_time_vars",
            "sysconfigdata_initializer_parameter": "vars",
            "sysconfigdata_initializer_update_receiver": "vars",
            "sysconfigdata_initializer_update_value": "build_time_vars",
        }
        line_facts = {676: True}
        import_target = {
            "module_name": "_sysconfigdata__linux_x86_64-linux-gnu",
            "image_file_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
            "importer": "__import__",
            "imported_attribute": "build_time_vars",
            "evidence_scope": "STATIC_IMPORT_TARGET_CANDIDATE",
        }
        image_facts = {
            "sysconfigdata_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
            "sysconfigdata_sha256": SUBJECT.TARGET_SYSCONFIGDATA_SHA256,
            "build_time_vars_literal_dict": True,
            "build_time_vars_entry_count": 14,
            "soabi": "cpython-312-x86_64-linux-gnu",
            "destshared": "/usr/local/lib/python3.12/lib-dynload",
            "extension_suffix": ".cpython-312-x86_64-linux-gnu.so",
            "multiarch": "x86_64-linux-gnu",
            "abiflags": "",
            "machdep": "linux",
            "prefix": "/usr/local",
            "exec_prefix": "/usr/local",
            "platlibdir": "lib",
            "compiled_pythonpath": "",
            "library_dir": "/usr/local/lib",
            "library_name": "libpython3.12.so",
            "library_soname": "libpython3.12.so.1.0",
            "shared_library_enabled": 1,
        }
        lazy_call_candidate = {
            "getter": "get_config_vars",
            "initial_config_vars": None,
            "initialization_flag": False,
            "outer_guard": "not _CONFIG_VARS_INITIALIZED",
            "lock": "_CONFIG_VARS_LOCK",
            "recheck_guard": "_CONFIG_VARS is None",
            "selected_call": "_init_config_vars()",
            "evidence_scope": "STATIC_LAZY_INITIALIZER_CALL_CANDIDATE",
        }
        reinitialization_candidate = {
            "getter": "get_config_vars",
            "initialization_flag_initial_value": False,
            "first_call_guard": "not _CONFIG_VARS_INITIALIZED",
            "reinitialization_guard": (
                "_CONFIG_VARS['base'] != os.path.normpath(sys.prefix)"
            ),
            "reinitialization_guard_is_runtime_dependent": True,
            "lock": "_CONFIG_VARS_LOCK",
            "actions_if_reinitialization_guard_true": [
                "_CONFIG_VARS_INITIALIZED = False",
                "_init_config_vars()",
            ],
            "evidence_scope": "STATIC_CONFIG_REINITIALIZATION_CANDIDATE",
        }
        public_value_flow_candidate = {
            "public_mapping_api": "get_config_vars",
            "no_arguments_return": "_CONFIG_VARS",
            "arguments_return": "[_CONFIG_VARS.get(name) for name in args]",
            "single_value_api": "get_config_var",
            "single_value_return": "get_config_vars().get(name)",
            "evidence_scope": "STATIC_CONFIG_API_VALUE_FLOW_CANDIDATE",
        }
        post_update_entries_candidate = {
            "mapping": "_CONFIG_VARS",
            "post_update_direct_overwrites": [],
            "post_update_customizer": "_osx_support.customize_config_vars",
            "customizer_guard": "sys.platform == 'darwin'",
            "customizer_selected": False,
            "entry_values": SUBJECT.TARGET_SYSCONFIGDATA_EXPECTED_VALUES,
            "evidence_scope": "STATIC_POST_INIT_MAPPING_ENTRY_CANDIDATE",
        }
        initialization_complete_flag_candidate = {
            "initializer": "sysconfig._init_config_vars",
            "flag": "_CONFIG_VARS_INITIALIZED",
            "initial_value": False,
            "completion_assignment": "_CONFIG_VARS_INITIALIZED = True",
            "assignment_is_final_statement": True,
            "evidence_scope": "STATIC_CONFIG_INITIALIZED_FLAG_CANDIDATE",
        }
        candidate = SUBJECT._target_sysconfigdata_initialization_route_candidate(
            inventory, lazy_call_candidate, reinitialization_candidate,
            public_value_flow_candidate,
            post_update_entries_candidate, initialization_complete_flag_candidate,
            line_facts, import_target, image_facts,
        )
        self.assertEqual(candidate["public_initializer_call_candidate"], lazy_call_candidate)
        self.assertEqual(candidate["reinitialization_candidate"], reinitialization_candidate)
        self.assertEqual(candidate["public_config_value_flow_candidate"],
                         public_value_flow_candidate)
        self.assertEqual(candidate["post_update_entries_candidate"],
                         post_update_entries_candidate)
        self.assertEqual(candidate["initialization_complete_flag_candidate"],
                         initialization_complete_flag_candidate)
        self.assertEqual(candidate["public_config_api_entry_candidate"], {
            "mapping": "_CONFIG_VARS",
            "get_config_vars_no_arguments_result": "_CONFIG_VARS",
            "get_config_var_lookup": "_CONFIG_VARS.get(name)",
            "known_entry_values": SUBJECT.TARGET_SYSCONFIGDATA_EXPECTED_VALUES,
            "requires_no_intervening_mapping_mutation": True,
            "evidence_scope": "STATIC_CONFIG_API_ENTRY_VALUE_CANDIDATE",
        })
        self.assertEqual(candidate["guard_source_line"], 676)
        self.assertEqual(candidate["module_name"], import_target["module_name"])
        self.assertEqual(candidate["imported_attribute"], "build_time_vars")
        self.assertEqual(candidate["image_attribute_candidate"], {
            "attribute": "build_time_vars",
            "value_kind": "literal_dict",
            "entry_count": 14,
            "evidence_scope": "STATIC_IMAGE_ATTRIBUTE_CANDIDATE",
        })
        self.assertEqual(candidate["config_vars_update_candidate"], {
            "source_attribute": "build_time_vars",
            "local_value_name": "build_time_vars",
            "initializer_parameter": "vars",
            "initializer_argument": "_CONFIG_VARS",
            "update_receiver": "vars",
            "target_mapping": "_CONFIG_VARS",
            "known_entry_values": {
                "SOABI": "cpython-312-x86_64-linux-gnu",
                "DESTSHARED": "/usr/local/lib/python3.12/lib-dynload",
                "EXT_SUFFIX": ".cpython-312-x86_64-linux-gnu.so",
                "MULTIARCH": "x86_64-linux-gnu",
                "ABIFLAGS": "",
                "MACHDEP": "linux",
                "prefix": "/usr/local",
                "exec_prefix": "/usr/local",
                "PLATLIBDIR": "lib",
                "PYTHONPATH": "",
                "LIBDIR": "/usr/local/lib",
                "LDLIBRARY": "libpython3.12.so",
                "INSTSONAME": "libpython3.12.so.1.0",
                "Py_ENABLE_SHARED": 1,
            },
            "evidence_scope": "STATIC_CONFIG_MAPPING_UPDATE_CANDIDATE",
        })
        self.assertEqual(
            candidate["evidence_scope"],
            "STATIC_CONDITIONAL_IMPORT_ROUTE_CANDIDATE",
        )
        self.assertIsNone(SUBJECT._target_sysconfigdata_initialization_route_candidate(
            inventory, lazy_call_candidate, reinitialization_candidate,
            public_value_flow_candidate,
            post_update_entries_candidate, initialization_complete_flag_candidate,
            {}, import_target, image_facts,
        ))
        self.assertIsNone(SUBJECT._target_sysconfigdata_initialization_route_candidate(
            inventory, {**lazy_call_candidate, "initialization_flag": True},
            reinitialization_candidate,
            public_value_flow_candidate, post_update_entries_candidate,
            initialization_complete_flag_candidate,
            line_facts, import_target, image_facts,
        ))
        self.assertIsNone(SUBJECT._target_sysconfigdata_initialization_route_candidate(
            inventory, lazy_call_candidate,
            {**reinitialization_candidate,
             "reinitialization_guard_is_runtime_dependent": False},
            public_value_flow_candidate, post_update_entries_candidate,
            initialization_complete_flag_candidate,
            line_facts, import_target, image_facts,
        ))
        self.assertIsNone(SUBJECT._target_sysconfigdata_initialization_route_candidate(
            inventory, lazy_call_candidate, reinitialization_candidate,
            {**public_value_flow_candidate, "no_arguments_return": "other"},
            post_update_entries_candidate, initialization_complete_flag_candidate,
            line_facts, import_target, image_facts,
        ))
        self.assertIsNone(SUBJECT._target_sysconfigdata_initialization_route_candidate(
            {**inventory, "sysconfigdata_initializer_update_receiver": "other"},
            lazy_call_candidate, reinitialization_candidate,
            public_value_flow_candidate,
            post_update_entries_candidate, initialization_complete_flag_candidate,
            line_facts, import_target, image_facts,
        ))
        self.assertIsNone(SUBJECT._target_sysconfigdata_initialization_route_candidate(
            inventory, lazy_call_candidate, reinitialization_candidate,
            public_value_flow_candidate,
            post_update_entries_candidate, initialization_complete_flag_candidate,
            line_facts, import_target,
            {**image_facts, "sysconfigdata_sha256": "0" * 64},
        ))
        self.assertIsNone(SUBJECT._target_sysconfigdata_initialization_route_candidate(
            inventory, lazy_call_candidate, reinitialization_candidate,
            public_value_flow_candidate,
            post_update_entries_candidate, initialization_complete_flag_candidate,
            line_facts, import_target,
            {**image_facts, "soabi": "unbound"},
        ))
        self.assertIsNone(SUBJECT._target_sysconfigdata_initialization_route_candidate(
            inventory, lazy_call_candidate, reinitialization_candidate,
            public_value_flow_candidate,
            post_update_entries_candidate, initialization_complete_flag_candidate,
            line_facts, import_target,
            {key: value for key, value in image_facts.items()
             if key != "build_time_vars_literal_dict"},
        ))

    def test_sysconfig_lazy_initializer_call_requires_bound_state_and_nested_guards(self):
        source = (
            b"_CONFIG_VARS = None\n"
            b"_CONFIG_VARS_INITIALIZED = False\n"
            b"def get_config_vars():\n"
            b"    global _CONFIG_VARS_INITIALIZED\n"
            b"    if not _CONFIG_VARS_INITIALIZED:\n"
            b"        with _CONFIG_VARS_LOCK:\n"
            b"            if _CONFIG_VARS is None:\n"
            b"                _init_config_vars()\n"
            b"    else:\n"
            b"        pass\n"
        )
        digest_patch = patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(source).hexdigest(),
        )
        expected = {
            "getter": "get_config_vars",
            "initial_config_vars": None,
            "initialization_flag": False,
            "outer_guard": "not _CONFIG_VARS_INITIALIZED",
            "lock": "_CONFIG_VARS_LOCK",
            "recheck_guard": "_CONFIG_VARS is None",
            "selected_call": "_init_config_vars()",
            "evidence_scope": "STATIC_LAZY_INITIALIZER_CALL_CANDIDATE",
        }
        with digest_patch:
            self.assertEqual(SUBJECT._target_sysconfig_lazy_initialization_call_candidate(
                {"sysconfig.py": source},
            ), expected)
            for changed in (
                    source.replace(b"_CONFIG_VARS_INITIALIZED = False",
                                   b"_CONFIG_VARS_INITIALIZED = True"),
                    source.replace(b"_CONFIG_VARS is None",
                                   b"_CONFIG_VARS is not None"),
                    source.replace(b"_init_config_vars()",
                                   b"_init_config_vars('unexpected')"),
                    source.replace(b"    global _CONFIG_VARS_INITIALIZED\n", b""),
            ):
                with self.subTest(changed=changed), patch.object(
                    SUBJECT, "SYSCONFIG_SOURCE_SHA256",
                    hashlib.sha256(changed).hexdigest(),
                ):
                    self.assertIsNone(
                        SUBJECT._target_sysconfig_lazy_initialization_call_candidate(
                            {"sysconfig.py": changed},
                        )
                    )

    def test_sysconfig_public_value_apis_return_the_config_mapping(self):
        source = (
            b"def get_config_vars(*args):\n"
            b"    if args:\n"
            b"        vals = []\n"
            b"        for name in args:\n"
            b"            vals.append(_CONFIG_VARS.get(name))\n"
            b"        return vals\n"
            b"    else:\n"
            b"        return _CONFIG_VARS\n"
            b"def get_config_var(name):\n"
            b"    return get_config_vars().get(name)\n"
        )
        expected = {
            "public_mapping_api": "get_config_vars",
            "no_arguments_return": "_CONFIG_VARS",
            "arguments_return": "[_CONFIG_VARS.get(name) for name in args]",
            "single_value_api": "get_config_var",
            "single_value_return": "get_config_vars().get(name)",
            "evidence_scope": "STATIC_CONFIG_API_VALUE_FLOW_CANDIDATE",
        }
        with patch.object(
                SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(source).hexdigest()):
            self.assertEqual(
                SUBJECT._target_sysconfig_public_config_value_flow_candidate(
                    {"sysconfig.py": source},
                ), expected,
            )
            for changed in (
                    source.replace(b"return _CONFIG_VARS\n",
                                   b"return None\n"),
                    source.replace(b"get_config_vars().get(name)",
                                   b"get_config_vars().get('other')"),
            ):
                with self.subTest(changed=changed), patch.object(
                    SUBJECT, "SYSCONFIG_SOURCE_SHA256",
                    hashlib.sha256(changed).hexdigest(),
                ):
                    self.assertIsNone(
                        SUBJECT._target_sysconfig_public_config_value_flow_candidate(
                            {"sysconfig.py": changed},
                        )
                    )

    def test_sysconfig_reinitialization_candidate_binds_dynamic_prefix_guard(self):
        source = (
            b"_CONFIG_VARS = None\n"
            b"_CONFIG_VARS_INITIALIZED = False\n"
            b"def get_config_vars(*args):\n"
            b"    global _CONFIG_VARS_INITIALIZED\n"
            b"    if not _CONFIG_VARS_INITIALIZED:\n"
            b"        with _CONFIG_VARS_LOCK:\n"
            b"            if _CONFIG_VARS is None:\n"
            b"                _init_config_vars()\n"
            b"    elif _CONFIG_VARS['base'] != os.path.normpath(sys.prefix):\n"
            b"        with _CONFIG_VARS_LOCK:\n"
            b"            _CONFIG_VARS_INITIALIZED = False\n"
            b"            _init_config_vars()\n"
        )
        expected = {
            "getter": "get_config_vars",
            "initialization_flag_initial_value": False,
            "first_call_guard": "not _CONFIG_VARS_INITIALIZED",
            "reinitialization_guard": (
                "_CONFIG_VARS['base'] != os.path.normpath(sys.prefix)"
            ),
            "reinitialization_guard_is_runtime_dependent": True,
            "lock": "_CONFIG_VARS_LOCK",
            "actions_if_reinitialization_guard_true": [
                "_CONFIG_VARS_INITIALIZED = False",
                "_init_config_vars()",
            ],
            "evidence_scope": "STATIC_CONFIG_REINITIALIZATION_CANDIDATE",
        }
        with patch.object(
                SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(source).hexdigest()):
            self.assertEqual(
                SUBJECT._target_sysconfig_reinitialization_candidate(
                    {"sysconfig.py": source},
                ), expected,
            )
            for changed in (
                    source.replace(
                        b"_CONFIG_VARS['base'] != os.path.normpath(sys.prefix)",
                        b"_CONFIG_VARS['base'] == os.path.normpath(sys.prefix)",
                    ),
                    source.replace(b"_CONFIG_VARS_INITIALIZED = False",
                                   b"_CONFIG_VARS_INITIALIZED = True", 1),
                    source.replace(b"_init_config_vars()",
                                   b"_init_config_vars('unexpected')", 1),
            ):
                with self.subTest(changed=changed), patch.object(
                    SUBJECT, "SYSCONFIG_SOURCE_SHA256",
                    hashlib.sha256(changed).hexdigest(),
                ):
                    self.assertIsNone(
                        SUBJECT._target_sysconfig_reinitialization_candidate(
                            {"sysconfig.py": changed},
                        )
                    )

    def test_sysconfigdata_entries_survive_pinned_post_update_initializer_body(self):
        source = (
            b"def _init_config_vars():\n"
            b"    if os.name == 'nt':\n"
            b"        _init_non_posix(_CONFIG_VARS)\n"
            b"    if os.name == 'posix':\n"
            b"        _init_posix(_CONFIG_VARS)\n"
            b"    if _HAS_USER_BASE:\n"
            b"        _CONFIG_VARS['userbase'] = _getuserbase()\n"
            b"    _CONFIG_VARS['srcdir'] = _safe_realpath('src')\n"
            b"    if sys.platform == 'darwin':\n"
            b"        import _osx_support\n"
            b"        _osx_support.customize_config_vars(_CONFIG_VARS)\n"
        )
        image_facts = {
            "sysconfigdata_path": SUBJECT.TARGET_SYSCONFIGDATA_PATH,
            "sysconfigdata_sha256": SUBJECT.TARGET_SYSCONFIGDATA_SHA256,
            "machdep": "linux",
        }
        image_facts.update({
            SUBJECT.TARGET_SYSCONFIGDATA_FACT_FIELDS[key]: value
            for key, value in SUBJECT.TARGET_SYSCONFIGDATA_EXPECTED_VALUES.items()
        })
        with patch.object(
                SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(source).hexdigest()):
            posix_facts = SUBJECT._target_sysconfig_posix_init_line_facts(
                {"sysconfig.py": source}, (("os.name", "posix"),),
            )
            expected = {
                "mapping": "_CONFIG_VARS",
                "post_update_direct_overwrites": [],
                "post_update_customizer": "_osx_support.customize_config_vars",
                "customizer_guard": "sys.platform == 'darwin'",
                "customizer_selected": False,
                "entry_values": SUBJECT.TARGET_SYSCONFIGDATA_EXPECTED_VALUES,
                "evidence_scope": "STATIC_POST_INIT_MAPPING_ENTRY_CANDIDATE",
            }
            self.assertEqual(
                SUBJECT._target_sysconfig_post_update_entries_candidate(
                    {"sysconfig.py": source}, posix_facts,
                    (("sys.platform", "linux"),), image_facts,
                ), expected,
            )
            overwritten = source.replace(
                b"_CONFIG_VARS['userbase']",
                b"_CONFIG_VARS['SOABI']",
            )
            with patch.object(
                    SUBJECT, "SYSCONFIG_SOURCE_SHA256",
                    hashlib.sha256(overwritten).hexdigest(),
            ):
                overwritten_facts = SUBJECT._target_sysconfig_posix_init_line_facts(
                    {"sysconfig.py": overwritten}, (("os.name", "posix"),),
                )
                self.assertIsNone(
                    SUBJECT._target_sysconfig_post_update_entries_candidate(
                        {"sysconfig.py": overwritten}, overwritten_facts,
                        (("sys.platform", "linux"),), image_facts,
                    )
                )
            updated = source.replace(
                b"    _CONFIG_VARS['srcdir']",
                b"    _CONFIG_VARS.update({'SOABI': 'changed'})\n"
                b"    _CONFIG_VARS['srcdir']",
            )
            with patch.object(
                    SUBJECT, "SYSCONFIG_SOURCE_SHA256",
                    hashlib.sha256(updated).hexdigest(),
            ):
                updated_facts = SUBJECT._target_sysconfig_posix_init_line_facts(
                    {"sysconfig.py": updated}, (("os.name", "posix"),),
                )
                self.assertIsNone(
                    SUBJECT._target_sysconfig_post_update_entries_candidate(
                        {"sysconfig.py": updated}, updated_facts,
                        (("sys.platform", "linux"),), image_facts,
                    )
                )
            self.assertIsNone(SUBJECT._target_sysconfig_post_update_entries_candidate(
                {"sysconfig.py": source}, posix_facts,
                (("sys.platform", "darwin"),), image_facts,
            ))

    def test_sysconfig_initialized_flag_is_bound_to_initializer_completion(self):
        source = (
            b"def _init_config_vars():\n"
            b"    if os.name == 'posix':\n"
            b"        _init_posix(_CONFIG_VARS)\n"
            b"    global _CONFIG_VARS_INITIALIZED\n"
            b"    _CONFIG_VARS_INITIALIZED = True\n"
        )
        expected = {
            "initializer": "sysconfig._init_config_vars",
            "flag": "_CONFIG_VARS_INITIALIZED",
            "initial_value": False,
            "completion_assignment": "_CONFIG_VARS_INITIALIZED = True",
            "assignment_is_final_statement": True,
            "evidence_scope": "STATIC_CONFIG_INITIALIZED_FLAG_CANDIDATE",
        }
        with patch.object(
                SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(source).hexdigest()):
            posix_facts = SUBJECT._target_sysconfig_posix_init_line_facts(
                {"sysconfig.py": source}, (("os.name", "posix"),),
            )
            self.assertEqual(
                SUBJECT._target_sysconfig_initialization_complete_flag_candidate(
                    {"sysconfig.py": source}, posix_facts,
                ), expected,
            )
            for changed in (
                    source.replace(b"_CONFIG_VARS_INITIALIZED = True",
                                   b"_CONFIG_VARS_INITIALIZED = False"),
                    source.replace(
                        b"    if os.name == 'posix':\n"
                        b"        _init_posix(_CONFIG_VARS)\n"
                        b"    global _CONFIG_VARS_INITIALIZED\n"
                        b"    _CONFIG_VARS_INITIALIZED = True\n",
                        b"    global _CONFIG_VARS_INITIALIZED\n"
                        b"    _CONFIG_VARS_INITIALIZED = True\n"
                        b"    if os.name == 'posix':\n"
                        b"        _init_posix(_CONFIG_VARS)\n",
                    ),
            ):
                with self.subTest(changed=changed), patch.object(
                    SUBJECT, "SYSCONFIG_SOURCE_SHA256",
                    hashlib.sha256(changed).hexdigest(),
                ):
                    changed_facts = SUBJECT._target_sysconfig_posix_init_line_facts(
                        {"sysconfig.py": changed}, (("os.name", "posix"),),
                    )
                    self.assertIsNone(
                        SUBJECT._target_sysconfig_initialization_complete_flag_candidate(
                            {"sysconfig.py": changed}, changed_facts,
                        )
                    )

    def test_debug_name_fact_requires_validated_unoptimized_guard(self):
        self.assertEqual(
            SUBJECT._target_importlib_debug_call_facts({17: True}),
            (("__debug__", True),),
        )
        for facts in ({}, {17: False}, {0: True}, {"line": True}, None):
            self.assertEqual(
                SUBJECT._target_importlib_debug_call_facts(facts), (),
            )
        condition = ast.parse("__debug__", mode="eval").body
        self.assertIsNone(SUBJECT._target_condition(condition))
        self.assertIs(SUBJECT._target_condition(
            condition,
            known_call_facts=SUBJECT._target_importlib_debug_call_facts({17: True}),
        ), True)

    def test_debug_name_fact_prunes_only_the_proven_normal_compile_branch(self):
        files = {
            "pkg.py": (
                b"if __debug__:\n    import normal_compile\n"
                b"else:\n    import optimized_compile\n"
            ),
            "normal_compile.py": b"VALUE = True\n",
            "optimized_compile.py": b"VALUE = False\n",
        }
        known_call_facts = SUBJECT._target_importlib_debug_call_facts({17: True})
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), known_call_facts=known_call_facts,
        )
        self.assertEqual(modules, ("normal_compile", "pkg"))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})

    def test_importlib_verbose_fact_requires_positive_callsite_verbosity(self):
        preconfig_source = b"case 'I': cmdline->isolated = 1;"
        initconfig_source = (
            b"if (config->isolated) { config->use_environment = 0; }\n"
            b"static void config_init_defaults(void) { config->verbose = 0; }\n"
            b"case 'v': config->verbose++;\n"
            b"static PyStatus config_read_env_vars(PyConfig *config) { "
            b"int use_env = config->use_environment; "
            b"_Py_get_env_flag(use_env, &config->verbose, \"PYTHONVERBOSE\"); }"
        )
        worker_source = (
            b"def run_import_only(ordinal, worker_nonce):\n"
            b"    command = [sys.executable, '-I', '-S', '-B', '-X', 'utf8=1', '-c', "
            b"_worker_source(ordinal, worker_nonce)]\n"
            b"def _collect_process(command):\n"
            b"    child_env = os.environ.copy()\n"
            b"    child_env.pop('_PYTHON_SYSCONFIGDATA_NAME', None)\n"
            b"    try:\n"
            b"        return subprocess.Popen(command, env=child_env)\n"
            b"    except OSError:\n"
            b"        return None\n"
        )
        bootstrap_source = (
            b"def _verbose_message(message, *args, verbosity=1):\n"
            b"    if sys.flags.verbose >= verbosity:\n"
            b"        print(message.format(*args), file=sys.stderr)\n"
            b"_verbose_message('import {!r}', module, loader)\n"
        )
        external_source = b"".join(
            b"_bootstrap._verbose_message('external')\n" for _ in range(14)
        )
        zipimport_source = b"".join(
            b"_bootstrap._verbose_message('zip')\n" for _ in range(7)
        )
        files = {
            "importlib/_bootstrap.py": bootstrap_source,
            "importlib/_bootstrap_external.py": external_source,
            "zipimport.py": zipimport_source,
        }
        with patch.multiple(
            SUBJECT,
            PRECONFIG_C_SHA256=hashlib.sha256(preconfig_source).hexdigest(),
            INITCONFIG_C_SHA256=hashlib.sha256(initconfig_source).hexdigest(),
            IMPORT_USED_BYTES_PROBE_SHA256=hashlib.sha256(worker_source).hexdigest(),
            IMPORTLIB_BOOTSTRAP_SOURCE_SHA256=hashlib.sha256(bootstrap_source).hexdigest(),
            IMPORTLIB_EXTERNAL_SOURCE_SHA256=hashlib.sha256(external_source).hexdigest(),
            ZIPIMPORT_SOURCE_SHA256=hashlib.sha256(zipimport_source).hexdigest(),
        ):
            fact = SUBJECT._target_importlib_verbose_line_facts(
                files,
                preconfig_source, initconfig_source, worker_source,
            )
            self.assertEqual(fact, {2: False})
            unsafe_source = external_source.replace(
                b"_bootstrap._verbose_message('external')",
                b"_bootstrap._verbose_message('external', verbosity=0)",
            )
            with patch.object(
                SUBJECT, "IMPORTLIB_EXTERNAL_SOURCE_SHA256",
                hashlib.sha256(unsafe_source).hexdigest(),
            ):
                unsafe_files = dict(files)
                unsafe_files["importlib/_bootstrap_external.py"] = unsafe_source
                self.assertEqual(SUBJECT._target_importlib_verbose_line_facts(
                    unsafe_files,
                    preconfig_source, initconfig_source, worker_source,
                ), {})

    def test_sysconfig_build_guard_requires_all_production_calls_to_be_empty(self):
        sysconfig_source = (
            b"def is_python_build(check_home=None):\n"
            b"    if check_home is not None:\n"
            b"        import warnings\n"
            b"        warnings.warn('deprecated')\n"
            b"    return False\n"
            b"is_python_build()\n"
        )
        venv_source = (
            b"import sysconfig\n"
            b"sysconfig.is_python_build()\n"
            b"sysconfig.is_python_build()\n"
            b"sysconfig.is_python_build()\n"
        )
        files = {
            "sysconfig.py": sysconfig_source,
            "venv/__init__.py": venv_source,
            "test/test_sysconfig.py": b"sysconfig.is_python_build('explicit')\n",
        }
        with patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256",
            hashlib.sha256(sysconfig_source).hexdigest(),
        ):
            facts = SUBJECT._target_sysconfig_is_python_build_line_facts(files)
            self.assertEqual(facts, {2: False})

            unsafe_files = dict(files)
            unsafe_files["venv/__init__.py"] = venv_source.replace(
                b"sysconfig.is_python_build()",
                b"sysconfig.is_python_build('explicit')", 1,
            )
            self.assertEqual(
                SUBJECT._target_sysconfig_is_python_build_line_facts(unsafe_files),
                {},
            )

            unsafe_files["venv/__init__.py"] = venv_source.replace(
                b"sysconfig.is_python_build()",
                b"sysconfig.is_python_build(check_home=None)", 1,
            )
            self.assertEqual(
                SUBJECT._target_sysconfig_is_python_build_line_facts(unsafe_files),
                {},
            )

            alias_files = dict(files)
            alias_files["venv/__init__.py"] = (
                b"from sysconfig import is_python_build as build_check\n"
                b"build_check()\n"
                + venv_source
            )
            self.assertEqual(
                SUBJECT._target_sysconfig_is_python_build_line_facts(alias_files),
                {},
            )

            reference_files = dict(files)
            reference_files["venv/__init__.py"] = (
                b"import sysconfig\n"
                b"build_check = sysconfig.is_python_build\n"
                + venv_source.split(b"\n", 1)[1]
            )
            self.assertEqual(
                SUBJECT._target_sysconfig_is_python_build_line_facts(reference_files),
                {},
            )

            dynamic_files = dict(files)
            dynamic_files["venv/__init__.py"] = (
                b"import sysconfig\n"
                b"getattr(sysconfig, 'is_python_build')()\n"
                + venv_source.split(b"\n", 1)[1]
            )
            self.assertEqual(
                SUBJECT._target_sysconfig_is_python_build_line_facts(dynamic_files),
                {},
            )

            rebound_files = dict(files)
            rebound_files["sysconfig.py"] = sysconfig_source.replace(
                b"        import warnings\n",
                b"        check_home = None\n        import warnings\n",
            )
            with patch.object(
                SUBJECT, "SYSCONFIG_SOURCE_SHA256",
                hashlib.sha256(rebound_files["sysconfig.py"]).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_sysconfig_is_python_build_line_facts(
                        rebound_files,
                    ),
                    {},
                )

            extra_caller_files = dict(files)
            extra_caller_files["extra.py"] = b"import sysconfig\nsysconfig.is_python_build()\n"
            self.assertEqual(
                SUBJECT._target_sysconfig_is_python_build_line_facts(
                    extra_caller_files,
                ),
                {},
            )

            changed_source_files = dict(files)
            changed_source_files["sysconfig.py"] = sysconfig_source.replace(
                b"check_home=None", b"check_home=True",
            )
            self.assertEqual(
                SUBJECT._target_sysconfig_is_python_build_line_facts(
                    changed_source_files,
                ),
                {},
            )

    def test_string_template_self_hook_guard_is_false_before_pattern_setup(self):
        string_lines = [
            "class Template:",
            "    def __init_subclass__(cls):",
            "        if 'pattern' in cls.__dict__:",
            "            pass",
        ]
        string_lines.extend([""] * (174 - len(string_lines)))
        string_lines.append("Template.__init_subclass__()")
        string_source = ("\n".join(string_lines) + "\n").encode()
        pipes_lines = [""] * 103 + ["Template()"]
        pipes_source = ("\n".join(pipes_lines) + "\n").encode()
        logging_lines = [""] * 28 + ["from string import Template"]
        logging_lines.extend([""] * (509 - len(logging_lines)))
        logging_lines.extend(
            ["Template('format')"] + [""] * 6 + ["Template.pattern"]
        )
        logging_source = ("\n".join(logging_lines) + "\n").encode()
        files = {
            "string.py": string_source,
            "pipes.py": pipes_source,
            "logging/__init__.py": logging_source,
        }
        with patch.multiple(
            SUBJECT,
            STRING_SOURCE_SHA256=hashlib.sha256(string_source).hexdigest(),
            PIPES_SOURCE_SHA256=hashlib.sha256(pipes_source).hexdigest(),
            LOGGING_SOURCE_SHA256=hashlib.sha256(logging_source).hexdigest(),
        ):
            self.assertEqual(
                SUBJECT._target_string_template_pattern_guard_line_facts(files),
                {3: False},
            )
            subclass_files = dict(files)
            subclass_files["pipes.py"] += b"\nclass CustomTemplate(Template):\n    pass\n"
            with patch.object(
                SUBJECT, "PIPES_SOURCE_SHA256",
                hashlib.sha256(subclass_files["pipes.py"]).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_string_template_pattern_guard_line_facts(
                        subclass_files,
                    ),
                    {},
                )

    def test_weakrefset_optional_data_guard_requires_all_empty_callers(self):
        weakrefset_source = (
            b"class WeakSet:\n"
            b"    def __init__(self, data=None):\n"
            b"        if data is not None:\n"
            b"            self.update(data)\n"
        )
        lines_by_path = {
            "threading.py": {9: "from _weakrefset import WeakSet", 849: "WeakSet()"},
            "weakref.py": {
                22: "from _weakrefset import WeakSet, _IterationGuard",
                36: "_collections_abc.MutableSet.register(WeakSet)",
            },
            "_py_abc.py": {
                1: "from _weakrefset import WeakSet",
                48: "WeakSet()", 49: "WeakSet()", 50: "WeakSet()",
                79: "WeakSet()", 118: "WeakSet()",
            },
            "asyncio/base_events.py": {434: "weakref.WeakSet()"},
            "asyncio/tasks.py": {986: "weakref.WeakSet()"},
            "asyncio/windows_events.py": {
                254: "weakref.WeakSet()", 425: "weakref.WeakSet()",
                427: "weakref.WeakSet()",
            },
            "logging/__init__.py": {260: "weakref.WeakSet()"},
            "multiprocessing/process.py": {
                22: "from _weakrefset import WeakSet", 439: "WeakSet()",
            },
        }
        files = {"_weakrefset.py": weakrefset_source}
        for path, statements in lines_by_path.items():
            lines = [""] * max(statements)
            for line, statement in statements.items():
                lines[line - 1] = statement
            files[path] = ("\n".join(lines) + "\n").encode()
        with patch.object(
            SUBJECT, "WEAKREFSET_SOURCE_SHA256",
            hashlib.sha256(weakrefset_source).hexdigest(),
        ):
            self.assertEqual(
                SUBJECT._target_weakrefset_empty_init_line_facts(files),
                {3: False},
            )
            unsafe_files = dict(files)
            unsafe_files["extra.py"] = b"WeakSet(items)\n"
            self.assertEqual(
                SUBJECT._target_weakrefset_empty_init_line_facts(unsafe_files),
                {},
            )
            subclass_files = dict(files)
            subclass_files["extra.py"] = b"class Derived(WeakSet):\n    pass\n"
            self.assertEqual(
                SUBJECT._target_weakrefset_empty_init_line_facts(subclass_files),
                {},
            )

    def test_copyreg_callable_guard_requires_complete_direct_call_inventory(self):
        copyreg_lines = {
            1: "def pickle(ob_type, pickle_function, constructor_ob=None):",
            2: "    if not callable(pickle_function):",
            3: "        raise TypeError()",
            19: "    if constructor_ob is not None:",
            20: "        constructor(constructor_ob)",
            21: "def constructor(object):",
            22: "    if not callable(object):",
            23: "        raise TypeError()",
            24: "def pickle_complex(value): return value",
            25: "def pickle_union(value): return value",
            31: "pickle(complex, pickle_complex, complex)",
            37: "pickle(type(int | str), pickle_union)",
        }
        typing_lines = {
            1: "def _pickle_psargs(value): return value",
            2: "def _pickle_pskwargs(value): return value",
            26: "import copyreg",
            1842: "copyreg.pickle(ParamSpecArgs, _pickle_psargs)",
            1847: "copyreg.pickle(ParamSpecKwargs, _pickle_pskwargs)",
        }
        re_lines = {
            1: "def _compile(value): return value",
            2: "def _pickle(value): return value",
            338: "import copyreg",
            343: "copyreg.pickle(Pattern, _pickle, _compile)",
        }
        other_lines = {
            "idlelib/rpc.py": {
                30: "import copyreg", 67: "copyreg.dispatch_table",
            },
            "multiprocessing/reduction.py": {
                11: "import copyreg", 36: "copyreg.dispatch_table",
            },
        }

        def make_source(lines):
            content = [""] * max(lines)
            for number, statement in lines.items():
                content[number - 1] = statement
            return ("\n".join(content) + "\n").encode()

        files = {
            "copyreg.py": make_source(copyreg_lines),
            "typing.py": make_source(typing_lines),
            "re/__init__.py": make_source(re_lines),
            **{path: make_source(lines) for path, lines in other_lines.items()},
        }
        with patch.multiple(
            SUBJECT,
            COPYREG_SOURCE_SHA256=hashlib.sha256(files["copyreg.py"]).hexdigest(),
            TYPING_SOURCE_SHA256=hashlib.sha256(files["typing.py"]).hexdigest(),
            RE_SOURCE_SHA256=hashlib.sha256(files["re/__init__.py"]).hexdigest(),
        ):
            self.assertEqual(
                SUBJECT._target_copyreg_pickle_callable_line_facts(files),
                {2: False, 22: False},
            )
            self.assertEqual(
                SUBJECT._target_copyreg_constructor_observation_facts(files),
                {("copyreg", "copyreg.py", 19): (False, True)},
            )
            unsafe_files = dict(files)
            unsafe_files["typing.py"] = files["typing.py"].replace(
                b"copyreg.pickle(ParamSpecArgs, _pickle_psargs)",
                b"copyreg.pickle(ParamSpecArgs, None)",
            )
            with patch.object(
                SUBJECT, "TYPING_SOURCE_SHA256",
                hashlib.sha256(unsafe_files["typing.py"]).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_copyreg_pickle_callable_line_facts(
                        unsafe_files,
                    ),
                    {},
                )
            alias_files = dict(files)
            alias_files["extra.py"] = (
                b"from copyreg import pickle as register\n"
                b"register(object, str)\n"
            )
            self.assertEqual(
                SUBJECT._target_copyreg_pickle_callable_line_facts(alias_files),
                {},
            )
            self.assertEqual(
                SUBJECT._target_copyreg_constructor_observation_facts(alias_files),
                {},
            )
            dynamic_import_files = dict(files)
            dynamic_import_files["extra.py"] = (
                b"__import__('copyreg')\n"
            )
            self.assertEqual(
                SUBJECT._target_copyreg_pickle_callable_line_facts(
                    dynamic_import_files,
                ),
                {},
            )
            aliased_dynamic_import_files = dict(files)
            aliased_dynamic_import_files["extra.py"] = (
                b"from importlib import import_module as load_module\n"
                b"load_module('copyreg')\n"
            )
            self.assertEqual(
                SUBJECT._target_copyreg_constructor_observation_facts(
                    aliased_dynamic_import_files,
                ),
                {},
            )

    def test_call_closure_accepts_only_bounded_trusted_condition_observations(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled):\n"
                b"    if enabled:\n        from . import yes\n"
                b"    else:\n        from . import no\n"
                b"choose(True)\nchoose(unknown)\n"
            ),
            "pkg/yes.py": b"VALUE = True\n",
            "pkg/no.py": b"VALUE = False\n",
        }
        unknown = []
        resolved = []
        trusted = {("pkg", "pkg/__init__.py", 2): (False, True)}
        result = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), trusted_condition_observations=trusted,
            unknown_conditions=unknown, resolved_conditions=resolved,
        )
        self.assertEqual(result[4], {"resolved": 1, "unknown": 0})
        self.assertEqual(unknown, [])
        self.assertEqual(resolved[0]["decisions"], [False, True])
        with self.assertRaisesRegex(ValueError, "UNTRUSTED_CONDITION_OBSERVATION"):
            SUBJECT._module_init_call_candidate_closure(
                files, ("pkg",), trusted_condition_observations={
                    ("pkg", "pkg/__init__.py", 2): (0, True),
                },
            )

    def test_opcode_pseudo_op_fact_requires_every_pinned_registration(self):
        calls = {
            262: "pseudo_op('SETUP_FINALLY', 256, ['NOP'])",
            264: "pseudo_op('SETUP_CLEANUP', 257, ['NOP'])",
            266: "pseudo_op('SETUP_WITH', 258, ['NOP'])",
            268: "pseudo_op('POP_BLOCK', 259, ['NOP'])",
            270: "pseudo_op('JUMP', 260, ['JUMP_FORWARD', 'JUMP_BACKWARD'])",
            271: "pseudo_op('JUMP_NO_INTERRUPT', 261, "
                 "['JUMP_FORWARD', 'JUMP_BACKWARD_NO_INTERRUPT'])",
            273: "pseudo_op('LOAD_METHOD', 262, ['LOAD_ATTR'])",
            274: "pseudo_op('LOAD_SUPER_METHOD', 263, ['LOAD_SUPER_ATTR'])",
            275: "pseudo_op('LOAD_ZERO_SUPER_METHOD', 264, ['LOAD_SUPER_ATTR'])",
            276: "pseudo_op('LOAD_ZERO_SUPER_ATTR', 265, ['LOAD_SUPER_ATTR'])",
            278: "pseudo_op('STORE_FAST_MAYBE_NULL', 266, ['STORE_FAST'])",
        }
        lines = {
            42: "oplists = [hasarg, hasconst, hasname, hasjrel, hasjabs, haslocal, hascompare, hasfree, hasexc]",
            66: "def pseudo_op(name, op, real_ops):",
            67: "    def_op(name, op)",
            68: "    _pseudo_ops[name] = real_ops",
            70: "    for oplist in oplists:",
            71: "        res = [opmap[rop] in oplist for rop in real_ops]",
            72: "        if any(res):",
            73: "            assert all(res)",
            74: "            oplist.append(op)",
        }
        lines.update(calls)

        def make_source(rows):
            content = [""] * max(rows)
            for number, statement in rows.items():
                content[number - 1] = statement
            return ("\n".join(content) + "\n").encode()

        source = make_source(lines)
        with patch.object(
            SUBJECT, "OPCODE_SOURCE_SHA256", hashlib.sha256(source).hexdigest(),
        ):
            self.assertEqual(
                SUBJECT._target_opcode_pseudo_op_condition_facts(
                    {"opcode.py": source},
                ),
                {("opcode", "opcode.py", 72): (False, True)},
            )
            mutated = dict(lines)
            mutated[279] = "pseudo_op('UNEXPECTED', 267, ['NOP'])"
            mutated_source = make_source(mutated)
            with patch.object(
                SUBJECT, "OPCODE_SOURCE_SHA256",
                hashlib.sha256(mutated_source).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_opcode_pseudo_op_condition_facts(
                        {"opcode.py": mutated_source},
                    ),
                    {},
                )
            changed_function = dict(lines)
            changed_function[73] = "            pass"
            changed_function_source = make_source(changed_function)
            with patch.object(
                SUBJECT, "OPCODE_SOURCE_SHA256",
                hashlib.sha256(changed_function_source).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_opcode_pseudo_op_condition_facts(
                        {"opcode.py": changed_function_source},
                    ),
                    {},
                )

    def test_json_encoder_import_constructor_arguments_require_complete_sources(self):
        encoder_lines = {
            120: "class JSONEncoder(object):",
            121: "    def __init__(self, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False, indent=None, separators=None, default=None):",
            154: "        if separators is not None:",
            155: "            self.item_separator, self.key_separator = separators",
            156: "        elif indent is not None:",
            157: "            self.item_separator = ','",
            158: "        if default is not None:",
            159: "            self.default = default",
        }
        package_lines = {
            107: "from .encoder import JSONEncoder",
            110: "_default_encoder = JSONEncoder(",
            111: "    skipkeys=False,",
            112: "    ensure_ascii=True,",
            113: "    check_circular=True,",
            114: "    allow_nan=True,",
            115: "    indent=None,",
            116: "    separators=None,",
            117: "    default=None,",
            118: ")",
        }

        def make_source(lines):
            content = [""] * max(lines)
            for number, statement in lines.items():
                content[number - 1] = statement
            return ("\n".join(content) + "\n").encode()

        files = {
            "json/encoder.py": make_source(encoder_lines),
            "json/__init__.py": make_source(package_lines),
        }
        with patch.multiple(
            SUBJECT,
            JSON_ENCODER_SOURCE_SHA256=hashlib.sha256(
                files["json/encoder.py"],
            ).hexdigest(),
            JSON_PACKAGE_SOURCE_SHA256=hashlib.sha256(
                files["json/__init__.py"],
            ).hexdigest(),
        ):
            self.assertEqual(
                SUBJECT._target_json_encoder_argument_condition_facts(files),
                {
                    ("json.encoder", "json/encoder.py", 154): (False,),
                    ("json.encoder", "json/encoder.py", 156): (False,),
                    ("json.encoder", "json/encoder.py", 158): (False,),
                },
            )
            aliased = dict(files)
            aliased["extra.py"] = (
                b"from json.encoder import JSONEncoder as Encoder\n"
                b"Encoder(separators=(',', ':'))\n"
            )
            self.assertEqual(
                SUBJECT._target_json_encoder_argument_condition_facts(aliased),
                {},
            )

    def test_hashlib_algorithm_guards_require_pinned_init_tuple_and_call_route(self):
        algorithms = (
            "'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512', "
            "'blake2b', 'blake2s', 'sha3_224', 'sha3_256', 'sha3_384', "
            "'sha3_512', 'shake_128', 'shake_256'")
        lines = {
            58: f"__always_supported = ({algorithms})",
            78: "__block_openssl_constructor = {'blake2b', 'blake2s'}",
            82: "def __get_builtin_constructor(name):",
            88: "    if name in {'SHA1', 'sha1'}:",
            89: "        pass",
            91: "    elif name in {'MD5', 'md5'}:",
            92: "        pass",
            94: "    elif name in {'SHA256', 'sha256', 'SHA224', 'sha224'}:",
            95: "        pass",
            98: "    elif name in {'SHA512', 'sha512', 'SHA384', 'sha384'}:",
            99: "        pass",
            102: "    elif name in {'blake2b', 'blake2s'}:",
            103: "        pass",
            106: "    elif name in {'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512'}:",
            107: "        pass",
            112: "    elif name in {'shake_128', 'shake_256'}:",
            113: "        pass",
            126: "def __get_openssl_constructor(name):",
            127: "    if name in __block_openssl_constructor:",
            128: "        pass",
            241: "for __func_name in __always_supported:",
            242: "    __get_hash(__func_name)",
        }

        def make_source(rows):
            content = [""] * max(rows)
            for number, statement in rows.items():
                content[number - 1] = statement
            return ("\n".join(content) + "\n").encode()

        source = make_source(lines)
        expected = {
            ("hashlib", "hashlib.py", line): (False, True)
            for line in (88, 91, 94, 98, 102, 106, 112, 127)
        }
        with patch.object(
            SUBJECT, "HASHLIB_SOURCE_SHA256", hashlib.sha256(source).hexdigest(),
        ):
            self.assertEqual(
                SUBJECT._target_hashlib_name_condition_facts(
                    {"hashlib.py": source},
                ),
                expected,
            )
            unsafe = {"hashlib.py": source, "extra.py": (
                b"import hashlib as hashes\nhashes.new('sha256')\n"
            )}
            self.assertEqual(
                SUBJECT._target_hashlib_name_condition_facts(unsafe),
                {},
            )

    def test_hashlib_builtin_fallback_files_require_source_and_image_binding(self):
        rows = {
            82: "def __get_builtin_constructor(name):",
            88: "    if name in {'SHA1', 'sha1'}:",
            89: "        import _sha1",
            90: "        cache['SHA1'] = cache['sha1'] = _sha1.sha1",
            91: "    elif name in {'MD5', 'md5'}:",
            92: "        import _md5",
            93: "        cache['MD5'] = cache['md5'] = _md5.md5",
            94: "    elif name in {'SHA256', 'sha256', 'SHA224', 'sha224'}:",
            95: "        import _sha2",
            96: "        cache['SHA224'] = cache['sha224'] = _sha2.sha224",
            97: "        cache['SHA256'] = cache['sha256'] = _sha2.sha256",
            98: "    elif name in {'SHA512', 'sha512', 'SHA384', 'sha384'}:",
            99: "        import _sha2",
            100: "        cache['SHA384'] = cache['sha384'] = _sha2.sha384",
            101: "        cache['SHA512'] = cache['sha512'] = _sha2.sha512",
            102: "    elif name in {'blake2b', 'blake2s'}:",
            103: "        import _blake2",
            104: "        cache['blake2b'] = _blake2.blake2b",
            105: "        cache['blake2s'] = _blake2.blake2s",
            106: "    elif name in {'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512'}:",
            107: "        import _sha3",
            108: "        cache['sha3_224'] = _sha3.sha3_224",
            109: "        cache['sha3_256'] = _sha3.sha3_256",
            110: "        cache['sha3_384'] = _sha3.sha3_384",
            111: "        cache['sha3_512'] = _sha3.sha3_512",
            112: "    elif name in {'shake_128', 'shake_256'}:",
            113: "        import _sha3",
            114: "        cache['shake_128'] = _sha3.shake_128",
            115: "        cache['shake_256'] = _sha3.shake_256",
        }
        source_lines = [""] * 115
        for line, statement in rows.items():
            source_lines[line - 1] = statement
        source = ("\n".join(source_lines) + "\n").encode()
        conditions = {
            ("hashlib", "hashlib.py", row[0]): (False, True)
            for row in SUBJECT.HASHLIB_BUILTIN_FALLBACK_BRANCHES
        }
        image_extensions = {
            path: {"sha256": digest, "size": 32}
            for path, digest in SUBJECT.HASHLIB_EXTENSION_FACTS.items()
        }
        with patch.object(
            SUBJECT, "HASHLIB_SOURCE_SHA256", hashlib.sha256(source).hexdigest(),
        ):
            candidates = SUBJECT._target_hashlib_builtin_fallback_file_candidates(
                {"hashlib.py": source}, conditions,
                {"hashlib_extension_facts": image_extensions},
            )
            self.assertEqual(len(candidates), 7)
            md5 = next(row for row in candidates if row["fallback_module"] == "_md5")
            self.assertEqual(md5["algorithm_names"], ["MD5", "md5"])
            self.assertFalse(md5["import_attempt_observed"])
            self.assertFalse(md5["constructor_success_observed"])

            incomplete_image = dict(image_extensions)
            incomplete_image.pop(md5["image_path"])
            self.assertEqual(
                SUBJECT._target_hashlib_builtin_fallback_file_candidates(
                    {"hashlib.py": source}, conditions,
                    {"hashlib_extension_facts": incomplete_image},
                ),
                [],
            )

    def test_re_compile_input_candidates_are_module_init_source_only(self):
        source = b"""import re as regex
from re import compile as make_regex
regex.compile('text')
make_regex(b'binary')
regex.compile('flagged', flags=0)
if FLAG:
    regex.compile(pattern)
def deferred():
    regex.compile(b'not module init')
"""
        candidates = SUBJECT._target_re_compile_input_candidates(
            {"pkg.py": source}, ("pkg",),
        )
        self.assertEqual(
            [row["argument_kind"] for row in candidates],
            ["STRING_LITERAL", "BYTES_LITERAL", "STRING_LITERAL",
             "UNRESOLVED_EXPRESSION"],
        )
        self.assertEqual(
            [row["api_form"] for row in candidates],
            ["re_module_compile_attribute", "re_imported_compile_name",
             "re_module_compile_attribute", "re_module_compile_attribute"],
        )
        self.assertEqual(
            [row["flags_argument_kind"] for row in candidates],
            ["OMITTED", "OMITTED", "INT_LITERAL", "OMITTED"],
        )
        self.assertEqual(
            [row["flags_literal_value"] for row in candidates],
            [None, None, 0, None],
        )
        self.assertTrue(all(not row["compile_call_observed"]
                            and not row["pattern_parse_observed"]
                            for row in candidates))
        self.assertTrue(all(row["source_sha256"]
                            and row["source_path"] == "pkg.py"
                            for row in candidates))
        self.assertEqual(
            SUBJECT._target_re_compile_input_candidates(
                {"pkg.py": b"regex.compile('shadowed')\n"}, ("pkg",),
            ),
            [],
        )
        self.assertEqual(
            SUBJECT._target_re_compile_input_candidates(
                {"pkg.py": b"regex.compile('before import')\nimport re as regex\n"},
                ("pkg",),
            ),
            [],
        )
        rebound = SUBJECT._target_re_compile_input_candidates(
            {"pkg.py": b"import re as regex\nregex.compile('before rebind')\n"
             b"regex = object()\nregex.compile('after rebind')\n"},
            ("pkg",),
        )
        self.assertEqual([row["line"] for row in rebound], [2])
        same_line = SUBJECT._target_re_compile_input_candidates(
            {"pkg.py": b"import re as regex; regex.compile('same line')\n"},
            ("pkg",),
        )
        self.assertEqual([row["line"] for row in same_line], [1])
        attribute_rebound = SUBJECT._target_re_compile_input_candidates(
            {"pkg.py": b"import re as regex\nregex.compile('before patch')\n"
             b"regex.compile = object\nregex.compile('after patch')\n"},
            ("pkg",),
        )
        self.assertEqual([row["line"] for row in attribute_rebound], [2])

    def test_regex_inline_verbose_flag_candidates_ignore_escapes_and_classes(self):
        self.assertEqual(
            SUBJECT._regex_inline_flag_directive_candidates(
                r"(?x: verbose )[(?x)]\(\?x\)(?-ix:literal)"
            ),
            [
                {
                    "offset": 0,
                    "scope": "SCOPED",
                    "enabled_flags": "x",
                    "disabled_flags": "",
                    "evidence_scope": "LEXICAL_INLINE_REGEX_FLAG_CANDIDATE",
                },
                {
                    "offset": 27,
                    "scope": "SCOPED",
                    "enabled_flags": "",
                    "disabled_flags": "ix",
                    "evidence_scope": "LEXICAL_INLINE_REGEX_FLAG_CANDIDATE",
                },
            ],
        )
        self.assertEqual(
            SUBJECT._regex_inline_flag_directive_candidates(b"(?i-x:bytes)"),
            [
                {
                    "offset": 0,
                    "scope": "SCOPED",
                    "enabled_flags": "i",
                    "disabled_flags": "x",
                    "evidence_scope": "LEXICAL_INLINE_REGEX_FLAG_CANDIDATE",
                },
            ],
        )
        self.assertEqual(
            SUBJECT._regex_inline_flag_directive_candidates(r"(?P<name>x)"),
            [],
        )
        self.assertIsNone(
            SUBJECT._regex_inline_flag_directive_candidates(42),
        )

    def test_regex_verbose_ignored_syntax_candidates_skip_escapes_and_classes(self):
        self.assertEqual(
            SUBJECT._regex_verbose_ignored_syntax_candidates(
                "a b[ c]\x5c d#note\nz", frozenset(" " + "\x09\x0a\x0d\x0b\x0c"),
            ),
            [
                {"offset": 1, "kind": "WHITESPACE"},
                {"offset": 10, "kind": "COMMENT_MARKER"},
            ],
        )
        self.assertEqual(
            SUBJECT._regex_verbose_ignored_syntax_candidates(
                b"x\x09#bytes", frozenset(" " + "\x09\x0a\x0d\x0b\x0c"),
            ),
            [
                {"offset": 1, "kind": "WHITESPACE"},
                {"offset": 2, "kind": "COMMENT_MARKER"},
            ],
        )
        self.assertEqual(
            SUBJECT._regex_verbose_ignored_syntax_candidates(
                "escaped\x5c space[#]", frozenset(" "),
            ),
            [],
        )
        self.assertIsNone(
            SUBJECT._regex_verbose_ignored_syntax_candidates("x", {" "}),
        )
        self.assertIsNone(
            SUBJECT._regex_verbose_ignored_syntax_candidates(42, frozenset(" ")),
        )

    def test_pinned_re_compile_cache_path_precedes_parser_without_observing_cache(self):
        source = (
            b"_cache2 = {}\n"
            b"_cache = {}\n"
            b"def _compile(pattern, flags):\n"
            b"    if isinstance(flags, RegexFlag):\n"
            b"        flags = flags.value\n"
            b"    try:\n"
            b"        return _cache2[type(pattern), pattern, flags]\n"
            b"    except KeyError:\n"
            b"        pass\n"
            b"    key = (type(pattern), pattern, flags)\n"
            b"    p = _cache.pop(key, None)\n"
            b"    if p is None:\n"
            b"        if isinstance(pattern, Pattern):\n"
            b"            if flags:\n"
            b"                raise ValueError\n"
            b"            return pattern\n"
            b"        if not _compiler.isstring(pattern):\n"
            b"            raise TypeError\n"
            b"        p = _compiler.compile(pattern, flags)\n"
            b"    _cache[key] = p\n"
            b"    _cache2[key] = p\n"
            b"    return p\n"
        )
        with patch.object(
                SUBJECT, "RE_INIT_SOURCE_SHA256",
                hashlib.sha256(source).hexdigest()):
            fact = SUBJECT._target_re_compile_cache_path_candidate(
                {"re/__init__.py": source},
            )
            self.assertEqual(fact["cache_lookup_order"], ["_cache2", "_cache"])
            self.assertEqual(
                fact["cache_key_expression"],
                "(type(pattern), pattern, flags)",
            )
            self.assertTrue(fact["parser_compile_call_on_both_cache_misses_candidate"])
            self.assertFalse(fact["cache_state_observed"])
            self.assertFalse(fact["cache_lookup_observed"])
            self.assertFalse(fact["parser_entry_observed"])

            for original, replacement in (
                    (b"return _cache2[type(pattern), pattern, flags]",
                     b"return _cache[type(pattern), pattern, flags]"),
                    (b"key = (type(pattern), pattern, flags)",
                     b"key = (type(pattern), pattern, 0)"),
                    (b"p = _cache.pop(key, None)",
                     b"p = _cache2.pop(key, None)"),
                    (b"p = _compiler.compile(pattern, flags)",
                     b"p = _compiler.other(pattern, flags)")):
                changed = source.replace(original, replacement, 1)
                with patch.object(
                        SUBJECT, "RE_INIT_SOURCE_SHA256",
                        hashlib.sha256(changed).hexdigest()):
                    self.assertIsNone(SUBJECT._target_re_compile_cache_path_candidate(
                        {"re/__init__.py": changed},
                    ))

    def test_re_compile_literal_types_bind_to_pinned_tokenizer_source_flow(self):
        files = {
            "pkg.py": (
                b"import re\n"
                b"re.compile('text space')\n"
                b"re.compile(b'bytes[ x]')\n"
                b"FLAGS = re.VERBOSE | re.MULTILINE\n"
                b"re.compile('flagged #note\\nnext', re.VERBOSE | re.MULTILINE)\n"
                b"re.compile('named\\\\ pattern', FLAGS)\n"
            ),
            "re/__init__.py": (
                b"import enum\n"
                b"from . import _compiler, _parser\n"
                b"@enum.global_enum\n"
                b"@enum._simple_enum(enum.IntFlag, boundary=enum.KEEP)\n"
                b"class RegexFlag:\n"
                b"    ASCII = A = _compiler.SRE_FLAG_ASCII\n"
                b"    MULTILINE = M = _compiler.SRE_FLAG_MULTILINE\n"
                b"    DOTALL = S = _compiler.SRE_FLAG_DOTALL\n"
                b"    VERBOSE = X = _compiler.SRE_FLAG_VERBOSE\n"
                b"_cache2 = {}\n"
                b"_cache = {}\n"
                b"def compile(pattern, flags=0):\n"
                b"    return _compile(pattern, flags)\n"
                b"def _compile(pattern, flags):\n"
                b"    if isinstance(flags, RegexFlag):\n"
                b"        flags = flags.value\n"
                b"    try:\n"
                b"        return _cache2[type(pattern), pattern, flags]\n"
                b"    except KeyError:\n"
                b"        pass\n"
                b"    key = (type(pattern), pattern, flags)\n"
                b"    p = _cache.pop(key, None)\n"
                b"    if p is None:\n"
                b"        if isinstance(pattern, Pattern):\n"
                b"            if flags:\n"
                b"                raise ValueError\n"
                b"            return pattern\n"
                b"        if not _compiler.isstring(pattern):\n"
                b"            raise TypeError\n"
                b"        p = _compiler.compile(pattern, flags)\n"
                b"    _cache[key] = p\n"
                b"    _cache2[key] = p\n"
                b"    return p\n"
            ),
            "re/_compiler.py": (
                b"from ._constants import *\n"
                b"def _compile(code, pattern, flags):\n"
                b"    emit = code.append\n"
                b"    _len = len\n"
                b"    for op, av in pattern:\n"
                b"        if op is BRANCH:\n"
                b"            emit(op)\n"
                b"            tail = []\n"
                b"            tailappend = tail.append\n"
                b"            for av in av[1]:\n"
                b"                skip = _len(code)\n"
                b"                emit(0)\n"
                b"                _compile(code, av, flags)\n"
                b"                emit(JUMP)\n"
                b"                tailappend(_len(code))\n"
                b"                emit(0)\n"
                b"                code[skip] = _len(code) - skip\n"
                b"            emit(FAILURE)\n"
                b"            for tail in tail:\n"
                b"                code[tail] = _len(code) - tail\n"
                b"def _code(p, flags):\n"
                b"    flags = p.state.flags | flags\n"
                b"    code = []\n"
                b"    _compile_info(code, p, flags)\n"
                b"    _compile(code, p.data, flags)\n"
                b"    code.append(SUCCESS)\n"
                b"    return code\n"
                b"def isstring(obj):\n"
                b"    return isinstance(obj, (str, bytes))\n"
                b"def compile(p, flags=0):\n"
                b"    if isstring(p):\n"
                b"        pattern = p\n"
                b"        p = _parser.parse(p, flags)\n"
                b"    else:\n"
                b"        pattern = None\n"
                b"    code = _code(p, flags)\n"
                b"    if flags & SRE_FLAG_DEBUG:\n"
                b"        print()\n"
                b"        dis(code)\n"
                b"    groupindex = p.state.groupdict\n"
                b"    indexgroup = [None] * p.state.groups\n"
                b"    for k, i in groupindex.items():\n"
                b"        indexgroup[i] = k\n"
                b"    return _sre.compile(pattern, flags | p.state.flags, code, p.state.groups - 1, groupindex, tuple(indexgroup))\n"
            ),
            "re/_constants.py": (
                b"SRE_FLAG_ASCII = 256\n"
                b"SRE_FLAG_MULTILINE = 8\n"
                b"SRE_FLAG_DOTALL = 16\n"
                b"SRE_FLAG_VERBOSE = 64\n"
            ),
            "re/_parser.py": (
                b"class State:\n"
                b"    def __init__(self):\n"
                b"        self.flags = 0\n"
                b"        self.groupdict = {}\n"
                b"        self.groupwidths = [None]\n"
                b"        self.lookbehindgroups = None\n"
                b"        self.grouprefpos = {}\n"
                b"    @property\n"
                b"    def groups(self):\n"
                b"        return len(self.groupwidths)\n"
                b"    def opengroup(self, name=None):\n"
                b"        gid = self.groups\n"
                b"        self.groupwidths.append(None)\n"
                b"        if self.groups > MAXGROUPS:\n"
                b"            raise error('too many groups')\n"
                b"        if name is not None:\n"
                b"            ogid = self.groupdict.get(name, None)\n"
                b"            if ogid is not None:\n"
                b"                raise error('duplicate')\n"
                b"            self.groupdict[name] = gid\n"
                b"        return gid\n"
                b"    def closegroup(self, gid, p):\n"
                b"        self.groupwidths[gid] = p.getwidth()\n"
                b"    def checkgroup(self, gid):\n"
                b"        return gid < self.groups and self.groupwidths[gid] is not None\n"
                b"    def checklookbehindgroup(self, gid, source):\n"
                b"        if self.lookbehindgroups is not None:\n"
                b"            if not self.checkgroup(gid):\n"
                b"                raise source.error('cannot refer to an open group')\n"
                b"            if gid >= self.lookbehindgroups:\n"
                b"                raise source.error('cannot refer to group defined in the same lookbehind subpattern')\n"
                b"class SubPattern:\n"
                b"    def getwidth(self):\n"
                b"        for op, av in self.data:\n"
                b"            if op is GROUPREF:\n"
                b"                i, j = self.state.groupwidths[av]\n"
                b"                lo = lo + i\n"
                b"                hi = hi + j\n"
                b"            elif op is GROUPREF_EXISTS:\n"
                b"                i, j = av[1].getwidth()\n"
                b"                if av[2] is not None:\n"
                b"                    l, h = av[2].getwidth()\n"
                b"                    i = min(i, l)\n"
                b"                    j = max(j, h)\n"
                b"                else:\n"
                b"                    i = 0\n"
                b"                lo = lo + i\n"
                b"                hi = hi + j\n"
                b"WHITESPACE = frozenset(' \\t\\n\\r\\v\\f')\n"
                b"def _uniq(items):\n"
                b"    return list(dict.fromkeys(items))\n"
                b"def _parse_sub(source, state, verbose, nested):\n"
                b"    items = []\n"
                b"    itemsappend = items.append\n"
                b"    sourcematch = source.match\n"
                b"    while True:\n"
                b"        itemsappend(_parse(source, state, verbose, nested + 1, not nested and not items))\n"
                b"        if not sourcematch('|'):\n"
                b"            break\n"
                b"        if not nested:\n"
                b"            verbose = state.flags & SRE_FLAG_VERBOSE\n"
                b"    if len(items) == 1:\n"
                b"        return items[0]\n"
                b"    subpattern = SubPattern(state)\n"
                b"    while True:\n"
                b"        prefix = None\n"
                b"        for item in items:\n"
                b"            if not item:\n"
                b"                break\n"
                b"            if prefix is None:\n"
                b"                prefix = item[0]\n"
                b"            elif item[0] != prefix:\n"
                b"                break\n"
                b"        else:\n"
                b"            for item in items:\n"
                b"                del item[0]\n"
                b"            subpattern.append(prefix)\n"
                b"            continue\n"
                b"        break\n"
                b"    set = []\n"
                b"    for item in items:\n"
                b"        if len(item) != 1:\n"
                b"            break\n"
                b"        op, av = item[0]\n"
                b"        if op is LITERAL:\n"
                b"            set.append((op, av))\n"
                b"        elif op is IN and av[0][0] is not NEGATE:\n"
                b"            set.extend(av)\n"
                b"        else:\n"
                b"            break\n"
                b"    else:\n"
                b"        subpattern.append((IN, _uniq(set)))\n"
                b"        return subpattern\n"
                b"    subpattern.append((BRANCH, (None, items)))\n"
                b"    return subpattern\n"
                b"def _parse(source, state, verbose, nested, first=False):\n"
                b"    sourceget = source.get\n"
                b"    sourceget()\n"
                b"    if capture:\n"
                b"        try:\n"
                b"            group = state.opengroup(name)\n"
                b"        except error as err:\n"
                b"            raise source.error(err.msg, len(name) + 1) from None\n"
                b"    else:\n"
                b"        group = None\n"
                b"    p = _parse_sub(source, state, sub_verbose, nested + 1)\n"
                b"    if not source.match(')'):\n"
                b"        raise source.error('missing close')\n"
                b"    if group is not None:\n"
                b"        state.closegroup(group, p)\n"
                b"    if not state.checkgroup(gid):\n"
                b"        raise source.error('open group')\n"
                b"    state.checklookbehindgroup(gid, source)\n"
                b"    state.checklookbehindgroup(condgroup, source)\n"
                b"    lookbehindgroups = state.lookbehindgroups\n"
                b"    if lookbehindgroups is None:\n"
                b"        state.lookbehindgroups = state.groups\n"
                b"    if dir < 0:\n"
                b"        if lookbehindgroups is None:\n"
                b"            state.lookbehindgroups = None\n"
                b"    condgroup = int(condname)\n"
                b"    if condgroup >= MAXGROUPS:\n"
                b"        raise source.error('invalid group')\n"
                b"    if condgroup not in state.grouprefpos:\n"
                b"        state.grouprefpos[condgroup] = source.tell() - len(condname) - 1\n"
                b"    if verbose:\n"
                b"        if this in WHITESPACE:\n"
                b"            continue\n"
                b"        if this == '#':\n"
                b"            while True:\n"
                b"                this = sourceget()\n"
                b"                if this is None or this == '\\n':\n"
                b"                    break\n"
                b"            continue\n"
                b"def _escape(source, escape, state):\n"
                b"    if group < state.groups:\n"
                b"        if not state.checkgroup(group):\n"
                b"            raise source.error('open group')\n"
                b"        state.checklookbehindgroup(group, source)\n"
                b"        return GROUPREF, group\n"
                b"class Tokenizer:\n"
                b"    def __init__(self, string):\n"
                b"        self.istext = isinstance(string, str)\n"
                b"        self.string = string\n"
                b"        if not self.istext:\n"
                b"            string = str(string, 'latin1')\n"
                b"        self.decoded_string = string\n"
                b"        self.index = 0\n"
                b"        self.next = None\n"
                b"        self.__next()\n"
                b"    def __next(self):\n"
                b"        index = self.index\n"
                b"        try:\n"
                b"            char = self.decoded_string[index]\n"
                b"        except IndexError:\n"
                b"            self.next = None\n"
                b"            return\n"
                b"        if char == '\\\\':\n"
                b"            index += 1\n"
                b"            try:\n"
                b"                char += self.decoded_string[index]\n"
                b"            except IndexError:\n"
                b"                raise error('bad escape (end of pattern)', self.string, len(self.string) - 1) from None\n"
                b"        self.index = index + 1\n"
                b"        self.next = char\n"
                b"    def get(self):\n"
                b"        this = self.next\n"
                b"        self.__next()\n"
                b"        return this\n"
                b"def parse(str, flags=0, state=None):\n"
                b"    source = Tokenizer(str)\n"
                b"    p = _parse_sub(source, state, flags & SRE_FLAG_VERBOSE, 0)\n"
                b"    for g in p.state.grouprefpos:\n"
                b"        if g >= p.state.groups:\n"
                b"            msg = 'invalid group reference %d' % g\n"
                b"            raise error(msg, str, p.state.grouprefpos[g])\n"
            ),
        }
        digests = {
            "RE_INIT_SOURCE_SHA256": hashlib.sha256(files["re/__init__.py"]).hexdigest(),
            "RE_COMPILER_SOURCE_SHA256": hashlib.sha256(
                files["re/_compiler.py"]
            ).hexdigest(),
            "RE_PARSER_SOURCE_SHA256": hashlib.sha256(
                files["re/_parser.py"]
            ).hexdigest(),
            "RE_CONSTANTS_SOURCE_SHA256": hashlib.sha256(
                files["re/_constants.py"]
            ).hexdigest(),
        }
        with (patch.object(SUBJECT, "RE_INIT_SOURCE_SHA256", digests[
                    "RE_INIT_SOURCE_SHA256"]),
              patch.object(SUBJECT, "RE_COMPILER_SOURCE_SHA256", digests[
                    "RE_COMPILER_SOURCE_SHA256"]),
              patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256", digests[
                    "RE_PARSER_SOURCE_SHA256"]),
              patch.object(SUBJECT, "RE_CONSTANTS_SOURCE_SHA256", digests[
                    "RE_CONSTANTS_SOURCE_SHA256"])):
            candidates = SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                files, ("pkg", "re", "re._compiler", "re._constants",
                        "re._parser"),
            )
            self.assertEqual(len(candidates), 4)
            self.assertEqual(
                [row["pattern_type_if_call_evaluates"] for row in candidates],
                ["str", "bytes", "str", "str"],
            )
            self.assertEqual(
                [row["tokenizer_istext_if_parser_entry_reached"]
                 for row in candidates],
                [True, False, True, True],
            )
            self.assertEqual(
                [row["flags_value_if_call_evaluates"] for row in candidates],
                [0, 0, 72, 72],
            )
            self.assertEqual(
                [row["verbose_mode_if_parser_entry_reached"] for row in candidates],
                [False, False, True, True],
            )
            self.assertEqual(
                [row["inline_verbose_flag_group_candidates_if_literal_bound"]
                 for row in candidates],
                [[], [], [], []],
            )
            self.assertTrue(all(row["inline_verbose_flag_scan_bound"]
                                for row in candidates))
            self.assertEqual(
                [row[
                    "verbose_ignored_syntax_candidates_if_verbose_and_literal_bound"
                ] for row in candidates],
                [
                    [{"offset": 4, "kind": "WHITESPACE"}],
                    [],
                    [
                        {"offset": 7, "kind": "WHITESPACE"},
                        {"offset": 8, "kind": "COMMENT_MARKER"},
                    ],
                    [],
                ],
            )
            self.assertEqual(
                [row["flags_resolution"] for row in candidates],
                ["PINNED_DEFAULT_ZERO", "PINNED_DEFAULT_ZERO",
                 "PINNED_REGEXFLAG_EXPRESSION", "PINNED_REGEXFLAG_EXPRESSION"],
            )
            self.assertTrue(all(not row["parser_entry_observed"]
                                and not row["standard_re_compile_binding_observed"]
                                for row in candidates))
            self.assertTrue(all(
                row["cache_path_candidate"]["cache_lookup_order"]
                == ["_cache2", "_cache"] for row in candidates
            ))
            self.assertTrue(all(
                not row["cache_path_candidate"]["cache_state_observed"]
                and not row["cache_path_candidate"]["parser_entry_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["tokenizer_access_candidate"]["bytes_to_text_expression"]
                == "str(string, 'latin1')"
                and row["tokenizer_access_candidate"]["escaped_character_access"]
                == "backslash plus following character"
                and row["tokenizer_access_candidate"]["trailing_backslash_behavior"]
                == "parser error candidate"
                and not row["tokenizer_access_candidate"]["tokenizer_execution_observed"]
                and not row["tokenizer_access_candidate"]["pattern_parse_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["parser_sourceget_candidate"]["_parse_alias_assignment"]
                == "sourceget = source.get"
                and row["parser_sourceget_candidate"][
                    "tokenizer_get_returns_current_then_advances"]
                and row["parser_sourceget_candidate"][
                    "sourceget_call_sites_in_pinned_parse_function"] == 2
                and not row["parser_sourceget_candidate"][
                    "alias_call_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["parser_sub_dispatch_candidate"]["dispatch_function"]
                == "_parse_sub"
                and row["parser_sub_dispatch_candidate"]["target_function"]
                == "_parse"
                and row["parser_sub_dispatch_candidate"]["dispatch_arguments"]
                == ["source", "state", "verbose", "nested + 1",
                    "not nested and (not items)"]
                and row["parser_sub_dispatch_candidate"][
                    "dispatch_is_wrapped_by"] == "itemsappend"
                and not row["parser_sub_dispatch_candidate"][
                    "parser_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["parser_alternation_candidate"]["alternation_match_alias"]
                == "sourcematch = source.match"
                and row["parser_alternation_candidate"][
                    "loop_continues_while_alternation_matches"] == "|"
                and row["parser_alternation_candidate"][
                    "root_group_verbose_refresh"]
                == "state.flags & SRE_FLAG_VERBOSE"
                and row["parser_alternation_candidate"][
                    "single_alternative_return"] == "items[0]"
                and not row["parser_alternation_candidate"][
                    "parser_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["parser_multi_alternative_candidate"][
                    "single_alternative_result"] == "items[0]"
                and row["parser_multi_alternative_candidate"][
                    "multiple_alternatives_container"] == "SubPattern(state)"
                and row["parser_multi_alternative_candidate"][
                    "common_prefix_append"] == "subpattern.append(prefix)"
                and row["parser_multi_alternative_candidate"][
                    "character_set_optimization_append"]
                == "subpattern.append((IN, _uniq(set)))"
                and row["parser_multi_alternative_candidate"][
                    "general_branch_append"]
                == "subpattern.append((BRANCH, (None, items)))"
                and row["parser_multi_alternative_candidate"][
                    "subpattern_return_sites"] == 2
                and not row["parser_multi_alternative_candidate"][
                    "parser_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["parser_charset_candidate"][
                    "each_alternative_must_have_one_item"]
                == "len(item) != 1 breaks shortcut"
                and row["parser_charset_candidate"]["accepted_item_kinds"]
                == ["LITERAL", "non-NEGATE IN"]
                and row["parser_charset_candidate"]["literal_items_added_as"]
                == "set.append((op, av))"
                and row["parser_charset_candidate"][
                    "positive_character_set_items_added_as"] == "set.extend(av)"
                and row["parser_charset_candidate"][
                    "shortcut_on_full_loop_completion"]
                == "subpattern.append((IN, _uniq(set)))"
                and not row["parser_charset_candidate"][
                    "parser_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["parser_prefix_candidate"]["prefix_initial_value"] is None
                and row["parser_prefix_candidate"]["prefix_comparison"]
                == "item[0] == prefix"
                and row["parser_prefix_candidate"][
                    "empty_alternative_stops_prefix_scan"]
                and row["parser_prefix_candidate"][
                    "mismatch_stops_prefix_scan"]
                and row["parser_prefix_candidate"][
                    "common_prefix_removed_from_each_alternative"] == "del item[0]"
                and row["parser_prefix_candidate"][
                    "common_prefix_added_to_subpattern"]
                == "subpattern.append(prefix)"
                and row["parser_prefix_candidate"][
                    "scan_repeats_after_prefix_extraction"]
                and not row["parser_prefix_candidate"][
                    "parser_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["parser_subpattern_order_candidate"][
                    "subpattern_paths_in_source_order"]
                == ["single alternative returns item", "extract shared prefix",
                    "try character-set shortcut", "append general BRANCH"]
                and row["parser_subpattern_order_candidate"][
                    "character_set_success_returns_before_general_branch"]
                and row["parser_subpattern_order_candidate"][
                    "general_branch_is_fallback_after_shortcut_loop"]
                and not row["parser_subpattern_order_candidate"][
                    "parser_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["parser_uniq_candidate"]["function_arguments"] == ["items"]
                and row["parser_uniq_candidate"]["deduplication_expression"]
                == "list(dict.fromkeys(items))"
                and row["parser_uniq_candidate"][
                    "preserves_first_occurrence_order_candidate"]
                and not row["parser_uniq_candidate"]["helper_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["parser_group_state_candidate"][
                    "group_zero_width_initializer"] == "self.groupwidths = [None]"
                and row["parser_group_state_candidate"]["group_count_source"]
                == "len(self.groupwidths)"
                and row["parser_group_state_candidate"]["new_group_index_source"]
                == "gid = self.groups"
                and row["parser_group_state_candidate"]["named_group_mapping"]
                == "self.groupdict[name] = gid"
                and row["parser_group_state_candidate"]["duplicate_name_guard"]
                == "self.groupdict.get(name, None)"
                and row["parser_group_state_candidate"][
                    "closed_group_width_assignment"]
                == "self.groupwidths[gid] = p.getwidth()"
                and row["parser_group_state_candidate"]["completed_group_check"]
                == "gid < self.groups and self.groupwidths[gid] is not None"
                and not row["parser_group_state_candidate"][
                    "parser_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["parser_group_call_candidate"]["capture_group_open_call"]
                == "state.opengroup(name)"
                and row["parser_group_call_candidate"]["capture_group_body_call"]
                == "_parse_sub(source, state, sub_verbose, nested + 1)"
                and row["parser_group_call_candidate"]["capture_group_close_call"]
                == "state.closegroup(group, p)"
                and row["parser_group_call_candidate"][
                    "group_width_lifecycle_order"]
                == ["allocate group index", "parse group body",
                    "match closing parenthesis", "store parsed group width"]
                and row["parser_group_call_candidate"]["parser_group_check_call"]
                == "state.checkgroup(gid)"
                and row["parser_group_call_candidate"]["escape_group_check_call"]
                == "state.checkgroup(group)"
                and not row["parser_group_call_candidate"][
                    "parser_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["parser_forward_group_candidate"][
                    "conditional_group_number_conversion"]
                == "condgroup = int(condname)"
                and row["parser_forward_group_candidate"][
                    "maximum_group_guard"] == "condgroup >= MAXGROUPS"
                and row["parser_forward_group_candidate"][
                    "deferred_group_position_assignment"]
                == "state.grouprefpos[condgroup] = source.tell() - len(condname) - 1"
                and row["parser_forward_group_candidate"][
                    "post_parse_registry_iteration"] == "for g in p.state.grouprefpos"
                and row["parser_forward_group_candidate"][
                    "final_group_count_guard"] == "g >= p.state.groups"
                and row["parser_forward_group_candidate"][
                    "invalid_reference_error"]
                == "error(msg, str, p.state.grouprefpos[g])"
                and row["parser_forward_group_candidate"][
                    "validation_after_pattern_parse"]
                and not row["parser_forward_group_candidate"][
                    "forward_reference_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["parser_lookbehind_candidate"]["lookbehind_boundary_source"]
                == "state.lookbehindgroups = state.groups"
                and row["parser_lookbehind_candidate"]["lookbehind_boundary_reset"]
                == "state.lookbehindgroups = None when no prior boundary existed"
                and row["parser_lookbehind_candidate"]["open_group_guard"]
                == "not self.checkgroup(gid)"
                and row["parser_lookbehind_candidate"][
                    "same_lookbehind_group_guard"]
                == "gid >= self.lookbehindgroups"
                and row["parser_lookbehind_candidate"][
                    "parser_reference_calls"]
                == ["state.checklookbehindgroup(gid, source)",
                    "state.checklookbehindgroup(condgroup, source)"]
                and row["parser_lookbehind_candidate"]["escape_reference_call"]
                == "state.checklookbehindgroup(group, source)"
                and not row["parser_lookbehind_candidate"][
                    "lookbehind_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["parser_group_width_candidate"]["group_reference_width_source"]
                == "self.state.groupwidths[av]"
                and row["parser_group_width_candidate"][
                    "group_reference_minimum_update"] == "lo = lo + i"
                and row["parser_group_width_candidate"][
                    "group_reference_maximum_update"] == "hi = hi + j"
                and row["parser_group_width_candidate"]["conditional_yes_width"]
                == "av[1].getwidth()"
                and row["parser_group_width_candidate"]["conditional_no_width"]
                == "av[2].getwidth()"
                and row["parser_group_width_candidate"]["conditional_minimum"]
                == "min(i, l)"
                and row["parser_group_width_candidate"]["conditional_maximum"]
                == "max(j, h)"
                and row["parser_group_width_candidate"][
                    "conditional_without_else_minimum"] == "i = 0"
                and not row["parser_group_width_candidate"][
                    "width_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["compiler_branch_candidate"]["compiler_branch_operator"]
                == "BRANCH"
                and row["compiler_branch_candidate"][
                    "alternative_container_expression"] == "av[1]"
                and row["compiler_branch_candidate"]["branch_end_marker"]
                == "FAILURE"
                and row["compiler_branch_candidate"]["branch_join_operator"]
                == "JUMP"
                and row["compiler_branch_candidate"][
                    "tail_offsets_patched_after_alternatives"]
                and not row["compiler_branch_candidate"][
                    "compiler_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["compiler_code_candidate"]["code_container_initializer"]
                == "code = []"
                and row["compiler_code_candidate"]["parsed_pattern_input"]
                == "p.data"
                and row["compiler_code_candidate"]["compiled_success_terminator"]
                == "code.append(SUCCESS)"
                and row["compiler_code_candidate"]["code_returned_to_compile"]
                == "code = _code(p, flags)"
                and row["compiler_code_candidate"]["code_passed_to_sre_compile"]
                and not row["compiler_code_candidate"][
                    "compiler_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["compiler_group_candidate"]["groupindex_source"]
                == "p.state.groupdict"
                and row["compiler_group_candidate"]["indexgroup_length"]
                == "p.state.groups"
                and row["compiler_group_candidate"]["indexgroup_population"]
                == "indexgroup[i] = k"
                and row["compiler_group_candidate"]["compiled_group_count"]
                == "p.state.groups - 1"
                and row["compiler_group_candidate"]["compile_flags_expression"]
                == "flags | p.state.flags"
                and row["compiler_group_candidate"][
                    "metadata_passed_to_sre_compile"]
                == ["groupindex", "tuple(indexgroup)"]
                and not row["compiler_group_candidate"][
                    "compiler_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["compiler_debug_candidate"]["debug_flag_condition"]
                == "flags & SRE_FLAG_DEBUG"
                and row["compiler_debug_candidate"]["disassembled_value"]
                == "code"
                and row["compiler_debug_candidate"]["order"]
                == "after_code_generation_before_group_metadata_and_native_compile"
                and not row["compiler_debug_candidate"][
                    "compiler_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(
                row["compiler_input_candidate"]["string_input_branch"]
                == "pattern = p; p = _parser.parse(p, flags)"
                and row["compiler_input_candidate"]["preparsed_input_branch"]
                == "pattern = None"
                and row["compiler_input_candidate"][
                    "code_generation_after_input_selection"]
                == "code = _code(p, flags)"
                and not row["compiler_input_candidate"][
                    "compiler_execution_observed"]
                for row in candidates
            ))
            self.assertTrue(all(not row["standard_re_flag_binding_observed"]
                                for row in candidates))

            with patch.object(SUBJECT, "RE_CONSTANTS_SOURCE_SHA256", "0" * 64):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        files, ("pkg", "re", "re._compiler", "re._constants",
                                "re._parser"),
                    ),
                    [],
                )

            changed_signature = dict(files)
            changed_signature["re/__init__.py"] = changed_signature[
                "re/__init__.py"
            ].replace(b"def compile(pattern, flags=0):",
                     b"def compile(pattern, flags=1):", 1)
            changed_signature_digest = hashlib.sha256(
                changed_signature["re/__init__.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_INIT_SOURCE_SHA256",
                              changed_signature_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        changed_signature,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered = dict(files)
            altered["re/_parser.py"] = altered["re/_parser.py"].replace(
                b"isinstance(string, str)", b"isinstance(string, bytes)",
            )
            altered_digest = hashlib.sha256(altered["re/_parser.py"]).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256", altered_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered, ("pkg", "re", "re._compiler", "re._constants",
                                  "re._parser"),
                    ),
                    [],
                )

            altered_verbose = dict(files)
            altered_verbose["re/_parser.py"] = altered_verbose[
                "re/_parser.py"
            ].replace(b"flags & SRE_FLAG_VERBOSE", b"flags & 0")
            altered_verbose_digest = hashlib.sha256(
                altered_verbose["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_verbose_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_verbose,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_whitespace = dict(files)
            altered_whitespace["re/_parser.py"] = altered_whitespace[
                "re/_parser.py"
            ].replace(b"WHITESPACE =", b"OTHERSPACE =", 1)
            altered_whitespace_digest = hashlib.sha256(
                altered_whitespace["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_whitespace_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_whitespace,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_verbose_comment = dict(files)
            altered_verbose_comment["re/_parser.py"] = altered_verbose_comment[
                "re/_parser.py"
            ].replace(b"this = sourceget()", b"this = otherget()", 1)
            altered_verbose_comment_digest = hashlib.sha256(
                altered_verbose_comment["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_verbose_comment_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_verbose_comment,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_tokenizer_encoding = dict(files)
            altered_tokenizer_encoding["re/_parser.py"] = altered_tokenizer_encoding[
                "re/_parser.py"
            ].replace(b"str(string, 'latin1')", b"str(string, 'utf8')")
            altered_tokenizer_encoding_digest = hashlib.sha256(
                altered_tokenizer_encoding["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_tokenizer_encoding_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_tokenizer_encoding,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_tokenizer_escape = dict(files)
            altered_tokenizer_escape["re/_parser.py"] = altered_tokenizer_escape[
                "re/_parser.py"
            ].replace(b"if char == '\\\\':", b"if char != '\\\\':", 1)
            altered_tokenizer_escape_digest = hashlib.sha256(
                altered_tokenizer_escape["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_tokenizer_escape_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_tokenizer_escape,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_sourceget = dict(files)
            altered_sourceget["re/_parser.py"] = altered_sourceget[
                "re/_parser.py"
            ].replace(b"sourceget = source.get", b"sourceget = source.match", 1)
            altered_sourceget_digest = hashlib.sha256(
                altered_sourceget["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_sourceget_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_sourceget,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_dispatch = dict(files)
            altered_dispatch["re/_parser.py"] = altered_dispatch[
                "re/_parser.py"
            ].replace(b"nested + 1", b"nested", 1)
            altered_dispatch_digest = hashlib.sha256(
                altered_dispatch["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_dispatch_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_dispatch,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_alternation = dict(files)
            altered_alternation["re/_parser.py"] = altered_alternation[
                "re/_parser.py"
            ].replace(b"sourcematch('|')", b"sourcematch('&')", 1)
            altered_alternation_digest = hashlib.sha256(
                altered_alternation["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_alternation_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_alternation,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_branch_shape = dict(files)
            altered_branch_shape["re/_parser.py"] = altered_branch_shape[
                "re/_parser.py"
            ].replace(b"(BRANCH, (None, items))", b"(LITERAL, (None, items))", 1)
            altered_branch_digest = hashlib.sha256(
                altered_branch_shape["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_branch_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_branch_shape,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_charset_kind = dict(files)
            altered_charset_kind["re/_parser.py"] = altered_charset_kind[
                "re/_parser.py"
            ].replace(b"elif op is IN", b"elif op is NOT_IN", 1)
            altered_charset_digest = hashlib.sha256(
                altered_charset_kind["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_charset_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_charset_kind,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_prefix = dict(files)
            altered_prefix["re/_parser.py"] = altered_prefix[
                "re/_parser.py"
            ].replace(b"item[0] != prefix", b"item[0] == prefix", 1)
            altered_prefix_digest = hashlib.sha256(
                altered_prefix["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_prefix_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_prefix,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            reordered_paths = dict(files)
            reordered_paths["re/_parser.py"] = reordered_paths[
                "re/_parser.py"
            ].replace(
                b"    set = []\n",
                b"    subpattern.append((BRANCH, (None, items)))\n    set = []\n",
                1,
            )
            reordered_paths_digest = hashlib.sha256(
                reordered_paths["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              reordered_paths_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        reordered_paths,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_uniq = dict(files)
            altered_uniq["re/_parser.py"] = altered_uniq[
                "re/_parser.py"
            ].replace(b"dict.fromkeys(items)", b"set(items)", 1)
            altered_uniq_digest = hashlib.sha256(
                altered_uniq["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_uniq_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_uniq,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_compiler_branch = dict(files)
            altered_compiler_branch["re/_compiler.py"] = altered_compiler_branch[
                "re/_compiler.py"
            ].replace(b"emit(FAILURE)", b"emit(SUCCESS)", 1)
            altered_compiler_branch_digest = hashlib.sha256(
                altered_compiler_branch["re/_compiler.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_COMPILER_SOURCE_SHA256",
                              altered_compiler_branch_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_compiler_branch,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_code_container = dict(files)
            altered_code_container["re/_compiler.py"] = altered_code_container[
                "re/_compiler.py"
            ].replace(b"code = []", b"code = ()", 1)
            altered_code_container_digest = hashlib.sha256(
                altered_code_container["re/_compiler.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_COMPILER_SOURCE_SHA256",
                              altered_code_container_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_code_container,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_group_map = dict(files)
            altered_group_map["re/_compiler.py"] = altered_group_map[
                "re/_compiler.py"
            ].replace(b"groupindex = p.state.groupdict",
                     b"groupindex = p.state.groups", 1)
            altered_group_map_digest = hashlib.sha256(
                altered_group_map["re/_compiler.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_COMPILER_SOURCE_SHA256",
                              altered_group_map_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_group_map,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_debug_disassembly = dict(files)
            altered_debug_disassembly["re/_compiler.py"] = altered_debug_disassembly[
                "re/_compiler.py"
            ].replace(b"dis(code)", b"dis(pattern)", 1)
            altered_debug_disassembly_digest = hashlib.sha256(
                altered_debug_disassembly["re/_compiler.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_COMPILER_SOURCE_SHA256",
                              altered_debug_disassembly_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_debug_disassembly,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_preparsed_input = dict(files)
            altered_preparsed_input["re/_compiler.py"] = altered_preparsed_input[
                "re/_compiler.py"
            ].replace(b"pattern = None", b"pattern = p", 1)
            altered_preparsed_input_digest = hashlib.sha256(
                altered_preparsed_input["re/_compiler.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_COMPILER_SOURCE_SHA256",
                              altered_preparsed_input_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_preparsed_input,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_group_state = dict(files)
            altered_group_state["re/_parser.py"] = altered_group_state[
                "re/_parser.py"
            ].replace(b"self.groupdict[name] = gid",
                     b"self.groupdict[name] = self.groups", 1)
            altered_group_state_digest = hashlib.sha256(
                altered_group_state["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_group_state_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_group_state,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_group_close = dict(files)
            altered_group_close["re/_parser.py"] = altered_group_close[
                "re/_parser.py"
            ].replace(b"self.groupwidths[gid] = p.getwidth()",
                     b"self.groupwidths[gid] = (0, 0)", 1)
            altered_group_close_digest = hashlib.sha256(
                altered_group_close["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_group_close_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_group_close,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_group_call = dict(files)
            altered_group_call["re/_parser.py"] = altered_group_call[
                "re/_parser.py"
            ].replace(b"state.closegroup(group, p)",
                     b"state.closegroup(group, group)", 1)
            altered_group_call_digest = hashlib.sha256(
                altered_group_call["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_group_call_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_group_call,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_forward_group_position = dict(files)
            altered_forward_group_position["re/_parser.py"] = (
                altered_forward_group_position["re/_parser.py"].replace(
                    b"source.tell() - len(condname) - 1", b"source.tell()", 1
                )
            )
            altered_forward_group_digest = hashlib.sha256(
                altered_forward_group_position["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_forward_group_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_forward_group_position,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_lookbehind_boundary = dict(files)
            altered_lookbehind_boundary["re/_parser.py"] = (
                altered_lookbehind_boundary["re/_parser.py"].replace(
                    b"gid >= self.lookbehindgroups",
                    b"gid > self.lookbehindgroups",
                    1,
                )
            )
            altered_lookbehind_digest = hashlib.sha256(
                altered_lookbehind_boundary["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_lookbehind_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_lookbehind_boundary,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

            altered_group_width = dict(files)
            altered_group_width["re/_parser.py"] = altered_group_width[
                "re/_parser.py"
            ].replace(b"i = min(i, l)", b"i = max(i, l)", 1)
            altered_group_width_digest = hashlib.sha256(
                altered_group_width["re/_parser.py"]
            ).hexdigest()
            with patch.object(SUBJECT, "RE_PARSER_SOURCE_SHA256",
                              altered_group_width_digest):
                self.assertEqual(
                    SUBJECT._target_re_compile_tokenizer_input_type_candidates(
                        altered_group_width,
                        ("pkg", "re", "re._compiler", "re._constants",
                         "re._parser"),
                    ),
                    [],
                )

    def test_functools_negative_cache_size_guard_requires_all_pinned_callers(self):
        lines = [""] * 565
        lines[481] = "def lru_cache(maxsize=128, typed=False):"
        lines[506] = "    if isinstance(maxsize, int):"
        lines[507] = "        pass"
        lines[508] = "        if maxsize < 0:"
        lines[509] = "            pass"
        lines[510] = "    elif callable(maxsize) and isinstance(typed, bool):"
        lines[511] = "        pass"
        lines[516] = "    elif maxsize is not None:"
        lines[517] = "        raise TypeError()"
        lines[527] = "def _lru_cache_wrapper(user_function, maxsize, typed, _CacheInfo):"
        lines[542] = "    if maxsize == 0:"
        lines[543] = "        pass"
        lines[551] = "    elif maxsize is None:"
        lines[552] = "        pass"
        source = ("\n".join(lines) + "\n").encode()
        client = (
            b"from functools import lru_cache\n"
            b"@lru_cache(maxsize=4)\n"
            b"def cached():\n    return None\n"
        )
        caller_digest = hashlib.sha256(json.dumps(
            [
                [["client.py", 2, "call", "lru_cache(maxsize=4)"]],
                [
                    ["client.py", hashlib.sha256(client).hexdigest()],
                    ["functools.py", hashlib.sha256(source).hexdigest()],
                ],
            ],
            separators=(",", ":"),
        ).encode()).hexdigest()
        expected = {
            ("functools", "functools.py", 507): (False, True),
            ("functools", "functools.py", 509): (False,),
            ("functools", "functools.py", 511): (False, True),
            ("functools", "functools.py", 517): (False,),
            ("functools", "functools.py", 543): (False,),
            ("functools", "functools.py", 552): (False, True),
        }
        with patch.multiple(
            SUBJECT,
            FUNCTOOLS_SOURCE_SHA256=hashlib.sha256(source).hexdigest(),
            FUNCTOOLS_LRU_CACHE_CALLS_SHA256=caller_digest,
        ):
            self.assertEqual(
                SUBJECT._target_functools_lru_cache_condition_facts(
                    {"functools.py": source, "client.py": client},
                ),
                expected,
            )
            unsafe = client.replace(b"maxsize=4", b"maxsize=-1")
            self.assertEqual(
                SUBJECT._target_functools_lru_cache_condition_facts(
                    {"functools.py": source, "client.py": unsafe},
                ),
                {},
            )
            zero_size = client.replace(b"maxsize=4", b"maxsize=0")
            self.assertEqual(
                SUBJECT._target_functools_lru_cache_condition_facts(
                    {"functools.py": source, "client.py": zero_size},
                ),
                {},
            )

    def test_logging_lock_guards_require_unmutated_truthy_lock_implementations(self):
        logging_lines = {
            232: "_lock = threading.RLock()",
            239: "def _acquireLock():",
            240: "    if _lock:",
            241: "        _lock.acquire()",
            246: "def _releaseLock():",
            247: "    if _lock:",
            248: "        _lock.release()",
        }
        threading_source = (
            b"def RLock(*args, **kwargs):\n"
            b"    if _CRLock is None:\n"
            b"        return _PyRLock(*args, **kwargs)\n"
            b"    return _CRLock(*args, **kwargs)\n"
            b"class _RLock:\n"
            b"    pass\n"
        )
        c_source = (
            b"static PyType_Slot rlock_type_slots[] = {\n"
            b"    {Py_tp_new, rlock_new},\n"
            b"    {Py_tp_methods, rlock_methods},\n"
            b"    {0, 0},\n"
            b"};\n"
        )

        def make_source(lines):
            content = [""] * max(lines)
            for number, statement in lines.items():
                content[number - 1] = statement
            return ("\n".join(content) + "\n").encode()

        files = {
            "logging/__init__.py": make_source(logging_lines),
            "threading.py": threading_source,
        }
        with patch.multiple(
            SUBJECT,
            LOGGING_SOURCE_SHA256=hashlib.sha256(
                files["logging/__init__.py"],
            ).hexdigest(),
            THREADING_SOURCE_SHA256=hashlib.sha256(threading_source).hexdigest(),
            THREAD_NATIVE_ID_MODULE_SHA256=hashlib.sha256(c_source).hexdigest(),
        ):
            self.assertEqual(
                SUBJECT._target_logging_lock_line_facts(files, c_source),
                {240: False, 247: False},
            )
            unsafe_files = dict(files)
            unsafe_files["extra.py"] = (
                b"import logging as log\nlog._lock = None\n"
            )
            self.assertEqual(
                SUBJECT._target_logging_lock_line_facts(unsafe_files, c_source),
                {},
            )
            unsafe_c_source = c_source.replace(
                b"{Py_tp_methods, rlock_methods}",
                b"{Py_nb_bool, custom_bool}",
            )
            with patch.object(
                SUBJECT, "THREAD_NATIVE_ID_MODULE_SHA256",
                hashlib.sha256(unsafe_c_source).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_logging_lock_line_facts(files, unsafe_c_source),
                    {},
                )

    def test_logging_level_guard_binds_all_import_time_callers(self):
        logging_lines = {
            1: "NOTSET = 0",
            2: "WARNING = 30",
            207: "def _checkLevel(level):",
            209: "    if isinstance(level, int):",
            210: "        return level",
            211: "    raise TypeError()",
            300: "class Handler:",
            934: "    def __init__(self, level=NOTSET):",
            935: "        _checkLevel(level)",
            985: "    def setLevel(self, level):",
            986: "        _checkLevel(level)",
            1000: "class StreamHandler(Handler):",
            1001: "    pass",
            1005: "class _StderrHandler(StreamHandler):",
            1010: "    def __init__(self, level):",
            1011: "        Handler.__init__(self, level)",
            1200: "class Manager:",
            1201: "    def __init__(self):",
            1202: "        self.disable = 0",
            1203: "        self.loggerClass = None",
            1250: "    def getLogger(self, name):",
            1251: "        return (self.loggerClass or _loggerClass)(name)",
            1365: "    @property",
            1366: "    def disable(self):",
            1367: "        return self._disable",
            1373: "    @disable.setter",
            1374: "    def disable(self, value):",
            1375: "        self._disable = _checkLevel(value)",
            1400: "class Logger:",
            1502: "    def __init__(self, name, level=NOTSET):",
            1503: "        _checkLevel(level)",
            1513: "    def setLevel(self, level):",
            1514: "        _checkLevel(level)",
            1520: "class RootLogger(Logger):",
            1521: "    def __init__(self, level):",
            1522: "        Logger.__init__(self, 'root', level)",
            1600: "_loggerClass = Logger",
            1601: "_defaultLastResort = _StderrHandler(WARNING)",
            2013: "root = RootLogger(WARNING)",
            2014: "Logger.root = root",
            2015: "Logger.manager = Manager(Logger.root)",
        }

        def make_source(lines):
            content = [""] * max(lines)
            for number, statement in lines.items():
                content[number - 1] = statement
            return ("\n".join(content) + "\n").encode()

        def caller(path, line, call):
            lines = [""] * line
            lines[0] = "import logging"
            lines[line - 1] = call
            return make_source({index + 1: value for index, value in enumerate(lines)})

        files = {
            "logging/__init__.py": make_source(logging_lines),
            "asyncio/log.py": caller(
                "asyncio/log.py", 7, "logging.getLogger(__package__)",
            ),
            "concurrent/futures/_base.py": caller(
                "concurrent/futures/_base.py", 43,
                "logging.getLogger('concurrent.futures')",
            ),
            "venv/__init__.py": caller(
                "venv/__init__.py", 18, "logging.getLogger(__name__)",
            ),
        }
        for source_path, source_bytes in files.items():
            try:
                ast.parse(source_bytes, filename=source_path)
            except SyntaxError as error:
                self.fail(f"invalid synthetic source {source_path}: {error}")
        module_calls = [
            ["asyncio/log.py", 7, "logging.getLogger(__package__)"] ,
            ["concurrent/futures/_base.py", 43,
             "logging.getLogger('concurrent.futures')"],
            ["venv/__init__.py", 18, "logging.getLogger(__name__)"] ,
        ]
        source_rows = [
            [path, hashlib.sha256(files[path]).hexdigest()]
            for path in sorted(files) if path != "logging/__init__.py"
        ]
        call_digest = hashlib.sha256(json.dumps(
            [module_calls, source_rows], separators=(",", ":"),
        ).encode()).hexdigest()
        with patch.multiple(
            SUBJECT,
            LOGGING_SOURCE_SHA256=hashlib.sha256(
                files["logging/__init__.py"],
            ).hexdigest(),
            LOGGING_LEVEL_CALLS_SHA256=call_digest,
        ):
            self.assertEqual(
                SUBJECT._target_logging_level_line_facts(files),
                {209: True},
            )
        unsafe_files = dict(files)
        unsafe_files["logging_mutator.py"] = (
            b"import logging\nlogging.setLevel(30)\n"
        )
        with patch.multiple(
            SUBJECT,
            LOGGING_SOURCE_SHA256=hashlib.sha256(
                files["logging/__init__.py"],
            ).hexdigest(),
            LOGGING_LEVEL_CALLS_SHA256=call_digest,
        ):
            self.assertEqual(
                SUBJECT._target_logging_level_line_facts(unsafe_files),
                {},
            )

    def test_threading_condition_lock_guard_tracks_main_thread_event(self):
        lines = {
            1: "import _thread",
            37: "_allocate_lock = _thread.allocate_lock",
            122: "Lock = _allocate_lock",
            250: "class Condition:",
            277: "    def __init__(self, lock=None):",
            278: "        if lock is None:",
            279: "            lock = RLock()",
            287: "        if hasattr(lock, '_release_save'):",
            288: "            pass",
            289: "        if hasattr(lock, '_acquire_restore'):",
            290: "            pass",
            291: "        if hasattr(lock, '_is_owned'):",
            292: "            pass",
            300: "class Event:",
            588: "    def __init__(self):",
            589: "        self._cond = Condition(Lock())",
            900: "class Thread:",
            901: "    def __init__(self, name=None, daemon=None):",
            910: "        if name:",
            911: "            pass",
            925: "        if daemon is not None:",
            926: "            if daemon and (not _daemon_threads_allowed()):",
            927: "                pass",
             928: "            self._daemonic = daemon",
            935: "        self._started = Event()",
             940: "        self._invoke_excepthook = _make_invoke_excepthook()",
             1052: "    def _set_tstate_lock(self):",
             1053: "        if not self.daemon:",
             1054: "            pass",
             1080: "    @property",
             1081: "    def daemon(self):",
             1082: "        return self._daemonic",
             1300: "try:",
             1301: "    from _thread import _excepthook as excepthook",
             1302: "except ImportError:",
             1303: "    def excepthook(args):",
             1304: "        pass",
             1356: "def _make_invoke_excepthook():",
             1361: "    old_excepthook = excepthook",
             1362: "    old_sys_excepthook = _sys.excepthook",
             1363: "    if old_excepthook is None:",
             1364: "        raise RuntimeError('threading.excepthook is None')",
             1365: "    if old_sys_excepthook is None:",
             1366: "        raise RuntimeError('sys.excepthook is None')",
             1404: "    return invoke_excepthook",
             1439: "class _MainThread(Thread):",
             1441: "    def __init__(self):",
             1442: "        Thread.__init__(self, name='MainThread', daemon=False)",
             1443: "        self._set_tstate_lock()",
             1470: "_main_thread = _MainThread()",
        }
        content = [""] * max(lines)
        for number, statement in lines.items():
            content[number - 1] = statement
        source = ("\n".join(content) + "\n").encode()
        module_source = b"""\
static PyObject *
thread_PyThread_allocate_lock(PyObject *module, PyObject *ignored)
{
    return (PyObject *) newlockobject(module);
}
static PyMethodDef thread_methods[] = {
    {"_excepthook", thread_excepthook,
    {"allocate_lock", thread_PyThread_allocate_lock,
};
static PyMethodDef lock_methods[] = {
    {"acquire", acquire},
    {"release", release},
    {NULL, NULL}
};
static PyMemberDef lock_type_members[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(lockobject, weaklist), READONLY},
    {NULL,}
};
static PyType_Slot lock_type_slots[] = {
    {Py_tp_methods, lock_methods},
    {0, 0}
};
static PyType_Spec lock_type_spec = {
    .name = "_thread.lock",
    .slots = lock_type_slots,
};
static lockobject *
newlockobject(PyObject *module)
{
    lockobject *self = allocate();
    if (self == NULL) {
        return NULL;
    }
    self->lock_lock = PyThread_allocate_lock();
    if (self->lock_lock == NULL) {
        PyErr_SetString(ThreadError, "can't allocate lock");
        return NULL;
    }
    return self;
}
"""
        files = {"threading.py": source}
        with patch.multiple(
            SUBJECT,
            THREADING_SOURCE_SHA256=hashlib.sha256(source).hexdigest(),
            THREAD_NATIVE_ID_MODULE_SHA256=hashlib.sha256(module_source).hexdigest(),
        ), patch.object(
            SUBJECT, "_TARGET_BUILTIN_MEMBERSHIP",
            {**SUBJECT._TARGET_BUILTIN_MEMBERSHIP, "_thread": True},
        ):
            self.assertEqual(
                SUBJECT._target_threading_condition_lock_line_facts(
                    files, module_source,
                ),
                {278: False, 287: False, 289: False, 291: False,
                 1053: True, 1363: False},
            )
            mutated = source.replace(b"Condition(Lock())", b"Condition()")
            mutated_files = {"threading.py": mutated}
            with patch.object(
                SUBJECT, "THREADING_SOURCE_SHA256",
                hashlib.sha256(mutated).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_threading_condition_lock_line_facts(
                        mutated_files, module_source,
                    ),
                    {},
                )

            hook_mutated = source.replace(
                b"class _MainThread(Thread):",
                b"excepthook = None\nclass _MainThread(Thread):",
            )
            with patch.object(
                SUBJECT, "THREADING_SOURCE_SHA256",
                hashlib.sha256(hook_mutated).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_threading_condition_lock_line_facts(
                        {"threading.py": hook_mutated}, module_source,
                    ),
                    {},
                )

            missing_native_hook = module_source.replace(
                b'{"_excepthook", thread_excepthook,',
                b'{"_missing_hook", thread_excepthook,',
            )
            with patch.object(
                SUBJECT, "THREAD_NATIVE_ID_MODULE_SHA256",
                hashlib.sha256(missing_native_hook).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_threading_condition_lock_line_facts(
                        files, missing_native_hook,
                    ),
                    {},
                )

            unsafe_files = dict(files)
            unsafe_files["client.py"] = (
                b"import threading\nthreading.Thread()\n"
            )
            self.assertEqual(
                SUBJECT._target_threading_condition_lock_line_facts(
                    unsafe_files, module_source,
                ),
                {},
            )
            unsafe_files["client.py"] = (
                b"import threading\n"
                b"def create(thread=threading.Thread()):\n"
                b"    return thread\n"
            )
            self.assertEqual(
                SUBJECT._target_threading_condition_lock_line_facts(
                    unsafe_files, module_source,
                ),
                {},
            )
            unsafe_files["client.py"] = (
                b"from threading import *\nThread()\n"
            )
            self.assertEqual(
                SUBJECT._target_threading_condition_lock_line_facts(
                    unsafe_files, module_source,
                ),
                {},
            )

    def test_threading_sys_excepthook_guard_is_bound_to_builtin_sys_method(self):
        lines = [""] * 1366
        lines[1359] = "def _make_invoke_excepthook():"
        lines[1361] = "    old_sys_excepthook = _sys.excepthook"
        lines[1364] = "    if old_sys_excepthook is None:"
        lines[1365] = "        raise RuntimeError('sys.excepthook is None')"
        threading_source = ("\n".join(lines) + "\n").encode()
        sys_module_source = b"""\
static PyMethodDef sys_methods[] = {
    SYS_EXCEPTHOOK_METHODDEF
};
static struct PyModuleDef sysmodule = {
    PyModuleDef_HEAD_INIT,
    "sys",
    sys_doc,
    -1,
    sys_methods,
};
"""
        clinic_source = b"""\
#define SYS_EXCEPTHOOK_METHODDEF \\
    {"excepthook", _PyCFunction_CAST(sys_excepthook), METH_FASTCALL},
"""
        files = {"threading.py": threading_source}
        with patch.multiple(
            SUBJECT,
            THREADING_SOURCE_SHA256=hashlib.sha256(threading_source).hexdigest(),
            SYS_MODULE_C_SHA256=hashlib.sha256(sys_module_source).hexdigest(),
            SYS_MODULE_CLINIC_SHA256=hashlib.sha256(clinic_source).hexdigest(),
        ), patch.object(
            SUBJECT, "_TARGET_BUILTIN_MEMBERSHIP",
            {**SUBJECT._TARGET_BUILTIN_MEMBERSHIP, "sys": True},
        ):
            args = (files, ("threading",), {1363: False},
                    sys_module_source, clinic_source)
            self.assertEqual(
                SUBJECT._target_threading_sys_excepthook_line_facts(*args),
                {1365: False},
            )
            self.assertEqual(
                SUBJECT._target_threading_sys_excepthook_line_facts(
                    files, (), {1363: False}, sys_module_source, clinic_source,
                ),
                {},
            )
            changed_clinic = clinic_source.replace(b'"excepthook"', b'"otherhook"')
            with patch.object(
                SUBJECT, "SYS_MODULE_CLINIC_SHA256",
                hashlib.sha256(changed_clinic).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_threading_sys_excepthook_line_facts(
                        files, ("threading",), {1363: False},
                        sys_module_source, changed_clinic,
                    ),
                    {},
                )
            mutating_files = {
                **files,
                "mutator.py": b"import sys\nsys.excepthook = None\n",
            }
            self.assertEqual(
                SUBJECT._target_threading_sys_excepthook_line_facts(
                    mutating_files, ("threading", "mutator"), {1363: False},
                    sys_module_source, clinic_source,
                ),
                {},
            )
            dynamic_files = {
                **files,
                "mutator.py": b"import sys\nsetattr(sys, 'excepthook', None)\n",
            }
            self.assertEqual(
                SUBJECT._target_threading_sys_excepthook_line_facts(
                    dynamic_files, ("threading", "mutator"), {1363: False},
                    sys_module_source, clinic_source,
                ),
                {},
            )
            aliased_files = {
                **files,
                "mutator.py": b"import sys as runtime\n"
                              b"hook_owner = runtime\n"
                              b"setattr(hook_owner, 'excepthook', None)\n",
            }
            self.assertEqual(
                SUBJECT._target_threading_sys_excepthook_line_facts(
                    aliased_files, ("threading", "mutator"), {1363: False},
                    sys_module_source, clinic_source,
                ),
                {},
            )
            dict_files = {
                **files,
                "mutator.py": b"import sys as runtime\n"
                              b"runtime.__dict__['excepthook'] = None\n",
            }
            self.assertEqual(
                SUBJECT._target_threading_sys_excepthook_line_facts(
                    dict_files, ("threading", "mutator"), {1363: False},
                    sys_module_source, clinic_source,
                ),
                {},
            )

    def test_namedtuple_rename_guard_requires_all_production_calls_to_omit_it(self):
        collections_source = (
            b"def namedtuple(typename, field_names, *, rename=False, "
            b"defaults=None, module=None):\n"
            b"    if rename:\n"
            b"        pass\n"
        )
        files = {
            "collections/__init__.py": collections_source,
            "caller.py": (
                b"from collections import namedtuple as nt\n"
                b"import collections as c\n"
                b"nt('Point', 'x y')\n"
                b"c.namedtuple('Pair', ('left', 'right'))\n"
            ),
        }
        with patch.object(
            SUBJECT, "COLLECTIONS_SOURCE_SHA256",
            hashlib.sha256(collections_source).hexdigest(),
        ):
            self.assertEqual(
                SUBJECT._target_collections_namedtuple_rename_line_facts(files),
                {2: False},
            )
            unsafe_files = dict(files)
            unsafe_files["caller.py"] += b"nt('Bad', 'x', rename=True)\n"
            self.assertEqual(
                SUBJECT._target_collections_namedtuple_rename_line_facts(
                    unsafe_files,
                ),
                {},
            )

    def test_namedtuple_type_guard_follows_string_normalization(self):
        collections_source = (
            b"def namedtuple(typename, field_names):\n"
            b"    typename = _sys.intern(str(typename))\n"
            b"    field_names = list(map(str, field_names))\n"
            b"    for name in [typename] + field_names:\n"
            b"        if type(name) is not str:\n"
            b"            raise TypeError()\n"
        )
        files = {"collections/__init__.py": collections_source}
        with patch.object(
            SUBJECT, "COLLECTIONS_SOURCE_SHA256",
            hashlib.sha256(collections_source).hexdigest(),
        ):
            self.assertEqual(
                SUBJECT._target_collections_namedtuple_string_type_line_facts(
                    files,
                ),
                {5: False},
            )
            mutated_source = collections_source.replace(
                b"list(map(str, field_names))",
                b"list(map(bytes, field_names))",
            )
            with patch.object(
                SUBJECT, "COLLECTIONS_SOURCE_SHA256",
                hashlib.sha256(mutated_source).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_collections_namedtuple_string_type_line_facts(
                        {"collections/__init__.py": mutated_source},
                    ),
                    {},
                )

    def test_namedtuple_module_guard_uses_pinned_cpython_fallback(self):
        collections_source = (
            b"import sys as _sys\n"
            b"def namedtuple(module=None):\n"
            b"    if module is None:\n"
            b"        try:\n"
            b"            module = _sys._getframemodulename(1) or '__main__'\n"
            b"        except AttributeError:\n"
            b"            try:\n"
            b"                module = _sys._getframe(1).f_globals.get('__name__', '__main__')\n"
            b"            except (AttributeError, ValueError):\n"
            b"                pass\n"
            b"    if module is not None:\n"
            b"        pass\n"
        )
        sys_source = (
            b'#include "clinic/sysmodule.c.h"\n'
            b"static PyMethodDef sys_methods[] = {\n"
            b"    SYS__GETFRAMEMODULENAME_METHODDEF\n};\n"
            b"static struct PyModuleDef sysmodule = {\n    sys_methods,\n};\n"
            b"static PyObject *sys__getframemodulename_impl(void) {\n"
            b"    PyObject *r = PyFunction_GetModule(frame);\n"
            b"    Py_RETURN_NONE;\n}\n"
        )
        clinic_source = (
            b"#define SYS__GETFRAMEMODULENAME_METHODDEF    \\\n"
            b'    {"_getframemodulename", sys__getframemodulename},\n'
        )
        files = {"collections/__init__.py": collections_source}
        with patch.object(
            SUBJECT, "COLLECTIONS_SOURCE_SHA256",
            hashlib.sha256(collections_source).hexdigest(),
        ), patch.object(
            SUBJECT, "SYS_MODULE_C_SHA256",
            hashlib.sha256(sys_source).hexdigest(),
        ), patch.object(
            SUBJECT, "SYS_MODULE_CLINIC_SHA256",
            hashlib.sha256(clinic_source).hexdigest(),
        ), patch.dict(SUBJECT._TARGET_BUILTIN_MEMBERSHIP, {"sys": True}):
            self.assertEqual(
                SUBJECT._target_collections_namedtuple_module_line_facts(
                    files, sys_source, clinic_source,
                ),
                {11: True},
            )
            unsafe_files = {
                **files,
                "extra.py": b"import sys\nsys._getframemodulename = None\n",
            }
            self.assertEqual(
                SUBJECT._target_collections_namedtuple_module_line_facts(
                    unsafe_files, sys_source, clinic_source,
                ),
                {},
            )
            mutated_collections = collections_source.replace(
                b" or '__main__'", b"",
            )
            with patch.object(
                SUBJECT, "COLLECTIONS_SOURCE_SHA256",
                hashlib.sha256(mutated_collections).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_collections_namedtuple_module_line_facts(
                        {"collections/__init__.py": mutated_collections},
                        sys_source, clinic_source,
                    ),
                    {},
                )
            no_method_source = sys_source.replace(
                b"SYS__GETFRAMEMODULENAME_METHODDEF", b"UNKNOWN_METHODDEF",
            )
            with patch.object(
                SUBJECT, "SYS_MODULE_C_SHA256",
                hashlib.sha256(no_method_source).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_collections_namedtuple_module_line_facts(
                        files, no_method_source, clinic_source,
                    ),
                    {},
                )

    def test_namedtuple_conditions_bind_complete_call_domain(self):
        collections_source = (
            b"def namedtuple(typename, field_names, *, rename=False, defaults=None, module=None):\n"
            b"    if isinstance(field_names, str):\n"
            b"        field_names = field_names.replace(',', ' ').split()\n"
            b"    if defaults is not None:\n"
            b"        defaults = tuple(defaults)\n"
            b"        if len(defaults) > len(field_names):\n            pass\n"
            b"    if defaults is not None:\n        pass\n"
            b"    if module is None:\n        pass\n"
            b"    if not name.isidentifier():\n        pass\n"
            b"    if _iskeyword(name):\n        pass\n"
            b"    if name.startswith('_') and not rename:\n        pass\n"
            b"    if name in seen:\n        pass\n"
            b"    field_names = tuple(map(_sys.intern, field_names))\n"
            b"    num_fields = len(field_names)\n"
            b"    if num_fields == 1:\n        pass\n"
            b"    class_namespace = {'_fields': field_names}\n"
            b"    return type(typename, (), class_namespace)\n"
            b"from keyword import iskeyword as _iskeyword\n"
        )
        inspect_source = (
            b"from collections import namedtuple\n"
            b"_Traceback = namedtuple('_Traceback', 'filename lineno function code_context index')\n"
            b"class Traceback(_Traceback):\n    pass\n"
            b"_FrameInfo = namedtuple('_FrameInfo', ('frame',) + Traceback._fields)\n"
        )
        caller_source = (
            b"from collections import namedtuple\n"
            b"namedtuple('A', 'x y')\n"
            b"namedtuple('B', ('x', 'y'))\n"
            b"namedtuple('C', ('x',), defaults=[None])\n"
            b"namedtuple('D', ('x',), module='sample')\n"
        )
        typing_source = (
            b"import collections\n"
            b"def _make_nmtuple(name, types, module, defaults=()):\n"
            b"    fields = [n for n, t in types]\n"
            b"    result = collections.namedtuple(name, fields, defaults=defaults, module=module)\n"
        )
        keyword_source = (
            b"kwlist = ['False', 'None', 'True', 'and', 'as', 'async']\n"
            b"iskeyword = frozenset(kwlist).__contains__\n"
        )
        files = {
            "collections/__init__.py": collections_source,
            "inspect.py": inspect_source,
            "caller.py": caller_source,
            "typing.py": typing_source,
            "keyword.py": keyword_source,
        }
        caller_rows = []
        source_rows = []
        for path, content in files.items():
            tree = ast.parse(content, filename=path)
            aliases = {
                alias.asname or alias.name
                for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                and node.module == "collections" for alias in node.names
                if alias.name == "namedtuple"
            }
            module_aliases = {
                alias.asname or alias.name.split(".")[0]
                for node in ast.walk(tree) if isinstance(node, ast.Import)
                for alias in node.names if alias.name == "collections"
            }
            if aliases or module_aliases:
                source_rows.append([path, hashlib.sha256(content).hexdigest()])
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                is_alias_call = (isinstance(node.func, ast.Name)
                                 and node.func.id in aliases)
                is_module_call = (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "namedtuple"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id in module_aliases
                )
                if is_alias_call or is_module_call:
                    caller_rows.append([path, node.lineno, ast.unparse(node)])
        caller_rows.sort()
        source_rows.sort()

        def caller_digest(source_bytes, added_rows):
            call_rows = caller_rows + added_rows
            call_rows.sort()
            changed_source_rows = [
                row for row in source_rows if row[0] != "caller.py"
            ] + [["caller.py", hashlib.sha256(source_bytes).hexdigest()]]
            changed_source_rows.sort()
            return hashlib.sha256(json.dumps(
                [call_rows, changed_source_rows], separators=(",", ":"),
            ).encode()).hexdigest()

        digest = hashlib.sha256(json.dumps(
            [caller_rows, source_rows], separators=(",", ":"),
        ).encode()).hexdigest()
        with patch.object(
            SUBJECT, "COLLECTIONS_SOURCE_SHA256",
            hashlib.sha256(collections_source).hexdigest(),
        ), patch.object(
            SUBJECT, "INSPECT_SOURCE_SHA256",
            hashlib.sha256(inspect_source).hexdigest(),
        ), patch.object(
            SUBJECT, "TYPING_SOURCE_SHA256",
            hashlib.sha256(typing_source).hexdigest(),
        ), patch.object(
            SUBJECT, "KEYWORD_SOURCE_SHA256",
            hashlib.sha256(keyword_source).hexdigest(),
        ), patch.object(
            SUBJECT, "COLLECTIONS_NAMEDTUPLE_CALLS_SHA256", digest,
        ):
            self.assertEqual(
                (facts := SUBJECT._target_collections_namedtuple_call_condition_facts(
                    files,
                )),
                {
                    ("collections", "collections/__init__.py", 2): (False, True),
                    ("collections", "collections/__init__.py", 4): (False, True),
                    ("collections", "collections/__init__.py", 8): (False, True),
                    ("collections", "collections/__init__.py", 10): (False, True),
                    ("collections", "collections/__init__.py", 12): (False,),
                    ("collections", "collections/__init__.py", 14): (False,),
                    ("collections", "collections/__init__.py", 16): (False,),
                    ("collections", "collections/__init__.py", 18): (False,),
                    ("collections", "collections/__init__.py", 6): (False,),
                    ("collections", "collections/__init__.py", 22): (False, True),
                },
            )
            resolved = []
            unknown = []
            SUBJECT._module_init_call_candidate_closure(
                files, roots=("caller",),
                trusted_condition_observations=facts,
                resolved_conditions=resolved, unknown_conditions=unknown,
            )
            self.assertEqual(
                [row["decisions"] for row in resolved
                 if row["module"] == "collections" and row["line"] == 2],
                [[False, True]],
            )
            self.assertFalse(any(
                row["module"] == "collections" and row["line"] == 2
                for row in unknown
            ))
            for line in (4, 8, 10):
                self.assertEqual(
                    [row["decisions"] for row in resolved
                     if row["module"] == "collections" and row["line"] == line],
                    [[False, True]],
                )
            self.assertEqual(
                [row["decisions"] for row in resolved
                 if row["module"] == "collections" and row["line"] == 12],
                [[False]],
            )
            for line in (12, 14, 16, 18, 6):
                self.assertEqual(
                    [row["decisions"] for row in resolved
                     if row["module"] == "collections" and row["line"] == line],
                    [[False]],
                )
            self.assertEqual(
                [row["decisions"] for row in resolved
                 if row["module"] == "collections" and row["line"] == 22],
                [[False, True]],
            )
            unsafe_files = dict(files)
            unsafe_files["caller.py"] = caller_source.replace(
                b"('x', 'y')", b"unknown_fields",
            )
            self.assertEqual(
                SUBJECT._target_collections_namedtuple_call_condition_facts(
                    unsafe_files,
                ),
                {},
            )
            unsafe_defaults = dict(files)
            unsafe_defaults["caller.py"] = caller_source.replace(
                b"defaults=[None]", b"defaults=dynamic_defaults",
            )
            self.assertEqual(
                SUBJECT._target_collections_namedtuple_call_condition_facts(
                    unsafe_defaults,
                ),
                {},
            )
            too_many_defaults_source = (
                caller_source
                + b"namedtuple('TooMany', 'x', defaults=[None, None])\n"
            )
            too_many_defaults_files = dict(files)
            too_many_defaults_files["caller.py"] = too_many_defaults_source
            too_many_defaults_digest = caller_digest(
                too_many_defaults_source,
                [["caller.py", 6,
                  "namedtuple('TooMany', 'x', defaults=[None, None])"]],
            )
            with patch.object(
                SUBJECT, "COLLECTIONS_NAMEDTUPLE_CALLS_SHA256",
                too_many_defaults_digest,
            ):
                self.assertEqual(
                    SUBJECT._target_collections_namedtuple_call_condition_facts(
                        too_many_defaults_files,
                    ),
                    {},
                )
            starred_defaults_call = (
                "namedtuple('Star', 'x', defaults=[*unknown_defaults])"
            )
            starred_defaults_source = (
                caller_source + f"{starred_defaults_call}\n".encode()
            )
            starred_defaults_files = dict(files)
            starred_defaults_files["caller.py"] = starred_defaults_source
            starred_defaults_digest = caller_digest(
                starred_defaults_source,
                [["caller.py", 6, starred_defaults_call]],
            )
            with patch.object(
                SUBJECT, "COLLECTIONS_NAMEDTUPLE_CALLS_SHA256",
                starred_defaults_digest,
            ):
                self.assertEqual(
                    SUBJECT._target_collections_namedtuple_call_condition_facts(
                        starred_defaults_files,
                    ),
                    {},
                )
            for before, after in (
                    (b"defaults = tuple(defaults)",
                     b"defaults = list(defaults)"),
                    (b"num_fields = len(field_names)",
                     b"num_fields = len(field_names) - 1")):
                changed_collections_source = collections_source.replace(
                    before, after,
                )
                changed_shape_files = dict(files)
                changed_shape_files[
                    "collections/__init__.py"
                ] = changed_collections_source
                with patch.object(
                    SUBJECT, "COLLECTIONS_SOURCE_SHA256",
                    hashlib.sha256(changed_collections_source).hexdigest(),
                ):
                    self.assertEqual(
                        SUBJECT._target_collections_namedtuple_call_condition_facts(
                            changed_shape_files,
                        ),
                        {},
                    )
            invalid_identifier_source = (
                caller_source + b"namedtuple('Bad-Type', 'field')\n"
            )
            invalid_identifier_files = dict(files)
            invalid_identifier_files["caller.py"] = invalid_identifier_source
            invalid_digest = caller_digest(
                invalid_identifier_source,
                [["caller.py", 6, "namedtuple('Bad-Type', 'field')"]],
            )
            with patch.object(
                SUBJECT, "COLLECTIONS_NAMEDTUPLE_CALLS_SHA256", invalid_digest,
            ):
                self.assertEqual(
                    SUBJECT._target_collections_namedtuple_call_condition_facts(
                        invalid_identifier_files,
                    ),
                    {},
                )
            for invalid_field, expression in (
                    ("_field", "namedtuple('Bad', '_field')"),
                    ("x x", "namedtuple('Dup', 'x x')")):
                invalid_field_source = (
                    caller_source + f"{expression}\n".encode()
                )
                invalid_field_files = dict(files)
                invalid_field_files["caller.py"] = invalid_field_source
                invalid_field_digest = caller_digest(
                    invalid_field_source,
                    [["caller.py", 6, expression]],
                )
                with patch.object(
                    SUBJECT, "COLLECTIONS_NAMEDTUPLE_CALLS_SHA256",
                    invalid_field_digest,
                ):
                    self.assertEqual(
                        SUBJECT._target_collections_namedtuple_call_condition_facts(
                            invalid_field_files,
                        ),
                        {},
                    )
            keyword_mutation = keyword_source.replace(
                b"'async'", b"'async', 'x'",
            )
            keyword_mutated_files = dict(files)
            keyword_mutated_files["keyword.py"] = keyword_mutation
            with patch.object(
                SUBJECT, "KEYWORD_SOURCE_SHA256",
                hashlib.sha256(keyword_mutation).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_collections_namedtuple_call_condition_facts(
                        keyword_mutated_files,
                    ),
                    {},
                )

    def test_target_imported_name_fact_does_not_override_function_parameter(self):
        files = {
            "entry.py": (
                b"def check(__name__):\n"
                b"    if __name__ == '__main__':\n"
                b"        import function_local_branch\n"
                b"check('synthetic')\n"
            ),
            "function_local_branch.py": b"VALUE = 1\n",
        }
        target = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",),
            known_name_facts={
                "entry": {"__name__": SUBJECT._IMPORTED_MODULE_NAME},
            },
        )
        self.assertIn("function_local_branch", target[0])
        self.assertGreaterEqual(target[4]["unknown"], 1)

    def test_target_name_fact_does_not_prune_nested_function_definition(self):
        files = {
            "entry.py": (
                b"def check(__name__):\n"
                b"    if __name__ == '__main__':\n"
                b"        def inner():\n"
                b"            import nested_function_branch\n"
                b"        inner()\n"
                b"check('synthetic')\n"
            ),
            "nested_function_branch.py": b"VALUE = 1\n",
        }
        target = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",),
            known_name_facts={
                "entry": {"__name__": SUBJECT._IMPORTED_MODULE_NAME},
            },
        )
        self.assertIn("nested_function_branch", target[0])

    def test_target_imported_module_name_survives_star_export_fact(self):
        files = {
            "entry.py": (
                b"from export import *\n"
                b"if __name__ == '__main__':\n    import script_only\n"
            ),
            "export.py": b"__all__ = ['VALUE']\nVALUE = 1\n",
            "script_only.py": b"VALUE = 2\n",
        }
        baseline = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",)
        )
        target = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",),
            known_name_facts={
                "entry": {"__name__": SUBJECT._IMPORTED_MODULE_NAME},
            },
        )
        self.assertIn("script_only", baseline[0])
        self.assertEqual(target[0], ("entry", "export"))
        self.assertEqual(target[4], {"resolved": 1, "unknown": 0})

    def test_target_module_init_call_scan_uses_only_bound_guard_facts(self):
        files = {
            "entry.py": (
                b"def selected_branch():\n    return True\n"
                b"if selected_branch():\n    import windows_branch\n"
                b"else:\n    import linux_branch\n"
            ),
            "windows_branch.py": b"VALUE = 'windows'\n",
            "linux_branch.py": b"VALUE = 'linux'\n",
        }
        baseline = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",)
        )
        unknown = []
        target = SUBJECT._module_init_call_candidate_closure(
            files, roots=("entry",),
            known_call_facts=(("selected_branch()", False),),
            unknown_conditions=unknown,
        )
        self.assertIn("windows_branch", baseline[0])
        self.assertIn("linux_branch", baseline[0])
        self.assertEqual(target[0], ("entry", "linux_branch"))
        self.assertEqual(target[4], {"resolved": 1, "unknown": 0})
        self.assertEqual(unknown, [])

    def test_module_source_rows_bind_name_path_and_bytes_in_stable_order(self):
        files = {
            "pkg/__init__.py": b"from . import child\n",
            "pkg/child.py": b"VALUE = 1\n",
        }
        modules = ("pkg", "pkg.child")
        rows = SUBJECT._module_source_rows(files, modules)
        self.assertEqual(rows, [
            {"module": "pkg", "source_path": "pkg/__init__.py",
             "source_sha256": hashlib.sha256(files["pkg/__init__.py"]).hexdigest()},
            {"module": "pkg.child", "source_path": "pkg/child.py",
             "source_sha256": hashlib.sha256(files["pkg/child.py"]).hexdigest()},
        ])
        self.assertEqual(SUBJECT._module_source_rows(files, modules), rows)

    def test_module_source_rows_reject_missing_or_unordered_candidates(self):
        files = {"pkg.py": b"VALUE = 1\n"}
        with self.assertRaisesRegex(ValueError, "CANDIDATE_SOURCE_MISSING"):
            SUBJECT._module_source_rows(files, ("pkg", "pkg.child"))
        with self.assertRaisesRegex(ValueError, "CANDIDATE_MODULES"):
            SUBJECT._module_source_rows(files, ("zeta", "alpha"))
        with self.assertRaisesRegex(ValueError, "CANDIDATE_MODULES"):
            SUBJECT._module_source_rows(files, ("pkg", "pkg"))
        with self.assertRaisesRegex(ValueError, "CANDIDATE_MODULES"):
            SUBJECT._module_source_rows(files, ("pkg", 1))
        with self.assertRaisesRegex(ValueError, "CANDIDATE_MODULES"):
            SUBJECT._module_source_rows(files, ("../outside",))

    def test_roots_are_derived_from_bound_bootstrap_and_profile_sources(self):
        tools = Path(__file__).resolve().parents[1] / "Tools"
        builder_path = tools / "dgn007_control_bootstrap_source.py"
        builder_spec = importlib.util.spec_from_file_location("dgn007_control_bootstrap_source", builder_path)
        builder = importlib.util.module_from_spec(builder_spec)
        builder_spec.loader.exec_module(builder)
        generated = builder.build_compressed_inline_session_end_control_bootstrap(
            b"synthetic profile bytes",
            logical_profile="/tmp/dgn007-profile.json",
            expected_soabi="cpython-312-x86_64-linux-gnu",
            expected_destshared="/usr/local/lib/python3.12/lib-dynload",
        )
        profile_tree = ast.parse((tools / "dgn007_import_runtime_profile.py").read_text(encoding="utf-8"))

        def direct_roots(tree):
            roots = set()
            for statement in tree.body:
                if isinstance(statement, ast.Import):
                    roots.update(alias.name for alias in statement.names)
                elif isinstance(statement, ast.ImportFrom):
                    self.assertEqual(statement.level, 0)
                    roots.add(statement.module)
            return roots

        bootstrap_roots = direct_roots(ast.parse(generated.source))
        profile_roots = direct_roots(profile_tree)
        self.assertEqual(len(bootstrap_roots), 6)
        self.assertEqual(len(profile_roots), 8)
        self.assertEqual(set(SUBJECT.ROOTS), bootstrap_roots | profile_roots)

    def test_unpinned_archive_is_rejected_before_tar_read(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.tar.xz"
            path.write_bytes(b"not the pinned CPython archive")
            with patch.object(SUBJECT.tarfile, "open") as tar_open:
                with self.assertRaisesRegex(ValueError, "SOURCE_ARCHIVE_MISMATCH"):
                    SUBJECT._source_files(path)
                tar_open.assert_not_called()

    def test_path_replacement_after_hash_cannot_change_parsed_bytes(self):
        first = b"VALUE = 'verified'\n"
        replacement = b"VALUE = 'replaced'\n"

        def archive(body):
            buffer = io.BytesIO()
            with SUBJECT.tarfile.open(fileobj=buffer, mode="w:xz") as output:
                info = SUBJECT.tarfile.TarInfo("Python-3.12.16/Lib/pkg.py")
                info.size = len(body)
                output.addfile(info, io.BytesIO(body))
            return buffer.getvalue()

        verified, changed = archive(first), archive(replacement)
        original_open = SUBJECT.tarfile.open
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.tar.xz"
            path.write_bytes(verified)

            def replace_path_before_parse(*, fileobj=None, mode="r", **kwargs):
                path.write_bytes(changed)
                return original_open(fileobj=fileobj, mode=mode, **kwargs)

            with patch.object(SUBJECT, "ARCHIVE_SHA256", hashlib.sha256(verified).hexdigest()):
                with patch.object(SUBJECT.tarfile, "open", side_effect=replace_path_before_parse):
                    files = SUBJECT._source_files(path)
        self.assertEqual(files, {"pkg.py": first})

    def test_stdlib_name_table_parses_only_sorted_unique_top_level_names(self):
        header = (
            b"// generated\n"
            b"static const char* _Py_stdlib_module_names[] = {\n"
            b'"alpha",\n"beta_2",\n'
            b"};\n"
        )
        with patch.object(
            SUBJECT, "STDLIB_MODULE_NAMES_SHA256", hashlib.sha256(header).hexdigest()
        ):
            names, digest = SUBJECT._stdlib_module_names(header)
        self.assertEqual(names, ("alpha", "beta_2"))
        self.assertEqual(
            digest, hashlib.sha256(b"alpha\nbeta_2\n").hexdigest()
        )

    def test_stdlib_name_table_rejects_unsorted_and_duplicate_names(self):
        for rows in (b'"beta",\n"alpha",\n', b'"alpha",\n"alpha",\n'):
            header = (
                b"static const char* _Py_stdlib_module_names[] = {\n"
                + rows + b"};\n"
            )
            with self.subTest(rows=rows):
                with patch.object(
                    SUBJECT,
                    "STDLIB_MODULE_NAMES_SHA256",
                    hashlib.sha256(header).hexdigest(),
                ):
                    with self.assertRaisesRegex(ValueError, "STDLIB_MODULE_NAMES_ORDER"):
                        SUBJECT._stdlib_module_names(header)

    def test_frozen_tables_keep_runtime_and_test_names_separate(self):
        source = (
            b"static const struct _frozen bootstrap_modules[] = {\n"
            b'{"boot", code, 1, false, GET_CODE(boot)},\n'
            b"{0, 0, 0} /* bootstrap sentinel */\n};\n"
            b"static const struct _frozen stdlib_modules[] = {\n"
            b'{"pkg.module", code, 1, false, GET_CODE(module)},\n'
            b"{0, 0, 0} /* stdlib sentinel */\n};\n"
            b"static const struct _frozen test_modules[] = {\n"
            b'{"test_only", code, 1, false, GET_CODE(test_only)},\n'
            b"{0, 0, 0} /* test sentinel */\n};\n"
            b"static const struct _module_alias aliases[] = {\n"
            b'{"boot", "pkg.boot"},\n{"test_alias", NULL},\n'
            b"{0, 0} /* aliases sentinel */\n};\n"
        )
        with patch.object(
            SUBJECT, "FROZEN_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ):
            inventory = SUBJECT._frozen_module_inventory(source)
        self.assertEqual(inventory["bootstrap_names"], ("boot",))
        self.assertEqual(inventory["stdlib_names"], ("pkg.module",))
        self.assertEqual(inventory["test_names"], ("test_only",))
        self.assertEqual(
            inventory["aliases"], (("boot", "pkg.boot"), ("test_alias", ""))
        )

    def test_frozen_tables_reject_duplicate_module_names(self):
        source = (
            b"static const struct _frozen bootstrap_modules[] = {\n"
            b'{"boot", code, 1, false, GET_CODE(boot)},\n'
            b'{"boot", code, 1, false, GET_CODE(boot)},\n'
            b"{0, 0, 0} /* bootstrap sentinel */\n};\n"
            b"static const struct _frozen stdlib_modules[] = {\n"
            b'{"module", code, 1, false, GET_CODE(module)},\n'
            b"{0, 0, 0} /* stdlib sentinel */\n};\n"
            b"static const struct _frozen test_modules[] = {\n"
            b'{"test_only", code, 1, false, GET_CODE(test_only)},\n'
            b"{0, 0, 0} /* test sentinel */\n};\n"
            b"static const struct _module_alias aliases[] = {\n"
            b'{"boot", "pkg.boot"},\n'
            b"{0, 0} /* aliases sentinel */\n};\n"
        )
        with patch.object(
            SUBJECT, "FROZEN_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ):
            with self.assertRaisesRegex(ValueError, "FROZEN_TABLE_NAMES"):
                SUBJECT._frozen_module_inventory(source)

    def test_frozen_tables_require_explicit_sentinels(self):
        source = (
            b"static const struct _frozen bootstrap_modules[] = {\n"
            b'{"boot", code, 1, false, GET_CODE(boot)},\n};\n'
            b"static const struct _frozen stdlib_modules[] = {\n"
            b'{"module", code, 1, false, GET_CODE(module)},\n'
            b"{0, 0, 0} /* stdlib sentinel */\n};\n"
            b"static const struct _frozen test_modules[] = {\n"
            b'{"test_only", code, 1, false, GET_CODE(test_only)},\n'
            b"{0, 0, 0} /* test sentinel */\n};\n"
            b"static const struct _module_alias aliases[] = {\n"
            b'{"boot", "pkg.boot"},\n'
            b"{0, 0} /* aliases sentinel */\n};\n"
        )
        with patch.object(
            SUBJECT, "FROZEN_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ):
            with self.assertRaisesRegex(ValueError, "FROZEN_TABLE_SENTINEL"):
                SUBJECT._frozen_module_inventory(source)

    def test_frozen_tables_reject_unparsed_alias_rows(self):
        source = (
            b"static const struct _frozen bootstrap_modules[] = {\n"
            b'{"boot", code, 1, false, GET_CODE(boot)},\n'
            b"{0, 0, 0} /* bootstrap sentinel */\n};\n"
            b"static const struct _frozen stdlib_modules[] = {\n"
            b'{"module", code, 1, false, GET_CODE(module)},\n'
            b"{0, 0, 0} /* stdlib sentinel */\n};\n"
            b"static const struct _frozen test_modules[] = {\n"
            b'{"test_only", code, 1, false, GET_CODE(test_only)},\n'
            b"{0, 0, 0} /* test sentinel */\n};\n"
            b"static const struct _module_alias aliases[] = {\n"
            b'BROKEN_ALIAS_ROW\n'
            b"{0, 0} /* aliases sentinel */\n};\n"
        )
        with patch.object(
            SUBJECT, "FROZEN_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ):
            with self.assertRaisesRegex(ValueError, "FROZEN_ALIAS_ROW"):
                SUBJECT._frozen_module_inventory(source)

    def test_bootstrap_setup_separates_conditional_module_names(self):
        source = (
            b"# static bootstrap fixture\n*static*\n"
            b"atexit atexitmodule.c\n"
            b"@MODULE_PWD_TRUE@pwd pwdmodule.c\n"
        )
        with patch.object(
            SUBJECT, "BOOTSTRAP_SETUP_SHA256", hashlib.sha256(source).hexdigest()
        ):
            inventory = SUBJECT._bootstrap_setup_inventory(source)
        self.assertEqual(inventory["name_count"], 2)
        self.assertEqual(inventory["conditional_name_count"], 1)
        self.assertEqual(inventory["conditional_names"], (("pwd", "PWD"),))

    def test_bootstrap_setup_rejects_unknown_rows_and_duplicate_names(self):
        for source in (
            b"*static*\nmodule without-source.c extra-token\n",
            b"*static*\nmodule source.c\nmodule other.c\n",
        ):
            with patch.object(
                SUBJECT, "BOOTSTRAP_SETUP_SHA256", hashlib.sha256(source).hexdigest()
            ):
                expected = (
                    "BOOTSTRAP_SETUP_SOURCES"
                    if b"extra-token" in source
                    else "BOOTSTRAP_SETUP_NAMES"
                )
                with self.assertRaisesRegex(ValueError, expected):
                    SUBJECT._bootstrap_setup_inventory(source)

    def test_stdlib_setup_separates_test_rows_and_conditions(self):
        source = (
            b"*@MODULE_BUILDTYPE@*\n"
            b"@MODULE_ARRAY_TRUE@array arraymodule.c\n"
            b"*shared*\n"
            b"# Test modules\n"
            b"@MODULE_TEST_TRUE@testmod testmod.c\n"
        )
        with patch.object(
            SUBJECT, "STDLIB_SETUP_SHA256", hashlib.sha256(source).hexdigest()
        ):
            inventory = SUBJECT._stdlib_setup_inventory(source)
        self.assertEqual(inventory["stdlib_entry_count"], 1)
        self.assertEqual(inventory["test_entry_count"], 1)
        self.assertEqual(inventory["condition_count"], 2)

    def test_stdlib_setup_rejects_malformed_and_duplicate_module_rows(self):
        for source, expected in (
            (
                b"*@MODULE_BUILDTYPE@*\n*shared*\nnot-a-module-row\n",
                "STDLIB_SETUP_ROW",
            ),
            (
                b"*@MODULE_BUILDTYPE@*\n*shared*\n"
                b"@MODULE_A_TRUE@module first.c\n"
                b"@MODULE_B_TRUE@module second.c\n",
                "STDLIB_SETUP_NAMES",
            ),
        ):
            with patch.object(
                SUBJECT, "STDLIB_SETUP_SHA256", hashlib.sha256(source).hexdigest()
            ):
                with self.assertRaisesRegex(ValueError, expected):
                    SUBJECT._stdlib_setup_inventory(source)

    def test_getpath_and_sysconfig_sources_bind_path_contracts(self):
        getpath = (
            b"platlibdir = config.get('platlibdir')\n"
            b"program_name = config.get('program_name')\n"
            b"home = config.get('home')\n"
            b"executable = config.get('executable')\n"
            b"base_executable = config.get('base_executable')\n"
            b"prefix = config.get('prefix')\n"
            b"exec_prefix = config.get('exec_prefix')\n"
            b"base_prefix = config.get('base_prefix')\n"
            b"base_exec_prefix = config.get('base_exec_prefix')\n"
            b"pythonpath = config.get('module_search_paths')\n"
            b"real_executable_dir = None\nstdlib_dir = None\n"
            b"platstdlib_dir = config.get('platstdlib_dir')\n"
            b"venv_prefix = None\n"
            b"ENV_PYTHONPATH = config['pythonpath_env']\n"
            b"def search_up(path):\n    return path\n"
            b"if os_name == 'posix' or os_name == 'darwin':\n"
            b"    ZIP_LANDMARK = f'{platlibdir}/python{VERSION_MAJOR}"
            b"{VERSION_MINOR}.zip'\n"
            b"    STDLIB_SUBDIR = f'{platlibdir}/python{VERSION_MAJOR}."
            b"{VERSION_MINOR}'\n"
            b"    STDLIB_LANDMARKS = [f'{STDLIB_SUBDIR}/os.py', "
            b"f'{STDLIB_SUBDIR}/os.pyc']\n"
            b"    PLATSTDLIB_LANDMARK = f'{platlibdir}/python{VERSION_MAJOR}."
            b"{VERSION_MINOR}/lib-dynload'\n"
            b"    pythonpath.append(joinpath(prefix, ZIP_LANDMARK))\n"
            b"    if os_name == 'nt':\n        pythonpath.append(platstdlib_dir)\n"
            b"    else:\n        pythonpath.append(stdlib_dir)\n"
            b"        pythonpath.append(platstdlib_dir)\n"
            b"if not py_setpath and not home_was_set:\n"
            b"    for p in [library, executable, real_executable]:\n"
            b"        p += '._pth'\n        pth = readlines(p)\n"
            b"if pth_dir:\n    home = pth_dir\n"
            b"config['base_prefix'] = base_prefix or prefix\n"
            b"config['base_exec_prefix'] = base_exec_prefix or exec_prefix\n"
        )
        with patch.object(
            SUBJECT, "GETPATH_SOURCE_SHA256", hashlib.sha256(getpath).hexdigest()
        ):
            inventory = SUBJECT._getpath_source_inventory(getpath)
            altered_getpath = getpath.replace(
                b"config['base_prefix'] = base_prefix or prefix\n", b"",
            )
            with patch.object(
                SUBJECT, "GETPATH_SOURCE_SHA256",
                hashlib.sha256(altered_getpath).hexdigest(),
            ):
                with self.assertRaisesRegex(
                        ValueError, "GETPATH_BASE_PREFIX_BINDING"):
                    SUBJECT._getpath_source_inventory(altered_getpath)
        self.assertEqual(inventory["path_variable_count"], 14)
        self.assertEqual(inventory["config_key_count"], 12)
        self.assertEqual(
            inventory["posix_zip_landmark_template"],
            "f'{platlibdir}/python{VERSION_MAJOR}{VERSION_MINOR}.zip'",
        )
        self.assertEqual(
            inventory["posix_stdlib_landmark_template"],
            "[f'{STDLIB_SUBDIR}/os.py', f'{STDLIB_SUBDIR}/os.pyc']",
        )
        self.assertEqual(
            inventory["posix_platstdlib_landmark_template"],
            "f'{platlibdir}/python{VERSION_MAJOR}.{VERSION_MINOR}/lib-dynload'",
        )
        self.assertEqual(
            inventory["posix_default_path_append_order"],
            ("ZIP_LANDMARK", "stdlib_dir", "platstdlib_dir"),
        )
        self.assertTrue(inventory["pth_override_guard"])
        self.assertTrue(inventory["base_prefix_config_read"])
        self.assertTrue(inventory["base_prefix_fallback_bound"])

        sysconfig = (
            b"_INSTALL_SCHEMES = {'posix': {'stdlib': 'lib/python', 'purelib': 'site'}}\n"
            b"def _get_sysconfigdata_name():\n"
            b"    multiarch = getattr(sys.implementation, '_multiarch', '')\n"
            b"    return os.environ.get('_PYTHON_SYSCONFIGDATA_NAME', "
            b"f'_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}')\n"
            b"def _init_posix(vars):\n"
            b"    name = _get_sysconfigdata_name()\n"
            b"    _temp = __import__(name, globals(), locals(), ['build_time_vars'], 0)\n"
            b"    build_time_vars = _temp.build_time_vars\n"
            b"    vars.update(build_time_vars)\n"
            b"def get_config_var(name): return name\n"
            b"def get_config_vars(): return {}\n"
            b"def get_path(name): return name\n"
            b"def get_path_names(): return ()\n"
            b"def get_paths(): return {}\n"
        )
        with patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(sysconfig).hexdigest()
        ):
            scheme_inventory = SUBJECT._sysconfig_source_inventory(sysconfig)
        self.assertEqual(scheme_inventory["scheme_count"], 1)
        self.assertEqual(scheme_inventory["path_key_count"], 2)
        self.assertEqual(scheme_inventory["sysconfigdata_override_key"], "_PYTHON_SYSCONFIGDATA_NAME")
        self.assertEqual(scheme_inventory["sysconfigdata_name_template"],
                         "_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}")
        self.assertEqual(scheme_inventory["sysconfigdata_importer"], "__import__")
        self.assertEqual(scheme_inventory["sysconfigdata_imported_attribute"], "build_time_vars")
        self.assertEqual(scheme_inventory["sysconfigdata_initializer_parameter"], "vars")
        self.assertEqual(scheme_inventory["sysconfigdata_initializer_update_receiver"], "vars")
        self.assertEqual(scheme_inventory["sysconfigdata_initializer_update_value"], "build_time_vars")

    def test_sysconfig_source_rejects_changed_sysconfigdata_import_route(self):
        source = (
            b"_INSTALL_SCHEMES = {'posix': {'stdlib': 'lib/python'}}\n"
            b"def _get_sysconfigdata_name():\n"
            b"    multiarch = getattr(sys.implementation, '_multiarch', '')\n"
            b"    return os.environ.get('_PYTHON_SYSCONFIGDATA_NAME', "
            b"f'_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}')\n"
            b"def _init_posix(vars):\n"
            b"    name = _get_sysconfigdata_name()\n"
            b"    _temp = __import__(name, globals(), locals(), ['wrong'], 0)\n"
            b"    build_time_vars = _temp.build_time_vars\n"
            b"    vars.update(build_time_vars)\n"
            b"def get_config_var(name): return name\n"
            b"def get_config_vars(): return {}\n"
            b"def get_path(name): return name\n"
            b"def get_path_names(): return ()\n"
            b"def get_paths(): return {}\n"
        )
        with patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ):
            with self.assertRaisesRegex(ValueError, "SYSCONFIGDATA_IMPORT_SOURCE"):
                SUBJECT._sysconfig_source_inventory(source)
        changed_name_source = source.replace(
            b"_PYTHON_SYSCONFIGDATA_NAME", b"_UNSELECTED_SYSCONFIGDATA_NAME"
        )
        with patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256",
            hashlib.sha256(changed_name_source).hexdigest(),
        ):
            with self.assertRaisesRegex(ValueError, "SYSCONFIGDATA_NAME_SOURCE"):
                SUBJECT._sysconfig_source_inventory(changed_name_source)
        async_source = source.replace(
            b"def _init_posix(vars):", b"async def _init_posix(vars):"
        )
        with patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(async_source).hexdigest()
        ):
            with self.assertRaisesRegex(ValueError, "SYSCONFIGDATA_IMPORT_SOURCE"):
                SUBJECT._sysconfig_source_inventory(async_source)
        decorated_source = source.replace(
            b"def _get_sysconfigdata_name():",
            b"@decorator\ndef _get_sysconfigdata_name():",
        )
        with patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256",
            hashlib.sha256(decorated_source).hexdigest(),
        ):
            with self.assertRaisesRegex(ValueError, "SYSCONFIGDATA_NAME_SOURCE"):
                SUBJECT._sysconfig_source_inventory(decorated_source)

    def test_sysconfig_source_rejects_executable_scheme_expression(self):
        source = (
            b"_INSTALL_SCHEMES = build_schemes()\n"
            b"def _get_sysconfigdata_name():\n"
            b"    multiarch = getattr(sys.implementation, '_multiarch', '')\n"
            b"    return os.environ.get('_PYTHON_SYSCONFIGDATA_NAME', "
            b"f'_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}')\n"
            b"def _init_posix(vars):\n"
            b"    name = _get_sysconfigdata_name()\n"
            b"    _temp = __import__(name, globals(), locals(), ['build_time_vars'], 0)\n"
            b"    build_time_vars = _temp.build_time_vars\n"
            b"    vars.update(build_time_vars)\n"
            b"def get_config_var(name): return name\n"
            b"def get_config_vars(): return {}\n"
            b"def get_path(name): return name\n"
            b"def get_path_names(): return ()\n"
            b"def get_paths(): return {}\n"
        )
        with patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ):
            with self.assertRaisesRegex(ValueError, "SYSCONFIG_SCHEME_LITERAL"):
                SUBJECT._sysconfig_source_inventory(source)

    def test_importlib_sources_bind_module_spec_and_loader_contracts(self):
        bootstrap = (
            b"class ModuleSpec:\n"
            b" def __init__(self):\n"
            b"  self.name = None\n  self.loader = None\n  self.origin = None\n"
            b"  self.loader_state = None\n  self.submodule_search_locations = None\n"
            b"  self._uninitialized_submodules = None\n  self._set_fileattr = None\n"
            b"  self._cached = None\n"
            b"class BuiltinImporter:\n def find_spec(self): pass\n"
            b"class FrozenImporter:\n def find_spec(self): pass\n"
            b"def _find_spec(): pass\ndef _find_and_load(): pass\n"
            b"def _load_unlocked(): pass\ndef _init_module_attrs(): pass\n"
        )
        external = (
            b"class SourceFileLoader: pass\nclass SourcelessFileLoader: pass\n"
            b"class ExtensionFileLoader: pass\nclass NamespaceLoader: pass\n"
            b"class PathFinder: pass\nclass FileFinder: pass\n"
        )
        with patch.object(
            SUBJECT, "IMPORTLIB_BOOTSTRAP_SOURCE_SHA256", hashlib.sha256(bootstrap).hexdigest()
        ), patch.object(
            SUBJECT, "IMPORTLIB_EXTERNAL_SOURCE_SHA256", hashlib.sha256(external).hexdigest()
        ):
            inventory = SUBJECT._importlib_source_inventory(bootstrap, external)
        self.assertEqual(inventory["module_spec_field_count"], 8)
        self.assertEqual(inventory["loader_finder_class_count"], 6)

    def test_importlib_public_api_binds_exported_source_aliases(self):
        machinery = (
            b"from _bootstrap import ModuleSpec, BuiltinImporter, FrozenImporter\n"
            b"from _bootstrap_external import PathFinder, FileFinder\n"
            b"from _bootstrap_external import SourceFileLoader, SourcelessFileLoader\n"
            b"from _bootstrap_external import ExtensionFileLoader, NamespaceLoader\n"
        )
        util = (
            b"from _bootstrap import module_from_spec, spec_from_loader\n"
            b"from _bootstrap_external import spec_from_file_location\n"
            b"from _bootstrap_external import LazyLoader\n"
            b"def find_spec(): pass\n"
        )
        with patch.object(
            SUBJECT, "IMPORTLIB_MACHINERY_SOURCE_SHA256", hashlib.sha256(machinery).hexdigest()
        ), patch.object(
            SUBJECT, "IMPORTLIB_UTIL_SOURCE_SHA256", hashlib.sha256(util).hexdigest()
        ):
            inventory = SUBJECT._importlib_public_api_inventory(machinery, util)
        self.assertEqual(inventory["machinery_export_count"], 9)
        self.assertEqual(inventory["util_export_count"], 5)

    def test_importlib_finder_registration_candidate_is_source_bounded(self):
        bootstrap = (
            b"class BuiltinImporter: pass\nclass FrozenImporter: pass\n"
            b"def _setup(sys_module, _imp_module): pass\n"
            b"def _install(sys_module, _imp_module):\n"
            b"    _setup(sys_module, _imp_module)\n"
            b"    sys.meta_path.append(BuiltinImporter)\n"
            b"    sys.meta_path.append(FrozenImporter)\n"
        )
        external = (
            b"class PathFinder: pass\nclass FileFinder:\n"
            b"    @staticmethod\n    def path_hook(*loaders): pass\n"
            b"def _set_bootstrap_module(module): pass\n"
            b"def _get_supported_file_loaders(): return ()\n"
            b"def _install(_bootstrap_module):\n"
            b"    _set_bootstrap_module(_bootstrap_module)\n"
            b"    supported_loaders = _get_supported_file_loaders()\n"
            b"    sys.path_hooks.extend([FileFinder.path_hook(*supported_loaders)])\n"
            b"    sys.meta_path.append(PathFinder)\n"
        )

        def check_sources(bootstrap_source, external_source):
            files = {
                "importlib/_bootstrap.py": bootstrap_source,
                "importlib/_bootstrap_external.py": external_source,
            }
            with patch.object(
                SUBJECT, "IMPORTLIB_BOOTSTRAP_SOURCE_SHA256",
                hashlib.sha256(bootstrap_source).hexdigest(),
            ), patch.object(
                SUBJECT, "IMPORTLIB_EXTERNAL_SOURCE_SHA256",
                hashlib.sha256(external_source).hexdigest(),
            ):
                return SUBJECT._target_importlib_finder_registration_candidate(files)

        candidate = check_sources(bootstrap, external)
        self.assertIsNotNone(candidate)
        self.assertEqual(
            candidate["sys_meta_path_registration_sites"],
            [
                ["importlib._bootstrap._install", "BuiltinImporter"],
                ["importlib._bootstrap._install", "FrozenImporter"],
                ["importlib._bootstrap_external._install", "PathFinder"],
            ],
        )
        self.assertEqual(candidate["file_path_hook_registration_site"], [
            "importlib._bootstrap_external._install", "FileFinder.path_hook",
        ])
        self.assertFalse(candidate["final_sys_meta_path_claimed"])
        self.assertFalse(candidate["final_sys_path_hooks_claimed"])

        changed_call = bootstrap + b"\nsys.meta_path.append(UnexpectedFinder)\n"
        self.assertIsNone(check_sources(changed_call, external))
        changed_hook = external.replace(
            b"sys.path_hooks.extend([FileFinder.path_hook(*supported_loaders)])",
            b"sys.path_hooks.append(FileFinder.path_hook(*supported_loaders))",
        )
        self.assertIsNone(check_sources(bootstrap, changed_hook))

    def test_meta_path_finder_labels_bind_to_declared_classes(self):
        bootstrap = (
            b"class BuiltinImporter:\n"
            b"    @classmethod\n    def find_spec(cls, fullname): pass\n"
            b"class FrozenImporter:\n"
            b"    @classmethod\n    def find_spec(cls, fullname): pass\n"
        )
        external = (
            b"class PathFinder:\n"
            b"    @classmethod\n    def find_spec(cls, fullname): pass\n"
        )

        def check_sources(bootstrap_source, external_source):
            files = {
                "importlib/_bootstrap.py": bootstrap_source,
                "importlib/_bootstrap_external.py": external_source,
            }
            with patch.object(
                SUBJECT, "IMPORTLIB_BOOTSTRAP_SOURCE_SHA256",
                hashlib.sha256(bootstrap_source).hexdigest(),
            ), patch.object(
                SUBJECT, "IMPORTLIB_EXTERNAL_SOURCE_SHA256",
                hashlib.sha256(external_source).hexdigest(),
            ):
                return SUBJECT._target_meta_path_finder_class_candidate(files)

        candidate = check_sources(bootstrap, external)
        self.assertIsNotNone(candidate)
        self.assertEqual(
            [(row["module"], row["class"], row["method_kind"])
             for row in candidate["registered_finder_declarations"]],
            [
                ("importlib._bootstrap", "BuiltinImporter", "classmethod"),
                ("importlib._bootstrap", "FrozenImporter", "classmethod"),
                ("importlib._bootstrap_external", "PathFinder", "classmethod"),
            ],
        )
        self.assertFalse(candidate["runtime_instances_claimed"])
        self.assertFalse(candidate["selection_claimed"])
        registration = {
            "source_sha256": candidate["source_sha256"],
            "sys_meta_path_registration_sites": [
                ["importlib._bootstrap._install", "BuiltinImporter"],
                ["importlib._bootstrap._install", "FrozenImporter"],
                ["importlib._bootstrap_external._install", "PathFinder"],
            ],
            "final_sys_meta_path_claimed": False,
            "evidence_scope": "STATIC_IMPORTLIB_REGISTRATION_SITES_CANDIDATE",
        }
        field_candidate = SUBJECT._target_s15_finders_field_candidate(
            registration, candidate,
        )
        self.assertEqual(field_candidate, {
            "values": ("BUILTIN", "FROZEN", "PATH"),
            "registration_sites": registration["sys_meta_path_registration_sites"],
            "class_declarations": candidate["registered_finder_declarations"],
            "source_sha256": registration["source_sha256"],
            "runtime_finder_instances_claimed": False,
            "runtime_selection_claimed": False,
            "evidence_scope": "STATIC_S15_FINDERS_FIELD_CANDIDATE",
        })
        self.assertIsNone(SUBJECT._target_s15_finders_field_candidate(
            {**registration, "sys_meta_path_registration_sites": []}, candidate,
        ))

        changed_class = bootstrap.replace(
            b"class BuiltinImporter:", b"class BuiltinLoader:"
        )
        self.assertIsNone(check_sources(changed_class, external))
        changed_method = external.replace(
            b"    @classmethod\n    def find_spec", b"    def find_spec"
        )
        self.assertIsNone(check_sources(bootstrap, changed_method))

    def test_filefinder_hook_factory_binds_loader_order_and_guard(self):
        source = (
            b"def _get_supported_file_loaders():\n"
            b"    extensions = ExtensionFileLoader, _imp.extension_suffixes()\n"
            b"    source = SourceFileLoader, SOURCE_SUFFIXES\n"
            b"    bytecode = SourcelessFileLoader, BYTECODE_SUFFIXES\n"
            b"    return [extensions, source, bytecode]\n\n"
            b"class FileFinder:\n"
            b"    @classmethod\n"
            b"    def path_hook(cls, *loader_details):\n"
            b'        """Hook constructor for FileFinder directories."""\n'
            b"        def path_hook_for_FileFinder(path):\n"
            b'            """Path hook for importlib.machinery.FileFinder."""\n'
            b"            if not _path_isdir(path):\n"
            b"                raise ImportError('only directories are supported', path=path)\n"
            b"            return cls(path, *loader_details)\n"
            b"        return path_hook_for_FileFinder\n"
        )

        def check_source(candidate_source):
            files = {"importlib/_bootstrap_external.py": candidate_source}
            with patch.object(
                SUBJECT, "IMPORTLIB_EXTERNAL_SOURCE_SHA256",
                hashlib.sha256(candidate_source).hexdigest(),
            ):
                return SUBJECT._target_filefinder_hook_factory_candidate(files)

        candidate = check_source(source)
        self.assertIsNotNone(candidate)
        self.assertTrue(candidate["path_hook_classmethod"])
        self.assertEqual(candidate["supported_loader_detail_order"], [
            "ExtensionFileLoader", "SourceFileLoader", "SourcelessFileLoader",
        ])
        self.assertEqual(candidate["returned_hook"], "path_hook_for_FileFinder")
        self.assertEqual(candidate["non_directory_result"], "ImportError(path=path)")

        changed_order = source.replace(
            b"return [extensions, source, bytecode]",
            b"return [bytecode, source, extensions]",
        )
        self.assertIsNone(check_source(changed_order))
        changed_guard = source.replace(
            b"if not _path_isdir(path):", b"if _path_isdir(path):"
        )
        self.assertIsNone(check_source(changed_guard))

    def test_zipimporter_attribute_is_bound_to_public_class_source(self):
        source = (
            b"__all__ = ['ZipImportError', 'zipimporter']\n"
            b"class ZipImportError(ImportError):\n    pass\n"
            b"class zipimporter(_bootstrap_external._LoaderBasics):\n"
            b"    pass\n"
        )

        def check_source(candidate_source):
            files = {"zipimport.py": candidate_source}
            with patch.object(
                SUBJECT, "ZIPIMPORT_SOURCE_SHA256",
                hashlib.sha256(candidate_source).hexdigest(),
            ):
                return SUBJECT._target_zipimporter_class_source_candidate(files)

        candidate = check_source(source)
        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["module"], "zipimport")
        self.assertEqual(candidate["requested_attribute"], "zipimporter")
        self.assertEqual(candidate["class_base"], "_bootstrap_external._LoaderBasics")
        self.assertTrue(candidate["listed_in_all"])
        self.assertFalse(candidate["runtime_imported"])

        changed_class = source.replace(b"class zipimporter(", b"class zip_importer(")
        self.assertIsNone(check_source(changed_class))
        changed_exports = source.replace(
            b"__all__ = ['ZipImportError', 'zipimporter']",
            b"__all__ = ['ZipImportError']",
        )
        self.assertIsNone(check_source(changed_exports))

    def test_zipimport_hook_registration_is_conditional_and_ordered(self):
        source = (
            b"static int\ninit_zipimport(PyThreadState *tstate, int verbose)\n{\n"
            b'    PyObject *path_hooks = _PySys_GetRequiredAttrString("path_hooks");\n'
            b"    if (path_hooks == NULL) {\n        return -1;\n    }\n\n"
            b"    if (verbose) {\n"
            b'        PySys_WriteStderr("# installing zipimport hook\\n");\n'
            b"    }\n\n"
            b'    PyObject *zipimporter = _PyImport_GetModuleAttrString("zipimport", "zipimporter");\n'
            b"    if (zipimporter == NULL) {\n"
            b"        _PyErr_Clear(tstate); /* No zipimporter object -- okay */\n"
            b"        if (verbose) {\n"
            b'            PySys_WriteStderr("# can\'t import zipimport.zipimporter\\n");\n'
            b"        }\n    }\n    else {\n"
            b"        /* sys.path_hooks.insert(0, zipimporter) */\n"
            b"        int err = PyList_Insert(path_hooks, 0, zipimporter);\n"
            b"        Py_DECREF(zipimporter);\n"
            b"        if (err < 0) {\n            Py_DECREF(path_hooks);\n"
            b"            return -1;\n        }\n"
            b"        if (verbose) {\n"
            b'            PySys_WriteStderr("# installed zipimport hook\\n");\n'
            b"        }\n    }\n    Py_DECREF(path_hooks);\n\n"
            b"    return 0;\n}\n\n"
            b"PyStatus\n_PyImport_InitExternal(PyThreadState *tstate)\n{\n"
            b"    int verbose = _PyInterpreterState_GetConfig(tstate->interp)->verbose;\n\n"
            b"    // XXX Initialize here: sys.path_hooks and sys.path_importer_cache.\n\n"
            b"    if (init_importlib_external(tstate->interp) != 0) {\n"
            b"        _PyErr_Print(tstate);\n"
            b'        return _PyStatus_ERR("external importer setup failed");\n'
            b"    }\n\n"
            b"    if (init_zipimport(tstate, verbose) != 0) {\n"
            b"        PyErr_Print();\n"
            b'        return _PyStatus_ERR("initializing zipimport failed");\n'
            b"    }\n\n    return _PyStatus_OK();\n}\n"
        )

        def check_source(candidate_source):
            with patch.object(
                SUBJECT, "PYTHON_IMPORT_C_SHA256",
                hashlib.sha256(candidate_source).hexdigest(),
            ):
                return SUBJECT._target_zipimport_hook_registration_candidate(
                    candidate_source
                )

        candidate = check_source(source)
        self.assertIsNotNone(candidate)
        self.assertEqual(
            candidate["registration_operation"],
            "PyList_Insert(path_hooks, 0, zipimporter)",
        )
        self.assertTrue(candidate["registration_conditional_on_attribute"])
        self.assertTrue(candidate["missing_attribute_skips_registration"])
        self.assertTrue(candidate["insertion_error_returns_failure"])
        self.assertTrue(
            candidate["external_importlib_setup_precedes_zipimport_attempt"]
        )
        self.assertFalse(candidate["final_sys_path_hooks_claimed"])

        changed_position = source.replace(
            b"PyList_Insert(path_hooks, 0, zipimporter)",
            b"PyList_Insert(path_hooks, 1, zipimporter)",
        )
        self.assertIsNone(check_source(changed_position))
        changed_order = source.replace(
            b"init_importlib_external(tstate->interp)",
            b"__ZIPORDER__",
        ).replace(
            b"init_zipimport(tstate, verbose)",
            b"init_importlib_external(tstate->interp)",
        ).replace(b"__ZIPORDER__", b"init_zipimport(tstate, verbose)")
        self.assertIsNone(check_source(changed_order))

    def test_s15_hooks_candidate_joins_registration_order_and_declarations(self):
        importlib_registration = {
            "source_sha256": [
                SUBJECT.IMPORTLIB_BOOTSTRAP_SOURCE_SHA256,
                SUBJECT.IMPORTLIB_EXTERNAL_SOURCE_SHA256,
            ],
            "file_path_hook_registration_site": [
                "importlib._bootstrap_external._install", "FileFinder.path_hook",
            ],
            "final_sys_path_hooks_claimed": False,
        }
        zipimport_registration = {
            "source_sha256": SUBJECT.PYTHON_IMPORT_C_SHA256,
            "registration_operation": "PyList_Insert(path_hooks, 0, zipimporter)",
            "registration_conditional_on_attribute": True,
            "missing_attribute_skips_registration": True,
            "external_importlib_setup_precedes_zipimport_attempt": True,
            "final_sys_path_hooks_claimed": False,
        }
        filefinder_factory = {
            "source_sha256": SUBJECT.IMPORTLIB_EXTERNAL_SOURCE_SHA256,
            "path_hook_factory": "FileFinder.path_hook",
            "returned_hook": "path_hook_for_FileFinder",
            "supported_loader_detail_order": [
                "ExtensionFileLoader", "SourceFileLoader", "SourcelessFileLoader",
            ],
            "evidence_scope": "STATIC_FILEFINDER_HOOK_FACTORY_CANDIDATE",
        }
        zipimporter_class = {
            "source_sha256": SUBJECT.ZIPIMPORT_SOURCE_SHA256,
            "module": "zipimport",
            "requested_attribute": "zipimporter",
            "listed_in_all": True,
            "runtime_imported": False,
            "evidence_scope": "STATIC_ZIPIMPORTER_CLASS_DECLARATION_CANDIDATE",
        }
        candidate = SUBJECT._target_s15_hooks_field_candidate(
            importlib_registration, zipimport_registration,
            filefinder_factory, zipimporter_class,
        )
        self.assertEqual(candidate, {
            "values": ("ZIPIMPORTER", "FILEFINDER"),
            "registration_order_basis": (
                "FileFinder appended during external importlib setup",
                "zipimporter inserted at index zero after that setup",
            ),
            "registration_source_sha256": {
                "importlib": importlib_registration["source_sha256"],
                "zipimport": zipimport_registration["source_sha256"],
            },
            "factory_source_sha256": SUBJECT.IMPORTLIB_EXTERNAL_SOURCE_SHA256,
            "class_source_sha256": SUBJECT.ZIPIMPORT_SOURCE_SHA256,
            "runtime_hook_objects_claimed": False,
            "final_sys_path_hooks_claimed": False,
            "evidence_scope": "STATIC_S15_HOOKS_FIELD_CANDIDATE",
        })
        self.assertIsNone(SUBJECT._target_s15_hooks_field_candidate(
            importlib_registration,
            {**zipimport_registration,
             "registration_operation": "PyList_Insert(path_hooks, 1, zipimporter)"},
            filefinder_factory, zipimporter_class,
        ))

    def test_s15_assumption_candidate_requires_one_fixed_literal_declaration(self):
        source = (
            b'ASSUMPTION = "DECLARED_SETUP_PYTHON_CONTROL_RUNTIME"\n'
            b"def observe():\n    return ASSUMPTION\n"
        )
        with patch.object(
            SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
            hashlib.sha256(source).hexdigest(),
        ):
            self.assertEqual(SUBJECT._target_s15_assumption_field_candidate(source), {
                "value": "DECLARED_SETUP_PYTHON_CONTROL_RUNTIME",
                "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
                "source_sha256": hashlib.sha256(source).hexdigest(),
                "runtime_assumption_attested": False,
                "evidence_scope": "STATIC_S15_ASSUMPTION_FIELD_CANDIDATE",
            })
            changed = source + b'ASSUMPTION = "OTHER"\n'
            with patch.object(
                SUBJECT, "DGN007_RUNTIME_PROFILE_SOURCE_SHA256",
                hashlib.sha256(changed).hexdigest(),
            ):
                self.assertIsNone(
                    SUBJECT._target_s15_assumption_field_candidate(changed)
                )

    def test_configure_sources_bind_builtin_template_and_module_block(self):
        config_c = (
            b"/* -- ADDMODULE MARKER 1 -- */\n"
            b"struct _inittab _PyImport_Inittab[] = {\n"
            b"/* -- ADDMODULE MARKER 2 -- */\n"
            b'{"marshal", PyMarshal_Init},\n{"_imp", PyInit__imp},\n'
            b'{"_ast", PyInit__ast},\n{"_tokenize", PyInit__tokenize},\n'
            b'{"builtins", NULL},\n{"sys", NULL},\n{"gc", PyInit_gc},\n'
            b'{"_warnings", _PyWarnings_Init},\n{"_string", PyInit__string},\n'
        )
        configure = (
            b"AC_DEFUN([_MODULE_BLOCK_ADD], [AS_VAR_APPEND([MODULE_BLOCK])])\n"
            b"MODULE_BLOCK=\nAC_SUBST([MODULE_BLOCK])\n"
            b"AC_SUBST([MODULE_BUILDTYPE])\n"
        )
        with patch.object(
            SUBJECT, "CONFIG_C_TEMPLATE_SHA256", hashlib.sha256(config_c).hexdigest()
        ), patch.object(
            SUBJECT, "CONFIGURE_SOURCE_SHA256", hashlib.sha256(configure).hexdigest()
        ):
            inventory = SUBJECT._configure_template_inventory(config_c, configure)
        self.assertEqual(inventory["config_c_row_count"], 9)
        self.assertEqual(inventory["configure_module_anchor_count"], 4)


    def test_relative_imports_and_function_imports_are_candidates(self):
        files = {
            "pkg/__init__.py": b"from . import child\n",
            "pkg/child.py": b"def load():\n    from . import helper\n",
            "pkg/helper.py": b"VALUE = 1\n",
        }
        modules, edges, digest = SUBJECT._candidate_closure(files, ("pkg",))
        self.assertEqual(modules, ("pkg", "pkg.child", "pkg.helper"))
        self.assertEqual(edges, 4)
        self.assertEqual(len(digest), 64)

    def test_module_and_class_bodies_are_kept_but_uncalled_function_body_is_not(self):
        files = {
            "pkg/__init__.py": (
                b"class Loaded:\n    from . import class_helper\n"
                b"if True:\n    try:\n        from . import nested_helper\n"
                b"    except ImportError:\n        pass\n"
                b"def unused():\n    from . import function_only\n"
            ),
            "pkg/class_helper.py": b"VALUE = 1\n",
            "pkg/nested_helper.py": b"VALUE = 3\n",
            "pkg/function_only.py": b"VALUE = 2\n",
        }
        modules, edges, _ = SUBJECT._module_body_candidate_closure(files, ("pkg",))
        self.assertEqual(modules, ("pkg", "pkg.class_helper", "pkg.nested_helper"))
        self.assertEqual(edges, 4)

    def test_target_platform_prunes_only_known_linux_cpython_branches(self):
        files = {
            "pkg/__init__.py": (
                b"import sys\n"
                b"if sys.platform == 'linux':\n    from . import linux_helper\n"
                b"else:\n    from . import non_linux_helper\n"
                b"if sys.version_info == [3, 12, 16, 'final', 0]:\n"
                b"    from . import list_wrong\n"
                b"else:\n    from . import tuple_correct\n"
                b"if feature_flag:\n    from . import unknown_a\n"
                b"else:\n    from . import unknown_b\n"
            ),
            "pkg/linux_helper.py": b"VALUE = 1\n",
            "pkg/non_linux_helper.py": b"VALUE = 2\n",
            "pkg/list_wrong.py": b"VALUE = 5\n",
            "pkg/tuple_correct.py": b"VALUE = 6\n",
            "pkg/unknown_a.py": b"VALUE = 3\n",
            "pkg/unknown_b.py": b"VALUE = 4\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            files, ("pkg",), known_call_facts=(("sys.platform", "linux"),),
        )
        self.assertEqual(
            modules,
            ("pkg", "pkg.linux_helper", "pkg.tuple_correct", "pkg.unknown_a", "pkg.unknown_b"),
        )
        self.assertEqual(conditions, {"resolved": 2, "unknown": 1})

    def test_target_platform_reports_unknown_guards_with_stable_source_locations(self):
        files = {
            "pkg.py": (
                b"if first_flag:\n    import child\n"
                b"else:\n    import fallback\n"
            ),
            "child.py": b"if second_flag:\n    pass\n",
            "fallback.py": b"VALUE = 1\n",
        }
        unknown = []
        _, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown
        )
        self.assertEqual(conditions, {"resolved": 0, "unknown": 2})
        self.assertEqual(unknown, [
            {"module": "child", "source_path": "child.py", "line": 1,
             "expression": "second_flag"},
            {"module": "pkg", "source_path": "pkg.py", "line": 1,
             "expression": "first_flag"},
        ])

    def test_target_python_version_info_uses_full_cpython_tuple(self):
        short_equal = ast.parse("sys.version_info == (3, 12, 16)", mode="eval").body
        minimum = ast.parse("sys.version_info >= (3, 12)", mode="eval").body
        identity = ast.parse("sys.platform is 'linux'", mode="eval").body
        self.assertIs(SUBJECT._target_condition(short_equal), False)
        self.assertIs(SUBJECT._target_condition(minimum), True)
        self.assertIsNone(SUBJECT._target_condition(identity))

    def test_target_python_version_info_resolves_named_fields(self):
        for expression, expected in (
                ("sys.version_info.major == 3", True),
                ("sys.version_info.minor == 12", True),
                ("sys.version_info.micro == 15", False),
                ("sys.version_info.releaselevel == 'final'", True),
                ("sys.version_info.serial == 0", True)):
            condition = ast.parse(expression, mode="eval").body
            self.assertIs(SUBJECT._target_condition(condition), expected)
        unknown = ast.parse(
            "sys.version_info.future_field == 0", mode="eval"
        ).body
        self.assertIsNone(SUBJECT._target_condition(unknown))

    def test_target_platform_closure_uses_version_info_named_fields(self):
        files = {
            "pkg.py": (
                b"import sys\n"
                b"if sys.version_info.major == 3:\n    import current\n"
                b"else:\n    import other\n"
                b"if sys.version_info.future_field == 0:\n"
                b"    import dynamic_a\nelse:\n    import dynamic_b\n"
            ),
            "current.py": b"VALUE = True\n",
            "other.py": b"VALUE = False\n",
            "dynamic_a.py": b"VALUE = 1\n",
            "dynamic_b.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            files, ("pkg",),
        )
        self.assertEqual(modules, (
            "current", "dynamic_a", "dynamic_b", "pkg",
        ))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 1})

    def test_target_python_version_info_resolves_constant_indexes_only(self):
        for expression, expected in (
                ("sys.version_info[0] == 3", True),
                ("sys.version_info[1] == 12", True),
                ("sys.version_info[2] >= 17", False),
                ("sys.version_info[-1] == 0", True),
                ("sys.version_info[-2] == 'final'", True)):
            condition = ast.parse(expression, mode="eval").body
            self.assertIs(SUBJECT._target_condition(condition), expected)
        for expression in (
                "sys.version_info[index] == 3",
                "sys.version_info[9] == 3",
                "sys.version_info[-9] == 3",
                "sys.version_info[True] == 3"):
            condition = ast.parse(expression, mode="eval").body
            self.assertIsNone(SUBJECT._target_condition(condition))

    def test_target_platform_closure_uses_version_info_constant_indexes(self):
        files = {
            "pkg.py": (
                b"import sys\n"
                b"if sys.version_info[0] == 3:\n    import py3\n"
                b"else:\n    import other\n"
                b"if sys.version_info[-1] == 0:\n    import final_release\n"
                b"else:\n    import prerelease\n"
                b"if sys.version_info[index] == 3:\n    import dynamic_a\n"
                b"else:\n    import dynamic_b\n"
            ),
            "py3.py": b"VALUE = 3\n",
            "other.py": b"VALUE = 0\n",
            "final_release.py": b"VALUE = 1\n",
            "prerelease.py": b"VALUE = 2\n",
            "dynamic_a.py": b"VALUE = 1\n",
            "dynamic_b.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            files, ("pkg",),
        )
        self.assertEqual(modules, (
            "dynamic_a", "dynamic_b", "final_release", "pkg", "py3",
        ))
        self.assertEqual(conditions, {"resolved": 2, "unknown": 1})

    def test_target_python_version_info_resolves_constant_slices_only(self):
        for expression, expected in (
                ("sys.version_info[:2] == (3, 12)", True),
                ("sys.version_info[1:3] == (12, 16)", True),
                ("sys.version_info[::2] == (3, 16, 0)", True),
                ("sys.version_info[-2:] == ('final', 0)", True),
                ("sys.version_info[4:1:-1] == (0, 'final', 16)", True)):
            condition = ast.parse(expression, mode="eval").body
            self.assertIs(SUBJECT._target_condition(condition), expected)
        for expression in (
                "sys.version_info[:bound] == (3, 12)",
                "sys.version_info[::0] == (3, 12, 16, 'final', 0)"):
            condition = ast.parse(expression, mode="eval").body
            self.assertIsNone(SUBJECT._target_condition(condition))

    def test_target_platform_closure_uses_version_info_constant_slices(self):
        files = {
            "pkg.py": (
                b"import sys\n"
                b"if sys.version_info[:2] == (3, 12):\n    import py312\n"
                b"else:\n    import other\n"
                b"if sys.version_info[:bound] == (3, 12):\n"
                b"    import dynamic_a\nelse:\n    import dynamic_b\n"
            ),
            "py312.py": b"VALUE = 312\n",
            "other.py": b"VALUE = 0\n",
            "dynamic_a.py": b"VALUE = 1\n",
            "dynamic_b.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            files, ("pkg",), known_call_facts=(("sys.platform", "linux"),),
        )
        self.assertEqual(modules, (
            "dynamic_a", "dynamic_b", "pkg", "py312",
        ))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 1})

    def test_target_platform_string_resolves_constant_indexes_and_slices(self):
        for expression, expected in (
                ("sys.platform[0] == 'l'", True),
                ("sys.platform[-1] == 'x'", True),
                ("sys.platform[:3] == 'lin'", True),
                ("os.name[0] == 'p'", True)):
            condition = ast.parse(expression, mode="eval").body
            self.assertIs(SUBJECT._target_condition(
                condition, known_call_facts=(
                    ("sys.platform", "linux"), ("os.name", "posix"),
                ),
            ), expected)
        for expression in (
                "sys.platform[index] == 'l'",
                "sys.platform[99] == 'l'",
                "sys.platform[:bound] == 'lin'"):
            condition = ast.parse(expression, mode="eval").body
            self.assertIsNone(SUBJECT._target_condition(condition))

    def test_target_platform_closure_uses_bound_string_slices(self):
        files = {
            "pkg.py": (
                b"import sys\n"
                b"if sys.platform[:3] == 'lin':\n    import linux\n"
                b"else:\n    import other\n"
                b"if sys.platform[index] == 'l':\n    import dynamic_a\n"
                b"else:\n    import dynamic_b\n"
            ),
            "linux.py": b"VALUE = True\n",
            "other.py": b"VALUE = False\n",
            "dynamic_a.py": b"VALUE = 1\n",
            "dynamic_b.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            files, ("pkg",), known_call_facts=(("sys.platform", "linux"),),
        )
        self.assertEqual(modules, (
            "dynamic_a", "dynamic_b", "linux", "pkg",
        ))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 1})

    def test_target_condition_indexes_complete_literal_lists(self):
        for expression, expected in (
                ("[3, 12, 16][0] == 3", True),
                ("[3, 12, 16][1:] == [12, 16]", True),
                ("[3, 12, 16][-1] == 16", True)):
            condition = ast.parse(expression, mode="eval").body
            self.assertIs(SUBJECT._target_condition(condition), expected)
        for expression in ("[3, 12][index] == 3", "[3, 12][9] == 3"):
            condition = ast.parse(expression, mode="eval").body
            self.assertIsNone(SUBJECT._target_condition(condition))

    def test_target_platform_closure_uses_complete_literal_list_indexes(self):
        files = {
            "pkg.py": (
                b"if [3, 12][0] == 3:\n    import selected\n"
                b"else:\n    import rejected\n"
                b"if [3, 12][index] == 3:\n    import dynamic_a\n"
                b"else:\n    import dynamic_b\n"
            ),
            "selected.py": b"VALUE = True\n",
            "rejected.py": b"VALUE = False\n",
            "dynamic_a.py": b"VALUE = 1\n",
            "dynamic_b.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            files, ("pkg",),
        )
        self.assertEqual(modules, (
            "dynamic_a", "dynamic_b", "pkg", "selected",
        ))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 1})

    def test_target_condition_indexes_complete_literal_dictionaries(self):
        for expression, expected in (
                ("{'x': 3, 4: 'a'}['x'] == 3", True),
                ("{(1, 2): True}[(1, 2)]", True)):
            condition = ast.parse(expression, mode="eval").body
            self.assertIs(SUBJECT._target_condition(condition), expected)
        for expression in (
                "{'x': 3}[key] == 3",
                "{'x': 3}['missing'] == 3",
                "{[]}"):
            condition = ast.parse(expression, mode="eval").body
            self.assertIsNone(SUBJECT._target_condition(condition))

    def test_target_platform_closure_uses_complete_literal_dictionary_indexes(self):
        files = {
            "pkg.py": (
                b"if {'x': True}['x']:\n    import selected\n"
                b"else:\n    import rejected\n"
                b"if {0: True}[dynamic_key]:\n    import dynamic_a\n"
                b"else:\n    import dynamic_b\n"
            ),
            "selected.py": b"VALUE = True\n",
            "rejected.py": b"VALUE = False\n",
            "dynamic_a.py": b"VALUE = 1\n",
            "dynamic_b.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            files, ("pkg",),
        )
        self.assertEqual(modules, (
            "dynamic_a", "dynamic_b", "pkg", "selected",
        ))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 1})

    def test_target_condition_resolves_get_on_literal_dictionaries(self):
        for expression, expected in (
                ("{'x': True}.get('x')", True),
                ("{'x': True}.get('missing', False)", False),
                ("{}.get('missing') is None", True)):
            condition = ast.parse(expression, mode="eval").body
            self.assertIs(SUBJECT._target_condition(condition), expected)
        for expression in (
                "{'x': True}.get(dynamic_key)",
                "{}.get('missing', dynamic_default)",
                "{'x': True}.get('x', dynamic_default)",
                "{'x': True}.get('x', default=False)"):
            condition = ast.parse(expression, mode="eval").body
            self.assertIsNone(SUBJECT._target_condition(condition))

    def test_target_platform_closure_uses_literal_dictionary_get(self):
        files = {
            "pkg.py": (
                b"if {'x': True}.get('x'):\n    import selected\n"
                b"else:\n    import rejected\n"
                b"if {}.get('missing', dynamic_default):\n"
                b"    import dynamic_a\nelse:\n    import dynamic_b\n"
            ),
            "selected.py": b"VALUE = True\n",
            "rejected.py": b"VALUE = False\n",
            "dynamic_a.py": b"VALUE = 1\n",
            "dynamic_b.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            files, ("pkg",),
        )
        self.assertEqual(modules, (
            "dynamic_a", "dynamic_b", "pkg", "selected",
        ))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 1})

    def test_target_condition_resolves_startswith_on_known_platform_strings(self):
        for expression, expected in (
                ("sys.platform.startswith('linux')", True),
                ("os.name.startswith(('nt', 'java'))", False),
                ("sys.platform.startswith(())", False)):
            condition = ast.parse(expression, mode="eval").body
            self.assertIs(SUBJECT._target_condition(
                condition, known_call_facts=(
                    ("sys.platform", "linux"), ("os.name", "posix"),
                ),
            ), expected)
        for expression in (
                "sys.platform.startswith(dynamic_prefix)",
                "sys.platform.startswith(('linux', dynamic_prefix))",
                "sys.platform.startswith('linux', 1)"):
            condition = ast.parse(expression, mode="eval").body
            self.assertIsNone(SUBJECT._target_condition(condition))

    def test_target_platform_closure_uses_known_platform_startswith(self):
        files = {
            "pkg.py": (
                b"if sys.platform.startswith('linux'):\n    import selected\n"
                b"else:\n    import rejected\n"
                b"if sys.platform.startswith(dynamic_prefix):\n"
                b"    import dynamic_a\nelse:\n    import dynamic_b\n"
            ),
            "selected.py": b"VALUE = True\n",
            "rejected.py": b"VALUE = False\n",
            "dynamic_a.py": b"VALUE = 1\n",
            "dynamic_b.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            files, ("pkg",), known_call_facts=(("sys.platform", "linux"),),
        )
        self.assertEqual(modules, (
            "dynamic_a", "dynamic_b", "pkg", "selected",
        ))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 1})

    def test_target_platform_membership_resolves_constant_set_literals(self):
        condition = ast.parse(
            "sys.platform in {'emscripten', 'vxworks', 'wasi'}", mode="eval"
        ).body
        self.assertIs(SUBJECT._target_condition(
            condition, known_call_facts=(("sys.platform", "linux"),),
        ), False)
        non_target = ast.parse("sys.platform in {'linux', 'wasi'}", mode="eval").body
        self.assertIs(SUBJECT._target_condition(
            non_target, known_call_facts=(("sys.platform", "linux"),),
        ), True)
        dynamic = ast.parse("sys.platform in {'linux', runtime_value}", mode="eval").body
        self.assertIsNone(SUBJECT._target_condition(dynamic))

    def test_os_name_requires_the_digest_bound_posix_export_fact(self):
        condition = ast.parse("os.name == 'posix'", mode="eval").body
        self.assertIsNone(SUBJECT._target_condition(condition))
        self.assertIs(SUBJECT._target_condition(
            condition, known_call_facts=(("os.name", "posix"),),
        ), True)
        self.assertIs(SUBJECT._target_condition(
            ast.parse("os.name == 'nt'", mode="eval").body,
            known_call_facts=(("os.name", "posix"),),
        ), False)

    def test_importlib_case_platform_facts_require_pinned_constants(self):
        source = (
            b"_CASE_INSENSITIVE_PLATFORMS_STR_KEY = ('win',)\n"
            b"_CASE_INSENSITIVE_PLATFORMS_BYTES_KEY = ('cygwin', 'darwin')\n"
            b"_CASE_INSENSITIVE_PLATFORMS = (_CASE_INSENSITIVE_PLATFORMS_BYTES_KEY "
            b"+ _CASE_INSENSITIVE_PLATFORMS_STR_KEY)\n"
            b"def _make_relax_case():\n"
            b"    if sys.platform.startswith(_CASE_INSENSITIVE_PLATFORMS): pass\n"
            b"    if sys.platform.startswith(_CASE_INSENSITIVE_PLATFORMS_STR_KEY): pass\n"
        )
        expected = (
            ("sys.platform.startswith(_CASE_INSENSITIVE_PLATFORMS)", False),
            ("sys.platform.startswith(_CASE_INSENSITIVE_PLATFORMS_STR_KEY)", False),
        )
        with patch.object(
            SUBJECT, "IMPORTLIB_EXTERNAL_SOURCE_SHA256",
            hashlib.sha256(source).hexdigest(),
        ):
            self.assertEqual(SUBJECT._target_importlib_case_platform_facts(
                {"importlib/_bootstrap_external.py": source}
            ), expected)
            self.assertEqual(SUBJECT._target_importlib_case_platform_facts({}), ())

    def test_types_descriptor_facts_require_exact_source_bindings(self):
        types_source = (
            b"GetSetDescriptorType = type(FunctionType.__code__)\n"
            b"MemberDescriptorType = type(FunctionType.__globals__)\n"
        )
        inspect_source = (
            b"import types\n"
            b"if hasattr(types, 'MemberDescriptorType'):\n    pass\n"
            b"if hasattr(types, 'GetSetDescriptorType'):\n    pass\n"
        )
        files = {"types.py": types_source, "inspect.py": inspect_source}
        with patch.object(
            SUBJECT, "_TYPES_SOURCE_SHA256", hashlib.sha256(types_source).hexdigest()
        ), patch.object(
            SUBJECT, "_INSPECT_SOURCE_SHA256", hashlib.sha256(inspect_source).hexdigest()
        ):
            facts = SUBJECT._target_types_descriptor_call_facts(files)
            self.assertEqual(
                facts,
                (("hasattr(types, 'GetSetDescriptorType')", True),
                 ("hasattr(types, 'MemberDescriptorType')", True)),
            )
            self.assertEqual(
                SUBJECT._target_types_descriptor_call_facts(
                    {**files, "types.py": types_source + b"Other = 1\n"}
                ),
                (),
            )
            rebound = inspect_source + b"hasattr = lambda *args: False\n"
            with patch.object(
                SUBJECT, "_INSPECT_SOURCE_SHA256", hashlib.sha256(rebound).hexdigest()
            ):
                self.assertEqual(
                    SUBJECT._target_types_descriptor_call_facts(
                        {**files, "inspect.py": rebound}
                    ),
                    (),
                )

    def test_source_bound_hasattr_fact_resolves_only_exact_recorded_call(self):
        fact = "hasattr(types, 'MemberDescriptorType')"
        expression = ast.parse(fact, mode="eval").body
        self.assertIs(SUBJECT._target_condition(
            expression, known_call_facts=((fact, True),)
        ), True)
        self.assertIsNone(SUBJECT._target_condition(expression))
        self.assertIsNone(SUBJECT._target_condition(
            ast.parse("hasattr(types, 'UnknownType')", mode="eval").body,
            known_call_facts=((fact, True),),
        ))

    def test_ast_compatibility_facts_require_all_digest_bound_sources(self):
        ast_source = (
            b"from _ast import *\n"
            b"if not hasattr(Constant, 'n'):\n    pass\n"
            b"if not hasattr(Tuple, 'dims'):\n    pass\n"
        )
        asdl_source = (
            b"Constant(constant value, string? kind)\n"
            b"Tuple(expr* elts, expr_context ctx)\n"
        )
        c_source = (
            b'PyObject_SetAttrString(state->AST_type, "_fields", empty_tuple) < 0 ||\n'
            b'PyObject_SetAttrString(state->AST_type, "_attributes", empty_tuple) < 0\n'
            b'state->expr_type = make_type(state, "expr", state->AST_type, NULL, 0,\n'
            b'Constant_fields[] = {"value", "kind"};\n'
            b'state->Constant_type = make_type(state, "Constant", state->expr_type, Constant_fields, 2, 0);\n'
            b'Tuple_fields[] = {"elts", "ctx"};\n'
            b'state->Tuple_type = make_type(state, "Tuple", state->expr_type, Tuple_fields, 2, 0);\n'
        )
        files = {"ast.py": ast_source}
        with patch.object(
            SUBJECT, "_AST_SOURCE_SHA256", hashlib.sha256(ast_source).hexdigest()
        ), patch.object(
            SUBJECT, "AST_ASDL_SHA256", hashlib.sha256(asdl_source).hexdigest()
        ), patch.object(
            SUBJECT, "AST_C_SHA256", hashlib.sha256(c_source).hexdigest()
        ):
            self.assertEqual(
                SUBJECT._target_ast_compatibility_call_facts(
                    files, asdl_source, c_source
                ),
                (("hasattr(Constant, 'n')", False),
                 ("hasattr(Tuple, 'dims')", False)),
            )
            self.assertEqual(SUBJECT._target_ast_compatibility_call_facts(
                files, asdl_source + b"changed", c_source
            ), ())
            rebound = ast_source + b"Constant = object\n"
            with patch.object(
                SUBJECT, "_AST_SOURCE_SHA256", hashlib.sha256(rebound).hexdigest()
            ):
                self.assertEqual(SUBJECT._target_ast_compatibility_call_facts(
                    {"ast.py": rebound}, asdl_source, c_source
                ), ())

    def test_source_bound_false_hasattr_fact_resolves_negated_guard(self):
        expression = ast.parse("not hasattr(Constant, 'n')", mode="eval").body
        self.assertIs(SUBJECT._target_condition(
            expression, known_call_facts=(("hasattr(Constant, 'n')", False),)
        ), True)
        self.assertIsNone(SUBJECT._target_condition(expression))

    def test_sys_getframe_fact_requires_builtin_method_table_bindings(self):
        logging_source = (
            b"import sys, os\n"
            b"if hasattr(sys, '_getframe'):\n    currentframe = sys._getframe\n"
        )
        sys_source = (
            b'#include "clinic/sysmodule.c.h"\n'
            b'static PyMethodDef sys_methods[] = {\n    SYS__GETFRAME_METHODDEF\n};\n'
            b'static struct PyModuleDef sysmodule = {\n    sys_methods,\n};\n'
        )
        clinic_source = (
            b"#define SYS__GETFRAME_METHODDEF    \\\n"
            b'    {"_getframe", sys__getframe},\n'
        )
        files = {"logging/__init__.py": logging_source}
        with patch.object(
            SUBJECT, "LOGGING_SOURCE_SHA256", hashlib.sha256(logging_source).hexdigest()
        ), patch.object(
            SUBJECT, "SYS_MODULE_C_SHA256", hashlib.sha256(sys_source).hexdigest()
        ), patch.object(
            SUBJECT, "SYS_MODULE_CLINIC_SHA256", hashlib.sha256(clinic_source).hexdigest()
        ):
            self.assertEqual(
                SUBJECT._target_sys_getframe_call_facts(files, sys_source, clinic_source),
                (("hasattr(sys, '_getframe')", True),),
            )
            self.assertEqual(SUBJECT._target_sys_getframe_call_facts(
                {"logging/__init__.py": logging_source + b"sys = None\n"},
                sys_source, clinic_source,
            ), ())

    def test_warnings_defaults_fact_requires_imported_c_backend(self):
        warnings_source = (
            b"try:\n"
            b"    from _warnings import (filters, _defaultaction, _onceregistry, warn, warn_explicit, _filters_mutated)\n"
            b"    _warnings_defaults = True\n"
            b"except ImportError:\n    _warnings_defaults = False\n"
            b"if not _warnings_defaults:\n    pass\n"
        )
        c_source = (
            b'#include "clinic/_warnings.c.h"\n'
            b"static PyMethodDef warnings_functions[] = {\n"
            b"WARNINGS_WARN_METHODDEF\nWARNINGS_WARN_EXPLICIT_METHODDEF\n"
            b"WARNINGS_FILTERS_MUTATED_METHODDEF\n};\n"
            b"static int warnings_module_exec(PyObject *module) {\n"
            b'PyModule_AddObjectRef(module, "filters", st->filters);\n'
            b'PyModule_AddObjectRef(module, "_onceregistry", st->once_registry);\n'
            b'PyModule_AddObjectRef(module, "_defaultaction", st->default_action);\n}\n'
            b"static PyModuleDef_Slot warnings_slots[] = {\n"
            b"{Py_mod_exec, warnings_module_exec}\n};\n"
            b"static struct PyModuleDef warnings_module = {\n"
            b".m_methods = warnings_functions,\n.m_slots = warnings_slots,\n};\n"
        )
        clinic_source = (
            b"#define WARNINGS_WARN_METHODDEF \\\n    {\"warn\", impl},\n"
            b"#define WARNINGS_WARN_EXPLICIT_METHODDEF \\\n    {\"warn_explicit\", impl},\n"
            b"#define WARNINGS_FILTERS_MUTATED_METHODDEF \\\n    {\"_filters_mutated\", impl},\n"
        )
        files = {"warnings.py": warnings_source}
        patches = (
            patch.object(SUBJECT, "WARNINGS_SOURCE_SHA256", hashlib.sha256(warnings_source).hexdigest()),
            patch.object(SUBJECT, "WARNINGS_C_SHA256", hashlib.sha256(c_source).hexdigest()),
            patch.object(SUBJECT, "WARNINGS_CLINIC_SHA256", hashlib.sha256(clinic_source).hexdigest()),
        )
        with patches[0], patches[1], patches[2]:
            facts = SUBJECT._target_warnings_default_call_facts(
                files, c_source, clinic_source
            )
            self.assertEqual(facts, {"_warnings_defaults": True})
            condition = ast.parse("not _warnings_defaults", mode="eval").body
            self.assertIs(SUBJECT._target_condition(condition, known_names=facts), False)
            self.assertEqual(SUBJECT._target_warnings_default_call_facts(
                {"warnings.py": warnings_source + b"_warnings_defaults = False\n"},
                c_source, clinic_source,
            ), {})

    def test_pinned_star_exports_preserve_imported_module_name_only(self):
        importer = (
            b"from opcode import *\n"
            b"if __name__ == '__main__':\n    import disassembler\n"
        )
        exporter = b"__all__ = ['cmp_op', 'opmap']\n"
        files = {"dis.py": importer, "opcode.py": exporter}
        digest_patches = (
            patch.object(SUBJECT, "DIS_SOURCE_SHA256", hashlib.sha256(importer).hexdigest()),
            patch.object(SUBJECT, "OPCODE_SOURCE_SHA256", hashlib.sha256(exporter).hexdigest()),
        )
        with digest_patches[0], digest_patches[1]:
            self.assertTrue(SUBJECT._target_imported_name_star_imports_safe(files, "dis"))
            aliases = SUBJECT._target_name_aliases(
                ast.parse(importer), imported_module_name=True
            )
            unknown = []
            stats = {"resolved": 0, "unknown": 0}
            imports = tuple(SUBJECT._module_body_import_names(
                ast.parse(importer), "dis", "dis.py", target_platform=True,
                condition_stats=stats, known_names=aliases,
                unknown_conditions=unknown,
                preserve_imported_name=True,
            ))
            self.assertEqual(imports, ("opcode",))
            self.assertEqual(stats, {"resolved": 1, "unknown": 0})
            self.assertFalse(SUBJECT._target_imported_name_star_imports_safe(
                {**files, "opcode.py": exporter + b"__all__.append('__name__')\n"},
                "dis",
            ))

    def test_plain_main_guard_requires_pinned_unmodified_module_name(self):
        source = b"VALUE = 1\nif __name__ == '__main__':\n    import demo\n"
        digest_patch = patch.dict(
            SUBJECT._TARGET_PLAIN_MAIN_GUARD_SOURCE_DIGESTS,
            {"fixture": hashlib.sha256(source).hexdigest()},
        )
        with digest_patch:
            self.assertTrue(SUBJECT._target_plain_main_guard_name_safe(
                {"fixture.py": source}, "fixture"
            ))
            for unsafe in (
                source + b"__name__ = 'changed'\n",
                source + b"g = globals\ng()\n",
                source + b"import builtins\nbuiltins.exec('pass')\n",
            ):
                with self.subTest(unsafe=unsafe), patch.dict(
                    SUBJECT._TARGET_PLAIN_MAIN_GUARD_SOURCE_DIGESTS,
                    {"fixture": hashlib.sha256(unsafe).hexdigest()},
                ):
                    self.assertFalse(SUBJECT._target_plain_main_guard_name_safe(
                        {"fixture.py": unsafe}, "fixture"
                    ))

    def test_ast_star_import_name_survives_only_fixed_legacy_namespace_removal(self):
        importer = (
            b"from _ast import *\n"
            b"_deprecated_globals = {name: globals().pop(name) "
            b"for name in ('Num', 'Str')}\n"
            b"def __getattr__(name):\n    return globals()[name]\n"
            b"if __name__ == '__main__':\n    import ast_demo\n"
        )
        c_source = b"static _ast module initialization without export table\n"
        files = {"ast.py": importer}
        with patch.object(
            SUBJECT, "_AST_SOURCE_SHA256", hashlib.sha256(importer).hexdigest()
        ), patch.object(
            SUBJECT, "AST_C_SHA256", hashlib.sha256(c_source).hexdigest()
        ):
            self.assertTrue(SUBJECT._target_ast_imported_name_star_import_safe(
                files, c_source
            ))
            changed = importer.replace(b"('Num', 'Str')", b"('Num', '__name__')")
            with patch.object(
                SUBJECT, "_AST_SOURCE_SHA256", hashlib.sha256(changed).hexdigest()
            ):
                self.assertFalse(SUBJECT._target_ast_imported_name_star_import_safe(
                    {"ast.py": changed}, c_source
                ))

    def test_inspect_module_name_survives_bounded_globals_initialization(self):
        source = (
            b"import dis\nmod_dict = globals()\n"
            b"for k, v in dis.COMPILER_FLAG_NAMES.items():\n"
            b"    mod_dict['CO_' + v] = k\n"
            b"del k, v, mod_dict\n"
            b"def helper():\n    return eval('x', globals(), locals())\n"
            b"if __name__ == '__main__':\n    import inspect_demo\n"
        )
        files = {"inspect.py": source}
        with patch.object(
            SUBJECT, "_INSPECT_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ):
            self.assertTrue(SUBJECT._target_inspect_imported_name_safe(files))
            self.assertIs(SUBJECT._target_condition(
                ast.parse("__name__ == '__main__'", mode="eval").body,
                known_names={"__name__": SUBJECT._IMPORTED_MODULE_NAME},
            ), False)
            rebound = source.replace(
                b"del k, v, mod_dict\n", b"globals()['__name__'] = '__main__'\n"
            )
            with patch.object(
                SUBJECT, "_INSPECT_SOURCE_SHA256", hashlib.sha256(rebound).hexdigest()
            ):
                self.assertFalse(SUBJECT._target_inspect_imported_name_safe(
                    {"inspect.py": rebound}
                ))

    def test_sysconfig_module_name_fact_rejects_executed_namespace_access(self):
        source = (
            b"def helper():\n    return globals()\n"
            b"VALUE = 1\n"
            b"if __name__ == '__main__':\n    import config_demo\n"
        )
        with patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ):
            self.assertTrue(SUBJECT._target_sysconfig_imported_name_safe(
                {"sysconfig.py": source}
            ))
            rebound = source.replace(
                b"VALUE = 1", b"globals()['__name__'] = '__main__'"
            )
            with patch.object(
                SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(rebound).hexdigest()
            ):
                self.assertFalse(SUBJECT._target_sysconfig_imported_name_safe(
                    {"sysconfig.py": rebound}
                ))

    def test_os_posix_star_import_cannot_replace_platform_name(self):
        os_source = (
            b"import sys\n_names = sys.builtin_module_names\n"
            b"def _exists(name):\n    return name in globals()\n"
            b"if 'posix' in _names:\n    name = 'posix'\n"
            b"    from posix import *\n"
            b"    try:\n        from posix import _have_functions\n"
            b"    except ImportError:\n        pass\n"
            b"elif 'nt' in _names:\n    name = 'nt'\n"
            b"if not _exists('fspath'):\n    pass\n"
            b"if _exists('_have_functions'):\n    pass\n"
        )
        posix_source = (
            b"static PyMemberDef DirEntry_members[] = {\n"
            b'{"name", T_OBJECT_EX, READONLY};\n'
            b"static PyMethodDef posix_methods[] = {\nOS_FSPATH_METHODDEF\n};\n"
            b"static int posixmodule_exec(PyObject *m) {\n"
            b'    return _PyModule_Add(m, "_have_functions", list);\n}\n'
            b"static struct PyModuleDef_Slot posixmodile_slots[] = {\n"
            b"    {Py_mod_exec, posixmodule_exec},\n};\n"
            b"static struct PyModuleDef posixmodule = {.m_methods = posix_methods, "
            b".m_slots = posixmodile_slots};\n"
        )
        clinic_source = (
            b'static const char * const _keywords[] = {"path", "name", NULL};\n'
            b'static _PyArg_Parser _parser = {.keywords = _keywords, '
            b'.fname = "pathconf"};\n'
            b'static const char * const _keywords[] = {"name", "flags", NULL};\n'
            b'static _PyArg_Parser _parser = {.keywords = _keywords, '
            b'.fname = "memfd_create"};\n'
            b"#define OS_FSPATH_METHODDEF \\\n    {\"fspath\", impl},\n"
        )
        patches = (
            patch.object(SUBJECT, "OS_SOURCE_SHA256", hashlib.sha256(os_source).hexdigest()),
            patch.object(SUBJECT, "POSIX_MODULE_C_SHA256", hashlib.sha256(posix_source).hexdigest()),
            patch.object(SUBJECT, "POSIX_MODULE_CLINIC_SHA256", hashlib.sha256(clinic_source).hexdigest()),
        )
        with patches[0], patches[1], patches[2]:
            facts = SUBJECT._target_os_posix_name_facts(
                {"os.py": os_source}, posix_source, clinic_source
            )
            self.assertEqual(facts, {"name": "posix"})
            self.assertIs(SUBJECT._target_condition(
                ast.parse("name == 'nt'", mode="eval").body,
                known_names=facts,
            ), False)
            self.assertEqual(SUBJECT._target_os_fspath_call_facts(
                {"os.py": os_source}, posix_source, clinic_source
            ), (("_exists('fspath')", True),))
            self.assertEqual(SUBJECT._target_os_have_functions_call_facts(
                {"os.py": os_source}, posix_source, clinic_source
            ), (("_exists('_have_functions')", True),))
            self.assertEqual(SUBJECT._target_os_have_functions_call_facts(
                {"os.py": os_source},
                posix_source.replace(
                    b'return _PyModule_Add(m, "_have_functions", list);',
                    b'return 0;',
                ),
                clinic_source,
            ), ())
            self.assertEqual(SUBJECT._target_os_posix_name_facts(
                {"os.py": os_source},
                posix_source + b'PyModule_AddObjectRef(m, "name", value);\n',
                clinic_source,
            ), {})

    def test_os_posix_name_fact_propagates_to_bytes_environment_guard(self):
        source = (
            b"import sys\n_names = sys.builtin_module_names\n"
            b"def _exists(name):\n    return name in globals()\n"
            b"if 'posix' in _names:\n    name = 'posix'\n"
            b"    from posix import *\n"
            b"elif 'nt' in _names:\n    name = 'nt'\n"
            b"supports_bytes_environ = (name != 'nt')\n"
            b"if supports_bytes_environ:\n    pass\n"
        )
        posix = (
            b"static PyMemberDef DirEntry_members[] = {\n"
            b'{"name", T_OBJECT_EX, READONLY};\n'
            b"static PyMethodDef posix_methods[] = {\n};\n"
            b"static struct PyModuleDef posixmodule = {.m_methods = posix_methods};\n"
        )
        clinic = (
            b'static const char * const _keywords[] = {"path", "name", NULL};\n'
            b'static _PyArg_Parser _parser = {.keywords = _keywords, '
            b'.fname = "pathconf"};\n'
            b'static const char * const _keywords[] = {"name", "flags", NULL};\n'
            b'static _PyArg_Parser _parser = {.keywords = _keywords, '
            b'.fname = "memfd_create"};\n'
        )
        with patch.object(
            SUBJECT, "OS_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ), patch.object(
            SUBJECT, "POSIX_MODULE_C_SHA256", hashlib.sha256(posix).hexdigest()
        ), patch.object(
            SUBJECT, "POSIX_MODULE_CLINIC_SHA256", hashlib.sha256(clinic).hexdigest()
        ):
            self.assertEqual(SUBJECT._target_os_posix_boolean_assignment_facts(
                {"os.py": source}, posix, clinic
            ), {"supports_bytes_environ": True})
            rebound = source.replace(b"name != 'nt'", b"name == 'nt'")
            with patch.object(
                SUBJECT, "OS_SOURCE_SHA256", hashlib.sha256(rebound).hexdigest()
            ):
                self.assertEqual(SUBJECT._target_os_posix_boolean_assignment_facts(
                    {"os.py": rebound}, posix, clinic
                ), {})

    def test_os_posix_boolean_fact_survives_the_star_import(self):
        source = b"from posix import *\nif supports_bytes_environ:\n    import bytes_env\n"
        unknown = []
        imports = tuple(SUBJECT._module_body_import_names(
            ast.parse(source, filename="os.py"), "os", "os.py",
            target_platform=True,
            known_names={"supports_bytes_environ": True},
            unknown_conditions=unknown,
        ))
        self.assertEqual(imports, ("posix", "bytes_env"))
        self.assertEqual(unknown, [])

    def test_target_pyconfig_binds_native_posix_export_facts(self):
        os_source = (
            b"import sys\n_names = sys.builtin_module_names\n"
            b"def _exists(name):\n    return name in globals()\n"
            b"if 'posix' in _names:\n    name = 'posix'\n"
            b"    from posix import *\n"
            b"    try:\n        from posix import _have_functions\n"
            b"    except ImportError:\n        pass\n"
            b"elif 'nt' in _names:\n    name = 'nt'\n"
            b"if _exists('_have_functions'):\n    pass\n"
            b"if not _exists('fspath'):\n    pass\n"
        )
        posix_source = (
            b"static PyMemberDef DirEntry_members[] = {\n"
            b'{"name", T_OBJECT_EX, READONLY};\n'
            b"static PyMethodDef posix_methods[] = {\n"
            b"OS_FSPATH_METHODDEF\nOS_STATVFS_METHODDEF\n"
            b"OS_FSTATVFS_METHODDEF\nOS_LCHOWN_METHODDEF\n"
            b"OS_REGISTER_AT_FORK_METHODDEF\nOS_FORK_METHODDEF\n"
            b"OS_EXECV_METHODDEF\nOS_SPAWNV_METHODDEF\n};\n"
            b"static int posixmodule_exec(PyObject *m) {\n"
            b'    return _PyModule_Add(m, "_have_functions", list);\n}\n'
            b"static PyModuleDef_Slot posixmodile_slots[] = {\n"
            b"    {Py_mod_exec, posixmodule_exec},\n};\n"
            b"static struct PyModuleDef posixmodule = {.m_methods = posix_methods, "
            b".m_slots = posixmodile_slots};\n"
        )
        clinic_source = (
            b'static const char * const _keywords[] = {"path", "name", NULL};\n'
            b'static _PyArg_Parser _parser = {.keywords = _keywords, '
            b'.fname = "pathconf"};\n'
            b'static const char * const _keywords[] = {"name", "flags", NULL};\n'
            b'static _PyArg_Parser _parser = {.keywords = _keywords, '
            b'.fname = "memfd_create"};\n'
            b"#define OS_FSPATH_METHODDEF \\\n    {\"fspath\", impl},\n"
            b"#if (defined(HAVE_STATVFS) && defined(HAVE_SYS_STATVFS_H))\n"
            b"#define OS_STATVFS_METHODDEF \\\n    {\"statvfs\", impl},\n#endif\n"
            b"#if (defined(HAVE_FSTATVFS) && defined(HAVE_SYS_STATVFS_H))\n"
            b"#define OS_FSTATVFS_METHODDEF \\\n    {\"fstatvfs\", impl},\n#endif\n"
            b"#if defined(HAVE_LCHOWN)\n#define OS_LCHOWN_METHODDEF \\\n"
            b"    {\"lchown\", impl},\n#endif\n"
            b"#if defined(HAVE_FORK)\n#define OS_REGISTER_AT_FORK_METHODDEF \\\n"
            b"    {\"register_at_fork\", impl},\n#endif\n"
            b"#if defined(HAVE_FORK)\n#define OS_FORK_METHODDEF \\\n"
            b"    {\"fork\", impl},\n#endif\n"
            b"#if defined(HAVE_EXECV)\n#define OS_EXECV_METHODDEF \\\n"
            b"    {\"execv\", impl},\n#endif\n"
            b"#if (defined(HAVE_SPAWNV) || defined(HAVE_WSPAWNV) || "
            b"defined(HAVE_RTPSPAWN))\n#define OS_SPAWNV_METHODDEF \\\n"
            b"    {\"spawnv\", impl},\n#endif\n"
        )
        pyconfig = (
            b"#define HAVE_STATVFS 1\n#define HAVE_FSTATVFS 1\n"
            b"#define HAVE_SYS_STATVFS_H 1\n#define HAVE_LCHOWN 1\n"
            b"#define HAVE_FORK 1\n#define HAVE_EXECV 1\n"
        )
        with patch.object(
            SUBJECT, "OS_SOURCE_SHA256", hashlib.sha256(os_source).hexdigest()
        ), patch.object(
            SUBJECT, "POSIX_MODULE_C_SHA256", hashlib.sha256(posix_source).hexdigest()
        ), patch.object(
            SUBJECT, "POSIX_MODULE_CLINIC_SHA256", hashlib.sha256(clinic_source).hexdigest()
        ), patch.object(
            SUBJECT, "TARGET_PYCONFIG_SHA256", hashlib.sha256(pyconfig).hexdigest()
        ):
            facts = SUBJECT._target_posix_build_call_facts(
                {"os.py": os_source}, posix_source, clinic_source, pyconfig
            )
            self.assertEqual(SUBJECT._target_posix_build_call_facts(
                {"os.py": os_source}, posix_source, clinic_source,
                pyconfig + b"#define HAVE_SPAWNV 1\n",
            ), ())
        self.assertIn(("_exists('statvfs') and _exists('fstatvfs')", True), facts)
        self.assertIn(("_exists('lchown')", True), facts)
        self.assertIn(("_exists('fork') and (not _exists('spawnv')) and _exists('execv')", True), facts)
        self.assertIn(("_exists('spawnv')", False), facts)
        self.assertIn(("_exists('spawnvp')", False), facts)
        self.assertIn(("hasattr(os, 'register_at_fork')", True), facts)

    def test_os_feature_add_condition_outcomes_are_source_and_build_bound(self):
        os_source = (
            b"import sys\n_names = sys.builtin_module_names\n"
            b"def _exists(name):\n    return name in globals()\n"
            b"if 'posix' in _names:\n    name = 'posix'\n"
            b"    from posix import *\n"
            b"    try:\n        from posix import _have_functions\n"
            b"    except ImportError:\n        pass\n"
            b"if _exists('_have_functions'):\n"
            b"    _globals = globals()\n"
            b"    def _add(str, fn):\n"
            b"        if (fn in _globals) and (str in _have_functions):\n"
            b"            _set.add(_globals[fn])\n"
            b"    _add('HAVE_FCHMOD', 'chmod')\n"
            b"    _add('HAVE_LCHFLAGS', 'chflags')\n"
        )
        posix_source = (
            b"static const struct have_function { const char *label; int (*probe)(void); } "
            b"have_functions[] = {\n"
            b"#ifdef HAVE_FCHMOD\n{\"HAVE_FCHMOD\", NULL},\n#endif\n"
            b"#ifdef HAVE_LCHFLAGS\n{\"HAVE_LCHFLAGS\", NULL},\n#endif\n"
            b"};\n"
            b"static PyMethodDef posix_methods[] = {\nOS_CHMOD_METHODDEF\n};\n"
            b"static int posixmodule_exec(PyObject *m) {\n"
            b'    return _PyModule_Add(m, "_have_functions", list);\n}\n'
            b"{Py_mod_exec, posixmodule_exec}\n"
            b".m_methods = posix_methods;\n.m_slots = posixmodile_slots;\n"
        )
        clinic_source = (
            b"#define OS_CHMOD_METHODDEF    \\\n"
            b'    {"chmod", _PyCFunction_CAST(os_chmod), METH_FASTCALL, doc},\n'
        )
        pyconfig = b"#define HAVE_FCHMOD 1\n"
        files = {"os.py": os_source}
        with patch.multiple(
            SUBJECT,
            OS_SOURCE_SHA256=hashlib.sha256(os_source).hexdigest(),
            POSIX_MODULE_C_SHA256=hashlib.sha256(posix_source).hexdigest(),
            POSIX_MODULE_CLINIC_SHA256=hashlib.sha256(clinic_source).hexdigest(),
            TARGET_PYCONFIG_SHA256=hashlib.sha256(pyconfig).hexdigest(),
        ):
            with patch.object(
                SUBJECT, "_target_os_have_functions_call_facts",
                return_value=(("_exists('_have_functions')", True),),
            ):
                expected = {("os", "os.py", 15): (False, True)}
                facts = SUBJECT._target_os_feature_add_condition_facts(
                    files, posix_source, clinic_source, pyconfig,
                )
                self.assertEqual(facts, expected)
                changed_os = os_source.replace(b"HAVE_LCHFLAGS", b"HAVE_FCHMOD", 1)
                with patch.object(SUBJECT, "OS_SOURCE_SHA256",
                                  hashlib.sha256(changed_os).hexdigest()):
                    self.assertEqual(SUBJECT._target_os_feature_add_condition_facts(
                        {"os.py": changed_os}, posix_source, clinic_source, pyconfig,
                    ), {})
                changed_posix = posix_source.replace(b'{"HAVE_FCHMOD", NULL}',
                                                      b'{"HAVE_FCHMOD", probe_fchmod}', 1)
                with patch.object(SUBJECT, "POSIX_MODULE_C_SHA256",
                                  hashlib.sha256(changed_posix).hexdigest()):
                    self.assertEqual(SUBJECT._target_os_feature_add_condition_facts(
                        files, changed_posix, clinic_source, pyconfig,
                    ), {})

    def test_logging_style_guards_keep_both_source_bound_outcomes(self):
        source = (
            b"_STYLES = {'%': 1, '{': 2, '$': 3}\n"
            b"class Formatter:\n"
            b"    def __init__(self, fmt=None, datefmt=None, style='%'):\n"
            b"        if style not in _STYLES:\n"
            b"            raise ValueError('style')\n"
            b"def basicConfig(**kwargs):\n"
            b"    style = kwargs.pop('style', '%')\n"
            b"    if style not in _STYLES:\n"
            b"        raise ValueError('style')\n"
            b"    Formatter(None, None, style)\n"
        )
        with patch.object(
            SUBJECT, "LOGGING_SOURCE_SHA256", hashlib.sha256(source).hexdigest(),
        ):
            facts = SUBJECT._target_logging_style_line_facts(
                {"logging/__init__.py": source},
            )
            self.assertEqual(facts, {
                ("logging", "logging/__init__.py", 4): (False, True),
                ("logging", "logging/__init__.py", 8): (False, True),
            })
            changed = source.replace(b"'$': 3", b"'!': 3")
            with patch.object(
                SUBJECT, "LOGGING_SOURCE_SHA256", hashlib.sha256(changed).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_logging_style_line_facts(
                    {"logging/__init__.py": changed},
                ), {})

    def test_target_pyconfig_binds_linux_descriptor_support_guard(self):
        os_source = (
            b"from posix import *\n"
            b"def _add(feature, name):\n    pass\n"
            b"_add(\"HAVE_OPENAT\", \"open\")\n"
            b"_add(\"HAVE_FSTATAT\", \"stat\")\n"
            b"_add(\"HAVE_FDOPENDIR\", \"scandir\")\n"
            b"_set.add(stat)\n"
            b"supports_dir_fd = _set\nsupports_fd = _set\n"
            b"if {open, stat} <= supports_dir_fd and {scandir, stat} <= supports_fd:\n"
            b"    pass\n"
        )
        posix_source = (
            b"#if defined(__APPLE__)\n#else\n"
            b"#  define HAVE_FSTATAT_RUNTIME 1\n"
            b"#  define HAVE_FDOPENDIR_RUNTIME 1\n"
            b"#  define HAVE_OPENAT_RUNTIME 1\n#endif\n"
            b"static PyMethodDef posix_methods[] = {\n"
            b"OS_OPEN_METHODDEF\nOS_STAT_METHODDEF\nOS_SCANDIR_METHODDEF\n};\n"
            b".m_methods = posix_methods;\n"
            b'{ "HAVE_OPENAT", probe_openat };\n'
            b'{ "HAVE_FSTATAT", probe_fstatat };\n'
            b'{ "HAVE_FDOPENDIR", probe_fdopendir };\n'
        )
        clinic_source = (
            b'#define OS_OPEN_METHODDEF \\\n    {"open", impl},\n'
            b'#define OS_STAT_METHODDEF \\\n    {"stat", impl},\n'
            b'#define OS_SCANDIR_METHODDEF \\\n    {"scandir", impl},\n'
        )
        pyconfig = (
            b"#define HAVE_OPENAT 1\n#define HAVE_FSTATAT 1\n"
            b"#define HAVE_FDOPENDIR 1\n"
        )
        patches = (
            patch.object(SUBJECT, "OS_SOURCE_SHA256", hashlib.sha256(os_source).hexdigest()),
            patch.object(SUBJECT, "POSIX_MODULE_C_SHA256", hashlib.sha256(posix_source).hexdigest()),
            patch.object(SUBJECT, "POSIX_MODULE_CLINIC_SHA256", hashlib.sha256(clinic_source).hexdigest()),
            patch.object(SUBJECT, "TARGET_PYCONFIG_SHA256", hashlib.sha256(pyconfig).hexdigest()),
            patch.object(SUBJECT, "_target_os_have_functions_call_facts",
                         return_value=(("_exists('_have_functions')", True),)),
        )
        with patches[0], patches[1], patches[2], patches[3], patches[4]:
            files = {"os.py": os_source}
            fact = (("{open, stat} <= supports_dir_fd and {scandir, stat} <= supports_fd", True),)
            self.assertEqual(SUBJECT._target_os_descriptor_support_facts(
                files, posix_source, clinic_source, pyconfig
            ), fact)
            missing_probe = pyconfig.replace(b"#define HAVE_FSTATAT 1\n", b"")
            with patch.object(
                SUBJECT, "TARGET_PYCONFIG_SHA256", hashlib.sha256(missing_probe).hexdigest()
            ):
                self.assertEqual(SUBJECT._target_os_descriptor_support_facts(
                    files, posix_source, clinic_source, missing_probe
                ), ())
            self.assertEqual(SUBJECT._target_os_descriptor_support_facts(
                {"os.py": os_source.replace(b"HAVE_OPENAT", b"HAVE_OPENAT_X")},
                posix_source, clinic_source, pyconfig,
            ), ())

    def test_linux_thread_native_id_source_binds_threading_flag(self):
        header = (
            b"#if (defined(__APPLE__) || defined(__linux__) || defined(_WIN32) "
            b"|| defined(__FreeBSD__))\n#define PY_HAVE_THREAD_NATIVE_ID\n#endif\n"
        )
        module = (
            b"#ifdef PY_HAVE_THREAD_NATIVE_ID\n"
            b"static PyObject * thread_get_native_id(void) { return NULL; }\n"
            b"#endif\nstatic PyMethodDef thread_methods[] = {\n"
            b"#ifdef PY_HAVE_THREAD_NATIVE_ID\n"
            b'{"get_native_id", thread_get_native_id, METH_NOARGS, doc},\n'
            b"#endif\n};\n"
        )
        pthread = b"unsigned long PyThread_get_thread_native_id(void) { return 0; }\n"
        threading_source = (
            b"import _thread\ntry:\n"
            b"    get_native_id = _thread.get_native_id\n"
            b"    _HAVE_THREAD_NATIVE_ID = True\n"
            b"except AttributeError:\n    _HAVE_THREAD_NATIVE_ID = False\n"
        )
        pyconfig = b"#define HAVE_PTHREAD_H 1\n"
        with patch.object(
            SUBJECT, "THREAD_NATIVE_ID_HEADER_SHA256", hashlib.sha256(header).hexdigest()
        ), patch.object(
            SUBJECT, "THREAD_NATIVE_ID_MODULE_SHA256", hashlib.sha256(module).hexdigest()
        ), patch.object(
            SUBJECT, "THREAD_NATIVE_ID_PTHREAD_SHA256", hashlib.sha256(pthread).hexdigest()
        ), patch.object(
            SUBJECT, "THREADING_SOURCE_SHA256", hashlib.sha256(threading_source).hexdigest()
        ), patch.object(
            SUBJECT, "TARGET_PYCONFIG_SHA256", hashlib.sha256(pyconfig).hexdigest()
        ):
            self.assertEqual(SUBJECT._target_threading_native_id_name_facts(
                {"threading.py": threading_source}, header, module, pthread, pyconfig
            ), {"_HAVE_THREAD_NATIVE_ID": True})
            non_linux = header.replace(
                b"defined(__APPLE__) || defined(__linux__)",
                b"defined(__WINDOWS__) || defined(__unix__)",
            )
            with patch.object(
                SUBJECT, "THREAD_NATIVE_ID_HEADER_SHA256",
                hashlib.sha256(non_linux).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_threading_native_id_name_facts(
                    {"threading.py": threading_source}, non_linux, module, pthread,
                    pyconfig,
                ), {})

    def test_threading_main_constructor_guard_uses_fixed_import_arguments(self):
        lines = [""] * 935
        lines[0] = "class Thread:"
        lines[1] = "    def __init__(self, name=None, daemon=None):"
        lines[909] = "        if name:"
        lines[910] = "            pass"
        lines[924] = "        if daemon is not None:"
        lines[925] = "            if daemon and not _daemon_threads_allowed():"
        lines[926] = "                pass"
        lines[930] = "class _MainThread(Thread):"
        lines[931] = "    def __init__(self):"
        lines[932] = "        Thread.__init__(self, name='MainThread', daemon=False)"
        lines[933] = "_main_thread = _MainThread()"
        source = ("\n".join(lines) + "\n").encode()
        expected = {910: True, 925: True, 926: False}
        with patch.object(
            SUBJECT, "THREADING_SOURCE_SHA256", hashlib.sha256(source).hexdigest(),
        ):
            self.assertEqual(
                SUBJECT._target_threading_main_constructor_line_facts(
                    {"threading.py": source},
                ),
                expected,
            )
            altered = source.replace(b"daemon=False", b"daemon=True")
            with patch.object(
                SUBJECT, "THREADING_SOURCE_SHA256",
                hashlib.sha256(altered).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_threading_main_constructor_line_facts(
                        {"threading.py": altered},
                    ),
                    {},
                )

    def test_sysconfig_user_base_is_present_on_the_bound_posix_branch(self):
        source = (
            b"def _getuserbase():\n"
            b"    env_base = os.environ.get('PYTHONUSERBASE', None)\n"
            b"    if env_base:\n        return env_base\n"
            b"    if sys.platform in {'emscripten', 'vxworks', 'wasi'}:\n"
            b"        return None\n"
            b"    def joinuser(*args):\n"
            b"        return os.path.expanduser(os.path.join(*args))\n"
            b"    if os.name == 'nt':\n        return joinuser('~', 'Python')\n"
            b"    if sys.platform == 'darwin':\n        return joinuser('~', 'Library')\n"
            b"    return joinuser('~', '.local')\n"
            b"_HAS_USER_BASE = (_getuserbase() is not None)\n"
            b"if _HAS_USER_BASE:\n    import user_site\n"
        )
        with patch.object(
            SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ):
            self.assertEqual(SUBJECT._target_sysconfig_user_base_name_facts(
                {"sysconfig.py": source}
            ), {"_HAS_USER_BASE": True})
            changed = source.replace(
                b"{'emscripten', 'vxworks', 'wasi'}",
                b"{'emscripten', 'vxworks', 'wasi', 'linux'}",
            )
            with patch.object(
                SUBJECT, "SYSCONFIG_SOURCE_SHA256", hashlib.sha256(changed).hexdigest()
            ):
                self.assertEqual(SUBJECT._target_sysconfig_user_base_name_facts(
                    {"sysconfig.py": changed}
                ), {})

    def test_sysconfig_home_guard_is_false_only_under_explicit_no_site(self):
        sysconfig_source = (
            b"_sys_home = getattr(sys, '_home', None)\n"
            b"if _sys_home:\n    _PROJECT_BASE = _sys_home\n"
        )
        site_source = (
            b"def venv():\n"
            b"    sys._home = None\n"
            b"    if candidate:\n        sys._home = value\n"
        )
        sys_c = b"static int sysmodule_exec(void) { return 0; }\n"
        files = {"sysconfig.py": sysconfig_source, "site.py": site_source}
        patches = (
            patch.object(SUBJECT, "SYSCONFIG_SOURCE_SHA256",
                         hashlib.sha256(sysconfig_source).hexdigest()),
            patch.object(SUBJECT, "SITE_SOURCE_SHA256",
                         hashlib.sha256(site_source).hexdigest()),
            patch.object(SUBJECT, "SYS_MODULE_C_SHA256",
                         hashlib.sha256(sys_c).hexdigest()),
        )
        with patches[0], patches[1], patches[2]:
            self.assertEqual(SUBJECT._target_sysconfig_no_site_facts(
                files, sys_c, True
            ), {"_sys_home": False})
            self.assertEqual(SUBJECT._target_sysconfig_no_site_facts(
                files, sys_c, False
            ), {})
            self.assertEqual(SUBJECT._target_sysconfig_no_site_facts(
                {**files, "extra.py": b"setattr(sys, '_home', injected)\n"},
                sys_c, True,
            ), {})
            self.assertEqual(SUBJECT._target_sysconfig_no_site_facts(
                files, sys_c + b"_home\n", True
            ), {})

    def test_sysconfig_project_base_env_guard_requires_pinned_config_and_no_override(self):
        source = (
            b"if '_PYTHON_PROJECT_BASE' in os.environ:\n"
            b"    _PROJECT_BASE = os.environ['_PYTHON_PROJECT_BASE']\n"
        )
        config = (
            b'{"os":"linux","architecture":"amd64","config":'
            b'{"Env":["PATH=/usr/local/bin","LANG=C.UTF-8"]}}'
        )
        files = {"sysconfig.py": source}
        patches = (
            patch.object(SUBJECT, "SYSCONFIG_SOURCE_SHA256",
                         hashlib.sha256(source).hexdigest()),
            patch.object(SUBJECT, "TARGET_IMAGE_CONFIG_SHA256",
                         hashlib.sha256(config).hexdigest()),
        )
        with patches[0], patches[1]:
            self.assertEqual(SUBJECT._target_sysconfig_project_base_env_facts(
                files, config, True
            ), (("'_PYTHON_PROJECT_BASE' in os.environ", False),))
            self.assertEqual(SUBJECT._target_sysconfig_project_base_env_facts(
                files, config, False
            ), ())
            with_override = config.replace(
                b"LANG=C.UTF-8", b"_PYTHON_PROJECT_BASE=/tmp/build"
            )
            with patch.object(
                SUBJECT, "TARGET_IMAGE_CONFIG_SHA256",
                hashlib.sha256(with_override).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_sysconfig_project_base_env_facts(
                    files, with_override, True
                ), ())
            wrong_platform = config.replace(b"amd64", b"arm64")
            with patch.object(
                SUBJECT, "TARGET_IMAGE_CONFIG_SHA256",
                hashlib.sha256(wrong_platform).hexdigest(),
            ):
                self.assertEqual(SUBJECT._target_sysconfig_project_base_env_facts(
                    files, wrong_platform, True
                ), ())

    def test_sysconfig_userbase_guard_requires_explicit_clean_environment(self):
        source = (
            b"def _getuserbase():\n"
            b"    env_base = os.environ.get('PYTHONUSERBASE', None)\n"
            b"    if env_base:\n        return env_base\n"
            b"    return None\n"
            b"_HAS_USER_BASE = (_getuserbase() is not None)\n"
        )
        config = (
            b'{"os":"linux","architecture":"amd64","config":'
            b'{"Env":["PATH=/usr/local/bin"]}}'
        )
        files = {"sysconfig.py": source}
        with patch.multiple(
            SUBJECT,
            SYSCONFIG_SOURCE_SHA256=hashlib.sha256(source).hexdigest(),
            TARGET_IMAGE_CONFIG_SHA256=hashlib.sha256(config).hexdigest(),
        ):
            expected = {("sysconfig", "sysconfig.py", 3): (False,)}
            self.assertEqual(
                SUBJECT._target_sysconfig_userbase_env_condition_facts(
                    files, config, True, True,
                ),
                expected,
            )
            self.assertEqual(
                SUBJECT._target_sysconfig_userbase_env_condition_facts(
                    files, config, True, False,
                ),
                {},
            )
            self.assertEqual(
                SUBJECT._target_sysconfig_userbase_env_condition_facts(
                    files, config, False, True,
                ),
                {},
            )
            self.assertEqual(
                SUBJECT._target_sysconfig_userbase_env_condition_facts(
                    {**files, "extra.py": b"os.environ['PYTHONUSERBASE'] = value\n"},
                    config, True, True,
                ),
                {},
            )
            with_userbase = config.replace(
                b'PATH=/usr/local/bin"]',
                b'PATH=/usr/local/bin","PYTHONUSERBASE=/tmp/user"]',
            )
            with patch.object(
                SUBJECT, "TARGET_IMAGE_CONFIG_SHA256",
                hashlib.sha256(with_userbase).hexdigest(),
            ):
                self.assertEqual(
                    SUBJECT._target_sysconfig_userbase_env_condition_facts(
                        files, with_userbase, True, True,
                    ),
                    {},
                )

    def test_importlib_windows_name_fact_requires_digest_and_direct_binding(self):
        source = (
            b"import sys\n"
            b"_MS_WINDOWS = (sys.platform == 'win32')\n"
            b"if _MS_WINDOWS:\n    import nt\n"
        )
        files = {"importlib/_bootstrap_external.py": source}
        with patch.object(
            SUBJECT, "IMPORTLIB_EXTERNAL_SOURCE_SHA256", hashlib.sha256(source).hexdigest()
        ):
            self.assertEqual(
                SUBJECT._target_importlib_windows_name_facts(files),
                {"_MS_WINDOWS": False},
            )
            rebound = source + b"_MS_WINDOWS = True\n"
            with patch.object(
                SUBJECT, "IMPORTLIB_EXTERNAL_SOURCE_SHA256", hashlib.sha256(rebound).hexdigest()
            ):
                self.assertEqual(SUBJECT._target_importlib_windows_name_facts(
                    {"importlib/_bootstrap_external.py": rebound}
                ), {})

    def test_target_byteorder_is_bound_to_linux_amd64_image(self):
        little = ast.parse("sys.byteorder == 'little'", mode="eval").body
        big = ast.parse("sys.byteorder == 'big'", mode="eval").body
        self.assertIs(SUBJECT._target_condition(little), True)
        self.assertIs(SUBJECT._target_condition(big), False)
        self.assertIsNone(SUBJECT._target_condition(
            ast.parse("sys.byteorder is 'little'", mode="eval").body
        ))

        files = {
            "pkg.py": (
                b"import sys\n"
                b"if sys.byteorder == 'little':\n    import little_helper\n"
                b"else:\n    import big_helper\n"
            ),
            "little_helper.py": b"VALUE = 1\n",
            "big_helper.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("little_helper", "pkg"))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})

    def test_literal_false_alias_prunes_only_after_single_static_binding(self):
        files = {
            "pkg.py": (
                b"from provider import *\n_false = 0\n"
                b"if _false:\n    import unreachable\n"
                b"else:\n    import reachable\n"
            ),
            "provider.py": b"VALUE = 0\n",
            "unreachable.py": b"VALUE = 1\n",
            "reachable.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "provider", "reachable"))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})

    def test_literal_false_alias_keeps_guards_unknown_when_reassigned_or_dynamic(self):
        for source in (
            b"if _false:\n    import left\nelse:\n    import right\n_false = 0\n",
            b"_false = 0\nfrom provider import *\n"
            b"if _false:\n    import left\nelse:\n    import right\n",
            b"_false = 0\nglobals()['_false'] = 1\n"
            b"if _false:\n    import left\nelse:\n    import right\n",
            b"_false = 0\n_false = feature_flag\n"
            b"if _false:\n    import left\nelse:\n    import right\n",
        ):
            files = {
                "pkg.py": source,
                "left.py": b"VALUE = 1\n",
                "right.py": b"VALUE = 2\n",
                "provider.py": b"VALUE = 3\n",
            }
            modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
                files, ("pkg",)
            )
            expected = {"left", "pkg", "right"}
            if b"from provider import *" in source:
                expected.add("provider")
            self.assertEqual(set(modules), expected)
            self.assertEqual(conditions, {"resolved": 0, "unknown": 1})

    def test_builtin_module_membership_uses_only_bound_target_facts(self):
        self.assertEqual(len(SUBJECT._TARGET_BUILTIN_MODULE_NAMES), 31)
        self.assertEqual(
            SUBJECT._TARGET_BUILTIN_MODULE_NAMES,
            tuple(sorted(set(SUBJECT._TARGET_BUILTIN_MODULE_NAMES))),
        )
        self.assertEqual(
            set(SUBJECT._TARGET_BUILTIN_MEMBERSHIP),
            {*SUBJECT._TARGET_BUILTIN_MODULE_NAMES, "nt"},
        )
        self.assertEqual(
            SUBJECT._TARGET_BUILTIN_CONFIG_C_SHA256,
            "30d353782cbaf8de2fed2ba82b1040940386e316b7f41604c49f8f3d6f16bb31",
        )
        self.assertEqual(
            SUBJECT._TARGET_BUILTIN_LAYER_SHA256,
            "7f0ea382d75a163999c21529b19913d158821816106eed6f02039f8fdf346779",
        )
        for name in ("gc", "_ast", "marshal", "posix"):
            expression = ast.parse(
                f"{name!r} in sys.builtin_module_names", mode="eval"
            ).body
            self.assertIs(SUBJECT._target_condition(expression), True)
        absent = ast.parse("'nt' in sys.builtin_module_names", mode="eval").body
        future = ast.parse(
            "'future_builtin' in sys.builtin_module_names", mode="eval"
        ).body
        self.assertIs(SUBJECT._target_condition(absent), False)
        absent_complement = ast.parse(
            "'nt' not in sys.builtin_module_names", mode="eval"
        ).body
        present_complement = ast.parse(
            "'gc' not in sys.builtin_module_names", mode="eval"
        ).body
        self.assertIs(SUBJECT._target_condition(absent_complement), True)
        self.assertIs(SUBJECT._target_condition(present_complement), False)
        self.assertIsNone(SUBJECT._target_condition(future))
        equality = ast.parse(
            "sys.builtin_module_names == ('posix',)", mode="eval"
        ).body
        self.assertIsNone(SUBJECT._target_condition(equality))
        files = {
            "pkg.py": (
                b"import sys\n_names = sys.builtin_module_names\n"
                b"if 'posix' in _names:\n    import posix_helper\n"
                b"if 'nt' in _names:\n    import nt_helper\nelse:\n    import no_nt_helper\n"
                b"if 'future_builtin' in _names:\n    import unknown_a\n"
                b"else:\n    import unknown_b\n"
            ),
            "posix_helper.py": b"VALUE = 1\n",
            "nt_helper.py": b"VALUE = 2\n",
            "no_nt_helper.py": b"VALUE = 3\n",
            "unknown_a.py": b"VALUE = 4\n",
            "unknown_b.py": b"VALUE = 5\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(files, ("pkg",))
        self.assertEqual(
            modules,
            ("no_nt_helper", "pkg", "posix_helper", "unknown_a", "unknown_b"),
        )
        self.assertEqual(conditions, {"resolved": 2, "unknown": 1})

    def test_imported_module_name_guards_resolve_only_without_rebinding(self):
        tree = ast.parse(
            "if __name__ == '__main__':\n"
            "    import main_only\n"
            "else:\n"
            "    import imported_only\n"
        )
        known = SUBJECT._target_name_aliases(tree, imported_module_name=True)
        equal = tree.body[0].test
        unequal = ast.parse("__name__ != '__main__'", mode="eval").body
        self.assertIs(SUBJECT._target_condition(equal, known), False)
        self.assertIs(SUBJECT._target_condition(unequal, known), True)

        alias_tree = ast.parse(
            "_entry_name = __name__\n"
            "if _entry_name == '__main__':\n    pass\n"
        )
        self.assertIs(
            SUBJECT._target_condition(
                alias_tree.body[1].test,
                SUBJECT._target_name_aliases(alias_tree, imported_module_name=True),
            ),
            False,
        )

        rebound = ast.parse(
            "if feature_flag:\n    __name__ = '__main__'\n"
            "if __name__ == '__main__':\n    import maybe_main\n"
        )
        self.assertIsNone(
            SUBJECT._target_condition(
                rebound.body[1].test,
                SUBJECT._target_name_aliases(rebound, imported_module_name=True),
            )
        )
        deleted = ast.parse(
            "del __name__\nif __name__ == '__main__':\n    pass\n"
        )
        self.assertIsNone(
            SUBJECT._target_condition(
                deleted.body[1].test,
                SUBJECT._target_name_aliases(deleted, imported_module_name=True),
            )
        )
        for mutation in (
            "globals()['__name__'] = '__main__'\n",
            "exec(\"__name__ = '__main__'\")\n",
        ):
            with self.subTest(mutation=mutation):
                dynamic = ast.parse(
                    mutation + "if __name__ == '__main__':\n    pass\n"
                )
                self.assertIsNone(
                    SUBJECT._target_condition(
                        dynamic.body[-1].test,
                        SUBJECT._target_name_aliases(
                            dynamic, imported_module_name=True
                        ),
                    )
                )
        mixed = ast.parse(
            "__name__ = 'before'\n"
            "_entry_name = __name__\n"
            "globals()['__name__'] = '__main__'\n"
            "if _entry_name == '__main__':\n    pass\n"
        )
        self.assertIsNone(
            SUBJECT._target_condition(
                mixed.body[-1].test,
                SUBJECT._target_name_aliases(mixed, imported_module_name=True),
            )
        )
        dynamic_with_builtin = ast.parse(
            "import sys\n_names = sys.builtin_module_names\n"
            "globals()\nif 'posix' in _names:\n    pass\n"
        )
        self.assertIs(
            SUBJECT._target_condition(
                dynamic_with_builtin.body[-1].test,
                SUBJECT._target_name_aliases(
                    dynamic_with_builtin, imported_module_name=True
                ),
            ),
            True,
        )

        files = {
            "pkg.py": (
                b"if __name__ == '__main__':\n    import main_only\n"
                b"else:\n    import imported_only\n"
            ),
            "main_only.py": b"VALUE = 1\n",
            "imported_only.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("imported_only", "pkg"))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})

        star_import_files = {
            "pkg.py": (
                b"from unknown_provider import *\n"
                b"if __name__ == '__main__':\n    import main_only\n"
                b"else:\n    import imported_only\n"
            ),
            "main_only.py": b"VALUE = 1\n",
            "imported_only.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            star_import_files, ("pkg",)
        )
        self.assertEqual(modules, ("imported_only", "main_only", "pkg"))
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})

        dynamic_namespace_files = {
            "pkg.py": (
                b"globals()['__name__'] = '__main__'\n"
                b"if __name__ == '__main__':\n    import main_only\n"
                b"else:\n    import imported_only\n"
            ),
            "main_only.py": b"VALUE = 1\n",
            "imported_only.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(
            dynamic_namespace_files, ("pkg",)
        )
        self.assertEqual(modules, ("imported_only", "main_only", "pkg"))
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})

    def test_rebound_builtin_alias_does_not_prune_reachable_fallback(self):
        files = {
            "pkg.py": (
                b"import sys\n_names = sys.builtin_module_names\n"
                b"if feature_flag:\n    _names = ()\n"
                b"if 'posix' in _names:\n    import posix_helper\n"
                b"else:\n    import fallback\n"
            ),
            "posix_helper.py": b"VALUE = 1\n",
            "fallback.py": b"VALUE = 2\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(files, ("pkg",))
        self.assertEqual(modules, ("fallback", "pkg", "posix_helper"))
        self.assertEqual(conditions, {"resolved": 0, "unknown": 2})

    def test_star_import_invalidates_builtin_alias_for_later_guards(self):
        files = {
            "pkg.py": (
                b"import sys\n_names = sys.builtin_module_names\n"
                b"from provider import *\n"
                b"if 'posix' in _names:\n    import posix_helper\n"
                b"else:\n    import fallback\n"
            ),
            "provider.py": b"VALUE = 1\n",
            "posix_helper.py": b"VALUE = 2\n",
            "fallback.py": b"VALUE = 3\n",
        }
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(files, ("pkg",))
        self.assertEqual(modules, ("fallback", "pkg", "posix_helper", "provider"))
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})

    def test_star_import_keeps_both_later_function_definitions(self):
        files = {
            "pkg/__init__.py": (
                b"import sys\n_names = sys.builtin_module_names\n"
                b"from provider import *\n"
                b"if 'nt' in _names:\n"
                b"    def boot():\n        from . import nt_helper\n"
                b"else:\n"
                b"    def boot():\n        from . import posix_helper\n"
                b"boot()\n"
            ),
            "provider.py": b"VALUE = 1\n",
            "pkg/nt_helper.py": b"VALUE = 2\n",
            "pkg/posix_helper.py": b"VALUE = 3\n",
        }
        modules, _, _, _, _ = SUBJECT._module_init_call_candidate_closure(files, ("pkg",))
        self.assertEqual(
            modules,
            ("pkg", "pkg.nt_helper", "pkg.posix_helper", "provider"),
        )

    def test_call_closure_follows_called_local_functions_only(self):
        files = {
            "pkg/__init__.py": (
                b"from __future__ import annotations\n"
                b"import sys\n"
                b"def boot(annotation: annotation_helper() = None):\n"
                b"    from . import called\n    helper()\n"
                b"    if sys.platform == 'linux':\n        from . import linux_helper\n"
                b"    if feature_flag:\n        from . import unknown_a\n"
                b"    else:\n        from . import unknown_b\n"
                b"    local_annotation: annotation_helper()\n"
                b"def helper():\n    from . import nested\n"
                b"def annotation_helper():\n    from . import annotation_only\n"
                b"def unused():\n    from . import unused_only\n"
                b"if sys.platform == 'linux':\n"
                b"    def block_boot():\n        from . import block_helper\n"
                b"else:\n    def block_boot():\n        from . import block_wrong\n"
                b"if feature_flag:\n"
                b"    def branch_boot():\n        from . import branch_left\n"
                b"else:\n    def branch_boot():\n        from . import branch_right\n"
                b"class Local:\n"
                b"    class_annotation: annotation_helper()\n"
                b"    def class_boot():\n        from . import class_helper\n"
                b"    class_boot()\n"
                b"def lambda_helper():\n    from . import lambda_only\n"
                b"lambda_value = lambda value=lambda_helper(): value\n"
                b"def nested_outer():\n"
                b"    def nested_helper():\n        from . import nested_closure\n"
                b"    def nested_inner():\n        nested_helper()\n"
                b"    nested_inner()\n"
                b"module_annotation: annotation_helper()\n"
                b"block_boot()\n"
                b"branch_boot()\n"
                b"nested_outer()\n"
                b"boot()\n"
            ),
            "pkg/called.py": b"VALUE = 1\n",
            "pkg/linux_helper.py": b"VALUE = 2\n",
            "pkg/unknown_a.py": b"VALUE = 3\n",
            "pkg/unknown_b.py": b"VALUE = 4\n",
            "pkg/nested.py": b"VALUE = 5\n",
            "pkg/block_helper.py": b"VALUE = 8\n",
            "pkg/block_wrong.py": b"VALUE = 11\n",
            "pkg/branch_left.py": b"VALUE = 12\n",
            "pkg/branch_right.py": b"VALUE = 13\n",
            "pkg/class_helper.py": b"VALUE = 9\n",
            "pkg/lambda_only.py": b"VALUE = 10\n",
            "pkg/nested_closure.py": b"VALUE = 14\n",
            "pkg/annotation_only.py": b"VALUE = 7\n",
            "pkg/unused_only.py": b"VALUE = 6\n",
        }
        modules, edges, function_count, digest, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",),
            known_call_facts=(("sys.platform", "linux"),),
        )
        self.assertEqual(
            modules,
            ("pkg", "pkg.block_helper", "pkg.branch_left", "pkg.branch_right", "pkg.called",
             "pkg.class_helper", "pkg.lambda_only", "pkg.linux_helper", "pkg.nested",
             "pkg.nested_closure", "pkg.unknown_a", "pkg.unknown_b"),
        )
        self.assertEqual(edges, 22)
        self.assertEqual(function_count, 10)
        self.assertEqual(len(digest), 64)
        self.assertEqual(conditions, {"resolved": 2, "unknown": 2})

    def test_call_closure_binds_literal_arguments_per_invocation(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose(True)\nchoose(False)\nchoose(True)\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        resolved = []
        modules, edges, function_count, _, conditions = (
            SUBJECT._module_init_call_candidate_closure(
                files, ("pkg",), unknown_conditions=unknown,
                resolved_conditions=resolved,
            )
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(function_count, 1)
        self.assertEqual(edges, 4)
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})
        self.assertEqual(unknown, [])
        self.assertEqual(resolved[0]["decisions"], [False, True])

    def test_call_closure_binds_boolean_not_literal_arguments(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose(not False)\nchoose(not True)\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        resolved = []
        modules, edges, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), resolved_conditions=resolved,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(edges, 4)
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})
        self.assertEqual(resolved[0]["decisions"], [False, True])

    def test_call_closure_binds_boolean_not_default_and_keeps_dynamic_unknown(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled=not True):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose()\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        resolved = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), resolved_conditions=resolved,
        )
        self.assertEqual(modules, ("pkg", "pkg.disabled_branch"))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})
        self.assertEqual(resolved[0]["decisions"], [False])

        files["pkg/__init__.py"] = (
            b"def choose(enabled):\n"
            b"    if enabled:\n        from . import enabled_branch\n"
            b"    else:\n        from . import disabled_branch\n"
            b"choose(not runtime_value)\n"
        )
        unknown = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        self.assertEqual(unknown[0]["expression"], "enabled")

    def test_call_closure_binds_primitive_equality_arguments(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose(1 == True)\nchoose('x' != 'x')\n"
                b"choose(1 == runtime_value)\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        modules, edges, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(edges, 4)
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        self.assertEqual(unknown[0]["expression"], "enabled")

    def test_call_closure_binds_primitive_equality_in_defaults(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled=(2 == 3)):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose()\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        resolved = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), resolved_conditions=resolved,
        )
        self.assertEqual(modules, ("pkg", "pkg.disabled_branch"))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})
        self.assertEqual(resolved[0]["decisions"], [False])

    def test_call_closure_binds_singleton_identity_arguments(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose(None is None)\n"
                b"choose(True is not False)\n"
                b"choose(None is True)\n"
                b"choose(runtime_value is None)\n"
                b"choose((True,) is (True,))\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        modules, edges, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(edges, 4)
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        self.assertEqual(len(unknown), 1)
        self.assertTrue(all(item["expression"] == "enabled" for item in unknown))
        function = ast.parse("def choose(enabled): pass").body[0]
        for expression in ("runtime_value is None", "(True,) is (True,)"):
            call = ast.parse(f"choose({expression})").body[0].value
            facts = dict(SUBJECT._static_literal_call_facts(function, call))
            self.assertIs(facts["enabled"], SUBJECT._UNKNOWN)

    def test_call_closure_binds_singleton_identity_defaults(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled=True is not False):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose()\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        resolved = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), resolved_conditions=resolved,
        )
        self.assertEqual(modules, ("pkg", "pkg.enabled_branch"))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})
        self.assertEqual(resolved[0]["decisions"], [True])

    def test_call_closure_binds_tuple_membership_arguments(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose(1 in (1, 2))\n"
                b"choose('z' not in ('x', 'y'))\n"
                b"choose(2 not in (1, 2))\n"
                b"choose(runtime_value in (1, 2))\n"
                b"choose(1 in runtime_values)\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        modules, edges, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(edges, 4)
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        self.assertEqual(len(unknown), 1)
        function = ast.parse("def choose(enabled): pass").body[0]
        for expression in (
                "runtime_value in (1, 2)", "1 in runtime_values"):
            call = ast.parse(f"choose({expression})").body[0].value
            facts = dict(SUBJECT._static_literal_call_facts(function, call))
            self.assertIs(facts["enabled"], SUBJECT._UNKNOWN)

    def test_call_closure_binds_tuple_membership_defaults(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled='a' in ('a', 'b')):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose()\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        resolved = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), resolved_conditions=resolved,
        )
        self.assertEqual(modules, ("pkg", "pkg.enabled_branch"))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})
        self.assertEqual(resolved[0]["decisions"], [True])

    def test_call_closure_binds_conditional_literal_arguments(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose(True if True else runtime_value)\n"
                b"choose(False if True else True)\n"
                b"choose(True if runtime_test else False)\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        modules, edges, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(edges, 4)
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        self.assertEqual(len(unknown), 1)
        function = ast.parse("def choose(enabled): pass").body[0]
        for expression in (
                "True if runtime_test else False",
                "True if False else runtime_value"):
            call = ast.parse(f"choose({expression})").body[0].value
            facts = dict(SUBJECT._static_literal_call_facts(function, call))
            self.assertIs(facts["enabled"], SUBJECT._UNKNOWN)

    def test_call_closure_binds_conditional_literal_defaults(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled=True if 0 else False):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose()\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        resolved = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), resolved_conditions=resolved,
        )
        self.assertEqual(modules, ("pkg", "pkg.disabled_branch"))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})
        self.assertEqual(resolved[0]["decisions"], [False])

    def test_call_closure_binds_literal_comparison_chains(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose(1 == 1 == 1)\n"
                b"choose(1 == 1 == 2)\n"
                b"choose(1 == 2 == runtime_value)\n"
                b"choose(1 == 1 == runtime_value)\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        modules, edges, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(edges, 4)
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        function = ast.parse("def choose(enabled): pass").body[0]
        for expression in (
                "1 == 1 == runtime_value", "1 == 1 is runtime_value"):
            call = ast.parse(f"choose({expression})").body[0].value
            facts = dict(SUBJECT._static_literal_call_facts(function, call))
            self.assertIs(facts["enabled"], SUBJECT._UNKNOWN)

    def test_call_closure_binds_literal_comparison_chain_defaults(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled=None is None is not False):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose()\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        resolved = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), resolved_conditions=resolved,
        )
        self.assertEqual(modules, ("pkg", "pkg.enabled_branch"))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})
        self.assertEqual(resolved[0]["decisions"], [True])

    def test_call_closure_binds_boolean_literals_with_short_circuit(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose(True and True)\n"
                b"choose(False or False)\n"
                b"choose(False and runtime_value)\n"
                b"choose(True or runtime_value)\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        resolved = []
        modules, edges, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), resolved_conditions=resolved,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(edges, 4)
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})
        self.assertEqual(resolved[0]["decisions"], [False, True])

    def test_call_closure_does_not_simplify_boolean_ops_with_dynamic_left_operand(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose(runtime_value and False)\n"
                b"choose(runtime_value or True)\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        modules, edges, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(edges, 4)
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        self.assertEqual(unknown[0]["expression"], "enabled")

    def test_call_closure_binds_unary_numeric_literals(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose(not -1)\nchoose(not +0)\n"
                b"choose(not -runtime_value)\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        modules, edges, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(edges, 4)
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        self.assertEqual(unknown[0]["expression"], "enabled")

    def test_call_closure_binds_unary_numeric_defaults(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled=not -0):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose()\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        resolved = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), resolved_conditions=resolved,
        )
        self.assertEqual(modules, ("pkg", "pkg.enabled_branch"))
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})
        self.assertEqual(resolved[0]["decisions"], [True])

    def test_call_closure_keeps_unknown_context_when_other_call_is_literal(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose(True)\nchoose(runtime_value)\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        self.assertEqual(len(unknown), 1)
        self.assertEqual(unknown[0]["expression"], "enabled")

    def test_call_closure_does_not_bind_arguments_after_function_rebinding(self):
        files = {
            "pkg/__init__.py": (
                b"def choose(enabled):\n"
                b"    if enabled:\n        from . import enabled_branch\n"
                b"    else:\n        from . import disabled_branch\n"
                b"choose = runtime_function\n"
                b"choose(True)\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        self.assertEqual(len(unknown), 1)
        self.assertEqual(unknown[0]["expression"], "enabled")

    def test_call_closure_does_not_bind_arguments_after_method_rebinding(self):
        files = {
            "pkg/__init__.py": (
                b"class Loader:\n"
                b"    def start(self, enabled=True):\n"
                b"        if enabled:\n            from . import enabled_branch\n"
                b"        else:\n            from . import disabled_branch\n"
                b"Loader.start = runtime_method\n"
                b"Loader().start()\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        self.assertEqual(len(unknown), 1)
        self.assertEqual(unknown[0]["expression"], "enabled")

    def test_call_closure_rejects_qualified_dynamic_method_rebinding(self):
        files = {
            "pkg/__init__.py": (
                b"import builtins as runtime\n"
                b"class Loader:\n"
                b"    def start(self, enabled=True):\n"
                b"        if enabled:\n            from . import enabled_branch\n"
                b"        else:\n            from . import disabled_branch\n"
                b"runtime.setattr(Loader, 'start', runtime_method)\n"
                b"Loader().start()\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        self.assertEqual(len(unknown), 1)
        self.assertEqual(unknown[0]["expression"], "enabled")

    def test_call_closure_binds_bound_method_default_arguments(self):
        files = {
            "pkg/__init__.py": (
                b"class Loader:\n"
                b"    def start(self, enabled=False):\n"
                b"        if enabled:\n            from . import enabled_branch\n"
                b"        else:\n            from . import disabled_branch\n"
                b"Loader().start()\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        modules, _, function_count, _, conditions = (
            SUBJECT._module_init_call_candidate_closure(
                files, ("pkg",), unknown_conditions=unknown,
            )
        )
        self.assertEqual(modules, ("pkg", "pkg.disabled_branch"))
        self.assertEqual(function_count, 1)
        self.assertEqual(conditions, {"resolved": 1, "unknown": 0})
        self.assertEqual(unknown, [])

    def test_call_context_limit_falls_back_to_both_unknown_branches(self):
        calls = "".join(f"choose({value})\n" for value in range(9))
        files = {
            "pkg/__init__.py": (
                b"def choose(value):\n"
                b"    if value == 8:\n        from . import matching\n"
                b"    else:\n        from . import other\n"
            ) + calls.encode("ascii"),
            "pkg/matching.py": b"VALUE = 8\n",
            "pkg/other.py": b"VALUE = 0\n",
        }
        unknown = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, ("pkg", "pkg.matching", "pkg.other"))
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        self.assertEqual(len(unknown), 1)
        self.assertEqual(unknown[0]["expression"], "value == 8")

    def test_decorated_method_argument_binding_fails_closed(self):
        files = {
            "pkg/__init__.py": (
                b"class Loader:\n"
                b"    @staticmethod\n"
                b"    def start(enabled=True):\n"
                b"        if enabled:\n            from . import enabled_branch\n"
                b"        else:\n            from . import disabled_branch\n"
                b"Loader().start()\n"
            ),
            "pkg/enabled_branch.py": b"VALUE = True\n",
            "pkg/disabled_branch.py": b"VALUE = False\n",
        }
        unknown = []
        modules, _, _, _, conditions = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",), unknown_conditions=unknown,
        )
        self.assertEqual(modules, (
            "pkg", "pkg.disabled_branch", "pkg.enabled_branch",
        ))
        self.assertEqual(conditions, {"resolved": 0, "unknown": 1})
        self.assertEqual(len(unknown), 1)

    def test_literal_call_binding_respects_explicit_unknowns_and_call_shapes(self):
        function = ast.parse(
            "def check(value=True, *, second=False):\n    pass\n"
        ).body[0]
        explicit_none = ast.parse("check(None, second=True)").body[0].value
        starred = ast.parse("check(*values)").body[0].value
        self.assertEqual(
            dict(SUBJECT._static_literal_call_facts(function, explicit_none)),
            {"value": None, "second": True},
        )
        unknown_facts = dict(SUBJECT._static_literal_call_facts(function, starred))
        self.assertIs(unknown_facts["value"], SUBJECT._UNKNOWN)
        self.assertIs(unknown_facts["second"], SUBJECT._UNKNOWN)

    def test_function_local_annotations_are_not_evaluated_without_future_import(self):
        files = {
            "pkg/__init__.py": (
                b"def boot():\n    local_value: annotation_helper()\n"
                b"    from . import called\n"
                b"def annotation_helper():\n    from . import annotation_only\n"
                b"boot()\n"
            ),
            "pkg/called.py": b"VALUE = 1\n",
            "pkg/annotation_only.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(files, ("pkg",))
        self.assertEqual(modules, ("pkg", "pkg.called"))
        self.assertEqual(function_count, 1)

    def test_calls_in_generator_expressions_are_kept_as_candidates(self):
        files = {
            "pkg/__init__.py": (
                b"def load():\n    from . import deferred_helper\n"
                b"tuple(load() for holder[load()] in ())\n"
            ),
            "pkg/deferred_helper.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.deferred_helper"))
        self.assertEqual(function_count, 1)

    def test_simple_same_scope_function_aliases_are_followed(self):
        files = {
            "pkg/__init__.py": (
                b"def load():\n    from . import alias_helper\n"
                b"module_alias = load\nmodule_alias()\n"
                b"class Holder:\n    class_alias = load\n    class_alias()\n"
                b"def boot():\n    local_alias = load\n    local_alias()\n"
                b"boot()\n"
            ),
            "pkg/alias_helper.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.alias_helper"))
        self.assertEqual(function_count, 2)

    def test_class_alias_uses_outer_binding_before_local_shadow(self):
        files = {
            "pkg/__init__.py": (
                b"def load():\n    from . import outer_helper\n"
                b"class Holder:\n"
                b"    alias = load\n"
                b"    def load():\n        from . import class_helper\n"
                b"    alias()\n"
            ),
            "pkg/outer_helper.py": b"VALUE = 1\n",
            "pkg/class_helper.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.outer_helper"))
        self.assertEqual(function_count, 1)

    def test_unknown_class_branch_preserves_both_function_targets(self):
        files = {
            "pkg/__init__.py": (
                b"class Holder:\n"
                b"    if feature_flag:\n"
                b"        def boot():\n            from . import left_helper\n"
                b"    else:\n"
                b"        def boot():\n            from . import right_helper\n"
                b"    boot()\n"
            ),
            "pkg/left_helper.py": b"VALUE = 1\n",
            "pkg/right_helper.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.left_helper", "pkg.right_helper"))
        self.assertEqual(function_count, 2)

    def test_direct_local_class_method_call_is_followed(self):
        files = {
            "pkg/__init__.py": (
                b"class Service:\n"
                b"    @staticmethod\n"
                b"    def initialize():\n        from . import method_helper\n"
                b"Service.initialize()\n"
            ),
            "pkg/method_helper.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.method_helper"))
        self.assertEqual(function_count, 1)

    def test_called_imported_class_alias_method_adds_its_imports(self):
        files = {
            "pkg/__init__.py": b"from .helper import Worker as Alias\nAlias.run()\n",
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper", "pkg.method_leaf"))
        self.assertEqual(function_count, 1)

    def test_imported_class_alias_chains_follow_constructor_and_method(self):
        files = {
            "pkg/__init__.py": (
                b"from .helper import Worker as Alias\n"
                b"FirstAlias = Alias\nSecondAlias = FirstAlias\n"
                b"SecondAlias()\nSecondAlias().run()\n"
            ),
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def __init__(self):\n        from . import init_leaf\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/init_leaf.py": b"VALUE = 1\n",
            "pkg/method_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.helper", "pkg.init_leaf", "pkg.method_leaf")
        )
        self.assertEqual(function_count, 2)

    def test_qualified_imported_class_aliases_follow_module_aliases(self):
        entries = (
            b"import pkg.helper as helper\n"
            b"Alias = helper.Worker\nChained = Alias\n"
            b"Chained()\nChained().run()\n",
            b"import pkg.helper\n"
            b"Alias = pkg.helper.Worker\nAlias()\nAlias().run()\n",
        )
        for entry in entries:
            with self.subTest(entry=entry):
                files = {
                    "pkg/__init__.py": entry,
                    "pkg/helper.py": (
                        b"class Worker:\n"
                        b"    def __init__(self):\n        from . import init_leaf\n"
                        b"    def run(self):\n        from . import method_leaf\n"
                    ),
                    "pkg/init_leaf.py": b"VALUE = 1\n",
                    "pkg/method_leaf.py": b"VALUE = 2\n",
                }
                modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
                    files, ("pkg",)
                )
                self.assertEqual(
                    modules,
                    ("pkg", "pkg.helper", "pkg.init_leaf", "pkg.method_leaf"),
                )
                self.assertEqual(function_count, 2)

    def test_qualified_class_alias_keeps_imported_function_entry(self):
        files = {
            "consumer/__init__.py": b"from .helper import start\nstart()\n",
            "consumer/helper.py": (
                b"import pkg.worker as worker\n"
                b"Alias = worker.Worker\n"
                b"def start():\n"
                b"    from . import started\n"
                b"    Alias().run()\n"
            ),
            "consumer/started.py": b"VALUE = 1\n",
            "pkg/__init__.py": b"",
            "pkg/worker.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 2\n",
        }
        modules, _, _, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("consumer",)
        )
        self.assertEqual(
            modules,
            ("consumer", "consumer.helper", "consumer.started", "pkg",
             "pkg.method_leaf", "pkg.worker"),
        )

    def test_local_class_aliases_follow_constructors_and_methods(self):
        files = {
            "pkg/__init__.py": (
                b"class Worker:\n"
                b"    def __init__(self):\n        from . import init_leaf\n"
                b"    def run(self):\n        from . import method_leaf\n"
                b"WorkerAlias = Worker\n"
                b"ChainedAlias = WorkerAlias\n"
                b"ChainedAlias()\nChainedAlias().run()\n"
            ),
            "pkg/init_leaf.py": b"VALUE = 1\n",
            "pkg/method_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.init_leaf", "pkg.method_leaf")
        )
        self.assertEqual(function_count, 2)

    def test_local_class_aliases_preserve_alternatives_and_reject_dynamic_values(self):
        files = {
            "pkg/__init__.py": (
                b"class First:\n"
                b"    def run(self):\n        from . import first_leaf\n"
                b"class Second:\n"
                b"    def run(self):\n        from . import second_leaf\n"
                b"if choice:\n    Candidate = First\n"
                b"else:\n    Candidate = Second\n"
                b"Candidate().run()\n"
                b"def make_worker():\n    return First()\n"
                b"FactoryAlias = make_worker\nFactoryAlias()\n"
                b"CycleA = CycleB\nCycleB = CycleA\nCycleA()\n"
            ),
            "pkg/first_leaf.py": b"VALUE = 1\n",
            "pkg/second_leaf.py": b"VALUE = 2\n",
        }
        modules, _, _, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.first_leaf", "pkg.second_leaf")
        )

    def test_local_class_rebinding_preserves_imported_class_alias_targets(self):
        files = {
            "pkg/__init__.py": (
                b"from .helper import Remote as Candidate\n"
                b"class Local:\n"
                b"    def run(self):\n        from . import local_leaf\n"
                b"if choice:\n    Candidate = Local\n"
                b"Candidate().run()\n"
            ),
            "pkg/helper.py": (
                b"class Remote:\n"
                b"    def run(self):\n        from . import remote_leaf\n"
            ),
            "pkg/local_leaf.py": b"VALUE = 1\n",
            "pkg/remote_leaf.py": b"VALUE = 2\n",
        }
        modules, _, _, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules,
            ("pkg", "pkg.helper", "pkg.local_leaf", "pkg.remote_leaf"),
        )

    def test_imported_class_aliases_preserve_unknown_branch_alternatives(self):
        files = {
            "pkg/__init__.py": (
                b"from .helper import First, Second\n"
                b"if class_choice:\n    Candidate = First\n"
                b"else:\n    Candidate = Second\n"
                b"Candidate()\n"
            ),
            "pkg/helper.py": (
                b"class First:\n"
                b"    def __init__(self):\n        from . import first_leaf\n"
                b"class Second:\n"
                b"    def __init__(self):\n        from . import second_leaf\n"
            ),
            "pkg/first_leaf.py": b"VALUE = 1\n",
            "pkg/second_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.first_leaf", "pkg.helper", "pkg.second_leaf")
        )
        self.assertEqual(function_count, 2)

    def test_function_scope_alias_of_imported_class_follows_method(self):
        files = {
            "pkg/__init__.py": (
                b"from .worker import Worker\n"
                b"def boot():\n    LocalWorker = Worker\n    LocalWorker().run()\n"
                b"boot()\n"
            ),
            "pkg/worker.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.method_leaf", "pkg.worker"))
        self.assertEqual(function_count, 2)

    def test_function_scope_class_alias_chain_preserves_imported_targets(self):
        files = {
            "pkg/__init__.py": (
                b"from .worker import Worker\n"
                b"def boot():\n    First = Worker\n    Second = First\n    Second().run()\n"
                b"boot()\n"
            ),
            "pkg/worker.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.method_leaf", "pkg.worker"))
        self.assertEqual(function_count, 2)

    def test_called_nested_function_inherits_imported_class_alias_closure(self):
        files = {
            "pkg/__init__.py": (
                b"from .worker import Worker\n"
                b"def boot():\n"
                b"    LocalWorker = Worker\n"
                b"    ChainedWorker = LocalWorker\n"
                b"    def invoke():\n        ChainedWorker().run()\n"
                b"    invoke()\n"
                b"boot()\n"
            ),
            "pkg/worker.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.method_leaf", "pkg.worker"))
        self.assertEqual(function_count, 3)

    def test_uninvoked_nested_function_does_not_add_closure_imports(self):
        files = {
            "pkg/__init__.py": (
                b"from .worker import Worker\n"
                b"def boot():\n"
                b"    LocalWorker = Worker\n"
                b"    def unused():\n        LocalWorker().run()\n"
                b"boot()\n"
            ),
            "pkg/worker.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.worker"))
        self.assertEqual(function_count, 1)

    def test_class_scope_alias_of_imported_class_follows_method(self):
        files = {
            "pkg/__init__.py": (
                b"from .worker import Worker\n"
                b"class Holder:\n    LocalWorker = Worker\n    LocalWorker().run()\n"
            ),
            "pkg/worker.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.method_leaf", "pkg.worker"))
        self.assertEqual(function_count, 1)

    def test_class_scope_alias_chain_preserves_imported_targets(self):
        files = {
            "pkg/__init__.py": (
                b"from .worker import Worker\n"
                b"class Holder:\n    First = Worker\n    Second = First\n    Second().run()\n"
            ),
            "pkg/worker.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.method_leaf", "pkg.worker"))
        self.assertEqual(function_count, 1)

    def test_class_alias_is_not_treated_as_method_lexical_closure(self):
        files = {
            "pkg/__init__.py": (
                b"from .worker import Worker\n"
                b"class Holder:\n"
                b"    ClassWorker = Worker\n"
                b"    def invoke(self):\n        ClassWorker().run()\n"
                b"Holder().invoke()\n"
            ),
            "pkg/worker.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.worker"))
        self.assertEqual(function_count, 1)

    def test_imported_class_alias_cycles_and_factories_are_not_guessed(self):
        files = {
            "pkg/__init__.py": (
                b"from .helper import Worker as Known\n"
                b"def choose_class():\n    return Known\n"
                b"FirstAlias = SecondAlias\nSecondAlias = FirstAlias\n"
                b"DynamicAlias = choose_class()\n"
                b"FirstAlias()\nDynamicAlias()\n"
            ),
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper"))
        self.assertEqual(function_count, 1)

    def test_imported_module_class_method_adds_its_imports(self):
        files = {
            "pkg/__init__.py": b"import pkg.helper as helper\nhelper.Worker.run()\n",
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper", "pkg.method_leaf"))
        self.assertEqual(function_count, 1)

    def test_imported_class_constructor_adds_init_imports(self):
        files = {
            "pkg/__init__.py": b"from .helper import Worker as Alias\nAlias()\n",
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def __init__(self):\n        from . import init_leaf\n"
            ),
            "pkg/init_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper", "pkg.init_leaf"))
        self.assertEqual(function_count, 1)

    def test_imported_subclass_follows_same_module_base_constructor_and_method(self):
        files = {
            "pkg/__init__.py": (
                b"from .helper import Worker as Alias\n"
                b"Alias()\nAlias().run()\n"
            ),
            "pkg/helper.py": (
                b"class Base:\n"
                b"    def __init__(self):\n        from . import init_leaf\n"
                b"    def run(self):\n        from . import method_leaf\n"
                b"class Worker(Base):\n    pass\n"
            ),
            "pkg/init_leaf.py": b"VALUE = 1\n",
            "pkg/method_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.helper", "pkg.init_leaf", "pkg.method_leaf")
        )
        self.assertEqual(function_count, 2)

    def test_imported_module_subclass_follows_same_module_base_methods(self):
        files = {
            "pkg/__init__.py": (
                b"import pkg.helper as helper\n"
                b"helper.Worker()\nhelper.Worker().run()\n"
            ),
            "pkg/helper.py": (
                b"class Base:\n"
                b"    def __init__(self):\n        from . import init_leaf\n"
                b"    def run(self):\n        from . import method_leaf\n"
                b"class Worker(Base):\n    pass\n"
            ),
            "pkg/init_leaf.py": b"VALUE = 1\n",
            "pkg/method_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.helper", "pkg.init_leaf", "pkg.method_leaf")
        )
        self.assertEqual(function_count, 2)

    def test_imported_subclass_with_dynamic_base_does_not_guess_inherited_method(self):
        files = {
            "pkg/__init__.py": (
                b"from .helper import Worker\nWorker().run()\n"
            ),
            "pkg/helper.py": (
                b"class Base:\n"
                b"    def run(self):\n        from . import method_leaf\n"
                b"def choose_base():\n    return Base\n"
                b"class Worker(choose_base()):\n    pass\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper"))
        self.assertEqual(function_count, 1)

    def test_imported_subclass_follows_source_base_from_another_module(self):
        fixtures = (
            (
                b"from .helper import Worker as Alias\nAlias()\nAlias().run()\n",
                b"from .base import Base\nclass Worker(Base):\n    pass\n",
            ),
            (
                b"import pkg.helper as helper\n"
                b"helper.Worker()\nhelper.Worker().run()\n",
                b"from . import base as source\n"
                b"class Worker(source.Base):\n    pass\n",
            ),
        )
        for entry, helper in fixtures:
            with self.subTest(entry=entry):
                files = {
                    "pkg/__init__.py": entry,
                    "pkg/helper.py": helper,
                    "pkg/base.py": (
                        b"class Base:\n"
                        b"    def __init__(self):\n        from . import init_leaf\n"
                        b"    def run(self):\n        from . import method_leaf\n"
                    ),
                    "pkg/init_leaf.py": b"VALUE = 1\n",
                    "pkg/method_leaf.py": b"VALUE = 2\n",
                }
                modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
                    files, ("pkg",)
                )
                self.assertEqual(
                    modules,
                    ("pkg", "pkg.base", "pkg.helper", "pkg.init_leaf", "pkg.method_leaf"),
                )
                self.assertEqual(function_count, 2)

    def test_uncalled_imported_class_method_does_not_expand_body(self):
        files = {
            "pkg/__init__.py": b"from .helper import Worker as Alias\n",
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper"))
        self.assertEqual(function_count, 0)

    def test_from_import_module_alias_follows_source_function(self):
        files = {
            "pkg/__init__.py": b"from . import helper as h\nh.boot()\n",
            "pkg/helper.py": b"def boot():\n    from . import leaf\n",
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper", "pkg.leaf"))
        self.assertEqual(function_count, 1)

    def test_from_import_module_alias_follows_class_method(self):
        files = {
            "pkg/__init__.py": b"from . import helper as h\nh.Worker.run()\n",
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import leaf\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper", "pkg.leaf"))
        self.assertEqual(function_count, 1)

    def test_from_import_module_alias_follows_class_constructor(self):
        files = {
            "pkg/__init__.py": b"from . import helper as h\nh.Worker()\n",
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def __init__(self):\n        from . import leaf\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper", "pkg.leaf"))
        self.assertEqual(function_count, 1)

    def test_constructed_imported_class_method_is_followed(self):
        files = {
            "pkg/__init__.py": (
                b"from .helper import Worker as Alias\nAlias().run()\n"
            ),
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def __init__(self):\n        from . import init_leaf\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/init_leaf.py": b"VALUE = 1\n",
            "pkg/method_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.helper", "pkg.init_leaf", "pkg.method_leaf")
        )
        self.assertEqual(function_count, 2)

    def test_constructed_module_alias_class_method_is_followed(self):
        files = {
            "pkg/__init__.py": (
                b"from . import helper as h\nh.Worker().run()\n"
            ),
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def __init__(self):\n        from . import init_leaf\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/init_leaf.py": b"VALUE = 1\n",
            "pkg/method_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.helper", "pkg.init_leaf", "pkg.method_leaf")
        )
        self.assertEqual(function_count, 2)

    def test_constructed_local_class_method_is_followed(self):
        files = {
            "pkg/__init__.py": (
                b"class Worker:\n"
                b"    def __init__(self):\n        from . import init_leaf\n"
                b"    def run(self):\n        from . import method_leaf\n"
                b"Worker().run()\n"
            ),
            "pkg/init_leaf.py": b"VALUE = 1\n",
            "pkg/method_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.init_leaf", "pkg.method_leaf"))
        self.assertEqual(function_count, 2)

    def test_direct_imported_class_factory_return_tracks_method(self):
        files = {
            "pkg/__init__.py": (
                b"def make():\n    from . import helper\n    return helper.Worker()\n"
                b"worker = make()\ninstance = worker\ninstance.run()\n"
            ),
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper", "pkg.method_leaf"))
        self.assertEqual(function_count, 2)

    def test_factory_local_instance_assignment_tracks_direct_return(self):
        files = {
            "pkg/__init__.py": (
                b"def make():\n    from . import helper\n"
                b"    worker = helper.Worker()\n    return worker\n"
                b"worker = make()\nworker.run()\n"
            ),
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper", "pkg.method_leaf"))
        self.assertEqual(function_count, 2)

    def test_simple_conditional_factory_returns_keep_both_method_candidates(self):
        files = {
            "pkg/__init__.py": (
                b"def make(flag):\n"
                b"    if flag:\n        return Worker()\n"
                b"    return Other()\n"
                b"class Worker:\n    def run(self):\n        from . import worker_leaf\n"
                b"class Other:\n    def run(self):\n        from . import other_leaf\n"
                b"make(flag).run()\n"
            ),
            "pkg/worker_leaf.py": b"VALUE = 1\n",
            "pkg/other_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.other_leaf", "pkg.worker_leaf"))
        self.assertEqual(function_count, 3)

    def test_same_scope_local_class_instance_method_is_followed(self):
        files = {
            "pkg/__init__.py": (
                b"class Worker:\n"
                b"    def __init__(self):\n        from . import init_leaf\n"
                b"    def run(self):\n        from . import method_leaf\n"
                b"worker = Worker()\nworker.run()\n"
            ),
            "pkg/init_leaf.py": b"VALUE = 1\n",
            "pkg/method_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.init_leaf", "pkg.method_leaf"))
        self.assertEqual(function_count, 2)

    def test_same_scope_imported_class_instance_method_is_followed(self):
        files = {
            "pkg/__init__.py": (
                b"from .helper import Worker as Alias\nworker = Alias()\nworker.run()\n"
            ),
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def __init__(self):\n        from . import init_leaf\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/init_leaf.py": b"VALUE = 1\n",
            "pkg/method_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.helper", "pkg.init_leaf", "pkg.method_leaf")
        )
        self.assertEqual(function_count, 2)

    def test_same_scope_imported_module_class_instance_method_is_followed(self):
        files = {
            "pkg/__init__.py": (
                b"from . import helper as h\nworker = h.Worker()\nworker.run()\n"
            ),
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def __init__(self):\n        from . import init_leaf\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/init_leaf.py": b"VALUE = 1\n",
            "pkg/method_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.helper", "pkg.init_leaf", "pkg.method_leaf")
        )
        self.assertEqual(function_count, 2)

    def test_same_scope_simple_instance_alias_is_followed(self):
        files = {
            "pkg/__init__.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
                b"worker = Worker()\ninstance = worker\ninstance.run()\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.method_leaf"))
        self.assertEqual(function_count, 1)

    def test_same_scope_imported_class_instance_alias_is_followed(self):
        files = {
            "pkg/__init__.py": (
                b"from .helper import Worker as Alias\n"
                b"worker = Alias()\ninstance = worker\ninstance.run()\n"
            ),
            "pkg/helper.py": (
                b"class Worker:\n"
                b"    def run(self):\n        from . import method_leaf\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper", "pkg.method_leaf"))
        self.assertEqual(function_count, 1)

    def test_local_subclass_constructor_follows_inherited_init(self):
        files = {
            "pkg/__init__.py": (
                b"class Base:\n"
                b"    def __init__(self):\n        from . import init_leaf\n"
                b"class Worker(Base):\n    pass\n"
                b"Worker()\n"
            ),
            "pkg/init_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.init_leaf"))
        self.assertEqual(function_count, 1)

    def test_constructed_subclass_follows_inherited_method(self):
        files = {
            "pkg/__init__.py": (
                b"class Base:\n"
                b"    def load(self):\n        from . import method_leaf\n"
                b"class Worker(Base):\n    pass\n"
                b"Worker().load()\n"
            ),
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.method_leaf"))
        self.assertEqual(function_count, 1)

    def test_constructed_subclass_follows_imported_base_method(self):
        files = {
            "pkg/__init__.py": (
                b"from .base import Base\n"
                b"class Worker(Base):\n    pass\n"
                b"worker = Worker()\nworker.load()\n"
            ),
            "pkg/base.py": (
                b"class Base:\n"
                b"    def __init__(self):\n        from . import init_leaf\n"
                b"    def load(self):\n        from . import method_leaf\n"
            ),
            "pkg/init_leaf.py": b"VALUE = 2\n",
            "pkg/method_leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.base", "pkg.init_leaf", "pkg.method_leaf")
        )
        self.assertEqual(function_count, 2)

    def test_instance_method_call_on_bound_receiver_is_followed(self):
        files = {
            "pkg/__init__.py": (
                b"class Worker:\n"
                b"    def boot(self):\n        self.load()\n"
                b"    def load(self):\n        from . import leaf\n"
                b"Worker().boot()\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.leaf"))
        self.assertEqual(function_count, 2)

    def test_classmethod_call_on_bound_receiver_is_followed(self):
        files = {
            "pkg/__init__.py": (
                b"class Worker:\n"
                b"    @classmethod\n"
                b"    def boot(cls):\n        cls.load()\n"
                b"    @classmethod\n"
                b"    def load(cls):\n        from . import leaf\n"
                b"Worker.boot()\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.leaf"))
        self.assertEqual(function_count, 2)

    def test_instance_and_classmethod_calls_follow_direct_local_base_methods(self):
        files = {
            "pkg/__init__.py": (
                b"class Base:\n"
                b"    def load(self):\n        from . import instance_leaf\n"
                b"    @classmethod\n"
                b"    def cload(cls):\n        from . import class_leaf\n"
                b"class Worker(Base):\n"
                b"    def boot(self):\n        self.load()\n"
                b"    @classmethod\n"
                b"    def cboot(cls):\n        cls.cload()\n"
                b"Worker().boot()\nWorker.cboot()\n"
            ),
            "pkg/instance_leaf.py": b"VALUE = 1\n",
            "pkg/class_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.class_leaf", "pkg.instance_leaf")
        )
        self.assertEqual(function_count, 4)

    def test_receiver_and_super_calls_follow_transitive_local_base_methods(self):
        files = {
            "pkg/__init__.py": (
                b"class Root:\n"
                b"    def load(self):\n        from . import leaf\n"
                b"class Middle(Root):\n    pass\n"
                b"class Worker(Middle):\n"
                b"    def boot(self):\n"
                b"        self.load()\n"
                b"        super().load()\n"
                b"Worker().boot()\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.leaf"))
        self.assertEqual(function_count, 2)

    def test_receiver_and_super_calls_follow_imported_source_bases(self):
        fixtures = (
            (
                b"from .base import Base\n"
                b"class Worker(Base):\n"
                b"    def boot(self):\n        self.load()\n"
                b"Worker().boot()\n"
            ),
            (
                b"from . import base as source\n"
                b"class Worker(source.Base):\n"
                b"    def boot(self):\n        super().load()\n"
                b"Worker().boot()\n"
            ),
        )
        for source in fixtures:
            with self.subTest(source=source):
                files = {
                    "pkg/__init__.py": source,
                    "pkg/base.py": (
                        b"class Base:\n"
                        b"    def load(self):\n        from . import leaf\n"
                    ),
                    "pkg/leaf.py": b"VALUE = 1\n",
                }
                modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
                    files, ("pkg",)
                )
                self.assertEqual(modules, ("pkg", "pkg.base", "pkg.leaf"))
                self.assertEqual(function_count, 2)

    def test_local_class_aliases_resolve_local_and_imported_bases(self):
        fixtures = (
            (
                {
                    "pkg/__init__.py": (
                        b"class Base:\n"
                        b"    def load(self):\n        from . import leaf\n"
                        b"BaseAlias = Base\n"
                        b"class Worker(BaseAlias):\n"
                        b"    def boot(self):\n        self.load()\n"
                        b"Worker().boot()\n"
                    ),
                    "pkg/leaf.py": b"VALUE = 1\n",
                },
                ("pkg", "pkg.leaf"),
            ),
            (
                {
                    "pkg/__init__.py": (
                        b"from .base import Base as ImportedBase\n"
                        b"BaseAlias = ImportedBase\n"
                        b"class Worker(BaseAlias):\n"
                        b"    def boot(self):\n        super().load()\n"
                        b"Worker().boot()\n"
                    ),
                    "pkg/base.py": (
                        b"class Base:\n"
                        b"    def load(self):\n        from . import leaf\n"
                    ),
                    "pkg/leaf.py": b"VALUE = 1\n",
                },
                ("pkg", "pkg.base", "pkg.leaf"),
            ),
            (
                {
                    "pkg/__init__.py": (
                        b"from . import base as source\n"
                        b"BaseAlias = source.Base\n"
                        b"class Worker(BaseAlias):\n"
                        b"    def boot(self):\n        super().load()\n"
                        b"Worker().boot()\n"
                    ),
                    "pkg/base.py": (
                        b"class Base:\n"
                        b"    def load(self):\n        from . import leaf\n"
                    ),
                    "pkg/leaf.py": b"VALUE = 1\n",
                },
                ("pkg", "pkg.base", "pkg.leaf"),
            ),
        )
        for files, expected_modules in fixtures:
            with self.subTest(expected_modules=expected_modules):
                modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
                    files, ("pkg",)
                )
                self.assertEqual(modules, expected_modules)
                self.assertEqual(function_count, 2)

    def test_conditional_chained_base_alias_preserves_all_source_candidates(self):
        files = {
            "pkg/__init__.py": (
                b"class First:\n"
                b"    def load(self):\n        from . import first_leaf\n"
                b"class Second:\n"
                b"    def load(self):\n        from . import second_leaf\n"
                b"if platform_choice:\n"
                b"    BaseAlias = First\n"
                b"else:\n"
                b"    BaseAlias = Second\n"
                b"ChainedAlias = BaseAlias\n"
                b"class Worker(ChainedAlias):\n"
                b"    def boot(self):\n        self.load()\n"
                b"Worker().boot()\n"
            ),
            "pkg/first_leaf.py": b"VALUE = 1\n",
            "pkg/second_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.first_leaf", "pkg.second_leaf")
        )
        self.assertEqual(function_count, 3)

    def test_dynamic_base_assignment_does_not_guess_returned_class(self):
        files = {
            "pkg/__init__.py": (
                b"class Base:\n"
                b"    def load(self):\n        from . import leaf\n"
                b"def choose_base():\n    return Base\n"
                b"BaseAlias = choose_base()\n"
                b"class Worker(BaseAlias):\n"
                b"    def boot(self):\n        self.load()\n"
                b"Worker().boot()\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg",))
        self.assertEqual(function_count, 2)

    def test_cyclic_base_aliases_terminate_without_guessing_a_class(self):
        files = {
            "pkg/__init__.py": (
                b"class Base:\n"
                b"    def load(self):\n        from . import leaf\n"
                b"FirstAlias = SecondAlias\n"
                b"SecondAlias = FirstAlias\n"
                b"class Worker(FirstAlias):\n"
                b"    def boot(self):\n        self.load()\n"
                b"Worker().boot()\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg",))
        self.assertEqual(function_count, 1)

    def test_zero_argument_super_call_follows_direct_local_base_method(self):
        files = {
            "pkg/__init__.py": (
                b"class Base:\n"
                b"    def load(self):\n        from . import leaf\n"
                b"class Worker(Base):\n"
                b"    def boot(self):\n        super().load()\n"
                b"Worker().boot()\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.leaf"))
        self.assertEqual(function_count, 2)

    def test_explicit_super_class_and_receiver_follow_direct_local_base(self):
        files = {
            "pkg/__init__.py": (
                b"class Base:\n"
                b"    def load(self):\n        from . import instance_leaf\n"
                b"    @classmethod\n"
                b"    def cload(cls):\n        from . import class_leaf\n"
                b"class Worker(Base):\n"
                b"    def boot(self):\n        super(Worker, self).load()\n"
                b"    @classmethod\n"
                b"    def cboot(cls):\n        super(Worker, cls).cload()\n"
                b"Worker().boot()\nWorker.cboot()\n"
            ),
            "pkg/instance_leaf.py": b"VALUE = 1\n",
            "pkg/class_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.class_leaf", "pkg.instance_leaf")
        )
        self.assertEqual(function_count, 4)

    def test_explicit_super_requires_exact_class_and_receiver_names(self):
        for expression in (
            "super(Other, self).load()",
            "super(Worker, other).load()",
        ):
            with self.subTest(expression=expression):
                files = {
                    "pkg/__init__.py": (
                        "class Base:\n"
                        "    def load(self):\n        from . import leaf\n"
                        "class Worker(Base):\n"
                        f"    def boot(self):\n        {expression}\n"
                        "Worker().boot()\n"
                    ).encode("ascii"),
                    "pkg/leaf.py": b"VALUE = 1\n",
                }
                modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
                    files, ("pkg",)
                )
                self.assertEqual(modules, ("pkg",))
                self.assertEqual(function_count, 1)

    def test_unknown_class_definitions_keep_all_direct_super_bases(self):
        files = {
            "pkg/__init__.py": (
                b"class First:\n"
                b"    def load(self):\n        from . import first_leaf\n"
                b"class Second:\n"
                b"    def load(self):\n        from . import second_leaf\n"
                b"if platform_choice:\n"
                b"    class Worker(First):\n"
                b"        def boot(self):\n            super().load()\n"
                b"else:\n"
                b"    class Worker(Second):\n"
                b"        def boot(self):\n            super().load()\n"
                b"Worker().boot()\n"
            ),
            "pkg/first_leaf.py": b"VALUE = 1\n",
            "pkg/second_leaf.py": b"VALUE = 2\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(
            modules, ("pkg", "pkg.first_leaf", "pkg.second_leaf")
        )
        self.assertEqual(function_count, 4)

    def test_staticmethod_parameter_is_not_treated_as_bound_receiver(self):
        files = {
            "pkg/__init__.py": (
                b"class Worker:\n"
                b"    @staticmethod\n"
                b"    def boot(self):\n        self.load()\n"
                b"    def load(self):\n        from . import leaf\n"
                b"Worker.boot(None)\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg",))
        self.assertEqual(function_count, 1)

    def test_nested_local_helper_inherits_method_receiver_context(self):
        files = {
            "pkg/__init__.py": (
                b"class Worker:\n"
                b"    def boot(self):\n"
                b"        def inner():\n            self.load()\n"
                b"        inner()\n"
                b"    def load(self):\n        from . import leaf\n"
                b"Worker().boot()\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.leaf"))
        self.assertEqual(function_count, 3)

    def test_nested_helper_parameter_shadow_does_not_inherit_receiver(self):
        files = {
            "pkg/__init__.py": (
                b"class Worker:\n"
                b"    def boot(self):\n"
                b"        def inner(self):\n            self.load()\n"
                b"        inner(None)\n"
                b"    def load(self):\n        from . import leaf\n"
                b"Worker().boot()\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg",))
        self.assertEqual(function_count, 2)

    def test_custom_attribute_staticmethod_decorator_keeps_unknown_binding(self):
        files = {
            "pkg/__init__.py": (
                b"class Worker:\n"
                b"    @custom.staticmethod\n"
                b"    def boot(self):\n        self.load()\n"
                b"    def load(self):\n        from . import leaf\n"
                b"Worker.boot(None)\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.leaf"))
        self.assertEqual(function_count, 2)

    def test_shadowed_staticmethod_name_keeps_receiver_candidate(self):
        files = {
            "pkg/__init__.py": (
                b"staticmethod = identity\n"
                b"class Worker:\n"
                b"    @staticmethod\n"
                b"    def boot(self):\n        self.load()\n"
                b"    def load(self):\n        from . import leaf\n"
                b"Worker.boot(None)\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.leaf"))
        self.assertEqual(function_count, 2)

    def test_match_capture_staticmethod_name_keeps_receiver_candidate(self):
        files = {
            "pkg/__init__.py": (
                b"match {}:\n    case {**staticmethod}:\n        pass\n"
                b"class Worker:\n"
                b"    @staticmethod\n"
                b"    def boot(self):\n        self.load()\n"
                b"    def load(self):\n        from . import leaf\n"
                b"Worker.boot(None)\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.leaf"))
        self.assertEqual(function_count, 2)

    def test_uncalled_from_import_module_alias_does_not_expand_function(self):
        files = {
            "pkg/__init__.py": b"from . import helper as h\n",
            "pkg/helper.py": b"def boot():\n    from . import leaf\n",
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper"))
        self.assertEqual(function_count, 0)

    def test_called_imported_source_function_adds_its_imports(self):
        files = {
            "pkg/__init__.py": (
                b"from .helper import boot as start\nstart()\n"
            ),
            "pkg/helper.py": (
                b"def boot():\n    from . import leaf\n"
            ),
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper", "pkg.leaf"))
        self.assertEqual(function_count, 1)

    def test_uncalled_imported_source_function_does_not_expand_body(self):
        files = {
            "pkg/__init__.py": b"from .helper import boot\n",
            "pkg/helper.py": b"def boot():\n    from . import leaf\n",
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper"))
        self.assertEqual(function_count, 0)

    def test_called_local_function_follows_imported_function_entry(self):
        files = {
            "pkg/__init__.py": (
                b"from .helper import boot\n"
                b"def start():\n    boot()\n"
                b"start()\n"
            ),
            "pkg/helper.py": b"def boot():\n    from . import leaf\n",
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg",)
        )
        self.assertEqual(modules, ("pkg", "pkg.helper", "pkg.leaf"))
        self.assertEqual(function_count, 2)

    def test_imported_module_alias_calls_follow_source_function(self):
        for import_statement, receiver in (
            ("import pkg.helper as helper", "helper"),
            ("import pkg.helper", "pkg.helper"),
        ):
            with self.subTest(import_statement=import_statement):
                files = {
                    "pkg/entry.py": (
                        f"{import_statement}\n{receiver}.boot()\n".encode("ascii")
                    ),
                    "pkg/helper.py": b"def boot():\n    from . import leaf\n",
                    "pkg/leaf.py": b"VALUE = 1\n",
                }
                modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
                    files, ("pkg.entry",)
                )
                self.assertEqual(modules, ("pkg.entry", "pkg.helper", "pkg.leaf"))
                self.assertEqual(function_count, 1)

    def test_uncalled_imported_module_alias_does_not_expand_function_body(self):
        files = {
            "pkg/entry.py": b"import pkg.helper as helper\n",
            "pkg/helper.py": b"def boot():\n    from . import leaf\n",
            "pkg/leaf.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(
            files, ("pkg.entry",)
        )
        self.assertEqual(modules, ("pkg.entry", "pkg.helper"))
        self.assertEqual(function_count, 0)

    def test_class_annotations_are_evaluated_inside_called_function(self):
        files = {
            "pkg/__init__.py": (
                b"def define_class():\n"
                b"    class Local:\n        class_value: annotation_helper()\n"
                b"def annotation_helper():\n    from . import annotation_only\n"
                b"define_class()\n"
            ),
            "pkg/annotation_only.py": b"VALUE = 1\n",
        }
        modules, _, function_count, _, _ = SUBJECT._module_init_call_candidate_closure(files, ("pkg",))
        self.assertEqual(modules, ("pkg", "pkg.annotation_only"))
        self.assertEqual(function_count, 2)

    def test_unresolvable_dynamic_import_is_not_claimed(self):
        files = {"entry.py": b"import importlib\n\ndef load(name):\n    return importlib.import_module(name)\n"}
        modules, _, _ = SUBJECT._candidate_closure(files, ("entry",))
        self.assertEqual(modules, ("entry",))

    def test_literal_dynamic_imports_add_source_candidates(self):
        files = {
            "entry.py": (
                b"import importlib\n"
                b"__import__('pkg.direct')\n"
                b"importlib.import_module('pkg.api')\n"
                b"importlib.import_module(runtime_name)\n"
            ),
            "pkg/__init__.py": b"VALUE = 1\n",
            "pkg/direct.py": b"VALUE = 2\n",
            "pkg/api.py": b"VALUE = 3\n",
        }
        modules, edges, _ = SUBJECT._candidate_closure(files, ("entry",))
        self.assertEqual(modules, ("entry", "pkg", "pkg.api", "pkg.direct"))
        self.assertEqual(edges, 2)

    def test_literal_dynamic_import_aliases_are_candidates(self):
        files = {
            "entry.py": (
                b"from importlib import import_module as load\n"
                b"import importlib as il\n"
                b"import builtins as bi\n"
                b"from builtins import __import__ as direct_import\n"
                b"assigned_loader = load\n"
                b"chained_loader = assigned_loader\n"
                b"assigned_import = bi.__import__\n"
                b"literal_name = 'pkg.literal_name'\n"
                b"concat_name = 'pkg.' + 'concat_name'\n"
                b"fstring_name = f'pkg.fstring_name'\n"
                b"formatted_fstring_name = f\"pkg.{'formatted_fstring_name'}\"\n"
                b"relative_name = '.pkg.relative'\n"
                b"load('pkg.api')\n"
                b"chained_loader('pkg.assigned_alias')\n"
                b"load(literal_name)\n"
                b"load(concat_name)\n"
                b"load('pkg.' + 'inline_concat')\n"
                b"load(fstring_name)\n"
                b"load(f'pkg.inline_fstring')\n"
                b"load(formatted_fstring_name)\n"
                b"load(f\"pkg.{'inline_formatted_fstring'}\")\n"
                b"load(f\"pkg.{'inline_string_converted_fstring'!s}\")\n"
                b"load(f\"pkg.{'inline_string_format_spec':s}\")\n"
                b"load(f\"pkg.{'inline_string_format_spec_and_conversion'!s:s}\")\n"
                b"load(f\"{f'pkg.inline_nested_fstring'}\")\n"
                b"nested_fstring_name = f\"{f'pkg.nested_fstring_name'}\"\n"
                b"load(nested_fstring_name)\n"
                b"load(f\"{f'pkg.{runtime_name}'}\")\n"
                b"load(f\"pkg.{'repr_conversion_not_supported'!r}\")\n"
                b"load(f\"pkg.{'format_spec_not_supported':>1}\")\n"
                b"dynamic_fstring_name = f'pkg.{runtime_name}'\n"
                b"load(dynamic_fstring_name)\n"
                b"load(relative_name)\n"
                b"il.import_module('pkg.module_alias')\n"
                b"bi.__import__('pkg.builtins_attr')\n"
                b"direct_import('pkg.builtins_alias')\n"
                b"assigned_import('pkg.assigned_builtin')\n"
                b"load(runtime_name)\n"
            ),
            "pkg/__init__.py": b"VALUE = 0\n",
            "pkg/api.py": b"VALUE = 1\n",
            "pkg/module_alias.py": b"VALUE = 2\n",
            "pkg/builtins_attr.py": b"VALUE = 3\n",
            "pkg/builtins_alias.py": b"VALUE = 4\n",
            "pkg/assigned_alias.py": b"VALUE = 5\n",
            "pkg/assigned_builtin.py": b"VALUE = 6\n",
            "pkg/literal_name.py": b"VALUE = 7\n",
            "pkg/concat_name.py": b"VALUE = 8\n",
            "pkg/inline_concat.py": b"VALUE = 9\n",
            "pkg/fstring_name.py": b"VALUE = 10\n",
            "pkg/inline_fstring.py": b"VALUE = 11\n",
            "pkg/formatted_fstring_name.py": b"VALUE = 12\n",
            "pkg/inline_formatted_fstring.py": b"VALUE = 13\n",
            "pkg/inline_string_converted_fstring.py": b"VALUE = 14\n",
            "pkg/inline_string_format_spec.py": b"VALUE = 17\n",
            "pkg/inline_string_format_spec_and_conversion.py": b"VALUE = 18\n",
            "pkg/inline_nested_fstring.py": b"VALUE = 15\n",
            "pkg/nested_fstring_name.py": b"VALUE = 16\n",
        }
        modules, edges, _ = SUBJECT._candidate_closure(files, ("entry",))
        self.assertEqual(
            modules,
            (
                "entry", "pkg", "pkg.api", "pkg.assigned_alias",
                "pkg.assigned_builtin", "pkg.builtins_alias",
                "pkg.builtins_attr", "pkg.concat_name",
                "pkg.formatted_fstring_name", "pkg.fstring_name",
                "pkg.inline_concat", "pkg.inline_formatted_fstring",
                "pkg.inline_fstring", "pkg.inline_nested_fstring",
                "pkg.inline_string_converted_fstring",
                "pkg.inline_string_format_spec",
                "pkg.inline_string_format_spec_and_conversion", "pkg.literal_name",
                "pkg.module_alias", "pkg.nested_fstring_name",
            ),
        )
        self.assertEqual(edges, 18)

    def test_import_from_resolves_existing_submodule_conservatively(self):
        files = {
            "pkg/__init__.py": b"from . import child\n",
            "pkg/child.py": b"VALUE = 1\n",
        }
        modules, edges, _ = SUBJECT._candidate_closure(files, ("pkg",))
        self.assertEqual(modules, ("pkg", "pkg.child"))
        self.assertEqual(edges, 2)

    def test_report_labels_candidates_without_attestation(self):
        source = TOOL.read_bytes()
        tree = ast.parse(source)
        labels = {n.value for n in ast.walk(tree)
                  if isinstance(n, ast.Constant) and type(n.value) is str}
        self.assertIn("CANDIDATES_ONLY", labels)
        self.assertIn("LEXICAL_SOURCE_CANDIDATES_ONLY", labels)
        self.assertIn("MODULE_AND_CLASS_BODIES_ONLY", labels)
        self.assertIn("source_stdlib_module_names_count", labels)
        self.assertIn("source_stdlib_module_names_sha256", labels)
        self.assertIn("frozen_bootstrap_name_count", labels)
        self.assertIn("frozen_bootstrap_names", labels)
        self.assertIn("frozen_stdlib_name_count", labels)
        self.assertIn("frozen_stdlib_names", labels)
        self.assertIn("frozen_test_name_count", labels)
        self.assertIn("frozen_alias_count", labels)
        self.assertIn("frozen_alias_rows", labels)
        self.assertIn("target_platform_frozen_name_candidates", labels)
        self.assertIn("module_init_call_frozen_name_candidates", labels)
        self.assertIn("bootstrap_setup_name_count", labels)
        self.assertIn("bootstrap_setup_conditional_name_count", labels)
        self.assertIn("bootstrap_setup_rows_sha256", labels)
        self.assertIn("stdlib_setup_entry_count", labels)
        self.assertIn("stdlib_setup_test_entry_count", labels)
        self.assertIn("stdlib_setup_condition_count", labels)
        self.assertIn("stdlib_setup_rows_sha256", labels)
        self.assertIn("getpath_path_variable_count", labels)
        self.assertIn("getpath_config_key_count", labels)
        self.assertIn("sysconfig_install_scheme_count", labels)
        self.assertIn("sysconfig_path_key_count", labels)
        self.assertIn("importlib_module_spec_field_count", labels)
        self.assertIn("importlib_loader_finder_class_count", labels)
        self.assertIn("importlib_public_api_row_count", labels)
        self.assertIn("config_c_row_count", labels)
        self.assertIn("configure_module_anchor_count", labels)
        self.assertIn("module_init_call_roots_outside_source_stdlib_names", labels)
        self.assertIn("module_init_call_source_candidates", labels)
        self.assertIn("target_module_init_re_compile_input_candidates", labels)
        self.assertIn(
            "target_module_init_re_compile_tokenizer_input_type_candidates", labels,
        )
        self.assertIn("flags_value_if_call_evaluates", labels)
        self.assertIn("PINNED_REGEXFLAG_EXPRESSION", labels)
        self.assertIn("verbose_mode_if_parser_entry_reached", labels)
        self.assertIn(
            "inline_verbose_flag_group_candidates_if_literal_bound", labels,
        )
        self.assertIn("inline_verbose_flag_scan_bound", labels)
        self.assertIn("LEXICAL_INLINE_REGEX_FLAG_CANDIDATE", labels)
        self.assertIn(
            "verbose_ignored_syntax_candidates_if_verbose_and_literal_bound",
            labels,
        )
        self.assertIn("target_platform_source_candidates", labels)
        self.assertIn(
            "MODULE_CLASS_AND_KNOWN_LINUX_CPYTHON312_IF_BUILTIN_AND_IMPORTED_MODULE_NAME_BRANCHES",
            labels,
        )
        self.assertIn("target_platform_builtin_membership", labels)
        self.assertIn("target_platform_builtin_module_names", labels)
        self.assertIn("target_platform_builtin_config_c_sha256", labels)
        self.assertIn("target_platform_builtin_layer_sha256", labels)
        self.assertIn(
            "MODULE_CLASS_CALLS_SIMPLE_ALIASES_GENERATORS_IMPORTED_FUNCTIONS_MODULE_ALIASES_FROM_IMPORT_IMPORTED_CLASS_METHODS_DIRECT_CONSTRUCTED_METHODS_SAME_SCOPE_INSTANCE_BINDINGS_INSTANCE_ALIASES_BOUND_RECEIVER_METHODS_NESTED_RECEIVER_CLOSURES_INHERITED_RECEIVER_METHODS_AND_TRANSITIVE_LOCAL_BASES_AND_IMPORTED_SOURCE_BASES_AND_BASE_ALIASES_AND_ZERO_ARG_AND_EXPLICIT_LOCAL_SUPER_METHODS_AND_INHERITED_CONSTRUCTORS_AND_CONSTRUCTED_INHERITED_METHODS_AND_IMPORTED_SOURCE_SUBCLASS_DISPATCH_SAME_MODULE_AND_IMPORTED_SOURCE_BASE_DISPATCH_AND_SIMPLE_IMPORTED_CLASS_ALIASES_AND_QUALIFIED_IMPORTED_CLASS_ALIASES_AND_LOCAL_CLASS_ALIASES_AND_DIRECT_FUNCTION_AND_CLASS_SCOPE_IMPORTED_CLASS_ALIASES_AND_CALLED_NESTED_FUNCTION_CLASS_ALIAS_CLOSURES_AND_DIRECT_TOP_LEVEL_FACTORY_RETURNS_AFTER_IMPORTS_AND_DOCSTRINGS_AND_SIMPLE_LOCAL_INSTANCE_ASSIGNMENTS",
            labels,
        )
        self.assertNotIn("P11_MATCH", labels)


if __name__ == "__main__":
    unittest.main()
