# Gebundener CON-010-SQLcmd-Clientadapter

`pool_client.py` ist eine Bibliothek in der Quellenvorbereitung. Es gibt keinen
Producer, Provisioner oder CLI-Einstieg und keinen neuen Native-Nachweis. Der
künftige ausdrücklich zugelassene RED-Producer muss den tatsächlich eigenen
Container, die vier vollständigen Frameworkmarker, gehaltene Principal-SIDs und
seine Ergebnis- und Cleanup-Verträge selbst prüfen. Eine deklarierte interne
Callerzulassung oder eine Quellenkarte attestiert diese Tatsachen nicht.

Die interne Callerbindung verlangt die aktuelle vollständige Quellenkarte,
einen eigenen 16-stelligen Hex-Inputtoken, einen SHA-gebundenen vorhandenen
SQLcmd-Endpunkt und den festen SQLAuth-Loopbackserver `tcp:127.0.0.1,<Port>`.
Die Authentifizierung dieses Owneradapters ist ausschließlich `sa`. Arbeitsphasen
binden `SQLPERF_LAB_CON010_POOLPUBLIC`; Preflight, Setup und SQL-Abwesenheit binden
`master`. Der spätere Producer verwendet RunToken `POOLPUBLIC`; das ist vom
Inputverzeichnistoken getrennt. Bestehende LOCAL-/TENANTPOOL-Profile bleiben bestehen.

Jeder geplante Input liegt ausschließlich unter
`Runtime/CON010_POOL_CLIENT_INPUTS/<Token>/phase-<Ordinal>.sql`. Vor Start werden
aktuelle UTF-8-Bytes (höchstens 160000), SHA, Links/Reparsepunkte und feste Phasen
geprüft. UTF-8-BOM, SQLcmd-Metakommandos und freie Variablen sind verboten. Nur die drei
eigenen Tenantsecret-Platzhalter sind zugelassen. Diese Prüfung attestiert keine
serverseitige Ausführung oder Markersemantik des Producertexts.

Vier private Credentials gelangen ausschließlich in eine frische Child-ENV;
SQLCMDINI, fremde SQLCMD-Variablen und Casekollisionen werden nicht übernommen.
Der öffentliche Commandbuilder liest vorhandenes SQLCMDPASSWORD nur als
Voraussetzung; der Adapter verändert die Host-ENV nicht. Vor jedem Input-/Output-
Digest prüft V2 Klartext, UTF-8-/UTF-16-Hex und seinen vollständig gebundenen
Outerframe einschließlich innerer Hexfelder. Bei Credentialtreffern gibt es
keinen Rawreturn oder Digestrecord, nur den festen Fehlerstatus. Der Adapter
persistiert keine Captures, Texte oder Credentials.

Der tatsächliche öffentliche Builder, Starter und Collector halten dasselbe
Prozessobjekt bis zum finalen Poll. Timeout, Signal, inkohärenter Rc/Poll,
Pollausnahme oder fehlende Collectorevidenz setzen UNKNOWN vor allen weiteren
Capturegates; UNKNOWN sperrt jedes Folge-SQL einschließlich Recovery. Ein
bestätigtes Clientende beweist kein serverseitiges Requestende. Normale Rückgaben
geben V2 deshalb `ServerRequestEnd=NOT_CAPTURED` und verlangen zusätzliche
Producersemantik. Der resultierende Text ist vom Collector dekodiert und erneut
UTF-8-kodiert; der Input-SHA bindet die Datei vor SQLcmd-ENV-Expansion.

Die einmalige Normaldeadline liegt höchstens 300 Sekunden voraus; eine explizite
Cleanupdeadline höchstens 60 Sekunden und darf nicht neu gestartet werden.
Jeder Client reserviert die erforderliche eigene Cleanupzeit sowie die aus der
öffentlichen Windows-Collectorquelle belegten 26 konfigurierten Nachlaufsekunden.
Der absolute Phasenendpunkt ist höchstens 40 Sekunden entfernt und bleibt innerhalb
der Gesamtzeit abzüglich Cleanupreserve; ein einziger Zeitsnapshot bindet diese
Grenze. Popenzeit verbraucht dasselbe primäre Collectorfenster. Ist es nach Start
verbraucht, sammelt der vorhandene Collector denselben Handle mit Timeout 0 und
UNKNOWN bleibt sticky. Überschreitet der tatsächliche Rücklauf
diesen Endpunkt, sind alle Folgeclients gesperrt. OS-/Schedulingoverhead ist damit
keine harte Wallclockgarantie. Ein Timeout oder Deadlinefehler erlaubt keine
nachträgliche Budgetverlängerung. Der echte Producer muss den eigenen Abbau mit
den tatsächlichen Restbudgets planen.

Die Quellenkarte enthält nur die drei Adapterquellen und die fünf vorhandenen
V2-/Collectorquellen. Die zwei separat geprüften LF-/CRLF-Collectorvarianten
werden mit ihrem jeweiligen tatsächlichen Rawbyte-SHA erfasst. Provider-,
PortableRuntime-, Pool-/TSK-009-/TP-CON- und vollständige Runtimeabnahme bleiben
`NOT_ESTABLISHED`. Gezielte Tests verwenden ausschließlich synthetische Dateien,
Fakehandles und Mocks der öffentlichen APIs; sie führen keine Prozesse oder SQL aus.
