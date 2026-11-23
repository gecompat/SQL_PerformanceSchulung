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

Der Runner muss beide Datenbanken mit diesen Markern und den
festgelegten Ressourcenobergrenzen bereitstellen. Vor dem ersten Indexbau
muss er beide sortierten Leseströme vollständig prüfen. Der erwartete
SHA-256-Digest ist
`bfa6e87fc9501d335d859b5d509d6ed466cd1a272e026cbd60e9657c065d955f`.
Die Prüfung liest jeweils eine Zeile und hält nur den laufenden Digest und
Zähler. Erst danach darf der Runner die beiden Indexbatches nacheinander
starten. Die [Offlineprüfungen](../../Tests/Static/test_idx010_pilot_setup.py)
sichern die Armtrennung, die Ladebereiche und den Identitätsnachweis ab.
Die SQL-Batches sind für den Methodenreview bestimmt.

### Indexmetadaten und überlappende Segmente

Die [Metadatenabfrage](../../Tests/Runtime/idx010_index_metadata.py) bindet
die Segmente an den genauen Index, seine einzige Partition und die
Schlüsselspalte. Der Katalog muss genau die zwei geplanten
`bigint NOT NULL`-Spalten ausweisen. `EventDayKey` hat die erwartete
Ordnungsposition je Arm. `EventId` trägt in beiden Armen die
Ordnungsposition 0. Ein fehlender `EventId`, eine weitere Indexspalte
oder ein zweiter Ordnungsschlüssel macht das Paar unvergleichbar.
Die Prüfung verlangt vier volle komprimierte Rowgroups und prüft
auch den separaten Löschpuffer. Jedes der vier Segmentgrenzenpaare muss
einer dieser Rowgroups zugeordnet sein und in den Wertebereich der
synthetischen Schlüssel fallen. Zusätzliche Segmente und mehrdeutige
Grenzen werden abgewiesen.
[Microsoft-Referenz zu Segmenten](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-segments-transact-sql?view=sql-server-ver17)
und [Referenz zum Löschpuffer](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-internal-partitions-transact-sql?view=sql-server-ver17).

Die Auswahl der Encoding-Typen und die Konvertierung der Grenzen
entsprechen dem oben gebundenen Microsoft-Beispiel. Für `bigint` verwendet
das Beispiel `min_data_id` und `max_data_id` bei `encoding_type` 1 oder 2.
Der Projektfilter lässt nur diese Kombination zu. Bei vier
Segmenten mit acht unterschiedlichen Grenzen ist die Summe der
Überlappungen im Microsoft-Verfahren doppelt so groß wie die Zahl der
überlappenden Paare. Die Abfrage zählt jedes Paar einmal und gibt nur den
Zähler und die gebundene Indexidentität aus. Der Decoder prüft das Ergebnis
gegen das Profil. Die tatsächlich verwendeten Encodings und das Format der
Katalogantwort bleiben auf dem Pilotbuild zu prüfen. Eine native
Metadatendiagnose bestätigte für beide Varianten vier volle Rowgroups,
Encoding 1 und nur eindeutige Grenzen. SQLCMD gab mit Exitcode 0 eine
Join-Reihenfolgewarnung für die Katalogabfrage aus. Der Transport akzeptiert
genau diese Warnung für die kataloggebundene Abfrage. Die Katalogwerte
durchlaufen auch in diesem Fall die vollständige Prüfung.

Die synthetische Ladeformel wurde über alle 4.194.304 IDs ausgewertet.
Der feste Abfragebereich enthält in den vier nach `EventId` definierten
Ladebereichen 1.023, 1.027, 1.023 und 1.023 Treffer.
Die Minima und Maxima jedes Ladebereichs umschließen den gesamten
Abfragebereich. Die berechnete Verteilung ist eine Eigenschaft der
Fixture. Die tatsächlich gebildeten Rowgroups und ihre Segmentgrenzen
werden aus dem Engine-Katalog gelesen.


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
Meldungskanal. Der Messvertrag erlaubt das beobachtete Zweizeilenformat
mit einer Standard-I/O-Zeile und genau einer Segmentzeile derselben
Tabelle. Eine Segmentmeldung allein und das einzeilige kombinierte
Format bleiben zulässig. Zwei Segmentmeldungen, weitere Tabellen oder
Zusatzdiagnosen führen zum Abbruch. Prozesslaufzeit und beide Ausgabeströme werden beim Lesen
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
einer höheren Ordnungsgüte. Beide Metadatenprüfungen laufen vor der ersten
Ergebnisabfrage. Hat der geordnete Arm nicht weniger überlappende Paare
als der Kontrollarm, endet die Prüfung in der Metadatenphase mit
`NOT_PROVEN`. Damit scheidet auch eine bereits überlappungsfreie Kontrolle
aus. Für `PASS` muss der geordnete Arm zusätzlich mehr Segmente in der
Ergebnisabfrage überspringen.

