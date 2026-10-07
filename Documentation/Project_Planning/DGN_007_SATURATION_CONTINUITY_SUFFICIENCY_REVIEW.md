# DGN-007 – Suffizienz von Sättigung, Intervallzuordnung und Herkunft

| Merkmal | Wert |
|---|---|
| Status | `REVIEW_COMPLETE` – bedingter logischer Schluss, keine Methodenfreigabe |
| Stand und Primärquellenabruf | 2026-10-07 |
| geprüfte Repositorybasis | `f90737c4b7bc5144947d396eba6999cee709407f` nach PR73 |
| Bezug | [Beobachtungsentwurf](DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md), [Quellenprüfung](DGN_007_PREMISE_SOURCE_REVIEW.md), [deklaratives Modell](DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md) |
| Prüfgrenze | `PROJECT_SEMANTIC`; Dokument- und Codeprüfung, keine SQL-/Docker-Runtime |

## 1. Drei getrennte Nachweisziele

**Endliche Sättigung kann vollständige Callerfassung tragen. Sie beweist keinen
durchgehend gleichen QS-Zustand.** Zusammen mit vollständigen Stageledgers kann
sie kollektiv die vier Calls eines Fensters einem QS-Bucket zuordnen. Diese
drei Aussagen verlangen unterschiedliche Voraussetzungen:

| Ziel | notwendige Belegart | daraus nicht ableitbar |
|---|---|---|
| vollständige Erfassung der eigenen erfolgreichen Calls | unabhängig geschlossenes Calluniversum und eindeutige, kohärente Zählung bis zur belegten Obergrenze | kontinuierliches RW/ALL, vollständige historische Zero-Metadaten |
| kollektive T0-/T1-Bucketzuordnung | zusätzlich Stageabschluss vor dem nächsten Fenster, vollständige keyweise Differenzen und finale Familienrückbindung | einzelner Parameter→Plan, unverändertes Intervall während Leerlauf, QS↔SYSUTC-Einschluss |
| durchgehender tatsächlicher QS-Zustand | vollständiger Beleg relevanter expliziter und automatischer Übergänge | aus Punktcaptures oder Sättigung allein nicht bewiesen |

Die kontinuierlichen RW/ALL-Bedingungen des Beobachtungsentwurfs bleiben
**vorgeschlagene konservative Methodengates**. Dieser Review hebt sie nicht auf.
Eine spätere Methodenentscheidung muss ausdrücklich festlegen, ob der engere
retrospektive Erfassungs-/Bucketnachweis genügt oder der stärkere kontinuierliche
Zustandsnachweis zusätzlich Pflicht bleibt. Es gibt keinen neuen positiven
AUTO-/NONE-/READ_ONLY-Zweig und keine Änderung an v1, G13 oder DEC-068.

## 2. Bedingter Sättigungsschluss ohne zirkuläre Herkunft

`INFERENZ`: Sei E die unabhängig belegte Menge tatsächlich erfolgreicher Calls
bis zum jeweiligen Stageabschluss. Jeder Call führt genau ein Zielstatement
aus. Jede gezählte Einheit muss injektiv einer unterschiedlichen tatsächlichen
Ausführung aus E entsprechen. Das schließt Fremdcalls, Replay, Joinvervielfachung,
doppelte Fragmentübernahme und eine historische Ersatzpopulation aus. Die
Acquisition muss die tatsächlich sichtbaren einschlägigen Familienmetadaten
und Rawfragmente vollständig enumerieren, kohärent in derselben Generation
und mit korrekter Familien-/Plan-/Type-/Intervallbindung. Ihre gezählten
Einheiten bilden unter der Injektivitätsprämisse eine Teilmenge von E; dass
alle E-Ausführungen enthalten sind, wird nicht vorausgesetzt. Destruktive
Ledgeränderungen dürfen den Schluss nicht ersetzen.

Unter diesen **separat belegpflichtigen Prämissen** gilt: Werden N Einheiten
gezählt und enthält E höchstens N Ausführungen, wurden alle N erfasst.
Die Obergrenze und Zähleindeutigkeit dürfen nicht aus derselben N-Summe
abgeleitet werden. Ein vom Payload behauptetes Calluniversum ist kein Beleg.

