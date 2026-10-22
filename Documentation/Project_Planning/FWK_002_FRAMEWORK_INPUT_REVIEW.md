# FWK-002 – Vollständige Eingaben vor Aktions- und Namensableitung

FWK-002 bezeichnet den Schutzvertrag für synthetische Testdatenbanken. Dieser
vierte begrenzte Produktschnitt folgt auf die abgeschlossenen Eigentumsprüfungen
der Cleanup-, Setup- und Frameworkquellen. Die Referenzimplementierung liegt in
`Demos/00_Framework/Sql/FWK_TestDatabaseLifecycle.sql`; Ausgang ist der vollständig
abgeschlossene Main `a541b978aa06fc663dbd7371cba16aca63858515` nach PR299/PR300.

## Fehlerklasse und Korrektur

Feste Eingabebreiten für Aktion, Demokennung und Lauftoken können ungültige
Suffixe vor der Vertragsprüfung abschneiden. Die bisherige normalisierte
Tokenvariable kann zusätzlich kürzen. Sprachabhängige Zeichenvergleiche können
andere Schreibweisen als kanonische Zeichen behandeln. Ein zutreffender
Eigentumsmarker löst diese vorherige Verwechslung des angeforderten Ziels oder
der Aktion nicht.

Die Korrektur erhält alle Rohwerte und den normalisierten Lauftoken als
`nvarchar(max)` (vollständiger Unicode-Text). Eine Demokennung benötigt exakt
sieben ASCII-Zeichen in der festgelegten Großschreibung; ASCII ist der hier
verwendete Grundzeichensatz für lateinische Buchstaben und Ziffern. Aktion und
Token behalten die erlaubte Normalisierung äußerer einfacher Leerzeichen und
kleiner ASCII-Buchstaben unter ausdrücklich festgelegter Kollation. Binäre Zeichenmengenprüfungen weisen andere
Unicodeformen ab. NULL-Aktionen werden ausdrücklich zurückgewiesen.
Erst gültige Eingaben dürfen den vollständigen Namen bestimmen und anschließend
in `sysname`, den SQL-Server-Namenstyp, überführt werden. Fehlerdiagnosefelder
werden für ihre Darstellung begrenzt; die Entscheidung verwendet den Vollwert.
Eigentumsmarker, Erstellungsparameter und Recovery bleiben inhaltlich erhalten.
Recovery bedeutet Wiederherstellung nach einem Fehler oder Abbruch.

## Prüfverfahren und tatsächlicher Stand

`Tests/Runtime/framework_inputs.py` prüft nur eine eigene synthetische Fixture
(Testaufbau) in einem eigenen Wegwerfcontainer. Für `CREATE` (erstellen oder
wiederverwenden), `VALIDATE` (prüfen) und `DROP` (löschen) sind zweimal je 18
Negativfälle vorgesehen: zu lange Suffixe, Abweichungen erst hinter Zeichen
4000, NULL, leere Werte, unzulässige Demokennungsschreibweise und andere
Unicodeformen. Insgesamt sechs Profile und 108 Negativfälle je Version.

Je Eingabefamilie und Profil wird die vollständige Datei einschließlich
GO-Batchtrenner und sqlcmd-Fehlerstopp ausgeführt; ein angehängter Batch darf
nicht erreicht werden. Der gleiche Fall muss außerdem im unveränderten
Kontrollbatch den spezifischen Eingabecheck und eine fehlgeschlagene
Zusammenfassung mit `FAIL_CONTRACT` liefern. Jeder weitere Negativfall verwendet
ebenfalls diesen Kontrollbatch. Unbekannte Batchformen werden zurückgewiesen.

Das Oracle, die unabhängig festgelegte Ergebniserwartung, vergleicht die
vollständigen Fixturebytes samt Identität, Optionen, Struktur, Prüfzeile und
allen Eigentumsmarkern. Zusätzlich wird das Inventar aller Benutzerdatenbanken
verglichen, damit eine irrtümliche Neuanlage unter anderem Namen auffällt.
SQL-seitige Vergleiche verlangen vollständige Werte, gleiche Länge und Inhalt;
übertragene Positivsnapshots verwenden die bestehende strikte Chunkdekodierung.
Die ersten fünf typisierten Ergebnisfelder sind das Ablehnungsoracle; freie
Diagnosefelder bleiben ungeteilt, da sie reguläre Pipezeichen enthalten können.
Fehlende oder doppelte Pflichtrecords, andere Fehler, Warnungen und übersprungene
Prüfungen werden nicht als Eingabeablehnung anerkannt.

Schädigende Gegenproben müssen sowohl eine geänderte Prüfzeile als auch eine
zusätzlich angelegte Datenbank erkennen; danach muss der vollständige Zustand
restauriert sein. Positive Fälle führen die tatsächlich übergebenen kleinen
Aktionen und gepolsterten Token unverändert aus. Wiederverwendung wird zweimal
geprüft; Neuanlage, tatsächlicher markergeprüfter Abbau und unabhängige Absenz
gehören dazu. Die alte unveränderte Quelle soll für alle drei Parameterfamilien
und Aktionen ihre tatsächliche falsche Annahme zeigen: neun Gegenfälle,
einschließlich tatsächlicher Entfernung der eigenen Fixture bei `DROP`.

