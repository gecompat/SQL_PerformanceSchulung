# VERTIEFUNG Kurs und technische Generalprobe

Stand: 18. Oktober 2026. Der beauftragte VERTIEFUNG-Kurs ist als Zweitagespaket
mit technischer und redaktioneller Generalprobe vorbereitet. Der
[Kursleitfaden](../HowTo/SQL_SERVER_2025_AI_VERTIEFUNG_COURSE.md) verbindet den
vollständigen STANDARD-Praxistag mit konkreten Tag-2-Beleg-/Entwurfsaufgaben
im bestehenden Arbeitsheft. Dies schließt den VERTIEFUNG-Materialschnitt von
TSK-012/TSK-014; reale Teilnehmererprobung und volle Streamfreigabe bleiben offen.

## Geprüftes Kurspaket

Die eigenständige Präsentation besitzt 61 Kursfolien aus 56 Masterfolien.
Fünf Quellfolien werden an Tag 2 gezielt wiederholt. Die erste Transferfolie
bleibt STANDARD-gerecht; die letzte verlangt eine begrenzte Empfehlung,
Gegenbeleg und konkreten Prüfauftrag. Auswahl, Tagesgrenzen, Wiederholungen
und Anpassung pro tatsächlicher Kursfolie sind in
[vertiefung.course.json](../../Presentations/AI_SQL_Server_2025/vertiefung.course.json)
gebunden. Tag 1 entspricht in Ablauf und Inhalt vollständig dem aktuellen
STANDARD-Profil. Alle Zeiten sind Planwerte: je 420 Lehr- und 60 Pausenminuten,
zusammen 840+120. Die Nacht zwischen den Tagen ist nicht Teil dieser Rechnung.

SHA256 der geprüften VERTIEFUNG-PPTX:
`40ab8506a211b127383b4c655faf9b60f6aa9157034bfcbecf63a743a776cc8f`.
Materialstand der übernommenen Folien bleibt der 12. Oktober; Kursauswahl,
Leitfaden und Generalprobe stammen vom 18. Oktober 2026. Vollständiges Deck,
BASIS-/STANDARD-PPTX, Masterquellen und sämtliche SQL-/Runtimequellen bleiben
unverändert. Die Aufgaben und Musterlösungen sind ausschließlich im bestehenden
Arbeitsheft ergänzt. Tag 1 hat unverändert höchstens 16 Punkte, Tag 2 ist unbewertet.

## Neue technische Probe von Tag 1

Für die ausdrücklich beauftragte Kursgeneralprobe wurde eine eigene frische
Linux-/Docker-Instanz mit dem vorhandenen Image
`mcr.microsoft.com/mssql/server:2025-CU9-ubuntu-24.04` erstellt, begrenzt auf
vier CPUs und acht GiB. Tatsächlich gemessen: SQL Server 17.0.5005.3, Major 17,
master CL 170. Keine Ports oder Hostverzeichnisse wurden veröffentlicht;
das zufällige Kennwort blieb ausschließlich in Prozessumgebungen.

Alle acht unveränderten Demos wurden über die vorhandenen öffentlichen
FWK-010-/FWK-011-Lifecycles je zweimal vollständig ausgeführt. Neue master-
Verbindungen bestätigten unabhängig die eigene DB-Abwesenheit vor und nach
jedem Lauf. Dies ist eine neue Kursprobe, keine Wiederholung der vollständigen
unveränderten Versions-/Provider-/Markerqualifikationsmatrizen.

| Demo | Lauf 1 | Lauf 2 | Ergebnisassertionen je Lauf |
|---|---|---|---:|
| QRY-014 | PASS / OK | PASS / OK | 3 |
| QRY-015 | PASS / OK | PASS / OK | 3 |
| QRY-016 | PASS / OK | PASS / OK | 3 |
| QRY-017 | WARN / WARN_OPTIONAL_EVIDENCE_SKIPPED | WARN / WARN_OPTIONAL_EVIDENCE_SKIPPED | 3 |
| QRY-018 | PASS / OK | PASS / OK | 4 |
| QRY-019 | PASS / OK | PASS / OK | 5 |
| DGN-008 | PASS / OK | PASS / OK | 9 |
| DGN-009 | PASS / OK | PASS / OK | 8 |

