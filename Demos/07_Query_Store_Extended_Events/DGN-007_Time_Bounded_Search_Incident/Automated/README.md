# DGN-007 – Automatisierter Datenmodell-Schnitt

Status: `IMPLEMENTED`, Runtime noch nicht ausgeführt. Dieser eigenständige
`DGN-007_DATA_MODEL`-Schnitt prüft Aufbau, deterministische Daten, Suchergebnisse
und Cleanup. Er ist eine Vorbereitung der Capstone-Runtime-Matrix und enthält
noch keine Incident-, Query-Store-, XE-, Hypothesen- oder Mitigationsabnahme.
Ein `PASS` gilt ausschließlich für diesen Datenmodellvertrag.

## Voraussetzungen und Grenzen

Zielmatrix: SQL Server 2019 / Compatibility Level 150, SQL Server 2022 / 160
und SQL Server 2025 / 170; Developer Edition auf einer isolierten Wegwerfinstanz.
Der T-SQL-Vertrag verwendet keine betriebssystemspezifischen Funktionen.
Benötigt werden `CREATE ANY DATABASE` und Eigentümerrechte für die selbst
erzeugte Datenbank. Keine bereits vorhandene Benutzerdatenbank ist zulässig.
Der Test verwendet höchstens eine SQL-Session gleichzeitig; parallele Läufe
gegen dieselbe Instanz sind ausgeschlossen.

Die Sicherheitsstufe bleibt `YELLOW`. Das Capstone-Mindestprofil von vier
logischen CPU-Kernen und 8 GB SQL-Server-Speicher bleibt Voraussetzung für die
spätere Gesamtabnahme; der Datenmodelltest misst keine Ressourcengrenze und
beweist keine Eignung dieses Profils. Für Daten- und Logdateien sowie TempDB
ist mindestens 512 MB freie Kapazität vorzusehen. Es werden 24.000 Faktzeilen
und 72.000 Detailzeilen erzeugt. Das reguläre Schutzbudget beträgt 180 Sekunden,
das unabhängige Cleanup-Budget 60 Sekunden. Dies sind Abbruchgrenzen, keine
Performance-Erwartungswerte.

## Datenvertrag und Framework

Die vier Tabellen und die Suchprozedur folgen dem synthetischen Vertrag von
[`ADV-007`](../../../../Documentation/Project_Planning/ADV_007_LAB_VP5_DESIGN.md).
Wie im vorhandenen Adapter gibt es zwölf Gruppen: vier mit je 4.000, drei mit
je 2.000 und fünf mit je 400 Faktzeilen, drei Details je Faktzeile sowie dieselbe
Statusverteilung. `ItemId` wird explizit aus der laufenden Nummer gebildet;
damit hängt die Zuordnung der fachlichen Werte nicht von der Reihenfolge einer
`IDENTITY`-Zuteilung ab. Der Datenmodelltest prüft vier feste Parameterklassen
und vergleicht jede Ergebnismenge in beide Richtungen einschließlich Zeilenzahl.

`FWK-001`, `FWK-002`, `FWK-003`, `FWK-008`, `FWK-010`, `FWK-011` und `FWK-012`
gelten für den begrenzten Schnitt. Abweichung vom wiederverwendbaren Generator:
der eigenständige Aufbau verwendet die fachlich benötigten `Case*`-Tabellen
und prüft deterministische Zuordnung, Zeilenzahlen und Suchergebnisse exakt.
Setup übernimmt keine vorhandene Datenbank; Wiederholbarkeit wird durch den
vollständigen Setup-/Cleanup-Lifecycle hergestellt. Unvollständig markierte
Zustände werden beim Cleanup sicher abgewiesen und benötigen eine manuelle
Eigentumsprüfung. Das automatische Nachlöschen einer teilweise markierten
Datenbank ist bewusst nicht implementiert.

