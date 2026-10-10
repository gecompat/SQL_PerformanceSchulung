# DGN-007 – Automatisierte Datenmodell-, Fenster-, Profil- und Kontrollverträge

Status Datenmodell: `IMPLEMENTED`; lokale Docker-Matrix am 2026-10-06 auf SQL Server
2019/150, 2022/160 und 2025/170 jeweils zweimal mit `PASS/OK` bestanden.
Der [Runtime-Nachweis](../../../../Documentation/Project_Planning/DGN_007_DATA_MODEL_RUNTIME_EVIDENCE.md)
dokumentiert Versionen, Cleanup und Grenzen. Dieser eigenständige
`DGN-007_DATA_MODEL`-Schnitt prüft Aufbau, deterministische Daten, Suchergebnisse
und Cleanup. Er ist eine Vorbereitung der Capstone-Runtime-Matrix und enthält
keine Incident-, XE-, Hypothesen- oder Mitigationsabnahme.
Der separate `DGN-007_QUERY_STORE_WINDOWS`-Vertrag ergänzt begrenzte
Query-Store-Capture-Evidenz für zwei disjunkte T0/T1-Intervalle.
Auch dieser Schnitt bestand am 2026-10-06 auf allen drei Versionen je zweimal.
Sein Runtime-Status steht im [Fensternachweis](../../../../Documentation/Project_Planning/DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md).
Ein `PASS` gilt ausschließlich für den jeweils ausgewählten Vertrag.
Der zusätzliche `DGN-007_PROFILE_COMPARISON`-Vertrag vergleicht vorhandene
T0/T1-Capture-Metriken, ohne daraus eine Incidentreproduktion abzuleiten.
Er bestand am 2026-10-07 auf allen drei Versionen jeweils zweimal; der
Profilnachweis dokumentiert vollständige Reihenfolge, Messwerte und Cleanup.
Die neutralen AB-/BA-/AA-Kontrollcaptures bestanden am 2026-10-07 auf allen
drei Versionen je zweimal. Die vollständige neue Reihenfolge umfasst 36
erfolgreiche lokale Lifecycles; der
[Kontrollnachweis](../../../../Documentation/Project_Planning/DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md)
dokumentiert Metriken, ausgeführte Planmengen und unabhängigen Cleanup.

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
Zusätzlich sind die `ItemId`-Domäne 1 bis 24.000, jede Gruppenmenge, feste
Suchcounts und die vier Request-Parameterpaare geprüft. Die Ausgabeordnung
des Resultstreams wird durch `INSERT EXEC` nicht nachgewiesen.

`FWK-001`, `FWK-002`, `FWK-003`, `FWK-008`, `FWK-010`, `FWK-011` und `FWK-012`
gelten für den begrenzten Schnitt. Abweichung vom wiederverwendbaren Generator:
der eigenständige Aufbau verwendet die fachlich benötigten `Case*`-Tabellen
und prüft deterministische Zuordnung, Zeilenzahlen und Suchergebnisse exakt.
Setup übernimmt keine vorhandene Datenbank; Wiederholbarkeit wird durch den
vollständigen Setup-/Cleanup-Lifecycle hergestellt. Unvollständig markierte
Zustände werden beim Cleanup sicher abgewiesen und benötigen eine manuelle
Eigentumsprüfung. Das automatische Nachlöschen einer teilweise markierten
Datenbank ist bewusst nicht implementiert.

