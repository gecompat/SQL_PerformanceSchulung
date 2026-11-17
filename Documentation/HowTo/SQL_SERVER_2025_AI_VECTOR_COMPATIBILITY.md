# VECTOR verstehen: Engine, Compatibility Level und Client

Stand: 2026-11-17. Zum Lesen genügen T-SQL-Grundkenntnisse. Sie lernen, warum
Engineversion, Datenbank-Kompatibilität und Clienttreiber verschiedene Fragen
beantworten. Die Beispiele verwenden vorhandene Labornachweise; ein lokales
Sprachmodell ist dafür nicht erforderlich.

Ein Vektor ist eine geordnete Liste von Zahlen, etwa `[3,4,0]`. SQL Server kann
diese Zahlen als VECTOR speichern und vergleichen. Der Datentyp allein erzeugt
keine Sprachbedeutung: Woher die Zahlen stammen und ob ein Treffer fachlich passt,
bleiben eigene Fragen. Die [Grundlagenbegriffe](SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md)
führen in diese Unterscheidung ein.

## Drei Angaben beantworten drei verschiedene Fragen

| Angabe | Verständliche Frage | Bedeutung für VECTOR |
|---|---|---|
| Engineversion / Build | Welche Datenbanksoftware verarbeitet die Abfrage? | SQL Server 2025 ist Engine 17.x. Ein genauer Build bezeichnet einen konkreten Softwarestand. Eine neue Clientbibliothek ersetzt keine fehlende Enginefunktion. |
| Compatibility Level, kurz CL | Welches Kompatibilitätsprofil verwendet diese Datenbank? | CL wird pro Datenbank gewählt. VECTOR ist laut Dokumentation unter allen CLs verfügbar; einzelne Funktionen haben eigene Voraussetzungen, etwa Chunking mit mindestens CL 170. |
| Client / Treiber / Transport | Wie gelangen Werte zwischen Anwendung und Server? | Der Treiber überträgt Werte. Native binäre VECTOR-Übertragung und die Darstellung als JSON-Zeichenfolge sind verschiedene Transportpfade. |

Die [Featurematrix](../Research/SQL_SERVER_2025_AI_FEATURE_MATRIX.md) stellt die
Voraussetzungen gegenüber. Eine dokumentierte Fähigkeit ist noch kein Nachweis,
dass die konkrete Anwendung sie erfolgreich verwendet hat.

## Vector-Indexgeneration als zusätzliche Grenze

Engine, Compatibility Level und Treiber bestimmen noch nicht, welche
Vector-Indexgeneration eine Suche verwendet. Microsoft führt
[Vectorindizes](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-vector-index-transact-sql?view=sql-server-ver17)
und [`VECTOR_SEARCH`](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-search-transact-sql?view=sql-server-ver17)
für SQL Server 2025 weiterhin als Preview mit `PREVIEW_FEATURES`. Die neueste
Indexgeneration Version 3 wird in der aktuellen
Herstellerdokumentation für Azure SQL Database, SQL database in Microsoft Fabric
und Azure SQL Managed Instance mit Always-up-to-date genannt, nicht für SQL
Server 2025. Übertragen Sie ihre DML- und Filtereigenschaften daher nicht
ungeprüft auf die SQL-Server-2025-Engine.

Die Suchsyntax hängt ebenfalls von der Generation ab: frühere Versionen nutzen
`TOP_N` innerhalb von `VECTOR_SEARCH`; Version 3 nutzt `SELECT TOP (N) WITH
APPROXIMATE`. Microsoft ordnet Postfilterung, die Read-only-Grenze nach dem
Indexbuild und den clustered-`int`-Primärschlüssel den früheren Versionen zu.
Ermitteln Sie vor der Wahl des Suchpfads die Generation des konkreten Indexes
und lesen Sie dessen Metadaten. Microsoft dokumentiert dafür eine
`JSON_VALUE`-Abfrage auf `sys.vector_indexes.build_parameters` (`SRC-077`):

