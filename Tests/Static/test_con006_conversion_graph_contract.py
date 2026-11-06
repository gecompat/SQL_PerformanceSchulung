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
    GraphIdentity,
    Verdict,
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


if __name__ == "__main__":
    unittest.main()
