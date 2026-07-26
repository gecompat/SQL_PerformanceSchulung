# ADV-007 – Design LAB-VP5 und DGN-007

| Merkmal | Wert |
|---|---|
| Arbeitspaket | `ADV-007` |
| Status | `DESIGNED` |
| Stand | 2026-07-26 |
| LAB-Serie | `LAB-VP5` |
| Demo | `DGN-007` |
| Curriculum | `LO-M07-04`, `LO-M06-08`, `LO-M03-07`; ergänzend `LO-M00-02`, `LO-M06-04` bis `LO-M06-06` |
| Claims | `ADV-CLM-013` bis `ADV-CLM-015`, `ADV-CLM-034` bis `ADV-CLM-039` |
| Zielversionen | SQL Server 2019, 2022 und 2025 |
| Standardpfad | isolierte synthetische Testdatenbank, Query Store und begrenzte XE-Session |

## 1. Ziel und didaktische Rolle

LAB-VP5 ist der abschließende Diagnose- und Transferfall des Vertiefungsstrangs. Ausgangspunkt ist ein zeitabhängiges Performance-Symptom. Die technische Ursache wird nicht im Teilnehmerfall benannt. Die Lernenden müssen Zeitraum, Workload, Planhistorie, Parameter- und Sessionkontext, Datenverteilung, Waits und Ereignisevidenz zu einer falsifizierbaren Hypothese verbinden.

Der Fall gilt nur dann als vollständig, wenn mindestens zwei plausible Alternativhypothesen anhand fehlender oder widersprechender Evidenz verworfen werden. Eine Tuningmaßnahme ohne dokumentierte Baseline, Gegenprobe, Nebenwirkungsprüfung und Rückfallplan ist kein erfolgreicher Abschluss.

Teilnehmerseitiger Fallname: **„Zeitabhängige Regression eines Suchworkloads“**. Die interne Demo-ID `DGN-007` und ihre Designbeschreibung dürfen in Trainerunterlagen genannt werden, die Lösung wird jedoch weder in der sichtbaren Folie noch im Dateinamen des Teilnehmerauftrags vorweggenommen.

## 2. Didaktische Reihenfolge

`DGN-001` → `DGN-003` → `QRY-013` → `DGN-007` → `M07-TRANSFER`

- `DGN-001` stellt den reproduzierbaren A/B-Messvertrag bereit.
- `DGN-003` führt Query-Store-Plan-, Runtime- und Wait-Historie ein.
- `QRY-013` trennt Client-/Sessionkontext von Parameter- und Datenkontext.
- `DGN-007` kombiniert die Evidenz in einem unbekannten Incident.
- `M07-TRANSFER` verlangt eine begründete nächste Messung für einen veränderten Fall.

Die geplante Dauer beträgt 90 bis 135 Minuten. Der eigentliche Capstone nimmt davon 55 bis 80 Minuten ein.

## 3. Synthetisches Incident-Modell

Die markergebundene Testdatenbank verwendet folgende neutrale Objekte:

- `dbo.CaseGroup`: kleine Dimension mit neutralen Segmentkennungen,
- `dbo.CaseItem`: Faktentabelle mit deterministisch schiefer Gruppen- und Statusverteilung,
- `dbo.CaseItemDetail`: optionale Detailzeilen zur Verstärkung der Lookup- beziehungsweise Scan-Arbeit,
- `dbo.CaseRequestLog`: ausschließlich synthetische, normalisierte Laufmarker ohne freie Benutzereingaben,
- `dbo.usp_CaseSearch`: markierte Suchprozedur mit festem Ergebnisvertrag.

Die Verteilung enthält mindestens eine häufige, eine mittlere und mehrere seltene Gruppen. Zeilenbreite und Detailgrad sind skalierbar. Alle Daten werden deterministisch erzeugt. Öffentliche Beispieldatenbanken, reale Anwendungstelemetrie, reale Hostnamen und freie Parameterprotokollierung sind ausgeschlossen.

## 4. Zeitfenster und Incident-Erzeugung

Die Vorbereitung erzeugt drei klar abgegrenzte Query-Store-Zeitfenster:

