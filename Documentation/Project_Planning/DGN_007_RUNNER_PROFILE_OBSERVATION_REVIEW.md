# DGN-007 – erste frische Runnerprofilaufnahme

DGN-007 bezeichnet die Diagnose-Demo mit getrenntem Quellen- und Laufnachweis.
Runner ist die vollständige Ausführungssteuerung. Der
[Beobachtungsplan](DGN_007_NATIVE_PROFILE_OBSERVATION_PLAN.md) ist über
[PR287](https://github.com/gecompat/SQL_PerformanceSchulung/pull/287) vollständig
in Main `3266c4763c0e452f8752cd792473308f87ef25df` abgeschlossen: unabhängiger
Review, lokale Dokumentationsprüfung, sieben grüne Head-, fünf grüne Base- und
fünf frische Main-Prüfungen, vollständige Übernahme und eigene Branchbereinigung.

## Fehlerbehebung und vollständiger Profilvergleich vom 22. Oktober 2026

Der vorzeitige Ausgabestromabschluss `EARLY_EOF` tritt im korrigierten,
instrumentierungsfreien Versuch nicht mehr auf. Der vollständige vor den
Kandidatenimports aufgenommene Profilreport stimmt mit der separat gewählten
Installation und allen 85 Moduldeklarationen überein. Sein Status lautet
`OBSERVED_PREIMPORT_PROFILE_ONLY`: ausschließlich das Profil vor den Imports
wurde beobachtet. Der Report enthält 9056 Bytes; insgesamt wurden 9289
Ausgabebytes und keine Fehlerausgabebytes gelesen. Kein Modul oder Feld wurde
aus einem abweichenden Istlauf in die Erwartung übernommen.

Korrekturen auf zwei Ebenen waren erforderlich. Die Runnerquelle
behandelt beim Dateieinstieg das eingebaute Modul `builtins` über sein gehaltenes
Wörterbuch und besitzt vor der Initialisierung einen kontrollierten
Ablehnungspfad. Der private Beobachtungshelfer legt zusätzlich die vollständige
Kindumgebung auf `LANG=C`, `LC_ALL=C` und `HOME=/` fest. Ohne `HOME` lädt die
verwendete Python-Bibliothek beim Import von `sysconfig` über die
Benutzerpfadauflösung zusätzlich `pwd`, das Modul für die Benutzerverwaltung.
Diese Umgebungsabhängigkeit fehlte in der zuvor quellenbegründeten Auswahl.
Die Korrektur erhält die Liste und bindet ihre Voraussetzung ausdrücklich;
sie entfernt keine Cacheeinträge und lockert keinen Profilvergleich.

Die Diagnose hatte zuerst eine frühe Profilablehnung vor der späteren
Runnerbindung gezeigt. Der begrenzte Trace im 17. Stand lokalisierte deren
erste Bedingung am Vergleich der Modulanzahl. Die unveränderten gepinnten
Bibliotheksquellen begründen den zusätzlichen Importpfad. Sechs reine
Gegenproben führen genau diese Funktionssyntaxbäume mit eigenen Providern im
Speicher aus: Die alte Umgebung verlangt `pwd`, die feste Umgebung vermeidet
den Import; Text-, Bytes- und benannte Benutzerpfade sowie die tatsächliche
Drei-Felder-Startumgebung werden getrennt geprüft. Es finden keine echten
Benutzerabfragen statt. Erst danach erfolgte der unabhängig freigegebene
native Lauf mit der unveränderten, nicht instrumentierten Runnerquelle.

Beide neuen Runnergegenproben scheitern am alten Generator. Alle 23 lokalen
Runnermodelle und die sechs Umgebungsgegenproben bestehen. Der unveränderte
volle Modelllauf und die sechs bereits erfolgreichen synthetischen nativen
Kanalgegenfälle wurden nicht erneut ausgeführt. Frühere Fixture-, Diagnose-,
Syntax- und Größenfehler bleiben mit ihren abgelehnten Ständen erhalten.

Nach vollständigem Vergleich wurde der weiterhin vor der Bodyfreigabe
wartende eigene Worker geplant gestoppt. Das ist kein regulärer Workerexit
mit Code null und kein vollständiger Sitzungshandshake; sein Exitstatus bleibt
`UNKNOWN`, also in diesem Nachweis nicht bestimmt. Beide tatsächlichen
Datenstromenden, eigener Gruppenabschluss und Wiederherstellung sind bestätigt;
der unabhängige Absenzprüfer benötigt 57 von 96 Schritten ohne
Wiederherstellungssignale. Beide Windows-Jobs sind leer und beendet, keine
offene Besitzsperre. 2804 technische Ein-/Ausgabeschritte und 13 Cleanupschritte
liegen innerhalb der unveränderten Grenzen.

Der gemeinsame Checkpoint steht bei 18 Quellen-/Test-/Aufrufständen, neun
nativen Versuchen, drei synthetischen Prüfläufen mit 21 reservierten Prozessen,
24 Aufrufen des Windows Subsystem for Linux (WSL) und 1400 reservierten
Prozesssekunden. Vor der früheren harten Grenze wurde der endliche Rahmen
unabhängig auf höchstens 20 Stände, zehn native Versuche, 26 WSL-Aufrufe und
1500 Sekunden fortgeschrieben. Alte Zählungen wurden nicht zurückgesetzt;
Modell- und Koordinationsverbrauch bleiben UNKNOWN, also nicht verlässlich
gemessen. Weitere native Versuche sind für diesen Abschluss nicht geplant.

Die Produktänderung und dieser Ergebnisstand werden auf
`codex/dgn007-early-eof-fix` bis zu unabhängig geschlossenen Befunden, lokalen
Dokumentationsprüfungen, aktuellen grünen Head-/Base-/Main-Prüfungen,
vollständiger Übernahme und eigener Branchbereinigung geführt. Head bezeichnet
den geprüften Pull-Request-Commit, Base dessen Main-Basis. Anschließend folgt
gemäß menschlichem Auftrag die aktuelle AI Repository Foundation.

Die ursprünglichen Profilbytes, Installationsquellen, Elternkontext und
Protokollkennung bleiben erhalten. Es wurden nur Header und Metadaten gesendet,
keine angekündigten Kandidatenbytes, keine Body- oder Importfreigabe und kein
SQL ausgeführt. Die Felder für Runtime-, Trust-, Importbyte- und
Methodenbestätigung bleiben falsch; ein passender Profilreport erteilt diese
weitergehenden Nachweise nicht. Die folgenden Abschnitte sind historische
Fehler- und Abschlussnachweise.

## Diagnosecheckpoint vom 22. Oktober 2026

Nach dem historischen Abschluss aus PR288 hat der Mensch zusätzliche native
Versuche zur Diagnose und Behebung von `EARLY_EOF` freigegeben. EOF bedeutet
End of File, hier das vorzeitige Ende des Ausgabestroms. Ein
Implementierungsverantwortlicher und derselbe unabhängige Reviewer haben die
Arbeit auf `codex/dgn007-early-eof-fix` fortgeführt. Die ursprünglichen
Auswahlbytes, Fehler und abgelehnten Reviewstände bleiben erhalten.

Die Produktänderung ergänzt einen kontrollierten Runner-Ablehnungspfad und
behandelt das ursprüngliche `builtins`-Modul beim Python-Dateieinstieg als dessen
gehaltenes Wörterbuch. Zwei Gegenproben scheitern am alten Generator; alle 23
lokalen Runnermodelle bestehen am korrigierten Stand. Der volle lokale Modelllauf
benötigte 532,487 Sekunden. Er wurde am unveränderten Stand nicht wiederholt.
Die sechs synthetischen nativen Kanalgegenfälle bestanden im fünften Stand;
der vorherige Fixturefehler und dessen nicht gestarteter Kindfall bleiben als
Fehlschlag erhalten. Keine zusätzliche vollständige Suite nach Ausschöpfung
der drei gemeinsam gezählten Prüfläufe.

Ein gesonderter Diagnosehelfer war ebenfalls fehlerhaft: Seine Writerqualifikation
lehnte mit Exitcode 13 ab. Dieser Code unterscheidet die beiden dort geprüften
Bedingungen nicht. Der letzte Stand bindet stattdessen den ursprünglichen nativen
Schreibdescriptor vor der Verwendung und prüft ihn vor jedem Schreibversuch.
Neun reine Gegenproben bestehen ohne übersprungene Tests, einschließlich alter
Ablehnung gegenüber korrigierter Bindung am selben Speicherschreiber. Ein im
Review gefundener fehlender Konstantenpool im Fehlerfixture wurde vor Ausführung
ergänzt; Prüferwartungen blieben unverändert. Quelle 131038 von höchstens 131072
Bytes, unveränderte Profilrohbytes, Gleichheit des gesamten abstrakten Syntaxbaums
gegen die separat hergeleitete Transformation und fünf vollständige Paketformen
mit zusammen 28255 Bytes sind geprüft. Diese Diagnosequelle ist kein Produktfix.

Nach unabhängigem exaktem Quellen-/Test-/Aufruf-GO startete der letzte
Diagnoseworker genau einmal. Die sechs Rückgaben für Kontrollquelle, Profilbindung,
Runnerbindung, Eingangsbindung, Reportbindung und Versiegelung waren jeweils
erwartet mit Fehlerlabel `NONE`. Der anschließende Runneraufruf lehnte mit
`RUNNER_SOURCE_BINDING` ab. Die innere Bindungsbedingung ist noch nicht
unterschieden; ein Einfluss der Instrumentierung ist nicht separat ausgeschlossen.
Es gibt keinen vollständigen Profilreport und keinen Nachweis der Behebung.

Erste und abschließende Kanalursache bleibt `EARLY_EOF`; normaler eigener Exitcode
1, null Bytes auf stdout (regulärer Ausgabestrom), 136 Diagnosebytes auf stderr
(Fehlerausgabestrom). Gespeichert sind nur geschlossene Labels, Stufen, Größen und
Hashes, keine tatsächlichen Profilwerte oder Reportbytes. Eigener Cleanup,
beide Stromabschlüsse, Gruppen-/Kinderabsenz und Wiederherstellung sind bestätigt.
Linux-Cleanup 302536 Nanosekunden, 2773 von 4096 belasteten Kanalschritten;
Windows 214 von 224 Außenoperationen, unabhängige Rückprüfung 65 von 96 Schritten,
keine Recoverysignale. Beide Windows-Jobs haben null aktive Prozesse, keine
offene Besitzsperre. Der letzte Flug dauerte 8,094 Sekunden, seine volle
100-Sekunden-Reservierung bleibt belastet.

Die unabhängig geprüfte Fortführung des endlichen Rahmens erhöhte vor Stand acht
die Quellengrenze auf zehn und vor Stand zehn auf zwölf, mit Checkpoint nach
Stand zehn und Versuch fünf. Jetzt sind zwölf Quellen-/Test-/Aufrufstände,
sechs native Versuche, drei synthetische Prüfläufe mit 21 reservierten Prozessen,
18 WSL-Aufrufe und 1100 reservierte Prozesssekunden ausgeschöpft. WSL bedeutet
Windows Subsystem for Linux. Auch die im Review abgelehnten, nicht ausgeführten
Stände acht und elf zählen. Verbrauch für Modelle und Koordination bleibt UNKNOWN,
also nicht verlässlich gemessen. Keine neue Implementierung, Wiederholung oder
automatische Grenzanhebung. Private Originale und Evidenz bleiben erhalten.

Die offene fachliche Aufgabe ist die konkrete Ablehnung innerhalb des Runneraufrufs
nach erfolgreicher Versiegelung. Eine neue menschliche Entscheidung über einen
endlichen Diagnose-/Korrekturrahmen ist erforderlich. Unabhängiger Review,
passende Gegenproben, lokale Tests und aktuelle grüne Head-/Base-/Main-Prüfungen
sowie reguläre Integration und Übernahmenachweis bleiben offen. Kein Pull Request
oder Merge für diesen Stand; der unübernommene Arbeitsbranch bleibt erhalten.
Die folgenden Abschnitte dokumentieren den historischen ersten Versuch, nicht
den aktuellen Restumfang. Keine Body-/Importfreigabe, kein Runtime- oder SQL-Nachweis.

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

Der unabhängige Ergebnisreview ist ohne offene priorisierte Befunde geschlossen und gibt ausschließlich den Dokumentationsabschluss frei. Die lokale Prüfung aller vier Dokumente bestand Datenschutz, striktes UTF-8, 620 relative Linkziele und Whitespace. [PR288](https://github.com/gecompat/SQL_PerformanceSchulung/pull/288) führt diesen Dokumentationsabschluss bis zur regulären Integration; seine aktuellen Head-/Base-/Main-Prüfungen, Baumübernahme und eigene Branchbereinigung sind über den Pull Request und frische Git-Evidenz nachzuweisen. Erfolgreicher
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
