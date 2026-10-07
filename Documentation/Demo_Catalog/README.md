# Demo-Katalog

Der Demo-Katalog ist die zentrale Zuordnung zwischen Schulungsinhalt und technischer Vorführung. Ein Eintrag gilt erst dann als `VALIDATED`, wenn Demo-Vertrag, Quellenprüfung, statische Prüfung und die zutreffende Runtime-Matrix im Repository nachvollziehbar sind.

Für die Ausführung beginnen Sie im [zentralen Ausführungsleitfaden](../HowTo/DEMO_EXECUTION_GUIDE.md). Seine Demo-Links und Manifestpfade führen zu den tatsächlich vorhandenen Paketen; die historisch unterschiedlichen Ordnernummern sind keine Modul- oder Freigabekennung. Der [Demo-Einstieg](../../Demos/README.md) erklärt Platzhalter und tatsächliche Ablage.

## Status und Nachweis richtig lesen

`VALIDATED` ist der Projektstatus einer abgegrenzten Abnahme. `PASS`, `WARN`, `SKIP` und `FAIL` sind Ergebnisse einzelner Ausführungen gemäß [FWK-012](../../Demos/00_Framework/Contracts/FWK-012_Status_Error_Skip_Contract.md). Diese Ebenen werden nicht gleichgesetzt:

- Ein erwarteter `SKIP_VERSION` belegt die kontrollierte Versionsgrenze, aber keine Funktionswirkung auf dieser Version.
- `WARN_EMPIRICAL_VARIANCE` lässt die im Vertrag erfüllten Invarianten bestehen; die eingeschränkte Performance-Richtung darf nicht als Verbesserung dargestellt werden.
- `SKIP_EVIDENCE_MISSING` liefert keinen Effektbeleg. Dass der Runner diesen Ausgang mit Exitcode 0 akzeptiert, ersetzt die fehlende Evidenz nicht.
- `FAIL`, insbesondere `FAIL_CLEANUP`, bleibt ein Fehler. Ein historischer erfolgreicher Lauf hebt einen späteren Fehler nicht auf.

Die folgenden Nachweise sind historische, an Datum und Commit gebundene Abnahmen. Am 2026-10-07 wurden ihre Repository-Reviews und die Metadaten der neun referenzierten Actions-Läufe abgeglichen; alle neun Runs und ihre Matrixjobs waren als erfolgreich abrufbar. Die Ergebnisdetails stammen aus den verlinkten Reviews. Es wurde dafür keine SQL-Runtime neu gestartet. Die Zusammenstellung behauptet weder einen neuen Effektbeleg am aktuellen Head noch eine vollständige Windows-, Editions- oder CU-Matrix. Die automatisierten Nachweise betreffen die dokumentierten Microsoft-Linux-Container; die Verwendung von `*-latest` ist kein festgeschriebener Image-Digest.

## Verbindliche Felder

- Demo-ID und Titel
- Themenblock und Lernziel
- zugehörige Präsentationsabschnitte
- SQL-Server-Version und Compatibility Level
- Edition und Betriebssystem
- Sicherheitsstufe und Ausführungspfad
- benötigte Sessions und Infrastruktur
- erwartete Dauer
- Quellen-, Claim- und Testprofilzuordnung
- Implementierungs- und Validierungsstatus

## Entscheidungspfad je Demo

Abschnitt 13.2 des Masterplans legt eine Stufenleiter fest. Verbindlich gilt die **kleinste ausreichende Stufe**. Die maschinenlesbare Zuordnung steht in [`demo_execution_paths.json`](demo_execution_paths.json) und wird durch `Tests/Static/validate_demo_execution_paths.py` geprüft.

| Stufe | Ausführungspfad | Verwendung |
|---:|---|---|
| 1 | `TSQL_TESTDB` | vorhandene Testinstanz plus eigene synthetische Testdatenbank |
| 2 | `TSQL_TESTDB` | reine T-SQL-Steuerung innerhalb einer isolierten Testinstanz |
| 3 | `CONTAINER` | containerisierte Einzelinstanz zur Bereitstellung oder für reproduzierbare CPU-/RAM-Grenzen |
| 4 | `HYPERV` | Windows-, OS-, Storage- oder Isolationsanforderungen |
| 5 | `MULTI_INSTANCE` | verteilte oder netzwerkabhängige Kernaussage |

Regeln:

