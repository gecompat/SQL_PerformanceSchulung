# DGN-010 – begrenzter privater SELECTvergleich ohne/mit Candidateindex

Stand: 2026-10-12. TSK-011/CUR-021, DGN-010 weiterhin PROPOSED.
Basis f1984f36a91c67161a0acf66f22e3d373089edc6; empirischer Teilnachweis, keine öffentliche FWK-/Versions-/
TP-PERF- oder Modulabnahme.

## Vollständig abgeschlossene Basis und neue Messfrage

[PR193](https://github.com/gecompat/SQL_PerformanceSchulung/pull/193) vollständig
abgeschlossen: Head 12b0716293a8607994b80804e0402768b18997f5, sieben aktuelle Head-Workflows PASS;
Squash f1984f36a91c67161a0acf66f22e3d373089edc6, fünf Main-Workflows PASS; ganzer Tree fc9d81e3cb7c81063f65694fefb97bf3bc4300c5
exakt übernommen, main FF/sauber und eigener lokaler/Remote-Branch entfernt.
Die [erzwungenen Readerpfade](SQL_SERVER_2025_AI_INDEX_MEASUREMENT_REVIEW.md)
und [Owner-DML-Batches](SQL_SERVER_2025_AI_INDEX_DML_REVIEW.md) bleiben getrennte
Nachweise. Frühere grüne Fensterscopes werden nicht unverändert wiederholt.

Hier wird dieselbe ungezwungene SELECT-Struktur ohne und mit Candidateindex
ausgeführt: IDs 101–110, gebundene int-Parameter, ORDER BY Id, MAXDOP1, keine
INDEX-Hints. Ein WITHOUT LOGIN Reader besitzt unverändert CONNECT+SourceRows-SELECT.
Build/Drop und vollständige Source-/Config-/Reader-/Indexprüfungen liegen außerhalb
der Messfenster. Der Optimizer wählt den Zugriffspfad; diese neuen Fenster enthalten
keine Planausgabe und belegen daher keine tatsächliche Indexnutzung. Frühere
repräsentative Ownerpläne werden nicht als aktuelle Readerpläne ausgegeben.

## Vorab feste Population und Scope

Je Profil fünf separate Einquery-Warmups pro Indexzustand, anschließend drei serielle
AB-/BA-/AA-Blöcke mit je zwei Fenstern: 18 Messfenster à 100 Queries.
AB/BA sechs Samples pro Zustand; drei AA-Paare ohne Candidateindex separat.
1810 vollständige Queryoracles/18100 Rowkontrollen pro Profil, plus eine getrennte
positive Einquerykontrolle und eine tatsächliche negative Kontrolle. Warmups
ausgeschlossen, keine nachträgliche Sample-/Ausreißerauswahl.

Vollständige fünfteilige eigene Session-/Request-/Startzeit-/Connection-/DB-Identität
bindet tatsächliche monotone CPU (Central Processing Unit; Prozessor)/Reads/LogicalReads/Writes vor/nach dem Loop.
UTC-Elapsed umfasst EXECUTE AS, Queryloop, Ergebnisbuffer/Transfers/Deletes und
REVERT; Countergrenzen zusätzlich enthalten. UTC-/CPU-I/O-Grenzen sind nicht
identisch. Der coarse DMV-datetime-Start ist nur Identität, keine Crossclockordnung;
UTC-Grenzen verwenden denselben datetime2(7)-Takt.

Alle zehn eindeutigen IDs 101–110, Value=Id×3, Ordinal und sämtliche 100 F-Payloadbytes
werden je Query vollständig geprüft, native zehn-Row-SHA256-Digests zusätzlich
gegen die feste UTF-16LE-Referenz gebunden. Fehlende Felder/Counter, Aliaswerte,
doppelte JSON-Keys/Parts, Trunkierung oder unvollständige Population führen zu FAIL;
fehlende Werte werden nicht Null. Das ist ein Readerbatch einschließlich Buffer-/
Impersonationaufwand, keine reine Einzelquerylatenz oder isolierter Indexgewinn.

## Tatsächliche zwei eigene Lifecycles

C1 zweimal bestanden, SQL 17.0.5005.3/EngineEdition3, eigener cached Imagehash
78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726,
vier CPU/sechs GiB, eigener Loopbackport. CL170/SIMPLE, Dateilimits 256/64 MB,
MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad)/PREVIEW_FEATURES beide 0 unverändert. Normalbudget 300 Sekunden,
anschließend insgesamt 60 Sekunden Cleanup. Vollständige bytegenaue vier
Eigentumsmarker vor Mutation/Drop, bekanntes Clientende; UNKNOWN false und keine
Folgeclients bei UNKNOWN. Passwort allein über Umgebung.

