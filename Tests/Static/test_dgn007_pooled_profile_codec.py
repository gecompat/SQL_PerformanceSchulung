"""Portable synthetische Codecgegenproben; kein Worker oder Kandidatenimport."""
from dataclasses import FrozenInstanceError, fields, replace
import ast
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))
import dgn007_pooled_profile_codec as c

b, i = c.b, c.b.input82


def parent(body=b"# synthetic\r\n"):
    return i.PreparedInput("a" * 40, "b" * 64, "dgn007-docker-sql-only/v1", b"n" * 32,
        tuple(i.SourceBytes(name, member, hashlib.sha256(body).hexdigest(), body)
              for name, member in i.MODULES))


def installation():
    return b.InstallationDeclaration(b.ASSUMPTION, "linux", "cpython", (3, 12, 14),
        "/synthetic/python", "/synthetic/python-target", ("/p0", "/p1", "/p2", "/p3"),
        "synthetic-abi", ("/lib", "/lib/dyn", "/python312.zip"), ("/lib", "/lib/dyn"),
        "/python312.zip", (1, 1, 1, 1, 1, 0), ("BUILTIN", "FROZEN", "PATH"),
        ("ZIPIMPORTER", "FILEFINDER"), (b.FileFingerprint("/synthetic/python-target", 7, "c" * 64),))


def module(name="package", kind="SOURCE", group=()):
    if kind == "CONTROL":
        return b.ModuleDeclaration(name, name, None, "", "/control.py", kind, (), "NONE")
    if kind == "BUILTIN":
        return b.ModuleDeclaration(name, name, name, "built-in", "", kind, (), kind)
    if kind == "FROZEN":
        mn, sn = b.FROZEN_NAMES.get(name, (name, name))
        return b.ModuleDeclaration(name, mn, sn, "frozen", "/lib/frozen.py", kind, (), kind,
                                   aliasGroup=group)
    path = "/lib/" + name + ".py"
    return b.ModuleDeclaration(name, name, name, path, path, kind,
        ("/lib/package",) if kind == "SOURCE" else (), kind, name, path)


def worker(ordinal=1, rows=None, inst=None):
    if rows is None:
        rows = (module("__main__", "CONTROL"), module("sys", "BUILTIN"), module(),
                module("extension", "EXTENSION"), module("_frozen_importlib", "FROZEN"))
    rows = tuple(sorted(rows, key=lambda x: x.name))
    return b.WorkerDeclaration(ordinal, b.ENTRIES[ordinal - 1], "PRE_IMPORT", inst or installation(),
                               tuple(r.name for r in rows if r.kind == "CONTROL"), rows)


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def frame(value, role=0):
    raw = canonical(value)
    return c.HEADER.pack(c.MAGIC, role + 1, len(raw)) + raw


def rawframe(raw, role=0):
    return c.HEADER.pack(c.MAGIC, role + 1, len(raw)) + raw


def named(v):
    if type(v) is tuple:
        return tuple(named(x) for x in v)
    if type(v) is bytes:
        return v.hex()
    if type(v) in (b.WorkerDeclaration, b.InstallationDeclaration, b.ModuleDeclaration,
                   b.FileFingerprint, b.SourceDescriptor, b.BindingContext):
        return {f.name: named(getattr(v, f.name)) for f in fields(v)}
    return v