| abgeschlossener Stage | unabhängig geschlossener Umfang | Sättigungskandidat |
|---|---:|---:|
| Basis nach Prior, vor dem ersten T0-Call | vier Prior-Ausführungen | B=4 |
| T0-Post vollständig abgeschlossen, vor dem ersten T1-Call | Prior vier + T0 vier | 8 |
| T1-Post und vollständige Finalrückbindung | Prior vier + T0 vier + T1 vier | 12 |

Bei korrekt gesättigtem B=4 kann eine verspätete fünfte Prior-Einheit keine
fehlende T0-Ausführung kompensieren: Es existieren unter der geschlossenen
Population nur vier unterschiedliche Prior-Ausführungen. Ohne die Prämissen
bleibt diese Kompensation ein zulässiges Gegenmodell. Die bedingte Ableitung
braucht keinen allgemeinen Requestpublikationswatermark.

Im vorgeschlagenen OFF-Zweig ist die Bilanz stattdessen 0→4→8. Dafür muss der
historische Ausschluss sämtlicher Prior-Statistik unabhängig gelten. B=0,
eine neue Datenbank oder ein späterer OFF-Capture belegen diesen Ausschluss
nicht. Keine OFF-/CLEAR-Operation wird hier eingeführt.

Microsoft dokumentiert Counts und die Aggregation aktiver Memory-/Diskzeilen
nach Plan, ExecutionType und Intervall. Das liefert keine individuellen
Ausführungsidentitäten für den obigen Injektivitätsbeleg.
[RuntimeStats](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17).

## 3. Was ein vollständiger Stageledger über Buckets trägt

Die Gesamtfolge 4→8→12 allein ordnet keine Calls einem Intervall zu. Zusätzlich
müssen die vollständigen keyweisen Ledgers ergeben:

1. T0-Postcapture ist abgeschlossen, bevor T1 überhaupt startet.
2. Frühere Gruppen behalten Counts und die vorab festgelegte vollständige
   Stabilitätssignatur. Es gibt keine Löschung/Repopulation oder ungeklärte
   Veränderung der Familien-/Planbindung.
3. Genau vier neue reguläre Einheiten liegen ausschließlich in I0; danach
   genau vier neue reguläre Einheiten ausschließlich in einem anderen I1.
   Alle anderen Intervalle und Types bleiben im vollständigen Vergleich ohne
   zusätzliche positive Counts.
4. Die finale Gesamtfamilie wird auf alle früheren Acquisitions zurückgebunden.
   Späte Varianten sind nicht nachträglich als früher bekannte Nullbasis zu
   behandeln. Unausgeführte/Zero-Mitglieder benötigen eigene Coverage.

`INFERENZ`: Unter §2 gehören die vier neuen T0-Einheiten kollektiv den vier
T0-Calls, entsprechend T1. I0/I1 sind ihre tatsächlichen QS-Buckets. Es folgt
keine individuelle Request→Plan-Zuordnung. Der gesamte Zielbucket muss für
diesen retrospektiven Schluss nicht während jedes Leerlaufmoments unverändert
aktiv gewesen sein. Ein Split der vier Calls über zwei Intervalle erfüllt
den vorgeschlagenen Ein-Bucket-Vertrag dagegen nicht.

Der separat bilanzierte Puls beschreibt seinen eigenen Call. Ein passender
Puls vor einer Rotation kann bei anders zugeordneten Suchcalls auftreten.
Weder Pulse noch die Intervallsicht besitzen einen dokumentierten vollständigen
Active-/Sealed-Watermark.
[QS-Intervalle](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-interval-transact-sql?view=sql-server-ver17).

## 4. Kontinuität und Acquisition bleiben eigene Gates

Ein vorübergehendes READ_ONLY zwischen Calls ohne verlorenen Zielcall ist mit
vollständiger Sättigung vereinbar. Desired und actual state können automatisch
abweichen; Optionscaptures an einzelnen Punkten erfassen keine vollständige
Übergangshistorie.
[QS-Optionen](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-query-store-options-transact-sql?view=sql-server-ver17).
Auch bekannte Queries unter NONE können weiter erfasst werden. Vollständige
Counts belegen deshalb kein dauerhaftes ALL.
[ALTER DATABASE](https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-database-transact-sql-set-options?view=sql-server-ver17).
AUTO wird nicht als behaupteter Verlustmechanismus für Procedurestatements
verwendet; die [Quellenprüfung](DGN_007_PREMISE_SOURCE_REVIEW.md) bleibt maßgeblich.

