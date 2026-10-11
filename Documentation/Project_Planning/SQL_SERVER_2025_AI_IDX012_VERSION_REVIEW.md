# IDX-012: tatsächliche Versionsgrenze vor Setup

Stand: 2026-10-12. TSK-006/DEC-074; unabhängiger Teilnachweis, keine vollständige
Runtime-/TP-PERF-Abnahme und kein freigegebenes Manifest. Die Kostenfolge
bestand nach zwei historischen Client-FAILs mit C3 beide vollständigen
Lifecycles; ihre Integration über PR 178 ist vor dieser Admission abzuschließen.
Die weitere lokale Wellenfreigabe autorisiert diesen eigenen Schnitt.

## Methode, Budget und Quellenbindung

Ein unveränderter öffentlicher Preflight und Controllerdefault ohne Storage-,
Rebuild- oder Kostenflag. Höchstens sechs stabile Kandidaten/24 serielle eigene
Container gemäß der ausdrücklichen Benutzererweiterung, je Kandidat in fester
Reihenfolge: 2019 zweimal, 2022 zweimal. Ein FAIL hält den Kandidaten an;
der Folgekandidat benötigt geschlossenen FAIL und geänderte Ausführungsquellen.
Keine unveränderte Wiederholung bei Fehler. Nach einem stabilen vollständigen
Vier-Slot-Nachweis endet der Schnitt ohne unnötigen Verbrauch freier Kandidaten.
Vor der nächsten Admission sind vorheriger Lifecycle und eigener Cleanup
vollständig geschlossen; sämtliche öffentlichen Dateien und der Parent
bleiben innerhalb des Kandidaten bytegleich. Alte Kandidatenbudgets werden nicht zurückgesetzt.

Tatsächliche Versionsfamilie muss vor dem öffentlichen Aufruf zum festen Slot
passen. Der Controller muss genau eine Phase PREFLIGHT/SKIP/SKIP_VERSION
liefern, OriginalPreview=None und cleanup_ok=false erhalten. Es gab dann
kein Setup, keine eigene DB oder Originalbaseline und keinen SQL-Restore;
dieses Feld wird nicht als bestandene SQL-Recovery umgedeutet. Ein neuer
read-only Client prüft unabhängig die eigene Ziel-DB abwesend. FAIL/Timeout/
Configuration-SKIP oder eine weitere Phase sind kein gültiges Versionsresultat.

Eigene unveränderliche lokale Images, jeweils vier CPUs/sechs GiB, neue eigene
Name-/Label-/CID-/Image-/Ressourcenbindung. Keine Pulls oder Änderungen fremder
Container/Repositories/Hostoptionen. Secret ausschließlich ENV, nie Passwortargv.
300-s-Deadline einschließlich Startup; gesamter eigener Containercleanup
60 s ab erster Bereinigungsaktion, mit unabhängiger Namens- und vollständiger
bekannter CID-Abwesenheit. Keine Preview/MAXDOP-/DB-/DML-/Index-/Modellwirkung;
Readiness, Versionsabfrage, Preflight und unabhängige DB-Abwesenheit sind die
einzigen SQL-Aufrufe dieses erwarteten Pfads. Fehlgeschlagene Probe hält an;
eigene Safety-Recovery bleibt erforderlich, falls unerwartet Setup erreicht wird.

Root einziger Implementer. Die frühere Quellenclosure zur tatsächlichen
Versions-/Setup-/SKIP-Grenze bleibt für unveränderten Preflight verfügbar.
Die geänderte Controllerbindung, SQLCMDINI-Entfernung im Parent und
Ledgererweiterung auf sechs Kandidaten sind jetzt ohne neue P1/P2 eng unabhängig geschlossen;
keine erneute Analyse unveränderter Guard-/Recoveryquellen. Keine Runtime
oder Providerprobe durch den Reviewer.

