# ADV-009 – Folienspezifikation Modul M03, Lernziel `LO-M03-07`

| Merkmal | Wert |
|---|---|
| Paket | `ADV-009` |
| Status | `SPECIFIED` |
| Modul | M03 – Optimizer, Statistiken und Pläne |
| Lernziel | `LO-M03-07` |
| Claims | `ADV-CLM-013`, `ADV-CLM-014`, `ADV-CLM-015`, `ADV-CLM-016` |
| Kanonische Demo | `QRY-013` |
| Tiefenprofil | `VERTIEFUNG` |
| Testprofil | `TP-RUN` |

## 1. Zweck und Lieferform

Das aktive Foliendeck `Presentations/Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx` ist als `SRC-DECK-001` registriert und in `Tests/Static/validate_privacy_metadata.py` über einen freigegebenen SHA-256-Wert gebunden. Jede Binäränderung entzieht dieser Freigabe die Grundlage und macht die Datenschutzprüfung rot.

Die Erweiterung wird deshalb bewusst auf der Spezifikationsebene geliefert: Dieses Dokument enthält folienfertige Inhalte einschließlich Sprechernotizen und Folienmarkern. Die Übernahme in das Deck ist ein eigener, freigabepflichtiger Schritt unter `ADV-009` und `PRS-012`; dabei wird der freigegebene Hashwert kontrolliert erneuert. Bis dahin bleiben die Claims in `Documentation/Curriculum/TRACEABILITY_MATRIX.md` auf `PLANNED` und ohne aktive Folie.

## 2. Didaktische Einordnung

Die fünf Folien bilden einen zusammenhängenden Vertiefungsbogen: Der Bogen beginnt mit der Diagnosehaltung, führt über die zwei belegbaren Kontextdimensionen und endet mit der Evidenzkette, die in `QRY-013` ausgeführt wird. Er setzt `OPT-007` (Plan-Cache-Grundlagen) und `OPT-008` (klassische Parameter Sensitivity) voraus.

| Reihenfolge | Folien-ID | Claim | Rolle im Bogen |
|---|---|---|---|
| 1 | `SLD-M03-101` | `ADV-CLM-014` | Problemstellung und Diagnosehaltung |
| 2 | `SLD-M03-102` | `ADV-CLM-013` | Dimension Cachekontext |
| 3 | `SLD-M03-103` | `ADV-CLM-015` | Dimension Parameterwert und Planwiederverwendung |
| 4 | `SLD-M03-104` | `ADV-CLM-016` | Vergleich der Informationsquellen des Optimierers |
| 5 | `SLD-M03-105` | alle vier | Evidenzkette und Übergang in `QRY-013` |

## 3. Folie `SLD-M03-101` – Anwendung langsam, Werkzeug schnell

**Kernaussage:** Die Differenz zwischen zwei Clients ist ein Evidenzproblem und erfordert eine mehrdimensionale Kontextdiagnose. (`ADV-CLM-014`)

**Folientext**

