# TSK-006 – begrenzter ANN-Build-/Suchentscheid mit DB-scoped-MAXDOP

Stand: 2026-10-11. PENDING_USER_DECISION. Die
[bestandene Parserdiagnose](SQL_SERVER_2025_AI_ANN_PARSER_PASS_REVIEW.md) autorisiert
keinen Indexbuild/Search. Die historischen Korrekturbudgets bleiben verbraucht;
keine neue ausführbare Quelle oder SQL-/Containerruntime durch diesen Entwurf.

Der enge unabhängige Befund-/Effekt-/Budgetreview fand keine konkreten P1/P2.
Dies schließt allein das Entwurfsgate; der tatsächliche neue Baseline-/Restore-/
Clientquellenreview bleibt nach ausdrücklicher Benutzerfreigabe vor SQL erforderlich.

## Konkrete Empfehlung und Budget

Empfohlen wird ein neu begrenzter privater IDX-011-Build-/Ergebnisumfang mit
höchstens zwei kohärenten Kandidaten und vier neuen eigenen Containern seriell,
je höchstens zwei vollständige Lifecycles eines stabilen Kandidaten. Ein Retry
benötigt geänderte Eingaben oder neue konkrete Evidenz. Nach zwei ungelösten
Kandidaten anhalten; kein zusätzlicher Kandidat durch ungenutzte Containerplätze.
Ein Owner, erforderlicher enger unabhängiger Quellenreview der neuen Baseline-/
Restore-/Clientphasen vor SQL. Unveränderte gültige Helperanalysen wiederverwenden,
keine Reviewkette. Modell-/Tokenverbrauch bleibt unbekannt.

