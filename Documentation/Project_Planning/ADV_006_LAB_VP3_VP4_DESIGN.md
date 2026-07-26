# ADV-006 – Design LAB-VP3 und LAB-VP4

| Merkmal | Wert |
|---|---|
| Arbeitspaket | `ADV-006` |
| Status | `DESIGNED` |
| Stand | 2026-07-26 |
| LAB-Serien | `LAB-VP3`, `LAB-VP4` |
| Curriculum | `LO-M06-07`, `LO-M06-08`, `LO-M02-11`; ergänzend `LO-M02-05` bis `LO-M02-07` |
| Claims LAB-VP3 | `ADV-CLM-021` bis `ADV-CLM-027`, `ADV-CLM-037` |
| Claims LAB-VP4 | `ADV-CLM-019`, `ADV-CLM-020`, `ADV-CLM-025`, `ADV-CLM-028` bis `ADV-CLM-033` |
| Zielversionen | SQL Server 2019, 2022 und 2025 |
| Standardpfad | isolierte synthetische Testdatenbank; rote Speicherlast ausschließlich auf dedizierter Wegwerfinstanz |

## 1. Ziel und Abgrenzung

LAB-VP3 trennt Query Execution Memory, operatorbezogene Spills, Undergrant, Overgrant, Grant-Warten, allgemeine Speicherknappheit und TempDB-Folgen. Ein Spill ist kein Nachweis für instanzweiten Speicherdruck. `RESOURCE_SEMAPHORE` ist kein Synonym für Buffer-Pool-Druck. Einzelquery und konkurrierender Workload werden deshalb in getrennten Phasen untersucht.

LAB-VP4 vergleicht Intelligent-Query-Processing-Funktionen versionsbewusst. Jede Funktion besitzt einen eigenen Vertrag für Engine-Version, Compatibility Level, Datenbankkonfiguration, Query-Store-Anforderung, Eligibility, sichtbare Planevidenz und erwarteten Skip. Ein neueres Feature wird nicht als generell bessere Lösung bewertet.

Nicht Bestandteil sind universelle Grant-Schwellen, feste Spill-Mengen, eine pauschale Empfehlung zur Erhöhung von Server Memory, instanzweite Konfigurationsänderungen auf gemeinsam genutzten Systemen oder das Erzwingen einer nicht produzierten adaptiven Planform.

## 2. Didaktische Reihenfolge

### 2.1 LAB-VP3 – Workspace Memory und Spills

`OPT-014` → `OPT-013` → `RES-004` → `RES-003` → `RES-007` → `DGN-005`

Der reguläre Schulungspfad umfasst `OPT-014`, `OPT-013`, `RES-004`, `RES-007` und `DGN-005`. `RES-003` ist eine rote, optionale Erweiterung. Sie darf nur auf einer dedizierten, wegwerfbaren Instanz mit begrenztem Ressourcenprofil ausgeführt werden. Die Serie wird ohne roten Teil auf 75 bis 105 Minuten und mit rotem Teil auf 105 bis 145 Minuten geplant.

### 2.2 LAB-VP4 – Intelligent Query Processing 2019–2025

`QRY-008` → `QRY-009` → `OPT-014` → `OPT-009` → `OPT-006` → `RES-002` → `OPT-010`

Die Serie verwendet getrennte Queryfamilien und Datenmodelle. Sie ist kein einzelner überladener Featurevergleich. Abhängig von Version und Eligibility entstehen `PASS`, `SKIP_FEATURE_UNAVAILABLE`, `SKIP_FEATURE_DISABLED`, `SKIP_FEATURE_NOT_ELIGIBLE` oder `SKIP_QUERY_STORE_REQUIRED`. Die geplante Dauer beträgt 95 bis 140 Minuten.

## 3. Gemeinsames synthetisches Daten- und Ressourcenmodell

LAB-VP3 verwendet ein markergebundenes Modell mit folgenden neutralen Objekten:

