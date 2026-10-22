# FWK-002 – Eigentumsprüfung der verbliebenen Cleanups

FWK-002 ist der Schutzvertrag für synthetische Testdatenbanken. Cleanup bedeutet
Aufräumen nach einer Demo. Dieser Nachweis behandelt ausschließlich die 22 am
22. Oktober 2026 noch offenen negativen Markerprüfungen, ausgehend von Main
`62b1ed2`. Der Mensch hat Korrektur, relevante Tests, Dokumentation, unabhängigen
Review und Integration nach `origin/main` ausdrücklich beauftragt.

## Bestätigte Fehlerklasse und Umfang

Alle 22 Quellen vergleichen vier möglicherweise fehlende Marker ausschließlich
mit `<>`. Ein fehlender Wert ergibt NULL und kann die Ablehnung umgehen.
Zusätzlich kürzen Typumwandlung, Ausgabeparameter und lokale Variablen Werte;
gewöhnliche Textvergleiche unterscheiden nicht alle Schreibweisen oder
angehängten Leerzeichen. Ein Name allein beweist kein Datenbankeigentum.

Die Korrektur liest alle vier Werte vollständig als `nvarchar(max)`, lehnt NULL
ausdrücklich ab und vergleicht Zeichen binär sowie die vollständige Bytelänge.
DGN-005 prüft das Eigentum vor jedem Stoppen oder Löschen einer Ereignissitzung.
Fehlt seine Datenbank bei noch vorhandener Ereignissitzung, bleibt die Sitzung
erhalten und Cleanup meldet einen Fehler statt eines vollständigen Abschlusses.
Extended Events ist die SQL-Server-Funktion zur gezielten Ereigniserfassung.

| Kennung | Thema | Cleanupwirkung |
|---|---|---|
| `STL-008` | Transaktionslog und Dateiwachstum | Datenbanklöschung |
| `STL-009` | Änderungen gemeinsam bestätigen | Datenbanklöschung |
| `OPT-002` | Statistiken lesen | Datenbanklöschung |
| `OPT-003` | Stichproben und Datenverteilung | Datenbanklöschung |
| `OPT-005` | Wachsende Schlüssel und Statistikpflege | Datenbanklöschung |
| `OPT-009` | Parametersensitive Planoptimierung | Datenbanklöschung |
| `OPT-010` | Planoptimierung für optionale Parameter | Datenbanklöschung |
| `OPT-013` | Sortieren bei Speichermangel | Datenbanklöschung |
| `OPT-015` | Planeigenschaften | Datenbanklöschung |
| `OPT-016` | Wiederholte Operatorausführung und Zwischenspeicherung | Datenbanklöschung |
| `OPT-017` | Ungleiche Last in parallelen Plänen | Datenbanklöschung |
| `IDX-006` | Seitenaufteilungen und Belegung | Datenbanklöschung |
| `IDX-010` | Columnstore-Segmente überspringen | Datenbanklöschung |
| `CON-009` | Kosten in tempdb unterscheiden | Datenbanklöschung |
| `QRY-004` | Optionale Filter und dynamisches SQL | Datenbanklöschung |
| `QRY-013` | Client- und Sitzungskontext | Datenbanklöschung |
| `RES-007` | Wartezeiten im richtigen Messbereich | Datenbanklöschung |
| `CON-004` | Blockierungsketten | Datenbanklöschung |
| `CON-006` | Zyklische Sperrkonflikte | Datenbanklöschung |
| `DGN-003` | Abfragehistorie mit Query Store | Datenbanklöschung |
| `DGN-005` | Gezielte Ereigniserfassung | Datenbanklöschung |
| `DGN-007` | Zeitlich begrenzter Diagnosefall | Rückfall ohne Datenbanklöschung |

## Prüfverfahren und aktueller Stand

`Tests/Runtime/cleanup_ownership.py` führt jede Originalquelle mit sqlcmd aus.
Die alte Quelle wird lokal aus einer unveränderten privaten Kopie geprüft:
Eine eigene synthetische Datenbank ohne Marker muss die tatsächliche alte
Löschung beziehungsweise den unzulässigen Rückfall zeigen. Die neue Quelle
muss fehlende und NULL-Marker, falsche/leere/lange Werte, angehängte Leerzeichen,
abweichende Schreibweise, reine Objektmarker und ein falsches Ziel abweisen.
Ein weiterer Batch nach der erwarteten Ablehnung darf nicht ausgeführt werden.

Vor und nach jeder Ablehnung werden Datenbankidentität, Zustand, Optionen,
Sentinelstruktur/-wert sowie vollständige Markerbytes mit Typ und Scope
verglichen. Sentinel bezeichnet eine synthetische Prüfzeile. Unterschiede
hinter 128 Zeichen müssen durch eine eigene Oracle-Gegenprobe sichtbar sein;
Oracle bezeichnet hier die unabhängig festgelegte Ergebniserwartung.
Bei den zwei Ereignispfaden bleiben zusätzlich Definition und Laufzustand der
Ereignissitzung erhalten; beim Diagnosefall ebenso Prozedur und Referenzdaten.
Zwei positive Durchläufe je Version prüfen den passenden Cleanup und dessen
Wiederholung sowie unabhängige Datenbank-/Sitzungsabsenz.

