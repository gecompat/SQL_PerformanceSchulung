# Verbindliche Projektregeln

## Repository-Grenze

- Schreibziel ist ausschließlich `gecompat/SQL_PerformanceSchulung`.
- `gecompat/SQL_Server_Analyze` darf durch Arbeiten an diesem Projekt nicht verändert werden.
- Eine lesende Nutzung anderer Quellen ist nur zur fachlichen oder lizenzbezogenen Referenz zulässig.

## Datenschutz

- Repository-Inhalte verwenden ausschließlich synthetische Labordaten.
- Keine realen Personen-, Kunden-, Firmen-, Organisations-, Umgebungs- oder proprietären Informationen.
- Keine Firmeninformationen, Logos, Kontaktdaten oder internen Systembezeichnungen in Präsentationen.
- Office-Metadaten, Bilder, Screenshots, Logs und Diagnoseausgaben sind vor jeder Übernahme ausdrücklich zu prüfen.
- Bei Unsicherheit ist die Dateierstellung oder Git-Operation anzuhalten und eine ausdrückliche Freigabe einzuholen.
- Die genehmigte Urheberangabe in `LICENCE.md` ist die einzige derzeit freigegebene reale Personenangabe.

## Fachliche Qualität

- Technische Aussagen gegen aktuelle Primärquellen prüfen.
- Version, Compatibility Level und Edition nicht vermischen.
- Dokumentierte Fakten, empirische Beobachtungen und Vermutungen klar unterscheiden.
- Keine pauschalen Tuning-Regeln ohne Voraussetzungen, Messmethode und Trade-offs.
- Veraltete Aussagen korrigieren, nicht aus Kompatibilitätsgründen konservieren.

## Umsetzung

- T-SQL bevorzugen.
- Infrastruktur nur verwenden, wenn der Effekt mit T-SQL allein nicht glaubwürdig demonstrierbar ist.
- Demos idempotent und wiederholbar aufbauen.
- Setup und Cleanup voneinander trennen.
- Globale Cache-, Konfigurations- und Neustart-Eingriffe ausschließlich in isolierten Laborinstanzen.
- Keine produktiven Zugangsdaten oder Secrets im Repository.

## Validierung

- Statische Sicherheits- und Datenschutzprüfung.
- Syntax- und Vertragsprüfung.
- Laufzeittest auf den unterstützten SQL-Server-Versionen, soweit die Demo dort verfügbar ist.
- Erwartete Resultate und tolerierte Abweichungen dokumentieren.
