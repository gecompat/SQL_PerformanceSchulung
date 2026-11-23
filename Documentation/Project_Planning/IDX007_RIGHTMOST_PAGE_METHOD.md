# IDX-007 – Methodenentwurf zur rechten Blattseite

| Merkmal | Wert |
|---|---|
| Status | `METHOD_DRAFT` – der kombinierte XE-/Seitenkettennachweis wurde auf drei gepinnten Builds lokal demonstriert; unabhängige Methodenprüfung und Demo-/Qualifikationsfreigabe bleiben offen |
| Lernziel | Eine wartende `PAGELATCH_EX`-Seite nur dann als letzte Blattseite eines bestimmten Indexes einordnen, wenn die Seitenmetadaten diese Zuordnung tragen |
| Lehrpfad | Vorhandene [IDX-007-Lehrnotiz](../Curriculum/LAST_PAGE_INSERT_CONTENTION_LESSON.md); kein neues Lernziel |
| Vertrag | [Offline-Prüfer](../../Tests/Static/idx007_last_page_contract.py) bleibt ein Konsistenzfilter für caller-gelieferte Werte |
| Quellen | `SRC-163`, `SRC-168`–`SRC-172`, `SRC-174` |

## Aussage, die geprüft werden soll

Ein Last-Page-Befund benötigt mindestens zwei eigene Sessions, die im engen
Messfenster wegen `PAGELATCH_EX` auf derselben Datenbank-/Datei-/Seitenadresse
warten. Die Seite muss zum synthetischen Zielobjekt, Index und Partition
gehören und Blattebene haben. Zusätzlich muss eine unabhängige aktuelle
Seitenkettenaufnahme zeigen, dass die Zielseite die rechte Kante der Blattkette
bildet. Ein sequentieller Schlüssel, `leaf_insert_count`, Indexoption oder
`page_level = 0` allein reicht nicht.

`sys.fn_PageResCracker` kann `page_resource` in Datenbank-, Datei- und
Seitennummer zerlegen. `sys.dm_db_page_info` liefert für genau eine Seite
Headerinformationen einschließlich Objekt, Index, Partition, Blattebene und
Vor-/Nachfolgeradressen. Diese Quellen bilden einen Startpunkt, aber keine
atomare Mehrseitenaufnahme. Zwischen zwei Funktionsaufrufen können Einfügungen,
Splits oder andere Strukturänderungen Blattlinks ändern. Eine Momentaufnahme
beweist keinen stabilen Zustand außerhalb ihres kurzen Erfassungsfensters.

## Vorgeschlagene Seitenkettenprüfung

1. **Wait-Ressource binden:** Für jede beobachtete eigene wartende Session die
   aktuelle Request-/Task-ID, `PAGELATCH_EX`, `wait_duration_ms`, den UTC-
   Capturebereich und die per `page_resource` entschlüsselte
   Datenbank-/Datei-/Seitenadresse erfassen. `PAGEIOLATCH_EX`, fehlende
   `page_resource` oder eine nicht zur eigenen Session gebundene Adresse sind
   kein Treffer. Weil `sys.dm_os_waiting_tasks` selbst keine `request_id`
   ausgibt, wird `waiting_task_address` eindeutig an
   `sys.dm_os_tasks.task_address` gebunden; daraus stammen Session-, Request-
   und Execution-Context-ID. Null oder mehrere Taskmatches, geänderte IDs oder
   fremde Sessions ergeben `NOT_PROVEN`. Die Verbindung nur über `session_id`
   reicht insbesondere bei mehreren gleichzeitigen Requests nicht.
2. **Zielseite prüfen:** `sys.dm_db_page_info` im vorgesehenen Zielkontext auf
   genau diese Adresse anwenden. Datenbank, Objekt, Index, Partition und
   `page_level = 0` müssen zum markergebundenen synthetischen Ziel passen.
   Nicht-Blattseiten, Heapseiten und systemfremde Objekte widerlegen den
   Last-Page-Claim.
3. **Vorwärtskette verfolgen:** Ab der Wait-Seite die `next_page_file_id`-/
   `next_page_page_id`-Adresse schrittweise lesen, bis ein vom Review
   bestätigter Terminalzustand erreicht wird. Ein caller-gelieferter Endmarker allein ist kein bestätigter Terminalzustand. Jede Seite muss zum selben
   Datenbank-/Objekt-/Index-/Partitions- und Blattseitenkontext gehören. Der
   vorwärts gelesene Link und der Rücklink des Nachfolgers müssen zueinander
   passen. Eine Seitenadresse darf nicht zyklisch wiederkehren.
