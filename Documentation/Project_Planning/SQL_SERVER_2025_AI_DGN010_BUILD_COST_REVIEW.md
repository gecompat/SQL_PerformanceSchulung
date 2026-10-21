# DGN-010: getrennte eigene Build-/Dropkosten

Stand: 2026-10-12. TSK-011/CUR-021. Status: PROPOSED, begrenzte private
Folgefrage; vollständige Runtime-/TP-PERF- und Indexnettonutzenabnahme offen.

## Ausgangspunkt und endlicher Umfang

Die [Originalreaderpläne](SQL_SERVER_2025_AI_DGN010_READER_CLOCK_REVIEW.md)
und [INSERT-/Rollbackfenster](SQL_SERVER_2025_AI_DGN010_INSERT_REVIEW.md)
liegen getrennt vor. Ihre Instrumentierung und Zeitbereiche werden hier nicht
wiederholt oder zu einer Gesamtindexbewertung addiert. PR 201 ist vollständig
geschlossen. Auch die Folienfortschritte sind abgeschlossen: PR 204 auf main
7a68bb7261ffbdb21b6cf7ece4d1d88cc1d5bee6, neun Head-/sieben Main-Workflows PASS,
ganzer Tree/FF-main sauber und eigener lokaler/Remote-Branch entfernt.

Fortgeltender Benutzerauftrag zur weiteren lokalen Entwicklung und zu mehr als
zwei nötigen Korrekturzyklen. Dieser neue Schnitt begrenzt sich auf sechs
zusammenhängende Kandidaten, maximal zwölf serielle neue eigene Container,
Checkpoint nach drei und harte Grenze nach sechs Kandidaten. Zwei vollständige
positive Profile desselben stabilen Kandidaten erforderlich. Gemeinsames privates
Ledger, kein Löschen historischer FAILs; Retry nur bei geänderten Nativeinputs
oder neuer konkreter Evidenz. Ein Owner und ein enger unabhängiger Quellenreview
der neuen DDL-/Lease-/Counter-/Stategrenzen, keine Reviewkette. Modell-/Tokenverbrauch
unbekannt. Alte Reader-/INSERT-/Folienbudgets werden nicht zurückgesetzt.

## Feste Effekte und Messbereiche

Eigenes vorhandenes SQL-17.0.5005.3-Image, tatsächlich Developer/CL170; eigener
neuer Container mit voller CID-/Name-/Image-/Ownerbindung, vier CPU (Central Processing Unit; Prozessor)/sechs GiB,
Loopbackendpunkt und ENV-Passwort ohne `-P`. Öffentlicher read-only Preflight,
1000 feste synthetische Rows, Value=Id×3 und 100 F-Payloadbytes. Vorhandene
DB-/Config-/Datei-/Reader-/Markergrenzen unverändert. Kein Provider, Cloud,
ONNX (Open Neural Network Exchange; Austauschformat für Modelle) oder rote Hoständerung. Insgesamt 300 Sekunden einschließlich Startup;
einmalige gemeinsame 60 Sekunden Recovery einschließlich SQL-90/91, frischer
DB-Abwesenheit und vollständigem eigenem Container-/CID-Abbau. Tatsächlicher
Clientendstatus bleibt verbindlich; UNKNOWN erlaubt keine weiteren SQL-Clients.

Je Profil zwei seriell festgelegte CREATE-/DROP-Zyklen, vier DDL-Fenster.
Fester Candidate: `ON lab.SourceRows(Id) INCLUDE(Value,Payload) WITH(MAXDOP=1)`.
Keine freie Modell-DDL (Data Definition Language; Anweisungen zum Definieren und Ändern von Datenbankobjekten). Vor CREATE tatsächliche Abwesenheit; vor DROP exakt
dieselbe gehaltene native Index-/Spaltendefinition aus dem vorigen CREATE.
DB-ID, Source-Object-ID und alle vier vollständigen bytegenauen Eigentumsmarker
vor jedem Fenster binden. Ein passender Name allein autorisiert keinen DROP.

UTC-Elapsed misst den `EXEC sp_executesql`-Bereich der festen DDL. CPU/Reads/
Logical Reads/Writes umfassen die Grenzen des gleichen tatsächlichen Requests
einschließlich Counteraufnahme. Fünfteilige Requestidentität, tatsächlich monotone
Counter, vollständige UTCs und UTF-16-Textdigest bleiben erhalten. Coarse
Requeststart ist nur Identität. Keine isolierte Compile-, Worker-, Log-I/O-,
Commit- oder komplette Lifecyclezeit aus diesen Zahlen ableiten. Gemessene Null
bleibt Null; fehlende Werte oder Trunkierung sind FAIL. N=2 je Operation/Profil
liefert weder p95/p99, Signifikanz noch allgemeinen Indexnettonutzen.

## Ergebnis-, Negativ- und Cleanuporacles

Acht vollständige Source-/Reader-/Indexaufnahmen je Profil, 8000 Source-Rows.
Vier vollständige 13-Key-Statepaare um die vier DDLs und ein weiteres Paar um
die abgewiesene DROP-Gegenprobe: zehn Vollstates/10000 Rows. Nur eigene
Index-/Spaltenpopulation und `SourceRows.modify_date` dürfen sich durch DDL
ändern. Ursprünglicher PK (Primary Key; Primärschlüssel), Rows, Spaltendefinitionen, DB/Config, Dateigrößen,
Readerrechte/-rollen und Propertybytes bleiben unverändert. Tatsächliche
native Index-/Spalten-Leases müssen mit den unabhängigen Vollstates übereinstimmen.

