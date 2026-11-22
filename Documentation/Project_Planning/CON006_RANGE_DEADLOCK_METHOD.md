# CON-006 – Methodenentwurf für einen Schlüsselbereichs-Deadlock

| Merkmal | Wert |
|---|---|
| Status | `METHOD_DRAFT` – keine SQL-, Demo- oder Laufzeitfreigabe |
| Zweck | Prüfen, ob gegenseitige Einfügungen in zwei logisch getrennte, aber physisch überlappende Indexlücken einen eigenständigen Deadlock-Lernfall ergeben |
| Bestehender Fall | Der qualifizierte CON-006-Grundfall und die Sperrumwandlungsvariante bleiben unverändert |
| Quellenbasis | `SRC-004`, `SRC-066`, `SRC-068` |

## Abgrenzung und Lernziel

Der geplante CON-002-Kandidat zeigt den Schutz eines leeren Schlüsselbereichs
unter `SERIALIZABLE`: Eine zweite Session wartet beim Einfügen, bis die erste
Transaktion den Bereichsschutz freigibt. Der mögliche CON-006-Zusatz soll eine
andere Frage beantworten: Können zwei Sessions ihre jeweiligen Bereichslesungen
halten und anschließend mit Einfügungen in den jeweils von der anderen Session
geschützten Bereich einen Zyklus erzeugen?

Das unterscheidet sich vom qualifizierten CON-006-Konversionsfall, der zwei
Sperrumwandlungsanforderungen auf derselben bereits vorhandenen Schlüsselzeile
untersucht. Beim Range-Kandidaten sind die gelesenen Schlüsselbereiche leer und
die Einfügungen konkurrieren um die Indexlücke. Das ist ein fachlich möglicher
Lernzuwachs, aber noch kein nachgewiesenes Engineverhalten.

## Kandidatenaufbau für einen späteren isolierten Pilot

1. Eine eigene, markergebundene Wegwerfdatenbank enthält eine Tabelle mit einem
   eindeutigen, geordneten Indexschlüssel und genau zwei festen Randwerten,
   beispielsweise `10` und `90`.
2. Actor A und Actor B beginnen jeweils eine `SERIALIZABLE`-Transaktion und
   lesen unterschiedliche leere logische Bereiche zwischen diesen Randwerten,
   beispielsweise `(20, 40)` und `(60, 80)`. Jeder meldet nach der Lesung ein
   eigenes Signal; feste Zeitverzögerungen steuern keine Reihenfolge.
3. Nach beiden Lesesignalen fordert A eine Einfügung in Bs gelesenen Bereich
   an. Erst wenn der Beobachter diese Anforderung als wartend erkennt, fordert
   B eine Einfügung in As gelesenen Bereich an. Sämtliche Waits, Signale und
   Abbrüche haben feste Zeit- und Iterationsgrenzen.
4. Eine getrennte serielle Gegenprobe führt denselben Datenaufbau und dieselben
   Einfügungen ohne gleichzeitig gehaltene Bereichslesungen aus. Sie muss beide
   Einfügungen und den vollständigen Endzustand bestätigen.

Die konkreten Prädikate und Reihenfolgen sind ein kontrollierbarer
Versuchsvorschlag, keine Garantie dafür, dass der Optimierer beide Abfragen auf
dem gewünschten Index ausführt oder dass sie dieselbe physische KEY-Ressource
schützen. Ein Lauf ohne diesen Nachweis ist `NOT_PROVEN`, auch wenn ein Actor
blockiert.

## Quellenbasierte Lockhypothese – kein vorweggenommener Graph

Microsoft bezeichnet `RangeS-S` als geteilte Bereichs-/Ressourcensperre einer
serialisierbaren Bereichslesung und `RangeI-N` als Einfügebereichsprüfung. Die
Kompatibilitätsmatrix weist diese Modi für überlappende Schlüsselbereiche als
inkompatibel aus. Sie beschreibt außerdem, dass unter Optimized Locking eine
`RangeI-N`-Sperre nur erworben wird, wenn mindestens eine Transaktion auf der
Instanz `SERIALIZABLE` verwendet. Beide Kandidaten-Actors erfüllen diese
Isolationsbedingung. Diese Produktregeln machen den erwarteten Wait-Zyklus
plausibel; sie beweisen nicht, dass die konkreten Prädikate mit dem tatsächlichen
Plan auf denselben `KEY`-Hash abgebildet werden oder dass der Deadlockgraph genau
diese einfachen Modi ausgibt. Der Pflichtnachweis bleibt der reale Graph samt
Ressource, gehaltenen/angeforderten Modi, Opfer und Survivor. Konversionsmodi
werden aus dem beobachteten Graphen gelesen, nicht aus dem Szenariotitel
abgeleitet.

## Pflichtnachweis für einen Varianten-PASS

- Beide Actors müssen im Deadlockgraph an dieselbe markergebundene Datenbank,
  dasselbe Objekt, denselben Index und dieselbe physische Schlüsselressource
  gebunden sein. Der Graph muss die gehaltenen und angeforderten Modi und den
  geschlossenen Zyklus tatsächlich zeigen. Der genaue Konversionsmodus wird
  nicht vorab aus dem Szenariotitel abgeleitet.
- Genau ein Actor muss dem Graphopfer mit Fehler 1205 entsprechen. Im
  Deadlockarm muss genau eine der beiden Einfügungen zurückgerollt und genau
  eine vom Survivor bestätigt sein. Im serialen Kontrollarm müssen beide
  Einfügungen bestätigt sein. Ein beliebiges `xml_deadlock_report`-Ereignis
  oder eine allgemeine Blockingkette genügt nicht.
