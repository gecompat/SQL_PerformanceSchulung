# ADV-008 · `OPT-009` Parametersensitive Planoptimierung – Umsetzung und Deckübernahme

| Feld | Wert |
|---|---|
| Arbeitspaket | `ADV-008` (Demo), `ADV-010` (Folien) |
| Status | `IMPLEMENTED_FOR_REVIEW` |
| Datum | 2026-08-03 |
| Demo | `OPT-009` – `Demos/04_Optimizer_Statistics_Plans/OPT-009_Parameter_Sensitive_Plans` |
| Lernziel | `LO-M03-08` |
| Claim | `ADV-CLM-019` |
| Quellen | `SRC-001`, `SRC-007`, `SRC-008`, `SRC-048` |
| Folienspezifikation | `Documentation/Curriculum/ADV_010_SLIDE_SPECIFICATION_M03_LO08_PSP.md` |
| Deck | 94 → 98 Folien |
| Werkzeug | `Tools/build_adv010_slides.py` |
| Prüfer | `Tests/Static/validate_adv008_opt009.py`, `Tests/Static/validate_adv010_deck_integration.py` |
| Entscheidungen | `DEC-057`, `DEC-058`, `DEC-059` |

## 1. Zweck des Schnitts

`QRY-004` endete mit einem ausdrücklichen Ausblick: Parameter Sensitive Plan Optimization und Optional Parameter Plan Optimization lösen jeweils eine eigene Problemform und sind an Version, Compatibility Level und Eignung gebunden. Dieser Schnitt löst den ersten Teil ein. Er liefert die Demo `OPT-009`, den zugehörigen statischen und laufzeitbezogenen Prüfvertrag sowie vier Vertiefungsfolien, die als geschlossener Block in das aktive Deck übernommen wurden.

Optional Parameter Plan Optimization bleibt `OPT-010` vorbehalten und wird hier weder bewertet noch vorweggenommen.

## 2. Fachlicher Aufbau der Demo

Die Demo trennt Befund und Deutung über sieben Phasen. Alle Phasen laufen in einer markergeschützten Demodatenbank `SQLPERF_LAB_OPT009_<RunToken>`.

| Phase | Zweck | Ergebnis |
|---|---|---|
| `00_Preflight` | Version, Berechtigung, Zielname | `PASS` oder kontrollierter `SKIP` |
| `10_Setup` | Datenbank, schiefe Verteilung, vier Vergleichsobjekte, Evidenztabelle | `PASS` |
| `20_Baseline` | selektiver Wert kompiliert zuerst, Optimierung aus | eine Planform, dominanter Wert benachteiligt |
| `30_Demonstration` | dominanter Wert kompiliert zuerst, Optimierung aus | eine Planform, selektiver Wert benachteiligt |
| `40_Observation` | reine Auswertung ohne neue Ausführungen | Symmetrie der Mehrkosten, Ergebnisgleichheit |
| `50_Mitigation` | Optimierung auf Datenbankebene ein | Dispatcherplan, Query Variants, Kardinalitätsgrenzen |
| `60_Comparison` | Abwahl auf Abfrageebene bei eingeschalteter Datenbankeinstellung | kein Dispatcherplan, gleiches Ergebnis |
| `90_Cleanup` | markergebunden und idempotent | `PASS` |

Die Datenverteilung ist bewusst extrem: 99 000 von 100 000 Zeilen tragen denselben Eigentümerschlüssel, die übrigen verteilen sich zu je fünf Zeilen auf 200 weitere Schlüssel. Der Index auf dem Schlüssel ist nicht abdeckend, sodass der Zugriffsweg über Suche mit Schlüsselsuche gegenüber einem Scan tatsächlich zur Entscheidung steht.

Alle vier Vergleichsobjekte tragen denselben Abfragerumpf und unterscheiden sich ausschließlich im eingebetteten Marker sowie – im Fall der Abwahl – im Hinweis auf Abfrageebene. Damit ist jede Messung eindeutig einem Objekt zuzuordnen, ohne dass die Abfragen fachlich voneinander abweichen.

## 3. Evidenzerhebung und ihre Fallstricke

Die Evidenz wird markerbezogen aus `sys.dm_exec_cached_plans`, `sys.dm_exec_sql_text`, `sys.dm_exec_query_plan` und `sys.dm_exec_query_stats` gelesen. Drei Fallstricke wurden erkannt und behoben:

1. **Selbsttreffer im Plancache.** Die Erfassungsprozedur enthält selbst die Suchmuster. Ohne Gegenmaßnahme hätte ihr eigener Anweisungstext die Muster `%PLAN PER VALUE%` und `%PspOrder%` erfüllt. Alle Muster werden deshalb zur Laufzeit aus Teilstücken zusammengesetzt, sodass die Literale im Quelltext nirgends zusammenhängend stehen. Zusätzlich sind nur die Objekttypen `Proc` und `Prepared` zugelassen, was Ad-hoc-Stapel des Aufbaus ausschließt.
2. **Kommentarverlust in Varianten.** Der vom Produkt erzeugte Variantentext muss den eingebetteten Markerkommentar nicht behalten. Varianten werden deshalb nicht über den Marker, sondern über Tabellenname und den erzeugten Hinweistext erkannt. Diese Erkennung ist datenbankweit statt markerbezogen; die Einschränkung ist in der Demo-README ausgewiesen.
3. **Mehrdeutige Zuordnung der Lesevorgänge.** Ein Dispatcherplan kann mit null logischen Lesevorgängen neben der Variante stehen. Die Auswahl ordnet deshalb nach letzter Ausführung und absteigenden Lesevorgängen, damit die tatsächlich arbeitende Zeile gewinnt.

Query-Store-Sichten werden bewusst nicht verwendet, solange deren Pilotabnahme offen ist. Der statische Prüfer verbietet `sys.query_store_plan` und `sys.query_store_query_variant` in den SQL-Dateien.

## 4. Statuscodes – Korrektur gegenüber den Entwurfsdokumenten

Die Entwürfe `ADV_005_LAB_VP2_DESIGN.md` und `ADV_006_LAB_VP3_VP4_DESIGN.md` verwenden die Codes `SKIP_FEATURE_UNAVAILABLE` und `SKIP_FEATURE_NOT_ELIGIBLE`. Beide stehen **nicht** in der abschließenden Liste aus `Demos/00_Framework/Contracts/FWK-012_Status_Error_Skip_Contract.md` §3 und werden von `Tests/Static/validate_framework_contracts.py` nicht anerkannt. Sie wurden deshalb nicht eingeführt.

| Sachverhalt | Verwendeter Code |
|---|---|
| SQL Server 2019, also vor Verfügbarkeit der Funktion | `SKIP` / `SKIP_VERSION` |
| passende Version, aber kein Dispatcherplan oder weniger als zwei Varianten beobachtet | `SKIP` / `SKIP_EVIDENCE_MISSING` |
| fehlende Plancache- oder Lesevorgangsevidenz | `SKIP` / `SKIP_EVIDENCE_MISSING` |
| erwarteter Nutzen nicht von der Messstreuung trennbar | `WARN` / `WARN_EMPIRICAL_VARIANCE` |

Der statische Prüfer erzwingt diese Disziplin: Jede `SQLPERF_SUMMARY`-Zeile muss einen Code aus der Vertragsliste tragen. Das ist als `DEC-059` festgehalten.

Der Runtime-Runner wertet `SKIP_VERSION`, `SKIP_PERMISSION`, `SKIP_EVIDENCE_MISSING` und `SKIP_TOOL_MISSING` als bestandene Läufe. Ein Lauf auf SQL Server 2019 ist damit ein planmäßiger, kein fehlgeschlagener Lauf.

## 5. Deckübernahme

Vier Folien wurden nach `DEC-058` als geschlossener Block unmittelbar nach dem Block `ADV-009` und vor der Schlussfolie angefügt.

| Stabile ID | Anzeigeposition | Folienteil | Claim |
|---|---|---|---|
| `SLD-M03-121` | 94 | `slide95.xml` | – |
| `SLD-M03-122` | 95 | `slide96.xml` | `ADV-CLM-019` |
| `SLD-M03-123` | 96 | `slide97.xml` | `ADV-CLM-019` |
| `SLD-M03-124` | 97 | `slide98.xml` | `ADV-CLM-019` |

`Tools/build_adv010_slides.py` folgt demselben Bauprinzip wie `Tools/build_adv009_slides.py`: vorlagengebunden auf Anzeigeposition 32, deterministisch über festgelegte Archivzeitstempel und aus stabilen Namen abgeleitete Bezeichner, idempotenzgesichert und atomar über eine Zwischendatei. Zwei Läufe aus unveränderten Kopien erzeugten byteweise identische Archive.

Die einzige Änderung an bestehenden Folien ist erneut der Nenner der Fußzeilenpaginierung (`n / 94` → `n / 98`). Die Schlussfolie bleibt Teil `slide84.xml` und letzte Anzeigeposition.

Erneuerte Prüfsumme:

| Feld | Vorher | Nachher |
|---|---|---|
| SHA-256 | `8f8ccd9ffce73cf4c09220de27e74303644642c31a4204f1921648cba86ac4e6` | `651d533596f30f77db2fdd04c9dd3296306884c5a721ecf3de2f2b6fd536b2b4` |
| SHA-1 | `994eba18625605a491f1082b297d13d55e4410a2` | `c2f0a8ae9f31559a1c35bb5b9a5383bdc19555cf` |

Der Wert wurde an allen vier hinterlegten Stellen fortgeschrieben: `Tests/Static/validate_privacy_metadata.py`, `Documentation/Inventories/SLIDE_STATEMENT_REGISTER.md`, `Documentation/Inventories/SOURCE_MANIFEST.md` und `Documentation/Project_Planning/W2_007_REFINE_CLAIMS_REVIEW.md`.

