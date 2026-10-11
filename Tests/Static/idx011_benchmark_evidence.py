"""Begrenzter Ergebnisvertrag für den öffentlichen IDX-011-Benchmarkentwurf.

Keine SQL-Ausführung, keine Freigabe und keine numerische Generationsableitung.
Die tatsächliche Quellen-, Index-, Plan- und Lifecyclebindung bleibt beim Runner.
"""
from __future__ import annotations

import datetime
import math
import statistics
import uuid

BATCH_SIZE = 100
K = 5
MIN_HITS = 4
METRICS = ("CpuMs", "ElapsedUs", "Reads", "LogicalReads", "Writes")
SEQUENCES = {"AB": ("EXACT", "VECTOR_SEARCH"),
             "BA": ("VECTOR_SEARCH", "EXACT"),
             "AA": ("EXACT", "EXACT")}
EXPECTED_WINDOWS = [(block, order, slot, path)
                    for block in range(1, 4)
                    for order, paths in SEQUENCES.items()
                    for slot, path in enumerate(paths, 1)]


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def request_identity(row):
    """Eine tatsächliche Identität; Booleans und Platzhalter sind keine IDs."""
    if (row.get("CounterSource") != "LIVE_REQUEST"
            or not integer(row.get("SessionId"), 1)
            or not integer(row.get("RequestId"))
            or not integer(row.get("DatabaseId"), 5)):
        raise ValueError("Tatsächliche Request-/Session-/DB-Bindung fehlt")
    started, connection = row.get("RequestStartTime"), row.get("ConnectionId")
    if not isinstance(started, str) or not isinstance(connection, str):
        raise ValueError("Tatsächliche Requestzeit oder Connection-ID fehlt")
    try:
        timestamp = datetime.datetime.fromisoformat(started)
        connection_id = uuid.UUID(connection)
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("Ungültige Requestzeit oder Connection-ID") from exc
    if timestamp.year < 2000 or connection_id.int == 0:
        raise ValueError("Requestbindung enthält einen Platzhalter")
    return (row["SessionId"], row["RequestId"], timestamp, connection_id, row["DatabaseId"])


def validate_query(rows, path, source_distances, exact_ids):
    """Qualität je Query; ein guter Batchmittelwert verdeckt keinen Ausreißer."""
    if not isinstance(rows, list) or len(rows) != K:
        raise ValueError("Tatsächliche Query muss genau fünf Rows liefern")
    ids = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Ungültige Ergebnisrow")
        identity, distance = row.get("Id"), row.get("DistanceValue")
        if (not integer(identity, 1) or identity not in source_distances or identity in ids
                or type(distance) not in (int, float) or not math.isfinite(distance)
                or not 0 <= distance <= 2
                or abs(distance - source_distances[identity]) > 0.0001):
            raise ValueError("Quellen-ID, Duplikat oder tatsächliche Distanz verletzt")
        ids.add(identity)
    hits = len(ids.intersection(exact_ids))
    if hits < (K if path == "EXACT" else MIN_HITS):
        raise ValueError("Vorab fixierte Qualität je Query verletzt")
    return hits


