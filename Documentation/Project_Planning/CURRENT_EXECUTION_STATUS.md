# Aktueller Ausführungsstand

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-08-30 |
| geprüfter Stand auf `origin/main` | `c75d7a25e966d28abeb8225779e7cc48939159fe` |
| Fachliche Hauptwelle | `W-COV-001` – acht Demos runtimevalidiert; `CON-009` mit offener SQL-Server-2019-Evidenz |
| Szenariowelle | `LABSCN-003` – Project Adapter `0.1` und vollständiger Docker-Lifecycle auf SQL Server 2025 validiert; Podman-Parität offen |
| Folgeplanung | [NEXT_DEVELOPMENT_WAVES.md](NEXT_DEVELOPMENT_WAVES.md) |
| Zweck | kanonischer operativer Einstiegspunkt für Nachweisstand, offene Gates und nächste Schnitte |

## 1. Verifizierter Repository-Stand

Der lokale Prüfstand auf dem oben genannten Commit ist sauber. Die statischen Validatoren und neun Unit-Tests liefen am 2026-08-24 erfolgreich. Der Privacy-Scan meldete `PASS (files=354; text=345; office=1; archives=0; approved_immutable=1)`.

Es bestehen keine offenen Pull Requests oder Issues. Die fachlichen Runtime-Nachweise stammen aus den verlinkten GitHub-Actions-Läufen; Demo, Runner und Workflow der als validiert markierten Einträge blieben bis zum geprüften Commit unverändert.

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
| `QRY-004` | Runner wertet `PASS`, `WARN` und kontrollierte `SKIP`-Codes wahrheitsgetreu aus; der ältere Actions-Lauf 30699410792 ist kein Freigabenachweis, die neue Zielmatrix bleibt offen | `IMPLEMENTED` |
| `OPT-017` | Gelbes `PARALLEL`-Paket mit balancierter und konzentrierter Verteilung, Actual-DOP-/Exchange-/Thread-Evidenz, serieller Gegenprobe und zweifachem Matrix-Runner; Runtime-Matrix noch offen | `IMPLEMENTED` |
| `OPT-003`, `OPT-005` | Statistik-Sampling/Skew sowie Ascending-Key-/Pflegevertrag; je zwei lokale Docker-Läufe auf 2019/2022/2025 mit `PASS` | `VALIDATED` |
| `CON-006` | Deadlock-Zyklus, Fehler 1205, Graph und geordnete Gegenprobe; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `CON-009` | TempDB-Kostenklassen; 2022/2025 je zwei `PASS`, 2019 zweimal `WARN_EMPIRICAL_VARIANCE` wegen fehlender interner Task-Allokation | `IMPLEMENTED` |
| `IDX-006`, `IDX-010` | Rowstore-Messkette je zweimal mit fachlich akzeptierter Warnung; klassische Columnstore-Segmente je zweimal `PASS` auf allen Zielversionen | `VALIDATED` |
| `STL-008`, `STL-009` | rote VLF-/Growth-Lane und gelber Commit-/WRITELOG-Schnitt; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `RES-007` | Task-, Request- und Instanz-Waitscope mit Gegenprobe; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |

`QRY-004` ist ausdrücklich noch nicht runtimefreigegeben: Der Runnerkonflikt ist behoben und regressionsgetestet, aber die zweifache 2019/2022/2025-Matrix auf dem korrigierten Stand wurde noch nicht ausgeführt.

## 3. Lab-Integration und Szenarien

`LABSCN-001` und `DEC-044` bleiben verbindlich:

- `SQL_Server_Lab` provisioniert die technische Umgebung; dieses Repository beschreibt Lernziel, Setup, synthetische Daten, Benutzeraktionen, Beobachtungen und Reset.
- Ein interaktives Szenario endet nach der Vorbereitung in `READY_FOR_USER`; Reset und Entfernen sind getrennte, bewusste Benutzeraktionen.
- Die automatisierte Matrix ist ein Qualitätssicherungsinstrument und kein Ersatz für den Benutzerworkflow.
- Änderungen an `SQL_Server_Lab` benötigen eine konkret nachgewiesene fehlende Fähigkeit und ausdrückliche Freigabe.

`LABSCN-002` hat Inventar und Definitionsschema für die ersten drei Wellen geliefert. `LABSCN-003` setzt `CON-004` als ersten vollständigen Vertical Slice um. Der versionierte Project Adapter `0.1` begrenzt den Pfad auf SQL Server 2025 Linux in einer isolierten Docker- oder Podman-Wegwerfumgebung und besitzt getrennte Preflight-, Install-, Validate- und Cleanup-Entrypoints.

```text
Auswahl -> Provisionierung -> fachliche Vorbereitung -> READY_FOR_USER
        -> interaktive Durchführung -> Reset -> Remove
```

