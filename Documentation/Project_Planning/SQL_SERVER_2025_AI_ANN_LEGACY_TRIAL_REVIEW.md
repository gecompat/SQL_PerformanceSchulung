# TSK-006 – begrenzter Legacy-Signaturversuch

Stand: 2026-10-11. SEARCH_RESULT_PASS_AT_FIXED_BUILD im zweiten Kandidaten,
GENERATION_UNKNOWN und INDEX_USAGE_UNPROVEN. Erster Kandidat FAIL erhalten.
Maßgeblich ist der [autorisierte Diagnoseumfang](SQL_SERVER_2025_AI_ANN_LEGACY_TRIAL_DECISION.md):
höchstens zwei neue Kandidaten/vier serielle eigene Container und höchstens zwei
vollständige Lifecycles eines positiven stabilen Kandidaten. Die zusätzliche
Benutzerfreigabe autorisiert notwendige lokale Folgeschritte dieser Entwicklungswelle.
Historische Budgets/FAILs bleiben erhalten; keine numerische Generation ableiten.

## Erster Kandidat

Genau ein neuer eigener Container/Lifecycle. Die beiden tatsächlichen Baselines
waren Preview 0 und DB-scoped MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad) 0; neue Clients attestierten nach getrennten
Setclients die Werte 1/1. Buildsession QUOTED_IDENTIFIER 1. CREATE VECTOR INDEX
lieferte die vollständige eigene Metadatenrow mit Typ 8/VECTOR, DiskANN/COSINE,
gültigen Buildparametern ohne Versionsschlüssel.

Der anschließende DATALENGTH-/varbinary-Vergleich mit varchar-Literalen stoppte
mit 51003 vor dem Versionsprofilmarker und vor VECTOR_SEARCH. Die angezeigten
Textwerte allein belegen den tatsächlichen Speichertyp nicht. Keine Such-, Recall-,
Indexnutzungs-, Generation- oder Performancequalifikation aus diesem Lauf.

Beide tatsächlichen Restores 0/0, neue Attestierung vor DB-Drop, separater SQL-Client
für DB-Abwesenheit und voll gebundener Containerabbau mit zusätzlicher Abwesenheit
bestanden. Cleanup 12,297 Sekunden, Prozesscode 1. Ausgeführte Quellen unverändert.

| Private Quelle unter ANN_LEGACY_TRIAL_CANDIDATE01 | SHA-256 |
|---|---|
| qualify_build.py | 670944AFA4799EFCAC01592C277E76EEB787F29389095ABF9E78DAC7D08F3443 |
| sql_build.py | 70C2424A2F3EC77C84A3FED72E7CE0C18098B5183776E7FBC1610ADB8914CC7F |
| test_build.py | 8DBADF75761657459E414C103149B2C37C995A751046583EEEC32D1BFF72D697 |
| lifecycle01.log | 52AF07DBF0EBDD800093139EAB9A4F816B6D10129BFA8A75EAABDC8298EDED0A |

## Zweiter Kandidat und Prüfgrenze

Der zweite erlaubte Kandidat erfasst die tatsächlichen Textspeichertypen und
Byte-Längen vor dem Guard. Beide ASCII-Werte werden in unveränderter Unicodeform
mit DATALENGTH und vollständigen varbinary-Bytes verglichen; keine Case- oder
Whitespaceangleichung. Eine echte varchar-/nvarchar-Positive und zehn feste
Textwertnegative liegen vor dem einzigen festen Legacy-Suchaufruf. Der vollständige
rohe Indexmetadatenvergleich bleibt erhalten. Ergebnis-/Quell-/Marker-/duale
Baseline-/Konfigurations- und Cleanupgrenzen bleiben unverändert.

Zwei lokale Generator-Testfehler durch implizite Windows-Decodierung wurden vor
SQL korrigiert; der anschließende Fünf-Test-Lauf bestand. Kein Containerverbrauch
durch diese lokalen Tests. Der enge unabhängige Review des tatsächlichen Deltas
fand keine konkreten P1/P2; Quellengate vor SQL geschlossen.
Im ersten tatsächlichen Lifecycle des zweiten Kandidaten sind beide Katalogwerte
nvarchar (14/12 Bytes); dies erklärt den vorherigen Speicherformvergleichsfehler.
Die feste Legacy-Signatur lieferte fünf distanzgeprüfte tatsächliche Quell-IDs;
Schnittmenge mit dem Exact-Oracle 5/5. Eigener Indexdrop, tatsächliche Restores 0/0,
neue Attestierung und separate DB-/Containerabwesenheit bestanden; Cleanup
12,383 Sekunden. Der ausdrücklich vorgesehene zweite Lifecycle mit unveränderten
Quellen bestand dieselben Kontrollen; Cleanup 12,710 Sekunden. In beiden Läufen
waren die distanzgeprüften Exact-/Approx-IDs 23, 40, 6, 63, 46. Tatsächliche
Schnittmenge 5/5 am festen Korpus und einem Queryvektor, kein Recallversprechen
für andere Daten/Queries. Keine Plan-/Indexnutzungsevidenz, Generation bleibt UNKNOWN.

Je Lifecycle bestanden vier vollständige Snapshots mit je 107 Host-/41 DB-scoped-
Konfigurationsrows, vollständige 1000-Row-JSON-/numerische Quellbindung, 24 Marker-,
neun duale Baseline-, drei Ergebnis-, drei Quell- und zehn neue Textwertgegenproben.
Vollständige Indexmetadaten vor/nach Search unverändert; eigener Indexdrop und
tatsächliche Indexabwesenheit belegt. Beide gespeicherten Originalwerte 0/0 wurden
tatsächlich wiederhergestellt und in einem neuen Client vor DB-Drop attestiert.
Separate SQL-DB- und Containerabwesenheit bestanden jeweils, Prozesscodes 0.

| Private Quelle unter ANN_LEGACY_TRIAL_CANDIDATE02 | SHA-256 |
|---|---|
| qualify_build.py | 4C963C8BECAEFE48E168B6A50CC3373035ACDD150B703EF827BC730A61BFAE23 |
| sql_build.py | 757F82E8AB370F7242F06ED2D4026E91CF3967F71FB99BE630FECB33EA70F6D3 |
| test_build.py | 8DBADF75761657459E414C103149B2C37C995A751046583EEEC32D1BFF72D697 |
| lifecycle01.log | 56A4BDF0E62A376F12C1116C0B97BEB9160B2EA79C5CE31A35A56832ED9E444E |
| lifecycle02.log | B2CAD186C2E2EADA8B549FD7592E6FCD5765EEC864D9EE0C6529E860CD852669 |

Zwei Kandidaten und drei Container/Lifecycles verbraucht. Kein weiterer Lauf
dieses Diagnoseumfangs erforderlich. Der nächste eigene
[Planausgabeschnitt](SQL_SERVER_2025_AI_ANN_PLAN_DECISION.md) trennt tatsächliche
Planbeobachtung und Indexnutzung von diesem Ergebnisnachweis. Vollständige
IDX-011-/IDX-012-Abnahme, gefilterte Queries, Laufzeit-/IO-/CPUvergleich und DML (Data Manipulation Language; Anweisungen zum Lesen oder Ändern von Daten)
bleiben offen; keine Azure-/andere Buildqualifikation.

Ein Implementierungsverantwortlicher, ein erforderlicher Reviewer; unveränderte
gültige Analysen werden wiederverwendet. Modell-/Tokenverbrauch bleibt unbekannt.
