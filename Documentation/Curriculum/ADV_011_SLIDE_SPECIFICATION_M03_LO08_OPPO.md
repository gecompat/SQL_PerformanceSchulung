# ADV-011 – Folienspezifikation Modul M03, Lernziel `LO-M03-08`, Optional Parameter Plan Optimization

| Merkmal | Wert |
|---|---|
| Paket | `ADV-011` |
| Status | `INTEGRATED` |
| Deckpositionen | 98 bis 101 (Folienteile `slide99.xml` bis `slide102.xml`) |
| Modul | M03 – Optimizer, Statistiken und Pläne |
| Lernziel | `LO-M03-08` |
| Claims | `ADV-CLM-020` |
| Kanonische Demo | `OPT-010` |
| Tiefenprofil | `VERTIEFUNG` |
| Testprofil | `TP-RUN`, `TP-PERF` |

## 1. Zweck und Lieferform

Das aktive Foliendeck `Presentations/Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx` ist als `SRC-DECK-001` registriert und in `Tests/Static/validate_privacy_metadata.py` über einen freigegebenen SHA-256-Wert gebunden. Nach `DEC-057` darf das Deck additiv und reproduzierbar erweitert werden; der Hashwert wird im selben Schnitt kontrolliert erneuert.

Dieses Dokument bleibt die verbindliche fachliche Quelle des Folieninhalts. Der sichtbare Folientext ist auf das Folienformat verdichtet; die Sprechernotizen tragen den unveränderten Marker `[SLIDE-ID: …]`. Nach `DEC-058` werden die Folien als geschlossener Block unmittelbar vor der Schlussfolie angefügt; bestehende Folienteile, Anzeigepositionen und Foliennummern der Basisfolien sowie der Blöcke `ADV-009` und `ADV-010` bleiben unverändert.

## 2. Didaktische Einordnung

Der Bogen löst den zweiten Teil des Versprechens ein, das `SLD-M03-115` gegeben und `ADV-010` zur Hälfte eingelöst hat. `OPT-009` behandelte die parametersensitive Planoptimierung für schiefe Gleichheitsprädikate; dieser Block behandelt ausschließlich Optional Parameter Plan Optimization für optionale Prädikate der Form `(Spalte = @p OR @p IS NULL)`. Beide Verfahren nutzen dieselbe Mehrplaninfrastruktur, entscheiden aber nach unterschiedlichen Kriterien und sind unabhängig voneinander. Der Bogen ersetzt keine der in `QRY-004` verglichenen Strategien, sondern ordnet ein versionsgebundenes Verfahren daneben ein.

| Reihenfolge | Folien-ID | Claim | Deckposition | Rolle im Bogen |
|---|---|---|---:|---|
| 1 | `SLD-M03-131` | – | 98 | Problemform: der belegte Parameter zahlt den offenen mit |
| 2 | `SLD-M03-132` | `ADV-CLM-020` | 99 | Dispatcherplan und optionales Parameterprädikat |
| 3 | `SLD-M03-133` | `ADV-CLM-020` | 100 | Voraussetzungen, Ausschlussgründe und Nachweis |
| 4 | `SLD-M03-134` | `ADV-CLM-020` | 101 | Steuerung, Abwahl und Abgrenzung |

## 3. Folie `SLD-M03-131` – Der belegte Parameter zahlt den offenen mit

**Kernaussage:** Ein optionales Parameterprädikat erzwingt eine Planform, die für beide Parameterzustände gültig sein muss.

**Folientext**

