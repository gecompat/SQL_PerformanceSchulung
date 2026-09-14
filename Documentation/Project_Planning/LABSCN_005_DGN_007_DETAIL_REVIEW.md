# LABSCN-005 – Detailreview DGN-007 (Planungsschnitt)

| Merkmal | Wert |
|---|---|
| Status | `DECIDED_PLANNING` |
| Stand | 2026-09-14 |
| Arbeitspaket | `LABSCN-005` |
| Kandidat | `DGN-007` – Capstone „Zeitabhängige Regression eines Suchworkloads“ |
| Task | `TSK-002` |
| Designgrundlage | [`ADV_007_LAB_VP5_DESIGN.md`](ADV_007_LAB_VP5_DESIGN.md) (`DESIGNED`) |
| interaktive Zielversion | SQL Server 2025 / Compatibility Level 170 |
| Safety | `YELLOW`, ausschließlich isolierte Wegwerfinstanz |
| Ausführungspfad | `TSQL_TESTDB`, Stufe 2, `DISPOSABLE_INSTANCE` |

## 1. Zweck und Statusgrenze

Dieses Dokument ist der verbindliche Planungsschnitt für den vierten
interaktiven `LABSCN-005`-Slice. Es entscheidet Umfang, Reihenfolge,
Vertragsquellen und die Voraussetzungen für die spätere Implementierung.
Es ist **kein Implementierungsauftrag** und keine Runtimefreigabe:

- `DGN-007` bleibt als fachliche Demo `PLANNED`; LAB-VP5 bleibt `DESIGNED`.
- Das interaktive Szenario existiert noch nicht. Es besitzt keinen
  Project Adapter, keine `Scenarios/DGN-007/`-Struktur und keinen
  Runtime-Laufnachweis.
- Eine Implementierung beginnt erst in einem eigenen Folgeschnitt nach
  diesem Review; daraus folgt noch kein automatischer Auftrag.

## 2. Zulässigkeit nach den Stop-Regeln

`NEXT_DEVELOPMENT_WAVES.md` nennt als Wellenrang 1 einen Capstone-Planungsschnitt
für `DGN-007` und fordert dafür ein vollständig abgeschlossenes Detailreview von
Incident, Alternativhypothesen, Zeitfenstern, Reset, Quellen und
Teilnehmerübergabe. Die Voraussetzungen sind erfüllt:

- `W-DGN-001` (Query-Store-/XE-Pilot, Lauf 33222989682) und `W-SCN-001`
  (Project Adapter `0.1`, Docker-/Podman-Lifecycle) sind `VALIDATED`.
- Die `DGN-005`- und `CON-006`-Folgeslices liefern praktisch wiederverwendbare
  Evidenz-, Mehrsession- und Cleanup-Verträge.
- Das Design `ADV-007` ist vollständig und durch
  `Tests/Static/validate_adv_006_007_designs.py` abgesichert.
- `SQL_Server_Lab` benötigt keine Änderung: Der Capstone bleibt innerhalb der
  belegten Fähigkeiten (eine isolierte 2025-Einzelinstanz, Query Store,
  begrenzte XE-Session, Post-Provision-T-SQL).

## 3. Lernmehrwert und Abgrenzung

Der Capstone orchestriert bereits implementierte Evidenzpfade zu einem
unbekannten Incident; er erzeugt keinen neuen Root Cause:

| Evidenzquelle | bereits validiert durch | Rolle im Capstone |
|---|---|---|
| A/B-Messvertrag | `DGN-001` (Messvertrag) | Baseline, genau eine Änderung, Gegenprobe |
| Query-Store-Plan-, Runtime- und Wait-Historie | `DGN-003` (Lauf 33222989682) | Zeitfenster T0/T1/T2, Planwechsel |
| Client-/Sessionkontext | `QRY-013` (Lauf 30699410795) | Hypothese 3 widerlegen |
| begrenzte XE-Evidenz | `DGN-005` (Slices) | Wait- und Ereignissignal im Requestscope |
| Wait-Scope-Deltas | `RES-007` (Lauf 33222989644) | Hypothesenstart statt Ursachenbeweis |
| Deadlock- und Mehrsession-Verträge | `CON-004`, `CON-006` | Sessiondisziplin, Signale, Timeouts |

Der Didaktikmehrwert ist die geprüfte Verknüpfung: Symptom → Historie →
Kontext → Plan → Systemsignale → Vergleich, mit mindestens zwei anhand
fehlender oder widersprechender Evidenz verworfenen Alternativhypothesen.

