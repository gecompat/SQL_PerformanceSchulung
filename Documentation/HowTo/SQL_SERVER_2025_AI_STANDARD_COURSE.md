# KI mit SQL Server 2025 STANDARD

Dieser Unterrichtstag erweitert den [BASIS-Kurs](SQL_SERVER_2025_AI_BASIS_COURSE.md)
auf den vollständigen Offlinekern: Vektortyp, Metrik, Chunking, Suchpfade,
Quellenentscheidungen, Wertbindung, Modellrechte und manipulierte Quellen.
Die [STANDARD-Präsentation](../../Presentations/SQL_Server_2025_KI_STANDARD.pptx)
enthält 45 Folien. Der gemeinsame Einstieg braucht SELECT-/ORDER-BY-Grundkenntnisse,
aber keine KI-Erfahrung. Eine vorherige BASIS-Teilnahme ist nicht erforderlich;
wer BASIS bereits kennt, nutzt den Einstieg zur Wiederholung.

Am Ende begründen Teilnehmende eine Suchentscheidung mit Modellraum und
Quellenherkunft, prüfen eine Antwort am erlaubten Kontext und unterscheiden
Wertbindung, Strukturpolicy und tatsächliche SQL-Rechte. Alle acht Aufgaben
verwenden feste synthetische Fixtures; es wird kein Live-Modell aufgerufen.
Ein Cloudkonto, Modellservice oder Modelldownload ist nicht erforderlich.

## Vorbereitung vor dem Kurstag

Die Lehrperson bereitet eine eigene SQL-2025-Testinstanz mit CL 170, Client,
Ownerzugang und den acht unveränderten Demomanifesten vor. Die tatsächlich
geprobte Umgebung und ihre Grenzen stehen im
[Generalprobenachweis](../Project_Planning/SQL_SERVER_2025_AI_STANDARD_REHEARSAL.md).
Die einzelnen Demo-READMEs und der [Ausführungsleitfaden](DEMO_EXECUTION_GUIDE.md)
bleiben für Rechte, Preflight, Phasen, Sicherheitsbestätigung und Recovery maßgeblich.
SQL-Authentifizierung verwendet ausschließlich `SQLCMDPASSWORD` in der Umgebung.
Setup-/Cleanupownerrechte sind keine Teilnehmerrechte. Die eingeschränkten
Identitäten von QRY-019, DGN-008 und DGN-009 bleiben Teil des Harness.

Öffnen Sie Präsentation, diesen Ablauf, [Arbeitsheft mit Lösungen und Rubrik](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md)
und [Glossar](SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md). Prüfen Sie vorab die eigene
Labverbindung sowie die Abwesenheit der eigenen Demo-Datenbanken. Verbindung,
Installation und Konteneinrichtung liegen außerhalb des Tagesfensters.
QRY-017 erlaubt fehlenden Full-Text als sichtbaren
`WARN_OPTIONAL_EVIDENCE_SKIPPED`; der übrige Suchvergleich bleibt prüfbar.
Dieser Status ist kein bestandener Full-Text-Lauf. SQL Server 2019/2022 mit
`SKIP_VERSION` ersetzt keine praktische SQL-2025-Durchführung.

## Tagesablauf mit drei Pausen

Alle Angaben sind Minuten seit Beginn. Geplant sind 480 Minuten, davon
420 Minuten Lehre einschließlich Rückfragen und 60 Minuten Pause. Die
SQL-Werkzeuglaufzeiten der Generalprobe sind keine gemessenen Unterrichtszeiten.
Die STANDARD-Fußzeile nennt Kursnummer und Quellfolie des Masterdecks;
die [Kursdefinition](../../Presentations/AI_SQL_Server_2025/standard.course.json)
bindet Auswahl, Aufgaben und Zeitfenster.