4. **Begrenzen:** Vor dem ersten Nachfolgeraufruf eine feste maximale Zahl
   gelesener Seiten festlegen. Eine unabhängige Seitenanzahl derselben
   Indexpartition kann als Plausibilitätsgrenze dienen, muss aber im
   Methodenreview gegen Inserts und Seiten-Splits abgeglichen werden. Wird
   irgendeine Grenze erreicht, ohne den bestätigten Terminalzustand zu finden,
   folgt `NOT_PROVEN`; die Schleife darf nicht stillschweigend weiterwachsen.
5. **Wait erneut binden:** Nach dem Kettenlauf die eigene Wait-Gruppe erneut
   lesen. Die gleiche Wait-Adresse und der gleiche Zielkontext müssen innerhalb
   des engen Capturefensters wieder vorkommen. Die beiden Aufnahmen werden als
   begrenzte Klammer um die Kettenlesung berichtet, nicht als atomare DMV-
   Transaktion oder exakter gemeinsamer Enginezeitpunkt.
6. **Ergebnis begrenzen:** Nur wenn beide Wait-Ränder dieselbe Zielseite
   melden, der einzelne dazwischenliegende Kettenlauf auf dieser Seite
   konsistent am bestätigten Ende ankommt und alle Seitenmetadaten vollständig
   sind, darf das Ergebnis höchstens lauten: „Die Wait-Seite war bei den
   umschließenden Wait-Aufnahmen identisch; der dazwischenliegende
   Seitenkettenlauf ordnete sie als rechte Blattseite der geprüften
   Indexpartition ein.“ Die Kettenmetadaten wurden dabei nicht an beiden
   Wait-Rändern erneut gelesen. Ein historischer, späterer oder allgemeiner
   Dauerzustand folgt daraus nicht.

Der konkrete Terminalwert für nicht vorhandene Nachfolger ist für die drei
später beschriebenen Builds empirisch als `(0,0)` beobachtet. Das ist keine
Herstellergarantie und gilt nicht automatisch für andere Builds. Eine sichere
Reaktion auf einen parallelen Split bleibt offen; bei geänderter oder
widersprüchlicher Struktur muss der Erheber `NOT_PROVEN` liefern.

## Ergebniszustände

| Befund | Ergebnis |
|---|---|
| Vollständige, widerspruchsfreie Wait-/Ziel-/Kettenbindung auf beiden Capture-Rändern | begrenzter Kandidat für `PASS`; noch keine Performancequalifikation |
| Kein gleichzeitiger eigener `PAGELATCH_EX`-Wait, fehlende Seite, unbestätigter Terminalwert, geänderte Kette oder erreichter Seiten-Cap | `NOT_PROVEN` beziehungsweise kontrollierter Skip |
| Wait-Adresse gehört nachweislich zu anderer Datenbank, anderem Index/Objekt/Partition, nicht zur Blattseite oder explizit zu einer nicht rechten Blattseite | `FAIL` für diesen Last-Page-Claim |
| Zeit-, Request- oder Ressourcenmarker widersprechen einander | Vertragsfehler; Cleanup hat weiterhin Vorrang |

`PASS` einer späteren Kettenprüfung wäre nur eine Aussage über die konkrete
Aufnahme. Er beweist weder hohe Konkurrenz über längere Zeit noch Durchsatz,
Ursache eines Produktionsengpasses oder einen Vorteil von
`OPTIMIZE_FOR_SEQUENTIAL_KEY`.

## Geltungsgrenzen und Gates

- Erste spätere Pilotierung nur auf einem eigenen, kurzlebigen SQL-Server-
  Developer-Wegwerfziel mit markierter Testdatenbank. Kein Zugriff auf eine
  geteilte Instanz; keine Änderung von Host-/Instanzkonfiguration.
- Die DMV-/Funktionsrechte, exakten Feldwerte für Blatt-Terminalseiten und
  Ressourcenkosten aller Einzelaufrufe sind buildgebunden vorab zu bestätigen.
- Der Capturepfad benötigt feste Obergrenzen für Wait-Rows, Seitenschritte,
  Laufzeit und Gesamtausgabe. Fehlende oder widersprüchliche Evidenz endet
  ohne Ausweitung der Abfrage oder Last.
