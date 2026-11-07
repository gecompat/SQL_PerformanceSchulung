# Lookup und steigende Treffermengen

Ein selektiver Indexzugriff kann zuerst passende Row Locators finden und
fehlende Spalten anschließend einzeln aus dem Clustered Index lesen. Dieser
Key Lookup kann bei wenigen Treffern sinnvoll sein. Bei vielen Treffern kann
ein Scan günstiger werden. Der konkrete Übergang hängt von Tabelle, Index,
Datenverteilung, Statistiken, Abfrage und Build ab; einen universellen
Prozent-Kippunkt gibt es nicht.

## Nicht abdeckender und abdeckender Index

Ein nicht abdeckender Nonclustered Index enthält nicht alle benötigten
Abfragespalten. Wenn etwa `Payload` weder Schlüssel- noch INCLUDE-Spalte ist,
muss ein vom Optimierer gewählter Key Lookup die fehlende Spalte aus dem
Clustered Index nachladen. Der Lookup ist im tatsächlichen Plan mit `Nested
Loops` verbunden. Seine tatsächliche Ausführungszahl und Zeilen sind wichtig:
ein Lookup-Operator allein sagt nicht, wie viel Arbeit er im konkreten Lauf
verrichtet.

Eine abdeckende Indexgegenprobe hält Prädikat und Ergebnisprojektion gleich,
nimmt aber die zusätzlich benötigte Spalte als `INCLUDE` auf. Damit liegt der
Wert auf der Blattebene des Nonclustered Index. Das kann den Lookup vermeiden,
wenn der Optimierer den Index für die Abfrage verwendet. Der breitere Index
beansprucht zugleich zusätzlichen Speicher und kann Änderungen verteuern.
Diese Folgekosten sind in der bestehenden Lookup-Kandidatenskizze noch nicht
qualifiziert.

## Plan- und Ergebnisevidenz lesen

Eine belastbare Gegenprobe hält für jede Treffermenge dasselbe Tupeloracle und
dieselbe Ergebnisprojektion zwischen clustered-only Baseline, nicht
abdeckendem Index und abdeckendem Index ein.

1. Vergleiche vollständige Ergebnistupel, nicht nur Zeilenzahlen.
2. Sieh im tatsächlichen Plan nach Seek-/Scan-Prädikaten, Residual-Prädikaten,
   `Key Lookup`, dessen tatsächlicher Ausführungszahl und tatsächlichen Zeilen.
3. Lies geschätzte und tatsächliche Zeilen nebeneinander. Eine Abweichung kann
   die Planwahl erklären, beweist aber für sich noch keine Ursache.
4. Vergleiche statementbezogene Logical Reads. CPU- und Elapsed-Zeit sind
   zusätzliche, umgebungsabhängige Messwerte; ein einzelner Lauf oder eine
   sichtbare Seek-Form beweist keinen Leistungsgewinn.
5. Berichte den gegebenenfalls beobachteten Planübergang für genau diese
   Fixture, Statistiken, Compilewerte und SQL-Server-Version. Wenn kein
   Übergang sichtbar ist, ist das ebenfalls das Ergebnis der Gegenprobe.

Falls ein Key Lookup fehlt, kann der Optimierer einen Scan, einen anderen
Index oder einen bereits abdeckenden Zugriff gewählt haben. Prüfe zuerst den
tatsächlich verwendeten Plan und den gebundenen Compilewert. Indexhints würden
die natürliche Planwahl der Lookup-Kurve verdecken und gehören nicht in diese
Gegenprobe.

## Quellen und Status

Das [Quellenregister](../Research/SOURCE_REGISTER.md) bindet `SRC-012` für
Indexstruktur und Selektivitätskontext, `SRC-125` für Plan-/Read-Evidenz und
`SRC-137` für Key Lookup und `OPTION (RECOMPILE)`. Der
[IDX-004-Entwurf](../Project_Planning/IDX004_LOOKUP_SELECTIVITY_DESIGN.md)
legt die vorgeschlagene Frequenzleiter und das vollständige Tupeloracle fest.
Diese Erläuterung gibt weder die Demo noch eine Laufzeit- oder
Performancequalifikation frei. Keine Laufzeit wurde ausgeführt; die
menschliche Generalprobe bleibt ausgeschlossen.
