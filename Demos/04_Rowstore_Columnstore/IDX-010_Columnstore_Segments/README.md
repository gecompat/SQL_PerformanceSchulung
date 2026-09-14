# IDX-010 – Columnstore-Segmente und Segment Elimination

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheit | `YELLOW`, dediziertes `performance`-Profil |
| Versionen | SQL Server 2019, 2022, 2025 |
| Daten / Budget | 1,2 Mio. synthetische Zeilen, 720 Sekunden |

`LO-M04-06`, `LO-M04-07`, `CLM-060` und `CLM-061`: Batch Mode, Segment Elimination und Rowgroup-Qualität sind getrennte Eigenschaften. Sortierte und deterministisch verwürfelte Loads werden als klassische Clustered Columnstore Indexes aufgebaut. `sys.column_store_segments` zeigt Segmentüberlappung; `sys.dm_db_column_store_row_group_physical_stats` zeigt Rowgroupzustand und gelöschte Zeilen. Ergebnisgleichheit ist exakt, Segmentanzahl und Laufzeitwirkung sind empirisch.

`SRC-016`, `SRC-017` und `SRC-015` sind `ACTIVE`. Ordered nonclustered columnstore indexes aus SQL Server 2025 sind laut Delta-Review `DEFER` und werden hier weder erstellt noch behauptet. Ressourcen- oder Kompressionsgrenzen werden kontrolliert übersprungen. Am 2026-08-29 liefen alle Zielversionen im Vier-CPU-/8-GB-Profil je zweimal mit `PASS/OK`, komprimierten Rowgroups, Segment- und Ergebnisevidenz sowie vollständigem Cleanup.

## 7. Ablauf

### 7.1 Schritt-für-Schritt-Anleitung

1. Öffnen Sie den [zentralen Ausführungsleitfaden](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md) und wählen Sie dort die Demo-ID `IDX-010`.
2. Prüfen Sie die dort genannten Voraussetzungen und die Sicherheitsstufe `YELLOW`. Bestätigen Sie vor dem Start die isolierte Laborinstanz mit `-ConfirmIsolatedLab`.
3. Laden Sie den manifestbasierten PowerShell-Aufrufer aus Schritt 4 des Leitfadens und führen Sie `Invoke-SqlPerfDemo -DemoId IDX-010 -Server $server -Authentication $authentication -Username $username -ConfirmIsolatedLab` aus.
4. Prüfen Sie die `SQLPERF_SUMMARY` und die erwartete Beobachtung in dieser README.
5. Wenn der Lauf abbricht, verwenden Sie ausschließlich das markergebundene Cleanup aus dem zentralen Ausführungsleitfaden; entfernen Sie keine Datenbank manuell anhand ihres Namens.
