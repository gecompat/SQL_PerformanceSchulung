# QRY-006 – NULL-Semantik von `NOT IN` und `NOT EXISTS`

| Merkmal | Wert |
|---|---|
| Status | `IMPLEMENTED` – lokale Docker-Runtime-Matrix bestanden; Runtime-Gate noch ausstehend |
| Sicherheitsstufe | `GREEN` |
| Zielversionen | SQL Server 2019, 2022 und 2025 |
| Compatibility Level | 150, 160 und 170 |
| Edition / Plattform | Database Engine; Windows oder Linux |
| Sessions | 1 |
| Ausführungspfad | `TSQL_TESTDB` |
| Testprofil | `TP-RUN` |

## 1. Lernziel

Nach der Demo kann die lernende Person erklären, warum ein `NULL` in der Vergleichsmenge von `NOT IN` die ungefilterte Abfrage leer machen kann, und die Ergebnisgrenze gegenüber `NOT EXISTS` anhand einer kleinen synthetischen Menge prüfen.

## 2. Fachliche Kernaussage

**Evidenzklasse:** `DOKUMENTIERT`

Für Parent `{1,2,3}` und Child `{1,NULL}` liefert das ungefilterte `NOT IN` keine Zeile. `NOT EXISTS` und `NOT IN` mit `WHERE ChildKey IS NOT NULL` liefern jeweils die explizite Anti-Menge `{2,3}`. Die Erklärung beschränkt sich auf die dreiwertige Logik: Eine `WHERE`-Bedingung gibt nur `TRUE` weiter.

## 3. Nichtziel

Die Demo macht keine Aussage über Performance, Indizes, Optimizer-Transformationen oder physische Planformen. Sie ist keine allgemeine Umformungsregel für beliebige nullable Datenmodelle.

## 4. Voraussetzungen

SQL Server 2019 bis 2025 mit Compatibility Level 150, 160 beziehungsweise 170 und `CREATE DATABASE` für die eigene markergebundene Testdatenbank. Weitere Server-State- oder Planberechtigungen sind nicht erforderlich.

## 5. Sicherheits- und Abbruchrahmen

Die grüne Demo erzeugt ausschließlich die synthetische Datenbank `SQLPERF_LAB_QRY006_<RunToken>`. Sie ändert keine Instanzoptionen und verwendet keine globalen Cache-, Index- oder Planoperationen. Der manifestbasierte Cleanup löscht die Datenbank nur nach vollständiger Prüfung der vier Eigentumsmarker.

## 6. Synthetisches Datenmodell

`lab.Qry006Parent` enthält genau die Schlüssel `1`, `2` und `3`. `lab.Qry006Child` enthält exakt zwei Zeilen: `1` und ein `NULL`. Es gibt keine zusätzlichen Spalten, Duplikate oder fachlichen Nebendaten.

## 7. Ablauf

### 7.1 Schritt-für-Schritt-Anleitung

Die vollständige Ausführung steht im [`DEMO_EXECUTION_GUIDE.md`](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md): `QRY-006` auswählen, den manifestbasierten Aufruf ausführen und je Phase `SQLPERF_SUMMARY|PASS|OK` erwarten. Die grüne Demo benötigt keine Zusatzbestätigung. Nach Abbruch ausschließlich den markergebundenen Cleanup aus dem Leitfaden verwenden.

| Phase | Datei | Zweck |
|---|---|---|
| Preflight | `00_Preflight.sql` | Version, Berechtigung und Zielkennung prüfen |
| Setup | `10_Setup.sql` | markierte Testdatenbank und feste Parent-/Child-Menge anlegen |
| Demonstration | `30_Demonstration.sql` | die drei Abfrageformen mit beschrifteten Ergebnissen ausgeben |
| Ergebnisassertion | `40_Result_Assertion.sql` | leere Menge und die explizite Anti-Menge unabhängig von der Darstellung prüfen |
| Cleanup | `90_Cleanup.sql` | nur vollständig markierte Datenbank idempotent entfernen |

Eine Mitigation-Phase ist absichtlich nicht vorhanden: Das gefilterte `NOT IN` ist hier die semantische Gegenprobe, nicht die Bewertung einer Performance-Gegenmaßnahme.

## 8. Erwartete Beobachtung

Die erste Ausgabe für ungefiltertes `NOT IN` enthält keine Zeile. Die Ausgaben für `NOT EXISTS` und gefiltertes `NOT IN` enthalten jeweils `2` und `3`. Die Assertion prüft die Mengen durch beidseitige `EXCEPT`-Vergleiche.

Vor dem Cleanup liest die Assertion außerdem das tatsächliche Compatibility Level der Testdatenbank aus `sys.databases` und prüft es gegen die Versionsmatrix. Der Runtime-Runner wertet diesen Nachweis aus und prüft nach jedem vollständigen Manifestlauf unabhängig, dass die Testdatenbank entfernt wurde.

## 9. Interpretation

Für Parent-Werte ohne passende Child-Zeile wird der Vergleich mit der `NULL`-Zeile nicht zu `TRUE`. Daher qualifiziert die ungefilterte `NOT IN`-Bedingung keine dieser Zeilen. `NOT EXISTS` prüft dagegen die Existenz einer passenden korrelierten Child-Zeile; die filternde Gegenprobe entfernt das `NULL` aus der Vergleichsmenge.

## 10. Cleanup und Wiederherstellung

`90_Cleanup.sql` liest `SQLPERF.Project`, `SQLPERF.ContractVersion`, `SQLPERF.DemoId` und `SQLPERF.RunToken`. Bei fehlender Datenbank endet der Cleanup erfolgreich und idempotent; bei abweichendem Marker wird nichts gelöscht.

## 11. Tests

`Tests/Static/validate_qry006_null_semantics_design.py` prüft den implementierten Bündelvertrag, die feste Datenmenge, die Ergebnisassertion, den bewussten Verzicht auf Mitigation sowie das Fehlen von Performance-, Index- und Planformbehauptungen. Die lokale Runtime-Matrix auf SQL Server 2019/150, 2022/160 und 2025/170 ist mit je zwei vollständigen Manifestläufen bestanden. Die Evidenz steht in [`QRY_006_RUNTIME_EVIDENCE.md`](../../../Documentation/Project_Planning/QRY_006_RUNTIME_EVIDENCE.md). Der Status bleibt bis zum vorgesehenen Runtime-Gate `IMPLEMENTED`, nicht `VALIDATED`; ein GitHub-Actions-Lauf und eine SQL_Server_Lab-Szenariopromotion sind damit nicht behauptet.

## 12. Bekannte Grenzen

Die Demo beweist nur den festgelegten kleinen NULL-Gegenfall. Sie bewertet weder komplexere mehrspaltige Vergleiche noch die fachliche Zulässigkeit von `NULL` in einem konkreten Datenmodell.

## 13. Quellen

| Quellen-ID | Aussagebezug | Gültigkeitsbereich | Abrufdatum |
|---|---|---|---|
| `SRC-069` | `IN` und `NOT IN` bei `NULL`-Rückgabewerten | SQL Server 2019–2025 | 2026-09-19 |
| `SRC-070` | `EXISTS` und `NOT EXISTS` als Existenzprüfung | SQL Server 2019–2025 | 2026-09-19 |
| `SRC-071` | dreiwertige Logik mit `NULL` und `UNKNOWN` | SQL Server 2019–2025 | 2026-09-19 |

## 14. Traceability

| Element | Zuordnung |
|---|---|
| Lernziel | `LO-M02-10` |
| Claim | `ADV-CLM-011` |
| Demo-ID | `QRY-006` |
| Testprofil | `TP-RUN` |
