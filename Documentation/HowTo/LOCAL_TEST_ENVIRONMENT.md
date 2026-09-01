# Lokale Testumgebung für Schulungsdemos

Arbeitspaket `INF-001` aus Welle 10. Grundlage: `Documentation/Project_Planning/MASTER_IMPLEMENTATION_PLAN.md` Abschnitt 13 und `Documentation/Project_Planning/INF_001_EXECUTION_TARGET_DESIGN.md`.

Dieses How-to beschreibt, wie eine Schulungsdemo auf einer **vorhandenen SQL-Server-Instanz** ausgeführt wird. Alle Beispiele verwenden neutrale Platzhalter in spitzen Klammern.

## 1. Auswahl des Ausführungspfads

Abschnitt 13.2 des Masterplans legt eine Stufenleiter fest. Es gilt immer die kleinste ausreichende Stufe.

| Stufe | Pfad | Verwendung | Stand |
|---:|---|---|---|
| 1 | vorhandene Testinstanz plus eigene synthetische Testdatenbank | Standard, wenn ein geeigneter SQL Server verfügbar ist | in diesem How-to beschrieben |
| 2 | reine T-SQL-Steuerung innerhalb der isolierten Testinstanz | bevorzugt für Pläne, Statistiken, Indizes, Blocking, Deadlocks, Query Store und Extended Events | in diesem How-to beschrieben |
| 3 | containerisierte Einzelinstanz | wenn kein SQL Server vorhanden ist oder reproduzierbare CPU-/RAM-Grenzen benötigt werden | als `INF-002` (Docker) und `INF-003` (Podman) in `CONTAINER_QUICKSTART.md` beschrieben und für den SQL-Server-2025-Lifecycle praktisch validiert |
| 4 | Hyper-V-VM | Windows-, OS-, Storage- oder Isolationsanforderungen | zurückgestellt (`INF-004`, DEC-049) |
| 5 | Mehrinstanz- oder Netzwerktopologie | verteilte oder netzwerkabhängige Kernaussage | zurückgestellt (`INF-006`, DEC-049) |

Entscheidungshilfe:

- Steht eine SQL-Server-Instanz zur Verfügung, die **verworfen oder zurückgesetzt werden darf**, ist Stufe 1 der richtige Weg. Die sechs runtimevalidierten Demos sind so aufgebaut, dass sie auf einer solchen Instanz laufen; ihre bisherige Validierung erfolgte containerisiert.
- Steht keine Instanz zur Verfügung, führt `Documentation/HowTo/CONTAINER_QUICKSTART.md` über den geprüften Docker- oder Podman-Arbeitsplatzpfad. Der vollständige interaktive Lifecycle ist für `CON-004` auf SQL Server 2025 validiert.
- Hyper-V und Mehrinstanztopologien sind ausdrücklich zurückgestellt, bis der externe Runner `Key18_Perf` bereitsteht. Die Anforderungen sind in `Documentation/Architecture/RUNNER_TOPOLOGY.md` beschrieben.

Läufe gegen eine vorhandene Instanz sind Entwicklungs- und Fehlersuchevidenz. Sie ersetzen keine Gate-Evidenz; diese entsteht ausschließlich auf GitHub-gehosteten Runnern über die Versionsmatrix 2019, 2022 und 2025 (DEC-047).

## 2. Mindestvoraussetzungen

| Voraussetzung | Anforderung |
|---|---|
| SQL Server | 2019, 2022 oder 2025; Engine Edition 2, 3 oder 4 (Standard, Enterprise oder Express) |
| Instanzcharakter | Wegwerf- oder Testinstanz. Der Lauf legt Datenbanken an und löscht sie wieder. |
| Berechtigungen | `CREATE DATABASE`, `ALTER DATABASE`, `SHOWPLAN`, `VIEW SERVER STATE`, ab SQL Server 2022 zusätzlich `VIEW SERVER PERFORMANCE STATE` |
| Client | `sqlcmd` im Suchpfad |
| Python | 3.12 oder neuer, ausschließlich Standardbibliothek |

Ressourcenbelegung: Die Testdatenbanken sind synthetisch und werden je Lauf neu erzeugt. Ihre Größe ergibt sich aus dem Setup-Skript der jeweiligen Demo. Das Zeitbudget steht im Manifest; `QRY-001` verwendet beispielsweise `timeout_seconds: 240` mit `cleanup_timeout_seconds: 60`. Eine gemessene Angabe zu Speicher- und CPU-Bedarf je Demo liegt derzeit nicht vor und wird hier bewusst nicht geschätzt.

`OPT-013` erzeugt gezielt einen Sort-Spill und belastet dabei `tempdb`. `CON-004` hält Blockierungen über mehrere Sitzungen. Beide sind als `YELLOW` eingestuft und verlangen eine isolierte Instanz.

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

Beispiel: `QRY-001` mit `run_token: LOCAL` ergibt `SQLPERF_LAB_QRY001_LOCAL`. Der Run Token steht im Manifest der Demo und ist synthetisch.

Das Präfix `SQLPERF_LAB_` ist das Schutzschema des Frameworks. Die Demo-Verträge verpflichten Setup und Cleanup darauf, ausschließlich Datenbanken mit diesem Präfix anzulegen und zu entfernen. Ein Runtime-Nachweis dieses Schutzschemas ist als `FWK-002` noch offen; die Zielinstanz muss deshalb ohnehin eine Wegwerfinstanz sein.

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

