# Interaktive Schulungsszenarien mit SQL_Server_Lab

| Merkmal | Wert |
|---|---|
| Arbeitspaket | `LABSCN-001` |
| Status | `DECIDED` |
| Stand | 2026-07-27 |
| Schulungsrepository | `gecompat/SQL_PerformanceSchulung` |
| Provisionierungsframework | `gecompat/SQL_Server_Lab` |
| Zielplattformen | Docker, Podman, Hyper-V und gemischte Topologien |

## 1. Ziel

Die Beispiele der Schulung sollen nicht nur automatisiert geprüft werden. Für jedes geeignete Beispiel soll eine technisch vorbereitete Laborumgebung erzeugt werden können, in der der Benutzer den beschriebenen Effekt selbst ausführt, beobachtet, verändert, zurücksetzt und erneut ausführt.

`SQL_Server_Lab` ist das verbindliche Framework für Aufbau, Konfiguration und Lifecycle dieser Umgebungen. `SQL_PerformanceSchulung` definiert die fachlichen Anforderungen des jeweiligen Beispiels und stellt die dafür erforderlichen T-SQL-Skripte, synthetischen Daten, Beobachtungsabfragen und Benutzeranleitungen bereit.

Der primäre Ablauf lautet:

```text
Beispiel auswählen
    -> technische Anforderungen auflösen
    -> geeignete Topologie bestimmen
    -> Umgebung mit SQL_Server_Lab erstellen
    -> SQL Server und Zusatzkomponenten konfigurieren
    -> Beispieldaten und Ausgangszustand vorbereiten
    -> betriebsbereite Umgebung an den Benutzer übergeben
    -> Benutzer führt das Beispiel interaktiv durch
    -> Umgebung auf Ausgangszustand zurücksetzen oder vollständig entfernen
```

## 2. Primärer Zweck und Abgrenzung

Der primäre Zweck ist eine interaktive Lern- und Experimentierumgebung. Ein automatischer Runtime-Test dient zusätzlich der Qualitätssicherung, ist aber nicht das Hauptprodukt der Integration.

Die Umgebung darf nach erfolgreicher Vorbereitung nicht automatisch entfernt werden. Sie verbleibt im Status `READY_FOR_USER`, bis der Benutzer ausdrücklich einen Reset oder den vollständigen Abbau anfordert.

Nicht Ziel ist ein allgemeines Infrastruktur-Labor ohne konkreten Bezug zu einem Schulungsbeispiel. Jede bereitgestellte Komponente muss aus dem Lernziel und dem technischen Reproduktionsbedarf eines konkreten Beispiels ableitbar sein.

## 3. Verantwortungsgrenze

### 3.1 SQL_PerformanceSchulung

Dieses Repository verantwortet je Beispiel:

- Lernziel und fachliche Kernaussage;
- zu reproduzierende Ausgangssituation;
- benötigte SQL-Server-Versionen und Compatibility Levels;
- erforderliche Instanzen, Datenbanken, Sessions und Zusatzkomponenten;
- Mindestanforderungen an CPU, RAM, Storage und Netzwerk;
- synthetische Daten und Datenverteilungen;
- Setup- und Vorbereitungsskripte;
- interaktive Arbeitsschritte für den Benutzer;
- Beobachtungs- und Diagnoseabfragen;
- erwartete Beobachtungen und Interpretationsgrenzen;
- Reset auf den definierten Ausgangszustand;
- vollständigen fachlichen Cleanup;
- Zuordnung zu Präsentation, Sprecherhinweisen und Teilnehmerunterlage.

### 3.2 SQL_Server_Lab

`SQL_Server_Lab` wird verwendet, um die vom Beispiel verlangte technische Umgebung zu realisieren. Dazu gehören abhängig vom Szenario:

- Docker-Container;
- Podman-Container;
- Hyper-V-VMs mit Windows oder Linux;
- mehrere SQL-Server-Instanzen;
- getrennte CPU-, RAM-, Storage- oder Netzwerkprofile;
- zusätzliche Client-, Workload- oder Infrastrukturkomponenten;
- gemischte Topologien aus mehreren Providern;
- Lifecycle, State, Start, Stop, Reset und Abbau der Infrastruktur.

Das Schulungsrepository implementiert keine eigene Docker-, Podman- oder Hyper-V-Provisionierung. Fehlt `SQL_Server_Lab` eine konkret benötigte Fähigkeit, wird diese Lücke mit dem betroffenen Beispiel und dem technischen Bedarf dokumentiert. Eine Änderung im Lab-Repository erfolgt erst nach ausdrücklicher Freigabe.

## 4. Unterstützte Topologien

Die Wahl der Zielplattform erfolgt aus den Anforderungen des Beispiels.

| Topologie | Typischer Einsatz |
|---|---|
| Docker | portable Linux-SQL-Server-Szenarien mit geringem Aufbauaufwand |
| Podman | alternative Container-Lane und rootless-orientierte Umgebungen |
| Hyper-V mit Windows | Windows Authentication, Windows-spezifische SQL-Funktionen, Client- oder Betriebssystemverhalten |
| Hyper-V mit Linux | kontrollierte Linux-, Storage- oder Netzwerkprofile außerhalb eines einzelnen Containers |
| Gemischte Topologie | mehrere SQL-Server-Knoten, getrennte Workload-Clients, Netzwerk- oder Storage-Komponenten über unterschiedliche Provider |

