# Kennungs- und Registrierungsstandard

## Zweck und Geltungsbereich

Diese Datei beschreibt die verbindliche Registrierungsautorität für neue allgemeine Tasks, Entscheidungen sowie Demo- und Arbeitspaket-Kennungen in `gecompat/SQL_PerformanceSchulung`. Sie ergänzt die projektführenden Regeln in `PROJECT_RULES.md` und die Foundation-Richtlinien unter `foundation/`.

`DEC-062` hat die zentrale Registry im Profil `foundation-artifact-registry/v2` ausdrücklich aktiviert. Alle zuvor veröffentlichten Kennungen bleiben im Modus `PRESERVE` unverändert und wurden als zentrale Datensätze übernommen. Quellenkennungen verbleiben im bestehenden Quellenregister und dessen Pflegeprozess.

## Autorität und Arbeitsablauf

Die einzige Registrierungsautorität ist `.ai/identity/registry.json`. Sie enthält Präfixdefinitionen und vollständige Registrierungsdatensätze; die kanonische menschliche Referenz ist jeweils der Schlüssel unter `artifacts`. Fachliche Planungszustände und Artefaktinhalte bleiben in den dafür benannten Projektdateien maßgeblich.

Das versionierte Foundation-Tool `.ai/foundation/artifact_registry_github/registry_semantic.py` validiert die Registry, leitet die nächste freie Referenz ab und berechnet objektbezogene Drei-Wege-Merges. Menschen und KI dürfen finale Kennungen weder aus dem Chat-Verlauf noch durch Suchen oder Zählen vorhandener Markdown-Dateien ableiten.

Beispiel aus dem Repository-Stamm:

```powershell
python .ai/foundation/artifact_registry_github/registry_semantic.py validate `
  --registry .ai/identity/registry.json

python .ai/foundation/artifact_registry_github/registry_semantic.py allocate `
  --registry .ai/identity/registry.json --prefix TSK
```

Nach der Ableitung wird im selben Branch unter `artifacts.<REF>` ein vollständiger Datensatz mit einer neuen UUIDv7 oder, wenn die lokale Toolchain UUIDv7 nicht bereitstellt, UUIDv4 angelegt. Er enthält mindestens `artifact_uid`, `kind`, `title`, `registration_state`, `aliases` und `relations`. Die Referenz ist erst nach erfolgreicher Validierung und Merge in den zentralen Branch final registriert.

Die v2-Registry enthält weder `next_sequence` noch `registry_revision`. Bei parallelen Branches prüft `.github/workflows/artifact-registry-integrity.yml` frühzeitig andere offene Pull Requests und vergleicht das Git-Merge-Ergebnis mit dem semantischen Drei-Wege-Merge. Eine Kollision wird gegen den aktuellen `main`-Stand neu aufgelöst; bestehende Referenzen oder UUIDs werden nicht überschrieben. Offline-Entwürfe erhalten noch keine finale menschliche Referenz und werden erst nach aktueller Kollisionsprüfung registriert.

## Nomenklatur

| Bereich | Neue Kennung | Bedeutung |
|---|---|---|
| allgemeiner Task | `TSK-###` | stabile, fachlich neutrale Arbeitseinheit |
| Entscheidung | `DEC-###` | verbindlicher Entscheideintrag |
| Demo oder fachliches Arbeitspaket | vorhandenes Fachpräfix, z. B. `OPT-###` | Inhalt des Demo-Katalogs oder zugehörige Arbeit |
| Welle | `W0` bis `W10` als Metadatum | Priorisierung, Reihenfolge und aktueller Planbezug; keine neue Identität |

Eine Task-ID bleibt bei Umplanung, Verschiebung in eine andere Welle, Statuswechsel, Teilung oder Zusammenlegung bestehen. Solche Änderungen werden durch Status und Beziehungen dokumentiert. Ein Nachfolger erhält eine neue Kennung und verweist auf seinen Vorgänger.

Historische wellencodierte Kennungen wie `W0-001` und `W2-007` bleiben gültige Referenzen. Sie werden nicht in `TSK` migriert und neue Kennungen mit Präfix `W0` bis `W10` werden nicht vergeben.

Die Registry enthält die zugelassenen Präfixe und ihre semantische Zuordnung. Ein Präfix darf nach Veröffentlichung nicht mit einer anderen Bedeutung wiederverwendet werden. Die v2-Migration hat den gesamten durch die früheren Zählerstände geschützten Bestand übernommen; die Evidenz steht in `identity/MIGRATION_V1_TO_V2.md`.

## Prüfung und Änderungen

Vor und nach jeder Registrierung wird die Registry mit dem v2-Semantiktool validiert. Änderungen an Präfixen oder diesem Ablauf benötigen eine neue `DEC-###`-Entscheidung und eine Aktualisierung dieser Datei. Eine Umnummerierung, Entfernung, UUID-Neuzuordnung oder nachträgliche Neudeutung historischer Kennungen ist nur nach ausdrücklicher, dokumentierter Migrationsentscheidung zulässig.