- `dbo.GrantGroup`: kleine Dimension für Verteilungsprofile,
- `dbo.GrantFact`: skalierbare Faktentabelle mit einstellbarer Zeilenbreite und Gruppenschiefe,
- `dbo.GrantPayload`: optionale breite Nutzlast für Sort- und Hash-Workloads,
- `dbo.GrantRequest`: kontrollierte Parametermengen für wiederholte und konkurrierende Ausführungen.

Der Generator stellt die Profile `MEMORY_STANDARD`, `MEMORY_CONCURRENT` und `MEMORY_PRESSURE` bereit. Das rote Profil wird nicht auf einer normalen Schulungsinstanz erzeugt. Es setzt eine dedizierte Instanz mit explizitem Ressourcenbudget, hartem Laufzeitlimit und automatischem Cleanup voraus.

LAB-VP4 verwendet pro Featurefamilie ein eigenes minimales Datenmodell. Gemeinsam sind feste Seeds, skalierbare Datenmengen, synthetische Schiefe, Ergebnischecksumme und markergebundene Querytexte. Systemkataloge dienen nicht als Zeilengenerator. Zufällige Daten und öffentliche Beispieldatenbanken sind unzulässig.

## 4. LAB-VP3 – Demo- und Evidenzverträge

### 4.1 OPT-014 – Grantstufen und Memory Grant Feedback

Die Demo misst Required, Desired, Requested, Granted und Max Used Memory derselben markierten Ausführung. Plan XML und `sys.dm_exec_query_memory_grants` werden zeitlich und über Session-/Requestbezug korreliert. Wiederholte Ausführungen prüfen, ob und wie sich der Grant verändert.

Verbindliche Evidenz:

- planbezogene Grantattribute,
- Requested, Granted und Used Memory,
- Estimated und Actual Rows,
- Spill-Warnings, soweit vorhanden,
- Logical Reads, CPU, Duration und Ergebnischecksumme,
- Ausführungsnummer und Query-Store-Zustand,
- versionsbezogener Feedbackmodus.

Eine Grantänderung ist kein stabiler Golden Value. Bewertet werden Richtung, Stabilisierung und Nebenwirkung. Bleibt Feedback wegen fehlender Eligibility aus, endet der Teil mit `SKIP_FEATURE_NOT_ELIGIBLE`.

**Sicherheitsstufe:** Gelb. **Sessions:** 1. **Mindestprofil:** 2 Kerne, 4 GB. **Quellen:** `SRC-009`, `SRC-010`, `SRC-050`.

### 4.2 OPT-013 – operatorbezogener Spill

Der bereits validierte Pilot bildet den Ausgangspunkt. Die Vertiefung ergänzt Plan-XML-Auswertung, TempDB-Folgeevidenz und die ausdrückliche Abgrenzung zu `RESOURCE_SEMAPHORE`. Ein kontrollierter Table-Variable- oder Schätzfehler erzeugt einen Undergrant. Die Gegenmaßnahme verbessert ausschließlich Kardinalitätsinformation oder Staging; Server Memory wird nicht verändert.

Pflichtabnahme:

- identische Ergebnismenge,
- Spill-Warning und TempDB-Arbeit im Problemzustand,
- reduzierte oder entfallene Spill-Arbeit nach der Gegenmaßnahme,
- kein Schluss von Spill auf allgemeinen Instanzspeicherdruck ohne zusätzliche Evidenz.

### 4.3 RES-004 – Overgrant, Undergrant und konkurrierende Grants

`RES-004` verwendet drei bis sechs kontrollierte Sessions. Eine Barriere startet synthetische Sort-/Hash-Abfragen gleichzeitig. Zwei Profile werden getrennt ausgeführt:

1. Undergrant-Profil mit beobachtbarer operatorbezogener Spill-Arbeit.
2. Overgrant-Profil mit deutlich höherem Requested/Granted Memory als Max Used Memory.

Die Demo misst Einzelquery und Nebenläufigkeit getrennt. Eine schnellere Einzelquery darf nicht als bessere Workloadentscheidung gelten, wenn sie weniger gleichzeitige Ausführungen zulässt.

