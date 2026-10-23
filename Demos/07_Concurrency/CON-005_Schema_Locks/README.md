# CON-005 – Schemasperren trotz NOLOCK beobachten

Diese Demo zeigt einen eng begrenzten Konflikt: Eine offene Schemaänderung hält
Sch-M (Schema Modification; Schemaänderungssperre). Eine Leseabfrage benötigt
Sch-S (Schema Stability; Schemastabilitätssperre) und wartet auch mit `NOLOCK`.
Die Beobachtung ordnet beide Sperren derselben Ressource und den richtigen
Sitzungen zu. Danach wird die Schemaänderung zurückgerollt.

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` – begrenzter Schemasperrenschnitt; Developer/Linux/Docker 2019, 2022 und 2025 |
| Sicherheitsstufe | `YELLOW` – ausschließlich eigene Wegwerfinstanz ohne fremde Daten |
| Zielversionen / Compatibility Level | SQL Server 2019/150, 2022/160, 2025/170; Compatibility Level ist die Datenbank-Kompatibilitätsstufe |
| Edition / Plattform | eigenständige Database Engine; Developer in Linux-Containern als Prüfziel; Windows und andere Editionen nicht empirisch qualifiziert |
| Ausführung | vorhandener Framework-Harness; drei gleichzeitig steuerbare `sqlcmd`-Sitzungen |
| Grenzen | 120 Sekunden regulär, 30 Sekunden Cleanup, 15 Sekunden je Signal-/Beobachtungsschritt |
| Daten | zwei Zeilen; höchstens 128 MiB je Datenbankdatei; Dateipfade aus der Instanzvorgabe |
| Testprofil | `TP-CON` – Nebenläufigkeit und Sperrkonflikte |

## 1. Lernziel und fachliche Aussage

`NOLOCK` entspricht für den Tabellenzugriff `READUNCOMMITTED`. Es verzichtet auf
gemeinsame Datensperren für diesen Lesezugriff; Schemasperren bleiben nötig.
Die Demo belegt konkret gewährtes Sch-M gegen wartendes Sch-S auf einem
Tabellenobjekt, einschließlich `LCK_M_SCH_S` (Warten auf Schemastabilität) und
der tatsächlichen `blocking_session_id` (unmittelbar blockierende Sitzung).

**Evidenzklasse:** dokumentiertes Produktverhalten, empirischer Lauf und
begrenzte Diagnosemethode. Eine Zahl aktiver Sitzungen oder irgendeine
Blockierung reicht für den Ergebnisvertrag nicht aus.

Sperreskalation, Deadlocks und eine vollständige Abdeckung aller Kompilierungs-
oder Metadatensperren gehören nicht zu diesem Schnitt. Es gibt keine
Leistungsbehauptung und keinen Benchmark. `CON-004` (Blockierungsketten)
und `CON-006` (zyklische Sperrkonflikte) bleiben eigenständige Demos.

## 2. Voraussetzungen und Sicherheit

Verwenden Sie eine eigene isolierte Wegwerfinstanz, mindestens zwei logische
Prozessorkerne, 2 GiB Arbeitsspeicher und Platz für die Standarddateien von
`model` sowie die begrenzten Demodateien. Die Testcontainer erhalten zwei
Prozessorkerne und 3 GiB Arbeitsspeicher. Eine bestehende Standarddatei über
128 MiB führt zum Sicherheitsabbruch; es wird keine große Last erzeugt.

Der ausführende Login benötigt `CREATE ANY DATABASE` und Kontrolle über eine
gegebenenfalls bereits eigene Zieldatenbank. Für die Diagnosesichten sind
unter SQL Server 2019 `VIEW SERVER STATE`, ab SQL Server 2022
`VIEW SERVER PERFORMANCE STATE` nötig. Ein neu erstelltes Datenbankobjekt
gehört dem erstellenden Login; dessen Rechte umfassen die eigene Schemaänderung.

`00_Preflight.sql` prüft Version, Engine-Edition, Rechte und die ausdrückliche
Bestätigung der isolierten Umgebung. Fehlende Rechte ergeben
`SKIP_PERMISSION` (Voraussetzung fehlt), bevor Setup beginnt. Fehlende
Sicherheitsbestätigungen ergeben `FAIL_SAFETY` (Sicherheitsvertrag verletzt).

Vor Wiederverwendung, Akteursstart und Cleanup (Aufräumen) müssen die vier
Datenbankmarker `SQLPERF.Project`, `SQLPERF.ContractVersion`, `SQLPERF.DemoId`
und `SQLPERF.RunToken` vollständig, binär und mit exakter Bytelänge passen.
Unbekanntes Eigentum ergibt `FAIL_STATE` (Zustand nicht bestätigt); die
Datenbank bleibt erhalten. Die Skripte prüfen vollständige Unicode-Rohwerte
vor einer Umwandlung in einen begrenzten Namenstyp.

## 3. Schritt-für-Schritt-Anleitung

Folgen Sie zuerst dem [zentralen Ausführungsleitfaden](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md):
Instanz und Arbeitsplatz vorbereiten, den dortigen Aufrufer laden und
`CON-005` (Schemasperren trotz NOLOCK) auswählen. Der manifestbasierte Aufruf
verwendet das vorhandene `run_demo.py`, `manifest.json` und drei unabhängige
Sitzungen. SQL-Authentifizierung bezieht das Kennwort ausschließlich aus
`SQLCMDPASSWORD`; Kennwörter gehören nicht in Dateien oder Befehlsargumente.

```powershell
Invoke-SqlPerfDemo -DemoId CON-005 -Server $server -Authentication $authentication -Username $username -ConfirmIsolatedLab
```

Der Aufrufer benötigt dieselben Verbindungsvariablen wie im Leitfaden.
`-ConfirmIsolatedLab` bestätigt die eigene isolierte Instanz. Starten Sie
keinen zweiten Lauf mit demselben Lauftoken parallel.

| Phase | Datei | Erwartetes Ergebnis |
|---|---|---|
| Preflight | `00_Preflight.sql` | Rechte, Zielkennung und Sicherheitsrahmen bestätigt |
| Setup | `10_Setup.sql` | eigene markierte Datenbank, zwei Zeilen, Signale und Evidenztabellen |
| Baseline | `20_Baseline.sql` | zwei Zeilen, Summe 30, zwei Spalten |
| Demonstration | `Sessions/problem.json` | drei Sitzungen erzeugen und beobachten den konkreten Sperrkonflikt |
| Observation | `40_Observation.sql` | vollständiger Sperrnachweis, fertiger Leser, Schema zurückgerollt |
| Comparison | `60_Comparison.sql` | dieselbe NOLOCK-Lesung ohne offene Schemaänderung; identische Daten |
| Cleanup | `90_Cleanup.sql` | vollständig markierte Datenbank entfernt |

Eine separate Gegenmaßnahmephase ist nicht nötig: Der Blockierer nimmt seine
Schemaänderung bereits nach dem Beobachtungssignal zurück. Der Vergleich
ändert weder Isolation noch Instanzoptionen. Baseline und Vergleich behandeln
dieselben zwei Zeilen; eine Cacheleerung oder ein Aufwärmlauf ist dafür unnötig.

## 4. Sitzungen und erwartete Beobachtung

1. **BLOCKER – Blockierer:** bestätigt Start und wartet außerhalb seiner
   Transaktion auf die Bereitschaft von Leser und Beobachter. Er fügt dann
   `TransientColumn` durch `ALTER TABLE` in einer offenen Transaktion hinzu.
2. **READER – Leser:** bestätigt Bereitschaft. Seine dynamische Leseabfrage
   wird erst nach `READER_GO` kompiliert; vorherige Kompilierung darf die
   Bereitschaftsmeldung nicht bereits blockieren.
3. **OBSERVER – Beobachter:** löst die Objektkennung vor dem Konflikt auf.
   Nach tatsächlich gewährtem Sch-M gibt er den Leser frei. Erst wenn
   `sys.dm_tran_locks` (dynamische Verwaltungssicht für Sperren) Sch-M/GRANT
   und Sch-S/WAIT auf derselben Ressource und `sys.dm_exec_requests`
   (Sicht für laufende Anforderungen) die passende Blockerbeziehung mit
   `LCK_M_SCH_S` zeigen, speichert er den Nachweis und gibt den Blockierer frei.

Die Ressourcenzuordnung vergleicht Typ, Untertyp, Datenbank, Objekt,
Beschreibung und Sperrpartition. Der Diagnosefilter bindet die Sitzungsnummern
zusätzlich an die laufbezogene Sitzungskennung. Ein eigener Batch bestätigt
`CONTEXT_INFO` (binäre Sitzungskennung), bevor andere Sitzungen deren Wert
über die Diagnosesicht verwenden. Alle Eigentums- und Objektauflösungen
enden vor der Schemaänderung; der Beobachter fragt danach keine Metadaten
des blockierten Tabellenobjekts ab.

Freigaben stammen aus unabhängigen Sitzungen außerhalb der gehaltenen
Schemaänderungstransaktion. Ein darin geschriebenes Signal wäre noch nicht
sichtbar. Kurzes begrenztes Polling beobachtet den Zustand; feste Wartezeiten
erzeugen keine fachliche Reihenfolge. Die Diagnosesichten sind flüchtige
Momentaufnahmen, kein transaktional konsistenter Historiennachweis.

Nach Freigabe rollt der Blockierer zurück. Der Leser erhält **zwei Zeilen mit
Summe 30**. `TransientColumn` existiert danach nicht, und es bleiben keine
eigenen offenen Transaktionen oder Schemasperren zurück. Der Vergleich liefert
dieselben Daten. Daraus folgt keine allgemeine Empfehlung für `NOLOCK`:
unsaubere oder widersprüchliche Datenlesungen bleiben dessen eigene Risiken.

## 5. Ergebnis, Abbruch und Recovery

`PASS / OK` (Vertrag erfüllt) setzt den konkreten Konfliktnachweis, den
Leserabschluss, die Rücknahme und erfolgreichen Cleanup voraus. Fehlendes
Sch-M oder Sch-S bei erfüllten Voraussetzungen ist ein Fehler, kein Skip.
Die Datenbankassertionen verwenden exakte fachliche Invarianten gemäß
`FWK-011` (Ergebnisnormalisierung); konkrete Millisekundenwerte sind kein
Erfolgskriterium. Zeitgrenzen dienen ausschließlich dem Schutz.

Der vorhandene Orchestrator beendet bei Fehler oder Timeout seine eigenen
Prozesse. Der Blockierer versucht im Fehlerpfad ein Rollback; ein
Verbindungsabbruch rollt eine noch offene Transaktion ebenfalls zurück.
Nach begonnenem Setup versucht der Harness unabhängig vom vorherigen Ergebnis
den begrenzten Cleanup. Dieser liest alle Marker erneut, beendet Verbindungen
ausschließlich zur eigenen Datenbank durch `SINGLE_USER WITH ROLLBACK IMMEDIATE`
und entfernt diese Datenbank. Fremde Datenbanken oder nach Sitzungsnummern
ausgewählte fremde Prozesse werden nicht verändert.

Prüfen Sie nach jedem Lauf die Abwesenheit der eigenen Datenbank, wie im
Leitfaden beschrieben. Ein Timeout allein ist kein Nachweis für Cleanup.
`FAIL_CLEANUP` (Aufräumen gescheitert) hat Vorrang. Nach einem harten Abbruch
oder unklaren Markern gilt zunächst der **Erhaltungsweg im Leitfaden**:
Datenbank und bisherige Instanz aufbewahren, keinen Wiederholungs- oder
eigenständigen Löschaufruf starten. Der geprüfte markergebundene Cleanup
innerhalb des Harness ist keine pauschale Freigabe eines manuellen Recovery-
oder Resetaufrufs. Erst nach geklärtem Zustand beginnt ein neuer Preflight.

Scheitert die erstmalige Markierung direkt nach `CREATE DATABASE`, wird keine
unmarkierte Datenbank zwangsweise entfernt. Der Fehler und Restzustand bleiben
sichtbar. Der allgemeine Erstmarkierungs-Recovery-Vertrag wird durch diesen
begrenzten Schemasperrenschnitt nicht zusätzlich qualifiziert.

## 6. Tests und Grenzen der Abnahme

`Tests/Runtime/run_con005.py` führt zwei vollständige Lifecycles je Zielversion
aus und prüft die Datenbankabwesenheit unabhängig. Dazu kommen die exakten
Eigentumsgegenproben für Setup und Cleanup, vollständige Datei-Ablehnung,
idempotente Wiederverwendung, ungültige ungekürzte Eingaben, fehlende
Sicherheitsbestätigung und ein kontrollierter Rechte-Skip.

Fehlende und verfälschte Sperrevidenz muss scheitern. Ein absichtlich
unterdrücktes Freigabesignal erzwingt außerdem einen Orchestrierungstimeout
während eines unabhängig beobachteten Sch-M-/Sch-S-Konflikts; auch danach
müssen Harness-Cleanup und Datenbankabwesenheit bestätigt sein. Die absichtlich
fehlerhafte Variante liegt nur in einer temporären Prüfkopie.

Am 2026-10-23 ist der finale SQL-Stand lokal auf SQL Server 2022 geprüft:
zwei reguläre Lifecycles, je 30 Setup-/Cleanup-Eigentumsgegenproben,
28 ungültige vollständige Eingaben, Sicherheits-/Rechteprüfungen, vollständiger
Inventarvergleich mit zusätzlicher eigener Datenbank, ein weiterer Voll-Lifecycle
mit 48 äußeren Leerzeichen und kleingeschriebenem Lauftoken, elf verfälschte
Evidenzfälle sowie ein Timeout während eines unabhängig beobachteten Konflikts.
Das nach der Signalnormalisierung angepasste Freigabeanker-Teststück wurde
gezielt erneut geprüft. Alle eigenen lokalen Datenbanken und Container sind entfernt.

Der unabhängige Quellenreview schloss Transaktionssichtbarkeit, Objekt-/Laufbindung,
ASCII-Rohprüfung (ASCII ist der grundlegende lateinische Zeichensatz),
NULL-Signalbudgets und den Containerabbau. Fünf Offline-Testmethoden prüfen
den tatsächlichen Bash-Cleanupblock einschließlich zehn negativer Docker-/
Identitätsfälle. Frühe fehlgeschlagene Diagnose- und Testversuche bleiben lokale
Evidenz; sie werden nicht zu Erfolgsbelegen umgedeutet.

Am 2026-10-23 bestand der Implementierungsstand
`ab27d42214ab24b6b12b2189e5b5e32da535166e` den
[Versionslauf 39981693499](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/39981693499):
statische Verträge sowie die vollständigen Prüfungen auf SQL Server
2019/150, 2022/160 und 2025/170, jeweils Developer unter Linux in eigenen
Dockercontainern. Alle oben genannten regulären und negativen Fälle bestanden
auf jeder Version, einschließlich des Abbruchs bei gehaltenem Konflikt und
des eigenen Datenbank- und Containerabbaus. Die ursprüngliche volle lokale
2022-Suite endete am veralteten Freigabeanker der Timeout-Prüfkopie; dessen
gezielte Korrektur ist zusätzlich durch diesen vollständigen Versionslauf belegt.
[PR310](https://github.com/gecompat/SQL_PerformanceSchulung/pull/310)
bindet die aktuellen Prüfungen des anschließenden Dokumentationsstands,
die frischen Main-Prüfungen und den Integrationsnachweis.
Scheduling, Objektkennungen und Wait-Dauer sind keine Golden Values.
Windows-, Editions-, Hardware- und umfassende Metadatenpfadabnahmen sowie
Sperreskalation werden nicht aus Linux-Developer-Läufen abgeleitet.

## 7. Quellen und fachliche Zuordnung

| Quelle | Aussage / Stand |
|---|---|
| `SRC-004` – [Transaction locking and row versioning guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide?view=sql-server-ver17) | Schemasperren; SQL Server 2019–2025 |
| [Table hints](https://learn.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-table?view=sql-server-ver17) | NOLOCK benötigt weiterhin Sch-S; Abruf 2026-10-23 |
| [sys.dm_tran_locks](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-tran-locks-transact-sql?view=sql-server-ver17) | Ressourcen, Modi, Status und Rechte; Abruf 2026-10-23 |
| [sys.dm_exec_requests](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-requests-transact-sql?view=sql-server-ver17) | wartender Request und Blockerbeziehung; Abruf 2026-10-23 |

Die Quellenbefunde und der genehmigte begrenzte Plan liegen kanonisch bei
`TSK-016` (Analyze-Labs als gezielte Curriculum-Ergänzungen) in der
[Registry](../../../.ai/identity/registry.json) und ihrer
[Backlogansicht](../../../.ai/BACKLOG.md). Aus dem Analyze-Quellprojekt wurden
weder Runner noch Framework importiert. Die Signalprimitive stammen aus dem
vorhandenen Schulungspfad von `CON-004`.

| Traceability | Zuordnung |
|---|---|
| Lernziel | `LO-M05-02` – Blockierungsdiagnose |
| Claim | `CLM-066` – Blocking vom Head Blocker aus analysieren; ergänzender Schemasperrenfall |
| Demo-ID | `CON-005` – Schemasperren trotz NOLOCK |
| Testprofil | `TP-CON` – Nebenläufigkeit |
