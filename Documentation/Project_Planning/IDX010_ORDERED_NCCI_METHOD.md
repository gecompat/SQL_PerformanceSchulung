# IDX-010 – Methodenentwurf für geordnete nicht gruppierte Columnstore-Indizes

**Status:** `METHOD_DRAFT` – gelber Offlineentwurf, keine Demo- oder Laufzeitfreigabe  
**Geltungsbereich:** SQL Server 2025, nicht gruppierter Columnstore-Index (NCCI) auf einer Rowstore-Tabelle  
**Bestehende Demo:** IDX-010 bleibt unverändert und behandelt gruppierte Columnstore-Indizes (CCI).

## Lernfrage und Aussagegrenze

Der Entwurf prüft, ob `ORDER (EventDayKey)` bei einem geordneten NCCI die
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
2. Halte die Tabelle als Rowstore mit demselben nicht nach `EventDayKey`
   geordneten Clustered Index. Erzeuge je Datenbank dieselbe NCCI-Spaltenliste,
   die `EventDayKey` und alle von der Testabfrage benötigten Werte enthält.
3. Der Kontrollarm baut den NCCI ohne `ORDER`; der Versuchsarm verwendet
   `ORDER (EventDayKey)`. Beide Builds laufen offline mit `MAXDOP = 1`; die
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
   Order-Quality-Auswertung tatsächlich überlappende `EventDayKey`-Segmente hat;
   andernfalls ist die Datengestaltung kein gültiger Gegenfall.
5. Die Testabfrage verwendet denselben selektiven `EventDayKey`-Bereich und
   dieselbe Aggregation in beiden Armen. Exaktes Ergebnis und Zeilenidentität
   müssen übereinstimmen. Der tatsächliche Ausführungsplan muss jeweils den
   vorgesehenen NCCI-Scan zeigen. Wird der NCCI nicht verwendet, ist der
   Vergleich für diesen Lauf `NOT_PROVEN`; kein erzwungener Zugriffspfad darf
   unbemerkt als Optimizerwahl dargestellt werden.

## Konkretes Profil für den unabhängigen Review

Das veröffentlichte Microsoft-Skript für die Ordnungsgüte lässt den Typ `date`
aus. Das Profil verwendet deshalb `EventDayKey bigint` als fortlaufenden
synthetischen Tagesschlüssel. Das Skript muss für jede der beiden Varianten
alle Segmente der Schlüsselspalte als auswertbar melden. Ein Wechsel des
Datentyps nach Sichtung der Ergebnisse erfordert ein eigenes Profil.

| Merkmal | Festlegung für den Pilotkandidaten |
|---|---|
| Daten und Ladefolge | `dbo.Events(EventId bigint NOT NULL, EventDayKey bigint NOT NULL)`. `EventId` ist der gruppierte eindeutige Primärschlüssel von 0 bis 4.194.303. `EventDayKey = (EventId * 1048573) % 4194304`. Der ungerade Faktor permutiert die Schlüssel eindeutig und mischt kurze und weite Abstände im physischen Primärschlüssel. Lade beide Arme nach denselben vier disjunkten ID-Bereichen mit je 1.048.576 Zeilen. Rechnerische und tatsächliche Segmentgrenzen werden getrennt beurteilt. |
| Datenidentität | Prüfe je Arm exakt 4.194.304 unterschiedliche IDs im festgelegten geschlossenen Bereich und null Abweichungen von der Schlüsselformel. Vergleiche außerdem SHA-256 über den vollständigen, nach `EventId` sortierten Strom aus UTF-8-Zeilen `EventId,EventDayKey` mit LF als Zeilenende und dezimalen Ganzzahlen ohne Gruppierung, Header oder BOM. Gib nur Digest und Zähler aus. |
| Index und Rowgroups | Eine Partition, gleiche NCCI-Spaltenliste `(EventDayKey, EventId)` und COLUMNSTORE-Kompression in beiden Armen. Erwartet sind vier vollständige komprimierte Rowgroups. Der Mechanismuslauf wertet nur vier vollständige Gruppen ohne Delta- oder gelöschte Zeilen je Arm aus. Ein anderer Aufteilungsschnitt endet als `NOT_PROVEN`. |
| Abfrage und Oracle | Halboffenes Intervall `EventDayKey >= 1048576 AND EventDayKey < 1052672`. Erwartet sind `COUNT_BIG(*) = 4096` und `SUM(EventDayKey) = 4303353856`. Die Bijektion und die geprüfte Fixture bestimmen die erwartete Zeilenidentität. Führe pro Arm eine markierte Abfrage in einer eigenen englischsprachigen SQL-Session aus und binde ihren tatsächlichen Plan sowie genau eine Tabellenmeldung mit Segmentzählern an diesen Aufruf. |
| Mindestbefund | In beiden Armen müssen gelesene und übersprungene Segmente zusammen vier ergeben. Die ungeordnete Kontrolle muss Segmente mit Überlappung enthalten. Der geordnete Arm muss höhere Ordnungsgüte und mindestens ein zusätzlich übersprungenes Segment zeigen. Andernfalls `NOT_PROVEN`. |
| Rollen | Eine lokale Einrichtungsidentität erstellt ausschließlich die zwei markierten Datenbanken und die Fixture. Das Beobachtungsprofil erhält Zugriff auf genau die beiden Testdatenbanken, Leserechte auf `dbo.Events`, die für das Profil erforderliche Metadatensicht und `SHOWPLAN` für die Testdatenbanken. Die Umsetzung prüft die effektiven Rechte vor Messung und benennt die konkreten Grants und ihre Rücknahme im Laufvertrag. |
| Buildkandidat | Linux/AMD64, SQL Server `17.0.5065.9`, `Enterprise Developer Edition (64-bit)`, Kompatibilitätsstufe 170. Der [OPTSP-Kataloglauf](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/45165364360) bestätigte Version und Edition für den unten genannten Digest. Der NCCI-Pilot muss diese Werte selbst vor der Fixture verifizieren. |
| Obergrenzen | Ein eigener Container mit 2 CPUs, 4 GiB RAM, ohne externes Netzwerk. Je Testdatenbank maximal 512 MiB Daten und 512 MiB Log, für TempDB insgesamt maximal 512 MiB Daten und 256 MiB Log. Ein Pilotversuch mit insgesamt 900 Sekunden für Start, Setup, Builds und Auswertung sowie einem separaten Cleanupfenster von 90 Sekunden. Das Profil ist ein Budgetvorschlag, dessen Eignung der Review und spätere Lauf prüfen. |

