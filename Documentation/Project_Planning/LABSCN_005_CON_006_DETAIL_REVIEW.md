# LABSCN-005 – Detailreview CON-006

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-09-01 |
| Kandidat | `CON-006` – reproduzierbarer Deadlock-Zyklus |
| Provider | Docker und Podman |
| interaktive Zielversion | SQL Server 2025 / Compatibility Level 170 |
| Safety | `YELLOW`, ausschließlich isolierte Wegwerfinstanz |

## Reviewentscheidung

`CON-006` wird als dritter interaktiver `LABSCN-005`-Slice freigegeben. Der
Lernmehrwert gegenüber `CON-004` ist eindeutig: `CON-004` zeigt eine gerichtete
Blocking Chain mit kontrollierter Freigabe, während `CON-006` einen Zyklus,
die Auflösung durch ein Opfer, Fehler 1205 und die Gegenprobe mit einheitlicher
Zugriffsreihenfolge verbindet. Die vorhandene automatisierte Demo ist im
Actions-Lauf 33222989644 auf SQL Server 2019, 2022 und 2025 jeweils zweimal
runtimevalidiert.

Die Primärquellen `SRC-066` bis `SRC-068` tragen Deadlockmechanismus,
Opferpriorität und die Nutzung der bestehenden `system_health`-Session. Die
konkrete Reproduktion bleibt `EMPIRICAL`: Der Vertrag fordert genau ein
abgefangenes Opfer mit Fehler 1205 und genau einen Survivor. Ein passender
Deadlock-Graph ist zusätzliche Evidenz; fehlende Sichtbarkeit wird kontrolliert
als `SKIP_EVIDENCE_MISSING` behandelt und nicht als erfundener Nachweis.

## Lifecycle- und Safety-Vertrag

- Eine frische SQL-Server-2025-Linux-Containerinstanz im Profil `standard` ist
  ausreichend; mehrere Instanzen, Providererweiterungen und Änderungen an
  `SQL_Server_Lab` sind nicht erforderlich.
- Der Project Adapter erzeugt nur die vierfach markergebundene Testdatenbank,
  zwei synthetische Zeilen, Signalobjekte und die Ergebnisablage.
- Drei Benutzer-Sessions übernehmen `ACTOR_A`, `ACTOR_B` und `OBSERVER`.
  Benannte Datenbanksignale sichern die Reihenfolge; feste Sleeps steuern nicht
  den fachlichen Zustand.
- `DEADLOCK_PRIORITY LOW` beziehungsweise `HIGH` macht `ACTOR_A` zum
  erwarteten Opfer. Beide Actor-Skripte rollen offene Transaktionen im
  Fehlerpfad zurück und akzeptieren ausschließlich Fehler 1205.
- Alle Signal-Waits sind auf höchstens 30 Sekunden, der Deadlockabschnitt auf
  45 Sekunden und der vollständige Demolauf auf 180 Sekunden begrenzt.
- Die Beobachtung liest ausschließlich die bestehende `system_health`-
  Ring-Buffer-Evidenz. Der Slice erstellt, verändert oder exportiert keine
  Extended-Events-Session und persistiert kein Plan- oder Graphartefakt.
- Reset und Remove prüfen vor dem Löschen die vier Eigentumsmarker. Remove
  beendet gegebenenfalls verbliebene Sessions durch den markergebundenen
  Datenbankabbau und entfernt anschließend nur die zugehörige Lab-Infrastruktur.

## Teilnehmer- und Evidenzvertrag

Der primäre Ablauf bleibt `MANUAL`. Die Teilnehmenden starten die drei
Deadlock-Sessions in getrennten SQL-Fenstern, prüfen Ergebnisablage und
optionalen Graph, setzen den Zustand zurück und führen die geordnete Gegenprobe
aus. `AUTOMATED_VERIFY` bleibt ein getrennter Qualitätssicherungspfad.

Die interaktive Abnahme verlangt je Provider:

1. `Start -> READY_FOR_USER` mit validiertem Adapterzustand;
2. genau ein Opfer mit Fehler 1205 und genau einen Survivor;
3. optionale, datenbankgefilterte `system_health`-Evidenz oder kontrollierten
   Skip;
4. zwei erfolgreiche Akteure in der geordneten Gegenprobe;
5. `Reset -> READY_FOR_USER` auf derselben Instanz;
6. markergebundenen Datenbank-, Infrastruktur- und State-Abbau mit `REMOVED`.

## Runtimeabnahme

Der vollständige Lifecycle bestand am 2026-09-01 auf SQL Server 2025 mit
Docker (RunId `76cff6ed-a714-44e6-beda-6b916600cb98`) und Podman (RunId
`6d2d0a51-1915-4e65-a380-baec715fc676`). Beide Läufe belegten genau ein Opfer
mit Fehler 1205, genau einen Survivor, einen datenbankbezogenen Deadlock-Graph,
zwei erfolgreiche Akteure in der geordneten Gegenprobe, Reset zu
`READY_FOR_USER` und abschließendes Remove zu `REMOVED`.

Der Podman-Lauf verwendete wegen einer fremden aktiven Altressource das
isolierte Netz `SQL_LAB_PODMAN_CON006` mit einem dedizierten privaten
Testsubnetz. Der Lifecycle entfernte seine eigenen Container-, Volume- und
Netzressourcen vollständig und ließ die fremde Ressource unverändert. Damit ist der Szenarioslice
`VALIDATED`; der automatisierte Demovertrag bleibt ebenfalls `VALIDATED`.
