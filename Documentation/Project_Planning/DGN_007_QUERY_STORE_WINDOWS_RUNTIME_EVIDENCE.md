# DGN-007 – Runtime-Nachweis der Query-Store-Fenster

| Merkmal | Wert |
|---|---|
| Status des Schnitts | `IMPLEMENTED` mit lokalem Runtime-Nachweis |
| Umfang | ausschließlich `DGN-007_QUERY_STORE_WINDOWS`, Run-Token `AUTO` |
| Ausführungsdatum | 2026-10-06 |
| Repository-Basis | `420f1d0f84c550b8fbda81ccd58b709a4c36d6e3` mit den Änderungen dieses PR |
| Infrastruktur | frische Linux-Docker-Wegwerfinstanzen, vier CPU-Kerne und 8 GB Container-Speicher; keine veröffentlichten Ports oder Host-Volumes |
| CI-Abgrenzung | lokale Evidenz und Actions-Ergebnisse werden getrennt bewertet |

## Umfang des Nachweises

Der Runner wählt ausdrücklich `--scope query-store-windows` und führt
`windows.manifest.json` genau zweimal aus. Ohne Scope bleibt der bisherige
Datenmodellvertrag ausgewählt. Preflight, Setup, Datenassertion,
Query-Store-Fenster und Cleanup müssen jeweils `PASS/OK` liefern. Nach jedem
Lifecycle prüft eine unabhängige Abfrage gegen `master` die Abwesenheit der
eigenen AUTO-Datenbank; die eigenen Container werden danach einschließlich
anonymer Volumes entfernt und ihre Abwesenheit separat geprüft.

Der Fenstervertrag beginnt nach den vier Datenassertionsrequests. Vor T0 lässt der Batch
das nach der Aktivierung beobachtete aktuelle Intervall aus. Capturewerte
werden ausschließlich aus den anschließend belegten T0-/T1-Intervall-IDs
übernommen; die früheren Datenassertionsrequests zählen nicht zu diesen Fenstern.
T0 und T1 belegen zwei unterschiedliche, nicht überlappende tatsächliche
Query-Store-Katalogintervalle. Je Fenster werden die vier Parameterpaare
`(8,3)`, `(1,3)`, `(5,3)` und `(1,1)` genau einmal ausgeführt. T0 beginnt mit
`(8,3)`, T1 mit `(1,3)` nach objektbezogener Neukompilierung ausschließlich
der eigenen markierten Suchprozedur. Suchcounts sind 228, 2.286, 1.144 und 571;
Ergebnismengen werden vollständig in beide Richtungen verglichen. Je Fenster
werden vier neue Requests und genau vier reguläre Query-Store-Suchausführungen
belegt, insgesamt zwölf Requests einschließlich der Datenassertion.

Query Store wird nur in der eigenen frischen Datenbank auf READ_WRITE,
Capture ALL, 128 MB, einminütige Intervalle und 60 Sekunden Flush eingestellt.
Der vollständige Konfigurationssnapshot liegt vor der ersten Änderung in
`lab.QueryStoreBaseline`. Dokumentierte FWK-007-Abweichung: Das markergebundene
DROP restituiert den ursprünglichen Zustand einer abwesenden Datenbank
vollständig; eine Wiederherstellung in einer vorhandenen Datenbank ist kein
Bestandteil dieses Vertrags.

Parentqueries werden auf ObjectId und den eigenen Statementmarker begrenzt;
PSP-Varianten werden ausschließlich auf unterstützten Engines dynamisch
aufgelöst. Aktive Runtime-Stats können mehrere Disk-/Speicherzeilen haben:
Counts werden summiert und Mittelwerte nach Ausführungsanzahl gewichtet.
Der Flush unterstützt Sichtbarkeit und belegt keinen Intervallwechsel.
Technische Primärquellen, geprüft am 2026-10-06:
[Runtime-Stats](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17),
[Flush](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-flush-db-transact-sql?view=sql-server-ver17),
[PSP-Varianten](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-variant?view=sql-server-ver16).
Diese technische Evidenz verändert keine Lehrinhaltsfreigabe.

## Matrix

Die finale Korrektur wurde pro Version in der vollständigen CI-Reihenfolge
geprüft: zweimal Datenmodell, danach zweimal Fenster auf demselben bereinigten
Container. Die zusätzlichen Datenmodell-Vorläufe bestanden ebenfalls; für
alle zwölf Lifecycles ist die Datenbankabwesenheit unabhängig bestätigt.

| SQL Server | ProductVersion | Engine Major | Compatibility Level | Fenster-Lifecycles | Ergebnis | Fenster-Abwesenheitsprüfungen |
|---|---|---:|---:|---:|---|---:|
| 2019 | `15.0.4490.9` | 15 | 150 | 2 | `PASS/OK` | 2 × bestanden |
| 2022 | `16.0.4265.3` | 16 | 160 | 2 | `PASS/OK` | 2 × bestanden |
| 2025 | `17.0.4075.5` | 17 | 170 | 2 | `PASS/OK` | 2 × bestanden |