- Der unabhängige Methoden-/Quellenreview vom 22. November 2026 fand nach
  Vertrags- und Dokukorrekturen keine offenen P1/P2 im Offline-/Draftumfang.
  Er bestätigte weder Terminalkodierung noch Traversalstabilität oder
  Captureüberlappung. Diese Punkte müssen auf dem Zielbuild separat belegt
  werden; ein Caller-Sentinel allein ist kein Terminalnachweis.
- Ein davon getrennter Offline-Checker darf caller-gelieferte Kettenrecords nur
  intern auf Seitenidentität, Blattniveau, Zyklen, Vorwärts-/Rücklinks,
  Startseite, expliziten Endmarker und Seiten-Cap prüfen. Er darf keine
  SQL-Abfrage oder Enginesemantik ableiten.
- Eine ausführbare read-only Seitenkettenprobe benötigt weiterhin einen
  konkreten Cleanup-/Runtimevertrag und einen buildgebundenen Plan für
  Terminalzustand, Waitränder, Rechte und Split-/Änderungsrisiko. Der faire
  OFF/ON-Lastvergleich bleibt ein getrenntes Gate und wird nicht durch
  Seitenkettenbelege freigegeben.

Die geltenden Herstellerquellen beschreiben Seiteneigenschaften und
Nachfolgerfelder, aber keinen atomaren Traversalvertrag für eine während
konkurrierender Inserts veränderliche B-Baum-Blattkette. Der begrenzte Versuch
belegt deshalb nur die beobachtete Stabilität zwischen zwei getrennten
Insertbursts auf den konkreten Builds, keinen allgemeinen Traversalschutz bei
gleichzeitigen Strukturänderungen.

`evaluate_last_page_wait_snapshot_consistency` verlangt neben dem Waitsnapshot auch caller-gelieferte `PageLink`-Records, einen expliziten Endmarker und ein begrenztes Seitenbudget. Es ruft den Kettenprüfer mit der Wait-Zielseite als Startadresse und der Ziel-Datenbank, dem Objekt, Index und der Partition auf. Ein PASS ohne passende Kette ist `NOT_PROVEN`; eine Kette mit abweichender Startseite oder Identität kann keinen PASS erzeugen. Der Checker prüft jedoch nur einen caller-gelieferten Waitsnapshot und die Linkkonsistenz. Sein PASS besagt weder, dass zwei unabhängige Waitränder vor und nach dem Kettenlauf bestanden, noch dass ein caller-gelieferter Sentinel im Zielbuild wirklich das Kettenende markiert. Die Kettenhilfe heißt daher `evaluate_supplied_page_chain_consistency`; ihr PASS meldet ausdrücklich nur strukturelle Konsistenz bis zum Caller-Sentinel. Beide Waitränder, ihre zeitliche Klammerung und bestätigte Terminalsemantik bleiben getrennte Implementierungs-/Buildgates. Keine der Offlinefunktionen authentifiziert DMV-/Seitenaufnahmen. Der hier beschriebene Pilot bleibt begrenzte Engineering-Evidenz. Ein unabhängiger Methodenreview ist Voraussetzung, bevor daraus eine wiederverwendbare Produktprobe, Demo- oder Qualifikationsfreigabe abgeleitet wird.

### Ergänzung des Offline-Waitvertrags

Der Offline-Waitchecker bindet jeden caller-gelieferten `PAGELATCH_EX`-Datensatz
jetzt zusätzlich an eine erwartete Actor-/Session-/Request-ID und eine
Taskausführung (`exec_context_id`). Beide erwarteten Actors müssen mit ihrer
caller-geliefert gebundenen Request-ID auf derselben Zielseite warten. Mehrere
unterschiedliche Tasks einer erwarteten Request-ID bleiben zulässig;
wiederholte Taskrecords, fehlende Identitäten und fremde Requests werden
abgewiesen. Der Checker prüft diese caller-Felder nur intern; er enthält keine
`task_address`-Records und verifiziert deshalb nicht den beschriebenen
`waiting_task_address`-zu-`task_address`-Join. Diese Zuordnung gehört zur
künftigen Erhebung und bleibt bis dahin `NOT_PROVEN`. Ebenso bleibt
`rightmost_leaf_claim` lediglich eine zusätzliche Callerbehauptung; nur die
noch nicht buildqualifizierte Kettenmetadatenaufnahme könnte den
Rechtsaußenstatus stützen. Der Offlinevertrag erteilt keine Enginefreigabe.

### Empirischer XE-/Kettenpilot (22. November 2026)