Alle 76 Ergebnisassertionen sind erfüllt. QRY-017 prüfte die tatsächlich
fehlende Full-Text-Komponente und behält den vorgesehenen optionalen WARN.
Die SQL-Gesamtprobe bleibt daher WARN. Es wurde nichts installiert und kein
Lauf bis zu einem PASS wiederholt. Am Ende war keine Benutzerdatenbank mehr
auf der eigenen Instanz vorhanden. CID, Name und beide Eigentumslabels wurden
vor dem vollständigen Entfernen des eigenen Containers einschließlich
anonymer Volumes exakt geprüft; neues Inspect bestätigte seine Abwesenheit.
Der Durchlauf dauerte 179,875 Sekunden einschließlich Start und Abbau.
Ein Containerdurchlauf, keine neue Modell-/Providerinferenz. Dies sind
Werkzeuglaufzeiten, keine gemessenen Unterrichtszeiten.

Die unveränderte erste Variablen-/SELECT-Vektorquery ist in der
[BASIS-Generalprobe](SQL_SERVER_2025_AI_BASIS_REHEARSAL.md) tatsächlich belegt
und wird hier nicht als erneut ausgeführt bezeichnet.

## Technischer und fachlicher Durchgang von Tag 2

Der neue Kursvalidator führt ausschließlich lokale Dateiprüfung und Rechnungen
aus. Acht veröffentlichte Belegquellen sind mit normalisierten SHA256 gebunden;
Änderungen daran verlangen eine neue Prüfung ihrer Kurszuordnung. Die
[Rechenfixture](../../Tests/Static/Fixtures/ai-courses/vertiefung.json) trennt
ausdrücklich didaktische Listen und bereits veröffentlichte empirische Zahlen.
Die synthetische ANN-Aufgabe ergibt zwei gemeinsame Treffer bei k=5, also
Recall 0,4. Sie ist keine neu gemessene ANN-Qualität. Die RES-008-Rechnung ergibt
20 Warmups, 54 Messfenster, 74 Requests und 5420 kontrollierte Queries sowie
n=6 Vergleichsfenster je A/B-Pfad. Die Zahlen des ersten 384er-Paars werden
direkt gegen die veröffentlichte Markdown-Beobachtungszeile geprüft.

Der redaktionelle Aufgabendurchgang verfolgte jede Abgabe bis zur Musterlösung:
erlaubte ANN-Population und DML-/Rollengrenze, unterschiedliche Messbereiche,
vier Modellarchitekturen, begrenzter Readerplan-/Kostenbefund, drei
Verbindungskontexte sowie vier vorab festgelegte Evaluationsfälle. Die fertigen
Empfehlungen verlangen einen widerlegbaren nächsten Prüfauftrag, keine neue
Ausführung im Kurs. Die Prüfung der Materialkonsistenz attestiert weder
Herkunft privater Rawrecords noch die bisher offene Gesamtqualifikation.

Generation UNKNOWN, V2-Recordkohärenz mit WARN, SQLcleanup TEXTS_COHERENT und
offene Performance-/Poolingabnahmen bleiben erhalten. Tag 2 erzeugte keine
SQL-, Modell-, Container-, Cloud-, ONNX- oder Hosteffekte. Der vorhandene
Original-FAIL wird nicht in PASS umgeschrieben. Private Receipts werden nicht
als Teilnehmermaterial benutzt.