- Das Muster `(Spalte = @p OR @p IS NULL)` deckt zwei Parameterzustände in einem Querytext ab.
- Für den belegten Zustand wäre eine Suche gültig, für den offenen Zustand nicht.
- Es gibt deshalb keine Suchplanform, die für beide Zustände zugleich gültig wäre.
- Der belegte Aufruf trägt die Prüfbreite des offenen Aufrufs mit – unabhängig von der Kompilierungsreihenfolge.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-131]` Diese Folie trennt zwei Dinge, die im Alltag ständig vermischt werden. Bei `OPT-009` ging es um Schiefe: dort existiert eine Suchplanform, sie passt nur nicht zu jedem Wert. Hier ist die Lage grundsätzlich anders. Die Demo `OPT-010` arbeitet bewusst mit einer völlig gleichmäßigen Verteilung – 2 000 Agenten zu je genau 50 Zeilen –, damit niemand die Wirkung der Schiefe zuschreiben kann. Wir messen denselben Querytext in beiden Kompilierungsreihenfolgen und erhalten in beiden Fällen dieselbe Planform und dieselben Lesekosten für den belegten Parameter. Das ist der entscheidende Befund: Hier hilft kein günstiger Erstaufruf, weil es keine passende Planform gibt, die man treffen könnte.

**Quellen:** `SRC-001`, `SRC-049` **Demo:** `OPT-010` **Tiefe:** `VERTIEFUNG`

## 4. Folie `SLD-M03-132` – Dispatcherplan mit optionalem Parameterprädikat

**Kernaussage:** Optional Parameter Plan Optimization ersetzt die eine Planform durch einen Dispatcherplan mit einer Query Variant je NULL-Zustand. (`ADV-CLM-020`)

**Folientext**

- Der Dispatcherplan trägt je optionalem Prädikat ein Element `OptionalParameterPredicate`.
- Je Kombination der NULL-Zustände entsteht eine eigene Query Variant mit eigener `QueryVariantID`.
- Nach der Variantenauswahl wird das optionale Prädikat konstant gefaltet.
- Das Verfahren verändert die Kosten, niemals das Ergebnis.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-132]` Technisch sitzt das Verfahren auf derselben Infrastruktur wie die parametersensitive Planoptimierung: ein Dispatcherplan als Weiche, dahinter mehrere Varianten als vorbereitete Anweisungen. Der Unterschied steckt im Prädikatelement. Bei `OPT-009` steht dort `ParameterSensitivePredicate` mit Kardinalitätsgrenzen; hier steht `OptionalParameterPredicate` mit einem Ausdruck der Form `[@p] IS NULL`. Genau daran macht die Demo ihre Zuordnung fest – sie zählt beide Elementarten getrennt und meldet eine Warnung, falls beide zugleich auftreten. Nach der Auswahl faltet der Optimierer das Prädikat konstant; die Variante für den belegten Zustand sieht schlicht eine Gleichheitsbedingung und darf deshalb eine Suche verwenden.

**Quellen:** `SRC-026`, `SRC-049` **Demo:** `OPT-010` **Tiefe:** `VERTIEFUNG`

## 5. Folie `SLD-M03-133` – Voraussetzungen, Ausschlussgründe und Nachweis

**Kernaussage:** Das Verfahren ist versionsgebunden und kennt dokumentierte Ausschlussgründe; die Eignung ist im Plan zu belegen. (`ADV-CLM-020`)

**Folientext**

- Voraussetzung sind SQL Server 2025 und Compatibility Level 170.
- Unter Compatibility Level 170 ist `OPTIONAL_PARAMETER_OPTIMIZATION` standardmäßig eingeschaltet.
- Nicht angewendet wird das Verfahren bei lokalen Variablen statt Parametern, bei `OPTION (RECOMPILE)`, bei `SET ANSI_NULLS OFF` und bei automatisch parametrisierten Anweisungen.
- Ausbleibende Variantenbildung ist ein dokumentierter Befund, kein Anlass für undokumentierte Eingriffe.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-133]` Die vier Ausschlussgründe sind keine Randnotiz, sondern der häufigste Grund dafür, dass die Funktion im eigenen Code nicht greift. Besonders die ersten beiden treffen bestehende Anwendungen hart: Wer optionale Suchen mit lokalen Variablen aufbaut oder sie bislang mit `OPTION (RECOMPILE)` entschärft hat, erhält keine Varianten. Das ist kein Fehler, sondern dokumentiertes Verhalten – und es bedeutet, dass eine Migration auf SQL Server 2025 die Funktion nicht automatisch nutzbar macht. Die Demo `OPT-010` behandelt Eignung deshalb als Messgröße: Findet sie trotz passender Version keinen Dispatcherplan mit optionalem Parameterprädikat, endet die Phase kontrolliert mit `SKIP_EVIDENCE_MISSING` und weist aus, was beobachtet wurde.

**Quellen:** `SRC-007`, `SRC-026` **Demo:** `OPT-010` **Tiefe:** `VERTIEFUNG`

## 6. Folie `SLD-M03-134` – Steuerung, Abwahl und Abgrenzung

**Kernaussage:** Die Optimierung ist auf Datenbank- und Abfrageebene steuerbar und ergänzt die klassischen Strategien, statt sie zu ersetzen. (`ADV-CLM-020`)

**Folientext**

- Datenbankebene: `ALTER DATABASE SCOPED CONFIGURATION SET OPTIONAL_PARAMETER_OPTIMIZATION`.
- Abfrageebene: `USE HINT ('DISABLE_OPTIONAL_PARAMETER_OPTIMIZATION')` überschreibt die Datenbankeinstellung.
- Der Abfragehinweis wirkt unter jedem Compatibility Level und ist auch als Query-Store-Hinweis verfügbar.
- Abgrenzung: `OPT-009` entscheidet nach Kardinalität, `OPT-010` nach dem NULL-Zustand eines Parameters.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-134]` Die Steuerung ist zweistufig: die Datenbankeinstellung für die Fläche, der Abfragehinweis für den Einzelfall. Die Demo weist das nach, indem sie bei eingeschalteter Datenbankeinstellung belegt, dass für die ausdrücklich abgewählte Abfrage kein Dispatcherplan entsteht – bei identischem Ergebnis. Merken Sie sich zum Abschluss die Trennlinie: Die parametersensitive Planoptimierung entscheidet anhand geschätzter Kardinalitätsunterschiede bei Gleichheits- oder Bereichsprädikaten, die Optional Parameter Plan Optimization anhand der Frage, ob ein Parameter `NULL` ist. Eine Abfrage kann von beiden profitieren, von einem oder von keinem. Damit schließt sich der Bogen zu `QRY-004`: Wo keines der beiden Verfahren greift, bleiben die dort verglichenen Strategien die tragfähige Antwort.