def reference(p, w, mutate=None):
    # Unabhängige benannte Felder; keine Sizerprojektion als Erwartungswert.
    wn = named(w)
    cn = named(b.derive_binding_context(p, w.ordinal))
    m = i._metadata(p)
    ds = lambda rows: tuple(tuple(r[k] for k in ("ordinal", "module", "member", "size", "sha256")) for r in rows)
    sk = ("assumption", "platform", "implementation", "version", "executable", "executable_target",
          "prefixes", "abi", "paths", "roots", "inert_zip", "flags", "finders", "hooks")
    pk = ("name", "moduleName", "specName", "origin", "file", "kind", "locations", "loader", "loaderName", "loaderPath", "aliasGroup")
    ins = tuple(wn["installation"][k] for k in sk) + (
        tuple(tuple(r[k] for k in ("path", "size", "sha256")) for r in wn["installation"]["files"]),)
    mods = tuple(tuple(r[k] for k in pk) for r in wn["modules"])
    wr = (wn["ordinal"], wn["entry"], wn["phase"], ins, wn["controls"], mods)
    kr = tuple(cn[k] for k in ("commit", "raw27_binding", "source_profile", "nonce")) + (ds(cn["modules"]),) + (
        cn["ordinal"], cn["entry"], cn["phase"])
    ip = tuple(m[k] for k in ("protocol", "commit", "raw27_binding", "source_profile", "nonce")) + (ds(m["modules"]), m["context_sha256"])
    payloads = ((ip, wr, kr), (kr, ins, wn["controls"], mods), (ins,), (wr,), (kr,))
    if mutate is not None:
        payloads = mutate(payloads)

    def texts(value):
        if type(value) is str:
            return {value}
        if type(value) is tuple:
            return set().union(*(texts(x) for x in value))
        return set()

    def pack(value, pool):
        if type(value) is str:
            return pool.index(value)
        if type(value) is tuple:
            return tuple(pack(x, pool) for x in value)
        return value

    result = []
    for role, payload in zip(c.ROLES, payloads):
        pool = tuple(sorted(texts(payload)))
        result.append((c.VERSION, role, pool, pack(payload, pool)))
    return tuple(result)


def at_size(p, w, index, target):
    remaining = target - (16 + len(canonical(reference(p, w)[index])))
    prefixes = list(w.installation.prefixes)
    for n in range(4):
        delta = min(remaining, 4096 - len(prefixes[n]))
        if delta < 0:
            raise AssertionError("synthetic size")
        prefixes[n] += "x" * delta
        remaining -= delta
    if remaining:
        raise AssertionError("synthetic capacity")
    return replace(w, installation=replace(w.installation, prefixes=tuple(prefixes)))


class Foreign:
    def __getattr__(self, _):
        raise RuntimeError("synthetic-private")
    def __eq__(self, _):
        raise RuntimeError("synthetic-private")
    def __iter__(self):
        raise RuntimeError("synthetic-private")


