# KI mit SQL Server 2025 VERTIEFUNG

Dieser Zweitageskurs verbindet den vollständigen Offline-Praxistag mit einem
zweiten Tag zu ANN (Approximate Nearest Neighbor; näherungsweise Suche nach ähnlichen Vektoren), Kosten, Modellarchitektur, SQL-Assistenz und Betrieb.
Die [eigenständige VERTIEFUNG-Präsentation](../../Presentations/SQL_Server_2025_KI_VERTIEFUNG.pptx)
enthält 61 Kursfolien aus 56 Quellfolien; fünf Fachfolien werden an Tag 2
gezielt wiederholt. Sie benötigt keine zweite Präsentationsdatei.
Die ersten 45 Folien entsprechen dem STANDARD-Inhalt mit VERTIEFUNG-Kennzeichnung.

Zielgruppe sind Teilnehmende mit SELECT-/ORDER-BY-Grundkenntnissen, die den
Mechanismus einer beobachteten SQL-Ausgabe erklären und anschließend eine
begründete Architektur- oder Messentscheidung treffen wollen. KI-Erfahrung
ist nicht Voraussetzung: Tag 1 enthält den vollständigen gemeinsamen Einstieg.
Eine vorherige BASIS-/STANDARD-Teilnahme ist daher nicht erforderlich.

Am Ende können Teilnehmende eine Suchentscheidung an Modellraum, erlaubten
Kandidaten und Quellenqualität prüfen, begrenzte Mess-/Rechtebelege einordnen
und einen fehlenden Nachweis mit Scope, Abbruch und Cleanup konkret benennen.
Tag 1 verwendet acht ausführbare Offline-Demos. Tag 2 verwendet Beleglesen,
eine synthetische Recallrechnung, die vorhandene RES-008-Leseaufgabe und
Architektur-/Evaluationsentwürfe. Live-Modelle, neue ANN-/Poolingversuche,
Cloud und ONNX (Open Neural Network Exchange; Austauschformat für Modelle) werden dabei nicht ausgeführt.

## Vorbereitung vor den Kurstagen

