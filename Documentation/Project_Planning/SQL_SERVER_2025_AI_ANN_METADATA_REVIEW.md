# TSK-006 – einzelne vollständige ANN-Metadatenaufnahme bestanden

Stand: 2026-10-11. METADATA_CAPTURE_PASS, GENERATION_UNKNOWN, NO_SEARCH.
Genau ein Kandidat, ein neuer eigener Container und ein Lifecycle gemäß dem
[ausdrücklich freigegebenen Paket](SQL_SERVER_2025_AI_ANN_METADATA_DECISION.md).
Keine Korrekturwelle; ausgeführte Quellen unverändert.

## Tatsächlicher Befund

Am vollständig gebundenen eigenen Image SQL 17.0.5005.3/EngineEdition 3/Linux
Ubuntu 24.04 bestanden vier CPUs/sechs GiB, eigene Loopbackbindung, CL170/SIMPLE,
256/64-MB-Dateilimits und volle bytegenaue Marker. Genau eine persistente
tokengebundene Baseline erfasste tatsächlich Preview 0 und DB-scoped MAXDOP 0.
Geschlossene Setclients und getrennte neue DB-Clients attestierten Preview 1,
MAXDOP 1. Die eigene Buildsession bestätigte QUOTED_IDENTIFIER 1.

1000 synthetische VECTOR(3)-float32-Rows wurden durch vollständige IDs, numerische
Oraclewerte, Dimension und volle Unicode-Bytes der unterstützten JSON-Darstellung
gebunden. CREATE VECTOR INDEX erstellte genau einen eigenen Index. Die vollständige
sys.vector_indexes-Row wurde als einzelne ungekürzte JSON-Ausgabe mit NULL-Feldern
aufgenommen, vor/nach Capture vollständig bytegenau verglichen.

| Tatsächliches Feld | Erhaltener Wert |
|---|---|
| type / type_desc | 8 / VECTOR |
| vector_index_type | DiskANN |
| distance_metric | COSINE |
| build_parameters | gültiges JSON mit Schlüsseln StartId, L, M, R |
| JSON_VALUE(build_parameters, '$.Version') | NULL; Schlüssel Version fehlt |
| TRY_CONVERT(int, Versiontext) | NULL |

Damit ist der fehlende Versionsschlüssel in dieser konkreten Metadatenaufnahme
belegt. Der frühere zweite Buildkandidat hatte die Metadaten nicht ausgegeben;
dessen exakter Rohwert bleibt historisch unbekannt. Keine numerische Generation
erraten und keine stabile öffentliche Struktur der internen Buildparameter behaupten.
[SRC-097](../Research/SOURCE_REGISTER.md) bezeichnet build_parameters als „Internal usage only“;
das Migrationsbeispiel in SRC-077 ersetzt die fehlende aktuelle Versionsangabe nicht.

Vier volle Snapshots verglichen je 107 Host- und 41 DB-scoped-Konfigurationsrows,
alle Marker/Baselines/Dateimetadaten und die ausgewählten sys.databases-Optionsfelder.
24 Markergegenproben, neun duale Baselinegegenproben und drei vollständige
Quellgegenproben bestanden. Keine Exact-/ANN-/VECTOR_SEARCH-/Recallphase.

## Cleanup und Abnahmegrenzen

Eigener Indexdrop und tatsächliche Vectorindexabwesenheit bestanden. Die volle
1000-Row-Quelle sowie Baseline-, Marker- und Konfigurationsbindungen blieben erhalten.
Beide tatsächlichen Restores 0/0 und ein neuer Attestierungs-/Dropclient vor DB-Abbau
bestanden. Ein separater neuer SQL-Client bestätigte DB-Abwesenheit; vollständig
gebundener Containerabbau und zusätzliche Abwesenheit bestanden. Gemeinsamer
Cleanup **12,439 Sekunden**, keine Cleanupfehler, Prozesscode 0.

Keine Generations-/Such-/Indexnutzungs-/Recallqualifikation, keine empirische
Worker-DOP-/Plan-/Performance- oder vollständige IDX-011-/IDX-012-Abnahme.
Das einzelne Diagnosebudget ist verbraucht. Der neue Benutzerauftrag erteilt auch
weitere notwendige Freigaben dieser Entwicklungswelle; der nächste
[begrenzte Legacy-Signaturversuch](SQL_SERVER_2025_AI_ANN_LEGACY_TRIAL_DECISION.md)
erhält einen eigenen endlichen Scope und erforderlichen Quellenreview.

## Quellen- und Prüfbindung

Fünf betroffene lokale Tests bestanden vor Runtime. Der enge unabhängige tatsächliche
Quellenreview fand keine konkreten P1/P2. Bestehende gültige Baseline-/Restore-/
Helper-/Readinessanalysen wurden wiederverwendet; kein unveränderter Runtime-Retry.
Ein Owner, ein erforderlicher Reviewer; Modell-/Tokenverbrauch unbekannt.

| Private Quelle | SHA-256 |
|---|---|
| qualify_build.py | 7266A7D3E62AF10C815896BBD4F6FCC3E1E6068ACF31B7FF1CB6E369842D4B4B |
| sql_build.py | 36CFC7B1A5B7608FF2B7497C2DEA163CDE6FEFA8B27D5C9D8124E165F78917EC |
| test_build.py | 162A7DF5DCD8D694DD6B8B528708929F276061F4C03A3883B8715004A0375D50 |
| lifecycle01.log | 91B614D18292662F2CC9E413E9ED965280D287F7290AB20C4F6584BA0137DD46 |
