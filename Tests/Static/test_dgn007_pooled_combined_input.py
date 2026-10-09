"""Synthetische CombinedFrame-Gegenproben ohne Vorbereitung oder Worker."""
from dataclasses import FrozenInstanceError, fields, replace
import ast
import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))
import dgn007_pooled_combined_input as c

b, i = c.b, c.input82


def parent(bodies=None):
    if bodies is None:
        bodies = tuple(("# synthetic-%d\r\n" % n).encode("ascii") for n in range(9))
    return i.PreparedInput("a" * 40, "b" * 64, "dgn007-docker-sql-only/v1", b"n" * 32,
        tuple(i.SourceBytes(name, member, hashlib.sha256(body).hexdigest(), body)
              for (name, member), body in zip(i.MODULES, bodies)))


def worker(ordinal=1):
    installation = b.InstallationDeclaration(b.ASSUMPTION, "linux", "cpython", (3, 12, 14),
        "/synthetic/python", "/synthetic/python-target", ("/p0", "/p1", "/p2", "/p3"),
        "synthetic-abi", ("/lib", "/lib/dyn", "/python312.zip"), ("/lib", "/lib/dyn"),
        "/python312.zip", (1, 1, 1, 1, 1, 0), ("BUILTIN", "FROZEN", "PATH"),
        ("ZIPIMPORTER", "FILEFINDER"), (b.FileFingerprint("/synthetic/python-target", 7, "c" * 64),))
    modules = (
        b.ModuleDeclaration("__main__", "__main__", None, "", "/control.py", "CONTROL", (), "NONE"),
        b.ModuleDeclaration("package", "package", "package", "/lib/package.py", "/lib/package.py",
                            "SOURCE", ("/lib/package",), "SOURCE", "package", "/lib/package.py"),
        b.ModuleDeclaration("sys", "sys", "sys", "built-in", "", "BUILTIN", (), "BUILTIN"),
    )
    return b.WorkerDeclaration(ordinal, b.ENTRIES[ordinal - 1], "PRE_IMPORT", installation,
                               ("__main__",), modules)


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def plain(value):
    if type(value) is tuple:
        return tuple(plain(v) for v in value)
    if type(value) in (b.WorkerDeclaration, b.InstallationDeclaration, b.ModuleDeclaration,
                       b.FileFingerprint):
        return {f.name: plain(getattr(value, f.name)) for f in fields(value)}
    return value


def payload(p, w):
    # Benannte unabhängige Referenz: Input82-SHA über ursprüngliche Feldmenge.
    rows = tuple(dict(ordinal=n, module=s.module, member=s.member,
                      size=len(s.body), sha256=s.sha256) for n, s in enumerate(p.sources))
    metadata = dict(protocol=i.PROTOCOL, commit=p.commit, raw27_binding=p.raw27_binding,
                    source_profile=p.source_profile, nonce=p.nonce.hex(), modules=list(rows))
    digest = hashlib.sha256(canonical(metadata)).hexdigest()
    descriptors = tuple(tuple(r[k] for k in ("ordinal", "module", "member", "size", "sha256"))
                        for r in rows)
    ip = tuple(metadata[k] for k in ("protocol", "commit", "raw27_binding", "source_profile", "nonce")) + (
        descriptors, digest)
    wn = plain(w)
    sk = ("assumption", "platform", "implementation", "version", "executable", "executable_target",
          "prefixes", "abi", "paths", "roots", "inert_zip", "flags", "finders", "hooks")
    pk = ("name", "moduleName", "specName", "origin", "file", "kind", "locations", "loader",
          "loaderName", "loaderPath", "aliasGroup")
    sn = wn["installation"]
    installation = tuple(sn[k] for k in sk) + (
        tuple(tuple(f[k] for k in ("path", "size", "sha256")) for f in sn["files"]),)
    modules = tuple(tuple(m[k] for k in pk) for m in wn["modules"])
    wr = (wn["ordinal"], wn["entry"], wn["phase"], installation, wn["controls"], modules)
    kr = (p.commit, p.raw27_binding, p.source_profile, p.nonce.hex(), descriptors,
          w.ordinal, w.entry, w.phase)
    return (ip, wr, kr)


