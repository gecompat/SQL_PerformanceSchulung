# ADV-008 / OPT-010 – Review der Optional Parameter Plan Optimization

| Merkmal | Wert |
|---|---|
| Arbeitspaket | `ADV-008` (Schnitt `OPT-010`), `ADV-011` (Deckübernahme) |
| Status | `IMPLEMENTED_FOR_REVIEW` |
| Prüfdatum | 2026-08-02 |
| Demo-ID | `OPT-010` |
| Sicherheitsstufe | `GREEN` |
| Claim | `ADV-CLM-020` |
| Lernziel | `LO-M03-08` |
| Quellen | `SRC-007`, `SRC-026`, `SRC-049` |

## 1. Gegenstand und Abgrenzung

Der Schnitt liefert die Demo `OPT-010` und die vier zugehörigen Vertiefungsfolien gemeinsam. Gegenstand ist ausschließlich die Optional Parameter Plan Optimization, also die Behandlung des Musters `WHERE (Spalte = @p OR @p IS NULL)` durch Dispatcherplan und Query Variants.

Die Abgrenzung ist bewusst scharf gezogen:

- `OPT-009` behandelt die parametersensitive Planoptimierung. Sie wählt anhand geschätzter Kardinalitätsunterschiede aus. Die Demo `OPT-010` verbietet den Bezeichner `PARAMETER_SENSITIVE_PLAN_OPTIMIZATION` in allen SQL-Dateien, damit beide Verfahren nicht gleichzeitig wirken.
- `QRY-004` behandelt die klassischen Strategien für Catch-all-Abfragen, insbesondere `OPTION (RECOMPILE)` und sicher parameterisiertes dynamisches SQL. Diese bleiben die Antwort, wo Optional Parameter Plan Optimization nicht greift.

Die Demo arbeitet mit einer streng gleichmäßigen Verteilung – 2 000 Agenten zu je genau 50 Zeilen bei 100 000 Zeilen insgesamt. Damit lässt sich die beobachtete Wirkung nicht der Datenschiefe zuschreiben; sie folgt allein aus der Gültigkeitsanforderung an eine einzige Planform.

## 2. Aufbau des Bündels

| Phase | Datei | Zielkontext | Prüfgegenstand |
|---|---|---|---|
| `PREFLIGHT` | `00_Preflight.sql` | `master` | Identität, Versionsband, Hauptversion 17, Berechtigungen |
| `SETUP` | `10_Setup.sql` | `master` | markierte Datenbank, Compatibility Level 170, Startzustand `OPTIONAL_PARAMETER_OPTIMIZATION = OFF`, vier Vergleichsobjekte, Evidenztabelle |
| `BASELINE` | `20_Baseline.sql` | Zieldatenbank | selektiver Erstaufruf, genau eine Planform, keine Dispatcher, keine Varianten |
| `DEMONSTRATION` | `30_Demonstration.sql` | Zieldatenbank | umgekehrte Kompilierungsreihenfolge, Nachweis der Reihenfolgeneutralität |
| `OBSERVATION` | `40_Observation.sql` | Zieldatenbank | Auswertung beider Vorphasen, Ergebnisgleichheit, Planformzahl |
| `MITIGATION` | `50_Mitigation.sql` | Zieldatenbank | Optimierung eingeschaltet, Dispatcherplan mit optionalem Parameterprädikat, mindestens zwei Varianten |
| `COMPARISON` | `60_Comparison.sql` | Zieldatenbank | abfragebezogene Abwahl über `USE HINT`, dokumentierte Ausschlussgründe |
| `CLEANUP` | `90_Cleanup.sql` | `master` | markierungsgeprüfter, idempotenter Abbau |

Alle Phasen sind `required` und liefern eine Zusammenfassungszeile nach `FWK-012`.

## 3. Statusdisziplin nach FWK-012 und DEC-059

Die Demo verwendet ausschließlich zulässige Codes:

| Situation | Ausgang |
|---|---|
| Hauptversion kleiner als 17 | `SKIP` / `SKIP_VERSION` |
| fehlende Berechtigung für Datenbank- oder Serverzustand | `SKIP` / `SKIP_PERMISSION` |
| kein auswertbarer Plancache-, Lese- oder XML-Nachweis | `SKIP` / `SKIP_EVIDENCE_MISSING` |
| kein Dispatcherplan oder weniger als zwei Varianten trotz passender Version | `SKIP` / `SKIP_EVIDENCE_MISSING` |
| gleichzeitig auftretendes parametersensitives Prädikat | `WARN` / `WARN_EMPIRICAL_VARIANCE` |
| Messstreuung oberhalb der gesetzten Schranke | `WARN` / `WARN_EMPIRICAL_VARIANCE` |
| Vertragsbruch bei Zeilenzahl, Prüfsumme oder Planform | `THROW 51006` |

Ausbleibende Variantenbildung wird als dokumentierter Befund berichtet. Undokumentierte Ablaufkennzeichen kommen nicht zum Einsatz.

## 4. Negativprüfungen des statischen Vertrags

