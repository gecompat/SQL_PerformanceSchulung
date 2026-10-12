# RES-008 – private Quellen-, Dimensions- und Storagevorbereitung

Stand: 2026-10-12. TSK-010/CUR-019, Basis
`84aef7016cc86194281805adc29ae9bc15fcec2f`, Branch
`codex/sql2025-ai-res008-preparation`. RES-008 bleibt PROPOSED.
Der Nachweis umfasst weder ein öffentlich ausführbares Demopaket noch eine
Performance-, TP-PERF- oder vollständige TSK-010-Abnahme.

## Ausgeführter Umfang und tatsächliche Ergebnisse

Drei neue eigene serielle Podmancontainer verwendeten das bereits vorhandene,
fest gebundene Image
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726`.
Jeder meldete exakt SQL Server 17.0.5005.3. Grenzen: vier CPU, sechs GiB,
eigener zufälliger Loopbackport, 300 Sekunden Gesamtbudget einschließlich
Readiness und eine separate gemeinsame 60-Sekunden-Cleanupdeadline ohne Reset.
Native ODBC-SQLCMD.EXE erhielt Secrets ausschließlich über Umgebung; private
Eingaben, vollständige Quellenhashes und Rohdiagnosen bleiben ignoriert.

Eine eigene Datenbank mit CL 170, SIMPLE und 256/64-MB-Dateilimits enthielt
vier Tabellen mit je 100 synthetischen Rows und eindeutigen IDs 1–100.
Die VECTOR-Dimensionen waren 32, 384, 768 und 1536. Die vollständige Fixture
lautete je Row `[Id,1,0,...,0]`; alle Komponenten, Typen, Keys und Anzahl wurden
tatsächlich geprüft. Zero-Padding erhält diese feste Geometrie und belegt
keine reale Modellkompression oder semantische Suchqualität.

Der stabile zweite Kandidat bestand zwei vollständige Lifecycles auf zwei
frischen Containern. Je Lifecycle wurden nach erstem Setup, zweitem Setup und
Wiederherstellung jeweils alle 400 Vektortexte mit vollständiger Länge und
SHA-256 erfasst. Alle Quellenaufnahmen und DB-Konfigurationen waren gleich,
auch über beide Wiederholungen. `sys.columns` belegte jede tatsächliche
Dimension, `vector_base_type=0` und NOT NULL. Vier tatsächliche Cosine-TOP1-
Kontrollen je Aufnahme lieferten Id 1 mit Distanz 0.

Die folgenden Zahlen sind die jeweils erste vollständige Punktaufnahme aus
`sys.dm_db_partition_stats` des Clustered-PK-Index und `DATALENGTH(V)`.
Sie sind Tabellenwerte für dieses kleine Profil, keine isolierten Index- oder
RAMkosten und keine Größenprognose. Spätere Aufnahmen wurden ebenfalls erfasst;
gleiche Seitenzahlen nach neuer Tabellenerzeugung waren kein künstliches Gate.

| Lauf | Dimension | Rows | Bytes je VECTOR | data pages | used pages | reserved pages |
|---|---|---|---|---|---|---|
| 1 | 32 | 100 | 136 | 2 | 4 | 9 |
| 1 | 384 | 100 | 1544 | 20 | 22 | 25 |
| 1 | 768 | 100 | 3080 | 50 | 52 | 57 |
| 1 | 1536 | 100 | 6152 | 100 | 102 | 105 |
| 2 | 32 | 100 | 136 | 2 | 4 | 9 |
| 2 | 384 | 100 | 1544 | 20 | 22 | 25 |
| 2 | 768 | 100 | 3080 | 50 | 52 | 57 |
| 2 | 1536 | 100 | 6152 | 100 | 102 | 105 |

Je Lifecycle wurde unter vollständigem Eigentumsguard tatsächlich Id 100 aus
der eigenen 32-dimensionalen Tabelle gelöscht. Die anschließende Quellenprüfung
musste exakt den nativen Fehler 51003/FAIL_RESULT_CONTRACT liefern; beliebige
andere Fehler waren unzulässig. Ein weiterer Setup stellte die vollständigen
400 Quellen und alle positiven Kontrollen wieder her. Datenbank-MAXDOP und
PREVIEW_FEATURES blieben tatsächlich 0; allein feste Suchstatements verwendeten
OPTION(MAXDOP 1). Keine Preview-, Host-, Provider-, Cloud- oder ONNX-Änderung.

## Kandidaten, Review und Cleanup

Die menschlich erweiterte Entwicklungswelle erlaubt sechs kohärente Kandidaten
und in diesem Vorschnitt höchstens zwölf serielle eigene Container. C1 bleibt
FAIL: nach positivem Setup verweigerte SQL mit Msg 8124 die Komponentenprüfung,
weil ein Aggregat innere JSON-Felder mit einer äußeren Rowreferenz mischte.
Kein Quellen-, Storage- oder Such-PASS wird für C1 behauptet.
C2 ersetzte ausschließlich vier identische Prüfstellen durch getrennte
Elementanzahl und korrelierte Komponentenprüfung einschließlich NULL-, Typ-
und Keygrenzen. Alle übrigen Ausführungsquellen blieben gleich. Beide grünen
Pflichtwiederholungen sind abgeschlossen; kein weiterer unveränderter Lauf.

Ein Implementierungsverantwortlicher und ein enger unabhängiger Quellenreview
prüften das konkrete neue Oracle-/Eigentums-/Cleanup-Risiko. Das C2-Delta wurde
vor Admission unabhängig geschlossen, keine offenen P1/P2. Der Reviewer führte
keine Runtime aus und attestierte keine Performance- oder Demoabnahme.
Alle elf Ausführungsabhängigkeiten sind bytegenau im privaten Ledger gebunden;
C1- und C2-Quellen wurden vor Promotion separat eingefroren. Vorhandene
Endstatusguards wurden nach tatsächlicher Quellenprüfung wiederverwendet.

Vier vollständige bytegenaue Eigentumsmarker und der vollständige DB-Kontext
schützten Setup, Gegenprobe und Cleanup. Parameter wurden vor begrenzten Casts
geprüft. Alle drei Läufe belegten natives Clientende, tatsächlichen SQL-Cleanup,
neue unabhängige DB-Abwesenheit sowie Entfernung und erneute Abwesenheit der
vollständigen eigenen Container-ID und des Namens. Cleanup dauerte C1
12,6449 Sekunden, C2 Lauf 1 12,6741 und Lauf 2 13,3017 Sekunden, jeweils unter
derselben 60-Sekunden-Grenze. Keine fremde Ressource oder anderes Repository
wurde verändert. Modell-/Tokenverbrauch bleibt unbekannt; keine Inferenz.

Die öffentlichen Änderungen sind ausschließlich dieser begrenzte Nachweis und
seine kanonischen Verweise. Registryidentität, Demoentwurf, neun implementierte
lokale KI-Demos und der geplante Katalog mit 32 Demos/372 Runs bleiben erhalten.
Aktuelle Head-/Main-Gates, PR-Merge, vollständige Treeübernahme, Synchronisierung
und eigener Branchcleanup müssen vor Schnittabschluss tatsächlich folgen.

## Fachquellen und verbleibende Abnahme

Microsoft dokumentiert float32 als Standard mit vier Bytes je Komponente und
höchstens 1998 Dimensionen. Diese Komponentenbytes sind vom hier tatsächlich
beobachteten DATALENGTH des ganzen VECTOR-Werts zu unterscheiden.
[Microsoft Learn: VECTOR-Datentyp](https://learn.microsoft.com/en-us/sql/t-sql/data-types/vector-data-type?view=sql-server-ver17),
abgerufen 2026-10-12. Die Zuordnung `vector_base_type=0` zu float32 und
`vector_dimensions` folgt
[Microsoft Learn: sys.columns](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-columns-transact-sql?view=sql-server-ver17),
abgerufen 2026-10-12. Float16 und seine Previewanforderung sind kein Teil dieses
Vorschnitts.

CPU, Elapsed, Memory, Pläne, Query-Reads, AB-/BA-/AA-Messung, Effektseparation,
größere Datenprofile, Loader-/Modelspacevertrag und reale semantische Qualität
bleiben offen. Ältere Engines, öffentliche Result-/Markergegenproben und
vollständige Runtime-/Negativ-/Cleanupqualifikation wurden für RES-008 noch
nicht ausgeführt. TSK-010 und die Gesamtwelle bleiben offen. Der nächste
zulässige lokale Schnitt nach vollständiger Integration erweitert die
RES-008-Messmethode unter denselben Datenschutz- und Autoritätsgrenzen.
