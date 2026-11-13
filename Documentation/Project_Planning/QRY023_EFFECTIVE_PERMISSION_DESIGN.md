# QRY-023: Effektivrechtequalifikation

Stand: 13. November 2026
Status: ADMIN-Inventur und READER-Exact-set-Preflight sind auf SQL Server
2019/2022/2025 automatisiert enginequalifiziert; eine zusätzliche Live-
Gegenprobe für unerwartete READER-Rechte besteht auf allen drei Engines.
QRY-023 bleibt `PROPOSED` und nicht katalogisiert.

## Ziel und Grenze

Der Entwurf konkretisiert die offene READER-Rechteprüfung des QRY-023-
Proposed-Harness. Der Qualifikationspreflight soll vor Korrektheit, Messung und
Planevidenz am tatsächlich verbundenen READER-Prinzipal die effektiven Rechte
für eine vorab festgelegte Menge von Server-, Datenbank-, Schema- und
Objektsecurables erfassen. Fehlende, nicht auswertbare oder nicht deklarierte
Rechte führen zum Abbruch vor der ersten Evidenzabfrage.

`sys.fn_my_permissions` wertet die Rechte des aktuellen Sicherheitskontexts
aus. Es liefert effektive Rechte einschließlich direkter, geerbter und über
Rollen erhaltener Grants; bei Abfragefehler liefert es `NULL`. Die Erfassung
muss daher in jeder tatsächlichen READER-Verbindung stattfinden. Ergebnisse
eines ADMIN-Kontexts, `EXECUTE AS`-Ersatzprüfungen oder einer anderen Verbindung
qualifizieren diesen Principal nicht. Microsoft beschreibt zugleich, dass
SQL-Serverrechte aus festgelegten Rollen und granularen Rechten zusammenwirken
und `sysadmin` die normale Berechtigungsprüfung umgeht. Die Funktion allein
belegt daher weder eine vollständige Instanzinventur noch eine belastbare
Minimalrechteaussage.

`DEC-083` legt die zulässige Umgebungsbaseline und die Ablehnungsgrenzen fest.
Dieser Entwurf war die Grundlage der späteren Implementierung. Die
Sollmengen- und Vererbungsprüfung läuft fail-closed je Securable; unbekannte
oder nicht inventarisierbare Rechte bleiben `NOT_PROVEN`. Der automatisierte
Lauf hat die SQL-Prinzipalbindung, die deklarierten Effektivrechte und die
Ownership-Chain-Wirkung auf den drei gepinnten Engines bestätigt. Allgemeine
Runtimeaufnahme und Katalogpromotion bleiben getrennte Gates.

Im Folgenden bezeichnet FWK-004 die sessionbezogene Messreferenz des Projekts;
FWK-010 bezeichnet den SQL-Demoaufrufer mit phasengebundenen Credential-
Profilen. `ADMIN` und `READER` sind die im vorgeschlagenen Manifest deklarierten
Profilnamen.

## Vorläufige Phasen- und Objektmatrix

| Identität / Phase | Bestehender Ablauf | Vorläufig nötiger Zugriffskandidat | Zusätzliche Qualifikation |
|---|---|---|---|
| `ADMIN` / `PREFLIGHT` | Read-only Prüfung in `master`, vollständige Benutzerdatenbanksicht und Markerprüfung eines vorhandenen Ziels | `VIEW ANY DATABASE`; eines der bereits deklarierten Rechte zum Anlegen der Testdatenbank | Vor Setup ist nur eine leere Instanz oder die exakte markierte Wiederaufnahme zulässig |
| `ADMIN` / `SETUP`, `FRAMEWORK`, `WORKLOAD` | Wegwerfdatenbank, FWK-004 und synthetische Objekte aufbauen | Datenbank, Schema, Tabellen, Prozeduren, Indizes und synthetische Inserts gemäß Setupskripten | Keine Minimalrechteaussage; Ziel muss eigens isoliert und vollständig markiert sein |
| `ADMIN` / `ADMIN_PERMISSION_INVENTORY` | READER-Login und Datenbankbenutzer binden sowie Rollen, explizite Rechte, Datenbanken und Endpoints vollständig inventarisieren | Read-only Katalogzugriff auf die markierte Zieldatenbank | Enginequalifiziert; fehlende Metadatensicht oder Abweichung führt zu `FAIL_NOT_PROVEN`; keine Rechtevergabe |
| `READER` / `QUALIFICATION_PREFLIGHT` | Marker lesen und vor allen Queryphasen positive Rechte prüfen | `SELECT` auf acht QRY-023 Query-/Oracletabellen und `lab.MeasurementRun`; `EXECUTE` auf `lab.USP_Qry023MeasureVariant`; Datenbankrecht `SHOWPLAN` | Effektivmengen außerdem auf Server, Datenbank, `dbo`, `lab` und allen inventarisierten Datenbankobjekten erfassen |
| `READER` / `CORRECTNESS` | kleines Tupeloracle und 10.000 eindeutige Pfade gegen beide Varianten | `SELECT` auf `dbo.Person`, `dbo.FriendOf`, `dbo.RelPerson`, `dbo.RelFriend`, `dbo.OraclePerson`, `dbo.OracleFriendOf`, `dbo.OracleRelPerson`, `dbo.OracleRelFriend` | Tabellenvariablen sind lokale Ausgabespeicher; keine persistenten Schreibrechte erforderlich |
| `READER` / `MEASUREMENT` | Messwrapper ausführen und zehn FWK-004-Messzeilen lesen | `EXECUTE` auf `lab.USP_Qry023MeasureVariant`; `SELECT` auf `lab.MeasurementRun`; `SELECT` auf den vier Querytabellen | Interne Schreiboperationen durch `USP_BeginMeasurement`/`USP_EndMeasurement` müssen über die konkrete Ownership Chain funktionieren; READER erhält dafür keine direkten Tabellen-Schreibrechte. Wait-Statistiken bleiben deaktiviert |
| `READER` / `PLAN_EVIDENCE` | zwei getrennte `COUNT_BIG`-Planabfragen | `SELECT` auf `dbo.Person`, `dbo.FriendOf`, `dbo.RelPerson`, `dbo.RelFriend`; Datenbankrecht `SHOWPLAN` | Planphase und Messreihe bleiben getrennt |
| `ADMIN` / `CLEANUP` | markierte Wegwerfdatenbank nur bei vollständigen Eigentumsmarkern entfernen | Cleanuprecht für exakt das eigene Ziel | Cleanup-, Abbruch- und Reaperverhalten ist Runtimepflicht und nicht durch die READER-Erfassung bewiesen |

