# Lokale Testumgebung für Schulungsdemos

Dieses How-to beschreibt, wie eine Schulungsdemo auf einer **vorhandenen SQL-Server-Instanz** ausgeführt wird. Alle Beispiele verwenden neutrale Platzhalter in spitzen Klammern.

Für die eigentliche Vorführung führt der [zentrale Ausführungsleitfaden](DEMO_EXECUTION_GUIDE.md)
durch Auswahl, Start und Ergebnisdeutung. Diese Seite vertieft die Vorbereitung
einer vorhandenen Testinstanz. Nach einem Abbruch gilt der dort beschriebene
Erhaltungsweg; die Eigentumsprüfung der Cleanupskripte ist noch nicht für alle
Demos belastbar.

## 1. Auswahl des Ausführungspfads

Wählen Sie den kleinsten ausreichenden Ausführungspfad. Wenn keine geeignete
Testinstanz vorhanden ist, verwenden Sie den verlinkten Container-Quickstart.

| Stufe | Pfad | Verwendung | Stand |
|---:|---|---|---|
| 1 | vorhandene Testinstanz plus eigene synthetische Testdatenbank | Standard, wenn ein geeigneter SQL Server verfügbar ist | in diesem How-to beschrieben |
| 2 | Steuerung mit Transact-SQL (T-SQL), der Abfragesprache von SQL Server, innerhalb der isolierten Testinstanz | Pläne, Statistiken, Indizes, Blocking, Deadlocks, Query Store und Extended Events | in diesem How-to beschrieben |
| 3 | containerisierte Einzelinstanz | wenn kein SQL Server vorhanden ist oder reproduzierbare Prozessor-/Arbeitsspeichergrenzen benötigt werden | [Container-Quickstart](CONTAINER_QUICKSTART.md); Bereitstellung mit Docker (`INF-002`) oder Podman (`INF-003`) |
| 4 | virtuelle Maschine mit Hyper-V | Anforderungen an Windows, Betriebssystem, Speicher oder Isolation | noch kein verfügbarer Ausführungspfad in dieser Anleitung |
| 5 | Mehrinstanz- oder Netzwerktopologie | verteilte oder netzwerkabhängige Kernaussage | noch kein verfügbarer Ausführungspfad in dieser Anleitung |

Entscheidungshilfe:

- Steht eine SQL-Server-Instanz zur Verfügung, die ausschließlich für die Übung vorgesehen ist und **verworfen oder zurückgesetzt werden darf**, beginnen Sie bei Stufe 1. Die Voraussetzungen der gewählten Demo bleiben maßgeblich.
- Steht keine Instanz zur Verfügung, führt `Documentation/HowTo/CONTAINER_QUICKSTART.md` über den geprüften Docker- oder Podman-Arbeitsplatzpfad. Der vollständige interaktive Lifecycle ist für `CON-004` (Blockierungsketten verfolgen) auf SQL Server 2025 validiert.
- Hyper-V und Mehrinstanztopologien werden hier nicht bereitgestellt. Ihre technischen Voraussetzungen stehen in der [Runner-Topologie](../Architecture/RUNNER_TOPOLOGY.md).

Läufe gegen eine vorhandene Instanz sind Entwicklungs- und Fehlersuchevidenz. Sie ersetzen keine Gate-Evidenz; diese entsteht ausschließlich auf GitHub-gehosteten Runnern über die Versionsmatrix 2019, 2022 und 2025 (DEC-047).

## 2. Mindestvoraussetzungen

| Voraussetzung | Anforderung |
|---|---|
| SQL Server | 2019, 2022 oder 2025; Engine Edition 2, 3 oder 4 (Standard, Enterprise oder Express) |
| Instanzcharakter | Wegwerf- oder Testinstanz. Der Lauf legt Datenbanken an und löscht sie wieder. |
| Berechtigungen | `CREATE DATABASE`, `ALTER DATABASE`, `SHOWPLAN`, `VIEW SERVER STATE`, ab SQL Server 2022 zusätzlich `VIEW SERVER PERFORMANCE STATE` |
| Client | `sqlcmd` im Suchpfad |
| Python | 3.12 oder neuer, ausschließlich Standardbibliothek |

Ressourcenbelegung: Die Testdatenbanken sind synthetisch und werden je Lauf neu erzeugt. Ihre Größe ergibt sich aus dem Setup-Skript der jeweiligen Demo. Das Zeitbudget steht im Manifest; `QRY-001` (Indexfreundliche Suchbedingungen) verwendet beispielsweise `timeout_seconds: 240` mit `cleanup_timeout_seconds: 60`. Eine gemessene Angabe zu Speicher- und CPU-Bedarf je Demo liegt derzeit nicht vor und wird hier bewusst nicht geschätzt.

