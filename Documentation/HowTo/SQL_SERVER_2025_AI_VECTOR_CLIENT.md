# VECTOR zwischen Anwendung und SQL Server lesen

Zum Lesen genügen T-SQL-Grundkenntnisse; KI- oder C#-Erfahrung und ein lokales
Sprachmodell sind nicht erforderlich. Diese Lesehilfe erklärt, wie drei Zahlen
von einer Anwendung nach SQL Server und wieder zurück gelangen und welche
Ergebnisse dafür tatsächlich geprüft wurden. Beginnen Sie bei Bedarf mit der
[VECTOR-Kompatibilitätslesehilfe](SQL_SERVER_2025_AI_VECTOR_COMPATIBILITY.md).

## Begriffe für den Datenfluss

Ein **Vektor** ist eine geordnete Zahlenliste. Die Beispiele `[3,4,0]` und
`[1,0,0]` haben jeweils drei Zahlen, also Dimension 3. Sie sind absichtlich
synthetische Rechen- und Transportdaten, keine von einem Modell erzeugten
Embeddings. Ein **Embedding** wäre eine Zahlenliste, die ein Modell etwa aus
Text erzeugt; eine solche Erzeugung wird hier nicht untersucht.

Die **Anwendung** hält die Zahlen im Speicher. Der **Clienttreiber** ist die
Bibliothek, die ihre SQL-Anfragen und Werte an den Server übergibt. Der
**Datenbanktyp** `VECTOR(3)` legt fest, dass ein Wert drei Koordinaten enthält.
Eine **JSON-Darstellung** schreibt diese Koordinaten als Text, etwa `[3,4,0]`.
Zahlenliste, SQL-Typ und Textdarstellung sind verschiedene Ebenen.

Der untersuchte Datenfluss lässt sich so lesen:

1. Die Anwendung hält drei `float`-Werte und verpackt sie als `SqlVector<float>`.
2. Ein SQL-Parameter mit `SqlDbTypeExtensions.Vector` übergibt den typisierten
   Wert an die eigene `VECTOR(3)`-Spalte.
3. Der Reader, also das Objekt zum Lesen der SQL-Ergebniszeilen, erhält den Wert
   über `GetSqlVector<float>` und dessen `Memory` zurück.
4. Ein zusätzlicher JSON-Lesepfad liefert alle Koordinaten als Text. Die
   Prüfung vergleicht beide vollständigen Zahlenlisten mit den Ausgangswerten.

Dieses Hin- und Zurücklesen heißt **Roundtrip**. Die beobachteten API-Werte
erklären das Ergebnis an der Anwendungsschnittstelle. Ein unabhängiger Mitschnitt
der Übertragungsbytes wäre ein zusätzlicher **Wirebeleg**; er liegt hier nicht vor.

## Mit vorhandenen Grundübungen beginnen

1. Lesen Sie zuerst die [Grundlagenbegriffe](SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md)
   und das [Offline-Arbeitsheft](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md).
   Dafür ist keine lokale Einrichtung erforderlich.
2. Für eigenes SQL-Üben verwenden Sie eine eigene isolierte SQL-Server-2025-
   Labumgebung. Prüfen Sie Engineversion und Compatibility Level gemäß dem
   [QRY-014-Vertrag](../../Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/README.md);
   das dortige Profil verlangt Engine 17.x und CL 170.
3. Nutzen Sie den vorhandenen QRY-014-Ausführungspfad und dessen vorbereiteten
   SQL-Client. Für diese SQL-Grundübung brauchen Sie weder einen zusätzlichen
   nativen VECTOR-Treiber noch ein lokales Sprachmodell.
4. Lesen Sie erst optional den C#-Clientweg unten. Sein begrenzter Nachweis gilt
   für die ausdrücklich benannte Kombination; die Fragmente stellen keinen
   neuen ausführbaren Client bereit.

## Kleine API-Ausschnitte zum Zuordnen

Die folgenden Fragmente erläutern vorhandene API-Namen. Sie sind kein Runner,
stellen keine Verbindung her und enthalten weder SQL-Ziel noch ausführbare DML.
In einem tatsächlichen Programm gehören Verbindungszulassung, Eigentumsprüfung,
Fehlerbehandlung und Cleanup zum vollständigen Ablauf.

