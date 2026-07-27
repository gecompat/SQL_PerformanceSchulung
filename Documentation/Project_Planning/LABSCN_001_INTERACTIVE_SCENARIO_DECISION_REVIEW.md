# Review – LABSCN-001 Interaktive Schulungsszenarien

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-07-27 |
| Entscheidung | `DEC-044` |
| Pull Request | `#23` |
| Änderungen in SQL_Server_Lab | keine |

## 1. Anlass

Die bisherige Lab-Planung konzentrierte sich zu stark auf automatisierte Testmatrizen. Der tatsächliche Zielzustand ist die Bereitstellung einzelner, vollständig vorbereiteter und interaktiv nutzbarer Schulungsbeispiele.

## 2. Verankerter Zielzustand

- Benutzer wählen ein einzelnes Beispiel oder eine LAB-Serie aus.
- `SQL_Server_Lab` realisiert die erforderliche Docker-, Podman-, Hyper-V- oder Mischumgebung.
- `SQL_PerformanceSchulung` bereitet Datenbanken, synthetische Daten, Konfigurationen und Ausgangssituation vor.
- Die Umgebung wird als `READY_FOR_USER` übergeben.
- Benutzer führen die Schritte selbst aus und können Abfragen, Parameter und Gegenmaßnahmen verändern.
- Jedes Szenario besitzt Reset und vollständigen Abbau.
- Automatisierte Testmatrizen bleiben nachgeordnete Qualitätssicherung.

## 3. Erzeugte und geänderte Artefakte

- neuer kanonischer Vertrag `Documentation/Architecture/SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md`;
- `DEC-044` in `.ai/DECISIONS.md`;
- neue Arbeitspakete `LABSCN-001` bis `LABSCN-006` im Backlog;
- Testautomatisierung als nachgeordnete Qualitätssicherung neu eingeordnet;
- operativer Status auf `LABSCN-002` als nächsten Schritt geändert;
- Infrastruktur- und Dokumentationsübersichten synchronisiert;
- frühere LABINT-Korrektur- und Reviewdokumente als historische, überholte Zwischenstände gekennzeichnet;
- statischer Validator um interaktiven Zielvertrag erweitert.

## 4. Abgrenzung

In `SQL_Server_Lab` wurde nichts geändert. Zusätzliche Lab-Funktionalität wird erst anhand einer konkreten Szenariodefinition benannt und nicht ohne ausdrückliche Freigabe implementiert.

## 5. Abnahme

Der Branchstand bestand:

- `SQL Server Lab scenario contract`, Lauf `30244511832`;
- `Framework contracts`, Lauf `30244511860`;
- `Curriculum and privacy validation`, Lauf `30244511870`;
- `Advanced lab design contracts`, Lauf `30244511868`;
- `Advanced lab design contracts VP3-VP5`, Lauf `30244511867`;
- `W2-001 legacy example classification`, Lauf `30244511815`.

## 6. Statusgrenze

Diese Welle verankert Ziel, Verantwortungsgrenze, Lifecycle und Folgearbeit. Sie implementiert noch kein konkretes interaktives Szenario.

## 7. Nächster Schritt

`LABSCN-002` inventarisiert alle vorhandenen und geplanten Beispiele, klassifiziert ihre interaktive Eignung und definiert das Szenarioschema. Danach wird unter `LABSCN-003` ein erster vollständiger Vertical Slice umgesetzt.
