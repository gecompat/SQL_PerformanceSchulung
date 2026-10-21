# QRY-018 – Offline-RAG mit überprüfbarer Retrieval-Evidenz

Status: IMPLEMENTED; lokaler Schnitt samt aktuellem PR-/Main-Gate integriert über
[PR 137](https://github.com/gecompat/SQL_PerformanceSchulung/pull/137).
Zuordnung: CUR-017/CUR-022, TSK-008, TP-RUN. Die Demo ist ein deterministischer
Offline-Replay; sie führt weder Embedding- noch generative Modellaufrufe aus.

## Lernziel und Aussagegrenze

Eine zitierte Quelle genügt nicht: Die Quellenstelle muss im erlaubten aktuellen
Retrievalkontext liegen und die konkrete Aussage stützen. Fehlender oder widersprüchlicher
Kontext verlangt eine begründete Nichtantwort. SQL macht Import, Chunking, Vektorspeicherung,
Exact Retrieval, Kontextauswahl und Claimprüfung einzeln sichtbar.

Die drei Geometrievektoren sind konstruiert, keine Sprachembeddings. Die zehn Antworten
sind vorab festgelegte Replayfixtures. Distanzgrenze 0,05 und Top-k=2 illustrieren nur
diesen Fall; sie sind keine allgemeine Relevanzschwelle. Die Claimprüfung erkennt ausschließlich
die feste Satzform zur Aufbewahrungsdauer. Sie ist kein allgemeiner Wahrheits- oder
Entailmentprüfer und belegt keine LLM-Sicherheit. Tokenzahl und Inferenzzeit sind N/A.

## Voraussetzungen und Sicherheitsstufe

SQL Server 2025 (17.x), CL 170, float32 und AI_GENERATE_CHUNKS; kein Preview.
Enterprise Developer ist der Entwicklungszielumfang; Windows, Podman und andere Editionen
benötigen eigene Qualifikation. 2019/2022 beenden Preflight vor Setup mit SKIP_VERSION.
Grün, eine Session, 180 Sekunden regulär und separat 60 Sekunden Cleanup.
19 Basisrows und drei erzeugte Chunks; Dateigrenzen 256 MiB Daten / 64 MiB Log.
Vorgeschlagenes Lab: vier logische CPUs, 16 GiB Host-RAM (Random Access Memory; Arbeitsspeicher), 10 GiB freier Laborplatz.

Setup/Cleanup benötigen CREATE DATABASE und Eigentümerrechte in der eigenen Datenbank.
Die reine Claim-/Retrievalbewertung benötigt nur SELECT auf lab-Views. Chunkaufbau ist
eine eigene Ingestionphase mit INSERT/DELETE; dieses Recht ist kein Teilnehmerrecht.
Keine Server-State-, Modell-, Credential- oder Endpointrechte. Keine fremden Datenbanken,
Container oder Modelle werden übernommen oder verändert.

## Schritt-für-Schritt-Anleitung

Die [zentrale Anleitung](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md) beschreibt
Voraussetzungen und den manifestbasiert ausgeführten FWK-010-Harness. Eigene dedizierte Testinstanz:

```powershell
python Demos/00_Framework/Tools/run_demo.py Demos/09_AI_SQL_Server_2025/QRY-018_Offline_RAG/manifest.json --server '<instanz>' --auth integrated --show-output
```

SQL-Authentifizierung verwendet ausschließlich SQLCMDPASSWORD, kein Passwortargument.
Preflight prüft Version, Edition, Funktionen, Rechte und bestehende Eigentumsmarker.
Setup legt nur die eigene markierte Datenbank und die kleinen synthetischen Tabellen/Views an.
Baseline zeigt die Antworten ohne Quellenkontext; Demonstration erzeugt FIXED64-Chunks
ohne Overlap und liest den gerankten aktuellen Kontext. Observation zeigt jede Entscheidung
mit Quellen-/Fragen-ID und Begründung. Mitigation gibt nur gestützte Antworten beziehungsweise
begründete Nichtantworten frei. Comparison prüft vier gemessene Ergebnisinvarianten.

Der Harness versucht nach gestartetem Setup immer Cleanup. Manueller markergebundener Recovery:

```powershell
sqlcmd -S '<instanz>' -E -b -v DemoId='QRY-018' RunToken='LOCAL' TargetDatabase='SQLPERF_LAB_QRY018_LOCAL' -i Demos/09_AI_SQL_Server_2025/QRY-018_Offline_RAG/90_Cleanup.sql
```

Alle vier vollständigen Eigentumsmarker werden bytegenau geprüft, einschließlich Leerzeichen
und überlanger Werte. Fachphasen prüfen zusätzlich DB-Kontext. Bei fehlendem/falschem Marker
bleibt die Datenbank zur Klärung erhalten. Der Runtime-Test prüft unabhängige DB-Abwesenheit
nach jedem Lifecycle und entfernt anschließend nur seine eigene Containerinstanz.

## Korpus, Replay und Bewertung

Modul A besitzt eine veraltete Version mit fünf Tagen und eine aktuelle mit sieben Tagen.
Die alternative aktuelle Quelle behauptet neun Tage. FIXED64 erzeugt pro kurzem Dokument
genau einen Chunk; Offset, Länge und Unicode-Bytes werden gegen den Originaltext geprüft.
Frage 1 erlaubt ausschließlich die aktuelle Modul-A-Quelle. Frage 2 besitzt im konstruierten
Vektorraum keinen nahen Kontext. Frage 3 erlaubt beide widersprüchlichen aktuellen Quellen.

| Ergebnis | Anzahl | Konkrete Fälle |
|---|---:|---|
| ACCEPTED | 1 | Sieben Tage, tatsächlich retrievte aktuelle stützende Quellenstelle |
| REJECTED | 7 | Falscher Wert; alte Version; fehlender Kontext; Widerspruch; nicht retrievte Quelle; NULL-Claim; unnötige Nichtantwort |
| ABSTAINED | 2 | Keine Evidenz beziehungsweise zwei widersprüchliche Fakten, jeweils ohne erfundenen Claim |

Baseline enthält sieben unüberprüfte Claimfixtures. Expected/result-contract.json prüft diese
Zahl sowie die drei tatsächlichen Ergebniscounts. Ein leeres Ergebnis darf nicht PASS ergeben.
Sieben Runtime-Gegenproben verändern Claim, Zitat, Chunkbestand/-inhalt, aktuelle Version,
Replaybestand und Faktmetadatum; jede muss FAIL_RESULT_CONTRACT auslösen.

Übung: Weshalb ist Antwortfixture 8 trotz eines existierenden Zitats abzulehnen?
Musterantwort: Die alternative Quelle gehört nicht zum erlaubten Retrievalkontext von Frage 1.
Eine beliebige existierende Quelle ersetzt die Bindung an den tatsächlich bereitgestellten Kontext nicht.

Übung: Ist die Antwort mit sieben Tagen bei Frage 3 akzeptabel?
Musterantwort: Beide aktuellen Quellen widersprechen sich. Die Fixture kennt keinen Vorrang;
sie muss den Konflikt benennen und eine Entscheidung zurückhalten. Ein gültiges Zitat löst ihn nicht.

## Quellen und offene Pfade

SRC-073/SRC-079 sowie SRC-095, geprüft am 2026-10-11 im
[Quellenregister](../../../Documentation/Research/SOURCE_REGISTER.md). Weitere Grenzen stehen
in der [Featurematrix](../../../Documentation/Research/SQL_SERVER_2025_AI_FEATURE_MATRIX.md).
Live-RAG (Retrieval-Augmented Generation; Antworterzeugung mit zuvor ausgewählten Quellen) gehört zu einem eigenen Modellpfad; die derzeitige Secret-Grenze von SQL_Server_Lab
steht im [Modellpfad-Leitfaden](../../../Documentation/HowTo/SQL_SERVER_2025_AI_MODEL_PATHS.md).
Der Offline-PASS ist keine Provider-, Sprachmodell-, Kosten- oder Benchmarkabnahme.
