"""Synthetic counterexamples for the CON-006 range graph checker."""
from __future__ import annotations

import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from Tests.Static.con006_conversion_graph_contract import GraphIdentity, Verdict  # noqa: E402
from Tests.Static.con006_range_graph_contract import evaluate_range_graph  # noqa: E402


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
      <resource-list><keylock dbid="73"
        objectname="SQLPERF_LAB_CON006_RUN.lab.DeadlockRows"
        indexname="PK_DeadlockRows" hobtid="72057594000000001">
        <owner-list>
          <owner id="processA" mode="RangeS-S" />
          <owner id="processB" mode="RangeS-S" />
        </owner-list>
        <waiter-list>
          <waiter id="processA" mode="RangeI-N" requestType="wait" />
          <waiter id="processB" mode="RangeI-N" requestType="wait" />
        </waiter-list>
      </keylock></resource-list>
    </deadlock>"""


def change_graph(mutator) -> str:
    root = ET.fromstring(good_graph())
    mutator(root)
    return ET.tostring(root, encoding="unicode")


class RangeGraphContractTests(unittest.TestCase):
    def test_complete_same_key_two_actor_graph_passes_without_lock_mode_assumption(self):
        result = evaluate_range_graph(good_graph(), IDENTITY)
        self.assertEqual(result.verdict, Verdict.PASS)
        self.assertEqual(result.victim_spid, 51)

    def test_checker_preserves_observed_modes_instead_of_fixing_a_range_pair(self):
        def mutate(root):
            modes = (
                ("owner-list/owner[@id='processA']", "U"),
                ("owner-list/owner[@id='processB']", "S"),
                ("waiter-list/waiter[@id='processA']", "X"),
                ("waiter-list/waiter[@id='processB']", "RangeI-N"),
            )
            for path, mode in modes:
                root.find("resource-list/keylock/" + path).set("mode", mode)
            root.find("resource-list/keylock/waiter-list/waiter[@id='processA']").set(
                "requestType", "convert")

        source = change_graph(mutate)
        self.assertEqual(evaluate_range_graph(source, IDENTITY).verdict, Verdict.PASS)

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

    def test_requires_exactly_the_supplied_key_resource(self):
        for name, value in (("dbid", "74"), ("indexname", "other"),
                            ("hobtid", "72057594000000002")):
            source = change_graph(lambda root: root.find("resource-list/keylock").set(name, value))
            with self.subTest(name=name):
                self.assertEqual(evaluate_range_graph(source, IDENTITY).verdict, Verdict.FAIL)
        duplicate = change_graph(lambda root: root.find("resource-list").append(
            ET.fromstring(ET.tostring(root.find("resource-list/keylock"), encoding="unicode"))))
        self.assertEqual(evaluate_range_graph(duplicate, IDENTITY).verdict, Verdict.FAIL)

    def test_both_actors_must_own_and_wait_on_the_same_key(self):
        missing_owner = change_graph(lambda root: root.find(
            "resource-list/keylock/owner-list").remove(root.find(
                "resource-list/keylock/owner-list/owner[@id='processB']")))
        foreign_waiter = change_graph(lambda root: root.find(
            "resource-list/keylock/waiter-list/waiter[@id='processB']").set("id", "foreign"))
        for source in (missing_owner, foreign_waiter):
            with self.subTest(source=source):
                self.assertEqual(evaluate_range_graph(source, IDENTITY).verdict, Verdict.FAIL)

    def test_actual_lock_mode_and_request_type_fields_are_required(self):
        missing_mode = change_graph(lambda root: root.find(
            "resource-list/keylock/waiter-list/waiter[@id='processA']").attrib.pop("mode"))
        missing_request = change_graph(lambda root: root.find(
            "resource-list/keylock/waiter-list/waiter[@id='processA']").attrib.pop("requestType"))
        self.assertEqual(evaluate_range_graph(missing_mode, IDENTITY).verdict, Verdict.FAIL)
        self.assertEqual(evaluate_range_graph(missing_request, IDENTITY).verdict, Verdict.FAIL)

    def test_unsafe_or_malformed_xml_fails(self):
        for source in ("<!DOCTYPE deadlock><deadlock />", "<deadlock", b"\xff",
                       "<deadlock />" * 20_000):
            with self.subTest(source=source[:32]):
                self.assertEqual(evaluate_range_graph(source, IDENTITY).verdict, Verdict.FAIL)


if __name__ == "__main__":
    unittest.main()
