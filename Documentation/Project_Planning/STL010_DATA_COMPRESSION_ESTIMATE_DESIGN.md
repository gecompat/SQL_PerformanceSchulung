# STL-010 – Entwurf: Kompressionsschätzung und tatsächliche Größe vergleichen

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `STL-010` – Schätzergebnis von ROW-/PAGE-Kompression mit tatsächlicher Seitenbelegung vergleichen |
| Quellen | `SRC-151`, `SRC-152` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Lernfrage und Aussagegrenze

Wie unterscheiden sich die von `sys.sp_estimate_data_compression_savings`
geschätzten Seitengrößen von den tatsächlichen Seitengrößen, nachdem
synthetische Tabellen mit ROW oder PAGE komprimiert wurden? Die gespeicherte
Prozedur sampelt das Quellobjekt und erstellt komprimierte Vergleichsobjekte
in `tempdb`. Ihr Ergebnis ist eine Schätzung und keine Messung des später
komprimierten Zielobjekts.

Der Entwurf vergleicht `NONE`, `ROW` und `PAGE` auf zwei synthetischen
Datenprofilen: stark repetitive Werte und weitgehend unterschiedliche
Nutzdaten. Er behauptet nicht, dass PAGE immer kleiner oder schneller ist.
Kompressionsspeicherung, CPU-Aufwand, Reads und Ausführungsdauer sind getrennte
Messgrößen. Der Vergleich begründet keine universelle Empfehlung.

## Synthetische Profile und Korrektheitsoracle

Ein späterer Fixtureentwurf kann pro Profil 20.000 Zeilen mit `RowId` von
1 bis 20.000 erzeugen. Der Gruppenschlüssel ist `((RowId - 1) % 100) + 1`.
Das repetitive Profil verwendet `Status = RowId % 4`, `Amount = RowId % 10`
und `Payload = REPLICATE('R', 120)`. Das variantenreiche Profil verwendet
`Status = (RowId * 17) % 251`, `Amount = (RowId * 37) % 100003` und einen
120-stelligen Payload aus den ersten 120 Hexzeichen von zweimal
`HASHBYTES('SHA2_256', CONVERT(varbinary(4), RowId))`. Die Decimal-Präzision
und die exakte T-SQL-Konvertierung sind vor einer Runtimefreigabe festzulegen.
Das Tupeloracle je Profil besteht aus allen Tupeln
`(RowId, GroupKey, Status, Amount, Payload)` in `RowId`-Reihenfolge und wird
vollständig aus diesen Formeln berechnet.

Für jedes Profil werden unabhängig vorbereitete Kopien mit identischen
Starttupeln angelegt. Die Varianten tragen explizit `NONE`, `ROW` und `PAGE`.
Die unkomprimierte Ausgangsgröße und der tatsächliche Seitenbeleg werden vor
einem späteren Rebuild festgehalten. Nach der Kompressionsänderung werden die
Kopie und ihr vollständiges Tupeloracle geprüft; anschließend werden die
tatsächlichen reservierten und verwendeten Seiten aus einer versionsgeprüften
Katalog-/DMV-Quelle erfasst. Die genaue Identitätsbindung an Objekt, Index,
Partition und Allocation Unit ist vor Runtime zu spezifizieren.

## Schätz- und Messablauf

Für jede Profil-/Kompressionskombination wird die Schätzung vor dem
entsprechenden Ziel-Rebuild gegen genau die passende Quellkopie erhoben. Der
Schätzer-Output wird zusammen mit Datenbank-, Objekt-, Index- und
Partitionsidentität gesichert. Die tatsächlichen Seitenwerte werden erst nach
dem später genehmigten Rebuild und einer konsistenten Aktualisierung der
Metadaten erfasst. Schätz- und Istwerte werden nebeneinander verglichen; eine
Abweichung wird nicht nachträglich durch Änderung des Profils oder der
Erfolgsschwelle beseitigt.

Die Probe folgt einem begrenzten Ressourcenvertrag. `SRC-151` dokumentiert
Sampling, Vergleichsobjekte in `tempdb`, benötigte Rechte und den während der
Prozedur erworbenen IS-Lock. Vor jeder späteren Laufphase werden TempDB-
Kapazität, Zeitlimit, konkurrierende Zugriffe und Cleanup separat festgelegt.
Die ausgeführte Prozedur ist read-only für das Quellobjekt, kann aber TempDB
beanspruchen und mit Schreibvorgängen über den Lock interagieren. Änderungen
der Kompression erfolgen nur an markierten synthetischen Kopien.

## Edition und Version

Die Featureunterstützung ist editionsabhängig. `SRC-152` belegt die Matrix
für SQL Server 2025 und kann nicht als Editionsnachweis für SQL Server 2019
oder 2022 verwendet werden. Vor einem konkreten Lauf sind Zielversion, exakter
Build und Edition festzulegen und mit der jeweiligen Microsoft-Matrix sowie
dem tatsächlichen Featurestatus abzugleichen. Fehlende Unterstützung führt zu
einem dokumentierten `SKIP_UNSUPPORTED`; sie wird nicht aus einem anderen
Build extrapoliert.

## Ergebnisdarstellung

Für jede Tabellenkopie bleiben folgende Werte getrennt:

- geschätzte Seitengröße und Prozedurmetadaten;
- tatsächliche Daten- und Indexseiten nach dem Rebuild;
- vollständige Ergebnistupel und Rowcount;
- optionale Reads, CPU und Dauer eines separat definierten Lese-/DML-Workloads.

Die Tupeloracles prüfen fachliche Gleichheit, nicht Kompressionsqualität.
Seitenwerte prüfen Speicherbelegung und nicht allein Performance. Reads, CPU
und Dauer erfordern einen eigenen kontrollierten Messvertrag und dürfen nicht
aus den Seitenwerten hergeleitet werden.

## Cleanup und offene Runtime-Gates

Jede spätere Kopie erhält einen eindeutigen Marker und wird aus einer
ursprünglich unkomprimierten Fixture erzeugt. Der Cleanup entfernt nur diese
markierten Kopien. Falls Änderungen auf einer langlebigen Fixture erfolgen,
muss sie wieder auf `NONE` gesetzt und ihr Ausgangszustand geprüft werden.
Ein abgebrochener oder fehlgeschlagener Rebuild darf keine Restvariante oder
unklare Kompressionseinstellung zurücklassen.

Vor einer Runtimefreigabe bleiben offen:

- konkrete T-SQL-Formeln und vollständige Tupeloracles für beide Profile;
- editions- und buildgenaue Unterstützung in SQL Server 2019, 2022 und 2025;
- Rechte auf Quelldatenbank und `tempdb` sowie tatsächliche TempDB-Grenzen;
- versionstabile Messung von Seitenbelegung je Objekt, Index und Partition;
- Rebuild-Zeitbudget, Transaktions-/Logginggrenzen, DML- und Cleanupvertrag;
- eigener Messvertrag, falls Reads, CPU oder Dauer als Kennzahlen erscheinen.

Dieser Offlineentwurf erteilt keine SQL-/Runtimefreigabe, nimmt keine
Kompressionsänderung vor und behauptet weder eine Kompressionsrangfolge noch
eine Leistungswirkung. Eine menschliche Generalprobe ist nicht vorgesehen.
