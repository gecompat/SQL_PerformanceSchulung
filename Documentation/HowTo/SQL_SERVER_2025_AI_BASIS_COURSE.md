# KI mit SQL Server 2025 BASIS

Dieser Vierstundenkurs führt von einer vertrauten SELECT-Abfrage zu Vektoren,
sicher gebundenen SQL-Werten und belegbaren Antworten. Die Teilnehmenden
brauchen SELECT- und ORDER-BY-Grundkenntnisse, aber keine KI-Erfahrung.
Die Lehrperson verwendet die [BASIS-Präsentation](../../Presentations/SQL_Server_2025_KI_BASIS.pptx)
mit 39 Folien und den folgenden Ablauf. Die Folien stammen aus der bestehenden
Masterquelle; der vollständige Foliensatz bleibt als Vertiefungsmaterial erhalten.

Am Ende können Teilnehmende den Vektortyp vom Modellraum unterscheiden,
Wertbindung und SQL-Struktur getrennt erklären und eine Antwort an ihrer
zugelassenen Quelle prüfen. Ein Cloudkonto oder Modellservice ist für diesen
Kurs nicht erforderlich. Die Beispiele verwenden synthetische Daten und feste
Antwortfixtures, keine Livegeneration.

## Vorbereitung vor dem Kurstag

Die Lehrperson stellt eine eigene SQL-2025-Testinstanz mit CL 170 und einen
getesteten Client bereit. Engine, Client und Datenbankeinstellung werden
getrennt geprüft. Für den tatsächlich erprobten Linux-/Dockerpfad, Rechte,
Authentifizierung und Recovery gelten der [Ausführungsleitfaden](DEMO_EXECUTION_GUIDE.md)
und die READMEs von [QRY-014](../../Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/README.md)
und [QRY-019](../../Demos/09_AI_SQL_Server_2025/QRY-019_SQL_Input_Policy/README.md).
Setup und Cleanup führt die Lehrperson mit dem vorbereiteten Ownerkonto aus.
Die eingeschränkten Rechte im QRY-019-Harness werden nicht als allgemeiner
Teilnehmerzugang ausgegeben. Die SQL-2019-/2022-Pfade ersetzen keine SQL-2025-Durchführung.

Öffnen Sie vor Beginn die Präsentation, dieses Kursblatt und das
[Offline-Arbeitsheft](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md).
Bereiten Sie ausschließlich die Aufgaben QRY-014 und QRY-019 sowie die
QRY-018-Leseaufgabe vor. Lösungen und Rubrik stehen allein im Arbeitsheft.
Prüfen Sie die Verbindung und die Abwesenheit der eigenen Demo-Datenbanken.
Verbindungsaufbau, Installation und Konteneinrichtung liegen vor dem Vierstundenfenster.

Die [Generalprobe](../Project_Planning/SQL_SERVER_2025_AI_BASIS_REHEARSAL.md)
dokumentiert den tatsächlich geprüften Stand. Ein Windows- oder anderer
Editionspfad wird durch einen erfolgreichen Linux-Lauf nicht mitqualifiziert.

## Ablauf mit zwei Pausen

Die Angaben sind Minuten seit Kursbeginn. Insgesamt sind 240 Minuten geplant:
210 Minuten Lehre einschließlich Rückfragen und 30 Minuten Pause. Die
Generalprobe misst SQL-/Werkzeuglaufzeiten getrennt; sie ersetzt keine
mit einer Teilnehmergruppe gemessene Lehrzeit.

