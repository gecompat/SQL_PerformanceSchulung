# OPT-013 – Kontrollierter Sort-Spill und geeigneter Zugriffspfad

| Merkmal | Wert |
|---|---|
| Status | `IMPLEMENTED` |
| Sicherheitsstufe | `YELLOW` |
| Primäre Zielversion | SQL Server 2025 |
| Unterstützte Versionen | SQL Server 2019, 2022 und 2025 |
| Compatibility Level | 150, 160 und 170 |
| Edition / Plattform | Database Engine; Windows oder Linux |
| Sessions | 1 |
| Laufzeitklasse | M |
| Testprofil | `TP-PERF` |

## 1. Lernziel

Nach Abschluss kann die lernende Person einen Sort-Spill als Runtime-Ereignis nachweisen, ihn von einer bloßen Memory-Grant-Schätzung unterscheiden und eine Gegenmaßnahme anhand der benötigten Ordnung und des Zugriffspfads bewerten.

## 2. Fachliche Kernaussage

**Evidenzklasse:** `DOKUMENTIERT` und `EMPIRISCH`

Sort- und Hashoperatoren verwenden Workspace Memory. Reicht der nutzbare Grant nicht aus, können Arbeitssätze nach TempDB ausgelagert werden. `last_spills` in `sys.dm_exec_query_stats` misst die zuletzt verschütteten Seiten eines beendeten Statements. Die Demo erzwingt einen begrenzten Sort-Spill über `MAX_GRANT_PERCENT`, ohne die Instanzkonfiguration zu verändern, und entfernt den Sort anschließend durch einen zur geforderten Ordnung passenden Index.

## 3. Nichtziel

Die Demo definiert keinen universellen Memory-Grant-Schwellenwert und empfiehlt nicht, Grants pauschal zu erhöhen. Sie behandelt weder globale Memory Pressure noch `RESOURCE_SEMAPHORE` als primäres Thema.

## 4. Voraussetzungen

SQL Server 2019 bis 2025, `CREATE DATABASE` und versionsgerechte Server-State-Sichtbarkeit. Mindestanforderungen sind 2 logische CPU-Kerne, 3 GB RAM und 600 MB freier Datenträgerspeicher. Es ist nur eine Instanz erforderlich.

## 5. Sicherheits- und Abbruchrahmen

Die Demo ist gelb, weil 300.000 breite Zeilen sortiert und ein kontrollierter TempDB-Spill erzeugt werden. Das Harness verlangt `--confirm-isolated-lab`; die maximale Laufzeit beträgt 360 Sekunden. Jede Query verwendet `MAXDOP 1`. Es werden keine globalen Caches geleert und keine Serveroptionen verändert. Timeout und Cleanup folgen `FWK-008` und `FWK-010`.

## 6. Synthetisches Datenmodell

`lab.SpillData` enthält 300.000 Zeilen mit einem deterministischen Sortierschlüssel und einer 200 Byte breiten Nutzlast. Die Baseline sortiert mit einem normalen prozentualen Grant. Der Problemzustand begrenzt den Grant auf 0,1 Prozent. Die Gegenmaßnahme ist `IX_SpillData_Payload_SortKey`, dessen Schlüsselreihenfolge der Window-Function-Ordnung entspricht.

## 7. Ablauf

| Phase | Datei | Zweck |
|---|---|---|
| Preflight | `00_Preflight.sql` | Version, Rechte und gelbe Sicherheitsbestätigung prüfen |
| Setup | `10_Setup.sql` | Testdatenbank und 300.000 breite Zeilen anlegen |
| Baseline | `20_Baseline.sql` | geordnete Window-Abfrage mit normalem Grant messen |
| Demonstration | `30_Demonstration.sql` | dieselbe Abfrage mit 0,1 Prozent Grant ausführen |
| Observation | `40_Observation.sql` | `last_spills` und Ergebnisequivalenz prüfen |
| Mitigation | `50_Mitigation.sql` | geordneten nichtclustered Index anlegen |
| Comparison | `60_Comparison.sql` | identische Low-Grant-Abfrage ohne Sort-Spill prüfen |
| Cleanup | `90_Cleanup.sql` | markierte Testdatenbank entfernen |

## 8. Erwartete Beobachtung

Baseline und Problemzustand liefern denselben Checksum-Wert. Die Baseline besitzt `last_spills = 0`; der Problemzustand besitzt `last_spills > 0`. Nach dem Indexaufbau verwendet die Abfrage die vorhandene Ordnung, der Sort entfällt und `last_spills` ist trotz desselben niedrigen Grant-Hints wieder 0.

## 9. Interpretation

Ein Spill ist Runtime-Evidenz für unzureichenden nutzbaren Workspace des konkreten Operators. Er beweist nicht automatisch, dass die Server-Memory-Konfiguration falsch ist. Geeignete Maßnahmen können Datenmenge, Schätzung, Operatorwahl, Ordnung oder Grant beeinflussen. Hier wird absichtlich ein Zugriffspfad gewählt, der die benötigte Sortierung vermeidet.

## 10. Cleanup und Wiederherstellung

Der Vergleichsindex liegt ausschließlich in der markierten Testdatenbank. `90_Cleanup.sql` entfernt die Datenbank nach vollständiger Markerprüfung. Ein Timeout führt über `FWK-010` in denselben Cleanup-Pfad.

## 11. Tests

Die Runtime-Matrix führt die Demo je Version zweimal aus und prüft identische Checksums, Baseline ohne Spill, Problemzustand mit positivem `last_spills`, Vergleich ohne Spill sowie vollständiges Cleanup. Es werden keine festen Laufzeit- oder TempDB-Größenverhältnisse verlangt.

## 12. Bekannte Grenzen

Die konkrete Spill-Seitenzahl hängt von verfügbarem Speicher und Engine-Build ab. Der Datensatz und der 0,1-Prozent-Hint sind so dimensioniert, dass nur die Richtung `0 → positiv → 0` Vertragsbestandteil ist.

## 13. Quellen

| Quellen-ID | Aussagebezug | Gültigkeitsbereich | Abrufdatum |
|---|---|---|---|
| `SRC-029` | TempDB- und Spill-Evidenz | SQL Server 2019–2025 | 2026-07-24 |
| `SRC-031` | Actual Plan und Runtime-Warnings | SQL Server 2019–2025 | 2026-07-24 |
| Microsoft Learn: `sys.dm_exec_query_stats` | `last_spills` und `total_spills` | SQL Server 2019–2025 | 2026-07-24 |

## 14. Traceability

| Element | Zuordnung |
|---|---|
| Lernziel | `LO-M02-05` |
| Folie / Claim | `CLM-030`, Folie 30 |
| Demo-ID | `OPT-013` |
| Testprofil | `TP-PERF` |
