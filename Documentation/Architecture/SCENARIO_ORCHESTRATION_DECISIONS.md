# Szenario-Orchestrierung – verbindliche Projektleitlinien

Diese Datei ergänzt `Documentation/Architecture/TSQL_SCENARIO_ORCHESTRATION.md` aus dem Schwesterprojekt und macht deren Architekturentscheidungen für dieses Repository verbindlich.

## Verbindliche Regeln

1. T-SQL bleibt die fachliche Source of Truth.
2. Beispiele werden immer als eigenständige T-SQL-Skripte aufgebaut.
3. Es wird immer die kleinste ausreichende Orchestrierungsstufe verwendet:
   - MANUAL
   - RUNNER_ASSISTED
   - AUTOMATED_VERIFY
4. SQL_Server_Lab ist ausschließlich für Infrastruktur verantwortlich.
5. Szenario-Orchestrierung, Sessionsteuerung, Workloads und Diagnose gehören in dieses Repository.
6. Runner koordinieren Sessions und Timing, enthalten aber keine fachliche SQL-Logik.
7. Automatische Tests prüfen nur stabile Invarianten und ersetzen nicht den interaktiven Lernablauf.
8. Jede neue Beispielwelle klassifiziert Szenarien nach ihrer Orchestrierungsstufe.

## Auswirkungen auf zukünftige Entscheidungen

- Zuerst immer prüfen, ob ein Szenario manuell reproduzierbar ist.
- Erst bei Bedarf Runner-Unterstützung ergänzen.
- Infrastruktur-Erweiterungen in SQL_Server_Lab nur dann anfordern, wenn allgemeine technische Fähigkeiten fehlen; komplexe Sessionabläufe allein sind kein Lab-Gap.
