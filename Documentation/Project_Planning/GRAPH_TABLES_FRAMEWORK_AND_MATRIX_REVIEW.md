# Graph Tables: Framework- und Zielmatrixprüfung

Stand: 7. November 2026  
Status: Quellen- und Vertragsprüfung; keine Implementierung oder Ausführung

## Ergebnis

Der Projektrahmen stellt einen begrenzten Ein-Session-Pfad bereit. Die
Framework-Readme, die Vorlagen und die Verträge `FWK-002`, `FWK-004`, `FWK-005`,
`FWK-008`, `FWK-010`, `FWK-011` und `FWK-012` bilden zusammen die notwendigen
Bausteine für markierte Testdatenbank, synthetische Daten, Vergleichsmessung,
Planbeobachtung, Sicherheits-/Abbruchstatus, Demoanleitung, Cleanup,
Ergebnisoracle und kontrollierte Versions-SKIPs.

Graph-NODE- und EDGE-Tabellen dürfen keine temporären Tabellen sein. Deshalb
müssen sie in der ausschließlich eigenen, über `FWK-002` markierten
wegwerfbaren Testdatenbank liegen. Ein Datenbankname allein berechtigt nie zur
Wiederverwendung oder Entfernung. `GREEN` ist angemessen, solange ausschließlich
synthetische Objekte in dieser Datenbank verändert werden und kein relevanter
Instanzzustand betroffen ist. Das Cleanup muss nach gestarteter Setup-Phase
unabhängig vom vorausgehenden Ergebnis laufen; unbekanntes Eigentum führt zum
Abbruch und nicht zum erzwungenen Entfernen.

## Curriculumabgleich

`LO-M03-06` fordert einen einzelnen Query-Rewrite als Hypothese mit identischer
Baseline und Vergleichsmessung. `CLM-047` verlangt ausdrücklich die Prüfung
über Plan und Messung. Daher sind Ergebniskorrektheit, Planbeobachtung und
Baseline-/Vergleichsmessung verpflichtende Lern- und Abnahmeschritte. Der
vorherige Konzeptstand, der Messung als optionale spätere Beobachtung führte,
war zu schwach und ist mit diesem Review korrigiert.

Messwerte werden als Ergebnis genau dieses synthetischen Laufs dokumentiert.
Ein einzelner oder schwankender Messbefund begründet weder eine allgemeine
Graph-/Relational-Rangfolge noch einen Performanceclaim. Die Vergleichsformen
müssen gleiche logische Daten, Parameter, Ergebnissemantik, Enginebuild,
Compatibility Level, Ressourcenprofil und Messmethode verwenden. Die
Graph- und relationalen Indexe müssen fachlich begründet und vollständig
beschrieben werden; ihre physische Implementierung kann nicht als identisch
vorausgesetzt werden.

`FWK-004` verlangt Warm-up-Ausschluss, dokumentierte Wiederholungen und einen
begründeten robusten Lagewert samt Streuung oder zulässiger Bandbreite. `FWK-005`
ergänzt sessionbezogene Plan- und Laufzeitevidenz. Ein fester Wiederholungsplan,
die deterministische Lastgröße und die Indexdefinitionen sind vor Erstellung
ausführbarer Dateien noch auszuarbeiten. Der bestehende Fünf-Knoten-Vier-Kanten-
Fixture bleibt ein kleines Korrektheitsoracle; es ist ausdrücklich nicht als
ausreichendes Messworkload qualifiziert.

## Zielmatrix für die nächste Designstufe

| Projektprofil | Engine | Compatibility Level | Rolle |
|---|---:|---:|---|
| Basis | SQL Server 2019 (15.x) | 150 | erste unterstützte Projektversion |
| Zwischenstand | SQL Server 2022 (16.x) | 160 | mittlere unterstützte Projektversion |
| aktuell | SQL Server 2025 (17.x) | 170 | aktuelle unterstützte Projektversion |

Dies ist die vorgeschlagene Matrix für die spätere gezielte QRY-023-Qualifikation.
Sie folgt den bestehenden Framework-/Demo-Zielversionen und Microsofts
Versionszuordnung der Compatibility Levels. Microsoft dokumentiert Graph
NODE-/EDGE-Tabellen und `MATCH` ab SQL Server 2017; die Referenz prüft keine
QRY-023-Projektbuilds, Editionen oder Compatibility-Level-Kombinationen. Die
gewählten Projektprofile sind daher **Designziele**, noch keine
Graph-Runtimefreigabe. Konkrete Build-/CU-Pins, Editionen und Containerimages
werden unmittelbar vor der Implementierung gegen den dann aktuellen
Projektmatrix- und Servicingstand bestätigt.

## Quellen

Microsoft-Primärquellen, abgerufen am 7. November 2026:

- [`SRC-122`](../Research/SOURCE_REGISTER.md#graph-tables--eng-begrenzte-sql-graph--und-compatibility-quellen): [CREATE TABLE (SQL Graph)](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-table-sql-graph?view=sql-server-ver17) – Geltung ab SQL Server 2017; NODE-/EDGE-Tabellen; temporäre Graph-Tabellen werden nicht unterstützt.
- [`SRC-123`](../Research/SOURCE_REGISTER.md#graph-tables--eng-begrenzte-sql-graph--und-compatibility-quellen): [ALTER DATABASE Compatibility Level (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-database-transact-sql-compatibility-level?view=sql-server-ver17) – Zuordnung und zulässige Compatibility Levels für SQL Server 2019, 2022 und 2025.

Projektverträge, geprüft am selben Datum: `Demos/00_Framework/README.md`,
`Demos/00_Framework/Templates/README_TEMPLATE.md`,
`Demos/00_Framework/Contracts/FWK-002_TestDatabase_Lifecycle_Contract.md`,
`FWK-004_Measurement_Contract.md`,
`FWK-005_Plan_Statistics_Evidence_Contract.md`,
`FWK-008_Safety_Abort_Contract.md`, `FWK-010_Runtime_Harness_Contract.md`,
`FWK-011_Result_Normalization_Contract.md`,
`Documentation/Curriculum/CURRICULUM_ARCHITECTURE.md` und
`TRACEABILITY_MATRIX.md`.

Es gab keine Code-, Test-, SQL-, Lab- oder Runtimeausführung.
