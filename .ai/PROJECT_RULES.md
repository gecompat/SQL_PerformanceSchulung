# Verbindliche Projektregeln

## Repository-Grenze

- Schreibziel ist ausschließlich `gecompat/SQL_PerformanceSchulung`.
- Andere Repositories dürfen durch Arbeiten an diesem Projekt nicht verändert werden.
- Eine lesende Nutzung anderer Quellen ist nur zur fachlichen oder lizenzbezogenen Referenz zulässig.

## AI Repository Foundation

- Der kanonische Einstieg für KI-gestützte Arbeit ist [`../AGENTS.md`](../AGENTS.md).
- Die unter `.ai/foundation/` versionierte Foundation `1.21.0` bildet eine gemeinsame Mindestbasis. Ihre `REQUIRED`-Regeln dürfen nicht abgeschwächt werden; bewusst strengere Projektregeln bleiben zulässig und maßgeblich.
- Die historischen Bewertungen bis `1.8.0` stehen in [`FOUNDATION_UPGRADE_1_7_0_ASSESSMENT.json`](FOUNDATION_UPGRADE_1_7_0_ASSESSMENT.json) und [`FOUNDATION_UPGRADE_1_8_0_ASSESSMENT.json`](FOUNDATION_UPGRADE_1_8_0_ASSESSMENT.json); das vollständige Delta von `1.8.0` auf `1.17.1` steht in [`FOUNDATION_UPGRADE_1_17_1_ASSESSMENT.json`](FOUNDATION_UPGRADE_1_17_1_ASSESSMENT.json). `DEC-062` aktiviert weiterhin die zentrale Registry im Profil `foundation-artifact-registry/v2` und die Capability `artifact-registry-github` als projektführende Registrierungsautorität. `DEC-064` aktiviert zusätzlich die Capability `rule-context-cache` mit dem lokalen, unversionierten Record-Pfad `Runtime/.foundation-rule-cache/`; native Instruction Discovery und der vollständige relevante Scope bei `CACHE_MISS` bleiben verpflichtend. Die vollständige Capability-Auswahl ist in `DEC-065` dokumentiert; sie installiert ausschließlich lokale Referenzimplementierungen und ersetzt keine projektbezogene Autorisierung für Runtime-, Provider-, Credential-, Netzwerk- oder externe Effektentscheidungen.
- Der scopebezogene Einstieg aus [`README.md`](README.md) ist gemäß `DEC-070` verbindlich. Zusätzliche Entscheidungen, Verträge, Planungsabschnitte und Abhängigkeiten werden nur bei Betroffenheit gelesen; Auffindbarkeit bedeutet keine Komplettlektüre. Registry-/Identitätsregeln gelten bei entsprechenden Änderungen.
- Datenschutz und Neutralisierung sind gegenüber der Foundation `PROJECT_STRONGER`. Sprache, Git-Workflow und KI-Commit-Kennzeichnung sind `PROJECT_SELECTABLE_OVERRIDE`. Die detaillierten Modell-, Validierungs- und SQL-Server-Regeln gelten `COMPLEMENTARY` zur Foundation.
- Für KI-gestützte Git-Änderungen gilt `branch_and_pr`: `main` bleibt stabil; Änderungen erfolgen auf einem thematisch kleinen Branch und werden vor dem Merge relevant validiert.
- Nach jedem erfolgreichen Pull-Request-Merge wird gemäß `DEC-066` das lokale `main` mit `origin/main` synchronisiert und der zugehörige lokale Arbeitsbranch entfernt. Vor dem Löschen sind der Merge und die vollständige Übernahme der lokalen Änderungen zu prüfen, auch bei Squash-Merges. Branches mit nicht übernommenen Änderungen oder Belegung durch einen anderen Worktree bleiben erhalten; die Abschlussmeldung nennt den bereinigten Zustand oder den konkreten Hinderungsgrund.
- `DEC-069` ergänzt den Abschluss: Begonnene, nicht ausdrücklich zurückgestellte oder ausgeschlossene Arbeit wird bis zur relevanten Validierung und Integration in `origin/main` verfolgt. Nach bestätigter vollständiger Übernahme gehört auch die Entfernung des zugehörigen Remote-Branches zum Abschluss. Ein offener PR oder Branch ist kein erledigter Task. Eine sachlich verworfene Arbeit erhält einen begründeten Abschluss; fehlgeschlagene Prüfungen werden nicht umgangen. Ausdrücklich zurückgestellte oder blockierte Arbeit wird im kanonischen Ausführungsstand mit Grund, verbleibendem Gate, Wiederaufnahmebedingung und konkretem PR-/Branch-Verweis geführt. Ein isoliert validierbarer Diagnoseschnitt wird nicht allein an den Abschluss einer größeren Folgeimplementierung gekoppelt; die Validierungs- und Methodengates des jeweiligen Claims bleiben maßgeblich.
- `DEC-063` und [`REPOSITORY_CONTINUITY.md`](REPOSITORY_CONTINUITY.md) wählen geschichtete GitHub-Rulesets: nicht umgehbare Core-Safety-Regeln und separate CI-Gates. Der CI-Bypass ist ausschließlich `gecompat`, nur über Pull Requests und nur für belegtes `INFRASTRUCTURE_UNAVAILABLE` zulässig; `VALIDATION_FAILURE` und `UNKNOWN` dürfen nicht umgangen werden.
- Tool-spezifische Adapter dienen ausschließlich der Auffindbarkeit von `AGENTS.md` und enthalten keine parallelen Projektregeln.
- `DEC-070` dokumentiert das Upgrade auf `1.20.0`, alle 21 Delta-Features und die ausdrücklich autorisierte Prozesskorrektur in [`FOUNDATION_UPGRADE_1_20_0_ASSESSMENT.json`](FOUNDATION_UPGRADE_1_20_0_ASSESSMENT.json) und [`FOUNDATION_UPGRADE_1_20_0_REVIEW.md`](FOUNDATION_UPGRADE_1_20_0_REVIEW.md). Geprüfte Sessionwiederverwendung folgt `foundation/PROCESSING_EFFICIENCY_POLICY.md` ohne Pflicht zu persistenten Records. Der strengere persistente Cachevertrag bleibt bei dessen Nutzung unverändert; ein Miss verlangt den vollständigen relevanten Scope statt sämtlicher Planung.
- `DEC-071` dokumentiert Foundation `1.21.0` und das vollständige sieben Features umfassende Delta in [`FOUNDATION_UPGRADE_1_21_0_ASSESSMENT.json`](FOUNDATION_UPGRADE_1_21_0_ASSESSMENT.json) und [`FOUNDATION_UPGRADE_1_21_0_REVIEW.md`](FOUNDATION_UPGRADE_1_21_0_REVIEW.md). Das erforderliche Aufwandassessment bewertet tatsächliche Test-, Log-, Review- und Modellwege; die korrigierte CI-Auswahl erhält aktuelle Pflichtnachweise und fachliche Qualifikationsgates.
- `DEC-067` dokumentiert das Upgrade von `1.17.2` auf `1.19.0`. Das vollständige Delta und die Integrationsprüfung stehen in [`FOUNDATION_UPGRADE_1_19_0_ASSESSMENT.json`](FOUNDATION_UPGRADE_1_19_0_ASSESSMENT.json) und [`FOUNDATION_UPGRADE_1_19_0_REVIEW.md`](FOUNDATION_UPGRADE_1_19_0_REVIEW.md). Die CI-Strategie wird in [`REPOSITORY_CONTINUITY.md`](REPOSITORY_CONTINUITY.md) konkretisiert; laufende SQL-Container-Validierungen bleiben erhalten.
- Die Session-Verträge `foundation-session-lifecycle/v1` und `foundation-session-handoff/v1` sowie der bereits gewählte lokale `ai-work`-Planner sind verfügbar. Projektschwellen, die Persistenz von Session-/Checkpoint-/Handoff-Runtime-Zustand und automatische Nachfolgesitzungen sind nicht aktiviert. Die Beispielwerte sind keine Projektvorgabe. Fehlende Kontextmetriken bleiben unbekannt; ohne vertrauenswürdige aktuelle Client-Evidenz gilt `successor_session_capability: UNKNOWN` mit manueller Fortsetzung bei einem tatsächlichen Rotationstrigger.
- Eine ausgelöste Fortsetzung übernimmt nur das Delta seit dem letzten erfolgreichen Checkpoint und Verweise auf maßgebliche Repository-Artefakte. Sie führt native Instruction Discovery und den aktuellen Projekt-Bootstrap erneut aus. Laufende semantische Chat-Analyse zur Rotationsentscheidung, Zusammenfassungsketten und die Übernahme nicht verfügbarer Regelanalysen sind unzulässig. Das Upgrade begründet keine Autorisierung zur Erstellung zusätzlicher Chats.

