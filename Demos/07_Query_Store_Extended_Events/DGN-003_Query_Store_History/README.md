# DGN-003 – Query-Store-Historie

| Feld | Wert |
|---|---|
| Demo-ID | `DGN-003` |
| Status | `VALIDATED` |
| Sicherheitsstufe | `GREEN` |
| Versionen | SQL Server 2019, 2022 und 2025 |
| Compatibility Level | 150, 160 und 170 |

## 1. Lernziel

Query-, Plan-, Runtime- und verfügbare Wait-Historie aus Query Store zeitlich und semantisch von Live-DMVs unterscheiden.

## 2. Fachliche Kernaussage

Query Store liefert persistente Historie innerhalb seiner Capture- und Aufbewahrungsgrenzen. Mehrere Pläne sind beobachtbare Evidenz, aber keine garantierte Optimizerentscheidung.

## 3. Nichtziel

Plan Forcing und Query Store Hints gehören zu `DGN-004`; diese Demo verändert keine Plansteuerung.

## 4. Voraussetzungen

Eine markergebundene Wegwerfdatenbank, Berechtigung zum Erstellen einer Datenbank und SQL Server 2019 bis 2025. Empfohlen sind zwei Kerne, 4 GB RAM und 2 GB freier Speicher.

## 5. Sicherheits- und Abbruchrahmen

Query Store wird nur in der neu erzeugten Testdatenbank aktiviert und zusammen mit ihr entfernt. Der Harness besitzt getrennte Laufzeit- und Cleanup-Budgets.

## 6. Synthetisches Datenmodell

`lab.SearchData` enthält 50.000 neutrale Zeilen mit einer deterministisch häufigen und mehreren seltenen Gruppen. `lab.QueryStoreEvidence` speichert nur aggregierte Zähler und Checksummen.

## 7. Ablauf

Preflight und Setup aktivieren einen begrenzten Query Store. Baseline und Demonstration führen dieselbe Prozedur mit unterschiedlicher Selektivität aus. Observation liest ausschließlich markerbezogene Query-Store-Zeilen; Comparison prüft den Ausführungsvertrag.

## 8. Erwartete Beobachtung

Query- und Runtime-Historie müssen vorhanden sein. Eine zweite Planform ergibt `PASS`; eine vorhandene Historie mit nur einer Planform ergibt kontrolliert `WARN_EMPIRICAL_VARIANCE`. Fehlende Historie ergibt `SKIP_EVIDENCE_MISSING`.

## 9. Interpretation

Plananzahl, Runtimeintervalle und Wait-Zeilen beschreiben verschiedene Dimensionen. Keine davon ist allein ein Ursachenbeweis.

## 10. Cleanup und Wiederherstellung

`90_Cleanup.sql` prüft alle vier Eigentumsmarker und entfernt danach die Testdatenbank einschließlich Query Store. Ein passender Name allein reicht nicht.

## 11. Tests

Der statische Pilotvertrag sowie der Runtime-Runner prüfen Struktur, Statuscodes, zwei Wiederholungen je Zielversion und das unabhängige Fehlen der Datenbank nach jedem Lauf.

## 12. Bekannte Grenzen

Query-Store-Flush und Optimizerplanwahl sind empirisch. Exakte Zeit-, Plan-ID- oder Wait-Werte sind keine Golden Values.

## 13. Quellen

- `SRC-027`, Microsoft Learn: Query Store, Abrufdatum 2026-07-24.
- `SRC-035` und `SRC-036`, Microsoft Learn: Wait-Statistiken, Abrufdatum 2026-07-24.

## 14. Traceability

`CLM-076`, `ADV-CLM-034`, `ADV-CLM-035`, `LO-M06-04`, `LO-M06-08`, `W-DGN-001`.
