# DGN-010: Readerplan-Folgewelle mit nativer UTC-Auflösung

Status: PROPOSED; begrenzte private Actual-Readerplanbeobachtung PASS,
keine vollständige TP-PERF-Abnahme.

[PR 200](https://github.com/gecompat/SQL_PerformanceSchulung/pull/200) hat die
[erste Readerplanwelle](SQL_SERVER_2025_AI_DGN010_READER_PLANS_REVIEW.md) vollständig
als FAIL integriert: sieben aktuelle Head-/fünf Main-Workflows PASS, exakte ganze
Treeübernahme, FF-main und eigener lokaler/Remote-Branchcleanup abgeschlossen.
Die sechs tatsächlichen FAIL-Lifecycles und ihre Sourcehashes bleiben unverändert.

## Autorisierte Fortsetzung und sichtbarer Folgecheckpoint

Der Benutzer hat weitere Freigaben dieser lokalen Entwicklungswelle bereits
erteilt und anschließend ausdrücklich mehr als zwei Testzyklen verlangt.
Das autorisiert die konkrete lokale Sourcekorrektur ohne erneute gewöhnliche
Budgetfrage. Die erreichte erste Sechsergrenze wird nicht zurückgesetzt.
Diese neue zusammenhängende Folgewelle verwendet kumulativ C7–C12, höchstens
zwölf weitere serielle eigene Container; mit den sechs geschlossenen bisherigen
Containern höchstens 18. Zwischencheckpoint C9, harte Grenze C12. Zwei frische
stabile vollständige positive Lifecycles desselben unveränderten Kandidaten
sind weiterhin erforderlich. Retry nur mit geänderter relevanter Source oder
neuer Evidenz; historische Admissions werden nicht ersetzt oder entfernt.

Der neue Controller lässt ausschließlich C7–C12 zu und prüft vor Admission die
vollständig erhaltenen sechs alten FAILs einschließlich tatsächlicher DB-/CID-
Abwesenheit und bekanntem Clientende. Ein Implementierungsverantwortlicher,
enger unabhängiger Review ausschließlich der neuen UTC-Zuordnungsgrenze.
Modell-/Tokenverbrauch unbekannt. Keine weitere Kontroll- oder Reviewkette.

## Tatsächlicher Befund und begrenzte Änderung

C6 lieferte das Originalreader-XE-Ereignis 2026-10-12T09:15:54.768Z, während
die beiden tatsächlichen SQL-UTC-Felder 2026-10-12T09:15:54.7684718 lauteten.
Die Quellen enthalten unterschiedliche Nachkommastellen. Der alte Vergleich
behandelte die Millisekundenrepräsentation als genauere Zeit und lehnte sie ab.

Die Folgequelle verlangt das tatsächlich gelieferte feste Nativeformat mit
genau drei Nachkommastellen und UTC-Z. Sie vergleicht das Ereignis mit den
Millisekunden-UTC-Buckets des unveränderten ursprünglichen Readerintervalls.
Keine beliebige Toleranz, keine neuen Abfragen, keine veränderten Messzeitpunkte
und keine aus diesen Zeitfeldern abgeleitete Querydauer. Vorangehender oder
nachfolgender Millisekundenbucket, verkehrtes Intervall oder anderes Nativeformat
werden abgewiesen. Die Zeitprüfung bleibt eine zusätzliche Zuordnungskontrolle;
die vollständige tatsächliche Source-/Preparedtext-/Parameter-/Request-/DB-/
Session-/Stackoffset-/Root10-/Source10-Bindung bleibt unverändert erforderlich.

## Unveränderte Sicherheits- und Ergebnisgrenzen

Alle im ersten Teilvertrag begrenzten Effekte gelten weiter: neuer eigener
SQL-17.0.5005.3-Container, vier CPU/sechs GiB/Loopback, höchstens 1000 synthetische
Source-Rows, Originalquery/MAXDOP1 und Reader CONNECT/SELECT unverändert.
Vollständige vier bytegenaue DB-Eigentumsmarker; tatsächliche kurzlebige gebundene
XE-Definition vor jedem DROP einschließlich CATCH; vollständiger Ring ohne
Verlust/Trunkierung/Verdrängung. Eigene Native-Stacktextaufnahme und vollständige
Source-/State-/Negativoracles, alle drei Sitzungen zusätzlich frisch unabhängig
abwesend, SQL90/91/frische DB-/CID-/Namensabwesenheit. Gemeinsames 300-Sekunden-
Normalbudget und einmaliges 60-Sekunden-Recoverybudget, sticky UNKNOWN.
Keine neue DB-/Hostkonfiguration, keine zusätzlichen Readerrechte, Cloud-,
Bezahl-API- oder ONNX-Aufrufe; andere Repositories bleiben unverändert.

Fünfzehn betroffene reine Methoden bestehen einschließlich der tatsächlich
beobachteten UTC-Kombination und negativer Format-/Bucket-/Intervallfälle.
Ein reiner oder unabhängiger Quellenabschluss ersetzt keinen Native-PASS.
Originalframes bleiben privat; veröffentlicht werden nur datensparsame Aggregate.
Öffentliche Producer bleiben Gesamt-WARN, DGN-010 PROPOSED; volle Runtime-/
TP-PERF-/Indexnettonutzenabnahme offen. Parallele explizit angeforderte KI-
Schulungsfolien ändern diesen Laufzeitstatus nicht.

## Integration und Weiterarbeit

Nach tatsächlichem lokalem Ergebnis folgen betroffene Privacy-/Linkkontrollen,
aktuelle Head-/Main-Gates, PR nach origin/main, ganze Treeübernahme, FF-Sync und
eigener lokaler/Remote-Branchcleanup. Im Anschluss unmittelbar nächster zulässiger
offener Schritt; Workstream und Heartbeat bleiben aktiv. Allgemeine Entwicklung,
DGN-007 und andere Automationen werden nicht wieder aufgenommen.

## Enger Quellenabschluss vor C7

Unabhängiger UTC-/Fortsetzungsreview ohne offene P1/P2 geschlossen. Tatsächlich
gelesene Source-SHA256: plans.py AF3556691D1FEE1594C6007B3400B1D982A531D5CB61E3799FBFD86182FFF605,
qualify.py A8FD3AF41D7C4E7F9FB9FD5C1A1759E0B8FBD435CEF4300578D9BEBA6EA55AF1.
Vorangehende unabhängige XE-/Cleanup-/Sourceattributionsreviews nur für ihre
unveränderten tatsächlichen Quellen wiederverwendet. Reviewer führte weder
Tests noch Native aus. Unveränderte C6-Originalframes werden rein von der neuen
UTC-Quelle akzeptiert; dieser Replay verändert den alten FAIL nicht und ersetzt
keinen frischen vollständigen Lifecycle. C7 zur tatsächlichen Zweiprofilprüfung
zugelassen, Ergebnis noch offen.


## Tatsächlicher Native-C7-Nachweis und Checkpoint

Kandidat 7 bestand zwei neue eigene vollständige SQL-17.0.5005.3-Lifecycles,
Tokens 102F335BC31343C9/8E457B5AFF5B48FA. Nativecalls je Profil:
32/32. Insgesamt sechs ursprüngliche
ungezwungene Reader-Abfragen mit 60 vollständigen Rowdigests, 18 Sourceproben/
18000 Rows und zwölf vollständige Stateaufnahmen/12000 Rows. Vier echte vollständige
51003/FAIL_RESULT_CONTRACT-Negativframes; ursprüngliche Source tatsächlich erhalten.

| Profil | Ohne Candidate | Mit Candidate | Nach Abbau |
| --- | --- | --- | --- |
| 1 | Clustered Index Seek / [DGN010_OwnPK] | Index Seek / [DGN010_OwnCandidate] | Clustered Index Seek / [DGN010_OwnPK] |
| 2 | Clustered Index Seek / [DGN010_OwnPK] | Index Seek / [DGN010_OwnCandidate] | Clustered Index Seek / [DGN010_OwnPK] |

Jeder passende Actualplan hat tatsächlichen Ergebnisroot10 und Source10,
jeweils genau einen Thread0/eine Ausführung; int-Runtimeparameter101/110.
Vollständiger tatsächlicher Batchtext, Event-Session-/DB-ID, fünfteiliger Request,
Native Stackhandle/Byteoffsets und genau passender vollständiger StatementText
gebunden. Native UTC-Ereignisse auf ihrer tatsächlich gelieferten Millisekunden-
auflösung dem ursprünglichen Readerintervall zugeordnet; kein Querydauerclaim.
Vollständiger Preparedtext-SHA mit Parameterdeklaration und originalem Semikolon,
Native-Statementoffsets ohne ausschließlich terminales Semikolon gebunden.
Kein geschätzter Cacheplan als Actualplan ausgegeben. Original-
ShowplanXML und vollständige tatsächlich ausgeführte/importierte Sourcehashes
privat erhalten und rein erneut an die Records gebunden, keine neue SQL-Ausführung
für diese Recordprüfung. Alle Ringpopulationen vollständig, keine Verdrängung/
Trunkierung/Dropcounter; eigene Sitzungsdefinition vor Abbau vollständig gleich.

Alle Source-/Statepaare einschließlich Config-Variant-/Datei-/Objekt-/Reader-/
Rechte-/Rollen-/Markerbytes vollständig unverändert. Zwei Candidate-DDL-
Transitions außerhalb der Queryaufnahme je Profil. Sechs eigene XE-Sitzungen
nativ abgebaut, je Profil zusätzlich frisch unabhängige Abwesenheit aller drei
Sitzungen. Guarded90/91, neue unabhängige DB-Abwesenheit und voller eigener
CID-/Namensabbau PASS. Alle 8 eigenen Container abwesend, kein UNKNOWN.
6 historische FAIL-Lifecycles bleiben sichtbar. Kumulativ C7; 1 von sechs
Kandidaten der Folgewelle verwendet. Erste Sechserwelle unverändert FAIL erhalten;
positiver Schnitt sicher geschlossen, kein Reset
und keine weiteren unveränderten grünen Wiederholungen. Fünfzehn reine Gegenfälle
und enge unabhängige Source-/Deltareviews ohne offene P1/P2 bestanden. Reviewer
attestierte keine Nativeausführung. Modell-/Tokenverbrauch unbekannt.

PASS der begrenzten privaten tatsächlichen Originalreaderplanbeobachtung.
Öffentliche Producer weiterhin Gesamt-WARN; volle Runtime/TP-PERF und
Indexnettonutzen NOT_ESTABLISHED. Die zusätzliche Instrumentierung ist getrennt
von den bisherigen Performance-Messungen. Ein Index Seek belegt für sich keinen
Nettonutzen. Commit-/Build-/volle Worker-/Modul-/Lehrmaterialabnahme bleiben offen.
Aktuelle selektierte Head-/Main-Gates, PR/Integration, ganze Treeübernahme,
FF-main und eigener lokaler/Remote-Branchcleanup folgen. Danach unmittelbar
nächste zulässige begrenzte Buildkostenfrage; Workstream/Heartbeat bleiben aktiv.
