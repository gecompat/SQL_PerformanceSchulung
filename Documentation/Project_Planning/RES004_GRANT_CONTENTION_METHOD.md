# RES-004 – Methodenentwurf für konkurrierende Abfragespeicherzuteilungen

| Merkmal | Wert |
|---|---|
| Status | `METHOD_DRAFT` – keine SQL-, Demo- oder Laufzeitfreigabe |
| Lernziel | Eine tatsächlich wartende eigene Speicheranforderung von gewährten Grants, aktiven Sessions und bloßen Spills unterscheiden |
| Curriculumanker | `LO-M06-07`; die Lehrnotiz [`COMPETING_MEMORY_GRANTS_LESSON.md`](../Curriculum/COMPETING_MEMORY_GRANTS_LESSON.md) bleibt maßgeblich |
| Getrennte Inhalte | `OPT-013` behandelt den kontrollierten Spill; `RES-003` behandelt instanzweiten Speicherdruck |
| Ziel | Zunächst ein begrenzter SQL-Server-2025-Developer-Pilot in einem eigenen Wegwerfcontainer |

## Aussage und Grenze

Der Pilot soll zeigen, wie eine bekannte eigene Anforderung auf
`RESOURCE_SEMAPHORE` wartet, während derselben Resource-Pool-/Semaphoregruppe
mindestens ein weiterer Grant erteilt ist. Der eigene wartende Request muss in
`sys.dm_exec_requests` stehen und über identische `session_id`/`request_id` mit
`grant_time IS NULL` und positiver Grant-Wartezeit in
`sys.dm_exec_query_memory_grants` verbunden sein. Ein Snapshot aus
`sys.dm_exec_query_resource_semaphores` muss für denselben Pool, dieselbe
Semaphore und denselben UTC-Capturewert positive `waiter_count` und
`grantee_count` ausweisen. Mindestens ein weiterer Grant derselben Semaphore
muss tatsächlich erteilt sein.

Der vorhandene Offlineprüfer kann diese Werte synthetisch auf Widersprüche
prüfen. Er authentifiziert weder ihre Aufnahme noch die Zuordnung der
Verbindungen. Aktive Sessions, ein Spill, ein `WAITFOR` nach Abschluss der
Abfrage oder kumulierte Wait-Stats sind kein Ersatz für den beschriebenen
zeitgleichen Befund. Das Szenario behauptet keinen allgemeinen
Speichermangel, keinen Spill und keinen Leistungsgewinn.

## Vorgeschlagener Ablauf

| Phase | Vorgesehener Ablauf | Akzeptanz |
|---|---|---|
| Vorprüfung | Nur die eigene SQL-Server-2025-Developer-Wegwerfinstanz; exakter Build, Compatibility Level, effektive Diagnoseberechtigung, Containergrenze und Serverzustand erfassen. Keine Verbindung zu einer gemeinsam genutzten Instanz. | Jede Abweichung oder fehlende Voraussetzung beendet den Lauf vor Setup. |
| Setup | Markergebundene Datenbank mit deterministischen synthetischen Zeilen. Eine feste Abfrageform muss im tatsächlichen Plan einen grantfähigen Sort- oder Hashoperator enthalten. Nur eigene Sitzungen erhalten ein eindeutiges Run-Token in `Application Name`; geheimhaltungsbedürftige Werte kommen nicht in Manifest oder Logs. | Eigentumsmarker, Datenumfang und Actor-Identitäten sind vollständig und vor dem Start fixiert. |
| Einzelactor-Kontrolle | Genau ein Actor führt die feste parametrisierte Abfrage aus. Der Beobachter ordnet die eigene `session_id` und aktuelle `request_id` aus dem gestarteten Clientprozess zu und sieht eine erteilte Anforderung oder beendet den Kontrollarm mit begrenztem Skip. | Kein WAIT-Anspruch; Querytext, Planform und Rowcount werden als Vergleichsgrundlage gehalten. |
| Konkurrenz | Ein Halte-Actor startet dieselbe Abfrageform und wird erst nach beobachtetem Grant als bereit signalisiert. Danach starten höchstens zwei weitere Actors über eine Startbarriere dieselbe Abfrage. Kein Actor wartet mit einer festen Pause; jeder Client hat einen begrenzten Fetch- und Laufzeitpfad. | Nur echte Zuordnung zu gestarteten eigenen Clientprozessen zählt. Die Beobachtung endet nach dem ersten vollständigen Pflichtsnapshot oder bei Ablauf der festen Frist. |
| Beobachtung | Eine begrenzte Pollschleife erfasst die aktuellen eigenen Requests, Grantzeilen und Pool-/Semaphorezeile samt gemeinsamem Erfassungszeitwert. Abfrage- und Session-IDs werden unmittelbar aus den eigenen Verbindungen gebunden, nicht aus einem losen Application-Name-Treffer abgeleitet. | `PASS` nur bei vollständigem RES-004-Vertrag; sonst `SKIP_NO_GRANT_WAIT`, `NOT_PROVEN` oder ein begründeter Fehlerstatus. |
| Abschluss | Alle gestarteten Clients werden regulär abgewartet oder über ihre eigenen Cancellation-Handles abgebrochen. Danach werden genau die gebundenen eigenen Sessions auf Abwesenheit geprüft. Die markergeprüfte Datenbank wird entfernt und ihre Abwesenheit unabhängig bestätigt. | Fremde Sessions werden weder beendet noch aufgrund von Login, Host oder Application Name als eigene behandelt. Unvollständige Rücknahme ergibt `FAIL_CLEANUP`. |

