# Generalprobe mit Teilnehmenden vorbereiten

| Merkmal | Wert |
|---|---|
| Bestehende Arbeitspakete | `PRS-010`, `CUR-007`, `CUR-008`, `DOC-002`, `DOC-003` |
| Planstatus | `DESIGNED` – Ablauf vorbereitet; Teilnehmerdurchführung und empirische Abnahme nicht ausgeführt |
| Stand | 2026-10-07 |
| Ziel | Orientierung, Bedienbarkeit, Erklärung und Transfer an einer repräsentativen Demoauswahl prüfen |
| Auswahl | `OPT-002`, `QRY-001`, `QRY-004`, `CON-004` |
| Geprüfte Präsentationsquelle | 102 Folien, SHA-256 `f655bc850e6d1367f52c7485babc5ce76eb23e14f8c8a1592b847d111473d7c5` |

## 1. Abnahmegrenze und vorhandene Planung

Der [Masterplan §14](MASTER_IMPLEMENTATION_PLAN.md#14-querschnitt-c--präsentation-und-lehrmaterial) verlangt eine vollständige Generalprobe durch `PRS-010`. `CUR-007` und `CUR-008` betreffen Aufgaben und Lernkontrolle. Die [ADV-010-Endabnahme](ADV_010_FINAL_ACCEPTANCE_REVIEW.md) und die [Lehrmittelfreigabe](W_PRS_001_TEACHING_RELEASE.md) belegen Quellen-, Runtime-, Render- und Profilprüfungen, enthalten aber keinen ausgefüllten Nachweis einer Generalprobe mit echten Teilnehmenden.

Dieser Plan konkretisiert die bestehenden Arbeitspakete. Die Auswahl ist eine begrenzte Pilot-Generalprobe, keine Prüfung aller Module und keine statistisch belastbare Wirksamkeitsstudie. Die historische Lehrmittelfreigabe wird dadurch weder umgedeutet noch auf einen empirischen Lernerfolg erweitert. Die vollständige Generalprobe des gewählten Kursprofils und die Releaseabnahme bleiben anschließend erforderlich.

## 2. Voraussetzungen und Vorbereitung

Für den ersten Durchlauf sind drei bis sechs freiwillige Teilnehmende mit T-SQL-Grundkenntnissen vorgesehen, möglichst mit unterschiedlichen Erfahrungen in Entwicklung und Administration. Eine Person führt die Schulung, eine weitere beobachtet Bedienung und Zeitbedarf. Diese Rollen sind eine Vorbereitung, keine bereits organisierte Veranstaltung. Kontaktaufnahme und Terminorganisation gehören nicht zum Auftrag.

1. Legen Sie vor Beginn Repository-Commit, Masterdeck-Hash und Kursprofil fest. Verwenden Sie für diese Auswahl das Masterdeck; die fünf Suchstrategie-Folien liegen im Vertiefungsblock. Die [Profilanleitung](../HowTo/PRESENTATION_VARIANTS.md) erklärt die Custom Shows. Es ist kein zusätzlicher Deck-Export erforderlich.
2. Prüfen Sie die [historischen Runtime-Nachweise](../Demo_Catalog/README.md). Planen Sie eine neue, isolierte Wegwerfinstanz für die tatsächliche Generalprobe; starten Sie sie erst im autorisierten Durchführungsauftrag. Es werden keine vorhandenen SQL-Ressourcen übernommen. Eine Engine-Version genügt für den didaktischen Pilotlauf; diese Probe ersetzt keine Versionsmatrix.
3. Verwenden Sie SQL Server 2025/CL170 oder eine dokumentierte unterstützte 2019/CL150- beziehungsweise 2022/CL160-Kombination. Rechte und Ressourcen müssen für alle vier Demo-README-Dateien genügen. Die größte Anforderung der Auswahl ist maßgeblich; der Preflight muss dennoch je Demo erfolgreich sein.
4. Folgen Sie [DEMO_EXECUTION_GUIDE.md §2–4](../HowTo/DEMO_EXECUTION_GUIDE.md#2-arbeitsplatz-und-instanz-vorbereiten) für Python, `sqlcmd`, Verbindung und Laden von `Invoke-SqlPerfDemo`. Zugangsdaten bleiben außerhalb von Dateien und Prozessargumenten. Öffnen Sie Folien und Sprechernotizen parallel.
5. Erläutern Sie die gelbe Sicherheitsstufe von `CON-004`, den begrenzten Lauf und den markergebundenen Abbruch-Cleanup. Vereinbaren Sie, dass bei `FAIL`, ungeklärtem Zustand oder Cleanupfehler keine nächste Demo startet.
6. Legen Sie einen neutralen Beobachtungsbogen nach Abschnitt 6 bereit. Speichern Sie weder Bildschirmaufnahmen noch rohe SQL-, Plan- oder Prozessausgaben. Die Lernenden erhalten die Aufgaben; Musterantworten aus Abschnitt 4 bleiben bis zur Auswertung bei der Schulungsleitung.

## 3. Ablauf und Zeitbudget

Die 100 Minuten sind ein vorab gesetztes didaktisches Planungsbudget, keine gemessene Demo-Laufzeit und keine SQL-Server-Leistungsgrenze. Erfasst werden die tatsächlichen Zeiten einschließlich Bedienung, Erklärung und Hilfe. Der bereits geprüfte Arbeitsplatz wird vorausgesetzt; Installationszeit wird gesondert dokumentiert.

| Abschnitt | Planzeit | Beobachtungsauftrag |
|---|---:|---|
| Einstieg und Sicherheit | 10 min | Eine Demo über den Einstieg finden, Versionsvoraussetzung und historische Evidenz unterscheiden; Manifestpfad und Cleanup finden |
| Statistikgrundlagen: `OPT-002`, Folien 23–24 | 15 min | Führende Statistikspalte, Sample-/Fullscan-Header, Histogramm und Density Vector am tatsächlich ausgegebenen Ergebnis zuordnen |
| SARGability: `QRY-001`, Folie 37 | 15 min | Vor der Messung eine Hypothese formulieren; danach Ergebnisgleichheit, Planform und Logical Reads getrennt bewerten |
| Suchstrategien: `QRY-004`, Folien 89–93 | 25 min | Gleichheit der Ergebnisse, Wiederverwendung, Compilearbeit und sichere Parameterbindung unterscheiden; Warnung ohne Verbesserungsbehauptung erklären |
| Blocking: `CON-004`, Folie 66 | 20 min | Unmittelbaren Blocker und Head Blocker bestimmen, Lock-Waits belegen und die geordnete Gegenprobe vergleichen |
| Selbstständige Transferfragen | 10 min | Vier Aufgaben aus Abschnitt 4 ohne vorgegebene Musterantwort lösen; Hilfen getrennt zählen |
| Abschluss und Cleanupkontrolle | 5 min | Übrig gebliebene Labordatenbanken ausschließen, Sitzung schließen und offene Befunde benennen |

Führen Sie die Demos seriell aus. Pro Block gilt: Folie erklären, Beobachtungsfrage stellen, Lernende den Einstieg finden lassen, Manifest ausführen, Phasenergebnisse gemeinsam lesen, Gegenprobe erklären und Cleanup kontrollieren. Die vorbereiteten Aufrufe verwenden die Variablen aus dem zentralen Leitfaden:

```powershell
Invoke-SqlPerfDemo -DemoId OPT-002 -Server $server -Authentication $authentication -Username $username
Invoke-SqlPerfDemo -DemoId QRY-001 -Server $server -Authentication $authentication -Username $username
Invoke-SqlPerfDemo -DemoId QRY-004 -Server $server -Authentication $authentication -Username $username
Invoke-SqlPerfDemo -DemoId CON-004 -Server $server -Authentication $authentication -Username $username -ConfirmIsolatedLab
```

Führen Sie jeden Aufruf einzeln aus und prüfen Sie sein Cleanup, bevor der nächste beginnt. `CON-004` orchestriert vier Sessions automatisch. Dieser kurze Harnesslauf ist keine dauerhaft interaktive `READY_FOR_USER`-Umgebung. Wird für die Beobachtung mehr Zeit benötigt, ist der bereits freigegebene [interaktive CON-004-Pfad](../HowTo/CON_004_INTERACTIVE_SCENARIO.md) separat zu wählen; seine zusätzlichen Lifecycle-Voraussetzungen sind dann Teil der Probe.

## 4. Aufgaben, Musterantworten und Übergänge

| Demo / Lernziel | Selbstständige Aufgabe | Musterantwort / typische Fehlannahme |
|---|---|---|
| `OPT-002` / `LO-M02-02` | Welche Statistikspalte beschreibt das Histogramm? Welche Metadaten belegen den Fullscan? Welche Aussage über die zweite Spalte ist damit noch nicht belegt? | Histogramm der ersten Statistikschlüsselspalte; nach Fullscan stimmen im Demomodell `rows_sampled` und `rows` überein. Density Vector und Histogramm liefern unterschiedliche Information. Eine vollständige Verteilung oder Korrelation der zweiten Spalte folgt daraus nicht. |
| `QRY-001` / `LO-M03-01` | Für einen Kalendertag auf einer `datetime2`-Spalte einen halboffenen Bereich formulieren. Welche Prüfungen müssen vor „besser“ erfolgen? | Typgerechter Tagesbeginn einschließlich und nächster Tagesbeginn ausschließlich; Ergebnisgleichheit prüfen, anschließend Plan und Logical Reads in gleichem Scope vergleichen. Ein Seek allein beweist keinen besseren Gesamtplan. |
| `QRY-004` / `LO-M03-08` | Recompile zeigt dieselben Reads wie Catch-all. Ist die Vorführung gescheitert? Welche zwei weiteren Kriterien braucht die Strategiewahl? | Der Richtungsvorteil ist nicht belegt; `WARN_EMPIRICAL_VARIANCE` wahrheitsgemäß einordnen. Ergebnis- und Sicherheitsverträge gesondert prüfen. Beispielsweise Compilearbeit/Ausführungsfrequenz und Parameterbindung beziehungsweise Wartbarkeit bewerten; keine allgemeine Rangfolge ableiten. |
| `CON-004` / `LO-M05-02` | Im neutralen Beispiel wartet C auf B, B auf A, A auf niemanden. Wer ist unmittelbarer Blocker von C, wer Head Blocker? Wie wird die Ursache geprüft? | B ist unmittelbarer Blocker, A die Wurzel. Request-, Session- und Transaktionszustand sowie gehaltene Ressource prüfen; anschließend geordnete Transaktionsbeendigung und erneute Messung vergleichen. Die längste Wait-Zeit allein benennt die Ursache nicht. |

Die folgenden Übergänge verbinden das Deck mit dem tatsächlichen Code:

- Vor `OPT-002`: Folie 23 ist ein Schema der begrenzten Histogrammauflösung, keine Abbildung der gemessenen Statistik. Zeigen Sie anschließend die tatsächliche führende Spalte und das gemessene Histogramm. Folie 24 trennt den Density Vector davon.
- Vor `QRY-001`: Folie 37 vergleicht einen Jahresfilter mit einer Jahresbereichsbedingung. Der Code vergleicht einen Tagesbereich auf `EventDateTime` mit `CONVERT(char(10), EventDateTime, 120)`. Beide illustrieren den Zugriffspfad, verwenden aber unterschiedliche Beispielzeiträume; diese Übergabe ausdrücklich erklären.
- Vor `QRY-004`: Folie 89 beschreibt die kontrollierte Catch-all-Baseline dieser Demo. Eine Planform ist keine allgemeine Garantie für alle Querytexte, Konfigurationen oder adaptiven Verfahren. Folie 90 und ihre Note müssen gemeinsam präsentiert werden: Im historischen Matrixlauf entstand kein Read-Vorteil. Folien 91–92 trennen Sicherheit und Wiederverwendung; Folie 93 eröffnet eine kontextabhängige Auswahl.
- Vor `CON-004`: Die Pfeile auf Folie 66 bedeuten „wartet auf“. Das Schema zeigt zusätzlich einen zweiten wartenden Zweig; der Code bildet Head–Middle–Leaf plus Beobachtersession ab. Die gezeigten Sessionnummern sind neutrale Beispielwerte und keine erwarteten Laufzeit-IDs. Von der wartenden Session aus wird die Beziehung bis zum Head Blocker verfolgt.

## 5. Abbruch, Recovery und Nachprüfung

Bei einem Fehler stoppen Sie die Folgeaufrufe. Lassen Sie den Harness sein begrenztes Cleanup versuchen. Nach einem abgebrochenen Prozess verwenden Sie ausschließlich [DEMO_EXECUTION_GUIDE.md §6](../HowTo/DEMO_EXECUTION_GUIDE.md#6-cleanup-prüfen-und-nach-abbruch-wiederherstellen) und die dort definierte Funktion, beispielsweise:

```powershell
Invoke-AbortedSqlPerfDemoCleanup -DemoId CON-004 -Server $server -Authentication $authentication -Username $username
```

Kontrollieren Sie danach die Abwesenheit der eigenen markierten Demodatenbank. Kein `DROP DATABASE` anhand eines Namensmusters und kein Beenden fremder Sessions. Bei unklaren Eigentumsmarkern oder `FAIL_CLEANUP` bleibt der Befund offen; es folgen keine weiteren Demos. Entfernen Sie abschließend Zugangsdaten aus der Prozessumgebung gemäß §7 des Leitfadens und bauen Sie ausschließlich die für die Probe neu erzeugte eigene Labinstanz über deren dokumentierten Lifecycle ab.

Ein Recovery-Test darf nur eine eigene Demo auf einer neuen bestätigten Wegwerfinstanz betreffen. Planen Sie dafür eine separate technische Vorprobe der Schulungsleitung; keine ungeprüfte harte Prozessunterbrechung während der Teilnehmerprobe. Solange der Abbruch-/Recovery-Pfad nicht praktisch geprüft wurde, bleibt diese Teilabnahme ausdrücklich offen.

## 6. Beobachtungsbogen und Auswertung

Pro Durchlauf werden nur folgende minimierte Angaben benötigt. Der Bogen ist leer; er enthält noch kein Teilnehmerergebnis.

| Feld | Auszufüllender Wert |
|---|---|
| Prüfstand | Datum, Repository-Commit, Deck-Hash und gewähltes Profil |
| Umgebung | Engine-Version/CU, Compatibility Level, Edition, OS, Provider und Ressourcenklasse; keine Hostnamen, lokalen Pfade oder Zugangsdaten |
| Zusammensetzung | Aggregierte Anzahl Teilnehmender und grobe Erfahrungsgruppen; keine Namen, Kontaktdaten oder Arbeitgeber |
| Je Block | Planzeit, Istzeit, gefundener Einstieg, Bedienhürde, benötigte Hilfe und neutral beschriebene Beobachtung |
| Je Transferaufgabe | Anzahl vollständig selbstständig, nach Hilfe, teilweise und nicht gelöst; Fehlannahme sachlich zusammenfassen |
| Lauf und Sicherheit | Tatsächlicher Outcome/Code, Einschränkung der Aussage, Cleanupkontrolle und gegebenenfalls Recoverybefund |
| Folie / Übergang | Folienposition oder stabile ID, Lesbarkeitsproblem, missverständliches Diagramm oder fehlende Überleitung |
| Konsequenz | Betroffener Pfad, konkrete Änderung, verantwortliche Rolle und benötigte Nachprüfung |

Speichern Sie zunächst nur eine datensparsame lokale Auswertung. Auch aggregierte Kleingruppenangaben können Rückschlüsse erlauben: keine identifizierenden Freitexte und keine Verknüpfung seltener Merkmale. Versionieren Sie ausschließlich neutralisierte sachliche Befunde nach Privacy-Prüfung; keine realen Teilnehmerrohaufzeichnungen, Plan-XML oder Logs. Der bestehende Registrierungsprozess gilt, wenn aus einem Befund ein neuer Task entsteht.

Die Auswertung trennt technische Ergebnisse, Bedienbarkeit und Lernerfolg. Für diesen Pilotlauf ist vorab festgelegt: Jede Person erhält alle vier Transferaufgaben; Hilfe wird sichtbar gezählt. Ein Verständnisziel bleibt offen, wenn es nur mit Hilfe oder mit einer fachlich falschen Erklärung erreicht wird. Sicherheits- und Cleanupfehler blockieren die betroffene Durchführung. Zeitüberschreitungen führen zu einer begründeten Anpassung des Ablaufs, nicht zu einer Produktleistungsbehauptung. Diese Kriterien sind lokale didaktische Abnahmekriterien, keine universelle Erfolgsquote.

Belegte Bedienungs- oder Inhaltsfehler werden gezielt korrigiert und am betroffenen Abschnitt nachgeprüft. Gestalterische Präferenzen und Verbesserungshypothesen werden als solche dokumentiert. Ein geänderter Ablauf erhält eine erneute Probe; frühere Ergebnisse bleiben an ihren Prüfstand gebunden. Erst ein ausgefüllter, überprüfter Bericht erlaubt eine Aussage über die tatsächlich getestete Auswahl. Die vollständige Kurs-Generalprobe bleibt ein eigener nächster Schritt.

## 7. Durchgeführte Folien- und Dokumentenprüfung

Am 2026-10-07 wurden neun Folien (23, 24, 37, 66, 89–93) mit PowerPoint aus dem oben genannten Deck frisch auf 1600 × 900 gerendert und einzeln visuell geprüft. Sprechernotizen wurden aus den jeweiligen OOXML-Beziehungen ausgelesen und gegen Demo-README, Phasen und Reviewnachweise abgeglichen. Der Deck-Hash war vor und nach Export identisch. Die PNGs dienten als lokale Prüfarbeitsdateien und wurden nach der Prüfung entfernt; es wurde kein zusätzliches Deck erzeugt. Diese Prüfung ist keine Teilnehmer- oder SQL-Runtime-Abnahme.

| Abschnitt | Objektiver Befund und Behandlung | Gestalterische Einschätzung / offene Prüfung |
|---|---|---|
| 23–24 / `OPT-002` | Führende Histogrammspalte, maximal 200 Schritte und getrennte Density-Information stimmen mit dem Demoauftrag überein. Die Überleitung vom Schema zur echten Ausgabe ist in Abschnitt 4 ergänzt. | Inhalt vollständig im Render sichtbar. Die orange Überschrift auf Folie 24 ist am Bildschirm erkennbar; Kontrast und Lesbarkeit unter realer Projektion bleiben zu prüfen. |
| 37 / `QRY-001` | Die Jahres-/Tagesbeispiele unterscheiden sich; Abschnitt 4 benennt diesen Übergang ausdrücklich. Die Note schließt eine pauschale Seek-Garantie aus. | Code und Erläuterung sind ohne erkennbaren Beschnitt sichtbar. Verständlichkeit des halboffenen Intervalls wird mit der Transferaufgabe geprüft. |
| 66 / `CON-004` | Wartepfeile und Note entsprechen dem Review vom 2026-10-05. Zusätzlicher Schemazweig, Laufzeit-IDs und tatsächliche Drei-Session-Kette plus Beobachter werden in Abschnitt 4 abgegrenzt. | Pfeilrichtung und Legende sind erkennbar. Ob Lernende unmittelbaren Blocker und Wurzel unterscheiden, ist noch nicht empirisch geprüft. |
| 89–93 / `QRY-004` | Die Note zu Folie 90 nennt den fehlenden Read-Vorteil bereits korrekt. Die Demo-README versprach ihn dagegen im Abschnitt „Erwartete Beobachtung“; diese Dokumentationsabweichung wurde korrigiert. Der Leitfaden erläutert Warnungen und Evidenz-Skips jetzt getrennt. | Kein erkennbarer Textbeschnitt im Einzelrender. Der Block ist textreich; Planzeit und Verständnisprüfung müssen klären, ob die Informationsdichte für die Zielgruppe passt. |

Die [Korrekturen vom 2026-10-05](../Reviews/PRESENTATION_DIAGRAM_REVIEW_2026_10_05.md) wurden berücksichtigt; bereits korrigierte Pfeile werden nicht als aktuelle Fehler geführt. In dieser begrenzten Prüfung war keine neue Layoutänderung am Deck erforderlich. Kontextgrenzen und Überleitungen stehen im Trainerablauf; die bestehende Präsentationsquelle, Notes und Custom Shows bleiben erhalten.

## 8. Offene Abnahme

Die eigentliche Teilnehmer-Generalprobe, eine praktische Abbruch-/Recovery-Vorprobe, Projektion im realen Raum, Messung der Istzeiten und selbstständiger Transfer sind nicht ausgeführt. Ein begrenzter erfolgreicher Pilotlauf würde diese Auswahl belegen, aber weder sämtliche Module noch die vollständige Schulungswirksamkeit oder Releasefähigkeit. Der nächste didaktische Schritt ist die beauftragte Durchführung mit ausgefülltem Beobachtungsbogen; eine erneute SQL-Versionsmatrix ist dafür nur bei einem konkret betroffenen Runtimevertrag erforderlich.
