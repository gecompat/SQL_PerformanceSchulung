# CON-010: öffentliche V2-Capturevorstufe

## Ausgangspunkt

[PR223](https://github.com/gecompat/SQL_PerformanceSchulung/pull/223) ist auf
c0e40cf8945cc7e135b871ed26641e223dc29d6d vollständig geschlossen: acht aktuelle
Head-/sechs Main-Gates PASS, voller identischer Tree, main synchron und sauber,
eigener lokaler und Remote-Branch entfernt. V1 prüft den unveränderten privaten
C3-Nachweis kohärent, Gesamtstatus WARN. Historische FAILs und Capturegrenzen bleiben.

V1 und dessen private 42-Quellenpopulation bleiben unverändert. Der nächste kleine
TSK-009-Schnitt definiert einen eigenständigen öffentlichen V2-Capturevertrag mit
kleinen Sourcehelpern und gezielten synthetischen Gegenfällen. Ausschließlich
tatsächlich vorhandene öffentliche Quellen binden; nicht implementierte zukünftige
Producer erhalten keine erfundenen Pins. Vollständiger authentifizierter Producer
und Nativeadmission folgen als eigener nachprüfbarer Umfang.

## Konkrete Evidenz- und Privacygrenzen

Der künftige Producer muss Captures an dasselbe tatsächlich gehaltene Clienthandle
binden: Ordinal/PID (Process Identifier; Prozesskennung), finaler typisierter Returncode, Timeout, Dauer und vollständige
Digests des zurückgegebenen dekodierten Stdout-/Stderr-Texts. Der reine Helper
prüft Callerangaben und ihre Kohärenz, startet oder pollt selbst keinen Prozess
und attestiert weder Handleprovenienz noch ursprüngliche Pipebytes unabhängig.
Prozessende ist kein unabhängiges Server-/TDS-Requestende. Timeout oder unbestätigtes
Ende bleibt UNKNOWN und sperrt Folge-SQL; spätere Prozessabwesenheit stellt keine
rückwirkende SQL-Entwarnung her. Fake-/Sourceonly-Ergebnisse sind keine Runtimeabnahme.

SQLcmd-InputSHA bezeichnet ausschließlich die tatsächliche UTF8-Eingabedatei VOR
ENV-/Sqlcmd-Variablenexpansion, keine Serverausführungsattestierung. Keine erweiterten
Passworttexte, ENVwerte oder Secret-/Passworthashes persistieren. Credentialprüfung
erfolgt vor Digests und Recorderzeugung; Treffer führen zu strukturiertem FAIL ohne
Rawdaten oder Digest. Für unterstützte Transporte vollständige Outerframes und
innere Hexformen prüfen, nicht einzelne Chunks oder eine behauptete Bool-Safety.

Künftige .NET-Open-/Scalar-/Close-Operationen brauchen einzelne tatsächliche
Returned-/Failed-/UNKNOWN-Records; aggregiertes Childende attestiert keine TDS-
Requests. Secretfreie Commandtextdigests sind nur CLIENT_CONFIGURED_TEXT.
Ausgaben bleiben feste Statuswerte und begrenzte Counts, keine Rawpayload-/GUID-/
SID-/Verbindungsstring-/Zeitwerte oder allgemeine Provider-/Runtime-/TP-CON-Claims.

## Producerdesign und endlicher heutiger Scope

Nur vorhandene öffentliche Frameworkcollector-/Marker-/Targetverträge nutzen;
keine privaten Runtimeimports oder CommonAPIänderungen. Kill-/Reaping-Headroom am
tatsächlichen Collectorcode bestimmen und innerhalb derselben Deadline reservieren.

Späterer optionaler RED-Producer: drei eigene Logins, zwei synthetische VECTOR(3)-Rows,
sechs A/B/U/A/B/U-Checkouts; volle vier bytegenaue DBmarker, gehaltene Principal-/
SIDlease, vollständig eigener CID/Image/Owner/NoMounts/Loopback-/4CPU-/6GiB-Namespace,
explizite RED-/Lab-/Scopeadmission vor Wirkungen. OwnClearPool und frische physische
Abwesenheit vor Login-Drops/DBdrop; frische SQL-/CID-/Namens-/Inputclosure. Maximal
ein neuer eigener Container je Quellenkandidat, insgesamt sechs, 300s plus dieselbe
einmalige 60s-Cleanupdeadline schon vor dem höchstens 40s-Child. Fehlender vorhandener
Provider führt vor Wirkungen zu SKIP; keine Install-/Truststore-/Host-/Cloudfallbacks.

Heute SOURCE_ONLY: höchstens sechs Quellenkandidaten/CP3/hard6, ein Owner und enger
unabhängiger Rootreview. Null neue Prozesse, Native-SQL-, Container-, Domänenmodell-
oder Provider-Metadatenaufrufe; keine reale Handle-/CLR-/Startup-/C3-Wiederholung.
V1 bleibt bytegleich. Neue Module/Tests/Fixture unter Tests/Static, Anleitung unter
Documentation/HowTo. Kein Demos09-/CommonFramework-/Workflow-/Selectorwechsel und
kein RED-Profil in Default-CI (Continuous Integration; automatisierte Integrationsprüfungen). Spätere tatsächliche Producereingaben benötigen
gezielte Dependency-/Nativegates; diese Vorstufe schafft keine Selectorausnahme.

Gebundener Quellen-/Resultatreview, neue betroffene Gegenfälle, aktuelle Head-/Main-
Gates, PRintegration, vollständige Treeübernahme, Synchronisierung und eigener
Branchcleanup vor Schnittabschluss. Modell-/Reasoningtokenverbrauch UNKNOWN.
Allgemeine Entwicklung/DGN-007 pausiert, andere Repositories unverändert.
Öffentlicher Producer und volle TSK-009-Abnahme offen.

## Enger unabhängiger Quellenabschluss

Vier neue Quellen und der unveränderte öffentliche Frameworkcollector tatsächlich
gebunden. Zehn neue reine Methoden PASS; betroffene Privacy-/Typ-/Reserveänderungen
gezielt nachgeprüft. Root prüft Credentialabweisung vor Digests, vollständigen
Outerframe plus inneres Hex über Chunkgrenzen, sticky UNKNOWN und die erforderliche
positive eigene Cleanupreserve zusätzlich zu 26s konfiguriertem Windows-Nachlauf.
26s sind keine Wallclockgarantie; verbleibende Zeit nach Rücklauf neu prüfen.

Quellform PASS, öffentliche Captureprovenienz weiterhin NOT_INDEPENDENTLY_ATTESTED,
Gesamtstatus WARN, Runtime/Producer/TP-CON NOT_ESTABLISHED. Keine tatsächlichen
Process-/CLR-/SQL-/Container-/Provider-/Modellaufrufe und kein C3-Replay. V1,
Private42, gemeinsame Frameworkquellen und Default-CI unverändert. Aktuelle
Head-/Main-Gates, volle Treeübernahme, Synchronisierung und eigener Branchcleanup
gehören noch zum Integrationsabschluss; der nächste Schnitt ist der begrenzte
öffentliche Producer, keine erneut ausgeführte private C3-Probe.