`FWK-004` bis `FWK-006` bleiben für die vollständige Capstone-Abnahme offen.
`FWK-007` wird im Fenstervertrag durch Konfigurationssnapshot vor Änderung
und vollständigen markergebundenen Abbau der frischen Datenbank erfüllt: Der
ursprüngliche Zustand ist eine abwesende Datenbank ohne Query Store. Das ist
eine strengere Wegwerfinstanzgrenze; eine Übernahme vorhandener Datenbanken
oder Konfigurationen ist nicht zulässig.
Im Datenmodellmanifest fehlen Baseline, Demonstration, Mitigation und
Comparison. Das zusätzliche `windows.manifest.json` enthält nach der
Datenassertion ausschließlich `QUERY_STORE_WINDOWS` (150 Sekunden), vor
dem unveränderten Cleanup. Das gemeinsame reguläre Budget bleibt 180 Sekunden. `setup.manifest.json` ist ein ausdrücklich begrenzter Prüfpfad und
kein freigegebenes Demo-`manifest.json` im Laufkatalog. Der 2025-Adapter und der
statische Teilnehmerpfad verwenden weiterhin den eigenen Run-Token `LOCAL`.
Dieser Test verwendet ausschließlich `AUTO`; es gibt keine `:r`-Abhängigkeit.
Das zusätzliche `profile-comparison.manifest.json` übernimmt diese Phasen und
fügt `PROFILE_COMPARISON` mit zehn Sekunden vor Cleanup ein. Die interne
Vergleichsdeadline beträgt acht Sekunden. Gesamt- und Cleanup-Budget bleiben
180 beziehungsweise 60 Sekunden.

## Ausführung und Recovery

Der strikte Docker-Runner führt den vollständigen Vertrag genau zweimal aus
und prüft nach jedem Lauf unabhängig, dass die AUTO-Datenbank fehlt. Er benötigt
einen ausdrücklich gewählten, frischen Container und `SQLCMDPASSWORD` aus der
Prozessumgebung. Die Wegwerfinstanz-Bestätigung autorisiert auch den isolierten
Lab-Lauf und den markergebundenen AUTO-Datenbankabbau.

```powershell
python Tests/Runtime/run_dgn007_automated_setup.py `
  --container <eigener-frischer-Container> --expected-major 17 `
  --confirm-disposable-instance
```

Für den Fenstervertrag denselben Aufruf um `--scope query-store-windows`
ergänzen. Ohne Scope bleibt der bisherige Datenmodellvertrag ausgewählt.
Für den neutralen Vergleich `--scope profile-comparison` verwenden. Für die
Kontrollcaptures `--scope control-ab`, `--scope control-ba` oder
`--scope control-aa` wählen. Jeder der sechs Scopes führt sein eigenes Manifest
jeweils zweimal vollständig aus.
Für 2019 und 2022 `--expected-major 15` beziehungsweise `16` verwenden.
Der Runner akzeptiert ausschließlich Developer-Editionen, leere Instanzen
und `PASS/OK` in jeder erforderlichen Phase. Bei fehlgeschlagenem Cleanup
bleibt das Ergebnis `FAIL_CLEANUP`, auch wenn eine einmalige markergebundene
Recovery den Zustand anschließend bereinigt. Ein Abbruch beendet zuerst den
lokalen Prozessbaum; die endgültige Infrastrukturgrenze ist die Entfernung
des eigenen Wegwerfcontainers. Harte Host-Unterbrechungen garantieren keinen
Cleanup. Der Runner entfernt selbst keinen Container.

Für einen einzelnen manuellen Manifestlauf:

Im Repository-Stamm gegen eine bereits bereitgestellte, leere Wegwerfinstanz
mit installiertem `sqlcmd` und integrierter Authentifizierung ausführen:

```powershell
python Demos/00_Framework/Tools/run_demo.py `
  Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/setup.manifest.json `
  --server localhost --auth integrated --confirm-isolated-lab
```

Für den einzelnen Fensterlauf `setup.manifest.json` durch
`windows.manifest.json` ersetzen.
Für den einzelnen Profilvergleich `profile-comparison.manifest.json` wählen.
Für einzelne Kontrollcaptures `control-ab.manifest.json`,
`control-ba.manifest.json` oder `control-aa.manifest.json` wählen.
Der normale Runner unterdrückt die SQL-Phasenausgaben. Ein interaktiver
Manifestlauf kann mit `--show-output` die unten beschriebenen skalaren
Vergleichsresultsets anzeigen; Rohoutput wird nicht gespeichert.

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
XE-Session. Der Datenmodellvertrag verändert Query Store nicht; der
Fenstervertrag setzt ausschließlich in seiner eigenen Datenbank READ_WRITE,
Capture ALL, 128 MB, einminütige Intervalle und 60 Sekunden Flushintervall.
Ein erneuter
Lauf beginnt wieder beim Preflight. Rohoutput, Pläne und Querytexte werden
nicht als Repository-Artefakte gespeichert.

## Validierung und nächste Einheit

