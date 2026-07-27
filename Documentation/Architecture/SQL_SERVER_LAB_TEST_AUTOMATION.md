# Automatisierter Testsystemaufbau mit SQL_Server_Lab

| Merkmal | Wert |
|---|---|
| Arbeitspakete | `LABINT-001` bis `LABINT-004` |
| Status | `VALIDATED` |
| Stand | 2026-07-27 |
| Schulungsrepository | `gecompat/SQL_PerformanceSchulung` |
| Lab-Repository | `gecompat/SQL_Server_Lab` |
| geprüfter Lab-Stand | `08fcc9525b9bbc29a5dd9a2ef08de23bd7ef650e` |
| geprüfter Schulungsstand | `37bc7d6896603eb614dfdeb41f8a77ff947abe68` |
| Zielprovider | Docker und Podman |
| Zielversionen | SQL Server 2019, 2022 und 2025 |

## 1. Zweck

`SQL_Server_Lab` soll für dieses Projekt die benötigten SQL-Server-Testumgebungen bereitstellen. `SQL_PerformanceSchulung` soll anschließend alle vorhandenen und künftig entstehenden Demo-Manifeste auf diesen Umgebungen ausführen und auswerten.

Die Erwartung ist bewusst einfach:

```text
SQL_Server_Lab
    -> SQL-Server-Umgebung erstellen
    -> Verbindungsdaten zurückgeben

SQL_PerformanceSchulung
    -> Demos auswählen
    -> Demos ausführen und prüfen
    -> Demo-Cleanup prüfen

SQL_Server_Lab
    -> Umgebung entfernen
```

Das Lab-Repository muss die Schulungsdemos, deren Lernziele, Phasen oder fachliche Assertions nicht kennen.

## 2. Verbindliche Verantwortungsgrenze

### 2.1 Erwartung an SQL_Server_Lab

Für die Testautomation werden nur folgende Fähigkeiten erwartet:

- Docker- oder Podman-Umgebung für eine angeforderte SQL-Server-Version erstellen;
- ein geeignetes CPU-/RAM-Profil anwenden;
- SQL-Readiness prüfen;
- ein PowerShell-Objekt mit mindestens Run-ID, Provider, Host und Port zurückgeben;
- die zugehörige Umgebung anhand der Run-ID sicher entfernen;
- Fehler beim Aufbau oder Abbau als PowerShell-Fehler beziehungsweise im Rückgabeobjekt erkennbar machen.

Die vorhandenen Commands `New-SqlServerLab`, `Get-SqlServerLab` und `Remove-SqlServerLab` bilden diese Erwartung grundsätzlich bereits ab.

### 2.2 Verantwortung von SQL_PerformanceSchulung

Dieses Repository verantwortet vollständig:

- Discovery aller produktiven Dateien `Demos/**/manifest.json`;
- Zuordnung zu SQL-Server-Versionen, Providern, Ressourcenprofilen und Sicherheitsstufen;
- Aufruf des bestehenden Harness `Demos/00_Framework/Tools/run_demo.py`;
- Demo-Phasen, synthetische Daten und fachliche Assertions;
- erlaubte `PASS`-, `WARN`- und `SKIP`-Ergebnisse;
- Wiederholungen und Matrixbildung;
- Prüfung, dass die jeweilige Demo-Testdatenbank entfernt wurde;
- zusammengefasste Testausgabe und Fehlerklassifikation.

## 3. Nicht erwartete Funktionalität von SQL_Server_Lab

Für die Schulungsautomation ist **keine Project-Adapter- oder Lab-Package-Engine erforderlich**. Der in `SQL_Server_Lab` dokumentierte langfristige Architekturentwurf darf nicht als Voraussetzung dieses Projekts interpretiert werden.

Ebenso ist **keine generische JSON-/Event-Schnittstelle erforderlich**. Der Runner wird in PowerShell implementiert und kann die vorhandenen PowerShell-Rückgabeobjekte und Fehler direkt verarbeiten. Der JSON-Katalog in `Tests/Lab` gehört ausschließlich zur schulungsinternen Demo- und Testmatrix; daraus entsteht keine Ausgabeforderung an `SQL_Server_Lab`.

