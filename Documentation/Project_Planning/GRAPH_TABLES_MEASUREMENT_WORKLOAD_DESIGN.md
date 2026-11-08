# Graph Tables: Messworkload für QRY-023

Stand: 7. November 2026
Status: statischer Workloaddesign-Vorschlag; nicht implementiert oder ausgeführt

## Trennung von Korrektheit und Messung

Die Fünf-Knoten-/Vier-Kanten-Probe in
[`GRAPH_TABLES_DEMO_CONCEPT.md`](GRAPH_TABLES_DEMO_CONCEPT.md) bleibt das kleine,
vollständig enumerierbare Korrektheitsoracle. Ihre zwei erwarteten Pfadtripel
werden unverändert geprüft. Sie ist zu klein, um Messwerte oder eine
Performancewirkung zu begründen.

Für `LO-M03-06`/`CLM-047` wird ein davon getrenntes, deterministisches
Messprofil vorgeschlagen: 10.000 disjunkte gerichtete Zwei-Kanten-Pfade. Für
`n` von 0 bis 9.999 lauten die synthetischen Personen-IDs `3*n+1`, `3*n+2` und
`3*n+3`; die Kanten sind `(3*n+1, 3*n+2)` und `(3*n+2, 3*n+3)`. Das ergibt
30.000 eindeutige Knoten, 20.000 gerichtete Kanten und exakt 10.000
Pfadtripel. Alle Werte sind künstlich generiert. Es gibt keine Querverbindungen,
doppelten Kanten oder zufallsabhängigen Seedwerte.

Ein Ziffernprodukt `0..9` × `0..9` × `0..9` × `0..9` kann die vollständige
Pfadnummernmenge ohne Rekursion erzeugen. Dieselben IDs und gerichteten Paare
werden in Graph- und relationalem Modell angelegt. Graph-NODE-/EDGE-Objekte
liegen dauerhaft nur in der eigenen, `FWK-002`-markierten wegwerfbaren
Testdatenbank; Hilfsnummern und Abfrageresultate dürfen temporär sein.

## Gleichheit und Indexvertrag

Vor der Messung liefern Graph- und relationale Vollpfadabfrage dieselben
Start-/Mittel-/Zieltripel. Die Abnahme prüft die Differenz in beide Richtungen
mit `EXCEPT` und zusätzlich Zeilenzahl und Eindeutigkeit; beide Differenzen
müssen leer sein und die Anzahl muss 10.000 betragen. Das verhindert, dass eine
bloß gleiche Gesamtanzahl fehlende und zusätzliche Pfade verdeckt.

Als initiale, semantisch begründete Zugriffsstrukturen werden vorgeschlagen:

- eindeutiger Index auf `PersonId` in beiden Knotentabellen,
- Graph-Edge-Index auf `($from_id, $to_id)`,
- relationaler Kantentabellenindex auf `(FromPersonId, ToPersonId)`.

Die beiden Indeximplementierungen sind fachlich ähnlich, physisch nicht
identisch. Beide Modelle werden mit denselben logischen Daten aufgebaut;
Indexdefinition und tatsächlicher Plan gehören zum Vergleichsbericht. Es gibt
keine Query Hints, keine unterschiedlichen Datenvolumen und keine zusätzliche
globale Cache- oder Serverkonfigurationsänderung.

Das [Quellen- und Methodenreview](GRAPH_TABLES_METHOD_REVIEW.md) präzisiert:
Die Graph-Query muss `MATCH` verwenden; direkte Gleichheit zwischen
Graph-ID-Pseudo-Spalten ist nicht der vorgesehene Pfad. Der empfohlene
Edge-Paarindex ist für diesen vollständigen Zwei-Hop-Scan eine Hypothese, kein
Leistungsversprechen. Die `PersonId`-Indizes sind Kandidaten und dürfen nicht
als von `MATCH` verwendete Strukturen behauptet werden.

## Messstatement und Ablauf

Die Messvariante zählt alle übereinstimmenden vollständigen Zwei-Kanten-Pfade
mit `COUNT_BIG(*)`. Graph- und Joinvariante verwenden dieselbe Ergebnisspalte,
keine Start-/Zielparameter und dieselbe 10.000-Pfade-Menge. Die separate
Korrektheitsphase vergleicht zuvor die vollständigen Pfadtripel; `COUNT_BIG`
vermeidet lediglich die Ausgabe von 10.000 Zeilen je Messlauf.