Der Messwrapper verwendet außerdem `lab.MeasurementWaitSnapshot` nur im
deaktivierten Wait-Erfassungspfad nicht. Das Objekt bleibt Teil des
Inventarvergleichs; für den READER ist dort kein Zugriff vorgesehen. Die
laufende Qualifikation darf weder `VIEW SERVER PERFORMANCE STATE` noch
`VIEW SERVER STATE` implizit zum READER-Profil hinzufügen.

## Erfassungsflächen und fail-closed Regeln

1. **Serverkontext:** `sys.fn_my_permissions(NULL, 'SERVER')` im READER-
   Login. `CONNECT SQL` ist das erforderliche reguläre Loginrecht; neue Logins
   erhalten es automatisch. `VIEW ANY DATABASE` ist ausschließlich als
   dokumentierte SQL-Server-`public`-Baseline zulässig; beide Rechte werden
   nicht als QRY-023-Fachrechte bezeichnet. Jedes weitere Serverrecht, unbekannte
   Berechtigungsnamen, fehlende Resultsets oder `NULL` ergeben einen harten
   Abbruch. ADMIN muss zusätzlich die vollständige Rollenmitgliedschaft des
   READER-Logins prüfen: `public` ist die einzige zulässige Serverrolle;
   `sysadmin`, jede andere feste Rolle, jede benutzerdefinierte Rolle sowie
   nicht sichtbare oder unbekannte Einträge führen zu `NOT_PROVEN`. Die
   ADMIN-Sicht muss außerdem explizite Rechtezuweisungen an READER und
   beteiligte Rollen erfassen: `CONNECT SQL` darf dem READER-Login als
   reguläres Loginrecht zugewiesen sein; `VIEW ANY DATABASE` darf nur aus der
   dokumentierten `public`-Baseline stammen. Ein weiterer oder abweichender
   expliziter Grant/DENY ist nicht durch gleiche Effektivrechtenamen gedeckt.
2. **Endpoints:** ADMIN inventarisiert alle sichtbaren eingebauten,
   nichtadministrativen Endpoints und gibt IDs sowie UTF-16LE-Hexnamen mit
   gebundenen Count-Markern aus. Der FWK-010-Caller validiert diese Übergabe
   vollständig, bevor die nächste SQL-Phase startet. Die tatsächliche READER-
   Verbindung ruft dann für jeden übergebenen Namen
   `sys.fn_my_permissions(name, 'ENDPOINT')` auf. Erwartet wird ausschließlich
   `CONNECT` je Endpoint. So wird keine Endpointmetadatensicht für READER
   vorausgesetzt. Die Dedicated Admin Connection ist ausgenommen. ADMIN bindet
   zusätzlich direkte Grants/DENYs und Rollenmitgliedschaften, sodass Rechte
   nicht allein aus der Sollbaseline abgeleitet werden.
   Benutzerdefinierte Endpoints, zusätzliche Rechte oder eine
   unvollständige Endpointinventur stoppen den Lauf. Ein Name oder Typ, den der
   Implementierer nicht als Standardendpoint klassifizieren kann, ist
   `NOT_PROVEN`.
3. **Datenbankkontext:** `sys.fn_my_permissions(NULL, 'DATABASE')` in der
   markierten Zieldatenbank. Erwartete Laufrechte sind auf den explizit
   vereinbarten Basiseintrag zum Verbinden und die oben ausgewiesenen
   Objektzugriffe zu begrenzen. Höherstufige Rechte wie `CONTROL`, `ALTER`,
   `CREATE`, `IMPERSONATE` oder eine andere unvereinbarte Berechtigung dürfen
   nicht als bloßes Vorhandensein der Pflichtrechte durchgehen.
