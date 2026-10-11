# TSK-006 – angehaltener privater ANN-Prototyp

Stand: 2026-10-11. Basis `3ac552998996500849dcd29c9a855c5dd7063f92`.
Der Benutzer hat das [unveränderte lokale Effektpaket](SQL_SERVER_2025_AI_PREVIEW_DECISION.md)
ausdrücklich freigegeben. Der erste zusammenhängende private IDX-011-Prototyp ist
nach zwei Korrekturwellen FAIL und wird nicht erneut unverändert ausgeführt.
IDX-011/IDX-012 bleiben PROPOSED; kein FWK-Paket wurde registriert.

## Tatsächliche Versuche und Fehler

Drei neue eigene Podmancontainer verwendeten ausschließlich den freigegebenen
vorhandenen Tag 2025-CU9-ubuntu-24.04, Build 17.0.5005.3, Enterprise Developer,
EngineEdition 3/Ubuntu 24.04 und die vollständige lokale Image-ID
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726`.
Der Helper band diese ID vor Create, Containerimage/Owner nach Create und den
eigenen Loopbackport. 4 CPU/6 GB und native SQLCMD mit SQLCMDPASSWORD nur in der
Umgebung blieben erhalten. Eigene DB: SQLPERF_LAB_IDX011_PROBE, vier vollständige
Marker, CL170, SIMPLE, 256/64-MB-Dateilimits. Keine fremde Instanz oder Hostoption
wurde verändert; keine Cloud-, Modell- oder ONNX-Aufrufe wurden ausgeführt.

1. Erstversuch: SQL-Parserfehler 343, unbekannter Objekttyp VECTOR in CREATE.
   Kein Indexbuildnachweis. Welle 1 verschob die feste Index-DDL in dynamisches SQL
   nach dem vorgesehenen Preview-Enable und ergänzte SQL-Recovery.
2. Danach: Fehler 257, implizite sql_variant-Konvertierung nach int unzulässig.
   SQL-Recovery schlug ebenfalls fehl und unterbrach den Container-finally-Ablauf.
   Der konkrete eigene Container wurde anschließend über vollständige ID, Image-ID
   und Ownerlabel verifiziert, gezielt entfernt und seine Abwesenheit geprüft.
3. Welle 2: explizite Metadatenkonvertierung, persistente PreviewState vor eigenem
   GO und Recoveryfehlerfang mit anschließendem Containerabbau. Die zusätzlich
   eingeführte direkte VECTOR→varbinary(max)-Konvertierung scheiterte mit Fehler 529.
   SQL-Recovery blieb FAIL; dessen Originalfehlertext wurde nicht erhalten.
   Der nachfolgende ownergebundene Containerabbau und separate Abwesenheitscheck
   bestanden. Keine dritte Korrektur oder Runtimewiederholung ist erfolgt.

Alle drei eigenen Container sind abwesend. Ein unabhängiger SQL-DB-Abwesenheits-
oder Preview-Restore-PASS wurde in keinem Versuch erreicht. Containerabwesenheit
ersetzt diesen noch offenen Vertragsnachweis nicht. Indexgeneration, Vector Search,
positive Ergebnisrows, Recall, tatsächlicher Plan, Ressourcen oder Performance
sind durch diesen Prototyp nicht qualifiziert. Die vorgesehenen Fixtures und
konstanten Summarytexte sind keine tatsächlich ausgeführte Evidenz.

## Budget, Review und Wiederaufnahme

Ein Owner und höchstens zwei kohärente Korrekturwellen begrenzten den Slice.
Das reguläre SQL-Prozesslimit betrug 300 Sekunden. Die letzte Konfiguration
addierte jedoch 20 Sekunden SQL-Recovery zu höchstens 50 Sekunden Containercleanup
und überschritt damit das genehmigte separate 60-Sekunden-Cleanupbudget. Ein
Budget-/Recovery-PASS wird ausdrücklich nicht behauptet. Keine weitere Änderung
oder Runtime darf durch stilles Zurücksetzen dieses Korrekturbudgets erfolgen.

Der enge unabhängige Quellenreview bestätigte zwei verbleibende P2: das
70-Sekunden-Cleanupbudget und einen unvollständigen Recoveryfehlerfang, bei dem
ein Prozessstartfehler wie OSError den nachfolgenden Containerabbau überspringen
könnte. Letzteres wurde nicht tatsächlich ausgelöst; die drei bekannten Container
sind abwesend. Der Reviewer änderte keine Quelle und führte keine Runtime aus.
Die bekannte Vektorkonversion und der unbekannte Original-Recoveryfehler bleiben
ebenfalls offen. Der bestehende Podmanadapter wurde nicht erneut voll analysiert.

Private Quellen bleiben ignoriert unter Runtime. Modell-/Tokenverbrauch bleibt
unbekannt. Eine neu abgegrenzte Wiederaufnahme benötigt erhaltene Fehlerdiagnostik,
ein garantiert getrenntes höchstens 60-Sekunden-Cleanupbudget, voll gebundene
Preview-Ausgangs-/Restorekontrollen und eine am Build zulässige vollständige
Vektorrepräsentation. Erst anschließend folgen Indexgeneration, tatsächliche
Oracle-/Negativ-/Plan-/Versionskontrollen und vollständige FWK-/TP-PERF-Abnahme.
Das ursprünglich freigegebene Effektpaket wird durch diesen FAIL nicht erweitert.

## Integration des Fehlercheckpoints

[PR 147](https://github.com/gecompat/SQL_PerformanceSchulung/pull/147) integrierte
ausschließlich diesen wahrheitsgemäßen Fehlerstand und die zugehörige Steuerung.
Sieben Headprüfungen auf `4e6fc20bd17be4c9480db143a6b8ce116bddec07` und alle fünf
ausgewählten Main-Workflows auf Squash `73316d6fa0d1c86c528457d4b01a4250fe026e8f`
bestanden. Tree `e2be0ab1b075423595b33ad9bb12b72b6ee7c246`, main-Synchronisierung
und Entfernung des eigenen lokalen/remote Branchs codex/sql2025-ai-ann-preview
sind geprüft. Diese statischen Gates ersetzen keinen fehlgeschlagenen SQL-Nachweis.
Der angehaltene Slice wird durch den aktiven Heartbeat nicht automatisch erneut
gestartet. Unabhängige Lehrmaterialarbeit für bereits qualifizierte Offline-Demos
bleibt im autorisierten Gesamtumfang möglich; Gesamtworkstream ist nicht abgeschlossen.