```sql
SELECT
    s.name AS schema_name,
    t.name AS table_name,
    i.name AS index_name,
    TRY_CONVERT(int, JSON_VALUE(v.build_parameters, '$.Version')) AS index_version,
    CASE
        WHEN TRY_CONVERT(int, JSON_VALUE(v.build_parameters, '$.Version')) >= 3
            THEN N'Version 3 oder neuer'
        WHEN TRY_CONVERT(int, JSON_VALUE(v.build_parameters, '$.Version')) < 3
            THEN N'Frühere Version'
        ELSE N'Unbekannt'
    END AS version_status
FROM sys.vector_indexes AS v
JOIN sys.indexes AS i
    ON i.object_id = v.object_id
   AND i.index_id = v.index_id
JOIN sys.tables AS t
    ON t.object_id = v.object_id
JOIN sys.schemas AS s
    ON s.schema_id = t.schema_id
WHERE v.object_id = OBJECT_ID(N'dbo.Chunks', N'U')
ORDER BY i.name;
```

`build_parameters` ist laut Katalogdokumentation ein internes Feld. Die
versionsbezogene Auswertung ist hier deshalb auf den von Microsoft dokumentierten
Migrations-/Prüfpfad beschränkt; ein fehlender oder nicht numerischer Wert ergibt
`Unbekannt` und darf nicht als frühere Generation interpretiert werden. Eine
leere Ergebnismenge beweist ebenfalls nicht, dass kein Index existiert, denn die
Metadatensichtbarkeit hängt von Besitz und erteilten Rechten ab (`SRC-097`). Die
Metadaten zeigen weder die Plattformverfügbarkeit noch den tatsächlichen
Suchplan. Der Projektbuild 17.0.5005.3 bleibt hierbei unqualifiziert; der
[Build-/Suchbefund](../Project_Planning/SQL_SERVER_2025_AI_ANN_BUILD_REVIEW.md)
erläutert die Grenze.

### Float16 ist eine zusätzliche Preview- und Typgrenze

Die Float16-Verfügbarkeit ist von der Indexgeneration unabhängig. Microsoft
führt den `VECTOR`-Basistyp `float16` auf SQL Server 2025 als Preview; die
Datenbank muss dafür `PREVIEW_FEATURES` aktiviert haben. In Azure SQL Database,
Azure SQL Managed Instance und SQL database in Microsoft Fabric wird Float16
laut Herstellerseite dagegen als allgemein verfügbar geführt. Dieser
Plattformunterschied macht Float16 weder auf jedem SQL-Server-2025-Build
verfügbar noch für das Projekt qualifiziert (`SRC-166`).

Zwischen `VECTOR(..., float32)` und `VECTOR(..., float16)` ist derzeit weder
implizite noch explizite Konvertierung dokumentiert; Dimension und Basistyp
müssen bei Vektorzuweisungen übereinstimmen. Funktionen wie `VECTOR_DISTANCE`
akzeptieren keine gemischten Basistypen. Die Herstellerseite nennt außerdem
ARM64 als nicht unterstützte Architektur für Float16. Prüfen Sie den Basistyp
bei Bedarf über `sys.columns`, weil SSMS ihn in der Oberfläche derzeit nicht
unterscheidet (`SRC-166`).

Native Float16-Übertragung ist eine weitere unabhängige Clientgrenze: Microsoft
nennt in der allgemeinen Produktdokumentation JDBC Driver 13.4+ und ODBC Driver
18.7.1+. Die ODBC-spezifische Anleitung präzisiert die Float16-Unterstützung auf
Version 18.7.1.1 oder höher und verlangt für native Unterstützung außerdem die
ausgehandelte Vektorstufe `v2`. Für eine reproduzierbare ODBC-Auswahl ist
daher mindestens 18.7.1.1 samt `vectorTypeSupport=v2` anzusetzen; die abweichend
verkürzte Versionsangabe der allgemeinen Seite bleibt als Quellenunterschied
sichtbar (`SRC-173`). Die SqlClient-Anleitung zeigt aktuell `SqlVector<float>`
und damit den hier bereits begrenzten float32-Pfad; daraus folgt keine
Float16-Unterstützung für SqlClient und kein Wire-Nachweis (`SRC-167`). Eine
Nutzung von Float16 benötigt daher einen separaten Preview-, Build-/Architektur-,
Typ- und Treiberbeleg. Sie wird nicht durch den bestehenden float32-Roundtrip
freigegeben.

