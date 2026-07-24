# Tests

## Aktive statische Prüfungen

`Tests/Static/validate_framework_contracts.py` prüft die Sicherheits- und Vertragsbasis aus `FWK-001`, `FWK-002`, `FWK-008`, `FWK-009` und `FWK-012`. Der Test verwendet ausschließlich die Python-Standardbibliothek und kontrolliert Pflichtdateien, Outcomes, Statuscodes, Eigentumsmarker, README-Abschnitte und unzulässige Hochrisikomuster.

Der Workflow `.github/workflows/framework-contracts.yml` ist auf Framework-, Demo-Vertrags- und Validatorpfade begrenzt. Änderungen an fachfremder Dokumentation lösen diesen Check nicht aus.

Lokaler Aufruf:

```bash
python Tests/Static/validate_framework_contracts.py
```

## Geplante Prüfbereiche

- statische Struktur- und Vertragsprüfung,
- Privacy- und Metadatenprüfung,
- T-SQL-Syntax- und Installationsprüfung,
- Laufzeittests für SQL Server 2019, 2022 und 2025,
- versions- und featureabhängige Skip-Regeln,
- erwartete Resultsets und zulässige Messbereiche,
- idempotentes Setup und vollständiges Cleanup,
- deterministische Multi-Session-Steuerung.

Tests dürfen keine realen Zugangsdaten oder Umgebungsinformationen ausgeben oder persistieren. Interaktiv notwendige reale Resultsets werden nicht als Testartefakt gespeichert.
