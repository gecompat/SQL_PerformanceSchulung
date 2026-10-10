# DGN-007 – G13-Fehler und Abschluss von PR 68

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-09 |
| Auftrag | Ursache und Nutzen des liegengebliebenen Diagnose-PR prüfen und den relevanten Abschluss verfolgen |
| geprüfte Main-Basis | `174076b505b4f317a0b3f2fe7830ae3244ff03d3` |
| aktueller Abgleich nach Foundation-Upgrade | `2f04deb2fed0faf5bedf70101fea3f4b93d46678`, [PR 123](https://github.com/gecompat/SQL_PerformanceSchulung/pull/123) |
| ursprünglicher Reporter-Head | `27a9b5ce81347beaa6d6bfd8788c62965495f0ca` |
| aktualisierter Reporter-Kandidat | `f9ec582017c942e4278252427c62695e313d37f9` |
| aktueller Abschluss | PR 68 fachlich verworfen; finaler Parser-/Methodenschnitt in [PR 132](https://github.com/gecompat/SQL_PerformanceSchulung/pull/132) gemäß `DEC-072`, Integration nur mit aktueller relevanter CI |
| Arbeit | [PR 68](https://github.com/gecompat/SQL_PerformanceSchulung/pull/68), `codex/dgn007-g13-boundary-report` |
| Ergebnisgrenze | Diagnosepaket; keine G13-Behebung, Methodenwahl oder Incidentfreigabe |

## Problem und nachweisbare Ursache des Fehlschlags

**Aktuelle Entscheidung vom 2026-10-10:** Der Benutzer hat die neue Methode
freigegeben und den Umfang anschließend auf einen zügigen, begrenzten Abschluss
festgelegt. `DEC-072` und der v2-Vertrag behandeln QS↔SYSUTC diagnostisch ohne
Zeitpuffer. SQL20/21 verlangen im gewählten Intervall zusätzlich tatsächliche
reguläre QS-Erfassung des festen separat markierten Pollqueries; eine passend
datierte Katalogzeile allein genügt nicht. Die eigene kontrollierte Last und
ihre Ergebnisse, vier reguläre Suchausführungen, Intervall-/Familien-/Planbindung,
Budgets und Cleanup bleiben überprüft. Die Aussage ist eine beobachtete
Labzuordnung, keine exakte Einzelrequest→Plan- oder Host-Provenienzattestation.
Die größere vorgeschlagene Nachweisarchitektur bleibt zurückgestellt.

PR 68 wird verworfen, weil sein ausschließlich am bisherigen G13-Fehlerpfad
hängender Reporter für diesen Abschluss überholt ist. Das ist kein Befund eines
defekten Reporters. Die nützliche Rawdiagnose aus PR 128 ist schon mit PR 130
auf Main; den zusätzlichen alten Reporter übernehmen wir aus demselben Grund
nicht. PR 132 korrigiert die tatsächlich fehlerhafte UTC-Z-/Vollsekunden-
Parserannahme und führt die v2-Methode ein. Originalzeiten bleiben vollständig
im Capture, die alte Rawdiagnose bleibt begrenzt erhalten. Der alte v1-Evaluator
behält sein G13-Prädikat; v1-Bodies werden nicht als v2 interpretiert.
Die relevante aktuelle Versionsmatrix und Integration sind direkt in PR 132
nachprüfbar. Erst danach folgt die Bereinigung der zugehörigen Branches;
verworfene Quellen werden zuvor lokal als geprüftes Git-Bundle gesichert.

Die folgenden Analysen und fehlgeschlagenen Runs bilden die Historie. Aussagen
über noch ausstehende Benutzerfreigabe oder notwendige größere Provenienzgates
gelten nicht mehr für den ausdrücklich gewählten begrenzten Abschluss.

SQL21 speichert unmittelbar vor den vier Suchrequests je Fenster
`ExecutionStarted` und danach `ExecutionFinished` aus `SYSUTCDATETIME()`.
SQL35/G13 verlangt den exakten Einschluss der gespeicherten Query-Store-Werte
`FirstExecutionTime` und `LastExecutionTime` in diese Klammer.
Der Reporter wird ausschließlich im bereits verletzten G13-Zweig ausgeführt.
Er verändert das Prädikat und den Fehlerausgang nicht.

Die [historischen PR68-Läufe](DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md#reguläre-pr68-ci-zwei-tatsächliche-untere-g13-verletzungen)
belegen untere Grenzverletzungen um 0,4263 ms auf SQL Server 2019 und
0,951 ms auf SQL Server 2022. In beiden Fällen ist First exakt der auf volle
Millisekunden abgerundete Startwert. Eine getrennte lokale Originalmaterialisierung
verletzte dieselbe Grenze um 0,2609 ms, bei einer positiven Raw-Zeile mit
Count vier und ohne Zero-/NULL-/Negative-Rows. Die Nullcount-Erklärung trägt
diesen konkreten lokalen Fehler nicht.

Das fehlschlagende Prädikat und die verletzten Werte sind belegt.
Die vermutete Ursache innerhalb der SQL-Server-Zeiterfassung bleibt offen:
Die beobachtete Millisekundenstruktur passt zu einer unterschiedlichen
Zeitauflösung; sie beweist keine allgemeine Quantisierung, gemeinsame Clock
oder zulässige Fehlergrenze. Der identische G13-Code steht bereits auf Main.
Ein Reporterdefekt ist durch diese Lifecycle-Fehler nicht nachgewiesen.

Microsoft beschreibt First/Last als Ausführungs-Endzeiten und verlangt bei
aktiven Intervallen die Aggregation der Memory-/Diskzeilen. Die Beschreibung
von `SYSUTCDATETIME` unterscheidet Präzision und Genauigkeit. Die am 2026-10-09
erneut geprüften Primärquellen garantieren keinen 100-ns-Einschluss zwischen
diesen Messwegen auf den verwendeten Linux-Containern:
[RuntimeStats](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17),
[SYSUTCDATETIME](https://learn.microsoft.com/en-us/sql/t-sql/functions/sysutcdatetime-transact-sql?view=sql-server-ver17),
[QS-Erfassung](https://learn.microsoft.com/en-us/sql/relational-databases/performance/how-query-store-collects-data?view=sql-server-ver17).
Eine Rundung, ein Zeitpuffer oder das Entfernen von G13 wäre eine Vertragsänderung
und ist kein Bestandteil dieses Abschlusses.

## Nutzen und Integrationsumfang

Der Diagnosebericht bleibt nützlich: Ohne ihn berichtet Main bei G13 nur die
Guard-ID; ein neuer Fehler kann die untere, obere oder beide Grenzen betreffen.
Die Ausgabe bewahrt exakte gespeicherte Werte, benennt Overflow und fehlende
Diagnose und erscheint erst nach der unabhängigen Cleanupprüfung. Sie liefert
keine Querytexte, Plan-XML oder zusätzliche QS-Abfrage.

Der Vergleich aller sechs Quell-/Vertragsdateien bestätigte vor der
Aktualisierung byteidentischen Main-/PR68-Base-Stand und fehlende
Reporterimplementierung. Der andere Inline-Profilreporter ersetzt sie nicht.
Die fünf weiterentwickelten Planungs-/Nachweisdokumente wurden bei der
Aktualisierung vollständig aus der aktuellen Main-Basis erhalten.
Der Diagnose-PR wird getrennt von einer zukünftigen Methodenänderung geprüft.
Das [Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md) und
DEC-068 bleiben unverändert; ihre Gates sind durch Reporter-PASS nicht erfüllt.

Der erste aktualisierte CI-Lauf
[37892132149](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37892132149)
erkannte einen zusätzlichen Integrationsbedarf: Der später hinzugekommene
Offline-Kantenverifier band noch den Runner vor der Reporteränderung und meldete
`PYTHON_PROFILE_CHANGED`. Die lokale Nachrechnung aller neun Ganzdatei-AST-Digests
mit dem geforderten CPython 3.12.14 bestätigte genau eine Änderung: den Runner.
Nach dem vollständigen Runnerdiffreview wurde nur sein expliziter Profildigest
aktualisiert. Die acht anderen Digests, Parserversion, Imports, deklarierten Kanten,
Manifestprojektionen und die außerhalb der Quellenhashes gebundene Incidentpolicy
bleiben unverändert. Der Kandidat wird nicht gegen seinen eigenen Digest akzeptiert;
das kontrollseitige Profil bleibt fest und negative AST-Gegenproben maßgeblich.

Die 26 Kantenprüfungen bestanden danach unter CPython 3.12.14. Eine zusätzlich
gestartete lokale Quellenbundlesuite lieferte im ersten Testcontainer mit
128-Prozesslimit anschließend `can't start new thread` und kein erfolgreiches
Ergebnis. Nach Änderung der Testumgebung auf einen eigenen Container mit
Init-Reaper und 512-Prozesslimit bestanden alle zwölf Offline-CI-Suiten:
885 Testmethoden, kein SKIP. Der Checkout war read-only eingebunden; während
der Tests war das Containernetz getrennt. Die Git-Abhängigkeit wurde ausschließlich
im eigenen wegwerfbaren Container bereitgestellt. Beide eigenen Testcontainer
wurden nach Eigentumsprüfung entfernt und ihre Abwesenheit unabhängig geprüft.
Diese lokalen Gegenproben attestieren keine SQL-Ausführung oder Methodenwahl.

## Aktuelle Runtime: vorheriger PASS und neue substantielle Fehler

Die erste neue [Matrix 37892132187](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37892132187)
am Head `5ab8c602e81e16dd027c02ba8192c75bd57dd0d9` gegen Main `174076b…`
bestand auf 2019, 2022 und 2025 jeweils zwölf Lifecycles, sechs Decoder-Captures
und alle ersten unabhängigen Datenbankabwesenheitsprüfungen: insgesamt 36
Lifecycles, 18 Captures und 36 Cleanup-PASS. Der Checkoutlog bindet Integration
`0f2442a…`. Alle 27 Runtime-Bundlemitglieder sind zwischen `5ab8c60…` und
`f9ec582…` Gitblob-identisch. Der nachfolgende Lauf ist dennoch nicht durch
diesen PASS freigegeben; negative neue Evidenz bleibt maßgeblich.

Die [aktuelle Matrix 37892941746](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37892941746)
bindet Head `f9ec582…` gegen dieselbe Base; Checkoutintegration `6519a57…`.
Sie weist zwei eigenständige substantielle Fehler nach:

- [SQL Server 2022](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37892941746/job/113700972634):
  `PROFILE_COMPARISON / RUN_1`, tatsächlich fehlgeschlagene Phase
  `QUERY_STORE_WINDOWS`, `FAIL_EXECUTION`, Msg 51002 / SQL20-Zeile 351.
  SQL20 verlangt dort nach höchstens zehn Sekunden Polling genau vier erfasste
  Suchausführungen je Fenster. Die Abnahmebedingung `@Ready=1` wurde nicht
  erreicht; konkrete fehlende/zusätzliche Counts und Ursache sind nicht geloggt
  und bleiben offen. SQL20 ist byteidentisch mit Main (Gitblob
  `cf620c3d7c66c5d21e7b3c2c8f64d552b2fd8c1b`). Diese Phase führt den
  SQL35-Reporter nicht aus. Die ersten vier Lifecycles bestanden; der fünfte
  scheiterte und seine erste unabhängige DB-Abwesenheitsprüfung bestand.
- [SQL Server 2025](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37892941746/job/113700972553):
  `CONTROL_BA / RUN_1`, tatsächlich fehlgeschlagene Phase `CONTROL_EVIDENCE`,
  `FAIL_RESULT_CONTRACT / G13`; abschließender Runnercode `FAIL_EXECUTION`.
  Der Reporter lieferte atomar eine vollständige gespeicherte Gruppe in Fenster
  1 mit Count vier: Start `639271251604808298`, Finish `639271251609553202`,
  First `639271251604800000`, Last `639271251609130000` UTC-100-ns-Ticks.
  First−Start = −8298 Ticks = −0,8298 ms; Last−Finish = −423202 Ticks
  = −42,3202 ms. Nur die untere Grenze ist verletzt. First ist erneut exakt
  der auf Millisekunden abgerundete Startwert; die Ursachen-/Genauigkeitsgrenze
  bleibt trotzdem offen. Acht Lifecycles bestanden, der neunte scheiterte mit
  erster unabhängiger DB-Abwesenheit PASS. Rawfragmente werden durch diesen
  Reporter nicht ausgegeben; ein Ausschluss von Zero-Rawzeilen für diesen neuen
  Versuch wird nicht behauptet.

SQL Server 2019 bestand seine zwölf Lifecycles und sechs Decoder-Captures.
Insgesamt begann der aktuelle Lauf 26 Lifecycles: 24 PASS und zwei FAIL;
acht tatsächliche Decoder-Captures bestanden. Alle 26 ersten unabhängigen
DB-Abwesenheitsprüfungen und die regulären Containerabbauten aller drei
Versionen einschließlich Volumes bestanden. Insgesamt sind 21/23 aktuelle
PR-Checks SUCCESS und zwei FAILURE. Weder der vorherige grüne Lauf
noch erfolgreiche statische Prüfungen heilen diese neuen Vertragsfehler. Es wird
kein unveränderter Kandidat erneut ausgeführt, um eine grüne Zufallsfolge zu erhalten.
Die direkte Integration des Reporterpakets bleibt gesperrt. Der Code-PR wurde
für die getrennte Integration dieses Prüfberichts und von DEC-069 vorübergehend
geschlossen; Code und Branch wurden erhalten, nicht verworfen oder integriert.

## Prüfung und Abschlussbedingung

Am aktualisierten Kandidaten bestanden lokal 170 Testmethoden: 169 PASS,
ein ausschließlich Linux betreffender SKIP unter Windows/Python 3.14.
Geprüft wurden Runner, Producer/Reporter, Phasenintervalle, Kontrollcaptures,
Profilvergleich, Compatibility, Transport und prospektive Bewertung.
Alle sieben DGN-007-Validatoren, Kennungsvertrag, Repositorykontinuität,
Registry und Privacyprüfung bestanden. Der genaue Reporter-Stripnachweis
bindet die ganze bisherige SQL35; Guard, Last, Budgets und Fehlerprioritäten
bleiben unverändert. Diese statischen Ergebnisse ersetzen keine Runtime.

Vor Integration muss die reguläre CI des aktualisierten PR-Heads gegen die
aktuelle Base erfolgreich sein. Historische G13-Fehler bleiben dokumentiert.
Ein neuer G13-, Timeout-, Vertrags- oder Cleanupfehler sperrt die Integration;
es gibt weder Bypass noch Wiederholung unveränderter Kandidaten bis grün.
Aktuelle Head-/Base- und Checkbelege stehen im PR. Nach erfolgreicher Integration
folgen Main-Synchronisierung, vollständiger Übernahmevergleich und lokale sowie
Remote-Branchbereinigung nach DEC-066/DEC-069.

## Vollständige Bestandsprüfung und ausdrückliche Zurückstellungen

Die anfängliche Bestandsprüfung fand genau einen offenen PR und einen
Remote-Arbeitsbranch: PR68. Nach der Prüfung ist seine Codearbeit technisch
blockiert und der PR vorübergehend geschlossen. Der Remote- und lokale Branch
`codex/dgn007-g13-boundary-report` bei `f9ec582…` bleiben wegen nicht übernommener
Änderungen erhalten. Wiederaufnahme erfordert die Klärung/Korrektur der
Erfassung und des G13-/Methodengates, einen aktuellen Quellenreview sowie
erfolgreiche relevante CI; der zusätzliche Scopeentscheid wurde dem Benutzer
vorgelegt. Das ist kein erfolgreich abgeschlossener Codetask und keine neue
ausdrückliche Zurückstellung durch den Benutzer. Der lokale Branch
`codex/dgn007-internal-capture-receipt` bei `83f08fb71446445e70fb6227e442ed7109637de6`
ist ausdrücklich zurückgestellt: Seine interne Capture-Rückgabe wartet auf die
G13-/Messvertragsklärung und die ausdrückliche Methodenentscheidung. Erst danach
werden Quellenreview, relevante Tests, aktuelle CI und Integration verfolgt.
Er wird nicht als übernommen gelöscht.

Die allgemeine Entwicklung und Automation bleiben pausiert; dieser Auftrag
nimmt ausschließlich Prüfung und Abschluss der bestehenden Reporterarbeit sowie
den verbindlichen Abschlussprozess wieder auf. SESSION_END und weitere
ausdrücklich pausierte Folgepakete werden nicht mit diesem Diagnoseauftrag
begonnen. Dauerhaft maßgeblich sind dieser Review, der kanonische
[Ausführungsstand](CURRENT_EXECUTION_STATUS.md) und DEC-069.

## Begrenzter Korrekturscope nach Foundation 1.20.0

Der anschließende Benutzerauftrag autorisiert Ursachenanalyse und normale
Fehlerkorrekturen für SQL20-Erfassung und G13 innerhalb der bestehenden Methode.
Eine zusätzliche Freigabe dieser Fehlerkorrekturen ist nicht erforderlich.
Die ausdrücklich ausgeschlossenen Entwicklungswellen, SESSION_END, interne
Capture-Rückgabe und pausierte Automation bleiben ausgeschlossen. Ein
Implementierungsverantwortlicher führte den Scope ohne Unteragenten. Das vorab
gewählte Diagnoselimit war ein Lifecycle je betroffener Version; eine zusätzliche
Bestätigungsmatrix war nur nach einer belegten Korrektur vorgesehen.

### Bestands- und Quellenabgleich

Main `2f04deb…` enthält das separat integrierte Foundation-Upgrade mit grüner
Pflicht-CI; sieben PR- und fünf Main-Checks bestanden. Der eigene Upgrade-Branch
wurde erst nach bestätigtem serverseitigem Merge und vollständig identischen
Trees lokal sowie remote entfernt. Die Aktualisierung ändert keine SQL-Quelle.
SQL20 und SQL21 sind zwischen Main und Reporter-Head `f9ec582…` Gitblob-identisch.
Die Reporter-Erweiterungen in SQL35, Runner, Decoder-Tests, Validator und
kontrollseitigem AST-Profil sind weiterhin unübernommen. PR68 ist `CLOSED`,
Remote-/Lokalbranch `codex/dgn007-g13-boundary-report` steht weiter exakt auf
`f9ec582017c942e4278252427c62695e313d37f9`. Die ausdrücklich zurückgestellte interne
Capturearbeit `83f08fb…` wurde weder integriert noch gelöscht.

Die drei oben verlinkten Microsoft-Primärquellen wurden erneut am 2026-10-09
geprüft. Query Store beschreibt First/Last als Ausführungs-Endzeiten und fordert
Aggregation aktiver Memory-/Diskfragmente. Eine Garantie für den exakten
100-ns-Einschluss zwischen Query Store und SYSUTC ergibt sich daraus weiterhin
nicht. Die Quellenprüfung ersetzt keinen beobachteten fehlgeschlagenen Capture.

### Zwei einmalige lokale Diagnosen

Grundlage war ein privater Git-Export des gepinnten Reporter-Heads. SQL20/SQL21
erhielten ausschließlich nach `CAPTURE_DONE` lesende skalare Projektionen aus
`lab.IncidentState`, `lab.IncidentProfile`, dem Requestcount und höchstens 32
RuntimeStats-Zeilen der eigenen Prozedur. SQL35 erhielt dieselbe zusätzliche
Rohsicht ausschließlich im bereits verletzten G13-Zweig vor dem vorhandenen
Reporter. Vier Assertionsrequests und zweimal vier Fenstercalls, Parameter,
Abnahmen, Aggregation, Guards, Caps und Budgets blieben unverändert. Kein neuer
Suchcall, kein OFF/CLEAR, keine Rundung und keine größere Wartefrist.

Der lokale Diagnosewrapper hatte den Rawbyte-SHA256
`fd88b131e154db82b3e15e4f88eed300b50f2453a1541e110bfe353df520a6c6`.
Er rief pro Version genau einmal den bestehenden FWK-Harness mit dem ausgewählten
Manifest und `--show-output` auf. Die privaten SQL-Ergänzungen sind Diagnose-
instrumentierung, kein versionsgebundener Bundle-/Gate- oder Importnachweis.
Die tatsächlichen Suchphase-Grenzen blieben SQL20/21 145 s, Lifecycle 180 s,
Cleanup 60 s und äußerer Schutz 260 s. Eigene Container hatten vier CPU/8 GiB,
keine Ports oder Mounts; vorhandene fremde Container wurden nicht verändert.

| Version und Scope | tatsächlich beobachtetes Ergebnis | Phasenlaufzeit | gesamte lokale Walltime |
|---|---|---|---|
| SQL Server 2022 Developer `16.0.4265.3`, `profile-comparison` | Harness Exit 0; alle sechs Phasen PASS; ausgewählte Suchprofile je Fenster Count 4, Requestgesamtcount 12 | SQL20 107,736 s | 460,184 s einschließlich fehlgeschlagenem Readinessvorlauf |
| SQL Server 2025 Developer `17.0.4075.5`, `control-ba` | Harness Exit 0; alle acht Phasen PASS einschließlich SQL35; ausgewählte Suchprofile je Fenster Count 4, Requestgesamtcount 12 | SQL21 108,431 s | 180,140 s einschließlich Readinessvorlauf |

Die initiale `localhost`-Verbindung im Docker-Netzmodus `none` scheiterte vor
dem Lifecycle mit ODBC-Login-Timeout/TCP-Namensauflösungsfehler. Eine getrennte
numerische Loopback-Readiness bestand. Nach Entfernen des `none`-Anschlusses und
Anschluss an das reguläre Bridge-Netz ohne Portfreigabe bestand die unveränderte
`localhost`-Route. Diese Änderung betrifft die lokale Diagnoseumgebung, nicht
den bestehenden Runner oder die SQL-Methode. Der erste Vorlauf bleibt ein
Infrastrukturfehllauf. Insgesamt liefen nur die beiden genannten SQL-Lifecycles.

Beide ersten unabhängigen Datenbankabwesenheitsprüfungen bestanden ohne Recovery.
Beide eigenen Container wurden nach Name-/Scope-/Eigentumsprüfung über ihre
vollständige CID entfernt; unabhängige CID-Abwesenheit bestand. Gesamtwalltime
der beiden lokalen Versuche: 640,324 s, inklusive Fehlervorlauf und Cleanup.
Keine Wiederholung bis zufällig grün und keine weitere SQL-Matrix.

Die gespeicherten Vergleichswerte, UTC:

| Version / Fenster | ExecutionStarted | FirstExecutionTime | First−Start |
|---|---|---|---|
| 2022 / 0 | `11:17:00.4030093` | `11:17:00.4170000` | +13,9907 ms |
| 2022 / 1 | `11:18:00.8997081` | `11:18:00.9230000` | +23,2919 ms |
| 2025 / 0 | `11:20:00.2668783` | `11:20:00.2900000` | +23,1217 ms |
| 2025 / 1 | `11:21:00.4391822` | `11:21:00.4470000` | +7,8178 ms |

Die SQL2025-Lastwerte lagen ebenfalls innerhalb der Klammer: Fenster 0
`11:20:00.6800000` vor Finish `11:20:00.7194504`; Fenster 1
`11:21:00.8130000` vor Finish `11:21:00.8498137`. Die zusätzliche Prozedur-Rohsicht
lieferte pro Version sechs Zeilen, jeweils Count vier, ohne sichtbare Null- oder
Zerozeilen. Sie enthält auch andere Statements der Prozedur: ihre Counts dürfen
nicht zusätzlich zum markergebundenen Suchstatement gezählt werden. Die Sicht
belegt weder vollständige Fehlerfall-Coverage noch die Herkunft früherer CI-Werte.

### Ergebnis, fehlender Beleg und Wiederaufnahme

Keiner der beiden bekannten CI-Fehler wurde in diesen einmaligen Diagnosen
reproduziert. Ein lokaler PASS ist **keine Fehlerbehebung** und überschreibt weder
die CI-Fehler am Reporter-Head noch die früheren echten G13-Verletzungen. Eine
aus belegter Ursache abgeleitete Codekorrektur liegt deshalb nicht vor. Reporter-
Code bleibt `BLOCKED`, PR68 bleibt geschlossen und sein Branch erhalten.

Der Messablauf bleibt: vier echte Suchrequests werden mit Ergebnissen und
Requestlog geprüft; Query Store gruppiert die Stats des Suchstatements nach
Fenster/Plan/Type. SQL20 verlangt genau vier erfasste Ausführungen je Fenster.
SQL35 verlangt anschließend, dass First/Last exakt in der zuvor gespeicherten
SYSUTC-Klammer liegen. Ein Countfehler beendet bereits SQL20 und erreicht den
SQL35-Reporter nicht. Eine G13-Verletzung beendet SQL35 unabhängig von der
Nützlichkeit des Diagnoseberichts.

- **SQL2022-Erfassung:** Der CI-Fehler belegt die verletzte Viererabnahme, aber
  nicht, ob ein Fenster zu wenige, zusätzliche oder falsch zugeordnete Counts
  hatte. Es fehlen die im **fehlerhaften** Lauf verwendeten Profile, der vollständige
  marker-/familiengebundene Rohcountzustand und dessen zeitliche Aufnahmebindung.
  Ohne diese Werte sind Captureverzug, unvollständige Familie, Acquisitionwechsel
  und Fehlzuordnung Hypothesen. Wiederaufnahme: eine begrenzte skalare Fehleraufnahme
  vor Cleanup aus dem tatsächlich fehlgeschlagenen SQL20-Pfad; vorhandene Poll-
  und Lifecyclegrenzen unverändert. Danach eine konkrete Ursachenhypothese samt
  Gegenprobe. Keine identische Matrixwiederholung allein für einen PASS.
- **SQL2025-Zeitgrenze:** Die tatsächlichen −0,8298 ms bleiben belegt. Die neue
  erfolgreiche Klammer beweist keine universelle Messgarantie. Für diesen CI-
  Fehler fehlen positive und Zero-Rawfragmente derselben Acquisition sowie ein
  belastbarer Zusammenhang zwischen Enginezeit und SYSUTC. Wiederaufnahme unter
  bestehender Methode: fehlende Fehlerbelege gezielt aufnehmen und eine belegte
  Aggregations-/Implementierungsursache prüfen. Rundung, Puffer, verschobene
  Fensterklammer oder Ersatz von G13 bleiben materielle Methodenänderungen.

Die konkrete fachliche Auswahl ist deshalb: G13 exakt erhalten und den Reporter
bis zu belastbarer Fehlerfall-Evidenz blockieren, oder die im
[Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md) vorgeschlagene
kollektive Zuordnung separat entscheiden. Diese Alternative benötigt vollständige
Call-/Familien-/Acquisition- und Zwischenstandsbelege statt eines exakten
QS↔SYSUTC-Einschlussclaims; alle dort offenen Gates und unveränderten Ressourcen-
grenzen wären zu erfüllen. Empfehlung für den begrenzten Korrekturscope:
**G13 zunächst exakt erhalten und die fehlende Fehleraufnahme nachholen**.
Die Methodenalternative hat mehrere zusätzliche offene Nachweise; ihre Auswahl
wäre keine kleine Fehlerkorrektur. Der Benutzer hat am 2026-10-09 ausdrücklich
„G13 exakt beibehalten; fehlende Fehlerbelege gezielt nachholen“ ausgewählt.
Damit ist die fachliche Abnahmerichtung geklärt, die Fehlerursache weiterhin offen.
Die Methodenalternative bleibt ungewählt; die fehlende Fehleraufnahme ist noch
kein implementierter oder erfolgreicher Nachweis.

Jeder später korrigierte Reporter-Kandidat benötigt Quellen-/Vertragsabgleich
gegen den dann aktuellen Main-Stand, passende lokale Gegenproben und erfolgreiche
relevante CI für den exakten Head/Base. Erst danach Integration und eigene
Branchbereinigung. Alte Failures bleiben sichtbar. Foundation-/Prozessupgrade
ist bereits getrennt abgeschlossen; allgemeine Welle und Automation bleiben
pausiert. Die Ursache-/Methodenarbeit ist mit diesen Wiederaufnahmebedingungen
offen, nicht als erledigte Reparatur geführt.

## Erneute begrenzte Fehleraufnahme am 2026-10-10

Der Benutzer nahm DGN-007 erneut auf und ließ die zuvor gewählte exakte
G13-Abnahme unverändert. [Draft-PR 128](https://github.com/gecompat/SQL_PerformanceSchulung/pull/128)
bindet den erhaltenen Reporter an den aktuellen Main-Stand und ergänzt nur im
tatsächlich fehlgeschlagenen SQL20- beziehungsweise G13-Zweig eine begrenzte
skalare Rohaufnahme vor Cleanup. Die Diagnose gibt höchstens 16 Query-Store-
Einzelzeilen mit Fenster-, Familien-, Plan-, Intervall-, Typ-, Count- und
Zeitfeldern aus; bei SQL20 zusätzlich die Ist-Counts beider Fenster. Der Runner
prüft die erlaubten Felder und zeigt sie erst nach unabhängiger Cleanupprüfung.
Ausführungsfolge, vier Requests je Fenster, G13-Prädikat, zehn Sekunden
Capture-Polling, Phasen- und Cleanupbudgets wurden nicht geändert.

Ein erster lokaler SQL-2022-Diagnoseversuch fand einen neu eingeführten
SQL-Syntaxfehler vor der fachlichen Abnahme. Nach dieser konkreten Korrektur
bestanden je ein gezielter `profile-comparison`-Lifecycle auf SQL Server 2022
und `control-ba` auf SQL Server 2025, jeweils mit erster unabhängiger
Datenbankabwesenheit und eigenem Containerabbau. Dieser Entwicklungsschritt ist
kein SQL20-Fehlerfallbeleg. Die einzige neue vollständige
[PR-Matrix 38045921184](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38045921184)
am Head `657bbb22759cfbf27e5fbbfbf63e3660a885b3b2` gegen Base `0601361…`
bestand auf SQL Server 2019, 2022 und 2025. Alle sechs Scopes je Version liefen
zweimal; die drei Jobs und ihre Cleanupschritte schlossen erfolgreich ab.
Statische DGN-007-, Offline-Bundle-, Privacy-, Registry- und Governance-Checks
bestanden. Die zwei bekannten Fehler traten nicht auf.

Damit fehlen unverändert die **Ist-Counts und Familien-/Rohzeilen aus dem
fehlgeschlagenen SQL20-Lauf** sowie **positive und Zero-Rohfragmente des
fehlgeschlagenen G13-Laufs** und eine belastbare QS↔SYSUTC-Zeitquellenbeziehung.
Die neue Matrix widerlegt die früheren Fehler nicht. Eine Ursache und eine
relevante Gegenprobe sind weiterhin offen; ein rein grüner Wiederholungslauf
ist keine Reparatur. PR 128 bleibt Draft/`BLOCKED`, der Reporter unintegriert.
Wiederaufnahme unter der gewählten Methode erfolgt erst mit einem authentischen
Fehlerfall und dessen vollständiger begrenzter Aufnahme. Eine kollektive
Zuordnung benötigt stattdessen die gesonderte Methodenentscheidung samt den
offenen Gates aus dem [Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md).

## Separat integrierte Rohdiagnose nach PR 130

[PR 130](https://github.com/gecompat/SQL_PerformanceSchulung/pull/130) isolierte
die auf 16 skalare Zeilen begrenzten SQL20-/G13-Rohdiagnosen aus dem weiterhin
blockierten Reporterpaket. SQL20 meldet im tatsächlichen Countfehler beide
Fenster-Counts und scoped Rawfragmente; G13 meldet im verletzten Guardzweig
positive und Zero-Rawfragmente. Jede Sicht ist eine spätere Query-Store-Abfrage
im selben Fehlerfall, keine atomare Rawaufnahme des gespeicherten Profils.
Fehlende, überlaufende oder ungültige Diagnose ist kein positiver Beleg.
Der bestehende Fehlerausgang und unabhängige Cleanup bleiben maßgeblich.

Der aktuelle [CI-Lauf 38048742623](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38048742623)
bestand gegen Base `0e71067…` auf 2019, 2022 und 2025 alle sechs Scopes
zweimal, insgesamt 36 Lifecycles mit 36 unabhängigen Cleanup-PASS, sowie die
statischen und Pflichtchecks. PR 130 wurde als Tree-identischer Squash-Commit
`aea230f…` auf `origin/main` integriert; sein eigener Branch wurde nach
Übernahmeprüfung lokal und remote gelöscht. Kein SQL20- oder G13-Fehler trat
auf. Diese grüne Diagnosematrix ersetzt weder den roten CI-Lauf
[37892941746](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37892941746)
noch die fehlende Ursachen- und Zeitquellenevidenz. Der Reporter bleibt in
[Draft-PR 128](https://github.com/gecompat/SQL_PerformanceSchulung/pull/128)
`BLOCKED`; dessen Branch sowie der alte PR68-Branch bleiben erhalten.
Die exakte G13-Abnahmerichtung des Benutzers bleibt gewählt. Für eine
Wiederaufnahme sind die echten SQL20-Ist-Counts und Rohzeilen, G13-Rohfragmente
und belastbare Zeitquellenbelege zu prüfen und eine gezielte Gegenprobe
abzuleiten. Ein Methodenwechsel benötigt eine gesonderte Entscheidung.

## Main- und PR-132-Fehler nach dem Diagnose-Merge

Der [Main-Lauf 38050043409](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38050043409)
scheiterte bei SQL Server 2019, `CONTROL_AA / RUN_2`, an G13. Die neue
Rohdiagnose wurde als `INSUFFICIENT|MALFORMED` verworfen. Eine einmalige
isolierte SQL-Server-2019-Probe des verwendeten Style-127-Ausdrucks ergab
`2026-10-10T12:17:11.3875115Z`: Das bisherige Decoderformat ließ das `Z`
nicht zu. Diese belegte Parserursache sagt nichts über die G13-Grenzverletzung.

[Draft-PR 132](https://github.com/gecompat/SQL_PerformanceSchulung/pull/132)
akzeptiert nur siebenstellige UTC-Zeitwerte mit `Z` oder `+00:00` und änderte
keinen SQL-Producer und kein Oracle. In der aktuellen
[Matrix 38051475267](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38051475267)
bestanden 2019 und 2025, während 2022 in `CONTROL_BA / RUN_1` an G13
scheiterte. Der nun erfolgreich decodierte begrenzte Rawblock enthielt genau
zwei positive reguläre Zeilen, je Count 4: Fenster 0 Plan 16 Intervall 2
mit First/Last `12:32:00.2930000Z`/`12:32:00.6570000Z`, Fenster 1 Plan 2
Intervall 3 mit `12:33:00.8500000Z`/`12:33:01.2200000Z`. Die
`ExecutionStarted`-/`ExecutionFinished`-Werte des Fehlerfalls fehlen weiterhin.
Der unabhängige Datenbank-Cleanup und alle Containerabbauten bestanden.
PR 132 bleibt wegen des fachlichen CI-FAILs Draft und ungemergt; kein Bypass.

Die positiven Rohgruppen widerlegen eine allgemeine Zero-Count-Ursache.
Die QS↔SYSUTC-Grenze ist damit nicht entschieden. SQL20-Ist-Counts eines
tatsächlichen Fehlers fehlen ebenfalls. Unter der vom Benutzer ausgewählten
exakten G13-Abnahme bleiben Reporter-PR 128 und Parserfix-PR 132 blockiert.
Wiederaufnahme braucht vollständige Fehler-Zeitgrenzen und eine gezielte
Gegenprobe; eine andere Zuordnungsmethode verlangt die gesonderte
Entscheidung samt offenen Gates des Methodenpakets.

## Isolierte Zeitquellen-Gegenprobe vom 2026-10-10

Der erneute Benutzerauftrag „weiterführen“ autorisiert den begrenzten
Korrekturscope. Eine neue Gegenprobe untersucht die Zeitklammer getrennt vom
DGN-007-Datenmodell: frischer eigener Docker-Container, SQL Server 2022
Developer `16.0.4265.3`, Image `2022-latest`, vier CPU und 8 GiB Limit.
Das tatsächlich verwendete Image war digestgebunden an
`sha256:ba4c8329f48fb8f02e1416be6a930ebfd71268caee78aa985f3af4315e457c89`;
Repositorybasis vor dem lokalen Kandidaten: `642bb09`.
Nur eine eigene synthetische Datenbank mit vier Projekt-/Vertrags-/Demo-/Runmarkern
wurde erzeugt. Es gab keine fremden Benutzerdatenbanken und keinen Zugriff auf
die anderen laufenden Container. Diese Probe ist keine DGN-007-Abnahme.

Query Store wurde auf `READ_WRITE`, Capture `ALL` und einminütige Intervalle
gesetzt. Eine Tabelle enthielt die vier Zahlen 1, 2, 3, 4. 32 verschiedene,
innerhalb des SELECT-Statements markierte parameterisierte Abfragen berechneten
`SUM(n) WHERE n>@p` mit `@p=0`. Nach einmaligem Warmup dieser 32 Statements
und `QUERY_STORE CLEAR ALL` wurde jedes Statement genau einmal zwischen
zwei unmittelbar davor/danach gespeicherten `SYSUTCDATETIME()`-Werten ausgeführt.
Nach dem Flush wurden die regulären Rawfragmente je eindeutiger Querymarkierung
über Query-/Planbindung aggregiert. Alle 32 Gruppen hatten Count 1, alle
berechneten Werte waren 10; die gemessenen Query-Store-Durations lagen bei
26 bis 57 Mikrosekunden. Die Warmup-Ausführungen sind in diesen Counts nicht
enthalten. Die Auswertung behauptet keine atomare Sicht der Katalogsichten.

Bei **31 von 32** Messpaaren lag `first_execution_time` vor dem zuvor
gespeicherten Start. Der größte negative Abstand war **75.996 Ticks =
7,5996 ms**. Ein konkretes Paar war Start/Finish
`2026-10-10T13:44:14.0075996Z`, First/Last
`2026-10-10T13:44:14Z`, Count 1, Duration 27 Mikrosekunden.
Kein Last-Wert lag oberhalb der jeweiligen Finish-Grenze. SYSUTC-Starts und
QS-First-Werte nahmen jeweils sieben verschiedene Werte an; die Probe
belegt weder eine universelle Quantisierung noch eine konkrete interne Clock-
Implementierung. Sie widerlegt jedoch für diese Umgebung die Voraussetzung,
dass eine korrekt erfasste erfolgreiche Ausführung zwingend in der exakten
QS↔SYSUTC-Klammer liegt. Die Abweichung über 1 ms widerlegt zusätzlich eine
Erklärung allein durch Abschneiden der SYSUTC-Nachkommastellen auf volle ms.
Die historischen SQL20-Countfehler werden dadurch nicht erklärt.

Ein erster Instrumentierungsvorlauf mit nachgestellten Querymarkierungen
lieferte keine zugeordneten Capturegruppen und wurde als
`CAPTURE_INSUFFICIENT` abgewiesen. Nur der korrigierte SELECT-interne Marker
erbrachte den obigen Count-1-Nachweis. Es wurde keine unveränderte DGN-007-Matrix
wiederholt. Beide eigenen Datenbanken wurden markergebunden entfernt,
ihre erste unabhängige Abwesenheitsprüfung bestand. Beide Container wurden
nach vollständiger CID-/Name-/Scope-/Eigentümerprüfung entfernt und unabhängig
abwesend geprüft. Gemessene Gesamtwalltime beider Versuche einschließlich
Cleanup: 21,592 s. Modell-/Tokenverbrauch ist unbekannt; keine Unteragenten.

Microsoft Learn beschreibt First/Last als Ausführungs-Endzeit und unterscheidet
bei SYSUTCDATETIME Präzision und Genauigkeit; daraus folgt keine gemeinsame
100-ns-Genauigkeit dieser beiden Quellen. Quellen am 2026-10-10 erneut geprüft:
[Query-Store-RuntimeStats](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17),
[SYSUTCDATETIME](https://learn.microsoft.com/en-us/sql/t-sql/functions/sysutcdatetime-transact-sql?view=sql-server-ver17).

### Konkreter Vorschlag; Methodenentscheidung noch ausstehend

Die QS↔SYSUTC-Klammer soll als Zuordnungsbeweis abgelöst werden; die exakten
Abstände bleiben als Diagnose erhalten. Die Alternative muss tatsächliche
erfolgreiche Calls, vollständige Query-/Planfamilien, korrekte Rawaggregation
ohne Doppelzählung, nachvollziehbare T0-/T1-Intervallzuordnung und die
Sichtbarkeits-/Zustandsgrenzen nach dem bestehenden
[Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md) belegen.
Ein bloßer Count 4 oder ein passendes Intervall reicht dafür nicht.
Der Vorschlag aktiviert keinen Puffer, keine Rundung, keine Capänderung und
keinen CI-Bypass. Auswahl und neuer registrierter DEC sind vor einer normativen
G13-Änderung erforderlich. Bis dahin bleibt G13 unverändert und die Reporter-
Integration blockiert. Die konkrete Auswahl wurde beim Benutzer angefragt.

Unabhängig davon zeigte die neue Probe einen weiteren realen Style-127-Fall:
bei vollen Sekunden entfällt der Bruchteil vollständig (`13:44:14Z`). Der lokale
Parserkandidat auf dem vorhandenen PR-132-Branch akzeptiert deshalb neben sieben
Nachkommastellen auch keinen Bruchteil, jeweils ausschließlich mit `Z` oder
`+00:00`. Positivkontrollen für beide Formen und eine Negativkontrolle für
abweichende Bruchteillänge erhalten die Kanal-, Scope-, Guard-, Count-, Overflow-
und Cleanupbindungen. Der neue CPython-3.12-Runner-AST-Digest ist explizit
gebunden; die acht anderen Digests bleiben unverändert. Dieser lokale Kandidat
ist keine G13-Korrektur, nicht nach Main übernommen und noch nicht neu in CI
ausgeführt. Er wird vor der abhängigen Methodenentscheidung nicht als neuer
unveränderter Matrixversuch gepusht.
Die 46 lokalen Runner-Testmethoden, Capture-Projektions-/Kontrollvalidatoren,
Privacy und `diff --check` bestanden. Das direkte CPython-3.12-Kantenprofil
bestand für die aktuellen Working-Tree-Bytes einschließlich aller neun ASTs,
Manifeste und Policy; eine zusätzliche ausführbare AST-Zeile wurde als
`PYTHON_PROFILE_CHANGED` abgewiesen. Das ist kein erneuter Lauf der vollständigen
commitgebundenen Offline-Suite und keine Runtimequalifikation des Parserkandidaten.
