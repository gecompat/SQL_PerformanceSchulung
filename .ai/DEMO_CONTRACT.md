# Demo-Vertrag

## Verbindliche Framework-Basis

Jede ausführbare Demo verwendet die Verträge aus `Demos/00_Framework/`:

- `FWK-001` für den read-only Preflight,
- `FWK-002` für Name, Eigentumsmarker und Lifecycle der synthetischen Testdatenbank,
- `FWK-008` für Sicherheitsstufe, Bestätigung, Abbruch und Recovery,
- `FWK-009` als Dokumentstruktur,
- `FWK-012` für `PASS`, `WARN`, `SKIP`, `FAIL` und die zugehörigen Codes.

Eine Abweichung ist im Demo-README fachlich zu begründen und durch einen gleichwertigen oder strengeren Test nachzuweisen.

## Pflichtangaben

Jede Demo dokumentiert:

1. stabile Demo-ID und Titel,
2. Lernziel,
3. fachliche Kernaussage und Evidenzklasse,
4. SQL-Server-Version, Compatibility Level, Edition und Betriebssystemabhängigkeiten,
5. erforderliche Rechte, Konfiguration und Ressourcen,
6. Mindestanforderungen an die Host-Hardware,
7. Sicherheitsstufe,
8. geschätzte Laufzeit, Sessionzahl und Speicherbelegung,
9. Setup und synthetisches Datenmodell,
10. Baseline-Messung,
11. kontrollierte Problemerzeugung,
12. Beobachtung und technische Evidenz,
13. Gegenmaßnahme,
14. Vorher-/Nachher-Vergleich,
15. erwartete Resultate und zulässige Abweichungen,
16. Cleanup, Abbruch und Wiederherstellung geänderter Optionen,
17. Quellen mit Abrufdatum,
18. Traceability zu Lernziel, Claim, Demo-ID und Testprofil.

## Empfohlener Dateiaufbau

| Datei/Pfad | Zweck |
|---|---|
| `README.md` | Lernziel, Ablauf, Voraussetzungen, Interpretation, Tests und Quellen |
| `00_Preflight.sql` | Version, Rechte, Edition, Datenbankzustand, Sicherheits- und Ressourcenprüfung |
| `10_Setup.sql` | idempotenter Aufbau der isolierten Labordaten |
| `20_Baseline.sql` | Ausgangsmessung |
| `30_Demonstration.sql` | kontrollierte Erzeugung des Effekts |
| `40_Observation.sql` | Plans, DMVs, Query Store oder Extended-Events-Evidenz |
| `50_Mitigation.sql` | gezielte Gegenmaßnahme |
| `60_Comparison.sql` | identische Messung nach der Gegenmaßnahme |
| `90_Cleanup.sql` | vollständige, wiederholbare Bereinigung und Recovery |
| `Sessions/` | nummerierte Batches für Multi-Session-Szenarien |
| `Expected/` | datenschutzgeprüfte, synthetische Erwartungsresultate |

Nicht jede Demo benötigt jede Datei. Fehlende Phasen sind im README zu begründen. Setup und Cleanup dürfen keine versteckte Abhängigkeit von SQLCMD, einer Steuerdatenbank oder nicht mitgelieferten Objekten besitzen, sofern diese Abhängigkeit nicht ausdrücklich Teil des Demo-Vertrags ist.

## Testdatenbankvertrag

Synthetische Testdatenbanken folgen dem Schema:

```text
SQLPERF_LAB_<DEMO-ID OHNE BINDESTRICH>_<RUN-TOKEN>
```

Der Name wird aus kanonischer Demo-ID und synthetischem Run-Token abgeleitet. Vor einer Entfernung müssen die Marker `SQLPERF.Project`, `SQLPERF.ContractVersion`, `SQLPERF.DemoId` und `SQLPERF.RunToken` vollständig und exakt übereinstimmen. Ein passender Name allein genügt nicht.

## Sicherheitsstufen

### Grün

Lokal begrenzte T-SQL-Demo ohne relevante Instanzwirkung. In einer dedizierten, markierten Schulungsdatenbank ausführbar.

### Gelb

Erzeugt kontrolliert hohe CPU-, RAM-, TempDB-, I/O-, Log- oder Concurrency-Last. Benötigt ein bestätigtes isoliertes Lab, eine positive Laufzeitgrenze, Abbruchsignal und Recovery.

### Rot

Verändert Instanz- oder Betriebssystemkonfiguration, leert globale Caches, startet Dienste neu, manipuliert Infrastruktur oder erzeugt absichtlich beschädigte Zustände. Ausschließlich in einer bestätigten wegwerfbaren Lab-Umgebung mit dokumentiertem Resetpfad. Rote Demos laufen nicht im unbeaufsichtigten Standard-CI.

## Messregeln

- Vorher und nachher dieselbe Abfrage, Parametrisierung und Messmethode verwenden.
- CPU, Duration, Logical Reads, Physical Reads, Writes, Rows und Memory Grant passend zum Thema erfassen.
- Cache- und Warm-up-Effekte ausdrücklich behandeln.
- Einzelläufe nicht als allgemeingültigen Benchmark darstellen.
- Hardwareabhängige Resultate als empirisch kennzeichnen.
- Instanzweite DMV-Summen nur als Delta eines definierten Zeitfensters interpretieren.
- `Wait Type`, Planoperator oder Estimated-/Actual-Abweichung allein ist kein Ursachenbeweis.

## Status- und Fehlerregeln

- `PASS`: Prüfung oder Phase erfolgreich.
- `WARN`: ausführbar, aber Interpretation eingeschränkt.
- `SKIP`: erwartete Voraussetzung nicht erfüllt; keine zustandsverändernde Folgephase.
- `FAIL`: Vertrags-, Sicherheits-, Zustands-, Ausführungs- oder Cleanup-Fehler.

Ein `SKIP` wird nicht als Engine-Fehler dargestellt. Ein Cleanup-Fehler darf nicht als `SKIP` oder Erfolg kaschiert werden.

## Verbote

- Keine realen Diagnosedaten oder Screenshots als Repository-Artefakt.
- Keine globalen Eingriffe ohne rote Kennzeichnung und Preflight.
- Keine verschleierten Abhängigkeiten von nicht mitgelieferten Datenbanken.
- Keine Erfolgsaussage ohne messbare Evidenz.
- Kein `DROP DATABASE` aufgrund eines Namens allein.
- Keine Beendigung fremder Sessions allein nach Loginname, Application Name oder Hostname.
- Keine festen, maschinenunabhängig behaupteten Laufzeit- oder Ressourcenschwellen.
