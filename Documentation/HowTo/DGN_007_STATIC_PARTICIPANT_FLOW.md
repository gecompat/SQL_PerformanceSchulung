# DGN-007 – Statischer Teilnehmerablauf

| Merkmal | Wert |
|---|---|
| Status | `IMPLEMENTED_STATIC_SLICE_B` |
| Übergabestatus | `STATIC_PARTICIPANT_FLOW_ONLY` |
| Sicherheitsstufe | `YELLOW` |
| Ausführungsart | `MANUAL` |

Dieses Dokument beschreibt ausschließlich die geordnete manuelle Arbeit mit
dem bereits vorbereiteten DGN-007-Zustand. Es ist kein interaktives Szenario,
kein Runtime-Nachweis und keine Freigabe für `READY_FOR_USER`. Es erstellt
keine Container, startet keinen Adapter und ersetzt weder dessen Cleanup noch
die noch offene Runtime-Matrix.

## Voraussetzungen

Die fachliche Ausführung ist nur auf einer bestätigten isolierten
Wegwerfinstanz zulässig. Der vorhandene Adapter muss die vier
Eigentumsmarker, die synthetische Datenbank und die Zeitfenster `T0_BASELINE`
und `T1_INCIDENT` bereits vorbereitet haben. Verbindung und SQLCMD-Variablen
sind vor jedem Skript wie folgt zu setzen:

```sql
:setvar DemoId "DGN-007"
:setvar RunToken "LOCAL"
```

Die kontrollierten Ausgänge `SKIP_QUERY_STORE_REQUIRED`,
`SKIP_INCIDENT_NOT_REPRODUCED` und `SKIP_EVIDENCE_MISSING` sind keine
Erfolgs- oder Ursachenbehauptungen. Nach einem solchen Ausgang nicht mit einer
anderen Maßnahme fortfahren; zuerst das lokale Recovery ausführen.

Der automatisierte statische Harness akzeptiert diese Codes nur in den
folgenden Stufen. Adapter-Preflight sowie Adapter-Install und -Validate müssen
weiterhin erfolgreich sein; Recovery, Adapter-Cleanup und Lab-Remove bleiben
zwingend. Ein kontrollierter Skip beendet den fachlichen Ablauf ohne Evidenz-,
Erfolgs- oder Promotionsaussage und wird zusammen mit Stufe und Code ausgegeben.

| Stufe | Zulässiger kontrollierter Skip |
|---|---|
| `PRECHECK` | `SKIP_QUERY_STORE_REQUIRED` |
| `TIME_WINDOWS` | `SKIP_INCIDENT_NOT_REPRODUCED` |
| `EVIDENCE` | `SKIP_INCIDENT_NOT_REPRODUCED`, `SKIP_EVIDENCE_MISSING` |
| `COMPARISON` | `SKIP_EVIDENCE_MISSING` |

`REFERENCE_CHANGE` und `RECOVERY` akzeptieren keinen Skip. Jeder andere
Skip, jede fehlende oder mehrdeutige Zusammenfassung und jeder Fehler beendet
den Harness als Fehler.

## Geordnete manuelle Phasen

Die Reihenfolge ist verbindlich. Eine Phase wird erst begonnen, wenn die
vorherige ihren Vertrag erfüllt oder kontrolliert beendet wurde.

1. **PRECHECK – Vertrag und Voraussetzungen:**
   [`00_Preflight.sql`](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/00_Preflight.sql)
   ausführen. Eigentumsmarker, Query-Store-Zustand und Rechte müssen passen.
2. **TIME_WINDOWS – Baseline und Incident-Fenster:**
   [`20_Baseline.sql`](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/20_Baseline.sql)
   ausführen. Die Stufe dokumentiert die vorhandenen Fenster und richtet nur
   die begrenzte Evidenzaufnahme für nachfolgende Vergleichsausführungen ein.
3. **EVIDENCE – gestufte Beobachtung:**
   [`40_Observation.sql`](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/40_Observation.sql)
   stufenweise lesen. Vor der eigenen Hypothese keine spätere Phase ausführen.
4. **HYPOTHESIS – Hypothesenblatt:**
   Für Memory Pressure, I/O-Engpass, Client-/SET-Options-Unterschied und
   Parameter-/Planwiederverwendung jeweils Evidenz, Gegenbefund und Urteil
   notieren. Mindestens zwei Alternativen müssen anhand des passenden Scopes
   verworfen werden.
5. **REFERENCE_CHANGE – reversible Referenzänderung:**
   Erst nach dem dokumentierten Urteil
   [`50_Mitigation.sql`](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/50_Mitigation.sql)
   ausführen. Es ist genau eine Änderung; sie ist kein allgemeiner Tuningrat.
6. **COMPARISON – Vergleichsfenster:**
   [`60_Comparison.sql`](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/60_Comparison.sql)
   ausführen. Das Skript wartet begrenzt auf ein eigenes Query-Store-Intervall,
   prüft vier vorbereitete Parameterklassen auf bidirektionale Ergebnisgleichheit
   und erzeugt dann `T2_COMPARISON`. Nebenwirkungen anhand dieses Fensters
   bewerten.
7. **RECOVERY – lokales Recovery:**
   [`90_Cleanup.sql`](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/90_Cleanup.sql)
   immer ausführen, auch nach Abbruch. Anschließend ausschließlich den
   vorhandenen markergebundenen Adapter-Cleanup verwenden.

## Sichtbarkeit im Modul

`Get-PerformanceTrainingScenario` listet nur freigegebene interaktive
Szenarien. Die statische Übergabe ist ausschließlich gezielt abrufbar:

```powershell
Get-PerformanceTrainingScenario -ScenarioId DGN-007
```

Die Ausgabe zeigt `STATIC_PARTICIPANT_FLOW_ONLY`, dieses Dokument und die
geordneten Phasen. `Start-PerformanceTrainingScenario`,
`Reset-PerformanceTrainingScenario` und `Remove-PerformanceTrainingScenario`
akzeptieren `DGN-007` nicht, solange kein validierter Szenariovertrag und kein
Runtime-Nachweis vorliegen.

## Statusgrenze

Die Teilnahmephasen sind statisch dokumentiert. Sie beweisen weder eine
Provider-/Versionsmatrix noch einen Lifecycle. Diese Nachweise und eine
didaktische Abnahme bleiben separat offen.
