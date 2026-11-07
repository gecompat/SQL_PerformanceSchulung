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

Die Microsoft-Produktübersicht weist zum 7. November 2026 die jüngsten
Servicingbuilds aus. Diese sind nicht automatisch in den gleichnamigen
Linux-Container-CU-Tags enthalten. Für die im QRY-023-Entwurf verwendeten
MCR-Tags wurde das Single-Platform-Manifest samt Konfiguration read-only
abgefragt. Die Konfiguration trägt das Label `com.microsoft.version`; kein
Image wurde heruntergeladen oder gestartet.

| Projektprofil / Linux-Image | Compatibility Level | Produktservicing laut Microsoft | Image-Label `com.microsoft.version` |
|---|---:|---|---:|
| SQL Server 2019 `2019-CU32-ubuntu-20.04` | 150 | CU32 + GDR `15.0.4500.2` | `15.0.4430.1` |
| SQL Server 2022 `2022-CU27-ubuntu-22.04` | 160 | CU27 + GDR `16.0.4305.5` | `16.0.4295.3` |
| SQL Server 2025 `2025-CU10-ubuntu-22.04` | 170 | CU10 `17.0.5035.5` | `17.0.5035.5` |

Die geprüften AMD64-Manifest- und Konfigurationsdigests lauten:

| Profil | Manifestdigest | Konfigurationsdigest |
|---|---|---|
| 2019 | `sha256:7a879e9af3557e81a3b3ad14acd071e3638788387f394d27a9d3404b28e954ce` | `sha256:b6d65c67219f3a0bd86870b0ef485928305923e8c3c83964170c476b5eef165e` |
| 2022 | `sha256:4402d880dd4c34bfa7d8705e56a86cd6c88da80a1f6bbbe741f999e76264a090` | `sha256:5b0916c7af8ca97ce9390be7e1182862d6fa90bff9f44f035dbe1626df140637` |
| 2025 | `sha256:6972fb831759433def6a34e107fa32a85230bff5af8014c6263fe4633ea9cc0f` | `sha256:e6b27c1b6b7c1faa799fc4cd831c442bb36a8f7a7f214e780652e8cc09a26625` |

Für die drei vorhandenen Images sind deshalb `15.0.4430.1`, `16.0.4295.3`
und `17.0.5035.5` die passenden Design-/Qualifikationspins. Die 2019- und
2022-CU-Tags enthalten jeweils den CU-Build ohne den separat veröffentlichten
GDR-Patchstand. Wer stattdessen die neueren GDR-Builds qualifizieren will,
benötigt ein dazu passendes Image oder eine kontrollierte Aktualisierung; beides
ist hier nicht vorbereitet. Die Konfiguration beschreibt nicht den tatsächlich
gestarteten Engineprozess: ein späterer Lauf muss Image-Manifestdigest und
`SERVERPROPERTY('ProductVersion')` binden.

Diese Builds sind zeitgebundene, reproduzierbare **Design-/Qualifikationspins**,
keine Mindestbuilds für Graph Tables. Die Graph-Dokumentation weist die Funktion ab
SQL Server 2017 aus; sie setzt für diese Graph-DDL-/`MATCH`-Funktionen keine
bestimmte CU-Stufe voraus. Die vorgeschlagenen Builds wählen den zum Abrufdatum
verfügbaren offiziellen Imagebuild, nicht den neuesten Produktservicingstand
und keinen empirisch getesteten Container.

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
nicht katalogisiert und ungefahren. Unabhängige Methodenfreigabe, formale
T-SQL-/Harness-Abnahme, Ressourcenprofil und konkrete Ausführungsautorisierung
bleiben offen.

## Quellen

- `SRC-126`: [Projektquellenregister](../Research/SOURCE_REGISTER.md#graph-tables--eng-begrenzte-sql-graph--und-compatibility-quellen) bindet die Editionsmatrizen für 2019, 2022 und 2025.
- `SRC-127`: Microsofts [Linux-Servicingübersicht](https://learn.microsoft.com/en-us/troubleshoot/sql/releases/linux/download-and-install-latest-updates-linux) bindet den Produktservicingstand am 7. November 2026; dieser stimmt für 2019/2022 nicht mit den geprüften CU-Container-Tags überein.
- `SRC-130`: Microsoft Artifact Registry, die drei oben dokumentierten Manifest-/Konfigurationsdigests und deren `com.microsoft.version`-Labels, read-only abgerufen am 7. November 2026; kein Laufzeitbeleg.
- `SRC-122` und `SRC-123`: derselbe Quellenregisterabschnitt bindet Graph-Unterstützung ab SQL Server 2017 und die Compatibility-Level-Zuordnung.
