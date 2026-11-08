# QRY-023 – SQL Graph Tables und relationale Pfadabfrage

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED`; integrierter Codeentwurf mit statischer Vertragsprüfung und ScriptDom-Grammatikparse, nicht katalogisiert |
| Sicherheitsstufe | `YELLOW` |
| Lernziel | `LO-M03-06` / `CLM-047` |
| Daten | ausschließlich synthetisch; 10.000 disjunkte Zwei-Kanten-Pfade plus kleines Korrektheitsoracle |
| Profile | Linux/AMD64-Images: SQL Server 2019/150, Build 15.0.4500.2; 2022/160, Build 16.0.4305.5; 2025/170, Build 17.0.5035.5; vorgeschlagene Qualifikationspins, keine Runtimequalifikation |
| Hostressourcen | Vorschlag: x86-64, 2 Kerne mit mindestens 2 GHz, 8 GiB RAM und 20 GiB freier Speicher; nicht empirisch qualifiziert |
| Containergrenze | Vorschlag: höchstens 2 CPU-Kerne, 4.096 MiB Speicher, SQL-Server-Limit 3.072 MiB; 900 Sekunden Lauf-/90 Sekunden Cleanupbudget |
| Runtime | nicht ausgeführt; keine Performanceaussage |

## Zweck

Die Demo stellt denselben gerichteten Pfad einmal mit SQL Graph `MATCH` und
einmal mit relationalen Joins dar. Eine getrennte Fünf-Knoten-Probe prüft die
erwarteten Tupel `(1,2,5)` und `(1,3,5)`. Das Messprofil vergleicht danach
10.000 disjunkte Pfade mit identischem Dateninhalt. Der Umfang begründet keine
allgemeine Empfehlung für Graph- oder relationale Speicherung.

## Codeentwurf und vorgesehene Phasen

| Phase | Datei | Aufgabe |
|---|---|---|
| Preflight | `00_Preflight.sql` | Version, Datenbankname, CREATE DATABASE und exakte Marker einer vorhandenen Zieldatenbank prüfen |
| Setup | `10_Setup.sql` | Eigene markierte Wegwerfdatenbank erstellen oder exakt passende wiederverwenden |
| Framework | `15_Framework.sql` | kanonische FWK-004-Messreferenz installieren |
| Workload | `20_Workload.sql` | 30.000 Knoten, 20.000 Kanten, kleines Oracle, Kandidatenindizes und Messprozedur anlegen |
| Qualification preflight | `25_Qualification_Preflight.sql` | vollständige Marker, SELECT und SHOWPLAN vor den Abfragen prüfen |
| Korrektheit | `30_Correctness.sql` | kleine Oracle-Tupel sowie vollständige 10.000-Pfade-Ergebnismengen in beide Richtungen vergleichen |
| Messung | `40_Measurement.sql` | Warm-up und fünf gepaarte BASELINE/COMPARISON-Läufe mit alternierendem AB/BA erfassen |
| Plan | `50_Plan_Evidence.sql` | separate Actual-Plan-Diagnostik; Planläufe fließen nicht in Messwerte ein |
| Cleanup | `90_Cleanup.sql` | Wegwerfdatenbank nur mit vollständigen Projekt-, Demo- und Run-Markern entfernen |

Der Entwurf heißt `manifest.proposed.json`, damit er von den bestehenden
Runtimekatalogen und automatischen Manifestmatrizen nicht als freigegebene
Demo erkannt wird. `YELLOW` erfordert im FWK-010-Aufrufer eine ausdrückliche
`--confirm-isolated-lab`-Bestätigung; das Manifest autorisiert selbst keinen
Lauf.

`15_Framework.sql` bindet `Demos/00_Framework/Sql/FWK_Measurement.sql` per
SQLCMD-`:r` ein. Der dokumentierte Harness-Aufruf startet deshalb aus dem
Repository-Stamm. Das Manifest ist noch nicht in einen allgemeinen
Ausführungspfad aufgenommen. Die Dateien sind ein nicht ausgeführter Entwurf
und keine qualifizierte Demoimplementierung.

## Rechte und Grenzen

Der vollständige Harness benötigt `CREATE DATABASE`, Berechtigungen für
Tabellen, Indizes und synthetische Inserts in der eigenen Datenbank, `SELECT`
auf den Demoobjekten und `SHOWPLAN` auf der markierten Zieldatenbank. Actual-
Plan-XML wird separat erfasst. `FWK-004` speichert keine Abfragetexte oder
Pläne; es erfasst Sessiondeltas. Die Datenbank wird als Wegwerfdatenbank mit
vollständigen QRY-023-Markern angelegt. Fremde oder nicht vollständig markierte
Ziele werden abgewiesen und nicht entfernt.

Der vorgeschlagene read-only Preflight begrenzt das RunToken auf 1 bis 20
ASCII-Bytes. `DATALENGTH` ergänzt die Zeichenprüfung, weil `LEN`
nachgestellte Leerzeichen ausschließt und ASCII-`LIKE` sie im Suchwert
ignoriert; siehe die Microsoft-Dokumentation zu [`LEN`](https://learn.microsoft.com/en-us/sql/t-sql/functions/len-transact-sql?view=sql-server-ver17) und [`LIKE`](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver17). Diese Bedingung ist offline statisch geprüft, aber noch nicht mit SQL Server ausgeführt.

SQLCMD setzt Skriptvariablen an ihren `$(Name)`-Vorkommen ein, auch in
Zeichenliteralen. Daraus folgt als Sicherheitsinferenz, dass der T-SQL-
Preflight keine SQLCMD-Eingabeinjektion verhindert: Eine unsichere Eingabe kann
die Skriptstruktur vor Auswertung der Guards verändern. Ein künftiger Harness-
Aufrufer muss Demo-ID, RunToken und Zielnamen vor dem SQLCMD-Aufruf exakt gegen
den Vertrag allowlisten. Ein solcher Aufrufer ist nicht Bestandteil dieses
Entwurfs; daher gibt es noch keine Caller-seitige Absicherung.
Die exakten Anforderungen sind im Feld `sqlcmd_input_validation` des
vorgeschlagenen Manifests maschinenlesbar festgelegt und werden offline
strukturell geprüft. Das Feld führt selbst keine Vorabvalidierung aus.

Der QRY-023-Prüflauf wurde nicht gestartet. Der read-only Preflight akzeptiert
für die vorgeschlagenen Linux-Imageprofile ausschließlich Builds `15.0.4500.2`,
`16.0.4305.5` und `17.0.5035.5`; die Setupphase prüft denselben Pin nochmals
vor der Datenbankanlage. Das sind reproduzierbare Designpins nach dem
Image-Metadatenstand vom 7. November 2026, keine Graph-Mindestbuilds. Die
Images werben diese Builds über `com.microsoft.version`. Die AMD64-Manifestdigests
lauten für 2019 `sha256:07d7dedecdbfcf6776035dc5eefb5bfd9aa1804b2f6b99f7dedb397d8a599069`,
2022 `sha256:cf8f0ab2ebe61feec2eed2629061a07d247f791c2a8ddda74a4ac9f06a291718`
und 2025 `sha256:6972fb831759433def6a34e107fa32a85230bff5af8014c6263fe4633ea9cc0f`.
Die 2019-/2022-Tags tragen `GDR12` bzw. `GDR1` und stimmen mit den aktuellen
Linux-CU+GDR-Builds überein. Imagekonfiguration und Produktlabel belegen nicht
den gestarteten `sqlservr`; jeder spätere Lauf muss `SERVERPROPERTY` erfassen
und das Image per Manifestdigest binden. SQL Graph wird
laut Microsoft-Editionsmatrizen in den Editionen von 2019, 2022 und 2025 angeboten.
Der Preflight protokolliert die tatsächliche Edition, beschränkt Graph aber
nicht auf eine bestimmte Edition.

Ein angehefteter Microsoft-ScriptDom-Parser prüft die acht ausführbaren
T-SQL-Dateien mit den Grammatiken für SQL Server 2019, 2022 und 2025. Den
SQLCMD-`:r`-Wrapper prüft er separat auf den erwarteten Include; er parst ihn
nicht als T-SQL. Platzhalter werden nur im Parserprozess synthetisch ersetzt.
Ein Parser-PASS ist keine Kompilierung gegen eine SQL-Server-Engine und belegt
keine Objektbindung, Berechtigungen oder Laufzeitsemantik. Ein Offlinevalidator
prüft zusätzlich Manifestphasen, Markerbindung, Workloadarithmetik,
Ergebnisorakel, Messreihenfolge, Plantrennung und den Nicht-Katalogstatus.

Bevor die Demo in den Katalog oder einen Runtimeworkflow aufgenommen wird,
bleiben formale Harness-Abnahme, unabhängige Methodenfreigabe,
Bestätigung/Erneuerung der Build-Pins, Integration des Image-Locks in einen
späteren Runtimeaufruf, Ressourcenprofil und konkrete Ausführungsgenehmigung
offen.

Der Ressourcenrahmen steht als Vorschlag im `resources`-Abschnitt von
[`container-images.proposed.json`](container-images.proposed.json). Er ist aus
Microsofts Linux-Mindestanforderungen und der geforderten Trennung zwischen
Container- und SQL-Server-Speichergrenze abgeleitet. 8/20 GiB Hostreserve sowie
4/3 GiB Container-/Enginegrenze sind Projektwerte ohne QRY-023-Laufmessung;
der Runtimeaufrufer muss sie vor Start tatsächlich durchsetzen.

## Verträge und Reviews

- [Statischer Demoentwurf](../../../Documentation/Project_Planning/GRAPH_TABLES_DEMO_CONCEPT.md)
- [Messworkload](../../../Documentation/Project_Planning/GRAPH_TABLES_MEASUREMENT_WORKLOAD_DESIGN.md)
- [Quellen- und Methodenreview](../../../Documentation/Project_Planning/GRAPH_TABLES_METHOD_REVIEW.md)
- [Editions- und Buildreview](../../../Documentation/Project_Planning/GRAPH_TABLES_BUILD_EDITION_REVIEW.md)
- [ScriptDom-Grammatikprüfung](../../../Documentation/Project_Planning/GRAPH_TABLES_SCRIPTDOM_PARSER_REVIEW.md)
- [Coverage-Prüfung des Proposed Harness](../../../Documentation/Project_Planning/QRY023_PROPOSED_HARNESS_REVIEW.md)
- Vorgeschlagener unveränderlicher Image-Lock: [`container-images.proposed.json`](container-images.proposed.json); nicht von einem Runtimeworkflow konsumiert und nicht ausführungsberechtigend.
- Framework: `FWK-002`, `FWK-003`, `FWK-004`, `FWK-005`, `FWK-008`, `FWK-010`, `FWK-011` und `FWK-012`.
