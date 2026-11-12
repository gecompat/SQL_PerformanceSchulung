# Nächste Entwicklungswellen

## Aktuelle autonome Fortsetzungsplanung vom 8. November 2026

### Begrenzung der Fortsetzung vom 12. November 2026

Der Nutzer hat die Bearbeitung aller restlichen freigegebenen Themen fortgesetzt
und sechs weitere Quellen-/Testkandidaten freigegeben. Für diese begrenzte
Fortsetzung gelten höchstens zwei Arbeitspakete, zwei Pull Requests und sechs
neue Quellen-/Vertragskandidaten. Das erste Paket, der External-Tables-
Konzeptentwurf, ist integriert; es verwendete keine neue Produktquelle und
zwei lokale Vertrags-/Lesepfadprüfungen. Die bestehenden `SRC-153` bis
`SRC-157` werden wiederverwendet und nicht als neue Quellenkandidaten gezählt.
Das zweite Paket beschränkt sich auf den Quellenabgleich der bestehenden
`CLM-045`-Traceability. Checkpoint ist spätestens die zweite PR-Integration.
SQL, Connector, Netzwerk, Dienst, Credential und menschliche Generalprobe sind
nicht Teil dieses Rahmens. Token- und Geldverbrauch sind nicht verlässlich
gemessen. Die Fortsetzung setzt die kumulative Budgethistorie nicht zurück;
der letzte ältere Summenstand ersetzt keine aktuelle Verbrauchsprüfung.

Die Fortsetzung nach PR #530 ergänzte `LO-M03-05` durch die
[External-Tables-Lernnotiz](../Curriculum/EXTERNAL_TABLES_LESSON.md); PR #531
integrierte sie mit sieben erfolgreichen CI-Checks. Sie bleibt erklärender
Inhalt ohne Demo-ID oder Lauf-/Messclaim.

Nach dem Checkpoint durch PR #531 setzt die ausdrückliche Anweisung des
Nutzers zur autonomen Bearbeitung aller übrigen freigegebenen Themen den
Auftrag fort. Für den nächsten eigenständigen Graph-Tables-Lehrnotizschnitt
gilt eine weitere begrenzte Fortsetzung von höchstens einem Arbeitspaket,
einem Pull Request und zwei Quellen-/Vertragskandidaten. Die vorhandenen
`SRC-122` und `SRC-124` sowie der abgeschlossene T-SQL-Syntaxreview bilden die
Quellenbasis; neue Produktquellen werden nicht benötigt. Checkpoint ist die
PR-Integration. Keine SQL-, Lab- oder Runtimeausführung und keine menschliche
Generalprobe. Kein Budgetreset und keine monetäre/tokenbasierte
Verbrauchsbehauptung.

Das Arbeitspaket ergänzt `LO-M03-06`/`CLM-047` mit einer quellengebundenen
Erklärung des Graph-gegen-relationalen Zwei-Kanten-Pfads und führt sie im
Curriculum-Lesepfad auf. Es übernimmt keine Performanceaussage des
PROPOSED-Demoentwurfs.

Nach PR #532 ist diese Graph-Notiz integriert. Die ausdrückliche Fortsetzung
aller übrigen freigegebenen Themen eröffnet eine neue, endliche Welle für die
Curriculum-Scopeentscheidung zu External Tables: höchstens ein Arbeitspaket,
ein PR und zwei lokale Vertrags-/Curriculumkandidaten; keine neuen
Produktquellen. Der Checkpoint ist die PR-Integration, die harte Grenze ein
Paket/ein PR/zwei Kandidaten. Verlässliche Token- und Geldmessung fehlt; die
Grenze wird daher über Arbeitspaket, PR und Kandidaten geprüft, nicht als
Provider-Ausgabenlimit ausgegeben. Ziel ist eine quellengebundene Empfehlung,
ob die vorhandene External-Tables-Lernnotiz QRY-012 als ausführbare Phase
erweitern sollte. SQL, Runtime, Connector, Netzwerk, Dienst, Credential und
menschliche Generalprobe bleiben ausgeschlossen.

Die [Scopeempfehlung](EXTERNAL_TABLES_CURRICULUM_SCOPE_REVIEW.md) ist erstellt:
External Tables bleiben eine ergänzende Erklärung zu `LO-M03-05`/`CLM-045`;
eine weitere ausführbare Phase in `QRY-012` wird bis zu einer registrierten
Projektentscheidung und einem eigenen Infrastruktur-/Methodenvertrag nicht
empfohlen. Zwei lokale Curriculum-/Vertragskandidaten wurden gegengeprüft; es
wurden keine neuen Produktquellen verwendet. Das Paket bleibt innerhalb des
1/1/2-Rahmens; der PR-Checkpoint ist noch offen. Die formale Entscheidung,
Demo-ID, Methoden- und Runtimefreigabe bleiben offen.

Der Nutzer hat anschließend die verbleibenden offenen Themen ausdrücklich
freigegeben. Für die formale Registrierung der bereits geprüften
Curriculumentscheidung gilt eine weitere endliche Welle von höchstens einem
Arbeitspaket, einem PR und zwei lokalen Entscheidungs-/Vertragskandidaten;
keine neuen Produktquellen. Der PR-Merge ist der Checkpoint, die Grenze ist
1/1/2 ohne Reset. Token- und Geldverbrauch bleiben unbekannt. Scope: DEC-078
bindet den erklärenden External-Tables-Lehrpfad an `LO-M03-05`/`CLM-045` und
entscheidet gegen eine ausführbare External-Tables-Phase in `QRY-012` im
aktuellen Curriculumstand. Keine Demo-ID, SQL-, Infrastruktur- oder
Runtimefreigabe. DEC-078 und der Registrydatensatz sind angelegt; lokale
Registry- und Projektchecks sowie der PR-/Integrationsabschluss sind mit PR
#534 abgeschlossen. Der Main-Stand ist `9aaa1b1`.

### Graph Tables: formale Freigabe der statischen Methodik

Die ausdrückliche Freigabe aller verbleibenden offenen Themen eröffnet für
QRY-023 ein begrenztes Offline-Arbeitspaket: höchstens ein Paket, ein PR und
zwei lokale Entscheidungs-/Vertragskandidaten; keine neuen Produktquellen.
Der Checkpoint ist die PR-Integration. Token- und Geldverbrauch bleiben
unbekannt; der Rahmen wird über Paket/PR/Kandidaten begrenzt und ist kein
Provider-Ausgabenlimit. Die bestehende Methodik aus Quellen-/Methodenreview,
Messworkload und Framework-/Matrixreview wird für die weitere statische
Vertragsimplementierung genehmigt und als `DEC-079` registriert. QRY-023 bleibt
`PROPOSED`. Keine SQL-/Lab-/Runtime-Ausführung, Rechteänderung, Infrastruktur,
neue Performanceaussage oder menschliche Generalprobe.

PR #535 integrierte `DEC-079` am Commit `6bbc09e`; der getestete Baum wurde
unverändert übernommen und `main` synchronisiert. Die nächste autonome Welle
begrenzt sich auf ein Arbeitspaket, einen PR und zwei Quellen-/Vertragskandidaten.
Sie registriert `DEC-080` für die statische ScriptDom-Syntaxakzeptanz der acht
ausführbaren QRY-023-T-SQL-Dateien unter 150/160/170 und synchronisiert die
betroffenen Lesepfade. Keine neuen Produktquellen, kein SQL-/Lab-/Runtimelauf,
keine menschliche Generalprobe. Token- und Geldverbrauch bleiben unbekannt;
Paket/PR/Kandidaten begrenzen den Umfang, nicht Providerkosten.

Nach lokaler gesperrter Parserprüfung und Projektvalidierung ist PR-Integration
der Checkpoint. Formale Harnessabnahme, phasenspezifische Identität,
Build-/Image-, Ressourcen-, Cleanup- und Runtimegates bleiben offen.

PR #536 integrierte `DEC-080` am Commit `73ef23a`; alle zehn CI-Checks waren
erfolgreich, der getestete Baum wurde übernommen, `main` synchronisiert und
der lokale sowie Remote-Arbeitsbranch entfernt. Für den nächsten offenen
Offlinepunkt gilt ein Paket, ein PR und zwei Quellen-/Vertragskandidaten. Der
bestehende `SRC-127`-Servicingeintrag wird neu geprüft; keine neue Produktquelle,
kein Container-/Imageabruf, kein SQL-/Lab-/Runtimelauf und keine menschliche
Generalprobe. Der Quellencheck bestätigt allein, dass die vorhandenen drei
Designpins weiterhin den neuesten Microsoft-Linux-Servicingbuilds entsprechen.
Die bisherigen OCI-Digests bleiben auf ihrem Quellenstand 7. November datiert.
Token- und Geldverbrauch bleiben unbekannt; Umfang ist über Paket/PR/Kandidaten
begrenzt, nicht monetär.

PR #537 integrierte `DEC-081` am Commit `9274937`; elf Checks waren erfolgreich,
`main` ist synchronisiert und der lokale/Remote-Branch entfernt. Der nächste
Offlinepunkt prüft innerhalb eines Pakets, eines PRs und höchstens zwei
Quellen-/Vertragskandidaten read-only die aktuellen MCR-Manifest- und
Konfigurationsdigests der drei bereits vorgeschlagenen Tags gegen den Lock.
Kein Image-Layerdownload, Build, Containerstart, SQL, Runtime oder menschliche
Generalprobe. `SRC-130` wird aktualisiert; Runtimecallerintegration bleibt ein
separates Gate. Verbrauch in Tokens/Geld ist nicht verlässlich messbar.

PR #538 integrierte `DEC-082` am Commit `ffaa196`; elf Checks waren erfolgreich,
`main` ist synchronisiert und der lokale/Remote-Branch entfernt. Der nächste
begrenzte Offlinepunkt aktualisiert innerhalb eines Arbeitspakets, eines PRs und
höchstens zwei bestehenden Quellen-/Vertragskandidaten die Editionsmatrix
`SRC-126` und den zugehörigen QRY-023-Review anhand der drei offiziellen
Microsoft-Editionsseiten. Keine neue Produktquelle, Engineabfrage, Imageaktion,
SQL-/Lab-/Runtimeausführung oder menschliche Generalprobe. Das belegt allein
die dokumentierte Verfügbarkeit, keine tatsächliche Edition oder Qualifikation.
Token- und Geldverbrauch bleiben unbekannt; Paket/PR/Kandidaten begrenzen den
Umfang, nicht Providerkosten.

PR #539 aktualisierte `SRC-126`; PR #540 erfasste den weiterhin offenen
DGN-004-Isolationsblocker. Beide sind integriert. Für den nächsten Offlinepunkt
gilt ein Arbeitspaket und ein PR mit höchstens drei Vertragskandidaten: FWK-010
erweitert den Caller um optionale SQL-Anmeldungsprofile je Phase; QRY-023 ordnet
das vorhandene Rechteprofil ADMIN beziehungsweise READER den Phasen zu; die
DGN-007-Prozesskantenprüfung bindet den angepassten `run_demo.py`-AST weiter
exakt. `sqlcmd_process.py` bleibt unverändert, damit der unabhängige CON-010-
Collectorvertrag unverändert gilt. Keine neue Produktquelle, keine
Loginerstellung, Rechteänderung, SQL-, Lab- oder Runtimeausführung und keine
menschliche Generalprobe. DGN-007-Quellenbundle-, Kanten- und Harnessloader-
prüfungen bleiben gebundene Verbraucher. Der Client-Identitätswechsel schließt
keine Serverrechte-, Ressourcen-, Abbruch-, Cleanup- oder Runtimequalifikation.
Token- und Geldverbrauch sind unbekannt; Umfangsgrenze ist 1/1/3 aus den sechs
freigegebenen Kandidaten, ohne Reset.

PR #541 integrierte die phasenspezifischen SQL-Anmeldungsprofile über Squash
`e430cde`; 77 PR-Checks und die ausgelösten Main-Workflows bestanden. Main ist
synchronisiert, der lokale und Remote-Branch sind entfernt. Der folgende
begrenzte Offlinepunkt klärt die Grenze zwischen positiven `READER`-
Rechteprüfungen und dem weiterhin offenen Nachweis fehlender Zusatzrechte.
Microsofts Rollenfunktionen prüfen Mitgliedschaft, nicht effektive Rechte, und
benötigen Rollenmetadatensicht. Die QRY-023-Dokumentation hält deshalb fest,
warum sie allein kein Minimalrechte-Gate bilden. Keine Änderung an
Serverprinzipalen oder Grants, kein SQL-/Runtime-/Lab-Lauf und keine
menschliche Generalprobe. Umfang: ein Arbeitspaket, ein PR, zwei
Dokumentationskandidaten; verbleibende SQL-, Rechte-, Ressourcen-, Abbruch-,
Cleanup- und Runtimegates bleiben offen.

PR #542 integrierte diese Rollenfunktionsgrenze. Der nächste Offlinepunkt
konkretisiert den Soll-Ist-Prüfansatz, ohne bereits eine Rechteprüfung oder
Runtimefreigabe zu behaupten: `sys.fn_my_permissions` wird als möglicher
Abgleich effektiver Rechte im tatsächlichen `READER`-Kontext dokumentiert.
README und Harnessreview müssen Server-, Datenbank-, Schema- und Objektkontexte,
eine vorab festgelegte phasengenaue Sollmenge, fail-closed Verhalten sowie die
Grenzen zu anderen Principals und Ownership Chain gemeinsam abbilden. Grenze:
ein Arbeitspaket, ein PR, zwei bestehende Dokumentationskandidaten; innerhalb
der sechs freigegebenen Kandidaten, ohne Reset. Keine neue Produktquelle, keine
Serverprinzipal-/Grantänderung, kein SQL-/Lab-/Runtime-Lauf und keine
menschliche Generalprobe. Der verbleibende Lauf- und Minimalrechtenachweis
bleibt offen.

Diese Planung konkretisiert den aktiven Auftrag in
[`CURRENT_EXECUTION_STATUS.md`](CURRENT_EXECUTION_STATUS.md). Sie ersetzt die
überholten Statusangaben der nachfolgenden historischen Planung, insbesondere
die dort genannten Pausen bis zum 20. Oktober. Sie setzt weder neue fachliche
Freigaben noch Laufrechte oder Budgets. Reihenfolge, Umfang und Status werden
vor jedem neuen Arbeitspaket gegen den aktuellen kanonischen Ausführungsstand,
die betroffenen Verträge und den verbleibenden Gesamtbudgetstand abgeglichen.

### Arbeitsfolge

