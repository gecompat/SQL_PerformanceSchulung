#!/usr/bin/env python3
"""Prüft ausschließlich DGN-007-Compatibility-Guards und Kontextprojektion.

SQLite wertet die extrahierten Katalogabfragen und NULL-Prädikate aus. Optional
laufen dieselben Guard-Batches mit lesenden T-SQL-Fixtures sowie die extrahierte
Kontextprojektion mit festen Query-Store-Options-Fixtures und echtem Compatibility-
Katalogwert aus master einer ausdrücklich bestätigten leeren Developer-
Wegwerfinstanz mit SQL Server 2025. Kein vollständiger Context-/Observationlauf,
Teilnehmer- oder Incidentnachweis.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import re
import sqlite3
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
OBSERVATION = ROOT / "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/40_Observation.sql"
ADAPTER = ROOT / "Scenarios/DGN-007/adapter/sql/validate.sql"
VARIABLE = "@ActualCompatibility"
PREDICATE = "@ActualCompatibility IS NULL OR @ActualCompatibility<>170"
BEGIN = "/* DGN007_COMPATIBILITY_GUARD_BEGIN */"
END = "/* DGN007_COMPATIBILITY_GUARD_END */"
TARGET = "SQLPERF_SYNTH_TARGET"
SOURCES = (OBSERVATION, ADAPTER)


class ContractError(ValueError):
    """Datenschutzneutraler Vertragsfehler ohne SQL-Rohoutput."""


@dataclass(frozen=True)
class CompatibilityContract:
    guard: str
    lookup: str
    predicate: str
    error_number: int


def uncomment(sql: str) -> str:
    return re.sub(r"N?'(?:''|[^'])*'|/\*.*?\*/|--[^\n]*",
                  lambda match: " " if match[0].startswith(("/*", "--")) else match[0],
                  sql, flags=re.DOTALL)


def extract_contract(sql: str, path: Path) -> CompatibilityContract:
    """Nur den vereinbarten lesenden Katalog-/Guard-Schnitt akzeptieren."""
    if sql.count(BEGIN) != 1 or sql.count(END) != 1:
        raise ContractError("FAIL_COMPATIBILITY_CONTRACT")
    block = sql.split(BEGIN, 1)[1].split(END, 1)[0].strip()
    selector = "database_id=DB_ID()" if path == OBSERVATION else "name=@TargetDatabase"
    lookup = f"SELECT compatibility_level FROM sys.databases WHERE {selector}"
    error_number = 51000 if path == OBSERVATION else 51002
    message = ("FAIL_CONTRACT: Compatibility Level 170 fehlt." if path == OBSERVATION
               else "PROJECT_ASSERTION_FAILED: Compatibility Level 170 fehlt.")
    pattern = (rf"DECLARE\s+{VARIABLE}\s+int\s*=\s*\(\s*(?P<lookup>{re.escape(lookup)})\s*\)\s*;\s*"
               rf"IF\s+(?P<predicate>{re.escape(PREDICATE)})\s+"
               rf"THROW\s+{error_number}\s*,\s*'{re.escape(message)}'\s*,\s*1\s*;")
    match = re.fullmatch(pattern, uncomment(block))
    if match is None:
        raise ContractError("FAIL_COMPATIBILITY_CONTRACT")
    code = uncomment(sql)
    guard_end = code.find(match[0]) + len(match[0])
    if path == OBSERVATION:
        evidence = re.search(r"\bSELECT\s+\d+\s+AS\s+EvidenceLevel\b", code)
    else:
        evidence = re.search(r"SET\s+@Sql=N'SELECT\s+@QsState=", code)
    if evidence is None or guard_end > evidence.start():
        raise ContractError("FAIL_GUARD_ORDER")
    if "DATABASEPROPERTYEX" in code.upper():
        raise ContractError("FAIL_COMPATIBILITY_PROPERTY")
    return CompatibilityContract(block, match["lookup"], match["predicate"], error_number)


def context_statement(sql: str) -> str:
    code = uncomment(sql)
    match = re.search(r"SELECT 3 AS EvidenceLevel,\s*N'CONTEXT' AS EvidenceScope,\s*"
                      r"@ActualCompatibility AS CompatibilityLevel,\s*"
                      r"o\.actual_state_desc AS QueryStoreState,\s*o\.query_capture_mode_desc AS CaptureMode\s*"
                      r"FROM sys\.database_query_store_options AS o;", code)
    if match is None:
        raise ContractError("FAIL_CONTEXT_PROJECTION")
    return match[0]


def load_contracts() -> dict[Path, CompatibilityContract]:
    return {path: extract_contract(path.read_text(encoding="utf-8"), path) for path in SOURCES}


class CompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contracts = load_contracts()
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        self.connection.create_function("DB_ID", 0, lambda: 7)
        self.connection.execute("CREATE TABLE databases(database_id INT, name TEXT, compatibility_level INT)")

    def rejected(self, path: Path, rows: tuple[tuple[int, str, int | None], ...]) -> bool:
        self.connection.execute("DELETE FROM databases")
        self.connection.executemany("INSERT INTO databases VALUES(?,?,?)", rows)
        contract = self.contracts[path]
        actual = self.connection.execute("SELECT (" + contract.lookup.replace("sys.databases", "databases") + ")",
                                         {"TargetDatabase": TARGET}).fetchone()[0]
        return bool(self.connection.execute("SELECT CASE WHEN " + contract.predicate + " THEN 1 ELSE 0 END",
                                            {"ActualCompatibility": actual}).fetchone()[0])

    def test_170_passes_and_other_database_does_not_override_target(self) -> None:
        for path in SOURCES:
            with self.subTest(source=path.name):
                self.assertFalse(self.rejected(path, ((8, "SQLPERF_SYNTH_OTHER", 160), (7, TARGET, 170))))

    def test_160_is_rejected_even_with_unrelated_170_row(self) -> None:
        for path in SOURCES:
            with self.subTest(source=path.name):
                self.assertTrue(self.rejected(path, ((8, "SQLPERF_SYNTH_OTHER", 170), (7, TARGET, 160))))

    def test_null_is_rejected(self) -> None:
        for path in SOURCES:
            with self.subTest(source=path.name):
                self.assertTrue(self.rejected(path, ((7, TARGET, None),)))

    def test_missing_catalog_row_is_rejected(self) -> None:
        for path in SOURCES:
            with self.subTest(source=path.name):
                self.assertTrue(self.rejected(path, ()))

    def test_wrong_database_cannot_supply_compatibility(self) -> None:
        for path in SOURCES:
            with self.subTest(source=path.name):
                self.assertTrue(self.rejected(path, ((8, "SQLPERF_SYNTH_OTHER", 170),)))

    def test_exact_lookup_and_null_guard_negative_controls(self) -> None:
        for path, contract in self.contracts.items():
            sql = path.read_text(encoding="utf-8")
            for old, new in ((contract.lookup, "SELECT 170"),
                             (PREDICATE, "@ActualCompatibility<>170"),
                             (PREDICATE, "@ActualCompatibility IS NULL OR @ActualCompatibility<>160")):
                with self.subTest(source=path.name, mutation=old):
                    self.assertNotEqual(sql.replace(old, new, 1), sql)
                    with self.assertRaises(ContractError):
                        extract_contract(sql.replace(old, new, 1), path)

    def test_guard_must_precede_any_evidence(self) -> None:
        for path in SOURCES:
            sql = path.read_text(encoding="utf-8")
            injected = ("SELECT 1 AS EvidenceLevel;\n" if path == OBSERVATION else "SET @Sql=N'SELECT @QsState=1';\n")
            with self.subTest(source=path.name), self.assertRaises(ContractError):
                extract_contract(injected + sql, path)

    def test_context_projects_same_guarded_catalog_value(self) -> None:
        sql = OBSERVATION.read_text(encoding="utf-8")
        self.assertIn(VARIABLE + " AS CompatibilityLevel", context_statement(sql))
        for replacement in ("170 AS CompatibilityLevel", "NULL AS CompatibilityLevel",
                            "DATABASEPROPERTYEX(DB_NAME(),N'CompatibilityLevel') AS CompatibilityLevel"):
            with self.subTest(replacement=replacement), self.assertRaises(ContractError):
                context_statement(sql.replace(VARIABLE + " AS CompatibilityLevel", replacement, 1))


def fixture_batch(contract: CompatibilityContract, source: str, case: str, value: int | None, present: bool) -> str:
    """Reale Guard-Syntax auf VALUES-Katalog; keine Datenbank-/Settingmutation."""
    catalog_value = "NULL" if value is None else str(value)
    fixture_name = TARGET if present else "SQLPERF_SYNTH_OTHER"
    fixture_id = 7 if present else 8
    catalog = (f"(VALUES({fixture_id},N'{fixture_name}',CAST({catalog_value} AS int))) "
               "AS fixture(database_id,name,compatibility_level)")
    guard = contract.guard.replace("sys.databases", catalog).replace("DB_ID()", "7")
    return (f"SET NOCOUNT ON; DECLARE @TargetDatabase sysname=N'{TARGET}';\nBEGIN TRY\n{guard}\n"
            f"SELECT 'DGN007_COMPATIBILITY_FIXTURE|{source}|{case}|ACCEPT';\nEND TRY\nBEGIN CATCH\n"
            f"IF ERROR_NUMBER()<>{contract.error_number} THROW;\n"
            f"SELECT 'DGN007_COMPATIBILITY_FIXTURE|{source}|{case}|REJECT';\nEND CATCH;\n")


def runtime_checks(container: str) -> None:
    sys.path.insert(0, str(ROOT / "Tests/Runtime"))
    from run_dgn007_automated_setup import assert_absent, assert_empty_instance, resolve_target
    import execution_target

    target = resolve_target(container)
    execution_target.verify_engine(target, expected_major=17)
    assert_empty_instance(target)
    assert_absent(target)
    contracts = load_contracts()
    batches, expected = [], []
    for path, contract in contracts.items():
        source = "OBSERVATION" if path == OBSERVATION else "ADAPTER"
        for case, value, present, outcome in (("170", 170, True, "ACCEPT"), ("160", 160, True, "REJECT"),
                                              ("NULL", None, True, "REJECT"), ("MISSING", 170, False, "REJECT")):
            batches.append(fixture_batch(contract, source, case, value, present))
            expected.append(f"DGN007_COMPATIBILITY_FIXTURE|{source}|{case}|{outcome}")
    output = execution_target.run_sql(target, database="master", sql_text="\nGO\n".join(batches), timeout_seconds=30)
    if output.strip().splitlines() != expected:
        raise ContractError("FAIL_TSQL_FIXTURES")
    # Zusätzlich echte fehlende Zielzeile im Systemkatalog; kein Fixture ersetzt sie.
    adapter = contracts[ADAPTER]
    missing_batch = ("SET NOCOUNT ON; DECLARE @TargetDatabase sysname=N'SQLPERF_SYNTH_MISSING'; "
                     "IF DB_ID(@TargetDatabase) IS NOT NULL THROW 51001,'FAIL_SAFETY',1; "
                     f"BEGIN TRY {adapter.guard} THROW 51001,'FAIL_MISSING_CATALOG',1; END TRY BEGIN CATCH "
                     f"IF ERROR_NUMBER()<>{adapter.error_number} THROW; SELECT N'MISSING_REJECTED'; END CATCH;")
    output = execution_target.run_sql(target, database="master", sql_text=missing_batch, timeout_seconds=30)
    if output.strip() != "MISSING_REJECTED":
        raise ContractError("FAIL_MISSING_CATALOG")
    observation = contracts[OBSERVATION]
    context = context_statement(OBSERVATION.read_text(encoding="utf-8"))
    # master kann keine QS-Optionszeile liefern. Nur diese Quelle wird durch
    # feste skalare OFF/ALL-Fixtures ersetzt; Compatibility bleibt echter Katalog.
    context = context.replace("sys.database_query_store_options AS o",
                              "(VALUES(N'OFF',N'ALL')) AS o(actual_state_desc,query_capture_mode_desc)")
    output = execution_target.run_sql(
        target, database="master", timeout_seconds=30,
        sql_text=f"SET NOCOUNT ON; DECLARE {VARIABLE} int=({observation.lookup}); {context} "
                 "SELECT N'CATALOG',compatibility_level FROM sys.databases WHERE database_id=DB_ID();")
    rows = [line.strip().split("|") for line in output.strip().splitlines()]
    if (len(rows) != 2 or len(rows[0]) != 5 or rows[0][:2] != ["3", "CONTEXT"]
            or len(rows[1]) != 2 or rows[1][0] != "CATALOG" or not rows[1][1].isdigit()
            or rows[0][2] != rows[1][1] or rows[0][3:] != ["OFF", "ALL"]):
        raise ContractError("FAIL_CONTEXT_CATALOG")
    assert_empty_instance(target)
    assert_absent(target)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container", help="Explizites leeres Docker-Ziel mit SQL Server 2025 Developer.")
    parser.add_argument("--confirm-disposable-instance", action="store_true")
    args = parser.parse_args(argv)
    if args.container is not None and (not args.confirm_disposable_instance or not os.environ.get("SQLCMDPASSWORD")
                                      or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", args.container)):
        print("DGN007_COMPATIBILITY|FAIL|FAIL_SAFETY")
        return 1
    result = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(CompatibilityTests))
    if not result.wasSuccessful():
        return 1
    if args.container is not None:
        try:
            runtime_checks(args.container)
        except (Exception, KeyboardInterrupt):
            # Kein Exceptiontext und kein sqlcmd-Rohoutput gelangen in CI-Logs.
            print("DGN007_COMPATIBILITY|FAIL|FAIL_READ_ONLY_CHECK")
            return 1
        print("DGN007_COMPATIBILITY|PASS|OK|scope=guard-and-context-fixtures-with-master-catalog; major=17")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
