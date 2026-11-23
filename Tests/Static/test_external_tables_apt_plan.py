from __future__ import annotations

from unittest import TestCase, main

from verify_external_tables_apt_plan import check_plan, parse_install_plan


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


if __name__ == "__main__":
    main()