## 6. Prüfung

`Tests/Static/validate_adv008_opt009.py` prüft Bündelaufbau, Phasenreihenfolge, lexikalische Konsistenz aller SQL-Dateien, die Zulässigkeit sämtlicher Statuscodes, die Trennung der vier Vergleichsobjekte auf ihre Phasen, den abgeschalteten Ausgangszustand, genau eine Abwahl auf Abfrageebene, den markergebundenen und idempotenten Cleanup sowie die Vollständigkeit der Folienspezifikation.

`Tests/Static/validate_adv010_deck_integration.py` prüft das Archiv auf Lesbarkeit, die Anzeigereihenfolge gegen `p:sldIdLst`, je Folie Modullabel, Leitabsatz, vier Aufzählungsabsätze, Fußzeilenpaginierung und Pflichtfragment im sichtbaren Text, je Notizfolie Folienmarker, Kennzeichnungszeile, Tiefenprofil und kanonische Demo, die unveränderten Positionen der Basisfolien, des Blocks `ADV-009` und der Schlussfolie sowie die Übereinstimmung von Register, Traceability-Matrix, Quellenmanifest, Datenschutzprüfer und Spezifikation.

Beide Prüfer wurden negativ getestet; jede Mutation wurde zurückgenommen und der Ausgangszustand byteweise wiederhergestellt.

| Prüfer | Erkannte Mutationen |
|---|---|
| `validate_adv008_opt009.py` | verfälschte Manifestidentität, Gegenmaßnahme schaltet die Optimierung nicht ein, fehlende README-Überschrift, verfälschter Folienmarker in der Spezifikation, vertragsfremder Statuscode, vermischte Vergleichsobjekte in einer Phase, entfernte Abwahl auf Abfrageebene |
| `validate_adv010_deck_integration.py` | unvollständige Folienliste eines Claims, falscher Folienteil im Register, veraltete Prüfsummenfreigabe, auf `SPECIFIED` zurückgesetzter Spezifikationsstatus, im Werkzeug fest verdrahtete Prüfsumme, auf den Vorzustand zurückgesetztes Deck |

Angepasste bestehende Prüfer:

| Prüfer | Änderung |
|---|---|
| `validate_w2_007_presentation.py` | `SLIDE_COUNT` auf 98 |
| `validate_adv009_deck_integration.py` | `TOTAL_SLIDES` auf 98; der Nenner der Fußzeilenpaginierung des Blocks `ADV-009` folgt dem neuen Gesamtumfang |
| `validate_privacy_metadata.py` | `APPROVED_ACTIVE_DECK` auf den neuen SHA-256-Wert |
| `validate_adv_003_curriculum.py` | `ADV-CLM-019` als integriert geführt; Kennzahlen auf sieben aktive Vertiefungsclaims und 14 Vertiefungsfolien |
| `validate_sql_server_lab_test_catalog.py` | erwartete Laufzahl der vollen Matrix von 96 auf 108 |
| `validate_inf_001_execution_path.py` | `run_adv008_opt009.py` und `adv008-opt009.yml` als Pflichtbestandteile |

Die vollständige statische Prüfstrecke läuft grün.

## 7. Wirkung auf die Traceability

| Kennzahl | Vorher | Nachher |
|---|---|---|
| Folien im aktiven Deck | 94 | 98 |
| Vertiefungsfolien im Deck | 10 | 14 |
| `ADV-CLM-*` auf `KEEP` | 6 | 7 |
| `ADV-CLM-*` auf `PLANNED` | 33 | 32 |
| Automatisierte Demos im Labkatalog | 8 | 9 |
| Läufe der vollen Versionsmatrix | 96 | 108 |

## 8. Offene Punkte

1. `OPT-009` steht auf `IMPLEMENTED`, nicht auf `VALIDATED`. Die Runtime-Matrix läuft ausschließlich auf GitHub-gehosteten Runnern und kann vom Arbeitsplatz nicht abgefragt werden. Dasselbe gilt unverändert für `QRY-013` und `QRY-004`.
2. Die visuelle Renderprüfung der vier neuen Folien in PowerPoint steht aus. Der Prüfer bewertet Struktur und Zuordnung, nicht Layoutqualität.
3. Ob der Optimierer die Demoabfrage auf allen Zielversionen tatsächlich als parametersensitiv einstuft, ist eine Laufzeitfrage. Bleibt die Variantenbildung aus, endet die Phase mit `SKIP_EVIDENCE_MISSING`; erzwungen wird nichts.
4. Die datenbankweite Variantenzählung ist eine bewusste Vereinfachung. Sie ist belastbar, solange in der Demodatenbank nur die Demo läuft, und in der Demo-README als Grenze ausgewiesen.
5. `docProps/app.xml` meldet weiterhin `<ap:Slides>0</ap:Slides>`. Der Wert war bereits vor beiden Erweiterungen falsch und wird bewusst nicht korrigiert.