4. **Schemata:** `dbo` und `lab` getrennt erfassen. Schema- oder
   Datenbankrechte können Rechte auf untergeordnete Objekte übertragen und
   würden das beabsichtigte objektweise Profil erweitern. Eine solche
   Berechtigung wird abgewiesen, sofern sie nicht ausdrücklich in der
   Sollmenge beschlossen ist.
5. **Objekte:** Das READER-Exact-set prüft die acht QRY-023-Tabellen,
   `lab.MeasurementRun`, `lab.MeasurementWaitSnapshot`,
   `lab.USP_Qry023MeasureVariant`, `lab.USP_BeginMeasurement` und
   `lab.USP_EndMeasurement` einzeln. Die vorgelagerte ADMIN-Inventur lässt nur
   explizite Grants an READER/`public` aus der deklarierten Menge zu; dadurch
   werden Rechte auf weiteren benutzerdefinierten Securables bereits dort
   zurückgewiesen. Nicht sichtbare oder unvollständige Grantzeilen bleiben
   `NOT_PROVEN`.
6. **Rollen:** ADMIN bindet die tatsächliche SQL-Login-SID an den erwarteten
   READER-Datenbankprincipal und inventarisiert Server- und Datenbankrollen.
   In der markierten QRY-023-Datenbank ist nur die feste Rolle `public`
   zulässig. Nicht sichtbare Rollenmitgliedschaften, zusätzliche Rollen oder
   eine Principal-/SID-Abweichung ergeben `NOT_PROVEN`. Die Rechteauswertung
   selbst läuft trotzdem unter der tatsächlichen READER-Anmeldung; ein
   ADMIN-Ergebnis oder `EXECUTE AS` ersetzt sie nicht.
7. **Objekt- und Spaltenrechte:** Für jedes inventarisierte Objekt die
   zurückgegebenen Namen `entity_name` auf Vorhandensein prüfen, `subentity_name`
   muss `NULL` sein; den exakten `permission_name`-Satz mit der vorab gebundenen
   Sollmenge je explizitem Funktionsaufrufkontext vergleichen. Nicht deklarierte
   Berechtigungen, Spaltenrechte, ein fehlendes Objekt oder ein unvollständiges
   Resultset stoppen die Prüfung. Column-level `SELECT` wird bis zu einer
   gesonderten vollständigen Ergebnisspaltenbegründung nicht als Ersatz für
   das Tabellenrecht akzeptiert.
8. **Vergleich:** Nur vollständige Mengengleichheit mit der vorab gebundenen
   Sollmenge darf `PASS` erzeugen. Keine Sollmenge zur Laufzeit aus den gerade
   beobachteten Rechten ableiten. `HAS_PERMS_BY_NAME` bleibt als positive
   Vorprüfung bestehen, ersetzt aber den zusätzlichen Mengengleichheitscheck
   nicht.

## Abdeckungsgrenzen

Die relevante Objektinventur muss an eine frisch erstellte, einmalige
QRY-023-Wegwerfdatenbank und die exakten Framework-/Run-Marker gebunden sein.
Sie muss auch Securables erfassen, für die der Funktionsaufruf nicht direkt
unterstützt wird, oder deren Existenz beziehungsweise Rechte ausdrücklich als
unbekannt zum Abbruch führen. Das Sichten einzelner erwarteter Tabellen allein
schließt zusätzliche Grants auf einem anderen Objekt nicht aus.

Die Funktion zeigt effektive Rechte, aber nicht zuverlässig deren Quelle. Das
ist für den Sollmengenvergleich ausreichend, sofern die gesamte relevante
Securable-Menge vollständig gebunden ist. Es reicht nicht, um externe
Windows-Gruppenmitgliedschaften, Login-Provisionierung, Ownership-Chain-
Ausführung, `EXECUTE AS`-Verhalten, Moduländerungen oder Server-/Hostgrenzen
abzunehmen. QRY-023 verwendet SQL-Authentifizierung für getrennte
Credential-Profile; reale Login- und Datenbankprincipalbindung muss dennoch im
isolierten Lauf auf allen drei festgeschriebenen Builds nachgewiesen; das ist keine Aussage über Windows-Gruppen oder Hostgrenzen.

Ein unbekannter Serverberechtigungsbaseline-Eintrag oder eine nicht
inventarisierbare Server-/Datenbanksecurable führt zu `NOT_PROVEN`/Skip vor
Korrektheit und Messung, niemals zu einem stillschweigenden PASS. Der
SQL-Server-`public`-Baselineeintrag `VIEW ANY DATABASE` wird nur dann
akzeptiert, wenn der Ausführungsträger eine frische, für genau diesen
QRY-023-Lauf reservierte Wegwerfinstanz bereitstellt. Vor Setup darf diese
Instanz keine Benutzerdatenbank enthalten; bei einem zulässigen Wiederaufnahmepfad
darf ausschließlich die vollständig markierte Datenbank desselben Runs
vorhanden sein. Nach Setup muss die gebundene QRY-023-Datenbank die einzige
Benutzerdatenbank sein. Ein abweichendes Inventar, ein nicht exklusiv
zuordenbarer Container oder eine nicht unabhängig bestätigte Instanzbindung
ergibt `NOT_PROVEN` vor der ersten Reader-Abfrage. Dadurch bleibt die
Metadatensichtbarkeit auf die absichtlich disposable Instanz begrenzt; sie wird
weder als erforderliches QRY-023-Recht noch als allgemeine Least-Privilege-
Ausnahme freigegeben.

