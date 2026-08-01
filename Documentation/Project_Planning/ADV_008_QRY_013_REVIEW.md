# ADV-008 – Review QRY-013 und ADV-009 Folienspezifikation M03

| Feld | Wert |
|---|---|
| Paket | `ADV-008` (Demo `QRY-013`), `ADV-009` (Folienspezifikation M03) |
| Status | `IMPLEMENTED_FOR_REVIEW` |
| Lernziel | `LO-M03-07` |
| Kanonische Demo | `QRY-013` |
| Sicherheitsstufe | `GREEN` |
| Ausführungspfad | `TSQL_TESTDB` / `SHARED_TEST_INSTANCE` (Stufe 1) |
| Datum | 2026-08-01 |

## 1. Gegenstand

Der Schnitt liefert zwei zusammengehörige Ergebnisse:

1. die ausführbare Demo `QRY-013` unter `Demos/05_Query_Patterns/QRY-013_Client_Session_Context`;
2. die Folienspezifikation `Documentation/Curriculum/ADV_009_SLIDE_SPECIFICATION_M03.md` mit fünf vertiefenden Folien `SLD-M03-101` bis `SLD-M03-105`.

Beide Ergebnisse behandeln dieselbe Fehlvorstellung: die Zuschreibung eines Laufzeitunterschieds an das verwendete Werkzeug. Die Demo ersetzt diese Einzelursachenbehauptung durch zwei unabhängig prüfbare Dimensionen.

## 2. Fachliche Trennung

| Dimension | Wirkung in der Demo | Nachweis |
|---|---|---|
| Sessionkontext | zwei explizit gesetzte, neutrale Profile unterscheiden sich in genau einer dokumentierten `SET`-Option | zwei Cacheeinträge mit zwei verschiedenen `set_options`-Werten bei identischem Ergebnis und identischer Prüfsumme |
| Parameterwert | unveränderter Kontext, anderer Parameterwert | ein wiederverwendeter Plan, abweichende Ergebnismenge und höhere logische Lesevorgänge |
| Ausrichtung | beide Aufrufe unter gleichem Kontext | ein Cacheeintrag, unveränderte Ergebnisequivalenz |

Der Aufbau nennt bewusst kein Produkt und keinen Treiber. Er zeigt, dass ein abweichender Sitzungskontext eine getrennte Planvariante erzeugen kann, ohne dass daraus eine allgemeine Regel über Werkzeuge folgt.

## 3. Warum die Präsentation nicht direkt geändert wurde

Das aktive Deck ist in `Tests/Static/validate_privacy_metadata.py` über `APPROVED_ACTIVE_DECK` per SHA-256 freigegeben. Die Erweiterung entstand deshalb zuerst als Spezifikationsschicht (`DEC-053`). Nach der ausdrücklichen Freigabe des Auftraggebers wurden die Folien unter `DEC-057` additiv in das Deck übernommen; der freigegebene Prüfsummenwert wurde im selben Schnitt kontrolliert erneuert. Die Ansprüche `ADV-CLM-013` bis `ADV-CLM-016` stehen seither auf `KEEP` und tragen die Anzeigepositionen 84 bis 88; die Zählwerte in `Documentation/Curriculum/TRACEABILITY_MATRIX.md` sind entsprechend fortgeschrieben. Der Vorgang ist in `Documentation/Project_Planning/ADV_009_DECK_INTEGRATION_REVIEW.md` dokumentiert.

## 4. Umgesetzte Artefakte

| Artefakt | Pfad |
|---|---|
| Demobündel | `Demos/05_Query_Patterns/QRY-013_Client_Session_Context` (Manifest, sieben Phasen, Cleanup, README) |
| Folienspezifikation | `Documentation/Curriculum/ADV_009_SLIDE_SPECIFICATION_M03.md` |
| Statischer Vertrag | `Tests/Static/validate_adv008_qry013.py` |
| Runtime-Runner | `Tests/Runtime/run_adv008_qry013.py` |
| Runtime-Workflow | `.github/workflows/adv008-qry013.yml` |
| Registrierungen | `Tests/Lab/performance-lab-matrix.json`, `Documentation/Demo_Catalog/demo_execution_paths.json`, `Documentation/Inventories/performance_scenario_inventory.json` |

## 5. Abbruch- und Ausweichverhalten

| Lage | Ergebnis |
|---|---|
| Hauptversion außerhalb 15–17 | `SKIP|SKIP_VERSION` im Preflight |
| fehlende Berechtigung für `CREATE DATABASE` oder Serverzustand | `SKIP|SKIP_PERMISSION` im Preflight |
| Plancache-Evidenz nicht lesbar | `SKIP|SKIP_EVIDENCE_MISSING` in der betroffenen Phase |
| kein Anstieg der logischen Lesevorgänge beim Parameterwechsel | `WARN|WARN_EMPIRICAL_VARIANCE` in der Beobachtungsphase |
| verletzter Ergebnisvertrag | `THROW 51006` |
| fremde oder fehlende Eigentumsmarkierung im Cleanup | `THROW 51004` |

Die Demo setzt keinen instanzweiten Cache zurück. Die Planentwertung erfolgt objektbezogen über `sys.sp_recompile` auf der Demoprozedur.

## 6. Abnahmestand

| Kriterium | Stand |
|---|---|
| statische Verträge vollständig grün | erfüllt |
| Negativprüfung des neuen Prüfers | erfüllt für abweichendes Sessionprofil, nicht idempotenten Cleanup und fehlende Foliensprechnotiz-Marke |
| Katalog-, Inventar- und Labmatrixeintrag | erfüllt |
| Runtime-Abnahme 2019/2022/2025, je zwei Läufe | offen |
| Deckübernahme der fünf Folien und Erneuerung der Freigabeprüfsumme | erfüllt unter `ADV-009` und `DEC-057` |

Der Status bleibt `IMPLEMENTED`, bis der Runtime-Nachweis auf `github-hosted` vorliegt. Nach `DEC-047` entsteht Gate-Evidenz ausschließlich dort.

## 7. Offene Punkte

1. Runtime-Abnahme von `QRY-013` über den Workflow `adv008-qry013.yml`; danach Statuswechsel auf `VALIDATED` in Demo-Katalog, Labmatrix und Inventar.
2. Die Deckübernahme der Folien `SLD-M03-101` bis `SLD-M03-105` ist erfolgt; die vier Ansprüche `ADV-CLM-013` bis `ADV-CLM-016` tragen die Anzeigepositionen 84 bis 88 und die Entscheidung `KEEP`. Der Vorgang ist in `Documentation/Project_Planning/ADV_009_DECK_INTEGRATION_REVIEW.md` dokumentiert; die fachliche Endabnahme der Folien hängt an der Runtime-Abnahme aus Punkt 1.
3. Der nächste ADV-008-Schnitt bleibt `QRY-004_CLASSIC_AND_DYNAMIC`.
