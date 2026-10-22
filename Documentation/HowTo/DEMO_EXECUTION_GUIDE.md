# Ausführungsleitfaden für die katalogisierten Demos

Mit dieser Anleitung wählen Sie ein Beispiel aus, bereiten die Testumgebung
vor, führen die Demo in PowerShell aus und ordnen ihre Ergebnisse ein.
Die [Schritt-für-Schritt-Erklärungen der Fachdemos](DEMO_WALKTHROUGHS.md)
erläutern die fachlichen Hintergründe. Die jeweilige Demo-README beschreibt
Lernziel, Datenmodell, Voraussetzungen und Grenzen.

| Ihr nächster Schritt | Abschnitt |
|---|---|
| Ein Thema und seine Versionsvoraussetzung wählen | [1. Demo auswählen](#1-demo-auswählen) |
| Werkzeuge und eine geeignete Instanz vorbereiten | [2. Arbeitsplatz und Instanz vorbereiten](#2-arbeitsplatz-und-instanz-vorbereiten) |
| Die Verbindung einrichten | [3. Zugangsdaten und Verbindungsparameter](#3-zugangsdaten-und-verbindungsparameter-setzen) |
| Den Aufrufer laden und ein Beispiel starten | [4. Aufrufer laden](#4-einmalig-den-demo-aufrufer-laden), dann [5. Ausführen und beobachten](#5-demo-ausführen-und-beobachten) |
| Nach einem Lauf oder Abbruch prüfen, was erhalten bleiben muss | [6. Cleanup und Wiederherstellung](#6-cleanup-prüfen-und-nach-abbruch-wiederherstellen) |
| Die Sitzung beenden | [7. Sitzung schließen](#7-sitzung-schließen) |

Beginnen Sie mit dem [Demo-Katalog](../Demo_Catalog/README.md): Dort sind Ausführungsvoraussetzung, Implementierungsstatus und datierter Runtime-Nachweis getrennt dargestellt. Die Demo zur NULL-Semantik (`QRY-006`) bleibt `IMPLEMENTED` mit lokalem Nachweis und offenem Runtime-Gate; seine Aufnahme in den Aufrufer bedeutet keine vollständige Abnahme. Die Teilmanifeste der zeitlich begrenzten Vorfallsdiagnose (`DGN-007`) gehören nicht zu diesem allgemeinen Ausführungspfad.

Für den ergänzenden Kurs zu künstlicher Intelligenz (KI) führen das
[Offline-Arbeitsheft mit Trainerlösungen](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md)
und der [Trainerleitfaden](SQL_SERVER_2025_AI_OFFLINE_TRAINER_GUIDE.md) durch
die Übungen. Diese Teilentwürfe sind keine Gesamtlehrgangsfreigabe.

Die Demos erzeugen und entfernen synthetische Testdatenbanken. Verwenden Sie
eine eigens dafür vorgesehene, zurücksetzbare Testinstanz ohne fremde Daten.
Nach einem Abbruch gilt der Erhaltungsweg in Abschnitt 6: Die Eigentumsprüfung
ist noch nicht für sämtliche hier aufgeführten Cleanupskripte belastbar.

## 1. Demo auswählen

Wählen Sie eine Demo aus der folgenden Tabelle. Die Demo-ID ist die stabile technische Kennung; das Thema und die Kurzbeschreibung erklären, was Sie damit lernen. Verwenden Sie in Schritt 5 nur die Kennung, etwa `QRY-001`, unverändert als `-DemoId`. Die Links führen zur ausführlichen fachlichen Beschreibung. Ein Manifest (`manifest.json`) legt die Skripte, Phasen und Laufparameter fest, die der Demo-Aufrufer (Harness) verwendet.

Die Kennungspräfixe bezeichnen Themenbereiche: `OPT` Optimizer und Ausführungspläne, `QRY` Abfragemuster, `DGN` Diagnose, `CON` Parallelzugriffe und Sperren, `IDX` Indizes, `STL` Speicherung und Transaktionslog sowie `RES` Ressourcen und Wartezeiten.

Die Sicherheitsstufen bedeuten `GREEN` (grün: eigene Testdatenbank), `YELLOW` (gelb: isolierte, zurücksetzbare Instanz) und `RED` (rot: ausdrücklich bestätigte Wegwerfinstanz). `2022/160` bezeichnet SQL Server 2022 mit Datenbank-Kompatibilitätsgrad (Compatibility Level) 160. Die Serverversion und diese Datenbankeinstellung sind getrennte Voraussetzungen.

| Kennung und Thema | Was zeigt die Demo? | Sicherheitsstufe | Versionsvoraussetzung: Engine / Compatibility Level | Besonderheit |
|---|---|---|---|---|
| [`OPT-002`](../../Demos/04_Optimizer_Statistics_Plans/OPT-002_Statistics_Anatomy/README.md) – Statistiken lesen | Statistikheader, Histogramm und Dichtewerte voneinander abgrenzen. | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`OPT-003`](../../Demos/04_Optimizer_Statistics_Plans/OPT-003_Sampling_Skew/README.md) – Stichproben und ungleiche Datenverteilung | Stichprobenstatistik und vollständige Datenerfassung am selben Datenbestand vergleichen. | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`OPT-005`](../../Demos/04_Optimizer_Statistics_Plans/OPT-005_Ascending_Key/README.md) – Wachsende Schlüssel und Statistikpflege | Neu hinzugekommene Schlüsselwerte und die Aktualität der Statistiken untersuchen. | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`OPT-009`](../../Demos/04_Optimizer_Statistics_Plans/OPT-009_Parameter_Sensitive_Plans/README.md) – Parametersensitive Planoptimierung | Parameter Sensitive Plan Optimization (PSP): unterschiedliche Planvarianten für geeignete Parameterwerte untersuchen. | `GREEN` | 2022/160, 2025/170 | 2019 ergibt vorgesehenes `SKIP_VERSION` |
| [`OPT-010`](../../Demos/04_Optimizer_Statistics_Plans/OPT-010_Optional_Parameter_Plans/README.md) – Planoptimierung für optionale Parameter | Optional Parameter Plan Optimization (OPPO): Planvarianten für optionale Filter mit und ohne Parameterwert untersuchen. | `GREEN` | 2025/170 | 2019 und 2022 ergeben vorgesehenes `SKIP_VERSION` |
| [`OPT-013`](../../Demos/04_Optimizer_Statistics_Plans/OPT-013_Controlled_Spill/README.md) – Sortieren mit zu wenig Arbeitsspeicher | Einen Sort-Spill, also das Auslagern von Sortierdaten nach tempdb, und eine Gegenmaßnahme beobachten. | `YELLOW` | 2019/150, 2022/160, 2025/170 | belastet `tempdb` |
| [`OPT-015`](../../Demos/04_Optimizer_Statistics_Plans/OPT-015_Plan_Properties/README.md) – Ausführungspläne systematisch lesen | Planweite Eigenschaften, Operatoren, Schätzungen und tatsächliche Zeilenzahlen unterscheiden. | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`OPT-016`](../../Demos/04_Optimizer_Statistics_Plans/OPT-016_Rebind_Rewind_Spools/README.md) – Wiederholte Operatorausführung und Zwischenspeicherung | Rebind, Rewind und Spools: neue Eingabebindung, Wiederverwendung und Zwischenspeicherung im Plan einordnen. | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`OPT-017`](../../Demos/04_Optimizer_Statistics_Plans/OPT-017_Parallelism_Skew/README.md) – Ungleich verteilte parallele Arbeit | Die Arbeit der beteiligten Ausführungsthreads statt nur die Anzahl der Prozessoren betrachten. | `YELLOW` | 2019/150, 2022/160, 2025/170 | Container oder Wegwerfinstanz mit mindestens vier sichtbaren logischen Prozessoren (CPUs) |
| [`QRY-001`](../../Demos/05_Query_Patterns/QRY-001_SARGability/README.md) – Indexfreundliche Suchbedingungen | Eine Funktion auf der Suchspalte durch eine gleichwertige Bereichsbedingung ersetzen und die Zugriffe vergleichen. | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`QRY-004`](../../Demos/05_Query_Patterns/QRY-004_Classic_And_Dynamic/README.md) – Optionale Filter, Recompile und dynamisches SQL | Wiederverwendung, erneute Kompilierung und parameterisiertes dynamisches SQL im selben Suchproblem vergleichen. | `GREEN` | 2019/150, 2022/160, 2025/170 | historischer Nachweis mit `WARN_EMPIRICAL_VARIANCE`; kein beobachteter Read-Vorteil durch Recompile |
| [`QRY-006`](../../Demos/05_Query_Patterns/QRY-006_NULL_Semantics/README.md) – NULL bei NOT IN und NOT EXISTS | Zeigen, wie unbekannte Werte die Ergebnismengen der beiden Vergleichsformen beeinflussen. | `GREEN` | 2019/150, 2022/160, 2025/170 | lokale Docker-Matrix bestanden; Runtime-Gate offen; NULL-Ergebnisvertrag |
| [`QRY-013`](../../Demos/05_Query_Patterns/QRY-013_Client_Session_Context/README.md) – Anwendung langsam, Verwaltungswerkzeug schnell | Datenbankkontext, Sitzungseinstellungen, Parameter und Planwahl verschiedener Clients vergleichen. | `GREEN` | 2019/150, 2022/160, 2025/170 | – |
| [`QRY-014`](../../Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/README.md) – Vektortypen und Dimensionen | Synthetische Vektoren speichern und ihre Dimension sowie den gemeinsamen Modellraum unterscheiden. | `GREEN` | 2025/170 | 2019/2022: SKIP_VERSION; lokale Mechanikfixture |
| [`QRY-015`](../../Demos/09_AI_SQL_Server_2025/QRY-015_Vector_Metrics/README.md) – Vektordistanzen und Normalisierung | Distanz, Vektorlänge und Normalisierung an konstruierten Geometrievektoren erklären. | `GREEN` | 2025/170 | 2019/2022: SKIP_VERSION; lokale Mechanikfixture |
| [`QRY-016`](../../Demos/09_AI_SQL_Server_2025/QRY-016_Chunk_Provenance/README.md) – Textabschnitte und Quellenherkunft | Chunking, Überlappung und die Rückverfolgbarkeit eines Textabschnitts zur Quelle zeigen. | `GREEN` | 2025/170 | 2019/2022: SKIP_VERSION; lokale Mechanikfixture |
| [`QRY-017`](../../Demos/09_AI_SQL_Server_2025/QRY-017_Search_Comparison/README.md) – Suchverfahren vergleichen | Relationale Filter, Volltextsuche und exakte Vektorsuche am selben Beispiel gegenüberstellen. | `GREEN` | 2025/170 | 2019/2022: SKIP_VERSION; Full-Text optional |
| [`QRY-018`](../../Demos/09_AI_SQL_Server_2025/QRY-018_Offline_RAG/README.md) – Quellengestützte Antworten im Offline-Beispiel | Retrieval-Augmented Generation (RAG): Quellen auswählen und vorab festgelegte Antworten gegen diesen Kontext prüfen. | `GREEN` | 2025/170 | 2019/2022: SKIP_VERSION; Offline-Replay, kein Modell |
| [`QRY-019`](../../Demos/09_AI_SQL_Server_2025/QRY-019_SQL_Input_Policy/README.md) – Feste SQL-Struktur und getrennte Parameterwerte | Erlaubte Anweisungsstruktur von Eingabewerten trennen und abgelehnte Strukturen nicht ausführen. | `GREEN` | 2025/170 | 2019/2022: SKIP_VERSION; feste SQL-Form, gebundene Werte |
| [`DGN-008`](../../Demos/09_AI_SQL_Server_2025/DGN-008_Offline_Model_Rights/README.md) – Modellmetadaten und Zugriffsrechte | Modellbeschreibung und getrennte Berechtigungen ohne externen Modellaufruf untersuchen. | `GREEN` | 2025/170 | 2019/2022: SKIP_VERSION; Modellmetadaten und getrennte Offline-Rechte |
| [`DGN-009`](../../Demos/09_AI_SQL_Server_2025/DGN-009_Offline_Injection/README.md) – Manipulierte Quellen und erlaubte Werkzeugaufrufe | Angriffstexte in Quellen von der festgelegten Erlaubnis für Werkzeuge trennen. | `GREEN` | 2025/170 | 2019/2022: SKIP_VERSION; manipulierte Quellen und feste Toolpolicy |
| [`CON-010`](../../Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/README.md) – Daten verschiedener Mandanten trennen | Row-Level Security (RLS), also zeilenbezogene Zugriffskontrolle, vor der Auswahl des Vektorkontexts prüfen. | `GREEN` | 2025/170 | 2019/2022: SKIP_VERSION; RLS, exakte Quellen und drei native Rechteverweigerungen |
| [`IDX-006`](../../Demos/04_Rowstore_Columnstore/IDX-006_Page_Splits_Density/README.md) – Seitenaufteilungen und Seitenbelegung | Page Splits, Belegungsgrad und logische Fragmentierung getrennt untersuchen. | `YELLOW` | 2019/150, 2022/160, 2025/170 | isolierte Instanz; historischer Nachweis mit `WARN_EMPIRICAL_VARIANCE`, keine allgemeine Fill-Factor-Richtung |
| [`IDX-010`](../../Demos/04_Rowstore_Columnstore/IDX-010_Columnstore_Segments/README.md) – Columnstore-Segmente gezielt überspringen | Zeilengruppenqualität und das Auslassen unpassender Spaltensegmente bei einer Abfrage untersuchen. | `YELLOW` | 2019/150, 2022/160, 2025/170 | Container oder Wegwerfinstanz mit Ressourcenprofil |
| [`CON-004`](../../Demos/07_Concurrency/CON-004_Blocking_Chain/README.md) – Blockierungsketten verfolgen | Blockierende Sitzungen und den Anfang einer Sperrwarte-Kette ermitteln. | `YELLOW` | 2019/150, 2022/160, 2025/170 | Mehrsitzungsorchestrierung; alternativ interaktiv gemäß [Interaktive Schulungsszenarien bedienen](INTERACTIVE_SCENARIO_LIFECYCLE.md) |
| [`CON-006`](../../Demos/07_Concurrency/CON-006_Deadlock_Cycle/README.md) – Zyklische Sperrkonflikte erkennen | Einen Deadlock-Zyklus zwischen Sitzungen nachvollziehen. | `YELLOW` | 2019/150, 2022/160, 2025/170 | Mehrsitzungsorchestrierung |
| [`CON-009`](../../Demos/05_Concurrency_Isolation_TempDB/CON-009_TempDB_Cost_Classes/README.md) – Kosten in tempdb unterscheiden | Unterschiedliche Ursachen der Belastung der temporären Systemdatenbank auseinanderhalten. | `YELLOW` | 2019/150, 2022/160, 2025/170 | isolierte Instanz |
| [`DGN-003`](../../Demos/07_Query_Store_Extended_Events/DGN-003_Query_Store_History/README.md) – Abfragehistorie mit Query Store | Historische Abfragen, Pläne und Laufzeitdaten gegenüber dem aktuellen Zustand einordnen. | `GREEN` | 2019/150, 2022/160, 2025/170 | Query Store nur in der Testdatenbank |
| [`DGN-005`](../../Demos/07_Query_Store_Extended_Events/DGN-005_Bounded_Extended_Events/README.md) – Gezielte Ereigniserfassung mit Extended Events | Ereignisse, Filter, Zusatzinformationen und Erfassungszeitraum zusammen festlegen. | `YELLOW` | 2019/150, 2022/160, 2025/170 | begrenzte Extended-Events-Evidenz |
| [`STL-008`](../../Demos/01_Storage_Pages_Log/STL-008_VLF_Log_Growth/README.md) – Transaktionslog und Dateiwachstum | Virtual Log Files (VLF), die internen Abschnitte einer Logdatei, und deren Wachstum untersuchen. | `RED` | 2019/150, 2022/160, 2025/170 | nur Wegwerf-Containerinstanz; Recovery muss vor Start bestätigt sein |
| [`STL-009`](../../Demos/01_Storage_Pages_Log/STL-009_Commit_Batching/README.md) – Mehrere Änderungen gemeinsam bestätigen | Kleine und gebündelte Transaktionen hinsichtlich ihrer Log-Schreibvorgänge vergleichen. | `YELLOW` | 2019/150, 2022/160, 2025/170 | isolierte Instanz |
| [`RES-007`](../../Demos/06_CPU_Memory_IO_Waits/RES-007_Wait_Scope_Deltas/README.md) – Wartezeiten im richtigen Messbereich | Zeitbezogene Differenzen von Wartezählern bilden und ihrem Erfassungsbereich zuordnen. | `YELLOW` | 2019/150, 2022/160, 2025/170 | Mehrsitzungsorchestrierung und Server-State-Berechtigung |

