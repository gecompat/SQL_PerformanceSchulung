# AI-Projektsteuerung

Der kanonische Repository-Einstieg ist [`../AGENTS.md`](../AGENTS.md). Dort wird zuerst die
gemeinsame Foundation-Basis und anschließend diese projektspezifische Steuerung erschlossen.

Dieser Ordner enthält den verbindlichen, maschinenlesbaren Arbeitskontext für AI-gestützte Änderungen. Vor einer Änderung sind die Dateien in folgender Reihenfolge zu lesen:

1. `PROJECT_CONTEXT.md`
2. `PROJECT_RULES.md`
3. `IDENTIFIER_REGISTRATION.md`
4. `DECISIONS.md`
5. `DEMO_CONTRACT.md`
6. `ROADMAP.md`
7. [`../Documentation/Project_Planning/MASTER_IMPLEMENTATION_PLAN.md`](../Documentation/Project_Planning/MASTER_IMPLEMENTATION_PLAN.md)
8. `BACKLOG.md`

## Geltungsbereich

Diese Dateien steuern ausschließlich das Repository `gecompat/SQL_PerformanceSchulung`. Sie ersetzen keine fachliche Quellenprüfung und keine Ausführungstests.

## Pflege

- Neue verbindliche Entscheidungen mit Datum und stabiler ID in `DECISIONS.md` ergänzen.
- Neue Task-, Entscheidungs- und Demo-/Arbeitspaket-Kennungen nur gemäß `IDENTIFIER_REGISTRATION.md` registrieren; vorhandene Kennungen nicht nachträglich umdeuten oder umnummerieren.
- Den Backlog nicht als Erledigt markieren, solange keine überprüfbare Evidenz vorliegt.
- Den Master-Umsetzungsplan aktualisieren, wenn sich Arbeitspakete, Abhängigkeiten, Gates, Demo-Bestand oder Wiederaufnahmeverfahren ändern.
- Änderungen an Projektzielen, Versionen oder Sicherheitsregeln gleichzeitig in allen betroffenen Steuerungsdateien nachziehen.
- Freitext sachlich, präzise und vollständig formulieren; weder ausschmückend noch stichwortartig.
