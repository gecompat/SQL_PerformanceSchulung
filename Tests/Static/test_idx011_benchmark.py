"""Synthetische Gegenproben; keine SQL- oder Demoqualifikation."""
import copy
import datetime
import unittest

from idx011_benchmark_evidence import EXPECTED_WINDOWS, validate_benchmark as evaluate_benchmark

DISTANCES = {i: i/1000 for i in range(1, 1001)}


def validate_benchmark(rows, source):
    return evaluate_benchmark(rows, source, expected_database_id=5)


def result_rows():
    return [{"Id": i, "DistanceValue": DISTANCES[i]} for i in range(1, 6)]


def fixture():
    records = []
    for path in ("EXACT", "VECTOR_SEARCH"):
        for ordinal in range(1, 6):
            records.append({"kind": "WARMUP_REQUEST", "Path": path,
                            "Ordinal": ordinal, "Statements": 1, "ResultRows": result_rows()})
    for block, order, slot, path in EXPECTED_WINDOWS:
        records.append({"kind": "MEASURED_WINDOW", "Path": path, "Block": block,
                        "Order": order, "Slot": slot, "Statements": 100,
                        "CpuMs": 3, "ElapsedUs": 4000, "Reads": 0, "LogicalReads": 120, "Writes": 0,
                        "StartedUtc": "2026-10-11T00:00:00.0000000",
                        "EndedUtc": "2026-10-11T00:00:00.0040000",
                        "Queries": [{"Ordinal": i, "ResultRows": result_rows()} for i in range(1, 101)]})
    for i, record in enumerate(records):
        binding = {"SessionId": 60+i, "RequestId": 0, "DatabaseId": 5,
                   "RequestStartTime": (datetime.datetime(2026, 10, 11)+datetime.timedelta(seconds=i)).isoformat(),
                   "ConnectionId": f"00000000-0000-0000-0000-{i+1:012x}", "CounterSource": "LIVE_REQUEST"}
        record.update(binding)
        started = datetime.datetime(2026, 10, 11)+datetime.timedelta(seconds=i)
        elapsed = 4000 if record["kind"] == "MEASURED_WINDOW" else 1000
        record.update({"StartedUtc": started.isoformat(timespec="microseconds"),
                       "EndedUtc": (started+datetime.timedelta(microseconds=elapsed)).isoformat(timespec="microseconds"),
                       "ElapsedUs": elapsed})
        if record["kind"] == "MEASURED_WINDOW":
            record["CountersBefore"] = {**binding, **{k: 0 for k in ("CpuMs", "Reads", "LogicalReads", "Writes")}}
            record["CountersAfter"] = {**binding, **{k: record[k] for k in ("CpuMs", "Reads", "LogicalReads", "Writes")}}
    return records


