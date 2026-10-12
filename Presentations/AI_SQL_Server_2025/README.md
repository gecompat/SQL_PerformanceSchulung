# KI mit und für Microsoft SQL Server 2025

Die [editierbare PowerPoint-Präsentation](../SQL_Server_2025_KI.pptx) enthält
61 deutschsprachige Folien für `CUR-013` bis `CUR-022`, davon 27 neue
Einführungsfolien vor den bisherigen Fachmodulen. Texte, Tabellen und
Sprechernotizen sind native PowerPoint-Objekte. Die Notizen enthalten
Moderation, konkrete Demoaufrufe und Quellen aus dem bestehenden Quellenregister.

`content.mjs` und der dort eingebundene Einsteigerblock `introduction.mjs`
bilden die fachliche Masterquelle dieses eigenständigen KI-Streams.
`build.mjs` erzeugt ausschließlich das zugehörige Deck. Änderungen erfolgen in
dieser Quelle und werden reproduzierbar exportiert. Das Performance-Masterdeck
und sein Variantenmanifest bleiben eigenständige bestehende Artefakte.

## Verwendung im Unterricht

Der gemeinsame Einstieg setzt keine KI-Erfahrung voraus. Ein synthetischer
Wissensbasisfall führt von einer bekannten SQL-Abfrage zu einer Frage in
Alltagssprache. Die Einführung erklärt KI, Modell, Training, Inferenz,
Sprachmodell und Embedding jeweils vor der ersten Verwendung in der Übung.
Sichtbare Voraussetzungen, typische Hindernisse und nächste Schritte helfen
bei Version, Client, eigener Labinstanz, Rechten und späterem Modellzugang.

Die erste angeleitete SQL-Vorführung verwendet fest zugeordnete geometrische
Vektoren und ausschließlich lokale Variablen/SELECT. Vorhersage, erwartete
Rangfolge und Interpretation folgen auf getrennten Folien. Sie benötigt weder
Modellservice noch Cloudkonto, Credential, Previewkonfiguration oder eigene
Tabelle. Die synthetischen Zahlen stammen aus einer didaktischen Zuordnung,
nicht aus einem Sprachmodell. Ohne eigene SQL-2025-Instanz lässt sich das
Ergebnis gemeinsam als Leseaufgabe besprechen. Für eine tatsächliche Ausführung
wird vorher die bereitgestellte Labverbindung geprüft.

Die Lehrperson entscheidet danach, welche Fachmodule und manifestbasierten
Demos zur Gruppe passen. Der vollständige Foliensatz ist ein Materialvorrat,
keine gemessene Kursdauer. Die bisherigen Zeitplanungen von 150/390/640 Minuten
belegen keine Lehrdauer der erweiterten Fassung. Die angeleitete Vorführung
führt keine neue bewertete Arbeitsheftaufgabe oder Rubrik ein.

Die Reihenfolge deckt Grundlagen, Vektoren, Chunking, Modellpfade, Suche/RAG,
Security, ANN, Performance, SQL-Assistenz und Entscheidung ab. Neun
IMPLEMENTED-Demos und neun PROPOSED-Entwürfe sind ausdrücklich getrennt.
Die vorgeschlagenen Lehrzeiten sind nicht erprobt. Vollständige Lehrpfad-,
TP-PERF-, Teilnehmer- und Generalprobenabnahme stehen weiterhin aus.

