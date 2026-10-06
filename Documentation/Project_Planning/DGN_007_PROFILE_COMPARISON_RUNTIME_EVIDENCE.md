# DGN-007 – Runtime-Nachweis des neutralen Profilvergleichs

| Merkmal | Wert |
|---|---|
| Status des Schnitts | `IMPLEMENTED` mit lokalem Runtime-Nachweis |
| Umfang | ausschließlich `DGN-007_PROFILE_COMPARISON`, Run-Token `AUTO` |
| Ausführungsdatum | 2026-10-07 Europe/Vienna (2026-10-06 UTC) |
| Repository-Basis | `6027e298b5f5266aed3e2196393864fc9b95a820` mit den Änderungen dieses PR |
| Infrastruktur | frische Linux-Docker-Wegwerfinstanzen, vier CPU-Kerne, 8 GB Container-Speicher, keine veröffentlichten Ports oder Host-Volumes |
| CI-Abgrenzung | lokale Runtime und Actions-Ergebnisse werden getrennt bewertet |

## Umfang und Messvertrag

Der neue Runner-Scope `--scope profile-comparison` führt das eigene Manifest
zweimal vollständig aus: Preflight, Setup, Datenassertion, Query-Store-Fenster,
Profilvergleich und Cleanup. Jede Phase muss `PASS/OK` liefern. Der bestehende
Datenmodell-Default und der Fensterscope bleiben eigenständige Verträge.
Das reguläre Budget bleibt 180 Sekunden, Cleanup unabhängig 60 Sekunden.
Der Vergleich besitzt zehn Sekunden externen Prozessschutz und acht Sekunden
interne Deadline vor der ersten Ausgabe und vor der abschließenden Summary.

Der Vergleich liest ausschließlich die bereits normalisierte Capture-Evidenz
aus `lab.IncidentProfile`. Marker, Versions-/Compatibility-Vertrag, zwei
disjunkte Katalogintervalle, dieselben vier Parameterpaare und je vier reguläre
Suchausführungen werden erneut geprüft. Parentqueries bleiben auf die eigene
markierte Prozedur beschränkt; PSP-Varianten werden versionsgebunden dynamisch
aufgelöst. Erzwungene Pläne und unterstützte Query-Store-Hints sind ausgeschlossen.
Der Live-Katalogabgleich revalidiert IDs, Ausführungszahlen und erste/letzte
Ausführungszeiten. Er vergleicht die gespeicherten Metrikwerte nicht unabhängig
mit neu aggregierten Live-Mittelwerten und ist kein Manipulationsnachweis.
Die Phase verwendet nur temporäre Tabellen. Sie erzeugt keine zusätzliche
Suchlast, Neukompilierung der Suchprozedur, Flushes oder direkten Änderungen
an persistenten Labtabellen und Query-Store-Konfiguration. Beobachtungsqueries
können selbst kompiliert und unter Capture ALL erfasst werden; sie bleiben
außerhalb des markierten Suchscope.

Je Fenster werden Duration, CPU, Logical Reads und Rows mit
`SUM(ExecutionCount * Mittelwert) / SUM(ExecutionCount)` gewichtet. Die Ausgabe
enthält T0, T1, Delta `T1-T0` und Ratio `T1/NULLIF(T0,0)`. Gültige Nullmessungen
(0) bleiben 0; `BaselineZero=1` erklärt die nicht definierte Ratio bei T0=0.
Fehlende oder negative Metriken werden zurückgewiesen. Die Plananzahl zählt
nur tatsächlich ausgeführte Pläne je Fenster, einschließlich eigener Varianten.
Es gibt keine Mindestplananzahl, erwartete Richtung oder Performance-Schwelle.
Je Fenster bleiben 4.229 Ergebniszeilen beziehungsweise 1.057,25 gewichtete
Rows je Ausführung erforderlich. Die Toleranz `0.000001` betrifft ausschließlich
die Rundung der `float`-Aggregation, nicht zusätzliche oder fehlende Last.

