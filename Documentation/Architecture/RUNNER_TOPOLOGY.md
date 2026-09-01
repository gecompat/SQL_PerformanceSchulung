# Runner-Topologie

Anforderungsspezifikation für den externen Runner `Key18_Perf`. Grundlage: `Documentation/Project_Planning/INF_001_EXECUTION_TARGET_DESIGN.md`, `DEC-046`, `DEC-047` und `DEC-049`.

Dieses Dokument beschreibt eine Anforderung, keinen vorhandenen Zustand. `Key18_Perf` ist derzeit **nicht eingerichtet**.

## 1. Ausgangslage

| Ausführungsziel | Runner | Stand |
|---|---|---|
| `local-host` | Arbeitsplatz der ausführenden Person | verfügbar, kein Gate-Pfad |
| `github-hosted` | GitHub-gehostete Runner, `ubuntu-latest` | verfügbar, verbindlicher Gate-Pfad |
| `key18-perf` | externer Runner `Key18_Perf` | nicht vorhanden |

Auf den derzeit verwendeten Arbeitsplätzen kann kein selbstgehosteter Runner installiert werden. GitHub-gehostete Runner bleiben uneingeschränkt nutzbar und tragen die gesamte heutige Gate-Evidenz.

## 2. Warum ein eigener Runner benötigt wird

GitHub-gehostete Runner decken die Stufen 1 bis 3 der Entscheidungsleiter aus Abschnitt 13.2 des Masterplans ab. Sie decken nicht ab:

| Anforderung | Grund |
|---|---|
| Hyper-V-VMs | Verschachtelte Virtualisierung mit Windows-Gastsystem ist auf den gehosteten Images nicht vorgesehen. |
| mehrere SQL-Server-Instanzen nebeneinander | Der Speicher- und Zeitrahmen eines gehosteten Runners reicht für eine Einzelinstanz je Job. |
| dedizierte CPU-, RAM- und I/O-Grenzen | Gehostete Runner geben keine stabile, wiederholbare Ressourcenzusage. |
| gedrosseltes I/O und Netzwerkbedingungen | Erfordert Kontrolle über Host und Speicherpfad. |
| Windows-nahe Messung | Erfordert ein Windows-Gastsystem unter eigener Kontrolle. |

## 3. Anforderungen an `Key18_Perf`

### 3.1 Kennzeichnung

| Merkmal | Anforderung |
|---|---|
| Name | `Key18_Perf` |
| Labels | `key18-perf` als verbindliches Auswahllabel; ergänzend `hyper-v`, `docker`, `podman` je nach tatsächlich bereitgestellter Fähigkeit |
| Auswahl in Workflows | über die Repository-Variable `SQLPERF_RUNTIME_RUNNER` |

### 3.2 Fähigkeiten

| Fähigkeit | Anforderung |
|---|---|
| Hyper-V | Erzeugen, Starten, Stoppen, Zurücksetzen und Entfernen von VMs aus einem Basisimage |
| Docker | Betrieb von `mcr.microsoft.com/mssql/server` für 2019, 2022 und 2025 |
| Podman | dieselbe Spezifikation wie Docker, damit `INF-003` geprüft werden kann |
| Parallelbetrieb | Docker und Podman müssen nebeneinander betreibbar sein, ohne sich gegenseitig zu stören |
| Ressourcengrenzen | reproduzierbare CPU- und RAM-Grenzen je Container oder VM |
| Speicher | ausreichend Platz für ein Windows-Basisimage plus differenzierende Testzustände |

### 3.3 Sicherheitsgrenzen

Ein selbstgehosteter Runner führt Code aus dem Repository auf eigener Infrastruktur aus. Daraus folgen verbindliche Grenzen:

- Der Runner wird **nicht** für Läufe aus Forks freigegeben. `pull_request`-Ereignisse fremder Forks bleiben auf GitHub-gehosteten Runnern.
- Der Arbeitsbereich wird vor und nach jedem Lauf vollständig entfernt. Zustände dürfen nicht zwischen Läufen fortbestehen.
- Der Runner erhält keine Zugangsdaten zu produktiven Systemen. Er benötigt ausschließlich lokale Wegwerfinstanzen.
- Kennwörter werden auch dort ausschließlich über `SQLCMDPASSWORD` bereitgestellt.
- Der Runner steht in einem eigenen Netzsegment ohne Zugriff auf Produktionsnetze.
- Erzeugte VMs und Container werden nach jedem Lauf entfernt, auch bei Abbruch.

### 3.4 Betrieb

| Aspekt | Anforderung |
|---|---|
| Verfügbarkeit | kein Dauerbetrieb erforderlich; Läufe dürfen warten |
| Aktualisierung | Basisimages werden nachvollziehbar versioniert |
| Diagnose | Laufprotokolle enthalten keine Host-, Instanz- oder Benutzernamen |
| Ausfall | Fällt der Runner aus, laufen alle heutigen Prüfungen unverändert auf GitHub-gehosteten Runnern weiter |

## 4. Was der Runner entsperrt

| Gegenstand | Heutiger Stand | Nach Bereitstellung |
|---|---|---|
| `INF-004` Hyper-V-Bereitstellungspfad | zurückgestellt | umsetzbar |
| `INF-005` CPU-/RAM-Limits für Ressourcen-Demos | zurückgestellt | umsetzbar |
| `INF-006` I/O-, Log-, Netzwerk- oder Mehrinstanztopologie | zurückgestellt | umsetzbar |
| Stufe 4 und 5 der Entscheidungsleiter | nicht implementiert | implementierbar |
| Rote Szenarien einschließlich `RES-003` | zurückgestellt | ausführbar |
| `RUNNER_ASSISTED`-Teilnehmerablauf in `LABSCN-003` | nicht umgesetzt | umsetzbar |
| `INF-003` geprüfte Podman-Variante | lokal mit vollständigem SQL-Server-2025-Lifecycle validiert | keine Runnerabhängigkeit mehr |

`LABSCN-002` ist abgeschlossen. `CON-004` und `DGN-005` verwenden die kleinste ausreichende Orchestrierungsstufe `MANUAL` und sind auf Docker sowie Podman praktisch validiert.

## 5. Umschaltung der Workflows

Die Runtimejobs der drei Workflows mit SQL-Server-Container wählen ihren Runner über eine Repository-Variable:

```yaml
runs-on: ${{ vars.SQLPERF_RUNTIME_RUNNER || 'ubuntu-latest' }}
```

Betroffen sind `framework-sql-matrix.yml`, `gate-b-pilots.yml` und `adv008-opt015-opt016.yml`. Ist die Variable nicht gesetzt, gilt unverändert `ubuntu-latest`.

Die statischen Jobs bleiben fest auf `ubuntu-latest`. Sie starten keinen SQL Server, laufen in wenigen Minuten und hätten auf eigener Infrastruktur keinen Nutzen, aber zusätzliche Angriffsfläche.

Die Variable wird erst gesetzt, wenn `Key18_Perf` verfügbar ist und die Sicherheitsgrenzen aus Abschnitt 3.3 erfüllt. Bis dahin bleibt die Parametrisierung wirkungslos und dient allein dazu, den späteren Wechsel ohne Workflow-Umbau zu ermöglichen.

## 6. Abgrenzung

Dieses Dokument richtet keinen Runner ein und beschreibt keine Installationsschritte. Es hält die Anforderungen fest, damit die zurückgestellten Bündel bei Verfügbarkeit ohne erneute Entwurfsarbeit begonnen werden können.
