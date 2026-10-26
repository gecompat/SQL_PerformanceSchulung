# Konkurrierende Abfragespeicherzuteilungen erkennen

Diese Lehrnotiz konkretisiert `LO-M06-07` innerhalb des vorhandenen Lernpfads.
Sie erklärt, welche Beobachtung eine wartende eigene Abfrage belegt. Sie ist
keine neue Demo, keine Laufzeitqualifikation und kein Nachweis für einen
konkreten Leistungsengpass.

## Grant-Zustände getrennt lesen

Ein Memory Grant (Abfragespeicherzuteilung) ist Workspace-Speicher, den SQL
Server zur Ausführung etwa für Sortier- oder Hashoperationen anfordert. Eine
Zeile in `sys.dm_exec_query_memory_grants` kann zu einer Anforderung gehören,
die noch wartet, oder zu einer bereits gewährten Zuteilung. Die Existenz einer
aktiven Session, einer laufenden Abfrage oder einer Grant-Zeile allein beweist
deshalb kein Grant-Warten.

Die DMV-Spalten beantworten unterschiedliche Fragen:

| Beobachtung | Bedeutung für die Diagnose |
|---|---|
| `required_memory_kb` | dokumentierte Mindestmenge für den Start der Abfrage |
| `requested_memory_kb` | angeforderte Menge für den Grant |
| `granted_memory_kb` | aktuell gewährte Menge; bei noch nicht gewährtem Request `NULL` |
| `used_memory_kb`, `max_used_memory_kb` | momentane und bislang höchste Nutzung; `max_used_memory_kb` wächst während der Ausführung |
| `grant_time` | `NULL`, solange noch keine Zuteilung erfolgt ist |
| `queue_id`, `wait_order`, `wait_time_ms` | Einordnung und bisherige Wartezeit einer noch wartenden Anforderung |

Ein einzelner früher Nutzungsschnappschuss begründet weder Overgrant noch
Undergrant. Dafür sind die angeforderte und gewährte Menge, die Nutzung bis
zum Ende der Ausführung, der Plan und ein möglicher Spill getrennt zu
betrachten. Memory Grant Feedback betrifft die Anpassung über Ausführungen;
es ersetzt keinen Nachweis des aktuellen Request-Zustands.

## Den wartenden eigenen Request an den Wait binden

Für eine Aussage über `RESOURCE_SEMAPHORE` müssen die grantbezogene Anforderung
und der aktuell wartende Request anhand von `session_id` und `request_id`
zusammenpassen. Die Werte in `@OwnRequests` stammen aus der unabhängigen
Zuordnung der eigenen kontrollierten Ausführung. Die Tabelle ist nur ein
callergebundener Filter; das Eintragen einer beliebigen Session-/Request-ID
beweist keine Eigentümerschaft. Diese read-only-Abfrage zeigt die zugeordneten
Requests, bei denen der Grant noch nicht erteilt wurde und derselbe aktuelle
Request den erwarteten Wait-Typ meldet:

```sql
DECLARE @OwnRequests TABLE
(
    session_id smallint NOT NULL,
    request_id int NOT NULL,
    PRIMARY KEY (session_id, request_id)
);

-- Nur unabhängig zugeordnete session_id/request_id-Paare der eigenen,
-- kontrollierten Ausführung eintragen.

SELECT
    own.session_id AS session_id,
    own.request_id AS request_id,
    mg.request_time,
    mg.grant_time,
    mg.required_memory_kb,
    mg.requested_memory_kb,
    mg.granted_memory_kb,
    mg.used_memory_kb,
    mg.max_used_memory_kb,
    mg.pool_id,
    mg.resource_semaphore_id,
    mg.queue_id,
    mg.wait_order,
    mg.wait_time_ms,
    r.status,
    r.wait_type,
    r.wait_time,
    r.wait_resource,
    rs.available_memory_kb,
    rs.granted_memory_kb AS pool_granted_memory_kb,
    rs.grantee_count,
    rs.waiter_count
FROM @OwnRequests AS own
INNER JOIN sys.dm_exec_query_memory_grants AS mg
    ON mg.session_id = own.session_id
   AND mg.request_id = own.request_id
INNER JOIN sys.dm_exec_requests AS r
    ON r.session_id = mg.session_id
   AND r.request_id = mg.request_id
INNER JOIN sys.dm_exec_query_resource_semaphores AS rs
    ON rs.pool_id = mg.pool_id
   AND rs.resource_semaphore_id = mg.resource_semaphore_id
WHERE mg.grant_time IS NULL
  AND r.wait_type = N'RESOURCE_SEMAPHORE';
```