| Zeit | STANDARD-Folien | Durchführung und Lernbeleg |
|---|---|---|
| 00–10 | 1–7 | Wissensbasisfall und bekannte SELECT-Abfrage lesen; erwartete Quelle und Antwort nennen. |
| 10–25 | 8–13 | KI (künstliche Intelligenz; Verfahren für Aufgaben wie Textverarbeitung oder Vorhersagen), Modell, Training, Inferenz und Token einzeln erklären und einer Aufgabe zuordnen. |
| 25–40 | 14–17 | Engine, Client, CL und Rechte unterscheiden; bei einem Hindernis den vorbereiteten nächsten Schritt wählen. |
| 40–60 | 18–21 | Id-Reihenfolge und Distanzen vorhersagen; vollständige read-only Query vorführen, geometrische Aussage erklären. |
| 60–70 | 22–23 | Zahlenzuordnung und Sprach-Embedding unterscheiden; Voraussetzungen eines echten Modellzugangs nennen. |
| 70–85 | 24–27 | Herkunft, Version und erlaubten Kontext verfolgen; falsche Antwort und begründete Nichtantwort unterscheiden. |
| 85–90 | 28 | Vorhersage → Beobachtung → Erklärung → Cleanup für die Praxis klären. |
| 90–105 | – | Pause. |
| 105–140 | 29–32 | QRY-014 und QRY-015 mit Arbeitsheftaufgaben: Typ/Modellraum sowie Rangfolge vor/nach Normalisierung belegen. |
| 140–170 | 33–34 | QRY-016: einen Chunk je Version und Overlapprofil dem Originaltext zuordnen. |
| 170–200 | 35–36 | QRY-017: die Frage nach MOD_A mit relationalem Pfad, LIKE, optionalem Full-Text und Exact Distance vergleichen. |
| 200–230 | 37–38 | QRY-018: Quellenentscheidungen an tatsächlichen Ergebnissen lesen und die Arbeitsheftaufgabe begründen. |
| 230–260 | – | Mittagspause. |
| 260–290 | 39–40 | QRY-019: Literal-Treffer, Strukturabwehr und tatsächliche Readergrenze getrennt belegen. |
| 290–325 | 41–43 | DGN-008: Setup, Ingestion und Retrieval den tatsächlichen Rollen und Grants zuordnen. Kein Embeddingaufruf. |
| 325–355 | 44 | DGN-009: manipulierten Retrievaltext, feste Antwort-/Toolpolicy und Rechteverweigerung auseinanderhalten. |
| 355–370 | – | Pause. |
| 370–410 | bisherige Fachfolien nach Bedarf | Acht Beobachtungsbögen vergleichen, Fehlinterpretationen am konkreten Ergebnis korrigieren und Cleanupbelege prüfen. |
| 410–430 | 45 | Transferfall mit Suchfrage, widersprüchlichen Quellen und manipulierter Zusatzanweisung bearbeiten. |
| 430–480 | nach Bedarf | Individuelle Hindernisse klären, Aufgaben erneut erklären und offene Begriffe sammeln. |

Die Lehrperson nutzt die Reserve für Rückfragen und Wiederholung, nicht für
zusätzliche Provider-, ANN- oder Performanceversuche. Der Tageskurs enthält
keine zusätzlichen RES-008-/E1–E3-Evidenzaufgaben und keine CON-010-Poolingprobe.
Diese bleiben Vertiefungsmaterial. Bei langsamer Bearbeitung werden Istzeiten
festgehalten und die Reserve genutzt; der Einstieg wird nicht stillschweigend gekürzt.

## Praktische Durchführung der acht Aufgaben

Die erste Vektorquery auf Folie 20 bleibt die vollständige Variablen-/SELECT-
Vorführung des BASIS-Einstiegs. Die manuell gesetzten Zahlen erklären Geometrie,
keine Sprachrelevanz. Danach führt die Lehrperson jeweils genau eine Demo
vollständig aus, bespricht ihre Ausgabe und prüft unabhängig die DB-Abwesenheit,
bevor die Gruppe zum nächsten Abschnitt geht.

Für jeden Eintrag wird die folgende Vorlage vom Repository-Stamm aus mit der
zugehörigen relativen Manifestdatei ausgeführt. `$courseServer` und
`$courseUser` werden vorab auf die eigene Labverbindung gesetzt. Authentifizierung
und Zertifikatswahl sind vor Beginn nach Ausführungsleitfaden einzurichten.

```powershell
# Pro Aufgabe genau einen Manifestpfad aus der Tabelle einsetzen.
$courseManifest = 'Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/manifest.json'
python Demos/00_Framework/Tools/run_demo.py $courseManifest --server $courseServer --auth sql --username $courseUser --show-output
if ($LASTEXITCODE -ne 0) { throw 'Demolauf ist nicht erfolgreich abgeschlossen.' }
```

| Aufgabe | Manifest unter Demos/09_AI_SQL_Server_2025/ | Beobachtung vor der Lösung |
|---|---|---|
| QRY-014 | `QRY-014_Vector_Type/manifest.json` | Fünf Rows, Dimension/Basistyp und ungültige Eingaben; gleicher Typ beweist keinen gleichen Modellraum. |
| QRY-015 | `QRY-015_Vector_Metrics/manifest.json` | Rohes Dot-Ranking, normalisierte Rangfolge und Id-Tieregel. |
| QRY-016 | `QRY-016_Chunk_Provenance/manifest.json` | DocId, Version, Offset, Länge und Overlap gegen den Originaltext. |
| QRY-017 | `QRY-017_Search_Comparison/manifest.json` | Autorisierter Identifier-Treffer, vier konstruierte Rows und tatsächlicher Full-Text-Status. |
| QRY-018 | `QRY-018_Offline_RAG/manifest.json` | Zehn Bewertungen: eine akzeptierte, sieben abgelehnte und zwei begründete Nichtantworten. Die Aufgabe bespricht vier ausgewählte Fälle. |
| QRY-019 | `QRY-019_SQL_Input_Policy/manifest.json` | Literal-Treffer trotz DDL-Text als Wert, abgelehnte Struktur und echte Rechtefehler. |
| DGN-008 | `DGN-008_Offline_Model_Rights/manifest.json` | Modellmetadatenrecht, Grantreduktion und erlaubter Restbetrieb; kein Nachweis einer Providerinferenz. |
| DGN-009 | `DGN-009_Offline_Injection/manifest.json` | Tatsächlich retrievter manipulierter Text, feste Fixtures und konkrete Rechteverweigerung. |

