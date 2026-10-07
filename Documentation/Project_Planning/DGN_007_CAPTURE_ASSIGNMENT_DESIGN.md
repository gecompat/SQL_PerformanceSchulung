# DGN-007 – Gegenentwurf zum Mess- und Zuordnungsbeleg

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED` – prüfbarer Methodenentwurf, keine Vertragsfreigabe |
| Stand und Quellenabruf | 2026-10-07 |
| Arbeitspaket | bestehender automatisierter DGN-007-Schnitt |
| geprüfte Repositorybasis | `3234fe0936e894d0c5d8e804c26e2d624a855c8d` nach PR69 |
| Ausgangsevidenz | [Producernachweis](DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md), einschließlich PR68 und privater Originalmaterialisierungsprobe |
| gültige Methode | [prospektiver v1-Vertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md), `DEC-068`, unverändert |
| Abnahmegrenze | Quellen-, Code- und Entwurfsprüfung; keine neue SQL-Runtime, kein implementierter alternativer Nachweis |

## 1. Problem und zulässige Aussagen

G13 verlangt im bestehenden SQL35, dass gespeicherte QS-First/Last-Zeiten
innerhalb `ExecutionStarted/ExecutionFinished` liegen. Transport und reiner
Evaluator verlangen denselben exakten Einschluss. Die getrennte lokale
Originalmaterialisierungsprobe verletzt die untere Grenze um 0,2609 ms,
obwohl die betreffende Gruppe genau eine positive Raw-Zeile mit vier
Ausführungen und keine Zero-/NULL-/Negative-Zeilen enthält. Das widerlegt
eine Zero-Extremum-Erklärung für diesen konkreten Versuch. Ursache,
QS-Auflösung und zulässige Fehlergrenze bleiben offen.

Dokumentiert sind QS-First/Last als **Ausführungs-Endzeiten**, aktive
Mehrfachzeilen und deren Aggregation nach Plan, ExecutionType und Intervall.
`SYSUTCDATETIME` liefert standardmäßig sieben Nachkommastellen; die
Herstellerbeschreibung unterscheidet Präzision und Genauigkeit und beschreibt
einen Windows-API-Pfad. Die geprüften Quellen garantieren keine identische
Clock, Quantisierung oder Fehlergrenze zwischen beiden Messwegen, insbesondere
keinen 100-ns-Einschluss für unsere Linux-Container. Dies ist eine Grenze der
vorliegenden Quellenlage, kein Beweis unterschiedlicher Clocks.
[QS-Runtime-Statistik](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17),
[SYSUTCDATETIME](https://learn.microsoft.com/en-us/sql/t-sql/functions/sysutcdatetime-transact-sql?view=sql-server-ver17).

Die verlustfreie Tickdarstellung erhält gelieferte Werte; sie erhöht deren
Messgenauigkeit nicht. Auch passende Counts, ein Flush oder nachträgliche
Vorher-/Nachher-SYSUTC-Werte beweisen den geforderten Einschluss nicht.
Die bestehenden v1-Fehler bleiben Fehler. Dieser Entwurf berechtigt weder
zum Merge des fehlgeschlagenen PR68 noch zum Umgehen seiner CI.

## 2. Zwei getrennte Methodenalternativen

| Alternative | Aussage und erforderlicher Nachweis | aktueller Stand |
|---|---|---|
| Exakter zeitlicher Einschluss | Die verwendeten Messwege müssten für die jeweilige Version und Plattform tatsächlich vergleichbar sein. Eine belegte gemeinsame Zeitbasis, Ereignissemantik und Genauigkeits-/Quantisierungsbehandlung muss den behaupteten Einschluss tragen. Eine empirisch beobachtete maximale Abweichung ist keine universelle Garantie. | Kein hinreichender Quellen- oder Runtime-Nachweis; v1 bleibt unverändert. |
| Kontrollierte Kollektivzuordnung | Die QS-Metriken gehören zum vollständig abgegrenzten Kollektiv der vier kontrollierten Suchausführungen je T0/T1. Herkunft folgt aus beobachtetem QS-Scope, vollständiger Bilanz und attestierter Ausführungsdisziplin; exakte QS-Endzeit innerhalb einer SYSUTC-Klammer wird dabei nicht behauptet. | Konkreter Kandidat in Abschnitt 3–6; Entscheidung, Implementierung und Abnahme fehlen. |

Die zweite Alternative wäre eine **andere Beweisart**. Sie darf nicht durch
ein optionales Flag im v1-Decoder oder das bloße Entfernen von G13 entstehen.
Sie weist weder den Plan einer einzelnen Request-ID noch eine bestimmte
Kompilierungsursache nach. `DEC-068` verwendet gewichtete Kollektivmetriken;
deren Separationsregel, Parameterlast und feste Kontrollblöcke bleiben
unverändert. Ob der neue Zuordnungsbeleg ihre Eingabevoraussetzungen ausreichend
erfüllt, muss separat entschieden und validiert werden.

## 3. Wiederverwendbarer Bestand und tatsächliche Lücken

| bestehende Quelle | verwendbarer Bestandteil | fehlender Beleg |
|---|---|---|
| [Setup](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/10_Setup.sql) | synthetische Daten, festes Suchstatement, Requestlog nach dem SELECT | `RequestedUtc` ist `datetime2(0)` und kein präziser Statement-Endzeitbeleg; eine Logzeile allein beweist keine externe Exklusivität. |
| [SQL21](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/21_Controlled_Query_Store_Windows.sql) | tatsächliche Katalogintervalle, vier Requests je Fenster, vollständiger Ergebnisvergleich, gemessene Ergebniszahl, Parent-/Variant-Scope, gewichtete QS-Metriken | Capture erfolgt heute erst nach beiden Fenstern; kein gebundener Vorher-/T0-/T1-Gesamtledger oder attestierter vollständiger Ausführungsumfang. |
| [SQL35](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/35_Control_Evidence.sql) | erneuter Familien-/Live-Abgleich, Counts, Planhashes, Request-Ergebnisbindung und Projektion | getrennte Live-Lesezeit ist kein atomarer Snapshot und liefert keine fehlende T0-Herkunft nachträglich. |
| [Transport](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md) | begrenztes Framing, exakte skalare Darstellung, strenge Schemas und Digests | deklarierte JSON-Felder attestieren keine Ausführung; bestehender Body enthält keinen vollständigen Coordinatorbeleg. |

Wichtig: Die vier vorausgehenden Datenassertionsrequests stehen bereits im
Requestlog, bevor SQL21 Query Store konfiguriert. Sie sind keine in SQL21
ausgeführten QS-Warmuprequests. SQL21 akzeptiert als rekonstruierbaren
Ausgangszustand sowohl OFF als auch READ_WRITE. Ihr QS-Erfassungsstatus ist
daher aus dieser Phasenreihenfolge allein nicht festgelegt. Ein neuer Entwurf
darf weder pauschal zwölf QS-Ausführungen verlangen noch eine fehlende
Warmup-Capture als gemessen ausgeben. Die vier vorhandenen Requests bleiben
unverändert; zusätzliche Suchaufrufe oder eine vorgezogene Aktivierung sind
kein Bestandteil dieses Kandidaten.

## 4. Kandidat: vollständige Bilanz mit attestiertem Ausführungsumfang

Die folgenden Anforderungen sind **vorgeschlagene Voraussetzungen**, noch
keine vorhandenen Records oder freigegebenen SQL-Schritte:

1. **Vorabbindung und Exklusivität:** Der spätere Coordinator prüft vor dem
   ersten mutierenden Schritt integrierte Quellen und Evaluator, kontraktierte
   Parameter, Zielidentität, Eigentum, Ressourcen und Budgets. Er führt nur die
   gebundenen Phasen aus, höchstens eine aktive SQL-Session und ausschließlich
   die vier vorangehenden sowie acht Fensterrequests. Separate Katalogpulses
   rufen die Suchprozedur nicht auf. Zusätzliche Clients, andere Calls,
   State-/Scopeänderungen oder nicht attestierbare Ausführungsdisziplin
   verhindern einen positiven Herkunftsbeleg. Ein JSON-Boolean oder passender
   Hash ersetzt diesen vertrauenswürdigen Ausführungsnachweis nicht.
2. **Erfassungsbeginn und Basis:** Nach positiver Zustandsprüfung wird der
   Beginn der kontrollierten QS-Erfassung gebunden. Tatsächlich vorhandene
   frühere Familien-Counts werden materialisiert und als Basis `B` bewahrt;
   fehlende Vorab-Erfassung bleibt unbekannt. Eine beobachtete Nullbasis
   nach den vier Vorabrequests schließt verzögert sichtbare Statistik nicht
   aus. Eine tatsächlich leere Basis benötigt zusätzliche nachvollziehbare
   QS-Zustandsbelege während dieser Requests. Bei bereits erfassten
   Vorabrequests braucht `B` einen vollständigen Abschluss-/Ausschlussnachweis.
   Welche konkrete QS-Zustands- und Abschlussregel `B` zuverlässig trägt,
   bleibt offen. Kein implizites OFF, CLEAR, pauschales Abziehen von vier oder
   nachträgliche Baselineanpassung. QS-Basiscounts attestieren auch kein
   individuelles Warmup-Profil.
3. **QS-eigene Intervallzuordnung:** T0 und T1 bekommen unterschiedliche,
   tatsächlich beobachtete QS-Intervall-IDs und widerspruchsfreie
   Kataloggrenzen. Aktivierungs-/Rotationsnachweis muss innerhalb der
   QS-Evidenz begründet werden, etwa durch einen gesondert gebundenen
   Katalogpulse; diese konkrete Methode ist noch zu prüfen. Ein berechneter
   Sleep oder SYSUTC-Vergleich allein ist kein solcher Beleg. Keine
   Nachbarintervall-Auswahl anhand eines nachträglich günstigeren Metrikwerts.
4. **Sequenzieller Capture:** Vor T0 werden die vollständige Basis `B` und
   die leere Familienbasis im gewählten neuen T0-Intervall geprüft.
   Die vier Calls werden in unveränderter A-/B-Reihenfolge mit tatsächlichen
   Request-IDs, Ergebnissen und Abschluss erfasst. T0 muss erfolgreich
   materialisiert und geprüft sein, bevor T1 ausgeführt wird. T1 erhält
   denselben Vorher-/Nachher-Beleg; kein gemeinsamer später Snapshot als
   Ersatz der fehlenden T0-Stufe. Polls unterstützen begrenzt die Sichtbarkeit,
   liefern aber keine atomare Historie oder Erlaubnis zur Lastwiederholung.
5. **Vollständiger Familienledger:** Ein Capture umfasst die endgültig
   aufgelösten Parent-Queries und alle zugehörigen Variants, einschließlich
   später sichtbarer Familienmitglieder. Für diese Familie werden alle
   vorhandenen Intervall-IDs und ExecutionTypes berücksichtigt; keine
   Beschränkung allein auf die zwei passenden Gruppen. Die reguläre Bilanz
   muss genau `B → B+4 → B+8` ergeben. Je Stage gehören die vier neuen
   Ausführungen genau einem der unterschiedlichen T0-/T1-Intervalle an;
   keine zusätzlichen positiven oder abgebrochenen Suchausführungen.
   Basisgruppen dürfen nicht nachträglich wachsen, verschwinden oder
   rückläufig werden. `4+4=8` ist nur das Delta auf einer belegten Basis;
   eine absolute Acht- oder Zwölfersumme gilt nicht pauschal für historische
   v1-Läufe. Eine fehlende Query-/Variant-Bindung, andere Intervallzuordnung
   oder ein Scopewechsel ist ein Defekt.
6. **Materialisierung und Stabilität:** Counts, gewichtete Metriken, Extrema,
   Familien-/Planbindung und verwendete Basis müssen aus derselben begrenzten
   Capturegeneration stammen. Aktive Disk-/Memory-Rows werden gruppiert;
   rohe `runtime_stats_id` sind dort kein stabiler Gruppenschlüssel.
   Eine SQL-Materialisierung wird nicht als transaktionaler Snapshot bezeichnet.
   Nach T1 bestätigt ein zusätzlicher gebundener Gesamtvergleich den
   unveränderten T0-Stand und die vollständige Bilanz. Vorab festgelegte
   Vergleichsstufen, Größenlimits und maximale Polls sind noch auszuarbeiten;
   wiederholt passende Counts allein garantieren keine Vollständigkeit.
7. **Abschluss:** Nur tatsächlich erfolgreiche Phasen, markergebundenes
   Cleanup und die erste unabhängige Datenbankabwesenheit können einen
   erfolgreichen Capture-Beleg liefern. Recovery heilt keinen ersten Fehler.
   Instanzabbau wird separat und unabhängig geprüft. Fehlende Herkunft darf
   nicht durch einen erfolgreichen späteren Cleanup ersetzt werden.

Der zentrale Gegenfall bleibt: Ein geplanter Request fehlt, eine ungeplante
Ausführung derselben Familie ersetzt ihn, die QS-Summe bleibt vier.
Eine reine Count-/Metrikbilanz erkennt diese Kompensation nicht. Nur der
unabhängig vertrauenswürdig gebundene Ausführungsumfang könnte sie ausschließen.
Ohne diesen Beleg muss das Modell die Zuordnung als nicht nachgewiesen
belassen. Auch mit Beleg bleibt die Aussage kollektiv, ohne einzelne
Request→Plan-Zuordnung, geteilte Clock oder historischen Ursachenbeweis.

## 5. Zeit-, Fehler- und Versionsgrenzen

QS-First/Last und SYSUTC-Requestklammer bleiben getrennt und mit ihrer
tatsächlichen Bedeutung erhalten. Ein neuer Record darf `execution_started`
oder `execution_finished` nicht mit QS-Kataloggrenzen füllen. Alle gelieferten
UTC-Ticks bleiben unverändert; kein Abrunden, 1-ms-Puffer oder Einschluss durch
Umetikettierung. Host-Chronologie und Budgets benötigen eine eigene geeignete
Messung; sie werden nicht aus QS-Duration oder einer ungeprüften gemeinsamen
Wallclock abgeleitet.

Vor einer Methodenentscheidung sind **alle drei** derzeitigen Beziehungen
zu behandeln: QS-Endzeiten gegen SYSUTC-Requestklammer (G13), QS-Endzeiten
gegen QS-Kataloggrenzen und SYSUTC-Requestklammer gegen QS-Kataloggrenzen.
Katalogdefinitionen beschreiben die Aggregation; sie garantieren nicht
automatisch Vergleichbarkeit mit dem Requestmessweg. Für den Kandidaten
könnten Katalogprüfungen die QS-Recordkonsistenz sichern, dürfen aber keinen
ungeprüften exakten SYSUTC-Herkunftsbeleg ersetzen.
[QS-Intervalle](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-interval-transact-sql?view=sql-server-ver17).

Dieser Slice ändert keine Statuscodes oder Fehlerklassifikation. Ein späterer
eigenständiger Vertrag muss Pflichtrecord-, Herkunfts-, Zustands-, Ergebnis-,
Timeout- und Cleanupdefekte gemäß
[FWK-012](../../Demos/00_Framework/Contracts/FWK-012_Status_Error_Skip_Contract.md)
von gültiger Evidenz ohne Separation unterscheiden. Ein fehlender Pflichtbeleg
darf nicht pauschal zu `SKIP_EVIDENCE_MISSING` werden. Die bekannten v1- und
PR68-G13-Fehler bleiben `FAIL`; ein zukünftiger alternativer Lauf kann sie
nicht nachträglich umklassifizieren. Die DEC-068-Separation vollständiger
gültiger Records bleibt unverändert.

Zielmatrix bleibt 2019/150, 2022/160 und 2025/170. Variants und PlanTypes
werden versionsgebunden behandelt. Vier CPU, 8 GiB, eine aktive Session,
180 Sekunden regulär und 60 Sekunden Cleanup bleiben die bestehenden
Grenzen. Zusätzliche Capturestufen verändern Beobachtungskosten; ihre
Durchführbarkeit innerhalb dieser Grenzen muss frisch geprüft werden.
Keine heimliche Budgetvergrößerung, keine neue Instanz oder SQL-Runtime in
diesem Dokumentationsschnitt.

## 6. Prüfplan und nächster kleiner Schnitt

Das getrennte [deklarative Voraussetzungenmodell](DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md)
ist inzwischen implementiert und synthetisch geprüft. Es analysiert
Receipt-/Scope-/Bilanz-Konsistenz, startet keine Prozesse und attestiert keine Runtime. Es muss
fehlende vertrauenswürdige Herkunft ausdrücklich von einer gültigen
deklarativen Modellannahme unterscheiden. Mindestens diese Fälle sind
vorab festzuhalten:

| Gegenprobe | erwartete Grenze des Kandidaten |
|---|---|
| Fehlender geplanter Call, zusätzlicher Familiencall, Summe weiterhin vier | Counts allein liefern keinen Zuordnungsbeleg; ohne gebundenen Ausführungsumfang keine positive Modellfolgerung. |
| T0 erst nach T1 erfasst oder fehlender Vorher-Capture | Reihenfolge-/Basisbeleg unvollständig; keine nachträgliche Ergänzung aus finalem Snapshot. |
| Vorabrequests vor expliziter QS-Konfiguration, unbekannte Basis oder verspätete Warmup-Statistik | Keine erfundene Warmup-Capture, implizite Nullbasis oder Zwölfersumme; kein nachträgliches Anpassen von `B`. |
| Nachlaufender Call oder zusätzliche neue positive Gruppe außerhalb der belegten Basis B in anderem Intervall/ExecutionType | Vollständige Bilanz widersprüchlich; kein Filter auf ausschließlich günstige Gruppen. |
| Vier Stageausführungen verteilen sich über zwei Intervalle oder alte Basisgruppe wächst | Einintervall-/Basisvertrag nicht erfüllt, auch wenn die Gesamtsumme passt. |
| Variant erst nach T0 sichtbar, zusätzliche Parent-Query, geänderter Scope | Finale Familienmenge muss auf frühere Captures rückbindbar sein; kein Weglassen unbekannter Zuordnung. |
| Disk-/Memory-Mehrfachzeilen, Zero-Rows, NULL/negative Counts, Overflow | Keine Doppelzählung oder stille Kürzung; Counts und Metriken an dieselbe begrenzte Generation binden. |
| Ungebundener Digest, fremde Lifecycle-/Instanz-ID, nur JSON-Exklusivitätsflag | Deklaration liefert keine Herkunftsattestation. |
| QS-First einen Tick vor SYSUTC-Start bei sonst vollständiger Kollektivbilanz | Keine Clockfolgerung; im v1 unverändert FAIL, im Modell ausdrücklich kein exakter zeitlicher Einschluss. |
| Ein-Tick-/Gleichheitsfälle an Katalog- und Requestgrenzen | Zeitbeziehungen separat modellieren; keine versteckte Rundung oder neue Inklusivität. |
| Timeout, erstes Abwesenheitscheck-FAIL und erfolgreiche Recovery | Kein erfolgreicher Runtimebeleg; ursprünglicher Fehler und Cleanuppriorität erhalten. |

Die getrennte [Quellen-/Ausführungspfadprüfung](DGN_007_PREMISE_SOURCE_REVIEW.md)
präzisiert inzwischen Procedure-Erfassung unter AUTO, Persistenz gegenüber
Publikation und tatsächliche Harnessgrenzen. Die oben genannten nachlaufenden
Statistiken sind bedingte Gegenproben bei unbekannten Voraussetzungen, keine
behauptete dokumentierte Publikationsverzögerung nach erfolgreichem Call.
Basisabschluss, QS-interne Aktivierung und vollständige Herkunft bleiben offen.
Der konkrete [Beobachtungs-/Herkunftsvertrag](DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md)
liegt inzwischen als PROPOSED vor. Der [Suffizienzreview](DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md)
trennt inzwischen bedingte Callerfassung und kollektive Bucketzuordnung vom
stärkeren kontinuierlichen QS-Zustand; das konservative Methodengate wird
nicht aufgehoben. Das getrennte [Gegenmodell](DGN_007_SATURATION_COUNTERMODEL.md)
ist implementiert; das [Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md)
ist vorbereitet, keine Methodenwahl. Der [Offline-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md)
ist statisch implementiert; Prozess-/Manifestdatenkanten und tatsächliche
Importumgebung bleiben Folgearbeit. Tatsächliche Herkunft, Acquisition-/
Floatregel und endliche Bounds bleiben offen. Danach braucht die alternative
Beweisart eine ausdrückliche Entscheidung vor gemeinsam versionierter Umsetzung.
Die spätere versionierte Umsetzung muss SQL21/35,
Quellenfreeze, Body-/Transportformat, Recordmodell, Evaluator, Runner und
Fixtures gemeinsam binden. Die bestehenden v1-Formate dürfen keine optionale
Hintertür erhalten. Konkrete Ledgergrenzen, neue Capturekosten und
Vertrauensquelle des Coordinatorbelegs gehören vor Implementierungsfreigabe
in diesen Folgeschnitt. Ein reines Modell-PASS genügt dafür nicht.

Erst nach den lokalen relevanten Prüfungen und erfolgreicher CI am aktuellen
Head/Base darf eine ausführbare Alternative integriert werden; erst danach
können frische prospektive Bestätigungsläufe folgen. Historische Captures
werden nicht umgewidmet. Der interne API-Schnitt bleibt bis zur G13-
Messvertragsklärung zurückgestellt. Incident-, Ursachen-, Mitigations-,
Capstone-, Teilnehmer- und Szenariofreigabe bleiben offen.

Weitere Primärquellen, geprüft am 2026-10-07:
[QS-Optionen](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-query-store-options-transact-sql?view=sql-server-ver17),
[Query-Variants](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-variant?view=sql-server-ver17),
[sp_query_store_flush_db](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-flush-db-transact-sql?view=sql-server-ver17).
Flush unterstützt die Persistierung vorhandener Daten; er liefert keine
Ausführungsexklusivität oder atomare historische Sicht.
