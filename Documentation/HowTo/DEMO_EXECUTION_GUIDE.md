# Ausführungsleitfaden für alle freigegebenen Demos

| Merkmal | Wert |
|---|---|
| Geltungsbereich | alle 22 runtimevalidierten Fachdemos mit `manifest.json` |
| Ausführung | PowerShell auf einer dedizierten Test- oder Wegwerfinstanz |
| Ergebnis | strukturierte `SQLPERF_SUMMARY` je Phase und markergeprüftes Cleanup |
| Ergänzende Erklärung | [`DEMO_WALKTHROUGHS.md`](DEMO_WALKTHROUGHS.md) |

Dieser Leitfaden ist der verbindliche Ausführungspfad für die freigegebenen Demos. Er beschreibt nicht nur deren Inhalt, sondern die Schritte, mit denen eine Person ohne Kenntnis der ursprünglichen Entwicklungsumgebung einen Lauf starten, das Ergebnis einordnen und einen abgebrochenen Lauf bereinigen kann. Die jeweilige Demo-README erklärt Lernziel, Datenmodell, Evidenz und fachliche Grenzen.

Die Demos erzeugen und entfernen eigene synthetische Testdatenbanken. Auch eine grüne Demo gehört deshalb nicht auf eine produktive Instanz. Gelbe und rote Demos dürfen ausschließlich auf einer Instanz ausgeführt werden, die verworfen oder kontrolliert zurückgesetzt werden darf.

## 1. Demo auswählen

Wählen Sie eine Demo aus der folgenden Tabelle. Der angegebene Schlüssel wird in Schritt 5 unverändert als `-DemoId` verwendet. Die Links führen zur fachlichen Beschreibung; der Pfad ist das tatsächlich vom Harness gelesene Manifest.

| Demo | Sicherheitsstufe | Unterstützte Engine / Compatibility Level | Besonderheit |
|---|---|---|---|
| [`OPT-002`](../../Demos/04_Optimizer_Statistics_Plans/OPT-002_Statistics_Anatomy/README.md) | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`OPT-003`](../../Demos/04_Optimizer_Statistics_Plans/OPT-003_Sampling_Skew/README.md) | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`OPT-005`](../../Demos/04_Optimizer_Statistics_Plans/OPT-005_Ascending_Key/README.md) | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`OPT-009`](../../Demos/04_Optimizer_Statistics_Plans/OPT-009_Parameter_Sensitive_Plans/README.md) | `GREEN` | 2022/160, 2025/170 | 2019 ergibt vorgesehenes `SKIP_VERSION` |
| [`OPT-010`](../../Demos/04_Optimizer_Statistics_Plans/OPT-010_Optional_Parameter_Plans/README.md) | `GREEN` | 2025/170 | 2019 und 2022 ergeben vorgesehenes `SKIP_VERSION` |
| [`OPT-013`](../../Demos/04_Optimizer_Statistics_Plans/OPT-013_Controlled_Spill/README.md) | `YELLOW` | 2019/150, 2022/160, 2025/170 | belastet `tempdb` |
| [`OPT-015`](../../Demos/04_Optimizer_Statistics_Plans/OPT-015_Plan_Properties/README.md) | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`OPT-016`](../../Demos/04_Optimizer_Statistics_Plans/OPT-016_Rebind_Rewind_Spools/README.md) | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`OPT-017`](../../Demos/04_Optimizer_Statistics_Plans/OPT-017_Parallelism_Skew/README.md) | `YELLOW` | 2019/150, 2022/160, 2025/170 | Container oder Wegwerfinstanz mit mindestens vier sichtbaren CPUs |
| [`QRY-001`](../../Demos/05_Query_Patterns/QRY-001_SARGability/README.md) | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`QRY-004`](../../Demos/05_Query_Patterns/QRY-004_Classic_And_Dynamic/README.md) | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`QRY-013`](../../Demos/05_Query_Patterns/QRY-013_Client_Session_Context/README.md) | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`IDX-006`](../../Demos/04_Rowstore_Columnstore/IDX-006_Page_Splits_Density/README.md) | `YELLOW` | 2019/150, 2022/160, 2025/170 | isolierte Instanz |
| [`IDX-010`](../../Demos/04_Rowstore_Columnstore/IDX-010_Columnstore_Segments/README.md) | `YELLOW` | 2019/150, 2022/160, 2025/170 | Container oder Wegwerfinstanz mit Ressourcenprofil |
| [`CON-004`](../../Demos/07_Concurrency/CON-004_Blocking_Chain/README.md) | `YELLOW` | 2019/150, 2022/160, 2025/170 | Mehrsitzungsorchestrierung; alternativ interaktiv gemäß [`INTERACTIVE_SCENARIO_LIFECYCLE.md`](INTERACTIVE_SCENARIO_LIFECYCLE.md) |
| [`CON-006`](../../Demos/07_Concurrency/CON-006_Deadlock_Cycle/README.md) | `YELLOW` | 2019/150, 2022/160, 2025/170 | Mehrsitzungsorchestrierung |
| [`CON-009`](../../Demos/05_Concurrency_Isolation_TempDB/CON-009_TempDB_Cost_Classes/README.md) | `YELLOW` | 2019/150, 2022/160, 2025/170 | isolierte Instanz |
| [`DGN-003`](../../Demos/07_Query_Store_Extended_Events/DGN-003_Query_Store_History/README.md) | `GREEN` | 2019/150, 2022/160, 2025/170 | Query Store nur in der Testdatenbank |
| [`DGN-005`](../../Demos/07_Query_Store_Extended_Events/DGN-005_Bounded_Extended_Events/README.md) | `YELLOW` | 2019/150, 2022/160, 2025/170 | begrenzte Extended-Events-Evidenz |
| [`STL-008`](../../Demos/01_Storage_Pages_Log/STL-008_VLF_Log_Growth/README.md) | `RED` | 2019/150, 2022/160, 2025/170 | nur Wegwerf-Containerinstanz; Recovery muss vor Start bestätigt sein |
| [`STL-009`](../../Demos/01_Storage_Pages_Log/STL-009_Commit_Batching/README.md) | `YELLOW` | 2019/150, 2022/160, 2025/170 | isolierte Instanz |
| [`RES-007`](../../Demos/06_CPU_Memory_IO_Waits/RES-007_Wait_Scope_Deltas/README.md) | `YELLOW` | 2019/150, 2022/160, 2025/170 | Mehrsitzungsorchestrierung und Server-State-Berechtigung |