`OPT-013` (Sortieren mit zu wenig Arbeitsspeicher) erzeugt gezielt einen Sort-Spill und belastet dabei `tempdb`. `CON-004` hält Blockierungen über mehrere Sitzungen. Beide sind als `YELLOW` eingestuft und verlangen eine isolierte Instanz.

## 3. Sichere Bereitstellung der Anmeldedaten

Kennwörter werden ausschließlich über die Umgebungsvariable `SQLCMDPASSWORD` übergeben und nie als Argument gesetzt. Repository-Secrets werden für lokale Läufe nicht benötigt und dürfen dafür auch nicht angelegt werden.

Windows PowerShell:

```powershell
$secure = Read-Host -AsSecureString 'Kennwort'
$env:SQLCMDPASSWORD = [System.Net.NetworkCredential]::new('', $secure).Password
```

Linux und macOS:

```bash
read -rs SQLCMDPASSWORD
export SQLCMDPASSWORD
```

Beide Varianten halten das Kennwort aus der Kommandozeilenhistorie heraus. Nach dem Lauf wird die Variable wieder entfernt:

```powershell
Remove-Item Env:SQLCMDPASSWORD
```

```bash
unset SQLCMDPASSWORD
```

Steht Windows-Authentifizierung zur Verfügung, ist sie vorzuziehen. Dann entfällt `SQLCMDPASSWORD` vollständig; das Harness wird mit `--auth integrated` und ohne `--username` aufgerufen.

## 4. Verbindung, Healthcheck und Versionserkennung

Der Healthcheck bestätigt, dass die Instanz erreichbar und antwortbereit ist:

```bash
sqlcmd -S <instanz> -U <anmeldename> -Q "SELECT 1"
```

Trägt die Instanz ein selbstsigniertes Zertifikat, lehnt `sqlcmd` ab Version 18 die Verbindung ab. Erst dann wird `-C` ergänzt. Das ist eine bewusste Absenkung der Transportprüfung und gilt nur für Wegwerfinstanzen.

Die Versionserkennung liefert die Werte, die der Preflight jeder Demo auswertet:

```sql
SELECT
    SERVERPROPERTY('ProductMajorVersion') AS MajorVersion,
    SERVERPROPERTY('ProductLevel')        AS ProductLevel,
    SERVERPROPERTY('EngineEdition')       AS EngineEdition;
```

| MajorVersion | SQL Server | Compatibility Level der Demos |
|---:|---|---:|
| 15 | 2019 | 150 |
| 16 | 2022 | 160 |
| 17 | 2025 | 170 |

Die Runtime-Runner führen dieselbe Prüfung selbst aus. Ohne `--expected-major` lesen sie die Hauptversion aus der Instanz; mit Angabe prüfen sie sie zusätzlich.

## 5. Anlage und Entfernung der synthetischen Schulungsdatenbank

Die Datenbank wird nicht von Hand angelegt. Das Setup-Skript der Demo erzeugt sie, das Cleanup-Skript entfernt sie wieder. Der Name folgt einem festen Schema:

```
SQLPERF_LAB_<DEMOID ohne Bindestrich>_<RUN_TOKEN>
```

Beispiel: Die Demo zu indexfreundlichen Suchbedingungen (`QRY-001`) mit
`run_token: LOCAL` ergibt `SQLPERF_LAB_QRY001_LOCAL`. Der Run Token ist die
synthetische Laufkennung aus dem Manifest.

Das Präfix `SQLPERF_LAB_` ist das Schutzschema des Frameworks. Die Demo-Verträge verpflichten Setup und Cleanup darauf, ausschließlich Datenbanken mit diesem Präfix anzulegen und zu entfernen. Ein Runtime-Nachweis dieses Schutzschemas ist als `FWK-002` (Namens-, Schutz- und Lifecycle-Vertrag für Testdatenbanken) noch offen; die Zielinstanz muss deshalb ohnehin eine Wegwerfinstanz sein.

Vorhandene Reste lassen sich so prüfen:

```sql
SELECT name FROM sys.databases WHERE name LIKE N'SQLPERF[_]LAB[_]%';
```

Vor einem Lauf sollte diese Abfrage keine Zeile liefern.

## 6. Ausführung der Demo-Preflights