Für Tag 1 gelten die [STANDARD-Vorbereitung und praktischen Aufrufe](SQL_SERVER_2025_AI_STANDARD_COURSE.md#vorbereitung-vor-dem-kurstag):
eigene vorbereitete SQL-2025-Testinstanz mit CL 170, getesteter Client,
Owner für Setup/Cleanup, SQLCMDPASSWORD bei SQL-Authentifizierung sowie
vier vollständige Eigentumsmarker. Rechte der eingeschränkten Demoidentitäten
sind keine allgemeinen Teilnehmerrechte. Installation und Verbindungsaufbau
liegen außerhalb des Lehrfensters. Die aktuellen Ergebnis-/Cleanupverträge
der Demo-READMEs und der [Ausführungsleitfaden](DEMO_EXECUTION_GUIDE.md) bleiben verbindlich.

Öffnen Sie vor beiden Tagen Präsentation, diesen Ablauf und das
[Offline-Arbeitsheft](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md). Lösungen und Rubrik
bleiben ausschließlich dort gepflegt. Für Tag 2 stellen Sie die verlinkten
öffentlichen Zusammenfassungen bereit. Die Gruppe benötigt hierfür weder
SQL Server noch Providerkonto oder Modellservice. Keine privaten Rawrecords,
Prompts, Vektoren, Verbindungsidentitäten oder Secrets werden ausgegeben.
Die frühere Ausführungsautorität eines historischen Reports wird nicht übernommen.

Die [technische Generalprobe](../Project_Planning/SQL_SERVER_2025_AI_VERTIEFUNG_REHEARSAL.md)
trennt die tatsächlichen Tag-1-Läufe, die reine Tag-2-Material-/Rechenprüfung
und die offene Teilnehmererprobung. Zeitfenster sind Planwerte, keine gemessene
Lehrdauer. Linux-/Docker-Belege qualifizieren keine anderen Editionen oder Windows.

## Zeitfenster und Folien

Jeder Tag umfasst 480 Minuten: 420 Minuten Lehre einschließlich Rückfragen
und 60 Minuten Pause. Zusammen sind das 960 Kursminuten mit 840 Lehr- und
120 Pausenminuten. Die Nacht zwischen den Tagen gehört nicht zu dieser Rechnung.
Die folgenden Zeiten beginnen an jedem Tag bei null; die maschinenlesbare
[Kursdefinition](../../Presentations/AI_SQL_Server_2025/vertiefung.course.json)
führt die kumulierten Kursminuten. Die Fußzeile nennt Kurs- und Quellfolie.

### Tag 1 vollständiger Offline-Praxistag

Tag 1 folgt vollständig dem [STANDARD-Ablauf](SQL_SERVER_2025_AI_STANDARD_COURSE.md#tagesablauf-mit-drei-pausen).
Die Kursfolien 1–45 besitzen dieselbe inhaltliche Zuordnung, Reihenfolge und
Transferaufgabe. Es wird der volle Ablauf durchgeführt, keine gekürzte Wiederholung.

| Zeit | VERTIEFUNG-Folien | Durchführung |
|---|---|---|
| 00–90 | 1–28 | Gemeinsamer Einstieg mit Wissensbasis, Begriffen, Voraussetzungen, Vektorquery und Quellenantwort. |
| 90–105 | – | Pause. |
| 105–170 | 29–34 | QRY-014/QRY-015 sowie QRY-016 und zugehörige Aufgaben. |
| 170–230 | 35–38 | QRY-017/QRY-018 mit Suchvergleich und begründeten Quellenentscheidungen. |
| 230–260 | – | Mittagspause. |
| 260–355 | 39–44 | QRY-019, DGN-008 und DGN-009: Wertbindung, Modellrechte und manipulierte Quelle. |
| 355–370 | – | Pause. |
| 370–410 | bisherige Fachfolien | Alle acht Aufgaben und Ergebnis-/Cleanupbelege gemeinsam besprechen. |
| 410–430 | 45 | STANDARD-Transfer mit Suchfrage, Quellenkonflikt und unzulässiger Zusatzaktion. |
| 430–480 | nach Bedarf | Rückfragen, Wiederholung und individuelle Hindernisse. |

Die Lehrperson führt die acht Manifeste einzeln gemäß STANDARD-Leitfaden aus,
liest die tatsächliche finale Summary und prüft nach **jedem** Lauf aus einer
neuen master-Verbindung die eigene DB-Abwesenheit. QRY-017 darf bei nachweislich
fehlendem Full-Text den dokumentierten optionalen WARN behalten. SKIP/FAIL und
ein gelesener Sollwert gelten nicht als erfolgreicher praktischer Lauf.

### Tag 2 Evidenz und begrenzte Entscheidungen

| Zeit | VERTIEFUNG-Folien | Aufgabe und sichtbarer Lernbeleg |
|---|---|---|
| 00–15 | Rückblick auf 45 | Eine Quelle, einen Modellraum, einen Antwortbeleg und die eigene Rechtefrage erklären. |
| 15–75 | 46–48 | ANN-Recall rechnen, V2-/DML-/Rollenbefund lesen und nächsten begrenzten Nachweis formulieren. |
| 75–90 | – | Pause. |
| 90–150 | 49–50 | RES-008-Aufgabe: Population, Einheiten, Gegenrichtungen, AA/Nullen/Ausreißer und Qualitätsgrenze. |
| 150–225 | 51–53 | Vier Modellarchitekturen mit Transport, Daten, Provenienz, Credentials und endlichem Budget vergleichen. |
| 225–255 | – | Mittagspause. |
| 255–300 | 54–56 | SQL-Assistenz: vorhandenen Planbeleg von Nettonutzen trennen und widerlegbaren Messauftrag abgeben. |
| 300–345 | 57–58 | EXECUTE AS, frische Anmeldung und Poolreuse unterscheiden; End-to-End-Diagnoseplan formulieren. |
| 345–360 | – | Pause. |
| 360–420 | 59–60 | Vier Evaluationsfälle für Quelle, Antwort, Toolpolicy und Rechte vorab festlegen. |
| 420–450 | 61 | Empfehlung mit Gegenbeleg und konkretem Prüf-/Abbruch-/Cleanupauftrag vorstellen. |
| 450–480 | nach Bedarf | Offene Begriffe, Gegenfragen und Rückblick. |

## Moderation der Tag 2 Aufgaben

Die vollständigen Aufgaben und die einzigen Musterlösungen stehen im
[Arbeitsheftabschnitt VERTIEFUNG Tag 2](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md#vertiefung-tag-2-aufgaben).
Die Lehrperson gibt zuerst Aufgabe und Quellen aus, danach die vorhandene Lösung.
Das gemeinsame Muster bleibt Vorhersage → Beleg → Erklärung → offene Grenze.

Für ANN sind zehn Minuten Beleglesen, zwanzig Minuten Recall-/Populationsarbeit,
fünfzehn Minuten DML-/Rollenvergleich und fünfzehn Minuten Prüfauftrag vorgesehen.
Die k=5-Listen sind eine ausdrücklich synthetische Rechenfixture, kein neuer
ANN-Messlauf. Der V2-Record bleibt ein begrenzter kohärenter Record mit WARN und
unbekannter Generation; ein beobachteter lokaler DML-Fehler ist keine allgemeine
Regel für neue Indexgenerationen oder andere Plattformen.

Die Kostenstunde verwendet vier gleich lange Abschnitte: Populationsrechnung,
Messbereiche/Einheiten, konkrete Gegenrichtungen und Grenzen der Empfehlung.
Die vorhandenen sechs Batchfenster je A/B-Pfad werden nicht zu individuellen
Query-p99-Werten umgedeutet. Modellqualität benötigt einen eigenen fachlichen
Beleg; höhere Dimension und mehr Bytes beweisen sie nicht.

Die Modellarchitektur erhält zehn Minuten Begriffsprüfung, fünfunddreißig
Minuten Arbeit an vier Pfaden, fünfzehn Minuten Gegenprüfung und fünfzehn
Minuten Ausfall-/Budgetdiskussion. Die Gruppe nennt Voraussetzungen, führt
aber weder WhatIf noch Inferenz aus. Der synthetische Offlinepfad bleibt die
Ausweichmöglichkeit; Cloud und Hoständerungen sind kein automatischer Fallback.

Bei SQL-Assistenz verteilen sich die 45 Minuten auf zehn Minuten Beleglesen,
fünfzehn Minuten Befund-/Lückentabelle und je zehn Minuten Hypothese und
Gegenfrage. Ein vorhandener Reader-Seek begründet keinen allgemeinen Speedup.
Die Lehrperson verlangt gleiche Workloadpopulation und passend getrennte
Lese-/DML-/Build-/Storagekosten, bevor Nettonutzen behauptet wird.

Für Betrieb/Tenant sind jeweils fünfzehn Minuten Verbindungskontext,
Diagnoseplan und sichere Beendigung vorgesehen. Verwechseln Sie den
EXECUTE-AS-Nachweis der öffentlichen Demo nicht mit neuer Authentifizierung
oder Poolreuse. Ein Containerabbau ersetzt weder SQL-Abwesenheit noch den
Nachweis eines bekannten Clientendes.

Die Evaluationsstunde verwendet fünfzehn Minuten Rückblick auf DGN-009,
fünfundzwanzig Minuten Vier-Fälle-Tabelle und zwanzig Minuten Gegenprüfung.
Eine Behauptung aus einem Quellenabsatz erteilt keine Toolbefugnis. Die
Schlussaufgabe erhält fünfzehn Minuten Empfehlung, zehn Minuten Gegenfragen
und fünf Minuten für den nächsten konkreten Prüfauftrag.

## Bewertung Beobachtung und Ausfall

Tag 1 verwendet unverändert die acht vorhandenen 0–2-Punkte-Rubriken, zusammen
höchstens 16 Punkte. Tag 2 einschließlich RES-008 und Transfer bleibt unbewertet.
Die Gruppe nutzt denselben Beobachtungsbogen mit Zweck, Erwartung, konkretem
Beleg und offener Grenze; die Lehrperson prüft die Erklärung an den Musterlösungen.
Es entsteht keine neue Bestehensschwelle oder Kompetenzzertifizierung.

An Tag 1 gelten STANDARD-Ausfallmodus und markergebundene Recovery. Der Lauf
ist erst mit geklärter eigener DB-Abwesenheit oder dokumentiertem Cleanupfehler
geschlossen. Keine Wiederholung bis PASS und keine Löschung anhand eines Namens.
An Tag 2 wird bei nicht verfügbarem oder geändertem Beleg auf das bereitgestellte
Arbeitsheft und den benannten historischen Scope zurückgegriffen. Fehlende oder
abweichende Evidenz wird vermerkt; sie löst keine neue Runtime aus.

Je Block protokolliert die Lehrperson Soll-/Ist-Minuten, praktische Ausführung
oder Beleglesen, konkrete Erklärung, offene Frage und etwaige Abweichung.
Verwenden Sie synthetische Teilnehmerkennungen und keine Namen oder Daten
fremder Systeme. Reale Verständlichkeit, Lernerfolg und die geplanten Lehrzeiten
werden erst mit einer tatsächlichen Gruppe erprobt. Die technische Generalprobe
und die offene Teilnehmererprobung bleiben getrennte Nachweise.