class BenchmarkBoundaries(unittest.TestCase):
    def test_complete_sequence_separates_warmup_aa_and_paired_paths(self):
        result = validate_benchmark(fixture(), DISTANCES)
        self.assertEqual(result["excluded_warmup_requests_per_path"], 5)
        self.assertEqual([p["measured_windows"] for p in result["paths"]], [6, 6])
        self.assertEqual(len(result["aa_controls"]), 3)
        self.assertEqual(result["runtime_qualification"], "NOT_ESTABLISHED")
        self.assertEqual(result["memory_grant"], "NOT_CAPTURED")

    def test_warmup_and_aa_never_change_paired_median(self):
        rows = fixture()
        for row in rows:
            if row.get("Order") == "AA":
                row["CpuMs"] = row["CountersAfter"]["CpuMs"] = 9999
        result = validate_benchmark(rows, DISTANCES)
        self.assertEqual(result["paths"][0]["metrics"]["CpuMs"]["median"], 3)
        self.assertEqual(result["aa_controls"][0]["first"]["CpuMs"], 9999)

    def test_coverage_order_and_duplicate_requests_fail(self):
        for mutation in ("missing", "duplicate", "order", "latewarm", "request"):
            rows = fixture()
            if mutation == "missing": rows.pop()
            if mutation == "duplicate": rows[11] = copy.deepcopy(rows[10])
            if mutation == "order": rows[10], rows[11] = rows[11], rows[10]
            if mutation == "latewarm": rows[9], rows[10] = rows[10], rows[9]
            if mutation == "request":
                for k in ("SessionId", "RequestId", "RequestStartTime", "ConnectionId"):
                    rows[9][k] = rows[8][k]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_benchmark(rows, DISTANCES)

    def test_missing_negative_boolean_and_inconsistent_counters_fail(self):
        for value in (None, -1, True, 2.5, 4):
            rows = fixture()
            rows[10]["CpuMs"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_benchmark(rows, DISTANCES)

    def test_changed_request_db_and_placeholder_bindings_fail(self):
        for target, key, value in (("CountersAfter", "SessionId", 999),
                                   ("CountersBefore", "ConnectionId", "00000000-0000-0000-0000-000000000000"),
                                   (None, "DatabaseId", 6), (None, "RequestId", True),
                                   (None, "RequestStartTime", "1900-01-01")):
            rows = fixture()
            (rows[10][target] if target else rows[10])[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate_benchmark(rows, DISTANCES)

    def test_one_bad_query_is_not_hidden_by_good_batch_mean(self):
        rows = fixture()
        rows[11]["Queries"][0]["ResultRows"] = [
            {"Id": i, "DistanceValue": DISTANCES[i]} for i in (1, 2, 3, 7, 8)]
        with self.assertRaises(ValueError): validate_benchmark(rows, DISTANCES)
        rows[11]["Queries"][0]["ResultRows"] = [
            {"Id": i, "DistanceValue": DISTANCES[i]} for i in (1, 2, 3, 4, 7)]
        self.assertEqual(validate_benchmark(rows, DISTANCES)["paths"][1]["min_query_recall_at_5"], 0.8)

    def test_missing_query_duplicate_id_foreign_id_and_false_distance_fail(self):
        for mutation in ("missing", "duplicate", "foreign", "distance", "ordinal"):
            rows = fixture()
            query = rows[10]["Queries"][0]
            if mutation == "missing": rows[10]["Queries"].pop()
            if mutation == "duplicate": query["ResultRows"][1] = copy.deepcopy(query["ResultRows"][0])
            if mutation == "foreign": query["ResultRows"][0]["Id"] = 1001
            if mutation == "distance": query["ResultRows"][0]["DistanceValue"] = 0.9
            if mutation == "ordinal": query["Ordinal"] = True
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_benchmark(rows, DISTANCES)

    def test_full_source_and_finite_distances_are_required(self):
        for mutation in ("missing", "extra", "bool", "nan"):
            source = dict(DISTANCES)
            if mutation == "missing": source.pop(1000)
            if mutation == "extra": source[1001] = 0.1
            if mutation == "bool": source[1] = True
            if mutation == "nan": source[1] = float("nan")
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_benchmark(fixture(), source)

    def test_actual_time_window_rejects_missing_reverse_and_wrong_delta(self):
        for key, value in (("StartedUtc", None), ("EndedUtc", "2026-10-10T00:00:00"),
                           ("ElapsedUs", 0), ("StartedUtc", "2026-10-11T00:00:00+02:00")):
            rows = fixture(); rows[10][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate_benchmark(rows, DISTANCES)

    def test_quantized_zero_is_visible_and_inactive_window_fails(self):
        rows = fixture()
        rows[10]["CpuMs"] = rows[10]["CountersAfter"]["CpuMs"] = 0
        rows[10]["ElapsedUs"] = 0; rows[10]["EndedUtc"] = rows[10]["StartedUtc"]
        result = validate_benchmark(rows, DISTANCES)
        self.assertTrue(result["paths"][0]["elapsed_zero_observed"])
        self.assertTrue(result["paths"][0]["cpu_zero_observed"])
        for row in rows[10:]:
            if row["Path"] == "VECTOR_SEARCH":
                row["LogicalReads"] = row["CountersAfter"]["LogicalReads"] = 0
        with self.assertRaises(ValueError): validate_benchmark(rows, DISTANCES)

    def test_warmup_and_measured_times_are_serial_in_declared_order(self):
        for mutation in ("warmup_missing", "warmup_overlap", "measure_overlap", "swapped"):
            rows = fixture()
            if mutation == "warmup_missing": rows[0].pop("StartedUtc")
            if mutation == "warmup_overlap": rows[1]["StartedUtc"] = rows[0]["StartedUtc"]
            if mutation == "measure_overlap": rows[11]["StartedUtc"] = rows[10]["StartedUtc"]
            if mutation == "swapped":
                for key in ("StartedUtc", "EndedUtc", "ElapsedUs"):
                    rows[10][key], rows[11][key] = rows[11][key], rows[10][key]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_benchmark(rows, DISTANCES)

    def test_all_consistent_foreign_database_and_unknown_attestation_fail(self):
        rows = fixture()
        for row in rows:
            row["DatabaseId"] = 6
            if row["kind"] == "MEASURED_WINDOW":
                row["CountersBefore"]["DatabaseId"] = row["CountersAfter"]["DatabaseId"] = 6
        with self.assertRaises(ValueError): validate_benchmark(rows, DISTANCES)
        for value in (None, True, 4, "5"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluate_benchmark(fixture(), DISTANCES, expected_database_id=value)


if __name__ == "__main__": unittest.main()