Für die erste und dauerhaft zulässige Integration sind außerdem nicht erforderlich:

- Migration der Demo-Manifeste in das Lab-Repository;
- Kenntnis der Demo-Phasen durch das Lab;
- zentrale Ausführung der fachlichen Assertions im Lab;
- ein allgemeiner Operations- oder Event-Bus;
- ein eigener Package-Katalog im Lab für dieses Projekt;
- ein Image-Digest als Voraussetzung jedes lokalen Testlaufs;
- ein besonderer JSON-Exitcode-Vertrag.

Solche Funktionen können für andere Ziele des Lab-Repositories sinnvoll sein, sind aber keine Anforderung von `SQL_PerformanceSchulung`.

## 4. Ausführungsmodell

Der geplante Runner `Tests/Lab/Invoke-PerformanceLabMatrix.ps1` führt pro Provider-/Versionszelle folgenden Ablauf aus:

1. `SQL_Server_Lab/SqlServerLab.psd1` importieren.
2. PowerShell, Python und Microsoft `sqlcmd` prüfen.
3. Katalog und Demo-Manifeste validieren.
4. `New-SqlServerLab` mit Version, Provider, Profil und einem zur Laufzeit erzeugten `SecureString` aufrufen.
5. Host und Port aus dem zurückgegebenen Lab-Objekt übernehmen.
6. Für jede ausgewählte Demo `run_demo.py` mit dem gebundenen SQL-Endpunkt aufrufen.
7. Nach jedem Demolauf die Abwesenheit der erwarteten Demo-Datenbank prüfen.
8. Im `finally`-Pfad `Remove-SqlServerLab -RunId ... -Force` aufrufen.
9. Prüfen, dass die Lab-Ressource nicht mehr vorhanden ist.

Der Runner verwendet keine eigenen Docker- oder Podman-Befehle zum Erstellen der Umgebung. Die Infrastruktur bleibt vollständig Eigentum von `SQL_Server_Lab`.

## 5. Testlanes

### 5.1 `SMOKE`

Ein verfügbarer Provider, SQL Server 2025, alle grünen Demos, eine Wiederholung.

### 5.2 `CORE`

Ein ausgewählter Provider, SQL Server 2019, 2022 und 2025, alle grünen Demos, zwei Wiederholungen.

### 5.3 `PROVIDER_PARITY`

Docker und Podman auf SQL Server 2025. Zunächst grüne Demos; gelbe Demos nur nach ausdrücklicher Isolationsbestätigung.

### 5.4 `FULL_CONTAINER_MATRIX`

Docker und Podman, SQL Server 2019, 2022 und 2025 sowie alle freigegebenen grünen und gelben Demos. Beim aktuellen Bestand entstehen 72 vollständige Demoläufe.

### 5.5 `RED_DISPOSABLE`

Rote Demos werden ausschließlich separat und nach dem jeweiligen Demo-Sicherheitsvertrag ausgeführt. Sie sind kein impliziter Bestandteil der normalen Container-Matrix.

## 6. Discovery- und Katalogvertrag

Alle produktiven Demo-Manifeste werden automatisch entdeckt. Inhalte unter `Demos/00_Framework/` bleiben ausgeschlossen.

Jedes entdeckte produktive Manifest muss genau einmal in `Tests/Lab/performance-lab-matrix.json` vorkommen. Der Katalog ergänzt nur projektseitige Informationen:

- Provider;
- SQL-Server-Versionen;
- Ressourcenprofil;
- Sicherheitsstufe;
- Sessionzahl;
- Wiederholungen;
- notwendige Isolation;
- erwartete Ergebnisarten.

Der Katalog stellt keine Erweiterung des Lab-Manifestschemas dar und wird nicht von `SQL_Server_Lab` verarbeitet.

## 7. Aktuell erforderliche Änderungen in SQL_Server_Lab

Für `LABINT-002` ist nach dem gegenwärtigen Stand **keine zusätzliche Lab-Funktion erforderlich**.

Der erste reale Runner muss jedoch zwei Dinge praktisch verifizieren:

1. Docker-Aufbau und -Abbau funktionieren vollständig über `New-SqlServerLab` und `Remove-SqlServerLab`.
2. Podman-Aufbau und -Abbau funktionieren vollständig über dieselben öffentlichen Commands.

Eine konkrete Erweiterung im Lab-Repository wird erst dann verlangt, wenn ein realer Lauf eine fehlende oder fehlerhafte Funktion nachweist.

### Beobachtung zum Providerneutralen Orphan-Cleanup

`Remove-SqlServerLab` führt nach dem allgemeinen Cleanup-Plan zusätzlich eine Docker-spezifische Suche nach verbliebenen Containern aus. Für Podman ist in diesem zusätzlichen Sicherheitsnetz derzeit kein entsprechender Pfad sichtbar. Der normale Cleanup-Plan enthält bereits providerbezogene `docker rm`- beziehungsweise `podman rm`-Compensation. Daher ist dies zunächst eine zu prüfende Robustheitslücke und kein nachgewiesener Blocker.

Erst wenn ein Podman-Test einen verbliebenen Container oder einen unvollständigen Cleanup nachweist, muss im Lab-Repository ein **providerneutraler Orphan-Cleanup** ergänzt werden. Diese Änderung wird vorher benannt und nicht ohne ausdrückliche Freigabe umgesetzt.

## 8. Umgang mit Testergebnissen

Eine strukturierte interne Testausgabe ist sinnvoll, damit der Runner mehrere Demos zusammenfassen kann. Diese Struktur gehört jedoch zum Schulungsrunner und nicht zur geforderten öffentlichen Schnittstelle von `SQL_Server_Lab`.

Ausreichend sind beispielsweise PowerShell-Objekte mit:

- Provider;
- SQL-Server-Version;
- Demo-ID;
- Wiederholung;
- Ergebnis `PASS`, `WARN`, `SKIP` oder `FAIL`;
- Fehlerkategorie;
- Cleanup-Ergebnis.

Ein JSON-Export kann optional aus diesen Objekten erzeugt werden. Er ist keine Voraussetzung des Lab-Repositories.

## 9. Datenschutz und Secrets

- Das SA-Kennwort wird ausschließlich zur Laufzeit gehalten.
- Es wird weder im Testkatalog noch in Reports persistiert.
- Lokaler Lab-State verbleibt außerhalb versionierter Projektpfade.
- Reports enthalten keine Plan-XML-Dokumente, vollständigen Querytexte oder Containerlogs.
- Reale Hostnamen und lokale Pfade werden nicht in Repository-Artefakte übernommen.

## 10. Arbeitspakete und Abhängigkeiten

| ID | Priorität | Arbeit | Voraussetzung | Abschlusskriterium |
|---|---:|---|---|---|
| `LABINT-001` | P0 | Verantwortungsgrenze, Testkatalog und statische Vollständigkeitsprüfung | vorhandene Demo-Manifeste und öffentliche Lab-Commands | jede produktive Demo ist katalogisiert; keine überzogene Lab-Anforderung bleibt dokumentiert |
| `LABINT-002` | P0 | PowerShell-Runner für `SMOKE` und `CORE` implementieren | `LABINT-001` | ein Provider kann die grünen Demos auf 2019/2022/2025 ausführen und vollständig abbauen |
| `LABINT-003` | P1 | Docker-/Podman-Parität praktisch prüfen | `LABINT-002` | beide Provider funktionieren oder eine konkrete Lab-Lücke ist reproduzierbar benannt |
| `LABINT-004` | P1 | gelbe Lane und vollständige Container-Matrix aktivieren | `LABINT-002`, Safety-Gates | alle freigegebenen grünen und gelben Demos werden gemäß Katalog ausgeführt |

## 11. Nächster Schritt

`LABINT-002` implementiert den einfachen PowerShell-Runner gegen die bereits vorhandenen öffentlichen Commands von `SQL_Server_Lab`. Es wird keine zusätzliche Lab-Architektur vorausgesetzt. Falls ein realer Lauf eine fehlende Lab-Funktion zeigt, wird diese konkrete Funktion mit reproduzierbarem Befund benannt, bevor irgendeine Änderung im Lab-Repository erfolgt.