## Stabile Kennungen und Wellenplanung

- [`IDENTIFIER_REGISTRATION.md`](IDENTIFIER_REGISTRATION.md) ist die verbindliche, projektweite Registrierungsautorität für neue Tasks, Entscheidungen und Demo-/Arbeitspaket-Kennungen ihres Geltungsbereichs. Chat-Verlauf und implizite Nummernsuche sind keine Registrierungsautorität.
- Bestehende Kennungen bleiben unverändert (`PRESERVE`). Insbesondere werden historische Wellenkennungen wie `W0-001` und `W2-007` weder umnummeriert noch aus ihrer bisherigen Dokumentation entfernt.
- Neue allgemeine Tasks erhalten eine stabile `TSK-###`-Kennung. Die Welle ist eine veränderbare Planungsmetadatenangabe und wird nicht mehr in neue Task-Kennungen codiert.
- Neue Kennungen werden ausschließlich als vollständige Datensätze in `.ai/identity/registry.json` registriert. Die nächste Nummer wird mit dem versionierten v2-Semantiktool aus den vorhandenen Datensätzen und bekannten Pull-Request-Reservierungen abgeleitet; ein persistierter Zähler oder `registry_revision` ist unzulässig. Kollidierende parallele Änderungen werden durch den GitHub-Preflight und den objektbezogenen Drei-Wege-Merge blockiert und gegen den aktuellen `main`-Stand neu aufgelöst.
- Das bestehende Quellenregister bleibt für Quellenkennungen außerhalb dieses Geltungsbereichs maßgeblich.

