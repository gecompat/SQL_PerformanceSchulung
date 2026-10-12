# TSK-004 – neue begrenzte CL-Istwertqualifikation

Stand: 2026-10-12. Neuer endlicher Folgeschnitt; keine Lockerung öffentlicher
CL170-Demoprofile und keine Wiederholung unveränderter grüner Profile.

## Ausgangsstand und tatsächliche Freigabe

[PR211](https://github.com/gecompat/SQL_PerformanceSchulung/pull/211) vollständig
abgeschlossen: Head 40e81941a3f8afc51a672e592346d9368bcdafac,
main 3675a8c3663155519da548de5560fdecc1dc0d95, neun Head-/sieben Main-Workflows
PASS, Tree 83d15f8f028532a01c2379d74b117b32e4395164 gleich, FF-main sauber,
eigener lokaler/Remote-Branch entfernt. Teaching Paths sind geplante Auswahl,
keine tatsächlich gemessene Teilnehmer-/Generalprobenabnahme; PPTX unverändert.

Der [alte Compatibility-Slice](SQL_SERVER_2025_AI_COMPATIBILITY_REVIEW.md) bleibt
mit seinen drei eigenen geschlossenen Containern, verlorenen frühen Fehlerdetails,
NULL-Oraclefehlern und nicht qualifizierten Skalar-/Low-CL-Chunkmarkern FAIL.
Er wird weder still zurückgesetzt noch nachträglich als PASS ausgegeben.
Der Benutzer hat weitere lokale Entwicklungsfreigaben erteilt und ausdrücklich
mehr als zwei erforderliche Testzyklen verlangt. Dieser neue Scope behebt die
bekannten Result-/Fehleraufbewahrungsprobleme mit neuer begrenzter Quellenwelle.

Ein Implementierungsverantwortlicher und enger unabhängiger Review neuer
Istwert-/NULL-/Chunkfehler-/Marker-/Restore-/Adaptergrenzen. Ein P2 zur tatsächlichen
transitiven Fehlerparserdependency wurde geschlossen: vollständiger Matcher im
ohnehin gehashten privaten Oracle, keine ungebundenen Publicimports. Acht reine
Gegenproben und CLI-help ohne Nativeadmission PASS; Quellenabschluss ohne P1/P2.
Modell-/Tokenverbrauch bleibt unbekannt.

## Vor Admission feste Grenzen

Sechs kohärente neue Ausführungskandidaten, insgesamt höchstens zwölf zusätzliche
eigene serielle Container, zwei stabile vollständige positive Profile. Checkpoint3/
hard6; eigener gemeinsamer Ledger ohne Reset, alle neuen FAILs zählen. Die drei
historischen Container bleiben zusätzlich im alten Nachweis sichtbar. Retry nur
bei geänderten ausführungsrelevanten Quellen oder neuer konkreter Evidenz.

Bereits vorhandenes fixes Image
78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726,
tatsächlich SQL17.0.5005.3/Developer/EngineEdition3, vier CPU/sechs GiB,
eindeutiger Voll-CID/Name/Ownerlabel und dynamischer Loopbackport. Keine Pulls,
Installationen oder Hosteffekte. Nur neue eigene DB SQLPERF_AI_CL_RESULT mit
SIMPLE, 256/64-MB-Dateilimits und vier vollständigen bytegenauen Eigentumsmarkern.
Keine Provider-/Cloud-/Bezahl-API-, Inferenz-, ONNX-, Preview- oder globalen
MAXDOP-Änderungen. Andere Repositories/Instanzen bleiben unverändert.

Alle Normalphasen einschließlich Readiness teilen höchstens300 Sekunden; danach
einmal insgesamt höchstens60 Sekunden für Restore/markergebundenen DBcleanup,
frische read-only DB-Abwesenheit und vollständig gebundenen CID-/Namensabbau.
SQLCMDPASSWORD nur im Environment, kein Passwortargument oder SQLCMDINI.
Bekanntes natives Clientende bleibt Voraussetzung für Inputentfernung/neue SQLclients.
UNKNOWN sperrt SQL, erhält Inputs und wird nicht durch ungebundene Rescue verdeckt.

## Neue Result- und Negativkontrollen

Nach vollständigem Setup wird tatsächliche unabhängige DB-ID gelesen und der
CL170-Baselinezustand aufgenommen. Je CL150/160/170 eigener guarded ALTER und
frische SQLCMD-Verbindung; tatsächlicher CL wird gelesen, nicht bloß als konstant
gedruckter Marker angenommen. Vollständige eigene DB-/Konfigurations-/Datei-/
Markerzustände und fehlende Userobjekte werden vor/nach den read-only Proben gehalten.
Nur der eigene Compatibility Level darf sich gegenüber der Baseline ändern.

Vektorfixture `[3,4,0]`: tatsächliche Dimensions-/BaseType-/Norm-/UnitNorm-/
Euclidean-/Dot-/Cosine-Werte und sämtliche normalisierten Koordinaten werden
als vollständige UTF-16-JSONframes ausgegeben. Explizite native IS-NULL-Gates
und unabhängige reine finite/type/tolerance-Referenzen verhindern P2-NULL-PASS.
Alle acht Felder besitzen je CL eine separate tatsächlich auf NULL gesetzte
Negativkontrolle mit erwarteter nativer51003-Abweisung:24 pro Profil.
Diese Kontrollen qualifizieren den Oracle; sie behaupten keinen Modellfehler.

Chunking führt dieselbe feste ABCDEFGH/FIXED4/Overlap0-Abfrage dynamisch aus.
Bei Erfolg werden beide tatsächlichen Rows vollständig mit Reihenfolge, Offset,
Länge und UTF-16-Textbytes erhalten. Bei Fehler bleiben tatsächliche Number,
Severity, State, Line, Procedure und sämtliche Messagebytes erhalten; kein internes
Fangen mit anschließend verlorener Ursache. CL170 verlangt beide korrekten Rows.

Für niedrige CLs wird keine erfolgreiche Denialoracle vorgetäuscht: tatsächliches
208 mit gebundenem Funktionsnamen wird als beobachtete Unverfügbarkeit erfasst;
andere Fehler ergeben keinen Verfügbarkeitsclaim. Tatsächlicher vollständiger
Erfolg wäre eine sichtbar dokumentierte Abweichung zur Microsoft-Learn-Grenze,
keine stillschweigende generelle Low-CL-Freigabe. Öffentliche Profile bleiben CL170.

Danach tatsächlicher CL170-Restore, vollständige Baselinegleichheit, markergebundener
eigener DBabbau und neue unabhängige Abwesenheit. Kein Runtime-PASS ohne eigenen
vollständigen Cleanup. Rohwerte/Fehler-/SQL-/Metadaten-/CID-/Tokenframes ausschließlich
privat unter Runtime; in Git nur neutralisierte begrenzte Beobachtungen.

## Quellen- und Aussagegrenzen

Quellenreview-SHA256:

- Adapter 4691A7558D99FA622D14C21DED4C1F202B20573EFEAE20F80D7B32E5A3EE959C
- Probe 8717FBA1ECA1CF210FE15BA083127F942E93DF9AD4A705A7AA52B5027EB5E5F9
- Oracle 961FB3E1C8CC2A397733D69471BC1649BFB119A14D471CF9264DC29338E16C9E
- Scalar 782EE05550CF37316019F3C930E5B65CC3074AD4989CFBC66E3D3C21531DA216
- Chunk A64FFE7AED2C5D02C4D7513ED7F3A05AEA56BF27E2EAD0750BDF2607F6E9671A

Bestehende Endstatus-/Containerfloors sind wiederverwendet, neue tatsächliche
ausgeführte Dependencies vollständig gehasht. Acht reine Methoden prüfen NULLs,
Typ-/Bool-/NaN-/Infinity-Aliase, alle Chunkbytes, vollständige Fehlerfelder,
Transportunvollständigkeit, Callerbindung und gemischte/fremde Fehlerframes.
Kein weiterer Review alter Helpers, keine zusätzliche Modell-/Reviewkette.

Erneut gelesene bestehende Primärquellen SRC-074/075/079, Abruf2026-10-12:
[VECTOR_NORM](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-norm-transact-sql?view=sql-server-ver17),
[VECTOR_NORMALIZE](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-normalize-transact-sql?view=sql-server-ver17),
[AI_GENERATE_CHUNKS](https://learn.microsoft.com/en-us/sql/t-sql/functions/ai-generate-chunks-transact-sql?view=sql-server-ver17).
Learn verlangt für AI_GENERATE_CHUNKS CL≥170 und beschreibt unterhalb davon eine
nicht auffindbare Funktion. Dokumentierte Grenze und konkrete gemessene Buildbeobachtung
bleiben getrennt. Weder Geometrie noch Chunking zeigen Sprachsemantik oder Inferenz.

Dieser Schnitt ändert zunächst nur kanonische Nachweisdokumente; tatsächliche
CI-Runtimeauswahl Head/Main muss False bleiben. Nach Native sind aktuelle Quellen-/
Frame-/Result-/Cleanupbindung, Privacy, Head-/Main-Gates, PR, ganzer Tree,
FF-Synchronisierung und eigenes Branchcleanup erforderlich. Volle TSK-004-/
Provider-/Demo-/Curriculum-/Workstreamabnahme bleibt offen. Native zunächst offen.

## Neue Native C1 zweimal bestanden

Beide stabile neue vollständige Profile bestanden auf der fixen eigenen Version.
Je48 protokollierte Nativephasen ohne Readiness-/separate Versionqueries, zusammen96.
Sechs tatsächliche vollständige Skalarrecords, 48 native NULL-Abweisungen, sechs
vollständige Chunk-/Fehlerrecords, 16 Vollstates und zwei vollständige Baseline-
Restores. Beide eigenen DB-/CID-/Namenslifecycles geschlossen, eigene Ownerlabel-
Inventur leer, keine verbleibenden Inputs und kein UNKNOWN.

Alle tatsächlichen Scalar-/State-/Chunk-/NULL-Fehlerframes, unabhängigen Caller-DB-
Frames, aktuelle ausgeführte Quellen, Restores und frische externe Abwesenheit
anschließend rein gebunden. Null zusätzlicher SQLaufruf für diesen Nachweis.

| Tatsächlicher CL | Dimensions / BaseType | Norm / UnitNorm | Euclidean / Dot / Cosine | Native Chunkresultat beider Profile |
|---|---|---|---|---|
| 150 | 3 / float32 | 5 / 1.000000023841858 | 0 / -25 / 0 | Error102, Severity15, State38, Line3, ProcedureNULL; vollständige Messagebytes erhalten |
| 160 | 3 / float32 | 5 / 1.000000023841858 | 0 / -25 / 0 | Error102, Severity15, State38, Line3, ProcedureNULL; vollständige Messagebytes erhalten |
| 170 | 3 / float32 | 5 / 1.000000023841858 | 0 / -25 / 0 | Beide Rows1/1/4/ABCD und2/5/4/EFGH mit vollständigen UTF-16-Bytes |

Normalisierte Koordinaten je tatsächlichem Skalarrecord:
`[6.0000002e-001,8.0000001e-001,0.0000000e+000]`. Die float32-Rundung bleibt
erhalten; UnitNorm ist innerhalb der vorab fixierten1e-5-Toleranz, nicht bitgenau1.
Alle acht NULL-Felder wurden jeCL tatsächlich separat abgewiesen.

Der feste benannte FIXED-Aufruf scheitert unter CL150/160 tatsächlich mit
„Incorrect syntax near '='.“; er liefert weder das vormals vorausgesetzte208 noch
korrekte Chunkrows. Dies erklärt den früheren Denialoracle-FAIL. Die neue
Klassifikation lautet OBSERVED_OTHER_ERROR_NO_AVAILABILITY_CLAIM. Sie behauptet
keine allgemeine Funktionsverfügbarkeit oder deren generelle Abwesenheit unter
Low-CL; der dokumentierte CL≥170-Vertrag und die öffentlichen CL170-Demos bleiben
unverändert. Beide Profile liefern unter CL170 die vollständige positive Fixture.

Ein neuer Ausführungskandidat/zwei zusätzliche eigene Container verbraucht, alte
drei Container/FAILs bleiben erhalten. Begrenzte Skalar-Istwerte-/Oracle-/Chunk-
Fehler-/CL-Restore-/Cleanupqualifikation PASS; keine allgemeine Low-CL-, Provider-,
Demo-, Teaching-Path- oder Workstreamabnahme. Aktuelle Head-/Main-/PR-/Tree-/FF-/
Ownbranchgates folgen; danach nächste unabhängige offene Qualifikationsfrage.
