# DGN-007 – Runtime-Nachweis der neutralen Kontrollcaptures

| Merkmal | Wert |
|---|---|
| Status des Schnitts | `IMPLEMENTED` mit lokalem Runtime-Nachweis |
| Umfang | ausschließlich `DGN-007_CONTROL_AB`, `DGN-007_CONTROL_BA`, `DGN-007_CONTROL_AA`, Run-Token `AUTO` |
| Ausführungsdatum | 2026-10-07 Europe/Vienna (2026-10-06 UTC) |
| Repository-Basis | `c21b20738204e6c477ca1d7fa981b6cd8b4fdf79` mit den Änderungen dieses PR |
| Infrastruktur | frische Linux-Docker-Wegwerfinstanzen, vier CPU-Kerne, 8 GB Container-Speicher, keine veröffentlichten Ports oder Host-Volumes |
| CI-Abgrenzung | lokale Runtime und Actions-Ergebnisse werden getrennt bewertet |

## Kontrollvertrag

Die drei unveränderlichen Runner-Scopes führen jeweils zweimal Preflight,
Setup, Datenassertion, feste Kontrollkonfiguration, zwei Query-Store-Fenster,
den bestehenden neutralen Profilvergleich, Kontrollevidenz und Cleanup aus.
Jede Phase muss `PASS/OK` liefern; fehlende, doppelte, nicht erfolgreiche oder
anders angeordnete Phasen werden zurückgewiesen. Die bisherigen drei Scopes
und ihre SQL-Batches bleiben unverändert. Das reguläre Budget beträgt weiter
180 Sekunden und Cleanup unabhängig 60 Sekunden. Der CI-Job hat 100 Minuten
äußeren Schutz für zwölf Lifecycles einschließlich Abwesenheitsprüfungen,
Readiness und begrenzter Recovery; dies verändert keine SQL-Phasenbudgets.

Die feste Konfiguration wird erst nach exakter Prüfung aller vier vollständigen
Eigentumsmarker, Developer-/Versions-/Compatibility-Vertrag und isoliertem
frischem Zustand in `lab.ControlSequence` angelegt. Nur AB, BA und AA sind
zulässig. A verwendet `(8,3)`, `(1,3)`, `(5,3)`, `(1,1)`; B verwendet `(1,3)`,
`(8,3)`, `(5,3)`, `(1,1)`. Je Fenster bleibt derselbe Vierermix mit vollständigem
bidirektionalem Ergebnisvertrag, vier regulären Suchausführungen und 4.229
Ergebniszeilen erhalten. WindowId 0 und 1 bleiben die chronologischen T0/T1;
auch bei BA ist das Profil-Delta weiterhin T1 minus T0.

Der neue Fensterbatch übernimmt den bisherigen geprüften Fenstervertrag.
Ausschließlich Kontrollkonfiguration und Parametermapping unterscheiden sich
im ausführbaren Code. Ein statischer Vergleich prüft diese Beschränkung
zusätzlich zu den ursprünglichen Snapshot-, Polling-, Capture-, Scope-,
Ownership- und Deadline-Prüfungen. Keine festen Wartezeiten ersetzen die zwei
disjunkten beobachteten Katalogintervalle. Vor jedem Fenster wird ausschließlich
die eigene markierte Suchprozedur objektbezogen mit `sp_recompile` vorbereitet.

Nach dem bestehenden gewichteten Profilvergleich prüft der neue lesende Batch
die tatsächliche Aufrufreihenfolge aus `CaseRequestLog` gegen die gewählte
Konfiguration in beide Richtungen. Er revalidiert eigene Parent-/Query-/Plan-
Bindung, positive reguläre Ausführungen, exakte Counts und Zeitgrenzen.
Die zusätzliche Planmenge enthält nur ausgeführte T0/T1-Pläne. Historische
ungenutzte Pläne und Dispatcher erweitern sie nicht. Der versionsgebundene
Dispatcher-Guard bleibt auf 2019 vollständig außerhalb statischer Bindung.
Eine Mindestplananzahl oder Metrikrichtung ist nicht erforderlich.

