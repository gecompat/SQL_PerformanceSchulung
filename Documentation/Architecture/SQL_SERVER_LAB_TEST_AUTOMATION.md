# Qualitätssicherung für Schulungsszenarien mit SQL_Server_Lab

| Merkmal | Wert |
|---|---|
| Arbeitspakete | `LABINT-001` bis `LABINT-004` |
| Status | `VALIDATED`, nachgeordnet zu `LABSCN-001` |
| Stand | 2026-07-27 |
| Primärer Szenariovertrag | [`SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md`](./SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md) |
| Schulungsrepository | `gecompat/SQL_PerformanceSchulung` |
| Provisionierungsframework | `gecompat/SQL_Server_Lab` |

## 1. Einordnung

Der primäre Zweck der Integration ist die Bereitstellung interaktiv nutzbarer Schulungsszenarien. Der Benutzer soll ein einzelnes Beispiel auswählen, eine vollständig vorbereitete Umgebung erhalten, das Verhalten selbst untersuchen, Änderungen ausprobieren und den Ausgangszustand wiederherstellen können.

Die in diesem Dokument beschriebene Testautomation ist ausschließlich ein Qualitätssicherungsinstrument. Sie prüft, ob Aufbau, Vorbereitung, Kernbeobachtung, Reset und Abbau reproduzierbar funktionieren. Sie ersetzt weder die Benutzerübergabe noch die interaktive Schritt-für-Schritt-Anleitung.

## 2. Verantwortungsgrenze

`SQL_Server_Lab` wird zur Erzeugung und Verwaltung der angeforderten Docker-, Podman-, Hyper-V- oder gemischten Umgebung verwendet.

`SQL_PerformanceSchulung` verantwortet:

- Szenarioauswahl;
- technische Anforderungen des Beispiels;
- Setup und synthetische Daten;
- Demo-Harness und Assertions;
- Benutzeranleitung und Beobachtungsaufträge;
- fachlichen Reset;
- Testzusammenfassung.

Das Lab-Repository muss Lernziele, Demo-Phasen oder fachliche Assertions nicht kennen.

## 3. Automatisierte Prüfmodi

### `SMOKE`

Prüft einen kleinen, geeigneten Szenarioausschnitt auf einem verfügbaren Provider. Ziel ist der Nachweis, dass Umgebung, Vorbereitung, Reset und Abbau grundsätzlich funktionieren.

### `CORE`

Prüft die freigegebenen grünen Szenarien auf SQL Server 2019, 2022 und 2025. Der Modus dient der Versionskompatibilität und nicht der interaktiven Durchführung.

### `PROVIDER_PARITY`

Prüft, ob dasselbe fachliche Szenario über Docker und Podman reproduzierbar bereitgestellt werden kann. Hyper-V wird nur für Szenarien geprüft, die diese Plattform fachlich benötigen.

### `FULL_CONTAINER_MATRIX`

Prüft alle freigegebenen Container-Szenarien über die vorgesehenen Versionen und Provider. Diese Matrix ist ein technischer Abnahmepfad und kein Benutzerworkflow.

## 4. Discovery- und Testkatalog

Produktive Demo-Manifeste unter `Demos/**/manifest.json` werden automatisch entdeckt. Der Katalog `Tests/Lab/performance-lab-matrix.json` ordnet sie den automatisierten Qualitätsprüfungen zu.

Dieser Katalog ist nicht der spätere Benutzerszenariokatalog. Interaktive Szenariodefinitionen werden unter `LABSCN-002` separat modelliert und enthalten zusätzlich Topologie, Vorbereitung, Übergabe, Benutzeraktionen und Reset.

## 5. Lebenszyklus der Qualitätssicherung

Eine automatisierte Prüfung darf eine kurzlebige Umgebung verwenden und sie nach dem Test entfernen. Für die interaktive Nutzung gilt dagegen:

```text
Provisionieren
-> Vorbereiten
-> READY_FOR_USER
-> Benutzer arbeitet mit dem Szenario
-> Reset oder ausdrücklicher Abbau
```

Der automatische Abbau eines Testlaufs darf daher nicht als Zielverhalten des interaktiven Szenarios dokumentiert werden.

## 6. Aktuelle Lab-Anforderungen

Für die bestehende Container-Testautomation reichen grundsätzlich die öffentlichen Commands von `SQL_Server_Lab` zur Erstellung, Statusabfrage und Entfernung einer Umgebung.

Für interaktive Szenarien können abhängig vom konkreten Beispiel weitere Fähigkeiten erforderlich sein, beispielsweise:

- Hyper-V-VMs;
- mehrere Instanzen;
- gemischte Provider;
- getrennte Storage- oder Netzwerkprofile;
- zusätzliche Workload-Clients;
- persistierbarer Szenariostatus für Start, Reset und Remove.

Eine fehlende Fähigkeit wird erst anhand eines konkreten Szenarios als Anforderung an `SQL_Server_Lab` formuliert. Änderungen im Lab-Repository erfolgen nicht ohne ausdrückliche Freigabe.

## 7. Arbeitspakete

| ID | Arbeit | Einordnung |
|---|---|---|
| `LABINT-001` | Testkatalog und statische Vollständigkeitsprüfung | abgeschlossen |
| `LABINT-002` | automatisierten Smoke-/Core-Test für Aufbau und Abbau implementieren | Qualitätssicherung für `LABSCN-003` |
| `LABINT-003` | Docker-/Podman-Parität prüfen | Qualitätssicherung geeigneter Container-Szenarien |
| `LABINT-004` | gelbe und vollständige Container-Matrix aktivieren | nach Safety- und Szenariofreigabe |

## 8. Nächster Schritt

Der nächste fachliche Schritt ist `LABSCN-002`: vorhandene und geplante Beispiele klassifizieren und den interaktiven Szenariovertrag pro Beispiel definieren. Die Testautomation wird danach so erweitert, dass sie die technische Reproduzierbarkeit dieser Szenarien prüft.
