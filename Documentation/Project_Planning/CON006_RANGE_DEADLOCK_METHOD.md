# CON-006 – Methodenentwurf für einen Schlüsselbereichs-Deadlock

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` – in CON-006 integriert; vollständige Demo- und Cleanupmatrix 2019/2022/2025 bestanden |
| Zweck | Prüfen, ob gegenseitige Einfügungen in zwei logisch getrennte, aber physisch getrennte Indexlücken einen eigenständigen Deadlock-Lernfall ergeben |
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
untersucht. Die integrierte Range-Variante liest leere Schlüsselbereiche und
konkurriert mit Einfügungen um zwei getrennte Indexlücken. Die vollständige
Variante und ihre serielle Gegenprobe sind auf den drei freigegebenen Builds
qualifiziert.

## Integrierter Ablauf

1. Eine eigene, markergebundene Wegwerfdatenbank enthält eine Tabelle mit einem
   eindeutigen, geordneten Indexschlüssel und drei festen Werten, beispielsweise
   `10`, `50` und `90`. Der mittlere Wert trennt die beiden physischen
   Indexlücken.
2. Actor A und Actor B beginnen jeweils eine `SERIALIZABLE`-Transaktion und
   lesen unterschiedliche leere Bereiche, beispielsweise A `(20, 40)` und B
   `(60, 80)`. Nach beiden Lesungen fügt A den Wert `70` in Bs geschützten
   Bereich ein; B fügt danach `30` in As geschützten Bereich ein. Jeder Actor
   hält damit eine KEY-Bereichssperre und wartet beim Einfügen auf die andere
   KEY-Ressource. Feste Zeitverzögerungen steuern keine Reihenfolge.
3. Der Beobachter gibt B erst frei, nachdem A beim Einfügen als wartend auf B
   nachgewiesen wurde. Sämtliche Waits, Signale und Abbrüche haben feste
   Zeit- und Iterationsgrenzen.
4. Eine getrennte serielle Gegenprobe führt denselben Datenaufbau und dieselben
   Einfügungen ohne gleichzeitig gehaltene Bereichslesungen aus. Sie muss beide
   Einfügungen und den vollständigen Endzustand bestätigen.

Der Beobachter bestätigt die tatsächlichen Range-Sperren über
`sys.dm_tran_locks`, gibt A zum Einfügen frei und startet B erst, nachdem die
Blockierung von A durch B nachgewiesen ist. Ein Lauf ohne den gebundenen
Deadlockgraph, das Opfer-/Survivorergebnis und den erwarteten Endbestand endet
mit `FAIL_RESULT_CONTRACT`.

## Quellenbasierte Lockhypothese – kein vorweggenommener Graph

Microsoft bezeichnet `RangeS-S` als geteilte Bereichs-/Ressourcensperre einer
serialisierbaren Bereichslesung und `RangeI-N` als Einfügebereichsprüfung. Die
Kompatibilitätsmatrix weist diese Modi für überlappende Schlüsselbereiche als
inkompatibel aus. Sie beschreibt außerdem, dass unter Optimized Locking eine
`RangeI-N`-Sperre nur erworben wird, wenn mindestens eine Transaktion auf der
Instanz `SERIALIZABLE` verwendet. Beide Kandidaten-Actors erfüllen diese
Isolationsbedingung. Diese Produktregeln machen den erwarteten Wait-Zyklus
plausibel; sie beweisen nicht, dass die konkreten Prädikate mit dem tatsächlichen
Plan auf die zwei vorgesehenen KEY-Ressourcen abgebildet werden oder dass der
Deadlockgraph genau diese einfachen Modi ausgibt. Der Pflichtnachweis bleibt der
reale Graph samt Ressourcen, gehaltenen/angeforderten Modi, Opfer und Survivor.
Konversionsmodi werden aus dem beobachteten Graphen gelesen, nicht aus dem
Szenariotitel abgeleitet.

Der Offlinegraphprüfer wendet die in `SRC-004` dokumentierte Kompatibilität für
`S`, `U`, `X`, `RangeS-S`, `RangeS-U`, `RangeI-N` und `RangeX-X` an. Er verlangt
für jeden Actor, dass seine angeforderte Sperre mit einer vom anderen Actor
gehaltenen Sperre inkompatibel ist. Dadurch genügt die bloße Präsenz beider
Actors als Owner und Waiter nicht mehr als Zyklusbeleg. Unbekannte Modi bleiben
`FAIL`, bis ihre Kompatibilität quellenbasiert ergänzt ist. Diese Offlineprüfung
belegt weiter weder XML-Herkunft noch einen realen Enginezyklus.

## Pflichtnachweis für einen Varianten-PASS

- Beide Actors müssen im Deadlockgraph an dieselbe markergebundene Datenbank,
  Tabelle, Index und HoBT gebunden sein. Der Graph muss genau zwei verschiedene
  KEY-Ressourcen auf diesem Index zeigen. Auf jeder Ressource hält ein Actor
  und wartet der andere; über beide Ressourcen müssen die Wait-Kanten den Zyklus
  schließen. Die beobachteten Modi und `requestType=wait` belegen die gekreuzten
  Kanten. Ein einzelner KEY mit beidseitiger Konversion ist eine andere Variante
  und qualifiziert diesen Versuch nicht.
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

## Status der Methoden- und Safety-Gates

Der unabhängige Review der überarbeiteten Zwei-Ressourcen-Methode vom
22. November 2026 fand nach Korrektur einer P2-Dokumentationsinkonsistenz keine
offenen P1/P2 im begrenzten Draftumfang. Der eigentliche Demoablauf wurde danach
auf allen drei freigegebenen Builds integriert und laufzeitqualifiziert. Der
Abgleich mit der CON-002-Kandidatenbeschreibung steht in der
[Szenarioanalyse](LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md): CON-002 beschreibt
einen Einzelwait, während CON-006 hier zwei KEY-Ressourcen in einem Zyklus
belegt. Es wird weder eine fertige CON-002-Implementierung noch deren
Laufzeitverhalten unterstellt. Die abgeschlossene Matrix gilt für die
aufgeführten gepinnten Builds und isolierten Ausführungsgrenzen; sie ist keine
allgemeine Supportzusage. Der Offlinevertrag bleibt eine Formprüfung und ersetzt
den realen Enginebeleg nicht.

## Quellen und Grenzen

- [`SRC-004`: Transaction locking and row versioning guide](../Research/SOURCE_REGISTER.md#src-004) beschreibt Schlüsselbereichsmodi, ihre Kompatibilität, Voraussetzungen und die Optimized-Locking-Bedingung für `RangeI-N`. Die drei Feasibility-Piloten nutzen drei geordnete Indexwerte und gekreuzte Einfügungen in die jeweils andere, durch einen mittleren Wert getrennte Indexlücke. Alle drei Builds haben diese Ressourcenfolge im Deadlockgraph belegt.
- [`SRC-066`: Deadlocks guide](../Research/SOURCE_REGISTER.md#src-066) beschreibt Deadlockgraphen und Opferauflösung.
- [`SRC-068`: system_health](../Research/SOURCE_REGISTER.md#src-068) beschreibt die vorhandene, begrenzte Deadlockereignisquelle.

Die früheren isolierten Feasibility-Piloten änderten weder CON-002 noch den
validierten CON-006-Grundfall. Sie waren Vorarbeiten zur anschließenden
vollständigen Manifestintegration und Buildqualifikation.

## Begrenzter statischer Graphvertrag

`Tests/Static/con006_range_graph_contract.py` prüft synthetisch oder später
bereitgestelltes Deadlock-XML auf genau zwei an die erwarteten SPIDs und eine
markergebundene Datenbank gebundene Prozesse, ein Opfer sowie genau zwei
verschiedene KEY-Ressourcen derselben Tabelle, desselben Indexes und derselben
HoBT. Auf jeder Ressource muss ein Actor halten und der andere mit
`requestType=wait` warten. Über beide Ressourcen müssen die Wait-Kanten den
Zyklus schließen. Der Vertrag erzwingt kein bestimmtes Lockmoduspaar wie
`RangeS-S`/`RangeI-N`, da der Entwurf die tatsächlichen Modi nicht vorwegnimmt.

`evaluate_range_capture` bindet diese Formprüfung zusätzlich an die
caller-gelieferte Ereignisquelle `system_health`, den Eventnamen
`xml_deadlock_report`, genau ein passendes Ereignis im RFC-3339-Laufzeitfenster,
die Actor-/SPID-Zuordnung sowie das Graphopfer mit Fehler 1205 und den anderen
Actor als erfolgreichen Survivor. Für den Range-Deadlockarm verlangt der
Range-Capturevertrag außerdem je Actor dessen erwarteten Insert-Schlüssel,
`ROLLED_BACK`/1205 für das Opfer, bestätigtes `INSERTED` ohne Fehler für den
Survivor und den exakten Endbestand aus Anfangsbestand plus Survivor-Einfügung.
Das ist dieselbe Offline-Korrelationsgrenze wie beim Konversionsvertrag; sie
stellt keine Herkunftsattestation dar.

Der Graphprüfer akzeptiert im begrenzten Range-Offlineprofil ausschließlich
`requestType="wait"`. Der Kandidat ist eine Einfügebereichs-Wartevariante;
Konversions- oder andere Requesttypen gehören nicht in diesen Vertrag und
ergeben `FAIL`, selbst wenn ihre Moduswerte sonst kompatibel wären. Das ist ein
enger Graphvertrag, keine Behauptung über ein vollständiges SQL-Server-XML-
Schema. Eine spätere Erweiterung erfordert eine eigene Quellenprüfung und
Gegenfälle.

## Ergebnis der isolierten SQL-Server-Runtime-Matrix

Am 22. November 2026 bestand je ein begrenzter Versuch auf den folgenden
digest-gepinnten SQL-Server-Builds in eigenen, netzwerkisolierten Containern
mit 2 CPUs und 4 GiB Speicher:

| SQL-Server-Build | Graphzeichen | Deadlockarm | Serieller Kontrollarm | Optimized Locking |
|---|---:|---|---|---|
| 2019 `15.0.4500.2` | 5.495 | PASS | PASS | DMV-Eigenschaft nicht verfügbar (`null`) |
| 2022 `16.0.4305.5` | 14.105 | PASS | PASS | DMV-Eigenschaft nicht verfügbar (`null`) |
| 2025 `17.0.5035.5` | 8.698 | PASS | PASS | vor/nach beiden Armen unverändert aus (`0`) |

Jeder Build lieferte genau ein passendes `system_health`-Deadlockereignis. Der
Graph enthielt zwei verschiedene KEY-Ressourcen auf derselben markergebundenen
Tabelle, demselben Index und derselben HoBT; beide Wait-Kanten schlossen den
Zyklus mit `requestType=wait`. Actor A war vor der Freigabe von B nachweislich
blockiert. Ein Actor wurde mit Fehler 1205 zurückgerollt, der Survivor fügte
ein; die serielle Kontrolle fügte beide Schlüssel ohne Deadlock ein. Der exakte
Endbestand und die Entfernung der markergebundenen Datenbank und des jeweiligen
Containers wurden bestätigt. Keine Datenbankoption wurde umgestellt.

Diese erste Matrix belegte die Machbarkeit der Methode. Die nachfolgende
vollständige Demo- und Cleanupmatrix ist im Abschnitt
„Vollständige Demoqualifikation“ dokumentiert.

## Vollständige Demoqualifikation

Die Rangevariante ist als eigene Phase in
[`manifest.json`](../../Demos/07_Concurrency/CON-006_Deadlock_Cycle/manifest.json)
integriert. Jeder Mehrsessionarm ist auf 45 Sekunden begrenzt; das gesamte
Manifest hat 180 Sekunden Laufzeit und 60 Sekunden Cleanup. Actor- und
Observer-Wartezeiten sind begrenzt. Die Reihenfolge wird durch Signale sowie
die beobachteten KEY-Range-Sperren und die reale Blockierung gesteuert; feste
Zeitverzögerungen erzeugen den Konflikt nicht.

Der Qualifikationsrunner
[`con006_full_demo_qualification.py`](../../Tests/Runtime/con006_full_demo_qualification.py)
startet je Ausführung einen eigenen digest-gepinnten SQL-Server-Container ohne
Netzwerk und mit 2 CPUs/4 GiB. Er prüft Enginebuild, Containerlabel und
Ressourcenbegrenzungen, führt alle Manifestphasen aus, bestätigt nach dem
markergeprüften Datenbankcleanup die Datenbankabwesenheit und entfernt nur den
eigenen zuvor verifizierten Container. Ein fehlgeschlagener Cleanup oder
Laufvertrag liefert keinen PASS.

Die vollständige Demo bestand am 22. November 2026 jeweils einmal auf diesen
Builds:

| SQL-Server-Build | Ergebnis | Cleanup |
|---|---|---|
| 2019 `15.0.4500.2` | PASS – alle 19 Phasen | Datenbank- und Containerabwesenheit bestätigt |
| 2022 `16.0.4305.5` | PASS – alle 19 Phasen | Datenbank- und Containerabwesenheit bestätigt |
| 2025 `17.0.5035.5` | PASS – alle 19 Phasen | Datenbank- und Containerabwesenheit bestätigt |

Die Aufrufe lauten `python Tests/Runtime/con006_full_demo_qualification.py
--product-major-version 15`, `16` und `17`. Die drei Läufe bestanden den
Deadlockgraphvertrag, genau ein Opfer mit Fehler 1205, den fehlerfreien
Survivor, den exakten Deadlock-Endbestand, den getrennten seriellen Kontrollarm
mit beiden Inserts und exaktem Fünf-Schlüssel-Endbestand sowie die
Abwesenheitsprüfungen. Sie qualifizieren die vollständige Demo auf diesen
Builds und Ressourcenlimits, nicht allgemeine Performanceeffekte oder beliebige
Builds.

`evaluate_range_control` prüft nun den seriellen Kontrollarm auf zwei
caller-gelieferte erfolgreiche Actorresultate, getrennte Actor- und
erwartete Schlüsselzuordnungen sowie die tatsächlich gemeldete
Actor-zu-Schlüssel-Zuordnung jeder Einfügung. Erwartete und beobachtete
Zuordnungen müssen übereinstimmen. Zusätzlich verlangt er vollständige
Übereinstimmung des beobachteten finalen
Schlüsselsatzes mit dem erwarteten Anfangssatz plus genau zwei Einfügungen und
null passende Deadlockereignisse. Fehlende Pflichtfelder ergeben
`NOT_PROVEN`; widersprüchliche Werte ergeben `FAIL`. Schlüsselwerte bleiben
Eingaben des Aufrufers. Ein synthetischer `PASS` authentifiziert weder die
Erhebung noch den tatsächlichen Insert- oder Tabellenzustand.

Das ist ausschließlich eine Formprüfung caller-gelieferter XML- und
Identitätswerte. Sie authentifiziert weder `system_health`-Herkunft noch
Run-Token, Zeitfenster, Actorresultate, Opferfehler 1205 oder Cleanup. Ein
synthetischer PASS belegt keinen Deadlocklauf. Diese Gates werden separat durch
die im vorstehenden Abschnitt gebundene Runtimeausführung erfüllt; der
statische Kontrollarmprüfer allein schließt sie nicht.
