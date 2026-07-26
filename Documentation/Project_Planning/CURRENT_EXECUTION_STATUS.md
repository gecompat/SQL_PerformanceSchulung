# Aktueller Ausführungsstand

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-07-26 |
| Geprüfter Ausgangs-`main` | `cbe6ca52229fe57f5043595d68fbdcbb36c00045` |
| Abnahmewelle | `ADV-003`, `TST-002` |
| Zweck | kanonischer operativer Einstiegspunkt und Korrektur historischer Statusmarker im Masterplan |

## 1. Geltung

Dieses Dokument ist der kanonische operative Status für die Wiederaufnahme der Arbeiten. Die langfristige Struktur und die fachlichen Arbeitspakete bleiben im [Master-Umsetzungsplan](MASTER_IMPLEMENTATION_PLAN.md) verbindlich. Widersprechen dessen historische Abschnitte 18 oder 20 diesem Status, gilt für Fortschritt, nächsten Einstiegspunkt und Blocker dieses Dokument, bis der Masterplan vollständig konsolidiert wird.

## 2. Abgeschlossener Stand

- Welle 0 und Gate A sind validiert.
- `FWK-001` bis `FWK-012` sind implementiert und auf SQL Server 2019, 2022 und 2025 runtime-validiert.
- Gate B ist mit `QRY-001`, `OPT-002`, `CON-004` und `OPT-013` sowie 24 vollständigen Demoläufen validiert.
- Die SQL-Server-Matrix 2019/2022/2025 ist aktiv und erfolgreich ausgeführt.
- `W2-001` hat alle historischen Beispiele klassifiziert; kein historisches Skript ist dadurch zur direkten Ausführung freigegeben.
- `W2-007` ist abgeschlossen. Der aktive Foliensatz besitzt 84 `KEEP`-Entscheidungen und keine offenen `REFINE`-Claims.
- `ADV-001` und `ADV-002` haben Vertiefungsstrang, fünf LAB-Serien und 39 quellenklassifizierte Claims festgelegt.
- `ADV-003` hat neun beobachtbare Vertiefungslernziele ergänzt und alle 39 Claims eindeutig in Curriculum und Traceability eingeordnet. Gate V0 und Gate V1 sind validiert.
- `DEC-043`, `PRS-009` und `PRS-011` haben Masterdeck, Tiefenprofile, SlideKey- sowie Variantenmanifest-Vertrag festgelegt.
- `TST-002` stellt eine SQL-Server-unabhängige Privacy- und Metadatenprüfung mit synthetischen Selbsttests und GitHub-Actions-Gate bereit.

## 3. Validierte zweite Prioritätswelle

| Arbeitspaket | Ergebnis | Status |
|---|---|---|
| `ADV-003` | 52 gesamte Lernziele; davon neun neue Vertiefungslernziele für M02, M03, M06 und M07 | `VALIDATED` |
| Traceability | 84 aktive Claims unverändert; 39 geplante Vertiefungsclaims mit Lernziel, Quelle, Demo/LAB und Testprofil | `VALIDATED` |
| `TST-002` | Text-, Office-, Archiv-, Metadata-, Secret- und Medien-Gate ohne Ausgabe gefundener Schutzwerte | `VALIDATED` |
| Qualitätsworkflow | Curriculum-, Scanner-Selbsttest-, Repository-Privacy-, Framework- und Präsentationsprüfung | `PASS` |

Der Privacy-Scanner ersetzt keine visuelle Einzelprüfung, kein OCR für texttragende Medien und keinen Rendervergleich. Neue oder geänderte Medien bleiben bis zum manuellen Nachweis blockiert.

## 4. Unmittelbar nächste ausführbare Arbeiten

Die folgenden Stränge können nach dieser Welle parallel begonnen werden:

1. `ADV-004`: LAB-VP1 sowie `OPT-015` bis `OPT-017` vollständig entwerfen.
2. `ADV-005`: LAB-VP2, `QRY-013` und die Erweiterung von `QRY-004` vollständig entwerfen.
3. `PRS-012` und `TST-011`: Masterdeck mit stabilen SlideKeys und Custom Shows ausstatten und statisch validieren.
4. `W2-002`: die neun priorisierten W2-A-Migrationen in fachlich getrennte, validierbare Teilpakete schneiden und neutralisieren.
5. Query Store und Extended Events als zentrale Diagnosepfade in repräsentativen Demos validieren.
6. Entscheidungspfad `TSQL_TESTDB` vor `CONTAINER` beziehungsweise `HYPERV` im Demo-Katalog verbindlich abbilden.

## 5. Abhängigkeiten

- `ADV-004` und `ADV-005` verwenden die validierten Claims und Lernziele; beide können parallel entworfen werden.
- `ADV-006` setzt die Feature- und Evidenzentscheidungen aus den vorangehenden Designpaketen sowie den Query-Store-/XE-Nachweis voraus.
- `ADV-007` setzt mindestens die Designs von `QRY-013`, `DGN-003` und `DGN-005` voraus.
- `ADV-008` setzt Gate V2 des jeweils umzusetzenden LABs voraus.
- `ADV-009` setzt belastbare Demo-Evidenz sowie `PRS-012` voraus.
- `PRS-013` setzt `PRS-012` und den statischen Kern von `TST-011` voraus.
- `TST-012` setzt erzeugte Varianten aus `PRS-013` voraus.
- `W2-003` bis `W2-006` setzen die jeweils betroffene Neutralisierung aus `W2-002` voraus.
- Ressourcengrenzen, Hyper-V- oder Netzwerkprofile werden nur nach einer konkreten Demo-Abhängigkeit bearbeitet.

## 6. Aktuelle Blocker

Es besteht kein globaler technischer Blocker. Die folgenden Abhängigkeiten begrenzen einzelne Stränge:

- Vertiefungsdemos dürfen erst nach dem jeweiligen Design und Gate V2 implementiert werden.
- Eigenständige Präsentationsvarianten dürfen erst nach stabiler Folienidentität und Manifestvalidierung erzeugt werden.
- Rote Ressourcen- und I/O-Demos benötigen eine ausdrücklich zugeordnete isolierte Testumgebung.
- Medien- und Office-Releases benötigen zusätzlich zum automatischen Scanner visuelle, OCR- und Renderabnahme.

## 7. Datenschutzstatus

Die in dieser Welle erzeugten Repository-Artefakte enthalten ausschließlich öffentliche technische Quellen-IDs, neutrale Projekt-, Claim-, Lernziel- und Demo-IDs sowie synthetische Scannerfälle. Findings werden nur nach Pfad, Kategorie und Anzahl ausgegeben. Reale Diagnosewerte, Hostnamen, Zugangsdaten, Kundeninformationen, interne Pfade oder proprietäre Umgebungsinformationen werden nicht persistiert.
