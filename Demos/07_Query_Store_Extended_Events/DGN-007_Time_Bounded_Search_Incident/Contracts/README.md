# DGN-007 – Prospektiver Reproduktionsvertrag

| Merkmal | Wert |
|---|---|
| Status | `STATIC_PROSPECTIVE_CONTRACT` |
| Entscheidung | `DEC-068` in [`.ai/DECISIONS.md`](../../../../.ai/DECISIONS.md) |
| Vertragsrevision | [`incident-acceptance.contract.json`](incident-acceptance.contract.json), `dgn007-prospective-acceptance/v1` |
| Implementierung | [reiner Evaluator](../../../../Tests/Contracts/dgn007_prospective_acceptance.py) |
| Abnahmegrenze | Prädikate und Konsistenz synthetischer Records; keine SQL-Runtime-Abnahme |

Die bisherigen [neutralen Kontrollcaptures](../Automated/README.md) prüfen
Last, Zeitfenster, Profile und ausgeführte Planmengen unabhängig von der
Performancewirkung. Dieser getrennte Vertrag legt die spätere
Reproduktionsbewertung vor frischen Bestätigungsläufen fest. Der Evaluator
nimmt bereits typisierte skalare Records entgegen. Er startet keine Prozesse,
öffnet keine Dateien oder SQL-Verbindungen und liest keinen `sqlcmd`-Output.
Ein Fixture-PASS bestätigt ausschließlich die Berechnung und Recordkonsistenz.

## Vorab festgelegte Methode

Je Zielversion sind genau sechs frische Lifecycles in zwei festen Blöcken
vorgesehen: `AB → BA → AA` und `AA → BA → AB`. Für SQL Server 2019, 2022 und
2025 gelten Major/Compatibility-Paare `15/150`, `16/160` und `17/170`.
Jede Version wird einzeln bewertet; Metriken verschiedener Versionen werden
nicht gepoolt. Die künftige vollständige Matrix verlangt alle drei Ergebnisse.

Die Lifecycles einer Version laufen seriell. Das bestehende Mindestprofil
von vier logischen CPU-Kernen und 8 GB sowie höchstens eine gleichzeitig
aktive SQL-Session je Lifecycle bleiben erhalten. Die Phasen dürfen seriell
neue Sessions öffnen. Auf einem gemeinsamen lokalen Host ist höchstens eine
Version gleichzeitig aktiv; Matrixjobs auf getrennten GitHub-Hosts dürfen
parallel laufen. Reguläres Budget und Cleanup-Budget bleiben 180 und
60 Sekunden je Lifecycle. Das ist ein deklarativer Vertrag, noch keine
gemessene Ressourcen- oder Laufzeitattestation.

Alle Fenster verwenden dieselben Parameterpaare und Ergebniszahlen:

| Bedingung | tatsächliche Requestfolge | Ergebniszeilen in derselben Reihenfolge |
|---|---|---|
| A | `(8,3)`, `(1,3)`, `(5,3)`, `(1,1)` | 228, 2.286, 1.144, 571 |
| B | `(1,3)`, `(8,3)`, `(5,3)`, `(1,1)` | 2.286, 228, 1.144, 571 |

Je Fenster sind genau vier reguläre Suchausführungen und insgesamt
4.229 Ergebniszeilen erforderlich. AB bezeichnet T0=A/T1=B, BA T0=B/T1=A,
AA T0=A/T1=A. T0 und T1 behalten ihre chronologischen WindowIds; insbesondere
wird das BA-Vorzeichen nicht aus einem unverändert übernommenen T1−T0-Delta
abgeleitet. Die künftige Übertragung muss die acht Suchrequests jedes
Lifecycles einschließlich IDs, Reihenfolge, Parameterpaaren und Ergebniszeilen
liefern. Die heutigen 30-/35-Ausgaben liefern diesen vollständigen typisierten
Record noch nicht.

## Gerichtetes Symptom und getrennte zusätzliche Evidenz

Die primäre Metrik ist gewichtete Statement-Duration in Mikrosekunden.
CPU und Logical Reads bleiben ergänzende Metriken; eine nachträgliche Auswahl
der günstigsten Metrik ist ausgeschlossen. Für die vier AB-/BA-Lifecycles
einer Version werden die Kontraste berechnet:

```text
dAB = Duration(T1, B) − Duration(T0, A)
dBA = Duration(T0, B) − Duration(T1, A)
AA_Duration = max(abs(Duration(T1, A) − Duration(T0, A))) aus beiden AA-Läufen
DurationSymptom = alle vier Kontraste > 0 UND min(Kontraste) > AA_Duration
```

