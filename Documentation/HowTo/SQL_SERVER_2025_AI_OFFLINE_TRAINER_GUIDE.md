# KI mit SQL Server 2025 – Trainerleitfaden für den Offlinepfad

Für die Durchführung des vierstündigen BASIS-Kurses verwenden Sie den
[BASIS-Kursleitfaden](SQL_SERVER_2025_AI_BASIS_COURSE.md) und die separate
39-Folien-Präsentation. Er wählt QRY-014/QRY-019 praktisch und QRY-018 als
Leseaufgabe aus diesem Materialvorrat aus. Der nachfolgende vollständige
Offlinepfad bleibt der weiterführende STANDARD-Entwurf. Der
[Generalprobenachweis](../Project_Planning/SQL_SERVER_2025_AI_BASIS_REHEARSAL.md)
benennt die tatsächlich geprüften Abläufe und den getrennten Teilnehmerpilot.

Stand: 2026-10-12. TSK-012, didaktischer Teilentwurf für acht implementierte Demos
plus getrennte RES-008-Ergebnisleseaufgabe und drei optionale lokale
Evidenzleseaufgaben. Alle Lösungen bleiben ausschließlich im Arbeitsheft.
Reihenfolge und Moderation sind Vorschläge; Teilnehmererprobung, Lehrzeiten und
Gesamtcurriculumabnahme stehen aus. Die Trainerlösungen und die Bewertungsrubrik
werden ausschließlich im [Arbeitsheft](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md)
gepflegt. Dieser Leitfaden ergänzt deren Durchführung.

## Vorbereitung der Lehrperson

### Gemeinsamer Einstieg ohne KI-Vorkenntnisse

Beginnen Sie mit dem [Einsteigerblock des KI-Foliensatzes](../../Presentations/AI_SQL_Server_2025/README.md).
Die bekannten Schritte einer SELECT-Abfrage bilden den Bezugspunkt für den
synthetischen Wissensbasisfall. Lassen Sie zuerst die erwartete Quelle und
Antwort benennen. Erklären Sie die neuen Begriffe einzeln, bevor Modellzugang,
Vektorindizes oder Performancefragen hinzukommen. Fragen der Gruppe und
gemeinsame Ergebnisbesprechung gehören zu diesem Einstieg.

Die [konkreten Teaching Paths für das 61-Folien-Deck](SQL_SERVER_2025_AI_TEACHING_PATHS.md)
binden diesen Einstieg an90 geplante Netto-Minuten. BASIS wählt danach Material für
ein Vierstundenfenster aus; STANDARD plant einen Unterrichtstag mit allen acht
Offlineaufgaben, VERTIEFUNG zwei Tage einschließlich getrennten Beleglese-/
Entwurfsaufgaben. Bruttofenster, Pausen und Nettolehrzeit sind im kanonischen
Workstreamplan getrennt. Zeiten und Verständlichkeit sind noch nicht erprobt.

Der erste geometrische SQL-Versuch ist eine angeleitete Vorführung mit lokalen
Variablen und SELECT. Zeigen Sie Voraussetzung, Vorhersage, Code und Ergebnis
in dieser Reihenfolge. Die vorgegebenen Zahlen stammen aus keiner realen
Embedding-Inferenz. Die Vorführung benötigt eine vorbereitete SQL-2025-
Labverbindung, aber weder Modellservice, Cloudkonto noch Preview-Enable.
Ohne passenden eigenen Server bespricht die Gruppe die Ergebnisfolie.
Installation, Login-/Rollenänderung und Modellzugang sind keine Schritte,
die Teilnehmende aus einem Fehler im Beispiel heraus eigenständig ausführen.

Erst danach wählen Sie passende Fachmodule und die unten aufgeführten
manifestbasierten Demos. Deren Setup, Rollen, vollständige Eigentumsmarker und
Cleanup bleiben verbindlich. Die neue Vorführung verändert die acht
Arbeitsheftaufgaben, ihre einzige Lösung und Rubrik nicht. Lehrzeiten und
Lernwirksamkeit der erweiterten Einführung sind noch nicht erprobt.

### Vorbereitung der manifestbasierten Demos