Die festen skalaren Reports zeigen Bedingung je Fenster, Parent-/Query-/Plan-IDs,
8-Byte-Planhash und die Vereinigungsmenge mit getrennten T0-/T1-Ausführungsflags.
Ein Plan je Fenster beweist weder gleiche noch verschiedene Plan-IDs. Hashes
ergänzen die IDs, begründen aber keine identischen Kosten oder Ursache.
IDs sind ausschließlich innerhalb des jeweiligen Lifecycles vergleichbar.
Die Kontrollevidenz liest keine Plan-XML-Inhalte und exportiert oder persistiert
keine Querytexte, Plan-XML oder Rohausgaben als Repository-Artefakte.
Query Store erfasst Texte und Pläne innerhalb der eigenen Labdatenbank;
dieser Zustand endet mit deren markergebundenem Abbau.
Der Live-Abgleich prüft IDs, Counts und Grenzen, nicht unabhängig
die bereits gespeicherten Metrikmittelwerte. Beobachtungsqueries können unter
Capture ALL selbst erfasst werden; sie gehören nicht zum markierten Suchscope.

## Lokale Matrix und Cleanup

Die lokale Matrix führt auf jeder neu erzeugten eigenen Instanz dieselbe
Reihenfolge wie CI aus: zweimal Datenmodell, zweimal Fenster, zweimal
Profilvergleich und je zweimal AB, BA und AA. Höchstens zwei eigene Instanzen
laufen parallel, je Instanz höchstens eine SQL-Session. Vor jedem Lifecycle
ist die eigene Datenbank abwesend; nach jedem folgt eine unabhängige Prüfung
gegen `master`. Vor Containerabbau werden ursprüngliche ID und eindeutiges
Eigentumslabel geprüft, danach die ID-Abwesenheit unabhängig bestätigt.
Bestehende Ressourcen werden nicht als Testziele verwendet.

Alle 36 Lifecycles bestanden einschließlich unabhängiger Datenbankabwesenheit.
Davon prüfen 18 die neuen Kontrollcaptures und 18 die bisherigen Verträge
in derselben Reihenfolge. Alle drei eigenen Container wurden nach ID-/Label-
Prüfung einschließlich anonymer Volumes entfernt. Ihre ursprünglich festgehaltenen
IDs wurden anschließend nochmals unabhängig als abwesend bestätigt.

| SQL Server | ProductVersion | Engine Major | Compatibility Level | AB / BA / AA | Ergebnis |
|---|---|---:|---:|---|---|
| 2019 | `15.0.4490.9` | 15 | 150 | je zwei Lifecycles | `PASS/OK` |
| 2022 | `16.0.4265.3` | 16 | 160 | je zwei Lifecycles | `PASS/OK` |
| 2025 | `17.0.4075.5` | 17 | 170 | je zwei Lifecycles | `PASS/OK` |

Die lokal vorhandenen offiziellen Images wurden über unveränderliche Digests
verwendet; bestehende Tags und Ressourcen blieben unangetastet:

| SQL Server | Image-Digest |
|---|---|
| 2019 | `mcr.microsoft.com/mssql/server@sha256:ef0b8db33970ecd01bed49c3a84a1d083c435a9891718df619298b67b352e74a` |
| 2022 | `mcr.microsoft.com/mssql/server@sha256:ba4c8329f48fb8f02e1416be6a930ebfd71268caee78aa985f3af4315e457c89` |
| 2025 | `mcr.microsoft.com/mssql/server@sha256:4bab24f36c1ecd48e85f7d37df26e6bf301641d84c3fe652f9a0dcc947d512e1` |

Ausgaben wurden ausschließlich transient gelesen
und auf feste numerische Reports, A/B-Bedingungen und hexadezimale Hashes
begrenzt; Rohoutput und Zugangsdaten werden nicht persistiert. Der normale
Runner unterdrückt unverändert die SQL-Phasenausgaben.

