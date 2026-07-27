# LABSCN-002 – Ergebnis Welle 2

| Merkmal | Wert |
|---|---|
| Status | `IMPLEMENTED_FOR_REVIEW` |
| Branch | `agent/labscn-wave1-inventory` |
| Arbeitspaket | `LABSCN-002` |
| Folgeschritt | `LABSCN-003` – erster vollständiger Vertical Slice |

## 1. Ergebnis

Welle 2 überführt das vorläufige Szenarioinventar in einen maschinenprüfbaren Vertragsstand. Die sechs im bestehenden Lab-Testkatalog runtimevalidierten Container-Demos wurden als belastbare Ausgangsmenge übernommen: `QRY-001`, `OPT-002`, `CON-004`, `OPT-013`, `OPT-015` und `OPT-016`.

Für diese Demos sind Provider, SQL-Server-Versionen, Safety Level, Sessionmodell, Isolationsbedarf, Erzwingungsmechanismus, Verifikation, Resetstrategie und Mindestressourcen erfasst. Geplante Demos bleiben ausdrücklich als `PLANNED` gekennzeichnet.

## 2. Neue Vertragsartefakte

`Documentation/Architecture/performance-training-scenario.schema.json` definiert den fachlichen Vertrag eines interaktiven Schulungsszenarios. Er umfasst Topologie, Vorbereitung, READY_FOR_USER-Übergabe, Verifikation, Reset und Abbau. Der Vertrag enthält keine Providerimplementierung; diese verbleibt in `SQL_Server_Lab`.

`Documentation/Architecture/performance-training-scenario-inventory.schema.json` definiert die Struktur des Szenarioinventars.

`Tests/Static/validate_performance_scenarios.py` prüft zusätzlich repositoryweite Beziehungen, die mit JSON Schema allein nicht abgesichert werden können. Dazu gehören eindeutige IDs, existierende Pfade, Übereinstimmung zwischen Inventar und Szenariodefinition sowie die Pflicht zur READY_FOR_USER-Übergabe.

## 3. Erster Szenarioentwurf

`Scenarios/CON-004/scenario.json` beschreibt den ersten Vertical-Slice-Kandidaten. Das Szenario verwendet eine einzelne SQL-Server-Instanz, aber mehrere unabhängige SQL-Sessions. Die fachliche Reihenfolge wird durch FWK-006-Signale gesteuert. Feste Prozessverzögerungen dürfen ausschließlich den Start entzerren und nicht als fachliche Synchronisation dienen.

Der Problemzustand verwendet vier parallele Sessions: `HEAD`, `MIDDLE`, `LEAF` und `OBSERVER`. Der getrennte Vergleichslauf verwendet `FIRST_WRITER` und `FOLLOWER`.

## 4. Gefundene Inkonsistenz

Im bisherigen Lab-Testkatalog war für `CON-004` der Wert `sessions: 3` eingetragen. Das tatsächlich ausgeführte Manifest `Sessions/problem.json` startet vier Sessions. Der Katalog wurde auf vier Sessions korrigiert. Diese Korrektur verändert keinen fachlichen Ablauf, sondern bringt Metadaten und ausführbare Quelle in Übereinstimmung.

## 5. Nicht Bestandteil dieser Welle

Noch nicht implementiert sind:

1. das konkrete `SQL_Server_Lab`-Manifest für `CON-004`;
2. die PowerShell- oder Command-Schnittstelle für Start, Reset und Remove;
3. die kompakte READY_FOR_USER-Verbindungsübergabe;
4. Docker- und Podman-Runtimeprüfungen des vollständigen interaktiven Lifecycles.

Diese Punkte bilden `LABSCN-003`.

## 6. Abnahmekriterien für den Übergang zu LABSCN-003

Der Übergang ist fachlich möglich, wenn die beiden JSON-Schemas, das Inventar, die `CON-004`-Szenariodefinition und der statische Validator konsistent sind. Die Runtime-Abnahme erfolgt erst in `LABSCN-003`, weil dort erstmals Provisionierung, Vorbereitung, READY_FOR_USER, Reset und Remove als zusammenhängender Ablauf implementiert werden.
