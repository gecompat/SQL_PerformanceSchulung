# TSK-006 – einzelne ANN-Metadatendiagnose nach Generationsstopp

Stand: 2026-10-11. PENDING_USER_DECISION. Keine neue ausführbare Quelle oder
SQL-/Containerruntime durch dieses Paket. Der
[Build-/Suchumfang](SQL_SERVER_2025_AI_ANN_BUILD_DECISION.md) hält ausdrücklich
nach zwei ungelösten Kandidaten an; beide sind verbraucht. Der
[FAIL-Checkpoint](SQL_SERVER_2025_AI_ANN_BUILD_REVIEW.md) belegt einen eigenen
Index, aber keinen ausgegebenen Rohwert für Generation/Typ/Metric.

Der enge unabhängige Befund-/Budget-/Effektreview fand keine konkreten P1/P2.
Dies schließt das Entwurfsgate; das spätere tatsächliche Delta-Quellengate bleibt
vor einer ausdrücklich freigegebenen SQL-Ausführung erforderlich.

## Empfehlung und endliches Zusatzbudget

Empfohlen wird genau ein neuer separater privater Kandidat und ein neuer eigener
Container mit **Metadatenaufnahme nach einem Indexbuild, ohne VECTOR_SEARCH**.
Keine Korrekturwelle, kein weiterer Probeaufruf bei Fehler. Nach einem Lifecycle
anhalten und Befund integrieren; ein erfolgreicher Metadatenbefund autorisiert
keinen nachfolgenden Such-/IDX-012-Lauf. Kein Rücksetzen historischer Budgets.
Ein Owner, enger unabhängiger Review des tatsächlichen Metadaten-/Clientdeltas
vor SQL; unveränderte gültige Baseline-/Restore-/Helperanalysen wiederverwenden.
Modell-/Tokenverbrauch unbekannt.

## Unveränderte lokale Effekte

Dieselbe volle Image-ID
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726`, SQL
17.0.5005.3/EngineEdition 3/Linux Ubuntu 24.04, vier CPUs/sechs GiB und eigene
Loopbackbindung; volle CID-/Image-/Ownerprüfung. Neue eigene
SQLPERF_LAB_IDX011_<RunToken>, CL170/SIMPLE, 256/64-MB-Dateilimits, vier volle
bytegenaue Marker, höchstens 1000 synthetische VECTOR(3)-float32-Rows/cosine.
Genau eine gleichzeitig aktive SQL-Session. Kein Provider-/Modellaufruf.

Vor beiden Sets eine tatsächlich erfasste persistente Baseline-Row: Preview 0/1,
MAXDOP genau 0 und voller eigener Token; fehlend/NULL/doppelt/ungültig stoppt.
Nur eigene DB-scoped PREVIEW_FEATURES=ON und MAXDOP=1. Geschlossene Setclients,
neue getrennte DB-Clients attestieren beide Werte vor Build. Nur die eigene
Buildsession setzt/prüft QUOTED_IDENTIFIER ON. Kein Host-MAXDOP, Resource Governor,
Cloud, TLS, ONNX, ALLOW_STALE_VECTOR_INDEX oder anderer DB-Effekt.

## Feste neue Metadatenaufnahme und Abnahmegrenze

1. Bestehenden Build-/Spalten-/Quell-/Marker-/Baseline-/Konfigurationsguard
   unverändert anwenden, 1000 feste Rows und unterstützte volle Unicode-Bytes
   ihrer JSON-Darstellung binden. Kein interner VECTOR-Speicherbyte-Claim.
2. Nach CREATE VECTOR INDEX zuerst genau einen eigenen Index auf dem tatsächlich
   gebundenen eigenen Objekt feststellen. **Vor jeder Generationsklassifikation**
   vollständige sys.vector_indexes-Row einschließlich unbearbeitetem build_parameters,
   vector_index_type und distance_metric privat aufnehmen. Vollständige skalare
   JSON-Ausgabe mit NULL-Feldern, kein direkt aufgeteiltes FOR-JSON-Resultset;
   fehlende/zu große Ausgabe bleibt FAIL, keine stillen Defaults/Abschneidungen.
3. Zusätzlich unverändert erfasste Rohmetadaten und deklarierte Ableitungen
   trennen: JSON-Gültigkeit, JSON_VALUE('$.Version') als Rohtext und TRY_CONVERT
   als Integer. Ungültiges JSON oder fehlender Generationswert bleibt ausdrücklich
   UNKNOWN. Das erfolgreiche Aufnehmen solcher NULL-/unqualifizierten Werte kann
   METADATA_CAPTURE_PASS sein, aber niemals GENERATION_QUALIFIED oder SEARCH_PASS.
   Keine andere JSON-Schreibweise, Generation oder Suchsyntax automatisch erraten.
4. Vollständige Source-/Baseline-/Marker-/Konfigurationsbindung vor/nach der
   SELECT-Aufnahme vergleichen, eigenen Index entfernen und Abwesenheit prüfen.
   Kein VECTOR_SEARCH, kein DML nach Build, keine Recall-/Plan-/DOP-/Performanceprobe.
5. Beide tatsächlichen Originalwerte wiederherstellen; beide Recoveryclients
   vor Restore/Drop an den tatsächlichen ursprünglichen Previewwert und MAXDOP 0
   binden. Neuer Client attestiert beide Restores vor eigener DB-Entfernung;
   separater SQL-Abwesenheitsclient sowie voll gebundener Containerabbau mit
   zusätzlicher Abwesenheit. Fehlender tatsächlicher MAXDOP-Restore bleibt FAIL.

Gemeinsame normale 300-Sekunden-Deadline; getrennt gemeinsamer Cleanup höchstens
60 Sekunden. Feste Prozesscaps Restore 6, neuer Attest/Drop 6, SQL-Abwesenheit 4,
Ownerlookup 4, vollständiger Inspect 6, Remove 16, Containerabwesenheit 8 ergeben
50 Sekunden plus zehn Reserve, jeder Aufruf zusätzlich an monotone Deadline
gebunden. finally auch nach OSError/Timeout/SQL-/Restorefehler, Secrets nur Umgebung.

Aktuelle Head-/Main-Gates, PR, Integration, Synchronisierung und eigener Branchcleanup
schließen diesen Einzelbefund ab. Ein unbekannter Generationswert bleibt sichtbar;
kein Versionsraten und kein weiterer Lauf ohne neuen erforderlichen Entscheid.
Andere Repositories und pausierte Workstreams bleiben unverändert.
