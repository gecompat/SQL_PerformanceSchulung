# Review – ADV-008 Runtime-Schnitt OPT-015 und OPT-016

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-07-26 |
| Pull Request | `#20` |
| Ausgangscommit auf `origin/main` | `6e914da6ab87e4ba17a354bc6e8c4d1c06446396` |
| Arbeitspaket | `ADV-008` – erster Implementierungs- und Runtime-Schnitt |
| Demos | `OPT-015`, `OPT-016` |
| PowerPoint geändert | nein |

## 1. Umfang

Der Schnitt implementiert zwei grüne Vertiefungsdemos aus LAB-VP1 als eigenständige, vollständig ausführbare Demo-Bündel. Jede Demo besitzt Preflight, Setup, Baseline, Demonstration, Observation, Mitigation, Comparison und Cleanup sowie eine eigene Quellen-, Claim-, Lernziel- und Testprofilzuordnung.

Die Implementierung verwendet das bestehende Framework und ausschließlich markergebundene synthetische Testdatenbanken. Plan XML wird während der Ausführung ausgewertet, aber nicht im Repository, in Tabellen oder Diagnoseartefakten persistiert. Persistiert werden nur normalisierte Plan- und Runtimeattribute innerhalb der kurzlebigen Testdatenbank.

## 2. OPT-015 – Planweite und operatorbezogene Eigenschaften

`OPT-015` implementiert einen synthetischen Statistikfall mit folgenden Zuständen:

1. Baseline mit 200.000 Zeilen in 20 gleichmäßig verteilten Gruppen und per Fullscan erfasster Indexstatistik.
2. Problemzustand mit zusätzlichen 60.000 Zeilen für die zuvor nicht vorhandene Gruppe 999 bei unveränderter Statistik.
3. Gezielte Gegenmaßnahme durch Aktualisierung ausschließlich der Statistik `IX_WorkItem_EntityGroupId`.
4. Vergleich mit derselben Ergebnismenge und kleinerem absoluten Schätzfehler.

Die normalisierte Evidenz umfasst Query Hash, Statementkosten, Estimated Rows, Actual Rows, Actual Rows Read, Number of Executions, Statistics Usage, Zugriffsoperator, Logical Reads, Worker Time und Elapsed Time. Geschätzte Kosten werden nicht als gemessene Laufzeit interpretiert.

## 3. OPT-016 – Rebind, Rewind, Outer References und Spools

`OPT-016` implementiert zwei äußere Schlüsselprofile:

- Profil `H`: 5.000 Anforderungen mit zehn wiederholten Gruppenschlüsseln.
- Profil `L`: 20 Anforderungen mit jeweils unterschiedlichem Gruppenschlüssel.

Der hintfreie Problemzustand entfernt den unterstützenden Detailindex und erzeugte auf SQL Server 2019, 2022 und 2025 eine Performance Spool. Erfasst werden Nested Loops, Outer References, Spoolart, Actual Rebinds, Actual Rewinds, Executions, tatsächliche Zeilen und Laufzeitmetriken.

Die erste Runtimeausführung zeigte, dass SQL Server selbst mit passendem Index bereits eine Performance Spool wählen kann. Der ursprüngliche Baselinevertrag „Index vorhanden bedeutet keine Spool“ wurde daher verworfen. Baseline und Vergleich verwenden `NO_PERFORMANCE_SPOOL` ausschließlich als explizite kontrollierte Gegenprobe; der Problemzustand bleibt hintfrei. Der Hint wird nicht als allgemeine Tuningmaßnahme dargestellt.

## 4. Technische Korrekturen während der Runtimeabnahme

Die reale Matrix identifizierte zwei implementierungsrelevante Punkte:

1. Der dynamische Datenbankkontext für `LAST_QUERY_PLAN_STATS` musste vollständig in einer Variablen aufgebaut und über `sys.sp_executesql` ausgeführt werden. Ein Funktionsaufruf direkt im dynamischen `EXEC(...)`-Ausdruck war nicht zulässig.
2. Die Capture-Prozeduren mit XML-Datentypmethoden mussten explizit unter `QUOTED_IDENTIFIER ON` und `ANSI_NULLS ON` erzeugt werden.

Beide Korrekturen gelten identisch für SQL Server 2019, 2022 und 2025. Die abschließende Matrix bestätigte den korrigierten Vertrag.

## 5. Sicherheits- und Datenschutzstatus

- Sicherheitsstufe beider Demos: Grün.
- Keine globale Cacheleerung.
- Keine instanzweite Konfigurationsänderung.
- Keine undokumentierten Trace Flags.
- `LAST_QUERY_PLAN_STATS` ausschließlich datenbankbezogen.
- Objektbezogene Recompilation über `sys.sp_recompile`.
- Vollständige Markerprüfung vor `DROP DATABASE`.
- Ephemere Container ohne Host-Port und ohne persistentes Volume.
- Ausschließlich deterministische synthetische Daten.
- Keine realen Host-, Kunden-, Benutzer-, Zugangs- oder Diagnosedaten.

## 6. Automatisierte Abnahme

Der Workflow `ADV-008 OPT-015 and OPT-016 runtime`, Lauf `30218932252`, bestand:

- statische Vertragsprüfung,
- vollständigen Repository-Privacy-Scan,
- SQL Server 2019 / Compatibility Level 150,
- SQL Server 2022 / Compatibility Level 160,
- SQL Server 2025 / Compatibility Level 170.

Jede Demo wurde je Version zweimal vollständig ausgeführt. Dies entspricht zwölf erfolgreichen Demo-Läufen. Nach jedem Lauf prüfte der Runtime-Treiber unabhängig über `master`, dass die markergebundene Datenbank nicht mehr vorhanden war.

Zusätzlich erfolgreich auf demselben Branchstand:

- `Framework SQL matrix`, Lauf `30218932272`,
- `Framework contracts`, Lauf `30218932273`,
- `Curriculum and privacy validation`, Lauf `30218932248`.

## 7. Abnahmekriterien

`OPT-015` ist bestanden, wenn:

- Baseline, Problem und Vergleich vollständige normalisierte Planevidenz besitzen,
- Problem und Vergleich dieselbe 60.000-Zeilen-Ergebnismenge und Checksumme liefern,
- die relevante Statistik per Fullscan aktualisiert wurde,
- der absolute Schätzfehler nach der Aktualisierung kleiner ist,
- Cleanup vollständig ist.

`OPT-016` ist bestanden, wenn:

- Baseline und Vergleich Outer References und einen direkten seekfähigen Zugriff ohne Performance Spool besitzen,
- der hintfreie Problemzustand die erwartete Spool-Planform oder einen begründeten Planform-Skip liefert,
- das High-Reuse-Profil mehr Rewinds als das Unique-Key-Profil besitzt,
- Baseline, Problem und Vergleich für Profil `H` dieselbe Ergebnismenge liefern,
- Cleanup vollständig ist.

Die Referenzmatrix erfüllte alle Kriterien ohne Skip.

## 8. Statusgrenze

`OPT-015` und `OPT-016` sind `VALIDATED`. `ADV-008` bleibt insgesamt `IN_PROGRESS`, da weitere Vertiefungsdemos noch nicht implementiert sind. Gate V3 ist damit `PARTIAL`.

## 9. Nächster Schnitt

Der nächste abhängige Implementierungsschnitt umfasst `QRY-013` und `QRY-004_CLASSIC_AND_DYNAMIC`. Query Store und Extended Events werden vor `DGN-007` als zentrale Diagnosepfade validiert. `RES-003` bleibt der letzte und separat freizugebende rote Schnitt.