Der Preflight ist die erste Phase jedes Demolaufs. Er prüft Demo-ID und Sicherheitsstufe, den Versionsbereich, die Engine Edition, den Zustand der Zieldatenbank, die Berechtigungen und die Sicherheitsbestätigungen. Sein Ergebnis entscheidet, ob die Demo überhaupt startet.

Der Preflight lässt sich getrennt ausführen, um eine Instanz zu bewerten, ohne eine Datenbank anzulegen. Dazu werden dieselben Variablen gesetzt, die das Harness übergibt:

```bash
sqlcmd -S <instanz> -U <anmeldename> -d master -b \
  -v DemoId="QRY-001" \
  -v RunToken="LOCAL" \
  -v TargetDatabase="SQLPERF_LAB_QRY001_LOCAL" \
  -v SafetyLevel="GREEN" \
  -v ConfirmIsolatedLab="0" \
  -v HighImpactConfirmed="0" \
  -v DisposableEnvironmentConfirmed="0" \
  -v RecoveryPlanConfirmed="0" \
  -v MaximumRuntimeSeconds="240" \
  -i Demos/05_Query_Patterns/QRY-001_SARGability/00_Preflight.sql
```

Die Ausgabe endet mit einer strukturierten Summary. Die wichtigsten Codes:

| Code | Bedeutung | Reaktion |
|---|---|---|
| `OK` | Alle Bedingungen erfüllt | Demo kann laufen |
| `SKIP_VERSION` | Instanzversion liegt außerhalb des Bereichs der Demo | andere Instanz wählen |
| `SKIP_PLATFORM` | Engine Edition wird nicht unterstützt | andere Instanz wählen |
| `SKIP_COMPATIBILITY_LEVEL` | Compatibility Level der Zieldatenbank passt nicht | Zieldatenbank prüfen |
| `SKIP_PERMISSION` | Eine benötigte Berechtigung fehlt | Berechtigung ergänzen |
| `FAIL_SAFETY` | Bestätigung für eine gelbe oder rote Demo fehlt | Lauf mit den passenden Bestätigungen wiederholen |
| `FAIL_CONTRACT` | Manifest- oder Vertragsverletzung | Demo prüfen, nicht die Instanz |

Für eine gelbe Demo werden `ConfirmIsolatedLab`, `HighImpactConfirmed` und ein positives `MaximumRuntimeSeconds` benötigt. Eine rote Demo verlangt zusätzlich `DisposableEnvironmentConfirmed` und `RecoveryPlanConfirmed`.

## 7. Vollständiger Demolauf

Ein einzelner Lauf über das Harness:

```bash
python Demos/00_Framework/Tools/run_demo.py \
  Demos/05_Query_Patterns/QRY-001_SARGability/manifest.json \
  --server <instanz> \
  --auth sql \
  --username <anmeldename>
```

Für eine gelbe Demo wird `--confirm-isolated-lab` ergänzt, für eine rote zusätzlich `--allow-red`. `--show-output` zeigt die rohe sqlcmd-Ausgabe.

Trägt die Instanz ein selbstsigniertes Zertifikat, wird das Shim für vorhandene Instanzen zwischengeschaltet, weil das Harness selbst kein `-C` setzt:

```bash
export SQLPERF_HOST_TRUST_SERVER_CERTIFICATE=1
python Demos/00_Framework/Tools/run_demo.py \
  Demos/05_Query_Patterns/QRY-001_SARGability/manifest.json \
  --server <instanz> \
  --auth sql \
  --username <anmeldename> \
  --sqlcmd Tests/Runtime/host_sqlcmd_target.py
```

Mehrere Demos nacheinander einschließlich Cleanup-Prüfung führt der Gate-B-Runner aus:

```bash
python Tests/Runtime/run_gate_b_pilots.py \
  --target host \
  --server <instanz> \
  --username <anmeldename> \
  --confirm-disposable-instance
```

Die Bestätigung ist verbindlich, weil der Lauf Datenbanken anlegt und wieder löscht (DEC-051).

## 8. Stop, Reset, Cleanup und Recovery

Das Harness führt das Cleanup selbst aus, sobald das Setup begonnen hat, auch wenn eine spätere Phase fehlschlägt. Scheitert das Cleanup, endet der Lauf mit `FAIL_CLEANUP`.

Nach jedem Lauf wird geprüft, ob die Testdatenbank tatsächlich entfernt wurde:

```sql
SELECT name FROM sys.databases WHERE name LIKE N'SQLPERF[_]LAB[_]%';
```

