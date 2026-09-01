# W2-002 – Neutralisierung priorisierter Bestandsbeispiele

| Merkmal | Wert |
|---|---|
| Arbeitspaket | `W2-002` |
| Status | `VALIDATED` |
| Prüfdatum | 2026-09-01 |
| Umfang | neun Kandidaten der Migrationswelle `W2-A` |
| Vertrag | `Documentation/Inventories/w2_002_dependency_neutralization.json` |
| Prüfer | `Tests/Static/validate_w2_002_dependency_neutralization.py` |

## Ergebnis

Die priorisierten historischen Dateien bleiben unveränderte, nicht ausführbare Quellen im Referenzarchiv. Keine Datei wurde in einen aktiven Demo-Pfad kopiert. Für bereits migrierte Lernziele verweist der Vertrag ausschließlich auf repositoryeigene Demos mit synthetischen `SQLPERF_LAB_`-Datenbanken. Für noch nicht neu gebaute Lernziele ist die historische Datei aus dem Runtimeumfang entfernt; ein verbindlicher neutraler Datenvertrag legt den späteren Neuaufbau fest.

Damit sind öffentliche Beispieldatenbanken, feste Objekt- oder Session-IDs, fremde Schemas, übernommene Messwerte, externe Datenquellen und globale Cacheeingriffe keine impliziten Voraussetzungen der Welle `W2-A` mehr. Der fachliche Neuaufbau noch fehlender Demos ist Folgearbeit und darf den Altcode nicht wieder als ausführbaren Pfad aktivieren.

| Altquelle | Entscheidung | Aktiver neutraler Ersatz | Verbleibender Neuaufbau |
|---|---|---|---|
| `SRC-LEGACY-008` | Altquelle ausgeschlossen | – | `CON-001` bis `CON-003` |
| `SRC-LEGACY-011` | Altquelle ausgeschlossen | – | `DGN-002`, `STL-004` |
| `SRC-LEGACY-012` | Altquelle ausgeschlossen | – | `DGN-002`, `OPT-014`, `RES-004` |
| `SRC-LEGACY-013` | Altquelle ausgeschlossen | – | `DGN-002` |
| `SRC-LEGACY-014` | Altquelle ausgeschlossen | `RES-007` | `DGN-002` |
| `SRC-LEGACY-018` | Altquelle ausgeschlossen | – | `OPT-012` |
| `SRC-LEGACY-020` | Altquelle ausgeschlossen | `QRY-001`, `QRY-004` | `QRY-002`, `QRY-003` |
| `SRC-LEGACY-022` | Altquelle ausgeschlossen | `OPT-009` | `OPT-008` |
| `SRC-LEGACY-028` | Altquelle ausgeschlossen | – | `IDX-004` |

## Validierungsgrenzen

Der statische Prüfer gleicht die neun Einträge gegen die autoritative `W2-A`-Klassifikation ab, bestätigt das Ausführungsverbot aller Altquellen, prüft aktive Ersatzpfade und Demo-IDs und sperrt bekannte öffentliche Beispieldatenbanken, externe Ladepfade sowie Linked-Server-Konstrukte. Er bestätigt keine Runtime-Eigenschaft eines noch nicht implementierten Folgedemos; diese bleibt an dessen vollständigen Demo- und Runtimevertrag gebunden.
