# Kennungs- und Registrierungsstandard

## Zweck und Geltungsbereich

Diese Datei ist die verbindliche Registrierungsautorität für neue allgemeine Tasks, Entscheidungen sowie Demo- und Arbeitspaket-Kennungen in `gecompat/SQL_PerformanceSchulung`. Sie ergänzt die projektführenden Regeln in `PROJECT_RULES.md` und die Foundation-Richtlinien unter `foundation/`.

Sie gilt nicht rückwirkend: Alle vor ihrer Einführung veröffentlichten Kennungen werden im Modus `PRESERVE` beibehalten. Quellenkennungen verbleiben im bestehenden Quellenregister und dessen Pflegeprozess.

## Autorität und Arbeitsablauf

Die Autorität besteht aus dem versionierten Registry-Stand `.ai/identity/registry.json` und den mitgelieferten, versionierten Foundation-Clients:

- PowerShell: `.ai/foundation/reference_clients/ArtifactReference.ps1`
- Python: `.ai/foundation/reference_clients/artifact_reference.py`

Menschen und KI verwenden dieselbe Registry und dürfen finale Kennungen weder aus dem Chat-Verlauf noch durch Suchen oder Zählen vorhandener Markdown-Dateien ableiten. Jede finale Vergabe aktualisiert die `registry_revision` und legt einen zugehörigen Artefaktdatensatz unter `.ai/identity/artifacts/` an.

Für eine serielle Vergabe wird `DIRECT` mit der erwarteten Revision verwendet. Bei parallelen Branches oder Offline-Arbeit wird zunächst `DEFERRED` verwendet; der Entwurf enthält nur seine UUID. Die finale Kennung wird erst beim zentralen Registrieren vergeben. Eine veraltete erwartete Revision ist ein Konflikt und wird erneut gegen die aktuelle Registry aufgelöst, nicht überschrieben.

Beispiel für eine direkte Task-Vergabe aus dem Repository-Stamm:

```powershell
pwsh -File .ai/foundation/reference_clients/ArtifactReference.ps1 `
  -Operation new -RegistryPath .ai/identity/registry.json `
  -ArtifactPath .ai/identity/artifacts/TSK-001.json `
  -Mode DIRECT -ExpectedRegistryRevision 1 `
  -Kind task -Title 'Kurzbeschreibung'
```

## Nomenklatur

| Bereich | Neue Kennung | Bedeutung |
|---|---|---|
| allgemeiner Task | `TSK-###` | stabile, fachlich neutrale Arbeitseinheit |
| Entscheidung | `DEC-###` | verbindlicher Entscheideintrag |
| Demo oder fachliches Arbeitspaket | vorhandenes Fachpräfix, z. B. `OPT-###` | Inhalt des Demo-Katalogs oder zugehörige Arbeit |
| Welle | `W0` bis `W10` als Metadatum | Priorisierung, Reihenfolge und aktueller Planbezug; keine neue Identität |

Eine Task-ID bleibt bei Umplanung, Verschiebung in eine andere Welle, Statuswechsel, Teilung oder Zusammenlegung bestehen. Solche Änderungen werden durch Status und Beziehungen dokumentiert. Ein Nachfolger erhält eine neue Kennung und verweist auf seinen Vorgänger.

Historische wellencodierte Kennungen wie `W0-001` und `W2-007` bleiben gültige Referenzen. Sie werden nicht in `TSK` migriert und neue Kennungen mit Präfix `W0` bis `W10` werden nicht vergeben.

Die Registry enthält die für diesen Geltungsbereich zugelassenen Präfixe und ihre semantische Zuordnung. Ein Präfix darf nach Veröffentlichung nicht mit einer anderen Bedeutung wiederverwendet werden. Der initiale Zählerstand liegt oberhalb des am Commit `2fad8b8` veröffentlichten Bestands; historische Kennungen sind bewusst keine nachträglich erzeugten Registry-Allokationen.

## Prüfung und Änderungen

Vor einer Registrierung wird die Registry mit einem der Referenz-Clients validiert. Änderungen an Präfixen, Zählerständen oder diesem Ablauf benötigen eine neue `DEC-###`-Entscheidung und eine Aktualisierung dieser Datei. Eine Umnummerierung oder nachträgliche Neudeutung historischer Kennungen ist nur nach ausdrücklicher, dokumentierter Migrationsentscheidung zulässig.