## Datenschutz und Neutralisierung

- Repository-Inhalte verwenden ausschließlich synthetische Labordaten.
- Keine realen Personen-, Kunden-, Firmen-, Organisations-, Umgebungs- oder proprietären Informationen, sofern sie nicht ausdrücklich freigegeben sind.
- `Gerhard Pisch` ist als Namensangabe freigegeben.
- Der unverändert erforderliche MIT-Herkunftsnachweis der Foundation ist ausschließlich in `.ai/foundation/AI_REPOSITORY_FOUNDATION_NOTICE.md` freigegeben. Diese pfad- und inhaltsgebundene Ausnahme erweitert keine allgemeine Namens- oder Echtdatenfreigabe.
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
- Laufzeittest auf den unterstützten SQL-Server-Versionen, soweit die Demo dort verfügbar ist und ausführbares Verhalten, Mess-/Ergebnisvertrag, Runtime-Werkzeug oder dessen relevante Abhängigkeit betroffen ist. Eine reine Dokumentations-, Governance- oder statische Prüfänderung löst für sich allein keine SQL-Matrix aus; unbekannte Wirkung wird konservativ als betroffen behandelt.
- Erwartete Resultate und tolerierte Abweichungen dokumentieren.
- Foundation-Prüfungen belegen ausschließlich `FOUNDATION_INTEGRITY`. Projektspezifische Regeln und Dokumentationsverträge bleiben `PROJECT_SEMANTIC`; Builds, SQL-Server-Läufe und empirische Prüfungen bleiben `RUNTIME_EMPIRICAL`.
- Ein grüner Foundation-Validator ersetzt keine betroffenen Projektvalidatoren und ist kein Nachweis für eine vollständig validierte Änderung.
- Diagnose und begrenzte Entwicklung dürfen mit einem betroffenen Scope beginnen und beanspruchen damit keine Versions- oder Modulabnahme. Die bestehende DGN-007-Qualifikation mit zwei Lifecycles je Scope und unterstützter Version, ihren Oracles und unabhängigen Cleanup-Prüfungen bleibt für den entsprechenden finalen Claim verbindlich. Fehlgeschlagene aktuelle Evidenz wird nicht durch einen früheren PASS ersetzt.
- Der vollständige Repository-Privacy-Scan wird zentral für jeden Pull Request und Push nach `main` ausgeführt. Fachworkflows prüfen ihre eigenen Verträge; ein identischer Vollscan am selben Commit wird dort nicht nochmals ausgeführt. Die Prüfung aller geänderten Dateien vor jedem Commit gemäß `CONTRIBUTING.md` bleibt bestehen. Scanner-Selbsttests werden bei Änderungen am Scanner, seinen Tests oder seinem Workflow ausgeführt.