Duration und CPU beziehen sich auf Statement-Runtime in Mikrosekunden; Logical
Reads auf 8-KB-Pages. Compilezeit und Clientlatenz werden nicht daraus abgeleitet.
Technische Primärquelle, geprüft am 2026-10-06:
[Query-Store-Runtime-Stats](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17),
[PSP-Varianten](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-variant?view=sql-server-ver17),
[Query-Store-Hints](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-hints-transact-sql?view=sql-server-ver17).
Die dokumentierte Aggregation aktiver Disk-/Speicherzeilen bleibt im vorgelagerten
[Fenstervertrag](DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md) maßgeblich.

## Lokale Matrix und Cleanup

Die lokale Prüfung verwendet die vollständige CI-Reihenfolge auf jedem frisch
erzeugten Container: zweimal Datenmodell, zweimal Fenster, zweimal Profilvergleich.
Es laufen höchstens drei eigene Instanzen parallel, jede mit genau einer
SQL-Session. Bestehende Ressourcen werden nicht als Testziele verwendet.
Nach jedem Lifecycle folgt die unabhängige Datenbankabwesenheitsprüfung gegen
`master`. Vor Containerabbau werden ursprüngliche Container-ID und eindeutiges
Eigentumslabel geprüft; anschließend wird die ID-Abwesenheit separat bestätigt.

Alle 18 Lifecycles in dieser Reihenfolge bestanden einschließlich unabhängiger
Datenbankabwesenheitsprüfung. Die drei zugehörigen Container wurden nach
Eigentumsprüfung einschließlich anonymer Volumes entfernt; die ursprünglichen
Container-IDs waren danach unabhängig nicht mehr vorhanden.

| SQL Server | ProductVersion | Engine Major | Compatibility Level | Profilvergleich-Lifecycles | Ergebnis |
|---|---|---:|---:|---:|---|
| 2019 | `15.0.4490.9` | 15 | 150 | 2 | `PASS/OK` |
| 2022 | `16.0.4265.3` | 16 | 160 | 2 | `PASS/OK` |
| 2025 | `17.0.4075.5` | 17 | 170 | 2 | `PASS/OK` |

Die lokal vorhandenen offiziellen Images wurden ohne Änderung bestehender
Tags verwendet. Unveränderliche Image-Digests:

| SQL Server | Image-Digest |
|---|---|
| 2019 | `mcr.microsoft.com/mssql/server@sha256:ef0b8db33970ecd01bed49c3a84a1d083c435a9891718df619298b67b352e74a` |
| 2022 | `mcr.microsoft.com/mssql/server@sha256:ba4c8329f48fb8f02e1416be6a930ebfd71268caee78aa985f3af4315e457c89` |
| 2025 | `mcr.microsoft.com/mssql/server@sha256:4bab24f36c1ecd48e85f7d37df26e6bf301641d84c3fe652f9a0dcc947d512e1` |

Die quantitative Diagnostik ergänzt ausschließlich im lokalen, nicht versionierten
Aufruf die interaktive Harness-Ausgabe. Der normale Runner unterdrückt weiterhin
SQL-Phasenausgaben. Aus den transienten Resultsets werden ausschließlich feste
`DGN007_PROFILE_*`-Kennungen und numerische Metriken übernommen. Rohoutput,
Querytext, Plan-XML, Zugangsdaten und reale Hostinformationen werden nicht
als Repository-Artefakte gespeichert.

Für die quantitative Kontrolle wurden 2019 und 2022 zusätzlich je zweimal
auf neuen eigenen Instanzen ausgeführt. Der erste lokale Diagnosefilter hatte
Framework-Präfix und Pipe-Trennzeichen nicht berücksichtigt und gab deshalb
keine Metrikzeilen weiter; die SQL-Verträge und Cleanup bestanden dennoch.
Diese früheren Läufe zählen als Lifecycle-, nicht als sichtbarer Ausgabenachweis.
Der korrigierte Filter übernimmt ausschließlich die festen skalaren Reports.
Die zusätzliche quantitative Kontrolle bestand einschließlich Cleanup.
Beide zusätzlichen Container wurden mit derselben ID-/Labelprüfung entfernt;
ihre Abwesenheit wurde unabhängig bestätigt. Damit bestanden insgesamt 22
lokale Lifecycles und der Abbau aller fünf selbst erzeugten Instanzen.

