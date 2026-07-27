# Automatisierter Testsystemaufbau mit SQL_Server_Lab

| Merkmal | Wert |
|---|---|
| Arbeitspakete | `LABINT-001` bis `LABINT-005` |
| Status | `PLANNED` |
| Stand | 2026-07-27 |
| Schulungsrepository | `gecompat/SQL_PerformanceSchulung` |
| Lab-Repository | `gecompat/SQL_Server_Lab` |
| geprüfter Lab-Stand | `08fcc9525b9bbc29a5dd9a2ef08de23bd7ef650e` |
| geprüfter Schulungsstand | `091fa8606491d6f5fff2f3cd483d11868ce7d5e7` |
| Zielprovider | Docker und Podman |
| Zielversionen | SQL Server 2019, 2022 und 2025; später kataloggesteuert erweiterbar |

## 1. Zweck

Diese Architektur beschreibt, wie sämtliche ausführbaren Schulungsdemos automatisiert auf durch `SQL_Server_Lab` bereitgestellten SQL-Server-Umgebungen geprüft werden. Das Schulungsrepository bleibt Eigentümer der fachlichen Demo-Phasen, synthetischen Daten, Assertions und Ergebnisverträge. `SQL_Server_Lab` stellt Provider-, Ressourcen-, Port-, Secret-, State- und Infrastruktur-Lifecycle bereit.

Die Integration darf keine Providerimplementierung in dieses Repository kopieren. Docker-, Podman- oder spätere Hyper-V-Befehle werden ausschließlich durch `SQL_Server_Lab` ausgeführt. Änderungen am Lab-Repository sind nicht Bestandteil dieser Welle.

## 2. Festgestellter Ausgangsstand

`SQL_Server_Lab` besitzt bereits eine reale PowerShell-Implementierung für Docker und Podman. `New-SqlServerLab` führt Resource Assessment, State-Anlage, Providerstart, SQL-Readiness, optionale Server- und Datenbankkonfiguration sowie Post-Provision-Skripte aus. Das Cmdlet liefert Run-ID, Scope-ID, Provider, Host und Port zurück. `Remove-SqlServerLab` führt den scopegebundenen Cleanup-Plan aus und entfernt lokale Secrets.

Die aktuelle Root-README des Lab-Repositories bezeichnet den Status noch als reine Planungsgrundlage. Diese Statusaussage ist durch die inzwischen vorhandenen Provider-, Manifest-, Datenbank-, Lifecycle- und Integrationstestimplementierungen überholt und wird für diese Integrationsentscheidung nicht als maßgeblich behandelt.

Das Schulungsrepository besitzt derzeit sechs produktive Demo-Manifeste:

| Demo-ID | Sicherheitsstufe | Sessions | Runtimevalidierung |
|---|---|---:|---|
| `QRY-001` | Grün | 1 | SQL Server 2019, 2022 und 2025 |
| `OPT-002` | Grün | 1 | SQL Server 2019, 2022 und 2025 |
| `CON-004` | Gelb | 3 | SQL Server 2019, 2022 und 2025 |
| `OPT-013` | Gelb | 1 | SQL Server 2019, 2022 und 2025 |
| `OPT-015` | Grün | 1 | SQL Server 2019, 2022 und 2025 |
| `OPT-016` | Grün | 1 | SQL Server 2019, 2022 und 2025 |

Jede dieser Demos verwendet bereits den gemeinsamen Schulungs-Harness mit Preflight, Setup, Baseline, Demonstration, Observation, Mitigation, Comparison und markergeprüftem Cleanup. Die Lab-Integration ersetzt diesen Harness nicht. Sie stellt die Instanz bereit, bindet den Endpunkt und entfernt die Umgebung nach Abschluss.

## 3. Verantwortungsgrenze

### 3.1 SQL_Server_Lab

Das Lab verantwortet im ersten Integrationsstand:

- Auswahl und Prüfung von Docker oder Podman;
- Auflösung von SQL-Server-Version und Containerimage;
- CPU- und RAM-Profil;
- Portvergabe;
- sichere Übergabe des SA-Kennworts an den Container;
- Containerlabels, Run-ID und Scope-ID;
- SQL-Readiness;
- lokalen Run State und Infrastruktur-Cleanup;
- Stop, Start, Restart und Remove der Umgebung.

### 3.2 SQL_PerformanceSchulung

Das Schulungsrepository verantwortet:

- Erkennung ausführbarer Demo-Manifeste;
- Zuordnung zu Versionen, Providern, Ressourcen- und Sicherheitsprofilen;
- Aufruf von `Demos/00_Framework/Tools/run_demo.py`;
- fachliche Assertions und Skip-Verträge;
- Wiederholungszahl;
- unabhängige Prüfung, dass die Demo-Testdatenbank nach jedem Lauf entfernt wurde;
- sanitisierten Testreport;
- Auswahl der zulässigen Testlane;
- projektspezifische Fehlerklassifikation.

## 4. Zielarchitektur der ersten Ausbaustufe

```text
Invoke-PerformanceLabMatrix.ps1
    |
    +-- liest performance-lab-matrix.json
    +-- entdeckt Demos/**/manifest.json
    +-- validiert Katalogvollständigkeit
    +-- erzeugt Provider-/Versions-/Sicherheitsmatrix
    |
    +-- Import-Module <SQL_Server_Lab>/SqlServerLab.psd1
    +-- New-SqlServerLab
    |       +-- Docker oder Podman
    |       +-- SQL Server 2019, 2022 oder 2025
    |       +-- compact, standard oder performance
    |
    +-- pro Demo und Wiederholung
    |       +-- run_demo.py
    |       +-- SQLPERF_SUMMARY auswerten
    |       +-- Demo-Cleanup unabhängig verifizieren
    |
    +-- Remove-SqlServerLab -Force
    +-- Infrastruktur-Cleanup verifizieren
    +-- sanitisierten Matrixreport schreiben
```

Die Ausführung erfolgt standardmäßig sequenziell. Mehrere SQL-Server-Container werden nicht parallel gestartet, solange keine ausdrückliche Ressourcenplanung vorliegt. Dadurch bleiben CPU-, RAM-, TempDB- und Laufzeiteffekte besser interpretierbar.

## 5. Testlanes

### 5.1 `SMOKE`

`SMOKE` prüft einen verfügbaren Provider, SQL Server 2025, alle grünen Demos und eine Wiederholung. Diese Lane dient der schnellen lokalen Funktionsprüfung nach Änderungen an Demo- oder Harnesscode.

### 5.2 `CORE`

`CORE` prüft einen ausgewählten Provider, SQL Server 2019, 2022 und 2025, alle grünen Demos und zwei Wiederholungen. Sie bildet die primäre fachliche Versionsmatrix.

### 5.3 `PROVIDER_PARITY`

`PROVIDER_PARITY` prüft Docker und Podman auf SQL Server 2025. Grüne Demos laufen automatisch. Gelbe Demos benötigen eine ausdrückliche Isolationsbestätigung. Zweck ist der Nachweis, dass Providerunterschiede den fachlichen Demo-Vertrag nicht verändern.

### 5.4 `FULL_CONTAINER_MATRIX`

`FULL_CONTAINER_MATRIX` umfasst Docker und Podman, SQL Server 2019, 2022 und 2025 sowie alle freigegebenen grünen und gelben Demos. Bei sechs aktuellen Demos, zwei Wiederholungen, drei Versionen und zwei Providern entstehen 72 vollständige Demoläufe. Die Lane wird daher nicht als Standard-Schnelltest verwendet.

### 5.5 `RED_DISPOSABLE`

Rote Demos werden niemals durch `FULL_CONTAINER_MATRIX` eingeschlossen. Sie benötigen eine eigene Lane, eine dedizierte Wegwerfumgebung, explizite High-Impact-Bestätigung, ein Laufzeitbudget, einen externen Kill-Switch und eine separate Recovery-Prüfung. `RES-003` bleibt bis zur Erfüllung dieser Bedingungen ausgeschlossen.

## 6. Umgebungswiederverwendung