Die zusätzlichen Produktgrenzen wurden am 18. Oktober gegen die Primärquellen
[VECTOR_SEARCH](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-search-transact-sql?view=sql-server-ver17),
[CREATE VECTOR INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-vector-index-transact-sql?view=sql-server-ver17)
und [SSMS 22 Release Notes](https://learn.microsoft.com/en-us/ssms/release-notes-22)
geprüft. SQL-2025-Preview und neue Azure-Indexgenerationen bleiben getrennt;
die historischen TOP_N-/DML-Befunde sind keine Empfehlung für neue Syntax.
Die genannten SSMS-GA-Stände sind Clientangaben und keine Enginefreigabe.
Bestehende Folienquellen bleiben in den Notizen erhalten.

## Präsentation Prüfungen und Aufwand

Alle zusätzlichen Quellfolien wurden einzeln vor der Ableitung geprüft;
bereits geprüfte unveränderte STANDARD-/BASIS-Quellen wiederverwendet.
Artifact Tool und PowerPoint 16.0 renderten alle 61 finalen Folien.
Alle 61 finalen PowerPoint-Bilder wurden einzeln bei voller Größe visuell
geprüft. Die Datei enthält 20 native Tabellen und 61 Sprechernotizen.
In einer privaten Testkopie blieben Text-, Tabellenzellen- und Notizänderungen
nach Speichern und erneutem Öffnen erhalten. Die veröffentlichte Datei
wurde durch diese Bearbeitung nicht verändert.

Die drei Kursvalidatoren und bestehenden Pakettests bestanden. Sechs neue
Gegenfalltests prüfen verkürzten Tag 1, unerlaubte Tag-2-Runtime, falsche
Tagesgrenzen, Folienreihenfolge/Wiederholungen, STANDARD-/Belegdrift, ungültige
Recallpopulation, falsche veröffentlichte Messwerte und hochgestufte Claims.
Ein tatsächlicher Austausch der letzten Transferfolie durch die Tag-1-Folie
wird abgewiesen. Beide CI-Events müssen die acht gebundenen Belegquellen
berücksichtigen. Ein anfänglicher ZIP-Testfixturefehler war auf die erneute
Verwendung bereits beim Kopieren veränderter ZipInfo-Offsets begrenzt; die
Vorlage wird vor dem Schreiben gelesen, danach bestanden alle sechs Methoden.

Ein Verantwortlicher, ein Zweitageskurs, keine zusätzlichen Agenten oder
Reviewketten. Der vorhandene Kurs-CI-Job führt sieben kleine Pythonaufrufe aus:
drei Validatoren, drei Gegenfallsuiten und einmal die gemeinsamen Pakettests.
Zusätzliche Auslöser sind nur VERTIEFUNG-Material, Arbeitsheft, Fixture und
die acht tatsächlich gebundenen Quellen; keine pauschale Auswahl aller
historischen Reviews. Timeout bleibt fünf Minuten. Kein Folienbuild,
SQL-Container oder Modellaufruf in diesem Job. Der zentrale vorhandene
Privacy-Workflow bleibt der gemeinsame Vollscan. Die einmalige lokale
Tag-1-Probe folgt dem ausdrücklichen Generalprobenauftrag; unveränderte
ANN-/Pooling-/Modell-/Versionsmatrizen werden nicht wiederholt.
Modell-/Tokenverbrauch bleibt mangels verlässlicher Messung unbekannt.

Alle 66 lokalen Materiallinks und Abschnittsverweise in Kursleitfaden,
Generalprobenachweis und Arbeitsheft bestanden die Pfad-/Ankerprüfung.
Der unveränderte Privacy-Scanner bestand für den gesamten Git-Publikationsbestand:
1194 Dateien, 1174 Textdateien, fünf Officepakete und ein unverändert
freigegebenes Artefakt. Diese Auswahl umfasst alle versionierten und neuen
nicht ignorierten Dateien. Bereits ignorierte private Altarchive bleiben
außerhalb dieses Bestands; der bekannte lokale Scannerabbruch daran ist im
BASIS-Nachweis dokumentiert. Der normale vollständige CI-Scan des frischen
Checkouts bleibt erforderlich.

## Verbleibende Teilnehmererprobung

Technische und redaktionelle Kursprobe sind abgeschlossen; reale
Verständlichkeit, Lernerfolg und die geplanten 840 Lehrminuten sind noch
mit einer tatsächlichen Gruppe zu erproben. Der Leitfaden enthält Soll-/Ist-
Protokoll, Beobachtungsbogen und Ausfall-/Recoveryverfahren. Wiederaufnahme
dieses Human-Nachweises bei moderierter Durchführung mit Lehrperson und Gruppe;
dafür bleibt kein angefangener Codebranch offen. Live-Provider, ANN-/Pooling-/
Performance- und volle TSK-012-/TSK-014-/Streamfreigabe bleiben getrennt offen.
Automation und andere pausierte Entwicklungswellen bleiben unverändert.
