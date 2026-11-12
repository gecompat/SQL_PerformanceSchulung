# QRY-023 – SQL Graph Tables und relationale Pfadabfrage

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED`; integrierter Codeentwurf mit statischer Vertragsprüfung und ScriptDom-Grammatikparse, nicht katalogisiert |
| Sicherheitsstufe | `YELLOW` |
| Lernziel | `LO-M03-06` / `CLM-047` |
| Daten | ausschließlich synthetisch; 10.000 disjunkte Zwei-Kanten-Pfade plus kleines Korrektheitsoracle |
| Profile | Linux/AMD64-Images: SQL Server 2019/150, Build 15.0.4500.2; 2022/160, Build 16.0.4305.5; 2025/170, Build 17.0.5035.5; vorgeschlagene Qualifikationspins, keine Runtimequalifikation |
| Hostressourcen | Vorschlag: x86-64, 2 Kerne mit mindestens 2 GHz, 8 GiB RAM und 20 GiB freier Speicher; nicht empirisch qualifiziert |
| Containergrenze | Vorschlag: höchstens 2 CPU-Kerne, 4.096 MiB Speicher, SQL-Server-Limit 3.072 MiB; 900 Sekunden Lauf-/90 Sekunden Cleanupbudget |
| Runtime | nicht ausgeführt; keine Performanceaussage |

## Zweck

Die Demo stellt denselben gerichteten Pfad einmal mit SQL Graph `MATCH` und
einmal mit relationalen Joins dar. Eine getrennte Fünf-Knoten-Probe prüft die
erwarteten Tupel `(1,2,5)` und `(1,3,5)`. Das Messprofil vergleicht danach
10.000 disjunkte Pfade mit identischem Dateninhalt. Der Umfang begründet keine
allgemeine Empfehlung für Graph- oder relationale Speicherung.

## Codeentwurf und vorgesehene Phasen

| Phase | Datei | Aufgabe |
|---|---|---|
| Preflight | `00_Preflight.sql` | Version, Datenbankname, CREATE DATABASE und exakte Marker einer vorhandenen Zieldatenbank prüfen |
| Setup | `10_Setup.sql` | Eigene markierte Wegwerfdatenbank erstellen oder exakt passende wiederverwenden |
| Framework | `15_Framework.sql` | kanonische FWK-004-Messreferenz installieren |
| Workload | `20_Workload.sql` | 30.000 Knoten, 20.000 Kanten, kleines Oracle, Kandidatenindizes und Messprozedur anlegen |
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
Ausführungspfad aufgenommen. Die Dateien sind ein nicht ausgeführter Entwurf
und keine qualifizierte Demoimplementierung.

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

Der nächste offline zu konkretisierende Prüfansatz ist `sys.fn_my_permissions` im
tatsächlichen `READER`-Verbindungskontext. Die vorgesehene Prüfung muss die
effektiven Rechte am Server, an der markierten Datenbank, an den verwendeten
Schemas und an jedem vorhandenen QRY-023-Objekt gegen eine vorab festgelegte
Sollmenge vergleichen. Die Sollmenge ist aus den konkreten Phasen abzuleiten;
`SELECT` auf den Querytabellen und Messdaten, `EXECUTE` auf der Messprozedur
sowie `SHOWPLAN` sind Mindestanforderungen, keine vollständige Sollmenge.
Unbekannte, nicht auflistbare oder zusätzliche effektive Rechte müssen den
Preflight fail-closed abbrechen. Die Prüfung ist im jeweiligen Kontext
auszuführen, weil `fn_my_permissions` die Rechte des aufrufenden Principals
auswertet. Sie belegt weder die Berechtigungen anderer Principals noch die
Ownership-Chain-Wirkung der internen Schreiboperationen; beides bleibt ein
separates Laufzeitgate. Diese Prüfstrategie ist ein Designvorschlag und noch
nicht implementiert oder auf SQL Server qualifiziert. Siehe Microsofts
[`sys.fn_my_permissions`](https://learn.microsoft.com/en-us/sql/relational-databases/system-functions/sys-fn-my-permissions-transact-sql?view=sql-server-ver17)-Dokumentation.
Die genannten QRY-023-Objekte allein bilden keine vollständige Instanz- oder
Datenbankinventur: Ein Grant auf einem anderen Objekt würde damit nicht
ausgeschlossen. Ein späterer Minimalrechtnachweis muss zusätzliche relevante
Securables und Spaltenrechte vollständig abdecken oder seine Aussage auf eine
qualifizierte, dedizierte Wegwerfinstanz mit gebundenem Bestand beschränken.

Der statische Harnessvalidator synchronisiert die direkten `dbo`-/`lab`-
Objektreferenzen der als `READER` markierten Phasenskripte mit den
`HAS_PERMS_BY_NAME`-Prüfungen im Qualifikationspreflight. Nicht zuordenbare
`dbo`-/`lab`-Referenzen, datenbankqualifizierte Namen und dynamische
`EXEC`-Formen werden fail-closed zurückgewiesen; als Prozeduraufruf ist nur
`lab.USP_Qry023MeasureVariant` zugelassen. Für diese Phasen erlaubt die Textprüfung direkt erkennbare
schreibende Ziele nur an lokalen Tabellenvariablen; erkannte persistente DML-,
`SELECT INTO`-, `BULK INSERT`-, DDL-, DBCC- und Rechteänderungen, direkte
Datenbank-/Sicherheitskontextwechsel sowie nicht freigegebene SQLCMD-Controlzeilen
werden abgelehnt; nur `:setvar SQLCMDMAXVARTYPEWIDTH 0` bleibt in
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
Diese Werte sind nicht empirisch qualifiziert und der aktuelle Caller setzt sie
nicht durch. Ein späterer Runtime-Aufrufer muss vor Setup ein abweichendes
Ressourcenprofil zurückweisen und Daten-/TempDB-Grenzen tatsächlich
überwachen. `CTRL+C`, Phasen- und Gesamtzeitüberschreitung müssen den
sqlcmd-Prozessbaum beenden. Der spätere Runtimecaller muss nach begonnenem
Setup Cleanup nur bei bestätigtem Prozessende und Reap starten; andernfalls muss
er Cleanup unterdrücken und `FAIL_CLEANUP` melden, damit es nicht parallel zu
einer möglicherweise noch laufenden SQL-Phase arbeitet. Dieses Verhalten ist
im vorhandenen FWK-010-Caller noch nicht qualifiziert. Bei erzwungenem Abbruch können synthetische
Teilobjekte in der markierten Datenbank verbleiben; Abschluss der serverseitigen
Abbruchwirkung und TempDB-Freigabe sind unbelegt. Unbekanntes Eigentum oder
fehlgeschlagenes Cleanup führt zu Erhalt der Datenbank und `FAIL_CLEANUP`, nicht
zum erzwungenen Entfernen. Diese Anforderungen sind im Proposed-Manifest
gebunden, aber noch keine Runtime-Durchsetzung.

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

Der QRY-023-Prüflauf wurde nicht gestartet. Der read-only Preflight akzeptiert
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
Bevor die Demo in den Katalog oder einen Runtimeworkflow aufgenommen wird,
bleiben formale Harness-Abnahme,
Runtimecaller-Integration, phasenspezifische Identität, Ressourcenprofil und
konkrete Ausführungsgenehmigung offen.

Der Ressourcenrahmen steht als Vorschlag im `resources`-Abschnitt von
[`container-images.proposed.json`](container-images.proposed.json). Er ist aus
Microsofts Linux-Mindestanforderungen und der geforderten Trennung zwischen
Container- und SQL-Server-Speichergrenze abgeleitet. 8/20 GiB Hostreserve sowie
4/3 GiB Container-/Enginegrenze sind Projektwerte ohne QRY-023-Laufmessung;
der Runtimeaufrufer muss sie vor Start tatsächlich durchsetzen.

## Verträge und Reviews

- [Statischer Demoentwurf](../../../Documentation/Project_Planning/GRAPH_TABLES_DEMO_CONCEPT.md)
- [Messworkload](../../../Documentation/Project_Planning/GRAPH_TABLES_MEASUREMENT_WORKLOAD_DESIGN.md)
- [Quellen- und Methodenreview](../../../Documentation/Project_Planning/GRAPH_TABLES_METHOD_REVIEW.md)
- [Editions- und Buildreview](../../../Documentation/Project_Planning/GRAPH_TABLES_BUILD_EDITION_REVIEW.md)
- [ScriptDom-Grammatikprüfung](../../../Documentation/Project_Planning/GRAPH_TABLES_SCRIPTDOM_PARSER_REVIEW.md)
- [Coverage-Prüfung des Proposed Harness](../../../Documentation/Project_Planning/QRY023_PROPOSED_HARNESS_REVIEW.md)
- Vorgeschlagener unveränderlicher Image-Lock: [`container-images.proposed.json`](container-images.proposed.json); nicht von einem Runtimeworkflow konsumiert und nicht ausführungsberechtigend.
- Framework: `FWK-002`, `FWK-003`, `FWK-004`, `FWK-005`, `FWK-008`, `FWK-010`, `FWK-011` und `FWK-012`.
