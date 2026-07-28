# Verbindliche Projektregeln

## Repository-Grenze

- Schreibziel ist ausschließlich `gecompat/SQL_PerformanceSchulung`.
- Andere Repositories dürfen durch Arbeiten an diesem Projekt nicht verändert werden.
- Eine lesende Nutzung anderer Quellen ist nur zur fachlichen oder lizenzbezogenen Referenz zulässig.

## Datenschutz und Neutralisierung

- Repository-Inhalte verwenden ausschließlich synthetische Labordaten.
- Keine realen Personen-, Kunden-, Firmen-, Organisations-, Umgebungs- oder proprietären Informationen, sofern sie nicht ausdrücklich freigegeben sind.
- `Gerhard Pisch` ist als Namensangabe freigegeben.
- Das vom Auftraggeber bezeichnete Firmenlogo sowie die dazugehörigen Firmen- und Markenkennzeichen sind aus allen Repository-Artefakten zu entfernen.
- Weitere Firmeninformationen, Logos, Kontaktdaten oder interne Systembezeichnungen dürfen in Präsentationen und Begleitmaterialien nicht enthalten sein.
- Office-Metadaten, Bilder, Screenshots, Logs und Diagnoseausgaben sind vor jeder Übernahme ausdrücklich zu prüfen.
- Bildbasierte Logos und Markenkennzeichen sind zusätzlich visuell zu prüfen; eine reine Textsuche ist nicht ausreichend.
- Bei Unsicherheit ist die Dateierstellung oder Git-Operation anzuhalten und eine ausdrückliche Freigabe einzuholen.

## Fachliche Qualität

- Technische Aussagen gegen aktuelle Primärquellen prüfen.
- Version, Compatibility Level und Edition nicht vermischen.
- Dokumentierte Fakten, empirische Beobachtungen und Vermutungen klar unterscheiden.
- Keine pauschalen Tuning-Regeln ohne Voraussetzungen, Messmethode und Trade-offs.
- Veraltete Aussagen korrigieren, nicht aus Kompatibilitätsgründen konservieren.

## Sprachstil und Übersetzungen

- Verbindlich gelten [`Documentation/Standards/LANGUAGE_AND_TRANSLATION_RULES.md`](../Documentation/Standards/LANGUAGE_AND_TRANSLATION_RULES.md) und der fachlich spezifischere [`Documentation/Standards/TERMINOLOGY_AND_STYLE_STANDARD.md`](../Documentation/Standards/TERMINOLOGY_AND_STYLE_STANDARD.md).
- Projekt- und Dokumentationssprache ist grundsätzlich Deutsch; ein Dokument verwendet nur eine Hauptsprache.
- Technische Fachbegriffe, Produktnamen, Programmiersprachen, SQL-Befehle, API-Namen, Dateinamen, Parameter sowie Klassen-, Methoden- und Funktionsnamen werden nicht übersetzt.
- Etablierte englische IT-Begriffe bleiben erhalten, wenn eine Übersetzung ungebräuchlich, künstlich oder missverständlich wäre. Insbesondere werden `Pull Request`, `Repository`, `Branch`, `Commit`, `Workflow`, `Provider`, `Runtime`, `Setup` und `Cleanup` konsistent verwendet.
- Texte sind sachlich, eindeutig, technisch präzise, gut lesbar und möglichst zeitlos. Marketing-Sprache, unnötige Füllwörter, emotionale Formulierungen, Spekulationen und unbegründete Wertungen sind unzulässig.
- Nach Möglichkeit aktiv formulieren, sofern dadurch Verantwortlichkeit und Ablauf klarer werden.
- Keine neuen Fachbegriffe erfinden. Ohne etablierte Übersetzung bleibt der Originalbegriff erhalten.
- Code, Befehle, Konfigurationswerte und Beispiele müssen der tatsächlichen Implementierung exakt entsprechen und dürfen nicht sinngemäß übersetzt werden.
- Vorhandene Dokumentation nicht allein zur sprachlichen Vereinheitlichung übersetzen. Übersetzungen erfolgen nur auf ausdrücklichen Auftrag, zur nachweisbaren Konsistenzverbesserung oder bei offiziell gepflegten Sprachversionen.
- Gleiche Konzepte werden projektweit gleich bezeichnet. Wechselnde Paare wie `Provider`/„Anbieter“, `Branch`/„Zweig“ oder `Commit`/„Einspielung“ sind zu vermeiden.
- KI-gestützte Änderungen passen sich automatisch an Sprache, Terminologie und Stil der betroffenen hochwertigen Projektdokumentation an. Bestehende spezifische Regeln haben Vorrang.

## Umsetzung

- T-SQL bevorzugen.
- Infrastruktur nur verwenden, wenn der Effekt mit T-SQL allein nicht glaubwürdig demonstrierbar ist.
- Demos idempotent und wiederholbar aufbauen.
- Setup und Cleanup voneinander trennen.
- Globale Cache-, Konfigurations- und Neustart-Eingriffe ausschließlich in isolierten Laborinstanzen.
- Keine produktiven Zugangsdaten oder Secrets im Repository.

## KI-generierte Commit Messages

- Jede vollständig oder überwiegend von einer KI erstellte Commit Message beginnt mit dem Namen der tatsächlich verwendeten KI und einem Doppelpunkt, beispielsweise `ChatGPT:`, `Codex:`, `Gemini:`, `Claude:` oder `Genie:`.
- Das KI-Präfix kennzeichnet ausschließlich den Ursprung der Commit Message. Es ersetzt keine bestehenden Anforderungen an Kürze, Eindeutigkeit, fachliche Korrektheit oder gegebenenfalls Conventional Commits.
- Führt die KI den Commit direkt aus, ist keine zusätzliche kopierbare Commit Message auszugeben.
- Ohne direkten Repositoryzugriff muss die KI neben ZIP, Patch, Download oder Dateiliste eine separat kopierbare, einzeilige Commit Message bereitstellen.
- Menschlich erstellte Commits benötigen kein KI-Präfix.
- Die Regel gilt für automatisierte Commits auf allen Versionsverwaltungs- und Hostingplattformen, insbesondere GitHub, GitLab und Azure DevOps.

## Validierung

- Statische Sicherheits- und Datenschutzprüfung.
- Syntax- und Vertragsprüfung.
- Laufzeittest auf den unterstützten SQL-Server-Versionen, soweit die Demo dort verfügbar ist.
- Erwartete Resultate und tolerierte Abweichungen dokumentieren.