Sieben reine Testmethoden prüfen Quelleninventar und Testoracles. Native Ausführung
und aktuelle Integrationsprüfungen sind noch offen; es wird kein Laufzeit-PASS
behauptet. Private Ausgangsbytes, Quellenbindungen, Rohlogs und Budgets liegen
ausschließlich im ignorierten Runtime-Verzeichnis.

## Aufwand, Grenzen und Folgearbeit

Ein Owner und ein unabhängiger Reviewer, höchstens sechs Kandidaten und sechs
serielle eigene lokale Container; Checkpoint nach drei oder erstem blockierenden
Befund. Pro Lauf 1800 Sekunden regulär plus einmal 90 Sekunden für den Abbau.
Keine Ports, Mounts, Downloads, fremde Daten oder vorhandene Hostinstanz.
Modell-/Tokenverbrauch bleibt unbekannt. Fehlversuche werden nicht überschrieben.

Der neue Workflow ergänzt drei Versionsjobs für diese bislang fehlenden
Markergegenproben. Bestehende fachliche Matrizen und ihre Wiederholungen bleiben
erhalten; keine zusätzliche Reviewkette. Die breite bestehende Katalogauswahl
wird hier nicht geändert. Lokale grüne Tests werden nur bei verändertem Input,
neuem Befund oder einer vorgeschriebenen Wiederholung erneut ausgeführt.
Aktuelle Pull-Request- und Main-Prüfungen bleiben erforderlich.

Vor dem ersten Push ist für die notwendige CI (Continuous Integration;
automatisierte Integrationsprüfung) genau eine aktuelle Head- und eine frische
Main-Welle reserviert. Die tatsächlichen Selektoren wählen je 54 SQL-Matrixjobs
einschließlich der drei neuen Eigentumsjobs; zusammen 108 Jobs und 7500
konfigurierte Jobminuten als Obergrenzenschätzung, kein gemessener Verbrauch.
Die lokale Sechscontainergrenze zählt ausschließlich lokale Admissionen und
bleibt mit ihrem verbrauchten Versuch erhalten. Es gibt keine manuellen
CI-Wiederholungen; laufende SQL-Jobs werden bis zu ihrem Cleanup erhalten.
Unterstützte Versionen werden durch diese frischen Matrizen qualifiziert,
ohne zusätzliche lokale 2019-/2022-Dopplung. Zusätzliche geänderte Head- oder
Base-Stände benötigen vor einer weiteren Welle eine neue konkrete Reservierung.

C3 wurde nach 253,740 Sekunden bewusst wegen zu vieler einzelner Clientaufrufe
abgebrochen. Sein Caller endete mit Fehler; der eigene Container ist unabhängig
abwesend. Dieser Versuch bleibt FAIL, kein vollständiger Laufzeitnachweis.
Die zwei damaligen uncommitteten Python-Testdateien wurden vor einer eigenen
Rohkopie ersetzt; ihre Hashbindungen, ursprünglichen Logs und Fehler-/Stop-/
Cleanuprecords sind erhalten, die exakten Testbytes nicht vollständig
rekonstruierbar. C3 ist deshalb keine reproduzierbare Qualifikation. Seine
Teil-PASSs werden nicht für C5 übernommen. Vor weiteren Änderungen wurden für
C5 alle 49 gebundenen Quellen bytegenau archiviert und erneut verglichen.
C4 war ein reiner Testentwurf. C5 bündelt jeden negativen Fall in einen echten
SQL-Aufruf mit getrennten vollständigen Vor-/Nach-Katalogrecords. XML
(Extensible Markup Language; strukturiertes Datenformat) hält die Records ohne
Markertrunkierung; Fehlercode, NULL und Länge werden ausdrücklich geprüft.
Eine echte vollständige sqlcmd-Form mit Batchtrenner und Fehlerstopp bleibt je
Demo erhalten. Die Anzahl der Fälle und Wiederholungen bleibt unverändert.
Eine absichtlich schädigende synthetische Quelle muss das Testoracle abweisen.
Der neue lokale 2025-Lauf ist noch nicht abgeschlossen.

Die Frameworkreferenz `FWK_TestDatabaseLifecycle.sql` besitzt außerhalb dieses
Inventars weiterhin gekürzte positive Markerprüfungen. Andere Setups und die
Wiederherstellung bei fehlgeschlagener Erstkennzeichnung bleiben getrennt offen.
Diese Korrektur ist keine globale Eigentumssicherheits-, Host- oder
Produktionsfreigabe und keine vollständige Abnahme des Diagnosefalls.

## Lesen und weiterarbeiten

Für Anwender gilt der [Demo-Ausführungsleitfaden](../HowTo/DEMO_EXECUTION_GUIDE.md).
Bei ungeklärtem Eigentum Daten erhalten und ausschließlich die eigene
Wegwerfinstanz verwenden. Der [Schutzvertrag](../../Demos/00_Framework/Contracts/FWK-002_TestDatabase_Lifecycle_Contract.md)
beschreibt die weiterhin geltenden Anforderungen. Der [aktuelle Ausführungsstand](CURRENT_EXECUTION_STATUS.md)
führt Integration, verbleibende Grenzen und den nächsten begrenzten Schnitt.