`FWK-004` bis `FWK-007` werden erst mit Messung und Incident implementiert.
Deshalb fehlen Baseline, Demonstration, Mitigation und Comparison in diesem
Manifest. `setup.manifest.json` ist ein ausdrücklich begrenzter Prüfpfad und
kein freigegebenes Demo-`manifest.json` im Laufkatalog. Der 2025-Adapter und der
statische Teilnehmerpfad verwenden weiterhin den eigenen Run-Token `LOCAL`.
Dieser Test verwendet ausschließlich `AUTO`; es gibt keine `:r`-Abhängigkeit.

## Ausführung und Recovery

Im Repository-Stamm gegen eine bereits bereitgestellte, leere Wegwerfinstanz
mit installiertem `sqlcmd` und integrierter Authentifizierung ausführen:

```powershell
python Demos/00_Framework/Tools/run_demo.py `
  Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/setup.manifest.json `
  --server localhost --auth integrated --confirm-isolated-lab
```

Für SQL-Authentifizierung `--auth sql --username sa` verwenden; das Passwort
kommt ausschließlich aus `SQLCMDPASSWORD`. Verbindungs- und Zertifikatoptionen
sind im [lokalen Ausführungsleitfaden](../../../../Documentation/HowTo/LOCAL_TEST_ENVIRONMENT.md)
beschrieben. `--confirm-isolated-lab` bestätigt ausdrücklich auch den unten
beschriebenen markergebundenen Abbau der für diesen Test erzeugten Datenbank.

Der Harness führt read-only Preflight, Setup und Datenassertion in dieser
Reihenfolge aus und versucht nach begonnenem Setup stets Cleanup. Ein
erforderlicher `SKIP` beendet Folgephasen. Fehler, Timeout oder `Ctrl+C` sind
kein Cleanupnachweis. Nach unterbrochener Prozesssteuerung diesen Recovery-Batch
mit passenden Anmeldeoptionen wiederholen:

```powershell
sqlcmd -S localhost -E -b -i Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/90_Cleanup.sql `
  -v DemoId=DGN-007 RunToken=AUTO TargetDatabase=SQLPERF_LAB_DGN007_AUTO ConfirmIsolatedLab=1 HighImpactConfirmed=1
sqlcmd -S localhost -E -b -Q "IF DB_ID(N'SQLPERF_LAB_DGN007_AUTO') IS NOT NULL THROW 51004,'FAIL_CLEANUP',1;"
```

Cleanup entfernt nur `SQLPERF_LAB_DGN007_AUTO` mit vier exakt passenden
Eigentumsmarkern. Fehlende, abgeschnittene oder abweichende Marker verhindern
den Abbau. Es gibt keine globale Konfigurationsänderung und keine eigene
XE-Session. Query Store wird in diesem Schnitt nicht verändert. Ein erneuter
Lauf beginnt wieder beim Preflight. Rohoutput, Pläne und Querytexte werden
nicht als Repository-Artefakte gespeichert.

## Validierung und nächste Einheit

```powershell
python Tests/Static/validate_dgn007_automated_setup.py
```

Vor einer Runtimefreigabe muss der Lifecycle auf allen drei Versionen je zweimal
laufen, einschließlich unabhängiger Prüfung des Datenbankabbaus. Danach folgen
die abgegrenzten Zeitfenster T0/T1/T2 und belastbare Incident-, Requestscope-,
Hypothesen- und Vergleichsevidenz. Es wurde kein neuer Runner und kein Workflow
für eine unvollständige Capstone-Abnahme angelegt. Szenariopromotion,
`READY_FOR_USER`, Katalogaufnahme und Änderungen an `SQL_Server_Lab` gehören
nicht zu diesem Schnitt.

Quellen und Traceability: bestehender Designvertrag `ADV-007`,
`SRC-001`, `SRC-007`, `SRC-027`, `SRC-028`, `SRC-031`, `SRC-035`, `SRC-036`
mit Abrufdatum gemäß Quellenregister; `LO-M07-04`, `LO-M06-08`, `LO-M03-07`.
