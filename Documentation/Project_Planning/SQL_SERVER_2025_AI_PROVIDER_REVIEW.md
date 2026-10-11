# TSK-004 – begrenzte Podman-Build- und Versionsqualifikation

Stand: 2026-10-11. Runtimequellen `5d71cda59849c357aafc5036c29529f7bf081d30`,
nach Squash `2f1dfec5d76cad63232f0a9eb968f880324ed5cf` identischer vollständiger Tree.
Die Erstqualifikation betrifft QRY-014 auf Podman und dessen 15.x/16.x-Versionsgrenze.
Die unten abgegrenzten Erweiterungen decken inzwischen alle acht implementierten
Offline-Demos ab; kein Nachweis für alle 18 Entwürfe, Live-Modelle oder eine
360-Lauf-Matrix.

## Tatsächlicher Ausführungspfad

Der bereits laufende öffentliche Podman-CLI-Dienst meldete crun/linux/amd64.
Vorhandene Microsoft-SQL-Images wurden mit --pull=never benutzt. Jede Instanz bekam
einen neuen eigenen Namen, Ownerlabel TSK004-Podman-qualification, 4 CPU, 6 GB und
eine zufällige ausschließlich an 127.0.0.1 gebundene Portzuordnung. Vollständige lokale
Image-ID und Ownerlabel wurden am tatsächlich erzeugten Container geprüft. Es wurde
keine vorhandene Instanz übernommen oder eine Podman-Maschine gestartet/umkonfiguriert.

Der vorhandene Repository-FWK-Hosttarget verwendete den nativen ODBC-SQLCMD.EXE
gegen ausschließlich diese frisch erzeugte eigene Instanz. Die ausdrückliche
Disposable-Bestätigung im Adapter bezieht sich auf diesen geprüften eigenen Container.
SQLCMDPASSWORD und MSSQL_SA_PASSWORD wurden nur über Umgebungsvariablennamen übergeben;
keine Passwortwerte in Prozessargumenten. -C vertraute dem Zertifikat ausschließlich
dieses lokalen Laborendpunkts; dies ist kein allgemeiner TLS-/Providerfreigabebeleg.
SQL_Server_Lab und andere Repositories wurden nicht verändert oder aufgerufen.

| Engine | Tatsächlicher Build / Edition / OS | Lokale Image-ID | Beobachtung |
|---|---|---|---|
| 17.x | 17.0.5005.3 / Enterprise Developer, EngineEdition 3 / Linux Ubuntu 24.04 | `78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726` | zwei QRY-014-Lifecycles, je drei Assertions PASS |
| 15.x | 15.0.4490.9 / Developer, EngineEdition 3 / Linux Ubuntu 20.04 | `aa00fc4a3e14cc8baf6ce7447e738023aab84b90f3bf913304729201a8d80556` | zwei SKIP_VERSION vor SETUP, keine fachlichen Assertions |
| 16.x | 16.0.4295.3 / Developer, EngineEdition 3 / Linux Ubuntu 22.04 | `5b0916c7af8ca97ce9390be7e1182862d6fa90bff9f44f035dbe1626df140637` | zwei SKIP_VERSION vor SETUP, keine fachlichen Assertions |

17.x verwendete den vorhandenen Tag 2025-CU9-ubuntu-24.04; 15.x/16.x die vorhandenen
2019-latest/2022-latest-Tags. Tagname und lokaler Image-ID-Wert sind kein Repository-
Manifestdigest oder Beleg einer künftig unveränderten latest-Version. ProductLevel
meldete jeweils RTM; daraus wird kein zusätzlicher CU-Stand abgeleitet.

17.x bestand zudem Setup-Idempotenz und 48 volle Markergegenproben auf eigener Fixture.
Alle sechs Lifecycles hatten unabhängigen eigenen DB-Abwesenheitsbeleg; nach jeder
Providerprobe wurde der exakte eigene Container ownergebunden entfernt und seine
Abwesenheit separat geprüft. Eigene Portzuordnungen verschwanden mit dem Container.
Andere Podmanobjekte blieben erhalten. Es gab keinen SQL-Runtime-Fehlversuch.

## Review, Korrektur und Aufwand

Ein erforderlicher enger unabhängiger Quellenreview prüfte ausschließlich den neuen
privaten Provideradapter, keine erneut gelesenen bereits qualifizierten SQL-Quellen.
Er fand P2: Podman-/sqlcmd-/Qualifikationsprozesse hatten keine eigene Prozesszeitgrenze;
eine Readinessfrist wird erst nach Prozessrückkehr geprüft. Die tatsächlichen erfolgreichen
SQL-Belege oben sind keine empirische Qualifikation einer Prozesshänge-Situation.

