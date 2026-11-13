# QRY-023: Effektivrechtequalifikation

Stand: 13. November 2026
Status: ADMIN-Inventur und READER-Exact-set-Preflight sind offline implementiert;
keiner der beiden Pfade ist auf SQL Server enginequalifiziert

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
Das ist noch keine Implementierung oder Laufqualifikation. Der spätere Prüfer
muss die vollständige, vorab versionierte Sollmenge je Securable und ihre
Vererbung aus diesem Vertrag abbilden; unbekannte oder nicht inventarisierbare
Rechte bleiben `NOT_PROVEN`. SQL-Prinzipalbindung, tatsächliche Effektivrechte,
Ownership-Chain-Wirkung, Runtime-Durchsetzung und QRY-023-Promotion bleiben
separate offene Gates.

Im Folgenden bezeichnet FWK-004 die sessionbezogene Messreferenz des Projekts;
FWK-010 bezeichnet den SQL-Demoaufrufer mit phasengebundenen Credential-
Profilen. `ADMIN` und `READER` sind die im vorgeschlagenen Manifest deklarierten
Profilnamen.

## Vorläufige Phasen- und Objektmatrix

| Identität / Phase | Bestehender Ablauf | Vorläufig nötiger Zugriffskandidat | Zusätzliche Qualifikation |
|---|---|---|---|
| `ADMIN` / `PREFLIGHT` | Read-only Prüfung in `master`, vollständige Benutzerdatenbanksicht und Markerprüfung eines vorhandenen Ziels | `VIEW ANY DATABASE`; eines der bereits deklarierten Rechte zum Anlegen der Testdatenbank | Vor Setup ist nur eine leere Instanz oder die exakte markierte Wiederaufnahme zulässig |
| `ADMIN` / `SETUP`, `FRAMEWORK`, `WORKLOAD` | Wegwerfdatenbank, FWK-004 und synthetische Objekte aufbauen | Datenbank, Schema, Tabellen, Prozeduren, Indizes und synthetische Inserts gemäß Setupskripten | Keine Minimalrechteaussage; Ziel muss eigens isoliert und vollständig markiert sein |
| `ADMIN` / `ADMIN_PERMISSION_INVENTORY` | READER-Login und Datenbankbenutzer binden sowie Rollen, explizite Rechte, Datenbanken und Endpoints vollständig inventarisieren | Read-only Katalogzugriff auf die markierte Zieldatenbank | Offline implementiert; fehlende Metadatensicht oder Abweichung führt zu `FAIL_NOT_PROVEN`; keine Rechtevergabe |
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
späteren Lauf nachgewiesen werden.

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
im Offlinevalidator objektgenau gebunden. Synthetische Regressionen schützen
gegen zusätzliches Datenbankrecht, unvollständige Objektinventur und
runtime-abgeleitete Sollwerte. Das prüft nur die Stabilität des vorgeschlagenen
Vertrags, weder SQL-Ausführung noch tatsächliche `sys.fn_my_permissions`-
Ausgaben. Der Kandidat bleibt `DESIGN_ONLY_NOT_ENGINE_QUALIFIED`.

## Geplante unabhängige Prüffälle

- Jede der acht Query-/Oracletabellen besitzt genau die vorgesehene effektive
  `SELECT`-Menge.
- Die Messphase besitzt das vorgesehene `EXECUTE` und `SELECT`; ein direkter
  `INSERT`, `UPDATE`, `DELETE`, `ALTER` oder `CONTROL`-Zugriff wird erkannt.
- Ein zusätzliches `SELECT` auf Schema- oder Datenbankebene wird erkannt, auch
  wenn alle einzelnen Tabellen weiterhin `SELECT` melden.
- Ein Recht auf einem zusätzlichen benutzerdefinierten Objekt wird erkannt;
  ein unerwartetes Objekt selbst stoppt den Ablauf.
- Zusätzliche Rollen-, Festrollen- und serverweite Rechte werden entweder
  explizit erkannt oder bleiben `NOT_PROVEN`; unbekannte Rechte dürfen nicht
  ignoriert werden.
- Jede Server- und Endpointbaseline wird mit dem tatsächlichen Endpointinventar,
  `public`-Mitgliedschaft und ADMIN-seitig sichtbaren expliziten Grants gebunden;
  ein benutzerdefinierter Endpoint oder eine weitere Benutzerdatenbank stoppt.
- Funktionsfehler, `NULL`, leere/fehlende Resultsets, doppelte Zeilen,
  unvollständige Spaltenresultate, veränderte Marker und Principalwechsel
  ergeben keinen PASS.
- Der Preflight läuft in jeder Readerphase tatsächlich unter dem für diese
  Phase deklarierten Profil und vor jeder Korrektheits-, Mess- oder Planabfrage.

Diese Fälle sind geplante Design-Gegenproben. Es wurden dafür keine Tests,
T-SQL-Änderungen oder SQL-Server-Läufe erstellt beziehungsweise ausgeführt.

## Quellen und nächste Grenze