Der Harness ändert weder Serverrechte noch `public`. Er entzieht `VIEW ANY
DATABASE` nicht, gewährt es nicht neu und nimmt keine Endpoint- oder
Rollenkorrektur vor. Die Laufvoraussetzung wird geprüft und bei Abweichung
abgebrochen.

## SQL-Server-Standardbaselines und festgelegte Laufgrenze

Eine vollständig leere Server-Sollmenge ist für einen normalen SQL-Server-
Login keine belastbare Annahme: Jeder Login gehört zur festen Serverrolle
`public`; neue Logins erhalten automatisch `CONNECT SQL`. Microsoft nennt
`CONNECT` auf den Serverendpunkten (außer Dedicated Admin Connection) als
normale `public`-Konfiguration. Außerdem hat `public` standardmäßig
`VIEW ANY DATABASE`; damit können Logins Datenbankinformationen sehen. Diese
Rechte sind von einer zusätzlich gewährten QRY-023-Berechtigung zu trennen.

`DEC-083` wählt die eng begrenzte Betriebsform: akzeptiert wird die
dokumentierte `public`-Baseline nur auf einer für einen QRY-023-Run exklusiv
bereitgestellten Wegwerfinstanz mit gebundenem Datenbankinventar und
Standardendpointbestand. Vor Setup ist keine Benutzerdatenbank vorhanden,
außer einer exakt markierten Wiederaufnahme desselben Runs; nach Setup ist die
markierte QRY-023-Datenbank die einzige Benutzerdatenbank. Die Rechteprüfung
läuft in jeder tatsächlichen READER-Verbindung und vergleicht vorab gebundene
Sollmengen für Server, jeden Standardendpoint, Datenbank, Schemas und sämtliche
benutzerdefinierten Securables. ADMIN bindet zusätzlich Login-SID, Datenbank-
Principal und Rollenmitgliedschaften; ausschließlich `public` ist zulässig.

Die Sollmenge darf `CONNECT SQL` als reguläres Loginrecht, `VIEW ANY DATABASE`
als Server-`public`-Baseline sowie Endpoint-`CONNECT` aus der `public`-Rolle auf nachweislich
standardmäßigen SQL-Endpoints tolerieren. `VIEW ANY DATABASE` ist dabei kein
für QRY-023-Abfragen erforderliches Recht. Die Einzel-Run-Instanz darf keine
anderen Benutzerdatenbanken oder benutzerdefinierten Endpoints enthalten.
Unbekannte Endpoints, zusätzliche oder nicht sichtbare Rollen, sonstige
Server-/Endpointrechte, unerwartete Rechte auf niedrigeren Securables und eine
abweichende Datenbankinventur führen zu `NOT_PROVEN` vor Korrektheit oder
Messung. Der Harness gewährt, entzieht oder verändert keine Serverrechte und
ändert die feste Serverrolle `public` nicht. Eine spätere Lockerung oder
Änderung dieser Umgebungsgrenze erfordert eine eigene Methodenentscheidung.

Die Implementierung muss die dokumentierte Rechtehierarchie beim Vergleich
berücksichtigen: effektiv geerbte Rechte werden nicht irrtümlich als
zusätzliche direkte Grants gezählt; zugleich darf keine beobachtete
Sollmenge aus dem Lauf selbst abgeleitet werden. Kann die statische Sollmenge
für eine Securable-Klasse oder die dafür benötigte Sichtbarkeit nicht
vollständig vorab gebunden werden, bleibt die Laufphase `NOT_PROVEN`.

Auch die Festrollenmatrix ist versionsgebunden: SQL Server 2019 besitzt die
Legacy-Festserverrollen; ab SQL Server 2022 kommen zusätzliche `##MS_*##`-
Serverrollen hinzu, deren Rechte Datenbankrechte weitervererben können. Die
Freigabe muss daher die tatsächliche Serverversion feststellen, die komplette
versionsgültige Festrollenmitgliedschaft des READER-Principals prüfen und
unbekannte oder nicht sichtbare Rolleneinträge als `NOT_PROVEN` behandeln.
Ein bloßer Vergleich der durch `sys.fn_my_permissions` gelieferten Namen darf
eine privilegierte Festrollenmitgliedschaft oder deren mögliche
Eskalationswirkung nicht verdecken.

Diese Baselineentscheidung ergänzt die noch auszuarbeitende konkrete
Effektivrechte-Sollmenge; sie autorisiert keine globale Rechteänderung.

## Versionierter Sollmengenkandidat `1.0`

Der Manifestblock `reader_permission_expectation_contract` konkretisiert die
vollständige erwartete Effektivrechtemenge unter der echten READER-Verbindung.
Der exact-set-Vergleich bindet jeden Funktionsaufruf an einen festen
Kontextschlüssel. Endpointnamen stammen aus dem validierten ADMIN-Handoff;
READER prüft jedes Endpointrecht selbst mit
`sys.fn_my_permissions(name, 'ENDPOINT')`. Fehlende oder `NULL`-Resultate, Duplikate, unbekannte Securables,
Spaltenrechte und zur Laufzeit aus Beobachtungen abgeleitete Erwartungen
führen zu `NOT_PROVEN`.

