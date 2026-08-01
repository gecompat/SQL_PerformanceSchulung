# Review – INF-001 Ausführungspfad

| Merkmal | Wert |
|---|---|
| Status | `IMPLEMENTED_FOR_REVIEW` |
| Stand | 2026-08-01 |
| Arbeitspaket | `INF-001` – Ausführungsziele und Testumgebungs-How-to |
| Entscheidungen | `DEC-046` bis `DEC-051` |
| PowerPoint geändert | nein |

## 1. Umfang

Der Schnitt bildet die Entscheidungsleiter aus Abschnitt 13.2 des Masterplans technisch ab. Sie war fachlich beschlossen, aber nicht implementiert: Die Runtime-Runner unterstützten ausschließlich die containerisierte Einzelinstanz.

Enthalten sind vier Teile:

1. ein Entwurf der Ausführungsziele `local-host`, `github-hosted` und `key18-perf`,
2. ein Modul, das die Zielunterschiede kapselt, samt Shim für eine vorhandene Instanz,
3. das Testumgebungs-How-to nach dem Pflichtinhalt aus Abschnitt 13.4,
4. die Anforderungsspezifikation des externen Runners `Key18_Perf`.

## 2. Geänderte und neue Artefakte

| Artefakt | Art | Inhalt |
|---|---|---|
| `Documentation/Project_Planning/INF_001_EXECUTION_TARGET_DESIGN.md` | neu | Zielmatrix, Gate-Regel, Schnittstelle der Runner |
| `Documentation/HowTo/LOCAL_TEST_ENVIRONMENT.md` | neu | Bedienanleitung für eine vorhandene Instanz |
| `Documentation/Architecture/RUNNER_TOPOLOGY.md` | neu | Anforderungen an `Key18_Perf` |
| `Tests/Runtime/execution_target.py` | neu | Kapselung der Ausführungsziele |
| `Tests/Runtime/host_sqlcmd_target.py` | neu | sqlcmd-Shim für eine vorhandene Instanz |
| `Tests/Static/validate_inf_001_execution_path.py` | neu | statische Prüfung des Ausführungspfads |
| `.github/workflows/inf-001-execution-path.yml` | neu | Workflow der statischen Prüfung |
| `Tests/Runtime/run_gate_b_pilots.py` | geändert | Zielwahl über `--target` |
| `Tests/Runtime/run_adv008_opt015_opt016.py` | geändert | Zielwahl über `--target` |
| `Tests/Runtime/run_framework_sql_matrix.py` | geändert | Primitive delegieren an das Zielmodul |
| `Demos/00_Framework/Tools/sqlcmd_process.py` | geändert | plattformunabhängiger Start eines Python-Shims |
| drei Runtime-Workflows | geändert | Runner-Auswahl über `SQLPERF_RUNTIME_RUNNER`, erweiterte Pfadfilter |

## 3. Technische Korrekturen während der Umsetzung

| Befund | Wirkung | Behebung |
|---|---|---|
| Ein als `--sqlcmd` übergebener Python-Shim war unter Windows nicht startbar (`WinError 193`). | Der Orchestrierungs-Selbsttest war auf Windows nicht ausführbar; der Docker-Proxy blieb auf POSIX begrenzt. | Der Shim wird über den laufenden Interpreter gestartet (`DEC-048`). Ein `.cmd`-Launcher schied aus, weil `cmd.exe` das Trennzeichenargument als Pipe interpretiert. |
| Ohne gesetztes `SQLCMDPASSWORD` ersetzte die Diagnoseausgabe den Leerstring. | Jedes einzelne Zeichen einer Fehlermeldung wurde mit der Maske umgeben und die Meldung damit unlesbar. | Zentrale Funktion `redact()` mit Prüfung auf ein gesetztes Kennwort. |
| Die Pfadfilter der Runtime-Workflows zählen ihre Auslöser einzeln auf. | Eine Änderung an der neuen gemeinsamen Abhängigkeit hätte den Laufzeitnachweis nicht ausgelöst. | `execution_target.py` und `host_sqlcmd_target.py` in beide Filter aufgenommen. |

## 4. Sicherheits- und Datenschutzstatus

- Kennwörter werden ausschließlich über `SQLCMDPASSWORD` übergeben. Kein Pfad setzt ein Kennwort als Argument.
- Ein Lauf gegen das Ziel `host` verlangt `--confirm-disposable-instance`, weil er Datenbanken anlegt und löscht (`DEC-051`).
- Das Vertrauen in ein selbstsigniertes Serverzertifikat ist **nicht** voreingestellt. Es wird über `SQLPERF_HOST_TRUST_SERVER_CERTIFICATE=1` einzeln freigegeben.
- Das How-to verwendet ausschließlich neutrale Platzhalter und beschreibt die Eingabe des Kennworts ohne Kommandozeilenhistorie.
- Der Repository-Privacy-Scan ist grün.
- Die statischen Jobs der Workflows bleiben fest auf GitHub-gehosteten Runnern; nur die Runtimejobs sind parametrisiert.

## 5. Abnahmekriterien

| Kriterium | Stand |
|---|---|
| Alle statischen Validatoren grün | erfüllt (16 von 16) |
| `validate_inf_001_execution_path.py` erkennt eine Verletzung | erfüllt (Negativtest gegen die Runner-Variable) |
| Ausgabekontrakt der Runner unverändert erweitert | erfüllt (`GATE_B_SUMMARY`, `ADV008_SUMMARY` behalten Präfix und Feldfolge, ergänzt um `target=`) |
| How-to deckt den Pflichtinhalt aus Abschnitt 13.4 | erfüllt (neun Themen statisch geprüft) |
| `--target docker` regressionsfrei | **offen** – Nachweis nur über die GitHub-gehosteten Runtime-Workflows |
| Laufnachweis gegen eine vorhandene Instanz | **offen** – erfordert eine Wegwerfinstanz mit Anmeldedaten |

## 6. Statusgrenze

Der Schnitt ist implementiert und statisch abgenommen. Er ist **nicht** runtimevalidiert. Die beiden offenen Kriterien aus Abschnitt 5 entscheiden über den Übergang nach `VALIDATED`.

Der Arbeitsplatz, auf dem die Umsetzung erfolgte, verfügt weder über Docker noch über eine SQL-Server-Instanz. Beide Nachweise waren dort nicht führbar.

## 7. Abgrenzung

Nicht enthalten sind `INF-002` bis `INF-006`, Änderungen an `SQL_Server_Lab`, die Umsetzung von `LABSCN-003` und die fachlichen `ADV-008`-Schnitte.

Die Framework-Matrix bleibt an das Ziel `docker` gebunden, weil sie Query Store und Extended Events auf Serverebene schaltet (`DEC-050`).

## 8. Nächste Schritte

1. Ergebnis der Runtime-Workflows für `--target docker` prüfen und hier eintragen.
2. Laufnachweis gegen eine vorhandene Instanz erbringen: `OPT-002` und `QRY-001` je zweimal einschließlich Cleanup-Prüfung.
3. `CON-004` gegen eine vorhandene Instanz als Risikonachweis für die Mehrsitzungsorchestrierung. Scheitert der Lauf, wird die Demo für das Ziel `host` als nicht unterstützt dokumentiert.
