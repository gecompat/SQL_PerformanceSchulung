# DGN-005 – Begrenzte Extended-Events-Evidenz

| Feld | Wert |
|---|---|
| Demo-ID | `DGN-005` |
| Status | `IMPLEMENTED` |
| Sicherheitsstufe | `YELLOW` |
| Versionen | SQL Server 2019, 2022 und 2025 |

## 1. Lernziel

Event, Action, Predicate, Target und Erfassungszeitraum als gemeinsamen Evidenzvertrag lesen.

## 2. Fachliche Kernaussage

Extended Events liefern ereignisbezogene Evidenz. Fehlende Ereignisse sind nur aussagekräftig, wenn Session, Filter, Ereignisklasse und Zeitraum geeignet waren.

## 3. Nichtziel

Die Demo ist kein allgemeiner Servertrace und exportiert weder `.xel`-Dateien noch Ring-Buffer-XML.

## 4. Voraussetzungen

Eine bestätigte isolierte Instanz, Berechtigung zum Verwalten und Lesen von Event Sessions sowie SQL Server 2019 bis 2025.

## 5. Sicherheits- und Abbruchrahmen

Die gelbe Demo benötigt `--confirm-isolated-lab` und ein positives Zeitbudget. Die Session heißt deterministisch `SQLPERF_DGN005_<RUN>` und verwendet `STARTUP_STATE = OFF`. Auf SQL Server 2025 begrenzt `MAX_DURATION = 300 SECONDS` zusätzlich die aktive Session; 2019 und 2022 behalten denselben expliziten Stop-/Cleanup-Vertrag ohne diese Syntax.

## 6. Synthetisches Datenmodell

Die Testdatenbank enthält nur Eigentumsmarker und aggregierte Ereigniszähler. Zwei kontrolliert abgefangene Fehler mit neutralen Meldungen erzeugen die Evidenz.

## 7. Ablauf

Setup erstellt und startet die begrenzte Session. Demonstration erzeugt zwei synthetische Fehler. Observation zählt passende Ring-Buffer-Ereignisse, Mitigation stoppt die Session und Comparison prüft den Zustand.

## 8. Erwartete Beobachtung

Mindestens ein `error_reported`-Ereignis der markierten Datenbank ist sichtbar. Fehlende Evidenz ergibt `SKIP_EVIDENCE_MISSING`, nicht eine falsche Produktaussage.

## 9. Interpretation

DMVs, Query Store und Extended Events besitzen unterschiedliche zeitliche und semantische Sichten und ergänzen einander.

## 10. Cleanup und Wiederherstellung

Cleanup stoppt und entfernt ausschließlich die exakt benannte Session. Danach prüft er alle Datenbankmarker und entfernt die Testdatenbank.

## 11. Tests

Statische Prüfung und Runtime-Matrix validieren Ring-Buffer-Limit, `STARTUP_STATE = OFF`, fehlenden `event_file`-Export, Statuscodes und Cleanup.

## 12. Bekannte Grenzen

Dispatch-Latenz und Eventzahl sind empirisch. `MAX_DURATION` ist nur ein zusätzlicher SQL-Server-2025-Schutz und ersetzt weder explizites Stoppen noch Cleanup.

## 13. Quellen

- `SRC-028`, Microsoft Learn: Extended Events, Abrufdatum 2026-07-24.
- `SRC-060`, Microsoft Learn: zeitgebundene Extended-Events-Sessions, Abrufdatum 2026-08-28.
- `SRC-051` wird ausschließlich als Diagnosemethode verwendet und begründet keine Featureverfügbarkeit.

## 14. Traceability

`CLM-077`, `ADV-CLM-034`, `ADV-CLM-036`, `LO-M06-04`, `LO-M06-08`, `W-DGN-001`.
