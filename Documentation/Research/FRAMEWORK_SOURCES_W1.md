# Primärquellen für die Welle-1-Framework-Basis

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-07-24 |
| Arbeitspakete | `FWK-003`, `FWK-004`, `FWK-005`, `FWK-011` |
| Geltungsbereich | SQL Server 2019, 2022 und 2025 sowie plattformneutrale Ergebnisnormalisierung |

## Quellen

| ID | Primärquelle | Aussagebezug | Gültigkeitsgrenze |
|---|---|---|---|
| `FWKSRC-001` | [Statistics](https://learn.microsoft.com/en-us/sql/relational-databases/statistics/statistics?view=sql-server-ver17) | Histogramm, Density, Sampling und Statistikinterpretation in `FWK-005` | SQL Server 2019–2025; CE- und Compatibility-Level-Kontext beachten |
| `FWKSRC-002` | [sys.dm_db_stats_properties](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-db-stats-properties-transact-sql?view=sql-server-ver17) | `last_updated`, Zeilen, Stichprobenzeilen, Schritte und Änderungszähler | leeres Ergebnis nicht als Nullstatistik interpretieren; Metadatensichtbarkeit beachten |
| `FWKSRC-003` | [sys.dm_db_stats_histogram](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-db-stats-histogram-transact-sql?view=sql-server-ver17) | Histogrammschritte in `FWK-005` | Histogramm bezieht sich auf die führende Statistikspalte |
| `FWKSRC-004` | [SET STATISTICS XML](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-statistics-xml-transact-sql?view=sql-server-ver17) | interaktive Actual-Showplan-XML-Ausgabe der Referenzabfrage | `SHOWPLAN` auf allen referenzierten Datenbanken erforderlich; keine automatische Persistierung |
| `FWKSRC-005` | [sys.dm_exec_sessions](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-sessions-transact-sql?view=sql-server-ver17) | sessionbezogene CPU-, Read-, Logical-Read- und Write-Zähler in `FWK-004` | kumulative Sessionzähler; geringer Messoverhead ist enthalten |
| `FWKSRC-006` | [sys.dm_exec_session_wait_stats](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-session-wait-stats-transact-sql?view=sql-server-ver17) | optionale sessionbezogene Wait-Deltas in `FWK-004` | Berechtigungsbezeichnung ist versionsabhängig; fehlende optionale Sichtbarkeit ergibt `WARN` |
| `FWKSRC-007` | [Query processing architecture guide](https://learn.microsoft.com/en-us/sql/relational-databases/query-processing-architecture-guide?view=sql-server-ver17) | Abgrenzung von Plan, Optimierung, Ausführung und Runtime-Evidenz | Plan- und Laufzeitbeobachtung sind keine alleinige Ursachenbestätigung |

## Evidenzgrenze

Die Quellen dokumentieren Produkteigenschaften und Messschnittstellen. Generatorverteilungen, konkrete Performancewirkungen und zulässige Bandbreiten bleiben empirische Eigenschaften der jeweiligen synthetischen Demo. `FWK-011` bewertet deshalb primär Invarianten, Richtungen und Verhältnisse statt universeller Laufzeitgrenzen.

## Abnahme

Die neuen Framework-Komponenten sind den verwendeten Herstellerquellen zugeordnet. Eine Runtime-Validierung der Referenzskripte auf SQL Server 2019, 2022 und 2025 ist nicht Bestandteil dieses Quellenreviews und bleibt als separates Arbeitspaket offen.