```csharp
// API-Ausschnitt: drei feste float32-Zahlen als typisierter Parameterwert.
var vector = new SqlVector<float>(
    new ReadOnlyMemory<float>(new float[] { 3f, 4f, 0f }));
var parameter = new SqlParameter("@V", SqlDbTypeExtensions.Vector)
{
    Value = vector
};
```

`float` ist hier der C#-Typ für float32. `SqlVector<float>` beschreibt den
typisierten Vektor; der Parametertyp sagt dem Treiber, wie der Wert zu behandeln
ist. Die API-Namen gehören zu `Microsoft.Data.SqlTypes`, `Microsoft.Data.SqlClient`
und `Microsoft.Data`; `ReadOnlyMemory` gehört zu `System`.

```csharp
// API-Ausschnitt: Spalte 1 des bereits verfügbaren Readers ist der Vektor.
SqlVector<float> value = reader.GetSqlVector<float>(1);
if (!value.IsNull)
{
    ReadOnlyMemory<float> coordinates = value.Memory;
}
```

Die Spaltenposition heißt **Ordinal** und beginnt bei null. Position 1 ist nur
im hier untersuchten Ergebnis die Vektorspalte. Für Sessiondaten zeigt die
[Sessionreader-Lesehilfe](SQL_SERVER_2025_AI_SESSION_READER.md), warum auch der
projizierte SQL-Typ zum gewählten Getter passen muss.

```csharp
// API-Ausschnitt: typisiertes SQL-NULL mit deklarierter Dimension 3.
parameter.Value = SqlVector<float>.CreateNull(3);
```

SQL-NULL bedeutet „kein Wert“. Es ist weder der Nullvektor `[0,0,0]` noch eine
Liste der Länge null. Im begrenzten Nachweis war NULL eine separate Parameter-/
Readerprobe; die beiden gespeicherten Ausgangsrows blieben erhalten.

## Was der vorhandene Nachweis tatsächlich zeigt

Empirisch wurde genau diese Kombination geprüft: Windows-Caller mit
.NET-Runtime 10.0.12, Microsoft.Data.SqlClient-Paket 6.1.4 und gelesener
Assemblyversion 6.0.0.0; SQL Server Build 17.0.5005.3 unter Linux/Developer,
Compatibility Level 170. Paket- und Assemblyversion sind getrennte Angaben.
Die Kompilierung verwendete SDK 10.0.401 und meldete zwei CS1701-WARNs für
Assemblyreferenzen von System.Data.Common/System.Runtime 9.0 auf 10.0. Diese
Warnungen bleiben sichtbar; der bestandene Fall ist keine pauschale Empfehlung
für andere Kombinationen.

Der [begrenzte Clientnachweis](../Project_Planning/SQL_SERVER_2025_AI_OPEN_SERIALIZATION_REVIEW.md)
ist mit PR238 integriert. Er enthält:

| Prüfung | Beobachtetes Ergebnis | Aussagegrenze |
|---|---|---|
| Zwei VECTOR(3)/float32-Rows | Alle Native- und JSON-Koordinaten entsprachen `[3,4,0]` und `[1,0,0]`; vor/nach unverändert | Keine Embedding- oder Suchqualitätsprüfung |
| Typisiertes NULL(3) | Reader meldete SQL-NULL und `SqlVector.IsNull` | Kein allgemeiner NULL-Vertrag für beliebige Typen |
| Zwei Koordinaten gegen Dimension 3 | Tatsächlicher SQLfehler 42204, Severity 16, State 1; Ausgangsrows unverändert | Spezifische Dimensionsabwehr, kein PASS für beliebige Fehler |
| Session und Reader | Acht tatsächliche SQL-/CLRtypfelder, 31 Read-/Projektions-/Dispose-Teilschritte und zehn Gesamt-API-Enden erhalten | API-Ende ersetzt keinen unabhängigen Wire- oder TLS-Beleg |
| Kontroll- und Abbaupfad | 52 bekannte SQLcmdenden, 24 Vollstates; Source-delete51003/Restore, vier Marker-DML- und vier Marker-Cleanup-Abweisungen51004 mit Restores; tatsächlicher Drop und frische DB-/Container-/Inputabwesenheit | Nur eigene isolierte Ressourcen und dieser begrenzte Lifecycle |