Bleibt eine Datenbank zurück, etwa nach einem Abbruch oder einem Zeitüberschreitungsfehler, wird sie gezielt entfernt. Der Name ist vorher zu prüfen; die Anweisung trennt bestehende Verbindungen:

```sql
ALTER DATABASE [SQLPERF_LAB_QRY001_LOCAL] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
DROP DATABASE [SQLPERF_LAB_QRY001_LOCAL];
```

Diese Anweisung wird ausschließlich auf Datenbanken mit dem Präfix `SQLPERF_LAB_` angewendet.

Blockiert eine hängende Sitzung das Löschen, hilft die Zuordnung über `sys.dm_exec_sessions` und `sys.dm_tran_locks`. `CON-004` erzeugt bewusst Blockierungen; ein abgebrochener Lauf dieser Demo kann Sitzungen hinterlassen.

Recovery ohne Datenverlustrisiko: Da alle Daten synthetisch sind und je Lauf neu erzeugt werden, ist das vollständige Entfernen aller `SQLPERF_LAB_`-Datenbanken der Rücksetzpunkt. Eine Sicherung dieser Datenbanken ist weder vorgesehen noch nötig.

Ein Reset der Instanz selbst ist nur nötig, wenn eine Demo Servereinstellungen verändert hat. Die derzeit runtimevalidierten Demos tun das nicht; Query Store und Extended Events werden nur im containerisierten Framework-Matrixlauf auf Serverebene geschaltet.

## 9. Unterschiede zwischen SQL Server 2019, 2022 und 2025

| Aspekt | 2019 (15.x) | 2022 (16.x) | 2025 (17.x) |
|---|---|---|---|
| Compatibility Level der Demos | 150 | 160 | 170 |
| Berechtigung für Laufzeitzustände | `VIEW SERVER STATE` | `VIEW SERVER PERFORMANCE STATE` | `VIEW SERVER PERFORMANCE STATE` |

Der gemeinsame Preflight des Frameworks berücksichtigt diese Unterscheidung: Unterhalb von Major 16 wird die ab SQL Server 2022 vorgesehene Berechtigungsbezeichnung mit `SKIP_VERSION` übergangen.

Compatibility Level und Engine-Version sind zu trennen. Eine Datenbank auf SQL Server 2025 mit Compatibility Level 150 zeigt ein anderes Optimierungsverhalten als dieselbe Datenbank mit 170. Die Setup-Skripte der Demos setzen das Compatibility Level daher ausdrücklich.

Eine Demo, deren Versionsbereich die vorhandene Instanz nicht einschließt, endet im Preflight mit `SKIP_VERSION`. Das ist kein Fehler, sondern der vorgesehene Ausgang.

## 10. Demos mit zusätzlichem Infrastrukturbedarf

Stand der runtimevalidierten Demos:

| Demo-ID | Sicherheitsstufe | Sitzungen | Zusatzbedarf |
|---|---|---:|---|
| `QRY-001` | `GREEN` | 1 | keiner |
| `OPT-002` | `GREEN` | 1 | keiner |
| `OPT-015` | `GREEN` | 1 | Planeigenschaften aus `sys.dm_exec_query_plan_stats` |
| `OPT-016` | `GREEN` | 1 | Planeigenschaften aus `sys.dm_exec_query_plan_stats` |
| `OPT-013` | `YELLOW` | 1 | isolierte Instanz; belastet `tempdb` |
| `CON-004` | `YELLOW` | 4 | isolierte Instanz; Mehrsitzungsorchestrierung über `orchestrate_sessions.py` |

`CON-004` ist die einzige Demo mit Mehrsitzungsorchestrierung. Sie startet vier Sitzungen über ein eigenes Sitzungsmanifest und benötigt deshalb ein `sqlcmd`, das mehrfach parallel gestartet werden kann.

Demos, die CPU-/RAM-Limits, gedrosseltes I/O, Netzwerkbedingungen, mehrere Instanzen oder Windows-nahe Messung benötigen, sind derzeit nicht umgesetzt. Sie gehören zu den zurückgestellten Bündeln `INF-004` bis `INF-006`.

## 11. Grenzen dieses How-tos

- Der Docker-/Podman-Arbeitsplatzpfad ist bewusst in `Documentation/HowTo/CONTAINER_QUICKSTART.md` getrennt. `INF-002` und `INF-003` sind damit für den validierten SQL-Server-2025-Vertical-Slice abgeschlossen.
- Hyper-V- und Mehrinstanzpfade sind zurückgestellt.
- Die Framework-Matrix `Tests/Runtime/run_framework_sql_matrix.py` läuft ausschließlich containerisiert, weil sie Query Store und Extended Events auf Serverebene schaltet (DEC-050).
- Die hier beschriebenen Kommandos sind gegen die Verträge des Repositories geprüft. Ein vollständiger Laufnachweis gegen eine vorhandene Instanz steht noch aus und wird in `Documentation/Project_Planning/INF_001_EXECUTION_TARGET_DESIGN.md` als offene Folgearbeit geführt.
