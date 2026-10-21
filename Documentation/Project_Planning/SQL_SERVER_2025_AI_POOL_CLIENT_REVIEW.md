# CON-010: öffentlicher SQLcmd-Clientadapter

## Ausgangspunkt und endlicher Schnitt

[PR224](https://github.com/gecompat/SQL_PerformanceSchulung/pull/224) ist vollständig
integriert: Main 04e4f08a8dfc9b5121a112c1083a1622f9057ecc, acht aktuelle Head- und
sechs Main-Gates PASS, voller identischer Tree, FF-Synchronisierung, sauberer Main
und eigener lokaler/Remote-Branch entfernt. V2-Capturevorstufe SOURCE_ONLY/WARN;
öffentlicher authentifizierter Producer und Runtimeabnahme bleiben offen.

Der nächste zusammenhängende Schnitt stellt einen öffentlichen Bibliotheksadapter
bereit, der vorhandene Framework-APIs zur Commandbildung, Prozessstart und
Collection verwendet und Captures direkt an dasselbe gehaltene Prozessobjekt
bindet. Kein vollständiger Controller, Containerprovisioner oder allgemein
verwendbarer CLI-Runner. Keine privaten Runtimeimporte oder Frameworkänderungen.
V1, private C3-Nachweise und Capturevorstufe werden nicht erneut ausgeführt.

Neue konkrete Sourceevidenz: Der bestehende Collector liegt lokal als CRLF mit
SHA256 d8b553419bb34e4bafe7d0a7baee55ca28a5b97d1ad64710e131674aa6ca9757 vor,
sein unveränderter Git-LF-Blob hat SHA256
ef33fbeb4436044ac2fd490b90b0608e4743f0f8accbbd3e3a2ee762fc2ac09d.
Der V2-Helper wird für genau diese beiden unabhängig bytegeprüften Varianten
erweitert. Captures behalten den tatsächlichen jeweiligen Rawsource-SHA;
keine stillschweigende Normalisierung, keine allgemeine Providerportabilität.
Nur betroffene Capture-/Sourcegegenfälle zusätzlich prüfen; der historische
Windows-SOURCE_ONLY-Abschluss von PR224 bleibt erhalten.

Heute SOURCE_ONLY: ein Owner, unabhängiger enger Rootreview für echte Handlebindung,
UNKNOWN, Privacy und Deadlines. Sechs relevante Quellenkandidaten, Checkpoint3,
hard6; null lokale echte Prozessstarts/-polls, SQL-, CLR-, Container-, Modell- oder
Provider-Metadatenaufrufe. Neue Tests verwenden Fakehandles am tatsächlichen
Adapter und gemockte öffentliche Collector-APIs. Alte unveränderte grüne Tests
werden nicht wiederholt. Modell-/Reasoningtokenverbrauch UNKNOWN.

## Verbindliche Clientgrenzen

Vor einem später tatsächlich gestarteten Client: vollständige aktuelle öffentliche
Sourcekarte, feste eigene private UTF8-Eingabe, vier private Credentials,
ENV-only SQLAuth ohne -P, explizite Callerzulassung und eigene Loopbackzielbindung.
Die Bibliothek erzeugt keine RED-/Lab-/CID-/Marker-/Semantikadmission. Der spätere
Producer muss vor Wirkungen die vollständig eigene isolierte Container-/Principal-
und Datenbankbindung prüfen; bestehende Instanzen und Hoständerungen bleiben außen.

PID (Process Identifier; Prozesskennung), finaler Pollstatus und tatsächliches Collectorresultat stammen von demselben
gehaltenen Prozessobjekt. Fehlende Collectorevidenz, Timeout, Signal oder unklarer
Poll erzeugen sticky UNKNOWN und sperren Folge-SQL. Rücklauf prüft erneut dieselbe
Deadline, ohne Reset. Privacy erfolgt vor Persistierung und Digests; Fehler dürfen
keine Credentialwerte, Rawargumente oder Secret-/Passworthashes exportieren.

26s konfigurierte Windows-Nachlaufcaps plus erforderliche positive eigene
Cleanupreserve bleiben innerhalb der bereits laufenden Gesamt-/Phasendeadline.
Keine Wallclockgarantie. InputSHA bindet ursprüngliche Datei vor ENV-Expansion,
OutputSHA den zurückgegebenen dekodierten Collectortext; keine Serverattestierung.
Prozessende ist kein TDS-Requestende; Ergebnisse bleiben WARN/NOT_ESTABLISHED.

## Integration und Folge

Betroffene Source-/Privacy-/Kontrollfolgentests und aktueller unabhängiger
Quellenabschluss vor PR. Tatsächliche Pfade bestimmen Head-/Main-Gates einschließlich
betroffener bestehender Runtime-CI (Continuous Integration; automatisierte Integrationsprüfungen); kein Selector-Ausnahmeeintrag und kein RED-Profil
in Default-CI. Integration erst nach aktuellen Pflichtchecks, vollständiger
Treeübernahme, Synchronisierung und eigenem Cleanup.

Danach folgt der begrenzte öffentliche Poolproducer mit drei eigenen Logins,
zwei synthetischen VECTOR(3)-Rows, sechs Checkouts, eigener Scope-/Marker-/Lease-
und Cleanupqualifikation. Lokale Nativeadmission bleibt separater überprüfbarer
Schritt innerhalb der bereits erteilten Benutzerfreigabe; keine neue allgemeine
Entwicklungs-/DGN-007-/Cloud-/ONNX-/Hostfreigabe. TSK-009/TP-CON offen.

## Enger unabhängiger Quellenabschluss

Acht tatsächliche öffentliche Quellen gebunden. Elf neue Adaptermethoden und ein
neuer LF-/CRLF-Vertragsfall PASS; vier betroffene Schutzfälle zusätzlich unter
Python -O PASS. Nach der letzten Quellenkorrektur nur drei betroffene Methoden
geprüft; jetzt 13 Adaptermethoden vorhanden, keine unveränderte Elferrunde erneut.
Root prüft die drei geänderten Eingabe-/Startup-/Uhrfälle und den Variantenfall
unabhängig unter -O: vier Methoden PASS, ohne echte Prozesse/Polls/SQL.

Konkrete Befunde geschlossen: UNKNOWN vor Privacy-/Capturefehlern; absoluter
Phasenendpunkt statt Clockdrift; Startupzeit reduziert denselben primären Wait
(synthetisch 14→7s); verbrauchtes Fenster sammelt denselben Handle mit Timeout0
und sticky UNKNOWN. Korrekt SHA-gebundene Metakommandos, unerlaubte Variablen,
Credentialinputs und BOM-Präfixe werden vor Start abgewiesen. Der feste eigene
Inputvertrag ist UTF8 ohne BOM; das ist keine native SQLcmd-BOM-Qualifikation.
Der feste V2-Vertrag und der Code erlauben genau die zwei tatsächlich geprüften
Collectorbytevarianten und behalten jeweils den tatsächlichen SHA.

Keine Captures/Secrets persistiert und keine neue Allgemein-Receiptinfrastruktur.
Interne Callerbindung bleibt deklariert, keine unabhängige RED-/CIDattestierung.
Sourceprüfung PASS, öffentlicher Producer/Runtime/TP-CON NOT_ESTABLISHED.
Aktuelle pfadbetroffene Head-/Main-Gates und vollständiger Integrationsabschluss
folgen. Bestehende GREEN-Runtime-CI ersetzt keine neue RED-Profilequalifikation.

Privacy-Floor vor PR zunächst FAIL: synthetische IP im Negativtarget wurde vom
unveränderten Scanner beanstandet. Durch eindeutig unzulässiges Texttarget
ersetzt; ausschließlich die betroffene Callerbindungs-Methode erneut PASS.
FAIL-Checkpoint erhalten, keine Scannerausnahme oder zusätzliche Nativeeffekte.
Aktuelle Privacyprüfung aller elf geänderten Pfade gehört zum Abschluss.
