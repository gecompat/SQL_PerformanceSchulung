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

Quellenkorrektur und vierzehn reine Oracle-Testmethoden sind vorbereitet und
bestehen. Statische Frameworkvertrags-, Bereitschafts-, Kontinuitäts- und
Selektorprüfungen bestehen. Der unabhängige Quellen- und Testreview ist ohne
offene priorisierte Befunde abgeschlossen. Ein Befund zur spezifischen
strukturierten Ablehnung im Fall ohne Marker ist korrigiert und unabhängig
geschlossen. Nach vollständigem Setupabschluss über PR297 und PR298 ist der
Branch auf den aktuellen Main übernommen; beide getrennten Selektorgegenproben
bleiben erhalten. Der konkrete Aufrufreview nach erneuter Quellenbindung ist
abgeschlossen. Versionsqualifikation und Integration sind inzwischen wie unten
beschrieben abgeschlossen.
Der erste lokale Lauf C3 endete nach 56,730 Sekunden als FAIL: Alle drei alten
Aktionen zeigten ihre tatsächliche falsche Eigentumsannahme, einschließlich der
unzulässigen Entfernung der eigenen Fixture. Beim ersten Profil scheiterte
anschließend der Testleser an den sechs Pipezeichen innerhalb des regulären
Sollwerts der Demokennungsablehnung. Der vollständige native Ausgabewert dieser
erfolgreich zurückgegebenen Abfrage war im ersten Fehlerlog nicht enthalten;
die kanonische Quelle belegt den Diagnosefeldwert. C3 ist keine vollständige
Qualifikation. Caller und eigener Container sind beendet und unabhängig abwesend;
28 Rohinputs und der unveränderte Fehlerlog bleiben erhalten.

C4 ergänzt ausschließlich eine verlustfreie Erkennung dieses vollständig
bekannten Diagnosefelds. Andere Zusatzspalten, geänderte Präfixlisten und
unpassende Records bleiben Fehler. Der Fehlerleser erhält begrenzte native
Diagnoseausgabe. Eine neue reine Gegenprobe prüft die konkrete reguläre Form
und ihre Ablehnungsfälle. Produkt- und SQL-Aufräumquellen bleiben unverändert.
Nach erneuter Quellenbindung und unabhängigem Ergebnis-/Deltareview bestand
der zweite lokale Lauf C4 nach 210,510 Sekunden auf SQL Server 2025: alle drei
tatsächlichen Altverletzungen, sechs eindeutige Profile mit insgesamt 180
Negativfällen, spezifische Ablehnungsrecords und vollständiger Zustandserhalt,
positive Wiederverwendung, zwei Neuanlagen mit anschließender Wiederverwendung
und tatsächlicher Löschung sowie unabhängiger Absenz. Beide schädigenden
Oracle-Gegenproben und die Markerabweichung hinter Zeichen 128 bestanden.
Caller und beide eigenen lokalen Container sind beendet und unabhängig abwesend;
kein Zeitablauf oder ungeklärter Ressourcenbestand. C3 bleibt FAIL. Alle
gebundenen Rohinputs und Logs beider Versuche bleiben erhalten.

## Versionsqualifikation und Integration

[PR299](https://github.com/gecompat/SQL_PerformanceSchulung/pull/299) ist regulär
in Main `6e9e485488c47d612f3e2da8622cf336f10b6f65` integriert. Am Änderungsstand
und auf frischem Main bestanden die drei Versionsprüfungen auf SQL Server 2019,
2022 und 2025 samt ihren drei eigentumsgebundenen Container-Abbau-/Absenzschritten.
Je Welle wurden 18 Profile mit 540 Negativfällen ausgeführt; die bisherigen
Frameworkverfahren liefen anschließend ebenfalls erfolgreich.

Am Änderungsstand waren alle zehn Workflow-Runs erfolgreich. Unter den 16
Prüfheadern waren bei der Integration zwölf erfolgreich, einer fachlich nicht
ausgewählt und drei trotz abgeschlossener erfolgreicher Verfahren noch
ausstehend: SQL Server 2019, SQL Server 2022 und Datenschutz. Ihre Schritte
einschließlich Jobabschluss waren erfolgreich. Beide erforderlichen Checks
waren erfolgreich; der reguläre Merge benötigte keinen Bypass. Die alten
Header wurden ausdrücklich als PENDING (ausstehend) erhalten, nicht grün ersetzt.

Der frische Main ist vollständig erfolgreich: acht Workflow-Runs und 14
Prüfheader mit 13 Erfolgen und einem fachlich nicht ausgewählten Matrixjob.
Es gibt dort keinen offenen Header. Vollständige Baumübernahme, lokale
Main-Synchronisation und Entfernung des eigenen lokalen sowie Remote-Branches
sind bestätigt. Alle elf eigenen lokalen Container aus den drei bisherigen
Produktschnitten sind unabhängig abwesend. Der getrennte Dokumentationsabschluss
löst keine neue SQL-Welle aus.

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
wählt konservativ Laufzeit. Die konkrete Auswahl bestätigt ausschließlich den
Frameworkworkflow mit drei SQL-Jobs und 90 konfigurierten Jobminuten je Welle
als Obergrenzenschätzung. Vorgesehen sind eine aktuelle Head-Welle, höchstens eine weitere bei
tatsächlich geändertem relevantem Input und eine frische Main-Welle. Head ist
der geprüfte Änderungsstand. Die endliche Reserve umfasst höchstens neun
SQL-Jobs; der unabhängige Ergebnis-/Integrationsreview ist abgeschlossen.
Tatsächlich wurden genau eine Head- und eine Main-Welle mit zusammen sechs
SQL-Jobs verbraucht, ohne zusätzliche lokale Versionsdopplung oder manuelle
Wiederholung. Die optionale weitere Welle wurde nicht zugelassen.

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
