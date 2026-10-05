# Integrationsprüfung der Foundation 1.19.0

Prüfdatum: 2026-10-05. Ausgangsstand: Foundation `1.17.2`, Source-Commit `36d2cb20c2880b7cfaa6428db3716e6768e23964`. Zielstand: `1.19.0` aus [Source-Commit `4aafd20442275d0fdedf291fc6e12e8fe1f683cc`](https://github.com/gecompat/AI_Repository_Foundation/commit/4aafd20442275d0fdedf291fc6e12e8fe1f683cc). Dieser Commit entsprach bei der Prüfung dem live abgefragten Source-`main`; der lokale Source-Checkout war unverändert. Versionsautorität ist `foundation/manifest.json` an diesem Commit.

## Vollständiges semantisches Delta

Das Intervall `(1.17.2, 1.19.0]` enthält genau zwei neu eingeführte oder materiell geänderte Features. Die maschinenlesbare Bewertung steht in [`FOUNDATION_UPGRADE_1_19_0_ASSESSMENT.json`](FOUNDATION_UPGRADE_1_19_0_ASSESSMENT.json).

| Feature | Bewertung | Ergebnis |
|---|---|---|
| `ci-supersession-and-integration-queue` seit `1.18.0` | `DECISION_REQUIRED`, durch `DEC-067` aufgelöst | Zehn Runtime-Workflows verlieren die automatische Cancellation laufender SQL-Container-Tests. Wartende, vollständig ersetzte Runs dürfen weiterhin ersetzt werden. Commit-Bindung und fehlende Evidenz werden ausdrücklich geregelt. |
| `session-lifecycle-management` seit `1.19.0` | `RECOMMENDED` | Regeln, drei Schemas und die Erweiterung des bereits ausgewählten lokalen Planners sind integriert. Konkrete Schwellen, Runtime-Persistenz und automatische Nachfolgesitzungen bleiben ungewählt. |

Die CI-Prüfung unterscheidet reine statische Workflows auf temporären GitHub-gehosteten Runnern von Workflows mit SQL-Containern und konfigurierbaren Runnern. `if: always()` belegt für Letztere keine Bereinigung nach harter Unterbrechung. Die konkrete Auswahl und die zehn korrigierten Workflows stehen in [`REPOSITORY_CONTINUITY.md`](REPOSITORY_CONTINUITY.md). Bestehende Cleanup-Schritte und Runner bleiben erhalten.

Die Session-Empfehlung erfordert keine laufende semantische Chat-Analyse, kein regelmäßiges Zusammenfassen und keinen zusätzlichen Modellaufruf. Unbekannte Metriken bleiben unbekannt. Ohne aktuelle vertrauenswürdige Client-Evidenz bleibt die Nachfolgefunktion `UNKNOWN` und eine ausgelöste Fortsetzung manuell. Die Beispielwerte `0.65`, `0.8` und `30000` sind lediglich Source-Testdaten. Eine spätere operative Aktivierung ist eine eigene Projektentscheidung; das Upgrade konfiguriert sie nicht.

## Transfer und semantische Erhaltung

Die Source-Whitelist umfasst für die unveränderte Auswahl zehn Capabilities und drei Adapter insgesamt 103 Zielpfade. Der ursprüngliche Plan enthielt 90 unveränderte Dateien, neun Merge-Prüfungen und vier neue Dateien. Alle bestehenden Dateien stimmten vor dem Transfer mit ihren aufgezeichneten installierten Hashes überein.

Acht aktualisierte Baseline-Dateien werden nach Prüfung aus den Source-Einträgen mit verifiziertem portablem Hash übertragen. Die vier neuen Dateien sind die Session-Schemas und das Planner-Beispiel. Bei `AGENTS.md` ist der Foundation-Block bereits exakt gleich; der projektspezifische Discovery-Abschnitt bleibt als begründeter `INTENTIONAL_OVERRIDE` erhalten. Die Provenienz zeichnet die vollständige Auswahl, den exakten Source-Commit und die Source-/Installationshashes erneut auf. Das Source-Repository wird ausschließlich gelesen.

Strengere Datenschutz- und Neutralisierungsregeln bleiben `PROJECT_STRONGER`. Sprache, Git-/PR-Verfahren, KI-Commit-Kennzeichnung, sichere CI-Strategie und nicht aktivierte Session-Optionen bleiben projektführende Auswahlentscheidungen. Die zentrale v2-Registry, historische Kennungen, der lokale Regelcache, alle bisherigen Capabilities, Adapter und projektspezifischen Validatoren bleiben erhalten. Es werden keine Provider, Credentials, Modelle, externen Runtimes, Branch-Schutzregeln oder Queues konfiguriert.

## Validierung

`FOUNDATION_INTEGRITY` wird getrennt von `PROJECT_SEMANTIC` geprüft. Lokal erfolgreich ausgeführt wurden:

- der Source-Foundation-Validator mit `--profile full` für die vollständige Auswahl: keine Warnungen, Fehler oder Blocker; 102 exakte Baseline-Dateien und der begründete Discovery-Override;
- `Tests/Static/validate_foundation_integration.py`: vollständiges Zwei-Feature-Delta, Source-Version/-Commit/-Manifest, 103 installierte Hashes und unveränderte Capability-/Adapter-Auswahl;
- Registry-Semantik und `validate_identifier_registration.py`: 218 Datensätze einschließlich der über die zentrale Autorität abgeleiteten `DEC-067`;
- `validate_repository_continuity.py` und `validate_sql_container_readiness.py`: elf SQL-Runtime-Workflows ohne automatischen Abbruch laufender Runs und mit authentifizierten Readiness-Probes;
- die repositoryweite Privacy-/Metadatenprüfung und `git diff --check`;
- acht synthetische Session-Fälle für unbekannte Metriken, Checkpoint-Delta, Gleichheit an Soft-/Hard-Schwellen, natürliche Grenzen, Überkapazität und ausdrücklichen Rotationswunsch: erwartete Entscheidungen, keine semantische Analyse und manueller Fallback bei unbekannter Client-Capability;
- zwei ungültige Session-Policies: beide abgewiesen; negative Cancellation-Prüfung für `true`, dynamische Ausdrücke und einen Job-Override trotz `false` auf Workflow-Ebene;
- 18 JSON-Schema-Prüfungen mit PowerShell `Test-Json` für die synthetischen Requests/Decisions sowie Assessment und Provenienz.

Die synthetischen Prüfungen führen keine Session-Erstellung, Provider-Aufrufe oder SQL-Tests aus. SQL-Demo-Inhalte und fachliche Runtime-Verträge werden durch dieses Upgrade nicht geändert; eine Prüfung der Cancellation-Konfiguration ersetzt keinen SQL-Lauf oder Nachweis einer Bereinigung nach harter Unterbrechung. Die durch die Workflow-Änderungen ausgelösten PR-Runs liefern ihre eigene, an den Integrationsstand gebundene Runtime-Evidenz.
