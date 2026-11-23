from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main

from verify_external_tables_apt_plan import (
    LOCK as LOCK_PATH, check_plan, parse_install_plan, select_role, verify_python_wheel,
)


PLAN = """Reading package lists...
Inst a:amd64 [1:1.0] (1:2.0 Ubuntu:24.04/noble-updates [amd64])
Inst b (2.0 /tmp/file.deb [amd64])
Conf b (2.0 /tmp/file.deb [amd64])
"""
LOCK = {"packages": [
    {"package": "a", "previous_version": "1:1.0", "version": "1:2.0"},
    {"package": "b", "version": "2.0"},
]}


class AptPlanTests(TestCase):
    def test_binds_native_new_packages_and_version_transitions(self):
        self.assertEqual(parse_install_plan(PLAN), {"a": ("1:1.0", "1:2.0"), "b": (None, "2.0")})
        self.assertEqual(check_plan(PLAN, LOCK), 2)

    def test_rejects_removals_and_ambiguous_installation(self):
        for plan in (PLAN + "Remv c [0]\n", PLAN + "Purg d\n", PLAN + "Inst b (2.0 [amd64])\n",
                     PLAN.replace("a:amd64", "a:i386"), PLAN.replace("(2.0 /tmp/file.deb", "broken")):
            with self.subTest(plan=plan), self.assertRaises(ValueError):
                check_plan(plan, LOCK)

    def test_rejects_candidate_drift_and_duplicate_lock(self):
        with self.assertRaises(ValueError):
            check_plan(PLAN.replace("1:2.0", "1:2.1"), LOCK)
        with self.assertRaises(ValueError):
            check_plan(PLAN, {"packages": LOCK["packages"] * 2})

    def test_query_and_source_roles_only_accept_their_own_packages(self):
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        query = select_role(lock, "query")
        source = select_role(lock, "source")
        query_names = {entry["package"] for entry in query["packages"]}
        source_names = {entry["package"] for entry in source["packages"]}
        self.assertEqual(query_names - source_names, {
            "libltdl7", "libodbc2", "libodbcinst2", "msodbcsql18", "mssql-server-polybase",
            "odbcinst", "unixodbc", "unixodbc-common",
        })
        self.assertIn("python_wheel", query)
        self.assertNotIn("python_wheel", source)
        self.assertFalse(source_names - query_names)
        self.assertIn("mssql-server", source_names)
        solver = "\n".join(f"Inst {row['package']} ({row['version']} [amd64])" for row in source["packages"])
        self.assertEqual(check_plan(solver, source), 13)
        with self.assertRaises(ValueError):
            check_plan(solver, query)

    def test_wheel_checks_name_size_and_digest_and_requires_query_role(self):
        data = b"synthetic wheel bytes"
        entry = {"filename": "fixture.whl", "size": len(data), "sha256": sha256(data).hexdigest()}
        lock = {"python_wheel": entry}
        with TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.whl"
            path.write_bytes(data)
            verify_python_wheel(path, lock)
            with self.assertRaisesRegex(ValueError, "only part of the query role"):
                verify_python_wheel(path, {"packages": []})
            with self.assertRaisesRegex(ValueError, "differs"):
                verify_python_wheel(path.with_name("wrong.whl"), lock)
            path.write_bytes(b"x" * len(data))
            with self.assertRaisesRegex(ValueError, "differs"):
                verify_python_wheel(path, lock)
            path.write_bytes(data + b"x")
            with self.assertRaisesRegex(ValueError, "differs"):
                verify_python_wheel(path, lock)


if __name__ == "__main__":
    main()
