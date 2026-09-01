# Aktueller Ausführungsstand

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-09-01 |
| geprüfter Repository-Basisstand | `b9a1ac373cd42015509069787e0c6646a7a62d22` auf `origin/main` |
| geprüfter Runtime-Stand | `782799e` aus Pull Request 42; `OPT-017`-Matrix vollständig grün |
| Fachliche Hauptwelle | `ADV-008` und `W-COV-001` vollständig runtimevalidiert |
| Abgeschlossene Folgepakete | `W2-002`, `ADV-009`, `ADV-010`, `LABSCN-002`, `LABSCN-004`, `INF-002`, `INF-003` und `LABINT-003` `VALIDATED` |
| Szenariowelle | `CON-004` und `DGN-005` – Project Adapter `0.1` und vollständiger Docker-/Podman-Lifecycle auf SQL Server 2025 validiert |
| Folgeplanung | [NEXT_DEVELOPMENT_WAVES.md](NEXT_DEVELOPMENT_WAVES.md) |
| Zweck | kanonischer operativer Einstiegspunkt für Nachweisstand, offene Gates und nächste Schnitte |

## 1. Verifizierter Repository-Stand

Der Repository-Basisstand war zu Beginn der Verarbeitung sauber. Für den korrigierten `OPT-017`-Stand liefen die betroffenen statischen Validatoren, Runner-Selbsttests, `git diff --check` und der Privacy-Scan erfolgreich; letzterer meldete `PASS (files=632; text=621; office=1; archives=0; approved_immutable=1)`.

Die fachlichen Runtime-Nachweise stammen aus den verlinkten GitHub-Actions-Läufen. Die Läufe 33222989681, 33222989682 und 33222989644 prüfen den in `origin/main` enthaltenen Commit `6fd2b1d5170f7658cf0b86ee05314f2ab543adc7`. Pull Request 42 prüft `OPT-017` auf dem unveränderlichen Head `782799e`.

## 2. Runtime-Nachweisstand der produktiven Demos

| Demo | Ergebnis | Status |
|---|---|---|
| `OPT-015` | Plan- und Statistikevidenz, zwei vollständige Läufe auf SQL Server 2019, 2022 und 2025 | `VALIDATED` |
| `OPT-016` | Outer References, Rebinds, Rewinds und Performance Spool, zwei vollständige Läufe auf 2019, 2022 und 2025 | `VALIDATED` |
| `QRY-013` | [Actions-Lauf 30699410795](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30699410795): zwei Docker-basierte Läufe auf 2019, 2022 und 2025 | `VALIDATED` |
| `OPT-009` | [Actions-Lauf 30701731564](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30701731564): 2022/2025 erfolgreich, 2019 erwartungsgemäß `SKIP_VERSION` | `VALIDATED` |
| `OPT-010` | [Actions-Lauf 30702590969](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30702590969): 2025 erfolgreich, 2019/2022 erwartungsgemäß `SKIP_VERSION` | `VALIDATED` |
| `OPT-013` | Gate-B-Nachweis | `VALIDATED` |
| `QRY-001` | Framework- und Lab-Nachweis | `VALIDATED` |
| `OPT-002` | Framework- und Lab-Nachweis | `VALIDATED` |
| `CON-004` | fachliche Demo und Szenariokandidat | `VALIDATED` |
| `QRY-004` | [Actions-Lauf 33222989681](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989681): je zwei vollständige Läufe auf 2019/2022/2025; erwartete `WARN_EMPIRICAL_VARIANCE` ohne Vertrags- oder Cleanup-Fehler | `VALIDATED` |
| `DGN-003`, `DGN-005` | [Actions-Lauf 33222989682](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989682): je zwei `PASS/OK` auf 2019/2022/2025 | `VALIDATED` |
| `OPT-017` | [Actions-Lauf 33447840232](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33447840232): je zwei `PASS/OK` auf 2019/2022/2025 mit Actual DOP, Exchange, positiver Threadarbeit, serieller Gegenprobe und Cleanup | `VALIDATED` |
| `OPT-003`, `OPT-005` | Statistik-Sampling/Skew sowie Ascending-Key-/Pflegevertrag; je zwei lokale Docker-Läufe auf 2019/2022/2025 mit `PASS` | `VALIDATED` |
| `CON-006` | Deadlock-Zyklus, Fehler 1205, Graph und geordnete Gegenprobe; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `CON-009` | [Actions-Lauf 33222989644](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989644): TempDB-Kostenklassen auf 2019/2022/2025 jeweils zweimal `PASS/OK` | `VALIDATED` |
| `IDX-006`, `IDX-010` | Rowstore-Messkette je zweimal mit fachlich akzeptierter Warnung; klassische Columnstore-Segmente je zweimal `PASS` auf allen Zielversionen | `VALIDATED` |
| `STL-008`, `STL-009` | rote VLF-/Growth-Lane und gelber Commit-/WRITELOG-Schnitt; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `RES-007` | Task-, Request- und Instanz-Waitscope mit Gegenprobe; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |

