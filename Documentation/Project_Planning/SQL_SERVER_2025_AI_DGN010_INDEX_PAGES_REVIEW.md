# DGN-010: vorhandene Indexseiten getrennt auswerten

Stand: 2026-10-12. TSK-011/CUR-021. DGN-010 weiterhin PROPOSED.
Reine neue Allokationsfrage auf zwei bereits vollständig qualifizierten
[Build-/Dropprofilen](SQL_SERVER_2025_AI_DGN010_BUILD_COST_REVIEW.md).
Keine SQL-Ausführung, kein Provisioning und keine neue Runtimequalifikation.

## Herkunft und begrenzter Umfang

PR 205 vollständig abgeschlossen: Head 80a15de86d52861a175185702e60ed22b13cd81e
mit sieben aktuellen Workflows PASS, main 6079f7a50f3ab0a61d1e21ec9d79a9d2d19e2e16
mit fünf Workflows PASS. Ganzer Tree a79cf4384f2d1787b862cc11ac30aa45f3d84084
exakt übernommen; FF-main sauber, eigener lokaler/Remote-Branch entfernt.
Beide eigenen Nativeinstanzen abwesend und kein UNKNOWN.

Ein Implementierungsverantwortlicher, genau eine reine Ableitung und drei
synthetische Gegenproben. Keine zusätzliche Reviewkette oder unveränderte
Nativewiederholung. Verbrauch unbekannt. Vollrecords bleiben privat; genaue
Record-SHA256 vor Ableitung erneut geprüft:

- Profil 1: 581deec8829a372b629384027e64a26dd654eb76ca131438de06feb5b04670f8
- Profil 2: 710b5a50ba66216f5b06d18fff1599d44619bc5d0ee401fe1a7bae24620c2181

Aktuelle ursprüngliche Nativequellen ebenfalls unverändert. Die fünf festen
Sourceaufnahmeplätze 3/4/5/6/7 je Profil repräsentieren A/B/A/B/A: vor Build1,
nach Build1/Drop1 und nach Build2/Drop2. Alle zehn Allokationsbeobachtungen
erhalten. Die vollständigen Row-/Reader-/Marker-/Lease-/State-/Cleanupbelege
stammen unverändert aus dem bereits gebundenen Ursprungsprofil.

## Tatsächliche Indexallokationen

`20_Probe.sql` summierte `sys.dm_db_partition_stats.row_count`,
`used_page_count` und `reserved_page_count` je tatsächlichem eigenen Index.
In beiden Profilen wurde je Index `row_count=1000` beobachtet. Der Katalogwert
ist dokumentiert näherungsweise; die tatsächlichen 1000 Source-Rows sind
separat durch vollständige ID-/Value-/Payloadoracles belegt.

Die folgenden Werte waren in beiden Profilen identisch:

| Zustand | PK Used / Reserved Pages | Candidate Used / Reserved Pages | Summe ausgewählter Indizes Used / Reserved Pages |
| --- | --- | --- | --- |
| A vor Build1 | 18 / 33 | Abwesend, keine Katalogrow | 18 / 33 |
| B nach Build1 | 18 / 33 | 17 / 33 | 35 / 66 |
| A nach Drop1 | 18 / 33 | Abwesend, keine Katalogrow | 18 / 33 |
| B nach Build2 | 18 / 33 | 17 / 33 | 35 / 66 |
| A nach Drop2 | 18 / 33 | Abwesend, keine Katalogrow | 18 / 33 |

Begrenzter beobachteter Mehrbedarf des vorhandenen Candidate: 17 Used Pages
und 33 Reserved Pages für diesen festen 1000-Row-Fall. Die Summe enthält nur
PK und gegebenenfalls Candidate, nicht alle Objekte der Datenbank. Bei A ist
der Candidate tatsächlich abwesend; fehlende Katalogwerte werden nicht als
gemessene Null ausgegeben. Used und Reserved werden getrennt erhalten.

`used_page_count` umfasst Speicher- und Verwaltungsseiten der Partition,
nicht allein Nutzdaten oder Leaf Pages. Reserved umfasst auch reservierte
ungefüllte Seiten. Die Aufnahme belegt weder kompletten Datenbank-/Datei- oder
OS-Speicher noch RAM, Logvolumen, Bytepayload, Shrink oder allgemeinen
Indexnettonutzen. Aus dem Verschwinden der Indexrow folgt kein Dateischrumpfen.
Die vorhandene Datei-Statebindung belegt nur unveränderte erfasste Dateimetadaten.

Drei reine Gegenproben bestanden: erwartete Abwesenheit/Summen, fehlende/fremde
Populationen, Bool-/Floataliaswerte, negative Werte, Reserved kleiner als Used
und PK-Drift werden abgewiesen. Reine Ableitung bestanden: null neue SQLcalls,
null neue Container. Keine neue Row-/DDL-/Runtime- oder vollständige TP-PERF-Abnahme.
Private Inputs/Hashes/Ergebnisse bleiben unter ignoriertem Runtime.

## Primärquelle und nächste Integration

[sys.dm_db_partition_stats](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-db-partition-stats-transact-sql?view=sql-server-ver17),
Abruf 2026-10-12: Used/Reserved/Rowcount und Aggregation je Partition/Index.
Dokumentierte Semantik ist kein zusätzlicher empirischer Speichernachweis.

Aktuelle Head-/Main-/PR-/Tree-/FF-/Ownbranchgates schließen den Dokumentschnitt.
Danach getrennten öffentlichen Record-/Aggregationsvertrag für die vorliegenden
Build-/Drop-/Allokationsfelder vorbereiten. Herkunft, numerische Konsistenz und
Runtime-/Worker-/Nettonutzenqualifikation bleiben verschiedene Claims.