```powershell
python Tests/Static/validate_dgn007_automated_setup.py
python Tests/Static/validate_dgn007_query_store_windows.py
python Tests/Static/validate_dgn007_profile_comparison.py
python Tests/Static/test_dgn007_profile_comparison.py
python Tests/Static/validate_dgn007_control_capture.py
python Tests/Static/test_dgn007_control_capture.py
```

Der Workflow `.github/workflows/dgn007-automated-setup.yml` prüft diese
sechs begrenzten Verträge auf allen drei Versionen je zweimal, einschließlich
unabhängiger Prüfung des Datenbankabbaus. Er startet frische Docker-Container
mit vier CPU-Kernen und 8 GB Speicher, ohne veröffentlichte Ports oder
Host-Volumes. Nach jedem Job entfernt er ausschließlich den eigenen Container
einschließlich anonymer Volumes. Laufende Prüfungen werden bis zum regulären
Cleanup erhalten; Rohoutputs werden nicht als Actions-Artefakte hochgeladen.
Die statischen Prüfungen enthalten negative Kontrollen für fehlende Phasen,
Warnungen, Timeouts, Eigentumsprüfung und Cleanup-Fehler.

## Fenstervertrag und verbleibende Abnahme

Der Fenstervertrag lässt das tatsächlich beobachtete anfängliche Query-Store-
Intervall aus. Danach führt er je vier Suchrequests in zwei getrennten,
katalogbelegten Intervallen aus. T0 beginnt mit `(8,3)`, T1 mit `(1,3)`; beide
enthalten dieselben vier Parameterpaare je einmal. Vor jedem Fenster wird nur
die eigene markierte Suchprozedur objektbezogen neu kompiliert. Vor jeder Intervallprobe führt der Batch eine separate Kontrollabfrage über
zwölf synthetische Gruppenzeilen in einem festen `sp_executesql`-Batch aus.
Dieser wird erst nach der Query-Store-Aktivierung separat kompiliert. Die
Kontrollabfrage verändert keine Suchrequests und bleibt
außerhalb des Parent-/Variant-Scope. Ein Flush unterstützt die Sichtbarkeit
und ersetzt keinen Intervallwechsel. Polling ist
auf 90 Sekunden je Grenze und insgesamt 145 Sekunden Phase begrenzt; ein
nicht beobachteter Übergang führt zu `FAIL_TIMEOUT`.

Ergebnisvertrag und Requestscope bleiben exakt; Query Store muss je Fenster
vier reguläre Suchausführungen aus dem Parent-/Variant-Scope erfassen.
PSP-Varianten werden nur auf unterstützten Engines dynamisch aufgelöst.
Disk-/Speicherzeilen werden aggregiert und Mittelwerte nach Ausführungszahl
gewichtet. Die Labtabellen speichern ausschließlich Konfiguration, IDs,
Grenzen, Counts und skalare Metriken; keine Pläne oder Querytexte. Cleanup
entfernt diesen gesamten Zustand mit der eigenen Datenbank.

## Neutraler Profilvergleich

Die zusätzliche Phase liest die vorhandenen `lab.IncidentProfile`-Werte und
prüft erneut die zwei disjunkten Katalogintervalle, dieselben vier Parameterpaare,
je vier reguläre Suchausführungen, Marker sowie den eigenen Parent-/Variant-Scope.
Erzwungene Pläne und unterstützte Query-Store-Hints sind ausgeschlossen. Der
Live-Katalogabgleich prüft IDs, Counts und Zeitgrenzen; er vergleicht die
gespeicherten Metrikwerte nicht unabhängig mit neu aggregierten Live-Mittelwerten.
Es entstehen weder weitere Suchrequests noch Flushes oder direkte Änderungen
an persistenten Labtabellen und Query-Store-Konfiguration. Capture ALL kann
die Beobachtungsqueries selbst erfassen; sie bleiben außerhalb des Suchscope
und werden mit der eigenen Datenbank abgebaut.

