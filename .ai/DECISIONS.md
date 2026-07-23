# Entscheidungen

| ID | Datum | Entscheidung | Begründung |
|---|---|---|---|
| DEC-001 | 2026-07-23 | Dieses Projekt schreibt ausschließlich in `gecompat/SQL_PerformanceSchulung`. | Klare Trennung vom SQL-Server-Analyseframework. |
| DEC-002 | 2026-07-23 | T-SQL ist das bevorzugte Demonstrationsmittel. | Direkte Nachvollziehbarkeit und geringe Einstiegshürde. |
| DEC-003 | 2026-07-23 | SQL Server 2025 ist primäre Zielplattform; 2019 und 2022 bilden die Kompatibilitätsmatrix. | Aktuelle Features zeigen, ohne ältere unterstützte Versionen zu ignorieren. |
| DEC-004 | 2026-07-23 | Alle veröffentlichten Beispieldaten und Bezeichnungen sind synthetisch. | Datenschutz und Wiederverwendbarkeit. |
| DEC-005 | 2026-07-23 | Präsentationen enthalten keine Firmeninformationen, Logos, Kontaktdaten oder internen Bezeichnungen. | Firmenneutrale Schulungsartefakte. |
| DEC-006 | 2026-07-23 | Jede Demo folgt einem einheitlichen Vertrag aus Ziel, Preflight, Setup, Baseline, Problem, Evidenz, Gegenmaßnahme, Vergleich und Cleanup. | Reproduzierbarkeit und didaktische Vergleichbarkeit. |
| DEC-007 | 2026-07-23 | Demos erhalten die Sicherheitsstufen Grün, Gelb oder Rot. | Klare Abgrenzung produktionsnaher Diagnose von belastenden oder destruktiven Laboroperationen. |
| DEC-008 | 2026-07-23 | Die Lizenz wird analog zum Referenzprojekt auf Software, Schulungsunterlagen, Präsentationen und Demo-Skripte erweitert. | Einheitlicher Nutzungs- und Weitergabevertrag für alle Artefaktarten. |
| DEC-009 | 2026-07-23 | Schulungsthemen werden zuerst fachlich aufbereitet und möglichst mit T-SQL in isolierten synthetischen Testdatenbanken demonstriert. Zusätzliche Infrastruktur wird erst eingesetzt, wenn der Effekt mit T-SQL allein nicht glaubwürdig reproduzierbar ist. | Das Projekt ist eine Performance-Schulung und kein Infrastruktur- oder Analyseframework-Lab. |
| DEC-010 | 2026-07-23 | Ein kompaktes Testumgebungs-How-to wird als unterstützender Einstieg für Personen ohne verfügbaren SQL Server vorgesehen. | Die Beispiele sollen reproduzierbar bleiben, ohne den Labaufbau zum eigentlichen Projektziel zu machen. |

Neue Entscheidungen werden fortlaufend ergänzt. Bestehende Einträge werden nicht stillschweigend umgedeutet; fachlich überholte Entscheidungen erhalten einen expliziten Nachfolgeeintrag.
