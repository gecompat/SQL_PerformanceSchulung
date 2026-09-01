# Privacy- und Metadaten-Prüfverfahren

| Merkmal | Wert |
|---|---|
| Arbeitspakete | `W0-002`, `TST-002` |
| Status | `VALIDATED` |
| Stand | 2026-07-26 |
| Geltung | alle neu erstellten, geänderten, importierten, exportierten oder versionierten Artefakte |
| Zulässige reale Namensangabe | `Gerhard Pisch` |
| Automatisiertes Werkzeug | `Tests/Static/validate_privacy_metadata.py` |

## 1. Ziel

Das Verfahren verhindert, dass reale Personen-, Kunden-, Firmen-, Organisations-, Umgebungs- oder proprietäre interne Informationen unbeabsichtigt in das Repository gelangen. Es erfasst sichtbare Inhalte, strukturierte Metadaten, eingebettete Objekte und bildbasierte Informationen.

Eine erfolgreiche Textsuche allein ist kein Freigabenachweis. Office-Artefakte und Exporte benötigen zusätzlich eine Paket-, Metadaten- und Sichtprüfung.

## 2. Prüfanlass

Die Prüfung ist vor jeder Datei- oder Git-Operation erforderlich, wenn ein Artefakt neu erstellt, verändert, importiert, exportiert, verpackt, entpackt, übertragen oder versioniert werden soll. Bei unverändertem, bereits über Hash freigegebenem Artefakt darf auf den vorhandenen Nachweis verwiesen werden.

Wenn reale oder interne Informationen vorhanden sein können und keine ausdrückliche Freigabe dokumentiert ist, erhält das Artefakt den Status `BLOCKED`. Es wird weder geschrieben noch in Git übernommen.

## 3. Statusmodell

| Status | Bedeutung |
|---|---|
| `PENDING` | Prüfung noch nicht vollständig |
| `PASS` | alle zutreffenden Prüfungen erfolgreich; keine unzulässigen Angaben gefunden |
| `APPROVED_EXCEPTION` | konkrete reale Angabe ausdrücklich freigegeben und im Nachweis benannt |
| `BLOCKED` | unzulässige oder nicht eindeutig bewertbare Information gefunden |
| `RETIRED` | Artefakt wurde ersetzt und darf nicht erneut als aktive Quelle importiert werden |

Die einzige allgemeine Ausnahme dieses Projekts ist die Namensangabe `Gerhard Pisch`. Sie gilt nicht automatisch für Kontakt-, Firmen-, Organisations- oder Umgebungsangaben.

## 4. Prüfschichten

### 4.1 Herkunft und Dateigrenze

Vor der Inhaltsprüfung werden Quelle, Zielpfad, Dateityp, Größe, SHA-256-Hash und beabsichtigte Projektrolle erfasst. Archive werden als Container und zusätzlich auf Ebene ihrer Einträge geprüft. Nicht neutralisierte Uploads dürfen nicht zum Repository-Artefakt erklärt werden.

### 4.2 Sichtbarer und textueller Inhalt

Zu prüfen sind Fließtext, Tabellen, Diagrammbeschriftungen, Formeln, Code, Kommentare, Speaker Notes, Fußzeilen, Kopfzeilen, Hyperlinktexte, Alt-Text, Dateinamen und Pfadangaben. Die Suche umfasst insbesondere:

- nicht freigegebene Personen-, Firmen- und Organisationsnamen,
- E-Mail-Adressen, Telefonnummern und Postanschriften,
- Host-, Instanz-, Datenbank-, Benutzer- und Mandantenkennungen,
- interne URLs, Repository-Pfade, Shares und lokale Dateipfade,
- Secrets, Tokens, Connection Strings und Zertifikatsbezüge,
- Logos, Markenkennzeichen und alte Vorlagenbezeichnungen.

Treffer werden im Prüfbericht nur als Kategorie und Anzahl dokumentiert. Schutzwürdige Fundwerte werden nicht in neue Log- oder Reportdateien kopiert.

### 4.3 Office-Paket und Metadaten

Für PPTX, DOCX und XLSX werden mindestens folgende Bestandteile geprüft:

- `docProps/core.xml`, `docProps/app.xml` und Custom Properties,
- Slide Masters, Layouts, Notes Masters, Notes, Kommentare und Alt-Text,
- Beziehungen, externe Links, `mailto`-Links und eingebettete Dateien,
- Medien, Vorschaubilder, OLE-Objekte, ActiveX, Makros und Custom XML,
- digitale Signaturen, Zertifikatsinformationen und Vorlagenpfade,
- Author, Last Modified By, Company, Manager, Template und ähnliche Felder.

