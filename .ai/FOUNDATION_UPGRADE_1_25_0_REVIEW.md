# Foundation 1.25.0: menschliche Lesepfade und getrennte KI-Steuerung

Stand: 22. Oktober 2026. Dieses Dokument bewertet die semantische Übernahme der
Foundation; es ist keine Schulungsanleitung und kein Nachweis vollständiger
Dokumentationskonformität.

## Quelle, Umfang und erhaltene Verträge

Ausgangspunkt ist Foundation 1.24.0 aus
`96391403a1b89e19d4824838806d7190d8033389`. Die aktuelle Quelle ist
[Foundation 1.25.0 am exakten Commit](https://github.com/gecompat/AI_Repository_Foundation/tree/9e1b9974de58ea775d40c7c6045cd5057ba8b30c)
`9e1b9974de58ea775d40c7c6045cd5057ba8b30c`. Die
[vollständige Bewertung](FOUNDATION_UPGRADE_1_25_0_ASSESSMENT.json) erfasst genau
das neue Feature `human-documentation-paths` mit `APPLY_DEFAULT`, also Übernahme
der anwendbaren Vorgabe. Im Versionsintervall gibt es kein weiteres neu
eingeführtes oder materiell geändertes Katalogfeature.

Der vorherige Fehlerbehebungsschnitt ist mit
[PR289](https://github.com/gecompat/SQL_PerformanceSchulung/pull/289) in Main
`b4e18472aeb925c34b2c34671253abce5541157b` abgeschlossen: unabhängige Reviews,
lokale positive und negative Prüfungen, acht grüne Head-, fünf Base- und sechs
frische Main-Prüfungen, vollständige Baumübernahme, Synchronisation und eigene
lokale sowie Remote-Branchbereinigung. Head bezeichnet den geprüften
Pull-Request-Commit, Base dessen Main-Basis. Der alte native Versuchsrahmen
bleibt geschlossen; das Upgrade eröffnet keine weiteren Workerstarts.

Die drei Adapter und zehn Capabilities bleiben ausgewählt. Der
[erneuerte Installationsnachweis](foundation/installation-provenance.json)
erfasst unverändert 114 Ziele mit Quell- und Zielhash. Neun Foundation-Ziele
erhalten neue Basisinhalte; die Root-Bridge wird ausschließlich innerhalb ihrer
Marker aktualisiert. Die projektgeführten Regeln außerhalb dieser Marker und
die bereits geprüfte relative Schemakorrektur im Orchestratorleitfaden bleiben
als begründete Overrides erhalten. Projekt-README, Lizenz, Backlog und Registry
der Foundationquelle werden nicht kopiert. Historische Projektkennungen,
Registry-Einträge, Lizenztexte und private Evidenz bleiben erhalten.

Datenschutz, vertrauenswürdige Schulungsquellen, konkrete Freigaben und frische
Integrationsgates bleiben `PROJECT_STRONGER`, also kompatible strengere
Projektvorgaben. Deutsch als Projektsprache, Verzeichnisnamen und Auswahl der
Capabilities bleiben `PROJECT_SELECTABLE_OVERRIDE`, bewusste Projektwahlen.
Die neue Lesepfadregel ergänzt die bestehenden Sprach- und Kennungsregeln;
gemeinsame fachliche und technische Quellen erhalten keine konkurrierenden
menschlichen und KI-Versionen. Kein ungelöster Required-Konflikt wurde gefunden.
Hosts, Provider, Modelle, Credentials, Automationen und externe Effekte werden
durch die Installation nicht aktiviert.

## Semantische Prüfung der menschlichen Wege

| Weg und Leseraufgabe | Ergebnis und Grenze |
|---|---|
| [Projekt-README](../README.md) → [Dokumentationsübersicht](../Documentation/README.md) → [Demo-Ausführungsleitfaden](../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md) | Zweck, Zielgruppe, Lernwege und Voraussetzungen sind auffindbar. Demo-Kennungen stehen mit Themen und Beschreibungen; die Anleitung führt über Vorbereitung und Ausführung zur Ergebnisdeutung, Abbruchbehandlung und Cleanup. Der aktuelle Entwicklungsschnitt wird nicht auf der Startseite berichtet. Diese Prüfung ist keine erneute SQL-Ausführung. |
| README → [ausdrücklich benannter KI-Einstieg](../AGENTS.md) → [KI-Projektsteuerung](README.md) | Der neue kurze Link macht den gesonderten Einstieg für Menschen sichtbar. Der Router unterscheidet Projektregeln, gemeinsame Verträge und abgeleitete Installationsdaten; er verlangt keine Komplettlektüre. |
| KI-Projektsteuerung → [Provenienznachweis](foundation/installation-provenance.json) → [Schema](foundation/schemas/installation-provenance.schema.json) → [Projektvalidator](../Tests/Static/validate_foundation_integration.py) | Herkunft, Format und Prüfung sind technisch nachvollziehbar. Der Nachweis erzeugt keine eigene Autorität. Integrität und auffindbare Links ersetzen die semantische Lesepfadprüfung nicht. |
| [Dokumentationsübersicht](../Documentation/README.md#projektpflege) → [aktueller Ausführungsstand](../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md) | Projektpflege ist vom Lernweg getrennt. Der aktuelle Abschnitt unterscheidet abgeschlossene Arbeit, laufendes Upgrade und historische Nachweise. Umfangreiche ältere Planung bleibt als abgegrenzte Altbestandsarbeit offen. |

Die Verzeichnisse für Lernen, gemeinsame Architektur/Standards, Planung und
KI-Steuerung werden in den bestehenden Einstiegen erklärt. Eine breite
Dateiverschiebung ist für die geänderten Wege nicht erforderlich. Der
Altbestand wurde nicht vollständig neu gelesen oder pauschal als verständlich
abgenommen. `TSK-015` (Menschliche Lesepfade und historische Planungseinstiege
konsolidieren) steht im [Backlog](BACKLOG.md): konkreter Umfang, zuständige
Dokumentationsrolle und Auslöser der nächsten abgegrenzten Welle sind benannt.
Jede wesentliche Änderung eines betroffenen bestehenden Pfads löst die
zugehörige Prüfung einschließlich notwendiger Folgeseiten zusätzlich aus.

## Erforderliche Bewertung des Verarbeitungsaufwands

CI bedeutet Continuous Integration, die automatisierte Integrationsprüfung.

| Tatsächlicher Weg | Disposition und Schutzgrund |
|---|---|
| Testauswahl und Pflichtgates | Der Foundation- und Regeländerungsdiff benötigt portable Integrität, Projektintegration, Kennungs-/Registry- und relevante Struktur-/Datenschutzprüfungen. SQL-Code, Workerquellen und Provider ändern sich nicht; keine native SQL-/Worker-Matrix wird ausgelöst. Vorhandene CI-Selektoren und Pflichtgates bleiben erhalten. |
| Überlappende Integritätschecks | Der portable Foundation-Validator prüft Transfer/Provenienz; der Projektvalidator prüft zusätzlich die exakte Auswahl, Entscheidungen, historische Verträge und projektgeführte Discovery. Die begrenzte Hashprüfung von 114 Zielen bleibt in beiden bestehenden Wegen erhalten; sie ersetzt keine fachliche Prüfung. |
| Lokale und frische Remote-Prüfungen | Ein lokaler relevanter Lauf pro stabilem Kandidaten und aktuelle Head-/Base-/Main-Gates bleiben wegen des menschlichen Auftrags erforderlich. Bereits grüne unveränderte aufwendige Runnermodelle werden für dieses Upgrade nicht wiederholt. Die vorherige Runner-CI benötigte 8:53 Minuten am Head und 5:18 Minuten auf Main; diese Beobachtung ist keine Token- oder allgemeine Leistungsangabe. |
| Dokumentationskontext | Der tatsächliche Diff, die oben benannten Wege und notwendige Fortsetzungsseiten bilden den Scope. Gleiche autoritative Inhalte werden nur bei vorhandener aktueller Sessionanalyse wiederverwendet; geänderte Abhängigkeiten invalidieren betroffene Analysen. Keine Vollkorpuslektüre und kein neues Dokumentationsregister. |
| Logs, Reviews und Modelle | Ein Implementierungsverantwortlicher und derselbe unabhängige Reviewer beurteilen das konkrete semantische Delta. Bestehende deterministische Validatoren liefern kompakte Ergebnisse; Rohlogs und Laufdaten bleiben lokal. Ein grüner Bericht oder Timer löst keinen zusätzlichen Modellreview aus. |
| Budget, Warten und Fortsetzung | Genau eine kohärente Upgrade-Welle mit Checkpoint am zweiten stabilen Kandidaten beziehungsweise erstem blockierenden Befund und harter Grenze vier Kandidaten einschließlich notwendiger Reviewkorrekturen, Tests und Integration. Keine neue Automation oder zweite Implementierung. Modell-/Koordinationsverbrauch bleibt UNKNOWN, also nicht verlässlich gemessen. |

## Validierung und verbleibende Grenzen

Die lokale portable Vollprüfung besteht ohne Fehler oder Blockierung. Ihre
einzige Warnung `LOCAL_OVERRIDE_OR_DRIFT` betrifft ausschließlich die bereits
geprüfte und unveränderte Schemalinkkorrektur im Orchestratorleitfaden. Der
aktuelle Installationsnachweis und der Projektvalidator binden deren feste
Quell-/Zielhashes und Begründung; die Warnung wird nicht als ungeprüfter Drift
übergangen. Der Projektvalidator besteht mit vollständigem Ein-Feature-Delta
und allen 114 Installationshashes. Registry-v2- und Kennungsprüfung bestehen
mit 269 Datensätzen; Kontinuitäts- und Container-Readinessverträge bestehen
für 13 Workflows. Readiness bedeutet hier die statische Prüfung der
Startbereitschaftsverträge, keinen tatsächlichen Containerstart.

Der unabhängige Diffreview ist ohne offene priorisierte Befunde geschlossen.
Die aktuellen Integrationsgates werden vor dem regulären Merge geschlossen.
Der Validator erhält bisherige
Aktivierungsgrenzen als historische Projektentscheidungen und behauptet aus
struktureller Discovery keine Verständlichkeit.

Native SQL-/Lab-, Host-, Trust-, Provider-, Importbyte- und reale Modellabnahmen
sind für dieses Upgrade nicht ausgeführt. Vollständige Dokumentationskonformität
des Altbestands wird nicht behauptet. Nach erfolgreichen Prüfungen und regulärer
Main-Integration mit eigener Branchbereinigung folgt die nächste eigenständig
begrenzte autorisierte Entwicklungswelle.
