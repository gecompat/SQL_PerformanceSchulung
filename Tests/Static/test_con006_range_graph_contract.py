"""Synthetic counterexamples for the CON-006 range graph checker."""
from __future__ import annotations

from dataclasses import replace
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from Tests.Static.con006_conversion_graph_contract import (  # noqa: E402
    ActorOutcome, CaptureEvidence, GraphIdentity, Verdict,
)
from Tests.Static.con006_range_graph_contract import (  # noqa: E402
    RangeCaptureEvidence, RangeControlEvidence, RangeInsertOutcome,
    evaluate_range_capture, evaluate_range_control, evaluate_range_graph,
)


IDENTITY = GraphIdentity(
    database_id=73,
    actor_spids=(("ACTOR_A", 51), ("ACTOR_B", 52)),
    object_name="SQLPERF_LAB_CON006_RUN.lab.DeadlockRows",
    index_name="PK_DeadlockRows",
    hobt_id="72057594000000001",
)


def good_graph() -> str:
    return """<deadlock>
      <victim-list><victimProcess id="processA" /></victim-list>
      <process-list>
        <process id="processA" spid="51" currentdb="73" />
        <process id="processB" spid="52" currentdb="73" />
      </process-list>
      <resource-list><keylock id="rangeA" dbid="73"
        objectname="SQLPERF_LAB_CON006_RUN.lab.DeadlockRows"
        indexname="PK_DeadlockRows" hobtid="72057594000000001">
        <owner-list>
          <owner id="processA" mode="RangeS-S" />
        </owner-list>
        <waiter-list>
          <waiter id="processB" mode="RangeI-N" requestType="wait" />
        </waiter-list>
      </keylock><keylock id="rangeB" dbid="73"
        objectname="SQLPERF_LAB_CON006_RUN.lab.DeadlockRows"
        indexname="PK_DeadlockRows" hobtid="72057594000000001">
        <owner-list><owner id="processB" mode="RangeS-S" /></owner-list>
        <waiter-list><waiter id="processA" mode="RangeI-N" requestType="wait" /></waiter-list>
      </keylock></resource-list>
    </deadlock>"""


def change_graph(mutator) -> str:
    root = ET.fromstring(good_graph())
    mutator(root)
    return ET.tostring(root, encoding="unicode")


def good_capture() -> CaptureEvidence:
    return CaptureEvidence(
        expected_run_token="RUN20261106A",
        observed_run_token="RUN20261106A",
        event_name="xml_deadlock_report",
        source_session="system_health",
        database_id=73,
        actor_spids=IDENTITY.actor_spids,
        event_timestamp_utc="2026-11-06T12:00:00.250Z",
        run_started_utc="2026-11-06T11:59:00Z",
        run_finished_utc="2026-11-06T12:01:00Z",
        matching_event_count=1,
        actor_outcomes=(
            ActorOutcome("ACTOR_A", 51, "VICTIM", 1205),
            ActorOutcome("ACTOR_B", 52, "SURVIVOR", None),
        ),
        graph_identity=IDENTITY,
        graph_xml=good_graph(),
    )


def good_range_capture() -> RangeCaptureEvidence:
    capture = good_capture()
    return RangeCaptureEvidence(
        capture=capture,
        expected_initial_keys=(10, 90),
        expected_insertions=(("ACTOR_A", 30), ("ACTOR_B", 70)),
        insert_outcomes=(
            RangeInsertOutcome("ACTOR_A", 51, 30, "ROLLED_BACK", 1205),
            RangeInsertOutcome("ACTOR_B", 52, 70, "INSERTED", None),
        ),
        observed_final_keys=(10, 70, 90),
    )


