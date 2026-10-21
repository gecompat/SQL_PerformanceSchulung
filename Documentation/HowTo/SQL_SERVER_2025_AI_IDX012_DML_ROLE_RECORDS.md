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

Fachliche Grundlage sind [DEC-074 – Gebundenes ANN-Legacyprofil mit Generation UNKNOWN/WARN](../Project_Planning/SQL_SERVER_2025_AI_ANN_PROFILE_DECISION.md),
der [DML-Grenznachweis](../Project_Planning/SQL_SERVER_2025_AI_IDX012_DML_BOUNDARY_REVIEW.md)
und der [begrenzte Rollensplit](../Project_Planning/SQL_SERVER_2025_AI_IDX012_ROLE_REVIEW.md).
Die Herstellergrenze beschreibt [CREATE VECTOR INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-vector-index-transact-sql?view=sql-server-ver17)
(SRC-077); sie ersetzt die Beobachtung dieses festen Builds nicht.

Die binäre JSON-Darstellung erläutert [FOR JSON: Datentypkonvertierung](https://learn.microsoft.com/en-us/sql/relational-databases/json/how-for-json-converts-sql-server-data-types-to-json-data-types-sql-server?view=sql-server-ver17) (SRC-117).

## V2: Resultate der öffentlichen Rollen-API lesen

Die öffentliche Rollen-API (Application Programming Interface; Programmierschnittstelle) liefert inzwischen individuelle Clientcaptures.
Dafür gibt es einen getrennten V2-Vertrag. V1 und seine beiden historischen
Inputpins bleiben erhalten: fehlende Captures werden dort weiterhin nicht ergänzt.

V2 erwartet drei unveränderte Resultdictionaries: zuerst den Gegenfall ohne
CREATE ANY DATABASE, danach den Gegenfall ohne VIEW SERVER PERFORMANCE STATE,
zuletzt den positiven WARN des festen operator-admin-build-/Drop-Rebuild-Profils.
In den zwei Kostenphasen bleibt jeweils derselbe Client aktiv: Operator,
Admin nur für den festen Indexbuild, anschließend wieder Operator. Acht
geordnete Kontextrecords werden mit den beiden BEFORE-/AFTER-Kostenpaaren
verbunden. Session-writes sind dabei keine gemessenen Dateischreibvorgänge;
der gesamte Phasenaufwand enthält auch Kontrollen und Beobachtung.

Mit bereits im Speicher vorhandenen Dictionaries lautet der reine Aufruf:

```python
from idx012_public_role_evidence_v2 import report

record = {"contract": "IDX012_PUBLIC_ROLE_RECORD_V2", "profiles": public_results}
summary = report(record, binding, secrets=private_known_secrets)
```

`binding` enthält Token, DB-ID, Fixture-Objekt-ID, Operator-/Admin-SID,
ursprünglichen Previewwert, die feste aktuelle 24-Dateien-ExecutionSourcekarte,
die Consumer-/Expectedkarte und die ausdrücklich erklärte Herkunft. Es gibt
keinen frei wählbaren Dateipfad oder SQL-Executor. Der Consumer liest nur
seinen festen Expectedvertrag, V1-Helfer und die öffentlichen reinen
Evidenzfunktionen; er startet keine Clients. Die Prüfung verbindet 25
Clientrecords mit tatsächlichen Inputtexten, UTF-8-Digests, getrennten
Kanälen, PID (Process Identifier; Prozesskennung)/Poll/Returncode und Quellen vor/nach den Aufrufen.
Die Inputbindung betrifft konfigurierte Texte vor ENV-Erweiterung, keine
unabhängig attestierten serverseitig ausgeführten SQLbytes.

Die Secretliste ist ein erforderlicher privater Parameter und wird nicht
ausgegeben oder gehasht. Plaintext, UTF-8-/UTF-16-Hex und JSON-escapete
bekannte Werte werden vor Digests geprüft. Empfangene Hexframes sind im
festen JSON-Zeilen-Transport nicht unterstützt und werden auch innerhalb
dekodierter JSON-Strings abgewiesen. Hexschreibungen werden unabhängig von
Groß-/Kleinschreibung erkannt; Plaintext bleibt unverändert case-sensitiv.
Eine ausdrücklich leere Liste ergibt NOT_CHECKED_FOR_UNAVAILABLE_SECRETS,
keine behauptete vollständige Credentialprüfung. Herkunft und Vollständigkeit
der Callerangaben bleiben DECLARED_NOT_INDEPENDENTLY_ATTESTED.

Die Ausgabe bleibt WARN mit festen Counts und Claims. Kohärente individuelle
Prozessenden attestieren kein Server-/TDS-Ende. SQL-Restore, guarded Drop und
frische DB-Abwesenheit werden anhand konkreter Kanaltexte geprüft. Die
öffentlichen Resultate enthalten keine eigenständigen Parent-Namespace-/
Principalcleanup-Records; diese Claims bleiben NOT_ESTABLISHED. Das gilt
auch für den unabhängigen Ownerquery, vollständige DML-Errorfelder,
allgemeine Runtimequalifikation und TP-PERF; die Indexgeneration bleibt UNKNOWN.
Für diese Leseaufgabe sind keine neue SQL-Ausführung, Installation oder
Login-DDL (Data Definition Language; Anweisungen zum Definieren und Ändern von Datenbankobjekten) nötig. Der [V2-Nachweis](../Project_Planning/SQL_SERVER_2025_AI_IDX012_PUBLIC_RECORD_V2_REVIEW.md)
beschreibt die abgegrenzte Source- und spätere Offlineprüfung.

Der erste einmalige historische V2-Abgleich endete mit bekanntem FAIL:
der damalige Consumer erwartete bei den beiden Rechtegegenfällen nur
Status=NOT_STARTED; die öffentliche API erfasst zusätzlich Seconds=60
sowie StartedMonotonic und DeadlineMonotonic jeweils NULL. Source5 bindet
nun diese vollständige feste Form. Der ursprüngliche Bericht bleibt FAIL;
das damalige Einmalbudget ist verbraucht und sein STOP bleibt erhalten.
Die neuen reinen Gegenfälle schreiben diesen Bericht nicht nachträglich um.

Ein getrennt zugelassener historischer Abgleich mit dem korrigierten Consumer
erreichte anschließend COHERENT_PUBLIC_V2 mit Gesamtergebnis WARN. Er prüfte
drei unveränderte öffentliche Profile, 25 individuelle Clientcaptures, acht
geordnete Rollenkontexte, zwei Kostenpaare und zwei Rechtegegenfälle sowie
vier erfolgreiche DML-Kontrollen und vier DML-Verweigerungen. Die vollständigen
Originalprofile und aktuellen Quellenbindungen blieben vor/nach identisch.
Nach diesem ersten kohärenten Befund wurde die neue Welle gestoppt. Insgesamt
liegen damit der ursprüngliche FAIL und ein neuer kohärenter WARN-Bericht vor.

Dieser reine Datenabgleich führte kein neues SQL, keinen Container und keinen
Provider aus. Er ersetzt keine unabhängige Herkunftsattestierung der Callerrecords.
Die ursprünglichen Credentials waren nicht verfügbar: secrets=[] blieb
ausdrücklich NOT_CHECKED_FOR_UNAVAILABLE_SECRETS. Der zusätzlich gebundene
Producer-Privacyreview ergänzt keine vollständige Consumer-Credentialprüfung.
Generation UNKNOWN, die genannten NOT_ESTABLISHED-Claims und insbesondere
die fehlende allgemeine Runtime-/TP-PERF-Qualifikation bleiben unverändert.
Der [getrennte Requalifikationsnachweis](../Project_Planning/SQL_SERVER_2025_AI_IDX012_V2_REQUALIFICATION_REVIEW.md)
grenzt diesen kohärenten historischen Recordcheck vom ersten fehlgeschlagenen
Einmalpaket ab.
