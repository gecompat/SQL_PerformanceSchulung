# FWK-002 – Vollständige Eigentumsprüfung der Frameworkreferenz

FWK-002 bezeichnet den Schutzvertrag für synthetische Testdatenbanken. Dieser
getrennte Folgeschnitt behandelt ausschließlich die vorhandene Referenz
`Demos/00_Framework/Sql/FWK_TestDatabaseLifecycle.sql`. Die Wiederherstellung
nach Fehlern beim erstmaligen Kennzeichnen bleibt getrennt offen.

## Fehlerklasse und Korrektur

Die Referenz liest Eigentumsmarker gekürzt und verwendet gewöhnliche positive
Textvergleiche. Dadurch können abweichende Schreibweise und angehängte
Leerzeichen als passend gelten. Die Korrektur liest alle vier Marker vollständig
über Typumwandlung, Ausgabeparameter und lokale Variablen als `nvarchar(max)`.
Vor Wiederverwendung, Prüfung und Löschung müssen vorhandene Werte ausdrücklich
nicht NULL sein sowie binär und mit vollständiger Bytelänge übereinstimmen.
Fehlercodes, Bestätigungen, Neuanlage und deren bisheriger Recoverypfad bleiben
inhaltlich erhalten. Recovery bedeutet Wiederherstellung nach Fehler oder Abbruch.
Der Nachweis verwendet kanonische Eingabeparameter. Deren bisherige Typbreiten
werden nicht geändert; die gesonderte Prüfung überlanger Rohparameter bleibt
eine offene Grenze dieser Abnahme.

## Gegenproben und Integrationsweg

`Tests/Runtime/framework_ownership.py` benutzt ausschließlich eine eigene
synthetische Testdatenbank in einem eigenen Wegwerfcontainer. Je unterstützter
SQL-Server-Version werden die Aktionen `CREATE` (erstellen oder wiederverwenden),
`VALIDATE` (unverändert prüfen) und `DROP` (löschen) zweimal geprüft. Je Profil
sind 29 Markerfälle und eine ungültige Demokennung vorgesehen: fehlende, NULL-,
falsche, leere, lange und ungenau passende Werte sowie reine Objektmarker.
Der Datenbankname wird durch die Referenz selbst abgeleitet; sie nimmt keinen
freien Zielnamen entgegen. Die ungültige Demokennung muss vor allen Änderungen
scheitern und darf auch keine zweite Datenbank erzeugen.

Jede Ablehnung verlangt den konkreten Fehlercode und die passende strukturierte
Eigentums- beziehungsweise Vertragsablehnung, eine fehlgeschlagene Zusammenfassung
und bytegleichen vollständigen Vor-/Nachzustand. Verglichen werden Identität,
Optionen, Prüfzeile, Struktur und sämtliche Markerbytes mit Typ und Scope.
Scope bezeichnet die Ebene des Markers, etwa Datenbank oder Tabelle.
Der Fall ohne Marker führt die vollständige Originaldatei einschließlich
GO-Batchtrenner und Fehlerstopp aus; ein angehängter Batch muss unerreicht bleiben.
Zusätzlich muss dieselbe Bedingung ohne Marker im unveränderten Kontrollbatch
die konkreten Eigentums- und Zusammenfassungsrecords liefern; ein bloßer
generischer Fehler 51002 genügt nicht.
Weitere Fälle führen den unveränderten Kontrollbatch aus. Ein konservativer
Parser weist andere Batchformen zurück.

Markerunterschiede hinter Zeichen 128 müssen sichtbar sein. Absichtlich
schädigende Änderungen an Prüfzeile und Konfiguration müssen das Oracle
abweisen; Oracle bezeichnet die unabhängig festgelegte Ergebniserwartung.
Positive Wiederverwendung und Prüfung müssen den vollständigen Zustand
erhalten. Neuanlage und anschließende Wiederverwendung werden ebenfalls geprüft.
Löschung erfolgt durch die tatsächliche Referenz mit allen Bestätigungen und
unabhängiger Absenzprüfung. Ein erneutes `DROP` bei bereits fehlender Datenbank
meldet nach dem bestehenden Vertrag `FAIL_STATE` statt `PASS`.