## 2. Arbeitsplatz und Instanz vorbereiten

1. Klonen Sie das Repository und öffnen Sie PowerShell im Repository-Stamm.
2. Installieren Sie Python 3.12 oder höher und Microsoft `sqlcmd`; beide Befehle müssen im Suchpfad liegen.
3. Stellen Sie eine SQL-Server-2019-, -2022- oder -2025-Instanz bereit. Verwenden Sie für gelbe und rote Demos eine Wegwerfinstanz. Für `OPT-017`, `IDX-010` und `STL-008` ist der Containerpfad erforderlich oder empfohlen; die Bereitstellung ist in [Docker-/Podman-Quickstart ohne vorhandenen SQL Server](CONTAINER_QUICKSTART.md) beschrieben.
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
    'QRY-006' = @{ Manifest = 'Demos/05_Query_Patterns/QRY-006_NULL_Semantics/manifest.json'; Safety = 'GREEN' }
    'QRY-013' = @{ Manifest = 'Demos/05_Query_Patterns/QRY-013_Client_Session_Context/manifest.json'; Safety = 'GREEN' }
    'QRY-014' = @{ Manifest = 'Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/manifest.json'; Safety = 'GREEN' }
    'QRY-015' = @{ Manifest = 'Demos/09_AI_SQL_Server_2025/QRY-015_Vector_Metrics/manifest.json'; Safety = 'GREEN' }
    'QRY-016' = @{ Manifest = 'Demos/09_AI_SQL_Server_2025/QRY-016_Chunk_Provenance/manifest.json'; Safety = 'GREEN' }
    'QRY-017' = @{ Manifest = 'Demos/09_AI_SQL_Server_2025/QRY-017_Search_Comparison/manifest.json'; Safety = 'GREEN' }
    'QRY-018' = @{ Manifest = 'Demos/09_AI_SQL_Server_2025/QRY-018_Offline_RAG/manifest.json'; Safety = 'GREEN' }
    'QRY-019' = @{ Manifest = 'Demos/09_AI_SQL_Server_2025/QRY-019_SQL_Input_Policy/manifest.json'; Safety = 'GREEN' }
    'DGN-008' = @{ Manifest = 'Demos/09_AI_SQL_Server_2025/DGN-008_Offline_Model_Rights/manifest.json'; Safety = 'GREEN' }
    'DGN-009' = @{ Manifest = 'Demos/09_AI_SQL_Server_2025/DGN-009_Offline_Injection/manifest.json'; Safety = 'GREEN' }
    'CON-010' = @{ Manifest = 'Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/manifest.json'; Safety = 'GREEN' }
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
        [Parameter(Mandatory)][ValidateSet('OPT-002','OPT-003','OPT-005','OPT-009','OPT-010','OPT-013','OPT-015','OPT-016','OPT-017','QRY-001','QRY-004','QRY-006','QRY-013','QRY-014','QRY-015','QRY-016','QRY-017','QRY-018','QRY-019','DGN-008','DGN-009','CON-010','IDX-006','IDX-010','CON-004','CON-006','CON-009','DGN-003','DGN-005','STL-008','STL-009','RES-007')][string]$DemoId,
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