def e4(value):
    def texts(v):
        if type(v) is str:
            return {v}
        if type(v) is tuple:
            return set().union(*(texts(x) for x in v))
        return set()

    pool = tuple(sorted(texts(value)))

    def pack(v):
        if type(v) is str:
            return pool.index(v)
        if type(v) is tuple:
            return tuple(pack(x) for x in v)
        return v
    return ("pooled-binding-design/v1", "METADATA", pool, pack(value))


def reference_frame(p, w, *, value=None, bodies=None):
    raw = canonical(e4(payload(p, w) if value is None else value))
    if bodies is None:
        bodies = tuple(s.body for s in p.sources)
    total = sum(len(x) for x in bodies)
    return struct.pack(">8sII", b"DGNC001\0", len(raw), total) + raw + b"".join(bodies)


def sized_worker(p, w, target):
    remaining = target - (16 + len(canonical(e4(payload(p, w)))))
    prefixes = list(w.installation.prefixes)
    for n in range(4):
        delta = min(remaining, 4096 - len(prefixes[n]))
        if delta < 0:
            raise AssertionError("synthetic capacity")
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


class CombinedTests(unittest.TestCase):
    def setUp(self):
        self.p, self.w = parent(), worker()
        self.frame = reference_frame(self.p, self.w)

    def decode(self, frame=None, **changes):
        kwargs = dict(expected_format=c.FORMAT, prepared=self.p, expected_worker=self.w)
        kwargs.update(changes)
        return c.decode_combined_input(self.frame if frame is None else frame, **kwargs)

    def encode(self, p=None, w=None, **changes):
        return c.encode_combined_input(self.p if p is None else p, self.w if w is None else w,
                                      expected_format=changes.get("expected_format", c.FORMAT))

    def reject(self, operation, issue=None):
        with self.assertRaises(c.CombinedInputRejected) as caught:
            operation()
        error = caught.exception
        if issue is not None:
            self.assertEqual(str(error), issue)
        self.assertIsNone(error.__context__)
        self.assertIsNone(error.__cause__)
        self.assertNotIn("synthetic-private", str(error))
        self.assertNotIn("/synthetic", str(error))
        return str(error)

    def test_three_ordinals_independent_complete_reference(self):
        for n in (1, 2, 3):
            w = worker(n)
            expected = reference_frame(self.p, w)
            self.assertEqual(self.encode(w=w), expected)
            actual = self.decode(expected, expected_worker=w)
            self.assertEqual(actual.input_metadata, payload(self.p, w)[0])
            self.assertEqual(actual.worker, w)
            self.assertIsNot(actual.worker, w)
            self.assertEqual(actual.context, b.derive_binding_context(self.p, n))
            for ordinal, (source, held) in enumerate(zip(actual.sources, self.p.sources)):
                self.assertEqual((source.ordinal, source.module, source.member, source.sha256, source.body),
                                 (ordinal, held.module, held.member, held.sha256, held.body))
                self.assertIs(type(source.body), bytes)
                self.assertIsNot(source, held)

    def test_both_descriptor_arrays_and_original_input_digest(self):
        actual = self.decode()
        self.assertEqual(actual.input_metadata[5], tuple(tuple(getattr(d, k) for k in
            ("ordinal", "module", "member", "size", "sha256")) for d in actual.context.modules))
        self.assertEqual(actual.input_metadata[-1], i._metadata(self.p)["context_sha256"])
        self.assertEqual(tuple(s.sha256 for s in actual.sources), tuple(s.sha256 for s in self.p.sources))

    def test_crlf_exact_rawbytes_and_changed_lf_rejected(self):
        self.assertTrue(all(b"\r\n" in s.body for s in self.decode().sources))
        p = parent(tuple(s.body.replace(b"\r\n", b"\n") for s in self.p.sources))
        self.reject(lambda: self.decode(reference_frame(p, self.w)), "DECLARATION_MISMATCH")
        self.assertNotEqual(payload(p, self.w)[0][-1], payload(self.p, self.w)[0][-1])

    def test_empty_nul_and_non_utf8_bodies_are_opaque(self):
        p = parent((b"", b"\0", b"\xff\xfe", b"\r\n", b"x", b"y", b"z", b"a", b"b"))
        actual = self.decode(self.encode(p=p), prepared=p)
        self.assertEqual(tuple(s.body for s in actual.sources), tuple(s.body for s in p.sources))

    def test_frozen_private_output_all_flags_false_replay_possible(self):
        actual = self.decode()
        self.assertEqual(self.decode(), actual)
        self.assertTrue(actual.declared_context_match)
        self.assertEqual(actual.status, "MATCHED_DECLARED_COMBINED_INPUT")
        self.assertEqual(actual.validation_scope, "PROJECT_SEMANTIC")
        for key in ("runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved"):
            self.assertIs(getattr(actual, key), False)
        self.assertNotIn("/lib", repr(actual))
        self.assertNotIn("synthetic-", repr(actual.sources[0]))
        with self.assertRaises(FrozenInstanceError):
            actual.worker = self.w
        with self.assertRaises(FrozenInstanceError):
            actual.sources[0].body = b"changed"

    def test_format_before_intake_and_no_default(self):
        for fmt in (None, True, Foreign(), "dgn007-import-input/v1", c.codec.VERSION, ""):
            with patch.object(c.codec, "_decode") as parser:
                self.reject(lambda: self.decode(Foreign(), expected_format=fmt), "FORMAT_SELECTION")
                parser.assert_not_called()
            self.reject(lambda: self.encode(expected_format=fmt), "FORMAT_SELECTION")
        with self.assertRaises(TypeError):
            c.encode_combined_input(self.p, self.w)

    def test_frame_exact_type(self):
        class Child(bytes):
            pass
        for value in (Child(self.frame), bytearray(self.frame), memoryview(self.frame), Foreign(), True):
            self.reject(lambda: self.decode(value), "FRAME_TYPE")

    def test_header_and_global_bounds_before_metadata_parser(self):
        bad = (b"", self.frame[:15], b"x" * (c.MAX_FRAME_BYTES + 1),
               c.HEADER.pack(c.MAGIC, 0, 0),
               c.HEADER.pack(c.MAGIC, 16369, 0) + b"x" * 16369,
               c.HEADER.pack(c.MAGIC, 1, 1048577) + b"[]",
               c.HEADER.pack(c.MAGIC, 0xFFFFFFFF, 0xFFFFFFFF))
        for value in bad:
            with patch.object(c.codec, "_decode") as parser:
                self.reject(lambda: self.decode(value))
                parser.assert_not_called()

    def test_magic_and_legacy_crossover(self):
        for magic in (i.MAGIC, c.codec.MAGIC, b"DGNC002\0", b"XXXXXXXX"):
            self.reject(lambda: self.decode(magic + self.frame[8:]), "FRAME_MAGIC")

    def test_truncate_trailing_and_length_mismatch(self):
        for value in (self.frame[:-1], self.frame + b"x", self.frame[:20]):
            self.reject(lambda: self.decode(value), "FRAME_LENGTH")
        _, size, total = c.HEADER.unpack_from(self.frame)
        for header in (c.HEADER.pack(c.MAGIC, size + 1, total),
                       c.HEADER.pack(c.MAGIC, size, total + 1)):
            self.reject(lambda: self.decode(header + self.frame[16:]), "FRAME_LENGTH")

    def test_header_body_length_must_match_all_received_descriptors(self):
        _, size, total = c.HEADER.unpack_from(self.frame)
        bad = c.HEADER.pack(c.MAGIC, size, total + 1) + self.frame[16:] + b"x"
        self.reject(lambda: self.decode(bad), "BODY_LENGTH")

    def test_each_received_body_hash_checked(self):
        offset = 16 + c.HEADER.unpack_from(self.frame)[1]
        for source in self.p.sources:
            bad = self.frame[:offset] + bytes((self.frame[offset] ^ 1,)) + self.frame[offset + 1:]
            self.reject(lambda: self.decode(bad), "BODY_HASH")
            offset += len(source.body)

    def test_body_exchange_and_reordered_bodies(self):
        bodies = tuple(s.body for s in self.p.sources)
        exchanged = (bodies[-1],) + bodies[1:-1] + (bodies[0],)
        self.reject(lambda: self.decode(reference_frame(self.p, self.w, bodies=exchanged)), "BODY_HASH")
        self.reject(lambda: self.decode(reference_frame(self.p, self.w, bodies=tuple(reversed(bodies)))), "BODY_HASH")

    def test_late_body_failure_dominates_early_valid_caller_mismatch(self):
        p = replace(self.p, nonce=b"q" * 32)
        bad = reference_frame(p, self.w)
        bad = bad[:-1] + bytes((bad[-1] ^ 1,))
        self.reject(lambda: self.decode(bad), "BODY_HASH")
        self.reject(lambda: self.decode(bad, prepared=Foreign()), "BODY_HASH")

    def test_full_body_validation_precedes_caller_access(self):
        with patch.object(c, "_caller_metadata", side_effect=AssertionError("caller too soon")):
            self.reject(lambda: self.decode(self.frame[:-1] + b"x"), "BODY_HASH")

    def test_commit_nonce_raw27_and_worker_ordinal_mismatch(self):
        for p in (replace(self.p, commit="c" * 40), replace(self.p, raw27_binding="d" * 64),
                  replace(self.p, nonce=b"q" * 32)):
            self.reject(lambda: self.decode(reference_frame(p, self.w)), "DECLARATION_MISMATCH")
        for n in (2, 3):
            self.reject(lambda: self.decode(reference_frame(self.p, worker(n))), "DECLARATION_MISMATCH")

    def test_received_mapping_wrong_member_module_duplicate_order(self):
        original = payload(self.p, self.w)
        for slot, value in ((0, 1), (1, "foreign"), (2, "Tests/foreign.py")):
            descriptors = list(original[2][4])
            first = list(descriptors[0])
            first[slot] = value
            descriptors[0] = tuple(first)
            kr = original[2][:4] + (tuple(descriptors),) + original[2][5:]
            self.reject(lambda: self.decode(reference_frame(self.p, self.w,
                value=(original[0], original[1], kr))))
        ds = (original[2][4][0],) * 9
        kr = original[2][:4] + (ds,) + original[2][5:]
        self.reject(lambda: self.decode(reference_frame(self.p, self.w, value=(original[0], original[1], kr))))

    def test_physical_input_descriptors_not_replaced_by_context_defaults(self):
        original = payload(self.p, self.w)
        descriptors = list(original[0][5])
        row = list(descriptors[-1])
        row[-1] = "e" * 64
        descriptors[-1] = tuple(row)
        ip = original[0][:5] + (tuple(descriptors), original[0][-1])
        self.reject(lambda: self.decode(reference_frame(self.p, self.w,
            value=(ip, original[1], original[2]))), "INPUT_BINDING")

    def test_original_input_digest_cannot_be_replaced(self):
        original = payload(self.p, self.w)
        ip = original[0][:-1] + ("e" * 64,)
        self.reject(lambda: self.decode(reference_frame(self.p, self.w,
            value=(ip, original[1], original[2]))), "INPUT_BINDING")

    def test_fixed_metadata_role_version_and_canonicality(self):
        _, n, total = c.HEADER.unpack_from(self.frame)
        metadata = self.frame[16:16 + n]
        for raw in (metadata.replace(b'METADATA', b'REPORTED'),
                    metadata.replace(b'pooled-binding-design/v1', b'pooled-binding-design/v2'),
                    b" " + metadata, c.codec.HEADER.pack(c.codec.MAGIC, 1, n) + metadata):
            bad = c.HEADER.pack(c.MAGIC, len(raw), total) + raw + self.frame[16 + n:]
            self.reject(lambda: self.decode(bad))

    def test_received_member_exact_cap_and_total_exact_cap(self):
        bodies = (b"x" * c.MAX_MEMBER_BYTES,) * 8 + (b"",)
        p = parent(bodies)
        actual = self.decode(self.encode(p=p), prepared=p)
        self.assertEqual(sum(len(s.body) for s in actual.sources), c.MAX_BODY_BYTES)
        self.assertTrue(all(len(s.body) == c.MAX_MEMBER_BYTES for s in actual.sources[:8]))

    def test_encoder_member_and_total_cap_plus_one(self):
        p = parent((b"x" * (c.MAX_MEMBER_BYTES + 1),) + (b"",) * 8)
        self.reject(lambda: self.encode(p=p))
        p = parent((b"x" * c.MAX_MEMBER_BYTES,) * 8 + (b"x",))
        self.reject(lambda: self.encode(p=p))

    def test_received_member_cap_plus_one_semantics_before_body_slice(self):
        p = parent((b"x" * (c.MAX_MEMBER_BYTES + 1),) + (b"",) * 8)
        with patch.object(c, "_caller_metadata", side_effect=AssertionError("caller")):
            self.reject(lambda: self.decode(reference_frame(p, self.w)))

    def test_received_total_cap_plus_one_before_parse(self):
        p = parent((b"x" * c.MAX_MEMBER_BYTES,) * 8 + (b"x",))
        with patch.object(c.codec, "_decode") as parse:
            self.reject(lambda: self.decode(reference_frame(p, self.w)), "FRAME_LIMIT")
            parse.assert_not_called()

    def test_valid_metadata_cap_and_cap_plus_one(self):
        w = sized_worker(self.p, self.w, c.MAX_METADATA_BYTES)
        f = reference_frame(self.p, w)
        self.assertEqual(16 + c.HEADER.unpack_from(f)[1], c.MAX_METADATA_BYTES)
        self.assertEqual(self.decode(f, expected_worker=w).worker, w)
        w = sized_worker(self.p, self.w, c.MAX_METADATA_BYTES + 1)
        with patch.object(c.codec, "_decode") as parse:
            self.reject(lambda: self.decode(reference_frame(self.p, w), expected_worker=w), "FRAME_LIMIT")
            parse.assert_not_called()

    def test_valid_full_frame_exact_cap_and_cap_plus_one(self):
        p = parent((b"x" * c.MAX_MEMBER_BYTES,) * 8 + (b"",))
        w = sized_worker(p, self.w, c.MAX_METADATA_BYTES)
        f = reference_frame(p, w)
        self.assertEqual(len(f), c.MAX_FRAME_BYTES)
        self.assertEqual(sum(len(s.body) for s in self.decode(f, prepared=p, expected_worker=w).sources), c.MAX_BODY_BYTES)
        with patch.object(c.codec, "_decode") as parse:
            self.reject(lambda: self.decode(f + b"x", prepared=p, expected_worker=w), "FRAME_LIMIT")
            parse.assert_not_called()

    def test_encoder_five_form_bytegate_not_small_single_success(self):
        w = sized_worker(self.p, self.w, c.MAX_METADATA_BYTES + 1)
        self.reject(lambda: self.encode(w=w), "FRAME_LIMIT")
        with patch.object(c.codec.sizing, "_size", return_value=14000):
            self.reject(lambda: self.encode(), "OUTPUT_LIMIT")

    def test_actual_received_only_metadata_no_unreceived_formgate_claim(self):
        with patch.object(c.codec, "_gated_forms", side_effect=AssertionError("unreceived")):
            self.assertEqual(self.decode().worker, self.w)

    def test_all_caller_forms_validated_no_foreign_callbacks(self):
        cases = (Foreign(), i.PreparedInput.__new__(i.PreparedInput),
                 replace(self.p, nonce=Foreign()), replace(self.p, sources=Foreign()))
        for value in cases:
            self.reject(lambda: self.decode(prepared=value), "INVALID_RECORD")
            self.reject(lambda: self.encode(p=value))
        for value in (Foreign(), b.WorkerDeclaration.__new__(b.WorkerDeclaration),
                      replace(self.w, ordinal=True), replace(self.w, modules=Foreign())):
            self.reject(lambda: self.decode(expected_worker=value), "INVALID_RECORD")
            self.reject(lambda: self.encode(w=value))

    def test_source_fields_and_bytes_subclasses_closed(self):
        class Child(bytes):
            pass
        for key, value in (("body", Child(b"x")), ("body", Foreign()), ("sha256", Foreign()),
                           ("module", Foreign()), ("member", Foreign())):
            sources = list(self.p.sources)
            sources[-1] = replace(sources[-1], **{key: value})
            p = replace(self.p, sources=tuple(sources))
            self.reject(lambda: self.decode(prepared=p), "INVALID_RECORD")
            self.reject(lambda: self.encode(p=p))

    def test_rehashed_caller_does_not_default_received_bodies(self):
        p = parent(tuple(b"x" * len(s.body) for s in self.p.sources))
        self.reject(lambda: self.decode(prepared=p), "DECLARATION_MISMATCH")
        self.assertEqual(self.decode(self.encode(p=p), prepared=p).sources[0].body, p.sources[0].body)

    def test_unicode_exact_scalar_roundtrip(self):
        w = replace(self.w, installation=replace(self.w.installation, abi="synthetic-ä-😀-\u007f"))
        self.assertEqual(self.encode(w=w), reference_frame(self.p, w))
        self.assertEqual(self.decode(reference_frame(self.p, w), expected_worker=w).worker, w)

    def test_scalar_late_malformed_dominates_early_mismatch(self):
        p = replace(self.p, nonce=b"q" * 32)
        value = payload(p, self.w)
        wr = value[1][:2] + ("INVALID_PHASE",) + value[1][3:]
        self.reject(lambda: self.decode(reference_frame(p, self.w, value=(value[0], wr, value[2]))), "INVALID_RECORD")

    def test_no_prepare_nonce_process_or_candidate_execution(self):
        with patch.object(i, "prepare_input", side_effect=AssertionError("prepare")), \
             patch.object(i.secrets, "token_bytes", side_effect=AssertionError("nonce")):
            self.assertEqual(self.decode(self.encode()).sources[0].body, self.p.sources[0].body)
        tree = ast.parse(Path(c.__file__).read_text(encoding="utf-8"))
        imports = {n.module for n in ast.walk(tree) if type(n) is ast.ImportFrom}
        imports |= {a.name for n in ast.walk(tree) if type(n) is ast.Import for a in n.names}
        self.assertEqual(imports, {"dataclasses", "hashlib", "struct", "dgn007_pooled_profile_codec"})
        forbidden = {"open", "eval", "exec", "compile", "print", "Popen", "run", "prepare_input", "token_bytes"}
        calls = {n.func.id if type(n.func) is ast.Name else n.func.attr for n in ast.walk(tree)
                 if type(n) is ast.Call and type(n.func) in (ast.Name, ast.Attribute)}
        self.assertFalse(calls & forbidden)


if __name__ == "__main__":
    unittest.main()
