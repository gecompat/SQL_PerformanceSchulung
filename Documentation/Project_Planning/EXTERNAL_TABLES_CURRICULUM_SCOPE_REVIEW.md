# External Tables: Curriculum-Scope und Projektentscheidung

Stand: 12. November 2026
Status: `DEC-078` registriert; begrenzte Curriculum-Scopeentscheidung, keine
Demo-, SQL- oder Runtimefreigabe

## Projektentscheidung für den aktuellen Scope

Die vorhandene External-Tables-Lernnotiz bleibt eine ergänzende Erklärung zu
`LO-M03-05` und `CLM-045`. Sie wird nicht als neue ausführbare Phase in
`QRY-012` aufgenommen. `QRY-012` behält seinen geplanten Remote-Pushdown-Pfad
für Linked Server als optionales, topologieabhängiges Sonderlabor. Eine spätere
External-Tables-Demo braucht einen eigenen abgegrenzten Vertrag und eine
separate Freigabe, bevor eine Demo-ID vergeben wird.

Diese Entscheidung gilt für den aktuellen Curriculum- und Demo-Scope. Sie
verwirft External Tables nicht als Lehrthema und erlaubt keine Infrastruktur-
oder Laufzeiteinrichtung. Die verbindliche Fassung steht als `DEC-078` im
[Projektentscheidungsregister](../../.ai/DECISIONS.md).

## Gründe

Der bestehende Abdeckungsplan ordnet `QRY-012` bereits zwei voneinander
getrennte Phasen zu: lokale Partition-Elimination und – nur bei freigegebener
Mehrinstanztopologie – Remote Pushdown mit Linked Server. Die Phasen teilen
eine Demo-ID, aber weder Setup noch Sicherheitsweg. Er mischt außerdem
JSON-/XML-/Stringkosten nicht in diese Demo. External Tables würden eine
weitere, wesentlich andere Zugriffsinfrastruktur hinzufügen: PolyBase-
Komponenten, eine externe Datenquelle, Connector- und Betriebssystemprofile,
Credentials sowie eigene Cleanup- und Recoverypfade.

Die gemeinsame Lernfrage „Remote Pushdown ist provider-, Ausdrucks- und
planabhängig“ passt zu `LO-M03-05`/`CLM-045`; die bereits integrierte Lernnotiz
erfüllt diesen erklärenden Zweck. Die tatsächliche Datenwegevidenz einer
External Table ist jedoch an ein konkretes Connectorprofil gebunden. Die
Microsoft-Produktmatrix weist zwar External Tables und SQL-Server-Quellen für
2019, 2022 und 2025 aus, aber die verfügbaren Connector-/Betriebssystemwege
sind nicht über alle Profile gleich. Der Entwurf wählt deshalb vorläufig
`sqlserver://` und Windows als gemeinsamen Matrixkandidaten, ohne damit
Verfügbarkeit oder Laufrechte in dieser Projektumgebung zu behaupten.

Die Pushdown-Quelle unterscheidet geplante Remoteabfrage und tatsächliche
Requestbeobachtung. Bei SQL Server 2019 und später kann
`sys.dm_exec_external_work.read_command` die an die Quelle gesendete Abfrage
anzeigen; für Hadoop- und Azure-Storage-Pfade ist der Wert `NULL`, und die
Ausgabe kann bei 4.000 Zeichen abgeschnitten sein. Eine fehlende oder nicht
korrelierbare Beobachtung bleibt daher `NOT_PROVEN`. Trace Flag 6408 ist keine
allgemeine Voraussetzung für diesen DMV-Nachweis. Diese Grenzen stützen eine
eigenständige Profilqualifikation statt einer zusätzlichen, undifferenzierten
Phase in `QRY-012`.

## Konsequenzen und offene Arbeit

- Die Lernnotiz bleibt über den vorhandenen Lernziel- und Claimlesepfad
  auffindbar; `CLM-045` und seine Quellenzuordnung werden durch diese
  Scopeentscheidung nicht umgedeutet.
- Der Abdeckungsplan für `QRY-012` bleibt bei seinen bestehenden Phasen. Diese
  Entscheidung ergänzt keine External-Tables-Slide, Demo-ID oder Runtime-
  Anforderung.
- Ein künftiger externer Zugriffspfad muss zunächst OS, Version, Builds/CUs,
  Editionen, Compatibility Levels, Quellbesitz, Isolation, Rechte, Credential-
  Lifecycle, Ressourcen, Zeitgrenzen, Statistikzustand, Pushdown-Evidenz,
  Cleanup und Recovery als zusammenhängenden Vertrag festlegen.
- Erst danach kann eine separate Entscheidung über einen ausführbaren
  External-Tables-Demoschnitt getroffen werden. Das vorliegende Arbeitspaket
  erstellt weder diesen Vertrag noch qualifiziert es die vorgeschlagene
  `sqlserver://`-Matrix.

## Geprüfte Projektpfade und Quellen

Geprüft wurden der bestehende [QRY-012-Abdeckungsplan](PRESENTATION_EXAMPLE_COVERAGE_PLAN.md),
die [External-Tables-Lernnotiz](../Curriculum/EXTERNAL_TABLES_LESSON.md), der
[Demoentwurf](EXTERNAL_TABLES_DEMO_CONCEPT.md), das
[Quellen-/Zugriffswegreview](EXTERNAL_TABLES_SOURCE_REVIEW.md) und die
zugehörigen Backlog- und Statusabschnitte. Die Produktbefunde bleiben an
`SRC-153` bis `SRC-157` gebunden. Die aktuelle Microsoft-Dokumentation hält
die [PolyBase-Verfügbarkeit und Connectorprofile](https://learn.microsoft.com/en-us/sql/relational-databases/polybase/data-virtualization-guide?view=sql-server-ver17)
und die [Grenzen der Pushdown-Diagnose](https://learn.microsoft.com/en-us/sql/relational-databases/polybase/polybase-how-to-tell-pushdown-computation?view=sql-server-ver17)
fest.

Die Scopeentscheidung ist eine Projektableitung auf Basis dieser Pfade und
Produktquellen. Sie ist weder eine Herstellerzusage noch eine Runtime-
Beobachtung oder Performanceaussage.