Verbindliche Evidenz:

- aktive und wartende Grants,
- Requested, Granted und Max Used Memory je Session,
- Start-, Grant- und Endzeitpunkt,
- Wait- und Queue-Zustand,
- Durchsatz und Gesamtdauer des kontrollierten Batches,
- Result Checksum je Session,
- vollständiger Multi-Session-Cleanup.

`RESOURCE_SEMAPHORE` ist in `RES-004` kein Pflichtresultat. Wenn kein Grant-Warten entsteht, bleibt die Overgrant-/Undergrant-Analyse gültig; der rote Drucktest wird nicht automatisch aktiviert.

**Sicherheitsstufe:** Gelb. **Sessions:** 3–6. **Mindestprofil:** 4 Kerne, 8 GB. **Skip:** `SKIP_CONCURRENCY_PROFILE_INSUFFICIENT`, `SKIP_MEMORY_PROFILE_INSUFFICIENT`, `SKIP_TOOL_MISSING`.

### 4.4 RES-003 – isolierter roter Memory-Pressure-Versuch

`RES-003` ist kein regulärer Bestandteil einer gemeinsam genutzten Schulungsinstanz. Die Ausführung ist ausschließlich zulässig, wenn alle folgenden Bedingungen erfüllt sind:

- dedizierte Wegwerfinstanz oder dedizierter Container/VM,
- keine weiteren Benutzerworkloads,
- dokumentiertes Speicherlimit der Instanzumgebung,
- maximal sechs Demo-Sessions,
- hartes Gesamtlaufzeitlimit von 180 Sekunden,
- Kill-Switch außerhalb der getesteten Sessions,
- automatisches Entfernen der Instanz oder Rücksetzen des Ressourcenprofils.

Der Versuch erzeugt konkurrierende Workspace-Anforderungen. Querylokale Grant-Hints dürfen nur als synthetisches Diagnoseinstrument verwendet werden, wenn die Zielversion sie unterstützt. Instanzweites `max server memory` wird durch die Demo nicht verändert.

Pflichtevidenz:

- mindestens ein wartender Query Grant,
- Wait-Typ `RESOURCE_SEMAPHORE` im Request- oder Task-Scope,
- gleichzeitig aktive beziehungsweise gewährte Grants,
- Abgrenzung von Buffer-Pool- und Betriebssystemspeicherdruck,
- Recovery nach Freigabe oder Abbruch,
- bestätigter Cleanup aller Sessions.

Kann der Zustand innerhalb des Budgets nicht erzeugt werden, endet die Demo mit `SKIP_MEMORY_PRESSURE_NOT_PRODUCED`. Ein stärkerer ungebremster Lastversuch ist unzulässig.

**Sicherheitsstufe:** Rot. **Ausführungspfad:** `DEDICATED_RESOURCE_INSTANCE`. **Mindestprofil:** 4 Kerne, 8 GB Hostspeicher; das effektive Instanzlimit wird im Preflight dokumentiert.

### 4.5 RES-007 – Wait-Scope und Zeitbezug

Die Demo untersucht denselben Workload aus drei Ebenen:

- Task-/Request-Waits während der laufenden Ausführung,
- sessionbezogene beziehungsweise querybezogene Deltas,
- instanzweite kumulative Deltas im eng begrenzten Zeitfenster.

Ein Wait-Name ohne Scope und Zeitraum ist kein Abnahmenachweis. Die Demo muss mindestens eine plausible, aber falsche Interpretation verwerfen, etwa die Gleichsetzung eines Spill-Effekts mit allgemeinem Memory Pressure.

### 4.6 DGN-005 – begrenzte Extended-Events-Evidenz

Die XE-Session verwendet ausschließlich im Zielbuild vorhandene Events und Actions. Eventverfügbarkeit wird über die Metadaten geprüft. Das Target bleibt ein begrenzter Ring Buffer oder ein kurzlebiges, markergebundenes Testtarget. Sessionname, Predicate, Max-Memory- und Event-Retention-Einstellungen sind Teil des Preflights.

