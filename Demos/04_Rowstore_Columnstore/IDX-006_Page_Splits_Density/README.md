# IDX-006 – Page Splits, Density und Fragmentierung

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheit | `YELLOW`, frische Wegwerf-Instanz |
| Versionen | SQL Server 2019, 2022, 2025 |
| Profil / Budget | `standard`, 360 Sekunden |

`LO-M04-05`, `CLM-057` und `CLM-058`: Page Splits, logische Fragmentierung und Seitendichte sind verschiedene Messgrößen. Zwei inhaltlich gleiche Tabellen erhalten Fill Factor 100 beziehungsweise 80; Einfügungen in Schlüssellücken werden gegen `sys.dm_db_index_operational_stats` und `sys.dm_db_index_physical_stats` gemessen. Ergebnisgleichheit ist exakt, die Split- und Density-Richtung ist empirisch und darf `WARN_EMPIRICAL_VARIANCE` liefern.

`SRC-014` und `SRC-015` sind `ACTIVE`. Die Demo gibt keine globale Rebuild-Schwelle vor und trennt Wartungseffekt von Workloadnutzen. Sie benötigt ein bestätigtes isoliertes Lab, positives Budget und markergeprüftes Cleanup. Am 2026-08-29 liefen alle drei Zielversionen je zweimal mit `WARN_EMPIRICAL_VARIANCE`: Ergebnisgleichheit und Messkette waren vollständig, nur eine pauschale Splitreduktion durch Fill Factor 80 trat bewusst nicht als universelle Invariante auf.

## 7. Ablauf

### 7.1 Schritt-für-Schritt-Anleitung

1. Öffnen Sie den [zentralen Ausführungsleitfaden](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md) und wählen Sie dort die Demo-ID `IDX-006`.
2. Prüfen Sie die dort genannten Voraussetzungen und die Sicherheitsstufe `YELLOW`. Bestätigen Sie vor dem Start die isolierte Laborinstanz mit `-ConfirmIsolatedLab`.
3. Laden Sie den manifestbasierten PowerShell-Aufrufer aus Schritt 4 des Leitfadens und führen Sie `Invoke-SqlPerfDemo -DemoId IDX-006 -Server $server -Authentication $authentication -Username $username -ConfirmIsolatedLab` aus.
4. Prüfen Sie die `SQLPERF_SUMMARY` und die erwartete Beobachtung in dieser README.
5. Wenn der Lauf abbricht, verwenden Sie ausschließlich das markergebundene Cleanup aus dem zentralen Ausführungsleitfaden; entfernen Sie keine Datenbank manuell anhand ihres Namens.
