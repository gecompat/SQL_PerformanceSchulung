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

Die Beobachtung muss in einer einzelnen Diagnoseabfrage erfolgen, die die
zugeordneten eigenen Requests, die passenden Grant-Zeilen und die
Pool-/Semaphorezeile gemeinsam projiziert. Ein einmal vor der Abfrage gesetzter
`captured_at_utc`-Wert kennzeichnet diesen Abfragelauf; er macht die DMV-Lesezugriffe
nicht zu einer atomaren Engine-Momentaufnahme. Deshalb lautet die maximal
zulässige Aussage, dass der vollständige Befund in derselben begrenzten
Abfrageaufnahme sichtbar war. Die genaue zeitliche Reihenfolge gleichzeitiger
Engineänderungen bleibt unbekannt. Mehrere getrennte DMV-Abfragen dürfen nicht
nachträglich mit demselben Zeitstempel zu einem gemeinsamen Snapshot verbunden
werden. Das konkrete read-only Abfragemuster und diese Aussagegrenze stehen in
der [Lehrnotiz](../Curriculum/COMPETING_MEMORY_GRANTS_LESSON.md#den-wartenden-eigenen-request-an-den-wait-binden).

Der vorhandene Offlineprüfer kann diese Werte synthetisch auf Widersprüche
prüfen. Er authentifiziert weder ihre Aufnahme noch die Zuordnung der
Verbindungen. Für einen gewährten Peer muss der nicht-NULL-Wert `grant_time`
im Offline-Datensatz als zeitzonenloses ISO-8601-Datum der SQL-Server-
`datetime`-Spalte vorliegen (Kalenderdatum ab 1753, höchstens drei
Nachkommastellen im 3,33-ms-Raster); der UTC-Capturemarker bleibt davon
getrennt. Aktive Sessions, ein Spill, ein `WAITFOR` nach Abschluss der Abfrage
oder kumulierte Wait-Stats sind kein Ersatz für den beschriebenen zeitgleichen
Befund. Das Szenario behauptet keinen allgemeinen Speichermangel, keinen Spill
und keinen Leistungsgewinn.

## Vorgeschlagener Ablauf

| Phase | Vorgesehener Ablauf | Akzeptanz |
|---|---|---|
| Vorprüfung | Nur die eigene SQL-Server-2025-Developer-Wegwerfinstanz; exakter Build, Compatibility Level, effektive Diagnoseberechtigung, Containergrenze und Serverzustand erfassen. Keine Verbindung zu einer gemeinsam genutzten Instanz. | Jede Abweichung oder fehlende Voraussetzung beendet den Lauf vor Setup. |
| Setup | Markergebundene Datenbank mit deterministischen synthetischen Zeilen. Eine feste Abfrageform muss im tatsächlichen Plan einen grantfähigen Sort- oder Hashoperator enthalten. Nur eigene Sitzungen erhalten ein eindeutiges Run-Token in `Application Name`; geheimhaltungsbedürftige Werte kommen nicht in Manifest oder Logs. | Eigentumsmarker, Datenumfang und Actor-Identitäten sind vollständig und vor dem Start fixiert. |
| Einzelactor-Kontrolle | Genau ein Actor führt die feste parametrisierte Abfrage aus. Der Beobachter ordnet die eigene `session_id` und aktuelle `request_id` aus dem gestarteten Clientprozess zu und sieht eine erteilte Anforderung oder beendet den Kontrollarm mit begrenztem Skip. | Kein WAIT-Anspruch; Querytext, Planform und Rowcount werden als Vergleichsgrundlage gehalten. |
| Konkurrenz | Ein Halte-Actor startet dieselbe Abfrageform und wird erst nach beobachtetem Grant als bereit signalisiert. Danach starten höchstens zwei weitere Actors über eine Startbarriere dieselbe Abfrage. Kein Actor wartet mit einer festen Pause; jeder Client hat einen begrenzten Fetch- und Laufzeitpfad. | Nur echte Zuordnung zu gestarteten eigenen Clientprozessen zählt. Die Beobachtung endet nach dem ersten vollständigen Pflichtsnapshot oder bei Ablauf der festen Frist. |
| Beobachtung | Eine begrenzte Pollschleife führt die gemeinsame read-only Diagnoseabfrage aus der Lehrnotiz aus. Sie projiziert aktuelle eigene Requests, dazu passende Grantzeilen und Pool-/Semaphorezeile mit einem gemeinsamen Abfragezeitmarker. Abfrage- und Session-IDs werden unmittelbar aus den eigenen Verbindungen gebunden, nicht aus einem losen Application-Name-Treffer abgeleitet. | `PASS` nur, wenn der vollständige Befund in dieser einen Abfrageaufnahme sichtbar ist. Der Zeitmarker belegt keinen atomaren DMV-Snapshot; getrennte Abfrageergebnisse werden nicht zusammengefügt. Sonst `SKIP_NO_GRANT_WAIT`, `NOT_PROVEN` oder ein begründeter Fehlerstatus. |
| Abschluss | Alle gestarteten Clients werden regulär abgewartet oder über ihre eigenen Cancellation-Handles abgebrochen. Danach werden genau die gebundenen eigenen Sessions auf Abwesenheit geprüft. Die markergeprüfte Datenbank wird entfernt und ihre Abwesenheit unabhängig bestätigt. | Fremde Sessions werden weder beendet noch aufgrund von Login, Host oder Application Name als eigene behandelt. Unvollständige Rücknahme ergibt `FAIL_CLEANUP`. |

Die drei Actor-Slots sind eine Planungsobergrenze, keine Behauptung, dass sie
einen Wait erzeugen. Datenmenge, Client-Fetchverhalten, Wiederholungszahl und
Zeitfristen sind noch nicht festgelegt. Grant-Hints sind für den aktuellen
Systempool-Pilot ausgeschlossen (siehe folgende Entscheidung). Die übrigen
Werte werden erst nach Review anhand des verfügbaren Containerprofils gewählt
und dürfen innerhalb eines Laufs nicht adaptiv nach oben skaliert werden.

## Begrenzungsstrategie und Entscheidung zu Grant-Hints

Für den vorgesehenen SQL-Server-2025-Developer-Systempool ist zunächst kein
`MIN_GRANT_PERCENT`- oder `MAX_GRANT_PERCENT`-Hint freigegeben. Microsoft
dokumentiert, dass `MAX_GRANT_PERCENT` nur in einem benutzerdefinierten
Resource-Governor-Pool garantiert nicht überschritten wird; im Systempool
erhält eine Query mindestens die für den Start benötigte Menge. `MIN_GRANT_PERCENT`
garantiert mindestens das Maximum aus benötigtem und angefordertem Mindestgrant;
fehlt die erforderliche Mindestmenge, kann die Query mit einem Fehler enden.
Keiner der beiden Hints ist daher für diesen Systempool-Pilot ein belegter
Ressourcen- oder Abbruchzaun. Die Actor-Obergrenze allein garantiert ebenfalls
keinen Speicherhöchstwert.

Die erste zulässige Machbarkeitsprüfung verwendet deshalb nur eine feste
Abfrageform, höchstens drei gebundene eigene Actors, vorab festgelegte
Daten-/Fetch-/Zeitgrenzen und das verifizierte Containerlimit. Das ist eine
begrenzte Versuchsanordnung, aber keine mathematische Obergrenze für den
Engine-Grant. Vor einem Pilot müssen unabhängiger Review und Harness belegen,
dass die gewählten Eingaben innerhalb des verfügbaren Budgets bleiben und
Timeout sowie Abbruch tatsächlich greifen. Erzeugt diese Variante keinen
beobachtbaren Grant-Wait, lautet das Ergebnis `SKIP_NO_GRANT_WAIT`; Datenmenge
oder Parallelität werden nicht während des Laufs erhöht.

Ein benutzerdefinierter Resource-Governor-Pool wäre eine separate,
instanzweite Konfigurationsmutation und erhält hier keine Freigabe. Eine spätere
Änderung dieses Entscheids erfordert eine eigene Änderungsfreigabe sowie einen
ausdrücklich isolierten Entwurf mit Vorher-/Nachher-Konfigurationsvergleich,
Kill-Switch und vollständigem Restore. Es gibt keinen automatischen Fallback.

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
empirisch geprüft werden. Die Entscheidung gegen einen Hint im aktuellen
Systempool-Pilot folgt aus den dokumentierten unterschiedlichen Garantien; sie
ist keine Aussage, dass die Actor- oder Containergrenzen selbst einen
Engine-Grant hard-cappen.
