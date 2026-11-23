# Methodenentwurf: konkurrierende Kompilierung mit `OPTIMIZED_SP_EXECUTESQL`

| Merkmal | Wert |
|---|---|
| Status | `METHOD_DRAFT` – keine Implementierungs- oder Runtimefreigabe |
| Geltungsbereich | Separater, isolierter SQL-Server-2025-Versuch zu gleichzeitigen `sp_executesql`-Aufrufen |
| Bestehende Demo | `QRY-004` bleibt unverändert und qualifiziert dieses Verhalten nicht |
| Produktquellen | `SRC-059`, `SRC-161`, `SRC-162`, `SRC-163` |

## Ziel und Grenze

Dieser Entwurf beschreibt, welche Bedingungen ein späterer Versuch erfüllen muss, bevor eine separate Demo entworfen oder ausgeführt werden kann. Er aktiviert keine Datenbankoption, führt kein SQL aus und behauptet weder eine beobachtete Serialisierung noch einen Leistungsgewinn. Die bestehende Entscheidung `DEFER` in der [SQL-Server-2025-Delta-Prüfung](SQL_SERVER_2025_DELTA_REVIEW.md) bleibt bestehen.

Microsoft dokumentiert, dass die datenbankbezogene Option ab SQL Server 2025 standardmäßig `OFF` ist und die Kompilierung identischer `sp_executesql`-Batchtexte serialisiert. Die verfügbaren Microsoft-Hinweise zu Compile-Locks beschreiben jedoch konkrete Sperrressourcen für Prozeduren und Trigger; daraus folgt keine belegte XE-Ereignis-/Feldzuordnung für dynamische `sp_executesql`-Batches. Diese Zuordnung ist ein vorgelagertes offenes Gate.

## Versuchsdesign nach Methodenfreigabe

