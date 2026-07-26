# Review – Erste Prioritätswelle

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-07-26 |
| Ausgangscommit | `e265a267764c4db29f3bf76b21622b43780a88fb` |
| Bearbeitete Arbeitspakete | Statuskonsolidierung, `ADV-002`, `PRS-011` |
| Ausführbare SQL-Dateien geändert | nein |
| PowerPoint-Datei geändert | nein |
| GitHub-Workflow geändert | nein |

## 1. Umfang

Die Welle konsolidiert den operativen Projektstatus, legt die fachliche Claim- und Quellenbasis des Vertiefungsstrangs fest und definiert den technischen Vertrag für die spätere Ableitung der Präsentationsprofile. `W2-002`, `ADV-003`, `PRS-012` und `TST-011` werden noch nicht umgesetzt.

## 2. Abnahmeevidenz

### Statuskonsolidierung

- [`CURRENT_EXECUTION_STATUS.md`](CURRENT_EXECUTION_STATUS.md) benennt den geprüften Ausgangscommit, abgeschlossene Gates, validierte Demos, aktuelle Blocker und die nächste parallele Arbeitswelle.
- `.ai/BACKLOG.md` verweist auf diesen operativen Einstiegspunkt.
- Veraltete historische Fortschrittsmarker des Masterplans werden nicht mehr als aktueller Arbeitsstand verwendet.

### ADV-002

- [`ADVANCED_PERFORMANCE_CLAIM_SOURCE_MATRIX.md`](../Research/ADVANCED_PERFORMANCE_CLAIM_SOURCE_MATRIX.md) enthält 39 stabile Claims.
- Jeder Claim besitzt eine Evidenzklasse, Quellenzuordnung, Demo-/Testbezug sowie eine Versions- oder Abnahmebedingung.
- Microsoft-Primärquellen und ergänzende Community- beziehungsweise Methodenquellen sind getrennt.
- Undokumentierte Optimizer-Interna sind als `EMPIRICAL` oder `INFERENCE` eingegrenzt und benötigen eigene Runtime-Evidenz.
- Der Vertiefungsplan markiert `ADV-001` und `ADV-002` als `VALIDATED` und benennt `ADV-003` als nächsten fachlichen Schritt.

### PRS-011

- [`PRESENTATION_VARIANT_MANIFEST_CONTRACT.md`](../Standards/PRESENTATION_VARIANT_MANIFEST_CONTRACT.md) definiert SlideKey, Tiefenprofile, Folienrollen, Abhängigkeiten, Custom Shows, Buildregeln und statische Prüfungen.
- [`presentation_variants.schema.json`](../../Presentations/variants/presentation_variants.schema.json) ist syntaktisch gültiges JSON Schema Draft 2020-12.
- Das Schema wurde mit `jsonschema.Draft202012Validator.check_schema` geprüft.
- Ein neutraler Beispielvertrag mit allen drei Profilen, einem technischen Claim, einer Quelle, einem Lernziel und einer Demo-ID wurde erfolgreich gegen das Schema validiert.
- Das Variantenverzeichnis dokumentiert ausdrücklich, dass das produktive Manifest erst in `PRS-012` nach Vergabe stabiler SlideKeys angelegt wird.
- Der Architekturplan markiert `PRS-011` als `VALIDATED` und lässt `PRS-012` sowie den schemaorientierten Teil von `TST-011` parallel beginnen.

## 3. Konsistenzprüfung

- Der Branch basiert ohne Rückstand auf dem geprüften `main`-Commit.
- Die neue Matrix referenziert ausschließlich bestehende Quellen- und kanonische Demo-ID-Schemata.
- Das Schema erlaubt nur Module M00 bis M07, die Profile `BASIS`, `STANDARD`, `VERTIEFUNG` und die vertraglich definierten Folienrollen.
- Buildregeln erzwingen die unveränderte Masterdatei, absteigendes Entfernen ausgeschlossener Folien und Fehler bei gebrochenen Links.
- Die Dateinamensregel im Architekturplan und im JSON Schema ist synchronisiert.
- Alle neu erzeugten Inhalte sind synthetisch und firmenneutral. Es wurden keine realen Umgebungswerte, Hostnamen, Zugangsdaten, Kundeninformationen oder Diagnoseausgaben aufgenommen.

## 4. Nicht durchgeführte Prüfungen

- Es wurde kein PowerPoint-Render durchgeführt, da das Masterdeck nicht geändert wurde.
- Es wurde keine SQL-Server-Runtime-Matrix gestartet, da keine SQL-Datei geändert wurde.
- Custom Shows und Notes-Marker wurden nicht geprüft, weil sie erst in `PRS-012` erzeugt werden.
- Die vollständige semantische Manifestprüfung bleibt Gegenstand von `TST-011`.

## 5. Nächste Welle

Die nächste sinnvolle Verarbeitungswelle kann in vier getrennten, teilweise parallelen Strängen erfolgen:

1. `ADV-003`: Claims in Curriculum-Lernziele und Traceability überführen.
2. `PRS-012` und `TST-011`: SlideKeys/Custom Shows im Masterdeck sowie statischen Validator entwickeln.
3. `W2-002`: priorisierte Bestandsbeispiele neutralisieren und von externen Abhängigkeiten befreien.
4. `TST-002` sowie Query-Store-/XE-Pilotvalidierung als Sicherheits- und Diagnosequerschnitt.

`ADV-004` und `ADV-005` beginnen erst nach `ADV-003`. `PRS-013` beginnt erst nach erfolgreichem `PRS-012` und dem relevanten Teil von `TST-011`.
