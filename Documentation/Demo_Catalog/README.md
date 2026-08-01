# Demo-Katalog

Der Demo-Katalog ist die zentrale Zuordnung zwischen Schulungsinhalt und technischer Vorführung. Ein Eintrag gilt erst dann als `VALIDATED`, wenn Demo-Vertrag, Quellenprüfung, statische Prüfung und die zutreffende Runtime-Matrix im Repository nachvollziehbar sind.

## Verbindliche Felder

- Demo-ID und Titel
- Themenblock und Lernziel
- zugehörige Präsentationsabschnitte
- SQL-Server-Version und Compatibility Level
- Edition und Betriebssystem
- Sicherheitsstufe und Ausführungspfad
- benötigte Sessions und Infrastruktur
- erwartete Dauer
- Quellen-, Claim- und Testprofilzuordnung
- Implementierungs- und Validierungsstatus

## Entscheidungspfad je Demo

Abschnitt 13.2 des Masterplans legt eine Stufenleiter fest. Verbindlich gilt die **kleinste ausreichende Stufe**. Die maschinenlesbare Zuordnung steht in [`demo_execution_paths.json`](demo_execution_paths.json) und wird durch `Tests/Static/validate_demo_execution_paths.py` geprüft.

| Stufe | Ausführungspfad | Verwendung |
|---:|---|---|
| 1 | `TSQL_TESTDB` | vorhandene Testinstanz plus eigene synthetische Testdatenbank |
| 2 | `TSQL_TESTDB` | reine T-SQL-Steuerung innerhalb einer isolierten Testinstanz |
| 3 | `CONTAINER` | containerisierte Einzelinstanz zur Bereitstellung oder für reproduzierbare CPU-/RAM-Grenzen |
| 4 | `HYPERV` | Windows-, OS-, Storage- oder Isolationsanforderungen |
| 5 | `MULTI_INSTANCE` | verteilte oder netzwerkabhängige Kernaussage |

Regeln:

- Jede implementierte Demo besitzt genau einen Eintrag. Fehlende und unbekannte Einträge sind ein Prüffehler.
- Stufe und Ausführungspfad müssen zusammenpassen. Die Stufen 1 und 2 verwenden beide `TSQL_TESTDB`.
- Für jeden Eintrag oberhalb von Stufe 2 werden die verworfene niedrigere Stufe und der technische Grund dokumentiert. Ohne diese Begründung schlägt die Prüfung fehl.
- Der Instanzbedarf wird getrennt von der Stufe geführt: `SHARED_TEST_INSTANCE` oder `DISPOSABLE_INSTANCE`. Eine gelbe oder rote Sicherheitsstufe verlangt immer eine Wegwerfinstanz.
- Sicherheitsstufe, Sitzungszahl und Manifestpfad müssen mit `Tests/Lab/performance-lab-matrix.json` und, sofern dort geführt, mit `Documentation/Inventories/performance_scenario_inventory.json` übereinstimmen.

Der Katalog beschreibt den **erforderlichen** Ausführungspfad. Er stellt keine Umgebung bereit und ist keine Eingabe für eine automatisierte Umgebungserzeugung. Die automatisierte Erstellung von Demoumgebungen ist bewusst zurückgestellt.

## Ausführungspfad der implementierten Demos

| Demo-ID | Titel | Sicherheit | Sitzungen | Stufe | Ausführungspfad | Instanzbedarf | Status |
|---|---|---|---:|---:|---|---|---|
| `QRY-001` | SARGability | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| `OPT-002` | Statistics Anatomy | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| `OPT-015` | Planweite und operatorbezogene Eigenschaften | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| `OPT-016` | Rebind, Rewind, Outer References und Spools | Grün | 1 | 1 | `TSQL_TESTDB` | `SHARED_TEST_INSTANCE` | `VALIDATED` |
| `OPT-013` | Controlled Spill | Gelb | 1 | 2 | `TSQL_TESTDB` | `DISPOSABLE_INSTANCE` | `VALIDATED` |
| `CON-004` | Blocking Chain | Gelb | 4 | 2 | `TSQL_TESTDB` | `DISPOSABLE_INSTANCE` | `VALIDATED` |

Keine implementierte Demo benötigt derzeit eine Stufe oberhalb von 2. Container werden ausschließlich für die Versionsmatrix der Gate-Evidenz eingesetzt, nicht weil eine Demo sie fachlich verlangt. `OPT-013` belastet `tempdb` der gesamten Instanz, `CON-004` hält Sperren über vier Sitzungen; beide verlangen deshalb eine Instanz, die zurückgesetzt oder verworfen werden darf.

Die Bedienanleitung für den Weg über eine vorhandene Instanz steht in [`LOCAL_TEST_ENVIRONMENT.md`](../HowTo/LOCAL_TEST_ENVIRONMENT.md).

## Validierte Vertiefungsdemos

| Demo-ID | Titel | Modul / Lernziel | Sicherheit | Ausführungspfad | Zielmatrix | Status |
|---|---|---|---|---|---|---|
| `OPT-015` | Planweite und operatorbezogene Eigenschaften | M02 / `LO-M02-08` | Grün | `TSQL_TESTDB` | SQL Server 2019/CL150, 2022/CL160, 2025/CL170; je zwei Läufe | `VALIDATED` |
| `OPT-016` | Rebind, Rewind, Outer References und Spools | M02 / `LO-M02-09` | Grün | `TSQL_TESTDB` | SQL Server 2019/CL150, 2022/CL160, 2025/CL170; je zwei Läufe | `VALIDATED` |

`OPT-015` verwendet einen synthetischen Out-of-range-Statistikfall und wertet Actual-Plan-Eigenschaften normalisiert aus. `OPT-016` untersucht eine hintfreie optimizergewählte Performance Spool; `NO_PERFORMANCE_SPOOL` wird ausschließlich als kontrollierte Gegenprobe verwendet.

Die vollständigen Phasen-, Ressourcen-, Evidenz-, Quellen- und Cleanup-Verträge stehen in den jeweiligen Demo-README-Dateien. Der formale Abnahmenachweis steht in [`ADV_008_OPT_015_016_REVIEW.md`](../Project_Planning/ADV_008_OPT_015_016_REVIEW.md).