Für die nativen ODBC-C-Bindungen bleibt der Anwendungsbuffer auch bei
`float16` ein Array aus 4-Byte-`float`-Werten; zwei Bytes pro Element betreffen
die Übertragung auf dem Draht. Der Treiber konvertiert zwischen beiden
Darstellungen. Deshalb den Puffer mit `sizeof(float)` dimensionieren. Ein
Speichern und Zurücklesen als `float16` ist verlustbehaftet, weil Werte auf den
nächsten darstellbaren Halbpräzisionswert gerundet werden (`SRC-173`). Das sind
ODBC-spezifische Bufferregeln und keine allgemeine Aussage über andere Clients.

## Drei kleine Fehler- und Entscheidungsfälle

### 1. Neuer Client, ältere Engine

**Situation:** Eine Anwendung verwendet eine moderne Clientbibliothek, ihr Server
ist aber SQL Server 2022. Die Erwartung lautet: „Der neue Treiber macht VECTOR verfügbar.“

**Entscheidung:** Zuerst die Enginegrenze prüfen. SQL Server 2022 ist Engine 16.x;
die hier behandelte native VECTOR-Funktion gehört zu 17.x. Weder Treiberversion
noch Datenbank-CL rüsten sie nach. Die vorhandenen
[Providerprofile](../Project_Planning/SQL_SERVER_2025_AI_PROVIDER_REVIEW.md)
endeten bei 15.x/16.x kontrolliert vor Setup mit SKIP_VERSION. Ein SKIP ist kein
fachlicher Erfolg auf dieser Version. Für die Lernbeispiele führt der nächste
Schritt zum vorbereiteten SQL-Server-2025-Labortarget der
[QRY-014-Demo](../../Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/README.md).
Dort stehen die Voraussetzungen und der vorhandene Ausführungspfad.

### 2. VECTOR funktioniert, Chunking scheitert

**Situation:** Auf dem tatsächlich geprüften Build 17.0.5005.3 bestehen die
float32-Skalarproben bei CL 160. Der feste Chunkaufruf liefert dennoch einen Fehler.

**Entscheidung:** Typ und Funktion getrennt lesen. Die
[CL-Istwertqualifikation](../Project_Planning/SQL_SERVER_2025_AI_CL_RESULT_REVIEW.md)
belegt bei CL 150/160/170 Dimension 3, Basistyp float32, Norm 5 und die vollständigen
normalisierten Koordinaten. Für den festen Chunkaufruf wurden bei CL 150/160
Error 102 („Incorrect syntax near '='.“) und bei CL 170 zwei vollständige Chunkrows
beobachtet. Aus diesem konkreten Fehler folgt weder allgemeine Low-CL-Verfügbarkeit
noch allgemeine Unverfügbarkeit. Die dokumentierte Chunkinggrenze bleibt CL 170;
die öffentlichen Demoprofile werden nicht gelockert. Ein erwarteter anderer
Fehlercode darf die tatsächliche Ausgabe nicht ersetzen.

### 3. Vollständiges JSON ist noch kein Binärtransporttest

**Situation:** Eine Anwendung sendet einen Vektor als JSON-Zeichenfolge und liest
alle Zahlen korrekt zurück. Die Erwartung lautet: „Damit ist auch der native
binäre VECTOR-Transport meines Treibers geprüft.“

**Entscheidung:** Nur den tatsächlich verwendeten Pfad als geprüft bezeichnen.
Die Dokumentation beschreibt native Übertragung mit TDS (Tabular Data Stream; Übertragungsprotokoll zwischen SQL-Client und Server) 7.4 oder höher und einem
unterstützenden Treiber; Microsoft.Data.SqlClient 6.1 dokumentiert dafür SqlVector
mit float32. Für ältere Clients ist VARCHAR(MAX)/JSON (JavaScript Object Notation; strukturiertes Textformat) als Abwärtspfad dokumentiert.
Das offene Projektgate bedeutet daher keine allgemeine Treiberinkompatibilität.

Im [Corpus-SQL-Komponentennachweis](../Project_Planning/SQL_SERVER_2025_AI_CORPUS_SQL_REVIEW.md)
wurden vier vollständige VECTOR(768)-Records über JSON zurückgelesen, alle
Koordinaten geprüft und die drei Dokument-Cosines unabhängig innerhalb der vorab
festgelegten 1e-5-Toleranz nachgerechnet. Das belegt diesen begrenzten Roundtrip.
Ein JSON-Hash bindet die Darstellung, nicht automatisch die physischen VECTORbits
oder den Übertragungspfad einer Clientbibliothek.

