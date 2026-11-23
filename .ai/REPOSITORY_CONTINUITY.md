# Repository-Kontinuität und Actions-Ausfallverfahren

Status: AUTHORITATIVE

Entscheidung: `DEC-063`

## Normalbetrieb

Der Default-Branch `main` wird durch zwei getrennte GitHub-Rulesets geschützt:

1. `Repository Core Safety` verlangt Änderungen über Pull Requests und lineare Historie. Force-Pushes und die Löschung von `main` sind verboten. Dieses Ruleset besitzt keinen Bypass.
2. `Repository CI Gates` verlangt die Checks `registry-integrity` und `repository-governance` gegen den aktuellen `main`-Stand. Ausschließlich der GitHub-Benutzer `gecompat` ist als Bypass-Akteur im Modus `pull_request` zugelassen.

Der Registry-Pfad für GitHub Actions ist über die Repository-Variable `ARTIFACT_REGISTRY_PATH=.ai/identity/registry.json` festgelegt. Die serverseitige Konfiguration wurde am 2026-08-28 aktiviert:

- `Repository Core Safety`: Ruleset-ID `21754402`, <https://github.com/gecompat/SQL_PerformanceSchulung/rules/21754402>
- `Repository CI Gates`: Ruleset-ID `21754415`, <https://github.com/gecompat/SQL_PerformanceSchulung/rules/21754415>
- erforderliche Checks: `registry-integrity` und `repository-governance`, jeweils gebunden an die GitHub-Actions-App-ID `15368`

## CI-Supersession und Bindung der Validierung

`DEC-067` ergänzt die Normalbetriebsregeln um eine konservative Strategie für veraltete Runs. Ein neuer Commit darf einen noch nicht gestarteten Run derselben logischen Änderung vollständig ersetzen. Abgebrochene, ersetzte oder nie gestartete Runs sind keine erfolgreiche Validierung. Für den Merge zählt nur Evidenz zum aktuellen PR-Head gegen den aktuellen Base-Stand beziehungsweise zum exakt definierten und getesteten Integrationskandidaten. Nach einer Änderung an Head oder relevanter Base ist die davon betroffene Evidenz zu erneuern.

Die bestehenden statischen Workflows mit `cancel-in-progress: true` dürfen ihre ersetzten Runs abbrechen: Sie arbeiten auf dem temporären Checkout eines GitHub-gehosteten Runners und erzeugen ausschließlich lokale oder runbezogene Prüfergebnisse. Sie mutieren keine persistenten SQL- oder externen Zielressourcen. Ihre Ergebnisse werden nur dem zugehörigen Commit zugeordnet.

SQL-Runtime-Workflows erzeugen und mutieren Container; ihre Runner sind teilweise über Repository-Variablen konfigurierbar. Die vorhandenen `if: always()`-Cleanup-Schritte belegen keine garantierte Bereinigung nach einer harten Unterbrechung. Deshalb gilt bei diesen Workflows `cancel-in-progress: false` oder keine automatische Cancellation. Die zehn zuvor abbrechbaren Workflows sind `adv008-opt009.yml`, `adv008-opt010.yml`, `adv008-opt015-opt016.yml`, `adv008-qry004.yml`, `adv008-qry013.yml`, `adv017-opt017.yml`, `framework-sql-matrix.yml`, `gate-b-pilots.yml`, `qry006-null-semantics.yml` und `w-cov-001.yml`. Ein bereits laufender Run wird bis zum Ergebnis und regulären Cleanup erhalten. Die bestehenden Concurrency-Gruppen dürfen weiterhin vollständig ersetzte, noch wartende Runs ersetzen.

Eine Integration Queue oder gemeinsame Batch-Validierung wird nicht aktiviert. Eine spätere automatische Cancellation mutierender Validierungen setzt einen dokumentierten, nachweislich idempotenten Cleanup- und Recovery-Vertrag voraus, der auch nach harter Unterbrechung wirksam bleibt. Eine fehlgeschlagene Bereinigung oder unbekannte Runtime-Situation bleibt ein offener Fehler beziehungsweise ungeklärter Zustand und darf nicht in erfolgreiche Evidenz umgedeutet werden. Die Regeln zu `VALIDATION_FAILURE`, `INFRASTRUCTURE_UNAVAILABLE`, `UNKNOWN` und Break-glass gelten unverändert.

## Umfang der DGN-007-Laufzeitprüfung bei Anleitungskorrekturen

