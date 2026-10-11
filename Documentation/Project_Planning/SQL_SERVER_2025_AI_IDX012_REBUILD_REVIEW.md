# IDX-012 – Drop-/Änderungs-/Rebuildcheckpoint

Stand: 2026-10-11. Beide Runtimekandidaten FAIL; Freshness nicht attestiert.
TSK-006 und vollständige Demoabnahme bleiben offen.

## Beendete ursprüngliche Welle

Umfang: höchstens zwei kohärente Kandidaten/vier eigene serielle Container,
zwei positive Lifecycles am stabilen Kandidaten. Tatsächlich: zwei Kandidaten,
zwei Container, kein erfolgreicher Drop-/Änderungs-/Rebuild-Lifecycle.
Quellenreview des zukünftigen öffentlichen Deltas ohne offene Methodenbefunde;
tatsächliche Promotion, öffentliche Importpfade und Hashbindung vor Admission
bestätigt. Vierzehn Controller-, zunächst dreizehn Lifecycle- und zehn Selector-
gegenproben bestanden. Die synthetischen Tests attestieren keine SQL-Kompilation.

| Tatsächlicher Lauf | Befund | Cleanup ab erstem Restore |
|---|---|---|
| Kandidat 1 E2EE1E999C104A0A | 50_DropRebuild: Parser 156/State 1 bei RowCount, 102/State 1 bei IndexCount; neuer Batch nicht ausgeführt | 12,671 s |
| Kandidat 2 E095EBFA02D548F0 | nach eng geprüfter Aliasquotierung: 50_DropRebuild liefert 42231/State 1 am UPDATE; kein erfolgreicher Commit-/Rebuildbefund | 12,155 s |

Beide Läufe: 17.0.5005.3, eigene IDX-012-DB/Marker, 999 VECTOR(3)-Rows,
vier CPUs/sechs GiB, gleiches vorhandenes Image wie im DML-Grenzenbefund.
Die vorangehenden vier erfolgreichen DML-Kontrollen ohne Index und vier
tatsächlichen Verweigerungen mit Index bestanden. Beide Originalbaselines
Preview/MAXDOP 0/0 tatsächlich restauriert; separate DB- sowie eigene CID-/
Namensabwesenheit bestanden. Beide Admissionen geschlossen mit tatsächlichem FAIL.

Kandidat 2 änderte ausschließlich [RowCount]/[IndexCount]. Enger unabhängiger
Review bestätigte unveränderte JSON-Felder und Wirkungen. Seine SQL-SHA256:
0cc40dad6b3c661e83ae7208864e73234d0588161189ff5d346e42d410042b2d.
Der Rohoutput enthält keine abgeschlossene Lifecycleaufnahme. Ob der Drop vor
42231 tatsächlich ausgeführt wurde, ist mit dieser Ausgabe nicht attestiert.
Eine Bindung der statischen DML an den vorher vorhandenen Index ist eine
Hypothese; das tatsächliche Compile-/Dropverhalten bleibt zu diagnostizieren.
Generation UNKNOWN, Freshness NOT_ESTABLISHED, keine Rebuild-/TP-PERF-Abnahme.

Das ursprüngliche Zweikandidatenbudget ist beendet. Keine dritte Admission
oder unveränderte Wiederholung im alten Runner. Vollständige Rohoutputs und
Quellenlisten bleiben lokal unter Runtime; keine Geheimnisse/Rohlogs im Git.

## Konkreter getrennt vorbereiteter Compile-Folgeschritt

Die weitere ausdrückliche lokale Wellenfreigabe autorisiert die begrenzte Folge;
das ursprüngliche Budget und die FAILs werden nicht zurückgesetzt. Admission
erst nach Integration dieses Checkpoints, aktueller enger Quellenreviewclosure
und tatsächlicher Pfad-/Hashbindung.

Neuer eigener Parent/Ledger: genau ein Kandidat, höchstens zwei eigene serielle
Container für die zwei weiterhin erforderlichen positiven Lifecycles. Keine
Korrekturwelle; bei Fehler Stop und neuer Checkpoint. Gleicher fester Build,
Image, 999 Rows, VECTOR(3), vier CPUs/sechs GiB, eigene Preview/MAXDOP mit
tatsächlichen Baselines/Restore. Startup im 300-s-Normalbudget; 20-s-SQL-
Recovery im gemeinsamen 60-s-Cleanup. Keine weitere Option, Provider-, Cloud-,
ONNX-, Imagepull- oder Host-/Fremdänderung.

Konkrete Änderung: nach eigenem Drop wird ein vollständiger eigener Datensatz
mit tatsächlichen Indexcount null, Rowcount 999 und Transaktionswerten 0/0
ausgegeben. Erst danach kompiliert ein festes parametrisiertes sp_executesql
das UPDATE Id 999 im unteren Scope; @@ROWCOUNT wird dort tatsächlich erfasst.
Commit-, Quellen-, Such-, Rebuild- und Recoveryoracles bleiben erhalten. Der
Consumer verlangt zusätzlich genau diesen ersten Dropdatensatz. Vierzehn
synthetische Lifecyclegegenproben einschließlich falscher Drop-/Transaktions-
werte bestanden; sie beweisen noch keinen erfolgreichen Compile-Folgelauf.

Das öffentliche CLI beschreibt diesen Modus als noch nicht qualifizierte
Vorstufe. Der Default dml-boundary bleibt ohne dauerhafte Änderung. Bei einer
zukünftig tatsächlich erfüllten Folge kann ausschließlich Freshness
OBSERVED_AFTER_REBUILD_ONLY berichtet werden, niemals allgemeine DML-/
Indexgeneration-/laufende Aktualisierungsunterstützung.

Der erforderliche enge unabhängige Quellenreview schloss ohne P1/P2.
SHA256 der geprüften Folgequellen:

- 50_DropRebuild.sql: 14fd46abe695e4100733891f08e6081599fa8943957f9150c3756d8e68685795
- lifecycle_evidence.py: 3629cfdaf3d237e056fa0cf682570dfb0a33e114397ddf8a111ae27e032b84bf
- run_profile.py: 7f81718bcfc45bf3db79df0e2e71d39605722ebb4f3eeed75aa7e3344b97b05d
- getrennter Compile-Parent: d09329f2a3056dce7bbda9e0c91b12210db33f649a8950eb3b7b23fecbbbfa17

Nur Quellenreview; keine Runtime durch den Reviewer. Checkpointintegration und
tatsächliche aktuelle öffentliche Import-/Hashbindung bleiben vor Admission Pflicht.

Aufwand: ein Owner, erforderliche enge Reviews zu den tatsächlichen neuen
Befunden; keine Reviewkette, keine Wiederholung grüner unveränderter Tests.
Neuer statischer Lifecycle-Test im vorhandenen KI-Job; Runtimejobdefinition
unverändert. Bestehende konservative acht-Demo-KI-Matrix bleibt Head-/Main-Gate,
keine neue IDX-012-Abnahme. Modell-/Tokenverbrauch bleibt unbekannt.
Quelle SRC-077: [CREATE VECTOR INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-vector-index-transact-sql?view=sql-server-ver17),
Abruf 2026-10-11; konkrete Fehler stammen aus den beiden eigenen Läufen.
