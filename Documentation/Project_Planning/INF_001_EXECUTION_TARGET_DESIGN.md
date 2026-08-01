# INF-001 – Ausführungsziele der Schulungsbeispiele

| Merkmal | Wert |
|---|---|
| Status | `DESIGNED` |
| Stand | 2026-08-01 |
| Arbeitspaket | `INF-001` |
| Welle | 10 |
| Verbindliche Grundlage | [`MASTER_IMPLEMENTATION_PLAN.md`](MASTER_IMPLEMENTATION_PLAN.md) Abschnitt 13 |
| Folgeschritte | Entkopplung der Runtime-Runner, Testumgebungs-How-to, Runner-Topologie |

## 1. Zweck

Abschnitt 13.2 des Masterplans definiert eine fünfstufige Entscheidungsleiter für den Ausführungspfad einer Demo. Die Leiter ist fachlich beschlossen, aber technisch nicht abgebildet: Die Runner unter `Tests/Runtime` unterstützen ausschließlich Stufe 3.

Dieses Dokument bildet die Leiter auf drei benennbare Ausführungsziele ab, legt ihre Gate-Relevanz fest und grenzt ab, welche Stufen ohne zusätzliche Infrastruktur nicht erreichbar sind.

## 2. Verifizierter Ausgangsbefund

| Befund | Fundstelle | Wirkung |
|---|---|---|
| Die Docker-Kopplung liegt in drei privaten Funktionen der Framework-Matrix. | `Tests/Runtime/run_framework_sql_matrix.py`, `_container_sqlcmd`, `_run_sql`, `_verify_engine` | Jeder Runner erbt die Containerbindung. |
| `_run_sql` setzt Verbindung, Anmeldung und Zertifikatsverhalten fest. | dieselbe Datei, `docker exec … -S localhost -U sa -C` | Weder Server noch Benutzername sind wählbar. |
| Die Gate-B- und ADV-008-Runner importieren diese privaten Funktionen und setzen `--server localhost` fest. | `Tests/Runtime/run_gate_b_pilots.py`, `Tests/Runtime/run_adv008_opt015_opt016.py` | Ein Lauf gegen eine vorhandene Instanz ist nicht vorgesehen. |
| Der Framework-Kommandobau erzeugt kein `-C`. | `Demos/00_Framework/Tools/sqlcmd_process.py`, `build_sqlcmd_command` | Gegen eine Instanz mit selbstsigniertem Zertifikat schlägt der Verbindungsaufbau fehl. Der Docker-Proxy ergänzt `-C` selbst. |
| Die Matrix erzwingt `MinimumMajorVersion` gleich `MaximumMajorVersion` sowie feste Compatibility Levels im Preflight. | `Tests/Runtime/run_framework_sql_matrix.py`, `_test_qry_database` | Auf einer vorhandenen Instanz muss die tatsächliche Version ermittelt statt vorgegeben werden. |
| Ein als `--sqlcmd` übergebener Python-Shim ist unter Windows nicht direkt startbar. | empirisch geprüft; `OSError: [WinError 193]` | Der vorhandene Docker-Proxy und jeder künftige Shim funktionieren nur auf POSIX-Systemen. |
| Ein Umweg über einen `.cmd`-Launcher ist nicht tragfähig. | empirisch geprüft | Das Trennzeichenargument der Framework-Aufrufe wird von `cmd.exe` als Pipe interpretiert. |

## 3. Ausführungsziele

| Ziel | Abgedeckte Stufen nach 13.2 | Umgebung | Verwendung |
|---|---|---|---|
| `local-host` | 1 und 2 | vorhandene SQL-Server-Instanz auf einem Entwickler- oder Schulungshost | Standardpfad für Entwicklung, Fehlersuche und Teilnehmerbetrieb |
| `github-hosted` | 3 | GitHub-gehosteter Runner mit containerisierter Einzelinstanz | verbindliche Versions- und Regressionsmatrix |
| `key18-perf` | 4 und 5 | dedizierter externer Runner mit Hyper-V, Docker und Podman | Windows-, OS-, Storage-, Ressourcen- und Mehrinstanzanforderungen |

Es gilt die niedrigste ausreichende Stufe. Ein verfügbares höheres Ziel begründet für sich genommen keine Verwendung.

## 4. Zuordnung der Sicherheitsstufen

| Sicherheitsstufe | `local-host` | `github-hosted` | `key18-perf` |
|---|---|---|---|
| Grün | zulässig | zulässig | zulässig |
| Gelb | nur nach ausdrücklicher Bestätigung einer Wegwerfinstanz | zulässig | zulässig |
| Rot | unzulässig | unzulässig | ausschließlich hier zulässig |

Der Schutz der Zielinstanz folgt dem Namensschema aus `FWK-002`. Ein Lauf gegen `local-host` darf ausschließlich Datenbanken mit dem Präfix `SQLPERF_` anlegen, verändern oder entfernen.

## 5. Evidenz- und Gate-Regel

Gate-Evidenz entsteht ausschließlich auf `github-hosted`, weil nur dort die Versionsmatrix 2019, 2022 und 2025 gemeinsam nachweisbar ist. Ein Einzelhost kann diese Matrix nicht garantieren.

Läufe gegen `local-host` sind Entwicklungs- und Fehlersuchevidenz. Sie werden in Reviews nicht als Nachweis einer Gate-Bedingung geführt.

Damit die Herkunft eines Laufs maschinenlesbar bleibt, führen die Zusammenfassungszeilen der Runner künftig zusätzlich das verwendete Ziel. Präfix und bestehende Feldreihenfolge bleiben unverändert.

## 6. Runner `Key18_Perf`

Die Stufen 4 und 5 sowie die Bündel `INF-004` bis `INF-006` setzen einen dedizierten externen Runner voraus. Auf den derzeit verwendeten Arbeitsplätzen kann kein selbstgehosteter Runner installiert werden; GitHub-gehostete Runner bleiben verfügbar.

Bis dieser Runner bereitsteht, gilt:

- Stufe 4 und Stufe 5 werden nicht implementiert.
- Rote Szenarien einschließlich `RES-003` bleiben zurückgestellt.
- Ein `RUNNER_ASSISTED`-Teilnehmerablauf wird nicht umgesetzt. Diese Einschränkung ist ohne Wirkung auf `LABSCN-002`, weil dort verbindlich die kleinste ausreichende Orchestrierungsstufe gilt und `CON-004` bereits auf `MANUAL` festgelegt ist.

Die Anforderungen an den Runner werden getrennt in `Documentation/Architecture/RUNNER_TOPOLOGY.md` beschrieben.

## 7. Abgrenzung

Nicht Bestandteil von `INF-001` sind die Bündel `INF-002` bis `INF-006`, Änderungen an `SQL_Server_Lab`, die Umsetzung von `LABSCN-003` sowie die fachlichen `ADV-008`-Schnitte.

## 8. Folgearbeiten

1. Ausführungsziel in den Runtime-Runnern auswählbar machen und die Containerbindung in ein eigenes Modul ziehen.
2. Python-Shims plattformunabhängig starten.
3. Testumgebungs-How-to nach dem Pflichtinhalt aus Abschnitt 13.4 des Masterplans erstellen.
4. Runner-Topologie und Anforderungen an `Key18_Perf` dokumentieren.
5. Statische Prüfung des Ausführungspfads ergänzen.
