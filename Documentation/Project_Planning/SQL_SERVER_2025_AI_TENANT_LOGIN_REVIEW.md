# CON-010 / TSK-009: begrenzte Authentifizierung über eigene SQL-Logins

Stand: 2026-10-12. Status: PASS_PRIVATE_AUTHENTICATED_SERVERLOGIN_COMPONENT;
vier historische FAILs erhalten, aktuelle Integration noch offen.
Basis ist der vollständig integrierte [PR 218](https://github.com/gecompat/SQL_PerformanceSchulung/pull/218)
auf `d8b6649a05938a76e7dec3833db23f59844370c4`: acht aktuelle Head-/sechs
Main-Workflows PASS, voller identischer Tree, main synchronisiert und sauber,
eigener lokaler und Remote-Branch entfernt. Die abgeschlossene Generatorwelle
bleibt FAIL und wird nicht wieder aufgenommen. Allgemeine Entwicklung und
DGN-007 bleiben pausiert.

## Konkrete Lücke und Aussagegrenze

Die öffentliche CON-010-Demo ist IMPLEMENTED und qualifiziert die RLS-/Quellen-/
Vektor-/Rechtekontrollen unter WITHOUT LOGIN Benutzern mit EXECUTE AS in einer
Owner-Session. Sie beweist keine tatsächliche Serverauthentifizierung. Dieser
neue private Komponentenschnitt prüft daher neue getrennte SQL-Authentifizierungs-
verbindungen für Tenant A, Tenant B und einen nicht zugeordneten Benutzer.
Originaler Serverlogin, wirksamer Server-/DBbenutzer und volle SIDbindung müssen
tatsächlich beobachtet werden. Keine Gleichsetzung von EXECUTE AS mit Login.

Die zwei synthetischen Dokumente und identischen VECTOR(3)-Werte verwenden den
vorhandenen Tenant-Vertrag. Jede autorisierte Verbindung muss ihren vollständigen
Quellen-/Vektorkontext liefern; Unmapped liefert keinen Kontext bei tatsächlich
bestätigter Authentifizierung. Ein manipulierter Sessionwert darf Tenant A nicht
zu Tenant B machen. Rechtegegenproben prüfen Policyänderung, fremde Impersonation
und tatsächlichen SELECT-Widerruf/Restore. Leere Ergebnisse ersetzen weder
positive Authentifizierung noch native Rechtefehler.

Echtes Verbindungspooling, ANN/Postfilter, allgemeine Seitenkanäle, Provider,
Inferenz, Performance und vollständige TSK-009-/TP-CON-Abnahme bleiben offen.
Privilegierter Labowner ist ausschließlich Kontrolle, kein Schutz vor sysadmin.
Die öffentliche Demo und ihre grüne Standard-CI werden durch private Vorbereitung
nicht als Login-/Poolingqualifikation umgedeutet.

## Effekte, Autorität und gemeinsames Budget

Die ausdrücklich erteilte allgemeine lokale Entwicklungswellenfreigabe einschließlich
mehr als zwei Testzyklen deckt eigene wegwerfbare Testcontainer und synthetische
SQL-Sicherheitskontrollen ab. Serverlogin-DDL besitzt Instanzscope und wird für
diesen Schnitt ausdrücklich RED-isolated klassifiziert: ausschließlich ein neu
erzeugter, vollständig gebundener eigener Testcontainer; dokumentierter Reset
ist dessen begrenzter eigener Abbau. Keine rote Host-/Trust-/Dienst-/Betriebssystem-
konfiguration, fremde Instanz, Cloud-/Bezahl-API oder ONNX. Kein unbeaufsichtigter
Standard-CI-Start dieser roten privaten Komponente.

Höchstens sechs kohärente Kandidaten, Checkpoint nach drei geschlossenen Kandidaten,
Hardstop sechs; ein eigener serieller Container und ein begrenztes Profil je
Kandidat, insgesamt maximal sechs. Vier CPU/sechs GiB, festes vorhandenes Image,
SQL 17.0.5005.3, Developer/CL170. Höchstens zwei Dokumente/VECTOR(3), drei neue
eigene SQL-Logins einschließlich Unmapped und drei exakt gebundene DBbenutzer.
Keine PREVIEW_FEATURES-/MAXDOP-Änderung. 300 Sekunden regulärer Parent-/Profilzeit
einschließlich Startup, anschließend ein gemeinsames maximal60-Sekunden-Budget
für eigene SQL-/Prozess-/Containerbereinigung; keine Resetdeadline je Phase.
Null Modell-/Metadaten-/Provideraufrufe; Modell-/Tokenverbrauch unbekannt.

Ein Implementierungsverantwortlicher, Root als unabhängiger Reviewer ausschließlich
der neuen Authentifizierungs-/Serverprincipal-/Credential-/Cleanup-Risiken. Die
qualifizierte Parent-/Known-End-/Deadline-Basis wird bytegebunden wiederverwendet.
Keine breite Legacyanalyse oder Reviewkette. Retry benötigt relevante geänderte
Ausführungsquellen oder neue konkrete Evidenz; historische FAILs bleiben erhalten.
Kein weiterer grüner Lauf nach einem vollständig belegten Profil.

## Schutz- und Ergebnisvertrag vor Native

Der Parent bindet Ownerlabel, vollständige CID, Image, Port und Ressourcen der
eigenen Instanz, bevor SQL-Effekte zugelassen werden. Vier vollständige bytegenaue
DB-Eigentumsmarker binden jede folgende DB-/Loginmutation sowie Cleanup.
Die initiale DB-/Markerneuanlage setzt vorher vollständig gebundene eigene CID
und tatsächliche Zielabwesenheit voraus; bestehende markerfremde DBs werden
weder übernommen noch repariert. Eigene Server-
principalnamen und vollständige vorab festgelegte SIDs dürfen vorher nicht
existieren. Benutzer-/Login-SIDmapping, Typ, Defaultdatabase/-language, eigene
Policy-/Expiryflags, Rollen und vollständige Server-/DBpermissions sind zu binden;
keine zusätzlichen Rechte. Konkrete grantor-/class-/major-/minor-/state-/Namensbytes
bleiben vollständig. Automatische bzw. explizite CONNECT-Rechte sind tatsächliche
Katalogbefunde, keine aus Benennungen angenommene Sicherheit.

SQL-Authentifizierung verwendet ausschließlich SQLCMDPASSWORD im eigenen
Clientenvironment, niemals -P oder Geheimnisse in Prozessargumenten, Konsole,
öffentlichen Dokumenten oder versionierten Dateien. Operative eigene Secrets
und transient notwendige SQLinputs bleiben privat; bekannte Enden führen zur
tatsächlich geprüften Inputabwesenheit. Bei UNKNOWN bleiben eigene Recoveryinputs
erhalten. Kein Folge-SQL oder Authentifizierungsversuch nach unbekanntem Requestende.

Vor/nach Kontrollen müssen vollständige ursprüngliche Quellen-/Policy-/Config-/
Permission-/Principalstates einschließlich Restore belegt werden. Eigene Logins
werden vor dem DBdrop nur bei passenden vollständigen Eigentums-/SID-/State-
bindungen entfernt. Fremde Namen, SIDs, Marker oder Principalstates sind FAIL,
kein Cleanup anhand eines Namens allein. Tatsächlicher Drop, getrennte neue
DB-/Loginabwesenheit und frische eigene CID-/Namensabwesenheit schließen das Profil.
UNKNOWN, FAIL, WARN und SKIP bleiben sichtbar. Source-/Scope-/Budget-/Review-
und exklusive Parentadmission müssen vor jedem Native-Effekt geschlossen sein.

## Quellen und nächster Schritt

Der vorhandene [Tenant-Vertrag](SQL_SERVER_2025_AI_TENANT_IMPLEMENTATION_REVIEW.md)
und die unveränderten öffentlichen CON-010-SQLquellen bleiben maßgeblich.
Microsoft Learn unterscheidet Serverlogin, dessen DBbenutzerzuordnung und die
ursprüngliche Verbindungsidentität:
[CREATE LOGIN](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-login-transact-sql?view=sql-server-ver17),
[CREATE USER](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-user-transact-sql?view=sql-server-ver17),
[ORIGINAL_LOGIN](https://learn.microsoft.com/en-us/sql/t-sql/functions/original-login-transact-sql?view=sql-server-ver17)
und [sys.sql_logins](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-sql-logins-transact-sql?view=sql-server-ver17),
ergänzt durch [sys.database_principals](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-principals-transact-sql?view=sql-server-ver17)
für die eigene Benutzer-SID und deren Metadata Visibility. Abruf/Prüfung
2026-10-12, SRC-114. Quellenvertrag ist kein eigener Runtime-PASS.

Das unabhängige Root-Quellenreview ist vor Native geschlossen. Die 32 gebundenen
Quellen einschließlich 16 SQL-Vorschauen erfassen echte Loginverbindungen,
vollständige Principal-/Permission-/Objektzustände und markergebundene Mutationen.
Geschlossen wurden die tatsächliche Error-Severity aus dem Systemkatalog,
der genaue Session-Context-Key, Source-/Authority-Gates vor jedem Effekt,
Known-End auch für Startup sowie die Prüfung verschachtelter Credentialausgaben
nach vollständiger Decodierung des Hextransports. Raw-Permissiontypen behalten
ihre Leerzeichen; die Objektpopulation und ihre vollständigen IDs sind gebunden.
Zwölf gezielte reine Methoden bestanden auch unter Python -O, ohne native SQL-
oder OCI-Aufrufe. Das ersetzt keinen authentifizierten Lauf.

Passworthashes werden nicht aufgenommen; Passwortintegrität bleibt ausdrücklich
NOT_ESTABLISHED. Bei fehlender vollständiger SQL-Cleanup-Lease darf nur der
vollständig gebundene eigene Container ohne Mounts entfernt werden. Frische
CID-/Namensabwesenheit, bekannte Clientenden und Inputabwesenheit belegen dann
den zerstörten eigenen Namespace, keine SQL-Abwesenheit: der Kandidat bleibt
FAIL und sql_absence_evidence bleibt NOT_ESTABLISHED. Ein positives Profil
benötigt weiterhin tatsächliche Login-/DBdrops und neue getrennte SQL-Abwesenheit.

## Erster authentifizierter Caller: FAIL vor Setup

Kandidat 1 hielt nach einem bekannten beendeten Startup-Clienttimeout vor Setup
an. Zwei tatsächliche Clienthandles wurden gestartet; der Folgeclient zur
Abwesenheitsprüfung erhielt ausschließlich ODBC-Verbindungs-/Preloginfehler.
Kein Login-/DBsetup und keine Tenant-Ergebnisprüfung erreicht. Alle Clientenden
sind bekannt, kein UNKNOWN. Vollständig gebundene eigene CID und Name sind frisch
abwesend, keine Mounts, keine eigenen Inputdateien: eigener Namespace zerstört.
SQL-Abwesenheit bleibt NOT_ESTABLISHED; kein Cleanup-PASS aus Containerabwesenheit.
Das vollständige Quellen-/Gatepaket ist vor Korrektur privat bytegebunden archiviert.

Kandidat 2 korrigiert ausschließlich die begrenzten Startup-Clientoptionen anhand
dieses Befunds: -l 2 ausschließlich am festen initialen master/SA-SELECT1, weiterhin
fünf Sekunden Collectorlimit und unveränderte Timeout-/UNKNOWN-Abwehr. Allgemeine
DDL-/Tenant-/Cleanupclients bleiben unverändert. Zwei betroffene reine Methoden
bestanden auch unter Python -O; der übrige geprüfte Scope bleibt byteidentisch.
Das gemeinsame sechs-Kandidaten-/Containerbudget wird nicht zurückgesetzt.
Enges unabhängiges Rootreview des Startupdeltas geschlossen; neue Admission vor Native.

## Zweiter Kandidat: Setup-FAIL nach erfolgreichem Startup

Kandidat 2 erreichte SQL 17.0.5005.3 und bestätigte vor Setup tatsächliche
Zielabwesenheit. Das Setup scheiterte mit dem vollständigen nativen Fehler 2760,
Severity 16, State 5, Line 10: sec konnte bei der Security-Policy-Erstellung noch
nicht aufgelöst werden. Die Schemas werden erst innerhalb des Batches dynamisch
angelegt. Keine Loginanlage oder authentifizierte Tenantkontrolle erreicht.
Sieben tatsächliche Clienthandles, alle Enden bekannt; kein UNKNOWN.
Ohne gehaltene vollständige Principal-Lease wurde SQL-Cleanup failclosed
verweigert. Dessen Meldung überdeckte im Parent die ursprüngliche Setupmeldung;
beide nativen Rohbefunde sind privat erhalten. DB-/SQL-Abwesenheit bleibt
NOT_ESTABLISHED. Der vollständig gebundene eigene Namespace ohne Mounts ist
zerstört, CID und Name frisch abwesend, Inputs entfernt. C2 bleibt FAIL.

Kandidat 3 korrigiert ausschließlich die sichere Reihenfolge der Policy-Erstellung
und erhält Primär- sowie Cleanupfehler getrennt. Keine Übernahme eines Teilsetups,
keine Erweiterung von Rechten, Laufzeit, Effekten oder Budget.
Das feste Policy-DDL wird nach vorhandenen Schemas und Prädikat dynamisch
kompiliert. Das enge unabhängige Rootreview dieses Deltas ist geschlossen;
zwei betroffene reine Methoden bestanden auch unter Python -O. Fehlender
Cleanup-Lease bleibt eine Abbruchgrenze; Primärfehler wird zusätzlich erhalten.

## Dritter Kandidat und Checkpoint 3: Servergrant-FAIL

Kandidat 3 erstellte das Setup erfolgreich, erreichte aber noch keine vollständige
Principal-Baseline oder authentifizierte Tenantkontrolle. Das Loginbatch lieferte
dreimal Fehler 4621, Severity 16, State 10, Line 1: Serverpermissions dürfen nur
aus master erteilt werden. Der ausgeführte Batch befand sich in der eigenen
Testdatenbank. Neun tatsächliche Clienthandles, Enden bekannt; kein UNKNOWN.
Primärfehler und fehlende SQL-Cleanup-Lease stehen diesmal getrennt im Ergebnis.
SQL-Abwesenheit bleibt NOT_ESTABLISHED; vollständig gebundener eigener Namespace
ohne Mounts zerstört, CID/Name frisch abwesend und Inputs entfernt. C3 bleibt FAIL.

Checkpoint nach drei geschlossenen Kandidaten: insgesamt drei eigene Container,
18 tatsächliche Clienthandles, kein authentifizierter Tenantfall bestanden.
Das Budget erlaubt noch höchstens drei relevante Korrekturkandidaten mit je einem
eigenen Container. Kein Zurücksetzen der historischen Fehler. C4 begrenzt das
Servergrant auf expliziten master-Kontext; eigene DBmarker und die bisherigen
Rechte-/Ergebnis-/Cleanuporacles bleiben unverändert. Null Modell-/Provideraufrufe.
Das feste GRANT CONNECT SQL verwendet ausschließlich master.sys.sp_executesql;
vollständige eigene DBmarker stehen unmittelbar vor jedem einzelnen Login-DDL,
Servergrant, Benutzer-DDL und DBgrant. Das enge unabhängige Rootreview dieses
Kontextdeltas ist geschlossen; seine gezielte reine Prüfmethode bestand auch
unter Python -O. Kein zusätzlicher Benutzer, Grant oder Kontextwechsel des Callers.

## Vierter Kandidat: Alias-FAIL, SQL-Cleanup bestanden

Kandidat 4 erstellte Setup und drei Login-/Benutzerzuordnungen, bestätigte die
vollständige Principal-Baseline und die tatsächlichen nativen Error-Severities.
Das erste Tenant-A-Ergebnisbatch scheiterte mit Fehler 156, Severity 15, State 1
am unquotierten SQL-Alias Identity; nachfolgende 137-Fehler sind erhalten.
Keine vollständige Tenant-Ergebnis-/Identitätskontrolle bestanden. C4 bleibt FAIL.

17 tatsächliche Clienthandles, Enden bekannt, kein UNKNOWN. Die gehaltene volle
Principal-Lease erlaubte diesmal tatsächlich drei Login-Drops vor dem DBdrop.
Zwei neue getrennte SQL-Abwesenheitsprüfungen sowie frische eigene CID-/Namens-
und Inputabwesenheit bestanden. Dieser tatsächliche SQL-Cleanup ersetzt nicht
die weiterhin unbelegte SQL-Abwesenheit von C1 bis C3.

C5 quotiert ausschließlich den festen Alias als [Identity] in Ergebnis- und
Fehlerprojektion; JSON-Feld, Rechte, Schutzregeln und Oracles bleiben unverändert.
Noch maximal zwei Kandidaten im selben Budget.

## Fünfter Kandidat: begrenztes Profil bestanden

C5 änderte ausschließlich die zwei festen [Identity]-Aliase. Die neue reine
Alias-/Framekey-Prüfung bestand; unveränderte Python-/Oracle-/Known-End-Gates
blieben bytegebunden. Enges Rootreview und exklusive Source-/Scope-/Budget-
Admission waren vor Native geschlossen. Insgesamt 17 reine Methoden wurden
mit betroffenen Deltas geprüft; keine Wiederholung unveränderter grüner Suiten.

Das vollständige tatsächliche Profil bestand auf SQL 17.0.5005.3, EngineEdition 3,
Developer/CL170 im neuen eigenen Container mit vier CPU/sechs GiB:

| Kontrolle | Tatsächlicher begrenzter Befund |
|---|---|
| Authentifizierung | Drei neue getrennte SQL-Loginverbindungen; SUSER_SNAME, ORIGINAL_LOGIN, USER_NAME und sämtliche vollständigen Server-/Original-/Benutzer-SIDs passend zur vorher gehaltenen Reservation |
| Tenant A / B | Je genau die eigene vollständige synthetische Quelle und VECTOR(3) [1,0,0], Cosinedistanz 0 |
| Unmapped | Tatsächlich bestätigte eigene Login-/Benutzeridentität, genau null Quellenrows |
| Sessionmanipulation | Tenant A bleibt A trotz CON010_TenantId=2; tatsächlicher Reset auf NULL |
| Rechtegegenproben | Policy-ALTER 33268/Severity16, fremde Impersonation 15517/Severity16, SELECT nach tatsächlichem Widerruf 229/Severity14; State/Line/Procedure und volle UTF16-Meldung erhalten |
| Zustandskontinuität | 23 vollständige Quellen-/RLS-/Principal-/Permission-/Config-/Objektzustände, tatsächlicher SELECT-Restore auf die vollständige Baseline |
| Eigentumsgegenproben | Vier real abgewehrte Marker-DDL-Eingaben und eine reale Drop-Abweisung mit falscher gehaltener SID; vor/nach volle Zustände, keine Mutation |
| Cleanup | Drei tatsächlich marker-/principalgebundene Login-Drops vor dem DBdrop, getrennte neue SQL-Abwesenheit von DB/Namen/SIDs, frische CID-/Namensabwesenheit, null eigene Inputdateien |

C5 besitzt 60 tatsächliche Clienthandles einschließlich Startup-/Bootstrapqueries.
Die gesamte Welle umfasst fünf eigene Container und 95 Clienthandles, alle
Clientenden bekannt und sämtliche eigenen Namespaces abwesend; kein UNKNOWN.
Vier historische FAILs bleiben unverändert, einschließlich NOT_ESTABLISHED für
SQL-Abwesenheit in C1–C3. C4 und C5 besitzen tatsächlichen SQL-Cleanupnachweis.
Vollständige native Frames, sieben Ergebnismengen, 23 Vollstates, Quellenarchive,
Reservation, fünf tatsächliche Guardfehler und unabhängige Cleanupprüfungen sind
privat rein neu gebunden. Keine erneute SQL-Ausführung zur Recordprüfung.
Null Modell-/Metadaten-/Provider-/Cloud-/Hoständerungen. Modell-/Tokens unbekannt.
Kein weiterer grüner Lauf; der unbenutzte sechste Kandidat wird nicht verbraucht.

Dies ist genau ein begrenztes privates Authentifizierungsprofil. Passwortintegrität,
Pooling, ANN/Postfilter, allgemeine Seitenkanäle, öffentliche authentifizierte
CON-010-Qualifikation und vollständige TSK-009-/TP-CON-Abnahme bleiben offen.
Die öffentliche WITHOUT-LOGIN-Demo bleibt in ihrem bisherigen qualifizierten Scope.

Nächster Schritt: aktuelle Head-/Main-Gates, vollständige Treeübernahme,
Synchronisierung und eigener Branchcleanup. Anschließend unabhängige TSK-012-
Belegleseaufgaben für tatsächliches lokales Embedding/SQL-Retrieval, gescheiterte
Generation und die begrenzte Login-Trennung; keine zusätzlichen Modell-/SQLläufe.
Andere Repositories bleiben unverändert; öffentliche Lab-RAG-/DEC-033-Grenzen
werden nicht umgangen. Allgemeine Entwicklung und DGN-007 bleiben pausiert.
