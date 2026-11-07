# OPT-004 – Entwurf für Constraint-Vertrauen und Eindeutigkeit

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `OPT-004` – vertrauenswürdige Constraints und eindeutige Schlüssel |
| Quellen | `SRC-024`, `SRC-144` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Lernfrage und Grenze

Dieser Teilschnitt ergänzt den [Korrelations-/Statistikentwurf](OPT004_CORRELATED_STATISTICS_DESIGN.md). Er trennt drei überprüfbare Dinge: identische fachliche Zeilen, den tatsächlichen Vertrauens-/Eindeutigkeitszustand der Constraints und spätere Optimiererschätzungen beziehungsweise Pläne.

SQL Server kann laut Produktdokumentation Constraint-Information bei der
Kardinalitätsschätzung berücksichtigen. Das garantiert weder, dass eine
bestimmte Constraint-Information für eine konkrete Abfrage verwendet wird,
noch einen bestimmten Schätzwert oder Plan. Der Entwurf behauptet deshalb
keine Planform, Schätzungsrichtung oder Leistungsvorteil.

## Gegenprobe: vertrauenswürdiges und nicht vertrauenswürdiges CHECK

Zwei markierte Heaps enthalten exakt dieselben 1.000 Tupel `(RowId, Bucket)`.
`RowId` läuft von 1 bis 1.000; `Bucket = (RowId - 1) % 10`. Jeder
Bucket-Wert 0 bis 9 kommt 100-mal vor. Es gibt keine Schlüssel, Indizes,
NULL-Werte oder anderen Constraints.

Auf beiden geladenen Tabellen wird derselbe benannte Constraint
`CHECK (Bucket BETWEEN 0 AND 9)` angelegt. In der trusted-Variante validiert
`WITH CHECK` alle bestehenden Zeilen. In der untrusted-Variante überspringt
`WITH NOCHECK` diese Bestandsprüfung. Da die synthetischen Zeilen den Bereich
bereits erfüllen, bleiben die Daten vollständig identisch. Der spätere
Metadatenoracle muss den Zustand getrennt bestätigen:

| Profil | `is_disabled` | `is_not_trusted` |
|---|---:|---:|
| `TRUSTED_CHECK` | 0 | 0 |
| `UNTRUSTED_CHECK` | 0 | 1 |

Die Werte stammen aus `sys.check_constraints`. Sie belegen Constraint-
Enablement und Bestandsvertrauen, nicht seine Verwendung im Plan. Für beide
Profile gilt dasselbe Ergebnistupeloracle: `WHERE Bucket = 10` liefert null
Zeilen; `WHERE Bucket = 4` liefert genau die 100 Tupel mit `RowId` 5, 15, …,
995. Ergebnisgleichheit und Trust-Metadaten sind getrennte Assertions.

## Gegenprobe: Unique Constraint gegenüber nicht eindeutiger Indexstruktur

Zwei weitere Heapkopien enthalten identische 1.000 Tupel
`(RowId, LookupKey, Payload)`, wobei `RowId` und `LookupKey` beide von 1 bis
1.000 laufen und `Payload` deterministisch aus `RowId` gebildet wird. Keine
Spalte hat einen Primary-Key-Constraint. Beide Tabellen erhalten einen
Nonclustered Index auf `LookupKey`: im ersten Profil als `UNIQUE`-Constraint,
im zweiten als nicht eindeutiger Index.

Für `LookupKey = 424` muss der vollständige Ergebnistupelvergleich in beiden
Profilen genau die Zeile mit `RowId = 424` und dem zugehörigen Payload liefern.
Eine separate ungültige Positiv-/Negativgegenprobe kann eine zweite Zeile mit
demselben `LookupKey` einfügen wollen: der Unique-Constraint-Aufbau darf diese
Duplikatdaten nicht akzeptieren. Diese Gegenprobe gehört nicht in die reguläre
gleiche-Daten-Ergebnisserie.

Ein Unique-Constraint erzeugt einen eindeutigen Index. Microsoft beschreibt,
dass der Optimierer Unique-Constraints und unabhängig erstellte Unique-Indexes
nicht unterscheidet und Eindeutigkeit zusätzliche Optimiererinformation
liefern kann. Der Vergleich mit einem nicht eindeutigen Index behauptet weder
gleiche physische Indexbreite noch gleiche Page Counts. Die vollständigen
Ergebnisdaten sind deterministisch; Estimates, tatsächlich gewählter Index,
Operatoren und Ressourcen bleiben spätere empirische Befunde.

## Qualifikations- und Cleanupgrenze

Die spätere Demo braucht einen markergebundenen Setup-/Cleanupvertrag für
genau die vier eigenen Heapkopien und ihre Constraints beziehungsweise
Indexes. Katalogabfragen müssen exakte Objekt- und Constraintnamen binden;
keine Fremdobjekte dürfen verändert werden. Metadatenrechte und tatsächlicher
SQL-Server-Build sind vor jeder Ausführung zu qualifizieren. Fehlerpfade beim
Unique-Constraint-Aufbau müssen eigene Fixtureobjekte sicher entfernen.

Dieser Entwurf erweitert den OPT-004-Plan um die Constraint-/Eindeutigkeits-
Gegenproben, implementiert aber keine Demo. Constraint-Nutzung durch den
Optimierer, geschätzte Zeilen, tatsächliche Pläne, Ausführungszeit, Cleanup
und Enginekompilierung bleiben offen. Keine SQL-/Runtimefreigabe und keine
menschliche Generalprobe.

## Quellenbindung

`SRC-144` bindet die mögliche Verwendung von Constraints bei der CE, das
Überspringen der Bestandsprüfung mit `WITH NOCHECK` und die Katalogfelder
`is_disabled`/`is_not_trusted`. `SRC-024` bindet die eindeutige
Indexgarantie, den von einem Unique-Constraint erzeugten Index und die
Optimiererinformation. Beide Einträge stehen im
[Quellenregister](../Research/SOURCE_REGISTER.md#constraint-vertrauen-und-optimiererinferenzen--opt-004).