1. Starten Sie genau eine ausgewählte Demo. Beispiel für die grüne Einsteiger-Demo zu indexfreundlichen Suchbedingungen (`QRY-001`) mit Windows-Authentifizierung:

```powershell
Invoke-SqlPerfDemo -DemoId QRY-001 -Server $server -Authentication $authentication
```

2. Für eine gelbe Demo bestätigen Sie vorher, dass die Instanz isoliert ist. Dieses Beispiel startet die Mehrsitzungsdemo für Blockierungsketten (`CON-004`):

```powershell
Invoke-SqlPerfDemo -DemoId CON-004 -Server $server -Authentication $authentication -Username $username -ConfirmIsolatedLab
```

3. Führen Sie die Demo zu Logwachstum (`STL-008`) nur auf einer Wegwerf-Containerinstanz aus, nachdem Sie den Resetpfad geprüft haben. Die explizite Bestätigung aktiviert die rote Demo:

```powershell
Invoke-SqlPerfDemo -DemoId STL-008 -Server $server -Authentication $authentication -Username $username -AllowRed
```

4. Bei einem selbstsignierten Zertifikat ergänzen Sie beim jeweiligen Aufruf `-TrustServerCertificate`. Diese Einstellung ist ausschließlich für die bereits bestätigte Wegwerfinstanz zulässig.