Der lokale Docker-Nachweis vom 2026-08-30 (RunId `30b69f0b-b140-47e6-8c90-c05e38bd7c99`) bestätigte Start und Reset jeweils als `READY_FOR_USER` sowie den anschließenden markergebundenen Datenbank-, Container- und Volume-Abbau einschließlich Abschluss des aktiven Szenario-States als `REMOVED`. Der Lab-Core behält ausschließlich den nicht aktiven Auditdatensatz des entfernten Runs. Podman war auf dem Prüfhost nicht installiert und bleibt deshalb ohne Runtime-Aussage.

## 4. Gate-Status

- Gate V0 – Quellenfreigabe: `VALIDATED`.
- Gate V1 – Curriculumfreigabe: `VALIDATED`.
- Gate V2 – Designfreigabe: `VALIDATED`.
- Gate V3 – Runtimefreigabe: `PARTIAL`; alle oben als `VALIDATED` markierten Demos sind belegt, `QRY-004` bleibt offen.
- Gate V4 – Lehrmittelfreigabe: `VALIDATED`; Masterdeck und Profile bestanden Notes-, Manifest-, Custom-Show-, Build-, Render-, Metadaten-, Privacy- und Branding-Abnahme.
- `LABSCN-001`: `DECIDED` und im Repository verankert.
- `LABSCN-002`: `IMPLEMENTED_FOR_REVIEW`; die vollständige Szenarioabdeckung ist noch nicht erreicht.
- `LABSCN-003`: `VALIDATED` für den vollständigen SQL-Server-2025-Docker-Lifecycle; Podman-Parität ist nachgeordnet offen.
- `LABINT-001`: `VALIDATED` als nachgeordneter Testkatalog.
- `LABINT-002`: `VALIDATED` für Start, `READY_FOR_USER`, Reset und Remove von `CON-004` auf Docker.
- `LABINT-003`: `PARTIAL`; die frühere `QRY-001`-Provider-Parität ist nachgewiesen, für den neuen `CON-004`-Adapter bleibt Podman offen.

`ADV-006` und `ADV-007` bleiben als `DESIGNED`-Verträge vollständig: Die zugehörigen LAB-VP3-/VP4-Grenzen, Feature-Skips und Diagnoseabhängigkeiten sind dokumentiert, ihre fachliche Umsetzung erfolgt erst in den jeweiligen Folgewellen.

## 5. Nächste fachliche Verarbeitung

Die verbindliche Reihenfolge und die Akzeptanzkriterien stehen in [NEXT_DEVELOPMENT_WAVES.md](NEXT_DEVELOPMENT_WAVES.md). Kurzfristig ist die Reihenfolge:

1. `QRY-004`-Runner-Konflikt korrigieren und Matrix erneut validieren.
2. Query-Store-/Extended-Events-Pilot (`DGN-003`/`DGN-005`) als belastbare Evidenz für diagnoseabhängige Schnitte aufbauen.
3. `CON-004` besitzt den validierten Docker-Vertical-Slice; als nachgeordnete Provider-Evidenz bleibt Podman offen.
4. `OPT-017` getrennt implementieren und validieren.
5. Quellen- und Delta-Review für relevante SQL-Server-2025-Funktionen durchführen, bevor daraus neue Lerninhalte entstehen.
6. `W-PRS-001` ist abgeschlossen.
7. `W-COV-001` ist in der festgelegten Reihenfolge implementiert und für acht Demos runtimevalidiert; als nächster belegpflichtiger Schritt folgt die SQL-Server-2019-Evidenzstabilisierung von `CON-009`.

## 6. Sicherheits-, Datenschutz- und Quellenstatus

- Szenariodefinitionen enthalten nur synthetische Daten, relative Projektpfade, öffentliche Versionsbezeichnungen und generische Rollen.
- Gelbe und rote Szenarien behalten ihre bestehenden Safety-Gates; `RES-003` benötigt zusätzlich dedizierte Wegwerfinfrastruktur, High-Impact-Bestätigung, Kill-Switch und Laufzeitbudget.
- `DGN-007` setzt validierte Query-Store- und Extended-Events-Evidenz voraus.
- Der SQL-Server-2025-Delta-Review ist in `SQL_SERVER_2025_DELTA_REVIEW.md` abgeschlossen: CE Feedback für Ausdrücke und zeitgebundene XE-Sessions sind in bestehende Verträge übernommen; vier Infrastruktur-/Abhängigkeitsthemen bleiben zurückgestellt, Vector/KI außerhalb des Curriculums.
- Aktuelle Herstellerdokumentation allein ist weiterhin kein Implementierungs- oder Runtime-Nachweis.
