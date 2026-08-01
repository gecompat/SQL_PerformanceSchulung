# ADV-009 – Folienspezifikation Modul M03, Lernziel `LO-M03-08`

| Merkmal | Wert |
|---|---|
| Paket | `ADV-009` |
| Status | `SPECIFIED` |
| Modul | M03 – Optimizer, Statistiken und Pläne |
| Lernziel | `LO-M03-08` |
| Claims | `ADV-CLM-017`, `ADV-CLM-018` |
| Kanonische Demo | `QRY-004` |
| Tiefenprofil | `VERTIEFUNG` |
| Testprofil | `TP-RUN`, `TP-PERF` |

## 1. Zweck und Lieferform

Das aktive Foliendeck `Presentations/Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx` ist als `SRC-DECK-001` registriert und in `Tests/Static/validate_privacy_metadata.py` über einen freigegebenen SHA-256-Wert gebunden. Jede Binäränderung entzieht dieser Freigabe die Grundlage und macht die Datenschutzprüfung rot.

Die Erweiterung wird deshalb bewusst auf der Spezifikationsebene geliefert: Dieses Dokument enthält folienfertige Inhalte einschließlich Sprechernotizen und Folienmarkern. Die Übernahme in das Deck ist ein eigener, freigabepflichtiger Schritt unter `ADV-009` und `PRS-012`; dabei wird der freigegebene Hashwert kontrolliert erneuert. Bis dahin bleiben die Claims in `Documentation/Curriculum/TRACEABILITY_MATRIX.md` auf `PLANNED` und ohne aktive Folie.

## 2. Didaktische Einordnung

Der Bogen schließt unmittelbar an `SLD-M03-104` an. Dort wurde gezeigt, dass Parameter, Variablen, Literale und `OPTION (RECOMPILE)` dem Optimierer unterschiedliche Information liefern. Hier wird daraus eine Auswahlentscheidung für optionale Suchbedingungen. Der Bogen setzt `OPT-007` und `OPT-008` voraus und endet vor `OPT-009` und `OPT-010`; Parameter Sensitive Plan Optimization und Optional Parameter Plan Optimization werden ausdrücklich nicht in diesem Bogen bewertet.

| Reihenfolge | Folien-ID | Claim | Rolle im Bogen |
|---|---|---|---|
| 1 | `SLD-M03-111` | – | Problemform: optionale Suchbedingungen |
| 2 | `SLD-M03-112` | `ADV-CLM-017` | Recompile als Tauschgeschäft |
| 3 | `SLD-M03-113` | `ADV-CLM-018` | Sicheres parameterisiertes dynamisches SQL |
| 4 | `SLD-M03-114` | `ADV-CLM-018` | Wiederverwendung und Zahl der Statementformen |
| 5 | `SLD-M03-115` | `ADV-CLM-017`, `ADV-CLM-018` | Auswahlkriterien und Übergang in `QRY-004` |

## 3. Folie `SLD-M03-111` – Eine Abfrage für viele Filterkombinationen

**Kernaussage:** Ein statischer Querytext mit optionalen Prädikaten bindet sich an eine einzige Planform, die für alle Selektivitäten gleichermaßen gilt.

**Folientext**