## Kosten- und qualitätsoptimierte Verarbeitung

Diese Regeln gelten anbieterneutral. Maßgeblich sind Gesamtkosten bis zum
verlässlich geprüften Ergebnis: Modell-/Tokenkosten, Kontextübertragung,
Rechenzeit, Werkzeuge, Versuche, Validierung, Koordination und menschliche
Nacharbeit. Verfügbarkeit, Preise und Kontingente dürfen nicht erfunden werden.

- Vor umfangreicher Arbeit vorhandene Werkzeuge, Testumgebung und tatsächlich
  nutzbare Modell-/Reasoningfunktionen mit geringem Aufwand feststellen.
  Deterministische lokale Verarbeitung (`LOCAL`) hat Vorrang, wenn sie genügt.
- Für klar begrenzte prüfbare Schritte gilt `ECONOMICAL`, für zusammenwirkende
  Quellen/Verträge `BALANCED`, für ungelöste kritische Entscheidungen `FRONTIER`.
  Eine geregelte Routine wird nicht allein durch ihr Fachgebiet teuer.
- Mit der niedrigsten plausibel ausreichenden Konfiguration beginnen; nur bei
  verbleibender Unsicherheit, konkretem Fehler, höherem Risiko oder fehlender
  Fähigkeit eskalieren und danach zurückkehren. Ohne Modellwechsel mit dem
  verfügbaren System weiterarbeiten; keinen Wechsel behaupten.
- Nur sinnvoll prüfbare Schritte trennen. Ein Verantwortlicher führt den Scope;
  zusätzliche Agenten oder Reviews brauchen einen belegbaren Nutzen, ein
  konkretes offenes Risiko und eigene Abnahmekriterien. Erforderliche
  unabhängige Reviews bleiben erhalten. Keine automatischen Reviewketten.
- Vor längerer autonomer Arbeit einen endlichen Gesamtumfang, Checkpoint,
  Abbruchbedingung und Verbrauchsquelle festlegen, einschließlich Unteragenten,
  Wiederholungen und Koordination. Fehlende Messung bleibt unbekannt; alternativ
  einen endlichen Aufgaben-/Agentenumfang wählen. Bei ausgeschöpftem Umfang
  keine neue Arbeit beginnen; erforderlichen sicheren Cleanup abschließen.
- Scopebezogene Quellen und tatsächlich verfügbare Analysen nach aktueller
  Inhalts-/Autoritäts-/Abhängigkeitsprüfung wiederverwenden. Bei Übergaben nur
  Ziel, bestätigte Fakten, Änderungen, Evidenz, offene Punkte und Gates übertragen.
- Zuerst kleinste relevante Tests, dann erforderliche statische Prüfungen und
  betroffene Integration/Runtime. Vollständige Suiten nur bei betroffenem Gate
  oder begründetem Risiko. Unveränderte erfolgreiche Checks nicht wiederholen.
- CI-Diagnosen zuerst lokal deterministisch auf Status, betroffenen Vertrag,
  fehlgeschlagene Phase und kleine redigierte Fundstellen verdichten. Den
  vollständigen ursprünglichen Lauf als verlinkte Evidenz erhalten; Voll-Logs
  nur bei einer konkret offenen Ursache in den Modellkontext übernehmen.
- Vorhandene synthetische Fixtures und lokale Werkzeuge bevorzugen. Neue
  Abhängigkeiten, Dienste, externe Effekte oder Kosten nur im Autorisierungsrahmen
  des Auftrags; reale Produktionsdaten und Secrets bleiben ausgeschlossen.
- Gleichartige sichere Operationen bündeln; nur unabhängige Arbeit parallelisieren.
  Retry braucht geänderte Eingaben, Umgebung oder neue Evidenz. Kein unveränderter
  Wiederholungsversuch bis zufällig grün. Bei unverändertem Blocker begrenzte
  Zustandsprüfung mit Backoff statt erneuter semantischer Analyse.
- Tatsächliche Testergebnisse, nicht ausgeführte Prüfungen, Gründe, Restrisiko und
  konkrete Wiederaufnahmebedingungen berichten. Interne Modellwahl nur bei
  relevanter Einschränkung, Kostenentscheidung oder ausdrücklicher Nachfrage
  erläutern. Keine erforderliche Sicherheits- oder Validierungsprüfung einsparen.