Je Profil 46 vollständige 1000-Row-Source-/Reader-/Indexaufnahmen, Setupidempotenz,
tatsächliches DELETE Id1000 → 51003/FAIL_RESULT_CONTRACT → voller Restore.
Querynegative mutiert nach Messende den Ergebnisbuffer Value0 bei Id101/Ordinal1
und erreicht ebenfalls exakt 51003/FAIL_RESULT_CONTRACT; Source bleibt unverändert.
Vier tatsächliche eigene Builds und vier Drops pro Profil durch vollständige native
Indexzustände getrennt bestätigt. Abschließend PK (Primary Key; Primärschlüssel) allein und vollständige Quelle.

92 vollständige Sourceframes/92000 Rows, 58 positive Fensterframes einschließlich
zwei separater Kontrollen und vier native Negative exakt an private Rawframes/
Recordhashes gebunden. Je Profil 93/
93 dokumentierte native Phasencalls. SQL-Markercleanup
und neue unabhängige DB-/Namens-/CID-Abwesenheit bestanden;
Cleanup 12.688/13.105 Sekunden.
Readerrechte/config/source unverändert; keine Cloud-/Modell-/ONNX-/Preview-/roten
Hosteffekte oder andere Repositoryänderung.

## Tatsächliche AB/BA-Readerbatchwerte

ElapsedUs in Mikrosekunden, CpuMs in Millisekunden; I/O-Werte sind Requestdeltas.
Alle Samples/Nullen/Ausreißer bleiben sichtbar. Kein Query-p95/p99, Durchsatz oder
statistischer Nachweis aus sechs kleinen Batchsamples.

| Profil | Candidateindex | Metrik | n | Median | Min–Max | alle Samples |
|---|---|---|---:|---:|---|---|
| 1 | abwesend | CpuMs | 6 | 30.0 | 21–47 | 47, 34, 26, 47, 21, 26 |
| 1 | abwesend | ElapsedUs | 6 | 33104.0 | 24773–49907 | 49691, 37256, 28952, 49907, 24773, 28714 |
| 1 | abwesend | Reads | 6 | 0.0 | 0–0 | 0, 0, 0, 0, 0, 0 |
| 1 | abwesend | LogicalReads | 6 | 11006.5 | 10983–11020 | 10983, 11012, 11020, 11001, 11017, 10997 |
| 1 | abwesend | Writes | 6 | 35.5 | 9–110 | 110, 38, 35, 12, 36, 9 |
| 1 | vorhanden | CpuMs | 6 | 23.5 | 21–32 | 32, 26, 23, 24, 21, 23 |
| 1 | vorhanden | ElapsedUs | 6 | 24578.5 | 24509–33049 | 33049, 28702, 24509, 24607, 24516, 24550 |
| 1 | vorhanden | Reads | 6 | 0.0 | 0–0 | 0, 0, 0, 0, 0, 0 |
| 1 | vorhanden | LogicalReads | 6 | 11005.0 | 10993–11028 | 11006, 10994, 11018, 11004, 10993, 11028 |
| 1 | vorhanden | Writes | 6 | 25.5 | 9–61 | 61, 55, 22, 29, 15, 9 |
| 2 | abwesend | CpuMs | 6 | 28.0 | 23–53 | 28, 28, 23, 53, 23, 30 |
| 2 | abwesend | ElapsedUs | 6 | 30939.5 | 24487–57356 | 29012, 36846, 24487, 57356, 24643, 32867 |
| 2 | abwesend | Reads | 6 | 0.0 | 0–0 | 0, 0, 0, 0, 0, 0 |
| 2 | abwesend | LogicalReads | 6 | 11017.5 | 10983–11037 | 10983, 11037, 11017, 10995, 11020, 11018 |
| 2 | abwesend | Writes | 6 | 31.5 | 10–110 | 110, 38, 10, 25, 22, 42 |
| 2 | vorhanden | CpuMs | 6 | 31.0 | 25–42 | 34, 32, 25, 28, 30, 42 |
| 2 | vorhanden | ElapsedUs | 6 | 32824.5 | 28689–45342 | 36894, 32859, 28689, 32747, 32790, 45342 |
| 2 | vorhanden | Reads | 6 | 0.0 | 0–0 | 0, 0, 0, 0, 0, 0 |
| 2 | vorhanden | LogicalReads | 6 | 10997.5 | 10993–11028 | 11006, 10994, 10993, 11028, 10994, 11001 |
| 2 | vorhanden | Writes | 6 | 23.0 | 15–61 | 61, 55, 15, 15, 16, 30 |

## Getrennte AA-Kontrollpaare

Beide AA-Slots ohne Candidateindex; weder AB/BA zugeschlagen noch nachträgliche
Baselinekorrektur.

