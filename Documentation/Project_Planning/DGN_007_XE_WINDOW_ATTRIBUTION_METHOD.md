# DGN-007 – Methodenentwurf für XE-Fensterzuordnung

| Merkmal | Wert |
|---|---|
| Status | `METHOD_DRAFT` – kein Mess-/Actor-Lifecycle freigegeben; eine isolierte synthetische Datenschutzprobe je gepinntem Build ist begrenzt autorisiert |
| Zweck | Prüfen, ob per-Request-Zeitgrenzen durch eine eigene, sequenzierte XE-Evidenzspur ersetzt werden können |
| Bestehender Vertrag | Unverändert; kein G13-Ursachen- oder Mitigationsclaim |
| Quellen | `SRC-027`, `SRC-031`, `SRC-163`; Microsoft Query Store-, XE- und DMV-Dokumentation |

## Fragestellung

Der bestehende G13-Guard vergleicht Requestgrenzen aus `SYSUTCDATETIME()` mit
Query-Store-Ausführungsendzeiten. Microsoft dokumentiert dafür keine gemeinsame
Tickuhr. Dieser Entwurf prüft daher eine alternative Bindung: eine eigene
Extended-Events-(XE)-Spur markiert Fenstergrenzen und zählt darin die
abgeschlossenen Actor-Statements über Ereignisreihenfolge statt Wandzeit.

Das ändert den Messvertrag. Per-Fenster-`count_executions` aus Query Store kann
nicht länger unverändert als Oracle behauptet werden. Query Store bleibt Quelle
für Planrecords und Aggregatmetriken; eine getrennte XE-Kontrollspur liefert
Execution-/Fensterzuordnung. Ergebnisgleichheit und vollständige Plan-/Count-
Oracles müssen vor jeder Umsetzung neu festgelegt und unabhängig geprüft sein.

## Kandidatenablauf

1. Auf einer eigenen, markergebundenen Wegwerfdatenbank wird eine dedizierte,
   begrenzte XE-Session angelegt. Der Scope erfasst ausschließlich die
   festgelegten Actor-Sessions und das Statement-Abschlussereignis. Bestehende
   XE-Sessions werden weder geändert noch gestoppt.
2. Vor dem Beginmarker müssen beide Actorverbindungen nachweislich idle sein;
   kein Request aus dem vorherigen Fenster darf noch laufen. Pro Fenster schreibt
   der Coordinator einen eindeutigen Beginmarker, führt die festgelegte Menge
   an Actorrequests aus und schreibt danach den Endmarker. Jeder erwartete
   Request benötigt ein Start- und Abschlussereignis innerhalb desselben
   Markerpaares und dieselbe Actor-/Session-/Requestbindung. Fehlende Starts,
   Abschlüsse, Cross-window-Paare, mehrfache gleichzeitige Actorrequests oder
   ein Actor, der vor dem Beginmarker nicht idle ist, ergeben `NOT_PROVEN` und
   sperren Folgefenster bis nach bestätigtem Drain/Reset. Marker und Actorereignisse
   müssen dieselbe monoton geordnete `event_sequence`-Spur belegen; Wandzeit
   wird nur diagnostisch ausgegeben und nicht zum Einschlussvergleich benutzt.
3. Nach dem Endmarker wird die XE-Session regulär gestoppt und ihr vollständiger
   bounded Targetinhalt gelesen. Das Fenster ist nur vollständig, wenn genau
   beide erwarteten Marker, die erwartete Zahl von Actorabschlüssen und keine
   Verlust-/Truncationanzeige vorliegen. Eventverlust, fehlender Marker,
   doppelter Marker, ungeordnete Folge oder Capüberschreitung ergeben
   `NOT_PROVEN`; es gibt keine Wiederholung oder automatische Erweiterung.
