"""Input-boundary tests for DGN-004 sqlcmd variable expansion."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dgn004_capture_input import CaptureInput, CaptureInputError, build_sqlcmd_variables


class Dgn004CaptureInputTests(unittest.TestCase):
    def test_valid_invocation_maps_to_exact_sqlcmd_variable_set(self) -> None:
        handle = "ab" * 64
        result = build_sqlcmd_variables(CaptureInput("run-2026_10.26", "H", 9, handle))
        self.assertEqual(result, {
            "DGN004_RUN": "run-2026_10.26",
            "DGN004_ROLE": "H",
            "DGN004_CALL": "9",
            "DGN004_PLAN_HANDLE": handle.upper(),
        })

    def test_rejects_interpolation_and_handle_mutations(self) -> None:
        bad = (
            CaptureInput("run' ; DROP DATABASE x--", "R", 1, "ab" * 64),
            CaptureInput("run x", "R", 1, "ab" * 64),
            CaptureInput("run", "X", 1, "ab" * 64),
            CaptureInput("run", "R", True, "ab" * 64),
            CaptureInput("run", "R", 10, "ab" * 64),
            CaptureInput("run", "R", 1, "ab" * 63),
            CaptureInput("run", "R", 1, "gh" * 64),
            CaptureInput("run", "R", 1, "ab" * 64 + "'"),
        )
        for value in bad:
            with self.subTest(value=value):
                with self.assertRaises(CaptureInputError):
                    build_sqlcmd_variables(value)

    def test_rejects_subclassed_or_untyped_container(self) -> None:
        class ExtendedInput(CaptureInput):
            pass

        with self.assertRaises(CaptureInputError):
            build_sqlcmd_variables(ExtendedInput("run", "R", 1, "ab" * 64))
        with self.assertRaises(CaptureInputError):
            build_sqlcmd_variables({"run": "run", "role": "R", "call": 1, "plan_handle_hex": "ab" * 64})  # type: ignore[arg-type]

    def test_rejects_overridden_primitive_fields_before_expansion(self) -> None:
        class UnsafeRun(str):
            def __format__(self, spec: str) -> str:
                raise AssertionError("run subclass formatting must not reach sqlcmd")

        class UnsafeRole(str):
            def __eq__(self, other: object) -> bool:
                return True

        class UnsafeCall(int):
            def __str__(self) -> str:
                raise AssertionError("call subclass formatting must not reach sqlcmd")

        class UnsafeHandle(str):
            def upper(self) -> str:
                raise AssertionError("handle subclass formatting must not reach sqlcmd")

        bad_values = (
            CaptureInput(UnsafeRun("run"), "R", 1, "ab" * 64),
            CaptureInput("run", UnsafeRole("X"), 1, "ab" * 64),
            CaptureInput("run", "R", UnsafeCall(1), "ab" * 64),
            CaptureInput("run", "R", 1, UnsafeHandle("ab" * 64)),
        )
        for value in bad_values:
            with self.subTest(field=type(value.run), role=type(value.role), call=type(value.call), handle=type(value.plan_handle_hex)):
                with self.assertRaises(CaptureInputError):
                    build_sqlcmd_variables(value)


if __name__ == "__main__":
    unittest.main()
