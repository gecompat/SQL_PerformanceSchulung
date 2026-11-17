# CON-006 – Quellen- und Methodenprüfung der Schlüsselbereichsvariante

| Merkmal | Wert |
|---|---|
| Prüfdatum | 17. November 2026 |
| Prüfumfang | `CON006_RANGE_DEADLOCK_METHOD.md`, CON-002-Kandidatenbeschreibung und Primärquellen `SRC-004`/`SRC-066` |
| Prüfart | quellenbasierte Methodenprüfung im Rahmen der Ausarbeitung; keine SQL-, Lab- oder Runtimeausführung |
| Ergebnis | kein fachlicher Widerspruch im Erstreview gefunden; unabhängige Gegenprüfung sowie Build-, Graph- und Cleanupnachweis bleiben erforderlich |

## Quellenbefund

Die aktuelle Microsoft-Anleitung zu Transaktionssperren beschreibt
`RangeS-S` als Bereichs- plus Shared-Resource-Sperre für einen
`SERIALIZABLE`-Bereichsscan und `RangeI-N` als Einfügebereichsprüfung. In ihrer
Kompatibilitätsmatrix ist eine angeforderte `RangeI-N`-Sperre mit einer bereits
gehaltenen `RangeS-S`-Sperre inkompatibel. Für Schlüsselbereichssperren verlangt
die Anleitung `SERIALIZABLE` und einen Index, den der Optimierer tatsächlich für
das Bereichsprädikat verwendet. Unter Optimized Locking wird `RangeI-N` laut
derselben Quelle erworben, wenn mindestens eine Transaktion der Instanz
`SERIALIZABLE` verwendet. Das stützt die Lockhypothese, beweist aber nicht die
Ressourcenabbildung der vorgeschlagenen konkreten Prädikate.

Die [Quellenregistrierung `SRC-004`](../Research/SOURCE_REGISTER.md#src-004)
bindet diese Herstelleranleitung. `SRC-066` beschreibt Deadlockgraph,
Opferauflösung und Fehler 1205. Diese Quellen schreiben weder ein verbindliches
Graph-XML-Schema noch den exakten Graph für die vorgeschlagene Abfragefolge vor.

## Methodenbefund

Die beiden leeren Suchbereiche `(20, 40)` und `(60, 80)` liegen bei den
vorgeschlagenen Schlüsselwerten `10` und `90` zwischen denselben benachbarten
Indexschlüsseln. Daraus folgt als ausdrücklich zu prüfende Hypothese, dass beide
Bereichslesungen dieselbe physische KEY-Ressource schützen könnten. Halten beide
Actors diesen Schutz und fordert danach jeder eine Einfügung in den jeweils
anderen gelesenen Bereich an, ist ein Wait-Zyklus plausibel. Das ist eine
fachliche Ableitung aus Indexaufbau und Hersteller-Kompatibilitätsmatrix, kein
beobachteter Enginegraph.

Der Vergleich mit der freigegebenen
[CON-002-Kandidatenanalyse](LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md#34-vierte-fachliche-kandidatengruppe-planlebenszyklus-und-concurrency)
ergibt ein unterscheidbares Lernziel: CON-002 ist dort als einzelner
Schlüsselbereichs-Wait mit späterer Freigabe beschrieben; die CON-006-Variante
soll zusätzlich den geschlossenen Deadlockzyklus, sein Opfer und den Survivor
zeigen. Die Kandidatenanalyse ist kein ausgeführter CON-002-Detailvertrag. Die
Methodengates wurden deshalb so präzisiert, dass sie auf diese vorhandene
Quelle verweisen, ohne ein nicht vorhandenes ausführbares Artefakt zu behaupten.

Der Entwurf verlangt bereits die wesentlichen Enginebelege: identische
Datenbank, Objekt, Index, HoBT und physische KEY-Ressource im Graph; tatsächliche
gehaltene und angeforderte Sperrmodi; genau ein Opfer mit Fehler 1205; einen
bestätigten Survivor; sowie den erfolgreichen seriellen Kontrollarm. Diese
Kriterien verhindern, dass bloßes Blocking als Varianten-PASS ausgegeben wird.

## Befunde und verbleibende Gates

| Befund | Bewertung | Folge |
|---|---|---|
| `RangeS-S`/`RangeI-N`-Kompatibilität als Lockhypothese | belegt durch `SRC-004` | Der reale Graph muss die konkreten Sperren und dieselbe KEY-Ressource nachweisen. |
| Lernziel gegenüber CON-002 | unterscheidbar anhand der freigegebenen Kandidatenanalyse | Der Einfügewait von CON-002 wird nicht als Deadlocknachweis ausgegeben. |
| Fehlender ausführbarer CON-002-Detailvertrag | korrekt als Planungsgrenze dokumentiert | Kein Verhalten der nicht implementierten Kandidatenvariante wird vorausgesetzt. |
| Build- und Runtimeverhalten | nicht geprüft | Isolierter Pilot, Graphprüfung, serieller Kontrollarm und markergebundener Cleanup bleiben offen. |

Dieses Erstreview fand keine P1/P2-Befunde im geprüften Quellen- und
Entwurfsumfang. Es ist keine unabhängige Gegenprüfung und erteilt keine SQL-,
Demo-, Engine- oder Versionsfreigabe. Der qualifizierte CON-006-Grundfall und
die Konversionsvariante bleiben unverändert; eine menschliche Generalprobe ist
nicht Teil dieser Prüfung.

## Quellen

- `SRC-004`, [Transaction locking and row versioning guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide?view=sql-server-ver17), abgerufen am 17. November 2026.
- `SRC-066`, [Deadlocks guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-deadlocks-guide?view=sql-server-ver17), aktueller Quellenregistereintrag.
