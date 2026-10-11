# TSK-006 – begrenzter privater ANN-Build-/Suchbefund

Stand: 2026-10-11. FAIL nach beiden Kandidaten innerhalb des ausdrücklich genehmigten
[Build-/Suchpakets](SQL_SERVER_2025_AI_ANN_BUILD_DECISION.md).
IDX-011/IDX-012 bleiben PROPOSED; keine vollständige Demo-/Performanceabnahme.

## Erster Kandidat: tatsächlicher FAIL

Ein neuer eigener Container am fest gebundenen SQL-17.0.5005.3-Image,
EngineEdition 3/Linux Ubuntu 24.04, vier CPUs/sechs GiB, eigene Loopbackbindung,
CL170/SIMPLE und 256/64-MB-Dateilimits. Die zwei tatsächlichen Ausgangswerte
Preview 0 und DB-scoped MAXDOP 0 wurden in genau einer voll tokengebundenen Row
gesichert. Vier vollständige bytegenaue Eigentumsmarker wurden geprüft.
Geschlossene eigene Setclients und neue getrennte DB-Clients attestierten
zuerst Preview 1/MAXDOP 0, anschließend Preview 1/MAXDOP 1.

Der tatsächliche Indexbuild scheiterte mit Msg 1934/Level 16:
`QUOTED_IDENTIFIER` war für CREATE VECTOR INDEX nicht korrekt gesetzt.
Keine Indexgeneration oder VECTOR_SEARCH-/Recallevidenz; kein abgeschlossener
Build-/Such-PASS. Drei volle Zustandsaufnahmen mit je 107 Host- und 41
DB-scoped-Konfigurationsrows bleiben privat erhalten.

Tatsächlicher Restore beider Werte 0/0 im eigenen Recoveryclient, erneute
Attestierung 0/0 in einem neuen Client vor DROP, separater SQL-DB-Abwesenheitsclient,
gebundener eigener Containerabbau und separate Abwesenheit bestanden.
Gemeinsamer Cleanup **12,444 Sekunden**, Prozesscode 1 bleibt FAIL.
Der erste Kandidat ist verbraucht; seine Quellen und Befunde bleiben unverändert.

## Zweiter Kandidat: Build erreicht, Generationsgate FAIL

Die konkrete neue Evidenz 1934 begründet ausschließlich `SET QUOTED_IDENTIFIER ON`
in der eigenen Buildsession und eine tatsächliche SESSIONPROPERTY-Kontrolle vor
CREATE VECTOR INDEX. [SRC-109](../Research/SOURCE_REGISTER.md) beschreibt den
Parse-time-Sessionzustand und seine Vererbung an EXEC; kein weiterer DB-/Hosteffekt.
Der enge unabhängige Delta-Quellenreview fand keine P1/P2. Im zweiten neuen eigenen
Container bestanden Baseline 0/0, geschlossene Setclients und frische Attestierungen
Preview 1/MAXDOP 1. SESSIONPROPERTY bestätigte QUOTED_IDENTIFIER 1.
CREATE VECTOR INDEX lief durch; die nachfolgende Abfrage fand genau einen eigenen
Index. Der nächste Guard meldete 51003 „Unknown generation before Search“.

Das beweist ausschließlich, dass der gefilterte TRY_CONVERT-Ausdruck keinen
zugelassenen Generationswert 1/2 lieferte. Der Guard stand vor der Ausgabe der
vollen Indexmetadaten. Konkreter Generationswert, Rohtext von build_parameters und
die tatsächlichen Typ-/Metricwerte bleiben deshalb **UNKNOWN**. Weder Generation 3
noch NULL, ein bestimmter Metadatenfehler oder eine Suchsyntaxursache sind bewiesen.
Keine VECTOR_SEARCH-Ausführung oder Recall-/Ergebnis-/Indexnutzungsevidenz.
Der reguläre eigene Indexdrop wurde nicht erreicht; die eigene DB wurde danach
gebunden entfernt, ihre separate SQL-Abwesenheit bestätigt.

Beide tatsächlichen Restores 0/0, neuer Attestierungs-/Dropclient und separate
SQL-DB-/Containerabwesenheit bestanden, gemeinsamer Cleanup **12,397 Sekunden**.
Prozesscode 1 bleibt FAIL. Auch der zweite Kandidat und seine Quellen bleiben
unverändert; kein unveränderter Retry.

**Zwei Kandidaten, zwei eigene Container verbraucht.** Zwei ungenutzte Containerplätze
erlauben keinen dritten Kandidaten. Die harte Abbruchgrenze des freigegebenen Pakets
ist erreicht. Die [begrenzte Metadatendiagnose](SQL_SERVER_2025_AI_ANN_METADATA_DECISION.md)
bleibt ein neuer Budgetentscheid; keine weitere ANN-Runtime dadurch autorisiert.

## Lokale Prüfungen und Quellenbindung

Fünf betroffene lokale Tests prüfen beide Baselines, vollständige erfasste
Konfigurationsbindung, tatsächliche duale Restore-/Attestierungsnachweise und
Start-/Timeout-/fehlende-MAXDOP-Fehler im Cleanup. Alle bestanden vor Runtime.
Ein anfänglich 17 Zeichen langer rein synthetischer Testtoken wurde vor Runtime
auf 16 korrigiert; der lokale Fixture-FAIL bleibt getrennt vom Runtimebudget.
Der unabhängige erste tatsächliche Quellenreview fand keine konkreten P1/P2;
unveränderte geprüfte Helper-/Readiness-/Marker-/Snapshotanalysen wurden wiederverwendet.

| Private Quelle des ersten Kandidaten | SHA-256 |
|---|---|
| qualify_build.py | AF1C211065B9EBC2A272E06295E0F87D9C0561166D66A0F40C41C072980A0020 |
| sql_build.py | 12FF562D3AE55DCE05A92B72887B5546D5C56FEE766E7CB3CC342883288C4901 |
| test_build.py | 40E57C60CB738A086AFE830585B4A0C509429209CC6B8BFBB0909EB7743B8E22 |
| lifecycle01.log | A9AC3DDEEE18833F42472C54C1CEC36335CE8FF4E0761682A7963D2BC4B09F34 |

| Private Quelle des zweiten Kandidaten | SHA-256 |
|---|---|
| qualify_build.py | F19533B721697EE68C4D3AF4891455130C860B15A24219E2AD506EE0B6470EA0 |
| sql_build.py | 590F2C94FA16A5C92141F426CAA2BBAAF0010C0CE32AACFBB8902C756DB6A909 |
| test_build.py | 40E57C60CB738A086AFE830585B4A0C509429209CC6B8BFBB0909EB7743B8E22 |
| lifecycle01.log | F90DD41E7A706781F0759819BCE279A978913AF9F50900FA1F6C3448E343A6D0 |

Ein Owner und erforderlicher enger Reviewer, Modell-/Tokenverbrauch unbekannt.
Konfigurationswerte sind keine empirische Worker-/DOP-Messung. Keine behauptete
Indexnutzung aus erfolgreichem Search; kein garantierter Recall, keine Plan-/TP-PERF-
oder allgemeine Versions-/Demoabnahme. Historische FAILs und Budgets bleiben erhalten.
