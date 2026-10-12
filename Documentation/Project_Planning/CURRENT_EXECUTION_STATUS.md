# Aktueller Ausführungsstand

## Aktive DGN-010-Veröffentlichung nach PR195

PR195 vollständig abgeschlossen: Head 83333b8d69532de77ddeab8b04f290e66e619c2f,
acht Head-Workflows PASS; Squash 398fecc664419cec5332b456de60c80498045d36,
sechs Main-Workflows PASS; ganzer Tree 93a2a03e4c42552cfe6342be71064014ac195eec
exakt übernommen, main FF/sauber, eigener lokaler/Remote-Branch entfernt.
Unmittelbare Fortsetzung: öffentlicher begrenzter SELECT-/DML-Runtimeproducer
im Branch codex/sql2025-ai-dgn010-public. DGN-010 bleibt PROPOSED; vollständiger
TP-PERF-/Nettonutzen-/Insert-/Worker-/Plan-/Modulclaim bleibt offen.

Vor Admission fest: sechs kohärente Quellenkandidaten, je höchstens 14 neue eigene
serielle Container, insgesamt höchstens 84. Je Scope zwei Versions-SKIPs für
2019/2022, zwei vollständige SQL2025-Lifecycles, zusätzlich ein kontrollierter
Setupfault pro Scope. 300 Sekunden reguläres Parent-/Profilbudget und 60 Sekunden
gemeinsamer eigener SQL-/Containercleanup, vier CPU/sechs GiB, feste vorhandene
Images, SQL2025 17.0.5005.3/Developer/CL170. 1000 synthetische Source-Rows,
MAXDOP/PREVIEW_FEATURES unverändert0, keine Host-/Provider-/anderen Repositoryeffekte.
Checkpoint nach geschlossenem Kandidaten; Retry ausschließlich nach relevant
geänderten Ausführungsquellen oder neuer Evidenz, historische FAILs erhalten.
Kandidat1: acht Versions-SKIPs erfolgreich; SQL2025-SELECT1 wegen falschem alten
Edition-Anzeigenamen SKIP_CONFIGURATION statt begrenztem Profil, Qualifikation
FAIL vor Setup. Alle neun eigenen Container/DBs abwesend, Endstatus bekannt.
Kandidat2 korrigiert ausschließlich die native Preflight-Editionsbindung auf
dokumentierte EditionID -2117995310/EngineEdition3, explizite NULLabwehr und
einen tatsächlichen Versions-/Editionsframe. Der geänderte gemeinsame Preflight
benötigt die Versionsqualifikation dieses Quellenkandidaten. Kein Budgetreset.
Aktuelle Head-/Main-CI qualifiziert den öffentlichen Consumer separat auf ihren
jeweiligen wegwerfbaren Instanzen; ein lokaler PASS ersetzt diese Gates nicht.

| Merkmal | Wert |
|---|---|
| Status | allgemeine Entwicklung `PAUSED`; begrenzter DGN-007-Abschluss gemäß `DEC-072` in [PR 132](https://github.com/gecompat/SQL_PerformanceSchulung/pull/132), dessen aktuelle CI-/Merge-Evidenz maßgeblich ist; PR 68 und PR 128 fachlich ersetzt und nicht weiterzuführen |
| Stand | 2026-10-11; KI-Workstream aktiv gemäß §0, übrige Entwicklung pausiert |
| aktueller Integrationsnachweis | Foundation `1.21.0` und die vertragsbezogene CI-Testauswahl sind durch [PR 126](https://github.com/gecompat/SQL_PerformanceSchulung/pull/126) integriert. Die eigenständige Fehlerrohdiagnose aus [PR 130](https://github.com/gecompat/SQL_PerformanceSchulung/pull/130) ist auf `aea230fb65798afddd4643c92b84f09403819ec6` in `origin/main`; die [PR-130-Matrix](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38048742623) bestand auf 2019/2022/2025. Der neuere [Main-Lauf](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38050043409) scheiterte auf SQL Server 2019 an G13; die [PR-132-Matrix](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38051475267) auf SQL Server 2022 ebenfalls. Keine Reporterfreigabe. |
| früherer fachlicher Basisstand | `2f04deb2fed0faf5bedf70101fea3f4b93d46678` nach PR 123; Ledgerkomponente §32.5 und Loaderrecordformen §33 bleiben im bisherigen Nachweisstand; SESSION_END und operativer Bootstrap-/Kanalvertrag bleiben pausiert/offen; SQL-Codebasis `da7b0eb…` aus Pull Request 65 unverändert |
| geprüfter Runtime-Stand | `782799e` aus Pull Request 42; `OPT-017`-Matrix vollständig grün |
| Fachliche Hauptwelle | `ADV-008` und `W-COV-001` vollständig runtimevalidiert |
| Abgeschlossene Folgepakete | `W2-002`, `ADV-009`, `ADV-010`, `LABSCN-002`, `LABSCN-004`, `INF-002`, `INF-003`, `LABINT-003` und der `CON-006`-bezogene `LABINT-004`-Schnitt `VALIDATED` |
| Szenariowelle | `CON-004`, `DGN-005` und `CON-006` – Project Adapter `0.1` und vollständiger Docker-/Podman-Lifecycle auf SQL Server 2025 validiert |
| Folgeplanung | [NEXT_DEVELOPMENT_WAVES.md](NEXT_DEVELOPMENT_WAVES.md) |
| Zweck | kanonischer operativer Einstiegspunkt für Nachweisstand, offene Gates und nächste Schnitte |

## 0. Entwicklungspause und Wiederaufnahme

### Autonome Umsetzung des KI-Workstreams vom 2026-10-11

Der neue Benutzerauftrag autorisiert die autonome Entwicklung des integrierten
KI-Workstreams durch den Orchestrator. Die Implementierungsgrenze des ursprünglichen
Planungsauftrags ist damit für diesen Workstream aufgehoben; allgemeine Entwicklung,
DGN-007-Folgearbeiten bleiben pausiert. Die spätere ausdrückliche Freigabe
„Ja, Heartbeat einrichten“ autorisiert ausschließlich den Heartbeat dieses
KI-Orchestrator-Chats: `sql-2025-ki-workstream-orchestrator`, alle 30 Minuten,
ACTIVE seit 2026-10-11. Er setzt zulässige Arbeit fort und meldet nur wesentliche
Änderungen, Abschluss, Fehler oder nötige Entscheidungen. Andere Automationen
werden nicht wieder aufgenommen; Cloud-/Bezahl- und ONNX-Gates bleiben bestehen.

Der endliche Gesamtumfang sind `TSK-004`–`TSK-014` und die 18 registrierten Demoentwürfe.
Erster zusammenhängender Schnitt: lokale Build-/Syntaxqualifikation aus `TSK-004` und
`QRY-014`–`QRY-017` aus `TSK-005`, auf eigenem Branch
`codex/sql2025-ai-local-demos`, Basis `fb53157eba381d23022b9a91aaa36a359f609576`.
Ein Implementierungsverantwortlicher führt den Schnitt; ein unabhängiger Review prüft
konkrete Sicherheits-/Versions-/Ergebnisrisiken. Pro Schnitt höchstens zwei kohärente
Korrekturwellen. Checkpoints sind lokale Qualifikation, stabiler Reviewkandidat und
validierte Integration. Bei ungelöstem Fehler, fehlender exakter Effektfreigabe oder
ausgeschöpfter Korrekturgrenze wird der betroffene Schnitt mit Evidenz angehalten und
eigener Cleanup abgeschlossen. Modell-/Tokenverbrauch ist unbekannt und wird nicht
als gemessener Wert ausgegeben.

Der erste Pfad verwendet synthetische Daten, float32 und eigene markierte Testdatenbanken.
Es werden weder bestehende Instanzen noch fremde Container verändert. Preview-, Modell-,
Cloud-/Bezahl-API- und ONNX-Pfade behalten ihre konkreten Qualifikations-/Freigabegates;
der lokale Pflichtpfad kann unabhängig fortschreiten. Die Rückmeldung des Benutzers bevorzugt die vorhandene
KI-Integration von SQL_Server_Lab. Der öffentliche lokale RAG-Controller ist der
zu prüfende Anwendungspfad; der interne HTTPS-Referenzslice ist getrennt von einem
allgemeinen Gateway zu behandeln. Cloudkosten und ONNX-Hoständerungen sind weiterhin
nicht freigegeben. Der Heartbeat ist eine Wiederaufnahmeabsicherung; ein regulär
abgeschlossener Schnitt führt im selben Turn zum nächsten zulässigen Schritt.

Die erste lokale Qualifikation von QRY-014 bis QRY-017 ist mit Ergebnisverträgen,
224 Markergegenproben, fünf fachlichen Negativkontrollen und eigenem Cleanup
belegt. QRY-017 meldet bei fehlender Full-Text-Komponente ausdrücklich WARN;
2019/2022 prüfen ausschließlich die Versionsgrenze. Der
[Implementierungsnachweis](SQL_SERVER_2025_AI_LOCAL_IMPLEMENTATION_REVIEW.md)
führt Charakterisierungsfehler und Korrekturen. Die unabhängige Quellenkontrolle
schloss alle vier Befundgruppen ohne weitere Safety-Befunde; sie ist kein eigener
Runtimebeleg. Alle 51 PR-Prüfungen am Head
`7831f9293d8e4653006c23e74b008e71707cabeb` bestanden, einschließlich der
[KI-Versionsmatrix](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38129371244).
[PR 135](https://github.com/gecompat/SQL_PerformanceSchulung/pull/135) ist in
`87017c04c04516495a4b653134532ac993db20ca` integriert. Vollständige Tree-Identität
des Squash-Ergebnisses wurde geprüft; main synchronisiert und der eigene
Arbeitsbranch lokal/remote entfernt. Alle 13 Main-Workflows desselben Integrationscommits
bestanden, darunter die [KI-Matrix](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38129793884)
und die [bestehende Regression](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38129793842).
Die anschließende Quellenprüfung des öffentlichen Modellpfads fand
eine konkrete Secret-Grenze: SQL_Server_Lab übergibt intern das SQL-Passwort als
sqlcmd-Prozessargument, entgegen DEC-033. Der
[Modellpfad-Leitfaden](../HowTo/SQL_SERVER_2025_AI_MODEL_PATHS.md#offene-secret-grenze-vor-live-rag)
bindet Quelle, Grenze und Wiederaufnahme. Kein Live-RAG-Aufruf, kein Lab-Run,
keine Änderung des anderen Repositorys. Nächster unabhängiger zulässiger Schnitt:
Offline-RAG QRY-018 aus TSK-008; die lokale Modellintegration aus TSK-007 bleibt
bis zu einem öffentlich nutzbaren passwortfreien Frameworkpfad angehalten.

Der zweite autonome Schnitt implementiert QRY-018 als modellfreien Offline-RAG-Replay,
Branch `codex/sql2025-ai-offline-rag`, Basis `0b6743f14f855103dfa63b0b67ffc75426f1ad1f`.
Zwei lokale 17.x-Lifecycles, 80 Markergegenproben, sieben fachliche Gegenproben,
Setup-Idempotenz und unabhängiger DB-/Containercleanup bestanden. Der unabhängige
Quellenreview fand im beauftragten Risikoscope keine offenen Befunde; keine zusätzliche
Runtimeattestation. Alle 49 aktuellen Headprüfungen bestanden; PR 137 ist in
`4de76ffc9eeb23882e5b6f4c02be3b32576b8f75` integriert. Tree-Identität, Synchronisierung,
lokaler/remote Branchabbau und alle elf Main-Workflows sind belegt im
[Offline-RAG-Nachweis](SQL_SERVER_2025_AI_OFFLINE_RAG_REVIEW.md). TSK-008 ist begonnen,
aber der Gesamtworkstream und der Livepfad bleiben offen.

Unmittelbar folgt QRY-019 aus TSK-009 auf `codex/sql2025-ai-sql-input-policy`, Basis
`4de76ffc9eeb23882e5b6f4c02be3b32576b8f75`. Der kontrollierte synthetische Harness
prüft eine feste vollständige SQL-Struktur, zwei tatsächlich gebundene Werte unter
QRY019_reader WITHOUT LOGIN und drei feste Rechteverweigerungen mit Bestandsnachkontrolle.
2019/2022 bestanden je zwei SKIP_VERSION-Lifecycles vor Setup und eigenen Cleanup.
Die aktuelle lokale 17.x-Qualifikation bestand zwei Lifecycles, fünf Ergebnisassertions,
80 Markergegenproben und acht fachliche Gegenproben; ein P2-Orakelfinding ist geschlossen.
Alle 49 Headprüfungen bestanden; PR 138 ist in `25a7c0af1b377b9250deeac4cf4288224900689f`
integriert. Tree-Identität, Synchronisierung, eigener Branchabbau und alle elf Main-Workflows
sind belegt im [QRY-019-Nachweis](SQL_SERVER_2025_AI_SQL_INPUT_REVIEW.md).
TSK-009 bleibt offen für Tenant-, Datenschutz- und weitere Providerfälle.

Der nächste zulässige CON-010-Schritt ist mit einer privaten 17.x-RLS-/Identitätsvorprobe
begonnen: drei Kontextfälle und drei tatsächliche Rechteverweigerungen bestanden samt
Sessionreset und eigenem DB-/Containerabbau. Konkreter Fehler und korrigierte Vor-/Nachbindung
stehen im [Checkpoint](SQL_SERVER_2025_AI_SQL_INPUT_REVIEW.md#nächster-checkpoint-private-con-010-vorbereitung).
Der vollständige CON-010-Kandidat wurde nach drei 17.x-Fehlversuchen und zwei
Korrekturwellen mit FAIL angehalten. Die neue Metadatenprobe belegt zusätzlich erzeugte
CONNECT-Grants als verbleibende Fixtureabweichung; Code und Registrierungsänderungen
wurden zurückgenommen, eigener DB-/Containerabbau ist belegt im
[Checkpoint](SQL_SERVER_2025_AI_TENANT_REVIEW.md). CON-010 bleibt PROPOSED. Nächster
unabhängiger Schritt DGN-009 bestand eine korrigierte private 17.x-Vorprobe mit
2 retrievten Quellen, Antworten/Tools je 1/3 und tatsächlichen Rechtefehlern 4613/229.
Der enge Quellenreview fand keine konkreten Befunde. Das daraus entstandene vollständige
DGN-009-Offline-Paket ist IMPLEMENTED und lokal qualifiziert: zwei 17.x-Lifecycles,
80 Markergegenproben, zehn Resultnegative und je zwei Versions-SKIPs auf 15.x/16.x,
jeweils eigener DB-/Containerabbau. Quellenreview und Integration sind abgeschlossen:
PR 141 bestand 49 aktuelle Headprüfungen; Squash
`8d3b074ddbfb4694f1d111ef41e56514da4a0391` alle elf Main-Workflows.
Tree-Identität, main-Synchronisierung und eigener Branchabbau werden
[getrennt geführt](SQL_SERVER_2025_AI_INJECTION_REVIEW.md).
Unmittelbar folgte die private DGN-008-Metadaten-/Rechtevorbereitung: tatsächliches
CREATE EXTERNAL MODEL ohne Inferenz, positiver parametrisierter SELECT und drei
Rechteverweigerungen 262/229/229 bestanden samt DB-/Container-/Netzabbau. Der erste
Readiness-Timeout und eine kohärente Korrekturwelle bleiben im
[Nachweis](SQL_SERVER_2025_AI_EXTERNAL_MODEL_REVIEW.md) sichtbar. Ein enger Quellenreview
fand keine konkreten Befunde. Der folgende vollständige DGN-008-Offline-Slice ist
IMPLEMENTED auf `codex/sql2025-ai-model-rights`, Basis
`eb203ed7f06abd3e52be2084fbc02e562eb3ecac`: getrennte Setup-/Ingestion-/Retrievalrollen,
tatsächliches Setup-CREATE, erlaubte Readerrow/Ingestion-Writes, fünf tatsächliche
Rechteverweigerungen nach Grantreduktion und volle Modell-/Rechte-/Endpointbindung.
Nach einer dokumentierten Korrekturwelle bestanden lokal zwei 17.x-Lifecycles mit
je neun Assertions, 80 Markergegenproben und zehn Resultnegative sowie eigener
DB-/Container-/Netzabbau. 15.x/16.x bestanden je zwei Versions-SKIPs vor SETUP;
der unabhängige Quellenreview fand keine offenen P1/P2. PR 143 bestand 49 Headprüfungen,
Squash `2f1dfec5d76cad63232f0a9eb968f880324ed5cf` alle elf Main-Workflows.
Tree-Identität, Synchronisierung und eigener lokaler/remote Branchabbau sind im
[Nachweis](SQL_SERVER_2025_AI_EXTERNAL_MODEL_REVIEW.md) geschlossen; Modell-EXECUTE
bleibt ausschließlich Metadatenrecht, Inferenz und echte Credential-/Egressabnahme offen.

Unmittelbar folgte eine begrenzte Podman-QRY-014-Providerprobe unter TSK-004:
17.0.5005.3 bestand zwei Lifecycles mit je drei Assertions, 48 Markergegenproben und
Setup-Idempotenz; 15.0.4490.9/16.0.4295.3 jeweils zwei Versions-SKIPs. Eigene DB-/
Containerabwesenheit bestand. Ein P2-Adapterfinding zu Prozesszeitgrenzen wurde mit
einer Korrekturwelle und vier privaten Timeoutgegenfixtures geschlossen; keine
unveränderte SQL-Wiederholung, keine empirische OCI-Hängequalifikation. Der
[Provider-Nachweis](SQL_SERVER_2025_AI_PROVIDER_REVIEW.md) begrenzt diese Aussage auf
QRY-014, keine vollständige Podman-/360-Matrixabnahme.
Für TSK-006 ist ein [konkretes lokales Preview-Freigabepaket](SQL_SERVER_2025_AI_PREVIEW_DECISION.md)
vorbereitet und inzwischen ausdrücklich vom Benutzer mit „Ja, lokalen ANN-Slice
freigeben“ genehmigt. Die Runtimequalifikation dieses begrenzten Effekts ist noch offen.
Andere zulässige Offlinearbeit bleibt ausführbar; Gesamtworkstream und Heartbeat bleiben aktiv.

Der Provider-/Previewcheckpoint ist über PR 144 mit sieben Headprüfungen und fünf
Main-Workflows integriert in `acd88e25e15932ff42154a7c40e436d8837aaee8`; Tree-Identität,
Synchronisierung und eigener lokaler/remote Branchabbau sind abgeschlossen.
Unmittelbar bestand eine neue private DGN-010-Ergebnis-/Storageprobe auf eigenem
Podman17.0.5005.3: je zehn gleiche volle Queryrows vor/mit/nach eigenem INCLUDE-Index,
1000 unveränderte SourceRows, 17 zusätzliche tatsächliche Indexseiten und unabhängiger
DB-/Containerabbau. Ein enger Quellenreview fand keine konkreten P1/P2. DGN-010 bleibt
PROPOSED; A/B/BA/AA, tatsächliche Pläne/Reads/CPU/DMLkosten und vollständige TP-PERF-
Abnahme fehlen. [Nachweis](SQL_SERVER_2025_AI_INDEX_HYPOTHESIS_REVIEW.md).
Dieser DGN-010-Checkpoint ist über PR 145 mit sieben Headprüfungen und fünf
Main-Workflows in `63f256fcbca522fa3ed7c2fdd6fee564c83381f1` integriert; Tree
`1908eeb9e1f4a9d97ae97e840627859fd9cd9eba`, Synchronisierung und eigener lokaler/remote
Branchabbau sind geprüft. Der folgende private CL-Slice ist nach zwei Korrekturwellen
mit FAIL angehalten: Skalaroracle ohne NULL-Gegenkontrolle, ungeklärter konkreter
Chunkfehler bei 150/160; nur die volle positive CL170-Chunkfixture und unabhängiger
eigener Cleanup sind belegt. [Grenzen und Wiederaufnahme](SQL_SERVER_2025_AI_COMPATIBILITY_REVIEW.md).
Keine dritte Korrektur. Dieser CL-/Freigabecheckpoint ist über PR 146 mit sieben
Headprüfungen und fünf Main-Workflows in `3ac552998996500849dcd29c9a855c5dd7063f92`
integriert; Tree `c36517efac6bb4c8d2f9fe9b279fc09cf39021c2`, Synchronisierung und
eigener lokaler/remote Branchabbau sind geprüft.
Unmittelbar folgte der neu konkret genehmigte lokale ANN-Slice. Sein erster privater
IDX-011-Prototyp ist nach zwei Korrekturwellen FAIL: Parser/Metadaten-/Vektorkonvertierung,
SQL-Recovery und konfiguriertes Cleanupbudget noch unqualifiziert. Alle drei eigenen
Container sind nach verifiziertem gezieltem Abbau abwesend; kein Index-/Recall-/Plan-
oder SQL-Restore-PASS. [Grenzen und Wiederaufnahme](SQL_SERVER_2025_AI_ANN_PREVIEW_REVIEW.md).
Keine dritte Korrektur oder automatische Rücksetzung dieses Slice-Budgets.
Der ANN-Fehlercheckpoint ist über PR 147 in
`73316d6fa0d1c86c528457d4b01a4250fe026e8f` integriert: sieben Headprüfungen,
fünf Main-Workflows, Tree `e2be0ab1b075423595b33ad9bb12b72b6ee7c246`,
Synchronisierung und eigener lokaler/remote Branchabbau abgeschlossen.
Der betreffende Runtime-Slice bleibt angehalten; Heartbeat und autorisierte
unabhängige Arbeit bleiben aktiv. Nächster unabhängiger Scope ist proportionales
Lehrmaterial für die acht bereits qualifizierten Offline-Demos, keine Wiederholung
der gescheiterten CL-/ANN-Prototypen und keine Gesamtlehrgangsfreigabe.
Der unabhängige TSK-012-Teilentwurf wird auf
`codex/sql2025-ai-offline-workbook`, Basis `e363d7e5d8927ffb4c4ce6e01e8740b93e8bc2a8`,
als [Offline-Arbeitsheft](../HowTo/SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md) umgesetzt:
acht Aufgaben mit Trainerlösungen, Beobachtungsbogen und didaktischer Rubrik.
Ein Owner, höchstens ein enger Review der neuen Fixture-/Rechte-/Providergrenzen und
zwei Korrekturwellen begrenzen den Scope. Keine Runtimequelle oder Präsentation wird
geändert; keine neue SQL-, Windows-/Podman-, Lehrzeit- oder Teilnehmerabnahme.
Betroffene lokale Doc-/Privacychecks und aktuelle Head-/Main-Gates sind vor Abschluss
erforderlich. Modell-/Tokenverbrauch bleibt unbekannt.
Die lokalen Guide-/Pfadprüfungen bestanden mit 31 Demos, Registry mit 264 Artefakten,
INF-001 mit sechs Runnern/neun How-to-Themen, Privacy, Diff und alle 27 Workbooklinks.
Der enge unabhängige Review fand keine konkreten P1/P2 in Aufgaben/Lösungen und deren
Fixture-/Rechte-/Providergrenzen; keine eigene Runtime oder Generalprobe ausgeführt.
Keine Korrekturwelle wurde benötigt. Die ausgewählten CI-Pfade führen statische
Gates aus; unveränderte SQL-Runtime und Officeprüfungen werden nicht wiederholt.
Der Arbeitsheft-Schnitt ist über PR 149 integriert: neun Headprüfungen auf
`4abed7167a6344279f1d81f028235adfd49556e3`, sieben Main-Workflows auf
`a566e23856758b7a1047dfbdb6641ffd094c7d82` bestanden. Tree
`f3bfe7241ef938c34b8d0b15148ce6a7047ba8ad`, Synchronisierung und eigener lokaler/remote
Branchabbau sind geprüft. Unmittelbar folgt auf `codex/sql2025-ai-offline-glossary`
der begrenzte [Grundlagenbegriffe-Teilentwurf](../HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md).
Ein Owner, maximal zwei Korrekturwellen, keine Runtime-/Präsentations-/Regeländerung;
bekannte Quellen werden gezielt geprüft, kein erneuter Review der alten Democodebasis.
Die fünf ausgewählten Primärquellen wurden aktuell geprüft; 33 lokale Links im
Glossar/Arbeitsheft, sechs mathematische Beispiele, INF-001 und Privacy bestanden.
Keine SQL-Runtime ausgeführt. Für diese reine Begriffserklärung ist kein zusätzliches
unabhängiges Sicherheitsreview erforderlich; der Arbeitsheftreview wird nicht auf
neue Inhalte umgedeutet. Keine ausgeführte Korrekturwelle.
Der Glossar-Schnitt ist über PR 150 integriert: fünf Headprüfungen auf
`d51245e628661d4042b8d19590569b48f07b9ee5`, drei Main-Workflows auf
`86b08af7b355addae497b94f9f06e536414b6dd2` bestanden. Tree
`ee31572c5087a1bd512e1ab9629dc4628c8beebf`, Synchronisierung und eigener lokaler/remote
Branchabbau sind bestätigt. Unmittelbar folgt auf
`codex/sql2025-ai-podman-metrics-chunks` eine begrenzte zusätzliche Providerqualifikation
von QRY-015/QRY-016: je zwei Lifecycles auf 17.x sowie je zwei ältere Versions-SKIPs
auf 15.x/16.x, maximal sechs neue eigene seriell betriebene Podmancontainer.
Vorhandene lokale Images, Loopback, vier CPUs/sechs GiB, Env-only-Secrets und der
vorhandene Host-/SQLCMD-/FWK-Pfad bleiben erhalten. Ein Owner, maximal zwei
Korrekturwellen; keine neue SQL-Funktion, Previewaktivierung oder Hoständerung.
Alle Ergebnis-/Marker-/Cleanupkontrollen bleiben unverändert; nur die Auswahl
des privaten Providerhelpers wird auf die zwei vorhandenen Demo-IDs begrenzt.
Die sechs frischen Providerläufe bestanden: vier positive Lifecycles auf
17.0.5005.3 mit je drei Assertions sowie acht SKIP_VERSION-Lifecycles vor Setup
auf 15.0.4490.9/16.0.4295.3. QRY-015/016 bestanden Setup-Idempotenz, 48/80 volle
Markerfälle und jeweils zwei fachliche Negativkontrollen. Unabhängige eigene
DB-Abwesenheit und sechs ownergebundene Containerabbaue sind bestätigt.
Keine Korrekturwelle; kein neuer unabhängiger Review unveränderter Grenzen.
Der [Providercheckpoint](SQL_SERVER_2025_AI_PROVIDER_REVIEW.md#erweiterung-auf-qry-015-und-qry-016)
begrenzt die Aussage. PR 151 ist mit acht Headprüfungen auf
`3427e0c9bcb60ebb822ddcab19131a3e0e0e9f91` und sechs Main-Workflows auf
`608280e0b1aaae4a64fdc20cfab7bc0569ef654c` integriert. Tree
`0da1460fde61843d72864030ea0456ed8decbabc`, Synchronisierung und eigener lokaler/remote
Branchabbau sind bestätigt. Unmittelbar folgt auf `codex/sql2025-ai-podman-search-rag`
der unabhängige QRY-017/QRY-018-Podmanschnitt mit denselben sechs seriellen eigenen
Containern als Höchstzahl, je zwei Lifecycles je Demo und 15.x/16.x/17.x sowie maximal
zwei Korrekturwellen. Unveränderte SQL-/Runner-/Marker-/Ergebnisverträge; optionales
Full-Text-WARN bleibt sichtbar. Ein Owner, keine neuen Provider-/Secret-/Cleanupgrenzen.
Der QRY-017/QRY-018-Podmanschnitt bestand die erwarteten Verträge auf allen drei
Versionen: QRY-017 zweimal WARN bei fehlender optionaler Full-Text-Evidenz mit je
drei Assertions, QRY-018 zweimal PASS mit je vier Assertions; acht ältere
SKIP_VERSION-Lifecycles vor Setup. 48/80 volle Markerfälle, Setup-Idempotenz und
ein/sieben fachliche Negativfälle bestanden; eigene DBs und sechs Container sind
unabhängig abwesend. Kein Runtimefehler, keine Korrekturwelle. PR 152 ist mit acht
Headprüfungen auf `3d11f2f5c8f12d77c47619033573cac42bbfdd4e` und sechs Main-Workflows
auf `941b11dab7dc5c4e8cb0a09a95473368714392db` integriert. Tree
`a3ad175b984436e0b98cc24e2674090468e9b3e1`, Synchronisierung und eigener lokaler/remote
Branchabbau bestätigt. Unmittelbar folgt auf `codex/sql2025-ai-podman-security`
der unabhängige Podmanumfang QRY-019/DGN-008/DGN-009, maximal neun serielle neue eigene
Container für drei Engineversionen und je zwei Lifecycles, ein Owner und maximal
zwei Korrekturwellen. Unveränderte öffentliche SQL-/Runner-/Ergebnis-/Markerquellen,
gleiche private Helpergrenzen, kein Modellaufruf und keine fremde Instanzwirkung.
Die neun Providerläufe bestanden die erwarteten Verträge: je zwei positive
17.x-Lifecycles mit fünf/neun/acht Assertions, zwölf kontrollierte ältere
Versions-SKIPs vor Setup. Je 80 vollständige Markerfälle, Setup-Idempotenz und
acht/zehn/zehn fachliche Negativfälle bestanden. Eigene DBs und alle neun eigenen
Container sind unabhängig abwesend; keine Korrekturwelle. Der konkrete Podmanpfad
deckt damit alle acht implementierten Offline-Demos ab, einschließlich des
sichtbaren QRY-017-Full-Text-WARN. Keine allgemeine Provider- oder Gesamt-TSK-Abnahme.
PR 153 ist mit acht Headprüfungen auf `c76943cc823c66c5370b7de1d682cce39d4d3ddb`
und sechs Main-Workflows auf `e4482e4d73a860a9b7c2f1b8d7204df749e1d2f5` integriert.
Tree `1fcbda32716960d9fb2dd797f5c7fdb57ca06158`, Synchronisierung und eigener
lokaler/remote Branchabbau bestätigt. Unmittelbar folgt auf
`codex/sql2025-ai-ann-resume-decision` der konkrete
[ANN-Wiederaufnahmeentwurf](SQL_SERVER_2025_AI_ANN_RESUME_DECISION.md),
PENDING_USER_DECISION: maximal zwei zusätzliche Korrekturkandidaten, vier neue
eigene Container, unveränderte Effekte. Der enge unabhängige Review prüfte allein
dieses neue Paket gegen beide ursprünglichen Autoritäten und fand keine P1/P2.
Keine neue Runtime, keine dritte ANN-Korrektur; die privaten Quellen sind unverändert.
Nach Integration dieses Entscheidungspakets bleibt ANN bis zur Benutzerantwort
angehalten. Cloud-/ONNX-/Secret- und übrige Fehlgates werden dadurch nicht geöffnet.
PR 154 ist mit sieben Headprüfungen auf `e84b18b608b22c9e3c7671ca70ef499d3a7f5ab4`
und fünf Main-Workflows auf `4f74caeb55dcbdaabd9f2176e7ced9dd77c103dc` integriert;
Tree `5d0747591b6094af1295f2cd05ae8b34238e323c`, Synchronisierung und eigener lokaler/
remote Branchabbau bestätigt. Die ausdrückliche Antwort „Ja, Zusatzpaket freigeben
(empfohlen)“ autorisiert jetzt allein das dort begrenzte neue ANN-Budget.
Wiederaufnahme auf `codex/sql2025-ai-ann-resume`, Basis dieses Integrationscommits,
maximal zwei zusätzliche kohärente Kandidaten und vier neue eigene Container.
Historische private Quellen bleiben erhalten; Kandidat 1 wird separat vorbereitet,
lokal gegen Recovery-/Deadline-/Baselinefehler geprüft und eng unabhängig reviewt,
bevor neue SQL-Runtime erfolgt. Andere Fehlbudgets bleiben angehalten.
Die begrenzte Wiederaufnahme wurde mit [FAIL abgeschlossen](SQL_SERVER_2025_AI_ANN_RESUME_REVIEW.md):
Kandidat 1 verwarf die Setupausgabe vor ANN, deren Originalinhalt nicht erhalten wurde;
Kandidat 2 erfasste Baseline 0, scheiterte aber bei dynamischer CREATE VECTOR INDEX
an Parserfehler 343 und anschließend 51003. Beide zusätzlichen Kandidaten sind
verbraucht; zwei von maximal vier Containern genutzt, keine dritte Korrektur.
Vor Runtime bestanden sieben lokale Sicherheitsfixtures und der enge unabhängige
Review mit geschlossenem Image-Tag-P2; Kandidat 2 bestand zwei betroffene Baseline-
Gegenfixtures und den Deltareview. Beide tatsächlichen Recoveries meldeten RESTORED_0
und DROP_CONFIRMED; jeweils separate SQL-DB-Abwesenheit und gebundener eigener
Containerabbau/Abwesenheit bestanden, Cleanup 12,112/12,117 Sekunden.
Keine Indexgeneration, ANN-Rows, Recall-/Plan-/Performance- oder FWK-Abnahme.
Parser-/Previewursache bleibt offen; weitere ANN-Arbeit benötigt einen konkret
vorbereiteten Nachweisumfang und neuen Budgetentscheid. Der Fehlercheckpoint wird
mit aktuellen Head-/Main-Gates integriert; unabhängige Lehrmaterialarbeit folgt.
PR 155 integrierte den wahrheitsgemäßen ANN-FAIL mit sieben Headprüfungen auf
`63a4263d6cea1c9d07a1bf4039d7b90e2d208780` und fünf Main-Workflows auf
`2ce534ab2f6d638c5fb38615c3a06ded6088aaac`. Tree
`8d1faa5eb105bb9d702c69c83c5a2c4465746244`, Synchronisierung und eigener lokaler/remote
Branchabbau bestätigt. Unmittelbar folgt auf `codex/sql2025-ai-offline-trainer`
der unabhängige TSK-012-Teilentwurf eines Trainerleitfadens für genau die acht
qualifizierten Offline-Demos: Moderation, Reihenfolge und Umgang mit tatsächlichen
Status-/Cleanupgrenzen. Lösungen/Rubrik bleiben im Arbeitsheft; keine neue SQL-,
Teilnehmer-, Masterdeck- oder Gesamtcurriculumabnahme. Ein Owner, höchstens zwei
kohärente Korrekturwellen; keine neue Runtime oder unabhängige Reviewkette für
unveränderte Demoquellen. Alle 14 lokalen Materiallinks, INF-001-Ausführungspfad,
Datenschutz-/Metadatenprüfung und git diff --check bestanden. Aktuelle Head-/Main-
Gates und Integration dieses reinen Materialschnitts folgen.
PR 156 ist mit neun Headprüfungen auf `4345ecbfddbb97120e5a679978a19ed65e7411e7`
und sieben Main-Workflows auf `5b638544621b50ad6a8db2c1051c4250861d3490` integriert.
Tree `07992392e80c446f83970ba2885af96782344d00`, Synchronisierung und eigener lokaler/
remote Branchabbau bestätigt. Unmittelbar folgt auf `codex/sql2025-ai-ann-parser-decision`
die reine Vorbereitung eines [einzelnen Parserdiagnoseentscheids](SQL_SERVER_2025_AI_ANN_PARSER_DECISION.md).
PENDING_USER_DECISION, keine neue Korrekturquelle oder SQL-Runtime: ein Kandidat/ein
Container, maximal zwei feste PARSEONLY-Aufrufe, kein Indexbuild/Search/Performance-
oder anschließender Implementierungsclaim. Drei frisch geprüfte Primärquellen sind
im Quellenregister ergänzt. SRC-106 dokumentiert den ignorierten MAXDOP-Parameter;
ein wirksamer freigegebener DOP-1-Pfad ist deshalb vor tatsächlichem Build/Search
zusätzlich erforderlich. Kein empirischer DOP-Befund und kein Konfigurationsworkaround.
Ein Owner und enger Entscheidungsreview allein der neuen Diagnose-/Effektgrenzen;
keine Wiederholung der unveränderten Runtime- oder Recoveryanalyse. Head-/Main-
Integration und eigener Cleanup dieses Entscheidungspakets sind erforderlich;
danach bleibt ANN bis zum ausdrücklichen neuen Budgetentscheid angehalten.
Der enge unabhängige Review des Diagnoseentscheids fand keine P1/P2 und schloss
das reine Entwurfs-Quellengate. Keine Ausführungsgenehmigung oder Runtime dadurch.
Die betroffene Datenschutz-/Metadatenprüfung und git diff --check bestanden.
TSK-012 bleibt insgesamt offen.
PR 157 ist mit acht Headprüfungen auf `1a85d7062f8d772e560b2eaa6f4a78dba9b053f4`
und sechs Main-Workflows auf `2f3cf94884bb4dcd0571ee8d55bfdcbbafd35c3a` integriert.
Tree `ce4ac56af199011a560b412ce07474ff0931c48e`, Synchronisierung und eigener lokaler/
remote Branchabbau bestätigt. Der Benutzer hat anschließend ausdrücklich
„Ja, Parserdiagnose freigeben (empfohlen)“ geantwortet. Auf
`codex/sql2025-ai-ann-parser-diagnosis` wird allein dieser neue Umfang umgesetzt:
ein privater Diagnosekandidat/ein Container, höchstens zwei unveränderte PARSEONLY-
Aufrufe, keine Korrekturwelle und kein anschließender Indexbuild/Search.
Die unveränderten hashgebundenen Setup-/Recovery-/Cleanuphelper wurden wiederverwendet.
Drei betroffene lokale Parser-/Snapshot-Gegenfixtures bestanden; der enge
unabhängige Review des neuen ausführbaren Deltas schloss zwei P2 vor SQL
(begrenzter JSON-Skalar und strikte 343-/Clientfehlerauswertung). Beide Reviews
übersahen die tatsächliche lokale sqlcmd-Inkompatibilität von `-h -1 -y 0`.
Der einzige Lauf ist [FAIL vor Setup](SQL_SERVER_2025_AI_ANN_PARSER_REVIEW.md):
300-Sekunden-Readinessbudget erschöpft, einzelne Readinessfehlerausgaben unbekannt;
SQL-Recovery und separate SQL-Abwesenheit tatsächlich FAIL wegen Clientoptionen.
Keine persistente Baseline oder Previewattestierung; beide PARSEONLY-Aufrufe
unausgeführt. Gebundener eigener Containerabbau und separate Abwesenheit bestanden,
Cleanup 11,989 Sekunden. Kein RESTORED-/DROP-/SQL-Abwesenheits-PASS behaupten.
Eine geänderte lokale Argumentkontrolle ohne SQL-Text/neuen Container gegen
ungültigen Loopbackport 0 erreichte ohne `-h` die erwartete Verbindungsablehnung;
keine SQL-/JSON-Runtimeabnahme. Ausgeführte private Quellen bleiben unverändert.
Ein neuer [enger Clientkorrekturentscheid](SQL_SERVER_2025_AI_ANN_PARSER_CLIENT_DECISION.md)
ist PENDING_USER_DECISION: ein zusätzlicher Kandidat/ein Container, keine
Korrekturwelle, unveränderte Parser-/Effekt-/Cleanupgrenzen. Der enge unabhängige
Review des Befunds und neuen Entwurfs fand keine P1/P2; keine Runtime dadurch.
Aktuelle Head-/Main-Gates, Integration und eigener Branchcleanup folgen;
keine neue Ausführungsfreigabe. Die alten FAIL-Checkpoints und weiteren
Build-/DOP-Gates bleiben bestehen. Der Heartbeat setzt keine dieser Grenzen zurück.
PR 158 ist mit sieben Headprüfungen auf `f119f8f172ba4107e34aabd38bb13e8d212021c1`
und fünf Main-Workflows auf `00b546416eb6e7250f10f42bff1c724dab43c4c6` integriert.
Tree `b78cbc4cd7e02c748d7ddd5374d31b2210ee7140`, Synchronisierung und eigener lokaler/
remote Branchabbau bestätigt. Anschließend bestätigte der Benutzer ausdrücklich
„Ja, Clientkorrekturpaket freigeben (empfohlen)“. Auf
`codex/sql2025-ai-ann-parser-client` wird genau dessen neuer Kandidat vorbereitet:
`-y 0 -w 65535` ohne `-h`, Optionsgegenfixture vor Containerstart und erhaltene
begrenzte redigierte Readinessfehler, sofortiger Stopp unbekannter Meldungen.
Die beiden neuen betroffenen Client-/Readinessfixtures bestanden; der enge
unabhängige Deltareview schloss gemischte Fehlerausgaben als P2 vor Runtime.
Der tatsächlich ausgeführte einzige neue Kandidat ist
[FAIL vor Setup](SQL_SERVER_2025_AI_ANN_PARSER_CLIENT_REVIEW.md): seine erhaltene
erste ODBC-TCP-Readinessmeldung enthielt eine zusätzliche Punktzeile und wurde
von der überengen Zeilenauswertung als unbekannt abgelehnt. 0 Parseraufrufe,
keine Baseline oder Previewattestierung. Tatsächlicher neuer Recoveryclient
meldete ALREADY_ABSENT, separater SQL-Client bestätigte DB-Abwesenheit; eigene
gebundene Containerentfernung und separate Abwesenheit bestanden, 13,887 Sekunden.
Die korrigierten Clientoptionen sind damit SQL-verbindungsfähig; keine Snapshot-,
Parser- oder ANN-Abnahme. Keine Änderung der ausgeführten historischen Quellen.
Der [Readinessentscheid](SQL_SERVER_2025_AI_ANN_READINESS_DECISION.md) bereitet
ausschließlich einen neuen Kandidaten/Container ohne Korrekturwelle und einen
präziseren Auswerter dieser tatsächlich erhaltenen Meldungsstruktur vor:
PENDING_USER_DECISION, keine neue ausführbare Quelle oder Runtime. Sein enger
Befund-/Entwurfsreview fand keine P1/P2; das spätere Ausführungsgate bleibt offen.
Aktuelle Head-/Main-Gates, Integration und eigener Branchcleanup folgen.
Der Heartbeat wiederholt diesen FAIL nicht automatisch.
PR 159 ist mit sieben Headprüfungen auf `80d07bc0c5a981851485c2ba182ee437e8a94ba9`
und fünf Main-Workflows auf `f0841b3652e23a3378bf535fe68caae53f3baea3` integriert.
Tree `8e5f0b43587a16284eca73e90ed686dd4d8e09b2`, Synchronisierung und eigener lokaler/
remote Branchabbau bestätigt. Der Benutzer bestätigte anschließend ausdrücklich
„Ja, Readinesspaket freigeben (empfohlen)“. Auf `codex/sql2025-ai-ann-readiness`
wird genau dessen neuer Kandidat vorbereitet: nur der Readinessmeldungsblock-
auswerter für die erhaltene TCP-/Punktzeilenstruktur wird geändert. Alle anderen
Client-/Parser-/Snapshot-/Helper-/Effekt-/Cleanupgrenzen bleiben unverändert.
Drei betroffene Readiness-/Optionsfixtures bestanden vor Containerstart;
der enge tatsächliche Delta-Quellenreview fand keine P1/P2. Der einzige neue
Kandidat bestand als [Parser-/Previewdiagnose](SQL_SERVER_2025_AI_ANN_PARSER_PASS_REVIEW.md):
tatsächliche Baseline 0, feste PARSEONLY-Probe mit Fehler 343 und unverändertem
erfasstem Zustand; nach abgeschlossenem Enable und frischem attestiertem DB-Client
Preview 1, derselbe Parsertext mit Code 0/leerer Ausgabe akzeptiert. Sieben volle
Snapshots mit je 107 Host-/41 DB-scoped-Konfigurationsrows verglichen, eigene
Fixture/Vectorindexabwesenheit vor/nach beiden Aufrufen. Ausgewählte sys.databases-
Optionsfelder erfasst, keine allgemeine Metadatenqualifikation behaupten.
Tatsächlicher RESTORED_0/DROP_CONFIRMED, separater neuer SQL-DB-Abwesenheitsclient,
gebundener eigener Containerabbau und separate Abwesenheit bestanden; Cleanup
12,715 Sekunden. Keine Indexgeneration, Suche, Recall-/Plan-/Performanceevidenz.
Historische 343-Batch-/Sessionursache nicht isoliert kausal bewiesen; alte FAILs
und Budgets bleiben erhalten. Ausgeführte Quellen unverändert, keine Wiederholung.
Unmittelbar wird ein [konkreter ANN-Build-/Suchentscheid](SQL_SERVER_2025_AI_ANN_BUILD_DECISION.md)
vorbereitet: zwei Kandidaten/vier eigene serielle Container, höchstens 1000
VECTOR(3)-Rows und zusätzlich nur eigener DB-scoped-MAXDOP-Set/Restore auf tatsächlich
gespeicherte 0. Frische Preview-/MAXDOP-Attestierung vor Build, Restore beider Werte
mit separatem neuem Attestierungs-/Dropclient. Angepasstes Cleanupcallbudget weiterhin
50 Sekunden/absolute 60; keine Host- oder zusätzlichen Providerwirkungen.
SRC-108 begründet den dokumentierten Konfigurationspfad, kein empirischer Worker-/
DOP-Befund. PENDING_USER_DECISION; enger Entwurfsreview fand keine P1/P2.
Aktuelle Head-/Main-Gates, Integration und eigener Branchcleanup folgen.
Kein automatischer ANN-Folgelauf oder neues Ausführungsgate dadurch.
PR 160 ist mit acht Headprüfungen auf `3030dc8ba5e00d7a057de0a09367e0ae4915993d`
und sechs Main-Workflows auf `443697b350c51aa153dff8a02f2d325fe78a734a` integriert.
Tree `252237a6024b22ba9bb352a7990a4d9f9381d4b0`, Synchronisierung und eigener
lokaler/remote Branchabbau bestätigt. Anschließend bestätigte der Benutzer
ausdrücklich „Ja, ANN-Build-/Suchpaket freigeben (empfohlen)“.
Auf `codex/sql2025-ai-ann-build` wird der erste neue private Kandidat vorbereitet:
beide persistente Baselines, separater Set/Attestierungsablauf und beide tatsächliche
Restores mit neuem Attestierungs-/Dropclient. Das neue Budget umfasst höchstens
zwei Kandidaten/vier serielle eigene Container; keine Wiederaufnahme alter Budgets.
Der unabhängige tatsächliche Delta-Quellenreview bleibt vor SQL erforderlich.
Dieser erforderliche erste Quellenreview und der gezielte QUOTED_IDENTIFIER-
Deltareview fanden keine P1/P2. Fünf betroffene lokale Tests bestanden.
Beide Kandidaten wurden auf je einem neuen eigenen Container ausgeführt:
[Build-/Such-FAIL](SQL_SERVER_2025_AI_ANN_BUILD_REVIEW.md). Erster Kandidat:
1934 wegen QUOTED_IDENTIFIER, kein Index-/Such-PASS. Zweiter Kandidat: tatsächliche
Sessionoption 1, eigener Index erstellt und Identitätscount 1, dann 51003 am
Generationsguard vor Metadatenausgabe und Search. Konkrete Generation/Typ-/Metric-
Rohwerte bleiben UNKNOWN; kein automatischer Generation-3-Schluss.
Beide tatsächlichen Restores 0/0, getrennte neue Attestierungs-/Dropclients,
separate SQL-DB-/Containerabwesenheit bestanden; Cleanup 12,444/12,397 Sekunden.
Zwei Kandidaten verbraucht, zwei ungenutzte Containerplätze erlauben keinen dritten.
Ausgeführte Quellen unverändert; kein neuer ANN-Lauf. Der konkrete
[einzelne Metadatenentscheid](SQL_SERVER_2025_AI_ANN_METADATA_DECISION.md) bereitet
einen neuen eigenen Kandidaten/Container ohne Search bei unveränderten lokalen
Effekten vor und bleibt PENDING_USER_DECISION. Aktuelle Head-/Main-Gates und
eigener Branchcleanup dieses begrenzten Befunds folgen vor der Benutzerfrage.
PR 161 ist mit acht Headprüfungen auf `cc62fd079ce6773880395b5b08ee1c5fe5d6f02b`
und sechs Main-Workflows auf `429d587d4b5b34bf36467c0b391afdb741b533a6` integriert.
Tree `966377ed486a6c7e09d57f9709c888f6e30d0879`, Synchronisierung und eigener
lokaler/remote Branchabbau bestätigt. Der Benutzer erteilte anschließend ausdrücklich
die Metadatenfreigabe und „auch alle weiteren Freigaben zur Durchführung dieser
Entwicklungswelle“. Diese zusätzliche Autorisierung erlaubt weitere notwendige
lokale ANN-Schritte der Welle ohne wiederholte Budgetfreigabefragen; historische
FAILs und verbrauchte Budgets bleiben erhalten. Jeder neue zusammenhängende Umfang
erhält weiterhin eine endliche Ausführungsgrenze, betroffene Tests, erforderliche
unabhängige Reviews und eigenen Cleanup. Zunächst genau die einzelne Metadatendiagnose
ohne Search auf `codex/sql2025-ai-ann-metadata`, Basis `429d587d4b5b34bf36467c0b391afdb741b533a6`.
Keine zusätzliche Host-/Cloud-/ONNX-Wirkung aus diesem lokalen Paket ableiten.
Der enge tatsächliche Metadaten-Quellenreview fand keine P1/P2, fünf betroffene
lokale Tests bestanden. Der einzige neue Kandidat bestand als
[vollständige Metadatenaufnahme](SQL_SERVER_2025_AI_ANN_METADATA_REVIEW.md):
eigener Index Typ 8/VECTOR, DiskANN/COSINE, gültige Buildparameter mit StartId/L/M/R,
Version-Schlüssel fehlt tatsächlich, beide Versionsableitungen NULL. Keine Generation
erraten; keine Search-/Recall-/Indexnutzungsevidenz. 1000 volle Quellenrows,
24 Marker-/neun Baseline-/drei Quellgegenproben und vier vollständige Snapshots
mit je 107 Host-/41 DB-scoped-Konfigurationsrows bestanden. Eigener Indexdrop,
tatsächliche Restores 0/0, neuer Attest/Dropclient, separater SQL-DB-Abwesenheitsclient
und gebundener Containerabbau/zusätzliche Abwesenheit bestanden; Cleanup 12,439 Sekunden.
Unmittelbar wird gemäß zusätzlicher ausdrücklicher Benutzerautorisierung ein
[begrenzter Legacy-Signaturversuch](SQL_SERVER_2025_AI_ANN_LEGACY_TRIAL_DECISION.md)
vorbereitet: eigener neuer Diagnoseumfang, Generation UNKNOWN bleibt erhalten,
eine feste dokumentierte TOP_N-Signatur, kein alternativer Syntaxfallback oder
volle IDX-011-Abnahme. Quellenreview und Integration der Metadatendiagnose
bleiben vor dessen SQL-Start erforderlich. Historische FAILs/Budgets unverändert.
PR 162 ist mit sieben erfolgreichen Headprüfungen auf
`b838f121e5e555d1d535991b2406452bb7ee92fb` gegen Basis
`429d587d4b5b34bf36467c0b391afdb741b533a6` integriert. Alle fünf ausgewählten
Main-Workflows auf `99657fa2c3bd29f17ee5139b96439f3b23a28e15` bestanden;
Tree-Identität `2c3b2d9491cb515fd024b699f524d0b3e6a1ef74`, Synchronisierung und
eigener lokaler/remote Branchabbau bestätigt. Unmittelbar beginnt der autorisierte
Legacy-Diagnoseumfang auf `codex/sql2025-ai-ann-legacy` an dieser Basis.
Der erforderliche Methoden-/Quellenreview des unveränderten ersten privaten
Kandidaten und seine fünf lokalen Tests sind abgeschlossen. Höchstens zwei neue
Kandidaten/vier serielle eigene Container, höchstens zwei vollständige Lifecycles
je positivem stabilem Kandidaten; keine Generation oder Indexnutzung voraussetzen.
Der erste Legacy-Kandidat stoppte am Texttyp-/Metricguard vor Search (51003),
bei ausgegebener vollständiger DiskANN/COSINE-Metadatenrow. Tatsächliche Speichertypen
noch unbekannt; beide Restores 0/0, neue Attestierung und separate DB-/Containerabwesenheit
bestanden, Cleanup 12,297 Sekunden. Seine ausgeführten Quellen bleiben unverändert.
Der zweite erlaubte Kandidat erfasst Textspeichertypen/-längen und vergleicht
die Werte ohne Case-/Whitespaceänderung in einheitlicher Unicodeform; zehn feste
Wertnegative und eine varchar-/nvarchar-Positive sind zusätzlich vor Search gebunden.
Zwei lokale Generator-Testfehler durch implizite Windows-Decodierung vor SQL wurden
im vorbereiteten Kandidaten korrigiert; der anschließende Fünf-Test-Lauf bestand.
Der enge unabhängige Review des tatsächlichen Deltas fand keine P1/P2; Quellengate
vor SQL geschlossen. Der zweite Kandidat bestand beide vorgesehenen vollständigen
[Legacy-Ergebnislifecycles](SQL_SERVER_2025_AI_ANN_LEGACY_TRIAL_REVIEW.md):
tatsächliche Texttypen nvarchar 14/12 Bytes, feste TOP_N-Signatur lieferte je fünf
distanzgeprüfte Rows und 5/5 Schnittmenge mit Exact-Oracle. Je 24 Marker-/neun
Baseline-/drei Ergebnis-/drei Quell-/zehn Textwertgegenproben und vier vollständige
107-Host-/41-DB-scoped-Snapshots bestanden. Voller Source-/Metadatenvergleich,
eigener Indexdrop, beide tatsächlichen Restores 0/0, neue Attestierung und separate
DB-/Containerabwesenheit bestanden; Cleanup 12,383/12,710 Sekunden. Generation
UNKNOWN und Indexnutzung UNPROVEN; kein Plan-/Performance-/Demo-PASS. Zwei neue
Kandidaten/drei Container verbraucht, Umfang regulär abgeschlossen; Integration folgt.
Unmittelbarer Folgeschnitt gemäß Wellenautorisierung ist die
[begrenzte tatsächliche Planausgabe](SQL_SERVER_2025_AI_ANN_PLAN_DECISION.md):
maximal zwei neue Kandidaten/zwei Container, eigener enger Plan-/Clientreview und
betroffene Tests vor SQL, keine DML-/Cloud-/ONNX-/Hostwirkung.
PR 163 ist mit sieben erfolgreichen Headprüfungen auf
`03c04a77644774df497e5514bcfe0632002d628e` gegen Basis
`99657fa2c3bd29f17ee5139b96439f3b23a28e15` integriert. Alle fünf ausgewählten
Main-Workflows auf `d4ace6614ae500329e05160e0dd4f7ad16c9b8e7` bestanden;
Tree-Identität `ff755ae9155f254508ccc8b034b7bd344eae9c1d`, main synchronisiert,
eigener Branch lokal/remote entfernt. Unmittelbar beginnt die begrenzte Plandiagnose
auf `codex/sql2025-ai-ann-plan` an dieser Basis. Fünf bestehende lokale Grenztests
und sechs neue Plan-/Manipulationstests bestanden. Der enge unabhängige Review des
tatsächlichen XML-/Statement-/Runtime-/Indexbindings fand keine P1/P2;
Quellengate vor SQL geschlossen. Der erste einzelne Plankandidat bestand die
[tatsächliche Planausgabe](SQL_SERVER_2025_AI_ANN_PLAN_REVIEW.md): vollständiges
gebundenes Actual-XML, eigener Vector Index Seek/DiskANN mit fünf tatsächlichen
Rows, daneben Nested Loops und Clustered Index Seek. Indexnutzung für diesen
festen ungefilterten Suchaufruf beobachtet; Generation UNKNOWN. Ergebnis-/Source-/
Metadaten-/Konfigurationskontrollen bestanden, beide tatsächlichen Restores 0/0,
neue Attestierung und separate SQL-/Containerabwesenheit bestanden; Cleanup
12,583 Sekunden. Ein Kandidat/Container verbraucht, Umfang regulär abgeschlossen;
Integration folgt. Unmittelbarer Folgeschnitt gemäß Wellenautorisierung ist die
[begrenzte Filter-/Ergebnisdiagnose](SQL_SERVER_2025_AI_ANN_FILTER_DECISION.md)
mit drei vorab festen Id-Fenstern und gebundenem Exact-Oracle; eigenes Quellen-/
Testgate vor SQL. Kein gefilterter Indexnutzungs-/Performance-/voller Demo-PASS.
PR 164 ist mit sieben erfolgreichen Headprüfungen auf
`eae8ebd1a1813366fe83154041e0757b7291d06d` gegen Basis
`d4ace6614ae500329e05160e0dd4f7ad16c9b8e7` integriert. Alle fünf ausgewählten
Main-Workflows auf `b35f147632ceba3a8b433ec2ac062bfe70205301` bestanden;
Tree-Identität `7997a7995efad05d05cb88f4c9085272040a0fdf`, main synchronisiert,
eigener Branch lokal/remote entfernt. Unmittelbar beginnt die Filterdiagnose
auf `codex/sql2025-ai-ann-filter` an dieser Basis. Fünf bestehende Grenztests
und sechs neue Filter-/Coverage-/Recall-/Manipulationstests bestanden. Enger
unabhängiger Review des tatsächlichen Filter-/Oracle-/Clientdeltas fand keine P1/P2;
Quellengate vor SQL geschlossen. Ein stabiler Kandidat bestand beide vollständigen
[Filterlifecycles](SQL_SERVER_2025_AI_ANN_FILTER_REVIEW.md): breite Fenster 1–1000/
1–100 je fünf ANN-/Exact-Rows und Recall@5 1; enges Fenster 501–510 null ANN- gegen
fünf Exact-Rows, Recall@5 0 und sichtbares ROWS_BELOW_K. Vier neue Filtergegenproben
und alle bisherigen Source-/Marker-/Baseline-/Metadaten-/Konfigurationskontrollen
bestanden. Beide tatsächlichen Restores 0/0, neue Attestierung und separate SQL-/
Containerabwesenheit bestanden; Cleanup 12,354/12,552 Sekunden. Generation UNKNOWN,
gefilterte Indexnutzung UNPROVEN, kein Performance-/voller Demo-PASS. Ein Kandidat/
zwei Container, Umfang regulär abgeschlossen; Integration folgt.

Unmittelbarer Folgeschnitt aus der erteilten lokalen Wellenautorisierung ist eine
begrenzte sessionbezogene Messdiagnose am ungefilterten festen Query/Korpus:
maximal zwei neue Kandidaten/vier serielle eigene Container und zwei Lifecycles
je positivem stabilem Kandidaten. Beide Pfade geben dieselben fünf Id-/Distanz-
Spalten zurück; identische temporäre Ergebnisspeicherung. Je Pfad ein ausgeschlossener
Warm-up und fünf gemessene Batches mit je zehn Suchstatements; alternierende
Paarreihenfolge, keine Cacheleerung. Pro Lifecycle höchstens 61 Legacy-Suchaufrufe
und 61 Exact-Queries einschließlich bisherigem Query-/Oraclevorlauf. Alle Rows
und Distanz-/Recallgrenzen weiterhin tatsächlich prüfen. Session-CPU-/Read-/
Logical-Read-/Write-Deltas und UTC-Elapsed erfassen, gleiche Session/Nicht-NULL/
Nichtnegativität prüfen; Median und Min/Max aus fünf Batches je Pfad. Quantisierung,
Mess-/temporärer Speicheraufwand und ausgeschlossener Warm-up bleiben sichtbar;
kein festes Speedupversprechen, optionale Waits nicht erhoben. Generation UNKNOWN,
neue Indexnutzung UNPROVEN ohne neue Planausgabe. Unveränderte 1000-Row-/Image-/
Build-/Ressourcen-/Konfigurations-/Marker-/300-Sekunden-/60-Sekunden-Cleanupgrenzen;
keine DML-/Stale-/Host-/Cloud-/ONNX-Wirkung. Betroffene Tests und enger erforderlicher
Methoden-/Quellenreview vor SQL; Retry nur mit geändertem Input/neuer Evidenz.
Nach zwei ungelösten Kandidaten Befund integrieren, kein stilles Budgetreset.
Aktuelle Head-/Main-Gates, PR, Synchronisierung und eigener Cleanup schließen
diesen eigenen Messbefund ab. Dies ist keine vollständige FWK-/TP-PERF-/Demoabnahme.
PR 165 ist mit sieben erfolgreichen Headprüfungen auf
`8e062ec7486b81d35ee2eec679f593d274f50a8b` gegen Basis
`b35f147632ceba3a8b433ec2ac062bfe70205301` integriert. Alle fünf ausgewählten
Main-Workflows auf `777c56210e08114f9d180ae907075a50544a4be0` bestanden;
Tree-Identität `8bb954836a5d8b90e8e066067a9af59d6f67cf23`, main synchronisiert,
eigener Branch lokal/remote entfernt. Unmittelbar beginnt der Messfolgeschnitt
auf `codex/sql2025-ai-ann-measure` an dieser Basis. Fünf bestehende Grenztests und
zunächst fünf neue Mess-/Coverage-/Manipulationstests bestanden. Der unabhängige
Review fand einen P2: Minimum der Batch-Recallmittelwerte irreführend als Queryminimum
benannt. Vor SQL im unbenutzten Kandidaten auf min_batch_mean_recall_at_5 korrigiert;
eine tatsächliche 49/50-Fixture bindet 0,98 ohne Queryminimumclaim. Sechs betroffene
Mess-Gegenproben bestanden; der enge Nachreview schloss den P2 vor SQL.
Messkandidat 01 wurde einmal unverändert ausgeführt: technische Capture-/Ergebnis-/
Cleanupkontrollen PASS, sämtliche Session-CPU-/Read-/Logical-Read-/Write-Deltas null.
EXACT-Elapsed-Median null; keine Performancequalifikation: WARN ungeeignetes oder
inaktives Zählerfenster und Zeitquantisierung. Der ausgeführte Kandidat wird nicht
verändert oder ohne neue Evidenz wiederholt. Seine fünf gemessenen Batches je Pfad
enthielten tatsächlich je 50 Treffer/50 mögliche; Restore beider Baselines 0/0 und
unabhängige DB-/Containerabwesenheit bestanden in 12,385 Sekunden.
Der zweite bereits budgetierte Kandidat ändert ausschließlich die Zählerquelle auf
sys.dm_exec_requests (LIVE_REQUEST), gebunden an dieselbe Session, Request-ID,
Startzeit, Connection-ID und eigene DB-ID vor/nach jedem Batch. Keine fehlenden/nullen
oder negativen Zähler und keine wechselnde Identität; mindestens ein positives
Logical-Read-Delta je Pfad nach Warm-up-Ausschluss verlangt. Das belegt ein aktives
Fenster, keine vollständige Worker-IO: parallele Row-Mode-Requests haben laut
SRC-110 eine Koordinatorgrenze; tatsächlicher Such-DOP bleibt UNPROVEN und
preemptive Zeit nicht erfasst. Suchzahl, Reihenfolge, Ergebnis-/Qualitätskontrollen,
Effekte und endliches Kandidaten-/Containerbudget bleiben unverändert. Betroffene
13 betroffene Gegenproben bestanden; enger unabhängiger Methoden-/Quellenreview
schloss vor SQL ohne offene P1/P2. Kandidat 02 bestand zwei unveränderte Lifecycles:
aktive CPU-/Logical-Read-Deltas, alle gemessenen Batches 50 Rows/50 Oracle-Treffer,
EXACT-Zeitnullwerte weiterhin sichtbar. Kein ANN-Vorteil am kleinen festen Korpus
belegt; keine Speedupratio aus quantisierten Kleinstmessungen. Vollständige Source-/
Metadaten-/Konfigurationskontrollen, Restores 0/0, neue Attestierung und separate
DB-/Containerabwesenheit bestanden; Cleanup 12,386/12,299 Sekunden. Zwei Kandidaten/
drei Container, Messscope abgeschlossen. Der [Messnachweis](SQL_SERVER_2025_AI_ANN_MEASUREMENT_REVIEW.md)
bewahrt Kandidat01-WARN und begrenzte Requestmetrik. PR 166 ist mit acht erfolgreichen
Headprüfungen auf `0f02c1422553d14bb143efda5b7e2a21b0177c10` gegen Basis
`777c56210e08114f9d180ae907075a50544a4be0` integriert. Alle sechs ausgewählten
Main-Workflows auf `b7fd69ce49e50a4f489b38640464e520f0329087` bestanden;
Tree-Identität `0050622ffdc09c9070bbceb73aad19ae98d0ccff`, main synchronisiert,
eigener Branch lokal/remote entfernt. Der neue DML-Diagnosebranch beginnt an
dieser Basis: `codex/sql2025-ai-ann-dml`.

Unmittelbarer nächster zulässiger eigener Schnitt nach dieser Integration:
ein fester gültiger UPDATE auf der eigenen 1000-Row-VECTOR(3)-Quelle bei aktivem
eigenem Vectorindex, innerhalb einer ausschließlich zurückgerollten Transaktion.
Höchstens zwei neue Kandidaten/vier serielle eigene Container, zwei Lifecycles
je stabilem positiven Kandidaten; kein INSERT/DELETE/MERGE und keine Staleoption.
Tatsächlichen SQL-Fehler oder Erfolg aufnehmen, keine erwartete Fehlernummer erfinden;
Erfolg ebenfalls immer zurückrollen. Vollständigen Sourcezustand nach Rollback
mit der vor DML gesicherten Quelle vergleichen, Own-Indexmetadaten weiter binden.
Keine Freshness-/DML-Freigabe aus einer technischen Diagnose ableiten. Alle bisherigen
Image-/Versions-/Ressourcen-/Konfigurations-/Marker-/Zeit-/Restore-/Cleanupgrenzen
gelten; betroffene Tests und enger tatsächlicher Quellen-/Methodenreview vor SQL.
Keine Host-/Cloud-/ONNX-Wirkung. Kein Reset früherer Budgets; eigener endlicher
DML-Diagnosescope aus der ausdrücklich erteilten weiteren lokalen Wellenfreigabe.
Vorprüfung der tatsächlichen vollständigen 41 DB-Konfigurationsrows des gebundenen
Builds zeigt keine ALLOW_STALE_VECTOR_INDEX-Row. Der Diagnoseguard verlangt dieses
ABSENT-Profil; keine erfundene OFF-Attestierung und kein Set. Ein neues privates
Kandidat01-Delta begrenzt genau ein parameterisiertes gültiges UPDATE auf Id 23,
vorher tatsächlich vorhandenes und abweichendes VECTOR(3)-Ziel. Nach Erfolg wird
die tatsächliche eine Row und Zielbyteform innerhalb der Transaktion gesichert;
SQL-Rejection und Fehlernummer/-State/-Text werden ohne Read-only-Klassifikation
aufgenommen. Immer Rollback und vollständiger beidseitiger Sourcebytevergleich.
Elf betroffene Grenz-/Diagnosegegenproben bestanden; erforderlicher enger Methoden-/
Quellenreview schloss vor SQL ohne offene P1/P2, kein vollständiger erneut unveränderter
Safetyreview. Kandidat 01 tatsächlich FAIL: gültiges UPDATE mit SQL 42231/State 1
verweigert, vollständige Source-/Metadaten-/Konfigurationskontrollen bestanden;
JSON meldete RolledBack=false trotz zuvor bestandenem Transaktionsguard. Dies
ist widersprüchliche Transaktionsevidenz, kein technischer DML-Diagnose-PASS.
Restores 0/0, neue Attestierung und separate DB-/Containerabwesenheit bestanden
in 12,253 Sekunden; Prozesscode 1, ausgeführte Bytes bleiben unverändert.
Der zweite bereits budgetierte Kandidat sichert tatsächlichen @@TRANCOUNT und
XACT_STATE() unmittelbar nach Rollback in Variablen, prüft beide null und gibt
diese Zahlen sowie das daraus abgeleitete RolledBack aus, statt erneut innerhalb
der JSON-SELECT auszuwerten. Parser verlangt beide tatsächlichen Zahlen null;
NULL, negativ, offen oder Boolean werden verworfen. Sieben betroffene Tests und
enger Befundnachreview schlossen vor SQL ohne offene P1/P2. Zwei unveränderte
Lifecycles bestanden: tatsächliche UPDATE-Verweigerung 42231/State 1,
TransactionCount=0/TransactionState=0, Sourcebytes/Indexmetadaten unverändert.
Vollständige Kontrollen, Restores 0/0, neue Attestierung und separate DB-/
Containerabwesenheit bestanden; Cleanup 12,391/12,323 Sekunden, Prozesscode 0.
Zwei Kandidaten/drei Container, Scope abgeschlossen; früherer FAIL bleibt erhalten.
Der [DML-Diagnosenachweis](SQL_SERVER_2025_AI_ANN_DML_REVIEW.md) begrenzt diesen
konkreten UPDATE-Befund: Freshness NOT_TESTED, allgemeine DML-Unterstützung UNPROVEN,
Generation UNKNOWN. PR 167 ist mit sieben erfolgreichen Headprüfungen auf
`1f0a81c8787ca666858236ee3e74f1ba51287096` gegen Basis
`b7fd69ce49e50a4f489b38640464e520f0329087` integriert. Alle fünf ausgewählten
Main-Workflows auf `3fea838a999c4576cc53a706567624aa280f0c3b` bestanden;
Tree-Identität `3118c61658aa883d48e11f437b29f39c6ae53370`, main synchronisiert,
eigener Branch lokal/remote entfernt. Methodenbranch `codex/sql2025-ai-ann-profile`
beginnt unmittelbar an dieser Basis.

Unmittelbarer nächster zulässiger Schritt nach Integration ist die enge fachliche
Methodenentscheidung für das beobachtete fehlende numerische Versionsfeld:
prüfen, ob IDX-011/IDX-012 für ausschließlich den festen Build 17.0.5005.3 ein
empirisch gebundenes Legacy-DiskANN/COSINE-/TOP_N-/UPDATE-Rejection-Profil mit
Generation UNKNOWN/WARN akzeptieren können. Kein Ersetzen unbekannter Werte durch
1/2/3, kein Azure-/anderer Buildtransfer und kein Wegfall von tatsächlicher
Plan-/Index-/Ergebnis-/Qualitäts-/Mess-/Versions-/Restore-/Cleanupabnahme.
Ein zusammenhängender Methodenentwurf und ein erforderlicher unabhängiger fachlicher
Review, höchstens eine kohärente Korrektur; keine neue SQL-/Provider-/Hostwirkung.
Bei fachlicher Annahme eigene stabile Entscheidung via zentraler Registry und
scopebezogene Aktualisierung der beiden Demoentwürfe; keine globale Framework-
Lockerung. Die Nutzerfreigabe umfasst notwendige weitere lokale Schritte dieser Welle.
Der konkrete [Profilentwurf](SQL_SERVER_2025_AI_ANN_PROFILE_DECISION.md) behält
Generation UNKNOWN/WARN und alle anderen Abnahmegates, keine neue Runtime.
DEC-074 ist vom zentralen Semantiktool bei leerer PR-Reservierungslage abgeleitet
und mit PR168 final integriert. Der erforderliche enge fachliche
Review schloss vor Registrierung ohne offene P1/P2: funktionale Qualifikation
benötigt keine erfundene numerische Generation, alle anderen Gates bleiben Pflicht.
Die Registry enthält den neuen vollständigen UUID-Datensatz; 265 Artefakte bestanden
zentrale Semantik-/projektbezogene Kennungsvalidierung. DECISIONS, beide Demoentwürfe
und der Workstreamplan wenden ausschließlich den begrenzten DEC-074-Pfad an.
Keine neue lokale Runtime und keine unveränderten Diagnosewiederholungen.
PR168-Head 26dee8d6b3d3fb5633e220a15cf62b27d91948ef gegen Base
3fea838a999c4576cc53a706567624aa280f0c3b bestand alle 42 gewählten Checks.
Squash 40159404acb1b20f0f69072f9e52664f2593bd86 bestand alle acht gewählten
Main-Workflows einschließlich der konservativ ausgewählten Legacy-Matrizen.
Vollständiger Tree e90913ccb9b56924b23fc51aba11327963f57301 wurde unabhängig
als identisch bestätigt; lokales main per Fast-forward synchronisiert und eigener
Arbeitsbranch lokal/remote entfernt. Keine Abnahme der pausierten Workstreams
oder der öffentlichen ANN-Demos aus diesen Integrationsprüfungen.

Unmittelbarer nächster Implementierungsschnitt nach Profilintegration ist die
öffentliche IDX-011-Demo mit dokumentiertem DEC-074-Profil, vollständigem Ergebnis-/
Qualitäts-/Filter-/Plan-/Benchmark-/Versions-/Recoveryvertrag. Höchstens zwei
kohärente Kandidaten und 16 eigene serielle Testcontainer insgesamt: je positivem
stabilem Kandidaten zweimal 2025-Happy-Path, je zweimal 2019/2022-SKIP_VERSION vor
Setup und zwei eigene 2025-Abbruch-/Recoveryproben nach Setup bzw. nach Indexbau.
Nur nachweislich verfügbare eigene lokale Images, keine Downloads/Hoständerungen.
Unveränderte 1000-Row-VECTOR(3)/K=5-/4CPU-/6GiB-/DB-Preview-/MAXDOP-/300-Sekunden-/
60-Sekunden-Cleanupgrenzen; Marker, tatsächliche duale Baselines/Restores und
separate DB-/Containerabwesenheit bleiben Pflicht. Benchmark vor SQL konkret
einfrieren: je Pfad fünf ausgeschlossene Warm-up-Requests und drei Reihenfolgeblöcke
AB/BA/AA, identische Ergebnisablage, keine Cacheleerung; fixe Batchgröße im konkreten
Implementierungsvertrag begrenzen. Active-Request- und Zeit-/Workergrenzen sichtbar,
keine unbewiesene Speedupratio oder generische Indexnutzung. Betroffene lokale Tests,
erforderlicher unabhängiger tatsächlicher Quellen-/Methodenreview und aktuelle Head-/
Main-Gates, Synchronisierung sowie eigener Cleanup schließen den Schnitt vollständig.
IDX-012-DML/Freshness und Provider-/Cloud-/ONNX-Gates bleiben eigene Schritte.

Der erste begrenzte Offline-Teil des öffentlichen IDX-011-Schnitts bereitet den
[Benchmark-Auswertungsvertrag](SQL_SERVER_2025_AI_IDX011_BENCHMARK_CONTRACT.md)
vor: fünf getrennt attestierte Warm-up-Requests je Pfad und 18 serielle Fenster
in drei AB-/BA-/AA-Blöcken mit je 100 Queries. Jede Query hat eigene vollständige
Rows-/Distanz-/Recallprüfung; AA und Warm-ups werden nicht in den A/B-Vergleich
gerechnet. Tatsächliche Counter-/UTC-Grenzen und vollständige Requestbindung,
unabhängig attestierte Ziel-DB-ID und chronologische nicht überlappende Fenster
verhindern falsche Serien- oder Qualitätsclaims. Zwölf synthetische Gegenproben
bestanden. Keine SQL-Ausführung, kein verbrauchter öffentlicher Runtimekandidat
oder Container und keine TP-PERF-/Demoabnahme. Quellen-/Plan-/Memory-/Spill-/
Buildkosten-/Versions-/Recoverygates bleiben offen; runtime_qualification ist
NOT_ESTABLISHED. Ein Owner, ein notwendiger konkreter Quellenreview und eine
kohärente Korrekturwelle für die zeitliche Serienbindung; der unabhängige enge
Quellenreview schloss ohne offene P1/P2. Demo-Ausführungspfade und zehn betroffene
Selector-Gegenproben bestanden. PR169-Head
2f8b7394eac4a8c3f2f754a8528cf8209492e072 gegen Base
40159404acb1b20f0f69072f9e52664f2593bd86 bestand 44 gewählte Checks;
der statisch ausgewählte KI-Runtimejob war SKIPPED/NOT_APPLICABLE.
Squash 87102e8fa022d4b7a870f3d824546efef2d1f341 bestand neun Main-Workflows.
Der vollständige Tree d305e6d0afc8ec8c919a48434bc8affcfbe57dc0 war identisch;
main synchronisiert, eigener Branch lokal/remote entfernt. Die konservativ
durch die Workflowdatei ausgewählten anderen CI-Matrizen sind Integrationsgates,
keine neue Abnahme pausierter Workstreams oder der ANN-Demo.
Der anschließende öffentliche Phasencontroller und seine SQL-Quellen entstehen in
[IDX-011](../../Demos/09_AI_SQL_Server_2025/IDX-011_Exact_Approximate_Search/README.md).
Noch keine freigegebene Demo, kein manifest.json und keine TP-PERF-Abnahme.
Der konkrete Quellen-/Sicherheitsreview und die begrenzte lokale Versions-/
Fehler-/Recoverymatrix sind im
[öffentlichen Runtimebefund](SQL_SERVER_2025_AI_IDX011_RUNTIME_REVIEW.md) belegt:
fünf P2 vor SQL geschlossen; Kandidat 1 FAIL_RESULT_CONTRACT nach vollständiger
Quellenaufnahme wegen eines falschen Python-Rundungsoracles, keine Index-/Suchphase.
Vollständiger vorhandener Output und enger unabhängiger Review bestätigten die
rationale Oraclekorrektur ohne Toleranzlockerung. Kandidat 2 erfüllte mit stabiler
Quelle alle acht seriellen Lifecycle-Erwartungen: zwei vollständige 2025-Läufe,
je zwei 2019-/2022-SKIP_VERSION vor Setup und kontrollierte Fehler nach Setup
bzw. Indexbau/vor Suche mit vollständiger Recovery. Neun eigene Container
insgesamt, alle abwesend, keine Downloads/Host-/Fremdmutation.
Je vollständigem Lauf 1810 tatsächlich einzeln geprüfte Benchmarkqueries,
minimales Recall@5 1,0; enge Filterprobe weiterhin null ANN-Rows/Recall 0.
Eigener tatsächlicher repräsentativer Indexplan und Exact-Fallback bestanden.
Beide Baselines/Restores 0/0; unabhängige Attestation vor Drop und DB-Abwesenheit.
Generations-/Memory-/Spill-/Worker-/DOP-/Rollen-/Hard-Abortgrenzen bleiben sichtbar,
keine TP-PERF- oder vollständige Demoabnahme. Betroffene Offlinegegenproben:
zwölf Controller-, zwölf Benchmark- und zehn Selectorprüfungen bestanden.
PR170-Head 159a68d849d91eaf4d2049e86ed361cef49393c4 gegen Base
87102e8fa022d4b7a870f3d824546efef2d1f341 bestand alle 48 Checks. Squash
fa17e414a75a362122a2977b39fb3d3fde577977 bestand alle zehn gewählten Main-Workflows;
vollständiger Tree f842bbb192e705d4aabf57295fa5c14d4a50d8e1 identisch.
main synchronisiert, eigener Branch lokal/remote entfernt. Der geänderte
Demo_Catalog-Pfad wählte W-COV/OPT-017 konservativ; diese Integrationsmatrizen
sind keine ANN-Abnahme und keine Wiederaufnahme pausierter Workstreams.
Unmittelbar folgt der reine Parserzusatz für fehlende Evidenz aus den beiden
neu vorhandenen tatsächlichen Plänen: eigene Statement-/Build-/Indexbindung,
rohe MemoryGrantInfo-/DOP-Attribute, fehlende Warnings/WaitStats bleiben
NOT_CAPTURED. Zwölf synthetische Gegenproben und der reine Replay beider
vollständigen Rohquellen bestanden bei unveränderten bisherigen Planassertions;
enger unabhängiger Methodenreview ohne offene P1/P2. Kein weiterer SQL- oder
Containerlauf und keine still erweiterte Runtimequalifikation. Konkrete Werte
stehen im öffentlichen Runtimebefund. PR171-Head
8991a2134e9d9966d81cdf63932aaa5e1c28fe7b gegen Base
fa17e414a75a362122a2977b39fb3d3fde577977 bestand zehn gewählte Headchecks.
Squash 8ce53d59f051ab385935ba9319fa5033f2fcb179 bestand alle vier gewählten
Main-Workflows; vollständiger Tree 0cd96e297a2f7b68ae8510b9f0a16ba7517bab4c
identisch. main synchronisiert, eigener Branch lokal/remote entfernt.

Unmittelbar folgt die eigene IDX-012-DML-Grenzenvorstufe auf
codex/sql2025-ai-dml-boundary, Basis 8ce53d59f051ab385935ba9319fa5033f2fcb179.
Sie nutzt die weitere ausdrückliche lokale Wellenfreigabe und hält bisherige
Budget-/FAIL-Historie unverändert. Neuer endlicher Umfang: höchstens zwei kohärente
Kandidaten/vier eigene serielle 2025-Container, zwei Lifecycles je positivem
stabilem Kandidaten; ein Owner und ein erforderlicher enger Quellenreview vor SQL.
17.0.5005.3, float32 VECTOR(3), vier CPUs/sechs GiB, eigene IDX-012-Marker/DB.
999 Ausgangsrows mit bisheriger Rezeptur; vier feste positive DML-Kontrollen vor
Indexbau und dieselben vier Operationen danach. UPDATE/DELETE/MERGE betreffen
Id 23, gültiger INSERT betrifft die fehlende Id 1000; höchstens 1000 Rows auch
innerhalb der Transaktion. Alle Änderungen werden zurückgerollt, vollständige
Quellbytes, tatsächlicher Transaktionssnapshot und Indexmetadaten nachkontrolliert.
Eine neue Verbindung prüft sämtliche 999 tatsächlichen Vektoren/Distanzen und
vollständige Snapshots. Erwartete feste Indexverweigerung 42231/State 1 muss
tatsächlich beobachtet werden; andere Resultate sind FAIL mit Rohbefund.
Keine zusätzliche Scoped-Option; nur eigene Preview/MAXDOP mit Originalbaselines,
300 s einschließlich Startup sowie 20 s SQL-Recovery im gemeinsamen 60-s-Cleanup.
Keine neue Benchmarkserie, kein Cloud-/Modell-/ONNX-Aufruf, kein Pull und keine
Host-/Fremdänderung. Der [konkrete DML-Grenzenbefund](SQL_SERVER_2025_AI_IDX012_DML_BOUNDARY_REVIEW.md)
belegt den unabhängig geschlossenen Quellenreview und beide vollständigen Lifecycles
des ersten unveränderten Kandidaten: CDC97E68E2114CE5 und 63AD6D8A17CE4FE9.
Je vier tatsächliche positive DML-Kontrollen ohne Index und vier Verweigerungen
42231/State 1 mit Index, vollständige 999-Row-Quellen-/Indexmetadatenprüfung,
tatsächliche Originalrestores 0/0 und separate DB-/Containerabwesenheit bestanden.
Buildwandzeiten 801,053/1130,006 ms, gesamter Cleanup 12,180/13,164 s.
Beide Admissionen geschlossen, zwei Container verbraucht, kein Runtime-FAIL.
Generation UNKNOWN/WARN, Freshness NOT_TESTED und Runtimequalifikation
NOT_ESTABLISHED; Storage-, Minimalrollen-, Versions- und Hard-Abort-Abnahme offen.
Zwölf Controller-, elf DML-Evidenz- und zehn Selector-Gegenproben bestanden;
anfängliche reine Fixture-Dateinamenfehler bleiben im Befund dokumentiert.
PR172-Head 2b31bd62333530c33d72e38ef1dafad9f842577d gegen Base
8ce53d59f051ab385935ba9319fa5033f2fcb179 bestand alle 13 Checks. Squash
a661ad0e3ac206beb66535c59bfb1512066b6c4a bestand alle sieben tatsächlich gewählten
Main-Workflows; vollständiger Tree 0e525a467777880e55d5fd4f66841d96e01464e7 identisch.
main synchronisiert, eigener Branch lokal/remote entfernt, alle Runtimegates beendet.

Unmittelbarer Folgeschritt: eigener IDX-012-Drop-/Änderungs-/Rebuildmodus auf
codex/sql2025-ai-idx012-rebuild, Basis a661ad0e3ac206beb66535c59bfb1512066b6c4a.
Neues eigenes Budget: höchstens zwei kohärente Kandidaten/vier serielle eigene
2025-Container, zwei vollständige positive Lifecycles am stabilen Kandidaten.
Die weitere ausdrückliche lokale Wellenfreigabe deckt diesen isolierten Effekt:
nach bestätigtem Indexdrop exakt Id 999 dauerhaft auf [1,0,0] ändern, tatsächlichen
Commit/übrige 998 Quellen prüfen, eigenen Index erneut bauen und dieselbe feste
Cosine-Top-5-Abfrage vor/nach anhand aller tatsächlichen Quellen kontrollieren.
Keine neue Scoped-Option, Dimension, Rowzahl, Lastserie, Images oder Hosteffekte;
4CPU/6GiB, Startup im 300-s-Budget und bisherige eigene 20-/60-s-Recoverygrenzen.
Ein Owner, ein erforderlicher unabhängiger enger Quellenreview ohne offene
Methodenbefunde; vor Admission tatsächliche Promotion-/Pfad-/Hashclosure und
betroffene Gegenproben. Der private Controllerentwurf darf nicht direkt laufen.
Freshness ausschließlich OBSERVED_AFTER_REBUILD_ONLY, Generation UNKNOWN/WARN;
keine vollständige Runtime-/TP-PERF-/Storage-/Rollen-/Hard-Abortabnahme.
Historische Budgets und FAIL bleiben erhalten, kein unveränderter Retry.
Rebuild-Kandidat 1 E2EE1E999C104A0A: FAIL_EXECUTION in 50_DropRebuild vor
Batchausführung, tatsächliche Parserfehler 156/State 1 am unquotierten RowCount-
Alias und 102/State 1 an IndexCount. Vorherige DML-Kontrollen bestanden; keine
Ausführung des neuen Drop-/Commit-/Rebuildbatches. Beide Originalrestores 0/0,
separate DB-/Containerabwesenheit und gesamter Cleanup 12,671 s bestanden.
Enge Korrektur ausschließlich SQL-Aliasquotierung [RowCount]/[IndexCount];
aktuelle konkrete Reviewclosure vor geänderter Kandidat-2-Admission erforderlich.
Diese enge Closure bestand; Kandidat 2 E095EBFA02D548F0 lieferte dennoch
FAIL_EXECUTION mit tatsächlichem 42231/State 1 am UPDATE. Der Output attestiert
keinen abgeschlossenen Commit/Rebuild und keinen tatsächlich vorher erfolgten
Drop. Beide Originalrestores 0/0, separate DB-/Containerabwesenheit und gesamter
Cleanup 12,155 s bestanden. Beide Kandidaten beendet; keine weitere Admission
im ursprünglichen Budget. [FAIL-Checkpoint und konkreter Compile-Folgeschritt](SQL_SERVER_2025_AI_IDX012_REBUILD_REVIEW.md)
bereiten getrennt genau einen Kandidaten/zwei Container ohne Korrekturwelle vor:
tatsächliche No-Index-/Transaktionsaufnahme nach Drop, erst danach festes
parametrisiertes UPDATE im unteren Compile-Scope. Frühere Hypothese zur statischen
Bindung bleibt unbewiesen; Freshness NOT_ESTABLISHED. Neue Runtime erst nach
Integration dieses Checkpoints und enger Quellen-/Pfad-/Hashclosure.
PR173 ist vollständig integriert: Head 273ed98bd3592d068dc8ddbb720772205c48617a
gegen Base a661ad0e3ac206beb66535c59bfb1512066b6c4a, alle 13 Headchecks SUCCESS;
Squash efc9d0fa820e633f1159f22d7b151ac74fc5eb06, alle sieben gewählten
Main-Workflows SUCCESS. Tree f0b03f9aebfd1ed9375b59b8c53d0094f3bd889f identisch,
main synchronisiert, eigener Branch lokal/remote entfernt.
Nach tatsächlicher öffentlicher Pfad-/Hashclosure erfüllte die getrennte
Compile-Folge ihren einzigen stabilen Kandidaten mit beiden Lifecycles:
605DA945288C4E55 und 65DAFE36C86649D3. Tatsächlicher Indexcount null nach Drop,
Commit exakt Id 999 und fünf vollständige distanzgeprüfte Suchkontrollen;
Top-5 zuvor 23/40/6/63/46, danach Exact und ANN 999/23/40/6/63, Recall@5 1.
Neue vollständige Quellen-/Metadatenaufnahme bestätigte alle 999 Rows und
unveränderte übrige 998 Vektortexte. Originalrestores 0/0 und separate DB-/
Containerabwesenheit bestanden, gesamter Cleanup 12,379/12,152 s.
Erster Build/Rebuild 756,468/895,366 und 732,222/747,841 ms; keine allgemeine
Kosten-/Qualitygarantie. Generation UNKNOWN/WARN, Freshness ausschließlich
OBSERVED_AFTER_REBUILD_ONLY und Runtimequalifikation NOT_ESTABLISHED.
Alle drei bisherigen Scopeledger bleiben geschlossen, ursprüngliche FAILs
bleiben erhalten. Folgeschnitt codex/sql2025-ai-idx012-compile integriert
ausschließlich diese tatsächlich neue Dokumentation; Code unverändert.
Bei FAIL hält der Kandidat an;
ein geänderter zweiter Kandidat braucht konkreten Befund und aktuelle Closure,
kein stiller Reset. Nach zwei ungelösten Kandidaten checkpointgebundener Stop.
Build-/Storage-/DML-Folgearbeit
bleibt konkret begrenzt und checkpointgebunden; der verbrauchte Zweikandidaten-
Controllerstand wird nicht still zurückgesetzt.
Serverlogin/Pooling und ANN sind nicht abgenommen; Live-/Cloud-/ONNX-Gates bleiben
offen, KI-Heartbeat aktiv.

### Eigenständiger KI-Planungsauftrag vom 2026-10-11

Der Benutzer hat `TSK-003`, den [KI-Workstream-Plan](SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md),
zur Recherche, Planung, Registrierung, Validierung und Planungsintegration autorisiert.
Allgemeine Entwicklung bleibt **PAUSED**. `DEC-073` erweitert nur das künftige Curriculum.
`CUR-013`–`CUR-022`, `TSK-004`–`TSK-014` und 18 Demoentwürfe sind keine begonnenen
Implementierungen und erhalten durch Registrierung keine Ausführungsfreigabe.

Planungsbasis war der saubere, mit origin/main identische Commit
`113648c4884fe788797c5f0c3788a54f74ecfc9c`; zu diesem Zeitpunkt waren keine offenen PRs vorhanden.
Eigener Branch: `codex/sql2025-ai-workstream-plan`. Aktuelle Head-/Base-, Prüf-, Review-
und Mergebelege werden im zugehörigen Planungs-PR geführt. Historische Runtimeprüfungen
werden nicht als KI-Evidenz übernommen. Bestehende DGN-007-/Pauseabschnitte und ausdrücklich
zurückgestellte Arbeiten werden durch diesen Auftrag nicht wieder aufgenommen.

Wiederaufnahme benötigt einen gesonderten Implementierungsauftrag mit gewähltem Erstumfang.
Cloud/Bezahl-API, ONNX/Instanzänderung und Previewpfade benötigen zusätzlich die benannten
konkreten Freigaben. Der damalige Planungsauftrag erlaubte keine Automation;
die spätere ausdrücklich freigegebene Implementierung und der oben benannte
Heartbeat ersetzen diese historische Grenze ausschließlich für den KI-Workstream.

### Verbindlicher Abschlussumfang vom 2026-10-10

Der Benutzer hat die Methodenänderung ausdrücklich freigegeben und danach
einen zügigen Abschluss verlangt. `DEC-072` ersetzt für diesen begrenzten
Schulungslauf die notwendige exakte QS↔SYSUTC-Klammer durch Diagnose ohne
Puffer. Die Query-Store-Intervallauswahl verlangt tatsächliche reguläre
Erfassung des separat markierten Pollqueries. Tatsächliche Requests,
Ergebnisse, Intervall-IDs, vier reguläre Suchausführungen je Fenster,
Planfamilien, Budgets und unabhängiger Cleanup bleiben maßgeblich.
Der v2-Vertrag und Decoder erhalten die Originalzeiten; historische
v1-Evaluatorregeln werden nicht umgedeutet. Unterschiedliche Starts sind erlaubt.

Der ursprüngliche Reporter ist kein nachgewiesener Reporterfehler. Sein
Fehler-only-Pfad ist durch diese Korrektur überholt: vorhandene Rawdiagnose
und die vollständigen skalaren Capture-Zeitwerte decken den begrenzten
Diagnosebedarf ab. PR 68 wird deshalb begründet verworfen. Die nutzbare
Rawdiagnose aus PR 128 ist bereits durch PR 130 integriert; verbleibender
Reportercode wird aus demselben Grund verworfen. PR 132 enthält den finalen
Parser-/Methodenschnitt und wird nur nach aktueller relevanter CI integriert.
Anschließend werden diese drei zugehörigen Branches nach geprüftem Abgleich
beziehungsweise begründeter Verwerfung und lokaler Sicherung bereinigt.

Weitergehende Provenienz-, Collector-, SESSION_END- und Capstonearbeiten
bleiben ausdrücklich zurückgestellt. Sie sind keine Abschlussbedingung dieses
begrenzten Diagnoseschnitts. Frühere Aussagen zu unverändertem G13 oder noch
fehlender Methodenfreigabe in den folgenden historischen Abschnitten sind
durch diesen Abschnitt und `DEC-072` ersetzt. Historische FAILs bleiben gültig;
der frühere SQL20-Countfehler ist ohne eigene Fehlrohwerte nicht abschließend
erklärt und wird durch einen späteren PASS nicht rückwirkend widerlegt.

Der Benutzerauftrag vom 2026-10-09 nimmt gezielt die Prüfung und den Abschluss
der bestehenden Reporterarbeit in PR 68 wieder auf. Der
[G13-/PR-Review](DGN_007_G13_PR_REVIEW.md) trennt den nützlichen Diagnoseschnitt
von der offenen Methodenänderung und dokumentiert Ursache, Quellenprüfung,
Bestandsabgleich sowie die aktuellen Abschlussbedingungen. Integration verlangt
erfolgreiche relevante CI am aktuellen Head/Base; historische G13-Fehler bleiben
gültig. DEC-069 macht Integration und eigene Branchbereinigung zum Arbeitsabschluss.
Die neue CI am Head `f9ec582…` scheiterte auf 2022 an der SQL20-Abnahme
von vier erfassten Ausführungen je Fenster und auf 2025 an G13 (−0,8298 ms).
Beide ersten DB-Abwesenheitsprüfungen und die eigenen Containerabbauten bestanden.
Der vorherige Matrix-PASS ist keine Freigabe dieses fehlgeschlagenen Heads.
PR68 ist für die getrennte Integration von Prüfbericht und Abschlussprozess
vorübergehend geschlossen; nicht übernommener Code und Branch bleiben konkret
referenziert erhalten. Der aktuelle Benutzerauftrag autorisiert zusätzlich die
begrenzte Ursachenanalyse und Korrektur der Erfassungs-/Zeitgrenzenfehler innerhalb
der bisherigen Methode sowie das getrennte Foundation-Upgrade auf `1.20.0` und
die Prozesskorrektur gemäß `DEC-070`. Die frühere Scopeanfrage ist damit erledigt;
eine materielle Methodenänderung bleibt ein eigener erläuterter Entscheid.
Kein Bypass oder Wiederholen bis grün.
Allgemeine Entwicklung, Automation, SESSION_END und die ausdrücklich
zurückgestellte interne Capture-Rückgabe bleiben pausiert.

Der begrenzte Korrekturscope ist im
[aktuellen Reviewabschnitt](DGN_007_G13_PR_REVIEW.md#begrenzter-korrekturscope-nach-foundation-1200)
abgeschlossen dokumentiert: ein lokaler `profile-comparison`-Lifecycle auf SQL
Server 2022 `16.0.4265.3` und ein `control-ba`-Lifecycle auf SQL Server 2025
`17.0.4075.5` bestanden ihre Phasen und beide ersten unabhängigen Cleanupchecks.
Sie reproduzierten die CI-Fehler nicht; es liegt **keine belegte Reparatur** vor.
640,324 s lokale Gesamtwalltime einschließlich fehlgeschlagenem Readinessvorlauf
und eigenem Cleanup; keine Unteragenten, identische Wiederholung oder zusätzliche
SQL-Matrix. Reporter-Head/Branch `f9ec582…` bleibt erhalten und `BLOCKED`.

Wiederaufnahmebedingungen: im tatsächlich fehlgeschlagenen SQL20-Pfad begrenzte
Counts-/Familien-/Rawaufnahme vor Cleanup und eine daraus abgeleitete Gegenprobe;
bei G13 positive/Zero-Rawfragmente desselben Fehlerfalls sowie belastbare
QS↔SYSUTC-Evidenz oder eine ausdrückliche neue Methodenentscheidung. Empfehlung:
G13 zunächst exakt erhalten und die fehlenden Fehlerbelege nachholen. Der Benutzer
hat diese Abnahmerichtung am 2026-10-09 ausdrücklich ausgewählt. Die Methoden-
alternative bleibt ungewählt; kein Puffer, keine Rundung und keine Capänderung
ist aktiviert. Die begrenzte Fehleraufnahme ist inzwischen in PR 130 implementiert, hat aber
noch keinen echten CI-Fehler erfasst. Erst ein belegter Fix mit erforderlichen
aktuellen Head-/Base-Checks erlaubt den Reporter-Merge.

### DGN-007-Diagnose und Abschlussgrenze vom 2026-10-10

Der erneute ausdrückliche Benutzerauftrag nahm ausschließlich DGN-007 zur
autonomen Bearbeitung wieder auf; allgemeine Entwicklung, SESSION_END, interne
Capture-Rückgabe und die pausierte Automation bleiben ausgenommen. Der erhaltene
Reporter wurde in [Draft-PR 128](https://github.com/gecompat/SQL_PerformanceSchulung/pull/128)
auf dem Branch `codex/dgn007-failure-evidence` mit einer ausschließlich im echten
SQL20- beziehungsweise G13-Fehlerzweig aktiven, auf 16 skalare Rohzeilen
begrenzten Diagnose kombiniert. Viererabnahme, G13, Requests, Polling und
Budgets sind unverändert. Nach einer korrigierten SQL-Syntaxstelle bestanden je
ein instrumentierter lokaler `profile-comparison`-Lifecycle auf SQL Server 2022
und `control-ba` auf SQL Server 2025 samt unabhängigen Cleanupprüfungen. Diese
beiden Läufe reproduzierten die Fehler nicht.

Die einzige aktuelle [PR-Matrix 38045921184](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38045921184)
am Head `657bbb22759cfbf27e5fbbfbf63e3660a885b3b2` gegen Base `0601361…`
bestand alle statischen Gates und die vollständigen SQL-Jobs auf 2019, 2022 und
2025. Je Version erreichte der Runner die sechs Scopes mit zwei Lifecycles;
Cleanup und Containerabbau sind im Job erfolgreich abgeschlossen. Weder der
frühere SQL20-Countfehler noch G13 trat auf. Ein aktueller PASS ist deshalb
**keine belegte Korrektur** der fehlgeschlagenen [Matrix 37892941746](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37892941746).
PR 128 bleibt Draft/`BLOCKED`; der Reporter-Code ist nicht in `main`.

Weiter fehlen die tatsächlichen SQL20-Ist-Counts samt Familien-/Rawzustand aus
einem fehlgeschlagenen Lauf und bei G13 die positiven/Zero-Rohfragmente derselben
fehlgeschlagenen Acquisition sowie ein belastbarer QS↔SYSUTC-Zeitquellenbeleg.
Die gewählte exakte G13-Abnahme bleibt bestehen. Wiederaufnahme braucht einen
authentischen Fehlerfall mit diesen begrenzten Belegen und eine daraus abgeleitete
Gegenprobe; eine alternative kollektive Zuordnung verlangt zuvor die ausdrückliche
Methodenentscheidung und ihre offenen Gates aus dem
[Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md). Keine weitere
unveränderte Matrix und keine Reporter-Integration allein aufgrund des PASS.
Der alte PR68-Branch `codex/dgn007-g13-boundary-report`, der Draft-Branch aus
PR 128 und die ausdrücklich zurückgestellte lokale interne Capturearbeit bleiben
wegen nicht übernommener Änderungen erhalten.

### Integrierter Rohdiagnoseschnitt; Reporter weiterhin blockiert

[PR 130](https://github.com/gecompat/SQL_PerformanceSchulung/pull/130) hat nur
begrenzte Rohdiagnosen in die bereits vorhandenen SQL20-/SQL21-Countfehler- und
SQL35/G13-Fehlerzweige übernommen. Die spätere Query-Store-Rohsicht ist keine
atomare Wiederholung der gespeicherten Profilaufnahme. Sie gibt höchstens
16 skalare Zeilen sowie bei SQL20 beide Fenster-Counts aus; Overflow,
Abfragefehler oder ungültige Records bleiben ausdrücklich unzureichende
Diagnose. Requests, Viererabnahme, exakter G13-Guard, Polling, Caps und
Cleanuppriorität sind unverändert. Der Grenzabstands-Reporter aus Draft-PR 128
ist nicht enthalten.

Die einzige aktuelle [PR-130-Matrix](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38048742623)
am Head `177b1b72341debce9dbc43432259dccffae919f1` gegen Base
`0e71067c2a86d9e866b705fdefaf7dd9f914f397` bestand auf SQL Server
2019/2022/2025 je sechs Scopes mit zwei Lifecycles (36 insgesamt). Alle
36 unabhängigen Datenbank-Cleanupchecks und die drei Containerabbauten
bestanden. Auch Privacy, Registry, Governance, Offline-Bundle und die
betroffenen statischen DGN-007-Checks waren grün. Der Squash-Merge
`aea230fb65798afddd4643c92b84f09403819ec6` hat denselben Tree wie der
geprüfte Head; lokales `main` ist mit `origin/main` synchronisiert. Der eigene
vollständig übernommene Diagnosebranch wurde lokal und remote entfernt.

Keiner der zwei alten Fehler trat in dieser Matrix auf. Tatsächliche SQL20-
Ist-Counts aus einem Fehllauf und positive/Zero-Rawfragmente des SQL-2025-
G13-Fehllaufs fehlen weiter; eine neue Query-Store-Abfrage wäre zudem kein
atomarer Beleg der ursprünglichen Profilaufnahme. Die beobachteten G13-
Grenzverletzungen und eine frühere positive Count-4-Rohzeile widerlegen eine
allgemeine Zero-Count-Erklärung, beweisen aber noch keine zulässige
Zeitquellengrenze. PR 128 bleibt Draft/`BLOCKED`, PR 68 geschlossen mit
erhaltenem Codebranch, die interne Capturearbeit pausiert. Wiederaufnahme:
authentischen fehlgeschlagenen Lauf mit Counts, Rohzeilen und Zeitwerten
gezielt auswerten, daraus eine ursachenbezogene Gegenprobe ableiten und den
exakten G13-Vertrag beibehalten. Falls dies innerhalb des Vertrags nicht
möglich ist, braucht die kollektive Zuordnung eine neue ausdrückliche
Methodenentscheidung mit den offenen Gates des Entscheidungspakets. Kein
weiterer unveränderter Matrixlauf und kein Reporter-Merge allein wegen PASS.

### Neue G13-Fehler nach der Diagnoseintegration

Der [Main-Push-Lauf 38050043409](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38050043409)
am Code-Merge `aea230f…` scheiterte auf SQL Server 2019 in
`CONTROL_AA / RUN_2` an G13. Der Fehlerpfad lieferte
`G13_RAW|INSUFFICIENT|MALFORMED`; die privaten Rawzeilen dieses Laufs sind
nicht rekonstruierbar. 2022 und 2025 bestanden. Alle drei Containerabbauten
und beim Fehllauf der unabhängige Datenbank-Cleanup bestanden. Eine einmalige
isolierte SQL-Server-2019-Formatprobe zeigte die tatsächliche UTC-Ausgabe von
`CONVERT(varchar(40), SWITCHOFFSET(...), 127)` mit abschließendem `Z`.
Der integrierte Decoder hatte `Z` ausgeschlossen. Die eigene Probeninstanz
wurde nach Identitätsprüfung entfernt. Dies belegt den Diagnose-Parserfehler,
nicht die Ursache der G13-Zeitverletzung.

Die darauf begrenzte UTC-Z-Parserkorrektur in
[Draft-PR 132](https://github.com/gecompat/SQL_PerformanceSchulung/pull/132)
am Head `440bfd909ef9ffe59a30ad3aa13c4d57c578b234` gegen Base `0045432…`
bestand lokal die betroffenen Tests, Privacy und das CPython-3.12-Kantenprofil.
Die einzige neue [PR-Matrix 38051475267](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38051475267)
bestand auf 2019 und 2025, scheiterte aber auf SQL Server 2022 in
`CONTROL_BA / RUN_1` an G13. Der korrigierte Decoder lieferte erstmals einen
vollständigen begrenzten Rohblock: Fenster 0, Parent/Query 12, Plan 16,
Intervall 2, Type 0, Count 4, First `12:32:00.2930000Z`, Last
`12:32:00.6570000Z`; Fenster 1, Parent/Query 12, Plan 2, Intervall 3,
Type 0, Count 4, First `12:33:00.8500000Z`, Last `12:33:01.2200000Z`.
Zero-Rawzeilen wurden in diesem begrenzten Block nicht gemeldet. Der
unabhängige Datenbank-Cleanup und alle drei Containerabbauten bestanden.
Der CI-FAIL sperrt PR 132 und bestätigt keine Reporterfreigabe; weder sein
Code noch der Reporter aus PR 128 sind in `main`.

Für SQL20 fehlen weiterhin die Ist-Counts und Rohdaten eines echten
Countfehlers. Für den neuen G13-Fehler fehlen die gespeicherten
`ExecutionStarted`-/`ExecutionFinished`-Werte und ein belastbarer Beleg zur
QS↔SYSUTC-Zeitquellengrenze; der spätere Raw-Read ist kein atomarer Snapshot.
Die zweimalige positive Count-4-Rohsicht schließt Zero-Counts als allgemeine
Erklärung aus. Die vom Benutzer gewählte exakte G13-Abnahme bleibt gültig.
Wiederaufnahme verlangt eine ursachenbezogene, begrenzte Gegenprobe mit
vollständigen Zeitgrenzen oder eine gesonderte materielle Methodenentscheidung
nach dem vorhandenen Entscheidungspaket. Keine weiteren unveränderten
Matrixläufe, kein Bypass und keine stillschweigende Rundung oder Pufferung.
PR 132 und sein Branch bleiben wegen nicht übernommener Parserkorrektur erhalten;
PR 128, der alte PR68-Branch und die pausierte interne Capturearbeit ebenfalls.

### Aktueller Gegenbefund zur Zeitklammer

Der neue Auftrag „weiterführen“ setzt die gezielte DGN-007-Ursachenprüfung fort.
Die [isolierte Zeitquellen-Gegenprobe](DGN_007_G13_PR_REVIEW.md#isolierte-zeitquellen-gegenprobe-vom-2026-10-10)
auf SQL Server 2022 `16.0.4265.3` erfasste 32 synthetische Abfragen genau einmal
je Query. Bei 31 lag der QS-First-Wert vor dem zuvor gemessenen SYSUTC-Start,
maximal um 7,5996 ms. Das ist ein Gegenbeleg zur exakten gemeinsamen Zeitklammer
in dieser Umgebung, keine allgemeine Clock-Erklärung und keine SQL20-Countreparatur.
Beide eigenen Probeninstanzen und Datenbanken sind unabhängig abwesend geprüft.
Der konkrete Ersatz der QS↔SYSUTC-Beweisart durch nachzuweisende Ausführungs-/
Intervallzuordnung ist zur ausdrücklichen Methodenentscheidung vorgelegt.
G13 und die Integrationssperre bleiben bis dahin unverändert. Ein zusätzlich
belegter UTC-Formatfall ohne Sekundenbruch ist im lokalen PR-132-Kandidaten
abgedeckt; kein neuer unveränderter Matrixlauf wurde gestartet.

Am 2026-10-08 hat der Benutzer angewiesen, keine neuen Aufgaben zu beginnen,
alle laufenden Arbeiten konsistent abzuschließen und anschließend diesen
Orchestrator samt Subagents zu beenden. Die bestehende Automation
`sql-performanceschulung-autonome-entwicklung` ist per App auf `PAUSED` gesetzt.
Ausschließlich der bereits vollständig entworfene und unabhängig geprüfte
Loaderrecordvertrag §33 sowie dieser Pausenstand werden in der laufenden PR-Runde
abgeschlossen. Danach folgen erfolgreiche aktuelle CI, Merge nach `origin/main`,
Main-Synchronisierung und unabhängig geprüfter Cleanup des übernommenen eigenen
Arbeitsbranches; keine neue Aufgabe und kein automatischer Chatwechsel.

Wiederaufnahme erfordert einen neuen ausdrücklichen Benutzerauftrag. Dann zuerst
die aktuelle AGENTS-Kette, relevante Regeln, Main, offene PRs, Branches und diese
kanonischen Pläne abgleichen. Erst danach ist der separate SESSION_END-DESIGN-
Vertrag der nächste geplante Schnitt; die vorbereitende Agentenanalyse wurde
beim Benutzerstopp unterbrochen und ist keine implementierte oder dauerhafte
Projektwahrheit. §33 ist ausschließlich DESIGNED: keine halbe ausführbare Demo,
keine operative Promotion und kein zusätzlicher Runtime-/Absenzbeleg. Die offene
G13-/Methodenarbeit in PR 68 und die unübernommene lokale interne Capturearbeit
bleiben aus den unten dokumentierten Gründen erhalten; sie dürfen weder blind
zusammengeführt noch als unbenötigt gelöscht werden. External-/Graph-Table-P2
bleibt im Backlog. PR- und Cleanupabschlussbelege werden im zugehörigen PR ergänzt;
der Basisstand in der Tabelle bleibt eine überprüfte Vorgängerversion.

Historie der vorherigen Wiederaufnahme (durch den aktuellen Stopp abgelöst):

Am 2026-10-07 wurde die allgemeine Verarbeitung ausdrücklich mit den bisherigen
Regeln wieder aufgenommen. Die bestehende 30-Minuten-Automation ist wieder
`ACTIVE`; es wird keine zweite Automation und kein neuer Chat erzeugt. Der
aktuelle nächste Scope bleibt die Importvorbereitung. Der getrennte
[Darstellungs- und Digestentwurf §10](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#10-vollständig-erhaltender-darstellungs--und-digestentwurf)
beschreibt eine feste verlustfreie Positionsdarstellung samt separater künftiger
Digestbindung bei unveränderten Inhalten und Caps. Dies ist `DESIGNED`, kein
implementierter Codec und keine v1-Migration. Der separate
[vollständige Fixture-/Größennachweis §11](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#11-separat-ausgewählte-vollständige-bootstrapfixture)
enthält 85 vorab gewählte vollständige Records und deren exakte Gegenaufnahme.
Die gemeinsame Metadata beträgt 17.127/17.113/17.091 Bytes einschließlich Header
und überschreitet das unveränderte 16.384-Byte-Cap bei allen drei Ordinals;
sämtliche anderen Formen passen. Neuer reiner Sizer mit 34/34 Gegenproben und
Legacy27/40 ohne SKIP. Dies ist ein negativer vollständiger Entwurfsnachweis,
keine operative Sollinventur, Codec-, Worker-, Trust- oder UsedBytesattestation.
Der getrennte [verlustfreie Stringpoolentwurf §12](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#12-verlustfreier-stringpoolentwurf)
liegt als `DESIGNED` vor: eigene Hülle und lokaler Pool je Form, vollständige
Positionen, Werte und Arrayvorkommen, höchstens 256 Poolwerte und sämtliche
bisherigen Caps. Der eigene [reine Pool-Sizer und vollständige Größenbeleg §13](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#13-separater-reiner-stringpool-sizer)
ist implementiert und unabhängig geprüft: 37/37 isolierte Gegenproben ohne SKIP,
vollständige neue 3×5-Rechnung mit derselben vorgewählten Fixture und dem
Originalrahmen. Alle 15 Formen passen einschließlich Header, maximal 9.389 Bytes;
Poolanzahlen je Ordinal 204/202/17/172/32. Unabhängige Nachrechnung und vollständige
Feldrückgewinnung bestätigt, keine neue Aufnahme oder Nonce. Dies ist ausschließlich
ein positiver Design-Größenbeleg für diese Kontrollfixture, keine operative
Workerbaseline. Der eigene experimentelle Codec-/Digestpfad steht in
[§14](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#14-separater-experimenteller-formcodec-und-design-digests);
41/41 isolierte Gegenproben ohne SKIP, unabhängiger Quell-/Testreview und die
vollständige Originalfixture mit 3×5 Frames, vollständiger Feldrückgewinnung,
kanonischem Repack und neun eigenen Digestwerten bestanden. Die Gesamtausgabe
beträgt 28.264/28.257/28.246 Bytes. Ein unabhängiger Nachreview rechnete sämtliche
Frames und Digests aus den unveränderten Eingaben nach, ohne Codec-/Helper-Replay.
Keine neue Aufnahme oder Nonce. Der eigene reine
[kombinierte Eingangsprototyp §15](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#15-separater-experimenteller-kombinierter-eingangsrahmen)
bestand 34/34 isolierte Gegenproben ohne SKIP und den neuen vollständigen
Originalfixturebeleg: drei Frames zu jeweils 140.226 Bytes einschließlich
9.389 Metadata-/Headerbytes und 130.837 unveränderten Rawbodybytes.
Tatsächliche vollständige Feld-/Rawbyterückgewinnung, Repack und unabhängige
Stdlib-Nachrechnung ohne Replay bestanden. Keine neue Aufnahme oder Nonce.
Die konkrete operative [Bootstrap-/Kanalreihenfolge §16](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#16-konkrete-operative-bootstrap--und-kanalreihenfolge)
liegt als `DESIGNED` vor. Der reine [Kontrollbootstrapquellengenerator §17](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#17-reiner-generator-gehaltener-kontrollbootstrapquellen)
bestand 32/32 ausschließlich synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die getrennte [Sysconfig-Vorinitialisierung §18](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#18-feste-sysconfig-vorinitialisierung-gehaltener-kontrollquellen) bestand 53/53 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die private native Auswahl nach [§19](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#19-private-auswahlgrundlage-vor-einer-vollständigen-operativen-inventur) ist mit genau einem begrenzten Versuch und unabhängigem Prozess-/Record-POST abgeschlossen. Die additive reine [Inline-Metadata-Syntaxquelle §20](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#20-reine-additive-inline-metadata-syntaxquelle) bestand 80/80 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste Fixture-Label-Fehllauf bleibt getrennt dokumentiert. Die additive reine [Inline-Metadata-Semantikquelle §21](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#21-reine-additive-inline-metadata-semantikquelle) bestand nach zwei engen Fixturekorrekturen 108/108 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 106/108-Lauf bleibt getrennt dokumentiert. Vollständige deklarative M/IP/S15/P11/D9-Semantik, unveränderter benannter Originaldigest und Providerkohärenz sind geprüft. Die additive reine [Inline-Profilreporterquelle §22](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#22-reiner-additiver-inline-profilreporter) bestand im einzigen isolierten Lauf 149/149 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige Scalarprojektion, eigener REPORTED-Pool, atomare begrenzte Records und getrennte Original-/Reportdigests sind geprüft; vier frühere Builder bleiben erhalten. Die reine begrenzte [Inline-Header-/Metadata-Aufnahme §23](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme) bestand im einzigen isolierten Lauf 174/174 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Exact-Chunktype-/Größenvorläufe, vollständige deklarative M-Semantik und atomare gehaltene Rückgabe sind geprüft; fünf frühere Builder bleiben erhalten. Die additive reine [K-Domain-/Commandquelle §24](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands) bestand im einzigen isolierten Lauf 209/209 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständiger K8-/D9-Vorlauf, eigene headerfreie E4-K-Domain und atomare kanonische Commands gegen separat gehaltene Callerwerte sind geprüft; sechs bisherige Builder und 174 alte Tests bleiben erhalten. Die additive reine [Inline-Metadata-Callerquelle §25](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich) bestand nach zwei engen Fixturekorrekturen 243/243 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 241/243-Lauf mit zwei Fehlern vor Matcheraufruf bleibt getrennt dokumentiert. Beide vollständigen Formen und Semantiken, zwei eigene Originalinputdigests und vollständiger Abgleich gegen separat gehaltene I7/W6/K8 sind geprüft; sieben bisherige Builder und 209 alte Tests bleiben erhalten. Die additive reine [Inline-Rawbodyaufnahme §26](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies) bestand nach einer engen Fixturelabelkorrektur 272/272 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 271/272-Lauf bleibt getrennt dokumentiert. Vollständige Formen und Größen vor Hashes, beide tatsächlichen D9 und neun Rawhashes vor Callerabgleich sowie atomare Originalbodyrückgabe sind geprüft; acht bisherige Builder und 243 alte Tests bleiben erhalten. Die additive reine [Profilrecord-Reassemblierung §27](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords) bestand im einzigen isolierten synthetischen Lauf 304/304 Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige begrenzte Control-/Envelopeformen, interne Konsistenz, kanonische Controls und tatsächlicher Footerhash vor Callerordinal sowie atomare Originalrecordrückgabe sind geprüft; neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei enge Fixturelabelkorrekturen wurden vor dem ersten Lauf reviewt; kein ausgeführter Fehllauf. Die additive reine [Inline-Profil-Callerquelle §28](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich) bestand im einzigen isolierten synthetischen Lauf 341/341 Gegenproben ohne SKIP unter CPython 3.12.14. Beide vollständigen R4-Formen/Semantiken, Actual-Pool-Repack und vollständiger separater Callerabgleich sind geprüft; die Matchfunktion berechnet keinen SHA. Zehn frühere Builder und 304 alte Methoden bleiben erhalten. Vorreviewkorrekturen und genaue Grenzen stehen in §28. Die additive reine R→BODY_RELEASE-Planquelle aus §29 bestand im einzigen isolierten synthetischen Lauf 378/378 Gegenproben ohne SKIP unter CPython 3.12.14; elf alte Builder und 341 alte Methoden bleiben erhalten. Die additive reine INPUT_COMPLETE-Quelle aus §30 bestand im einzigen isolierten synthetischen Lauf 413/413 Gegenproben ohne SKIP unter CPython 3.12.14; zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige Record-/Footer→R-Calleradapter aus §31 ist rein additiv implementiert und im isolierten synthetischen Lauf mit 460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden bleiben erhalten. Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente) ist im isolierten synthetischen Lauf mit 66/66 PASS ohne SKIP geprüft. Reservierungen, ganze Slot-/Zustandsbindung, sticky Fehler und einmaliger Fakecleanup sind lokal belegt; kein tatsächlicher Kanal-/Loader-/Absenznachweis. Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.
Frische operative Auswahl, inline Empfang und Reporting sowie tatsächliche
Parent-/Worker-, Loader-, Consumption-, Replay- und Cleanupnachweise bleiben
getrennte Gates. Die charakterisierte Fixture ist keine operative Workerbaseline.

Der separate INPUT_COMPLETE-Recordvertrag wurde über
[Pull Request 115](https://github.com/gecompat/SQL_PerformanceSchulung/pull/115)
integriert. Alle acht PR- und sechs separaten Main-Prüfungen bestanden am
jeweiligen aktuellen Stand; tatsächliche Logs und vollständige unabhängige
Übernahme aller 797 versionierten Dateien wurden geprüft. Main ist synchron,
eigener lokaler/remote Branch und Tempref sind unabhängig als abwesend geprüft.
Squash: `dcb6f032d488dfb751329a1e71a906cd1e10ac11`. Dieser abgeschlossene
Dokumentationsschnitt führte keine lokale Suite oder private Probe aus.

Der vollständige Record-/Footer→R-Caller-Vertrag nach §31 wurde über
[Pull Request 117](https://github.com/gecompat/SQL_PerformanceSchulung/pull/117)
integriert. Acht PR- und sechs separate Main-Runs/Jobs/Checks bestanden.
Tatsächliche Checkoutlogs binden Integration
`64c4841a7abfd120b05e93d1aa73816be59d3f5a` und Squash
`665de6dd4127e3f4c3fa4fe9e9ccb7a1c1dd12e7` mit identischem Tree.
Offline bestand alle elf Suiten ohne Test-SKIP, CPython 3.12.14,
zuletzt 413/413; PR 13.058 s, Main 12.623 s. Der Dokumentationsschnitt
führte keine lokale Suite oder private Probe aus. Vollständige unabhängige
Übernahme aller 797 Mode-/Blob-Einträge, Main-FF, eigener lokaler/remote
CAS-Branch-/Tempref-Cleanup und unabhängiger POSTCLEAN sind abgeschlossen.

Die additive reine Builder14-Umsetzung nach §31 wurde über
[Pull Request 118](https://github.com/gecompat/SQL_PerformanceSchulung/pull/118)
vollständig integriert. Alle neun PR- und sieben separaten Main-Runs/Jobs/Checks
bestanden am jeweiligen geprüften Stand. Tatsächliche Checkoutlogs binden
Integration `229b233aa0a14261c1daeb5b7d7ec876b1c8c034` und Squash
`f6559e084ebd660a41a503129f1a28c32be8848b` an denselben Tree
`d39472f26b698e96b8a5d4f6fbce57107b61c75e`.
Offline bestanden alle elf Suiten ohne Test-SKIP; die letzte Suite hatte
jeweils 460/460 PASS: PR unter Ubuntu/CPython 3.12.15 in 13.436 s,
Main unter Ubuntu/CPython 3.12.14 in 15.122 s. Framework bestand separat
alle fünf Befehle, vier Evaluatortests und die tatsächliche Linux-Kindsessionprobe;
PR verwendete CPython 3.12.14, Main 3.12.15. Vollständige unabhängige Übernahme
aller 797 Mode-/Blob-Einträge einschließlich der sieben Scopepins, Main-FF,
eigener lokaler/remote CAS-Branch-/Tempref-Cleanup und unabhängiger POSTCLEAN
sind abgeschlossen. Der lokale einzelne 460/460-Lauf und seine Grenzen bleiben
unverändert in §31.6 dokumentiert.

Der separate Parent-Ledgervertrag nach §32 wurde über
[Pull Request 119](https://github.com/gecompat/SQL_PerformanceSchulung/pull/119)
vollständig integriert. Acht PR- und sechs separate Main-Runs/Jobs/Checks
bestanden am jeweiligen geprüften Stand. Tatsächliche Checkoutlogs binden
Integration `41628e2b407c18e6f32ee469149c4d9b156854d3` und Squash
`6439f03627483a0c7a73a64817898fd0cf215460` an denselben Tree
`89de4120dd4d4c1870f5abc46207021ab8ab527d`.
Offline bestand alle elf Suiten ohne Test-SKIP unter Ubuntu/CPython 3.12.14,
zuletzt jeweils 460/460; PR 14.689 s, Main 12.634 s. Der Designschnitt
führte keine lokale Suite oder private Probe aus. Vollständige unabhängige
Übernahme aller 797 Mode-/Blob-Einträge, Main-FF, eigener lokaler/remote
CAS-Branch-/Tempref-Cleanup und unabhängiger POSTCLEAN sind abgeschlossen.
Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente)
ist mit genau einem isolierten Lauf geprüft: 66/66 PASS, 0 Failures/Errors/Skips,
CPython 3.12.14, Exit 0; Unittestzeit 0,426 s, separat gemessene Prozesswall
0,5766168 s. Die nach dem Lauf gemessene Source-/Test-Paarbindung
`91f10b0e68fd9a27f53db65b6b31c295645688d7cf302fd7d8e15cc0f636347c`
blieb unverändert. Tatsächliche Harness-Sentinels für eigene Restorepatches,
Modulcache/__main__, Klassen, Funktionen und Closureinhalte bestanden.
Keine alte Suite oder private Runtime wurde lokal wiederholt. Die Komponente wurde über
[Pull Request 120](https://github.com/gecompat/SQL_PerformanceSchulung/pull/120)
vollständig integriert: neun PR- und sieben separate Main-Runs/Jobs/Checks SUCCESS,
App 15368, Attempt 1, ohne Bypass. Tatsächliche Checkoutlogs binden Integration
`86a658b27469236b5e3bfb223a19f323cb499c35` und Squash
`99af91bc8d25312b62659f6e83f29b3fd2bbcd30` an denselben Tree
`c0f2f9d4cbd1b7403f22960ec23a53b6d455eb4d`.
Alle zwölf Offline-Suiten bestanden ohne Test-SKIP unter Ubuntu/CPython 3.12.15;
Ledger 66/66: PR 0,572 s, Main 0,753 s; Builder14 460/460: PR 11,220 s,
Main 14,963 s. [PR-Offline](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37786515837/job/113342548563)
und [Main-Offline](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37787761337/job/113346816906)
liefern getrennte Nachweise. Alle 799 Pfad-/Mode-/Blob-Einträge und acht LF-Pins
wurden unabhängig vollständig übernommen; 791 Basisdateien blieben unverändert.
Main-FF, eigener lokaler/remote CAS-Branch-/Tracking-/Konfigurations-/Tempref-Cleanup
und unabhängiger POSTCLEAN sind abgeschlossen. Die Gesamtgates bleiben offen.

Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.

Die neue reine additive INPUT_COMPLETE-Quelle nach §30 ist lokal im einzigen
isolierten Versuch mit 413/413 PASS ohne SKIP geprüft. Root und unabhängiger
Reviewer lasen vorher die vollständigen finalen Source-/Testdeltas sowie
tatsächliches Run.execute und delegierten Reporter-tearDown. Die Umsetzung
attestiert keine tatsächliche Eingangsprüfung, Senderherkunft oder Consumption.
Die Umsetzung wurde über
[Pull Request 116](https://github.com/gecompat/SQL_PerformanceSchulung/pull/116)
integriert. Alle neun PR- und sieben separaten Main-Runs/Jobs/Checks bestanden;
sämtliche tatsächlichen Checkoutlogs binden die PR-Integration
`d3ec83010fdd69c923f24c4363b333534c712d30` beziehungsweise den tatsächlichen
Squash `f19e05ad51534cbd9ec4b53fd055317c8d9b9973`. Offline bestand in beiden
CI-Läufen alle elf Suiten mit 413/413 zuletzt und ohne Test-SKIP, CPython 3.12.15;
die letzte Suite dauerte im PR 12.931 s, auf Main 9.812 s. Framework prüfte
jeweils alle fünf Befehle samt vier Evaluatortests und tatsächlicher
Linux-Kindsessionprobe; PR verwendete 3.12.14, Main 3.12.15.
Vollständige unabhängige Übernahme aller 797 Mode-/Blob-Einträge, Main-FF und
eigener lokaler/remote CAS-Branch-/Tempref-Cleanup samt unabhängiger POSTCLEAN-
Prüfung sind abgeschlossen. Dieser neue Dokumentationsschnitt wiederholt
keine lokale Suite oder private Probe.

Die additive reine R→BODY_RELEASE-Planquelle wurde über
[Pull Request 114](https://github.com/gecompat/SQL_PerformanceSchulung/pull/114)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme aller 797 versionierten
Dateien, Main-Synchronisierung und eigener lokaler/remote Branch- sowie
Tempref-Cleanup einschließlich unabhängiger POSTCLEAN-Prüfung sind bestätigt.
Der Squash ist `94e06d48aecc3940e861f80b488e3423ece4cef1`.
Der lokale isolierte Einzelversuch bestand 378/378 synthetische Methoden
ohne SKIP. Dieser abgeschlossene PR 114 enthielt noch keinen INPUT_COMPLETE-
Matcher; die getrennte spätere Umsetzung und ihre Evidenz stehen in §30.

Der deklarative R→BODY_RELEASE-Vertrag wurde über
[Pull Request 113](https://github.com/gecompat/SQL_PerformanceSchulung/pull/113)
integriert. Alle acht PR- und sechs Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung
und eigener lokaler/remote Branch- sowie Tempref-Cleanup sind bestätigt.
Der Squash ist `7519d0b7e1c4321faafa43ef27efb8629d72cd18`.
Diese Integration änderte ausschließlich fünf kanonische Markdowndateien;
es wurde keine lokale Suite oder private Probe erneut ausgeführt.

Der vollständige deklarative Inline-Profilabgleich wurde über
[Pull Request 112](https://github.com/gecompat/SQL_PerformanceSchulung/pull/112)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung
und eigener lokaler/remote Branch- sowie Tempref-Cleanup sind bestätigt.
Der Squash ist `1d3b73c5d593d8d04514abc259ee4c18727c2126`.
341/341 Methoden bestanden lokal und in beiden CI-Läufen ohne SKIP;
lokal und PR verwendeten CPython 3.12.14, Main 3.12.15.
Der präzisierte finale Reviewnachweis steht in §28.

Die reine begrenzte Profilrecord-Reassemblierung wurde über
[Pull Request 111](https://github.com/gecompat/SQL_PerformanceSchulung/pull/111)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung
und eigener lokaler/remote Branch- sowie Tempref-Cleanup sind bestätigt.
Der Squash ist `a2cd96220973b54172b59a637f4b81276715189a`.
Die Offline-Suite bestand lokal und in beiden CI-Läufen mit 304/304 Methoden
unter CPython 3.12.14; die CI-Frameworkprüfungen verwendeten 3.12.15.
§27 hält den einzigen lokalen Versuch und seine Grenzen fest.

Die reine begrenzte deklarative Inline-Rawbodyaufnahme wurde über
[Pull Request 110](https://github.com/gecompat/SQL_PerformanceSchulung/pull/110)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squashübernahme, FF-only-Main-Synchronisierung
und eigener lokaler/remote Branch- sowie Tempref-Cleanup sind unabhängig bestätigt.
Der Squash ist `ac1228537a3de1dcc9126569cf6eec0ef37df810`.
Lokaler und PR-Lauf verwendeten CPython 3.12.14, der separate Main-Lauf 3.12.15.
272/272 Methoden bestanden; der frühere 271/272-Fehllauf und die enge
Fixturelabelkorrektur bleiben in §26 getrennt erhalten. Dieser Beleg ist
ausschließlich synthetisch; operative Kanal-, Worker- und Methodengates bleiben offen.

Der vollständige deklarative Inline-Metadata-Callerabgleich wurde über
[Pull Request 109](https://github.com/gecompat/SQL_PerformanceSchulung/pull/109)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Beide lokalen Fixtureversuche bleiben in §25
erhalten. Die Abnahme belegt vollständigen deklarativen Metadata-Abgleich;
Bodyaufnahme, tatsächlicher Kanal und Freigaben bleiben eigene nächste Schritte.

Die reine additive K-Domain-/Commandquelle wurde über
[Pull Request 108](https://github.com/gecompat/SQL_PerformanceSchulung/pull/108)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Der einzige lokale Lauf bleibt in §24
festgehalten. Die Abnahme belegt K-Digestbildung und deklarativ gebundene
Commandbytes; tatsächlicher Kanal, vollständiger Metadata-Callerabgleich,
Bodyaufnahme und Freigaben bleiben offen.

Die reine begrenzte Inline-Header-/Metadata-Aufnahme wurde über
[Pull Request 107](https://github.com/gecompat/SQL_PerformanceSchulung/pull/107)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Der einzige lokale Lauf bleibt in §23
festgehalten. Die Abnahme belegt begrenzte Aufnahme gegebener Header-/Metadata-
Chunks; tatsächlicher Kanal, Callerabgleich, Bodyaufnahme und Freigaben
bleiben offen.

Der reine additive Inline-Profilreporter wurde über
[Pull Request 106](https://github.com/gecompat/SQL_PerformanceSchulung/pull/106)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Der einzige lokale Lauf bleibt in §22
festgehalten. Die Abnahme belegt die reine Reporterfunktion für gegebene
Scalarinputs; operative Inventur, Receiver, Caller-/Bodyprüfung und
Workerfreigabe bleiben offen.

Die reine additive Inline-Metadata-Semantikquelle wurde über
[Pull Request 105](https://github.com/gecompat/SQL_PerformanceSchulung/pull/105)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Beide lokalen Fixtureversuche bleiben in §21
erhalten. Die Abnahme belegt deklarative Metadata-Semantik und Providerkohärenz;
operative Inventur, Caller-/Bodyprüfung und Workerfreigabe bleiben offen.

Die reine additive Inline-Metadata-Syntaxquelle wurde über
[Pull Request 104](https://github.com/gecompat/SQL_PerformanceSchulung/pull/104)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Beide lokalen Fixtureversuche bleiben in §20
erhalten. Die Abnahme belegt Syntax allein; Metadata-Semantik, Digest-/Body-/
Callerprüfung und Workerfreigabe bleiben eigene nächste Schritte.

Die private begrenzte Auswahlgrundlage wurde über
[Pull Request 103](https://github.com/gecompat/SQL_PerformanceSchulung/pull/103)
integriert. Alle acht PR- und sechs Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Der einmalige native Nachweis ist keine
operative S15-/P11-Inventur oder Workerfreigabe.

Die getrennte feste Sysconfig-Vorinitialisierung wurde über
[Pull Request 102](https://github.com/gecompat/SQL_PerformanceSchulung/pull/102)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweils
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Der 53/53-PASS bleibt auf feste Synthetik
begrenzt; kein realer Sysconfigcall, Profil- oder Workerstart.

Der reine Kontrollbootstrapquellengenerator wurde über
[Pull Request 101](https://github.com/gecompat/SQL_PerformanceSchulung/pull/101)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head; unabhängige vollständige Squash-Übernahme, Main-Synchronisierung
und eigene lokale/remote Branch- und Tempref-Bereinigung samt unabhängiger
Nachprüfung sind abgeschlossen. Die beiden lokalen Fixture-Fehlläufe bleiben
in §17 getrennt vom korrigierten 32/32-PASS dokumentiert.

Der konkrete operative Bootstrap-/Kanalvertrag wurde über
[Pull Request 100](https://github.com/gecompat/SQL_PerformanceSchulung/pull/100)
integriert. Alle acht PR- und sechs Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squash-Übernahme, Main-Synchronisierung
und eigener lokaler/remote Branch- und Tempref-Cleanup einschließlich
unabhängiger Nachprüfung sind abgeschlossen. Die übrigen Implementierungsgates
bleiben offen.

Der vollständige reine kombinierte Eingangsprototyp wurde über
[Pull Request 99](https://github.com/gecompat/SQL_PerformanceSchulung/pull/99)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squash-Übernahme, Main-Synchronisierung und lokale/
remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig bestätigt.

Der vollständige experimentelle Formcodec-/Digestbeleg wurde über
[Pull Request 98](https://github.com/gecompat/SQL_PerformanceSchulung/pull/98)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squash-Übernahme, Main-Synchronisierung und lokale/
remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig bestätigt.

Der vollständige Stringpool-Größenbeleg wurde über
[Pull Request 97](https://github.com/gecompat/SQL_PerformanceSchulung/pull/97)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squash-Übernahme, Main-Synchronisierung und lokale/
remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig bestätigt.

Der separate Stringpoolentwurf wurde über
[Pull Request 96](https://github.com/gecompat/SQL_PerformanceSchulung/pull/96)
integriert. Alle acht PR- und sechs Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squash-Übernahme, Main-Synchronisierung und lokale/
remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig bestätigt.

Der vollständige Größenprüfschnitt wurde über
[Pull Request 95](https://github.com/gecompat/SQL_PerformanceSchulung/pull/95)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squash-Übernahme, Main-Synchronisierung und lokale/
remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig bestätigt.

Der vorige Designschnitt wurde über
[Pull Request 94](https://github.com/gecompat/SQL_PerformanceSchulung/pull/94)
integriert. Alle acht PR- und sechs Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squash-Übernahme, Main-Synchronisierung und lokale/
remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig bestätigt.

Am 2026-10-07 wurde nach der abgeschlossenen Entwicklungsrunde eine Pause
beauftragt. Der letzte integrierte Implementierungs-/Nachweisschnitt ist
[Pull Request 91](https://github.com/gecompat/SQL_PerformanceSchulung/pull/91):
Die getrennte Charakterisierung umfasst 85 Bootstrapnamen; die vollständige
verkleinerte Modularray-Untergrenze beträgt 16.449 Bytes und die gemeinsame
Metadata mit Header mindestens 21.108 bis 21.144 Bytes. Dies schließt nur die
heutige benannte JSON-Darstellung dieses charakterisierten Umfangs aus und
liefert keine operative Sollinventur oder Worker-, Trust- oder UsedBytesattestation.
40 Matcher-Tests bestanden lokal und in Linux-CI. Alle neun PR- und sieben
Main-Prüfungen waren erfolgreich; vollständige Squash-Übernahme, synchronisiertes
Main und lokale/remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig
bestätigt. Die Nachweise und Grenzen stehen im
[Profilbindungsentwurf §9](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#9-charakterisierte-bootstraproute-und-größenuntergrenze).

Die damalige Pause wurde einschließlich Wiederaufnahmeverfahren über
[Pull Request 92](https://github.com/gecompat/SQL_PerformanceSchulung/pull/92)
integriert und die Automation pausiert. Erst der spätere ausdrückliche
Fortsetzungsauftrag hebt diese Pause auf. Das Gesamtprojekt und die offenen
fachlichen Gates sind nicht abgeschlossen.

### Geordnete offene Schritte

Der ausdrückliche Auftrag vom 2026-10-07 zur Demo-Orientierung und Vorbereitung der Schulungsabnahme ist ein begrenzter Dokumentationsschnitt. Der [Demo-Katalog](../Demo_Catalog/README.md) ordnet historische Nachweise ein; der [Generalprobenplan](PRS_010_REHEARSAL_PLAN.md) enthält die vorbereitete Auswahl und eine getrennte Folien-/Notes-Prüfung. Eine Teilnehmer-Generalprobe wurde nicht durchgeführt; zur Aufarbeitung der Nachweise wurde keine lokale oder manuell angestoßene SQL-Runtime ausgeführt. Automatisch durch den Pull Request ausgelöste bestehende CI-Prüfungen bleiben an ihren eigenen Run-Commit gebunden und ersetzen keine Teilnehmerabnahme. Dieser frühere Auftrag allein reaktivierte die allgemeine Entwicklung nicht; die spätere ausdrückliche Fortsetzung ist oben getrennt festgehalten. Offene DGN-007-Gates bleiben bestehen.

1. Der vollständig erhaltende Darstellungs- und Digestentwurf liegt als
   getrennter Designschnitt in §10 vor und ist unabhängig zu reviewen.
   Gemeinsame Metadata, Berichte und alle kanonischen Digestpräbilder müssen
   zusammen betrachtet werden: Nur den Transport zu verkleinern reicht bei
   anschließender Expansion in die heutige benannte JSON-Form nicht aus.
   Input82/DGNI001, sämtliche Felder, beide vollständigen Neuner-Deskriptorarrays
   und die bestehenden Caps bleiben erhalten. Keine stillschweigende Filterung,
   Capanhebung oder Digestersetzung; ein Codec ist damit noch nicht implementiert.
2. Die separat vorgewählte vollständige Kontrollfixture und alle fünf Größen sind
   in §11 geprüft. Der §10-Tupelkandidat überschreitet die gemeinsame Grenze.
   Der separate Stringpoolentwurf in §12 erhält alle Inhalte, Arrays, Locator
   und Caps. Der eigene reine Pool-Sizer und alle fünf Formen für alle drei
   Ordinals sind in §13 vollständig geprüft: sämtliche Größen passen, maximal
   9.389 Bytes und 204 Poolwerte; 37 Gegenproben ohne SKIP und unabhängige
   vollständige Nachrechnung. Kein Codec-, Transfer- oder Legacy-Fitclaim.
   Die gewählte Kontrollfixture ist keine zukünftige Workerbaseline.
3. Der eigene experimentelle Formcodec-/Digestpfad in §14 und der reine
   kombinierte Metadata-/Rawbody-Eingang in §15 sind vollständig getrennt
   implementiert und geprüft. Die konkrete operative Bootstrap-/Kanalreihenfolge
   liegt in §16 als `DESIGNED` vor. Der reine Kontrollbootstrapquellengenerator
   in §17 ist ausschließlich synthetisch implementiert und geprüft:
   `Tests/Tools/dgn007_control_bootstrap_source.py` und
   `Tests/Static/test_dgn007_control_bootstrap_source.py`. Seine privaten
   Scriptbytes sind keine operative Workerroute; der §8-Workerlocator bleibt
   Folgearbeit. §8 bleibt importneutral;
   vor PRE_IMPORT keine Combined-/Codec-/Input82-/Matcherimports und keine
   Übernahme der charakterisierten Fixture als operative Baseline. Die reine
   Inline-Syntax, deklarative Metadata-Semantik und der Profilreporter sind
   in §20–22 implementiert und synthetisch geprüft. Die reine begrenzte
   Header-/Metadata-Aufnahme aus gehaltenen Chunks ist nach §23 implementiert
   und synthetisch geprüft. Die reine K-Domain-/Commandquelle nach §24 ist
   mit 209/209 isolierten synthetischen Gegenproben implementiert und geprüft.
   Der vollständige deklarative Header-/Metadata-Callerabgleich nach §25
   ist nach zwei engen Fixturekorrekturen mit 243/243 isolierten synthetischen
   Gegenproben implementiert und geprüft; der erste Fixturefehllauf bleibt
   erhalten. Die reine Bodyaufnahme nach §26 ist nach einer Fixturelabelkorrektur
   mit 272/272 isolierten Gegenproben geprüft; der erste Fehllauf bleibt erhalten.
   Die reine Reassemblierung nach §27 ist im einzigen isolierten Lauf mit
   304/304 Gegenproben geprüft; zwei neue Fixturelabels wurden vor dem Lauf
   korrigiert. Der vollständige deklarative R-Abgleich nach §28 ist im einzigen
   isolierten Lauf mit 341/341 Gegenproben geprüft; zehn frühere Builder und
   304 alte Methoden bleiben erhalten. Die additive reine R→BODY_RELEASE-Planquelle nach §29
   ist im einzigen isolierten Lauf mit 378/378 Gegenproben synthetisch geprüft;
   elf alte Builder und 341 Methoden bleiben erhalten. Der separate
   [INPUT_COMPLETE-Recordvertrag §30](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#30-deklarativer-input_complete-rückkanalrecord)
   ist als reine additive Quelle im einzigen isolierten Lauf mit 413/413 PASS
   ohne SKIP geprüft; zwölf alte Builder und 378 alte Methoden bleiben erhalten.
   Der vollständige
   [Record-/Footer→R-Calleradapter §31](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#31-vollständiger-deklarativer-profilrecord-callerabgleich)
   ist rein additiv implementiert und mit 460/460 synthetischen Methoden
   ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden bleiben erhalten.
   Die eigene lokale Ledgerkomponente nach §32.5 ist isoliert synthetisch geprüft.
   Vollständige Loaderrecordformen nach §33 liegen als DESIGNED vor.
   Nächster kleiner Schnitt: separater SESSION_END-DESIGN-Vertrag mit exakten
   Counts und nicht selbstreferentiellem Kanalhashpräbild.
   Tatsächlicher Kanal und Freigaben folgen getrennt.
   Anschließend operative Auswahl samt Fünf-Formen-/64-KiB-Gate für die
   endgültige Quelle vor jeder tatsächlichen Workerfreigabe sowie
   tatsächliche Parent-/Worker-, Quellen-, Kanal-, Kontext-, Consumption- und
   Replaybindung in kleinen getrennten Schnitten umsetzen und validieren.
4. Anschließend den begrenzten Linux-/Python-3.12-Import-Only-Prototyp mit
   tatsächlicher DGN-Loaderverwendung, Importabschluss und unabhängigem Cleanup
   eigener Worker belegen. Dies ist weiterhin keine vollständige UsedBundle-,
   SQL-, Acquisition-, Methoden- oder Capstoneattestation.
5. G13-/Messvertragsklärung und ausdrückliche Methodenentscheidung bleiben eigene
   Gates. Erst danach die zurückgestellte interne Capture-Rückgabe integrieren,
   Coordinator-Freeze, Ressourcen, serielle Reihenfolge und Budgets belegen und
   frische prospektive Bestätigungsläufe ausführen. Historische Fehler, v1 und
   `DEC-068` bleiben gültig; keine Toleranz- oder Metrikkorrektur ohne Entscheidung.

### Erhaltene Arbeit und Startverfahren

Die Reporterarbeit in [Pull Request 68](https://github.com/gecompat/SQL_PerformanceSchulung/pull/68)
wurde seit dem gezielten Auftrag vom 2026-10-09 gegen den aktuellen Main-Stand
erneut validiert. Der aktuelle Head `f9ec582…` ist wegen der beiden im
Abschlussreview belegten Runtimefehler technisch blockiert; PR68 wurde für den
getrennten Dokumentationsabschluss vorübergehend geschlossen. Der Code bleibt
auf seinem konkret benannten Branch erhalten. Nach Klärung/Korrektur der
Erfassung und des G13-/Methodengates folgen Quellenreview, erfolgreiche aktuelle
CI, Integration und eigene Branchbereinigung.
Der [Abschlussreview](DGN_007_G13_PR_REVIEW.md) ist für diesen Schnitt maßgeblich.
Der ursprüngliche Reporter-Head war
`27a9b5ce81347beaa6d6bfd8788c62965495f0ca`; die folgenden Befunde beschreiben
den historischen HOLD-Stand, keine abgeschlossene aktuelle Revalidierung.
Der erneute vollständige Branchabgleich am 2026-10-08 gegen Main
`e8dc3a0f37e64ecef8f69cc0afb7dd5912341eac` und sein unabhängiger Review
bestätigen: SQL35, Runner, Producer-Test und -Validator, VertragsJSON sowie
`SQL_CAPTURE_PRODUCER.md` stehen auf Main weiterhin auf PR68-Base
`12b130f0df1f963a9075430745e406e8e2a38494`; die Reporteränderungen fehlen.
Die fünf Kanonik-/Evidenzdokumente wurden dagegen separat übernommen
beziehungsweise fortgeschrieben. Der Branch ist daher weiterhin benötigt
und wurde nicht als redundant gelöscht. PR68 war ausdrücklich als HOLD
ohne Mergefreigabe gekennzeichnet; 20/22 abgeschlossene Checks SUCCESS,
2019 AA1 und 2022 BA1 weiterhin G13 FAIL. Vor einer Integration sind
Methodengate, aktueller Quellenreview und erfolgreiche head-/basegebundene
CI erforderlich; alte Planungsstände dürfen nicht zurückgesetzt werden.
Dieser Statusabgleich änderte keinen G13-Code und startete keine SQL-Runtime.

Der unveröffentlichte lokale Branch `codex/dgn007-internal-capture-receipt`
bei `83f08fb71446445e70fb6227e442ed7109637de6` bleibt erhalten; seine Veröffentlichung
ist zurückgestellt. Beide sind keine freigegebenen Integrationen. Private
Review-/Runtime-Dateien, Chat-Verlauf und lokale Cache-Records sind keine
Voraussetzung oder dauerhafte Projektwahrheit. In dem damaligen Pausenschnitt wurde
keine SQL-Runtime gestartet und keine bestehende SQL- oder Containerressource verändert.

Bei späterer Fortsetzung die native AGENTS-Anweisungskette und die Lesereihenfolge
aus [`.ai/README.md`](../../.ai/README.md) erneut erschließen, den dann aktuellen
`origin/main` samt offenen PRs, Branches und laufender Arbeit prüfen und diesen
Abschnitt gegen [NEXT_DEVELOPMENT_WAVES.md](NEXT_DEVELOPMENT_WAVES.md),
[Masterplan §19](MASTER_IMPLEMENTATION_PLAN.md#19-wiederaufnahmeprotokoll) und
[Backlog](../../.ai/BACKLOG.md) abgleichen. Den nächsten Scope genau einem
Implementierungsowner zuweisen und unabhängig reviewen. SQL-Runtime bleibt auf
ausdrücklich bestätigte neue isolierte Wegwerfinstanzen begrenzt. Die Automation
nur nach ausdrücklicher Fortsetzung wieder aktivieren; keine automatische
Chat-/Sessionrotation. External Tables und Graph Tables bleiben im Backlog als
nachgeordnetes `P2`-Thema ohne Implementierungs- oder Runtimefreigabe.

## 1. Verifizierter Repository-Stand

Der Repository-Basisstand war zu Beginn der Verarbeitung sauber. Für den korrigierten `OPT-017`-Stand liefen die betroffenen statischen Validatoren, Runner-Selbsttests, `git diff --check` und der Privacy-Scan erfolgreich; letzterer meldete `PASS (files=632; text=621; office=1; archives=0; approved_immutable=1)`.

Die bestehenden CI-Nachweise stammen aus den verlinkten GitHub-Actions-Läufen; ergänzende lokale Nachweise sind in der Tabelle ausdrücklich gekennzeichnet. Die Läufe 33222989681, 33222989682 und 33222989644 prüfen den in `origin/main` enthaltenen Commit `6fd2b1d5170f7658cf0b86ee05314f2ab543adc7`. Pull Request 42 prüft `OPT-017` auf dem unveränderlichen Head `782799e`.

## 2. Runtime-Nachweisstand der produktiven Demos

| Demo | Ergebnis | Status |
|---|---|---|
| `OPT-015` | Plan- und Statistikevidenz, zwei vollständige Läufe auf SQL Server 2019, 2022 und 2025 | `VALIDATED` |
| `OPT-016` | Outer References, Rebinds, Rewinds und Performance Spool, zwei vollständige Läufe auf 2019, 2022 und 2025 | `VALIDATED` |
| `QRY-013` | [Actions-Lauf 30699410795](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30699410795): zwei Docker-basierte Läufe auf 2019, 2022 und 2025 | `VALIDATED` |
| `OPT-009` | [Actions-Lauf 30701731564](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30701731564): 2022/2025 erfolgreich, 2019 erwartungsgemäß `SKIP_VERSION` | `VALIDATED` |
| `OPT-010` | [Actions-Lauf 30702590969](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30702590969): 2025 erfolgreich, 2019/2022 erwartungsgemäß `SKIP_VERSION` | `VALIDATED` |
| `OPT-013` | Gate-B-Nachweis | `VALIDATED` |
| `QRY-001` | Framework- und Lab-Nachweis | `VALIDATED` |
| `OPT-002` | Framework- und Lab-Nachweis | `VALIDATED` |
| `CON-004` | fachliche Demo und Szenariokandidat | `VALIDATED` |
| `QRY-004` | [Actions-Lauf 33222989681](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989681): je zwei vollständige Läufe auf 2019/2022/2025; erwartete `WARN_EMPIRICAL_VARIANCE` ohne Vertrags- oder Cleanup-Fehler | `VALIDATED` |
| `DGN-003`, `DGN-005` | [Actions-Lauf 33222989682](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989682): je zwei `PASS/OK` auf 2019/2022/2025 | `VALIDATED` |
| `OPT-017` | [Actions-Lauf 33447840232](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33447840232): je zwei `PASS/OK` auf 2019/2022/2025 mit Actual DOP, Exchange, positiver Threadarbeit, serieller Gegenprobe und Cleanup | `VALIDATED` |
| `OPT-003`, `OPT-005` | Statistik-Sampling/Skew sowie Ascending-Key-/Pflegevertrag; je zwei lokale Docker-Läufe auf 2019/2022/2025 mit `PASS` | `VALIDATED` |
| `CON-006` | Deadlock-Zyklus, Fehler 1205, Graph und geordnete Gegenprobe; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `CON-009` | [Actions-Lauf 33222989644](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989644): TempDB-Kostenklassen auf 2019/2022/2025 jeweils zweimal `PASS/OK` | `VALIDATED` |
| `IDX-006`, `IDX-010` | Rowstore-Messkette je zweimal mit fachlich akzeptierter Warnung; klassische Columnstore-Segmente je zweimal `PASS` auf allen Zielversionen | `VALIDATED` |
| `STL-008`, `STL-009` | rote VLF-/Growth-Lane und gelber Commit-/WRITELOG-Schnitt; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `RES-007` | Task-, Request- und Instanz-Waitscope mit Gegenprobe; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `QRY-006` | Lokaler Docker-Nachweis: SQL Server 2019/150, 2022/160 und 2025/170, je zwei vollständige Manifestläufe `PASS`; siehe [QRY_006_RUNTIME_EVIDENCE.md](QRY_006_RUNTIME_EVIDENCE.md) | `IMPLEMENTED` – Runtime-Gate und SQL_Server_Lab-Szenariopromotion bleiben offen |
| `DGN-007_DATA_MODEL` | Lokaler Docker-Nachweis vom 2026-10-06: 2019/150, 2022/160 und 2025/170 je zwei vollständige Datenmodell-Lifecycles `PASS/OK`, unabhängiger Datenbankabbau nach jedem Lauf und Entfernung aller eigenen Container; siehe [DGN_007_DATA_MODEL_RUNTIME_EVIDENCE.md](DGN_007_DATA_MODEL_RUNTIME_EVIDENCE.md) | `IMPLEMENTED` – begrenzter Datenmodellvertrag; vollständige Capstone-Abnahme und Szenariopromotion bleiben offen |
| `DGN-007_QUERY_STORE_WINDOWS` | Lokaler Docker-Nachweis vom 2026-10-06: 2019/150, 2022/160 und 2025/170 je zwei vollständige Fenster-Lifecycles `PASS/OK`; disjunkte Katalogintervalle, gleiche vier Parameterklassen und je vier erfasste Suchausführungen, unabhängiger Datenbankabbau und Entfernung aller eigenen Container; siehe [DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md](DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md) | `IMPLEMENTED` – begrenzte Capture-Evidenz; kein Incident-, Regressions- oder Capstone-Nachweis |

`QRY-004` bleibt fachlich bewusst warnungsfähig. `WARN_EMPIRICAL_VARIANCE` behauptet keinen nicht gemessenen Performancevorteil und verhindert die Runtimefreigabe nicht, sofern die Matrix vollständig läuft und Ergebnis-, Sicherheits-, Wiederverwendungs- und Cleanup-Verträge erfüllt sind. Genau diesen Zustand belegt Lauf 33222989681.

## 3. Lab-Integration und Szenarien

`LABSCN-001` und `DEC-044` bleiben verbindlich:

- `SQL_Server_Lab` provisioniert die technische Umgebung; dieses Repository beschreibt Lernziel, Setup, synthetische Daten, Benutzeraktionen, Beobachtungen und Reset.
- Ein interaktives Szenario endet nach der Vorbereitung in `READY_FOR_USER`; Reset und Entfernen sind getrennte, bewusste Benutzeraktionen.
- Die automatisierte Matrix ist ein Qualitätssicherungsinstrument und kein Ersatz für den Benutzerworkflow.
- Änderungen an `SQL_Server_Lab` benötigen eine konkret nachgewiesene fehlende Fähigkeit und ausdrückliche Freigabe.

`LABSCN-002` inventarisiert alle 22 produktiven Demos vollständig und wird
gegen den aktiven Demo-Katalog validiert. `LABSCN-003` setzt `CON-004` als
ersten vollständigen Vertical Slice um; `LABSCN-005` ergänzt `DGN-005` und
`CON-006` als zweiten und dritten freigegebenen Slice. Alle drei versionierten
Project Adapter `0.1` begrenzen ihren interaktiven Pfad auf SQL Server 2025 Linux in einer isolierten
Docker- oder Podman-Wegwerfumgebung und besitzen getrennte Preflight-, Install-,
Validate- und Cleanup-Entrypoints.

```text
Auswahl -> Provisionierung -> fachliche Vorbereitung -> READY_FOR_USER
        -> interaktive Durchführung -> Reset -> Remove
```

Die lokalen Nachweise vom 2026-08-30 bestätigten denselben vollständigen
Lifecycle auf Docker (RunId `30b69f0b-b140-47e6-8c90-c05e38bd7c99`) und Podman
(RunId `f80f7d82-934b-4c7c-9d2a-a80e975d92d5`): Start und Reset endeten
jeweils als `READY_FOR_USER`; der anschließende markergebundene Datenbank-,
Container- und Volume-Abbau einschließlich Abschluss des aktiven
Szenario-States endete als `REMOVED`. Der Lab-Core behält ausschließlich den
nicht aktiven Auditdatensatz des entfernten Runs. Der Podman-Cleanup ließ eine
bereits vorhandene, nicht zum Run gehörende Ressource unverändert gesund.

Der `DGN-005`-Folgeslice bestand am 2026-09-01 denselben Lifecycle auf Docker
(RunId `d5143f2a-9f18-49fa-8e9f-b91604993252`) und Podman (RunId
`82791985-b76a-4594-a5be-bab014907f7d`). Beide Provider führten Demonstration,
Observation, Mitigation und Comparison mit `PASS/OK` aus und erreichten nach
dem Reset erneut `READY_FOR_USER`; die markergefilterte, speicherbegrenzte
Extended-Events-Session sowie Datenbank, Container und Volume wurden danach
vollständig entfernt.

Der `CON-006`-Folgeslice bestand am 2026-09-01 den vollständigen Lifecycle auf
Docker (RunId `76cff6ed-a714-44e6-beda-6b916600cb98`) und Podman (RunId
`6d2d0a51-1915-4e65-a380-baec715fc676`). Beide Provider belegten genau ein
Opfer mit Fehler 1205, genau einen Survivor, einen Deadlock-Graph sowie zwei
erfolgreiche Akteure in der geordneten Gegenprobe. Start und Reset endeten als
`READY_FOR_USER`; Cleanup und Infrastrukturabbau endeten als `REMOVED`. Der
Podman-Lauf nutzte wegen einer fremden aktiven Altressource ein isoliertes
Ausweichnetz und ließ die fremde Ressource unverändert.

## 4. Gate-Status

- Gate V0 – Quellenfreigabe: `VALIDATED`.
- Gate V1 – Curriculumfreigabe: `VALIDATED`.
- Gate V2 – Designfreigabe: `VALIDATED`.
- Gate V3 – Runtimefreigabe: `VALIDATED`; alle freigegebenen `ADV-008`- und `W-COV-001`-Demos besitzen den zutreffenden Matrixnachweis.
- Gate V4 – Lehrmittelfreigabe: `VALIDATED`; Masterdeck und Profile bestanden Notes-, Manifest-, Custom-Show-, Build-, Render-, Metadaten-, Privacy- und Branding-Abnahme.
- `LABSCN-001`: `DECIDED` und im Repository verankert.
- `LABSCN-002`: `VALIDATED`; 22 von 22 produktiven Demos besitzen den vollständigen Inventarvertrag.
- `LABSCN-003`: `VALIDATED` für den vollständigen SQL-Server-2025-Lifecycle auf Docker und Podman.
- `LABSCN-004`: `VALIDATED`; Auswahl, Start, Übergabe, Reset und Remove sind standardisiert dokumentiert und statisch abgesichert.
- `LABSCN-005/DGN-005`: `VALIDATED` als zweiter interaktiver SQL-Server-2025-Slice auf Docker und Podman.
- `LABSCN-005/CON-006`: `VALIDATED` als dritter interaktiver SQL-Server-2025-Slice auf Docker und Podman.
- `LABSCN-005/DGN-007`: `IMPLEMENTED_STATIC_SLICE_B` mit praktischer Adapter-Lifecycle-Abnahme vom 2026-09-14: Docker-Run `9ac100f8-f24f-420e-949c-943e35b9bcda` und Podman-Run `e06e9ec9-d239-4cd0-b9a7-0050dc574180` bestanden jeweils Start -> `READY_FOR_USER`, Reset -> `READY_FOR_USER` und Remove -> `REMOVED` auf SQL Server 2025. Die aktuelle Fassung bestand am 2026-09-19 zusätzlich vollständig auf frischen SQL-Server-2025/Linux-Runs: Docker (`ea802c20-4820-4007-a441-43a74a89c8fc`) und Podman (`fba84720-5f0b-4537-bc98-75bbad37a85b`). Jeweils endeten Adapter-Install/Validate, Preflight, Baseline, Evidenz, reversible Mitigation, Vergleich, Teilnehmer-Cleanup, Adapter-Cleanup und Lab-Remove mit `PASS` beziehungsweise `REMOVED`. Als kontrollierter Negativtest des 2025-only-Vertrags liefen auf Docker außerdem SQL Server 2019 (`5a12e48a-46df-471a-a266-4646ba3a02e2`) und SQL Server 2022 (`139c68d8-8a22-42fb-ba19-b51059f21f2b`): kanonisch `ADAPTER_UNSUPPORTED_SQL_VERSION`, tatsächlicher Lab-Core-Status `ADAPTER_UNSUPPORTED_CONTRACT`, keine DGN-Datenbank und abschließend `REMOVED`. Diese Läufe belegen ausdrücklich keine fachliche Unterstützung von 2019/2022 und keine Promotion; sie bestätigen nur den kontrollierten Skip-/Cleanup-Pfad. Die positive Evidenz belegt die aktuelle Linux-Providerparität, aber weder eine vollständige Lifecycle-Matrix noch eine Szenariopromotion. Teilnehmerorchestrierung als interaktives Szenario und `scenario.json` bleiben offen.
- `LABINT-001`: `VALIDATED` als nachgeordneter Testkatalog.
- `LABINT-002`: `VALIDATED` für Start, `READY_FOR_USER`, Reset und Remove von `CON-004` auf Docker.
- `LABINT-003`: `VALIDATED` für die freigegebenen Slices `QRY-001`, `CON-004` und `DGN-005`; Docker-/Podman-Parität ist praktisch belegt.
- `LABINT-004`: `VALIDATED` für die vollständige freigegebene SQL-Server-2025-/Docker-/Podman-Matrix des gelben `CON-006`-Slices einschließlich fachlicher Gegenprobe und Cleanup.
- `INF-002`/`INF-003`: `VALIDATED`; beide Provider-Preflights melden `RESOURCE_OK`, Quickstart und Recovery sind dokumentiert.

`ADV-006` und `ADV-007` bleiben als `DESIGNED`-Verträge vollständig: Die zugehörigen LAB-VP3-/VP4-Grenzen, Feature-Skips und Diagnoseabhängigkeiten sind dokumentiert, ihre fachliche Umsetzung erfolgt erst in den jeweiligen Folgewellen.

## 5. Nächste fachliche Verarbeitung

Die verbindliche Reihenfolge und die Akzeptanzkriterien stehen in [NEXT_DEVELOPMENT_WAVES.md](NEXT_DEVELOPMENT_WAVES.md). Kurzfristig ist die Reihenfolge:

1. `DGN-007` Capstone-Planungsschnitt ist mit `TSK-002` entschieden
   (`DECIDED_PLANNING`, Stand 2026-09-14); der Detailreviewvertrag steht in
   [LABSCN_005_DGN_007_DETAIL_REVIEW.md](LABSCN_005_DGN_007_DETAIL_REVIEW.md).
2. Implementierungsschnitt A ist umgesetzt und adapterseitig abgenommen:
   Project Adapter `0.1` mit Datenaufbau, Query-Store-Zeitfenstern und
   Incident-Erzeugung ohne Mitigationsmarker; die Docker-/Podman-Lifecycle-Abnahme
   bestand am 2026-09-14 mit RunId `9ac100f8-…` (Docker) und `e06e9ec9-…`
   (Podman) jeweils über Start, Reset und Remove bis `REMOVED`.
3. Implementierungsschnitt B besitzt einen nicht-promotenden statischen
   Teilnehmerablauf und ist auf frischen SQL-Server-2025/Linux-Läufen mit Docker
   und Podman praktisch belegt. Der Ablauf endet nach Cleanup mit
   `REMOVED`; er erzeugt keine interaktive `READY_FOR_USER`-Übergabe. Offen
   bleiben die vollständige Lifecycle-/Versionsmatrix sowie die für eine
   Promotion erforderlichen `scenario.json`-, Manifest- und Inventareinträge.
   Der getrennte Datenmodellvertrag ist am 2026-10-06 auf Docker für alle drei
   Zielversionen je zweimal praktisch belegt. Der getrennte Query-Store-
   Fenstervertrag bestand anschließend ebenfalls je zweimal auf allen drei
   Versionen. Der neutrale `DGN-007_PROFILE_COMPARISON`-Vertrag bestand am
   2026-10-07 ebenfalls je zweimal auf allen drei Versionen. Die vollständige
   Reihenfolge ergab 18 erfolgreiche lokale Lifecycles, vier zusätzliche
   Ausgabekontrollen bestanden auf 2019/2022. Datenbankabwesenheit je Lauf und
   Abbau aller fünf eigenen Container wurden unabhängig bestätigt. Der
   [Profilnachweis](DGN_007_PROFILE_COMPARISON_RUNTIME_EVIDENCE.md) dokumentiert
   gewichtete CPU-/Duration-/Reads-/Rows-Metriken ohne Incidentpromotion.
   Die anschließend getrennten neutralen AB-/BA-/AA-Kontrollcaptures bestanden
   am 2026-10-07 auf allen drei Versionen je zweimal. Die vollständige neue
   Reihenfolge ergab 36 erfolgreiche lokale Lifecycles und unabhängigen Abbau
   aller drei eigenen Container. Der
   [Kontrollnachweis](DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md) dokumentiert
   tatsächliche Requestfolge, aktive Plan-ID-/Hash-Union und Metrikvariation.
   Auf 2019 überlappt eine AA-Schwankung einen BA-Duration-Kontrast.
   Der getrennte [prospektive Prüfvertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md)
   liegt jetzt als `STATIC_PROSPECTIVE_CONTRACT` vor (`DEC-068`): reine
   Recordprüfung, gerichtete Duration-Separation gegenüber AA und globaler
   Planfingerprint- oder Reads-Zweig. 34 synthetische Tests und der Validator
   für 14 gebundene SQL-/Manifestquellen bestanden lokal. Das ist ausschließlich
   `PROJECT_SEMANTIC`, keine SQL-Runtime-Abnahme. Der getrennte
   [skalare Collector-Transport](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md)
   ist jetzt als `STATIC_COLLECTOR_TRANSPORT` implementiert: reiner begrenzter
   JSON-Decoder, genaue Decimal-/100-ns-Übertragung und gebundene Records.
   19 Transporttests und beide Validatoren bestanden lokal, ebenso die
   34 Prospektivtests. Fehlende Ergebniszeilen je Request bleiben ausdrücklich
   `NOT_CAPTURED`/`None`; auch `MEASURED` ist nur eine Eingabedeklaration.
   Dieser reine Decoder bildet keinen vollständigen RunRecord. Der getrennte
   [SQL-Producer](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/SQL_CAPTURE_PRODUCER.md)
   erfasst jetzt tatsächlich gezählte Ergebniszeilen je Request und stellt
   die vollständige skalare Projektion vor Cleanup bereit. Die neue lokale
   Matrix bestand am 2026-10-07 auf 2019/150, 2022/160 und 2025/170 je zweimal
   AB/BA/AA: insgesamt 18 vollständige Lifecycles mit tatsächlichem Decoder
   und unabhängiger Datenbankabwesenheit. Alle drei eigenen Container sind
   unabhängig abwesend bestätigt. Quellenfreeze, genaue Versions-/Imagebindung
   und getrennte frühere Fehlversuche stehen im
   [Producernachweis](DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md).
   156 lokale Testmethoden der Phasendiagnostikrevision ergaben 155 PASS und einen ausdrücklich
   Linux-spezifischen SKIP unter Windows. Die Producer-Integration über
   [Pull Request 65](https://github.com/gecompat/SQL_PerformanceSchulung/pull/65)
   ist abgeschlossen: Head `20a867e…` gegen Base `94ed561b…`, geprüfter
   Integrationscommit `df78cb0…`, 14 Workflows und alle 22 Jobs SUCCESS.
   Linux führte alle 156 Methoden ohne SKIP aus. Je Version bestanden zwölf
   Lifecycles, sechs Decoder-Captures und zwölf unabhängige Datenbank-
   abwesenheitsprüfungen; die drei DGN-007-CIDs sind explizit abwesend bestätigt.
   Der Squash `da7b0eb…` wurde am 2026-10-07 um 04:18:12 UTC integriert;
   vollständige Tree-Gleichheit, Main-Synchronisierung und lokale/remote
   Bereinigung des eigenen Arbeitsbranches sind unabhängig bestätigt.
   Die zwei historischen CI-Fehler bleiben im Producernachweis getrennt
   dokumentiert; ihre Ursache ist unbekannt. Die Diagnostik ändert weder
   SQL-Prädikate noch Budgets und behauptet keine Fehlerbehebung.
   Die anschließend getrennte Main-Push-CI am Squash `da7b0eb…` ist vollständig
   beendet: 12 von 13 Workflows und 47 von 48 Jobs SUCCESS. Im
   [DGN-007-Lauf 37570814577](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37570814577)
   scheiterte SQL Server 2022 im zweiten BA-Lifecycle mit
   `CONTROL_EVIDENCE / FAIL_RESULT_CONTRACT / G13`; dieser Guard prüft
   gespeicherte Query-Store-Zeiten gegen `ExecutionStarted/ExecutionFinished`.
   Alle zehn begonnenen 2022-Datenbankabwesenheitsprüfungen und der eigene
   Containerabbau einschließlich expliziter CID-Abwesenheit bestanden.
   2019/2025 bestanden jeweils zwölf Lifecycles und sechs Decoder-Captures.
   Das ist ein neuer tatsächlicher Runtime-Vertragsfehler, keine vollständige
   Main-CI-Freigabe und keine Aufhebung der erfolgreichen PR65-Abnahme.
   Welche Grenze verletzt wurde und weshalb, ist noch nicht belegt.
   Die getrennte private 2022-Gegenprobe bestand anschließend den CI-Präfix
   Datenmodell, Fenster, Profil, AB und BA je zweimal: zehn Lifecycles,
   vier Decoder-Captures, zehn Abwesenheitsprüfungen und fünf zusätzliche
   Gruppen-Leerheitsprüfungen PASS. Die eigene Instanz ist unabhängig abwesend;
   alle 21 Freeze-Dateien blieben gleich. G13 wurde nicht reproduziert und
   es liegen keine tatsächlichen G13-Zeitwerte vor. Zwei vorherige synthetische
   Probe-Vorchecks scheiterten vor jedem Lifecycle; ihre Defekte und ihr
   unabhängig bestätigter Cleanup stehen im Producernachweis getrennt.
   Nächster Schnitt ist der begrenzte kanonische G13-Grenzabstandsbericht,
   ausschließlich im bereits verletzten Fehlerzweig, mit strenger Kanalbindung
   und Ausgabe erst nach Cleanup. Guards, Last und Budgets bleiben gleich.
   Dieser begrenzte kanonische Reporter ist jetzt lokal implementiert und
   unabhängig geprüft. 43 Runner-Tests, 37 Producer-/Reporter-Methoden
   (36 PASS, ein Linux-spezifischer SKIP unter Windows) und sieben
   DGN-007-Validatoren bestanden. Acht tatsächliche temporäre SQL-Branchfixtures
   bestanden auf einer neuen eigenen 2022-Instanz `16.0.4295.3`:
   beide Ein-Tick-Verletzungen, beide Seiten, Gleichheit, gleiche Requestgrenzen,
   UTC-Offset, acht Gruppen und ausdrücklicher Overflow bei neun.
   Quellenfreeze unverändert; eigene CID und Name nach Entfernung unabhängig
   abwesend bestätigt. Der ganze vorherige SQL35 ergibt sich nach exakt
   validierter Reporterentfernung unverändert. Der Report bleibt atomar
   innerhalb 24 Diagnosezeilen und wird erst nach Cleanup ausgegeben.
   Die reguläre CI von [Pull Request 68](https://github.com/gecompat/SQL_PerformanceSchulung/pull/68)
   am Head `27a9b5c…` gegen Base `12b130f…`, Integration `55877a5…`, ist
   vollständig beendet: 13/14 Workflows und 20/22 Jobs SUCCESS. 2019 AA1
   und 2022 BA1 scheiterten an G13; 2025 bestand zwölf Lifecycles und sechs
   Captures. Der Reporter erfasste jeweils genau eine vollständige verletzte
   Gruppe: First−Start beträgt −4.263 beziehungsweise −9.510 100-ns-Ticks,
   entsprechend −0,4263 beziehungsweise −0,951 ms; nur die untere Grenze
   ist verletzt. Alle 32 begonnenen Lifecycles bestanden die erste unabhängige
   Datenbankabwesenheitsprüfung, alle neun SQL-Containerabbauten bestanden;
   DGN-007 mit expliziter eigener CID-Abwesenheit. Linux 163 Methoden PASS.
   Der PR bleibt ohne Mergefreigabe offen. Beide QS-Zeitwerte liegen in diesen
   zwei Beobachtungen auf einem Millisekundenraster; daraus folgt keine
   allgemeine Auflösung, Clockursache oder Toleranzfreigabe. Die getrennte private
   Originalmaterialisierungsprobe reproduzierte G13 auf einer neuen eigenen
   2022-Instanz in AB1: First−Start −0,2609 ms. Die verletzte Gruppe enthält im
   tatsächlich übernommenen Captureversuch und im Live-SELECT jeweils eine
   positive Zeile mit Count vier, keine Zero-/NULL-/Negative-Zeilen. Ein
   Zero-Extremum erklärt diese lokale Verletzung nicht. Elf temporäre SQL-
   Fixtures bestanden; sechs Präfix-Lifecycles PASS, AB1 FAIL, sofortiger Stop.
   Alle sieben ersten DB-Abwesenheitsprüfungen und unabhängiger eigener
   Containerabbau bestanden; Freeze mit 27 Dateien unverändert. Kein AB2/BA/AA
   und kein erfolgreicher AB-Capture. Die Messvertragsgrenze zwischen QS-Endzeit
   und SYSUTC-Requestklammer bleibt ungeklärt. Der quellenbasierte
   [Mess-/Zuordnungsgegenentwurf](DGN_007_CAPTURE_ASSIGNMENT_DESIGN.md) liegt
   jetzt als `PROPOSED` vor: exakter Einschluss und kontrollierte
   Kollektivzuordnung sind getrennte Alternativen. Der Kandidat verlangt
   eine belegte Familienbasis B, sequenziellen T0-Capture vor T1,
   vollständige Bilanz B→B+4→B+8 und vertrauenswürdig attestierten
   Ausführungsumfang. Vorabrequests erfolgen vor der expliziten QS-
   Konfiguration; eine frische Datenbank garantiert kein QS-OFF oder
   Nullbaseline. Konkrete Baseline-/Intervall- und Herkunftsbelege bleiben
   offen. Das getrennte [deklarative Voraussetzungenmodell](DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md)
   prüft jetzt synthetische Gegenbeispiele und bedingte Konsistenz, ohne
   SQL-/v1-Änderung oder Runtimeattestation. Passende Counts allein belegen
   keine Herkunft; fehlende Annahmen und Widersprüche bleiben getrennt.
   Die getrennte [Quellen-/Ausführungspfadprüfung](DGN_007_PREMISE_SOURCE_REVIEW.md)
   ist abgeschlossen: Procedure-Queries werden auch unter AUTO erfasst;
   asynchrone Persistenz ist keine belegte Publikationsverzögerung. Eigene
   Calls, Ergebnismessung und erster Cleanupabschluss sind nutzbar, aber
   kontinuierlicher QS-Zustand, vollständiger Basisabschluss, interne
   Intervallaktivierung und geschlossene Coordinatorherkunft bleiben offen.
   Der konkrete [Beobachtungs-/Herkunftsvertrag](DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md)
   liegt jetzt als `PROPOSED` vor: acht Stages, vollständige Raw-/Gruppen-/
   Coveragebindung, zwölf tatsächliche Calls, getrennte Pulsgrenze,
   Coordinator-Vertrauensquelle und endliche Größen-/Poll-/Kostenlimits.
   Diese Obergrenzen sind vorgeschlagen, nicht runtimevalidiert; Sättigung
   bleibt bedingt, punktweise States belegen keine Kontinuität. Die äußere
   256-KiB-Grenze belegt heute keine Gesamtgrenze im vorher puffernden Proxy.
   Der [Suffizienzreview](DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md) ist abgeschlossen: unter unabhängig
   geschlossenem Callumfang und injektiver kohärenter Zählung trägt Sättigung
   Callerfassung; vollständige keyweise Stageledger tragen kollektiv I0/I1.
   Durchgängiges RW/ALL ist ein getrenntes konservatives Methodengate,
   aus Counts nicht bewiesen und hier nicht aufgehoben. Der heutige Pfad
   liest Live-Dateien und adressiert Namen; Bundle-/Zugangs-/Hostgrenze,
   Acquisition-/Floatregel und Kostenmachbarkeit bleiben tatsächlich offen.
   Das getrennte [Sättigungs-/Acquisition-Gegenmodell](DGN_007_SATURATION_COUNTERMODEL.md)
   prüft jetzt den Zählschluss mit synthetischen Ausführungstokens und getrennten
   Claims für Callerfassung, Bucketzuordnung und QS-Zustand. Die alte 42-Test-
   Voraussetzungssuite bleibt erhalten. Keine reale QS-Einzelidentität oder
   Runtime-/Methodenfreigabe. Das konkrete
   [Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md) ist vorbereitet:
   Acquisition-/Count- und Floatkandidat, ausführbare Freeze-/Actor-/CID-/
   Host-/Zugangsgrenzen sowie gleichzeitige Streaming-/Poll-/Kostenlimits.
   Alle Methodengates bleiben offen; normative Auswahl braucht eine ausdrückliche
   neue Entscheidung. Der [Offline-Quellenbundle-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md)
   ist statisch implementiert: feste 27 Mitglieder, originale Gitblobs,
   getrennte Rohbyte-/LF-Bindung und deklarierte AST-Imports mit Manipulationsfixtures.
   Keine SQL-/Launcher-Runtime oder tatsächliche Ausführungsattestation.
   Die getrennte [Prozess-/Manifestkantenprüfung](DGN_007_EXECUTION_EDGE_VERIFIER.md)
   ist statisch implementiert: Python-3.12-Ganz-AST-Profil, sechs SQL-only-Manifeste,
   14 Quellenhashes und SQLCMD-Gegenproben. Import-/Launcherentwurf PROPOSED,
   tatsächliche Importumgebung und verwendete Runtimebytes offen. Der getrennte
   [synthetische Streaming-/Budgetprototyp](DGN_007_STREAMING_BUDGET_PROTOTYPE.md) ist implementiert:
   portable Budgetgegenproben und feste eigene Linux-Kindfälle, ohne Integration
   in Runtimequellen oder Methoden-/Runtimeattestation. Die getrennte [numerische Pipelinegegenprobe](DGN_007_NUMERIC_PIPELINE_COUNTERMODEL.md) ist implementiert: 28 synthetische Tests trennen Oracle, deklarierte Fragmentrundung, vorgegebenen Text und bestehende Consumergewichtung. Keine SQL-Konversionsemulation, Epsilon- oder Methodenfreigabe. Der konkrete [Import-/UsedBytes-Entwurf](DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md) liegt als `DESIGNED` vor: feste Import-Only-Einstiege, kontrollierter Rohbyte-Loader, vertrauenswürdiges Interpreter-/Stdlibprofil, getrennte Receipts und begrenzter eigener Cleanup. Der erste Implementierungsteil ist das getrennte [Eingangsprotokoll](DGN_007_IMPORT_PROBE_INPUT_PROTOCOL.md): unveränderter 27-Member-Git-/Kantenvorcheck, eingefrorene neun Python-Rohbytes und begrenzte binäre Rahmung mit Kontext- und Manipulationsgegenproben. Keine Worker- oder Kandidatenimportausführung und kein UsedBytes-Claim. Die getrennte [synthetische Memory-Loader-Komponente](DGN_007_MEMORY_LOADER_FIXTURE.md) ist implementiert: ausschließlich feste Fixturebytes, tatsächliches Compile/Exec und objektgebundene Beginn-/Abschlussreceipts. Kein DGN-Import oder Importauflösungsnachweis; DGN-Attestationsflags bleiben false. Der getrennte [Interpreter-/Stdlib-Profilvorschnitt](DGN_007_IMPORT_RUNTIME_PROFILE.md) ist implementiert: begrenzte aktuelle Bootstrapmetadaten und Vergleich gegen separat deklarierte Baseline. Keine Trust- oder bereits ausgeführte Bibliotheksbyteattestation; die gewählte Kontrollruntime bleibt eine ausdrücklich benannte Annahme. Der [skalare Parent-/Worker-Profilbindungsvertrag](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md) liegt als `DESIGNED` vor. Der getrennte [reine Profilvergleich](DGN_007_IMPORT_PROFILE_BINDING_MATCHER.md) ist implementiert: 38 synthetische Tests prüfen exakte deklarierte Installation und Workerinventur, eingefrorenen Eingangs-/Ordinal-/Phasenkontext sowie gemeinsame Metadatengrenzen. Sein Match attestiert keine tatsächliche Workerbeobachtung, Herkunft oder Consumption. Die tatsächliche Prozessanbindung bleibt unimplementiert. Die getrennte lokale Record-Rückgabe des Profilvorschnitts ist jetzt implementiert: `observe_current_interpreter_records` liefert ausschließlich die tatsächlich aufgenommene und vollständig geprüfte Abschlussaufnahme, bei Ablehnung keine Records. Gehaltene Liveanker sind kein dauerhaft gültiger Zustand des Modulcaches; spätere aktuelle Runtimeverwendung braucht eine frische Aufnahme. Legacyreports, Bootstrapimports und Grenzen bleiben erhalten. Die konkrete Bootstraproute ist jetzt im [Profilbindungsentwurf §8](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#8-konkreter-bootstrap--und-projektionsvorschnitt) festgelegt: geplante Scriptquelle als `__main__`, unveränderter Profilmodulname, benannte direkte Stdlibimports und Vorinitialisierung der Sysconfigwerte ohne zusätzliche Projektimports. Feldherkunft, frische Aufnahme, erneute Livekohärenz und engere Scalarformen sind getrennt beschrieben. Die getrennte importneutrale skalare Projektion ist jetzt im bestehenden Profilmodul implementiert: frische Aufnahme, vollständige private primitive Tupel, erneute Livekohärenz vor und nach Projektion sowie zusätzliche separat gewählte und gegen Factorycode/Closure geprüfte FileFinder-Hookbindung; bei Ablehnung keine Skalare. Dies attestiert keine unabhängige Factoryherkunft oder tatsächlichen Worker. Eine getrennte lokale Bootstrap-Charakterisierung unter CPython 3.12.3 erfasste 85 Modulnamen mit genau zwei Controls; dies ist keine operative Sollinventur. Der [konservative Größenbeleg](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#9-charakterisierte-bootstraproute-und-größenuntergrenze) zeigt bereits mindestens 16.449 Bytes für das vollständige Modularray und 21.108 bis 21.144 Bytes für die gemeinsame Metadata einschließlich Header, unverändertem Input82 und Kontext. Die heutige benannte JSON-Form ist damit für diesen vollständigen charakterisierten Namenumfang nicht darstellbar; andere Routen und Installationen sind dadurch nicht ausgeschlossen. Keine Capanhebung, Filterung oder Digestersetzung ist freigegeben. Der vollständige Linux-/Python-3.12-Import-Only-Prototyp bleibt offen; der getrennte Darstellungs- und Digestentwurf aus Profilbindungsentwurf §10 liegt als DESIGNED vor. Die separat vorgewählte vollständige Kontrollfixture und reine Größenprüfung in §11 belegen gemeinsame Metadata von 17.127/17.113/17.091 Bytes; der §10-Tupelkandidat überschreitet das unveränderte 16.384-Byte-Cap. Neuer Sizer34/34 und Legacy27/40 ohne SKIP. Der getrennte verlustfreie Stringpoolentwurf in §12 liegt als DESIGNED vor, mit eigenen lokalen Pools je Form und unveränderten Inhalten/Caps einschließlich höchstens 256 Poolwerten. Der eigene reine Pool-Sizer in §13 bestand 37/37 isolierte Gegenproben ohne SKIP und die vollständige neue 3×5-Rechnung: maximal 9.389 Bytes einschließlich Header und 204 Poolwerte, vollständig unabhängig nachgerechnet und rückgewonnen. Der getrennte experimentelle Formcodec in §14 bestand 41/41 isolierte Gegenproben ohne SKIP; die vollständige Originalfixture bestand alle 3×5 Frames, Feldrückgewinnung, kanonischen Repack und drei eigene Digestdomains je Ordinal. Das gesamte Fünf-Formen-Set umfasst 28.264/28.257/28.246 Bytes. Originalauswahl und Inputrahmen bleiben unverändert, keine neue Aufnahme oder Nonce. Der unabhängige Nachreview bestätigte sämtliche Frames, Feldrückgewinnung und Digests aus den unveränderten Originaleingaben ohne Codec-/Helper-Replay. Der eigene reine kombinierte Eingangsprototyp in §15 bestand 34/34 isolierte Gegenproben ohne SKIP und die neue vollständige Originalfixtureprüfung: drei Frames mit jeweils 9.389 Metadata-/Headerbytes und 130.837 unveränderten Bodybytes, insgesamt 140.226 Bytes. Tatsächliche vollständige Feld-/Rawbyterückgewinnung und Repack sowie unabhängige Stdlib-Nachrechnung ohne Replay bestanden. Alle gleichzeitig geltenden Caps bleiben erhalten; 64 KiB begrenzen ausschließlich die fünf Metadataausgaben. Die konkrete operative Bootstrap-/Kanalreihenfolge in §16 liegt als DESIGNED vor: importneutraler PRE-Vorschnitt, vollständiger Profilvergleich vor Bodyfreigabe und vollständige Eingangsprüfung vor Importfreigabe, unveränderte gemeinsame Caps und gehaltene Kontrollquellenführung. Der reine Kontrollbootstrapquellengenerator in §17 bestand 32/32 ausschließlich synthetische Gegenproben ohne SKIP unter CPython 3.12.14; er ist keine operative Workerroute. Die getrennte [Sysconfig-Vorinitialisierung §18](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#18-feste-sysconfig-vorinitialisierung-gehaltener-kontrollquellen) bestand 53/53 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die private native Auswahl nach [§19](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#19-private-auswahlgrundlage-vor-einer-vollständigen-operativen-inventur) ist mit genau einem begrenzten Versuch und unabhängigem Prozess-/Record-POST abgeschlossen. Die additive reine [Inline-Metadata-Syntaxquelle §20](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#20-reine-additive-inline-metadata-syntaxquelle) bestand 80/80 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste Fixture-Label-Fehllauf bleibt getrennt dokumentiert. Die additive reine [Inline-Metadata-Semantikquelle §21](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#21-reine-additive-inline-metadata-semantikquelle) bestand nach zwei engen Fixturekorrekturen 108/108 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 106/108-Lauf bleibt getrennt dokumentiert. Vollständige deklarative M/IP/S15/P11/D9-Semantik, unveränderter benannter Originaldigest und Providerkohärenz sind geprüft. Die additive reine [Inline-Profilreporterquelle §22](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#22-reiner-additiver-inline-profilreporter) bestand im einzigen isolierten Lauf 149/149 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige Scalarprojektion, eigener REPORTED-Pool, atomare begrenzte Records und getrennte Original-/Reportdigests sind geprüft; vier frühere Builder bleiben erhalten. Die reine begrenzte [Inline-Header-/Metadata-Aufnahme §23](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme) bestand im einzigen isolierten Lauf 174/174 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Exact-Chunktype-/Größenvorläufe, vollständige deklarative M-Semantik und atomare gehaltene Rückgabe sind geprüft; fünf frühere Builder bleiben erhalten. Die additive reine [K-Domain-/Commandquelle §24](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands) bestand im einzigen isolierten Lauf 209/209 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständiger K8-/D9-Vorlauf, eigene headerfreie E4-K-Domain und atomare kanonische Commands gegen separat gehaltene Callerwerte sind geprüft; sechs bisherige Builder und 174 alte Tests bleiben erhalten. Die additive reine [Inline-Metadata-Callerquelle §25](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich) bestand nach zwei engen Fixturekorrekturen 243/243 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 241/243-Lauf mit zwei Fehlern vor Matcheraufruf bleibt getrennt dokumentiert. Beide vollständigen Formen und Semantiken, zwei eigene Originalinputdigests und vollständiger Abgleich gegen separat gehaltene I7/W6/K8 sind geprüft; sieben bisherige Builder und 209 alte Tests bleiben erhalten. Die additive reine [Inline-Rawbodyaufnahme §26](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies) bestand nach einer engen Fixturelabelkorrektur 272/272 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 271/272-Lauf bleibt getrennt dokumentiert. Vollständige Formen und Größen vor Hashes, beide tatsächlichen D9 und neun Rawhashes vor Callerabgleich sowie atomare Originalbodyrückgabe sind geprüft; acht bisherige Builder und 243 alte Tests bleiben erhalten. Die additive reine [Profilrecord-Reassemblierung §27](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords) bestand im einzigen isolierten synthetischen Lauf 304/304 Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige begrenzte Control-/Envelopeformen, interne Konsistenz, kanonische Controls und tatsächlicher Footerhash vor Callerordinal sowie atomare Originalrecordrückgabe sind geprüft; neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei enge Fixturelabelkorrekturen wurden vor dem ersten Lauf reviewt; kein ausgeführter Fehllauf. Die additive reine [Inline-Profil-Callerquelle §28](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich) bestand im einzigen isolierten synthetischen Lauf 341/341 Gegenproben ohne SKIP unter CPython 3.12.14. Beide vollständigen R4-Formen/Semantiken, Actual-Pool-Repack und vollständiger separater Callerabgleich sind geprüft; die Matchfunktion berechnet keinen SHA. Zehn frühere Builder und 304 alte Methoden bleiben erhalten. Vorreviewkorrekturen und genaue Grenzen stehen in §28. Die additive reine R→BODY_RELEASE-Planquelle aus §29 bestand im einzigen isolierten synthetischen Lauf 378/378 Gegenproben ohne SKIP unter CPython 3.12.14; elf alte Builder und 341 alte Methoden bleiben erhalten. Die additive reine INPUT_COMPLETE-Quelle aus §30 bestand im einzigen isolierten synthetischen Lauf 413/413 Gegenproben ohne SKIP unter CPython 3.12.14; zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige Record-/Footer→R-Calleradapter aus §31 ist rein additiv implementiert und im isolierten synthetischen Lauf mit 460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden bleiben erhalten. Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente) ist im isolierten synthetischen Lauf mit 66/66 PASS ohne SKIP geprüft. Reservierungen, ganze Slot-/Zustandsbindung, sticky Fehler und einmaliger Fakecleanup sind lokal belegt; kein tatsächlicher Kanal-/Loader-/Absenznachweis. Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen. Frische operative Auswahl, inline Empfang/Reporting, tatsächliche Parent-/Worker-Anbindung, feste Quellenauflösung, tatsächliche DGN-Loaderverwendung und Importabschluss sowie begrenzte eigene Worker mit unabhängigem Cleanup bleiben getrennte Gates. Die charakterisierte Kontrollfixture ist keine operative Workerbaseline; Migration bleibt offen. Sein Claim bleibt auf tatsächlich abgeschlossene Top-Level-Imports begrenzt; keine vollständige UsedBundle-, SQL-, Acquisition- oder Methodenattestation.
   Erst nach
   tragfähiger Methodenentscheidung gemeinsam versionierte Umsetzung.
   Keine implizite OFF-/CLEAR-/Laständerung.
   Bestehende Guards, Fehler und DEC-068 bleiben erhalten;
   Ursache und Behebung offen.
   Einzelheiten stehen im
   [Producernachweis](DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md).
   Keine identische Wiederholung oder Toleranzkorrektur ohne neue Evidenz.
   Die interne Capture-Rückgabe ist lokal vorbereitet und unabhängig
   geprüft, ihre Veröffentlichung und Integration sind zunächst zurückgestellt.
   Nach der G13-Klärung folgt die interne verlustfreie Capture-Rückgabe:
   den vollständigen Body und tatsächlich geprüfte Phasen übernehmen,
   Rückgabe erst nach erfolgreichem Harness-Cleanup und erstem erfolgreichen
   unabhängigen Abwesenheitscheck. Counts, CLI und Fehlerprioritäten bleiben
   gleich; Recovery liefert niemals einen erfolgreichen Capture-Beleg.
   Dies erzeugt keine RunRecords oder Runtimeattestation. Danach folgen
   Coordinator-Freeze, Ressourcen, tatsächliche serielle Reihenfolge und
   präzise Budgets; erst danach frische prospektive Bestätigungsläufe.
   Die bisherigen Captures belegen keine Regression, Ursache, Mitigation oder
   Capstone-Freigabe.
   Der Compatibility-Vorfix ersetzt im älteren Teilnehmerpfad die ungültige
   Property-Abfrage durch den Katalogwert und lehnt NULL oder Werte ungleich
   170 vor der Evidenzausgabe ab. Die Adaptervalidierung besitzt denselben
   NULL-Schutz. Die Plan- oder Laufzeitprofilbedingung bleibt Folgearbeit.
   Die acht statischen Compatibility-Tests bestanden. Am 2026-10-06 bestanden
   zusätzlich acht T-SQL-Guard-Fixtures (170, 160, NULL und fehlende Zeile je
   SQL-Quelle), die echte Abfrage eines fehlenden Zielnamens sowie die
   Kontextprojektion mit synthetischen Query-Store-Optionen und echtem
   `master`-Katalogwert auf SQL Server 2025 Developer `17.0.4075.5`.
   Aufruf: `python Tests/Static/test_dgn007_compatibility.py --container NAME
   --confirm-disposable-instance`. Die frische eigene Instanz war vor und
   nach den lesenden Prüfungen leer und wurde anschließend nach
   Eigentumsprüfung entfernt; ihre Abwesenheit wurde unabhängig bestätigt.
   Die ersten Versuche scheiterten an der fehlenden Query-Store-Optionszeile
   in `master` und zählen nicht als erfolgreiche Evidenz. Der Nachweis gilt
   nur für Katalogzugriff, Guard- und Projektionsfixtures; er enthält keine
   echte Compatibility-Änderung und keinen vollständigen Teilnehmerlauf.
4. Eine weitere `LABINT-004`-Matrixaussage erst aktivieren, wenn ein zusätzlicher gelber Slice samt Safety- und Szenariofreigabe sie benötigt.
5. Docker-/Podman-Ressourcen-, Netzwerk-, Hyper-V- oder gemischte Topologien nur bei einer konkret nachgewiesenen fachlichen Abhängigkeit bearbeiten.
6. Änderungen an `SQL_Server_Lab` bleiben ohne konkrete Fähigkeitslücke und ausdrückliche Freigabe gesperrt.

## 6. Sicherheits-, Datenschutz- und Quellenstatus

- Szenariodefinitionen enthalten nur synthetische Daten, relative Projektpfade, öffentliche Versionsbezeichnungen und generische Rollen.
- Gelbe und rote Szenarien behalten ihre bestehenden Safety-Gates; `RES-003` benötigt zusätzlich dedizierte Wegwerfinfrastruktur, High-Impact-Bestätigung, Kill-Switch und Laufzeitbudget.
- `DGN-007` setzt validierte Query-Store- und Extended-Events-Evidenz voraus.
- Der SQL-Server-2025-Delta-Review ist in `SQL_SERVER_2025_DELTA_REVIEW.md` abgeschlossen: CE Feedback für Ausdrücke und zeitgebundene XE-Sessions sind in bestehende Verträge übernommen; vier Infrastruktur-/Abhängigkeitsthemen bleiben zurückgestellt, Vector/KI außerhalb des Curriculums.
- Aktuelle Herstellerdokumentation allein ist weiterhin kein Implementierungs- oder Runtime-Nachweis.

### IDX-012: Speicherfolge nach vollständig abgeschlossener PR174-Integration

PR174-Head d1b3395810461bb849409efc93af0a9daf8f3694 gegen Basis efc9d0fa820e633f1159f22d7b151ac74fc5eb06 bestand alle 13 Headchecks. Squash 2d8a6005a9300094af573ae05e30b9dea69192e6 bestand alle sieben ausgewählten Main-Workflows einschließlich KI-Matrix und Cleanup. Vollständiger Tree f03f807aadbf3e52d7ba221a2861de444e5896fc identisch; main/origin/main synchronisiert, eigener Compile-Branch lokal und remote entfernt. Der [Rebuildnachweis](SQL_SERVER_2025_AI_IDX012_REBUILD_REVIEW.md) belegt die beiden positiven Lifecycles unter Erhalt der historischen FAILs.

Unmittelbar folgt der [begrenzte DB-Speichernachweis](SQL_SERVER_2025_AI_IDX012_STORAGE_REVIEW.md) auf codex/sql2025-ai-idx012-storage, Basis 2d8a6005a9300094af573ae05e30b9dea69192e6. Die ausdrückliche weitere lokale Wellenfreigabe gilt; neues endliches Budget genau ein stabiler Kandidat/höchstens zwei eigene serielle Container, keine Korrekturwelle. Drei vollständige read-only DB-Katalogaufnahmen ergänzen den festen Drop-/Commit-/Rebuildpfad. Effektgrenzen bleiben eigene Preview/MAXDOP/999–1000 Rows/300 s einschließlich Startup/20 s SQL-Recovery innerhalb 60 s gesamtem Cleanup. Unabhängiger Quellenreview und tatsächliche Runtime vor Ergebnisclaim erforderlich. Kein isolierter Indexkosten-, TempDB-, Writes-, Worker- oder TP-PERF-Claim; alte geschlossene Budgets werden nicht wiederverwendet. Gesamtworkstream und Heartbeat bleiben aktiv.

Der erste Storage-Lauf 0B6514D624F84921 scheiterte vor Indexbau am SQL-Guard (51003/State1/Zeile59); vollständige Storageaufnahme fehlt, tatsächliche abweichende Guardgröße UNKNOWN. Restore Preview/MAXDOP0/0, unabhängige DB-/eigene CID-/Namensabwesenheit und gesamter Cleanup12,353s bestanden; LedgergeschlossenFAIL, kein zweiter Lauf/keineKorrekturwelle. Eine getrennte Capturefolge mit getrennt vor Subqueries erfasstem Transaktionsstatus und ausgegebenen tatsächlichen Guardwerten ist im [Speichercheckpoint](SQL_SERVER_2025_AI_IDX012_STORAGE_REVIEW.md) vorbereitet. Das frühere Budget wird nicht zurückgesetzt. Neue Admission erst nach enger unabhängiger Quellenclosure und vollständiger PR-Integration dieses Checkpoints; weitere lokale Wellenfreigabe gilt. Gesamtworkstream und Heartbeat bleiben aktiv.

PR175 ist vollständig abgeschlossen: Head 7a27ba984834a8d75f5d3d7a39db178c6f2fb29b gegen Base 2d8a6005a9300094af573ae05e30b9dea69192e6 mit 13 SUCCESS; Squash 36c2d7aacd4a27185968128f72ae4a8164e120b1 mit sieben ausgewählten Main-SUCCESS. Vollständiger Tree ee6fb8ab17ed0e1de9cc017d95523af66f2a9617 identisch, main synchronisiert und eigener Branch lokal/remote bereinigt. Die Capturefolge auf codex/sql2025-ai-idx012-storage-capture scheiterte erneut vor Indexbau, nun mit tatsächlichen Guardwerten: Token DCC9B668B1234055, 999 Rows, Indexcount 0, Transaktion 0/0, zwei Dateien, 43 interne Tabellen und 199 Partitionen. Limit 128 ist zu klein; der erste FAIL ohne Counts bleibt einzeln ungeklärt. Restores 0/0, unabhängige DB-/CID-/Namensabwesenheit und gesamter Cleanup 12,658 s bestanden; Captureledger geschlossen FAIL, kein zweiter Lauf.

Die neue [begrenzte Katalogfolge](SQL_SERVER_2025_AI_IDX012_STORAGE_REVIEW.md#tatsächliche-capturefolge-und-neue-kataloggrenze) nutzt die weitere lokale Wellenfreigabe: vollständige Aufnahme bis 512 Partitionen/unverändert 120000 UTF-16-Bytes; übrige Guards, DB-/Dateimaxima, Optionen, 999–1000 Rows, 300 s einschließlich Startup und 20 s SQL-Recovery innerhalb 60 s Cleanup bleiben unverändert. Neuer unabhängiger Parent/Ledger: genau ein stabiler Kandidat/maximal zwei serielle eigene Container, keine Korrekturwelle; die beiden alten FAIL-Budgets bleiben geschlossen. Admission erst nach engem Quellenreview und öffentlichem Pfad-/Hashschluss; vollständiger PR-/Integrationsabschluss dieses zusammenhängenden Capture-/Grenzenschnitts bleibt Pflicht. Gesamtworkstream und Heartbeat bleiben aktiv.

Die Katalogfolge bestand danach beide vollständigen eigenen Lifecycles: Tokens 2D00C5B617964E25/B249FF1FEB194EC3, tatsächlicher Build 17.0.5005.3, WARN_OPTIONAL_EVIDENCE_SKIPPED. Drei vollständige Storageaufnahmen je Lauf mit 199/203/203 Partitionen und 43/45/45 internen Tabellen; alle Scalars 102438/104908/104908 UTF-16-Bytes ohne Trunkierung. Tatsächliche Originalrestores 0/0, unabhängige DB-/CID-/Namensabwesenheit und gesamter Cleanup 12,686/12,624 s bestanden. Beide Admissionen des stabilen Kandidaten sind geschlossen, Budget ausgeschöpft ohne Korrekturwelle. Alle bisherigen DML-/Quellen-/Drop-/Commit-/Rebuild-/Recallkontrollen bestanden. [Ergebnisse und Grenzen](SQL_SERVER_2025_AI_IDX012_STORAGE_REVIEW.md#katalogfolge-zwei-vollständige-positive-lifecycles); Generation UNKNOWN, Freshness OBSERVED_AFTER_REBUILD_ONLY, isolierte Kosten und vollständige Runtimequalifikation offen. Beide alten FAIL-Ledger bleiben erhalten. Der konsistente Ergebnisstand wird jetzt über PR integriert; anschließend nächster zulässiger Schritt tatsächliche, getrennt interpretierte Session-/TempDB-/DB-Dateikostenpunkte, keine reine Indexkostenbehauptung. Gesamtworkstream und Heartbeat bleiben aktiv.

### IDX-012: Kostenfolge nach vollständig abgeschlossener PR176-Integration

[PR 176](https://github.com/gecompat/SQL_PerformanceSchulung/pull/176) ist nach
13 erfolgreichen Headchecks auf cd28bf5ccf11ba6865c410b3c7e3a4f8c1384606 in
018c678f55660a559bfd2acc4eb3f56675bce8eb integriert. Vollständiger Tree
f68328b2943b93a306874dbee76c015e36e6fdfa identisch; alle sieben ausgewählten
Main-Workflows bestanden: 38174402097/38174402166/38174402101/38174402066/
38174402139/38174402067/38174402085. main synchron, sauber; eigener
Storage-Capture-Branch lokal/remote entfernt, keine eigenen Container verblieben.

Der [Phasenkostenschnitt](SQL_SERVER_2025_AI_IDX012_COST_REVIEW.md) auf
codex/sql2025-ai-idx012-costs, Basis 018c678f55660a559bfd2acc4eb3f56675bce8eb,
ist nach zwei Kandidaten mit FAIL angehalten. Die weitere lokale Wellenfreigabe
gilt; der neue eigene Parent/Ledger erlaubte maximal zwei stabile Kandidaten/
vier serielle eigene Container und verlangte zwei positive Lifecycles desselben
Kandidaten. Effekte unverändert: eigene Preview/MAXDOP, 999–1000 Rows,
300 s einschließlich Startup, 20 s SQL-Recovery innerhalb 60 s gesamtem Cleanup.
Keine isolierten Indexbau- oder vollständigen Worker-Kosten. Admissionen erst
nach öffentlicher Quellenbindung und engem unabhängigem Review.

C1 448381C255F044D1: native Windows-ODBC-sqlcmd verwirft die neuen unquotierten
-v-Drivepfade vor Kosten-SQL/erstem Indexbau. Setup/Enable/Source-/Storagebaseline
bestanden; beide tatsächlichen Restores 0/0 und unabhängige DB-/eigene Namens-/
vollständige CID-Abwesenheit belegt. Gesamter Cleanup 13,2039358 s;
closed=true/FAIL, keine zweite C1-Admission. C2 änderte ausschließlich die
feste Include-Pfadübergabe auf Prozess-ENV. Der enge ENV-Review fand vor
Admission einen Windows-Case-P2; alle reservierten Schreibvarianten werden
entfernt. Unabhängige Closure, 22 Controllergegenproben PASS; keine zusätzliche
Runtime durch diese vorbereitende Korrektur.

C2 C7273FFC05C04F70: NativeClient meldet wörtlich '$(CostFrameFile)': Invalid
filename beim ersten :r vor Kosten-SQL/Indexbau. Ursache über die unverarbeitete
Dateinamenvariable hinaus UNKNOWN, kein Kostenclaim. Beide tatsächlichen
Originalrestores 0/0, neue Attestation, markergebundener Drop, DB-Abwesenheit
und unabhängige eigene Namens-/CID-Abwesenheit PASS; Cleanup 13,5870011 s.
Zwei Kandidaten/zwei Admissionen geschlossen, Budget regulär beendet;
unbenutzte Slots sind keine weitere Korrekturwelle. Öffentlicher Kostenmodus
jetzt mit FAIL_CLIENT_INCLUDE vor jedem SQL/Setup gesperrt. 23 Controller-
gegenproben PASS; unveränderte Kosten-/Selektortests nicht erneut ausgeführt.

Die bekannten DML-/Rebuild-/Storagemodi bleiben verfügbar. Writes/TempDB/Worker,
vollständige IDX-012-Abnahme, Minimalrollen und Hard-Abort bleiben offen.
Checkpoint über PR integrieren; anschließend nächster unabhängiger zulässiger
Schritt: tatsächliche IDX-012-Versions-SKIPs auf 2019/2022 vor Setup. Eine
Kostenwiederaufnahme benötigt einen getrennten endlichen Clientvertrag,
geänderte Eingaben und Quellenclosure nach vollständiger Checkpointintegration;
keine unveränderte Probe, keine stille Budgetrücksetzung. Gesamtworkstream und
Heartbeat aktiv; übrige Provider-/Cloud-/ONNX-Gates bleiben unverändert.

### IDX-012: Benutzererweiterung nach vollständiger PR177-Integration

[PR 177](https://github.com/gecompat/SQL_PerformanceSchulung/pull/177) ist
vollständig abgeschlossen: Head 5a80dbdb6c3cbe7af4928fd843ec97bdd0a6f823 gegen
Base 018c678f55660a559bfd2acc4eb3f56675bce8eb mit 13 SUCCESS;
Squash 4dc956df3f66c21c672e9add30405853bc1e4ca8 mit sieben ausgewählten
Main-SUCCESS (38176790631/38176790669/38176790632/38176790662/38176790708/
38176790645/38176790629). Vollständiger Tree
63adece444541ba2913e7ee33d207a40e2c17ed7 identisch; main/origin/main sauber
synchronisiert, eigener Kostenbranch lokal/remote entfernt. Keine eigenen
Container verblieben. C1/C2 bleiben geschlossene FAILs ohne Kostenframes.

Der Benutzer verlangt jetzt ausdrücklich mehr als zwei Testzyklen. Die
lokale Entwicklungswelle erhält sechs kohärente Test-/Korrekturkandidaten je
Schnitt. Die Kostenfolge verwendet denselben Ledger: C1/C2 zählen mit,
maximal sechs Kandidaten/zwölf serielle eigene Container. Kein unveränderter
Retry nach FAIL; Quellenänderung und gezielte Risiko-Closure erforderlich.
Keine Wiederöffnung alter Ledger und keine Änderung von Provider-/Cloud-/
ONNX-/roten Hostgrenzen. Unbekannter Modell-/Tokenverbrauch bleibt unbekannt.

Unmittelbar läuft die [C3-Clientkorrektur](SQL_SERVER_2025_AI_IDX012_COST_REVIEW.md#benutzererweiterung-und-dritter-kandidat)
auf codex/sql2025-ai-idx012-cost-bundle, Basis 4dc956df3f66c21c672e9add30405853bc1e4ca8.
Feste öffentliche Quellen werden mit vier Batchgrenzen in genau einer
eigenen temporären SQL-Datei bis 160000 UTF-8-Bytes zusammengefügt;
Startupskriptvererbung ist ausgeschlossen. Aufnahme und eigener Cleanup
werden eng unabhängig geprüft; Admission erst danach. SQL-Effekte,
Countersemantik, Originalrestore und 300 s einschließlich Startup/20 s
SQL-Recovery innerhalb 60 s gesamtem Cleanup bleiben unverändert.
28 betroffene Controllergegenproben bestanden. Quellenreview-P2 vor
Admission korrigiert: Die neue Input-Lease verlangt bestätigtes Prozessende
vor Dateientfernung; sonst FAIL_CLEANUP ohne konkurrierende SQL-Recovery.
Unabhängige Closure ohne weitere Befunde erteilt; aktuelle Controllerbindung
5D7964A85FE8041726901A66BA4629633119BDB97491972E25F82F41CF685705 und
Parent EBF13336594B74558567F331E5A7A7BD87C128D47B6388946461067B5E47BB36.
Kein C3-Runtimeclaim vor
tatsächlicher Ausführung. Zwei positive Lifecycles desselben stabilen
Kandidaten erforderlich. Danach konsistenter PR-/Main-/Sync-/Cleanupabschluss
und unmittelbar nächster zulässiger Schritt Versions-SKIPs 2019/2022.
Gesamtworkstream und Heartbeat bleiben aktiv.


C3 bestand anschließend beide vollständigen Kostenlifecycles, Tokens
3E2901DC14FA4A4E/064EB3DBC5FC4B54, tatsächlicher Build 17.0.5005.3 und
WARN_OPTIONAL_EVIDENCE_SKIPPED. Beide Phasen je Lauf liefern vollständige
BEFORE/AFTER-Kostenframes in derselben Session; Session-/TempDB-/eigene
DB-Dateideltas sind tatsächlich erfasst, reine Index-/vollständige
Workerkosten bleiben NOT_ESTABLISHED. Alle DML-/Quellen-/Drop-/Commit-/
Rebuild-/Recall-/Storagekontrollen bestanden. Tatsächliche Originalrestores
und unabhängige Attestation 0/0, markergebundener Drop, neue DB-Abwesenheit,
eigene vollständige CID-/Namensabwesenheit und temporäre Dateiabwesenheit
bestanden; Cleanup 13,7552919/13,3577670 s. Beide C3-Admissionen geschlossen
ohne failure. Kostenfolge nach drei Kandidaten/vier Admissionen beendet;
die freien Zyklen werden nicht ohne neue Frage verbraucht. Historische
C1/C2-FAILs erhalten. [Tatsächliche Werte und Grenzen](SQL_SERVER_2025_AI_IDX012_COST_REVIEW.md#c3-zwei-vollständige-tatsächliche-kostenlifecycles).
Dieser konsistente Stand wird über PR integriert; danach unmittelbar
tatsächliche Versions-SKIPs 2019/2022. Gesamtworkstream und Heartbeat aktiv.


### IDX-012: Versionsfolge nach vollständig abgeschlossener PR178-Integration

[PR 178](https://github.com/gecompat/SQL_PerformanceSchulung/pull/178):
Head 528e770d237e1ac59738fd7712bbf99f4f1b8af7 gegen
Base 4dc956df3f66c21c672e9add30405853bc1e4ca8, alle 13 Headchecks SUCCESS.
Squash 1aead3c727e90d907bf20048e2feebca41642b68, vollständiger Tree
b3e6a389fd9373d4d8180fd6adf73ea3cf533d01 identisch. Alle sieben ausgewählten
Main-Workflows SUCCESS: 38179207709/38179207543/38179207514/38179207439/
38179207560/38179207542/38179207525. main/origin/main sauber synchronisiert;
eigener Kostenbranch lokal und remote entfernt, keine eigenen Container
oder temporären Kosteninputs verblieben.

Unmittelbar folgt der [IDX-012-Versionsnachweis](SQL_SERVER_2025_AI_IDX012_VERSION_REVIEW.md)
auf codex/sql2025-ai-idx012-versions, Basis
1aead3c727e90d907bf20048e2feebca41642b68. Ein stabiler Kandidat muss je zwei
tatsächliche 2019-/2022-SKIPs vor Setup erfüllen. Ausdrücklich erweiterte
lokale Wellenfreigabe: maximal sechs Kandidaten/24 serielle eigene Container;
ein FAIL hält an, Folgekandidat nur bei geändertem Ausführungsinput und
geschlossenem vorherigem Lifecycle. Nach vollständigem Vier-Slot-Nachweis
kein unnötiger Verbrauch weiterer Kandidaten. Vorhandene ursprüngliche
Ledger anderer Schnitte bleiben geschlossen.

Unveränderter öffentlicher Preflight, Controllerdefault ohne Storage-,
Rebuild- oder Kostenflags. Genau eine PREFLIGHT/SKIP/SKIP_VERSION-Phase,
OriginalPreview=None und cleanup_ok=false sind erforderlich; dieses Feld
ist keine SQL-Recovery. Neue read-only DB-Abwesenheit und unabhängige eigene
vollständige CID-/Namensabwesenheit nötig. Kein Preview/MAXDOP/Setup/DDL.
Eigene lokale unveränderliche 2019-/2022-Images, vier CPUs/sechs GiB,
300 s einschließlich Startup und 60 s tatsächlichem eigenen Cleanup.
Secret nur ENV, geerbtes SQLCMDINI entfernt; keine Pulls oder Fremdeffekte.

Enge ursprüngliche Guardclosure und aktuelle Controller-/Parent-/Ledger-
Delta-Closure ohne offene P1/P2 vorhanden, keine Runtime durch den Reviewer.
Nach main-Sync unveränderte SHA256: Preflight C9B56105FF001C49D5C2453D2214105C5BEE569E5976D28DCC1EEC344CE30CD3,
Controller 5D7964A85FE8041726901A66BA4629633119BDB97491972E25F82F41CF685705,
Parent 92D9C91D2F830F7B8DC8D82D2B83979BAF5F4A8FABC135F031E450C65D3F5F2D.
Keine unveränderten Tests/Reviews wiederholen. 28 Controllergegenproben
am selben Quellstand bereits PASS; tatsächliche Versionsruntime erst nach
dieser kanonischen Scopebindung. PR-/Head-/Main-/Tree-/Sync-/eigener Cleanup-
Abschluss erforderlich. Minimalrollen, Hard-Abort und vollständige Abnahme
bleiben Folgearbeit. Gesamtworkstream und Heartbeat aktiv.


Die Versionsfolge bestand alle vier eigenen seriellen Lifecycles desselben
stabilen Kandidaten: zweimal tatsächliches 15.0.4490.9 und zweimal
16.0.4295.3; Tokens D95D67B29CBB4BBA/3BFE11AA071F43BC/
D0D5543990174020/F588C8C09C0941AE. Je genau PREFLIGHT/SKIP/SKIP_VERSION,
keine weitere Phase/kein Setup. OriginalPreview=None und cleanup_ok=false
sind kein SQL-Recoveryclaim. Neuer unabhängiger read-only Client bestätigt
jeweils DB-Abwesenheit; eigene vollständige CID und Name unabhängig abwesend.
Cleanup 11,3410314/10,6015398/12,7354592/12,4055188 s; vier Admissionen
closed=true ohne failure. Quellen und Parent innerhalb C1 bytegleich.
Alle Kandidaten bleiben endlich begrenzt; nach diesem vollständigen Nachweis
keine unnötigen weiteren grünen Proben. [Details](SQL_SERVER_2025_AI_IDX012_VERSION_REVIEW.md#tatsächliche-vier-versionslifecycles).
Konsistenten Stand jetzt über PR/aktuelle Head-/Main-Gates/Tree-/Sync-/
eigene Branchbereinigung abschließen. Unmittelbar danach kontrollierte
IDX-012-Fehler-/Recoveryfälle; Minimalrollen, Hard-Abort und vollständige
Runtime-/TP-PERF-Abnahme bleiben zusätzlich offen. Gesamtworkstream und
Heartbeat aktiv.

### IDX-012: kontrollierte Recovery nach vollständiger PR179-Integration

[PR 179](https://github.com/gecompat/SQL_PerformanceSchulung/pull/179):
Head 7152584274b9037db1e210eb50505f9771ef2f8f gegen
Base 1aead3c727e90d907bf20048e2feebca41642b68, sieben Head-SUCCESS;
Squash 99b8df923f144f6e915ff3718addf24582de7224, voller Tree
8f3b19b9f76f60cfd3e8955708f0af28f1819873 identisch. Alle fünf ausgewählten
Main-Workflows SUCCESS: 38180208984/38180209017/38180208983/38180209019/
38180209001. main/origin/main sauber synchronisiert; eigener Versionsbranch
lokal/remote entfernt, keine eigenen Container verblieben.

Unmittelbar folgt die [kontrollierte IDX-012-Recovery](SQL_SERVER_2025_AI_IDX012_RECOVERY_REVIEW.md)
auf codex/sql2025-ai-idx012-recovery, Basis
99b8df923f144f6e915ff3718addf24582de7224. Ausdrücklich erweiterte lokale
Welle: maximal sechs Kandidaten/24 serielle eigene Container; je stabiler
Kandidat zwei Fehler nach Setup und zwei nach qualifiziertem Indexbau samt
vollständiger unabhängiger Sourceprüfung. Kontrollierter FAIL_EXECUTION
bleibt im Ergebnis FAIL; der Parent attestiert ausschließlich dessen
tatsächlich erwartete Auslösung und vollständige Recovery. Frühere Fehler,
Timeout, ungeklärtes Clientende oder FAIL_CLEANUP erfüllen den Fall nicht.
Vier abgeschlossene stabile Fälle nötig; keine unnötigen weiteren Zyklen.
SQL-Effekte, Originalrestores, 999–1000 Rows, 300 s einschließlich Startup,
20 s SQL-Recovery innerhalb 60 s gesamtem Cleanup bleiben unverändert.
30 betroffene Controllergegenproben PASS. Neuer Fehlerpunkt und Parent
vor Admission eng unabhängig ohne neue P1/P2 geschlossen; aktuelle Bindung
Controller DFBC01CAE5428F279BCE1DF8363ECFF0BCD692A507842A0DD2625DBC5F13D6F1,
Parent F9EB8B93AC5AB947EF2F7B09D3F21E916A5A2A3623B56129735748333C1B2A8D.
Die anschließende tatsächliche Runtime bestand alle vier festen Fälle desselben
C1 auf 17.0.5005.3: Setup-Tokens 0D5DA53FBF6B43CE/D86B5FF43CC246A5,
Build-Tokens 3C04F622FC6D4E14/47C9D7AA36DF4A74. Öffentlich je erwartetes
FAIL/FAIL_EXECUTION mit passendem kontrolliertem Fehlercheckpoint; Parent-PASS
nur für diesen Fall samt tatsächlicher Recovery. Alle Originalrestores/
Attestationen 0/0, neue DB-Abwesenheit und eigene vollständige CID-/
Namensabwesenheit belegt; Cleanup 12,6183559/13,0445620/12,7929698/
12,8262864 s, alle Admissionen geschlossen ohne failure. Nach Build je
vier positive/vier tatsächliche 42231-DML-Kontrollen, voller 999-Row-
Quellen-/Distanzabgleich und vollständige eigene Indexmetadaten vorhanden.
Alle Ausführungsquellen samt Parent innerhalb C1 bytegleich; kein Rebuild.
[Ergebnisdetails](SQL_SERVER_2025_AI_IDX012_RECOVERY_REVIEW.md#tatsächliche-vier-fehler--und-recoverylifecycles).
Kosten-/Versionsledger bleiben geschlossen. Hard-Abort, Minimalrollen und
vollständige Runtime-/TP-PERF-Abnahme bleiben offen. Keine Änderung anderer
Repositories/Provider-/Cloud-/ONNX-/roter Hostgrenzen. Gesamtworkstream und
Heartbeat aktiv; regulärer PR-/Integrations-/Sync-/Cleanupabschluss nötig.


### IDX-012: Rollenfolge nach vollständiger PR180-Integration

[PR 180](https://github.com/gecompat/SQL_PerformanceSchulung/pull/180):
Head d29d3ac2e0f64b4c72fa09af7484031c6bc8d8b3 gegen
Base 99b8df923f144f6e915ff3718addf24582de7224, alle 13 Head-SUCCESS;
Squash 6a8c6ca3835f1f88ae63d6588685f19a675dcb7c, voller Tree
055be4f7410f802376be02f47f8c324affb41120 identisch.
Alle sieben ausgewählten Main-Workflows SUCCESS: 38181778703/38181778718/
38181778753/38181778713/38181778747/38181778711/38181778695.
main/origin/main sauber synchronisiert; eigener Recoverybranch lokal/remote
entfernt, keine eigenen Container verblieben.

Unmittelbar folgt der [eingeschränkte IDX-012-Ausführungskontext](SQL_SERVER_2025_AI_IDX012_ROLE_REVIEW.md)
auf codex/sql2025-ai-idx012-roles, Basis
6a8c6ca3835f1f88ae63d6588685f19a675dcb7c. Ausdrücklich erweiterte lokale
Welle: sechs Kandidaten/zwölf serielle eigene Container, zwei stabile
Rollenlifecycles nach engen tatsächlichen Grant-/Revoke-Gegenproben.
Eigenes Login/SID im eigenen Container, nur CREATE ANY DATABASE und
VIEW SERVER PERFORMANCE STATE, keine feste Serverrolle; eigene DB-Owner-
Bindung und vollständige öffentliche DML-/Rebuild-/Storage-/Kostenfolge.
Admin nur für Fixture und dessen Cleanup, keine sa-Demophase. Neues
SKIP_PERMISSION-Gate vor Host-DMV/Setup, übriger Controller unverändert.
Secret nur ENV; tatsächlich gebundener eigener Login-Drop erst nach DB-
Abwesenheit und mit neuem unabhängigem Principal-/SID-Abwesenheitsclient.
300 s inklusive Startup/20 s SQL-Recovery innerhalb 60 s Gesamtcleanup
einschließlich Login-/Containercleanup; keine Fremd-/Host-/Provideränderung.
Noch keine Rollenruntime dieses Scopes. Kein absoluter Minimalitätsclaim,
kein Hard-Abort oder vollständiger Runtime-/TP-PERF-Claim. Vor Admission
enge Quellenclosure und betroffene Gegenproben; regulärer PR-/Integrations-/
Sync-/eigener Cleanupabschluss erforderlich. Workstream und Heartbeat aktiv.

Vor der ersten Rollenadmission enge unabhängige Quellenclosure ohne weitere
P1/P2; zwei P2 zum Phasentupel und konkurrierenden Principal-SQL-Cleanup bei
unbestätigtem Clientende vor Runtime korrigiert. 31 Controllergegenproben und
eine enge rein synthetische Parent-Gegenprobe für genau diesen Unknown-Guard
PASS. Keine Runtime durch den Reviewer. Aktuelle Quellenbindung: Preflight
7FC2A900E2419CDF10590145270F3A06377CBB6A8A49E6E6836860EEE36DB684,
Controller unverändert DFBC01CAE5428F279BCE1DF8363ECFF0BCD692A507842A0DD2625DBC5F13D6F1,
Parent 59B6EF00AFF65FF42B8FD6BFE6EE84AB475E8223BCC32594739B1F9C02C81736.

Tatsächlicher C1-Rollenlauf 803B41BD338040B1 geschlossen FAIL: Rechteentzug-
Gegenproben/Grantrestore, Setup/Owner/Baseline/Storage/Kosten-BEFORE und vier
NO_INDEX-DML-Kontrollen bestanden; Indexbau verweigert internen DBCC TRACEON
mit 2571/State 3, anschließend 42234/State 1. Kein Rollen-/Index-/Rebuild-PASS.
Originalrestores/Attestation 0/0, neue DB-Abwesenheit, tatsächlicher eigener
Login-Drop/neue Principal-/SID-Abwesenheit und voller CID-/Namenscleanup
bestanden (13,0928537 s). Ein tatsächlicher Versuch verbraucht, kein zweiter
unveränderter Lauf. [FAIL und Quellenabgleich](SQL_SERVER_2025_AI_IDX012_ROLE_REVIEW.md#tatsächlicher-erster-fail-und-begrenzte-kontexttrennung).
Innerhalb desselben Sechskandidatenledgers folgt C2 mit geändertem festen
Parent/privater Kontextquelle: nur die beiden vorhandenen Indexbuilds unter
sa, kontrollierte DML/Beobachtung vor/nach jeweils unter tatsächlichem
Operator mit vier geordneten Kontext-/SID-Records pro Kostenphase. Kein
sa-Fallback, keine zusätzlichen Operatorgrants; kein öffentlicher unveränderter
Einzel-Login- oder vollständiger Nicht-sysadmin-Buildclaim. Native Quellen-
bytes/Hashes privat aufnehmen; drei betroffene synthetische Gegenproben PASS,
enge Delta-Closure vor Admission erforderlich. Alle alten FAILs/Grenzen und
gesamte Deadline/ClientEndUnknown-Eigentumsfloors bleiben erhalten.

Enge unabhängige C2-Closure vor Admission ohne P1/P2 zur konkret neuen
Identitäts-/Native-Input-Grenze erteilt. Aktueller Parent
F0341668E58E5FD6C0E00E09DA21579F5B694D8F6C2E44A0944C77E20FA0451A,
feste Kontextquelle E320B1D61E1599C6A63017D15D40575D19D1548FFB5DA0DF42F61272979E3E76.
Privilegierter Kontext nur der exakt erkannte einzelne Index-DDL je Phase;
geordnete Operatorrückkehr, Secret-/Token-/SID-/Lease-/Größenfloors bestätigt.
Keine Runtime oder Tests durch den Reviewer; Closure vor C2-Admission.

C2/A16779D9D401423E geschlossen FAIL_EXECUTION: Msg 156 am unquotierten
reservierten Alias Checkpoint in der ersten nativen Kontextquelle, keine
tatsächlichen Kontext-/Index-/DML-/Rebuild-Ergebnisse. Beide Rechtegegenproben,
Grantrestores und DB-Ownerbindung bestanden; Originalrestores/Attestation 0/0,
neue DB-Abwesenheit, eigener Login-Drop mit neuer Principal-/SID-Abwesenheit
und volle CID-/Namensabwesenheit bestanden (13,0965515 s Gesamtcleanup).
Zwei geschlossene Fehlkandidaten bleiben im selben Sechskandidatenledger.
C3 korrigiert ausschließlich [Checkpoint], Kontextquelle
F78446CF632378D3A2CE31357D2E75879765B75AC9459C8C9161878D3C4B89D0,
Parent unverändert. Drei betroffene synthetische Gegenproben PASS; enge
unabhängige Syntaxdelta-Closure vor Admission erteilt, ursprüngliche C2-
Identitäts-/Privileg-/Lease-/Cleanupsemantik unverändert. Kein neuer
Benutzerfreigabezyklus innerhalb der ausdrücklich erweiterten lokalen Welle.


IDX-012-Rollensplit C3 tatsächlich mit zwei stabilen vollständigen Lifecycles
bestanden: F2BED8B1B7FB4008/CA7DFACE4C9F47D3 auf 17.0.5005.3, sämtliche
Ausführungsquellen und native Eingabebytes gleich. Je beide einzeln entzogenen
Rechte vor Setup SKIP_PERMISSION, tatsächliche Grantrestores/DB-Ownerbindung;
acht geordnete Kontext-/SID-Records, Admin nur für beide Indexbuilds,
DML/Beobachtung/Drop/Commit/Kosten unter Operator; vier positive/vier 42231-
DML-Kontrollen, vollständige 999-Row-Quellenkontrolle, fünf Rebuild-Suchen mit
Recall@5 1 und übrige 998 Texte gleich. Drei Speicherpunkte/zwei Kostenfolgen
mit unveränderten Grenzen; öffentliche Ergebnisse WARN, Generation UNKNOWN,
runtime_qualification NOT_ESTABLISHED. Tatsächliche Restores/Attestation 0/0,
neue DB-Abwesenheit, eigener Login-Drop und neue Principal-/SID-Abwesenheit,
volle eigene CID-/Namensabwesenheit bestanden; Cleanup 13,4958547/13,7201669 s.
C1/C2 FAIL bleiben im selben Ledger; vier eigene Container entfernt. Keine
weitere identische grüne Admission. [Teilnachweis](SQL_SERVER_2025_AI_IDX012_ROLE_REVIEW.md#tatsächliche-zwei-stabile-rollenlifecycles-c3).
Öffentliche Multi-Login-API/absolute Minimalrollen/Hard-Abort und Gesamt-/
TP-PERF-Abnahme bleiben offen. Nächster Schritt: reguläre PR-Integration
gegen aktuelle Basis, alle Head-/Main-Gates, Tree-/Sync-/eigener Branchcleanup;
danach unmittelbar nächster zulässiger lokaler Schnitt. Workstream aktiv.

PR 181 vollständig geschlossen: Head fa74265781803fd41a8310d41b5e7f38f8cbfe59
gegen Basis 6a8c6ca3835f1f88ae63d6588685f19a675dcb7c, alle 13 Head-Checks SUCCESS;
Squash 7acf4c27868285ad08872f3e954c19347f0f7c6d, vollständiger Tree
b0f0144b8fd8e98dd90cd0d2ed9a0e4ea43e9f9d exakt identisch. Alle sieben Main-
Workflows SUCCESS: 38184152108/38184152119/38184152145/38184152159/38184152171/
38184152093/38184152149. main/origin/main per FF sauber synchronisiert;
eigener Rollenbranch lokal/remote entfernt, keine eigenen Container verblieben.

Unmittelbar folgt der [begrenzte eigene Containerabbruch](SQL_SERVER_2025_AI_IDX012_HARD_ABORT_REVIEW.md)
auf codex/sql2025-ai-idx012-hard-abort, Basis 7acf4c27868285ad08872f3e954c19347f0f7c6d.
Nur idle Container-SIGKILL nach qualifiziertem fertiggestelltem Index-/Source-/
Snapshotcheckpoint und beendetem Client; gleicher vollständig gebundener CID
und tatsächlicher neuer Wiederanlauf, danach neue read-only Snapshot-/Source-
Kontrollen und unveränderte Originalrestores/markergebundener Cleanup.
Sechs Kandidaten/zwölf serielle eigene Container, zwei stabile Lifecycles,
gesamter Cleanup 60 s bereits vor Kill ohne Reset; öffentlicher SQL-Recovery-
Vertrag 20 s bleibt erhalten. Keine aktive DDL-/vollständige Hard-Abortabnahme.
Noch keine Admission; enge Quellenclosure für Signal-/Restart-/Deadline-/
ClientEndUnknown-Grenze vor Runtime erforderlich. Workstream/Heartbeat aktiv.

Vor Admission enge unabhängige Quellenclosure erteilt ohne weitere P1/P2.
Collector-/Pollausnahmen mit unbestätigtem Ende verwenden ClientEndUnknown;
Review-P2 vor Runtime geschlossen, neun betroffene rein synthetische
Gegenproben PASS (fünf Restart-, vier tatsächliche ClientEnd-/Recoveryfälle).
Parent 2A7DF31DB4C573248B3B51C5E5D56762FDD0A13E1CAB56F49D1C86BED4503454,
Restarthelper 27858DFD1D2050E3E4A1DD8E4D27765E29B9C84EE7DF7316E69734C144C52D9B;
öffentlicher Controller DFBC unverändert. Kein SQL/Container durch Reviewer.


IDX-012 eigener idle Container-SIGKILL tatsächlich zweimal auf stabilen C1-
Quellen bestanden: F92CEAC8A7614EAB/3EF8E51FAD3B4BE8. Vor Kill jeweils
qualifizierter Index-/vollständiger 999-Row-Source-/Snapshotcheckpoint und
bestätigt beendeter Arbeitsclient. Tatsächlicher Exit 137 ohne OOM, neuer
Start desselben gebundenen CID/neue Readiness, neue vollständig identische
Snapshot-/Source-/Indexrecords samt Originalbaseline 0/0 und aktuellem 1/1.
Öffentlich je kontrolliertes FAIL_EXECUTION; tatsächliche Originalrestores/
Attestation 0/0, neuer DB-Abwesenheitsclient und eigene volle CID-/
Namensabwesenheit bestanden. Gesamtes Cleanup ab vor Kill einschließlich
Restart/read-only/SQL-Restore/Containerabbau 19.4342235/19.3921410 s,
keine Deadline zurückgesetzt; beide eigenen Container entfernt.
[Begrenzter Teilnachweis](SQL_SERVER_2025_AI_IDX012_HARD_ABORT_REVIEW.md#tatsächliche-zwei-stabile-containerabbruch-lifecycles).
Aktive Build-/DML-/Rebuild-Unterbrechung und vollständige Hard-Abort-/Runtime-/
TP-PERF-Abnahme bleiben offen. Nächster Schritt: aktuelle Head-/Main-Gates,
PR-Integration/Tree-/FF-Sync-/eigener Branchcleanup, danach nächster
zulässiger lokaler Schnitt. Workstream und Heartbeat aktiv.


## CON-010-Wiederaufnahme nach Erweiterung der Testzyklen

Unmittelbar nach vollständigem PR-182-Abschluss folgt der begrenzte private
TSK-009-/CUR-018-Schnitt CON-010 auf codex/sql2025-ai-con010-resume,
Basis 9a9c0e957a1444d79f936c8cc1bcb9b83839435a. PR 182 hatte 13 aktuelle
Head- und sieben Main-Gates erfolgreich; vollständiger Tree
35ef8a41a67180fc8cc1543c5585910cab4201de, lokales main synchronisiert,
eigener lokaler/Remote-Branch entfernt. Idle-SIGKILL bleibt Teilnachweis;
Abbruch während aktiver DDL aus TSK-006 weiterhin offen.

Benutzerfreigabe erweitert auf sechs kohärente Test-/Korrekturkandidaten.
Drei historische vollständige CON-010-FAILs und zwei Metadatenproben werden
weitergezählt. C4 korrigierte die vollständige Rechtefixture, scheiterte
jedoch nativ in Setup mit Kollationsfehler 468; actual Cleanup/DB/CID/Name
PASS. C5 korrigiert ausschließlich Statebytes und bestand zwei vollständige
Lifecycles mit je zwei Setups und sechs Resultassertions. Alle sechs
CONNECT-/SELECT-Grants einschließlich Klassen, Ziel, Grantor, Zustand und
vollständigen Bytes sind exakt gebunden; RLS/Funktions-/Quellen-/Vektoren-
oracles sowie drei tatsächliche Rechteverweigerungen und Reset bestanden.
Cleanup und unabhängige DB-/CID-/Namensabwesenheit unter derselben 60-s-
Deadline PASS. Quellen-/Test-/Review-/Verbrauchsgrenzen im
[begrenzten Wiederaufnahmenachweis](SQL_SERVER_2025_AI_TENANT_RESUME_REVIEW.md).

Die alte Abbruchgrenze wird ausschließlich durch die neue menschliche
Wellenautorität übersteuert; kein stilles Zurücksetzen, kein C6 nach grünen
Pflichtwiederholungen. Enger unabhängiger Quellenreview, konkreter P2 vor
Admission geschlossen, C5-Statebyte-Delta geschlossen. Sechs rein synthetische
Endstatus-/Recoverytests PASS, kein wiederholter grüner Altcheck.
CON-010 bleibt PROPOSED. Nächster zulässiger Schnitt nach diesem PR-/Main-/
Sync-/Cleanupabschluss: öffentliche Demoeinbindung mit vollständigen
Marker-/Fixturegegenproben und 2019-/2022-Versionsgrenzen; Pooling/echte
Logins/ANN bleiben getrennt. Provider-/Cloud-/ONNX-/rote Hostgrenzen bleiben.


## CON-010: öffentliche Demo und tatsächliche Gegenproben

Nach vollständigem PR-183-Abschluss unmittelbar nächster TSK-009-Schnitt auf
codex/sql2025-ai-con010-public, Basis d43a1c0303ad18e26cecc63a9c944f5b7ca8bf16.
PR 183: sieben aktuelle Head-/fünf Main-Gates erfolgreich, vollständiger Tree
f6f1480bd96ab29adbdb754b45cbb2e31b1d682b, lokales main FF-synchronisiert,
eigener lokaler/Remote-Branch entfernt. Historische CON-010-FAILs unverändert.

Neuer öffentlicher Consumer mit sechs Kandidaten/maximal 30 seriellen eigenen
Containern. C1: vier Versions-SKIPs und 192 Markerabweisungen bestanden; FAIL
an wirkungslosem zusätzlichem Spalten-SELECT unter Tabellen-SELECT. Tatsächlicher
Cleanup/neue DB-/vollständige CID-/Namensabwesenheit bestanden. C2 änderte nur
Spalten-DENY und verlangt vollständige Snapshotänderung vor jeder Mutation.
Alle 16 tatsächlichen Source-/Policy-/Rechte-/Rollenmanipulationen mit exakt
51003/FAIL_RESULT_CONTRACT gegen Baseline und Comparison abgewiesen; alle
192 Markerproben mit exakt 51004/FAIL_STATE über acht Phasen abgewiesen,
vollständige Snapshots unverändert und tatsächliche markergebundene Reparatur.
Setup zweimal semantisch gleich; je zweimal echte 2019-/2022-SKIPs vor Setup.
Alle zehn eigenen Container vollständig geschlossen, DB/CID/Name neu abwesend;
Cleanup jeweils unter gemeinsamer 60-s-Deadline. Keine rohe Diagnose veröffentlicht.

CON-010 jetzt IMPLEMENTED unter vorhandener Registryidentität; neunte lokale
KI-Demo. 32 Demos/372 Runs bleiben geplanter Providerkatalog, keine Vollausführung.
Neue Consumerabhängigkeit in beiden Workflowpathsets, mutierende CI unverändert
cancel-in-progress=false. Ein Owner/enger Risiko- und Deltaquellenreview; zwei
P2 vor Admission geschlossen, wirkungslose native Probe wahrheitsgemäß FAIL.
Sechs synthetische Endstatus-/neun öffentliche Runnermethoden und betroffene
Framework-/Guide-/Katalog-/Selektorgates PASS. Modell-/Tokenverbrauch unbekannt.

[Gebundener öffentlicher Nachweis](SQL_SERVER_2025_AI_TENANT_IMPLEMENTATION_REVIEW.md).
Aktuelle Head-/Main-Gates, PR-Merge, vollständige Treeübernahme/FF-Sync und eigener
Branchcleanup sind vor Schnittabschluss erforderlich. Pooling, authentifizierte
Serverlogins, mehrere Sessions, ANN/Postfilter, Seitenkanäle und TSK-009-Gesamtabnahme
bleiben offen. Nächster unabhängiger lokaler Schnitt nach vollständiger Integration:
RES-008-Quellen-/Dimensions-/Storagevorbereitung aus TSK-010, mit begrenztem
synthetischem float32-Profil; keine Cloud-/ONNX-/rote Hostwirkung oder Wiederaufnahme
anderer Workstreams. Heartbeat bleibt Wiederaufnahmeabsicherung des aktiven Auftrags.


### CON-010 C3: korrigierter öffentlicher Ausgabekanal

PR 184 ist noch offen. Head 4c28f5d2f0c10efd1cc1af80bc1ea4a35a677a7c:
SQL-AI-CI 38188982540 FAIL nach zwei positiven regulären CON-010-Lifecycles,
vor Setup des Gegenprobenconsumers; PRINT war durch -r 1 nach stderr geroutet,
API lieferte stdout. Eigener CI-Container bereinigt, kein Merge dieses Heads.
Andere zwölf ausgewählte Head-Workflows abgeschlossen erfolgreich.
C3 korrigiert optionalen API-Diagnostikkanal/gezielte Consumer-Summaries und
strukturierten ValueError-FAIL. Alle fünf festen C3-Slots unter tatsächlichen
öffentlichen Ausgabeoptionen bestanden: 192 Marker-/32 Resultabweisungen,
16 tatsächliche Mutationen, Setupidempotenz und je zwei 2019-/2022-SKIPs.
Alle 15 eigenen Container samt DB/CID/Name neu abwesend, Endstatus bekannt;
alle historischen FAILs bleiben im gemeinsamen sechs-Kandidaten-Ledger.
Enger C3-Deltaquellenreview vor Admission geschlossen, sieben synthetische
Endstatus-/elf öffentliche Runnermethoden PASS. Keine geänderten SQLoracles.
Aktuelle korrigierte Head-/Main-Gates, Integration/FF-Sync/eigener Branchcleanup
folgen vollständig; nächster unabhängiger Schnitt weiterhin RES-008. Keine
TSK-009-/Provider-/Pooling-/Gesamtabnahme, Modell-/Tokenverbrauch unbekannt.


### CON-010 C4: gemeinsame API wiederhergestellt

C3 lokal PASS, anschließend Head c720508 im Offline-CI 38190655438
FAIL/PYTHON_PROFILE_CHANGED an eingefrorener gemeinsamer API-Abhängigkeit;
kein Merge. C4 stellt gemeinsame API exakt auf Baseline zurück und projiziert
ausschließlich die feste positive CON-010-Consumersummary per SELECT auf stdout.
Keine Migration pausierter Workstreams/Profiles; reguläre Demo-SQLbytes und
SQL-/RLS-/Grant-/Fehleroracles unverändert. Alle fünf C4-Slots bestanden:
192 Marker-/32 Resultabweisungen, 16 tatsächliche Mutationen, Setupidempotenz,
je zwei 2019-/2022-SKIPs vor Setup. Alle 20 eigenen Container samt DB/CID/Name
neu abwesend, Endstatus bekannt, Cleanup unter derselben 60-s-Deadline.
Alle historischen nativen-/CI-FAILs im selben sechs-Kandidaten-Ledger erhalten,
keine weitere unveränderte grüne Wiederholung. Enger C4-Review geschlossen,
elf öffentliche Runner-/sieben private Endstatustests PASS. Aktuelle C4-
Head-/Main-Gates/Integration/FF-Sync/eigener Branchcleanup erforderlich; danach
unmittelbar RES-008-Vorschnitt. Kein TSK-009-/Pooling-/Provider-Gesamtabschluss.


## RES-008: private Dimensions- und Storagevorbereitung

PR 184 vollständig abgeschlossen: Head 7f37469c0b83ae36618cd26b5b12133930b8c78b
mit 49 erfolgreichen Checks/13 ausgewählten Workflows, Squash
84aef7016cc86194281805adc29ae9bc15fcec2f mit elf erfolgreichen Main-Workflows.
Vollständiger Tree 1418d4f9f9786dba176759d499ed53a19db11423 gleich übernommen;
lokales main FF-synchronisiert, sauber, eigener lokaler/Remote-Branch entfernt.
Die vorstehenden C2-/C3-CI-FAILs bleiben historische Befunde ihrer Heads.

Unmittelbar folgte codex/sql2025-ai-res008-preparation auf dieser Main-Basis.
TSK-010/CUR-020, RES-008 weiterhin PROPOSED. Sechs Kandidaten/maximal zwölf
eigene serielle Container; ein Owner, enger unabhängiger Quellenreview und
C2-Deltaclosure vor Admission. C1 nach Setup FAIL/8124 an äußerer Referenz in
Komponentenaggregat, tatsächlicher SQL-/DB-/Containercleanup bestanden.
C2 änderte nur vier Oracleprüfstellen; zwei vollständige Lifecycles bestanden.
Je drei vollständige Aufnahmen aller 400 Rows in vier float32-Dimensionen,
Storage/Metadaten/vier Suchkontrollen, Setupidempotenz, tatsächliche DELETE-
Quellengegenprobe mit exakt 51003 und vollständiger Restore bestanden.
DB-Optionen 0/0 erhalten; Cleanup aller drei DBs/Container unabhängig belegt,
bekanntes natives Ende und dieselbe 60-s-Deadline ohne Reset. Private Ledger,
Sourcebytes und Rohlogs bleiben ignoriert; keine weitere grüne Wiederholung.

[Gebundener Teilnachweis](SQL_SERVER_2025_AI_RESOURCE_DIMENSION_REVIEW.md).
Aktuelle Head-/Main-Gates, PR-Merge, vollständige Treeübernahme, FF-Sync und
eigener Branchcleanup folgen vor Abschluss. CPU/Elapsed/Memory/Plans, AB/BA/AA,
Loader/Modellqualität, ältere Engines und öffentliche Demo-/TP-PERF-Abnahme
bleiben offen. Nächster zulässiger lokaler Schritt nach vollständiger Integration:
RES-008-Messmethodenerweiterung. Kein Workstream-Gesamtabschluss; Heartbeat aktiv,
Cloud-/ONNX-/rote Hostgrenzen unverändert, Modell-/Tokenverbrauch unbekannt.


## RES-008: begrenzte private Messfenster

PR185 vollständig abgeschlossen: Head 4f29e564d2602fa38cafcf0ae5a89775425ec07b
mit sieben Head-Workflows, Squash a3bfb66fb032c292b604fa939d27a211ded19ecb
mit fünf Main-Workflows PASS. Vollständiger Tree f7ce3e181fdfdba2c916e828061bdda2db76a8cd
gleich übernommen; lokales main FF-synchronisiert und sauber, eigener lokaler/Remote-Branch entfernt.
Unmittelbar codex/sql2025-ai-res008-measurement gestartet, TSK-010/CUR-020.

Neue konkrete Messfrage mit sechs Kandidaten/maximal zwölf eigenen seriellen
Containern; C1 FAIL am groben DMV-/feinen Fensterzeitvergleich erhalten,
tatsächlicher eigener SQL-/DB-/CID-/Namenscleanup PASS. C2 ändert nur diesen
unbegründeten Cross-Type-Vergleich, rohe Requestidentity und tatsächliche
Counter-/UTCdeltas/Nichtüberlappung voll erhalten. Zwei vollständige stabile
Lifecycles mit je 20 Warmups, 54 AB-/BA-/AA-Fenstern und 5420 einzelnen Queryoracles
bestanden; alle Fenster gegen unabhängig attestierte eigene DB-ID und volle
native Chunkframes gebunden. Tatsächliche SourceDELETE-/Querymutationsnegative
mit exakt 51003, acht vollständige 400-Row-/Config-Aufnahmen und Restore gleich.
Eigener Cleanup aller drei Container/DBs unter unveränderter 60-Sekunden-Deadline.

[Gebundener Teilnachweis](SQL_SERVER_2025_AI_RESOURCE_MEASUREMENT_REVIEW.md).
Ein Owner, enger Source- und C2-Delta-Review geschlossen, 18 betroffene synthetische
Cases PASS. Keine weitere grüne Wiederholung; Runtime-/Sourcebytes privat ignoriert.
Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. Danach unmittelbar begrenzte Plan-/Memoryaufnahme für RES-008.
RES-008 PROPOSED, TSK-010/TP-PERF/Worker-/Provider-/Gesamtabnahme offen. Kein
Cloud-/ONNX-/roter Hosteffekt, Modell-/Tokenverbrauch unbekannt, Heartbeat aktiv.

## RES-008: repräsentative tatsächliche Pläne

PR186 vollständig abgeschlossen: Head 78f9747209ca0aea52508bcb6a584ff431816841
mit sieben aktuellen Head-Workflows, Squash e8fb5d801464e5e2acb37fdeef5f7d203c048cb3
mit fünf aktuellen Main-Workflows PASS. Vollständiger Tree
e0ab4de7a0cca55a92bdc91909dfebdc469cc47f gleich übernommen, lokales main
FF-synchronisiert und sauber, eigener lokaler/Remote-Branch entfernt.
Unmittelbar codex/sql2025-ai-res008-plans gestartet, TSK-010/CUR-020.

Neue konkrete Planfrage mit sechs Kandidaten/maximal zwölf eigenen seriellen
Containern. C1 FAIL am fehlenden tatsächlichen Ergebnisrootzähler erhalten;
eigener SQL-/DB-/CID-/Namenscleanup bestanden. C2 ändert nur direkte Id-/Distanz-
projektion und deren exakte Statement-/Rowauswertung; Root-/Scan-/Threadguards
erhalten. Enge unabhängige P2-Closure und 24 synthetische Gegenfälle bestanden.
Zwei vollständige stabile Lifecycles mit je vier tatsächlichen Exact-Plänen,
eigener Scan mit 100 Rows, Ergebnisroot mit einer Row und Id 1/Distanz 0,
acht Raw-/Recordbindungen und elf vollständige 400-Row-Aufnahmen über alle drei
Lifecycles bestanden. Tatsächliche DELETE-Gegenprobe mit 51003 und Restore, idempotentes zweites
Setup, volle Source-/Configgleichheit und unabhängiger eigener Cleanup.

[Gebundener Teilnachweis](SQL_SERVER_2025_AI_RESOURCE_PLAN_REVIEW.md).
Tatsächliche Memoryattribute veröffentlicht; Compute-Scalar-RuntimeRows und
Waits/Warnings NOT_CAPTURED, Roh-DOP 0 ohne Umdeutung. Keine Aussage über alle
früheren Messfenster oder fehlende Spills/Waits; Zeit-WARNs bleiben sichtbar.
Keine weitere grüne Wiederholung; Runtime-/Sourcebytes privat ignoriert.
Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Cleanup
folgen vor Abschluss. Danach unmittelbar öffentliche RES-008-Demoqualifikation
unter getrennten Performancegrenzen. RES-008 PROPOSED, TSK-010/TP-PERF/
Worker-/Provider-/Gesamtabnahme offen. Kein Cloud-/ONNX-/roter Hosteffekt,
Modell-/Tokenverbrauch unbekannt; Heartbeat aktiv.

## RES-008: öffentlicher begrenzter Consumer

PR187 vollständig abgeschlossen: Head 334f91f743081c7c73ff1d823715e011227dec6c
mit sieben aktuellen Head-Workflows, Squash 1891b35d81dcdc61274a4a738994c3b25aa09dd4
mit fünf aktuellen Main-Workflows PASS. Ganzer Tree d516ca9e6fc919c5c05bc8bf4a83fe32e5871b04
gleich übernommen, lokales main per FF sauber, eigener lokaler/Remote-Branch entfernt.
Unmittelbar codex/sql2025-ai-res008-public gestartet, TSK-010/CUR-020.

Öffentlicher Controller mit sechs Kandidaten/maximal 42 eigenen seriellen
Containern für sieben feste Slots. C1 alle sieben lokal bestanden: vier tatsächliche
2019-/2022-SKIPs vor Setup, zwei vollständige SQL-17.0.5005.3-Profile mit je
20 Warmups, 54 AB-/BA-/AA-Fenstern, 5420 einzelnen Queryoracles und vier Actual-
Plänen; tatsächlicher eindeutig attestierter Fault nach PASS-Setup mit Recovery.
Zehn vollständige 400-Row-Aufnahmen gleich, Source-/Querynegative exakt 51003,
Restore, Setupidempotenz, DB-Konfiguration 0/0 und unabhängiger eigener Cleanup.
148 native Fenster und acht native Pläne exakt gegen vollständige Records gebunden.

[Öffentlicher Teilnachweis](SQL_SERVER_2025_AI_RESOURCE_PUBLIC_REVIEW.md).
15 Controller-/24 Plan-/18 Messgegenfälle und enger unabhängiger Abschluss
dreier konkreter P2 vor Admission bestanden. Private Launcherimportkollision
vor Admission korrigiert, kein damaliger Container-/SQL-Effekt; historische
Source-/Mess-/Plan-FAILs bleiben erhalten. Keine unveränderte grüne Wiederholung.
Öffentliche gemeinsame API unverändert; neue CI prüft den öffentlichen
Consumer-/Shim-/Prozesspfad, Pflicht-SKIPs und WARNs sowie eigenen Cleanup.

CI-C1 (Head ba65cf386e028cb2e8e2b5efcc91142b146d1726, Run 38199574328)
FAIL am bisherigen Containerproxy: zusätzliche RES-008-Optionen nicht akzeptiert,
2019/2022 mit unabhängiger Containerentfernung, öffentliche SQL-Abwesenheit
dabei nicht qualifiziert. CI-C2 ändert nur den eigenen Adapter und dessen Auswahl
im neuen Runner; gemeinsame API/Proxy und SQL-/Controllerbytes unverändert.
Drei neue Argument-/ENV-/stdin-/Exitcodegegenfälle bestanden. Beide CI-Kandidaten
werden im erweiterten Sechskandidatenbudget erhalten; aktueller CI-Nachweis folgt.

Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. Danach unmittelbar begrenzte öffentliche Aggregation/
Ergebnisinterpretation aus den bereits vollständigen Records ohne erneute
unveränderte SQL-Läufe. RES-008 PROPOSED, neun lokale Demopakete IMPLEMENTED;
vollständige FWK-011-/Demo-/TP-PERF-/TSK-010-/Modul-/Workstreamabnahme offen.
Keine Cloud-/Modell-/ONNX-/rote Hostwirkung, kein anderes Repository verändert;
Modell-/Tokenverbrauch unbekannt, Heartbeat aktiv.


## RES-008: begrenzte öffentliche Aggregation

PR188 vollständig abgeschlossen: Head b2c55911994db6460a15e27e2b5b3ca32390ac0b,
zwölf aktuelle Head-Workflows; Squash 192fcd945d1408bf6509263600af7beb2bb83c4d,
zehn aktuelle Main-Workflows PASS. Ganzer Tree 151bd6af448e7b6153b23c5a7b69f63d9f7353d6
gleich übernommen, main FF-synchronisiert/sauber und eigener lokaler/Remote-Branch
entfernt. CI-C1 auf allen drei Versionen FAIL am Proxy erhalten, Containercleanup
bestanden; eigener CI-C2-Adapter mit aktuellem Public-PASS/SKIP/WARN/Recoverypfad.
Unmittelbar codex/sql2025-ai-res008-aggregation begonnen, TSK-010/CUR-020.

[Gebundene Aggregation](SQL_SERVER_2025_AI_RESOURCE_AGGREGATION_REVIEW.md):
exakte 20-Warmup-/54-Fensterpopulation, sechs A/B-Batchfenster je Pfad/Paar, AA
separat; nullbedingtes N/A, Nullzählungen und Ausreißer sichtbar. 148 vorhandene
Raw-Windowframes und acht Raw-Pläne exakt gebunden, zwei begrenzte Auswertungen
mit je 30 numerischen FWK-011-Invarianten bestanden, keine neuen lokalen SQL-Läufe.
25 reine Populations-/Counter-/Oracle-/Plan-/Privacy-/FWK-Gegenfälle und drei
öffentliche CLI-Fälle bestanden. Konkreter unabhängiger Assertionbinding-P2
geschlossen; keine Reviewer-Tests/-Runtime oder Reviewkette. Gesamt-WARN,
PROPOSED und offene volle Worker-/TP-PERF-/TSK-010-/Modulabnahme erhalten.

CLI --summary optional nach positivem bekanntem Controllerabschluss, keine
Rawdiagnosepersistierung; CI bewertet die neue Aggregation am öffentlichen
nativen Consumer und erhält vollständigen eigenen Cleanup. Aktuelle Head-/Main-
Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup folgen vor
Abschluss. Danach begrenzte Teilnehmer-/Traineraufgabe zu diesem Teilprofil
unter TSK-012 ohne SQL-Retry/volle didaktische Abnahme. Keine Cloud-/Modell-/ONNX-/
roten Hosteffekte oder andere Repositoryänderung; Verbrauch unbekannt,
Heartbeat aktiv; sechs kohärente Kandidaten je lokalem Schnitt bleiben autorisiert.


## RES-008: begrenztes Teilnehmer- und Trainermaterial

[PR189](https://github.com/gecompat/SQL_PerformanceSchulung/pull/189) vollständig
abgeschlossen: Head 88a9d60f640fc9984c61cdb7a9be0703ba6b1d37, neun aktuelle Head-Workflows PASS;
Squash eab09f6e8de580e9087f214e07bdaf62283a9690, sieben aktuelle Main-Workflows PASS.
Ganzer Tree 2418eb0933d76903d98644f7ffef392aa67d68bb exakt übernommen, main FF-synchronisiert/sauber;
eigener lokaler/Remote-Branch entfernt. Öffentliche 2025-Aggregation in Head/Main
je zweimal mit 30 numerischen FWK-PASSs bei Gesamt-WARN, tatsächlicher Setupfault-
Recovery und eigenem Cleanup; Versions-SKIPs vor Setup erhalten. Abschließende
Dokumentpräzisierung trennt UTC-Schleifenzeit von umgebenden Request-Countergrenzen.
Unmittelbar codex/sql2025-ai-res008-teaching begonnen, TSK-012/CUR-020.

Das bestehende [Arbeitsheft](../HowTo/SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md#ergänzende-ergebnisleseaufgabe-res-008)
und der [Trainerleitfaden](../HowTo/SQL_SERVER_2025_AI_OFFLINE_TRAINER_GUIDE.md#getrennte-ergänzung-res-008-ergebnisse-lesen)
enthalten eine getrennte Ergebnisleseaufgabe aus den bereits gebundenen Beobachtungen:
20 Warmups, 54 Messfenster, 74 Requests, 5420 Querykontrollen; sechs A/B-Fenster
je Pfad/Paar, AA separat. Batch-/Counter-/UTC-Grenzen, N/A/Nullwerte/Ausreißer,
beschränkte FWK-Invarianten und fehlende Modellqualität sind Aufgaben und Lösung.
Die einzige Lösung/Rubrik bleibt im Arbeitsheft; acht Basisübungen maximal 16 Punkte,
getrennte optionale Ergänzung 0–2 Punkte. Keine neuen SQL-Läufe oder didaktischen
Istwerte; tatsächliche Teilnehmererprobung, Lehrzeiten, Masterdeck/Notes/Render und
Generalprobe offen. Historische FAILs und aktuelle ANN-Teilqualifikation unterschieden.

Quellen-, Link-, Sprach-, Privacy- und Diffprüfung für diese Dokumentänderung;
aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. RES-008 PROPOSED/Gesamt-WARN und volle TP-PERF-/Modulabnahme
bleiben offen. Danach unmittelbar nächste unabhängige kanonische Teilaufgabe;
allgemeine Entwicklung/DGN-007 bleiben pausiert. Keine Cloud-/Modell-/ONNX-/roten
Hosteffekte, kein anderes Repository verändert. Sechs kohärente Kandidaten je
lokalem Schnitt autorisiert; Modell-/Tokenverbrauch unbekannt, Heartbeat aktiv.


## DGN-010: begrenzte private Actual-Planqualifikation

PR190 vollständig abgeschlossen: acht aktuelle Head-/sechs Main-Workflows PASS;
Head 71aa155ad6e86fdd4490534e22969ddaf92f2089, Squash e7c407fe957245bcc83052ce266748fc19b1aa62,
ganzer Tree 95c407b5d74cf93fd7db942731385732dcc9b738 exakt übernommen;
main FF/sauber und eigener lokaler/Remote-Branch entfernt. Unmittelbar TSK-011/
CUR-021 im Branch codex/sql2025-ai-dgn010-plans fortgesetzt.

[Gebundener DGN-010-Ownerplannachweis](SQL_SERVER_2025_AI_INDEX_PLAN_REVIEW.md):
C1 zweimal auf eigener fester 2025-Instanz bestanden, je acht vollständige 1000-Row-
Sourceaufnahmen, tatsächliche DELETE-51003-Gegenprobe/Restore, feste Readerrechte
und eigene Indexbuild-/Dropfolge. Sechs native Actual-Pläne/16000 Source-Rows exakt
gegen private Records gebunden. Je drei vollständige zehn-Row-Ownerqueryresultate;
Clustered Index Seek → eigener Candidate-Index Seek → Clustered Index Seek.
17 zusätzliche used pages, keine Performancewiderlegung. Roher DOP0/erfasste echte
Memorynullen getrennt von fehlenden Attributen, Waits/Warnings NOT_CAPTURED.

Zwei konkrete P2 vor Admission geschlossen, fünf reine Methoden mit elf/neun/neun
Gegenfällen bestanden; anfängliche reine Testtreiberfehler erhalten. Kein Reviewer-
Test-/Runtime oder Reviewkette. Je 21 dokumentierte native Phasencalls und Marker-
Cleanup mit unabhängiger DB-/Namens-/CID-Abwesenheit innerhalb 60 Sekunden bestanden.
Ownerpläne qualifizieren keine Readerpläne/Minimalrollen; Reads/CPU/Elapsed, DMLkosten,
AB/BA/AA/Effektseparation, ältere Engines, öffentliches Paket und volle TP-PERF-/
TSK-011-/Modulabnahme offen. DGN-010 PROPOSED.

Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. Danach nächste begrenzte kanonische DGN-010-Messaufgabe;
keine unveränderte Wiederholung dieser grünen Pläne. Allgemeine Entwicklung/DGN-007
pausiert; keine Cloud-/Modell-/ONNX-/roten Hosteffekte oder andere Repositoryänderung.
Sechs kohärente Kandidaten je lokalem Schnitt autorisiert, Verbrauch unbekannt,
Heartbeat aktiv.


## DGN-010: begrenzte private Reader-Zugriffspfadmessung

PR191 vollständig abgeschlossen: Head 4065d6a36dd45e04b261c0164ba153badd975de3, sieben Head-Workflows PASS;
Squash 27ef0a118fb25a8ad00353ebd347fb1ad258db4c, fünf Main-Workflows PASS; ganzer Tree ab91c69b0de0d9f8c94fcccf0822518dd14a745d exakt übernommen,
main FF/sauber und eigener lokaler/Remote-Branch entfernt. Unmittelbar TSK-011/
CUR-021 im Branch codex/sql2025-ai-dgn010-measurement fortgesetzt.

[Gebundene feste Readerbatchmessung](SQL_SERVER_2025_AI_INDEX_MEASUREMENT_REVIEW.md):
C1 Counter-FAIL erhalten, C2 mit zwei vollständigen Lifecycles bestanden. Je zehn
Warmups/18 serielle AB-/BA-/AA-Fenster, 1810 vollständige Queryoracles, zusätzliche
positive/negative Kontrolle; beide eigenen Indizes während aller Messphasen vorhanden.
AB/BA sechs Samples je erzwungenem PK-/Candidatepfad, drei AA-Paare separat.
CPU/I/O eigene Requestdeltas einschließlich Grenzen, UTC-Elapsed enthält
Impersonation/Query-/Buffer-/Transfer-/Delete-/REVERT-Aufwand; keine identischen
Messgrenzen, individuelle Querylatenz oder Nettonutzenbehauptung.

22000 Source-Rows, vier neue tatsächliche Ownerpläne, 58 positive Fensterframes
inklusive zwei separater Kontrollen und vier native Negative vollständig gebunden.
Quelle/Config/Readerrechte unverändert; SourceDELETE/Restore/Setupidempotenz,
Indexbuild/Drop und markergebundener SQL-/DB-/CID-/Namenscleanup bestanden.
Enger unabhängiger P2-/Sourceabschluss, acht reine Methoden PASS; ursprünglicher
reiner Fixturefehler erhalten. Reviewer ohne Tests/Runtime, keine Reviewkette.
Sechs kohärente Kandidaten je Schnitt autorisiert, bisherige FAILs erhalten.

Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. Danach nächste begrenzte DGN-010-DML-/Effektseparationsfrage.
Isolierte Index-/Query-/vollständige Worker-/DMLkosten, ältere Engines, öffentliches
Paket und vollständige TP-PERF-/TSK-011-/Modulabnahme offen; DGN-010 PROPOSED.
Allgemeine Entwicklung/DGN-007 pausiert; keine Cloud-/Modell-/ONNX-/roten
Hosteffekte oder andere Repositoryänderung. Verbrauch unbekannt, Heartbeat aktiv.


## DGN-010: begrenzte private DML-Effektseparation

PR192 vollständig abgeschlossen: Head 003bad4017233091f560752e93d2420b00c2f764, sieben Head-Workflows PASS;
Squash 2bef37419d9399cb5fc49658592de351b16815e5, fünf Main-Workflows PASS; ganzer Tree a6dc9110a041c9c8be37c64aa9f41959e5efec81 exakt übernommen,
main FF/sauber und eigener lokaler/Remote-Branch entfernt. Unmittelbar TSK-011/
CUR-021 im Branch codex/sql2025-ai-dgn010-dml fortgesetzt.

[Gebundene Owner-DML-Batchmessung](SQL_SERVER_2025_AI_INDEX_DML_REVIEW.md):
C1 zweimal mit je zehn Warmups/18 seriellen AB-/BA-/AA-Fenstern und 1810 tatsächlichen
UPDATEs/18100 vollständigen OUTPUT-Rowkontrollen bestanden. A ohne/B mit Candidateindex;
vier Build-/Dropzyklen je Profil außerhalb Messfenster, 46 vollständige Source-/
Config-/Reader-/Indexaufnahmen. Value=Id×3+Ordinal während eigener Transaktion,
tatsächlicher Rollback und voller unveränderter Source-Nachbestand; Source-/OUTPUT-
51003-Gegenproben/Restore/Idempotenz und vollständiger eigener Cleanup bestanden.

92000 Source-Rows/58 positive Fensterframes/vier native Negative exakt gebunden.
Sechs AB/BA-Samples pro Indexzustand, drei AA-Paare separat. Requestdeltas und
UTC-Batchgrenzen einschließlich OUTPUT-/Transaktions-/Rollbackaufwand sichtbar;
keine isolierten Index-/Commit-/vollständigen Workerkosten. Enger unabhängiger
Quellenabschluss ohne offene P1/P2, acht reine Methoden PASS; Reviewer ohne
Tests/Runtime, keine Reviewkette oder Wiederholung früherer grüner Nativeruns.

Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. Danach begrenzter ungezwungener SELECTvergleich ohne/mit Index.
Nettonutzen, weitere Kosten, öffentliche FWK-/Versions-/Recoveryqualifikation und
vollständige TP-PERF-/TSK-011-/Modulabnahme offen; DGN-010 PROPOSED.
Sechs kohärente Kandidaten je Schnitt autorisiert, historische FAILs erhalten.
Allgemeine Entwicklung/DGN-007 pausiert; keine Cloud-/Modell-/ONNX-/roten
Hosteffekte oder andere Repositoryänderung. Verbrauch unbekannt, Heartbeat aktiv.


## DGN-010: begrenzter ungezwungener SELECTvergleich ohne/mit Index

PR193 vollständig abgeschlossen: Head 12b0716293a8607994b80804e0402768b18997f5, sieben Head-Workflows PASS;
Squash f1984f36a91c67161a0acf66f22e3d373089edc6, fünf Main-Workflows PASS; ganzer Tree fc9d81e3cb7c81063f65694fefb97bf3bc4300c5 exakt übernommen,
main FF/sauber und eigener lokaler/Remote-Branch entfernt. Unmittelbar TSK-011/
CUR-021 im Branch codex/sql2025-ai-dgn010-select fortgesetzt.

[Gebundener ungezwungener Readerbatchvergleich](SQL_SERVER_2025_AI_INDEX_SELECT_REVIEW.md):
C1 zweimal je zehn Warmups/18 AB-/BA-/AA-Fenster und 1810 vollständige Queryoracles
bestanden. A ohne/B mit Candidateindex, identische SELECT ohne INDEX-Hints, feste
Readerrechte; vier Build-/Dropzyklen je Profil außerhalb Messfenster. AB/BA sechs
Samples je Zustand, drei AA-Paare separat. UTC-/Requestgrenzen enthalten Buffer-/
Impersonationaufwand, keine individuelle Querylatenz/isolierte Indexkosten.

92000 vollständige Source-Rows/58 positive Fensterframes/vier native Negative
exakt gebunden; Source/config/Readerrechte gleich, Source-/Querynegative/Restore/
Idempotenz und eigener markergebundener SQL-/DB-/CID-/Namenscleanup bestanden.
Enger unabhängiger Quellenabschluss ohne offene P1/P2, grüne Readerparseranalyse
nach tatsächlichem LF-normalisiertem Vergleich wiederverwendet. Neue positive/
zwei fremde Scopepräfixfälle bestanden; anfängliche reine Fixture-/Bytevergleichs-
Fehler erhalten, keine Runtimewirkung. Keine alte grüne Suitewiederholung.

Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. Danach begrenzte Vorbereitung des öffentlichen DGN-010-Pakets.
Keine aktuellen Readerpläne/Indexnutzungs-/Nettonutzen-/vollständigen Workerkosten-
oder vollen TP-PERF-/TSK-011-/Modulclaims; ältere Engines/Recoveryqualifikation und
öffentlicher Consumer offen. DGN-010 PROPOSED. Sechs kohärente Kandidaten je Schnitt
autorisiert, historische FAILs erhalten; allgemeine Entwicklung/DGN-007 pausiert,
keine Provider-/roten Hosteffekte oder andere Repositoryänderung. Verbrauch
unbekannt, Heartbeat aktiv.


## DGN-010: öffentlicher reiner Benchmarkauswertungsvertrag

PR194 vollständig abgeschlossen: Head f30021a308bbd1bc6571ccd0d375330daabb839b, sieben aktuelle Head-
Workflows PASS; Squash abd392c63d7b89421df91f27626261f942ebe494, fünf Main-Workflows PASS; ganzer Tree
32d8d00dca6f1f7d49ed6b3967ac3cc745edea26 exakt übernommen, main FF/sauber und eigener lokaler/Remote-
Branch entfernt. Unmittelbar TSK-011/CUR-021 im Branch
codex/sql2025-ai-dgn010-contract fortgesetzt.

[Öffentlicher reiner Auswertungsvertrag](SQL_SERVER_2025_AI_DGN010_BENCHMARK_CONTRACT.md)
mit festen SELECT-/DML-Scopes, 46 vollständigen Quellenzuständen, 29 eindeutigen
positiven Fenstern inklusive separater Kontrolle, zehn Warmups/18 AB-/BA-/AA-
Messfenstern, 1810 Statementoracles und 18100 Rowkontrollen. Vollständige Source-/
Payload-/Request-/DB-/Counter-/UTC-/DML-Ordinal-/Rollbackdepthbindung; Warmups und
AA separat, alle Samples/Nullen/Ausreißer/exakte große Dezimalmediane erhalten.
Keine Identitäts-/UTC-/Source-/Plan-Rawausgabe. Zwei feste FWK-011-Verträge mit je
zwölf vollständig gebundenen Pflichtinvarianten; numerischer PASS ist kein Runtime-PASS.

20 reine Methoden bestanden, enger unabhängiger Quellenabschluss ohne offene
P1/P2; Reviewer ohne Tests/Runtime, keine Reviewkette. Vier bereits gebundene
Native-Records erneut rein geprüft: 48 FWK-PASSs und exakt gleiche Samples/Mediane,
null weitere SQL-/Containerläufe. Vorhandene Nativequellen/Recordhashes und
unabhängiger DB-ID-Frame gebunden. Keine neue Runtime-/Herkunfts-/Versionsattestation.

Statische KI-CI um neue Tests/Quellen erweitert, Runtimejob/Gemeinsam-API unverändert.
Aktuelle Head-/Main-Gates einschließlich tatsächlicher statischer Selection,
PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup folgen vor Abschluss.
Danach öffentlicher bounded DGN-010-Runtimeproducer mit getrennten SELECT-/DML-
Messscopes und Versions-/Marker-/Fehler-/Recoveryqualifikation. DGN-010 PROPOSED,
vollständige TP-PERF-/TSK-011-/Modulabnahme/Indexnettonutzen/weitere Kosten offen.
Sechs kohärente Kandidaten je lokalem Schnitt autorisiert, historische FAILs erhalten;
allgemeine Entwicklung/DGN-007/andere Automationen pausiert, keine Provider-/roten
Hosteffekte oder andere Repositoryänderung. Verbrauch unbekannt, Heartbeat aktiv.


## Öffentlicher DGN-010-Consumer: gebundener Kandidat2

[Teilnachweis](SQL_SERVER_2025_AI_DGN010_PUBLIC_REVIEW.md).

## Tatsächlicher begrenzter öffentlicher Nachweis

Kandidat2 vollständig geschlossen: acht tatsächliche Versions-SKIPs vor Setup
(je Scope zweimal 2019/2022), SELECT und DML jeweils zweimal vollständig SQL2025,
zwei kontrollierte Fehler nach PASS-Setup mit anschließender eigener Recovery.
14 neue eigene Container dieses Kandidaten, alle DB-/CID-/Namensabwesenheiten
unabhängig bestätigt, kein unbekannter Clientendstatus. Einschließlich C1 sind
23 Container geschlossen; der Editions-FAIL bleibt erhalten, vier Kandidaten
des gemeinsamen Sechserbudgets verbleiben, kein Budgetreset.

Vier vollständige öffentliche Profile an tatsächliche Nativeframes gebunden:
184000 Source-Rows in 184 Vollsnapshots, 116 positive Fensterframes einschließlich
vier separater Kontrollen, acht echte 51003-Negativframes, 32 Indexübergänge,
7240 vollständige Statementoracles/72400 Rowkontrollen und 48 numerische FWK-PASSs.
Jeder tatsächliche Versions-/Editionsframe ist 17/17.0.5005.3/3/-2117995310;
unabhängige DB-ID, komplette Rawhashes und ausgewählte Ausführungsquellen gebunden.
Source-/Querynegative/Restore/Idempotenz, Config-/Readerrechte, eigener Rollback
und markergebundener regulärer SQLcleanup bestanden. Zehn Warmups/18 Messfenster
je Profil; sechs AB-/BA-Samples je Zustand, drei AA-Paare separat. Alle Samples,
Nullen/Ausreißer/exakte Mediantexte erhalten. Kein Rawausgabeclaim aus CLI/Repository.

Öffentlicher Gesamtstatus WARN_OPTIONAL_EVIDENCE_SKIPPED; reine Recordvalidierung
und numerische FWK-Invarianten PASS, Runtime-/TP-PERF-Abnahme NOT_ESTABLISHED und
aktuelle Indexnutzung NOT_CAPTURED. Keine vollen Worker-/Indexnettonutzen-/Modulclaims.
Separate vollständige Marker-Manipulationsgegenproben, harte DML-/Buildunterbrechung,
Readerpläne, Insert-/Commit-/Buildkosten und vollständige TP-PERF-Abnahme offen.

Aktuelle Head-/Main-Gates mit tatsächlicher Consumer-Matrix, PR/Integration,
ganze Treeübernahme/FF-Synchronisierung/eigener lokaler und Remote-Branchcleanup
folgen vor Abschluss. Danach native Marker-Manipulationsqualifikation desselben
öffentlichen Pakets. Allgemeine Entwicklung/DGN-007/andere Automationen pausiert;
keine Provider-/roten Hosteffekte oder andere Repositoryänderung, Verbrauch unbekannt,
Heartbeat aktiv.


## DGN-010: PR196 geschlossen, begrenzte Markerqualifikation

Stand: 2026-10-12, TSK-011/CUR-021; DGN-010 bleibt PROPOSED.
Der [öffentliche Producer](SQL_SERVER_2025_AI_DGN010_PUBLIC_REVIEW.md) ist über
[PR 196](https://github.com/gecompat/SQL_PerformanceSchulung/pull/196) vollständig
integriert. Zehn Head- und acht Main-Workflows bestanden einschließlich tatsächlicher
Consumer-Matrix auf drei Engineversionen. Head 6d9ac26f69ac76f46ade8a094acb8225ce64e7b1,
Main 324c8ba21df182dddeb30c76e4947a793b84b022, ganzer Tree
224dce4178d6d28340657dbdab41c9aa9ffefb88 exakt übernommen; FF-Synchronisierung,
eigener lokaler und Remote-Branchcleanup abgeschlossen. Historischer C1-Editions-FAIL,
Gesamt-WARN und NOT_ESTABLISHED bleiben erhalten.


Vor Admission gilt der [kanonische Markerschnitt](SQL_SERVER_2025_AI_DGN010_MARKER_REVIEW.md): sechs Quellenkandidaten/maximal zwölf eigene lokale Container, zwei stabile vollständige Lifecycles, je 192 Nativeabweisungen/24 Restores und volle Source-/Metadatenvergleiche. Enger Review und neun reine Gegenfallmethoden abgeschlossen; noch kein nativer Marker-PASS. 300+60-Sekundenfloors, sticky UNKNOWN, CI-Aufwandgrenze und dreier Wave-Checkpoint im Teilvertrag. Danach tatsächliche Readerplan-/Indexnutzungsfrage. Workstream/Heartbeat aktiv; alle alten FAIL-/Provider-/TP-PERF-Grenzen bleiben sichtbar.

C1 der Markerqualifikation ist nach tatsächlichem PASS-Setup vor Markerprobe mit
FAIL geschlossen: die Auswertung wies den einzelnen normalen USE-Infoframe ab.
Eigenes SQLcleanup und neue DB-/CID-/Namensabwesenheit tatsächlich bestanden,
kein UNKNOWN; geschlossener Fehler bleibt im selben Sechserledger. C2 erlaubt
nur den exakten positiven Setupinfoframe, elf reine Methoden einschließlich
gemischter Fehlermeldungsabwehr PASS; enger Deltaabschluss und danach neue
native Admission gemäß [Teilnachweis](SQL_SERVER_2025_AI_DGN010_MARKER_REVIEW.md#tatsächlicher-c1-fail-und-gebundener-c2).

C2 der Markerqualifikation ist bei der ersten vollständigen Snapshotabfrage mit
Msg 8114 geschlossen FAIL: pauschale bigint-Konvertierung eines tatsächlichen
nvarchar-Konfigwerts. Source-/Readerprobe sowie eigener SQLcleanup und neue
DB-/CID-/Namensabwesenheiten bestanden; keine Markerprobe/kein UNKNOWN. C3 erhält
Typ und vollständige primäre/sekundäre Konfigbytes statt Zahlannahme, neuer reiner
Typ-/Byte-/NULLgegenfall PASS, alte grüne Fälle nicht wiederholt. Enger Deltaabschluss
und neue NativeAdmission, danach dreier Wave-Checkpoint gemäß
[Teilnachweis](SQL_SERVER_2025_AI_DGN010_MARKER_REVIEW.md#tatsächlicher-c2-fail-und-gebundener-c3).

Dreier Wave-Checkpoint: C3-FAIL nach tatsächlichem vollständigem Snapshot mit
1000 Rows/41 Configs, fehlender Key für die tatsächlich leere Rollenliste.
Alle drei Kandidaten einschließlich eigener DB/CID/Name vollständig geschlossen,
kein UNKNOWN; Fehlerhistorie bleibt erhalten. C4 erhält [] ausdrücklich und
transportiert vollständige Snapshotbytes als begrenzte UTF-16-Hexframes. 13 reine
Codec-/Controllerfälle bestanden wegen geändertem Codec, enger Capture-Deltaabschluss
vor neuer NativeAdmission. Drei weitere Quellenkandidaten bleiben autorisiert,
kein Reset; [Checkpoint](SQL_SERVER_2025_AI_DGN010_MARKER_REVIEW.md#dreier-wave-checkpoint-c3-fail-und-gebundener-c4).


## DGN-010: C4-Markerqualifikation tatsächlich bestanden

[Teilnachweis](SQL_SERVER_2025_AI_DGN010_MARKER_REVIEW.md#tatsächlicher-c4-nachweis-und-wave-checkpoint).

Der stabile C4 bestand zwei neue eigene vollständige SQL-17.0.5005.3-Lifecycles,
Tokens 51335850D04844FA/02B1C9C49BF649B8. 982 tatsächliche Nativecalls; je 192 einzelne echte vollständige
51004/FAIL_STATE-Abweisungen über vier Marker/sechs Abweichungen/acht Phasen,
24 an die tatsächliche Abweichung gebundene vollständige Restores und eigene
Source-/Readerprobe vor/nach der Matrix. Keine akzeptierte fremde Fixture.

384 tatsächliche Negativframes, 482 vollständige Stateaufnahmen mit 482000
Id/Value/Payload-Rows und 4000 weitere Source-Proberows aus vier Nativeproben an
Originalframes und ausgewählte Sourcehashes gebunden. Die vollständigen State-
Aufnahmen erhalten alle DB-/Datei-/Config-/Objekt-/Index-/Spalten-/Reader-/Rechte-/
Rollen-/Propertywerte; alle 192 Vergleiche je Profil unverändert, 24 vollständige
Originalbaseline-Restores. Tatsächliche Text-Variantwerte inklusive vollständiger
Bytes/Typ/NULL und tatsächlich leere Rollenliste aufgenommen. Keine Trunkierung,
Byte-/Präfixverkürzung oder angenommene Defaults. Frisch unabhängige DB-ID und
Versions-/Editionsframe attestiert. Regular 300/Gesamtrecovery 60 Sekunden erhalten.

Alle fünf eigenen lokalen Container dieser Wave geschlossen, eigenes guarded
SQLcleanup sowie neue DB-/CID-/Namensabwesenheiten bestanden; kein UNKNOWN.
Die drei historischen C1/C2/C3-FAILs bleiben im selben Sechserledger erhalten.
Vier von sechs Quellenkandidaten verwendet; zwei verbleiben, kein Reset und
keine weiteren lokalen grünen Wiederholungen ohne neue Eingaben. Dreier-FAIL-
Checkpoint und nun vollständiger C4-Ergebnischeckpoint dokumentiert.

13 reine Codec-/Controllergegenfälle PASS; enger unabhängiger Marker-/Parent-/
CI-/Captureabschluss jeweils nur für neue konkrete Risiken, keine Reviewkette.
Echte native Markerqualifikation PASS als separater Sicherheitsclaim; öffentlicher
SELECT-/DML-Producer bleibt Gesamt-WARN, volle Runtime-/TP-PERF-/Indexnettonutzen-
Qualifikation NOT_ESTABLISHED, aktuelle Readerpläne/Indexnutzung weiterhin offen.
Modell-/Tokenverbrauch unbekannt; keine Provider-/Host-/anderen Repositoryeffekte.

Aktuelle Head-/Main-Gates mit tatsächlichem neuen Markerconsumer, PR/Integration,
ganze Treeübernahme, FF-Synchronisierung und eigener lokaler/Remote-Branchcleanup
folgen vor Abschluss. Danach separate tatsächliche Readerplan-/Indexnutzungsfrage;
Workstream und Heartbeat bleiben aktiv.


## DGN-010: Marker integriert, begrenzte Indexnutzung registriert

PR 197 tatsächlich abgeschlossen: Head9/Main7 einschließlich nativer Marker-
Dreierversionenmatrix PASS, Squash 4c7c7382041143c06be76bb18aa4124322a6f0e5, ganzer Tree
87f31d31e55658f16f49a1413a91feffca21b533 exakt, FF-main synchron und eigener lokaler/
Remotebranch abwesend. Historische drei FAILs und Producer-WARN erhalten.

Unmittelbare Folge ist [drei tatsächliche einzelne Reader-Indexnutzungsfenster](SQL_SERVER_2025_AI_DGN010_USAGE_REVIEW.md)
mit vollem Source-/Rechte-/Config-Orakel; Budget sechs neue Korrekturkandidaten/
zwölf serielle eigene Container, Checkpoint3/hard6, zwei stabile positive
Lifecycles erforderlich. Neue konkrete Source-/Cleanup-P2 vor Native geschlossen,
elf reine DMVgegenfälle und ein Cleanupfehlerpfad PASS. Admission noch offen;
kein Readerplan-/Nettonutzen-/voller Runtimeclaim, öffentliche Producer unverändert.
Modell-/Tokenverbrauch unbekannt. Workstream/Heartbeat aktiv.


## Tatsächlicher Native-C1-Nachweis

Der stabile erste Kandidat bestand zwei neue eigene vollständige SQL-17.0.5005.3-
Lifecycles, Tokens EC61C42B0BEF4CB3/F4D8F54238FF4633. Je 31 tatsächliche Nativecalls,
drei einzelne ungezwungene Readerqueries mit vollständigem Zehnrow-/Payload-
Digest; insgesamt sechs Queryfenster/60 Queryrows, 18 Sourceproben/18000 Rows,
zwölf vollständige Stateaufnahmen/12000 Rows und vier echte vollständige
51003/FAIL_RESULT_CONTRACT-Negativframes. Alle ursprünglichen Nativeframes und
die tatsächlich verwendeten Sourcehashes lokal gebunden und unabhängig vom
In-memory-Ergebnis rein geprüft, keine neue SQL-Ausführung dabei.

In beiden Profilen tatsächliche UserSeeks-Differenz 1 am PK ohne Candidate,
1 am Candidate bei vorhandenem Candidate und 1 am PK nach Candidateabbau.
Im mittleren Fenster PK-Differenz 0; alle beobachteten UserScan-/Lookup-/Update-
und Systemcounterdifferenzen 0. Keine INDEX-Hints. Alle relevanten DMVrows waren
vor/nach tatsächlich vorhanden; der fehlende-/neue-Rowpfad wurde hier nicht
nativ erreicht und bleibt nur rein gegengeprüft. Nullwerte sind hier tatsächliche
Differenzen vorhandener Rows, keine Ergänzung fehlender Baselines.

Tatsächliche DB-ID, vollständiger Request, gleicher Startup, exakter fester
SQLtextdigest und tatsächliche Source-/Indexidentität gebunden. Jede vollständige
Statepaarung unverändert, zwei kontrollierte Candidate-DDL-Transitions außerhalb
der jeweiligen Queryintervalle; vollständiger Source-Restore nach Negativprobe.
Guarded SQLcleanup 90/91, frisch unabhängige DB-Abwesenheit und voller eigener
CID-/Namenscleanup bestanden; beide eigenen Container abwesend, kein UNKNOWN.
Ein von sechs Kandidaten verwendet; keine weiteren unveränderten grünen Läufe.

Dies ist ein PASS der begrenzten privaten tatsächlichen Nutzungsbeobachtung,
keine zusätzliche öffentliche Producer-Funktion. Öffentlicher Producer weiterhin
Gesamt-WARN; runtime_qualification und index_net_benefit NOT_ESTABLISHED,
actual_reader_plan NOT_CAPTURED. Keine allgemeine Performanceempfehlung aus drei
Singlequeries. Modell-/Tokenverbrauch unbekannt.

Aktuelle selektierte Head-/Main-Gates, PR/Integration, ganzer Tree, FF-main und
eigener lokaler/Remote-Branchcleanup folgen. Danach nächste zulässige begrenzte
DGN-010-Kostenfrage: Owner-INSERT mit tatsächlichem Rollbackrestore ohne/mit
Candidate. Commit-/Build-/Worker-/volle Readerpläne und vollständige TP-PERF-/
Modul-/Lehrmaterialabnahme bleiben offen; Workstream/Heartbeat aktiv.


## DGN-010: Indexnutzung integriert, Owner-INSERT-/Rollback registriert

PR198 mit aktuellen Head7/Main5 PASS abgeschlossen, Squashd6e0efe9e5d6fd7a0e403fa610176ebbd68cb44b,
ganzer Treee5eaf5d57ac42e8ab99f7db34b5bd5690c4b2fb6 exakt, FF-main synchron/Ownbranches abwesend.
Nächste [private INSERT-/per-Statement-Rollbackfrage](SQL_SERVER_2025_AI_DGN010_INSERT_REVIEW.md)
mit1000Originalrows/max1010kurzzeitig, 10Warmups/18ABBAAA/Control1/46Sources/
29vollständigen Statepaaren: sechsKandidaten/max12eigeneContainer, Checkpoint3/
hard6/zwei stabilevolleLifecycles. Acht neue reine Oraclegegenfälle bestanden;
NativeAdmission erst nach engem Sourceabschluss. Kein Commit-/Build-/Worker-/
Readerplan-/Nettonutzen-/vollerRuntimeclaim; Workstream/Heartbeat aktiv.


## Tatsächlicher Native-C1-Nachweis

Der stabile erste Kandidat bestand zwei neue eigene vollständige SQL-17.0.5005.3-
Lifecycles, Tokens FBFF95626B5D4922/9A106CC3A62A44FE. Je 153 tatsächliche
Nativecalls; insgesamt 58 positive Fenster, 3620 Warmup-/Mess-INSERTs plus zwei
separate positive Einzelcontrols. 36200 vollständige Benchmark-OUTPUT-Roworacles
plus 20 separate Controlrows, 3622 tatsächlich geprüfte positive Rollbacks.
92 volle Sourceproben/92000 Rows und 116 vollständige Stateaufnahmen/116000 Rows;
58 vollständige unveränderte Vorher-/Nachherpaare inklusive aller DB-/Datei-/
Config-Variantbytes/NULL/Metadata/Reader-/Rechte-/Rollen-/Property-/Sourcewerte.
Alle ursprünglichen Nativeframes an tatsächliche Sourcehashes und komplette
transportierte Ergebnisse rein gebunden; keine neue SQL-Ausführung für diese
Recordprüfung. Vier echte vollständige 51003/FAIL_RESULT_CONTRACT-Gegenframes,
Source-/OUTPUT-Negative tatsächlich abgewiesen und ursprüngliche Source erhalten.

Je Profil zehn Warmups, 18 AB/BA/AA-Fenster zu hundert INSERTs, sechs Baseline-/
sechs Vergleichssamples und drei AA-Paare. Mediane pro Hundert-INSERT-Fenster,
Warmups/AA ausgeschlossen; sämtliche Originalsamples/Range/Nullwerte/AA lokal
erhalten. Kein Durchschnitt über die beiden Profile und keine Signifikanzbehauptung.

| Profil | CPU ohne/mit (ms) | Logical Reads ohne/mit | Elapsed ohne/mit (µs) |
| --- | --- | --- | --- |
| 1 | 23.5 / 30.5 | 8958 / 15155.5 | 24686.5 / 36995.5 |
| 2 | 23 / 32 | 8957 / 15152.5 | 22608.5 / 39136 |

In diesen beiden begrenzten Profilen liegen die Candidate-Mediane für CPU,
Logical Reads und Elapsed höher. Das beobachtet INSERT-/OUTPUT-/Rowprüf-/
BEGIN-/ROLLBACK-Batchkosten unter den festgelegten Bedingungen. Keine reine
INSERTcpu, Commit-/Builddauer, gesamte Worker-/Log-I/O oder Gesamt-Nettonutzen-
qualifikation. Ergebnisse anderer Workloads, Datenumfänge und tatsächlicher
Readerpläne sind damit nicht attestiert; ein Seek allein belegt keinen Lesegewinn.

Originalsource1000 nach jedem Statement wiederhergestellt, kurzzeitig nur zehn
zusätzliche synthetische Rows; kein Commit. Acht kontrollierte Create-/Drop-
transitions außerhalb der Messfenster je Profil, Source-/Readerrechte unverändert.
Guarded90/91 sowie frisch unabhängige DB-Abwesenheit, voller eigener CID-/Name-
Cleanup bestanden; beide eigenen Container abwesend, kein UNKNOWN. Ein von sechs
Kandidaten verwendet, keine weiteren unveränderten grünen Wiederholungen.
Acht reine neue Gegenfälle und enger unabhängiger Review ohne offene P1/P2
bestanden; Modell-/Tokenverbrauch unbekannt, keine anderen Repositories verändert.

Dies ist PASS der begrenzten privaten INSERT-/Rollbackbeobachtung; öffentliche
Producer unverändert Gesamt-WARN, Runtime/TP-PERF/Indexnettonutzen NOT_ESTABLISHED.
Tatsächliche Readerpläne, Commit-/Build-/volle Workerkosten, vollständige Modul-/
Lehrmaterial-/Workstreamabnahme bleiben offen. Aktuelle selektierte Head-/Main-
Gates, PR/Integration, ganzer Tree/FF-main und eigener lokaler/Remotebranchcleanup
folgen. Danach unmittelbar nächste zulässige begrenzte Kosten-/Planfrage;
Workstream/Heartbeat bleiben aktiv.


## DGN-010: INSERT integriert, tatsächliche Readerpläne registriert

PR199 vollständig abgeschlossen: Head7/Main5 PASS, Main 83d28cd59ae1f8a34028518e4904e44800236e81,
ganzer Tree a84484ab10f07518decb402972a9a4af10a59a93 exakt, FF-main und eigene Branches bereinigt.
Nächster [begrenzter Readerplanschnitt](SQL_SERVER_2025_AI_DGN010_READER_PLANS_REVIEW.md):
sechs Kandidaten/max12 serielle eigene Container, Checkpoint3/hard6 und zwei
stabile Lifecycles. Drei Originalqueries/volle Source-Statepaare, kurzlebige
gebundene XE-Sitzung nur im eigenen Container; noch keine Nativeadmission.
Commit-/Build-/volle Worker-/Nettonutzen-/vollständige Abnahme offen.


Readerplan-C1 FAIL nach 17 Nativecalls: Lightweight-XML ohne StatementText,
strikte ursprüngliche Zuordnung deshalb nicht bestanden. Eigene DB/CID/Name
vollständig abwesend, kein UNKNOWN. Gebundene Formatkorrektur C2 mit nativer
sql_text-Aktion und tatsächlichen Runtimeparametern im
[Readerplannachweis](SQL_SERVER_2025_AI_DGN010_READER_PLANS_REVIEW.md); zehn reine
Gegenfälle bestanden. Enger Deltaabschluss vor C2-Admission, Budget sechs unverändert.


Readerplan-Checkpoint3: C1/C2 fehlgeschlagene Formatzuordnung, C3 SQL1934
(QUOTED_IDENTIFIER für XML). Alle drei eigenen DB-/CID-/Namenslifecycles
sicher geschlossen, kein UNKNOWN. Drei von sechs Kandidaten verbraucht,
C4 setzt ausschließlich QUOTED_IDENTIFIER ON in der eigenen temporären
Nativeverbindung; Stack-/Source-/Reader-/Cleanupfloors unverändert.
[Gebundene Befunde und Korrektur](SQL_SERVER_2025_AI_DGN010_READER_PLANS_REVIEW.md).


## C6: geschlossener FAIL-Checkpoint der ersten Readerplanwelle

C6 (9577FCB01FA0466E) endet nach 17 Nativecalls mit FAIL: Die tatsächliche
XE-Ereigniszeit 2026-10-12T09:15:54.768Z besteht den bisherigen Vergleich mit dem
Readerintervall 2026-10-12T09:15:54.7684718 bis 2026-10-12T09:15:54.7684718 nicht.
Die vorliegenden Zeitfelder haben unterschiedliche Nachkommastellen; noch kein
akzeptierter tatsächlicher Originalreaderplannachweis und keine stabile
Zweiprofilqualifikation. Die vorangehenden vollständigen Source-/Request-/
Prepared-Text-/Stackoffsetkontrollen wurden tatsächlich erreicht.

Guarded90/91, frische unabhängige DB-Abwesenheit und voller eigener CID-/
Namensabbau sind bestätigt. Cleanup 13.46 Sekunden, kein
UNKNOWN. Alle sechs Kandidaten dieser Welle sind fehlgeschlagen, alle sechs
Container sicher abwesend; harte Sechsergrenze erreicht. Kein C7 in dieser
Welle, keine unveränderte Wiederholung und kein stilles Zurücksetzen.
Vierzehn betroffene reine Tests und enge unabhängige Quellenreviews ohne
offene P1/P2 ersetzen keinen Native-PASS. Modell-/Tokenverbrauch unbekannt.

Dieser konsistente FAIL-Checkpoint wird über PR integriert. Öffentliche
Producer weiterhin Gesamt-WARN, DGN-010 PROPOSED, vollständige TP-PERF-/
Nettonutzen-/Lehrmaterialabnahme NOT_ESTABLISHED. Aktuelle Head-/Main-Gates,
Integration, ganze Treeübernahme, FF-Synchronisierung und eigener lokaler/
Remote-Branchcleanup folgen. Danach unabhängige autorisierte Folienarbeit und
weitere konkrete Sourcekorrekturen ausschließlich mit sichtbarem Folgecheckpoint.

## Readerplan-Folgewelle C7–C12 registriert

PR200 ist vollständig geschlossen: sieben aktuelle Head-/fünf Main-Gates,
ganzer Tree/FF-main/eigener lokaler und Remote-Branchcleanup bestanden.
[UTC-Folgewelle](SQL_SERVER_2025_AI_DGN010_READER_CLOCK_REVIEW.md): tatsächlich
beobachtete Native-Millisekundenauflösung statt falscher genauerer Zeitannahme;
vollständige Originalsource-/Preparedtext-/Request-/Runtime-/Cleanupbindung
unverändert. Explizite fortgeltende Freigabe der weiteren lokalen Entwicklung;
keine erneute gewöhnliche Budgetfrage. Alte sechs FAILs erhalten, kumulativ
C7–C12/max18 Container einschließlich alter sechs; Zwischencheckpoint C9/hard C12.
Fünfzehn reine Methoden bestanden; zwei stabile tatsächliche Lifecycles fehlen.
Parallele KI-Schulungsfolien im eigenen Worktree werden erstellt.


## Tatsächlicher Native-C7-Nachweis und Checkpoint

Kandidat 7 bestand zwei neue eigene vollständige SQL-17.0.5005.3-Lifecycles,
Tokens 102F335BC31343C9/8E457B5AFF5B48FA. Nativecalls je Profil:
32/32. Insgesamt sechs ursprüngliche
ungezwungene Reader-Abfragen mit 60 vollständigen Rowdigests, 18 Sourceproben/
18000 Rows und zwölf vollständige Stateaufnahmen/12000 Rows. Vier echte vollständige
51003/FAIL_RESULT_CONTRACT-Negativframes; ursprüngliche Source tatsächlich erhalten.

| Profil | Ohne Candidate | Mit Candidate | Nach Abbau |
| --- | --- | --- | --- |
| 1 | Clustered Index Seek / [DGN010_OwnPK] | Index Seek / [DGN010_OwnCandidate] | Clustered Index Seek / [DGN010_OwnPK] |
| 2 | Clustered Index Seek / [DGN010_OwnPK] | Index Seek / [DGN010_OwnCandidate] | Clustered Index Seek / [DGN010_OwnPK] |

Jeder passende Actualplan hat tatsächlichen Ergebnisroot10 und Source10,
jeweils genau einen Thread0/eine Ausführung; int-Runtimeparameter101/110.
Vollständiger tatsächlicher Batchtext, Event-Session-/DB-ID, fünfteiliger Request,
Native Stackhandle/Byteoffsets und genau passender vollständiger StatementText
gebunden. Native UTC-Ereignisse auf ihrer tatsächlich gelieferten Millisekunden-
auflösung dem ursprünglichen Readerintervall zugeordnet; kein Querydauerclaim.
Vollständiger Preparedtext-SHA mit Parameterdeklaration und originalem Semikolon,
Native-Statementoffsets ohne ausschließlich terminales Semikolon gebunden.
Kein geschätzter Cacheplan als Actualplan ausgegeben. Original-
ShowplanXML und vollständige tatsächlich ausgeführte/importierte Sourcehashes
privat erhalten und rein erneut an die Records gebunden, keine neue SQL-Ausführung
für diese Recordprüfung. Alle Ringpopulationen vollständig, keine Verdrängung/
Trunkierung/Dropcounter; eigene Sitzungsdefinition vor Abbau vollständig gleich.

Alle Source-/Statepaare einschließlich Config-Variant-/Datei-/Objekt-/Reader-/
Rechte-/Rollen-/Markerbytes vollständig unverändert. Zwei Candidate-DDL-
Transitions außerhalb der Queryaufnahme je Profil. Sechs eigene XE-Sitzungen
nativ abgebaut, je Profil zusätzlich frisch unabhängige Abwesenheit aller drei
Sitzungen. Guarded90/91, neue unabhängige DB-Abwesenheit und voller eigener
CID-/Namensabbau PASS. Alle 8 eigenen Container abwesend, kein UNKNOWN.
6 historische FAIL-Lifecycles bleiben sichtbar. Kumulativ C7; 1 von sechs
Kandidaten der Folgewelle verwendet. Erste Sechserwelle unverändert FAIL erhalten;
positiver Schnitt sicher geschlossen, kein Reset
und keine weiteren unveränderten grünen Wiederholungen. Fünfzehn reine Gegenfälle
und enge unabhängige Source-/Deltareviews ohne offene P1/P2 bestanden. Reviewer
attestierte keine Nativeausführung. Modell-/Tokenverbrauch unbekannt.

PASS der begrenzten privaten tatsächlichen Originalreaderplanbeobachtung.
Öffentliche Producer weiterhin Gesamt-WARN; volle Runtime/TP-PERF und
Indexnettonutzen NOT_ESTABLISHED. Die zusätzliche Instrumentierung ist getrennt
von den bisherigen Performance-Messungen. Ein Index Seek belegt für sich keinen
Nettonutzen. Commit-/Build-/volle Worker-/Modul-/Lehrmaterialabnahme bleiben offen.
Aktuelle selektierte Head-/Main-Gates, PR/Integration, ganze Treeübernahme,
FF-main und eigener lokaler/Remote-Branchcleanup folgen. Danach unmittelbar
nächste zulässige begrenzte Buildkostenfrage; Workstream/Heartbeat bleiben aktiv.

## TSK-012: Eigenständiger KI-Foliensatz vom 2026-10-12

Der ausdrücklich parallel autorisierte Schulungsschnitt enthält
[34 editierbare PowerPoint-Folien](../../Presentations/SQL_Server_2025_KI.pptx)
für CUR-013 bis CUR-022 mit 34 vollständigen Sprechernotizen, Quellen und
konkreten manifestbasierten Demoaufträgen. Alle 18 registrierten Demoentwürfe
sind als neun IMPLEMENTED- und neun PROPOSED-Demos abgedeckt.
[Reproduzierbare Masterquelle und Trainerhinweis](../../Presentations/AI_SQL_Server_2025/README.md)
verlinken die bestehenden Ausführungsverträge, Lösungen und Rubrik. Neue
SlideKeys und eigene KI-Tiefenprofile sind nicht als abgenommen registriert.

Der Quellenstand des Decks ist main 83d28cd59ae1f8a34028518e4904e44800236e81.
Der neue konkrete Reviewbefund erforderte eine eng begrenzte Korrektur von
Folie 31: zwei private Original-Readerplanprofile sind jetzt ausdrücklich
auf der Folie und in den Notizen mit dem kanonischen Clock-Nachweis gebunden.
Quellenstand dieser Aussage ist main 4bfb191; die allgemeine Recherchebindung
an main 83d28cd bleibt dokumentiert.
PR 201 ist auf main 4bfb1914623c3c49fcc287ee8079013a0fad6ddb mit sieben Head-/
fünf Main-Workflows, exakter Treeübernahme, FF-main und eigenem Branchcleanup
abgeschlossen. Öffentliche Producer, volle Runtime-/TP-PERF- und
Indexnettonutzengates bleiben weiterhin getrennt und offen.

Erster Export in PR 202: 147514 Bytes, SHA-256
726398beff736cb9b51818b4596e65c0895a66f568de021ebd3cc3af19202fcd.
34/34 Folien vollständig gerendert und einzeln auf Inhalt, Umbruch,
Lesbarkeit und Privacy geprüft. 13 native Tabellen, 34 Notizen und alle
18 Demo-IDs bestätigt. Paket-, Geometrie-, Arial- und First-Party-Importprüfung
bestanden; ein konservativer Tabellenhöhenhinweis auf Folie 5 zeigt im
tatsächlichen Render keinen Überlauf. Identitätsmetadaten neutralisiert,
keine Medien, Logos, eingebetteten Objekte, Credentials oder privaten Pfade.
Die betroffenen Dateien bestanden die bestehende Privacyprüfung vor Commit.
Beim ersten Export kein editierender PowerPoint-Anwendungstest, keine neue SQL- oder
Provider-/Cloud-/ONNX-/Hostausführung. Rawrender und Prüfrecords bleiben unter
ignoriertem Runtime. Sechs endliche Authoring-/Korrekturkandidaten verbraucht,
Checkpoint3 eingehalten. Der zusätzliche konkrete Reviewbefund zur inzwischen
überholten Readerplanaussage autorisierte einen sichtbaren C7-Folgecheckpoint
ohne Reset der alten Kandidaten. C7 korrigierte nur Folie 31 und ihre Quellen-
notizen; geänderte Folie neu gerendert und einzeln geprüft, notwendige finale
Paket-/Metadaten-/Geometrie-/Importbindung am vollständigen Deck bestanden.
Unveränderte Einzelprüfungen wiederverwendet; kein zusätzlicher Native-Lauf.
Der fachliche Folienumfang ist geschlossen.

PR 202 ist auf main 1a514f92a88e2c4034dfa333026784e496456676 mit acht Head-/
sechs Main-Workflows, exakter Treeübernahme, FF-main und eigenem Branch-/
Worktreecleanup abgeschlossen. Die anschließende Benutzerprobe in PowerPoint
schlug trotz der Paket-/Renderprüfungen fehl: Die Metadatenneutralisierung
benannte den Namespacepräfix um, ließ aber `xsi:type="dcterms:W3CDTF"` mit
ungebundenem `dcterms` stehen. Dieser Fehler bleibt als ursprünglicher FAIL
sichtbar; er betrifft die Office-Lesbarkeit und keine SQL-Demo.

Der ausdrücklich angeforderte Reparaturschnitt auf
`codex/sql2025-ai-pptx-office-repair` erhält den Datumspräfix und ergänzt drei
Regressionen einschließlich der ursprünglichen negativen Kontrolle im
bestehenden Presentation-Workflow. Genau ein korrigiertes Paket wurde in
PowerPoint 16.0 tatsächlich geöffnet: 34 Folien, 13 native Tabellen; Text,
Tabellenzelle und Sprechernotiz bearbeitet, private Kopie gespeichert und erneut
geöffnet, jeweils PASS. Repariertes PPTX in PR 203: 147868 Bytes, SHA-256
f7ac0e74cc41333bff3f0c38ab0f472b1e47cb2b2f7f796c795f0868b1f6f97c.
Alle Folien- und Notizenparts bleiben bytegleich. Keine SQL-, Provider-, Cloud-,
ONNX- oder Hostausführung. Office-Testkopie und ursprünglicher Export bleiben
privat. Head-/Main-Gates, PR-Integration, Synchronisierung und eigenes
Branchcleanup schlossen diesen Reparaturschnitt ab: PR 203 integriert auf
main b17113bd479bef0f8a644d6e6246b53ac0814338, acht Head-/sechs Main-Workflows
PASS, exakter Tree, FF-main sauber und eigener lokaler/Remote-Branch entfernt.

TSK-012 bleibt offen: tatsächliche Teilnehmererprobung, gemessene Lehrzeiten,
vollständige Teaching Paths und Generalprobe fehlen. Der Workstream und sein
Heartbeat bleiben aktiv.

### Erweiterte Einführung für Anwender:innen ohne KI-Erfahrung

Der anschließende Benutzerauftrag verlangt einen umfangreicheren Einstieg vor
den Fachdetails. Der Schnitt `codex/sql2025-ai-beginner-introduction` erweitert
TSK-012 auf 61 Folien: 27 neue Einführungsfolien vor den bisherigen 34 Fachfolien.
Ein durchgehender synthetischer MOD_A-Wissensbasisfall erklärt Quelle/Fassung,
KI/ML, Modell, Training/Inferenz, Sprachmodell, Tokens, Rollen und Anwendungsfälle.
Server/Client/CL, vorbereitete Labverbindung, Rechte und späterer Modellzugang
erhalten verständliche Voraussetzungen und nächste Schritte. Cloudkonto,
ChatGPT, Copilot, Modellservice, Preview und neue Datenbankobjekte sind für den
ersten geometrischen DECLARE-/VALUES-/SELECT-Versuch nicht erforderlich.
Vorhersage, vollständiger Code und besprochene Sollwerte 0/1/2 sind getrennt;
die Werte sind mathematisch hergeleitet, kein neuer SQL-Runtimebefund und keine
gemessene Sprachsemantik. Quellen-/Nichtantwortfälle schließen den Einstieg ab.

Der reproduzierbare Export leitet Folienzahl und native Tabellen aus der
Masterquelle ab und erlaubt getrennte private Build-/Ausgabepfade. C1 hielt
an der Eingangsprüfung des Finalizers an, weil Receipt und finaler Ausgabeordner nicht getrennt
waren. Dieser FAIL bleibt privat erhalten. C2 mit getrennten Ordnern bestand
Paket, Geometrie, Arial und finalen First-Party-Import. Alle 61 Folien wurden
neu gerendert und einzeln visuell geprüft. Ein konservativer Tabellenhöhenhinweis
auf Folie 32 zeigte im konkreten Render keinen Überlauf. PowerPoint 16.0 öffnete
61 Folien mit 23 nativen Tabellen und 61 Sprechernotizen. Text, Tabellenzelle
und Notiz bearbeiten sowie private Kopie speichern/erneut öffnen jeweils PASS.
Aktuelles neutrales PPTX: 245680 Bytes, SHA-256
72275f2fa0156799e4346b35fb3436fe420b113f0ae38dea0b94cd3a10b62a99.
Alle 18 Demo-IDs, neun IMPLEMENTED/neun PROPOSED und ihre offenen Gates bleiben
erhalten. Arbeitsheftlösungen und Rubrik bleiben unverändert. Trainerleitfaden,
Backlog und Workstreamplan sind mit dem neuen gemeinsamen Einstieg abgeglichen.

Keine SQL-, Provider-, Cloud- oder ONNX-Ausführung und keine roten Hoständerungen. Office-Testkopien,
Renderdaten und Prüfnachweise bleiben privat. Head-/Main-Gates, PR-Integration,
Synchronisierung und eigenes Branchcleanup bilden den Integrationsabschluss.
Lehrzeiten, Teilnehmererprobung, vollständige Teaching Paths und Generalprobe
bleiben offen; die alten Zeitplanwerte belegen keine Dauer dieses größeren Decks.

## Fortsetzung: begrenzte DGN-010-Build-/Dropkosten

PR 204 ist vollständig abgeschlossen: main 7a68bb7261ffbdb21b6cf7ece4d1d88cc1d5bee6,
neun Head-/sieben Main-Workflows PASS, ganzer Tree/FF-main sauber und eigener
lokaler/Remote-Branch entfernt. Der nächste zulässige SQL-Schritt ist auf
`codex/sql2025-ai-dgn010-build-costs` begonnen: [getrennte Build-/Dropfenster](SQL_SERVER_2025_AI_DGN010_BUILD_COST_REVIEW.md)
unter TSK-011/CUR-021. Sechs Kandidaten/max12 eigene serielle Container,
Checkpoint3/hard6; zwei vollständige stabile positive Profile. Bestehende
Reader-/INSERT-/Folienfehler bleiben erhalten. Unbekannter Modell-/Tokenverbrauch
bleibt unbekannt, keine weitere gewöhnliche Budgetfreigabe erforderlich.

Private feste Quellen und sieben reine Gegenproben/CLI-help vorhanden; enger
unabhängiger DDL-/Lease-/Request-/Counter-/Vollstate-/Cleanupquellenreview ohne
offene P1/P2. Noch keine neue Nativeausführung. Messbereiche getrennt von
bestehenden Reader-/Rollbackfenstern, vollständige 13-Key-States, echte Source-
und DROP-ohne-Indexnegative, gleiche bytegenaue Eigentumsmarker und KnownEnd-
300/60-Sekunden-/CID-Cleanupfloors. Öffentliche Producer weiterhin WARN,
DGN-010 PROPOSED; vollständige Runtime/TP-PERF/Nettonutzen bleiben offen.

### Native Buildkosten-C1 zweimal bestanden

Zwei stabile neue vollständige Profile, je 34 Nativecalls: vier Builds/vier
Abbaue, 16000 Source-Rows, 20000 Vollstate-Rows und vier tatsächliche
51003-Negativen/Source-Restore. Native Request-/DDL-/Counter-/UTC-/gehaltene
Index-/Spalten-Lease und unabhängige Vollstatebindung bestanden. Alle acht
Zahlen im [Buildkostennachweis](SQL_SERVER_2025_AI_DGN010_BUILD_COST_REVIEW.md)
erhalten; keine isolierten Worker-/Log-/Commit-/vollen Lifecyclezeiten daraus
ableiten. Writes 0 bei DROP bleibt eine begrenzte tatsächliche Requestbeobachtung.

Beide SQL-90/91-/frischen DB-Abwesenheits-/vollständigen CID-/Namens-/zusätzlichen
Ownerlabel-Abwesenheitskontrollen PASS, kein UNKNOWN und keine eigene Restinstanz.
Ein Kandidat/zwei Container verbraucht; keine unveränderte grüne Wiederholung.
Sieben reine Gegenproben und enger unabhängiger Quellenabschluss bestanden;
Vollrecords anschließend an tatsächliche unveränderte Ausführungsquellen rein
gebunden, kein zusätzlicher SQL-Lauf. Private Inputs/Logs/Records bleiben privat.
Aktuelle Head-/Main-/PR-/Tree-/FF-/Ownbranchgates folgen. Danach unmittelbar
bereits erhobene Indexseiten rein aufbereiten; Nettonutzen/volle Abnahme offen.

## DGN-010: reine Folgeaufbereitung vorhandener Indexseiten

PR 205 ist auf main 6079f7a50f3ab0a61d1e21ec9d79a9d2d19e2e16 mit sieben
Head-/fünf Main-Workflows PASS, ganzer Tree/FF-main sauber und eigenem lokalem/
Remote-Branchcleanup abgeschlossen. Beide eigenen Testinstanzen abwesend,
kein UNKNOWN. Unmittelbare Folge auf `codex/sql2025-ai-dgn010-index-pages`:
[vorhandene native Indexseiten](SQL_SERVER_2025_AI_DGN010_INDEX_PAGES_REVIEW.md)
aus denselben exakt hashgebundenen Vollrecords und unveränderten Quellen.

Je Profil fünf feste A/B/A/B/A-Aufnahmen. Originaler PK durchgängig 18 Used/
33 Reserved Pages, Candidate in B 17 Used/33 Reserved Pages; ausgewählte
Indexsumme 18/33 gegen 35/66. Candidate in A tatsächlich abwesend, kein
fehlender Wert als gemessene Null. Rowcount-1000-Katalogaufnahme und die
vollständige tatsächliche Source-Rowqualifikation bleiben getrennt.
Alle zehn Beobachtungen erhalten, drei reine Gegenproben bestanden,
null zusätzliche SQLcalls oder Container, keine unveränderte grüne Wiederholung.

Used/Reserved sind Partitionallokationen einschließlich Verwaltungsaufwand,
keine vollständige Datei-/RAM-/Log-/Nutzdatenmessung oder Nettonutzenqualifikation.
Quelle/Record/DDL-/Cleanupbelege unverändert; kein weiteres Review derselben
geprüften Nativequellen. Aktuelle PR-/Head-/Main-/Tree-/FF-/Ownbranchgates folgen,
danach öffentlicher getrennt begrenzter Kostenrecord-/Aggregationsvertrag.

## DGN-010: öffentlicher reiner Kostenrecordvertrag

PR206 ist vollständig abgeschlossen: main 5c5c2596f54db93b33229fe3c99bf98881500a4b,
sieben Head-/fünf Main-Workflows PASS, ganzer Tree gleich, FF-main sauber und
eigener lokaler/Remote-Branch entfernt. Unmittelbare Folge auf
`codex/sql2025-ai-dgn010-cost-records`: [öffentlicher numerischer Vertrag](SQL_SERVER_2025_AI_DGN010_COST_CONTRACT.md),
sechs Kandidaten/Checkpoint3/hard6, keine neuen SQLcalls oder Container.

15 synthetische Gegenproben bestanden. Enger unabhängiger Review meldete drei P2,
anschließend geschlossen: siebte datetime2(7)-Stelle, nullable Typbindung und volle
Statekontinuität zwischen Fenstern. Zwei vorhandene exakt hashgebundene Native-
Vollrecords mit separat gebundenen Caller-DBID-Frames rein neu geprüft: acht
DDL-Fenster, 16000 Source-/20000 State-Rows. Nativequellen und frühere tatsächliche
Negativ-/Cleanupbelege bleiben unverändert; keine unveränderte grüne Wiederholung.

Alle beiden Samples/Nullen/exakte Mediane und fünf A/B/A/B/A-Allokationen je Profil
erhalten. Numerischer PASS attestiert keine bloßen Controllerflags; öffentliche
Producer WARN/DGN-010 PROPOSED, Runtime/TP-PERF/Worker/Nettonutzen NOT_ESTABLISHED.
Nur zwei neue Workflowtrigger/ein reiner statischer Schritt, Runtimeauswahl am
tatsächlichen Head/Main False erforderlich. Aktuelle PR-/Head-/Main-/Tree-/FF-/
Ownbranchgates folgen; danach öffentliche begrenzte Producerintegration.

## DGN-010: öffentliche feste Kostenproducer-Eingaben

PR207 ist vollständig abgeschlossen: main f8b212f1e25370cda958892a53c75890a3e7367a,
acht Head-/sechs Main-Workflows PASS, Runtimeauswahl False (Runtimejob SKIPPED,
kein Runtime-PASS), ganzer Tree gleich, FF-main sauber und eigener Branch lokal/
remote entfernt. Unmittelbare erste Produceranbindung auf
`codex/sql2025-ai-dgn010-cost-inputs`: [feste öffentliche SQLeingaben](SQL_SERVER_2025_AI_DGN010_COST_INPUT_REVIEW.md).
Sechs Quellenkandidaten/Checkpoint3/hard6, keine neuen SQLcalls/Container.

Sechs reine Gegenproben und enger unabhängiger Kompositionsreview ohne offene
P1/P2 bestanden. Vorhandene feste DDL-/Statequellen übernommen, nur Source-NULL-
Guard enger. Vollständige DB-/Marker-/Source-/gehaltene Leasebindung vor DDL;
alle acht vorhandenen tatsächlichen DDL-Leases rein angebunden. Kein Prozessstart
oder SQLaufruf; kein ausführbarer Kostencontroller und keine neue Nativeabnahme.

Zwei neue Trigger/ein statischer Schritt, Runtimejob unverändert. Aktuelle
PR-/Head-/Main-/Tree-/FF-/Ownbranchgates folgen. Danach tatsächlichen öffentlichen
Kostencontroller vorbereiten; Producer WARN/DGN-010 PROPOSED und volle Runtime/
TP-PERF/Worker/Nettonutzen NOT_ESTABLISHED bleiben erhalten.

## DGN-010: öffentliche Kostencontroller-Vorbereitung

PR208 vollständig abgeschlossen: main 40d56069f28e4add5e2380fd2c3cd2ec93853afe,
acht Head-/sechs Main-Workflows PASS, tatsächliche Runtimeauswahl False/Job SKIPPED,
ganzer Tree gleich, FF-main sauber und eigener lokaler/Remote-Branch entfernt.
Unmittelbare Fortsetzung auf `codex/sql2025-ai-dgn010-cost-controller`:
[öffentlicher begrenzter Kostencontroller](SQL_SERVER_2025_AI_DGN010_COST_CONTROLLER_REVIEW.md),
sechs Quellenkandidaten/Checkpoint3/hard6, noch keine lokale Controller-Nativequalifikation.

Elf synthetische Controller- und sieben Eingabemethoden PASS, CLI-help ohneClient;
enger unabhängiger neuer Ablauf-/KnownEnd-/Negativ-/Input-/Cleanupreview ohne
offene P1/P2. Vier DDL-Fenster, acht Source-/zehn Vollstateaufnahmen, feste echte
Source-/DROP-Abwesenheitsnegative, volle Zwischenfensterkontinuität und einmalige
Parent300/60-Deadlines. UNKNOWN sperrt SQL und erhält Inputs; Unlinkfehler bleiben
FAIL_CLEANUP. CLI nur geprüfte Aggregate bei WARN und vollständigem Cleanup.

Neue Demosource erfordert tatsächliche bestehende CI-Runtimeauswahl True,
vorhandene isolierte Versionsmatrix inklusive eigenem CI-Cleanup. Diese Matrix
prüft bisherige Scopes, keine neue Kostencontroller-Nativequalifikation.
Aktuelle PR-/Head-/Main-/Tree-/FF-/Ownbranchgates folgen; danach separat budgetierte
Nativequalifikation des neuen Controllers. Producer WARN/DGN-010 PROPOSED,
Runtime/TP-PERF/Worker/Nettonutzen NOT_ESTABLISHED; alle historischen FAILs erhalten.

## DGN-010: separate native öffentliche Kostenqualifikation

PR209 vollständig abgeschlossen: main bf206ccbb1b0892773b9b0ef785b85e80b1ba9d0,
neun Head-/sieben Main-Workflows PASS, tatsächliche bestehende Versionsmatrix
inklusive eigenem CI-Cleanup an Head/Main bestanden, ganzer Tree gleich,
FF-main sauber und eigener lokaler/Remote-Branch entfernt. Unmittelbare Folge
auf `codex/sql2025-ai-dgn010-cost-qualification`: [separate neue Nativewelle](SQL_SERVER_2025_AI_DGN010_COST_PUBLIC_REVIEW.md).

Vor erster Admission sechs kohärente Quellenkandidaten/max12 neue eigene serielle
Container, Checkpoint3/hard6. Zwei2025positive, je zwei2019/22-SKIPs vorSetup und
ein2025Setupfault/Recovery; insgesamt sieben feste Slots. Vollständige aktuelle
Publicquellenbindung nach alleiniger EOL-Normalisierung, ausgeführte Rohbytes
jeAdmission zusätzlich. Enger unabhängiger neuer Input-/Adapter-/Budgetreview
ohne offene P1/P2; bestehende Endstatus-/Containerfloors unverändert.

Native noch offen. 300 Sekunden regulär/einmal60gesamtCleanup einschließlich
frischer DB-Abwesenheit und voll gebundenem CID-/Namensabbau. UNKNOWN sperrt SQL
und erhält Inputs, keine ungebundene Rettung oder Ledgerreset. Provider-/Cloud-/
ONNX-/Hostgrenzen unverändert. DGN-010 PROPOSED/Producer WARN; volle Runtime/
TP-PERF/Worker/Commit/Nettonutzen/Modulabnahme bleibt NOT_ESTABLISHED.

### Öffentliche Kosten-C1 vollständig nativ bestanden

Alle sieben festen eigenen Slots bestanden: zwei2025positive/WARN, je zwei
2019/22-SKIP_VERSION vorSetup, ein tatsächlicher erwarteter FAIL_EXECUTION nach
PASS-Setup mit vollständiger Recovery. 97 protokollierte Nativephasen ohne
Readiness-/separate Engineversionqueries; acht DDL-Fenster, 16000 Source-/20000
Vollstate-Rows, vier echte51003-Abweisungen/Source-Restore. Alle sieben DB-/
CID-/Namenslifecycles geschlossen, eigene Ownerlabel-Inventur leer, Inputs
abwesend/keinUNKNOWN. C1/sieben Container verbraucht, keine Nativekorrekturwelle.

Alle Native-Vollframes/Records/negativen Fehlerframes/Source-/State-/DDL-/
Caller-DB-/OID-/Aggregate-/Cleanupbelege rein an tatsächliche ausgeführte Quellen
gebunden; null zusätzlicher SQLaufruf dafür. Sämtliche acht Zahlen einschließlich
CREATE49211us/Cpu46 aus Profil1 bleiben erhalten und jeProfil getrennt.

Ein zusätzlicher reiner EOL-Bindungshelfer war zunächst zu eng; erste Admission
startete nach dessen FAIL. Scope/Budget/Safety bereits kanonisch registriert und
im Adapter durchgesetzt. Danach raw- oder ausschließlichEOL-identische Review-
Quellen korrekt gebunden, keine Codeänderung/Nativewiederholung. Privater Receipt
erst danach erstellt; Ablaufbefund bleibt im konkreten Nachweis sichtbar.

Begrenzte öffentliche Kosten-/Versions-/Setuprecoveryqualifikation PASS; tatsächlicher
Producer WARN/DGN-010 PROPOSED. Runtime/TP-PERF/Worker/Commit/Nettonutzen/Lehrpfade/
Modulabnahme bleiben offen. Aktuelle Head-/Main-/PR-/Tree-/FF-/Ownbranchgates folgen;
danach nächste unabhängige offene Kosten-/Lehrpfadfrage, keine grünen Wiederholungen.

## TSK-012: konkrete Teaching Paths zum erweiterten Einsteigerdeck

PR210 vollständig abgeschlossen: main 658ed3be28e8c349e5270a0a2c98cc32cfaaf264,
sieben Head-/fünf Main-Workflows PASS, tatsächliche Runtimeauswahl False, ganzer
Tree gleich, FF-main sauber und eigener lokaler/Remote-Branch entfernt. Alle
sieben eigenen Cost-Nativecontainer/Inputs abwesend. Unmittelbare unabhängige
Fortsetzung auf `codex/sql2025-ai-beginner-teaching-paths`:
[konkrete Teaching Paths](../HowTo/SQL_SERVER_2025_AI_TEACHING_PATHS.md) für61Folien.

Gemeinsamer90-Minuten-Einstieg: bekannte Quelle/SELECT, einzelne KI-Begriffe,
Version/Client/CL/Lab/Rechte, geometrische Vorhersage/SQL/Ergebnis, echte Modell-
hürden und Quelle/Antwort/Nichtantwort. BASIS240brutto/210netto/30Pause,
STANDARD480/420/60 mit allen acht Offlineaufgaben, VERTIEFUNG960/840/120 über
zwei Tage mit abgegrenzten Beleglese-/Entwurfsaufgaben. Aktuelle kanonische
Fenster ersetzen alte150/390/640 als neue Unterrichtsplanung; historische
Modulgewichte bleiben erhalten. Foliennummern aus tatsächlicher Masterquelle.

Alle Zeiten ungemessene Planwerte, keine tatsächliche Teilnehmer-/Generalprobe.
Lösungen/Rubrik ausschließlich im bestehenden Arbeitsheft, keine neue Bewertung
oder Liveausführungsfreigabe. Kein neues PPTX/Render/Office-/SQL-/Providerprofil.
Lehrpfad-Praxis/Freigaben/volle TP-PERF-/Modulabnahme und TSK012/014 bleiben offen.
Kleine reine Planung: ein Owner, keine zusätzliche Reviewkette; aktuelle lokale
Summen-/Link-/Material-/Privacy- und Head-/Main-/PR-/Tree-/FF-/Ownbranchgates folgen.

## TSK-004: neue begrenzte CL-Istwertqualifikation

PR211 vollständig abgeschlossen: main 3675a8c3663155519da548de5560fdecc1dc0d95,
neun Head-/sieben Main-Workflows PASS, RuntimeauswahlFalse, ganzerTreegleich,
FF-main sauber/eigener lokaler undRemoteBranchentfernt. TeachingPaths geplant,
keine Teilnehmer-/Zeit-/Generalprobenabnahme; PPTXunverändert. UnmittelbareFolge
auf `codex/sql2025-ai-cl-result-qualification`: [neue CL-Istwertwelle](SQL_SERVER_2025_AI_CL_RESULT_REVIEW.md).

VorAdmission sechs neuekohärenteKandidaten/max12 zusätzlicheeigeneContainer,
Checkpoint3/hard6/zwei stabilevollständigeProfile. Alte dreiContainer/FAILs und
fehlende frühereSQL-Abwesenheitsbelege bleiben erhalten, keinLedgerreset.
NativeCL150/160/170: tatsächlicheSkalare/normalisierteKoordinaten, explizite
NULL-Gates/24 erwarteteNativeNULL-Rejections jeProfil, volleChunkrows oder
volleErrorNumber/Severity/State/Line/Procedure/Messagebytes. Keine erzwungene
LowCL-Denialannahme, dokumentierteGrenze vonbeobachtetemBuildresultat trennen.

Acht reineMethoden/CLIhelp undengerunabhängigerQuellenabschluss nachgeschlossener
Dependency-P2 bestanden. Neue eigeneCL-DB/Marker, gleicherKnownEnd/300-60-/
vollgebundenerCID-/Namenscleanupfloor; tatsächlicherCL170BaselineRestore.
Native zunächst offen; keineLockerungöffentlicherCL170Demos oderProvider-/
Cloud-/ONNX-/Hosteffekte. TSK004/volleDemo-/Curriculum-/Workstreamabnahme offen.

### Neue CL-Istwert-C1 zweimal nativ bestanden

Je48 protokolliertePhasen ohneReadiness-/Versionbootstrap, sechs vollständige
Skalarrecords/48 nativeNULL-Abweisungen/sechs volleChunkrecords/16Vollstates und
zwei vollständigeCL170BaselineRestores. BeideeigeneDB-/CID-/Namenslifecycles
geschlossen, Ownerlabelinventurleer, Inputsabwesend/keinUNKNOWN; einneuer
Ausführungskandidat/zweiContainer, alte dreiFAIL-Container unverändert erhalten.

TatsächlicheSkalare beiCL150/160/170: Dimensions3/float32, Norm5,
UnitNorm1.000000023841858, Euc0/Dot-25/Cos0 undalle drei normalisierten
Koordinaten. Vorabfixierte1e-5-Toleranz, keinebitgenaue1 behaupten.
BeiCL150/160 tatsächlicherChunkError102/Severity15/State38/Line3/ProcedureNULL
mitvollenMessagebytes „Incorrect syntax near '='.“; kein208 undkeinekorrekten
Chunkrows. DeralteDenialoracle-FAIL ist erklärt; OBSERVED_OTHER_ERROR_NO_AVAILABILITY_CLAIM,
keine generelleLowCL-Funktionsfreigabe. CL170vollständigezweiFixtureRows.

AlleNative-Skalar-/NULL-Fehler-/Chunk-/State-/Caller-/Source-/Restore-/
Abwesenheitsframes rein gebunden, null weitereSQLcalls dafür. Begrenzte
Istwert-/Oracle-/Fehleraufbewahrungs-/Restore-/CleanupqualifikationPASS;
öffentlicheCL170Profile/alteFAILs erhalten, volleTSK004-/Provider-/Demo-/
Curriculum-/Workstreamabnahme offen. AktuelleHead-/Main-/PR-/Tree-/FF-/
Ownbranchgates folgen; danach nächste unabhängigeoffeneQualifikationsfrage.

## TSK-007: aktuelle öffentliche Providerverträge

PR212 vollständig abgeschlossen: sieben Head-/fünf Main-Workflows bestanden,
Squash187ecae23d20c724e4a060ae909f6f237ff2ce60, vollständiger Tree
5d24a814a996795517a3a64c8e5f429ac8857a6b exakt übernommen; main synchronisiert,
sauber und eigener lokaler/Remote-Branch abgebaut. Danach den aktuellen lokalen
Modellpfad quellengebunden geprüft.

[Aktueller Modellpfadbefund](../HowTo/SQL_SERVER_2025_AI_MODEL_PATHS.md#aktualisierte-öffentliche-verträge-am-2026-10-12)
am sauberen Lab-Commit f4c9fcd30c397e25c95e57d7aeecc98dc194063e:
RAG weiterhin BLOCKED_DEC033, tatsächliches sqlcmd-Passwortargument und kein
öffentlicher alternativer Executor. Neue öffentliche Shared-Gateway-Sitzungs-
APIs sind vorhanden, Backendvertrag Llama.cpp/OVMS, keine allgemeine Ollama-
Bridge. Lokaler Ollama-Probe/Katalog erfolgreich; kein Modell aufgerufen und
keine Capability-/Digest-/Qualitätsabnahme daraus abgeleitet. Sieben betroffene
Labquellen bytegebunden, null SQL/Inferenz, andere Repositories unverändert.
TSK007/Live-RAG/volle Abnahme offen, alte FAILs und Cloud-/ONNX-/Hostgrenzen
erhalten. Aktuelle PR-/Head-/Main-/Tree-/FF-/Ownbranchgates folgen; anschließend
unmittelbar unabhängige Kostencontrollerqualifikation aus TSK013.

## TSK-013: getrennte Kostencontroller-Gateprüfung

PR213 abgeschlossen: acht Head-/sechs Main-Workflows PASS, Squash
e15e821ebfe99ff23924fb2498e218f0dd1c0193, voller identischer Tree, main FF/sauber,
eigener lokaler/Remote-Branch entfernt. RAG-Secretblocker bleibt sichtbar. Danach
unmittelbar [Kosten-CI-Consumer](SQL_SERVER_2025_AI_DGN010_COST_CI_REVIEW.md)
vorbereitet: zehn synthetische Consumermethoden/elf Selector-Methoden PASS,
volle bounded Record-/Aggregate-/Negativ-/Cleanupbindung und fail-closed2025Gate.
-y0-Adapter ermöglicht Vollframes bei unverändertem Remote-End-/Envsecretvertrag.
Keine lokale SQLwiederholung. Sechs Quellenkandidaten/Checkpoint3/hard6, maximal21
eigene CI-Container einschließlich Integration. Enger unabhängiger Review und
tatsächliche aktuelle Head-/Main-Matrizen folgen; DGN010 PROPOSED/WARN, volle
TP-PERF-/Workstreamabnahme offen und historische FAILs erhalten.
