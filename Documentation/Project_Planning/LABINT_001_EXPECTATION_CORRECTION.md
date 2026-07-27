# Korrektur – Erwartung von SQL_PerformanceSchulung an SQL_Server_Lab

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-07-27 |
| Pull Request | `#22` |
| Anlass | zu weitgehende Ableitung aus dem langfristigen Architekturentwurf von `SQL_Server_Lab` |
| Änderungen in SQL_Server_Lab | keine |

## Festgestellte Fehlinterpretation

Die vorherige Planung behandelte eine native Project-Adapter-/Lab-Package-Engine, eine generische JSON-/Event-Schnittstelle sowie weitere Control-Plane-Funktionen als spätere Anforderungen des Schulungsprojekts.

Diese Anforderungen folgen nicht aus dem tatsächlichen Integrationsziel. Sie wurden aus einem allgemeinen Architekturentwurf des Lab-Repositories übernommen, obwohl die Schulungsautomation sie nicht benötigt.

## Korrigierte Erwartung

`SQL_Server_Lab` muss für dieses Projekt:

1. eine angeforderte SQL-Server-Version über Docker oder Podman bereitstellen;
2. SQL-Readiness prüfen;
3. Run-ID, Provider, Host und Port zurückgeben;
4. die bereitgestellte Umgebung sicher entfernen.

`SQL_PerformanceSchulung` übernimmt selbst:

1. Demo-Discovery und Testkatalog;
2. Demoauswahl und Matrixbildung;
3. Ausführung des vorhandenen Demo-Harness;
4. fachliche Assertions und Skip-Verträge;
5. Demo-Cleanup und Testzusammenfassung.

## Konsequenz

`LABINT-005` und die Migration auf eine native Lab-Package-Ausführung wurden aus dem Backlog entfernt. Der nächste Schritt bleibt ein einfacher PowerShell-Runner über die bereits vorhandenen öffentlichen Lab-Commands.

Zusätzliche Funktionalität in `SQL_Server_Lab` wird nur dann verlangt, wenn ein realer Docker- oder Podman-Lauf eine konkrete und reproduzierbare Lücke nachweist. Eine solche Änderung wird vorab benannt und nicht ohne ausdrückliche Freigabe umgesetzt.

## Abnahme

Der korrigierte Branchstand bestand:

- `SQL Server Lab integration contract`, Lauf `30242868365`;
- `Framework contracts`, Lauf `30242868248`;
- `Curriculum and privacy validation`, Lauf `30242868268`;
- `Advanced lab design contracts`, Lauf `30242868260`;
- `Advanced lab design contracts VP3-VP5`, Lauf `30242868256`;
- `W2-001 legacy example classification`, Lauf `30242868303`.
