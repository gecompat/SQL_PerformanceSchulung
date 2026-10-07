# DGN-007 – SQL-Producer der skalaren Capture-Projektion

| Merkmal | Wert |
|---|---|
| Status | implementiert; begrenzter lokaler Runtime-Nachweis vorhanden |
| Umfang | tatsächliche Request-Ergebniszahlen und skalare Projektion vor Cleanup |
| Transport | `DGN007_CAPTURE_FRAME`, Version `1` |
| Methodenbezug | [prospektiver Vertrag](README.md), unveränderte Methodik aus `DEC-068` |
| Abnahmegrenze | Producer und deklarierter Transport; kein vollständiger Coordinator oder Incidentnachweis |

Der Producer erweitert die vorhandene kontrollierte Pipeline. Die drei
AB-/BA-/AA-Manifeste, acht Phasen, vier Parameterpaare je Fenster, Suchprozedur
und regulären 180-/Cleanup-60-Sekunden-Budgets bleiben erhalten. Es gibt keine
zweite Capture-Implementierung. Die neutrale Kontrollprüfung wird um die
Bereitstellung gemessener skalarer Records ergänzt.

## Tatsächliche Ergebniszeilen

[CONTROL_WINDOWS](../Automated/21_Controlled_Query_Store_Windows.sql) speichert
nach der vorhandenen Ergebnis- und RequestLog-Prüfung `COUNT_BIG(*)` aus dem
gerade materialisierten `#Actual` in `lab.RequestResultCapture`. Der Datensatz
bindet WindowId, Ordinal, die tatsächliche RequestLogId und ReturnedRows.
Bekannte Erwartungszahlen dienen ausschließlich der Assertion. Sie werden
nicht als Messquelle übernommen. Die Suchprozedur und `CaseRequestLog`
bleiben unverändert; die zusätzliche Tabelle gehört zur eigenen markierten
Wegwerfdatenbank und wird mit ihr entfernt.

[CONTROL_EVIDENCE](../Automated/35_Control_Evidence.sql) übernimmt genau acht
gebundene Requestzeilen, zwei Fenster, verwendete Queryfamilien samt nötigen
Self-Parent-Ankern, positiv ausgeführte reguläre Pläne und deren exakte Union.
Ein nicht ausgeführter Parent-Anker ist kein aktiver Plan. Die zusätzliche
Zeitprüfung verlangt, dass die Plan-Ausführungszeiten innerhalb der
Request-Ausführungsgrenzen liegen. Fehlende oder widersprüchliche Bindungen
verhindern den erfolgreichen Producer-Ausgang.

## Präzision und Framing

Die fünf gewichteten Fenstermetriken werden direkt in SQL als `CONVERT`-
Style-3-Text ausgegeben. Dies erhält unterscheidbare SQL-`float`-Werte und
erhöht keine bereits begrenzte Mess- oder Aggregationsgenauigkeit.
`datetimeoffset(7)` wird auf UTC normalisiert. Ganzzahlige 100-ns-Ticks werden
aus Tagen ab `0001-01-01` und dem Nanosekundenrest des einzelnen Tages
berechnet. Ein Nanosekunden-Differenzwert über Jahrtausende wird vermieden.
Planhashes bleiben acht Bytes, transportiert als 16 Hexzeichen ohne `0x`.
Plan Type ist auf 2019 ausdrücklich JSON `null`; spätere Katalogspalten
werden nur versionsgebunden über statisches `sys.sp_executesql` abgefragt.

SQL erzeugt neun Bodyfelder: Major, Compatibility, Scope, Parent-Objekt und
die fünf Recordarrays aus dem [Transportvertrag](COLLECTOR_TRANSPORT.md).
Schema und beide Digests kommen erst extern hinzu. Es werden keine freien
Querytexte, Plan XML, Verbindungsinformationen oder Lifecycle-Attestationen
ausgegeben.

Die ASCII-Projektion ist auf 32.000 Zeichen begrenzt. Der Producer emittiert
bei Maximalpayload höchstens 63 `PRINT`-Frames mit jeweils höchstens
512 Payloadzeichen; der Packager hat zusätzlich ein defensives 64-Frame-Limit:

```text
DGN007_CAPTURE_FRAME|1|ordinal|total_frames|total_payload_chars|chunk
```