| Zeit | BASIS-Folien | Durchführung und sichtbares Ergebnis |
|---|---|---|
| 00–10 | 1–7 | Wissensbasisfall lesen. Erwartete Quelle und Antwort zur bekannten SQL-Frage nennen lassen. |
| 10–25 | 8–13 | KI, Modell, Training, Inferenz und Token an demselben Fall erklären. Teilnehmende ordnen eine Aufgabe einem Modell zu. |
| 25–40 | 14–17 | Engine, Client, CL und Rechte unterscheiden. Bei einem vorbereiteten Fehler den passenden nächsten Schritt nennen lassen. |
| 40–60 | 18–21 | Rangfolge der drei Vektoren vorhersagen, die vollständige read-only Query zeigen und die beobachteten Distanzen besprechen. |
| 60–70 | 22–23 | Handgesetzte Geometrievektoren von echten Textembeddings unterscheiden. Die zusätzlich benötigten Modellvoraussetzungen nennen lassen. |
| 70–85 | 24–27 | Herkunft, Version und erlaubten Antwortkontext am Wissensbasisfall verfolgen. Falsche und fehlende Antworten auseinanderhalten. |
| 85–90 | 28 | Den Ablauf Vorhersage → Beobachtung → Erklärung → Cleanup für die Demos klären. |
| 90–105 | – | Pause. |
| 105–130 | 29–30 | QRY-014 vorführen und die gleichnamige Arbeitsheftaufgabe bearbeiten. Dimension, Basistyp und Modellraum am tatsächlichen Output zeigen lassen. |
| 130–155 | 31–32 | QRY-019 vorführen und die gleichnamige Arbeitsheftaufgabe bearbeiten. Literal-Treffer, abgelehnte Struktur und echte Rechteverweigerung getrennt begründen lassen. |
| 155–175 | 33–34 | QRY-018 als moderierte Leseaufgabe: stützende Quelle, unzulässiges Zitat, fehlender Kontext und widersprüchliche Quellen unterscheiden. |
| 175–190 | – | Pause. |
| 190–210 | 35–38 | Modellzugang, ANN, Messung und SQL-Assistenz einordnen. Je Thema Zweck und zusätzlich benötigten Nachweis nennen lassen. Keine zusätzliche Livevorführung. |
| 210–225 | 39 | Transferfall bearbeiten und die Entscheidung mit Quelle, Zugriffsgrenze und nächstem Prüfschritt begründen. |
| 225–240 | – | Offene Begriffe klären; bei Bedarf dieselbe Aufgabe erneut erklären. |

Die Folienfußzeile nennt zusätzlich die Quellfolie des 61-Folien-Masterdecks.
Die [Kursdefinition](../../Presentations/AI_SQL_Server_2025/basis.course.json)
bindet Auswahl, Reihenfolge und Zeitfenster reproduzierbar.

## Praktische Vorführungen

Die erste Vektorquery auf BASIS-Folie 20 verwendet nur Variablen und SELECT.
Lassen Sie zunächst Id-Reihenfolge und Distanzen vorhersagen. Führen Sie die
vollständige Query aus der Folie in der vorbereiteten CL-170-Labverbindung aus.
Besprechen Sie die tatsächliche Ausgabe vor dem Wechsel zur Ergebnisfolie.
Eine Zahlenliste ist hier ein Geometriebeispiel und kein Nachweis sprachlicher Relevanz.

QRY-014 und QRY-019 werden über die unveränderten Manifeste vollständig
ausgeführt. Die folgende PowerShell-Vorlage wird vom Repository-Stamm aus
verwendet. `$courseServer` und `$courseUser` werden vor dem Kurs auf die eigene
vorbereitete Labverbindung gesetzt; SQL-Authentifizierung liest das Kennwort
ausschließlich aus `SQLCMDPASSWORD`. Zertifikats- und Authentifizierungswahl
werden vorab gemäß Ausführungsleitfaden eingerichtet.

```powershell
python Demos/00_Framework/Tools/run_demo.py Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/manifest.json --server $courseServer --auth sql --username $courseUser --show-output
if ($LASTEXITCODE -ne 0) { throw 'QRY-014 ist nicht erfolgreich abgeschlossen.' }

python Demos/00_Framework/Tools/run_demo.py Demos/09_AI_SQL_Server_2025/QRY-019_SQL_Input_Policy/manifest.json --server $courseServer --auth sql --username $courseUser --show-output
if ($LASTEXITCODE -ne 0) { throw 'QRY-019 ist nicht erfolgreich abgeschlossen.' }
```

Halten Sie nach jedem Lauf die finale Summary und die unabhängige Abwesenheit
der zugehörigen eigenen Datenbank fest. Für diesen unveränderten LOCAL-Pfad
sind dies `SQLPERF_LAB_QRY014_LOCAL` und `SQLPERF_LAB_QRY019_LOCAL`.
Die Abwesenheit lässt sich aus einer neuen Verbindung zu master lesen:

Nur `PASS|OK` zählt hier als erfolgreiche praktische Durchführung. Ein
Versions-SKIP oder ein Ausfall wird im Beobachtungsbogen als Leseaufgabe
gekennzeichnet. Führen Sie die folgende Abwesenheitsprüfung nach jeder der
beiden Demos aus, nicht erst nach beiden zusammen.

```powershell
sqlcmd -S $courseServer -U $courseUser -d master -b -Q "SET NOCOUNT ON; IF DB_ID(N'SQLPERF_LAB_QRY014_LOCAL') IS NOT NULL OR DB_ID(N'SQLPERF_LAB_QRY019_LOCAL') IS NOT NULL THROW 51004,'FAIL_CLEANUP',1; PRINT 'BASIS_DB_ABSENT';"
if ($LASTEXITCODE -ne 0) { throw 'Cleanup muss geklärt werden.' }
```

