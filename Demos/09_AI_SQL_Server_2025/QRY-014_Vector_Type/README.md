# QRY-014 – Vektortypen, Dimension und Modellraum

Status: IMPLEMENTED; aktuelle Runtime-/CI-Abnahme noch offen. Zuordnung: CUR-013/CUR-014, TSK-005.

## Lernziel und Aussagegrenze

Die Demo erklärt vektortypen, dimension und modellraum mit synthetischen, deterministischen Geometrievektoren
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
python Demos/00_Framework/Tools/run_demo.py Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/manifest.json --server '<instanz>' --auth integrated --show-output
```

SQL-Authentifizierung nutzt ausschließlich SQLCMDPASSWORD; kein Kennwort als Argument.
Preflight ist read-only und prüft Engine, Plattform, Rechte, native Funktionen und vorhandene
Marker. Setup validiert Marker vor Änderungen, setzt nur die eigene DB auf CL 170 und baut
kleine Fixtures. Baseline, Demonstration und Observation zeigen Werte und Ursache; Mitigation
begründet die fachliche Entscheidung; Comparison prüft Invarianten mit EXACT/RANGE statt
maschinenabhängigen Laufzeitversprechen. Jede Phase druckt SQLPERF_SUMMARY.

Bei Abbruch wird Cleanup vom Harness versucht. Manueller markergebundener Recovery:

```powershell
sqlcmd -S '<instanz>' -E -b -v DemoId='QRY-014' RunToken='LOCAL' TargetDatabase='SQLPERF_LAB_QRY014_LOCAL' -i Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/90_Cleanup.sql
```

Ohne alle vier exakten Eigentumsmarker wird Cleanup abgewiesen, auch bei passendem Namen.
Bei Markerfehler bleibt die Datenbank zur bewussten Klärung erhalten. Marker werden ohne Trunkierung als Unicode-Bytes verglichen, einschließlich nachgestellter Leerzeichen.
Alle Fachphasen prüfen zusätzlich Marker und aktuellen DB-Kontext. Die Runtimeprüfung liest
nach jedem Lauf unabhängig master und bestätigt DB-Abwesenheit; ein Cleanupfehler ist FAIL.

## Phasen und Übung

| Phase | Beobachtung und Einordnung |
|---|---|
| Baseline | Fünf geometrische Vektoren; VECTORPROPERTY liefert drei Dimensionen und float32. JSONdarstellung und DATALENGTH betreffen unterschiedliche Speicherformen. |
| Demonstration | Zwei ungültige Eingaben (Dimension und JSON (JavaScript Object Notation; strukturiertes Textformat)) werden abgewiesen. Das ist Typvalidierung, keine Modellqualifikation. |
| Observation | Daten- und Logfiles sowie Typproperties werden in der eigenen Datenbank gelesen. |
| Mitigation | Gleiche Dimension genügt nicht: GEOMETRY_V1 und GEOMETRY_V2 bleiben verschiedene Modellräume. Der einfache Metadatencheck ist eine Lehrfixture, keine produktive Modellregistry. |
| Comparison | Genau fünf Rows besitzen Dimension drei und den Basistyp float32. |

Übung: Warum lässt sich aus VECTOR(3) nicht erkennen, welches Modell den Vektor erzeugt hat?
Musterantwort: Der Typ trägt Dimension und Basistyp; Modellidentität, Digest und Eingabeprofil
müssen zusätzlich gespeichert und vor Vergleichen geprüft werden. Ein Cast validiert keine Semantik.

## Erwartung und Bewertung

Die SQL-Assertions und Expected/result-contract.json bilden prüfbare Invarianten. Rundungsfehler
werden ausschließlich bei Floating-Point-Größen mit 1e-6 toleriert. Auffällige Werte sind mit
Build und Versuch zu erklären, nicht bis zu einem zufälligen PASS zu wiederholen. Verständnisfrage:
Welche Beobachtung belegt Mechanik, welche zusätzliche Evidenz wäre für fachliche Qualität nötig?
Die Musterantwort nennt die Fixturegrenze und trennt SQL-Ergebnis, Retrieval und Modellantwort.

## Quellen und Traceability

SRC-072/SRC-076; geprüft am 2026-10-11 im [Quellenregister](../../../Documentation/Research/SOURCE_REGISTER.md).
Dokumentierte Produktgrenzen, empirische Buildbeobachtungen und offene Gates werden in der
[Featurematrix](../../../Documentation/Research/SQL_SERVER_2025_AI_FEATURE_MATRIX.md) getrennt geführt.
Testprofile: TP-RUN, bei Suchvergleich zusätzlich TP-PERF; keine Benchmarkfreigabe durch einen Einzellauf.