Der Demo-Aufrufer führt die im jeweiligen `manifest.json` festgelegten Phasen in ihrer Reihenfolge sowie `CLEANUP` aus. Die NULL-Demo (`QRY-006`) verwendet bewusst nur die vier fachlichen Phasen `PREFLIGHT`, `SETUP`, `DEMONSTRATION` und `ASSERTION` sowie das anschließende Cleanup; Mehrsitzungsdemos führen an Stelle der Demonstration ein Sitzungsmanifest aus.

| Phasenname | Bedeutung |
|---|---|
| `PREFLIGHT` | Voraussetzungen vor dem Lauf prüfen. |
| `SETUP` | Synthetische Testdatenbank und Testdaten vorbereiten. |
| `DEMONSTRATION` | Das Verhalten ausführen und beobachten. |
| `ASSERTION` | Ergebnisse gegen die festgelegten Erwartungen prüfen. |
| `CLEANUP` | Eigene Testdatenbank nach Prüfung der Eigentumsmarker entfernen. |

Ordnen Sie die Summary nach dem bestehenden [Vertrag für Status-, Fehler- und Überspringcodes (`FWK-012`)](../../Demos/00_Framework/Contracts/FWK-012_Status_Error_Skip_Contract.md) ein:

| Ergebnis | Bedeutung für die Vorführung |
|---|---|
| `PASS / OK` | Die im Lauf geprüften Verträge sind erfüllt. Die beobachtete Wirkung gilt für das konkrete Datenmodell und die verwendete Umgebung. |
| `SKIP / SKIP_VERSION` | Die Funktion ist auf dieser Version nicht verfügbar. Das ist ein Nachweis der Versionsgrenze, kein Nachweis ihrer Wirkung. Bei den oben genannten Versions-Skips für die oben beschriebenen Planoptimierungen (PSP und OPPO) entsteht keine Demodatenbank. |
| `WARN / WARN_EMPIRICAL_VARIANCE` | Eine erwartete Performance-Richtung oder Messqualität ist eingeschränkt. Beispielsweise lieferte `QRY-004` im dokumentierten Matrixlauf keinen Read-Vorteil durch Recompile. Stellen Sie keine Verbesserung dar, die nicht beobachtet wurde. |
| `WARN / WARN_OPTIONAL_EVIDENCE_SKIPPED` | Ein optionaler Evidenzteil entfiel. Die zulässige Schlussfolgerung ergibt sich aus der Demo-README und den übrigen Resultaten. |
| `SKIP / SKIP_EVIDENCE_MISSING` | Die erforderliche Wirkung ist in diesem Lauf nicht nachgewiesen. Benennen Sie die Prüflücke und verwenden Sie den Lauf nicht als fachlichen Erfolgsbeleg. |
| andere kontrollierte `SKIP`-Codes | Eine konkrete Voraussetzung fehlt, etwa Rechte, Werkzeug oder Ressourcenprofil. Beheben Sie die benannte Voraussetzung; eine Wirkung ist damit noch nicht geprüft. |
| `FAIL` | Ein Vertrag oder die Ausführung ist fehlgeschlagen. Die gemeldete Phase ist der Diagnoseeinstieg; keine erfolgreiche Vorführung behaupten. `FAIL_CLEANUP` hat Vorrang und muss vor weiteren Läufen behoben werden. |