| Profil | AA-Slot | Metrik | n | Median | Min–Max | alle Samples |
|---|---:|---|---:|---:|---|---|
| 1 | 1 | CpuMs | 3 | 29 | 23–45 | 29, 45, 23 |
| 1 | 1 | ElapsedUs | 3 | 32956 | 24596–49214 | 32956, 49214, 24596 |
| 1 | 1 | LogicalReads | 3 | 11012 | 11010–11035 | 11035, 11010, 11012 |
| 1 | 2 | CpuMs | 3 | 36 | 30–40 | 30, 40, 36 |
| 1 | 2 | ElapsedUs | 3 | 41069 | 32901–45022 | 32901, 45022, 41069 |
| 1 | 2 | LogicalReads | 3 | 11008 | 10998–11010 | 11008, 11010, 10998 |
| 2 | 1 | CpuMs | 3 | 28 | 26–29 | 26, 28, 29 |
| 2 | 1 | ElapsedUs | 3 | 32750 | 28755–32989 | 28755, 32989, 32750 |
| 2 | 1 | LogicalReads | 3 | 11017 | 10997–11017 | 11017, 11017, 10997 |
| 2 | 2 | CpuMs | 3 | 24 | 23–29 | 23, 24, 29 |
| 2 | 2 | ElapsedUs | 3 | 24595 | 24487–32911 | 24595, 24487, 32911 |
| 2 | 2 | LogicalReads | 3 | 11014 | 10993–11020 | 10993, 11020, 11014 |

## Enger Review, Wiederverwendung und Quellenbindung

Unabhängiger neuer Indexzustands-/Query-/Präfixreview ohne offene P1/P2; Reviewer
ohne Tests/Runtime, keine Reviewkette. Bestehende native Marker-/Source-/Cleanup-
Quellen bytegleich. Der ausgewählte Readerparser stimmt nach ausdrücklich
LF-normalisiertem Vergleich bis auf den neuen Scopepräfix mit dem grün geprüften
Parser überein; keine behauptete Rohbytegleichheit oder alte Suitewiederholung.
Ein neuer positiver SELECT-Transportfall und zwei fremde Scopepräfix-Abweisungen
bestanden. Anfänglicher reiner Fixtureimportfehler vor Testeintritt und roher
CRLF-/LF-Vergleichsfehler bleiben sichtbar; beide behoben, keine Nativeffekte.
Keine zusätzliche Laufkorrektur nötig: C1 mit zwei erforderlichen stabilen Profilen.
Sechs kohärente Kandidaten je lokalem Schnitt bleiben autorisiert; frühere FAILs
werden nicht zurückgesetzt, kein unveränderter Retry.

Ausgewählte Ausführungsquellen vor jedem Lauf gehasht und nach beiden Lifecycles
unverändert geprüft; keine vollständige transitive Importattestation:

| Quelle | SHA256 |
|---|---|
| `Runtime/DGN010_SELECT/sources/10_Setup.sql` | `9a462b1e805711d6254105ec5d84966943e6547703ab458386b89bff7f06ea47` |
| `Runtime/DGN010_SELECT/sources/20_Probe.sql` | `5b5a52e1059beeb053d565a9310a0a254c6d44b75164caa3880e1ca16ea8c862` |
| `Runtime/DGN010_SELECT/sources/40_Window.sql` | `83a02a826227cdc4daca48e15b5237f5d6d3aaf0f853fd98ae952535fb2d815b` |
| `Runtime/DGN010_SELECT/sources/90_Cleanup.sql` | `129894ffc2a7eea35f5c26bbe40d0b328674329e344e72929922abfa029c1b84` |
| `Runtime/DGN010_SELECT/sources/guard.sql` | `69ab06578c30d17432bc335b7c5ec399ab1d137d1260de016e65c139f881a9e2` |
| `Runtime/DGN010_SELECT/qualify.py` | `9ddd4fda1baa92c1e1dba562431094f056d12b6299330dd005121e71c47e243f` |
| `Runtime/DGN010_SELECT/probe.py` | `6adbb3884bf9a1560f54921e72fba13524543d9f800c095a0ed9e6a15f749e7d` |
| `Runtime/DGN010_SELECT/source_evidence.py` | `b51a7d2a65eae1a12561b00bed4e962a88a0abdf47a8d5ee58cecf4b0a461211` |
| `Runtime/DGN010_SELECT/measurement.py` | `4af310f44034e3a6b504c64c099346e613cc1fc247718f1700b44659fe4ed051` |

Die Messwerte beantworten nur den festen ungezwungenen Readerbatchvergleich
ohne/mit Candidateindex mit Buffer-/Impersonationaufwand. Eine Advicehypothese
wird dadurch allein weder allgemein bestätigt noch widerlegt. Indexnutzung der
aktuellen Fenster, individuelle Latenz, Indexnettonutzen einschließlich DML (Data Manipulation Language; Anweisungen zum Lesen oder Ändern von Daten)/Build,
isolierte Query-/Index-/vollständige Workerkosten, öffentliche FWK-/Versions-/
Recoveryqualifikation und volle TP-PERF-/TSK-011-/Modulabnahme bleiben offen.
DGN-010 PROPOSED; Modell-/Tokenverbrauch unbekannt, Heartbeat aktiv.

Aktuelle Head-/Main-Gates, PR/Integration, ganze Treeübernahme, FF-Sync und eigener
lokaler/Remote-Branchcleanup folgen vor Abschluss. Nächster begrenzter kanonischer
Schritt bereitet das öffentliche DGN-010-Demopaket mit getrennten Messscopes vor.
