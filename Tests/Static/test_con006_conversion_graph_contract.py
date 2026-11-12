"""Synthetic counterexamples for the offline CON-006 conversion graph contract."""
from __future__ import annotations

from dataclasses import replace
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from con006_conversion_graph_contract import (  # noqa: E402
    MAX_GRAPH_BYTES,
    ActorOutcome,
    CaptureEvidence,
    GraphIdentity,
    Verdict,
    evaluate_conversion_capture,
    evaluate_conversion_graph,
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
      <resource-list>
        <keylock dbid="73" objectname="SQLPERF_LAB_CON006_RUN.lab.DeadlockRows"
                 indexname="PK_DeadlockRows" hobtid="72057594000000001">
          <owner-list>
            <owner id="processA" mode="S" />
            <owner id="processB" mode="S" />
          </owner-list>
          <waiter-list>
            <waiter id="processA" mode="X" requestType="convert" />
            <waiter id="processB" mode="X" requestType="convert" />
          </waiter-list>
        </keylock>
      </resource-list>
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


class ConversionGraphContractTests(unittest.TestCase):
    def test_complete_same_key_s_to_x_cycle_passes(self) -> None:
        result = evaluate_conversion_graph(good_graph(), IDENTITY)
        self.assertEqual(result.verdict, Verdict.PASS)
        self.assertEqual(result.reasons, ())
        self.assertEqual(evaluate_conversion_graph(good_graph().encode("utf-8"), IDENTITY).verdict, Verdict.PASS)

    def test_missing_graph_or_identity_is_not_proven(self) -> None:
        self.assertEqual(evaluate_conversion_graph(None, IDENTITY).verdict, Verdict.NOT_PROVEN)
        self.assertEqual(evaluate_conversion_graph(good_graph(), None).verdict, Verdict.NOT_PROVEN)

    def test_wrong_root_or_malformed_xml_fails(self) -> None:
        for source in ("<event><deadlock /></event>", "<deadlock>", "<deadlock /> trailing"):
            with self.subTest(source=source):
                self.assertEqual(evaluate_conversion_graph(source, IDENTITY).verdict, Verdict.FAIL)

    def test_xml_declarations_and_oversize_inputs_fail_closed(self) -> None:
        self.assertEqual(
            evaluate_conversion_graph("<!DOCTYPE deadlock><deadlock />", IDENTITY).verdict,
            Verdict.FAIL,
        )
        self.assertEqual(
            evaluate_conversion_graph(" " * (MAX_GRAPH_BYTES + 1), IDENTITY).verdict,
            Verdict.FAIL,
        )
        self.assertEqual(
            evaluate_conversion_graph(b" " * (MAX_GRAPH_BYTES + 1), IDENTITY).verdict,
            Verdict.FAIL,
        )
        self.assertEqual(evaluate_conversion_graph(b"\xff", IDENTITY).verdict, Verdict.FAIL)

    def test_exact_two_processes_and_owned_database_are_required(self) -> None:
        too_many = change_graph(lambda root: root.find("process-list").append(ET.Element("process", id="extra", spid="53", currentdb="73")))
        wrong_db = change_graph(lambda root: root.find("process-list/process").set("currentdb", "74"))
        wrong_spid = change_graph(lambda root: root.find("process-list/process").set("spid", "99"))
        for source in (too_many, wrong_db, wrong_spid):
            with self.subTest(source=source):
                self.assertEqual(evaluate_conversion_graph(source, IDENTITY).verdict, Verdict.FAIL)

    def test_unique_victim_must_be_one_of_the_two_processes(self) -> None:
        unknown = change_graph(lambda root: root.find("victim-list/victimProcess").set("id", "foreign"))
        multiple = change_graph(lambda root: root.find("victim-list").append(ET.Element("victimProcess", id="processB")))
        for source in (unknown, multiple):
            with self.subTest(source=source):
                self.assertEqual(evaluate_conversion_graph(source, IDENTITY).verdict, Verdict.FAIL)

    def test_same_database_object_index_and_hobt_are_bound(self) -> None:
        mutations = (
            ("dbid", "74"),
            ("objectname", "other.lab.DeadlockRows"),
            ("indexname", "other_index"),
            ("hobtid", "72057594000000002"),
        )
        for name, value in mutations:
            with self.subTest(name=name):
                source = change_graph(lambda root: root.find("resource-list/keylock").set(name, value))
                self.assertEqual(evaluate_conversion_graph(source, IDENTITY).verdict, Verdict.FAIL)

    def test_both_processes_must_hold_shared_lock_on_same_key(self) -> None:
        missing_owner = change_graph(lambda root: root.find("resource-list/keylock/owner-list").remove(root.find("resource-list/keylock/owner-list/owner[@id='processB']")))
        wrong_owner_mode = change_graph(lambda root: root.find("resource-list/keylock/owner-list/owner[@id='processA']").set("mode", "U"))
        for source in (missing_owner, wrong_owner_mode):
            with self.subTest(source=source):
                self.assertEqual(evaluate_conversion_graph(source, IDENTITY).verdict, Verdict.FAIL)

    def test_both_processes_must_request_x_conversion_on_same_key(self) -> None:
        wrong_mode = change_graph(lambda root: root.find("resource-list/keylock/waiter-list/waiter[@id='processA']").set("mode", "S"))
        ordinary_wait = change_graph(lambda root: root.find("resource-list/keylock/waiter-list/waiter[@id='processA']").set("requestType", "wait"))
        missing_waiter = change_graph(lambda root: root.find("resource-list/keylock/waiter-list").remove(root.find("resource-list/keylock/waiter-list/waiter[@id='processB']")))
        for source in (wrong_mode, ordinary_wait, missing_waiter):
            with self.subTest(source=source):
                self.assertEqual(evaluate_conversion_graph(source, IDENTITY).verdict, Verdict.FAIL)

    def test_extra_matching_resource_and_duplicate_process_id_fail(self) -> None:
        duplicate_resource = change_graph(lambda root: root.find("resource-list").append(ET.fromstring(ET.tostring(root.find("resource-list/keylock"), encoding="unicode"))))
        duplicate_process = change_graph(lambda root: root.find("process-list/process[2]").set("id", "processA"))
        for source in (duplicate_resource, duplicate_process):
            with self.subTest(source=source):
                self.assertEqual(evaluate_conversion_graph(source, IDENTITY).verdict, Verdict.FAIL)

    def test_invalid_expected_identity_fails(self) -> None:
        invalid = replace(IDENTITY, actor_spids=(("ACTOR_A", 51), ("ACTOR_A", 52)))
        self.assertEqual(evaluate_conversion_graph(good_graph(), invalid).verdict, Verdict.FAIL)
        invalid = replace(IDENTITY, database_id=True)
        self.assertEqual(evaluate_conversion_graph(good_graph(), invalid).verdict, Verdict.FAIL)
        invalid = replace(IDENTITY, actor_spids=(([], 51), ("ACTOR_B", 52)))
        self.assertEqual(evaluate_conversion_graph(good_graph(), invalid).verdict, Verdict.FAIL)
        self.assertEqual(evaluate_conversion_graph("\ud800", IDENTITY).verdict, Verdict.FAIL)

    def test_complete_capture_binds_graph_window_victim_and_survivor(self) -> None:
        result = evaluate_conversion_capture(good_capture())
        self.assertEqual(result.verdict, Verdict.PASS)
        self.assertEqual(result.victim_spid, 51)
        self.assertEqual(evaluate_conversion_capture(None).verdict, Verdict.NOT_PROVEN)

    def test_missing_capture_fields_remain_not_proven(self) -> None:
        for changes in (
            {"observed_run_token": None},
            {"event_timestamp_utc": None},
            {"actor_outcomes": None},
            {"matching_event_count": None},
            {"graph_xml": None},
        ):
            with self.subTest(changes=changes):
                self.assertEqual(
                    evaluate_conversion_capture(replace(good_capture(), **changes)).verdict,
                    Verdict.NOT_PROVEN,
                )

    def test_event_source_database_run_and_actor_bindings_are_exact(self) -> None:
        for changes in (
            {"event_name": "lock_deadlock"},
            {"source_session": "other_session"},
            {"database_id": 74},
            {"observed_run_token": "OTHER"},
            {"actor_spids": (("ACTOR_A", 52), ("ACTOR_B", 51))},
            {"graph_identity": "not-an-identity"},
        ):
            with self.subTest(changes=changes):
                self.assertEqual(
                    evaluate_conversion_capture(replace(good_capture(), **changes)).verdict,
                    Verdict.FAIL,
                )

    def test_event_must_be_inside_a_valid_explicit_offset_run_window(self) -> None:
        for changes in (
            {"event_timestamp_utc": "2026-11-06T12:02:00Z"},
            {"run_started_utc": "2026-11-06T12:02:00Z"},
            {"run_finished_utc": "2026-11-06T11:00:00Z"},
            {"event_timestamp_utc": "2026-11-06T12:00:00"},
            {"event_timestamp_utc": "not-a-timestamp"},
        ):
            with self.subTest(changes=changes):
                self.assertEqual(
                    evaluate_conversion_capture(replace(good_capture(), **changes)).verdict,
                    Verdict.FAIL,
                )

    def test_rfc3339_timestamp_case_precision_and_boundary_values(self) -> None:
        lowercase = replace(
            good_capture(),
            event_timestamp_utc="2026-11-06t12:00:00.250z",
            run_started_utc="2026-11-06t11:59:00z",
            run_finished_utc="2026-11-06t12:01:00z",
        )
        self.assertEqual(evaluate_conversion_capture(lowercase).verdict, Verdict.PASS)

        equivalent_offsets = replace(
            good_capture(),
            event_timestamp_utc="2026-11-06T12:00:00.250+01:00",
            run_started_utc="2026-11-06T11:00:00.250Z",
            run_finished_utc="2026-11-06T11:00:00.250Z",
        )
        self.assertEqual(evaluate_conversion_capture(equivalent_offsets).verdict, Verdict.PASS)

        precise = replace(
            good_capture(),
            event_timestamp_utc="2026-11-06T12:00:00.2500001Z",
            run_started_utc="2026-11-06T12:00:00.2500001Z",
            run_finished_utc="2026-11-06T12:00:00.2500001Z",
        )
        self.assertEqual(evaluate_conversion_capture(precise).verdict, Verdict.PASS)
        self.assertEqual(
            evaluate_conversion_capture(replace(precise, run_finished_utc="2026-11-06T12:00:00.2500000Z")).verdict,
            Verdict.FAIL,
        )

        boundary = "0001-01-01T00:00:00+23:59"
        boundary_capture = replace(
            good_capture(),
            event_timestamp_utc=boundary,
            run_started_utc=boundary,
            run_finished_utc=boundary,
        )
        self.assertEqual(evaluate_conversion_capture(boundary_capture).verdict, Verdict.PASS)
        self.assertEqual(
            evaluate_conversion_capture(replace(
                good_capture(), event_timestamp_utc="2026-11-06T12:00:60Z"
            )).verdict,
            Verdict.FAIL,
        )

    def test_matching_event_count_is_exactly_one(self) -> None:
        self.assertEqual(
            evaluate_conversion_capture(replace(good_capture(), matching_event_count=0)).verdict,
            Verdict.NOT_PROVEN,
        )
        for count in (2, True, -1):
            with self.subTest(count=count):
                self.assertEqual(
                    evaluate_conversion_capture(replace(good_capture(), matching_event_count=count)).verdict,
                    Verdict.FAIL,
                )

    def test_actor_outcomes_must_match_graph_victim_and_successful_counterpart(self) -> None:
        good = good_capture()
        bad_outcomes = (
            (ActorOutcome("ACTOR_A", 51, "VICTIM", 1204), good.actor_outcomes[1]),
            (ActorOutcome("ACTOR_A", 51, "SURVIVOR", None), good.actor_outcomes[1]),
            (good.actor_outcomes[0], ActorOutcome("ACTOR_B", 52, "SURVIVOR", 1205)),
            (ActorOutcome("ACTOR_B", 52, "VICTIM", 1205), ActorOutcome("ACTOR_A", 51, "SURVIVOR", None)),
            (good.actor_outcomes[0], good.actor_outcomes[0]),
        )
        for outcomes in bad_outcomes:
            with self.subTest(outcomes=outcomes):
                self.assertEqual(
                    evaluate_conversion_capture(replace(good, actor_outcomes=outcomes)).verdict,
                    Verdict.FAIL,
                )

    def test_capture_failure_precedes_missing_evidence(self) -> None:
        result = evaluate_conversion_capture(replace(
            good_capture(), expected_run_token=None, observed_run_token=None,
            event_name="wrong_event", graph_xml=None,
        ))
        self.assertEqual(result.verdict, Verdict.FAIL)


if __name__ == "__main__":
    unittest.main()