1. **Getrennte Arme:** für jede gepaarte Wiederholung zwei frische, markergebundene Datenbanken derselben isolierten SQL Server 2025-Instanz. Schema, synthetische Daten, Kompatibilitätsstufe, Rechte, Statistiken und sonstige Optionen sind identisch; ausschließlich `OPTIMIZED_SP_EXECUTESQL` unterscheidet `OFF` und `ON`. Beide Zustände werden vor und nach jedem Arm verifiziert. Keine serverweite Konfiguration und kein globales Leeren des Plancaches.
2. **Feste Aufrufmenge:** derselbe byteidentische, parametrisierte dynamische Batchtext und dieselbe Parameterdefinition in allen Actors. Parameterwerte variieren dürfen, Batchtext und Datenbankkontext nicht. Eine zweite, absichtlich andere Batchtextgruppe dient nur als Negativkontrolle für die dokumentierte Gleichheitsbedingung.
3. **Synchronisierte Konkurrenz:** feste Actorzahl und Versuchszahl, gemeinsamer Client-Startbarrier, begrenzte Zeitüberschreitung und alternierende Reihenfolge der OFF-/ON-Arme. Die Daten bleiben während der Messfenster unverändert; jede Wiederholung nutzt ein neu provisioniertes, gepaartes Datenbankpaar mit leerem, dokumentiertem Datenbankplanbestand vor dem Startbarrier. Es wird kein Instanzcache geleert. Kein `DBCC FREEPROCCACHE`.
4. **Statistiken:** `AUTO_UPDATE_STATISTICS`- und Async-Einstellungen werden explizit erfasst und in beiden Armen gleich gehalten. Bei aktivierter automatischer Statistikaktualisierung wird die dokumentierte Empfehlung zu `AUTO_UPDATE_STATISTICS_ASYNC` und `ASYNC_STATS_UPDATE_WAIT_AT_LOW_PRIORITY` im Methodenreview bewertet. Statistikfrische und ein möglicher Lauf mit asynchron veralteten Statistiken dürfen nicht verschwiegen oder zwischen Armen vermischt werden.
5. **Evidenzbindung:** Im isolierten Kataloglauf auf Build `17.0.5065.9` sind `spexec_batch_compilation_serialization` und `spexec_batch_compilation_serialization_telemetry` vorhanden. Beide führen `database_id` und `object_id`; das Telemetrieereignis zusätzlich `plan_handle` und `sql_handle`. `sql_statement_post_compile` führt unter anderem `duration`, `cpu_time`, `is_recompile`, `statement` und `object_name`. Die Actions `database_id`, `query_hash`, `query_plan_hash`, `session_id`, `sql_text` und `tsql_stack` sind katalogisiert. Das ist die Kandidatenmenge für den nächsten Review, kein Nachweis tatsächlicher Auslösung oder zuverlässiger Zuordnung für dynamische `sp_executesql`-Batches. Vor Implementierung muss ein unabhängiger Methodenreview auf dem exakten Enginebuild verifizieren, welche Ereignisse und Felder Kompilierung, Datenbank, Batchidentität, Session, Zeitfenster und relevante Waits zuverlässig binden. Die Session muss eng gefiltert, zeitlich begrenzt und nachweislich gestoppt/entfernt werden. Plan-Cache-Evidenz wird nur als ergänzende Zuordnung verwendet; sie allein beweist keine Zahl gleichzeitiger Kompilierungen.
6. **Auswertung:** OFF muss im ausgerichteten Zeitfenster mehrere tatsächliche Kompilierungen für die identische Batchgruppe nachweisen, bevor die Kontrollbehauptung zulässig ist. Für ON sind konkurrierende Compile-Waits und anschließende Planwiederverwendung mit batch- und zeitgebundener Evidenz zu belegen. Die abweichende Batchtextgruppe prüft, dass nicht fälschlich alle Texte als identisch behandelt werden. Ergebnisse, Fehler, Latenzverteilung, Compileaktivität und Waits werden getrennt berichtet; es gibt keinen vorab behaupteten Gewinner oder absoluten Performancegrenzwert.
7. **Abbruch und Cleanup:** fehlende Ereignisfelder, nicht eindeutige Batchzuordnung, fehlgeschlagene Barriere, Timeout, unerwartete Abweichung zwischen Armen oder unvollständiger Cleanup ergeben `NOT_PROVEN` beziehungsweise einen expliziten Skip-/Failstatus. Vorher-/Nachherzustand aller Datenbankoptionen, XE-Session, Datenbanken und Testobjekte wird geprüft. Der Cleanup darf nur vollständige Projekt-/Vertrags-/Demo-/RunToken-Marker entfernen.

## Kandidat für die Beobachtung von Wartezeiten