class RangeGraphContractTests(unittest.TestCase):
    def test_serial_control_requires_both_inserts_and_complete_final_state(self):
        evidence = RangeControlEvidence(
            expected_run_token="RUN-CONTROL-1", observed_run_token="RUN-CONTROL-1",
            actor_spids=IDENTITY.actor_spids,
            actor_outcomes=(ActorOutcome("ACTOR_A", 51, "SUCCESS", None),
                            ActorOutcome("ACTOR_B", 52, "SUCCESS", None)),
            expected_initial_keys=(10, 90), expected_insertions=(("ACTOR_A", 30), ("ACTOR_B", 70)),
            observed_final_keys=(10, 30, 70, 90), matching_deadlock_event_count=0,
            observed_insertions=(("ACTOR_A", 30), ("ACTOR_B", 70)),
        )
        self.assertEqual(evaluate_range_control(evidence).verdict, Verdict.PASS)

    def test_serial_control_missing_fields_are_not_proven(self):
        base = RangeControlEvidence(
            "RUN-CONTROL-1", "RUN-CONTROL-1", IDENTITY.actor_spids,
            (ActorOutcome("ACTOR_A", 51, "SUCCESS", None),
             ActorOutcome("ACTOR_B", 52, "SUCCESS", None)),
            (10, 90), (("ACTOR_A", 30), ("ACTOR_B", 70)), (10, 30, 70, 90), 0,
            (("ACTOR_A", 30), ("ACTOR_B", 70)),
        )
        self.assertEqual(evaluate_range_control(None).verdict, Verdict.NOT_PROVEN)
        for missing in ("observed_run_token", "expected_initial_keys", "observed_final_keys",
                        "observed_insertions",
                        "actor_outcomes", "matching_deadlock_event_count"):
            with self.subTest(missing=missing):
                self.assertEqual(evaluate_range_control(replace(base, **{missing: None})).verdict,
                                 Verdict.NOT_PROVEN)

    def test_serial_control_rejects_incomplete_state_failed_actor_or_event(self):
        base = RangeControlEvidence(
            "RUN-CONTROL-1", "RUN-CONTROL-1", IDENTITY.actor_spids,
            (ActorOutcome("ACTOR_A", 51, "SUCCESS", None),
             ActorOutcome("ACTOR_B", 52, "SUCCESS", None)),
            (10, 90), (("ACTOR_A", 30), ("ACTOR_B", 70)), (10, 30, 70, 90), 0,
            (("ACTOR_A", 30), ("ACTOR_B", 70)),
        )
        variants = (
            replace(base, observed_final_keys=(10, 30, 90)),
            replace(base, actor_outcomes=(base.actor_outcomes[0], ActorOutcome("ACTOR_B", 52, "ERROR", 2627))),
            replace(base, matching_deadlock_event_count=1),
            replace(base, observed_run_token="OTHER"),
            replace(base, observed_final_keys=(10, 30, 30, 70, 90)),
            replace(base, observed_insertions=(("ACTOR_A", 70), ("ACTOR_B", 30))),
        )
        for evidence in variants:
            with self.subTest(evidence=evidence):
                self.assertEqual(evaluate_range_control(evidence).verdict, Verdict.FAIL)

    def test_reciprocal_range_insert_waits_on_two_keys_pass_without_lock_mode_assumption(self):
        result = evaluate_range_graph(good_graph(), IDENTITY)
        self.assertEqual(result.verdict, Verdict.PASS)
        self.assertEqual(result.victim_spid, 51)

    def test_checker_preserves_observed_modes_instead_of_fixing_a_range_pair(self):
        def mutate(root):
            first, second = root.findall("resource-list/keylock")
            first.find("owner-list/owner").set("mode", "RangeS-U")
            first.find("waiter-list/waiter").set("mode", "X")
            second.find("owner-list/owner").set("mode", "RangeS-U")
            second.find("waiter-list/waiter").set("mode", "X")

        source = change_graph(mutate)
        self.assertEqual(evaluate_range_graph(source, IDENTITY).verdict, Verdict.PASS)

    def test_compatible_modes_and_unknown_modes_cannot_claim_a_closed_cycle(self):
        compatible = change_graph(lambda root: [
            node.set("mode", "S") for node in root.findall("resource-list/keylock/owner-list/owner")
        ] + [node.set("mode", "S") for node in root.findall("resource-list/keylock/waiter-list/waiter")])
        unknown = change_graph(lambda root: root.findall("resource-list/keylock")[1].find(
            "waiter-list/waiter").set("mode", "not-a-lock-mode"))
        self.assertEqual(evaluate_range_graph(compatible, IDENTITY).verdict, Verdict.FAIL)
        self.assertEqual(evaluate_range_graph(unknown, IDENTITY).verdict, Verdict.FAIL)

    def test_capture_binds_range_graph_event_window_victim_and_survivor(self):
        result = evaluate_range_capture(good_range_capture())
        self.assertEqual(result.verdict, Verdict.PASS)
        self.assertEqual(result.victim_spid, 51)
        self.assertEqual(evaluate_range_capture(None).verdict, Verdict.NOT_PROVEN)

    def test_deadlock_capture_requires_insert_rollback_and_exact_survivor_final_state(self):
        good = good_range_capture()
        self.assertEqual(evaluate_range_capture(replace(
            good, observed_final_keys=(10, 30, 70, 90)
        )).verdict, Verdict.FAIL)
        self.assertEqual(evaluate_range_capture(replace(
            good, insert_outcomes=(
                RangeInsertOutcome("ACTOR_A", 51, 30, "INSERTED", None),
                RangeInsertOutcome("ACTOR_B", 52, 70, "ROLLED_BACK", 1205),
            )
        )).verdict, Verdict.FAIL)
        self.assertEqual(evaluate_range_capture(replace(
            good, insert_outcomes=None
        )).verdict, Verdict.NOT_PROVEN)

    def test_capture_rejects_wrong_event_outside_window_and_wrong_victim(self):
        good = good_range_capture()
        for capture in (
            replace(good.capture, source_session="other_session"),
            replace(good.capture, event_timestamp_utc="2026-11-06T12:02:00Z"),
            replace(good.capture, actor_outcomes=(
                ActorOutcome("ACTOR_A", 51, "VICTIM", 1204),
                ActorOutcome("ACTOR_B", 52, "SURVIVOR", None),
            )),
        ):
            with self.subTest(capture=capture):
                self.assertEqual(evaluate_range_capture(replace(good, capture=capture)).verdict, Verdict.FAIL)

    def test_capture_requires_one_matching_graph_event(self):
        good = good_range_capture()
        self.assertEqual(evaluate_range_capture(replace(
            good, capture=replace(good.capture, matching_event_count=0))).verdict, Verdict.NOT_PROVEN)
        self.assertEqual(evaluate_range_capture(replace(
            good, capture=replace(good.capture, matching_event_count=2))).verdict, Verdict.FAIL)

    def test_missing_graph_or_identity_is_not_proven(self):
        self.assertEqual(evaluate_range_graph(None, IDENTITY).verdict, Verdict.NOT_PROVEN)
        self.assertEqual(evaluate_range_graph(good_graph(), None).verdict, Verdict.NOT_PROVEN)

    def test_requires_two_owned_actors_and_one_victim(self):
        extra_process = change_graph(lambda root: root.find("process-list").append(
            ET.Element("process", id="processC", spid="53", currentdb="73")))
        extra_victim = change_graph(lambda root: root.find("victim-list").append(
            ET.Element("victimProcess", id="processB")))
        foreign_db = change_graph(lambda root: root.find("process-list/process").set(
            "currentdb", "74"))
        for source in (extra_process, extra_victim, foreign_db):
            with self.subTest(source=source):
                self.assertEqual(evaluate_range_graph(source, IDENTITY).verdict, Verdict.FAIL)

    def test_requires_exactly_two_supplied_key_resources(self):
        for name, value in (("dbid", "74"), ("indexname", "other"),
                            ("hobtid", "72057594000000002")):
            source = change_graph(lambda root: root.find("resource-list/keylock").set(name, value))
            with self.subTest(name=name):
                self.assertEqual(evaluate_range_graph(source, IDENTITY).verdict, Verdict.FAIL)
        duplicate = change_graph(lambda root: root.find("resource-list").append(
            ET.fromstring(ET.tostring(root.find("resource-list/keylock"), encoding="unicode"))))
        self.assertEqual(evaluate_range_graph(duplicate, IDENTITY).verdict, Verdict.FAIL)

    def test_both_actors_must_form_reciprocal_key_ownership_and_waits(self):
        missing_owner = change_graph(lambda root: root.find(
                "resource-list/keylock/owner-list").remove(root.find(
                "resource-list/keylock/owner-list/owner[@id='processA']")))
        foreign_waiter = change_graph(lambda root: root.findall("resource-list/keylock")[1].find(
            "waiter-list/waiter").set("id", "foreign"))
        for source in (missing_owner, foreign_waiter):
            with self.subTest(source=source):
                self.assertEqual(evaluate_range_graph(source, IDENTITY).verdict, Verdict.FAIL)

    def test_actual_lock_mode_and_request_type_fields_are_required(self):
        missing_mode = change_graph(lambda root: root.findall("resource-list/keylock")[1].find(
            "waiter-list/waiter").attrib.pop("mode"))
        missing_request = change_graph(lambda root: root.findall("resource-list/keylock")[1].find(
            "waiter-list/waiter").attrib.pop("requestType"))
        unknown_request = change_graph(lambda root: root.findall("resource-list/keylock")[1].find(
            "waiter-list/waiter").set("requestType", "arbitrary"))
        conversion_request = change_graph(lambda root: root.findall("resource-list/keylock")[1].find(
            "waiter-list/waiter").set("requestType", "convert"))
        self.assertEqual(evaluate_range_graph(missing_mode, IDENTITY).verdict, Verdict.FAIL)
        self.assertEqual(evaluate_range_graph(missing_request, IDENTITY).verdict, Verdict.FAIL)
        self.assertEqual(evaluate_range_graph(unknown_request, IDENTITY).verdict, Verdict.FAIL)
        self.assertEqual(evaluate_range_graph(conversion_request, IDENTITY).verdict, Verdict.FAIL)

    def test_unsafe_or_malformed_xml_fails(self):
        for source in ("<!DOCTYPE deadlock><deadlock />", "<deadlock", b"\xff",
                       "<deadlock />" * 20_000):
            with self.subTest(source=source[:32]):
                self.assertEqual(evaluate_range_graph(source, IDENTITY).verdict, Verdict.FAIL)


if __name__ == "__main__":
    unittest.main()
