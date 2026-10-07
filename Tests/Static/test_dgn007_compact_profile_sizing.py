"""Unabhängige synthetische Gegenproben der reinen Entwurfsgrößenrechnung."""
from dataclasses import FrozenInstanceError, fields, replace
import ast
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / "Tools"
sys.path.insert(0, str(TOOLS))
import dgn007_compact_profile_sizing as s
import dgn007_import_profile_binding as b
import dgn007_import_probe_input as i


def prepared(body=b"# synthetic raw\r\n"):
    sources = tuple(i.SourceBytes(name, member, hashlib.sha256(body).hexdigest(), body)
                    for name, member in i.MODULES)
    return i.PreparedInput("a" * 40, "b" * 64, "dgn007-docker-sql-only/v1", b"n" * 32, sources)


def installation():
    return b.InstallationDeclaration(b.ASSUMPTION, "linux", "cpython", (3, 12, 14),
        "/synthetic/python", "/synthetic/python-target", ("/synthetic",) * 4, "synthetic-abi",
        ("/synthetic/lib", "/synthetic/lib/lib-dynload", "/synthetic/python312.zip"),
        ("/synthetic/lib", "/synthetic/lib/lib-dynload"), "/synthetic/python312.zip",
        (1, 1, 1, 1, 1, 0), ("BUILTIN", "FROZEN", "PATH"), ("ZIPIMPORTER", "FILEFINDER"),
        (b.FileFingerprint("/synthetic/python-target", 123, "c" * 64),
         b.FileFingerprint("/synthetic/lib/reviewed.py", 456, "d" * 64)))


def control():
    return b.ModuleDeclaration("__main__", "__main__", None, "", "/synthetic/control.py",
                               "CONTROL", (), "NONE")


def builtin(name="sys"):
    return b.ModuleDeclaration(name, name, name, "built-in", "", "BUILTIN", (), "BUILTIN")


def source(name="synthetic_package", kind="SOURCE"):
    file = "/synthetic/lib/" + name.replace(".", "/") + ".py"
    return b.ModuleDeclaration(name, name, name, file, file, kind,
        ("/synthetic/lib/package",) if kind == "SOURCE" else (), kind, name, file)


def frozen(name="_frozen_importlib", group=()):
    mn, sn = b.FROZEN_NAMES.get(name, (name, name))
    return b.ModuleDeclaration(name, mn, sn, "frozen", "/synthetic/lib/frozen.py",
                               "FROZEN", (), "FROZEN", aliasGroup=group)


def worker(ordinal=1, modules=None, inst=None):
    rows = modules if modules is not None else (control(), builtin(), source(), source("synthetic_ext", "EXTENSION"), frozen())
    rows = tuple(sorted(rows, key=lambda r: r.name))
    return b.WorkerDeclaration(ordinal, b.ENTRIES[ordinal - 1], "PRE_IMPORT", inst or installation(),
                               tuple(r.name for r in rows if r.kind == "CONTROL"), rows)


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def named(value):
    # Unabhängige benannte Referenz: alle DTO-Felder, keine Produktionsprojektion.
    if type(value) is tuple:
        return tuple(named(v) for v in value)
    if type(value) is bytes:
        return value.hex()
    if type(value) in (b.FileFingerprint, b.ModuleDeclaration, b.InstallationDeclaration,
                        b.WorkerDeclaration, b.SourceDescriptor, b.BindingContext):
        return {f.name: named(getattr(value, f.name)) for f in fields(value)}
    return value


INSTALLATION_KEYS = ("assumption", "platform", "implementation", "version", "executable",
    "executable_target", "prefixes", "abi", "paths", "roots", "inert_zip", "flags", "finders", "hooks", "files")
MODULE_KEYS = ("name", "moduleName", "specName", "origin", "file", "kind", "locations", "loader", "loaderName", "loaderPath", "aliasGroup")
DESCRIPTOR_KEYS = ("ordinal", "module", "member", "size", "sha256")


