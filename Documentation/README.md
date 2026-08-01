# Documentation

Dieser Bereich enthält die lehrgangsweite fachliche Dokumentation.

| Ordner | Inhalt |
|---|---|
| `Architecture/` | Architekturverträge für interaktive Schulungsszenarien, SQL_Server_Lab-Integration und technische Qualitätssicherung |
| `Project_Planning/` | Master-Umsetzungsplan, aktueller Ausführungsstatus, quellenbasierte Vertiefungspläne, Masterdeck-Variantenarchitektur, Arbeitspakete, Abhängigkeiten, Gates und Wiederaufnahmeverfahren |
| `Curriculum/` | Lernpfade, Zielgruppen, Voraussetzungen und Reihenfolge |
| `Demo_Catalog/` | Zuordnung von Themen, Folien, Demos, Versionen und Sicherheitsstufen |
| `HowTo/` | Bedienanleitungen für die Ausführung der Schulungsdemos, insbesondere die lokale Testumgebung |
| `Research/` | Quellenbasierte Fachprüfung, Claim-/Quellenmatrizen und dokumentierte Recherche |
| `Standards/` | verbindliche Terminologie-, Schreib-, Präsentations- und Manifestverträge |

Der verbindliche langfristige Gesamtplan liegt in [`Project_Planning/MASTER_IMPLEMENTATION_PLAN.md`](Project_Planning/MASTER_IMPLEMENTATION_PLAN.md). Der aktuelle operative Fortschritt und der nächste Einstiegspunkt stehen in [`Project_Planning/CURRENT_EXECUTION_STATUS.md`](Project_Planning/CURRENT_EXECUTION_STATUS.md); dieses Dokument korrigiert veraltete historische Fortschrittsmarker des Masterplans.

Der kanonische Zielvertrag für auswählbare, vollständig vorbereitete und interaktiv nutzbare Schulungsumgebungen auf Docker, Podman, Hyper-V oder gemischten Topologien liegt in [`Architecture/SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md`](Architecture/SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md). Die automatisierte Testmatrix ist als nachgeordnete Qualitätssicherung in [`Architecture/SQL_SERVER_LAB_TEST_AUTOMATION.md`](Architecture/SQL_SERVER_LAB_TEST_AUTOMATION.md) beschrieben.

Der modulübergreifende Plan für vertiefende Query-Processing-, Execution-Plan-, Parameter-Sensitivity-, Memory-, IQP- und Incident-LABs liegt in [`Project_Planning/ADVANCED_PERFORMANCE_BLOCK_PLAN.md`](Project_Planning/ADVANCED_PERFORMANCE_BLOCK_PLAN.md). Die zugehörige verbindliche Claim- und Quellenmatrix liegt in [`Research/ADVANCED_PERFORMANCE_CLAIM_SOURCE_MATRIX.md`](Research/ADVANCED_PERFORMANCE_CLAIM_SOURCE_MATRIX.md).

Die Ableitung der Tiefenprofile `BASIS`, `STANDARD` und `VERTIEFUNG` aus dem kanonischen PowerPoint-Masterdeck wird in [`Project_Planning/MASTER_DECK_VARIANT_ARCHITECTURE.md`](Project_Planning/MASTER_DECK_VARIANT_ARCHITECTURE.md) geregelt. Der konkrete SlideKey- und Variantenmanifest-Vertrag liegt in [`Standards/PRESENTATION_VARIANT_MANIFEST_CONTRACT.md`](Standards/PRESENTATION_VARIANT_MANIFEST_CONTRACT.md); das maschinenlesbare Schema liegt unter [`../Presentations/variants/presentation_variants.schema.json`](../Presentations/variants/presentation_variants.schema.json).

Objektspezifische Bedienungs- und Interpretationshinweise verbleiben bei der jeweiligen Demo. Übergreifende Erklärungen werden hier zentral geführt und nicht unkontrolliert dupliziert.
