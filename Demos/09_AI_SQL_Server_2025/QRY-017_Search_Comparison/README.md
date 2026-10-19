# QRY-017 – Relationale, Full-Text- und exakte Vektorsuche

Status: IMPLEMENTED; gezielte Volltextprobe auf SQL Server 2025/Linux bestanden.
Umfang und Grenzen stehen im [Abnahmenachweis](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_FULLTEXT_REHEARSAL.md).
Zuordnung: CUR-017/CUR-020, TSK-005; vollständige Streamabnahme bleibt offen.

## Lernziel und Aussagegrenze

Die Demo erklärt relationale, full-text- und exakte vektorsuche mit synthetischen, deterministischen Geometrievektoren
und technischen Fantasietexten. Sie erzeugt keine Embeddings und behauptet keine gemessene
Sprachsemantik, Inferenzleistung oder allgemeine Suchbeschleunigung. Theorie und Bewertung
stehen im [Modulvertrag](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md).

## Voraussetzungen und Sicherheitsstufe

SQL Server 2025 (17.x), CL 170; float32 ohne Preview. Enterprise Developer auf Windows/Linux
ist der Entwicklungszielumfang; weitere Editionen und Windows-Runtime sind noch nicht qualifiziert.
2019/2022 enden vor Setup mit SKIP_VERSION. Grün, eine Session, 180 Sekunden plus 60 Sekunden
Cleanup. Maximal 1000 synthetische Rows; Datenfile maximal 256 MiB, Logfile maximal 64 MiB.
Vorgeschlagenes Lab: vier logische CPUs, 16 GiB Host-RAM und 10 GiB Laborplatz.

Setup/Cleanup benötigen CREATE DATABASE und Eigentümerrechte an der eigenen Datenbank;
Teilnehmerabfragen nur SELECT auf lab-Objekte. Keine Server-State-, Modell-, Credential- oder
externen Endpointrechte. Das separate Setupkonto wird nicht als notwendiges Teilnehmerrecht
interpretiert. Zeit- und Dateilimits werden durch Harness und SQL-Dateigrenzen erzwungen.
Float16 und ANN gehören zu separaten Previewpfaden. Fremde Datenbanken, Container, Modelle
und Hostdienste werden weder übernommen noch verändert.

## Schritt-für-Schritt-Anleitung

Die [zentrale Anleitung](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md) führt den
manifestbasiert ausgeführten Pfad. Auf einer dedizierten Testinstanz mit eigener Authentifizierung:

```powershell
python Demos/00_Framework/Tools/run_demo.py Demos/09_AI_SQL_Server_2025/QRY-017_Search_Comparison/manifest.json --server '<instanz>' --auth integrated --show-output
```

SQL-Authentifizierung nutzt ausschließlich SQLCMDPASSWORD; kein Kennwort als Argument.
Preflight ist read-only und prüft Engine, Plattform, Rechte, native Funktionen und vorhandene
Marker. Setup validiert Marker vor Änderungen, setzt nur die eigene DB auf CL 170 und baut
kleine Fixtures. Baseline, Demonstration und Observation zeigen Werte und Ursache; Mitigation
begründet die fachliche Entscheidung; Comparison prüft Invarianten mit EXACT/RANGE statt
maschinenabhängigen Laufzeitversprechen. Jede Phase druckt SQLPERF_SUMMARY.

Bei Abbruch wird Cleanup vom Harness versucht. Manueller markergebundener Recovery:

```powershell
sqlcmd -S '<instanz>' -E -b -v DemoId='QRY-017' RunToken='LOCAL' TargetDatabase='SQLPERF_LAB_QRY017_LOCAL' -i Demos/09_AI_SQL_Server_2025/QRY-017_Search_Comparison/90_Cleanup.sql
```

Ohne alle vier exakten Eigentumsmarker wird Cleanup abgewiesen, auch bei passendem Namen.
Bei Markerfehler bleibt die Datenbank zur bewussten Klärung erhalten. Marker werden ohne Trunkierung als Unicode-Bytes verglichen, einschließlich nachgestellter Leerzeichen.
Alle Fachphasen prüfen zusätzlich Marker und aktuellen DB-Kontext. Die Runtimeprüfung liest
nach jedem Lauf unabhängig master und bestätigt DB-Abwesenheit; ein Cleanupfehler ist FAIL.

## Phasen und Übung