Bleibt eine Datenbank zurück, erhalten Sie sie und starten keinen weiteren
Demolauf gegen diese Instanz. Der [zentrale Wiederherstellungsweg](DEMO_EXECUTION_GUIDE.md#6-cleanup-prüfen-und-nach-abbruch-wiederherstellen)
erläutert die aktuelle Grenze der Eigentumsprüfung. Ein Namenspräfix reicht
für eine Löschentscheidung nicht aus. Verwenden Sie weder manuelles
`DROP DATABASE` anhand des Namens noch einen ungeprüften eigenständigen
Cleanupaufruf.

Recovery bedeutet hier die Wiederherstellung eines geklärten Ausgangszustands.
Solange der korrigierte Eigentumsnachweis fehlt, bleiben die bisherige Instanz
und ihr Szenariozustand erhalten. Stoppen Sie an dieser Stelle; ein unabhängig
abgegrenzter Wiederanlauf mit getrenntem Steuerungszustand ist hier noch nicht
beschrieben. Übernehmen Sie keine Reset- oder Remove-Schritte anderer Anleitungen.
Die bisherige Empfehlung, alle Datenbanken mit Schulungspräfix zu entfernen,
entfällt. Es gibt keinen pauschalen Auftrag zum Zurücksetzen einer vorhandenen
Instanz oder zum Beenden fremder Sitzungen.

## 9. Unterschiede zwischen SQL Server 2019, 2022 und 2025

| Aspekt | 2019 (15.x) | 2022 (16.x) | 2025 (17.x) |
|---|---|---|---|
| Compatibility Level der Demos | 150 | 160 | 170 |
| Berechtigung für Laufzeitzustände | `VIEW SERVER STATE` | `VIEW SERVER PERFORMANCE STATE` | `VIEW SERVER PERFORMANCE STATE` |

Der gemeinsame Preflight des Frameworks berücksichtigt diese Unterscheidung: Unterhalb von Major 16 wird die ab SQL Server 2022 vorgesehene Berechtigungsbezeichnung mit `SKIP_VERSION` übergangen.

Compatibility Level und Engine-Version sind zu trennen. Eine Datenbank auf SQL Server 2025 mit Compatibility Level 150 zeigt ein anderes Optimierungsverhalten als dieselbe Datenbank mit 170. Die Setup-Skripte der Demos setzen das Compatibility Level daher ausdrücklich.

Eine Demo, deren Versionsbereich die vorhandene Instanz nicht einschließt, endet im Preflight mit `SKIP_VERSION`. Das ist kein Fehler, sondern der vorgesehene Ausgang.

## 10. Demos mit zusätzlichem Infrastrukturbedarf

Die aktuelle Zuordnung von Demo, Sicherheitsstufe, Sitzungszahl und
**Zusatzbedarf** steht im [Demo-Katalog](../Demo_Catalog/README.md#ausführungspfad-der-implementierten-demos).
Prüfen Sie dort die Zeile Ihrer gewählten Demo und anschließend ihre README.
Eine zweite, verkürzte Liste in dieser Anleitung würde bei neuen Demos schnell
veraltet sein.

Die Demo für Blockierungsketten (`CON-004`) benötigt mehrere gleichzeitige
Sitzungen. Die Demo zur ungleich verteilten parallelen Arbeit (`OPT-017`)
benötigt ein Container-Ressourcenprofil. Weitere Mehrsitzungs- und
Ressourcenanforderungen ergeben sich aus dem Katalog und dem jeweiligen
Manifest; planen Sie die Instanz anhand dieser Angaben.

## 11. Grenzen dieses How-tos

- Der Docker-/Podman-Arbeitsplatzpfad ist bewusst in `Documentation/HowTo/CONTAINER_QUICKSTART.md` getrennt. `INF-002` und `INF-003` sind damit für den validierten SQL-Server-2025-Vertical-Slice abgeschlossen.
- Hyper-V- und Mehrinstanzpfade sind zurückgestellt.
- Die Framework-Matrix `Tests/Runtime/run_framework_sql_matrix.py` läuft ausschließlich containerisiert, weil sie Query Store und Extended Events auf Serverebene schaltet (DEC-050).
- Die hier beschriebenen Kommandos sind gegen die Verträge des Repositories geprüft. Ein vollständiger Laufnachweis gegen eine vorhandene Instanz steht noch aus und wird in `Documentation/Project_Planning/INF_001_EXECUTION_TARGET_DESIGN.md` als offene Folgearbeit geführt.
