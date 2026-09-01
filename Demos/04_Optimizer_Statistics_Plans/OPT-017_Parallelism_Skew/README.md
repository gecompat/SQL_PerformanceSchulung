# OPT-017 – Parallele Planbereiche und Skew

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Runtime-Abnahme | [Actions-Lauf 33447840232](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33447840232); je zwei `PASS/OK` auf SQL Server 2019, 2022 und 2025 |
| Sicherheitsstufe | `YELLOW` |

## 1. Lernziel

Actual DOP, Exchanges und Threadarbeit in einem parallelen Actual Plan lesen und ungleich verteilte Arbeit von einer bloßen DOP-Zahl unterscheiden.

## 2. Fachliche Kernaussage

Parallelität garantiert keine gleichmäßige Arbeit. Ein Exchange verteilt Daten zwischen Planbereichen; die tatsächliche Arbeit muss je Thread und zusammen mit Zeilen, Reads, CPU und Duration interpretiert werden. Operatorzeiten werden nicht ungeprüft addiert.

## 3. Nichtziel

Die Demo empfiehlt weder einen globalen `MAXDOP`-Wert noch eine universelle Skew-Schwelle. Sie bewertet keine produktiven Pläne und ändert keine Instanzkonfiguration.

## 4. Voraussetzungen

- SQL Server 2019, 2022 oder 2025;
- isolierte Wegwerfinstanz mit mindestens vier sichtbaren logischen Kernen;
- empfohlen 8 GB Arbeitsspeicher und ausreichend Datenbank-/TempDB-Platz;
- `CREATE DATABASE` und Zugriff auf die planbezogene Runtime-Evidenz.

## 5. Sicherheits- und Abbruchrahmen

`OPT-017` ist `YELLOW` und erfordert `--confirm-isolated-lab`. Das Manifest begrenzt den Gesamtlauf auf 600 Sekunden; jede Lastphase besitzt ein engeres Zeitbudget. `lab.DemoControl.StopRequested` ist der kooperative Kill-Switch vor einer Lastabfrage. Ein abgebrochener Clientlauf wird vom Harness durch das markergeprüfte Cleanup beendet.

## 6. Synthetisches Datenmodell

Das Profil `PARALLEL` enthält je 600.000 Zeilen in zwei Verteilungen. `B` verteilt 4.096 Gruppenschlüssel annähernd gleichmäßig; `S` konzentriert 95 Prozent der Zeilen auf einen Schlüssel. Die Aggregation verwendet einen fest auf 16 Zeilen begrenzten synthetischen Multiplikator und normalisiert Anzahl und Messwertsumme anschließend wieder. Damit überschreitet die Abfrage auch auf kompakten Testinstanzen reproduzierbar die Parallelitätsschwelle, ohne Ergebnismenge oder Datenbestand zu vergrößern. Zeilenzahl und Messwertsumme sind identisch. Alle Daten sind deterministisch und synthetisch.

## 7. Ablauf

1. Preflight prüft Version, Bestätigung, Zeitbudget, Berechtigung, sichtbare Kerne und effektive DOP.
2. Setup erzeugt die markergebundene Datenbank und aktiviert `LAST_QUERY_PLAN_STATS` nur dort.
3. Baseline aggregiert die balancierte Verteilung mit querylokalem `MAXDOP 4`.
4. Demonstration führt denselben Abfragetyp auf der konzentrierten Verteilung aus.
5. Observation liest Actual DOP, Exchanges und positive Threadzeilen aus dem Actual-Plan-XML.
6. Mitigation führt ausschließlich eine serielle Gegenprobe mit `MAXDOP 1` aus.
7. Comparison prüft Ergebnisequivalenz und berichtet das Verhältnis größter zu kleinster positiver Threadarbeit.

## 8. Erwartete Beobachtung

Ein geeigneter Host erzeugt Actual DOP mindestens 2, mindestens einen Exchange und Arbeit auf mindestens zwei Threads. Das Skew-Verhältnis wird als Messwert ausgegeben, nicht gegen eine hardwareunabhängige Golden-Schwelle geprüft.

## 9. Interpretation

Eine konzentrierte Verteilung kann einen einzelnen Consumer-Thread dominieren und dadurch den parallelen Bereich begrenzen. DOP allein erklärt weder Laufzeit noch Grant. Die serielle Gegenprobe isoliert die Planform, ist aber keine allgemeine Gegenmaßnahme.

## 10. Cleanup und Wiederherstellung

Cleanup löscht ausschließlich die Datenbank `SQLPERF_LAB_OPT017_<RunToken>`, nachdem Projekt-, Vertrags-, Demo- und Run-Marker übereinstimmen. Datenbankbezogene Konfigurationen verschwinden damit vollständig.

## 11. Tests

Der statische Vertrag prüft Phasen, Safety, Datenprofile, `MAXDOP`, Plan-XML-Marker, Kill-Switch, Skipcodes und verbotene globale Eingriffe. Der Runtime-Runner führt die Demo je Engine zweimal aus und prüft nach jedem Lauf den Cleanup.

## 12. Bekannte Grenzen

Ressourcenarme Hosts liefern kontrolliert `SKIP_RESOURCE_PROFILE`; eine nicht erzeugte parallele Planform liefert `SKIP_EVIDENCE_MISSING`. Ein schwach sichtbarer Skew bleibt `WARN_EMPIRICAL_VARIANCE`. Keiner dieser Ausgänge ersetzt die Kernevidenz für eine Runtimefreigabe.

## 13. Quellen

- `SRC-001` – Microsoft Showplan/SQL-Server-Dokumentation
- `SRC-031` – Execution-Plan-Referenz
- `SRC-043` – parallele Branches und Threads
- `SRC-044` – Grenzen operatorbezogener Zeitwerte

## 14. Traceability

`OPT-017` gehört zu `LAB-VP1`, `ADV-004`, `W-ADV-017`, `LO-M02-09` sowie `ADV-CLM-007`, `ADV-CLM-008` und `ADV-CLM-026`.
