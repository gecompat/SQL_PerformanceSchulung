# Aktueller Ausführungsstand

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-07-26 |
| Geprüfter Ausgangscommit auf `origin/main` | `b3597d3c53c98ebf78d1fcf3ee5425f0af3cb5ad` |
| Aktuelle Verarbeitungswelle | `ADV-006`, `ADV-007` |
| Zweck | kanonischer operativer Einstiegspunkt für Implementierung und Runtime-Validierung |

## 1. Verifizierter Repository-Stand

Der Commit `b3597d3c53c98ebf78d1fcf3ee5425f0af3cb5ad` ist auf `origin/main` vorhanden. Er enthält die validierten Designverträge für LAB-VP1 und LAB-VP2 sowie `ADV-001` bis `ADV-005`.

Welle 0 und Gate A, `FWK-001` bis `FWK-012`, die SQL-Server-Matrix 2019/2022/2025, Gate B, `W2-001`, `W2-007`, `ADV-001` bis `ADV-005`, `PRS-009`, `PRS-011` und `TST-002` sind validiert.

## 2. Abgeschlossene Designwelle

| Arbeitspaket | Ergebnis | Status |
|---|---|---|
| `ADV-006` | LAB-VP3 und LAB-VP4 einschließlich Ressourcen-, Versions-, Compatibility-Level-, Query-Store-, Eligibility- und Skip-Matrix vollständig entworfen | `VALIDATED` nach CI-Abnahme |
| `ADV-007` | LAB-VP5 und `DGN-007` einschließlich Incident-, Hypothesen-, Evidenzfreigabe-, Vergleichs- und Rückfallvertrag vollständig entworfen | `VALIDATED` nach CI-Abnahme |

Die Designwelle erzeugt keine ausführbaren SQL-Demos. Sie legt verbindlich fest:

- regulären gelben LAB-VP3-Pfad und optionalen roten `RES-003`-Pfad,
- harte Laufzeit-, Bestätigungs-, Kill-Switch- und Infrastrukturgrenzen für rote Speicherlast,
- Featurematrix für SQL Server 2019, 2022 und 2025,
- getrennte Voraussetzungen für Engine-Version, Compatibility Level, Datenbankkonfiguration, Query Store und Eligibility,
- Query-Store-Zeitfenster, XE-Grenzen und Evidence-Ladder für `DGN-007`,
- mindestens zwei zu verwerfende Alternativhypothesen,
- genau eine reversible Referenzänderung,
- kleine spätere Implementierungsschnitte für `ADV-008`.

## 3. Gate-Status

- Gate V0 – Quellenfreigabe: `VALIDATED`.
- Gate V1 – Curriculumfreigabe: `VALIDATED`.
- Gate V2 – Designfreigabe: `VALIDATED` nach erfolgreicher statischer Prüfung dieser Welle.
- Gate V3 – Runtimefreigabe: offen.
- Gate V4 – Lehrmittelfreigabe: offen.

`OPT-015`, `OPT-016`, `OPT-017`, `QRY-013`, die erweiterte Struktur von `QRY-004`, die LAB-VP3-/VP4-Schritte und `DGN-007` sind entworfen, aber ausdrücklich noch nicht `IMPLEMENTED` oder runtime-validiert.

## 4. Nächste fachliche Verarbeitung

Der nächste abhängige Schritt ist `ADV-008`. Die Umsetzung erfolgt nicht als Sammel-PR. Empfohlene Reihenfolge:

1. `OPT-015` – Planweite und operatorbezogene Eigenschaften.
2. `OPT-016` – Rebind, Rewind, Outer References und Spools.
3. `QRY-013` – neutraler Client-/Sessionkontext.
4. `QRY-004_CLASSIC_AND_DYNAMIC` – Catch-all, Recompile und sicher parameterisiertes dynamisches SQL.
5. Query-Store-/XE-Pilotvalidierung als Voraussetzung für diagnoseabhängige Schnitte.
6. LAB-VP3-/VP4-Implementierungen in getrennten Feature- und Ressourcenpaketen.
7. `DGN-007` erst nach stabiler Query-Store-/XE- und Runtime-Evidenz.
8. `RES-003` zuletzt, separat und ausschließlich auf dedizierter Infrastruktur.

## 5. Parallel ausführbare Querschnittsarbeit

Unabhängig von `ADV-008` bleiben ausführbar:

- `PRS-012` und `TST-011`: SlideKeys, Custom Shows und statische Präsentationsvariantenprüfung,
- fachlich getrennte `W2-002`-Teilpakete,
- Query-Store-/Extended-Events-Pilotvalidierung,
- Entscheidungspfad T-SQL/Testdatenbank vor zusätzlicher Infrastruktur im Demo-Katalog,
- Testumgebungs-How-to für vorhandene Instanz sowie Docker/Podman.

## 6. Abhängigkeiten und Sicherheitsgrenzen

- `ADV-008` verwendet ausschließlich die validierten Designverträge aus `ADV-004` bis `ADV-007`.
- `ADV-009` setzt belastbare Runtime-Evidenz und die Präsentationsvariantenverträge voraus.
- `DGN-007` setzt eine validierte Query-Store- und XE-Nutzung voraus.
- `RES-003` setzt dedizierte Wegwerfinfrastruktur, explizite High-Impact-Bestätigung, externen Kill-Switch und ein maximales Laufzeitbudget voraus.
- `PRS-013` setzt `PRS-012` und den statischen Kern von `TST-011` voraus.
- `W2-003` bis `W2-006` setzen die jeweils zugehörige Neutralisierung aus `W2-002` voraus.

## 7. Aktuelle Blocker

Es besteht kein globaler technischer Blocker. Einzelne Implementierungsschnitte besitzen jedoch harte Voraussetzungen. Planform- und featureabhängige Demos liefern kontrollierte Skips, wenn eine Optimizerentscheidung, Eligibility oder Query-Store-Voraussetzung nicht erfüllt ist. Rote Ressourcenlast wird nicht auf gemeinsam genutzten Systemen ausgeführt.

## 8. Datenschutz- und Quellenstatus

Die Designartefakte enthalten ausschließlich synthetische Objektmodelle, öffentliche Quellen-IDs, neutrale Demo- und Claim-IDs sowie generische Ressourcenprofile. Reale Anwendungs-, Host-, Benutzer-, Kunden-, Zugangs- oder Diagnosedaten sind ausgeschlossen. Query- und Parameterwerte in späteren Repository-Artefakten bleiben auf bekannte synthetische Testwerte begrenzt.