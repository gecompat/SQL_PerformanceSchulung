# IDX-010 – Methodenentwurf für geordnete nicht gruppierte Columnstore-Indizes

**Status:** `METHOD_DRAFT` – gelber Offlineentwurf, keine Demo- oder Laufzeitfreigabe  
**Geltungsbereich:** SQL Server 2025, nicht gruppierter Columnstore-Index (NCCI) auf einer Rowstore-Tabelle  
**Bestehende Demo:** IDX-010 bleibt unverändert und behandelt gruppierte Columnstore-Indizes (CCI).

## Lernfrage und Aussagegrenze

Der Entwurf prüft, ob `ORDER (EventDate)` bei einem geordneten NCCI die
Überlappung geeigneter Segmente gegenüber demselben ungeordneten NCCI reduziert
und dadurch eine selektive Bereichsabfrage mehr Segmente überspringen kann.
Microsoft beschreibt geordnete Columnstore-Indizes als Best-Effort-Sortierung;
Sortiergüte und Nutzen hängen unter anderem von Indexart, Datenmenge, Speicher,
Parallelität und Buildmodus ab. Die Funktion kann den Indexaufbau verlängern.
Aus der Syntax oder einem einzelnen Lauf folgt weder ein allgemeiner
Leistungsgewinn noch eine Eignung für einen beliebigen OLTP-Workload.

Der Methodenentwurf qualifiziert weder eine Produktversion noch eine Edition,
einen konkreten Build, eine Laufzeitwirkung oder einen Performanceclaim. Er
erweitert und ändert keine Phase, kein Manifest und kein Laufzeitprofil der
bestehenden IDX-010-Demo.

## Vergleichsaufbau

1. Verwende zwei getrennte Wegwerf-Datenbanken mit identischem Schema,
   deterministisch erzeugten synthetischen Zeilen und identischem Seed. Ein
   gebundener Datenbestandshash und exakte Zeilenzahl müssen vor dem Indexbau
   übereinstimmen.
2. Halte die Tabelle als Rowstore mit demselben nicht nach `EventDate`
   geordneten Clustered Index. Erzeuge je Datenbank dieselbe NCCI-Spaltenliste,
   die `EventDate` und alle von der Testabfrage benötigten Werte enthält.
3. Der Kontrollarm baut den NCCI ohne `ORDER`; der Versuchsarm verwendet
   `ORDER (EventDate)`. Beide Builds laufen offline mit `MAXDOP = 1`; die
   Option gilt identisch für beide Arme. Damit ist die Buildparallelität
   kontrolliert; höhere Parallelität kann laut Microsoft zusätzliche
   Segmentüberlappung verursachen, weil jeder Thread nur lokal sortiert.
   `MAXDOP = 1` garantiert für diesen NCCI dennoch keine vollständige
   Ordnung. DDL, Daten,
   Indexspalten, Kompression, Partitionierung, Buildoptionen und Reihenfolge
   der Ausführung sind ansonsten gleich. Führe die Builds nacheinander aus
   und schreibe keine Daten zwischen Build und Messung.
4. Das synthetische Profil muss ausreichend viele vollständige komprimierte
   Rowgroups ergeben, um Segmentüberlappung sinnvoll zu vergleichen. Es mischt
   deterministisch mehrere Datumsbereiche innerhalb jeder Ladeportion, damit
   der ungeordnete Kontrollarm keine durch Ladefolge zufällig vorgegebene
   Datumsordnung erhält. Zeilenzahl, Generator und erwartete Rowgroupzahl
   werden vor einem Pilot im ausführbaren Vertrag festgelegt. Der Pilot ist
   nur aussagekräftig, wenn der Kontrollarm nach der unterstützten
   Order-Quality-Auswertung tatsächlich überlappende `EventDate`-Segmente hat;
   andernfalls ist die Datengestaltung kein gültiger Gegenfall.
5. Die Testabfrage verwendet denselben selektiven `EventDate`-Bereich und
   dieselbe Aggregation in beiden Armen. Exaktes Ergebnis und Zeilenidentität
   müssen übereinstimmen. Der tatsächliche Ausführungsplan muss jeweils den
   vorgesehenen NCCI-Scan zeigen. Wird der NCCI nicht verwendet, ist der
   Vergleich für diesen Lauf `NOT_PROVEN`; kein erzwungener Zugriffspfad darf
   unbemerkt als Optimizerwahl dargestellt werden.

## Evidenz und Auswertung

- Binde Buildversion, Edition, Compatibility Level, Datenbank- und
  Indexmetadaten, Buildoptionen, Datenhash, Zeilenzahl und die finale
  `column_store_order_ordinal` für `EventDate` an beide Arme.
- Erfasse Rowgroupzustand und Segmentmetadaten für genau den geprüften Index.
  Als Ausgangspunkt dient Microsofts offizielles Order-Quality-Skript, das
  geeignete Datentypen und Encodings anhand von `sys.column_store_segments`
  auswertet. Es schließt nicht unterstützte Metadatenformen aus. Ein
  ausgelassenes oder nicht auswertbares Segment ist kein Null-Overlap-Beleg.
- Die Spalten `min_data_id`, `max_data_id`, `min_deep_data` und
  `max_deep_data` sind laut Katalogdokumentation interne Metadaten. Das
  Methodenpaket darf ihre Interpretation nicht selbst nachbauen oder als
  stabile öffentliche API ausgeben; es verwendet die geprüfte Microsoft-
  Auswertung nur, wenn Typ und Encoding unterstützt sind, andernfalls
  `NOT_PROVEN`.