## Skalare Beobachtungen und statische Gegenprüfungen

Die Werte sind gewichtete Mittelwerte je chronologischem Fenster; keine Golden
Values, Schwellen oder Incidentabnahme. Jede Tabellenzeile besitzt vier reguläre
Ausführungen und 4.229 Ergebniszeilen je Fenster. AB und BA zeigen je einen Plan
pro Fenster, zusammen zwei unterschiedliche ausgeführte Plan-IDs und Hashes.
AA zeigt je einen Plan pro Fenster und dieselbe Plan-ID in beiden Fenstern.
Die beobachteten Hashes waren für A `0x2b0c9b54e639aab5` und für B
`0x70c7888694fc74a5`; diese Werte sind keine festgeschriebenen Erwartungen.

| SQL Server | Folge | Lauf | Duration T0 / T1 (µs) | CPU T0 / T1 (µs) | Logical Reads T0 / T1 (Pages) |
|---|---|---:|---|---|---|
| 2019 | AB | 1 | 6311,25 / 10919,25 | 6311 / 10918,25 | 5896 / 3380 |
| 2019 | AB | 2 | 6104,75 / 12841,25 | 6104,5 / 12840 | 5905 / 3387 |
| 2019 | BA | 1 | 8574 / 7418,75 | 8573,25 / 7417,75 | 3379,25 / 5908 |
| 2019 | BA | 2 | 10175,75 / 6718,75 | 10175,25 / 6718 | 3388,5 / 5901,25 |
| 2019 | AA | 1 | 6159,75 / 6981,75 | 6159,25 / 6981 | 5900,5 / 5906,25 |
| 2019 | AA | 2 | 8344 / 6630,5 | 8343,25 / 6630 | 5905,75 / 5901,25 |
| 2022 | AB | 1 | 6679 / 14698,5 | 6678 / 14697,75 | 5906,5 / 3379,25 |
| 2022 | AB | 2 | 6483,5 / 12275,5 | 6483 / 12274,5 | 5899,5 / 3384,5 |
| 2022 | BA | 1 | 9561,75 / 6942,25 | 9560,75 / 6941,5 | 3380 / 5908,75 |
| 2022 | BA | 2 | 11560 / 7511,75 | 11559 / 7511 | 3376,5 / 5908 |
| 2022 | AA | 1 | 6013,75 / 7268,25 | 6013 / 7268 | 5907,25 / 5907,25 |
| 2022 | AA | 2 | 6462,25 / 7013,5 | 6462 / 6978,5 | 5905,75 / 5907,5 |
| 2025 | AB | 1 | 5280 / 11181,5 | 5279,5 / 11180,75 | 5907,25 / 3380,75 |
| 2025 | AB | 2 | 7705,75 / 9572 | 7705 / 9571,5 | 5900 / 3380,25 |
| 2025 | BA | 1 | 10855,75 / 8847,5 | 10854,75 / 8846,75 | 3380,25 / 5906,25 |
| 2025 | BA | 2 | 9390,25 / 6813,5 | 9389,75 / 6812,75 | 3383,25 / 5900,25 |
| 2025 | AA | 1 | 6653,5 / 6760,75 | 6653,25 / 6760,25 | 5897,75 / 5898,75 |
| 2025 | AA | 2 | 6648 / 6344 | 6646,75 / 6343,25 | 5897,75 / 5900,5 |

Alle B-A-Duration-Kontraste sind positiv. Das genügt allein nicht: Auf 2019
beträgt der erste BA-Kontrast 1.155,25 µs, während der absolute zweite AA-Drift
1.713,5 µs beträgt. Diese konkrete Überlappung begründet keine klare Separation
für alle Versionen und darf nicht durch eine nachträgliche Schwellenwahl
überdeckt werden. Die vorliegenden Captures sind explorative Kontrollbelege,
keine prospektiven Bestätigungsläufe einer bereits implementierten Incidentregel.
Alle Runtime-Baselines waren positiv; der Zero-Baseline-Zweig bleibt durch
die getrennten numerischen Profilfixtures geprüft.