Die vollständige Message bleibt als `varchar(8000)` unter der dokumentierten
PRINT-Grenze. Eine neue lokale Gegenprobe zeigte dennoch die Kürzung
längerer Nachrichten in der konkreten Übertragungskette; 512-Zeichen-Stücke
werden deshalb separat praktisch geprüft. Die SQL-PRINT-Grenze garantiert
keine gleich große Clientnachricht. Damit wird keine ungeschützte MAX-Resultsetspalte benutzt, die
`sqlcmd` standardmäßig kürzen könnte. Der Frameheader bindet Version,
Reihenfolge, Anzahl und Gesamtlänge. Fehlende, doppelte, zusätzliche,
umgeordnete, unbekannte oder gekürzte Frames sind Fehler.

## Reiner Packager und Quellenrevision

```python
from Tests.Contracts.dgn007_capture_projection import decode_projection

body = decode_projection(frames, expected_contract)
```

`frames` ist ein Tuple der vollständigen Framezeilen. Der reine Packager
ergänzt ausschließlich Schema, `contract_digest` und `source_digest` aus dem
validierten erwarteten Vertrag. Er gibt den unverändert zusammengesetzten
JSON-Text an den bestehenden Decoder weiter. Doppelte JSON-Schlüssel,
unbekannte Felder und numerische Fehler werden nicht durch eine vorgezogene
Normalisierung verdeckt. Ein Producer-Body ohne acht deklarierte `MEASURED`-
Ergebniswerte scheitert mit `FAIL_RESULT_CONTRACT`.

Die Quellenliste im v1-Vertrag bleibt bei genau 14 SQL-/Manifestdateien.
Nur die normalisierten SHA-256-Werte von 21 und 35 werden erneuert. Damit
ändern sich Quellen- und Vertragsdigest; Shape, Methodik und Entscheidung
bleiben gleich. Historische Captures und ihre Nachweise behalten ihren alten
Commit-/Freeze-Bezug und sind keine Bestätigungsläufe dieser Revision.
Die SQL-Datei enthält ihren eigenen Digest nicht, um eine Selbstreferenz
zu vermeiden. Auch ergänzte Digests sind deklarierte Integritätsmetadaten,
keine tatsächliche Herkunfts- oder Vorabfreeze-Attestation. Die spätere
Coordinator-Prüfung muss zusätzlich den ausführenden Collector binden.

## Begrenzte Runtime-Prüfung

Der additive Runner-Modus `--check-capture-projection` ist ausschließlich
für `control-ab`, `control-ba` und `control-aa` vorgesehen. Er übernimmt die
Frames aus `CONTROL_EVIDENCE` im Speicher, prüft den tatsächlichen Body gegen
Major, Scope und vollständige Ergebniszeilen und erhält die unabhängige
Datenbankabwesenheitsprüfung. Rohoutput oder Secrets werden weder als
Testreport ausgegeben noch persistiert. Cleanupfehler und Timeouts behalten
ihre Priorität. Diese Prüfung erzeugt keine vollständigen `RunRecord`s und
ruft keine Incident-Separationsbewertung auf.

Die zusätzliche Option `--check-phase-diagnostics` verwendet dieselbe private,
begrenzte Pipe für alle sechs bekannten Scopes, ohne Capture-Abnahme oder
weitere SQL-Ausführung. Die bestehende CI aktiviert sie für Datenmodell,
Fenster und Profilvergleich. Beide Optionen zusammen erlauben Capture
weiterhin ausschließlich für die drei Kontrollscopes. Erfolgreiche öffentliche
Ausgabe, SQL-Prädikate, Budgets und Fehlerprioritäten bleiben unverändert.
Auch der normale Nichtproducer-Pfad bewahrt bei Fehlern das tatsächliche
Child-Ergebnis für dieselbe begrenzte Metadatendiagnose.

Im Fehlerfall ergänzt der Modus nach der unabhängigen Cleanup-Prüfung
ausschließlich bekannte Phasenstatus und begrenzte numerische SQL-Fehlerdetails.
Zusätzlich kann er eine der 17 konstanten Guardkennungen aus SQL35 ausgeben:
`DGN007_FAILURE|SQL_GUARD|CONTROL_EVIDENCE|G13`. Dazu müssen der tatsächliche
stderr-Kanal, die fehlgeschlagene Evidenzphase und die unmittelbar folgende
`FAIL_RESULT_CONTRACT`-Summary übereinstimmen. Unbekannte, doppelte oder
verschobene Kennungen werden nicht veröffentlicht. Die Kennungen gehören
zu den folgenden unverändert bestehenden Prüfabschnitten:

| Kennung | Prüfabschnitt |
|---|---|
| G01 | Kontrollkonfiguration |
| G02 | Fenster und Katalogintervalle |
| G03 | Requestmenge und Parametermix |
| G04 | tatsächliche Requestfolge |
| G05 | gespeicherte Profile, Scope, Counts und Metriken |
| G06 | Forced Plans |
| G07 | Live-Katalogmetriken |
| G08 | Live-Abgleich von IDs, Counts und Zeiten |
| G09 | aktive Planhashes |
| G10 | aktive PlanTypes |
| G11 | aktive Ausführungsanzahl |
| G12 | tatsächliche Request-Ergebnisbindung |
| G13 | Query-Store-Endzeiten innerhalb der Ausführungsgrenzen |
| G14 | gewichtete Totals und Recordanzahl |
| G15 | UTC-Tickdarstellung |
| G16 | projizierte Planbindung und PlanType |
| G17 | JSON-, ASCII- und Größenvertrag |

Er veröffentlicht keinen Rohfehlertext. Diese Diagnose ändert weder Outcome
noch Fehlerpriorität, Budget oder Wiederholungsverhalten.

Der begrenzte G13-Grenzabstandsbericht liest ausschließlich die bereits
gespeicherten verletzten `lab.IncidentProfile`-/`lab.IncidentState`-Gruppen,
erst nachdem das unveränderte G13-Prädikat verletzt ist. `TOP(9)` erkennt
einen Überlauf; höchstens acht Gruppen werden vollständig berichtet. Die
Counts bleiben positiv und auf höchstens vier je Fenster begrenzt. Es gibt
keine zusätzliche Query-Store-Sicht, Suchausführung, Flush oder Wartephase.
Ein eindeutiger, exakt gehashter Reporterabschnitt ist die einzige
SQL-Erweiterung. Sein Entfernen muss den gesamten bisherigen SQL35-Text
mit identischem normalisierten SHA-256 ergeben; freie PRINT-Normalisierung
ist unzulässig.

Die ASCII-Records sind einschließlich Prefix auf 512 Zeichen begrenzt:

```text
DGN007_G13_BOUNDARY|1|BEGIN|COMPLETE|group_count
DGN007_G13_BOUNDARY|1|GROUP|ordinal|window|parent|query|plan|interval|type|count|start|finish|first|last|first_minus_start|last_minus_finish
DGN007_G13_BOUNDARY|1|END|group_count
```

`OVERFLOW|9` bezeichnet mindestens neun beobachtete Gruppen und liefert
keine partiellen Gruppen; `INSUFFICIENT|0` bezeichnet nicht bereitstellbare
Skalarwerte. Beide schließen mit `END|0`. Die Ausgabe der Diagnose erfolgt
im Runner erst nach seiner unabhängigen Cleanup-Prüfung. Der Parser verlangt
einen unveränderten bekannten Kontrollvertrag, die eindeutige tatsächlich
fehlgeschlagene `CONTROL_EVIDENCE`-Phase und ihren tatsächlichen stderr-Kanal.
BEGIN, geordnete vollständige Gruppen und END müssen lückenlos vor genau
einem G13 mit unmittelbar folgender `FAIL_RESULT_CONTRACT`-Summary stehen.
Keys, Counts, Zeitdomäne und exakte vorzeichenbehaftete Subtraktionen werden
erneut geprüft. Der gesamte Report wird atomar innerhalb der bestehenden
24-Zeilen-Diagnosegrenze reserviert. Strukturierte Status- und Guardfelder
haben Vorrang; optionale SQL-Msg-Zahlen erhalten nur verbleibende Plätze.
Ein ungültiger Report liefert nur eine feste
`INSUFFICIENT|MALFORMED`-Kennung; bei fehlender Failure-/Kanalbindung wird
kein Grenzabstandsbericht veröffentlicht. Fehlende oder unvollständige
Diagnose unterdrückt niemals den ursprünglichen Fehler, Timeout oder Cleanup.

