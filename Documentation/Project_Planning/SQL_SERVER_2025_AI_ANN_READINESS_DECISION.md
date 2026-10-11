# TSK-006 – einzelner Entscheid für nachgewiesenes Readinessformat

Stand: 2026-10-11. AUTHORIZED: Der Benutzer bestätigte ausdrücklich
„Ja, Readinesspaket freigeben (empfohlen)“. Ausschließlich der folgende einzelne
Kandidat ist genehmigt; keine Runtimeabnahme dadurch. Der letzte
[Clientkorrekturkandidat](SQL_SERVER_2025_AI_ANN_PARSER_CLIENT_REVIEW.md) ist FAIL,
sein Budget verbraucht; eigene DB und Container sind nachweislich abwesend.

Die genehmigte einzelne Readinesswiederaufnahme ist inzwischen als
[Parser-/Previewdiagnose bestanden](SQL_SERVER_2025_AI_ANN_PARSER_PASS_REVIEW.md).
Zwei identische Parseraufrufe, tatsächlicher Restore 0 und unabhängige DB-/
Containerabwesenheit sind belegt. Kein Indexbuild oder Search; dieser einzelne
Umfang ist abgeschlossen und wird nicht erneut ausgeführt. Ein neuer
[Build-/Suchentscheid](SQL_SERVER_2025_AI_ANN_BUILD_DECISION.md) bleibt PENDING.

Der enge unabhängige Review dieses Befund-/Budgetentwurfs fand keine P1/P2.
Dies schließt ausschließlich das Entwurfsgate. Ein tatsächlich ausführbarer neuer
Kandidat benötigt nach Benutzerfreigabe weiterhin den unten begrenzten Quellenreview.

## Empfehlung und veränderte Evidenz

Empfohlen wird ausschließlich ein neuer privater Diagnosekandidat und ein neuer
eigener Container, keine Korrekturwelle oder weitere Probe bei Fehler.
Die Clientoptionen funktionieren inzwischen tatsächlich für Recovery und separate
SQL-Abwesenheit. Der konkrete verbleibende Vorbereitungsfehler ist die überenge
zeilenweise Erkennung des erhaltenen Windows-ODBC-Readinessformats.
Die tatsächliche erste TCP-Fehlermeldung enthält eine zusätzliche einzelne Punktzeile.
Dies ist kein Preview-/Vector-Parserbefund; beide Parseraufrufe sind unausgeführt.

Einzige zulässige Korrektur ist die Auswertung dieser erhaltenen Meldungsstruktur:
ODBC-Meldungsblöcke mit bekannten TCP-/Login-/Startupheadern erfassen. Eine einzelne
Punktzeile ausschließlich unmittelbar nach einem solchen tatsächlich passenden
Header innerhalb desselben stdout- oder stderr-Streams zulassen. Keine generelle
Entfernung unbekannter Zeilen, kein streamübergreifendes Anhängen und keine Annahme
beliebiger ODBC-Fehler. Clientoptions-/SQL-/unbekannte Zusatzmeldungen stoppen sofort.
Rückgabecode und begrenzte redigierte Originalausgabe weiterhin vor Auswertung erhalten.

Vor einem Containerstart benötigt die neue Auswertung lokale Gegenfixtures:

| Meldungsfixture | Erwartung |
|---|---|
| tatsächlich erhaltene synthetische TCP-/Punkt-/Timeoutfolge | begrenztes Readinesswarten erlaubt |
| Punkt ohne unmittelbar vorherigen passenden ODBC-Header | STOP |
| zweite Punktzeile oder Text nach Punkt | STOP |
| bekannter Timeout plus Clientoptionsfehler in stdout oder stderr | STOP |
| bekannter Timeout plus SQL-Msg-Fehler oder anderer ODBC-Fehler | STOP |
| fehlende Ausgabe oder fremde zusätzliche Meldung | STOP |
| verbotene Kombination `-h -1 -y 0` | Ablehnung vor Containerstart |

Ein Owner; vor SQL ein enger unabhängiger Quellenreview nur dieser tatsächlichen
Auswertungsdeltas und Gegenfixtures. Die unveränderte Parser-/Snapshot-/Marker-/
Helper-/Deadlineanalyse wiederverwenden. Modell-/Tokenverbrauch bleibt unbekannt.

## Unveränderter Effekt- und Nachweisumfang

Alle [ursprünglichen Parserdiagnosegrenzen](SQL_SERVER_2025_AI_ANN_PARSER_DECISION.md)
bleiben bestehen: genau die vollständige Image-ID für SQL 17.0.5005.3, vier CPUs/
sechs GiB, eigene Loopbackinstanz, volle CID-/Image-/Ownerbindung; Build/Edition/OS
vor Setup tatsächlich prüfen. Eigene CL170/SIMPLE-DB mit 256/64-MB-Dateilimits,
vier vollständige bytegenaue Marker und genau eine persistente Previewbaseline.
Höchstens eine gleichzeitig aktive SQL-Session; kein vorhandener Container/DB,
fremder Host oder anderes Repository wird verändert. Secrets nur in der Umgebung.

Höchstens zwei unveränderte feste PARSEONLY-Aufrufe: bei tatsächlicher Baseline 0
einmal davor; nach zulässigem 343 oder Syntaxannahme einmal nach eigenem Enable und
separat attestiertem Previewwert 1. Bei ursprünglicher 1 ist die OFF-Kontrolle SKIP;
kein künstliches OFF. Kein anderer Parser-/Client-/Bindungsfehler erlaubt den
zweiten Aufruf. Kein Fixture-/Indexbuild, VECTOR_SEARCH oder ANN-Folgelauf.

PREVIEW_FEATURES=ON bleibt der einzige Konfigurationseffekt. Vorher/nachher volle
Source-/Baseline-/Host-/DB-Optionsbindung, anschließend tatsächlicher Restore der
gespeicherten 0/1, markergebundener eigener DB-Abbau, neuer separater SQL-Abwesenheits-
client und gebundener Containerabbau mit eigener separater Abwesenheitsprüfung.
Regulärer gemeinsamer Lifecycle höchstens 300 Sekunden; separater gesamter Cleanup
höchstens 60 Sekunden, Prozessbudgets insgesamt 50 Sekunden plus zehn Sekunden
Reserve. Primäre und Recoveryfehler getrennt erhalten; fehlende Nachweise bleiben FAIL.

Kein zusätzlicher MAXDOP-, Host-, TLS-, Cloud-/Bezahl-API-, ONNX- oder
ALLOW_STALE_VECTOR_INDEX-Effekt. Nach diesem einzigen Kandidaten wird unabhängig
vom Ergebnis angehalten. Aktuelle Head-/Main-Gates, PR-Integration, Synchronisierung
und eigener Branchcleanup schließen seinen wahrheitsgemäßen Befund ab. Tatsächlicher
Indexbuild/Search bleibt an einen eigenen späteren Umfang und einen wirksamen
freigegebenen DOP-1-Pfad gebunden. Der Heartbeat setzt kein Budget zurück.