| Schritt | Arbeit und Abschlusskriterium | Grenze / Folgeentscheidung |
|---|---|---|
| 1. DGN-004 statische Annahmeprüfung | Der reine Neun-Aufruf-/Statusprüfer und seine synthetischen Gegenfälle sind integriert. Der unabhängige Methoden-/Quellen-/Zuordnungs-/Transport-/Messreview vom 2026-11-12 fand nach PR #518 keine offenen P1/P2. Eine erneute read-only Inventur am 2026-11-12 fand fünf aktive, nicht DGN-004 zugeordnete SQL-Server-Container (2017, 2019, 2022, zweimal 2025); kein Container wurde verändert. | Das YELLOW-Isolations-/Lastgate ist weiterhin nicht erfüllt. Keine SQL-/Lab-Ausführung, bis eine kontrollierte Wegwerfumgebung belegbar ist. Danach gelten unverändert Zielbuilds 2022/16.0.4265.3 und 2025/17.0.4075.5, neun Aufrufe je Build, zwei eigene sequenzielle Container, 900 Sekunden gemeinsames Laufbudget plus je 60 Sekunden Cleanup. |
| 2. QRY-002 Lehrnotiz | PR #383 integrierte die quellengebundene Erklärung beider Konvertierungsrichtungen und trennt Typauflösung von konkreter Zugriffswirkung. | Menschliche Generalprobe bleibt ausgeschlossen. Kein Scan-/Seek- oder Leistungsclaim ohne konkrete Plan- und Messbelege. |
| 3. Lesepfade und Kerninhalte | QRY-003/RES-004-Pfade sowie QRY-007 und IDX-003/004/001/002 sind quellengebunden integriert. PR #394 integrierte STL-001, PR #395 STL-002, PR #396 QRY-005, PR #397/#398 OPT-004, PR #399 STL-003, PR #400 QRY-011, PR #401 IDX-005, PR #402 OPT-012, PR #403 STL-010, PR #405 QRY-003, PR #406 QRY-007, PR #408 IDX-003, PR #410 IDX-004, PR #412 IDX-001, PR #414 IDX-002, PR #416 STL-001 und PR #418 STL-002. STL-002 bindet vollständige Nutzdaten- und Padding-Formeln sowie Mengentupeloracles für alle drei Speicherprofile. | Keine SQL-/Runtimefreigabe. STL-001/002 enthalten synthetische Entwurfsoracles; reale Record-/Seiten- und Allocation-Unit-Evidenz sowie Lese-I/O bleiben offen. |
| 4. Diagnose- und vorhandene KI-Qualifikation | Jeweils nur den im aktiven Status ausgewählten, unabhängig prüfbaren Schnitt vorbereiten; Verträge, synthetische Prüfungen und erforderliche Reviews vor jeder Runtimephase abschließen. | Kein SQL-/Provider-/Netzwerk-/Lab-Effekt aus statischer Evidenz ableiten. Lauf-, Provider- und Datenfreigaben gelten pro konkretem Schnitt. |
| 5. CON-006- und IDX-007-Varianten | Der synthetisch geprüfte CON-006-Offline-Graph- und Capturevertrag sowie der IDX-007-Offlinevertrag für caller-supplied `PAGELATCH_EX`-Waits sind im Framework-Contracts-Workflow enthalten. PR #420 ergänzt die IDX-007-Prüfung: fehlender Rechtsaußenbeleg ist `NOT_PROVEN`, expliziter Gegenbeleg `FAIL`. PR #422 prüft den CON-006-Graph-/Capturevertrag lokal. Die unabhängigen Offline-Methoden-/Quellenreviews vom 12.11.2026 fanden nach Timestamp-Korrekturen keine offenen P1/P2 im geprüften Parser-/Quellenumfang. Die aktuellen Herstellertexte spezifizieren das genaue `requestType="convert"`-Schema nicht; Herkunftsbindung der Capturefelder, dessen Engine-Qualifikation und IDX-007-Seitenkettenauflösung bleiben offen. Vor Laufvarianten folgen empirische Darstellung, fairer IDX-007-Vergleich und tatsächlicher Wait-/Page-Nachweis. | Graph, Zeitfenster, Marker, Eventquelle, Actorresultate, Waits und Seitenfelder sind caller-geliefert und unauthentifiziert. Der statische `PASS` ist kein Laufzeit- oder Engpassnachweis. Range bleibt zurückgestellt. Kein SQL-/Lab-Lauf ohne konkreten Demo-Vertrag, Methodenfreigabe und Safety-/Cleanup-Gates. |
| 6. Nachgelagerte Erweiterungen | Der statische RES-001-Offlineschnitt und RES-003-Offlinevertrag samt quellengebundener Lehrnotiz sind integriert. Die Detailprüfung zu SQL-Server-2025-`OPTIMIZED_SP_EXECUTESQL` ist abgeschlossen; Aktivierung, Demo und Performanceclaim bleiben `DEFER`, weil die bestehende `QRY-004`-Abnahme keine zeitgleiche Kompilierung prüft. Die [Graph-Table-Quellen- und Abdeckungsprüfung](GRAPH_TABLES_SOURCE_COVERAGE_REVIEW.md) empfiehlt Graph Tables als ersten Offline-Entwurf; die [Versions- und Indexprüfung](GRAPH_TABLES_VERSION_INDEX_REVIEW.md) und die [2022/2025-Releaseübersichtenprüfung](GRAPH_TABLES_2022_2025_SOURCE_REVIEW.md) binden die begrenzte Versionssicht. `LO-M03-06`/`CLM-047` ist der bestehende Curriculum-Anker; [Demoentwurf und Vertrag](GRAPH_TABLES_DEMO_CONCEPT.md), [T-SQL-Syntaxreview](GRAPH_TABLES_TSQL_SYNTAX_REVIEW.md), [Messworkload](GRAPH_TABLES_MEASUREMENT_WORKLOAD_DESIGN.md) und [Quellen-/Methodenreview](GRAPH_TABLES_METHOD_REVIEW.md) legen Korrektheitsoracle, 10.000-Pfade-Profil, `MATCH`, Kandidatenindizes und getrennte Mess-/Planevidenz dar. `QRY-023` ist unter `TSK-017` registriert und bleibt `PROPOSED`; Graph-Tabellen verlangen eine eigene markierte Testdatenbank. Das Framework-/Curriculumreview bindet die Zielmatrix 2019/150, 2022/160, 2025/170 und Plan-/Baseline-/Vergleichsmessung. PR #525 bindet den letzten `SQLCMDMAXVARTYPEWIDTH`-Wert vor der XML-Planphase gegen spätere Überschreibungen. Ein lokaler Harness-Codeentwurf ist vorhanden, aber nicht abgenommen oder katalogisiert. Der unabhängige Offline-Review ist abgeschlossen; formale Methodenfreigabe, Vertrags-/T-SQL-Abnahme, konkrete Index-/Build-/CU-Definitionen und Runtimefreigaben bleiben offen. Für External Tables liegt jetzt der [statische Lehr- und Demoentwurf](EXTERNAL_TABLES_DEMO_CONCEPT.md) als Vorschlag zu `LO-M03-05`/`CLM-045` und einer möglichen `QRY-012`-Ergänzung vor; die formale Curriculumentscheidung und alle Infrastruktur-/Laufgates bleiben offen. | RES-003 bleibt ein roter, nicht ausführbarer Druckversuch; `OPTIMIZED_SP_EXECUTESQL` erhält keine Runtimefreigabe. Graph Tables bleiben `PROPOSED`; `QRY-023` besitzt nur einen lokalen, nicht katalogisierten Codeentwurf und keine Runtimequalifikation und behauptet keine allgemeine Leistungsrangfolge. External Tables besitzen weiterhin keine Demo-ID und keine Laufzeitqualifikation; das Konzept behauptet weder eine allgemeine Rangfolge noch tatsächliches Pushdown ohne korrelierte Evidenz. Statische und quellengebundene Erklärung ersetzt weder authentische Runtime-Evidenz noch Kausalitätsnachweis. Weitere Ressourcen und Infrastruktur nur mit eigenem Methoden-, Versions-, Sicherheits- und Cleanupvertrag. |

