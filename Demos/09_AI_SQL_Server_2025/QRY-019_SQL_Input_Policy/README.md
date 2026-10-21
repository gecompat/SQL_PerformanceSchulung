# QRY-019 – Feste SQL-Struktur und gebundene Werte

Status: IMPLEMENTED; lokaler Slice über [PR 138](https://github.com/gecompat/SQL_PerformanceSchulung/pull/138) mit grünen Head-/Main-Gates integriert. Allgemeine Tenant-/Providerabnahme bleibt getrennt offen.
Zuordnung: CUR-018/CUR-021, TSK-009, TP-RUN. Acht eingefrorene synthetische
Ausgabefixtures ersetzen Modellantworten. Kein Modellaufruf, keine Generationsqualifikation.

## Lernziel und Aussagegrenze

Eine KI (künstliche Intelligenz; Verfahren für Aufgaben wie Textverarbeitung oder Vorhersagen) darf Werte für eine vorab festgelegte Query liefern. Die Statementstruktur und
Identifier werden vollständig bytegenau gegen die feste erlaubte Form geprüft.
Eine abgelehnte Struktur wird angezeigt und niemals ausgeführt. Nur der kanonische
SQL-Text gelangt zu sp_executesql; Werte bleiben separate Parameter.

Die Policy ist absichtlich eine einzige erlaubte Form, kein allgemeiner SQL-Parser.
Parameter ersetzen keine Identifier. Ein Wert mit Quote, Semikolon und DROP-Text darf
als Literalwert vorkommen: Die Fixture besitzt genau einen solchen Schlüssel und liefert
die erwartete Farbe `literal`. Das ist ein positiver Nachweis tatsächlicher Wertbindung.
Tokenzahl und Inferenzzeit sind N/A; Live-LLM- und Anwendungspfad bleiben separat.

## Voraussetzungen und Sicherheitsstufe

Ziel: SQL Server 2025 (17.x), CL 170, Enterprise Developer auf Linux/Docker.
Die Demo benutzt keine VECTOR-/Modellfunktion. Die gemeinsame Workstreamgrenze
beendet 2019/2022 vor Setup mit SKIP_VERSION; das ist keine technische Aussage,
dass Parameterbindung auf älteren Versionen unmöglich wäre. Windows, Podman und
andere Editionen benötigen eigene Qualifikation. Grün, eine Session, 180 Sekunden
regulär und separat 60 Sekunden Cleanup. Elf Basisrows, keine Lastgenerierung.
Dateigrenzen: 256 MiB Daten / 64 MiB Log; Testcontainer vier CPUs / sechs GiB RAM (Random Access Memory; Arbeitsspeicher).
Vorgeschlagenes Lab: vier logische CPUs, 16 GiB Host-RAM, 10 GiB freier Laborplatz.

Setup/Cleanup benötigen CREATE DATABASE und Eigentümerrechte ausschließlich in der
eigenen markierten Datenbank. Setup erzeugt QRY019_reader WITHOUT LOGIN mit SELECT
ausschließlich auf lab.Inventory. Das ist ein echter nichtprivilegierter Datenbankbenutzer,
kein Serverlogin. Der Eigentümer-Harness liest die synthetischen Kandidaten und ruft
lab.RunControls auf. Darin werden Werte vor EXECUTE AS in lokale Tabellenvariablen
kopiert und Query-/Rechtegegenproben unter dem eingeschränkten Benutzer ausgeführt.
REVERT erfolgt auch bei Fehlern. Die Prozedur wird dem Querybenutzer nicht freigegeben.
Das demonstriert einen kontrollierten Harness, keinen fertigen Anwendungszugangsservice.

## Schritt-für-Schritt-Anleitung

Der [zentrale Leitfaden](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md) beschreibt
den manifestbasiert ausgeführten FWK-010-Harness. Eigene dedizierte Testinstanz:

```powershell
python Demos/00_Framework/Tools/run_demo.py Demos/09_AI_SQL_Server_2025/QRY-019_SQL_Input_Policy/manifest.json --server '<instanz>' --auth integrated --show-output
```

SQL-Authentifizierung verwendet ausschließlich SQLCMDPASSWORD. Preflight ist read-only
und prüft Version, Edition, Setuprechte und bestehende Eigentumsmarker. Setup erzeugt
die drei Inventoryrows, acht Kandidaten, Policyview und Kontrollprozedur. Baseline führt
den normalen MOD-A-Wert unter QRY019_reader aus und prüft genau eine blaue Ergebnisrow.
Demonstration zeigt alle Kandidaten und Entscheidungen; Observation zeigt den tatsächlichen
Objektgrant; Mitigation zeigt die beiden freigegebenen Werte mit der festen Struktur.
Comparison führt beide gebundenen Queries, drei feste Rechtegegenproben und vollständige
Row-/Objektnachkontrollen aus. Fünf tatsächlich gemessene FWK-011-Metriken bestimmen PASS.

| Eingabe | Ergebnis |
|---|---|
| Kanonische Struktur und normaler Wert | Erlaubt, tatsächlicher Treffer `blue` |
| Kanonische Struktur und Quote-/DDL-Text als Wert | Erlaubt, tatsächlicher Literal-Treffer |
| Zusatzstatement, manipulierter Identifier, zusätzliches Strukturleerzeichen | Abgelehnt |
| NULL-Statement, überlanger Identifier, Wert über 400 Unicodebytes | Abgelehnt vor begrenzter Konversion |

UPDATE muss mit 229, DROP mit 229 oder 3701 und CREATE mit 262 scheitern. Die Kontrolle
verlangt zusätzlich drei unveränderte erwartete Inventoryrows, bestehende Inventory und
keine Counterprobe-Tabelle. Ein zufälliger Syntaxfehler ersetzt keine Rechteverweigerung.
Leere Policy-/Inventorybestände dürfen niemals PASS ergeben.

Der Harness versucht nach gestartetem Setup immer Cleanup. Manueller markergebundener Recovery:

```powershell
sqlcmd -S '<instanz>' -E -b -v DemoId='QRY-019' RunToken='LOCAL' TargetDatabase='SQLPERF_LAB_QRY019_LOCAL' -i Demos/09_AI_SQL_Server_2025/QRY-019_SQL_Input_Policy/90_Cleanup.sql
```

Alle vier vollständigen Eigentumsmarker werden bytegenau vor Fachphasen, Setup und
Cleanup geprüft. Bei fehlenden/falschen Markern bleibt die Datenbank zur Klärung erhalten.
Der Runtime-Test prüft unabhängige DB-Abwesenheit nach beiden Lifecycles, Setup-Idempotenz,
80 Markerabweichungen und acht fachliche Gegenproben, darunter die Ersetzung aller
negativen Statementfixtures durch NULL bei unveränderten Counts. Die vollständigen
Fallinhalte werden ebenfalls bytegenau mit dem eingefrorenen Vertrag verglichen.
Kein fremder Container wird übernommen.

Übung: Warum darf Kandidat 2 passieren, obwohl der Wert DROP TABLE enthält?
Musterantwort: Die Struktur ist unverändert; sp_executesql bindet den vollständigen Text
als Wert. Die Query liefert ausschließlich die zu diesem Literal gehörende Fixture.
Ein Identifier müsste aus einer festen erlaubten Menge gewählt werden, nicht parameterisiert.

## Quellen und offene Pfade

SRC-099 und SRC-091 im [Quellenregister](../../../Documentation/Research/SOURCE_REGISTER.md),
Primärquellen geprüft am 2026-10-11. Diese feste Form belegt keine allgemeine Sicherheit
beliebiger generierter SQL-Texte und keine Prompt-Injection-Abwehr eines Live-Modells.
Keine Cloud-, Endpoint-, Credential-, ONNX- oder globalen Hosteffekte.