Eine einzelne Provider-/Versionsumgebung darf mehrere grüne Demos sequenziell ausführen, wenn jede Demo:

- ausschließlich eine eigene markergebundene Testdatenbank verändert;
- keine instanzweite Konfiguration verändert;
- keine globalen Caches leert;
- keine persistente XE-Session, Agent-Definition oder Serverrolle hinterlässt;
- ihr Cleanup vollständig nachweist.

Gelbe Demos werden in einer getrennten Umgebungslane ausgeführt. Demos mit instanzweiter Konfiguration, Ressourcenlimitierung, Fault Injection oder roten Sicherheitsmerkmalen erhalten grundsätzlich eine frische dedizierte Umgebung.

Der Katalog führt hierfür das Feld `environmentIsolation` mit den Werten:

- `SHARED_PROVIDER_VERSION`;
- `FRESH_INSTANCE`;
- `DEDICATED_DISPOSABLE`.

## 7. Discovery- und Katalogvertrag

Alle produktiven Manifeste unter `Demos/**/manifest.json` werden automatisch entdeckt. Inhalte unter `Demos/00_Framework/Examples` sind keine produktiven Demos und bleiben ausgeschlossen.

Jedes entdeckte produktive Manifest muss genau einen Eintrag in `Tests/Lab/performance-lab-matrix.json` besitzen. Ein neues Manifest ohne Katalogeintrag ist ein statischer Fehler. Damit kann keine neue Demo unbemerkt außerhalb der automatisierten Matrix entstehen.

Der Katalog wiederholt nicht den Phasenvertrag des Demo-Manifests. Er ergänzt ausschließlich infrastrukturelle und orchestrierende Felder:

- zulässige Provider;
- Zielversionen;
- Ressourcenprofil;
- Sicherheitsstufe;
- Sessions;
- Wiederholungen;
- Environment-Isolation;
- erforderliche Lab- und SQL-Capabilities;
- erwartete Ergebnisarten `PASS`, `WARN` oder begründeter `SKIP`;
- manuelle oder rote Freigabebedingungen.

Sicherheitsstufe und Demo-ID müssen mit dem jeweiligen Demo-Manifest übereinstimmen.

## 8. Ausführungsalgorithmus

Der spätere Runner verarbeitet eine Lane in folgender Reihenfolge:

1. Projektroot, Lab-Repository und Modulversion prüfen.
2. PowerShell 7.2+, Python und Microsoft `sqlcmd` prüfen.
3. Katalog und alle produktiven Demo-Manifeste validieren.
4. Verfügbare Provider feststellen.
5. Matrixzellen nach Lane, Provider, Version, Safety und Capability auflösen.
6. Ein kurzlebiges Lab-Manifest ohne Secrets erzeugen.
7. `New-SqlServerLab` mit `SecureString`, explizitem `StateRoot` und gewähltem Profil aufrufen.
8. Host und Port ausschließlich aus dem zurückgegebenen Lab-Objekt übernehmen.
9. Das Kennwort nur im Prozesskontext als `SQLCMDPASSWORD` bereitstellen.
10. Für jede Demo den vorhandenen Python-Harness aufrufen.
11. Nach jedem Lauf die Abwesenheit der erwarteten Demo-Datenbank über `master` prüfen.
12. Bei Demo-Fehlern keine weiteren regulären Demos derselben Matrixzelle starten.
13. Im `finally`-Pfad `Remove-SqlServerLab -RunId ... -Force` ausführen.
14. Container- und State-Cleanup prüfen.
15. Einen sanitisierten Report ohne Kennwort, reale Hostpfade, Plan XML oder vollständige SQL-Ausgaben erzeugen.

## 9. Ergebnis- und Fehlervertrag

Eine Matrixzelle liefert genau einen der folgenden Statuswerte:

- `PASS` – alle erforderlichen Demos und Cleanup-Prüfungen bestanden;
- `WARN` – ausschließlich optionale Evidenz wurde kontrolliert übersprungen;
- `SKIP_PROVIDER_UNAVAILABLE`;
- `SKIP_VERSION_UNAVAILABLE`;
- `SKIP_CAPABILITY_UNAVAILABLE`;
- `SKIP_SAFETY_CONFIRMATION_REQUIRED`;
- `FAIL_LAB_PROVISION`;
- `FAIL_DEMO_CONTRACT`;
- `FAIL_DEMO_EXECUTION`;
- `FAIL_DEMO_CLEANUP`;
- `FAIL_LAB_CLEANUP`;
- `RECOVERY_REQUIRED`.

Ein Demo-`SKIP` ist nur erfolgreich, wenn der Demo-Vertrag diesen Code für die konkrete Version oder Capability zulässt. Ein unerwarteter Skip wird als Fehler behandelt.

## 10. Datenschutz und Secrets

- Das SA-Kennwort wird nicht in einem Manifest, Report oder Kommandozeilenargument des Schulungsrunners gespeichert.
- Lokaler Lab-State liegt außerhalb des Repositorys oder in einem ignorierten Pfad.
- Runtime-Reports enthalten nur Demo-ID, Provider, Version, Engine-Build, Laufnummer, Statuscode, Dauerklasse und normalisierte Assertions.
- Plan XML, vollständige Querytexte, Containerlogs und lokale Pfade werden nicht automatisch exportiert.
- Diagnoseartefakte bleiben lokal und benötigen vor einer Weitergabe die bestehende Privacy-Prüfung.

## 11. Vorläufig ohne Änderung am Lab-Repository umsetzbar

Die erste lauffähige Integration benötigt keine Änderung an `SQL_Server_Lab`. Folgende bestehende Schnittstellen reichen aus:

- `Import-Module SqlServerLab.psd1`;
- `Test-LabResources`;
- `New-SqlServerLab` mit Docker oder Podman;
- Rückgabe von Run-ID, Host, Port und Provider;
- `Get-SqlServerLab`;
- `Remove-SqlServerLab -Force`;
- bestehender Schulungs-Harness für Demoablauf und fachlichen Cleanup.

Der Runner bleibt deshalb zunächst ein Project Adapter im Schulungsrepository und verwendet das Lab ausschließlich als Infrastrukturprovider.

## 12. Erforderliche spätere Erweiterungen in SQL_Server_Lab

Für die endgültige, im Lab-Architekturvertrag vorgesehene Package-Ausführung sind zusätzliche Lab-Funktionen erforderlich. Diese Welle implementiert sie ausdrücklich nicht.

### 12.1 Project Adapter und Lab Package Engine

Der dokumentierte `Project Adapter` mit Package-Katalog, `SqlPurpose`, Deployment Units, DataSets, Workflows, Probes, Assertions und Project Cleanup ist derzeit Architekturentwurf. Das implementierte Lab-Manifest beschreibt hauptsächlich Instanzen, Datenbanken, Serverkonfiguration und `postProvision`. Für die spätere native Ausführung der Schulungspakete muss der Project-Adapter-/Package-Vertrag implementiert werden.

### 12.2 Öffentliche Recovery- und Cleanup-Commands

`Invoke-LabCleanup` und `Invoke-LabRecovery` sind im Modulmanifest exportiert, in der öffentlichen Modulübersicht jedoch als nicht implementiert ausgewiesen. Für wiederaufnehmbare automatisierte Läufe müssen beide Commands implementiert und mit stabilen Rückgabeobjekten versehen werden.

### 12.3 Providerneutraler Orphan-Cleanup

`Remove-SqlServerLab` führt nach dem Cleanup-Plan ein zusätzliches Docker-Orphan-Sicherheitsnetz aus. Ein entsprechender Podman-Orphan-Pfad ist im öffentlichen Remove-Cmdlet nicht vorhanden. Für belastbare Providerparität muss die Orphan-Prüfung anhand des im Run State gespeicherten Providers providerneutral erfolgen.

### 12.4 Maschinenlesbarer Capability- und Build-Nachweis

Die spätere Package Engine benötigt einen öffentlichen, providerneutralen Capability-Record mit mindestens:

- Provider und Runtimeversion;
- angeforderter Bildreferenz;
- tatsächlich verwendeter Image-ID beziehungsweise Digest;
- SQL `ProductVersion`, `ProductMajorVersion`, Edition und Plattform;
- wirksamem Compatibility Level;
- CPU-, RAM- und Storageprofil;
- verfügbaren Capabilities wie Query Store, XE, Agent, CLR, Parallelität und Multi-Session.

Die aktuellen Rückgabeobjekte enthalten Host, Port, Version-ID und Imagebezug, aber keinen vollständigen reproduzierbaren Build- und Capability-Nachweis.

### 12.5 Ressourcen-Override mit sichtbarem Defizit

Die Projektvorgabe erlaubt eine bewusste Übersteuerung vorhergesagter Unterversorgung, wobei das Defizit sichtbar bleiben muss. Der aktuelle öffentliche Aufruf bietet `-SkipAssessment`. Für den endgültigen Vertrag wird stattdessen ein explizites `-AllowResourceDeficit` mit persistiertem Assessment und Bestätigung benötigt. Ein vollständiges Überspringen der Prüfung erfüllt diese Anforderung nicht.

### 12.6 Strukturierter nichtinteraktiver Ausgabemodus

Für eine spätere sprach- und prozessunabhängige Control Plane wird ein stabiler JSON-/Objektmodus mit definierten Exitcodes, Operations und Events benötigt. Die aktuelle PowerShell-Nutzung ist für den ersten Runner ausreichend, die im Architekturvertrag vorgesehene generische Control Plane ist jedoch noch nicht implementiert.

## 13. Nicht erforderliche Lab-Erweiterungen für die erste Runner-Version

Nicht erforderlich sind:

- Kopieren der Schulungsdemos in das Lab-Repository;
- ein eigener Docker- oder Podman-Compose-Stack im Schulungsrepository;
- Post-Provision-Unterstützung für alle Demo-Phasen;
- Persistieren von Demo-Plan XML im Lab-State;
- parallele Provisionierung aller Versionen;
- Hyper-V für die derzeit grünen und gelben Containerdemos.

## 14. Arbeitspakete und Abhängigkeiten

| ID | Priorität | Arbeit | Voraussetzung | Abschlusskriterium |
|---|---:|---|---|---|
| `LABINT-001` | P0 | Architektur, Testkatalog und statische Vollständigkeitsprüfung | vorhandene Demo-Manifeste und Lab-Lifecycle | jedes produktive Manifest ist katalogisiert; Lab-Grenzen sind dokumentiert |
| `LABINT-002` | P0 | lokalen PowerShell-Runner für `SMOKE` und `CORE` implementieren | `LABINT-001` | Docker oder Podman kann eine Instanz provisionieren, alle grünen Demos ausführen und vollständig entfernen |
| `LABINT-003` | P1 | `PROVIDER_PARITY` für Docker und Podman validieren | `LABINT-002` | identische fachliche Verträge auf beiden Providern oder begründete Capability-Skips |
| `LABINT-004` | P1 | gelbe Lane und `FULL_CONTAINER_MATRIX` implementieren | `LABINT-002`, Safety-Gates | gelbe Demos laufen nur mit Bestätigung und getrenntem Ressourcenprofil |
| `LABINT-005` | P2 | auf native Lab-Package-Ausführung migrieren | erforderliche Lab-Erweiterungen 12.1 bis 12.6 | Schulungsrunner enthält keine eigene Infrastrukturorchestrierung mehr |

## 15. Reihenfolge der nächsten Umsetzung

Die nächste sinnvolle Umsetzung ist `LABINT-002` mit ausschließlich grünen Demos. Der Runner verwendet zunächst einen ausgewählten Provider und die drei SQL-Server-Versionen. Erst nach erfolgreicher Cleanup- und Providerbindung werden Podman-Parität und gelbe Demos aktiviert.

Parallel kann `ADV-008` weitere fachliche Demos implementieren. Der statische Katalogvalidator verhindert, dass neue Demo-Manifeste ohne Testmatrixzuordnung integriert werden.
