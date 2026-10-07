# DGN-007 – Synthetisches Sättigungs- und Acquisition-Gegenmodell

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-07 |
| Status | `IMPLEMENTED_SYNTHETIC_MODEL` – keine Runtime-/Methodenfreigabe |
| geprüfte Repositorybasis | `b68d32a87984337b7330aa5f7f97e338ec963971` nach PR74 |
| Grundlage | [Suffizienzreview](DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md), Abschnitt 6 |
| Geltungsbereich | `PROJECT_SEMANTIC`; ausschließlich synthetisches Oracle |
| Abnahmegrenze | Keine QS-Erfassung, Runtime-/Herkunftsattestation, Methoden- oder Incidentfreigabe |

## Zweck und getrennte Ergebnisse

Das [Modul](../../Tests/Contracts/dgn007_saturation_countermodel.py) untersucht
den expliziten Zählschluss aus PR74. Es ergänzt das unveränderte
[deklarative Voraussetzungenmodell](DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md).
Das neue Modell verwendet synthetische Ausführungstokens als unabhängig
deklarierte Ground Truth. Reale QS-RuntimeStats liefern keine individuellen
Ausführungstokens; diese API ist kein Collector- oder Decoderformat.

`evaluate_countermodel(case, expected_binding)` liefert ein unveränderliches
`CounterResult`. Callerfassung, kollektive Bucketzuordnung und kontinuierlicher
Zustand sind getrennte Claims mit `CONDITIONALLY_SUPPORTED`, `NOT_ESTABLISHED`
oder `REFUTED`. Ein positiver Claim gilt ausschließlich in der ausdrücklich
deklarierten Modellwelt. Feste Issues sind Modelllabels, keine neuen
FWK-012-Statuscodes. Sämtliche Runtime-, Methoden- und exakten Zeitclaims bleiben
falsch. Das Modell startet keine Prozesse und öffnet keine Dateien, SQL- oder
Netzwerkverbindungen. Es verwendet ausschließlich die Python-Standardbibliothek.

## Nichtzirkuläre Sättigung und Stagefolge

Die zwölf unabhängigen Oraclecalls beschreiben vier Prior-, vier T0- und vier
T1-Calls mit eigener Quellen-/Generationsbindung und Start-/Endordinalen.
Die geplante Kardinalität und die tatsächlichen Callrecords samt ausdrücklich
deklariertem Erfolg werden getrennt geprüft. Ein Call muss genau ein gebundenes Zielstatement ausführen.
Die vier kumulativen Snapshots sind `BASELINE`, `T0_POST`, `T1_POST` und `FINAL`.
Sie sind ein enger Modellumfang, keine Implementierung der acht vorgeschlagenen
Runtime-Acquisitionstages aus PR73.

Jede Rawaufnahme wird vor günstiger Scopefilterung geprüft. Gezählt werden
synthetische Einheiten, die innerhalb derselben Aufnahme injektiv einer
bereits abgeschlossenen zulässigen Ausführung entsprechen müssen. Dieselbe
historische Einheit darf in einer späteren kumulativen Aufnahme erneut
vorkommen. Ein zukünftiger T1-Token gehört nicht zum T0-Präfixuniversum.
Vollständige Callerfassung wird nicht als Voraussetzung eingegeben: Sie folgt
im Modell aus eindeutiger Teilmengenzählung und Sättigung 4→8→12.

Im OFF-Kandidaten gilt 0→4→8 nur unter ausdrücklich deklarierter unabhängiger
historischer Ausschlussprämisse. Nullcounts oder ein Statepunkt ergänzen diese
nicht. Das Modell führt keine OFF-/CLEAR-Operation aus und entscheidet keinen
neuen positiven QS-Konfigurationszweig.

Vollständige keyweise Differenzen, T0-Postabschluss vor T1 und unveränderte
frühere Gruppen tragen zusätzlich die kollektive Zuordnung der jeweils vier
Fenstercalls zu unterschiedlichen Buckets. Gleiche Gesamtsummen bei
Intervallsplit, Tokenaustausch oder Fremdkompensation reichen nicht. Individuelle
Parameter→Plan-Zuordnung und QS↔SYSUTC-/Katalogzeitgleichheit folgen nicht.

## Coverage, Metriken und kontinuierlicher Zustand

Die finale Familienmenge wird auf die vier Aufnahmen zurückgebunden.
Unbekannte frühere Zero-/Varianten-Coverage bleibt unbekannt. Sie verhindert
den vollständigen Familien-/Bucketclaim; bereits korrekt gesättigte positive
Oracleeinheiten können trotzdem den engeren Callerfassungsclaim tragen.

Die vier gelieferten Mittelwerte Duration, CPU, Reads und Rows werden über
`Fraction(Decimal)` exakt gewichtet. Frühere Gruppen behalten Counts, die
vier Metriken und positive First-/Last-Extrema. Gleiche Counts bei verändertem
Profil oder Extrema erfüllen die konservative Modellstabilität nicht.
Unterschiedlich gerundete Mittelwerte bei anderer Fragmentaufteilung bleiben
ein sichtbares Gegenbeispiel. Exakte Signaturgleichheit ist ausschließlich
eine Modellregel, keine Entscheidung der offenen SQL-Float-Stabilitätsregel.
Es gibt kein aus Fixtures abgeleitetes Epsilon oder Zeitfensterpuffer.

