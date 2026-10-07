# DGN-007 – Entwurf des Beobachtungs- und Herkunftsvertrags

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED` – konkrete Records und Grenzen, keine Methodenfreigabe |
| Stand und Quellenabruf | 2026-10-07 |
| geprüfte Repositorybasis | `f13359cac6bc6a5120f61d09b6cff21e6d431c5a` nach PR72 |
| Arbeitspaket | bestehender automatisierter DGN-007-Schnitt |
| Grundlage | [Methodenentwurf](DGN_007_CAPTURE_ASSIGNMENT_DESIGN.md), [deklaratives Modell](DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md), [Quellen-/Codeprüfung](DGN_007_PREMISE_SOURCE_REVIEW.md) |
| Abnahmegrenze | Dokumententwurf und unabhängiger Review; keine SQL-Runtime oder ausführbare Vertragsänderung |

## 1. Aussage und unveränderte Grenzen

Der Entwurf konkretisiert die Beobachtung einer vollständig abgegrenzten
Suchfamilie und den dafür benötigten Coordinatorbeleg. Ein enumerierter
Capture beschreibt zunächst tatsächlich gelesene Katalogdaten. Historische
Vollständigkeit, kontinuierliche QS-Erfassung und geschlossene Herkunft sind
zusätzliche Voraussetzungen; ein Record darf sie nicht selbst attestieren.
Die sechs offenen Modellprämissen bleiben ausdrücklich offen.

Alle folgenden Records, Schritte und Zahlen sind `PROPOSED`. Es existiert
noch kein solcher Transport oder Runtimebeleg. Die Aussagegrenze bleibt
`PROJECT_SEMANTIC`, `runtime_attested=False`; exakter zeitlicher Einschluss
und Methodenfreigabe werden nicht behauptet. G13, v1, DEC-068, Last und
historische FAILs bleiben unverändert. Der Entwurf ergänzt weder OFF/CLEAR
noch Suchcalls oder Warmupprofile. Er erlaubt keinen Merge von PR68.

## 2. Gemeinsame Bindung und Recordgruppen

Jeder Record erhält dieselbe überprüfte Lifecycle-/DBgeneration, vollständige
eigene CID, Sourcebundlebindung, Major/Compatibility, Scope, Block/Slot,
tatsächliche Phase und streng geordnete Ereignisordinal. Eine Acquisition
bekommt zusätzlich Stage, Versuch und eindeutige Capturegeneration.
Datenbankname, `AUTO`, Object-/Query-/Plan-ID gelten nur innerhalb dieser
Generation. Frei deklarierte Digests oder Identitäten liefern keine Herkunft.

| vorgeschlagene Recordgruppe | konkreter Inhalt | zulässige Aussage |
|---|---|---|
| Acquisition | Hoststart/-ende monoton, unveränderte SQL-Readticks, Source-/Zielbindung, Stage/Versuch, Enumerationszahlen, Overflow und vollständiger Abschluss | zeitlich und mengenmäßig begrenzter eigener Read; kein atomarer Snapshot |
| QSState | desired/actual state, Capturemode, Readonlyreason, Intervall-/Flushkonfiguration, Storagegröße/-limit, Retention, Cleanupmode, MaxPlansPerQuery; vor/nach jedem Acquire sowie vor/nach Calls und Zustandsoperationen | tatsächlicher Zustand an diesen Punkten; keine unbeobachtete Kontinuität |
| Family | sämtliche marker-/objekt-/kontextgebundenen Parentqueries, alle zugehörigen Variants und Dispatcheranker, Version und Relationstyp | enumerierter Familienumfang; Dispatcher gelten nicht als aktive Ausführungen |
| Plan und Interval | eindeutiges Plan→Query, Hash und versionszulässiger Typ; alle in der Familienaufnahme referenzierten Intervall-IDs mit Originalgrenzen | vollständige Bindung der aufgenommenen Gruppen, ohne Filter auf T0/T1 |
| RawFragment | Snapshotordinal, Query/Plan/Intervall/ExecutionType, nullable Count, originale vier QS-Avgmetriken und First/Last-Ticks | tatsächlich gelieferte Fragmente; keine Deduplizierung anhand runtime_stats_id |
| Group | Countsumme, gewichtete Duration/CPU/Reads/Rows, All-Fragment- und separat Positive-/Zero-Extrema, Anzahl Positive/Zero/NULL/Negative | Aggregate aus exakt derselben Rawmaterialisierung; keine stille Null-/Zeroentfernung |
| Coverage | je finalem Familienmitglied und Stage: aufgenommen, vollständig nachgewiesen abwesend oder unbekannt, jeweils mit Acquisitionbindung | Abwesenheit nur bei begründeter vollständiger Scopeaufnahme; fehlend ist nicht null |
| Call | tatsächlicher Start/Abschluss, Parameter, Request-ID, Statement-/Sourcebindung, Ergebnisvergleich, tatsächlich gemessene Rows oder ausdrücklich nicht erfasst | eigener erfolgreicher Aufruf; keine individuelle Request→Plan-Zuordnung |
| Pulse | fester Statementursprung und Querykontexte, eigener Start/Abschluss, Ergebnis 12, vollständige Vor-/Nachgruppen und QS-Countdelta genau 1 je erfolgreichem Ein-Statement-Call im tatsächlichen Intervall | retrospektive QS-Aktivität dieses Pulses |
| Lifecycle | tatsächliche Pflichtphasen, monotoner Budgetabschluss, erster DBabwesenheitsstatus, getrennte eigene CIDentfernung/-abwesenheit | gebundener eigener Abschluss unter der benannten Vertrauensgrenze |

Die vier Rawmetriken sind `avg_duration`, `avg_cpu_time`,
`avg_logical_io_reads` und `avg_rowcount`. Ihre SQL-float-Werte werden mit
einer verlustfreien Darstellung, etwa CONVERT Style 3, aufgenommen. Nullable
oder ungültige Werte bleiben erkennbar; sie sind keine gültigen positiven
Metriken. Die Darstellung entscheidet keine fachliche Vergleichstoleranz.
[CAST/CONVERT](https://learn.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-ver17).

Aktive Memory-/Diskfragmente werden nach Plan, Intervall und ExecutionType
aggregiert. Ein vielfach joinender Familienpfad darf Fragmente nicht mehrfach
zählen. First/Last bleiben gelieferte Ausführungs-Endzeiten; All-Fragment-
Extrema werden durch die getrennte Positive-Diagnostik nicht ersetzt.
Count 0 liefert keinen neuen Zeitnachweis; NULL/negative Counts verhindern
eine positive Bilanz. Positive Counts anderer ExecutionTypes bleiben sichtbar.
[RuntimeStats](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17).

## 3. Tatsächliche Folge und Acquisition

| Punkt | Lage im gebundenen Ablauf | Pflichtbeleg |
|---|---|---|
| PRIOR_PRE | nach eigenem Setup, vor erstem Vorabcall | neue Generation, QSState und Familienaufnahme vor den vier Calls |
| PRIOR_POST | nach letztem erfolgreichem Vorabcall | tatsächliche vier Calls und Zustände, vollständiger Ledger |
| CONFIG_POST | nach bestehender RW/ALL-Konfiguration | tatsächliche Optionen und unveränderte Basis B; keine nachträgliche Basisanpassung |
| T0_PRE | nach separat beobachtetem Puls, vor erstem T0-Call | gebundenes T0-Intervall und leere zusätzliche Familienbasis dort |
| T0_POST | nach vier T0-Calls, vollständig vor erstem T1-Call | vier tatsächliche Ergebnisse und Bilanz B+4 |
| T1_PRE | nach Rotation/Puls, vor erstem T1-Call | anderes tatsächlich beobachtetes Intervall, unveränderter T0-/Basisstand |
| T1_POST | nach vier T1-Calls | vier tatsächliche Ergebnisse und Bilanz B+8 |
| FINAL | später vor Cleanup, ohne weiteren Suchcall | finale Familie, Rückbindung aller Stages und unveränderte Gesamtbilanz |

CONFIG_POST und T0_PRE dürfen nur denselben Acquire verwenden, wenn zwischen
beiden nachweislich kein Ereignis liegt. Ein dazwischen ausgeführter Puls
verhindert dieses Zusammenfallen. Stagebezeichnungen ersetzen keine
tatsächlichen Start-/Abschlussordinale. Alle Versuche bleiben gebunden;
fehlgeschlagene Aufnahme oder Overflow werden nicht durch eine günstigere
Wiederholung ersetzt. Ein ausdrücklich noch unvollständiger Sichtbarkeitsread
darf höchstens einen weiteren Versuch erhalten, ohne neue Suchlast.

Genau zwölf eigene Calls führen das gebundene Zielstatement jeweils genau
einmal aus: vier unveränderte Vorabcalls, vier T0-, vier T1-Calls. Die
Vorabparameter werden als Menge und tatsächlich beobachtete Reihenfolge
erfasst; der bisherige Cursor garantiert keine feste Ordnung. Nicht gemessene
Vorab-Rows bleiben unbekannt. Für T0/T1 bleiben A-/B-Reihenfolge und
tatsächlich gemessene Rows gemäß v1 erhalten, je Fenster insgesamt 4.229.

Jeder Acquire enumeriert sämtliche passenden Parentkontexte, Variants und
Pläne vor dem Rawread und bindet sie anschließend erneut. Aus genau einer
begrenzten Rawmaterialisierung entstehen Originalaggregate und Diagnostik.
Es gibt keinen Fenster-/Type-0-/Positive-only-Filter und keine Kürzung durch
`HAVING SUM>0`. Größenprüfungen lesen höchstens Limit+1 Records; der zusätzliche
Sentinel kennzeichnet Overflow und liefert keine gültige Teilbilanz.
Vor-/Nachgleichheit erkennt sichtbare Änderungen, garantiert aber keine
atomare Historie der getrennten Views.

FINAL bindet seine ganze Familie auf frühere Acquisitions zurück. Ein spät
sichtbares Mitglied erhält dort ohne vollständigen Abwesenheitsbeleg
`UNKNOWN`, keinen erfundenen Nullcount. Basis und T0 werden **keyweise**
verglichen: Plan/Query/Intervall/Type, Counts, sämtliche Vertragsmetriken
und positive First-/Last-Extrema. All-/Zero-Extrema bleiben getrennte
Originaldiagnostik; deren zusätzliche Stabilitätsregel ist noch zu entscheiden.
Verschwindende und wachsende Gruppen dürfen sich nicht verrechnen.
Die Float-Stabilitätsregel über mehrere Materialisierungen muss vor Freigabe
ausdrücklich entschieden werden; dieser Entwurf führt keinen Puffer ein.

## 4. Puls, Zustand und bedingter Basisabschluss

Der Puls besitzt einen festen quellengebundenen Statementursprung, überprüfte
Querykontexte und getrennte vollständige QS-Gruppen. „Neueste Query-ID“ oder
Queryhash allein genügt nicht. Sein eigenes positives Countdelta muss genau
einem tatsächlichen QS-Intervall zugeordnet werden; mehrere Intervalle,
unbekannte Basis oder zusätzliche Pulscalls erlauben keine eindeutige Wahl.
Je erfolgreichem Pulscall wird das gebundene Statement genau einmal
ausgeführt; der erwartete Countdeltaumfang ist genau 1 über sämtliche
gebundenen Pulsgruppen aller Types und Intervalle. Jeder tatsächliche
Pulscall besitzt einen eigenen Start-/Abschlussordinal und Ergebnisbeleg.
Ein Delta größer als 1 darf nicht als passender Aktivierungsbeleg gelten.
Delta 1 heilt keine unbekannte frühere Pulsbasis oder Herkunft.
Ergebnis 12, Flushreturn oder SYSUTC-Katalogvergleich ersetzen dieses Delta
nicht. Der Puls ruft die Suchprozedur nicht auf.

`INFERENZ`: Das Delta belegt retrospektiv diesen Puls. Es belegt weder die
Bucketzuordnung der folgenden Suchcalls noch einen durchgehenden QS-Zustand.
Der [Suffizienzreview](DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md) trennt
den möglichen retrospektiven Stageledgerschluss von diesen stärkeren Ansprüchen.
Zustände vor/nach Calls können zwischenzeitliche
OFF/READ_ONLY/Capturemodeänderungen übersehen. Auch ein geschlossener eigener
Actor verhindert automatische QS-Zustandswechsel nicht. Die beobachteten
Optionsrecords sind daher keine vollständige Statechange-Historie.
[QS-Optionen](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-query-store-options-transact-sql?view=sql-server-ver17).

| tatsächlicher Vorabzweig | bedingter Vollständigkeitskandidat | verbleibende Voraussetzung |
|---|---|---|
| durchgehend OFF während aller vier Vorabcalls, neue Generation | zwölf echte Calls, später acht erfasste Fenstercalls; keine universelle QS-Zwölfersumme | historischer Ausschluss früherer Familienstatistik und durchgehende RW/ALL-Erfassung beider Fenster |
| durchgehend RW/ALL während aller vier Vorabcalls | endliche Sättigung B=4 vor T0, danach 8 und 12 | geschlossener Umfang, genau ein Statement je erfolgreichem Call, korrekte eindeutige Countsemantik, vollständiger Scope und Erfassungs-/Intervallkontinuität |
| gemischt, NONE, READ_ONLY, AUTO/CUSTOM ohne separat entschiedenen Beleg oder unbekannt | kein positiver Basiszweig dieses Kandidaten | weder B=0/B=4 noch nachträgliche Korrektur aus Counts ableiten |

Die Sättigungsfolgerung ist logisch **bedingt**: Wenn maximal vier zulässige
Prior-Ausführungen möglich sind und vier unterschiedliche Ausführungen
vollständig bilanziert wurden, verbleibt unter diesen Voraussetzungen kein
zusätzlicher positiver Priorcount. Die Herkunfts-/Acquisitionprämissen dürfen
nicht aus derselben Vierersumme zirkulär abgeleitet werden. AUTO ist hier
kein behaupteter Verlustmechanismus für Procedurestatements.

Flush dokumentiert Memory→Disk, keine Watermark aller Requests. Gleiche
Pollergebnisse schließen die Basis nicht. Eine normale synchrone OFF-Operation
wäre ein eigener methodischer Eingriff und ist hier nicht vorgesehen.
[sp_query_store_flush_db](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-flush-db-transact-sql?view=sql-server-ver17),
[Quellenprüfung](DGN_007_PREMISE_SOURCE_REVIEW.md).

## 5. Konkrete Coordinator-Vertrauensgrenze

Der spätere Vertrag benennt den tatsächlich vertrauenswürdigen Launcher,
Verifier und Host-/Zielverwalter sowie deren kontrollierte Zugänge. Der
gebundene Ausführungspfad erzeugt Records unmittelbar an tatsächlichen
Aktionen. Vom Payload behauptete Vertrauenswürdigkeit, Hashketten oder
Signaturen ersetzen diesen Ausführungsbeleg nicht. Unbekannte Herkunft bleibt
unbelegt; der Entwurf behauptet keine Absicherung gegen beliebige Hostadmins.

Vor der ersten Zielwirkung wird ein unveränderliches ausführbares Bundle
verifiziert und tatsächlich verwendet: SQL, Manifeste, Coordinator, Runner,
Harness, ExecutionTarget, Proxy, Prozesshelper, Packager, Decoder/Evaluator
und ausführungsrelevante Imports. Interpreter, externe Tools und tatsächliches
Image erhalten Identitäts-/Versionsbindungen. Live-Imports, externe Symlinks
und spätere Pfadsubstitution sind ausgeschlossen. Ein Vor-/Nachhash allein
belegt keine Unveränderlichkeit während der Ausführung. Die bisherigen 14
SQL-/Manifesthashes bleiben getrennte statische Integritätsprüfungen.

Jede Aktion adressiert die vollständige eigene CID und dieselbe tatsächlich
erzeugte DBgeneration. Ein neuer synthetischer Lifecyclemarker wird der
Erzeugung zugeordnet und serverseitig geprüft; sein konkreter Mechanismus
gehört in die gemeinsame Umsetzung. Container-/DBersatz oder Replay scheitert.
Der Actor begrenzt sich auf serielle Phasen und höchstens eine aktive eigene
SQL-Session. Der zusätzliche Ausschluss fremder Familiencalls und
Stateoperationen benötigt einen überprüften Zugangsumfang; keine Ports oder
eine leere Sessionmomentaufnahme beweisen ihn allein.

Vier CPU und 8 GiB bleiben erhalten. Konfigurierte Limits, verfügbare
Ressourcen und physische Hostbelegung werden getrennt belegt. Ein ausdrücklich
zuständiger Host-/Scheduleractor muss höchstens eine Zielversion auf demselben
physischen Host durchsetzen. Ein kooperatives Lock umfasst nur seine
kontrollierten Teilnehmer; unterschiedliche Runnernamen oder Matrixjobs
beweisen keine physische Trennung. Eine neue Hoststruktur wird nicht eingeführt.

Der Actor verwendet monotone Hostzeit für tatsächliche Starts/Abschlüsse und
180 Sekunden regulär/60 Sekunden Cleanup. SQL-/QS-Ticks bleiben getrennt.
Prozesswechsel benötigen eine überprüfte Ereignis-/Zeitbindung. Wiederholungen
setzen Budgets nicht zurück. Pflichtphasen und erster unabhängiger
DBabwesenheitscheck müssen erfolgreich sein; Recovery heilt keinen ersten
Fehler. Eigener Containerabbau und exact-CID-Abwesenheit werden separat
unabhängig geprüft. Harte Unterbrechung lässt Cleanup unbekannt.

## 6. Endliche Entwurfsgrenzen und Observerkosten

Diese Zahlen sind **vorgeschlagene technische Obergrenzen**, keine gemessenen
SQL-Kosten oder Übernahme der synthetischen Modelllimits. Alle Teil- und
Gesamtgrenzen gelten gleichzeitig; der zuerst erschöpfte Bound beendet den
Nachweispfad ohne Teil-PASS. Ihre Durchführbarkeit ist noch nachzuweisen.

| Größe | vorgeschlagener Bound je Lifecycle |
|---|---:|
| Stages / Acquireversuche | 8 / höchstens 2 je Stage, insgesamt 16 |
| Familienqueries / Pläne / referenzierte Intervalle je Acquire | 16 / 64 / 16 |
| Rawfragmente / aggregierte Gruppen je Acquire | 256 / 128 |
| zusätzliche Puls-/Rotationspolls | insgesamt höchstens 64, kein Suchcall |
| Sleep zwischen Rotationspolls | höchstens 1 Sekunde, tatsächliche Wartezeit zählt im bestehenden Budget |
| einzelne Acquisition, einschließlich Vor-/Nachbindung | höchstens 2 Sekunden monotone Hostzeit |
| kumulierte aktive Observer-/Pulsqueryzeit | höchstens 20 Sekunden; Wartezeit zählt zusätzlich im regulären Budget |
| skalare Observation-Payload je Acquire / insgesamt | 16.384 / 131.072 UTF-8-Bytes, einschließlich sämtlicher Versuche und Pulsrecords |
| zusätzliche Array-/Parsergrenzen | maximal Tiefe 8; Integer höchstens 19 Ziffern, gültige Werte enger begrenzt |

Metadaten und Coverage zählen innerhalb der Payloadgrenzen. Pro Fragment
werden höchstens vier Metriktexte mit je 64 Zeichen und die gebundenen
Skalare übertragen. Der maximale Zeilenbound garantiert daher kein passendes
Bytevolumen: auch weniger Zeilen können den Bytebound überschreiten. Ein
neues, separat versioniertes Observationformat muss Framezahl/-reihenfolge,
Kanal, Stage und tatsächliche erfolgreiche Summary strikt prüfen. Es wird
hier weder implementiert noch in den v1-Body eingebaut.

Die bisherigen v1-Grenzen bleiben erhalten: 32.768 Bodybytes, 32.000
Framepayloadzeichen, 512 Payloadzeichen je Frame und höchstens 64 defensive Frames.
Observationpayload und v1-Body müssen zusammen mit Phasenoutput innerhalb
der bestehenden äußeren **262.144-Byte-Grenze** bleiben. Diese zählt
normalisierte UTF-8-Textausgabe beider Pipes, unter Windows nach CRLF→LF;
sie ist keine Messung identischer Rohpipebytes. Der heutige Proxy
puffert inneren SQL-Output vorher; eine solche Gesamtgrenze über die ganze
Kindprozesskette ist heute **nicht** belegt. Ein späterer versionierter Pfad
muss Eingangsbytes bereits beim Lesen begrenzen und Overflow fest melden;
nachträgliches Abschneiden oder unbegrenztes Vorpuffern genügt nicht.
[Runner](../../Tests/Runtime/run_dgn007_automated_setup.py),
[Proxy](../../Tests/Runtime/docker_sqlcmd_proxy.py),
[Transport](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md).

Neue Reads, Pulses und Polls zählen in 180 Sekunden regulär; SQL21 behält
seine bestehende 145-Sekunden-Phase, Cleanup 60 Sekunden. Vor Runtime ist
ein überprüfter Kostenplan einschließlich Rotation, Calls, Capture und
übrigen Pflichtphasen nötig. Die Summe der einzelnen Maxima ist keine
Zusage, dass der Gesamtablauf hineinpasst. Kein Timeoutreset, zusätzlicher
Lifecycle oder Budgetanstieg kompensiert den Observeraufwand.

Records enthalten nur erlaubte synthetische Identitäten und Skalare.
Querytext wird zur Herkunftsprüfung serverseitig geprüft, nicht exportiert.
Secrets, Connectionstrings, Plan-XML, Rohfehler und ungeprüfte Prozessausgaben
werden nicht gespeichert. Parse-/Overflowfehler liefern feste bestehende
FWK-012-Codes ohne Payload oder Exceptioncontext.

## 7. Gegenproben und Entscheidungsgates

| Gegenprobe | erforderliche Abgrenzung |
|---|---|
| fehlender geplanter Call und kompensierender fremder Familiencall | passende Count-/Metriksumme ohne geschlossenen Zugang liefert keine Herkunft |
| OFF→RW→OFF oder temporäres READ_ONLY zwischen gleichen Statecaptures | punktweise States/Pulsdelta sind kein Kontinuitätsbeleg |
| zusätzliche Priorstatistik, später Variant, anderer Type/Intervall | vollständige Rückbindung und keyweise Bilanz; unbekannte Coverage bleibt unbekannt |
| duplizierter Join, Memory-/Diskfragmente, Zero/NULL/negative Counts | korrekt gruppieren, Original- und Diagnosewerte erhalten, ungültige Bilanz ablehnen |
| T0 erst nach T1, rückläufige Ordinale, gleicher Count bei geänderten Metriken/positiven First-/Last-Zeiten | tatsächliche Chronologie und vollständige Stabilitätssignatur prüfen |
| Executoränderung trotz gleichem SQLhash, CID-/Generationmix, Replay | unveränderliches Bundle und tatsächliche Ziel-/Ausführungskette erforderlich |
| Hostbindung verloren, Poll-/Zeilen-/Gruppen-/Byteoverflow, Transportkürzung | Bounds vor vollständigem Read/Parse durchsetzen; kein Teilbeleg oder stiller Retry |
| erster DBabwesenheitsfehler, danach erfolgreiche Recovery | ursprünglicher Fehler bleibt; Cleanuppriorität unverändert |
| QS-First einen Tick vor SYSUTC-Start bei sonst passenden Records | im v1 unverändert G13-FAIL; keine Clockfolgerung aus Kollektivbilanz |

Vor einer expliziten Methodenentscheidung sind konkrete Suffizienzgates
zu schließen: (1) wirksame Freeze-/Zugangs-/Hostmechanik und ihre
Vertrauensquelle, (2) kontinuierlicher tatsächlicher Erfassungszustand,
(3) zulässiger historischer Basisabschluss durch endliche Sättigung oder
begründeten OFF-Ausschluss, (4) QS-interne Intervallwahl und Kontinuität,
(5) Acquisitionkohärenz und Float-Stabilitätsregel, (6) durchgängige Bounds
und durchführbarer Kostenplan. Alle sind derzeit **offen**.

Der [Suffizienzreview](DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md) ist
abgeschlossen: injektive kohärente Sättigung unter unabhängig geschlossenem
Callumfang kann Erfassung tragen; vollständige keyweise Stageledger können
kollektive Bucketzuordnung tragen. Kontinuierliches RW/ALL folgt daraus nicht.
Die obigen kontinuierlichen Zustands-/Intervallgates bleiben konservative
Methodenanforderungen dieses Vorschlags, nicht Prämissen des engeren
Sättigungssatzes. Sie werden hier nicht aufgehoben. Tatsächliche Freeze-/
Zugangs-/Hostgrenze, Acquisition-/Floatregel und Kostenmachbarkeit bleiben offen.
Das getrennte [Sättigungs-/Acquisition-Gegenmodell](DGN_007_SATURATION_COUNTERMODEL.md)
prüft jetzt synthetische Ausführungstokens, keine Runtimeidentitäten.
Das konkrete [Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md)
ist vorbereitet: alle Acquisition-/Float-, Vertrauens-/Host-/Zugangs- und
Kostengates bleiben offen. Der [Offline-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md)
ist statisch implementiert; die getrennte [Kantenprüfung](DGN_007_EXECUTION_EDGE_VERIFIER.md)
ist ebenfalls statisch implementiert. Import-/Launcherentwurf PROPOSED,
tatsächliche Importumgebung offen; kein SQL oder Launcherstart. Erst danach folgt die tragfähige Entscheidung vor gemeinsam
versionierter SQL-/Freeze-/Transport-/Record-/Evaluator-/Coordinator-Umsetzung.
Alle drei Zeitbeziehungen QS↔SYSUTC, QS↔Katalog und SYSUTC↔Katalog bleiben
gesondert zu entscheiden; diese Records entfernen kein Zeitprädikat.
Fehlende Pflichtbelege werden nicht zu optionalem `SKIP_EVIDENCE_MISSING`.
Die spätere Fehlerzuordnung verwendet ausschließlich
[FWK-012](../../Demos/00_Framework/Contracts/FWK-012_Status_Error_Skip_Contract.md).

Die Matrix bleibt 2019/150, 2022/160 und 2025/170. Neue Runtime braucht
die ausdrücklich bestätigte genaue eigene Wegwerfinstanz und unabhängig
überprüfbaren Cleanup. Interne API-Veröffentlichung, vollständige RunRecords,
Incident-, Ursachen-, Mitigations-, Capstone-, Teilnehmer- und Szenariofreigabe
bleiben offen. Dieser Dokumententwurf erzeugt keine solche Abnahme.

Der getrennte [synthetische Streaming-/Budgetprototyp](DGN_007_STREAMING_BUDGET_PROTOTYPE.md) ist implementiert:
portable Budgetgegenproben und feste eigene Linux-Kindfälle, ohne Integration
in Runtimequellen oder Methoden-/Runtimeattestation. Nächster kleiner Schnitt: getrennte numerische Gegenprobe von endlicher Oraclepopulation
über ausdrücklich deklarierte Fragmentrundung und separat vorgegebenen synthetischen
Style3-Text bis zur bestehenden Consumergewichtung. Keine SQL-Konversionsemulation,
Epsilon- oder Methodenfreigabe.
