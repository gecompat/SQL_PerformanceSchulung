# Ergänzung zum Vertiefungsplan – Abschluss ADV-004 und ADV-005

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` nach erfolgreicher CI-Abnahme |
| Stand | 2026-07-26 |
| Bezugsplan | [`ADVANCED_PERFORMANCE_BLOCK_PLAN.md`](ADVANCED_PERFORMANCE_BLOCK_PLAN.md) |
| Maschinenlesbarer Vertrag | [`advanced_vp1_vp2_design.json`](advanced_vp1_vp2_design.json) |

## Fortschrittsänderung

`ADV-004` und `ADV-005` sind vollständig entworfen. Die Detailverträge stehen in [`ADV_004_LAB_VP1_DESIGN.md`](ADV_004_LAB_VP1_DESIGN.md) und [`ADV_005_LAB_VP2_DESIGN.md`](ADV_005_LAB_VP2_DESIGN.md).

Der Status `VALIDATED` bezeichnet ausschließlich die fachliche und statische Designfreigabe. Keine der neuen oder erweiterten Demos ist dadurch implementiert oder runtime-validiert.

## Auswirkungen auf die Reihenfolge

- `ADV-006` und `ADV-007` sind die nächsten fachlichen Designpakete.
- `ADV-008` wird anschließend in den im maschinenlesbaren Vertrag festgelegten Implementierungsschnitten bearbeitet.
- Gate V2 wird je LAB-Serie beziehungsweise Demo-Schnitt geprüft; der Abschluss von LAB-VP1 und LAB-VP2 ersetzt nicht die Designfreigabe von LAB-VP3 bis LAB-VP5.
- `ADV-009` bleibt von belastbarer Runtime-Evidenz und der Präsentationsvariantenarchitektur abhängig.

## Quellenbindung

Für LAB-VP1 gelten die Claims `ADV-CLM-001` bis `ADV-CLM-012` und die in `ADV-002` zugeordneten Quellen. Für LAB-VP2 gelten `ADV-CLM-013` bis `ADV-CLM-020`. Die Detaildesigns nennen zusätzlich die jeweils tragenden Quellen-IDs direkt bei den neuen Demos.