Elf neue reine Testmethoden und die bisherigen 14 Framework-/13 Selektormethoden
bestehen. Frameworkvertrag, authentifizierte Containerbereitschaft, Erhalt
laufender SQL-Prüfungen und Differenzprüfung bestehen. Der unabhängige Quellen-,
Test- und Aufrufreview von C2 ist abgeschlossen. Die erste lokale SQL-Ausführung
dieses Schnitts besteht; entfernte Versions- und Integrationsgates stehen aus.

Der Quellenreview von C1 fand vor jeder Ausführung drei Befunde: die zunächst
noch standardkollationsabhängige Großschreibung, eine zu enge Phasenerkennung
ohne die regulären erfolgreichen SAFETY-Records und eine zu breite Zulassung
zusätzlicher Vertragsfehler. C1 wurde nicht ausgeführt; seine 33 Rohinputs
bleiben erhalten. C2 legt die Großschreibungskollation ausdrücklich fest,
erlaubt ausschließlich die bekannten erfolgreichen Sicherheitsrecords und
bindet alle Pflichtfehler an LIFECYCLE. Zusätzlich sind Namensablehnungsrecord
und Zusammenfassung eindeutig erforderlich. Fremde Vertragsfehler vor dem
Erhaltungsrecord und unpassende Phasen werden durch neue Gegenfälle abgewiesen.
Der unabhängige Delta-/Bindungsreview ließ genau einen lokalen Lauf auf SQL
Server 2025 zu. C2 bestand in 271,230 Sekunden: neun tatsächliche alte
Fehlannahmen, darunter drei Löschungen der eigenen Fixture, und sechs korrigierte
Profile mit 108 Negativfällen. Erhaltungsprüfungen, schädigende Gegenproben,
Normalisierung, Wiederverwendung, Neuanlage, tatsächlicher Abbau und unabhängige
Absenz bestanden. Der eigene Caller ist beendet; der einzige neue Container ist
entfernt und unabhängig abwesend. Alle 33 Rohinputs und das vollständige Log
bleiben privat erhalten. C3 dokumentiert diesen Checkpoint ohne Codeänderung;
Ergebnisreview und Zulassung der entfernten Versionsprüfung folgen.

## Aufwand und Grenzen

Ein Verantwortlicher und der vorhandene unabhängige Reviewer, höchstens sechs
Quellenstände und vier eigene lokale Container; Checkpoint nach drei Ständen
oder dem ersten Blocker. Elf frühere und der eine neue Container sind geschlossen,
globale Grenze weiterhin 17, bei vollständiger Nutzung dieser Reserve höchstens
15 tatsächliche lokale Container. Je Parentlauf gelten 1800 Sekunden plus
einmal 90 Sekunden zum Abbau. Keine Ports, Mounts, Downloads oder Hostinstanz.
Alle Rohquellen, Logs und Ressourcenrecords bleiben privat im ignorierten
Runtime-Verzeichnis. Modell- und Tokenverbrauch sind unbekannt.

Die beiden bestehenden Frameworkrunner ergänzen den Eingabenachweis vor den
vorhandenen 180 Eigentumsgegenfällen und ihren bisherigen Frameworkverfahren.
Der vorhandene Versionsworkflow erhält die tatsächliche Eingabeabhängigkeit
und eine zusätzliche reine Testdatei in seiner einmaligen statischen Stufe.
Keine neue Matrix, keine zweite lokale Versionsprüfung und kein unveränderter
Wiederholungsversuch. Vorläufig drei SQL-Jobs je aktueller Head- und frischer
Main-Welle, eine weitere Welle nur bei relevant geändertem Input; konkrete
Auswahl und endliche Reserve sind vor dem Push zu prüfen. Die bestehende
Prozessgrenze, der eigentumsgebundene Abbau vor Diagnoseupload und unabhängige
Absenz bleiben unverändert. Ein Zeitablauf oder ungeklärter Ressourcenbestand
sperrt neue Admissions (zugelassene Prüfläufe).

Die Wiederherstellung bei fehlgeschlagener Erstmarkierung bleibt getrennt offen.
Dies ist keine allgemeine Framework-, Produktions- oder Hostfreigabe.

## Lesen und weiterarbeiten

Einstieg ist das [Framework-README](../../Demos/00_Framework/README.md), fachliche
Autorität der [Namens- und Schutzvertrag](../../Demos/00_Framework/Contracts/FWK-002_TestDatabase_Lifecycle_Contract.md).
Für Fehler gilt der [Ausführungsleitfaden](../HowTo/DEMO_EXECUTION_GUIDE.md).
Der [aktuelle Ausführungsstand](CURRENT_EXECUTION_STATUS.md) führt das maßgebliche
Integrationsgate und die verbleibenden Prioritäten. Technische Nachprüfung:
genannter Runtime-Consumer, reine Gegenproben und vorhandener Frameworkworkflow.