Die Ablaufsteuerung übergibt dem Transport eine gemeinsame Laufzeitgrenze
von 900 Sekunden und eine getrennte Cleanupfrist von 90 Sekunden. Docker- und
SQLCMD-Aufrufe verwenden die jeweils verbleibende Frist. Der gemeinsame
Prozessrunner behält für DGN-004 seine Standardgrenze von 20 Sekunden. Die Ablaufsteuerung registriert jede Zielbereitstellung vor dem ersten Aufruf und fordert auch
bei Fehlern während des Instanzstarts oder der Bereitstellung Cleanup an.
`FAIL_CLEANUP` hat Vorrang vor einem positiven Befund. Der [Docker- und SQL-Transport](../../Tests/Runtime/idx010_docker_transport.py)
bindet das lokal vorgehaltene Image, das private Netzwerkprofil `none`, CPU,
RAM und die laufende Engineversion. Er erzeugt den Container aus dem lokal
vorhandenen Image und startet ihn erst nach Prüfung von Eigentum,
Image und Ressourcenlimits. Bricht der Client die Erzeugung ab, gilt eine
leere Bestandsabfrage allein nicht als Abbaunachweis. Ein später
sichtbarer Container wird nur nach eindeutigem Abgleich von Namen und
Eigentumslabel entfernt.
[Docker-Referenz zu `docker create`](https://docs.docker.com/reference/cli/docker/container/create/).

Vor der ersten SQL-Änderung prüft der Transport
mindestens 2.816 MiB freien Platz am Datenpfad im eigenen Container. Die
Summe deckt die vier Datenbankdateien und TempDB bis zu ihren Obergrenzen.
Fehlende oder zu geringe Kapazitätsangaben beenden den Preflight. Der
Transport liest die Fixture in begrenzten
Bereichen des Primärschlüssels, erhebt die Indexmetadaten und ruft den
Messadapter mit dem laufgebundenen Reader auf. Die
[SQL-Batches](../../Tests/Runtime/idx010_provision_sql.py) setzen und prüfen
die Dateiobergrenzen, erstellen die markierten Datenbanken und prüfen die
effektiven Leserrechte. Der Abbau prüft die Datenbankmarker, entfernt den
Reader und gleicht die Container-ID über Namen und zufälliges Eigentumslabel
ab. Fehlender SQL-Abbaunachweis bleibt ein Fehler, auch wenn der eigene
Container entfernt werden konnte.

Die Reader-Erstellung wird vor dem SQL-Aufruf als versucht registriert.
Der Login erhält eine zufällige 16-Byte-SID. Auch wenn der Client die
Bestätigung der Erstellung nicht erhält, prüft der Abbau den Login anhand
seines Namens und dieser SID. Bei abweichender SID bleibt das Login-DDL
aus und der SQL-Abbau gilt als unbestätigt.
[Microsoft-Referenz zur SID in CREATE LOGIN](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-login-transact-sql?view=sql-server-ver17).

Die [Ablaufprüfungen](../../Tests/Static/test_idx010_pilot_sequence.py) und
[Transportprüfungen](../../Tests/Static/test_idx010_docker_transport.py)
verwenden simulierte Prozess- und SQL-Antworten. Der Runner hat keinen
automatischen Laufzeittrigger. Vor einem echten Lauf stehen der
unabhängige Methodenreview und die Prüfung der Laufvoraussetzungen an.

### Read-only-Komponententest für den SQLCMD-Transport

Auf Build `17.0.5065.9` gab SQLCMD eine vollständige synthetische
Seite mit 262.144 Wertepaaren aus zwei `bigint`-Spalten aus. Der
[Fixture-Reader](../../Tests/Runtime/idx010_docker_transport.py) dekodierte
alle Paare nach der vorgesehenen Schlüsselformel. Die Abfrage verwendete
`GENERATE_SERIES` in `master`.

Für die [Planerfassung](../../Tests/Runtime/idx010_sqlcmd_capture.py)
wies der mitgelieferte SQLCMD-Client das bisherige `-y 60000` zurück.
Der Aufruf verwendet jetzt `-y 0` ohne `-h`, da der Client diese
beiden Optionen zusammen ablehnte. Damit erhielt der Transport in einem
Read-only-Komponententest das Ergebnis, einen vollständigen XML-Plan
mit 6.881 Zeichen und die Abschlussmarke. Die Begrenzung bleibt im
Prozessreader bei 256 KiB Standardausgabe und 16 KiB Fehlerausgabe
sowie bei weniger als 60.000 Zeichen für den verarbeiteten XML-Plan.
Die synthetische Planabfrage auf einem Systemkatalog wurde wegen der
fehlenden `Events`-Segmentmeldung erwartungsgemäß abgewiesen.
[Microsoft-Referenz zu SQLCMD-Ausgabeoptionen](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver17#format-options).

Die Komponentenläufe legten keine Testdatenbank und keinen Index an
und bestätigten den Abbau des eigenen Containers. Die tatsächlichen
NCCI-Pläne und Segmentmeldungen bleiben Gegenstand des späteren Piloten.

Ein weiterer Read-only-Komponententest prüfte die getrennte Docker-Erzeugung
und den Start am selben Image. Die Limits waren vor dem Start bestätigt.
Der anschließende SQL-Aufruf bestätigte Build und Edition, die
Kapazitätsabfrage war erfolgreich und der eigene Container wurde entfernt.
Die SQL-Schritte für TempDB-Änderungen und Reader-Anlage waren in diesem
Komponententest ausgenommen.

Ein weiterer Komponententest führte eine lesende Abfrage über den
gruppierten Columnstore-Index der bestehenden IDX-010-Demo aus.
Auf demselben festgeschriebenen Build schrieb SQLCMD Standard- und
Segmentzähler in zwei getrennte Meldungen für dieselbe Tabelle.
Die Segmentmeldung wies ein gelesenes und ein übersprungenes Segment
aus. Der XML-Plan zeigte den ausgeführten gruppierten Columnstore-Scan.
Die Regressionstests bilden die beobachtete Ausgabeform mit den
Sollzählern des Vier-Rowgroup-Profils nach. Der markierte Aufbau
der bestehenden CCI-Demo und der eigene Container wurden entfernt.
Die Ausgabeform des eigentlichen NCCI-Paars bleibt empirisch zu prüfen.


### Native Bereitstellungsprobe beider leeren Testdatenbanken

Die Bereitstellungsprobe verwendete den vorhandenen
`DockerPilotTransport` auf dem festgeschriebenen Developer-Build
`17.0.5065.9` über die Docker-kompatible Schnittstelle von Podman.
Vor dem Start prüfte der Transport das Image, zwei CPUs, 4 GiB RAM,
das gleich große RAM-/Swap-Gesamtlimit und das Netzwerkprofil `none`.
Im laufenden Container bestanden der Build- und Editionsabgleich, die
Kapazitätsprüfung und die Abfrage der gesetzten TempDB-Obergrenzen.

Anschließend legte der Transport beide markierten Datenbanken mit den
festgelegten Dateigrenzen und je einer leeren `dbo.Events` an. Die
Rechteprüfung unter dem laufgebundenen Reader bestätigte in beiden
Datenbanken eine erfolgreiche Abfrage der leeren Tabelle, erteiltes
`SHOWPLAN` und fehlendes `UPDATE`. Die isolierte Probe prüfte den
markergestützten Abbau beider Datenbanken, des SID-gebundenen Logins und
des Containers. Sie belegt Bereitstellung, Rechte und Abbau. Die
Befüllung, beide NCCI-Bauten und die Segmentauswertung gehören zum
isolierten Mechanismuspilot.

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