- Jede implementierte Demo besitzt genau einen Eintrag. Fehlende und unbekannte Einträge sind ein Prüffehler.
- Stufe und Ausführungspfad müssen zusammenpassen. Die Stufen 1 und 2 verwenden beide `TSQL_TESTDB`.
- Für jeden Eintrag oberhalb von Stufe 2 werden die verworfene niedrigere Stufe und der technische Grund dokumentiert. Ohne diese Begründung schlägt die Prüfung fehl.
- Der Instanzbedarf wird getrennt von der Stufe geführt: `SHARED_TEST_INSTANCE` oder `DISPOSABLE_INSTANCE`. Eine gelbe oder rote Sicherheitsstufe verlangt immer eine Wegwerfinstanz.
- Sicherheitsstufe, Sitzungszahl und Manifestpfad müssen mit `Tests/Lab/performance-lab-matrix.json` und, sofern dort geführt, mit `Documentation/Inventories/performance_scenario_inventory.json` übereinstimmen.

Der Katalog beschreibt den **erforderlichen** Ausführungspfad. Er stellt keine Umgebung bereit und ist keine Eingabe für eine automatisierte Umgebungserzeugung. Die automatisierte Erstellung von Demoumgebungen ist bewusst zurückgestellt.

## Ausführungspfad der implementierten Demos

| Demo-ID | Titel | Sicherheit | Sitzungen | Stufe | Ausführungspfad | Instanzbedarf | Status |
|---|---|---|---:|---:|---|---|---|
| [`QRY-001`](../../Demos/05_Query_Patterns/QRY-001_SARGability/README.md) | SARGability | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| [`OPT-002`](../../Demos/04_Optimizer_Statistics_Plans/OPT-002_Statistics_Anatomy/README.md) | Statistics Anatomy | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| [`OPT-015`](../../Demos/04_Optimizer_Statistics_Plans/OPT-015_Plan_Properties/README.md) | Planweite und operatorbezogene Eigenschaften | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| [`OPT-016`](../../Demos/04_Optimizer_Statistics_Plans/OPT-016_Rebind_Rewind_Spools/README.md) | Rebind, Rewind, Outer References und Spools | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| [`QRY-013`](../../Demos/05_Query_Patterns/QRY-013_Client_Session_Context/README.md) | Anwendung langsam, SSMS schnell | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| [`QRY-004`](../../Demos/05_Query_Patterns/QRY-004_Classic_And_Dynamic/README.md) | Catch-all, Recompile und dynamisches SQL | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| [`OPT-009`](../../Demos/04_Optimizer_Statistics_Plans/OPT-009_Parameter_Sensitive_Plans/README.md) | Parametersensitive Planoptimierung | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| [`OPT-010`](../../Demos/04_Optimizer_Statistics_Plans/OPT-010_Optional_Parameter_Plans/README.md) | Optional Parameter Plan Optimization | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| [`OPT-013`](../../Demos/04_Optimizer_Statistics_Plans/OPT-013_Controlled_Spill/README.md) | Controlled Spill | Gelb | 1 | 2 | `TSQL_TESTDB` | `DISPOSABLE_INSTANCE` | `VALIDATED` |
| [`CON-004`](../../Demos/07_Concurrency/CON-004_Blocking_Chain/README.md) | Blocking Chain | Gelb | 4 | 2 | `TSQL_TESTDB` | `DISPOSABLE_INSTANCE` | `VALIDATED` |
| [`DGN-003`](../../Demos/07_Query_Store_Extended_Events/DGN-003_Query_Store_History/README.md) | Query-Store-Historie | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| [`DGN-005`](../../Demos/07_Query_Store_Extended_Events/DGN-005_Bounded_Extended_Events/README.md) | Begrenzte Extended-Events-Evidenz | Gelb | 1 | 2 | `TSQL_TESTDB` | `DISPOSABLE_INSTANCE` | `VALIDATED` |
| [`OPT-017`](../../Demos/04_Optimizer_Statistics_Plans/OPT-017_Parallelism_Skew/README.md) | Parallele Planbereiche und Skew | Gelb | 1 | 3 | `CONTAINER` | `DISPOSABLE_INSTANCE` | `VALIDATED` |
| [`OPT-003`](../../Demos/04_Optimizer_Statistics_Plans/OPT-003_Sampling_Skew/README.md) | Sampling, Skew und Histogrammgrenzen | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| [`OPT-005`](../../Demos/04_Optimizer_Statistics_Plans/OPT-005_Ascending_Key/README.md) | Ascending Key und Statistikpflege | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| [`CON-006`](../../Demos/07_Concurrency/CON-006_Deadlock_Cycle/README.md) | Reproduzierbarer Deadlock-Zyklus | Gelb | 3 | 2 | `TSQL_TESTDB` | `DISPOSABLE_INSTANCE` | `VALIDATED` |
| [`CON-009`](../../Demos/05_Concurrency_Isolation_TempDB/CON-009_TempDB_Cost_Classes/README.md) | TempDB-Kostenklassen | Gelb | 1 | 2 | `TSQL_TESTDB` | `DISPOSABLE_INSTANCE` | `VALIDATED` |
| [`IDX-006`](../../Demos/04_Rowstore_Columnstore/IDX-006_Page_Splits_Density/README.md) | Page Splits, Density und Fragmentierung | Gelb | 1 | 2 | `TSQL_TESTDB` | `DISPOSABLE_INSTANCE` | `VALIDATED` |
| [`IDX-010`](../../Demos/04_Rowstore_Columnstore/IDX-010_Columnstore_Segments/README.md) | Columnstore-Segmente und Rowgroup-Qualität | Gelb | 1 | 3 | `CONTAINER` | `DISPOSABLE_INSTANCE` | `VALIDATED` |
| [`STL-008`](../../Demos/01_Storage_Pages_Log/STL-008_VLF_Log_Growth/README.md) | VLF-Struktur und Logwachstum | Rot | 1 | 3 | `CONTAINER` | `DISPOSABLE_INSTANCE` | `VALIDATED` |
| [`STL-009`](../../Demos/01_Storage_Pages_Log/STL-009_Commit_Batching/README.md) | Commit-Batching und WRITELOG | Gelb | 1 | 2 | `TSQL_TESTDB` | `DISPOSABLE_INSTANCE` | `VALIDATED` |
| [`RES-007`](../../Demos/06_CPU_Memory_IO_Waits/RES-007_Wait_Scope_Deltas/README.md) | Wait-Scope und zeitbezogene Deltas | Gelb | 3 | 2 | `TSQL_TESTDB` | `DISPOSABLE_INSTANCE` | `VALIDATED` |

