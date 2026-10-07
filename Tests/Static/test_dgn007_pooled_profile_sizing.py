"""Unabhängige synthetische Feld- und Größenprüfungen des Poolentwurfs."""
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
import dgn007_pooled_profile_sizing as s
import dgn007_compact_profile_sizing as old
import dgn007_import_profile_binding as b
import dgn007_import_probe_input as i


def prepared(body=b"# synthetic raw\r\n"):
    return i.PreparedInput("a" * 40, "b" * 64, "dgn007-docker-sql-only/v1", b"n" * 32,
        tuple(i.SourceBytes(name, member, hashlib.sha256(body).hexdigest(), body)
              for name, member in i.MODULES))


def installation():
    return b.InstallationDeclaration(b.ASSUMPTION, "linux", "cpython", (3, 12, 14),
        "/synthetic/python", "/synthetic/python-target",
        tuple("/synthetic/p" + str(n) for n in range(4)), "synthetic-abi",
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
    path = "/synthetic/lib/" + name.replace(".", "/") + ".py"
    return b.ModuleDeclaration(name, name, name, path, path, kind,
        ("/synthetic/lib/package",) if kind == "SOURCE" else (), kind, name, path)


def frozen(name="_frozen_importlib", group=()):
    mn, sn = b.FROZEN_NAMES.get(name, (name, name))
    return b.ModuleDeclaration(name, mn, sn, "frozen", "/synthetic/lib/frozen.py",
                               "FROZEN", (), "FROZEN", aliasGroup=group)


def worker(ordinal=1, modules=None, inst=None):
    rows = (control(), builtin(), source(), source("synthetic_ext", "EXTENSION"), frozen()) if modules is None else modules
    rows = tuple(sorted(rows, key=lambda r: r.name))
    return b.WorkerDeclaration(ordinal, b.ENTRIES[ordinal - 1], "PRE_IMPORT", inst or installation(),
                               tuple(r.name for r in rows if r.kind == "CONTROL"), rows)


def canonical(v):
    return json.dumps(v, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


S_KEYS = ("assumption", "platform", "implementation", "version", "executable",
    "executable_target", "prefixes", "abi", "paths", "roots", "inert_zip", "flags", "finders", "hooks", "files")
P_KEYS = ("name", "moduleName", "specName", "origin", "file", "kind", "locations", "loader", "loaderName", "loaderPath", "aliasGroup")
D_KEYS = ("ordinal", "module", "member", "size", "sha256")
F_KEYS = ("path", "size", "sha256")
W_KEYS = ("ordinal", "entry", "phase", "installation", "controls", "modules")
K_KEYS = ("commit", "raw27_binding", "source_profile", "nonce", "modules", "ordinal", "entry", "phase")


def named(v):
    # Unabhängige benannte Referenz, keine Produktionsprojektion.
    if type(v) is tuple:
        return tuple(named(x) for x in v)
    if type(v) is bytes:
        return v.hex()
    if type(v) in (b.WorkerDeclaration, b.InstallationDeclaration, b.ModuleDeclaration,
                   b.FileFingerprint, b.BindingContext, b.SourceDescriptor):
        return {f.name: named(getattr(v, f.name)) for f in fields(v)}
    return v


def reference_payloads(parent, selected):
    wn = named(selected)
    cn = named(b.derive_binding_context(parent, selected.ordinal))
    metadata = i._metadata(parent)
    descriptors = lambda rows: tuple(tuple(row[k] for k in D_KEYS) for row in rows)
    ins = tuple(wn["installation"][k] for k in S_KEYS[:-1]) + (
        tuple(tuple(r[k] for k in F_KEYS) for r in wn["installation"]["files"]),)
    modules = tuple(tuple(row[k] for k in P_KEYS) for row in wn["modules"])
    inp = tuple(metadata[k] for k in ("protocol", "commit", "raw27_binding", "source_profile", "nonce")) + (
        descriptors(metadata["modules"]), metadata["context_sha256"])
    ctx = tuple(cn[k] for k in K_KEYS[:4]) + (descriptors(cn["modules"]),) + tuple(cn[k] for k in K_KEYS[5:])
    wrk = (wn["ordinal"], wn["entry"], wn["phase"], ins, wn["controls"], modules)
    return ((inp, wrk, ctx), (ctx, ins, wn["controls"], modules), (ins,), (wrk,), (ctx,))


def text_set(v):
    if type(v) is str:
        return {v}
    if type(v) is tuple:
        result = set()
        for x in v:
            result.update(text_set(x))
        return result
    return set()


def reference(parent, selected):
    result = []
    roles = ("METADATA", "REPORTED", "pooled-installation-declaration/v1",
             "pooled-worker-declaration/v1", "pooled-profile-binding-context/v1")
    for role, payload in zip(roles, reference_payloads(parent, selected)):
        pool = tuple(sorted(text_set(payload)))
        def project(v):
            if type(v) is str:
                return pool.index(v)
            if type(v) is tuple:
                return tuple(project(x) for x in v)
            return v
        result.append(("pooled-binding-design/v1", role, pool, project(payload)))
    return tuple(result)


def recover(projected, original, pool):
    # Erwartetes benanntes Schema disambiguiert Referenzen und semantische Integer.
    if type(original) is str:
        return pool[projected]
    if type(original) is tuple:
        if len(projected) != len(original):
            raise AssertionError("synthetic arity")
        return tuple(recover(x, y, pool) for x, y in zip(projected, original))
    return projected


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
        raise AssertionError("synthetic capacity")
    return replace(selected, installation=replace(selected.installation, prefixes=tuple(prefixes)))


def with_pool_count(target):
    selected = worker()
    base = len(reference(prepared(), selected)[0][2])
    extra = tuple("/synthetic/lib/path" + str(n).zfill(3) for n in range(target - base))
    rows = tuple(replace(r, locations=r.locations + extra) if r.name == "synthetic_package" else r
                 for r in selected.modules)
    return replace(selected, modules=rows)


class Foreign:
    def __getattribute__(self, _):
        raise RuntimeError("synthetic-private-getter")
    def __eq__(self, _):
        raise RuntimeError("synthetic-private-equality")
    def __iter__(self):
        raise RuntimeError("synthetic-private-iteration")


class PoolSizingTests(unittest.TestCase):
    def rejected(self, parent=None, selected=None, issue="INVALID_RECORD"):
        result = s.size_declared_profile(prepared() if parent is None else parent,
                                        worker() if selected is None else selected)
        self.assertEqual((result.status, result.issue, result.forms, result.ordinal),
                         ("REJECTED_POOL_DESIGN_SIZING", issue, (), None))
        self.assertNotIn("synthetic-private", repr(result))
        return result

    def test_all_three_ordinals_full_reference(self):
        for ordinal in (1, 2, 3):
            parent, selected = prepared(), worker(ordinal)
            expected = reference(parent, selected)
            self.assertEqual(s._forms(parent, selected), expected)
            report = s.size_declared_profile(parent, selected)
            self.assertEqual(report.status, "POOL_DESIGN_SIZING_ONLY")
            self.assertEqual(report.ordinal, ordinal)
            self.assertEqual(tuple(r.bytes_including_header for r in report.forms),
                             tuple(16 + len(canonical(v)) for v in expected))
            self.assertEqual(tuple(r.pool_count for r in report.forms), tuple(len(v[2]) for v in expected))

    def test_complete_independent_recovery(self):
        parent, selected = prepared(), worker()
        for form, expected in zip(s._forms(parent, selected), reference_payloads(parent, selected)):
            self.assertEqual(recover(form[3], expected, form[2]), expected)

    def test_schema_retains_every_dataclass_field(self):
        for cls, keys in ((b.InstallationDeclaration, S_KEYS), (b.ModuleDeclaration, P_KEYS),
                          (b.SourceDescriptor, D_KEYS), (b.FileFingerprint, F_KEYS),
                          (b.WorkerDeclaration, W_KEYS), (b.BindingContext, K_KEYS)):
            self.assertEqual(tuple(f.name for f in fields(cls)), keys)
            self.assertEqual(s._FIELDS[cls], keys)

    def test_physical_descriptor_arrays(self):
        forms = s._forms(prepared(), worker())
        payload = forms[0][3]
        self.assertEqual(len(payload[0][5]), 9)
        self.assertEqual(len(payload[2][4]), 9)
        self.assertIsNot(payload[0][5], payload[2][4])
        self.assertEqual(payload[0][5], payload[2][4])
        self.assertEqual(len(forms[1][3][0][4]), 9)
        self.assertEqual(len(forms[4][3][0][4]), 9)

    def test_original_input_context_digest_and_raw_bytes(self):
        parent = prepared(b"# synthetic\r\n")
        form = s._forms(parent, worker())[0]
        self.assertEqual(form[2][form[3][0][6]], i._metadata(parent)["context_sha256"])
        self.assertNotEqual(i._metadata(parent)["context_sha256"], i._metadata(prepared(b"# synthetic\n"))["context_sha256"])
        self.assertTrue(all(r.body == b"# synthetic\r\n" for r in parent.sources))

    def test_pool_256_is_valid(self):
        selected = with_pool_count(256)
        self.assertEqual(len(reference(prepared(), selected)[0][2]), 256)
        result = s.size_declared_profile(prepared(), selected)
        self.assertEqual(result.issue, "NONE")
        self.assertEqual(result.forms[0].pool_count, 256)

    def test_pool_257_rejected(self):
        self.rejected(selected=with_pool_count(257), issue="POOL_LIMIT")

    def test_pool_is_sorted_unique_and_only_used(self):
        for actual, original in zip(s._forms(prepared(), worker()), reference_payloads(prepared(), worker())):
            self.assertEqual(actual[2], tuple(sorted(text_set(original))))
            self.assertEqual(len(actual[2]), len(set(actual[2])))

    def test_each_form_has_own_pool(self):
        forms = s._forms(prepared(), worker())
        self.assertEqual(len({id(v[2]) for v in forms}), 5)
        self.assertNotIn(i._metadata(prepared())["context_sha256"], forms[2][2])

    def test_null_empty_text_and_empty_arrays_are_distinct(self):
        form = s._forms(prepared(), worker())[0]
        row = form[3][1][5][0]
        self.assertIsNone(row[2])
        self.assertEqual(form[2][row[3]], "")
        self.assertEqual(row[6], ())

    def test_reference_zero_does_not_replace_real_integer_zero(self):
        form = s._forms(prepared(), worker())[0]
        self.assertEqual(form[3][0][5][0][0], 0)
        self.assertEqual(form[3][1][3][11], (1, 1, 1, 1, 1, 0))
        original = reference_payloads(prepared(), worker())[0]
        self.assertEqual(recover(form[3], original, form[2]), original)

    def test_text_equal_to_tag_is_retained_as_payload(self):
        selected = worker(inst=replace(installation(), abi=s.DESIGN_TAG))
        form = s._forms(prepared(), selected)[2]
        self.assertEqual(form[2][form[3][0][7]], s.DESIGN_TAG)
        self.assertEqual(form[0], s.DESIGN_TAG)

    def test_unicode_escaping_matches_stdlib(self):
        for text in ("synthetic\u007f", "syntheticé", "synthetic😀", "synthetic\t\n\"\\"):
            selected = worker(inst=replace(installation(), abi=text))
            result = s.size_declared_profile(prepared(), selected)
            self.assertEqual(tuple(r.bytes_including_header for r in result.forms),
                tuple(16 + len(canonical(v)) for v in reference(prepared(), selected)))

    def test_exact_utf8_field_boundary(self):
        selected = worker(inst=replace(installation(), abi="é" * 2048))
        self.assertEqual(s.size_declared_profile(prepared(), selected).issue, "NONE")
        self.rejected(selected=worker(inst=replace(installation(), abi="é" * 2049)))

    def test_surrogate_and_nul_rejected(self):
        for text in ("synthetic\ud800", "synthetic\0"):
            self.rejected(selected=worker(inst=replace(installation(), abi=text)))

    def test_mixed_alias_remains_empty(self):
        selected = worker(modules=(control(), frozen("_collections_abc"), source("collections.abc")))
        self.assertEqual(s._forms(prepared(), selected), reference(prepared(), selected))

    def test_complete_frozen_alias_and_singleton(self):
        pair = tuple(sorted(("_frozen_importlib", "importlib._bootstrap")))
        selected = worker(modules=(control(), frozen(pair[0], pair), frozen(pair[1], pair)))
        self.assertEqual(s._forms(prepared(), selected), reference(prepared(), selected))
        self.assertEqual(s.size_declared_profile(prepared(), worker()).issue, "NONE")

    def test_invalid_alias_and_own_names(self):
        self.rejected(selected=worker(modules=(control(), frozen(group=("_frozen_importlib", "importlib._bootstrap")))))
        self.rejected(selected=worker(modules=(control(), builtin("Tests"))))

    def test_four_valid_caps_and_cap_plus_one(self):
        for index in (0, 1, 2, 3):
            for target in (16384, 16385):
                selected = at_size(index, target)
                result = s.size_declared_profile(prepared(), selected)
                self.assertEqual(result.issue, "NONE")
                self.assertEqual(result.forms[index].bytes_including_header, target)
                self.assertEqual(result.forms[index].overflow, target > 16384)

    def test_all_sizes_retained_for_multiple_byte_overflows(self):
        selected = at_size(2, 16385)
        result = s.size_declared_profile(prepared(), selected)
        self.assertEqual(result.status, "POOL_DESIGN_SIZING_OVERFLOW")
        self.assertEqual(len(result.forms), 5)
        self.assertTrue(all(result.forms[n].overflow for n in (0, 1, 2, 3)))
        self.assertFalse(result.forms[4].overflow)

    def test_context_honest_upper_bound_and_separate_counter_math(self):
        parent = prepared(b"x" * 100000)
        for ordinal in (1, 2, 3):
            form = s._forms(parent, worker(ordinal))[4]
            self.assertLess(s._size(form), 16384)
        # Interne Zählprobe, ausdrücklich kein gültiger Kontext/Decoderinput.
        for target in (16384, 16385):
            value = (s.DESIGN_TAG, s.ROLES[4], ("",), (0,))
            delta = target - s._size(value)
            self.assertEqual(s._size((s.DESIGN_TAG, s.ROLES[4], ("x" * delta,), (0,))), target)

    def test_small_pool_form_does_not_call_or_heal_legacy(self):
        selected = worker(inst=replace(installation(), prefixes=("/synthetic/" + "x" * 3000,) * 4))
        self.assertEqual(old.size_declared_profile(prepared(), selected).status, "DESIGN_SIZING_OVERFLOW")
        with patch.object(b, "_canonical", side_effect=AssertionError("legacy called")), \
             patch.object(b, "match_reported_profile", side_effect=AssertionError("matcher called")):
            self.assertEqual(s.size_declared_profile(prepared(), selected).status, "POOL_DESIGN_SIZING_ONLY")
        self.assertEqual(old.size_declared_profile(prepared(), selected).status, "DESIGN_SIZING_OVERFLOW")

    def test_late_malformed_dominates_earlier_byte_overflow(self):
        selected = at_size(0, 16385)
        bad = replace(selected.modules[-1], loaderPath=Foreign())
        self.rejected(selected=replace(selected, modules=selected.modules[:-1] + (bad,)))

    def test_late_malformed_dominates_earlier_pool_overflow(self):
        selected = with_pool_count(257)
        bad = replace(selected.modules[-1], loaderPath=Foreign())
        self.rejected(selected=replace(selected, modules=selected.modules[:-1] + (bad,)))

    def test_foreign_objects_before_getters_equality_or_iteration(self):
        self.rejected(parent=Foreign())
        self.rejected(selected=Foreign())
        for key in W_KEYS:
            self.rejected(selected=replace(worker(), **{key: Foreign()}))
        for key in S_KEYS:
            self.rejected(selected=worker(inst=replace(installation(), **{key: Foreign()})))
        for key in P_KEYS:
            selected = worker()
            row = replace(selected.modules[-1], **{key: Foreign()})
            self.rejected(selected=replace(selected, modules=selected.modules[:-1] + (row,)))

    def test_uninitialized_and_subclass_records(self):
        self.rejected(parent=i.PreparedInput.__new__(i.PreparedInput))
        self.rejected(selected=b.WorkerDeclaration.__new__(b.WorkerDeclaration))
        class Sub(b.WorkerDeclaration):
            pass
        self.rejected(selected=Sub(*[getattr(worker(), k) for k in W_KEYS]))

    def test_bools_and_wrong_primitive_containers(self):
        for value in (True, 0, 4, "1"):
            self.rejected(selected=replace(worker(), ordinal=value))
        self.rejected(selected=replace(worker(), modules=list(worker().modules)))
        self.rejected(selected=worker(inst=replace(installation(), flags=(True, 1, 1, 1, 1, 0))))

    def test_many_repeated_locations_fail_before_projection(self):
        locations = ("/synthetic/lib/location",) * 256
        rows = tuple(replace(source("synthetic" + str(n).zfill(3)), locations=locations) for n in range(65))
        selected = worker(modules=(control(),) + rows)
        with patch.object(s, "_project", side_effect=AssertionError("early projection")):
            self.rejected(selected=selected, issue="NODE_LIMIT")

    def test_repeated_large_text_is_shared_not_copied(self):
        text = "/synthetic/lib/" + "x" * (4096 - len("/synthetic/lib/"))
        selected = worker(modules=(control(), replace(source(), locations=(text,) * 128)))
        form = s._forms(prepared(), selected)[0]
        expected = reference_payloads(prepared(), selected)[0]
        recovered = recover(form[3], expected, form[2])
        row = recovered[1][5][-1]
        self.assertEqual(len(row[6]), 128)
        self.assertTrue(all(v is row[6][0] for v in row[6]))
        self.assertEqual(recovered, expected)

    def test_internal_depth_and_integer_and_sequence_guards(self):
        with self.assertRaises(s._Rejected) as caught:
            s._preflight(((((((((),),),),),),),))
        self.assertEqual(str(caught.exception), "DEPTH_LIMIT")
        for value in ((True,), (-1,), (100000000,), ("x",) * 257, (Foreign(),)):
            with self.assertRaises(s._Rejected):
                s._preflight(value)

    def test_exact_internal_node_cap_counts_physical_repetition_and_pool(self):
        # E4/Tag/Rolle/Poolcontainer4 + Payload1 + 64Arrays + Pooltext1
        # + 16298 physische Textpositionen = exakt16368 Knoten.
        payload = (("synthetic",) * 256,) * 63 + (("synthetic",) * 170,)
        self.assertEqual(s._preflight(payload), ("synthetic",))
        with self.assertRaises(s._Rejected) as caught:
            s._preflight(payload[:-1] + (("synthetic",) * 171,))
        self.assertEqual(str(caught.exception), "NODE_LIMIT")

    def test_exact_internal_eight_array_levels(self):
        value = ()
        for _ in range(6):
            value = (value,)
        self.assertEqual(s._preflight(value), ())  # Payload beginnt bei Ebene2.
        with self.assertRaises(s._Rejected) as caught:
            s._preflight((value,))
        self.assertEqual(str(caught.exception), "DEPTH_LIMIT")

    def test_missing_records_and_fields_without_raw_exception(self):
        selected = worker()
        for missing in (b.InstallationDeclaration.__new__(b.InstallationDeclaration), None):
            self.rejected(selected=replace(selected, installation=missing))
        self.rejected(selected=replace(selected, modules=(b.ModuleDeclaration.__new__(b.ModuleDeclaration),)))
        parent = prepared()
        self.rejected(parent=replace(parent, sources=parent.sources[:-1] + (i.SourceBytes.__new__(i.SourceBytes),)))

    def test_invalid_descriptor_body_hash_and_nonce(self):
        parent = prepared()
        bad = replace(parent.sources[-1], sha256="c" * 64)
        self.rejected(parent=replace(parent, sources=parent.sources[:-1] + (bad,)))
        self.rejected(parent=replace(parent, nonce=b"n" * 31))

    def test_public_report_is_frozen_private_and_all_flags_false(self):
        result = s.size_declared_profile(prepared(), worker())
        for key in ("runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved"):
            self.assertIs(getattr(result, key), False)
        self.assertEqual(result.validation_scope, "PROJECT_SEMANTIC")
        self.assertNotIn("/synthetic", repr(result))
        with self.assertRaises(FrozenInstanceError):
            result.status = "changed"
        with self.assertRaises(FrozenInstanceError):
            result.forms[0].pool_count = 0

    def test_tag_and_domains_and_header_are_in_all_sizes(self):
        forms = s._forms(prepared(), worker())
        self.assertEqual(tuple(v[1] for v in forms), s.ROLES)
        for form in forms:
            self.assertEqual(s._size(form), 16 + len(canonical(form)))
            self.assertGreater(s._size(form), len(canonical(form[2:])))

    def test_pure_imports_and_no_io_or_digest_or_decoder(self):
        tree = ast.parse((TOOLS / "dgn007_pooled_profile_sizing.py").read_text(encoding="utf-8"))
        imports = {n.module for n in ast.walk(tree) if type(n) is ast.ImportFrom}
        imports.update(a.name for n in ast.walk(tree) if type(n) is ast.Import for a in n.names)
        self.assertEqual(imports, {"dataclasses", "json", "dgn007_compact_profile_sizing"})
        calls = {n.func.id for n in ast.walk(tree) if type(n) is ast.Call and type(n.func) is ast.Name}
        self.assertFalse(calls & {"open", "exec", "eval", "compile", "print", "__import__"})
        attrs = {n.attr for n in ast.walk(tree) if type(n) is ast.Attribute}
        self.assertFalse(attrs & {"Popen", "run", "decode_input", "prepare_input", "sha256", "_canonical", "match_reported_profile"})


if __name__ == "__main__":
    unittest.main()
