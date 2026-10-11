# TSK-006 – FAIL des einzelnen Parser-Clientkorrekturkandidaten

Stand: 2026-10-11. Der Benutzer bestätigte das
[Clientkorrekturpaket](SQL_SERVER_2025_AI_ANN_PARSER_CLIENT_DECISION.md) ausdrücklich.
Genau ein neuer privater Kandidat und ein neuer eigener Container wurden verwendet;
keine Korrekturwelle oder weiterer Lauf nach dem Fehler.

## Vorbereitung und tatsächliche Grenze

Der Kandidat entfernte `-h -1` und behielt `-y 0 -w 65535` bei. Der Optionsvalidator
lief vor dem Containerstart. Zwei neue lokale Gegenfixtures prüften unzulässige
Clientoptionen und redigierte Readinessmeldungen; drei übernommene Parser-/Snapshot-
Tests bestanden ebenfalls. Der enge unabhängige Deltareview fand P2 für gemischte
Readinessmeldungen. Noch vor Runtime wurde jede Meldungszeile getrennt geprüft;
zusätzliche unbekannte Meldungen in stdout/stderr wurden als Gegenfixtures abgelehnt.
Der betroffene Readiness-Test bestand erneut, Schließungsreview und Helperhashbindung
bestanden. Keine erneute Vollanalyse oder Reviewkette der unveränderten Helper.

Die erste tatsächliche Readinessantwort hatte Rückgabecode 1. Ihre Ausgabe wurde
erhalten und enthielt einen ODBC-TCP-Verbindungsfehler mit der lokalisierten
Windowsmeldung `Der Wartevorgang wurde abgebrochen.`, danach eine einzelne Punktzeile,
anschließend Login-Timeout und die allgemeine Verbindungsfehlermeldung.
Die Punktzeile erfüllte den zeilenweisen ODBC-Headervergleich nicht. Der Kandidat
stoppte deshalb sofort mit `Client option or unexpected readiness error; immediate stop`.

Dies ist ein zu enger Meldungsauswerter in der Vorbereitung. Kein SQL-Server-
Vector-Parserbefund und kein bestätigter dauerhafter Serverausfall. Setup, SQL-Build-/
Edition-/OS-Attestierung, persistente Baseline, Preview-Enable und beide PARSEONLY-
Aufrufe wurden nicht erreicht. **0 Parseraufrufe**; keine Index-/Such-/Recall-/Plan-
oder Performanceevidenz. Eine neue Instanz ist durch ungenutzte Aufrufe nicht freigegeben.

## Tatsächlicher Cleanup

Der unveränderte finally-Pfad lief vollständig. Ein neuer Recoveryclient meldete
`ANN_RECOVERY|ALREADY_ABSENT`; ein weiterer separater SQL-Client belegte tatsächlich
die DB-Abwesenheit. Damit war die korrigierte Clientoptionskombination während
Cleanup tatsächlich SQL-verbindungsfähig, keine bloße Argumentannahme.

Die eigene DB war abwesend; Setup hatte keine persistente Baseline oder
Previewkonfiguration angelegt. Ein Preview-Restore war deshalb nicht erforderlich
und wurde nicht behauptet. Der allgemeine Helper meldet ohne Baseline keinen
RESTORED-PASS. Gebundener eigener Containerabbau und separate Containerabwesenheit
bestanden. Cleanup: **13,887 Sekunden**, innerhalb des separaten gemeinsamen
60-Sekunden-Budgets. Keine Cleanupfehler im erhaltenen Lauf, kein eigenes Residuum.
Ein zusätzlicher Präfixlookup nach Abschluss fand keinen Diagnosecontainer.
Der primäre Diagnosestatus bleibt **FAIL** trotz erfolgreicher Abwesenheitsbelege.

## Erhaltene private Quellen

| Quelle | SHA-256 |
|---|---|
| qualify_parser.py | 1B8F213A5B0A6ED9A56FD625096B5566EE937329948D657ECD506BFDAE7463AF |
| test_parser.py | C91705AEAE025A7DDD48CA6AA6EC43999A4B0F3B8C8227C9D411A42CA0935A99 |
| lifecycle01.log | A5CB98B10A688839D814DF8F1C62E82D900146E4CF98D2136C1DB446E1DD2B8A |

Die zuvor ausgeführte Parserquelle bleibt unverändert bei
CAD0FC759F8F17955A86D37E3BECFCDBF685E9B56DD03D2DF755BC8B1A29D598.
Die zwei wiederverwendeten Helper sind weiterhin durch die im
[ersten Parsercheckpoint](SQL_SERVER_2025_AI_ANN_PARSER_REVIEW.md) angegebenen
vollständigen Hashes gebunden. Ein Owner und ein erforderlicher enger Reviewer;
Modell-/Tokenverbrauch bleibt unbekannt.

## Angehaltene Wiederaufnahme

Der freigegebene einzelne Kandidat und Container sind verbraucht. Die neue
tatsächlich erhaltene Meldung ist geänderte Evidenz für einen präziseren
Meldungsblockvergleich, keine Befugnis zur Korrektur oder Wiederholung.
Der [enge Readinessentscheid](SQL_SERVER_2025_AI_ANN_READINESS_DECISION.md)
benötigt eine neue ausdrückliche Budgetfreigabe. Bis dahin bleiben Parser-/ANN-
Arbeit und ein automatischer Heartbeat-Retry angehalten; andere autorisierte
unabhängige Arbeit bleibt zulässig. IDX-011/IDX-012 bleiben PROPOSED.
