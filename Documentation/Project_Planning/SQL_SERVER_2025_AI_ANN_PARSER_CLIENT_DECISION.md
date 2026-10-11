# TSK-006 – begrenzter Clientkorrekturentscheid für Parserdiagnose

Stand: 2026-10-11. PENDING_USER_DECISION. Keine neue ausführbare Korrekturquelle
oder neue SQL-/Containerruntime durch diesen Entwurf autorisiert.

Der enge unabhängige Review dieses neuen Budget-/Claimentwurfs fand keine P1/P2.
Dies schließt allein das Entwurfsgate, nicht den noch erforderlichen tatsächlichen
Quellen-/Effektreview eines später ausdrücklich autorisierten neuen Kandidaten.

Die [einzelne Parserdiagnose](SQL_SERVER_2025_AI_ANN_PARSER_REVIEW.md) scheiterte
vor Setup. Die erhaltenen Recovery-/Abwesenheitsfehler belegen die lokale
sqlcmd-Optionsablehnung `-h -1 -y 0`; konkrete einzelne Readinessausgaben sind
unbekannt. Das freigegebene Kandidatenbudget ist verbraucht, obwohl kein
PARSEONLY-Aufruf erreicht wurde. Kein stilles Zurücksetzen oder Retry.

## Konkreter neuer Umfang

Empfohlen wird höchstens ein neuer privater Diagnosekandidat und ein neuer eigener
Container, keine Korrekturwelle. Ein Implementierungsowner und vor SQL genau ein
enger unabhängiger Review der geänderten Client-/Fehlerausgabedeltas. Vorhandene
gültige Helper-, Snapshot-, Marker- und Effektanalysen bleiben wiederverwendbar.
Modell-/Tokenverbrauch bleibt unbekannt.

Einzige Korrekturen gegenüber dem erhaltenen ausgeführten Kandidaten:

- `-h -1` entfernen; `-y 0 -w 65535` beibehalten. Snapshot bleibt ein einzelner
  nvarchar(max)-Skalar mit harter Grenze 60.000 UTF-16-Codeeinheiten. Keine
  pauschale Entfernung fremder Header oder unbekannter Ausgabe in der Auswertung.
- Fehlgeschlagene Readinesscalls mit Rückgabecode und begrenzter redigierter
  stdout/stderr erhalten; eine Clientoptionsablehnung stoppt sofort, statt bis
  zum Lifecycledeadline erneut aufzurufen. Keine zusätzlichen SQL-Textvarianten.
- Eine lokale Argumentgegenfixture muss die verbotene Kombination vor einem
  Containerstart erkennen. Die bereits erfolgte geänderte Argumentkontrolle
  erreichte ohne `-h` die erwartete Ablehnung des ungültigen Loopbackports 0;
  dies ersetzt keine tatsächliche SQL- oder JSON-Ausgabequalifikation.

## Unveränderte Effekte und Abbruch

Alle [ursprünglichen Diagnosegrenzen](SQL_SERVER_2025_AI_ANN_PARSER_DECISION.md)
bleiben unverändert: genau dasselbe vollständige lokale Image, SQL 17.0.5005.3/
EngineEdition 3/Linux Ubuntu 24.04, vier CPUs/sechs GiB, eigene Loopbackbindung,
vollständige CID-/Image-/Ownerbindung, eigene CL170/SIMPLE-DB mit 256/64-MB-Limits,
vier vollständige bytegenaue Eigentumsmarker, genau eine synthetische persistente
Previewbaseline, höchstens eine gleichzeitig aktive SQL-Session.

Höchstens zwei identische feste PARSEONLY-Aufrufe aus dem ursprünglichen Paket:
bei tatsächlicher Baseline 0 einmal davor; nach einem zulässigen 343-Gegenbefund
oder Syntaxannahme einmal nach separat attestiertem Previewwert 1. Bei Baseline 1
bleibt die ausgeschaltet-gegen-eingeschaltet-Kontrolle SKIP, kein künstliches OFF.
Alle anderen Client-/SQL-/Bindungsfehler stoppen. Keine Fixture oder Vector-Indizes
vor/nach Parsing, kein Indexbuild, VECTOR_SEARCH oder automatischer ANN-Folgelauf.

PREVIEW_FEATURES=ON bleibt der einzige erlaubte Konfigurationseffekt, danach
tatsächlicher Restore der exakt gespeicherten 0/1. Vollständiger Source-/Baseline-/
Host-/DB-Optionsvergleich, markergebundener eigener DB-Abbau, separater neuer
SQL-Abwesenheitsclient und gebundener Containerabbau mit separater Abwesenheit.
Regulärer gemeinsamer Lifecycle höchstens 300 Sekunden; separater gesamter Cleanup
höchstens 60 Sekunden, Prozessbudgets zusammen höchstens 50 Sekunden plus zehn
Sekunden Reserve. Original-/Recoveryfehler getrennt erhalten; kein Cleanup-PASS
bei fehlendem Nachweis. Secrets ausschließlich in der Umgebung.

Kein zusätzlicher MAXDOP-, Host-, TLS-, Cloud-/Bezahl-API-, ONNX- oder
ALLOW_STALE_VECTOR_INDEX-Effekt. Andere Repositories unverändert. Nach diesem
einzigen Kandidaten wird unabhängig vom Resultat angehalten; Integration des
wahrheitsgemäßen Befunds, aktuelle Head-/Main-Gates, Synchronisierung und eigener
Branchcleanup gehören zum Abschluss. Tatsächlicher Build/Search bleibt weiterhin
an einen späteren eigenen Umfang und wirksamen freigegebenen DOP-1-Pfad gebunden.
