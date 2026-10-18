# STANDARD Kurs und Generalprobe

Stand: 18. Oktober 2026. Die nächste beauftragte KI-Welle liefert den
[STANDARD-Tageskurs](../HowTo/SQL_SERVER_2025_AI_STANDARD_COURSE.md) als begrenztes
Teilprodukt von TSK-012/TSK-014. Technische und redaktionelle Generalprobe sind
abgeschlossen. Der optionale Full-Text-Teil bleibt ausdrücklich WARN; eine
Teilnehmererprobung oder Gesamtfreigabe des KI-Streams ist damit nicht belegt.

## Kurspaket und fachlicher Durchgang

Die eigenständige editierbare STANDARD-Datei enthält 45 ausgewählte Folien,
acht vorhandene Offline-Aufgaben und einen durchgehenden Ablauf für
420 geplante Lehr- und 60 Pausenminuten. Auswahl, Praxiszuordnung, Titel und
Masterquellen sind in
[standard.course.json](../../Presentations/AI_SQL_Server_2025/standard.course.json)
gebunden. Die vollständige 61-Folien-Datei und die BASIS-Datei bleiben bytegleich.
Die Masterquellen content.mjs/introduction.mjs und sämtliche SQL-Demos bleiben
unverändert. Der Materialstand der übernommenen Folien ist weiterhin 12. Oktober;
STANDARD-Auswahl, Generalprobe und Kursleitfaden stammen vom 18. Oktober.

SHA256 der geprüften STANDARD-PPTX:
`97f1bcf19c3cd50af17e226d754bc3c3e5898b81e043362520cab9f904106618`.

Der Leitfaden verbindet jede der acht Aufgaben mit Folie, Manifest und
beobachtbarem Befund. Die vorhandene Arbeitsheftrubrik bleibt die einzige
Bewertung mit achtmal 0–2, insgesamt höchstens 16 Punkten. Transfer ist
unbewertet. Die Transferfolie verlangt Suchentscheidung, Quellenkonflikt und
Abgrenzung einer manipulierten Zusatzanweisung statt eines unbehandelten
Indexentwurfs. Auf Quellfolie 41 wird allein in der STANDARD-Ableitung die
zu lange Beschriftung „Vor dem Request“ zu „Vor Anfrage“ gekürzt; die übrigen
Inhalte bleiben erhalten. BASIS und vollständiger Materialvorrat werden nicht exportiert.

Der redaktionelle Durchgang prüfte Auswahl, Reihenfolge, Aufgaben, Resultate,
Pausen, Lösungsverweise und Ausfallverfahren. Vier besprochene RAG-Fälle und
zehn tatsächlich ausgeführte Bewertungen bleiben getrennt. Modellmetadaten-
EXECUTE wird nicht als erfolgreiche Inferenz beschrieben. Die feste
Injectionfixture belegt keine Sicherheit eines unbekannten Live-Modells.
Die unveränderte erste Vektorquery und ihr tatsächlicher Lauf sind durch die
[BASIS-Generalprobe](SQL_SERVER_2025_AI_BASIS_REHEARSAL.md) belegt; sie wurden
hier nicht erneut als neue Ausführung ausgegeben.