Lokal soll die unveränderte alte Quelle für alle drei Aktionen ihre falsche
Eigentumsannahme zeigen; beim Löschen wird die tatsächlich unzulässige Entfernung
der eigenen synthetischen Fixture nachgewiesen. Fixture bedeutet Testaufbau.
Die beiden öffentlichen Frameworkrunner führen die neuen Gegenproben vor ihren
bisherigen vier Datenbank-Lifecycles aus. Der vorhandene Versionsworkflow bleibt
die Integrationsroute; eine zweite Laufzeitmatrix wird nicht ergänzt.

## Tatsächlicher Stand und endlicher Rahmen

Quellenkorrektur und dreizehn reine Oracle-Testmethoden sind vorbereitet und
bestehen. Statische Frameworkvertrags-, Bereitschafts-, Kontinuitäts- und
Selektorprüfungen bestehen. Unabhängiger Quellen-/Test-/Aufrufreview,
lokale Gegenproben, frische Versionsqualifikation und Integration stehen aus.
Es wurde noch kein lokaler oder entfernter SQL-Prüflauf dieses Schnitts gestartet.
Die Vorbereitung darf parallel zum wartenden vorherigen Integrationsgate
erfolgen; die Ausführung beginnt erst nach dessen vollständigem Abschluss.

Ein Verantwortlicher und der vorhandene unabhängige Reviewer bearbeiten
höchstens acht Quellenstände und vier neue lokale Container. Checkpoint nach
fünf Ständen oder dem ersten blockierenden Befund. Neun frühere lokale Container
bleiben abgeschlossen gezählt; die globale Grenze bleibt 17. Je Parentlauf
gelten 1800 Sekunden regulär plus einmal 90 Sekunden zum Abbau. Keine Ports,
Mounts, Downloads, vorhandene Hostinstanz oder fremde Daten. Rohquellen und
Fehlernachweise bleiben privat im ignorierten Runtime-Verzeichnis. Modell- und
Tokenverbrauch sind unbekannt. An der harten Grenze oder bei ungeklärten
Ressourcen beginnt kein weiterer Lauf.

Die neue reine Teststufe läuft einmal vor der vorhandenen Versionsmatrix.
Der tatsächliche Laufzeitconsumer erhält seine importierten Abhängigkeiten
als Workflowinputs; reine Oracletests bleiben statisch, unklare Revisionsbindung
wählt konservativ Laufzeit. Es sind vorläufig drei SQL-Jobs je Head- oder
Main-Welle vorgesehen: eine aktuelle Head-Welle, höchstens eine weitere bei
tatsächlich geändertem relevantem Input und eine frische Main-Welle. Head ist
der geprüfte Änderungsstand. Die konkrete Auswahl und Reservierung erfolgen vor
dem Push. Unveränderte Wiederholungen und zusätzliche lokale Versionsdopplungen
sind nicht vorgesehen.

Der Versionsworkflow bindet vor Erstellung eine konkrete Image-ID (Kennung des
Containerabbilds), eigenen Besitzer und Containernamen. Er begrenzt den
Prüfbefehl auf 25 Minuten mit höchstens 30 Sekunden bis zum erzwungenen Ende;
das Joblimit bleibt 30 Minuten. Zeitablauf ist ein Fehler. Der immer ausgeführte
eigene Abbau prüft Besitzer und Image, danach unabhängig Kennung, Name und
Besitzerabsenz. Er erfolgt vor dem entfernten Hochladen der Diagnose. Laufende
SQL-Jobs werden nicht automatisch abgebrochen. Bestehende fachliche Gates und
die Anforderungen bei fehlgeschlagenem Abbau bleiben erhalten.

## Lesen und weiterarbeiten

Der [Frameworkeinstieg](../../Demos/00_Framework/README.md) erklärt Verwendung,
Verzeichnisse und Grenzen; der [Schutzvertrag](../../Demos/00_Framework/Contracts/FWK-002_TestDatabase_Lifecycle_Contract.md)
ist die fachliche Autorität. Nach Fehlern gilt der
[Demo-Ausführungsleitfaden](../HowTo/DEMO_EXECUTION_GUIDE.md). Der
[aktuelle Ausführungsstand](CURRENT_EXECUTION_STATUS.md) führt Integration und
verbleibende Prioritäten. Dieser begrenzte Eigentumsnachweis ist keine globale
Framework-, Produktions- oder Hostfreigabe.