- Gleicher Querytext bedeutet nicht gleiche Ausführungsbedingungen.
- Mindestens vier Dimensionen sind zu prüfen: Datenbankkontext, SET-Optionen, Parameterwerte, Compile-Reihenfolge und Planidentität.
- Eine Ein-Ursachen-Hypothese wird erst akzeptiert, wenn die übrigen Dimensionen widerlegt sind.
- Der Vergleich benötigt zwei dokumentierte Sessionprofile, keine Vermutung über Clientdefaults.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-101]` Die verbreitete Formulierung „in der Anwendung langsam, in SSMS schnell" beschreibt eine Beobachtung, keine Ursache. Wir benennen bewusst keine Clientdefaults, weil Treiber- und Werkzeugversionen unterschiedliche Vorgaben setzen. Stattdessen arbeiten wir mit zwei explizit gesetzten, neutralen Sessionprofilen. Das Ziel dieser Folie ist die Haltung: erst Kontext erheben, dann Hypothesen bilden. Die Demo `QRY-013` widerlegt später genau eine solche voreilige Hypothese.

**Quellen:** `SRC-001`, `SRC-027`, `SRC-046` **Demo:** `QRY-013` **Tiefe:** `VERTIEFUNG`

## 4. Folie `SLD-M03-102` – Cachekontext und SET-Optionen

**Kernaussage:** Cachekontext und SET-Optionen können zusätzliche Cacheeinträge für dasselbe Objekt erzeugen. (`ADV-CLM-013`)

**Folientext**

- Der Cacheschlüssel umfasst mehr als den Anweisungstext, unter anderem Datenbankkontext und wirksame SET-Optionen.
- Zwei Clients mit abweichenden SET-Optionen erhalten getrennte Cacheeinträge desselben Objekts.
- Getrennte Einträge bedeuten getrennte Kompilierungen mit möglicherweise unterschiedlichen kompilierten Werten.
- Das fachliche Ergebnis bleibt identisch; unterschiedlich ist der Weg dorthin.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-102]` Sichtbar wird das über `sys.dm_exec_plan_attributes`, insbesondere über das Attribut `set_options`, ausgewertet für ein einzelnes Demoobjekt. Wichtig ist die Reihenfolge der Aussagen: Der zusätzliche Cacheeintrag ist eine gesicherte Beobachtung, ein daraus abgeleiteter Laufzeitunterschied ist es nicht. In `QRY-013` unterscheiden sich die beiden Profile ausschließlich in `ARITHABORT`; das Ergebnis bleibt bitgleich, die Anzahl der Cacheeinträge steigt von eins auf zwei. Eine pauschale Empfehlung zu einer einzelnen SET-Option leiten wir daraus nicht ab.

**Quellen:** `SRC-001`, `SRC-040`, `SRC-046` **Demo:** `QRY-013`, `OPT-007` **Tiefe:** `VERTIEFUNG`

## 5. Folie `SLD-M03-103` – Parameterwert und Planwiederverwendung

**Kernaussage:** Parameter Sensitivity folgt der Planwiederverwendung bei unterschiedlicher Verteilung. (`ADV-CLM-015`)

**Folientext**

- Ein wiederverwendeter Plan wurde für einen konkreten Parameterwert kompiliert.
- Trifft dieser Plan auf eine andere Verteilung, ändert sich die Arbeitsmenge, nicht das Ergebnis.
- Der Effekt tritt auch bei vollständig identischem Sessionkontext auf.
- Damit ist die Parameterdimension unabhängig von der Kontextdimension nachweisbar.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-103]` Diese Folie ist das Gegengewicht zur vorherigen. In der Demo halten wir das Sessionprofil konstant und ändern nur den Parameterwert von einem seltenen auf einen häufigen Wert. Die logischen Lesevorgänge steigen deutlich, obwohl kein zusätzlicher Cacheeintrag entsteht. Genau hier bricht die Hypothese „es liegt an den SET-Optionen" zusammen. Bleibt die Arbeitsmenge in einer Umgebung wider Erwarten gleich, meldet die Demo `WARN_EMPIRICAL_VARIANCE` statt eine Verschlechterung zu behaupten.

**Quellen:** `SRC-007`, `SRC-047` **Demo:** `QRY-013`, `OPT-008` **Tiefe:** `VERTIEFUNG`

## 6. Folie `SLD-M03-104` – Parameter, Variable, Literal und Recompile

**Kernaussage:** Parameter, Variablen, Literale und `OPTION (RECOMPILE)` liefern dem Optimierer unterschiedliche Information. (`ADV-CLM-016`)

**Folientext**

- Parameter: Schätzung anhand des kompilierten Werts, Plan wird wiederverwendet.
- Lokale Variable: kein bekannter Wert zur Kompilierzeit, Schätzung ohne Wertbezug.
- Literal: Wert zur Kompilierzeit bekannt, dafür eigener Cacheeintrag je Wert.
- `OPTION (RECOMPILE)`: Wert zur Kompilierzeit bekannt, dafür Kompilierarbeit bei jeder Ausführung.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-104]` Die vier Varianten sind keine Rangfolge, sondern ein Tauschverhältnis zwischen Planqualität, Wiederverwendung und Kompilierarbeit. Wer die Diagnose aus Folie 101 ernst nimmt, muss wissen, welche Variante im Verdachtsfall tatsächlich vorliegt: Eine Anwendung sendet häufig parametrisierte Aufrufe, ein Werkzeugfenster häufig Literale. Damit unterscheiden sich beide bereits in der Information, die dem Optimierer zur Verfügung steht – unabhängig von jeder SET-Option. Die belastbare Bewertung von `OPTION (RECOMPILE)` erfolgt in `QRY-004` über mehrere Ausführungen, nicht über eine einzelne schnelle Messung.

