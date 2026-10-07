#!/usr/bin/env python3
"""Gebundene synthetische Eingangsframes; keine Kandidatenimporte oder Workers."""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests" / "Tools"))
import dgn007_source_bundle as bundle
import dgn007_execution_edges as edges
import dgn007_import_probe_input as protocol

UNSET = object()


def snapshot():
    sources = tuple(protocol.SourceBytes(module, member, hashlib.sha256(body).hexdigest(), body)
                    for module, member in protocol.MODULES
                    for body in (b"# Synthetic input\r\npass\r\n",))
    return protocol.PreparedInput("a" * 40, "b" * 64, edges.PROFILE, bytes(range(32)), sources)


def parts(frame):
    _, size, _ = protocol.HEADER.unpack_from(frame)
    return json.loads(frame[protocol.HEADER.size:protocol.HEADER.size + size]), frame[protocol.HEADER.size + size:]


def pack(value, body, rebind=True):
    if type(value) is dict:
        value = dict(value)
        if rebind:
            value.pop("context_sha256", None)
            value["context_sha256"] = hashlib.sha256(protocol._canonical(value)).hexdigest()
        value = protocol._canonical(value)
    return protocol.HEADER.pack(protocol.MAGIC, len(value), len(body)) + value + body


class InputProtocolTests(unittest.TestCase):
    def setUp(self):
        self.parent = snapshot()
        self.frame = protocol.encode_input(self.parent)

    def reject(self, frame=UNSET, parent=UNSET, issue=None):
        with self.assertRaises(protocol.InputRejected) as caught:
            protocol.decode_input(self.frame if frame is UNSET else frame,
                                  expected=self.parent if parent is UNSET else parent)
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        if issue:
            self.assertEqual(str(caught.exception), issue)
        self.assertRegex(str(caught.exception), r"^[A-Z_]+$")

    def test_roundtrip_preserves_exact_raw_bytes_and_claim_boundaries(self):
        actual = protocol.decode_input(self.frame, expected=self.parent)
        self.assertIs(actual, self.parent)
        self.assertTrue(all(s.body.endswith(b"\r\n") for s in actual.sources))
        self.assertEqual((actual.status, actual.validation_scope), ("PREPARED_INPUT_ONLY", "PROJECT_SEMANTIC"))
        self.assertFalse(actual.runtime_attested or actual.import_used_bytes_attested or actual.method_approved)
        self.assertEqual(tuple((s.module, s.member) for s in actual.sources), bundle.MODULES)

    def test_records_tuple_and_bytes_are_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            self.parent.commit = "c" * 40
        with self.assertRaises(FrozenInstanceError):
            self.parent.sources[0].body = b"changed"
        self.assertIs(type(self.parent.sources), tuple)
        self.assertNotIn("Synthetic input", repr(self.parent))
        self.assertNotIn("Synthetic input", repr(self.parent.sources[0]))

    def test_nonce_context_is_not_a_replay_receipt(self):
        self.assertIs(protocol.decode_input(self.frame, expected=self.parent), self.parent)
        self.assertIs(protocol.decode_input(self.frame, expected=self.parent), self.parent)
        self.reject(parent=replace(self.parent, nonce=b"z" * 32), issue="PARENT_MISMATCH")

    def test_byte_exchange_with_same_metadata_fails(self):
        value, body = parts(self.frame)
        self.reject(pack(value, b"x" + body[1:]), issue="BODY_MISMATCH")

    def test_rehashed_foreign_body_does_not_become_parent(self):
        value, body = parts(self.frame)
        changed = b"x" + self.parent.sources[0].body[1:]
        value["modules"][0]["sha256"] = hashlib.sha256(changed).hexdigest()
        self.reject(pack(value, changed + body[len(changed):]), issue="PARENT_MISMATCH")

    def test_lf_equivalent_is_not_raw_equivalent(self):
        sources = tuple(replace(s, body=s.body.replace(b"\r\n", b"\n"),
                        sha256=hashlib.sha256(s.body.replace(b"\r\n", b"\n")).hexdigest())
                        for s in self.parent.sources)
        self.reject(protocol.encode_input(replace(self.parent, sources=sources)), issue="PARENT_MISMATCH")

    def test_context_commit_binding_nonce_profile_and_protocol(self):
        for key, replacement in (("commit", "c" * 40), ("raw27_binding", "d" * 64),
                                 ("nonce", "e" * 64), ("source_profile", "foreign"),
                                 ("protocol", "foreign")):
            with self.subTest(key=key):
                value, body = parts(self.frame)
                value[key] = replacement
                self.reject(pack(value, body))

    def test_context_digest_is_recomputed(self):
        value, body = parts(self.frame)
        value["context_sha256"] = "0" * 64
        self.reject(pack(value, body, False), issue="CONTEXT_HASH")

    def test_mapping_order_duplicate_module_member_and_ordinal(self):
        for key, replacement in (("module", "foreign"), ("member", "../foreign.py"),
                                 ("module", self.parent.sources[1].module),
                                 ("member", self.parent.sources[1].member), ("ordinal", 1),
                                 ("ordinal", False)):
            with self.subTest(key=key, replacement=replacement):
                value, body = parts(self.frame)
                value["modules"][0][key] = replacement
                self.reject(pack(value, body), issue="METADATA_MAPPING")
        value, body = parts(self.frame)
        value["modules"].reverse()
        self.reject(pack(value, body), issue="METADATA_MAPPING")

    def test_unknown_missing_and_wrong_metadata_shape(self):
        for mutate in (lambda m: m.update(extra=1), lambda m: m.pop("nonce"),
                       lambda m: m.update(modules=None), lambda m: m["modules"].pop(),
                       lambda m: m["modules"][0].update(extra=1),
                       lambda m: m["modules"][0].pop("size")):
            value, body = parts(self.frame)
            mutate(value)
            self.reject(pack(value, body), issue="METADATA_SHAPE")

    def test_duplicate_json_keys_at_header_and_module(self):
        value, body = parts(self.frame)
        text = protocol._canonical(value)
        for target, prefix in ((b'"commit":', b'"commit":"' + b'a' * 40 + b'","commit":'),
                               (b'"ordinal":0', b'"ordinal":0,"ordinal":0')):
            self.reject(pack(text.replace(target, prefix, 1), body), issue="METADATA_DUPLICATE")

    def test_sizes_bool_null_float_negative_and_overflow(self):
        for size in (True, None, 1.0, -1, protocol.MAX_MEMBER_BYTES + 1, 10**20):
            value, body = parts(self.frame)
            value["modules"][0]["size"] = size
            self.reject(pack(value, body))
        value, body = parts(self.frame)
        for row in value["modules"]:
            row["size"] = protocol.MAX_MEMBER_BYTES
        self.reject(pack(value, body), issue="METADATA_LIMIT")

    def test_declared_body_length_does_not_override_record_lengths(self):
        value, body = parts(self.frame)
        value["modules"][0]["size"] += 1
        self.reject(pack(value, body), issue="FRAME_LENGTH")

    def test_payload_truncation_trailing_bytes_and_magic(self):
        for frame in (self.frame[:-1], self.frame + b"x", self.frame + self.frame,
                      b"foreign!" + self.frame[8:]):
            self.reject(frame)

    def test_limits_are_checked_before_metadata_parse(self):
        for frame in (b"x" * (protocol.MAX_FRAME_BYTES + 1), b"x" * 15,
                      protocol.HEADER.pack(protocol.MAGIC, protocol.MAX_METADATA_BYTES, 0),
                      protocol.HEADER.pack(protocol.MAGIC, 1, protocol.MAX_BODY_BYTES + 1)):
            with patch.object(protocol, "_parse", side_effect=AssertionError("must not parse")) as parser:
                self.reject(frame, issue="FRAME_LIMIT")
                parser.assert_not_called()

    def test_exact_total_bound_and_member_bound(self):
        sources = tuple(replace(s, body=b"x" * size, sha256=hashlib.sha256(b"x" * size).hexdigest())
                        for i, s in enumerate(self.parent.sources)
                        for size in (protocol.MAX_MEMBER_BYTES if i < 8 else 0,))
        parent = replace(self.parent, sources=sources)
        frame = protocol.encode_input(parent)
        self.assertLessEqual(len(frame), protocol.MAX_FRAME_BYTES)
        self.assertIs(protocol.decode_input(frame, expected=parent), parent)
        for size in (1, protocol.MAX_MEMBER_BYTES + 1):
            bad = replace(sources[-1], body=b"x" * size, sha256=hashlib.sha256(b"x" * size).hexdigest())
            with self.assertRaisesRegex(protocol.InputRejected, "PARENT_LIMIT"):
                protocol.encode_input(replace(parent, sources=sources[:-1] + (bad,)))

    def test_non_ascii_constants_extra_json_and_deep_nesting(self):
        _, body = parts(self.frame)
        for metadata in (b'null', b'{}{}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1.2}',
                         b'{"x":"\xff"}', b'[' * 1100 + b'0' + b']' * 1100):
            self.reject(pack(metadata, body))

    def test_false_metadata_context_and_body_hashes(self):
        for key, value in (("commit", None), ("nonce", "A" * 64), ("raw27_binding", "short")):
            metadata, body = parts(self.frame)
            metadata[key] = value
            self.reject(pack(metadata, body), issue="METADATA_CONTEXT")
        metadata, body = parts(self.frame)
        metadata["modules"][0]["sha256"] = None
        self.reject(pack(metadata, body), issue="METADATA_HASH")

    def test_foreign_objects_subclasses_and_missing_fields_are_closed(self):
        class Foreign:
            def __getattribute__(self, name):
                raise AssertionError("foreign getter")
            def __eq__(self, other):
                raise AssertionError("foreign equality")
        class BytesSubclass(bytes):
            pass
        for frame in (bytearray(self.frame), memoryview(self.frame), BytesSubclass(self.frame), Foreign(), None):
            self.reject(frame, issue="FRAME_SHAPE")
        for parent in (False, Foreign(), object.__new__(protocol.PreparedInput),
                       replace(self.parent, commit=Foreign()), replace(self.parent, nonce=Foreign()),
                       replace(self.parent, sources=list(self.parent.sources)),
                       replace(self.parent, sources=(Foreign(),) + self.parent.sources[1:]),
                       replace(self.parent, sources=(object.__new__(protocol.SourceBytes),) + self.parent.sources[1:]),
                       replace(self.parent, sources=(replace(self.parent.sources[0], body=Foreign()),) + self.parent.sources[1:])):
            self.reject(parent=parent)
            with self.assertRaises(protocol.InputRejected):
                protocol.encode_input(parent)
        for field_name in ("module", "member", "sha256", "body"):
            source = replace(self.parent.sources[0], **{field_name: Foreign()})
            self.reject(parent=replace(self.parent, sources=(source,) + self.parent.sources[1:]))
        for field_name in ("commit", "raw27_binding", "source_profile", "nonce", "sources",
                           "status", "validation_scope", "runtime_attested", "import_used_bytes_attested", "method_approved"):
            parent = snapshot()
            object.__setattr__(parent, field_name, Foreign())
            self.reject(parent=parent)

    def test_encoder_rechecks_parent_hash_mapping_context_and_flags(self):
        for parent in (replace(self.parent, raw27_binding="bad"), replace(self.parent, nonce=b"short"),
                       replace(self.parent, source_profile="foreign"),
                       replace(self.parent, sources=tuple(reversed(self.parent.sources))),
                       replace(self.parent, sources=(replace(self.parent.sources[0], sha256="0" * 64),) + self.parent.sources[1:])):
            with self.assertRaises(protocol.InputRejected):
                protocol.encode_input(parent)
        forged = snapshot()
        object.__setattr__(forged, "runtime_attested", True)
        self.reject(parent=forged, issue="PARENT_SHAPE")

    def test_decoder_and_encoder_have_no_io_or_candidate_execution(self):
        tree = ast.parse((ROOT / "Tests/Tools/dgn007_import_probe_input.py").read_text(encoding="utf-8"))
        self.assertEqual({n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)},
                         {"__future__", "dataclasses", "pathlib"})
        self.assertEqual({a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names},
                         {"hashlib", "json", "re", "secrets", "struct", "dgn007_source_bundle", "dgn007_execution_edges"})
        forbidden = {"exec", "eval", "compile", "__import__", "open", "Popen", "import_module", "read_bytes", "write_bytes"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
                self.assertNotIn(name, forbidden)


def git(repo, *args):
    env = bundle.git_environment()
    env.update(GIT_AUTHOR_DATE="2026-10-07T00:00:00Z", GIT_COMMITTER_DATE="2026-10-07T00:00:00Z")
    return subprocess.check_output(["git", "--no-replace-objects", "--no-lazy-fetch", "-C", str(repo),
        "-c", "core.hooksPath=" + str(repo / "empty-hooks"), "-c", "core.autocrlf=false",
        "-c", "commit.gpgSign=false", "-c", "user.name=Synthetic Lab", "-c", "user.email=synthetic-fixture", *args],
        env=env, stderr=subprocess.DEVNULL, timeout=10, shell=False)


class BoundPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.head = git(ROOT, "rev-parse", "HEAD").decode().strip()
        cls.sources = {p: git(ROOT, "cat-file", "blob", cls.head + ":" + p) for p in bundle.DGN007.members}

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dgn007-input-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo, self.candidate = self.root / "repo", self.root / "candidate"
        self.repo.mkdir(); self.candidate.mkdir()
        git(self.repo, "init", "--quiet", "--template=")
        self.bodies = dict(self.sources)
        self.commit()

    def commit(self):
        for member, body in self.bodies.items():
            for root in (self.repo, self.candidate):
                path = root / member
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body)
        git(self.repo, "add", "--all")
        git(self.repo, "commit", "--quiet", "-m", "Synthetic input fixture")
        self.oid = git(self.repo, "rev-parse", "HEAD").decode().strip()

    def test_actual_27_bundle_edge_callback_nonce_and_later_candidate_exchange(self):
        with patch.object(protocol.secrets, "token_bytes", return_value=b"n" * 32) as nonce:
            result = protocol.prepare_input(self.repo, self.oid, self.candidate)
        self.assertEqual((result.status, result.issue), ("PREPARED_INPUT_ONLY", "NONE"))
        nonce.assert_called_once_with(32)
        self.assertEqual(result.prepared.commit, self.oid)
        self.assertEqual(result.prepared.raw27_binding, result.verification.raw_binding)
        self.assertEqual(result.verification.members, 27)
        self.assertTrue(result.verification.raw_bytes_verified and result.verification.declared_import_graph_verified)
        self.assertFalse(result.runtime_attested or result.import_used_bytes_attested)
        for source in result.prepared.sources:
            self.assertEqual(source.body, self.bodies[source.member])
        # Austausch erst nach Prepare darf weder Neuaufnahme noch Ausführung auslösen.
        member = bundle.PYTHON_MEMBERS[2]
        (self.candidate / member).write_bytes(b"raise RuntimeError('Synthetic post-prepare sentinel')\n")
        original = self.bodies[member]
        self.assertEqual(result.prepared.sources[2].body, original)
        self.assertIs(protocol.decode_input(protocol.encode_input(result.prepared), expected=result.prepared), result.prepared)
        self.assertEqual(result.prepared.sources[2].body, original)

    def test_real_commit_bound_crlf_is_retained(self):
        member = bundle.PYTHON_MEMBERS[2]
        self.bodies[member] = self.bodies[member].replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        self.commit()
        result = protocol.prepare_input(self.repo, self.oid, self.candidate)
        self.assertEqual(result.status, "PREPARED_INPUT_ONLY", result.issue)
        self.assertEqual(result.prepared.sources[2].body, self.bodies[member])
        self.assertIn(b"\r\n", result.prepared.sources[2].body)

    def test_raw_failure_never_reaches_edges_or_nonce(self):
        (self.candidate / bundle.PYTHON_MEMBERS[2]).write_bytes(b"pass\n")
        with (patch.object(edges, "_validate_edges", side_effect=AssertionError("must not reach")) as edge,
              patch.object(protocol.secrets, "token_bytes", side_effect=AssertionError("must not reach")) as nonce):
            result = protocol.prepare_input(self.repo, self.oid, self.candidate)
        self.assertEqual((result.status, result.issue), ("FAIL_PREPARE_INPUT", "RAW_BYTES_DIFFER"))
        self.assertIsNone(result.prepared)
        edge.assert_not_called(); nonce.assert_not_called()

    def test_commit_bound_sentinel_rejected_by_unchanged_ast_profile(self):
        self.bodies[bundle.PYTHON_MEMBERS[2]] += b"\nraise RuntimeError('Synthetic sentinel must never execute')\n"
        self.commit()
        with patch.object(protocol.secrets, "token_bytes", side_effect=AssertionError("must not reach")) as nonce:
            result = protocol.prepare_input(self.repo, self.oid, self.candidate)
        self.assertEqual((result.status, result.issue), ("FAIL_PREPARE_INPUT", "PYTHON_PROFILE_CHANGED"))
        self.assertTrue(result.verification.raw_bytes_verified)
        self.assertIsNone(result.prepared)
        nonce.assert_not_called()

    def test_malformed_prepare_arguments_do_not_start_verification(self):
        with patch.object(bundle, "verify_bundle", side_effect=AssertionError("must not reach")) as verifier:
            for args in ((str(self.repo), self.oid, self.candidate), (self.repo, False, self.candidate),
                         (self.repo, "HEAD", self.candidate), (self.repo, self.oid, object())):
                result = protocol.prepare_input(*args)
                self.assertEqual((result.status, result.issue), ("FAIL_PREPARE_INPUT", "PREPARE_ARGUMENT"))
                self.assertIsNone(result.prepared)
        verifier.assert_not_called()

    def test_nonce_failure_and_malformed_rng_output_leave_no_prepared_input(self):
        # Tatsächlich gebundene Bytes einmal aufnehmen, dann nur RNG-Grenzen variieren.
        saved = []
        original = bundle.verify_bundle
        def record(*args, bound_validator):
            def capture(bodies):
                saved.append(bodies)
                bound_validator(bodies)
            return original(*args, bound_validator=capture)
        with patch.object(bundle, "verify_bundle", side_effect=record):
            positive = protocol.prepare_input(self.repo, self.oid, self.candidate)
        self.assertIsNotNone(positive.prepared)
        def replay(*args, bound_validator):
            bound_validator(saved[0])
            return positive.verification
        for error in (OSError("private raw error"), ValueError("private raw error"), TypeError("private raw error")):
            with (patch.object(bundle, "verify_bundle", side_effect=replay),
                  patch.object(protocol.secrets, "token_bytes", side_effect=error)):
                result = protocol.prepare_input(self.repo, self.oid, self.candidate)
                self.assertEqual((result.status, result.issue), ("FAIL_PREPARE_INPUT", "PREPARE_NONCE"))
                self.assertIsNone(result.prepared)
        for value in (None, True, b"short", bytearray(32)):
            with (patch.object(bundle, "verify_bundle", side_effect=replay),
                  patch.object(protocol.secrets, "token_bytes", return_value=value)):
                result = protocol.prepare_input(self.repo, self.oid, self.candidate)
                self.assertEqual((result.status, result.issue), ("FAIL_PREPARE_INPUT", "PREPARE_NONCE"))
                self.assertIsNone(result.prepared)


if __name__ == "__main__":
    unittest.main()
