# ADV-009 · Übernahme der Vertiefungsfolien in das aktive Deck

| Feld | Wert |
|---|---|
| Arbeitspaket | `ADV-009` |
| Status | `IMPLEMENTED_FOR_REVIEW` |
| Datum | 2026-08-02 |
| Grundlage | `Documentation/Curriculum/ADV_009_SLIDE_SPECIFICATION_M03.md`, `Documentation/Curriculum/ADV_009_SLIDE_SPECIFICATION_M03_LO08.md` |
| Entscheidungen | `DEC-057`, `DEC-058` (Nachfolger von `DEC-053`) |
| Deck | `Presentations/Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx` |
| Folienumfang | 84 → 94 |
| Werkzeug | `Tools/build_adv009_slides.py` |
| Prüfer | `Tests/Static/validate_adv009_deck_integration.py` |

## 1. Ausgangslage und Freigabeänderung

`DEC-053` hatte festgelegt, dass Präsentationserweiterungen zuerst als versionierte Folienspezifikation entstehen und die Übernahme in das Deck ein getrennter Schritt bleibt. Der Grund war kein fachlicher, sondern ein Freigabegrund: Das aktive Deck ist in `Tests/Static/validate_privacy_metadata.py` über `APPROVED_ACTIVE_DECK` per SHA-256 freigegeben, und eine unangekündigte Bearbeitung hätte diese Freigabe stillschweigend entwertet.

Der Auftraggeber hat die Bearbeitung der `.pptx` ausdrücklich freigegeben. Damit entfällt die Sperre, nicht jedoch das Schutzziel. `DEC-057` hält deshalb fest, unter welchen Bedingungen die Bearbeitung zulässig ist: additiv, deterministisch reproduzierbar über ein versioniertes Werkzeug, mit kontrollierter Erneuerung der Prüfsumme an allen hinterlegten Stellen und mit einem eigenen Prüfer für die Zuordnung.

## 2. Platzierung

Die zehn Folien bilden einen geschlossenen Vertiefungsblock unmittelbar vor der Schlussfolie (`DEC-058`).

| Alternative | Bewertung |
|---|---|
| Einschub in Modul 3 nach Anzeigeposition 47 | Verschiebt 38 Registerzeilen, 38 Matrixzeilen und mehrere Dokumentverweise auf Foliennummern. Kein fachlicher Gewinn gegenüber einem Anhang, aber hohes Risiko stiller Inkonsistenzen. |
| Anhang vor der Schlussfolie | Basissatz bleibt vollständig stabil. Genau ein Claim (`CLM-084`) musste umnummeriert werden, weil er auf der Schlussfolie sitzt. Umgesetzt. |
| Anhang nach der Schlussfolie | Die Schlussfolie wäre nicht mehr letzte Folie. Fachlich unsauber, verworfen. |

Die einzige Änderung an bestehenden Folien ist der Nenner der Fußzeilenpaginierung (`n / 84` → `n / 94`). Sie erfolgte über ein gezieltes Muster auf den Fußzeilentext, das den Literaltext „Session 84“ auf Anzeigeposition 66 nachweislich nicht berührt.

## 3. Abweichung zwischen Folienteil und Anzeigeposition

Die neuen Folien liegen als Paketteile `slide85.xml` bis `slide94.xml` im Archiv, erscheinen aber an den Anzeigepositionen 84 bis 93; die Schlussfolie bleibt Teil `slide84.xml` an Anzeigeposition 94. Die Reihenfolge ergibt sich ausschließlich aus `p:sldIdLst` in `ppt/presentation.xml`, nicht aus den Teilenamen.

Diese Abweichung ist bewusst in Kauf genommen. Eine Umbenennung der Schlussfolie hätte deren Beziehungen, ihre Notizfolie und die in `Tests/Static/validate_w2_007_presentation.py` auf Teilenamen verankerten Prüfungen der Folien 32, 34, 42 und 43 berührt. Die Zuordnung ist stattdessen in `Documentation/Inventories/SLIDE_STATEMENT_REGISTER.md` je Folie mit Teilename und Anzeigeposition geführt und wird durch den neuen Prüfer gegen `p:sldIdLst` abgeglichen.

| Stabile ID | Anzeigeposition | Folienteil | Claim |
|---|---|---|---|
| `SLD-M03-101` | 84 | `slide85.xml` | `ADV-CLM-014` |
| `SLD-M03-102` | 85 | `slide86.xml` | `ADV-CLM-013` |
| `SLD-M03-103` | 86 | `slide87.xml` | `ADV-CLM-015` |
| `SLD-M03-104` | 87 | `slide88.xml` | `ADV-CLM-016` |
| `SLD-M03-105` | 88 | `slide89.xml` | `ADV-CLM-013` bis `ADV-CLM-016` |
| `SLD-M03-111` | 89 | `slide90.xml` | – |
| `SLD-M03-112` | 90 | `slide91.xml` | `ADV-CLM-017` |
| `SLD-M03-113` | 91 | `slide92.xml` | `ADV-CLM-018` |
| `SLD-M03-114` | 92 | `slide93.xml` | `ADV-CLM-018` |
| `SLD-M03-115` | 93 | `slide94.xml` | `ADV-CLM-017`, `ADV-CLM-018` |

Die kanonischen Demos sind `QRY-013` für die Anzeigepositionen 84 bis 88 und `QRY-004` für 89 bis 93.

## 4. Erzeugung

`Tools/build_adv009_slides.py` erzeugt die Erweiterung aus dem Basisdeck. Das Werkzeug arbeitet ausschließlich mit der Standardbibliothek (`zipfile`, `xml.etree.ElementTree`); `python-pptx` ist im Projekt bewusst nicht verfügbar.

