# Mitwirken

## Inhaltlicher Maßstab

Beiträge müssen eine fachlich belastbare, reproduzierbare und versionsbewusste SQL-Server-Schulung unterstützen. Pauschale Performance-Regeln ohne dokumentierte Voraussetzungen oder Messung sind nicht zulässig.

## Datenschutz und Vertraulichkeit

Vor jedem Commit sind alle geänderten Dateien auf reale personen-, kunden-, firmen-, organisations-, umgebungsbezogene und proprietäre Informationen zu prüfen.

- Nur synthetische Labordaten und neutrale Bezeichnungen verwenden.
- Keine Logos, Kontaktdaten, internen Server-, Instanz-, Datenbank-, Schema- oder Projektnamen übernehmen.
- Screenshots und Office-Metadaten vor einer Übernahme vollständig prüfen und bereinigen.
- Diagnosedaten aus realen Systemen nicht in das Repository übernehmen.
- Die ausdrücklich lizenzierten Urheberhinweise in `LICENCE.md` und `.ai/foundation/AI_REPOSITORY_FOUNDATION_NOTICE.md` sind ausschließlich an diesen Pfaden hiervon ausgenommen.

Ist die Herkunft oder Unbedenklichkeit eines Inhalts nicht eindeutig, darf er nicht committed werden, bevor eine ausdrückliche Freigabe vorliegt.

## Anforderungen an Demos

Jede Demo folgt dem Vertrag in [`.ai/DEMO_CONTRACT.md`](.ai/DEMO_CONTRACT.md). Sie muss insbesondere Version, Compatibility Level, Edition, Rechte, Sicherheitsstufe, erwartete Evidenz und Cleanup dokumentieren.

Globale oder destruktive Befehle sind nur in klar gekennzeichneten, isolierten Laborszenarien zulässig.

## Quellen

Fachliche Aussagen sollen möglichst auf Microsoft Learn, offizielle Produktdokumentation, dokumentierte DMVs oder andere belastbare Primärquellen gestützt werden. Quellen und Abrufdatum gehören in die jeweilige Fach- oder Demo-Dokumentation.

## Sprachstil und Übersetzungen

Für Dokumentation, Kommentare, Commit Messages, Pull Requests, AI-Metadaten und sonstige Projekttexte gelten die verbindlichen [Sprachstil- und Übersetzungsregeln](Documentation/Standards/LANGUAGE_AND_TRANSLATION_RULES.md) sowie der fachlich spezifischere [Terminologie- und Schreibstandard](Documentation/Standards/TERMINOLOGY_AND_STYLE_STANDARD.md).

Projekt- und Dokumentationssprache ist grundsätzlich Deutsch. Ein Dokument verwendet nur eine Hauptsprache. Technische Originalbegriffe, Produktnamen, Codebezeichner, Befehle, Dateinamen und etablierte englische IT-Begriffe werden nicht künstlich übersetzt. Beispiele und Befehle müssen der tatsächlichen Implementierung exakt entsprechen.

Neue Texte sind sachlich, eindeutig, technisch präzise, gut lesbar und möglichst zeitlos zu formulieren. Marketing-Sprache, unnötige Füllwörter, emotionale Formulierungen, Spekulationen und unbegründete Wertungen sind nicht zulässig. Vorhandene Dokumentation wird nicht ohne ausdrücklichen oder fachlich begründeten Anlass übersetzt.

## Änderungen

Änderungen sollen thematisch klein, nachvollziehbar und prüfbar bleiben. Dokumentation, Demo und Test werden gemeinsam aktualisiert, wenn sie denselben Vertrag betreffen.

## KI-generierte Commit Messages

Jede Commit Message, die vollständig oder überwiegend von einer KI erstellt wird, muss mit dem Namen der tatsächlich verwendeten KI und einem Doppelpunkt beginnen. Beispiele sind:

```text
ChatGPT: Add Docker smoke test
Codex: Fix provider detection
Gemini: Update documentation
Claude: Refactor runtime provider
Genie: Improve validation
```

Es ist stets der Name der tatsächlich verwendeten KI anzugeben. Das Präfix kennzeichnet ausschließlich den Ursprung der Commit Message.

Bestehende Anforderungen an Commit Messages bleiben verbindlich. Insbesondere müssen Commit Messages kurz, eindeutig und fachlich korrekt bleiben. Soweit für einen Teil des Projekts Conventional Commits oder andere zusätzliche Konventionen festgelegt sind, ergänzt das KI-Präfix diese Vorgaben und ersetzt sie nicht.

Schreibt die KI den Commit direkt in das Repository, genügt die Commit Message des ausgeführten Commits. Eine zusätzliche kopierbare Ausgabe derselben Commit Message ist nicht erforderlich.

Besitzt die KI keinen direkten Repositoryzugriff und stellt Änderungen stattdessen beispielsweise als ZIP-Datei, Patch, Download oder Dateiliste bereit, muss sie zusätzlich eine separat kopierbare, einzeilige Commit Message ausgeben. Diese Ausgabe dient ausschließlich dazu, die Commit Message unverändert für den manuellen Commit zu übernehmen.

Menschlich erstellte Commit Messages benötigen kein KI-Präfix.

Die Regel gilt für alle automatisiert erstellten Commits unabhängig von der verwendeten Versionsverwaltungs- oder Hostingplattform, insbesondere GitHub, GitLab und Azure DevOps.