## 2. Arbeitsplatz und Instanz vorbereiten

1. Klonen Sie das Repository und öffnen Sie PowerShell im Repository-Stamm.
2. Installieren Sie Python 3.12 oder höher und Microsoft `sqlcmd`; beide Befehle müssen im Suchpfad liegen.
3. Stellen Sie eine SQL-Server-2019-, -2022- oder -2025-Instanz bereit. Verwenden Sie für gelbe und rote Demos eine Wegwerfinstanz. Für `OPT-017`, `IDX-010` und `STL-008` ist der Containerpfad erforderlich oder empfohlen; die Bereitstellung ist in [`CONTAINER_QUICKSTART.md`](CONTAINER_QUICKSTART.md) beschrieben.
4. Verwenden Sie ein Login mit `CREATE DATABASE`, `ALTER DATABASE`, `SHOWPLAN` sowie `VIEW SERVER STATE` (SQL Server 2019) oder `VIEW SERVER PERFORMANCE STATE` (SQL Server 2022/2025).
5. Prüfen Sie die Tools und die Verbindung. Ersetzen Sie `<instanz>` durch den Server- und gegebenenfalls Instanznamen.

```powershell
python --version
sqlcmd -?
sqlcmd -S '<instanz>' -E -Q 'SELECT SERVERPROPERTY(''ProductMajorVersion'') AS MajorVersion;'
```

Für SQL-Authentifizierung ersetzt `-U '<anmeldename>'` das `-E`. Wenn `sqlcmd` wegen eines selbstsignierten Zertifikats ablehnt, ergänzen Sie ausschließlich für die Wegwerfinstanz `-C`; der Harness erhält die entsprechende explizite Einstellung in Schritt 4.

## 3. Zugangsdaten und Verbindungsparameter setzen

Für Windows-Authentifizierung sind keine Zugangsdaten in einer Umgebungsvariable nötig. Führen Sie die folgenden Zeilen aus und ersetzen Sie nur `<instanz>`:

```powershell
$server = '<instanz>'
$authentication = 'integrated'
$username = $null
```

Für SQL-Authentifizierung wird das Kennwort weder in einer Datei noch in der Befehlszeile gespeichert:

```powershell
$server = '<instanz>'
$authentication = 'sql'
$username = '<anmeldename>'
$credentialInput = Read-Host -AsSecureString 'Kennwort'
$env:SQLCMDPASSWORD = [System.Net.NetworkCredential]::new('', $credentialInput).Password
```