1. `T0_BASELINE`: stabiler Ausgangszustand mit dokumentiertem Parameterprofil.
2. `T1_INCIDENT`: wiederholte Ausführungen mit einer ungünstigen Compile-/Reuse-Konstellation und messbarer Regression.
3. `T2_COMPARISON`: dieselbe Last nach genau einer begründeten, reversiblen Änderung.

Der primäre Incidentpfad nutzt Daten-Skew, dedizierte Objektkompilierung und eine kontrollierte Ausführungsreihenfolge. Globale Cacheleerung ist verboten. Cacheisolation erfolgt durch Neuanlage der markergebundenen Prozedur oder objektbezogenes `sp_recompile`.

Der Fall wird nur freigegeben, wenn mindestens zwei Query-Store-Pläne oder zwei klar unterscheidbare Ausführungsprofile mit demselben fachlichen Ergebnisvertrag vorliegen. Entsteht trotz geeignetem Datenprofil keine ausreichende Regression, endet die Vorbereitung mit `SKIP_INCIDENT_NOT_REPRODUCED`. Eine Planform wird nicht durch undokumentierte Trace Flags oder versteckte globale Einstellungen erzwungen.

## 5. Verbindliche Evidenzquellen

### 5.1 Query Store

Query Store wird in der Testdatenbank mit begrenztem Größen- und Capture-Vertrag aktiviert. Zu dokumentieren sind:

- `actual_state_desc` und Capture-Konfiguration,
- Query-, Plan- und Runtime-Statistik-IDs,
- Zeitintervalle `T0`, `T1` und `T2`,
- Plananzahl und Planwechsel,
- Duration, CPU, Logical Reads, Executions und Rows pro Intervall,
- Wait-Kategorien, soweit in der Zielversion erfasst,
- erzwungene Pläne oder Query-Store-Hints; im Primärfall müssen beide fehlen.

Query-Store-Historie ist nicht vollständig, wenn Capture deaktiviert, Speicher erschöpft oder der Zustand nicht `READ_WRITE` war. Diese Grenzen sind Bestandteil des Falls.

### 5.2 Plan- und Parameterkontext

Für relevante Pläne werden gesichert:

- Plan XML und Query Hash,
- kompilierter Parameterwert, soweit vorhanden,
- Estimated und Actual Rows,
- Actual Rows Read und Number of Executions,
- Join-, Lookup-/Scan-, Grant- und Spill-Evidenz,
- Statistics Usage,
- planbezogene SET- und Cacheattribute.

Parameterwerte werden ausschließlich aus den synthetischen, bekannten Testwerten abgeleitet. Freie oder reale Eingaben werden nicht protokolliert.

### 5.3 Datenverteilung und Statistiken

Der Fall stellt Statistikheader, relevantes Histogramm, Datensatzanzahl und synthetische Verteilung bereit. Die Lernenden müssen zwischen Daten-Skew, veralteter Statistik und Clientkontext unterscheiden. Eine Statistikabweichung darf nur dann als Ursache gelten, wenn sie zur beobachteten Schätzung und Planentscheidung passt.

### 5.4 Waits und Livezustand

Request-, Task- und eng begrenzte Instanzdeltas werden getrennt erfasst. Der Fall darf keine serverweite Wait-Rangliste als alleinigen Ursachenbeweis verwenden. Blocking, `RESOURCE_SEMAPHORE`, I/O-Waits und CPU-bezogene Waits werden nur als Hypothesenstart behandelt.

### 5.5 Extended Events

Eine begrenzte, markergefilterte XE-Session erfasst ausschließlich für den Fall benötigte Ereignisklassen und Actions. Eventverfügbarkeit wird im Zielbuild geprüft. Ring Buffer oder kurzlebiges Testtarget werden im Cleanup entfernt. Fehlende Ereignisse widerlegen einen Zustand nur dann, wenn Session, Predicate, Eventklasse und Zeitraum nachweislich geeignet waren.

## 6. Evidenzfreigabe in Stufen

Der Trainer beziehungsweise das Harness gibt Evidenz nicht vollständig zu Beginn aus. Die Freigabestufen sind:

1. **Symptom:** betroffener Zeitraum, fachlicher Requesttyp und beobachtete Antwortzeitklasse.
2. **Historie:** Query-Store-Runtime- und Planübersicht ohne Planerklärung.
3. **Kontext:** Sessionoptionen, Datenbankkontext und Planattribute.
4. **Plan:** Estimated/Actual Rows, kompilierter Parameter, Statistics Usage und Operatorarbeit.
5. **Systemsignale:** Waits, Grants und XE-Ereignisse.
6. **Vergleich:** Ergebnis der gewählten Änderung und Nebenwirkungen.

Die Lösung darf nicht in einem Dateinamen, Marker, Querykommentar oder vorzeitig sichtbaren Spaltenalias enthalten sein.

## 7. Verbindliche Alternativhypothesen

Der Referenzfall enthält mindestens drei plausible Hypothesen. Mindestens zwei müssen durch Evidenz verworfen werden:

### 7.1 Allgemeiner Memory Pressure

Widerlegungskriterien können sein:

- kein `RESOURCE_SEMAPHORE` im relevanten Request-/Task-Zeitfenster,
- keine wartenden Grants,
- ausreichender Grant für den tatsächlich ausgeführten Plan,
- keine korrespondierende Instanz- oder Betriebssystemevidenz.

Ein vorhandener Spill allein bestätigt diese Hypothese nicht.

### 7.2 I/O-Engpass

Widerlegungskriterien können sein:

- warmes Cacheprofil und keine relevanten Physical Reads,
- fehlende passende `PAGEIOLATCH_*`-Evidenz im Requestscope,
- Regression durch veränderte Zeilenverarbeitung trotz vergleichbarer Speicher-/Dateibedingungen,
- A/B-Vergleich zeigt Plan- oder Kardinalitätsänderung bei unverändertem Storageprofil.

### 7.3 Client-/SET-Options-Unterschied

Widerlegungskriterien können sein:

- identische explizite Sessionoptionen,
- gleicher Datenbankkontext,
- gleiche Cacheattribute,
- Abweichung bleibt bei identischem Clientprofil und ändert sich mit Parameter-/Compilekontext.

### 7.4 Parameter- und Planwiederverwendung

Diese Hypothese gilt nur als bestätigt, wenn Datenverteilung, kompilierter Wert, tatsächliche Werte, Planhistorie und gemessene Arbeit eine konsistente Kette bilden.

## 8. Referenzänderung, Vergleich und Rückfallplan

Die automatisierte Referenzlösung verändert genau eine Variable: Die dedizierte Suchprozedur erhält eine querylokale `OPTION (RECOMPILE)`-Variante. Der Originaltext wird vor der Änderung in einem synthetischen, repositoryseitig bekannten Setupschritt gesichert und im Cleanup wiederhergestellt.

Die Referenzlösung wird gewählt, weil sie auf SQL Server 2019, 2022 und 2025 verfügbar ist und die Auswirkung veränderter Compileinformation isoliert zeigt. Sie ist keine allgemeine Empfehlung. Gemessen werden:

- Ergebnisgleichheit,
- Reads, CPU, Duration und Compileindikatoren über mehrere Ausführungen,
- Verhalten für häufige, mittlere und seltene Werte,
- Verlust der Planwiederverwendung,
- Query-Store-Historie vor und nach der Änderung.

Teilnehmende dürfen andere Maßnahmen begründen. Für die technische Abnahme des Demoskripts bleibt jedoch genau eine referenzierte Änderung verbindlich, damit Ursache und Wirkung nicht vermischt werden.

## 9. Versionsvertrag

Der Kernfall ist auf SQL Server 2019, 2022 und 2025 ausführbar. Die Ursachenanalyse darf nicht von PSP, OPPO oder Query Store Hints abhängen.