36 Runner-Tests, zwölf neue tatsächliche SQL-Kontrollfixtures, zehn Profil-
und acht Compatibility-Tests bestanden. Die neuen SQLite-Fixtures extrahieren
Parametermapping, echte Requestreihenfolge, aktive Planbasis und Union aus dem
ausgeführten SQL. Sie prüfen gleiche beziehungsweise verschiedene Plan-IDs
bei einem Plan je Fenster, ungenutzte Dispatcher, ungültige Bedingungen,
Counts, Hashes, fremde Queries und entfernte NULL-/Deadline-/Scope-Guards.
SQLite ersetzt keine T-SQL-Syntax- oder Query-Store-Katalogprüfung; dafür
ist die getrennte SQL-Server-Matrix maßgeblich. Alle vier DGN-007-Validatoren
sowie relevante Framework-, Foundation-, Registry-, Privacy-, Readiness-
und Kontinuitätsprüfungen bestanden. Foundation-Grün belegt nur Integration.

## Abnahmegrenzen und Quellen

Ein Kontrollcapture-PASS belegt ausschließlich die funktionsfähigen Last-,
Fenster-, Profil-, Sequenz-, Plan- und Cleanup-Verträge. Metrikdeltas sind
Beobachtungen ohne Richtungsgate. Die AA-Läufe erfassen konkrete lokale
Variation; sie ergeben keine allgemeine Messunsicherheit oder statistische
Signifikanz. A und B ändern zugleich Erstparameter nach `sp_recompile` und
Aufrufreihenfolge. Auch Gegenreihenfolge und AA isolieren keine Kompilierungsursache.
Ein abschließender Planmetadaten-Snapshot liefert keinen phasenspezifischen
kompilierten Parameter.

Der nächste Reproduktionsschnitt benötigt vor seiner Runtime-Ausführung
prospektive Akzeptanzregeln: gewichtete Statement-Duration als primäre
zeitbezogene Metrik, CPU und Reads als getrennte ergänzende Befunde,
gerichteter B-A-Kontrast unter AB und BA sowie begründete Separation gegenüber
AA-Variation. DirectedSymptom und Plan- oder klar unterscheidbare Runtimeprofile
müssen getrennt begründet werden. Eine bloße Plananzahl, beliebige steigende
Nebenmetrik oder nachträglich ausgewählte Ratio ist kein Incidentgate.
Fehlende tragfähige Evidenz ergibt beim späteren Schnitt den bestehenden
`SKIP_EVIDENCE_MISSING`-Ausgang; er ist kein erfolgreicher Incidentnachweis.

Der übergeordnete DGN-007-Status bleibt `IMPLEMENTED_STATIC_SLICE_B`.
Kontrollierter Incident, ältere LOCAL-Last mit bisherigem 3/5-Mix und deren
Beobachtungsbedingung, phasenspezifischer Compilekontext, Alternativhypothesen,
Request-/XE-Evidenz, Mitigation und T2 bleiben offen. Es erfolgt keine
Szenariopromotion, vollständige Capstone-Matrix oder `READY_FOR_USER`-Übergabe.

Technische Primärquellen, geprüft am 2026-10-06:
[Query-Store-Runtime-Stats](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17),
[Planmetadaten](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17),
[sp_recompile](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-recompile-transact-sql?view=sql-server-ver17).
Runtime-Stats zählen erfolgreiche Ausführungen gesondert und verwenden
Abschlusszeitpunkte. Duration und CPU sind Statement-Runtime in Mikrosekunden,
Reads zählen 8-KB-Pages; Compilekosten und Clientlatenz werden nicht abgeleitet.
`sp_recompile` veranlasst die nächste Kompilierung, belegt deren Ergebnis aber
nicht. Fachlicher Vertrag bleibt [ADV-007](ADV_007_LAB_VP5_DESIGN.md).
