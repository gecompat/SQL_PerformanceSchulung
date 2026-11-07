# OPT-012 – Entwurf: Adaptive Join unter wechselnder Eingabekardinalität

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `OPT-012` – eine adaptive Joinentscheidung bei kleinen und großen Build-Inputs beobachten |
| Quellen | `SRC-007`, `SRC-008`, `SRC-150` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Lernfrage und Aussagegrenze

Kann ein einzelner gecachter Adaptive-Join-Plan für dieselbe Abfrage bei
unterschiedlicher Build-Input-Kardinalität zur Laufzeit Nested Loops oder Hash
Join verwenden? Der spätere Lauf soll die Entscheidung über den Actual Plan
belegen. Das Vorhandensein von CL 140 oder höher allein garantiert weder
Batch-Mode-Ausführung noch einen Adaptive Join.

Microsoft beschreibt Adaptive Joins ab SQL Server 2017. Der Operator scannt
zuerst seinen Build-Input und vergleicht die gelesene Zeilenanzahl mit einer
im Plan hinterlegten Schwelle. Bei kleinerer Kardinalität kann er auf Nested
Loops wechseln; ab der Schwelle läuft der Hash-Join-Pfad weiter. Derselbe
gecachte adaptive Plan kann bei Folgeausführungen anhand dieser Schwelle und
der dann beobachteten Zeilen eine andere Runtimeentscheidung treffen.
Die Schwelle und konkrete Planform werden vom Optimierer abgeleitet und sind
keine vorab festgelegten Lehrwerte.

Der Entwurf behauptet keine Leistungsrangfolge. `ActualJoinType` belegt den
gewählten Operator, nicht dass er schneller war. CPU, Reads, Dauer und
Speicherwirkung sind weder Teil eines statischen Erfolgsoracles noch durch die
Quellen festgelegt.

## Eligibility und kontrollierter Skip

Eine spätere Engineprobe bindet jede Voraussetzung einzeln:

- Datenbank-Compatibility-Level mindestens 140;
- `SELECT`-Anweisung;
- der Join muss sowohl für indexed Nested Loops als auch Hash Join geeignet
  sein;
- die Hash-Alternative muss Batch Mode verwenden können, etwa über einen
  Columnstore-Pfad oder ab CL 150 einen tatsächlich geeigneten Batch-Mode-on-
  Rowstore-Pfad;
- beide generierten Alternativen müssen denselben ersten Child-Operator
  (Outer Reference) besitzen.

Diese Voraussetzungen sind Eligibility, keine Zusage der Optimiererwahl.
Wenn Initialisierung, Build oder Actual Plan keinen Adaptive Join liefern,
bleibt der adaptive Claim unqualifiziert und der Lauf endet mit einem
begründeten `SKIP_EVIDENCE_MISSING`. Fixture oder Assertions werden nicht
nachträglich verändert, um einen gewünschten Operator zu erzwingen.

## Geplantes Fixture und zwei Eingabeprofile

Der spätere Fixtureentwurf kann eine `Fact`-Tabelle mit 100.000 deterministisch
erzeugten Zeilen und eine `Dimension`-Tabelle mit 1.000 eindeutigen Schlüsseln
verwenden. `FactId` läuft von 1 bis 100.000, `DimensionId = ((FactId - 1) %
1000) + 1`, `BatchKey` ist für IDs 1–100 klein und für 101–100.000 groß, und
`Measure = (FactId * 37) % 100003`. Die Dimension enthält jeden Schlüssel
1–1.000 einmal sowie `Label = DimensionId % 17` und einen eindeutigen Index auf
`DimensionId`. Ein Columnstore-Pfad für die Faktentabelle ist ein möglicher
Batch-Mode-Enabler; die tatsächliche Batch-Mode- und Adaptive-Join-Eligibility
muss im Zielbuild beobachtet werden.

Eine parametrisierte Abfrage verbindet beide Tabellen über `DimensionId` und
filtert mit `WHERE f.BatchKey = @BatchKey`. Die beiden Profilwerte sind der
kleine und der große Schlüssel. Die Abfrage, der Datenbank-/SET-Kontext und die
Planinstanz bleiben identisch; der erste Lauf kompiliert und cached den Plan,
der zweite verwendet ihn mit dem anderen Parameter. Erwartete vollständige
Tupel lassen sich je Profil aus den `FactId`-Bereichen berechnen:
`(FactId, DimensionId, Measure, Label)` mit `DimensionId = ((FactId - 1) %
1000) + 1` und `Label = DimensionId % 17`. Kleines Profil umfasst exakt IDs
1–100 und damit 100 Tupel; großes Profil IDs 101–100.000 und damit 99.900
Tupel. Beide vollständigen sortierten Ausgaben werden gegen diese Formeln
geprüft.