- Marker, Session-IDs, Datenbank, Zeitfenster, Signalreihenfolge, Abfrageplan,
  Indexprofil, Compatibility Level und Optionen werden vor und nach jedem Arm
  geprüft. Auf SQL Server 2025 wird insbesondere der tatsächliche Zustand von
  Optimized Locking erfasst; eine instanzweite Umschaltung oder ein ungesicherter
  Fallback ist ausgeschlossen.
- Beide Arme müssen den jeweiligen erwarteten Tabellenendzustand prüfen. Abbruch,
  offene Transaktionen, XE-Erfassung und Cleanup haben begrenzte Deadlines und
  markergebundene Eigentumsprüfungen.

Ein Ergebnis ohne Zyklus ist kein Fehler des Grundfalls, sondern lässt diesen
Zusatz `NOT_PROVEN` beziehungsweise `SKIP` enden. Ein anderer Graph als der
vertraglich festgelegte Range-Konflikt widerlegt den Kandidaten für diesen
Versuch.

## Gates

Vor einer ausführbaren Variante sind ein unabhängiger Methoden-/Quellenreview,
der Abgleich mit der freigegebenen CON-002-Kandidatenbeschreibung in der
[Szenarioanalyse](LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md) und die Freigabe
eines isolierten Zielbuilds erforderlich. Derzeit liegt für CON-002 nur diese
Kandidatenbeschreibung, kein ausführbarer Detailvertrag vor; deshalb darf der
Abgleich weder eine fertige CON-002-Implementierung noch deren Laufzeitverhalten
unterstellen. Ein später veröffentlichter Detailvertrag muss vor einer
ausführbaren CON-006-Variante erneut berücksichtigt werden. Der erste Pilot darf
keine gemeinsam genutzte Instanz verändern. SQL Server 2019, 2022 und 2025 sind
mögliche Matrixziele, keine bereits zugesagte Unterstützung; jedes Build benötigt
einen eigenen Graph- und Cleanupnachweis. Ein bestandener synthetischer
Offlinevertrag kann diese Gates nicht ersetzen.

## Quellen und Grenzen

- [`SRC-004`: Transaction locking and row versioning guide](../Research/SOURCE_REGISTER.md#src-004) beschreibt Schlüsselbereichsmodi, ihre Kompatibilität, Voraussetzungen und die Optimized-Locking-Bedingung für `RangeI-N`. Die Folgerung, dass zwei logisch verschiedene Suchprädikate in derselben Indexlücke konkurrieren könnten, ist eine Hypothese aus dem vorgeschlagenen Indexaufbau.
- [`SRC-066`: Deadlocks guide](../Research/SOURCE_REGISTER.md#src-066) beschreibt Deadlockgraphen und Opferauflösung.
- [`SRC-068`: system_health](../Research/SOURCE_REGISTER.md#src-068) beschreibt die vorhandene, begrenzte Deadlockereignisquelle.

Dieser Entwurf wertet keine SQL-Abfrage aus, beweist keine Deadlockvariante und
ändert weder CON-002 noch den validierten CON-006-Grundfall.

## Begrenzter statischer Graphvertrag

`Tests/Static/con006_range_graph_contract.py` prüft jetzt synthetisch oder
später bereitgestelltes Deadlock-XML auf genau zwei an die erwarteten SPIDs und
Datenbank gebundene Prozesse, ein Opfer sowie genau eine gemeinsame
Datenbank-/Objekt-/Index-/HoBT-`KEY`-Ressource. Beide Actors müssen dort als
Owner und als Waiter erscheinen; die Lockmodi und `requestType` müssen im Graph
vorhanden sein. Der Vertrag erzwingt absichtlich kein bestimmtes Paar wie
`RangeS-S`/`RangeI-N`, da der Entwurf den tatsächlichen Graphen nicht vorwegnimmt.

`evaluate_range_capture` bindet diese Formprüfung zusätzlich an die
caller-gelieferte Ereignisquelle `system_health`, den Eventnamen
`xml_deadlock_report`, genau ein passendes Ereignis im RFC-3339-Laufzeitfenster,
die Actor-/SPID-Zuordnung sowie das Graphopfer mit Fehler 1205 und den anderen
Actor als erfolgreichen Survivor. Das ist dieselbe Offline-Korrelationsgrenze
wie beim Konversionsvertrag; sie stellt keine Herkunftsattestation dar.

`evaluate_range_control` prüft nun den seriellen Kontrollarm auf zwei
caller-gelieferte erfolgreiche Actorresultate, getrennte Actor- und
Schlüsselzuordnungen, vollständige Übereinstimmung des beobachteten finalen
Schlüsselsatzes mit dem erwarteten Anfangssatz plus genau zwei Einfügungen und
null passende Deadlockereignisse. Fehlende Pflichtfelder ergeben
`NOT_PROVEN`; widersprüchliche Werte ergeben `FAIL`. Schlüsselwerte bleiben
Eingaben des Aufrufers. Ein synthetischer `PASS` authentifiziert weder die
Erhebung noch den tatsächlichen Insert- oder Tabellenzustand.

Das ist ausschließlich eine Formprüfung caller-gelieferter XML- und
Identitätswerte. Sie authentifiziert weder `system_health`-Herkunft noch
Run-Token, Zeitfenster, Actorresultate, Opferfehler 1205 oder Cleanup. Ein
synthetischer PASS belegt keinen Deadlocklauf. Der unabhängige Methodenreview,
der reale Graph mit tatsächlichen Modi, der serielle Kontrollarm und der
isolierte Enginepilot bleiben Voraussetzungen für jede Ausführungsfreigabe.
Der statische Kontrollarmprüfer schließt diese Voraussetzungen ebenfalls nicht.
