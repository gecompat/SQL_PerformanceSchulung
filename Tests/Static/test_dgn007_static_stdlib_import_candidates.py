"""Gegenproben für die deklarative CPython-Quellkandidatenanalyse."""
import ast
import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


TOOL = Path(__file__).resolve().parents[1] / "Tools/dgn007_static_stdlib_import_candidates.py"
SPEC = importlib.util.spec_from_file_location("dgn007_static_stdlib_import_candidates", TOOL)
SUBJECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUBJECT)


class StaticImportCandidateTests(unittest.TestCase):
    def test_archive_binding_and_limits_are_fixed(self):
        self.assertEqual(len(SUBJECT.ARCHIVE_SHA256), 64)
        self.assertEqual(SUBJECT.ARCHIVE_ROOT, "Python-3.12.16/Lib/")
        self.assertEqual(SUBJECT.MAX_ARCHIVE_BYTES, 64 * 1024 * 1024)
        self.assertEqual(SUBJECT.MAX_SOURCE_BYTES, 64 * 1024 * 1024)
        self.assertEqual(SUBJECT.MAX_SOURCE_FILES, 2048)

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
        )
        with patch.object(
            SUBJECT, "GETPATH_SOURCE_SHA256", hashlib.sha256(getpath).hexdigest()
        ):
            inventory = SUBJECT._getpath_source_inventory(getpath)
        self.assertEqual(inventory["path_variable_count"], 14)
        self.assertEqual(inventory["config_key_count"], 12)

        sysconfig = (
            b"_INSTALL_SCHEMES = {'posix': {'stdlib': 'lib/python', 'purelib': 'site'}}\n"
            b"def _get_sysconfigdata_name(): return 'name'\n"
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

    def test_sysconfig_source_rejects_executable_scheme_expression(self):
        source = (
            b"_INSTALL_SCHEMES = build_schemes()\n"
            b"def _get_sysconfigdata_name(): return 'name'\n"
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
        modules, _, _, conditions = SUBJECT._target_platform_candidate_closure(files, ("pkg",))
        self.assertEqual(
            modules,
            ("pkg", "pkg.linux_helper", "pkg.tuple_correct", "pkg.unknown_a", "pkg.unknown_b"),
        )
        self.assertEqual(conditions, {"resolved": 2, "unknown": 1})

    def test_target_python_version_info_uses_full_cpython_tuple(self):
        short_equal = ast.parse("sys.version_info == (3, 12, 16)", mode="eval").body
        minimum = ast.parse("sys.version_info >= (3, 12)", mode="eval").body
        identity = ast.parse("sys.platform is 'linux'", mode="eval").body
        self.assertIs(SUBJECT._target_condition(short_equal), False)
        self.assertIs(SUBJECT._target_condition(minimum), True)
        self.assertIsNone(SUBJECT._target_condition(identity))

    def test_builtin_module_membership_uses_only_bound_target_facts(self):
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
            files, ("pkg",)
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

    def test_constructed_instance_from_factory_is_not_guessed(self):
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
        self.assertEqual(modules, ("pkg", "pkg.helper"))
        self.assertEqual(function_count, 1)

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
        self.assertIn("frozen_stdlib_name_count", labels)
        self.assertIn("frozen_test_name_count", labels)
        self.assertIn("frozen_alias_count", labels)
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
        self.assertIn(
            "MODULE_CLASS_CALLS_SIMPLE_ALIASES_GENERATORS_IMPORTED_FUNCTIONS_MODULE_ALIASES_FROM_IMPORT_IMPORTED_CLASS_METHODS_DIRECT_CONSTRUCTED_METHODS_SAME_SCOPE_INSTANCE_BINDINGS_INSTANCE_ALIASES_BOUND_RECEIVER_METHODS_NESTED_RECEIVER_CLOSURES_INHERITED_RECEIVER_METHODS_AND_TRANSITIVE_LOCAL_BASES_AND_IMPORTED_SOURCE_BASES_AND_BASE_ALIASES_AND_ZERO_ARG_AND_EXPLICIT_LOCAL_SUPER_METHODS_AND_INHERITED_CONSTRUCTORS_AND_CONSTRUCTED_INHERITED_METHODS_AND_IMPORTED_SOURCE_SUBCLASS_DISPATCH_SAME_MODULE_AND_IMPORTED_SOURCE_BASE_DISPATCH_AND_SIMPLE_IMPORTED_CLASS_ALIASES_AND_QUALIFIED_IMPORTED_CLASS_ALIASES_AND_LOCAL_CLASS_ALIASES_AND_DIRECT_FUNCTION_AND_CLASS_SCOPE_IMPORTED_CLASS_ALIASES_AND_CALLED_NESTED_FUNCTION_CLASS_ALIAS_CLOSURES",
            labels,
        )
        self.assertNotIn("P11_MATCH", labels)


if __name__ == "__main__":
    unittest.main()