Korrekturwelle 1 ergänzte 30 Sekunden je Helpercall, maximal 10 Sekunden je Readiness-
Client innerhalb der 180-Sekunden-Frist und 360 Sekunden für den Qualifikationskindprozess.
Cleanup besitzt einen separaten maximal 50-sekündigen Prozessbudgetpfad: Bestand 10,
Owner 10, Remove 20 und Abwesenheit 10 Sekunden. Ein zeitlich abgebrochener Create-Aufruf
kann das Objekt bereits angelegt haben; deshalb prüft Cleanup den tatsächlichen Bestand
und dessen exakten Owner statt allein das lokale Create-Erfolgsflag.

Vier private Python-Mockgegenfixtures bestanden Create-, Readiness-, Qualifikations-
und Cleanup-Timeout: begrenzte Calls, Fehlerpropagation, Abbau nach unklarem Create-
Ausgang und kein Cleanup-PASS nach Timeout. Diese Fixtures führen keine SQL-/OCI-Runtime
aus. Der gezielte Quellen-Nachcheck schloss P2 ohne weitere konkrete Befunde; keine
zusätzliche Reviewkette und keine eigene Runtime im Review. Die unveränderten bereits
grünen SQL-Läufe wurden nicht erneut ausgeführt. Private Helper/Fixtures bleiben unter
dem ignorierten Runtime-Verzeichnis, kein zweiter Backlog oder öffentlicher neuer Runner.

Ein Owner, ein erforderlicher Review und eine von maximal zwei kohärenten Korrekturwellen
bilden diesen endlichen Slice. Modell-/Tokenverbrauch des Orchestrators bleibt unbekannt.
TSK-004 bleibt offen für weitere Syntax-/Treiber-/Feature- und Providerpfade; der reale
lokale Modellpfad bleibt am DEC-033-Secretgate. Preview/ANN, Cloud-/Bezahl-, ONNX- und
rote Hoständerungen werden durch diesen Providerbeleg nicht freigegeben.

## Integration des Checkpoints

