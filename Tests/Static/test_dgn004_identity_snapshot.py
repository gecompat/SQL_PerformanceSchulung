"""Synthetic raw-row checks for the offline DGN-004 identity comparator."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dgn004_identity_snapshot import (
    CACHE_ORIGIN,
    MODULE_ORIGIN,
    QUERY_STORE_ORIGIN,
    CacheRecord,
    IdentitySnapshotError,
    ModuleRecord,
    QueryStoreRecord,
    SuppliedIdentityCandidate,
    check_supplied_record_consistency,
    registered_text_views,
)


def records(*, cache_variant: str = "S", query_variant: str = "S") -> list[SuppliedIdentityCandidate]:
    views = registered_text_views()
    output = []
    for role, object_id, query_id, text_id in (("R", 101, 201, 301), ("H", 102, 202, 302)):
        view = views[role]
        module_schema, module_name = view.module_name
        module = ModuleRecord(
            MODULE_ORIGIN, 73, module_schema, module_name, object_id, view.module_text
        )
        if cache_variant == "S":
            end = view.statement_start_offset + view.statement_bytes - 2
        elif cache_variant == "T":
            end = view.statement_start_offset + len(view.statement_without_terminator.encode("utf-16le")) - 2
        elif cache_variant == "M_END":
            end = -1
        else:
            raise AssertionError(cache_variant)
        cache = CacheRecord(
            CACHE_ORIGIN, 73, object_id, view.module_text,
            view.statement_start_offset, end,
        )
        query_text = view.statement_text if query_variant == "S" else view.statement_without_terminator
        query = QueryStoreRecord(
            QUERY_STORE_ORIGIN, 73, object_id, query_id, text_id, 901 + object_id, 0, query_text
        )
        output.append(SuppliedIdentityCandidate(role, module, cache, query))
    return output


class Dgn004IdentitySnapshotTests(unittest.TestCase):
    def test_exact_registered_m_and_all_finite_s_t_offset_forms_are_accepted(self) -> None:
        for cache_variant in ("S", "T", "M_END"):
            for query_variant in ("S", "T"):
                with self.subTest(cache=cache_variant, query_store=query_variant):
                    result = check_supplied_record_consistency(
                        records(cache_variant=cache_variant, query_variant=query_variant),
                        expected_database_id=73,
                    )
                    self.assertEqual([item.role for item in result], ["R", "H"])
                    self.assertEqual([item.cache_statement_variant for item in result], [
                        "S" if cache_variant == "M_END" else cache_variant,
                        "S" if cache_variant == "M_END" else cache_variant,
                    ])
                    self.assertEqual([item.query_store_text_variant for item in result], [query_variant] * 2)

    def test_summary_is_explicitly_offline_and_carries_no_plan_handle(self) -> None:
        result = check_supplied_record_consistency(records(), expected_database_id=73)
        self.assertTrue(all(item.scope == "OFFLINE_SUPPLIED_RECORD_CONSISTENCY_ONLY" for item in result))
        self.assertFalse(any(hasattr(item, "plan_handle") for item in result))

    def test_role_mapping_is_exact_and_not_swappable(self) -> None:
        values = records()
        values[0] = replace(values[0], module=replace(values[0].module, module_name="ReplayHintControl"))
        with self.assertRaisesRegex(IdentitySnapshotError, "R: module name does not match"):
            check_supplied_record_consistency(values, expected_database_id=73)

    def test_distinct_role_ids_are_required_and_ambiguous_candidates_are_rejected(self) -> None:
        values = records()
        values[1] = replace(
            values[1],
            module=replace(values[1].module, object_id=values[0].module.object_id),
            cache=replace(values[1].cache, object_id=values[0].cache.object_id),
            query_store=replace(
                values[1].query_store,
                object_id=values[0].query_store.object_id,
                query_id=values[0].query_store.query_id,
                query_text_id=values[0].query_store.query_text_id,
            ),
        )
        with self.assertRaisesRegex(IdentitySnapshotError, "distinct supplied object_id"):
            check_supplied_record_consistency(values, expected_database_id=73)
        with self.assertRaisesRegex(IdentitySnapshotError, "exactly one caller-supplied"):
            check_supplied_record_consistency(records() + [records()[0]], expected_database_id=73)

    def test_supplied_origin_labels_and_database_object_joins_are_checked(self) -> None:
        values = records()
        values[0] = replace(values[0], cache=replace(values[0].cache, origin="other source"))
        with self.assertRaisesRegex(IdentitySnapshotError, "cache origin label"):
            check_supplied_record_consistency(values, expected_database_id=73)
        values = records()
        values[0] = replace(values[0], cache=replace(values[0].cache, object_id=999))
        with self.assertRaisesRegex(IdentitySnapshotError, "object_id differs across"):
            check_supplied_record_consistency(values, expected_database_id=73)
        values = records()
        values[1] = replace(values[1], query_store=replace(values[1].query_store, database_id=74))
        with self.assertRaisesRegex(IdentitySnapshotError, "expected database_id"):
            check_supplied_record_consistency(values, expected_database_id=73)

    def test_exact_m_sources_and_query_store_text_forms_are_required(self) -> None:
        values = records()
        values[0] = replace(values[0], module=replace(values[0].module, definition=values[0].module.definition + " "))
        with self.assertRaisesRegex(IdentitySnapshotError, "module definition does not equal registered M"):
            check_supplied_record_consistency(values, expected_database_id=73)
        values = records()
        values[0] = replace(values[0], cache=replace(values[0].cache, batch_text=values[0].cache.batch_text[:-1]))
        with self.assertRaisesRegex(IdentitySnapshotError, "cache batch text does not equal registered M"):
            check_supplied_record_consistency(values, expected_database_id=73)
        values = records()
        values[0] = replace(values[0], query_store=replace(values[0].query_store, query_text="EXEC [dgn004].[ReplayReference]"))
        with self.assertRaisesRegex(IdentitySnapshotError, "Query Store text does not equal registered S or T"):
            check_supplied_record_consistency(values, expected_database_id=73)

    def test_cache_offsets_and_parameterization_must_match_the_planned_contract(self) -> None:
        values = records()
        values[0] = replace(values[0], cache=replace(values[0].cache, statement_start_offset=values[0].cache.statement_start_offset + 2))
        with self.assertRaisesRegex(IdentitySnapshotError, "cache statement start offset"):
            check_supplied_record_consistency(values, expected_database_id=73)
        values = records()
        values[0] = replace(values[0], cache=replace(values[0].cache, statement_end_offset=values[0].cache.statement_end_offset - 1))
        with self.assertRaisesRegex(IdentitySnapshotError, "cache statement offsets"):
            check_supplied_record_consistency(values, expected_database_id=73)
        values = records()
        values[0] = replace(values[0], query_store=replace(values[0].query_store, parameterization_type=1))
        with self.assertRaisesRegex(IdentitySnapshotError, "parameterization_type"):
            check_supplied_record_consistency(values, expected_database_id=73)

    def test_context_id_is_retained_and_required_but_not_reinterpreted(self) -> None:
        values = records()
        values[0] = replace(values[0], query_store=replace(values[0].query_store, context_settings_id=-1))
        with self.assertRaisesRegex(IdentitySnapshotError, "context_settings_id must be retained"):
            check_supplied_record_consistency(values, expected_database_id=73)
        result = check_supplied_record_consistency(records(), expected_database_id=73)
        self.assertEqual(result[0].context_settings_id, 1002)


if __name__ == "__main__":
    unittest.main()
