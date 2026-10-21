# DGN-007 – Plan für die erste native Profilbeobachtung

DGN-007 bezeichnet die Diagnose-Demo mit getrennten Quellen- und Laufnachweisen.
Dieser Plan bereitet die erste tatsächliche Aufnahme des vorgewählten
Runnerprofils vor. Runner bezeichnet die vollständige Ausführungssteuerung.
Der Plan startet keine Prozesse und erteilt kein Lauf-GO.

## Abgeschlossene Auswahl als unveränderlicher Eingang

[PR286](https://github.com/gecompat/SQL_PerformanceSchulung/pull/286) ist in
Main `a714c7d578a18d2fa31fe862bc1e184ed1037444` vollständig abgeschlossen:
unabhängiger Quellen-/Test- und Ergebnisreview ohne offene Befunde, sieben
grüne Head-, fünf grüne Base- und fünf frische grüne Main-Prüfungen,
vollständige Baumübernahme, Synchronisation und eigene Branchbereinigung.
Head ist der geprüfte PR-Commit, Base dessen Main-Basis.

Das [vollständige Auswahlpaket](DGN_007_WORKER_PROFILE_SELECTION_REVIEW.md#ergebnis-des-achten-standes-vollständiges-auswahlpaket)
enthält drei separat vorgewählte Workerprofile und drei erzeugte, bislang
nicht ausgeführte Scripts. Alle 40 Datengegenproben und drei ursprünglichen
Ganz-AST-/Fitmethoden bestanden; AST bedeutet Abstract Syntax Tree, abstrakter
Syntaxbaum. Der Status bleibt `SOURCE_SELECTED_DECLARATIONS_ONLY`, also eine
quellenbegründete Deklarationsauswahl. Die tatsächliche Laufzeit wurde damit
nicht beobachtet. Acht von hart acht Auswahlständen bleiben abgeschlossen;
dieser Plan ändert keine Auswahlbytes und eröffnet keinen neunten Stand.

## Endlicher Umfang dieses Planungsschnitts

Der kontinuierliche menschliche Auftrag umfasst die weitere operative
Anbindung. Ein Implementierungsverantwortlicher root und derselbe unabhängige
Reviewer führen genau diesen Dokumentationsschnitt aus: eingefrorener Entwurf
als Checkpoint, höchstens eine zusammenhängende Nacharbeit, harte Grenze zwei
Entwurfsstände einschließlich Review, lokaler Prüfungen, Koordination und
vollständiger Integration. Verbrauch UNKNOWN, also nicht verlässlich gemessen.
Danach kein dritter Entwurf ohne ausdrückliche Erweiterung.

Geändert werden nur dieser Plan und seine drei Einstiege in Ausführungsstand,
Masterplan und Backlog. Keine Generator-, Codec-, Kontroll-, Test- oder
Runtimequelle wird geändert oder importiert. Keine Probe-, Worker-, Linux-/
WSL- oder SQL-Ausführung; WSL bedeutet Windows Subsystem for Linux. Bestehende
grüne Paket- und Runnermodelle werden nicht wiederholt. Private Artefakte,
Fehlerstände und fremde Ressourcen bleiben erhalten.

## Genau eine nächste Beobachtungsfrage

Der spätere Implementierungsschnitt soll ausschließlich diese Frage beantworten:
**Entspricht der erste vollständige, frisch aufgenommene PRE_IMPORT-Report des
Runner-Scripts seiner separat vorgewählten Installation und seinem gesamten
Modulprofil?** PRE_IMPORT bezeichnet den Zeitpunkt vor Kandidatenimports.
S15 umfasst alle 15 Installationsfelder, P11 alle elf Felder je Modul. Kein
Modul oder Feld darf aus einer abweichenden Beobachtung ins Soll übernommen
werden. Proxy und Harness, also Vermittlung und Prüfrahmen, folgen erst nach
vollständigem Abschluss dieses eigenen Schnitts.

Der bestehende [Profilbindungsvertrag, §16](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#16-konkrete-operative-bootstrap--und-kanalreihenfolge)
und die [Auswahlprüfung](DGN_007_WORKER_PROFILE_SELECTION_PLAN.md#prüfung-und-übergang-zur-ausführung)
bleiben maßgeblich. Der spätere konkrete Quellen-/Aufrufplan bindet insbesondere:

1. **Unveränderte Eingänge.** Das private Auswahlpaket, dessen festen
   Eingangscommit, ursprüngliche Profilbytes, Runner-Scriptbytes und alle
   Quellenabhängigkeiten vor Import und erneut vor Start prüfen. Neue
   Dokumentationscommits werden nicht stillschweigend zum Eingangscommit.
   Die Auswahl bleibt eingefroren; ein abweichender Pin stoppt den Versuch.
2. **Tatsächlichen Scripteintritt.** Den vorgewählten absoluten Scriptlocator
   unter dem vorgewählten isolierten Linux-CPython 3.12 mit `-I -S -B` verwenden:
   isolierter Modus, keine Site-Initialisierung, keine Bytecodedateien. Die
   Installation, Patchversion, Toolidentitäten und Startumgebung sind vorab
   separat zu binden. Ein Aufruf mit `-c` ist kein gleichwertiger Datei-Einstieg.
   Der vorhandene [Kanalstarter](../../Tests/Tools/dgn007_session_channel.py)
   verwendet `-c`; sein erfolgreicher Modelllauf belegt diesen Eintritt nicht.
3. **Fehlende eigene Dateien.** Für jeden ausgewählten Locator prüfen, ob die
   erforderlichen Originalbytes tatsächlich vorhanden sind. Nur vorher
   abwesende, einzeln übernommene Ziele mit den bereits gewählten Bytes
   materialisieren. Bestehende C8-Artefakte nicht überschreiben oder umbenennen;
   neue Helferquellen außerhalb ihres eingefrorenen Pakets halten. Besitzer,
   Hash, Größe und spätere Behandlung jeder neuen Datei vor dem ersten Write
   festlegen. Ein anderer Locator verlangt eine neue Auswahlentscheidung.
4. **Begrenzte Eingangsphase.** Nur den bereits gebundenen DGNC-Header und die
   vollständige Metadata senden; DGNC bezeichnet die festgelegte Eingangsform.
   Die neun angekündigten Rawbodies, also ursprünglichen Kandidatenbytes,
   bleiben vollständig beim Parent, dem steuernden Prozess. Kein
   `BODY_RELEASE`, keine Bodies, kein `BODY_END`, kein `IMPORT_RELEASE` und
   keine Kandidatenoperation in diesem Beobachtungsschnitt.
5. **Vollständige Aufnahme.** Die tatsächlich gelesenen stdout-/stderr-Bytes
   gemeinsam vor Speicherung buchen. Den gesamten Profilbeginn, alle
   geordneten Fragmente und den Profilabschluss innerhalb ihrer bestehenden
   Größen-/Sequenzgrenzen aufnehmen. Den vorhandenen Decoder und vollständigen
   Profilrecordvergleich gegen separat gehaltene Erwartung und Kontext nutzen.
   Fehlende Felder nicht ergänzen; ein Hash, Teilreport oder Bool genügt nicht.
6. **Geplanter Halt und eigener Cleanup.** Nach vollständiger Aufnahme den
   weiterhin vor der Bodyfreigabe wartenden eigenen Worker kontrolliert stoppen.
   Ein gültiger Profilreport ist kein vollständiger Handshakeabschluss. Weder
   `INPUT_COMPLETE` noch `SESSION_END` werden erwartet oder synthetisch ergänzt:
   ersteres bestätigt vollständigen Eingang, letzteres Counts und Kanalhash.
   Der geplante Gruppenstop ist getrennt von einem regulären Exit mit Code null
   zu dokumentieren. Kein `CLOSED_SESSION_CHANNELS` allein aus dieser Teilphase.

## Prozessbesitz, Grenzen und Fehlerpriorität vor jedem Lauf schließen

Das konkrete spätere Paket benötigt eine unabhängige Auswahl-/Quellen-/
Testprüfung und ein ausdrückliches einmaliges Lauf-GO für den exakten Aufruf.
Vor neuer Implementierung wird sein gemeinsamer endlicher Quellen-/
Versuchsrahmen mit Checkpoint und harter Grenze festgelegt. Dieser
Dokumentationsrahmen gewährt keine zusätzlichen Implementierungsversuche.

Der spätere Laufplan muss alle vorbereitenden Pin-, Dateianlage-, Plattform-,
Start-, Transfer-, Vergleichs- und Absenzaufrufe enthalten. Er reserviert
regularen Ablauf und Cleanup getrennt unter denselben bereits geltenden
Grenzen: 20 Sekunden regulär ohne Neustart der Deadline, höchstens zehn
Sekunden kumulativen Cleanup, 4096 technische Ein-/Ausgabeschritte,
64 Schritte ohne Fortschritt und 65536 tatsächliche Ausgabebytes. Bestehende
Header-, Metadata-, Fragment-, Zeilen- und Transfercaps bleiben gleichzeitig
maßgeblich. Ein Plattformvorlauf erhält kein ungezähltes Zusatzbudget.
Ein äußerer Timeout ersetzt weder diese Zähler noch einen Absenzbeleg.

Windows-Launcher und Linux-Owner sowie dessen eigene neue Workerprozessgruppe
müssen getrennt gehalten, begrenzt gestoppt und auf Abschluss beziehungsweise
Absenz geprüft werden. Die bestehenden Windows-Jobs aus PR286 qualifizieren
keinen Linux-Cleanup. Eigener Leaderanker, Gruppenbindung, Reap, tatsächliche
Pipeabschlüsse, unabhängige frische Kinder-/Gruppenabsenz und Restore sind
vorab konkret zu lösen. Reap bezeichnet das kontrollierte Abholen des
Prozessendes. Keine fremde Namens-/PID-Suche; PID ist die Prozesskennung.
Ein früher Launcherexit oder eine harte Unterbrechung ohne unabhängigen
Linux-Abschlussnachweis bleibt UNKNOWN und erlaubt keinen Wiederholungslauf.

stdout und stderr werden während sämtlicher Schreibphasen gemeinsam begrenzt
drainiert, also laufend geleert. EOF bedeutet End of File, das tatsächliche Ende
der jeweiligen gehaltenen Pipe. EOF, Profilabschluss, Workerexit und Cleanup
sind getrennte Beobachtungen. Kein Erfolg aus einem Launcherexit, geschlossener
erster Pipe oder passendem Profil bei verlorenem Prozessbesitz. Fehler bleiben
gesetzt; ungeklärter Start, Bindungsverlust oder Cleanupfehler werden nicht
durch spätere Abwesenheit zu einem erfolgreichen ursprünglichen Lauf.

## Verbindliche Gegenproben und Ergebnisgrenze

Vor einem tatsächlichen ausgewählten Workerstart sind wenigstens folgende
Fragen im konkreten Quellen-/Testplan zu schließen:

- falscher Interpreter, Eintritt oder Quellenpin: Ablehnung vor Workerfreigabe;
- fehlender, zusätzlicher oder abweichender Profilwert und falscher Kontext:
  vollständige Ablehnung gegen unveränderte Erwartung;
- Teil-, Doppel-, umgeordnete oder fremde Fragmente sowie Byte-/Zeilenoverflow:
  keine Teilaufnahme und keine Folgefreigabe;
- vorzeitiges EOF, blockierter Rückkanal oder No-progress: begrenzter Stop mit
  eigener Bereinigung; keine nachträgliche Fortsetzung;
- Leaderexit mit offen gehaltenen Pipes beziehungsweise eigenem Nachfahren:
  kein Cleanup-PASS aus dem Exit, tatsächliche Gruppen-/Kinderabsenz nötig;
- Fehler nach Start oder während des geplanten Stops: unveränderte dominante
  Fehlerpriorität, keine verlorenen Prozesse oder fremde Bereinigung;
- Sentinel am Body-/Importpfad: belegen, dass keine Freigabe und keine
  Kandidatenoperation erfolgt. Ein Sentinel ist eine beobachtbare Testmarke.

Synthetische Gegenproben sind von der einzigen separat freigegebenen frischen
Runneraufnahme zu unterscheiden. Eine Abweichung macht die Auswahl nicht
nachträglich richtig. Änderungen an den abgeschlossenen Auswahlbytes oder ein
erneuter Auswahlpaketlauf wären eine ausdrückliche Erweiterung dieses alten
Scopes; der neue Beobachtungsrahmen erlaubt sie nicht.

Ein späterer positiver Abschluss könnte ausschließlich die konkret gehaltene
frische Profilaufnahme und ihren eigenen Cleanup belegen. Tatsächlich
verwendete Kandidatenbytes, vollständige Loaderfolge, SESSION_END, drei
Workerabschlüsse, physischer Installationstrust und Messmethode bleiben
getrennte offene Nachweise. DEC-076 gilt weiter: vertrauenswürdige
Schulungsquellen ohne Schutz gegen gezielten Austausch des Kontrollcodes.
Keine Sandbox-, Produktions-, SQL- oder pauschale Runtimefreigabe; die
bestehenden Attestierungsflags bleiben unverändert false.

## Abschluss dieses Planungsschnitts

Der unabhängige Review prüft Aufgabenabgrenzung, unveränderte Auswahl,
Profilvollständigkeit, geplanten Halt, fehlende Wirkungsfreigaben, Prozessbesitz
und Gegenproben. Lokal werden alle vier geänderten Dokumente auf Datenschutz,
UTF-8, relative Markdownziele und Whitespace geprüft. Nach Befundschließung
folgen aktuelle grüne Head-/Base-Gates, reguläre Integration, frische Main-Gates,
vollständige Baumübernahme, Synchronisation und eigene Branchbereinigung.
Der zugehörige Pull Request bindet den tatsächlich erreichten Abschluss.