- Optionale Prädikate der Form `@Wert IS NULL OR Spalte = @Wert` sind nicht such-optimierbar.
- Der Optimierer wählt eine Planform, die jede Filterkombination bedienen muss.
- Diese Planform wird wiederverwendet, unabhängig davon, ob ein Filter 20 oder 20 000 Zeilen trifft.
- Das ist kein Fehler der Formulierung, sondern die Folge einer bewussten Wiederverwendung.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-111]` Wichtig ist die Wortwahl: Wir nennen das Catch-all-Muster nicht falsch. Es ist wartbar, es liefert korrekte Ergebnisse und es erzeugt genau einen Cacheeintrag. Der Preis ist die fehlende Anpassung an die Selektivität. In der Demo `QRY-004` messen wir das an drei Kombinationen mit 20, 19 980 und 4 000 Trefferzeilen; die Zahl der Planformen bleibt dabei bei eins. Erst diese Messung macht die anschließende Strategiediskussion belastbar.

**Quellen:** `SRC-001`, `SRC-045`, `SRC-049` **Demo:** `QRY-004` **Tiefe:** `VERTIEFUNG`

## 4. Folie `SLD-M03-112` – `OPTION (RECOMPILE)` ist ein Tauschgeschäft

**Kernaussage:** `OPTION (RECOMPILE)` ermöglicht laufzeitnahe Optimierung und gibt dafür die Planwiederverwendung auf. (`ADV-CLM-017`)

**Folientext**

- Der Optimierer kennt bei jeder Ausführung den konkreten Wert und kann unbenutzte Prädikatszweige vereinfachen.
- Dafür entsteht bei jeder Ausführung Kompilierarbeit.
- Der Nutzen wächst mit der Schwankung der Selektivität, die Kosten wachsen mit der Ausführungsfrequenz.
- Die Bewertung erfordert mehrere Ausführungen, nicht eine einzelne schnelle Messung.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-112]` Diese Folie korrigiert zwei gegenläufige Vereinfachungen: „Recompile ist die Lösung" und „Recompile ist zu teuer". Beide sind ohne Kontext falsch. In `QRY-004` messen wir zuerst den Nutzen – für den selektiven Wert sinken die logischen Lesevorgänge – und danach den Preis: 25 ungefilterte Wiederholungen je Variante, bei identischer Arbeitsmenge, zeigen die höhere CPU-Zeit je Ausführung. Wenn sich der Kompilierungsanteil in einer Umgebung nicht von der Messstreuung trennen lässt, meldet die Demo `WARN_EMPIRICAL_VARIANCE` und behauptet keine Verschlechterung.

**Quellen:** `SRC-001`, `SRC-045` **Demo:** `QRY-004` **Tiefe:** `VERTIEFUNG`

## 5. Folie `SLD-M03-113` – Dynamisches SQL sicher bauen

**Kernaussage:** Dynamische Suchbedingungen werden aus einer Positivliste zusammengesetzt; Werte werden gebunden, nicht konkateniert. (`ADV-CLM-018`)

**Folientext**

- Prädikatsbausteine stammen ausschließlich aus einer festen Positivliste im Code.
- Werte werden über `sys.sp_executesql` als Parameter gebunden und erscheinen nie im Statementtext.
- Objektbezeichner werden mit `QUOTENAME` behandelt, nie roh eingesetzt.
- Eine unbekannte Filterdefinition führt zu einem kontrollierten Abbruch, nicht zu einem improvisierten Prädikat.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-113]` Sicherheit ist hier kein Nebenthema, sondern ein eigenständiges Abnahmekriterium. Die Demo prüft zwei Dinge unabhängig voneinander: Erstens enthält kein zwischengespeicherter Statementtext einen Filterwert – das belegt die Parameterbindung. Zweitens wird eine Filterdefinition außerhalb der Positivliste abgewiesen. Wer stattdessen Benutzereingaben in den Text konkateniert, baut eine Injektionsfläche und zusätzlich eine unbegrenzte Zahl von Statementformen. Beide Probleme entstehen aus derselben Entscheidung.

**Quellen:** `SRC-001`, `SRC-045` **Demo:** `QRY-004` **Tiefe:** `VERTIEFUNG`

## 6. Folie `SLD-M03-114` – Wiederverwendung bleibt messbar

**Kernaussage:** Sicher parameterisiertes dynamisches SQL erzeugt je Filterform genau eine Statementform. (`ADV-CLM-018`)

**Folientext**

- Die Zahl der Statementformen folgt der Zahl der Filterformen, nicht der Zahl der Aufrufe.
- Gleiche Filterform mit unterschiedlichen Werten verwendet dieselbe Statementform wieder.
- Eine normalisierte Prädikatsreihenfolge verhindert unnötige Formvarianten.
- Die Zahl der Formen ist zu messen, nicht anzunehmen.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-114]` In der Demo führen drei Ausführungen zu genau zwei Statementformen: zweimal Filter auf die Kategorie mit unterschiedlichen Werten, einmal Filter auf den Status. Die Prädikatsreihenfolge wird im Code normalisiert, damit `Kategorie;Status` und `Status;Kategorie` denselben Text ergeben. Ohne diese Normalisierung wächst die Zahl der Formen kombinatorisch. Das ist der Punkt, an dem dynamisches SQL tatsächlich teuer wird – nicht durch die Technik selbst, sondern durch unkontrollierte Textvarianten.