- Microsoft Learn, [`sys.fn_my_permissions`](https://learn.microsoft.com/en-us/sql/relational-databases/system-functions/sys-fn-my-permissions-transact-sql?view=sql-server-ver17): effektive Rechte des aufrufenden Kontexts, unterstützte Securable-Klassen einschließlich `ENDPOINT`, `NULL` bei Abfragefehler und benötigter `public`-Mitgliedschaftszustand; abgerufen am 12. November 2026.
- Microsoft Learn, [effektive Database-Engine-Berechtigungen](https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/determining-effective-database-engine-permissions?view=sql-server-ver17): Zusammenwirken des granularen und Festrollensystems sowie Sonderbehandlung von `sysadmin`; abgerufen am 12. November 2026.
- Microsoft Learn, [Database-Engine-Berechtigungen](https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/getting-started-with-database-engine-permissions?view=sql-server-ver17): Vererbung durch Datenbank-/Schemahierarchie und weiterreichende `CONTROL`-Rechte; abgerufen am 12. November 2026.
- Microsoft Learn, [`sys.databases`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-databases-transact-sql?view=sql-server-ver17) und [Server-`public`-Berechtigungen](https://learn.microsoft.com/en-us/sql/relational-databases/policy-based-management/server-public-permissions?view=sql-server-ver17): Standard-`VIEW ANY DATABASE`, automatische `CONNECT SQL`-Berechtigung und Endpoint-`CONNECT`; abgerufen am 12. November 2026.
- Microsoft Learn, [Serverrollen](https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/server-level-roles?view=sql-server-ver17): neue SQL-Server-2022-Rollen und in Datenbanken weiterwirkende Rechte; abgerufen am 12. November 2026.
- Microsoft Learn, [Datenbankrollen](https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/database-level-roles?view=sql-server-ver17) und [`sys.fn_builtin_permissions`](https://learn.microsoft.com/en-us/sql/relational-databases/system-functions/sys-fn-builtin-permissions-transact-sql?view=sql-server-ver17): `public`-Datenbank-`CONNECT` und die vordefinierte Rechtehierarchie; abgerufen am 12. November 2026, in `SRC-158` ergänzt.
- Microsoft Learn, [`sys.server_permissions`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-server-permissions-transact-sql?view=sql-server-ver17), [`sys.server_role_members`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-server-role-members-transact-sql?view=sql-server-ver17), [`sys.database_permissions`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-permissions-transact-sql?view=sql-server-ver17), [`sys.database_role_members`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-role-members-transact-sql?view=sql-server-ver17), [`sys.endpoints`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-endpoints-transact-sql?view=sql-server-ver17) und [Metadatensichtbarkeit](https://learn.microsoft.com/en-us/sql/relational-databases/security/metadata-visibility-configuration?view=sql-server-ver17): versionierte Security-Katalogrechte und Grenzen expliziter Permission-Zeilen; abgerufen am 13. November 2026, in `SRC-159` ergänzt.
- Bestehender QRY-023-Vertrag: [Proposed-Harness README](../../Demos/05_Query_Patterns/QRY-023_Graph_Tables/README.md), [Proposed-Manifest](../../Demos/05_Query_Patterns/QRY-023_Graph_Tables/manifest.proposed.json) und [Methodenreview](GRAPH_TABLES_METHOD_REVIEW.md).
- Die wiederverwendeten Microsoft-Primärquellen sind als [`SRC-158` und `SRC-159`](../Research/SOURCE_REGISTER.md#qry-023--effektivrechte-und-sql-server-public-baseline) im Quellenregister zusammengeführt.

Die konkrete Methodenentscheidung ist in [DEC-083](../../.ai/DECISIONS.md)
registriert. Der spätere Harness bleibt für die tatsächliche Inventur und
Sollmengenprüfung verantwortlich; dieser Vertrag führt weder eine
SQL-Server-Abfrage aus noch belegt er eine reale Rechtevergabe.

`22_Admin_Permission_Inventory.sql` setzt den ADMIN-Anteil read-only um;
`25_Qualification_Preflight.sql` vergleicht unter der echten READER-Verbindung
effektive Server-, Datenbank-, Schema- und Objektrechte mit dem statischen
Exact-set-Vertrag. Die ADMIN-Inventur bestätigt den Objektnamen-/Typensatz und
übergibt den Endpointbestand; READER prüft `CONNECT` pro Endpoint. Die Umsetzung
bleibt offline und engineunqualifiziert.
Er prüft die exakte Login-/Datenbankbenutzer-SID, verwirft explizite
Server-/Datenbankrollen, inventarisiert die expliziten Grants/DENYs an READER
und `public`, begrenzt den Benutzerdatenbankbestand und weist benutzerdefinierte
Endpoints zurück. Ein `public`-SELECT auf Systemobjekten bleibt bis zur exakten,
versionsgebundenen Inventur der Standardobjektmenge ausdrücklich `NOT_PROVEN`;
negative `major_id` allein ist kein Allowlist-Nachweis. Die READER-Objektgrants
werden nur auf eine zulässige Sollmenge begrenzt; fehlende Laufrechte werden
weiterhin erst durch den
nachfolgenden tatsächlichen READER-Preflight erkannt. Der Vor-Setup-Preflight
verlangt vollständige Datenbanksicht und blockiert jede fremde
Benutzerdatenbank vor Setup.

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
Ownership-Chain-Wirkung. QRY-023 bleibt `PROPOSED` und ohne Runtimequalifikation.
