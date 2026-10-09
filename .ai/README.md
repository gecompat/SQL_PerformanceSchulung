# AI-Projektsteuerung

Der kanonische Repository-Einstieg ist [`../AGENTS.md`](../AGENTS.md). Dort wird zuerst die
gemeinsame Foundation-Basis und anschließend diese projektspezifische Steuerung erschlossen.

Dieser Ordner erschließt die verbindlichen Projektquellen. Gemäß `DEC-070` gilt
ein scopebezogener Einstieg statt einer Pflichtlektüre aller Planungsdateien.
Nach nativer Instruction Discovery und dem kurzen Foundation-Ruleset werden
[`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md), [`PROJECT_RULES.md`](PROJECT_RULES.md)
und für Beiträge [`../CONTRIBUTING.md`](../CONTRIBUTING.md) gelesen. Weitere
Quellen werden anhand der betroffenen Änderung ausgewählt:

| Änderung oder Grenze | Zusätzlich maßgebliche Quellen |
|---|---|
| Aktueller Auftrag, Pause, Blocker oder Wiederaufnahme | [`CURRENT_EXECUTION_STATUS.md`](../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md), betroffener Abschnitt und dort verlinkter konkreter Vertrag/Nachweis |
| SQL-Demo, Messung, Runtime oder Cleanup | [`DEMO_CONTRACT.md`](DEMO_CONTRACT.md), betroffene Demo-/Framework-Verträge, Manifest und relevante Tests |
| Neue oder geänderte Kennung, Registry oder Zuordnung | [`IDENTIFIER_REGISTRATION.md`](IDENTIFIER_REGISTRATION.md), Registry und betroffene Identitäts-/Registrierungsregeln der Foundation |
| Methoden- oder sonstige Projektentscheidung | Betroffene Einträge in [`DECISIONS.md`](DECISIONS.md), ihre Vertragsquellen und das betreffende Entscheidungspaket |
| CI, Merge, Pflichtchecks oder Infrastruktur-Ausfall | [`REPOSITORY_CONTINUITY.md`](REPOSITORY_CONTINUITY.md), betroffene Workflows und Validators |
| Planungsänderung | Betroffene Abschnitte aus [`ROADMAP.md`](ROADMAP.md), [`MASTER_IMPLEMENTATION_PLAN.md`](../Documentation/Project_Planning/MASTER_IMPLEMENTATION_PLAN.md) und [`BACKLOG.md`](BACKLOG.md) samt Abhängigkeiten |
| Dokumentation und Quellen | Die in `CONTRIBUTING.md` verlinkten Sprach-/Terminologiestandards und betroffene fachliche Primärquellen |
| Foundation-Upgrade oder aktive Regeländerung | Manifest, Feature-Katalog, semantisches Upgradeverfahren und betroffene aktive Autoritäten |

Verweise dienen der Auffindbarkeit, nicht als rekursiver Lesebefehl. Registry-
und Identitätsregeln gelten bei entsprechenden Änderungen; sie erzwingen keine
Lektüre sämtlicher Planung. Ein `CACHE_MISS` verlangt den vollständigen Aufbau
des **ausgewählten relevanten Scopes**, nicht die Wiederherstellung der früheren
neun Dokumente umfassenden Pflichtfolge.

## Sessionwiederverwendung und Aufwand

Unveränderte, tatsächlich in der Session vorhandene Regelanalysen dürfen nach
aktueller Prüfung von Autorität, Inhalt, Scope und transitiven Abhängigkeiten
gemäß [`foundation/PROCESSING_EFFICIENCY_POLICY.md`](foundation/PROCESSING_EFFICIENCY_POLICY.md)
wiederverwendet werden. Neue Sessions führen native Discovery erneut aus.
Fehlende Analysen werden gelesen; unbekannte Discovery-Einstellungen werden
einmal benannt und erlauben keinen behaupteten Hit. Eine neue Git-Bindung
erfordert eine aktuelle Prüfung, nicht automatisch erneute semantische Lektüre.

Die gewählte persistente Cache-Capability bleibt verfügbar, ist für normale
Sessionwiederverwendung aber keine Pflicht. Wer Records verwendet, beachtet
zusätzlich unverändert deren strengeren Vertrag. Cache-Records enthalten keine
Regeltexte oder Zusammenfassungen und sind kein Validierungsnachweis.

Ein Implementierungsverantwortlicher führt einen zusammenhängenden Schnitt.
Zusätzliche Reviews benötigen ein konkretes offenes Risiko und Abnahmekriterien;
kein Review eines Reviews allein aufgrund eines abgeschlossenen Reviews.
Erforderliche unabhängige Reviews und fachliche Gates bleiben bestehen.
Vor längerer autonomer Arbeit wird ein endlicher Gesamtumfang einschließlich
Unteragenten, Wiederholungen und Koordination festgelegt. Messwerte, Schätzungen
und unbekannter Verbrauch werden getrennt berichtet. Grüne unveränderte Checks
oder unveränderte Blocker werden ohne neuen Anlass nicht wiederholt.

## Geltungsbereich

Diese Dateien steuern ausschließlich das Repository `gecompat/SQL_PerformanceSchulung`. Sie ersetzen keine fachliche Quellenprüfung und keine Ausführungstests.

## Pflege

- Neue verbindliche Entscheidungen mit Datum und stabiler ID in `DECISIONS.md` ergänzen.
- Neue Task-, Entscheidungs- und Demo-/Arbeitspaket-Kennungen nur gemäß `IDENTIFIER_REGISTRATION.md` registrieren; vorhandene Kennungen nicht nachträglich umdeuten oder umnummerieren.
- Den Backlog nicht als Erledigt markieren, solange keine überprüfbare Evidenz vorliegt.
- Den Master-Umsetzungsplan aktualisieren, wenn sich Arbeitspakete, Abhängigkeiten, Gates, Demo-Bestand oder Wiederaufnahmeverfahren ändern.
- Änderungen an Projektzielen, Versionen oder Sicherheitsregeln gleichzeitig in allen betroffenen Steuerungsdateien nachziehen.
- Freitext sachlich, präzise und vollständig formulieren; weder ausschmückend noch stichwortartig.
