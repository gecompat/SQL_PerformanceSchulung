# QRY-016 – Chunking, Overlap und Provenienz

Status: IMPLEMENTED; aktuelle Runtime-/CI-Abnahme noch offen. Zuordnung: CUR-015, TSK-005.

## Lernziel und Aussagegrenze

Die Demo erklärt chunking, overlap und provenienz mit synthetischen, deterministischen Geometrievektoren
und technischen Fantasietexten. Sie erzeugt keine Embeddings und behauptet keine gemessene
Sprachsemantik, Inferenzleistung oder allgemeine Suchbeschleunigung. Theorie und Bewertung
stehen im [Modulvertrag](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md).

## Voraussetzungen und Sicherheitsstufe

SQL Server 2025 (17.x), CL 170; float32 ohne Preview. Enterprise Developer auf Windows/Linux
ist der Entwicklungszielumfang; weitere Editionen und Windows-Runtime sind noch nicht qualifiziert.
2019/2022 enden vor Setup mit SKIP_VERSION. Grün, eine Session, 180 Sekunden plus 60 Sekunden
Cleanup. Maximal 1000 synthetische Rows; Datenfile maximal 256 MiB, Logfile maximal 64 MiB.
Vorgeschlagenes Lab: vier logische CPUs, 16 GiB Host-RAM (Random Access Memory; Arbeitsspeicher) und 10 GiB Laborplatz.

Setup/Cleanup benötigen CREATE DATABASE und Eigentümerrechte an der eigenen Datenbank;
Teilnehmerabfragen nur SELECT auf lab-Objekte. Keine Server-State-, Modell-, Credential- oder
externen Endpointrechte. Das separate Setupkonto wird nicht als notwendiges Teilnehmerrecht
interpretiert. Zeit- und Dateilimits werden durch Harness und SQL-Dateigrenzen erzwungen.
Float16 und ANN (Approximate Nearest Neighbor; näherungsweise Suche nach ähnlichen Vektoren) gehören zu separaten Previewpfaden. Fremde Datenbanken, Container, Modelle
und Hostdienste werden weder übernommen noch verändert.

## Schritt-für-Schritt-Anleitung

Die [zentrale Anleitung](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md) führt den
manifestbasiert ausgeführten Pfad. Auf einer dedizierten Testinstanz mit eigener Authentifizierung:

```powershell
python Demos/00_Framework/Tools/run_demo.py Demos/09_AI_SQL_Server_2025/QRY-016_Chunk_Provenance/manifest.json --server '<instanz>' --auth integrated --show-output
```

SQL-Authentifizierung nutzt ausschließlich SQLCMDPASSWORD; kein Kennwort als Argument.
Preflight ist read-only und prüft Engine, Plattform, Rechte, native Funktionen und vorhandene
Marker. Setup validiert Marker vor Änderungen, setzt nur die eigene DB auf CL 170 und baut
kleine Fixtures. Baseline, Demonstration und Observation zeigen Werte und Ursache; Mitigation
begründet die fachliche Entscheidung; Comparison prüft Invarianten mit EXACT/RANGE statt
maschinenabhängigen Laufzeitversprechen. Jede Phase druckt SQLPERF_SUMMARY.

Bei Abbruch wird Cleanup vom Harness versucht. Manueller markergebundener Recovery:

```powershell
sqlcmd -S '<instanz>' -E -b -v DemoId='QRY-016' RunToken='LOCAL' TargetDatabase='SQLPERF_LAB_QRY016_LOCAL' -i Demos/09_AI_SQL_Server_2025/QRY-016_Chunk_Provenance/90_Cleanup.sql
```

Ohne alle vier exakten Eigentumsmarker wird Cleanup abgewiesen, auch bei passendem Namen.
Bei Markerfehler bleibt die Datenbank zur bewussten Klärung erhalten. Marker werden ohne Trunkierung als Unicode-Bytes verglichen, einschließlich nachgestellter Leerzeichen.
Alle Fachphasen prüfen zusätzlich Marker und aktuellen DB-Kontext. Die Runtimeprüfung liest
nach jedem Lauf unabhängig master und bestätigt DB-Abwesenheit; ein Cleanupfehler ist FAIL.

## Phasen und Übung

| Phase | Beobachtung und Einordnung |
|---|---|
| Baseline | Beide Dokumentversionen werden mit FIXED, CHUNK_SIZE=24 und OVERLAP=0 zerlegt. |
| Demonstration | OVERLAP=25 erzeugt ein zweites getrenntes Profil; Chunkzahl und summierte Bereichslängen werden ausgegeben. Zeichen sind keine Modelltoken. |
| Observation | DocId, Version, Reihenfolge, Offset, Länge und Text werden mit SUBSTRING der Originalquelle verglichen. |
| Mitigation | Versionen bleiben erhalten; Chunkgröße null und Overlap 51 werden abgewiesen. |
| Comparison | Beide Versionen und beide Profile müssen nichtleer vorhanden sein; Reihenfolgen sind lückenlos und Chunktexte entsprechen bytegenau ihren Quellenbereichen. |

Übung: Warum ist ein Chunktext ohne Dokumentversion und Zeichenbereich kein ausreichender Quellenbeleg?
Musterantwort: Änderungen am Dokument können den Text und dessen Position verändern.
Quellenversion und Bereich erlauben die erneute Prüfung. Overlap erzeugt mehrfach verarbeitete
Zeichen; eine größere Summe beweist weder bessere Relevanz noch geringe Inferenzkosten.

## Erwartung und Bewertung

Die SQL-Assertions und Expected/result-contract.json bilden prüfbare Invarianten. Rundungsfehler
werden ausschließlich bei Floating-Point-Größen mit 1e-6 toleriert. Auffällige Werte sind mit
Build und Versuch zu erklären, nicht bis zu einem zufälligen PASS zu wiederholen. Verständnisfrage:
Welche Beobachtung belegt Mechanik, welche zusätzliche Evidenz wäre für fachliche Qualität nötig?
Die Musterantwort nennt die Fixturegrenze und trennt SQL-Ergebnis, Retrieval und Modellantwort.

## Quellen und Traceability

SRC-079; geprüft am 2026-10-11 im [Quellenregister](../../../Documentation/Research/SOURCE_REGISTER.md).
Dokumentierte Produktgrenzen, empirische Buildbeobachtungen und offene Gates werden in der
[Featurematrix](../../../Documentation/Research/SQL_SERVER_2025_AI_FEATURE_MATRIX.md) getrennt geführt.
Testprofile: TP-RUN, bei Suchvergleich zusätzlich TP-PERF; keine Benchmarkfreigabe durch einen Einzellauf.

Zusätzliche Preflightgrenze: Die initiale Verbindung in master benötigt CL 170 für die read-only Chunkfunktionprobe. Ein niedrigeres Master-CL führt konservativ vor Setup zu SKIP_COMPATIBILITY_LEVEL; master wird nie geändert.
