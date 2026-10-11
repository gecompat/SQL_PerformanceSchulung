# TSK-006 – tatsächliche eigene ANN-Indexnutzung beobachtet

Stand: 2026-10-11. ACTUAL_PLAN_CAPTURE_PASS und OWN_INDEX_RUNTIME_OBSERVED
für genau einen festen Suchaufruf; GENERATION_UNKNOWN. Genau ein eigener neuer
Kandidat/Container/Lifecycle gemäß [begrenztem Planentscheid](SQL_SERVER_2025_AI_ANN_PLAN_DECISION.md).
Kein zweiter Lauf erforderlich; keine unveränderte Wiederholung.

## Tatsächliche Beobachtung

Am voll gebundenen Image SQL 17.0.5005.3/EngineEdition 3/Linux Ubuntu 24.04 mit
vier CPUs/sechs GiB, eigenem Loopbackport, CL170/SIMPLE und 256/64-MB-Dateilimits
wurden Preview 0/MAXDOP 0 tatsächlich persistiert, anschließend in neuen Clients
1/1 attestiert. QUOTED_IDENTIFIER 1 in der eigenen Buildsession. Volle Marker,
1000 VECTOR(3)-float32-Rows und Indexmetadaten wurden gebunden.

Genau ein fester Legacy-Suchaufruf unter SET STATISTICS XML ON/OFF lieferte
vollständiges begrenztes XML, Build 17.0.5005.3, das exakt gebundene synthetische
Suchstatement und tatsächliche RunTimeCountersPerThread. Der unabhängige private
Parser bindet Objektattribute jeweils an den unmittelbar zugehörigen RelOp;
Laufzeitrows eines Elternoperators ersetzen keine Laufzeitinformation des Kindes.

| Beobachteter PhysicalOp | Tatsächliche Rows | Objektbindung |
|---|---|---|
| Clustered Index Insert | 5 | eigene temporäre Ergebnistabelle |
| Nested Loops | 5 | Inner Join |
| Vector Index Seek | 5 | volle eigene DB-/lab-/VectorFixture-/IDX011_OwnVector-Bindung, IndexKind DiskANN |
| Clustered Index Seek | 5 | dieselbe eigene Quelltable, clustered Primary Key |

Damit ist die tatsächliche Nutzung des eigenen DiskANN-Indexes für diesen einen
festen Suchaufruf belegt. Keine pauschale Nutzung bei anderen Queries/Filtern,
keine numerische Generation aus Operatornamen ableiten. Version-Feld fehlt
weiterhin; Generation UNKNOWN. Fünf distanzgeprüfte Ergebnisrows und 5/5
Schnittmenge mit Exact-Oracle bestanden; keine allgemeine Recallgarantie.

## Zustandsbindung, Cleanup und Grenzen

Vier vollständige Snapshots mit je 107 Host-/41 DB-scoped-Konfigurationsrows,
24 Marker-/neun Baseline-/drei Ergebnis-/drei Quell-/zehn Textwertgegenproben
bestanden. Vollständige Quell- und Indexmetadaten vor/nach Search unverändert.
Eigener Indexdrop und tatsächliche Indexabwesenheit bestanden. Beide tatsächlichen
Restores 0/0, neue Attestierung vor DB-Drop und separate SQL-DB-/Containerabwesenheit
bestanden. Cleanup 12,583 Sekunden, Prozesscode 0. Ausgeführte Quellen unverändert.

Kein CPU-/IO-/Elapsedvergleich, kein empirischer Worker-DOP, keine gefilterte
Query-, DML-, andere Build-/Azure- oder volle IDX-011-/IDX-012-Abnahme. Rohplan
und Prozessoutput bleiben privat/unversioniert; nur synthetische Zusammenfassung
und Hashbindung werden übernommen. Nächster eigenständig begrenzter Schnitt ist
die [Filter-/Ergebnisdiagnose](SQL_SERVER_2025_AI_ANN_FILTER_DECISION.md).

## Quellen- und Prüfbindung

Fünf bestehende Grenztests und sechs neue Plan-/Manipulationstests bestanden vor
SQL. Der enge unabhängige Methoden-/Quellenreview fand keine konkreten P1/P2.
Unveränderte gültige Safety-/Helperanalysen wiederverwendet. Ein Owner, ein
erforderlicher Reviewer; Modell-/Tokenverbrauch unbekannt.

| Private Quelle unter ANN_PLAN_CANDIDATE01 | SHA-256 |
|---|---|
| qualify_build.py | B87CCCDED2667520F27F3D7229EBEC46D212E90AD4A1D38343B33FE1144C9EDA |
| sql_build.py | 46C628012A9B6BC5C8DD761DFEAF0BACFACD8864123B6A1128650B9DFBA12B26 |
| plan_evidence.py | 9F6E12D55A739FDAEDB16F2668F13F37ACF0A04489425AEA57ACB072985767EC |
| test_plan.py | DE090F9556A0FEAAA872B23D8EEE58E9FC0A7BB0F657B15D594DBAB37F455EA6 |
| lifecycle01.log | 7F4EB6BD139106A970875724DD3DC1F5B30A8C3EDB25DF5CC9C6EFCC3C5A1B76 |