`QRY-004` bleibt fachlich bewusst warnungsfähig. `WARN_EMPIRICAL_VARIANCE` behauptet keinen nicht gemessenen Performancevorteil und verhindert die Runtimefreigabe nicht, sofern die Matrix vollständig läuft und Ergebnis-, Sicherheits-, Wiederverwendungs- und Cleanup-Verträge erfüllt sind. Genau diesen Zustand belegt Lauf 33222989681.

## 3. Lab-Integration und Szenarien

`LABSCN-001` und `DEC-044` bleiben verbindlich:

- `SQL_Server_Lab` provisioniert die technische Umgebung; dieses Repository beschreibt Lernziel, Setup, synthetische Daten, Benutzeraktionen, Beobachtungen und Reset.
- Ein interaktives Szenario endet nach der Vorbereitung in `READY_FOR_USER`; Reset und Entfernen sind getrennte, bewusste Benutzeraktionen.
- Die automatisierte Matrix ist ein Qualitätssicherungsinstrument und kein Ersatz für den Benutzerworkflow.
- Änderungen an `SQL_Server_Lab` benötigen eine konkret nachgewiesene fehlende Fähigkeit und ausdrückliche Freigabe.

`LABSCN-002` inventarisiert alle 22 produktiven Demos vollständig und wird
gegen den aktiven Demo-Katalog validiert. `LABSCN-003` setzt `CON-004` als
ersten vollständigen Vertical Slice um; `LABSCN-005` ergänzt `DGN-005` als
zweiten freigegebenen Slice. Beide versionierten Project Adapter `0.1`
begrenzen ihren interaktiven Pfad auf SQL Server 2025 Linux in einer isolierten
Docker- oder Podman-Wegwerfumgebung und besitzen getrennte Preflight-, Install-,
Validate- und Cleanup-Entrypoints.

```text
Auswahl -> Provisionierung -> fachliche Vorbereitung -> READY_FOR_USER
        -> interaktive Durchführung -> Reset -> Remove
```

Die lokalen Nachweise vom 2026-08-30 bestätigten denselben vollständigen
Lifecycle auf Docker (RunId `30b69f0b-b140-47e6-8c90-c05e38bd7c99`) und Podman
(RunId `f80f7d82-934b-4c7c-9d2a-a80e975d92d5`): Start und Reset endeten
jeweils als `READY_FOR_USER`; der anschließende markergebundene Datenbank-,
Container- und Volume-Abbau einschließlich Abschluss des aktiven
Szenario-States endete als `REMOVED`. Der Lab-Core behält ausschließlich den
nicht aktiven Auditdatensatz des entfernten Runs. Der Podman-Cleanup ließ eine
bereits vorhandene, nicht zum Run gehörende Ressource unverändert gesund.

Der `DGN-005`-Folgeslice bestand am 2026-09-01 denselben Lifecycle auf Docker
(RunId `d5143f2a-9f18-49fa-8e9f-b91604993252`) und Podman (RunId
`82791985-b76a-4594-a5be-bab014907f7d`). Beide Provider führten Demonstration,
Observation, Mitigation und Comparison mit `PASS/OK` aus und erreichten nach
dem Reset erneut `READY_FOR_USER`; die markergefilterte, speicherbegrenzte
Extended-Events-Session sowie Datenbank, Container und Volume wurden danach
vollständig entfernt.

## 4. Gate-Status

