#!/usr/bin/env python3
"""Statische Regressionen für die QRY-006-Eigentumsprüfung; keine SQL-Ausführung."""
from __future__ import annotations

import unittest

from validate_qry006_null_semantics_design import DEMO, ownership_findings, read


class OwnershipGuardTests(unittest.TestCase):
    def test_current_guards(self) -> None:
        for script in ("10_Setup.sql", "90_Cleanup.sql"):
            with self.subTest(script=script):
                self.assertEqual([], ownership_findings(read(DEMO / script), script))

    def test_rejects_unsafe_mutations(self) -> None:
        for script in ("10_Setup.sql", "90_Cleanup.sql"):
            sql = read(DEMO / script)
            mutations = {
                "NULL-Vergleichslücke": sql.replace("@Project IS NULL OR ", ""),
                "fehlender Run-Marker": sql.replace("@ExistingRun IS NULL OR ", ""),
                "gekürzter Property-Wert": sql.replace("CONVERT(nvarchar(max), value)", "CONVERT(nvarchar(7), value)"),
                "gekürzte OUTPUT-Bindung": sql.replace("@DemoOut nvarchar(max) OUTPUT", "@DemoOut varchar(7) OUTPUT"),
                "gekürzte lokale Variable": sql.replace("@ExistingRun nvarchar(max)", "@ExistingRun varchar(20)"),
                "abweichende Schreibweise": sql.replace(" COLLATE Latin1_General_100_BIN2", ""),
                "angehängte Leerzeichen": sql.replace("OR DATALENGTH(@Contract) <> DATALENGTH(N'1.0')", ""),
            }
            for label, mutated in mutations.items():
                with self.subTest(script=script, mutation=label):
                    self.assertNotEqual(sql, mutated)
                    self.assertTrue(ownership_findings(mutated, script))


if __name__ == "__main__":
    unittest.main()