Ein begrenzter Pilot in
[`Tests/Runtime/idx007_hot_leaf_pilot.py`](../../Tests/Runtime/idx007_hot_leaf_pilot.py)
umgeht das Pollingproblem kurzer Waits. Er erfasst `latch_suspend_begin` und
`latch_suspend_end` in einer eigenen Extended-Events-Sitzung, bindet die
Ereignisse über Sequenz, Session und Request an bekannte Actor-Requests und
wertet nur ausgeglichene erfolgreiche Latch-Waitpaare mit XEvent-Klasse
`BUF` und Modus `EX` aus. Die monotone `package0.event_sequence`-Action ordnet
Beginn und Ende innerhalb der XE-Sitzung; eine Überlappung liegt vor, wenn die
Beginn-/Endereignisse zweier unterschiedlicher Actor-Waits ineinander
verschachtelt sind und dieselbe Datenbank-/Datei-/Seitenadresse betreffen.
Das im Enginekatalog als Mikrosekunden beschriebene `duration`-Feld wird
weiterhin auf einen 60-Sekunden-Cap geprüft und diagnostisch ausgegeben. Die
millisekundengenauen UTC-Zeitstempel entscheiden nicht über die Überlappung;
ein CI-Lauf auf SQL Server 2022 zeigte eine Abweichung zwischen Zeitstempel und
Waitdauer, die die frühere 1-ms-Konsistenzannahme nicht erfüllte. Verluste,
Duplikate in der Ereignisfolge, abgeschnittene oder zu
große Ringpuffer, unvollständige Paare und abweichende Ereignisressourcen
ergeben keinen Nachweis.

Der Pilot lädt 501 Seedzeilen und baut den Zielindex vor den Actor-Requests mit
`FILLFACTOR=100` neu auf. Vor Freigabe der Actors prüft er die physische
terminal markierte Indexseite und verlangt mehr als eine Blattseite sowie
mindestens 6.000 freie Bytes als Burstreserve. Die drei lokalen Builds ergaben
je zwei Blattseiten, 25 Slots und 7.671 freie Bytes. Er lässt 96 Actors je
eine Einfügung in zwei getrennten Bursts ausführen. Nach dem ersten Burst sind
alle Actor-Inserts beendet; danach prüft der Pilot die per
`sys.dm_db_page_info` gelesene Zielseite und ihren
Vorgänger-Rücklink. Erst danach startet der zweite Burst. Jeder Burst muss
eigene überlappende exklusive Waitintervalle auf einer Seite zeigen, die nach
Abschluss dieses Bursts als terminale Blattseite der markierten synthetischen
Clustered-Indexpartition bestätigt wird. Die physische Seite darf sich durch
eine Seitenaufteilung zwischen den Bursts ändern. Zwischen der Kettenprüfung
nach Burst 1 und dem Start von Burst 2 ändert kein Actor den Zielindex. Die
Blattseitenanzahl muss größer als eins sein; Seite, Objekt, Index, Partition,
Ebene und Rücklink werden je Capture geprüft. Da die Metadatenaufnahme nach
Abschluss der Actor-Inserts erfolgt, belegt sie keine atomare Zuordnung der
Seitenstruktur zum exakten Zeitstempel jedes Waits; parallele Split-/Änderungs-
Semantik bleibt ein Review- und Qualifikationsgate.

Auf den isolierten, digest-gepinnten Builds SQL Server 2019
`15.0.4500.2`, 2022 `16.0.4305.5` und 2025 `17.0.5035.5` bestand je ein
identischer 48×1-Lauf. Weitere CI-Läufe zeigten, dass 451 Seedzeilen mit
`FILLFACTOR=10` oder `1` sowie 801 Seedzeilen mit `FILLFACTOR=100` die
terminalen Wait-Seiten nicht stabil über beide Bursts hielten. Auch 701 Seeds
und 48 Actors ergaben CI-Grenzen: auf 2025 fehlte ein überlappender Wait, und
auf 2019 wurde die Wait-Seite nach Burst 1 nicht terminal bestätigt. Der Pilot
verwendet nun 501 Seeds, `FILLFACTOR=100` und 96 Actors; vorab prüft er die
reale Seitenreserve. Er bestätigte auf jedem Build die konkrete Produktversion
und Compatibility Level (150, 160, 170); jeder Rebuild ergab zwei Blattseiten,
25 Slots und 7.671 freie Bytes. Beide Burstcaptures bestanden jeweils mit einer nach dem
Burst bestätigten terminalen Seite und korrektem Vorgänger-Rücklink. Die
physische Seite kann sich nach einer Aufteilung ändern. Die genauen
Seitenadressen und Wartezeiten sind lauflokale Diagnosedaten und werden nicht
als Produkt- oder Performancewerte verallgemeinert. Je Lauf wurden 693
synthetische Zeilen bestätigt und Testdatenbank, XE-Sitzungen und eigener
Container entfernt. Die pro Lauf benannte Datenbank trug die vier
Framework-Ownershipmarker; der Cleanup prüfte sie vor dem Entfernen.