Das Ergebnis ist eine Momentaufnahme. Ein Treffer bindet den noch nicht
erteilten Grant und den `RESOURCE_SEMAPHORE`-Wait an denselben aktuellen
Request des vorab zugeordneten session-/request-Paars. Er beweist für sich
allein weder, welche anderen Anforderungen die Ressource belegen, noch dass
der Zustand über einen längeren Zeitraum anhält. Kein Treffer bedeutet nur,
dass diese Abfrage in diesem Moment keinen solchen Request gefunden hat.

Als getrennten Kontext liefert
`sys.dm_exec_query_resource_semaphores` pro Resource Pool und Semaphore unter
anderem `available_memory_kb`, `granted_memory_kb`, `grantee_count` und
`waiter_count`. Für einen Konkurrenzbefund müssen wartende und bereits
gewährte Anforderungen zum selben `(pool_id, resource_semaphore_id)` gehören.
Die Zähler dieser Pool-/Semaphore-Zeile müssen `waiter_count > 0` und
`grantee_count > 0` zeigen. Sie identifizieren keine andere Abfrage und
beweisen für sich allein keine Ursache. Die Beobachtungen sind zeitabhängig.
Eine kontrollierte
Konkurrenzuntersuchung muss deshalb die zugehörigen Requests und Poolwerte im
selben engen Beobachtungsfenster erfassen.

Memory Grants werden nach Abschluss der Query-Ausführung freigegeben. Eine
nachgelagerte Pause oder ein später noch sichtbarer Session-Eintrag hält den
Grant-Wait nicht künstlich aufrecht. Ein echter Konkurrenznachweis braucht
gleichzeitig wartende und gewährte Anforderungen im vorgesehenen, begrenzten
Workload. Das bloße Vorhandensein mehrerer Sessions oder ein Spill allein
belegt ihn nicht.

## Umfang und Voraussetzungen

Die Abfragen lesen aktuelle DMV-Zustände; sie erzeugen selbst keine
Konkurrenzlast und verändern keine Konfiguration. Die benötigte Berechtigung
ist versionsabhängig: Microsoft dokumentiert `VIEW SERVER STATE` für ältere
SQL-Server-Versionen und `VIEW SERVER PERFORMANCE STATE` ab SQL Server 2022.
Leere Ergebnisse sind kein Beleg dafür, dass eine Anforderung außerhalb des
Beobachtungszeitpunkts niemals gewartet hat.

Die bestehende Szenariovormerkung `RES-004` bleibt von dieser Lehrnotiz
getrennt. Eine ausführbare Probe benötigt weiterhin eine begrenzte
Konkurrenzlast, korrekte Bindung eigener Requests, tatsächliche Wait-Evidenz,
eine passende Gegenprobe und einen sicheren Abbruch- und Cleanup-Pfad.
Allgemeiner Instanzspeicherdruck bleibt beim getrennten Lernumfang `RES-003`;
der kontrollierte Sort-Spill bleibt in `OPT-013`.

## Quellen

- Microsoft Learn, [sys.dm_exec_query_memory_grants](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-memory-grants-transact-sql?view=sql-server-ver17): wartende und gewährte Requests, Grant-Spalten, Schlüssel und Berechtigungen; Abruf am 2026-10-26.
- Microsoft Learn, [sys.dm_exec_requests](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-requests-transact-sql?view=sql-server-ver17): aktuelle Requests, Session-/Request-IDs und Wait-Spalten; Abruf am 2026-10-26.
- Microsoft Learn, [sys.dm_exec_query_resource_semaphores](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-resource-semaphores-transact-sql?view=sql-server-ver17): Pool-/Semaphore-Scope sowie Grant- und Waiter-Zähler; Abruf am 2026-10-26.
- Microsoft Learn, [Troubleshoot slow performance or low memory issues caused by memory grants](https://learn.microsoft.com/en-us/troubleshoot/sql/database-engine/performance/troubleshoot-memory-grant-issues): Grant-Lebensdauer, `RESOURCE_SEMAPHORE`-Diagnose und Poolkontext; Abruf am 2026-10-26.
