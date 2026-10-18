# BASIS Kurs und Generalprobe

Stand: 18. Oktober 2026. Der beauftragte BASIS-Schnitt ist als eigenständiger
Vierstundenkurs vorbereitet. Die technische und redaktionelle Generalprobe
ist bestanden. Dies ist der begrenzte BASIS-Teil von TSK-012/TSK-014, keine
Gesamtabnahme des KI-Streams oder gemessene Teilnehmererprobung.

## Geprüftes Kurspaket

Der [Kursleitfaden](../HowTo/SQL_SERVER_2025_AI_BASIS_COURSE.md) verbindet
39 ausgewählte Folien mit 210 geplanten Lehr- und 30 Pausenminuten,
zwei praktischen Aufgaben, einer RAG-Leseaufgabe, Transfer, Beobachtungsbogen
und Ausfall-/Cleanupverfahren. Der
[reproduzierbare BASIS-Export](../../Presentations/AI_SQL_Server_2025/basis.course.json)
verwendet die vorhandene Masterquelle. Das vollständige 61-Folien-Deck wurde
nicht verändert. Die letzte Transferfolie ist für den tatsächlich behandelten
BASIS-Stoff konkretisiert. Bestehende Lösungen und Rubrik bleiben allein im Arbeitsheft.

Geprüfte BASIS-PPTX, SHA256:
`159e3ab60547cd7ba6f9b2cd8fb67dc87dbffdb339287e2bc240af2a8237f265`.
Die Foliengrundlage trägt weiterhin ihren Materialstand vom 12. Oktober;
Kursauswahl und diese Generalprobe stammen vom 18. Oktober 2026.

## Tatsächliche technische Durchführung

Ein neu erzeugter eigener Linux-Container mit dem lokal vorhandenen Image
`mcr.microsoft.com/mssql/server:2025-CU9-ubuntu-24.04` wurde auf vier CPUs und
acht GiB begrenzt. Tatsächlich gemessen: SQL Server `17.0.5005.3`, Major 17,
master CL 170. Keine Ports oder Hostverzeichnisse wurden veröffentlicht.
Das zufällige Kennwort blieb ausschließlich in Prozessumgebungen.

Die vollständige Einstiegsquery wurde unmittelbar aus der Masterquelle von
Quellfolie 20 entnommen und unverändert ausgeführt. Ergebnis: Ids 1/2/3,
Cosine-Distanzen 0/1/2, PASS. Die beiden Praxisdemos und die technische
Vorbereitung der RAG-Leseaufgabe wurden über den vorhandenen öffentlichen
FWK-010-/FWK-011-Aufrufer je zweimal vollständig ausgeführt:

| Pfad | Lauf 1 | Lauf 2 | Nach jedem Lauf |
|---|---|---|---|
| QRY-014, Praxis | PASS, 3 Ergebnisassertionen | PASS, 3 Ergebnisassertionen | unabhängige DB-Abwesenheit |
| QRY-019, Praxis | PASS, 5 Ergebnisassertionen | PASS, 5 Ergebnisassertionen | unabhängige DB-Abwesenheit |
| QRY-018, Lesevorbereitung | PASS, 4 Ergebnisassertionen | PASS, 4 Ergebnisassertionen | unabhängige DB-Abwesenheit |

QRY-019 bestand zusätzlich die vorhandenen acht fachlichen Gegenfälle,
80 Eigentumsmarkerabweichungen, Setupidempotenz und abschließenden Cleanup.
Am Ende war auf der eigenen Instanz keine Benutzerdatenbank mehr vorhanden.
Der exakte eigene Container wurde nach CID-/Namens-/Ownerprüfung einschließlich
anonymer Volumes entfernt; unabhängiges Inspect bestätigte seine Abwesenheit.
Es gab einen Containerdurchlauf und keinen Retry bis zu einem günstigen Ergebnis.
Der gesamte technische Durchlauf einschließlich Start, Gegenfällen und Abbau
dauerte 255,237 Sekunden. Das ist eine Werkzeuglaufzeit, keine Unterrichtszeit.

## Präsentation und redaktioneller Durchgang

Alle ausgewählten Quellfolien wurden gerendert und einzeln geprüft. Die finale
BASIS-Datei wurde mit dem Artifact Tool und mit PowerPoint 16.0 vollständig
gerendert; alle 39 finalen PowerPoint-Bilder wurden einzeln visuell geprüft.
Folienformat, Farben und native Inhalte der ausgewählten Masterfolien sind
erhalten; Titelfolie, BASIS-Fußzeilen und begrenzte Transferaufgabe sind angepasst.
Der Validator vergleicht die tatsächlichen nativen Folieninhalte mit dem Master,
prüft Reihenfolge, Quellenbindung, Sprechernotizen und neutralisierte Metadaten.

