from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main

from verify_external_tables_apt_plan import (
    LOCK as LOCK_PATH, check_plan, parse_install_plan,
    select_role, verify_guest_state, verify_python_wheel,
)
from external_tables_package_state import installed_package_digest, parse_dpkg_status


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


def package(name, version, architecture="amd64", status="install ok installed"):
    return (
        f"Package: {name}\nStatus: {status}\nArchitecture: {architecture}\n"
        f"Version: {version}\nDescription: Synthetic package\n continuation text\n\n"
    ).encode()


class GuestPackageStateTests(TestCase):
    BASE = package("base", "1:1.0") + package("common", "1.0", "all")
    ROLE = {"packages": [
        {"package": "base", "architecture": "amd64", "previous_version": "1:1.0", "version": "1:2.0"},
        {"package": "client", "architecture": "amd64", "version": "3.0"},
    ]}
    GUEST = package("base", "1:2.0") + package("common", "1.0", "all") + package("client", "3.0")

    def verify(self, guest, base=BASE, lock=ROLE):
        return verify_guest_state(base, guest, sha256(self.BASE).hexdigest(), lock)

    def test_installed_state_must_match_pinned_base_and_exact_role_delta(self):
        self.assertEqual(self.verify(self.GUEST), 3)
        with self.assertRaisesRegex(ValueError, "pinned image"):
            self.verify(self.GUEST, base=self.BASE + b"\n")
        with self.assertRaisesRegex(ValueError, "locked transition"):
            self.verify(self.GUEST, lock={"packages": [dict(self.ROLE["packages"][0], previous_version="1:0.9")]})

    def test_fingerprint_uses_sorted_package_identity_and_version(self):
        expected = sha256(b"SQLPERF-EXTERNAL-DPKG-V1\nbase\tamd64\t1:2.0\nclient\tamd64\t3.0\ncommon\tall\t1.0\n").digest()
        reordered = package("client", "3.0") + package("common", "1.0", "all") + package("base", "1:2.0")
        self.assertEqual(installed_package_digest(reordered), expected)
        self.assertEqual(installed_package_digest(self.GUEST), expected)

    def test_rejects_missing_extra_or_changed_packages(self):
        for guest, condition in (
            (self.GUEST.replace(package("client", "3.0"), b""), "missing=1"),
            (self.GUEST + package("polybase", "1.0"), "extra=1"),
            (self.GUEST.replace(package("common", "1.0", "all"), package("common", "2.0", "all")), "changed=1"),
            (self.GUEST.replace(package("client", "3.0"), package("client", "3.0", "all")), "missing=1, extra=1"),
        ):
            with self.subTest(condition=condition), self.assertRaisesRegex(ValueError, condition):
                self.verify(guest)

    def test_rejects_unconfigured_duplicate_and_non_native_status(self):
        for sample in (
            package("base", "1.0", status="install ok unpacked"),
            package("base", "1.0", status="deinstall ok config-files"),
            package("base", "1.0", "i386"),
            package("base", "1.0") * 2,
            package("base", "1.0").replace(b"Version: 1.0", b"Version: 0.9\nVersion: 1.0"),
            package("base", "1.0").replace(b"Architecture: amd64\n", b""),
        ):
            with self.subTest(sample=sample), self.assertRaises(ValueError):
                parse_dpkg_status(sample)

    def test_role_selection_rejects_duplicate_package_transitions(self):
        lock = {"roles": {"query": ["base"]}, "packages": [self.ROLE["packages"][0]] * 2}
        with self.assertRaisesRegex(ValueError, "duplicate or unknown"):
            select_role(lock, "query")



if __name__ == "__main__":
    main()
