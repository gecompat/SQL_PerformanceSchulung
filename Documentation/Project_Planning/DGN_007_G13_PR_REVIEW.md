# DGN-007 – G13-Fehler und Abschluss von PR 68

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-09 |
| Auftrag | Ursache und Nutzen des liegengebliebenen Diagnose-PR prüfen und den relevanten Abschluss verfolgen |
| geprüfte Main-Basis | `174076b505b4f317a0b3f2fe7830ae3244ff03d3` |
| aktueller Abgleich nach Foundation-Upgrade | `2f04deb2fed0faf5bedf70101fea3f4b93d46678`, [PR 123](https://github.com/gecompat/SQL_PerformanceSchulung/pull/123) |
| ursprünglicher Reporter-Head | `27a9b5ce81347beaa6d6bfd8788c62965495f0ca` |
| aktualisierter Reporter-Kandidat | `f9ec582017c942e4278252427c62695e313d37f9` |
| aktuelle Codefreigabe | `BLOCKED` – zwei aktuelle substantielle Runtimefehler; kein Merge oder Bypass |
| Arbeit | [PR 68](https://github.com/gecompat/SQL_PerformanceSchulung/pull/68), `codex/dgn007-g13-boundary-report` |
| Ergebnisgrenze | Diagnosepaket; keine G13-Behebung, Methodenwahl oder Incidentfreigabe |

## Problem und nachweisbare Ursache des Fehlschlags

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
wäre keine kleine Fehlerkorrektur. Die Auswahl wurde dem Benutzer konkret
vorgelegt; keine Variante ist stillschweigend aktiviert.

Jeder später korrigierte Reporter-Kandidat benötigt Quellen-/Vertragsabgleich
gegen den dann aktuellen Main-Stand, passende lokale Gegenproben und erfolgreiche
relevante CI für den exakten Head/Base. Erst danach Integration und eigene
Branchbereinigung. Alte Failures bleiben sichtbar. Foundation-/Prozessupgrade
ist bereits getrennt abgeschlossen; allgemeine Welle und Automation bleiben
pausiert. Die Ursache-/Methodenarbeit ist mit diesen Wiederaufnahmebedingungen
offen, nicht als erledigte Reparatur geführt.
