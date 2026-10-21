# KI mit SQL Server 2025 – Teaching Paths für den gemeinsamen Einstieg

Stand: 2026-10-12. TSK-012/CUR-013–CUR-022. Diese Planung bezieht sich auf das
editierbare [61-Folien-Deck](../../Presentations/SQL_Server_2025_KI.pptx).
Alle Zeiten sind Vorschläge für eine spätere Generalprobe, keine gemessenen
Lehrzeiten oder Teilnehmerabnahme. Der [kanonische Workstreamplan](../Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md#5-pfade-und-zeitbedarf)
führt die aktuellen Planfenster; dieser Leitfaden konkretisiert Materialauswahl und Ablauf.

Für BASIS ist seit dem 18. Oktober 2026 das eigenständige
[Kurspaket mit 39 Folien](SQL_SERVER_2025_AI_BASIS_COURSE.md) maßgeblich.
Es enthält den konkreten Ablauf, Durchführung, Ausfallpfad und Beobachtungsbogen.
Die [technische und redaktionelle Generalprobe](../Project_Planning/SQL_SERVER_2025_AI_BASIS_REHEARSAL.md)
ist von einer Teilnehmererprobung und gemessenen Unterrichtszeiten getrennt.
Für STANDARD gilt ebenfalls seit dem 18. Oktober der eigenständige
[Tageskurs mit 45 Folien](SQL_SERVER_2025_AI_STANDARD_COURSE.md) und
[abgeschlossener technischer/redaktioneller Generalprobe](../Project_Planning/SQL_SERVER_2025_AI_STANDARD_REHEARSAL.md).
Der optionale Full-Text-WARN und die offene Teilnehmererprobung bleiben sichtbar.
VERTIEFUNG steht ebenfalls als eigenständiger
[Zweitageskurs mit 61 Kursfolien](SQL_SERVER_2025_AI_VERTIEFUNG_COURSE.md) und
[technischer/redaktioneller Generalprobe](../Project_Planning/SQL_SERVER_2025_AI_VERTIEFUNG_REHEARSAL.md)
bereit. Tag 2 liest begrenzte Belege und bearbeitet Architektur-/Evaluationsentwürfe;
offene Runtimequalifikationen werden dadurch nicht hochgestuft. Die folgenden STANDARD-Nummern
beziehen sich weiterhin auf die Quellfolien des vollständigen Masterdecks;
der Kursleitfaden nennt die zugehörigen STANDARD-Folien.

## Zielgruppe und vorbereiteter Einstieg

Teilnehmende benötigen keine KI-Erfahrung. Einfache SELECT-Abfragen sind der
gemeinsame Ausgangspunkt. Wer SELECT/ORDER BY noch nicht kennt, erhält vor der
Einheit eine eigene SQL-Grundlageneinführung; diese Planung ersetzt sie nicht.
Die Lehrperson klärt dies vorab und stellt eine eigene vorbereitete Labverbindung
bereit. Serverversion, Client, Compatibility Level und Rechte werden ausdrücklich
unterschieden. Teilnehmende benötigen für den Einstieg weder Cloudkonto noch
Modelldownload, Credentialanlage oder Previewkonfiguration.

Die zuerst gezeigten Zahlen sind eine geometrische Zuordnung, keine echten
Sprach-Embeddings. Ohne passend vorbereiteten SQL-2025-Server bespricht die Gruppe
die Ergebnisfolie. Ein Verbindungs-, Versions- oder Rechtefehler führt zur passenden
Leseaufgabe; die Gruppe installiert oder verändert daraus keine Instanz. Die
[Ausführungsanleitung](DEMO_EXECUTION_GUIDE.md) und Demo-READMEs bleiben für spätere
manifestbasierte Läufe maßgeblich. Setup-/Cleanupownerrechte sind keine Teilnehmerrechte.

## Gemeinsamer Einsteigerblock: 90 Minuten Netto als Planwert

Die Foliennummern wurden aus der aktuellen Masterquelle `content.mjs`/`introduction.mjs`
abgeleitet. Die Lehrperson zeigt die Inhalte in dieser Reihenfolge und erklärt die
neuen Wörter vor der jeweiligen Anwendung. Fragen und Ergebnisbesprechung sind enthalten.

| Block | Folien | Planminuten | Aktivität und sichtbarer Lernbeleg |
|---|---|---:|---|
| Vertrauter Fall | 1–7 | 10 | Drei synthetische Quellen und eine bekannte SELECT-Abfrage lesen. Erwartete Quelle und Antwort in eigenen Worten nennen. |
| Neue Begriffe einzeln | 8–13 | 15 | KI (künstliche Intelligenz; Verfahren für Aufgaben wie Textverarbeitung oder Vorhersagen), Modell, Training/Inferenz, Sprachmodell, Token und Datenfluss auseinanderhalten. Eine Aufgabe dem passenden Modell zuordnen. |
| Einstiegshürden | 14–17 | 15 | Engine/Client/CL/Lab/Rechte erklären. Aus einem vorgegebenen Hindernis den nächsten vorbereiteten Lehrschritt wählen. |
| Erster SQL-Versuch | 18–21 | 20 | Erst Rangfolge vorhersagen, dann lokale Variablen/SELECT vorführen oder Ergebnisfolie lesen. Mathematische Nähe erklären und ihre Sprachgrenze benennen. |
| Echter Modellzugang | 22–23 | 10 | Embedding von manueller Zahlenzuordnung unterscheiden. Zusätzliche API-/TLS-/Zugangs-/Datenschutzvoraussetzungen erkennen, ohne einen Provider aufzurufen. |
| Quelle und Antwort | 24–27 | 15 | Herkunft, Version, Retrieval, belegbare Antwort und begründete Nichtantwort am gleichen Fall verfolgen. Eine Antwort ihrer Quelle zuordnen. |
| Übergang | 28 | 5 | Vorhersage–Beobachtung–Besprechung–Cleanup als Ablauf der folgenden Demos beschreiben. |
| **Summe** | | **90** | |

Ein falsches Verständnis wird an derselben synthetischen Quelle besprochen,
bevor zusätzliche Fachbegriffe hinzukommen. Die erste Vektorquery wird nicht
als Sprachrelevanzbeweis oder als neue bewertete Arbeitsheftaufgabe ausgegeben.

## BASIS: geplantes Vierstundenfenster

240 Minuten brutto, davon 210 Nettolehrzeit und 30 Pausenminuten. Dieser Pfad
wählt Material aus dem Deck aus; er verlangt nicht alle 61 Folien in vier Stunden.

| Baustein | Material | Netto-Planminuten |
|---|---|---:|
| Gemeinsamer Einstieg | Folien1–28, obiger Ablauf | 90 |
| Typ/Modellraum vertiefen | Quellfolien34–35, BASIS29–30; QRY-014 und zugehörige Arbeitsheftaufgabe | 25 |
| Parameter und Rechte sehen | Folien47–48, QRY-019 und zugehörige Arbeitsheftaufgabe | 25 |
| Quelle/Antwort und Grenzen | Folien45–46, QRY-018 als moderierte Ergebnisleseaufgabe | 20 |
| Fachthemen einordnen | Quellfolien40/51/54/57, BASIS35–38: Modellzugang, ANN (Approximate Nearest Neighbor; näherungsweise Suche nach ähnlichen Vektoren), Messung und Assistenz | 20 |
| Entscheidung/Transfer | Folie61, einen Fall begründen und nächsten Nachweis nennen | 15 |
| Rückfragen/Reserve | Hindernisse klären und offene Fragen festhalten | 15 |
| **Summe Netto** | | **210** |

Nur die ausgewählten manifestbasierten Vorführungen werden praktisch geplant;
die Übersicht über offene Vertiefungsthemen ist keine zusätzliche Liveabnahme.
Für die zwei bearbeiteten Arbeitsheftaufgaben wird ausschließlich deren vorhandene
Lösung/Rubrik benutzt. Aus einer Teilmenge entsteht keine Gesamtwertung aller acht Aufgaben.

Die separate BASIS-Datei verwendet die Kursreihenfolge einschließlich Security
vor der RAG-Leseaufgabe. Die abschließende Transferfolie ist auf Quellenkonflikt
und begründete Nichtantwort zugeschnitten. Sie verlangt keine zusätzliche
Indexentwurfsaufgabe. Quellfoliennummern im übrigen Dokument beziehen sich auf
das vollständige Masterdeck; die BASIS-Fußzeile zeigt beide Zuordnungen.

## STANDARD: vorbereiteter Unterrichtstag

480 Minuten brutto, davon 420 Nettolehrzeit und 60 Pausenminuten. Der vorbereitete
Tag enthält alle acht Aufgaben des Offlinearbeitshefts. Die genaue Zuordnung und
Moderation stehen im [Trainerleitfaden](SQL_SERVER_2025_AI_OFFLINE_TRAINER_GUIDE.md).
Live-Embeddings sind eine getrennte spätere Erweiterung mit ihren Voraussetzungen.

| Baustein | Material | Netto-Planminuten |
|---|---|---:|
| Gemeinsamer Einstieg | Folien1–28 | 90 |
| Typ/Metrik/Normalisierung | Folien34–37, QRY-014/QRY-015 | 35 |
| Chunk und Version | Folien38–39, QRY-016 | 30 |
| Suche und belegbare Antwort | Folien43–46, QRY-017/QRY-018 | 60 |
| Struktur/Rechte/manipulierte Quelle | Folien47–49, QRY-019/DGN-009 | 60 |
| Modelle und getrennte Rechte | Folien40–42, DGN-008 ohne Modellaufruf | 35 |
| Gemeinsame Ergebnisbesprechung | Rows, Status, Fehlinterpretationen und Cleanupbelege der acht Aufgaben | 40 |
| Entscheidung/Transfer | Folie61 und vorhandene Arbeitsheftrubrik | 20 |
| Rückfragen/Reserve | Individuelle Hindernisse und erneut zu erklärende Begriffe | 50 |
| **Summe Netto** | | **420** |

Bei fehlendem optionalem Full-Text bleibt QRY-017 WARN. Erwartete Ausgaben lesen
ersetzt keine tatsächliche Demoausführung; beides wird im Beobachtungsbogen getrennt.
Es gibt keine zusätzliche Lösungssammlung oder Bewertungsgrenze in diesem Dokument.

## VERTIEFUNG: zwei vorbereitete Unterrichtstage

960 Minuten brutto, davon 840 Nettolehrzeit und 120 Pausenminuten. Tag1 ist der
vollständige STANDARD-Pfad. Tag2 verbindet die Fachfolien mit getrennten vorliegenden
Records, begrenzten qualifizierten Profilen und offen bezeichneten Demoentwürfen.
Eine Recordleseaufgabe benötigt keinen erneuten unveränderten SQL-Qualifikationslauf.
Die folgende Tabelle nennt Quellfolien; der eigenständige VERTIEFUNG-Leitfaden
enthält Kursfoliennummern, alle Zeitblöcke und die konkreten Arbeitsheftaufgaben.

| Tag2-Baustein | Material | Netto-Planminuten |
|---|---|---:|
| Rekapitulation | Quelle, Modellraum, Antwortbeleg und eigene Rechte erklären | 15 |
| ANN und Lifecycle | Folien51–53, IDX-011/IDX-012: vorhandene begrenzte Belege lesen; offene volle Abnahme benennen | 60 |
| Messgrenzen und Kosten | Folien54–55, RES-008-Ergebnisleseaufgabe aus dem Arbeitsheft | 60 |
| Modellpfade und Provenienz | Folien40–42, QRY-020/021/022 als getrennte Architektur-/Voraussetzungsaufgaben | 75 |
| SQL-Assistenz | Folien57–59, DGN-010: Vorschlag, Originalplan, DML-/Buildkosten und offene Nettonutzenfrage trennen | 45 |
| Betrieb/Tenant/Diagnose | Folien50/56, CON-010/RES-009/DGN-011: begrenzte Kontrollen gegenüber offenem Pooling/End-to-End einordnen | 45 |
| Angriff und Evaluation | Folien49/60: vorhandene feste Quelle/Policy lesen, weitere Modell-/Toolgrenzen als Entwurf bearbeiten | 60 |
| Entscheidung/Transfer | Folie61: Empfehlung mit Voraussetzungen, Gegenbeleg und nächstem Prüfauftrag begründen | 30 |
| Rückfragen/Reserve | Offene Begriffe und getrennte Gates klären | 30 |
| **Summe Tag2 Netto** | | **420** |

Alle 18 registrierten Demoentwürfe bleiben im [Demokatalog](../Demo_Catalog/SQL_SERVER_2025_AI_DEMO_DESIGNS.md)
mit ihrem tatsächlichen Status. Neun IMPLEMENTED/neun PROPOSED sind kein Versprechen,
18 ausführbare und vollständig abgenommene Liveversuche anzubieten. Cloud-/Bezahl-
APIs, ONNX (Open Neural Network Exchange; Austauschformat für Modelle)/rote Hoständerungen und andere offenen Grenzen benötigen weiterhin
ihre konkrete Freigabe; die didaktische Auswahl erteilt keine neue Ausführungsautorität.

## Erprobung und getrennte Nachweise

Ersteinrichtung und Modelldownloads finden außerhalb der Lehrfenster statt. Die
frühere Schätzung von60–120 Minuten ist keine Installations- oder Hardwaregarantie.
Die Lehrperson prüft die eigene Labvorbereitung vor der Einladung zur praktischen Einheit.

Für eine spätere Generalprobe werden je Baustein geplante und tatsächliche Minuten,
erklärte Begriffe, bearbeitete Aufgabe, konkrete Ergebnis-/Cleanupbelege und offene
Verständnisfragen getrennt erfasst. Nur synthetische Teilnehmerkennungen verwenden;
keine Namen, fremden SQL-Texte, Sourcepayloads oder echten Systemdaten sammeln.
Abweichungen verkürzen nicht stillschweigend den Einstieg und erzeugen keine
ungeprüften Installation-/Provider-/Recovery-Schritte während des Unterrichts.

TSK-014 bestätigt anschließend tatsächliche Lehrdauer, Verständlichkeit, Pfadabdeckung
und Generalprobe. Diese Planung schließt TSK-012 oder TSK-014 nicht allein ab.
Der vorhandene [Beobachtungsbogen und die einzige Rubrik](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md)
bleiben maßgeblich; keine neue Bestehensgrenze oder gemessene Lernwirksamkeit.