## 4. Incident-, Zeitfenster- und Hypothesenvertrag

Der Vertrag folgt unverändert Kapitel 3 bis 8 von
[`ADV_007_LAB_VP5_DESIGN.md`](ADV_007_LAB_VP5_DESIGN.md). Für den interaktiven
Slice werden folgende Festlegungen zusätzlich getroffen:

- **Zeitfenster:** `T0_BASELINE`, `T1_INCIDENT`, `T2_COMPARISON` als klar
  abgegrenzte Query-Store-Intervalle. Die Incident-Erzeugung nutzt Daten-Skew,
  dedizierte Objektkompilierung der markierten Prozedur `dbo.usp_CaseSearch`
  und eine kontrollierte Ausführungsreihenfolge; globale Cacheleerung bleibt
  verboten.
- **Freigabe in Stufen:** Die sechs Evidenzstufen aus dem Design (Symptom,
  Historie, Kontext, Plan, Systemsignale, Vergleich) werden im
  Teilnehmerartefakt als getrennte, nummerierte Arbeitsschritte abgebildet.
- **Referenzänderung:** genau eine reversible, querylokale `OPTION (RECOMPILE)`
-Variante der Suchprozedur; Originaltext wird vor der Änderung gesichert und
  im Cleanup wiederhergestellt. Incident-Erzeugung und Referenzmitigation
  bleiben getrennte Implementierungsschnitte, damit der Fall nicht durch
  versehentlich sichtbare Lösungsmarker entwertet wird.
- **Kontrollierte Skips:** `SKIP_QUERY_STORE_REQUIRED` (Query Store nicht
  `READ_WRITE`), `SKIP_INCIDENT_NOT_REPRODUCED` (keine unterscheidbaren
  Plan-/Laufzeitprofile) und `SKIP_EVIDENCE_MISSING` (fehlerhaft konfigurierte
  Evidenzquelle) bleiben die einzigen zulässigen Abbruchausgänge. Kein Skip
  erzeugt eine Evidenzbehauptung.

## 5. Alternativhypothesen

Der Referenzfall führt mindestens drei Hypothesen, von denen mindestens zwei
verworfen werden. Die Widerlegungskriterien aus dem Designvertrag bleiben
verbindlich und werden im Teilnehmerartefakt als Prüfliste geführt:

1. Allgemeiner Memory Pressure – widerlegt durch fehlende
   `RESOURCE_SEMAPHORE`- und Grant-Evidenz im Request-/Task-Zeitfenster.
2. I/O-Engpass – widerlegt durch warmes Cacheprofil, fehlende
   `PAGEIOLATCH_*`-Evidenz im Requestscope und Regression trotz unverändertem
   Storageprofil.
3. Client-/SET-Options-Unterschied – widerlegt durch identische Sessionoptionen,
   identischen Datenbankkontext und identische Cacheattribute bei gleichzeitiger
   Änderung mit Parameter-/Compilekontext.
4. Parameter- und Planwiederverwendung – nur bei konsistenter Kette aus
   Datenverteilung, kompiliertem Wert, tatsächlichen Werten, Planhistorie und
   gemessener Arbeit bestätigt.

## 6. Lifecycle-, Ressourcen- und Safety-Vertrag

- Eine frische SQL-Server-2025-Linux-Wegwerfinstanz im Profil `standard`
  (Mindestprofil gemäß Design: 4 logische Kerne, 8 GB SQL-Server-Speicher)
  ist ausreichend. Mehrere Instanzen, Providererweiterungen und Änderungen an
  `SQL_Server_Lab` sind nicht erforderlich.
- Der Project Adapter `0.1` mit den vier Entrypoints `preflight`, `install`,
  `validate` und `cleanup` erzeugt ausschließlich die vierfach markergebundene
  Testdatenbank, synthetische Objekte (`dbo.CaseGroup`, `dbo.CaseItem`,
  `dbo.CaseItemDetail`, `dbo.CaseRequestLog`, `dbo.usp_CaseSearch`),
  Query-Store-Konfiguration und die begrenzte, markergefilterte XE-Session.
- Maximal drei gleichzeitig aktive Sessions: Workload, Beobachtung und
  Orchestrierung. Benannte Datenbanksignale sichern die Reihenfolge; feste
  Sleeps steuern nicht den fachlichen Zustand.