Zusätzlich muss global einer dieser beiden Zweige erfüllt sein:

1. Alle vier AB-/BA-Lifecycles besitzen innerhalb ihres eigenen Lifecycles
   unterschiedliche vollständig gebundene aktive Hashmengen zwischen T0/T1.
   Nur positive reguläre Ausführungen aus dem validierten Parent-/Variant-Scope
   zählen. Unterschiedliche Plan-IDs bei gleichem Hash genügen nicht.
2. Die vier B−A-Kontraste der Logical Reads sind einheitlich positiv oder
   einheitlich negativ. Ihr kleinster Absolutbetrag liegt strikt über dem
   größten absoluten AA-Reads-Drift aus beiden AA-Läufen. Es gibt keinen
   Wechsel auf CPU oder eine andere Profilmetrik.

```text
Akzeptanz = valide Records UND DurationSymptom
            UND (vollständiger Planfingerprint-Zweig ODER Reads-Profilseparation)
```

Der Reads-Zweig ist eine ausdrücklich strengere automatisierte Voraussetzung
gegenüber dem allgemeinen Plan-oder-Laufzeitprofilvertrag aus
[`ADV-007`](../../../../Documentation/Project_Planning/ADV_007_LAB_VP5_DESIGN.md).
Er verhindert, dass dasselbe Duration-Prädikat zugleich als Symptom und
zusätzlicher Profilbeleg ausgegeben wird. Beide Reads-Richtungen sind von
Anfang an zulässig: unterschiedliche Arbeit bedeutet keine Reads-Regression.
Die Metriken stammen aus derselben Capturequelle und sind kein statistisch
unabhängiger Nachweis. Es gibt weder einen Mindestplanzähler noch eine
universelle Ratio oder absolute Performancegrenze.

Planhashes werden nur innerhalb desselben Lifecycles verglichen. Verschiedene
IDs oder gleich aussehende Hashes aus verschiedenen Datenbanken begründen
keine Identität. Eine Hashmengen-Unterscheidung belegt keine bestimmte Planform
oder Kompilierungsursache. Auch die vollständige Akzeptanzregel prüft nur eine
begrenzte Reproduktionsvoraussetzung, keine Ursachenhypothese.

Der explorative [2019-Kontrollnachweis](../../../../Documentation/Project_Planning/DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md)
enthält einen BA-Kontrast von 1.155,25 µs innerhalb eines AA-Drifts von
1.713,5 µs. Eine synthetische Characterization dieser Überlappung muss unter
der neuen Regel `SKIP_EVIDENCE_MISSING` ergeben. Die alten Captures werden
weder als vorab eingefrorene Bestätigungsläufe übernommen noch durch einen
nachträglich angepassten Schwellenwert aufgewertet.

## Record-, Präzisions- und Ergebnisgrenzen

Der Evaluator prüft Version, Block/Slot, Scope, Lifecycle-ID, Phasenfolge,
Cleanup- und Abwesenheitsstatus sowie Fenster-, Request-, Queryfamilien-,
Plan- und Union-Zuordnungen. Counts, IDs und Bedingungen müssen vollständig
und widerspruchsfrei sein. Nur erfasste Planzeilen mit positiver regulärer
ExecutionCount dürfen die aktive Menge bilden. Die Union muss genau den
Fenstern entsprechen; ungenutzte historische Katalogpläne werden nicht
hinzugefügt. Die Herkunft all dieser Angaben wird damit nicht attestiert.

Metriken sind endliche nichtnegative `Decimal`-Werte; `bool`, binäre Python-
Floats, NULL, NaN und Infinity sind keine zulässigen metrischen Eingaben.
Kontraste und Grenzen werden exakt über `Fraction(Decimal)` verglichen,
unabhängig vom globalen Decimal-Kontext. Die im JSON festgelegten Grenzen für
Ziffernzahl und Exponent begrenzen die technische Recordrepräsentation und
den Rechenaufwand; sie sind keine Performance-Golden-Values. Gültige
Null-Baselines bleiben für absolute Kontraste zulässig. Eine Ratio ist kein
Bestandteil der Abnahme. Die bestehende Zeilentoleranz `0.000001` behandelt
ausschließlich die Rundung der SQL-`float`-Rows-Aggregation.