Nicht benötigte eingebettete Objekte werden physisch aus dem Office-Paket entfernt. Eine optische Überdeckung gilt nicht als Entfernung.

### 4.4 Bilder, Screenshots und Videos

Jedes Rasterbild, Vorschaubild, Video und jede Animation wird visuell geprüft. Bei texttragenden Bildern ist zusätzlich OCR oder eine gleichwertige Texterkennung erforderlich. Zu kontrollieren sind insbesondere Logos, Taskleisten, Benutzerkennungen, Server- und Datenbanknamen, Browserleisten, Fensterüberschriften und Diagnoseausgaben.

Ein Medium mit nicht neutralisierbaren internen Angaben wird entfernt. Ein Ersatz darf nur synthetische Daten verwenden. Für dieses Projekt werden keine dekorativen Bilder erzeugt, wenn sie keinen fachlichen Informationswert besitzen.

### 4.5 Code, Logs und Diagnoseausgaben

Quellcode wird auf reale Objekt-, Host-, Benutzer- und Pfadnamen sowie eingebettete Zugangsdaten geprüft. Veröffentlichte Erwartungsresultate müssen synthetisch sein. Diagnostisch erzeugte reale Resultsets dürfen während einer lokalen Prüfung angezeigt werden, werden jedoch nicht als Repository-Artefakt gespeichert.

Öffentliche Microsoft-Beispieldatenbanken gelten nicht als vertrauliche Daten. Abhängigkeiten von ihnen werden trotzdem vermieden, wenn die Demo eine isolierte synthetische Testdatenbank erzeugen kann.

### 4.6 Render- und Exportprüfung

Präsentationen und Dokumente werden vollständig gerendert. Jede Seite beziehungsweise Folie wird auf unzulässige Kennzeichen, abgeschnittene Inhalte, unerwartete Masterelemente und durch Export sichtbar gewordene Metadaten geprüft. Kontaktbögen unterstützen die Übersicht, ersetzen aber nicht die Einzelprüfung in lesbarer Größe.

PDF-, Bild- und Handout-Exporte werden als eigenständige Artefakte geprüft, weil Exporter zusätzliche Metadaten oder Vorschaubilder erzeugen können.

## 5. Freigabenachweis

Der Nachweis enthält mindestens:

| Feld | Inhalt |
|---|---|
| Artefakt | Repository-Pfad oder vorgesehener Zielpfad |
| Identität | SHA-256-Hash und Dateigröße |
| Umfang | Seiten, Folien, Archiveinträge oder relevante Dateien |
| Prüfschichten | ausgeführte Text-, Paket-, Metadaten-, Medien- und Renderprüfungen |
| Ergebnis | `PASS`, `APPROVED_EXCEPTION`, `BLOCKED` oder `RETIRED` |
| Ausnahme | konkret freigegebene Angabe und Geltungsbereich |
| Prüfbasis | eingesetzte Prüfer oder Skripte und deren Version, soweit relevant |
| Datum | Prüfdatum in ISO-Format |

Prüfberichte enthalten keine Fundwerte, die selbst schutzwürdig sind. Für reproduzierbare Identität werden Hashes und aggregierte Zähler verwendet.

## 6. Abbruch- und Korrekturverfahren

Bei einem Fund wird die Verarbeitung vor dem Schreiben oder der Git-Operation angehalten. Anschließend gilt genau einer der folgenden Pfade:

1. Die Angabe wird vollständig entfernt oder durch synthetische Information ersetzt.
2. Das betroffene Medium oder Artefakt wird verworfen.
3. Eine konkrete ausdrückliche Freigabe wird eingeholt und als `APPROVED_EXCEPTION` dokumentiert.

Nach jeder Korrektur werden alle betroffenen Prüfschichten erneut ausgeführt. Bei Office-Dateien ist zusätzlich zu bestätigen, dass gelöschte Medien, Beziehungen und Metadaten nicht mehr im Paket enthalten sind.

## 7. Projektbezogene Anwendung

| Artefakt | Ergebnis | Evidenz |
|---|---|---|
| neutralisiertes Referenzarchiv unter `Presentations/old` | `PASS` | Hash und Umfang im Quellenmanifest; Firmen-, Kontakt-, interne System- und Brandingangaben entfernt |
| aktives 102-Folien-Masterdeck unter `Presentations` | `PASS` mit zulässiger Namensangabe | 102/102 Folien sowie die Profile `BASIS` 41, `STANDARD` 66 und `VERTIEFUNG` 102 gerendert; Office-Paket, Metadaten, Privacy und Branding geprüft; nur `Gerhard Pisch` als reale Angabe |
| Vertiefungsblöcke `ADV-009` bis `ADV-011`, Anzeigepositionen 84 bis 101 | `PASS` textuell, paketseitig und visuell | Folien deterministisch aus der bestehenden Vorlage erzeugt; vollständiger PowerPoint-Render und Einzelprüfung in `ADV_010_FINAL_ACCEPTANCE_REVIEW.md` und `W_PRS_001_TEACHING_RELEASE.md`; Notizen führen Quellen ausschließlich als `SRC-`-IDs ohne URL |