## 4. Einmalig den Demo-Aufrufer laden

Kopieren Sie den folgenden Block vollständig in dieselbe PowerShell-Sitzung. Er ordnet jeder freigegebenen Demo exakt ihr versioniertes Manifest und ihre Sicherheitsstufe zu. Der Aufrufer übergibt die Sicherheitsbestätigungen nur für die dazugehörigen Demos und zeigt die Ausgaben der Phasen an.

```powershell
$demoCatalog = @{
    'OPT-002' = @{ Manifest = 'Demos/04_Optimizer_Statistics_Plans/OPT-002_Statistics_Anatomy/manifest.json'; Safety = 'GREEN' }
    'OPT-003' = @{ Manifest = 'Demos/04_Optimizer_Statistics_Plans/OPT-003_Sampling_Skew/manifest.json'; Safety = 'GREEN' }
    'OPT-005' = @{ Manifest = 'Demos/04_Optimizer_Statistics_Plans/OPT-005_Ascending_Key/manifest.json'; Safety = 'GREEN' }
    'OPT-009' = @{ Manifest = 'Demos/04_Optimizer_Statistics_Plans/OPT-009_Parameter_Sensitive_Plans/manifest.json'; Safety = 'GREEN' }
    'OPT-010' = @{ Manifest = 'Demos/04_Optimizer_Statistics_Plans/OPT-010_Optional_Parameter_Plans/manifest.json'; Safety = 'GREEN' }
    'OPT-013' = @{ Manifest = 'Demos/04_Optimizer_Statistics_Plans/OPT-013_Controlled_Spill/manifest.json'; Safety = 'YELLOW' }
    'OPT-015' = @{ Manifest = 'Demos/04_Optimizer_Statistics_Plans/OPT-015_Plan_Properties/manifest.json'; Safety = 'GREEN' }
    'OPT-016' = @{ Manifest = 'Demos/04_Optimizer_Statistics_Plans/OPT-016_Rebind_Rewind_Spools/manifest.json'; Safety = 'GREEN' }
    'OPT-017' = @{ Manifest = 'Demos/04_Optimizer_Statistics_Plans/OPT-017_Parallelism_Skew/manifest.json'; Safety = 'YELLOW' }
    'QRY-001' = @{ Manifest = 'Demos/05_Query_Patterns/QRY-001_SARGability/manifest.json'; Safety = 'GREEN' }
    'QRY-004' = @{ Manifest = 'Demos/05_Query_Patterns/QRY-004_Classic_And_Dynamic/manifest.json'; Safety = 'GREEN' }
    'QRY-013' = @{ Manifest = 'Demos/05_Query_Patterns/QRY-013_Client_Session_Context/manifest.json'; Safety = 'GREEN' }
    'IDX-006' = @{ Manifest = 'Demos/04_Rowstore_Columnstore/IDX-006_Page_Splits_Density/manifest.json'; Safety = 'YELLOW' }
    'IDX-010' = @{ Manifest = 'Demos/04_Rowstore_Columnstore/IDX-010_Columnstore_Segments/manifest.json'; Safety = 'YELLOW' }
    'CON-004' = @{ Manifest = 'Demos/07_Concurrency/CON-004_Blocking_Chain/manifest.json'; Safety = 'YELLOW' }
    'CON-006' = @{ Manifest = 'Demos/07_Concurrency/CON-006_Deadlock_Cycle/manifest.json'; Safety = 'YELLOW' }
    'CON-009' = @{ Manifest = 'Demos/05_Concurrency_Isolation_TempDB/CON-009_TempDB_Cost_Classes/manifest.json'; Safety = 'YELLOW' }
    'DGN-003' = @{ Manifest = 'Demos/07_Query_Store_Extended_Events/DGN-003_Query_Store_History/manifest.json'; Safety = 'GREEN' }
    'DGN-005' = @{ Manifest = 'Demos/07_Query_Store_Extended_Events/DGN-005_Bounded_Extended_Events/manifest.json'; Safety = 'YELLOW' }
    'STL-008' = @{ Manifest = 'Demos/01_Storage_Pages_Log/STL-008_VLF_Log_Growth/manifest.json'; Safety = 'RED' }
    'STL-009' = @{ Manifest = 'Demos/01_Storage_Pages_Log/STL-009_Commit_Batching/manifest.json'; Safety = 'YELLOW' }
    'RES-007' = @{ Manifest = 'Demos/06_CPU_Memory_IO_Waits/RES-007_Wait_Scope_Deltas/manifest.json'; Safety = 'YELLOW' }
}

function Invoke-SqlPerfDemo {
    param(
        [Parameter(Mandatory)][ValidateSet('OPT-002','OPT-003','OPT-005','OPT-009','OPT-010','OPT-013','OPT-015','OPT-016','OPT-017','QRY-001','QRY-004','QRY-013','IDX-006','IDX-010','CON-004','CON-006','CON-009','DGN-003','DGN-005','STL-008','STL-009','RES-007')][string]$DemoId,
        [Parameter(Mandatory)][string]$Server,
        [ValidateSet('integrated','sql')][string]$Authentication = 'integrated',
        [string]$Username,
        [switch]$ConfirmIsolatedLab,
        [switch]$AllowRed,
        [switch]$TrustServerCertificate
    )

    $entry = $demoCatalog[$DemoId]
    if ($Authentication -eq 'sql' -and [string]::IsNullOrWhiteSpace($Username)) {
        throw 'Für SQL-Authentifizierung ist -Username erforderlich; das Kennwort kommt nur aus SQLCMDPASSWORD.'
    }
    if ($entry.Safety -eq 'YELLOW' -and -not $ConfirmIsolatedLab) {
        throw 'Diese gelbe Demo benötigt eine bestätigte isolierte Instanz: -ConfirmIsolatedLab.'
    }
    if ($entry.Safety -eq 'RED' -and -not $AllowRed) {
        throw 'Diese rote Demo benötigt eine Wegwerf-Containerinstanz und -AllowRed.'
    }
    if ($TrustServerCertificate) {
        $env:SQLPERF_HOST_TRUST_SERVER_CERTIFICATE = '1'
    }

    $arguments = @('Demos/00_Framework/Tools/run_demo.py', $entry.Manifest, '--server', $Server, '--auth', $Authentication, '--show-output')
    if ($Authentication -eq 'sql') { $arguments += @('--username', $Username) }
    if ($entry.Safety -eq 'YELLOW') { $arguments += '--confirm-isolated-lab' }
    if ($entry.Safety -eq 'RED') { $arguments += '--allow-red' }
    & python @arguments
}
```

