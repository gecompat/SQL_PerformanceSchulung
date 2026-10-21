# CON-010: Poolrecords ohne neue SQL-Ausführung lesen

Der [reine Poolrecordconsumer](../../Tests/Static/con010_pool_evidence.py) prüft
vollständige deklarierte InMemory-Records des begrenzten lokalen Tenantpoolprofils.
Er öffnet keine Verbindung, provisioniert nichts und importiert keine privaten
Runtimequellen. [Fester Expectedvertrag](../../Tests/Static/Fixtures/con010/pool-record-contract.json)
und [synthetische Gegenfälle](../../Tests/Static/test_con010_pool_evidence.py)
gehören zum statischen Schnitt. Die öffentliche CON-010-Demo bleibt eine
WITHOUT-LOGIN-/EXECUTE-AS-Demo; dieser Vertrag erweitert deren Runtimeabnahme nicht.

## Zweck, Beobachtung und Grenze

Das Profil enthält sechs Checkouts in A/B/U/A/B/U-Reihenfolge. A und B lesen jeweils
ihre vollständige synthetische Quelle samt VECTOR(3); der authentifizierte Unmapped-
Benutzer U liest keine Row. Je Checkout liegen vollständige Before-/After-Identitäten,
Quellen, Vektoren und Kontextwerte vor. Acht positive Quellrows und zwölf Ergebnisrecords
werden geprüft. Drei getrennte Poolkeys und Serververbindungen sowie wiederholte
connection_id/connect_time innerhalb jeder Lane sind der physische Kohärenzbeleg.
ClientConnectionId bleibt erfasste Clientmetadaten; gleiche oder verschiedene
Client-GUIDs gelten nicht als eigenständiger Wiederverwendungsbeweis.

Der zweite Checkout jeder Lane muss NULL vor einer eigenen Kontextreparatur zeigen.
Ein nachträgliches Zurücksetzen ersetzt diese drei Resetbeobachtungen nicht.
Manipulierte Kontextwerte ändern die Tenantquelle nicht. Zwei vollständige States
binden alle Quellen-/VECTOR-/RLS-/Principal-/Rechte-/Config-/Katalog-/Markerfelder
und müssen einschließlich Metadaten unverändert bleiben. Vier Marker sind bytegenau
an das feste TENANTPOOL-Profil gebunden. Der feste Profilshape gilt für den erfassten
Build17.0.5005.3, nicht allgemein für andere Versionen, Provider oder Authformen.

## Feste InMemory-API

Ein bereits autorisierter Caller übergibt `report(record, binding=binding)`.
Es gibt keine freien Dateipfad-, Server-, SQLtext- oder Ausführungsargumente.
Die einzige feste Dateiquelle ist der eigene versionierte Expectedvertrag.

`binding` enthält typisierte DatabaseId/ObjectId, Runnonce, drei verschiedene volle
16-Byte-SIDs, die vollständige feste Quellenpopulation, SHA256-Pins aller Rawartefakte
und der vollständigen geordneten Native-Rawpopulation sowie den tatsächlichen
Expectedvertrag-SHA. Diese Werte müssen vor dem Konsum feststehen. Ein Caller,
der Eingaben und Pins gemeinsam erfindet, wird dadurch nicht unabhängig attestiert.

`record` enthält die vollständige Quellenkarte und acht vollständig erhaltene
Rawartefakte: Build, Poolreceipt, Parentresult, zwei States, frische physische
Parentabwesenheit und zwei getrennte frische SQL-Abwesenheitstexte. Die Native-
Rawpopulation wird geordnet und ohne Weglassen an Caller-Pins gebunden.
Vollständige UTF16LE-Hexframes werden mit Ordinals-, Längen- und Summarybindung
zurückgelesen. Rohdaten bleiben beim autorisierten privaten Caller; weder Logs noch
Receipts, Pfade, GUIDs, SIDs, Verbindungsstrings, Zeitstrings oder Payloads werden
öffentlich exportiert oder in dieses Repository kopiert.

Zwei Felder sind zwingend vorhanden und dürfen bei fehlendem echten Nachweis nur
explizit NULL sein: `capture_ends` und `input_sha256`. Tatsächliche Einzelhandle-
Returncodes/Requestendreceipts und ausgeführte Inputdigests dürfen nicht aus
Quellcode, einem Boolflag oder einem erhaltenen positiven Summarytext rekonstruiert
und als erfasste Fakten ausgegeben werden. Falls vollständige deklarierte Captures
vorliegen, bindet der Consumer deren Ordinals/Arten/Rawhashes/Inputpins strikt;
auch das ersetzt keine unabhängige Producer- oder Callerattestierung.

## Ergebnis richtig lesen

Ein kohärenter positiver Record ergibt `record_validation=PASS` und Gesamtstatus
`WARN`. Die Ausgabe enthält ausschließlich feste Statuswerte und begrenzte Counts.
Fehlen Einzelhandle- oder Inputcaptures, bleiben die entsprechenden Gates explizit
`NOT_ESTABLISHED`; ihre Anzahl wird separat ausgewiesen. Fehlende Rawclosuretexte,
leere positive Quellen, UNKNOWN, false-/Boolalias-Closurefelder, unvollständige
Populationen oder abweichende Source-/Expectedpins ergeben einen Fehler und werden
nicht zu Null/PASS ergänzt.

`caller_provenance=NOT_INDEPENDENTLY_ATTESTED`, vollständige öffentliche Closure,
Runtimequalifikation, öffentliche CON-010-/TP-CON-Abnahme und portabler Providersupport
bleiben offen. Ein synthetischer Fixture-PASS ist ausschließlich eine reine
Validatorkontrolle. Historische private C1-/C2-FAILs bleiben erhalten; deren
SQL-/Pool-Cleanup NOT_ESTABLISHED wird nicht nachträglich geändert. Der private
C3-PASS und die Grenze des aktuellen Consumers stehen im
[Poolnachweis](../Project_Planning/SQL_SERVER_2025_AI_TENANT_POOL_REVIEW.md).

Für diesen statischen Schnitt werden keine Modelle, Dienste, Container oder SQL
aufgerufen. Ein einmaliger Konsum vorhandener unveränderter C3-Belege erfolgt erst
nach dem engen Quellenreview. Ein öffentlicher authentifizierter Poolproducer mit
RED-isolated-Login-DDL (Data Definition Language; Anweisungen zum Definieren und Ändern von Datenbankobjekten), tatsächlichen Capture-/Admission-/Recoverygates ist ein
separater Folgeumfang. Keine TLS-/Passwort-/Seitenkanal-/Performance- oder allgemeine
TSK-009-Abnahme folgt aus diesen Zahlen.
