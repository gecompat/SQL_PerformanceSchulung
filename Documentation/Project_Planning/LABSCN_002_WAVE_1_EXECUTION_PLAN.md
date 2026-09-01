# LABSCN-002 – Welle 1: Szenarioinventar und Reproduktionsmodell

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-09-01 |
| Arbeitsrepository | `gecompat/SQL_PerformanceSchulung` |
| Provisionierungsframework | `gecompat/SQL_Server_Lab` |
| Zielprovider dieser Welle | Docker und Podman |
| Nachfolgewelle | `LABSCN-003` – erster vollständiger Vertical Slice |

## 1. Ziel

Welle 1 klassifiziert die vorhandenen und geplanten Schulungsdemos danach, ob ihr technischer Effekt in einer durch `SQL_Server_Lab` bereitgestellten Docker- oder Podman-Umgebung reproduzierbar hergestellt, beobachtet, zurückgesetzt und erneut ausgeführt werden kann.

Die Welle implementiert keine eigene Containerprovisionierung im Schulungsrepository. `SQL_Server_Lab` erzeugt und entfernt die technische Umgebung. `SQL_PerformanceSchulung` definiert Datenzustand, Sessionrollen, Erzwingungslogik, Beobachtung, fachliche Assertions und Reset.

## 2. Verbindliches Ausführungsmodell

Jedes geeignete Szenario wird in vier getrennten Schichten beschrieben:

```text
Lab-Manifest
    -> SQL-Server-Version, Provider, Ressourcen, Datenbanken und Serverkonfiguration

Szenariodefinition
    -> Lernziel, Ausgangszustand, Rollen, Vorbereitung, Benutzerübergabe und Reset

Demo-Manifest
    -> automatisierte Phasen, Safety-Gates, Zeitbudget und Cleanup

T-SQL-Skripte
    -> Datenzustand, Synchronisation, Workload, Beobachtung und Assertions
```

Der externe Runtime-Harness startet unabhängige SQL-Verbindungen und überwacht deren Laufzeit. Fachliche Reihenfolgen werden nicht durch Betriebssystem-Sleeps oder zufällige Prozessstartzeiten bestimmt. Sie werden durch benannte T-SQL-Signale und nachprüfbare Zustandsübergänge innerhalb der markierten Testdatenbank gesteuert.

## 3. Reproduzierbarkeitsklassen

### Klasse A – logisch deterministisch und containergeeignet

Der Effekt kann durch kontrollierte Daten, Datenbankoptionen, Sessionreihenfolge und T-SQL-Assertions weitgehend unabhängig von der Hostleistung hergestellt werden. Typische Bereiche sind SARGability, implizite Konvertierung, Statistikverteilungen, Parameter Sniffing, Blocking, Deadlocks, Isolation, Query Store und Extended Events.

### Klasse B – containergeeignet mit Ressourcen- und Toleranzvertrag

Der Effekt kann in Containern erzeugt werden, hängt aber zusätzlich von CPU, RAM, Scheduleranzahl, Memory Grants oder Workloadintensität ab. Typische Bereiche sind Parallelität, Sort- und Hash-Spills, Tempdb-Belastung und CPU Pressure. Ein Szenario dieser Klasse benötigt Mindestressourcen, Toleranzwerte und einen kontrollierten `SKIP_HOST_CAPABILITY`-Pfad.

### Klasse C – nur eingeschränkt reproduzierbar

Der Effekt hängt wesentlich von realer Storage-Latenz, NUMA, Netzwerkverhalten, Betriebssystemdetails oder anderer nicht ausreichend kontrollierbarer Hosthardware ab. Solche Inhalte können beobachtbar oder erklärbar sein, gelten aber nicht ohne weiteren Nachweis als vollständig reproduzierbare Docker-/Podman-Szenarien.

### Klasse D – kein technisches Laufzeitszenario

Der Inhalt besitzt keinen isolierbaren technischen Effekt oder dient ausschließlich der Erklärung, Einordnung oder visuellen Analyse.

## 4. Erzwingungsvertrag je Szenario

Für jede Demo werden mindestens folgende Fragen beantwortet:

1. Welcher konkrete SQL-Server-Zustand muss eintreten?
2. Welche Datenverteilung, Datenbankoption oder Serverkonfiguration ist dafür erforderlich?
3. Welche unabhängigen Sessions werden benötigt?
4. Durch welches T-SQL-Signal oder welche Zustandsbarriere wird die Reihenfolge festgelegt?
5. Welche DMV-, Plan-, Query-Store- oder Extended-Events-Evidenz weist den Zustand nach?
6. Welche Aspekte sind versions- oder buildabhängig?
7. Wann ist `SKIP` fachlich korrekt und wann liegt ein `FAIL` vor?
8. Wie wird der Ausgangszustand wiederhergestellt?
9. Welche Mindestressourcen benötigt der Host?

## 5. Regeln für deterministische T-SQL-Szenarien

Synthetische Daten verwenden feste Zeilenzahlen, kontrollierte Schlüsselbereiche und explizite Verteilungen. Unkontrollierte Zufallswerte, aktuelle Zeitstempel und Abhängigkeiten von physischer Zeilenreihenfolge sind für den fachlichen Ausgangszustand unzulässig.