Die Kandidatenmenge akzeptiert im Serverkontext ausschließlich `CONNECT SQL`
und `VIEW ANY DATABASE` gemäß `DEC-083`; pro ADMIN-inventarisiertem Standard-
Endpoint ausschließlich `CONNECT`; im Datenbankkontext `CONNECT`, `SHOWPLAN`
und die dokumentierten `public`-Baseline-Rechte
`VIEW ANY COLUMN ENCRYPTION KEY DEFINITION` sowie
`VIEW ANY COLUMN MASTER KEY DEFINITION`. Darüber hinaus dokumentiert Microsoft
standardmäßiges `SELECT` für `public` auf einzelnen Systemobjekten. Die negative
`major_id` allein weist jedoch nur
Systemobjekte aus und identifiziert nicht die exakte Standardmenge. Die ADMIN-
Inventur weist solche Grants daher bis zu einer exakten, versionsgebundenen
Sollmenge mit `FAIL_NOT_PROVEN` zurück; eine pauschale Freigabe aller Systemobjekte
ist ausgeschlossen. `public`-Grants auf QRY-023-/FWK-004-Nutzobjekten und direkte
READER-Grants auf Systemobjekte bleiben unzulässig. Auf `dbo` und `lab` sind
keine Schemarechte erlaubt. Die acht Query-/Oracle-
Tabellen sowie `lab.MeasurementRun` erwarten `SELECT`; das Messverfahren
`lab.USP_Qry023MeasureVariant` erwartet `EXECUTE`. `lab.MeasurementWaitSnapshot`,
`lab.USP_BeginMeasurement` und `lab.USP_EndMeasurement` erwarten für READER
keine direkten Rechte; der Messwrapper-Zugriff auf interne Messobjekte muss
getrennt über die bestehende Ownership Chain qualifiziert werden. Zusätzliche
benutzerdefinierte Securables werden nicht stillschweigend ignoriert.

Der Manifestvertrag ist mit `EXPECTED_READER_PERMISSION_EXPECTATION_CONTRACT`
im Offlinevalidator objektgenau gebunden; synthetische Regressionen schützen
gegen zusätzliches Datenbankrecht, unvollständige Objektinventur und
runtime-abgeleitete Sollwerte. Der vorgeschlagene CI-Aufrufer führt den
Exact-set-Vergleich zusätzlich auf den echten READER-Verbindungen aus. Die
positiven Server-, Datenbank-, Schema-, Objekt- und Endpoint-Sollmengen sowie
der Messprozedurpfad bestanden auf allen drei gepinnten Builds.

PRs #566–#581 ergänzten auf diesen Builds echte fail-closed Gegenproben:
direkter Objekt-SELECT plus `db_datareader`, Objekt-DENY, `dbcreator`- und
`securityadmin`-Serverrollen, fehlendes erwartetes Objekt, zusätzliche und
verweigerte Server-/Datenbankrechte, Endpoint-CONNECT-Grant und -DENY,
`VIEW ANY DATABASE`-Grant und -DENY, `DENY CONNECT SQL` sowie ein
unregistrierter gestoppter TSQL-Endpoint. Das ADMIN-Inventar wies jeden
Berechtigungsfall vor den Queryphasen mit seiner exakten Fehlerkategorie ab;
owner-/markergebundener Restore und Cleanup bestanden. Nach den Gegenproben
bestand der positive Zehnphasenlauf. Für den Custom-Endpoint-Fall läuft die
DDL absichtlich nach dem positiven Lauf als letzte Instanzmutation; danach
werden Endpoint und Wegwerfinstanz entfernt.

Die negativen SQL-Katalogzustände wurden ausschließlich in eigens markierten
Wegwerfcontainern erzeugt. Es wurden keine fremden Instanzen oder absichtlich
beschädigten Systemkataloge verändert. Die technische Rechtequalifikation gilt
für den gebundenen Ein-Run-Container und die drei gepinnten Builds; sie setzt
QRY-023 weder in den Runtimekatalog noch setzt sie `runtime_authorized`.
Allgemeine Runtime-/Produktfreigabe und Katalogaufnahme bleiben offen.

## Qualifizierte Gegenproben und verbleibende Grenzen

Die Live-Matrix belegt die genannten konkreten Abweichungen, nicht jede
mögliche Berechtigungspermutation. Der exact-set-Preflight fail-closed für
unbekannte Rechte, Metadatenlücken, `NULL`/leere/duplizierte Resultate,
unvollständige Spaltenrechte, Markerabweichungen und Principalwechsel.
Zusätzliche Rechte auf nicht deklarierte Objekte, Datenbank- oder
Schemaebene werden über den ADMIN-Katalogvergleich erfasst. Die Tests bleiben
auf die einzelnen Run-Container, synthetischen Daten und festgeschriebenen
Builds begrenzt.

