# Graph Tables: Editions- und Buildprüfung für QRY-023

Stand: 7. November 2026  
Status: aktuelle Quellenprüfung; vorgeschlagene Qualifikationspins, keine Ausführung

## Befund

Microsofts Editionsmatrizen führen SQL Graph für SQL Server 2019 und 2022 in
allen dort aufgeführten Editionen (Enterprise, Standard, Web sowie Express mit
Advanced Services und Express) als verfügbar. Die 2025-Matrix weist Graph
Tables für Enterprise, Standard und Express aus. Für Developer und Evaluation
gelten laut 2025-Seite die Enterprise-Featurezeilen; für 2022 entsprechend die
Enterprise-Zuordnung der Entwickler-/Evaluierungsausgaben. Damit ist keine
Graph-spezifische Editionsbeschränkung in den drei Projektprofilen erkennbar.
Die eigentliche QRY-023-Ausführung verlangt unabhängig davon `CREATE DATABASE`,
Objekt-/DML-Rechte sowie `SELECT` und `SHOWPLAN` nach den jeweiligen Phasen.

Die Microsoft-Übersicht der verfügbaren Updates weist zum 7. November 2026
folgende jüngste qualifizierende Builds aus:

| Projektprofil | Compatibility Level | Servicingstand am 7.11.2026 | Vorgeschlagener QRY-023-Build |
|---|---:|---|---:|
| SQL Server 2019 (15.x) | 150 | CU32 + GDR | `15.0.4500.2` |
| SQL Server 2022 (16.x) | 160 | CU27 + GDR | `16.0.4305.5` |
| SQL Server 2025 (17.x) | 170 | CU10 | `17.0.5035.5` |

Das sind zeitgebundene, reproduzierbare **Design-/Qualifikationspins**, keine
Mindestbuilds für Graph Tables. Die Graph-Dokumentation weist die Funktion ab
SQL Server 2017 aus; sie setzt für diese Graph-DDL-/`MATCH`-Funktionen keine
bestimmte CU-Stufe voraus. Die vorgeschlagenen Builds wählen den zum Abrufdatum
von Microsoft veröffentlichten neuesten CU-/GDR-Stand, nicht einen empirisch
getesteten Container.

`00_Preflight.sql` soll ausschließlich den zum jeweiligen Profil passenden
Build zulassen und bei Abweichung vor Setup `SKIP_VERSION` zurückgeben.
`10_Setup.sql` prüft denselben Build vor jeder Datenbankanlage erneut. Beide
Skripte protokollieren die tatsächliche Edition. Das belegt weder die exakte
Imageidentität noch den tatsächlich gestarteten SQL-Server-Build; vor einem
späteren Lauf muss die Image-Digestbindung separat ergänzt und `SERVERPROPERTY`
im Laufresultat geprüft werden. Ein späteres CU/GDR führt zunächst zum
begründeten Skip, bis Quellenstand, Pin und Prüfer erneuert wurden.

Die Compatibility Levels 150/160/170 bleiben die Projektmatrix und sind keine
Graph-Featureanforderung. Der Abgleich des `ALTER DATABASE`-Levels mit dem
konkreten Build und die T-SQL-Kompilierbarkeit sind nicht durch diese
Editions-/Servicingquellen qualifiziert. QRY-023 bleibt `PROPOSED`/`YELLOW`,
nicht katalogisiert und ungefahren. Unabhängige Methodenfreigabe, formale
T-SQL-/Harness-Abnahme, Ressourcenprofil und konkrete Ausführungsautorisierung
bleiben offen.

## Quellen

- `SRC-126`: [Projektquellenregister](../Research/SOURCE_REGISTER.md#graph-tables--eng-begrenzte-sql-graph--und-compatibility-quellen) bindet die Editionsmatrizen für 2019, 2022 und 2025.
- `SRC-127`: Microsofts [Übersicht aktueller SQL-Server-Updates](https://learn.microsoft.com/en-us/sql/database-engine/install-windows/latest-updates-for-microsoft-sql-server?view=sql-server-ver17) bindet die Builds und deren CU/GDR-Stände am 7. November 2026.
- `SRC-122` und `SRC-123`: derselbe Quellenregisterabschnitt bindet Graph-Unterstützung ab SQL Server 2017 und die Compatibility-Level-Zuordnung.