Die drei Actor-Slots sind eine Planungsobergrenze, keine Behauptung, dass sie
einen Wait erzeugen. Datenmenge, Client-Fetchverhalten, Abfragehint,
Wiederholungszahl und Zeitfristen sind noch nicht festgelegt. Diese Werte werden
erst nach Review anhand des verfügbaren Containerprofils gewählt und dürfen
innerhalb eines Laufs nicht adaptiv nach oben skaliert werden.

## Begrenzungsstrategie und offene Varianten

Die erste Implementierungsprüfung soll eine ausschließlich abfragebezogene
Steuerung mit einem passenden Speichergrant-Hint untersuchen und die
Enginekonfiguration unverändert lassen. `MIN_GRANT_PERCENT` kann eine
Mindestanforderung erzwingen; `MAX_GRANT_PERCENT` ist im benutzerdefinierten
Ressourcenpool hart begrenzend dokumentiert. Im Systempool gelten andere
Grenzen. Daher ist vor Festlegung eines Hints zu belegen, welche prozentuale
Basis im gewählten Ziel gilt, dass der Mindestgrant für die Query erforderlich
ist und dass weder er noch mehrere Actors das Containerlimit gefährden.

Falls die Hint-Variante keinen begrenzten und nachvollziehbaren Wait erzeugt,
wird sie verworfen. Ein benutzerdefinierter Resource-Governor-Pool wäre eine
separate, instanzweite Konfigurationsmutation und erhält hier keine Freigabe.
Das würde einen roten, ausdrücklich isolierten Versuch mit Vorher-/Nachher-
Konfigurationsvergleich, Kill-Switch und vollständigem Restore erfordern. Es
gibt keinen automatischen Fallback auf diese Variante.

## Ressourcen-, Fehler- und Ergebnisvertrag

- Der erste Pilot gehört ausschließlich in einen kurzlebigen SQL-Server-2025-
  Developer-Container mit vorher verifiziertem CPU-/Speicherlimit; keine
  lokale gemeinsam genutzte SQL-Instanz und keine veröffentlichten Ports oder
  Host-Mounts.
- Das verbindliche Laufbudget, Containerlimit, Datenmaximum, Client-Timeouts
  und separates Cleanupbudget sind Eingaben des späteren unabhängigen Reviews.
  Bis dahin werden sie nicht als qualifiziert ausgegeben.
- Diagnoseabfragen benötigen auf SQL Server 2022 und neuer `VIEW SERVER
  PERFORMANCE STATE`; ältere Builds benötigen die jeweils dokumentierte
  Berechtigung. Die erste Pilotfreigabe gilt nur für den geprüften SQL-Server-
  2025-Build.
- Kein Grant-Wait im Messfenster bedeutet `SKIP_NO_GRANT_WAIT`, nicht Erfolg und
  nicht automatisch einen stärkeren Workload. Ein abgelaufener Request,
  Timeout, fehlender Snapshot oder unvollständige Actorzuordnung bedeutet
  `NOT_PROVEN` beziehungsweise den passenderen Fehlerstatus; Cleanupfehler
  haben Vorrang.
- Nach jedem Fehler werden eigene Clients abgebrochen, Sessions geprüft und
  eigene Datenbank-/Harnessressourcen markergebunden bereinigt. Es wird weder
  `KILL` für fremde SPIDs noch ein serverweiter Cache-, Memory- oder
  Konfigurationsreset verwendet.

## Gates vor ausführbarer Umsetzung

1. Unabhängiger Methoden- und Quellenreview prüft Abfrageform, Hintsemantik,
   Grant-Halterung, Versions-/Berechtigungsgrenze, Pollintervall, Lastprofil,
   Statusoracle und Restore.
2. Ein SQL-Server-2025-Developer-Pilot wird auf genau einem eigenen
   Wegwerfcontainer ausgeführt. Der geänderte Effekt muss sowohl den
   tatsächlich wartenden eigenen Request als auch einen gewährten Peer-Grant
   zur selben Semaphore belegen; andernfalls endet die Variante ohne
   Ausweitung.
3. Der Frameworkvertrag bindet Clientprozess/Session/Request, Rowcount,
   Diagnoseaufnahme, Cleanup und unabhängige Ressourcenabwesenheit. Die
   synthetische Prüfung des Offlineprüfers bleibt ergänzend.
4. Erst nach bestandenem Review und begrenztem Pilot darf ein ausführbares
   Demo-Paket mit eigener Demo-ID und einem konkreten Runtimeprofil vorbereitet
   werden. Eine allgemeine 2019/2022/2025-Matrix, Lastqualifikation und
   menschliche Generalprobe folgen daraus nicht.

## Quellen und Grenzen

- `SRC-010`: `sys.dm_exec_query_memory_grants`, Grant-Zustände und Wartefelder.
- `SRC-110`: aktuelle Requests und Session-/Request-Identität.
- `SRC-134`: Resource-Pool-/Semaphore-Snapshots und allgemeiner
  Memory-Grant-Kontext.
- `SRC-164`: Hintgrenzen und Abgrenzung zwischen Systempool und
  benutzerdefiniertem Ressourcenpool.

Die Microsoft-Quellen dokumentieren Felder und Hintverhalten. Sie bestimmen
weder die konkrete Grantgröße dieser Abfrage noch die Verfügbarkeit eines
Semaphore-Waits in einem bestimmten Build. Das muss im begrenzten Pilot
empirisch geprüft werden.
