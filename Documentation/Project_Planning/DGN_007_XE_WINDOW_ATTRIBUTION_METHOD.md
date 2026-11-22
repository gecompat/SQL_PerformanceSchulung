# DGN-007 – Methodenentwurf für XE-Fensterzuordnung

| Merkmal | Wert |
|---|---|
| Status | `METHOD_DRAFT` – keine Änderung an SQL, Demo oder Runtime freigegeben |
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
2. Pro Fenster schreibt der Coordinator einen eindeutigen Beginmarker, führt
   die festgelegte Menge an Actorrequests aus und schreibt danach den
   Endmarker. Marker und Actorereignisse müssen dieselbe monoton geordnete
   `event_sequence`-Spur belegen; Wandzeit wird nur diagnostisch ausgegeben und
   nicht zum Einschlussvergleich benutzt.
3. Nach dem Endmarker wird die XE-Session regulär gestoppt und ihr vollständiger
   bounded Targetinhalt gelesen. Das Fenster ist nur vollständig, wenn genau
   beide erwarteten Marker, die erwartete Zahl von Actorabschlüssen und keine
   Verlust-/Truncationanzeige vorliegen. Eventverlust, fehlender Marker,
   doppelter Marker, ungeordnete Folge oder Capüberschreitung ergeben
   `NOT_PROVEN`; es gibt keine Wiederholung oder automatische Erweiterung.
4. Jedes Actorereignis wird über die caller-/producerseitig festgelegte
   Session-/Request-/Tokenbindung und die geprüfte Statementidentität der
   Fensterpopulation zugeordnet. Der konkrete XE-Katalog muss je Zielbuild
   bestätigen, dass alle erforderlichen Eventfelder und Actions vorhanden
   sind. Ein abweichender oder unvollständiger Katalog beendet den Kandidaten
   vor der Messung als `NOT_PROVEN`.
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
Ereignisse, Actions und Ziele bereit. Diese Quellen belegen für sich allein
weder eine vollständige Markerordnung für diesen Coordinator noch die
Hash-Eindeutigkeit, verlustfreie Eventzustellung oder einen Query-Store-
Sichtbarkeitsbarrier. Der Entwurf behandelt diese Punkte deshalb als
Qualifikationsbedingungen, nicht als zugesicherte Produkteigenschaften.

- Keine Vergleiche zwischen XE-, Query-Store- und `SYSUTCDATETIME()`-Ticks für
  die Fensteraufnahme.
- Keine `NO_EVENT_LOSS`- oder Targeteinstellung ohne separate Deadlock-,
  Backpressure-, Ressourcen- und Cleanupbewertung.
- Kein Query-Store-Flush, Pollingloop, Intervallwechsel, Hashforcierung oder
  Querytextmarker im gemessenen Statement ohne neue Oracle-/Planprüfung.
- Keine Ausgabe von Rohquerytext, Eventpayload, Actorparametern oder Secrets.
  Das Target bleibt markergebunden, begrenzt und wird vor Cleanup nur durch
  den eigenen Collector konsumiert.
- Jede Unvollständigkeit, Mehrdeutigkeit, nicht unterstützte Feldstruktur,
  Hashkollision oder Actorabweichung ist `NOT_PROVEN`, nicht `PASS`.

## Gates vor Implementierung

Ein unabhängiger Methoden-/Quellenreview muss zuerst den geänderten
Countvertrag, Eventmarkerfolge, XE-Lossindikatoren, tatsächliche Katalogfelder
und -Actions, Actor-/Requestbindung, Hashkardinalität, Targetobergrenzen,
Datenschutz und Eigentums-/Cleanupverfahren bestätigen. Der Reviewautor ist
nicht unabhängig. Danach braucht jeder Zielbuild eine separat freigegebene
read-only Katalog-/Einzelereignisprobe in einer eigenen Instanz. Erst wenn alle
Builds dieselben Pflichtfelder bereitstellen und die Loss-/Cleanupgrenzen
eingehalten werden, darf ein neuer eng begrenzter Lifecycle-Entwurf geprüft
werden. Es gibt hier keine SQL-Abfrage, keine XE-Session, keine neue Demo-ID
und keine Runtimeausführung.

## Quellen

- [`SRC-027`: Query Store](../Research/SOURCE_REGISTER.md#src-027) und Microsoft [Query Store collects data](https://learn.microsoft.com/en-us/sql/relational-databases/performance/how-query-store-collects-data?view=sql-server-ver17), [`sys.query_store_query`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-transact-sql?view=sql-server-ver17) sowie [`sys.query_store_plan`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17).
- [`SRC-163`: XE-Metadateninventur](../Research/SOURCE_REGISTER.md#src-163), Microsoft [Quickstart: Extended Events](https://learn.microsoft.com/en-us/sql/relational-databases/extended-events/quick-start-extended-events-in-sql-server?view=sql-server-ver17) und [XE catalog views](https://learn.microsoft.com/en-us/sql/relational-databases/extended-events/selects-and-joins-from-system-views-for-extended-events-in-sql-server?view=sql-server-ver17).
- [`SRC-031`: tatsächliche Planerfassung](../Research/SOURCE_REGISTER.md#src-031).
