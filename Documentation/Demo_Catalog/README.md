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

## Validierte Vertiefungsdemos

| Demo-ID | Titel | Modul / Lernziel | Sicherheit | Ausführungspfad | Zielmatrix | Status |
|---|---|---|---|---|---|---|
| `OPT-015` | Planweite und operatorbezogene Eigenschaften | M02 / `LO-M02-08` | Grün | `TSQL_TESTDB` | SQL Server 2019/CL150, 2022/CL160, 2025/CL170; je zwei Läufe | `VALIDATED` |
| `OPT-016` | Rebind, Rewind, Outer References und Spools | M02 / `LO-M02-09` | Grün | `TSQL_TESTDB` | SQL Server 2019/CL150, 2022/CL160, 2025/CL170; je zwei Läufe | `VALIDATED` |

`OPT-015` verwendet einen synthetischen Out-of-range-Statistikfall und wertet Actual-Plan-Eigenschaften normalisiert aus. `OPT-016` untersucht eine hintfreie optimizergewählte Performance Spool; `NO_PERFORMANCE_SPOOL` wird ausschließlich als kontrollierte Gegenprobe verwendet.

Die vollständigen Phasen-, Ressourcen-, Evidenz-, Quellen- und Cleanup-Verträge stehen in den jeweiligen Demo-README-Dateien. Der formale Abnahmenachweis steht in [`ADV_008_OPT_015_016_REVIEW.md`](../Project_Planning/ADV_008_OPT_015_016_REVIEW.md).