PowerPoint 16.0 öffnete die Datei mit 39 Folien, 15 nativen Tabellen und
39 Sprechernotizen. In einer privaten Testkopie wurden Text, Tabellenzelle und
Notiz geändert, gespeichert und erneut geöffnet. Alle drei Änderungen blieben
erhalten. Die veröffentlichte Datei wurde durch diese Testbearbeitung nicht verändert.

Der Ablauf wurde gegen Folien, Aufgaben, tatsächliche Ergebnisverträge und
Moderationshinweise durchgegangen. Dabei wurden drei Verwechslungen beseitigt:
vier besprochene RAG-Fälle sind nicht die zehn ausgeführten Bewertungen;
zwei BASIS-Aufgaben sind nicht die Acht-Aufgaben-Gesamtwertung; der BASIS-
Transfer verlangt keine zusätzliche Indexentwurfsaufgabe. Der Ausfallpfad
kennzeichnet eine Ergebnisleseaufgabe ausdrücklich als solche.

Die übernommenen Dimensions-/Previewangaben wurden am 18. Oktober 2026 gegen
Microsoft Learn nachgelesen:
[Vektortyp und float16](https://learn.microsoft.com/en-us/sql/t-sql/data-types/vector-data-type?view=sql-server-ver17),
[VECTOR_SEARCH im SQL-Server-2025-Pfad](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-search-transact-sql?view=sql-server-ver17).
Die Quellenbindung in den bestehenden Masterfolien bleibt erhalten.

## Prüfungen und Aufwand

Kursvalidator und vier gezielte Gegenfalltests prüfen die Auswahl der 39 Folien,
Masterdrift, falsche Praxis-/Lesezuordnung, Zeitsprünge und Pausen. Die drei
bestehenden Pakettests prüfen weiterhin PowerPoint-Datumsmetadaten. Der neue
CI-Job führt genau diese drei Standardbibliotheks-Aufrufe bei Änderungen an
Kursdefinition, Masterquelle, PPTX, Lehrpfad oder eigenen Checks aus. Sein
äußerer Timeout beträgt fünf Minuten. Er baut keine Folien und startet weder
SQL-Container noch Modelle. Der zentrale Privacy-Scan bleibt der vorhandene
gemeinsame Pfad; eine zusätzliche identische Privacy-Suite wird nicht angelegt.

Die einmalige lokale SQL-Generalprobe war durch den neuen Kursauftrag begründet.
Die SQL-Demos und ihre Runtimewerkzeuge wurden nicht geändert; unveränderte
Gesamtmatrizen des KI-Streams werden für diese Materialwelle nicht erneut gestartet.
Ein Implementierungsverantwortlicher, keine zusätzlichen Agenten oder Reviewketten.
PR-/Main-Checks und die vollständige Übernahme werden beim Integrationsabschluss bestätigt.

Der gesamte Git-Publikationsbestand bestand die Prüfung mit dem unveränderten
Privacy-Scanner: 1181 Dateien, 1163 Textdateien, drei Officepakete und ein
unverändert freigegebenes Artefakt. Ein ungefilterter lokaler Working-Tree-Scan
war zuvor an einer URL-Form in einem bereits ignorierten Archiv einer früheren
Welle abgebrochen. Dieses Archiv wurde nicht verändert. Die Prüfung des
Publikationsbestands enthält alle versionierten und neuen nicht ignorierten
Dateien und lässt die normale vollständige CI-Prüfung des frischen Checkouts bestehen.

## Freigabegrenze und Teilnehmerpilot

Der Kurs ist als technisch und redaktionell geprobtes BASIS-Paket bereit für
die erste moderierte Durchführung. Eine Teilnehmergruppe war an dieser
Generalprobe nicht beteiligt. Verständlichkeit, Lernerfolg und die geplanten
210 Lehrminuten sind deshalb weiterhin mit einer realen Gruppe zu erproben.
Der Kursleitfaden enthält dafür den Beobachtungsbogen und die Soll-/Ist-Trennung.
Wiederaufnahmebedingung dieses Human-Nachweises ist eine tatsächliche
Durchführung mit Lehrperson und Gruppe; dafür bleibt kein angefangener Codebranch offen.
STANDARD/VERTIEFUNG, Liveprovider, ANN-/Performance-Gesamtabnahme und die
volle TSK-012-/TSK-014-/Workstreamfreigabe werden durch diesen Schnitt nicht geschlossen.
