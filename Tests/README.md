# Tests

## Aktive SQL-Server-unabhängige Prüfungen

Der Workflow `.github/workflows/framework-contracts.yml` ist auf Framework-, Demo-Vertrags- und statische Testpfade begrenzt. Er führt aus:

```bash
python Tests/Static/validate_framework_contracts.py
python Tests/Static/test_result_contract_evaluator.py
python Tests/Static/validate_orchestration_runtime.py
python Tests/Static/test_orchestration_runtime.py
```

Die Prüfungen kontrollieren unter anderem:

- Pflichtdateien, Statuscodes, Eigentumsmarker und README-Struktur,
- deterministische Generatorregeln,
- T-SQL-Lexik, Python-Syntax und JSON-Metadaten,
- positive und negative Ergebnisverträge,
- Multi-Session-Erfolg, Fail-fast und Timeout,
- Runtime-Harness mit Preflight-Skip, optionalem Evidenz-Skip und Safety-Gates,
- Cleanup-Ausführung und Priorität von `FAIL_CLEANUP`,
- Query-Store-Status ohne Zustandsänderung,
- Extended Events ohne `event_file` und ohne Autostart,
- fehlende Verbindung- oder Secretfelder in Manifesten.

Die Prozess-Selbsttests verwenden ein synthetisches `sqlcmd`-Ersatzprogramm. Sie benötigen weder Netzwerk noch SQL Server und persistieren keinen Prozessoutput.

## Toolklassifikation

- Die Python-Prüfungen sind User-defined Tools des Projekts.
- Das produktive Runtime-Framework verwendet das externe Microsoft-Tool `sqlcmd`.
- Fehlt `sqlcmd`, wird dies als `SKIP_TOOL_MISSING` und nicht als SQL-Server-Fehler behandelt.

## Offene Runtime-Prüfungen

- Parse, Installation und Cleanup aller Framework-SQL-Dateien auf SQL Server 2019, 2022 und 2025,
- tatsächliche Signalsteuerung über parallele SQL-Sessions,
- Query-Store-Baseline, Enable, Clear und Restore,
- XE-Create, Start, Status, Stop und Drop,
- kompletter Runtime-Harness mit realen Demo-Skripten,
- vier Gate-B-Pilotdemos.

Tests und Reports dürfen keine realen Zugangsdaten oder Umgebungsinformationen persistieren. Interaktiv notwendige reale Resultsets sind keine Repository-Artefakte.