**Quellen:** `SRC-001`, `SRC-045` **Demo:** `QRY-004` **Tiefe:** `VERTIEFUNG`

## 7. Folie `SLD-M03-115` – Strategie auswählen statt Rangfolge lernen

**Kernaussage:** Die Auswahl folgt Verteilung, Ausführungsfrequenz, Sicherheit und Wartbarkeit; alle Strategien müssen ergebnisgleich sein. (`ADV-CLM-017`, `ADV-CLM-018`)

**Folientext**

- Stabile Selektivität und hohe Frequenz: statischer Querytext mit Wiederverwendung.
- Stark schwankende Selektivität und geringe Frequenz: `OPTION (RECOMPILE)`.
- Viele Filterkombinationen mit begrenzten Formen: sicher parameterisiertes dynamisches SQL.
- Ergebnisgleichheit ist Voraussetzung jedes Laufzeitvergleichs, nicht dessen Resultat.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-115]` Diese Folie leitet in `QRY-004` über und schließt den Bogen. Die Demo vergleicht die drei Strategien unter identischer Datenverteilung und prüft für jede Filterkombination Zeilenzahl und Ergebnischecksumme, bevor sie über Lesevorgänge oder CPU spricht. Der Ausblick gehört ausdrücklich in die folgenden Demos: Parameter Sensitive Plan Optimization in `OPT-009` und Optional Parameter Plan Optimization in `OPT-010` lösen jeweils eine eigene Problemform und sind an Version, Compatibility Level und Eligibility gebunden. Sie ersetzen keine der drei hier verglichenen Strategien.

**Quellen:** `SRC-001`, `SRC-007`, `SRC-045`, `SRC-049` **Demo:** `QRY-004` **Tiefe:** `VERTIEFUNG`

## 8. Abnahmekriterien für die Deckübernahme

1. Jede Folie erhält im Notizfeld den unveränderten Marker `[SLIDE-ID: SLD-M03-11x]`.
2. Die Claims `ADV-CLM-017` und `ADV-CLM-018` werden in `Documentation/Curriculum/TRACEABILITY_MATRIX.md` von `PLANNED` auf `KEEP` gesetzt und erhalten eine aktive Foliennummer.
3. Der freigegebene SHA-256-Wert in `Tests/Static/validate_privacy_metadata.py` wird im selben Schnitt kontrolliert erneuert.
4. `Documentation/Inventories/SLIDE_STATEMENT_REGISTER.md` erhält je Folie eine Zeile mit stabiler ID und Evidenzklasse.
5. Die Abnahme setzt eine erfolgreiche Runtime-Abnahme von `QRY-004` auf SQL Server 2019, 2022 und 2025 voraus.

## 9. Quellenübersicht

| Quellen-ID | Aussagebezug |
|---|---|
| `SRC-001` | Ausführungspläne, Kompilierung und Planwiederverwendung |
| `SRC-007` | Parameter, Variablen und Kompilierverhalten |
| `SRC-045` | Dynamische Suchbedingungen, Recompile und parameterisiertes dynamisches SQL |
| `SRC-049` | Catch-all-Prädikate und Schätzfehler bei optionalen Parametern |