Das ist ein empirischer Methodenbeleg für genau diese drei Builds und diese
kontrollierte Lastform. Er bestätigt weder einen allgemeinen atomaren
Seitenkettenvertrag noch das Verhalten bei gleichzeitigen Page-Splits,
Produktionslast oder einen Vorteil von `OPTIMIZE_FOR_SEQUENTIAL_KEY`. Der
Pilot ist keine vollständige Demoqualifikation. Vor einer Änderung des
Methodenstatus oder einem Leistungsclaim bleibt ein unabhängiger Review dieses
Erhebungsvertrags erforderlich. Die serielle PR-/manuelle Runtime-Matrix steht
in [IDX-007 Live-Capture](../../.github/workflows/idx007-live-capture.yml).

### Zeitliche Klammer im laufenden Burst (22. November 2026)

Die vorherige Pilotfassung las die Seitenmetadaten erst nach dem Actor-Ende
und konnte die Terminalseite daher nicht in dasselbe Waitfenster einordnen.
Der Erheber startet jetzt vor der Burstfreigabe eine eigene SQL-Session, die an
der Barriere wartet. Die Actorfreigabe startet sowohl die Einfügungen als auch
den bereits verbundenen Kettenleser. Markierte
`sql_statement_starting`-/`sql_statement_completed`-XE-Ereignisse grenzen den
Kettenlesebatch über `package0.event_sequence` ein. Ein PASS erfordert zwei
erfolgreiche exklusive `BUF`-Waits verschiedener Actor-Requests auf derselben
Seite, deren gemeinsame Überlappung in dieses Kettenlesefenster fällt. Die
Kettenaufnahme liest die dann allozierten Blattkandidaten und muss dieselbe
Waitseite mit passender Objekt-/Index-/Partitionsidentität, Blattebene,
terminalem Nachfolger und stimmigem Vorgänger-Rücklink finden. Fehlt eine
dieser Bindungen, liefert der Lauf `NOT_PROVEN`.

Die Diagnose einer fremden Waitseite führte zu einer Korrektur am Harness:
Actor-Sitzungen werden vor dem Burst registriert; Fortschritts-Updates auf
`lab.ActorSessions` während der gemessenen Bursts entfallen. Der Harness
erkennt Burstabschlüsse jetzt über die erwartete Zeilenzahl in `dbo.Hot`.
So erzeugt die Fortschrittsverfolgung keine eigenen Seiten-Waits, die mit dem
Zielindex verwechselt werden könnten. Die CI-Artefakte zeigten zusätzlich
einen Startreihenfolgefehler: Die Orchestrierung öffnete die Actor-Barriere,
bevor die Capture-Session ihren XE-Startmarker ausgab. Writer-Waits konnten
dadurch vor dem markierten Kettenlesefenster liegen. Die Capture-Session wartet
jetzt auf ein Startsignal. Die Actors melden sich danach vor dem Burst in
`lab.ActorReady`. Für die Freigabe hält der Reader einen exklusiven,
sitzungsgebundenen `sp_getapplock`; alle Actors fordern anschließend einen
Shared-Lock auf derselben lauf- und burstgebundenen Ressource an. Nachdem die
erwartete Actorzahl ihre Bereitschaft registriert hat, setzt der Reader den
XE-Startmarker und gibt den exklusiven Lock frei. Die Steuerung wartet auf den
erwarteten Zeilenzuwachs, meldet danach `lab.BurstDone`, und der Reader wartet
innerhalb des markierten Fensters auf dieses Abschlusssignal, bevor er die
Seitenkette liest. Dadurch umfasst das Fenster die beiden vollständigen
Writerbursts samt serverseitiger Erfassung ihrer Warteintervalle, ohne
Actorzahl oder Einfügungen zu erhöhen. Die verbundene Session pausiert nach jeder
Blattseitenprobe fünfzig Millisekunden; zusätzliche Schreiblasten kommen nicht
hinzu. Das XE-Markerfilter nutzt nun das Ereignisfeld `statement` statt der
Action `sql_text`, die den ganzen Batch einschloss und auch Poll-Statements
erfasste. Die vorherige 1-ms-Pollingvariante und die anschließende
`ActorReady`-Pollingbarriere ließen SQL Server 2025 in der CI ohne vollständige
Waitüberlappungen. Die Variante mit Anwendungs-Lock und Ereignisfeldfilter
bestand lokal zuvor auf allen drei Builds je drei von drei Zweiburstversuchen.
Der finale `BurstDone`-Kandidat bestand lokal Build 15 und 16 je einmal sowie
Build 17 drei von drei Zweiburstversuchen, jeweils mit bestätigtem Cleanup. Die
neue PR-Matrix steht noch aus. Die serielle
CI-Matrix ([Lauf 45082708807](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/45082708807))
bestand ebenfalls auf allen drei Builds: Build 15 mit drei, Build 16 mit zwei
und Build 17 mit einem vollständigen Zweiburstnachweis aus je drei begrenzten
Versuchen. Alle Versuche bestätigten das Cleanup; erfolglose Varianten blieben
`NOT_PROVEN`. Der finale lokale `BurstDone`-Kandidat bestand Build 15 und 16
je einen vollständigen Zweiburstversuch sowie Build 17 drei von drei Versuchen;
alle bestätigten Kettenbindungen und das Cleanup. Die unmittelbar vorherige
Kandidatenmatrix ohne `BurstDone` bestand auf allen drei Builds je drei von drei
Versuchen. Für den finalen Kandidaten steht die neue PR-Matrix noch aus.

