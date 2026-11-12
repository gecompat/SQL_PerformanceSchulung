# External Tables: Quellen- und Zugriffswegprüfung

Stand: 12. November 2026  
Status: begrenzte Offline-Quellenprüfung; kein Connector, Infrastrukturaufbau,
Lauf oder Demo-Vertrag freigegeben

## Ergebnis und Versionsgrenzen

`CREATE EXTERNAL TABLE` ist über SQL Server 2019, 2022 und 2025 verfügbar.
Das allein ergibt aber noch keinen identischen Vergleichspfad: Die verfügbaren
Quelltypen, Betriebssysteme, PolyBase-Dienste und Authentifizierungswege
unterscheiden sich. Die aktuelle Microsoft-Matrix dokumentiert unter anderem:

| Profil | SQL-Server-Quelle | ODBC/RDBMS-Connectoren | Dateiquellen |
|---|---|---|---|
| 2019 | `sqlserver://` verfügbar | PolyBase-RDBMS-Connectoren auf Windows; generisches ODBC auf Windows. Datei-CSV benötigt Hadoop. | Parquet nicht verfügbar; ADLS Gen2 ab CU11 mit `abfs[s]` |
| 2022 | `sqlserver://` verfügbar | PolyBase-RDBMS-Connectoren auf Windows; für PolyBase unter Linux verlangt der Installationsguide Trace Flag 13702 beim Start | CSV nativ, Parquet, Delta und S3-kompatibel verfügbar; Hadoop entfällt; Azure-Präfixe wechseln zu `abs`/`adls` |
| 2025 | `sqlserver://` verfügbar | RDBMS- und generische ODBC-Connectoren auch unter Linux | CSV, Parquet und Delta auf Blob/ADLS/S3 können mit `OPENROWSET(BULK ...)` ohne PolyBase-Dienst abgefragt werden; Dateipfad und persistente externe Tabellen nicht gleichsetzen |

Die Tabellenansicht `External tables: Yes` darf daher nicht als Aussage über
jeden Connector, jedes Betriebssystem oder denselben Installationsweg gelesen
werden. Der Guide nennt für persistente RDBMS-Connectoren SQL-Authentifizierung
und PolyBase-Dienste; SQL Server, Oracle, Teradata, MongoDB und ODBC haben
jeweils eigene Voraussetzungen. Microsoft dokumentiert Scale-out-Gruppen als
ab SQL Server 2022 entfernt; ein Scale-out-Aufbau ist kein notwendiger Teil
dieses Entwurfs.

## Vergleichsweg, der versionsübergreifend übrig bleibt

Der SQL-Server-Connector (`sqlserver://`) ist der am klarsten gemeinsame
Kandidat für 2019/2022/2025 und persistente externe Tabellen. Für eine
gleichartige Versionsmatrix müsste der spätere Entwurf Windows als gemeinsames
Betriebssystem wählen oder die Matrix sichtbar in Windows- und Linuxprofile
teilen: Die aktuelle Produktmatrix weist den RDBMS-Connector unter Linux erst
ab SQL Server 2025 aus. Ein Linux-only-Profil kann damit keine gemeinsame
SQL-Server-Connectorreihe über 2019/2022/2025 liefern.

Der SQL-Server-Connector verlangt eine erreichbare separate SQL-Server-Quelle,
SQL-Authentifizierung, einen datenbankweiten Berechtigungsnachweis und einen
PolyBase-Setuppfad. Das macht ihn für einen reproduzierbaren Vergleich
inhaltlich passend, erzeugt aber eine zusätzliche Instanz, Credentials,
Netzwerk- und Cleanupgrenzen. Diese Infrastruktur ist nicht vorhanden oder
freigegeben nachgewiesen und wird nicht eingerichtet.

Datei-Connectoren lösen das gemeinsame Versionsproblem nicht ohne
unterschiedliche Bedingungen: CSV in 2019 benötigt Hadoop, während CSV ab
2022 nativ verfügbar ist; Parquet und Delta beginnen erst ab 2022. Ein solcher
Vergleich müsste die andere Connector-/Dateiverarbeitung explizit als Teil der
Version behandeln und dürfte keinen isolierten Versions- oder
External-Table-Effekt behaupten.