Nach **jeder** Demo wird die folgende neue master-Verbindung geprüft. Die
Liste umfasst ausschließlich die acht bekannten LOCAL-Namen dieses Kurses.
Sie dient der Abwesenheitsprüfung und erteilt keine Löschbefugnis.

```powershell
sqlcmd -S $courseServer -U $courseUser -d master -b -Q "SET NOCOUNT ON; IF EXISTS(SELECT 1 FROM sys.databases WHERE name IN(N'SQLPERF_LAB_QRY014_LOCAL',N'SQLPERF_LAB_QRY015_LOCAL',N'SQLPERF_LAB_QRY016_LOCAL',N'SQLPERF_LAB_QRY017_LOCAL',N'SQLPERF_LAB_QRY018_LOCAL',N'SQLPERF_LAB_QRY019_LOCAL',N'SQLPERF_LAB_DGN008_LOCAL',N'SQLPERF_LAB_DGN009_LOCAL')) THROW 51004,'FAIL_CLEANUP',1; PRINT 'STANDARD_DB_ABSENT';"
if ($LASTEXITCODE -ne 0) { throw 'Cleanup muss geklärt werden.' }
```

Nur `PASS|OK` gilt als uneingeschränkt erfolgreiche Demo. QRY-017 darf bei
nachweislich fehlendem Full-Text den genannten optionalen WARN behalten.
Notieren Sie diesen mit dem konkreten Teilbefund. DDL-Text in einer Wertfixture
oder Quelle wird gelesen und nie als freier SQL-Auftrag übernommen.

## Beobachtung, Bewertung und Transfer

Verwenden Sie den bestehenden [Arbeitsheftbogen und die einzige Rubrik](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md#beobachtungsbogen-und-bewertungsrubrik).
Vor jeder Demo notieren Teilnehmende eine Vorhersage. Danach halten sie die
konkrete Row, Quellenstelle oder Rechteverweigerung fest und erklären die
beobachtete Grenze. Jede der acht Aufgaben hat unverändert 0–2 Punkte, zusammen
höchstens 16 Punkte. Es wird keine zusätzliche Bestehensgrenze eingeführt.
Lösungen bleiben ausschließlich im Arbeitsheft.

In der gemeinsamen Besprechung erklärt jede Gruppe einen Befund und eine
Schlussfolgerung, die der kleine Versuch noch nicht trägt. Halten Sie
Geometrie/Sprachrelevanz, vier Besprechungsfälle/zehn RAG-Bewertungen,
Metadatenrecht/Inferenz und feste Policy/Verhalten unbekannter Modelle auseinander.

Der unbewertete Transfer auf Folie 45 verbindet drei Fragen: Welche Suche passt
zu einer exakten Dokumentkennung und welche zu einer inhaltlichen Frage?
Was tun bei zwei aktuellen erlaubten Quellen mit widersprüchlichen Werten?
Welche Befugnis folgt aus einem Quellenabsatz, der eine Zusatzaktion verlangt?
Begründen Sie die Antwort mit Herkunft, erlaubtem Kontext und dem nächsten
fachlichen Prüfschritt anhand der vorhandenen Aufgabenlösungen. Die Aufgabe
verlangt keinen neuen Indexentwurf und keine Livegeneration.

## Ausfall und sicherer Abschluss

Bei Verbindungs-, Versions- oder Rechtefehlern wird die betreffende Aufgabe als
Ergebnisleseaufgabe mit dem Arbeitsheft fortgesetzt und im Beobachtungsbogen
so bezeichnet. Ein gelesener Sollwert ersetzt keinen tatsächlichen Lauf.
Installationen, zusätzliche Grants und Provideränderungen werden außerhalb
der Schulung geklärt. Ein fachlicher FAIL bleibt erhalten; ein neuer Lauf
braucht geänderte Eingaben oder einen begründeten Prüfauftrag.

Nach Abbruch verwendet die Lehrperson den markergebundenen Recoverypfad der
betroffenen Demo. Der Datenbankname allein genügt nie für Cleanup. Der Abschnitt
ist erst mit geklärter eigener DB-Abwesenheit oder dokumentiertem Cleanupfehler
geschlossen. Fremde Datenbanken und Sessions bleiben unberührt.

Das Trainerprotokoll erfasst je Zeitblock Soll-/Ist-Minuten, Live-/Lesemodus,
Ergebnis-/Cleanupbeleg, Unterbrechung und offene Verständnisfrage. Verwenden
Sie synthetische Teilnehmerkennungen und keine Namen oder fremden SQL-Texte.
Die technische und redaktionelle Generalprobe qualifiziert das Kurspaket;
Verständlichkeit, Lernerfolg und reale Lehrdauer werden erst mit einer
tatsächlichen Teilnehmergruppe erprobt.