Lesen Sie die [Grundlagenbegriffe](SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md), das
Arbeitsheft und die acht unten verlinkten Demo-READMEs. Klären Sie vor der Einheit,
ob SELECT, ORDER BY, Parameter und Objektberechtigungen bereits bekannt sind.
Bei fehlendem Vorwissen erklären Sie diese Begriffe am jeweiligen synthetischen
Beispiel, bevor die Gruppe die zugehörige Aufgabe bearbeitet.

Die [Ausführungsanleitung](DEMO_EXECUTION_GUIDE.md) ist der verbindliche SQL-Aufrufer.
Die bereits vorliegenden [Runtimebelege](../Project_Planning/SQL_SERVER_2025_AI_PROVIDER_REVIEW.md)
betreffen SQL Server 2025 Enterprise Developer auf Linux/Docker und den zusätzlichen
Podmanpfad für alle acht Demos. Andere Editionen und Windows sind nicht dadurch
qualifiziert. CL170 ist eine eigene Voraussetzung; eine passende Engineversion
beweist noch keinen passenden Compatibility Level. SQL Server 2019/2022 liefern
hier den vorgesehenen SKIP_VERSION vor Setup.

Verwenden Sie eine eigene dedizierte Labinstanz und die vorgesehenen synthetischen
Fixtures. Prüfen Sie vorhandene Runtimebelege und den tatsächlichen aktuellen
Preflight; dieser Materialentwurf fordert keinen erneuten unveränderten
Qualifikationslauf. Für die spätere Lehrdurchführung gelten Authentifizierung,
Sicherheitsbestätigung, Phasenreihenfolge und Recovery aus der Ausführungsanleitung.
Setup-/Cleanupownerrechte werden nicht als Teilnehmerrechte ausgegeben.
SQL-Authentifizierung bezieht Passwörter ausschließlich aus SQLCMDPASSWORD in der
Umgebung. Anleitungen enthalten keine Passwortwerte oder reale Verbindungsnamen.