`OPT-017` benötigt als erste implementierte Demo Stufe 3, weil vier sichtbare Kerne und ein begrenztes Ressourcenprofil Teil ihres Evidenzvertrags sind. `OPT-013` belastet `tempdb` der gesamten Instanz, `CON-004` hält Sperren über vier Sitzungen; auch sie verlangen deshalb eine Instanz, die zurückgesetzt oder verworfen werden darf.

Die Bedienanleitung für den Weg über eine vorhandene Instanz steht in [`LOCAL_TEST_ENVIRONMENT.md`](../HowTo/LOCAL_TEST_ENVIRONMENT.md).

## Historische Runtime-Ergebnisse je Demo

Die Versionsspalten nennen Engine und Compatibility Level getrennt. Jede Zelle beschreibt zwei vollständige Manifestläufe. „Effekt belegt“ fasst den fachlichen Nachweis des Reviews zusammen und ist kein neuer Statuscode. Lernziel- und Claim-Zuordnung bleiben in den Demo-README-Dateien und der [Traceability-Matrix](../Curriculum/TRACEABILITY_MATRIX.md) maßgeblich.

| Demo-ID | 2019 / CL150 | 2022 / CL160 | 2025 / CL170 | Fachlicher Nachweis / Grenze | Review und Prüfdatum |
|---|---|---|---|---|---|
| `QRY-001` | `PASS` | `PASS` | `PASS` | Ergebnisgleichheit, Seek/Scan und statementbezogene Logical Reads im kontrollierten Modell | [Gate B, 2026-07-24](../Project_Planning/GATE_B_REVIEW.md) |
| `OPT-002` | `PASS` | `PASS` | `PASS` | Sample-/Fullscan-Header, führende Histogrammspalte und Density Vector | [Gate B, 2026-07-24](../Project_Planning/GATE_B_REVIEW.md) |
| `CON-004` | `PASS` | `PASS` | `PASS` | Zwei unmittelbare Blockerbeziehungen, positive Lock-Waits und blockierungsfreie Gegenprobe | [Gate B, 2026-07-24](../Project_Planning/GATE_B_REVIEW.md) |
| `OPT-013` | `PASS` | `PASS` | `PASS` | Identische Ergebnisse, kleinerer Grant und Sort-Spill; Staging-Gegenprobe ohne Spill | [Gate B, 2026-07-24](../Project_Planning/GATE_B_REVIEW.md) |
| `OPT-015` | Effekt belegt | Effekt belegt | Effekt belegt | Normalisierte Planeigenschaften und verringerter Schätzfehler nach Statistikpflege | [Planmechanik, 2026-07-26](../Project_Planning/ADV_008_OPT_015_016_REVIEW.md) |
| `OPT-016` | Effekt belegt | Effekt belegt | Effekt belegt | Outer References, Rebind/Rewind und Spool unter den dokumentierten Query-Hints | [Planmechanik, 2026-07-26](../Project_Planning/ADV_008_OPT_015_016_REVIEW.md) |
| `QRY-013` | Effekt belegt | Effekt belegt | Effekt belegt | Getrennte Sessionkontexte und Parameterdimension bei gleichem Ergebnis | [Sessionkontext, 2026-08-01](../Project_Planning/ADV_008_QRY_013_REVIEW.md) |
| `OPT-009` | `SKIP_VERSION` | Effekt belegt | Effekt belegt | Dispatcher, mindestens zwei Varianten und Grenzen auf geeigneten Versionen; auf 2019 keine PSP-Wirkung geprüft | [PSP, 2026-08-01](../Project_Planning/ADV_008_OPT_009_REVIEW.md) |
| `OPT-010` | `SKIP_VERSION` | `SKIP_VERSION` | Effekt belegt | Optionales Prädikat, Dispatcher und Varianten ausschließlich auf 2025; ältere Versionen prüfen den Skip | [OPPO, 2026-08-01](../Project_Planning/ADV_008_OPT_010_REVIEW.md) |
| `QRY-004` | `WARN_EMPIRICAL_VARIANCE` | `WARN_EMPIRICAL_VARIANCE` | `WARN_EMPIRICAL_VARIANCE` | Ergebnis, Wiederverwendung, Parameterbindung und Cleanup erfüllt; kein beobachteter Read-Vorteil durch Recompile | [Suchstrategien, 2026-08-29](../Project_Planning/ADV_008_QRY_004_REVIEW.md) |
| `DGN-003` | `PASS / OK` | `PASS / OK` | `PASS / OK` | Query-Store-Historie im Pilotvertrag; keine Freigabe des DGN-007-Incidents | [Operativer Nachweis §2, Lauf vom 2026-08-29](../Project_Planning/CURRENT_EXECUTION_STATUS.md#2-runtime-nachweisstand-der-produktiven-demos) |
| `DGN-005` | `PASS / OK` | `PASS / OK` | `PASS / OK` | Begrenzte, gefilterte XE-Evidenz und Cleanup; interaktive Provider-Abnahme separat | [Freigabegrundlage, Lauf vom 2026-08-29](../Project_Planning/LABSCN_005_DGN_005_DETAIL_REVIEW.md) |
| `OPT-003` | `PASS / OK` | `PASS / OK` | `PASS / OK` | Sampling, Fullscan, Skew und Histogrammgrenze | [Abdeckung, 2026-08-29](../Project_Planning/W_COV_001_COVERAGE_IMPLEMENTATION.md) |
| `OPT-005` | `PASS / OK` | `PASS / OK` | `PASS / OK` | Ascending Key, Änderungszähler und Statistikpflege; keine universelle Sync-/Async-Empfehlung | [Abdeckung, 2026-08-29](../Project_Planning/W_COV_001_COVERAGE_IMPLEMENTATION.md) |
| `CON-006` | `PASS / OK` | `PASS / OK` | `PASS / OK` | Opfer 1205, Survivor, Deadlock-Graph und geordnete Gegenprobe | [Abdeckung, 2026-08-29](../Project_Planning/W_COV_001_COVERAGE_IMPLEMENTATION.md) |
| `CON-009` | `PASS / OK` | `PASS / OK` | `PASS / OK` | TempDB-Kostenklassen; keine Abnahme neuer Instanzkonfiguration | [Abdeckung, 2026-08-29](../Project_Planning/W_COV_001_COVERAGE_IMPLEMENTATION.md) |
| `IDX-006` | `WARN_EMPIRICAL_VARIANCE` | `WARN_EMPIRICAL_VARIANCE` | `WARN_EMPIRICAL_VARIANCE` | Split-/Density-/Fragmentierungsmessung und Ergebnis erfüllt; keine allgemeine Fill-Factor-Richtung | [Abdeckung, 2026-08-29](../Project_Planning/W_COV_001_COVERAGE_IMPLEMENTATION.md) |
| `IDX-010` | `PASS / OK` | `PASS / OK` | `PASS / OK` | Klassische CCI-Segmente und Rowgroups im begrenzten Ressourcenprofil; Ordered NCCI zurückgestellt | [Abdeckung, 2026-08-29](../Project_Planning/W_COV_001_COVERAGE_IMPLEMENTATION.md) |
| `STL-008` | `PASS / OK` | `PASS / OK` | `PASS / OK` | VLF und Logwachstum auf dedizierter roter Wegwerf-Lane; keine Storage-Latenzgarantie | [Abdeckung, 2026-08-29](../Project_Planning/W_COV_001_COVERAGE_IMPLEMENTATION.md) |
| `STL-009` | `PASS / OK` | `PASS / OK` | `PASS / OK` | Einzelcommit/Batch, Log-File- und zeitbezogene WRITELOG-Deltas | [Abdeckung, 2026-08-29](../Project_Planning/W_COV_001_COVERAGE_IMPLEMENTATION.md) |
| `RES-007` | `PASS / OK` | `PASS / OK` | `PASS / OK` | Task-/Request-/Instanzscope und Freigabe-Gegenprobe; kein künstlicher ASYNC_NETWORK_IO-Beleg | [Abdeckung, 2026-08-29](../Project_Planning/W_COV_001_COVERAGE_IMPLEMENTATION.md) |
| `OPT-017` | `PASS / OK` | `PASS / OK` | `PASS / OK` | Actual DOP, Exchange, Threadarbeit und serielle Gegenprobe auf vier sichtbaren CPUs; keine allgemeine DOP-Empfehlung | [Operativer Nachweis §2, Lauf vom 2026-09-01 (Europe/Vienna)](../Project_Planning/CURRENT_EXECUTION_STATUS.md#2-runtime-nachweisstand-der-produktiven-demos) |

### Bindung an den geprüften Commit

Die Zeitangaben hier sind die von GitHub gelieferten UTC-Erstellungszeiten (`createdAt`). Die Commitkennung bezeichnet den Run-Head, nicht automatisch den heutigen Repository-Head oder einen späteren Squash-Commit.

| Demos | Actions-Lauf | Erstellzeit UTC | Geprüfter Commit |
|---|---|---|---|
| `QRY-001`, `OPT-002`, `CON-004`, `OPT-013` | [30108023315](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30108023315) | 2026-07-24 16:07:52 | `14ad846e6bae1472aaa60d0e2e3de676c5a54b61` |
| `OPT-015`, `OPT-016` | [30218932252](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30218932252) | 2026-07-26 20:25:18 | `7299be32143408f6f3ef0e779a9613b414c82afe` |
| `QRY-013` | [30699410795](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30699410795) | 2026-08-01 12:17:46 | `706d079a681576064bbbed5489a210b82ef936be` |
| `OPT-009` | [30701731564](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30701731564) | 2026-08-01 13:26:34 | `8831dfcfd1009d4a500bccfc41cb9325b8310c83` |
| `OPT-010` | [30702590969](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30702590969) | 2026-08-01 13:52:05 | `c944abe635ea3cd0a945e5c3bc84cbd26ccde5b3` |
| `QRY-004` | [33222989681](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989681) | 2026-08-29 00:15:31 | `6fd2b1d5170f7658cf0b86ee05314f2ab543adc7` |
| `DGN-003`, `DGN-005` | [33222989682](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989682) | 2026-08-29 00:15:31 | `6fd2b1d5170f7658cf0b86ee05314f2ab543adc7` |
| die neun `W-COV-001`-Demos | [33222989644](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989644) | 2026-08-29 00:15:31 | `6fd2b1d5170f7658cf0b86ee05314f2ab543adc7` |
| `OPT-017` | [33447840232](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33447840232) | 2026-08-31 22:47:34 | `782799ea65d6c6c826d7aa9a86603f1689de897d` |

### Zusätzlich vorhandene Implementierungen

[`QRY-006`](../../Demos/05_Query_Patterns/QRY-006_NULL_Semantics/README.md) bleibt `IMPLEMENTED`: Der [lokale Docker-Nachweis vom 2026-09-20](../Project_Planning/QRY_006_RUNTIME_EVIDENCE.md) umfasst je zwei `PASS` auf 2019/150, 2022/160 und 2025/170 mit Cleanup. Ein Actions-/Runtime-Gate-Nachweis ist dort ausdrücklich nicht ausgeführt. Die Demo gehört deshalb nicht zu den 22 vollständig abgenommenen Einträgen oben.

`DGN-007` besitzt getrennte statische und lokale Runtime-Teilnachweise. Die Grenzen und offenen Fehler stehen im [aktuellen Ausführungsstand](../Project_Planning/CURRENT_EXECUTION_STATUS.md); daraus folgt keine Abnahme des vollständigen Incidents und kein neuer Katalogstatus.

`OPT-015` verwendet einen synthetischen Out-of-range-Statistikfall und wertet Actual-Plan-Eigenschaften normalisiert aus. `OPT-016` lässt den Optimierer die Performance Spool innerhalb eines mit `MAXDOP 1`, `FORCE ORDER` und `LOOP JOIN` begrenzten Plans wählen; der Aufbau ist somit nicht hintfrei. `NO_PERFORMANCE_SPOOL` dient der kontrollierten Gegenprobe.


`OPT-010` trennt das optionale Parameterprädikat `(Spalte = @p OR @p IS NULL)` bewusst vom Schiefefall aus `OPT-009`: Die Gleichverteilung vermeidet im Datenmodell den Schiefefall zwischen belegten Parameterwerten; der Unterschied zwischen NULL und einem belegten Wert bleibt Gegenstand der Demo. Ohne Optional Parameter Plan Optimization entsteht im kontrollierten Aufbau eine Planform, und die Kompilierungsreihenfolge bleibt wirkungslos. Danach weist die Demo Dispatcherplan, optionales Parameterprädikat und Query Variants marker- und objektbezogen im Plancache nach. Die zugehörigen Folieninhalte stehen als Spezifikation in [`ADV_011_SLIDE_SPECIFICATION_M03_LO08_OPPO.md`](../Curriculum/ADV_011_SLIDE_SPECIFICATION_M03_LO08_OPPO.md).

`OPT-009` zeigt zuerst, dass ohne aktivierte Parameter Sensitive Plan Optimization im kontrollierten Aufbau eine Planform je Querytext entsteht und die Kompilierungsreihenfolge deren Eignung für die Parameterwerte beeinflusst. Danach weist die Demo Dispatcherplan, Query Variants und die ausgewiesenen Kardinalitätsgrenzen marker- und objektbezogen im Plancache nach und belegt die Abwahl auf Abfrageebene. Bleibt die Variantenbildung trotz passender Version aus, endet die Phase kontrolliert mit `SKIP_EVIDENCE_MISSING`. Die zugehörigen Folieninhalte stehen als Spezifikation in [`ADV_010_SLIDE_SPECIFICATION_M03_LO08_PSP.md`](../Curriculum/ADV_010_SLIDE_SPECIFICATION_M03_LO08_PSP.md).

`QRY-004` vergleicht drei Implementierungsstrategien für optionale Suchbedingungen unter identischer Datenverteilung: den statischen Catch-all-Querytext, denselben Text mit `OPTION (RECOMPILE)` und sicher parameterisiertes dynamisches SQL aus einer Positivliste. Die Demo stellt keine Rangfolge auf; sie belegt Wiederverwendung, Compilepreis und Injektionssicherheit getrennt. Die zugehörigen Folieninhalte stehen als Spezifikation in [`ADV_009_SLIDE_SPECIFICATION_M03_LO08.md`](../Curriculum/ADV_009_SLIDE_SPECIFICATION_M03_LO08.md) und sind als Anzeigepositionen 89 bis 93 in das aktive Deck übernommen.

`QRY-013` trennt Kontext- und Parameterdimension: Zwei explizit gesetzte, neutrale Sessionprofile erzeugen bei identischem Ergebnis getrennte Cacheeinträge, während ein unveränderter Kontext mit anderem Parameterwert eine abweichende Arbeitsmenge zeigt. Die Demo benennt keinen Client und keinen Treiber als Ursache. Die zugehörigen Folieninhalte stehen als Spezifikation in [`ADV_009_SLIDE_SPECIFICATION_M03.md`](../Curriculum/ADV_009_SLIDE_SPECIFICATION_M03.md) und sind als Anzeigepositionen 84 bis 88 in das aktive Deck übernommen.

Die vollständigen Phasen-, Ressourcen-, Evidenz-, Quellen- und Cleanup-Verträge stehen in den jeweiligen Demo-README-Dateien. Die datierten Abnahmenachweise je Demo sind in der Runtime-Tabelle oben verlinkt.