Die [konkreten Teaching Paths](../../Documentation/HowTo/SQL_SERVER_2025_AI_TEACHING_PATHS.md)
planen90 Netto-Minuten für den gemeinsamen Einstieg. Die aktuellen kanonischen
Bruttofenster betragen vier Stunden für BASIS, einen Unterrichtstag für STANDARD
und zwei Tage für VERTIEFUNG; Pausen und Nettolehrzeit sind getrennt.
STANDARD enthält den vorbereiteten Offlinekern mit acht Arbeitsheftaufgaben.
Offene Live-/Provider-/Performancepfade bleiben gesonderte Erweiterungen.
Die frühere Modulschätzung wird nur als Planhistorie erhalten; alle neuen Zeiten
brauchen eine tatsächliche Generalprobe. Deck/PPTX und seine bisherigen Prüfnachweise
werden durch diese reine Ablaufplanung nicht neu erzeugt.

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
Readerplanaussage auf Folie 58 ist auf main
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
| `AI_SLIDES_BUILD_DIR` | Optionaler frischer privater Buildbereich innerhalb des Workspace |
| `AI_SLIDES_OUTPUT` | Optionaler neuer Ausgabepfad innerhalb des Workspace |

```powershell
node Presentations/AI_SQL_Server_2025/build.mjs
```

Der Builder exportiert ein privates Kandidatenpaket, standardmäßig unter
`Runtime/Temp/ai-slides`, neutralisiert ausschließlich Identitätsmetadaten
und automatische Vorschau, prüft Paket, Geometrie, Schrift und native Tabellen
und schreibt anschließend die Präsentation. Der Finalizer überschreibt keine
vorhandene Ausgabe. Für einen neuen Kandidaten wird die vorherige eigene
Ausgabe nach Prüfung ihres Pfads in den privaten Buildbereich verschoben.
Bei einer Überarbeitung empfehlen sich stattdessen ein frischer privater
Buildbereich und `AI_SLIDES_OUTPUT` auf einen neuen privaten Ausgabepfad.
Build-/Receiptbereich und finaler Ausgabeordner müssen getrennte Ordner sein,
zum Beispiel `Runtime/Temp/ai-slides-c2/render` und
`Runtime/Temp/ai-slides-c2/output/SQL_Server_2025_KI.pptx`.
Erst die validierten finalen Bytes ersetzen die gewünschte veröffentlichte Datei.
Der Gesamtumfang und die Tabelleneigentümer folgen der tatsächlichen Deckquelle.
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

Der reparierte ursprüngliche 34-Folien-Export vom 2026-10-12 ist zusätzlich in
Microsoft PowerPoint 16.0 geprüft: 34 Folien geöffnet, 13 native Tabellen erkannt,
Text, Tabellenzelle und Sprechernotiz bearbeitet sowie eine private Kopie
gespeichert und erneut geöffnet. Seine Folien- und Notizenparts blieben gegenüber
dem ersten Deck bytegleich. Die nun erweiterte 61-Folien-Fassung ist vollständig
neu gerendert und einzeln visuell geprüft. PowerPoint 16.0 öffnete alle 61 Folien
mit 23 nativen Tabellen und 61 Sprechernotizen. Text, Tabellenzelle und Notiz
bearbeiten sowie eine private Kopie speichern/erneut öffnen bestanden ebenfalls.
Die Office-Testkopien bleiben privat, die veröffentlichte Datei ist neutralisiert.
Diese Prüfung ersetzt keine Teilnehmererprobung oder Generalprobe.

## Hinweise bei abweichender Darstellung

Eine fehlende Arial-Schrift, andere Glyphenmetriken oder abweichende
Localeeinstellungen können Zeilenumbrüche und Zahlenformate verändern.
Die Tabelle auf Folie 55 enthält feste deutsche Dezimaldarstellung sowie die
angegebenen Einheiten. Vor Unterricht oder PDF-Export die konkrete Anwendung
auf Umbruch und Glyphen prüfen. Ein PNG-Render bestätigt keinen editierenden
PowerPoint- oder Google-Slides-Anwendungstest. Bei SQL-Ausgaben Nativeencoding,
Dezimalzeichen und Zeitauflösung gemäß dem jeweiligen Ergebnisvertrag prüfen.
Fehlende Messwerte, gemessene Null, WARN, SKIP und FAIL bleiben getrennt.

Pflegeautorität für Demo-Gates, neue Runtimebelege und Wiederaufnahme bleibt
der [kanonische Ausführungsstand](../../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md).
Das Deck erweitert dessen Freigaben nicht.