Gleiche vollständige lokale Image-ID
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726`, SQL
17.0.5005.3/EngineEdition 3/Linux Ubuntu 24.04, vier CPUs/sechs GiB, eigene
Loopbackbindung, volle CID-/Image-/Ownerprüfung, CL170/SIMPLE, 256/64-MB-Dateilimits.
Nur neue eigene SQLPERF_LAB_IDX011_<RunToken> mit vier vollständigen bytegenauen
Markern. Höchstens 1000 synthetische VECTOR(3)-Rows mit float32, cosine, K=5;
höchstens eine gleichzeitig aktive SQL-Session. Kein Modell-/Providercall.

## Ein zusätzlicher ausdrücklich freizugebender DB-Effekt

Neben dem bisherigen eigenen PREVIEW_FEATURES=ON wird ausschließlich
`ALTER DATABASE SCOPED CONFIGURATION SET MAXDOP=1` in der eigenen Testdatenbank
beantragt. Kein Server-/Host-MAXDOP, Resource-Governor-, Thread-/TLS-/Cloud-/ONNX-
oder ALLOW_STALE_VECTOR_INDEX-Effekt. Andere Repositories bleiben unverändert.

[SRC-106](https://learn.microsoft.com/en-us/sql/sql-server/sql-server-2025-known-issues?view=sql-server-ver17#vector-index)
dokumentiert den ignorierten Vector-MAXDOP-Parameter und nennt DB-Konfiguration
als Alternative. [SRC-108](https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-database-scoped-configuration-transact-sql?view=sql-server-ver17)
dokumentiert den DB-scoped-Pfad und seine Priorität. Beide Quellen begründen den
Konfigurationspfad; sie sind kein empirischer Worker-/DOP-Befund am eigenen Indexbuild.
Diese Grenze bleibt ausdrücklich sichtbar, keine tatsächliche DOP-Messung behaupten.

Vor jedem Set zwei vollständige persistente Ausgangswerte sichern: Preview genau
0/1 und MAXDOP genau der tatsächlich erfasste 0. Genau eine eigene tokengebundene
Baseline-Row, keine Defaults bei fehlenden/NULL-/doppelten/ungültigen Werten.
Ein anderer MAXDOP-Ausgangswert stoppt diesen festen Profilumfang vor Effekten.
Beide Setclients müssen schließen; neue eigene DB-Clients attestieren Preview 1
und MAXDOP 1 vor tatsächlichem Build/Search. Kein höherer Query-/Indexhint.

Nach Erfolg oder Fehler beide tatsächlichen Ausgangswerte wiederherstellen und
in einem neuen Client attestieren, bevor die eigene DB abgebaut wird. Der bisherige
Preview-only-Recoverytext genügt nicht für diesen neuen Effekt. Fehlender tatsächlicher
MAXDOP-Restore bleibt FAIL, auch wenn Previewrestore oder Containerabbau bestanden.
Alle übrigen Host-/DB-scoped-/Datei-/Quellbindungen unverändert kontrollieren.

## Feste Ausführungsfolge und Ergebnisgrenzen

1. Einen separaten neuen privaten Kandidaten vorbereiten; lokale Gegenfixtures für
   beide Baselines, zusätzliche Restorefehler und vollständige Bindungen. Nur
   betroffene Tests/Reviewdeltas; keine historische Probe ändern oder erneut ausführen.
2. Eigene neue Instanz binden; Build/Edition/OS prüfen. Eigene DB/Baseline anlegen,
   Marker vollständig prüfen, beide Konfigurationseffekte wie oben setzen/attestieren.
3. Höchstens 1000 feste nicht-NULL-Vektoren mit clustered int PK laden. Tatsächliche
   Spaltenmetadaten, Dimension/float32, numerische Oraclewerte und vollständige
   Unicode-Bytes der unterstützten JSON-Darstellung binden; keine internen VECTOR-
   Speicherbytes behaupten. Exakte fünf Treffer mit Distanz und deterministischem
   Tiebreaker vor Indexbuild als Oracle sichern.
4. CREATE VECTOR INDEX in einem frischen Client nach geschlossenem Enable und
   separat belegtem Preview-/MAXDOPwert ausführen. Tatsächliche eigene Indexidentität,
   Typ, Metric und Generation erfassen. Unbekannte/fehlende/unqualifizierte Generation
   stoppt vor Search; kein automatisches Versionsraten. Frisch dokumentierte und am
   tatsächlichen Build belegte Generationssyntax verwenden. Aktuelle Azure-Formate
   nicht pauschal auf SQL Server übertragen; Quellenkonflikte sichtbar erhalten.
5. Tatsächliche fünf ANN-Rows, gültige eindeutige Quell-IDs und exakte Distanzkontrolle
   erfassen; tatsächliche Schnittmenge mit dem Exactoracle als Recalltreffer berichten.
   Fehlende/fremde/geänderte Resultate als isolierte Gegenfixtures ablehnen. Kein
   garantierter Recall oder behauptete Indexnutzung aus bloß erfolgreichem Search.
6. Vollständige Quell-/Baseline-/Marker-/Index-/Konfigurationsbindungen vor/nach
   Search vergleichen, eigenen Index entfernen und Abwesenheit prüfen. Keine DML-
   oder Aktualitätsprobe nach Build; IDX-012 folgt erst in einem eigenen späteren
   Umfang. Kein Plan-/Performance-, TP-PERF- oder vollständiger Demopaket-PASS.
7. Beide tatsächlichen Konfigurationsrestores, markergebundener eigener DB-Abbau,
   unabhängiger neuer SQL-Abwesenheitsclient und gebundener Containerabbau mit
   separater Abwesenheit. FAIL/WARN/SKIP/fehlende Messungen getrennt erhalten.

Je Lifecycle gilt die bisherige gemeinsame normale 300-Sekunden-Deadline und
separater gemeinsamer Cleanup höchstens 60 Sekunden, Prozessbudgets insgesamt
50 Sekunden plus zehn Sekunden Reserve. Start-/Timeout-/SQL-/Restorefehler erreichen
weiterhin den finally-Pfad; kein unbeschränktes Warten. Secrets nur in der Umgebung.
Das neue separate Attestierungs-/Dropclientbudget wird nicht zusätzlich auf den
alten 50-Sekunden-Block aufgeschlagen: Restore 6, neuer Attestierungs-/Dropclient 6,
SQL-Abwesenheit 4, Ownerlookup 4, vollständiger Containerinspect 6, Remove 16,
Containerabwesenheit 8 Sekunden ergeben zusammen genau 50. Jeder Aufruf bleibt
zusätzlich an die gemeinsame monotone 60-Sekunden-Deadline gebunden.
Aktuelle Head-/Main-Gates, PR, Integration, Synchronisierung und eigener Branchcleanup
schließen den begrenzten tatsächlichen Befund ab. Der Heartbeat setzt das Budget
nicht zurück. Eine positive Vorbereitung ist weiterhin keine IDX-011-/IDX-012-
Gesamtabnahme oder allgemeine DOP-/Recall-/Performancegarantie.
