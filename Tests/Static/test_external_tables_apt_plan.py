from __future__ import annotations

import json
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import patch
from zipfile import ZipFile

from verify_external_tables_apt_plan import (
    LOCK as LOCK_PATH, check_plan,
    select_role, verify_guest_state, verify_python_wheel,
)
from external_tables_guest_apt import apt_install_command, install_verified_guest_packages, parse_install_plan
from external_tables_odbc import read_pinned_pyodbc_wheel, stage_pinned_pyodbc
from external_tables_pilot_sql import Role
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
        self.assertEqual(query_names - source_names, {"mssql-server-polybase"})
        self.assertEqual(query["python_wheel"], source["python_wheel"])
        self.assertFalse(source_names - query_names)
        self.assertIn("mssql-server", source_names)
        solver = "\n".join(f"Inst {row['package']} ({row['version']} [amd64])" for row in source["packages"])
        self.assertEqual(check_plan(solver, source), 20)
        with self.assertRaises(ValueError):
            check_plan(solver, query)

    def test_wheel_checks_name_size_and_digest_and_requires_a_role_lock(self):
        binary = b"synthetic extension bytes"
        filename = "pyodbc.cpython-312-x86_64-linux-gnu.so"
        buffer = BytesIO()
        with ZipFile(buffer, "w") as archive:
            archive.writestr(filename, binary)
        data = buffer.getvalue()
        extension = {"filename": filename, "size": len(binary), "sha256": sha256(binary).hexdigest()}
        entry = {
            "filename": "fixture.whl", "size": len(data), "sha256": sha256(data).hexdigest(),
            "installed_extension": extension,
        }
        lock = {"python_wheel": entry}
        with TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.whl"
            path.write_bytes(data)
            verify_python_wheel(path, lock)
            payload = read_pinned_pyodbc_wheel(path, entry)
            destination = path.with_name(filename)
            stage_pinned_pyodbc(path.parent, entry, payload)
            stage_pinned_pyodbc(path.parent, entry, payload)
            self.assertEqual(destination.read_bytes(), binary)
            destination.write_bytes(b"x" * len(binary))
            with self.assertRaisesRegex(ValueError, "installed pyodbc extension differs"):
                stage_pinned_pyodbc(path.parent, entry, payload)
            self.assertEqual(destination.read_bytes(), b"x" * len(binary))
            self.assertFalse(tuple(path.parent.glob(".pyodbc-*")))
            wrong = dict(entry, installed_extension=dict(extension, sha256="f" * 64))
            with self.assertRaisesRegex(ValueError, "extension differs"):
                verify_python_wheel(path, {"python_wheel": wrong})
            with self.assertRaisesRegex(ValueError, "no Python wheel lock"):
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


