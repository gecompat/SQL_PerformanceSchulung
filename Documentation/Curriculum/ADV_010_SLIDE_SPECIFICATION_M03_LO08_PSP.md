# ADV-010 – Folienspezifikation Modul M03, Lernziel `LO-M03-08`, Parametersensitive Planoptimierung

| Merkmal | Wert |
|---|---|
| Paket | `ADV-010` |
| Status | `INTEGRATED` |
| Deckpositionen | 94 bis 97 (Folienteile `slide95.xml` bis `slide98.xml`) |
| Modul | M03 – Optimizer, Statistiken und Pläne |
| Lernziel | `LO-M03-08` |
| Claims | `ADV-CLM-019` |
| Kanonische Demo | `OPT-009` |
| Tiefenprofil | `VERTIEFUNG` |
| Testprofil | `TP-RUN`, `TP-PERF` |

## 1. Zweck und Lieferform

Das aktive Foliendeck `Presentations/Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx` ist als `SRC-DECK-001` registriert und in `Tests/Static/validate_privacy_metadata.py` über einen freigegebenen SHA-256-Wert gebunden. Nach `DEC-057` darf das Deck additiv und reproduzierbar erweitert werden; der Hashwert wird im selben Schnitt kontrolliert erneuert.

Dieses Dokument bleibt die verbindliche fachliche Quelle des Folieninhalts. Der sichtbare Folientext ist auf das Folienformat verdichtet; die Sprechernotizen tragen den unveränderten Marker `[SLIDE-ID: …]`. Nach `DEC-058` werden die Folien als geschlossener Block unmittelbar vor der Schlussfolie angefügt; bestehende Folienteile, Anzeigepositionen und Foliennummern der Basisfolien bleiben unverändert.

## 2. Didaktische Einordnung

Der Bogen schließt unmittelbar an `SLD-M03-115` an. Dort endete der Vergleich der drei klassischen Strategien für optionale Suchbedingungen mit einem ausdrücklichen Ausblick auf `OPT-009` und `OPT-010`. Dieser Block löst den ersten Teil dieses Versprechens ein: Er behandelt ausschließlich Parameter Sensitive Plan Optimization. Optional Parameter Plan Optimization bleibt `OPT-010` vorbehalten und wird hier nicht bewertet. Der Bogen ersetzt keine der in `QRY-004` verglichenen Strategien, sondern ordnet ein versionsgebundenes Verfahren daneben ein.

| Reihenfolge | Folien-ID | Claim | Deckposition | Rolle im Bogen |
|---|---|---|---:|---|
| 1 | `SLD-M03-121` | – | 94 | Problemform: eine Planform, zwei Wahrheiten |
| 2 | `SLD-M03-122` | `ADV-CLM-019` | 95 | Dispatcherplan und Query Variants |
| 3 | `SLD-M03-123` | `ADV-CLM-019` | 96 | Eignung, Grenzen und Nachweis |
| 4 | `SLD-M03-124` | `ADV-CLM-019` | 97 | Entscheidung, Steuerung und Abwahl |

## 3. Folie `SLD-M03-121` – Eine Planform, zwei Wahrheiten

**Kernaussage:** Bei stark schiefer Verteilung entscheidet allein die Kompilierungsreihenfolge, welche Parameterbelegung benachteiligt wird.

**Folientext**