Alle sechs finalen Fenster-Lifecycles bestanden mit den eingefrorenen dynamischen
Kontrollqueries. Alle selbst erzeugten Container wurden nach Eigentumsprüfung
entfernt und ihre Abwesenheit unabhängig bestätigt. Für 2019 wurde der konkrete
Digest aus dem fehlgeschlagenen CI-Lauf neu geladen, ohne vorhandene Tags
umzubinden. 2022 und 2025 verwenden vorhandene Images ohne erneuten Pull.
Die unveränderlichen Digests lauten:

| SQL Server | Image-Digest |
|---|---|
| 2019 | `mcr.microsoft.com/mssql/server@sha256:ef0b8db33970ecd01bed49c3a84a1d083c435a9891718df619298b67b352e74a` |
| 2022 | `mcr.microsoft.com/mssql/server@sha256:ba4c8329f48fb8f02e1416be6a930ebfd71268caee78aa985f3af4315e457c89` |
| 2025 | `mcr.microsoft.com/mssql/server@sha256:4bab24f36c1ecd48e85f7d37df26e6bf301641d84c3fe652f9a0dcc947d512e1` |

## Fehlerprüfung und Grenzen

Ein erster Versuch auf SQL Server 2019 bestand RUN_1, endete bei RUN_2 jedoch
als `FAIL_TIMEOUT`. Unabhängiger Datenbankabbau und Containerabbau bestanden.
Eine anschließende Diagnose bestätigte den Timeout bereits bei der ersten
Intervallprobe des zweiten Laufs: Ohne erfassbare Ausführung war kein
aktuelles Intervall sichtbar. Beide Versuche zählen nicht als vollständige
positive Matrixnachweise.

Die Korrektur ergänzt vor den initialen und folgenden Intervallproben eine
Kontrollabfrage über zwölf synthetische Gruppenzeilen und einen Flush. Sie
verändert weder die Suchprozedur noch Requestlog oder Ergebnismengen und liegt
außerhalb des markierten Parent-/Variant-Scope. Deadlines werden vor und nach
der Probe geprüft. Die tatsächlichen Kataloggrenzen bleiben unverändert. Die
korrigierte Kontrollquery-/Flush-Fassung wurde separat in der Matrix geprüft.
Eine Materialisierungswirkung ist eine Inferenz aus der Diagnose, keine
dokumentierte Garantie einer Intervallrotation durch Flush.

Der erste CI-Lauf am Head `b62eaad`
([Actions 37530007591](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37530007591))
bestand auf 2022 und 2025; auf 2019 scheiterte der zweite Fenster-Lifecycle
erneut am Timeout. Die vorgeschalteten Datenmodellläufe und der Infrastrukturabbau
bestanden. Eine lokale Wiederholung der vollständigen CI-Reihenfolge
(zweimal Datenmodell vor zweimal Fenstern) reproduzierte auf 2019 den fehlenden
aktuellen Intervallkatalog im zweiten Fensterlauf. Die vorher erfolgreiche
Matrix mit statischem Kontrollquery ist deshalb kein Nachweis der finalen Fassung.

Die finale Korrektur verwendet für beide Kontrollabfragen feste
`sp_executesql`-Batches mit gebundenem `bigint OUTPUT`. Dokumentiert ist deren
separate Kompilierung erst beim Aufruf, hier nach Query-Store-Aktivierung:
[sp_executesql](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-executesql-transact-sql?view=sql-server-ver17).
Eine Vorabkompilierung des früheren statischen Queries bleibt eine mögliche
Erklärung, keine nachgewiesene Kausalursache. Die vollständige Reihenfolge
mit den zwei vorgeschalteten Datenmodellläufen wurde mit der finalen Fassung
erneut erfolgreich geprüft.

Die internen Poll- und Phasendeadlines melden strukturiert `FAIL_TIMEOUT` und
beenden den SQL-Batch; das Framework versucht danach Cleanup. Das reguläre
Budget bleibt 180 Sekunden, die Fensterphase 150 Sekunden mit interner
145-Sekunden-Grenze, Cleanup unabhängig 60 Sekunden. 26 Runner-Selbsttests und
statische Negativkontrollen prüfen unter anderem Scope-Dispatch, fehlende oder
doppelte Phasen, Warnungen, Timeouts, Eigentumsgrenzen und Cleanupvorrang.
Der Prozessabbruchtest mit Linux-Nachfahren läuft im CI; die lokalen Prüfungen
laufen auf Windows. Harte Host-Abbrüche sind kein Cleanupnachweis.

Die Labtabellen enthalten nur Konfiguration, IDs, Zeitgrenzen, Counts und
skalare Metriken. Keine Zugangsdaten, Hostnamen, Rohoutputs, Querytexte oder
Plan-XML werden als Repository-Artefakte gespeichert. Bereits vorhandene
Ressourcen sind keine Testziele.

Ein PASS belegt keine unterschiedlichen Pläne, Planregression, Performance-
verschlechterung oder Incidentreproduktion. PSP bleibt aktiviert. T2,
Alternativhypothesen, reversible Mitigation, Vergleich, XE-Abnahme und die
vollständige Capstone-Matrix bleiben offen. Der übergeordnete DGN-007-Status
bleibt `IMPLEMENTED_STATIC_SLICE_B`; keine Szenariopromotion,
Docker-/Podman-Parität, Windows-SQL-Runtime, Katalogaufnahme oder
`READY_FOR_USER`-Übergabe folgt aus diesem Nachweis.