Inzwischen belegt der separate
[Client-Roundtrip](../Project_Planning/SQL_SERVER_2025_AI_OPEN_SERIALIZATION_REVIEW.md)
einen begrenzten nativen float32-API-Pfad: Microsoft.Data.SqlClient-Paket 6.1.4
unter Windows/.NET 10.0.12 gegen SQL Server Build 17.0.5005.3/Linux/Developer,
CL 170. Zwei VECTOR(3)-Rows wurden typisiert übertragen und vollständig native/
JSON-zurückgelesen; NULL(3), spezifische Dimensionsabwehr und der eigene Cleanup
bestanden. Die [Client-Lesehilfe](SQL_SERVER_2025_AI_VECTOR_CLIENT.md) erklärt
die APIs und den konkreten Nachweis ohne neue Ausführung.

Die Anwendungsschnittstelle ist damit für diese Kombination tatsächlich geprüft.
Ein unabhängiger Mitschnitt der binären Wire-/TDS-Übertragung und eine separate
Attestierung ausgehandelter TLS-Eigenschaften bleiben UNQUALIFIED: Diese
konkreten Belege fehlen hier weiterhin. Dokumentierte native Treiberunterstützung
und beobachteter API-Roundtrip ersetzen sie nicht.

## Mit vorhandenen Übungen weiterlernen

Die Demos [QRY-014: Vektortyp und Dimension](../../Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/README.md),
[QRY-015: Metrics und Normalisierung](../../Demos/09_AI_SQL_Server_2025/QRY-015_Vector_Metrics/README.md)
und [QRY-016: Chunking und Provenienz](../../Demos/09_AI_SQL_Server_2025/QRY-016_Chunk_Provenance/README.md)
zeigen die getrennten Lernfragen. Im
[Offline-Arbeitsheft](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md)
können Sie die entsprechenden Aufgaben und die optionale Evidenzleseaufgabe E1
anhand vorhandener Ergebnisse bearbeiten. Ein gespeichertes Ergebnis ist kein
neuer eigener Lauf; die Ausführungsbedingungen stehen jeweils bei der Demo.

Float16 bleibt für das Projekt unqualifiziert, obwohl seine dokumentierte
Produkt- und Treibergrenze jetzt getrennt ausgewiesen ist. Weitere Builds/
Editionen/OS (Operating System; Betriebssystem), unabhängige Wire-/TLS-Attestierung und die
vollständige TSK-004-Abnahme bleiben offen. Dieser Abgleich belegt keine allgemeine Suchqualität,
Live-RAG-, Provider-, Modell- oder Performanceabnahme.

## Quellenstand

Die Primärquellen [VECTOR](https://learn.microsoft.com/en-us/sql/t-sql/data-types/vector-data-type?view=sql-server-ver17)
(SRC-072; erneut geprüft am 2026-11-17), [Float16](https://learn.microsoft.com/en-us/sql/t-sql/data-types/vector-data-type-half-precision-float?view=sql-server-ver17)
(SRC-166), die [ODBC-Vektoranleitung](https://learn.microsoft.com/en-us/sql/connect/odbc/vector-data-type?view=sql-server-ver15)
(SRC-173) und [SqlClient VECTOR](https://learn.microsoft.com/en-us/sql/connect/ado-net/sql/vector-data-sql-server?view=sql-server-ver17)
(SRC-167) wurden am 2026-11-17 für Typstatus, Plattformgrenze und dokumentierte native Treiberunterstützung geprüft. Die Quelle
[AI_GENERATE_CHUNKS](https://learn.microsoft.com/en-us/sql/t-sql/functions/ai-generate-chunks-transact-sql?view=sql-server-ver17)
(SRC-079) wurde für diesen Abgleich am 2026-10-13 erneut geprüft. Die Quellen
[`CREATE VECTOR INDEX`](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-vector-index-transact-sql?view=sql-server-ver17)
(SRC-077) und [`VECTOR_SEARCH`](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-search-transact-sql?view=sql-server-ver17)
(SRC-078) sowie [`sys.vector_indexes`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-vector-indexes-transact-sql?view=sql-server-ver17)
(SRC-097) wurden am 2026-11-17 hinsichtlich Indexgeneration,
Plattformverfügbarkeit und Suchsyntax erneut geprüft. Weitere
Quellenangaben stehen im [Quellenregister](../Research/SOURCE_REGISTER.md).
Der allgemeine Prüfstand der übrigen Featurematrix bleibt 2026-10-11.
