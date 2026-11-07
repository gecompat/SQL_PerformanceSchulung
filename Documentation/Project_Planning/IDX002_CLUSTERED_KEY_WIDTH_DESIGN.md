# IDX-002 – Entwurf für Breite und Eindeutigkeit des Clustered Key

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `IDX-002` – schmaler eindeutiger gegen breiten nicht eindeutigen Clustered Key |
| Quellen | `SRC-012`, `SRC-136`, `SRC-139` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Fragestellung und Grenze

Der Vergleich isoliert den Einfluss der Clustered-Key-Definition auf die
Clustered- und Nonclustered-Indexstrukturen. Beide Varianten enthalten
dieselben 100.000 vollständigen Zeilentupel, dieselben Spalten, dieselbe
Verteilung und denselben nicht eindeutigen sekundären Index auf `FilterBand`.
Nur der Clustered Key unterscheidet sich: ein schmaler eindeutiger `int`-
Schlüssel gegenüber einem breiten nicht eindeutigen `(KeyGroup, KeyLabel)`-
Schlüssel. Die zweite Variante hat absichtlich Duplikate, damit der
Uniquifier-Fall sichtbar ist.

Die Microsoft-Indexleitlinie beschreibt, dass Row-Locator-Spalten dem
Nonclustered-Indexschlüssel folgen und bei einem nicht eindeutigen Clustered
Index den Uniquifier einschließen. Die Microsoft-Schätzmethoden für Clustered-
und Nonclustered-Indizes beschreiben den Uniquifier als nullable variable-length
value, der in Zeilen mit nicht eindeutigen Key-Werten vier Byte belegt; ihre
Größenformel setzt für die Schätzung alle Key-Werte als nicht eindeutig voraus.
Das ist keine Zusage
konkreter Seitenzahlen, tatsächlicher Laufzeit oder allgemeiner optimaler
Indexgestaltung. Reale Seitenzahlen bleiben engine-, build-, Optionen- und
Belegungsabhängige Beobachtungen.

## Fixture und Clustered-Key-Profile

Vorgeschlagen sind in beiden Tabellen die Spalten `RowId int NOT NULL`,
`KeyGroup int NOT NULL`, `KeyLabel char(64) NOT NULL`, `FilterBand int NOT
NULL` und `Payload char(200) NOT NULL`. `RowId` läuft lückenlos von 1 bis
100.000. `KeyGroup` und `FilterBand` sind `(RowId - 1) % 100`; `KeyLabel` ist
für jede `KeyGroup` deterministisch `GROUP-` gefolgt von ihrer dezimalen Zahl,
links mit Nullen auf insgesamt 64 ASCII-Zeichen aufgefüllt.
`Payload` wird deterministisch allein aus `RowId` erzeugt. Damit sind die
Zeilentupel beider Varianten identisch und jeder `(KeyGroup, KeyLabel)`-Wert
kommt 1.000-mal vor.

| Profil | Clustered Key | Eindeutigkeit | Konsequenz für den Locator des nicht eindeutigen NCI |
|---|---|---|---|
| `NARROW_UNIQUE` | `(RowId)` | eindeutig | `RowId` wird als Clustered-Key-Locator ergänzt |
| `WIDE_NONUNIQUE` | `(KeyGroup, KeyLabel)` | nicht eindeutig; 1.000 Duplikate je Schlüsselwert | Clustered-Key-Spalten und der erforderliche 4-Byte-Uniquifier werden im nicht eindeutigen NCI berücksichtigt |

Beide Tabellen erhalten jeweils nur einen nicht eindeutigen
Nonclustered-Index auf `(FilterBand)`, ohne `INCLUDE`-Spalten. Weitere
sekundäre Indizes, Kompression und abweichende Indexoptionen sind im
Vergleichsprofil ausgeschlossen. Die Ausführungsumgebung muss identische
Builds, Datenbankoptionen und Messbedingungen verwenden.

## Oracles und Größenbeobachtung

Ein Korrektheitsfall liest `FilterBand = 37` und muss in beiden Varianten
1.000 vollständige Tupel liefern. Die Tupel und `RowId`-Multiplizitäten
müssen vollständig übereinstimmen; gleiche Zeilenzahl allein genügt nicht.
Dieser Ergebnisoracle prüft Fixturegleichheit, nicht den gewählten Plan.

Eine spätere, gesondert autorisierte Engineprüfung kann verwendete und
reservierte Seiten je Tabelle und Index aus den passenden Partitionen
aggregieren. Clustered- und Nonclustered-Indexseiten sind getrennte Ergebnisse;
`row_count` oder eine geschätzte Indexgröße ersetzt weder das Tupeloracle noch
die reale Seitenbeobachtung. Die Schätzformel für die nonclustered Variante
weist Key-Spalten und Uniquifier-Annahme explizit aus. Gemessene Seitendifferenzen
gelten nur für genau diese Daten, Build- und Indexoptionen.

Vor Implementierung oder Ausführung sind die Berechnung auf das konkrete
DDL-/Fixtureprofil anzuwenden, exakte Solltupel generatorunabhängig zu
definieren und die eingesetzten Seitenmetadaten samt Berechtigungen zu prüfen.
Ein Demo-/Setup-/Cleanupvertrag, Methodenreview und konkrete Ausführungsfreigabe
bleiben ebenfalls erforderlich. Dieser statische Entwurf wurde nicht auf einer
SQL-Engine ausgeführt und schließt keine menschliche Generalprobe ein.

Die Quellen-IDs sind im [Quellenregister](../Research/SOURCE_REGISTER.md)
aufgeführt. `SRC-012` deckt implizite Row Locator und Uniquifier-Regeln,
`SRC-136` die verwendeten/reservierten Seiten je Partition und `SRC-139` die
Key-, Locator- und Uniquifier-Annahmen für die Indexgrößenschätzungen ab.