Nicht qualifiziert wurden absichtlich beschädigte Systemkataloge, beliebige
System-/Service-Konfigurationen und allgemeine Datenbankumgebungen. Es wurde
keine Produkt-/Katalogpromotion ausgeführt; QRY-023 bleibt `PROPOSED` und
`runtime_authorized: false`. Die menschliche Generalprobe bleibt ausdrücklich
ausgeschlossen. Weitere Freigabeschritte müssen die allgemeine Runtime- und
Produktaufnahme getrennt bewerten.
## Quellen und nächste Grenze

- Microsoft Learn, [`sys.fn_my_permissions`](https://learn.microsoft.com/en-us/sql/relational-databases/system-functions/sys-fn-my-permissions-transact-sql?view=sql-server-ver17): effektive Rechte des aufrufenden Kontexts, unterstützte Securable-Klassen einschließlich `ENDPOINT`, `NULL` bei Abfragefehler und benötigter `public`-Mitgliedschaftszustand; abgerufen am 12. November 2026.
- Microsoft Learn, [effektive Database-Engine-Berechtigungen](https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/determining-effective-database-engine-permissions?view=sql-server-ver17): Zusammenwirken des granularen und Festrollensystems sowie Sonderbehandlung von `sysadmin`; abgerufen am 12. November 2026.
- Microsoft Learn, [Database-Engine-Berechtigungen](https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/getting-started-with-database-engine-permissions?view=sql-server-ver17): Vererbung durch Datenbank-/Schemahierarchie und weiterreichende `CONTROL`-Rechte; abgerufen am 12. November 2026.
- Microsoft Learn, [`sys.databases`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-databases-transact-sql?view=sql-server-ver17) und [Server-`public`-Berechtigungen](https://learn.microsoft.com/en-us/sql/relational-databases/policy-based-management/server-public-permissions?view=sql-server-ver17): Standard-`VIEW ANY DATABASE`, automatische `CONNECT SQL`-Berechtigung und Endpoint-`CONNECT`; abgerufen am 12. November 2026.
- Microsoft Learn, [Serverrollen](https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/server-level-roles?view=sql-server-ver17): neue SQL-Server-2022-Rollen und in Datenbanken weiterwirkende Rechte; abgerufen am 12. November 2026.
- Microsoft Learn, [Datenbankrollen](https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/database-level-roles?view=sql-server-ver17) und [`sys.fn_builtin_permissions`](https://learn.microsoft.com/en-us/sql/relational-databases/system-functions/sys-fn-builtin-permissions-transact-sql?view=sql-server-ver17): `public`-Datenbank-`CONNECT` und die vordefinierte Rechtehierarchie; abgerufen am 12. November 2026, in `SRC-158` ergänzt.
- Microsoft Learn, [`sys.server_permissions`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-server-permissions-transact-sql?view=sql-server-ver17), [`sys.server_role_members`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-server-role-members-transact-sql?view=sql-server-ver17), [`sys.database_permissions`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-permissions-transact-sql?view=sql-server-ver17), [`sys.database_role_members`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-role-members-transact-sql?view=sql-server-ver17), [`sys.endpoints`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-endpoints-transact-sql?view=sql-server-ver17) und [Metadatensichtbarkeit](https://learn.microsoft.com/en-us/sql/relational-databases/security/metadata-visibility-configuration?view=sql-server-ver17): versionierte Security-Katalogrechte und Grenzen expliziter Permission-Zeilen; abgerufen am 13. November 2026, in `SRC-159` ergänzt.
- Die [empirische public-Systemobjektbaseline](QRY023_PUBLIC_SYSTEM_OBJECT_BASELINE.json) erfasst ausschließlich neue Nutzerdatenbanken auf den drei festgeschriebenen SQL-Server-Builds; Eintrag `SRC-160`. Sie ist weder ein QRY-023-Workloadlauf noch eine allgemeine Versions-/Editionsbaseline.
- Bestehender QRY-023-Vertrag: [Proposed-Harness README](../../Demos/05_Query_Patterns/QRY-023_Graph_Tables/README.md), [Proposed-Manifest](../../Demos/05_Query_Patterns/QRY-023_Graph_Tables/manifest.proposed.json) und [Methodenreview](GRAPH_TABLES_METHOD_REVIEW.md).
- Die wiederverwendeten Microsoft-Primärquellen sind als [`SRC-158` und `SRC-159`](../Research/SOURCE_REGISTER.md#qry-023--effektivrechte-und-sql-server-public-baseline) im Quellenregister zusammengeführt.

Die konkrete Methodenentscheidung ist in [DEC-083](../../.ai/DECISIONS.md)
registriert. Dieser Entwurf hält die Sollmengen- und Inventurmethodik fest; die
SQL-Ausführung und der empirische Qualifikationsnachweis sind im vorgeschlagenen
Harness und im aktuellen Ausführungsstand dokumentiert.

`22_Admin_Permission_Inventory.sql` setzt den ADMIN-Anteil read-only um;
`25_Qualification_Preflight.sql` vergleicht unter der echten READER-Verbindung
effektive Server-, Datenbank-, Schema- und Objektrechte mit dem statischen
Exact-set-Vertrag. Die ADMIN-Inventur bestätigt den Objektnamen-/Typensatz und
übergibt den Endpointbestand; READER prüft `CONNECT` pro Endpoint. Die Umsetzung ist implementiert und durch die automatisierten Engine-Läufe
auf SQL Server 2019/2022/2025 qualifiziert. Das Skript prüft die exakte Login-/Datenbankbenutzer-SID, verwirft explizite
Server-/Datenbankrollen, inventarisiert die expliziten Grants/DENYs an READER
und `public`, begrenzt den Benutzerdatenbankbestand und weist benutzerdefinierte
Endpoints zurück. Die exakte `public`-SELECT-Menge in einer frisch erstellten
Nutzerdatenbank wurde auf den gesperrten Builds 15.0.4500.2, 16.0.4305.5 und
17.0.5035.5 mit 186/226/232 Grants erfasst. Der vollständige Satz ist als
kanonisches Artefakt gebunden; der ADMIN-Preflight vergleicht Anzahl und
SHA-256-Digest für den exakten Build. Ein unbekannter Build, eine abweichende
Menge oder fehlende Metadatensicht bleibt `NOT_PROVEN`; negative `major_id`
allein ist kein Allowlist-Nachweis. Die deutlich größeren `master`-Mengen sind
Kontrollwerte und keine Sollmenge für die QRY-023-Zieldatenbank. Die READER-Objektgrants
werden gegen eine zulässige Sollmenge geprüft; die erforderlichen Rechte werden
vor den Abfragephasen durch den
nachfolgenden tatsächlichen READER-Preflight geprüft. Die Baseline erfasst nur
den Standardzustand der drei exakten Wegwerfimages; sie belegt weder die
vollständigen QRY-023-ADMIN-/READER-Rechte noch die Ownership Chain oder einen
QRY-023-Enginepass. Der Harnesslauf ergänzte diese Baseline mit der vollständigen
ADMIN-/READER-Qualifikation auf allen drei Builds. Der Vor-Setup-Preflight
verlangt vollständige Datenbanksicht und blockiert jede fremde Benutzerdatenbank.

Für SQL Server 2022+ prüft die Phase `VIEW ANY SECURITY DEFINITION`,
`VIEW ANY DEFINITION`, `VIEW SERVER SECURITY STATE`, `VIEW ANY DATABASE`,
`VIEW SECURITY DEFINITION` und `VIEW DEFINITION`; auf SQL Server 2019 gelten
`VIEW ANY DEFINITION`, `VIEW SERVER STATE`, `VIEW ANY DATABASE` und
`VIEW DEFINITION`. Die Definitionsrechte decken auch die dokumentierten
Anforderungen der Rollenmitgliedschaftskataloge ab. Der ADMIN-Kontext erhält
keine automatischen Grants. Fehlende Sichtbarkeit oder eine Abweichung erzeugt
`FAIL_NOT_PROVEN`. Quellenregistereintrag `SRC-159` bindet die jeweilige
Metadatensicht und die Grenzen der Permission-Kataloge.

Der Offlinevalidator, seine synthetischen Regressionen und der ScriptDom-Parse
unter den Grammatiken 150/160/170 prüfen nur die Struktur des ADMIN-Inventars
und des READER-Exact-set-Preflights. Sie attestieren keine
vollständigen Katalogresultate, SQL-Ausführung, tatsächlichen READER-Rechte oder
Ownership-Chain-Wirkung. Der nachfolgend dokumentierte isolierte Enginepass prüft
diese Claims gesondert. QRY-023 bleibt `PROPOSED` und nicht katalogisiert; die
Enginequalifikation ändert diesen Status nicht.

## Isolierte Ressourcen- und Timeoutdurchsetzung

Der vorgeschlagene CI-Aufrufer in [`.github/workflows/qry023-proposed-runtime.yml`](../../.github/workflows/qry023-proposed-runtime.yml)
bindet die drei Image-Digests und setzt 2 CPU, 4 GiB Container-RAM sowie
3 GiB SQL-Server-Speicher. Jeder Matrixjob läuft in einer eigenen GitHub-Hosted-VM
und prüft die ADMIN-Anmeldung mit `SELECT 1`, bevor er Mutationen startet.
Vor dem Harness fordert er genau eine TempDB-Logdatei und 1–15 Datendateien;
er verteilt ein Gesamtmaximum von 1 GiB gleichmäßig auf das vorhandene Layout
und setzt pro Datei `FILEGROWTH = 64MB`. Er legt außerdem den notwendigen `READER`-
SQL-Login vor dem Harness einmalig in der frischen Wegwerfinstanz an. Das
Passwort wird ausschließlich über stdin an SQLCMD übergeben; das SA-Passwort
liegt beim Containerstart in einer nur für den Runner lesbaren Env-Datei.
Serverrollen und Zusatzrechte werden nicht vergeben. Der Aufrufer läuft nur in einem neuen, markergebundenen
Container ohne Benutzerdatenbanken und entfernt ihn im Abschlussschritt nur,
wenn das SQL-Cleanup nachgewiesen ist.

Für QRY-023 unterdrückt `run_demo.py` nach einem SQL-Timeout den SQL-Cleanup und
meldet `FAIL_CLEANUP`, weil Prozessabbruch des lokalen Proxys kein Beweis für
serverseitige Abfragebeendigung oder TempDB-Freigabe ist. Bei unbewiesenem
Cleanup erhält die Route den Container als Diagnosezustand; auf einem ephemeren
GitHub-Runner endet er mit dem Job, auf einem selbstgehosteten Runner braucht er
eine separat geprüfte Bereinigung. PR #563 qualifizierte diese vorgeschlagene
CI-Route am 13.11.2026 auf allen drei festgebundenen Engines und allen zehn
Harnessphasen. Sie ersetzt keinen allgemeinen Runner-Prozessbaum- oder
Serverabbruchvertrag und aktiviert weder `runtime_authorized` noch einen
Katalogeintrag. PRs #566–#581 ergänzten auf allen drei Engines Live-Negativgegenproben: direkter
`SELECT`-Grant an READER auf `lab.MeasurementWaitSnapshot` plus
`db_datareader`-Mitgliedschaft (#566), explizites Objekt-`DENY` (#567),
`dbcreator`-Serverrollenmitgliedschaft (#568), fehlendes erwartetes
`lab.MeasurementWaitSnapshot` (#569), `VIEW SERVER STATE`-Servergrant (#570)
und explizites serverweites `DENY VIEW SERVER STATE` (#571), datenbankweiter
`VIEW DEFINITION`-Grant (#572) und Datenbank-`DENY VIEW DEFINITION` (#573),
direkter `CONNECT`-Grant und -DENY auf `TSQL Default TCP` (#574/#575),
unregistrierter gestoppter TSQL-Endpoint (#576/#577), direkte
`VIEW ANY DATABASE`-Grant- und -DENY-Zuweisungen (#578/#579),
`DENY CONNECT SQL` (#580) sowie direkte `securityadmin`-
Serverrollenmitgliedschaft (#581). Die ADMIN-Inventur wies die negativen
Berechtigungsfälle vor Korrektheit und Messung mit ihrer exakten Kategorie als
`FAIL_NOT_PROVEN` ab; markergebundener Cleanup und positiver Zehnphasenlauf
bestanden auf allen drei Builds. Die unregistrierte TSQL-Endpoint-Gegenprobe
(#576/#577) lief gemäß DEC-083 als letzte Instanzmutation nach dem positiven
Lauf; Endpoint-Drop und anschließende Instanzentfernung bestanden. Serverrollen,
Serverrechte und Endpointrechte wurden im owner-geprüften Container
wiederhergestellt und verifiziert. Der erste SQL-2025-Lauf von PR #581
scheiterte vor Setup im TempDB-Growth-Guard, weil zwei Dateien noch
`MAXSIZE = UNLIMITED` meldeten; nur dieser frische Job wurde wiederholt und
bestand vollständig. Absichtlich beschädigte SQL-Kataloge wurden nicht geprüft.
Allgemeine Runtimefreigabe und Produkt-/Katalogaufnahme bleiben offen.

PR #586 qualifizierte zusätzlich die T-SQL-Defense-in-Depth für ein
nachgestelltes Leerzeichen im RunToken auf SQL Server 2019/2022/2025. Die erste
unabhängige Reviewrunde fand, dass `LEN` und ASCII-`LIKE` den Wert nicht
zuverlässig zurückweisen; der Preflight vergleicht jetzt `DATALENGTH` und
`LEN`. Der Proxy verändert ausschließlich den vom Caller bereits validierten
RunToken beim `master`-Preflight, blockiert alle späteren Phasen und der
owner-geprüfte Container bestätigt die Abwesenheit einer Nutzerdatenbank.
PR #587 qualifizierte denselben Vergleichsrand für den Ziel-Datenbanknamen:
SQL-`=` kann nachgestellte Leerzeichen gleichsetzen und eine sprachabhängige
Kollation kann abweichende Groß-/Kleinschreibung als gleich behandeln. BIN2-
Vergleich und gleiche Bytelänge weisen diese Abweichungen zurück; die
Gegenprobe bestand auf allen drei Engines vor Setup, ohne eine Nutzerdatenbank
anzulegen. Microsoft Learn dokumentiert die Auffüllung beim
Zeichenkettenvergleich sowie BIN2-Codepunktvergleiche und `DATALENGTH`
(abgerufen am 13. November 2026; siehe die Quellenlinks im [Proposed-Harness
README](../../Demos/05_Query_Patterns/QRY-023_Graph_Tables/README.md)). PR #588
verbreiterte die Demo-ID-Variable vor der Guard-Prüfung und bindet die feste
Kennung an exakt sieben Bytes sowie den BIN2-Wert `QRY-023`. Die
Gegenkontrollen für nachgestellte Leerzeichen und eine case-variant
geschriebene ID mit passend abgeleitetem Zielnamen wurden auf allen drei
Engines vor Setup abgewiesen. Es entstand keine Nutzerdatenbank. Die drei
konkreten SQLCMD-Identitätsgrenzen RunToken, Zielname und Demo-ID sind damit
live qualifiziert; allgemeine Runtime-/Produkt-/Katalogfreigabe bleibt offen.
