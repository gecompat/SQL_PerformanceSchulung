# TSK-004 – begrenzte Podman-Build- und Versionsqualifikation

Stand: 2026-10-11. Runtimequellen `5d71cda59849c357aafc5036c29529f7bf081d30`,
nach Squash `2f1dfec5d76cad63232f0a9eb968f880324ed5cf` identischer vollständiger Tree.
Qualifiziert ist ausschließlich QRY-014 auf Podman und dessen 15.x/16.x-Versionsgrenze;
kein vollständiger Podman-, Live-Modell- oder 360-Lauf-Matrixnachweis.

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