Die angepasste Lastform verwendet 501 Seeds und eine Einfügung pro Actor je
Burst. Build 15 (`15.0.4500.2`) und Build 16 (`16.0.4305.5`) verwenden
`FILLFACTOR=100` mit 80 Actors; Build 17 (`17.0.5035.5`) verwendet
`FILLFACTOR=10` mit 56 Actors. Das Build-17-Profil folgt der beobachteten
Seitenteilung bei 64 Actors; die Zwischenstufe soll mit weniger Inserts die
Terminalseite halten und durch das geringere Füllziel genug Waits erzeugen.
Vor jedem Lauf werden Blattseitenzahl und freie Bytes physisch
gemessen. Die aktuellen lokalen Profile bestanden auf Build 15/16 und Build 17
je drei von drei gleich begrenzten Versuchen mit je zwei getrennten
Wait-/Kettenklammern; 661 synthetische Zeilen auf Build 15/16 und 613 auf
Build 17. Ein früherer fehlgeschlagener CI-Lauf zeigte, dass die
überlappende Waitseite eine andere Objekt-ID als den Zielindex hatte; die
zusätzliche DMV-Diagnose bleibt deshalb fail-closed. Alle aktuellen lokalen
Versuche bestätigten Datenbank- und Container-Cleanup. Die erfolgreichen
Waitüberlappungen lagen jeweils innerhalb des markierten Kettenlesefensters.

Die serielle CI-Matrix wiederholt pro Build bis zu drei vollständige
Engineeringläufe mit denselben Profilgrenzen. Jeder Versuch protokolliert
separat `PASS` oder `NOT_PROVEN` und bestätigt sein Cleanup. Der Buildjob ist
nur erfolgreich, wenn mindestens ein vollständiger Zweiburstversuch den
Nachweis erbringt; drei erfolglose Versuche schlagen ihn fehl. Das lässt
variierende Konkurrenzsichtbarkeit sichtbar, ohne sie als deterministische
Buildgarantie umzudeuten. Die Methodenfreigabe bleibt getrennt.

Das bindet den beobachteten Wait und die Kettenabfrage über dieselbe geordnete
XE-Ereignisfolge und denselben laufenden Burst. Es macht DMV-Abfragen nicht zu
einem atomaren Snapshot: insbesondere beweist es nicht, dass jede einzelne
Seitenkopfzeile exakt im Moment eines Latch-Waits gelesen wurde, und es
qualifiziert keine gleichzeitigen Page-Splits. Der Methodenstatus bleibt
`METHOD_DRAFT`; der Pilot ist weder vollständige Demo- noch
Leistungsqualifikation. Der reproduzierbare Buildnachweis muss noch die frische
serielle PR-Matrix bestehen.
