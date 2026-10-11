# QRY-019 – Feste SQL-Struktur, Wertbindung und Rechtegegenproben

Stand: 2026-10-11. TSK-009, CUR-018/CUR-021, TP-RUN.
Basis: `4de76ffc9eeb23882e5b6f4c02be3b32576b8f75`, Branch
`codex/sql2025-ai-sql-input-policy`. IMPLEMENTED; lokaler Schnitt samt PR-/Main-Gates integriert.

## Ergebnisvertrag und Sicherheitsgrenze

Das markierte FWK-010/FWK-011-Paket besitzt drei synthetische Inventoryrows und acht
eingefrorene Kandidaten. Eine Policyview vergleicht den vollständigen Statement- und
Identifiertext bytegenau mit einer einzigen erlaubten Form und begrenzt Werte vor
Konversion auf 400 Unicodebytes. Zwei Kandidaten sind erlaubt, sechs abgelehnt.
Nur der kanonische SQL-Text wird ausgeführt; Modelltext und Identifier werden nie
konkateniert. Der Quote-/DDL-Text bleibt ein separat gebundener nvarchar(200)-Wert und
trifft seine eigene Literalrow. Keine privilegierte Ausführung eines Angriffstrings.

QRY019_reader ist ein Datenbankbenutzer WITHOUT LOGIN mit SELECT ausschließlich auf
lab.Inventory. Der Eigentümer-Harness kopiert erlaubte Inputs in lokale Tabellenvariablen
und führt tatsächliche Wertqueries sowie feste UPDATE-/DROP-/CREATE-Gegenproben unter
EXECUTE AS USER aus. REVERT ist im Erfolgs- und Fehlerpfad gebunden. Rechtefehler 229,
229/3701 beziehungsweise 262 zählen nur zusammen mit drei unveränderten vollständigen
Inventoryrows, bestehender Inventory und abwesender Counterprobe-Tabelle.
Die Kontrollprozedur wird nicht an den Querybenutzer freigegeben. Dies ist kein fertig
authentifizierter Anwendungsservice, allgemeiner SQL-Parser oder Live-LLM-Sicherheitsnachweis.

Baseline zählt einen tatsächlichen erlaubten Querytreffer. Comparison zählt zwei erlaubte,
sechs abgelehnte Kandidaten, zwei gebundene Querytreffer und drei Rechteverweigerungen.
Die fünf FWK-011-Assertions sind nichtleer; fehlender Bestand muss scheitern.

## Lokale Qualifikation und konkrete Fehler

17.x bestand zwei vollständige Lifecycles mit unabhängiger DB-Abwesenheit,
Setup-Idempotenz, 80 bytegenauen Markerabweichungen und sieben fachlichen Gegenproben.
Diese betreffen leere Kandidaten, leere Inventory, falsche Farbe, Strukturleerzeichen,
überlangen Wert, anderen Literalwert und bewusst erweitertes UPDATE-Recht. Jeder Fall
scheiterte mit FAIL_RESULT_CONTRACT; er ersetzt keine Produktionsprüfung.
Eigene Testcontainer liefen mit vier CPUs / sechs GiB RAM und wurden nach kontrollierter
Ownerbindung entfernt, ihre Abwesenheit separat geprüft. Versionsqualifikation 2019/2022
bestand je zwei SKIP_VERSION-Lifecycles vor Setup, unabhängige DB-Abwesenheit und eigenen
Containerabbau. Diese Versionen liefern keinen Parameter-/Rechteruntime-PASS.

Vor dem Demopaket liefen zwei begrenzte vorbereitende SQL-Proben. Die Auswahlprobe
bestand zwei erlaubte / sechs abgelehnte Fälle; ihre erste Ausgabe war PRINT auf stderr,
während der private Adapter stdout las. Die geänderte SELECT-Ausgabe bestand.
Die erste Ausführungsprobe scheiterte an vorzeitig kompiliertem USE vor CREATE DATABASE,
die erste Korrektur am gemischten DECLARE von Tabellenvariable und Skalarwerten. Nach
zwei kohärenten Aufbaukorrekturen bestand sie zwei tatsächliche Wertbindungen, drei
Rechteverweigerungen, unveränderte drei Rows sowie DB- und eigenen Containerabbau.
Diese Entwicklungsfehler sind keine erfolgreich ausgeführten Parameter-/Rechtekontrollen.
Das daraus erzeugte vollständige Demopaket bestand den ersten lokalen Runtimeversuch.
Zwei anfängliche Validatoraufrufe verwendeten nicht existierende Dateinamen;
die korrekten Framework-/ADV-006/007-Validatoren bestanden. Kein SQL-/Oraclebypass oder Retry bis grün.

Der unabhängige Quellenreview fand eine konkrete P2-Lücke: Alle sechs negativen
Statementfixtures konnten durch NULL ersetzt werden, während die Counts PASS lieferten.
Die erste kohärente Demopaketkorrektur bindet deshalb sämtliche acht Fallinhalte in
beiden Richtungen bytegenau an ein getrennt gehaltenes eingefrorenes Fixturemodell.
Eine achte fachliche Gegenprobe ersetzt alle sechs negativen Statementtexte durch NULL.
Der gezielte unabhängige Findingabschluss bestätigte die Korrektur ohne Restbefund.
Die geänderte 17.x-Runtime bestand erneut zwei Lifecycles, fünf Ergebnisassertions,
80 Markergegenproben und alle acht fachlichen Gegenproben mit unabhängigem DB-/Containerabbau.
Die früheren Versionsprüfungen bleiben gebunden an unveränderten Preflight vor Setup;
die neuen 17.x-Inputs begründen diese erneute lokale Qualifikation.
Quellenreview ist keine zusätzliche Runtimeattestation. Windows, Podman, weitere Editionen,
Serverlogin-/Anwendungszugang, beliebige generierte SQL-Formen und Live-LLM bleiben offen.