4. Jedes Actorereignis wird über die caller-/producerseitig festgelegte
   Session-/Request-/Tokenbindung und die geprüfte Statementidentität der
   Fensterpopulation zugeordnet. Der konkrete XE-Katalog muss je Zielbuild
   bestätigen, dass alle erforderlichen Start-/Endeventfelder und Actions
   vorhanden sind. Ein abweichender oder unvollständiger Katalog beendet den
   Kandidaten vor der Messung als `NOT_PROVEN`.
5. Für die Query-Store-Verknüpfung werden Queryhash und Planhash nur verwendet,
   wenn die aktuelle markergebundene Datenbank genau einen erwarteten
   Query-/Planrecord für den Hashverbund enthält. Null oder mehrere Kandidaten,
   Planhashabweichung, Kontextsettingskonflikt oder Query-Store-Read-only/Drop
   ergeben `NOT_PROVEN`. Hashes sind Korrelationswerte und keine langlebige
   oder globale Identität.
6. Resultcount wird weiterhin gegen die actorgebundene tatsächliche
   `#Actual`-Evidenz geprüft. Das per-Fenster-Executioncount-Oracle stammt in
   diesem Kandidaten aus vollständigen XE-Abschlussereignissen. Query-Store-
   Aggregatzahlen dürfen nur als getrenntes Konsistenzoracle über die gesamte
   passend gebundene Population genutzt werden, wenn ein unabhängiger Vertrag
   deren Vollständigkeit und Sichtbarkeit belegt.

## Evidenzgrenzen und Abbruchregeln

Microsoft dokumentiert Query-Store-Runtimewerte als aggregierte Plan-/Intervall-
Statistik und `query_hash`/`query_plan_hash` als Hashes; Extended Events stellen
Ereignisse, Actions und Ziele bereit. Die dokumentierte `sql_statement_completed`-
Beispielpayload enthält das Statement selbst. Der Kandidat darf deshalb nur
eine pro Build geprüfte Event-/Action-Allowlist verwenden, die Statementtext,
Parameter, Eingabepuffer, Showplan und andere vertrauliche Payload ausschließt.
Wenn ein ausgewähltes Ereignis solche Daten zwingend im Target ablegt und sie
nicht mit der gewählten Eventsemantik ausgeschlossen werden können, ist diese
Methode unter der aktuellen Datenschutzgrenze nicht verwendbar; kein
„nicht ausgegeben“ ersetzt „nicht aufgezeichnet“.

Die Quellen belegen für sich allein weder eine vollständige Markerordnung für
diesen Coordinator noch Hash-Eindeutigkeit, verlustfreie Eventzustellung oder
einen Query-Store-Sichtbarkeitsbarrier. Der Entwurf behandelt diese Punkte daher
als Qualifikationsbedingungen, nicht als zugesicherte Produkteigenschaften.

- Keine Vergleiche zwischen XE-, Query-Store- und `SYSUTCDATETIME()`-Ticks für
  die Fensteraufnahme.
- Keine `NO_EVENT_LOSS`- oder Targeteinstellung ohne separate Deadlock-,
  Backpressure-, Ressourcen- und Cleanupbewertung.
- Kein Query-Store-Flush, Pollingloop, Intervallwechsel, Hashforcierung oder
  Querytextmarker im gemessenen Statement ohne neue Oracle-/Planprüfung.
- Keine Ausgabe von Rohquerytext, Eventpayload, Actorparametern oder Secrets.
  Ein lokales Target wird vor dem Start auf exakt erlaubte Eventfelder geprüft,
  markergebunden und größenbegrenzt; ausschließlich der eigene Collector darf
  es konsumieren. Auf allen Erfolgs-, Fehler-, Timeout- und Abbruchpfaden werden
  die eigene Session und Zielartefakte innerhalb derselben begrenzten
  Cleanupdeadline entfernt und ihre Abwesenheit unabhängig bestätigt.
- Jede Unvollständigkeit, Mehrdeutigkeit, nicht unterstützte Feldstruktur,
  Hashkollision oder Actorabweichung ist `NOT_PROVEN`, nicht `PASS`.