Die visuelle Einzelprüfung aller 102 Masterfolien und der drei Tiefenprofile ist abgeschlossen. Sie bleibt methodisch von der automatisierten Privacy-Prüfung getrennt: Der Scanner prüft personenbezogene und kundenbezogene Angaben, während der Rendernachweis Umbruch und Lesbarkeit im Vortrag bewertet.

Die fachliche Freigabe eines Artefakts ist von der Privacy-Freigabe getrennt. `PASS` bestätigt ausschließlich die hier definierten Datenschutz- und Metadatenanforderungen.

## 8. Automatisierte Prüfung durch TST-002

`Tests/Static/validate_privacy_metadata.py` ist ein User-defined Tool des Projekts und verwendet ausschließlich die Python-Standardbibliothek. Der Workflow `.github/workflows/privacy-metadata.yml` führt Curriculumprüfung, Scanner-Selbsttests und Repositoryscan ohne SQL-Server-Start aus.

Der Scanner prüft automatisiert:

- Textdateien auf hochsignifikante Kontakt-, Pfad-, interne URL-, private IP-, Secret- und Legacy-Identifier-Muster,
- Office-Pakete und ZIP-Archive auf Integrität, Pfadtraversal, Verschlüsselung, Größenbegrenzungen und verschachtelte Inhalte,
- Office-Eigenschaften auf nicht freigegebene Identitätsmetadaten,
- Pakete auf Makros, ActiveX, OLE-/Embedding-Inhalte, digitale Signaturen und Custom XML,
- eigenständige oder eingebettete Medien auf die Notwendigkeit manueller Sichtprüfung,
- unveränderte, bereits freigegebene Altartefakte ausschließlich über ihren dokumentierten SHA-256-Hash.

Der Scanner meldet ausschließlich Repository-Pfad, Finding-Kategorie und Anzahl. Der konkrete Fundwert wird weder auf Standard Output noch in das kurzlebige Diagnoseartefakt geschrieben. Ein Scannerfehler erzeugt `FAIL`; nicht automatisierbare Medien- oder Binary-Prüfungen werden als blockierende Kategorie ausgegeben.

### 8.1 Grenzen

TST-002 ersetzt keine visuelle Einzelprüfung, kein OCR für texttragende Bilder und keinen Rendervergleich. Medieninhalte werden automatisiert erkannt und blockiert, sofern sie nicht durch einen unveränderten hashgebundenen Nachweis gedeckt sind. Neue oder geänderte Medien benötigen weiterhin die Prüfschichten 4.4 und 4.6.

Heuristische Muster können weder jede proprietäre Bezeichnung erkennen noch jeden zufälligen Zeichenwert zuverlässig als Secret klassifizieren. Der Scanner ist deshalb ein verpflichtendes technisches Gate, aber kein alleiniger Datenschutzfreigabenachweis.

### 8.2 Diagnoseartefakt

Bei einem fehlgeschlagenen Workflow wird für höchstens einen Tag ein Artefakt `privacy-categories` erzeugt. Es enthält nur kategorisierte Findings ohne Fundwerte. Nach Korrektur und erfolgreicher Wiederholung ist dieses Artefakt nicht Bestandteil des Releasepakets.

## 9. Abnahmekriterien

### 9.1 W0-002

- Prüfanlass, Statusmodell und Abbruchregel sind eindeutig.
- Text, Office-Paket, Metadaten, Bilder, Medien, Code und Exporte sind abgedeckt.
- Die zulässige Namensausnahme ist eng begrenzt.
- Schutzwürdige Fundwerte werden nicht in Prüfberichte übernommen.
- Hashbasierte Wiederverwendung vorhandener Nachweise ist geregelt.
- Referenzarchiv und aktiver Foliensatz besitzen einen nachvollziehbaren aktuellen Nachweis.

### 9.2 TST-002

- Scanner und Selbsttests sind ohne Drittanbieterbibliothek ausführbar.
- Positive synthetische Findings werden kategorisiert, aber ihre Werte nicht ausgegeben.
- Office-Metadaten, Makros, eingebettete Objekte, Archive und Medien-Gates werden geprüft.
- Der vollständige Repositoryscan ist im Pull Request erfolgreich.
- Manuelle Sicht-, OCR- und Renderprüfungen bleiben als getrennte Pflichtschichten dokumentiert.
