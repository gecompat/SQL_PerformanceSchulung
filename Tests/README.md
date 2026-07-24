# Tests

## Aktive SQL-Server-unabhängige Prüfungen

Der Workflow `.github/workflows/framework-contracts.yml` ist auf Framework-, Demo-Vertrags- und statische Testpfade begrenzt. Er führt aus:

```bash
python Tests/Static/validate_framework_contracts.py
python Tests/Static/test_result_contract_evaluator.py
python Tests/Static/validate_orchestration_runtime.py
python Tests/Static/test_orchestration_runtime.py
```

Die Prüfungen kontrollieren Pflichtdateien, Statuscodes, Eigentumsmarker, deterministische Generatorregeln, T-SQL-Lexik, Python-Syntax, JSON-Metadaten, Ergebnisverträge, Prozesssteuerung, Safety-Gates, Query-Store- und XE-Verträge sowie Cleanup-Priorität. Die Prozess-Selbsttests verwenden ein synthetisches `sqlcmd`-Ersatzprogramm und benötigen weder Netzwerk noch SQL Server.

## Aktive SQL-Server-Runtime-Matrix

Der Workflow `.github/workflows/framework-sql-matrix.yml` validiert das gemeinsame Framework gegen:

| SQL Server | Major | Compatibility Level | Container |
|---|---:|---:|---|
| 2019 | 15 | 150 | `mcr.microsoft.com/mssql/server:2019-latest` |
| 2022 | 16 | 160 | `mcr.microsoft.com/mssql/server:2022-latest` |
| 2025 | 17 | 170 | `mcr.microsoft.com/mssql/server:2025-latest` |

Der validierte Lauf `30099942191` hat alle drei Matrixjobs erfolgreich abgeschlossen. Geprüft wurden Lifecycle, Preflight, Datengenerator, Messrahmen, Plan-/Statistikevidenz, parallele SQL-Sessions, Query Store, Extended Events, Runtime-Harness und markergeprüftes Cleanup.

Die Matrix verwendet pro Job eine ephemere Developer-Instanz ohne Host-Port und ohne persistentes Volume. Das Kennwort wird zur Laufzeit erzeugt, maskiert und nicht in Dateien oder Prozessargumenten gespeichert. Details stehen unter [`Tests/Runtime`](Runtime/README.md) und im [Matrixreview](../Documentation/Project_Planning/SQL_SERVER_RUNTIME_MATRIX_REVIEW.md).

## Toolklassifikation

- Die Python-Prüfungen und Frameworkskripte sind User-defined Tools des Projekts.
- Das produktive Runtime-Framework verwendet das externe Microsoft-Tool `sqlcmd`.
- Fehlt `sqlcmd`, wird dies als `SKIP_TOOL_MISSING` und nicht als SQL-Server-Fehler behandelt.

## Nächste Prüfbereiche

- zwei grüne Gate-B-Pilotdemos,
- eine gelbe Multi-Session-Blocking-Demo,
- eine gelbe Ressourcen-Demo,
- automatisierte Privacy- und Metadatenprüfung,
- Windows- oder OS-spezifische Profile nur bei konkreter Demoabhängigkeit,
- Releasevalidierung mit dokumentierten Containerdigests oder CU-Ständen.

Tests und Reports dürfen keine realen Zugangsdaten oder Umgebungsinformationen persistieren. Interaktiv notwendige reale Resultsets sind keine Repository-Artefakte.