## Begrenzte Kataloginventur

Die erste technische Stufe liest ausschließlich sys.dm_xe_objects,
sys.dm_xe_object_columns, sys.dm_xe_packages und die Engine-Identität. Sie
erfasst Feld- und Actionnamen für sql_statement_starting sowie
sql_statement_completed. Die Katalogabfrage selbst erzeugt keine
Nutzer-/Labordatenbank oder XE-Session, liest keine Eventpayload, verändert
kein Query Store und führt kein Actor-Workload aus. Die SQL-Server-Engine
startet ihre üblichen Systemdatenbanken einschließlich tempdb. Der SQL-Text
und seine Prüfgrenzen liegen in
[dgn007_xe_catalog_probe.sql](../../Tests/Runtime/dgn007_xe_catalog_probe.sql)
und [dgn007_xe_catalog_probe.py](../../Tests/Runtime/dgn007_xe_catalog_probe.py).
Der Workflow validiert diese Grenze auf Pull Requests und main; die tatsächlichen
Buildinventare laufen ausschließlich manuell und seriell auf gepinnten Images.

Lokale Vorversuche auf Docker Desktop für alle drei Image-Digests endeten vor
dem SQL-Ready-Signal (Produktbuilds 15.0.4500.2, 16.0.4305.5 und 17.0.5035.5;
korrigierte Versuche mit Exitstatus 1 und OOMKilled=false). Die Images liefen
in eigenen, begrenzten Containern auf einer internen Bridge ohne Ports oder
Mounts. Die Startlogs enthielten Hinweise zu verweigertem /proc- und dmesg-
Zugriff sowie fehlendem journalctl, belegen diese Hinweise aber nicht als
Ursache. Jeder gestartete Container und das zugehörige Netzwerk wurden
eigentumsgeprüft entfernt. Es wurde nur der Ready-Check SELECT 1 versucht;
die Katalogabfrage und eine XE-Session liefen nicht. Die lokale Engineprobe ist
damit NOT_PROVEN.

Der erste manuelle GitHub-Lauf (`45016650824`) stoppte alle Builds bei der
Imageidentitätsprüfung vor dem Containerstart. Die Korrektur akzeptiert beide
Docker-ID-Darstellungen, prüft weiterhin den exakten Manifestdigest und
Linux/AMD64 und ergänzt Regressionstests. Beim zweiten Lauf
(`45017169620`) starteten die Engines; SQL Server 2022 meldete im Log
„ready for client connections“ und SQLCMD lieferte Exitcode 0 sowie `1` mit
zusätzlichem `(1 rows affected)`. Der Runner verwarf diese erfolgreiche
Antwort, weil der Ready-Check Zeilenzahltext nicht unterdrückte. Die fehlende
`SET NOCOUNT ON`-Anweisung ist korrigiert; die Katalogabfrage lief in keinem
der beiden Läufe. Die Ergebnisse bleiben NOT_PROVEN und sind kein Produkt-
oder XE-Metadatenbefund.

## Synthetische Statement-Payload-Datenschutzprobe

Der manuelle Kataloglauf `45018450462` bestand für die gepinnten Builds
15.0.4500.2, 16.0.4305.5 und 17.0.5035.5. Die beiden ausgewählten
Statementereignisse liefern in allen Builds das Feld `statement:data` sowie
die konfigurierbaren Felder `collect_statement` und
`collect_parameterized_plan_handle`. Das Kataloginventar bestätigt außerdem
`event_sequence`, `database_id`, `query_hash`, `query_plan_hash` und
`session_id`; verfügbare Aktionen `sql_text` und `tsql_stack` werden nicht
aktiviert. Die Inventare waren über alle drei Builds identisch.