## 5. Demo ausführen und beobachten

1. Starten Sie genau eine ausgewählte Demo. Beispiel für die grüne Einsteiger-Demo `QRY-001` mit Windows-Authentifizierung:

```powershell
Invoke-SqlPerfDemo -DemoId QRY-001 -Server $server -Authentication $authentication
```

2. Für eine gelbe Demo bestätigen Sie vorher, dass die Instanz isoliert ist. Dieses Beispiel startet die Mehrsitzungsdemo `CON-004`:

```powershell
Invoke-SqlPerfDemo -DemoId CON-004 -Server $server -Authentication $authentication -Username $username -ConfirmIsolatedLab
```

3. Führen Sie `STL-008` nur auf einer Wegwerf-Containerinstanz aus, nachdem Sie den Resetpfad geprüft haben. Die explizite Bestätigung aktiviert die rote Demo:

```powershell
Invoke-SqlPerfDemo -DemoId STL-008 -Server $server -Authentication $authentication -Username $username -AllowRed
```

4. Bei einem selbstsignierten Zertifikat ergänzen Sie beim jeweiligen Aufruf `-TrustServerCertificate`. Diese Einstellung ist ausschließlich für die bereits bestätigte Wegwerfinstanz zulässig.

Das Harness führt die Phasen des jeweiligen `manifest.json` in der festgelegten Reihenfolge aus: `PREFLIGHT`, `SETUP`, `BASELINE`, `DEMONSTRATION`, `OBSERVATION`, `MITIGATION`, `COMPARISON` und `CLEANUP`. Mehrsitzungsdemos führen an Stelle der Demonstration ein Sitzungsmanifest aus; die fachliche Reihenfolge wird dabei über Datenbanksignale gesteuert.

Ein erfolgreicher Lauf endet mit `SQLPERF_SUMMARY|PASS|OK`. Ein `SKIP_VERSION` bei den in Schritt 1 genannten nicht unterstützten Versionen ist erwartetes Verhalten und erzeugt keinen Datenbankaufbau. `WARN` bedeutet, dass optionale Evidenz eingeschränkt war; lesen Sie in diesem Fall die betreffende Demo-README. Bei `FAIL` ist die angegebene Phase die Ausgangsbasis für die Diagnose. Ein `FAIL_CLEANUP` hat Vorrang und muss vor einem weiteren Lauf behoben werden.

