# QRY-023 – SQL Graph Tables und relationale Pfadabfrage

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED`; integrierter Codeentwurf mit statischer Vertragsprüfung, ScriptDom-Grammatikparse und automatischer Enginequalifikation auf den drei festgeschriebenen SQL-Server-Builds; nicht katalogisiert |
| Sicherheitsstufe | `YELLOW` |
| Lernziel | `LO-M03-06` / `CLM-047` |
| Daten | ausschließlich synthetisch; 10.000 disjunkte Zwei-Kanten-Pfade plus kleines Korrektheitsoracle |
| Profile | Linux/AMD64-Images: SQL Server 2019/150, Build 15.0.4500.2; 2022/160, Build 16.0.4305.5; 2025/170, Build 17.0.5035.5; festgeschriebene und automatisiert qualifizierte Profile |
| Hostressourcen | Vorschlag: x86-64, 2 Kerne mit mindestens 2 GHz, 8 GiB RAM und 20 GiB freier Speicher; nicht empirisch qualifiziert |
| Containergrenze | Vorschlag: höchstens 2 CPU-Kerne, 4.096 MiB Speicher, SQL-Server-Limit 3.072 MiB; 900 Sekunden Lauf-/90 Sekunden Cleanupbudget |
| Runtime | automatisierter isolierter End-to-End-Lauf auf SQL Server 2019/2022/2025 bestanden; fünf synthetische Messpaare je Engine, keine Performanceaussage und keine menschliche Generalprobe |

## Zweck

Die Demo stellt denselben gerichteten Pfad einmal mit SQL Graph `MATCH` und
einmal mit relationalen Joins dar. Eine getrennte Fünf-Knoten-Probe prüft die
erwarteten Tupel `(1,2,5)` und `(1,3,5)`. Das Messprofil vergleicht danach
10.000 disjunkte Pfade mit identischem Dateninhalt. Der Umfang begründet keine
allgemeine Empfehlung für Graph- oder relationale Speicherung.

## Codeentwurf und vorgesehene Phasen

| Phase | Datei | Aufgabe |
|---|---|---|
| Preflight | `00_Preflight.sql` | Version, Datenbankname, CREATE DATABASE, vollständigen Benutzerdatenbankbestand und exakte Marker einer vorhandenen Zieldatenbank prüfen |
| Setup | `10_Setup.sql` | Eigene markierte Wegwerfdatenbank erstellen oder exakt passende wiederverwenden |
| Framework | `15_Framework.sql` | kanonische FWK-004-Messreferenz installieren |
| Workload | `20_Workload.sql` | 30.000 Knoten, 20.000 Kanten, kleines Oracle, Kandidatenindizes und Messprozedur anlegen |
| ADMIN permission inventory | `22_Admin_Permission_Inventory.sql` | READER-SID, Rollen, explizite Grants/DENYs, Zieldatenbankbestand und Endpoints read-only inventarisieren; bei unvollständiger Sicht oder Abweichung vor READER stoppen |
| Qualification preflight | `25_Qualification_Preflight.sql` | vollständige Marker, SELECT und SHOWPLAN vor den Abfragen prüfen |
| Korrektheit | `30_Correctness.sql` | kleine Oracle-Tupel sowie vollständige 10.000-Pfade-Ergebnismengen in beide Richtungen vergleichen |
| Messung | `40_Measurement.sql` | Warm-up und fünf gepaarte BASELINE/COMPARISON-Läufe mit alternierendem AB/BA erfassen |
| Plan | `50_Plan_Evidence.sql` | separate Actual-Plan-Diagnostik; Planläufe fließen nicht in Messwerte ein; sqlcmd gibt variable XML-Datentypen für diese auf zwei Abfragen begrenzte Phase ungekürzt aus |
| Cleanup | `90_Cleanup.sql` | Wegwerfdatenbank nur mit vollständigen Projekt-, Demo- und Run-Markern entfernen |

Der Entwurf heißt `manifest.proposed.json`, damit er von den bestehenden
Runtimekatalogen und automatischen Manifestmatrizen nicht als freigegebene
Demo erkannt wird. `YELLOW` erfordert im FWK-010-Aufrufer eine ausdrückliche
`--confirm-isolated-lab`-Bestätigung; das Manifest autorisiert selbst keinen
Lauf.

`15_Framework.sql` bindet `Demos/00_Framework/Sql/FWK_Measurement.sql` per
SQLCMD-`:r` ein. Der dokumentierte Harness-Aufruf startet deshalb aus dem
Repository-Stamm. Das Manifest ist noch nicht in einen allgemeinen
Ausführungspfad aufgenommen. Die Dateien bleiben `PROPOSED`; die isolierte technische
Enginequalifikation ist für die drei festgeschriebenen Profile bestanden und
ersetzt weder die menschliche Generalprobe noch eine Katalogfreigabe.

## Rechte und Grenzen

Die Rechte müssen fachlich getrennt werden: Setup benötigt `CREATE DATABASE`
sowie Tabellen-, Index- und synthetische Insert-Rechte; Korrektheit und
Die Korrektheitsphase benötigt `SELECT` auf den vier Query- und den vier
Oracle-Tabellen. Mess- und Planevidenz benötigen `SELECT` auf den vier
Querytabellen sowie `SHOWPLAN` auf der markierten Zieldatenbank. Messung
benötigt zusätzlich `SELECT` auf `lab.MeasurementRun` und `EXECUTE` auf
`lab.USP_Qry023MeasureVariant`; deren
interne Schreiboperationen setzen eine passende Ownership Chain voraus und
müssen in der Laufzeitqualifikation bestätigt werden. Cleanup benötigt das
Entfernen der eigenen Datenbank nach exakter Markerprüfung. Das vorgeschlagene Manifest weist
Setup-/Installationsphasen dem Profil `ADMIN` und Qualifikations-, Korrektheits-,
Mess- und Planphasen dem Profil `READER` zu; Cleanup erhält `ADMIN`. Der
FWK-010-Caller verlangt unterschiedliche SQL-Benutzernamen, liest ihre
Zugangsdaten aus `SQLPERF_SQL_USERNAME_ADMIN`/
`SQLPERF_SQL_PASSWORD_ADMIN` und den entsprechenden `READER`-Variablen und
übergibt das jeweilige Kennwort nur als `SQLCMDPASSWORD` an den Phasenprozess.
Der Client schaltet damit die konfigurierte Identität um. Ob die realen
SQL-Prinzipale die Sollrechte und keine darüber hinausgehenden Rechte besitzen,
ist nicht serverseitig verifiziert. Das bleibt ein Runtime-/Methodengate; die
aufgezählten Gesamtberechtigungen dürfen nicht als Minimalrechte ausgegeben
werden. `FWK-004` speichert keine Abfragetexte oder Pläne; es erfasst
Sessiondeltas. Fremde oder nicht vollständig markierte Ziele werden abgewiesen
und nicht entfernt.

Der aktuelle Qualifikationspreflight prüft, ob die benötigten positiven Rechte
vorliegen; er inventarisiert keine direkten, geerbten oder über Rollen
gewährten Berechtigungen. Eine Prüfung nur auf Mitgliedschaft in `sysadmin` oder
`db_owner` würde Minimalrechte ebenfalls nicht beweisen: `IS_SRVROLEMEMBER` und
`IS_ROLEMEMBER` fragen Rollenmitgliedschaft ab, nicht die zugrunde liegenden
Rechte, und benötigen `VIEW DEFINITION` auf der jeweiligen Rolle. Eine spätere
Überprivilegierungsprüfung muss daher effektive Rechte gezielt bewerten und
ihre Sichtbarkeit für `READER` fail-closed qualifizieren. Bis dahin bleibt die
Minimalrechte- und Runtimefreigabe offen.

Der Offlineentwurf für die Effektivrechteprüfung mit `sys.fn_my_permissions`
liegt in der [QRY-023-Effektivrechtequalifikation](../../../Documentation/Project_Planning/QRY023_EFFECTIVE_PERMISSION_DESIGN.md).
`DEC-083` akzeptiert `CONNECT SQL` als reguläres Loginrecht sowie die
dokumentierte `public`-Baseline `VIEW ANY DATABASE` ausschließlich auf einer
frischen, exklusiv für einen QRY-023-Run reservierten Wegwerfinstanz. Vor Setup darf keine
Benutzerdatenbank vorhanden sein (außer der exakt markierten Wiederaufnahme
desselben Runs); danach ist die markierte QRY-023-Datenbank die einzige
Benutzerdatenbank. Erlaubt sind nur `public` als READER-Server-/Datenbankrolle
und `CONNECT` aus `public` auf nachweislich standardmäßigen SQL-Endpoints.
Der Harness ändert weder Serverrechte noch `public`. Die read-only ADMIN-Endpoint-, Rollen-, SID- und explizite Rechteinventur
wurde in isolierten Wegwerfcontainern auf allen drei festgeschriebenen Engines
ausgeführt und bestanden. Die READER-Phase erfasst jetzt die Effektivrechte
für Server, Zieldatenbank, jeden Standardendpoint, `dbo`/`lab` und alle 13
gebundenen
Framework-/Demoobjekte mit `sys.fn_my_permissions` und vergleicht sie
fail-closed mit dem Manifest. Die ADMIN-Phase bestätigt unter ausreichender
Metadatensicht zuerst die Existenz aller 13 gebundenen Objekte, darunter drei intern genutzte Objekte,
die READER absichtlich nicht sehen kann. Sie gibt dafür einen festen
PASS-Marker sowie die begrenzte Endpointliste als SQLCMD-sichere ID-/UTF-16LE-
Hexdatensätze mit `G`- und `H`-Trennzeichen außerhalb des Hexalphabets
aus; der Caller validiert Objektmarker, Count, Grenzen, IDs, Namen und Encoding
vor dem nächsten SQL-Aufruf. Die tatsächliche
READER-Verbindung prüft anschließend `CONNECT` für jeden übergebenen Endpoint.
Der READER braucht dafür keine Endpointmetadatensicht. Die tatsächlichen
READER-Verbindungen bestanden auf allen drei festgeschriebenen Engine-Builds.
`manifest.proposed.json` hält den Vorschlagsstatus getrennt; der Offlinevalidator
allein führt keine Rechteprüfung aus. Ein expliziter Grant an READER oder `public` außerhalb des gebundenen
Objektinventars wird bereits durch die ADMIN-Inventur abgelehnt; unbekannte
Effektivrechte in allen geprüften Scopes blockieren den Lauf ebenfalls.
Microsoft beschreibt, dass `sys.fn_my_permissions` die Rechte des aktuellen
Aufrufkontexts zurückgibt und bei Fehler `NULL` liefert; die Funktion qualifiziert
für sich weder andere Principals noch Ownership-Chain-Wirkungen. Der Harness
prüfte die tatsächlichen READER-Verbindungen und den Messprozedurpfad auf allen
drei Builds. Eine Live-Gegenprobe mit zusätzlichem direktem READER-`SELECT`-Grant
und Mitgliedschaft in `db_datareader` wurde auf allen drei Builds vor den
Queryphasen fail-closed abgewiesen. Die seither ergänzten und auf den drei
Builds qualifizierten Live-Gegenproben für Objekt-DENY, Serverrollen und
Objektinventar, Server-/Datenbankrechte (einschließlich direktem
`VIEW ANY DATABASE`-GRANT und -DENY sowie `CONNECT SQL`-DENY) und Endpoints
samt Cleanup sind im [aktuellen
Ausführungsstatus](../../../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md)
nach PR dokumentiert. QRY-023 bleibt dabei `PROPOSED` und nicht katalogisiert.

`DEC-084` schließt den konkreten Verbindungsfehler im Setup und in dessen
Offline-Vertragsprüfung:
FWK-010 übergibt den READER-Profilnamen über die explizite SQLCMD-Variable
`ReaderLogin`; der Caller erlaubt dafür nur `[A-Za-z0-9_]{1,128}`. Setup
verlangt einen aktiven `SQL_LOGIN` und erstellt oder bestätigt dessen
Datenbankbenutzer ausschließlich in der exakt markierten QRY-023-Datenbank.
Reservierte FWK-010-SQLCMD-Variablennamen können nicht überschrieben werden.
Namens- oder SID-Konflikte brechen fail-closed ab. Die Setup- und SID-Prüfung
lief auf allen drei gepinnten SQL-Server-Engines erfolgreich durch.

Der vorgeschlagene isolierte CI-Aufrufer legt den dafür benötigten `READER`-
SQL-Login vor dem Harness einmalig in der frischen Wegwerfinstanz an. Das
separate Passwort gelangt ausschließlich über SQLCMD-stdin und phasengebundene
Umgebungsvariablen; es ist keine allgemeine Loginprovisionierung und ändert
keine Serverrolle oder Zusatzberechtigung.

Das Proposed-Manifest bindet jetzt zusätzlich eine versionierte
READER-Effektivrechte-Sollmenge für Server, ADMIN-inventarisierte
Standardendpoints, Datenbank, `dbo`/`lab` und alle 13 erwarteten
QRY-023-/FWK-004-Securables. Der Offlinevalidator schützt die exakte Vertragsform sowie Fail-closed Regeln
für Duplikate, fehlende Resultate, Spaltenrechte und unerwartete Objekte. Der
Vertrag trägt `ENGINE_QUALIFIED_PROPOSED_NOT_RUNTIME_AUTHORIZED`. Der Validator
selbst prüft keine Live-Rechte; die getrennte Enginequalifikation tat dies unter
den tatsächlichen ADMIN- und READER-Verbindungen und änderte keine Rechte.

Vor Setup verlangt der `PREFLIGHT` eine vollständige Sicht auf
`sys.databases` und lässt nur eine leere Instanz oder die exakt markierte
Wiederaufnahme desselben Runs zu. Nach `WORKLOAD` läuft die neue
`ADMIN_PERMISSION_INVENTORY`-Phase in der markierten Zieldatenbank. Sie bindet
den aktiven SQL-Login an den gleichnamigen Datenbankbenutzer mit identischer
SID, verwirft explizite Zusatzrollen und nicht deklarierte Grants/DENYs und
inventarisiert Benutzerdatenbanken sowie Endpoints. SQL Server 2022+ verlangt
serverseitig `VIEW ANY SECURITY DEFINITION`, `VIEW ANY DEFINITION`,
`VIEW SERVER SECURITY STATE` und `VIEW ANY DATABASE` sowie in der
Zieldatenbank `VIEW SECURITY DEFINITION` und `VIEW DEFINITION`. SQL Server
2019 verlangt stattdessen `VIEW ANY DEFINITION`, `VIEW SERVER STATE` und
`VIEW ANY DATABASE` sowie `VIEW DEFINITION` in der Zieldatenbank. Die
Definitionsrechte sind nötig, um auch benutzerdefinierte
Rollenmitgliedschaften vollständig zu sehen; das Skript nutzt sie nur lesend.
Die unveränderte Datenbankrolle `public` besitzt außerdem die von Microsoft
dokumentierte Plattformbaseline ([Datenbankrollen](https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/database-level-roles?view=sql-server-ver17)):
`CONNECT`, `VIEW ANY COLUMN ENCRYPTION KEY DEFINITION`,
`VIEW ANY COLUMN MASTER KEY DEFINITION` und `SELECT` auf systemeigenen
Systemobjekten. `sys.database_permissions` kennzeichnet Systemobjekte mit
negativer `major_id` ([Katalogsicht](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-permissions-transact-sql?view=sql-server-ver17)).
Die exakte `public`-SELECT-Menge wurde in frischen, digestgebundenen
Wegwerfcontainern für die festgelegten Builds 15.0.4500.2, 16.0.4305.5 und
17.0.5035.5 erfasst: 186, 226 beziehungsweise 232 effektive `public`-
`SELECT`-Grants auf negative Systemobjekt-IDs in einer neu angelegten
Nutzerdatenbank. Dazu gehören sieben PDW-Kompatibilitätsviews, die nicht in
`sys.system_objects` erscheinen; eine Inventur nur über diese Sicht wäre
unvollständig. Der vollständige Eintragssatz und die
kanonischen SHA-256-Werte stehen in der [Baseline](../../../Documentation/Project_Planning/QRY023_PUBLIC_SYSTEM_OBJECT_BASELINE.json)
und sind als `SRC-160` registriert. Der ADMIN-Preflight akzeptiert diese Rechte
nur bei exakter Build-, Anzahl- und Digestübereinstimmung. Ein unbekannter Build,
eine abweichende Menge oder fehlende Metadatensicht bleibt `FAIL_NOT_PROVEN`.
Die negative `major_id`-Kennzeichnung allein genügt weiterhin nicht. Die
Kontrollabfragen in `master` ergaben deutlich größere und abweichende Mengen;
sie werden ausdrücklich nicht als Sollmenge für die QRY-023-Zieldatenbank
verwendet. `public`-Grants auf QRY-023-/FWK-004-Nutzobjekten und direkte
Systemobjektgrants an READER bleiben unzulässig. Die getrennte Baselineerfassung
führte weder QRY-023-Skripte noch Rechteänderungen aus; der Harness wurde in
einem separaten Schritt auf den drei Engines qualifiziert.
Fehlt eine dieser Sichtbarkeiten oder erscheint ein unbekannter Endpoint, eine
weitere READER-Rolle oder ein nicht deklarierter Berechtigungszustand,
endet die Phase mit `FAIL_NOT_PROVEN`. Die Phase vergibt, entzieht und ändert
keine Rechte. Ihre ADMIN-Metadatenrechte sind keine READER-Rechte und werden
nicht durch diesen statischen Entwurf bereitgestellt.

Der statische Validator schützt Vor- und Nach-Setup-Inventar, die
ADMIN-Phasenbindung und das Verbot von Rechteänderungen; synthetische Tests
prüfen unter anderem entfernte Sichtbarkeitsgates, SID-Bindung und verbotene
Grants. ScriptDom parst das neue T-SQL unter den Grammatiken 150, 160 und 170.
Das belegt weder Metadatenvollständigkeit noch erfolgreiche T-SQL-Ausführung.
Der Vertragsvalidator deckt diese synthetischen Negativfälle ab. Die
automatisierten Engine-Läufe qualifizieren den positiven Standardpfad. Auf
allen drei Builds wurden vor den Queryphasen folgende Live-Negativfälle
abgewiesen: zusätzlicher direkter READER-`SELECT`-Grant, Mitgliedschaft in
`db_datareader`, explizites Objekt-`DENY`, Mitgliedschaft in der
Serverrolle `dbcreator`, fehlendes erwartetes Tabellenobjekt, ein serverweiter
`VIEW SERVER STATE`-Grant sowie ein explizites serverweites
`DENY VIEW SERVER STATE`, datenbankweiter `VIEW DEFINITION`-Grant und
datenbankweites `DENY VIEW DEFINITION`, direkte `CONNECT`-Grant- und `DENY`-
Gegenproben auf dem Standardendpoint `TSQL Default TCP`, direkte
`VIEW ANY DATABASE`-Grant- und `DENY`-Gegenproben sowie `DENY CONNECT SQL`.
Jeder Fall verlangte die exakte
Abweichungskategorie, `FAIL_NOT_PROVEN`, keinen Eintritt in Queryphasen und
bestandenes markergebundenes Cleanup; nach temporären Rechteänderungen wurde
deren Wiederherstellung separat geprüft. Der anschließende positive
Zehnphasenlauf bestand ebenfalls. Eine zusätzliche direkte
`securityadmin`-Serverrollenmitgliedschaft wird als nächster isolierter
Inventarfall qualifiziert. Absichtlich beschädigte SQL-Kataloge wurden nicht
ausgeführt. QRY-023 bleibt vorgeschlagen
und nicht katalogisiert.

Der statische Harnessvalidator synchronisiert die direkten `dbo`-/`lab`-
Objektreferenzen der als `READER` markierten Phasenskripte mit den
`HAS_PERMS_BY_NAME`-Prüfungen im Qualifikationspreflight. Nicht zuordenbare
`dbo`-/`lab`-Referenzen, datenbankqualifizierte Namen und dynamische
`EXEC`-Formen werden fail-closed zurückgewiesen; als Prozeduraufruf ist nur
`lab.USP_Qry023MeasureVariant` zugelassen. Für diese Phasen erlaubt die Textprüfung direkt erkennbare
schreibende Ziele nur an lokalen Tabellenvariablen; erkannte persistente DML-,
`SELECT INTO`-, `BULK INSERT`-, DDL-, DBCC- und Rechteänderungen, direkte
Datenbank-/Sicherheitskontextwechsel sowie SQLCMD-Controlzeilen und
Batchtrenner `GO` mit oder ohne Wiederholungszahl werden abgelehnt; nur
`:setvar SQLCMDMAXVARTYPEWIDTH 0` bleibt in
`50_Plan_Evidence.sql` zugelassen. Das
schützt die statische Zuordnung der aktuellen Skripttexte, ist
aber kein T-SQL-AST-/Datenflussnachweis, kein Serverrechteinventar und kein
Nachweis des tatsächlichen Verhaltens unter SQL Server. Die Runtime- und
Effektivberechtigungsgates bleiben offen.

Der Messpfad hält außerdem die optionale FWK-004-Wartezeiterfassung aus:
`lab.USP_Qry023MeasureVariant` ruft `USP_BeginMeasurement` mit
`@CaptureSessionWaits=0` auf. Die Messprozeduren lesen dadurch nur die eigene
Session aus `sys.dm_exec_sessions`; Microsoft dokumentiert den Zugriff auf die
eigene Session ohne Zusatzrecht. Die bedingten Abfragen auf
`sys.dm_exec_session_wait_stats` werden übersprungen. Auf SQL Server 2022 und
neuer wäre für diese Wait-Statistik DMV das Serverrecht
`VIEW SERVER PERFORMANCE STATE` erforderlich. Dieses Recht gehört daher nicht
zum QRY-023-READER-Profil; eine Negativregression schützt den festen Wert `0`.
Quellen, abgerufen am 12. November 2026: [`sys.dm_exec_sessions`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-exec-sessions-transact-sql?view=sql-server-ver17), [`sys.dm_exec_session_wait_stats`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-exec-session-wait-stats-transact-sql?view=sql-server-ver17).

Der vorgeschlagene Ausführungs-Sicherheitsvertrag nennt 1 GiB als erwartete
Größenordnung/Obergrenze der QRY-023-Testdatenbank und 1 GiB als Obergrenze für
zusätzliches TempDB-Wachstum; zugleich ist höchstens eine SQL-Session aktiv.
Diese Werte sind noch nicht als allgemeine Runtimequalifikation abgenommen. Der
separate vorgeschlagene CI-Aufrufer setzt für seine frische Wegwerfinstanz 2 CPU,
4 GiB Container-RAM und 3 GiB SQL-Speicher. Er akzeptiert ein TempDB-Layout aus
einer Logdatei und 1–15 Datendateien, verteilt das Maximalbudget von 1 GiB auf
alle Dateien und setzt 64 MiB Wachstum pro Datei; vor Setup verifiziert er die
Grenzwerte und das leere Benutzerdatenbankinventar. Der Aufrufer bleibt vom
Runtimekatalog getrennt.
Bei einem QRY-023-SQL-Timeout unterdrückt der FWK-010-Runner das SQL-Cleanup und
meldet `FAIL_CLEANUP`, weil serverseitiges Ende und TempDB-Freigabe nicht
bewiesen sind. Der äußere CI-Schritt entfernt den exakt markierten
Wegwerfcontainer nur nach bestätigtem SQL-Cleanup. Bei unbewiesenem Cleanup
bleibt er als Diagnosezustand erhalten. Ein ephemerer GitHub-Runner endet nach
dem Job; ein selbstgehosteter Runner benötigt eine separat geprüfte Bereinigung.
Ohne diesen isolierten Aufrufer können bei erzwungenem Abbruch synthetische
Teilobjekte verbleiben; ein
allgemeiner Prozess-/Serverabbruchvertrag und eine Produktabnahme sind damit
nicht qualifiziert. Unbekanntes Eigentum oder fehlgeschlagenes Cleanup führt
nicht zum erzwungenen Entfernen eines nicht eindeutig markierten Ziels.

Der FWK-010-Caller begrenzt das RunToken auf 1 bis 20 ASCII-Zeichen und verlangt
ein alphanumerisches erstes Zeichen. Separat prüft der vorgeschlagene
read-only SQL-Preflight den erlaubten ASCII-Zeichensatz und die Bytegrenze.
`DATALENGTH` ergänzt die Zeichenprüfung, weil `LEN`
nachgestellte Leerzeichen ausschließt und ASCII-`LIKE` sie im Suchwert
ignoriert; siehe die Microsoft-Dokumentation zu [`LEN`](https://learn.microsoft.com/en-us/sql/t-sql/functions/len-transact-sql?view=sql-server-ver17) und [`LIKE`](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver17). Diese Bedingung ist offline statisch geprüft, aber noch nicht mit SQL Server ausgeführt.

SQLCMD setzt Skriptvariablen an ihren `$(Name)`-Vorkommen ein, auch in
Zeichenliteralen. Daraus folgt als Sicherheitsinferenz, dass der T-SQL-
Preflight keine SQLCMD-Eingabeinjektion verhindert: Eine unsichere Eingabe kann
die Skriptstruktur vor Auswertung der Guards verändern. Ein künftiger Harness-
Aufrufer muss Demo-ID, RunToken und Zielnamen vor dem SQLCMD-Aufruf exakt gegen
den Vertrag allowlisten. Der vorhandene FWK-010-Caller `run_demo.py` prüft das
`sqlcmd_input_validation`-Vertragsobjekt bereits beim Laden des Manifests,
bevor SQLCMD aufgelöst oder gestartet wird. Die vorgeschlagene Demo ist aber
weiterhin nicht katalogisiert oder zur Ausführung freigegeben.
Die exakten Anforderungen sind im Feld `sqlcmd_input_validation` des
vorgeschlagenen Manifests maschinenlesbar festgelegt und durch statische sowie
synthetische Caller-Tests geprüft. Das Feld allein führt keine Validierung aus.

Der automatisierte QRY-023-Prüflauf wurde auf allen drei gepinnten Builds
ausgeführt und bestanden. Der read-only Preflight akzeptiert
für die vorgeschlagenen Linux-Imageprofile ausschließlich Builds `15.0.4500.2`,
`16.0.4305.5` und `17.0.5035.5`; die Setupphase prüft denselben Pin nochmals
vor der Datenbankanlage. Das sind reproduzierbare Designpins, die gemäß dem
Servicingquellencheck vom 12. November 2026 weiterhin aktuell sind, keine
Graph-Mindestbuilds. Die
Images werben diese Builds über `com.microsoft.version`. Die AMD64-Manifestdigests
lauten für 2019 `sha256:07d7dedecdbfcf6776035dc5eefb5bfd9aa1804b2f6b99f7dedb397d8a599069`,
2022 `sha256:cf8f0ab2ebe61feec2eed2629061a07d247f791c2a8ddda74a4ac9f06a291718`
und 2025 `sha256:6972fb831759433def6a34e107fa32a85230bff5af8014c6263fe4633ea9cc0f`.
Die 2019-/2022-Tags tragen `GDR12` bzw. `GDR1` und stimmen mit den aktuellen
Linux-CU+GDR-Builds überein. Imagekonfiguration und Produktlabel belegen nicht
den gestarteten `sqlservr`; jeder spätere Lauf muss `SERVERPROPERTY` erfassen
und das Image per Manifestdigest binden. SQL Graph wird
laut Microsoft-Editionsmatrizen in den Editionen von 2019, 2022 und 2025 angeboten.
Der Preflight protokolliert die tatsächliche Edition, beschränkt Graph aber
nicht auf eine bestimmte Edition.

Ein angehefteter Microsoft-ScriptDom-Parser prüft die acht ausführbaren
T-SQL-Dateien mit den Grammatiken für SQL Server 2019, 2022 und 2025. Den
SQLCMD-`:r`-Wrapper prüft er separat auf den erwarteten Include; er parst ihn
nicht als T-SQL. Platzhalter werden nur im Parserprozess synthetisch ersetzt.
Ein Parser-PASS ist keine Kompilierung gegen eine SQL-Server-Engine und belegt
keine Objektbindung, Berechtigungen oder Laufzeitsemantik. Ein Offlinevalidator
prüft zusätzlich Manifestphasen, Markerbindung, Workloadarithmetik,
Ergebnisorakel, Messreihenfolge, Plantrennung und den Nicht-Katalogstatus.

`DEC-079` genehmigt die Methodenbasis; `DEC-080` akzeptiert die acht
ausführbaren T-SQL-Dateien nur für statische ScriptDom-Syntax 150/160/170;
`DEC-081` bestätigt die Buildpins als aktuelle Linux-Servicingstände am
12.11.2026. `DEC-082` bestätigt am selben Tag die OCI-Manifest-/Konfigurations-
digests und Produktlabels gegen den vorgeschlagenen Lock. Das belegt keinen
gestarteten SQL-Server-Prozess.
Vor einer Katalog- oder allgemeinen Runtimeaufnahme bleiben formale
Produktabnahme und allgemeine Runtimefreigabe offen. Ein eigener vorgeschlagener
CI-Aufrufer ist inzwischen integriert und auf den drei festgeschriebenen
Engine-Builds ausgeführt; er verwendet begrenzte Wegwerfinstanzen und separate
ADMIN-/READER-Anmeldungen. Das qualifiziert nur diesen isolierten Einzelrun-
Pfad, nicht einen allgemeinen Runtimeworkflow oder eine Katalogaufnahme. Die
menschliche Generalprobe bleibt wie beauftragt ausgeschlossen.

Der Ressourcenrahmen steht als Vorschlag im `resources`-Abschnitt von
[`container-images.proposed.json`](container-images.proposed.json). Er ist aus
Microsofts Linux-Mindestanforderungen und der geforderten Trennung zwischen
Container- und SQL-Server-Speichergrenze abgeleitet. 8/20 GiB Hostreserve sowie
4/3 GiB Container-/Enginegrenze sind Projektwerte ohne QRY-023-Laufmessung;
der vorgeschlagene CI-Aufrufer prüft Hostressourcen und setzt die Container-
und SQL-Server-Grenzen vor Start durch. Diese Werte sind keine gemessenen
Anwendungsressourcen oder Performancegrenzen.

## Verträge und Reviews

- [Statischer Demoentwurf](../../../Documentation/Project_Planning/GRAPH_TABLES_DEMO_CONCEPT.md)
- [Messworkload](../../../Documentation/Project_Planning/GRAPH_TABLES_MEASUREMENT_WORKLOAD_DESIGN.md)
- [Quellen- und Methodenreview](../../../Documentation/Project_Planning/GRAPH_TABLES_METHOD_REVIEW.md)
- [Editions- und Buildreview](../../../Documentation/Project_Planning/GRAPH_TABLES_BUILD_EDITION_REVIEW.md)
- [ScriptDom-Grammatikprüfung](../../../Documentation/Project_Planning/GRAPH_TABLES_SCRIPTDOM_PARSER_REVIEW.md)
- [Coverage-Prüfung des Proposed Harness](../../../Documentation/Project_Planning/QRY023_PROPOSED_HARNESS_REVIEW.md)
- [Normative Laufgrenze und Entwurf der Effektivrechtequalifikation](../../../Documentation/Project_Planning/QRY023_EFFECTIVE_PERMISSION_DESIGN.md)
- Vorgeschlagener unveränderlicher Image-Lock: [`container-images.proposed.json`](container-images.proposed.json); nicht von einem Runtimeworkflow konsumiert und nicht ausführungsberechtigend.
- Framework: `FWK-002`, `FWK-003`, `FWK-004`, `FWK-005`, `FWK-008`, `FWK-010`, `FWK-011` und `FWK-012`.