Die zusätzlichen Fachfolien wurden am 18. Oktober gegen Microsoft Learn geprüft:
[VECTOR_DISTANCE](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-distance-transact-sql?view=sql-server-ver17),
[AI_GENERATE_CHUNKS](https://learn.microsoft.com/en-us/sql/t-sql/functions/ai-generate-chunks-transact-sql?view=sql-server-ver17)
und [CREATE EXTERNAL MODEL, Rechte](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-model-transact-sql?view=sql-server-ver17#permissions).
Negative Dot-Distanz, Zeichen-/Overlapmechanik und getrennte Modellrechte
stimmen mit dem begrenzten Unterrichtspfad überein. Bestehende Quellenbindungen
in den Notizen bleiben erhalten; es wird kein neuer Live- oder ONNX-Pfad freigegeben.

## Tatsächliche technische Durchführung

Ein neu erzeugter eigener Linux-/Docker-Container mit dem lokal vorhandenen
Image `mcr.microsoft.com/mssql/server:2025-CU9-ubuntu-24.04` wurde auf vier CPUs
und acht GiB begrenzt. Tatsächlich gemessen: SQL Server 17.0.5005.3, Major 17,
master CL 170. Keine Ports oder Hostverzeichnisse wurden veröffentlicht.
Das zufällige Kennwort blieb ausschließlich in Prozessumgebungen.

Die unveränderten öffentlichen FWK-010-/FWK-011-Lifecycles wurden je zweimal
vollständig ausgeführt. Unabhängige neue master-Abfragen bestätigten die
eigene DB-Abwesenheit vor und nach jedem Lauf.

| Demo | Lauf 1 | Lauf 2 | Ergebnisprüfungen je Lauf |
|---|---|---|---:|
| QRY-014 | PASS / OK | PASS / OK | 3 |
| QRY-015 | PASS / OK | PASS / OK | 3 |
| QRY-016 | PASS / OK | PASS / OK | 3 |
| QRY-017 | WARN / WARN_OPTIONAL_EVIDENCE_SKIPPED | WARN / WARN_OPTIONAL_EVIDENCE_SKIPPED | 3 |
| QRY-018 | PASS / OK | PASS / OK | 4 |
| QRY-019 | PASS / OK | PASS / OK | 5 |
| DGN-008 | PASS / OK | PASS / OK | 9 |
| DGN-009 | PASS / OK | PASS / OK | 8 |

Alle 76 Ergebnisassertionen waren erfüllt. QRY-017 prüfte zusätzlich den
tatsächlichen Full-Text-Voraussetzungswert: nicht installiert, daher korrekt
WARN. Die optionale Full-Text-Ausführung ist nicht qualifiziert; der Kurs
dokumentiert diesen Modus. Gesamtstatus der technischen SQL-Probe bleibt WARN.
Es gab keine Installation und keinen Retry, um daraus einen PASS zu machen.

Nach den 16 Lifecycles war auf der eigenen Instanz keine Benutzerdatenbank
vorhanden. CID, Name und beide Eigentumslabels wurden vor dem Entfernen des
eigenen Containers einschließlich anonymer Volumes exakt geprüft. Ein neues
Inspect bestätigte seine Abwesenheit. Der gesamte technische Durchlauf dauerte
212,937 Sekunden einschließlich Start und Abbau; dies ist keine Lehrzeit.
Es gab einen Containerdurchlauf und keine neue Modell-/Providerinferenz.
Die unveränderten historischen Versions-/Markerqualifikationen werden nicht
als hier erneut durchgeführt bezeichnet; es handelt sich um eine Kursprobe.

## Präsentation und statische Prüfungen

Alle zusätzlichen Quellfolien wurden einzeln in der vorhandenen Darstellung
geprüft. Die bereits geprüften unveränderten BASIS-Quellfolien wurden als
Vorlage weiterverwendet. Artifact Tool und PowerPoint 16.0 renderten alle
45 finalen Folien. Alle 45 PowerPoint-Bilder wurden einzeln bei voller Größe
visuell geprüft; Inhalt, Lesbarkeit, Fußzeilen und die beiden Anpassungen passen.
Die native Datei enthält 15 Tabellen und 45 Sprechernotizen. In einer privaten
Testkopie blieben Änderungen an Text, Tabellenzelle und Notiz nach Speichern
und erneutem Öffnen erhalten. Die veröffentlichte Datei blieb dabei unverändert.

Kursvalidatoren für BASIS und STANDARD vergleichen native Inhalte mit dem
Master einschließlich ausdrücklich definierter Anpassungen. Sie prüfen
Auswahl, Quellenbindung, Notizen und neutralisierte Metadaten. Vier neue
Gegenfalltests decken Zeitlücken, Unterricht in Pausen, fehlende Praxis,
Reihenfolgendrift, Masterdrift sowie tatsächlich manipulierte native
Folieninhalte und Fußzeilen ab. Die vier bestehenden BASIS-Gegenfalltests
und drei Pakettests sichern die gemeinsam betroffene Implementierung ab.
Ein anfänglicher STANDARD-Validatorfehler an der bisher fest auf Quellfolie 61
begrenzten Anpassungsprüfung wurde auf den tatsächlichen Quellfolientitel
korrigiert. Der aktuelle STANDARD- und BASIS-Validator bestanden.

Der gesamte Git-Publikationsbestand bestand den unveränderten Privacy-Scanner:
1187 Dateien, 1168 Textdateien, vier Officepakete und ein unverändert
freigegebenes Artefakt. Die Auswahl umfasst alle versionierten und neuen
nicht ignorierten Dateien. Bereits ignorierte private Altarchive bleiben
außerhalb dieses Bestands; der bekannte lokale Scannerabbruch daran ist im
BASIS-Nachweis dokumentiert. Die vollständige normale CI-Prüfung des frischen
Checkouts bleibt erforderlich.

## Aufwand und offene Teilnehmererprobung

Ein Verantwortlicher bearbeitet genau einen Tageskurs; keine zusätzlichen
Agenten oder Reviewketten. Der bestehende Kurs-CI-Job wird um STANDARD ergänzt,
statt einen zweiten Job mit doppeltem Pakettest anzulegen. Fünf kleine
Standardbibliotheksaufrufe prüfen beide Validatoren, beide Gegenfallsuiten
und einmal die Pakettests. Auslöser bleiben Kursquellen, betroffene PPTX,
Leitfäden und eigene Prüfdateien; der äußere Timeout bleibt fünf Minuten.
Der zentrale Privacy-Scan bleibt der gemeinsame vorhandene Workflow. Es
werden keine Folien oder SQL-Container in diesem Kursjob gebaut. Die einmalige
lokale SQL-Probe ist durch die neue vollständige Kursauswahl begründet;
unveränderte Versions-/Provider-/Markermatrizen werden nicht wiederholt.
Modell-/Tokenverbrauch ist nicht verlässlich gemessen und bleibt unbekannt.

Der tatsächliche Teilnehmerpilot bleibt offen: Verständlichkeit, Lernerfolg
und 420 Lehrminuten müssen mit Lehrperson und Gruppe erprobt werden.
Der Leitfaden enthält Soll-/Ist-Protokoll, Beobachtungsbogen und sicheren
Ausfallpfad. Wiederaufnahmebedingung ist eine reale moderierte Durchführung;
hierfür bleibt kein angefangener Codebranch offen. VERTIEFUNG, Live-Provider,
Cloud, ANN-/Performancequalifikation und volle TSK-012-/TSK-014-/Streamfreigabe
bleiben getrennt offen. Dieser Auftrag aktiviert keine Automation.
