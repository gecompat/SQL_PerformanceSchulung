# Graph Tables: Editions- und Buildprüfung für QRY-023

Stand: 12. November 2026
Status: aktuelle Servicingquellenbestätigung gemäß `DEC-081`; vorgeschlagene Qualifikationspins, keine Ausführung

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

Die erneute Microsoft-Versionshistorieprüfung vom 12. November 2026 weist
weiterhin die jüngsten Servicingbuilds aus. Die MCR-Tagliste enthält sowohl
CU-only- als auch GDR-Linux-Tags; deren Namen allein reichen nicht als
Buildnachweis. Für die im
QRY-023-Entwurf verwendeten GDR-Tags wurde das Single-Platform-Manifest samt
Konfiguration read-only abgefragt. Das Image-Label `com.microsoft.version`
stimmt bei allen drei Profilen mit dem jeweiligen Produktbuild überein. Kein
Image wurde heruntergeladen oder gestartet.

| Projektprofil / Linux-Image | Compatibility Level | Produktservicing laut Microsoft | Image-Label `com.microsoft.version` |
|---|---:|---|---:|
| SQL Server 2019 `2019-CU32-GDR12-ubuntu-20.04` | 150 | CU32 + GDR `15.0.4500.2` | `15.0.4500.2` |
| SQL Server 2022 `2022-CU27-GDR1-ubuntu-22.04` | 160 | CU27 + GDR `16.0.4305.5` | `16.0.4305.5` |
| SQL Server 2025 `2025-CU10-ubuntu-22.04` | 170 | CU10 `17.0.5035.5` | `17.0.5035.5` |

Die geprüften AMD64-Manifest- und Konfigurationsdigests lauten:

| Profil | Manifestdigest | Konfigurationsdigest |
|---|---|---|
| 2019 | `sha256:07d7dedecdbfcf6776035dc5eefb5bfd9aa1804b2f6b99f7dedb397d8a599069` | `sha256:d47c3524cdcabc59024d5cca4f9888e4eff01d7efc5ceedd0f4e383cc72a8366` |
| 2022 | `sha256:cf8f0ab2ebe61feec2eed2629061a07d247f791c2a8ddda74a4ac9f06a291718` | `sha256:7fb2139341715e8a71843cfc2f02bab6e95f1c52c0fa9f9a6b2e7b761f060780` |
| 2025 | `sha256:6972fb831759433def6a34e107fa32a85230bff5af8014c6263fe4633ea9cc0f` | `sha256:e6b27c1b6b7c1faa799fc4cd831c442bb36a8f7a7f214e780652e8cc09a26625` |

Für die drei GDR-/CU-Images sind deshalb `15.0.4500.2`, `16.0.4305.5` und
`17.0.5035.5` weiterhin passende Design-/Qualifikationspins; Microsoft führt
sie auch am 12. November 2026 als neueste dokumentierte Linux-Servicingbuilds.
Die vorhandene OCI-Manifestprüfung und Labels stammen vom 7. November; die
Tags wurden beim aktuellen Standcheck nicht erneut abgefragt. Die
plain-CU-Tags `2019-CU32-ubuntu-20.04` und `2022-CU27-ubuntu-22.04` enthalten
ältere Buildstände und werden nicht verwendet. Die Konfiguration beschreibt
nicht den tatsächlich
gestarteten Engineprozess: ein späterer Lauf muss Image-Manifestdigest und
`SERVERPROPERTY('ProductVersion')` binden.

Diese Builds sind zeitgebundene, reproduzierbare **Design-/Qualifikationspins**,
keine Mindestbuilds für Graph Tables. Die Graph-Dokumentation weist die Funktion ab
SQL Server 2017 aus; sie setzt für diese Graph-DDL-/`MATCH`-Funktionen keine
bestimmte CU-Stufe voraus. Die vorgeschlagenen Builds wählen den zum Abrufdatum
verfügbaren offiziellen Linux-Servicingbuild, aber keinen empirisch getesteten Container.

`00_Preflight.sql` soll ausschließlich den zum jeweiligen Profil passenden
Build zulassen und bei Abweichung vor Setup `SKIP_VERSION` zurückgeben.
`10_Setup.sql` prüft denselben Build vor jeder Datenbankanlage erneut. Beide
Skripte protokollieren die tatsächliche Edition. Der vorgeschlagene Image-Lock
ist noch nicht in einen Runtimeaufruf integriert und belegt nicht den
tatsächlich gestarteten SQL-Server-Build; vor einem späteren Lauf müssen
Image-Digest und `SERVERPROPERTY` im Laufresultat gebunden werden. Ein späteres CU/GDR führt zunächst zum
begründeten Skip, bis Quellenstand, Pin und Prüfer erneuert wurden.