## Aufwand, CI und nächste Schritte

Ein Implementierungsverantwortlicher, eine Demo, zwei Lifecycles je Version, ein fokussierter
Review und höchstens zwei kohärente Korrekturwellen im Demopaket. Checkpoints sind lokale
Qualifikation, stabiler Reviewkandidat, aktuelle Head-CI und Integration mit Main-Gates,
Synchronisierung und eigenem Cleanup. Modell-/Tokenverbrauch bleibt unbekannt.
Kein weiterer Provider, Modellaufruf oder Provisionierungspfad in versionierten Quellen.
Der bestehende Runner und die drei KI-Versionsjobs werden erweitert. Die geplante
Docker-/Podman-Vollmatrix erhöht sich von 324 auf 336 Runs, kein ausgeführter Vollnachweis.
Die bestehende Katalogregression bleibt erhalten; grüne Logs werden nicht erneut voll gelesen,
und administrativer Abschluss verursacht keine Reviewkette oder zusätzliche SQL-Qualifikation.

```powershell
python Tests/Runtime/run_sql2025_ai_local.py --target docker --container '<eigener-container>' --expected-major 17 --demo QRY-019
```

SQLCMDPASSWORD bleibt die Passwortquelle ohne Wert in Prozessargumenten. Alle Daten sind
synthetisch. SRC-099/SRC-091 wurden am 2026-10-11 an Microsoft-Primärquellen geprüft.
TSK-009 bleibt IN_PROGRESS: Tenant-/Datenschutz-/Providergrenzen sind separat offen.
Alle 49 PR-Prüfungen am aktuellen Head `3ac2b6c63c435446208b51d5955f440e39510e2e`
bestanden, einschließlich der [KI-Matrix](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38133330578)
und der [bestehenden Regression](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38133330553).
[PR 138](https://github.com/gecompat/SQL_PerformanceSchulung/pull/138) ist in
`25a7c0af1b377b9250deeac4cf4288224900689f` integriert. Vollständige Tree-Identität wurde
geprüft, main synchronisiert und der eigene Branch lokal/remote entfernt.
Alle elf Main-Workflows dieses Integrationscommits bestanden, darunter die
[KI-Matrix](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38133801177)
und die [bestehende Regression](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38133801231).
Die übrigen Plattform-/Anwendungs-/Livegates bleiben sichtbar offen; kein Gesamtabschluss.


## Nächster Checkpoint: private CON-010-Vorbereitung

Der nächste zulässige Schritt CON-010 ist mit einer begrenzten privaten 17.x-Vorprobe
begonnen. Eine echte RLS-Filterpolicy bindet zwei synthetische Dokumente und ihre
Geometrievektoren an TenantA/TenantB als eingeschränkte Datenbankbenutzer WITHOUT LOGIN.
Drei tatsächliche Ergebnisfälle bestanden: je eine eigene vollständige Quelle mit
Exact-Cosinusdistanz null für A/B und kein Kontext für einen nicht zugeordneten Benutzer.
Ein manipulierter Sessionwert mit Tenant B erweitert den Zugriff von A nicht; die
Policy verwendet die Datenbankidentität. Die erweiterte Vorprobe bestand zusätzlich
drei tatsächliche Verweigerungen: Policyänderung mit 33268, Fremdimpersonation mit
15517 und Lesen nach SELECT-Revocation mit 229. Bestehende aktive Policy und Zielbindung
werden davor/danach aus dem Eigentümerkontext geprüft. Der erste Rechteversuch erwartete
irrtümlich 15151 statt 33268 und blieb FAIL; eigener Containerabbau bestand. Nach neuer
Runtime-/Primärquellen-Evidenz wurde ausschließlich diese Fehlerbindung korrigiert und
die Vor-/Nachkontrolle gegen fehlende/NULL-Metadaten verstärkt. Der geänderte Lauf bestand.
REVERT, expliziter Sessionreset, DB-Abbau und separat geprüfte eigene Containerabwesenheit
bestanden. Das ist nur eine Vorprobe,
kein implementiertes CON-010-Demopaket und keine Serverlogin-/Pooling-/ANN-Abnahme.
SRC-093 und der [Microsoft-Fehlerkatalog](https://learn.microsoft.com/en-us/sql/relational-databases/errors-events/database-engine-events-and-errors-31000-to-41399?view=sql-server-ver17)
wurden erneut gelesen. Nächster kleiner Schnitt:
vollständiger markierter Lifecycle mit echten Policy-/Impersonations-/Revocationkontrollen,
Sessionwechsel und Ergebnis-/Leakagegegenproben. ANN bleibt von TSK-006 abhängig,
Cloud-/ONNX-/Live-Modellgrenzen unverändert offen. Der KI-Heartbeat bleibt aktiv.

Die privaten Proben bleiben unter Runtime, außerhalb der versionierten Demoquellen.
Dieser Nachweis behauptet dafür keinen unabhängigen Quellenreview oder vollständigen
FWK-010/FWK-011-/TP-CON-Lifecycle. Der bestehende CON-010-Entwurf bleibt PROPOSED.