PR #424 bindet beim QRY-023-Proposed-Harness Phasenscript, Zieldatenbank,
Zeitlimits, Cleanup und Gesamtbudgets. PR #426 ergänzt `Reads` und `Writes` als
Pflichtfelder und gepaarte Statistikmetriken neben CPU, Logical Reads und
Elapsed; Zähler bleiben Sessiondeltas einschließlich Messprozedur-Overhead.
PR #429 schützt das Abschalten von `STATISTICS XML` bei Erfolg und fangbaren
Fehlern in der separaten Actual-Plan-Phase nach dem FWK-005-Cleanupmuster. Der
Validator und eine Negativregression binden den Fehlerpfad; Verbindungsabbruch
und tatsächliche Sessionwirkung bleiben unbelegt. PR #431 bindet beide
`COUNT_BIG`-Planabfragen per normalisiertem Statementvergleich an die Graph-
und Relationsvarianten der Messprozedur; zwei Negativregressionen schützen
Graph-`MATCH` und den relationalen Zieljoin. 19 QRY-023-Regressionen sowie die
statischen QRY-023-, Framework- und Repository-Continuity-Prüfungen bestanden.
Das bleibt eine Textstrukturprüfung ohne SQL-/Runtime- oder Lab-Ausführung.
QRY-023 bleibt `PROPOSED`; formale T-SQL-Abnahme, unabhängige
Methodenfreigabe und Runtimegates bleiben offen.
PR #433 schützt die Reihenfolge von erfolgreicher Plan-Summary und
`STATISTICS XML OFF` einschließlich TRY/CATCH-Grenze. Die gezielte
Negativregression weist vorgezogenes PASS zurück; 20 QRY-023-Regressionen und
die statischen QRY-023-, Framework- und Repository-Continuity-Prüfungen
bestanden. Dies belegt nur Textreihenfolge, keine SQL-/Runtimeausführung oder
Sessionwirkung. QRY-023 bleibt `PROPOSED`; formale T-SQL-Abnahme, unabhängige
Methodenfreigabe und Runtimegates bleiben offen.
PR #435 bindet die Summaryfelder `Phase=PLAN_EVIDENCE`, `CheckId=SUMMARY`,
`Outcome=PASS`, `Code=OK` und den korrespondierenden PASS-Print. Die
Negativregressionen mit WARN-Outcome und Fehlercode werden abgewiesen.
22 QRY-023-Regressionen und die zugehörigen statischen Projektprüfungen
bestanden. Dies belegt keine SQL-Ausführung oder Ergebniswahrheit; QRY-023
bleibt `PROPOSED` und alle formalen sowie Runtimegates bleiben offen.
PR #437 bindet beide Planabfragen statisch innerhalb des
`STATISTICS XML ON/OFF`-Fensters; eine Negativregression verschiebt sie vor
`BEGIN TRY` und wird abgewiesen. 23 QRY-023-Regressionen und die statischen
QRY-023-, Framework- und Repository-Continuity-Prüfungen bestanden. Keine
SQL-/Runtimeausführung; die formalen T-SQL-, Methoden- und Runtimegates bleiben
offen.
PR #439 bindet `SHOWPLAN` an `DB_NAME()`/`DATABASE` und `SELECT` an alle vier
Querytabellen. Scope-, Tabellenrecht- und Skip-Code-Negativfälle werden
abgewiesen; 26 QRY-023-Regressionen sowie die statischen Projektvalidatoren
bestanden. Es wurde kein Recht erteilt oder SQL ausgeführt. Formale T-SQL-,
Methoden- und Runtimegates bleiben offen.
PR #441 bindet beide Qualification-Preflight-Statuszeilen und ihre PRINT-Marker.
Drei Negativregressionen für Skip-Outcome, Erfolgs-Outcome und Skip-Print werden
abgewiesen; 29 QRY-023-Regressionen und die statischen Projektvalidatoren
bestanden. Keine Rechteänderung oder SQL-Ausführung.
PR #443 bindet Systemdatenbankausschluss und den `DB_NAME()`/
`@TargetDatabase`-Abgleich vor der Rechteprüfung. Zwei Negativfälle werden
abgewiesen; 31 QRY-023-Regressionen und die statischen Projektvalidatoren
bestanden nach Korrektur eines lokalen Validatorfehlers. Keine Datenbank- oder
Rechteänderung und kein SQL-Lauf.
PR #445 bindet die vier Ownership-Markerzuweisungen und vollständigen Vergleiche
vor der Rechteprüfung; Projektwert- und RunToken-Negativproben werden
abgewiesen. 33 QRY-023-Regressionen und die statischen Projektvalidatoren
bestanden. Tatsächliche Datenbankmarker wurden nicht gelesen oder verändert.
Der nächste ausgewählte Offline-Schnitt bindet im read-only Preflight den
erwarteten Ziel-Datenbanknamen an Demo-ID und RunToken und schützt die
Längen-/Zeichenmengenprüfung des Tokens durch Negativregressionen. Er erweitert
den kumulativen Rahmen um 1 Arbeitspaket, 2 PRs und höchstens 2
Quellen-/Testkandidaten auf 83/110/193. SQL-/Runtime-/Lab-Ausführung,
Rechteänderungen und menschliche Generalprobe bleiben ausgeschlossen.
PR #447 ergänzt die statische Bindung und drei Gegenproben; 36
QRY-023-Regressionen und die betroffenen Validatoren bestanden. Damit bleibt
der Datenbank- und Runtimezustand unberührt.
Als nächstes bindet ein eigenständiger Offline-Schnitt die boolesche
`OR`-Verknüpfung aller Vertragsguards, damit jede einzelne ungültige Eingabe
zum Abbruch führt. Er erhöht den kumulativen Rahmen um 1 Arbeitspaket, 2 PRs
und höchstens 2 Quellen-/Testkandidaten auf 84/112/195. Keine SQL-/Runtime-/
Lab-Ausführung oder menschliche Generalprobe.
PR #449 bindet die vollständige Guardklausel und weist die `AND`-Gegenprobe ab;
37 QRY-023-Regressionen und die betroffenen statischen Validatoren bestanden.
Die nächste begrenzte Prüfung ergänzt eine `DATALENGTH`-Grenze für das
RunToken, weil `LEN` und ASCII-`LIKE` laut Microsoft-Dokumentation trailing
spaces auslassen. Eine Negativprobe lockert die Byteobergrenze. Kumulativ
85/114/197; Quellen: Microsoft Learn zu [`LEN`](https://learn.microsoft.com/en-us/sql/t-sql/functions/len-transact-sql?view=sql-server-ver17) und [`LIKE`](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver17), abgerufen am 8. November 2026. Keine Engineausführung.
PR #451 bindet `DATALENGTH(@RunToken) NOT BETWEEN 1 AND 20`; eine gelockerte
Byteobergrenze wird durch die statische Negativregression abgewiesen. 38
QRY-023-Regressionen und die betroffenen Validatoren bestanden. Es wurde kein
SQL ausgeführt.
Als nächstes dokumentiert ein begrenzter Schnitt die SQLCMD-Eingabegrenze:
Aufrufer müssen Demo-ID, RunToken und Zielnamen vor SQLCMD allowlisten, da die
T-SQL-Guards erst nach Skriptvariablen-Einsetzung greifen. Dies folgt als
Sicherheitsinferenz aus den Microsoft-Beispielen zur SQLCMD-Skriptvariablen-
Einsetzung. Kumulativ 86/116/199; keine Runtimeautorisierung oder Ausführung.
PR #452 dokumentiert den ausstehenden Caller-Schutz und prüft, dass die
SQLCMD-Eingabegrenze im Demo-Lesepfad genannt bleibt. Eine Negativregression
entfernt die Schutzformulierung; 39 QRY-023-Regressionen und betroffene
Validatoren bestanden. Die Eingabeinjektionsbewertung bleibt eine
quellenbasierte Inferenz, keine Laufbeobachtung.

Der nächste Offline-Schnitt überführt diesen Schutz in ein maschinenlesbares
Manifestobjekt mit exakter Demo-ID, RunToken-Muster, Zielnamenschablone und
Validierungszeitpunkt vor SQLCMD. Der Offlinevalidator bindet die vollständigen
Werte. Kumulativ 87/118/201; kein SQLCMD-Aufruf und keine Runtime- oder
menschliche Generalprobe.
PR #455 integriert `sqlcmd_input_validation`; Gegenproben ändern Prüfzeitpunkt
und Tokenzeichensatz und werden abgewiesen. 41 QRY-023-Regressionen sowie die
betroffenen Projektvalidatoren bestanden. Das Feld bleibt eine Vorgabe für
einen späteren Caller.

PR #457 integriert die optionale Vertragsprüfung vor `resolve_sqlcmd`; die
synthetischen Tests lehnen geänderten Vertrag und bösartigen Token vor jedem
SQLCMD-Prozess ab. Der QRY-023-Manifestentwurf bleibt dennoch nicht
katalogisiert und ungeprüft gegen SQL Server.

PR #458 integriert die RunToken-Vertragsangleichung. Die vollständige CI
endete mit 20/22 erfolgreichen Workflows; zwei unabhängige DGN-007-
Quellenprofilchecks meldeten `PYTHON_PROFILE_CHANGED`. Alle übrigen
Framework-/Runtimeworkflows, einschließlich SQL Server 2025 AI, waren nach
regulärem Abschluss erfolgreich. Kumulativ höchstens 89 Arbeitspakete, 122
PRs und 204 Quellen-/Testkandidaten.

Nachreview zeigte, dass diese Negativregression noch nicht aus der
Testmodul-`main()`-Funktion aufgerufen wurde; der grüne Modultest belegte den
Einzelfall somit nicht. PR #459 registriert und führt `_LOCAL` explizit aus;
der erneute Modultest und alle fünf ausgelösten Workflows bestanden. Die
Ablehnung geschieht vor SQLCMD-Auflösung und -Start. Kumulativ höchstens 90
Arbeitspakete, 124 PRs und 205 Quellen-/Testkandidaten. Keine SQL- oder
Runtimeausführung.

PR #460 ergänzt die ausgeführten synthetischen Caller-Grenzen: gültige
1-/20-Zeichenwerte werden geladen; leere, überlange, nicht-ASCII-,
kleingeschriebene und nachgestellte-Leerzeichen-Token scheitern vor SQLCMD-
Auflösung/-Start. Die QRY-023-, FWK-010- und Repository-Continuity-Prüfungen
bestanden. Kumulativ höchstens 91 Arbeitspakete, 126 PRs und 206 Quellen-/
Testkandidaten. Keine Engine- oder Runtimeausführung.

PR #461 prüft den konkreten `run_token`-Wert im vorgeschlagenen Manifest gegen
dieselbe ASCII-/Zeichen-/Längengrenze, die das maschinelle Caller-Vertragsobjekt
deklariert. Vier Negativproben für Unterstrich am Anfang, Länge, ASCII und
nachgestelltes Leerzeichen bestanden. Kumulativ höchstens 92 Arbeitspakete,
128 PRs und 207 Quellen-/Testkandidaten. Keine Engine- oder Runtimeausführung.

PR #462 ergänzt Negativregressionen für unbekannte Zusatzfelder im exakten
Vertragsobjekt und einen booleschen Wert im Byte-Limit. Beide werden vor
SQLCMD-Auflösung und -Start abgewiesen; alle sechs direkten CI-Workflows waren
grün. Kumulativ höchstens 93 Arbeitspakete, 130 PRs und 208 Quellen-/
Testkandidaten. Keine Vertragsausweitung, Engine- oder Runtimeausführung.

PR #463 pinnt synthetisch die exakte Vertrags-Demo-ID und Zielnamenschablone;
beide veränderten Werte scheitern vor SQLCMD-Auflösung und -Start. Alle fünf
Workflows bestanden. Kumulativ höchstens 94 Arbeitspakete, 132 PRs und 209
Quellen-/Testkandidaten. Keine Runtimeausführung.

PR #464 legt den QRY-023-Vertrag in ein `OPT-001`-Manifest; der Demo-Scope
wird vor SQLCMD-Auflösung und -Start fail-closed durchgesetzt. Alle fünf
Workflows bestanden. Kumulativ höchstens 95 Arbeitspakete, 134 PRs und 210
Quellen-/Testkandidaten. Keine Runtimeausführung.

PR #465 trennt die vom FWK-010-Caller erzwungene alphanumerische
Startzeichenregel von Zeichensatz- und Bytegrenze des vorgeschlagenen
SQL-Preflights. Die Negativregression, 43 QRY-023-Tests und alle sieben
ausgelösten Workflows bestanden. Kumulativ höchstens 96 Arbeitspakete, 136 PRs
und 211 Quellen-/Testkandidaten. Keine SQL- oder Runtimeausführung.

PR #466 setzt den exakten QRY-023-Vertrag in ein `OPT-001`-Manifest; der
Demo-ID-Scopekonflikt wird vor SQLCMD-Auflösung und -Start abgewiesen. Alle
fünf Workflows bestanden. Kumulativ höchstens 97 Arbeitspakete, 138 PRs und
212 Quellen-/Testkandidaten. Keine Runtimeausführung.

PR #467 ersetzt `sqlcmd_input_validation` synthetisch durch eine Liste; die
Zurückweisung vor SQLCMD-Auflösung und Prozessstart sowie die übrigen
Manipulationsgegenproben bestanden. Alle fünf Workflows waren grün. Kumulativ
höchstens 98 Arbeitspakete, 140 PRs und 213 Quellen-/Testkandidaten. Keine
Runtimeausführung.

PR #468 entfernt die doppelte Definition/Registrierung des `OPT-001`-Scope-
Tests und ergänzt eine Driftprobe für `target_database_name()`. Ein vom
Manifesttemplate abweichender Zielname wird vor SQLCMD abgewiesen; alle fünf
Workflows bestanden. Kumulativ höchstens 99 Arbeitspakete, 142 PRs und 214
Quellen-/Testkandidaten.

PR #469 vergleicht die per AST gefundenen `test_*`-Definitionen mit den
Aufrufen in `main()` und verlangt eine exakte Eins-zu-eins-Registrierung. Der
Runner-Test und alle fünf Workflows bestanden. Kumulativ höchstens 100
Arbeitspakete, 144 PRs und 215 Quellen-/Testkandidaten.

PR #470 führt denselben AST-Wächter gegen synthetische Fälle mit korrekter,
fehlender und doppelter Registrierung sowie doppelter Definition aus. Der
Runner-Test und alle fünf Workflows bestanden. Kumulativ höchstens 101
Arbeitspakete, 146 PRs und 216 Quellen-/Testkandidaten.

PR #471 ergänzt Fälle mit fehlendem und doppeltem `main()` und einem Aufruf
eines nicht definierten Testnamens; die Gegenproben wurden erkannt. Der
Runner-Test und alle fünf Workflows bestanden. Kumulativ höchstens 102
Arbeitspakete, 148 PRs und 217 Quellen-/Testkandidaten.

PR #472 ignoriert Testaufrufe in verschachtelten Funktionen und Lambdas; ein
solcher Hilfsaufruf verdeckt keine fehlende `main()`-Registrierung. Der
Runner-Test und alle fünf Workflows bestanden. Kumulativ höchstens 103
Arbeitspakete, 150 PRs und 218 Quellen-/Testkandidaten.

PR #473 zählt nur direkte, unbedingte Testaufrufe in `main()` und dessen
`with`-Blöcken. Eine `if False`-Gegenprobe kaschiert keine fehlende
Registrierung. Der Runner-Test und alle fünf Workflows bestanden. Kumulativ
höchstens 104 Arbeitspakete, 152 PRs und 219 Quellen-/Testkandidaten.

PR #474 berücksichtigt nur synchrone `test_*`-Definitionen als Registrierung;
ein nicht-awaited Aufruf einer Coroutine wird als fehlende Registrierung
abgewiesen. Alle fünf ausgelösten Workflows bestanden. Die bisherige
Obergrenze 105/154/220 ist erreicht. Für den Schattenfall einer gleichnamigen
`def`-/`async def`-Definition erweitert die autonome Fortsetzung den
kumulativen Rahmen einmalig um ein Arbeitspaket, einen PR und einen
synthetischen Kandidaten auf höchstens 106/155/221. Der Wächter muss die
überschreibende asynchrone Definition als Namensduplikat zurückweisen. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #475 integriert die eindeutige Erkennung gleichnamiger synchroner und
asynchroner `test_*`-Definitionen; alle fünf Workflows bestanden. Als nächste
Fortsetzung wird der Rahmen ohne Reset einmalig um ein Paket, einen PR und
einen synthetischen Testkandidaten auf höchstens 107/156/222 erweitert. Die
Gegenprobe definiert erst eine synchrone `main()` und überschreibt sie danach
mit `async def main()`; der AST-Wächter muss den Einstiegspunkt fail-closed
ablehnen. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #476 integriert die Zurückweisung der asynchronen `main()`-Überschreibung;
alle fünf Workflows bestanden. Die Fortsetzung erweitert den Rahmen ohne Reset
um ein Arbeitspaket, einen PR und einen Testkandidaten auf höchstens 108/157/223.
Der Wächter prüft nun auch den direkten Modulaufruf unter dem
`__main__`-Guard und die Weitergabe des Rückgabecodes über
`raise SystemExit(main())`. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #477 bindet die Modulstartbedingung und die Weitergabe des `main()`-
Rückgabecodes. Alle fünf Workflows bestanden. Der kumulative Rahmen wird für
die drei synthetischen Gegenproben ohne Reset um ein Arbeitspaket, einen PR
und bis zu drei Testkandidaten auf höchstens 109/158/226 erweitert: umgedrehte
`__name__`-Bedingung, direkter Aufruf ohne `SystemExit` und Funktionsreferenz
statt Funktionsaufruf. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #478 integriert alle drei negativen Guardformen; alle fünf Workflows
bestanden. Die autonome Fortsetzung erweitert das kumulative Budget ohne Reset
um ein Arbeitspaket, einen PR und einen Testkandidaten auf höchstens
110/159/227. Ein zusätzliches ungeschütztes `main()` auf Modulebene darf keinen
zweiten oder vorzeitigen Testrun auslösen. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #479 integriert den Schutz vor ungeschützten Aufrufen; alle fünf Workflows
bestanden. Der nächste einzelne Kandidat erweitert den kumulativen Rahmen ohne
Reset um ein Paket, einen PR und einen Test auf höchstens 111/160/228. Auch
innerhalb des einzigen `__main__`-Guards darf `main()` genau einmal aufgerufen
werden. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #480 integriert die Prüfung auf genau einen Guard-Aufruf; alle fünf
Workflows bestanden. Der nächste Schnitt erweitert das Budget ohne Reset um
ein Paket, einen PR und bis zu drei Testkandidaten auf höchstens 112/161/231.
Ungeschützte `main()`-Aufrufe in Klassenbasen, Funktionsstandardwerten und
Dekoratoren müssen als Importzeitaufrufe erkannt werden. Keine SQL-/Runtime-
Ausführung oder menschliche Generalprobe.

PR #481 integriert die Prüfung der Importzeit-Auswertungsstellen; alle fünf
Workflows bestanden. Für ungeschützte Aliasreferenzen auf `main` erweitert sich
der kumulative Rahmen ohne Reset um ein Arbeitspaket, einen PR und einen
Testkandidaten auf höchstens 113/162/232. Der Test nutzt die Aliaszuweisung
`runner = main`. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #482 integriert die Aliasprüfung; alle fünf Workflows bestanden. Der nächste
Schnitt erweitert das Budget ohne Reset um ein Arbeitspaket, einen PR und zwei
synthetische Gegenproben auf höchstens 114/163/234. Dynamische Aufrufe über
`globals()["main"]()` und `getattr(globals(), "main")()` werden außerhalb des
Guards zurückgewiesen. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #483 integriert diese beiden Formen; alle fünf Workflows bestanden. Zwei
weitere synthetische Gegenproben für `locals()["main"]()` und `vars()["main"]()`
erweitern den Rahmen ohne Reset um ein Paket, einen PR und zwei Testkandidaten
auf höchstens 115/164/236. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #484 integriert die lokalen Mappingformen; alle fünf Workflows bestanden.
Der nächste Schnitt erweitert den Rahmen ohne Reset um ein Arbeitspaket, einen
PR und zwei Testkandidaten auf höchstens 116/165/238. Direkte Testaufrufe nach
`return` oder `raise` im `main()`-Ablauf gelten als unerreichbar und dürfen die
Vollständigkeitsprüfung nicht bestehen. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #485 integriert die beiden Kontrollflussenden; alle fünf Workflows
bestanden. Für vier direkte Prozessendeaufrufe erweitert sich der Rahmen ohne
Reset um ein Paket, einen PR und vier synthetische Testkandidaten auf höchstens
117/166/242. `exit()`, `quit()`, `sys.exit()` und `os._exit()` dürfen danach
liegende Testaufrufe nicht als ausgeführt zählen lassen. Keine SQL-/Runtime-
Ausführung oder menschliche Generalprobe.

PR #486 integriert die vier direkten Exitformen; alle fünf Workflows bestanden.
Der nächste Schritt erweitert den kumulativen Rahmen ohne Reset um ein Paket,
einen PR und zwei Testkandidaten auf höchstens 118/167/244. Importierte oder
umbenannte `sys.exit`-Aufrufe beenden den Kontrollfluss ebenfalls. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #487 integriert beide `sys.exit`-Aliasfälle; alle fünf Workflows bestanden.
Für drei weitere Aliasfälle erweitert sich das Budget ohne Reset um ein
Arbeitspaket, einen PR und drei Testkandidaten auf höchstens 119/168/247:
`builtins.exit`, `os._exit` und ein `os`-Modulalias. Keine SQL-/Runtime-
Ausführung oder menschliche Generalprobe.

PR #488 integriert alle drei Aliase; alle fünf Workflows bestanden. Der nächste
Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und einen
Testkandidaten auf höchstens 120/169/248. Ein `sys.exit()` als einfache
Zuweisung beendet den Kontrollfluss ebenfalls; folgende Tests gelten als
unerreichbar. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #489 integriert die einfache Zuweisungsform; alle fünf Workflows bestanden.
Der nächste Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und
einen Testkandidaten auf höchstens 121/170/249. Ein Prozessende in einer
erweiterten Zuweisung wie `status += sys.exit()` muss ebenfalls als Ende erkannt
werden. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #490 integriert die erweiterte Zuweisung; alle fünf Workflows bestanden.
Der nächste Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und
einen Testkandidaten auf höchstens 122/171/250. Die annotierte Zuweisung
`result: int = sys.exit()` erhält eine eigene synthetische Gegenprobe. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #491 integriert die annotierte Zuweisung; alle fünf Workflows bestanden.
Der nächste Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und
drei Testkandidaten auf höchstens 123/172/253. Prozessendeaufrufe innerhalb von
Tupel-, Listen- und Dictionary-Literalen müssen als eager ausgewertet erkannt
werden. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #492 integriert die drei eager Literalformen; alle fünf Workflows bestanden.
Der nächste Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und
einen Testkandidaten auf höchstens 124/173/254. Eine bedingte Exit-Auswertung
innerhalb eines Zuweisungswerts darf einen nachfolgenden Test nicht als
unbedingt erreichbar ausweisen. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #493 integriert den bedingten Zuweisungsfall; alle fünf Workflows bestanden.
Der nächste Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und
einen Testkandidaten auf höchstens 125/174/255. Ein Prozessende in einer
`if`-Verzweigung darf einen späteren Test nicht als auf allen Pfaden
ausführbaren Aufruf bestehen lassen. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #494 integriert den `if`-Abbruchpfad; alle fünf Workflows bestanden. Für
Schleifen, `try`/`except`, `match` und `with` erweitert sich der Rahmen ohne
Reset um ein Arbeitspaket, einen PR und fünf Testkandidaten auf höchstens
126/175/260. Mögliche Prozessenden innerhalb dieser Kontrollflussblöcke dürfen
spätere Tests nicht als unbedingt ausführbar bestehen lassen. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #495 integriert die fünf Pfadfälle; alle fünf Workflows bestanden. Der
nächste Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und
einen Testkandidaten auf höchstens 127/176/261. Nicht aufgerufene verschachtelte
Funktionskörper werden bei der Prozessende-Pfadanalyse ignoriert; ihre
Dekoratoren, Defaults und Annotationen bleiben als beim Definieren ausgewertete
Ausdrücke berücksichtigt. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #496 integriert das Überspringen unaufgerufener Funktionskörper; alle fünf
Workflows bestanden. Für Prozessenden in ausgeführten Helper-Dekoratoren oder
Defaults erweitert sich der Rahmen ohne Reset um ein Paket, einen PR und zwei
Testkandidaten auf höchstens 128/177/263. Diese Ausdrücke laufen bereits bei
der Definition des Helpers. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #497 integriert die ausgeführten Helper-Header; alle fünf Workflows
bestanden. Für Klassenkörper und unaufgerufene Methoden erweitert sich der
Rahmen ohne Reset um ein Paket, einen PR und zwei Testkandidaten auf höchstens
130/179/265. Die Gegenproben trennen den ausgeführten Klassenkörper vom erst
bei Aufruf ausgeführten Methodenrumpf. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #498 integriert diese Auswertungsgrenze; alle fünf Workflows bestanden. Für
Generatorausdrücke erweitert sich der Rahmen ohne Reset um ein Arbeitspaket,
einen PR und zwei Testkandidaten auf höchstens 132/181/267. Der Generatorrumpf
ist aufgeschoben, das äußerste Iterable läuft beim Erzeugen. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #499 integriert die lazy Auswertungsgrenze; alle fünf Workflows bestanden.
Für Generatoren unter direktem Eager-Verbrauch erweitert sich der Rahmen ohne
Reset um ein Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens
134/183/270. `list`, `tuple`, `set`, `sorted`, `sum`, `min`, `max`, `any` und
`all` führen den Generatorrumpf aus. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #500 integriert den Generatorverbrauch durch diese eingebauten Funktionen;
alle fünf Workflows bestanden. Für ausgeführte `map`-/`filter`-Callbacks
erweitert sich der Rahmen ohne Reset um ein Arbeitspaket, einen PR und zwei
Testkandidaten auf höchstens 136/185/273. Die Gegenproben unterscheiden einen
Callback bei Eager-Verbrauch von einem lazy `map` ohne Iteration. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #501 integriert die ausgeführten Lambda-Callbacks; alle fünf Workflows
bestanden. Für benannte synchrone `map`-/`filter`-Callbacks erweitert sich der
Rahmen ohne Reset um ein Arbeitspaket, einen PR und zwei Testkandidaten auf
höchstens 138/187/276. Eine benannte synchrone Funktion wird nur beim Eager-
Verbrauch ihres Iterators aufgerufen. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #502 integriert benannte synchrone Callbacks; alle fünf Workflows bestanden.
Für Generatoren direkt in `for`-/`async for`-Iteratoren erweitert sich der
Rahmen ohne Reset um ein Arbeitspaket, einen PR und zwei Testkandidaten auf
höchstens 140/189/279. Die Schleife konsumiert den Generator. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #503 integriert die Loop-Konsumierung; alle fünf Workflows bestanden. Für
Generatorfunktionen als `main` erweitert sich der Rahmen ohne Reset um ein
Arbeitspaket, einen PR und drei Testkandidaten auf höchstens 143/192/283.
`yield` im ausgeführten `main`-Pfad oder Helper-Header macht `main()` lazy;
ein verschachtelter Helper-Rumpf ändert das nicht. Keine SQL-/Runtimeausführung
oder menschliche Generalprobe.

PR #504 integriert die Prüfung von Generatorfunktionen als `main`; alle fünf
Workflows bestanden. Für die `yield from`-Gegenprobe erweitert sich der Rahmen
ohne Reset um ein Arbeitspaket, einen PR und einen Testkandidaten auf höchstens
144/193/285. `yield from` macht `main` lazy. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #505 integriert die `yield from`-Gegenprobe; alle fünf Workflows bestanden.
Für Modulstart-Prozessenden erweitert sich der Rahmen ohne Reset um ein
Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens 146/195/288. Die
Gegenproben trennen direkte Importzeit-Ausführung von einem unaufgerufenen
Helper-Rumpf. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #506 integriert Prozessenden beim Modulstart; alle fünf Workflows bestanden.
Für lokale Exit-Alias-Imports in `main()` erweitert sich der Rahmen ohne Reset
um ein Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens 148/197/291.
`from sys import exit as stop` und `import sys as runtime` werden erkannt.
Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #507 integriert direkte lokale Exit-Imports; alle fünf Workflows bestanden.
Für bedingte Imports in `main()` erweitert sich der Rahmen ohne Reset um ein
Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens 150/199/294.
Mögliche Exit-Imports in Kontrollflusszweigen werden erkannt; unaufgerufene
Helper-Rümpfe bleiben ausgenommen. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #508 integriert bedingte lokale Exit-Imports; alle fünf Workflows bestanden.
Für relative `.sys`-Imports erweitert sich der Rahmen ohne Reset um ein
Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens 152/201/297. Nur
absolute Imports werden als Standardmodul `sys` erkannt. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #509 integriert die Abgrenzung relativer Imports; alle fünf Workflows
bestanden. Für lokale Überschreibungen von Exit-Aliasen erweitert sich der
Rahmen ohne Reset um ein Arbeitspaket, einen PR und zwei Testkandidaten auf
höchstens 154/203/300. Zuweisungen und lokale Definitionen ersetzen die
vorherige Aliasbindung. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

### DGN-007 getrenntes Qualifikationsband

Der am 4. November integrierte Import-only-Worker ist begrenzte lokale
Komponentenevidenz. Ein nächster DGN-007-Schritt darf nur aus dem aktiven
kanonischen Status gewählt und auf einen einzelnen, statisch prüfbaren
Quell-/Vertragsschnitt begrenzt werden. Loader-/Parentregistrierung,
SESSION_END, tatsächlicher Kanal, operative Inventur, UsedBytes, Trust,
Consumption, Replay, unabhängiger Worker-Cleanup, SQL und Methodenfreigabe
bleiben getrennte Gates. Jeder PASS einer Komponente ist ausschließlich für
deren festgelegten Scope gültig; keine Komponente aktiviert automatisch den
nächsten Lauf.

### Gemeinsame Autonomie- und Stopregeln

- Ein Owner, höchstens zwei zusammenhängende Arbeitspakete je Fortsetzung und
  Checkpoint spätestens am dritten Quellenkandidaten oder beim ersten Blocker.
- Die bisherigen kumulativen Obergrenzen von 15 Arbeitspaketen, 23 Pull
  Requests und 57 Quellenkandidaten bleiben als Verbrauchsbasis erhalten.
  Der Nutzer autorisierte am 2026-11-06 zwei begrenzte Fortsetzungserweiterungen
  für die autonome Entwicklung, jeweils um ein Arbeitspaket, einen Pull Request
  und zwei Quellen-/Testkandidaten. Die kumulative Obergrenze beträgt nun
  17/25/61; kein Reset. Diese aktuelle Erweiterung gilt für den RES-001-Schnitt
  und wird am PR-/Integrationscheckpoint gegen den Stand geprüft.
  Mit der Fortsetzungsanweisung vom 2026-11-07 gilt für den nächsten
  eigenständigen RES-003-Offlineschnitt eine begrenzte Erweiterung um ein
  Arbeitspaket, einen Pull Request und zwei Quellen-/Testkandidaten. Die
  kumulative Obergrenze beträgt 18/26/63; kein Reset. Sie gilt ausschließlich
  für diesen Offlinevertrag und wird am Integrationscheckpoint abgeglichen.
  Die Fortsetzungsanweisung vom 2026-11-07 autorisiert am nächsten Checkpoint
  einen zusätzlichen, eigenständigen Dokumentationsschnitt mit weiteren
  1/1/2 Einheiten; die kumulative Obergrenze beträgt nun 19/27/65. Diese
  Erweiterung gilt für die quellengebundene RES-003-Lehrergänzung.
  Für die anschließende Detailprüfung des SQL-Server-2025-`OPTIMIZED_SP_EXECUTESQL`
  gilt nach der Fortsetzungsanweisung vom 2026-11-07 eine weitere klar begrenzte
  Erweiterung um ein Arbeitspaket, einen PR und zwei Quellenkandidaten; kumulativ
  höchstens 20/28/67, kein Reset. Sie deckt nur Quellenprüfung und dokumentarische
  Entscheidung ab, keine Featureaktivierung oder Runtime.
  Die nächste autonome Fortsetzung erweitert den begrenzten Rahmen um genau ein
  Arbeitspaket, einen Pull Request und zwei Quellenkandidaten; kumulativ höchstens
  21/29/69, ohne Reset. Diese Erweiterung gilt für die Offline-Quellen- und
  Abdeckungsprüfung zu Graph Tables. Sie autorisiert weder SQL-/Lab-Ausführung
  noch Demo-Implementierung oder Performanceaussage.
  Für die anschließende getrennte Graph-Table-Versions- und Indexprüfung galt
  eine begrenzte Erweiterung um 1 Arbeitspaket, 1 Pull Request und
  2 Quellenkandidaten; kumulativ höchstens 22/30/71, kein Reset. Sie erfasste
  zwei weitere Microsoft-Primärquellen und eine Offline-Dokumentation, ohne
  SQL-/Runtimefreigabe. Der Schnitt ist über PR #365 vollständig integriert.
  Die Curriculum-Zuordnung erweiterte den Rahmen um ein Arbeitspaket,
  einen Pull Request und bis zu zwei Quellenkandidaten auf kumulativ 23/31/73.
  Sie verwendete bestehende Projektquellen und begründete keine neue Lernziel-ID.
  Der Schnitt ist über PR #366 vollständig integriert.
  Für die Quellenprüfung der 2022/2025-Releaseübersichten gilt die nächste
  begrenzte Erweiterung um 1 Arbeitspaket, 1 Pull Request und 2 Quellenkandidaten;
  kumulativ höchstens 24/32/75. Sie bewertet nur die beiden Versionsübersichten
  und erteilte keine Kompatibilitäts- oder Laufzeitfreigabe. Der Schnitt ist
  über PR #367 integriert.
  Der statische Graph-Demoentwurf erweitert den Rahmen um ein Arbeitspaket,
  einen Pull Request und bis zu zwei Quellenkandidaten auf kumulativ 25/33/77.
  Er erstellt keine Demo-ID und erteilt keine SQL-/Runtimefreigabe.
  Der Syntaxreview für `MATCH` und Edge-INSERT erweitert den endlichen Rahmen
  um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten; kumulativ höchstens 26/34/79.
  Er bleibt auf Primärquellen und statische Dokumentation begrenzt.
  Die Fortsetzung nach der Syntaxprüfung erweitert den endlichen Rahmen um 1 Arbeitspaket, 1 PR und 2 Quellen-/Vertragskandidaten auf höchstens 27/35/81. Sie gilt für die Registrierung von `QRY-023` und den vollständigen statischen Vertrag; keine SQL-/Lab-Ausführung.
  Das Framework-/Curriculumreview setzt die autonome Fortsetzung um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten auf höchstens 28/36/83 fort. Es bindet die Projektprofile 2019/150, 2022/160, 2025/170 als Designziele und macht Plan-/Baseline-/Vergleichsmessung verpflichtend; keine Laufzeitfreigabe.
  Der Entwurf des deterministischen QRY-023-Messworkloads und die formale CLM-047-Traceabilityzuordnung erweitern die Obergrenze um 1 Arbeitspaket, 1 PR und 2 Kandidaten auf höchstens 29/37/85. Die Designprofile und Messmethodik sind weiterhin keine Graph-Runtimefreigabe.
  Das Quellen-/Methodenreview zu MATCH, Kandidatenindizes und getrennter Planevidenz erweitert die Obergrenze um 1 Arbeitspaket, 1 PR und 2 Kandidaten auf höchstens 30/38/87. Die unabhängige Methodenfreigabe bleibt ausdrücklich offen.
  Der initiale QRY-023-Harness-Codeentwurf erweitert die Obergrenze um 1 Arbeitspaket und 1 PR auf höchstens 31/39/89. Er bleibt nicht katalogisiert und ungefahren; statische Abnahme, unabhängige Methodenfreigabe und konkrete Runtimefreigabe sind getrennte weitere Gates.
  PR #374 integriert den QRY-023-Codeentwurf nach erfolgreichen Projektworkflows. Der statische allgemeine Cleanup-Eigentumstest lief in disposable SQL-Server-Containern für 2019, 2022 und 2025; QRY-023 selbst wurde nicht ausgeführt. Die nächste Welle ergänzt einen gezielten Offlinevertrag mit Regressionstests und eigenem nur statischen CI-Workflow. Die kumulative Obergrenze steigt um 1 Arbeitspaket, 1 PR und 2 Evidenzkandidaten auf 32/40/91. Diese Strukturprüfung schließt weder T-SQL-Kompilierbarkeit noch unabhängige Methodenfreigabe.
  PR #375 integriert den Offlinevalidator und seine Regressionstests; sämtliche PR-Gates waren grün. Die Editions-/Servicingprüfung für QRY-023 ergibt graphfähige Projekteditionen und bindet die zum 7.11.2026 neuesten dokumentierten Servicingbuilds als zeitgebundene Designpins ein. Preflight und Setup prüfen sie vor Mutation. Diese Fortsetzung erweitert den Rahmen um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten auf höchstens 33/41/93. Image-Digests, unabhängige Methodenfreigabe und Ausführung bleiben offen.
  PR #376 integriert das Editions-/Buildreview und die vor Setup erzwungenen ProductVersion-Pins. Der nächste Offline-Schnitt ergänzt ScriptDom `170.191.0` mit Lockfile und grammatikgebundenem Parse der ausführbaren QRY-023-Dateien für SQL Server 2019/2022/2025. Er schließt keine Engine-Kompilierung und keinen Runtimegate. Obergrenze: 34 Arbeitspakete, 42 PRs und 95 Quellenkandidaten.
  Der read-only MCR-Abgleich bindet die tatsächlichen Buildlabels und Manifestdigests der vorgesehenen Linux/AMD64-Images. Er ersetzt zwei Produktservicingpins in Preflight/Setup durch die dazu passenden CU-Imagebuilds und dokumentiert, dass diese 2019/2022 nicht die separat veröffentlichten GDR-Builds enthalten. Für den statischen Abgleich gilt eine begrenzte Erweiterung um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten; kumulativ höchstens 35/43/97. Kein Image wurde heruntergeladen oder gestartet.
  Der maschinenlesbare `container-images.proposed.json`-Lock und seine synthetischen Positiv-/Negativprüfungen erweitern den begrenzten Rahmen um weitere 1/1/2 Einheiten auf 36/44/99. Er bindet Profile, Labels und Digest-Referenzen statisch, ist noch nicht in einen Runtimeaufruf integriert und erteilt keine Laufberechtigung.
  Das vorgeschlagene Ressourcenprofil ergänzt Hersteller-Minimum, Hostreserve, harte Containergrenzen, SQL-Speicherlimit und bestehendes Zeit-/Cleanupbudget. Die zwei Microsoft-Quellen sowie die MCR-Layergrößen sind gebunden; die zusätzlichen 8/20-GiB-Host- und 4/3-GiB-Containerwerte bleiben ungemessene Projektannahmen. Begrenzte Erweiterung +1/1/2 auf kumulativ 37/45/101; kein Runtime- oder Ressourcenlauf.
  Der MCR-Tagabgleich findet GDR-spezifische Tags für 2019 und 2022, deren Image-Labels zu den neuesten Linux-CU+GDR-Builds passen. Lock und Preflight/Setup werden auf diese Tags und ihre neuen AMD64-Manifestdigests umgestellt; dies ist Registrymetadaten-, keine Engineevidenz. Begrenzte Erweiterung +1/1/2 auf kumulativ 38/46/103.
  PR #382 bindet QRY-023-Aufrufe, FWK-004-Prozedursignaturen und Messergebnis-Spalten mit zwei gezielten Offline-Regressionen an den bestehenden Framework-Contracts-Workflow. Alle zehn PR- und sieben relevanten Main-Workflows waren erfolgreich; kein QRY-023-SQL-Lauf. Begrenzte Erweiterung +1/1/2 auf 39/47/105.
  PR #383 integriert QRY-002-Lehrnotiz und Quellenregister nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Die Lehre trennt beide Konvertierungsrichtungen von konkreter Plan-/Zugriffswirkung. Begrenzte Erweiterung +1/1/2 auf 40/48/107.
  Der folgende QRY-003-Schnitt präzisiert `datetime`- und `datetime2(7)`-Tagesgrenzen, `BETWEEN`-Inklusivität, typed `DATEADD` und die empirische SARGability-Grenze; `SRC-133` wird ergänzt. Kein SQL-Lauf. Begrenzte Erweiterung +1/1/2 auf 41/49/109.
  PR #384 ist integriert; fünf PR-Gates und drei Main-Workflows waren erfolgreich. Der folgende RES-004-Quellenabgleich bindet Lehrnotiz, `SRC-010`, `SRC-110` und die neue `SRC-134` ohne DMV-Lauf zusammen. Begrenzte Erweiterung +1/1/2 auf 42/50/111.
  PR #385 integriert die RES-004-Quellenregisterpflege nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Der vollständige Lesepfad zeigt konsistente Lernziel-/Navigationsbezüge; der nächste Offlineentwurf konkretisiert QRY-003-Grenztupel und Ergebnisoracles. Begrenzte Erweiterung +1/1/2 auf 43/51/113.
  PR #386 integriert den QRY-003-Intervallentwurf nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Der nächste priorisierte Offlinekandidat ist QRY-007: Join-Kardinalität, `DISTINCT` und `EXISTS`, gebunden an `SRC-135`. Begrenzte Erweiterung +1/1/2 auf höchstens 44/52/115.
  PR #387 integriert QRY-007-Quellenbundle und Join-Kardinalitätsentwurf nach fünf erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. PR #388 ergänzt die quellengebundene Lehrnotiz mit Fixture, Ergebnis-/Multiplizitätsoracle und Curriculum-Navigation; vier PR-Gates und zwei Main-Workflows waren erfolgreich. Begrenzte Erweiterung +1/1/2 auf 45/53/117.
  Für den nächsten priorisierten IDX-003-Schnitt gilt eine begrenzte Erweiterung +1 Arbeitspaket, +1 PR und +2 Quellen-/Testkandidaten auf höchstens 46/54/119. Sie gilt für Key-Reihenfolge, INCLUDE, vier Ergebnisoracles und eine Seitengrößengegenprobe; keine Plan- oder Performancefreigabe.
  PR #389 integriert den IDX-003-Entwurf nach fünf erfolgreichen PR-Gates und drei betroffenen Main-Workflows. Der nächste priorisierte Schnitt ist die `IDX-004`-Lookup-Kurve mit abgestufter Trefferzahl, nicht abdeckendem/abdeckendem Index, vollständigem Tupeloracle und ohne allgemeine Prozentgrenze. Begrenzte Erweiterung +1/1/2 auf höchstens 47/55/121.
  PR #390 integriert das IDX-004-Quellenbundle und den Selektivitäts-/Oracleentwurf; fünf PR-Gates und drei Main-Workflows waren erfolgreich. Der folgende Schritt bindet die Lookup-Erklärung in den Curriculum-Lesepfad, ohne einen Kippunkt oder Performancevorteil zu behaupten. Begrenzte Erweiterung +1/1/2 auf höchstens 48/56/123.
  Der Nutzer hat die autonome Fortsetzung ausdrücklich angeordnet und darauf hingewiesen, dass begrenzte Budgets bei kontinuierlicher Entwicklung fortgeschrieben werden müssen. Für den folgenden klar isolierten IDX-001-Offlineentwurf gilt deshalb eine neue, begrenzte Erweiterung um 1 Arbeitspaket, 1 Pull Request und höchstens 2 Quellenkandidaten auf kumulativ 49/57/125. Sie autorisiert keine SQL-/Runtimeausführung oder menschliche Generalprobe.
  PR #392 integriert den IDX-001-Entwurf nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Die fortlaufende autonome Entwicklung erhält für IDX-002 eine weitere begrenzte Erweiterung um 1 Arbeitspaket, 1 PR und höchstens 2 Quellenkandidaten auf kumulativ 50/58/127. Diese gilt ausschließlich für den statischen Quellen-/Designschnitt zur Clustered-Key-Breite und erteilt keine SQL-/Runtimefreigabe.
  PR #393 integriert IDX-002 mit fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Der folgende begrenzte Offlineentwurf STL-001 erweitert den fortlaufenden Auftrag um 1 Arbeitspaket, 1 PR und höchstens 2 Quellenkandidaten auf kumulativ 51/59/129. Es gibt keine SQL-/Runtimefreigabe oder Generalprobe.
  PR #394 integrierte STL-001 mit fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Für STL-002 galt eine weitere begrenzte Erweiterung um 1 Arbeitspaket, 1 PR und höchstens 2 Quellenkandidaten auf kumulativ 52/60/131; PR #395 ist mit fünf erfolgreichen PR-Gates und drei Main-Workflows integriert.
  PR #395 schloss den STL-002-Schnitt ab. Für QRY-005 galt eine Fortsetzungserweiterung um 1/1/2 auf kumulativ 53/61/133; PR #396 ist mit fünf erfolgreichen PR-Gates und drei Main-Workflows integriert. Der nächste OPT-004-Teilschnitt erweitert den Rahmen um 1/1/2 auf kumulativ 54/62/135. Er gilt ausschließlich für die Korrelations-/Mehrspaltenstatistikfrage und keine SQL-/Runtimeausführung.
  PR #396 schloss den QRY-005-Offlineentwurf ab. Für den begrenzten OPT-004-Korrelationsschnitt galt eine Fortsetzungserweiterung um 1 Arbeitspaket, 1 PR und höchstens 2 Quellenkandidaten auf kumulativ 54/62/135; PR #397 ist mit fünf erfolgreichen PR-Gates und drei Main-Workflows integriert.
  PR #397 schloss den OPT-004-Korrelations-/Mehrspaltenstatistikentwurf ab. Der noch offene Constraint-Vertrauens- und Eindeutigkeitsschnitt erweitert den fortlaufenden Rahmen um 1/1/2 auf kumulativ 55/63/137. Runtime, Cleanupqualifikation und menschliche Generalprobe bleiben ausgeschlossen.
  PR #398 integriert den getrennten OPT-004-Constraint-/Eindeutigkeitsschnitt nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Die Fortsetzung zu STL-003 erweitert den fortlaufenden Rahmen um 1/1/2 auf kumulativ 56/64/139. Sie umfasst ausschließlich Quellen- und Offlineentwurf zum Forwarded-Record-Lifecycle; keine SQL-/Runtimeausführung oder menschliche Generalprobe.
  PR #399 integriert STL-003 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. QRY-011 erhält eine weitere begrenzte Erweiterung um 1/1/2 auf kumulativ 57/65/141; Scope sind Quellenprüfung, synthetische vollständige Ergebnisoracles und ein statischer Entwurf zu Filtered Indexes, berechneter Spalte und einer SET-Option-Gegenprobe. Keine SQL-/Runtimeausführung, Planfreigabe oder menschliche Generalprobe.
  PR #400 integriert QRY-011 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. IDX-005 erhält eine weitere begrenzte Erweiterung um 1/1/2 auf kumulativ 58/66/143; Scope sind aktuelle Primärquellen und ein statischer Entwurf zur Prüfung zweier überlappender Missing-Index-Vorschläge, Indexkonsolidierung und DML-Trade-offs. Keine SQL-/Runtimeausführung, Indeximplementierung oder menschliche Generalprobe.
  PR #401 integriert IDX-005 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. OPT-012 erhält eine weitere begrenzte Erweiterung um 1/1/2 auf kumulativ 59/67/145; Scope ist ein quellengebundener Offlineentwurf zu Eligibility, Wiederverwendung desselben Plans, kleinem/großem Build-Input und Actual-Plan-Nachweisen. Keine SQL-/Runtimeausführung, adaptive Planformgarantie, Leistungsbehauptung oder menschliche Generalprobe.
  PR #402 integriert OPT-012 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. STL-010 erhält eine weitere begrenzte Erweiterung um 1/1/2 auf kumulativ 60/68/147; Scope sind aktuelle Primärquellen und ein statischer Entwurf zum Abgleich synthetischer Kompressionsprofile, Schätzungen in `tempdb` und tatsächlicher Seitenbelegung. Keine SQL-/Runtimeausführung, pauschale Editionsannahme, Leistungsrangfolge oder menschliche Generalprobe.
  PR #403 integriert STL-010 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Der nächste begrenzte QRY-003-Schnitt erweitert die kumulative Obergrenze um 1/1/2 auf 61/69/149; er prüft vorhandene Datumsquellen und vervollständigt bei Bedarf den statischen Entwurf samt Ergebnistupeln für `datetime` und `datetime2(7)`. Keine SQL-/Runtimeausführung, Plan-/Leistungsbehauptung oder menschliche Generalprobe.
  PR #405 integriert QRY-003 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. QRY-007 erweitert den fortlaufenden Rahmen um 1/1/2 auf kumulativ 62/70/151; Umfang sind Quellenprüfung und vollständige statische Tupeloracles für One-to-many-Join, `DISTINCT`, `EXISTS` und angeforderte Kindaggregation. Keine SQL-/Runtimeausführung, pauschale `DISTINCT`-Empfehlung, Plan-/Leistungsbehauptung oder menschliche Generalprobe.
  PR #406 integriert QRY-007 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. IDX-003 erhält eine begrenzte Fortsetzungserweiterung um 1/1/2 auf kumulativ 63/71/153; Scope sind Quellenabgleich, Prüfung der statischen Fixturezählwerte und vollständige Tupeloracles für Key-Reihenfolge-/INCLUDE-Profile. Keine SQL-/Runtimeausführung, Seek-Garantie, Leistungsbehauptung oder menschliche Generalprobe.
  PR #408 integriert IDX-003 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. IDX-004 erhält eine begrenzte Erweiterung um 1/1/2 auf kumulativ 64/72/155; Scope sind Quellenprüfung, deterministische Fixtureformeln und vollständige Tupeloracles für die Lookup-Treffermengen auf BASE-, LOOKUP- und COVERING-Profilen. Kein SQL-/Runtimelauf, garantierter Lookup-/Scan-Übergang, Leistungsclaim oder menschliche Generalprobe.
  PR #410 integriert IDX-004 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Die vollständige Fixtureformel, Bandintervalle und sortierten Tupeloracles sind gebunden; Plan-/Lookup-/Read-Befunde bleiben empirisch. IDX-001 erhält für die autonome Fortsetzung eine begrenzte Erweiterung um 1 Arbeitspaket, 2 PRs (Statusübergang und Entwurfsintegration) und bis zu 2 Quellenkandidaten auf kumulativ 65/74/157. Scope: aktuelle Quellenprüfung und vollständige Punkt-/Bereichsoracles für HEAP und CLUSTERED. Kein SQL-/Runtimelauf, keine Planformgarantie, Leistungsbehauptung oder menschliche Generalprobe.
  PR #412 integriert IDX-001 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Die vollständigen Punkt-/Bereichsoracles sind für beide Row-Locator-Profile gebunden; Enginequalifikation und Planwahl bleiben offen. IDX-002 erhält für die autonome Fortsetzung eine begrenzte Erweiterung um 1 Arbeitspaket, 2 PRs (Statusübergang und Entwurfsintegration) und bis zu 2 Quellenkandidaten auf kumulativ 66/76/159. Scope: aktuelle Quellenprüfung, exakte Fixtureformeln und vollständige Ergebnistupeloracles für `NARROW_UNIQUE` und `WIDE_NONUNIQUE`. Keine SQL-/Runtimeausführung, Größen-/Leistungsbehauptung oder menschliche Generalprobe.
  PR #414 integriert IDX-002 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Die vollständigen Fixtureformeln und Band-37-Tupeloracles sind gebunden; Größenmodell und gemessene Seiten bleiben getrennt. STL-001 erhält für die autonome Fortsetzung eine begrenzte Erweiterung um 1 Arbeitspaket, 2 PRs (Statusübergang und Entwurfsintegration) und bis zu 2 Quellenkandidaten auf kumulativ 67/78/161. Scope: aktuelle Quellenprüfung, vollständige Tupeloracles der vier kumulativen Heapprofile und Nachrechnung des Größenmodells. Keine SQL-/Runtimeausführung, Page-Density- oder Leistungsbehauptung oder menschliche Generalprobe.
  PR #416 integriert STL-001 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Vollständige Ergebnistupeloracles, Verteilungen und Modellrechnungen sind gebunden; Heapseiten bleiben empirisch. STL-002 erhält eine begrenzte Erweiterung um 1 Arbeitspaket, 2 PRs (Statusübergang und Entwurfsintegration) und bis zu 2 Quellenkandidaten auf kumulativ 68/80/163. Scope: Quellenabgleich sowie exaktes Payload-/Padding-Oracle und kanonischer Tupelvergleich für INROW, ROW_OVERFLOW und LOB. Keine SQL-/Runtimeausführung, keine Allocation-Unit- oder Leistungsbehauptung und keine menschliche Generalprobe.
  Vor dem nächsten Start muss der Verbrauch anhand des aktuellen Status und
  der Integrationshistorie verifiziert werden; der zuletzt dokumentierte
  Startverbrauch 1/19/45 ist kein Nachweis des heutigen Restbudgets.
- Token- und Geldverbrauch bleiben unbekannt. Die endlichen Kandidaten-/PR-
  Obergrenzen begrenzen die Arbeit, sind aber keine behauptete Kostenmessung
  oder Provider-Ausgabensperre.
- Aufwand für den RES-003-Offlineschnitt: ein Prüfer und eine gezielte
  Testdatei wurden lokal einmal ausgeführt und im passenden PR- und
  Main-Workflow erneut geprüft; kein SQL-Lab-Trigger. Für die aktuelle
  Lehrergänzung werden die zwei direkt betroffenen Markdown-Lesepfade und ihre
  Microsoft-Quellen geprüft; keine Code- oder SQL-Ausführung.
  Für die `OPTIMIZED_SP_EXECUTESQL`-Detailprüfung wurden zwei Microsoft-
  Quellenstellen geprüft und die vorhandene `QRY-004`-Abnahme als Curriculum-
  Verbraucher abgeglichen; keine Code-, SQL- oder Runtimeausführung.
  Für den Graph-Table-Schnitt wurden die aktuelle Curriculum-Abdeckung und zwei
  Microsoft-Primärquellen geprüft; ein Planungsdokument und zwei bestehende
  Index-/Statuspfade wurden angepasst. Keine Code-, SQL- oder Runtimeausführung.
  Für die getrennte Graph-Versions-/Indexwelle wurden zwei Microsoft-Quellen,
  Review- und Statusnotiz sowie Backlog-/Planungspfade geprüft; kein Code-,
  SQL- oder Runtimeaufruf.
  Die Curriculum-Zuordnung glich `CURRICULUM_ARCHITECTURE.md`,
  `TRACEABILITY_MATRIX.md`, `SLIDE_STATEMENT_REGISTER.md` und den
  Masterimplementierungsplan ab; keine neuen Produktquellen, Code- oder
  SQL-Ausführung.
  Die 2022/2025-Übersichten werden auf Graph-Einträge geprüft; Abwesenheit in
  der Änderungsübersicht wird nicht als Abwesenheits- oder Paritätsbeweis
  ausgelegt. Keine Code- oder SQL-Ausführung.
  Der Graph-Demoentwurf wird an den zwei vorhandenen Microsoft-Einstiegsquellen
  und am Framework-Demovertrag abgeglichen; keine SQL-/Runtimeausführung und
  kein zusätzlicher Testlauf.
  Fehlende/fehlgeschlagene
  Evidenz wird lokal nur bei neuem Befund weiter untersucht. Ein Owner, keine
  zusätzliche Reviewkette und keine Subagenten; reale Token-/Geldmessung bleibt
  unbekannt.
- Nach jedem kohärenten Schnitt: relevante lokale Prüfungen und erforderliche
  unabhängige Prüfung, PR- und Main-Gates gemäß Projektregeln, Integration,
  Main-Synchronisierung und Branchbereinigung. Begonnene Arbeit nicht als
  abgeschlossen melden, solange diese Integrationsschritte offen sind.
- Bei FAIL, fehlender Evidenz, unbekanntem Zustand, veraltetem Quellenbinder,
  verbrauchter Obergrenze oder nicht erfülltem Gate: keine Folgeausführung.
  Fehler nicht weginterpretieren und unveränderte Kandidaten nicht wiederholen.
  Den Blocker mit Wiederaufnahmebedingung im kanonischen Ausführungsstand
  vermerken.

Die Umsetzung dieser Planung selbst ist keine Aufforderung, nach Abschluss
dieses Planungsdokuments autonom mit Arbeitspaket 1 fortzufahren. Eine spätere
Fortsetzung muss am dann aktuellen Status und der dort wirksamen Autorisierung
ansetzen.

## Historischer Planungsstand vom 20. Oktober 2026

Der damalige Benutzerauftrag nahm nach Bestandsprüfung die
allgemeine Entwicklung wieder auf. Der interne Capture-Vorschnitt war nach
[unabhängigem Review und aktueller CI](DGN_007_INTERNAL_CAPTURE_RECEIPT_REVIEW.md)
über PR255 integriert und vollständig bereinigt. Danach ist ausschließlich der
[SESSION_END-Entwurf §34](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#34-session_end-counts-und-kanalhashpräbild)
aufgenommen: maximal zwei Entwurfsstände, Checkpoint nach dem ersten,
ein unabhängiger Designreview und aktuelle Dokumentationsgates. Frühere
ausgeschöpfte Quell-/Import-/Generatorwellen erhalten keine neuen Versuche.
Der Erststand `a6ca3f5…` ist unabhängig ohne Befunde geprüft, alle acht
Dokumentationsgates sind grün. PR256 führt den endgültigen Head-/Base- und
Main-Abschluss; der nächste Implementierungskandidat wäre erst danach ein
separat gewählter reiner Footer-/Trace-Matcher mit eigenen Quellen- und Testgates.
Die folgenden älteren Pausen-/G13-Planungsstände sind insoweit historisch.
Keine Automationaktivierung und keine operative Kanal-/Loader-/Worker- oder
SQLimplementierung in dieser Designwelle.

| Merkmal | Wert |
|---|---|
| Historischer Status zum damaligen Planungsstand | allgemeine Entwicklung `PAUSED`; PR68-Code `BLOCKED` durch damalige Runtimefehler; Prüfbericht und Abschlussprozess getrennt |
| Historischer Bezugsstand | 2026-10-08 |
| Ausgangsstand | Produktive Runtimeevidenz bis Pull Request 42; begrenzte DGN-007-Kontrollcaptures bis Pull Request 62 und prospektiver Prüfvertrag aus Pull Request 63 und skalarer Transport aus Pull Request 64 sowie begrenzter SQL-Producer aus Pull Request 65; Detailstand in `CURRENT_EXECUTION_STATUS.md` |
| Bezug | [Aktueller Ausführungsstand](CURRENT_EXECUTION_STATUS.md), `.ai/BACKLOG.md`, `MASTER_IMPLEMENTATION_PLAN.md` |
| Zweck | priorisierte, kleine Folgepakete; keine Aussage, dass die beschriebenen Inhalte bereits umgesetzt sind |

## 1. Planungsgrundlagen

Der gezielte Benutzerauftrag vom 2026-10-09 betrifft Prüfung und Abschluss von
PR 68 sowie DEC-069; der [G13-/PR-Review](DGN_007_G13_PR_REVIEW.md) führt diesen
isolierten Diagnoseschnitt. Er verlangt erfolgreiche relevante aktuelle CI (Continuous Integration; automatisierte Integrationsprüfungen),
ohne G13 oder die offene Methodenentscheidung zu ändern. Die nachfolgende
allgemeine Folgeplanung und die interne Capture-Rückgabe bleiben ausdrücklich
zurückgestellt.
Der aktuelle Reporter-Head `f9ec582…` scheiterte auf 2022 an SQL20 und auf
2025 an G13. Deshalb wird nur der geprüfte Befund und Abschlussprozess getrennt
integriert; der Code-PR ist vorübergehend geschlossen und sein Branch wegen
nicht übernommener Änderungen erhalten. Zusätzlicher Scopeentscheid angefragt;
kein Bypass und kein Wiederholen unveränderter Kandidaten bis grün.

Die Entwicklung wurde am 2026-10-07 nach der über PR 92 dokumentierten Pause
ausdrücklich mit den bisherigen Regeln wieder aufgenommen. Seit dem Benutzerstopp
vom 2026-10-08 gilt `PAUSED`: nur den bereits laufenden §33-DESIGN-/PR-Schnitt
vollständig integrieren und seinen eigenen Branch unabhängig bereinigen; danach
Orchestrator und Subagents beenden. Alle hier genannten Folgepakete einschließlich
SESSION_END sind bis zu einer neuen ausdrücklichen Wiederaufnahme zurückgestellt.
Der vollständige Einstieg samt offener Reihenfolge und geschützter ungemergter
Arbeit steht in [CURRENT_EXECUTION_STATUS.md §0](CURRENT_EXECUTION_STATUS.md#0-entwicklungspause-und-wiederaufnahme).
Der getrennte [Darstellungs- und Digestentwurf §10](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#10-vollständig-erhaltender-darstellungs--und-digestentwurf)
liegt als `DESIGNED` vor. Die separat vorgewählte vollständige Kontrollfixture
und reine Größenprüfung in [§11](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#11-separat-ausgewählte-vollständige-bootstrapfixture)
belegen 85 Records und gemeinsame Metadata von 17.127/17.113/17.091 Bytes:
Der Tupelkandidat überschreitet das unveränderte 16.384-Byte-Cap bei allen Ordinals.
Der separate [Stringpoolentwurf §12](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#12-verlustfreier-stringpoolentwurf)
liegt als `DESIGNED` vor, mit eigenen lokalen Pools, vollständigen Formfeldern und
unveränderten Caps einschließlich höchstens 256 Poolwerten. Der eigene
[reine Pool-Sizer §13](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#13-separater-reiner-stringpool-sizer)
bestand 37/37 isolierte Gegenproben ohne SKIP und die vollständige neue
3×5-Größenprüfung: maximal 9.389 Bytes einschließlich Header und 204 Poolwerte.
Unabhängige vollständige Nachrechnung und Feldrückgewinnung bestätigt; keine
erneute Aufnahme oder Nonce. Der getrennte experimentelle Codec-/Digestpfad im
[Vertrag §14](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#14-separater-experimenteller-formcodec-und-design-digests)
bestand 41/41 isolierte Gegenproben ohne SKIP, unabhängigen Quell-/Testreview
und die vollständige Originalfixture: alle 3×5 Frames, Feldrückgewinnung,
kanonischer Repack und neun eigene Digestwerte. Gesamtausgabe
28.264/28.257/28.246 Bytes; unabhängig aus unveränderten Eingaben nachgerechnet,
ohne Codec-/Helper-Replay. Der eigene reine
[kombinierte Eingangsprototyp §15](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#15-separater-experimenteller-kombinierter-eingangsrahmen)
bestand 34/34 isolierte Gegenproben ohne SKIP und die vollständige Originalfixture
mit drei Frames zu jeweils 140.226 Bytes: 9.389 Metadata einschließlich Header,
130.837 unveränderte Rawbodybytes. Vollständige tatsächliche Rückgewinnung,
Repack und unabhängige Stdlib-Nachrechnung ohne Replay bestanden.
Die konkrete operative [Bootstrap-/Kanalreihenfolge §16](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#16-konkrete-operative-bootstrap--und-kanalreihenfolge)
liegt als `DESIGNED` vor. Der reine [Kontrollbootstrapquellengenerator §17](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#17-reiner-generator-gehaltener-kontrollbootstrapquellen)
bestand 32/32 ausschließlich synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die getrennte [Sysconfig-Vorinitialisierung §18](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#18-feste-sysconfig-vorinitialisierung-gehaltener-kontrollquellen) bestand 53/53 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die private native Auswahl nach [§19](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#19-private-auswahlgrundlage-vor-einer-vollständigen-operativen-inventur) ist mit genau einem begrenzten Versuch und unabhängigem Prozess-/Record-POST abgeschlossen. Die additive reine [Inline-Metadata-Syntaxquelle §20](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#20-reine-additive-inline-metadata-syntaxquelle) bestand 80/80 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste Fixture-Label-Fehllauf bleibt getrennt dokumentiert. Die additive reine [Inline-Metadata-Semantikquelle §21](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#21-reine-additive-inline-metadata-semantikquelle) bestand nach zwei engen Fixturekorrekturen 108/108 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 106/108-Lauf bleibt getrennt dokumentiert. Vollständige deklarative M/IP/S15/P11/D9-Semantik, unveränderter benannter Originaldigest und Providerkohärenz sind geprüft. Die additive reine [Inline-Profilreporterquelle §22](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#22-reiner-additiver-inline-profilreporter) bestand im einzigen isolierten Lauf 149/149 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige Scalarprojektion, eigener REPORTED-Pool, atomare begrenzte Records und getrennte Original-/Reportdigests sind geprüft; vier frühere Builder bleiben erhalten. Die reine begrenzte [Inline-Header-/Metadata-Aufnahme §23](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme) bestand im einzigen isolierten Lauf 174/174 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Exact-Chunktype-/Größenvorläufe, vollständige deklarative M-Semantik und atomare gehaltene Rückgabe sind geprüft; fünf frühere Builder bleiben erhalten. Die additive reine [K-Domain-/Commandquelle §24](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands) bestand im einzigen isolierten Lauf 209/209 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständiger K8-/D9-Vorlauf, eigene headerfreie E4-K-Domain und atomare kanonische Commands gegen separat gehaltene Callerwerte sind geprüft; sechs bisherige Builder und 174 alte Tests bleiben erhalten. Die additive reine [Inline-Metadata-Callerquelle §25](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich) bestand nach zwei engen Fixturekorrekturen 243/243 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 241/243-Lauf mit zwei Fehlern vor Matcheraufruf bleibt getrennt dokumentiert. Beide vollständigen Formen und Semantiken, zwei eigene Originalinputdigests und vollständiger Abgleich gegen separat gehaltene I7/W6/K8 sind geprüft; sieben bisherige Builder und 209 alte Tests bleiben erhalten. Die additive reine [Inline-Rawbodyaufnahme §26](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies) bestand nach einer engen Fixturelabelkorrektur 272/272 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 271/272-Lauf bleibt getrennt dokumentiert. Vollständige Formen und Größen vor Hashes, beide tatsächlichen D9 und neun Rawhashes vor Callerabgleich sowie atomare Originalbodyrückgabe sind geprüft; acht bisherige Builder und 243 alte Tests bleiben erhalten. Die additive reine [Profilrecord-Reassemblierung §27](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords) bestand im einzigen isolierten synthetischen Lauf 304/304 Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige begrenzte Control-/Envelopeformen, interne Konsistenz, kanonische Controls und tatsächlicher Footerhash vor Callerordinal sowie atomare Originalrecordrückgabe sind geprüft; neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei enge Fixturelabelkorrekturen wurden vor dem ersten Lauf reviewt; kein ausgeführter Fehllauf. Die additive reine [Inline-Profil-Callerquelle §28](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich) bestand im einzigen isolierten synthetischen Lauf 341/341 Gegenproben ohne SKIP unter CPython 3.12.14. Beide vollständigen R4-Formen/Semantiken, Actual-Pool-Repack und vollständiger separater Callerabgleich sind geprüft; die Matchfunktion berechnet keinen SHA. Zehn frühere Builder und 304 alte Methoden bleiben erhalten. Vorreviewkorrekturen und genaue Grenzen stehen in §28. Die additive reine R→BODY_RELEASE-Planquelle aus §29 bestand im einzigen isolierten synthetischen Lauf 378/378 Gegenproben ohne SKIP unter CPython 3.12.14; elf alte Builder und 341 alte Methoden bleiben erhalten. Die additive reine INPUT_COMPLETE-Quelle aus §30 bestand im einzigen isolierten synthetischen Lauf 413/413 Gegenproben ohne SKIP unter CPython 3.12.14; zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige Record-/Footer→R-Calleradapter aus §31 ist rein additiv implementiert und im isolierten synthetischen Lauf mit 460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden bleiben erhalten. Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente) ist im isolierten synthetischen Lauf mit 66/66 PASS ohne SKIP geprüft. Reservierungen, ganze Slot-/Zustandsbindung, sticky Fehler und einmaliger Fakecleanup sind lokal belegt; kein tatsächlicher Kanal-/Loader-/Absenznachweis. Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.
Frische operative Auswahl, inline Empfang und Reporting, Parent-/Worker-Anbindung,
Loader, Consumption, Replay und unabhängig bereinigte eigene Worker bleiben
getrennte Gates; die charakterisierte Fixture ist keine operative Workerbaseline.
Die Wiederaufnahme ändert keine fachliche Freigabe oder offenen Methodengates.

- `QRY-004` (Optionale Filter, Recompile und dynamisches SQL), `DGN-003` (Abfragehistorie mit Query Store), `DGN-005` (Gezielte Ereigniserfassung mit Extended Events), `OPT-017` (Ungleich verteilte parallele Arbeit) und alle neun Demos aus `W-COV-001` besitzen aktuelle Matrixnachweise aus GitHub Actions.
- `WARN_EMPIRICAL_VARIANCE` ist nur dort als Freigabeausgang zulässig, wo der Demo-Vertrag die empirische Abweichung ausdrücklich beschreibt und alle invarianten Ergebnis-, Sicherheits- und Cleanup-Verträge erfüllt sind.
- Die Curriculum-Analyse verlangt kein neues Hauptmodul. Neue Arbeit erweitert deshalb nur bestehende Lernziele und Demo-IDs.
- Jede Welle ist ein eigenständiger, kleiner Pull Request mit klarer Runtime-, Quellen- und Safety-Grenze. Öffentliche Herstellerdokumentation wird erst nach dem Source-Register-Delta-Review zu Lehrinhalt.

Der reine begrenzte Header-/Metadata-Vorschnitt aus gehaltenen Chunks nach
[§23](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme)
ist implementiert und unabhängig geprüft: einziger isolierter Lauf mit
174/174 PASS ohne SKIP; fünf bisherige Builder und 149 alte Tests erhalten.
Die reine [K-Domain-/Commandquelle §24](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands)
ist im einzigen isolierten Lauf mit 209/209 PASS ohne SKIP geprüft;
sechs bisherige Builder und 174 alte Tests bleiben erhalten.
Die reine [Inline-Metadata-Callerquelle §25](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich)
ist nach zwei engen Fixturekorrekturen mit 243/243 PASS ohne SKIP geprüft;
sieben bisherige Builder und 209 alte Tests bleiben erhalten.
Die reine [Inline-Rawbodyaufnahme §26](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies)
ist nach einer Fixturelabelkorrektur mit 272/272 PASS ohne SKIP geprüft;
acht bisherige Builder und 243 alte Tests bleiben erhalten.
Die reine [Profilrecord-Reassemblierung §27](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords)
ist im einzigen isolierten Lauf mit 304/304 PASS ohne SKIP geprüft;
neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei neue
Fixturelabelkorrekturen wurden vor dem ersten Lauf geprüft.
Die reine [Inline-Profil-Callerquelle §28](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich)
ist im einzigen isolierten Lauf mit 341/341 PASS ohne SKIP geprüft;
zehn bisherige Builder und 304 alte Tests bleiben erhalten.
Die additive reine [R→BODY_RELEASE-Planquelle §29](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#29-deklarativer-rbody_release-plan)
ist im einzigen isolierten Lauf mit 378/378 PASS ohne SKIP synthetisch geprüft:
vollständige Actual-/Caller-R4- und unabhängige K8-Bindung vor Command-SHA,
gehaltene äußere Anker und atomare reine Rückgabe; elf alte Builder und
341 alte Methoden bleiben erhalten. Phasenlabels attestieren weder vorherige
Übergänge noch Einmalverbrauch. Der separate
[INPUT_COMPLETE-Recordvertrag §30](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#30-deklarativer-input_complete-rückkanalrecord)
ist als reine additive Quelle implementiert und im einzigen isolierten Lauf mit
413/413 PASS ohne SKIP geprüft: vollständige Caller-/Receivedformen und Semantik,
kanonische Actualbytes, eigene vollständige K-Domainbindung und dominante POSTs.
Zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige
[Record-/Footer→R-Calleradapter §31](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#31-vollständiger-deklarativer-profilrecord-callerabgleich)
ist rein additiv implementiert und im isolierten synthetischen Lauf mit
460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden
bleiben erhalten. PR 118 ist vollständig integriert; geprüfte Basis ist
`f6559e084ebd660a41a503129f1a28c32be8848b`. Die getrennten CI-/Übernahme-/Cleanupbelege
stehen in [CURRENT_EXECUTION_STATUS.md §0](CURRENT_EXECUTION_STATUS.md#0-entwicklungspause-und-wiederaufnahme).
Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente)
ist mit 66/66 isolierten synthetischen Methoden ohne SKIP geprüft.
Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.
Operativer Workerbetrieb und Ressourcen-Cleanup bleiben getrennte Gates.

## 2. Priorisierte Wellen

| Reihenfolge | Welle | Ziel und abgegrenzter Umfang | Akzeptanzkriterium |
|---:|---|---|---|
| 1 | `LABSCN-005/DGN-007` | Capstone erst als eigenen Schnitt planen, nachdem Query-Store-/XE-Pilot und `CON-006` (Zyklische Sperrkonflikte erkennen) praktisch wiederverwendbare Evidenz- und Mehrsession-Verträge liefern. | Incident, Alternativhypothesen, Zeitfenster, Reset, Quellen und Teilnehmerübergabe sind vollständig; keine versteckte Lösung in Teilnehmerartefakten. |
| 2 | nächster `LABSCN-005`-Einzelslice | Nur einen Kandidaten mit eigenem Quellen-, Safety- und Detailreview auswählen; keine pauschale Infrastrukturwelle. | Lernmehrwert, Providerbedarf, Reset, Cleanup und versionsgebundene Aussage sind vor Implementierung eindeutig. |
| 3 | weitere `LABINT-004`-Matrix | Nur für einen neu freigegebenen gelben Szenarioslice aktivieren. | Matrix und Cleanup prüfen ausschließlich die neue freigegebene Aussage. |

## 2.1 Umsetzungsstand der Wellen

| Welle | Status | Evidenzgrenze |
|---|---|---|
| `TSK-002` (Detailreview LABSCN-005/DGN-007: Capstone-Planungsschnitt mit Incident-, Hypothesen-, Zeitfenster-, Reset- und Teilnehmeruebergabevertrag) | `DECIDED_PLANNING` | Detailreview [LABSCN-005 – Detailreview DGN-007 (Planungsschnitt)](LABSCN_005_DGN_007_DETAIL_REVIEW.md) entscheidet den Capstone-Planungsschnitt; daraus folgt kein Implementierungsauftrag und kein Runtimestatus. |
|---|---|---|
| `W-STA-001` | `VALIDATED` | Lauf 33222989681 belegt die vollständige Matrix einschließlich der erwarteten empirischen Warnungen. |
| `W-DGN-001` | `VALIDATED` | Lauf 33222989682 belegt alle zwölf Query-Store-/XE-Pilotläufe mit `PASS/OK`. |
| `W-SCN-001` | `VALIDATED` | Project Adapter `0.1` und vollständiger SQL-Server-2025-Lifecycle sind auf Docker und Podman praktisch validiert. |
| `W-ADV-017` | `VALIDATED` | Lauf 33447840232 belegt Actual DOP (Degree of Parallelism; Parallelitätsgrad einer Ausführung), Exchange, positive Threadarbeit und Cleanup auf allen drei Zielversionen. |
| `W-SQL25-001` | `VALIDATED` | Quellen-, Claim- und Entscheidungsgrundlage ist abgeschlossen; daraus folgt keine neue Featuredemo. |
| `W-PRS-001` | `VALIDATED` | 102 SlideKeys, drei Custom Shows, Build 41/66/102 und vollständige Master-/Profilrender liegen vor. |
| `W-COV-001` | `VALIDATED` | Lauf 33222989644 belegt alle neun Demos; `CON-009` (Kosten in tempdb unterscheiden) endet auch auf SQL Server 2019 zweimal mit `PASS/OK`. |
| `W2-002` | `VALIDATED` | Neun `W2-A`-Altquellen sind nicht ausführbar; vier aktive Ersatzdemos und alle künftigen Neuaufbauten sind an synthetische, neutrale Datenverträge gebunden. |
| `ADV-009` (Folienspezifikation Modul M03, Lernziel LO-M03-07) | `VALIDATED` | Runtimewarnung, Masterdeck, Notes, Hashbindung, vollständiger Render und Privacy-Freigabe sind synchron. |
| `ADV-010` (Folienspezifikation Modul M03, Lernziel LO-M03-08, Parametersensitive Planoptimierung) | `VALIDATED` | Fachliche, didaktische und technische Endabnahme grenzt verbleibende Designs ausdrücklich als Folgearbeit ab. |
| `LABSCN-002` | `VALIDATED` | 22 produktive Demos sind vollständig mit Lifecycle, Provider, Ressourcen, Versionen, Reset und Evidenz inventarisiert. |
| `LABSCN-004` | `VALIDATED` | Der generische Benutzerablauf für Auswahl, Start, Übergabe, Reset und Remove ist dokumentiert und statisch geprüft. |
| `INF-002`/`INF-003` | `VALIDATED` | Docker und Podman melden `RESOURCE_OK`; der kompakte SQL-Server-2025-Lifecycle und Recovery-Pfad sind dokumentiert. |
| `LABINT-003` | `VALIDATED` | Provider-Parität ist für `QRY-001` (Indexfreundliche Suchbedingungen), `CON-004` (Blockierungsketten verfolgen) und `DGN-005` praktisch belegt. |
| `LABSCN-005/DGN-005` | `VALIDATED` | Project Adapter `0.1`; Docker-Run `d5143f2a-…` und Podman-Run `82791985-…` führten die Teilnehmerphasen aus und endeten nach Start und Reset vollständig als `REMOVED`. |
| `LABSCN-005/CON-006` | `VALIDATED` | Project Adapter `0.1`; Docker-Run `76cff6ed-…` und Podman-Run `6d2d0a51-…` belegten Opfer 1205, Survivor, Deadlock-Graph, geordnete Gegenprobe, Reset und `REMOVED`. |
| `LABSCN-005/DGN-007` | `IMPLEMENTED_STATIC_SLICE_B` | Der nicht-promotende statische Teilnehmerfluss bestand am 2026-09-19 auf SQL Server 2025/Linux mit Docker (`ea802c20-…`) und Podman (`fba84720-…`): Adapter-Preflight, Install/Validate, alle sechs Teilnehmerstufen, Cleanup und Lab-Remove (`PASS`/`REMOVED`). Kontrollierte Negativtests auf Docker mit SQL Server 2019 (`5a12e48a-46df-471a-a266-4646ba3a02e2`) und 2022 (`139c68d8-8a22-42fb-ba19-b51059f21f2b`) ergaben kanonisch `ADAPTER_UNSUPPORTED_SQL_VERSION`, im Lab-Core `ADAPTER_UNSUPPORTED_CONTRACT`, keine DGN-Datenbank und `REMOVED`. Das ist keine 2019/2022-Fachunterstützung und keine Promotion, sondern ausschließlich der erwartete 2025-only-Skip-/Cleanup-Nachweis. Weiterhin keine `READY_FOR_USER`-Übergabe, keine Szenariopromotion und kein Nachweis für `scenario.json`, Manifest, Inventar oder vollständige Lifecycle-/Versionsmatrix. |
| `LABINT-004/CON-006` | `VALIDATED` | Die vollständige freigegebene Matrix SQL Server 2025 × Docker/Podman ist praktisch belegt und prüft ausschließlich den neuen gelben Slice. |
| `DGN-007_DATA_MODEL` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-06 bestanden je zwei vollständige Docker-Lifecycles auf 2019/150, 2022/160 und 2025/170; unabhängiger Datenbankabbau und eigene Container entfernt. [Nachweis](DGN_007_DATA_MODEL_RUNTIME_EVIDENCE.md). Der Datenmodell-Scope bleibt begrenzt und unverändert als Default. |
| `DGN-007_QUERY_STORE_WINDOWS` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-06 bestanden je zwei vollständige Docker-Lifecycles auf 2019/150, 2022/160 und 2025/170; zwei disjunkte Katalogintervalle, gleiche Parameterlast, je vier Suchausführungen und unabhängiger Cleanup. [Nachweis](DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md). Runner und CI prüfen diesen Scope getrennt; kein Incident- oder Regressionsnachweis. |
| `DGN-007_PROFILE_COMPARISON` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-07 bestanden gewichtete T0/T1-Metrikvergleiche auf allen drei Versionen je zweimal, einschließlich unabhängigem Cleanup. [Nachweis](DGN_007_PROFILE_COMPARISON_RUNTIME_EVIDENCE.md). Ohne Richtungsgate oder Incidentpromotion. |
| `DGN-007_CONTROL_AB` / `BA` / `AA` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-07 bestanden alle drei neutralen Kontrollfolgen auf jeder Version je zweimal; vollständige neue Reihenfolge mit 36 Lifecycles und unabhängigem Abbau aller drei eigenen Instanzen. Tatsächliche Requestfolge, aktive Plan-ID-/Hash-Union und Variation im [Nachweis](DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md). Ein 2019-BA-Duration-Kontrast liegt innerhalb beobachteter AA-Variation; keine Incidentfreigabe. |
| prospektiver `DGN-007` (Zeitabhängige Regression eines Suchworkloads)-Prüfvertrag | `STATIC_PROSPECTIVE_CONTRACT` | `DEC-068` (Prospektive Duration- und Kontrollseparation für DGN-007 festlegen), reine Record-/Separationsprüfung, 34 synthetische Tests und Quellenvalidator lokal PASS. [Vertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md). Keine SQL-Runtime-Abnahme; Collector und frische Bestätigungsläufe bleiben offen. |
| skalarer `DGN-007`-Collector-Transport | `STATIC_COLLECTOR_TRANSPORT` | Reiner JSON-Decoder mit genauer Decimal-/100-ns-Darstellung, 19 Transporttests und beide Validatoren lokal PASS; 34 Prospektivtests bleiben grün. [Transportgrenze](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md). Keine SQL-Erfassung oder vollständigen RunRecords; fehlende Request-Ergebniszeilen bleiben `NOT_CAPTURED`/`None`. |

## 3. SQL-Server-2025-Delta: abgeschlossene Entscheidungen

Der abgeschlossene Delta-Review dokumentiert folgende Zuordnung:

| Herstellerfunktion | bestehende Anknüpfung | Entscheidung |
|---|---|---|
| Cardinality Estimation Feedback für Ausdrücke | `OPT-006` | `ADOPT`; keine neue Demo, spätere Evidenz im bestehenden Schnitt |
| Optimiertes `sp_executesql` | `QRY-004`, `OPT-007` | `DEFER`; eine spätere Concurrent-Compile-Detailanalyse ist nach der nun belegten `QRY-004`-Freigabe zulässig |
| zeitgebundene Extended-Events-Sessions | `DGN-005` | `ADOPT`; optionaler Engine-17-Schutzpfad |
| TempDB Space Resource Governance | `CON-009`, `RES-004` | `DEFER`; roter Safety- und Infrastrukturvertrag erforderlich |
| Ordered nonclustered Columnstore | `IDX-010` (Columnstore-Segmente gezielt überspringen) | `DEFER`; gelbes Detaildesign erforderlich |
| Query Store auf lesbaren Secondary Replicas | kein unmittelbarer Slice | `DEFER`; Preview- und Mehrinstanzabhängigkeit |

Vector- und KI-Funktionen liegen außerhalb des derzeitigen Curriculumzuschnitts. Der Review verwendet als Ausgangspunkt die offiziellen Microsoft-Dokumentationen zu [SQL Server 2025](https://learn.microsoft.com/sql/sql-server/what-s-new-in-sql-server-2025?view=sql-server-ver17), [Extended Events](https://learn.microsoft.com/sql/relational-databases/extended-events/sql-server-extended-events-sessions?view=sql-server-ver17) und [Query Store auf Secondary Replicas](https://learn.microsoft.com/sql/relational-databases/performance/query-store-for-secondary-replicas?view=sql-server-ver17); vor einer Inhaltsübernahme muss der Projekt-Quellenregisterprozess durchlaufen werden.

## 4. Abhängigkeits- und Stop-Regeln

```text
LABSCN-002 + LABSCN-004 -> DGN-005 + CON-006 validiert -> weiterer Kandidat nur nach Einzelreview
Query Store/XE-Pilot + Mehrsession-Vertrag validiert -> DGN-007 als eigener Folgeschnitt zulässig
```

- Kein `DGN-007` ohne validierten Query-Store-/XE-Pilot.
- Keine rote oder gelbe Lastdemo ohne bestehende Safety-Gates, Wegwerfinfrastruktur, Kill-Switch und Laufzeitbudget.
- Keine Änderung an `SQL_Server_Lab` ohne dokumentierte Fähigkeitslücke und ausdrückliche Freigabe.
- Keine Statusanhebung aus statischem Testbestand allein; Runtime-Status benötigt einen konkreten Laufnachweis.

## 5. Nächster belegpflichtiger Schritt

Der eigenständige automatisierte Datenmodellvertrag ist auf Docker für alle
drei Zielversionen jeweils zweimal praktisch belegt. Seine Prüfungen enthalten
keine Incident-, Query-Store-, XE-, Hypothesen-, Mitigations- oder interaktive
Teilnehmerabnahme. Der anschließend getrennt implementierte
`DGN-007_QUERY_STORE_WINDOWS`-Vertrag ist auf allen drei Versionen je zweimal
praktisch belegt. Er prüft ausschließlich disjunkte T0/T1-Capture-Fenster mit
gleicher Parameterlast. Der getrennte neutrale `DGN-007_PROFILE_COMPARISON`-
Vertrag bestand am 2026-10-07 ebenfalls je zweimal auf allen drei Versionen:
gewichtete Mittelwerte, T1-T0-Deltas und tatsächlich ausgeführte Plananzahl;
kein Richtungs- oder Mindestplangate. Die NULL-Ratio bei Null-Baseline wurde
gesondert mit numerischer Fixture geprüft. Lokale Matrix,
skalare Messwerte und unabhängiger Cleanup stehen im
[Profilnachweis](DGN_007_PROFILE_COMPARISON_RUNTIME_EVIDENCE.md).
Die zusätzlichen neutralen AB-/BA-/AA-Kontrollcaptures sind auf jeder Version
je zweimal praktisch belegt. Sie prüfen denselben Vierermix in fester tatsächlicher
Reihenfolge und unterscheiden ausgeführte Planmengen über beide Fenster.
AB/BA zeigten zwei aktive Plan-IDs/Hashes, AA dieselbe Plan-ID in beiden Fenstern.
Die vollständige neue Reihenfolge mit 36 Lifecycles und unabhängigem Cleanup
steht im [Kontrollnachweis](DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md).
Ein 2019-BA-Duration-Kontrast liegt innerhalb beobachteter AA-Variation;
positives Vorzeichen allein trägt deshalb keine versionsübergreifende
Separation. Diese Captures sind explorative Voraussetzungen, keine
prospektiven Bestätigungsläufe einer Incidentregel. Der getrennte reine
[Prüfvertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md)
legt diese Regel jetzt vorab fest (`DEC-068`): gewichtete Statement-Duration
als primäre zeitbezogene Metrik, alle vier B-A-Kontraste unter AB/BA strikt
positiv und oberhalb beider absoluter AA-Drifts; zusätzlich global entweder
vier unterschiedliche aktive Hashmengen oder einheitlich gerichtete Reads-
Kontraste oberhalb beider absoluter AA-Reads-Drifts. 34 synthetische Tests und
der Quellenvalidator bestanden lokal. Der Status ist ausschließlich
`STATIC_PROSPECTIVE_CONTRACT`, keine Runtime-Abnahme. Der getrennte
[Transport-Vorschnitt](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md)
ist jetzt als `STATIC_COLLECTOR_TRANSPORT` implementiert: 19 tatsächliche
Decoderfixtures, beide Validatoren und die 34 Prospektivtests lokal PASS.
Decimal-Text und UTC-100-ns-Integer bleiben präzise. Fehlende Request-
Ergebniszeilen bleiben `NOT_CAPTURED`/`None`; deklarierte `MEASURED`-Werte
attestieren keine Herkunft. Der Body enthält keine erfundenen Phasen-,
Cleanup-, Lifecycle- oder Ressourcenangaben. Der getrennte SQL-Producer
speichert jetzt tatsächlich gezählte Ergebniszeilen je Request und stellt
die vollständige skalare Projektion vor Cleanup bereit. Seine neue lokale
2019/150-, 2022/160- und 2025/170-Matrix bestand je zweimal AB/BA/AA,
insgesamt 18 vollständige Lifecycles mit tatsächlichem Decoder und unabhängigem
Cleanup. Alle drei eigenen Container sind unabhängig abwesend bestätigt.
Der [Producernachweis](DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md)
bindet konkrete Versionen, Images und Quellenfreeze und hält frühere
Fehlversuche getrennt fest. 156 lokale Testmethoden der Phasendiagnostikrevision ergaben 155 PASS und
einen Linux-spezifischen SKIP unter Windows. Die Producer-Integration über
[Pull Request 65](https://github.com/gecompat/SQL_PerformanceSchulung/pull/65)
ist abgeschlossen: 14 Workflows und alle 22 Jobs SUCCESS am Head
`20a867e…` gegen Base `94ed561b…`, Integration `df78cb0…`.
Je Version bestanden zwölf Lifecycles mit sechs tatsächlichen Decoder-
Captures und unabhängigem Cleanup; Linux führte alle 156 Methoden ohne
SKIP aus. Der Squash `da7b0eb…`, vollständige Übernahme, synchronisiertes
Main und lokale/remote Bereinigung des eigenen Branches sind bestätigt.
Die zwei historischen CI-Fehler bleiben getrennt dokumentiert, ohne
behauptete Ursache oder Behebung. SQL-Prädikate und Budgets bleiben gleich.

Die getrennte Main-Push-CI am Squash `da7b0eb…` ist danach vollständig
beendet: 12/13 Workflows und 47/48 Jobs SUCCESS, ausschließlich SQL Server
2022 im zweiten BA-Lifecycle `CONTROL_EVIDENCE / FAIL_RESULT_CONTRACT / G13`.
Alle zehn begonnenen 2022-Abwesenheitsprüfungen und der ownergebundene
Containerabbau einschließlich expliziter CID-Abwesenheit bestanden.
2019/2025 bestanden je zwölf Lifecycles und sechs Captures. Der neue Fehler
ist von der erfolgreichen PR65-Integration und den zwei historischen
CI-Fehlern getrennt zu bewerten; seine skalare Ursache ist offen.

Die private skalare Probe ist als begrenzte Gegenprobe abgeschlossen: auf
neuer eigener 2022-Instanz mit CI-Imagebindung und tatsächlicher Version
`16.0.4295.3` bestanden Datenmodell, Fenster, Profil, AB und BA jeweils zweimal,
insgesamt zehn Lifecycles und vier Decoder-Captures. Zehn unabhängige
Datenbankabwesenheitsprüfungen, fünf Gruppen-Leerheitsprüfungen, Quellenfreeze
mit 21 Dateien und unabhängiger own-CID-/Namensabbau bestanden. G13 wurde
nicht reproduziert; es liegen keine tatsächlichen verletzten Grenzabstände vor.
Zwei frühere private synthetische Vorchecks scheiterten vor jedem Lifecycle;
Defekte und unabhängiger Cleanup bleiben im Producernachweis getrennt.
Kein Main-, Incident- oder Behebungsnachweis; AA wurde nicht ausgeführt.

Nächster belegpflichtiger Schnitt ist ein eigener kanonischer Diagnosebericht,
keine identische Wiederholung: maximal acht gespeicherte verletzte
Profilgruppen, exakte UTC-Ticks und Grenzabstände ausschließlich im bereits
ausgelösten G13-Fehlerzweig. Der Runner bindet diese Metadaten an tatsächliches
stderr, die eindeutige fehlgeschlagene Kontroll-Evidenzphase und den
unveränderten Guard-/Summary-Abschluss; Ausgabe erst nach Cleanup.
Keine zusätzliche Query-Store-Sicht, keine Prädikat-, Last-, Zeitbudget- oder
Outcomeänderung. Der Reporter ist inzwischen lokal implementiert und
unabhängig geprüft: exakt validiertes Entfernen ergibt den ganzen bisherigen
SQL35, Quellenbindung ist erneuert, 43 Runner- und 37 Producer-/Reporter-
Methoden (ein Linux-spezifischer Windows-SKIP) sowie sieben Validatoren
bestanden. Acht tatsächliche temporäre SQL-Branchfixtures auf einer neuen
eigenen 2022-Instanz bestanden, einschließlich Ein-Tick-Abständen, gleicher
Requestgrenzen, UTC-Offset, acht Gruppen und ausdrücklichem Overflow.
Unveränderter Freeze und eigener Containerabbau sind unabhängig bestätigt.
Der ganze Report bleibt atomar innerhalb 24 Diagnosezeilen. Als nächster
Schritt wurde die reguläre CI von [Pull Request 68](https://github.com/gecompat/SQL_PerformanceSchulung/pull/68)
am Head `27a9b5c…` gegen Base `12b130f…`, Integration `55877a5…`, vollständig
beendet: 13/14 Workflows und 20/22 Jobs SUCCESS. 2019 AA1 und 2022 BA1
scheiterten an G13. First−Start beträgt −0,4263 beziehungsweise −0,951 ms;
Last liegt jeweils innerhalb der oberen Grenze. 2025 bestand zwölf Lifecycles
und sechs Captures. Alle 32 ersten Datenbankabwesenheitsprüfungen und neun
SQL-Containerabbauten bestanden; Linux 163 Methoden PASS. Der PR bleibt
unmerged und ohne CI-Freigabe. Der Reporter schließt die Messlücke, belegt
aber keine Ursache oder Behebung. Das beobachtete Millisekundenraster ist
keine zugesagte QS-Auflösung oder Toleranz.

Die einmalige private Originalmaterialisierungsprobe auf neuer eigener 2022-
Instanz reproduzierte G13 bereits in AB1: First−Start −0,2609 ms. Die verletzte
Gruppe enthält in Captureversuch 1 und im getrennten Live-SELECT jeweils genau
eine positive Raw-Zeile mit Count vier, keine Zero-/NULL-/Negative-Zeilen.
Ein Zero-Extremum erklärt diesen lokalen Fehler nicht. Elf temporäre SQL-
Fixtures PASS; sechs Präfix-Lifecycles PASS, AB1 FAIL mit sofortigem Stop,
keine AB2/BA/AA oder erfolgreiche AB-Capture. Sieben erste DB-Abwesenheits-
prüfungen, vier Gruppen-Leerheitsprüfungen und eigener Containerabbau PASS;
CID/Name unabhängig abwesend, Freeze mit 27 Dateien unverändert. Zusätzliche
Projektion/DML (Data Manipulation Language; Anweisungen zum Lesen oder Ändern von Daten) sind Beobachterinstrumentierung, keine identische kanonische
Timingprüfung und kein historischer CI-Ursachenbeweis.

Der quellenbasierte [Mess-/Zuordnungsgegenentwurf](DGN_007_CAPTURE_ASSIGNMENT_DESIGN.md)
liegt jetzt als `PROPOSED` vor. Er trennt exakten zeitlichen Einschluss und
kontrollierte Kollektivzuordnung. Der ausgearbeitete Kandidat benötigt eine
belegte vollständige Familienbasis B, T0-Capture vor T1, Bilanz B→B+4→B+8
über alle Familien-/Intervallgruppen sowie vertrauenswürdig attestierten
Ausführungsumfang. Die vier Vorabrequests laufen vor der expliziten QS-
Konfiguration; frische Datenbank und beobachtete Nullcounts beweisen keine
QS-OFF-Basis oder fehlende nachlaufende Statistik. Konkrete Baseline-,
Intervallaktivierungs- und Herkunftsbelege bleiben offen. Die Vergleichbarkeit
von QS-Endzeiten und SYSUTC-Requestklammer auf exakten 100-ns-Grenzen bleibt
ungeklärt. Das getrennte [deklarative Voraussetzungenmodell](DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md)
prüft die vorab festgehaltenen synthetischen Gegenbeispiele und bedingte
Konsistenz; keine Prozesse im Modell, SQL-/v1-Änderung oder Runtimeattestation.
Die Prüfung ersetzt insbesondere keine tatsächliche Herkunft trotz passender
Counts. Die [Quellen-/Ausführungspfadprüfung](DGN_007_PREMISE_SOURCE_REVIEW.md)
ist abgeschlossen: Procedure-Queries unter AUTO werden erfasst; dokumentierte
asynchrone Persistenz belegt keine verzögerte Publikation. Der tatsächliche
Pfad prüft eigene Calls und Ergebnisse, attestiert aber weder vollständigen
Basisabschluss noch interne Aktivierung, kontinuierlichen Zustand oder
geschlossene Coordinatorherkunft. Der konkrete
[Beobachtungs-/Herkunftsvertrag](DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md)
liegt als PROPOSED vor: acht Acquisitionstages, vollständige Raw-/Gruppen-/
Coveragebindung, zwölf tatsächliche Calls, getrennte Pulsgrenze, überprüfte
Coordinator-Vertrauensquelle und endliche Größen-/Poll-/Observerkosten.
Bounds und deren Durchführbarkeit sind noch nicht runtimevalidiert.
Punktweise QSStates beweisen keine Kontinuität; Sättigung bleibt bedingt.
Die äußere Pipegrenze begrenzt heute nicht das Vorpuffern im Proxy.
Der [Suffizienzreview](DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md) ist abgeschlossen: injektive kohärente
Zählung aus einem unabhängig geschlossenen tatsächlichen Calluniversum kann
Callerfassung tragen; vollständige keyweise Stageledger zusätzlich kollektive
QS-Buckets. Counts beweisen kein kontinuierliches RW/ALL; dieses gesonderte
konservative Methodengate bleibt vorgeschlagen. Heutige Live-Dateizugriffe
und Zielnamen binden keinen vollständigen unveränderlichen Ausführungspfad.
Das getrennte [Sättigungs-/Acquisition-Gegenmodell](DGN_007_SATURATION_COUNTERMODEL.md)
implementiert die synthetischen Gegenproben mit getrennten Teilclaims.
Kein Token ist eine reale QS-Einzelidentität. Das konkrete
[Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md) ist vorbereitet:
Gate-Matrix mit Acquisition-/Count- und konservativem Floatkandidaten, tatsächlicher
Freeze-/Actor-/CID-/Host-/Zugangsgrenze und Kostenplan innerhalb 145/180/60 Sekunden
und 4 CPU (Central Processing Unit; Prozessor)/8 GiB. Alle Methodengates bleiben offen; Einzelmaxima sind keine
gemeinsame Machbarkeitsevidenz. Der [Offline-Quellenbundle-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md)
ist statisch implementiert: feste 27 Mitglieder, Gitblob-/Rohbytebindung,
separate LF-Äquivalenz und deklarierte AST-Imports samt Manipulationsfixtures.
Statischer Kandidaten-PASS attestiert keine verwendeten Runtimebytes.
Die getrennte [Prozess-/Manifestkantenprüfung](DGN_007_EXECUTION_EDGE_VERIFIER.md)
ist statisch implementiert: Python-3.12-Ganz-AST-Profil, sechs SQL-only-Manifeste,
14 Quellenhashes und SQLCMD-Gegenproben. Import-/Launcherentwurf PROPOSED,
tatsächliche Importumgebung und verwendete Runtimebytes offen. Der getrennte
[synthetische Streaming-/Budgetprototyp](DGN_007_STREAMING_BUDGET_PROTOTYPE.md) ist implementiert:
portable Budgetgegenproben und feste eigene Linux-Kindfälle; keine Integration
in die neun Runtimequellen oder reale Laufzeitmachbarkeit. Die getrennte [numerische Pipelinegegenprobe](DGN_007_NUMERIC_PIPELINE_COUNTERMODEL.md) ist implementiert: 28 synthetische Tests trennen Oracle, deklarierte Fragmentrundung, vorgegebenen Text und bestehende Consumergewichtung. Keine SQL-Konversionsemulation, Epsilon- oder Methodenfreigabe. Der konkrete [Import-/UsedBytes-Entwurf](DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md) liegt als `DESIGNED` vor: feste Import-Only-Einstiege, kontrollierter Rohbyte-Loader, vertrauenswürdiges Interpreter-/Stdlibprofil, getrennte Receipts und begrenzter eigener Cleanup. Der erste Implementierungsteil ist das getrennte [Eingangsprotokoll](DGN_007_IMPORT_PROBE_INPUT_PROTOCOL.md): unveränderter 27-Member-Git-/Kantenvorcheck, eingefrorene neun Python-Rohbytes und begrenzte binäre Rahmung mit Kontext- und Manipulationsgegenproben. Keine Worker- oder Kandidatenimportausführung und kein UsedBytes-Claim. Die getrennte [synthetische Memory-Loader-Komponente](DGN_007_MEMORY_LOADER_FIXTURE.md) ist implementiert: ausschließlich feste Fixturebytes, tatsächliches Compile/Exec und objektgebundene Beginn-/Abschlussreceipts. Kein DGN-Import oder Importauflösungsnachweis; DGN-Attestationsflags bleiben false. Der getrennte [Interpreter-/Stdlib-Profilvorschnitt](DGN_007_IMPORT_RUNTIME_PROFILE.md) ist implementiert: begrenzte aktuelle Bootstrapmetadaten und Vergleich gegen separat deklarierte Baseline. Keine Trust- oder bereits ausgeführte Bibliotheksbyteattestation; die gewählte Kontrollruntime bleibt eine ausdrücklich benannte Annahme. Der [skalare Parent-/Worker-Profilbindungsvertrag](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md) liegt als `DESIGNED` vor. Der getrennte [reine Profilvergleich](DGN_007_IMPORT_PROFILE_BINDING_MATCHER.md) ist implementiert: 38 synthetische Tests prüfen exakte deklarierte Installation und Workerinventur, eingefrorenen Eingangs-/Ordinal-/Phasenkontext sowie gemeinsame Metadatengrenzen. Sein Match attestiert keine tatsächliche Workerbeobachtung, Herkunft oder Consumption. Die tatsächliche Prozessanbindung bleibt unimplementiert. Die getrennte lokale Record-Rückgabe des Profilvorschnitts ist jetzt implementiert: `observe_current_interpreter_records` liefert ausschließlich die tatsächlich aufgenommene und vollständig geprüfte Abschlussaufnahme, bei Ablehnung keine Records. Gehaltene Liveanker sind kein dauerhaft gültiger Zustand des Modulcaches; spätere aktuelle Runtimeverwendung braucht eine frische Aufnahme. Legacyreports, Bootstrapimports und Grenzen bleiben erhalten. Die konkrete Bootstraproute ist jetzt im [Profilbindungsentwurf §8](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#8-konkreter-bootstrap--und-projektionsvorschnitt) festgelegt: geplante Scriptquelle als `__main__`, unveränderter Profilmodulname, benannte direkte Stdlibimports und Vorinitialisierung der Sysconfigwerte ohne zusätzliche Projektimports. Feldherkunft, frische Aufnahme, erneute Livekohärenz und engere Scalarformen sind getrennt beschrieben. Die getrennte importneutrale skalare Projektion ist jetzt im bestehenden Profilmodul implementiert: frische Aufnahme, vollständige private primitive Tupel, erneute Livekohärenz vor und nach Projektion sowie zusätzliche separat gewählte und gegen Factorycode/Closure geprüfte FileFinder-Hookbindung; bei Ablehnung keine Skalare. Dies attestiert keine unabhängige Factoryherkunft oder tatsächlichen Worker. Eine getrennte lokale Bootstrap-Charakterisierung unter CPython 3.12.3 erfasste 85 Modulnamen mit genau zwei Controls; dies ist keine operative Sollinventur. Der [konservative Größenbeleg](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#9-charakterisierte-bootstraproute-und-größenuntergrenze) zeigt bereits mindestens 16.449 Bytes für das vollständige Modularray und 21.108 bis 21.144 Bytes für die gemeinsame Metadata einschließlich Header, unverändertem Input82 und Kontext. Die heutige benannte JSON-Form ist damit für diesen vollständigen charakterisierten Namenumfang nicht darstellbar; andere Routen und Installationen sind dadurch nicht ausgeschlossen. Keine Capanhebung, Filterung oder Digestersetzung ist freigegeben. Der vollständige Linux-/Python-3.12-Import-Only-Prototyp bleibt offen; der getrennte Darstellungs- und Digestentwurf aus Profilbindungsentwurf §10 liegt als DESIGNED vor. Die separat vorgewählte vollständige Kontrollfixture und reine Größenprüfung in §11 belegen gemeinsame Metadata von 17.127/17.113/17.091 Bytes; der §10-Tupelkandidat überschreitet das unveränderte 16.384-Byte-Cap. Neuer Sizer34/34 und Legacy27/40 ohne SKIP. Der getrennte verlustfreie Stringpoolentwurf in §12 liegt als DESIGNED vor, mit eigenen lokalen Pools je Form und unveränderten Inhalten/Caps einschließlich höchstens 256 Poolwerten. Der eigene reine Pool-Sizer in §13 bestand 37/37 isolierte Gegenproben ohne SKIP und die vollständige neue 3×5-Rechnung: maximal 9.389 Bytes einschließlich Header und 204 Poolwerte, vollständig unabhängig nachgerechnet und rückgewonnen. Der getrennte experimentelle Formcodec in §14 bestand 41/41 isolierte Gegenproben ohne SKIP; die vollständige Originalfixture bestand alle 3×5 Frames, Feldrückgewinnung, kanonischen Repack und drei eigene Digestdomains je Ordinal. Das gesamte Fünf-Formen-Set umfasst 28.264/28.257/28.246 Bytes. Originalauswahl und Inputrahmen bleiben unverändert, keine neue Aufnahme oder Nonce. Der unabhängige Nachreview bestätigte sämtliche Frames, Feldrückgewinnung und Digests aus den unveränderten Originaleingaben ohne Codec-/Helper-Replay. Der eigene reine kombinierte Eingangsprototyp in §15 bestand 34/34 isolierte Gegenproben ohne SKIP und die neue vollständige Originalfixtureprüfung: drei Frames mit jeweils 9.389 Metadata-/Headerbytes und 130.837 unveränderten Bodybytes, insgesamt 140.226 Bytes. Tatsächliche vollständige Feld-/Rawbyterückgewinnung und Repack sowie unabhängige Stdlib-Nachrechnung ohne Replay bestanden. Alle gleichzeitig geltenden Caps bleiben erhalten; 64 KiB begrenzen ausschließlich die fünf Metadataausgaben. Die konkrete operative Bootstrap-/Kanalreihenfolge in §16 liegt als DESIGNED vor: importneutraler PRE-Vorschnitt, vollständiger Profilvergleich vor Bodyfreigabe und vollständige Eingangsprüfung vor Importfreigabe, unveränderte gemeinsame Caps und gehaltene Kontrollquellenführung. Der reine Kontrollbootstrapquellengenerator in §17 bestand 32/32 ausschließlich synthetische Gegenproben ohne SKIP unter CPython 3.12.14; er ist keine operative Workerroute. Die getrennte [Sysconfig-Vorinitialisierung §18](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#18-feste-sysconfig-vorinitialisierung-gehaltener-kontrollquellen) bestand 53/53 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die private native Auswahl nach [§19](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#19-private-auswahlgrundlage-vor-einer-vollständigen-operativen-inventur) ist mit genau einem begrenzten Versuch und unabhängigem Prozess-/Record-POST abgeschlossen. Die additive reine [Inline-Metadata-Syntaxquelle §20](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#20-reine-additive-inline-metadata-syntaxquelle) bestand 80/80 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste Fixture-Label-Fehllauf bleibt getrennt dokumentiert. Die additive reine [Inline-Metadata-Semantikquelle §21](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#21-reine-additive-inline-metadata-semantikquelle) bestand nach zwei engen Fixturekorrekturen 108/108 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 106/108-Lauf bleibt getrennt dokumentiert. Vollständige deklarative M/IP/S15/P11/D9-Semantik, unveränderter benannter Originaldigest und Providerkohärenz sind geprüft. Die additive reine [Inline-Profilreporterquelle §22](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#22-reiner-additiver-inline-profilreporter) bestand im einzigen isolierten Lauf 149/149 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige Scalarprojektion, eigener REPORTED-Pool, atomare begrenzte Records und getrennte Original-/Reportdigests sind geprüft; vier frühere Builder bleiben erhalten. Die reine begrenzte [Inline-Header-/Metadata-Aufnahme §23](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme) bestand im einzigen isolierten Lauf 174/174 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Exact-Chunktype-/Größenvorläufe, vollständige deklarative M-Semantik und atomare gehaltene Rückgabe sind geprüft; fünf frühere Builder bleiben erhalten. Die additive reine [K-Domain-/Commandquelle §24](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands) bestand im einzigen isolierten Lauf 209/209 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständiger K8-/D9-Vorlauf, eigene headerfreie E4-K-Domain und atomare kanonische Commands gegen separat gehaltene Callerwerte sind geprüft; sechs bisherige Builder und 174 alte Tests bleiben erhalten. Die additive reine [Inline-Metadata-Callerquelle §25](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich) bestand nach zwei engen Fixturekorrekturen 243/243 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 241/243-Lauf mit zwei Fehlern vor Matcheraufruf bleibt getrennt dokumentiert. Beide vollständigen Formen und Semantiken, zwei eigene Originalinputdigests und vollständiger Abgleich gegen separat gehaltene I7/W6/K8 sind geprüft; sieben bisherige Builder und 209 alte Tests bleiben erhalten. Die additive reine [Inline-Rawbodyaufnahme §26](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies) bestand nach einer engen Fixturelabelkorrektur 272/272 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 271/272-Lauf bleibt getrennt dokumentiert. Vollständige Formen und Größen vor Hashes, beide tatsächlichen D9 und neun Rawhashes vor Callerabgleich sowie atomare Originalbodyrückgabe sind geprüft; acht bisherige Builder und 243 alte Tests bleiben erhalten. Die additive reine [Profilrecord-Reassemblierung §27](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords) bestand im einzigen isolierten synthetischen Lauf 304/304 Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige begrenzte Control-/Envelopeformen, interne Konsistenz, kanonische Controls und tatsächlicher Footerhash vor Callerordinal sowie atomare Originalrecordrückgabe sind geprüft; neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei enge Fixturelabelkorrekturen wurden vor dem ersten Lauf reviewt; kein ausgeführter Fehllauf. Die additive reine [Inline-Profil-Callerquelle §28](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich) bestand im einzigen isolierten synthetischen Lauf 341/341 Gegenproben ohne SKIP unter CPython 3.12.14. Beide vollständigen R4-Formen/Semantiken, Actual-Pool-Repack und vollständiger separater Callerabgleich sind geprüft; die Matchfunktion berechnet keinen SHA. Zehn frühere Builder und 304 alte Methoden bleiben erhalten. Vorreviewkorrekturen und genaue Grenzen stehen in §28. Die additive reine R→BODY_RELEASE-Planquelle aus §29 bestand im einzigen isolierten synthetischen Lauf 378/378 Gegenproben ohne SKIP unter CPython 3.12.14; elf alte Builder und 341 alte Methoden bleiben erhalten. Die additive reine INPUT_COMPLETE-Quelle aus §30 bestand im einzigen isolierten synthetischen Lauf 413/413 Gegenproben ohne SKIP unter CPython 3.12.14; zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige Record-/Footer→R-Calleradapter aus §31 ist rein additiv implementiert und im isolierten synthetischen Lauf mit 460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden bleiben erhalten. Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente) ist im isolierten synthetischen Lauf mit 66/66 PASS ohne SKIP geprüft. Reservierungen, ganze Slot-/Zustandsbindung, sticky Fehler und einmaliger Fakecleanup sind lokal belegt; kein tatsächlicher Kanal-/Loader-/Absenznachweis. Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen. Frische operative Auswahl, inline Empfang/Reporting, tatsächliche Parent-/Worker-Anbindung, feste Quellenauflösung, tatsächliche DGN-Loaderverwendung und Importabschluss sowie begrenzte eigene Worker mit unabhängigem Cleanup bleiben getrennte Gates. Die charakterisierte Kontrollfixture ist keine operative Workerbaseline; Migration bleibt offen. Sein Claim bleibt auf tatsächlich abgeschlossene Top-Level-Imports begrenzt; keine vollständige UsedBundle-, SQL-, Acquisition- oder Methodenattestation.
Normative Methoden-/Grenzänderungen brauchen eine ausdrückliche neue Entscheidung.
Keine implizite OFF-/CLEAR-/Laständerung. Erst eine tragfähige explizite
Methodenentscheidung erlaubt gemeinsam versionierte
SQL-/Transport-/Record-/Evaluator-/Coordinator-Umsetzung. Bestehende Guards,
Fehlerklassifikation, DEC-068, Last und Budgets bleiben erhalten; keine
pauschale 1-ms-Toleranz, Abrundung oder Wiederholen bis grün. Die alternative
Methode ist weder entschieden noch implementiert oder abgenommen. Der frühere Acht-Fixture-Vorcheck enthält keine vollständige
Lifecycle-/Versionsmatrix oder Reproduktion des Main-G13.

Die interne verlustfreie Capture-Rückgabe ist lokal vorbereitet und geprüft;
Veröffentlichung und Integration sind bis zur G13-Klärung zurückgestellt.
Danach folgt der geplante API-Schnitt:
Body, tatsächlich geprüfte Phasen und erfolgreiche erste unabhängige
Datenbankabwesenheit über denselben Harness erhalten. Rückgabe erfolgt
nur nach erfolgreichem Lifecycle und Cleanup; erfolgreiche Recovery
ändert einen ersten Abwesenheitsfehler nicht in PASS. Der direkte Helper
akzeptiert ausschließlich unveränderte bekannte Kontrollverträge.
Counts-/CLI-Ausgabe und Fehlerprioritäten bleiben erhalten; keine
RunRecords, Incidentbewertung oder `runtime_attested=True`.
Danach muss der Collector-Coordinator den integrierten Freeze und Quellen,
Ressourcen, präzise Budgets und tatsächliche serielle Reihenfolge attestieren
und Cleanup unabhängig bestätigen. Die interne Capture-Rückgabe allein
ist kein vollständiger RunRecord oder Coordinator-Nachweis.
Erst danach folgen frische Bestätigungsläufe unter
der festgelegten Regel. CPU bleibt ergänzend, ohne Fallback. Keine
nachträglich ausgewählte Ratio oder statistische Signifikanzbehauptung;
fehlende tragfähige Evidenz bleibt `SKIP_EVIDENCE_MISSING`.
Plan- beziehungsweise klar unterscheidbare Runtimeprofile sind zusätzlich
gegen den Designvertrag zu begründen; Planunterschiede ersetzen kein Symptom
und isolieren keine Kompilierungsursache. Unterschiedliche Parameterlast
allein ist kein Regressionsnachweis. Als begrenzte Voraussetzung verwendet der
ältere Teilnehmerpfad jetzt `sys.databases.compatibility_level` mit NULL-Guard
und prüft vor der Evidenzausgabe den bestehenden 2025-/170-Vertrag; auch die
Adaptervalidierung lehnt fehlende Compatibility-Werte ab. Die
Beobachtungsbedingung muss weiterhin auf den Designvertrag (Plan- oder
Laufzeitprofilevidenz) abgeglichen werden. Der Compatibility-Vorfix belegt
weder den Incident noch eine vollständige Teilnehmerabnahme.
Für die ältere Beobachtungsbedingung sind ausschließlich erfolgreich
ausgeführte T0/T1-Pläne und ihre validierten Profile maßgeblich; historische
oder ungenutzte Planzeilen und bloße Counts 3/5 genügen nicht. Ihr bisheriger
unterschiedlicher Lastmix ist zuerst gegen den gleichen Parameterlastvertrag
abzugleichen. Live-Mittelwerte dürfen keine nachträglichen Zusatzrequests
enthalten; Plan-/Profilunterscheidbarkeit und Verschlechterung sind getrennt
zu begründen. Die jetzt gemessenen unterschiedlichen Richtungen für CPU und
Reads erfüllen allein keine Incidentfreigabe.
Danach folgen die vollständige Capstone-Matrix und die
interaktive Docker-/Podman-Abnahme; deren offene Gates bleiben bestehen.

Der Capstone-Planungsschnitt ist mit `TSK-002` entschieden
(`DECIDED_PLANNING`, Detailreview
[LABSCN-005 – Detailreview DGN-007 (Planungsschnitt)](LABSCN_005_DGN_007_DETAIL_REVIEW.md)).
Implementierungsschnitt A (Project Adapter `0.1` mit Datenaufbau,
Query-Store-Zeitfenstern und Incident-Erzeugung ohne Mitigationsmarker) besitzt
seit dem 2026-09-14 die praktische Docker-/Podman-Lifecycle-Abnahme: Docker-Run
`9ac100f8-f24f-420e-949c-943e35b9bcda` und Podman-Run
`e06e9ec9-d239-4cd0-b9a7-0050dc574180` bestanden jeweils Start -> `READY_FOR_USER`,
Reset -> `READY_FOR_USER` und Remove -> `REMOVED` auf SQL Server 2025. Die
verbleibende Gesamtabnahme umfasst den vollständigen Lifecycle dieser
Schnitt-B-Fassung und die begrenzte Provider-/Versionsmatrix. Der manuelle Teilnehmerablauf sowie
die Evidenz-, Hypothesen- und Mitigationsartefakte sind statisch geprüft.
Frische SQL-Server-2025/Linux-Runs bestanden am 2026-09-19 auf Docker
(`ea802c20-4820-4007-a441-43a74a89c8fc`) und Podman
(`fba84720-5f0b-4537-bc98-75bbad37a85b`) Adapter-Install/Validate, alle sechs
Demo-Stufen, Teilnehmer- und Adapter-Cleanup sowie Lab-Remove. Das belegt die
aktuelle Linux-Providerparität, ist aber keine Szenariopromotion und keine
vollständige Lifecycle-/Versionsmatrix. Ressourcen-, Netzwerk-, Hyper-V- und
gemischte Topologien bleiben ohne konkreten fachlichen Bedarf gestoppt.
