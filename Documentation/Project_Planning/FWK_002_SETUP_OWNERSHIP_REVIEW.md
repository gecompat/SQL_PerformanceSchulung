# FWK-002 – Eigentumsprüfung vor Setupänderungen

FWK-002 bezeichnet den Schutzvertrag für synthetische Testdatenbanken. Setup
bedeutet Einrichtung einer Demo. Dieser getrennte Folgeschnitt prüft zehn
vorhandene Einrichtungsskripte nach der abgeschlossenen Cleanupkorrektur
(Aufräumen) aus [PR295](https://github.com/gecompat/SQL_PerformanceSchulung/pull/295).
Ausgangsstand ist Main `dd73310`; der nachfolgende Dokumentationsabschluss
ändert keine Produkt- oder Testquellen.

## Bestätigter Fehler und Korrektur

Die zehn Quellen ändern bislang die Datenbankkonfiguration, bevor sie das
Eigentum einer vorhandenen Datenbank prüfen. Ihre Markerprüfung weist NULL
nicht ausdrücklich ab und kann Werte kürzen oder ungenau vergleichen.
Die Korrektur prüft vor der ersten Änderung alle vier vollständigen Marker:
Projekt, Vertragsversion, Demo und Lauftoken. NULL wird abgewiesen; binärer
Zeichenvergleich und vollständige Bytelänge müssen übereinstimmen. Erst danach
folgen die unveränderte Konfiguration und die weiteren Datenmodellbatches.

| Kennung | Thema | Unterstützte SQL-Server-Versionen |
|---|---|---|
| OPT-002 | Statistiken lesen | 2019, 2022, 2025 |
| OPT-009 | Parametersensitive Planoptimierung | 2022, 2025 |
| OPT-010 | Planoptimierung für optionale Parameter | 2025 |
| OPT-013 | Sortieren bei Speichermangel | 2019, 2022, 2025 |
| OPT-015 | Planeigenschaften | 2019, 2022, 2025 |
| OPT-016 | Wiederholte Operatorausführung und Zwischenspeicherung | 2019, 2022, 2025 |
| OPT-017 | Ungleiche Last in parallelen Plänen | 2019, 2022, 2025 |
| QRY-004 | Optionale Filter und dynamisches SQL | 2019, 2022, 2025 |
| QRY-013 | Client- und Sitzungskontext | 2019, 2022, 2025 |
| CON-004 | Blockierungsketten | 2019, 2022, 2025 |

## Prüfverfahren und tatsächlicher Stand

`Tests/Runtime/setup_ownership.py` verwendet ausschließlich eigene synthetische
Datenbanken in einem eigenen Wegwerfcontainer. Je unterstützter Demo werden
zwei Profile mit je 31 Negativfällen geprüft: fehlende, NULL-, falsche, leere,
lange und ungenau passende Marker, reine Objektmarker, falsches Ziel und
abweichender AUTO_CLOSE-Zustand. AUTO_CLOSE steuert das automatische Schließen
einer unbenutzten Datenbank. Erwarteter Fehlercode und unveränderter vollständiger
Zustand müssen gemeinsam nachgewiesen werden.

Der Fall ohne Marker führt zweimal die vollständige Originaldatei mit sqlcmd
und ihren GO-Batchtrennern aus; ein nachfolgender Batch muss unerreicht bleiben.
Die weiteren Fälle führen den unveränderten ersten Kontrollbatch aus. Ein
konservativer Parser weist unbekannte Vorspann- oder Batchformen zurück; die
späteren Datenmodellbatches werden hierbei nicht in einen anderen Ablauf kopiert.
Verglichen werden Datenbankidentität, vollständige Marker mit Typ und Scope,
Optionen, synthetische Prüfzeilen, Tabellen-/Spalten-/Prozedurkatalog und
datenbankbezogene Konfiguration. Vollständige XML-Records (Extensible Markup
Language; strukturiertes Datenformat) werden bytegenau übertragen; Überlänge,
Lücken und Kürzung sind Fehler.

Eine Markeränderung hinter Zeichen 128 muss sichtbar sein. Absichtliche
Änderungen an Prüfzeile und Konfiguration müssen das Oracle abweisen; Oracle
bezeichnet die unabhängig festgelegte Ergebniserwartung. Positive Gesamtdateiläufe
prüfen zweimal die Wiederverwendung mit erhaltener Identität, Markern und
Prüfzeilen, außerdem Neuanlage, Sollkonfiguration und vollständige Marker.
Jeder Abschluss verwendet den tatsächlichen markergebundenen Cleanup zweimal
und prüft unabhängig die Datenbankabsenz. Lokal muss die unveränderte alte
Quelle ihre tatsächliche Konfigurationsänderung vor der Ablehnung zeigen.

Zwölf reine Testmethoden prüfen die Setuporacles. Zwölf Selektortests prüfen
die Auswahl der Laufzeitjobs. Statische Prüfungen für authentifizierte
Containerbereitschaft und Erhalt laufender SQL-Jobs bestehen. Unabhängiger
Quellen-/Testreview ohne offene priorisierte Befunde liegt vor; Aufrufreview,
lokale Laufzeitgegenproben, Versionsqualifikation und Integration stehen aus.

## Aufwand und Grenzen

Ein Implementierungsverantwortlicher und der vorhandene unabhängige Reviewer
bearbeiten diesen Schnitt. Der endliche Rahmen umfasst höchstens zwölf
Quellenstände und zehn neue lokale Container; Checkpoint nach sechs Ständen
oder dem ersten blockierenden Befund. Die sieben abgeschlossenen Container
des Vorgängers bleiben gezählt. Je Parentlauf gelten 1800 Sekunden regulär
plus einmal 90 Sekunden für den Abbau. Keine Ports, Mounts, Downloads oder
Hostinstanz in lokalen Prüfungen. Rohquellen, Fehlerlogs und Ressourcenrecords
bleiben privat im ignorierten Runtime-Verzeichnis. Modellverbrauch ist unbekannt.

Der neue Workflow wählt nur die zehn tatsächlichen Setup-/Cleanupquellen und
ihre Laufzeitabhängigkeiten. Änderungen reiner Testmethoden führen deren
statische Prüfung aus; unbekannte Revisionsbindungen wählen konservativ die
Laufzeitmatrix. Die reine Prüfung läuft einmal vor der Matrix. Bestehende
fachliche Matrizen und erforderliche Wiederholungen bleiben erhalten.
Laufende SQL-Jobs werden nicht automatisch abgebrochen. Authentifizierte
Bereitschaft, eigener Containerabbau und unabhängige Absenz bleiben Pflicht.

Für CI (Continuous Integration; automatisierte Integrationsprüfung) sind eine
aktuelle Änderungswelle, höchstens eine weitere Welle bei tatsächlich geändertem
relevantem Input und eine frische Main-Welle vorgesehen. Die genaue Auswahl
wird vor dem Push geprüft; geschätzt sind 24 SQL-Jobs je Welle, höchstens 72.
Konfigurierte Zeitgrenzen sind Schätzungen und kein gemessener Verbrauch.
Keine manuellen Wiederholungen unveränderter grüner Läufe und keine zusätzliche
lokale Versionsdopplung. Gegenwärtig wurde keine SQL-Welle dieses Schnitts
ausgelöst. Der Workflow und sein konkreter Aufruf benötigen vor Ausführung
den unabhängigen Review.

Die Frameworkreferenz und Recovery bei fehlgeschlagener Erstmarkierung einer
neuen Datenbank bleiben getrennt offen. Recovery bedeutet Wiederherstellung
nach Fehler oder Abbruch. Dieser Schnitt qualifiziert ausschließlich die zehn
vorhandenen Eigentumspfade; er schafft keine globale Freigabe einer gemeinsam
genutzten Instanz oder des gesamten Frameworks.

## Lesen und weiterarbeiten

Für Anwender gilt der [Demo-Ausführungsleitfaden](../HowTo/DEMO_EXECUTION_GUIDE.md).
Nach einem Abbruch bleiben Daten bei ungeklärtem Eigentum erhalten. Der
[Schutzvertrag](../../Demos/00_Framework/Contracts/FWK-002_TestDatabase_Lifecycle_Contract.md)
beschreibt die Eigentumsanforderungen. Der
[aktuelle Ausführungsstand](CURRENT_EXECUTION_STATUS.md) führt das maßgebliche
Integrationsgate und die danach offenen Prioritäten. Technische Nachprüfung
erfolgt über den genannten Runner und `.github/workflows/setup-ownership.yml`;
die tatsächlichen Nachweise werden hier nach Ausführung ergänzt.
