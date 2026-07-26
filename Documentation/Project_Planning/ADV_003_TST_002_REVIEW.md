# Review – ADV-003 und TST-002

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-07-26 |
| Pull Request | `#17` |
| Ausgangsstand | `cbe6ca52229fe57f5043595d68fbdcbb36c00045` |
| Arbeitspakete | `ADV-003`, `TST-002` |
| PowerPoint geändert | nein |
| SQL-Demos geändert | nein |

## 1. ADV-003 – Curriculum und Traceability

Die 39 Claims aus `ADV-002` wurden in neun beobachtbare Vertiefungslernziele überführt:

- `LO-M02-08` bis `LO-M02-11` für Planmechanik, Operatorinteraktion, Row Goals und IQP,
- `LO-M03-07` und `LO-M03-08` für Anwendungskontext und Parametrisierungsstrategien,
- `LO-M06-07` und `LO-M06-08` für Workspace Memory und zeitlichen Evidenz-Scope,
- `LO-M07-04` für die mehrhypothetische Incident-Diagnose.

Die Curriculumarchitektur besitzt damit 52 beobachtbare Lernziele. Der Kernpfad und die Modulfolge M00 bis M07 bleiben unverändert. Alle neuen Lernziele sind `VERTIEFUNG`.

Die Traceability-Matrix enthält weiterhin genau 84 aktive Claims für 84 aktive Folien. Ergänzend besitzt jeder Claim `ADV-CLM-001` bis `ADV-CLM-039` genau eine Lernziel-, Quellen-, Demo-/LAB- und Testprofilzuordnung. Die aktive Folie bleibt bis `ADV-009` und `PRS-012` bewusst leer; `PLANNED` wird nicht als Implementierungs- oder Runtimefreigabe behandelt.

Gate V0 und Gate V1 sind erfüllt. `ADV-004` und `ADV-005` können unabhängig und parallel beginnen.

## 2. TST-002 – Privacy- und Metadatenprüfung

`Tests/Static/validate_privacy_metadata.py` ist ein User-defined Tool auf Basis der Python-Standardbibliothek. Es untersucht:

- Textdateien auf hochsignifikante Kontakt-, Pfad-, interne URL-, private IP-, Secret- und Legacy-Identifier-Muster,
- Office-Pakete und Archive auf Integrität, Pfadtraversal, Verschlüsselung, Größenlimits und verschachtelte Inhalte,
- Office-Eigenschaften auf nicht freigegebene Identitätsmetadaten,
- Pakete auf Makros, ActiveX, OLE-/Embedding-Inhalte, Signaturen und Custom XML,
- Medien und andere Binärartefakte auf notwendige manuelle Sichtprüfung,
- unveränderte freigegebene Altartefakte über dokumentierte SHA-256-Hashes.

Der Scanner gibt keine Fundwerte aus. Ein Finding enthält ausschließlich Repository-Pfad, Kategorie und Anzahl. Das kurzlebige Workflow-Artefakt `privacy-categories` verwendet dasselbe reduzierte Format und wird einen Tag aufbewahrt.

Die initiale Repositoryausführung erkannte mehrere False Positives: Versionsfolgen wurden als Telefonnummern und das Lesen einer Passwort-Umgebungsvariable als hartcodiertes Secret klassifiziert. Die Heuristiken wurden auf explizite Telefonkontexte und tatsächliche Passwortliterale beschränkt. Die bereits geprüfte aktive Präsentation wird nur bei exakt passendem SHA-256-Hash bezüglich der vorhandenen Metadaten- und Medienfreigabe wiederverwendet.

TST-002 ersetzt keine visuelle Einzelprüfung, kein OCR und keinen Rendervergleich. Neue oder geänderte Medien bleiben bis zur manuellen Freigabe blockiert.

## 3. Automatisierte Abnahme

Der Workflow `Curriculum and privacy validation` prüft:

1. `validate_adv_003_curriculum.py`,
2. `test_privacy_metadata_scanner.py`,
3. den vollständigen Repositoryscan.

Der finale Stand bestand zusätzlich die bestehenden Workflows:

- `Framework contracts`,
- `Presentation refine claims`,
- `W2-001 legacy example classification`, soweit durch die geänderten Steuerungsdateien ausgelöst.

Es wurde keine SQL-Server-Runtime-Matrix ausgeführt, weil keine SQL-Datei und keine Runtime-Implementierung verändert wurde. Ein PowerPoint-Render war nicht erforderlich, weil das Masterdeck unverändert blieb.

## 4. Datenschutzstatus

Alle neu erzeugten Inhalte sind firmenneutral und synthetisch. Scanner-Selbsttests setzen Testwerte zur Laufzeit aus Fragmenten zusammen und geben sie im Fehlerreport nicht aus. Es wurden keine realen Host-, Benutzer-, Kontakt-, Kunden-, Zugangs- oder Diagnosedaten in Repository-Artefakte übernommen.

## 5. Nächster ausführbarer Schritt

Die nächste fachliche Welle sollte `ADV-004` und `ADV-005` als getrennte, parallelisierbare Designpakete bearbeiten. Parallel bleiben `PRS-012`/`TST-011`, die fachlich geschnittene Neutralisierung der W2-A-Kandidaten aus `W2-002` sowie die Query-Store-/XE-Pilotvalidierung ausführbar.