Eigenschaften:

- **Vorlagengebunden.** Anzeigeposition 32 dient als Vorlage. Ihre Familie besitzt einheitlich vier Aufzählungsabsätze mit je einem Textlauf, sodass reine Textersetzung ohne strukturellen Eingriff genügt.
- **Deterministisch.** Zeitstempel neuer Archiveinträge sind festgelegt, Bezeichner werden über `uuid5` aus stabilen Namen abgeleitet, Beziehungskennungen über einen Hash des Teilenamens. Zwei Läufe aus unveränderten Kopien erzeugten byteweise identische Archive.
- **Idempotent.** Ein Lauf gegen ein bereits erweitertes Deck bricht kontrolliert ab; `--check` meldet den Zustand ohne Fehlschlag und ist als Dauerprüfung in der Werkbank eingebunden.
- **Atomar.** Das Archiv wird als `.pptx.tmp` geschrieben und erst nach vollständigem Aufbau an die Zielposition verschoben.

Erneuerte Prüfsumme:

| Feld | Vorher | Nachher |
|---|---|---|
| SHA-256 | `3ad528c2eb6ad531c1bbf5a26bee17e35004f764357b5061c9fc15bc04807a18` | `8f8ccd9ffce73cf4c09220de27e74303644642c31a4204f1921648cba86ac4e6` |
| SHA-1 | `48e479c56691c6fb5b91818e59ab7c05bb18dbed` | `994eba18625605a491f1082b297d13d55e4410a2` |

Der Wert wurde an allen vier hinterlegten Stellen fortgeschrieben: `Tests/Static/validate_privacy_metadata.py`, `Documentation/Inventories/SLIDE_STATEMENT_REGISTER.md`, `Documentation/Inventories/SOURCE_MANIFEST.md` und `Documentation/Project_Planning/W2_007_REFINE_CLAIMS_REVIEW.md`.

## 5. Prüfung

`Tests/Static/validate_adv009_deck_integration.py` prüft das Archiv auf Lesbarkeit, die Anzeigereihenfolge gegen `p:sldIdLst`, je Vertiefungsfolie das Vertiefungs-Modullabel, genau einen Leitabsatz, genau vier Aufzählungsabsätze und die zutreffende Fußzeilenpaginierung, je Notizfolie den unveränderten Folienmarker, die Kennzeichnungszeile und das Tiefenprofil, ferner die Unverrücktheit der Basisfolien und der Schlussfolie sowie die Übereinstimmung von Register, Traceability-Matrix, Quellenmanifest, Datenschutzprüfer und beiden Spezifikationen. Verallgemeinernde Formulierungen im sichtbaren Text werden gegen eine Sperrliste geprüft.

Der Prüfer wurde negativ getestet. Fünf gezielte, jeweils zurückgenommene Mutationen wurden erkannt: falsche Foliennummer im Register, unvollständige Folienliste eines Claims in der Traceability-Matrix, auf `SPECIFIED` zurückgesetzter Spezifikationsstatus, abweichende Prüfsumme im Datenschutzprüfer und ein veränderter Folienmarker in einer Notizfolie.

Angepasste bestehende Prüfer:

| Prüfer | Änderung |
|---|---|
| `validate_w2_007_presentation.py` | `SLIDE_COUNT` auf 94; die auf Teilenamen verankerten Inhaltsprüfungen bleiben unverändert gültig. |
| `validate_privacy_metadata.py` | `APPROVED_ACTIVE_DECK` auf den neuen SHA-256-Wert. |
| `validate_adv_003_curriculum.py` | Sechs Ansprüche werden nicht mehr als `PLANNED` ohne Folie, sondern als `KEEP` mit erwarteter Folienliste geprüft; die Kennzahlen für aktive Vertiefungsclaims und Vertiefungsfolien sind Pflichtfragmente. |

Die vollständige statische Prüfstrecke läuft grün.

## 6. Wirkung auf die Traceability

| Kennzahl | Vorher | Nachher |
|---|---|---|
| Folien im aktiven Deck | 84 | 94 |
| Ansprüche mit aktiver Folie | 84 | 90 |
| `ADV-CLM-*` auf `KEEP` | 0 | 6 |
| `ADV-CLM-*` auf `PLANNED` | 39 | 33 |

`ADV-CLM-013` bis `ADV-CLM-018` sind damit belegt. Die verbleibenden 33 Ansprüche bleiben `PLANNED`; sie gehören zu Arbeitspaketen, deren Demos noch nicht implementiert sind.

## 7. Offene Punkte

1. Die fachliche Endabnahme der Vertiefungsfolien setzt eine erfolgreiche Runtime-Abnahme von `QRY-013` und `QRY-004` auf SQL Server 2019, 2022 und 2025 voraus. Beide Demos stehen auf `IMPLEMENTED`, nicht auf `VALIDATED`, weil die Runtime-Matrix ausschließlich auf GitHub-gehosteten Runnern läuft und vom Arbeitsplatz nicht abgefragt werden kann.
2. `docProps/app.xml` meldet weiterhin `<ap:Slides>0</ap:Slides>`. Der Wert war bereits vor der Erweiterung falsch und wird bewusst nicht korrigiert, um die Änderung auf den fachlichen Zweck zu begrenzen.
3. Jede weitere Deckerweiterung ändert erneut Prüfsumme und Folienzahl. `OPT-009`, `OPT-010` und `OPT-017` benötigen deshalb ein verallgemeinertes Erzeugungswerkzeug sowie eine Fortschreibung von `SLIDE_COUNT` und der Liste integrierter Ansprüche.