Die Lehrperson lässt in QRY-014 die fünf Rows und beide ungültigen Eingaben
zeigen. In QRY-019 liest sie die beiden zugelassenen Werte, die abgelehnten
Strukturen und die tatsächlichen Rechtegegenproben. DDL-Text in einer
Wertfixture wird als Wert besprochen; er ist kein frei auszuführender SQL-Auftrag.
Vor jeder Vorführung kommen erst die Vorhersage und dann der tatsächliche Befund.

## Quellenentscheidungen lesen

Verwenden Sie die vier beschriebenen Fälle der
[QRY-018-Aufgabe](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md#qry-018--antwort-ablehnung-oder-nichtantwort).
Sie sind eine Auswahl zur Besprechung. Der vollständige Demo-Vertrag enthält
zehn Bewertungen: eine akzeptierte Behauptung, sieben abgelehnte und zwei
begründete Nichtantworten. Verwechseln Sie vier Besprechungsfälle nicht mit
vier ausgeführten Bewertungen. Die technische Generalprobe prüft den
vollständigen Vertrag; im BASIS-Kurs wird das Ergebnis moderiert gelesen.
Eine reale generative Modellantwort wird dabei nicht erzeugt.

## Beobachtungsbogen für die Teilnehmenden

Nutzen Sie eine synthetische Kennung statt eines Namens. Die beiden bewerteten
Aufgaben verwenden unverändert die jeweilige Lösung und 0–2-Punkte-Rubrik im
Arbeitsheft. Die ausgewählte Teilmenge hat höchstens vier Punkte; daraus wird
keine Gesamtwertung der acht Offlineaufgaben und keine neue Bestehensgrenze abgeleitet.

| Aufgabe | Meine Vorhersage | Beobachteter Beleg | Erklärung oder Korrektur |
|---|---|---|---|
| QRY-014 | Welcher Unterschied bleibt trotz gleicher Dimension? | Row/Typ und Eingabeabwehr nennen. | Modellraum und zusätzlich benötigte Provenienz erklären. |
| QRY-019 | Was geschieht mit DDL-Text als Wert? | Literal-Treffer, Strukturabwehr und einen Rechtefehler nennen. | Wertbindung und Berechtigung getrennt erklären. |
| QRY-018, unbewertet | Antworten, verwerfen oder nicht antworten? | Erlaubte Quelle und Kontext nennen. | Entscheidung für jeden der vier Besprechungsfälle begründen. |

Transferfrage: Für die Frage nach einer Aufbewahrungsdauer liefern zwei aktuelle
zugelassene Quellen verschiedene Werte. Erklären Sie, welche Herkunft und
Zugriffsprüfung vor einer Antwort nötig sind, wie Sie den Widerspruch zeigen
und welchen fachlichen Klärungsschritt Sie auslösen. Besprechen Sie dies anhand
der vorhandenen QRY-018-Lösung; die Aufgabe führt keine zusätzliche Rubrik ein.

## Wenn eine Vorführung ausfällt

Bei Verbindungs-, Versions- oder Rechtefehlern bleibt die Gruppe bei der
Vorhersage und liest die vorbereitete Ergebnisfolie beziehungsweise das
Arbeitsheft. Markieren Sie den Abschnitt im Beobachtungsbogen ausdrücklich
als Leseaufgabe statt als tatsächlichen Lauf. Installationen, zusätzliche
Grants oder Provideränderungen erfolgen nicht aus dem Kurs heraus.

Bei einem fachlichen FAIL wird der Befund festgehalten. Einen unveränderten
Lauf bis zum gewünschten Ergebnis zu wiederholen ist kein Ersatz für die
Klärung. Bei Abbruch prüft die Lehrperson zuerst den markergebundenen
Cleanup-/Recoverypfad der betroffenen Demo. Bei unklaren Markern wird keine
Datenbank aufgrund ihres Namens gelöscht. Der Abschnitt endet erst mit
geklärter eigener DB-Abwesenheit oder ausdrücklich dokumentiertem Cleanupfehler.

## Abschluss des Kurstags

Die Lehrperson prüft die beiden Erklärungen gemeinsam mit den vorhandenen
Lösungen und sammelt offene Begriffe. Im Trainerprotokoll werden tatsächlicher
Live- oder Lesemodus, Unterbrechungen, Cleanup und Soll-/Ist-Unterrichtszeiten
getrennt erfasst. Verständnis und Zeitbedarf einer Teilnehmergruppe werden
erst durch diese Erprobung belegt. Der technische und redaktionelle
Generalprobenstand ist im verlinkten Nachweis dokumentiert.