Je Fenster werden Duration, CPU, Logical Reads und Rows als
`SUM(ExecutionCount * Mittelwert) / SUM(ExecutionCount)` gewichtet. Resultsets
`DGN007_PROFILE_WINDOW` und `DGN007_PROFILE_METRIC` zeigen die Mittelwerte,
tatsächlich ausgeführte Plananzahl je Fenster, Delta `T1-T0` und Ratio
`T1/NULLIF(T0,0)`. `BaselineZero=1` kennzeichnet den nicht definierten Quotienten
bei gültiger Null-Baseline; fehlende und negative Metriken werden abgewiesen.
Duration und CPU beziehen sich auf Statement-Runtime in Mikrosekunden,
Logical Reads auf 8-KB-Pages. Compilezeit und Clientlatenz werden nicht daraus
abgeleitet.
Je Fenster bleiben 4.229 Ergebniszeilen erforderlich; die Toleranz `0.000001`
betrifft ausschließlich die Rundung der `float`-Aggregation.

Ein Vergleichs-PASS setzt weder mehrere Pläne noch eine bestimmte Richtung,
Ratio oder Performance-Schwelle voraus. Gleiche Profile und negative Deltas
sind zulässige Evidenz. Der [Profilnachweis](../../../../Documentation/Project_Planning/DGN_007_PROFILE_COMPARISON_RUNTIME_EVIDENCE.md)
grenzt lokale Runtime, numerische Fixtures und Cleanup voneinander ab.
Technische Primärquelle, geprüft am 2026-10-06:
[Query-Store-Runtime-Stats](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17).

## Neutrale Kontrollcaptures

Die drei eigenständigen Scopes konfigurieren vor der Last die feste Bedingung
je chronologischem Fenster. A führt `(8,3)`, `(1,3)`, `(5,3)`, `(1,1)` aus;
B führt `(1,3)`, `(8,3)`, `(5,3)`, `(1,1)` aus. AB weist T0=A und T1=B zu,
BA weist T0=B und T1=A zu, AA verwendet A in beiden Fenstern. Die chronologischen
WindowIds und Metrikdeltas bleiben T0 und T1; eine nachträgliche Umbenennung
zu Baseline und Incident findet nicht statt. Alle Bedingungen besitzen genau
denselben Vierermix, je vier reguläre Ausführungen und 4.229 Ergebniszeilen.

`CONTROL_CONFIG` verwendet eine der drei festen `15_Control_*.sql`-Dateien
(fünf Sekunden), `CONTROL_WINDOWS` den eigenen `21_Controlled_Query_Store_Windows.sql`
(150 Sekunden). Die bestehende `PROFILE_COMPARISON`-Phase bleibt unverändert.
Danach prüft `CONTROL_EVIDENCE` die tatsächlich protokollierte Aufrufreihenfolge
und die Bindung der ausgeführten Planmengen an die beiden Profile. Ihr externer
Schutz beträgt zehn Sekunden, die interne Deadline acht Sekunden. Gesamtbudget
und unabhängiges Cleanup bleiben 180 und 60 Sekunden. Der bisherige Fensterbatch
und die bisherigen Manifeste bleiben eigenständige Verträge.

Die zusätzlichen Resultsets zeigen Bedingungen, aktive Parent-/Query-/Plan-IDs,
Planhashes und die Vereinigungsmenge ausgeführter Plan-IDs. Historische Pläne
ohne positive reguläre Ausführungen in T0/T1 erweitern diese Menge nicht.
Ein Plan je Fenster kann dieselbe oder verschiedene Plan-IDs bedeuten; auch
gleiche Hashes erlauben keinen Schluss auf identische Kosten oder eine Ursache.
Die skalaren IDs gelten nur innerhalb des jeweiligen Lifecycles. Die Phase
liest keine Plan-XML-Inhalte und persistiert keine Querytexte oder Pläne.

Jeder Lifecycle beginnt nach geprüftem Cleanup wieder mit einer neuen eigenen
Datenbank. Ein Kontrollcapture-PASS prüft die Last-, Fenster-, Profil-, Plan-
und Cleanup-Verträge unabhängig von Richtung und Größe der gemessenen Metriken.
Die Gegenreihenfolge und AA sind Voraussetzungen eines späteren prospektiv
definierten Reproduktionsvergleichs. Ein einzelner AA-Vergleich oder zwei
Wiederholungen quantifizieren keine allgemeine Messunsicherheit.