Die Katalogprobe erfasst zusätzlich `sqlos.wait_info` und den numerischen
Schlüssel von `LCK_M_X` aus `sqlos.wait_types`. Microsoft zeigt diese
Paket- und Map-Zuordnung in der [Extended-Events-Dokumentation zu Waits](https://learn.microsoft.com/en-us/sql/database-engine/availability-groups/windows/always-on-wait-types?view=sql-server-ver17).
Der Pilot braucht eine eindeutige Zuordnung des Waits zu einem teilnehmenden
Request, dem Batch und einer Compile-Sperrressource. `LCK_M_X` beschreibt den
Sperrmodus. Die konkrete Ursache bleibt bis zur Korrelation offen.

## Zuordnung von Request, Kompilierung und Sperrwartezeit

Der Pilotkandidat verwendet je Actor eine eigene Verbindung ohne mehrere
gleichzeitig aktive Requests. Er ruft `sp_executesql` direkt als RPC auf.
Der dynamische Batch enthält genau ein synthetisches, schreibfreies
Statement. Alle Verbindungen verwenden dieselbe Identität, Sprache,
Transaktionsisolation und dieselben SET-Optionen. Vergleiche die wirksamen
Cache-Attribute innerhalb des jeweiligen Arms. Der dokumentierte Cache-Key
umfasst weitere Attribute neben dem Batchtext.
[Microsoft-Referenz zu Planattributen](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-exec-plan-attributes-transact-sql?view=sql-server-ver17).

| Evidenz | Annahmeregel für den Pilotkandidaten |
|---|---|
| Requestgrenzen | Binde RPC-Start und -Ende an die eigene Datenbank, den Actor und genau einen Aufruf. Die gehashte Batch-/Parameterdefinition, der bekannte synthetische Statementmarker und der erwartete RPC-Typ müssen übereinstimmen. Nutze Ereignisreihenfolge aus derselben XE-Session. Fehlende oder doppelte Grenzen machen die betreffende Actor-Spur unvollständig. |
| OFF-Kompilierung | Verlange für das markierte Statement mindestens zwei getrennte Erstkompilierungen in Requests verschiedener Actors. Eventfelder und ausgewiesene Zeitsemantik müssen auch dann echte Kompilierungsüberlappung belegen, wenn die äußeren RPC-Fenster überlappen. Ohne belegten Compilebeginn oder nachgewiesenen Bezug der Compile-Dauer zum Zeitpunkt des Ereignisses bleibt die Überlappung `NOT_PROVEN`. |
| ON-Sperrwartezeit | Ein Actor muss im eigenen RPC-Fenster einen Wait des Buildschlüssels für `LCK_M_X` auf einer eindeutig gebundenen Compile-Ressource derselben Datenbank zeigen. Begin/End-Paarung, Actor und Ressourcenbeschreibung müssen eindeutig sein. `wait_resource_desc` ist ein Kandidatenfeld. Fehlt der Subressourcennachweis in XE, kann ein zeitnahes, eindeutiges DMV-Recordpaar ihn beisteuern. Ein flüchtiger Lock-Adresswert überlebt nur innerhalb der Erhebung, in der die Adresse gelesen wurde. |
| Abgrenzung | Microsoft dokumentiert `OBJECT.COMPILE` für gespeicherte Prozeduren. Die dynamische Batchressource und der Bezug zum laufenden Compile-Actor müssen im Pilot separat belegt werden. Ein beliebiger X-Wait, ein Cacheinsert oder ein Serialisierungsereignis allein genügt nicht. Eine Gegenprobe mit gewöhnlicher exklusiver Datensperre und eine zweite Batchidentität müssen von der Annahmeregel abgewiesen werden. |
| ON-Planwiederverwendung | Binde den Plan des ersten erfolgreichen Compile-Actors und den Plan der späteren Statementausführung desselben Batchtexts an denselben eindeutigen Planhandle innerhalb dieses Arms. Prüfe den Handle gegen Cacheattribute und Statementidentität. Ein Hash allein genügt nicht. Ein fehlender, unbrauchbarer oder nachweislich zum äußeren RPC gehörender Handle ergibt `NOT_PROVEN`. |
| Vollständigkeit | Unbekannte Ressourcenformate, nicht eindeutige Actor- oder Batchbindung, Eventverlust, Trunkierung und unbestätigter Abbau verhindern einen positiven Befund. Die Ressourcenerhebung exportiert nur die normalisierten Befunde aus dem synthetischen Lauf. |

Die DMV-Route orientiert sich am dokumentierten Join von
`sys.dm_tran_locks.lock_owner_address` mit
`sys.dm_os_waiting_tasks.resource_address`. Die Stichprobe muss während des
Wartens erfolgen. Fehlt sie bei einem kurzen Wait, bleibt der Ressourcenbezug
offen. Die Katalogprobe erfasst die zusätzlich benötigten RPC-/Statement-
Kandidaten und möglichen Actions auf dem festgeschriebenen Image. Die
Kombinierbarkeit der Events, deren tatsächliche Payload und der direkte
Ressourcennachweis bleiben separate Pilotfragen.
[Microsoft-Referenz zu Sperrressourcen](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-tran-locks-transact-sql?view=sql-server-ver17).

## Gates vor einer Implementierung

- Unabhängiger Methodenreview bestätigt Buildbindung, Ereignis-/Feldvertrag, Auswertungsregeln, Statistikbehandlung, Sicherheitsklasse und Restore.
- Ein Wegwerfziel mit SQL Server 2025 und reproduzierbarem Cleanup ist verfügbar. SQL Server 2019/2022 führen keinen Versuch aus; falls sie im späteren Runner auftauchen, muss der Versions-Skip vor jeder Mutation erfolgen.
- Der vollständige Versuch ist auf dem freigegebenen Build zunächst pilotiert. Fehlende oder mehrdeutige Evidenz bleibt `NOT_PROVEN`; sie darf nicht durch eine Quelltextannahme oder ältere `QRY-004`-Ergebnisse ersetzt werden.
- Erst nach bestandenen Gates werden eigene Demo-ID, ausführbarer Vertrag, Tests und Runtime-Matrix vorgeschlagen. Dieser Entwurf erteilt diese Freigaben nicht.

## Quellen und Aussagegrenzen

- `SRC-059` wurde am 22. November 2026 erneut geprüft: Microsoft Learn bestätigt die Verfügbarkeit ab SQL Server 2025, den Default `OFF`, die Serialisierung identischer Batches (Parameterunterschiede ausgenommen), das Warten weiterer Sessions auf den Compile-Lock und die Empfehlung zu asynchronen Statistikupdates samt `ASYNC_STATS_UPDATE_WAIT_AT_LOW_PRIORITY`, wenn Auto-Update-Statistiken aktiv sind. Die [Konfigurationsreferenz](https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-database-scoped-configuration-transact-sql?view=sql-server-ver17) bestätigt Option, Geltungsbereich und Default; die [sp_executesql-Referenz](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-executesql-transact-sql?view=sql-server-ver17#optimized_sp_executesql) beschreibt das Verhalten und die Statistikempfehlung.
- `SRC-161` beschreibt Compile-Lock-Diagnosebeispiele für Prozeduren/Trigger. Es ist keine Evidenz für die exakte dynamische Batchressource.
- `SRC-162` weist auf möglichen Diagnoseoverhead breit erfasster Compile-/Showplan-Ereignisse hin; daher sind Filterung und Zeitbegrenzung Teil des Designs.
- `SRC-163` dokumentiert, wie Extended-Events-Pakete, Ereignisse, Actions und deren Metadaten aus den XE-Systemkatalogen gelesen werden. Die Microsoft-Dokumentation zu [`sys.dm_xe_object_columns`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-xe-object-columns-transact-sql?view=sql-server-ver17) beschreibt die Metadatenspalten und deren Typen; sie sagt nicht voraus, welche Ereignisse eine konkrete Workload auslöst. Die [read-only Katalogabfrage](../../Tests/Runtime/optsp_xe_catalog_probe.sql) wurde am 17. und erneut am 23. November 2026 in kurzlebigen SQL-Server-2025-CI-Containern ausgeführt. Beide Läufe meldeten Build `17.0.5065.9`, Edition `Enterprise Developer Edition (64-bit)` und Image-Digest `sha256:05644dad1266ca3d445d1e8f6d2ebb9a6a03df9a39376e0f7b48917356dca9d9`; der aktuelle Detailbeleg ist CI-Lauf [45165364360](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/45165364360). Die Inventur fand `spexec_batch_compilation_serialization` mit `database_id`/`object_id`, das Telemetrieereignis zusätzlich mit `plan_handle`/`sql_handle`, `sql_statement_post_compile` mit unter anderem `duration`, `cpu_time`, `is_recompile`, `statement` und `object_name` sowie die katalogisierten Actions `database_id`, `query_hash`, `query_plan_hash`, `session_id`, `sql_text` und `tsql_stack`. Das belegt nur verfügbare Ereignis-/Action-Schemas auf genau diesem Build; es belegt weder tatsächliche Auslösung bei dynamischem `sp_executesql` noch konkurrierende Compile-Waits oder Planwiederverwendung. Die Probe hat keine XE-Session angelegt und die Datenbankoption nicht aktiviert.

Der Entwurf ist ein prüfbarer Methodenstand, keine Produkt- oder Enginequalifikation. Die menschliche Generalprobe ist ausgeschlossen.
