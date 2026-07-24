# OPT-013 – Kontrollierter Sort-Spill durch veraltete Statistik

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

Nach Abschluss kann die lernende Person einen Sort-Spill als Runtime-Ereignis nachweisen, ihn mit einer unzutreffenden Kardinalitätsgrundlage in Beziehung setzen und die Wirkung einer Statistikaktualisierung unter identischer Ergebnismenge prüfen.

## 2. Fachliche Kernaussage

**Evidenzklasse:** `DOKUMENTIERT` und `EMPIRISCH`

Sort- und Hashoperatoren verwenden Workspace Memory. Reicht der auf Basis der erwarteten Arbeitssatzgröße vergebene Grant nicht aus, können Arbeitssätze nach TempDB ausgelagert werden. `last_spills` in `sys.dm_exec_query_stats` beschreibt die zuletzt verschütteten Seiten eines beendeten Statements. Die Demo erzeugt zunächst eine korrekte Filterstatistik für 299.000 Zielzeilen, ersetzt den Datenbestand dann bei deaktivierter automatischer Statistikaktualisierung durch dieselbe Zielmenge, während die Statistik nur 1.000 Tabellenzeilen beschreibt, und aktualisiert die Statistik anschließend mit `FULLSCAN`.

## 3. Nichtziel

Die Demo definiert keinen universellen Memory-Grant-Schwellenwert und empfiehlt weder pauschale Grant-Hints noch eine globale Speichererhöhung. Sie behandelt globale Memory Pressure und `RESOURCE_SEMAPHORE` nicht als primäres Thema.

## 4. Voraussetzungen

SQL Server 2019 bis 2025, `CREATE DATABASE` und versionsgerechte Server-State-Sichtbarkeit. Mindestanforderungen sind 2 logische CPU-Kerne, 3 GB RAM und 600 MB freier Datenträgerspeicher. Es ist nur eine Instanz erforderlich.

## 5. Sicherheits- und Abbruchrahmen

Die Demo ist gelb, weil 299.000 breite Zielzeilen mehrfach sortiert und ein kontrollierter TempDB-Spill erzeugt werden. Das Harness verlangt `--confirm-isolated-lab`; die maximale Laufzeit beträgt 360 Sekunden. Jede Workloadabfrage verwendet `MAXDOP 1`. Es werden keine globalen Caches geleert, keine Serveroptionen verändert und keine fremden Statistikobjekte bearbeitet. Timeout und Cleanup folgen `FWK-008` und `FWK-010`.

## 6. Synthetisches Datenmodell

`lab.SpillData` enthält 300.000 Zeilen mit `FilterKey`, deterministischem Sortierschlüssel und 200 Byte breiter Nutzlast. 299.000 Zeilen besitzen `FilterKey = 1`. Die Baseline verwendet eine aktuelle Fullscan-Statistik. Für den Problemzustand werden die 299.000 Zielzeilen entfernt, die Statistik auf den verbleibenden 1.000 Zeilen aktualisiert und anschließend dieselben 299.000 Zielzeilen deterministisch wieder eingefügt. `NORECOMPUTE` hält diesen kontrolliert veralteten Statistikzustand bis zur Mitigation stabil.

## 7. Ablauf

| Phase | Datei | Zweck |
|---|---|---|
| Preflight | `00_Preflight.sql` | Version, Rechte und gelbe Sicherheitsbestätigung prüfen |
| Setup | `10_Setup.sql` | Testdatenbank, Daten und aktuelle Filterstatistik anlegen |
| Baseline | `20_Baseline.sql` | Sort mit korrekter Statistik und `last_spills = 0` messen |
| Demonstration | `30_Demonstration.sql` | identische Zielmenge bei Statistikstand von 1.000 Zeilen erzeugen und Sort ausführen |
| Observation | `40_Observation.sql` | Ergebnisequivalenz, Statistikzustand, Planform und Spill gemeinsam prüfen |
| Mitigation | `50_Mitigation.sql` | Filterstatistik mit `FULLSCAN` aktualisieren |
| Comparison | `60_Comparison.sql` | identische Abfrage mit aktueller Statistik und ohne Spill prüfen |
| Cleanup | `90_Cleanup.sql` | markierte Testdatenbank entfernen |

## 8. Erwartete Beobachtung

Baseline, Problemzustand und Vergleich liefern denselben Checksum-Wert über 299.000 Zielzeilen. In der Baseline beschreibt die Statistik 300.000 Tabellenzeilen, der Modification Counter ist 0 und `last_spills = 0`. Im Problemzustand beschreibt die Statistik nur 1.000 Tabellenzeilen, während mindestens 299.000 Änderungen offen sind; der Sort besitzt `last_spills > 0`. Nach `FULLSCAN` beschreibt die Statistik wieder 300.000 Tabellenzeilen, der Modification Counter ist 0 und der identische Sort besitzt `last_spills = 0`.

## 9. Interpretation

Ein Spill ist Runtime-Evidenz für unzureichenden nutzbaren Workspace des konkreten Operators. Die Demo belegt zusätzlich eine kontrollierte Ursache für den Undergrant: Die tatsächliche Zielmenge bleibt 299.000 Zeilen, während die Statistik im Problemzustand nur einen Tabellenstand von 1.000 Zeilen kennt. Die Beobachtung beweist nicht, dass jeder Spill durch veraltete Statistiken entsteht; geeignete Folgeanalysen müssen Schätzung, Operator, Grant, Parallelität und konkurrierenden Speicherbedarf gemeinsam prüfen.

## 10. Cleanup und Wiederherstellung

Statistikobjekt, Daten und Evidenztabelle liegen ausschließlich in der markierten Testdatenbank. `90_Cleanup.sql` entfernt die Datenbank nach vollständiger Markerprüfung. Ein Timeout führt über `FWK-010` in denselben Cleanup-Pfad.

## 11. Tests

Die Runtime-Matrix führt die Demo je Version zweimal aus und prüft identische Checksums, 299.000 tatsächliche Zielzeilen, Baseline mit Statistikstand 300.000/Modification Counter 0/Spill 0, Problemzustand mit Statistikstand 1.000/Modification Counter mindestens 299.000/positivem `last_spills`, Vergleich mit erneut aktueller Fullscan-Statistik und Spill 0 sowie vollständiges Cleanup. Es werden keine festen Laufzeit- oder TempDB-Größenverhältnisse verlangt.

## 12. Bekannte Grenzen

Die konkrete Spill-Seitenzahl hängt von verfügbarem Speicher, Engine-Build und internen Mindestgrants ab. Vertragsbestandteil ist nur die gemeinsam belegte Richtung `aktuelle Statistik und 0 Spill → veraltete Statistik und positiver Spill → aktuelle Statistik und 0 Spill`. Die Matrix verwendet offizielle Linux-Container; Windows- oder editionsspezifische Eigenschaften sind nicht Bestandteil dieser Demo.

## 13. Quellen

| Quellen-ID | Aussagebezug | Gültigkeitsbereich | Abrufdatum |
|---|---|---|---|
| `SRC-005` | Statistikaktualität, Sampling und Schätzungsgrundlage | SQL Server 2019–2025 | 2026-07-24 |
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