Der Harness kann auch bei `WARN` oder kontrolliertem `SKIP` mit Exitcode 0 enden. Exitcode und grüner Status der automatisierten Repository-Prüfungen (Continuous Integration, CI) allein ersetzen daher weder die Phasenergebnisse noch die fachliche Evidenz. Die Tabelle erläutert bestehende Codes und führt keine neuen Statuswerte ein.

## 6. Cleanup prüfen und nach Abbruch wiederherstellen

Das Harness startet nach begonnenem Setup immer `CLEANUP`. Prüfen Sie dennoch nach jedem Lauf, dass keine Schulungsdatenbank zurückblieb:

```powershell
sqlcmd -S $server -E -d master -Q "SELECT name FROM sys.databases WHERE name LIKE N'SQLPERF[_]LAB[_]%';"
```

Für SQL-Authentifizierung verwenden Sie stattdessen `-U $username`; das Kennwort bleibt in `SQLCMDPASSWORD`.

Wenn PowerShell, `sqlcmd` oder der Rechner während eines Laufs beendet wurde,
erhalten Sie zurückgebliebene Datenbanken und starten vorerst keinen weiteren
Lauf gegen diese Instanz. Ein Name mit dem Präfix `SQLPERF_LAB_` belegt kein
Eigentum. Führen Sie kein manuelles `DROP DATABASE` anhand eines Namensmusters
und keinen eigenständigen Wiederholungsaufruf eines Cleanupskripts aus.

