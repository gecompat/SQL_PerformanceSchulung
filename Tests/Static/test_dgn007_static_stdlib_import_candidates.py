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
        self.assertIn(
            "MODULE_CLASS_CALLS_SIMPLE_ALIASES_GENERATORS_IMPORTED_FUNCTIONS_MODULE_ALIASES_FROM_IMPORT_AND_IMPORTED_CLASS_METHODS",
            labels,
        )
        self.assertNotIn("P11_MATCH", labels)


if __name__ == "__main__":
    unittest.main()
