# Aktueller Ausführungsstand

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-07-26 |
| Geprüfter Ausgangscommit auf `origin/main` | `6e914da6ab87e4ba17a354bc6e8c4d1c06446396` |
| Aktuelle Verarbeitungswelle | `ADV-008` – Runtime-Schnitte `OPT-015` und `OPT-016` |
| Zweck | kanonischer operativer Einstiegspunkt für die weitere Implementierung und Runtime-Validierung |

## 1. Verifizierter Repository-Stand

Der Commit `6e914da6ab87e4ba17a354bc6e8c4d1c06446396` ist auf `origin/main` vorhanden. Er enthält `ADV-001` bis `ADV-007`, die vollständige Designfreigabe Gate V2 sowie die Designverträge für LAB-VP1 bis LAB-VP5.

Welle 0 und Gate A, `FWK-001` bis `FWK-012`, die Framework-Matrix 2019/2022/2025, Gate B, `W2-001`, `W2-007`, `ADV-001` bis `ADV-007`, `PRS-009`, `PRS-011` und `TST-002` sind validiert.

## 2. Abgeschlossener ADV-008-Teilstand

| Demo | Ergebnis | Status |
|---|---|---|
| `OPT-015` | planweite und operatorbezogene Planevidenz mit synthetischem Out-of-range-Statistikfall, gezielter Statistikaktualisierung und normalisiertem Actual-Plan-Vertrag | `VALIDATED` |
| `OPT-016` | Outer References, Rebinds, Rewinds und optimizergewählte Performance Spool mit kontrollierter `NO_PERFORMANCE_SPOOL`-Gegenprobe | `VALIDATED` |

Beide Demos besitzen den vollständigen Phasenvertrag Preflight, Setup, Baseline, Demonstration, Observation, Mitigation, Comparison und Cleanup. Sie verwenden markergebundene synthetische Testdatenbanken, aktivieren `LAST_QUERY_PLAN_STATS` ausschließlich datenbankbezogen und persistieren kein Plan XML.

Die Runtime-Matrix führte jede Demo auf SQL Server 2019, 2022 und 2025 zweimal aus. Damit wurden zwölf vollständige Demo-Läufe einschließlich unabhängig geprüftem Cleanup erfolgreich abgeschlossen.

## 3. Fachliche Ergebnisse

`OPT-015` trennt Estimated Cost, Estimated Rows und Actual Runtime Evidence. Der Problemzustand ergänzt 60.000 Zeilen für einen zuvor nicht vorhandenen Schlüssel, ohne die relevante Indexstatistik zu aktualisieren. Die Gegenmaßnahme aktualisiert ausschließlich diese Statistik. Problem und Vergleich liefern dieselbe Ergebnismenge; der absolute Schätzfehler wird nachweisbar kleiner.

`OPT-016` zeigte während der ersten Runtimeabnahme, dass SQL Server auch mit passendem Index bereits eine Performance Spool erzeugen kann. Der Vertrag wurde deshalb nicht gegen die reale Optimizerentscheidung durchgesetzt. Baseline und Vergleich verwenden `NO_PERFORMANCE_SPOOL` als explizite A/B-Gegenprobe; der Problemzustand bleibt hintfrei. Auf allen drei Zielversionen wurden Outer References, Spool, Rebind-/Rewind-Richtung und Ergebnisequivalenz nachgewiesen.

## 4. Gate-Status

- Gate V0 – Quellenfreigabe: `VALIDATED`.
- Gate V1 – Curriculumfreigabe: `VALIDATED`.
- Gate V2 – Designfreigabe: `VALIDATED`.
- Gate V3 – Runtimefreigabe: `PARTIAL`; `OPT-015` und `OPT-016` sind freigegeben, weitere Vertiefungsdemos bleiben offen.
- Gate V4 – Lehrmittelfreigabe: offen.

`OPT-015` und `OPT-016` sind vollständig `VALIDATED`. `OPT-017`, `QRY-013`, die erweiterte Struktur von `QRY-004`, die LAB-VP3-/VP4-Schritte und `DGN-007` bleiben `DESIGNED` beziehungsweise `PLANNED`.

## 5. Nächste fachliche Verarbeitung

Der nächste abhängige ADV-008-Schnitt umfasst:

1. `QRY-013` – neutraler Client- und Sessionkontext mit getrennten SET-, Cache-, Parameter- und Datenbankdimensionen.
2. `QRY-004_CLASSIC_AND_DYNAMIC` – Catch-all, `OPTION (RECOMPILE)` und sicher parameterisiertes dynamisches SQL.
3. Query-Store-/XE-Pilotvalidierung vor diagnoseabhängigen Schnitten.
4. `OPT-017` und LAB-VP3-/VP4-Implementierungen anschließend in getrennten Ressourcen- und Featurepaketen.
5. `DGN-007` erst nach stabiler Query-Store-/XE-Evidenz.
6. `RES-003` zuletzt, separat und ausschließlich auf dedizierter Infrastruktur.

## 6. Parallel ausführbare Querschnittsarbeit

Unabhängig vom nächsten ADV-008-Schnitt bleiben ausführbar:

- `PRS-012` und `TST-011`: SlideKeys, Custom Shows und statische Präsentationsvariantenprüfung,
- fachlich getrennte `W2-002`-Teilpakete,
- Entscheidungspfad T-SQL/Testdatenbank vor zusätzlicher Infrastruktur im Demo-Katalog,
- Testumgebungs-How-to für vorhandene Instanz sowie Docker/Podman.

## 7. Abhängigkeiten und Sicherheitsgrenzen

- `ADV-008` verwendet ausschließlich die validierten Designverträge aus `ADV-004` bis `ADV-007`.
- `ADV-009` setzt belastbare Runtime-Evidenz und die Präsentationsvariantenverträge voraus.
- `DGN-007` setzt eine validierte Query-Store- und XE-Nutzung voraus.
- `RES-003` setzt dedizierte Wegwerfinfrastruktur, explizite High-Impact-Bestätigung, externen Kill-Switch und ein maximales Laufzeitbudget voraus.
- `PRS-013` setzt `PRS-012` und den statischen Kern von `TST-011` voraus.
- `W2-003` bis `W2-006` setzen die jeweils zugehörige Neutralisierung aus `W2-002` voraus.

## 8. Aktuelle Blocker

Es besteht kein globaler technischer Blocker. Der nächste Runtime-Schnitt kann beginnen. Planform- und featureabhängige Demos liefern kontrollierte Skips, wenn eine Optimizerentscheidung, Eligibility oder Query-Store-Voraussetzung nicht erfüllt ist. Rote Ressourcenlast wird nicht auf gemeinsam genutzten Systemen ausgeführt.

## 9. Datenschutz- und Quellenstatus

Die implementierten Demos enthalten ausschließlich deterministische synthetische Daten, öffentliche Quellen-IDs, neutrale Demo- und Claim-IDs sowie generische Ressourcenprofile. Reale Anwendungs-, Host-, Benutzer-, Kunden-, Zugangs- oder Diagnosedaten sind ausgeschlossen. Plan XML wird nur flüchtig ausgewertet; Repository und Diagnoseartefakte enthalten ausschließlich normalisierte, synthetische Evidenz.