Der statische Vertrag `Tests/Static/validate_adv008_opt010.py` wurde mit reversiblen Mutationen gegengeprüft. Alle elf Mutationen wurden erkannt.

| # | Mutation | Erkannt |
|---:|---|---|
| 1 | Versionsschranke `@MajorVersion < 17` im Preflight entfernt | ja |
| 2 | Startzustand im Setup auf `ON` gesetzt | ja |
| 3 | Abwahlhinweis im Setup entfernt | ja |
| 4 | XQuery auf das optionale Parameterprädikat entfernt | ja |
| 5 | Attributionsprüfung in der Gegenmaßnahme entfernt | ja |
| 6 | Variantenschranke `@Variants < 2` entfernt | ja |
| 7 | Abschnitt `DOCUMENTED_LIMITS` im Vergleich entfernt | ja |
| 8 | Reihenfolgeprüfung in der Beobachtung entfernt | ja |
| 9 | Idempotenz im Cleanup entfernt | ja |
| 10 | verbotenes Konstrukt `DBCC FREEPROCCACHE` eingefügt | ja |
| 11 | unbalancierte Klammer eingefügt | ja |

## 5. Deckübernahme ADV-011

Die Übernahme erfolgt additiv nach `DEC-057` und `DEC-058`. Der Block schließt unmittelbar an `ADV-010` an; die Schlussfolie bleibt letzte Anzeigeposition.

| Stabile ID | Folienteil | Anzeigeposition | Claim |
|---|---|---:|---|
| `SLD-M03-131` | `slide99.xml` | 98 | – |
| `SLD-M03-132` | `slide100.xml` | 99 | `ADV-CLM-020` |
| `SLD-M03-133` | `slide101.xml` | 100 | `ADV-CLM-020` |
| `SLD-M03-134` | `slide102.xml` | 101 | `ADV-CLM-020` |

Die einzige Änderung an bestehenden Folien ist der Nenner der Fußzeilenpaginierung (`n / 98` wird zu `n / 102`).

## 6. Kontrollierte Hashfortschreibung

| Merkmal | Vorher | Nachher |
|---|---|---|
| Folienzahl | 98 | 102 |
| Größe in Byte | 370 762 | 386 377 |
| SHA-256 | `651d533596f30f77db2fdd04c9dd3296306884c5a721ecf3de2f2b6fd536b2b4` | `e83bfebff93721cc5e5ef907dccc919ab574bcb420dcf8d91af90d4226c7c141` |
| SHA-1 | `c2f0a8ae9f31559a1c35bb5b9a5383bdc19555cf` | `69e5b51abec5100accbaf643b339ec5eb016ff4a` |

Der neue Wert wurde in `Tests/Static/validate_privacy_metadata.py`, `Documentation/Inventories/SLIDE_STATEMENT_REGISTER.md`, `Documentation/Inventories/SOURCE_MANIFEST.md`, `Documentation/Project_Planning/W2_007_REFINE_CLAIMS_REVIEW.md` und in der Folienspezifikation fortgeschrieben. Der Erzeuger `Tools/build_adv011_slides.py` wurde aus dem Vorgängerstand erneut ausgeführt und lieferte ein byteidentisches Ergebnis; der Determinismus ist damit belegt.

## 7. Traceability-Delta

| Artefakt | Änderung |
|---|---|
| `Documentation/Curriculum/TRACEABILITY_MATRIX.md` | `ADV-CLM-020` von `PLANNED` auf `KEEP`, Folien `99, 100, 101` |
| `Documentation/Curriculum/CURRICULUM_ARCHITECTURE.md` | aktive Vertiefungsclaims 7 auf 8, Vertiefungsfolien 14 auf 18 |
| `Documentation/Inventories/SLIDE_STATEMENT_REGISTER.md` | neuer Block `ADV-011` mit vier Zeilen, Entscheidung `KEEP` |
| `Documentation/Demo_Catalog/demo_execution_paths.json` | neuer Eintrag `OPT-010`, `TSQL_TESTDB` |
| `Tests/Lab/performance-lab-matrix.json` | neue Lane `OPT-010`, Laufzahl 108 auf 120 |
| `Tests/Static/validate_inf_001_execution_path.py` | Runner und Workflow registriert |

## 8. Offene Punkte

1. Die Runtime-Abnahme über SQL Server 2019, 2022 und 2025 steht aus. Sie ist ausschließlich über die GitHub-Matrix möglich; von der Entwicklungsumgebung aus lässt sich kein Ergebnis abrufen. Der Status bleibt deshalb `IMPLEMENTED`, nicht `VALIDATED`.
2. Auf 2019 und 2022 ist planmäßig `SKIP_VERSION` zu erwarten. Ein fachlicher Nachweis der Variantenbildung ist nur auf 2025 möglich.
3. Die visuelle Renderprüfung der achtzehn Vertiefungsfolien im Deck steht weiterhin aus. Geprüft sind bislang Struktur, Zuordnung, Paginierung und Textinhalte, nicht die Layoutqualität.
4. `docProps/app.xml` meldet unverändert `<ap:Slides>0</ap:Slides>`. Dieser Vorzustand wird bewusst nicht im Rahmen dieses Schnitts geändert.
