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
        self.assertNotIn("P11_MATCH", labels)


if __name__ == "__main__":
    unittest.main()