Vorgeschlagener Ablauf je qualifiziertem Engine-/Compatibility-Profil:

1. Relationaler Ausdruck ist die `BASELINE`, Graph-Ausdruck die `COMPARISON`;
   je Variante ein Warm-up, nicht in die fachliche Messreihe aufnehmen.
2. Fünf gepaarte Messwiederholungen in derselben Session und Datenbank.
3. Reihenfolge zwischen Paaren abwechseln: Graph–Relational, dann
   Relational–Graph, danach fortsetzen.
4. Keine Cacheleerung; beide Varianten laufen unter demselben unveränderten
   Ressourcen- und Datenzustand.
5. Mit `FWK-004` je Wiederholung Phase, Paar, Reihenfolge, Session-CPU,
   Logical Reads, Reads/Writes, verstrichene Zeit und Ergebnisanzahl erfassen.
   Für CPU, Logical Reads, Reads, Writes und Elapsed werden Median und
   Streuung der fünf gepaarten Deltas berichtet. Der Messprozedur-Overhead ist
   enthalten und wird offengelegt; alle Werte sind Sessiondeltas des Profils.
6. Actual-Plan-Evidenz getrennt nach `FWK-005` erfassen. Dieser Diagnosegang
   braucht `SHOWPLAN` auf den referenzierten Datenbanken und ist keine
   Messwiederholung der Performancewerte. `STATISTICS IO/TIME` verlangt laut
   Microsoft kein `SHOWPLAN`, muss aber im ausführbaren Vertrag von
   Parse-/Compile-Ausgabe getrennt werden.
7. Rohwerte erhalten und je Profil Median plus Streuung der fünf gepaarten
   Differenzen ausweisen. Keine Werte über Engineversionen aggregieren.

Ein Ergebnis, das ausschließlich für dieses synthetische Profil gilt, ist kein
allgemeiner Graph-/Relational-Leistungsgewinner. Planform oder einzelne Werte
erzeugen keinen Performanceclaim. Der didaktische Abschluss muss die Hypothese,
den Messbefund, die Streuung und die Grenzen gemeinsam beurteilen. Es gibt keine
Leistungsgrenze als Pass/Fail-Schwelle.

## Abnahmekriterien vor Implementierung

- Offline-Vertrag für Ergebnisdifferenz, eindeutige Pfadtripel und Sollanzahl
  ist statisch festgelegt.
- Generator ist für alle Nummern 0–9.999 vollständig und kollisionsfrei.
- Graph- und relationale Datensätze, Indizes und Messstatements bilden dieselbe
  fachliche Abfrage ab.
- Graph-`MATCH`, die Indexpaarung und die getrennten Plan-/Messrechte sind im
  ausführbaren Vertrag festgelegt.
- Warm-up-, Paarreihenfolge-, Mess- und Zusammenfassungsprotokoll sind im
  ausführbaren Demo-Vertrag konkretisiert.
- Sicherheitsstufe, Rechte, Ressourcenprofil, Version, Edition, Compatibility
  Level, Build-/CU-Pin, Skipfälle und `FWK-002`-Cleanup sind freigegeben.

Keines dieser Kriterien dokumentiert bereits einen SQL-Lauf, einen
Performancebefund oder eine Runtimefreigabe. Umsetzung, unabhängige
Methodenprüfung und Ausführung bleiben nächste getrennte Schritte.

## Grundlage

- Curriculum: [`LO-M03-06` / `CLM-047`](../Curriculum/TRACEABILITY_MATRIX.md#clm-047).
- Quellen: [`SRC-122` und `SRC-123`](../Research/SOURCE_REGISTER.md#graph-tables--eng-begrenzte-sql-graph--und-compatibility-quellen).
- Framework: `FWK-002`, `FWK-004`, `FWK-005`, `FWK-008`, `FWK-010`, `FWK-011`
  und `FWK-012`.
- Quellen- und Methodenreview: [`GRAPH_TABLES_METHOD_REVIEW.md`](GRAPH_TABLES_METHOD_REVIEW.md),
  `SRC-124` und `SRC-125`.