**Quellen:** `SRC-026`, `SRC-049` **Demo:** `OPT-010` **Tiefe:** `VERTIEFUNG`

## 7. Abnahmekriterien für die Deckübernahme

1. **Erfüllt.** Jede Folie trägt im Notizfeld den unveränderten Marker `[SLIDE-ID: SLD-M03-13x]`; geprüft durch `Tests/Static/validate_adv011_deck_integration.py`.
2. **Erfüllt.** Der Claim `ADV-CLM-020` steht in `Documentation/Curriculum/TRACEABILITY_MATRIX.md` auf `KEEP` und trägt die aktiven Foliennummern 99, 100 und 101.
3. **Erfüllt.** Der freigegebene SHA-256-Wert in `Tests/Static/validate_privacy_metadata.py` wurde im selben Schnitt kontrolliert auf `e83bfebff93721cc5e5ef907dccc919ab574bcb420dcf8d91af90d4226c7c141` erneuert.
4. **Erfüllt.** `Documentation/Inventories/SLIDE_STATEMENT_REGISTER.md` enthält je Folie eine Zeile mit stabiler ID, Anzeigeposition, Folienteil und Evidenzklasse.
5. **Teilweise erfüllt.** [Actions-Lauf 30702590969](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30702590969) belegt `OPT-010` auf SQL Server 2025; SQL Server 2019 und 2022 enden planmäßig mit `SKIP_VERSION`. Offen bleibt die visuelle Renderprüfung der vier Folien in PowerPoint.

Die Übernahme erfolgte additiv über `Tools/build_adv011_slides.py`. Bestehende Folienteile, Anzeigepositionen und Foliennummern der Basisfolien und der Blöcke `ADV-009` und `ADV-010` bleiben unverändert; geändert wurde ausschließlich der Nenner der Fussnotenpaginierung von 98 auf 102.

## 8. Quellenübersicht

| Quellen-ID | Aussagebezug |
|---|---|
| `SRC-001` | Ausführungspläne, Kompilierung und Planwiederverwendung |
| `SRC-007` | Funktionsmatrix der intelligenten Abfrageverarbeitung |
| `SRC-026` | Optional Parameter Plan Optimization: Voraussetzungen, Dispatcherplan, Abwahlhinweis und Ausschlussgründe |
| `SRC-049` | empirische Einordnung optionaler Parameter und ihrer Behandlungsmuster |

## 9. Abgrenzung

Dieser Bogen bewertet weder die parametersensitive Planoptimierung aus `OPT-009` noch die in `QRY-004` verglichenen Strategien neu. Er verwendet keine Query-Store-Sichten und keine erweiterten Ereignisse, solange deren Pilotabnahme offen ist, und behauptet keine Beschleunigung, die nicht an Dispatcher- und Variantenevidenz belegt ist.