Das kleine Profil muss unterhalb der tatsächlich im Plan ausgewiesenen
`AdaptiveThresholdRows` liegen; das große Profil muss mindestens diese
Schwelle erreichen. Die statische Planung fixiert keine konkrete Schwelle,
Zeilenwerte oder Planform. Vor dem späteren Lauf müssen Datenverteilung und
Abfrage so qualifiziert werden, dass beide Tupelmengen korrekt und die
Joinalternativen möglich sind. Falls kein Profil die Plan-Schwelle auf beiden
Seiten belastbar erreicht, ist das ein offener Qualifikationspunkt und kein
Grund, ein erwartetes Ergebnis vorzutäuschen.

## Planidentität und Nachweisvertrag

Für beide Ausführungen werden Querytext/Hash, Datenbankkontext, relevante
SET-Optionen, Planhandle beziehungsweise äquivalente exakte Planbindung und
vollständige Plan-XML gesichert. Vor der ersten Ausführung wird der adaptive
Plan identifiziert; nach beiden Läufen wird belegt, dass dieselbe gecachte
Planinstanz verwendet wurde. Eine erneute Kompilierung zwischen den Profilen
entwertet die Aussage zur Runtimeanpassung und führt zu `SKIP_EVIDENCE_MISSING`.

Der Planbeleg verlangt am Adaptive-Join-Operator:

1. `AdaptiveThresholdRows` mit positivem Wert;
2. `EstimatedJoinType` als dokumentiertes Planattribut;
3. `ActualJoinType` aus dem Actual Plan für jede Ausführung;
4. für das kleine Profil `ActualJoinType = Nested Loops` und eine
   Build-Input-Zeilenanzahl unter der Schwelle;
5. für das große Profil `ActualJoinType = Hash Match` und eine
   Build-Input-Zeilenanzahl an oder über der Schwelle.

Fehlt die Planinstanzbindung, ein Attribut oder die Actual-Plan-Evidenz, wird
keine adaptive Umschaltung behauptet. Plan XML, Laufzeitzeilen und Ergebnisse
werden getrennt von etwaigen Leistungsmetriken ausgewertet.

## Ergebnistupel und Gegenproben

Der spätere Generator muss disjunkte Schlüsselbereiche und vorab berechenbare
Joinmultiplikitäten liefern. Für jedes Eingabeprofil werden erwartete
Tupelanzahl und vollständige sortierte Tupel aus den Generatorformeln
abgeleitet. Die kleine und große Ausgabe müssen sich in der Zeilenanzahl
unterscheiden dürfen; jede Ausgabe wird exakt gegen ihr eigenes Oracle
geprüft. Ein bloßer Rowcount oder eine Prüfsumme ersetzt den vollständigen
Tupelvergleich nicht.

Eligibility-Gegenproben können getrennt dokumentieren, dass eine ungeeignete
Abfrage oder fehlende Batch-Mode-Bedingung keinen Adaptive Join erzeugt. Sie
gehören nicht in das positive Umschaltoracle und dürfen aus dem Ausbleiben des
Operators keine Aussage zur Query-Performance ableiten. Die konkreten
Generator- und Abfragedetails bleiben vor Runtime gegen die Zielversionen zu
qualifizieren; insbesondere muss der Build-Input den Adaptive-Join-Operator
speisen, und die beiden Profile müssen die beobachtete Schwelle über- bzw.
unterschreiten.

## Offene Punkte vor einer Runtimefreigabe

- konkrete, weiterhin synthetische Tabellen- und Datenformeln einschließlich
  beider vollständiger Tupeloracles;
- Version-/Buildprofil und Batch-Mode-Pfad für SQL Server 2019, 2022 und 2025;
- statische T-SQL- und Demo-Vertragsprüfung, sichere Ressourcenobergrenzen,
  Rechte und vollständiger Cleanup;
- Nachweis, wie exakt dieselbe gecachte Planinstanz zwischen den beiden
  Ausführungen gebunden und gegen Recompile/Cacheverlust geschützt wird;
- erwartbare Plan-XML-Attribute je Zielversion und kontrollierter Skip bei
  fehlender Eligibility oder Evidence.

Der Entwurf erteilt keine SQL-/Runtimefreigabe, kein Ausführungs- oder
Performanceclaim und schließt eine menschliche Generalprobe aus. Eine spätere
Fortsetzung muss diese Punkte über den regulären Vertrags- und Qualifikationsweg
schließen.