| Funktion | 2019 | 2022 | 2025 |
|---|---|---|---|
| Query-Store-Plan- und Runtime-Historie | erforderlich | erforderlich | erforderlich |
| Query-Store-Wait-Historie | soweit im Build verfügbar; Preflight | soweit im Build verfügbar; Preflight | soweit im Build verfügbar; Preflight |
| PSP als zusätzliche Kontextinformation | `SKIP_FEATURE_UNAVAILABLE` | optional, Eligibility prüfen | optional, Eligibility prüfen |
| OPPO als zusätzliche Kontextinformation | `SKIP_FEATURE_UNAVAILABLE` | `SKIP_FEATURE_UNAVAILABLE` | optional, CL170 und Konfiguration prüfen |
| Query Store Hints | keine Voraussetzung | optionaler Erweiterungspfad | optionaler Erweiterungspfad |

Fehlt Query Store oder kann er nicht `READ_WRITE` aktiviert werden, endet `DGN-007` mit `SKIP_QUERY_STORE_REQUIRED`. Ein vereinfachter DMV-Fall darf separat ausgeführt werden, erfüllt aber nicht LAB-VP5.

## 10. Sicherheits-, Datenschutz- und Cleanup-Vertrag

- ausschließlich synthetische Testdatenbank,
- keine freien Parameterwerte in Logs oder Reports,
- keine globalen Cacheleerungen,
- keine erzwungenen Pläne oder Query Store Hints im Primärincident,
- XE- und Query-Store-Artefakte markergebunden und größenbegrenzt,
- harte Laufzeitlimits je Phase,
- Objekt- und Datenbankcleanup auch nach Abbruch,
- keine Persistenz realer Umgebungs- oder Hostinformationen.

Die Sicherheitsstufe ist Gelb. Maximal drei gleichzeitig aktive Sessions sind zulässig: Workload, Beobachtung und Orchestrierung. Mindestprofil: 4 logische CPU-Kerne, 8 GB SQL-Server-Speicher und ausreichend Platz für Query Store, Testdaten und TempDB.

## 11. Abnahmekriterien

`DGN-007` gilt als fachlich und technisch bestanden, wenn:

- T0, T1 und T2 reproduzierbar abgegrenzt sind,
- Query Store mindestens zwei unterscheidbare Plan- oder Laufzeitprofile erfasst,
- mindestens zwei Alternativhypothesen begründet verworfen werden,
- die bestätigte Hypothese Plan-, Parameter-, Verteilungs- und Zeitevidenz verbindet,
- genau eine reversible Änderung durchgeführt wird,
- Ergebnisgleichheit und Nebenwirkungen dokumentiert sind,
- Cleanup Query Store, XE, Sessions und Testdaten vollständig zurücksetzt.

Nicht zulässig sind feste Millisekunden, eine bestimmte Plan-Node-ID, ein universeller Planoperator oder ein festes Verhältnis als alleinige Golden Values.

## 12. Implementierungsschnitte für ADV-008

1. `DGN-007_DATA_MODEL`
2. `DGN-007_QUERY_STORE_WINDOWS`
3. `DGN-007_INCIDENT_GENERATION`
4. `DGN-007_CONTEXT_AND_PLAN_EVIDENCE`
5. `DGN-007_WAIT_AND_XE_EVIDENCE`
6. `DGN-007_HYPOTHESIS_WORKSHEET`
7. `DGN-007_REFERENCE_MITIGATION`
8. `DGN-007_RUNTIME_MATRIX`
9. `LAB-VP5_ORCHESTRATION`
10. `M07_TRANSFER_VARIANT`

Incident-Erzeugung und Referenzmitigation werden in getrennten Pull Requests implementiert, damit der Fall nicht durch versehentlich sichtbare Lösungsmarker entwertet wird.

## 13. Quellen

Primärquellen: `SRC-001`, `SRC-007`, `SRC-027`, `SRC-028`, `SRC-031`, `SRC-035`, `SRC-036`. Ergänzende Fachquellen: `SRC-040`, `SRC-046`, `SRC-047`, `SRC-051`. Community-Quellen dienen ausschließlich der Diagnosemethode und ersetzen keine Versions- oder Featuregarantie.

## 14. Statusgrenze

`ADV-007` ist mit diesem Dokument `DESIGNED`. `DGN-007` und LAB-VP5 bleiben bis zur Implementierung, Runtime-Matrix und didaktischen Generalprobe ausdrücklich `PLANNED` beziehungsweise `DESIGNED`.