Ein Beispiel darf mehrere Provider kombinieren. Die Topologie ist kein Selbstzweck, sondern Teil des Reproduktionsvertrags.

## 5. Lebenszyklus eines Schulungsszenarios

### 5.1 Auswahl

Der Benutzer wählt ein einzelnes Beispiel oder eine zusammengehörige LAB-Serie aus. Die Auswahl muss unabhängig vom vollständigen Schulungslauf möglich sein.

### 5.2 Anforderungsauflösung

Aus der Szenariodefinition werden mindestens aufgelöst:

- Demo-ID oder LAB-ID;
- unterstützte SQL-Server-Versionen;
- erforderliche Provider und Topologie;
- Anzahl und Rollen der Instanzen;
- Ressourcenprofil;
- benötigte Datenbanken und Datenbankoptionen;
- erforderliche Sessions und Clients;
- zusätzliche Dienste;
- Safety-Klasse;
- Aufbau-, Reset- und Abbaupfad.

### 5.3 Provisionierung

`SQL_Server_Lab` erzeugt die benötigte Infrastruktur. Die Provisionierung ist erst abgeschlossen, wenn alle erforderlichen Komponenten erreichbar und ihre grundlegenden Fähigkeiten geprüft sind.

### 5.4 Vorbereitung

Nach der Infrastrukturprovisionierung bereitet `SQL_PerformanceSchulung` den fachlichen Ausgangszustand vor. Dies umfasst je nach Beispiel:

- Datenbanken und Schemata;
- synthetische Tabellen und Datenverteilungen;
- Statistiken und Indexzustände;
- Query Store und Extended Events;
- Logins, Benutzer und Berechtigungen;
- mehrere vorbereitete Sessions;
- Workload- oder Clientskripte;
- definierte Fehl- oder Kontrastzustände.

### 5.5 Übergabe an den Benutzer

Nach erfolgreicher Vorbereitung erhält der Benutzer eine kompakte Übergabe mit:

- Szenario-ID und Titel;
- Status `READY_FOR_USER`;
- Verbindungsinformationen ohne persistierte Secrets;
- Rollen der bereitgestellten Instanzen und Komponenten;
- Startpunkt der Anleitung;
- auszuführenden Schritten;
- erwarteten Beobachtungen;
- Reset- und Abbaukommando;
- bekannten Grenzen des aktuellen Hosts oder Providers.

### 5.6 Interaktive Durchführung

Der Benutzer führt die vorgesehenen Schritte selbst aus. Dazu gehören ausdrücklich:

- T-SQL ändern und erneut ausführen;
- unterschiedliche Parameterwerte testen;
- Pläne, Waits, Locks, Query Store oder Extended Events untersuchen;
- Gegenmaßnahmen anwenden und zurücknehmen;
- Beobachtungsabfragen wiederholen;
- alternative Hypothesen prüfen.

Die Umgebung ist nicht auf einen einzigen automatisierten Ablauf beschränkt.

### 5.7 Reset

Jedes interaktive Szenario benötigt einen definierten Reset. Der Reset stellt den fachlichen Ausgangszustand wieder her, ohne zwingend die gesamte Infrastruktur neu aufzubauen.

Ein Reset kann beispielsweise:

- die markierte Testdatenbank neu erzeugen;
- synthetische Daten erneut generieren;
- Statistiken und Indexe auf den Ausgangszustand setzen;
- Query Store oder Extended Events kontrolliert zurücksetzen;
- vorbereitete Sessions beenden und neu starten;
- geänderte Konfigurationen reversibel zurücknehmen.

Ist ein sicherer partieller Reset technisch nicht möglich, wird die gesamte Szenarioumgebung verworfen und reproduzierbar neu aufgebaut.

### 5.8 Abbau

Der vollständige Abbau entfernt fachliche Artefakte und anschließend die durch `SQL_Server_Lab` erzeugte Infrastruktur. Der Abbau erfolgt nur auf ausdrücklichen Benutzerwunsch oder bei einem nicht fortsetzbaren Fehler.

## 6. Szenariovertrag je Beispiel

Für jedes interaktiv bereitstellbare Beispiel wird künftig eine Szenariodefinition geführt. Sie ergänzt das bestehende Demo-Manifest und ersetzt es nicht.

Das bestehende `manifest.json` bleibt für automatisierte Phasen- und Runtime-Prüfungen zuständig. Die interaktive Szenariodefinition beschreibt zusätzlich:

- `scenarioId`;
- zugehörige Demo- und LAB-IDs;
- Titel für den Benutzer;
- Lernziel;
- Topologie und Providerrollen;
- SQL-Server-Versionen;
- Ressourcenanforderungen;
- erforderliche Komponenten;
- Vorbereitungsschritte;
- Benutzerübergabe;
- interaktive Schrittfolge;
- Beobachtungsaufträge;
- Resetstrategie;
- Abbaustrategie;
- bekannte Varianten und Grenzen.