- Harte Laufzeitlimits je Phase bleiben Pflicht; der Gesamtlifetime folgt den
  belegten Slices (`CON-006`: 180 Sekunden Demolauf).
- Die XE-Session folgt dem `DGN-005`-Vertrag: In-Memory-Ring-Buffer,
  größen- und dauerbegrenzt, `STARTUP_STATE=OFF`, kein Event-File-Target, kein
  automatischer Export. `MAX_DURATION` wird nur auf SQL Server 2025
  dokumentiert und im Zielbuild geprüft.
- Reset und Remove prüfen vor dem Löschen die vier Datenbankmarker. Remove
  beendet gegebenenfalls verbliebene Sessions durch den markergebundenen
  Datenbankabbau, entfernt die XE-Session vor dem Datenbankabbau und löscht
  anschließend nur die zugehörige Lab-Infrastruktur bis `REMOVED`.
- Teilnehmerartefakte dürfen die Lösung weder im Dateinamen noch im Marker,
  Querykommentar oder vorzeitig sichtbaren Spaltenalias enthalten.

## 7. Teilnehmer- und Evidenzvertrag

Der primäre Ablauf bleibt `MANUAL`; `AUTOMATED_VERIFY` bleibt ein getrennter
Qualitätssicherungspfad. Die Teilnehmenden durchlaufen in einem SQL-Fenster die
Phase `DGN-007` in der Stufenreihenfolge aus Kapitel 6 des Designs; die
Orchestrierung übernimmt Provisionierung und fachliche Vorbereitung und endet
in `READY_FOR_USER`.

Die interaktive Abnahme verlangt je Provider:

1. `Start -> READY_FOR_USER` mit validiertem Adapterzustand;
2. abgegrenzte Zeitfenster T0/T1/T2 in der Query-Store-Historie;
3. mindestens zwei unterscheidbare Plan- oder Laufzeitprofile;
4. mindestens zwei begründet verworfene Alternativhypothesen;
5. genau eine reversible Änderung mit Ergebnisgleichheit und Nebenwirkungen;
6. `Reset -> READY_FOR_USER` auf derselben Instanz;
7. markergebundenen XE-, Query-Store-, Session- und Datenbankabbau mit
   abschließendem `REMOVED`.

## 8. Quellenstatus

Die Designquellen `SRC-001`, `SRC-007`, `SRC-027`, `SRC-028`, `SRC-031`,
`SRC-035`, `SRC-036` sowie ergänzend `SRC-040`, `SRC-046`, `SRC-047`, `SRC-051`
sind registriert und im `ADV_007_LAB_VP5_DESIGN.md` gebunden. Ein zusätzliches
Quellen-Delta-Review ist für den Planungsschnitt nicht erforderlich; vor der
Implementierung ist der Projekt-Quellenregisterprozess für neu hinzukommende
Detailquellen erneut zu durchlaufen. Aktuelle Herstellerdokumentation allein
bleibt kein Implementierungs- oder Runtime-Nachweis.

## 9. Folgeschnitte nach diesem Review

Die Reihenfolge nach diesem Planungsschnitt ist bewusst klein gehalten:

1. **Implementierungsschnitt A:** Project Adapter `0.1` mit Datenaufbau,
   Query-Store-Fenstern und Incident-Erzeugung (`DGN-007_DATA_MODEL`,
   `DGN-007_QUERY_STORE_WINDOWS`, `DGN-007_INCIDENT_GENERATION`); kein
   Mitigationsmarker im Teilnehmerpfad.
2. **Implementierungsschnitt B:** Evidenz-, Hypothesen- und Mitigationsschnitte
   (`DGN-007_CONTEXT_AND_PLAN_EVIDENCE`, `DGN-007_WAIT_AND_XE_EVIDENCE`,
   `DGN-007_HYPOTHESIS_WORKSHEET`, `DGN-007_REFERENCE_MITIGATION`) plus
   Orchestrierung und Transfervariante.
3. **Runtime-Matrix:** automatisierte Demo auf SQL Server 2019, 2022 und 2025
   je zweimal; anschließend die interaktive Docker-/Podman-Abnahme nach
   Kapitel 7.

Ein Schnitt entspricht einem eigenen, kleinen Pull Request. Die
Statusanhebung erfolgt ausschließlich über konkrete Laufnachweise gemäß
[`DEMO_CONTRACT.md`](../../.ai/DEMO_CONTRACT.md).