Bei der Demo zu indexfreundlichen Suchbedingungen (`QRY-001`) prüfen Setup
und Cleanup die vollständigen Eigentumsmarker; das Setup tut dies bei einer
vorhandenen Datenbank vor Konfigurations- und Tabellenänderungen. Die begrenzten
Gegenproben verwenden eigene synthetische Daten in einer Wegwerfinstanz.
Zehn weitere Einrichtungsskripte prüfen vorhandene Datenbanken ebenfalls vor
der ersten Konfigurations- oder Tabellenänderung. Die einzelnen Demos mit Thema,
Versionsgrenzen und tatsächlichem Prüfstand stehen im
[abgegrenzten Setupumfang](../Project_Planning/FWK_002_SETUP_OWNERSHIP_REVIEW.md).
Fehlende oder abweichende Eigentumsmarker führen zur Ablehnung und Erhaltung
der Datenbank.

Die 22 weiteren Cleanupquellen im [abgegrenzten Eigentumsumfang](../Project_Planning/FWK_002_CLEANUP_OWNERSHIP_REVIEW.md)
lesen inzwischen ebenfalls alle vier Eigentumsmarker vollständig und weisen
fehlende oder abweichende Werte ab. Bei der gezielten Ereigniserfassung
(`DGN-005`) bleibt auch die Ereignissitzung erhalten, solange das
Datenbankeigentum ungeklärt ist. Eine fehlende Datenbank bei vorhandener
Ereignissitzung ist ein Fehler und verlangt Klärung.