Einmalige Rawmaterialisierung verhindert eigene Wiederaufnahme derselben
Materialisierung, garantiert aber keine atomare gemeinsame Katalogsicht.
Vor-/Nachgleichheit der Familienmetadaten attestiert ebenfalls keine solche
Sicht. Die dokumentierte vereinte Memory-/Diskdarstellung ist von der offenen
Kohärenzfrage für getrennte Familien-/Plan-/Runtime-Aufnahmen zu unterscheiden.
Es wird weder ein Herstellerfehler noch eine verzögerte Publikation nach
erfolgreichen Calls behauptet.
[QS-Erfassung](https://learn.microsoft.com/en-us/sql/relational-databases/performance/how-query-store-collects-data?view=sql-server-ver17).

Style3 erhält unterschiedliche einzelne Floatwerte als unterschiedliche Texte.
`INFERENZ`: Das garantiert keine identische gewichtete Rekonstruktion bei
veränderter Fragmentaufteilung; Decimal/Fraction entfernt bereits entstandene
Floatrundung nicht. Exakte Signaturgleichheit wäre konservativ, kann aber
eine unveränderte Ausführungspopulation ablehnen. Die konkrete Regel muss vor
Methodenfreigabe feststehen; kein nachträgliches Epsilon. Positive Extrema,
Zero-Extrema und alle vier Metriken bleiben sichtbar und getrennt zu prüfen.
[CAST/CONVERT](https://learn.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-ver17).

## 5. Tatsächlich verfügbarer Herkunftspfad und seine Grenzen

| heutiger Pfad am geprüften Main | wiederverwendbar | fehlender Beleg |
|---|---|---|
| [Harness](../../Demos/00_Framework/Tools/run_demo.py) lädt Manifest; [Proxy](../../Tests/Runtime/docker_sqlcmd_proxy.py) liest SQL bei jedem Aufruf | tatsächliche serielle Phasen und Calls | unveränderliche verwendete Executor-/Importbytes |
| [Quellenvalidator](../../Tests/Static/validate_dgn007_prospective_acceptance.py) prüft 14 SQL-/Manifesthashes | statische Integrität der benannten Quellen | Interpreter, Tools und vollständig ausgeführte Importkette |
| [ExecutionTarget](../../Tests/Runtime/execution_target.py) und Readiness adressieren Namen | vorhandene Zieladapter | vollständige CID/Daemon-/DBgenerationbindung aller Aktionen |
| [CI](../../.github/workflows/dgn007-automated-setup.yml) ohne Ports/Mounts, mit Labels und CID-Abbau | eigene Provisionierung und unabhängiger CID-Abwesenheitscheck | unbekannte Daemon-/Credentialzugänge, physische Hostexklusivität |
| [Runner](../../Tests/Runtime/run_dgn007_automated_setup.py) erhält ersten DB-Abwesenheitsfehler | Cleanupdominanz trotz erfolgreicher Recovery | vollständiger Coordinatorbeleg |
| [SQL21](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/21_Controlled_Query_Store_Windows.sql) erfasst nach beiden Fenstern | tatsächliche Ergebnisprüfung | vollständiger T0-Postledger vor T1 |

Ein begrenzter Launcher-/Bundle-Verifier ist ein konkreter späterer Kandidat,
keine heute implementierte Vertrauensquelle:

- Tatsächlich verwendete Bundlemitglieder und Bytes gegen eine exakte
  Pfadliste und Gitblobs prüfen; keine externen Symlinks oder Live-Imports.
  `git archive` ist allein kein Freeze: Exportattribute können Mitglieder
  weglassen oder Bytes ersetzen, auch lokale Archivattribute greifen.
  [Git archive](https://git-scm.com/docs/git-archive).
- Tatsächliche private Berechtigungen, festgelegte Tool-/Interpreteridentität
  und Schutz während der Ausführung brauchen einen benannten vertrauenswürdigen
  Launcher und Host-/Zielverwalter. Dieselbe OS-Identität, Administratoren und
  Docker-Daemonberechtigte gehören ausdrücklich in diese Vertrauensgrenze.
  Privatberechtigung allein schließt deren Änderungen nicht aus.
  [Docker-Sicherheitsmodell](https://docs.docker.com/engine/security/).
- Vollständige CID und festgelegten Daemon durch jede SQL-, Readiness-,
  Recovery- und Cleanupaktion führen; tatsächliche DBgeneration und Lifecycle
  serverseitig binden. `--network none` wäre eine konkrete Netzwerkbegrenzung
  auf Loopback, keine Sperre gegen Daemonberechtigte.
  [Docker-Netzwerk](https://docs.docker.com/engine/network/drivers/none/).
- Ein serieller Versionsablauf verhindert Überlappung der eigenen kontrollierten
  Jobs. Ein kooperatives Lock bindet nur Teilnehmer. Eine neue GitHub-VM pro
  Standardjob beweist keine physische Hostexklusivität; vorhandene Hostgrenzen
  werden dadurch nicht umdefiniert.
  [GitHub-Runner](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).

Die API auf dem geschützten lokalen Branch `83f08fb…` ist nur eine Referenz für
Bodyrückgabe nach Lifecycle und erstem DB-Abwesenheitscheck. Sie schließt diese
Gates nicht und bleibt unveröffentlicht. Ein Host-/Daemonabbruch kann Cleanup
unbekannt lassen. Bundle-/Actorbelege beweisen keine QS-Zustandskontinuität.

## 6. Endliche Gegenproben und nächster ausführbarer Vorschnitt

Der in diesem Review vorgeschlagene Vorschnitt ist inzwischen als getrenntes
[synthetisches Sättigungs-/Acquisition-Gegenmodell](DGN_007_SATURATION_COUNTERMODEL.md)
implementiert. Es ergänzt die vorhandenen 42
Voraussetzungstests um den hier expliziten Zählschluss. Synthetische
Ausführungstokens dienen ausschließlich als Modelloracle; reale QS-Zeilen
liefern keine solchen individuellen Tokens. Keine Prozesse, Dateien,
Verbindungen, SQL-/v1-Änderung oder Runtimeattestation im Modell.

| Gegenprobe | erwartete Grenze |
|---|---|
| RO-Lücke ohne Call, alle Calls eindeutig gezählt | bedingte Callerfassung möglich; Kontinuität nicht belegt |
| ein Call fehlt, ein Fremdcall kompensiert die Summe | Herkunftsprämisse verletzt, kein Vollständigkeitsschluss |
| dieselbe synthetische Ausführung durch Join/Fragment zweimal gezählt | Injektivität verletzt trotz passender Summe |
| korrekt gesättigtes B=4, angeblicher fünfter Priorcount | geschlossene Population oder Zählung widersprüchlich |
| Löschen/Repopulation, Replay oder Generationmix | kein unverändert gebundener Stageledger |
| Gesamtbilanz stimmt, vier Calls auf zwei Intervalle verteilt | Callerfassung getrennt von Ein-Bucket-Zuordnung |
| Puls in I0, Suchcalls in anderem Intervall | Puls belegt ausschließlich eigene Aktivität |
| gleiche Counts, veränderte Metriken/positive Extrema | vollständige Stabilität nicht erfüllt |
| wechselnde Fragmentaufteilung bei gerundeten Mittelwerten | Floatregel bleibt separat, kein Epsilon aus Fixture |
| spät sichtbare unausgeführte Variante | positive Sättigung heilt unbekannte historische Coverage nicht |
| T0-Capture erst nach T1 oder gemischte Acquisition | Stage-/Kohärenzprämisse nicht etabliert |

Modell-PASS bedeutet nur bedingte synthetische Konsistenz. Unknown/fehlende
Prämissen ergeben keine Runtimefreigabe. Danach folgt die konkrete
Methodenentscheidung samt Acquisition-/Floatregel, tatsächlicher Vertrauens-
und Hostgrenze sowie Kostenplan, bevor gemeinsam versionierte SQL-, Freeze-,
Transport-, Record-, Evaluator- und Coordinatoränderungen zulässig sind.
Ein Bundle-Verifier kann später separat mit manipulierten Mitgliedern,
Executorbytes, Importpfaden, Zielalias und Replay negativ geprüft werden.

Die acht Stages und vorgeschlagenen Zeilen-/Byte-/Poll-/Observerlimits aus
PR73 bleiben unvalidiert. Durchgängiges Streaming vor dem heute vorpuffernden
Proxy sowie Machbarkeit innerhalb 180/60 Sekunden und 4 CPU/8 GiB bleiben
Pflichtgates. Keine neue SQL-Runtime wird durch diesen Review freigegeben.
Alle drei Zeitbeziehungen bleiben gesondert offen. PR68 bleibt ohne
Mergefreigabe; historische FAILs werden nicht umgewidmet. Incident-,
Ursachen-, Mitigations-, Capstone-, Teilnehmer- und Szenarioabnahme bleiben offen.