Die Ticks bewahren die Darstellung ab `0001-01-01` mit sieben Nachkommastellen
nach UTC-Normalisierung. Dokumentiert sind die QS-Zeitfelder als
Ausführungs-Endzeiten; eine gemeinsame Clock oder identische tatsächliche
Messauflösung mit `SYSUTCDATETIME` und die Zeitsemantik bei Nullzählzeilen
sind in den geprüften Primärquellen nicht zugesagt. Der gespeicherte Bericht
behauptet weder einen neuen QS-Snapshot noch eine Ursache, Toleranz oder
Fehlerbehebung. Er enthält keine Querytexte, Plan-XML oder Metriken.
Quellen, geprüft am 2026-10-07:
[QS-Zeitfelder](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17),
[SYSUTCDATETIME](https://learn.microsoft.com/en-us/sql/t-sql/functions/sysutcdatetime-transact-sql?view=sql-server-ver17),
[SWITCHOFFSET](https://learn.microsoft.com/en-us/sql/t-sql/functions/switchoffset-transact-sql?view=sql-server-ver17).
Die neue Reporterrevision bestand acht tatsächliche temporäre SQL-Branchfixtures
auf einer neuen eigenen 2022-Developerinstanz `16.0.4295.3`, einschließlich
Ein-Tick-Verletzungen, gleicher Requestgrenzen, UTC-Offset, acht Gruppen und
Overflow bei neun. Freeze und eigener Cleanup sind getrennt gebunden im
[Runtime-Nachweis](../../../../Documentation/Project_Planning/DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md).
Die reguläre CI am exakten neuen Head/Base bleibt vor Integration erforderlich;
der Vorcheck ersetzt keine Lifecycle-/Versionsmatrix oder G13-Ursachenklärung.

Die ursprüngliche lokale Producerprüfung bestand am 2026-10-07 auf 2019/150, 2022/160 und
2025/170: je zweimal AB/BA/AA auf frisch erzeugten, ausdrücklich bestätigten
eigenen Developer-Wegwerfinstanzen, insgesamt 18 vollständige Lifecycles mit
tatsächlichem Decoder, unabhängiger Datenbankabwesenheit und überprüftem
Containerabbau. Alle drei eigenen CIDs und exakten Namen sind unabhängig
abwesend bestätigt. Der [Runtime-Nachweis](../../../../Documentation/Project_Planning/DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md)
bindet konkrete Versionen, Images und Quellendigest und trennt frühere
Fehlversuche von der erfolgreichen ursprünglichen Matrix. Die spätere
Guarddiagnostikrevision ist separat gebunden. Die ursprüngliche Actions-
Prüfung scheiterte auf SQL Server 2025 in BA-RUN1; lokale private Gegenproben
reproduzierten diesen Fehler nicht. Seine Ursache bleibt offen. Das sind
begrenzte Entwicklungsnachweise; erfolgreiche GitHub-Actions-Evidenz zum
aktuellen Head und Base bleibt vor Integration erforderlich.

## Statische und synthetische Prüfung

```powershell
python Tests/Static/validate_dgn007_capture_projection.py
python Tests/Static/test_dgn007_capture_projection.py
```

Die aktuelle Suite enthält 37 Testmethoden mit parametrisierten Gegenproben für
alle drei Major Versions und Kontrollscopes, echte Decoderanbindung,
Framegrenzen, Queryfamilien, Requestbindungen, SQL-Ausdrucksfixtures und
begrenzte Prozess-/Fehlerausgabe. Unter Windows bestanden 36; die
Linux-spezifische Exit-vor-EOF-Gegenprobe ist dort ausdrücklich SKIP und
wird im Linux-CI ausgeführt. Zusammen mit den bestehenden DGN-007-Suites
wurden vor der Reporterrevision 156 Testmethoden ausgeführt: 155 PASS und dieser eine SKIP.
Die sieben zusätzlichen Reporter-Testmethoden prüfen beide verletzten Grenzen,
einzelne Ticks, acht Gruppen, Kanal-/Failurebindung, fehlende oder doppelte
Records, Überlauf, exaktes Entfernen des SQL-Abschnitts und unveränderte
Cleanup-/Timeoutprioritäten sowie vollständige atomare Reports bei vielen
optionalen SQL-Messages. Unter Windows bestanden die aktuellen
37 Producer-/Reporter-Methoden mit dem bereits genannten Linux-SKIP.
Die SQL-Ausdrucksfixtures sind modellbasierte Prüfungen; die gesonderten
T-SQL-Proben und Kontrolllifecycles bleiben erforderlich. Der Validator
prüft die additive SQL-Erweiterung, reine Packagergrenze und CI-Anbindung;
er attestiert keine SQL-Runtime oder Incidentfreigabe.

Technische Primärquellen, geprüft am 2026-10-07:
[CONVERT](https://learn.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-ver17),
[DATEDIFF_BIG](https://learn.microsoft.com/en-us/sql/t-sql/functions/datediff-big-transact-sql?view=sql-server-ver17),
[PRINT](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/print-transact-sql?view=sql-server-ver17),
[sqlcmd](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver17).
Die Herstellerdokumentation belegt die Darstellungsgrenzen; sie bestätigt
keinen ausgeführten Projektlauf. Ressourcen-, Reihenfolge-, Freeze- und
Lifecycleattestation sowie Incident-, Ursachen-, Mitigations-, Capstone- und
Szenariofreigabe bleiben offen.
