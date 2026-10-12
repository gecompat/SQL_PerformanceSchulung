# CON-010 – begrenzte Wiederaufnahme der sechs Rechtebindungen

Autorität: menschliche allgemeine lokale Wellenfreigabe und ausdrückliche
Erweiterung auf mehr als zwei Testzyklen. Kanonischer Workstreamplan wählt
sechs kohärente Kandidaten je Schnitt. Der unveränderte historische
SQL_SERVER_2025_AI_TENANT_REVIEW.md bleibt erhalten: C1 Setup-2760,
C2 Policydefinitions-51003, C3 Rechtefixture-51003 sowie zwei separate
Metadatenproben. Drei vollständige Kandidaten und fünf eigene historische
Container bleiben gezählt; ihre damaligen Quellenhashes sind unbekannt.
Das vorhandene letzte Archiv wird weder überschrieben noch als vollständig
versionierte historische Admission ausgegeben.

Diese Wiederaufnahme beginnt C4. Höchstens C4–C6, jeweils zwei serielle
positive Wiederholungen auf stabilen gleichen Quellen; maximal sechs neue
eigene Container, insgesamt höchstens elf einschließlich der fünf früheren.
FAIL beendet den Kandidaten; Folge nur nach geänderten .sql/.py-Eingaben.
Kein zusätzlicher grüner Lauf nach den zwei erforderlichen Wiederholungen.
Ein Verantwortlicher, ein enger unabhängiger Sicherheitsreview vor Admission.
Unbekannter Modell-/Tokenverbrauch bleibt unbekannt.

Nur private Quelle Runtime/CON010_RESUME/sources, kein öffentlicher Manifest-
oder Matrixeintrag in diesem Qualifikationsschnitt. CON-010 bleibt PROPOSED
bis zum gesonderten vollständigen Demo-/Versions-/Negativkontrollgate.
Native Laufzeit prüft auf dem eigenen festen lokalen SQL-17.0.5005.3-Image:
zwei identische synthetische VECTOR(3)-Rows und drei WITHOUT LOGIN Benutzer;
konkrete sechs CONNECT-/SELECT-Grants mit Klasse, Major-/Minorbindung,
Grantor dbo, exaktem Permissionnamen samt DATALENGTH und Zustand G;
keine zusätzliche explizite Rollenzugehörigkeit. Vollständige eingefrorene
Funktions-/Policy-/Quellenbytes mit Längenprüfung, dbo nur als Labkontrolle.
Feste dynamische Quellenabfragen vermeiden den Eigentumsketten-Bypass.
Zwei positive Tenantkontexte, Unmapped ohne Rows, frei manipuliertes
Sessioncontextattribut ohne Autoritätswirkung, native Policy-ALTER-/fremde
Impersonation-/SELECT-Revoke-Verweigerungen und abschließender tatsächlicher
Kontext-/Grantrestore sind der Ergebnisvertrag. EXPECTED natives 33268,
15517,229 werden unverändert geprüft und bei Abweichung nicht aufgeweicht.

Alle acht SQL-Phasen binden vier vollständige Marker mit Unicodebytes und
DATALENGTH der Namen/Werte plus class=0/major_id=0/minor_id=0. Demo-/Token-/
Zielinput wird vor begrenzter Typkonversion vollständig geprüft. Setup wird
im tatsächlichen Lifecycle zweimal aufgerufen, Folgefixture erneut vollständig
geprüft. Kein Preview, MAXDOP, Login, externe Credentials, Modelle, Internet,
Inferenz, ANN oder Hoständerung. Keine echten Verbindungspools oder mehrere
Sessions, keine allgemeine Seitenkanalfreiheit. Nur aktuelle Offlinekontrolle.

Private Qualification verwendet unveränderte öffentliche FWK-010/-011-APIs
mit klar benanntem Adapter: synthetisches 16-Hex-RunToken per Manifestobjekt-
ersetzung statt LOCAL; begrenzter Native-Executor und zusätzliche Setup-
Wiederholung. Native ODBC-Optionen entfernen -W/-h und verwenden -C/-l2/-m1/
-y0/-w65535 für vollständige Ausgabe, maximal eine Million UTF-8-Bytes;
kein Include, Startupscript oder Shell. Passwort nur ENV. Quellen-/APIhashes
und synthetischer Admissionledger bleiben im ignorierten eigenen Runtimepfad.