Multi-Session-Szenarien verwenden die vorhandenen Objekte `fwk.USP_Signal`, `fwk.USP_WaitForSignal` und `fwk.USP_ClearSignals`. `WAITFOR DELAY` darf innerhalb der Polling-Implementierung oder als begrenzte Beobachtungsdauer verwendet werden, jedoch nicht als alleinige fachliche Synchronisation zwischen Sessions.

Ein erfolgreicher Prozess-Exitcode belegt lediglich die technische Ausführung. Der fachliche Effekt gilt erst als hergestellt, wenn ein Verification-Skript eine definierte Assertion erfüllt und einen maschinenlesbaren Summary-Code ausgibt.

## 6. Resetstrategien

Die bevorzugte Resetstrategie ist die deterministische Neuerzeugung der markierten Testdatenbank. Sie entfernt Restzustände aus Daten, Statistiken, Plan Cache, Query Store, Extended Events und offenen Transaktionen.

Ein Restore einer vorbereiteten Baseline ist nur dann vorzuziehen, wenn die Neuerzeugung der Daten unverhältnismäßig lange dauert. Der Restore muss versionskompatibel, vollständig automatisiert und ebenso verifizierbar sein.

Ein partieller Reset ist zulässig, wenn er nachweislich alle szenariorelevanten Zustände zurücksetzt. Ist dies nicht belastbar möglich, wird die Szenarioumgebung vollständig entfernt und reproduzierbar neu aufgebaut.

## 7. Welle-1-Arbeitspakete

| ID | Priorität | Arbeit | Ergebnis |
|---|---:|---|---|
| `LABSCN-002.1` | P0 | vorhandene und geplante Demos inventarisieren | kanonisches Inventar mit Demo-ID, Pfad und Status |
| `LABSCN-002.2` | P0 | Docker-/Podman-Eignung klassifizieren | Klasse A bis D je Demo |
| `LABSCN-002.3` | P0 | Erzwingungs- und Verifikationsmechanismus erfassen | Zustand, Sessions, Signale, Assertions und Reset je Demo |
| `LABSCN-002.4` | P0 | Mindestressourcen und Versionsgrenzen erfassen | Host- und SQL-Version-Vertrag je Szenario |
| `LABSCN-002.5` | P0 | Szenariodefinitionsschema entwerfen | maschinenlesbarer Vertrag für interaktive Szenarien |
| `LABSCN-002.6` | P0 | Vertical Slice auswählen | freigegebener Kandidat für `LABSCN-003` |

Alle sechs Arbeitspakete sind abgeschlossen. Das maschinenlesbare Inventar
enthält alle 22 produktiven Demo-Manifeste; die statische Prüfung vergleicht
die Menge vollständig mit dem aktiven Demo-Katalog und erzwingt Lifecycle-,
Ressourcen-, Provider-, Versions- und Resetfelder je Eintrag.

## 8. Reihenfolge innerhalb der ersten Welle

Zuerst werden logisch deterministische Demos untersucht. Die erste Prioritätsgruppe umfasst Concurrency, SARGability, Statistiken, Parameter- und Planverhalten sowie Query Store und Extended Events. Ressourcenabhängige Demos werden anschließend klassifiziert, jedoch erst nach einem eigenen Capability- und Toleranzvertrag als Vertical Slice umgesetzt.

Der bevorzugte erste Vertical Slice ist `CON-004_Blocking_Chain`, weil die Sessionrollen bereits getrennt vorliegen, der Zustand durch explizite Transaktionen und T-SQL-Signale erzwingbar ist und Docker beziehungsweise Podman keine besondere Infrastrukturkomponente benötigen.

Die wichtigste Alternative ist `QRY-001_SARGability`. Sie ist technisch einfacher und eignet sich als Single-Session-Referenz, validiert jedoch nicht den vorhandenen Multi-Session-Vertrag.

## 9. Abschlusskriterien der Welle

Welle 1 ist abgeschlossen, wenn:

- jede inventarisierte Demo einer Reproduzierbarkeitsklasse zugeordnet ist;
- für jede Klasse-A- und Klasse-B-Demo der zu erzwingende Zustand dokumentiert ist;
- erforderliche Sessions und T-SQL-Barrieren bekannt sind;
- Assertions, Resetstrategie und Mindestressourcen erfasst sind;
- nicht belastbar reproduzierbare Aspekte ausdrücklich gekennzeichnet sind;
- ein Szenariodefinitionsschema vorliegt;
- `CON-004` oder ein fachlich besser geeigneter Kandidat für `LABSCN-003` freigegeben ist.

## 10. Sicherheits- und Datenschutzgrenze

Szenariodefinitionen und Inventare enthalten ausschließlich synthetische Kennungen, öffentliche SQL-Server-Versionen, generische Rollen und repositoryrelative Pfade. Reale Hostnamen, Benutzernamen, Kennwörter, interne Pfade oder produktive Diagnosedaten werden nicht versioniert.

## 11. Abschlussnachweis

`Tests/Static/validate_performance_scenarios.py` bestätigt 22 inventarisierte
produktive Demos und die freigegebenen interaktiven Szenariodefinitionen. Der
erste Vertical Slice `CON-004` sowie der Folgeslice `DGN-005` besitzen jeweils
einen praktisch validierten Docker-/Podman-Lifecycle auf SQL Server 2025.
