# SQL-Server-Runtime-Matrix

## Zweck

Dieser Bereich validiert die implementierten Framework-Komponenten gegen reale, ephemere SQL-Server-Instanzen. Die GitHub-Actions-Matrix verwendet nacheinander beziehungsweise parallel getrennte Container für SQL Server 2019, 2022 und 2025. Pro Job läuft genau eine SQL-Server-Version.

## Matrix

| SQL Server | Container-Tag | erwartete Major Version | Compatibility Level |
|---|---|---:|---:|
| 2019 | `mcr.microsoft.com/mssql/server:2019-latest` | 15 | 150 |
| 2022 | `mcr.microsoft.com/mssql/server:2022-latest` | 16 | 160 |
| 2025 | `mcr.microsoft.com/mssql/server:2025-latest` | 17 | 170 |

Die Tags werden vor jeder Ausführung neu aus der Microsoft Container Registry bezogen. Das Ergebnis bezieht sich deshalb auf den zum Laufzeitpunkt ausgelieferten aktuellen Containerstand und nicht auf ein dauerhaft festgeschriebenes CU.

## Ausgeführte Prüfungen

Der Testtreiber `run_framework_sql_matrix.py` prüft je Version:

1. Engine-Major-Version und unterstützte Engine Edition,
2. `FWK-002` mit `CREATE`, Markerprüfung und `DROP`,
3. `FWK-001` gegen die erzeugte Testdatenbank,
4. Installation und zweimalige deterministische Ausführung von `FWK-003`,
5. Installation sowie Begin/End-Messung von `FWK-004`,
6. Statistikproperties, Histogramm und Actual-Plan-Ausgabe aus `FWK-005`,
7. Installation und reale parallele Sessions aus `FWK-006`,
8. Query-Store-Status, Enable und Restore aus `FWK-007`,
9. XE-Status, Create, Start, Stop und Drop aus `FWK-007`,
10. einen realen `FWK-010`-Harness-Lauf über den containerinternen `sqlcmd`-Proxy.

Alle Testdatenbanken verwenden die FWK-002-Marker und werden im `finally`-Pfad entfernt. Ein Cleanup-Finding lässt den Matrixjob fehlschlagen.

## Zugangsdaten und Datenschutz

Das SA-Kennwort wird ausschließlich zur Laufzeit aus GitHub-Run-Kennungen erzeugt, sofort maskiert und über Umgebungsvariablen an Container und `sqlcmd` übergeben. Es wird nicht im Repository gespeichert. Der Container besitzt keine veröffentlichte Host-Portzuordnung und kein persistentes Volume.

Der Proxy `docker_sqlcmd_proxy.py` legt kein Kennwort auf die Kommandozeile. Er liest repositorylokale SQL-Dateien und überträgt sie über Standard Input an das im Container enthaltene Microsoft-Tool `sqlcmd`. Rohoutput wird nicht als Workflow-Artefakt gespeichert.

## Grenzen

Die Matrix validiert SQL Server auf Linux in offiziellen Microsoft-Containern. Sie ersetzt keine separate Prüfung Windows-spezifischer Funktionen, Editionen oder OS-Metriken. Die `latest`-Tags eignen sich zur laufenden Kompatibilitätsprüfung; ein späterer Release benötigt zusätzlich dokumentierte konkrete Image-Digests oder CU-Stände.
