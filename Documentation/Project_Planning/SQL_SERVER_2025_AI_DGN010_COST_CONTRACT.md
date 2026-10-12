# DGN-010 – öffentlicher reiner Kostenrecordvertrag

Stand: 2026-10-12. TSK-011/CUR-021; DGN-010 bleibt PROPOSED.
Öffentliche numerische Aufbereitung, kein SQL, Provisioning oder Provideraufruf.

## Abgeschlossene Grundlagen und begrenzter Schnitt

[PR206](https://github.com/gecompat/SQL_PerformanceSchulung/pull/206) ist vollständig
integriert: Head 62fd7b91e642f8377b18ef4a4ae97a91cfd8bda0,
main 5c5c2596f54db93b33229fe3c99bf98881500a4b, sieben Head-/fünf Main-Workflows
PASS, ganzer Tree gleich, FF-main sauber, eigener lokaler/Remote-Branch entfernt.
Die [Build-/Dropfenster](SQL_SERVER_2025_AI_DGN010_BUILD_COST_REVIEW.md) und
[Indexseiten](SQL_SERVER_2025_AI_DGN010_INDEX_PAGES_REVIEW.md) stammen aus zwei
bereits vollständig geschlossenen eigenen Nativeprofilen. Ihre Quellen bleiben
unverändert; historische FAILs anderer Schnitte bleiben erhalten.

Dieser Schnitt hat einen Implementierungsverantwortlichen und einen unabhängigen
Review ausschließlich der neuen Schema-/Kontinuitäts-/Aggregationsrisiken.
Sechs kohärente Quellenkandidaten, Checkpoint3/hard6; keine neuen SQLcalls oder
Container. Drei P2 des ersten Quellenreviews wurden im engen Delta geschlossen:
volle datetime2(7)-Ordnung, konkrete nullable Typen und volle Statekontinuität.
Kein weiterer Review derselben qualifizierten Nativequellen. Modell-/Tokenverbrauch
ist unbekannt. Gewöhnliche Korrekturfreigaben sind bereits erteilt.

## API und feste Eingabebindung

[dgn010_cost_evidence.py](../../Tests/Static/dgn010_cost_evidence.py) stellt
`decode(native_text)` und `report(record, expected_database_id=attested_id)` bereit.
Der Caller muss die DB-ID unabhängig aus dem tatsächlichen Nativekontext attestieren.
Der feste Record verlangt exakt zwei eigene CREATE-/DROP-Zyklen in dieser Reihenfolge,
acht vollständige Source-/Indexaufnahmen, vier unabhängige Before-/After-Statepaare
und zwei volle Zustände der abgewiesenen DROP-Gegenprobe.

Der Metadatenvertrag gilt für die bereits gebundene SQL17.0.5005.3/Developer/CL170-
Form: 41 Konfigurationen, zwei Dateien, eigene lab-Schema-/Source-/PK-/Readerstruktur,
vier vollständige Eigentumsmarker und 1000 synthetische Rows (Id1–1000, Value=Id×3,
100 F-Payloadbytes). Er ist kein generischer Validator anderer Builds oder Labs.
Alle 13 Statebereiche, vollständigen Feldmengen, Populationen und skalaren Typen
werden geprüft. Nullable Felder verlangen ihren konkreten SQL-Ausgabetyp oder NULL;
Bool-/Floataliaswerte gelten nicht als Integer. Markername und -wert werden aus
vollständigen UTF-16-Bytes mit tatsächlichen Längen geprüft. Sourcewerte/-bytes,
Original-PK, Konfiguration, Dateien, Rechte und Reader bleiben gebunden.

Jeder DDL-Record bindet den UTF-16-Digest des festen tatsächlich ausgeführten Texts,
Cycle, DB/Source, vollständige gehaltene Index-/Spalten-Lease und dieselbe fünfteilige
Requestidentität vor/nach dem Fenster. Counter sind tatsächliche monotone int64-
Deltas; fehlende Werte und Zahlenaliasse werden abgewiesen. Vollständige siebenstellige
datumvalidierte UTC-Werte bestimmen Intervall-/Serienordnung. Erst danach erfolgt
die getrennte Mikrosekunden-Differenzberechnung. Eine positive 100ns-Spanne kann
ElapsedUs0 ergeben; ein umgekehrtes Intervall oder überlappende Seriengrenze bleibt FAIL.

Negative-After→erstes Before und jedes After→nächstes Before sind vollständig gleich,
einschließlich SourceRows.modify_date. Nur innerhalb der tatsächlich gebundenen
CREATE-/DROP-Paare sind eigene Index-/Spaltenänderung und monotone Source-modify_date
zulässig. Doppelte JSON-Felder, fremde Transportpräfixe und fehlende/trunkierte Parts
bleiben FAIL. Vorhandene Nativequellen und deren frühere Prüfungen werden nicht verändert.

## Ausgabe und Aussagegrenzen

Je CREATE/DROP werden beide Samples, n2, Min/Max, Nullanzahl und exakter dezimaler
Mediantext für ElapsedUs und die vier Requestcounter erhalten. Große gültige
int64-Samples werden nicht durch Floatmediane gerundet. CPU/I/O umfasst die eigenen
Countergrenzen; UTC begrenzt den EXEC-Bereich. Keine isolierten Worker-, Compile-,
Log-, Commit- oder vollständigen Lifecyclekosten daraus ableiten.

Fünf A/B/A/B/A-Aufnahmen je Profil trennen PK und Candidate, Used und Reserved Pages
sowie die ausgewählte Indexsumme. Ein abwesender Candidate ist `None`, keine
gemessene Null. Katalog-row_count1000 ersetzt nicht die vollständige Sourceprüfung.
Used/Reserved sind die bereits dokumentierten Partitionallokationen; sie belegen
keine ganze DB-/Datei-/RAM-/Loggröße, Shrinkwirkung oder Nettonutzenqualifikation.

Die Ausgabe enthält keine Request-/Connection-/DB-Identitäten, UTCs, Markerbytes,
Sourcepayloads oder Pläne. `record_validation=PASS` bedeutet numerische Konsistenz.
`controller_flags=DECLARED_NOT_INDEPENDENTLY_ATTESTED` und
`provenance=CALLER_ATTESTATION_REQUIRED` verhindern einen Runtimeclaim aus bloßen
Flags. Runtime, TP-PERF, volle Workerkosten, Indexnettonutzen und ganze DB-/Dateigröße
bleiben ausdrücklich NOT_ESTABLISHED. Der öffentliche Producer bleibt WARN.

## Tatsächlich geprüfter Umfang und Verarbeitungsaufwand

[15 synthetische Gegenproben](../../Tests/Static/test_dgn010_cost_evidence.py) PASS,
einschließlich siebter UTC-Stelle, konsistent falschem nullable Typ, State-Rücksprung,
großen exakten Medianen, Nullwerten, fehlenden Populationen und fremden Allokationen.
Der unabhängige enge Quellenabschluss schloss alle drei gemeldeten P2.
Aktuelle Modul-/Test-SHA256:

- C4FB955B241D15BC0782125CFD03DB9219FDC881EFAD01DF5BA9160A4AC60EF0
- 3269E760D01F9E1DB04D5EADD7D3DDAB0C5A331EF3A578C2B92A16122EA57D4D

Beide vorhandenen vollständigen Native-Records wurden mit diesem öffentlichen
Code erneut rein gebunden: acht DDL-Fenster, 16000 Source-Rows und 20000 State-Rows.
Record-SHA256 581deec8829a372b629384027e64a26dd654eb76ca131438de06feb5b04670f8 und
710b5a50ba66216f5b06d18fff1599d44619bc5d0ee401fe1a7bae24620c2181;
Caller-DB jeweils aus dem separat vorhandenen Native-DBID-Frame. Tatsächliche
frühere Negative-/KnownEnd-/Cleanupbelege bleiben unverändert und privat.
Neue SQLcalls0/Container0; keine Wiederholung bereits grüner Nativeprofile.

Der bestehende AI-Workflow erhält nur zwei zusätzliche Modul-/Test-Triggerpfade
und einen reinen statischen Testschritt. Sein Runtimejob und dessen Abhängigkeiten
bleiben unverändert; die tatsächliche Base-/Head-/Main-Auswahl muss False ergeben.
Kein zusätzlicher Native-Matrixlauf für diese reine Änderung. Lokaler geänderter
Datenschutzcheck und einmalige aktuelle Head-/Main-Projektgates bleiben erforderlich;
keine doppelte Vollanalyse oder neue Reviewkette. Logs/Records bleiben unter Runtime.

PR, aktuelle Head-/Main-Gates, Treegleichheit, FF-Synchronisierung und eigenes
Branchcleanup schließen den Schnitt. Anschließend bleibt die öffentliche Integration
dieses Kostenvertrags in den begrenzten Producer als nächster offener Schritt;
volle Runtime-/TP-PERF-/Nettonutzen- und Modulabnahme bleiben offen.
