# Tests

## Aktive statische Prüfungen

`Tests/Static/validate_framework_contracts.py` prüft die implementierte Framework-Basis aus `FWK-001` bis `FWK-005`, `FWK-008`, `FWK-009`, `FWK-011` und `FWK-012`. Der Test verwendet ausschließlich die Python-Standardbibliothek und kontrolliert Pflichtdateien, Outcomes, Statuscodes, Eigentumsmarker, README-Abschnitte, Generator-Determinismus, T-SQL-Lexik, Python-Syntax, JSON-Metadaten und unzulässige Hochrisikomuster.

`Tests/Static/test_result_contract_evaluator.py` prüft den `FWK-011`-Evaluator mit positivem und negativem synthetischem Beispiel. Zusätzlich werden nicht endliche JSON-Werte und eine ungültige Nullbasis für Verhältnisassertionen abgewiesen.

Der Workflow `.github/workflows/framework-contracts.yml` ist auf Framework-, Demo-Vertrags- und statische Testpfade begrenzt. Änderungen an fachfremder Dokumentation lösen diesen Check nicht aus.

Lokaler Aufruf:

```bash
python Tests/Static/validate_framework_contracts.py
python Tests/Static/test_result_contract_evaluator.py
```

Beispiel für die Ergebnisprüfung:

```bash
python Demos/00_Framework/Tools/evaluate_result_contract.py \
  Demos/00_Framework/Examples/FWK-011_ResultContract.example.json \
  Demos/00_Framework/Examples/FWK-011_Evidence.pass.example.json
```

## Geplante Prüfbereiche

- T-SQL-Parse-, Installations- und Lifecycle-Test auf SQL Server 2019, 2022 und 2025,
- vollständiger Runtime-Harness aus `FWK-010`,
- deterministische Multi-Session-Steuerung aus `FWK-006`,
- Query-Store- und Extended-Events-Lifecycle aus `FWK-007`,
- Privacy- und Metadatenprüfung,
- versions- und featureabhängige Skip-Regeln,
- idempotentes Setup und vollständiges Cleanup,
- vier Gate-B-Pilotdemos.

Tests dürfen keine realen Zugangsdaten oder Umgebungsinformationen ausgeben oder persistieren. Interaktiv notwendige reale Resultsets werden nicht als Testartefakt gespeichert.