Das Modell vergleicht das separat deklarierte Pulsintervall mit dem
Suchcallbucket. Es implementiert keinen Runtime-Pulscall oder Delta1-Beleg.
Ein Puls in I0 sagt nichts über Suchcalls in einem anderen Intervall aus.
Für den kontinuierlichen Zustandsclaim ist eine ausdrücklich vollständige
deklarierte Übergangshistorie nötig, im RW-Kandidaten vom ersten Prior-Call
bis zum Finalcapture-Ende, im historisch ausgeschlossenen Kandidaten vom
ersten T0-Call bis zum Finalcapture-Ende. Die gemeinsame Quellen-/Zielbindung
und gültige Call-/Aufnahmefolge gelten auch für diesen Claim; bekannte
Zustandslücken innerhalb dieser Domain
widerlegen ihn unabhängig von unbekannter Historienvollständigkeit. Ein
Zustandspunkt vor ihrem Anfang wird nur bei ausdrücklich vollständiger
Historie bis zum Anfang fortgeschrieben; UNKNOWN erlaubt keine solche Ableitung. Unbekannte Kontinuität wird nicht aus
passenden Counts abgeleitet. Eine RO-Lücke ohne verlorenen Call ist mit
bedingter vollständiger Callerfassung vereinbar. Die vorgeschlagenen strengeren
Methodengates bleiben unverändert offen.

## Prüfung und Folgearbeit

Die [Gegenproben](../../Tests/Static/test_dgn007_saturation_countermodel.py)
prüfen Fremdkompensation, Doppelzählung, kumulative Wiederholung, zukünftige
Tokens, historischen Ausschluss, Replay/Generationmix, Löschung/Repopulation,
Intervallsplit, Pulsgrenze, späte Zero-Varianten und Metrik-/Extremadrift.
Malformed Records einschließlich nichtkanonischer Enumobjekte, unbekannte
Prämissen und bekannte Widersprüche erhalten
keine positive Gesamtattestation. Eingabegrenzen gelten ausschließlich für
synthetische Fixtures und ersetzen keine SQL-Payload-, Poll- oder Kostenlimits.

| technischer Modellbound | Wert |
|---|---|
| Calls / kumulative Aufnahmen / Fenster | semantisch 12 / 4 / 2 |
| Rawfragmente je Aufnahme / Tokens je Fragment | höchstens 64 / 64 |
| Familienmitglieder / Coveragerecords je Aufnahme | höchstens 16 / 16 |
| Zustandsübergänge / deklarierte destructive Ordinals | höchstens 64 / 64 |
| eigene IDs und Ereignisordinals | exakte Integer 1 bis 10.000; Callordinal je Stage 1 bis 4 |
| einzelne Countwerte | −64 bis 64 als Eingabe; NULL/negative Werte werden widerlegt |
| dokumentierte Ausführungstypen | 0/3/4; positive 3/4 ersetzen keine erfolgreichen regulären Oraclecalls |
| deklarierte 100ns-Zeitwerte | exakte Integer 0 bis 3.155.378.975.999.999.999 |
| Metrikwerte | endliche nichtnegative Decimal, höchstens 34 Stellen, Exponent −30 bis 20 |

Diese Grenzen beschreiben endliche Pythonfixtures. Eigene Ereignisordinals und
deklarierte Zeitwerte sind unterschiedliche Domains; daraus folgt keine
gemeinsame Clock- oder Scopeattestation.

Der bestehende [Statikworkflow](../../.github/workflows/dgn007-assignment-prerequisites.yml)
prüft beide Modelle separat auf einem temporären Checkout. Der alte
42-Test-Step bleibt erhalten; SQL-Runtime wird nicht gestartet.

```powershell
python Tests/Static/test_dgn007_saturation_countermodel.py
python Tests/Static/test_dgn007_assignment_prerequisites.py
python Tests/Static/validate_dgn007_prospective_acceptance.py
python Tests/Static/test_dgn007_prospective_acceptance.py
```

Am 2026-10-07 bestanden tatsächlich 51 neue Testmethoden und die unveränderten
42 Voraussetzungstestmethoden. Beide Suiten prüfen ausschließlich synthetische
Claims. Der unveränderte v1-Validator und seine 34 Fixtures, die elf
Governance-/Projektvalidatoren und fünf Frameworkprüfungen bestanden ebenfalls.
Unabhängige Reviews führten zu Gegenproben für ungültige Ausführungstypen und
Ziel-/Zeitanker des gesonderten Zustandsclaims. Die finale Bindung wird vor
Integration unabhängig überprüft.
Das konkrete [Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md)
ist inzwischen vorbereitet: Acquisition-/Floatkandidat, tatsächliche Freeze-/
Host-/Zugangsgrenze und Kostenplan mit weiterhin offenen Gates. Der
[Offline-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md) ist statisch implementiert;
die getrennte [Kantenprüfung](DGN_007_EXECUTION_EDGE_VERIFIER.md) ist ebenfalls
statisch implementiert. Import-/Launcherentwurf PROPOSED; tatsächliche
Importumgebung bleibt offen, kein SQL.
Vor gemeinsam versionierter Umsetzung bleibt die Methodenentscheidung offen. Ein
synthetisches PASS schließt keines dieser Runtimegates. v1, G13, DEC-068,
historische FAILs, PR68 und der zurückgestellte API-Schnitt bleiben erhalten.
Incident-, Ursachen-, Mitigations-, Capstone-, Teilnehmer- und Szenariofreigabe
bleiben offen.

Technische Primärquellen erneut geprüft am 2026-10-07:
[RuntimeStats](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17)
beschreibt die gruppierte Aggregation aktiver Fragmente und Ausführungs-Endzeiten;
[CAST/CONVERT](https://learn.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-ver17)
beschreibt die verlustfreie Darstellung einzelner Floatwerte mit Style3.
Der synthetische Tokenschluss und die Stabilitätsprüfung sind Projektmodelle,
keine dokumentierten QS-Ausführungsidentitäten oder Snapshotgarantien.
