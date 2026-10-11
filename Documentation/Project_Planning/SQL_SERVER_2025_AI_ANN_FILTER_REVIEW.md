# TSK-006 – Filterdiagnose mit sichtbarem Qualitätsverlust

Stand: 2026-10-11. FILTER_DIAGNOSIS_PASS in zwei vollständigen Lifecycles;
enger Filter ROWS_BELOW_K/Recall@5 0, Generation UNKNOWN,
FILTERED_INDEX_USAGE_UNPROVEN. Ein stabiler Kandidat, zwei eigene neue Container
gemäß [vor SQL festgelegtem Ergebnisvertrag](SQL_SERVER_2025_AI_ANN_FILTER_DECISION.md).
Kein Such-/Qualitätsversprechen aus dem technischen Diagnose-PASS.

## Tatsächliche Ergebnisse

Vor Indexbau wurden für dieselbe vollständig gebundene 1000-Row-VECTOR(3)-float32-
Quelle, Queryvektor, cosine/K=5 und Id-Tiebreaker drei Exact-Oracles gesichert.
Nach Build wurde je Fenster genau ein zusätzlicher parameterisierter Legacy-
Suchaufruf mit äußerem WHERE-Prädikat ausgeführt. Die vorab festgelegten breiten
Grenzen waren mindestens vier gültige Rows und vier Exact-Treffer; das disjunkte
enge Fenster erwartete null ANN-Rows bei fünf Exact-Rows. Keine adaptive Schwelle.

| Festes Id-Fenster | Exact-Rows | ANN-Rows, beide Lifecycles | Recall@5 | Einordnung |
|---|---|---|---|---|
| 1–1000 | 5 | 5 | 1 | fünf Treffer am festen Queryvektor/Korpus |
| 1–100 | 5 | 5 | 1 | breite Filterung ohne beobachteten Verlust |
| 501–510 | 5 | 0 | 0 | sichtbarer Postfilterverlust, ROWS_BELOW_K |

Das enge Exact-Oracle lieferte die IDs 505, 503, 509, 504, 510; das ANN-Resultat
war leer. Dies demonstriert für den konkreten Build/Query/Korpus den Unterschied
zwischen gefiltertem Exact-Top-k und nachträglicher Filterung des ungefilterten
ANN-Top-k. SRC-078 beschreibt diesen Legacy-Postfilterpfad; dies bestimmt keine
numerische Generation und unterstellt keine aktuelle Azure-Iterativfilterung.
Kein allgemeines Recallversprechen für andere Daten oder Queryvektoren.

Jede zurückgegebene Row wurde an Quelle/Id-Fenster und VECTOR_DISTANCE mit der
qualifizierten Toleranz 0,0001 gebunden. Vier neue tatsächliche Filtergegenproben
lehnten fehlende Rows, fremde ID 1001, vorhandene aber filterfremde ID 501 und
geänderte Distanz ab. Die Clientauswertung bindet vollständige Fallabdeckung,
eindeutige IDs und tatsächliche Schnittmengen an die erhaltenen Summaries.

## Zustandsbindung, Cleanup und Abnahmegrenzen

Fester SQL-Build 17.0.5005.3/EngineEdition 3/Linux Ubuntu 24.04, gleiche volle Image-ID,
vier CPUs/sechs GiB, eigener Loopbackport, volle CID-/Image-/Ownerbindung, CL170/SIMPLE,
256/64-MB-Dateilimits und bytegenaue Marker. Tatsächliche persistierte Baselines
Preview 0/MAXDOP 0, getrennte Set-/neue Attestclients 1/1, Buildsession QUOTED_IDENTIFIER 1.

Je Lifecycle vier vollständige 107-Host-/41-DB-scoped-Snapshots, 24 Marker-/neun
Baseline-/drei bisherige Ergebnis-/drei Quell-/zehn Textwert- und vier neue Filter-
gegenproben bestanden. Volle 1000-Row-Quellen und Indexmetadaten unverändert;
eigener Indexdrop und tatsächliche Indexabwesenheit bestanden. Beide tatsächlichen
Restores 0/0, neue Attestierung vor DB-Drop und separate SQL-/Containerabwesenheit
bestanden. Cleanup 12,354/12,552 Sekunden, Prozesscodes 0. Ausgeführte Quellen unverändert.

Generation UNKNOWN, tatsächliche Indexnutzung dieser gefilterten Queries UNPROVEN.
Der frühere Actual-Plan gilt nur für seinen ungefilterten Suchaufruf. Keine CPU-/IO-/
Elapsed-, DML-, andere Build-/Azure- oder volle IDX-011-/IDX-012-Abnahme. Ein Kandidat/
zwei Container verbraucht; keine weitere Filterwiederholung erforderlich.

## Quellen- und Prüfbindung

Fünf bestehende Grenztests und sechs neue Filter-/Coverage-/Recall-/Manipulationstests
bestanden vor SQL. Der enge unabhängige Methoden-/Quellenreview fand keine konkreten
P1/P2; gültige unveränderte Analysen wiederverwendet. Ein Owner, ein erforderlicher
Reviewer; Modell-/Tokenverbrauch unbekannt. Rohprozessoutput bleibt privat.

| Private Quelle unter ANN_FILTER_CANDIDATE01 | SHA-256 |
|---|---|
| qualify_build.py | E8D2AC071C98965AB731BC66EEB7046FA95EF5EB8E48B1FC2EA25D5F63A99D69 |
| sql_build.py | 492B72AEEEF4EC455A53ABF749593A7944DC8C203247CCA9CB8B720ECC07DEF4 |
| filter_evidence.py | 5C92F85050640A794B56E478D4FE55327E63CC1CC505BB36D057B8C6F0649A23 |
| test_filter.py | 92FC32EDF6EDDD9A1319543F7CFEF05A6C1D780664EE0A42564298EDEEDAEDA0 |
| lifecycle01.log | 010E25243FBE4F69A890EB729F05D9897BB9A550620258B9B58FC49F690C78A0 |
| lifecycle02.log | FE63F5FFF22DE7511E08FADEF77D846D84B3EBFA159516681DC4EE57C1F1B45A |
