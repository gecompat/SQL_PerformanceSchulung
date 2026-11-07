# QRY-005 – Entwurf für OR-Aufteilung und Mengensemantik

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `QRY-005` – OR-Prädikat gegen `UNION ALL`- und `UNION`-Varianten |
| Quellen | `SRC-142` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Lernfrage und Aussagegrenze

Eine Zeile, die beide Teilprädikate erfüllt, kommt bei einem OR-Prädikat genau
einmal aus der Quelltabelle. Werden beide Prädikate stattdessen als zwei
`UNION ALL`-Zweige ausgeführt, kommt diese Zeile zweimal vor. `UNION` entfernt
doppelte Ergebniszeilen; disjunkte Zweige können mit `UNION ALL` dagegen die
OR-Ergebnismenge ohne Duplikatentfernung rekonstruieren.

Der Entwurf prüft nur die dokumentierte Ergebnis- und Multiplizitätssemantik.
Er behauptet nicht, dass `OR`, `UNION`, `UNION ALL` oder disjunkte Prädikate
allgemein schneller sind. Sort-, Hash-, Concatenation- oder andere Planformen
sind keine statischen Erwartungen und benötigen später eine konkrete
Ausführung.

## Synthetische Fixture

Die spätere markierte Testtabelle enthält genau 10.000 Zeilen:

- `RowId`: eindeutige Ganzzahl von 1 bis 10.000;
- `Bucket`: `RowId % 10`, ganzzahlig und `NOT NULL`;
- `Payload`: acht ASCII-Zeichen, bestehend aus `R` und `RowId` links mit Nullen
  auf sieben Stellen aufgefüllt.

Jeder `Bucket`-Wert von 0 bis 9 kommt genau 1.000-mal vor. Für die fachliche
Abfrage seien `P := Bucket BETWEEN 0 AND 4` und
`Q := Bucket BETWEEN 4 AND 7`. Die Prädikate überlappen bei `Bucket = 4`.
Alle Prädikatswerte sind nicht NULL, sodass dieser Fixture keine
`UNKNOWN`-Ergebnisse der dreiwertigen Logik erzeugt.

| Teilmenge | Bucket-Werte | Zeilen |
|---|---|---:|
| nur P | 0–3 | 4.000 |
| P und Q | 4 | 1.000 |
| nur Q | 5–7 | 3.000 |
| weder P noch Q | 8–9 | 2.000 |
| P oder Q | 0–7 | 8.000 |

## Varianten und Oracles

Jede Variante projiziert vollständig `(RowId, Bucket, Payload)` und verwendet
dieselben Ausgangszeilen. Die Ergebnisauswertung normalisiert die Reihenfolge
über `RowId`; ohne explizite äußere Sortierung ist eine SQL-Ergebnisreihenfolge
nicht vorausgesetzt.

1. **Referenz mit OR:** `WHERE P OR Q`. Erwartet werden genau 8.000 Tupel, je
   passender `RowId` genau einmal.
2. **Naive Aufteilung mit UNION ALL:** erster Zweig `WHERE P`, zweiter Zweig
   `WHERE Q`. Erwartet werden 9.000 Ergebniszeilen: die 1.000 Zeilen mit
   `Bucket = 4` erscheinen je zweimal, alle anderen passenden Zeilen je
   einmal. Das ist absichtlich nicht tupel-/multiplizitätsgleich zur Referenz.
3. **Duplikatentfernung mit UNION:** dieselben beiden Zweige mit `UNION`.
   Erwartet werden 8.000 vollständige Tupel, identisch zur Referenz. Die
   eindeutige `RowId` bleibt Teil der Projektion, damit zwei unterschiedliche
   Quellzeilen mit sonst gleichen Nutzspalten nicht versehentlich als dieselbe
   fachliche Zeile behandelt würden.
4. **Disjunkte Aufteilung mit UNION ALL:** erster Zweig `WHERE P`, zweiter
   Zweig `WHERE Q AND NOT P`. Erwartet werden 8.000 vollständige Tupel,
   identisch zur Referenz; kein `RowId` erscheint mehrfach.

Für alle Varianten ist ein vollständiger Tupelvergleich gegen die erwarteten
`RowId`-/`Bucket`-/`Payload`-Werte erforderlich. Ein bloßer Zeilenzähler oder
eine Prüfsumme reicht nicht aus. Die Mengengleichheit der Varianten 1, 3 und 4
und die absichtliche Multiplizitätsabweichung von Variante 2 sind getrennte
Assertions.

## Methodische Grenzen

Die Microsoft-Dokumentation beschreibt `OR` als wahr, wenn mindestens eine
Bedingung wahr ist, und `UNION ALL` als Zusammenführung mit erhaltenen
Duplikaten; `UNION` entfernt doppelte projizierte Zeilen. Die Fixture belegt
keine Optimiererumschreibung oder Zugriffswirkung. Falls später tatsächliche
Pläne und Reads erhoben werden, sind sie pro Build und Ausführung zu berichten
und dürfen nicht in ein allgemeines Ergebnis überführt werden.

Die spätere Demo braucht einen eigenen Setup-/Cleanupvertrag, der nur die
markierte Testtabelle und die eigenen temporären Objekte entfernt. SQL-
Kompilierbarkeit, Engineergebnisse, Plan, Reads und Cleanup sind nicht durch
diesen Entwurf qualifiziert. Es gibt keine SQL-/Runtimefreigabe und keine
menschliche Generalprobe.

## Quellenbindung

`SRC-142` bindet die Produktsemantik der logischen `OR`-Bedingung und der
`UNION`-/`UNION ALL`-Duplikatbehandlung an zwei Microsoft-Primärseiten. Der
Eintrag steht im [Quellenregister](../Research/SOURCE_REGISTER.md#or-aufteilung-und-mengensemantik--qry-005).