def reference(parent, selected):
    # Die vollständigen benannten Referenzen werden erst hier positionsgebunden.
    metadata = i._metadata(parent)
    wn = named(selected)
    cn = named(b.derive_binding_context(parent, selected.ordinal))
    ins = tuple(wn["installation"][key] for key in INSTALLATION_KEYS[:-1]) + (
        tuple((f["path"], f["size"], f["sha256"]) for f in wn["installation"]["files"]),)
    modules = tuple(tuple(row[key] for key in MODULE_KEYS) for row in wn["modules"])
    descriptors = lambda rows: tuple(tuple(row[key] for key in DESCRIPTOR_KEYS) for row in rows)
    inp = tuple(metadata[key] for key in ("protocol", "commit", "raw27_binding", "source_profile", "nonce")) + (
        descriptors(metadata["modules"]), metadata["context_sha256"])
    ctx = tuple(cn[key] for key in ("commit", "raw27_binding", "source_profile", "nonce")) + (
        descriptors(cn["modules"]), cn["ordinal"], cn["entry"], cn["phase"])
    wrk = (wn["ordinal"], wn["entry"], wn["phase"], ins, wn["controls"], modules)
    return (("compact-binding-design", "METADATA", inp, wrk, ctx),
        ("compact-binding-design", "REPORTED", ctx, ins, wn["controls"], modules),
        ("compact-binding-design", "compact-installation-declaration", ins),
        ("compact-binding-design", "compact-worker-declaration", wrk),
        ("compact-binding-design", "compact-profile-binding-context", ctx))


def at_size(index, target):
    selected = worker()
    remaining = target - (16 + len(canonical(reference(prepared(), selected)[index])))
    prefixes = list(selected.installation.prefixes)
    for n in range(4):
        delta = min(remaining, 4096 - len(prefixes[n]))
        if delta < 0:
            raise AssertionError("synthetic target below base")
        prefixes[n] += "x" * delta
        remaining -= delta
    if remaining:
        raise AssertionError("synthetic prefix capacity")
    return replace(selected, installation=replace(selected.installation, prefixes=tuple(prefixes)))


class Foreign:
    def __getattribute__(self, _):
        raise RuntimeError("synthetic-private-getter")
    def __eq__(self, _):
        raise RuntimeError("synthetic-private-equality")
    def __iter__(self):
        raise RuntimeError("synthetic-private-iterator")


