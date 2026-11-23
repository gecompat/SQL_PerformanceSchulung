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

## Eingabepuffer als Diagnose für den Aufrufweg

Der [Komponententest](../../Tests/Runtime/Invoke-OptspInputBufferComponent.ps1)
führt denselben synthetischen Parameteraufruf einmal mit
`SqlCommand.CommandType = StoredProcedure` und einmal als T-SQL-Batch
mit `EXEC sys.sp_executesql` aus. Eine zweite Verbindung liest jeweils
den Eingabepuffer der noch offenen Actor-Session. Das Skript erwartet den
Ergebniswert 37 und gibt nur die beiden beobachteten Ereignistypen und
klassifizierten Textformen aus.
[Microsoft-Referenz zu SqlCommand.CommandType](https://learn.microsoft.com/en-us/dotnet/api/system.data.sqlclient.sqlcommand.commandtype?view=netframework-4.8)
· [Microsoft-Referenz zu sys.dm_exec_input_buffer](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-input-buffer-transact-sql?view=sql-server-ver17).

Auf Build `17.0.5065.9` meldete `sys.dm_exec_input_buffer` für beide
Aufrufe `Language Event`. Beim Aufruf als Stored Procedure stand im
Puffer die innere Anweisung mit ihrer Parameterdefinition. Beim
Textaufruf enthielt er den äußeren `EXEC`-Batch. Damit ist der
Ereignistyp des Eingabepuffers für den Nachweis eines direkten RPC
ungeeignet. Die Ereignisgrenzen lassen sich mit Extended Events prüfen.

Der Test lief mit PowerShell 7.6.9 unter Windows und
`System.Data.SqlClient` in Assemblyversion `4.6.1.6` gegen den
festgeschriebenen Wegwerfcontainer. Für eine Wiederholung wird die
ausschließlich lokal erreichbare Instanzadresse übergeben.
`SQLCMDPASSWORD` enthält das Laufpasswort der Testinstanz.

```powershell
pwsh -NoProfile -File Tests/Runtime/Invoke-OptspInputBufferComponent.ps1 -Server $LoopbackInstanz -ConfirmDisposableInstance
```

Der Wert von `$LoopbackInstanz` folgt dem SQL-Server-Format
`127.0.0.1,<Port>`. Der Test prüft Build, Developer-Edition, leere
Instanz und `OFF` im aktuellen Datenbankkontext. Im Komponentenlauf
wurden beide Verbindungen geschlossen und der eigene Container entfernt.
Die Katalog-CI prüft die Syntax des PowerShell-Skripts.

### Requestgrenzen mit Extended Events

Mit `-CheckXeRequestBoundaries` prüft derselbe Komponententest die
Aufrufgrenzen auf Build `17.0.5065.9`. Der Stored-Procedure-Aufruf erzeugte
`rpc_starting` und `rpc_completed`. Der äußere T-SQL-Batch erzeugte
`sql_batch_starting` und `sql_batch_completed`. Der Test verlangt diese
Reihenfolge sowie dieselbe Actor-Session und Datenbank (`master`).
Bei beiden RPC-Ereignissen prüft er `object_name` auf `sp_executesql` und
`statement` auf die synthetische Anweisung. Bei beiden Batch-Ereignissen
muss `batch_text` mit dem äußeren `EXEC`-Batch übereinstimmen.

```powershell
pwsh -NoProfile -File Tests/Runtime/Invoke-OptspInputBufferComponent.ps1 -Server $LoopbackInstanz -ConfirmDisposableInstance -CheckXeRequestBoundaries
```

Die kurzlebige XE-Sitzung filtert auf die eigene Actor-Session und hält
die Ereignisse in einem begrenzten Ringpuffer im Speicher. Der Test prüft
Ereignisverlust, abgeschnittene Daten und das Entfernen der Sitzung aus
beiden Systemansichten. Die Ausgabe enthält nur die geprüften Ereignisnamen
und den Cleanup-Status. Die Datenbankoption bleibt `OFF`.
Für den Pilotversuch sind noch die Compile-Intervalle, die Bindung von
Wait und Sperrressource sowie die Planwiederverwendung im gepaarten
OFF-/ON-Lauf zu belegen.
[Microsoft-Referenz zum Ringpuffer](https://learn.microsoft.com/en-us/sql/relational-databases/extended-events/targets-for-extended-events-in-sql-server?view=sql-server-ver17).

### Zuordnung einer Erstkompilierung zum dynamischen Batch

`-CheckXeCompileIdentity` erfasst zusätzlich
`sql_statement_post_compile` mit `collect_statement = 1`. Der Actor
sendet zuerst Batch A per RPC, wiederholt A mit einem anderen Parameter
und sendet dann den eigenständigen Batch B mit derselben Parameterdefinition.
Beide Batchtexte liefern den Parameterwert zurück und enthalten
unterschiedliche Ausdrücke im Anweisungstext. Der abschließende äußere
`EXEC`-Batch verwendet noch einmal A.

Auf Build `17.0.5065.9` lag je ein Erstkompilierungsereignis zwischen
Start und Ende des ersten A-RPC und des B-RPC. Beim zweiten A-RPC
und beim anschließenden äußeren Batch trat in dieser Spur kein weiteres
`sql_statement_post_compile` auf. Der Test prüft den Anweisungstext
zeichengetreu bis vor das abschließende Semikolon, einschließlich des
unterscheidenden Ausdrucks. Ein Kommentar als Kennzeichen war in der
Vorprobe im Compile-Ereignis entfallen.

```powershell
pwsh -NoProfile -File Tests/Runtime/Invoke-OptspInputBufferComponent.ps1 -Server $LoopbackInstanz -ConfirmDisposableInstance -CheckXeCompileIdentity
```

Die Erhebung bleibt auf die eigene Actor-Session und den verifizierten
Wegwerfcontainer mit `OPTIMIZED_SP_EXECUTESQL = OFF` beschränkt. Für
die Messung konkurrierender Kompilierungen fehlen weiterhin ein
nachgewiesener Compilebeginn und die Unsicherheitsgrenze für die
Umrechnung der Ereignisdauer in ein Intervall.

### Überlappung anhand von Kardinalitätsschätzungen

Der [Komponententest](../../Tests/Runtime/Invoke-OptspCompileWitnessComponent.ps1)
sendet zwei unterscheidbare synthetische Batches auf getrennten
RPC-Verbindungen. Beide haben eine einzige Anweisung und verwenden fünf
verknüpfte Tabellenwertkonstruktoren. Die Datenbankoption bleibt `OFF`.
Im parallelen Lauf können beide RPCs ausstehen. Im Kontrolllauf startet
der zweite RPC erst, nachdem der erste vollständig zurückgekehrt ist.
Für jeden Aufruf des Skripts ist eine frische Instanz erforderlich, damit
beide Batches erstmals kompiliert werden.

```powershell
pwsh -NoProfile -File Tests/Runtime/Invoke-OptspCompileWitnessComponent.ps1 -Server $LoopbackInstanz -ConfirmDisposableInstance
# In einer zweiten frischen Instanz
pwsh -NoProfile -File Tests/Runtime/Invoke-OptspCompileWitnessComponent.ps1 -Server $LoopbackInstanz -ConfirmDisposableInstance -SequentialControl
```

Die Auswertung verlangt mindestens zwei Schätzereignisse aus
`query_optimizer_estimate_cardinality` innerhalb jeder nachgewiesenen
Erstkompilierung. Sie bindet sie an denselben RPC, dieselbe Datenbank
und den zugehörigen Batchtext. Die Ereignisfolgen müssen sich in
`event_sequence` kreuzen. Die anhand der ersten und letzten
Schätzung je Batch gebildeten Zeitfenster müssen sich auch anhand der
XE-Zeitstempel strikt überschneiden. Die Zeitspanne in 100-ns-Ticks ist
eine Differenz der aufgezeichneten Labels. Ihre Darstellung kalibriert
die Uhr nicht. `creation_time` wird bei der Berechnung nicht verwendet.
In der Vorprobe lag dieses Feld vor dem zugehörigen RPC-Start.

Auf Build `17.0.5065.9` lieferten beide Batches im parallelen und
sequenziellen Komponentenlauf jeweils 48 Schätzereignisse. Der parallele
Lauf zeigte eine Überlappung, die sequenzielle Kontrolle keine. Ein
paralleler Lauf ohne beobachtete Überlappung liefert `NOT_PROVEN`.
Die CE-Ereignisse enthalten XML-Payload. Das Skript hält sie ausschließlich
im gefilterten XE-Ringpuffer und im Client-Arbeitsspeicher. Es gibt nur
Anzahl, Reihenfolge, Zeitdifferenz und Cleanup-Status aus.
Mit `-IdenticalBatch` senden beide Verbindungen denselben Batchtext,
dieselbe Parameterdefinition und denselben Wert als RPC. Der
Komponententest prüft für beide Requests Start und Ende sowie das
synthetische Ergebnis. Eine vollständige Spur aus RPC-Start und RPC-Ende
allein ist für diese Variante zulässig. Eine erfasste Erstkompilierung
erfordert weiterhin mindestens zwei gebundene Schätzereignisse.
Der sequenzielle Kontrolllauf verlangt genau eine Erstkompilierung im
ersten Request. Jede Variante läuft auf einer eigenen frischen Instanz.

Auf Build `17.0.5065.9` mit `OFF` beobachtete der parallele Lauf mit
identischem Batchtext zwei Erstkompilierungen mit je 48 Schätzereignissen.
Ereignisreihenfolge und XE-Zeitstempel bestätigten die Überlappung.
Der sequenzielle Lauf meldete eine Erstkompilierung mit 48
Schätzereignissen. Die Zeitdifferenz ist nur bei zwei Kompilierungen
definiert. Die serielle Kontrolle prüft zusätzlich den wiederverwendeten
Plan. Beide `sp_statement_completed`-Ereignisse müssen innerhalb ihrer
RPC-Spuren das exakte innere Statement und denselben Handle melden. Der
Handle muss zum eindeutigen `Prepared`-Eintrag in derselben Datenbank
passen. Die Cacheabfrage bindet Batchtext und Parameterdefinition über
Text- und Längengleichheit. Auf diesem Build sind die beobachteten
Statement-Handles 44 Byte lang und stehen im XML als Hex ohne Präfix.
Der Test gibt ausschließlich den Befund zur Wiederverwendung aus.

Die Erkundung lieferte für diese Aufrufe keine
`sql_statement_completed`-Ereignisse. `sp_cache_hit` lieferte beim zweiten
Aufruf einen 64-Byte-Wert mit Null-Padding hinter den 44 Cache-Bytes.
Der direkte Abgleich mit `sp_statement_completed` nutzt die vollständigen
44 Byte des zum inneren Statement gehörenden Handles.
Für den gepaarten Versuch fehlen die ON-Kompilierungssperre, die
zugehörigen Wartezeiten und der Nachweis der Wiederverwendung unter
Konkurrenz.
[Microsoft-Referenz zur Kardinalitätsschätzung und zum XE-Ereignis](https://learn.microsoft.com/en-us/sql/relational-databases/performance/cardinality-estimation-sql-server?view=sql-server-ver17).

## Statische Auswertung normalisierter Befunde

Für den Methodenreview steht eine [SQL-freie Auswertung je Versuchsarm](../../Tests/Runtime/optsp_compile_evidence.py) bereit. Sie vergleicht tatsächliche Compile-Intervalle und verlangt im ON-Arm einen dem Compile-Actor zugeordneten Wait, der während der Kompilierung beginnt und bis zu deren Ende reicht. Alle erfolgreichen Folgeaufrufe müssen denselben Statement-Planhandle verwenden. Die [synthetischen Gegenproben](../../Tests/Static/test_optsp_compile_evidence.py) decken unter anderem nacheinander liegende Kompilierungen bei überlappenden RPCs, fremde Sessions, gewöhnliche X-Waits und abweichenden Batchtext ab.

Der spätere Producer muss die gemeinsame Zeitbasis und die Compile-Grenzen, Statement-/Cache-Identität, Wait-Ressource und Blockerbindung aus qualifizierten Engine-Daten liefern. Die Auswertung erwartet außerdem eine vollständige Spur der vorab registrierten Actors und eine geprüfte Erfassung samt Abbau. Die Tests validieren die Annahmeregeln mit synthetischen Eingaben. Ein positiver Einzelarm ersetzt weder den gepaarten Lauf noch dessen Negativkontrollen. Die tatsächliche XE-Payload und der Ressourcenbezug des dynamischen Batches bleiben offen.

Die Auswertung verbindet Wait und Sperrbesitz anhand desselben
datenbankbezogenen Ressourcenschlüssels. Sie akzeptiert den ON-Arm nur,
wenn genau ein erfasstes Besitzintervall diese Wartezeit überlappt. Der
kompilierende Request muss die Ressource bereits beim Wait-Beginn halten.
Sein Besitz muss mindestens bis zum Ende der Kompilierung reichen.
Eine konkurrierende Zuordnung, ein anderer Schlüssel oder ein
unvollständiges Besitzintervall ergeben `NOT_PROVEN`.

Der Producer muss deshalb die erteilte Sperre mit Erwerb und Freigabe
an denselben Request binden und Ressourcentyp sowie Identität mit der
Wait-Spur abgleichen. Eine einzelne DMV-Stichprobe kann bei der
Klassifikation helfen. Das vollständige Besitzintervall benötigt
weiterführende Evidenz. Aus dem Modus `LCK_M_X` allein folgt kein
Compile-Lock.
[Microsoft-Referenz zu den Spalten einer Sperrressource](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-tran-locks-transact-sql?view=sql-server-ver17).

### Nachweis für ein OFF/ON-Paar

Die [Paarprüfung](../../Tests/Runtime/optsp_compile_evidence.py) akzeptiert
zwei für sich nachgewiesene Arme erst mit übereinstimmendem Versuchsprofil.
Vor und nach jedem Arm müssen Instanzidentität, Engine-Startkennung und
Datenbankbindung konstant sein. Die beiden Datenbanken erhalten getrennte
IDs unter demselben Engine-Start. Die gelesene Option muss in beiden
Messungen zum jeweiligen Arm passen. Der aus dem Zustand gebildete
SHA-256-Wert umfasst Schema, Daten, Rechte, Statistiken, effektive
Session- und sonstige Datenbankoptionen. Instanz-, Datenbank- und
Actor-IDs sowie die untersuchte Option gehen separat in die Prüfung ein.

Vor der gemeinsamen Startfreigabe verlangt der Vertrag einen tatsächlich
leeren Datenbankplanbestand und die vollständige Teilnehmerliste der
Barriere. Für beide Arme müssen die Batch- und Parameterdefinition,
die Anzahl der Teilnehmenden sowie deren logische Parameter- und
Ergebniszuordnung übereinstimmen. Die Parameterwerte unterschiedlicher
Teilnehmender dürfen voneinander abweichen. Der Producer muss pro
Aufruf den erfolgreichen Abschluss und das erwartete synthetische
Ergebnis belegen, bevor er dessen Zuordnung hasht.

Die [read-only Katalogprobe](../../Tests/Runtime/optsp_xe_catalog_probe.sql)
liest die untersuchte Option und die Konfiguration der Statistikupdates
im aktuellen Datenbankkontext. Sie erfasst auch Kompatibilitätsstufe und
Datenbank-ID. Auf dem festgeschriebenen Container lieferte die Abfrage
getrennte Records für `master` und `tempdb`. In beiden stand die Option
auf `0`, das automatische Erstellen und Aktualisieren von Statistiken
auf `1` und die Optionen für asynchrone Updates und deren niedrige
Priorität auf `0`. Der spätere Collector muss diese Werte vor und nach dem
jeweiligen Arm erheben und die übrigen Profilmerkmale ergänzen.
[Microsoft-Referenz zum Katalog der Datenbankoptionen](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-scoped-configurations-transact-sql?view=sql-server-ver17).

Ein akzeptiertes Paar ist die Grundlage für die vorab festgelegten
Wiederholungen und die Negativkontrollen. Die Regressionen prüfen die
Zuordnung und Ablehnung anhand synthetischer Records. Die echte
Zeitbasis, der Inhalt der Profile und die aktuelle Planidentität
müssen weiterhin auf dem Pilotbuild erhoben werden.


## Zeiteinheiten und Planhandle auf Build 17.0.5065.9

Der [Kataloglauf 45188183551](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/45188183551) dokumentiert unterschiedliche Einheiten in den Feldbeschreibungen.

| Ereignis | Relevante Metadaten des Builds |
|---|---|
| `sql_statement_post_compile` | `duration` und `cpu_time` in Millisekunden. Der Statementtext muss über `collect_statement` angefordert werden. |
| `sqlos.wait_info` | `duration` in Millisekunden. `opcode` und die Ressourcenbeschreibung stehen als separate Felder zur Verfügung. |
| `sql_statement_completed` | `duration` und `cpu_time` in Mikrosekunden. `collect_parameterized_plan_handle` schaltet ein separates Feld für den Handle des parametrisierten Plans frei. |
| `sp_cache_hit` | `collect_plan_handle` schaltet das Feld für den Handle des Cacheeintrags frei. Der Katalog beschreibt den Eintrag als Objekt aus dem Cache. |
| `spexec_batch_compilation_serialization_telemetry` | `plan_handle` und `sql_handle` bezeichnen den Cacheeintrag. |

[Microsoft Support zu `sql_statement_post_compile`](https://support.microsoft.com/en-us/servicing/sql/sql-server-2017/cumulative-update/kb4480630-improvement-enhancement-adds-sql-statement-post-compile-extended-event-in-sql-server-2017) beschreibt für SQL Server 2016/2017 das Kompilierungsende als Auslösepunkt und eine eigene Dauer für die Kompilierung. Für den 2025-Pilot sind der Zeitstempelbezug und die Unsicherheit der ganzzahligen Millisekundenwerte auf dem festgeschriebenen Build zu prüfen. Überlappung ist nur belegbar, wenn sie auch unter der bestätigten Unsicherheit besteht. Ein unbestimmter Zeitbezug, fehlende Grenzen oder eine Überschneidung innerhalb der Zeitauflösung ergeben `NOT_PROVEN`.

Die Auswertung kann für jede Zeitgrenze den frühesten und spätesten
möglichen Zeitpunkt auf derselben qualifizierten Uhr übernehmen. Im
OFF-Arm muss der späteste mögliche Start der beiden Kompilierungen
vor ihrem frühesten möglichen Ende liegen. Im ON-Arm muss die
Reihenfolge von Compile-, Wait-, Sperrbesitz- und Statementgrenzen
auch mit den ungünstigsten Werten stimmen. Schon ein weiterer
möglicher Sperrbesitz über dieselbe Ressource verhindert einen
eindeutigen Befund.

Die Dauergrenzen werden nur dann vom Ende abgezogen, wenn der
Producer den Bezug der Dauer zu diesem Ende nachgewiesen hat. Die
Auswertung setzt keine Millisekunden-Rundungsregel und keine
Übereinstimmung zwischen verschiedenen Uhren voraus. Die Tests
verwenden synthetische Zeitgrenzen. Die Messunsicherheit der
SQL-Server-Ereignisse muss im Pilot bestimmt werden.

Die optionalen Handle-Felder sind Kandidaten für einen Abgleich desselben inneren Statements. Dafür braucht der Pilot eine tatsächlich befüllte Payload, die Bindung an den synthetischen Marker sowie den Abgleich mit Batchtext und Cacheattributen.

Die Katalogprobe löst die möglichen Feldwerte über den Typnamen und die zugehörige Paket-GUID auf. Auf Build `17.0.5065.9` listet `compile_synchronization.query_type` ausschließlich `Adhoc` (Schlüssel 0). Das Feld `step` beschreibt Cache-Lookups, das Einfügen eines Synchronisationsmarkers bei `CompileStarting` (Schlüssel 8) sowie dessen Zustandswechsel bei `CompileFinished` (Schlüssel 9 und 10). Diese Einträge geben keinen Zeitpunkt für den Beginn oder das Ende des konkreten parametrisierten RPC-Statements vor. Ein Pilot muss die tatsächliche Auslösung und die Zuordnung zu den inneren Statements belegen. `compilation_stage_statistics` liefert Stufenzähler ohne zugeordnete Start- oder Endpunkte einzelner Statements.

Die Probe bindet `sqlos.wait_info.opcode` an `Begin` (0) und `End` (1) aus der zugehörigen Map. `lock_acquired` und `lock_released` führen beide Datenbank-ID, Sperrmodus, Ressourcentyp, Ressourcenkennungen und die zuschaltbare `resource_description`. Das liefert eine weitere Möglichkeit zur Gegenprüfung der Besitzdauer. Ob die dynamische Compile-Sperre in beiden Ereignissen erscheint und sich mit `wait_resource_desc` auf dieselbe Ressource abbilden lässt, bleibt vor einer positiven Aussage empirisch zu klären.

## Vollständigkeit der XE-Erfassung

Der [Offline-Reader](../../Tests/Runtime/optsp_xe_snapshot.py) prüft die
XML-Ausgabe eines Ringpuffers vor der Zuordnung einzelner Ereignisse. Er
verwirft abgeschnittene Dokumente, verlorene oder verdrängte Ereignisse,
noch ausstehende volle Puffer und doppelte Ereignisnummern.
`package0.event_sequence` dient zur Zuordnung innerhalb derselben
Aufzeichnung. Die Reihenfolge im XML und lückenlose Nummerierung sind
keine Voraussetzungen. Die Zeitstempel bleiben mit bis zu sieben
Nachkommastellen erhalten.
[Microsoft Learn zu Ringpuffer und XML-Trunkierung](https://learn.microsoft.com/en-us/sql/relational-databases/extended-events/targets-for-extended-events-in-sql-server?view=sql-server-ver17)
· [Microsoft Learn zu den Sitzungszählern](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-xe-sessions-transact-sql?view=azuresqldb-current)

Der spätere Collector muss die Zähler derselben Sitzung und die
XML-Ausgabe erfassen, nachdem alle beteiligten Requests abgeschlossen
sind und bevor die Sitzung beendet wird. Ein leerer Zähler für
ausstehende **volle** Puffer belegt allein keinen vollständigen
Dispatch. Der Pilot muss die Terminalereignisse aller erwarteten
Requests wiederfinden und die vollständige Erfassung auf dem
festgeschriebenen Build prüfen, bevor er die Rohdaten verwirft.
Die [synthetischen Regressionstests](../../Tests/Static/test_optsp_xe_snapshot.py)
prüfen das Einlesen. Die zugehörige Zeitbasis und die semantische
Zuordnung der Felder bleiben Gegenstand des Methodenreviews und des
Engine-Piloten.

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