**Quellen:** `SRC-001`, `SRC-007`, `SRC-045`, `SRC-046` **Demo:** `QRY-004`, `OPT-008` **Tiefe:** `VERTIEFUNG`

## 7. Folie `SLD-M03-105` – Evidenzkette statt Einzelursache

**Kernaussage:** Die Diagnose ist erst abgeschlossen, wenn jede Dimension einzeln belegt oder ausgeschlossen ist.

**Folientext**

- Erheben: Datenbankkontext, wirksame SET-Optionen, Parameterwerte, Planidentität.
- Trennen: Kontextdimension und Parameterdimension getrennt messen.
- Angleichen: genau eine Dimension verändern und erneut messen.
- Bewerten: Ergebnisgleichheit sichern, bevor Laufzeiten verglichen werden.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-105]` Diese Folie leitet unmittelbar in `QRY-013` über. Der Ablauf der Demo ist die Evidenzkette dieser Folie: Baseline mit Profil A, Demonstration mit Profil B, Observation mit Profil A und anderem Parameterwert, Mitigation mit Angleichung genau einer Dimension, Comparison mit erneuter Messung. Entscheidend ist die letzte Zeile: Wir vergleichen erst dann Laufzeiten, wenn alle Proben dieselbe Ergebnischecksumme liefern. Andernfalls vergleichen wir unterschiedliche Arbeiten und nicht unterschiedliche Bedingungen.

**Quellen:** `SRC-001`, `SRC-027`, `SRC-040`, `SRC-046` **Demo:** `QRY-013` **Tiefe:** `VERTIEFUNG`

## 8. Abnahmekriterien für die Deckübernahme

1. Jede Folie erhält im Notizfeld den unveränderten Marker `[SLIDE-ID: SLD-M03-1xx]`.
2. Die vier Claims werden in `Documentation/Curriculum/TRACEABILITY_MATRIX.md` von `PLANNED` auf `KEEP` gesetzt und erhalten eine aktive Foliennummer.
3. Der freigegebene SHA-256-Wert in `Tests/Static/validate_privacy_metadata.py` wird im selben Schnitt kontrolliert erneuert.
4. `Documentation/Inventories/SLIDE_STATEMENT_REGISTER.md` erhält je Folie eine Zeile mit stabiler ID und Evidenzklasse.
5. Die Abnahme setzt eine erfolgreiche Runtime-Abnahme von `QRY-013` auf SQL Server 2019, 2022 und 2025 voraus.

## 9. Quellenübersicht

| Quellen-ID | Aussagebezug |
|---|---|
| `SRC-001` | Ausführungspläne und Sessionkontext |
| `SRC-007` | Parameter, Variablen und Kompilierverhalten |
| `SRC-027` | Kompilierung und Parameterverhalten |
| `SRC-040` | Planattribute und Cacheschlüssel |
| `SRC-045` | Recompile-Verhalten |
| `SRC-046` | Unterschiedliche Laufzeit zwischen Anwendung und Werkzeug |
| `SRC-047` | Parameter Sensitivity |
