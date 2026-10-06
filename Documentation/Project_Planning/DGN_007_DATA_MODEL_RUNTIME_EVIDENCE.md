# DGN-007 – lokaler Runtime-Nachweis des Datenmodells

| Merkmal | Wert |
|---|---|
| Status des Schnitts | `IMPLEMENTED` mit lokalem Runtime-Nachweis |
| Umfang | ausschließlich `DGN-007_DATA_MODEL`, Run-Token `AUTO` |
| Ausführungsdatum | 2026-10-06 |
| Repository-Basis | `8b49b7788228e483e4f4021a078e6dc7b07e11d0` mit den Änderungen dieses PR |
| Infrastruktur | frische lokale Linux-Docker-Wegwerfinstanzen, jeweils vier CPU-Kerne und 8 GB Container-Speicher, keine veröffentlichten Ports oder Host-Volumes |
| Actions-Nachweis | dieser Bericht dokumentiert lokale Läufe; der neue Datenmodellworkflow liefert davon getrennte CI-Ergebnisse |

## Matrix und reproduzierbarer Umfang

Der Runner `Tests/Runtime/run_dgn007_automated_setup.py` wurde je Version mit
explizitem Container, erwartetem Engine Major und bestätigter Wegwerfinstanz
ausgeführt. Jeder Aufruf führte das bestehende `setup.manifest.json` genau
zweimal aus. Preflight, Setup, Datenassertion und Cleanup mussten jeweils
`PASS/OK` liefern. Nach jedem vollständigen Lifecycle bestätigte eine getrennte
Abfrage gegen `master` unabhängig, dass `SQLPERF_LAB_DGN007_AUTO` nicht existiert.

| SQL Server | ProductVersion | Engine Major | Compatibility Level | vollständige Lifecycles | Ergebnis | Abwesenheitsprüfungen |
|---|---|---:|---:|---:|---|---:|
| 2019 | `15.0.4480.2` | 15 | 150 | 2 | `PASS/OK` | 2 × bestanden |
| 2022 | `16.0.4265.3` | 16 | 160 | 2 | `PASS/OK` | 2 × bestanden |
| 2025 | `17.0.4075.5` | 17 | 170 | 2 | `PASS/OK` | 2 × bestanden |

Für alle sechs Lifecycles sind 12 Gruppen, 24.000 Faktzeilen, 72.000 Details,
die ItemId-Domäne, feste Gruppenmengen und deterministische Zuordnungen geprüft.
Die vier Suchklassen `(8,3)`, `(1,3)`, `(5,3)` und `(1,1)` liefern exakt
228, 2.286, 1.144 beziehungsweise 571 Zeilen. Bidirektionaler Mengenvergleich,
Detailcount, Gruppenlabel und die vier protokollierten Requestpaare sind geprüft.
Die Ausgabeordnung des Resultstreams ist ausdrücklich kein Laufnachweis.

Verwendet wurden vorhandene Images mit den Tags `2019-latest`, `2022-latest`
und `2025-latest`; für diesen lokalen Nachweis erfolgte kein erneuter Pull.
Die unveränderlichen Digests lauten:

| SQL Server | Image-Digest |
|---|---|
| 2019 | `mcr.microsoft.com/mssql/server@sha256:46f719fd3457d4e7e8e5845fe00c35c20e7bae7ff1e8b9fe595f2a81029f5ba8` |
| 2022 | `mcr.microsoft.com/mssql/server@sha256:ba4c8329f48fb8f02e1416be6a930ebfd71268caee78aa985f3af4315e457c89` |
| 2025 | `mcr.microsoft.com/mssql/server@sha256:4bab24f36c1ecd48e85f7d37df26e6bf301641d84c3fe652f9a0dcc947d512e1` |

## Fehlerprüfung und Bereinigung

Ein erster Matrixversuch bestand auf 2019 und 2022, wies SQL Server 2025
jedoch vor dem Setup ab: Die neue Editionsbezeichnung begann nicht mit
`Developer`. Nach Umstellung auf die dokumentierten Developer-EditionIDs
wurde die gesamte Matrix mit dem korrigierten Runner erneut erfolgreich
ausgeführt. Der fehlgeschlagene Erstversuch zählt nicht zur erfolgreichen Matrix.

Die Compatibility-Prüfung verwendet jetzt `sys.databases.compatibility_level`
mit ausdrücklicher Prüfung fehlender Werte. Die frühere, nicht unterstützte
`DATABASEPROPERTYEX`-Property konnte Abweichungen übersehen.
Technische Primärquellen, geprüft am 2026-10-06:
[DATABASEPROPERTYEX](https://learn.microsoft.com/en-us/sql/t-sql/functions/databasepropertyex-transact-sql?view=sql-server-ver17),
[Compatibility Level](https://learn.microsoft.com/en-us/sql/relational-databases/databases/view-or-change-the-compatibility-level-of-a-database?view=sql-server-ver17),
[SERVERPROPERTY/EditionID](https://learn.microsoft.com/en-us/sql/t-sql/functions/serverproperty-transact-sql?view=sql-server-ver17).
Diese Korrekturen verändern keine Lehrinhaltsfreigabe.

Alle selbst erzeugten Container wurden nach Eigentumsprüfung einschließlich
anonymer Volumes entfernt, auch im fehlgeschlagenen Erstversuch. Bereits
vorhandene fremde Container waren keine Testziele und wurden nicht verändert.
Zugangsdaten kamen ausschließlich aus der temporären Prozessumgebung.
Rohoutput, Pläne, Querytexte, Hostnamen und Zugangsdaten wurden nicht als
Repository-Artefakte gespeichert.

19 Runner-Selbsttests prüfen unter anderem fehlende Phasen, Warnungen, Timeouts,
Versionsabweichung, fehlende Bestätigung, Cleanupvorrang und fehlgeschlagene
Recovery. Framework-Regressionstests prüfen Doppelversagen und Terminierung
vor Reap bei einem Interrupt. Der reale Linux-Test mit einem Nachfahren in
eigener Session wird im CI-Job ausgeführt; lokal wurden diese Tests auf Windows
ausgeführt. Harte Host-Abbrüche und atomare Prozesscontainment-Garantien sind
nicht nachgewiesen. Der endgültige CI-Infrastrukturabbau entfernt den eigenen
Wegwerfcontainer.

## Offene Gates

Dieser Nachweis enthält keine Incident-, Query-Store-, XE-, Hypothesen-,
Mitigations-, T0/T1/T2- oder Performanceabnahme. Er belegt keine
Docker-/Podman-Parität und keine Windows-SQL-Server-Runtime. `DGN-007` bleibt
`IMPLEMENTED_STATIC_SLICE_B`; ein freigegebenes Demo-`manifest.json`,
`scenario.json`, Inventaraufnahme und interaktive Teilnehmerübergabe bleiben
offen. Der nächste kleine Schnitt ist die automatisierte Incident- und
Zeitfensterevidenz auf diesem Datenmodell.