Full-Text ist bei QRY-017 optional. Bereiten Sie die Besprechung des sichtbaren WARN
bei fehlender Komponente vor; eine Installation oder Konfigurationsänderung gehört
nicht zu dieser Lehreinheit. Live-Embeddings, Cloud, ONNX, ANN und Tenant-/Pooling-
Grenzen besitzen eigene offene Gates im
[Ausführungsstand](../Project_Planning/CURRENT_EXECUTION_STATUS.md#autonome-umsetzung-des-ki-workstreams-vom-2026-10-11).
Die acht Offlineaufgaben ersetzen diese Nachweise nicht.

## Wiederkehrender Ablauf je Aufgabe

1. Stellen Sie die Vorhersagefrage aus dem Arbeitsheft. Lassen Sie die Erklärung
   zuerst ohne Lösungstabelle formulieren und die erwartete Beobachtung festhalten.
2. Zeigen Sie Demo-ID, Voraussetzungen und die tatsächlich verwendete Phase.
   Führen Sie die Demo später nur über den Ausführungsleitfaden aus. Eine
   Rückmeldung zum aktuellen Preflight bleibt von historischen Belegen getrennt.
3. Lassen Sie konkrete Rows, Counts oder Rechtefehler dem jeweiligen Codepfad
   zuordnen. Lesen Sie die Summary zusammen mit den fachlichen Assertions.
4. Besprechen Sie die Trainerlösung im Arbeitsheft. Fragen Sie nach einer
   naheliegenden Schlussfolgerung, die der kleine konkrete Versuch noch nicht belegt.
5. Lassen Sie Cleanupsummary und unabhängige eigene DB-Abwesenheit festhalten.
   Der Lauf ist bei einem Cleanupfehler noch nicht abgeschlossen. Anschließend
   bewerten Sie Erklärung und Beobachtungsbeleg nach der vorhandenen Rubrik.

Sammeln Sie im Beobachtungsbogen keine Namen, echten SQL-Texte oder Daten aus
anderen Systemen. Eine synthetische Kennung genügt. Soll- und Ist-Lehrzeiten
werden erst bei einer späteren Erprobung getrennt erfasst; aus Runtime-Laufzeiten
lassen sich keine Lehrzeiten ableiten.

## Vorgeschlagene Reihenfolge und Moderation

Die Reihenfolge baut vom Datentyp über Retrieval bis zu überprüfbaren
Kontrollgrenzen auf und beginnt erst nach dem gemeinsamen Einsteigerblock.
Die [Teaching Paths](SQL_SERVER_2025_AI_TEACHING_PATHS.md) ordnen sie dem derzeit
vorbereiteten Offlinekern zu; vollständige Live-/Curriculum-/Generalprobenabnahme
bleiben im [Workstreamplan](../Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md) offen.

| Schritt / Material | Fokus der Moderation | Beobachtung für die Besprechung | Transferfrage |
|---|---|---|---|
| 1. [QRY-014](../../Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/README.md), CUR-013/CUR-014 | Vektortyp und fachlichen Modellraum vor der Suche auseinanderhalten. | Dimension/float32 und die verschiedenen Modellraumkennungen im eigenen Geometriefall. | Welche Provenienz benötigen Sie zusätzlich zum gültigen SQL-Typ? |
| 2. [QRY-015](../../Demos/09_AI_SQL_Server_2025/QRY-015_Vector_Metrics/README.md), CUR-014/CUR-019 | Vor der Sortierung die Bedeutung von Distanz, Norm und Normalisierung erklären lassen. | Rangfolge vor/nach Normalisierung und die feste Id-Tieregel. | Welche Aussage über Sprachrelevanz lässt dieser Geometriefall offen? |
| 3. [QRY-016](../../Demos/09_AI_SQL_Server_2025/QRY-016_Chunk_Provenance/README.md), CUR-015 | Vom Vektor zur belegbaren Eingabeeinheit wechseln. | DocId/Version, Anfang/Länge und Überlappung gegen den synthetischen Quelltext prüfen. | Welche Versionsinformation ginge bei einem isoliert gespeicherten Chunk verloren? |
| 4. [QRY-017](../../Demos/09_AI_SQL_Server_2025/QRY-017_Search_Comparison/README.md), CUR-015/CUR-019/CUR-020 | Auswahl des Suchpfads aus der konkreten Frage begründen lassen. | Autorisierter Identifier-Treffer und optionaler Full-Text-Status; vier konstruierte Rows. | Welcher Qualitäts- und Performancebeleg fehlt für eine allgemeine Pfadempfehlung? |
| 5. [QRY-018](../../Demos/09_AI_SQL_Server_2025/QRY-018_Offline_RAG/README.md), CUR-017 | Retrieval, stützende Quelle und zulässige Antwort als getrennte Entscheidungen zeigen. | ACCEPTED/REJECTED/ABSTAINED mit konkreter Quellenstelle und Versions-/Kontextbezug. | Wann ist die begründete Nichtantwort das passende Ergebnis? |
| 6. [QRY-019](../../Demos/09_AI_SQL_Server_2025/QRY-019_SQL_Input_Policy/README.md), CUR-018/CUR-021/CUR-022 | Feste Statementstruktur, Wertparameter und tatsächliche SQL-Rechte im Code verorten lassen. | Literal-Treffer trotz Quote-/DDL-Text als Wert; abgelehntes Zusatzstatement und Readergrenzen. | Warum sind Strukturpolicy und Rechteverweigerung zwei unterschiedliche Belege? |
| 7. [DGN-008](../../Demos/09_AI_SQL_Server_2025/DGN-008_Offline_Model_Rights/README.md), CUR-016/CUR-018/CUR-022 | Setup, Ingestion und Retrieval ihren tatsächlichen Rechten zuordnen. | Grantreduktion und erlaubter Restbetrieb; External-Model-Recht als Metadatenbeleg. | Was müsste für einen tatsächlichen Provider-/Embeddingaufruf zusätzlich geprüft werden? |
| 8. [DGN-009](../../Demos/09_AI_SQL_Server_2025/DGN-009_Offline_Injection/README.md), CUR-018/CUR-022 | Quelleninhalt und Befugnis zur Ausführung getrennt verfolgen. | Tatsächlich retrievte manipulierte Quelle, feste Antwort-/Toolpolicy und echte SQL-Rechtefehler. | Welche Grenze bleibt gegenüber einem unbekannten Live-Modell und seinen Tools offen? |

## Getrennte Ergänzung: RES-008-Ergebnisse lesen

Nutzen Sie die ergänzende Aufgabe und die einzige gepflegte Lösung im
[Arbeitsheft](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md#ergänzende-ergebnisleseaufgabe-res-008).
Diese Ergänzung ist nicht Teil der acht implementierten Basisdemos und hebt
PROPOSED/volle TP-PERF-/Modulgrenzen nicht auf. Vorliegende
[gebundene aggregierte Beobachtungen](../Project_Planning/SQL_SERVER_2025_AI_RESOURCE_AGGREGATION_REVIEW.md)
genügen für die Leseaufgabe; kein erneuter unveränderter SQL-Lauf erforderlich.
Ein späterer begründeter praktischer Versuch folgt ausschließlich der
[Demo-README](../../Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions/README.md)
mit YELLOW-/Owner-/Build-/Cleanupgrenzen und optional `--summary`.

Lassen Sie zuerst 20/54/74/5420 sowie sechs A/B-Fenster je Pfad/Paar berechnen.
Zeigen Sie danach, wie CPU, Elapsed und Reads im konkreten Dimensionspaar
unterschiedliche Richtungen besitzen können. Fragen Sie nach Batch- gegenüber
individueller Querylatenz, AA-Kontrolle, N/A/Nullfenstern und vollständigem
Beibehalten von Ausreißern. Die UTC-Schleifenzeit einschließlich Tempresult-Inserts
und die sie umgebenden eigenen Request-Counterdifferenzen besitzen verschiedene
Messgrenzen. Besprechen Sie abschließend die beschränkte Bedeutung
der 30 numerischen FWK-PASSs bei Gesamt-WARN, repräsentativem Plan und offener
Modellqualität. Keine Lehrdauer oder gemessene Lernwirksamkeit aus Runtime ableiten.

Bewerten Sie die Ergänzung getrennt nach der Arbeitsheftrubrik; die acht
Basisaufgaben behalten maximal 16 Punkte. Keine Namen, Rawidentitäten,
Querytexte oder Daten realer Systeme sammeln. Die Auswertung allein belegt
keinen neuen Runtime-, Provider-, Tenant- oder vollständigen Performancepfad.

## Drei optionale lokale Evidenzleseaufgaben moderieren

Die neuen [Aufgaben E1–E3 mit Lösungen](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md#drei-optionale-evidenzleseaufgaben-lokale-komponenten)
lesen bestehende öffentliche Teilnachweise. Sie erfordern keine neue Modell- oder
SQL-Ausführung. Geben Sie ausschließlich die dort verlinkten öffentlichen
Zusammenfassungen aus; keine privaten Receipts, Vektoren, Server-/Containernamen,
IDs, SIDs oder Secrets. Installation, Login-/Rollen-DDL, Cloud-/Provideraufrufe
und private Qualifikationsskripte sind keine Teilnehmeraufgaben.

Leiten Sie Einsteigende je Aufgabe durch **Zweck → vorherige Erwartung → tatsächliche
Beobachtung → offene Schlussfolgerung**. Lassen Sie Erwartung und Status vor der
Interpretation getrennt notieren. Eine Komponentenprüfung betrifft einen einzelnen
Schritt; sie ist keine Abnahme der gesamten Anwendung. Bewerten Sie nach der
getrennten optionalen Arbeitsheftrubrik; keine Bestehens- oder Zeitbehauptung.

| Optionale Aufgabe | Geeigneter Anschluss | Moderationsfrage vor der Lösung |
|---|---|---|
| E1, Modellreceipt und SQL-Suche | Nach QRY-014/QRY-018: vom geometrischen Beispiel zu einem gebundenen tatsächlichen Modell-/SQL-Teilbeleg. | Welche Stufe erzeugte die Vektoren, welche verwendete sie nur erneut, und welche Antwortstufe fehlt? |
| E2, gescheiterte Generation | Nach QRY-018: verfügbare Rückgabe, gültiges Format und fachlich richtige Antwort getrennt behandeln. | Was durfte nach dem positiven Fehlerfall noch als tatsächlich geprüft gezählt werden? |
| E3, tatsächliche SQL-Logins | Nach QRY-019/DGN-008: Anmeldung, DBuser-Zuordnung, Datenfilter und Rechtefehler getrennt verorten. | Welcher Identitätsbeleg unterscheidet eine neue authentifizierte Verbindung vom bisherigen EXECUTE-AS-Beispiel? |

Besprechen Sie Lösungen ausschließlich anhand der drei zusätzlichen Einträge im
Arbeitsheft. Bei historischen FAILs wird keine Korrektur oder Wiederholung im
Unterricht beauftragt. Ein zerstörter eigener Container ist von einem tatsächlich
belegten SQL-Drop und einer frischen SQL-Abwesenheitsprüfung zu unterscheiden.
Die Ergänzungen verändern weder acht Basisaufgaben/16 Punkte noch die separate
RES-008-Bewertung; E1–E3 erhalten optional je eigene 0–2 Punkte. Die vorhandenen
Teaching-Path-Zeiten bleiben unveränderte Planung ohne gemessene Lehrdauer.

## Umgang mit abweichenden Beobachtungen

Die folgende Handlungstabelle betrifft später tatsächlich ausgeführte Basisdemos.
Bei E1–E3 lesen Sie ausschließlich den vorhandenen Status- und Cleanupnachweis;
keine neue Recovery, Inferenz, Login-DDL oder Wiederholung wird damit beauftragt.

| Tatsächlicher Status | Nächster Lehrschritt |
|---|---|
| PASS | Den konkreten Assertionbeleg erklären lassen und seine Aussagegrenze benennen. Ein grüner Labfall begründet keine allgemeine Modell-/Provider-/Tenantfreigabe. |
| WARN | Die optionale fehlende Evidenz sichtbar lassen und die passende Grenze der Interpretation besprechen. Bei QRY-017 begründet fehlendes Full-Text keinen vollständigen Suchvergleich. |
| SKIP | Den konkreten Voraussetzungscode erklären; bei vorgesehenem Versions-SKIP erfolgt kein Setup. Ohne Demoausführung entsteht kein fachlicher Runtimebeleg. |
| FAIL | Die betroffene Phase und den begrenzten Fehlerbeleg festhalten, dann den vorgesehenen eigenen Cleanup/Recovery ausführen. Keine Erfolgsaussage und kein unveränderter Retry; Änderungen oder ein neuer begründeter Prüfauftrag werden vor dem nächsten Lauf geklärt. |

Bleibt die eigene DB nach Cleanup vorhanden oder fehlt der unabhängige
Abwesenheitsbeleg, führen Sie die Wiederherstellung gemäß Ausführungsleitfaden und
Demo-README zu Ende. Namen allein autorisieren keinen DB-Abbau; die vier vollständigen
Eigentumsmarker und der eigene RunToken bleiben verbindlich. Fremde oder nicht
gebundene Bestände dürfen nicht verändert werden.

## Abschluss der Offlineeinheit

Lassen Sie die Gruppe an einem der acht Fälle erklären, welche Eingabe geprüft wurde,
welcher tatsächliche Beleg vorliegt und welcher nächste Nachweis noch fehlt. Verwenden
Sie dafür den vorhandenen Beobachtungsbogen und die Rubrik mit höchstens 16 Punkten.
Eine Bestehensgrenze oder gemessene Lernwirksamkeit ist damit nicht festgelegt.

Dokumentieren Sie offene Verständnisfragen und tatsächliche Status-/Cleanupgrenzen
ohne reale Systemdaten. Dieses Material ist für die anschließende Generalprobe
vorbereitet. Das [61-Folien-KI-Deck mit editierbaren Sprechernotizen](../../Presentations/AI_SQL_Server_2025/README.md)
hat bereits dokumentierte Render-/Einzelbild- und native PowerPoint-Prüfung.
Teilnehmererprobung, gemessene Lehrzeiten, tatsächliche Generalprobe, volle
Live-/Lehrpfade und die vollständige Abnahme aller 18 registrierten Demoentwürfe
bleiben im kanonischen Workstreamplan und Ausführungsstand offen. Hierfür wurden
weder das Deck neu exportiert noch Office, SQL oder ein Modell aufgerufen.
