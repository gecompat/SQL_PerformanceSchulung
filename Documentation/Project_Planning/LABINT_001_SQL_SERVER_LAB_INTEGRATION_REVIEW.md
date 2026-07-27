# Review – SQL_Server_Lab-Integration für Schulungsszenarien

| Merkmal | Wert |
|---|---|
| Status | `SUPERSEDED_BY_LABSCN-001` |
| Stand | 2026-07-27 |
| Ursprünglicher Testumfang | `LABINT-001` |
| Aktueller Zielvertrag | `LABSCN-001`, `DEC-044` |
| Änderungen in SQL_Server_Lab | keine |

## 1. Einordnung

Das ursprüngliche Review konzentrierte sich auf automatisierte Docker-/Podman-Testläufe. Dieser Umfang bleibt als technische Qualitätssicherung gültig, ist aber nicht der primäre Zweck der Integration.

Der verbindliche Zielzustand ist nun die Bereitstellung interaktiver Schulungsszenarien. Der Benutzer wählt ein Beispiel aus, erhält eine vollständig vorbereitete Umgebung und kann die Situation selbst untersuchen, verändern, zurücksetzen und erneut ausführen.

## 2. Primärer Ablauf

```text
Beispiel auswählen
-> Anforderungen und Topologie auflösen
-> Umgebung mit SQL_Server_Lab erzeugen
-> fachlichen Ausgangszustand vorbereiten
-> READY_FOR_USER
-> Benutzer führt das Beispiel interaktiv durch
-> Reset oder vollständiger Abbau
```

Die Umgebung wird nach der Vorbereitung nicht automatisch entfernt.

## 3. Unterstützte Zielsysteme

Abhängig vom Beispiel können verwendet werden:

- Docker;
- Podman;
- Hyper-V mit Windows oder Linux;
- mehrere SQL-Server-Instanzen;
- zusätzliche Workload- oder Clientkomponenten;
- gemischte Topologien.

Die Providerwahl folgt dem technischen Reproduktionsbedarf des Beispiels.

## 4. Verantwortungsgrenze

`SQL_PerformanceSchulung` definiert Lernziel, Topologiebedarf, Setup, synthetische Daten, Benutzeraktionen, Beobachtungsabfragen, Reset und fachlichen Cleanup.

`SQL_Server_Lab` wird verwendet, um die dafür benötigte technische Umgebung zu provisionieren und deren Lifecycle zu verwalten.

Das Schulungsrepository implementiert keine eigene Docker-, Podman- oder Hyper-V-Provisionierung.

## 5. Rolle des vorhandenen Testkatalogs

Der Katalog unter `Tests/Lab/performance-lab-matrix.json` bleibt bestehen. Er dient der automatisierten Prüfung von:

- Provisionierung;
- Vorbereitung;
- Kernbeobachtungen;
- Reset;
- Abbau.

Er ist nicht der spätere Benutzerszenariokatalog. Interaktive Szenariodefinitionen werden unter `LABSCN-002` separat modelliert.

## 6. Zusätzliche Lab-Funktionalität

Es wird nicht pauschal eine generische Package-, Event- oder Control-Plane-Architektur verlangt.

Zusätzliche Funktionalität in `SQL_Server_Lab` wird nur dann angefordert, wenn ein konkretes Schulungsszenario mit den vorhandenen Fähigkeiten nicht realisierbar ist. Die Lücke wird mit Szenario-ID, benötigter Topologie und technischem Grund dokumentiert. Eine Umsetzung im Lab-Repository erfolgt erst nach ausdrücklicher Freigabe.

## 7. Nachfolgearbeit

1. `LABSCN-002`: Szenarioinventar und Definitionsschema.
2. `LABSCN-003`: erster vollständiger interaktiver Vertical Slice.
3. `LABSCN-004`: standardisierte Benutzerbedienung und Anleitung.
4. `LABSCN-005`: weitere Container- und Hyper-V-Szenarien.
5. `LABSCN-006`: gemischte Topologien bei nachgewiesenem Bedarf.
6. `LABINT-002` bis `LABINT-004`: nachgeordnete automatisierte Qualitätssicherung.
