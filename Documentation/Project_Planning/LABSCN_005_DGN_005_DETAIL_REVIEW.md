# LABSCN-005 – Detailreview DGN-005

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-09-01 |
| Kandidat | `DGN-005` – begrenzte Extended-Events-Evidenz |
| Provider | Docker und Podman |
| interaktive Zielversion | SQL Server 2025 / Compatibility Level 170 |
| Safety | `YELLOW`, ausschließlich isolierte Wegwerfinstanz |

## Freigabegrundlage

`DGN-005` ist der erste autonome Folgeschnitt aus der priorisierten
LABSCN-005-Kandidatenliste. Der fachliche Demovertrag und die Quellen `SRC-028`
und `SRC-060` sind bereits registriert. Actions-Lauf 33222989682 validiert die
automatisierte Demo auf SQL Server 2019, 2022 und 2025 jeweils zweimal mit
`PASS/OK`. Für den interaktiven Slice wird die kleinere, bereits durch
`SQL_Server_Lab` unterstützte SQL-Server-2025-Einzelinstanz verwendet; das
Fremdrepository benötigt keine Änderung.

## Lifecycle- und Sicherheitsvertrag

- Start erstellt eine markergebundene Datenbank und eine exakt benannte,
  datenbankgefilterte Event Session.
- Die Session verwendet ausschließlich `error_reported`, einen In-Memory-Ring-
  Buffer mit 100 Ereignissen und 1024 KB, 2048 KB Session Memory,
  `STARTUP_STATE=OFF` und 300 Sekunden Maximaldauer.
- Es gibt keinen Event-File-Target und keinen automatischen Export.
- Benutzerinnen und Benutzer führen Demonstration, Observation, Mitigation und
  Comparison in einem SQL-Fenster nacheinander aus.
- Reset und Remove prüfen vor dem Löschen alle vier Datenbankmarker. Eine
  gleichnamige Event Session ohne passende Datenbank wird nicht übernommen.

## Evidenz- und Stopgrenze

Die Kernaussage ist nicht eine feste Ereigniszahl. Validiert werden aktive und
begrenzte Session, exaktes Datenbankprädikat, sichtbare synthetische Evidenz
oder kontrollierter `SKIP_EVIDENCE_MISSING`, Stopzustand und vollständiger
Cleanup. Die Runtimeabnahme vom 2026-09-01 bestand je einen vollständigen
Lifecycle `Start -> READY_FOR_USER -> Reset -> READY_FOR_USER -> Remove`:
Docker-Run `d5143f2a-9f18-49fa-8e9f-b91604993252` und Podman-Run
`82791985-b76a-4594-a5be-bab014907f7d` führten zusätzlich alle vier
Teilnehmerphasen mit `PASS/OK` aus und endeten beide mit `REMOVED`. Damit ist der
Slice `VALIDATED`.
