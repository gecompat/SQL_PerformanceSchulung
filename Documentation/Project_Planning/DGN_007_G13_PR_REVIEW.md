# DGN-007 – G13-Fehler und Abschluss von PR 68

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-09 |
| Auftrag | Ursache und Nutzen des liegengebliebenen Diagnose-PR prüfen und den relevanten Abschluss verfolgen |
| geprüfte Main-Basis | `174076b505b4f317a0b3f2fe7830ae3244ff03d3` |
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