Erfasst werden nur synthetische Querymarker und die für den LAB-Schritt benötigte Ereignisklasse. Fehlende Events bedeuten nicht automatisch, dass der technische Zustand nicht auftrat. Plan-, DMV- und XE-Evidenz werden getrennt bewertet. Nicht verfügbare Eventklassen führen zu `SKIP_XE_EVENT_UNAVAILABLE`.

## 5. LAB-VP4 – Featurematrix

| Feature | Erste Zielversion | Mindest-CL | Datenbankkonfiguration | Query Store | Demo | Erwartung älterer Versionen |
|---|---:|---:|---|---|---|---|
| Interleaved Execution für MSTVF | 2019 | 140 | featurebezogene Konfiguration nicht deaktiviert | nicht als Featurevoraussetzung | `QRY-009` | in allen Zielversionen prüfbar |
| Table Variable Deferred Compilation | 2019 | 150 | Deferred Compilation nicht deaktiviert | nicht als Featurevoraussetzung | `QRY-008`, `OPT-013` | `SKIP_FEATURE_DISABLED` bei deaktivierter Konfiguration |
| Scalar UDF Inlining | 2019 | 150 | UDF Inlining nicht deaktiviert | nicht als Featurevoraussetzung | `QRY-009` | `SKIP_FEATURE_NOT_ELIGIBLE` bei nicht inlinebarer Ausprägung |
| Batch Mode on Rowstore | 2019 | 150 | Batch Mode on Rowstore nicht deaktiviert | nicht als Featurevoraussetzung | `OPT-006`, `RES-002` | keine Performancezusage; Eligibility nachweisen |
| Row-Mode Memory Grant Feedback | 2019 | 150 | MGF nicht deaktiviert | für Basismodus nicht zwingend | `OPT-014` | Feedbackzustand und Wiederholungen dokumentieren |
| persistentes/perzentilbasiertes MGF | 2022 | 160 | MGF nicht deaktiviert | `READ_WRITE` erforderlich | `OPT-014` | 2019: `SKIP_FEATURE_UNAVAILABLE` |
| Parameter Sensitive Plan Optimization | 2022 | 160 | PSP nicht deaktiviert | für Historienevidenz aktiviert | `OPT-009` | 2019: `SKIP_FEATURE_UNAVAILABLE` |
| Cardinality Estimation Feedback | 2022 | 160 | Feature nicht deaktiviert | `READ_WRITE` erforderlich | `OPT-006`, `DGN-003` | 2019: `SKIP_FEATURE_UNAVAILABLE` |
| Degree of Parallelism Feedback | 2022 | 160 | Feature nicht deaktiviert | `READ_WRITE` erforderlich | `RES-002`, `DGN-003` | 2019: `SKIP_FEATURE_UNAVAILABLE` |
| Optional Parameter Plan Optimization | 2025 | 170 | OPPO aktiviert | für Variantenhistorie aktiviert | `OPT-010`, `QRY-004` | 2019/2022: `SKIP_FEATURE_UNAVAILABLE` |

Die konkreten Konfigurationsnamen werden während der Implementierung aus der Zielversion ermittelt und gegen die Microsoft-Primärquellen im Quellenregister geprüft. Die Tabelle beschreibt den Designvertrag, nicht die Erlaubnis, Konfigurationen auf fremden Datenbanken zu verändern.

## 6. Versions- und Skip-Vertrag

Für jede Featureausführung werden getrennt erfasst:

- Engine Major Version und vollständiger Build,
- Compatibility Level,
- Edition und Betriebssystem,
- relevante Database Scoped Configurations,
- Query-Store-Zustand einschließlich `actual_state_desc`,
- Eligibility- beziehungsweise Reason-Evidenz, soweit dokumentiert,
- Plan- und Query-Store-Nachweis.

Zulässige Ergebnisstatus:

- `PASS_FEATURE_OBSERVED`,
- `PASS_FEATURE_DISABLED_CONTRAST`,
- `SKIP_FEATURE_UNAVAILABLE`,
- `SKIP_FEATURE_DISABLED`,
- `SKIP_FEATURE_NOT_ELIGIBLE`,
- `SKIP_QUERY_STORE_REQUIRED`,
- `SKIP_PERMISSION_MISSING`,
- `SKIP_RESOURCE_PROFILE_INSUFFICIENT`.

Ein Skip ist nur gültig, wenn die konkrete fehlende Voraussetzung ausgegeben wird. Ein fehlender erwarteter Planoperator ohne Eligibility-Nachweis ist kein Produktfehler.

## 7. Mess- und Golden-Vertrag

Stabile Abnahmen verwenden:

- Ergebnisequivalenz,
- normalisierte Planattribute,
- Vorhandensein oder Fehlen dokumentierter Featuremarker,
- Richtung und Verhältnis von Grant, Spill, Reads, CPU oder Durchsatz,
- kontrollierte Status- und Skip-Codes,
- vollständigen Cleanup.

Nicht als Golden Values zulässig sind exakte Millisekunden, exakte Grantgrößen, vollständige Plan-XML-Dokumente, konkrete Operator-Node-IDs oder universelle Wait-Schwellen.

## 8. Sicherheits- und Cleanup-Vertrag

Jeder LAB-Schritt besitzt Preflight, Setup, Baseline, Problem oder Kontrast, Evidenz, Gegenprobe beziehungsweise Gegenmaßnahme, Vergleich und Cleanup. Multi-Session-Schritte verwenden Barrieren, maximale Laufzeiten und einen externen Kill-Switch. Query Store, XE-Sessions und Database Scoped Configurations werden ausschließlich in der markergebundenen Testdatenbank aktiviert beziehungsweise verändert und im Cleanup auf den Ausgangszustand zurückgeführt.

Rote Schritte werden standardmäßig übersprungen. Ihre Freigabe benötigt eine dedizierte Instanz und den Parameter `@HighImpactConfirmed = 1` beziehungsweise den äquivalenten Harness-Schalter.

## 9. Implementierungsschnitte für ADV-008

Die spätere Umsetzung wird in folgende unabhängige Schnitte geteilt:

1. `OPT-014_GRANT_AND_MGF`
2. `OPT-013_SPILL_EXTENSION`
3. `RES-004_CONCURRENT_GRANTS`
4. `RES-007_WAIT_SCOPE`
5. `DGN-005_MEMORY_XE`
6. `LAB-VP3_ORCHESTRATION`
7. `QRY-008_TVDC`
8. `QRY-009_MSTVF_UDF`
9. `OPT-006_CE_AND_BATCH_MODE`
10. `RES-002_DOP_FEEDBACK_EXTENSION`
11. `OPT-009_PSP_RUNTIME`
12. `OPT-010_OPPO_RUNTIME`
13. `OPT-014_PERSISTED_MGF`
14. `LAB-VP4_ORCHESTRATION`
15. `RES-003_DEDICATED_MEMORY_PRESSURE` als zuletzt und separat freizugebender roter Schnitt

Kein roter Schnitt darf gemeinsam mit grünen oder gelben Demos in einen Pull Request aufgenommen werden.

## 10. Quellen

Verbindliche Primärquellen: `SRC-001`, `SRC-007` bis `SRC-010`, `SRC-026`, `SRC-027`, `SRC-029`, `SRC-031`, `SRC-035`, `SRC-036`. Ergänzende Fachquellen: `SRC-043`, `SRC-050`, `SRC-051`. Community-Quellen begründen keine Featureverfügbarkeit oder universelle Schwellenwerte.

## 11. Statusgrenze

`ADV-006` ist mit diesem Dokument `DESIGNED`. Kein aufgeführter Demo-Schritt wird dadurch `IMPLEMENTED` oder runtime-validiert. Gate V2 wird erst nach erfolgreicher statischer Vertragsprüfung und Konsistenzabnahme gesetzt.