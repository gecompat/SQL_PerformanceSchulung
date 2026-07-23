# Demo-Vertrag

## Pflichtangaben

Jede Demo dokumentiert:

1. stabile Demo-ID und Titel,
2. Lernziel,
3. fachliche Kernaussage,
4. SQL-Server-Version, Compatibility Level, Edition und Betriebssystemabhängigkeiten,
5. erforderliche Rechte, Konfiguration und Ressourcen,
6. Sicherheitsstufe,
7. geschätzte Laufzeit und Speicherbelegung,
8. Setup und synthetisches Datenmodell,
9. Baseline-Messung,
10. kontrollierte Problemerzeugung,
11. Beobachtung und technische Evidenz,
12. Gegenmaßnahme,
13. Vorher-/Nachher-Vergleich,
14. erwartete Resultate und zulässige Abweichungen,
15. Cleanup und Wiederherstellung geänderter Optionen,
16. Quellen mit Abrufdatum.

## Empfohlener Dateiaufbau

| Datei/Pfad | Zweck |
|---|---|
| `README.md` | Lernziel, Ablauf, Voraussetzungen, Interpretation und Quellen |
| `00_Preflight.sql` | Version, Rechte, Edition, Konfiguration und Sicherheitsprüfung |
| `10_Setup.sql` | idempotenter Aufbau der isolierten Labordaten |
| `20_Baseline.sql` | Ausgangsmessung |
| `30_Demonstration.sql` | kontrollierte Erzeugung des Effekts |
| `40_Observation.sql` | Plans, DMVs, Query Store oder Extended-Events-Evidenz |
| `50_Mitigation.sql` | gezielte Gegenmaßnahme |
| `60_Comparison.sql` | identische Messung nach der Gegenmaßnahme |
| `90_Cleanup.sql` | vollständige, wiederholbare Bereinigung |
| `Sessions/` | nummerierte Batches für Multi-Session-Szenarien |
| `Expected/` | datenschutzgeprüfte, synthetische Erwartungsresultate |

Nicht jede Demo benötigt jede Datei. Fehlende Phasen sind im README zu begründen.

## Sicherheitsstufen

### Grün

Lokal begrenzte T-SQL-Demo ohne relevante Instanzwirkung. In einer dedizierten Schulungsdatenbank ausführbar.

### Gelb

Erzeugt kontrolliert hohe CPU-, RAM-, TempDB-, I/O-, Log- oder Concurrency-Last. Benötigt eine isolierte Instanz und definierte Abbruchbedingungen.

### Rot

Verändert Instanz- oder Betriebssystemkonfiguration, leert globale Caches, startet Dienste neu, manipuliert Infrastruktur oder erzeugt absichtlich beschädigte Zustände. Ausschließlich in einer wegwerfbaren Lab-Umgebung.

## Messregeln

- Vorher und nachher dieselbe Abfrage, Parametrisierung und Messmethode verwenden.
- CPU, Duration, Logical Reads, Physical Reads, Writes, Rows und Memory Grant passend zum Thema erfassen.
- Cache- und Warm-up-Effekte ausdrücklich behandeln.
- Einzelläufe nicht als allgemeingültigen Benchmark darstellen.
- Hardwareabhängige Resultate als empirisch kennzeichnen.
- Instanzweite DMV-Summen nur als Delta eines definierten Zeitfensters interpretieren.

## Verbote

- Keine realen Diagnosedaten oder Screenshots.
- Keine globalen Eingriffe ohne rote Kennzeichnung und Preflight.
- Keine verschleierten Abhängigkeiten von nicht mitgelieferten Datenbanken.
- Keine Erfolgsaussage ohne messbare Evidenz.