[PR 144](https://github.com/gecompat/SQL_PerformanceSchulung/pull/144) bestand sieben
Headprüfungen auf `4ac365c4b94ca78b8c5eaf76a7eb2d35c2bff83d`; Squash
`acd88e25e15932ff42154a7c40e436d8837aaee8` alle fünf ausgewählten Main-Workflows.
Vollständiger Tree `34b170cbf4cc4e2b20882459c261d1eb7a1cd3f7`, main-Synchronisierung
und eigener lokaler/remote Branchabbau wurden geprüft. Keine SQL-Runtimequelle
wurde im Checkpoint geändert oder unverändert erneut ausgeführt.
Unmittelbar folgte die [private DGN-010-Ergebnis-/Storagevorbereitung](SQL_SERVER_2025_AI_INDEX_HYPOTHESIS_REVIEW.md).

## Erweiterung auf QRY-015 und QRY-016

Am 2026-10-11 wurden die unveränderten Runtimequellen auf Basis
`86b08af7b355addae497b94f9f06e536414b6dd2` zusätzlich qualifiziert. Der private
Providerhelper übernimmt den oben geprüften Pfad unverändert und ergänzt nur eine
vor Create geprüfte Auswahl aus QRY-015/QRY-016. Prozess-/Readiness-/Cleanupgrenzen,
Env-only-Secrets und der öffentliche FWK-Hosttarget bleiben erhalten. Keine neue
SQL-Implementierung, Previewaktivierung, Lab-Schnittstelle oder Hostkonfiguration.

Es wurden sechs neue eigene Container seriell erzeugt und vollständig bereinigt;
die drei vorhandenen Images und ihre vollständigen lokalen IDs entsprechen der
obigen Tabelle. Tatsächliche Builds/Editionen/OS entsprechen ebenfalls dieser
Tabelle. Es gab keinen Runtime-Fehlversuch und keine Korrekturwelle.

| Demo | 17.0.5005.3 / Enterprise Developer / Linux | 15.0.4490.9 und 16.0.4295.3 / Developer / Linux |
|---|---|---|
| QRY-015 | zwei Lifecycles PASS, je drei Ergebnisassertionen; Setup-Idempotenz und 48 volle Markergegenproben PASS | je zwei SKIP_VERSION vor SETUP, keine fachliche Assertion |
| QRY-016 | zwei Lifecycles PASS, je drei Ergebnisassertionen; Setup-Idempotenz und 80 volle Markergegenproben PASS | je zwei SKIP_VERSION vor SETUP, keine fachliche Assertion |

QRY-015 wies zusätzlich leere Vektorfixtures in Baseline und Demonstration mit dem
erwarteten Ergebnisvertragsfehler ab. QRY-016 wies manipulierten Chunktext und
fehlende Chunks in Comparison mit diesem Fehler ab. Die Markerfälle umfassen jeden
der vier vollständigen Marker als fehlend, falsch, mit nachgestelltem Leerzeichen
und mit langem Suffix; Fehlerrückgabe und unveränderte Fixture-/Konfigurationswerte
werden je geprüfter Phase kontrolliert. Alle zwölf Lifecycles und die beiden
Negativkontroll-Fixtures haben unabhängige DB-Abwesenheitsbelege. Alle sechs exakten
eigenen Container wurden nach Ownerprüfung entfernt und separat als abwesend geprüft.

Ein Owner führt diesen begrenzten Schnitt. Die neue Auswahl benötigt kein zusätzliches
unabhängiges Sicherheitsreview: Sie verändert keine der bereits unabhängig geprüften
Provider-/Secret-/Prozess-/Cleanupgrenzen. Dies ist kein Review neuer SQL-Quellen oder
Nachweis von Prozesshängen. Der frühere Quellenreview und dessen vier private
Timeoutfixtures bleiben auf ihren damaligen Input gebunden und werden hier nicht als
neu ausgeführte Prüfung ausgegeben. Die alten QRY-014-Läufe wurden nicht wiederholt.
Modell-/Tokenverbrauch bleibt unbekannt.

Dieser zusätzliche Schnitt erweitert ausschließlich den Providerumfang auf QRY-014
bis QRY-016; er allein qualifiziert QRY-017–QRY-019 und DGN-008/009 nicht.
Windows, andere Editionen, niedrigere CLs, ANN und reale Modellintegration bleiben
offen. Vollständige TSK-004-/TSK-013-Abnahme ist damit nicht gegeben.

## Erweiterung auf QRY-017 und QRY-018

Der folgende unabhängige Schnitt verwendet Basis
`608280e0b1aaae4a64fdc20cfab7bc0569ef654c` und dieselben unveränderten öffentlichen
SQL-/FWK-/Host-/SQLCMD-Quellen. Nur die vor Create begrenzte Demo-Auswahl des
privaten Helpers wurde auf QRY-017/QRY-018 gesetzt. Die oben genannten Prozess-,
Ressourcen-, Secret- und Cleanupgrenzen bleiben erhalten; kein zusätzliches
unabhängiges Review unveränderter Grenzen. Ein Owner, maximal zwei Korrekturwellen;
keine Korrekturwelle oder Runtimefehlversuch wurde benötigt.

Sechs neue eigene Container wurden seriell mit denselben drei lokalen Image-IDs
betrieben. Builds, Editionen und OS entsprechen der ersten Tabelle.

| Demo | 17.0.5005.3 / Enterprise Developer / Linux | 15.0.4490.9 und 16.0.4295.3 / Developer / Linux |
|---|---|---|
| QRY-017 | zwei Lifecycles WARN_OPTIONAL_EVIDENCE_SKIPPED, je drei Ergebnisassertionen; Setup-Idempotenz und 48 volle Markergegenproben PASS | je zwei SKIP_VERSION vor SETUP, keine fachliche Assertion |
| QRY-018 | zwei Lifecycles PASS, je vier Ergebnisassertionen; Setup-Idempotenz, sieben fachliche Negativfälle und 80 volle Markergegenproben PASS | je zwei SKIP_VERSION vor SETUP, keine fachliche Assertion |

Das Full-Text-WARN ist an den tatsächlich gemessenen fehlenden optionalen
Full-Text-Bestand gebunden; es wird nicht zu einer Full-Text-Abnahme umgedeutet.
Die QRY-017-Gegenprobe mit fehlenden Suchdokumenten wurde mit dem erwarteten
Ergebnisvertragsfehler abgewiesen. QRY-018 prüft feste Offlineantworten mit
Claim-/Quellen-/Versions-/Kontextbindung, keine tatsächliche Generierung.
Seine sieben Negativkontrollen weisen falschen Claim, falsches Zitat, fehlende oder
manipulierte Chunks, fehlende aktuelle Quelle, fehlenden Replay und falschen
Quellenfakt ab. Die 48/80 Markerfälle behalten den vollständigen Bytevergleich.

Alle zwölf Lifecycles und beide Negativkontroll-Fixtures haben unabhängige eigene
DB-Abwesenheitsbelege. Alle sechs Container wurden nach Ownerprüfung entfernt und
separat als abwesend geprüft. Die Quellenlogs bleiben privat unter Runtime;
kein Hostinventar, Prompt, Secret oder Office-Artefakt wird übernommen.

Dieser Schnitt erweitert den bisherigen Podmanumfang auf QRY-014–QRY-018.
QRY-019 und DGN-008/009 sind darin nicht enthalten. Windows, andere Editionen,
niedrigere CLs und weitere Feature-/Modellpfade bleiben
offen. Die angehaltenen CL-/ANN-/Tenantfehler und DEC-033 ändern sich nicht.
Modell-/Tokenverbrauch bleibt unbekannt; keine Gesamt-TSK-Abnahme.

## Erweiterung auf QRY-019, DGN-008 und DGN-009

Dieser weitere unabhängige Schnitt verwendet Basis
`941b11dab7dc5c4e8cb0a09a95473368714392db` und dieselben unveränderten öffentlichen
SQL-/FWK-/Host-/SQLCMD-Quellen. Die private Demo-Auswahl ist vor Create auf genau
QRY-019/DGN-008/DGN-009 begrenzt. Ein Owner und maximal zwei Korrekturwellen;
kein zusätzliches unabhängiges Review unveränderter Provider-/Secret-/Zeit-/
Cleanupgrenzen. Kein Runtimefehlversuch und keine Korrekturwelle.

Neun neue eigene Container wurden seriell mit denselben drei lokalen Image-IDs
betrieben. Builds, Editionen und OS entsprechen der ersten Tabelle.

| Demo | 17.0.5005.3 / Enterprise Developer / Linux | 15.0.4490.9 und 16.0.4295.3 / Developer / Linux |
|---|---|---|
| QRY-019 | zwei Lifecycles PASS, je fünf Ergebnisassertionen; Setup-Idempotenz, acht fachliche Negativfälle und 80 volle Markerfälle PASS | je zwei SKIP_VERSION vor SETUP, keine fachliche Assertion |
| DGN-008 | zwei Lifecycles PASS, je neun Ergebnisassertionen; Setup-Idempotenz, zehn fachliche Negativfälle und 80 volle Markerfälle PASS | je zwei SKIP_VERSION vor SETUP, keine fachliche Assertion |
| DGN-009 | zwei Lifecycles PASS, je acht Ergebnisassertionen; Setup-Idempotenz, zehn fachliche Negativfälle und 80 volle Markerfälle PASS | je zwei SKIP_VERSION vor SETUP, keine fachliche Assertion |

QRY-019 benutzt tatsächliche Wertparameter und einen eingeschränkten Reader;
Fixture-/Statement-/Wert-/Rechteabweichungen wurden abgewiesen. DGN-008 prüft
tatsächliche SQL-Nutzung, Rechteverweigerungen und gebundene External-Model-
Metadaten ohne Inferenz oder Credentialbindung. DGN-009 prüft tatsächliches
Retrieval manipulierten Quelltexts, feste Tool-/Antwortfixtures und eingeschränkte
SQL-Rechte; keine allgemeine Sicherheit beliebiger Modellantworten.

Alle 18 Lifecycles und drei Negativkontroll-Fixtures haben unabhängige eigene
DB-Abwesenheitsbelege. Alle neun Container wurden nach Ownerprüfung entfernt und
separat als abwesend geprüft. Die privaten Quellenlogs sind mechanisch gegen
Status, Assertions, Negativfälle und Cleanup geprüft; keine Green-Vollogs oder
unveränderten SQL-Quellen werden erneut an einen Reviewer gegeben.

Damit sind QRY-014–QRY-019 und DGN-008/DGN-009 auf diesem konkreten Podmanpfad
qualifiziert: zusammen 16 SQL-2025-Lifecycles einschließlich zwei Full-Text-WARNs
und 32 kontrollierte ältere Versions-SKIPs. Dies erweitert den Providerbeleg,
keine Windows-/Editions-/CL-/Live-/Tenant-/ANN-/Gesamtworkstreamabnahme.
Die bekannten FAILs und DEC-033 bleiben unverändert; Modell-/Tokenverbrauch unbekannt.
