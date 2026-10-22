# FWK-002 – Eigentumsprüfung vor Setupänderungen

FWK-002 bezeichnet den Schutzvertrag für synthetische Testdatenbanken. Setup
bedeutet Einrichtung einer Demo. Dieser getrennte Folgeschnitt prüft zehn
vorhandene Einrichtungsskripte nach der abgeschlossenen Cleanupkorrektur
(Aufräumen) aus [PR295](https://github.com/gecompat/SQL_PerformanceSchulung/pull/295).
Ausgangsstand ist Main `dd73310`; der nachfolgende Dokumentationsabschluss
ändert keine Produkt- oder Testquellen.

## Bestätigter Fehler und Korrektur

Die zehn alten Quellen änderten die Datenbankkonfiguration, bevor sie das
Eigentum einer vorhandenen Datenbank prüften. Ihre Markerprüfung wies NULL
nicht ausdrücklich ab und konnte Werte kürzen oder ungenau vergleichen.
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
Quellen-/Test-/Aufrufreview ohne offene priorisierte Befunde liegt vor.

Der erste lokale Lauf C2 scheiterte nach 21,781 Sekunden im synthetischen
Testaufbau: `CREATE SCHEMA` war mit nachfolgenden Anweisungen in einem Batch
verbunden und meldete Syntaxfehler 156. Es wurde keine vollständige
Produktgegenprobe erreicht. Caller und eigener Container sind beendet und
unabhängig abwesend. Die 41 gebundenen Rohquellen und der Fehlerlog bleiben
erhalten. C3 führt die Schemaanlage in einem eigenen dynamischen Batch aus;
Produktquellen und Prüfanforderungen bleiben unverändert.

C3 bestand nach 1068,273 Sekunden auf SQL Server 2025: zehn tatsächliche alte
Konfigurationsverletzungen, alle zehn korrigierten Quellen zweimal mit insgesamt
620 Negativfällen, positive wiederholte Einrichtung und Neuanlage sowie die
jeweiligen wiederholten Cleanups mit unabhängiger Datenbankabsenz. Die
Marker-Gegenproben und beide schädigenden Oracle-Gegenproben bestanden.
Caller und beide eigenen lokalen Container sind beendet und unabhängig
abwesend; kein ungeklärter Ressourcenbestand. Alle 41 gebundenen Rohquellen
beider Versuche bleiben erhalten. `C2` und `C3` bezeichnen die jeweiligen
Quellen-/Teststände dieses Setup-Schnitts. Dieser lokale 2025-Nachweis ersetzt
die frischen Versions- und Integrationsgates nicht.

## Versionsprüfung und Integration

[PR297](https://github.com/gecompat/SQL_PerformanceSchulung/pull/297) ist regulär
in Main `44f12b4797c7f492fabc5706f9bf8d03d9a739bb` integriert; der vollständige
Baum stimmt mit dem geprüften Änderungsstand überein. Am Änderungsstand bestanden
24 SQL-Matrixjobs und ihre 24 Container-Abbauschritte. Der neue Setupworkflow
bestand auf SQL Server 2019 acht Demos mit 496 Negativfällen, auf 2022 neun mit
558 und auf 2025 zehn mit 620. Zusammen sind das zweimal je unterstützter Demo,
54 Profile und 1674 Negativfälle. Nicht unterstützte Demos werden vor ihrem
Testaufbau übersprungen.

Bei der Integration waren 48 Prüfungen am Änderungsstand erfolgreich und ein
nicht ausgewählter Matrixjob übersprungen. Ein optionaler statischer Header blieb ausstehend:
Run 39823663642, Job 119981159307. Alle acht Schritte einschließlich der
Ausführungspfad- und Leitfadenvalidatoren sowie Jobabschluss sind erfolgreich;
der Header wurde ausdrücklich PENDING (ausstehend) geführt. Beide erforderlichen
Prüfungen waren erfolgreich. Der reguläre Merge erfolgte ohne Bypass und ohne
grünen Ersatzstatus. Die aktuelle GitHub-Status-API meldet Actions seit
17:41:38 UTC wieder als verfügbar; eine zuvor ältere HTML-Antwort begründet
keine Ausfallausnahme. Die Ursache des einzelnen offenen Headers bleibt unbekannt.

Die ergänzenden lokalen Pflichtprüfungen bestanden am exakten Änderungsstand.
Ein voller Datenschutzscan im Arbeitsverzeichnis scheiterte am URL-Parser in
ignorierten privaten Runtime-Dateien und bleibt als Fehlversuch erhalten. Der
volle Scan des sauberen Git-Exports desselben veröffentlichten Baums bestand;
alle Pfade stimmen überein, ausschließlich lokale Zeilenenden unterscheiden
Textbytes. Das ersetzt keine fehlgeschlagene fachliche Prüfung.

Die frische Main-Prüfung ist vollständig erfolgreich: 15 Workflows, 47 erfolgreiche
Prüfungen und ein fachlich nicht ausgewählter Matrixjob. Alle 24 SQL-Jobs und
24 Abbauschritte bestanden; der neue Setupworkflow erneut mit denselben
54 Profilen und 1674 Negativfällen auf allen drei Versionen. Auch der zuvor
betroffene statische Workflow ist am frischen Main vollständig erfolgreich.
Der einzelne alte Header war bei dieser Nachprüfung weiterhin ausstehend;
dies wird nicht als erfolgreicher Head-Check umgedeutet. Vollständige Baumübernahme,
lokale Main-Synchronisation und Entfernung des eigenen lokalen sowie
Remote-Branches sind bestätigt. Alle neun eigenen lokalen Container aus
Cleanup- und Setup-Schnitt sind unabhängig abwesend. Der getrennte
Dokumentationsabschluss löst keine neue SQL-Welle aus.

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
Der eigentliche CI-Prüfbefehl besitzt ein eigenes Limit von 1800 Sekunden mit
höchstens 30 Sekunden bis zum erzwungenen Prozessende. Das Joblimit von
45 Minuten lässt danach Zeit für den immer ausgeführten Containerabbau.
Ein Zeitlimit ist ein Fehler und wird nicht als erfolgreiche Prüfung gewertet.

Für CI (Continuous Integration; automatisierte Integrationsprüfung) sind eine
aktuelle Änderungswelle, höchstens eine weitere Welle bei tatsächlich geändertem
relevantem Input und eine frische Main-Welle vorgesehen. Die genaue Auswahl
wurde anhand der betroffenen Quellen und tatsächlichen Filter geprüft:
24 SQL-Jobs je Welle, höchstens 72. Je Welle sind 1170 konfigurierte Jobminuten
eine Obergrenzenschätzung und kein gemessener Verbrauch.
Keine manuellen Wiederholungen unveränderter grüner Läufe und keine zusätzliche
lokale Versionsdopplung. Genau eine Änderungswelle mit 24 SQL-Jobs und die
reservierte frische Main-Welle mit weiteren 24 sind erfolgreich. Eine weitere
Änderungswelle wurde nicht zugelassen. Der abschließende unabhängige
Ergebnis-/Deltareview liegt ohne offene priorisierte Befunde vor. Zwei eigene
lokale Container wurden verbraucht und sind unabhängig abwesend; die übrige
lokale Reserve wird nicht in diesen abgeschlossenen Versuch zurückgesetzt.

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
