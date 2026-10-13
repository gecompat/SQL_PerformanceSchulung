# IDX-012: DML und Rollen anhand aufgezeichneter Ergebnisse prüfen

Datenänderungen können an einem vorhandenen ANN-Index scheitern. Außerdem kann
die Rolle für den Indexbau von der Rolle für spätere Datenänderungen abweichen.
Der reine Recordvertrag hilft, diese beiden Beobachtungen auseinanderzuhalten.
Zum Lesen und Prüfen vorhandener Records ist kein SQL Server, Modell oder
zusätzlicher Treiber erforderlich. Die Prüfung führt keine SQL-Befehle aus.

Der Vertrag gilt ausschließlich für das beobachtete Profil SQL Server
17.0.5005.3, Linux, EngineEdition 3 und Compatibility Level 170. Die numerische
Indexgeneration bleibt UNKNOWN. Andere Builds können andere DML-Regeln haben;
dieser Nachweis überträgt das Ergebnis nicht auf sie.

## Was wird geprüft?

Ohne Index müssen UPDATE, DELETE, INSERT und MERGE jeweils die aufgezeichnete
positive Kontrolle erfüllen. Mit Index müssen dieselben vier Operationen den
tatsächlichen Fehler 42231/State 1 zeigen. Der feste INSERT erreicht während
seiner Transaktion höchstens 1000 Rows; nach jedem Rollback sind wieder 999
ursprüngliche Rows und Transaktionswerte 0/0 erforderlich. Zwei vollständige
Quellenaufnahmen binden alle Koordinaten und ihre Cosinedistanzen.

Die Rollenrecords trennen je Phase vier Zeitpunkte: Operator am Anfang,
Admin unmittelbar am Indexbau, Rückkehr zum gleichen Operator und Operator
am Ende. Der Operator erhält dadurch keine zusätzliche Serverrolle. Die beiden
Rechtegegenproben müssen vor Setup anhalten und anschließend den ursprünglichen
Grantzustand wiederherstellen. Marker, vollständige Snapshotprojektionen und
Indexmetadaten dürfen keine fremde Datenbank oder veränderte Quelle verdecken.
Die Snapshotfelder `ValueBytes` und `NameBytes` enthalten die kanonische
Base64-Darstellung vollständiger UTF-16LE-Bytes. Marker benötigen zusätzlich
die exakte ByteLength; die beiden Dateinamen sind die eigene Datenbank und
ihr Name mit `_log`. Hextexte oder fremde Dateinamen erfüllen diese Bindung nicht.

Ein Ausschnitt einer aufgezeichneten DML-Zeile sieht so aus:

```json
{
  "kind": "DML_BOUNDARY",
  "Stage": "WITH_INDEX",
  "Operation": "UPDATE_ID_23",
  "ErrorNumber": 42231,
  "ErrorState": 1,
  "RolledBack": true,
  "TransactionCount": 0,
  "TransactionState": 0
}
```

Dieser Ausschnitt genügt noch nicht als Eingabe. Der vollständige Vertrag
verlangt alle acht DML-Zeilen, acht Rollenzeitpunkte, fünf Principal-Audits,
zwei Rechtegegenproben sowie die vollständigen Quellen-, Snapshot- und
Cleanuprecords. Fehlende Pflichtfelder werden abgewiesen.

## Aufruf ohne SQL-Ausführung

Der Caller übergibt `record` und `binding` als vollständige einfache Python-
Dictionaries im Speicher. Das Modul lädt ausschließlich seinen festen eigenen
Expected-Vertrag; es akzeptiert keinen frei wählbaren Recorddateipfad.

```python
from idx012_dml_role_evidence import report

# record: vollständiger bereitgestellter Record im Speicher
# binding: getrennte Token-/DB-/Objekt-/SID- und aktuelle Sourcebindung
summary = report(record, binding)
print(summary)
```

Für den Import kann `Tests/Static` im vorhandenen Pythonpfad verwendet werden.
`source_binding()` liefert die tatsächlich vorhandenen Consumer- und
Expecteddatei-SHAs. Diese Bindung prüft aktuelle Dateibytes, attestiert aber
nicht die Herkunft des übergebenen SQL-Records. Die zwei eingefrorenen nativen
C3-Eingabehashes beziehen sich auf konfigurierte UTF-8-Quelldateien vor
SQLCMD-ENV-Expansion, nicht auf unabhängig nachgewiesenen serverseitigen Text.

Die synthetischen Gegenfälle können ohne Datenbank ausgeführt werden:

```powershell
python Tests/Static/test_idx012_dml_role_evidence.py
```

Sie sind ausdrücklich PUREFIXTURE_ONLY und kein neuer Native-PASS.

## Wie ist das Ergebnis zu lesen?

`record_validation=COHERENT` bedeutet, dass die übergebenen Daten zum festen
Schema, zur Reihenfolge und zu den numerischen Oracles passen. Die Ausgabe
enthält ausschließlich begrenzte Counts und feste Ergebnisgrenzen; keine
SID, Token, Quelltexte, Vektoren, Verbindung oder Zeitstempel.

Das Gesamtergebnis bleibt WARN. Die vorhandene Recordform enthält keinen
vollständigen individuellen Input-/Clientendnachweis und keinen allgemeinen
Serverrequest-Endnachweis. Diese Felder bleiben ausdrücklich NOT_ESTABLISHED;
ein `true` oder eine erfundene Nullzahl ersetzt sie nicht. Die DML-Zeilen
enthalten Number/State/Message, jedoch keinen vollständigen Severity-/Line-/
Procedurecapture. Der Verbraucher ergänzt solche Werte nicht.

Auch leere Namespaceabwesenheitstexte sind lediglich kohärente übergebene
Texte; sie attestieren keine tatsächliche Containeroperation. Fehlende
Namespace- und Inputwitnesses bleiben sichtbar. SQL-Restore, Drop und frische
DB-/Principalabwesenheit benötigen ihre konkreten aufgezeichneten Frames;
`ALREADY_ABSENT` erfüllt diesen positiven Cleanupvertrag nicht.

Die Prüfung belegt keine Minimalrollen, keinen vollständigen Nicht-sysadmin-
Indexbuild, keine öffentliche Multi-Login-Producerqualifikation, Freshness,
TP-PERF oder vollständige Demoabnahme. Anwender:innen brauchen für diese
Leseaufgabe keine Logins anzulegen, keine roten DDL-Befehle auszuführen und
keinen Provider zu installieren.

Fachliche Grundlage sind [DEC-074](../Project_Planning/SQL_SERVER_2025_AI_ANN_PROFILE_DECISION.md),
der [DML-Grenznachweis](../Project_Planning/SQL_SERVER_2025_AI_IDX012_DML_BOUNDARY_REVIEW.md)
und der [begrenzte Rollensplit](../Project_Planning/SQL_SERVER_2025_AI_IDX012_ROLE_REVIEW.md).
Die Herstellergrenze beschreibt [CREATE VECTOR INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-vector-index-transact-sql?view=sql-server-ver17)
(SRC-077); sie ersetzt die Beobachtung dieses festen Builds nicht.

Die binäre JSON-Darstellung erläutert [FOR JSON: Datentypkonvertierung](https://learn.microsoft.com/en-us/sql/relational-databases/json/how-for-json-converts-sql-server-data-types-to-json-data-types-sql-server?view=sql-server-ver17) (SRC-117).
