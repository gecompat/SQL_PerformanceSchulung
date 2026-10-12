// Einsteigerfolge für den eigenständigen KI-Stream. Nur synthetische Lehrbeispiele.
// Quellenprüfung: 2026-10-12. Fachlicher Entwurf, keine Ausführung oder Lehrgangsabnahme.
export const introductionSlides = [
  {
    title: 'Einstieg mit bekannten SQL-Grundlagen', module: 'CUR-013',
    blocks: [
      ['Ausgangspunkt', 'Sie kennen SELECT und Tabellen. Erfahrung mit KI brauchen Sie für diesen Einstieg nicht.'],
      ['Unser Fall', 'Eine kleine technische Wissensbasis soll eine nachvollziehbare Antwort liefern.'],
      ['Erstes Ergebnis', 'Wir lesen Quellen und vergleichen feste Zahlen. Ein Modellzugang ist dafür noch nicht nötig.']
    ],
    notes: 'Didaktische Einführung. Frage an die Gruppe: Welche Informationen brauchen Sie, um eine technische Frage zuverlässig zu beantworten? Erwartete Antworten: die passende Quelle, ihre aktuelle Fassung und die Berechtigung zum Lesen. An diese bekannten Anforderungen knüpft die Einheit an. Die kleine Vektorübung zeigt später eine zusätzliche Suchmöglichkeit mit ausschließlich festen Zahlen. Vorwissen in Statistik, Modelltraining oder Cloudbereitstellung ist dafür nicht erforderlich. Erklären Sie neue Begriffe beim ersten Auftreten und lassen Sie die Gruppe den Unterschied zwischen einer Tabellenzeile und einem formulierten Antwortsatz wiedergeben. Übergang: Zunächst betrachten wir die Frage, bevor wir ein Werkzeug auswählen.',
    refs: ['.ai/PROJECT_CONTEXT.md', 'Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md']
  },
  {
    title: 'Eine Frage aus der technischen Wissensbasis', module: 'CUR-013 / CUR-017',
    blocks: [
      ['Frage', 'Wie lange bleiben die Protokolle des Moduls MOD_A erhalten?'],
      ['Quellen', 'Eine alte Anleitung nennt fünf Tage. Die aktuelle Anleitung nennt sieben Tage.'],
      ['Erwartung', 'Die Antwort muss zur aktuellen Anleitung passen und ihre Quelle nennen.']
    ],
    bottom: 'MOD_A und alle Dokumente sind frei erfundene Schulungsdaten.',
    notes: 'Dies ist ein eigenständiger synthetischer Einstiegskorpus, keine neue Demoimplementierung und keine behauptete Ausgabe einer bestehenden Demo. MOD_A ist ein imaginärer technischer Baustein. Die Texte und ihre festen Zuordnungen dienen der gemeinsamen Diskussion. Frage: Was könnte schiefgehen, wenn eine Suche beide Fassungen gleich behandelt? Erwartete Antwort: Eine veraltete Fassung kann die Antwort beeinflussen oder einen scheinbaren Widerspruch erzeugen. Eine flüssige Formulierung löst dieses Versionsproblem nicht. Übergang: Wir halten die kleinen Dokumente mit Kennung und Fassung sichtbar fest.',
    refs: ['Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md', 'Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md']
  },
  {
    title: 'Drei überschaubare Quelldokumente', module: 'CUR-013 / CUR-015',
    table: [
      ['Dokument', 'Fassung', 'Quelltext'],
      ['1: MOD_A', 'v1, veraltet', 'MOD_A bewahrt Protokolle fünf Tage auf.'],
      ['2: MOD_A', 'v2, aktuell', 'MOD_A bewahrt Protokolle sieben Tage auf.'],
      ['3: MOD_B', 'v1, aktuell', 'MOD_B bewahrt Protokolle neun Tage auf.']
    ],
    widths: [230, 230, 660],
    notes: 'Lassen Sie die Gruppe Dokument 2 für die konkrete MOD_A-Frage auswählen. Antwort: Es betrifft das richtige Modul und seine aktuelle Fassung. Dokument 1 ist veraltet. Dokument 3 ist aktuell, betrifft aber ein anderes Modul. Frage: Reicht die Zahl sieben als gespeichertes Ergebnis? Erwartete Antwort: Für eine überprüfbare Antwort benötigen wir zusätzlich Dokumentkennung, Fassung und den stützenden Textbereich. Alle drei vollständigen Sätze sind synthetisch. Es gibt hier keine Aussage über reale Aufbewahrungsfristen. Übergang: Eine SELECT-Abfrage liefert solche Daten als Rows.',
    refs: ['Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md']
  },
  {
    title: 'Eine vertraute SELECT-Abfrage', module: 'CUR-013',
    code: "SELECT DocId, Fassung, Text\nFROM (VALUES\n  (2, N'v2', N'MOD_A: sieben Tage')\n) AS d(DocId, Fassung, Text);",
    blocks: [['Ergebnis', 'Eine Row mit DocId 2, Fassung v2 und dem festen Text MOD_A: sieben Tage.']],
    bottom: 'Read-only-Beispiel. VALUES stellt eine feste Row bereit, ohne eine Tabelle anzulegen.',
    notes: 'Die gezeigte Abfrage ist vollständig und benötigt keine eigene Tabelle. Sie ist eine Illustration des bekannten tabellarischen Ergebnisformats. Der feste VALUES-Ausdruck enthält bereits die ausgewählte Fassung. Er sucht oder prüft nicht selbstständig, ob ein Dokument aktuell ist. Frage: Woher kennt SQL hier die sieben Tage? Antwort: Aus dem ausdrücklich angegebenen Literalwert. Es gibt weder Training noch Modellaufruf. Die Statements schreiben keine persistenten Daten. Ein späterer praktischer Versuch erfolgt nur auf dem vorbereiteten Schulungsziel. Übergang: Aus einer Row kann eine Anwendung einen Satz formulieren, doch die Herkunft des Werts muss erhalten bleiben.',
    refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md']
  },
  {
    title: 'Unterschiedliche Fragen an dieselben Daten', module: 'CUR-013 / CUR-017',
    table: [
      ['Frage', 'Was wir benötigen'],
      ['Was steht aktuell zu MOD_A?', 'Richtiges Modul und aktuelle Fassung'],
      ['Wann verschwinden die Logeinträge?', 'Passende Bedeutung trotz anderer Wortwahl'],
      ['Warum sind es genau sieben Tage?', 'Eine Quelle, die den Grund tatsächlich erklärt']
    ],
    widths: [500, 620],
    notes: 'Logeinträge und Protokolle gelten für diesen didaktischen Fall als alternative Wortwahl. Das ist eine festgelegte Lehrannahme, kein gemessener Sprachmodellbefund. Die erste Frage lässt sich bei bekanntem Datenmodell relational bearbeiten. Die zweite motiviert eine Suche nach Bedeutung. Die dritte zeigt eine Grenze: Unser Quelltext nennt eine Frist, aber keinen Grund. Frage: Darf die Anwendung daraus eine Erklärung für die Frist erfinden? Antwort: Nein, der Grund ist mit diesen Quellen nicht belegt. Ein begründetes Offenlassen ist angemessen. Übergang: Wir benennen nun, was KI-Verfahren in diesem Ablauf leisten sollen.',
    refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md', 'Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md']
  },
  {
    title: 'KI-Anwendungen rund um SQL Server', module: 'CUR-013 / CUR-016 / CUR-021',
    table: [
      ['Anwendung', 'Beispiel'],
      ['Wissenssuche', 'Passende Anleitung zu einer anders formulierten Frage finden.'],
      ['Textaufbereitung', 'Aus gelieferten Quellen einen kurzen Antwortentwurf oder eine Zusammenfassung bilden.'],
      ['SQL-Assistenz', 'Eine Query erklären oder einen Änderungsvorschlag diskutieren.'],
      ['Vorhersage und Klassifikation', 'Mit einem passenden zusätzlichen Modell einen Wert vorhersagen oder eine Kategorie zuordnen.']
    ],
    widths: [350, 770],
    bottom: 'Die Aufgabe bestimmt das Modell und den Anwendungspfad. Eine Funktion deckt nicht jede Aufgabe ab.',
    notes: 'Die Tabelle zeigt die Breite als didaktische Anwendungsideen, keine Liste bereits freigegebener Implementierungen. Bei Klassifikation ordnet ein passendes Modell eine Eingabe einer Kategorie zu. Bei Vorhersage liefert es einen Wert für die zuvor definierte Aufgabe. Dafür sind jeweils geeignete Daten, Modellwahl und eigene Bewertung nötig. Die SQL-2025-External-Modeldefinition im behandelten Pfad hat MODEL_TYPE=EMBEDDINGS. AI_GENERATE_EMBEDDINGS ist ein Embeddingzugang. Daraus folgt keine allgemeine native Chat-, Zusammenfassungs-, Vorhersage- oder Klassifikationsfunktion. Antworttext und Zusammenfassung sind im geplanten generativen Pfad Aufgaben der Anwendung und ihres Sprachmodells. SQL-Assistenz gehört ebenfalls zu einem ausdrücklich gewählten Client-/Anwendungspfad. Frage: Würde ein einziger Vektordatentyp alle vier Anwendungen lösen? Antwort: Nein, er ist ein Baustein. Übergang: Für die passende Auswahl erklären wir nun die grundlegenden Begriffe.',
    sources: ['SRC-080', 'SRC-081', 'SRC-089'], refs: ['Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md', 'Documentation/Research/SQL_SERVER_2025_AI_FEATURE_MATRIX.md']
  },
  {
    title: 'KI und Machine Learning in einfachen Worten', module: 'CUR-013',
    blocks: [
      ['KI', 'Künstliche Intelligenz umfasst etwa Systeme mit Wissensregeln oder gelernten Mustern. Suche und Texterzeugung sind mögliche Anwendungen.'],
      ['Machine Learning', 'Ein Modell lernt Muster aus Beispielen. Die Abkürzung dafür lautet ML.'],
      ['Unser Ziel', 'Wir verwenden geeignete Funktionen und prüfen ihr Ergebnis an konkreten Quellen.']
    ],
    notes: 'Die Folie bietet eine einfache Einordnung des breiteren KI-Feldes. Regelbasierte Wissensverarbeitung, Mustererkennung, Vorhersage und Sprachverarbeitung können KI-Anwendungen dienen. Machine Learning bezeichnet darin Verfahren, die Modellverhalten aus Trainingsdaten lernen. Ein regelbasiertes Wissenssystem kann mit ausdrücklich formulierten Regeln arbeiten. Eine generative Textanwendung ist deshalb nur ein möglicher Fall. Frage: Lernt schon ein SELECT aus einer festen VALUES-Row? Antwort: Nein, es verarbeitet die angegebenen Werte nach SQL-Regeln. Nicht jede regelgeleitete Berechnung wird dadurch automatisch zur KI-Anwendung. Das Erstellen einer Tabelle oder fester Geometrievektoren ist ebenfalls kein Modelltraining. Wir beginnen mit dieser Unterscheidung, um später keinen mathematischen Lehrfall als echte Sprachsemantik auszugeben. Übergang: Für unsere späteren Modellpfade betrachten wir nun Modellaufgabe und Eingabe genauer.',
    refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md']
  },
  {
    title: 'Ein Modell und seine Aufgabe', module: 'CUR-013',
    blocks: [
      ['Modell', 'Eine vorbereitete Rechenvorschrift verarbeitet eine Eingabe und liefert eine Ausgabe.'],
      ['Aufgabe', 'Ein Modell kann zum Beispiel Text in Zahlen abbilden oder einen Antworttext erzeugen.'],
      ['Prüfung', 'Wir müssen wissen, welches Modell welche Aufgabe übernimmt und wo seine Ausgabe geprüft wird.']
    ],
    notes: 'Die Rechenvorschrift umfasst bei einem ML-Modell gelernte Parameter. Für den Einstieg reicht die Eingabe-/Ausgabevorstellung. Vermeiden Sie eine Erklärung, in der ein Modell als Person dargestellt wird, die automatisch unsere Datenbank kennt. Frage: Sind Textsuche und Antwortformulierung dieselbe Aufgabe? Antwort: Nein. Eine numerische Repräsentation kann der Suche dienen. Die Formulierung eines Antworttexts ist ein weiterer Verarbeitungsschritt. Einige Modelle und Anwendungen verbinden mehrere Fähigkeiten, doch die Aufgaben und ihre Ergebnisse werden hier getrennt bewertet. Übergang: Ein vorbereitetes Modell kann verwendet werden, ohne es in der Schulung neu zu trainieren.',
    sources: ['SRC-087'], refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md']
  },
  {
    title: 'Training und Inferenz', module: 'CUR-013 / CUR-016',
    table: [
      ['Begriff', 'Was geschieht?', 'In diesem Einstieg'],
      ['Training', 'Ein Modell lernt aus Trainingsbeispielen.', 'Wir trainieren kein Modell.'],
      ['Inferenz', 'Ein vorbereitetes Modell verarbeitet neue Eingaben.', 'Späterer Modellpfad mit eigenen Voraussetzungen.'],
      ['Feste Lehrwerte', 'Wir geben Zahlen oder Antworten ausdrücklich vor.', 'Das ist unser erster Offlinepfad.']
    ],
    widths: [210, 480, 430],
    notes: 'Frage: Wenn wir MOD_A als neue Tabellenrow speichern, haben wir damit ein Sprachmodell trainiert? Antwort: Nein. Speichern, Suchen, Inferenz und Training sind verschiedene Vorgänge. Eine Anwendung kann aktuelle Dokumente zur Antwort hinzufügen, ohne das vorbereitete Sprachmodell neu zu trainieren. Ein Cloudservice kann Daten je nach Dienst und Funktion unterschiedlich verarbeiten. Aus unserer Erklärung des Anwendungspfads folgt deshalb keine allgemeine Datenschutz- oder Retentiongarantie. Die festen Werte des Einstiegs sind bewusst ohne Modell erzeugt. Übergang: Bei der Textausgabe betrachten wir ein Sprachmodell genauer.',
    sources: ['SRC-087', 'SRC-088'], refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md']
  },
  {
    title: 'Ein Sprachmodell erzeugt Antworttext', module: 'CUR-013',
    blocks: [
      ['Sprachmodell', 'Ein Large Language Model, kurz LLM, verarbeitet Textkontext und kann neue Textfolgen erzeugen.'],
      ['Beispiel', 'Aus einer gegebenen Quelle könnte die Anwendung den Satz bilden: MOD_A bewahrt Protokolle sieben Tage auf.'],
      ['Grenze', 'Ein gut formulierter Satz kann sachlich falsch oder durch die Quelle nicht gestützt sein.']
    ],
    notes: 'Der Beispielsatz auf der Folie ist von der Lehrperson fest vorgegeben. Er ist kein Ergebnis eines hier ausgeführten Modellaufrufs. Frage: Woran würden Sie die Antwort prüfen? Erwartete Antwort: Am aktuellen Dokument 2, Fassung v2, und an der Aussage zur Aufbewahrung. Ein Sprachmodell kann plausiblen Text erzeugen, obwohl nötiger Kontext fehlt. Die Qualität der Formulierung und die Qualität des Belegs werden deshalb getrennt bewertet. Vermeiden Sie den Eindruck, ein Modell hätte automatisch Zugriff auf unsere SQL-Tabellen. Diesen Zugriff vermittelt die Anwendung mit den tatsächlichen Rechten. Übergang: Text wird dabei in Verarbeitungseinheiten aufgeteilt.',
    refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md', 'Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md']
  },
  {
    title: 'Tokens und Textlänge', module: 'CUR-013 / CUR-015',
    blocks: [
      ['Token', 'Eine Verarbeitungseinheit des konkreten Sprachmodells. Ein Token kann einen Wortteil darstellen.'],
      ['Tokenizer', 'Er zerlegt den Text nach den Regeln des verwendeten Modells.'],
      ['Folge', 'Zeichenanzahl und Tokenanzahl sind verschieden. Beide Grenzen müssen zum jeweiligen Schritt passen.']
    ],
    notes: 'Nennen Sie den kurzen Satz MOD_A bewahrt Protokolle sieben Tage auf. Lassen Sie die Gruppe Wörter und Zeichen zählen. Frage: Kennen wir damit bereits seine genaue Tokenzahl? Antwort: Nein, dafür benötigen wir den tatsächlich verwendeten Tokenizer. Geben Sie keine erfundene Tokenzerlegung als Produktresultat aus. Tokens können Modelllimits und Requestkosten beeinflussen. Das später erläuterte SQL-FIXED-Chunking arbeitet dagegen mit Zeichenbereichen. Eine Chunkgröße ist daher kein bewiesenes Modelltokenlimit. Übergang: Die beteiligten Komponenten benötigen unterschiedliche Eingaben und liefern unterschiedliche Ergebnisse.',
    sources: ['SRC-079', 'SRC-087'], refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md']
  },
  {
    title: 'SQL Server, Modell und Anwendung', module: 'CUR-013 / CUR-016',
    table: [
      ['Komponente', 'Aufgabe im Wissensbasisfall'],
      ['SQL Server', 'Speichert Dokumente und liefert erlaubte Daten.'],
      ['Modell', 'Verarbeitet bereitgestellte Eingaben für seine Aufgabe.'],
      ['Anwendung', 'Vermittelt die Frage, sucht Quellen und prüft die Antwort.']
    ],
    widths: [330, 790],
    notes: 'Frage: Wer entscheidet, welche SQL-Rows ein Benutzer lesen darf? Antwort: Die tatsächliche Datenbankautorisierung zusammen mit dem festgelegten Anwendungspfad. Das Modell erhält nur den Kontext, den die Anwendung ihm übergibt. Die aktuelle SQL-External-Modeldefinition beschreibt im behandelten Pfad einen Embeddingzugang. Sie hostet nicht automatisch ein allgemeines generatives Chatmodell in der Database Engine. Diese technische Unterscheidung wird in der Vertiefung genauer behandelt. Ein Modell verändert keine Datenbankrechte allein durch seine Ausgabe. Übergang: Für das erste Verständnis können wir diese Komponenten auf einen noch kleineren Offlineversuch reduzieren.',
    sources: ['SRC-080', 'SRC-099'], refs: ['Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md']
  },
  {
    title: 'Der erste Offlineeinstieg', module: 'CUR-013 / CUR-014',
    blocks: [
      ['Eingaben', 'Kleine feste Vektoren und synthetische Texte statt eines Live-Modells.'],
      ['Zugang', 'Diese ersten Beispiele benötigen weder ChatGPT noch Copilot oder ein Cloudkonto.'],
      ['Beobachtung', 'Werte, Rangfolge und Quellen lassen sich gemeinsam erklären. Es gibt keinen Modellrequest.']
    ],
    bottom: 'Für die praktische Vorführung genügt die vorbereitete SQL-Testinstanz mit einem Queryclient.',
    notes: 'Frage: Brauche ich für diese ersten Beispiele schon ChatGPT, Copilot oder ein Cloudkonto? Antwort: Nein. Die festen T-SQL-Werte und die Distanzberechnung rufen keinen Modellservice auf. Frage: Welchen Teil können wir schon ohne Modellzugang verstehen? Antwort: Datentyp, Distanzberechnung, tabellarische Resultate und die Prüfung eines festen Antwortbelegs. Das ist der bewusst kleine Einstiegspfad. Er belegt keine Sprachmodellqualität und führt keinen Provideraufruf aus. Für Personen ohne laufenden SQL Server können die festen Eingaben und erwarteten Werte zunächst gemeinsam auf den Folien besprochen werden. Die praktische Vorführung benötigt anschließend eine passend vorbereitete Testinstanz mit einem Queryclient. Der vorhandene Demo-Ausführungsleitfaden übernimmt spätere vollständige Demos mit ihren eigenen Verträgen. Übergang: Die häufigste erste Hürde ist die Trennung von Server und Client.',
    sources: ['SRC-072', 'SRC-073'], refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_TRAINER_GUIDE.md', 'Documentation/HowTo/LOCAL_TEST_ENVIRONMENT.md']
  },
  {
    title: 'Serverversion und Client sind verschieden', module: 'CUR-014 / CUR-016',
    blocks: [
      ['SQL Server', 'Unsere VECTOR-Beispiele benötigen SQL Server 2025, Engine 17.x.'],
      ['Client', 'Das Programm zum Senden der Query macht aus einer älteren Engine keine SQL-Server-2025-Engine.'],
      ['Datenbank', 'Das Schulungsprofil verwendet Compatibility Level 170. Das ist eine eigene Datenbankeinstellung.']
    ],
    notes: 'Erklären Sie Engine als das SQL-Server-Programm, das die Query ausführt. Ein Client ist zum Beispiel ein Queryeditor oder sqlcmd. Compatibility Level steuert bestimmte Datenbankverhaltensweisen und ist nicht identisch mit der installierten Engineversion. VECTOR ist laut Microsoft unter allen Compatibility Levels der geeigneten Engine verfügbar. Das vollständige Schulungsprofil verwendet dennoch CL170, unter anderem wegen AI_GENERATE_CHUNKS. Frage: Beweist ein neuer Queryeditor die Verfügbarkeit von VECTOR auf einem älteren Server? Antwort: Nein. Wenn die Engine ungeeignet ist, wird die vorbereitete SQL-2025-Testumgebung benötigt. Es wird hier keine Installation oder Änderung ausgeführt. Übergang: Zwei read-only Abfragen zeigen die getrennten Werte.',
    sources: ['SRC-072', 'SRC-079', 'SRC-089'], refs: ['Documentation/Research/SQL_SERVER_2025_AI_FEATURE_MATRIX.md']
  },
  {
    title: 'Version und Datenbankeinstellung lesen', module: 'CUR-014',
    code: "SELECT CAST(SERVERPROPERTY('ProductMajorVersion') AS int) AS Major;\nSELECT compatibility_level AS CL\nFROM sys.databases WHERE name = DB_NAME();",
    blocks: [['Einordnung', 'Major 17 bezeichnet die Enginefamilie. CL 170 bezeichnet das gewählte Datenbankprofil.']],
    bottom: 'Die Query liest Eigenschaften. Sie ändert weder Server noch Datenbank.',
    notes: 'Der Code ist read-only. Die angezeigten Werte sind tatsächliche Umgebungswerte eines späteren praktischen Versuchs und werden nicht für diesen Entwurf als gemessen behauptet. Erwartung im vorbereiteten Schulungsprofil: Major17 und CL170. Eine Ausgabe Major16 ist kein SQL Server2025. Eine17.x-Engine kann eine Datenbank mit niedrigerem CL betreiben. Die Abfrage beweist noch nicht Edition, Rechte, verfügbare Komponente, Clienttransport oder die vollständigen Demovoraussetzungen. Frage: Was tun bei einer Abweichung? Antwort: Erst das Ziel und den vorgesehenen Preflight mit der Lehrperson klären. Keine automatische ALTER-Anweisung ergänzen. Den Compatibility-Level-Bezug entnehmen wir SRC079 und dem gewählten Projektprofil. Reale Namen oder Verbindungsdetails werden nicht in Unterlagen übernommen.',
    sources: ['SRC-072', 'SRC-079'], refs: ['Documentation/HowTo/DEMO_EXECUTION_GUIDE.md', 'Documentation/Research/SQL_SERVER_2025_AI_FEATURE_MATRIX.md']
  },
  {
    title: 'Eine vorbereitete Testumgebung und passende Rechte', module: 'CUR-014 / CUR-018',
    blocks: [
      ['Umgebung', 'Die Lehrperson bereitet eine dedizierte SQL-Server-2025-Testinstanz vor.'],
      ['Teilnehmende', 'Für unsere kleinen Beispiele lesen wir feste Werte. Einrichtung und Verwaltung bleiben getrennt.'],
      ['Falls etwas fehlt', 'Verbindung, Ziel und Rechte gemeinsam prüfen. Für die Diskussion können wir zuerst die Sollwerte lesen.']
    ],
    bottom: 'Spätere vollständige Demos nutzen ihre dokumentierten Setup- und Cleanup-Verträge.',
    notes: 'Frage: Benötigt die Person, die eine Query versteht, automatisch dieselben Rechte wie die Person, die das Lab einrichtet? Antwort: Nein. Eigene Demo-Setups können Datenbanken oder Rollen anlegen, während unsere DECLARE-/VALUES-/SELECT-Übung keine solchen Rechte benötigt. Die Lehrperson nutzt den vorhandenen Ausführungsleitfaden und bei fehlender Testinstanz die passende Umgebungsanleitung. Der Container-Quickstart ist für sein dort beschriebenes Szenario qualifiziert und wird nicht pauschal zur Freigabe sämtlicher KI-Pfade erklärt. Ein Berechtigungsfehler wird als Voraussetzung untersucht. Er wird nicht mit einer ungeprüften Rechteerweiterung gelöst. Die praktische Übung erfolgt auf dem vorbereiteten Schulungsziel. Übergang: Nun können wir die festen Zahlen kennenlernen.',
    refs: ['Documentation/HowTo/LOCAL_TEST_ENVIRONMENT.md', 'Documentation/HowTo/CONTAINER_QUICKSTART.md', 'Documentation/HowTo/DEMO_EXECUTION_GUIDE.md']
  },
  {
    title: 'Ein Vektor als kleine Zahlenliste', module: 'CUR-013 / CUR-014',
    blocks: [
      ['Drei Komponenten', 'VECTOR(3) enthält drei numerische Werte, zum Beispiel [1,0,0].'],
      ['Unsere Lehrwerte', 'Wir geben alle Zahlen ausdrücklich vor. Sie stammen aus keinem Textmodell.'],
      ['Vergleich', 'Die Cosine-Distanz vergleicht die Richtung der beiden Zahlenlisten.']
    ],
    notes: 'Zeigen Sie die drei Positionen in [1,0,0], ohne ihnen Wörter oder eine gemessene Sprachbedeutung zuzuweisen. In dieser geometrischen Übung stellen sie Koordinaten dar. Dimension3 bedeutet drei Komponenten. Die Richtung [1,0,0] zeigt entlang einer Achse, [0,1,0] entlang einer anderen und [-1,0,0] in die Gegenrichtung. Alle drei Vektoren sind Nichtnullvektoren mit Länge1. Die Cosine-Distanz wird deshalb an einem besonders einfachen Fall erklärt. Frage: Hat SQL hier Textverständnis erzeugt? Antwort: Nein, wir haben Zahlen vorgegeben und werden Mathematik anwenden. Echte Textembeddings erläutern wir erst nach der Übung.',
    sources: ['SRC-072', 'SRC-073'], refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md']
  },
  {
    title: 'Vorhersage für drei Richtungen', module: 'CUR-014',
    table: [
      ['Id', 'Vektor', 'Richtung zur Frage [1,0,0]'],
      ['1', '[1,0,0]', 'Gleiche Richtung'],
      ['2', '[0,1,0]', 'Senkrechte Richtung'],
      ['3', '[-1,0,0]', 'Entgegengesetzte Richtung']
    ],
    widths: [150, 310, 660],
    bottom: 'Vorhersage: Welcher Vektor soll bei aufsteigender Cosine-Distanz zuerst erscheinen?',
    notes: 'Lassen Sie zunächst nur die Rangfolge vorhersagen. Erwartete Reihenfolge: Id1, Id2, Id3. Begründen lassen: Gleiche Richtung ist näher als senkrechte und entgegengesetzte Richtung. Die verwendete Distanz ist eins minus Cosine-Ähnlichkeit. Für unsere Nichtnull-Einheitsvektoren sind die Ähnlichkeiten1,0,−1 und die Distanzen deshalb0,1,2. Diese Werte sind mathematische Sollwerte des ausdrücklich konstruierten Falls, kein protokollierter SQL-Lauf. Erklären Sie bei Bedarf die Begriffe senkrecht und Gegenrichtung verbal. Erst die folgende Query zeigt die Zuordnung zum SQL-Ausdruck. Es gibt hier keine realen Dokumentembeddings oder Relevanzurteile.',
    sources: ['SRC-073'], refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md']
  },
  {
    title: 'Eine vollständige read-only Vektorquery', module: 'CUR-014',
    code: "DECLARE @q VECTOR(3) = '[1,0,0]';\nSELECT Id, VECTOR_DISTANCE('cosine', @q, CAST(V AS VECTOR(3))) AS D\nFROM (VALUES (1,'[1,0,0]'),(2,'[0,1,0]'),(3,'[-1,0,0]')) d(Id,V)\nORDER BY D, Id;",
    bottom: 'DECLARE definiert den Fragevektor. VALUES liefert Kandidaten. SELECT berechnet und sortiert.',
    notes: 'Vollständiges kopierbares Lehrbeispiel:\nDECLARE @q VECTOR(3) = \'[1,0,0]\';\nSELECT Id, VECTOR_DISTANCE(\'cosine\', @q, CAST(V AS VECTOR(3))) AS D\nFROM (VALUES (1,\'[1,0,0]\'),(2,\'[0,1,0]\'),(3,\'[-1,0,0]\')) d(Id,V)\nORDER BY D, Id;\n\nDiese Query legt keine Tabelle an, schreibt keine Daten und ruft kein Modell auf. Die angeleitete Vorführung setzt die vorbereitete Engine 17.x voraus. Frage: Welche Zahl ist der Fragevektor? Antwort: @q. Welche Werte werden verglichen? Antwort: Die drei ausdrücklich angegebenen V-Zeichenfolgen nach der Konvertierung zu VECTOR(3). Die Funktion berechnet für jede Row eine exakte Distanz. ORDER BY D,Id legt die Reihenfolge fest und löst gleiche Distanzwerte nach Id auf. VECTOR_DISTANCE nutzt dafür keinen Vector Index. Die resultierenden Sollwerte stehen auf der nächsten Folie. Diese angeleitete Vorführung ist ein didaktischer read-only Ausdruck, keine neue katalogisierte Demo, keine bewertete Arbeitsheftaufgabe und keine zusätzliche Runtimefreigabe. Es gibt hierfür keine neue Rubrik. Die bestehenden bewerteten Aufgaben, Trainerlösungen und Bewertungsrubrik bleiben ausschließlich im Arbeitsheft.',
    sources: ['SRC-072', 'SRC-073'], refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md']
  },
  {
    title: 'Ergebnisbesprechung der Vektorquery', module: 'CUR-014',
    table: [
      ['Ausgabe Id', 'Cosine-Distanz D', 'Erklärung'],
      ['1', '0', 'Gleiche Richtung wie die Frage'],
      ['2', '1', 'Senkrecht zur Frage'],
      ['3', '2', 'Entgegengesetzte Richtung']
    ],
    widths: [230, 290, 600],
    bottom: 'Mathematische Sollwerte des festen Lehrfalls. Kleine Floating-Point-Abweichungen fachlich einordnen.',
    notes: 'Frage: Was bedeutet der erste Treffer? Antwort: Id1 ist unter der gewählten Metric und den vorgegebenen Zahlen am nächsten. Frage: Bedeutet Distanz0, dass ein Antworttext mit100Prozent Wahrscheinlichkeit wahr ist? Antwort: Nein. Die Distanz bezieht sich auf Zahlen im gewählten Raum und ist keine Antwortwahrscheinlichkeit. Die mathematischen Sollwerte0,1,2 sind direkt aus den drei Einheitsvektoren hergeleitet, keine erhobene Runtimeevidenz. Bei einem praktischen Lauf erst tatsächliche Rows und die sichtbare numerische Darstellung lesen. Sehr kleine Rundungsabweichungen werden begründet eingeordnet und dürfen keine geänderten Kandidaten oder andere Metric verbergen. Übergang: Für Textsuche muss noch erklärt werden, wo geeignete Zahlen überhaupt herkommen.',
    sources: ['SRC-073'], refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md']
  },
  {
    title: 'Text als Zahlen: ein Embedding', module: 'CUR-013 / CUR-016',
    blocks: [
      ['Embedding', 'Ein bestimmtes Modell bildet einen Text auf einen numerischen Vektor ab.'],
      ['Suche', 'Frage und Quellen erhalten vergleichbare Vektoren aus demselben Modellraum.'],
      ['Bewertung', 'Ähnliche Vektoren können passende Texte liefern. Die fachliche Relevanz müssen wir prüfen.']
    ],
    bottom: 'Unsere VECTOR(3)-Lehrwerte waren handgesetzt. Sie sind keine echten Textembeddings.',
    notes: 'Embedding bedeutet hier eine modellabhängige numerische Repräsentation von Text. Rückbezug zur Frage Wann verschwinden die Logeinträge: Ein geeignetes Textmodell könnte unterschiedliche Formulierungen nahe abbilden. Das ist eine zu bewertende Anwendungsidee, kein in dieser Einführung gemessenes Ergebnis. Die Frage und die Quellen müssen zum selben geeigneten Modellraum gehören. Gleiche Dimensionszahl allein genügt nicht. Modellversion, Dimension und Normalisierung werden bei gespeicherten Embeddings nachvollziehbar gehalten. Jede Koordinate ist nicht einfach einem verständlichen Wort zuzuordnen. Das Suchmodell und ein Modell zur Antwortformulierung können unterschiedliche Komponenten sein. Übergang: Der echte Modellpfad bringt zusätzliche praktische Hürden mit sich.',
    sources: ['SRC-087'], refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md', 'Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md']
  },
  {
    title: 'Zusätzliche Hürden eines echten Modellpfads', module: 'CUR-016 / CUR-018',
    table: [
      ['Hürde', 'Vorbereitete Lösung', 'Sichtbare Prüfung'],
      ['Modell', 'Geeignete Version und Dimension festlegen.', 'Der Vektor passt zum erwarteten Modellraum.'],
      ['Verbindung', 'Verschlüsselten Transport und Zertifikat prüfen.', 'Der erlaubte Dienst ist aus dem Aufrufer erreichbar.'],
      ['Kosten', 'Menge der Requests und Wiederholungen begrenzen.', 'Verbrauch und Abbruchgrenze bleiben nachvollziehbar.'],
      ['Datenschutz', 'Erlaubte Daten und Dienstverarbeitung klären.', 'Nur freigegebener Kontext verlässt seine Grenze.']
    ],
    widths: [190, 465, 465],
    notes: 'Ein Provider ist der Dienst, der das vorbereitete Modell ausführt. Im direkten SQL-External-Modelpfad verlangt Microsoft einen HTTPS-Endpunkt mit TLS, einem Verfahren für verschlüsselten Transport. Diese Prüfung ist mehr als die Frage, ob ein Dienst im Browser antwortet. Bei Containern bezeichnet localhost den jeweiligen Ausführungskontext. Rechte für Modellnutzung bleiben von Einrichtungs- und Credentialrechten getrennt. Ein lokal laufendes Modell benötigt ebenfalls Prüfung von Modelllizenz, Ressourcen und Eingaben. Das bedeutet nicht, dass sämtliche Daten automatisch das Gerät verlassen. Der jeweilige Datenfluss entscheidet. Kostenangaben, Retention und Verarbeitung unterscheiden sich nach Modell und Dienst. Es gibt keine allgemeine Nullkosten- oder Datenschutzgarantie. Diese Folie erklärt einen späteren Pfad und startet keinen Modellcall, keine Cloudbereitstellung und keine Instanzaktivierung. Bei fehlenden Voraussetzungen bleiben wir beim Offlineeinstieg. Frage: Welche dieser Hürden entfällt in unserer festen Zahlenübung? Antwort: Ein Modellrequest und dessen Providerkonfiguration sind dort nicht beteiligt.',
    sources: ['SRC-080', 'SRC-082', 'SRC-088'], refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_MODEL_PATHS.md', 'Documentation/Research/SQL_SERVER_2025_AI_FEATURE_MATRIX.md']
  },
  {
    title: 'Ein Textausschnitt braucht seine Herkunft', module: 'CUR-015 / CUR-017',
    blocks: [
      ['Quelltext', 'Dokument 2, v2: MOD_A bewahrt Protokolle sieben Tage auf.'],
      ['Ausschnitt', 'Ein Chunk ist ein abgegrenzter Textbereich. Er bleibt mit Dokument und Fassung verbunden.'],
      ['Prüfung', 'Wir können zeigen, wo die gefundene Information steht und ob diese Fassung aktuell ist.']
    ],
    notes: 'Für den kurzen Einstiegssatz kann der gesamte Satz ein Textbereich sein. Bei längeren Dokumenten entstehen mehrere Chunks. Provenienz bedeutet nachvollziehbare Herkunft und Verarbeitung. Dazu gehören Dokumentkennung, Fassung, Reihenfolge, Anfang und Länge des Bereichs. Diese Felder werden in den anschließenden Demos konkret untersucht. Die SQL-Funktion AI_GENERATE_CHUNKS benötigt mindestens Compatibility Level170. Ihr FIXED-Verfahren verwendet Zeichenbereiche und ist kein Modelltokenizer. Frage: Was verlieren wir, wenn wir nur den Satz und seine Zahlenliste speichern? Antwort: Die Verbindung zur überprüfbaren Quelle und ihrer aktuellen Fassung. Übergang: Ein solcher erlaubter Quellenausschnitt kann Kontext für einen Antwortentwurf bilden.',
    sources: ['SRC-079'], refs: ['Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md']
  },
  {
    title: 'Eine Antwort mit abgerufenem Quellenkontext', module: 'CUR-017',
    blocks: [
      ['Suche', 'Die Anwendung findet zur Frage erlaubte, aktuelle Quellen.'],
      ['Kontext', 'Sie gibt passende Ausschnitte zusammen mit der Frage an die Antwortstufe.'],
      ['Antwort', 'Ein Antwortentwurf nennt seine Belege. Die Anwendung prüft die stützende Quelle.']
    ],
    bottom: 'Dieser Ablauf heißt Retrieval-Augmented Generation, kurz RAG.',
    notes: 'RAG bezeichnet die Verbindung von abgerufenem Kontext und generativer Antwort. Retrieval heißt hier das Suchen und Bereitstellen von Quellen. Die Architektur wurde bereits mit den getrennten Rollen vorbereitet. Frage: Trainieren wir das Modell mit jeder neuen Frage automatisch neu? Antwort: Nein, die Anwendung kann dem vorbereiteten Modell neuen Kontext bereitstellen. Sie muss dabei sowohl Zugriffsrechte als auch Quellenstand beachten. Ein erlaubter Text allein stützt noch nicht jeden erzeugten Satz. Der kurze folgende Fall arbeitet mit ausdrücklich vorgegebenen Antworten, damit die Gruppe die Belegentscheidung gemeinsam prüfen kann. Das ist ein Offline-Kontrollfall und keine Livegeneration. Übergang: Wir lesen Frage, Quelle und Antwort nebeneinander.',
    refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md', 'Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md']
  },
  {
    title: 'Eine belegbare Antwort im Wissensbasisfall', module: 'CUR-017',
    table: [
      ['Bestandteil', 'Sichtbarer Inhalt'],
      ['Frage', 'Wie lange bleiben die Protokolle von MOD_A erhalten?'],
      ['Gelieferte Quelle', 'Dokument 2, v2: MOD_A bewahrt Protokolle sieben Tage auf.'],
      ['Fester Antwortentwurf', 'Sieben Tage. Beleg: Dokument 2, Fassung v2.']
    ],
    widths: [320, 800],
    notes: 'Lassen Sie die Gruppe die Antwort freigeben oder zurückweisen und die Entscheidung an einem sichtbaren Beleg festmachen. Erwartete Entscheidung für diesen festen Lehrfall: Die Fristaussage ist durch die aktuelle erlaubte Quelle gestützt. Frage: Welche zusätzliche Behauptung wäre noch nicht belegt? Antwort: Eine Begründung, warum die Frist sieben Tage beträgt. Unser Dokument nennt keinen Grund. Die Existenz einer Dokumentkennung genügt nicht, wenn der zitierte Satz außerhalb des tatsächlich gelieferten Kontexts liegt. Der Antwortentwurf ist hier vorgegeben und nicht mit einem Modell erzeugt. Übergang: Jetzt prüfen wir dieselbe Regel an einer falschen und an einer unbeantwortbaren Frage.',
    refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md', 'Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md']
  },
  {
    title: 'Falsche und fehlende Antworten erkennen', module: 'CUR-017 / CUR-022',
    table: [
      ['Frage oder Antwortentwurf', 'Gemeinsame Entscheidung'],
      ['MOD_A bewahrt Protokolle 14 Tage auf.', 'Falsch zum gelieferten Beleg von sieben Tagen.'],
      ['Warum sind es genau sieben Tage?', 'Der Grund fehlt in der Quelle. Keine Erklärung erfinden.'],
      ['Ohne passende Quelle bleibt die Antwort leer.', 'Eine begründete Nichtantwort ist nachvollziehbarer.']
    ],
    widths: [560, 560],
    notes: 'Geben Sie dieselbe aktuelle Quelle aus Dokument2 vor. Erst die falsche14-Tage-Antwort besprechen. Frage: Reicht eine korrekte Quellenkennung für diese Antwort? Antwort: Nein, ihr Inhalt widerspricht dem Quelleninhalt. Danach die Warum-Frage behandeln. Der passende feste Nichtantworttext lautet: Die aktuelle Anleitung nennt sieben Tage, erklärt den Grund aber nicht. Die Gruppe soll zwischen falscher Antwort und fehlender Information unterscheiden. Eine leere Ausgabe allein erklärt keine dieser Situationen. Eine begründete Nichtantwort macht die fehlende Evidenz sichtbar. Diese Lehrfälle greifen die späteren Offline-RAG-Kontrollen auf, ersetzen aber deren vollständigen Ergebnisvertrag nicht. Übergang: Mit diesen Kriterien können wir nun die konkreten SQL-Demos verstehen.',
    refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md', 'Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_TRAINER_GUIDE.md']
  },
  {
    title: 'Vorbereitung auf die konkreten Demos', module: 'CUR-013 / CUR-014 / CUR-017 / CUR-018',
    blocks: [
      ['Zahlen verstehen', 'Eine Vektorquery vergleicht Werte. Ihre Distanz beweist noch keine richtige Antwort.'],
      ['Quellen prüfen', 'Dokument, Fassung und erlaubter Kontext gehören zum Ergebnis.'],
      ['Nächster Schritt', 'Wir untersuchen nun Datentypen, Suche, Quellen und Rechte an den vorbereiteten Offline-Demos.']
    ],
    notes: 'Kurzer Verständnischeck vor dem Übergang: Woher stammen unsere ersten drei Vektoren? Antwort: Aus ausdrücklich gesetzten Geometriewerten. Was liefert ein echtes Embedding-Modell? Antwort: Eine modellabhängige numerische Repräsentation der Eingabe. Was prüft unsere sieben-Tage-Antwort? Antwort: Eine konkrete aktuelle Quellenstelle im erlaubten Kontext. Was tun wir bei fehlendem Modellzugang? Antwort: Den lokalen Offlinepfad und seine begrenzten Lernziele nutzen. Die folgenden vorhandenen Folien führen die konkreten Demo-IDs, Voraussetzungen, Ergebnisverträge und offenen Vertiefungspfade ein. Keine zusätzlichen Modell-, Cloud- oder Hosteffekte aus den Einführungscodebeispielen ableiten. Lehrperson fragt vor dem Demostart nach tatsächlichem Ziel, Preflight und dokumentiertem Cleanup. Lehrzeiten und Lernwirksamkeit dieser neuen Einsteigerfolge sind noch nicht erprobt.',
    refs: ['Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_TRAINER_GUIDE.md', 'Documentation/HowTo/DEMO_EXECUTION_GUIDE.md']
  }
];
