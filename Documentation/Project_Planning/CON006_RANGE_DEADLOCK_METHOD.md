# CON-006 – Methodenentwurf für einen Schlüsselbereichs-Deadlock

| Merkmal | Wert |
|---|---|
| Status | `METHOD_DRAFT` – Runtime-Matrix 2019/2022/2025 und unabhängiger Methodenreview bestanden; vollständige Demoqualifikation offen |
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
untersucht. Beim Range-Kandidaten sind die gelesenen Schlüsselbereiche leer und
die Einfügungen konkurrieren um die Indexlücke. Das ist ein fachlich möglicher
Lernzuwachs, aber noch kein nachgewiesenes Engineverhalten.

## Kandidatenaufbau für einen späteren isolierten Pilot

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

Die konkreten Prädikate und Reihenfolgen sind ein kontrollierbarer
Versuchsvorschlag, keine Garantie dafür, dass der Optimierer beide Abfragen auf
den gewünschten Index ausführt oder dass beide KEY-Ressourcen gegeneinander
warten. Ein Lauf ohne diesen Nachweis ist `NOT_PROVEN`, auch wenn ein Actor
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

## Gates

Der unabhängige Review der überarbeiteten Zwei-Ressourcen-Methode vom
22. November 2026 fand nach Korrektur einer P2-Dokumentationsinkonsistenz keine
offenen P1/P2 im begrenzten Draftumfang. Er ersetzt weder Quellen- noch
Runtimequalifikation. Vor einer ausführbaren Demo-Integration sind
der Abgleich mit der freigegebenen CON-002-Kandidatenbeschreibung in der
[Szenarioanalyse](LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md) und die Freigabe
eines isolierten Zielbuilds erforderlich. Derzeit liegt für CON-002 nur diese
Kandidatenbeschreibung, kein ausführbarer Detailvertrag vor; deshalb darf der
Abgleich weder eine fertige CON-002-Implementierung noch deren Laufzeitverhalten
unterstellen. Ein später veröffentlichter Detailvertrag muss vor einer
ausführbaren CON-006-Variante erneut berücksichtigt werden. Die drei
Feasibility-Piloten veränderten keine gemeinsam genutzte Instanz und erbrachten
je Build einen eigenen Graph- und Datenbank-/Container-Cleanupnachweis. Sie
stellen keine allgemeine Supportzusage und keine Demoqualifikation dar. Ein
bestandener synthetischer Offlinevertrag kann diese Gates nicht ersetzen. Die
vorgeschlagenen Obergrenzen und Recoveryregeln bleiben ein Draft; sie sind nicht
auf einer laufenden Engine als vollständiger Zeit-/Cleanupvertrag qualifiziert.

## Quellen und Grenzen

- [`SRC-004`: Transaction locking and row versioning guide](../Research/SOURCE_REGISTER.md#src-004) beschreibt Schlüsselbereichsmodi, ihre Kompatibilität, Voraussetzungen und die Optimized-Locking-Bedingung für `RangeI-N`. Die drei Feasibility-Piloten nutzen drei geordnete Indexwerte und gekreuzte Einfügungen in die jeweils andere, durch einen mittleren Wert getrennte Indexlücke. Alle drei Builds haben diese Ressourcenfolge im Deadlockgraph belegt.
- [`SRC-066`: Deadlocks guide](../Research/SOURCE_REGISTER.md#src-066) beschreibt Deadlockgraphen und Opferauflösung.
- [`SRC-068`: system_health](../Research/SOURCE_REGISTER.md#src-068) beschreibt die vorhandene, begrenzte Deadlockereignisquelle.

Die isolierten Feasibility-Piloten werten SQL aus, ändern aber weder CON-002 noch den validierten CON-006-Grundfall. Sie belegen die begrenzte Range-Methode auf den drei dokumentierten Builds, ersetzen aber weder den vollständigen CON-006-Zeit-/Cleanupvertrag noch Demo-Integration oder Releasequalifikation.

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

Die Matrix belegt die Machbarkeit dieser Methode auf genau diesen drei Builds.
Vollständiger Abfrageplan-/Optionenabgleich, unabhängiger Review der
überarbeiteten Zwei-Ressourcen-Methode, vollständige gemeinsame Zeit- und
Cleanupgrenzen, Demo-Integration und Releasequalifikation bleiben offen.

## Obergrenzen und Eigentums-Cleanup für weitere Qualifikation

Die drei Machbarkeitspiloten verwendeten feste Einzelzeitlimits für
SQL-Aufrufe, Actorprozesse und Signalwartezeiten und entfernte seine
markergebundene Datenbank. Er setzt jedoch noch nicht den vollständigen
CON-006-Zeitvertrag durch und ist daher kein Ersatz für dessen Runtime- und
Cleanupqualifikation. Ein weiterer qualifizierender Lauf muss die
Ein qualifizierender Demo-Lauf muss die CON-006-Runnerobergrenzen übernehmen:
höchstens 45 Sekunden je
Mehrsessionarm, 180 Sekunden Gesamtlaufzeit und 60 Sekunden Cleanup
([bestehendes Manifest](../../Demos/07_Concurrency/CON-006_Deadlock_Cycle/manifest.json)).
Alle Signal- und Waitschleifen verwenden eine gemeinsame monotone Armdeadline,
höchstens 50-ms-Pollintervalle und keine festen Delay-Reihenfolgen. Bei Deadline,
Abbruch oder unerwartetem SQL-Fehler werden beide Actorclients beendet, alle
eigenen Sessions auf Transaktionsende geprüft und keine nächste Phase gestartet.
Cleanup darf nur die beim Setup erzeugte Datenbank und die eigene markierte
XE-Session entfernen; es prüft vor Entfernung Run-Token, Datenbank-ID,
Sessionname, Ownermarker und Zielinstanz. Nach erfolgreichem Cleanup muss eine
unabhängige Abfrage die Datenbank- und XE-Sessionabwesenheit bestätigen. Läuft
dieser Eigentumsnachweis oder Cleanup in die 60-Sekunden-Grenze, lautet der
Lauf `FAIL_CLEANUP` und der Pilot stoppt. Im Abbruchpfad werden Actorclients
zuerst mit einem begrenzten Cancel beendet; ein `KILL` ist nur auf der eigenen
Wegwerfinstanz nach frischer Prüfung von SPID, Login, eindeutiger
`program_name`-Runmarke und Datenbank-ID zulässig, nie allein aufgrund einer
gespeicherten SPID. Der Rollback wird höchstens 30 Sekunden innerhalb des
60-Sekunden-Cleanupbudgets beobachtet. Bleibt eine eigene Session oder
Transaktion danach aktiv, wird nur der zuvor durch CID, exakten Namen, Image-ID
und Ownerlabel bestätigte Wegwerfcontainer gestoppt/entfernt; anschließend
müssen CID- und Namensabwesenheit unabhängig bestehen. Für Ziele ohne solch
einen frischen, verifizierbaren Containerbesitz gibt es keinen automatischen
Force-Recovery-Pfad; dort endet der Versuch `FAIL_CLEANUP`. Diese Grenzen sind
im aktuellen Pilotrunner noch nicht vollständig implementiert und müssen vor
Demoqualifikation unabhängig geprüft werden.

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
synthetischer PASS belegt keinen Deadlocklauf. Die überarbeitete Methode wurde
unabhängig geprüft; der vollständige gemeinsame Zeit- und Cleanupvertrag, der
Abfrageplan-/Optionenabgleich sowie Demo-Integration und Demoqualifikation
bleiben offen. Der statische Kontrollarmprüfer schließt diese Voraussetzungen
ebenfalls nicht.