Vorher echte Source-Negative mit 51003 und tatsächlichem Restore über den eigenen
Setupvertrag. Danach DROP auf abwesenden eigenen Candidate muss mit
51003/FAIL_RESULT_CONTRACT vor DDL ablehnen; vollständiger Vor-/Nachstate identisch.
Regulärer markergebundener SQL-90/91-Abbau und anschließend neue unabhängige
DB-/CID-/Namensabwesenheit schließen jedes positive Profil ab. Keine ungeprüfte
SQLrettung oder Zurücksetzung des Cleanupbudgets.

Sieben synthetische reine Gegenproben und CLI-help bestanden; sie prüfen
ausgeführten DDL-Digest, Typ-/Boolalias-, Request-/Counter-/Zeit-/Lease-/Spalten-
und Transportfehler. Enger unabhängiger Quellenreview ohne offene P1/P2; Reviewer
führte keine Tests oder Nativeausführung aus. Nativeergebnis vor Admission offen.
Private Quellen, Vollrecords und Logs bleiben unter ignoriertem Runtime.

## Tatsächlicher stabiler C1-Nachweis

Zwei neue eigene vollständige SQL-17.0.5005.3-Profile bestanden, je 34 Nativecalls.
Insgesamt vier CREATEs/vier DROPs, 16000 vollständige Source-Rows und 20000
vollständige State-Rows. Vier tatsächliche 51003-Negativen: je Source-/Restore
und DROP-ohne-Index. Beide vollständigen Negativstatepaare bleiben unverändert.
Jede CREATE-/DROP-Transition besitzt aktuelle Requestidentität, Textdigest,
monotone Counter und native Vor-/Nach-Lease mit unabhängiger Statebindung.

| Profil | Zyklus | Operation | UTC-Elapsed µs | CPU ms | Reads | Logical Reads | Writes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | CREATE | 12316 | 9 | 0 | 263 | 18 |
| 1 | 1 | DROP | 4102 | 3 | 0 | 105 | 0 |
| 1 | 2 | CREATE | 8142 | 6 | 0 | 228 | 16 |
| 1 | 2 | DROP | 4068 | 3 | 0 | 105 | 0 |
| 2 | 1 | CREATE | 12263 | 9 | 0 | 263 | 18 |
| 2 | 1 | DROP | 4144 | 3 | 0 | 105 | 0 |
| 2 | 2 | CREATE | 8222 | 5 | 0 | 228 | 16 |
| 2 | 2 | DROP | 4048 | 3 | 0 | 105 | 0 |

Alle acht Beobachtungen erhalten, keine Ausreißer-/Nullverwerfung. Dies sind
Requestcounterdeltas, keine Byte-/vollständigen Worker-/Log-I/O-Messungen.
Writes 0 bei DROP beweist keine Abwesenheit späterer oder anderer I/O-Arbeit.
N=2 je Operation und Profil bleibt zu klein für allgemeine Kostenregeln.

Vollständiger markergebundener SQL-90/91-Abbau, frische unabhängige DB-Abwesenheit,
voller CID-/Namensabbau und zusätzliche eigene Labelabwesenheit bestanden.
Beide eigenen Container abwesend, kein UNKNOWN. Tatsächlich identische aktuelle
Ausführungs-/Importquellen und sämtliche Vollrecords rein erneut gebunden;
diese Recordprüfung startete kein SQL. Keine frühere grüne Reader-/DML-Prüfung
wiederholt. Ein Kandidat/zwei Container verbraucht; nicht weiter unverändert testen.

Private Quellen-SHA256 des unabhängig abgeschlossenen Nativekandidaten:

- `costs.py`: 300C95F08FED050DB5C0C79FE7D8707DBAAD1807C03D24B49765877E525F659B
- `probe.py`: 64B951AD86C6A440EDF5C7BB9B939F925699DE292D035BF84B501C9D032CBDBE
- `30_BuildWindow.sql`: DEBB7CFE8E0248E7F6D6781A605EBDA89CF92F59F31C1FE68CC74C4E5D8F2BD5
- `qualify.py`: 4293F592500892034629EAB227A626CE6D23A58E75AAA2C1D685A5E88790FF12

PASS ausschließlich der begrenzten privaten eigenen Build-/Dropbeobachtung.
Öffentliche Producer weiterhin Gesamt-WARN, DGN-010 PROPOSED; volle Runtime/
TP-PERF-/Worker-/Commit-/Nettonutzen-/Modulabnahme offen. Aktuelle Head-/Main-Gates,
PR-Integration, ganzer Tree, FF-main und eigener lokaler/Remote-Branchcleanup
folgen. Danach tatsächliche vorhandene Indexseitenaufnahme rein aufbereiten,
ohne neue unveränderte SQLprofile oder allgemeinen Speicher-/Nettonutzenclaim.

## Primärquellen

- [CREATE INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver17): feste Rowstore-DDL und MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad). Abruf 2026-10-12.
- [sys.dm_exec_requests](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-requests-transact-sql?view=sql-server-ver17): tatsächlicher Request und Countergrenzen. Abruf 2026-10-12.

Diese dokumentierten Funktionen ersetzen keine tatsächliche Scope-/Kostenbeobachtung.