- Gate V0 – Quellenfreigabe: `VALIDATED`.
- Gate V1 – Curriculumfreigabe: `VALIDATED`.
- Gate V2 – Designfreigabe: `VALIDATED`.
- Gate V3 – Runtimefreigabe: `VALIDATED`; alle freigegebenen `ADV-008`- und `W-COV-001`-Demos besitzen den zutreffenden Matrixnachweis.
- Gate V4 – Lehrmittelfreigabe: `VALIDATED`; Masterdeck und Profile bestanden Notes-, Manifest-, Custom-Show-, Build-, Render-, Metadaten-, Privacy- und Branding-Abnahme.
- `LABSCN-001`: `DECIDED` und im Repository verankert.
- `LABSCN-002`: `VALIDATED`; 22 von 22 produktiven Demos besitzen den vollständigen Inventarvertrag.
- `LABSCN-003`: `VALIDATED` für den vollständigen SQL-Server-2025-Lifecycle auf Docker und Podman.
- `LABSCN-004`: `VALIDATED`; Auswahl, Start, Übergabe, Reset und Remove sind standardisiert dokumentiert und statisch abgesichert.
- `LABSCN-005/DGN-005`: `VALIDATED` als zweiter interaktiver SQL-Server-2025-Slice auf Docker und Podman.
- `LABINT-001`: `VALIDATED` als nachgeordneter Testkatalog.
- `LABINT-002`: `VALIDATED` für Start, `READY_FOR_USER`, Reset und Remove von `CON-004` auf Docker.
- `LABINT-003`: `VALIDATED` für die freigegebenen Slices `QRY-001`, `CON-004` und `DGN-005`; Docker-/Podman-Parität ist praktisch belegt.
- `INF-002`/`INF-003`: `VALIDATED`; beide Provider-Preflights melden `RESOURCE_OK`, Quickstart und Recovery sind dokumentiert.

`ADV-006` und `ADV-007` bleiben als `DESIGNED`-Verträge vollständig: Die zugehörigen LAB-VP3-/VP4-Grenzen, Feature-Skips und Diagnoseabhängigkeiten sind dokumentiert, ihre fachliche Umsetzung erfolgt erst in den jeweiligen Folgewellen.

## 5. Nächste fachliche Verarbeitung

Die verbindliche Reihenfolge und die Akzeptanzkriterien stehen in [NEXT_DEVELOPMENT_WAVES.md](NEXT_DEVELOPMENT_WAVES.md). Kurzfristig ist die Reihenfolge:

1. Nächsten `LABSCN-005`-Kandidaten erst nach eigenem Detailreview und Quellenfreigabe auswählen; die Kandidatenanalyse priorisiert `CON-006` nach dem abgeschlossenen Query-Store/XE-Schnitt.
2. `LABINT-004` erst aktivieren, wenn ein weiterer gelber Slice samt Safety- und Szenariofreigabe eine neue Matrixaussage benötigt.
3. Docker-/Podman-Ressourcen-, Netzwerk-, Hyper-V- oder gemischte Topologien nur bei einer konkret nachgewiesenen fachlichen Abhängigkeit bearbeiten.
4. Änderungen an `SQL_Server_Lab` bleiben ohne konkrete Fähigkeitslücke und ausdrückliche Freigabe gesperrt.

## 6. Sicherheits-, Datenschutz- und Quellenstatus

- Szenariodefinitionen enthalten nur synthetische Daten, relative Projektpfade, öffentliche Versionsbezeichnungen und generische Rollen.
- Gelbe und rote Szenarien behalten ihre bestehenden Safety-Gates; `RES-003` benötigt zusätzlich dedizierte Wegwerfinfrastruktur, High-Impact-Bestätigung, Kill-Switch und Laufzeitbudget.
- `DGN-007` setzt validierte Query-Store- und Extended-Events-Evidenz voraus.
- Der SQL-Server-2025-Delta-Review ist in `SQL_SERVER_2025_DELTA_REVIEW.md` abgeschlossen: CE Feedback für Ausdrücke und zeitgebundene XE-Sessions sind in bestehende Verträge übernommen; vier Infrastruktur-/Abhängigkeitsthemen bleiben zurückgestellt, Vector/KI außerhalb des Curriculums.
- Aktuelle Herstellerdokumentation allein ist weiterhin kein Implementierungs- oder Runtime-Nachweis.
