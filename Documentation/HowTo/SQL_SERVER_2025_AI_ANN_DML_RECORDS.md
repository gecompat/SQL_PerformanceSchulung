# SQL Server 2025: einen aufgezeichneten ANN-UPDATE-Fall prüfen

Diese Leseaufgabe prüft zwei bereits dokumentierte ANN-DML-Lifecycles des
festen Profils SQL Server 17.0.5005.3 unter Linux, Engine Edition 3 und
Compatibility Level 170. Sie startet weder SQL Server noch einen Container,
Client, Provider oder ein Modell.

## Aussage und Grenze

In beiden abgeschlossenen Lifecycles wurde derselbe gültige parameterisierte
UPDATE auf Zeile 23 mit Fehler 42231, State 1 abgewiesen. Der Recordvertrag
verlangt nach dem Rollback `@@TRANCOUNT = 0` und `XACT_STATE() = 0`, unveränderte
Quelldaten und Indexmetadaten sowie den dokumentierten erfolgreichen Cleanup.
Die Generation bleibt `UNKNOWN`.

Das ist ein enges Ergebnis für den aufgezeichneten Build. Es beweist weder
allgemeine UPDATE-Unterstützung noch INSERT, DELETE oder MERGE, Freshness,
Leistung oder Rollenberechtigungen. Die getrennten IDX-012-Rollenbelege gehören
zu einem anderen Profilablauf und werden hier nicht als ANN-Rollennachweis
übernommen. Der ANN-Rollenstatus bleibt `NOT_ESTABLISHED`.

## Reine Offlineprüfung

Der Consumer akzeptiert ein vollständiges Record-Dictionary und ein getrenntes
Binding im Arbeitsspeicher. Der Record enthält das feste Profil, die sechs
historischen Quellenpins, genau zwei geordnete UPDATE-Ergebnisse und den
expliziten Rollenstatus. Das Binding nennt die aktuelle Consumer-/Contract-
Quellkarte sowie `PUREFIXTURE_ONLY` oder `DECLARED_HISTORICAL_CAPTURE`.
Letzteres beschreibt die vom Aufrufer erklärte Herkunft; der Consumer attestiert
sie nicht unabhängig. Auch die geprüften Quellpins belegen keine Herkunft der
übergebenen Records.

```python
from ann_dml_role_evidence import report

summary = report(record, binding)
print(summary)
```

Eine kohärente Eingabe ergibt `WARN`, nicht `PASS`. Das Ergebnis enthält keine
SID, Token, SQL-Fehlermeldung, Vektoren oder Rohkanäle. Der feste Expected-Vertrag
liegt unter
[`Tests/Static/Fixtures/ann/ANN_DML_ROLE.result-contract.json`](../../Tests/Static/Fixtures/ann/ANN_DML_ROLE.result-contract.json).

Die ausschließlich synthetischen Regressionen laufen mit:

```powershell
$env:PYTHONPATH = 'Tests/Static'
python Tests/Static/test_ann_dml_role_evidence.py
```

Ein bestandener Fixturetest ist kein erneuter SQL-Lauf und keine neue
Runtimequalifikation. Für den historischen Ausgangsbefund und seine
Quellhashes siehe die [ANN-DML-Diagnose](../Project_Planning/SQL_SERVER_2025_AI_ANN_DML_REVIEW.md).
