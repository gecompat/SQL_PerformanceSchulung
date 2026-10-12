# KI mit und für Microsoft SQL Server 2025

Die [editierbare PowerPoint-Präsentation](../SQL_Server_2025_KI.pptx) enthält
34 deutschsprachige Folien für `CUR-013` bis `CUR-022`. Texte, Tabellen und
Sprechernotizen sind native PowerPoint-Objekte. Die Notizen enthalten
Moderation, konkrete Demoaufrufe und Quellen aus dem bestehenden Quellenregister.

`content.mjs` ist die fachliche Masterquelle dieses eigenständigen KI-Streams.
`build.mjs` erzeugt ausschließlich das zugehörige Deck. Änderungen erfolgen in
dieser Quelle und werden reproduzierbar exportiert. Das Performance-Masterdeck
und sein Variantenmanifest bleiben eigenständige bestehende Artefakte.

## Verwendung im Unterricht

Die Reihenfolge deckt Grundlagen, Vektoren, Chunking, Modellpfade, Suche/RAG,
Security, ANN, Performance, SQL-Assistenz und Entscheidung ab. Neun
IMPLEMENTED-Demos und neun PROPOSED-Entwürfe sind ausdrücklich getrennt.
Die vorgeschlagenen Lehrzeiten sind nicht erprobt. Vollständige Lehrpfad-,
TP-PERF-, Teilnehmer- und Generalprobenabnahme stehen weiterhin aus.

Demoaufrufe setzen den [Ausführungsleitfaden](../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md)
voraus. Eine eigene dedizierte Labinstanz, aktuelle Preflight-Ergebnisse und
markergebundenes Cleanup sind verbindlich. SQL-Authentifizierung verwendet
ausschließlich `SQLCMDPASSWORD` in der Umgebung. Aufgeführte Codeauszüge sind
keine zusätzlichen Aufrufer. Der [Trainerleitfaden](../../Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_TRAINER_GUIDE.md)
ergänzt die Durchführung. Lösungen und Rubrik bleiben ausschließlich im
[Arbeitsheft](../../Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md).

Die lokale Offlinequalifikation betrifft Linux/Docker und den ergänzenden
Podmanpfad der acht Basisdemos. `CON-010` besitzt einen eigenen begrenzten
Consumer-/Versionsnachweis. Windows, andere Editionen, Serverlogins und
Verbindungspooling werden daraus nicht abgeleitet. Live-Provider, Cloud und
ONNX besitzen eigene Freigaben. Der öffentliche Provider-Livepfad bleibt
wegen `DEC-033`/SQLcmd-P blockiert. Zwei private DGN-010-Original-Readerplanprofile
sind belegt. Vollständige Runtime-/TP-PERF-Abnahme und Indexnettonutzen bleiben
`NOT_ESTABLISHED`.

Die fachliche Recherchebindung des Decks ist `origin/main` bei
`83d28cd59ae1f8a34028518e4904e44800236e81`, Stand 2026-10-12. Die konkrete
Readerplanaussage auf Folie 31 ist auf main
`4bfb1914623c3c49fcc287ee8079013a0fad6ddb` aktualisiert. Der integrierte
[Readerplan-UTC-Nachweis](../../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_READER_CLOCK_REVIEW.md)
belegt zwei private vollständige Original-Readerplanprofile.
Die öffentlichen Producer und vollständige Runtime-/TP-PERF-/Nettonutzengates
bleiben davon getrennt. Dieser zusätzliche Nachweis hebt die allgemeine
Unterrichts- oder Performancegrenze des Decks nicht auf.

## Reproduzierbarer Export

Voraussetzungen: Node.js, Python, `@oai/artifact-tool`, die Präsentationswerkzeuge
des Presentations-Skills und eine verfügbare Schrift Arial. Diese Abhängigkeiten
werden vom Aufrufer bereitgestellt, nicht aus privaten Verzeichnissen importiert.
Vor einer Erstellung wird die Artifact-Operation gemäß Presentations-Skill
markiert. Anschließend werden folgende Umgebungsvariablen gesetzt:

| Variable | Inhalt |
|---|---|
| `ARTIFACT_NODE_MODULES` | Absoluter Pfad zum bereitgestellten Node-Paketverzeichnis |
| `PRESENTATION_SKILL_DIR` | Absoluter Pfad zum Presentations-Skill |
| `RUNTIME_PYTHON` | Absoluter Pfad zum Python-Interpreter |

```powershell
node Presentations/AI_SQL_Server_2025/build.mjs
```

Der Builder exportiert ein privates Kandidatenpaket unter
`Runtime/Temp/ai-slides`, neutralisiert ausschließlich Identitätsmetadaten
und automatische Vorschau, prüft Paket, Geometrie, Schrift und native Tabellen
und schreibt anschließend die Präsentation. Der Finalizer überschreibt keine
vorhandene Ausgabe. Für einen neuen Kandidaten wird die vorherige eigene
Ausgabe nach Prüfung ihres Pfads in den privaten Buildbereich verschoben.
Renderbilder, Layoutdaten und Validierungsbericht bleiben unter `Runtime`.
Jede finale Folie muss zusätzlich einzeln visuell geprüft werden.
Nach einer eng begrenzten Korrektur erlaubt `AI_SLIDES_RENDER_ONLY` die
aktuelle betroffene Foliennummer. Unveränderte Folien benötigen dabei einen
vorhandenen passenden Render- und Einzelprüfnachweis. Paket, Metadaten,
Geometrie und finaler Import werden weiter am vollständigen Deck geprüft.

Die Neutralisierung erhält den Namespacepräfix `dcterms` auch für den
Attributwert `xsi:type="dcterms:W3CDTF"` in den Datumsmetadaten. Wohlgeformtes
XML und ein erfolgreicher Rendererimport reichen dafür nicht: ein ungebundener
Präfix in diesem Attributwert führte beim ersten Export zur Ablehnung durch
PowerPoint. Der Regressionstest `Tests/Static/test_ai_presentation_package.py`
prüft die auflösbaren Datums-QNames am synthetischen Export und am veröffentlichten
Deck sowie eine negative Kontrolle des ursprünglichen Fehlers. Der vorhandene
Presentation-Workflow führt diese drei lokalen Prüfungen zusätzlich aus;
SQL-Runtime und weitere Dienste werden dadurch nicht ausgelöst.

Die Metadatenkorrektur vom 2026-10-12 ist zusätzlich in Microsoft PowerPoint
16.0 geprüft: 34 Folien geöffnet, 13 native Tabellen erkannt, Text, Tabellenzelle
und Sprechernotiz bearbeitet sowie eine private Kopie gespeichert und erneut
geöffnet. Die veröffentlichten Folien- und Notizenparts sind gegenüber dem
ersten Deck bytegleich; die bestehenden visuellen Einzelprüfungen gelten weiter.
Die Office-Testkopie bleibt privat, die veröffentlichte Datei ist neutralisiert.

## Hinweise bei abweichender Darstellung

Eine fehlende Arial-Schrift, andere Glyphenmetriken oder abweichende
Localeeinstellungen können Zeilenumbrüche und Zahlenformate verändern.
Die Tabelle auf Folie 28 enthält feste deutsche Dezimaldarstellung sowie die
angegebenen Einheiten. Vor Unterricht oder PDF-Export die konkrete Anwendung
auf Umbruch und Glyphen prüfen. Ein PNG-Render bestätigt keinen editierenden
PowerPoint- oder Google-Slides-Anwendungstest. Bei SQL-Ausgaben Nativeencoding,
Dezimalzeichen und Zeitauflösung gemäß dem jeweiligen Ergebnisvertrag prüfen.
Fehlende Messwerte, gemessene Null, WARN, SKIP und FAIL bleiben getrennt.

Pflegeautorität für Demo-Gates, neue Runtimebelege und Wiederaufnahme bleibt
der [kanonische Ausführungsstand](../../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md).
Das Deck erweitert dessen Freigaben nicht.
