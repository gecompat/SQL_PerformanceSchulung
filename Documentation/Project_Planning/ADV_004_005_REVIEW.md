# Review – ADV-004 und ADV-005

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-07-26 |
| Pull Request | `#18` |
| Ausgangscommit auf `origin/main` | `1849e2207c67a062cd33e91b184cdc192a784a37` |
| Arbeitspakete | `ADV-004`, `ADV-005` |
| PowerPoint geändert | nein |
| SQL-Demos geändert | nein |

## 1. Umfang

Die Welle entwirft die beiden priorisierten Vertiefungsserien LAB-VP1 und LAB-VP2 vollständig. Sie legt die späteren SQL-Implementierungen fachlich, sicherheitsbezogen und testtechnisch fest, erzeugt jedoch noch keine ausführbaren Demos.

## 2. ADV-004 – LAB-VP1

Der Designvertrag umfasst:

- die didaktische Reihenfolge von `OPT-001` bis `OPT-017`,
- ein gemeinsames deterministisches Datenmodell für Planmechanik,
- `OPT-015` für planweite und operatorbezogene Eigenschaften,
- `OPT-016` für Rebind, Rewind, Outer References und Spools,
- `OPT-017` für parallele Planbereiche, Exchanges und Threadverteilung,
- planformabhängige Skip-Regeln statt erzwungener Optimizerentscheidungen,
- grüne Verträge für `OPT-015` und `OPT-016` sowie ein gelbes Ressourcenprofil für `OPT-017`.

## 3. ADV-005 – LAB-VP2

Der Designvertrag umfasst:

- die didaktische Reihenfolge von `OPT-007` bis `OPT-010`,
- eine deterministische, schiefe Suchdatenverteilung,
- `QRY-013` mit neutralen Clientprofilen statt behaupteter SSMS-/Treiberdefaults,
- die Trennung von Catch-all, `OPTION (RECOMPILE)`, sicher parameterisiertem dynamischem SQL, PSP und OPPO,
- kontrollierte Feature- und Eligibility-Skips für SQL Server 2019, 2022 und 2025,
- das Verbot globaler Cacheleerung und unparametrisierter Wertkonkatenation.

## 4. Gemeinsame Designregeln

Jede spätere Demo besitzt die Phasen Preflight, Setup, Baseline, Problem oder Kontrast, Evidenz, Gegenprobe beziehungsweise Gegenmaßnahme, Vergleich und Cleanup. Exakte Plankosten, Millisekundenwerte und vollständige Planformen sind keine stabilen Golden Values. Ergebnisgleichheit, normalisierte Planattribute, Richtungen, Verhältnisse und begründete Skips bilden den Testvertrag.

## 5. Automatisierte Abnahme

Die statische Prüfung validiert:

- Claim-, Lernziel-, Quellen- und Demoabdeckung,
- Reihenfolge der LAB-Serien,
- Ressourcen-, Risiko- und Versionsverträge,
- verpflichtende Evidenz und Skip-Codes,
- die vollständige Strategieauswahl für `QRY-004`,
- verbotene globale oder datenschutzkritische Aktionen,
- Backlog- und Dokumentationskonsistenz.

Final erfolgreich:

- `Advanced lab design contracts`, Lauf `30214930385`,
- `Curriculum and privacy validation`, Lauf `30214930363`,
- `Framework contracts`, Lauf `30214930319`,
- `W2-001 legacy example classification`, Lauf `30214930361`.

## 6. Nicht durchgeführte Prüfungen

Eine SQL-Server-Runtime-Matrix wurde nicht ausgeführt, weil keine SQL-Datei und keine ausführbare Demo implementiert wurde. Ein PowerPoint-Render war nicht erforderlich, weil das Masterdeck unverändert blieb. Runtime-, Planform- und Ressourcenvalidierung folgen erst während `ADV-008`.

## 7. Statusgrenze

`ADV-004` und `ADV-005` sind fachlich und statisch `VALIDATED`. `OPT-015`, `OPT-016`, `OPT-017`, `QRY-013` sowie die Erweiterung von `QRY-004` bleiben bis zur Umsetzung und Runtimeprüfung ausdrücklich `PLANNED` beziehungsweise `DESIGNED`; sie sind nicht `IMPLEMENTED`.

## 8. Nächste fachliche Schritte

`ADV-006` und `ADV-007` können beginnen. Erste SQL-Implementierungen werden anschließend in kleinen, voneinander unabhängigen Schnitten unter `ADV-008` umgesetzt. Parallel bleiben `PRS-012`/`TST-011`, W2-002-Teilpakete und die Query-Store-/XE-Pilotvalidierung offen.
