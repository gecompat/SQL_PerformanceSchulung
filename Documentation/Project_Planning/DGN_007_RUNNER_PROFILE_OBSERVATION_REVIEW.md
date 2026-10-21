# DGN-007 – erste frische Runnerprofilaufnahme

DGN-007 bezeichnet die Diagnose-Demo mit getrenntem Quellen- und Laufnachweis.
Runner ist die vollständige Ausführungssteuerung. Der
[Beobachtungsplan](DGN_007_NATIVE_PROFILE_OBSERVATION_PLAN.md) ist über
[PR287](https://github.com/gecompat/SQL_PerformanceSchulung/pull/287) vollständig
in Main `3266c4763c0e452f8752cd792473308f87ef25df` abgeschlossen: unabhängiger
Review, lokale Dokumentationsprüfung, sieben grüne Head-, fünf grüne Base- und
fünf frische Main-Prüfungen, vollständige Übernahme und eigene Branchbereinigung.

## Gewählter endlicher Implementierungsrahmen

Der kontinuierliche menschliche Auftrag autorisiert diesen eigenen operativen
Schnitt. Ein Implementierungsverantwortlicher root und derselbe unabhängige
Reviewer, höchstens sechs stabile Quellen-/Test-/Aufrufstände, Checkpoint nach
zwei. Die Grenze umfasst Arbeit des Implementierungsverantwortlichen, Reviews, Tests, Koordination und vollständige
Integration. Verbrauch UNKNOWN, also nicht verlässlich gemessen. Höchstens zwei
synthetische Prüfläufe mit je sechs Kindfällen und einem zusätzlichen eigenen Nachfahren; sieben Prozesse je Lauf, höchstens 14 unter der unveränderten Grenze von
18 synthetischen Prozessen, genau ein ausgewählter Runnerstart ohne Retry und
höchstens zehn WSL-Aufrufe einschließlich unabhängiger Absenzprüfung. WSL ist
Windows Subsystem for Linux. Jeder Suitelauf reserviert 200 Sekunden aus dem
gemeinsamen 600-Sekunden-Prozessrahmen; unvollständige Reservierungen bleiben
voll gebucht. Diese äußeren Grenzen erweitern keine fachliche Kanalgrenze.

Die unabhängige Auswahlprüfung gab genau dieses Paket zur Implementierung frei.
Die Auswahl aus [PR286](https://github.com/gecompat/SQL_PerformanceSchulung/pull/286)
bleibt mit allen ursprünglichen Feldern, Rawbytes und ihrer Protokollnonce
unverändert; Rawbytes sind die ursprünglichen Quelldateibytes. Ihr Rahmen mit
acht von hart acht Ständen bleibt geschlossen. Kein neunter Auswahlstand,
kein erneuter Auswahlpaketlauf und kein neues Soll aus beobachteten Istwerten.
Eine getrennte Ownershipnonce bezeichnet ausschließlich den neuen Prozessbesitz.

## Tatsächlich vorgesehenes Verfahren

Der private Windows-Owner prüft vor Projektimporten und erneut vor dem Start
alle alten 22 und zusätzlich benötigten Quellen sowie die neuen Helfer. Er
rekonstruiert den vollständigen gehaltenen Eingang aus den unveränderten
27 Rohdateien, dem alten Commit und derselben Protokollnonce. Die vorhandenen
Codecs erzeugen den DGNC-Header und die vollständige Metadata. DGNC bezeichnet
die festgelegte Eingangsform; die deklarierte Bodylänge bleibt korrekt, obwohl
die neun Kandidatenbodies nicht übertragen werden. Die 58 ausgewählten
Installationsquellen werden auf beiden Seiten erneut gepinnt: jeweils höchstens
16 MiB, zusammen höchstens 32 MiB. MiB bezeichnet 1048576 Bytes. Dies ist eine
Quellenprüfung, kein Nachweis tatsächlich verwendeter Importbytes.

Vor genau einem nativen Dateieinstieg hält ein frischer isolierter
Linux-CPython-3.12-Supervisor seine eigene Identität und die seines neuen
Workerleaders. Er prüft den tatsächlichen Interpreter und den vorgewählten
absoluten Scriptlocator. Die isolierten Flags `-I -S -B` bedeuten isolierter
Modus, keine Site-Initialisierung und keine Bytecodedateien. Es wird weder ein
`-c`-Eintritt als Datei ausgegeben noch eine alte Quelle regeneriert.

Der Supervisor sendet ausschließlich Header und Metadata und drainiert beide
Rückkanäle, leert sie also laufend. Der begrenzte Empfänger prüft Profilbeginn,
geordnete Fragmente und Profilabschluss vollständig; der bestehende Poolcodec
prüft sämtliche empfangenen Felder gegen die separat gehaltene Erwartung.
Native Reportbytes und tatsächliche Skalare bleiben ausschließlich im begrenzten
Arbeitsspeicher des steuernden Prozesses. Gespeichert werden nur feste Ergebnislabels, Größen, Hashes und
gegebenenfalls Feldpositionen ohne tatsächliche Werte.

Es gibt kein `BODY_RELEASE`, keinen Kandidatenbody, kein `BODY_END` und kein
`IMPORT_RELEASE`. Nach dem Profilvergleich stoppt der Supervisor ausschließlich
seine eigene gehaltene Prozessgruppe. Geplanter Stop, tatsächliche Pipeabschlüsse,
Reap, frische Gruppen-/Kinderabsenz und Restore bleiben getrennte Bedingungen;
Reap ist das kontrollierte Abholen des Prozessendes. Der Windows-Owner hält
separat seinen Launcherjob. Ein weiterer begrenzter Linux-Helfer prüft nur die
bekannten Prozess-/Gruppenidentitäten auf Abwesenheit. Er sendet keine
Recoverysignale anhand bloßer Prozesskennungen. Ein Launcherbruch ohne
unabhängigen Linux-Abschlussnachweis bleibt UNKNOWN, kein Wiederholungslauf.

## Gemeinsame Grenzen und Gegenproben

Die einzige tatsächliche Aufnahme hält 20 Sekunden reguläre Deadline ab ihrer
Vorbereitung und höchstens zehn Sekunden kumulativen Cleanup ein. Davon sind
höchstens sechs für Linux-Cleanup und vier für Windows-Abschluss samt unabhängiger
Absenzprüfung reserviert. Die 4096 technischen Ein-/Ausgabeschritte enthalten
vor Start fest 1088 Schritte des Kindes, 1024 Aufräumschritte einschließlich 32 reservierter Abschlussoperationen und 512 Schritte für Vorbereitung, Launcher
und Readback; Readback ist die unabhängige Rückprüfung. Hinzu kommen keine neuen
Schrittbudgets. 64 Schritte ohne Fortschritt und 65536 tatsächliche Ausgabe-
und stderr-Bytes bleiben maßgeblich, ebenso alle Metadata-/Fragment-/Zeilencaps.
Ein äußerer Timeout oder zusätzlicher WSL-Aufruf erneuert diese Grenzen nicht.

Portable Gegenproben prüfen vollständigen positiven Vergleich, fehlende,
zusätzliche, umgestellte und doppelte Fragmente, ASCII-/Zeilen-/Gesamtgrenzen,
Ordinal-/Dezimalformen, Hash-/Kanonizitätsfehler, semantische Feld- und
Kontextabweichungen, reine Metadata ohne Bodyfreigabe, falsche Interpreter,
falschen Dateieinstieg und Quellenpinabbruch vor Folgeimporten.

Die sechs eigenen nativen Kindfälle sind: passendes Profil mit geplantem Halt,
semantisch falsches Profil, Teilreport mit frühem EOF (End of File; Ende eines
Eingabestroms), stiller Timeout, Leaderexit mit eigenem pipehaltendem Nachfahren
und Fehler nach Start vor Metadata. Eine Sentinelmarke am Folgepfad prüft die
ausbleibende Bodyfreigabe. Diese synthetischen Fälle verwenden eigene Profile
und eine andere Protokollnonce. Erst nach ihrem Erfolg und unabhängiger
Absenzprüfung darf genau der vorgewählte Runner starten.

## Tatsächliches Ergebnis des dritten Standes

Status `CLOSED_REJECTED_NATIVE_PREIMPORT_EOF`: Die begrenzte Aufnahme ist
abgeschlossen und abgelehnt. EOF bedeutet End of File, also Ende eines
Datenstroms. Es liegt kein vollständiger tatsächlicher Profilreport vor.

Der erste und zweite Stand erhielten keine Lauffreigabe und wurden nie
operativ ausgeführt. Ihre Befunde und Quellen bleiben privat erhalten.
Der dritte schloss die Befunde im unabhängigen Quellen-/Test-/Aufrufreview:
lückenloser Alarm über Zielimporte und Vorbereitung, konservative Übergabe
der ursprünglichen Deadline, feste Außenreserve mit
224 Windows-, 64 Start-, 64 Vorbereitungs-, 64 Prüfstart- und 96 Rückprüfschritten,
explizite Startbelege, vorab reservierter Cleanup, phasenübergreifende
Sentinelprüfung und getrennte erste Fehlerursache. Danach wurde genau der
freigegebene gestufte Aufruf einmal ausgeführt.

Alle 19 portablen Prüfmethoden bestanden ohne übersprungene Tests. Alle sechs
nativen Gegenfälle lieferten das erwartete Ergebnis: passendes Profil,
Profilabweichung, früher Teilreportabschluss, Timeout, Leaderexit mit eigenem
Nachfahren und Fehler nach Start. Sämtliche eigenen Prozessgruppen wurden
aufgeräumt und anschließend unabhängig als abwesend nachgewiesen. Ein Prüflauf
verbrauchte sieben synthetische Prozesse einschließlich des einen Nachfahren.

Erst danach startete der unveränderte ausgewählte Runner genau einmal als
absolute Datei. Er schloss seinen Ausgabestrom vor dem Profilreport:
`EARLY_EOF` bleibt erste und abschließende Fehlerursache. Auf stdout, dem
regulären Ausgabestrom, kamen null Bytes; auf stderr, dem Fehlerausgabestrom,
865 Bytes. Gespeichert wurden ausschließlich Größen und Hashes, keine
nativen Reportbytes oder tatsächlichen Profilwerte. Diese Metadaten belegen
keine konkrete Interpreter-, Quellen- oder Protokollursache. Die Ursache
bleibt UNKNOWN, also mit der vorliegenden Evidenz unbekannt.

Der anschließende eigene Abschluss war nachgewiesen: beide Datenströme
beendet, Leader und eigene Nachfahren abgeholt, Gruppe und Kinder abwesend,
ursprünglicher Prozesszustand wiederhergestellt. Der Linux-Cleanup benötigte
234563 Nanosekunden, die unabhängige Rückprüfung 49 von 96 reservierten
Schritten. Einschließlich aller vorab reservierten Anteile wurden 2792 von
4096 Kanalschritten belastet; Windows verwendete 180 von 224 Außenoperationen.
Vier WSL-Aufrufe und ihre vier Windows-Jobs sind vollständig beendet; kein
aktiver eigener Jobprozess und keine offene Besitzsperre. Es wurden keine
zusätzlichen Recoverysignale oder Wiederholungsläufe benötigt.

Der Prozesslauf dauerte insgesamt 10,797 Sekunden und belastete eine volle
200-Sekunden-Reservierung des gemeinsamen Rahmens. Drei von höchstens sechs
Quellenständen, Checkpoint nach zwei, ein synthetischer Prüflauf und genau ein
nativer Runner-Versuch sind verbraucht. Modell- und Koordinationsverbrauch
bleiben UNKNOWN. Der einzige ausgewählte Versuch ist damit ausgeschöpft;
freie Quellenstände oder äußere Restzeit erlauben keinen zweiten Versuch.
Das geschlossene Auswahlpaket bleibt unverändert. Diagnose oder Korrektur
mit weiteren nativen Versuchen benötigt eine ausdrücklich freigegebene neue
Grenze; bis dahin kein weiterer Workerstart.

Der unabhängige Ergebnisreview ist ohne offene priorisierte Befunde geschlossen und gibt ausschließlich den Dokumentationsabschluss frei. Lokale Dokumentationsprüfung und reguläre
Integration dieser abgelehnten Beobachtung stehen noch aus. Erfolgreicher
Cleanup heilt den fehlenden Profilvergleich nicht.

## Nachweisgrenze und vollständiger Abschluss

Auch ein positiver Abschluss belegt ausschließlich diese frische Profilaufnahme
und ihren eigenen Cleanup. Kein vollständiger Handshake, kein `INPUT_COMPLETE`,
kein `SESSION_END` mit Counts und Kanalhash, kein regulärer Workerexit mit Code
null und kein `CLOSED_SESSION_CHANNELS`. Proxy und Harness, also Vermittlung und
Prüfrahmen, werden nicht gestartet. Kandidatenimporte, SQL, neue Installation,
physischer Trust und Messmethode bleiben ausgeschlossen beziehungsweise offen.
DEC-076 gilt für vertrauenswürdige Schulungsquellen; alle bisherigen Runtime-,
Trust-, Importbyte- und Methodenattestierungsflags bleiben false.

Nach unabhängiger Befundschließung und passenden lokalen positiven/negativen
Prüfungen folgen aktuelle grüne Head-/Base-Gates, regulärer Merge, frische
Main-Gates, vollständige Baumübernahme, Synchronisation und eigene lokale/
Remote-Branchbereinigung. Der zugehörige Pull Request bindet den tatsächlichen
Abschluss. Private Helfer, Reservierungen, Fehler und Ergebnisse bleiben erhalten.