Der nächste enge Gate startet je Build in der eigenen digestgebundenen
Wegwerfinstanz genau eine temporäre XE-Session und führt ein festes synthetisches
Statement aus. Für Start- und Abschlussereignis werden
`collect_statement=(0)` und `collect_parameterized_plan_handle=(0)` gesetzt;
`sql_text` und `tsql_stack` bleiben ausgeschlossen. Ein begrenzter
`ring_buffer` mit `ALLOW_SINGLE_EVENT_LOSS` dient nur zur Prüfung, ob der
Ereignistext tatsächlich leer bleibt. Der SQL-Collector gibt weder XML noch
Querytext aus, sondern nur Ereigniszahlen, Vorhandensein der Korrelationsfelder
und die Anzahl nichtleerer Statementwerte. Die Session wird gestoppt, gelöscht
und ihre Abwesenheit bestätigt; anschließend wird der gesamte temporäre
SQL-Server-Container eigentumsgeprüft entfernt.
SQL und Runner stehen in
[dgn007_xe_payload_privacy_probe.sql](../../Tests/Runtime/dgn007_xe_payload_privacy_probe.sql)
und [dgn007_xe_catalog_probe.py](../../Tests/Runtime/dgn007_xe_catalog_probe.py).

Dieser synthetische Gate prüft ausschließlich die Wirkung der
Statementunterdrückung und die erforderlichen Korrelationsactions. Ein
nichtleerer Statementwert, fehlendes Ereignis/Feld, unvollständige Ausgabe oder
fehlendes Cleanup ist `NOT_PROVEN`; der Kandidat wird nicht zu einem
Actor-/Messlauf erweitert. Ein erfolgreicher Test bestätigt noch keine
Markerordnung, Verlustfreiheit, Hashkardinalität, Query-Store-Sichtbarkeit oder
Messgenauigkeit.

## Gates vor Messvertragsimplementierung

Der unabhängige Methodenreview vom 22. November 2026 prüfte den geänderten
Countvertrag, Fenster-/Requestbindung, Payloadschutz und Cleanupentwurf; nach
den Korrekturen fand die Nachprüfung keine offenen P1/P2 im Draft. Das ist keine
Freigabe des Messvertrags oder eines Builds. Der manuelle frische-Runner-Job
führt je Build erst die begrenzte read-only Kataloginventur und anschließend
den synthetischen Statementunterdrückungs-Gate aus. Das kurzlebige
CI-Artefakt enthält Engineidentität, Metadatenfeldnamen und nur Ereigniszähler
sowie Privacy-Flags, keine Ereignis-XML oder Statementtexte. Eine
Kataloginventur allein startet weder eine XE-Session noch einen Mess-Lifecycle;
die separate Probe startet nur die temporäre synthetische Datenschutzsession.
Ereignisordnung, Verlust, Hashkardinalität, Query-Store-Sichtbarkeit und
Cleanup bleiben weitere Gates. Es gibt keine Actor-Messung, Demo-ID oder
Runtimequalifikation.

## Quellen

- [`SRC-027`: Query Store](../Research/SOURCE_REGISTER.md#src-027) und Microsoft [Query Store collects data](https://learn.microsoft.com/en-us/sql/relational-databases/performance/how-query-store-collects-data?view=sql-server-ver17), [`sys.query_store_query`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-transact-sql?view=sql-server-ver17) sowie [`sys.query_store_plan`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17).
- [`SRC-163`: XE-Metadateninventur](../Research/SOURCE_REGISTER.md#src-163), Microsoft [Quickstart: Extended Events](https://learn.microsoft.com/en-us/sql/relational-databases/extended-events/quick-start-extended-events-in-sql-server?view=sql-server-ver17), [`CREATE EVENT SESSION`](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-event-session-transact-sql?view=sql-server-ver17), [`sys.dm_xe_session_targets`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-xe-session-targets-transact-sql?view=sql-server-ver17) und [Extended Events Targets](https://learn.microsoft.com/en-us/sql/relational-databases/extended-events/targets-for-extended-events-in-sql-server?view=sql-server-ver17).
- [`SRC-031`: tatsächliche Planerfassung](../Research/SOURCE_REGISTER.md#src-031).