class CodecTests(unittest.TestCase):
    def setUp(self):
        self.p, self.w = parent(), worker()
        self.forms = reference(self.p, self.w)
        self.frames = tuple(frame(v, n) for n, v in enumerate(self.forms))

    def decode(self, f, role=0, **changes):
        kwargs = dict(expected_version=c.VERSION, expected_role=c.ROLES[role],
                      prepared=self.p, expected_worker=self.w)
        kwargs.update(changes)
        return c.decode_declared_form(f, **kwargs)

    def reject(self, operation, issue=None):
        with self.assertRaises(c.CodecRejected) as caught:
            operation()
        error = caught.exception
        if issue:
            self.assertEqual(str(error), issue)
        self.assertIsNone(error.__context__)
        self.assertIsNone(error.__cause__)
        self.assertNotIn("synthetic-private", str(error))
        self.assertNotIn("/synthetic", str(error))
        return str(error)

    def test_all_roles_three_ordinals_independent_reference(self):
        for ordinal in (1, 2, 3):
            w = worker(ordinal)
            expected = reference(self.p, w)
            actual = c.encode_declared_formset(self.p, w, expected_version=c.VERSION)
            self.assertEqual(actual, tuple(frame(v, n) for n, v in enumerate(expected)))
            for n, f in enumerate(actual):
                self.assertEqual(c.encode_declared_form(self.p, w, expected_version=c.VERSION, role=c.ROLES[n]), f)
                result = self.decode(f, n, expected_worker=w)
                self.assertEqual(result.role, c.ROLES[n])
                self.assertEqual(result.declared_context_match, n in (0, 1, 4))
                context = b.derive_binding_context(self.p, ordinal)
                expected_dtos = ((result.payload[0], w, context),
                    (b.ReportedProfile(context, w.installation, w.controls, w.modules),),
                    (w.installation,), (w,), (context,))
                self.assertEqual(result.payload, expected_dtos[n])
            report = c.match_declared_formset(actual, self.p, w, expected_version=c.VERSION)
            self.assertEqual(report.status, "MATCHED_DECLARED_FORMSET")

    def test_exact_recovered_dtos_and_input_fields(self):
        m = self.decode(self.frames[0]).payload
        self.assertEqual(m[1], self.w)
        self.assertEqual(m[2], b.derive_binding_context(self.p, 1))
        self.assertEqual(m[0][-1], i._metadata(self.p)["context_sha256"])
        r = self.decode(self.frames[1], 1).payload[0]
        self.assertEqual(r.installation, self.w.installation)
        self.assertEqual(r.modules, self.w.modules)
        self.assertEqual(r.controls, self.w.controls)
        self.assertEqual(self.decode(self.frames[2], 2).payload, (self.w.installation,))
        self.assertEqual(self.decode(self.frames[3], 3).payload, (self.w,))

    def test_domains_independent_digest_reference(self):
        expected = tuple(hashlib.sha256(canonical(f)).hexdigest() for f in self.forms[2:])
        for report in (c.digest_declared_profile(self.p, self.w, expected_version=c.VERSION),
                       c.match_declared_formset(self.frames, self.p, self.w, expected_version=c.VERSION)):
            self.assertEqual((report.installation_digest, report.worker_digest, report.context_digest), expected)
            self.assertEqual(len(set(expected)), 3)
            self.assertFalse(report.runtime_attested or report.trust_attested or report.method_approved or report.import_used_bytes_attested)
        self.assertNotEqual(expected[0], hashlib.sha256(self.frames[2]).hexdigest())
        self.assertNotEqual(expected[0], hashlib.sha256(b._canonical(["installation-declaration", b._value(self.w.installation)])).hexdigest())

    def test_frozen_private_result_and_replay(self):
        result = self.decode(self.frames[0])
        with self.assertRaises(FrozenInstanceError):
            result.role = "OTHER"
        self.assertNotIn("/", repr(result))
        self.assertFalse(result.runtime_attested or result.trust_attested or result.method_approved)
        self.assertEqual(self.decode(self.frames[0]), result)

    def test_sw_never_establish_nonce_or_parent_binding(self):
        p = replace(self.p, nonce=b"x" * 32, commit="f" * 40)
        for n in (2, 3):
            result = self.decode(self.frames[n], n, prepared=p)
            self.assertFalse(result.declared_context_match)
        for n in (0, 1, 4):
            self.reject(lambda n=n: self.decode(self.frames[n], n, prepared=p), "DECLARATION_MISMATCH")

    def test_header_actual_layout_and_exact_end(self):
        self.assertEqual(c.HEADER.size, 16)
        for n, f in enumerate(self.frames):
            self.assertEqual(c.HEADER.unpack_from(f), (b"DGNP001\0", n + 1, len(f) - 16))
            for damaged in (f[:-1], f + b"x", c.HEADER.pack(c.MAGIC, n + 1, 0) + f[16:]):
                self.reject(lambda damaged=damaged, n=n: self.decode(damaged, n), "FRAME_LENGTH")

    def test_dispatch_before_parser_or_foreignoperation(self):
        with patch.object(c, "_Parser", side_effect=AssertionError):
            for version in (None, True, Foreign(), "old/v1"):
                self.reject(lambda version=version: self.decode(b"", expected_version=version), "VERSION_SELECTION")
            for role in (None, 1, Foreign(), "INSTALLATION"):
                self.reject(lambda role=role: self.decode(b"", expected_role=role), "ROLE_SELECTION")
            self.reject(lambda: self.decode(c.HEADER.pack(b"DGNI001\0", 1, 1) + b"x"), "FRAME_MAGIC")
            self.reject(lambda: self.decode(c.HEADER.pack(c.MAGIC, 2, 1) + b"x"), "FRAME_ROLE")

    def test_frame_exact_type_and_limit_before_parse(self):
        class Bytes(bytes):
            pass
        for bad in (Foreign(), bytearray(self.frames[0]), Bytes(self.frames[0]), None):
            self.reject(lambda bad=bad: self.decode(bad), "FRAME_TYPE")
        with patch.object(c, "_Parser", side_effect=AssertionError):
            for bad in (b"", b"x" * 16385):
                self.reject(lambda bad=bad: self.decode(bad), "FRAME_LIMIT")

    def test_json_tag_role_before_references(self):
        bad = list(self.forms[0])
        bad[0], bad[3] = "compact-binding-design", (99999999,)
        self.reject(lambda: self.decode(frame(bad)), "VERSION_MISMATCH")
        bad[0], bad[1] = c.VERSION, c.ROLES[1]
        self.reject(lambda: self.decode(frame(bad)), "ROLE_MISMATCH")

    def test_parser_forbidden_primitives_and_objects(self):
        for token in (b"{}", b"true", b"false", b"-1", b"1.0", b"1e1", b"NaN", b"Infinity", b"+1", b"01", b"100000000"):
            self.reject(lambda token=token: self.decode(rawframe(token)))

    def test_parser_ascii_and_surrogate_forms(self):
        for text in (b'"\x00"', b'"\xff"', b'"\\u0000"', b'"\\ud800"', b'"\\udc00"',
                     b'"\\ud800\\u0061"', b'"\\x01"', b'"unterminated'):
            self.reject(lambda text=text: self.decode(rawframe(text)))

    def test_canonical_alternative_encodings_rejected(self):
        raw = self.frames[0][16:]
        for changed in (raw + b" ", b" " + raw, raw.replace(b'[', b'[ ', 1),
                        raw.replace(b'pooled', b'\\u0070ooled', 1)):
            self.reject(lambda changed=changed: self.decode(rawframe(changed)))

    def test_parser_node_depth_sequence_preallocation_caps(self):
        parser = c._Parser(b'[' * 9 + b']' * 9)
        self.reject(lambda: parser.value(), "DEPTH_LIMIT")
        parser = c._Parser(b'[' + b','.join([b'0'] * 257) + b']')
        self.reject(lambda: parser.value(), "SEQUENCE_LIMIT")
        parser = c._Parser(b'0')
        parser.nodes = 16368
        self.reject(lambda: parser.value(), "NODE_LIMIT")
        self.assertEqual(c._Parser(b'[' * 8 + b']' * 8).value(), ((((((((),),),),),),),))

    def test_parser_text_utf8_boundary_before_join(self):
        self.assertEqual(c._Parser(canonical("é" * 2048)).value(), "é" * 2048)
        for text in ("é" * 2049, "x" * 4097):
            self.reject(lambda text=text: c._Parser(canonical(text)).value(), "TEXT_LIMIT")

    def test_unicode_exact_roundtrip(self):
        for abi in ('é中😀\u007f"\\\n\t', c.VERSION):
            w = replace(self.w, installation=replace(self.w.installation, abi=abi))
            f = c.encode_declared_form(self.p, w, expected_version=c.VERSION, role=c.ROLES[2])
            self.assertEqual(self.decode(f, 2, expected_worker=w).payload[0].abi, abi)

    def test_pool_duplicate_order_unused_and_257(self):
        for pool, label in ((self.forms[0][2] + (self.forms[0][2][-1],), "POOL_FORM"),
                            (tuple(reversed(self.forms[0][2])), "POOL_FORM"),
                            (self.forms[0][2] + ("zzzz-unused",), "POOL_UNUSED"),
                            (tuple("x" + str(n) for n in range(257)), "SEQUENCE_LIMIT")):
            bad = self.forms[0][:2] + (pool, self.forms[0][3])
            self.reject(lambda bad=bad: self.decode(frame(bad)), label)

    def test_schema_all_arities_and_position_types(self):
        for n in range(5):
            bad = self.forms[n][:3] + (self.forms[n][3] + (0,),)
            self.reject(lambda bad=bad, n=n: self.decode(frame(bad, n), n), "SCHEMA_FORM")
        bad = list(self.forms[3][3][0])
        bad[0] = None
        payload = (tuple(bad),)
        self.reject(lambda: self.decode(frame(self.forms[3][:3] + (payload,), 3), 3), "POSITION_TYPE")

    def test_semantic_integer_zero_not_text_reference(self):
        result = self.decode(self.frames[0]).payload
        self.assertEqual(result[2].modules[0].ordinal, 0)
        self.assertEqual(result[1].installation.flags[-1], 0)
        self.assertIn("", self.forms[0][2])
        controlrow = next(r for r in result[1].modules if r.kind == "CONTROL")
        self.assertIsNone(controlrow.specName)
        self.assertEqual(controlrow.origin, "")
        self.assertEqual(controlrow.locations, ())

    def test_reference_out_of_range_and_negative(self):
        ip = list(self.forms[0][3][0])
        ip[0] = len(self.forms[0][2])
        bad = self.forms[0][:3] + ((tuple(ip), *self.forms[0][3][1:]),)
        self.reject(lambda: self.decode(frame(bad)), "REFERENCE_RANGE")
        ip[0] = -1
        bad = self.forms[0][:3] + ((tuple(ip), *self.forms[0][3][1:]),)
        self.reject(lambda: self.decode(frame(bad)), "JSON_FORM")

    def test_both_descriptor_arrays_input_original_digest(self):
        payload = self.forms[0][3]
        self.assertEqual(payload[0][5], payload[2][4])
        self.assertIsNot(payload[0][5], payload[2][4])
        ip = list(payload[0])
        ds = list(ip[5])
        ds[0] = (ds[0][0], ds[0][1], ds[0][2], ds[0][3] + 1, ds[0][4])
        ip[5] = tuple(ds)
        self.reject(lambda: self.decode(frame(self.forms[0][:3] + ((tuple(ip), *payload[1:]),))), "INPUT_BINDING")
        def wrong_digest(values):
            ip, wr, kr = values[0]
            return ((ip[:-1] + ("f" * 64,), wr, kr), *values[1:])
        changed = reference(self.p, self.w, wrong_digest)
        self.reject(lambda: self.decode(frame(changed[0])), "INPUT_BINDING")

    def test_rawbody_exchange_crlf_and_context_mismatch(self):
        exchanged = parent(b"# synthetic\n")
        self.reject(lambda: self.decode(self.frames[0], prepared=exchanged), "DECLARATION_MISMATCH")
        bad = replace(self.p, sources=(replace(self.p.sources[0], body=b"other"), *self.p.sources[1:]))
        self.reject(lambda: self.decode(self.frames[0], prepared=bad), "INVALID_RECORD")

    def test_frozen_pairs_singletons_and_mixed_keep_shapes(self):
        rows = (module("_collections_abc", "FROZEN"), module("collections.abc", "SOURCE"))
        w = worker(rows=rows)
        actual = c.encode_declared_formset(self.p, w, expected_version=c.VERSION)
        self.assertTrue(all(r.aliasGroup == () for r in self.decode(actual[3], 3, expected_worker=w).payload[0].modules))
        pair = tuple(sorted(("_frozen_importlib", "importlib._bootstrap")))
        w = worker(rows=tuple(module(name, "FROZEN", pair) for name in pair))
        self.assertEqual(self.decode(c.encode_declared_formset(self.p, w, expected_version=c.VERSION)[3], 3, expected_worker=w).payload[0], w)
        w = worker(rows=(module("_frozen_importlib", "FROZEN", pair),))
        self.reject(lambda: c.encode_declared_formset(self.p, w, expected_version=c.VERSION), "INVALID_RECORD")

    def test_contaminated_fields_never_accepted_by_equal_caller(self):
        for row in (module("Tests", "BUILTIN"), replace(module(), file="/outside.py", origin="/outside.py", loaderPath="/outside.py")):
            w = worker(rows=(row,))
            self.reject(lambda w=w: c.encode_declared_form(self.p, w, expected_version=c.VERSION, role=c.ROLES[2]), "INVALID_RECORD")

    def test_foreign_and_uninitialized_before_callbacks(self):
        for bad in (Foreign(), b.WorkerDeclaration.__new__(b.WorkerDeclaration), replace(self.w, ordinal=True),
                    replace(self.w, controls=Foreign()), replace(self.w, modules=(Foreign(),)),
                    replace(self.w, installation=replace(self.w.installation, abi=Foreign()))):
            self.reject(lambda bad=bad: c.encode_declared_formset(self.p, bad, expected_version=c.VERSION), "INVALID_RECORD")
        for bad in (Foreign(), i.PreparedInput.__new__(i.PreparedInput), replace(self.p, nonce=Foreign())):
            self.reject(lambda bad=bad: c.digest_declared_profile(bad, self.w, expected_version=c.VERSION), "INVALID_RECORD")

    def test_late_malformed_dominates_earlier_mismatch(self):
        other = replace(self.w, installation=replace(self.w.installation, abi="other"))
        frames = list(c.encode_declared_formset(self.p, other, expected_version=c.VERSION))
        bad = list(self.forms[4][3][0])
        bad[5] = None
        frames[4] = frame(self.forms[4][:3] + ((tuple(bad),),), 4)
        report = c.match_declared_formset(tuple(frames), self.p, self.w, expected_version=c.VERSION)
        self.assertEqual(report.issue, "POSITION_TYPE")
        self.assertEqual(report.installation_digest, "")

    def test_valid_mismatch_all_forms_checked(self):
        other = replace(self.w, installation=replace(self.w.installation, abi="other"))
        report = c.match_declared_formset(c.encode_declared_formset(self.p, other, expected_version=c.VERSION), self.p, self.w, expected_version=c.VERSION)
        self.assertEqual(report.issue, "DECLARATION_MISMATCH")

    def test_formset_duplicates_missing_reorder_and_types(self):
        for frames in (list(self.frames), self.frames[:-1], (self.frames[0],) * 5,
                       tuple(reversed(self.frames)), self.frames[:4] + (Foreign(),)):
            report = c.match_declared_formset(frames, self.p, self.w, expected_version=c.VERSION)
            self.assertEqual(report.status, "REJECTED_DECLARED_FORMSET")
            self.assertEqual(report.worker_digest, "")

    def test_all_five_gate_before_small_single_or_digest(self):
        w = replace(self.w, installation=replace(self.w.installation, prefixes=tuple("/" + chr(97 + n) * 3900 for n in range(4))))
        self.assertGreater(c.sizing._size(c.sizing._forms(self.p, w)[0]), 16384)
        for operation in (lambda: c.encode_declared_form(self.p, w, expected_version=c.VERSION, role=c.ROLES[4]),
                          lambda: c.encode_declared_formset(self.p, w, expected_version=c.VERSION),
                          lambda: c.digest_declared_profile(self.p, w, expected_version=c.VERSION)):
            self.reject(operation, "FRAME_LIMIT")

    def test_global_64k_arithmetic_separate_from_fixture_forms(self):
        # Kontrollierte interne Kostengegenprobe, keine gültige DTO-Maximalfixture.
        for lengths, accepted in (((13107,) * 4 + (13108,), True), ((13107,) * 4 + (13109,), False)):
            with patch.object(c.sizing, "_size", side_effect=lengths):
                if accepted:
                    self.assertEqual(len(c.encode_declared_formset(self.p, self.w, expected_version=c.VERSION)), 5)
                else:
                    self.reject(lambda: c.encode_declared_form(self.p, self.w, expected_version=c.VERSION, role=c.ROLES[2]), "OUTPUT_LIMIT")
            if not accepted:
                with patch.object(c.sizing, "_size", side_effect=lengths):
                    self.reject(lambda: c.digest_declared_profile(self.p, self.w, expected_version=c.VERSION), "OUTPUT_LIMIT")

    def test_four_valid_received_frame_caps_and_plus_one(self):
        for index in (0, 1, 2, 3):
            for target in (16384, 16385):
                w = at_size(self.p, self.w, index, target)
                f = frame(reference(self.p, w)[index], index)
                self.assertEqual(len(f), target)
                if target == 16384:
                    self.assertEqual(self.decode(f, index, expected_worker=w).role, c.ROLES[index])
                else:
                    self.reject(lambda f=f, index=index, w=w: self.decode(f, index, expected_worker=w), "FRAME_LIMIT")

    def test_context_valid_maximum_and_frame_arithmetic_only(self):
        p = parent(b"x" * 100000)
        for ordinal in (1, 2, 3):
            w = worker(ordinal)
            f = frame(reference(p, w)[4], 4)
            self.assertLess(len(f), 16384)
            self.assertTrue(self.decode(f, 4, prepared=p, expected_worker=w).declared_context_match)
        # Keine erfundene gültige K-Maximalfixture: nur frühe Framearithmetik.
        for target in (16384, 16385):
            f = rawframe(b"0" * (target - 16), 4)
            issue = self.reject(lambda f=f: self.decode(f, 4))
            self.assertEqual(issue, "FRAME_LIMIT" if target > 16384 else "INTEGER_LIMIT")

    def test_pool_256_valid_and_257_all_apis_reject(self):
        base = len(self.forms[0][2])
        for target in (256, 257):
            locations = tuple("/lib/loc" + str(n).zfill(3) for n in range(target - base))
            rows = tuple(replace(r, locations=r.locations + locations) if r.name == "package" else r for r in self.w.modules)
            w = replace(self.w, modules=rows)
            self.assertEqual(len(reference(self.p, w)[0][2]), target)
            if target == 256:
                frames = c.encode_declared_formset(self.p, w, expected_version=c.VERSION)
                self.assertEqual(self.decode(frames[0], expected_worker=w).payload[1], w)
            else:
                self.reject(lambda: c.encode_declared_form(self.p, w, expected_version=c.VERSION, role=c.ROLES[2]), "POOL_LIMIT")
                self.reject(lambda: c.digest_declared_profile(self.p, w, expected_version=c.VERSION), "POOL_LIMIT")

    def test_repeated_text_sharing_preserves_array_occurrences(self):
        locations = ("/lib/" + "q" * 1000,) * 64
        w = replace(self.w, modules=tuple(replace(r, locations=locations) if r.name == "package" else r for r in self.w.modules))
        f = c.encode_declared_form(self.p, w, expected_version=c.VERSION, role=c.ROLES[3])
        recovered = next(r for r in self.decode(f, 3, expected_worker=w).payload[0].modules if r.name == "package")
        self.assertEqual(recovered.locations, locations)
        self.assertEqual(len(recovered.locations), 64)
        self.assertTrue(all(text is recovered.locations[0] for text in recovered.locations))

    def test_late_foreign_dominates_early_byte_overflow(self):
        large = at_size(self.p, self.w, 0, 16385)
        bad = replace(large, modules=large.modules[:-1] + (replace(large.modules[-1], loaderPath=Foreign()),))
        self.reject(lambda: c.encode_declared_form(self.p, bad, expected_version=c.VERSION, role=c.ROLES[4]), "INVALID_RECORD")

    def test_digest_header_domain_and_crossrole_corruption(self):
        for a, n in ((0, 1), (2, 3), (3, 4)):
            body = self.frames[a][16:]
            self.reject(lambda body=body, n=n: self.decode(rawframe(body, n), n), "ROLE_MISMATCH")
        changed = list(self.forms[2])
        changed[1] = "compact-installation-declaration"
        self.reject(lambda: self.decode(frame(changed, 2), 2), "ROLE_MISMATCH")

    def test_all_received_frames_output_cap_before_parser(self):
        # Nur Transportaufnahme-Gegenprobe: keine gültigen JSON-Feldformen.
        frames = tuple(rawframe(b"x" * 13100, n) for n in range(5))
        self.assertGreater(sum(map(len, frames)), 65536)
        with patch.object(c, "_Parser", side_effect=AssertionError):
            result = c.match_declared_formset(frames, self.p, self.w, expected_version=c.VERSION)
        self.assertEqual(result.issue, "OUTPUT_LIMIT")

    def test_header_lengths_rejected_before_parser(self):
        with patch.object(c, "_Parser", side_effect=AssertionError):
            for length in (0, 16369, 0xffffffff, len(self.frames[0]) - 15):
                f = c.HEADER.pack(c.MAGIC, 1, length) + self.frames[0][16:]
                self.reject(lambda f=f: self.decode(f), "FRAME_LENGTH")

    def test_received_semantic_invalid_before_declaration_mismatch(self):
        def invalid_late(values):
            kr, ins, controls, rows = values[1]
            altered = list(rows[-1])
            altered[7] = "SOURCE"  # BUILTIN darf keinen SOURCE-Loader tragen.
            changed_ins = ins[:7] + ("different-abi",) + ins[8:]
            return (values[0], (kr, changed_ins, controls, rows[:-1] + (tuple(altered),)), *values[2:])
        bad = reference(self.p, self.w, invalid_late)[1]
        self.reject(lambda: self.decode(frame(bad, 1), 1), "INVALID_RECORD")

    def test_untrusted_caller_type_subclasses_and_uninitialized_fields(self):
        class Worker(b.WorkerDeclaration):
            pass
        w = Worker(*tuple(getattr(self.w, f.name) for f in fields(self.w)))
        self.reject(lambda: self.decode(self.frames[3], 3, expected_worker=w), "INVALID_RECORD")
        for field_name in ("module", "member", "sha256", "body"):
            src = replace(self.p.sources[-1], **{field_name: Foreign()})
            p = replace(self.p, sources=self.p.sources[:-1] + (src,))
            self.reject(lambda p=p: self.decode(self.frames[0], prepared=p), "INVALID_RECORD")

    def test_no_legacy_canonical_match_prepare_or_jsonloads(self):
        with patch.object(b, "_canonical", side_effect=AssertionError), patch.object(b, "match_reported_profile", side_effect=AssertionError), \
             patch.object(i, "prepare_input", side_effect=AssertionError), patch.object(c.json, "loads", side_effect=AssertionError):
            self.assertEqual(c.encode_declared_formset(self.p, self.w, expected_version=c.VERSION), self.frames)
            self.assertEqual(c.match_declared_formset(self.frames, self.p, self.w, expected_version=c.VERSION).status, "MATCHED_DECLARED_FORMSET")

    def test_imports_and_no_io_process_candidate_execution(self):
        tree = ast.parse(Path(c.__file__).read_text(encoding="utf-8"))
        imports = {n.module if isinstance(n, ast.ImportFrom) else n.names[0].name
                   for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))}
        self.assertEqual(imports, {"dataclasses", "hashlib", "json", "struct", "dgn007_pooled_profile_sizing"})
        forbidden = {"open", "exec", "eval", "compile", "print", "__import__", "Popen", "run", "prepare_input", "token_bytes", "loads"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
                self.assertNotIn(name, forbidden)


if __name__ == "__main__":
    unittest.main()