Zeitangaben verwenden ganzzahlige UTC-Ticks mit 100-ns-Auflösung ab
`0001-01-01T00:00:00Z`, im Bereich `0..3155378975999999999`. Die Plan-Endzeiten
müssen innerhalb des deklarierten Ausführungsfensters und Katalogintervalls
liegen. Block/Slot prüfen nur die deklarierte Reihenfolge; tatsächliche
Lifecycle-Chronologie, Ressourcen und die 180-/60-Sekunden-Budgets werden
noch nicht attestiert. Der spätere Collector muss die Herkunft und
verlustfreie Zuordnung der Query-Store-Zeiten
verifizieren; eine stillschweigende Kürzung auf Python-Mikrosekunden wäre
keine gleichwertige Übertragung.

Es gelten ausschließlich die Codes aus
[`FWK-012`](../../../00_Framework/Contracts/FWK-012_Status_Error_Skip_Contract.md).
Cleanupfehler dominieren Timeouts und frühere Fehler. Fehlende oder
widersprüchliche Pflichtrecords und Bindungen ergeben `FAIL_CONTRACT`;
ungültige Metriken oder Ergebnisinvarianten `FAIL_RESULT_CONTRACT`.
Vollständige gültige Records ohne tragfähige Separation ergeben
`SKIP_EVIDENCE_MISSING`. Gleichheit an einer strikten Grenze ist ebenfalls
kein ausreichender Nachweis. Ein kontrollierter Skip wird nicht als PASS
oder als misslungene Produkteigenschaft ausgegeben.

## Quellenbindung und noch fehlende Runtime-Anbindung

Das JSON bindet die vorhandenen SQL-/Manifestquellen mit SHA-256 über UTF-8
und ausschließlich CRLF→LF-Normalisierung. Der statische Validator prüft diese
Quellen gegen das Repository. Der reine Evaluator bindet den kanonischen
Vertragsdigest und einen separaten Quelldigest an seine Records. Eine
Digestgleichheit ist Integritätsmetadatum, keine Herkunfts-, Autorisierungs-
oder Vorabfreeze-Attestation. Die konkrete kanonische Serialisierung ist in
`contract_from_mapping()` dokumentiert.

Ein späterer Collector muss vor dem SQL-Start den integrierten Freeze-Stand,
die Quellen, Zielinstanz, Ressourcen und Reihenfolge verifizieren. Er muss
skalare Metriken und Zeitangaben verlustfrei übertragen, die vollständigen
Request- und Familienrecords erfassen und Cleanup unabhängig bestätigen.
Der heutige Statusrunner, die SQL-Batches, neutralen Capture-PASS-Ausgänge
und Teilnehmerartefakte werden durch diesen Schnitt nicht verändert.

Danach folgen frische prospektive Bestätigungsläufe. Incidentfreigabe,
Compile-Ursache, Alternativhypothesen, XE-/Wait-Kontext, reversible Mitigation,
T2, vollständige Capstone-Matrix, Teilnehmerübergabe und Szenariopromotion
bleiben offen. Der JSON-Vertrag ist kein ausführbares FWK-Manifest und keine
Freigabe für SQL-Runtime auf vorhandenen Instanzen.

Der getrennte [skalare Collector-Transport](COLLECTOR_TRANSPORT.md) ergänzt
jetzt die reine JSON-Decodierung mit genauer Decimal-/100-ns-Darstellung.
Fehlende Ergebniszeilen je Request bleiben `NOT_CAPTURED`/`None`; es werden
keine Erwartungswerte als Messwerte ergänzt. Das ist ausschließlich ein
Transport-Vorschnitt, ohne SQL-Producer, Coordinator oder Runtime-Abnahme.

## Statische Prüfung

```powershell
python Tests/Static/validate_dgn007_prospective_acceptance.py
python Tests/Static/test_dgn007_prospective_acceptance.py
```

34 synthetische Tests und der Quellenvalidator bestanden lokal. Der separate
Workflow `dgn007-prospective-acceptance.yml` führt ausschließlich
diese reinen Prüfungen auf einem temporären GitHub-Checkout aus. Er erzeugt
keine SQL-Ressource und exportiert keine Diagnosedaten.

Methodenentscheidung: `DEC-068`; fachlicher Bezug: `ADV-007`, `LO-M07-04`,
`LO-M06-08`, `LO-M03-07`. Technische Primärquellen, geprüft am 2026-10-07:
[Query-Store-Runtime-Statistik](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17),
[Planmetadaten](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17),
[Python Decimal](https://docs.python.org/3/library/decimal.html).
Die Kontrollseparationsregel ist eine Projektmethode, keine dokumentierte
SQL-Server-Produkteigenschaft.