Binde die Ordnungsgüte an die [gesichtete Fassung des Microsoft-Skripts](https://github.com/microsoft/sql-server-samples/blob/c68199caedd6e843ee30cc982f469abdf25dec29/samples/features/columnstore/ordered-columnstore/order-quality.sql).
Beschränke die Auswertung auf das Zielobjekt, die Index-ID, die Partition und
die Schlüsselspalte. Ergänze beim Join auf `sys.index_columns` die Index-ID.
Die ausgewerteten Segment-IDs müssen mit den vier komprimierten Rowgroups
übereinstimmen. Die Schlüsselformel erzeugt eindeutige Werte. Bei vollständigen,
disjunkten Rowgroups muss deshalb jede Segmentgrenze in einem Arm eindeutig
sein und jedes Minimum unter dem zugehörigen Maximum liegen. Prüfe diese
Vorbedingung mit der gebundenen Beispielauswertung, bevor deren
`TOP (1)`-Abfragen zur Überlappung herangezogen werden. Bei gleichen Grenzen,
Mehrfachtreffern oder unvollständigen Segmentmetadaten lautet das Ergebnis
`NOT_PROVEN`.

## Evidenz und Auswertung

- Binde Buildversion, Edition, Compatibility Level, Datenbank- und
  Indexmetadaten, Buildoptionen, Datenhash, Zeilenzahl und die finale
  `column_store_order_ordinal` für `EventDayKey` an beide Arme.
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
  `EventDayKey`-Segmentüberlappung; die geordnete Variante weist bei gleicher
  Segmentzahl weniger Überlappung und die Testabfrage mehr übersprungene bzw.
  weniger gelesene Segmente auf. Fehlt die Überlappung im Kontrollarm, ist die
  Ordnungsgüte wegen Typ/Encoding nicht auswertbar oder fehlt ein gebundener
  `SET STATISTICS IO`-Wert, lautet das Ergebnis `NOT_PROVEN` statt `PASS`.
- Ein Performancevergleich wäre ein separates Folgepaket mit vorab fixiertem
  Messprotokoll, Wiederholungen, Cachezustand, Laufreihenfolge, Messgrößen und
  Ressourcenobergrenzen. Bis dahin werden weder Laufzeit noch I/O-Vorteil
  quantifiziert.

### SQL-Batches für Datenaufbau und Indexbau

Der [Setup-Baustein](../../Tests/Runtime/idx010_pilot_setup.py) erzeugt pro
Arm einen Tabellenaufbau, vier aufeinanderfolgende Ladebatches, einen
sortierten Lesestrom zum Identitätsnachweis und den Indexbau. Alle Batches
prüfen den genauen Serverbuild, die Edition, die Datenbank, die
Kompatibilitätsstufe, das Wiederherstellungsmodell und die fünf
Eigentumsmarker. Die Batches setzen Autocommit voraus. Der zusätzliche Marker
`SQLPERF.PilotProfile` und das Namenspräfix `SQLPERF_LAB_IDX010_NCCI_`
kennzeichnen die Pilotdatenbanken eindeutig.

Der spätere Runner muss beide Datenbanken mit diesen Markern und den
festgelegten Ressourcenobergrenzen bereitstellen. Vor dem ersten Indexbau
muss er beide sortierten Leseströme vollständig prüfen. Der erwartete
SHA-256-Digest ist
`bfa6e87fc9501d335d859b5d509d6ed466cd1a272e026cbd60e9657c065d955f`.
Die Prüfung liest jeweils eine Zeile und hält nur den laufenden Digest und
Zähler. Erst danach darf der Runner die beiden Indexbatches nacheinander
starten. Die [Offlineprüfungen](../../Tests/Static/test_idx010_pilot_setup.py)
sichern die Armtrennung, die Ladebereiche und den Identitätsnachweis ab.
Die SQL-Batches sind für den Methodenreview bestimmt.

### Offlineprüfung der Abfrageevidenz

Der [Offlineprüfer](../../Tests/Runtime/idx010_query_evidence.py) legt die
Abfrage mit `OPTION (MAXDOP 1)` für beide Arme fest. Er verlangt die exakte
Ergebniszeile, genau einen ausgeführten Scan des erwarteten NCCI sowie eine
eindeutige Segmentmeldung für `Events`. Mehrere Datenzugriffe, Zugriffshints,
ein abweichender Index oder widersprüchliche Segmentzähler verhindern die
Annahme. [Synthetische Regressionen](../../Tests/Static/test_idx010_query_evidence.py)
decken diese Ablehnungen ab. Die Shape-Anforderungen orientieren sich am
[Microsoft-Showplan-Schema](https://schemas.microsoft.com/sqlserver/2004/07/showplan/)
und müssen auf dem Pilotbuild durch die reale Ausgabe bestätigt werden.

Der [sqlcmd-Adapter](../../Tests/Runtime/idx010_sqlcmd_capture.py) erzeugt
einen Batch für genau eine Messabfrage und eine Abschlusszeile. Er startet
den ODBC-Client im Wegwerfcontainer über dessen feste ID und verbindet sich
per Loopback mit dem für den Lauf eingerichteten Reader. Das Passwort
gelangt über die Prozessumgebung zum Client. Plan und Ergebnis werden auf
Standardausgabe erwartet, die eindeutige Segmentmeldung auf dem separaten
Meldungskanal. Prozesslaufzeit und beide Ausgabeströme werden beim Lesen
begrenzt. Fehlende, mehrdeutige oder abgeschnittene Ausgabe bleibt
`NOT_PROVEN`.
[Microsoft-Referenz zu sqlcmd](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver17).

[Synthetische Prüfungen](../../Tests/Static/test_idx010_sqlcmd_capture.py)
verbinden den Decoder mit dem Abfrageprüfer. Format und Zuordnung der
tatsächlichen Engine-Ausgabe bleiben im Pilot zu bestätigen. Ordnungsgüte,
Indexmetadaten und SQL-Cleanup bleiben weitere Annahmebedingungen.

### Reihenfolge und Abbruch im Pilotlauf

Die [Ablaufsteuerung](../../Tests/Runtime/idx010_pilot_sequence.py) verlangt
die vollständige Identitätsprüfung beider Datenbestände vor dem ersten
Indexbau. Nach dem Aufbau prüft sie je Arm Indexidentität, Ordnungsposition
und vier vollständige komprimierte Rowgroups. Die Metadatenaufnahme liefert
die Zahl überlappender Segmentpaare aus der geprüften Microsoft-Auswertung.
Bei vier vollständig abgedeckten Segmenten entspricht weniger Überlappung
einer höheren Ordnungsgüte. Für `PASS` muss der geordnete Arm zusätzlich mehr
Segmente in der Ergebnisabfrage überspringen.

Die Ablaufsteuerung übergibt dem Transport eine gemeinsame Laufzeitgrenze
von 900 Sekunden und eine getrennte Cleanupfrist von 90 Sekunden. Sie
registriert jede Zielbereitstellung vor dem ersten Aufruf und fordert auch
bei Fehlern während des Instanzstarts oder der Bereitstellung Cleanup an.
`FAIL_CLEANUP` hat Vorrang vor einem positiven Befund. Der konkrete
Container- und SQL-Transport muss die Fristen durchsetzen, Eigentum vor dem
Abbau prüfen und die bestätigte Abwesenheit melden. Bereitstellung, Rechtevergabe,
Metadatenaufnahme und Abbau stehen noch aus. Der Messadapter ist als
einzelner Teil des Transports implementiert.
Die [Offlineprüfungen](../../Tests/Static/test_idx010_pilot_sequence.py)
verwenden einen simulierten Transport.

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
2. Numerische Ressourcen-, Zeit- und Cleanupobergrenzen sowie ein für den
   späteren Lauf unveränderlich gebundener SQL-Server-2025-Image-Digest,
   Build und tatsächliche Edition.
3. Separat autorisierter isolierter Pilot; dessen Ergebnis gilt nur für den
   erfassten Build, die gewählten Indexoptionen, den Datentyp/Encoding und die
   synthetische Verteilung.
4. Ein eigener, späterer Performancevertrag, falls quantitative Aussagen
   gewünscht sind.

Die menschliche Generalprobe ist ausgeschlossen. Bis Gates 1–3 erfüllt sind,
bleibt die Erweiterung `DEFER` und die bestehende IDX-010-Qualifikation gilt nur
für die bisherige CCI-Demo.

### Quellenabgleich zu Build und Edition (17. November 2026)

Der frühere Kataloglauf zu PR #941 beobachtete Build `17.0.5065.9` aus
`mcr.microsoft.com/mssql/server:2025-latest` mit dem Image-Digest
`sha256:05644dad1266ca3d445d1e8f6d2ebb9a6a03df9a39376e0f7b48917356dca9d9`.
Seine Containerkonfiguration setzte `MSSQL_PID=Developer`. Das ist ein
historischer Kandidat: Der Katalogbeleg weist weder NCCI-`ORDER`-Verhalten
nach noch enthält er eine ausgewertete `SERVERPROPERTY('Edition')`-Ausgabe.
Ein beweglicher Tag ist außerdem kein künftiger Image-Lock; ein Pilot müsste
den Digest selbst festsetzen und seine laufende Version und Edition erfassen.

Microsoft dokumentiert `ORDER` für nicht gruppierte Columnstore-Indizes ab
SQL Server 2025. Die Editionsmatrix führt Columnstore für Enterprise,
Standard und Express auf; Developer-Editionen übernehmen laut derselben
Matrix die jeweilige Enterprise- oder Standard-Funktionalität. Sie weist
`ORDER` für NCCI nicht separat je Edition aus. Der Entwurf verlangt Offline-
Builds; die editionsbeschränkte Online-Indexoperation ist damit keine
Voraussetzung dieses Versuchs. Das ist eine quellenbasierte Eingrenzung, keine
projektseitige Engine- oder Editionsqualifikation. Die konkreten Image-, Build-
und Editionwerte bleiben am Pilot gebunden. Quellen: `SRC-083` und `SRC-165`.

## Quellen

- `SRC-063`: [Performance tuning with ordered columnstore indexes](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/ordered-columnstore-indexes?view=sql-server-ver17)
- `SRC-017`: [Columnstore query performance](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/columnstore-indexes-query-performance?view=sql-server-ver17), einschließlich der dokumentierten `SET STATISTICS IO`-Ausgabe für gelesene und übersprungene Segmente.
- `SRC-165`: Microsoft Learn, [CREATE COLUMNSTORE INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-columnstore-index-transact-sql?view=sql-server-ver17), [sys.column_store_segments](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-segments-transact-sql?view=sql-server-ver17) und [What's new in columnstore indexes](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/columnstore-indexes-what-s-new?view=sql-server-ver17); ergänzend Microsofts [Order-Quality-Skript](https://github.com/microsoft/sql-server-samples/blob/master/samples/features/columnstore/ordered-columnstore/order-quality.sql).
- `SRC-083`: Microsoft, [SQL Server 2025 editions](https://learn.microsoft.com/en-us/sql/sql-server/editions-and-components-of-sql-server-2025?view=sql-server-ver17), für Editionstypen, Developer-Funktionsumfang und Columnstore-/Onlineoperationsmatrix.

Die Microsoft-Dokumentation beschreibt, dass geordnete Columnstore-Builds mit
`MAXDOP > 1` je Thread lokal sortieren und dadurch mehr Segmentüberlappung
erzeugen können. `MAXDOP = 1` wird deshalb hier als kontrollierte
Versuchsbedingung gewählt, nicht als allgemeine Buildempfehlung oder Garantie
vollständiger Ordnung. Der Offlinebuild bleibt von der verfügbaren
Arbeitsbereichsspeichermenge und dem konkreten NCCI-Verhalten abhängig.

