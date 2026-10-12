# CON-010: öffentlicher reiner Poolrecordvertrag

## Ausgangspunkt und Zweck

[PR222](https://github.com/gecompat/SQL_PerformanceSchulung/pull/222) ist auf
e98822c4cd9ca6568c67d5a108336c31b2b975ee vollständig abgeschlossen: sieben aktuelle
Head-/fünf Main-Gates PASS, vollständiger identischer Tree, main synchron und sauber,
eigener lokaler und Remote-Branch entfernt. Die private Poolkomponente bestand
begrenzt in C3; beide historischen FAILs und ihre SQL-/Pool-Abwesenheitsgrenzen bleiben.

Der nächste kleine TSK-009-Schnitt veröffentlicht eine reine API zur Prüfung
vollständiger typisierter Records samt expliziter Callerbindung und begrenzter
Summary. Kein öffentlicher Provisioner und kein zusätzlicher Poollauf. Die API
führt keine SQL-, Netzwerk-, Container-, Provider- oder Modelloperation aus.
Sie lädt ausschließlich ihren eigenen festen Vertragsfile, nimmt keine frei
wählbaren Datei-/Rawpfade an und importiert keine privaten Runtimequellen.
Anleitung und feste synthetische
Vertragsfixture bleiben getrennt vom tatsächlich vorhandenen privaten C3-Nachweis.

## Wahrheit des Records und Provenienz

Geprüfte Form und interne Kohärenz sind keine unabhängige Attestierung des Producers.
Bool-Flags, Callerbehauptungen oder reproduzierte Input-SHAs ersetzen keine
tatsächlich aufgenommenen Requestenden, Returncodes und Inputbindungen.
Fehlende oder unbestätigte Felder werden nicht als null Fehler oder PASS ergänzt.
Der tatsächliche C3-Nachweis besitzt vollständige Ergebnis-/State-/Rawclosuretexte
und einen Quellen-/Expected-/Parent-/Childnachweis. Er enthält keine individuellen
aufgenommenen SQLcmd-Returncodes, Requestendreceipts und Input-SHAs je Handle.
Diese öffentliche Capturegrenze bleibt NOT_ESTABLISHED und sichtbar im Ergebnis.
Das ändert den abgegrenzten privaten Collector-/Runtimebefund nicht nachträglich.

Der Consumer prüft nur tatsächlich vorliegende typisierte Resultate, volle
Identitäts-/Source-/Vektor-/Reset-/physische Bindungen, Statekontinuität und
vorhandene Closuretexte. ClientGUID-Gleichheit ist kein Reuseoracle. Kein freier
Dateipfad und keine Rawpayload-/GUID-/SID-/Verbindungsstring-/Timestampausgabe.
Die Summary exportiert ausschließlich feste Status-/Grenzwerte und begrenzte Counts.
Synthetische vollständige Formen bleiben PUREFIXTURE_ONLY, keine Runtimequalifikation.

## Endlicher Scope und erforderliche Prüfung

Ein Implementierungsverantwortlicher; Root prüft unabhängig ausschließlich neue
Schema-, Population-, Bool-, Source-, Reset-, Closure- und Privacyrisiken.
Höchstens sechs kohärente Quellenkandidaten, Checkpoint nach drei, harter Stop nach
sechs; kein neuer Modell-/Tokenquotenclaim. Unbekannter Verbrauch bleibt UNKNOWN.
Null neue SQL-/Container-/Modell-/Provider-Metadatenaufrufe. Genau ein Offline-Replay
des unveränderten C3-Nachweises erst nach gebundenem Quellenabschluss; keine
Wiederholung früherer grüner Native-/Auth-/Poolproben.

Alle neuen Code-/Fixturepfade bleiben unter Tests/Static; Anleitung unter
Documentation/HowTo. Änderungen im CON-010-README oder dessen Expectedfolder würden
die vollständige bestehende SQLruntime-Matrix auswählen. Deshalb folgt dieser Link
erst beim anschließenden tatsächlichen öffentlichen Producercut. Keine Workflow-
oder Selectorausnahme; aktuelle Pflichtgates werden anhand tatsächlicher Pfade
abgeleitet und ausgeführt. Dieses Layout begrenzt unnötige Nativewiederholungen.

Quellen-/Resultatreview, betroffene reine Gegenfälle, aktueller Head/Base-/Main-CI,
PRintegration, vollständige Treeübernahme, Synchronisierung und eigener Branchcleanup
sind vor Schnittabschluss erforderlich. Öffentlicher Producer, Captureattestierung,
weitere Provider/Authformen und volle CON-010-/TSK-009-/TP-CON-Abnahme bleiben offen.
Andere Repositories unverändert; allgemeine Entwicklung und DGN-007 bleiben pausiert.

## Enge Befunde vor dem einzigen Offline-Replay

Root erkannte vor Replay den tatsächlichen Parent-Phasenliteral mit `_ONLY`;
Consumer und synthetische Fixture werden auf den historischen Record abgestimmt,
ohne ihn umzuschreiben. Summaryfelder aus dem festen Contractfile benötigen ein
explizites Schema, feste Counts und ausschließlich die erlaubten offenen Claims.
Ein geänderter, neu gebundener Expectedfile darf keine Rawfelder oder Runtime-PASS
in die Summary einschleusen. Callerfelder benötigen tatsächliche Builtintypen,
keine bloße Gleichheit des Typnamens; Nichtdict-Eingaben werden vor `.get` abgewiesen.
Die betroffenen engen Gegenfälle folgen auf diese konkreten neuen Abnahmegrenzen.
Der unabhängige übrige Row-/Pool-/Marker-/State-/Closure-Sourcereview ist geschlossen;
Quellenfreeze und Ergebnisprüfung bleiben vor Replay erforderlich.


## Quellenkandidat 1: Offline-Recordprüfung FAIL

Der erste einzige bis dahin geplante öffentliche Reportaufruf scheiterte bekannt
an einem falsch angenommenen Katalogfeld: Der Contract verlangte `operation` bei
`predicates`, obwohl der tatsächlich eingefrorene C3-Producer dieses Feld nicht
erfasste. Der read-only Abgleich sämtlicher 13 Kataloggruppen zeigt ausschließlich
dieses zusätzliche erwartete Feld; keine weiteren Keydifferenzen. Originalbytes
und C3-Collector-/Poolbefund bleiben unverändert. Der Consumer-FAIL ist erhalten.

Die reine synthetische Fixture hatte dieselbe falsche Annahme. Quellenabschluss
und 13 reine Methoden samt drei optimierten Schutzmethoden bleiben auf ihren
tatsächlichen Scope begrenzt; sie ersetzen keine reale Recordkompatibilität.
Ein erweiterter Fixturelauf hatte zuvor vier Folgefehler durch eine gemeinsam
mutierte synthetische SIDmap. Die Kopie wurde korrigiert; nur betroffene neue
Methoden erneut geprüft. Keine Nativekandidaten durch diese reinen Fehler.

Der Benutzer hat ausdrücklich alle weiteren Freigaben dieser Entwicklungswelle
und mehr als zwei Testzyklen erteilt. Daher wird die selbst gewählte Einmal-Replay-
Planung transparent auf höchstens sechs kohärente geänderte Quellenkandidaten mit
je höchstens einem C3-Reportaufruf erweitert, insgesamt höchstens sechs, CP3/hard6.
C1 bleibt verbraucht; kein Reset. Unveränderte Wiederholung verboten. Null neue
SQL-/Container-/Modell-/Provider-Metadatenaufrufe und die offenen Cloud-/ONNX-/Host-
Grenzen bleiben erhalten. Die Korrektur passt ausschließlich den öffentlichen
erwarteten Captureshape an die tatsächliche historische Aufnahme an; keine
Rekonstruktion fehlender Felder und keine Änderung der Originalakte.


## Quellenkandidat 2: tatsächlicher Record kohärent, Capturegrenzen WARN

Der schmale geänderte Captureshape verzichtet auf das nicht erfasste `operation`.
Original-C3-Record und alle Rawbytes bleiben bytegleich. Neue Caller-/Expectedpins
sind separat gebunden; keine historische Datei und kein FAIL wurde überschrieben.
Ein neuer Gegenfall bestand normal und optimiert: Die tatsächlich erfasste Form
wird akzeptiert; zusätzliches `operation` in beiden vollständigen States unter
neu gebundenen Rawpins wird abgewiesen. Insgesamt 14 neue reine Methoden besitzen
betroffene PASS-Nachweise. Nach Korrektur des gemeinsamen Captureshape bestand
der neue 14-Methoden-Satz einmal vollständig auf den finalen Quellen; dies prüft
geänderte gemeinsame Fixtureinputs. Unveränderte Legacy-/Native-/Auth-/Pooltests
wurden nicht wiederholt. Drei Root-Schutzmethoden bestanden unter python -O;
der neue Captureshape-Gegenfall zusätzlich normal und optimiert.

Root schloss das enge Schema-/Source-/Adapterreview unabhängig. 40 historische
Quellendateien, 17 vollständige Native-Rawdateien, zwei States und alle Closuretexte
sind an tatsächliche Bytes gebunden. Die UTF8-Texte werden ohne CRLF-Normalisierung
inMemory übernommen. Hostbinärdateien bleiben ausschließlich historische SHA-
Referenzen, keine neue Host-/Providerprobe. Der gesamte C3-Payload ist unverändert.

Der zweite und abschließende öffentliche Reportaufruf ergibt Record-Kohärenz PASS,
Gesamtstatus WARN: sechs Checkouts, drei physische Wiederverwendungen/getrennte
Poolkeys, drei zweite Checkoutresets vor Reparatur, zwölf vollständige Identitäts-/
Source-/Vektor-/Kontextrecords, acht Queryquellrows und zwei vollständige States.
Ein physischer Parent-Abwesenheitstext und zwei getrennte SQL-Abwesenheitstexte
sind vollständig gebunden. Deklarierter Parent-/Source-/Expected-/Closureinhalt
wird nicht unabhängig nachattestiert. Zwei fehlende Capturegates bleiben
NOT_ESTABLISHED: individuelle Requestenden und ausgeführte Inputbindungen.

Zwei geänderte Quellenkandidaten/zwei tatsächliche Reportaufrufe, C1-FAIL erhalten,
keine weiteren Aufrufe nach erreichtem Kohärenz-PASS. Null neue Native-SQL-, Container-,
Domänenmodell- und Provider-Metadatenaufrufe. Der frühere begrenzte private Pool-C3-
PASS bleibt separat; historische Pool-C1/C2-SQL-/Pool-Cleanup NOT_ESTABLISHED erhalten.
Die [öffentliche Anleitung](../HowTo/SQL_SERVER_2025_AI_POOL_RECORDS.md) beschreibt
API, statische Vertragsdatei, Callerbindung und offene Provenienz ausdrücklich.

Lokale reine und Recordchecks sind bestanden; aktuelle Head-/Main-Gates, PRintegration,
vollständige Treeübernahme, Synchronisierung und eigener Branchcleanup folgen vor
Schnittabschluss. Kein vollständiger öffentlicher Runtime-/Closure-/CON-010-/TP-CON-
PASS; öffentlicher authentifizierter Producer mit echten Capture-/Admission- und
Recoverygates bleibt der nächste getrennte Umfang. Andere Repositories unverändert.