## Mess- und Evidenzvertrag für einen späteren Entwurf

- Externe Tabellen lesen Daten außerhalb der lokalen Tabellenverwaltung; die
  Quelle kann unabhängig geändert oder entfernt werden. Für wiederholbare
  Resultate müsste die Quelle je Lauf unveränderlich markiert oder durch einen
  vollständigen Snapshot gebunden werden.
- Pushdown hängt vom Connector, Ausdruck und Optimiererzustand ab. Microsoft
  nennt Funktionen und Syntax, die Pushdown verhindern; Variablenfilter werden
  standardmäßig nicht gepusht und benötigen geeignete Optimizer-Hotfixes.
  `PUSHDOWN = ON` allein beweist keine Auslagerung.
- Eine spätere Pushdown-Prüfung könnte den Remote-Query-Plan mit Trace Flag
  6408 untersuchen und `sys.dm_exec_external_work.read_command` binden. Der
  DMV-Wert kann auf 4.000 Zeichen begrenzt sein und ist für Hadoop- und
  Azure-Storage-Pfade `NULL`; er darf nicht als universeller Nachweis benutzt
  werden. `sys.dm_exec_dms_workers` dokumentiert `bytes_processed`, dessen
  Bedeutung und Vollständigkeit für einen konkreten Vergleich eigens zu
  qualifizieren wären.
- Externe Tabellen unterstützen Statistiken, aber deren Erstellung kann
  externe Daten in eine temporäre SQL-Server-Tabelle importieren. Bei einer
  Remotequelle folgt daraus als Projektschlussfolgerung zusätzlicher
  Netzwerktransport. SQL Server kann außerdem TempDB zum Sortieren gesampelter
  Zeilen verwenden. TempDB- und lokale I/O-Kosten sind daher mögliche,
  profilabhängige Folgen, keine garantierte Wirkung jedes Statistikaufbaus.
  Seit SQL Server 2022 können fehlende Statistiken außerdem automatisch und
  synchron entstehen. Eine
  spätere Messung müsste gleiche, explizit gebundene Statistikzustände vor den
  Messläufen herstellen und Statistikaufbau getrennt messen.
- Für einen fairen Vergleich wären dieselbe synthetische Zeilenmenge,
  Spalten-/Datentypen, Ergebnisoracle, Prädikate und Projektion festzulegen.
  Ein lokaler Tabellenlauf und ein externer Lauf messen dennoch verschiedene
  Datenwege: lokale Seiten-I/O, Remoteausführung, Netzwerktransport,
  Data-Movement-Service und gegebenenfalls TempDB. Diese Kosten wären getrennt
  auszuweisen; Planform oder eine einzelne Laufzeit würde keinen allgemeinen
  Geschwindigkeitsclaim tragen.

## Offene Gates

Die Quellenprüfung empfiehlt, den SQL-Server-Connector als ersten
versionsübergreifenden Kandidaten weiterzuverfolgen, aber keinen endgültigen
Zugriffsweg festzulegen, bevor das gemeinsame OS-Profil und eine isolierte
synthetische Quellinstanz entschieden und nachgewiesen sind. Offen bleiben
außerdem exakte Builds/CUs, Editionen, Compatibility Levels, Rechte und
Credentials, Ressourcen-/Netzwerkgrenzen, Connector-Verfügbarkeit,
Setup-/Cleanupvertrag, Statistikaufbau, Pushdown-Nachweis, Transportmessung,
unabhängiger Methodenreview und konkrete Laufautorisierung. Es wurde kein
SQL, Connector, Netzwerk oder externer Dienst angesprochen.

## Quellen

- `SRC-153` bis `SRC-157`: [Projektquellenregister](../Research/SOURCE_REGISTER.md#external-tables-und-polybase-2026-11).
- Alle Matrix- und Verhaltensaussagen oben sind Herstellerdokumentation. Die
  Empfehlung für `sqlserver://` als ersten Kandidaten und die notwendige
  Windows-/Linux-Aufteilung sind daraus abgeleitete Projektschlussfolgerungen,
  keine Laufzeitbelege.