- Ein Querytext besitzt ohne Parametersensitivität genau eine zwischengespeicherte Planform.
- Der zuerst kompilierte Wert prägt diese Planform für alle weiteren Werte.
- Ein selektiver Erstwert benachteiligt den dominanten Wert; ein dominanter Erstwert benachteiligt den selektiven.
- Die Wahl des „richtigen“ Erstwerts verschiebt den Schaden, sie behebt ihn nicht.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-121]` Diese Folie räumt mit der Vorstellung auf, Parameter Sniffing lasse sich durch einen geschickt gewählten ersten Aufruf lösen. Die Demo `OPT-009` misst denselben Querytext in beiden Reihenfolgen: einmal kompiliert der selektive Wert mit fünf Trefferzeilen, einmal der dominante mit 99 000. In beiden Durchläufen bleibt es bei genau einer Planform, und in beiden Durchläufen zahlt genau ein Wert drauf. Die Prüfsummen sind identisch – wir sprechen über Kosten, nicht über Ergebnisse. Erst wenn dieser Befund steht, ist die Diskussion über mehrere Planformen überhaupt sinnvoll.

**Quellen:** `SRC-001`, `SRC-007` **Demo:** `OPT-009` **Tiefe:** `VERTIEFUNG`

## 4. Folie `SLD-M03-122` – Dispatcherplan und Query Variants

**Kernaussage:** Parameter Sensitive Plan Optimization ersetzt die eine Planform durch einen Dispatcherplan und mehrere Query Variants. (`ADV-CLM-019`)

**Folientext**

- Der Dispatcherplan enthält die ausgewählten Prädikate mit unterer und oberer Kardinalitätsgrenze.
- Je Prädikat entstehen bis zu drei Kardinalitätsbänder und damit bis zu drei Planformen.
- Die Varianten liegen als eigene zwischengespeicherte Pläne vor und tragen eine eigene `QueryVariantID`.
- Voraussetzung sind SQL Server 2022 und Compatibility Level 160.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-122]` Der Dispatcherplan ist kein Ausführungsplan im gewohnten Sinn, sondern eine Weiche. Er trägt im Plan-XML das Element `ParameterSensitivePredicate` mit den Grenzen, an denen die Bänder getrennt werden. Die eigentliche Arbeit leisten die Varianten; sie werden als vorbereitete Anweisungen zwischengespeichert und tragen den vom Produkt erzeugten Hinweis `PLAN PER VALUE`. Diesen Hinweis kann niemand von Hand schreiben – er ist ein Erzeugnis des Optimierers und ausschließlich Evidenz. In der Demo weisen wir genau das nach: mindestens einen Dispatcherplan, mindestens zwei Varianten und die ausgewiesenen Grenzen.

**Quellen:** `SRC-007`, `SRC-008` **Demo:** `OPT-009` **Tiefe:** `VERTIEFUNG`

## 5. Folie `SLD-M03-123` – Eignung ist nachzuweisen, nicht anzunehmen

**Kernaussage:** Das Verfahren ist eng begrenzt; ob es greift, entscheidet der Optimierer und ist im Plan zu belegen. (`ADV-CLM-019`)

**Folientext**