300 s einschließlich Readiness; öffentliche reguläre 180 s und Phasenkappen
bleiben nachgeordnet erhalten, Setupwiederholung teilt dieselbe Phasendeadline.
Separate tatsächliche 60 s Cleanupdeadline ab erster Cleanupwirkung, nie
zurückgesetzt; SQL-Cleanup höchstens 20 s, neue unabhängige DB-Abwesenheit
höchstens vier Sekunden, voller own-CID- und Namensabbau/Abwesenheit in
restlichem selben Budget. Native Clients werden auch bei Collectorausnahme
auf tatsächlichen strikten int-Endstatus geprüft. UNKNOWN/ungeprüft verhindert
weiteres SQL und bleibt FAIL; ausschließlich vorher gebundener eigener
Container darf danach entfernt werden. Kein Cleanup aufgrund des Namens allein.
Fremder vorhandener Labcontainer bleibt unberührt. Kein Pull, vier CPUs,
sechs GiB, nur Loopback, Eigentumslabel plus vollständiger CID/Image/Resource-
Bindung vor Entfernung. Abwesenheit wird neu sowohl per CID als auch Name geprüft.

Primärquellen am 2026-10-12 geprüft: Microsoft Learn Row-Level Security
(SRC-093) und sys.database_permissions. RLS hängt vom Ausführungskontext ab;
privilegierte Policyverwaltung kann Grenzen ändern. Die drei automatischen
CONNECT-Grants sind konkrete historische Metadatenevidenz, keine universelle
Behauptung für jede Plattform oder jeden CREATE USER-Pfad.

Admissionvorlauf: sechs synthetische Endstatus-/Recoverygegenproben PASS. Erster rein synthetischer 3/5-Lauf scheiterte an einem nicht existierenden Fakeendpoint; der korrigierte Fixturelauf bestand sechs Methoden, ohne native Wirkung. Enger unabhängiger Quellenreview bestätigte Parent 42D47AC7CF006C5E3720AEB81D538885D5384AF106DBB87085C403127F58457D und Setup C752F9B665140E695F903EFE38A4EE1EABCE60F5A0135A11A846C22024E83828. P2 zum zweiten Endstatuspoll vor Admission geschlossen, keine weiteren konkreten P1/P2 im beauftragten Scope. Reviewer führte weder Runtime noch Tests aus.

C4 ist tatsächlich FAIL in SETUP mit Msg 468: EXCEPT kollidiert zwischen Datenbank- und Katalogcollation beim Grantzustand. Keine erfolgreiche Baseline oder Tenantabnahme. Token 564542236A8842E5; ursprüngliche Quellen unverändert archiviert in candidate4/frozen-sources, Ledger und Rawphasen bleiben erhalten. Marker-Cleanup PASS und neue DB-Abwesenheit sowie eigener vollständiger CID-/Namensabbau PASS; tatsächliches gemeinsames Cleanup 12,5917808 s. C5 korrigiert ausschließlich beide Richtungen des Zustandsvergleichs auf varbinary(1). Permissions bleiben unverändert, Orakel werden nicht erweitert. Parent- und APIquellen unverändert, sechs synthetische Gegenproben nicht erneut ausgeführt.

C5-Delta vor Admission unabhängig geschlossen: State char(1) beidseitig vollständig varbinary(1), genaue G-Bindung/alle sechs Grants und RLS-/Resultoracles unverändert; keine konkreten P1/P2. Setup 0D942FB328CE5D011A8ADC87877CC6BDD5E0BA04452537CEF495464074134790, Parent 42D47AC7CF006C5E3720AEB81D538885D5384AF106DBB87085C403127F58457D. Archivierter C4-Setuphash C752 bestätigt. Reviewer ohne Runtime/Tests.


## Tatsächliche Wiederaufnahme

| Kandidat/Slot | Synthetischer Token | Tatsächlicher Verlauf | Gesamter eigener Cleanup | DB/CID/Name abwesend |
|---|---|---|---|---|
| C4.1 | `564542236A8842E5` | FAIL_SETUP / Msg 468 | 12.5917808 s | PASS |
| C5.1 | `8CA1645CD07C4A84` | PASS / 6 Assertions / Setup zweimal | 12.8087104 s | PASS |
| C5.2 | `E087336FC90E4E68` | PASS / 6 Assertions / Setup zweimal | 12.5800160 s | PASS |

