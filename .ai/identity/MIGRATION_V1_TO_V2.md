# Migration der Artefakt-Registry von v1 auf v2

Status: abgeschlossen am 2026-08-28

Entscheidung: `DEC-062`

Migrationsmodus: `MIGRATE_EXPLICIT`

## Ausgangspunkt und Kollisionsprüfung

- Ausgangsprofil: `foundation-artifact-registry/v1`, Registry-Revision 2
- Ausgangs-Commit der Foundation-Integration: `83b187dd46e51227fbf5e23ef5e51ef44c915c9a`
- Vor der Migration geprüfte offene Pull Requests: 0
- Unverändert übernommene Zuordnungen:
  - `DEC-061` → `urn:uuid:01a03379-e43c-7fbc-8b44-fb156fb2c205`
  - `DEC-062` → `urn:uuid:01a0499c-af28-7779-bb1c-1b70e49597a3`

## Transformationsregeln

1. Die bisherigen `next_sequence`-Werte definieren die bereits geschützten historischen Bereiche. Jede Kennung von 1 bis `next_sequence - 1` wurde als eigener zentraler Datensatz übernommen.
2. Bestehende UUID-Zuordnungen wurden unverändert übernommen. Historische Kennungen ohne frühere UUID erhielten einmalig eine UUIDv4.
3. Die kanonische Referenz ist der Schlüssel im Objekt `artifacts`; ein redundantes Feld `human_ref` wird nicht gespeichert.
4. `next_sequence`, `registry_revision`, `allocations` und die getrennten Datensätze unter `.ai/identity/artifacts/` wurden entfernt.
5. Alle 211 übernommenen Datensätze sind `REGISTERED`. Ihre fachlichen Inhalte und Planungszustände bleiben in den bisherigen projektspezifischen Dokumenten maßgeblich; die Registry ist die Autorität für Identität und Registrierung.

## Ergebnis und Wiederherstellung

Das Zielprofil ist `foundation-artifact-registry/v2`. Die nächste Referenz wird aus dem höchsten vorhandenen Sequenzwert abgeleitet; unmittelbar nach der Migration ergeben sich unter anderem `DEC-063` und `ADV-012`.

Der unveränderte Foundation-Workflow liest den Registry-Pfad aus der GitHub-Repository-Variable `ARTIFACT_REGISTRY_PATH`. Für dieses Repository ist sie auf `.ai/identity/registry.json` gesetzt.

Die Migration ist vollständig in Git nachvollziehbar. Eine Wiederherstellung erfolgt durch Revert des Migrations-Commits; außerhalb des Repositorys wurde kein Registry-Zustand verändert. Nach einem Revert dürfen keine unter v2 neu registrierten Kennungen ohne gesonderte Konfliktprüfung in v1 übernommen werden.
