"""Quellen- und Textgegenproben für das DGN-004-Source-Only-Paar."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
PAIR_DIR = ROOT / "Tests" / "Fixtures" / "DGN004_SourcePair"
REGISTRY = ROOT / ".ai" / "identity" / "registry.json"
ROLES = ("R", "H")
FILES = {"R": "ReplayReference.sql", "H": "ReplayHintControl.sql"}
HINT = "OPTION (USE HINT ('DISABLE_OPTIMIZED_PLAN_FORCING'))"
MODULE_NAMES = {"R": "[dgn004].[ReplayReference]", "H": "[dgn004].[ReplayHintControl]"}
PROJECTIONS = (
    "o.[OrderId] AS [OrderId]",
    "l.[LineId] AS [LineId]",
    "c.[CustomerValue] AS [CustomerValue]",
    "ca.[CategoryValue] AS [CategoryValue]",
    "ct.[ContactValue] AS [ContactValue]",
    "ci.[CityValue] AS [CityValue]",
    "rg.[RegionValue] AS [RegionValue]",
    "co.[CountryValue] AS [CountryValue]",
    "i.[ItemValue] AS [ItemValue]",
    "ig.[GroupNo] AS [GroupNo]",
)
JOINS = (
    ("[dgn004].[Customers] AS c", "c.[CustomerId] = o.[CustomerId]"),
    ("[dgn004].[Categories] AS ca", "ca.[CategoryId] = c.[CategoryId]"),
    ("[dgn004].[Contacts] AS ct", "ct.[ContactId] = o.[ContactId]"),
    ("[dgn004].[Cities] AS ci", "ci.[CityId] = c.[CityId]"),
    ("[dgn004].[Regions] AS rg", "rg.[RegionId] = ci.[RegionId]"),
    ("[dgn004].[Countries] AS co", "co.[CountryId] = rg.[CountryId]"),
    ("[dgn004].[OrderLines] AS l", "l.[OrderId] = o.[OrderId]"),
    ("[dgn004].[Items] AS i", "i.[ItemId] = l.[ItemId]"),
    ("[dgn004].[ItemGroups] AS ig", "ig.[ItemId] = i.[ItemId]"),
)
BASE_TABLE = "[dgn004].[Orders] AS o"
ORDER = "ORDER BY [OrderId], [LineId], [GroupNo]"


def registry_plan() -> dict:
    document = json.loads(REGISTRY.read_text(encoding="utf-8"))
    candidate = next(
        item for item in document["artifacts"]["TSK-016"]["candidates"]
        if item["target"] == "DGN-004"
    )
    if candidate.get("active_plan") != "classical_forcing_hint_control_plan":
        raise ValueError("Der aktive DGN-004-Plan hat sich geändert.")
    return candidate["rh_source_text_plan"]


def expected_statement() -> str:
    branch = "SELECT " + ", ".join(PROJECTIONS) + " FROM " + BASE_TABLE
    for table, predicate in JOINS:
        branch += f" INNER JOIN {table} ON {predicate}"
    return f"{branch} UNION ALL {branch} {ORDER};"


def validate_pair(sources: dict[str, bytes], plan: dict | None = None) -> dict[str, str]:
    """Prüft vollständige M-Bytes und die begrenzte M/S/T-Paarung ohne SQL."""
    plan = plan or registry_plan()
    entries = {entry["role"]: entry for entry in plan["module_sources"]}
    if set(sources) != set(ROLES) or set(entries) != set(ROLES):
        raise ValueError("R- und H-Quelle müssen jeweils genau einmal vorliegen.")
    module_names = {role: entries[role].get("module_name") for role in ROLES}
    if module_names != MODULE_NAMES or len(set(module_names.values())) != len(ROLES):
        raise ValueError("R/H-Rollenidentität verletzt: Modulnamen müssen eindeutig R=ReplayReference und H=ReplayHintControl zuordnen.")

    statements: dict[str, str] = {}
    for role in ROLES:
        expected = entries[role]
        raw = sources[role]
        text = raw.decode("ascii", errors="strict")
        if not raw or raw.startswith(b"\xef\xbb\xbf") or any(c in raw for c in (b"\r", b"\n", b"\t")):
            raise ValueError(f"{role}: Quelle muss eine BOM- und zeilenumbruchfreie ASCII-Zeile sein.")
        prefix = f"CREATE PROCEDURE {expected['module_name']} AS "
        start = expected["statement_start_utf16_bytes"]
        if start != len(prefix.encode("utf-16le")) or not text.startswith(prefix):
            raise ValueError(f"{role}: Modulname oder Nutzstatementoffset stimmt nicht.")
        body = text[len(prefix) :]
        if role == "R" and body != expected_statement():
            raise ValueError("R: Projektionen, Tabellen/JOINs, UNION ALL oder Sortierung weichen ab.")
        if role == "H" and body != expected_statement()[:-1] + " " + HINT + ";":
            raise ValueError("H: einzig zulässiger Unterschied ist der terminale feste Hint.")
        if text != expected["module_source"]:
            raise ValueError(f"{role}: vollständiger Quelltext weicht von der registrierten Vorlage ab.")
        encoded = text.encode("utf-16le")
        if len(encoded) != expected["module_utf16_bytes"]:
            raise ValueError(f"{role}: Modulbytezahl stimmt nicht.")
        if hashlib.sha256(encoded).hexdigest() != expected["module_sha256_utf16le"]:
            raise ValueError(f"{role}: Modulprüfsumme stimmt nicht.")
        size = expected["statement_utf16_bytes"]
        if start < 0 or size < 2 or start % 2 or size % 2 or start + size != len(encoded):
            raise ValueError(f"{role}: M/S/T-Bytegrenzen sind ungültig.")
        statement = encoded[start : start + size].decode("utf-16le", errors="strict")
        if hashlib.sha256(statement.encode("utf-16le")).hexdigest() != expected["statement_sha256_utf16le"]:
            raise ValueError(f"{role}: Statementprüfsumme stimmt nicht.")
        if hashlib.sha256(statement[:-1].encode("utf-16le")).hexdigest() != expected["without_terminator_sha256_utf16le"]:
            raise ValueError(f"{role}: T-Darstellung stimmt nicht.")
        statements[role] = statement

    r_statement = statements["R"]
    if HINT in r_statement or statements["H"].count(HINT) != 1:
        raise ValueError("Hint fehlt, ist doppelt oder steht in R.")
    return statements


def load_sources() -> dict[str, bytes]:
    return {role: (PAIR_DIR / FILES[role]).read_bytes() for role in ROLES}


class Dgn004SourcePairTests(unittest.TestCase):
    def test_registered_module_bytes_and_pair_contract(self):
        plan = registry_plan()
        entries = {entry["role"]: entry for entry in plan["module_sources"]}
        sources = load_sources()
        statements = validate_pair(sources, plan)
        self.assertEqual(set(ROLES), set(statements))
        self.assertTrue(all(sources[role] == entries[role]["module_source"].encode("ascii") for role in ROLES))
        self.assertEqual(10, len(PROJECTIONS))
        self.assertEqual(9, len(JOINS))
        self.assertEqual(2, statements["R"].count("SELECT "))
        self.assertEqual(1, statements["R"].count("UNION ALL"))

    def test_source_text_mutations_are_rejected(self):
        good = load_sources()
        mutations = (
            ("module", "R", lambda text: text.replace("ReplayReference", "ReplayWrong", 1)),
            ("schema", "R", lambda text: text.replace("[dgn004].[Orders]", "[other].[Orders]", 1)),
            ("type", "R", lambda text: text.replace("o.[OrderId] AS [OrderId]", "CONVERT(bigint, o.[OrderId]) AS [OrderId]", 1)),
            ("projection", "R", lambda text: text.replace(", ig.[GroupNo] AS [GroupNo]", "", 1)),
            ("missing hint", "H", lambda text: text.replace(" OPTION (USE HINT ('DISABLE_OPTIMIZED_PLAN_FORCING'))", "", 1)),
            ("duplicate hint", "H", lambda text: text.replace(" OPTION (USE HINT ('DISABLE_OPTIMIZED_PLAN_FORCING'))", " OPTION (USE HINT ('DISABLE_OPTIMIZED_PLAN_FORCING')) OPTION (USE HINT ('DISABLE_OPTIMIZED_PLAN_FORCING'))", 1)),
            ("hint position", "H", lambda text: text.replace("SELECT o.[OrderId]", "SELECT o.[OrderId] OPTION (USE HINT ('DISABLE_OPTIMIZED_PLAN_FORCING'))", 1)),
            ("extra statement", "R", lambda text: text + "; SELECT 1"),
            ("line ending", "R", lambda text: text.replace(" AS ", " AS\r\n", 1)),
            ("BOM", "H", lambda text: "\ufeff" + text),
        )
        plan = registry_plan()
        for label, role, mutate in mutations:
            with self.subTest(label=label):
                changed = dict(good)
                changed[role] = mutate(good[role].decode("ascii")).encode("utf-8")
                with self.assertRaises((ValueError, UnicodeDecodeError)):
                    validate_pair(changed, plan)

    def test_registry_role_identity_is_rejected_before_source_hash_checks(self):
        sources = load_sources()
        original = registry_plan()
        mutations = (
            ("duplicate module name", {"R": MODULE_NAMES["R"], "H": MODULE_NAMES["R"]}),
            ("swapped module names", {"R": MODULE_NAMES["H"], "H": MODULE_NAMES["R"]}),
        )
        for label, names in mutations:
            with self.subTest(label=label):
                changed = copy.deepcopy(original)
                by_role = {entry["role"]: entry for entry in changed["module_sources"]}
                for role, name in names.items():
                    by_role[role]["module_name"] = name
                with self.assertRaisesRegex(ValueError, "R/H-Rollenidentität verletzt"):
                    validate_pair(sources, changed)

    def test_mst_offset_mutations_are_rejected(self):
        good = load_sources()
        plan = registry_plan()
        for role_index, role in enumerate(ROLES):
            for label, field, delta in (
                ("start odd", "statement_start_utf16_bytes", 1),
                ("start wrong", "statement_start_utf16_bytes", 2),
                ("statement truncated", "statement_utf16_bytes", -2),
                ("statement past end", "statement_utf16_bytes", 2),
            ):
                with self.subTest(role=role, label=label):
                    changed = copy.deepcopy(plan)
                    changed["module_sources"][role_index][field] += delta
                    with self.assertRaises(ValueError):
                        validate_pair(good, changed)


if __name__ == "__main__":
    unittest.main()
