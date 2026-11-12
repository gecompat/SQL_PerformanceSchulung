# Graph Tables: ScriptDom-Grammatikprüfung für QRY-023

Stand: 7. November 2026  
Status: statische Grammatikprüfung; keine SQL-Server-Kompilierung oder Ausführung

## Prüfmethode

Der statische CI-Workflow verwendet Microsoft `Microsoft.SqlServer.TransactSql.ScriptDom`
in der festgehaltenen NuGet-Version `170.191.0`. Das eigenständige .NET-10-
Projekt bindet den exakten Paketinhalt mit `packages.lock.json`. Es liest alle
neun erwarteten QRY-023-`.sql`-Dateien ein, prüft die Dateiliste und parst die
acht ausführbaren T-SQL-Quelldateien je mit `TSql150Parser`, `TSql160Parser`
und `TSql170Parser`. Damit werden die Grammatiken der drei vorgeschlagenen
Projektprofile geprüft.

Die drei SQLCMD-Variablen `$(DemoId)`, `$(RunToken)` und
`$(TargetDatabase)` werden nur im flüchtigen Parser-Eingabetext mit
synthetischen Werten ersetzt. Die zusätzlich benötigte SQLCMD-Direktive für
`SQLCMDMAXVARTYPEWIDTH` wird im Strukturvalidator exakt gebunden und vor dem
T-SQL-Parsing aus dem Parser-Eingabetext entfernt; die Direktive selbst ist
keine T-SQL-Syntax. `15_Framework.sql` ist ein SQLCMD-`:r`-Wrapper,
kein eigenständiges T-SQL: der Prüfer parst ihn nicht, sondern bestätigt separat
den erwarteten Include-Pfad zur kanonischen `FWK-004`-Referenz.

## Ergebnis und Grenzen

Am 7. November 2026 bestanden alle acht Dateien die Grammatikparser 150, 160
und 170. Es wurde kein SQL Server angesprochen; weder QRY-023-SQL noch ein
SQLCMD-Harness wurden gestartet.

Ein ScriptDom-PASS belegt ausschließlich, dass der Parsertext mit diesen
Grammatiken ohne Parserfehler verarbeitet wurde. Er beweist keine Bindung von
Objekten, Datenbankkontext, Edition, Berechtigungen, gespeicherten
Prozedurverträgen oder SQL-Engine-Kompilierung und keine tatsächliche
Ausführbarkeit. SQLCMD-Expansion über die drei expliziten Platzhalter und die
separat strukturell gebundene `SQLCMDMAXVARTYPEWIDTH`-Direktive hinaus sowie
die eingebundene Frameworkdatei sind nicht Teil dieses Grammatikdurchlaufs.
Unabhängige Methodenfreigabe, formale Harness-Abnahme und jede konkrete
Runtimequalifikation bleiben offen.

Der Workflow wird nur durch Änderungen am QRY-023-Demopfad, Parser, seinem
Regressionstest oder dem eigenen Workflow ausgelöst. Er führt die vorhandenen
Python-Strukturprüfungen, eine gesperrte NuGet-Wiederherstellung und drei
Parserdurchläufe je T-SQL-Datei innerhalb eines fünfminütigen statischen Jobs
aus. Keine SQL-Container-, Lab- oder Runtime-Matrix wird dadurch ausgelöst.

## Quellen

- `SRC-128`: [Projektquellenregister](../Research/SOURCE_REGISTER.md#graph-tables--eng-begrenzte-sql-graph--und-compatibility-quellen) bindet die Microsoft-Implementierung und unterstützten Grammatiken des ScriptDom-Parsers.
- `SRC-129`: derselbe Registerabschnitt bindet den festgeschriebenen [ScriptDom-NuGet-Paketstand 170.191.0](https://www.nuget.org/packages/Microsoft.SqlServer.TransactSql.ScriptDom/170.191.0).