## 6. Cleanup prüfen und nach Abbruch wiederherstellen

Das Harness startet nach begonnenem Setup immer `CLEANUP`. Prüfen Sie dennoch nach jedem Lauf, dass keine Schulungsdatenbank zurückblieb:

```powershell
sqlcmd -S $server -E -d master -Q "SELECT name FROM sys.databases WHERE name LIKE N'SQLPERF[_]LAB[_]%';"
```

Für SQL-Authentifizierung verwenden Sie stattdessen `-U $username`; das Kennwort bleibt in `SQLCMDPASSWORD`.

Wenn PowerShell, `sqlcmd` oder der Rechner während eines Laufs beendet wurde, führen Sie **nur** das Cleanup der abgebrochenen Demo aus. Es entfernt eine Datenbank ausschließlich bei vollständiger Übereinstimmung der vier Eigentumsmarker. Führen Sie nie ein manuelles `DROP DATABASE` anhand eines Namensmusters aus.

```powershell
function Invoke-AbortedSqlPerfDemoCleanup {
    param(
        [Parameter(Mandatory)][ValidateSet('OPT-002','OPT-003','OPT-005','OPT-009','OPT-010','OPT-013','OPT-015','OPT-016','OPT-017','QRY-001','QRY-004','QRY-013','IDX-006','IDX-010','CON-004','CON-006','CON-009','DGN-003','DGN-005','STL-008','STL-009','RES-007')][string]$DemoId,
        [Parameter(Mandatory)][string]$Server,
        [ValidateSet('integrated','sql')][string]$Authentication = 'integrated',
        [string]$Username
    )

    $entry = $demoCatalog[$DemoId]
    $demoFolder = Split-Path $entry.Manifest -Parent
    $targetDatabase = "SQLPERF_LAB_$($DemoId.Replace('-', ''))_LOCAL"
    $connection = if ($Authentication -eq 'integrated') { @('-E') } else { @('-U', $Username) }
    $safetyValues = if ($entry.Safety -eq 'RED') { @('SafetyLevel=RED','ConfirmIsolatedLab=0','HighImpactConfirmed=1','DisposableEnvironmentConfirmed=1','RecoveryPlanConfirmed=1') } elseif ($entry.Safety -eq 'YELLOW') { @('SafetyLevel=YELLOW','ConfirmIsolatedLab=1','HighImpactConfirmed=1','DisposableEnvironmentConfirmed=0','RecoveryPlanConfirmed=0') } else { @('SafetyLevel=GREEN','ConfirmIsolatedLab=0','HighImpactConfirmed=0','DisposableEnvironmentConfirmed=0','RecoveryPlanConfirmed=0') }
    & sqlcmd -S $Server @connection -d master -b -i (Join-Path $demoFolder '90_Cleanup.sql') -v "DemoId=$DemoId" 'RunToken=LOCAL' "TargetDatabase=$targetDatabase" @safetyValues "MaximumRuntimeSeconds=600"
}

# Beispiel: nur nach einem abgebrochenen Lauf von CON-004
Invoke-AbortedSqlPerfDemoCleanup -DemoId CON-004 -Server $server -Authentication $authentication -Username $username
```

Wiederholen Sie danach die Datenbankabfrage. Bleibt eine Datenbank bestehen oder endet das Cleanup nicht mit `PASS`, stoppen Sie weitere Läufe und prüfen Sie die Demo-README sowie [`LOCAL_TEST_ENVIRONMENT.md`](LOCAL_TEST_ENVIRONMENT.md).

## 7. Sitzung schließen

Entfernen Sie nach SQL-Authentifizierung das Kennwort aus der Prozessumgebung. Entfernen Sie bei Bedarf auch die Zertifikatsausnahme.

```powershell
Remove-Item Env:SQLCMDPASSWORD -ErrorAction SilentlyContinue
Remove-Item Env:SQLPERF_HOST_TRUST_SERVER_CERTIFICATE -ErrorAction SilentlyContinue
```

Die fachliche Deutung der Beobachtungen steht jeweils in der Demo-README; die zusammenhängende didaktische Erklärung aller Demos bietet [`DEMO_WALKTHROUGHS.md`](DEMO_WALKTHROUGHS.md).
