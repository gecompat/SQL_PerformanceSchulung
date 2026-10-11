# QRY-019 – Feste SQL-Struktur, Wertbindung und Rechtegegenproben

Stand: 2026-10-11. TSK-009, CUR-018/CUR-021, TP-RUN.
Basis: `4de76ffc9eeb23882e5b6f4c02be3b32576b8f75`, Branch
`codex/sql2025-ai-sql-input-policy`. IMPLEMENTED; aktuelle PR-/Main-Gates offen.

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
Ein anfänglicher Validatoraufruf verwendete einen nicht existierenden Dateinamen;
der korrekte Frameworkvalidator bestand. Kein SQL-/Oraclebypass oder Retry bis grün.

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
Aktuelle PR-/Main-Evidenz und vollständiger Branchabschluss sind vor Abschluss erforderlich.