- Nur Gleichheitsprädikate kommen infrage; Bereichs-, Ungleichheits- und `LIKE`-Prädikate nicht.
- Höchstens drei Prädikate je Abfrage werden ausgewählt.
- Ohne ausreichende Schiefe in der Statistik entsteht keine Variantenbildung.
- Ausbleibende Variantenbildung ist ein dokumentierter Befund, kein Anlass für undokumentierte Eingriffe.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-123]` Hier liegt der häufigste Denkfehler im Umgang mit dieser Funktion: Sie wird eingeschaltet und danach als wirksam vorausgesetzt. Die Demo `OPT-009` behandelt Eignung deshalb als Messgröße. Findet sie trotz passender Version keinen Dispatcherplan, endet die Phase kontrolliert mit `SKIP_EVIDENCE_MISSING` und weist aus, was beobachtet wurde. Sie erzwingt nichts über Ablaufkennzeichen oder undokumentierte Hinweise. Für die Praxis heißt das: Wer die Funktion einsetzt, prüft im Plan, ob sie für die eigene Abfrage überhaupt greift – und plant für den Fall, dass sie es nicht tut.

**Quellen:** `SRC-007`, `SRC-008`, `SRC-048` **Demo:** `OPT-009` **Tiefe:** `VERTIEFUNG`

## 6. Folie `SLD-M03-124` – Steuerung, Abwahl und Einordnung

**Kernaussage:** Die Optimierung ist auf Datenbank- und Abfrageebene steuerbar und ergänzt die klassischen Strategien, statt sie zu ersetzen. (`ADV-CLM-019`)

**Folientext**

- Datenbankebene: `ALTER DATABASE SCOPED CONFIGURATION SET PARAMETER_SENSITIVE_PLAN_OPTIMIZATION`.
- Abfrageebene: `USE HINT ('DISABLE_PARAMETER_SENSITIVE_PLAN')` wählt gezielt ab.
- `OPTION (RECOMPILE)` und abgeschaltetes Parameter Sniffing setzen das Verfahren ebenfalls außer Kraft.
- Ergebnisgleichheit bleibt in jeder Konfiguration Voraussetzung jedes Vergleichs.

**Sprechernotiz**

`[SLIDE-ID: SLD-M03-124]` Die Steuerbarkeit ist der praktische Kern dieser Folie. Eine Abfrage, die von der Weiche nicht profitiert, lässt sich einzeln abwählen, ohne die Datenbankeinstellung anzutasten – das prüft die Demo, indem sie bei eingeschalteter Datenbankeinstellung nachweist, dass für die abgewählte Abfrage kein Dispatcherplan entsteht. Umgekehrt gilt: Wer ohnehin mit `OPTION (RECOMPILE)` arbeitet, erhält keine Varianten, weil bei jeder Ausführung neu optimiert wird. Damit schließt sich der Bogen zu `QRY-004`: Parametersensitive Planoptimierung ist eine gezielte Antwort auf schiefe Gleichheitsprädikate, kein allgemeiner Beschleuniger und kein Ersatz für eine bewusste Strategiewahl. Optional Parameter Plan Optimization behandeln wir getrennt in `OPT-010`.

**Quellen:** `SRC-007`, `SRC-008` **Demo:** `OPT-009` **Tiefe:** `VERTIEFUNG`

## 7. Abnahmekriterien für die Deckübernahme

1. **Erfüllt.** Jede Folie trägt im Notizfeld den unveränderten Marker `[SLIDE-ID: SLD-M03-12x]`; geprüft durch `Tests/Static/validate_adv010_deck_integration.py`.
2. **Erfüllt.** Der Claim `ADV-CLM-019` steht in `Documentation/Curriculum/TRACEABILITY_MATRIX.md` auf `KEEP` und trägt die aktiven Foliennummern 95, 96 und 97.
3. **Erfüllt.** Der freigegebene SHA-256-Wert in `Tests/Static/validate_privacy_metadata.py` wurde im selben Schnitt kontrolliert auf `651d533596f30f77db2fdd04c9dd3296306884c5a721ecf3de2f2b6fd536b2b4` erneuert.
4. **Erfüllt.** `Documentation/Inventories/SLIDE_STATEMENT_REGISTER.md` enthält je Folie eine Zeile mit stabiler ID, Anzeigeposition, Folienteil und Evidenzklasse.
5. **Teilweise erfüllt.** [Actions-Lauf 30701731564](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30701731564) belegt `OPT-009` auf SQL Server 2022 und 2025; SQL Server 2019 endet planmäßig mit `SKIP_VERSION`. Offen bleibt die visuelle Renderprüfung der vier Folien in PowerPoint.

Die Übernahme erfolgte additiv über `Tools/build_adv010_slides.py`. Bestehende Folienteile, Anzeigepositionen und Foliennummern der Basisfolien und des Blocks `ADV-009` bleiben unverändert; geändert wurde ausschließlich der Nenner der Fussnotenpaginierung von 94 auf 98.

## 8. Quellenübersicht

| Quellen-ID | Aussagebezug |
|---|---|
| `SRC-001` | Ausführungspläne, Kompilierung und Planwiederverwendung |
| `SRC-007` | Funktionsmatrix der intelligenten Abfrageverarbeitung |
| `SRC-008` | Detailgrenzen der parametersensitiven Planoptimierung |
| `SRC-048` | empirische Grenzfälle der Variantenbildung |

## 9. Abgrenzung

Dieser Bogen bewertet weder Optional Parameter Plan Optimization noch die in `QRY-004` verglichenen Strategien neu. Er verwendet keine Query-Store-Sichten, solange deren Pilotabnahme offen ist, und behauptet keine Beschleunigung, die nicht an Dispatcher- und Variantenevidenz belegt ist.
