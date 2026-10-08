"""Neue isolierte Synthetik des lokalen Ledgers, ohne Worker oder Template."""
from dataclasses import FrozenInstanceError, replace
import ast
import copy
from pathlib import Path
import pickle
import sys
import unittest
from types import FunctionType

TOOLS = Path(__file__).resolve().parents[1] / "Tools"
sys.path.insert(0, str(TOOLS))
import dgn007_parent_ledger as l
import dgn007_import_profile_binding as b


def contexts(count=3):
    rows = tuple(b.SourceDescriptor(index, module, member, 0, "c" * 64)
                 for index, (module, member) in enumerate(b.input82.MODULES))
    return tuple(b.BindingContext("a" * 40, "b" * 64, "dgn007-docker-sql-only/v1",
                 b"n" * 32, rows, index + 1, b.ENTRIES[index], "PRE_IMPORT")
                 for index in range(count))


class Bomb:
    def __bool__(self):
        raise AssertionError("FOREIGN_BOOL")

    def __eq__(self, other):
        raise AssertionError("FOREIGN_EQ")

    def __str__(self):
        raise AssertionError("FOREIGN_STR")

    def __iter__(self):
        raise AssertionError("FOREIGN_ITER")

    def __len__(self):
        raise AssertionError("FOREIGN_LEN")


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.cache = tuple(sys.modules.items())
        self.main = sys.modules.get("__main__")
        modules = (l, b, b.input82, b.input82.bundle, b.input82.edges,
                   b.json, b.json.encoder, b.hashlib)
        if "sysconfig" in sys.modules:
            modules += (sys.modules["sysconfig"],)
        self.namespaces = tuple((m, tuple(m.__dict__.items())) for m in modules)
        functions = list(l._HELD_FUNCTIONS)
        classes = l._HELD_CLASSES + (b.json.JSONEncoder,)
        for cls in classes:
            functions.extend(value for value in cls.__dict__.values()
                             if type(value) is FunctionType)
        self.functions = tuple((fn, fn.__code__, fn.__globals__, fn.__defaults__,
                                () if fn.__defaults__ is None else tuple(fn.__defaults__),
                                fn.__kwdefaults__, () if fn.__kwdefaults__ is None
                                else tuple(fn.__kwdefaults__.items()), fn.__closure__,
                                tuple((cell, cell.cell_contents) for cell in fn.__closure__ or ()))
                               for fn in functions)
        self.cls = tuple((cls, tuple(cls.__dict__.items()), cls.__mro__, cls.__bases__)
                         for cls in classes)
        self.restore = []

    def tearDown(self):
        # Wiederherstellung ausschließlich eigener ausdrücklich registrierter Patches.
        for callback in reversed(self.restore):
            callback()
        self.assertEqual(tuple(sys.modules), tuple(key for key, _ in self.cache))
        for key, module in self.cache:
            self.assertIs(sys.modules[key], module)
        self.assertIs(sys.modules.get("__main__"), self.main)
        for module, snapshot in self.namespaces:
            self.assertEqual(tuple(module.__dict__), tuple(key for key, _ in snapshot))
            for key, value in snapshot:
                self.assertIs(module.__dict__[key], value)
        for fn, code, glob, defaults, values, kw, kw_values, closure, cells in self.functions:
            self.assertIs(fn.__code__, code)
            self.assertIs(fn.__globals__, glob)
            self.assertIs(fn.__defaults__, defaults)
            self.assertIs(fn.__kwdefaults__, kw)
            if defaults is not None:
                self.assertEqual(len(defaults), len(values))
                for actual, expected in zip(defaults, values):
                    self.assertIs(actual, expected)
            if kw is not None:
                self.assertEqual(tuple(kw), tuple(key for key, _ in kw_values))
                for key, value in kw_values:
                    self.assertIs(kw[key], value)
            self.assertIs(fn.__closure__, closure)
            for cell, value in cells:
                self.assertIs(cell.cell_contents, value)
        for cls, snapshot, mro, bases in self.cls:
            self.assertEqual(tuple(cls.__dict__), tuple(key for key, _ in snapshot))
            for key, value in snapshot:
                self.assertIs(cls.__dict__[key], value)
            self.assertIs(cls.__mro__, mro)
            self.assertIs(cls.__bases__, bases)

    def ledger(self, count=1, hook=None, chosen=None):
        return l.create_local_ledger(contexts(count) if chosen is None else chosen,
                                     adapter=l._SyntheticAdapter(hook))

    def factory_rejected(self, chosen, issue=None):
        with self.assertRaises(l.LedgerRejected) as caught:
            l.create_local_ledger(chosen, adapter=l._SyntheticAdapter())
        if issue is not None:
            self.assertEqual(caught.exception.args, (issue,))
        self.assertTrue(caught.exception.__suppress_context__)

    def mutate_code(self, fn, replacement):
        old = fn.__code__
        self.restore.append(lambda: setattr(fn, "__code__", old))
        fn.__code__ = replacement.__code__

    def register_global_change(self, name, value):
        self.assertNotIn(name, l.__dict__)
        def restore():
            if l.__dict__.get(name) is value:
                del l.__dict__[name]
        self.restore.append(restore)

    def register_own_global(self, name, value):
        self.register_global_change(name, value)
        l.__dict__[name] = value

    def register_existing_global_change(self, name, replacement):
        original = l.__dict__[name]
        def restore():
            if l.__dict__.get(name) is replacement:
                l.__dict__[name] = original
        self.restore.append(restore)
        return original

    def test_three_serial_slots_all_eleven_edges_and_ten_calls(self):
        events = []
        def hook(inv):
            events.append((inv.context.ordinal, inv.before, inv.after,
                           inv.slot.bits, inv.slot.start_attempted))
        ledger = self.ledger(3, hook)
        for ordinal in range(1, 4):
            for state in l._STATES[1:]:
                result = ledger.advance()
                self.assertEqual((result.slot_index, result.state), (ordinal, state))
                self.assertEqual(result.first_issue, "")
        result = ledger.diagnose()
        self.assertEqual(result.status, "LOCAL_CLOSED")
        self.assertEqual((result.starts, result.commands, result.bookings, result.cleanup), (3, 9, 33, 3))
        self.assertEqual([(o, a, z) for o, a, z, _, _ in events],
                         [(o, n, n + 1) for o in (1, 2, 3) for n in range(1, 11)])
        self.assertTrue(all(row[-1] for row in events))
        self.assertTrue(all(slot.cleanup_complete for slot in ledger._slots))

    def test_local_start_reserve_is_not_launch_attempt_or_callback(self):
        calls = []
        def hook(inv):
            calls.append(inv)
        ledger = self.ledger(hook=hook)
        result = ledger.advance()
        self.assertEqual(result.state, "START_RESERVED")
        self.assertEqual(calls, [])
        self.assertFalse(ledger._slots[0].start_attempted)
        ledger._stop("LEDGER_ORDER")
        ledger.failure_cleanup()
        self.assertEqual(calls, [])
        self.assertEqual(ledger.diagnose().cleanup, 0)

    def test_command_bits_reserved_before_each_write(self):
        writes = []
        def hook(inv):
            if inv.before in (3, 5, 7):
                writes.append((inv.before, inv.slot.bits))
        ledger = self.ledger(hook=hook)
        for _ in range(11):
            ledger.advance()
        self.assertEqual(writes, [(3, 3), (5, 7), (7, 15)])

    def test_callback_receipt_is_prebound_but_not_completed(self):
        captured = []
        def hook(inv):
            captured.append(inv)
            self.assertTrue(inv.attempted)
            self.assertFalse(inv.completed)
            self.assertFalse(inv.consumed)
            self.assertIs(inv.receipt.invocation, inv)
            self.assertIs(inv.context, inv.slot.context)
            self.assertIs(inv.receipt.baseline, inv.slot.baseline)
        ledger = self.ledger(hook=hook)
        ledger.advance()
        self.assertEqual(ledger.advance().state, "AWAIT_PROFILE")
        self.assertTrue(captured[0].completed)
        self.assertTrue(captured[0].consumed)

    def test_hook_return_has_no_success_or_failure_authority(self):
        def hook(inv):
            return Bomb()
        ledger = self.ledger(hook=hook)
        ledger.advance()
        self.assertEqual(ledger.advance().state, "AWAIT_PROFILE")

    def test_slot_count_and_foreign_top_types(self):
        for value in (None, Bomb(), [], (), contexts() + contexts(1)):
            self.factory_rejected(value, "LEDGER_LIMIT")

    def test_subclass_context_and_descriptor_rejected(self):
        class Context(b.BindingContext):
            pass
        row = contexts(1)[0]
        self.factory_rejected((Context(row.commit, row.raw27_binding, row.source_profile,
                                     row.nonce, row.modules, row.ordinal, row.entry, row.phase),))
        class Descriptor(b.SourceDescriptor):
            pass
        d = row.modules[0]
        self.factory_rejected((replace(row, modules=(Descriptor(d.ordinal, d.module, d.member,
                                d.size, d.sha256),) + row.modules[1:]),))

    def test_global_late_primitive_before_early_semantic(self):
        rows = list(contexts())
        rows[0] = replace(rows[0], commit="bad")
        rows[-1] = replace(rows[-1], modules=rows[-1].modules[:-1] + (
            replace(rows[-1].modules[-1], sha256=Bomb()),))
        self.factory_rejected(tuple(rows), "LEDGER_FORM")

    def test_bool_float_null_and_foreign_primitives(self):
        row = contexts(1)[0]
        for value in (True, 1.0, None, Bomb()):
            self.factory_rejected((replace(row, ordinal=value),), "LEDGER_FORM")

    def test_text_nul_surrogate_utf8_and_boundary(self):
        row = contexts(1)[0]
        for value in ("x\0", "\ud800", "é" * 2049, "x" * 4097):
            self.factory_rejected((replace(row, entry=value),), "LEDGER_FORM")
        self.factory_rejected((replace(row, entry="é" * 2048),), "LEDGER_FORM")

    def test_nonce_and_descriptor_complete_forms(self):
        row = contexts(1)[0]
        for nonce in (b"n" * 31, b"n" * 33, "n" * 32, bytearray(b"n" * 32)):
            self.factory_rejected((replace(row, nonce=nonce),), "LEDGER_FORM")
        for modules in (row.modules[:-1], row.modules + row.modules[:1], list(row.modules)):
            self.factory_rejected((replace(row, modules=modules),), "LEDGER_FORM")

    def test_full_semantics_mapping_size_digest_and_phase(self):
        row = contexts(1)[0]
        variants = [replace(row, commit="x" * 40), replace(row, phase="AWAIT_PROFILE"),
                    replace(row, source_profile="other"), replace(row, entry=b.ENTRIES[1])]
        for field, value in (("ordinal", 8), ("module", "other"), ("member", "other"),
                             ("size", 131073), ("sha256", "x" * 64)):
            variants.append(replace(row, modules=(replace(row.modules[0], **{field: value}),) + row.modules[1:]))
        for value in variants:
            self.factory_rejected((value,), "LEDGER_FORM")

    def test_shared_nonce_and_full_input_binding(self):
        selected = contexts()
        ledger = self.ledger(3, chosen=selected)
        self.assertIs(ledger._slots[2].context, selected[2])
        for field, value in (("commit", "d" * 40), ("raw27_binding", "d" * 64), ("nonce", b"d" * 32)):
            self.factory_rejected(selected[:2] + (replace(selected[2], **{field: value}),), "LEDGER_CONTEXT")
        changed = replace(selected[2].modules[-1], sha256="d" * 64)
        self.factory_rejected(selected[:2] + (replace(selected[2], modules=selected[2].modules[:-1] + (changed,)),), "LEDGER_CONTEXT")

    def test_order_is_prefix_not_permutation(self):
        rows = contexts()
        for value in ((rows[1],), (rows[0], rows[2]), (rows[1], rows[0]), rows[:2] + rows[:1]):
            self.factory_rejected(value, "LEDGER_CONTEXT")

    def test_adapter_exact_type_and_single_owner(self):
        class Adapter(l._SyntheticAdapter):
            pass
        for adapter in (Bomb(), None, Adapter()):
            with self.assertRaises(l.LedgerRejected) as error:
                l.create_local_ledger(contexts(1), adapter=adapter)
            self.assertEqual(error.exception.args, ("LEDGER_OWNER",))
        adapter = l._SyntheticAdapter()
        l.create_local_ledger(contexts(1), adapter=adapter)
        with self.assertRaises(l.LedgerRejected) as error:
            l.create_local_ledger(contexts(1), adapter=adapter)
        self.assertEqual(error.exception.args, ("LEDGER_CONSUMED",))

    def test_context_is_not_its_own_baseline(self):
        selected = contexts(1)
        def hook(inv):
            object.__setattr__(selected[0], "commit", "d" * 40)
        ledger = self.ledger(hook=hook, chosen=selected)
        ledger.advance()
        result = ledger.advance()
        self.assertEqual((result.status, result.first_issue, result.final_issue),
                         ("UNKNOWN", "LEDGER_CONTEXT", "LEDGER_CLEANUP"))
        self.assertEqual(ledger._slots[0].baseline[0], "a" * 40)

    def test_inactive_future_slot_mutation_rejected(self):
        selected = contexts(3)
        def hook(inv):
            object.__setattr__(selected[2].modules[-1], "sha256", "d" * 64)
        ledger = self.ledger(3, hook, selected)
        ledger.advance()
        self.assertEqual(ledger.advance().first_issue, "LEDGER_CONTEXT")

    def test_context_foreign_mutation_before_equality(self):
        selected = contexts(1)
        def hook(inv):
            object.__setattr__(selected[0], "commit", Bomb())
        ledger = self.ledger(hook=hook, chosen=selected)
        ledger.advance()
        self.assertEqual(ledger.advance().first_issue, "LEDGER_FORM")

    def test_receipt_primitive_shapes_before_identity(self):
        for field, value in (("baseline", Bomb()), ("sequence", True), ("before", None), ("after", Bomb())):
            def hook(inv):
                object.__setattr__(inv.receipt, field, value)
            ledger = self.ledger(hook=hook)
            ledger.advance()
            self.assertEqual(ledger.advance().status, "UNKNOWN")

    def test_receipt_wrong_owner_slot_invocation_and_return_binding(self):
        for field in ("owner", "slot", "invocation", "context", "ledger"):
            def hook(inv):
                object.__setattr__(inv.receipt, field, object())
            ledger = self.ledger(hook=hook)
            ledger.advance()
            self.assertEqual(ledger.advance().first_issue, "LEDGER_OWNER")

    def test_swapped_receipt_is_closed(self):
        def hook(inv):
            inv.receipt = object()
        ledger = self.ledger(hook=hook)
        ledger.advance()
        self.assertEqual(ledger.advance().first_issue, "LEDGER_OWNER")

    def test_reentrancy_outer_normal_return_cannot_heal(self):
        events = []
        def hook(inv):
            events.append(inv.ledger.advance())
        ledger = self.ledger(hook=hook)
        ledger.advance()
        result = ledger.advance()
        self.assertEqual(result.first_issue, "LEDGER_REENTRANT")
        self.assertEqual(result.state, "START_RESERVED")
        self.assertEqual((result.status, result.cleanup_state), ("UNKNOWN", "PENDING"))
        self.assertEqual(len(events), 1)

    def test_reentrant_failure_cleanup_is_sticky(self):
        def hook(inv):
            inv.ledger.failure_cleanup()
        ledger = self.ledger(hook=hook)
        ledger.advance()
        self.assertEqual(ledger.advance().first_issue, "LEDGER_REENTRANT")

    def test_partial_unknown_and_generic_errors_keep_reservations(self):
        for signal in (l._SyntheticPartial, l._SyntheticUnknown, ValueError):
            def hook(inv):
                raise signal("synthetic-private")
            ledger = self.ledger(hook=hook)
            ledger.advance()
            result = ledger.advance()
            self.assertEqual((result.status, result.starts, result.commands), ("UNKNOWN", 1, 0))
            self.assertEqual(result.first_issue, "LEDGER_INTERNAL")
            self.assertNotIn("synthetic-private", repr(result))

    def test_closed_issue_allowlist_empty_and_foreign_exception_args(self):
        for args in ((), ("synthetic-private",), ("private" * 10000,),
                     (Bomb(),), ("LEDGER_ORDER", "extra")):
            def hook(inv):
                raise l.LedgerRejected(*args)
            ledger = self.ledger(hook=hook)
            ledger.advance()
            result = ledger.advance()
            self.assertEqual(result.first_issue, "LEDGER_INTERNAL")
            self.assertEqual(repr(result), "<LedgerDiagnostic>")

    def test_signals_ignore_foreign_and_malformed_attributes(self):
        def hook(inv):
            error = l._SyntheticUnknown(Bomb())
            error.private = Bomb()
            raise error
        ledger = self.ledger(hook=hook)
        ledger.advance()
        self.assertEqual(ledger.advance().status, "UNKNOWN")

    def test_provider_encoder_and_both_signal_priority(self):
        for signal, issue in ((l._SyntheticProviderLoss, "HASH_PROVIDER_BINDING"),
                              (l._SyntheticEncoderLoss, "REPORT_ENCODER_BINDING"),
                              (l._SyntheticBothLoss, "HASH_PROVIDER_BINDING")):
            calls = []
            def hook(inv):
                calls.append(inv)
                if len(calls) == 1:
                    inv.ledger.advance()
                    raise signal()
            ledger = self.ledger(hook=hook)
            ledger.advance()
            result = ledger.advance()
            self.assertEqual(result.first_issue, "LEDGER_REENTRANT")
            self.assertEqual(result.final_issue, "LEDGER_CLEANUP")
            self.assertEqual(ledger.failure_cleanup().final_issue, issue)

    def test_failure_cleanup_once_shared_reserve_and_completion(self):
        calls = []
        def hook(inv):
            calls.append(inv)
            if len(calls) == 1:
                raise l._SyntheticUnknown()
        ledger = self.ledger(hook=hook)
        ledger.advance()
        ledger.advance()
        result = ledger.failure_cleanup()
        self.assertEqual((result.status, result.cleanup), ("UNKNOWN", 1))
        self.assertTrue(ledger._slots[0].cleanup_complete)
        self.assertTrue(ledger._slots[0].bits & 16)
        for _ in range(10):
            ledger.failure_cleanup()
            ledger.advance()
        self.assertEqual(len(calls), 2)
        self.assertEqual(ledger.diagnose().cleanup, 1)

    def test_normal_cleanup_reservation_can_be_used_after_stop_once(self):
        calls = []
        def hook(inv):
            calls.append(inv.before)
        ledger = self.ledger(hook=hook)
        for _ in range(10):
            ledger.advance()
        self.assertEqual(ledger.diagnose().state, "AWAIT_CLEANUP")
        self.assertTrue(ledger._slots[0].bits & 16)
        ledger._stop("LEDGER_ORDER")
        ledger.failure_cleanup()
        ledger.failure_cleanup()
        self.assertEqual(calls.count(10), 1)
        self.assertEqual(ledger.diagnose().status, "FAILED")

    def test_cleanup_failure_dominates_provider_and_does_not_retry(self):
        calls = []
        def hook(inv):
            calls.append(inv)
            if len(calls) == 1:
                raise l._SyntheticProviderLoss()
            raise l._SyntheticCleanupUnknown()
        ledger = self.ledger(hook=hook)
        ledger.advance()
        ledger.advance()
        result = ledger.failure_cleanup()
        self.assertEqual((result.first_issue, result.final_issue, result.status),
                         ("HASH_PROVIDER_BINDING", "LEDGER_CLEANUP", "UNKNOWN"))
        ledger.failure_cleanup()
        self.assertEqual(len(calls), 2)
        self.assertFalse(ledger._slots[0].cleanup_complete)

    def test_cleanup_pre_failure_attempt_is_consumed(self):
        selected = contexts(1)
        def hook(inv):
            raise l._SyntheticUnknown()
        ledger = self.ledger(hook=hook, chosen=selected)
        ledger.advance()
        ledger.advance()
        object.__setattr__(selected[0], "commit", "d" * 40)
        result = ledger.failure_cleanup()
        self.assertEqual((result.cleanup, result.final_issue), (1, "LEDGER_CLEANUP"))
        for _ in range(20):
            ledger.failure_cleanup()
        self.assertEqual(ledger.diagnose().cleanup, 1)

    def test_failed_normal_cleanup_is_not_invoked_again(self):
        calls = []
        def hook(inv):
            calls.append(inv.before)
            if inv.before == 10:
                raise l._SyntheticCleanupUnknown()
        ledger = self.ledger(hook=hook)
        for _ in range(11):
            ledger.advance()
        ledger.failure_cleanup()
        self.assertEqual(calls.count(10), 1)
        self.assertEqual(ledger.diagnose().cleanup, 1)

    def test_terminal_calls_and_following_slot_never_invoke(self):
        calls = []
        def hook(inv):
            calls.append(inv.context.ordinal)
            raise l._SyntheticPartial()
        ledger = self.ledger(3, hook)
        ledger.advance()
        ledger.advance()
        for _ in range(50):
            ledger.advance()
        self.assertEqual(calls, [1])
        self.assertEqual(ledger.diagnose().starts, 1)
        self.assertLessEqual(ledger.diagnose().bookings, 42)

    def test_core_code_drift_is_detected_before_changed_checker(self):
        for fn in (l.LocalLedger._post, l.LocalLedger._receipt_check,
                   l.LocalLedger._contexts_check, l._Anchors.check, l._function_check):
            calls = []
            old = fn.__code__
            # Closurefreier Ersatzcode greift nur auf eine eigene gehaltene Liste zu.
            def foreign(*args, **kwargs):
                _DRIFT_HITS.append("changed")
            def hook(inv):
                fn.__code__ = foreign.__code__
            self.restore.append(lambda fn=fn, old=old: setattr(fn, "__code__", old))
            self.register_own_global("_DRIFT_HITS", calls)
            ledger = self.ledger(hook=hook)
            ledger.advance()
            try:
                result = ledger.advance()
                self.assertEqual(result.first_issue, "LEDGER_OWNER")
                self.assertEqual(calls, [])
            finally:
                fn.__code__ = old
                del l._DRIFT_HITS

    def test_diagnostic_and_generated_constructor_code_drift_not_dispatched(self):
        for fn in (l.LocalLedger.diagnose, l.LedgerDiagnostic.__init__):
            old = fn.__code__
            hits = []
            # Generated __init__ has closurecells: retain matching freevars.
            if fn.__closure__:
                def build(cell):
                    def foreign(*args, **kwargs):
                        cell
                        _DRIFT_HITS.append("changed")
                    return foreign
                replacement = build(fn.__closure__[0].cell_contents)
                # Source fixture only targets compatible constructor closurearity.
                self.assertEqual(len(replacement.__closure__), len(fn.__closure__))
            else:
                def replacement(*args, **kwargs):
                    _DRIFT_HITS.append("changed")
            def hook(inv):
                fn.__code__ = replacement.__code__
            self.restore.append(lambda fn=fn, old=old: setattr(fn, "__code__", old))
            self.register_own_global("_DRIFT_HITS", hits)
            ledger = self.ledger(hook=hook)
            ledger.advance()
            try:
                result = ledger.advance()
                self.assertEqual(result.first_issue, "LEDGER_OWNER")
                self.assertEqual(hits, [])
            finally:
                fn.__code__ = old
                del l._DRIFT_HITS

    def test_hook_default_and_kwdefault_inplace_changes_are_detected(self):
        for mode in ("default", "keyword"):
            def hook(inv, fixed=None, *, selected=None):
                if mode == "default":
                    hook.__defaults__ = (object(),)
                else:
                    hook.__kwdefaults__["selected"] = object()
            ledger = self.ledger(hook=hook)
            ledger.advance()
            self.assertEqual(ledger.advance().first_issue, "LEDGER_OWNER")

    def test_adapter_hook_replacement_and_owner_exchange(self):
        for mode in ("hook", "owner"):
            def hook(inv):
                if mode == "hook":
                    inv.ledger._adapter.hook = None
                else:
                    inv.ledger._adapter._owner = object()
            ledger = self.ledger(hook=hook)
            ledger.advance()
            self.assertEqual(ledger.advance().first_issue, "LEDGER_OWNER")

    def test_native_post_lookups_are_held_before_namespace_drift(self):
        for name in ("type", "len", "tuple", "all", "zip", "max"):
            hits = []
            def foreign(*args, **kwargs):
                hits.append(name)
                raise AssertionError("UNBOUND_NATIVE")
            def hook(inv):
                l.__dict__[name] = foreign
            self.register_global_change(name, foreign)
            ledger = self.ledger(hook=hook)
            ledger.advance()
            try:
                result = ledger.advance()
                self.assertEqual(result.first_issue, "LEDGER_OWNER")
                self.assertEqual(hits, [])
            finally:
                del l.__dict__[name]

    def test_local_diagnostic_builtins_do_not_share_mutated_module_globals(self):
        hits = []
        class ForeignObject:
            @staticmethod
            def __new__(*args):
                hits.append("allocation")
                raise AssertionError("UNBOUND_DIAGNOSTIC")
        def hook(inv):
            l.object = ForeignObject
        self.register_global_change("object", ForeignObject)
        ledger = self.ledger(hook=hook)
        ledger.advance()
        try:
            result = ledger.advance()
            self.assertEqual((result.first_issue, result.final_issue),
                             ("LEDGER_OWNER", "LEDGER_CLEANUP"))
            self.assertEqual(hits, [])
        finally:
            del l.object

    def test_reentrant_first_cause_survives_later_core_loss(self):
        old = l.LocalLedger._post.__code__
        self.restore.append(lambda: setattr(l.LocalLedger._post, "__code__", old))
        def replacement(*args, **kwargs):
            raise AssertionError("CHANGED_POST")
        def hook(inv):
            inv.ledger.advance()
            l.LocalLedger._post.__code__ = replacement.__code__
        ledger = self.ledger(hook=hook)
        ledger.advance()
        try:
            result = ledger.advance()
            self.assertEqual(result.first_issue, "LEDGER_REENTRANT")
            self.assertEqual(result.final_issue, "LEDGER_CLEANUP")
            self.assertEqual(result.state, "START_RESERVED")
        finally:
            l.LocalLedger._post.__code__ = old

    def test_cleanup_post_failure_never_marks_completion(self):
        chosen = contexts(1)
        calls = []
        def hook(inv):
            calls.append(inv)
            if len(calls) == 1:
                raise l._SyntheticUnknown()
            object.__setattr__(chosen[0], "commit", "d" * 40)
        ledger = self.ledger(hook=hook, chosen=chosen)
        ledger.advance()
        ledger.advance()
        result = ledger.failure_cleanup()
        self.assertEqual((result.status, result.first_issue, result.final_issue,
                          result.cleanup_state, result.cleanup),
                         ("UNKNOWN", "LEDGER_INTERNAL", "LEDGER_CLEANUP", "UNKNOWN", 1))
        self.assertFalse(ledger._slots[0].cleanup_complete)
        ledger.failure_cleanup()
        self.assertEqual(len(calls), 2)

    def test_missing_cleanup_is_dominant_until_one_known_fake_completion(self):
        calls = []
        def hook(inv):
            calls.append(inv)
            if len(calls) == 1:
                raise l._SyntheticProviderLoss()
        ledger = self.ledger(hook=hook)
        ledger.advance()
        result = ledger.advance()
        self.assertEqual((result.status, result.first_issue, result.final_issue, result.cleanup_state),
                         ("UNKNOWN", "HASH_PROVIDER_BINDING", "LEDGER_CLEANUP", "PENDING"))
        result = ledger.failure_cleanup()
        self.assertEqual((result.status, result.first_issue, result.final_issue, result.cleanup_state),
                         ("FAILED", "HASH_PROVIDER_BINDING", "HASH_PROVIDER_BINDING", "COMPLETE"))
        self.assertNotEqual(result.state, "CLOSED")

    def test_malformed_private_state_has_no_foreign_boolean_or_arithmetic(self):
        for name in ("_busy", "_terminal", "_rank", "_bookings", "_first", "_final", "_index", "_slots"):
            ledger = self.ledger()
            setattr(ledger, name, Bomb())
            result = ledger.advance()
            self.assertIn(result.first_issue, ("LEDGER_OWNER", "LEDGER_FORM"))
            self.assertIn(result.status, ("FAILED", "UNKNOWN"))
        for name in ("start_attempted", "cleanup_attempted", "bits"):
            ledger = self.ledger()
            ledger._stop("LEDGER_ORDER")
            setattr(ledger._slots[0], name, Bomb())
            result = ledger.failure_cleanup()
            self.assertEqual(result.first_issue, "LEDGER_ORDER")
            self.assertEqual(result.cleanup, 0)

    def test_corrupted_diagnostic_issue_fields_are_bounded_before_membership(self):
        for value in (Bomb(), "private" * 10000):
            ledger = self.ledger()
            ledger._first = ledger._final = value
            result = ledger.diagnose()
            self.assertEqual((result.first_issue, result.final_issue), ("LEDGER_OWNER", "LEDGER_OWNER"))
            self.assertEqual(repr(result), "<LedgerDiagnostic>")

    def test_cleanup_counters_and_slot_state_guard_precedes_reservation_math(self):
        for target, name in (("ledger", "_bookings"), ("ledger", "_cleanup"),
                             ("ledger", "_rank"), ("ledger", "_commands"),
                             ("slot", "state"), ("slot", "sequence")):
            calls = []
            def hook(inv):
                calls.append(inv)
                raise l._SyntheticUnknown()
            ledger = self.ledger(hook=hook)
            ledger.advance()
            ledger.advance()
            obj = ledger if target == "ledger" else ledger._slots[0]
            setattr(obj, name, Bomb())
            result = ledger.failure_cleanup()
            self.assertEqual(result.final_issue, "LEDGER_CLEANUP")
            self.assertEqual(len(calls), 1)

    def test_signal_alias_drift_cannot_reselect_failure_priority(self):
        replacement = ValueError
        held = self.register_existing_global_change("_SyntheticProviderLoss", replacement)
        def hook(inv):
            l._SyntheticProviderLoss = replacement
            raise held()
        ledger = self.ledger(hook=hook)
        ledger.advance()
        result = ledger.advance()
        self.assertEqual(result.first_issue, "HASH_PROVIDER_BINDING")
        self.assertEqual(result.final_issue, "LEDGER_CLEANUP")

    def test_post_foreign_slot_sequence_is_rejected_before_receipt_comparison(self):
        captured = []
        def hook(inv):
            captured.append(inv)
            inv.slot.sequence = Bomb()
        ledger = self.ledger(hook=hook)
        ledger.advance()
        result = ledger.advance()
        self.assertEqual(result.first_issue, "LEDGER_FORM")
        self.assertTrue(captured[0].consumed)

    def test_active_reservation_and_start_attempt_cannot_be_rolled_back(self):
        for name, value in (("bits", 0), ("start_attempted", False),
                            ("state", 0), ("sequence", 0),
                            ("cleanup_attempted", True), ("cleanup_complete", True)):
            calls = []
            def hook(inv):
                calls.append(inv)
                if len(calls) == 1:
                    setattr(inv.slot, name, value)
            ledger = self.ledger(hook=hook)
            ledger.advance()
            result = ledger.advance()
            slot = ledger._slots[0]
            self.assertEqual((result.first_issue, result.final_issue, result.status),
                             ("LEDGER_OWNER", "LEDGER_CLEANUP", "UNKNOWN"))
            self.assertEqual((slot.state, slot.sequence, slot.bits), (1, 1, 1))
            self.assertTrue(slot.start_attempted)
            self.assertFalse(slot.cleanup_attempted)
            self.assertFalse(slot.cleanup_complete)
            self.assertTrue(calls[0].consumed)
            result = ledger.failure_cleanup()
            self.assertEqual((result.status, result.first_issue, result.cleanup_state),
                             ("FAILED", "LEDGER_OWNER", "COMPLETE"))
            self.assertEqual(len(calls), 2)
            ledger.failure_cleanup()
            self.assertEqual(len(calls), 2)

    def test_valid_counter_or_index_changes_cannot_mint_or_erase_bookings(self):
        for name, value in (("_index", 1), ("_starts", 0), ("_commands", 1),
                            ("_bookings", 0), ("_cleanup", 1)):
            calls = []
            def hook(inv):
                calls.append(inv)
                if len(calls) == 1:
                    setattr(inv.ledger, name, value)
            ledger = self.ledger(3, hook=hook)
            ledger.advance()
            result = ledger.advance()
            self.assertEqual((result.first_issue, result.slot_index, result.starts,
                              result.commands, result.bookings, result.cleanup),
                             ("LEDGER_OWNER", 1, 1, 0, 2, 0))
            self.assertTrue(ledger._slots[0].start_attempted)
            self.assertFalse(ledger._slots[1].start_attempted)
            ledger.advance()
            self.assertEqual(len(calls), 1)
            result = ledger.failure_cleanup()
            self.assertEqual((result.slot_index, result.cleanup), (1, 1))
            self.assertEqual(len(calls), 2)

    def test_inactive_slots_keep_all_reserved_state_and_identity(self):
        for index in (1, 2):
            for name, value in (("state", 11), ("sequence", 11), ("bits", 31),
                                ("start_attempted", True), ("cleanup_attempted", True),
                                ("cleanup_complete", True), ("context", contexts(1)[0]),
                                ("baseline", ("replacement",))):
                calls = []
                def hook(inv):
                    calls.append(inv)
                    if len(calls) == 1:
                        setattr(inv.ledger._slots[index], name, value)
                ledger = self.ledger(3, hook=hook)
                slots = ledger._slots
                originals = tuple((slot.context, slot.baseline) for slot in slots)
                ledger.advance()
                result = ledger.advance()
                self.assertEqual((result.first_issue, result.slot_index), ("LEDGER_OWNER", 1))
                self.assertIs(ledger._slots, slots)
                for future, (context, baseline) in zip(slots[1:], originals[1:]):
                    self.assertEqual((future.state, future.sequence, future.bits), (0, 0, 0))
                    self.assertFalse(future.start_attempted)
                    self.assertFalse(future.cleanup_attempted)
                    self.assertFalse(future.cleanup_complete)
                    self.assertIs(future.context, context)
                    self.assertIs(future.baseline, baseline)
                ledger.failure_cleanup()
                for _ in range(3):
                    ledger.advance()
                self.assertEqual(len(calls), 2)
                self.assertEqual(ledger.diagnose().slot_index, 1)

    def test_replaced_slots_tuple_is_not_a_new_state_authority(self):
        calls = []
        def hook(inv):
            calls.append(inv)
            if len(calls) == 1:
                inv.ledger._slots = (inv.slot,)
        ledger = self.ledger(3, hook=hook)
        selected = ledger._slots
        ledger.advance()
        result = ledger.advance()
        self.assertEqual(result.first_issue, "LEDGER_OWNER")
        self.assertIs(ledger._slots, selected)
        self.assertEqual(len(ledger._slots), 3)
        self.assertTrue(ledger._slots[0].start_attempted)
        self.assertFalse(ledger._slots[1].start_attempted)

    def test_cleanup_attempt_and_completion_mutations_never_renew_callback(self):
        for mode in ("normal", "failure"):
            for name, value in (("bits", 0), ("cleanup_attempted", False),
                                ("cleanup_complete", True), ("start_attempted", False)):
                calls = []
                def hook(inv):
                    calls.append(inv)
                    if mode == "failure" and len(calls) == 1:
                        raise l._SyntheticUnknown()
                    if (mode == "normal" and inv.before == 10) or (mode == "failure" and len(calls) == 2):
                        setattr(inv.slot, name, value)
                ledger = self.ledger(hook=hook)
                ledger.advance()
                if mode == "normal":
                    for _ in range(9):
                        ledger.advance()
                    self.assertEqual(ledger._slots[0].state, 10)
                    result = ledger.advance()
                    expected_calls = 10
                    expected_first = "LEDGER_OWNER"
                else:
                    ledger.advance()
                    result = ledger.failure_cleanup()
                    expected_calls = 2
                    expected_first = "LEDGER_INTERNAL"
                slot = ledger._slots[0]
                self.assertEqual((result.status, result.first_issue, result.final_issue,
                                  result.cleanup, result.cleanup_state),
                                 ("UNKNOWN", expected_first, "LEDGER_CLEANUP", 1, "UNKNOWN"))
                self.assertTrue(slot.start_attempted)
                self.assertTrue(slot.cleanup_attempted)
                self.assertFalse(slot.cleanup_complete)
                self.assertTrue(slot.bits & 16)
                for _ in range(3):
                    ledger.failure_cleanup()
                    ledger.advance()
                self.assertEqual(len(calls), expected_calls)
                self.assertEqual(ledger.diagnose().cleanup, 1)

    def test_genuine_reentry_keeps_first_booking_and_reservation_obligation(self):
        calls = []
        def hook(inv):
            calls.append(inv)
            if len(calls) == 1:
                inv.ledger.advance()
                inv.slot.bits = 0
                inv.slot.start_attempted = False
        ledger = self.ledger(hook=hook)
        ledger.advance()
        result = ledger.advance()
        self.assertEqual((result.first_issue, result.final_issue, result.bookings),
                         ("LEDGER_REENTRANT", "LEDGER_CLEANUP", 2))
        self.assertEqual(ledger._slots[0].bits, 1)
        self.assertTrue(ledger._slots[0].start_attempted)
        result = ledger.failure_cleanup()
        self.assertEqual((result.status, result.first_issue, result.cleanup, result.cleanup_state),
                         ("FAILED", "LEDGER_REENTRANT", 1, "COMPLETE"))
        self.assertEqual(len(calls), 2)

    def test_all_slot_control_primitives_precede_comparison_without_foreign_hits(self):
        for target, name in (("ledger", "_bookings"), ("ledger", "_index"),
                             ("ledger", "_first"), ("slot", "state"),
                             ("slot", "sequence"), ("slot", "bits"),
                             ("slot", "start_attempted"), ("slot", "cleanup_complete")):
            def hook(inv):
                obj = inv.ledger if target == "ledger" else inv.ledger._slots[2]
                setattr(obj, name, Bomb())
            ledger = self.ledger(3, hook=hook)
            ledger.advance()
            result = ledger.advance()
            self.assertEqual(result.first_issue, "LEDGER_FORM")
            self.assertEqual((result.slot_index, result.starts, result.commands, result.cleanup),
                             (1, 1, 0, 0))
            self.assertEqual(ledger._slots[2].state, 0)
            self.assertFalse(ledger._slots[2].start_attempted)

    def test_missing_own_fields_and_stop_code_loss_never_dispatch_changed_error_path(self):
        for target, name in (("slot", "state"), ("slot", "bits"),
                             ("slot", "start_attempted"), ("ledger", "_bookings"),
                             ("ledger", "_first"), ("ledger", "_terminal"),
                             ("anchor", "functions")):
            hits = []
            def foreign(*args, **kwargs):
                _DRIFT_HITS.append("changed-stop")
            self.register_own_global("_DRIFT_HITS", hits)
            original = l.LocalLedger._stop.__code__
            self.restore.append(lambda code=original: setattr(l.LocalLedger._stop, "__code__", code))
            def hook(inv):
                obj = inv.slot if target == "slot" else (
                    inv.ledger._anchors if target == "anchor" else inv.ledger)
                delattr(obj, name)
                l.LocalLedger._stop.__code__ = foreign.__code__
            ledger = self.ledger(hook=hook)
            ledger.advance()
            try:
                result = ledger.advance()
                self.assertEqual((result.first_issue, result.final_issue, result.status),
                                 ("LEDGER_OWNER", "LEDGER_CLEANUP", "UNKNOWN"))
                self.assertEqual((ledger._slots[0].state, ledger._slots[0].bits), (1, 1))
                self.assertTrue(ledger._slots[0].start_attempted)
                for _ in range(3):
                    result = ledger.failure_cleanup()
                self.assertEqual((result.status, result.cleanup, result.final_issue),
                                 ("UNKNOWN", 1, "LEDGER_CLEANUP"))
                self.assertFalse(ledger._slots[0].cleanup_complete)
                self.assertEqual(hits, [])
            finally:
                l.LocalLedger._stop.__code__ = original
                del l._DRIFT_HITS

    def test_signal_dominance_survives_valid_own_state_mutation(self):
        for signal, issue in ((l._SyntheticProviderLoss, "HASH_PROVIDER_BINDING"),
                              (l._SyntheticBothLoss, "HASH_PROVIDER_BINDING"),
                              (l._SyntheticEncoderLoss, "REPORT_ENCODER_BINDING")):
            for mode in ("start", "cleanup"):
                calls = []
                def hook(inv):
                    calls.append(inv)
                    if mode == "cleanup" and len(calls) == 1:
                        raise l._SyntheticUnknown()
                    if len(calls) == (1 if mode == "start" else 2):
                        inv.slot.bits = 0
                        inv.ledger._bookings = 0
                        if mode == "cleanup":
                            inv.slot.cleanup_attempted = False
                            inv.slot.cleanup_complete = True
                        raise signal()
                ledger = self.ledger(hook=hook)
                ledger.advance()
                result = ledger.advance()
                if mode == "start":
                    self.assertEqual((result.first_issue, result.final_issue),
                                     (issue, "LEDGER_CLEANUP"))
                    self.assertEqual(ledger._slots[0].bits, 1)
                    self.assertTrue(ledger._slots[0].start_attempted)
                    result = ledger.failure_cleanup()
                    self.assertEqual((result.status, result.first_issue, result.final_issue,
                                      result.cleanup_state), ("FAILED", issue, issue, "COMPLETE"))
                else:
                    result = ledger.failure_cleanup()
                    self.assertEqual((result.first_issue, result.final_issue, result.status,
                                      result.cleanup, result.cleanup_state),
                                     ("LEDGER_INTERNAL", "LEDGER_CLEANUP", "UNKNOWN", 1, "UNKNOWN"))
                    self.assertTrue(ledger._slots[0].cleanup_attempted)
                    self.assertFalse(ledger._slots[0].cleanup_complete)
                    self.assertTrue(ledger._slots[0].bits & 16)
                for _ in range(3):
                    ledger.failure_cleanup()
                    ledger.advance()
                self.assertEqual(len(calls), 2)

    def test_all_native_descriptor_choices_are_immutable_without_foreign_dispatch(self):
        for index, key in ((3, "_first"), (4, "state"),
                           (5, "status"), (14, "functions")):
            for catch_error in (False, True):
                hits = []
                calls = []
                class ForeignDescriptor:
                    def __get__(self, *args):
                        hits.append("getter")
                        raise AssertionError("FOREIGN_NATIVE_CHOICE")

                    def __set__(self, *args):
                        hits.append("setter")
                        raise AssertionError("FOREIGN_NATIVE_CHOICE")
                foreign = ForeignDescriptor()
                selected = []
                def hook(inv):
                    calls.append(inv)
                    if len(calls) == 1:
                        choice = inv.ledger._report[index]
                        if index == 14:
                            choice = choice[1]
                        selected.append(choice)
                        try:
                            choice[key] = foreign
                        except TypeError:
                            if not catch_error:
                                raise
                ledger = self.ledger(hook=hook)
                original = ledger._report[index]
                if index == 14:
                    original = original[1]
                descriptor = original[key]
                ledger.advance()
                result = ledger.advance()
                self.assertIs(selected[0], original)
                self.assertIs(original[key], descriptor)
                if catch_error:
                    self.assertEqual((result.state, result.first_issue), ("AWAIT_PROFILE", ""))
                    ledger._stop("LEDGER_ORDER")
                    expected_issue = "LEDGER_ORDER"
                else:
                    expected_issue = "LEDGER_INTERNAL"
                    self.assertEqual(result.first_issue, expected_issue)
                result = ledger.diagnose()
                self.assertEqual((result.first_issue, result.final_issue, result.cleanup_state),
                                 (expected_issue, "LEDGER_CLEANUP", "PENDING"))
                result = ledger.failure_cleanup()
                self.assertEqual((result.status, result.first_issue, result.final_issue,
                                  result.cleanup, result.cleanup_state),
                                 ("FAILED", expected_issue, expected_issue, 1, "COMPLETE"))
                for _ in range(3):
                    ledger.failure_cleanup()
                    ledger.diagnose()
                self.assertEqual(len(calls), 2)
                self.assertEqual(hits, [])

    def test_cleanup_after_core_entry_loss_never_dispatches_changed_code(self):
        for mode in ("run_code", "run_alias", "stop_code"):
            hits = []
            def foreign(*args, **kwargs):
                _DRIFT_HITS.append("changed")
            self.register_own_global("_DRIFT_HITS", hits)
            target = l.LocalLedger._stop if mode == "stop_code" else l.LocalLedger._run
            old = target.__code__
            if mode == "run_alias":
                original_alias = self.register_existing_global_change("_LEDGER_RUN", foreign)
            else:
                self.restore.append(lambda fn=target, code=old: setattr(fn, "__code__", code))
            def hook(inv):
                if mode == "run_alias":
                    l._LEDGER_RUN = foreign
                else:
                    target.__code__ = foreign.__code__
            ledger = self.ledger(hook=hook)
            ledger.advance()
            try:
                result = ledger.advance()
                self.assertEqual(result.first_issue, "LEDGER_OWNER")
                for _ in range(3):
                    result = ledger.failure_cleanup()
                self.assertEqual((result.status, result.final_issue, result.cleanup),
                                 ("UNKNOWN", "LEDGER_CLEANUP", 1))
                self.assertFalse(ledger._slots[0].cleanup_complete)
                ledger._busy = Bomb()
                ledger.advance()
                ledger.failure_cleanup()
                self.assertEqual(hits, [])
            finally:
                if mode == "run_alias":
                    l._LEDGER_RUN = original_alias
                else:
                    target.__code__ = old
                del l._DRIFT_HITS

    def test_anchor_instance_and_snapshot_replacements_have_no_foreign_getter(self):
        for mode in ("instance", "functions", "classes", "namespaces"):
            hits = []
            class ForeignAnchor:
                def __getattribute__(self, name):
                    hits.append(name)
                    raise AssertionError("FOREIGN_ANCHOR")
            def hook(inv):
                if mode == "instance":
                    inv.ledger._anchors = ForeignAnchor()
                else:
                    setattr(inv.ledger._anchors, mode, Bomb())
            ledger = self.ledger(hook=hook)
            ledger.advance()
            result = ledger.advance()
            self.assertEqual(result.first_issue, "LEDGER_OWNER")
            for _ in range(3):
                result = ledger.failure_cleanup()
            self.assertEqual((result.status, result.final_issue, result.cleanup),
                             ("UNKNOWN", "LEDGER_CLEANUP", 1))
            self.assertEqual(hits, [])

    def test_class_namespace_and_generated_closure_drift_are_closed(self):
        old = l._Receipt.__repr__ if "__repr__" in l._Receipt.__dict__ else None
        def replacement(self):
            return "private"
        def restore_repr():
            if l._Receipt.__dict__.get("__repr__") is replacement:
                if old is None:
                    del l._Receipt.__repr__
                else:
                    l._Receipt.__repr__ = old
        self.restore.append(restore_repr)
        def hook(inv):
            l._Receipt.__repr__ = replacement
        ledger = self.ledger(hook=hook)
        ledger.advance()
        try:
            self.assertEqual(ledger.advance().first_issue, "LEDGER_OWNER")
        finally:
            if old is None:
                del l._Receipt.__repr__
            else:
                l._Receipt.__repr__ = old
        cell = l._Receipt.__init__.__closure__[0]
        previous = cell.cell_contents
        self.restore.append(lambda: setattr(cell, "cell_contents", previous))
        def closure_hook(inv):
            cell.cell_contents = Bomb()
        ledger = self.ledger(hook=closure_hook)
        ledger.advance()
        try:
            self.assertEqual(ledger.advance().first_issue, "LEDGER_OWNER")
        finally:
            cell.cell_contents = previous

    def test_separate_factory_is_not_global_replay_proof(self):
        selected = contexts(1)
        first = self.ledger(chosen=selected)
        second = self.ledger(chosen=selected)
        self.assertIsNot(first._owner, second._owner)
        self.assertFalse(first.diagnose().replay_attested)
        self.assertFalse(second.diagnose().replay_attested)

    def test_diagnostic_frozen_bounded_private_and_all_flags_false(self):
        result = self.ledger(3).diagnose()
        self.assertEqual(repr(result), "<LedgerDiagnostic>")
        for name in ("trust_attested", "runtime_attested", "channel_attested", "replay_attested",
                     "consumption_attested", "cleanup_attested", "import_used_bytes_attested", "method_approved"):
            self.assertIs(getattr(result, name), False)
        for name in ("context", "nonce", "receipt", "owner", "payload"):
            self.assertFalse(hasattr(result, name))
        with self.assertRaises(FrozenInstanceError):
            result.state = "CLOSED"
        self.assertEqual(len(result.slots), 3)

    def test_no_copy_serialization_reset_or_event_input(self):
        ledger = self.ledger()
        for operation in (lambda: copy.copy(ledger), lambda: copy.deepcopy(ledger), lambda: pickle.dumps(ledger)):
            with self.assertRaises(l.LedgerRejected):
                operation()
        for name in ("reset", "resume", "submit", "mint", "retry"):
            self.assertFalse(hasattr(ledger, name))
        with self.assertRaises(TypeError):
            ledger.advance(("event",))

    def test_initial_context_check_function_and_class_anchors_are_transitive(self):
        ledger = self.ledger()
        functions = tuple(a[0] for a in ledger._anchors.functions)
        for fn in (b._context, b._need, b._hex, b._text, b._integer, b._selector, b._tuple):
            self.assertIn(fn, functions)
        classes = tuple(a[0] for a in ledger._anchors.classes)
        self.assertIn(b.BindingContext, classes)
        self.assertIn(b.SourceDescriptor, classes)
        self.assertTrue(any(ns is b.input82.__dict__ for ns, _ in ledger._anchors.namespaces))

    def test_generated_constructor_closure_contents_are_held(self):
        ledger = self.ledger()
        anchors = [a for a in ledger._anchors.functions if a[0] is l._Receipt.__init__]
        self.assertTrue(anchors)
        for cell, value in anchors[0][-1]:
            self.assertIs(cell.cell_contents, value)

    def test_static_source_has_no_channel_runtime_or_generator_import(self):
        tree = ast.parse((TOOLS / "dgn007_parent_ledger.py").read_text(encoding="utf-8"))
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertEqual(imports, ["dataclasses", "types", "dgn007_import_profile_binding"])
        calls = [node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
        self.assertFalse(set(calls) & {"open", "exec", "eval", "compile", "print", "input"})


if __name__ == "__main__":
    unittest.main()
