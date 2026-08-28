# CON-009 – TempDB-Kostenklassen

| Merkmal | Wert |
|---|---|
| Status | `IMPLEMENTED` |
| Sicherheit | `YELLOW`, frische Wegwerf-Instanz |
| Versionen | SQL Server 2019, 2022 und 2025 |
| Sessions | 1 |
| Profil / Budget | `performance`, 300 Sekunden, mindestens 8 GB freier Speicher |

`LO-M05-04`, `CLM-068` und `ADV-CLM-027` trennen Benutzerobjekte, interne Worktables/Spills und Versionsspeicher. Die Demo misst kumulative Task-Allokations-Deltas für User/Internal Objects sowie einen zeitgebundenen instanzweiten Version-Store-Snapshot. Eine querylokal auf `MAX_GRANT_PERCENT=0.1` begrenzte Sortierung erzeugt die interne Arbeitsstrecke; sie ändert keine Instanzoption. Freigegebene Pages werden nicht fälschlich als nie allokiert interpretiert. Die Demo leitet aus Dateigröße allein keine Ursache ab.

`SRC-029`, `SRC-004` und `SRC-031` sind `ACTIVE`. Instanzweite Dateikonfiguration, Restart, Memory-optimized TempDB Metadata und SQL-Server-2025-Space-Governance sind Nichtziele und bleiben laut Delta-Review `DEFER`. Cleanup entfernt nur die markergebundene Datenbank; temporäre Objekte sind sessionlokal. Runtimestatus bleibt bis zur zweifachen Zielmatrix `IMPLEMENTED`.