def validate_benchmark(records, source_distances, expected_database_id):
    """Zehn getrennte Warm-ups und 18 AB-/BA-/AA-Fenster, ohne Speedupclaim.

    source_distances muss aus der unabhängig vollständig geprüften synthetischen
    Quelle stammen. Dieser Validator ersetzt diese vorgelagerte Prüfung nicht.
    """
    if not integer(expected_database_id, 5):
        raise ValueError("Unabhängig attestierte eigene DB-ID fehlt")
    if (not isinstance(source_distances, dict)
            or set(source_distances) != set(range(1, 1001))
            or any(type(k) is not int for k in source_distances)
            or any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 2
                   for v in source_distances.values())):
        raise ValueError("Vollständige 1000-Row-Quellendistanzen fehlen")
    if not isinstance(records, list) or len(records) != 28:
        raise ValueError("Zehn Warm-ups und 18 Messfenster erforderlich")
    exact_ids = set(sorted(source_distances, key=lambda i: (source_distances[i], i))[:K])
    warmup_keys, window_keys, request_keys, database_ids = set(), [], set(), set()
    measured = []
    warmups_finished = False
    previous_end = None
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("Ungültiger Benchmarkdatensatz")
        binding = request_identity(row)
        if row["DatabaseId"] != expected_database_id:
            raise ValueError("Request gehört nicht zur unabhängig attestierten eigenen DB")
        if binding in request_keys:
            raise ValueError("Ein Request wurde mehrfach als unabhängiger Lauf gezählt")
        request_keys.add(binding)
        database_ids.add(row["DatabaseId"])
        path, kind = row.get("Path"), row.get("kind")
        if path not in ("EXACT", "VECTOR_SEARCH"):
            raise ValueError("Unbekannter Suchpfad")
        try:
            if not isinstance(row.get("StartedUtc"), str) or not isinstance(row.get("EndedUtc"), str):
                raise ValueError("Zeitfenster fehlt")
            started = datetime.datetime.fromisoformat(row["StartedUtc"])
            ended = datetime.datetime.fromisoformat(row["EndedUtc"])
        except (ValueError, TypeError) as exc:
            raise ValueError("Tatsächliches UTC-Zeitfenster fehlt") from exc
        if (started.tzinfo is not None or ended.tzinfo is not None or started.year < 2000
                or ended < started or previous_end is not None and started < previous_end):
            raise ValueError("UTC-Fenster fehlen, sind vertauscht oder überlappen")
        previous_end = ended
        delta = ended-started
        elapsed = (delta.days*86400+delta.seconds)*1000000+delta.microseconds
        if not integer(row.get("ElapsedUs")) or row["ElapsedUs"] != elapsed:
            raise ValueError("Elapsed stimmt nicht mit tatsächlichen UTC-Grenzen überein")
        if kind == "WARMUP_REQUEST":
            ordinal = row.get("Ordinal")
            if warmups_finished or not integer(ordinal, 1) or ordinal > 5:
                raise ValueError("Warm-up fehlt, ist verspätet oder außerhalb des Umfangs")
            key = path, ordinal
            if key in warmup_keys or row.get("Statements") != 1 or type(row.get("Statements")) is not int:
                raise ValueError("Doppelter Warm-up oder falscher Statementumfang")
            validate_query(row.get("ResultRows"), path, source_distances, exact_ids)
            warmup_keys.add(key)
            continue
        if kind != "MEASURED_WINDOW":
            raise ValueError("Unbekannter Benchmarkdatensatz")
        warmups_finished = True
        if warmup_keys != {(p, i) for p in ("EXACT", "VECTOR_SEARCH") for i in range(1, 6)}:
            raise ValueError("Messung begann vor allen separat protokollierten Warm-ups")
        block, order, slot = row.get("Block"), row.get("Order"), row.get("Slot")
        if not integer(block, 1) or not integer(slot, 1):
            raise ValueError("Block-/Slotbindung fehlt")
        window_keys.append((block, order, slot, path))
        if window_keys[-1] != EXPECTED_WINDOWS[len(window_keys)-1]:
            raise ValueError("Vorab fixierte AB-/BA-/AA-Reihenfolge verletzt")
        if type(row.get("Statements")) is not int or row["Statements"] != BATCH_SIZE:
            raise ValueError("Vorab fixierter Statementumfang verletzt")
        start, end = row.get("CountersBefore"), row.get("CountersAfter")
        if not isinstance(start, dict) or not isinstance(end, dict):
            raise ValueError("Tatsächlich beobachtete Start-/Endzähler fehlen")
        for name in METRICS:
            if not integer(row.get(name)):
                raise ValueError("Fehlender, negativer oder nicht ganzzahliger Messwert")
        for name in ("CpuMs", "Reads", "LogicalReads", "Writes"):
            if (not integer(start.get(name)) or not integer(end.get(name))
                    or end[name] < start[name] or row[name] != end[name]-start[name]):
                raise ValueError("Messdelta stimmt nicht mit tatsächlichen Zählern überein")
        if request_identity(start) != binding or request_identity(end) != binding:
            raise ValueError("Start-/Endfenster ist nicht derselbe tatsächliche Request")
        queries = row.get("Queries")
        if not isinstance(queries, list) or len(queries) != BATCH_SIZE:
            raise ValueError("Vollständige Ergebnisabdeckung aller Querys fehlt")
        hits = []
        for ordinal, query in enumerate(queries, 1):
            if not isinstance(query, dict) or type(query.get("Ordinal")) is not int or query["Ordinal"] != ordinal:
                raise ValueError("Query fehlt, ist doppelt oder außerhalb ihrer Reihenfolge")
            hits.append(validate_query(query.get("ResultRows"), path, source_distances, exact_ids))
        measured.append((row, hits))
    if window_keys != EXPECTED_WINDOWS or len(database_ids) != 1:
        raise ValueError("Messfenster oder vollständige DB-Bindung verletzt")
    summaries = []
    for path in ("EXACT", "VECTOR_SEARCH"):
        selected = [(row, hits) for row, hits in measured if row["Path"] == path and row["Order"] != "AA"]
        if not any(row["LogicalReads"] > 0 for row, _ in selected):
            raise ValueError("Live-Request-Messfenster nach Warm-up-Ausschluss inaktiv")
        summaries.append({"path": path, "measured_windows": len(selected),
                          "min_query_recall_at_5": min(min(hits)/K for _, hits in selected),
                          "metrics": {name: {"median": statistics.median(r[name] for r, _ in selected),
                                             "min": min(r[name] for r, _ in selected),
                                             "max": max(r[name] for r, _ in selected)} for name in METRICS},
                          "elapsed_zero_observed": any(r["ElapsedUs"] == 0 for r, _ in selected),
                          "cpu_zero_observed": any(r["CpuMs"] == 0 for r, _ in selected)})
    aa = [{"block": block,
           "first": {name: measured[block*6-2][0][name] for name in METRICS},
           "second": {name: measured[block*6-1][0][name] for name in METRICS}}
          for block in range(1, 4)]
    return {"kind": "BENCHMARK_SUMMARY", "generation": "UNKNOWN", "index_usage": "UNPROVEN",
            "excluded_warmup_requests_per_path": 5, "statements_per_window": BATCH_SIZE,
            "paths": summaries, "aa_controls": aa, "complete_worker_io": "UNPROVEN",
            "actual_search_dop": "UNPROVEN", "memory_grant": "NOT_CAPTURED",
            "spills": "NOT_CAPTURED", "waits": "NOT_CAPTURED", "preemptive_time": "NOT_CAPTURED",
            "includes_temp_result_storage_and_counter_capture": True,
            "no_speedup_guarantee": True, "runtime_qualification": "NOT_ESTABLISHED"}