A und B verändern gemeinsam Erstparameter nach objektbezogenem `sp_recompile`
und Aufrufreihenfolge. Die Kontrollen isolieren deshalb keine Kompilierungsursache.
`sp_recompile` bereitet die nächste Ausführung vor; sein Aufruf belegt weder
den konkreten kompilierten Parameter noch eine ungünstige Kompilierung.
Primärquellen, geprüft am 2026-10-06:
[Planmetadaten](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17),
[sp_recompile](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-recompile-transact-sql?view=sql-server-ver17).

Der getrennte [SQL-Producer](../Contracts/SQL_CAPTURE_PRODUCER.md) ergänzt
jetzt tatsächlich erfasste Ergebniscounts je Request und vollständige
skalare ASCII-Frames vor Cleanup. Die additive Option
`--check-capture-projection` prüft dieselben Kontroll-Lifecycles über den
reinen Packager und Decoder. Acht Phasen und 180-/60-Sekunden-Budgets bleiben
erhalten. Quellenrevision, Präzision, Ausgabegrenzen und die eigene begrenzte
Runtime-Abnahme stehen im Producer-Vertrag.

Für begrenzte Fehlerdiagnose unterstützt derselbe Runner zusätzlich
`--check-phase-diagnostics` in allen sechs bekannten Scopes. Die vorhandenen
CI-Aufrufe für Datenmodell, Fenster und Profilvergleich verwenden diese Option.
Bei Fehlern erscheinen erst nach Cleanup ausschließlich erlaubte
Phasen-/Summarycodes und tatsächlich stderr-gebundene numerische SQL-Details.
SQL35-Guardkennungen bleiben auf Kontroll-Evidenz beschränkt. Die Option
aktiviert keine Capture-Abnahme; SQL, Lifecycles und Budgets bleiben gleich.

Ein Fenster- oder Vergleichs-PASS belegt weder unterschiedliche Pläne noch eine Planregression,
Performanceverschlechterung oder Reproduktion eines Incidents. Auch PSP wird
nicht deaktiviert. Die Akzeptanzmethodik ist im
[prospektiven Vertrag](../Contracts/README.md) durch `DEC-068` vorab festgelegt.
Nach der begrenzten Producer-Prüfung folgt der Collector-Coordinator mit
verifiziertem Freeze, Ressourcen, Reihenfolge, Budgets und unabhängigem
Cleanup. Erst danach folgen frische Bestätigungsläufe. Das ist weiterhin
kein Incident-Gate und kein Nachweis von Clientlatenz oder statistischer
Signifikanz. Danach folgen Requestscope, Alternativhypothesen,
reversible Mitigation und T2-Vergleich. Szenariopromotion, `READY_FOR_USER`,
Katalogaufnahme, vollständige Capstone-Matrix und Änderungen an
`SQL_Server_Lab` bleiben offen.

Quellen und Traceability: bestehender Designvertrag `ADV-007`,
`SRC-001`, `SRC-007`, `SRC-027`, `SRC-028`, `SRC-031`, `SRC-035`, `SRC-036`
mit Abrufdatum gemäß Quellenregister; `LO-M07-04`, `LO-M06-08`, `LO-M03-07`.

Seit `DEC-072` muss der separate feste Pollquery mit dem Marker
`DGN007_INTERVAL_PULSE` im ausgewählten Query-Store-Intervall tatsächlich
regulär erfasst sein. Eine lediglich passend datierte Katalogzeile reicht
nicht mehr für die Rotation. Die Suchrequests laufen weiterhin nacheinander.
SQL35 meldet eine Abweichung zwischen QS-First/Last und SYSUTC-Start/Ende als
`DGN007_CLOCK_DIAGNOSTIC|2|QS_SYSUTC_ENVELOPE_MISMATCH` und gibt die unveränderten
skalaren Capture-Zeitwerte aus. Diese Abweichung beendet den Lauf nicht.
Ausführungszahlen, Intervall-IDs, Requests, Ergebnisse, Planfamilien und Cleanup
bleiben Voraussetzung des begrenzten Kontrollcapture-PASS. Der Capture-Body
und der prospektive Vertrag verwenden explizit Version 2; es gibt keinen
optional abschaltbaren Zeitguard und keinen Zeitpuffer.