class SizingTests(unittest.TestCase):
    def reject(self, parent, selected):
        result = s.size_declared_profile(parent, selected)
        self.assertEqual((result.status, result.issue, result.ordinal, result.forms),
                         ("REJECTED_DESIGN_SIZING", "INVALID_RECORD", None, ()))
        self.assertNotIn("synthetic-private", repr(result))

    def test_all_five_complete_sizes_all_three_ordinals(self):
        for ordinal in (1, 2, 3):
            with self.subTest(ordinal=ordinal):
                selected = worker(ordinal)
                result = s.size_declared_profile(prepared(), selected)
                self.assertEqual(result.status, "DESIGN_SIZING_ONLY")
                self.assertEqual(result.ordinal, ordinal)
                self.assertEqual(tuple(r.form for r in result.forms), s.FORM_NAMES)
                self.assertEqual(tuple(r.bytes_including_header for r in result.forms),
                                 tuple(16 + len(canonical(v)) for v in reference(prepared(), selected)))

    def test_all_field_positions_against_independent_named_reference(self):
        parent, selected = prepared(), worker()
        actual = s._forms(parent, selected)
        self.assertEqual(actual, reference(parent, selected))
        self.assertEqual(len(actual[0][2]), 7)
        self.assertEqual(len(actual[0][3]), 6)
        self.assertEqual(len(actual[0][4]), 8)
        self.assertEqual(len(actual[2][2]), 15)
        self.assertTrue(all(len(row) == 11 for row in actual[0][3][5]))
        self.assertEqual(set(INSTALLATION_KEYS), {f.name for f in fields(b.InstallationDeclaration)})
        self.assertEqual(set(MODULE_KEYS), {f.name for f in fields(b.ModuleDeclaration)})

    def test_both_nine_descriptor_arrays_present_with_raw_hashes(self):
        parent = prepared(b"a\r\nb\n")
        common = s._forms(parent, worker())[0]
        for array in (common[2][5], common[4][4]):
            self.assertEqual(len(array), 9)
            for n, row in enumerate(array):
                self.assertEqual(row, (n, *i.MODULES[n], 5, hashlib.sha256(b"a\r\nb\n").hexdigest()))
        self.assertEqual(common[2][5], common[4][4])

    def test_original_input_context_digest_is_not_replaced(self):
        metadata = i._metadata(prepared())
        without_digest = {k: v for k, v in metadata.items() if k != "context_sha256"}
        digest = hashlib.sha256(canonical(without_digest)).hexdigest()
        self.assertEqual(s._forms(prepared(), worker())[0][2][6], digest)
        self.assertNotEqual(digest, hashlib.sha256(canonical(s._forms(prepared(), worker())[4])).hexdigest())

    def test_raw_crlf_not_normalized(self):
        lf, crlf = prepared(b"a\nb\n"), prepared(b"a\r\nb\r\n")
        a, z = s._forms(lf, worker()), s._forms(crlf, worker())
        self.assertNotEqual(a[0][2], z[0][2])
        self.assertNotEqual(a[0][4], z[0][4])
        self.assertEqual(lf.sources[0].body, b"a\nb\n")
        self.assertEqual(crlf.sources[0].body, b"a\r\nb\r\n")

    def test_module_locations_and_loader_fields_retained(self):
        selected = worker()
        rows = s._forms(prepared(), selected)[0][3][5]
        package = next(r for r in rows if r[0] == "synthetic_package")
        self.assertEqual(package[6], ("/synthetic/lib/package",))
        self.assertEqual(package[8:10], ("synthetic_package", "/synthetic/lib/synthetic_package.py"))
        changed = replace(selected, modules=tuple(replace(r, locations=("/synthetic/lib/longer_package",))
            if r.name == "synthetic_package" else r for r in selected.modules))
        self.assertGreater(s.size_declared_profile(prepared(), changed).forms[3].bytes_including_header,
                           s.size_declared_profile(prepared(), selected).forms[3].bytes_including_header)

    def test_two_file_fingerprints_complete(self):
        ins = s._forms(prepared(), worker())[2][2]
        self.assertEqual(ins[14], (("/synthetic/python-target", 123, "c" * 64),
                                  ("/synthetic/lib/reviewed.py", 456, "d" * 64)))

    def test_null_spec_and_empty_text_remain_distinct(self):
        rows = s._forms(prepared(), worker())[0][3][5]
        main = next(r for r in rows if r[0] == "__main__")
        self.assertIsNone(main[2])
        self.assertEqual(main[3], "")
        self.assertIn(b'null,""', canonical(main))

    def test_mixed_frozen_source_empty_aliases_preserved(self):
        selected = worker(modules=(control(), frozen("_collections_abc"), source("collections.abc")))
        rows = s._forms(prepared(), selected)[0][3][5]
        self.assertTrue(all(r[10] == () for r in rows))
        self.assertEqual(s.size_declared_profile(prepared(), selected).status, "DESIGN_SIZING_ONLY")

    def test_complete_frozen_pair_retained(self):
        pair = ("_frozen_importlib", "importlib._bootstrap")
        selected = worker(modules=(control(), frozen(pair[0], pair), frozen(pair[1], pair)))
        rows = s._forms(prepared(), selected)[0][3][5]
        self.assertEqual(tuple(r[10] for r in rows if r[5] == "FROZEN"), (pair, pair))

    def test_missing_or_mixed_claimed_alias_rejected(self):
        pair = ("_frozen_importlib", "importlib._bootstrap")
        for rows in ((control(), frozen(pair[0], pair)),
                     (control(), frozen(pair[0], pair), source(pair[1]))):
            self.reject(prepared(), worker(modules=rows))

    def test_all_form_tags_header_and_no_digest(self):
        values = s._forms(prepared(), worker())
        tags = ("METADATA", "REPORTED", "compact-installation-declaration", "compact-worker-declaration", "compact-profile-binding-context")
        for value, tag in zip(values, tags):
            self.assertEqual(value[:2], ("compact-binding-design", tag))
            self.assertEqual(s._size(value), 16 + len(canonical(value)))
        self.assertFalse(hasattr(s.SizingReport, "worker_digest"))

    def test_valid_common_cap_and_cap_plus_one(self):
        for target in (16384, 16385):
            result = s.size_declared_profile(prepared(), at_size(0, target))
            self.assertEqual(result.forms[0].bytes_including_header, target)
            self.assertEqual(result.forms[0].overflow, target > 16384)

    def test_valid_report_cap_and_cap_plus_one(self):
        for target in (16384, 16385):
            result = s.size_declared_profile(prepared(), at_size(1, target))
            self.assertEqual(result.forms[1].bytes_including_header, target)
            self.assertEqual(result.forms[1].overflow, target > 16384)

    def test_valid_installation_cap_and_cap_plus_one(self):
        for target in (16384, 16385):
            result = s.size_declared_profile(prepared(), at_size(2, target))
            self.assertEqual(result.forms[2].bytes_including_header, target)
            self.assertEqual(result.forms[2].overflow, target > 16384)

    def test_valid_worker_cap_and_cap_plus_one(self):
        for target in (16384, 16385):
            result = s.size_declared_profile(prepared(), at_size(3, target))
            self.assertEqual(result.forms[3].bytes_including_header, target)
            self.assertEqual(result.forms[3].overflow, target > 16384)

    def test_context_maximum_input_remains_bounded_below_cap(self):
        # Feste Namen/Member/Hexbreiten: kein gültiges Kontext-Capfixture erfinden.
        parent = prepared()
        rows = []
        for n, row in enumerate(parent.sources):
            body = b"x" * (131072 if n < 8 else 0)
            rows.append(replace(row, body=body, sha256=hashlib.sha256(body).hexdigest()))
        parent = replace(parent, sources=tuple(rows))
        for ordinal in (1, 2, 3):
            result = s.size_declared_profile(parent, worker(ordinal))
            self.assertEqual(result.status, "DESIGN_SIZING_ONLY")
            self.assertLess(result.forms[4].bytes_including_header, 16384)
            self.assertEqual(result.forms[4].bytes_including_header, 16 + len(canonical(reference(parent, worker(ordinal))[4])))

    def test_internal_counter_cap_and_plus_one_all_roles(self):
        # Nur Counterarithmetik; diese übergroßen Strings sind KEINE DTO-Kontexte.
        for role in ("METADATA", "REPORTED", "compact-installation-declaration", "compact-worker-declaration", "compact-profile-binding-context"):
            empty = (s.DESIGN_TAG, role, "")
            base = 16 + len(canonical(empty))
            for target in (16384, 16385):
                self.assertEqual(s._size((s.DESIGN_TAG, role, "x" * (target - base))), target)

    def test_all_five_returned_despite_multiple_overflows(self):
        selected = worker(inst=replace(installation(), prefixes=("/" + "x" * 4095,) * 4))
        result = s.size_declared_profile(prepared(), selected)
        self.assertEqual(result.status, "DESIGN_SIZING_OVERFLOW")
        self.assertEqual(len(result.forms), 5)
        self.assertEqual(tuple(r.overflow for r in result.forms), (True, True, True, True, False))

    def test_native_ascii_escaping_exact(self):
        for text in ('a', '"', '\\', '\b\f\n\r\t', '\x01', '\x7f', 'é', '😀'):
            value = (s.DESIGN_TAG, "REPORTED", text)
            self.assertEqual(s._size(value), 16 + len(canonical(value)))
        selected = worker(inst=replace(installation(), abi="é😀\x7f\t"))
        self.assertEqual(s.size_declared_profile(prepared(), selected).forms[2].bytes_including_header,
                         16 + len(canonical(reference(prepared(), selected)[2])))

    def test_utf8_field_cap_distinct_from_ascii_size(self):
        for text, accepted in (("é" * 2048, True), ("é" * 2049, False), ("😀" * 1024, True), ("😀" * 1025, False)):
            selected = worker(inst=replace(installation(), abi=text))
            result = s.size_declared_profile(prepared(), selected)
            self.assertEqual(bool(result.forms), accepted)

    def test_nul_and_surrogate_rejected(self):
        for text in ("synthetic\0", "synthetic\ud800"):
            self.reject(prepared(), worker(inst=replace(installation(), abi=text)))

    def test_late_invalid_after_large_valid_records_before_counting(self):
        huge = worker(inst=replace(installation(), prefixes=("/" + "x" * 4095,) * 4))
        huge = replace(huge, modules=huge.modules + (b.ModuleDeclaration.__new__(b.ModuleDeclaration),))
        with patch.object(s, "_size", side_effect=AssertionError("counter must not run")) as count:
            self.reject(prepared(), huge)
            count.assert_not_called()

    def test_unknown_foreign_top_level_before_getter(self):
        for parent, selected in ((Foreign(), worker()), (prepared(), Foreign())):
            self.reject(parent, selected)

    def test_foreign_fields_and_containers_before_comparison_iteration(self):
        selected = worker()
        for key in ("ordinal", "entry", "phase", "installation", "controls", "modules"):
            self.reject(prepared(), replace(selected, **{key: Foreign()}))
        for key in INSTALLATION_KEYS:
            self.reject(prepared(), worker(inst=replace(installation(), **{key: Foreign()})))
        for key in MODULE_KEYS:
            bad = replace(builtin(), **{key: Foreign()})
            self.reject(prepared(), replace(selected, modules=(control(), bad)))

    def test_bool_numbers_and_subclasses_rejected(self):
        class Text(str):
            pass
        class Tuple(tuple):
            pass
        class Worker(b.WorkerDeclaration):
            pass
        self.reject(prepared(), replace(worker(), ordinal=True))
        self.reject(prepared(), worker(inst=replace(installation(), version=(3, 12, True))))
        self.reject(prepared(), replace(worker(), entry=Text(b.ENTRIES[0])))
        self.reject(prepared(), replace(worker(), modules=Tuple(worker().modules)))
        base = worker()
        self.reject(prepared(), Worker(*(getattr(base, f.name) for f in fields(base))))

    def test_uninitialized_exact_dtos_return_fixed_rejection(self):
        self.reject(i.PreparedInput.__new__(i.PreparedInput), worker())
        self.reject(prepared(), b.WorkerDeclaration.__new__(b.WorkerDeclaration))
        self.reject(prepared(), replace(worker(), installation=b.InstallationDeclaration.__new__(b.InstallationDeclaration)))
        self.reject(prepared(), replace(worker(), modules=(b.ModuleDeclaration.__new__(b.ModuleDeclaration),)))
        self.reject(prepared(), worker(inst=replace(installation(), files=(b.FileFingerprint.__new__(b.FileFingerprint),))))

    def test_input_context_mapping_hash_and_limits_not_repaired(self):
        parent = prepared()
        variants = (replace(parent, commit="x" * 40), replace(parent, nonce=b"n" * 31),
                    replace(parent, raw27_binding="b" * 63), replace(parent, source_profile="other"),
                    replace(parent, sources=parent.sources[::-1]),
                    replace(parent, sources=(replace(parent.sources[0], sha256="c" * 64),) + parent.sources[1:]),
                    replace(parent, sources=(replace(parent.sources[0], body=b"x" * 131073),) + parent.sources[1:]))
        for value in variants:
            self.reject(value, worker())

    def test_selector_own_cached_names_and_duplicate_order_rejected(self):
        base = worker()
        for value in (replace(base, entry=b.ENTRIES[1]), replace(base, phase="POST_IMPORT"),
                      replace(base, modules=base.modules[::-1]), replace(base, modules=(builtin("Tests"),)),
                      replace(base, modules=(builtin("sys"), builtin("sys")), controls=())):
            self.reject(prepared(), value)

    def test_absolute_root_guards_not_weakened(self):
        for path in ("relative.py", "/synthetic/lib/../foreign.py", "/foreign/file.py"):
            row = replace(source(), origin=path, file=path, loaderPath=path)
            self.reject(prepared(), worker(modules=(control(), row)))

    def test_legacy_named_cap_preserved_not_caught_as_fit(self):
        selected = at_size(0, 16384)
        context = b.derive_binding_context(prepared(), 1)
        reported = b.ReportedProfile(context, selected.installation, selected.controls, selected.modules)
        self.assertEqual(b.match_reported_profile(selected, reported, context).issue, "METADATA_LIMIT")
        result = s.size_declared_profile(prepared(), selected)
        self.assertEqual(result.forms[0].bytes_including_header, 16384)
        self.assertFalse(result.forms[0].overflow)
        self.assertEqual(result.status, "DESIGN_SIZING_ONLY")

    def test_no_legacy_canonical_or_match_dispatch(self):
        with patch.object(b, "_canonical", side_effect=AssertionError("legacy canonical called")), \
             patch.object(b, "match_reported_profile", side_effect=AssertionError("matcher called")):
            self.assertEqual(s.size_declared_profile(prepared(), worker()).status, "DESIGN_SIZING_ONLY")

    def test_private_locators_nonce_and_payload_not_in_report(self):
        result = s.size_declared_profile(prepared(), worker())
        for forbidden in ("/synthetic", "synthetic-abi", b"n".hex() * 32, "synthetic raw"):
            self.assertNotIn(forbidden, repr(result))
        self.assertEqual(result.validation_scope, "PROJECT_SEMANTIC")
        for key in ("runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved"):
            self.assertIs(getattr(result, key), False)
        with self.assertRaises(FrozenInstanceError):
            result.status = "MATCHED"
        with self.assertRaises(FrozenInstanceError):
            result.forms[0].overflow = True

    def test_module_purity_and_project_dependency_boundary(self):
        tree = ast.parse((TOOLS / "dgn007_compact_profile_sizing.py").read_text(encoding="utf-8"))
        imports = {n.module for n in ast.walk(tree) if type(n) is ast.ImportFrom}
        imports.update(a.name for n in ast.walk(tree) if type(n) is ast.Import for a in n.names)
        self.assertEqual(imports, {"dataclasses", "json", "dgn007_import_profile_binding"})
        banned = {"open", "exec", "eval", "compile", "print", "__import__", "prepare_input", "_canonical", "match_reported_profile", "encode_input", "decode_input", "sha256", "Popen"}
        for node in ast.walk(tree):
            if type(node) is ast.Call:
                name = node.func.id if type(node.func) is ast.Name else node.func.attr if type(node.func) is ast.Attribute else ""
                self.assertNotIn(name, banned)


if __name__ == "__main__":
    unittest.main()