Eine Demo kann mehrere Szenariovarianten besitzen, beispielsweise eine kompakte Containerfassung und eine vertiefte Hyper-V- oder Mischfassung.

## 7. Bedienmodell

Die spätere Bedienung soll mindestens folgende Operationen anbieten:

```powershell
# verfügbare Schulungsszenarien anzeigen
Get-PerformanceTrainingScenario

# ein ausgewähltes Beispiel vollständig vorbereiten
Start-PerformanceTrainingScenario -ScenarioId <ID> -Provider <docker|podman|hyperv|mixed>

# den fachlichen Ausgangszustand wiederherstellen
Reset-PerformanceTrainingScenario -ScenarioId <ID>

# die gesamte Umgebung entfernen
Remove-PerformanceTrainingScenario -ScenarioId <ID>
```

Die Namen sind ein Zielvertrag für die spätere Implementierung im Schulungsrepository. Sie erzeugen keine Pflicht zu gleichnamigen Commands in `SQL_Server_Lab`.

## 8. Verhältnis zur automatisierten Testmatrix

Die automatisierte Testmatrix prüft, ob:

- die Umgebung aufgebaut werden kann;
- die Vorbereitung reproduzierbar ist;
- die erwarteten Kernbeobachtungen eintreten;
- der Reset funktioniert;
- der vollständige Abbau funktioniert.

Sie darf die interaktive Nutzbarkeit nicht ersetzen. Ein Szenario gilt erst als vollständig umgesetzt, wenn zusätzlich eine verständliche Benutzeranleitung und ein praktisch verwendbarer Übergabepunkt vorhanden sind.

Der bisherige Katalog unter `Tests/Lab/performance-lab-matrix.json` bleibt als Qualitätssicherungsinstrument bestehen. Er ist nicht der primäre Szenariokatalog für den Benutzer.

## 9. Mindestanforderungen an eine vollständige Umsetzung

Ein Schulungsszenario gilt erst als vollständig, wenn folgende Artefakte vorhanden und geprüft sind:

1. fachlicher Szenariovertrag;
2. technische Topologiedefinition;
3. Provisionierung über `SQL_Server_Lab`;
4. reproduzierbare Vorbereitung;
5. Benutzerübergabe mit Verbindungs- und Rollenbeschreibung;
6. interaktive Schritt-für-Schritt-Anleitung;
7. Beobachtungs- und Diagnoseabfragen;
8. Resetpfad;
9. vollständiger Abbaupfad;
10. automatisierter Smoke-Test für Aufbau, Vorbereitung, Reset und Abbau;
11. Mindestanforderungen an die Hosthardware;
12. dokumentierte Provider- und Versionsgrenzen.

## 10. Arbeitspakete und Reihenfolge

| ID | Priorität | Arbeit | Voraussetzung | Abschlusskriterium |
|---|---:|---|---|---|
| `LABSCN-001` | P0 | Ziel, Verantwortungsgrenze und Lebenszyklus interaktiver Schulungsszenarien festlegen | bestehende Demo- und Lab-Verträge | diese Architekturentscheidung ist im Repository verankert |
| `LABSCN-002` | P0 | Szenarioinventar und Schema für Szenariodefinitionen erstellen | `LABSCN-001` | jedes bestehende und geplante Beispiel ist als interaktiv geeignet, nur automatisiert prüfbar oder nicht anwendbar klassifiziert |
| `LABSCN-003` | P0 | ersten vollständigen Vertical Slice umsetzen | `LABSCN-002` | ein grünes Beispiel kann über `SQL_Server_Lab` aufgebaut, vorbereitet, interaktiv genutzt, zurückgesetzt und entfernt werden |
| `LABSCN-004` | P1 | Benutzerbedienung und How-to standardisieren | `LABSCN-003` | Auswahl, Start, Übergabe, Reset und Remove sind dokumentiert und praktisch geprüft |
| `LABSCN-005` | P1 | weitere Container- und Hyper-V-Szenarien umsetzen | `LABSCN-003` | geeignete Beispiele besitzen reproduzierbare Providerprofile |
| `LABSCN-006` | P2 | gemischte Topologien umsetzen | konkretes Beispiel mit nachgewiesenem Bedarf | mindestens ein fachlich begründetes Mischszenario ist vollständig reproduzierbar |

## 11. Nächster Umsetzungsschritt

Als nächster Schritt wird unter `LABSCN-002` das vorhandene und geplante Demo-Inventar klassifiziert. Danach wird für ein geeignetes grünes Beispiel ein vollständiger Vertical Slice umgesetzt. Die Umgebung bleibt nach der Vorbereitung für den Benutzer verfügbar und wird nicht durch den Testlauf automatisch entfernt.

Zusätzliche Funktionalität in `SQL_Server_Lab` wird nur verlangt, wenn die konkrete Szenariodefinition mit den vorhandenen Lab-Funktionen nicht realisierbar ist. Die fehlende Fähigkeit wird dann vor jeder Änderung im Lab-Repository ausdrücklich benannt.