- Erfasse den tatsächlichen Plan und Ergebnisgleichheit als Mechanismusevidenz.
  Verwende `SET STATISTICS IO` für die dokumentierten `Segment reads`- und
  `segment skipped`-Ausgaben je Testabfrage und binde sie an den jeweiligen
  tatsächlichen Plan. Das direkte Skip-Ergebnis muss mit identischen
  Resultaten, selektivem Prädikat und ausgewähltem NCCI vorliegen. Die
  Order-Quality-Metrik beschreibt zusätzlich die physische Überlappung; sie
  ersetzt diese Queryevidenz nicht.
- Akzeptanz für den Mechanismuspilot: der Kontrollarm zeigt messbare
  `EventDate`-Segmentüberlappung; die geordnete Variante weist bei gleicher
  Segmentzahl weniger Überlappung und die Testabfrage mehr übersprungene bzw.
  weniger gelesene Segmente auf. Fehlt die Überlappung im Kontrollarm, ist die
  Ordnungsgüte wegen Typ/Encoding nicht auswertbar oder fehlt ein gebundener
  `SET STATISTICS IO`-Wert, lautet das Ergebnis `NOT_PROVEN` statt `PASS`.
- Ein Performancevergleich wäre ein separates Folgepaket mit vorab fixiertem
  Messprotokoll, Wiederholungen, Cachezustand, Laufreihenfolge, Messgrößen und
  Ressourcenobergrenzen. Bis dahin werden weder Laufzeit noch I/O-Vorteil
  quantifiziert.

## Voraussetzungen, Stop und Cleanup für einen späteren Pilot

Vor jeder SQL-Freigabe muss ein unabhängiger Methodenreview den vollständigen
Versuchsvertrag bestätigen. Zusätzlich sind ein konkreter SQL-Server-2025-
Build und eine Edition festzulegen, die Verfügbarkeit von `ORDER` für NCCI,
die Voraussetzungen des ausgewählten Online-/Offline-Builds und die
erforderlichen Rechte zu prüfen. Das offizielle Featureblatt nennt `ORDER` für
NCCI ab SQL Server 2025; Onlineoperationen sind editionsabhängig.

Der Pilot benötigt eine eigene dedizierte Wegwerfinstanz. Da `MAXDOP = 1` die
Builddauer eines geordneten Columnstore-Index deutlich verlängern kann, muss
das numerische Zeitbudget den gemessenen Aufbau beider NCCI-Builds einschließen;
ein Timeout beendet den Pilot fail-closed und führt zum Cleanup. Vor Start sind
Instanzidentität, Image-Digest, CPU-/Speicher-/Datenträgergrenzen und freie
Kapazität zu prüfen. Ein numerisches Gesamtzeitbudget für Aufbau, beide Builds,
Abfragen und Cleanup sowie Höchstwerte für Datenbankgröße und Speicherbedarf
müssen im freizugebenden Laufvertrag stehen. Ohne diese konkreten Werte,
geeignete Isolation oder einen sauberen Preflight: `SKIP`, keine Verbindung und
keine Änderung. Aktive fremde Container, produktive Instanzen und die bestehende
IDX-010-Umgebung werden nicht verwendet.

Beide Datenbanken tragen die bestehenden Framework-Eigentumsmarker. Cleanup
prüft vor dem Entfernen jeden Marker und Run-Token exakt; es löscht ausschließlich
die beiden nachweislich eigenen Datenbanken. Bei abgebrochenem oder
uneindeutigem Cleanup wird der Lauf nicht als bestanden gewertet.

## Noch erforderliche Gates

1. Unabhängiger Review dieses Methodenentwurfs samt konkreter Daten-,
   Rowgroup-, Rechte- und Messdefinition.
2. Numerische Ressourcen-, Zeit- und Cleanupobergrenzen sowie verifizierter
   SQL-Server-2025-Image-Digest/Build/Edition.
3. Separat autorisierter isolierter Pilot; dessen Ergebnis gilt nur für den
   erfassten Build, die gewählten Indexoptionen, den Datentyp/Encoding und die
   synthetische Verteilung.
4. Ein eigener, späterer Performancevertrag, falls quantitative Aussagen
   gewünscht sind.

Die menschliche Generalprobe ist ausgeschlossen. Bis Gates 1–3 erfüllt sind,
bleibt die Erweiterung `DEFER` und die bestehende IDX-010-Qualifikation gilt nur
für die bisherige CCI-Demo.

## Quellen

- `SRC-063`: [Performance tuning with ordered columnstore indexes](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/ordered-columnstore-indexes?view=sql-server-ver17)
- `SRC-017`: [Columnstore query performance](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/columnstore-indexes-query-performance?view=sql-server-ver17), einschließlich der dokumentierten `SET STATISTICS IO`-Ausgabe für gelesene und übersprungene Segmente.
- `SRC-165`: Microsoft Learn, [CREATE COLUMNSTORE INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-columnstore-index-transact-sql?view=sql-server-ver17), [sys.column_store_segments](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-segments-transact-sql?view=sql-server-ver17) und [What's new in columnstore indexes](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/columnstore-indexes-what-s-new?view=sql-server-ver17); ergänzend Microsofts [Order-Quality-Skript](https://github.com/microsoft/sql-server-samples/blob/master/samples/features/columnstore/ordered-columnstore/order-quality.sql).

Die Microsoft-Dokumentation beschreibt, dass geordnete Columnstore-Builds mit
`MAXDOP > 1` je Thread lokal sortieren und dadurch mehr Segmentüberlappung
erzeugen können. `MAXDOP = 1` wird deshalb hier als kontrollierte
Versuchsbedingung gewählt, nicht als allgemeine Buildempfehlung oder Garantie
vollständiger Ordnung. Der Offlinebuild bleibt von der verfügbaren
Arbeitsbereichsspeichermenge und dem konkreten NCCI-Verhalten abhängig.

