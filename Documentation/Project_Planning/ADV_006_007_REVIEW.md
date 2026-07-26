# Review – ADV-006 und ADV-007

| Merkmal | Wert |
|---|---|
| Status | `IN_PROGRESS` |
| Stand | 2026-07-26 |
| Ausgangscommit auf `origin/main` | `b3597d3c53c98ebf78d1fcf3ee5425f0af3cb5ad` |
| Arbeitspakete | `ADV-006`, `ADV-007` |
| PowerPoint geändert | nein |
| SQL-Demos geändert | nein |

## 1. Umfang

Die Welle schließt die fachliche Designphase des Vertiefungsstrangs ab. Sie entwirft LAB-VP3 und LAB-VP4 für Workspace Memory, Spills und Intelligent Query Processing sowie LAB-VP5 mit `DGN-007` als vollständigen Diagnose- und Capstone-Fall. Es werden noch keine ausführbaren SQL-Demos erzeugt.

## 2. ADV-006 – LAB-VP3 und LAB-VP4

Der Designvertrag umfasst:

- die Trennung von Grantstufen, Spill, Undergrant, Overgrant, Grant-Warten und allgemeinem Memory Pressure,
- einen normalen gelben LAB-VP3-Pfad und eine optionale rote `RES-003`-Erweiterung,
- dedizierte Wegwerfinfrastruktur, High-Impact-Bestätigung, 180-Sekunden-Budget und externen Kill-Switch für `RES-003`,
- Multi-Session-Verträge für `RES-004`,
- Wait-Scope und zeitbezogene Deltas für `RES-007`,
- begrenzte, versionsgeprüfte XE-Evidenz für `DGN-005`,
- eine Featurematrix für SQL Server 2019, 2022 und 2025,
- getrennte Voraussetzungen für Engine-Version, Compatibility Level, Datenbankkonfiguration, Query Store und Eligibility,
- begründete Feature- und Ressourcen-Skips anstelle erzwungener Planformen.

## 3. ADV-007 – LAB-VP5 und DGN-007

Der Designvertrag umfasst:

- einen neutral benannten Teilnehmerfall ohne vorweggenommene Lösung,
- Query-Store-Zeitfenster `T0_BASELINE`, `T1_INCIDENT` und `T2_COMPARISON`,
- Plan-, Parameter-, Statistik-, Wait- und XE-Evidenz,
- gestufte Evidenzfreigabe,
- mindestens drei plausible Hypothesen, von denen mindestens zwei verworfen werden müssen,
- genau eine querylokale, reversible Referenzänderung,
- versionsübergreifenden Kernpfad ohne Abhängigkeit von PSP, OPPO oder Query Store Hints,
- vollständigen Cleanup und Rückfallplan.

## 4. Maschinenlesbarer Vertrag

`advanced_vp3_vp5_design.json` definiert:

- LAB-Sequenzen und Claimabdeckung,
- Featurematrix und Versionsergebnisse,
- Demo-Risiken, Ausführungspfade, Sessions und Mindestressourcen,
- Evidenzfelder und Skip-Codes,
- verbotene globale, datenschutzkritische oder didaktisch entwertende Aktionen,
- die Implementierungsschnitte für `ADV-008`.

## 5. Automatisierte Abnahme

Die statische Prüfung validiert:

- vollständige Claim- und Lernzielabdeckung,
- LAB-VP3-, LAB-VP4- und LAB-VP5-Reihenfolge,
- Featurematrix für 2019, 2022 und 2025,
- Query-Store-Anforderungen für persistentes Feedback, CE Feedback und DOP Feedback,
- roten Sicherheitsvertrag für `RES-003`,
- mindestens zwei falsifizierbare Alternativhypothesen für `DGN-007`,
- neutrale Teilnehmerbezeichnung,
- Query-Store-, Plan-, Statistik-, Wait-, XE- und Rollback-Evidenz,
- Backlog- und Statuskonsistenz,
- vollständigen Repository-Privacy-Scan.

## 6. Nicht durchgeführte Prüfungen

Eine SQL-Server-Runtime-Matrix wird in dieser Welle nicht ausgeführt, weil keine SQL-Datei und keine ausführbare Demo implementiert wird. Ein PowerPoint-Render ist nicht erforderlich, weil das Masterdeck unverändert bleibt. Runtime-, Feature-, Planform- und Ressourcenvalidierung folgen unter `ADV-008`.

## 7. Statusgrenze

`ADV-006` und `ADV-007` können nach erfolgreicher CI fachlich und statisch `VALIDATED` werden. Sämtliche zugehörigen Demos bleiben bis zur Implementierung und Runtimeprüfung `PLANNED` beziehungsweise `DESIGNED`.

## 8. Nächster fachlicher Schritt

Nach der Abnahme beginnt `ADV-008` mit kleinen, unabhängigen Implementierungsschnitten. Als erste Schnitte sind `OPT-015`, `OPT-016`, `QRY-013` und `QRY-004_CLASSIC_AND_DYNAMIC` vorgesehen. Query-Store-/XE-Pilotvalidierung erfolgt vor `DGN-007`. `RES-003` bleibt der letzte und separat freizugebende rote Schnitt.