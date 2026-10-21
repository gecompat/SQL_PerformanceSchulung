# VECTOR verstehen: Engine, Compatibility Level und Client

Stand: 2026-10-13. Zum Lesen genügen T-SQL-Grundkenntnisse. Sie lernen, warum
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

Float16, weitere Builds/Editionen/OS (Operating System; Betriebssystem), unabhängige Wire-/TLS-Attestierung und die
vollständige TSK-004-Abnahme bleiben offen. Dieser Abgleich belegt keine allgemeine Suchqualität,
Live-RAG-, Provider-, Modell- oder Performanceabnahme.

## Quellenstand

Die Primärquellen [VECTOR](https://learn.microsoft.com/en-us/sql/t-sql/data-types/vector-data-type?view=sql-server-ver17)
(SRC-072) und [AI_GENERATE_CHUNKS](https://learn.microsoft.com/en-us/sql/t-sql/functions/ai-generate-chunks-transact-sql?view=sql-server-ver17)
(SRC-079) wurden für diesen Abgleich am 2026-10-13 erneut geprüft. Weitere
Quellenangaben stehen im [Quellenregister](../Research/SOURCE_REGISTER.md).
Der allgemeine Prüfstand der übrigen Featurematrix bleibt 2026-10-11.
