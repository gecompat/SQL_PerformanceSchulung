# TSK-006 – FAIL der einzelnen Parserdiagnose

Stand: 2026-10-11. Die ausdrücklich genehmigte
[Parserdiagnose](SQL_SERVER_2025_AI_ANN_PARSER_DECISION.md) wurde mit genau einem
privaten Kandidaten und einem neuen eigenen Container durchgeführt und angehalten.
Kein weiterer Lauf oder korrigierter Kandidat ist dadurch freigegeben.

## Vorbereitung und tatsächlicher Befund

Drei betroffene lokale Tests bestanden: zulässige Parserausgabe, fehlende/fremde
Kontext-/Baseline-/Objekt-/Dateilimitbindung und allein erlaubte Previewdifferenz.
Der enge unabhängige Quellenreview fand zwei P2, beide vor Runtime geschlossen:
direkte mehrzeilige FOR-JSON-Ausgabe wurde durch einen auf 60.000 UTF-16-
Codeeinheiten begrenzten einzelnen nvarchar(max)-Skalar ersetzt; die
343-Klassifikation akzeptiert ausschließlich vollständige bekannte Meldungsblöcke
und lehnt zusätzliche Clientfehler in stdout/stderr ab. Die betroffenen drei
Tests bestanden erneut. Unveränderte hashgebundene Helperanalyse wurde
wiederverwendet, keine erneute Vollanalyse oder Reviewkette.

Der tatsächlich verwendete SQL-Client meldet Version 15.0.1300.359, Microsoft ODBC
Driver 17. Die Quellenfreigabe übersah dessen inkompatible Optionskombination
`-h -1 -y 0`. Das reguläre gemeinsame 300-Sekunden-Budget endete mit
`Readiness consumed lifecycle budget`. Die einzelnen Readiness-Fehlerausgaben
wurden nicht erhalten; ihre konkreten Einzelbefunde bleiben unbekannt.
SQL-Recovery und separate SQL-Abwesenheitsprüfung lieferten danach beide den
tatsächlich erhaltenen Fehler:

```text
Sqlcmd: The -h and the -y 0 options are mutually exclusive.
```

Die identische Optionskombination war auch in der Readinessquelle enthalten.
Dies ist ein Fehler der Diagnosevorbereitung, kein Vector-Parserbefund.
Setup, SQL-Build-/Edition-/OS-Attestierung, persistente Previewbaseline,
Preview-Enable und beide PARSEONLY-Aufrufe wurden nicht erreicht. Parseraufrufe:
**0 von höchstens 2**. Keine Vector-Fixture, Indexgeneration, ANN-Rows, Recall-,
Plan- oder Performanceevidenz. Aus dem früher qualifizierten Image wird keine
aktuelle SQL-Runtimeabnahme abgeleitet.

## Recovery und Abwesenheit

Der gebundene eigene Container wurde trotz des primären Fehlers im finally-Pfad
entfernt. Die separate Containerabwesenheit bestand; zusätzlich wurde nach dem
Prozessabschluss kein Container dieses Diagnosepräfixes gefunden. Cleanup dauerte
**11,989 Sekunden**, innerhalb des separaten gemeinsamen 60-Sekunden-Budgets.

SQL-Recovery: **FAIL**, separate SQL-DB-Abwesenheitsprüfung: **FAIL**, jeweils wegen
der tatsächlichen Clientoptionsablehnung. Kein RESTORED- oder DROP-Nachweis und
keine SQL-DB-Abwesenheit behaupten. Die Setupquelle wurde nicht aufgerufen;
der nachgewiesene Containerabbau ersetzt trotzdem keine erfolgreiche separate
SQL-Abwesenheitsprüfung. Gesamtstatus bleibt FAIL; kein Recovery-PASS.

## Private Quellenbindung und Budget

| Private Quelle | SHA-256 |
|---|---|
| qualify_parser.py | CAD0FC759F8F17955A86D37E3BECFCDBF685E9B56DD03D2DF755BC8B1A29D598 |
| test_parser.py | 2568C80370613FF1F29E1A4535C6417EF70EB5680029C2411C194A8F403B9C5B |
| lifecycle01.log | 1E582720025D1679BBCCEF8DF08CF4DB452A6D60CB114BF78E1B8B783B59DA20 |
| wiederverwendeter qualify.py-Helper | F4F2D13D1332D1CAF3406C127B8A5853A4126A6C71F87D66225E97F7FAC6B7CE |
| wiederverwendeter sql_sources.py-Helper | 1D72CCF7C601A40FDD11B30BAE3FD69D3EF812F03C971CD86593A42A9576793F |

Ein Implementierungsowner und ein enger unabhängiger Reviewer; Modell-/Tokenverbrauch
bleibt unbekannt. Der einzige Diagnosekandidat und Container sind verbraucht.
Unausgeführte Parseraufrufe erlauben keine neue Instanz oder Korrekturwelle.
Die privaten ausgeführten Quellen bleiben unverändert erhalten.

## Wiederaufnahmegrenze

Eine anschließende lokale Clientargumentkontrolle verwendete die geänderte
Kombination `-y 0 -w 65535` ohne `-h` gegen den ungültigen eigenen Loopbackport 0,
ohne SQL-Text, reale Credentials oder neuen Container. Der Client erreichte die
erwartete Verbindungsablehnung statt der Optionsablehnung. Dies belegt allein
die Argumentannahme; keine Verbindung, JSON-Ergebnisausgabe oder SQL-Runtime.

Eine neue Parserprobe benötigt einen ausdrücklich genehmigten, begrenzten
[Clientkorrekturentscheid](SQL_SERVER_2025_AI_ANN_PARSER_CLIENT_DECISION.md).
Der Heartbeat wiederholt diesen FAIL nicht und setzt sein Budget nicht zurück.
IDX-011/IDX-012 bleiben PROPOSED; tatsächlicher Indexbuild/Search benötigt weiterhin
einen eigenen Umfang und einen wirksamen freigegebenen DOP-1-Pfad.