Empirische Messwerte der zusätzlichen 2019-/2022-Kontrolle und der beiden
2025-Profilvergleiche aus der vollständigen Reihenfolge; Ratios sind nur
zur Darstellung auf sechs Nachkommastellen gerundet. Sie sind keine Golden
Values oder Performance-Erwartungen. Je Fenster wurden vier Suchausführungen,
ein tatsächlich ausgeführter Plan und 4.229 Ergebniszeilen erfasst.

| SQL Server | Lauf | CPU T0 / T1 (µs) | Duration T0 / T1 (µs) | Logical Reads T0 / T1 (Pages) | CPU-Ratio | Reads-Ratio |
|---|---:|---|---|---|---:|---:|
| 2019 | 1 | 6999,25 / 11431,25 | 7000 / 11432,5 | 5897 / 3388,5 | 1,633211 | 0,574614 |
| 2019 | 2 | 7319,75 / 10060 | 7320,5 / 10061 | 5896 / 3380 | 1,374364 | 0,573270 |
| 2022 | 1 | 6865,75 / 13526,5 | 6866,5 / 13528 | 5906,5 / 3389,25 | 1,970142 | 0,573817 |
| 2022 | 2 | 6310 / 10330 | 6310,5 / 10331 | 5906,5 / 3379,5 | 1,637084 | 0,572166 |
| 2025 | 1 | 6871,75 / 9224 | 6872,5 / 9224,25 | 5897,75 / 3386,25 | 1,342307 | 0,574160 |
| 2025 | 2 | 6549 / 10072,5 | 6549,5 / 10073,25 | 5900,25 / 3384 | 1,538021 | 0,573535 |

Diese Läufe zeigen unterschiedliche Richtungen für CPU und Reads. Der
Plananzahlwert eins erfüllt den neutralen Vertrag. Die Beobachtung ist kein
unabhängiger Ursachennachweis und keine Freigabe des Incident-Backlogpunkts.
Alle dargestellten Runtime-Baselines waren positiv. Der Zero-Baseline-Zweig
ist ausschließlich durch die unten beschriebene numerische Fixture geprüft.

## Statische Gegenprüfungen und Statusgrenzen

30 Runner-Tests prüfen die drei unveränderlichen Verträge, exakte Phasenfolgen,
Cleanupvorrang und fehlende, doppelte oder nicht erfolgreiche Ergebnisse.
Zehn numerische Fixturetests führen extrahierte Abschnitte des tatsächlichen
Vergleichs-SQL mit SQLite aus. Sie prüfen ungleiche Planhäufigkeiten, einen
einzelnen ausgeführten Plan, Null-Baseline, negative Deltas, identische Profile,
NULL-/negative Metriken, Counts, fremde Queries, Parameterpaare, Intervalle und
Rows. Quelltextmutationen prüfen entfernte NULL-/Deadline-/RETURN-Guards.
Diese Fixtures sind kein SQL-Server-Runtime-Nachweis; SQL-Syntax und
Katalogverhalten benötigen die getrennte Runtime-Matrix.

Der Vergleich ist eine Voraussetzung der nächsten Incidentarbeit. Ein PASS
belegt weder Performanceverschlechterung noch Ursache oder Incidentreproduktion.
Die bisherige Compile-/Ausführungsreihenfolge und mehrere beobachtete Pläne
allein erlauben diese Schlussfolgerung nicht. Die ältere Beobachtungsbedingung,
kontrollierte Incidentreproduktion, T2, Alternativhypothesen, Mitigation und
XE-Abnahme bleiben offen. Der übergeordnete DGN-007-Status bleibt
`IMPLEMENTED_STATIC_SLICE_B`; keine Szenariopromotion, vollständige
Capstone-Matrix, Docker-/Podman-Parität oder `READY_FOR_USER`-Übergabe folgt daraus.