C5 bestand beide vollständigen privaten Lifecycles auf identischen gebundenen
Quellen. Tatsächliche Katalogaufnahme bestätigt je Benutzer CONNECT mit
class=0/major_id=0/minor_id=0 und SELECT mit class=1/eigene Documents-ObjectId/
minor_id=0, Grantor jeweils dbo, State G. Vollständige Quellen-/Vektor-/RLS-
Bytes und native drei Rechteverweigerungen wurden in jeder fachlichen Phase
erneut geprüft. Sechs Resultassertions je Lauf: baseline_rows=2,
authorized_contexts=2, unauthorized_rows=0, permission_denials=3,
revoked_rows=0, session_resets=1. Alle acht öffentlichen Frameworkphasen PASS;
zusätzliche native Setupwiederholung PASS. Originale Ziel-/Eigentumsmarker
blieben bis zum tatsächlichen Drop gebunden. Neue getrennte DB-Abwesenheit,
vollständige CID- und Namensabwesenheit bestätigt. Kein Containerrest dieser
Wiederaufnahme; fremder vorhandener Labcontainer unverändert.

Fünf kohärente Kandidaten insgesamt, sechs vollständige historische/neue
SQL-Lifecycles plus zwei historische Metadatenproben; acht eigene Container
insgesamt. Die drei alten und der neue C4-FAIL bleiben erhalten. Kein C6 und
kein unveränderter zusätzlicher grüner Lauf. Neue native Testläufe: drei,
davon ein FAIL und zwei stabile PASS; keine Provideraufrufe. Sechs betroffene
synthetische Methoden PASS; kein Wiederholen unveränderter alter Tests.
Keine betroffene öffentliche SQL-/Runner-/Manifest-/Registryänderung in
diesem Nachweisschnitt. Volle Marker- und Fixturemutationskontrollen,
Versionsgrenzen, öffentlicher Demoeinstieg/Matrizen/Anleitung und ihre
aktuellen Gates bleiben nächster separater Schritt. CON-010 weiterhin PROPOSED;
keine volle TP-RUN-/TP-CON-, Login-/Pooling-/ANN-/Providerqualifikation.

## Gebundene Quellen und Integration

- `Runtime/CON010_RESUME/qualify.py`: SHA256 `42D47AC7CF006C5E3720AEB81D538885D5384AF106DBB87085C403127F58457D`.
- `Runtime/CON010_RESUME/sources/00_Preflight.sql`: SHA256 `B690BAF8DAE24A3463B30C3B2483906F8BC7FFD7BE574CE9E8EEA0894866200B`.
- `Runtime/CON010_RESUME/sources/10_Setup.sql`: SHA256 `0D942FB328CE5D011A8ADC87877CC6BDD5E0BA04452537CEF495464074134790`.
- `Runtime/CON010_RESUME/sources/90_Cleanup.sql`: SHA256 `031210E4B4F2E7F1DD86078D039791B29612B51B168A4AA1433346994570D393`.
- `Runtime/CON010_RESUME/sources/Expected/result-contract.json`: SHA256 `0856DD36A98C56B3FF3237DEFCAA197971A640EF34D0B6B7E60945A323413F83`.

Vollständige Quellen-/APIhashes, native Phasen und tatsächliche Admissionen
liegen ausschließlich im ignorierten Runtime/CON010_RESUME; sie sind keine
zweite Backlogwahrheit. Fachlicher Status ist dieser begrenzte Nachweis mit
[historischem FAIL-Checkpoint](SQL_SERVER_2025_AI_TENANT_REVIEW.md),
[Workstreamplan](SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md) und kanonischem
[Ausführungsstand](CURRENT_EXECUTION_STATUS.md).

Primärquellen: [Microsoft Learn RLS](https://learn.microsoft.com/en-us/sql/relational-databases/security/row-level-security?view=sql-server-ver17)
und [sys.database_permissions](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-permissions-transact-sql?view=sql-server-ver17),
Abruf 2026-10-12. Der aktuelle PR benötigt die tatsächlich ausgewählten
Head-/Integrationsgates sowie Treeprüfung, main-Synchronisierung und eigenen
Branchabbau. Erst danach ist dieser Dokumentationsschnitt integriert.
