# Aktueller Ausführungsstand

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-08-24 |
| geprüfter Stand auf `origin/main` | `c75d7a25e966d28abeb8225779e7cc48939159fe` |
| Fachliche Hauptwelle | `ADV-008` – neun von zehn produktiven Demos runtimevalidiert; `QRY-004` implementiert, mit offenem Runner-Konflikt |
| Szenariowelle | `LABSCN-002` – Inventar und Schema für die ersten drei Wellen implementiert zur Prüfung |
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
| `QRY-004` | [Actions-Lauf 30699410792](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30699410792): SQL-Phasen und Cleanup erfolgreich, Workflow dennoch wegen `WARN_EMPIRICAL_VARIANCE` fehlgeschlagen | `IMPLEMENTED` |

`QRY-004` ist ausdrücklich kein Runtime-Nachweis: Der Runner muss den Konflikt zwischen erfolgreicher Ausführung (`returncode=0`) und der Workflow-Bewertung des Warnsummaries auflösen und anschließend die 2019/2022/2025-Matrix erneut laufen.

## 3. Lab-Integration und Szenarien

`LABSCN-001` und `DEC-044` bleiben verbindlich:

- `SQL_Server_Lab` provisioniert die technische Umgebung; dieses Repository beschreibt Lernziel, Setup, synthetische Daten, Benutzeraktionen, Beobachtungen und Reset.
- Ein interaktives Szenario endet nach der Vorbereitung in `READY_FOR_USER`; Reset und Entfernen sind getrennte, bewusste Benutzeraktionen.
- Die automatisierte Matrix ist ein Qualitätssicherungsinstrument und kein Ersatz für den Benutzerworkflow.
- Änderungen an `SQL_Server_Lab` benötigen eine konkret nachgewiesene fehlende Fähigkeit und ausdrückliche Freigabe.

`LABSCN-002` hat Inventar und Definitionsschema für die ersten drei Wellen geliefert. Der nächste geeignete Vertical Slice ist `CON-004`; er ist verbindlich `YELLOW` und benötigt eine isolierte Wegwerfumgebung. Der vollständige Lifecycle bleibt erst mit `LABSCN-003` fällig.

```text
Auswahl -> Provisionierung -> fachliche Vorbereitung -> READY_FOR_USER
        -> interaktive Durchführung -> Reset -> Remove
```

## 4. Gate-Status

- Gate V0 – Quellenfreigabe: `VALIDATED`.
- Gate V1 – Curriculumfreigabe: `VALIDATED`.
- Gate V2 – Designfreigabe: `VALIDATED`.
- Gate V3 – Runtimefreigabe: `PARTIAL`; alle oben als `VALIDATED` markierten Demos sind belegt, `QRY-004` bleibt offen.
- Gate V4 – Lehrmittelfreigabe: offen; die visuelle Renderprüfung der Vertiefungsfolien steht aus.
- `LABSCN-001`: `DECIDED` und im Repository verankert.
- `LABSCN-002`: `IMPLEMENTED_FOR_REVIEW`; die vollständige Szenarioabdeckung ist noch nicht erreicht.
- `LABINT-001`: `VALIDATED` als nachgeordneter Testkatalog.
- `LABINT-002` und `LABINT-003`: technischer `QRY-001`-Vorläufer und Provider-Parität für SQL Server 2025 sind nachgewiesen; weitere Szenarien und Versionen bleiben offen.

`ADV-006` und `ADV-007` bleiben als `DESIGNED`-Verträge vollständig: Die zugehörigen LAB-VP3-/VP4-Grenzen, Feature-Skips und Diagnoseabhängigkeiten sind dokumentiert, ihre fachliche Umsetzung erfolgt erst in den jeweiligen Folgewellen.

## 5. Nächste fachliche Verarbeitung

Die verbindliche Reihenfolge und die Akzeptanzkriterien stehen in [NEXT_DEVELOPMENT_WAVES.md](NEXT_DEVELOPMENT_WAVES.md). Kurzfristig ist die Reihenfolge:

1. `QRY-004`-Runner-Konflikt korrigieren und Matrix erneut validieren.
2. Query-Store-/Extended-Events-Pilot (`DGN-003`/`DGN-005`) als belastbare Evidenz für diagnoseabhängige Schnitte aufbauen.
3. `CON-004` als gelben, isolationspflichtigen interaktiven Vertical Slice umsetzen.
4. `OPT-017` getrennt implementieren und validieren.
5. Quellen- und Delta-Review für relevante SQL-Server-2025-Funktionen durchführen, bevor daraus neue Lerninhalte entstehen.
6. `PRS-012`/`TST-011` sowie danach `PRS-013`/`TST-012` inklusive visueller Renderprüfung abschließen.

## 6. Sicherheits-, Datenschutz- und Quellenstatus

- Szenariodefinitionen enthalten nur synthetische Daten, relative Projektpfade, öffentliche Versionsbezeichnungen und generische Rollen.
- Gelbe und rote Szenarien behalten ihre bestehenden Safety-Gates; `RES-003` benötigt zusätzlich dedizierte Wegwerfinfrastruktur, High-Impact-Bestätigung, Kill-Switch und Laufzeitbudget.
- `DGN-007` setzt validierte Query-Store- und Extended-Events-Evidenz voraus.
- Aktuelle Produktdokumentation wird erst nach einem Source-Register-Delta-Review zu Lehrinhalt; aktuelle Herstellerdokumentation allein ist kein Implementierungsnachweis.
