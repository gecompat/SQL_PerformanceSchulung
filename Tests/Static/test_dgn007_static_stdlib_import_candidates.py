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
        self.assertNotIn("P11_MATCH", labels)


if __name__ == "__main__":
    unittest.main()