Das qualifiziert ausschließlich die genannten Eigentumspfade. Insbesondere
die erstmalige Markierung einer neuen Datenbank und weitere bestehende Setups
sind nicht allgemein freigegeben. Die verbleibenden Prüfungen stehen im
[aktuellen Ausführungsstand](../Project_Planning/CURRENT_EXECUTION_STATUS.md#wiederaufnahme-vom-22-oktober-2026-eigentumsprüfungen-zuerst).
Eine pauschale Eigentumsgarantie für den gesamten Ausführungspfad gilt weiterhin
nicht. Die oben angeordnete Erhaltung nach einem Abbruch bleibt maßgeblich.

Stoppen Sie hier bei erhaltenem oder ungeklärtem Instanz- beziehungsweise
Szenariozustand und schließen Sie die Sitzung gemäß Abschnitt 7. Bewahren Sie
die bisherige Instanz und ihre Daten zur Klärung auf. Übernehmen Sie keine
Reset- oder Remove-Schritte aus dem Container-Quickstart: Er beschreibt keinen
Wiederanlauf mit erhaltenem Altzustand. Ein neuer Bereitstellungsweg müsste
die neue Umgebung und ihren Steuerungszustand unabhängig abgrenzen; ein
solcher Weg ist hier noch nicht beschrieben. Erst ein korrigierter und
geprüfter Cleanupweg darf die zurückgebliebene Datenbank entfernen.

## 7. Sitzung schließen

Entfernen Sie nach SQL-Authentifizierung das Kennwort aus der Prozessumgebung. Entfernen Sie bei Bedarf auch die Zertifikatsausnahme.

```powershell
Remove-Item Env:SQLCMDPASSWORD -ErrorAction SilentlyContinue
Remove-Item Env:SQLPERF_HOST_TRUST_SERVER_CERTIFICATE -ErrorAction SilentlyContinue
```

Die fachliche Deutung der Beobachtungen steht jeweils in der Demo-README; die zusammenhängende didaktische Erklärung aller Demos bietet [Demo-Walkthroughs – Schritt-für-Schritt-Erklärungen aller Fachdemos](DEMO_WALKTHROUGHS.md).