Die Compatibility Levels 150/160/170 bleiben die Projektmatrix und sind keine
Graph-Featureanforderung. Der Abgleich des `ALTER DATABASE`-Levels mit dem
konkreten Build und die T-SQL-Kompilierbarkeit sind nicht durch diese
Editions-/Servicingquellen qualifiziert. QRY-023 bleibt `PROPOSED`/`YELLOW`,
nicht katalogisiert und ungefahren. `DEC-079` genehmigt die Methodik und
`DEC-080` akzeptiert den statischen ScriptDom-Parse. Formale Harnessabnahme,
Ressourcenprofil und konkrete Ausführungsautorisierung bleiben offen.

## Vorgeschlagene Ressourcenbegrenzung

Microsoft nennt für SQL Server auf Linux mindestens zwei x64-kompatible
Prozessorkerne zu 2 GHz, 2 GB Arbeitsspeicher und 6 GB Speicherplatz. Das ist
die Produktstartanforderung, keine ausreichende Messumgebung für QRY-023. Für
die noch ungefahrene Demo schlägt der Projektentwurf 8 GiB Host-RAM, 20 GiB
freien Speicher, höchstens zwei Containerkerne, ein Containerlimit von 4.096
MiB und `MSSQL_MEMORY_LIMIT_MB=3072` vor. Der SQL-Prozess liegt damit unter
der harten Containergrenze; 2 GiB sind die Microsoft-Mindestmenge zum Start.

Die Hostreserve über den Produktminimumwerten und die 4/3-GiB-Aufteilung sind
bewusste Planungsannahmen, keine Messwerte oder Laufzeitmachbarkeit. Die
MCR-Manifeste weisen je Profil drei komprimierte Layers mit zusammen rund
0,53–0,64 GB aus; das ersetzt weder den installierten Dateisystembedarf von
6 GB noch eine qualifizierte Datenbank-/TempDB-Spitzenmessung. Das Zeitbudget
bleibt aus dem vorgeschlagenen Manifest bei 900 Sekunden plus 90 Sekunden
Cleanup. Ein künftiger Runtimeaufrufer muss CPU-, Speicher-, Zeit- und
Hostfreigrenzen vor Start prüfen und erzwingen; keine solche Integration oder
QRY-023-Messung liegt vor.

Quellen: `SRC-131` (Linux-Systemminimum) und `SRC-132` (Trennung von
Containergrenze und SQL-Server-Speicherlimit). Die Werte 8/20 GiB und 4/3 GiB
sind klar ausgewiesene Projektvorschläge.

## Quellen

- `SRC-122` und `SRC-123`: [Projektquellenregister](../Research/SOURCE_REGISTER.md#graph-tables--eng-begrenzte-sql-graph--und-compatibility-quellen) bindet Graph-Unterstützung ab SQL Server 2017 und die Compatibility-Level-Zuordnung.
- `SRC-126`: derselbe Registerabschnitt bindet die Editionsmatrizen für 2019, 2022 und 2025.
- `SRC-127`: Microsofts [Linux-Servicingübersicht](https://learn.microsoft.com/en-us/troubleshoot/sql/releases/linux/download-and-install-latest-updates-linux) wurde am 12. November erneut geprüft und bestätigt die Pins als aktuelle Linux-Servicingstände.
- `SRC-130`: Microsoft Artifact Registry, die drei oben dokumentierten Manifest-/Konfigurationsdigests und deren `com.microsoft.version`-Labels, read-only abgerufen am 7. November 2026; kein Laufzeitbeleg.
- `SRC-131`: Microsofts [Linux-Installationsanforderungen](https://learn.microsoft.com/en-us/sql/linux/install-upgrade/setup) nennen zwei x64-Kerne mit 2 GHz, 2 GB RAM und 6 GB Speicherplatz als Produktminimum.
- `SRC-132`: Microsofts [Speicherempfehlungen für SQL Server auf Linux](https://learn.microsoft.com/en-us/sql/linux/configure/performance-best-practices-sql-server-memory?view=sql-server-ver17) dokumentieren die getrennten Container- und Enginegrenzen.