Ein **Vollstate** ist eine vollständige Zustandsaufnahme der im Prüfvertrag
festgelegten Daten und Metadaten. Die vier **Eigentumsmarker** kennzeichnen die
eigene Testdatenbank; absichtlich falsche Marker müssen Änderungen und Cleanup
abweisen. **Cleanup** bedeutet hier den geprüften Abbau der eigenen Ressourcen.
Diese Kontrollen gehören zum Nachweis und sind keine Aufforderung, sie selbst
auszuführen.

Die Zahlen der Prüfprotokolle sind keine Lernzeit- oder Performancewerte. Zum
Lesen genügen die öffentlichen Zusammenfassungen; private Rawlogs, DLLs,
Credentials und Verbindungsdaten werden nicht benötigt.

## Drei Fragen beim Lesen eines Ergebnisses

**„Die drei Zahlen sind richtig zurückgekommen. Ist damit die Suchqualität gut?“**
Die Zahlen bestätigen hier den Transport an der API. Für Suchqualität braucht
es geeignete Dokumente, Fragen und unabhängig bewertete Treffer. Die
[Offlineübungen](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md) behandeln diese
Unterscheidung mit vorhandenen Ergebnissen.

**„Ein anderer Fehler trat auf. Ist die Dimensionsnegative bestanden?“**
Ein Verbindungs-, Rechte- oder Readerfehler beantwortet die Dimensionsfrage
nicht. Der vorhandene Kontrollfall erhielt die spezifische SQL-Abweisung
für die Dimensionen 2 und 3 und prüfte danach die unveränderten Ausgangsrows.
Das Beschreiben dieses Falls startet keinen neuen Lauf.

**„Encrypt=True steht im Text. Ist die Verschlüsselung unabhängig bewiesen?“**
Im gepinnten Herstellerquellstand 6.1.4 wird `Mandatory` als `True` serialisiert;
die boolsche API-Zuordnung true→Mandatory ist dokumentiert. Der exakt geprüfte
Text passt deshalb zur konfigurierten TLS-Anforderung. Die tatsächlich
ausgehandelte TLS-Verbindung wurde nicht separat attestiert.
`TrustServerCertificate` war ausschließlich eine Ausnahme im eigenen isolierten
Labclient, keine Änderung globaler Trusteinstellungen oder Produktionsanleitung.

## Mit vorhandenen Lernpfaden weiterarbeiten

Die [QRY-014-Demo](../../Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/README.md)
erklärt Datentyp und Dimension; die
[QRY-015-Demo](../../Demos/09_AI_SQL_Server_2025/QRY-015_Vector_Metrics/README.md)
behandelt Metrics und Normalisierung. Deren vorhandene Ausführungspfade haben
eigene Voraussetzungen; die API-Fragmente oben erweitern sie nicht um einen
neuen Clientrunner.

Geprüft ist der begrenzte float32-API-/SQL-/Cleanupfall. Unabhängige Wire-/TLS-
Attestierung, float16, andere Builds/OS/Editionen, Pooling, Rollen, Performance,
RAG und die vollständige TSK-004-/Releaseabnahme bleiben offen. Die früheren
gestoppten UNKNOWN-Akten behalten ihren ursprünglichen Status und ihre fehlenden
SQLcleanup-Belege; der neue PASS ändert sie nicht rückwirkend.

## Quellen

Stand 2026-10-13: [VECTOR, SRC-072](https://learn.microsoft.com/en-us/sql/t-sql/data-types/vector-data-type?view=sql-server-ver17)
dokumentiert die float32-APIs ab SqlClient 6.1.
[SqlConnectionEncryptOption v6.1.4](https://github.com/dotnet/SqlClient/blob/v6.1.4/src/Microsoft.Data.SqlClient/src/Microsoft/Data/SqlClient/SqlConnectionEncryptOption.cs)
und die [API6.1](https://learn.microsoft.com/en-us/dotnet/api/microsoft.data.sqlclient.sqlconnectionencryptoption?view=sqlclient-dotnet-core-6.1)
bilden SRC-121. Dokumentierte Fähigkeit, konfigurierte Verwendung und tatsächlicher
Nachweis bleiben getrennt; Details stehen im [Quellenregister](../Research/SOURCE_REGISTER.md).