class DetachedAptTests(TestCase):
    def test_command_uses_absolute_local_files_and_closes_apt_sources(self):
        package_path = Path.cwd() / "example.deb"
        apt_state = Path.cwd() / 'apt-state'
        simulated = apt_install_command((package_path,), apt_state, simulate=True)
        applied = apt_install_command((package_path,), apt_state, simulate=False)
        self.assertEqual(simulated[2:], applied[2:])
        self.assertEqual((simulated[1], applied[1]), ("--simulate", "--assume-yes"))
        self.assertIn("--no-remove", applied)
        self.assertIn(f"Dir::Etc::sourceparts={apt_state / 'sources.list.d'}", applied)
        self.assertIn(f"Dir::State::lists={apt_state / 'lists'}", applied)
        self.assertEqual(applied[-2:], ["install", str(package_path)])
        with self.assertRaisesRegex(ValueError, "absolute package paths"):
            apt_install_command((Path("example.deb"),), apt_state, simulate=True)

    def test_real_role_requires_the_wheel_before_apt(self):
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        base = package("base", "1.0")
        lock["dpkg_status_sha256"] = sha256(base).hexdigest()
        guest_os = SimpleNamespace(geteuid=lambda: 0, statvfs=lambda _: SimpleNamespace(f_flag=1), ST_RDONLY=1)
        with (
            TemporaryDirectory() as directory,
            patch("external_tables_guest_apt.sys", SimpleNamespace(platform="linux")),
            patch("external_tables_guest_apt.os", guest_os),
            patch("external_tables_guest_apt.require_guest_detached"),
            patch("external_tables_guest_apt.read_dpkg_status", return_value=base),
            patch("external_tables_guest_apt.verify_packages"),
            patch("external_tables_guest_apt._run_apt") as apt,
        ):
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "requires its role lock and private directory"):
                install_verified_guest_packages(root, lock, Role.SOURCE, monotonic() + 3)
            with self.assertRaises(FileNotFoundError):
                install_verified_guest_packages(root, lock, Role.SOURCE, monotonic() + 3, wheel_install_dir=root)
            apt.assert_not_called()

    def test_query_stages_dotnet_after_simulation_but_before_package_configuration(self):
        base = package("base", "1.0")
        after = base + package("client", "2.0")
        sdk = {"filename": "locked-sdk.tar.gz"}
        lock = {
            "roles": {"query": ["client"]},
            "dpkg_status_sha256": sha256(base).hexdigest(),
            "dotnet_sdk": sdk,
            "packages": [{"package": "client", "version": "2.0", "architecture": "amd64", "path": "pool/client.deb"}],
        }
        guest_os = SimpleNamespace(geteuid=lambda: 0, statvfs=lambda _: SimpleNamespace(f_flag=1), ST_RDONLY=1)
        for broken in (False, True):
            with self.subTest(broken=broken), TemporaryDirectory() as directory:
                events = []
                root = Path(directory).resolve()
                deadline = monotonic() + 5

                def run_apt(command, bound):
                    self.assertEqual(bound, deadline)
                    if "--simulate" in command:
                        events.append("simulate")
                        return b"Inst client (2.0 local [amd64])\n"
                    events.append("configure")
                    return b""

                def install_sdk(stage, entry, bound):
                    self.assertEqual((stage, entry, bound), (root, sdk, deadline))
                    events.append("sdk")
                    if broken:
                        raise ValueError("wrong SDK")

                with (
                    patch("external_tables_guest_apt.sys", SimpleNamespace(platform="linux")),
                    patch("external_tables_guest_apt.os", guest_os),
                    patch("external_tables_guest_apt.require_guest_detached"),
                    patch("external_tables_guest_apt.read_dpkg_status", side_effect=[base, base, after]),
                    patch("external_tables_guest_apt.verify_packages"),
                    patch("external_tables_guest_apt.install_dotnet_sdk", side_effect=install_sdk),
                    patch("external_tables_guest_apt._run_apt", side_effect=run_apt),
                ):
                    if broken:
                        with self.assertRaisesRegex(ValueError, "wrong SDK"):
                            install_verified_guest_packages(root, lock, Role.QUERY, deadline)
                        self.assertEqual(events, ["simulate", "sdk"])
                    else:
                        self.assertEqual(install_verified_guest_packages(root, lock, Role.QUERY, deadline), 2)
                        self.assertEqual(events, ["simulate", "sdk", "configure"])

    def test_requires_detachment_again_after_the_exact_simulation(self):
        base = package("base", "1.0")
        after = base + package("client", "2.0")
        plan = b"Inst client (2.0 local [amd64])\n"
        lock = {
            "roles": {"source": ["client"]},
            "dpkg_status_sha256": sha256(base).hexdigest(),
            "packages": [{"package": "client", "version": "2.0", "architecture": "amd64", "path": "pool/client.deb"}],
        }
        guest_os = SimpleNamespace(geteuid=lambda: 0, statvfs=lambda _: SimpleNamespace(f_flag=1), ST_RDONLY=1)
        for attach in (True, False):
            with self.subTest(attach=attach), TemporaryDirectory() as directory:
                net = Path(directory) / "net"
                net.mkdir()
                (net / "lo").touch()

                def run_apt(command, _deadline):
                    if "--simulate" in command:
                        if attach:
                            (net / "eth0").touch()
                        return plan
                    return b""

                with (
                    patch("external_tables_guest_apt.sys", SimpleNamespace(platform="linux")),
                    patch("external_tables_guest_apt.os", guest_os),
                    patch("external_tables_guest_apt._NET_INTERFACES", net),
                    patch("external_tables_guest_apt.read_dpkg_status", side_effect=[base, base, after]),
                    patch("external_tables_guest_apt.verify_packages"),
                    patch("external_tables_guest_apt._run_apt", side_effect=run_apt) as apt,
                ):
                    if attach:
                        with self.assertRaisesRegex(ValueError, "only its loopback"):
                            install_verified_guest_packages(Path(directory), lock, Role.SOURCE, monotonic() + 3)
                        self.assertEqual(apt.call_count, 1)
                    else:
                        self.assertEqual(
                            install_verified_guest_packages(Path(directory), lock, Role.SOURCE, monotonic() + 3), 2,
                        )
                        self.assertEqual(apt.call_count, 2)


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