| Quelle | SHA256 |
|---|---|
| öffentlicher 00_Preflight.sql | C9B56105FF001C49D5C2453D2214105C5BEE569E5976D28DCC1EEC344CE30CD3 |
| öffentlicher run_profile.py nach C3-Clientkorrektur | 5D7964A85FE8041726901A66BA4629633119BDB97491972E25F82F41CF685705 |
| eigener ignorierter Parent qualify_versions.py | 92D9C91D2F830F7B8DC8D82D2B83979BAF5F4A8FABC135F031E450C65D3F5F2D |

Die übrigen öffentlichen SQL-/Helperbytes bleiben unverändert; tatsächliches
Ledger bindet alle öffentlichen Quellen und Parent. Admission erst nach
vollständig abgeschlossener PR178-Integration, kanonischer Scopebindung und
frischer öffentlicher Hashprüfung auf dem Folgebranch.

## Aktueller Nachweis

Eng unabhängig geprüft und anschließend mit allen vier tatsächlichen
Versionslifecycles bestanden. PR178 ist vollständig abgeschlossen, main
synchronisiert und eigener Kostenbranch lokal/remote entfernt. Quellenhashes
bleiben nach Synchronisierung unverändert. Aktueller Folgebranch
codex/sql2025-ai-idx012-versions auf Basis
1aead3c727e90d907bf20048e2feebca41642b68; kanonischer Scope vor Admission
im CURRENT_EXECUTION_STATUS gebunden.
Der vorhandene statische Controllernachweis wird bei identischen Quellen nicht
erneut ausgeführt. Der enge Review attestiert ausschließlich Quellen; frühere
IDX-011-SKIPs und bestehende Offline-Demo-CI attestieren IDX-012 nicht.

Vier begrenzte eigene Proben dienen ausschließlich der Versionsgrenze; keine
zusätzliche Benchmark-/Provider-/Kosten- oder allgemeine Schulungsabnahme.
Aktuelle Head-/Main-Gates, Treegleichheit, Synchronisierung und eigener
lokaler/remote Branchabbau bleiben zusätzliche Integrationspflichten.
Modell-/Tokenverbrauch unbekannt; kein neuer Workflow oder administrativer Review.


## Tatsächliche vier Versionslifecycles

Alle vier eigenen Admissionen desselben bytegleichen Kandidaten bestanden.
Der öffentliche Controller lieferte jeweils genau
PREFLIGHT/SKIP/SKIP_VERSION; keine weitere Phase, kein Setup, keine eigene
DB-Baseline und kein Preview/MAXDOP-Effekt. OriginalPreview=None und
cleanup_ok=false bleiben wahrheitsgemäß erhalten; es wurde kein SQL-Restore
benötigt oder attestiert. Ein neuer read-only NativeClient bestätigte jeweils
ANN_DB|ABSENT; Rückgabecode null, stderr leer. Namen und vollständige eigene
CIDs sind nach Eigentumsprüfung unabhängig abwesend.

| Slot | Token | Tatsächlicher Build | Gesamter eigener Cleanup s |
|---|---|---|---:|
| 2019-skip-1 | D95D67B29CBB4BBA | 15.0.4490.9 | 11.3410314 |
| 2019-skip-2 | 3BFE11AA071F43BC | 15.0.4490.9 | 10.6015398 |
| 2022-skip-1 | D0D5543990174020 | 16.0.4295.3 | 12.7354592 |
| 2022-skip-2 | F588C8C09C0941AE | 16.0.4295.3 | 12.4055188 |

Alle Admissionen closed=true/failure=null; kein eigener Container verblieben.
Der Schnitt beendet seine Laufaufnahme nach einem stabilen Kandidaten/vier
Slots. Die freien Kandidaten werden nicht ohne neue Frage verbraucht. Dies
belegt die aktuelle öffentliche IDX-012-Versionsgrenze vor Setup, keine
SQL-2019/2022-Unterstützung des ANN-Profils, kein vollständiges IDX-012-
Release oder TP-PERF. Generation UNKNOWN bleibt erhalten. Rohoutput,
Konfiguration und Ledger bleiben lokal ignoriert. Konsistenter Nachweis
über PR integrieren, danach kontrollierte IDX-012-Fehler-/Recoveryfälle;
Minimalrollen und Hard-Abort bleiben zusätzlich offen.