| Phase | Beobachtung und Einordnung |
|---|---|
| Baseline | Identifier MOD_A liefert genau eine autorisierte Row über eine relationale Abfrage. STATISTICS IO/TIME liefern sessionbezogene Beobachtungen. |
| Demonstration | Exakte Cosine-Rangfolge, LIKE und optional CONTAINS beantworten unterschiedliche Sucharten. Alle Abfragen filtern Tenant A. |
| Observation | Herkunft/Modellraum und Full-Text-Voraussetzung werden sichtbar; vier Rows ergeben keinen repräsentativen Performancebenchmark. |
| Mitigation | Eine Identifierfrage wird relational beantwortet, ohne Modellaufruf. |
| Comparison | Autorisierte Exact-Top-ID ist eins; Modellrequests sind null. Bei installierter Volltextkomponente werden fünf Suchfälle mit exakten ID-Mengen geprüft; fehlende optionale Evidenz bleibt WARN. |

Übung: Welche Suchform eignet sich für eine exakte Modulkennung, welche für Wortsuche und welche für ähnliche Bedeutung?
Musterantwort: Relationale Prädikate behandeln Kennungen, Full-Text behandelt lexikalische Suche.
Eine fachlich qualifizierte semantische Suche benötigt echte Embeddings und Relevanzurteile.
Die konstruierten Vektoren dieses Versuchs belegen ausschließlich die Rangfolgemechanik.

## Erwartung und Bewertung

Die SQL-Assertions und Expected/result-contract.json bilden prüfbare Invarianten. Rundungsfehler
werden ausschließlich bei Floating-Point-Größen mit 1e-6 toleriert. Auffällige Werte sind mit
Build und Versuch zu erklären, nicht bis zu einem zufälligen PASS zu wiederholen. Verständnisfrage:
Welche Beobachtung belegt Mechanik, welche zusätzliche Evidenz wäre für fachliche Qualität nötig?
Die Musterantwort nennt die Fixturegrenze und trennt SQL-Ergebnis, Retrieval und Modellantwort.

## Quellen und Traceability

SRC-073/SRC-100/SRC-104; geprüft am 2026-10-11 im [Quellenregister](../../../Documentation/Research/SOURCE_REGISTER.md).
Dokumentierte Produktgrenzen, empirische Buildbeobachtungen und offene Gates werden in der
[Featurematrix](../../../Documentation/Research/SQL_SERVER_2025_AI_FEATURE_MATRIX.md) getrennt geführt.
Testprofile: TP-RUN, bei Suchvergleich zusätzlich TP-PERF; keine Benchmarkfreigabe durch einen Einzellauf.

Full-Text ist optional. Fehlende Komponente ergibt WARN_OPTIONAL_EVIDENCE_SKIPPED und keinen Full-Text-Beleg. Bei vorhandener Komponente wird ausschließlich der eigene Katalog eingerichtet und Population begrenzt abgewartet. Tenantfilter ist eine Mechanikfixture und ersetzt nicht die CON-010-Abnahme.

Die neutrale Indexsprache `LANGUAGE 0` besitzt keinen Stemmer. Die Wortsuche
verwendet daher das tatsächlich gespeicherte Wort `rote`; `LIKE '%rot%'`
bleibt ein Teilstringvergleich. `CONTAINS`, `FREETEXT` und `CONTAINSTABLE`
müssen für Tenant A jeweils exakt die IDs 1 und 3 liefern. Die Rangwerte
werden nur auf positive Werte geprüft, nicht auf eine feste Größe oder
Reihenfolge. Eine getrennte Tenant-B-Kontrolle erwartet ausschließlich ID 4;
die Suche nach `quarzxyz` darf keine Row liefern. Abweichende oder fehlende
Treffer ergeben `FAIL_RESULT_CONTRACT`. Der Runner verlangt bei installierter
Komponente genau fünf geprüfte Fälle, ansonsten null.

Für eine gezielte Volltextabnahme auf einem eigenen Docker-Lab mit aktivierter
Volltextkomponente:

```powershell
python Tests/Runtime/run_sql2025_ai_local.py --target docker --container '<eigener-container>' --expected-major 17 --demo QRY-017 --require-fulltext
```

Der Aufruf führt zwei vollständige Lifecycles sowie Marker-, Idempotenz- und
Ergebnisgegenfälle aus. Die fünf Suchfälle prüfen auch den Tenantfilter.
Eine fehlende Volltextkomponente ist in diesem
strengen Modus ein Fehler. Der normale Kursaufruf erhält den optionalen
WARN-Pfad. Einrichtung und Entfernung der Komponente bleiben Aufgabe von
`SQL_Server_Lab`; die Demo installiert keine Serverkomponenten.

Die Begriffsabgrenzung folgt
[CONTAINS](https://learn.microsoft.com/en-us/sql/t-sql/queries/contains-transact-sql?view=sql-server-ver17)
und [Volltextsuche](https://learn.microsoft.com/en-us/sql/relational-databases/search/full-text-search?view=sql-server-ver17),
geprüft am 19. Oktober 2026. Die dokumentierte Syntax ersetzt keinen nativen
Suchnachweis.
