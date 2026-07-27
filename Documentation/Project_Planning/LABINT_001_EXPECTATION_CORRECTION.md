# Historische Korrektur – Erwartung an SQL_Server_Lab

| Merkmal | Wert |
|---|---|
| Status | `SUPERSEDED_BY_DEC-044` |
| Stand | 2026-07-27 |
| Ursprünglicher Pull Request | `#22` |
| Aktueller Zielvertrag | [`SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md`](../Architecture/SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md) |
| Änderungen in SQL_Server_Lab | keine |

## 1. Historischer Zweck

Dieses Dokument korrigierte eine frühere Überinterpretation, nach der `SQL_PerformanceSchulung` eine generische Project-Adapter-/Lab-Package-Engine, eine JSON-/Event-Schnittstelle und weitere Control-Plane-Funktionen von `SQL_Server_Lab` verlangen würde.

Diese generischen Anforderungen bleiben verworfen.

## 2. Warum die damalige Kurzfassung nicht der endgültige Zielzustand ist

Die damalige Korrektur reduzierte die Integration anschließend zu stark auf:

```text
SQL-Server-Instanz erstellen
-> automatisierte Demos ausführen
-> Umgebung entfernen
```

Diese Kurzfassung beschreibt nur einen technischen Testlauf. Sie bildet nicht das inzwischen verbindlich präzisierte Lernziel ab, nach dem Benutzer einzelne Beispiele selbst erleben, verändern, zurücksetzen und erneut ausführen können sollen.

## 3. Aktueller verbindlicher Zielzustand

`DEC-044` und `LABSCN-001` legen fest:

- `SQL_Server_Lab` ist das verbindliche Provisionierungsframework;
- Zielplattformen können Docker, Podman, Hyper-V oder gemischte Topologien sein;
- `SQL_PerformanceSchulung` beschreibt je Beispiel die benötigte Topologie, Vorbereitung und Benutzeraktionen;
- die Umgebung wird nach der Vorbereitung als `READY_FOR_USER` übergeben;
- sie bleibt für interaktive Versuche bestehen;
- der Benutzer kann Reset oder vollständigen Abbau anfordern;
- automatisierte Testmatrizen dienen ausschließlich der Qualitätssicherung.

## 4. Weiterhin gültige Abgrenzung

Weiterhin nicht verlangt werden pauschale generische Plattformfunktionen ohne konkreten Szenariobedarf. Eine zusätzliche Fähigkeit in `SQL_Server_Lab` wird nur anhand eines tatsächlich zu realisierenden Schulungsszenarios benannt und erst nach ausdrücklicher Freigabe umgesetzt.

## 5. Nachfolgearbeit

Die weitere Verarbeitung erfolgt unter `LABSCN-002` bis `LABSCN-006`. `LABINT-002` bis `LABINT-004` bleiben nachgeordnete technische Prüfungen für Aufbau, Vorbereitung, Reset und Abbau.
