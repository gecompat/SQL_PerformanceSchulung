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