Die DGN-007-Matrix in [PR 1188](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/45206075266)
wurde durch eine reine README-Änderung gestartet. Der breite
`Automated/**`-Trigger erfasste die Anleitung wie einen ausführbaren
Eingabepfad. Als Referenz benötigten im [vorherigen gebundenen Lauf](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/44921319212)
die drei Enginejobs jeweils rund 20,5 Minuten. Die DGN-007-Enginejobs
erzeugen eigene Container und führen je sechs Captures samt Abbau aus.

Die einzige dokumentationsbezogene Ausnahme in der DGN-007-Auswahl ist
`Automated/README.md`. Ausführbare Verbraucher verwenden diesen Pfad
nicht. Der Trigger für statische DGN-007-Vertragschecks sowie die
zentralen Datenschutzprüfungen bleibt wirksam. Der
[Selektortest](../Tests/Static/test_runtime_workflow_selector.py) prüft
auch gemischte Änderungen mit SQL und Manifest sowie einen geänderten
Runtime-Job. Unbekannte Eingaben, der manuell ausgelöste Lauf und die
bestehenden Runtime-, Abbau- und Reviewpflichten folgen ihren bisherigen
Verträgen. Die Änderung ergänzt keine zusätzlichen Modelle, Reviewer
oder Logübertragungen.


## Zulässige Klassifikation

Ein CI-Bypass ist ausschließlich bei `INFRASTRUCTURE_UNAVAILABLE` zulässig. Dafür muss mindestens eine der folgenden Bedingungen belegt sein:

- GitHub Status weist einen laufenden, für den erforderlichen Check relevanten Actions-Ausfall oder eine erhebliche Störung aus; oder
- der Job kann in drei aufeinanderfolgenden Versuchen über mindestens 30 Minuten nicht starten oder kein vertrauenswürdiges Ergebnis erzeugen und das Fehlerbild weist auf GitHub Actions beziehungsweise dessen Runner-Infrastruktur statt auf Repository-Code hin.

Ein ausgeführter Check mit einem fachlichen, Schema-, Registry-, Sicherheits- oder sonstigen Projektfehler ist `VALIDATION_FAILURE` und darf nicht umgangen werden. Ist die Ursache nicht eindeutig, gilt `UNKNOWN`; auch dann ist ein Bypass verboten.

## Autorisierung und Auditspur

Nur `gecompat` darf den CI-Bypass verwenden, und nur über die Bypass-Funktion eines bestehenden Pull Requests. Direkte Pushes auf `main`, Force-Pushes und Branch-Löschung bleiben verboten.

Vor dem Merge werden im Abschnitt `Actions-Ausfall / Break-glass` des Pull Requests vollständig dokumentiert:

- Grund, Zeitraum und beobachtetes Infrastrukturfehlerbild;
- betroffene erforderliche Checks sowie PR-, Head- und Base-Referenz;
- lokal ausgeführte deterministische Prüfungen und ihre Ergebnisse;
- nicht lokal reproduzierbare Prüfungen;
- Restrisiko und Bypass-Autorisierung;
- konkrete Verpflichtung zur Nachprüfung nach Wiederherstellung.

Mindestens lokal auszuführen sind, soweit die lokale Laufzeit verfügbar ist:

```powershell
python .ai/foundation/artifact_registry_github/registry_semantic.py validate `
  --registry .ai/identity/registry.json
python Tests/Static/validate_identifier_registration.py
python Tests/Static/validate_repository_continuity.py
python Tests/Static/validate_privacy_metadata.py .
git diff --check
```

Ein Bypass erzeugt keinen grünen Ersatzstatus. Nicht ausführbare Prüfungen bleiben `PENDING`.

## Wiederherstellung

Nach Wiederherstellung von GitHub Actions werden die umgangenen Workflow-Runs gegen den gemergten Commit oder denselben unveränderlichen Head-Commit erneut ausgeführt. Das Ergebnis wird im ursprünglichen Pull Request dokumentiert. Die Nachprüfung erfolgt spätestens am nächsten Arbeitstag nach Wiederherstellung.

Ergibt die Nachprüfung einen fachlichen Fehler, wird unverzüglich ein Korrektur- oder Incident-Arbeitselement registriert und der bekannte gute Zustand wiederhergestellt oder eine geprüfte Korrektur über einen neuen Pull Request eingespielt. Der Break-glass-Vorgang ist erst geschlossen, wenn jede ausstehende Prüfung ein wahrheitsgemäßes Ergebnis besitzt.
